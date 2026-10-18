using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Trusted local observations and recovery protocol; WorldSession remains the worker-state writer.</summary>
    [DisallowMultipleComponent]
    public sealed class LocalWorkerStateHost : MonoBehaviour
    {
        private readonly Dictionary<Guid, long> hazardSequences = new Dictionary<Guid, long>();
        private WorldSession world;
        private Guid actor, diagnosticHazard;
        private WorkerBodyRig rig;
        private WorkerRecoveryPlacement placement;
        private Action pumpClock, resetLocomotion;
        private Action<Exception> reportFailure;
        private bool active;
        private Vector2 downMovement;
        private long pendingAttempt, completeAt;
        public string LastAction { get; private set; } = "Worker upright";
        public WorkerView Worker => world == null ? null : world.GetWorker(actor);
        public bool Recovering => pendingAttempt > 0;
        public bool CrawlDriveActive { get; private set; }

        public void Initialize(WorldSession session, Guid workerId, WorkerBodyRig body,
            WorkerRecoveryPlacement recovery, Action sampleClock, Action resetWalking, Action<Exception> onFailure)
        {
            if (world != null || session == null || session.View.Phase != WorldPhase.Setup ||
                session.GetWorker(workerId) == null || body == null || body.Epoch != session.Epoch || body.Actor != workerId)
                throw new InvalidOperationException("Compose one worker adapter before the world starts.");
            world = session; actor = workerId; rig = body; placement = recovery ?? throw new ArgumentNullException(nameof(recovery));
            pumpClock = sampleClock ?? throw new ArgumentNullException(nameof(sampleClock));
            resetLocomotion = resetWalking ?? throw new ArgumentNullException(nameof(resetWalking));
            reportFailure = onFailure ?? throw new ArgumentNullException(nameof(onFailure));
        }

        public void BindHazard(Guid hazard, bool diagnostic = false)
        {
            if (world == null || active || world.View.Phase != WorldPhase.Setup || hazard == Guid.Empty ||
                hazardSequences.ContainsKey(hazard) || hazardSequences.Count >= 8 || (diagnostic && diagnosticHazard != Guid.Empty))
                throw new InvalidOperationException("Bind a unique bounded host hazard source during setup.");
            hazardSequences.Add(hazard, 0); if (diagnostic) diagnosticHazard = hazard;
        }

        public void Activate()
        {
            if (active || world == null || world.View.Phase != WorldPhase.Running)
                throw new InvalidOperationException("Activate the worker adapter once after world startup.");
            rig.Reconcile(Worker, world.View.Phase); active = true;
        }

        public void SetDownMovement(Vector2 movement)
        {
            if (float.IsNaN(movement.x) || float.IsNaN(movement.y) || float.IsInfinity(movement.x) || float.IsInfinity(movement.y))
                throw new ArgumentException("Down-worker movement must be finite.");
            downMovement = Vector2.ClampMagnitude(movement, 1);
        }

        public WorkerStatus ObserveKnockdown(Guid hazard, Vector3 impulse, Vector3 contact)
        {
            if (!active) return WorkerStatus.NotReady;
            try
            {
                pumpClock();
                if (!hazardSequences.TryGetValue(hazard, out long previous))
                    throw new InvalidOperationException("Unregistered physical hazard source.");
                if (!Finite(impulse) || !Finite(contact)) throw new ArgumentException("Physical impact samples must be finite.");
                long sequence = checked(previous + 1);
                var reply = world.ApplyWorkerImpact(world.Epoch, actor, sequence, WorkerImpact.Knockdown,
                    1500, hazard, Guid.NewGuid());
                LastAction = "Impact: " + reply.Status;
                if (reply.Status == WorkerStatus.Applied)
                {
                    hazardSequences[hazard] = sequence; pendingAttempt = 0; placement.CancelStage();
                    downMovement = Vector2.zero;
                    rig.Reconcile(reply.Worker, world.View.Phase); rig.ApplyImpactImpulse(impulse, contact);
                }
                else if (reply.Status != WorkerStatus.Paused && reply.Status != WorkerStatus.WorldEnded &&
                    reply.Status != WorkerStatus.WorldStopped && reply.Status != WorkerStatus.WorldFaulted)
                    throw new InvalidOperationException("The trusted impact stream was rejected: " + reply.Status);
                return reply.Status;
            }
            catch (Exception exception) { Fail(exception); return WorkerStatus.WorldFaulted; }
        }

        public void DiagnosticKnockdown()
        {
            if (diagnosticHazard == Guid.Empty || rig == null) return;
            ObserveKnockdown(diagnosticHazard, rig.Controller.transform.right * 22 + Vector3.up * 8, rig.Pelvis.position);
        }

        public void RequestRecovery()
        {
            if (!active) return;
            try
            {
                pumpClock(); var worker = Worker;
                if (worker == null || worker.Pose != WorkerPose.Down)
                { LastAction = "Recovery needs a down worker"; return; }
                if (world.GetWorkerBodyClaim(actor)?.HolderId != null)
                { LastAction = "Release the worker's suit grip before recovery"; return; }
                var clearance = placement.Prepare();
                if (clearance != RecoveryClearance.Safe) { LastAction = "Recovery: " + clearance; return; }
                var begin = world.BeginWorkerRecovery(world.Epoch, actor, worker.RecoveryEpisode, worker.Revision);
                LastAction = "Recovery: " + begin.Status;
                if (begin.Status != WorkerStatus.Applied) return;
                pendingAttempt = begin.Worker.RecoveryAttempt;
                placement.Stage(world.Epoch, actor, pendingAttempt);
                // A brief process-clock window makes the pending handoff visible and rechecks the pose afterward.
                completeAt = checked(world.View.ElapsedMilliseconds + 400);
            }
            catch (Exception exception) { Fail(exception); }
        }

        private void Update()
        {
            if (!active) return;
            try
            {
                pumpClock(); var worker = Worker;
                if (pendingAttempt > 0 && (worker == null || worker.Pose != WorkerPose.Recovering || worker.RecoveryAttempt != pendingAttempt))
                { LastAction = "Recovery attempt interrupted or expired"; pendingAttempt = 0; placement.CancelStage(); }
                if (pendingAttempt > 0 && world.View.Phase == WorldPhase.Running && world.View.ElapsedMilliseconds >= completeAt)
                {
                    Physics.SyncTransforms();
                    long attempt = pendingAttempt;
                    var result = world.CompleteWorkerRecovery(world.Epoch, actor, attempt);
                    LastAction = "Recovery: " + result.Status;
                    if (result.Status == WorkerStatus.Applied) { placement.ApplyAccepted(world.Epoch, actor, attempt); resetLocomotion(); }
                    pendingAttempt = 0; placement.CancelStage(); worker = Worker;
                }
                if (worker == null) { Shutdown(); return; }
                rig.Reconcile(worker, world.View.Phase);
            }
            catch (Exception exception) { Fail(exception); }
        }

        private void LateUpdate()
        {
            if (!active || rig == null) return;
            try
            {
                var worker = Worker;
                if (worker == null) { Shutdown(); return; }
                rig.Reconcile(worker, world.View.Phase); rig.UpdatePresentation();
            }
            catch (Exception exception) { Fail(exception); }
        }
        private void FixedUpdate()
        {
            CrawlDriveActive = false;
            if (!active) return;
            try
            {
                pumpClock(); var worker = Worker;
                if (worker == null) { Shutdown(); return; }
                rig.Reconcile(worker, world.View.Phase);
                if (world.View.Phase != WorldPhase.Running || worker.Awareness != WorkerAwareness.Alert ||
                    worker.Pose != WorkerPose.Down || pendingAttempt > 0) return;
                var custody = world.GetWorkerBodyClaim(actor);
                if (custody != null && (custody.HolderId.HasValue || custody.SlotId.HasValue || custody.IsRetired)) return;
                CrawlDriveActive = rig.Crawl(downMovement);
            }
            catch (Exception exception) { Fail(exception); }
        }
        private void Fail(Exception exception) { Shutdown(); reportFailure?.Invoke(exception); }
        public void Shutdown()
        {
            active = false; pendingAttempt = 0; placement?.CancelStage(); downMovement = Vector2.zero; CrawlDriveActive = false;
            if (rig != null) rig.Freeze();
        }
        private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z);
        private void OnDisable()
        {
            bool unexpected = active && world != null && (world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused);
            Shutdown();
            if (unexpected) reportFailure?.Invoke(new InvalidOperationException("The live worker-state adapter was disabled."));
        }
        private void OnDestroy() => Shutdown();
        private void OnApplicationFocus(bool focused) { if (!focused) downMovement = Vector2.zero; }
    }
}
