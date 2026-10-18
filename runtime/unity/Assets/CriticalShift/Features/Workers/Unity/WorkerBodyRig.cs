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
        private Rigidbody pelvis, headBody;
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
        private WorkerKinematicPose normalPose;
        private Vector3 eyePosition;
        private Quaternion recoveryRotation;
        private Guid epoch, actor;
        private bool ragdoll, frozen;
        private readonly RaycastHit[] crawlSupport = new RaycastHit[32];
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
                if (frozen || !isActiveAndEnabled || controller == null || controller.enabled == ragdoll || !controller.detectCollisions ||
                    !UnitScale(controller.transform) || eyes == null || !eyes.gameObject.activeInHierarchy ||
                    !eyes.IsChildOf(controller.transform) || eyes.GetComponentInParent<Rigidbody>() != null ||
                    pelvis == null || head == null || headBody == null || !head.gameObject.activeInHierarchy ||
                    head.GetComponentInParent<Rigidbody>() != headBody || dragPoint == null || dragBody == null ||
                    !dragPoint.gameObject.activeInHierarchy || dragPoint.GetComponentInParent<Rigidbody>() != dragBody || bodies == null ||
                    normalPose == null || !normalPose.HasBoundHierarchy()) return false;
                for (int i = 0; i < bodies.Length; i++)
                    if (bodies[i] == null || colliders[i] == null || !bodies[i].gameObject.activeInHierarchy ||
                        !bodies[i].transform.IsChildOf(controller.transform) || !UnitScale(bodies[i].transform) ||
                        !bodies[i].detectCollisions || bodies[i].isKinematic == ragdoll || colliders[i].enabled != ragdoll ||
                        colliders[i].isTrigger || !colliders[i].gameObject.activeInHierarchy ||
                        !ContactBelongsTo(colliders[i], bodies[i])) return false;
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
            if (!UnitScale(walkingController.transform) || !walkingController.detectCollisions)
                throw new ArgumentException("The fixture worker root must use unit scale and collision detection.");
            if (!eyePivot.gameObject.activeInHierarchy || !eyePivot.IsChildOf(walkingController.transform) ||
                eyePivot.GetComponentInParent<Rigidbody>() != null || !headAnchor.gameObject.activeInHierarchy ||
                !headAnchor.IsChildOf(walkingController.transform))
                throw new ArgumentException("The eyes and head must belong to the explicitly bound worker root.");
            var unique = new HashSet<Rigidbody>();
            for (int i = 0; i < segments.Length; i++)
            {
                var body = segments[i]; var contact = segmentColliders[i];
                string label = "Worker segment " + i + " (" + (body == null ? "missing" : body.name) + ")";
                if (body == null || !unique.Add(body)) throw new ArgumentException(label + " must have a unique Rigidbody.");
                if (!body.gameObject.activeInHierarchy || !body.transform.IsChildOf(walkingController.transform) || !UnitScale(body.transform))
                    throw new ArgumentException(label + " must be an active unit-scale descendant of its worker root.");
                if (!body.detectCollisions) throw new ArgumentException(label + " must retain collision detection.");
                if (contact == null || !contact.gameObject.activeInHierarchy || contact.isTrigger)
                    throw new ArgumentException(label + " needs an active solid contact shape.");
                if (!ContactBelongsTo(contact, body))
                    throw new ArgumentException(label + " contact must belong to that same Rigidbody: " + contact.name);
            }
            if (!unique.Contains(hip)) throw new ArgumentException("The pelvis must belong to the bound body rig.");
            var boundHeadBody = headAnchor.GetComponentInParent<Rigidbody>();
            if (boundHeadBody == null || !unique.Contains(boundHeadBody))
                throw new ArgumentException("The head anchor must belong to a bound physical segment.");
            var gripBody = suitGrip.GetComponentInParent<Rigidbody>();
            if (!suitGrip.gameObject.activeInHierarchy || gripBody == null || !unique.Contains(gripBody))
                throw new ArgumentException("The suit grip must belong to a bound physical segment.");
            epoch = worldEpoch; actor = workerId; controller = walkingController; eyes = eyePivot; pelvis = hip; head = headAnchor;
            headBody = boundHeadBody; dragPoint = suitGrip; dragBody = gripBody;
            gripBodyOffset = dragBody.transform.InverseTransformPoint(suitGrip.position);
            bodies = (Rigidbody[])segments.Clone(); colliders = (Collider[])segmentColliders.Clone();
            restPositions = new Vector3[bodies.Length]; restRotations = new Quaternion[bodies.Length];
            for (int i = 0; i < bodies.Length; i++)
            {
                restPositions[i] = controller.transform.InverseTransformPoint(bodies[i].position);
                restRotations[i] = Quaternion.Inverse(controller.transform.rotation) * bodies[i].rotation;
                TotalPhysicalMass += bodies[i].mass;
            }
            eyePosition = eyes.localPosition; recoveryRotation = controller.transform.rotation;
            SetSimulation(false);
            normalPose = new WorkerKinematicPose(controller.transform, bodies, restPositions, restRotations);
        }

        public void BindNormalLimb(Rigidbody upper, Rigidbody lower, bool arm, bool left)
        {
            if (normalPose == null || frozen) throw new InvalidOperationException("Initialize the live body rig before binding its visual limbs.");
            normalPose.BindLimb(upper, lower, arm, left);
        }
        public void BindNormalHands(Func<bool> busy)
        {
            if (normalPose == null || frozen) throw new InvalidOperationException("Initialize the live body rig before binding its hands query.");
            normalPose.BindHands(busy);
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
            if (!Available) throw new InvalidOperationException("An active worker lost its physical rig binding, contact geometry or anchors.");
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
                Physics.SyncTransforms();
                for (int i = 0; i < colliders.Length; i++)
                    if (!ContactBelongsTo(colliders[i], bodies[i]))
                        throw new InvalidOperationException("An enabled ragdoll contact lost its native Rigidbody owner: " + bodies[i].name);
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

        internal bool Crawl(Vector2 movement)
        {
            if (!ragdoll || !Available || movement.sqrMagnitude < 0.0001f) return false;
            int count = Physics.RaycastNonAlloc(pelvis.position + Vector3.up * 0.05f, Vector3.down, crawlSupport,
                0.8f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            if (count == crawlSupport.Length) throw new InvalidOperationException("Crawl support observation bounds were saturated.");
            bool supported = false; RaycastHit nearest = default;
            for (int i = 0; i < count; i++)
            {
                var hit = crawlSupport[i];
                if (Owns(hit.collider)) continue;
                if (!supported || hit.distance < nearest.distance) { nearest = hit; supported = true; }
            }
            if (!supported || Vector3.Dot(nearest.normal, Vector3.up) < 0.5f) return false;
            Vector3 forward = Vector3.ProjectOnPlane(eyes.forward, Vector3.up).normalized;
            Vector3 motion = Vector3.Cross(Vector3.up, forward) * movement.x + forward * movement.y;
            Vector3 supportVelocity = nearest.rigidbody == null ? Vector3.zero : nearest.rigidbody.GetPointVelocity(nearest.point);
            Vector3 desired = Vector3.ProjectOnPlane(supportVelocity, Vector3.up) + Vector3.ClampMagnitude(motion, 1) * 0.65f;
            Vector3 current = Vector3.ProjectOnPlane(pelvis.linearVelocity, Vector3.up);
            pelvis.AddForce(Vector3.ClampMagnitude((desired - current) * TotalPhysicalMass * 8, 220), ForceMode.Force);
            return true;
        }

        internal bool Owns(Collider collider)
        {
            if (collider == controller) return true;
            if (colliders != null) foreach (var own in colliders) if (own == collider) return true;
            return false;
        }

        internal bool HasSettledRecoveryMotion()
        {
            foreach (var body in bodies)
            {
                Vector3 linear = body.linearVelocity, angular = body.angularVelocity;
                if (!Finite(linear) || !Finite(angular))
                    throw new InvalidOperationException("A worker recovery body has non-finite motion: " + body.name);
                if (linear.sqrMagnitude > 1.25f * 1.25f || angular.sqrMagnitude > 3 * 3) return false;
            }
            return true;
        }

        internal void StandAt(Vector3 position, Quaternion rotation)
        {
            if (!ragdoll || !Available || !Finite(position)) throw new InvalidOperationException("No active ragdoll can accept this recovery pose.");
            Quaternion look = eyes.rotation;
            SetSimulation(false);
            ReleaseBodyClaim();
            controller.transform.SetPositionAndRotation(position, rotation);
            normalPose.RestoreRestPose(); // Native pose first, then top-down publication while contacts remain disabled.
            eyes.localPosition = eyePosition; eyes.rotation = look;
            Physics.SyncTransforms();
            ragdoll = false; controller.enabled = true; // Dynamic motion has already ended.
            normalPose.Reset();
        }

        public void UpdatePresentation()
        {
            if (!Available) return;
            if (ragdoll)
            {
                // Keep the existing look heading; a tumbling skull must not spin the first-person camera.
                eyes.position = head.position;
            }
            else normalPose.Update(Time.deltaTime);
        }

        public void Freeze()
        {
            if (frozen) return;
            frozen = true; SetSimulation(false); ReleaseBodyClaim(); ragdoll = false;
            Array.Clear(crawlSupport, 0, crawlSupport.Length);
            if (controller != null) controller.enabled = false;
        }

        private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z);
        private static bool UnitScale(Transform value) => (value.lossyScale - Vector3.one).sqrMagnitude <= 0.0001f;
        // Disabled normal-mode shapes still need the exact hierarchy owner; enabled shapes also need native attachment.
        private static bool ContactBelongsTo(Collider contact, Rigidbody body) =>
            contact.GetComponentInParent<Rigidbody>() == body && (!contact.enabled || contact.attachedRigidbody == body);
        private void OnDisable() => Freeze();
        private void OnDestroy() => Freeze();
    }
}
