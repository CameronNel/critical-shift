using System;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    public sealed partial class WorkerController
    {
        private readonly Collider[] clearanceHits = new Collider[64];
        private readonly RaycastHit[] floorHits = new RaycastHit[64];
        private bool movingCapsule, pendingKnockdown;
        private Vector3 pendingImpulse;
        private Vector3? pendingPoint;
        private float downYaw;
        private double phaseAt;
        public bool CanStandAt(Vector3 position) => ClearCapsule(position, standingHeight);
        public bool InStation => station;
        public bool PhysicsFaulted => ragdoll == null || !ragdoll.isActiveAndEnabled || ragdoll.Faulted;
        public long StationPresentation { get; private set; }
        private bool stationExiting;
        public override Rigidbody GripBody(Vector3 target)
        {
            var left = leftHand != null ? leftHand.GetComponent<Rigidbody>() : null;
            var right = rightHand != null ? rightHand.GetComponent<Rigidbody>() : null;
            if (left == null || !ragdoll.Owns(left)) left = null;
            if (right == null || !ragdoll.Owns(right)) right = null;
            if (left == null) return right != null ? right : PhysicalBody;
            return right == null || (left.position - target).sqrMagnitude < (right.position - target).sqrMagnitude ? left : right;
        }
        public override void ApplyBodyImpulse(Vector3 impulse, Vector3 point) { ragdoll.ApplyImpulse(impulse, point); }

        private bool ClearCapsule(Vector3 position, float height)
        {
            if (capsule == null || !WorkerRagdollRigValidation.RootConvention(transform) || height < capsule.radius * 2) return false;
            float radius = Mathf.Max(.01f, capsule.radius - capsule.skinWidth);
            int count = Physics.OverlapCapsuleNonAlloc(position + Vector3.up * (radius + .03f),
                position + Vector3.up * (height - radius), radius, clearanceHits, clearanceMask, QueryTriggerInteraction.Ignore);
            if (count == clearanceHits.Length) return false;
            for (int i = 0; i < count; i++) if (Array.IndexOf(BodyColliders, clearanceHits[i]) < 0) return false;
            count = Physics.RaycastNonAlloc(position + Vector3.up * .12f, Vector3.down, floorHits, .3f, clearanceMask, QueryTriggerInteraction.Ignore);
            if (count == floorHits.Length) return false;
            float closest = float.PositiveInfinity; RaycastHit floor = default;
            for (int i = 0; i < count; i++) if (Array.IndexOf(BodyColliders, floorHits[i].collider) < 0 && floorHits[i].distance < closest)
            { closest = floorHits[i].distance; floor = floorHits[i]; }
            return floor.collider != null && Vector3.Angle(floor.normal, Vector3.up) <= capsule.slopeLimit;
        }
        private void TickRecovery()
        {
            movement.SuspendPlayback();
            if (!gateway.RecoveryReady(this) || !ragdoll.TryRecoveryPose(clearanceMask, capsule.slopeLimit, out var candidate) || !CanStandAt(candidate.Position)) return;
            long attempt = gateway.BeginRecovery(this);
            if (attempt == 0) return;
            var clip = candidate.FaceDown ? MovementClip.GETUP_FRONT : MovementClip.GETUP_BACK;
            ragdoll.MoveRootPreservingPose(candidate); ragdoll.BeginRecoveryBlend(); ragdoll.Freeze();
            ResetMotor(); capsule.enabled = false; recoveryAttempt = attempt; recoveryRemaining = movement.Duration(clip);
            phaseAt = Time.realtimeSinceStartupAsDouble;
            if (recoveryRemaining > 4.5f || !movement.PrimeGroundedAction(clip, ++actionSequence))
            { gateway.CancelRecovery(this, attempt); KnockDown(Vector3.zero); }
        }
        private void ResetMotor()
        { planar = velocity = Vector3.zero; vertical = -2; airborne = groundGrace = jumpBuffer = reactionRemaining = 0; jumpTime = -1; yawRate = 0; crouched = false; }
        public void KnockDown(Vector3 impulse) => KnockDown(impulse, null);
        public void KnockDown(Vector3 impulse, Vector3? contactPoint)
        {
            if (movingCapsule)
            { pendingKnockdown = true; pendingImpulse += impulse; if (contactPoint.HasValue) pendingPoint = contactPoint; return; }
            Vector3 inherited = Down ? Vector3.zero : velocity;
            CancelSceneActions(); station = false; recoveryAttempt = 0; movement.SuspendPlayback(); capsule.enabled = false;
            ragdoll.Activate(inherited, impulse, contactPoint ?? ragdoll.Pelvis.worldCenterOfMass);
            ResetMotor(); downYaw = transform.eulerAngles.y;
        }
        public void Stagger(Vector3 worldDirection)
        {
            if (!gateway.CanAct(this) || !Grounded) return;
            CancelSceneActions();
            Vector3 local = transform.InverseTransformDirection(worldDirection);
            var clip = Mathf.Abs(local.x) > Mathf.Abs(local.z) ? local.x < 0 ? MovementClip.STAGGER_L : MovementClip.STAGGER_R :
                local.z < 0 ? MovementClip.STAGGER_B : MovementClip.STAGGER_F;
            movement.TryPlayAction(clip, ++actionSequence); reactionRemaining = movement.Duration(clip);
        }
        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var hazard = hit.collider.GetComponentInParent<WorkerCollisionHazard>(); var body = hit.collider.attachedRigidbody;
            if (hazard != null && body != null) hazard.Observe(this, body.GetPointVelocity(hit.point) - velocity, hit.point, hit.normal);
        }
        public void BecomeUpright()
        { ragdoll.Freeze(); ResetMotor(); capsule.height = standingHeight; capsule.center = Vector3.up * standingHeight / 2; capsule.enabled = true; station = false; recoveryAttempt = 0; }
        public override void StopSceneSimulation()
        {
            CancelSceneActions(); station = false; recoveryAttempt = 0; pendingKnockdown = false; pendingImpulse = Vector3.zero; pendingPoint = null;
            ResetMotor(); if (capsule != null) capsule.enabled = false;
            if (ragdoll != null) ragdoll.Stop(); if (movement != null) movement.SuspendPlayback();
        }
        private void TickDowned()
        {
            bool input = localInput && inputState.Captured && gateway.ConsciousDown(this);
            if (input)
            {
                if (Input.GetKeyDown(KeyCode.G)) gateway.Execute(this, gateway.Held(this), SceneOperation.Release, out _);
                if (Input.GetKeyDown(KeyCode.E))
                {
                    var held = gateway.Held(this); var target = held != null ? held : LookTarget();
                    if (gateway.Execute(this, target, held != null ? SceneOperation.Release : SceneOperation.Grab, out var feedback)) ShowFeedback(held != null ? "Handle released." : "Handle gripped. G or E releases it.");
                    else ShowFeedback(feedback);
                }
                downYaw += Input.GetAxisRaw("Mouse X") * sensitivity;
                pitch = Mathf.Clamp(pitch - Input.GetAxisRaw("Mouse Y") * sensitivity, -80, 80);
                if (Input.GetKeyDown(KeyCode.H) || Input.GetKeyDown(KeyCode.P)) { pingEffect?.Invoke(ragdoll.Pelvis.position); ShowFeedback("Help beacon activated."); }
            }
            Vector3 crawl = input ? Quaternion.Euler(0, downYaw, 0) * new Vector3(Key(KeyCode.D) - Key(KeyCode.A), 0, Key(KeyCode.W) - Key(KeyCode.S)) : Vector3.zero;
            ragdoll.SetConsciousMotion(crawl, input && Input.GetKey(KeyCode.B));
        }
        private void TrackDownedCamera()
        {
            if (!localInput) return;
            Vector3 target = head != null ? head.position + Vector3.up * .1f : ragdoll.Pelvis.position + Vector3.up * .35f;
            eye.position = Vector3.Lerp(eye.position, target, 1 - Mathf.Exp(-Time.deltaTime / .05f));
            eye.rotation = Quaternion.Euler(pitch, downYaw, 0);
        }
        public override void PresentStation(SceneOperation value, Transform anchor)
        {
            CancelSceneActions(); ragdoll.Stop(); ResetMotor(); capsule.enabled = false;
            transform.SetPositionAndRotation(anchor.position, Quaternion.Euler(0, anchor.eulerAngles.y, 0)); station = true; StationPresentation++; stationExiting = false; stationTime = 0; phaseAt = Time.realtimeSinceStartupAsDouble;
            if (value == SceneOperation.Reanimation) movement.PrimeGroundedAction(MovementClip.REANIM_IDLE, ++actionSequence);
            else { stationExiting = true; movement.PrimeGroundedAction(MovementClip.LOCKER_EXIT, ++actionSequence); stationTime = -movement.Duration(MovementClip.LOCKER_EXIT); }
        }
        public void ReanimationJolt() { movement.TryPlayAction(MovementClip.REANIM_JOLT, ++actionSequence, MovementClip.REANIM_IDLE); }
        public void ReanimationExit(long attempt)
        {
            recoveryAttempt = attempt; float duration = movement.Duration(MovementClip.REANIM_EXIT);
            if (duration > 4.5f || !movement.TryPlayAction(MovementClip.REANIM_EXIT, ++actionSequence))
            { gateway.CancelRecovery(this, attempt); KnockDown(Vector3.zero); return; }
            stationExiting = true; stationTime = -duration; phaseAt = Time.realtimeSinceStartupAsDouble;
        }
        private float PhaseDelta()
        { double now = Time.realtimeSinceStartupAsDouble; float elapsed = (float)Math.Max(0, now - phaseAt); phaseAt = now; return elapsed; }
        private void ApplyPhaseSample(float elapsed)
        {
            elapsed = Mathf.Clamp(elapsed, 0, 4.5f);
            do { float step = Mathf.Min(elapsed, 1); movement.ApplySample(new MovementAnimationSample(0, 0, 0, true), step); elapsed -= step; } while (elapsed > 0);
        }
        private void TickStation()
        {
            float elapsed = PhaseDelta(); ApplyPhaseSample(stationTime < 0 ? Mathf.Min(elapsed, -stationTime) : elapsed);
            if (!stationExiting) return;
            stationTime = Mathf.Min(0, stationTime + elapsed);
            if (stationTime != 0) return;
            if (recoveryAttempt == 0) { if (RecoveryClear) BecomeUpright(); else ShowFeedback("Clear the locker exit to stand up."); }
            else if (!gateway.CompleteRecovery(this, recoveryAttempt)) KnockDown(Vector3.zero);
            recoveryAttempt = 0;
        }
    }
}
