#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    /// <summary>Authored station access and coordination. Each WorkerState owns its condition and pending attempt.</summary>
    public sealed class SuitFittingOperations
    {
        private readonly WorldSession world;
        private readonly WorkerWorkflow workers;
        private readonly InteractionWorld interaction;
        private readonly IInteractionAccessPolicy access;
        private readonly Dictionary<Guid, SuitFittingDefinition> stations = new Dictionary<Guid, SuitFittingDefinition>();
        private long started, completed, cancelled, interrupted;
        private SuitFittingSummary? terminal;
        internal SuitFittingOperations(WorldSession owner, WorkerWorkflow conditions, InteractionWorld custody, IInteractionAccessPolicy observations)
        { world = owner; workers = conditions; interaction = custody; access = observations; }
        public SuitFittingSummary Summary => terminal ?? new SuitFittingSummary(started, completed, cancelled, interrupted, PendingCount);
        public int StationCount => stations.Count;
        public void Register(Guid station, SuitFittingDefinition definition) => world.RegisterProduction(() =>
        {
            if (definition == null || station == Guid.Empty) throw new ArgumentException("Bind an authored suit station.");
            if (stations.Count >= 8 || stations.ContainsKey(station)) throw new InvalidOperationException("Suit stations must be unique and bounded.");
            interaction.RegisterProductionSlot(station); stations.Add(station, definition);
        });
        private int PendingCount
        { get { int count = 0; foreach (var worker in workers.Snapshot()) if (worker.SuitFitting != null) count++; return count; } }
        internal long NextBoundary
        {
            get
            {
                long next = long.MaxValue;
                foreach (var worker in workers.Snapshot()) if (worker.SuitFitting != null) next = Math.Min(next, worker.SuitFitting.DueAtMilliseconds);
                return next;
            }
        }
        internal InteractionReply Apply(Guid actor, Guid station, SuitFittingRequest request)
        {
            var worker = workers.Get(actor);
            if (!stations.TryGetValue(station, out var definition)) return Reply(SuitFittingStatus.UnknownStation, worker);
            if (worker == null) return Reply(SuitFittingStatus.InvalidWorker, worker);
            if (request.Action == SuitFittingAction.Cancel)
            {
                var attempt = worker.SuitFitting;
                if (attempt == null || attempt.Id != request.AttemptId || attempt.StationId != station)
                    return Reply(SuitFittingStatus.StaleAttempt, worker);
                long count = checked(cancelled + 1);
                var result = workers.CancelSuitFitting(actor, attempt.Id);
                if (result.Status != WorkerStatus.Applied) throw new InvalidOperationException("Prepared fitting cancellation failed.");
                cancelled = count;
                return Reply(SuitFittingStatus.Applied, result.Worker, new SuitFittingChange(SuitFittingEvent.Cancelled, result.Worker!, attempt, world.View.ElapsedMilliseconds));
            }
            if (worker.Revision != request.WorkerRevision) return Reply(SuitFittingStatus.RevisionConflict, worker);
            if (!worker.CanInteract) return Reply(SuitFittingStatus.InvalidWorker, worker);
            if (worker.Suit == WorkerSuit.Intact) return Reply(SuitFittingStatus.NoChange, worker);
            if (interaction.ActorHasClaim(actor)) return Reply(SuitFittingStatus.HandsOccupied, worker);
            foreach (var other in workers.Snapshot())
                if (other.SuitFitting?.StationId == station) return Reply(SuitFittingStatus.StationOccupied, worker);
            long now = world.View.ElapsedMilliseconds;
            if (now > long.MaxValue - definition.DurationMilliseconds) return Reply(SuitFittingStatus.InvalidTime, worker);
            long starts = checked(started + 1);
            var begin = workers.BeginSuitFitting(actor, request.WorkerRevision, station, Guid.NewGuid(), definition.Rules, now);
            if (begin.Status != WorkerStatus.Applied) throw new InvalidOperationException("Prepared fitting start failed.");
            started = starts;
            return Reply(SuitFittingStatus.Applied, begin.Worker, new SuitFittingChange(SuitFittingEvent.Started, begin.Worker!, begin.Worker!.SuitFitting!, now));
        }
        internal IReadOnlyList<SuitFittingChange> SampleAccessAt(long at)
        {
            var changes = new List<SuitFittingChange>();
            foreach (var worker in workers.Snapshot())
            {
                var attempt = worker.SuitFitting; if (attempt == null) continue;
                // Current spatial observations have no historical timestamp. Sample once at
                // this poll's projected coordinate, before settling any skipped boundaries.
                // The original policy excludes RunningAccess's intentional busy-work guard.
                var observation = access.Evaluate(worker.Id, attempt.StationId, InteractionKind.SuitFitting);
                if (!Enum.IsDefined(typeof(AccessDecision), observation)) throw new InvalidOperationException("Invalid suit station observation.");
                if (!Eligible(worker, attempt) || observation != AccessDecision.Allowed)
                    changes.Add(Interrupt(worker, attempt, at));
            }
            return changes.AsReadOnly();
        }
        private bool Eligible(WorkerView worker, SuitFittingAttemptView attempt) =>
            stations.ContainsKey(attempt.StationId) && worker.PhysicallyUpright && worker.Suit == attempt.OriginalSuit &&
            !interaction.ActorHasClaim(worker.Id);
        internal IReadOnlyList<SuitFittingChange> AdvanceTo(long at)
        {
            var changes = new List<SuitFittingChange>();
            foreach (var worker in workers.Snapshot())
            {
                var attempt = worker.SuitFitting; if (attempt == null) continue;
                if (attempt.DueAtMilliseconds < at) throw new InvalidOperationException("World settlement skipped a required suit-fitting boundary.");
                if (!Eligible(worker, attempt)) { changes.Add(Interrupt(worker, attempt, at)); continue; }
                if (at < attempt.DueAtMilliseconds) continue;
                long count = checked(completed + 1);
                var done = workers.CompleteSuitFitting(worker.Id, attempt.Id, at);
                if (done.Status != WorkerStatus.Applied) throw new InvalidOperationException("Prepared suit fitting completion failed.");
                completed = count; changes.Add(new SuitFittingChange(SuitFittingEvent.Completed, done.Worker!, attempt, at));
            }
            return changes.AsReadOnly();
        }
        private SuitFittingChange Interrupt(WorkerView worker, SuitFittingAttemptView attempt, long at)
        {
            long count = checked(interrupted + 1); var result = workers.CancelSuitFitting(worker.Id, attempt.Id);
            if (result.Status != WorkerStatus.Applied) throw new InvalidOperationException("Prepared fitting interruption failed.");
            interrupted = count; return new SuitFittingChange(SuitFittingEvent.Interrupted, result.Worker!, attempt, at);
        }
        internal SuitFittingChange? ObserveConditionChange(Guid actor, SuitFittingAttemptView? previous, long at)
        {
            var worker = workers.Get(actor);
            if (previous == null || worker == null || worker.SuitFitting != null) return null;
            long count = checked(interrupted + 1); interrupted = count;
            return new SuitFittingChange(SuitFittingEvent.Interrupted, worker, previous, at);
        }
        internal SuitFittingChange? Disconnect(Guid actor)
        {
            var worker = workers.Get(actor);
            return worker?.SuitFitting == null ? null : Interrupt(worker, worker.SuitFitting, world.View.ElapsedMilliseconds);
        }
        internal void Close()
        {
            if (terminal != null) return;
            // These are historical cutoff facts. Do not invoke checked gameplay cancellation during fault cleanup.
            int pending = PendingCount; bool overflow = cancelled > long.MaxValue - pending;
            terminal = new SuitFittingSummary(started, completed, overflow ? long.MaxValue : cancelled + pending, interrupted, 0, overflow);
            stations.Clear();
        }
        private static InteractionReply Reply(SuitFittingStatus status, WorkerView? worker, SuitFittingChange? change = null) =>
            new InteractionReply(status == SuitFittingStatus.Applied ? InteractionStatus.Applied :
                status == SuitFittingStatus.NoChange ? InteractionStatus.NoChange : InteractionStatus.SuitFittingRejected,
                true, suitFitting: new SuitFittingReply(status, worker, change));
    }
}
