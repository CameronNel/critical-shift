#nullable enable
using System;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    /// <summary>One logical OCRU prototype. Worker-specific physical chamber placement is a separate adapter obligation.</summary>
    public sealed class MedicalOperations
    {
        private readonly WorldSession world;
        private readonly InteractionWorld interaction;
        private readonly WorkerWorkflow workers;
        private MedicalStationState? state;
        private MedicalSummary? terminal;
        private Guid injuryCause;
        private int completed, cancelled, interrupted;
        internal MedicalOperations(WorldSession owner, InteractionWorld custody, WorkerWorkflow condition)
        { world = owner; interaction = custody; workers = condition; }
        public MedicalView? View => state == null ? null : new MedicalView(world.Epoch, state);
        public MedicalSummary Summary => terminal ?? new MedicalSummary(state?.Cartridges ?? 0,
            state == null ? 0 : state.Rules.Cartridges - state.Cartridges, completed, cancelled, interrupted);
        public void Register(Guid id, MedicalDefinition definition) => world.RegisterMedical(id, definition);
        internal void Configure(Guid id, MedicalDefinition definition)
        {
            if (definition == null) throw new ArgumentNullException(nameof(definition));
            if (state != null || terminal != null) throw new InvalidOperationException("One medical station may be registered.");
            var proposed = new MedicalStationState(id, definition.Rules);
            interaction.RegisterProductionSlot(id); state = proposed;
        }
        internal InteractionReply Apply(Guid actor, Guid station, MedicalRequest request)
        {
            if (state == null || state.Id != station) return Reply(MedicalStatus.UnknownStation);
            if (state.Revision != request.StationRevision) return Reply(MedicalStatus.RevisionConflict);
            switch (request.Action)
            {
                case MedicalAction.Insert: return Insert(actor, request);
                case MedicalAction.Start: return Start(request.PatientRevision);
                case MedicalAction.Cancel:
                    if (state.Mode != MedicalMode.Treating) return Reply(MedicalStatus.InvalidState);
                    state = state.Interrupt(); cancelled++;
                    return Reply(MedicalStatus.Applied, Change(MedicalEvent.Cancelled, world.View.ElapsedMilliseconds));
                case MedicalAction.EmergencyEject:
                    if (!state.CanEject) return Reply(MedicalStatus.InvalidState);
                    if (state.PatientId != actor || workers.Get(actor)?.Awareness != WorkerAwareness.Alert ||
                        workers.Get(actor)?.Pose != WorkerPose.Down) return Reply(MedicalStatus.InvalidPatient);
                    return Eject(request, true);
                case MedicalAction.Eject: return Eject(request, false);
                default: throw new InvalidOperationException("An unvalidated medical action reached the owner.");
            }
        }
        private InteractionReply Eject(MedicalRequest request, bool emergency)
        {
            if (state == null) return Reply(MedicalStatus.UnknownStation);
            if (!state.CanEject) return Reply(MedicalStatus.InvalidState);
            var previous = state; var empty = state.Eject();
            var ejection = interaction.EjectBatch(state.Id, request.ObjectRevision);
            if (!ejection.HasNewCommit) return Reply(MedicalStatus.CustodyRejected, custody: ejection);
            state = empty;
            return Reply(MedicalStatus.Applied, Change(emergency ? MedicalEvent.EmergencyEjected : MedicalEvent.Ejected,
                world.View.ElapsedMilliseconds, identity: previous), ejection);
        }
        private InteractionReply Insert(Guid actor, MedicalRequest request)
        {
            if (state!.Mode != MedicalMode.Empty) return Reply(MedicalStatus.InvalidState);
            var patient = workers.ActorForBody(request.BodyId);
            var condition = patient.HasValue ? workers.Get(patient.Value) : null;
            if (condition == null || condition.Awareness != WorkerAwareness.Unconscious || condition.Pose != WorkerPose.Down)
                return Reply(MedicalStatus.InvalidPatient);
            var proposed = state.Load(request.BodyId, condition.Id);
            var insertion = interaction.InsertBatch(request.BodyId, actor, request.LeaseGeneration, request.ObjectRevision, state.Id);
            if (!insertion.HasNewCommit) return Reply(MedicalStatus.CustodyRejected, custody: insertion);
            state = proposed; injuryCause = condition.LastCauseId;
            return Reply(MedicalStatus.Applied, Change(MedicalEvent.Inserted, world.View.ElapsedMilliseconds), insertion);
        }
        private InteractionReply Start(long expectedPatientRevision)
        {
            if (state!.Mode != MedicalMode.Loaded && state.Mode != MedicalMode.Interrupted) return Reply(MedicalStatus.InvalidState);
            var patient = workers.Get(state.PatientId);
            if (patient == null || patient.Awareness != WorkerAwareness.Unconscious || patient.Pose != WorkerPose.Down)
                return Reply(MedicalStatus.InvalidPatient);
            if (patient.Revision != expectedPatientRevision) return Reply(MedicalStatus.RevisionConflict);
            if (patient.Contamination > state.Rules.MaximumContamination) return Reply(MedicalStatus.Contaminated);
            if (state.Cartridges == 0) return Reply(MedicalStatus.NoCartridge);
            long now = world.View.ElapsedMilliseconds;
            if (now > long.MaxValue - state.Rules.DurationMilliseconds ||
                now + state.Rules.DurationMilliseconds > long.MaxValue - state.Rules.RecoveryDelayMilliseconds)
                return Reply(MedicalStatus.InvalidTime);
            if (interaction.SlotOccupant(state.Id) != state.BodyId) throw new InvalidOperationException("Medical patient lost chamber custody.");
            var proposed = state.Begin(Guid.NewGuid(), patient.RecoveryEpisode, patient.Revision, now);
            if (!world.Reactor.TryPrepareReserveDebit(state.Rules.ReserveCost, out var debit)) return Reply(MedicalStatus.InsufficientReserve);
            // All expected rejections and arithmetic precede these installs. No callbacks or awaits occur between owners.
            world.Reactor.CommitReserveDebit(debit!); state = proposed; injuryCause = patient.LastCauseId;
            return Reply(MedicalStatus.Applied, Change(MedicalEvent.Started, now, spent: state.Rules.ReserveCost, cartridges: 1));
        }
        internal MedicalChange? AdvanceTo(long elapsed)
        {
            if (state == null || state.Mode != MedicalMode.Treating) return null;
            if (interaction.SlotOccupant(state.Id) != state.BodyId) throw new InvalidOperationException("Treating patient lost chamber custody.");
            var patient = workers.Get(state.PatientId);
            if (patient == null || patient.RecoveryEpisode != state.PatientEpisode || patient.Awareness != WorkerAwareness.Unconscious ||
                patient.Pose != WorkerPose.Down || patient.Contamination > state.Rules.MaximumContamination)
            {
                state = state.Interrupt(); interrupted++;
                return Change(MedicalEvent.Interrupted, elapsed);
            }
            if (elapsed < state.DueAtMilliseconds) return null;
            long due = state.DueAtMilliseconds;
            var proposed = state.Complete(due);
            var stabilized = workers.Stabilize(patient.Id, patient.Revision, state.Rules.RecoveryDelayMilliseconds, due);
            if (stabilized.Status != WorkerStatus.Applied) throw new InvalidOperationException("Prepared medical completion could not stabilize its patient.");
            state = proposed; completed++;
            return Change(MedicalEvent.Completed, due, worker: stabilized.Worker);
        }
        internal MedicalChange? DetachDisconnectedPatient(Guid patient, Guid body)
        {
            if (state == null || state.PatientId != patient) return null;
            if (state.BodyId != body) throw new InvalidOperationException("Medical patient body changed unexpectedly.");
            var previous = state; bool treating = state.Mode == MedicalMode.Treating;
            var releasable = treating ? state.Interrupt() : state;
            var empty = releasable.Eject(); var claim = interaction.GetObject(body);
            if (claim == null || claim.SlotId != state.Id) throw new InvalidOperationException("Disconnect lost medical chamber custody.");
            var ejection = interaction.EjectBatch(state.Id, claim.Revision);
            if (!ejection.HasNewCommit) throw new InvalidOperationException("Disconnected medical patient could not be ejected.");
            state = empty; if (treating) interrupted++;
            return Change(MedicalEvent.PatientDisconnected, world.View.ElapsedMilliseconds, identity: previous);
        }
        internal void Clear()
        {
            if (terminal != null) return;
            terminal = new MedicalSummary(state?.Cartridges ?? 0, state == null ? 0 : state.Rules.Cartridges - state.Cartridges,
                completed, cancelled + (state?.Mode == MedicalMode.Treating ? 1 : 0), interrupted);
            state = null;
        }
        private MedicalChange Change(MedicalEvent kind, long at, long spent = 0, int cartridges = 0,
            WorkerView? worker = null, MedicalStationState? identity = null)
        {
            var source = identity ?? state!;
            return new MedicalChange(kind, View!, source.CycleId, source.PatientId, source.BodyId, injuryCause, at, spent, cartridges, worker);
        }
        private InteractionReply Reply(MedicalStatus status, MedicalChange? change = null, InteractionReply? custody = null) =>
            new InteractionReply(status == MedicalStatus.Applied ? InteractionStatus.Applied : custody?.Status ?? InteractionStatus.MedicalRejected,
                true, custody?.State, medical: new MedicalReply(status, View, change));
    }
}
