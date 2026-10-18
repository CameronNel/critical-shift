using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Read-only recovery clearance for one explicitly bound worker and staged attempt.</summary>
    public sealed class WorkerRecoveryPlacement : IWorkerRecoveryPolicy
    {
        private WorkerBodyRig rig;
        private readonly RaycastHit[] groundHits = new RaycastHit[32];
        private readonly Collider[] overlaps = new Collider[32];
        private Vector3 proposedPosition, stagedPosition;
        private Quaternion proposedRotation, stagedRotation;
        private Collider proposedGround, stagedGround;
        private long stagedAttempt;
        private bool prepared;

        public void Bind(WorkerBodyRig body)
        {
            if (rig != null || body == null || body.Epoch == Guid.Empty) throw new InvalidOperationException("Bind one initialized worker rig.");
            rig = body;
        }

        internal RecoveryClearance Prepare()
        {
            prepared = false;
            if (rig == null || !rig.Available || !rig.IsRagdoll) return RecoveryClearance.Unavailable;
            Physics.SyncTransforms();
            // Search immediately below the body; an overhead shelf or ceiling is not a recovery floor.
            Vector3 origin = rig.Pelvis.position + Vector3.up * 0.15f;
            var ground = FindGround(origin, 1.4f, out var hit);
            if (ground != RecoveryClearance.Safe) return ground;
            if (hit.point.y > rig.Pelvis.position.y + 0.02f) return RecoveryClearance.Blocked;
            proposedRotation = rig.StandingRotation; proposedGround = hit.collider;
            proposedPosition = hit.point + Vector3.up * SupportOffset(hit.normal, proposedRotation);
            var clearance = Check(proposedPosition, proposedRotation, proposedGround);
            prepared = clearance == RecoveryClearance.Safe; return clearance;
        }

        internal void Stage(Guid epoch, Guid worker, long attempt)
        {
            if (!prepared || rig == null || epoch != rig.Epoch || worker != rig.Actor || attempt < 1)
                throw new InvalidOperationException("Stage only a prepared pose for the current worker recovery attempt.");
            stagedPosition = proposedPosition; stagedRotation = proposedRotation; stagedGround = proposedGround;
            stagedAttempt = attempt; prepared = false;
        }

        public RecoveryClearance Evaluate(Guid epoch, Guid workerId, long recoveryAttempt)
        {
            if (rig == null || !rig.Available || !rig.IsRagdoll || epoch != rig.Epoch || workerId != rig.Actor ||
                recoveryAttempt < 1 || recoveryAttempt != stagedAttempt) return RecoveryClearance.Unavailable;
            return Check(stagedPosition, stagedRotation, stagedGround);
        }

        private RecoveryClearance FindGround(Vector3 origin, float distance, out RaycastHit nearest)
        {
            nearest = default;
            int count = Physics.RaycastNonAlloc(origin, Vector3.down, groundHits, distance,
                Physics.AllLayers, QueryTriggerInteraction.Ignore);
            if (count == groundHits.Length) return RecoveryClearance.Unavailable;
            bool found = false;
            for (int i = 0; i < count; i++)
            {
                var hit = groundHits[i];
                if (!BlocksController(hit.collider)) continue;
                if (!found || hit.distance < nearest.distance) { nearest = hit; found = true; }
            }
            if (!found || nearest.rigidbody != null || Vector3.Angle(nearest.normal, Vector3.up) > rig.Controller.slopeLimit)
                return RecoveryClearance.Blocked;
            return RecoveryClearance.Safe;
        }

        private bool BlocksController(Collider contact) => contact != null && !rig.Owns(contact) &&
            !Physics.GetIgnoreLayerCollision(rig.Controller.gameObject.layer, contact.gameObject.layer) &&
            !Physics.GetIgnoreCollision(rig.Controller, contact);

        private float SupportOffset(Vector3 normal, Quaternion rotation)
        {
            var capsule = rig.Controller;
            float extent = Mathf.Max(0, capsule.height * 0.5f - capsule.radius);
            // Lift the expanded lower sphere above the actual support plane. A
            // fixed vertical skin offset intersects otherwise walkable slopes.
            float lowerCenter = Vector3.Dot(rotation * capsule.center - Vector3.up * extent, normal);
            return (capsule.radius + capsule.skinWidth + 0.02f - lowerCenter) / normal.y;
        }

        private RecoveryClearance Check(Vector3 position, Quaternion rotation, Collider support)
        {
            if (support == null || !support.enabled || !support.gameObject.activeInHierarchy) return RecoveryClearance.Unavailable;
            float bodyHeight = rig.Pelvis.position.y - position.y;
            if (!rig.HasSettledRecoveryMotion() ||
                Vector3.ProjectOnPlane(rig.Pelvis.position - position, Vector3.up).magnitude > 0.8f || bodyHeight < -0.05f || bodyHeight > 1.25f)
                return RecoveryClearance.Blocked;
            var ground = FindGround(position + Vector3.up * 0.3f, 1.4f, out var hit);
            if (ground != RecoveryClearance.Safe) return ground;
            if (hit.collider != support || Mathf.Abs(hit.point.y + SupportOffset(hit.normal, rotation) - position.y) > 0.08f)
                return RecoveryClearance.Blocked;
            var capsule = rig.Controller;
            Vector3 center = position + rotation * capsule.center;
            float extent = Mathf.Max(0, capsule.height * 0.5f - capsule.radius);
            int count = Physics.OverlapCapsuleNonAlloc(center + Vector3.up * extent, center - Vector3.up * extent,
                capsule.radius + capsule.skinWidth, overlaps, Physics.AllLayers, QueryTriggerInteraction.Ignore);
            if (count == overlaps.Length) return RecoveryClearance.Unavailable;
            for (int i = 0; i < count; i++) if (BlocksController(overlaps[i])) return RecoveryClearance.Blocked;
            return RecoveryClearance.Safe;
        }

        internal void ApplyAccepted(Guid epoch, Guid worker, long attempt)
        {
            if (rig == null || epoch != rig.Epoch || worker != rig.Actor || attempt != stagedAttempt || attempt < 1)
                throw new InvalidOperationException("An accepted recovery lost its exact staged pose.");
            rig.StandAt(stagedPosition, stagedRotation); stagedAttempt = 0; stagedGround = null;
        }

        internal void CancelStage() { stagedAttempt = 0; stagedGround = null; prepared = false; }
        public void Clear() { CancelStage(); rig = null; }
    }
}
