using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    public sealed partial class WorkerController
    {
        private Transform bonkGrip;
        private Vector3 savedBonkPosition;
        private Quaternion savedBonkRotation;
        public bool BonkReady => !acting && !station && !Bonking && recoveryAttempt == 0 && reactionRemaining == 0 && jumpTime < 0 && Grounded;
        private bool Bonking => gateway != null && gateway.BonkPhase(this) >= 0;
        private void RestoreBonkGrip()
        {
            if (bonkGrip == null) return;
            bonkGrip.localPosition = savedBonkPosition; bonkGrip.localRotation = savedBonkRotation; bonkGrip = null;
        }
        private void ApplyBonkPose()
        {
            float phase = gateway.BonkPhase(this); if (phase < 0) return;
            var anchor = Grip; var sample = gateway.BonkPose(this);
            Vector3 left = leftHand != null ? anchor.InverseTransformPoint(leftHand.position) : Vector3.zero;
            Vector3 right = rightHand != null ? anchor.InverseTransformPoint(rightHand.position) : Vector3.zero;
            bonkGrip = anchor; savedBonkPosition = anchor.localPosition; savedBonkRotation = anchor.localRotation;
            anchor.position += transform.up * sample.Lift + transform.forward * sample.Forward;
            anchor.rotation = transform.rotation * Quaternion.Euler(sample.Tilt, sample.Twist, 0) * Quaternion.Inverse(transform.rotation) * anchor.rotation;
            PoseHand(leftHand, anchor.TransformPoint(left), -1); PoseHand(rightHand, anchor.TransformPoint(right), 1);
        }
        private void PoseHand(Transform hand, Vector3 target, float side)
        {
            if (hand == null || hand.parent == null || hand.parent.parent == null) return;
            var lower = hand.parent; var upper = lower.parent;
            WorkerCrouchPose.Solve(upper, lower, hand, target, transform.forward + transform.right * side * .4f);
        }
    }
}
