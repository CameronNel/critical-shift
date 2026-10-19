using System;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    public sealed partial class WorkerBodyRig
    {
        private bool medicalPlacementBound;
        internal void BindMedicalPlacement()
        {
            if (medicalPlacementBound || frozen || bodyEntity == Guid.Empty)
                throw new InvalidOperationException("Each live worker rig has one medical placement binding for its lifetime.");
            medicalPlacementBound = true;
        }

        internal Collider[] CopyMedicalContacts() => colliders == null ? Array.Empty<Collider>() : (Collider[])colliders.Clone();

        internal void BuildMedicalPose(Vector3 anchor, Quaternion frame, Vector3[] positions, Quaternion[] rotations)
        {
            if (!Available || !ragdoll || bodyEntity == Guid.Empty || !Finite(anchor) || !ValidMedicalRotation(frame) ||
                positions == null || rotations == null || positions.Length != bodies.Length || rotations.Length != bodies.Length)
                throw new InvalidOperationException("Medical placement requires the bound down worker and finite complete pose.");
            int hip = Array.IndexOf(bodies, pelvis);
            if (hip < 0) throw new InvalidOperationException("Medical placement lost its pelvis binding.");
            for (int i = 0; i < bodies.Length; i++)
            {
                // One rigid transform of the stored joint-consistent rest pose; the controller root never moves.
                positions[i] = anchor + frame * (restPositions[i] - restPositions[hip]);
                rotations[i] = frame * restRotations[i];
                if (!Finite(positions[i]) || !ValidMedicalRotation(rotations[i]))
                    throw new InvalidOperationException("Medical placement produced a non-finite or invalid segment pose.");
            }
        }

        internal void ApplyMedicalPose(bool entering, Vector3[] positions, Quaternion[] rotations)
        {
            if (!Available || (entering ? !IsFreeRagdoll : !chambered))
                throw new InvalidOperationException("The medical handoff lost its exact physical mode.");
            // Stop all dynamics before any native pose setter, including for a previously held body.
            SetSimulation(false); ReleaseBodyClaim();
            normalPose.PublishPreparedPose(positions, rotations);
            chambered = entering;
            if (!entering)
            {
                SetSimulation(true);
                foreach (var body in bodies)
                { body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; body.WakeUp(); }
            }
            eyes.position = head.position; // Preserve look heading while the camera follows the actual physical head.
        }

        internal bool MatchesMedicalPose(Vector3[] positions, Quaternion[] rotations)
        {
            if (!chambered || !Available || positions == null || rotations == null || positions.Length != bodies.Length || rotations.Length != bodies.Length)
                return false;
            for (int i = 0; i < bodies.Length; i++)
                if (!Finite(bodies[i].position) || !ValidMedicalRotation(bodies[i].rotation) ||
                    !Finite(bodies[i].linearVelocity) || !Finite(bodies[i].angularVelocity) ||
                    (bodies[i].position - positions[i]).sqrMagnitude > 0.000004f ||
                    Mathf.Abs(Quaternion.Dot(bodies[i].rotation, rotations[i])) < 0.999999f) return false;
            return true;
        }

        internal static bool ValidMedicalVector(Vector3 value) => Finite(value);
        internal static bool ValidMedicalRotation(Quaternion value)
        {
            if (float.IsNaN(value.x) || float.IsNaN(value.y) || float.IsNaN(value.z) || float.IsNaN(value.w) ||
                float.IsInfinity(value.x) || float.IsInfinity(value.y) || float.IsInfinity(value.z) || float.IsInfinity(value.w)) return false;
            float square = value.x * value.x + value.y * value.y + value.z * value.z + value.w * value.w;
            return Mathf.Abs(square - 1) <= 0.001f;
        }
    }
}
