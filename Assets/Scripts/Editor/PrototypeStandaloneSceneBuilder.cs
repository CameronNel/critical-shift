#if UNITY_EDITOR
using System;
using System.IO;
using CriticalShift.Prototype;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Editor
{
    public static class PrototypeStandaloneSceneBuilder
    {
        const string SceneDirectory = "Assets/Scenes/Tests";

        [MenuItem("Critical Shift/Prototype/Build All Standalone Machine Scenes")]
        public static void BuildAll()
        {
            Directory.CreateDirectory(SceneDirectory);
            SaveScene("ConveyorStandalone", BuildConveyor);
            SaveScene("CrusherStandalone", BuildCrusher);
            SaveScene("ReactorStandalone", BuildReactor);
            SaveScene("OCRUStandalone", BuildOcru);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[CriticalShift] Built four standalone machine scenes under " + SceneDirectory);
        }

        public static void BuildAllCommandLine() { BuildAll(); }

        static void SaveScene(string name, Action build)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            CreateCommon(name);
            build();
            EditorSceneManager.SaveScene(scene, SceneDirectory + "/" + name + ".unity");
        }

        static void CreateCommon(string title)
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = title + " Floor";
            floor.transform.position = new Vector3(0f, -.25f, 0f);
            floor.transform.localScale = new Vector3(14f, .5f, 10f);
            var light = new GameObject("Test Directional Light").AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1f;
            light.transform.rotation = Quaternion.Euler(48f, -30f, 0f);
            var camera = new GameObject("Test Camera").AddComponent<Camera>();
            camera.transform.position = new Vector3(0f, 6f, -10f);
            camera.transform.rotation = Quaternion.Euler(20f, 0f, 0f);
        }

        static void BuildConveyor()
        {
            var belt = GameObject.CreatePrimitive(PrimitiveType.Cube);
            belt.name = "Conveyor Machine";
            belt.transform.localScale = new Vector3(7f, .4f, 2f);
            belt.GetComponent<BoxCollider>().isTrigger = true;
            var conveyor = belt.AddComponent<PrototypeConveyor>();
            var output = new GameObject("Output").transform;
            output.position = new Vector3(0f, .5f, 3f);
            conveyor.output = output;
            var ore = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            ore.name = "Carryable Ore Input";
            ore.transform.position = new Vector3(0f, 1f, -3f);
            ore.AddComponent<Rigidbody>();
            ore.AddComponent<PrototypeOre>();
            ore.AddComponent<PrototypeCarryable>();
        }

        static void BuildCrusher()
        {
            var crusher = GameObject.CreatePrimitive(PrimitiveType.Cube);
            crusher.name = "Crusher Machine";
            crusher.transform.position = new Vector3(0f, 1f, 0f);
            crusher.transform.localScale = new Vector3(3f, 2f, 3f);
            crusher.AddComponent<PrototypeCrusher>().BeginOperation();
        }

        static void BuildReactor()
        {
            var reactor = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            reactor.name = "Reactor Machine";
            reactor.transform.position = new Vector3(0f, 1.25f, 0f);
            reactor.transform.localScale = new Vector3(2f, 1.25f, 2f);
            reactor.AddComponent<PrototypeReactorMachine>();
            var valve = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            valve.name = "Cooling Valve";
            valve.transform.position = new Vector3(4f, 1f, 0f);
            valve.AddComponent<PrototypeCoolingValve>();
            var gauge = GameObject.CreatePrimitive(PrimitiveType.Cube);
            gauge.name = "Demand Gauge";
            gauge.transform.position = new Vector3(-4f, 1f, 0f);
            gauge.AddComponent<PrototypeDemandGauge>();
            for (int i = 0; i < 2; i++)
            {
                var fuel = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                fuel.name = "Fuel Assembly " + (i + 1);
                fuel.transform.position = new Vector3(-1f + i * 2f, .8f, -3f);
                fuel.AddComponent<PrototypeFuelAssembly>().batch = new PrototypeBatch { grade = .8f, mass = .5f, fuelQuality = .75f };
            }
        }

        static void BuildOcru()
        {
            var cabinet = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cabinet.name = "OCRU Reanimation Machine";
            cabinet.transform.position = new Vector3(2f, 1.25f, 0f);
            cabinet.transform.localScale = new Vector3(2f, 2.5f, 2f);
            cabinet.AddComponent<PrototypeReanimationStation>();
            var worker = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            worker.name = "Incapacitated Worker Input";
            worker.transform.position = new Vector3(-2f, 1f, 0f);
            worker.AddComponent<Rigidbody>();
            var body = worker.AddComponent<PrototypeWorkerBody>();
            body.Incapacitate();
        }
    }
}
#endif
