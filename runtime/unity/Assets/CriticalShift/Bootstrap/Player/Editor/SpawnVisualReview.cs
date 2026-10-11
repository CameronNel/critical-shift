using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using CriticalShift.Features.Player.Unity;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Player.Editor
{
    [Serializable] public sealed class SourceView { public string name; public float[] position, forward, up; public float verticalFov; }
    [Serializable] public sealed class SourceViews { public SourceView[] views; }
    [Serializable] public sealed class PreparedScene { public string mapBindingsSha256, sceneSha256, sourceSha256; public int lightmaps; }

    // Real engine captures at the authored validation cameras, not substitute concept renders.
    public static class SpawnVisualReview
    {
        public static void BakeAndRender()
        {
            SpawnMapBuild.Create();
            var root = GameObject.Find("ROOM_spawn-room").transform;
            var worker=GameObject.Find("Local crew worker");worker.SetActive(false);
            var settings = new LightingSettings
            {
                bakedGI = true, realtimeGI = false,
                lightmapper = LightingSettings.Lightmapper.ProgressiveCPU,
                lightmapResolution = 20, lightmapMaxSize = 2048, lightmapPadding = 4,
                directSampleCount = 32, indirectSampleCount = 128, environmentSampleCount = 64,
                maxBounces = 6, lightmapCompression = LightmapCompression.None,
                mixedBakeMode = MixedLightingMode.IndirectOnly
            };
            string path = SpawnMapBuild.Folder + "Surfaces/SpawnLightingSettings.lighting";
            AssetDatabase.DeleteAsset(path); AssetDatabase.CreateAsset(settings,path); Lightmapping.lightingSettings=settings;
            var probes = new GameObject("Spawn lighting probes"); probes.transform.SetParent(root,false);
            var group = probes.AddComponent<LightProbeGroup>(); var positions=new List<Vector3>();
            for (float x=-7f; x<8.5f; x+=1.2f)
                for (float z=0.7f; z<12f; z+=1.2f)
                    for (float y=0.3f; y<2.7f; y+=1)
                        positions.Add(new Vector3(x,y,z));
            group.probePositions=positions.ToArray();
            var rooms=EditorSceneManager.GetActiveScene().GetRootGameObjects().SelectMany(o=>o.GetComponentsInChildren<Transform>(true))
                .Where(o=>o.name.StartsWith("ROOM_",StringComparison.Ordinal) && o!=root).Select(o=>o.gameObject).ToArray();
            foreach (var room in rooms) room.SetActive(false);
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),SpawnMapBuild.ScenePath);
            Debug.Log("CS_SPAWN_LIGHTING_BAKE_START");
            if (!Lightmapping.Bake()) throw new InvalidOperationException("Spawn lightmap bake did not complete.");
            Debug.Log("CS_SPAWN_LIGHTING_BAKE_OK; lightmaps="+LightmapSettings.lightmaps.Length);
            foreach (var room in rooms) room.SetActive(true);
            FinishLighting(root);
            worker.SetActive(true);
            SavePreparedScene();
            Render();
        }

        // A point bake starts inside the authored bulb; its shadow mask can still self-occlude.
        // Keep the indirect bake, but evaluate the practical's direct light and shadows at runtime.
        private static void FinishLighting(Transform root)
        {
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            var authored=map.rooms.Single(r=>r.key=="spawn-room").lights.ToDictionary(l=>l.name,StringComparer.Ordinal);
            foreach(var light in root.GetComponentsInChildren<Light>().Where(l=>l.type==LightType.Point))
            {
                light.intensity=authored[light.name].power/500;
                light.lightmapBakeType=LightmapBakeType.Realtime;
                light.bakingOutput=new LightBakingOutput();
            }
            foreach(var old in root.GetComponentsInChildren<ReflectionProbe>()) UnityEngine.Object.DestroyImmediate(old.gameObject);
            // Built-in baked area lights have no runtime geometry to reflect. Give the captures
            // the authored rectangle radiance, then remove these temporary emitters from the scene.
            var emitters=new List<GameObject>(); var emitterMaterials=new List<Material>();
            foreach (var light in root.GetComponentsInChildren<Light>().Where(l=>l.type==LightType.Rectangle && !l.name.Contains("_spill")))
            {
                var node=GameObject.CreatePrimitive(PrimitiveType.Quad);
                UnityEngine.Object.DestroyImmediate(node.GetComponent<Collider>());
                node.name="Temporary source area reflection";
                node.transform.position=light.transform.position;node.transform.rotation=light.transform.rotation;
                node.transform.localScale=new Vector3(light.areaSize.x,light.areaSize.y,1);
                var material=new Material(Shader.Find("CriticalShift/BlenderSurface"));
                material.SetColor("_Color",Color.black);material.EnableKeyword("_EMISSION");
                material.SetColor("_EmissionColor",light.color.linear*light.intensity);
                var renderer=node.GetComponent<Renderer>();renderer.sharedMaterial=material;
                renderer.shadowCastingMode=ShadowCastingMode.Off;
                GameObjectUtility.SetStaticEditorFlags(node,StaticEditorFlags.ReflectionProbeStatic);
                emitters.Add(node);emitterMaterials.Add(material);
            }
            int index=0;
            foreach (var local in new[] {new Vector3(0,2,6),new Vector3(-4.8f,2,4),new Vector3(5,2,4)})
            {
                var node=new GameObject("Spawn reflection "+index); node.transform.SetParent(root,false); node.transform.localPosition=local;
                var probe=node.AddComponent<ReflectionProbe>(); probe.mode=ReflectionProbeMode.Baked;
                probe.size=index==0 ? new Vector3(3.6f,4.2f,13) : new Vector3(7.6f,4.2f,9);
                probe.resolution=256; probe.boxProjection=true; probe.hdr=true;
                string file=SpawnMapBuild.Folder+"Surfaces/SpawnReflection"+index+".exr";
                if (!Lightmapping.BakeReflectionProbe(probe,file)) throw new InvalidOperationException("Reflection snapshot failed.");
                AssetDatabase.ImportAsset(file);
                var importer=(TextureImporter)AssetImporter.GetAtPath(file);
                importer.sRGBTexture=false; importer.textureShape=TextureImporterShape.TextureCube;
                importer.textureCompression=TextureImporterCompression.Uncompressed; importer.SaveAndReimport();
                probe.mode=ReflectionProbeMode.Custom;
                probe.customBakedTexture=AssetDatabase.LoadAssetAtPath<Cubemap>(file);
                if(probe.customBakedTexture==null) throw new InvalidOperationException("Reflection capture must import as a linear cubemap.");
                index++;
            }
            foreach(var node in emitters) UnityEngine.Object.DestroyImmediate(node);
            foreach(var material in emitterMaterials) UnityEngine.Object.DestroyImmediate(material);
            ReflectionProbe.UpdateCachedState();
        }

        private static void SavePreparedScene()
        {
            AssetDatabase.SaveAssets(); EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),SpawnMapBuild.ScenePath);
            File.WriteAllText(SpawnMapBuild.Folder+"prepared-scene.json",JsonUtility.ToJson(new PreparedScene
            {
                mapBindingsSha256=Digest(SpawnMapBuild.Folder+"map-bindings.json"),sceneSha256=Digest(SpawnMapBuild.ScenePath),
                sourceSha256=SourceDigest(),lightmaps=LightmapSettings.lightmaps.Length
            },true));
        }

        internal static void ValidatePreparedScene()
        {
            string path=SpawnMapBuild.Folder+"prepared-scene.json";
            if (!File.Exists(path)) throw new InvalidOperationException("Run SpawnVisualReview.BakeAndRender before building the visual scene.");
            var record=JsonUtility.FromJson<PreparedScene>(File.ReadAllText(path));
            if (record.lightmaps<1 || record.sceneSha256!=Digest(SpawnMapBuild.ScenePath) ||
                record.mapBindingsSha256!=Digest(SpawnMapBuild.Folder+"map-bindings.json") || record.sourceSha256!=SourceDigest())
                throw new InvalidOperationException("Prepared spawn scene is stale; regenerate lighting and inspect the views.");
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            foreach (var room in map.rooms) { SpawnMapBuild.CheckHash(room.mesh,room.meshSha256); SpawnMapBuild.CheckHash(room.collision,room.collisionSha256); }
            var package=map.materials.Single(p=>p.room=="spawn-room");
            SpawnMapBuild.CheckHash(package.letteringMesh.file,package.letteringMesh.sha256);
            foreach (var atlas in package.atlases)
                foreach (var texture in new[] {atlas.albedo,atlas.normal,atlas.metallicSmoothness,atlas.emission})
                    SpawnMapBuild.CheckHash(texture.file,texture.sha256);
            SpawnMapBuild.CheckHash(package.displayLut.file,package.displayLut.sha256);
            foreach (var definition in package.definitions.Where(d=>d.directEmission!=null && !string.IsNullOrEmpty(d.directEmission.file)))
                SpawnMapBuild.CheckHash(definition.directEmission.file,definition.directEmission.sha256);
        }
        private static string Digest(string path)
        { using var hash=SHA256.Create(); using var stream=File.OpenRead(path); return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-","").ToLowerInvariant(); }
        private static string SourceDigest()
        {
            using var hash=SHA256.Create(); using var bytes=new MemoryStream();
            foreach (var directory in new[] {"Assets/CriticalShift/Features/Player","Assets/CriticalShift/Bootstrap/Player"})
                foreach (var path in Directory.GetFiles(directory,"*",SearchOption.AllDirectories).Where(p=>p.EndsWith(".cs",StringComparison.Ordinal)||p.EndsWith(".shader",StringComparison.Ordinal)).OrderBy(p=>p,StringComparer.Ordinal))
                { var file=File.ReadAllBytes(path); bytes.Write(file,0,file.Length); }
            return BitConverter.ToString(hash.ComputeHash(bytes.ToArray())).Replace("-","").ToLowerInvariant();
        }

        public static void Render()
        {
            if (SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null) throw new InvalidOperationException("Captures require a real graphics context.");
            EditorSceneManager.OpenScene(SpawnMapBuild.ScenePath);
            LightProbes.Tetrahedralize();ReflectionProbe.UpdateCachedState();
            var persistedProbes=UnityEngine.Object.FindObjectsByType<ReflectionProbe>();
            if(persistedProbes.Length!=3 || persistedProbes.Any(p=>p.mode!=ReflectionProbeMode.Custom || p.customBakedTexture==null))
                throw new InvalidOperationException("Spawn requires three persisted reflection cubemaps.");
            var args=Environment.GetCommandLineArgs();
            string Argument(string flag)
            { int i=Array.IndexOf(args,flag); if (i<0 || i+1>=args.Length) throw new ArgumentException("Missing "+flag); return Path.GetFullPath(args[i+1]); }
            string output=Argument("-csCapturePath"); Directory.CreateDirectory(output);
            var map=JsonUtility.FromJson<ExportMap>(File.ReadAllText(SpawnMapBuild.Folder+"map-bindings.json"));
            int cameraFile=Array.IndexOf(args,"-csCameraFile");
            var views=cameraFile>=0 ? JsonUtility.FromJson<SourceViews>(File.ReadAllText(Argument("-csCameraFile"))) : map.validationViews;
            if (views==null || views.views==null || views.views.Length!=3) throw new InvalidOperationException("Missing the three authored camera bindings.");
            var root=GameObject.Find("ROOM_spawn-room").transform;
            Debug.Log("CS_LIGHTMAP_CAPTURE count="+LightmapSettings.lightmaps.Length+" data="+Lightmapping.lightingDataAsset);
            var worker=GameObject.Find("Local crew worker"); worker.SetActive(false);
            foreach (var door in UnityEngine.Object.FindObjectsByType<MovingDoor>()) door.Capture();
            var display=SpawnSurfaceBuild.View(map.materials.Single(p=>p.room=="spawn-room"));
            foreach (var view in views.views)
            {
                var node=new GameObject("Validation camera "+view.name); node.transform.SetParent(root,false);
                node.transform.localPosition=V(view.position); node.transform.localRotation=Quaternion.LookRotation(V(view.forward),V(view.up));
                var camera=node.AddComponent<Camera>(); camera.fieldOfView=view.verticalFov; camera.nearClipPlane=0.05f; camera.farClipPlane=250;
                camera.allowHDR=true; camera.allowMSAA=true; camera.renderingPath=RenderingPath.Forward;
                camera.clearFlags=CameraClearFlags.SolidColor; camera.backgroundColor=Color.black;
                if (Array.IndexOf(args,"-csRawCapture")<0) node.AddComponent<BlenderView>().Configure(display);
                var target=new RenderTexture(1440,810,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);
                target.antiAliasing=4;
                camera.targetTexture=target; camera.Render();
                var previous=RenderTexture.active; RenderTexture.active=target;
                var pixels=new Texture2D(1440,810,TextureFormat.RGB24,false,false);
                pixels.ReadPixels(new Rect(0,0,1440,810),0,0); pixels.Apply();
                File.WriteAllBytes(Path.Combine(output,view.name+".png"),pixels.EncodeToPNG());
                RenderTexture.active=previous; camera.targetTexture=null;
                UnityEngine.Object.DestroyImmediate(pixels); UnityEngine.Object.DestroyImmediate(target); UnityEngine.Object.DestroyImmediate(node);
            }
            Debug.Log("CS_SPAWN_VISUAL_CAPTURE_OK; graphics="+SystemInfo.graphicsDeviceName+"; scene not saved by captures");
        }
        private static Vector3 V(float[] v)=>new Vector3(v[0],v[2],v[1]);
    }
}
