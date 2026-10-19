using System;
using System.Collections.Generic;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only oracle from new command commits and owner changes; never reads the bounded trace.</summary>
    internal sealed class MedicalSoakLedger
    {
        private readonly WorldSession world;
        private readonly int initialStock;
        private readonly long cost;
        private readonly long duration;
        private readonly int maximumContamination;
        private readonly HashSet<Guid> starts = new HashSet<Guid>(), closed = new HashSet<Guid>();
        private Guid patient, body, cycle, lastCycle, injuryCause, polledCycle;
        private long due, patientEpisode;
        private WorkerView? polledPatient;
        private WorkerView? requestedActor, requestedPatient;
        private ObjectClaimView? requestedClaim;
        private MedicalAction? requestedAction;
        private Guid requestedBodyId, requestedActorId;
        private long reserveBefore;
        private bool accessBefore;
        private WorldPhase worldPhaseBefore;
        private MedicalPhase phase;
        private int completed, cancelled, interrupted;
        private long reactorSpent;
        private bool terminalSettled;

        internal MedicalSoakLedger(WorldSession owner, MedicalDefinition definition)
        { world = owner; initialStock = definition.InitialCartridges; cost = definition.ReserveCost;
          duration = definition.DurationMilliseconds; maximumContamination = definition.MaximumContamination; }

        internal void BeforeMedical(MedicalAction action, Guid actor, Guid targetBody, bool accessAllowed)
        {
            requestedAction = action; requestedActorId = actor; requestedBodyId = targetBody;
            requestedActor = world.GetWorker(actor); Guid targetPatient = patient;
            if (action == MedicalAction.Insert)
            {
                targetPatient = Guid.Empty;
                for (int i = 0; i < 4; i++) if (targetBody == Id(40 + i)) targetPatient = Id(200 + i);
            }
            requestedPatient = world.GetWorker(targetPatient);
            requestedClaim = world.GetObject(action == MedicalAction.Insert ? targetBody : body);
            reserveBefore = world.Reactor.PowerSummary!.Available;
            accessBefore = accessAllowed; worldPhaseBefore = world.View.Phase;
        }

        internal void Observe(InteractionReply reply, ReactorAction? reactorAction = null,
            MedicalAction? medicalAction = null, Guid requestedBody = default)
        {
            if (!reply.HasNewCommit) return; // Historical changes in replay receipts cannot count again.
            if (reactorAction.HasValue)
            {
                // Bind() uses the existing default reactor costs, independently of its resulting balance.
                long expected = reactorAction == ReactorAction.Start ? 3 : reactorAction == ReactorAction.EmergencyCooling ? 4 :
                    reactorAction == ReactorAction.AuxiliaryPower ? 6 : 0;
                Require(reply.Reactor?.Change?.SpentUnits == expected, "Mixed reactor cost receipt disagrees with authored action.");
                reactorSpent += expected;
            }
            if (medicalAction.HasValue)
            {
                Require(requestedAction == medicalAction && requestedBody == requestedBodyId && accessBefore && worldPhaseBefore == WorldPhase.Running &&
                    (medicalAction == MedicalAction.EmergencyEject ? requestedActorId == patient && requestedActor?.Awareness == WorkerAwareness.Alert && requestedActor.Pose == WorkerPose.Down :
                     requestedActor?.CanInteract == true), "Mixed medical commit bypassed host access, phase or actor admission.");
                var change = reply.Medical?.Change;
                var expected = medicalAction == MedicalAction.Insert ? MedicalEvent.Inserted : medicalAction == MedicalAction.Start ? MedicalEvent.Started :
                    medicalAction == MedicalAction.Cancel ? MedicalEvent.Cancelled : medicalAction == MedicalAction.Eject ? MedicalEvent.Ejected : MedicalEvent.EmergencyEjected;
                Require(change != null && change.Kind == expected, "Mixed medical commit disagrees with its requested action.");
                if (medicalAction == MedicalAction.Insert)
                {
                    int index = -1;
                    for (int i = 0; i < 4; i++) if (requestedBody == Id(40 + i)) index = i;
                    Require(index >= 0 && change!.BodyId == requestedBody && change.PatientId == Id(200 + index),
                        "Mixed insertion changed a different requested body or patient.");
                    Require(requestedPatient?.Awareness == WorkerAwareness.Unconscious && requestedPatient.Pose == WorkerPose.Down &&
                        requestedClaim?.HolderId == requestedActorId && !requestedClaim.SlotId.HasValue && !requestedClaim.IsRetired,
                        "Mixed insertion admitted an invalid or unheld patient.");
                }
                if (medicalAction == MedicalAction.Start)
                    Require(requestedPatient?.Awareness == WorkerAwareness.Unconscious && requestedPatient.Pose == WorkerPose.Down &&
                        requestedPatient.Contamination <= maximumContamination && starts.Count < initialStock && reserveBefore >= cost &&
                        requestedClaim?.SlotId == Id(60), "Mixed treatment admitted invalid condition, stock, reserve or chamber custody.");
                Apply(change!);
                if (medicalAction == MedicalAction.Insert || medicalAction == MedicalAction.Start)
                    Require(world.GetWorker(change!.PatientId)?.Revision == requestedPatient!.Revision,
                        "Mixed insertion/start changed patient condition before completion.");
            }
        }

        internal void BeforeAdvance()
        { polledCycle = cycle; polledPatient = cycle == Guid.Empty ? null : world.GetWorker(patient); }
        private bool Eligible => polledPatient != null && polledPatient.Awareness == WorkerAwareness.Unconscious &&
            polledPatient.Pose == WorkerPose.Down && polledPatient.RecoveryEpisode == patientEpisode &&
            polledPatient.Contamination <= maximumContamination;
        internal void ObserveAdvance(MedicalChange change)
        {
            Require(polledCycle != Guid.Empty && change.CycleId == polledCycle, "Mixed owner poll changed a different treatment cycle.");
            Require(change.Kind == (!Eligible ? MedicalEvent.Interrupted : MedicalEvent.Completed) &&
                (!Eligible || world.View.ElapsedMilliseconds >= due), "Mixed poll completed early or chose the wrong patient transition.");
            if (change.Kind == MedicalEvent.Completed)
            {
                Require(change.ShiftMilliseconds == due && change.Worker != null && change.Worker.Id == patient &&
                    change.Worker.Awareness == WorkerAwareness.Alert && change.Worker.Pose == WorkerPose.Down &&
                    change.Worker.Suit == polledPatient!.Suit && change.Worker.Contamination == polledPatient.Contamination,
                    "Mixed completion lost exact timing or the patient's independent condition facts.");
            }
            Apply(change);
        }
        internal void AfterAdvance()
        {
            if (polledCycle != Guid.Empty && (!Eligible || world.View.ElapsedMilliseconds >= due))
                Require(closed.Contains(polledCycle), "Mixed owner omitted required treatment completion or interruption.");
        }

        private void Apply(MedicalChange change)
        {
            if (change.Kind != MedicalEvent.Inserted)
                Require(body != Guid.Empty && patient != Guid.Empty && change.BodyId == body && change.PatientId == patient &&
                    change.InjuryCauseId == (change.Kind == MedicalEvent.Started ? world.GetWorker(patient)!.LastCauseId : injuryCause),
                    "Mixed medical change lost its patient, body or captured injury cause.");
            switch (change.Kind)
            {
                case MedicalEvent.Inserted:
                    Require(body == Guid.Empty && change.BodyId != Guid.Empty && change.PatientId != Guid.Empty,
                        "Mixed chamber admitted overlapping patient identities.");
                    body = change.BodyId; patient = change.PatientId; phase = MedicalPhase.Loaded;
                    injuryCause = world.GetWorker(patient)!.LastCauseId;
                    Require(change.InjuryCauseId == injuryCause, "Mixed insertion lost the patient's injury cause.");
                    break;
                case MedicalEvent.Started:
                    Require((phase == MedicalPhase.Loaded || phase == MedicalPhase.Interrupted) && cycle == Guid.Empty && body == change.BodyId && patient == change.PatientId &&
                        change.CycleId != Guid.Empty && starts.Add(change.CycleId), "Mixed treatment reused or lost cycle identity.");
                    Require(change.CartridgesUsed == 1 && change.ReserveSpent == cost, "Mixed treatment receipt lost its exact cost.");
                    cycle = lastCycle = change.CycleId; phase = MedicalPhase.Treating;
                    patientEpisode = world.GetWorker(patient)!.RecoveryEpisode; injuryCause = world.GetWorker(patient)!.LastCauseId;
                    due = world.View.ElapsedMilliseconds + duration;
                    Require(change.ShiftMilliseconds == world.View.ElapsedMilliseconds && change.Station.DueAtMilliseconds == due,
                        "Mixed treatment start disagrees with authored shift-time duration.");
                    break;
                case MedicalEvent.Completed:
                    Close(change.CycleId); completed++; phase = MedicalPhase.Ready;
                    break;
                case MedicalEvent.Cancelled:
                    Close(change.CycleId); cancelled++; phase = MedicalPhase.Interrupted;
                    break;
                case MedicalEvent.Interrupted:
                    Close(change.CycleId); interrupted++; phase = MedicalPhase.Interrupted;
                    break;
                case MedicalEvent.Ejected:
                case MedicalEvent.EmergencyEjected:
                    Require((phase == MedicalPhase.Loaded || phase == MedicalPhase.Ready || phase == MedicalPhase.Interrupted) &&
                        cycle == Guid.Empty && change.CycleId == lastCycle && body == change.BodyId && patient == change.PatientId,
                        "Mixed ejection lost patient identity or released active treatment.");
                    Empty();
                    break;
                default: Require(false, "Mixed ledger received an unexpected medical change channel."); break;
            }
            Require(change.Station.Id == Id(60) && change.Station.Epoch == world.Epoch && change.Station.Phase == phase &&
                change.Station.BodyId == body && change.Station.PatientId == patient, "Mixed change station projection disagrees with the independent transition.");
        }

        internal void PatientDisconnected(Guid actor)
        {
            if (patient != actor) return;
            if (cycle != Guid.Empty) { Close(cycle); interrupted++; }
            Empty();
        }

        internal void Check()
        {
            bool ended = world.View.Phase == WorldPhase.Ended || world.View.Phase == WorldPhase.Stopped || world.View.Phase == WorldPhase.Faulted;
            if (ended && !terminalSettled)
            {
                if (cycle != Guid.Empty) { Close(cycle); cancelled++; }
                Empty(); terminalSettled = true;
            }
            var actual = world.Medical.Summary;
            Require(actual.UsedCartridges == starts.Count && actual.RemainingCartridges == initialStock - starts.Count,
                "Mixed medical stock disagrees with distinct new paid starts.");
            Require(actual.CompletedCycles == completed && actual.CancelledCycles == cancelled && actual.InterruptedCycles == interrupted,
                "Mixed treatment closure disagrees with committed cycle ledger.");
            Require(completed + cancelled + interrupted + (cycle != Guid.Empty ? 1 : 0) == starts.Count,
                "Mixed treatment cycle was lost or closed more than once.");
            Require(world.Reactor.PowerSummary!.Spent == reactorSpent + starts.Count * cost,
                "Mixed reactor/medical consumers double charged or lost a shared reserve debit.");
            var station = world.Medical.View;
            Require(ended ? station == null : station != null && station.Phase == phase && station.BodyId == body && station.PatientId == patient,
                "Mixed station projection disagrees with its command/change ledger.");
            int occupants = 0;
            for (int i = 0; i < 4; i++)
            {
                var claim = world.GetObject(Id(40 + i)); var worker = world.GetWorker(Id(200 + i));
                if (!ended) Require(claim != null && claim.IsRetired == (worker == null), "Mixed disconnected body was lost or not retired with its worker.");
                if (claim == null) continue;
                if (claim.IsRetired) Require(worker == null && !claim.HolderId.HasValue && !claim.SlotId.HasValue,
                    "Mixed disconnected patient retained condition or custody.");
                if (claim.SlotId != Id(60)) continue;
                occupants++;
                Require(claim.EntityId == body && worker != null && worker.Id == patient && worker.Pose == WorkerPose.Down && !claim.HolderId.HasValue,
                    "Mixed chamber contains the wrong, held or standing patient.");
            }
            Require(occupants == (body == Guid.Empty ? 0 : 1), "Mixed station occupancy disagrees with canonical body custody.");
        }

        private void Close(Guid id)
        {
            Require(phase == MedicalPhase.Treating && id != Guid.Empty && id == cycle && starts.Contains(id) && closed.Add(id), "Mixed cycle closed without one matching new start.");
            cycle = Guid.Empty;
        }
        private void Empty() { body = Guid.Empty; patient = Guid.Empty; lastCycle = Guid.Empty; injuryCause = Guid.Empty; phase = MedicalPhase.Empty; }
    }
}
