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
            internal readonly Rigidbody Upper, Lower, Parent;
            internal readonly bool Arm, Left;
            private readonly Vector3 upperAnchor, parentAnchor, lowerAnchor, elbowAnchor;
            private readonly Quaternion upperRest, lowerRest;
            internal Limb(Rigidbody upper, Rigidbody lower, bool arm, bool left)
            {
                var upperJoint = upper.GetComponent<CharacterJoint>(); var lowerJoint = lower.GetComponent<CharacterJoint>();
                if (upperJoint == null || upperJoint.connectedBody == null || lowerJoint == null || lowerJoint.connectedBody != upper)
                    throw new ArgumentException("A visual limb must use the bound physical two-segment joint chain.");
                Upper = upper; Lower = lower; Parent = upperJoint.connectedBody; Arm = arm; Left = left;
                upperAnchor = upperJoint.anchor; parentAnchor = upperJoint.connectedAnchor;
                lowerAnchor = lowerJoint.anchor; elbowAnchor = lowerJoint.connectedAnchor;
                upperRest = Quaternion.Inverse(Parent.rotation) * Upper.rotation;
                lowerRest = Quaternion.Inverse(Upper.rotation) * Lower.rotation;
            }
            internal void Apply(float swing, float bend)
            {
                Quaternion upperRotation = Parent.rotation * upperRest * Quaternion.AngleAxis(swing, Vector3.right);
                Vector3 shoulder = Parent.position + Parent.rotation * parentAnchor;
                Upper.rotation = upperRotation; Upper.position = shoulder - upperRotation * upperAnchor;
                Quaternion lowerRotation = upperRotation * lowerRest * Quaternion.AngleAxis(bend, Vector3.right);
                Vector3 elbow = Upper.position + upperRotation * elbowAnchor;
                Lower.rotation = lowerRotation; Lower.position = elbow - lowerRotation * lowerAnchor;
            }
        }

        private readonly Transform root;
        private readonly Rigidbody[] bodies;
        private readonly Vector3[] positions;
        private readonly Quaternion[] rotations;
        private readonly List<Limb> limbs = new List<Limb>(4);
        private readonly HashSet<Rigidbody> animated = new HashSet<Rigidbody>();
        private Func<bool> handsBusy;
        private Vector3 lastPosition;
        private float phase, walking, carrying;
        private bool started;

        internal WorkerKinematicPose(Transform workerRoot, Rigidbody[] segments, Vector3[] restPositions, Quaternion[] restRotations)
        { root = workerRoot; bodies = segments; positions = restPositions; rotations = restRotations; lastPosition = root.position; }

        internal void BindLimb(Rigidbody upper, Rigidbody lower, bool arm, bool left)
        {
            if (started || upper == null || lower == null || limbs.Count >= 4 || Array.IndexOf(bodies, upper) < 0 ||
                Array.IndexOf(bodies, lower) < 0 || animated.Contains(upper) || animated.Contains(lower))
                throw new InvalidOperationException("Bind each normal-mode limb once before presentation starts.");
            var limb = new Limb(upper, lower, arm, left);
            if (Array.IndexOf(bodies, limb.Parent) < 0) throw new ArgumentException("A limb parent must belong to the same worker body.");
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
            Quaternion rotation = root.rotation;
            for (int i = 0; i < bodies.Length; i++)
            {
                if (bodies[i] == null || !bodies[i].isKinematic) throw new InvalidOperationException("Normal presentation cannot write a dynamic or missing body.");
                bodies[i].position = root.TransformPoint(positions[i]); bodies[i].rotation = rotation * rotations[i];
            }
            foreach (var limb in limbs)
            {
                float wave = Mathf.Sin(phase + (limb.Left ? 0 : Mathf.PI));
                float swing = wave * walking * (limb.Arm ? 16 : -18);
                float bend = limb.Arm ? Mathf.Lerp(6, -15, carrying) : Mathf.Max(0, wave) * walking * 24;
                if (limb.Arm) swing = Mathf.Lerp(swing, -30, carrying);
                limb.Apply(swing, bend);
            }
        }
    }
}
