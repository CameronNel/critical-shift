using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;

namespace CriticalShift.Player.Editor
{
    // Inactive rooms still retain their meshes. Keep an owned, serialized copy
    // outside the delivered scene while the existing lighting subset is baked.
    internal sealed class ExcludedRoomBakeScope : IDisposable
    {
        private sealed class Node
        {
            internal string Path, Components;
            internal Vector3 Position, Scale;
            internal Quaternion Rotation;
            internal bool Active;
            internal int Layer, Flags;
        }

        private sealed class Room
        {
            internal string Name;
            internal Transform Parent;
            internal int Sibling;
            internal Node[] Nodes;
        }

        private sealed class RetainedLighting
        {
            private readonly Scene scene;
            private readonly Renderer[] renderers;
            private readonly int[] indices, realtimeIndices;
            private readonly Vector4[] scales, realtimeScales;
            private readonly Light[] lights;
            private readonly LightBakingOutput[] outputs;
            private readonly LightmapData[] maps;
            private readonly LightmapsMode mode;
            private readonly LightingDataAsset data;
            private readonly LightingSettings settings;
            private readonly Vector3[] probePositions;
            private readonly SphericalHarmonicsL2[] probeValues;
            private readonly SphericalHarmonicsL2 ambient;
            private readonly string environment;

            internal RetainedLighting(Scene original,HashSet<string> excluded)
            {
                scene=original;
                bool Retained(Component c)
                {
                    for(var t=c.transform;t!=null;t=t.parent) if(excluded.Contains(t.name)) return false;
                    return true;
                }
                renderers=original.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Renderer>(true)).Where(Retained).ToArray();
                indices=renderers.Select(r=>r.lightmapIndex).ToArray();scales=renderers.Select(r=>r.lightmapScaleOffset).ToArray();
                realtimeIndices=renderers.Select(r=>r.realtimeLightmapIndex).ToArray();realtimeScales=renderers.Select(r=>r.realtimeLightmapScaleOffset).ToArray();
                lights=original.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Light>(true)).Where(Retained).ToArray();
                outputs=lights.Select(l=>l.bakingOutput).ToArray();
                maps=LightmapSettings.lightmaps.Select(m=>new LightmapData {lightmapColor=m.lightmapColor,lightmapDir=m.lightmapDir,shadowMask=m.shadowMask}).ToArray();
                mode=LightmapSettings.lightmapsMode;
                data=Lightmapping.lightingDataAsset;settings=Lightmapping.lightingSettings;
                probePositions=LightmapSettings.lightProbes?.positions ?? Array.Empty<Vector3>();
                probeValues=LightmapSettings.lightProbes?.bakedProbes ?? Array.Empty<SphericalHarmonicsL2>();
                ambient=RenderSettings.ambientProbe;environment=EnvironmentSignature();
            }

            internal void Verify()
            {
                if(SceneManager.GetActiveScene()!=scene || Lightmapping.lightingDataAsset!=data || Lightmapping.lightingSettings!=settings ||
                   LightmapSettings.lightmaps.Length!=maps.Length || LightmapSettings.lightmapsMode!=mode || !RenderSettings.ambientProbe.Equals(ambient) || EnvironmentSignature()!=environment)
                    throw new InvalidOperationException("Additive room restoration changed active/global baked lighting.");
                for(int i=0;i<maps.Length;i++)
                {
                    var actual=LightmapSettings.lightmaps[i];
                    if(actual.lightmapColor!=maps[i].lightmapColor || actual.lightmapDir!=maps[i].lightmapDir || actual.shadowMask!=maps[i].shadowMask)
                        throw new InvalidOperationException("Additive room restoration changed baked lightmap texture assignments.");
                }
                for(int i=0;i<renderers.Length;i++)
                    if(renderers[i]==null || renderers[i].lightmapIndex!=indices[i] || renderers[i].lightmapScaleOffset!=scales[i] ||
                       renderers[i].realtimeLightmapIndex!=realtimeIndices[i] || renderers[i].realtimeLightmapScaleOffset!=realtimeScales[i])
                        throw new InvalidOperationException("Additive restoration changed retained renderer lightmap assignments.");
                for(int i=0;i<lights.Length;i++)
                    if(lights[i]==null || !lights[i].bakingOutput.Equals(outputs[i]))
                        throw new InvalidOperationException("Additive restoration changed retained light baking output.");
                var positions=LightmapSettings.lightProbes?.positions ?? Array.Empty<Vector3>();
                var values=LightmapSettings.lightProbes?.bakedProbes ?? Array.Empty<SphericalHarmonicsL2>();
                if(!positions.SequenceEqual(probePositions) || !values.SequenceEqual(probeValues))
                    throw new InvalidOperationException("Additive restoration changed baked probe positions or coefficients.");
            }

            private static string EnvironmentSignature()=>RenderSettings.ambientMode+":"+RenderSettings.ambientLight.ToString("F9")+":"+
                RenderSettings.ambientIntensity.ToString("R",CultureInfo.InvariantCulture)+":"+RenderSettings.reflectionIntensity.ToString("R",CultureInfo.InvariantCulture)+":"+
                AssetId(RenderSettings.skybox)+":"+RenderSettings.fog+":"+RenderSettings.fogColor.ToString("F9")+":"+RenderSettings.fogDensity.ToString("R",CultureInfo.InvariantCulture);
        }

        private readonly Scene original;
        private readonly Room[] rooms;
        private readonly string folder, scenePath;
        private Scene stash;
        private bool restored;

        internal ExcludedRoomBakeScope(Scene scene, GameObject[] excluded)
        {
            original=scene;
            if(!scene.IsValid() || !scene.isLoaded || excluded.Any(o=>o.activeSelf || o.scene!=scene) ||
               excluded.Select(o=>o.name).Distinct(StringComparer.Ordinal).Count()!=excluded.Length)
                throw new InvalidOperationException("Bake exclusions must be unique inactive rooms in the current scene.");
            CheckReferences(scene,excluded);
            rooms=excluded.Select(o=>new Room {Name=o.name,Parent=o.transform.parent,
                Sibling=o.transform.GetSiblingIndex(),Nodes=Snapshot(o.transform)}).ToArray();
            folder=SpawnMapBuild.Folder.TrimEnd('/')+"/BakeRoomStash-"+Guid.NewGuid().ToString("N");
            scenePath=folder+"/ExcludedRooms.unity";
            var lightingOnEntry=new RetainedLighting(original,rooms.Select(r=>r.Name).ToHashSet(StringComparer.Ordinal));
            try
            {
                if(string.IsNullOrEmpty(AssetDatabase.CreateFolder(SpawnMapBuild.Folder.TrimEnd('/'),Path.GetFileName(folder))))
                    throw new IOException("Could not create owned bake room stash.");
                stash=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
                EditorSceneManager.SetActiveScene(original);
                foreach(var room in excluded)
                {
                    var position=room.transform.position;var rotation=room.transform.rotation;
                    room.transform.SetParent(null,true);
                    SceneManager.MoveGameObjectToScene(room,stash);
                    if((room.transform.position-position).magnitude>0.00001f || !SameRotation(room.transform.rotation,rotation))
                        throw new InvalidOperationException("Bake stash changed a room's world pose: "+room.name);
                }
                if(!EditorSceneManager.SaveScene(stash,scenePath) || !File.Exists(scenePath))
                    throw new IOException("Could not serialize excluded rooms before unloading.");
                if(!EditorSceneManager.CloseScene(stash,true)) throw new IOException("Could not unload excluded room scene.");
                EditorSceneManager.SetActiveScene(original);
                EditorUtility.UnloadUnusedAssetsImmediate();GC.Collect();GC.WaitForPendingFinalizers();
                lightingOnEntry.Verify();
                Debug.Log("CS_BAKE_EXCLUDED_ROOMS_UNLOADED; rooms="+rooms.Length+"; ownedScene="+scenePath);
            }
            catch(Exception initiating)
            {
                // A failed scope never proceeds to lighting. Preserve the owned
                // scene if recovery itself fails; the full pre-bake scene exists.
                try { Restore(); }
                catch(Exception recovery) { throw new AggregateException("Bake stash failed and recovery failed; owned recovery data preserved.",initiating,recovery); }
                throw;
            }
        }

        public void Dispose()=>Restore();

        // Bounded actual-engine control: do not bake or save the delivery scene.
        public static void VerifyRoundTrip()
        {
            var scene=EditorSceneManager.OpenScene(SpawnMapBuild.ScenePath,OpenSceneMode.Single);
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            Transform Root(string key)=>scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Transform>(true)).Single(t=>t.name=="ROOM_"+key);
            var originalActive=map.rooms.ToDictionary(r=>r.key,r=>Root(r.key).gameObject.activeSelf,StringComparer.Ordinal);
            var expected=map.rooms.Select(r=>"ROOM_"+r.key).ToHashSet(StringComparer.Ordinal);
            foreach(var room in map.rooms) UnityEngine.Object.DestroyImmediate(Root(room.key).Find("Static collision — "+room.key).gameObject);
            var excluded=map.rooms.Where(r=>r.key!="spawn-room" && r.key!="mine" && r.key!="front-end-area")
                .Select(r=>Root(r.key).gameObject).ToArray();
            foreach(var room in excluded) room.SetActive(false);
            Debug.Log("CS_BAKE_SCOPE_CONTROL_BEFORE; nativeAllocatedBytes="+UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong());
            using(var scope=new ExcludedRoomBakeScope(scene,excluded))
                Debug.Log("CS_BAKE_SCOPE_CONTROL_UNLOADED; nativeAllocatedBytes="+UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong());
            foreach(var room in map.rooms)
            {
                SpawnMapBuild.RestoreCollision(Root(room.key),room);Root(room.key).gameObject.SetActive(originalActive[room.key]);
            }
            var actual=scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Transform>(true))
                .Where(t=>t.name.StartsWith("ROOM_",StringComparison.Ordinal)).Select(t=>t.name).ToArray();
            if(actual.Length!=expected.Count || !actual.ToHashSet(StringComparer.Ordinal).SetEquals(expected))
                throw new InvalidOperationException("Bake scope failed to restore complete current map room inventory.");
            if(Directory.GetDirectories(SpawnMapBuild.Folder,"BakeRoomStash-*").Length!=0)
                throw new InvalidOperationException("Bake scope left an owned scene in delivery assets.");
            Physics.SyncTransforms();MineVisualLighting.CheckCentreline(Root("mine"));
            Debug.Log("CS_BAKE_SCOPE_ROUND_TRIP_OK; rooms="+actual.Length+"; excluded="+excluded.Length+"; nativeAllocatedBytes="+UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong());
        }

        private void Restore()
        {
            if(restored) return;
            var lighting=new RetainedLighting(original,rooms.Select(r=>r.Name).ToHashSet(StringComparer.Ordinal));
            if((!stash.IsValid() || !stash.isLoaded) && File.Exists(scenePath))
                stash=EditorSceneManager.OpenScene(scenePath,OpenSceneMode.Additive);
            EditorSceneManager.SetActiveScene(original);
            var stashed=stash.IsValid() && stash.isLoaded ? stash.GetRootGameObjects() : Array.Empty<GameObject>();
            var names=rooms.Select(r=>r.Name).ToHashSet(StringComparer.Ordinal);
            if(stashed.Any(o=>!names.Contains(o.name))) throw new InvalidOperationException("Owned stash contains an unexpected root.");
            var loaded=original.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Transform>(true))
                .Where(t=>names.Contains(t.name)).Select(t=>t.gameObject).Concat(stashed).ToArray();
            if(loaded.Length!=rooms.Length || loaded.Select(o=>o.name).Distinct(StringComparer.Ordinal).Count()!=rooms.Length ||
               !loaded.Select(o=>o.name).ToHashSet(StringComparer.Ordinal).SetEquals(names))
                throw new InvalidOperationException("Bake room inventory cannot be reconciled between original and owned stash.");
            foreach(var entry in rooms.OrderBy(r=>r.Sibling))
            {
                var room=loaded.Single(o=>o.name==entry.Name);
                if(room.scene!=original) SceneManager.MoveGameObjectToScene(room,original);
                room.transform.SetParent(entry.Parent,false);
                room.transform.localPosition=entry.Nodes[0].Position;
                room.transform.localRotation=entry.Nodes[0].Rotation;
                room.transform.localScale=entry.Nodes[0].Scale;
                room.transform.SetSiblingIndex(entry.Sibling);
                var actual=Snapshot(room.transform);
                if(actual.Length!=entry.Nodes.Length) throw new InvalidOperationException("Restored room hierarchy changed: "+entry.Name);
                for(int i=0;i<actual.Length;i++)
                {
                    var a=actual[i];var b=entry.Nodes[i];
                    if(a.Path!=b.Path || a.Components!=b.Components || a.Active!=b.Active || a.Layer!=b.Layer || a.Flags!=b.Flags ||
                        (a.Position-b.Position).magnitude>0.00001f || (a.Scale-b.Scale).magnitude>0.00001f || !SameRotation(a.Rotation,b.Rotation))
                        throw new InvalidOperationException("Restored room state differs: "+entry.Name+" / "+b.Path);
                }
            }
            if(stash.IsValid() && stash.isLoaded && !EditorSceneManager.CloseScene(stash,true)) throw new IOException("Could not close empty room stash.");
            EditorSceneManager.SetActiveScene(original);
            lighting.Verify();
            CheckReferences(original,rooms.Select(r=>original.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Transform>(true))
                .Single(t=>t.name==r.Name).gameObject).ToArray());
            if(AssetDatabase.IsValidFolder(folder) && !AssetDatabase.DeleteAsset(folder)) throw new IOException("Could not remove owned temporary bake scene.");
            if(File.Exists(scenePath) || EditorBuildSettings.scenes.Any(s=>s.path==scenePath))
                throw new InvalidOperationException("Owned stash leaked into delivered assets or build scenes.");
            restored=true;
            Debug.Log("CS_BAKE_EXCLUDED_ROOMS_RESTORED; rooms="+rooms.Length+"; exactHierarchyMeshMaterialLightAndPoseChecks=Passed");
        }

        private static string PathOf(Transform node,Transform root)
        {
            if(node==root) return ".";
            return PathOf(node.parent,root)+"/"+node.GetSiblingIndex()+":"+node.name;
        }

        private static bool SameRotation(Quaternion a,Quaternion b)
        {
            var av=new Vector4(a.x,a.y,a.z,a.w);var bv=new Vector4(b.x,b.y,b.z,b.w);
            return Mathf.Min((av-bv).sqrMagnitude,(av+bv).sqrMagnitude)<=0.0000000001f;
        }

        private static string AssetId(UnityEngine.Object value)
        {
            if(value==null) return "null";
            if(!EditorUtility.IsPersistent(value) || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value,out string guid,out long id))
                throw new InvalidOperationException("Excluded room has an unpersisted asset: "+value.name);
            return guid+":"+id+":"+AssetDatabase.GetAssetPath(value);
        }

        private static Node[] Snapshot(Transform root)
        {
            return root.GetComponentsInChildren<Transform>(true).Select(t=>
            {
                var signature=new StringBuilder();
                foreach(var component in t.GetComponents<Component>())
                {
                    if(component==null) throw new InvalidOperationException("Excluded room has a missing component.");
                    signature.Append(component.GetType().FullName).Append('|');
                    if(component is Transform) continue;
                    if(component is MeshFilter filter)
                    {
                        var mesh=filter.sharedMesh;signature.Append(AssetId(mesh));
                        if(mesh!=null)
                        {
                            signature.Append(':').Append(mesh.vertexCount);
                            for(int s=0;s<mesh.subMeshCount;s++) signature.Append(':').Append(mesh.GetTopology(s)).Append(':').Append(mesh.GetIndexCount(s));
                        }
                    }
                    else if(component is MeshRenderer renderer)
                    {
                        if(renderer.HasPropertyBlock()) throw new InvalidOperationException("Excluded renderer has an unsupported material property block: "+renderer.name);
                        signature.Append(renderer.enabled).Append(':').Append(renderer.shadowCastingMode).Append(':').Append(renderer.receiveShadows)
                            .Append(':').Append(renderer.lightmapIndex).Append(':').Append(renderer.receiveGI).Append(':').Append(renderer.lightProbeUsage)
                            .Append(':').Append(renderer.reflectionProbeUsage).Append(':').Append(renderer.scaleInLightmap.ToString("R",CultureInfo.InvariantCulture))
                            .Append(':').Append(renderer.lightmapScaleOffset.ToString("F9")).Append(':').Append(renderer.realtimeLightmapIndex)
                            .Append(':').Append(renderer.realtimeLightmapScaleOffset.ToString("F9"));
                        foreach(var material in renderer.sharedMaterials) signature.Append(':').Append(AssetId(material));
                    }
                    else if(component is Light light)
                    {
                        signature.Append(light.enabled).Append(':').Append(light.type).Append(':').Append(light.lightmapBakeType).Append(':').Append(light.shadows)
                            .Append(':').Append(light.intensity.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(light.range.ToString("R",CultureInfo.InvariantCulture))
                            .Append(':').Append(light.spotAngle.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(light.shapeRadius.ToString("R",CultureInfo.InvariantCulture))
                            .Append(':').Append(light.color.r.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(light.color.g.ToString("R",CultureInfo.InvariantCulture))
                            .Append(':').Append(light.color.b.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(AssetId(light.cookie))
                            .Append(':').Append(light.innerSpotAngle.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(light.areaSize.ToString("F9"))
                            .Append(':').Append(light.bounceIntensity.ToString("R",CultureInfo.InvariantCulture));
                    }
                    else if(component is Animation animation)
                    {
                        if(animation.isPlaying) throw new InvalidOperationException("Excluded room has a playing animation: "+animation.name);
                        signature.Append(animation.enabled).Append(':').Append(animation.playAutomatically).Append(':').Append(animation.wrapMode)
                            .Append(':').Append(animation.cullingType).Append(':').Append(AssetId(animation.clip));
                        foreach(AnimationState state in animation)
                        {
                            if(state.enabled || state.time!=0 || state.speed!=1 || state.weight!=1)
                                throw new InvalidOperationException("Excluded animation has transient playback state: "+animation.name+" / "+state.name);
                            signature.Append(':').Append(state.name).Append(':').Append(AssetId(state.clip)).Append(':').Append(state.layer)
                                .Append(':').Append(state.wrapMode).Append(':').Append(state.blendMode).Append(':').Append(state.enabled)
                                .Append(':').Append(state.time.ToString("R",CultureInfo.InvariantCulture)).Append(':').Append(state.speed.ToString("R",CultureInfo.InvariantCulture))
                                .Append(':').Append(state.weight.ToString("R",CultureInfo.InvariantCulture));
                        }
                    }
                    else throw new InvalidOperationException("Excluded room component needs an explicit serialization contract: "+component.GetType().FullName);
                }
                return new Node {Path=PathOf(t,root),Position=t.localPosition,Rotation=t.localRotation,Scale=t.localScale,
                    Active=t.gameObject.activeSelf,Layer=t.gameObject.layer,Flags=(int)GameObjectUtility.GetStaticEditorFlags(t.gameObject),Components=signature.ToString()};
            }).ToArray();
        }

        private static void CheckReferences(Scene scene,GameObject[] excluded)
        {
            var ownership=new Dictionary<GameObject,GameObject>();
            foreach(var room in excluded)
                foreach(var transform in room.GetComponentsInChildren<Transform>(true)) ownership.Add(transform.gameObject,room);
            foreach(var component in scene.GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Component>(true)))
            {
                if(component==null) throw new InvalidOperationException("Bake scene contains a missing component.");
                if(component is Transform) continue; // Parent/child transforms are explicitly restored.
                ownership.TryGetValue(component.gameObject,out var owner);
                using var serialized=new SerializedObject(component);var property=serialized.GetIterator();
                while(property.Next(true))
                {
                    if(property.propertyType!=SerializedPropertyType.ObjectReference) continue;
                    var value=property.objectReferenceValue;
                    if(value==null || EditorUtility.IsPersistent(value)) continue;
                    var target=value is GameObject go ? go : (value as Component)?.gameObject;
                    if(target==null) continue;
                    ownership.TryGetValue(target,out var targetOwner);
                    if(owner!=targetOwner && (owner!=null || targetOwner!=null))
                        throw new InvalidOperationException("Bake room has a cross-room serialized reference: "+component.name+"."+property.propertyPath);
                }
            }
        }
    }
}
