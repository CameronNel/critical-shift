using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CriticalShift.Features.Player.Unity;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Player.Editor
{
    // Surface UV0 remains Blender's atlas. Verify the independently generated
    // lightmap channel; a shared texture atlas is not a valid lighting layout.
    internal sealed class MineLightmapUvImport : AssetPostprocessor
    {
        public override uint GetVersion() => 3;
        private void OnPostprocessModel(GameObject model)
        {
            if(assetPath!=SpawnMapBuild.Folder+"Room-mine.fbx" && assetPath!=SpawnMapBuild.Folder+"MineContext.fbx") return;
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
            // Cycles SUN energy is irradiance; Unity's built-in BRDF omits
            // diffuse /pi. Native direct and baked 18% grey controls verify
            // this conversion independently of the mine's material colours.
            light.intensity=source.sun_energy/Mathf.PI;light.lightmapBakeType=LightmapBakeType.Mixed;light.shadows=LightShadows.Soft;
            light.shadowAngle=1.5f; // The assembly builder's COMBINED moon angle.
            var sourceRotation=Quaternion.AngleAxis(source.sun_rot_deg[2],Vector3.forward)*
                Quaternion.AngleAxis(source.sun_rot_deg[1],Vector3.up)*Quaternion.AngleAxis(source.sun_rot_deg[0],Vector3.right);
            var forward=sourceRotation*Vector3.back;var up=sourceRotation*Vector3.up;
            node.transform.rotation=Quaternion.LookRotation(new Vector3(forward.x,forward.z,forward.y),new Vector3(up.x,up.z,up.y));
        }

        internal static void ConfigureSourceSun(Light light,ExportLight source)
        {
            if(source.type!="SUN" || source.rotation==null || source.rotation.Length!=4)
                throw new InvalidOperationException("Authored sun is missing its orientation: "+source.name);
            light.type=LightType.Directional;light.intensity=source.power/Mathf.PI;light.shadowAngle=source.angle;
            var q=source.rotation;var rotation=new Quaternion(q[1],q[2],q[3],q[0]);
            var forward=rotation*Vector3.back;var up=rotation*Vector3.up;
            light.transform.localRotation=Quaternion.LookRotation(new Vector3(forward.x,forward.z,forward.y),new Vector3(up.x,up.z,up.y));
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

        internal static void CheckCentreline(Transform root)
        {
            Physics.SyncTransforms();
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            var rays=map.materials.Single(p=>p.room=="mine").joinRays;
            if(rays==null || rays.Length!=9) throw new InvalidOperationException("Missing Blender mine join-ray expectations.");
            Vector3 V(float[] p)=>new Vector3(p[0],p[2],p[1]);
            foreach(var ray in rays)
            {
                bool hit=Physics.Raycast(root.TransformPoint(V(ray.origin)),root.TransformDirection(V(ray.direction)),out var contact,ray.distance,~0,QueryTriggerInteraction.Ignore);
                if(hit!=ray.hit || (hit && (contact.point-root.TransformPoint(V(ray.point))).magnitude>0.01f))
                    throw new InvalidOperationException("Mine join differs from Blender at "+V(ray.origin)+"; expected="+ray.node+"; native="+(hit ? contact.collider.name+" "+contact.point : "clear"));
            }
            if(rays.Count(r=>!r.hit && Math.Abs(r.origin[1]+29)>0.1f)!=6)
                throw new InvalidOperationException("Both authored walking lanes must remain clear.");
            Debug.Log("CS_MINE_JOIN_RAYS_OK; sourceMatched=9; clearWalkingLanes=6");
        }

        internal static void Finish(Transform root)
        {
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            var sky=map.materials.Single(p=>p.room=="mine").assemblyLighting;
            // The scoped legacy bake baseline is restored to source-physical
            // runtime intensity before actors and reflections are rendered.
            // Keep baked finite-angle SUN shadows on static scenery; moving
            // receivers use runtime casters and baked probe occlusion.
            foreach(var sun in UnityEngine.Object.FindObjectsByType<Light>()
                .Where(l=>l.type==LightType.Directional && l.lightmapBakeType==LightmapBakeType.Mixed &&
                    (l.transform.IsChildOf(root) || l.name=="Combined map moon" || l.name=="FE_MOON")))
                sun.lightShadowCasterMode=LightShadowCasterMode.ShadowMask;
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
            FinishAtmosphere(map.materials.Single(p=>p.room=="mine"));
            Validate(root,map);
        }

        private static void FinishAtmosphere(SurfacePackage package)
        {
            if(package.volumes==null) return;
            if(package.volumes.Length>2 || package.volumes.Any(v=>Mathf.Abs(v.anisotropy)>0.0001f)) throw new InvalidOperationException("Mine atmosphere requires the authored two isotropic volumes.");
            LightProbes.Tetrahedralize();
            var normals=new[] {Vector3.right,Vector3.left,Vector3.up,Vector3.down,Vector3.forward,Vector3.back};
            for(int index=0;index<package.volumes.Length;index++)
            {
                var volume=package.volumes[index];
                Vector3 V(float[] p)=>new Vector3(p[0],p[2],p[1]);
                var minimum=V(volume.minimum);var maximum=V(volume.maximum);
                var texture=new Texture2D(32,16,TextureFormat.RGBAHalf,false,true) {filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp};
                var values=new Color[6];
                for(int z=0;z<4;z++) for(int y=0;y<4;y++) for(int x=0;x<32;x++)
                {
                    var p=minimum+Vector3.Scale(maximum-minimum,new Vector3((x+.5f)/32,(z+.5f)/4,(y+.5f)/4));
                    LightProbes.GetInterpolatedProbe(p,null,out var probe);probe.Evaluate(normals,values);
                    var color=values.Aggregate(Color.black,(sum,c)=>sum+c)/6;
                    color=new Color(Mathf.Max(color.r,0),Mathf.Max(color.g,0),Mathf.Max(color.b,0),1);
                    texture.SetPixel(x,z*4+y,color);
                }
                texture.Apply(false,false);
                string path=SpawnMapBuild.Folder+"Surfaces/MineVolume"+index+"Lighting.asset";
                AssetDatabase.DeleteAsset(path);AssetDatabase.CreateAsset(texture,path);
            }
            string materialPath=SpawnMapBuild.Folder+"Surfaces/MineAtmosphere.mat";
            var material=AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if(material==null) { material=new Material(Shader.Find("Hidden/CriticalShift/MineAtmosphere"));AssetDatabase.CreateAsset(material,materialPath); }
            foreach(var camera in UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsInactive.Include)) ConfigureAtmosphere(camera,package,material);
            Debug.Log("CS_MINE_ATMOSPHERE_OK; sourceDensityVolumes="+package.volumes.Length);
        }
        internal static void ConfigureAtmosphere(Camera camera,SurfacePackage package,Material material=null)
        {
            if(package.volumes==null || package.volumes.Length==0) return;
            material=material ?? AssetDatabase.LoadAssetAtPath<Material>(SpawnMapBuild.Folder+"Surfaces/MineAtmosphere.mat");
            if(material==null) throw new InvalidOperationException("Mine atmosphere has not been prepared.");
            var volumes=package.volumes.Select((source,index)=>new MineFogVolume
            {
                minimum=new Vector3(source.minimum[0],source.minimum[2],source.minimum[1]),
                maximum=new Vector3(source.maximum[0],source.maximum[2],source.maximum[1]),
                grid=new Vector3(source.grid[0],source.grid[1],source.grid[2]),
                // Raw shader scatter uniforms consume Blender linear colour directly.
                color=new Color(source.color[0],source.color[1],source.color[2],source.color[3]),
                density=SpawnSurfaceBuild.Texture(source.densityMap,false),
                lighting=AssetDatabase.LoadAssetAtPath<Texture2D>(SpawnMapBuild.Folder+"Surfaces/MineVolume"+index+"Lighting.asset")
            }).ToArray();
            if(volumes.Any(v=>v.density==null || v.lighting==null)) throw new InvalidOperationException("Missing mine volume maps.");
            // Unity evaluates image effects in component order. Atmosphere precedes the view LUT.
            var view=camera.GetComponent<BlenderView>();
            var fog=camera.GetComponent<MineAtmosphere>() ?? camera.gameObject.AddComponent<MineAtmosphere>();
            fog.Configure(material,volumes);
            if(view!=null)
            {
                // Move the atmosphere earlier without altering the existing display-profile settings.
                UnityEditorInternal.ComponentUtility.MoveComponentUp(fog);
            }
        }

        private static void Validate(Transform root,ExportMap map)
        {
            var source=map.rooms.Single(r=>r.key=="mine");
            var package=map.materials.Single(p=>p.room=="mine");
            foreach(var definition in package.definitions.Where(d=>!d.thinSurface))
            {
                var material=AssetDatabase.LoadAssetAtPath<Material>(SpawnMapBuild.Folder+"Surfaces/"+definition.key+".mat");
                if(material==null) throw new InvalidOperationException("Missing authored mine material: "+definition.key);
                if(!definition.emissionConstant && material.GetTexture("_EmissionMap")==null)
                    throw new InvalidOperationException("Authored mine emission has no texture: "+definition.key);
                if(!definition.baseConstant && material.GetTexture("_MainTex")==null)
                    throw new InvalidOperationException("Authored mine colour has no texture: "+definition.key);
                if(definition.sourceWood?.diffuse!=null && !string.IsNullOrEmpty(definition.sourceWood.diffuse.file) &&
                    (!material.IsKeywordEnabled("_SOURCE_WOOD") || new[] {"_WoodDiffuse","_WoodNormal","_WoodHigh"}.Any(key=>material.GetTexture(key)==null)))
                    throw new InvalidOperationException("Authored wood detail is missing: "+definition.key);
            }
            var nodes=root.GetComponentsInChildren<Transform>(true).Where(t=>t.name.StartsWith("CS_",StringComparison.Ordinal))
                .ToDictionary(t=>t.name,StringComparer.Ordinal);
            var woodMaterials=new HashSet<string>(package.definitions.Where(d=>d.sourceWood?.diffuse!=null &&
                !string.IsNullOrEmpty(d.sourceWood.diffuse.file)).Select(d=>d.key),StringComparer.Ordinal);
            int surfaces=0,lightmapped=0,probeLit=0;
            foreach(var binding in source.objects.Where(o=>o.materials!=null && o.materials.Length>0))
            {
                var renderer=nodes[binding.node].GetComponent<MeshRenderer>();
                if(renderer==null || !renderer.enabled || renderer.sharedMaterials.Any(m=>m==null || !binding.materials.Contains(m.name)))
                    throw new InvalidOperationException("Mine surface binding changed: "+binding.node);
                ValidateShadowBinding(renderer,binding);
                if(renderer.sharedMaterials.Any(m=>m.shader.name!="CriticalShift/BlenderSurface" && m.shader.name!="CriticalShift/BlenderGlass"))
                    throw new InvalidOperationException("Mine has an automatic preview material: "+binding.node);
                var mesh=renderer.GetComponent<MeshFilter>().sharedMesh;
                if(binding.materials.Any(woodMaterials.Contains))
                {
                    var sourceUV=mesh.uv3;
                    if(sourceUV.Length!=mesh.vertexCount || sourceUV.Any(p=>float.IsNaN(p.x) || float.IsNaN(p.y) || float.IsInfinity(p.x) || float.IsInfinity(p.y)))
                        throw new InvalidOperationException("Authored wood UV channel is invalid: "+binding.node);
                }
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
            int contextSurfaces=0;
            if(package.contextObjects!=null)
            {
                var front=GameObject.Find("ROOM_front-end-area").GetComponentsInChildren<MeshRenderer>().Where(r=>r.name.StartsWith("CS_",StringComparison.Ordinal)).ToDictionary(r=>r.name,StringComparer.Ordinal);
                foreach(var binding in package.contextObjects.Where(b=>b.materials!=null))
                {
                    var renderer=front[binding.node];
                    ValidateShadowBinding(renderer,binding);
                    if(!renderer.enabled || renderer.sharedMaterials.Any(m=>!binding.materials.Contains(m.name) || !m.shader.name.StartsWith("CriticalShift/Blender",StringComparison.Ordinal)))
                        throw new InvalidOperationException("Mine context uses a preview material: "+binding.node);
                    if(renderer.receiveGI!=ReceiveGI.LightProbes && (renderer.lightmapIndex<0 || renderer.lightmapIndex>=LightmapSettings.lightmaps.Length))
                        throw new InvalidOperationException("Mine context is missing baked lighting: "+binding.node);
                    if(binding.source=="cliff_face" && (renderer.receiveGI!=ReceiveGI.LightProbes ||
                        renderer.lightProbeUsage!=LightProbeUsage.Off || renderer.reflectionProbeUsage!=ReflectionProbeUsage.Off ||
                        !GameObjectUtility.GetStaticEditorFlags(renderer.gameObject).HasFlag(StaticEditorFlags.ContributeGI)))
                        throw new InvalidOperationException("Mine cliff backface lighting adapter changed: "+binding.node);
                    contextSurfaces++;
                }
            }
            foreach(var emitter in root.GetComponentsInChildren<MeshRenderer>().Where(r=>r.name=="Embedded emitter surface"))
                if(emitter.receiveGI!=ReceiveGI.LightProbes || GameObjectUtility.GetStaticEditorFlags(emitter.gameObject).HasFlag(StaticEditorFlags.ContributeGI))
                    throw new InvalidOperationException("Small mine emitter must use probes and its authored point light.");
            if(package.volumes!=null)
            {
                foreach(var camera in UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsInactive.Include))
                {
                    var fog=camera.GetComponent<MineAtmosphere>();
                    if(fog==null) throw new InvalidOperationException("Player camera is missing the mine atmosphere.");
                    var serialized=new SerializedObject(fog);
                    if(serialized.FindProperty("profile").objectReferenceValue==null || serialized.FindProperty("volumes").arraySize!=package.volumes.Length)
                        throw new InvalidOperationException("Player mine atmosphere is incomplete.");
                }
            }
            var collider=root.GetComponentsInChildren<MeshCollider>().Single();
            if(collider.sharedMesh.triangles.Length/3!=source.collisionTriangles)
                throw new InvalidOperationException("Mine collision inventory changed.");
            if((root.position-new Vector3(source.translation[0],source.translation[2],source.translation[1])).sqrMagnitude>0.000001f)
                throw new InvalidOperationException("Mine moved away from its pinned assembly placement.");
            CheckCentreline(root);
            foreach(var probe in root.GetComponentsInChildren<ReflectionProbe>())
            {
                var cube=probe.customBakedTexture as Cubemap;
                if(cube==null || cube.mipmapCount<6 || cube.filterMode!=FilterMode.Trilinear || cube.wrapMode!=TextureWrapMode.Clamp)
                    throw new InvalidOperationException("Mine reflection filtering is invalid.");
            }
            File.WriteAllText(SpawnMapBuild.Folder+"mine-native-validation.json",JsonUtility.ToJson(new MineValidation
            {
                mapCommit=map.mapCommit,surfaces=surfaces,contextSurfaces=contextSurfaces,collisionTriangles=source.collisionTriangles,
                reflectionProbes=root.GetComponentsInChildren<ReflectionProbe>().Length,atmosphereVolumes=package.volumes?.Length ?? 0,
                lightmaps=LightmapSettings.lightmaps.Length,lightmapped=lightmapped,probeLit=probeLit,
                joinCentrelineRays=package.joinRays.Length,clearWalkingRays=6,sourcePreservation="Verified separately by prepare_mine.py"
            },true));
            Debug.Log("CS_MINE_NATIVE_BINDINGS_OK; surfaces="+surfaces+"; collision="+source.collisionTriangles);
        }

        private static void ValidateShadowBinding(MeshRenderer renderer,ExportObject binding)
        {
            var expected=binding.visible && !binding.sourceShadowExcluded ? ShadowCastingMode.On : ShadowCastingMode.Off;
            if(renderer.shadowCastingMode!=expected)
                throw new InvalidOperationException("Mine source shadow visibility changed: "+binding.node+
                    "; expected="+expected+"; actual="+renderer.shadowCastingMode);
        }

        [Serializable] private sealed class MineValidation
        {
            public string mapCommit,sourcePreservation;public int surfaces,contextSurfaces,atmosphereVolumes,collisionTriangles,reflectionProbes,lightmaps,lightmapped,probeLit,joinCentrelineRays,clearWalkingRays;
        }
    }
}
