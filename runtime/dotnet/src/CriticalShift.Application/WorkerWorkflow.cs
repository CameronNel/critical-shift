#nullable enable
using System;
using System.Collections.Generic;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    /// <summary>Only worker operations and their possession effects; WorldSession owns lifetime and time.</summary>
    internal sealed partial class WorkerWorkflow
    {
        private readonly Guid _epoch;
        private readonly int _capacity;
        private readonly long _completionWindow;
        private readonly Dictionary<Guid, WorkerState> _workers = new Dictionary<Guid, WorkerState>();
        private readonly Dictionary<Guid, Guid> _bodyEntities = new Dictionary<Guid, Guid>();
        private readonly Dictionary<Guid, ContaminationRules> _contaminationSources = new Dictionary<Guid, ContaminationRules>();
        private readonly IWorkerRecoveryPolicy? _recovery;

        internal WorkerWorkflow(Guid epoch, int capacity, IWorkerRecoveryPolicy? recovery, long completionWindow)
        { _epoch = epoch; _capacity = capacity; _recovery = recovery; _completionWindow = completionWindow; }
        internal int Count => _workers.Count;
        internal IReadOnlyList<WorkerView> Snapshot()
        {
            var actors = new List<Guid>(_workers.Keys); actors.Sort();
            var copy = new List<WorkerView>(actors.Count);
            foreach (var actor in actors) copy.Add(Project(_workers[actor].Snapshot));
            return copy.AsReadOnly();
        }
        internal WorkerView? Get(Guid actor) => _workers.TryGetValue(actor, out var state) ? Project(state.Snapshot) : null;
        internal bool CanInteract(Guid actor) => _workers.TryGetValue(actor, out var state) && state.Snapshot.CanInteract;
        internal bool CanLeaveMedicalChamber(Guid actor) => _workers.TryGetValue(actor, out var state) &&
            state.Snapshot.Consciousness == Consciousness.Alert && state.Snapshot.Posture == Posture.Down;
        internal Guid? BodyFor(Guid actor) => _bodyEntities.TryGetValue(actor, out var body) ? body : (Guid?)null;
        internal Guid? ActorForBody(Guid body)
        {
            foreach (var pair in _bodyEntities) if (pair.Value == body) return pair.Key;
            return null;
        }
        internal bool CanTargetBody(Guid body)
        {
            var actor = ActorForBody(body);
            return !actor.HasValue || (_workers.TryGetValue(actor.Value, out var worker) && worker.Snapshot.Posture == Posture.Down);
        }
        internal void ValidateBodyRegistration(Guid actor, Guid body)
        {
            if (!_workers.ContainsKey(actor) || body == Guid.Empty || _bodyEntities.ContainsKey(actor) || ActorForBody(body).HasValue)
                throw new InvalidOperationException("A registered worker may have one unique physical-body entity.");
        }
        internal void RegisterBody(Guid actor, Guid body) => _bodyEntities.Add(actor, body);
        internal void ValidateRegistration(Guid actor)
        {
            if (actor == Guid.Empty) throw new ArgumentException("A worker identity is required.", nameof(actor));
            if (_workers.ContainsKey(actor)) throw new InvalidOperationException("Worker already registered.");
            if (_workers.Count >= _capacity) throw new InvalidOperationException("Worker capacity reached.");
        }
        internal void Register(Guid actor) { ValidateRegistration(actor); _workers.Add(actor, new WorkerState(actor, _completionWindow)); }
        internal void Remove(Guid actor) { _bodyEntities.Remove(actor); _workers.Remove(actor); }
        internal void Clear() { _bodyEntities.Clear(); _workers.Clear(); _contaminationSources.Clear(); }

        internal void RegisterContaminationSource(Guid source, WorkerContaminationDefinition definition)
        {
            if (source == Guid.Empty || definition == null) throw new ArgumentException("An authored contamination source is required.");
            if (_contaminationSources.ContainsKey(source) || _contaminationSources.Count >= WorkerState.ContaminationSourceCapacity)
                throw new InvalidOperationException("Contamination sources must be unique and bounded.");
            _contaminationSources.Add(source, definition.Rules);
        }
        internal WorkerReply Contamination(Guid actor, Guid source, long sequence, Guid cause, long sample, long now)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            if (!_contaminationSources.TryGetValue(source, out var rules)) return new WorkerReply(WorkerStatus.UnknownSource, worker: Get(actor));
            var result = worker.ObserveContamination(source, sequence, cause, rules, sample, now);
            return new WorkerReply(Map(result.Status), result.Status == WorkerResult.Applied, Project(worker.Snapshot),
                occurredAtMilliseconds: result.Contact?.SampleShiftMilliseconds,
                contaminationContact: result.Contact == null ? null : new WorkerContaminationContact(result.Contact));
        }

        internal IReadOnlyList<WorkerReply> ExpireRecovery(long now)
        {
            var changed = new List<WorkerReply>();
            var actors = new List<Guid>(_workers.Keys); actors.Sort();
            foreach (var actor in actors)
            {
                var worker = _workers[actor];
                long deadline = worker.Snapshot.RecoveryExpiresAt;
                var result = worker.ExpireRecovery(now);
                if (result == WorkerResult.RecoveryExpired) changed.Add(Reply(result, worker, occurredAt: deadline));
            }
            return changed.AsReadOnly();
        }

        internal WorkerReply Impact(InteractionWorld interaction, Guid actor, long sequence,
            WorkerImpact severity, long delay, long now, Guid hazardId, Guid causeId)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            if (severity != WorkerImpact.Knockdown && severity != WorkerImpact.Incapacitating)
                return new WorkerReply(WorkerStatus.InvalidInput, worker: Get(actor));
            var result = worker.Impact(sequence, severity == WorkerImpact.Knockdown ?
                ImpactSeverity.Knockdown : ImpactSeverity.Incapacitating, delay, now, hazardId, causeId);
            // No external callbacks occur between these logical owner updates. Unexpected integrity
            // failure propagates to WorldSession, which faults and clears the whole affected world.
            var released = result == WorkerResult.Applied ? interaction.ReleaseActorClaims(actor) : null;
            return Reply(result, worker, released);
        }

        internal WorkerReply Stabilize(Guid actor, long revision, long delay, long now) =>
            _workers.TryGetValue(actor, out var worker) ? Reply(worker.Stabilize(revision, delay, now), worker) :
                new WorkerReply(WorkerStatus.UnknownWorker);

        internal WorkerReply Environment(Guid actor, long revision, WorkerSuit suit, int contamination)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            if (suit != WorkerSuit.None && suit != WorkerSuit.Intact && suit != WorkerSuit.Compromised)
                return new WorkerReply(WorkerStatus.InvalidInput, worker: Get(actor));
            return Reply(worker.SetEnvironment(revision, (SuitCondition)(int)suit, contamination), worker);
        }

        internal WorkerReply Begin(InteractionWorld interaction, Guid actor, long episode, long revision, long now)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            var body = BodyFor(actor);
            if (body.HasValue && interaction.GetObject(body.Value)?.HolderId != null)
                return new WorkerReply(WorkerStatus.BodyClaimed, worker: Get(actor));
            if (body.HasValue && interaction.GetObject(body.Value)?.SlotId != null)
                return new WorkerReply(WorkerStatus.BodySlotted, worker: Get(actor));
            return Reply(worker.BeginRecovery(episode, revision, now), worker);
        }

        internal WorkerReply Resolve(Guid actor, long attempt, bool cancel)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            if (!worker.IsPending(attempt)) return new WorkerReply(WorkerStatus.StaleRecovery, worker: Get(actor));
            // Validate before invoking the engine boundary; stale callbacks never query a new pose.
            var clearance = cancel ? RecoveryClearance.Blocked :
                _recovery?.Evaluate(_epoch, actor, attempt) ?? RecoveryClearance.Unavailable;
            if (clearance != RecoveryClearance.Safe && clearance != RecoveryClearance.Blocked &&
                clearance != RecoveryClearance.Unavailable) throw new InvalidOperationException("Invalid clearance result.");
            var result = worker.ResolveRecovery(attempt, clearance == RecoveryClearance.Safe);
            var reply = Reply(result, worker);
            return cancel ? new WorkerReply(WorkerStatus.Cancelled, reply.Changed, reply.Worker) :
                clearance == RecoveryClearance.Unavailable ?
                    new WorkerReply(WorkerStatus.ClearanceUnavailable, reply.Changed, reply.Worker) : reply;
        }

        private WorkerReply Reply(WorkerResult result, WorkerState worker, ObjectClaimView? released = null, long? occurredAt = null)
        {
            return new WorkerReply(Map(result), result == WorkerResult.Applied || result == WorkerResult.ClearanceBlocked || result == WorkerResult.RecoveryExpired,
                Project(worker.Snapshot), released, occurredAt);
        }
        internal static WorkerStatus Map(WorkerResult result) => result switch
            {
                WorkerResult.Applied => WorkerStatus.Applied, WorkerResult.Duplicate => WorkerStatus.Duplicate,
                WorkerResult.InvalidInput => WorkerStatus.InvalidInput, WorkerResult.SequenceGap => WorkerStatus.SequenceGap,
                WorkerResult.TooOld => WorkerStatus.TooOld, WorkerResult.PayloadMismatch => WorkerStatus.PayloadMismatch,
                WorkerResult.RevisionConflict => WorkerStatus.RevisionConflict, WorkerResult.StaleRecovery => WorkerStatus.StaleRecovery,
                WorkerResult.TooEarly => WorkerStatus.TooEarly, WorkerResult.RequiresAid => WorkerStatus.RequiresAid,
                WorkerResult.InvalidState => WorkerStatus.InvalidState, WorkerResult.ClearanceBlocked => WorkerStatus.ClearanceBlocked,
                WorkerResult.RecoveryExpired => WorkerStatus.RecoveryExpired,
                WorkerResult.SourceCapacityReached => WorkerStatus.SourceCapacityReached,
                WorkerResult.NoChange => WorkerStatus.NoChange, WorkerResult.CoolingDown => WorkerStatus.CoolingDown,
                WorkerResult.StaleObservation => WorkerStatus.StaleObservation,
                _ => throw new InvalidOperationException("Unmapped worker outcome.")
            };

        private WorkerView Project(WorkerSnapshot s) => new WorkerView(_epoch, s.Id, s.Revision,
            (WorkerAwareness)(int)s.Consciousness, (WorkerPose)(int)s.Posture, (WorkerSuit)(int)s.Suit,
            s.Contamination, s.LastImpactSequence, s.RecoveryEpisode, s.RecoveryAttempt, s.RecoveryNotBefore, s.RecoveryExpiresAt, s.LastHazardId, s.LastCauseId,
            s.SuitFitting == null ? null : new SuitFittingAttemptView(s.SuitFitting));
    }
}
