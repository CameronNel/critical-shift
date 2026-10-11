using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Player.Editor
{
    // Surface UV0 remains Blender's atlas. Verify Unity's independently generated
    // lightmap channel; a shared texture atlas is not a valid lighting layout.
    internal sealed class MineLightmapUvImport : AssetPostprocessor
    {
        public override uint GetVersion() => 2;
        private void OnPostprocessModel(GameObject model)
        {
            if(assetPath!=SpawnMapBuild.Folder+"Room-mine.fbx") return;
            var visited=new HashSet<Mesh>();int checkedMeshes=0;
            foreach(var filter in model.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh=filter.sharedMesh;
                if(mesh==null || !visited.Add(mesh)) continue;
                var uv=mesh.uv2;
                if(mesh.uv3.Length!=mesh.vertexCount) continue; // Source volume containers have no delivery UV channels.
                if(uv.Length!=mesh.vertexCount || uv.Any(p=>float.IsNaN(p.x) || float.IsNaN(p.y) || float.IsInfinity(p.x) || float.IsInfinity(p.y) || p.x<0 || p.y<0 || p.x>1.001f || p.y>1.001f))
                    throw new InvalidOperationException("Invalid imported mine lightmap UVs: "+mesh.name);
                checkedMeshes++;
            }
            Debug.Log("CS_MINE_LIGHTMAP_UV_IMPORT_OK; meshes="+checkedMeshes);
        }
    }

    // Engine-only lighting of the pinned assembly; no Blender source or placement is changed.
    internal static class MineVisualLighting
    {
        internal static void ConfigureAssembly(AssemblyLighting source)
        {
            if(source==null || source.world_color==null || source.sun_color==null || source.sun_rot_deg==null)
                throw new InvalidOperationException("Mine delivery is missing the assembly's lighting contract.");
            RenderSettings.ambientLight=new Color(source.world_color[0],source.world_color[1],source.world_color[2]).gamma*source.world_strength;
            var node=new GameObject("Combined map moon");
            var light=node.AddComponent<Light>();light.type=LightType.Directional;
            light.color=new Color(source.sun_color[0],source.sun_color[1],source.sun_color[2]).gamma;
            light.intensity=source.sun_energy;light.lightmapBakeType=LightmapBakeType.Mixed;light.shadows=LightShadows.Soft;
            light.shadowAngle=1.5f; // The assembly builder's COMBINED moon angle.
            var sourceRotation=Quaternion.AngleAxis(source.sun_rot_deg[2],Vector3.forward)*
                Quaternion.AngleAxis(source.sun_rot_deg[1],Vector3.up)*Quaternion.AngleAxis(source.sun_rot_deg[0],Vector3.right);
            var forward=sourceRotation*Vector3.back;var up=sourceRotation*Vector3.up;
            node.transform.rotation=Quaternion.LookRotation(new Vector3(forward.x,forward.z,forward.y),new Vector3(up.x,up.z,up.y));
        }

        internal static void AddProbes(Transform root)
        {
            var node=new GameObject("Mine lighting probes");node.transform.SetParent(root,false);
            var positions=new List<Vector3>();
            // Measured haulage centreline and retained shed footprint from COMBINED_MAP.md.
            for(float x=-91;x<=-22;x+=3)
                foreach(float z in new[] {-32f,-29f,-26f})
                    foreach(float y in new[] {-0.3f,1.2f,2.5f}) positions.Add(new Vector3(x,y,z));
            node.AddComponent<LightProbeGroup>().probePositions=positions.ToArray();
        }

        internal static void Finish(Transform root)
        {
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            var sky=map.materials.Single(p=>p.room=="mine").assemblyLighting;
            var authored=map.rooms.Single(r=>r.key=="mine").lights.ToDictionary(l=>l.name,StringComparer.Ordinal);
            foreach(var light in root.GetComponentsInChildren<Light>().Where(l=>l.type==LightType.Point && l.lightmapBakeType==LightmapBakeType.Mixed))
                light.intensity=authored[light.name].power/500;
            int index=0;
            foreach(float x in new[] {-27f,-47f,-68f,-87f})
            {
                var node=new GameObject("Mine reflection "+index);node.transform.SetParent(root,false);
                node.transform.localPosition=new Vector3(x,1.7f,-29);
                var probe=node.AddComponent<ReflectionProbe>();probe.mode=ReflectionProbeMode.Baked;
                probe.clearFlags=ReflectionProbeClearFlags.SolidColor;
                probe.backgroundColor=new Color(sky.world_color[0],sky.world_color[1],sky.world_color[2]).gamma*sky.world_strength;
                probe.size=new Vector3(index==0 ? 20:24,9,20);probe.resolution=128;probe.boxProjection=true;probe.hdr=true;
                string file=SpawnMapBuild.Folder+"Surfaces/MineReflection"+index+".exr";
                if(!Lightmapping.BakeReflectionProbe(probe,file)) throw new InvalidOperationException("Mine reflection capture failed.");
                AssetDatabase.ImportAsset(file);
                var importer=(TextureImporter)AssetImporter.GetAtPath(file);
                importer.sRGBTexture=false;importer.textureShape=TextureImporterShape.TextureCube;
                var settings=new TextureImporterSettings();importer.ReadTextureSettings(settings);
                settings.cubemapConvolution=TextureImporterCubemapConvolution.Specular;importer.SetTextureSettings(settings);
                importer.mipmapEnabled=true;importer.filterMode=FilterMode.Trilinear;importer.wrapMode=TextureWrapMode.Clamp;
                importer.anisoLevel=0;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.SaveAndReimport();
                probe.mode=ReflectionProbeMode.Custom;probe.customBakedTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(file);
                if(probe.customBakedTexture==null) throw new InvalidOperationException("Mine reflection did not import as a cubemap.");
                index++;
            }
            ReflectionProbe.UpdateCachedState();
            Validate(root,map);
        }

        private static void Validate(Transform root,ExportMap map)
        {
            var source=map.rooms.Single(r=>r.key=="mine");
            var package=map.materials.Single(p=>p.room=="mine");
            var nodes=root.GetComponentsInChildren<Transform>(true).Where(t=>t.name.StartsWith("CS_",StringComparison.Ordinal))
                .ToDictionary(t=>t.name,StringComparer.Ordinal);
            int surfaces=0,lightmapped=0,probeLit=0;
            foreach(var binding in source.objects.Where(o=>o.materials!=null && o.materials.Length>0))
            {
                var renderer=nodes[binding.node].GetComponent<MeshRenderer>();
                if(renderer==null || !renderer.enabled || renderer.sharedMaterials.Any(m=>m==null || !binding.materials.Contains(m.name)))
                    throw new InvalidOperationException("Mine surface binding changed: "+binding.node);
                if(renderer.sharedMaterials.Any(m=>m.shader.name!="CriticalShift/BlenderSurface" && m.shader.name!="CriticalShift/BlenderGlass"))
                    throw new InvalidOperationException("Mine has an automatic preview material: "+binding.node);
                var mesh=renderer.GetComponent<MeshFilter>().sharedMesh;
                var uv=mesh.uv2;
                if(uv.Length!=mesh.vertexCount || uv.Any(p=>float.IsNaN(p.x) || float.IsNaN(p.y) || float.IsInfinity(p.x) || float.IsInfinity(p.y)))
                    throw new InvalidOperationException("Mine lightmap UV channel is invalid: "+binding.node);
                if(renderer.receiveGI==ReceiveGI.LightProbes) probeLit++;
                else
                {
                    if(renderer.lightmapIndex<0 || renderer.lightmapIndex>=LightmapSettings.lightmaps.Length)
                        throw new InvalidOperationException("Mine surface was omitted from the lighting bake: "+binding.node);
                    lightmapped++;
                }
                surfaces++;
            }
            if(surfaces!=package.meshes) throw new InvalidOperationException("Mine delivery mesh coverage changed.");
            var collider=root.GetComponentsInChildren<MeshCollider>().Single();
            if(collider.sharedMesh.triangles.Length/3!=source.collisionTriangles)
                throw new InvalidOperationException("Mine collision inventory changed.");
            if((root.position-new Vector3(source.translation[0],source.translation[2],source.translation[1])).sqrMagnitude>0.000001f)
                throw new InvalidOperationException("Mine moved away from its pinned assembly placement.");
            Physics.SyncTransforms();
            foreach(float height in new[] {0.6f,1.7f,3f})
                if(Physics.Raycast(root.TransformPoint(new Vector3(-21.6f,height,-29f)),root.TransformDirection(Vector3.left),out var hit,25,~0,QueryTriggerInteraction.Ignore))
                    throw new InvalidOperationException("Mine/yard centreline is blocked at height "+height+": "+hit.collider.name);
            foreach(var probe in root.GetComponentsInChildren<ReflectionProbe>())
            {
                var cube=probe.customBakedTexture as Cubemap;
                if(cube==null || cube.mipmapCount<6 || cube.filterMode!=FilterMode.Trilinear || cube.wrapMode!=TextureWrapMode.Clamp)
                    throw new InvalidOperationException("Mine reflection filtering is invalid.");
            }
            File.WriteAllText(SpawnMapBuild.Folder+"mine-native-validation.json",JsonUtility.ToJson(new MineValidation
            {
                mapCommit=map.mapCommit,surfaces=surfaces,collisionTriangles=source.collisionTriangles,
                reflectionProbes=root.GetComponentsInChildren<ReflectionProbe>().Length,
                lightmaps=LightmapSettings.lightmaps.Length,lightmapped=lightmapped,probeLit=probeLit,
                joinCentrelineRays=3,sourcePreservation="Verified separately by prepare_mine.py"
            },true));
            Debug.Log("CS_MINE_NATIVE_BINDINGS_OK; surfaces="+surfaces+"; collision="+source.collisionTriangles);
        }

        [Serializable] private sealed class MineValidation
        {
            public string mapCommit,sourcePreservation;public int surfaces,collisionTriangles,reflectionProbes,lightmaps,lightmapped,probeLit,joinCentrelineRays;
        }
    }
}
