using System;
using System.Collections.Generic;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    /// <summary>Only worker operations and their possession effects; WorldSession owns lifetime and time.</summary>
    internal sealed class WorkerWorkflow
    {
        private readonly Guid _epoch;
        private readonly int _capacity;
        private readonly long _completionWindow;
        private readonly Dictionary<Guid, WorkerState> _workers = new Dictionary<Guid, WorkerState>();
        private readonly IWorkerRecoveryPolicy? _recovery;

        internal WorkerWorkflow(Guid epoch, int capacity, IWorkerRecoveryPolicy? recovery, long completionWindow)
        { _epoch = epoch; _capacity = capacity; _recovery = recovery; _completionWindow = completionWindow; }
        internal int Count => _workers.Count;
        internal WorkerView? Get(Guid actor) => _workers.TryGetValue(actor, out var state) ? Project(state.Snapshot) : null;
        internal bool CanInteract(Guid actor) => _workers.TryGetValue(actor, out var state) && state.Snapshot.CanInteract;
        internal void ValidateRegistration(Guid actor)
        {
            if (actor == Guid.Empty) throw new ArgumentException("A worker identity is required.", nameof(actor));
            if (_workers.ContainsKey(actor)) throw new InvalidOperationException("Worker already registered.");
            if (_workers.Count >= _capacity) throw new InvalidOperationException("Worker capacity reached.");
        }
        internal void Register(Guid actor) { ValidateRegistration(actor); _workers.Add(actor, new WorkerState(actor, _completionWindow)); }
        internal void Remove(Guid actor) => _workers.Remove(actor);
        internal void Clear() => _workers.Clear();

        internal IReadOnlyList<WorkerReply> ExpireRecovery(long now)
        {
            var changed = new List<WorkerReply>();
            var actors = new List<Guid>(_workers.Keys); actors.Sort();
            foreach (var actor in actors)
            {
                var worker = _workers[actor];
                var result = worker.ExpireRecovery(now);
                if (result == WorkerResult.RecoveryExpired) changed.Add(Reply(result, worker));
            }
            return changed.AsReadOnly();
        }

        internal WorkerReply Impact(InteractionWorld interaction, Guid actor, long sequence,
            WorkerImpact severity, long delay, long now)
        {
            if (!_workers.TryGetValue(actor, out var worker)) return new WorkerReply(WorkerStatus.UnknownWorker);
            if (severity != WorkerImpact.Knockdown && severity != WorkerImpact.Incapacitating)
                return new WorkerReply(WorkerStatus.InvalidInput, worker: Get(actor));
            var result = worker.Impact(sequence, severity == WorkerImpact.Knockdown ?
                ImpactSeverity.Knockdown : ImpactSeverity.Incapacitating, delay, now);
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

        internal WorkerReply Begin(Guid actor, long episode, long revision, long now) =>
            _workers.TryGetValue(actor, out var worker) ? Reply(worker.BeginRecovery(episode, revision, now), worker) :
                new WorkerReply(WorkerStatus.UnknownWorker);

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

        private WorkerReply Reply(WorkerResult result, WorkerState worker, ObjectClaimView? released = null)
        {
            WorkerStatus status = result switch
            {
                WorkerResult.Applied => WorkerStatus.Applied, WorkerResult.Duplicate => WorkerStatus.Duplicate,
                WorkerResult.InvalidInput => WorkerStatus.InvalidInput, WorkerResult.SequenceGap => WorkerStatus.SequenceGap,
                WorkerResult.TooOld => WorkerStatus.TooOld, WorkerResult.PayloadMismatch => WorkerStatus.PayloadMismatch,
                WorkerResult.RevisionConflict => WorkerStatus.RevisionConflict, WorkerResult.StaleRecovery => WorkerStatus.StaleRecovery,
                WorkerResult.TooEarly => WorkerStatus.TooEarly, WorkerResult.RequiresAid => WorkerStatus.RequiresAid,
                WorkerResult.InvalidState => WorkerStatus.InvalidState, WorkerResult.ClearanceBlocked => WorkerStatus.ClearanceBlocked,
                WorkerResult.RecoveryExpired => WorkerStatus.RecoveryExpired,
                _ => throw new InvalidOperationException("Unmapped worker outcome.")
            };
            return new WorkerReply(status, result == WorkerResult.Applied || result == WorkerResult.ClearanceBlocked || result == WorkerResult.RecoveryExpired,
                Project(worker.Snapshot), released);
        }

        private WorkerView Project(WorkerSnapshot s) => new WorkerView(_epoch, s.Id, s.Revision,
            (WorkerAwareness)(int)s.Consciousness, (WorkerPose)(int)s.Posture, (WorkerSuit)(int)s.Suit,
            s.Contamination, s.LastImpactSequence, s.RecoveryEpisode, s.RecoveryAttempt, s.RecoveryNotBefore, s.RecoveryExpiresAt);
    }
}
