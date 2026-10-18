using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Normal-mode debug poses only. The body rig invokes this while every segment is kinematic and non-contacting.</summary>
    internal sealed class WorkerKinematicPose
    {
        private sealed class Limb
        {
            internal readonly bool Arm, Left;
            private readonly int upperIndex, lowerIndex, parentIndex;
            private readonly Vector3 upperAnchor, parentAnchor, lowerAnchor, elbowAnchor;
            private readonly Quaternion upperRest, lowerRest;
            internal Limb(Rigidbody[] bodies, Rigidbody upper, Rigidbody lower, bool arm, bool left)
            {
                var upperJoint = upper.GetComponent<CharacterJoint>(); var lowerJoint = lower.GetComponent<CharacterJoint>();
                if (upperJoint == null || upperJoint.connectedBody == null || lowerJoint == null || lowerJoint.connectedBody != upper)
                    throw new ArgumentException("A visual limb must use the bound physical two-segment joint chain.");
                var parent = upperJoint.connectedBody;
                upperIndex = Array.IndexOf(bodies, upper); lowerIndex = Array.IndexOf(bodies, lower);
                parentIndex = Array.IndexOf(bodies, parent);
                if (parentIndex < 0) throw new ArgumentException("A limb parent must belong to the same worker body.");
                Arm = arm; Left = left;
                upperAnchor = upperJoint.anchor; parentAnchor = upperJoint.connectedAnchor;
                lowerAnchor = lowerJoint.anchor; elbowAnchor = lowerJoint.connectedAnchor;
                upperRest = Quaternion.Inverse(parent.rotation) * upper.rotation;
                lowerRest = Quaternion.Inverse(upper.rotation) * lower.rotation;
            }
            internal void Apply(Vector3[] positions, Quaternion[] rotations, float swing, float bend)
            {
                Quaternion upperRotation = rotations[parentIndex] * upperRest * Quaternion.AngleAxis(swing, Vector3.right);
                Vector3 shoulder = positions[parentIndex] + rotations[parentIndex] * parentAnchor;
                rotations[upperIndex] = upperRotation; positions[upperIndex] = shoulder - upperRotation * upperAnchor;
                Quaternion lowerRotation = upperRotation * lowerRest * Quaternion.AngleAxis(bend, Vector3.right);
                Vector3 elbow = positions[upperIndex] + upperRotation * elbowAnchor;
                rotations[lowerIndex] = lowerRotation; positions[lowerIndex] = elbow - lowerRotation * lowerAnchor;
            }
        }

        private readonly Transform root;
        private readonly Rigidbody[] bodies;
        private readonly Vector3[] positions;
        private readonly Quaternion[] rotations;
        private readonly Vector3[] worldPositions;
        private readonly Quaternion[] worldRotations;
        private readonly int[] publicationOrder;
        private readonly Transform[][] boundHierarchy;
        private readonly List<Limb> limbs = new List<Limb>(4);
        private readonly HashSet<Rigidbody> animated = new HashSet<Rigidbody>();
        private Func<bool> handsBusy;
        private Vector3 lastPosition;
        private float phase, walking, carrying;
        private bool started;

        internal WorkerKinematicPose(Transform workerRoot, Rigidbody[] segments, Vector3[] restPositions, Quaternion[] restRotations)
        {
            root = workerRoot; bodies = segments; positions = restPositions; rotations = restRotations;
            worldPositions = new Vector3[bodies.Length]; worldRotations = new Quaternion[bodies.Length]; lastPosition = root.position;
            publicationOrder = new int[bodies.Length]; boundHierarchy = new Transform[bodies.Length][];
            for (int i = 0; i < publicationOrder.Length; i++)
            {
                publicationOrder[i] = i;
                var chain = new List<Transform>();
                for (var node = bodies[i].transform; node != root; node = node.parent)
                {
                    if (node == null) throw new ArgumentException("A presented segment must remain beneath its bound controller root.");
                    chain.Add(node);
                }
                boundHierarchy[i] = chain.ToArray();
            }
            // PublishTransform requires topmost-to-bottommost order. Keep pose/limb indices untouched;
            // this separate ordering is computed only during setup, including for nested registered segments.
            Array.Sort(publicationOrder, (left, right) =>
            {
                int order = boundHierarchy[left].Length.CompareTo(boundHierarchy[right].Length);
                return order != 0 ? order : left.CompareTo(right);
            });
        }

        internal void BindLimb(Rigidbody upper, Rigidbody lower, bool arm, bool left)
        {
            if (started || upper == null || lower == null || limbs.Count >= 4 || Array.IndexOf(bodies, upper) < 0 ||
                Array.IndexOf(bodies, lower) < 0 || animated.Contains(upper) || animated.Contains(lower))
                throw new InvalidOperationException("Bind each normal-mode limb once before presentation starts.");
            var limb = new Limb(bodies, upper, lower, arm, left);
            animated.Add(upper); animated.Add(lower); limbs.Add(limb);
        }

        internal void BindHands(Func<bool> query)
        {
            if (started || handsBusy != null || query == null) throw new InvalidOperationException("Bind the hands query before presentation starts.");
            handsBusy = query;
        }

        internal void Reset() { lastPosition = root.position; phase = 0; walking = 0; carrying = 0; }

        internal void Update(float seconds)
        {
            started = true;
            float dt = Mathf.Min(seconds, 0.05f); Vector3 delta = root.position - lastPosition; lastPosition = root.position;
            float speed = dt > 0 && delta.sqrMagnitude < 9 ? Vector3.ProjectOnPlane(delta, Vector3.up).magnitude / dt : 0;
            walking = Mathf.MoveTowards(walking, Mathf.Clamp01(speed / 3.2f), dt * 6);
            carrying = Mathf.MoveTowards(carrying, handsBusy != null && handsBusy() ? 1 : 0, dt * 4);
            phase = Mathf.Repeat(phase + walking * dt * 9, Mathf.PI * 2);
            PrepareRestPose();
            foreach (var limb in limbs)
            {
                float wave = Mathf.Sin(phase + (limb.Left ? 0 : Mathf.PI));
                float swing = wave * walking * (limb.Arm ? 16 : -18);
                float bend = limb.Arm ? Mathf.Lerp(6, -15, carrying) : Mathf.Max(0, wave) * walking * 24;
                if (limb.Arm) swing = Mathf.Lerp(swing, -30, carrying);
                limb.Apply(worldPositions, worldRotations, swing, bend);
            }
            PublishPose();
            Physics.SyncTransforms();
        }

        internal void RestoreRestPose()
        {
            PrepareRestPose(); PublishPose();
        }

        private void PrepareRestPose()
        {
            if (!HasBoundHierarchy()) throw new InvalidOperationException("A worker's bound presentation hierarchy changed.");
            Quaternion rotation = root.rotation;
            for (int i = 0; i < bodies.Length; i++)
            {
                if (bodies[i] == null || !bodies[i].isKinematic) throw new InvalidOperationException("Normal presentation cannot write a dynamic or missing body.");
                worldPositions[i] = root.TransformPoint(positions[i]); worldRotations[i] = rotation * rotations[i];
            }
        }

        private void PublishPose()
        {
            // These non-contacting poses are explicit teleports, not physical movement targets. Commit
            // all precomputed native poses before publishing any deferred Transform from the physics engine.
            // SyncTransforms alone runs in the other direction and cannot publish Rigidbody setters.
            for (int i = 0; i < bodies.Length; i++)
            { bodies[i].position = worldPositions[i]; bodies[i].rotation = worldRotations[i]; }
            foreach (int index in publicationOrder) bodies[index].PublishTransform();
        }

        internal bool HasBoundHierarchy()
        {
            if (root == null) return false;
            for (int i = 0; i < bodies.Length; i++)
            {
                if (bodies[i] == null) return false;
                var node = bodies[i].transform;
                foreach (var bound in boundHierarchy[i])
                {
                    if (node == null || node != bound) return false;
                    node = node.parent;
                }
                if (node != root) return false;
            }
            return true;
        }
    }
}
