#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using CriticalShift.Prototype;

namespace CriticalShift.Editor
{
    public static class PrototypeProductionSceneMenu
    {
        [MenuItem("Critical Shift/Prototype/Build Production Shoebox")]
        public static void BuildShoebox() { PrototypeMachineSceneBuilder.BuildProductionShoebox(Vector3.zero); Selection.activeGameObject = GameObject.Find("Prototype Production Shoebox"); }
        [MenuItem("Critical Shift/Prototype/Build Conveyor Test")]
        public static void BuildConveyor() { var root = new GameObject("Conveyor Standalone Test"); var c = new GameObject("Conveyor"); c.transform.SetParent(root.transform); c.AddComponent<PrototypeConveyor>(); Selection.activeGameObject = root; }
        [MenuItem("Critical Shift/Prototype/Build Crusher Test")]
        public static void BuildCrusher() { var root = new GameObject("Crusher Standalone Test"); var c = new GameObject("Crusher"); c.transform.SetParent(root.transform); c.AddComponent<PrototypeCrusher>(); Selection.activeGameObject = root; }
        [MenuItem("Critical Shift/Prototype/Build Fuel Reactor Test")]
        public static void BuildFuelReactor() { var root = new GameObject("Fuel Reactor Standalone Test"); var r = new GameObject("Reactor"); r.transform.SetParent(root.transform); r.AddComponent<PrototypeReactorMachine>(); new GameObject("Cooling Valve").transform.SetParent(root.transform); Selection.activeGameObject = root; }
    }
}
#endif
