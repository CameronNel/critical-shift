using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>One physical handoff between a walking capsule and an explicitly bound fixture ragdoll.</summary>
    [DisallowMultipleComponent]
    public sealed class WorkerBodyRig : MonoBehaviour
    {
        private CharacterController controller;
        private Transform eyes, head;
        private Rigidbody pelvis;
        private Transform dragPoint;
        private Rigidbody dragBody;
        private Vector3 gripBodyOffset;
        private Guid bodyEntity;
        private long dragGeneration;
        private long lastPhysicalLease;
        private long hoistGeneration;
        private bool hoist;
        private float dragObstruction;
        private Rigidbody[] bodies;
        private Collider[] colliders;
        private Vector3[] restPositions;
        private Quaternion[] restRotations;
        private Vector3 eyePosition;
        private Quaternion eyeRotation, recoveryRotation;
        private Guid epoch, actor;
        private bool ragdoll, frozen;
        public bool IsRagdoll => ragdoll;
        public int BodyCount => bodies == null ? 0 : bodies.Length;
        public float TotalPhysicalMass { get; private set; }
        public Transform SuitGrip => dragPoint;
        public Rigidbody[] CopyBodySegments() => bodies == null ? Array.Empty<Rigidbody>() : (Rigidbody[])bodies.Clone();
        internal Guid Epoch => epoch;
        internal Guid Actor => actor;
        internal CharacterController Controller => controller;
        internal Rigidbody Pelvis => pelvis;
        internal Quaternion StandingRotation => recoveryRotation;
        internal bool Available
        {
            get
            {
                if (frozen || !isActiveAndEnabled || controller == null || eyes == null || pelvis == null || head == null ||
                    dragPoint == null || dragBody == null || bodies == null) return false;
                for (int i = 0; i < bodies.Length; i++)
                    if (bodies[i] == null || colliders[i] == null || !bodies[i].gameObject.activeInHierarchy ||
                        bodies[i].isKinematic == ragdoll || colliders[i].enabled != ragdoll) return false;
                return true;
            }
        }

        public void Initialize(Guid worldEpoch, Guid workerId, CharacterController walkingController,
            Transform eyePivot, Rigidbody hip, Transform headAnchor, Transform suitGrip, Rigidbody[] segments, Collider[] segmentColliders)
        {
            if (bodies != null || worldEpoch == Guid.Empty || workerId == Guid.Empty || walkingController == null ||
                eyePivot == null || hip == null || headAnchor == null || suitGrip == null || segments == null || segments.Length < 2 ||
                segments.Length > 16 || segmentColliders == null || segmentColliders.Length != segments.Length)
                throw new ArgumentException("Bind one bounded body rig, worker identity and walking controller.");
            if ((walkingController.transform.lossyScale - Vector3.one).sqrMagnitude > 0.0001f)
                throw new ArgumentException("The fixture worker root must use unit scale.");
            if (!eyePivot.IsChildOf(walkingController.transform) || !headAnchor.IsChildOf(walkingController.transform))
                throw new ArgumentException("The eyes and head must belong to the explicitly bound worker root.");
            var unique = new HashSet<Rigidbody>();
            for (int i = 0; i < segments.Length; i++)
                if (segments[i] == null || !unique.Add(segments[i]) || !segments[i].transform.IsChildOf(walkingController.transform) ||
                    segmentColliders[i] == null || segmentColliders[i].attachedRigidbody != segments[i] || segmentColliders[i].isTrigger)
                    throw new ArgumentException("Each body segment needs its own solid collider beneath the worker root.");
            if (!unique.Contains(hip)) throw new ArgumentException("The pelvis must belong to the bound body rig.");
            var gripBody = suitGrip.GetComponentInParent<Rigidbody>();
            if (gripBody == null || !unique.Contains(gripBody)) throw new ArgumentException("The suit grip must belong to a bound physical segment.");
            epoch = worldEpoch; actor = workerId; controller = walkingController; eyes = eyePivot; pelvis = hip; head = headAnchor;
            dragPoint = suitGrip; dragBody = gripBody;
            gripBodyOffset = dragBody.transform.InverseTransformPoint(suitGrip.position);
            bodies = (Rigidbody[])segments.Clone(); colliders = (Collider[])segmentColliders.Clone();
            restPositions = new Vector3[bodies.Length]; restRotations = new Quaternion[bodies.Length];
            for (int i = 0; i < bodies.Length; i++)
            {
                restPositions[i] = controller.transform.InverseTransformPoint(bodies[i].position);
                restRotations[i] = Quaternion.Inverse(controller.transform.rotation) * bodies[i].rotation;
                TotalPhysicalMass += bodies[i].mass;
            }
            eyePosition = eyes.localPosition; eyeRotation = eyes.localRotation; recoveryRotation = controller.transform.rotation;
            SetSimulation(false);
        }

        public void BindDragEntity(Guid entity)
        {
            if (bodies == null || ragdoll || frozen || entity == Guid.Empty || bodyEntity != Guid.Empty)
                throw new InvalidOperationException("Bind one logical body identity during physical composition.");
            bodyEntity = entity;
        }

        public void Reconcile(WorkerView worker, WorldPhase phase)
        {
            if (worker == null || worker.Epoch != epoch || worker.Id != actor)
                throw new InvalidOperationException("A body rig cannot reconcile another worker or epoch.");
            if (phase != WorldPhase.Running && phase != WorldPhase.Paused) { Freeze(); return; }
            if (!Available) throw new InvalidOperationException("An active worker lost its physical rig binding.");
            if (worker.Pose != WorkerPose.Upright)
            {
                if (!ragdoll) EnterRagdoll();
            }
            else if (ragdoll)
                throw new InvalidOperationException("Standing requires the approved recovery-placement handoff.");
        }

        private void EnterRagdoll()
        {
            Vector3 inherited = Vector3.ClampMagnitude(controller.velocity, 5);
            recoveryRotation = Quaternion.Euler(0, controller.transform.eulerAngles.y, 0);
            eyeRotation = eyes.localRotation;
            controller.enabled = false; // Stop locomotion before any dynamic body becomes active.
            Physics.SyncTransforms();
            SetSimulation(true); ragdoll = true;
            foreach (var body in bodies) { body.linearVelocity = inherited; body.angularVelocity = Vector3.zero; }
        }

        private void SetSimulation(bool dynamic)
        {
            if (bodies == null) return;
            // Disable contacts before restoring kinematic poses; enable them only after the walking capsule is off.
            if (!dynamic) foreach (var collider in colliders) if (collider != null) collider.enabled = false;
            foreach (var body in bodies)
            {
                if (body == null) continue;
                if (!body.isKinematic) { body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; }
                if (!dynamic) body.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
                body.isKinematic = !dynamic; body.useGravity = dynamic;
                if (dynamic) body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
                body.interpolation = dynamic ? RigidbodyInterpolation.Interpolate : RigidbodyInterpolation.None;
            }
            if (dynamic)
            {
                foreach (var collider in colliders) collider.enabled = true;
                for (int i = 0; i < colliders.Length; i++)
                    for (int j = i + 1; j < colliders.Length; j++) Physics.IgnoreCollision(colliders[i], colliders[j]);
            }
        }

        public void ApplyImpactImpulse(Vector3 impulse, Vector3 point)
        {
            if (!ragdoll || !Available || !Finite(impulse) || !Finite(point))
                throw new InvalidOperationException("Impact forces require the current active ragdoll and finite observations.");
            pelvis.AddForceAtPosition(Vector3.ClampMagnitude(impulse, 80), point, ForceMode.Impulse);
        }

        public bool PullBodyClaim(ObjectClaimView claim, Vector3 target, float seconds)
        {
            if (!ragdoll || !Available || dragPoint == null || dragBody == null || claim == null || claim.Epoch != epoch ||
                claim.EntityId != bodyEntity || !claim.HolderId.HasValue || claim.LeaseGeneration < 1 ||
                claim.LeaseGeneration < lastPhysicalLease ||
                !Finite(target) || seconds <= 0 || float.IsNaN(seconds) || float.IsInfinity(seconds)) return false;
            lastPhysicalLease = claim.LeaseGeneration;
            if (dragGeneration != claim.LeaseGeneration) { dragGeneration = claim.LeaseGeneration; dragObstruction = 0; }
            Vector3 point = dragBody.position + dragBody.rotation * gripBodyOffset;
            Vector3 error = target - point;
            dragObstruction = error.magnitude > 1.2f ? dragObstruction + Mathf.Min(seconds, 0.05f) : 0;
            if (error.sqrMagnitude > 3 * 3 || dragObstruction > 1.25f) return false;
            bool lifting = hoist && hoistGeneration == claim.LeaseGeneration;
            Vector3 force = error * 320 - dragBody.GetPointVelocity(point) * (lifting ? 160 : 80);
            float budget = 250;
            if (lifting)
            {
                force -= Physics.gravity * TotalPhysicalMass;
                budget = Mathf.Min(1100, Physics.gravity.magnitude * TotalPhysicalMass + 250);
            }
            dragBody.AddForceAtPosition(Vector3.ClampMagnitude(force, budget), point, ForceMode.Force);
            return true;
        }

        public void SetBodyHoist(ObjectClaimView claim, bool raised)
        {
            if (!ragdoll || !Available || claim == null || claim.Epoch != epoch || claim.EntityId != bodyEntity ||
                !claim.HolderId.HasValue || claim.LeaseGeneration < 1 || claim.LeaseGeneration < lastPhysicalLease) return;
            lastPhysicalLease = claim.LeaseGeneration;
            hoist = raised; hoistGeneration = raised ? claim.LeaseGeneration : 0;
        }

        public void ReleaseBodyClaim() { dragGeneration = 0; dragObstruction = 0; hoist = false; hoistGeneration = 0; }

        internal bool Owns(Collider collider)
        {
            if (collider == controller) return true;
            if (colliders != null) foreach (var own in colliders) if (own == collider) return true;
            return false;
        }

        internal void StandAt(Vector3 position, Quaternion rotation)
        {
            if (!ragdoll || !Available || !Finite(position)) throw new InvalidOperationException("No active ragdoll can accept this recovery pose.");
            SetSimulation(false);
            ReleaseBodyClaim();
            controller.transform.SetPositionAndRotation(position, rotation);
            for (int i = 0; i < bodies.Length; i++)
            {
                bodies[i].position = controller.transform.TransformPoint(restPositions[i]);
                bodies[i].rotation = rotation * restRotations[i];
            }
            eyes.localPosition = eyePosition; eyes.localRotation = eyeRotation;
            ragdoll = false; controller.enabled = true; // Dynamic motion has already ended.
        }

        public void UpdateCamera()
        {
            if (!ragdoll || !Available || head == null) return;
            // Keep the existing look heading; a tumbling skull must not spin the first-person camera.
            eyes.position = head.position;
        }

        public void Freeze()
        {
            if (frozen) return;
            frozen = true; SetSimulation(false); ReleaseBodyClaim(); ragdoll = false;
            if (controller != null) controller.enabled = false;
        }

        private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z);
        private void OnDisable() => Freeze();
        private void OnDestroy() => Freeze();
    }
}
