using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Unity
{
    public enum CarryableKind { Cargo, Shovel, Pickaxe, Cart, Body }
    [DisallowMultipleComponent]
    public sealed class CarryableObject : SceneTarget
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private Rigidbody body;
        [SerializeField] private Transform objectGrip;
        [SerializeField] private Transform assistantObjectGrip;
        [SerializeField] private CarryableKind kind;
        [SerializeField] private WorkerScenePort workerBody;
        [SerializeField] private bool allowAssistance;
        [SerializeField] private float maximumForce = 140;
        [SerializeField] private float bodyMaximumForce = 1800;
        [SerializeField] private float spring = 60, damping = 12, maximumAcceleration = 30, breakDistance = 1.2f;
        private WorkerScenePort holder;
        private WorkerScenePort assistant;
        private long generation;
        private bool hauling, slotted, originalKinematic;
        private Quaternion rotationOffset = Quaternion.identity;
        private readonly CollisionIgnoreScope primaryIgnores = new CollisionIgnoreScope(), assistantIgnores = new CollisionIgnoreScope();
        private Collider[] cargoColliders;
        private Collider[] Shapes => kind == CarryableKind.Body && workerBody != null ? workerBody.PhysicalColliders :
            cargoColliders ?? (cargoColliders = GetComponentsInChildren<Collider>(true));
        private float AttachedMass => kind == CarryableKind.Body && workerBody != null ? workerBody.PhysicalMass : body.mass;
        private float ForceLimit => kind == CarryableKind.Body ? bodyMaximumForce : maximumForce;
        private bool ValidForces => Positive(maximumForce, 10000) && Positive(bodyMaximumForce, 10000) &&
            Positive(spring, 1000) && float.IsFinite(damping) && damping >= 0 && damping <= 1000 &&
            Positive(maximumAcceleration, 100) && Positive(breakDistance, 3);
        private static bool Positive(float value, float maximum) => float.IsFinite(value) && value > 0 && value <= maximum;
        public bool ValidBodyBinding => kind != CarryableKind.Body || workerBody != null && workerBody.PhysicalBody == body && workerBody.PhysicalMass > 0;
        public override Transform Contact => kind == CarryableKind.Body && body != null ? body.transform : base.Contact;
        public Rigidbody Body => body;
        public CarryableKind Kind => kind;
        public WorkerScenePort WorkerBody => workerBody;
        public WorkerScenePort Holder => holder;
        public WorkerScenePort Assistant => assistant;
        public bool AllowAssistance => allowAssistance && (kind == CarryableKind.Cargo || kind == CarryableKind.Body);
        public long Generation => generation;
        public void SynchronizeSlot(Transform slot)
        {
            if (body == null) { slotted = false; return; }
            if (slot != null)
            {
                if (!slotted) originalKinematic = body.isKinematic;
                slotted = true; body.isKinematic = true;
                body.position = slot.position; body.rotation = slot.rotation;
            }
            else if (slotted) { body.isKinematic = originalKinematic; slotted = false; }
        }
        public override bool Supports(SceneOperation value) => value == SceneOperation.Grab || value == SceneOperation.Release ||
            value == SceneOperation.Place || value == SceneOperation.ThrowUnder || value == SceneOperation.ThrowOver ||
            (kind == CarryableKind.Cart && (value == SceneOperation.Push || value == SceneOperation.Pull)) ||
            (kind == CarryableKind.Body && value == SceneOperation.Drag);
        public override bool Apply(WorkerScenePort worker, SceneOperation value, long lease)
        {
            if (body == null || gateway == null || worker == null || lease <= 0 || !Supports(value) ||
                !ValidForces || !ValidBodyBinding || (kind == CarryableKind.Body && !workerBody.Down)) return false;
            if (value == SceneOperation.Grab || value == SceneOperation.Push || value == SceneOperation.Pull || value == SceneOperation.Drag)
            {
                if (holder != null && holder != worker)
                { if (!AllowAssistance || assistant != null || lease != generation) return false; SynchronizeAssistant(worker); return true; }
                if (holder == worker)
                {
                    if (generation != lease) return false;
                    SetPrimaryMode(worker, value); return true;
                }
                ClearBinding(); holder = worker; generation = lease; rotationOffset = Quaternion.identity;
                SetPrimaryMode(worker, value);
                primaryIgnores.Capture(Shapes, worker.BodyColliders);
                body.WakeUp(); return true;
            }
            if (assistant == worker && generation == lease) { SynchronizeAssistant(null); return true; }
            if (holder != worker || generation != lease) return false;
            ClearBinding();
            if (value == SceneOperation.ThrowUnder || value == SceneOperation.ThrowOver)
            {
                float forward = value == SceneOperation.ThrowUnder ? 2.6f : 2.2f;
                float up = value == SceneOperation.ThrowUnder ? 3.2f : 4;
                Vector3 throwVelocity = worker.transform.forward * forward + Vector3.up * up;
                if (kind == CarryableKind.Body) workerBody.ApplyBodyImpulse(throwVelocity * AttachedMass, body.worldCenterOfMass);
                else body.AddForce(throwVelocity, ForceMode.VelocityChange);
            }
            return true;
        }
        private void FixedUpdate()
        {
            if (holder == null) return;
            if (body == null || gateway == null || !gateway.Running || !gateway.CanAct(holder) || !isActiveAndEnabled || !ValidForces || !ValidBodyBinding || body.isKinematic || (workerBody != null && !workerBody.Down))
            { if (gateway != null) gateway.AttachmentFailed(this, generation); else ClearBinding(); return; }
            Vector3 point = objectGrip != null ? objectGrip.position : body.worldCenterOfMass;
            Vector3 target = holder.Grip.position;
            if (Vector3.Distance(target, point) > breakDistance) { gateway.AttachmentFailed(this, generation); return; }
            if (assistant != null)
            {
                Vector3 assistPoint = assistantObjectGrip != null ? assistantObjectGrip.position : point;
                if (!gateway.CanAct(assistant) || Vector3.Distance(assistant.Grip.position, assistPoint) > breakDistance)
                    gateway.AttachmentFailed(this, generation, assistant);
                else
                {
                    ApplyGripForce(assistPoint, assistant.Grip.position, assistant.Velocity, .5f);
                }
            }
            ApplyGripForce(point, target, holder.Velocity, assistant != null ? .5f : 1);
            if (!hauling && kind != CarryableKind.Body)
            {
                Quaternion desired = holder.Grip.rotation * rotationOffset;
                var delta = desired * Quaternion.Inverse(body.rotation);
                delta.ToAngleAxis(out float angle, out Vector3 axis);
                if (angle > 180) angle -= 360;
                body.AddTorque(Vector3.ClampMagnitude(axis * angle * Mathf.Deg2Rad * 10 - body.angularVelocity * 4, 20), ForceMode.Acceleration);
            }
        }
        private void ApplyGripForce(Vector3 point, Vector3 target, Vector3 actorVelocity, float share)
        {
            Vector3 error = target - point, relative = body.GetPointVelocity(point) - actorVelocity;
            if (hauling) { error = Vector3.ProjectOnPlane(error, Vector3.up); relative = Vector3.ProjectOnPlane(relative, Vector3.up); }
            Vector3 force = Vector3.ClampMagnitude(error * spring - relative * damping, maximumAcceleration) * AttachedMass * share;
            if (!hauling && body.useGravity) force -= Physics.gravity * AttachedMass * share;
            body.AddForceAtPosition(Vector3.ClampMagnitude(force, ForceLimit), point, ForceMode.Force);
        }
        private void SetPrimaryMode(WorkerScenePort worker, SceneOperation value)
        {
            hauling = value != SceneOperation.Grab;
            worker.SetHaulPose(hauling ? value : kind == CarryableKind.Shovel ? SceneOperation.Dig :
                kind == CarryableKind.Pickaxe ? SceneOperation.Lever : SceneOperation.Grab);
        }
        public void RotateGrip(float degrees) { rotationOffset *= Quaternion.Euler(0, degrees, 0); }
        public override void ClearBinding()
        {
            SynchronizeAssistant(null);
            if (holder != null)
            {
                holder.SetHaulPose(null);
            }
            primaryIgnores.Restore();
            holder = null; generation = 0;
        }
        public void SynchronizeAssistant(WorkerScenePort worker)
        {
            if (assistant == worker) return;
            if (assistant != null)
            {
                assistant.SetHaulPose(null);
            }
            assistantIgnores.Restore();
            assistant = worker;
            if (assistant != null)
            {
                assistantIgnores.Capture(Shapes, assistant.BodyColliders);
                assistant.SetHaulPose(SceneOperation.Grab);
            }
        }
        private void OnDisable() { if (holder != null && gateway != null) gateway.AttachmentFailed(this, generation); ClearBinding(); }
    }
}
