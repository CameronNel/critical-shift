using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.FacilityPhysics.Unity;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Features.Workers.Editor;
using CriticalShift.Unity.Shared;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Bootstrap.Editor
{
    public sealed class FacilitySceneSetup : EditorWindow
    {
        private WorkerAnimationLibrary library;
        private CarryableKind objectKind;
        private ControlKind controlKind;
        [MenuItem("Critical Shift/Scene bindings")]
        public static void Open() { GetWindow<FacilitySceneSetup>("Scene bindings"); }
        private void OnGUI()
        {
            EditorGUILayout.HelpBox("Select a worker, physical object, or interaction marker. These tools add gameplay components and explicit scene references. Animation sources and clips are never changed.", MessageType.Info);
            library = (WorkerAnimationLibrary)EditorGUILayout.ObjectField("Finished clip library", library, typeof(WorkerAnimationLibrary), false);
            if (GUILayout.Button("Bind selected worker")) BindWorker();
            if (GUILayout.Button("Build selected ragdoll physics")) BuildRagdoll();
            objectKind = (CarryableKind)EditorGUILayout.EnumPopup("Object kind", objectKind);
            if (GUILayout.Button("Bind selected physical object")) BindObject();
            controlKind = (ControlKind)EditorGUILayout.EnumPopup("Control kind", controlKind);
            if (GUILayout.Button("Bind selected control marker")) BindControl();
            if (GUILayout.Button("Bind selected downed handle")) BindHandle();
            if (GUILayout.Button("Bind selected production machine")) BindMachine();
            if (GUILayout.Button("Wire scene references")) WireScene();
            if (GUILayout.Button("Validate scene bindings")) ValidateScene();
        }
        private static GameObject Selected()
        { if (Selection.activeGameObject == null) throw new InvalidOperationException("Select a scene object."); return Selection.activeGameObject; }
        private static T Add<T>(GameObject go) where T : Component
        { return go.GetComponent<T>() ?? Undo.AddComponent<T>(go); }
        private static void Set(UnityEngine.Object owner, string field, UnityEngine.Object value)
        { var data = new SerializedObject(owner); var property = data.FindProperty(field);
          if (property == null) throw new InvalidOperationException("Missing serialized field: " + field);
          property.objectReferenceValue = value; data.ApplyModifiedProperties(); }
        private static void SetEnum(UnityEngine.Object owner, string field, int value)
        { var data = new SerializedObject(owner); data.FindProperty(field).intValue = value; data.ApplyModifiedProperties(); }
        private static void SetArray(UnityEngine.Object owner, string field, UnityEngine.Object[] values)
        { var data = new SerializedObject(owner); var array = data.FindProperty(field); array.arraySize = values.Length;
          for (int i = 0; i < values.Length; i++) array.GetArrayElementAtIndex(i).objectReferenceValue = values[i]; data.ApplyModifiedProperties(); }
        private static Transform Anchor(GameObject parent, string name, Vector3 position)
        {
            var existing = parent.transform.Find(name); if (existing != null) return existing;
            var go = new GameObject(name); Undo.RegisterCreatedObjectUndo(go, "Create binding anchor");
            go.transform.SetParent(parent.transform, false); go.transform.localPosition = position; return go.transform;
        }
        private void BindWorker()
        {
            var go = Selected();
            if (go.GetComponent<Animator>() != null && go.GetComponent<WorkerController>() == null)
            {
                var wrapper = new GameObject(go.name + " worker"); Undo.RegisterCreatedObjectUndo(wrapper, "Create worker motion root");
                wrapper.transform.SetParent(go.transform.parent, false);
                wrapper.transform.SetPositionAndRotation(go.transform.position, go.transform.rotation);
                Undo.SetTransformParent(go.transform, wrapper.transform, "Parent worker visual model");
                go = wrapper; Selection.activeGameObject = go;
            }
            var capsule = Add<CharacterController>(go);
            Undo.RecordObject(capsule, "Configure worker capsule");
            capsule.height = 1.55f; capsule.center = Vector3.up * 0.775f; capsule.radius = 0.25f;
            capsule.stepOffset = 0.22f; capsule.slopeLimit = 50; capsule.skinWidth = 0.03f;
            var worker = Add<WorkerController>(go); var movement = Add<WorkerMovementAnimator>(go); var ragdoll = Add<WorkerRagdoll>(go);
            var crouch = Add<WorkerCrouchPose>(go); Set(worker, "crouchPose", crouch);
            var animator = go.GetComponentInChildren<Animator>(); if (animator == null) animator = Add<Animator>(Anchor(go, "WorkerModel", Vector3.zero).gameObject);
            var eye = Anchor(go, "WorkerEye", new Vector3(0, 1.4f, 0.2f)); Add<Camera>(eye.gameObject).fieldOfView = 60;
            Set(worker, "capsule", capsule); Set(worker, "movement", movement); Set(worker, "ragdoll", ragdoll); Set(worker, "eye", eye);
            Set(worker, "grip", Anchor(go, "CarryGrip", new Vector3(0, 1.02f, 0.48f)));
            Set(movement, "animator", animator); if (library != null) Set(movement, "library", library);
            var hips = animator.isHuman ? animator.GetBoneTransform(HumanBodyBones.Hips) : go.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == "Hips");

            Set(crouch, "hips", hips);
            foreach (var pair in new[] { ("leftThigh", "LeftUpperLeg", HumanBodyBones.LeftUpperLeg), ("leftShin", "LeftLowerLeg", HumanBodyBones.LeftLowerLeg),
                ("leftFoot", "LeftFoot", HumanBodyBones.LeftFoot), ("rightThigh", "RightUpperLeg", HumanBodyBones.RightUpperLeg),
                ("rightShin", "RightLowerLeg", HumanBodyBones.RightLowerLeg), ("rightFoot", "RightFoot", HumanBodyBones.RightFoot) })
            { var bone = animator.isHuman ? animator.GetBoneTransform(pair.Item3) : go.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == pair.Item2); Set(crouch, pair.Item1, bone); }
            foreach (var pair in new[] { ("leftHand", "LeftHand", HumanBodyBones.LeftHand), ("rightHand", "RightHand", HumanBodyBones.RightHand), ("head", "Head", HumanBodyBones.Head) })
            { var bone = animator.isHuman ? animator.GetBoneTransform(pair.Item3) : go.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == pair.Item2); Set(worker, pair.Item1, bone); }
            var tool = go.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == "Tool"); if (tool != null) Set(worker, "toolGrip", tool);
            Debug.Log("Worker binding added. Use Build selected ragdoll physics to generate limb bodies, shapes and joints; assign final clip library and mesh visibility references.", go);
            WireScene();
        }
        private void BindObject()
        {
            var go = Selected(); var item = Add<CarryableObject>(go);
            if (objectKind == CarryableKind.Body)
            {
                var worker = go.GetComponent<WorkerController>();
                if (worker == null || worker.PhysicalBody == null) throw new InvalidOperationException("Select a worker root with built ragdoll physics for a body binding.");
                Set(item, "body", worker.PhysicalBody); Set(item, "workerBody", worker); Set(item, "contact", worker.PhysicalBody.transform);
                Set(item, "objectGrip", Anchor(worker.PhysicalBody.gameObject, "BodyGrip", Vector3.up * .1f));
                Set(item, "assistantObjectGrip", Anchor(worker.PhysicalBody.gameObject, "BodyAssistantGrip", Vector3.down * .1f));
            }
            else { Set(item, "body", Add<Rigidbody>(go)); Set(item, "objectGrip", Anchor(go, "ObjectGrip", Vector3.zero)); }
            SetEnum(item, "kind", (int)objectKind); SetEnum(item, "operation", (int)(objectKind == CarryableKind.Cart ? SceneOperation.Push : objectKind == CarryableKind.Body ? SceneOperation.Drag : SceneOperation.Grab));
            WireScene();
        }
        private static void BuildRagdoll()
        {
            var worker = Selected().GetComponentInParent<WorkerController>();
            if (worker == null) throw new InvalidOperationException("Bind/select the worker first.");
            Undo.IncrementCurrentGroup(); int group = Undo.GetCurrentGroup(); Undo.SetCurrentGroupName("Build worker ragdoll physics");
            try { WorkerRagdollBuilder.Build(worker, worker.GetComponentInChildren<Animator>(), worker.GetComponent<WorkerRagdoll>()); WireScene(); Undo.CollapseUndoOperations(group); }
            catch { Undo.RevertAllDownToGroup(group); throw; }
        }
        private void BindControl()
        {
            var go = Selected(); var control = Add<FacilityControl>(go); SetEnum(control, "kind", (int)controlKind);
            SceneOperation op = controlKind == ControlKind.Lever ? SceneOperation.Lever : controlKind == ControlKind.Valve ? SceneOperation.ValveTurn :
                controlKind == ControlKind.Door ? SceneOperation.Open : controlKind == ControlKind.ServicePort ? SceneOperation.Connect :
                controlKind == ControlKind.DigSite ? SceneOperation.Dig : controlKind == ControlKind.SuitLocker ? SceneOperation.Suit :
                controlKind == ControlKind.ReanimationStation ? SceneOperation.Reanimation : controlKind == ControlKind.Aid ? SceneOperation.Help : SceneOperation.Button;
            SetEnum(control, "operation", (int)op); Set(control, "contact", go.transform); WireScene();
        }
        private void BindHandle()
        { var go = Selected(); var handle = Add<RagdollHandle>(go); Set(handle, "contact", go.transform); SetEnum(handle, "operation", (int)SceneOperation.Grab); WireScene(); }
        private void BindMachine()
        {
            var go = Selected(); var machine = Add<MachineBinding>(go); Set(machine, "slot", Anchor(go, "ContainerSlot", Vector3.up));
            SetEnum(machine, "operation", (int)SceneOperation.Button); WireScene();
        }
        private static T[] Components<T>() where T : Component => ObjectFind<T>();
        private static T[] ObjectFind<T>() where T : Component => UnityEngine.Object.FindObjectsByType<T>(FindObjectsInactive.Include, FindObjectsSortMode.None)
            .Where(c => !EditorUtility.IsPersistent(c) && c.gameObject.scene == UnityEngine.SceneManagement.SceneManager.GetActiveScene()).ToArray();
        public static void WireScene()
        {
            var hosts = Components<FacilitySceneHost>();
            if (hosts.Length > 1) throw new InvalidOperationException("Keep one FacilitySceneHost in the active scene.");
            FacilitySceneHost host;
            if (hosts.Length == 0) { var go = new GameObject("FacilitySceneHost"); Undo.RegisterCreatedObjectUndo(go, "Create host"); host = Add<FacilitySceneHost>(go); }
            else host = hosts[0];
            var workers = Components<WorkerController>(); var targets = Components<SceneTarget>();
            SetArray(host, "workers", workers); SetArray(host, "targets", targets);
            foreach (var worker in workers) Set(worker, "gateway", host);
            foreach (var item in Components<CarryableObject>()) Set(item, "gateway", host);
            foreach (var handle in Components<RagdollHandle>()) Set(handle, "gateway", host);
            foreach (var hazard in Components<WorkerCollisionHazard>()) Set(hazard, "gateway", host);
            EditorSceneManager.MarkSceneDirty(host.gameObject.scene);
        }
        public static void ValidateScene()
        {
            var errors = new List<string>(); var ids = new HashSet<Guid>();
            foreach (var target in Components<SceneTarget>())
            {
                if (!ids.Add(target.Id)) errors.Add("Duplicate target identity: " + target.name);
                if (!target.Supports(target.Operation)) errors.Add("Operation does not match component kind: " + target.name);
                if (target.GetComponentInChildren<Collider>() == null) errors.Add("Interaction target needs a raycast collider: " + target.name);
                if (target is CarryableObject item)
                {
                    if (item.Body == null || item.Body.isKinematic && item.Kind != CarryableKind.Body) errors.Add(item.name + ": assign a dynamic object Rigidbody");
                    if (item.Kind == CarryableKind.Body && !item.ValidBodyBinding) errors.Add(item.name + ": bind the represented worker's actual pelvis body");
                }
                if (target is MachineBinding machine)
                {
                    if (machine.Slot == null) errors.Add(machine.name + ": assign machine slot");
                    if (!Components<SceneTarget>().Contains(machine.Machine)) errors.Add(machine.name + ": referenced machine is outside this scene");
                }
                if (target is FacilityControl control)
                {
                    var controlData = new SerializedObject(control);
                    if (control.Kind == ControlKind.Door && controlData.FindProperty("doorHinge").objectReferenceValue == null) errors.Add(control.name + ": assign door HingeJoint");
                    if (control.Kind == ControlKind.ReanimationStation && (control.Patient == null || control.WorkerAnchor == null)) errors.Add(control.name + ": assign patient and chamber anchor");
                }
            }
            ids.Clear();
            foreach (var worker in Components<WorkerController>())
            {
                if (!ids.Add(worker.Id)) errors.Add("Duplicate worker identity: " + worker.name);
                var data = new SerializedObject(worker);
                foreach (var field in new[] { "gateway", "movement", "capsule", "eye", "grip", "ragdoll" })
                    if (data.FindProperty(field).objectReferenceValue == null) errors.Add(worker.name + ": assign " + field);
                var movement = worker.GetComponent<WorkerMovementAnimator>();
                if (movement == null) { errors.Add(worker.name + ": add WorkerMovementAnimator"); continue; }
                var movementData = new SerializedObject(movement);
                var boundAnimator = movementData.FindProperty("animator").objectReferenceValue as Animator;
                if (boundAnimator == null || boundAnimator.transform == worker.transform) errors.Add(worker.name + ": bind Animator on the visual child, separate from the capsule root");
                var library = movementData.FindProperty("library").objectReferenceValue as WorkerAnimationLibrary;
                if (library == null) errors.Add(worker.name + ": assign finished animation library");
                else try { library.CreateClipTable(); } catch (Exception error) { errors.Add(worker.name + ": " + error.Message); }
                var ragdoll = worker.GetComponent<WorkerRagdoll>();
                if (ragdoll == null) { errors.Add(worker.name + ": add WorkerRagdoll"); continue; }
                var ragdollData = new SerializedObject(ragdoll);
                if (!ragdoll.TryValidate(out var ragdollError)) errors.Add(worker.name + ": " + ragdollError);
            }
            if (Components<WorkerController>().Length == 0) errors.Add("Bind at least one worker.");
            if (Components<WorkerController>().Count(w => new SerializedObject(w).FindProperty("localInput").boolValue) != 1)
                errors.Add("Select exactly one Local Input worker/camera for this host scene; transport remains separate.");
            if (errors.Count > 0) throw new InvalidOperationException(string.Join("\n", errors));
            Debug.Log("Scene reference checks passed. Native motion, physics, contact alignment and Player tests remain required.");
        }
    }
}
