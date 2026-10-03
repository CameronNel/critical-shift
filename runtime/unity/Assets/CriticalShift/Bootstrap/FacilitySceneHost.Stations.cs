using System;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using UnityEngine;

namespace CriticalShift.Bootstrap
{
    public sealed partial class FacilitySceneHost
    {
        private sealed class ReanimationCycle
        {
            public readonly FacilityControl Control;
            public readonly WorkerController Patient;
            public readonly WorkerRecoveryTicket Ticket;
            public readonly WorldTimerHandle Timer;
            public long Presentation;
            public ReanimationCycle(FacilityControl control, WorkerController patient, WorkerRecoveryTicket ticket, WorldTimerHandle timer)
            { Control = control; Patient = patient; Ticket = ticket; Timer = timer; }
        }
        private readonly Dictionary<Guid, ReanimationCycle> stations = new Dictionary<Guid, ReanimationCycle>();
        private bool AidReady(FacilityControl control)
        {
            var patient = control.Patient;
            return patient != null && actors.TryGetValue(patient.Id, out var actor) && actor == patient && actor.isActiveAndEnabled &&
                world.GetWorker(patient.Id)?.Awareness == WorkerAwareness.Unconscious && world.GetWorker(patient.Id)?.Pose == WorkerPose.Down &&
                !IsInStation(patient) && patient.PhysicalBody != null && Vector3.Distance(patient.PhysicalBody.position, control.Contact.position) <= control.Reach;
        }
        private bool StationReady(FacilityControl control)
        {
            if (!control.Connected || control.Patient == null || control.WorkerAnchor == null || stations.ContainsKey(control.Id) ||
                !actors.TryGetValue(control.Patient.Id, out var patient) || patient != control.Patient || !patient.isActiveAndEnabled ||
                IsInStation(patient) || BodyHeld(patient) || patient.PhysicalBody == null || !patient.Down) return false;
            var state = world.GetWorker(patient.Id);
            return state != null && state.Awareness == WorkerAwareness.Unconscious && state.Pose == WorkerPose.Down &&
                Vector3.Distance(patient.PhysicalBody.position, control.WorkerAnchor.position + Vector3.up * .5f) <= 1 &&
                patient.CanStandAt(control.WorkerAnchor.position) && world.View.PendingTimerCount < world.Configuration.TimerCapacity;
        }
        private void StartStation(FacilityControl control)
        {
            var patient = actors[control.Patient.Id]; var state = world.GetWorker(patient.Id);
            var timer = world.Schedule(world.Epoch, control.Id, "reanimation", delayMilliseconds: 3000, basis: WorldTimeBasis.ShiftTime);
            if (timer.Status != WorldControlStatus.Applied) throw new InvalidOperationException("Prevalidated station scheduling failed: " + timer.Status);
            var cycle = new ReanimationCycle(control, patient, new WorkerRecoveryTicket(world.Epoch, patient.Id, state.RecoveryEpisode), timer.Handle);
            stations.Add(control.Id, cycle); patient.PresentStation(CriticalShift.Unity.Shared.SceneOperation.Reanimation, control.WorkerAnchor); cycle.Presentation = patient.StationPresentation; patient.ReanimationJolt();
        }
        private bool Current(ReanimationCycle cycle)
        {
            if (cycle.Control == null || !cycle.Control.isActiveAndEnabled || cycle.Patient == null || !cycle.Patient.isActiveAndEnabled ||
                cycle.Control.Patient != cycle.Patient || !OwnsPresentation(cycle) || !actors.TryGetValue(cycle.Ticket.Patient, out var patient) || patient != cycle.Patient) return false;
            var state = world.GetWorker(cycle.Ticket.Patient);
            return state != null && state.Pose == WorkerPose.Down && state.Awareness == WorkerAwareness.Unconscious &&
                cycle.Ticket.Matches(world.Epoch, state.Id, state.RecoveryEpisode);
        }
        private bool OwnsPresentation(ReanimationCycle cycle) => cycle.Patient != null && cycle.Patient.isActiveAndEnabled &&
            cycle.Patient.InStation && cycle.Patient.StationPresentation == cycle.Presentation &&
            actors.TryGetValue(cycle.Ticket.Patient, out var patient) && patient == cycle.Patient;
        private void CancelInvalidStations()
        {
            cancelledStations.Clear();
            foreach (var binding in stations) if (!Current(binding.Value)) cancelledStations.Add(binding.Key);
            foreach (var id in cancelledStations)
            {
                var cycle = stations[id]; world.CancelTimer(cycle.Timer); stations.Remove(id);
                if (OwnsPresentation(cycle)) cycle.Patient.KnockDown(Vector3.zero);
            }
        }
        private void FinishStation(WorldTimerSignal signal)
        {
            if (!stations.TryGetValue(signal.OwnerId, out var cycle) || signal.Handle.Epoch != cycle.Timer.Epoch || signal.Handle.Sequence != cycle.Timer.Sequence) return;
            bool current = Current(cycle); stations.Remove(signal.OwnerId);
            if (!current) { if (OwnsPresentation(cycle)) cycle.Patient.KnockDown(Vector3.zero); return; }
            var state = world.GetWorker(cycle.Ticket.Patient);
            var aided = world.StabilizeWorker(world.Epoch, state.Id, state.Revision, 0);
            if (!aided.Changed) { cycle.Patient.KnockDown(Vector3.zero); return; }
            long attempt = BeginRecovery(cycle.Patient);
            if (attempt == 0) { cycle.Patient.KnockDown(Vector3.zero); return; }
            cycle.Patient.ReanimationExit(attempt);
        }
    }
}
