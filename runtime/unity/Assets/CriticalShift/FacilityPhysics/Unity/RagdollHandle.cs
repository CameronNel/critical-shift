using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Unity
{
    // Bounded compliant hand constraint. Custody and lifetime remain the host's claim/lease.
    [DisallowMultipleComponent]
    public sealed class RagdollHandle : SceneTarget
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private float maximumForce = 1000, spring = 500, damping = 90, breakDistance = 1.2f;
        private Rigidbody hand;
        public WorkerScenePort Holder { get; private set; }
        public long Generation { get; private set; }
        public override bool Supports(SceneOperation value) => value == SceneOperation.Grab || value == SceneOperation.Release;
        public bool CanGrip(WorkerScenePort worker)
        {
            var body = worker != null ? worker.GripBody(Contact.position) : null;
            return body != null && !body.isKinematic && Vector3.Distance(body.position, Contact.position) <= breakDistance &&
                float.IsFinite(maximumForce) && maximumForce > 0 && maximumForce <= 1500 &&
                float.IsFinite(spring) && spring > 0 && spring <= 1000 && float.IsFinite(damping) && damping >= 0 && damping <= 200 &&
                float.IsFinite(breakDistance) && breakDistance > 0 && breakDistance <= 1.5f;
        }
        public override bool Apply(WorkerScenePort worker, SceneOperation value, long generation)
        {
            if (value == SceneOperation.Release)
            { if (Holder != worker || Generation != generation) return false; ClearBinding(); return true; }
            if (value != SceneOperation.Grab || generation <= 0 || Holder != null || !CanGrip(worker)) return false;
            Holder = worker; Generation = generation; hand = worker.GripBody(Contact.position); return true;
        }
        private void FixedUpdate()
        {
            if (Holder == null) return;
            if (gateway == null || !gateway.Running || !gateway.ConsciousDown(Holder) || hand == null || hand.isKinematic ||
                Vector3.Distance(hand.position, Contact.position) > breakDistance)
            { if (gateway != null) gateway.AttachmentFailed(this, Generation); ClearBinding(); return; }
            var anchorBody = Contact.GetComponentInParent<Rigidbody>();
            Vector3 anchorVelocity = anchorBody != null ? anchorBody.GetPointVelocity(Contact.position) : Vector3.zero;
            Vector3 force = Vector3.ClampMagnitude((Contact.position - hand.worldCenterOfMass) * spring -
                (hand.linearVelocity - anchorVelocity) * damping, maximumForce);
            hand.AddForce(force, ForceMode.Force);
            if (anchorBody != null && !anchorBody.isKinematic && anchorBody != hand) anchorBody.AddForceAtPosition(-force, Contact.position, ForceMode.Force);
        }
        public override void ClearBinding() { Holder = null; Generation = 0; hand = null; }
        private void OnDisable() { if (Holder != null && gateway != null) gateway.AttachmentFailed(this, Generation); ClearBinding(); }
    }
}
