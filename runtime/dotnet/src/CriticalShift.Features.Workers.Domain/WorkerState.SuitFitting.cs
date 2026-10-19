#nullable enable
using System;

namespace CriticalShift.Features.Workers.Domain
{
    public sealed class SuitFittingRules
    {
        public SuitFittingRules(long durationMilliseconds = 20000, long removalDurationMilliseconds = 5000)
        {
            if (durationMilliseconds < 15000 || durationMilliseconds > 30000)
                throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            if (removalDurationMilliseconds < 1000 || removalDurationMilliseconds > 15000)
                throw new ArgumentOutOfRangeException(nameof(removalDurationMilliseconds));
            DurationMilliseconds = durationMilliseconds; RemovalDurationMilliseconds = removalDurationMilliseconds;
        }
        public long DurationMilliseconds { get; }
        public long RemovalDurationMilliseconds { get; }
    }
    public sealed class SuitFittingAttempt
    {
        internal SuitFittingAttempt(Guid id, Guid station, long start, long due, SuitCondition original, SuitCondition target)
        { Id = id; StationId = station; StartedAtMilliseconds = start; DueAtMilliseconds = due; OriginalSuit = original; TargetSuit = target; }
        public Guid Id { get; }
        public Guid StationId { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public SuitCondition OriginalSuit { get; }
        public SuitCondition TargetSuit { get; }
    }
    public sealed partial class WorkerState
    {
        private SuitFittingAttempt? _fitting;
        public WorkerResult BeginSuitFitting(long expectedRevision, Guid station, Guid attempt, SuitFittingRules rules, long now, SuitCondition target = SuitCondition.Intact)
        {
            if (expectedRevision != _revision) return WorkerResult.RevisionConflict;
            if (station == Guid.Empty || attempt == Guid.Empty || rules == null || now < _lastTime ||
                (target != SuitCondition.Intact && target != SuitCondition.None)) return WorkerResult.InvalidInput;
            long duration = target == SuitCondition.None ? rules.RemovalDurationMilliseconds : rules.DurationMilliseconds;
            if (now > long.MaxValue - duration) return WorkerResult.InvalidInput;
            if (!Snapshot.CanInteract) return WorkerResult.InvalidState;
            if (_suit == target) return WorkerResult.NoChange;
            var next = new SuitFittingAttempt(attempt, station, now, now + duration, _suit, target);
            long revision = checked(_revision + 1);
            _fitting = next; _lastTime = now; _revision = revision; return WorkerResult.Applied;
        }
        public WorkerResult CancelSuitFitting(Guid attempt)
        {
            if (_fitting == null || attempt != _fitting.Id) return WorkerResult.InvalidState;
            long revision = checked(_revision + 1);
            _fitting = null; _revision = revision; return WorkerResult.Applied;
        }
        public WorkerResult CompleteSuitFitting(Guid attempt, long now)
        {
            if (_fitting == null || attempt != _fitting.Id || !Snapshot.PhysicallyUpright || _suit != _fitting.OriginalSuit)
                return WorkerResult.InvalidState;
            if (now != _fitting.DueAtMilliseconds || now < _lastTime) return WorkerResult.InvalidInput;
            long revision = checked(_revision + 1);
            _suit = _fitting.TargetSuit; _fitting = null; _revision = revision; _lastTime = now;
            return WorkerResult.Applied;
        }
    }
}
