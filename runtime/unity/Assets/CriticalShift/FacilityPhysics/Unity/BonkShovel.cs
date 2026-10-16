using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Unity
{
    [RequireComponent(typeof(CarryableObject)), DisallowMultipleComponent, DefaultExecutionOrder(100)]
    public sealed class BonkShovel : MonoBehaviour
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private CarryableObject carry;
        [SerializeField] private AudioSource impactAudio;
        [SerializeField] private AudioClip bonkSound;
        private WorkerScenePort actor;
        private Rigidbody body;
        private CollisionDetectionMode originalDetection;
        private RigidbodyInterpolation originalInterpolation;
        private Quaternion bodyInGrip;
        private Vector3 positionInGrip, initialPosition;
        private Quaternion initialRotation;
        private float contactPhase = -1;
        public bool Animating => actor != null;
        public float LastStrike { get; set; }
        public Quaternion Aim { get; private set; }
        public bool Ready => isActiveAndEnabled && carry != null && carry.Kind == CarryableKind.Shovel && carry.Body != null &&
            carry.Body.transform == transform && impactAudio != null && impactAudio.transform != transform && impactAudio.transform.IsChildOf(transform) && bonkSound != null;
        public bool BeginMotion(WorkerScenePort worker)
        {
            if (!Ready || carry.Holder != worker || carry.Body.isKinematic || Animating) return false;
            actor = worker; body = carry.Body; Aim = worker.Eye.rotation; LastStrike = 0;
            initialPosition = worker.Grip.InverseTransformPoint(body.position); initialRotation = Quaternion.Inverse(worker.Grip.rotation) * body.rotation;
            carry.GetHoldPose(out var heldPosition, out var heldRotation);
            positionInGrip = worker.Grip.InverseTransformPoint(heldPosition); bodyInGrip = Quaternion.Inverse(worker.Grip.rotation) * heldRotation; contactPhase = -1;
            originalDetection = body.collisionDetectionMode; originalInterpolation = body.interpolation;
            body.linearVelocity = body.angularVelocity = Vector3.zero;
            body.collisionDetectionMode = CollisionDetectionMode.Discrete; body.isKinematic = true; body.interpolation = RigidbodyInterpolation.None;
            return true;
        }
        private void LateUpdate()
        {
            if (!Animating) { if (body != null) EndMotion(); return; }
            if (body == null || carry == null || !body.isKinematic || gateway == null || !gateway.Running || !gateway.CanAct(actor) || carry.Holder != actor || gateway.BonkPhase(actor) < 0)
            { if (gateway != null) gateway.CancelBonk(actor); EndMotion(); return; }
            // Owns the tool's pose only for this accepted swing; ordinary carry forces are suspended.
            float blend = Mathf.SmoothStep(0, 1, gateway.BonkPhase(actor) / .22f);
            body.position = actor.Grip.TransformPoint(Vector3.Lerp(initialPosition, positionInGrip, blend));
            body.rotation = actor.Grip.rotation * Quaternion.Slerp(initialRotation, bodyInGrip, blend);
        }
        public BonkSwingPose Pose(float phase) => contactPhase < 0 ? BonkSwingPose.Sample(phase) : BonkSwingPose.Recover(contactPhase, phase);
        public void PlayImpact(Vector3 position)
        {
            if (actor != null && gateway != null) contactPhase = gateway.BonkPhase(actor);
            if (impactAudio == null || bonkSound == null) return;
            impactAudio.transform.position = position; impactAudio.pitch = 1;
            impactAudio.PlayOneShot(bonkSound, .8f);
        }
        public void EndMotion()
        {
            if (body != null)
            {
                body.isKinematic = false; body.collisionDetectionMode = originalDetection; body.interpolation = originalInterpolation;
                body.linearVelocity = actor != null ? Vector3.ClampMagnitude(actor.Velocity, 6) : Vector3.zero; body.angularVelocity = Vector3.zero;
            }
            actor = null; body = null; LastStrike = 0;
        }
        private void OnDisable() { if (Animating && gateway != null) gateway.CancelBonk(actor); EndMotion(); }
    }
}
