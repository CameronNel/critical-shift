using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CriticalShift.Editor
{
    public static class BlenderModelIntegrator
    {
        private const string ScenePath = "Assets/Scenes/FacilityGreybox.unity";
        private const string GulletMineFbx = "Assets/Models/GulletMine/GulletMine_StylizedLowPoly.fbx";
        private const string ReactorPoolFbx = "Assets/Models/ReactorPool/ReactorPool_StylizedLowPoly.fbx";
        private const string VehiclesFleetFbx = "Assets/Models/VehiclesFleet/VehiclesFleet.fbx";

        [MenuItem("Critical Shift/Integrate 3 Blender Models", priority = 20)]
        public static void IntegrateModels()
        {
            try
            {
                EditorUtility.DisplayProgressBar("Integrating Blender Models", "Opening Facility scene...", 0.1f);

                Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
                if (!scene.IsValid())
                {
                    Debug.LogError($"[BlenderModelIntegrator] Failed to open scene at {ScenePath}");
                    return;
                }

                GameObject rootFacility = GameObject.Find("--- FACILITY_ZONES ---");
                if (rootFacility == null)
                {
                    Debug.LogError("[BlenderModelIntegrator] '--- FACILITY_ZONES ---' not found in scene!");
                    return;
                }

                Transform zoneArrival = rootFacility.transform.Find("Zone_ARRIVAL");
                Transform zoneMine = rootFacility.transform.Find("Zone_MINE");
                Transform zoneReactor = rootFacility.transform.Find("Zone_REACTOR");
                Transform zoneRefinery = rootFacility.transform.Find("Zone_REFINERY");
                Transform zoneStorage = rootFacility.transform.Find("Zone_STORAGE");
                Transform zoneCompliance = rootFacility.transform.Find("Zone_COMPLIANCE");

                // 1. Integrate Gullet Mine
                EditorUtility.DisplayProgressBar("Integrating Blender Models", "Integrating Gullet Mine...", 0.3f);
                IntegrateGulletMine(zoneMine != null ? zoneMine : rootFacility.transform);

                // 2. Integrate Reactor Reference Pool
                EditorUtility.DisplayProgressBar("Integrating Blender Models", "Integrating Reactor Reference Pool...", 0.6f);
                IntegrateReactorPool(zoneReactor != null ? zoneReactor : rootFacility.transform);

                // 3. Integrate Vehicles Fleet
                EditorUtility.DisplayProgressBar("Integrating Blender Models", "Integrating Vehicles Fleet...", 0.85f);
                IntegrateVehicles(zoneArrival, zoneMine, zoneRefinery, zoneStorage, zoneReactor, zoneCompliance);

                EditorSceneManager.SaveScene(scene);
                Debug.Log("<color=#4CAF50>[BlenderModelIntegrator] Successfully component-split and integrated all 3 Blender models into the Facility scene!</color>");
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }

        private static void IntegrateGulletMine(Transform parent)
        {
            OptimizeModelImport(GulletMineFbx);
            GameObject fbxPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(GulletMineFbx);
            if (fbxPrefab == null)
            {
                Debug.LogError($"[BlenderModelIntegrator] Gullet Mine FBX not found at {GulletMineFbx}");
                return;
            }

            // Remove previous instance if re-running
            Transform existing = parent.Find("Gullet_Mine_Authored");
            if (existing != null) UnityEngine.Object.DestroyImmediate(existing.gameObject);

            GameObject root = new GameObject("Gullet_Mine_Authored");
            root.transform.SetParent(parent);
            // Position at Mine datum (-2m elevation, aligned with mine adit)
            root.transform.position = new Vector3(-83.4f, -2.0f, 0.0f);
            root.transform.rotation = Quaternion.identity;

            GameObject inst = UnityEngine.Object.Instantiate(fbxPrefab, root.transform);
            inst.name = "Gullet_Mine_Hierarchy";
            inst.transform.localPosition = Vector3.zero;
            inst.transform.localRotation = Quaternion.identity;

            // Create Component Split Containers
            GameObject catCave = new GameObject("01_Cave_And_RockMass");
            catCave.transform.SetParent(root.transform);
            catCave.transform.localPosition = Vector3.zero;

            GameObject catStructures = new GameObject("02_Timber_And_Structures");
            catStructures.transform.SetParent(root.transform);
            catStructures.transform.localPosition = Vector3.zero;

            GameObject catRails = new GameObject("03_Rail_And_Track");
            catRails.transform.SetParent(root.transform);
            catRails.transform.localPosition = Vector3.zero;

            GameObject catWater = new GameObject("04_Water_And_Drainage");
            catWater.transform.SetParent(root.transform);
            catWater.transform.localPosition = Vector3.zero;

            GameObject catProps = new GameObject("05_Equipment_And_Props");
            catProps.transform.SetParent(root.transform);
            catProps.transform.localPosition = Vector3.zero;

            // Classify and re-parent children
            List<Transform> children = new List<Transform>();
            for (int i = 0; i < inst.transform.childCount; i++)
            {
                children.Add(inst.transform.GetChild(i));
            }

            foreach (var child in children)
            {
                string n = child.name.ToLower();
                if (n.Contains("cave") || n.Contains("rock") || n.Contains("earth") || n.Contains("chalk") || n.Contains("copper") || n.Contains("iron") || n.Contains("gold") || n.Contains("glimmer"))
                {
                    child.SetParent(catCave.transform, true);
                    AddMeshCollider(child.gameObject);
                }
                else if (n.Contains("timber") || n.Contains("lift") || n.Contains("shaft") || n.Contains("floor") || n.Contains("safety") || n.Contains("breaker"))
                {
                    child.SetParent(catStructures.transform, true);
                    AddMeshCollider(child.gameObject);
                }
                else if (n.Contains("rail") || n.Contains("sleeper") || n.Contains("ballast") || n.Contains("track"))
                {
                    child.SetParent(catRails.transform, true);
                }
                else if (n.Contains("water") || n.Contains("pit") || n.Contains("pump") || n.Contains("ravine") || n.Contains("trestle"))
                {
                    child.SetParent(catWater.transform, true);
                }
                else
                {
                    child.SetParent(catProps.transform, true);
                }
            }

            // Remove empty inst root wrapper if desired or keep
            if (inst.transform.childCount == 0) UnityEngine.Object.DestroyImmediate(inst);

            // Assign shared greybox materials so untextured meshes respond to lighting
            ApplyCategoryMaterial(catCave, "Mat_Rock_Cavern");
            ApplyCategoryMaterial(catStructures, "Mat_Floor_Grade");
            ApplyCategoryMaterial(catRails, "Mat_Cart_Track");
            ApplyCategoryMaterial(catWater, "Mat_Coolant_Liquid");
            ApplyCategoryMaterial(catProps, "Mat_Metal_Machine");
            StripImportedRuntimeComponents(root);
        }

        private static void IntegrateReactorPool(Transform parent)
        {
            OptimizeModelImport(ReactorPoolFbx);
            GameObject fbxPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ReactorPoolFbx);
            if (fbxPrefab == null)
            {
                Debug.LogError($"[BlenderModelIntegrator] Reactor Pool FBX not found at {ReactorPoolFbx}");
                return;
            }

            Transform existing = parent.Find("Reactor_Waste_Storage_Pool");
            if (existing != null) UnityEngine.Object.DestroyImmediate(existing.gameObject);

            GameObject root = new GameObject("Reactor_Waste_Storage_Pool");
            root.transform.SetParent(parent);
            // Placed at Reactor east wing / waste storage interface (aligned at Y=0m, pool pit drops to -5m)
            root.transform.position = new Vector3(18.0f, 0.0f, -8.0f);
            root.transform.rotation = Quaternion.identity;

            GameObject inst = UnityEngine.Object.Instantiate(fbxPrefab, root.transform);
            inst.name = "Reactor_Pool_Hierarchy";
            inst.transform.localPosition = Vector3.zero;
            inst.transform.localRotation = Quaternion.identity;

            // Create Component Split Containers
            GameObject catPit = new GameObject("01_Pool_And_Pit_Structure");
            catPit.transform.SetParent(root.transform);
            catPit.transform.localPosition = Vector3.zero;

            GameObject catHoist = new GameObject("02_Monorail_And_Hoist");
            catHoist.transform.SetParent(root.transform);
            catHoist.transform.localPosition = Vector3.zero;

            GameObject catCasks = new GameObject("03_Radioactive_Casks");
            catCasks.transform.SetParent(root.transform);
            catCasks.transform.localPosition = Vector3.zero;

            GameObject catDrums = new GameObject("04_Waste_Drums");
            catDrums.transform.SetParent(root.transform);
            catDrums.transform.localPosition = Vector3.zero;

            GameObject catGrates = new GameObject("05_Grates_And_Markings");
            catGrates.transform.SetParent(root.transform);
            catGrates.transform.localPosition = Vector3.zero;

            List<Transform> children = new List<Transform>();
            for (int i = 0; i < inst.transform.childCount; i++) children.Add(inst.transform.GetChild(i));

            foreach (var child in children)
            {
                string n = child.name.ToLower();
                if (n.Contains("pit") || n.Contains("floor") || n.Contains("wall") || n.Contains("ceil") || n.Contains("curb"))
                {
                    child.SetParent(catPit.transform, true);
                    AddMeshCollider(child.gameObject);
                }
                else if (n.Contains("monorail") || n.Contains("hoist") || n.Contains("monohang"))
                {
                    child.SetParent(catHoist.transform, true);
                }
                else if (n.Contains("cask"))
                {
                    child.SetParent(catCasks.transform, true);
                    AddMeshCollider(child.gameObject);
                }
                else if (n.Contains("drum"))
                {
                    child.SetParent(catDrums.transform, true);
                    AddMeshCollider(child.gameObject);
                }
                else if (n.Contains("grate") || n.Contains("haz") || n.Contains("sign"))
                {
                    child.SetParent(catGrates.transform, true);
                }
                else
                {
                    child.SetParent(catPit.transform, true);
                }
            }

            if (inst.transform.childCount == 0) UnityEngine.Object.DestroyImmediate(inst);

            ApplyCategoryMaterial(catPit, "Mat_Wall_Industrial");
            ApplyCategoryMaterial(catHoist, "Mat_Metal_Machine");
            ApplyCategoryMaterial(catCasks, "Mat_Hazard_Stripe");
            ApplyCategoryMaterial(catDrums, "Mat_Metal_Machine");
            ApplyCategoryMaterial(catGrates, "Mat_Metal_Catwalk");
            StripImportedRuntimeComponents(root);
        }

        private static void IntegrateVehicles(Transform zArrival, Transform zMine, Transform zRefinery, Transform zStorage, Transform zReactor, Transform zCompliance)
        {
            OptimizeModelImport(VehiclesFleetFbx);
            GameObject fbxPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(VehiclesFleetFbx);
            if (fbxPrefab == null)
            {
                Debug.LogError($"[BlenderModelIntegrator] Vehicles Fleet FBX not found at {VehiclesFleetFbx}");
                return;
            }

            GameObject tempInst = UnityEngine.Object.Instantiate(fbxPrefab);
            tempInst.name = "Temp_Vehicles";

            var vehicleDefinitions = new List<(string search, Transform parent, Vector3 pos, float rotY)>
            {
                ("Vehicle_ShuttleBus", zArrival, new Vector3(-67.2f, 0.0f, -48.0f), 90f),
                ("Vehicle_Loader_Mine", zMine, new Vector3(-79.8f, -2.0f, 0.0f), 180f),
                ("Vehicle_Pickup_Mine", zMine, new Vector3(-72.0f, 0.0f, -8.0f), 45f),
                ("Vehicle_Forklift_Refinery", zRefinery, new Vector3(0.0f, 0.0f, -32.0f), 0f),
                ("Vehicle_Forklift_Storage", zStorage, new Vector3(-40.0f, 0.0f, 16.0f), -90f),
                ("Vehicle_Pickup_Reactor", zReactor, new Vector3(18.0f, 0.0f, -22.0f), 135f),
                ("Vehicle_Pickup_Substation", zCompliance, new Vector3(12.0f, 0.0f, -50.0f), -45f)
            };

            foreach (var (search, targetParent, pos, rotY) in vehicleDefinitions)
            {
                if (targetParent == null) continue;

                // Remove existing
                Transform existing = targetParent.Find(search);
                if (existing != null) UnityEngine.Object.DestroyImmediate(existing.gameObject);

                GameObject vehRoot = new GameObject(search);
                vehRoot.transform.SetParent(targetParent);
                vehRoot.transform.position = pos;
                vehRoot.transform.rotation = Quaternion.Euler(0f, rotY, 0f);

                // Find all parts belonging to this vehicle in tempInst
                List<Transform> parts = new List<Transform>();
                for (int i = 0; i < tempInst.transform.childCount; i++)
                {
                    Transform c = tempInst.transform.GetChild(i);
                    if (c.name.StartsWith(search))
                    {
                        parts.Add(c);
                    }
                }

                foreach (var p in parts)
                {
                    p.SetParent(vehRoot.transform, false);
                }

                // Add Box Collider for vehicle hull
                BoxCollider col = vehRoot.AddComponent<BoxCollider>();
                col.center = new Vector3(0f, 1.2f, 0f);
                col.size = new Vector3(2.4f, 2.4f, 4.8f);
                StripImportedRuntimeComponents(vehRoot);
            }

            UnityEngine.Object.DestroyImmediate(tempInst);
        }

        private static void ApplyCategoryMaterial(GameObject categoryRoot, string materialName)
        {
            if (categoryRoot == null) return;
            Material mat = AssetDatabase.LoadAssetAtPath<Material>($"Assets/Materials/Greybox/{materialName}.mat");
            if (mat == null)
            {
                Debug.LogWarning($"[BlenderModelIntegrator] Material {materialName} not found for category {categoryRoot.name}");
                return;
            }

            foreach (var renderer in categoryRoot.GetComponentsInChildren<MeshRenderer>())
            {
                var mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++) mats[i] = mat;
                renderer.sharedMaterials = mats;
            }
        }

        private static void AddMeshCollider(GameObject go)
        {
            MeshFilter mf = go.GetComponent<MeshFilter>();
            if (mf != null && mf.sharedMesh != null && go.GetComponent<Collider>() == null)
            {
                MeshCollider mc = go.AddComponent<MeshCollider>();
                mc.sharedMesh = mf.sharedMesh;
            }
        }

        private static void StripImportedRuntimeComponents(GameObject root)
        {
            // Authored FBXs may contain presentation cameras, listeners, and Blender
            // area lights. The Unity facility supplies its own deliberately cheap
            // lighting; retaining imported components both overexposes the map and
            // increases the per-frame light/camera cost.
            foreach (Light light in root.GetComponentsInChildren<Light>(true))
                UnityEngine.Object.DestroyImmediate(light);
            foreach (Camera camera in root.GetComponentsInChildren<Camera>(true))
                UnityEngine.Object.DestroyImmediate(camera);
            foreach (AudioListener listener in root.GetComponentsInChildren<AudioListener>(true))
                UnityEngine.Object.DestroyImmediate(listener);
        }

        private static void OptimizeModelImport(string assetPath)
        {
            var importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer == null) return;

            // The source scenes are authored as low-poly modular kits. These importer
            // settings preserve their broad silhouettes while reducing CPU/GPU memory
            // pressure for the playable prototype. No runtime mesh decimation/package
            // is needed, and the original Blender files remain untouched.
            bool changed = false;
            if (importer.meshCompression != ModelImporterMeshCompression.Medium)
            {
                importer.meshCompression = ModelImporterMeshCompression.Medium;
                changed = true;
            }
            if (!importer.optimizeMeshPolygons) { importer.optimizeMeshPolygons = true; changed = true; }
            if (!importer.optimizeMeshVertices) { importer.optimizeMeshVertices = true; changed = true; }
            if (importer.isReadable) { importer.isReadable = false; changed = true; }
            if (changed) AssetDatabase.WriteImportSettingsIfDirty(assetPath);
        }
    }
}
