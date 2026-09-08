using System;

namespace CriticalShift.Application
{
    // Worker-facing entrypoints share WorldSession's existing epoch, clock, revision and reentrancy guard.
    // WorkerWorkflow contains the use cases; this file does not own a second world or custody store.
    public sealed partial class WorldSession
    {
        public int WorkerCount => _workers.Count;
        public WorkerView? GetWorker(Guid actorId) => _workers.Get(actorId);
        public SessionTraceView Trace => _diagnostics.View;

        /// <summary>Trusted, ordered host observations; this is not an unauthenticated client damage API.</summary>
        public WorkerReply ApplyWorkerImpact(Guid epoch, Guid actorId, long observationSequence,
            WorkerImpact severity, long recoveryDelayMilliseconds, Guid hazardId, Guid causeId) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.Impact, observationSequence, false,
                () => _workers.Impact(_interaction, actorId, observationSequence, severity,
                    recoveryDelayMilliseconds, _timeline.ElapsedMilliseconds, hazardId, causeId), hazardId, causeId, severity);

        public WorkerReply StabilizeWorker(Guid epoch, Guid actorId, long expectedRevision, long delayMilliseconds) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.Aid, expectedRevision, false,
                () => _workers.Stabilize(actorId, expectedRevision, delayMilliseconds, _timeline.ElapsedMilliseconds));

        public WorkerReply SetWorkerEnvironment(Guid epoch, Guid actorId, long expectedRevision,
            WorkerSuit suit, int contamination) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.Environment, expectedRevision, false,
                () => _workers.Environment(actorId, expectedRevision, suit, contamination));

        public WorkerReply BeginWorkerRecovery(Guid epoch, Guid actorId, long episode, long expectedRevision) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.RecoveryRequested, episode, false,
                () => _workers.Begin(actorId, episode, expectedRevision, _timeline.ElapsedMilliseconds));

        public WorkerReply CompleteWorkerRecovery(Guid epoch, Guid actorId, long attempt) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.RecoveryResolved, attempt, false,
                () => _workers.Resolve(actorId, attempt, false));

        public WorkerReply CancelWorkerRecovery(Guid epoch, Guid actorId, long attempt) =>
            ExecuteWorker(epoch, actorId, SessionTraceKind.RecoveryCancelled, attempt, true,
                () => _workers.Resolve(actorId, attempt, true));

        private WorkerReply ExecuteWorker(Guid epoch, Guid actor, SessionTraceKind kind, long input,
            bool allowPaused, Func<WorkerReply> operation, Guid hazardId = default, Guid causeId = default, WorkerImpact? severity = null)
        {
            RequireIdle();
            long? before = _workers.Get(actor)?.Revision;
            WorkerReply reply;
            var status = Readiness(epoch);
            if (status.HasValue)
            {
                var rejected = status.Value switch
                {
                    WorldControlStatus.WrongEpoch => WorkerStatus.WrongEpoch,
                    WorldControlStatus.NotReady => WorkerStatus.NotReady,
                    WorldControlStatus.Ended => WorkerStatus.WorldEnded,
                    WorldControlStatus.Stopped => WorkerStatus.WorldStopped,
                    WorldControlStatus.Faulted => WorkerStatus.WorldFaulted,
                    _ => throw new InvalidOperationException("Unmapped world readiness.")
                };
                reply = new WorkerReply(rejected);
            }
            else if (!allowPaused && View.Phase == WorldPhase.Paused) reply = new WorkerReply(WorkerStatus.Paused);
            else
            {
                long next = NextRevision();
                _executing = true;
                try { reply = operation(); if (reply.Changed) _revision = next; }
                catch { FailClosed(); throw; }
                finally { _executing = false; }
            }
            _diagnostics.Append(View, epoch, kind, actor, reply.ReleasedClaim?.EntityId ?? Guid.Empty,
                input, reply.Changed, worker: reply, previousWorkerRevision: before, hazardId: hazardId, causeId: causeId, severity: severity);
            return reply;
        }
    }
}
