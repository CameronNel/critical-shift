using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Player.Editor
{
    [Serializable] public sealed class ExportPose { public float[] position, rotation; }
    [Serializable] public sealed class ExportDoor { public string name, node; public ExportPose closed, opened; }
    [Serializable] public sealed class ExportObject { public string source, node; public bool visible, dynamic, sourceUv, lettering, wallSurface, sourceShadowExcluded; public string[] materials, faceMaterials; public int[] deliveryUvAxes; }
    [Serializable] public sealed class ExportLight { public float[] position, color, rotation; public float power, size, sizeY, radius, angle, spotSize, spotBlend; public bool normalized, softFalloff; public string name, type; }
    [Serializable] public sealed class ExportAnchor { public string name, node; public float[] position; }
    [Serializable] public sealed class ExportRoom
    {
        public string key, mesh, collision, meshSha256, collisionSha256;
        public float[] translation; public float yaw; public int collisionTriangles; public ExportObject[] objects; public ExportLight[] lights;
    }
    [Serializable] public sealed class ExportMap { public int schema; public string mapCommit; public ExportRoom[] rooms; public ExportAnchor[] anchors; public ExportDoor[] doors; public SurfacePackage[] materials; public SourceViews validationViews; }
    [Serializable] public sealed class ExportClip { public string name; public float first, last; public bool loop, derivative; }
    [Serializable] public sealed class ExportWorkerMesh { public string name, region; public bool suit, head; public string[] materials; }
    [Serializable] public sealed class ExportRig { public string rig_commit, fbx_sha256, animationFile, animationSha256; public int fps; public float seatedSupportHeight; public ExportClip[] clips; public ExportWorkerMesh[] meshes; public SurfacePackage surfaces; }

    // Generates an isolated runtime scene from exact source/export bindings. Never saves a Blender authoring file.
    public static class SpawnMapBuild
    {
        internal const string Folder = "Assets/CriticalShift/Generated/Spawn/";
        public const string ScenePath = "Assets/CriticalShift/Generated/Spawn/AssembledMap.unity";
        [MenuItem("Critical Shift/Spawn/Create assembled map scene")]
        public static void Create()
        {
            if (UnityEngine.Application.unityVersion != "6000.4.3f1") throw new InvalidOperationException("Use the pinned 6000.4.3f1 editor.");
            var map = JsonUtility.FromJson<ExportMap>(File.ReadAllText(Folder + "map-bindings.json"));
            var rig = JsonUtility.FromJson<ExportRig>(File.ReadAllText(Folder + "rig-bindings.json"));
            var requiredRooms=new[] {"front-end-area","spawn-room","mine","refinery","medical-reanimation","fuel-corridor"};
            if (map.schema != 1 || map.rooms == null || map.rooms.Select(r=>r.key).Distinct().Count()!=map.rooms.Length ||
                requiredRooms.Any(key=>!map.rooms.Any(r=>r.key==key)) || rig.fps != 24 || rig.clips.Length != 52)
                throw new InvalidOperationException("Unexpected current-map/rig inventory. Regenerate and review the interface.");
            foreach (var room in map.rooms)
            { CheckHash(room.mesh, room.meshSha256); CheckHash(room.collision, room.collisionSha256); }
            CheckHash("CrewWorker.fbx", rig.fbx_sha256);
            CheckHash(rig.animationFile,rig.animationSha256);
            AssetDatabase.Refresh();
            PlayerSettings.colorSpace = ColorSpace.Linear;
            UnityEngine.Rendering.GraphicsSettings.lightsUseLinearIntensity = true;
            QualitySettings.pixelLightCount = 12; QualitySettings.shadows = ShadowQuality.All;
            QualitySettings.antiAliasing = 4;
            QualitySettings.shadowResolution = ShadowResolution.VeryHigh; QualitySettings.shadowDistance = 25;
            QualitySettings.shadowmaskMode = ShadowmaskMode.Shadowmask;
            var package=map.materials.Single(p => p.room == "spawn-room");
            var surfaces = map.materials.SelectMany(p=>SpawnSurfaceBuild.Materials(p)).ToDictionary(p=>p.Key,p=>p.Value,StringComparer.Ordinal);
            CheckHash(package.letteringMesh.file,package.letteringMesh.sha256);
            Import(package.letteringMesh.file,false,readable:true);
            var lettering=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+package.letteringMesh.file)
                .GetComponentsInChildren<MeshFilter>().ToDictionary(f=>f.name,StringComparer.Ordinal);
            CheckHash(package.wallMesh.file,package.wallMesh.sha256);
            Import(package.wallMesh.file,false,readable:true);
            var wallMeshes=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+package.wallMesh.file)
                .GetComponentsInChildren<MeshFilter>().ToDictionary(f=>f.name,StringComparer.Ordinal);
            foreach (var room in map.rooms) { Import(room.mesh, false, readable: room.key == "spawn-room"); Import(room.collision, false, readable: true); }
            var contextPackage=map.materials.SingleOrDefault(p=>p.room=="mine");
            var contextBindings=(contextPackage?.contextObjects ?? Array.Empty<ExportObject>()).ToDictionary(b=>b.node,StringComparer.Ordinal);
            var contextMeshes=new Dictionary<string,MeshFilter>(StringComparer.Ordinal);
            if(contextPackage?.contextMesh!=null)
            {
                CheckHash(contextPackage.contextMesh.file,contextPackage.contextMesh.sha256);
                Import(contextPackage.contextMesh.file,false,readable:true);
                contextMeshes=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+contextPackage.contextMesh.file)
                    .GetComponentsInChildren<MeshFilter>().ToDictionary(f=>f.name,StringComparer.Ordinal);
            }
            Import("CrewWorker.fbx", true);
            Import(rig.animationFile,true,clips:rig.clips);
            var controller = Controller(rig);
            if (!UnityEngine.Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Critical Shift — assembled map " + map.mapCommit.Substring(0, 8));
            var host = root.AddComponent<LocalShiftHost>();
            var nodes = new Dictionary<string, Transform>();
            Transform spawnRoot = null;
            foreach (var room in map.rooms)
            {
                var roomRoot = new GameObject("ROOM_" + room.key); roomRoot.transform.SetParent(root.transform, false);
                roomRoot.transform.localPosition = V(room.translation); roomRoot.transform.localRotation = Quaternion.Euler(0, -room.yaw, 0);
                var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Folder + room.mesh));
                // The FBX root carries Blender-to-Unity axis correction. Placement belongs to a separate parent.
                model.transform.SetParent(roomRoot.transform, false);
                // Runtime carryables must leave the imported hierarchy. Editor prefab instances
                // reject that reparenting; unpack this scene instance without changing its FBX.
                if (room.key == "spawn-room")
                    PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var pointLights=room.lights.Where(l=>l.type=="POINT").Select(l=>roomRoot.transform.TransformPoint(V(l.position))).ToArray();
                foreach (var node in model.GetComponentsInChildren<Transform>(true))
                    if (node.name.StartsWith("CS_", StringComparison.Ordinal)) nodes.Add(node.name, node);
                foreach (var originalBinding in room.objects)
                {
                    var binding=contextBindings.TryGetValue(originalBinding.node,out var contextBinding) ? contextBinding : originalBinding;
                    if (!nodes.TryGetValue(binding.node, out var node)) throw new InvalidOperationException("Missing exported node: " + binding.node);
                    var renderer = node.GetComponent<Renderer>(); if (renderer != null) renderer.enabled = binding.visible;
                    if(contextBindings.ContainsKey(binding.node))
                    {
                        var target=node.GetComponent<MeshFilter>();var source=contextMeshes[binding.node];
                        var mesh=UnityEngine.Object.Instantiate(source.sharedMesh);
                        var transform=node.worldToLocalMatrix*roomRoot.transform.localToWorldMatrix*source.transform.localToWorldMatrix;
                        mesh.vertices=mesh.vertices.Select(v=>transform.MultiplyPoint3x4(v)).ToArray();
                        var normalTransform=transform.inverse.transpose;
                        mesh.normals=mesh.normals.Select(n=>normalTransform.MultiplyVector(n).normalized).ToArray();
                        mesh.RecalculateBounds();mesh.RecalculateTangents();
                        if((mesh.bounds.center-target.sharedMesh.bounds.center).magnitude>0.002f ||
                           (mesh.bounds.size-target.sharedMesh.bounds.size).magnitude>0.002f || mesh.triangles.Length!=target.sharedMesh.triangles.Length)
                            throw new InvalidOperationException("Mine context overlay changed geometry: "+binding.node+
                                "; sourceBounds="+mesh.bounds+"; targetBounds="+target.sharedMesh.bounds+
                                "; sourceIndices="+mesh.triangles.Length+"; targetIndices="+target.sharedMesh.triangles.Length);
                        string meshPath=Folder+"Surfaces/"+binding.node+"-mine-context.asset";
                        AssetDatabase.DeleteAsset(meshPath);AssetDatabase.CreateAsset(mesh,meshPath);target.sharedMesh=mesh;
                        renderer.sharedMaterials=source.GetComponent<Renderer>().sharedMaterials;
                    }
                    if(binding.lettering || binding.wallSurface)
                    {
                        var glyphFilter=node.GetComponent<MeshFilter>();
                        var source=binding.wallSurface ? wallMeshes[binding.node+"__Walls"] : lettering[binding.node+"__Lettering"];
                        var glyphMesh=UnityEngine.Object.Instantiate(source.sharedMesh);
                        var transform=node.worldToLocalMatrix*roomRoot.transform.localToWorldMatrix*source.transform.localToWorldMatrix;
                        glyphMesh.vertices=glyphMesh.vertices.Select(v=>transform.MultiplyPoint3x4(v)).ToArray();
                        var normalTransform=transform.inverse.transpose;
                        glyphMesh.normals=glyphMesh.normals.Select(n=>normalTransform.MultiplyVector(n).normalized).ToArray();
                        glyphMesh.RecalculateBounds();glyphMesh.RecalculateTangents();
                        if((glyphMesh.bounds.center-glyphFilter.sharedMesh.bounds.center).magnitude>0.002f ||
                           (glyphMesh.bounds.size-glyphFilter.sharedMesh.bounds.size).magnitude>0.002f ||
                           glyphMesh.triangles.Length!=glyphFilter.sharedMesh.triangles.Length)
                            throw new InvalidOperationException("Surface delivery changed source geometry: "+binding.node);
                        string meshPath=Folder+"Surfaces/"+binding.node+(binding.wallSurface?"-wall":"-lettering")+".asset";
                        AssetDatabase.DeleteAsset(meshPath);AssetDatabase.CreateAsset(glyphMesh,meshPath);glyphFilter.sharedMesh=glyphMesh;
                        renderer.sharedMaterials=source.GetComponent<Renderer>().sharedMaterials;
                    }
                    if (renderer != null && binding.materials != null)
                    {
                        var expectedKeys=binding.faceMaterials ?? binding.materials;
                        if (binding.faceMaterials==null && renderer.sharedMaterials.Length != expectedKeys.Length) throw new InvalidOperationException("Surface slot inventory changed: " + binding.node);
                        var importedKeys=renderer.sharedMaterials.Select(material=>material.name).ToArray();
                        if (expectedKeys.Length>1 && !importedKeys.Distinct().OrderBy(key=>key,StringComparer.Ordinal).SequenceEqual(expectedKeys.Distinct().OrderBy(key=>key,StringComparer.Ordinal)))
                            throw new InvalidOperationException("Imported surface names changed: "+binding.node+"; expected="+string.Join(",",expectedKeys)+"; actual="+string.Join(",",importedKeys));
                        if(binding.faceMaterials!=null && expectedKeys.Length==1 && importedKeys.Any(key=>key!=expectedKeys[0] && key!="Default-Material"))
                            throw new InvalidOperationException("Imported mine surface changed: "+binding.node);
                        // FBX orders slots by first face use, rather than the source datablock's slot array.
                        // Some single-slot line/text meshes import as Default-Material. Their explicit
                        // source binding is unambiguous; multi-slot meshes must match imported names.
                        // FBX also removes unused slots and collapses repeated materials. Mine's
                        // declared face-material set verifies that every actually used shader survives.
                        renderer.sharedMaterials = (expectedKeys.Length==1 ? Enumerable.Repeat(expectedKeys[0],importedKeys.Length) : importedKeys).Select(key => surfaces[key]).ToArray();
                        if (binding.sourceUv || binding.deliveryUvAxes!=null)
                        {
                            var sourceFilter=node.GetComponent<MeshFilter>();var sourceMesh=UnityEngine.Object.Instantiate(sourceFilter.sharedMesh);
                            if(binding.sourceUv)
                            {
                                if (sourceMesh.uv3.Length!=sourceMesh.vertexCount) throw new InvalidOperationException("Missing original screen UV coordinates.");
                                sourceMesh.uv=sourceMesh.uv3;
                            }
                            else
                            {
                                var axes=binding.deliveryUvAxes;
                                if(axes.Length!=2 || axes.Any(a=>a<0 || a>2) || axes[0]==axes[1]) throw new InvalidOperationException("Invalid delivery projection axes.");
                                var bounds=sourceMesh.bounds;
                                sourceMesh.uv=sourceMesh.vertices.Select(v=>new Vector2((v[axes[0]]-bounds.min[axes[0]])/bounds.size[axes[0]],(v[axes[1]]-bounds.min[axes[1]])/bounds.size[axes[1]])).ToArray();
                                sourceMesh.RecalculateTangents();
                            }
                            string meshPath=Folder+"Surfaces/"+binding.node+"-sourceUV.asset";
                            AssetDatabase.DeleteAsset(meshPath);AssetDatabase.CreateAsset(sourceMesh,meshPath);sourceFilter.sharedMesh=sourceMesh;
                        }
                        renderer.receiveShadows = true;
                        renderer.shadowCastingMode = binding.visible && !binding.sourceShadowExcluded ? UnityEngine.Rendering.ShadowCastingMode.On : UnityEngine.Rendering.ShadowCastingMode.Off;
                        if (binding.visible)
                            GameObjectUtility.SetStaticEditorFlags(node.gameObject, StaticEditorFlags.ReflectionProbeStatic |
                                (binding.dynamic ? 0 : StaticEditorFlags.ContributeGI));
                        if(room.key=="spawn-room" || room.key=="mine" || contextBindings.ContainsKey(binding.node))
                            SpawnSurfaceBuild.SplitEmbeddedEmitter(node,pointLights,contextBindings.ContainsKey(binding.node) ? contextPackage : map.materials.Single(p=>p.room==room.key));
                        if((room.key=="mine" || contextBindings.ContainsKey(binding.node)) && renderer is MeshRenderer mineRenderer)
                        {
                            mineRenderer.scaleInLightmap=binding.source=="context_ground" ? 0.1f : 1;
                            var size=mineRenderer.bounds.size;
                            if(Mathf.Max(size.x,Mathf.Max(size.y,size.z))<0.5f)
                            {
                                mineRenderer.receiveGI=ReceiveGI.LightProbes;
                                GameObjectUtility.SetStaticEditorFlags(node.gameObject,StaticEditorFlags.ReflectionProbeStatic);
                            }
                        }
                        if(contextBindings.ContainsKey(binding.node) && binding.source=="cliff_face")
                        {
                            // This single sheet is seen from its authored back.
                            // One baked chart lights the opposite face green.
                            // Retain its baked occlusion/bounce contribution,
                            // and shade the visible side with direct moonlight
                            // and the authored ambient rather than that chart.
                            ((MeshRenderer)renderer).receiveGI=ReceiveGI.LightProbes;
                            renderer.lightProbeUsage=UnityEngine.Rendering.LightProbeUsage.Off;
                            renderer.reflectionProbeUsage=UnityEngine.Rendering.ReflectionProbeUsage.Off;
                        }
                        if(binding.source=="LIFE_whiteboard_surface" ||
                           (binding.source.StartsWith("LIFE_socket_",StringComparison.Ordinal) && binding.source.EndsWith("_face",StringComparison.Ordinal)))
                        {
                            // Its authored front normal faces the wall. Runtime two-sided shading is
                            // correct, but one baked chart cannot represent both sides reliably.
                            ((MeshRenderer)renderer).receiveGI=ReceiveGI.LightProbes;
                            GameObjectUtility.SetStaticEditorFlags(node.gameObject,StaticEditorFlags.ReflectionProbeStatic);
                        }
                    }
                }
                if(room.key=="spawn-room") SpawnSurfaceBuild.BindSuitOcclusion(nodes,roomRoot.transform,package);
                RestoreCollision(roomRoot.transform,room);
                foreach (var sourceLight in room.lights)
                {
                    if(room.key=="front-end-area" && contextBindings.Count>0 && sourceLight.type=="SUN")
                        continue; // The scoped context contract supplies its omitted source rotation.
                    if(room.key=="front-end-area" && contextBindings.Count>0 && sourceLight.type=="SPOT")
                        continue; // Preserve the complete authored spot contract below.
                    var lamp = new GameObject(sourceLight.name ?? "Room practical"); lamp.transform.SetParent(roomRoot.transform, false);
                    lamp.transform.localPosition = V(sourceLight.position);
                    var light = lamp.AddComponent<Light>(); light.type = LightType.Point; light.range = 12;
                    light.color = new Color(sourceLight.color[0], sourceLight.color[1], sourceLight.color[2]).gamma;
                    // Existing rooms retain their calibrated legacy intensity. The mine's
                    // explicit physical-point adapter overrides this scale below.
                    light.intensity = sourceLight.power / 100;
                    light.shapeRadius = Mathf.Max(sourceLight.radius,0.001f);
                    light.shadows = LightShadows.Soft;
                    light.shadowBias = 0.015f; light.shadowNormalBias = 0.025f; light.bounceIntensity = 1;
                    if(room.key=="spawn-room") light.shadowNearPlane=0.01f;
                    light.renderMode = LightRenderMode.ForcePixel;
                    if(room.key=="mine")
                    {
                        light.shadowNearPlane=0.01f;
                        light.lightmapBakeType=sourceLight.name.IndexOf("lantern",StringComparison.OrdinalIgnoreCase)>=0 ? LightmapBakeType.Mixed : LightmapBakeType.Baked;
                        if(sourceLight.type=="SUN")
                        {
                            MineVisualLighting.ConfigureSourceSun(light,sourceLight);
                        }
                        else if(sourceLight.type=="POINT") MinePointLighting.Configure(light,sourceLight);
                    }
                    if(room.key=="front-end-area" && contextBindings.Count>0 && lamp.transform.position.x<=-23 && lamp.transform.position.z>=-99 && lamp.transform.position.z<=-44)
                    {
                        light.lightmapBakeType=LightmapBakeType.Baked;light.shadowNearPlane=0.01f;
                        if(sourceLight.type=="AREA")
                        {
                            light.type=LightType.Rectangle;
                            light.areaSize=new Vector2(sourceLight.size,sourceLight.sizeY>0 ? sourceLight.sizeY : sourceLight.size);
                            light.intensity=sourceLight.power/(Mathf.PI*Mathf.Max(light.areaSize.x*light.areaSize.y,0.001f));
                            var q=sourceLight.rotation;var rotation=new Quaternion(q[1],q[2],q[3],q[0]);
                            var forward=rotation*Vector3.back;var up=rotation*Vector3.up;
                            light.transform.localRotation=Quaternion.LookRotation(V(new[] {forward.x,forward.y,forward.z}),V(new[] {up.x,up.y,up.z}));
                        }
                    }
                    if (room.key == "spawn-room")
                    {
                        if (sourceLight.type == "AREA")
                        {
                            // Built-in supports authored rectangle area lights in its lightmap bake.
                            light.type = LightType.Rectangle;
                            light.areaSize = new Vector2(sourceLight.size, sourceLight.sizeY > 0 ? sourceLight.sizeY : sourceLight.size);
                            // The source area power is total energy; Unity's area intensity scales with emitting area.
                            light.intensity=sourceLight.power/(Mathf.PI*Mathf.Max(light.areaSize.x*light.areaSize.y,0.001f));
                            var q = sourceLight.rotation;
                            var rotation = new Quaternion(q[1],q[2],q[3],q[0]);
                            var forward = rotation * Vector3.back; var up = rotation * Vector3.up;
                            light.transform.localRotation = Quaternion.LookRotation(new Vector3(forward.x,forward.z,forward.y), new Vector3(up.x,up.z,up.y));
                            light.lightmapBakeType = LightmapBakeType.Baked;
                        }
                        else light.lightmapBakeType = sourceLight.name.Contains("_pendant") ? LightmapBakeType.Mixed : LightmapBakeType.Baked;
                    }
                }
                if(room.key=="front-end-area" && contextBindings.Count>0)
                {
                    var context=map.materials.Single(p=>p.room=="mine");
                    if(context.contextSunLights==null || context.contextSunLights.Length==0)
                        throw new InvalidOperationException("Regenerate the mine context's authored sun contract.");
                    foreach(var sun in context.contextSunLights)
                    {
                        var lamp=new GameObject(sun.name);lamp.transform.SetParent(roomRoot.transform,false);
                        lamp.transform.localPosition=V(sun.position);
                        var light=lamp.AddComponent<Light>();light.color=new Color(sun.color[0],sun.color[1],sun.color[2]).gamma;
                        light.lightmapBakeType=LightmapBakeType.Mixed;light.shadows=LightShadows.Soft;
                        light.shadowBias=.015f;light.shadowNormalBias=.025f;light.renderMode=LightRenderMode.ForcePixel;
                        MineVisualLighting.ConfigureSourceSun(light,sun);
                    }
                    if(context.contextSpotLights==null || context.contextSpotLights.Length==0)
                        throw new InvalidOperationException("Regenerate the mine context's authored spot contract.");
                    var authoredSpots=room.lights.Where(l=>l.type=="SPOT").ToArray();
                    if(authoredSpots.Any(s=>string.IsNullOrEmpty(s.name)) ||
                        authoredSpots.Select(s=>s.name).Distinct().Count()!=authoredSpots.Length ||
                        context.contextSpotLights.Select(s=>s.name).Distinct().Count()!=context.contextSpotLights.Length ||
                        !authoredSpots.Select(s=>s.name).OrderBy(s=>s).SequenceEqual(context.contextSpotLights.Select(s=>s.name).OrderBy(s=>s)))
                        throw new InvalidOperationException("Context spotlight inventory differs from the authored room.");
                    foreach(var spot in context.contextSpotLights)
                    {
                        var original=authoredSpots.Single(s=>s.name==spot.name);
                        MineSpotLighting.ValidateSource(original);MineSpotLighting.ValidateSource(spot);
                        if(Vector3.Distance(V(original.position),V(spot.position))>.0001f ||
                            original.rotation==null || spot.rotation==null || original.rotation.Length!=4 || spot.rotation.Length!=4 ||
                            original.rotation.Zip(spot.rotation,(a,b)=>Mathf.Abs(a-b)).Any(d=>d>.0001f) ||
                            original.color.Zip(spot.color,(a,b)=>Mathf.Abs(a-b)).Any(d=>d>.0001f) ||
                            Mathf.Abs(original.power-spot.power)>.0001f || Mathf.Abs(original.radius-spot.radius)>.00001f ||
                            Mathf.Abs(original.spotSize-spot.spotSize)>.00001f || Mathf.Abs(original.spotBlend-spot.spotBlend)>.00001f ||
                            original.type!=spot.type)
                            throw new InvalidOperationException("Context spotlight does not match its authored room: "+spot.name);
                        var lamp=new GameObject(spot.name);lamp.transform.SetParent(roomRoot.transform,false);
                        lamp.transform.localPosition=V(spot.position);
                        var light=lamp.AddComponent<Light>();light.range=12;
                        light.color=new Color(spot.color[0],spot.color[1],spot.color[2]).gamma;
                        light.shapeRadius=spot.radius;light.shadows=LightShadows.Soft;
                        light.shadowNearPlane=.01f;light.shadowBias=.015f;light.shadowNormalBias=.025f;
                        light.bounceIntensity=1;light.renderMode=LightRenderMode.ForcePixel;
                        if(lamp.transform.position.x<=-23 && lamp.transform.position.z>=-99 && lamp.transform.position.z<=-44)
                            light.lightmapBakeType=LightmapBakeType.Baked;
                        MineSpotLighting.Configure(light,spot);
                    }
                }
                if (room.key == "spawn-room") spawnRoot = roomRoot.transform;
            }
            if (spawnRoot == null) throw new InvalidOperationException("Missing assembled spawn room.");
            foreach (var anchor in map.anchors)
            {
                var node = Require(nodes, anchor.node);
                var actual = spawnRoot.InverseTransformPoint(node.position); var expected = V(anchor.position);
                if (Vector3.Distance(actual, expected) > 0.02f)
                    throw new InvalidOperationException("Imported scale/axes changed a spawn binding: " + anchor.name +
                        "; actual=" + actual.ToString("F4") + "; expected=" + expected.ToString("F4") +
                        "; local rotation=" + node.localEulerAngles.ToString("F2") + "; room rotation=" + spawnRoot.localEulerAngles.ToString("F2"));
            }
            var actor = Worker(root.transform, Require(nodes, "CS_spawn-room_SPAWN_1"), host, rig, controller);
            var viewCamera = actor.GetComponentInChildren<Camera>(); viewCamera.allowHDR = true;
            viewCamera.renderingPath = RenderingPath.Forward; viewCamera.allowMSAA=true;
            viewCamera.gameObject.AddComponent<BlenderView>().Configure(SpawnSurfaceBuild.View(map.materials.Single(p => p.room == "spawn-room")));
            var targets = new List<InteractionTarget>(); var stations = new List<InteractionTarget>(); var controls = new List<SpawnControl>();
            var airlock = Door(root.transform, nodes, map, "Airlock", new[] { "AIRLOCK_leaf_L", "AIRLOCK_leaf_R" }, false);
            var airlockCentre = (Require(nodes, "CS_spawn-room_AIRLOCK_leaf_L").position + Require(nodes, "CS_spawn-room_AIRLOCK_leaf_R").position) * 0.5f;
            // Explicit controls on both approaches; independent of the leaf's animation.
            foreach (int side in new[] { -1, 1 })
                controls.Add(new SpawnControl { Door = airlock, PpeWarning = true, Label = "open/close airlock",
                    Shape = Trigger(root.transform, "Airlock control " + side, airlockCentre + Vector3.right * 1.45f + Vector3.up * 1.15f + Vector3.forward * side * 0.25f, new Vector3(0.3f, 0.45f, 0.18f)) });
            for (int i = 1; i <= 4; i++)
            {
                string code = i.ToString("00");
                var door = Door(root.transform, nodes, map, "Locker " + i, new[] { "BELONG_" + code + "_door_L", "BELONG_" + code + "_door_R" }, true);
                var left = Require(nodes, "CS_spawn-room_BELONG_" + code + "_door_L");
                var right = Require(nodes, "CS_spawn-room_BELONG_" + code + "_door_R");
                var front = (left.position + right.position) * 0.5f;
                var proxy = Trigger(root.transform, "Suit station " + i, front + Vector3.up * 1.1f, new Vector3(0.55f, 0.65f, 0.18f));
                var body = proxy.gameObject.AddComponent<Rigidbody>(); body.isKinematic = true; body.useGravity = false;
                var station = proxy.gameObject.AddComponent<InteractionTarget>();
                station.Configure(Id(20 + i), PlayerTargetKind.ProtectiveEquipment, "prepare suit at locker " + i, proxy, body);
                var outward = spawnRoot.forward * (spawnRoot.InverseTransformPoint(front).z > 4 ? -1 : 1);
                var position = front + outward * 0.9f; position.y = spawnRoot.position.y + 0.06f;
                var standing = Anchor(root.transform, "Locker " + i + " standing position", position);
                standing.rotation = Quaternion.LookRotation(-outward);
                station.ConfigureStation(Require(nodes, "CS_spawn-room_PPE_" + code + "_suit"), standing);
                targets.Add(station); stations.Add(station);
                controls.Add(new SpawnControl { Door = door, Station = station, Label = "open/close locker " + i,
                    Shape = Trigger(root.transform, "Locker control " + i, left.position + Vector3.up * 1.25f, new Vector3(0.16f, 0.35f, 0.22f)) });
            }
            for (int i = 1; i <= 2; i++)
            {
                var bench = Require(nodes, "CS_spawn-room_BRIEFING_bench_" + i.ToString("00"));
                var slat = Require(nodes, "CS_spawn-room_BRIEFING_bench_" + i.ToString("00") + "_laminate_slat.001");
                var surface = slat.GetComponent<Renderer>().bounds.max.y;
                for (int seat = 0; seat < 2; seat++)
                {
                    // The authored bench's local X spans the seat; local -Y faces its TV.
                    var centre = bench.position + bench.right * (seat == 0 ? -0.27f : 0.27f); centre.y = surface + 0.03f;
                    var shape = Trigger(root.transform, $"Bench {i} seat {seat + 1}", centre, new Vector3(0.42f, 0.12f, 0.43f));
                    var pose = Anchor(root.transform, "Seated body pose", centre); pose.rotation = Quaternion.LookRotation(-bench.up);
                    var exit = Anchor(root.transform, "Seat exit", centre - bench.up * 0.95f); exit.position = new Vector3(exit.position.x, bench.position.y + 0.05f, exit.position.z);
                    var target = shape.gameObject.AddComponent<InteractionTarget>(); target.Configure(Id(30 + i * 2 + seat), PlayerTargetKind.Seat, "sit on bench", shape, anchor: pose, exitPose: exit);
                    targets.Add(target);
                }
            }
            foreach (int i in new[] { 1, 3 })
            {
                var prop = Require(nodes, "CS_spawn-room_BELONG_" + i.ToString("00") + "_thermos");
                // The runtime root is world-aligned; the imported prop carries FBX axis
                // correction. Copy world bounds so the collider follows the visible axes.
                var worldBounds = prop.GetComponentsInChildren<Renderer>(true).Select(renderer => renderer.bounds)
                    .Aggregate((bounds, next) => { bounds.Encapsulate(next); return bounds; });
                var centre = worldBounds.center;
                var originalPosition = prop.position; var originalRotation = prop.rotation; var originalScale = prop.lossyScale;
                var item = new GameObject("Carryable thermos " + i); item.transform.SetParent(root.transform, false); item.transform.position = centre;
                var shape = item.AddComponent<BoxCollider>(); shape.size = worldBounds.size;
                prop.SetParent(item.transform, true);
                if (prop.parent != item.transform || Vector3.Distance(prop.position, originalPosition) > 0.0001f ||
                    Quaternion.Angle(prop.rotation, originalRotation) > 0.01f || Vector3.Distance(prop.lossyScale, originalScale) > 0.0001f)
                    throw new InvalidOperationException("Thermos visual extraction changed its source pose or failed: " + prop.name);
                var body = item.AddComponent<Rigidbody>(); body.mass = 0.5f; body.interpolation = RigidbodyInterpolation.Interpolate;
                var target = item.AddComponent<InteractionTarget>(); target.Configure(Id(100 + i), PlayerTargetKind.Carryable, "pick up thermos", shape, body);
                targets.Add(target);
            }
            var top = Require(nodes, "CS_spawn-room_BRIEFING_sideboard_laminate_top").GetComponent<Renderer>().bounds;
            Physics.SyncTransforms();
            var itemHalf = targets.Where(target => target.Kind == PlayerTargetKind.Carryable).Select(target => target.Shape.bounds.extents).Aggregate(Vector3.Max);
            var margin = itemHalf + Vector3.one * 0.025f;
            if (top.size.x <= margin.x * 2 || top.size.z <= margin.z * 2)
                throw new InvalidOperationException("The authored sideboard cannot support the imported thermos footprint.");
            Vector3? placementPoint = null;
            // Source decorations occupy the centre. Find a supported clear slot on
            // the authored tabletop; retain every solid object and the original height.
            var candidates = Enumerable.Range(0, 5).SelectMany(x => Enumerable.Range(0, 5).Select(z =>
                new Vector3(Mathf.Lerp(top.max.x - margin.x, top.min.x + margin.x, x / 4f), top.max.y + 0.18f,
                    Mathf.Lerp(top.min.z + margin.z, top.max.z - margin.z, z / 4f))))
                .OrderBy(candidate => new Vector2(candidate.x - top.center.x, candidate.z - top.center.z).sqrMagnitude);
            foreach (var candidate in candidates)
            {
                if (Physics.CheckBox(candidate, itemHalf + Vector3.one * 0.02f, Quaternion.identity, ~0, QueryTriggerInteraction.Ignore)) continue;
                bool supported = true;
                foreach (var corner in new[] { Vector3.zero, new Vector3(-itemHalf.x, 0, -itemHalf.z), new Vector3(-itemHalf.x, 0, itemHalf.z),
                    new Vector3(itemHalf.x, 0, -itemHalf.z), new Vector3(itemHalf.x, 0, itemHalf.z) })
                {
                    var origin = new Vector3(candidate.x, top.max.y + 0.01f, candidate.z) + corner;
                    if (!Physics.Raycast(origin, Vector3.down, out var contact, 0.025f, ~0, QueryTriggerInteraction.Ignore) ||
                        Mathf.Abs(contact.point.y - top.max.y) > 0.002f || Vector3.Dot(contact.normal, Vector3.up) < 0.9f)
                    { supported = false; break; }
                }
                if (supported) { placementPoint = candidate; break; }
            }
            if (!placementPoint.HasValue) throw new InvalidOperationException("No clear sideboard placement remains between authored decorations.");
            var point = placementPoint.Value;
            Debug.Log("CS_SPAWN_SIDEBOARD_SLOT_OK; point=" + point.ToString("F5") + "; footprint=" + (itemHalf * 2).ToString("F5"));
            var placementShape = Trigger(root.transform, "Sideboard placement", new Vector3(point.x, top.max.y + 0.06f, point.z), new Vector3(0.4f, 0.1f, 0.6f));
            var placement = placementShape.gameObject.AddComponent<InteractionTarget>();
            placement.Configure(Id(41), PlayerTargetKind.Placement, "place/take thermos", placementShape,
                anchor: Anchor(root.transform, "Sideboard item pose", point), slot: Id(61));
            targets.Add(placement);
            var pod = Door(root.transform, nodes, map, "Integrity chamber", new[] { "POD_door_L", "POD_door_R" }, true);
            var buttonNode = Require(nodes, "CS_spawn-room_POD_physical_button");
            var button = Trigger(root.transform, "Integrity test button", buttonNode.position, Vector3.one * 0.18f);
            var podPosition = Anchor(root.transform, "Integrity test position", Require(nodes, "CS_spawn-room_INTEGRITY_POD").position + Vector3.up * 0.05f);
            var indicators = new[] { "READY", "SEALED", "TESTING", "PASS", "INSPECT", "FAIL" }.Select(state => Require(nodes, "CS_spawn-room_POD_state_" + state).gameObject).ToArray();
            foreach (var indicator in indicators) foreach (var renderer in indicator.GetComponentsInChildren<Renderer>(true)) renderer.enabled = true;
            for (int i = 0; i < indicators.Length; i++) indicators[i].SetActive(i == 0);
            // The authored TV's screen remains in place; add only an interaction volume.
            var screenNode = Require(nodes, "CS_spawn-room_BRIEFING_TV_display");
            var screen = Trigger(root.transform, "Briefing screen", screenNode.GetComponent<Renderer>().bounds.center, new Vector3(0.15f, 0.65f, 1.1f));
            var bindings = root.AddComponent<SpawnRoomBindings>(); bindings.Configure(new[] { actor }, stations.ToArray(), controls.ToArray(), pod, button, podPosition, indicators, screen);
            host.ConfigureSpawn(bindings);
            var bootstrap = root.AddComponent<CriticalShift.Bootstrap.Player.PlayerRoomBootstrap>();
            bootstrap.Configure(host, new[] { actor }, targets.ToArray());
            using (var hash = System.Security.Cryptography.SHA256.Create())
                bootstrap.ConfigureMapIdentity(map.mapCommit,
                    BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(Folder+"map-bindings.json"))).Replace("-","").ToLowerInvariant(),
                    map.rooms.Select(room=>room.key).ToArray(),map.rooms.Select(room=>room.collisionTriangles).ToArray());
            RenderSettings.skybox = null;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = (new Color(0.32f, 0.36f, 0.55f) * 0.025f).gamma;
            RenderSettings.reflectionIntensity = 1;
            var minePackage=map.materials.SingleOrDefault(p=>p.room=="mine");
            if(minePackage!=null)
            {
                MineVisualLighting.ConfigureAssembly(minePackage.assemblyLighting);
                var bounds=spawnRoot.Find("Static collision — spawn-room").GetComponentInChildren<MeshCollider>().bounds;
                var sky=minePackage.assemblyLighting;
                var background=new Color(sky.world_color[0],sky.world_color[1],sky.world_color[2]).gamma*sky.world_strength;
                viewCamera.GetComponent<BlenderView>().ConfigureOutside(bounds,SpawnSurfaceBuild.View(minePackage),background);
            }
            Physics.SyncTransforms();
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new IOException("Could not save the isolated runtime scene.");
            Debug.Log("Generated current assembled map with spawn runtime bindings: " + map.mapCommit + ". Native tests and Player validation still required.");
        }
        internal static void RestoreCollision(Transform roomRoot,ExportRoom room)
        {
            var collisionModel=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+room.collision);
            var filters=collisionModel.GetComponentsInChildren<MeshFilter>(true);
            if(filters.Length!=1 || filters[0].sharedMesh==null || filters[0].sharedMesh.triangles.Length/3!=room.collisionTriangles)
                throw new InvalidOperationException("Room collision import changed or split: "+room.key);
            var collision=(GameObject)PrefabUtility.InstantiatePrefab(collisionModel);
            collision.name="Static collision — "+room.key;collision.transform.SetParent(roomRoot,false);
            var filter=collision.GetComponentInChildren<MeshFilter>(true);var mesh=filter.sharedMesh;var node=filter.gameObject;
            UnityEngine.Object.DestroyImmediate(filter.GetComponent<Renderer>());UnityEngine.Object.DestroyImmediate(filter);
            // Configure large-mesh cooking before assigning the source mesh.
            var collider=node.AddComponent<MeshCollider>();
            if(room.collisionTriangles>2000000) collider.cookingOptions&=~MeshColliderCookingOptions.UseFastMidphase;
            collider.sharedMesh=mesh;
        }

        public static void Build()
        {
            // Build the reviewed lightmapped scene. Regenerating it here would discard its lighting.
            SpawnVisualReview.ValidatePreparedScene();
            EditorSceneManager.OpenScene(ScenePath);
            PlayerSettings.colorSpace = ColorSpace.Linear;
            UnityEngine.Rendering.GraphicsSettings.lightsUseLinearIntensity = true;
            QualitySettings.pixelLightCount = 12; QualitySettings.shadows = ShadowQuality.All;
            QualitySettings.antiAliasing = 4;
            QualitySettings.shadowResolution = ShadowResolution.VeryHigh; QualitySettings.shadowDistance = 25;
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-csBuildPath");
            if (index < 0 || index + 1 >= args.Length) throw new BuildFailedException("-csBuildPath must name the executable.");
            var path = Path.GetFullPath(args[index + 1]); Directory.CreateDirectory(Path.GetDirectoryName(path));
            var target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneLinux64 && target != BuildTarget.StandaloneWindows64)
                throw new BuildFailedException("Only Linux64/Windows64 are in this local map scope.");
            var named = NamedBuildTarget.Standalone;
            PlayerSettings.companyName = "Critical Shift"; PlayerSettings.productName = "Critical Shift";
            PlayerSettings.SetApiCompatibilityLevel(named, ApiCompatibilityLevel.NET_Standard);
            PlayerSettings.SetScriptingBackend(named, ScriptingImplementation.Mono2x);
            PlayerSettings.SetManagedStrippingLevel(named, ManagedStrippingLevel.Disabled);
            PlayerSettings.bakeCollisionMeshes = true;
            if (UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline != null)
                throw new BuildFailedException("The prepared map requires Built-in rendering.");
            var options=BuildOptions.Development|BuildOptions.StrictMode;
            if(args.Contains("-csCompressedBuild")) options|=BuildOptions.CompressWithLz4HC;
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { ScenePath }, target = target,
                locationPathName = path, options = options });
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new BuildFailedException("Assembled map build failed.");
            Debug.Log("CS_SPAWN_MAP_BUILD_OK");
        }
        internal static void CheckHash(string file, string expected)
        {
            using var hash = SHA256.Create(); using var stream = File.OpenRead(Folder + file);
            string actual = BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
            if (actual != expected) throw new InvalidOperationException("Export hash mismatch: " + file);
        }
        private static void Import(string file, bool animated, bool readable = false, ExportClip[] clips = null)
        {
            var importer = AssetImporter.GetAtPath(Folder + file) as ModelImporter;
            if (importer == null) throw new InvalidOperationException("Expected the built-in FBX importer: " + file);
            string previous=EditorJsonUtility.ToJson(importer);
            ConfigureImporter(importer, animated, readable);
            if(animated && clips==null)
            { importer.importAnimation=false;importer.clipAnimations=Array.Empty<ModelImporterClipAnimation>(); }
            if (animated && clips!=null)
            {
                importer.animationType = ModelImporterAnimationType.Generic; importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                var takes = importer.defaultClipAnimations;
                foreach (var clip in clips)
                {
                    var take = takes.Single(t => t.name == clip.name || t.name.EndsWith("|" + clip.name, StringComparison.Ordinal));
                    take.name = clip.name; take.firstFrame = clip.first; take.lastFrame = clip.last; take.loopTime = clip.loop;
                    take.lockRootRotation = true; take.lockRootPositionXZ = true; take.lockRootHeightY = true;
                }
                importer.clipAnimations = takes;
            }
            if (previous!=EditorJsonUtility.ToJson(importer)) importer.SaveAndReimport();
        }
        internal static void ConfigureImporter(ModelImporter importer, bool animated, bool readable)
        {
            importer.globalScale = 1; importer.useFileScale = true; importer.bakeAxisConversion = true;
            importer.importAnimation = animated; importer.importLights = false; importer.importCameras = false;
            importer.isReadable = readable; importer.optimizeGameObjects = false;
            // Character surfaces are bound explicitly from the source manifest.
            // FBX's automatic material conversion cannot retain the face alpha graph.
            if(animated) importer.materialImportMode=ModelImporterMaterialImportMode.None;
            if (Path.GetFileName(importer.assetPath) == "Room-spawn-room.fbx" || Path.GetFileName(importer.assetPath) == "Lettering.fbx" || Path.GetFileName(importer.assetPath) == "Walls.fbx")
            { importer.weldVertices = false; importer.meshCompression = ModelImporterMeshCompression.Off; importer.generateSecondaryUV = true; importer.secondaryUVMinLightmapResolution = 40; importer.secondaryUVMinObjectScale = 0.1f; }
            if(Path.GetFileName(importer.assetPath)=="Room-mine.fbx" || Path.GetFileName(importer.assetPath)=="MineContext.fbx")
            { importer.weldVertices=false;importer.meshCompression=ModelImporterMeshCompression.Off;importer.generateSecondaryUV=false; }
            if(Path.GetFileName(importer.assetPath)=="Room-front-end-area.fbx")
                importer.weldVertices=false; // Match the overlay: retain authored faces before Unity's vertex welding.
            // Keep each room's complete collision mesh from the first import.
            importer.indexFormat = ModelImporterIndexFormat.UInt32;
            if (Path.GetFileName(importer.assetPath).StartsWith("Collision-", StringComparison.Ordinal))
            {
                // Welding coincident source vertices makes Unity discard faces before collision validation.
                // PhysX retains its normal mesh-cleaning/cooking pass on the complete imported mesh.
                importer.weldVertices = false; importer.optimizeMeshPolygons = false; importer.optimizeMeshVertices = false;
                importer.importNormals = ModelImporterNormals.None; importer.importTangents = ModelImporterTangents.None;
            }
            if (animated)
            { importer.animationType = ModelImporterAnimationType.Generic; importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel; }
        }
        private static AnimatorController Controller(ExportRig rig)
        {
            string path = Folder + "CrewWorker.controller"; AssetDatabase.DeleteAsset(path);
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path); var machine = controller.layers[0].stateMachine;
            var clips = AssetDatabase.LoadAllAssetsAtPath(Folder + rig.animationFile).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToArray();
            foreach (var definition in rig.clips)
            {
                var state = machine.AddState(definition.name); state.motion = clips.Single(c => c.name == definition.name);
                if (definition.name == "IDLE") machine.defaultState = state;
            }
            AssetDatabase.SaveAssets(); return controller;
        }
        private static FirstPersonWorker Worker(Transform parent, Transform spawn, LocalShiftHost host, ExportRig rig, AnimatorController controller)
        {
            var root = new GameObject("Local crew worker"); root.transform.SetParent(parent, false);
            root.transform.SetPositionAndRotation(spawn.position + Vector3.up * 0.06f, Quaternion.LookRotation(spawn.up, -spawn.forward));
            var worker = root.AddComponent<FirstPersonWorker>();
            var eye = Anchor(root.transform, "First-person camera", root.transform.position + Vector3.up * 1.4f);
            var camera = eye.gameObject.AddComponent<Camera>(); camera.nearClipPlane = 0.05f; camera.farClipPlane = 250; camera.fieldOfView = 60;
            var carry = Anchor(eye, "Carry anchor", eye.position + eye.forward * 1.1f);
            var gear = Anchor(root.transform, "Equipment anchor", root.transform.position);
            worker.Configure(Id(1), Id(11), camera, carry, gear); worker.ConfigureCharacter(1.55f, 1.4f, 1.6f);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Folder + "CrewWorker.fbx"));
            model.transform.SetParent(root.transform, false);
            var animator = model.GetComponent<Animator>() ?? model.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller; animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            animator.avatar = AssetDatabase.LoadAllAssetsAtPath(Folder + "CrewWorker.fbx").OfType<Avatar>().Single();
            var renderers = model.GetComponentsInChildren<Renderer>(true);
            var materials=SpawnSurfaceBuild.Materials(rig.surfaces);
            foreach(var record in rig.meshes)
            {
                var renderer=renderers.Single(r=>r.name==record.name);
                if(record.materials==null || renderer.sharedMaterials.Length!=record.materials.Length)
                    throw new InvalidOperationException("Suit material slots changed: "+record.name);
                renderer.sharedMaterials=record.materials.Select(key=>materials[key]).ToArray();
            }
            var meshes = rig.meshes.Select(record => new WorkerMesh { Renderer = renderers.Single(r => r.name == record.name),
                Suit = record.suit, Head = record.head, Covered = !string.IsNullOrEmpty(record.region) }).ToArray();
            foreach (var mesh in meshes)
            {
                mesh.Renderer.enabled = !mesh.Suit;
                mesh.Renderer.shadowCastingMode = mesh.Head ? UnityEngine.Rendering.ShadowCastingMode.ShadowsOnly : UnityEngine.Rendering.ShadowCastingMode.On;
            }
            root.AddComponent<WorkerAnimation>().Configure(animator, model.transform, worker, host, meshes, rig.seatedSupportHeight);
            return worker;
        }
        private static MovingDoor Door(Transform parent, Dictionary<string, Transform> nodes, ExportMap map, string name, string[] names, bool open)
        {
            var root = new GameObject(name); root.transform.SetParent(parent, false); var door = root.AddComponent<MovingDoor>();
            var leaves = names.Select(source =>
            {
                var binding = map.doors.Single(d => d.name == source); var node = Require(nodes, binding.node);
                var bounds = LocalBounds(node); var shape = node.gameObject.AddComponent<BoxCollider>(); shape.center = bounds.center; shape.size = bounds.size;
                shape.enabled = false; shape.isTrigger = true; // Query bounds only; collision uses the actual curved/hinged leaf mesh.
                var filters = node.GetComponentsInChildren<MeshFilter>(true);
                var combined = new Mesh { name = name + " collision", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
                combined.CombineMeshes(filters.Select(f => new CombineInstance { mesh = f.sharedMesh,
                    transform = node.worldToLocalMatrix * f.transform.localToWorldMatrix }).ToArray(), true, true);
                combined.RecalculateBounds();
                string path = Folder + "Door-" + source + ".asset"; AssetDatabase.DeleteAsset(path); AssetDatabase.CreateAsset(combined, path);
                var body = node.gameObject.AddComponent<Rigidbody>(); body.isKinematic = true; body.useGravity = false;
                var physical = node.gameObject.AddComponent<MeshCollider>(); physical.sharedMesh = combined;
                return new DoorLeaf { Root = node, Shape = shape, PhysicalShapes = new Collider[] { physical }, ClosedPosition = ImportedPosition(binding.closed.position), OpenPosition = ImportedPosition(binding.opened.position),
                    ClosedRotation = ImportedRotation(binding.closed.rotation), OpenRotation = ImportedRotation(binding.opened.rotation) };
            }).ToArray();
            door.Configure(leaves, open); return door;
        }
        private static Bounds LocalBounds(Transform root)
        {
            var bounds = new Bounds(); bool first = true;
            foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh = filter.sharedMesh.bounds;
                foreach (int x in new[] { -1, 1 }) foreach (int y in new[] { -1, 1 }) foreach (int z in new[] { -1, 1 })
                {
                    var p = root.InverseTransformPoint(filter.transform.TransformPoint(mesh.center + Vector3.Scale(mesh.extents, new Vector3(x, y, z))));
                    if (first) { bounds = new Bounds(p, Vector3.zero); first = false; } else bounds.Encapsulate(p);
                }
            }
            if (first || bounds.size.sqrMagnitude < 0.0001f) throw new InvalidOperationException("Door leaf has no geometry: " + root.name);
            return bounds;
        }
        private static BoxCollider Trigger(Transform parent, string name, Vector3 position, Vector3 size)
        { var root = new GameObject(name); root.transform.SetParent(parent, false); root.transform.position = position; var shape = root.AddComponent<BoxCollider>(); shape.size = size; shape.isTrigger = true; return shape; }
        private static Transform Anchor(Transform parent, string name, Vector3 position)
        { var root = new GameObject(name); root.transform.SetParent(parent, false); root.transform.position = position; return root.transform; }
        private static Transform Require(Dictionary<string, Transform> nodes, string name) => nodes.TryGetValue(name, out var node) ? node : throw new InvalidOperationException("Missing exact map binding: " + name);
        private static Vector3 V(float[] value) => value != null && value.Length == 3 ? new Vector3(value[0], value[2], value[1]) : throw new ArgumentException("Invalid exported vector.");
        // Node-local FBX transforms use reflected Blender Z; the prefab root performs the final Y-up conversion.
        private static Vector3 ImportedPosition(float[] value) => value != null && value.Length == 3 ? new Vector3(value[0], value[1], -value[2]) : throw new ArgumentException("Invalid exported vector.");
        private static Quaternion ImportedRotation(float[] value) => value != null && value.Length == 4 ? new Quaternion(-value[0], -value[1], value[2], value[3]) : throw new ArgumentException("Invalid exported quaternion.");
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
    }

    // Apply the same scoped settings on a fresh checkout before Unity splits large FBX meshes.
    public sealed class SpawnExportImporter : AssetPostprocessor
    {
        private void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(SpawnMapBuild.Folder, StringComparison.Ordinal)) return;
            string file = Path.GetFileName(assetPath);
            SpawnMapBuild.ConfigureImporter((ModelImporter)assetImporter, file == "CrewWorker.fbx" || file == "CrewWorkerAnimations.fbx",
                file.StartsWith("Collision-", StringComparison.Ordinal) || file == "Room-spawn-room.fbx");
        }
    }
}
