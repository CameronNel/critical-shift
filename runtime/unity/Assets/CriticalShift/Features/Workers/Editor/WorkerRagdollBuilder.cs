using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Features.Workers.Unity;
using UnityEditor;
using UnityEngine;

namespace CriticalShift.Features.Workers.Editor
{
    public static class WorkerRagdollBuilder
    {
        private readonly struct Segment
        {
            public readonly string Name, Parent, End;
            public readonly HumanBodyBones Human;
            public readonly float Mass;
            public readonly int Kind;
            public Segment(string name, HumanBodyBones human, string parent, string end, float mass, int kind = 0)
            { Name = name; Human = human; Parent = parent; End = end; Mass = mass; Kind = kind; }
        }
        private static Segment[] Segments() => new[]
        {
            new Segment("Hips", HumanBodyBones.Hips, null, "Spine", .16f),
            new Segment("Spine", HumanBodyBones.Spine, "Hips", "Chest", .10f),
            new Segment("Chest", HumanBodyBones.Chest, "Spine", "Head", .16f),
            new Segment("Head", HumanBodyBones.Head, "Chest", null, .08f, 1),
            new Segment("LeftUpperArm", HumanBodyBones.LeftUpperArm, "Chest", "LeftLowerArm", .045f, 2),
            new Segment("LeftLowerArm", HumanBodyBones.LeftLowerArm, "LeftUpperArm", "LeftHand", .025f, 3),
            new Segment("LeftHand", HumanBodyBones.LeftHand, "LeftLowerArm", null, .0125f, 4),
            new Segment("RightUpperArm", HumanBodyBones.RightUpperArm, "Chest", "RightLowerArm", .045f, 2),
            new Segment("RightLowerArm", HumanBodyBones.RightLowerArm, "RightUpperArm", "RightHand", .025f, 3),
            new Segment("RightHand", HumanBodyBones.RightHand, "RightLowerArm", null, .0125f, 4),
            new Segment("LeftUpperLeg", HumanBodyBones.LeftUpperLeg, "Hips", "LeftLowerLeg", .10f, 5),
            new Segment("LeftLowerLeg", HumanBodyBones.LeftLowerLeg, "LeftUpperLeg", "LeftFoot", .055f, 6),
            new Segment("LeftFoot", HumanBodyBones.LeftFoot, "LeftLowerLeg", null, .0125f, 7),
            new Segment("RightUpperLeg", HumanBodyBones.RightUpperLeg, "Hips", "RightLowerLeg", .10f, 5),
            new Segment("RightLowerLeg", HumanBodyBones.RightLowerLeg, "RightUpperLeg", "RightFoot", .055f, 6),
            new Segment("RightFoot", HumanBodyBones.RightFoot, "RightLowerLeg", null, .0125f, 7),
        };

        // Reads skeleton transforms; only physics components and references are authored.
        public static void Build(WorkerController worker, Animator animator, WorkerRagdoll ragdoll)
        {
            if (worker == null || animator == null || ragdoll == null || !animator.transform.IsChildOf(worker.transform) || animator.transform == worker.transform)
                throw new InvalidOperationException("Bind the worker's Animator on a separate visual child first.");
            if (worker.GetComponent<Rigidbody>() != null) throw new InvalidOperationException("Remove the competing Rigidbody from the capsule root before building limb physics.");
            var segments = Segments(); var transforms = new Dictionary<string, Transform>(); var unique = new HashSet<Transform>();
            var children = animator.GetComponentsInChildren<Transform>(true);
            foreach (var segment in segments)
            {
                var bone = animator.isHuman ? animator.GetBoneTransform(segment.Human) : null;
                if (bone == null)
                {
                    var candidates = children.Where(t => t.name == segment.Name).ToArray();
                    if (candidates.Length != 1) throw new InvalidOperationException("Resolve exactly one skeleton bone: " + segment.Name);
                    bone = candidates[0];
                }
                if (!unique.Add(bone)) throw new InvalidOperationException("Two physical segments resolve to the same bone.");
                if (bone.GetComponents<Joint>().Length > 1 || bone.GetComponents<Joint>().Any(j => !(j is CharacterJoint)))
                    throw new InvalidOperationException("Resolve existing incompatible joints on " + bone.name);
                if (bone.GetComponents<Collider>().Any(c => c is MeshCollider mesh && !mesh.convex || c.isTrigger))
                    throw new InvalidOperationException("Resolve trigger/non-convex bone colliders on " + bone.name);
                transforms.Add(segment.Name, bone);
            }
            float height = Mathf.Abs(Vector3.Dot(transforms["Head"].position - transforms["LeftFoot"].position, worker.transform.up)) * 1.25f;
            if (!float.IsFinite(height) || height < 0.5f || height > 3) throw new InvalidOperationException("Use a metre-scale worker skeleton between 0.5 and 3 metres tall.");
            var data = new SerializedObject(ragdoll); float mass = data.FindProperty("tuning").FindPropertyRelative("totalMass").floatValue;
            if (!float.IsFinite(mass) || mass < 10 || mass > 200) throw new InvalidOperationException("Set a ragdoll mass between 10 and 200 kg.");
            var bodies = new Dictionary<string, Rigidbody>(); var shapes = new List<Collider>();
            var hazard = GetOrAdd<WorkerCollisionHazard>(worker.gameObject);
            foreach (var segment in segments)
            {
                var bone = transforms[segment.Name]; var body = GetOrAdd<Rigidbody>(bone.gameObject); Undo.RecordObject(body, "Configure ragdoll body");
                body.mass = mass * segment.Mass; body.isKinematic = true; body.useGravity = true;
                body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.Discrete;
                bodies.Add(segment.Name, body);
                var relay = GetOrAdd<RagdollCollisionRelay>(bone.gameObject); var relayData = new SerializedObject(relay);
                relayData.FindProperty("hazard").objectReferenceValue = hazard; relayData.ApplyModifiedProperties();
                Vector3 end = segment.End != null ? transforms[segment.End].position : bone.position +
                    (segment.Kind == 7 ? worker.transform.forward : segment.Kind == 4 ? (segment.Name.StartsWith("Left") ? -worker.transform.right : worker.transform.right) : worker.transform.up) * height * (segment.Kind == 1 ? .18f : .08f);
                var shape = GetOrAdd<CapsuleCollider>(bone.gameObject); Undo.RecordObject(shape, "Configure limb shape");
                Vector3 local = bone.InverseTransformVector(end - bone.position);
                shape.direction = Dominant(local); shape.center = local * .5f;
                float length = local.magnitude;
                shape.radius = Mathf.Max(.015f, length * (segment.Kind <= 1 ? .42f : segment.Kind == 5 ? .22f : .18f));
                shape.height = Mathf.Max(shape.radius * 2, length * .95f); shape.isTrigger = false; shape.enabled = false;
                shapes.AddRange(bone.GetComponents<Collider>());
            }
            foreach (var segment in segments)
            {
                if (segment.Parent == null) continue;
                var bone = transforms[segment.Name]; var joint = GetOrAdd<CharacterJoint>(bone.gameObject); Undo.RecordObject(joint, "Configure ragdoll joint");
                joint.connectedBody = bodies[segment.Parent]; joint.anchor = Vector3.zero; joint.autoConfigureConnectedAnchor = true;
                Vector3 axis = segment.Kind == 6 ? worker.transform.right : segment.Kind == 3 ? Vector3.Cross(transforms[segment.End].position - bone.position, worker.transform.forward).normalized :
                    (segment.End != null ? transforms[segment.End].position - bone.position : worker.transform.up);
                joint.axis = bone.InverseTransformDirection(axis.normalized);
                Vector3 swing = Vector3.ProjectOnPlane(bone.InverseTransformDirection(worker.transform.forward), joint.axis);
                if (swing.sqrMagnitude < .01f) swing = Vector3.ProjectOnPlane(bone.InverseTransformDirection(worker.transform.right), joint.axis);
                joint.swingAxis = swing.normalized;
                float low = -20, high = 20, swing1 = 25, swing2 = 20;
                if (segment.Kind == 1) { low = -40; high = 40; swing1 = swing2 = 40; }
                if (segment.Kind == 2) { low = -60; high = 60; swing1 = 80; swing2 = 65; }
                if (segment.Kind == 3) { low = -5; high = 120; swing1 = swing2 = 5; }
                if (segment.Kind == 5) { low = -30; high = 30; swing1 = 60; swing2 = 35; }
                if (segment.Kind == 6) { low = -5; high = 125; swing1 = swing2 = 5; }
                joint.lowTwistLimit = Limit(low); joint.highTwistLimit = Limit(high); joint.swing1Limit = Limit(swing1); joint.swing2Limit = Limit(swing2);
                joint.enableCollision = false; joint.enablePreprocessing = false; joint.enableProjection = true;
                joint.projectionDistance = .05f; joint.projectionAngle = 10; joint.breakForce = joint.breakTorque = float.PositiveInfinity;
            }
            data.Update(); data.FindProperty("pelvis").objectReferenceValue = bodies["Hips"];
            SetArray(data.FindProperty("bones"), segments.Select(s => (UnityEngine.Object)bodies[s.Name]).ToArray());
            SetArray(data.FindProperty("colliders"), shapes.Cast<UnityEngine.Object>().ToArray());
            data.FindProperty("anatomicalForward").vector3Value = transforms["Hips"].InverseTransformDirection(worker.transform.forward);
            data.FindProperty("anatomicalUp").vector3Value = transforms["Hips"].InverseTransformDirection(worker.transform.up);
            data.ApplyModifiedProperties();
            if (!ragdoll.TryValidate(out var reason)) throw new InvalidOperationException(reason);
            EditorUtility.SetDirty(ragdoll);
        }
        private static SoftJointLimit Limit(float degrees) => new SoftJointLimit { limit = degrees, bounciness = 0, contactDistance = 2 };
        private static int Dominant(Vector3 value) => Mathf.Abs(value.x) > Mathf.Abs(value.y) && Mathf.Abs(value.x) > Mathf.Abs(value.z) ? 0 : Mathf.Abs(value.z) > Mathf.Abs(value.y) ? 2 : 1;
        private static T GetOrAdd<T>(GameObject go) where T : Component => go.GetComponent<T>() ?? Undo.AddComponent<T>(go);
        private static void SetArray(SerializedProperty array, UnityEngine.Object[] values)
        { array.arraySize = values.Length; for (int i = 0; i < values.Length; i++) array.GetArrayElementAtIndex(i).objectReferenceValue = values[i]; }
    }
}
