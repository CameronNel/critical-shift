using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    public sealed partial class LocalWorldHost
    {
        private Func<MedicalView, string> medicalControls;
        private Func<MedicalReply, string> medicalResult;

        public void BindMedicalReadout(Func<MedicalView, string> controls, Func<MedicalReply, string> result)
        {
            RequireSetup();
            if (medicalControls != null || controls == null || result == null)
                throw new InvalidOperationException("Bind one read-only medical formatter before host startup.");
            medicalControls = controls; medicalResult = result;
        }

        public void BindMedicalSlot(Guid station, Transform bed, Collider bedSupport, Transform discharge, Collider floor, Transform console)
        { RequireSetup(); bindings.BindMedicalSlot(station, bed, bedSupport, discharge, floor, console); }

        public void BindMedicalWorker(Guid body, Func<ObjectClaimView, Guid, Transform, Collider, bool, bool> prepare,
            Action<ObjectClaimView, Guid> reconcile, Action cancel, Action clear)
        { RequireSetup(); bindings.BindMedicalWorker(body, prepare, reconcile, cancel, clear); }

        private MedicalView OwnMedicalStation()
        {
            if (!active || stopped || world == null) return null;
            var patient = world.GetWorker(localActor); var medical = world.Medical.View;
            var claim = world.GetWorkerBodyClaim(localActor);
            return patient?.Awareness == WorkerAwareness.Alert && patient.Pose == WorkerPose.Down &&
                medical != null && medical.PatientId == localActor && claim != null && !claim.IsRetired &&
                claim.EntityId == medical.BodyId && claim.SlotId == medical.Id ? medical : null;
        }

        public void OperateMedical(Guid station, MedicalAction action, Guid body)
        {
            if (!active || stopped) return;
            Guid stagedBody = Guid.Empty;
            try
            {
                // One final host sample, including same-time medical interruption settlement.
                // No second Pump, callback or physics step is allowed between staging and the command.
                Pump(true); if (!active) return;
                if (world.View.Phase != WorldPhase.Running)
                { LastAction = "Resume the shift clock before using medical equipment"; return; }
                Physics.SyncTransforms();
                bindings.RequireMedicalStation(station);
                bool movesBody = action == MedicalAction.Insert || action == MedicalAction.Eject || action == MedicalAction.EmergencyEject;
                if (movesBody && !bindings.PrepareMedicalMove(station, action, body, out stagedBody))
                { LastAction = "Medical transfer unavailable: use an incapacitated patient and clear the complete bed or discharge area"; return; }
                var reply = commands.OperateMedical(station, action, body);
                if (!reply.HasNewCommit && stagedBody != Guid.Empty) bindings.CancelMedicalStage(stagedBody);
                LastAction = reply.Medical == null ? reply.Status.ToString() : medicalResult == null ? reply.Medical.Status.ToString() : medicalResult(reply.Medical);
                if (reply.IsReplay) LastAction += " (previous result; no repeated effect)";
                // Reconciliation reads current world custody, never the historical reply's claim.
                Reconcile(false);
            }
            catch (Exception exception)
            {
                if (stagedBody != Guid.Empty) bindings?.CancelMedicalStage(stagedBody);
                StopAfterFailure(exception);
            }
        }
    }
}
