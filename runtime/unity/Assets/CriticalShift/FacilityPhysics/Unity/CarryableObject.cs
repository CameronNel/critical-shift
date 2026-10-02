using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Unity
{
    public enum CarryableKind { Cargo, Shovel, Pickaxe, Cart, Body }
    [RequireComponent(typeof(Rigidbody)), DisallowMultipleComponent]
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
        [SerializeField] private float spring = 60, damping = 12, maximumAcceleration = 30, breakDistance = 1.2f;
        private WorkerScenePort holder;
        private WorkerScenePort assistant;
        private long generation;
        private bool hauling, slotted, originalKinematic;
        private Quaternion rotationOffset = Quaternion.identity;
        public Rigidbody Body => body;
        public CarryableKind Kind => kind;
        public WorkerScenePort WorkerBody => workerBody;
        public WorkerScenePort Holder => holder;
        public WorkerScenePort Assistant => assistant;
        public bool AllowAssistance => allowAssistance && (kind == CarryableKind.Cargo || kind == CarryableKind.Body);
        public long Generation => generation;
        public void SynchronizeSlot(Transform slot)
        {
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
                (kind == CarryableKind.Body && (workerBody == null || !workerBody.Down))) return false;
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
                foreach (var own in GetComponentsInChildren<Collider>()) foreach (var other in worker.BodyColliders)
                    if (own != other) Physics.IgnoreCollision(own, other, true);
                body.WakeUp(); return true;
            }
            if (assistant == worker && generation == lease) { SynchronizeAssistant(null); return true; }
            if (holder != worker || generation != lease) return false;
            ClearBinding();
            if (value == SceneOperation.ThrowUnder || value == SceneOperation.ThrowOver)
            {
                float forward = value == SceneOperation.ThrowUnder ? 2.6f : 2.2f;
                float up = value == SceneOperation.ThrowUnder ? 3.2f : 4;
                body.AddForce(worker.transform.forward * forward + Vector3.up * up, ForceMode.VelocityChange);
            }
            return true;
        }
        private void FixedUpdate()
        {
            if (holder == null) return;
            if (!gateway.Running || !gateway.CanAct(holder) || !isActiveAndEnabled || (workerBody != null && !workerBody.Down))
            { gateway.AttachmentFailed(this, generation); return; }
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
                    Vector3 assistForce = (assistant.Grip.position - assistPoint) * spring - (body.GetPointVelocity(assistPoint) - assistant.Velocity) * damping;
                    body.AddForceAtPosition(Vector3.ClampMagnitude(Vector3.ClampMagnitude(assistForce, maximumAcceleration) * body.mass, maximumForce), assistPoint, ForceMode.Force);
                }
            }
            Vector3 error = target - point;
            if (hauling) error.y = 0;
            Vector3 force = Vector3.ClampMagnitude(error * spring - (body.GetPointVelocity(point) - holder.Velocity) * damping, maximumAcceleration);
            body.AddForceAtPosition(Vector3.ClampMagnitude(force * body.mass, maximumForce), point, ForceMode.Force);
            if (!hauling)
            {
                Quaternion desired = holder.Grip.rotation * rotationOffset;
                var delta = desired * Quaternion.Inverse(body.rotation);
                delta.ToAngleAxis(out float angle, out Vector3 axis);
                if (angle > 180) angle -= 360;
                body.AddTorque(Vector3.ClampMagnitude(axis * angle * Mathf.Deg2Rad * 10 - body.angularVelocity * 4, 20), ForceMode.Acceleration);
            }
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
                foreach (var own in GetComponentsInChildren<Collider>()) foreach (var other in holder.BodyColliders)
                    if (own != other && own != null && other != null) Physics.IgnoreCollision(own, other, false);
                holder.SetHaulPose(null);
            }
            holder = null; generation = 0;
        }
        public void SynchronizeAssistant(WorkerScenePort worker)
        {
            if (assistant == worker) return;
            if (assistant != null)
            {
                foreach (var own in GetComponentsInChildren<Collider>()) foreach (var other in assistant.BodyColliders)
                    if (own != other && own != null && other != null) Physics.IgnoreCollision(own, other, false);
                assistant.SetHaulPose(null);
            }
            assistant = worker;
            if (assistant != null)
            {
                foreach (var own in GetComponentsInChildren<Collider>()) foreach (var other in assistant.BodyColliders)
                    if (own != other) Physics.IgnoreCollision(own, other, true);
                assistant.SetHaulPose(SceneOperation.Grab);
            }
        }
        private void OnDisable() { if (holder != null && gateway != null) gateway.AttachmentFailed(this, generation); ClearBinding(); }
    }
}
