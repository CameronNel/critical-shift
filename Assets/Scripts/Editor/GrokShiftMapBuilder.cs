using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Prototype;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CriticalShift.Editor
{
    public static class GrokShiftMapBuilder
    {
        const string SourceScenePath = "Assets/Scenes/FacilityGreybox.unity";
        const string TargetScenePath = "Assets/Scenes/GrokShiftMap.unity";
        const string ModelPath = "Assets/Models/GrokShift/GrokShiftEnvironment.fbx";
        static readonly Vector3 GrokOffset = new Vector3(-42.05f, 0f, 24.4f);

        static readonly string[] RequiredSystems =
        {
            "[MACHINE] BRIEFING BOARD", "[MACHINE] SUIT INTEGRITY TEST", "[MACHINE] DRILL RIG",
            "mine.cart.parked", "[MACHINE] RECEIVING HOPPER", "[MACHINE] PRIMARY CRUSHER",
            "[MACHINE] SORTER", "[MACHINE] PROCESSOR", "[MACHINE] DRYER", "[MACHINE] FUEL ASSEMBLY",
            "[MACHINE] INSPECTION", "[MACHINE] FUEL RECEIVING", "[MACHINE] REACTOR CORE",
            "[MACHINE] COOLANT PUMP", "[MACHINE] COOLANT VALVES", "[MACHINE] EMERGENCY COOLING",
            "[MACHINE] CONTROL POSITION", "[MACHINE] GRID DEMAND", "[MACHINE] REANIMATION BAY"
        };

        [MenuItem("Critical Shift/Maps/Build and Open Grok Shift Map")]
        public static void BuildAndOpen()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null) throw new InvalidOperationException("Grok environment FBX is not imported: " + ModelPath);

            Scene scene = EditorSceneManager.OpenScene(SourceScenePath, OpenSceneMode.Single);
            EnsureRequiredSystems(scene);
            DisableLegacyShell(scene, "Zone_ARRIVAL", "Zone_MINE", "Zone_HAULAGE");

            var mapRoot = new GameObject("--- GROK SHIFT ARRIVAL / MINE / HAULAGE ---");
            SceneManager.MoveGameObjectToScene(mapRoot, scene);

            var environment = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            environment.name = "[GROK] Arrival Mine Haulage Environment";
            environment.transform.SetParent(mapRoot.transform, false);
            environment.transform.position = GrokOffset;
            // The FBX retains Blender Z-up coordinates. Rotate them into Unity Y-up;
            // X handedness is corrected in the Blender conversion source.
            environment.transform.rotation = Quaternion.Euler(-90f, 0f, 0f);
            environment.transform.localScale = Vector3.one;
            environment.isStatic = true;
            AddStaticCollision(environment);
            AddLighting(mapRoot.transform);

            MoveNamed(scene, "[MACHINE] BRIEFING BOARD", mapRoot.transform,
                GrokPoint(-10.95f, 1.5f, -8.2f), Quaternion.Euler(0f, 90f, 0f));
            MoveNamed(scene, "[MACHINE] SUIT INTEGRITY TEST", mapRoot.transform,
                GrokPoint(7.3f, 0f, -8.05f), Quaternion.Euler(0f, 90f, 0f));
            MoveNamed(scene, "[MACHINE] DRILL RIG", mapRoot.transform,
                GrokPoint(-55.4f, .8f, -18.7f), Quaternion.Euler(0f, 90f, 0f));
            MoveNamed(scene, "mine.cart.parked", mapRoot.transform,
                GrokPoint(-52f, .8f, -18.7f), Quaternion.Euler(0f, 90f, 0f), false);

            Transform markerRoot = FindInScene(scene, "--- SPAWN POINTS & MARKERS ---")?.transform ?? mapRoot.transform;
            CreateMarker(markerRoot, PrototypeFacilityLayout.PlayerSpawnMarker,
                GrokPoint(0f, .06f, -1.8f), Quaternion.Euler(0f, 180f, 0f));
            CreateMarker(markerRoot, PrototypeFacilityLayout.OreOutputMarker,
                GrokPoint(-54.2f, .65f, -17.2f), Quaternion.identity);
            CreateMarker(markerRoot, PrototypeFacilityLayout.MineTntMarker,
                GrokPoint(-4.6f, .7f, -15.4f), Quaternion.identity);
            CreateMarker(markerRoot, PrototypeFacilityLayout.HopperDeckMarker,
                new Vector3(-43.8f, .8f, -28.2f), Quaternion.identity);

            Transform routeRoot = FindInScene(scene, "--- ROUTES & TRACKS ---")?.transform ?? mapRoot.transform;
            CreateCartRoute(routeRoot);

            EditorSceneManager.MarkSceneDirty(scene);
            if (!EditorSceneManager.SaveScene(scene, TargetScenePath, false))
                throw new InvalidOperationException("Unity could not save " + TargetScenePath);
            AddSceneToBuildSettings();
            AssetDatabase.SaveAssets();

            Selection.activeGameObject = environment;
            if (SceneView.lastActiveSceneView != null) SceneView.lastActiveSceneView.FrameSelected();
            Debug.Log("[GrokShiftMap] Built and opened a system-complete map at " + TargetScenePath);
        }

        static Vector3 GrokPoint(float x, float y, float z)
        {
            return GrokOffset + new Vector3(x, y, z);
        }

        static void AddStaticCollision(GameObject environment)
        {
            foreach (MeshFilter filter in environment.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null || filter.GetComponent<MeshCollider>() != null) continue;
                var collider = filter.gameObject.AddComponent<MeshCollider>();
                collider.sharedMesh = filter.sharedMesh;
            }
        }

        static void AddLighting(Transform parent)
        {
            var lights = new (float x, float y, float z)[]
            {
                (0f, 3.4f, -3f), (0f, 3.4f, -8f), (-5.4f, 3.3f, -8.2f),
                (0f, 3.2f, -18f), (-5f, 3f, -18.7f), (-12f, 2.4f, -18.7f),
                (-20f, 2.2f, -18.7f), (-28f, 2.2f, -18.7f), (-36f, 2.2f, -18.7f),
                (-44f, 2.2f, -18.7f), (-52f, 2.4f, -18.7f),
                (0f, 3.6f, -28f), (0f, 5.5f, -36f), (0f, 5.5f, -44f), (0f, 5.5f, -52f)
            };

            for (int i = 0; i < lights.Length; i++)
            {
                var go = new GameObject("Grok Work Light " + (i + 1).ToString("00"));
                go.transform.SetParent(parent, false);
                go.transform.position = GrokPoint(lights[i].x, lights[i].y, lights[i].z);
                Light light = go.AddComponent<Light>();
                light.type = LightType.Point;
                light.color = new Color(.72f, .94f, .96f);
                light.intensity = 8f;
                light.range = 13f;
                light.shadows = i % 3 == 0 ? LightShadows.Soft : LightShadows.None;
            }
        }

        static void CreateCartRoute(Transform parent)
        {
            var route = new GameObject(PrototypeFacilityLayout.CartRouteMarker).transform;
            route.SetParent(parent, false);
            var points = new List<Vector3> { GrokPoint(-52f, .8f, -18.7f) };
            const float centerX = -4.75f;
            const float centerZ = -21.7f;
            const float radius = 3f;
            const int steps = 12;
            for (int i = 0; i <= steps; i++)
            {
                float angle = Mathf.PI * .5f * (i / (float)steps);
                points.Add(GrokPoint(centerX + radius * Mathf.Sin(angle), .8f,
                    centerZ + radius * Mathf.Cos(angle)));
            }
            points.Add(GrokPoint(-1.75f, .8f, -52.6f));

            for (int i = 0; i < points.Count; i++)
                CreateMarker(route, "Waypoint " + i.ToString("00"), points[i], Quaternion.identity);
        }

        static GameObject CreateMarker(Transform parent, string name, Vector3 position, Quaternion rotation)
        {
            var marker = new GameObject(name);
            marker.transform.SetParent(parent, false);
            marker.transform.SetPositionAndRotation(position, rotation);
            return marker;
        }

        static void DisableLegacyShell(Scene scene, params string[] names)
        {
            foreach (string name in names)
            {
                GameObject zone = FindInScene(scene, name);
                if (zone == null) throw new InvalidOperationException("Expected legacy zone was not found: " + name);
                zone.SetActive(false);
            }
        }

        static void EnsureRequiredSystems(Scene scene)
        {
            foreach (string system in RequiredSystems)
                if (FindInScene(scene, system) == null)
                    throw new InvalidOperationException("Required Critical Shift system is missing: " + system);
        }

        static void MoveNamed(Scene scene, string name, Transform parent, Vector3 position,
            Quaternion rotation, bool isStatic = true)
        {
            GameObject target = FindInScene(scene, name);
            if (target == null) throw new InvalidOperationException("Cannot move missing scene object: " + name);
            target.transform.SetParent(parent, true);
            target.transform.SetPositionAndRotation(position, rotation);
            target.isStatic = isStatic;
        }

        static GameObject FindInScene(Scene scene, string name)
        {
            foreach (GameObject root in scene.GetRootGameObjects())
            {
                Transform match = FindRecursive(root.transform, name);
                if (match != null) return match.gameObject;
            }
            return null;
        }

        static Transform FindRecursive(Transform current, string name)
        {
            if (current.name == name) return current;
            for (int i = 0; i < current.childCount; i++)
            {
                Transform match = FindRecursive(current.GetChild(i), name);
                if (match != null) return match;
            }
            return null;
        }

        static void AddSceneToBuildSettings()
        {
            var scenes = EditorBuildSettings.scenes.ToList();
            if (scenes.All(entry => entry.path != TargetScenePath))
                scenes.Add(new EditorBuildSettingsScene(TargetScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }
    }
}
