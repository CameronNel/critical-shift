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
    [Serializable] public sealed class ExportObject { public string source, node; public bool visible, dynamic; }
    [Serializable] public sealed class ExportLight { public float[] position, color; public float power; public string type; }
    [Serializable] public sealed class ExportAnchor { public string name, node; public float[] position; }
    [Serializable] public sealed class ExportRoom
    {
        public string key, mesh, collision, meshSha256, collisionSha256;
        public float[] translation; public float yaw; public ExportObject[] objects; public ExportLight[] lights;
    }
    [Serializable] public sealed class ExportMap { public int schema; public string mapCommit; public ExportRoom[] rooms; public ExportAnchor[] anchors; public ExportDoor[] doors; }
    [Serializable] public sealed class ExportClip { public string name; public float first, last; public bool loop, derivative; }
    [Serializable] public sealed class ExportWorkerMesh { public string name, region; public bool suit, head; }
    [Serializable] public sealed class ExportRig { public string rig_commit, fbx_sha256; public int fps; public float seatedSupportHeight; public ExportClip[] clips; public ExportWorkerMesh[] meshes; }

    // Generates an isolated runtime scene from exact source/export bindings. Never saves a Blender authoring file.
    public static class SpawnMapBuild
    {
        private const string Folder = "Assets/CriticalShift/Generated/Spawn/";
        public const string ScenePath = "Assets/CriticalShift/Generated/Spawn/AssembledMap.unity";
        [MenuItem("Critical Shift/Spawn/Create assembled map scene")]
        public static void Create()
        {
            if (UnityEngine.Application.unityVersion != "6000.4.3f1") throw new InvalidOperationException("Use the pinned 6000.4.3f1 editor.");
            var map = JsonUtility.FromJson<ExportMap>(File.ReadAllText(Folder + "map-bindings.json"));
            var rig = JsonUtility.FromJson<ExportRig>(File.ReadAllText(Folder + "rig-bindings.json"));
            if (map.schema != 1 || map.rooms == null || map.rooms.Length != 6 || rig.fps != 24 || rig.clips.Length != 52)
                throw new InvalidOperationException("Unexpected current-map/rig inventory. Regenerate and review the interface.");
            foreach (var room in map.rooms)
            { CheckHash(room.mesh, room.meshSha256); CheckHash(room.collision, room.collisionSha256); }
            CheckHash("CrewWorker.fbx", rig.fbx_sha256);
            AssetDatabase.Refresh();
            foreach (var room in map.rooms) { Import(room.mesh, false, readable: room.key == "spawn-room"); Import(room.collision, false, readable: true); }
            Import("CrewWorker.fbx", true, clips: rig.clips);
            var controller = Controller(rig);
            if (!UnityEngine.Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Critical Shift — assembled map " + map.mapCommit.Substring(0, 8));
            var host = root.AddComponent<LocalShiftHost>();
            var nodes = new Dictionary<string, Transform>();
            Transform spawnRoot = null;
            foreach (var room in map.rooms)
            {
                var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Folder + room.mesh));
                model.name = "ROOM_" + room.key; model.transform.SetParent(root.transform, false);
                model.transform.localPosition = V(room.translation); model.transform.localRotation = Quaternion.Euler(0, -room.yaw, 0);
                foreach (var node in model.GetComponentsInChildren<Transform>(true))
                    if (node.name.StartsWith("CS_", StringComparison.Ordinal)) nodes.Add(node.name, node);
                foreach (var binding in room.objects)
                {
                    if (!nodes.TryGetValue(binding.node, out var node)) throw new InvalidOperationException("Missing exported node: " + binding.node);
                    var renderer = node.GetComponent<Renderer>(); if (renderer != null) renderer.enabled = binding.visible;
                }
                var collisionModel = AssetDatabase.LoadAssetAtPath<GameObject>(Folder + room.collision);
                var filter = collisionModel.GetComponentInChildren<MeshFilter>(true);
                if (filter == null || filter.sharedMesh == null) throw new InvalidOperationException("Missing room collision mesh.");
                var collision = new GameObject("Static collision — " + room.key); collision.transform.SetParent(model.transform, false);
                collision.AddComponent<MeshCollider>().sharedMesh = filter.sharedMesh;
                foreach (var sourceLight in room.lights)
                {
                    var lamp = new GameObject("Runtime light preview"); lamp.transform.SetParent(model.transform, false);
                    lamp.transform.localPosition = V(sourceLight.position);
                    var light = lamp.AddComponent<Light>(); light.type = LightType.Point; light.range = 7;
                    light.color = new Color(sourceLight.color[0], sourceLight.color[1], sourceLight.color[2]);
                    light.intensity = Mathf.Clamp(sourceLight.power / 150, 0.25f, 3); light.shadows = LightShadows.None;
                }
                if (room.key == "spawn-room") spawnRoot = model.transform;
            }
            if (spawnRoot == null) throw new InvalidOperationException("Missing assembled spawn room.");
            foreach (var anchor in map.anchors)
            {
                var node = Require(nodes, anchor.node);
                if (Vector3.Distance(spawnRoot.InverseTransformPoint(node.position), V(anchor.position)) > 0.02f)
                    throw new InvalidOperationException("Imported scale/axes changed a spawn binding: " + anchor.name);
            }
            var actor = Worker(root.transform, Require(nodes, "CS_spawn-room_SPAWN_1"), host, rig, controller);
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
                station.ConfigureStation(Require(nodes, "CS_spawn-room_PPE_" + code + "_suit"));
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
                    var centre = bench.position + bench.forward * (seat == 0 ? -0.27f : 0.27f); centre.y = surface + 0.03f;
                    var shape = Trigger(root.transform, $"Bench {i} seat {seat + 1}", centre, new Vector3(0.42f, 0.12f, 0.43f));
                    var pose = Anchor(root.transform, "Seated body pose", centre); pose.rotation = Quaternion.LookRotation(-bench.right);
                    var exit = Anchor(root.transform, "Seat exit", centre - bench.right * 0.95f); exit.position = new Vector3(exit.position.x, bench.position.y + 0.05f, exit.position.z);
                    var target = shape.gameObject.AddComponent<InteractionTarget>(); target.Configure(Id(30 + i * 2 + seat), PlayerTargetKind.Seat, "sit on bench", shape, anchor: pose, exitPose: exit);
                    targets.Add(target);
                }
            }
            foreach (int i in new[] { 1, 3 })
            {
                var prop = Require(nodes, "CS_spawn-room_BELONG_" + i.ToString("00") + "_thermos");
                var local = LocalBounds(prop); var centre = prop.TransformPoint(local.center);
                var item = new GameObject("Carryable thermos " + i); item.transform.SetParent(root.transform, false); item.transform.position = centre;
                var shape = item.AddComponent<BoxCollider>(); shape.size = Vector3.Scale(local.size, prop.lossyScale);
                prop.SetParent(item.transform, true);
                var body = item.AddComponent<Rigidbody>(); body.mass = 0.5f; body.interpolation = RigidbodyInterpolation.Interpolate;
                var target = item.AddComponent<InteractionTarget>(); target.Configure(Id(100 + i), PlayerTargetKind.Carryable, "pick up thermos", shape, body);
                targets.Add(target);
            }
            var top = Require(nodes, "CS_spawn-room_BRIEFING_sideboard_laminate_top").GetComponent<Renderer>().bounds;
            var placementShape = Trigger(root.transform, "Sideboard placement", new Vector3(top.center.x, top.max.y + 0.06f, top.center.z), new Vector3(0.4f, 0.1f, 0.6f));
            var placement = placementShape.gameObject.AddComponent<InteractionTarget>();
            placement.Configure(Id(41), PlayerTargetKind.Placement, "place/take thermos", placementShape,
                anchor: Anchor(root.transform, "Sideboard item pose", new Vector3(top.center.x, top.max.y + 0.18f, top.center.z)), slot: Id(61));
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
            var sky = new GameObject("Runtime dusk light"); sky.transform.SetParent(root.transform, false); sky.transform.rotation = Quaternion.Euler(52, 38, 0);
            var sun = sky.AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 0.7f; sun.color = new Color(0.62f, 0.72f, 1);
            RenderSettings.ambientLight = new Color(0.22f, 0.24f, 0.3f);
            Physics.SyncTransforms();
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new IOException("Could not save the isolated runtime scene.");
            Debug.Log("Generated current assembled map with spawn runtime bindings: " + map.mapCommit + ". Native tests and Player validation still required.");
        }
        public static void Build()
        {
            Create();
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-csBuildPath");
            if (index < 0 || index + 1 >= args.Length) throw new BuildFailedException("-csBuildPath must name the executable.");
            var path = Path.GetFullPath(args[index + 1]); Directory.CreateDirectory(Path.GetDirectoryName(path));
            var target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneLinux64 && target != BuildTarget.StandaloneWindows64)
                throw new BuildFailedException("Only Linux64/Windows64 are in this local map scope.");
            var named = NamedBuildTarget.Standalone;
            PlayerSettings.SetApiCompatibilityLevel(named, ApiCompatibilityLevel.NET_Standard);
            PlayerSettings.SetScriptingBackend(named, ScriptingImplementation.Mono2x);
            PlayerSettings.SetManagedStrippingLevel(named, ManagedStrippingLevel.Disabled);
            if (UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline != null)
                throw new BuildFailedException("The prepared map requires Built-in rendering.");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { ScenePath }, target = target,
                locationPathName = path, options = BuildOptions.Development | BuildOptions.StrictMode });
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new BuildFailedException("Assembled map build failed.");
            Debug.Log("CS_SPAWN_MAP_BUILD_OK");
        }
        private static void CheckHash(string file, string expected)
        {
            using var hash = SHA256.Create(); using var stream = File.OpenRead(Folder + file);
            string actual = BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
            if (actual != expected) throw new InvalidOperationException("Export hash mismatch: " + file);
        }
        private static void Import(string file, bool animated, bool readable = false, ExportClip[] clips = null)
        {
            var importer = AssetImporter.GetAtPath(Folder + file) as ModelImporter;
            if (importer == null) throw new InvalidOperationException("Expected the built-in FBX importer: " + file);
            importer.globalScale = 1; importer.useFileScale = true; importer.bakeAxisConversion = true;
            importer.importAnimation = animated; importer.importLights = false; importer.importCameras = false;
            importer.isReadable = readable; importer.optimizeGameObjects = false;
            if (animated)
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
            importer.SaveAndReimport();
        }
        private static AnimatorController Controller(ExportRig rig)
        {
            string path = Folder + "CrewWorker.controller"; AssetDatabase.DeleteAsset(path);
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path); var machine = controller.layers[0].stateMachine;
            var clips = AssetDatabase.LoadAllAssetsAtPath(Folder + "CrewWorker.fbx").OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToArray();
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
            root.transform.SetPositionAndRotation(spawn.position + Vector3.up * 0.06f, spawn.rotation);
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
                var physical = node.gameObject.AddComponent<MeshCollider>(); physical.sharedMesh = combined;
                var body = node.gameObject.AddComponent<Rigidbody>(); body.isKinematic = true; body.useGravity = false;
                return new DoorLeaf { Root = node, Shape = shape, PhysicalShapes = new Collider[] { physical }, ClosedPosition = V(binding.closed.position), OpenPosition = V(binding.opened.position),
                    ClosedRotation = Q(binding.closed.rotation), OpenRotation = Q(binding.opened.rotation) };
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
        private static Quaternion Q(float[] value) => value != null && value.Length == 4 ? new Quaternion(-value[0], -value[2], -value[1], value[3]) : throw new ArgumentException("Invalid exported quaternion.");
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
    }
}
