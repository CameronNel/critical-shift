using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Sandbox.Editor
{
    /// <summary>Imports only the combined map's collision/anchor derivative, outside the baked-art importer.</summary>
    public static class CombinedMapSceneBuilder
    {
        public const string ScenePath = "Assets/CriticalShift/Sandbox/Generated/CombinedMapTraversal.unity";
        private const string SourceFolder = "Assets/CriticalShift/Sandbox/Generated/CombinedMapSource";
        [Serializable] private sealed class EditorProfile { public string editor = ""; }

        [MenuItem("Critical Shift/Combined Map/Create collision traversal scene")]
        public static void PrepareMenu()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            Prepare(Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "../../../sections/facility-assembly/combined")));
        }
        public static void PrepareBatch()
        {
            var args = Environment.GetCommandLineArgs(); int at = Array.IndexOf(args, "-csCombinedMapSourceRoot");
            if (at < 0 || at + 1 >= args.Length) throw new BuildFailedException("Pass -csCombinedMapSourceRoot with the scoped combined-map input copy.");
            Prepare(Path.GetFullPath(args[at + 1]));
        }
        private static void Prepare(string source)
        {
            var profile = JsonUtility.FromJson<EditorProfile>(File.ReadAllText(Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "../../toolchain.json"))));
            if (profile == null || profile.editor != UnityApplication.unityVersion)
                throw new BuildFailedException("Use the exact project Unity editor for combined-map preparation.");
            SandboxRenderPipeline.Prepare();
            var manifest = Read<CombinedBindingManifest>(source, "export/binding_manifest.json");
            var doors = Read<CombinedDoorCatalogue>(source, "validation/doors.json");
            // Unity's serializer cannot read jagged arrays. Adapt only the two
            // numeric AABB arrays in memory; the original file remains unchanged.
            string colliderText = File.ReadAllText(Path.Combine(source, "validation/colliders.json"));
            var boundArrays = new Regex("\"bounds\"\\s*:\\s*\\[\\s*(\\[[0-9eE+.,\\s-]+\\])\\s*,\\s*(\\[[0-9eE+.,\\s-]+\\])\\s*\\]");
            int boundCount = boundArrays.Matches(colliderText).Count;
            var proxies = JsonUtility.FromJson<CombinedColliderCatalogue>(boundArrays.Replace(colliderText, "\"minimum\":$1,\"maximum\":$2"));
            if (manifest?.export == null || manifest.room_placements == null || manifest.room_placements.Length == 0 ||
                doors?.doors == null || doors.doors.Length == 0 || doors.doors.Length > 128 || proxies?.colliders == null || proxies.colliders.Length == 0)
                throw new BuildFailedException("Combined-map input has missing definitions.");
            if (boundCount != proxies.colliders.Length) throw new BuildFailedException("Every collision proxy needs its two numeric bounds arrays.");
            string fbx = Path.Combine(source, "export/compact_map_colliders_anchors.fbx");
            string hash;
            using (var digest = SHA256.Create()) hash = BitConverter.ToString(digest.ComputeHash(File.ReadAllBytes(fbx))).Replace("-", "").ToLowerInvariant();
            if (manifest.export.file != Path.GetFileName(fbx) || manifest.export.sha256 != hash)
                throw new BuildFailedException("The combined collision FBX differs from its binding manifest.");
            Folder(SourceFolder);
            string asset = SourceFolder + "/compact_map_colliders_anchors.fbx";
            File.Copy(fbx, Physical(asset), true);
            AssetDatabase.ImportAsset(asset, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            var importer = AssetImporter.GetAtPath(asset) as ModelImporter;
            if (importer == null) throw new BuildFailedException("Unity did not recognize the combined-map FBX.");
            importer.globalScale = 1; importer.useFileScale = true; importer.bakeAxisConversion = true; importer.importAnimation = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None; importer.addCollider = false;
            importer.isReadable = true; importer.meshCompression = ModelImporterMeshCompression.Off; importer.SaveAndReimport();
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(asset);
            if (prefab == null) throw new BuildFailedException("The combined collision FBX produced no model prefab.");
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            if (shader == null) throw new BuildFailedException("The configured renderer's debug shader is unavailable.");
            SandboxMaterialTemplates.Prepare(shader, out var litTemplate, out var emissionTemplate);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Combined map traversal derivative");
            var bootstrap = root.AddComponent<CombinedMapBootstrap>();
            // Unpack only this generated derivative so explicit door roots can group imported siblings.
            var model = (GameObject)PrefabUtility.InstantiatePrefab(prefab, root.transform);
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            var authoring = model.AddComponent<CombinedMapAuthoring>();
            var named = new Dictionary<string, Transform>(StringComparer.Ordinal);
            foreach (var item in model.GetComponentsInChildren<Transform>(true))
                if (!named.TryAdd(item.name, item)) throw new BuildFailedException("Ambiguous imported node name: " + item.name);
            foreach (var placement in manifest.room_placements)
            {
                if (placement.room != "spawn-room" && placement.room != "reactor-room" && placement.room != "condenser-bay") continue;
                Vector3 actual = Node(named, "ANCHOR_ROOM_" + placement.room).position;
                Vector3 expected = Point(placement.translation);
                Debug.Log("CS_COMBINED_MAP_FRAME stage=raw room=" + placement.room + " actual=" + Coordinates(actual) + " expected=" + Coordinates(expected));
            }
            // Native 6000.4.3f1 measurements of three separated room anchors,
            // including the lower condenser, put this scoped FBX in (x,z,y).
            // Normalize its generated root into the baked importer's (-x,z,-y)
            // frame. The source FBX and protected baked importer stay unchanged;
            // every proxy bound and room/door anchor is still checked below.
            Quaternion collisionToBakedFrame = Quaternion.Euler(0, 180, 0);
            model.transform.localPosition = collisionToBakedFrame * model.transform.localPosition;
            model.transform.localRotation = collisionToBakedFrame * model.transform.localRotation;
            var contacts = new Dictionary<string, Collider>(StringComparer.Ordinal);
            var rows = new Dictionary<string, CombinedColliderRow>(StringComparer.Ordinal);
            var materials = new Dictionary<string, Material>(StringComparer.Ordinal);
            foreach (var row in proxies.colliders)
            {
                if (row == null || string.IsNullOrEmpty(row.name) || !rows.TryAdd(row.name, row) || !named.TryGetValue(row.name, out var node))
                    throw new BuildFailedException("Missing or duplicate imported collision proxy.");
                bool trigger = row.role == "door_threshold" || row.role == "ladder";
                if (row.trigger != trigger || !new[] { "floor", "wall", "roof", "ramp", "door_blocker", "door_threshold", "ladder" }.Contains(row.role))
                    throw new BuildFailedException("Unknown or contradictory collision role: " + row.name);
                var mesh = node.GetComponent<MeshFilter>();
                if (mesh == null || mesh.sharedMesh == null || mesh.sharedMesh.vertexCount == 0 || node.GetComponent<Collider>() != null)
                    throw new BuildFailedException("A collision proxy has no usable mesh or already has a collider: " + row.name);
                var contact = node.gameObject.AddComponent<MeshCollider>(); contact.sharedMesh = mesh.sharedMesh;
                contact.convex = trigger; contact.isTrigger = trigger; contacts.Add(row.name, contact);
                var renderer = node.GetComponent<Renderer>();
                if (renderer != null)
                {
                    if (!materials.TryGetValue(row.role, out var material))
                    {
                        string path = SourceFolder + "/debug_" + row.role + ".mat";
                        material = AssetDatabase.LoadAssetAtPath<Material>(path);
                        if (material == null) { material = new Material(shader); AssetDatabase.CreateAsset(material, path); }
                        material.color = row.role == "door_blocker" ? new Color(0.8f, 0.43f, 0.12f) :
                            row.role == "floor" || row.role == "ramp" ? new Color(0.22f, 0.28f, 0.3f) : new Color(0.42f, 0.47f, 0.5f);
                        materials.Add(row.role, material);
                    }
                    renderer.sharedMaterial = material; renderer.enabled = !trigger;
                }
            }
            float maximumError = 0;
            var references = new List<CombinedMapDoorReference>(); var doorIds = new HashSet<string>(StringComparer.Ordinal);
            Physics.SyncTransforms();
            foreach (var row in proxies.colliders)
            {
                if (row.minimum == null || row.minimum.Length != 3 || row.maximum == null || row.maximum.Length != 3 ||
                    Enumerable.Range(0, 3).Any(axis => row.minimum[axis] >= row.maximum[axis]))
                    throw new BuildFailedException("A collision proxy has invalid validation bounds: " + row.name);
                var expected = new Bounds(Point(row.minimum), Vector3.zero); expected.Encapsulate(Point(row.maximum));
                var actual = contacts[row.name].bounds;
                maximumError = Mathf.Max(maximumError, Error(actual.min, expected.min), Error(actual.max, expected.max));
            }
            foreach (var row in doors.doors)
            {
                if (row == null || string.IsNullOrWhiteSpace(row.id) || !doorIds.Add(row.id) || row.plan == null || row.plan.Length != 3 ||
                    row.outward == null || row.outward.Length != 2 || !Finite(row.clear_w) || row.clear_w <= 0 || !Finite(row.clear_h) || row.clear_h <= 0 ||
                    !ValidState(row.state) || !ValidState(row.evac_state)) throw new BuildFailedException("Invalid door definition.");
                var anchor = Node(named, "DOOR_" + row.id);
                maximumError = Mathf.Max(maximumError, Error(anchor.position, Point(row.plan)));
                var blocker = Contact(proxies.colliders, contacts, row.id, "door_blocker");
                var threshold = Contact(proxies.colliders, contacts, row.id, "door_threshold");
                Vector3 outward = new Vector3(-row.outward[0], 0, -row.outward[1]);
                if (!Finite(outward.x) || !Finite(outward.z) || Mathf.Abs(outward.magnitude - 1) > 0.001f)
                    throw new BuildFailedException("A door outward vector is invalid: " + row.id);
                Vector3 centre = anchor.position + Vector3.up * (row.clear_h * 0.5f);
                if (!blocker.Raycast(new Ray(centre + outward * 0.4f, -outward), out _, 0.8f))
                    throw new BuildFailedException("The imported blocker does not cross its authored door plane: " + row.id);
                var doorRoot = new GameObject("Door binding " + row.id).transform; doorRoot.SetParent(model.transform, false);
                doorRoot.position = anchor.position;
                anchor.SetParent(doorRoot, true); blocker.transform.SetParent(doorRoot, true); threshold.transform.SetParent(doorRoot, true);
                var control = new GameObject("Door interaction point").transform; control.SetParent(doorRoot, false);
                control.localPosition = Vector3.up * Mathf.Min(1.2f, row.clear_h * 0.5f);
                references.Add(new CombinedMapDoorReference { definition = row, anchor = anchor, interactionPoint = control, blocker = blocker, threshold = threshold });
            }
            foreach (var placement in manifest.room_placements)
            {
                if (placement == null || string.IsNullOrEmpty(placement.room) || placement.translation == null || placement.translation.Length != 3)
                    throw new BuildFailedException("Invalid room anchor placement.");
                maximumError = Mathf.Max(maximumError, Error(Node(named, "ANCHOR_ROOM_" + placement.room).position, Point(placement.translation)));
            }
            if (maximumError > 0.01f) throw new BuildFailedException("Imported map anchor error exceeds one centimetre: " + maximumError);
            if (!contacts.TryGetValue("COL spine floor", out var floor)) throw new BuildFailedException("The known spine start floor is absent.");
            Vector3 start = floor.bounds.center; start.y = floor.bounds.max.y + 0.08f;
            var worldRegion = floor.bounds;
            foreach (var contact in contacts.Values) worldRegion.Encapsulate(contact.bounds);
            worldRegion.Expand(6f);
            var localRegion = new Bounds(model.transform.InverseTransformPoint(worldRegion.center), Vector3.zero);
            for (int corner = 0; corner < 8; corner++)
                localRegion.Encapsulate(model.transform.InverseTransformPoint(worldRegion.center + Vector3.Scale(worldRegion.extents,
                    new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1))));
            authoring.Configure(references.ToArray(), model.transform.InverseTransformPoint(start), localRegion, hash);
            model.SetActive(false); bootstrap.Configure(authoring, shader, litTemplate, emissionTemplate);
            var daylight = new GameObject("Collision traversal debug daylight").AddComponent<Light>();
            daylight.transform.SetParent(root.transform, false); daylight.type = LightType.Directional; daylight.intensity = 1;
            daylight.transform.rotation = Quaternion.Euler(55, -35, 0);
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new BuildFailedException("Could not save the combined-map traversal derivative.");
            AssetDatabase.SaveAssets();
            Debug.Log("CS_COMBINED_MAP_PREPARED doors=" + references.Count + " colliders=" + contacts.Count +
                " room_anchors=" + manifest.room_placements.Length + " source_sha256=" + hash +
                " max_anchor_error_metres=" + maximumError.ToString("R", CultureInfo.InvariantCulture) + " scene=" + ScenePath);
        }
        private static Collider Contact(CombinedColliderRow[] rows, Dictionary<string, Collider> contacts, string door, string role)
        {
            var matching = rows.Where(row => row.door_id == door && row.role == role).ToArray();
            if (matching.Length != 1) throw new BuildFailedException("A door needs exactly one " + role + ": " + door);
            return contacts[matching[0].name];
        }
        private static Transform Node(Dictionary<string, Transform> named, string name) =>
            named.TryGetValue(name, out var node) ? node : throw new BuildFailedException("Missing imported anchor: " + name);
        private static T Read<T>(string source, string file) => JsonUtility.FromJson<T>(File.ReadAllText(Path.Combine(source, file)));
        private static string Physical(string asset) => Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "..", asset));
        private static void Folder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = path.Substring(0, path.LastIndexOf('/')); Folder(parent);
            AssetDatabase.CreateFolder(parent, path.Substring(path.LastIndexOf('/') + 1));
        }
        // Matches the existing baked importer, whose protected files remain untouched.
        private static Vector3 Point(float[] plan)
        {
            if (plan.Any(value => !Finite(value))) throw new BuildFailedException("An authored position is non-finite.");
            return new Vector3(-plan[0], plan[2], -plan[1]);
        }
        private static float Error(Vector3 actual, Vector3 expected)
        {
            float error = Vector3.Distance(actual, expected);
            if (!Finite(error)) throw new BuildFailedException("Imported anchor position is non-finite.");
            return error;
        }
        private static string Coordinates(Vector3 point) => string.Join(",", new[] { point.x, point.y, point.z }.Select(value => value.ToString("R", CultureInfo.InvariantCulture)));
        private static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);
        private static bool ValidState(string value) => value == "open" || value == "closed" || value == "locked";
    }
}
