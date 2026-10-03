using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    internal static class WorkerRagdollRigValidation
    {
        public static bool RootConvention(Transform root) => Finite(root.position) &&
            (root.lossyScale - Vector3.one).sqrMagnitude < .000001f && Vector3.Dot(root.up, Vector3.up) > .9999f;

        public static bool Validate(Transform root, Rigidbody pelvis, Rigidbody[] bones, Collider[] colliders, out string reason)
        {
            reason = "";
            if (!RootConvention(root)) { reason = "Worker motion root must be upright with positive unit world scale."; return false; }
            var bodies = new HashSet<Rigidbody>(); double mass = 0;
            foreach (var body in bones)
            {
                if (body == null || !bodies.Add(body) || body.transform == root || !body.transform.IsChildOf(root) || !float.IsFinite(body.mass) || body.mass <= 0)
                { reason = "Ragdoll bodies must be unique owned children with positive finite masses."; return false; }
                mass += body.mass;
            }
            if (mass < 10 || mass > 200) { reason = "Aggregate physical ragdoll mass must be 10–200 kg."; return false; }
            if (!bodies.Contains(pelvis) || pelvis.GetComponents<Joint>().Length != 0)
            { reason = "The declared pelvis must be free of joints."; return false; }
            foreach (var owned in root.GetComponentsInChildren<Rigidbody>(true))
                if (!bodies.Contains(owned)) { reason = "Declare every owned physical body."; return false; }
            foreach (var body in bones)
            {
                var visited = new HashSet<Rigidbody>(); var cursor = body;
                while (cursor != pelvis)
                {
                    var joints = cursor.GetComponents<Joint>();
                    if (!visited.Add(cursor) || joints.Length != 1 || !(joints[0] is CharacterJoint joint) ||
                        joint.connectedBody == null || !bodies.Contains(joint.connectedBody) || !ValidJoint(joint))
                    { reason = "Every limb needs a bounded CharacterJoint in one acyclic path to the owned pelvis."; return false; }
                    cursor = joint.connectedBody;
                }
            }
            var shapes = new HashSet<Collider>();
            foreach (var shape in colliders)
                if (shape == null || !shapes.Add(shape) || shape.isTrigger || !bodies.Contains(shape.attachedRigidbody) || !ValidShape(shape))
                { reason = "Declare unique solid box/sphere/capsule shapes of finite metre-scale geometry."; return false; }
            foreach (var shape in root.GetComponentsInChildren<Collider>(true))
                if (!shapes.Contains(shape) && !(shape is CharacterController) && (!shape.isTrigger || shape.attachedRigidbody != null))
                { reason = "Declare every collider attached to an owned body."; return false; }
            foreach (var body in bones)
            {
                bool hasShape = false; foreach (var shape in colliders) if (shape.attachedRigidbody == body) hasShape = true;
                if (!hasShape) { reason = "Each physical body needs a declared shape."; return false; }
            }
            return true;
        }
        private static bool ValidJoint(CharacterJoint joint) => Finite(joint.anchor) && Finite(joint.connectedAnchor) &&
            joint.anchor.magnitude <= 3 && joint.connectedAnchor.magnitude <= 3 &&
            Finite(joint.axis) && Finite(joint.swingAxis) && joint.axis.sqrMagnitude > .5f && joint.swingAxis.sqrMagnitude > .5f &&
            Mathf.Abs(Vector3.Dot(joint.axis.normalized, joint.swingAxis.normalized)) < .1f &&
            ValidLimit(joint.lowTwistLimit, -177, 177) && ValidLimit(joint.highTwistLimit, -177, 177) &&
            joint.lowTwistLimit.limit <= joint.highTwistLimit.limit &&
            ValidLimit(joint.swing1Limit, 0, 177) && ValidLimit(joint.swing2Limit, 0, 177);
        private static bool ValidLimit(SoftJointLimit limit, float min, float max) => float.IsFinite(limit.limit) && limit.limit >= min && limit.limit <= max &&
            float.IsFinite(limit.bounciness) && limit.bounciness >= 0 && limit.bounciness <= 1 &&
            float.IsFinite(limit.contactDistance) && limit.contactDistance >= 0 && limit.contactDistance <= 10;
        private static bool ValidShape(Collider shape)
        {
            if (shape is CapsuleCollider capsule) return Finite(capsule.center) && capsule.center.magnitude <= 3 && Size(capsule.radius) && Size(capsule.height) && capsule.height >= capsule.radius * 2;
            if (shape is SphereCollider sphere) return Finite(sphere.center) && sphere.center.magnitude <= 3 && Size(sphere.radius);
            if (shape is BoxCollider box) return Finite(box.center) && box.center.magnitude <= 3 && Size(box.size.x) && Size(box.size.y) && Size(box.size.z);
            return false;
        }
        private static bool Size(float size) => float.IsFinite(size) && size > 0 && size <= 3;
        private static bool Finite(Vector3 value) => float.IsFinite(value.x) && float.IsFinite(value.y) && float.IsFinite(value.z);
    }
}
