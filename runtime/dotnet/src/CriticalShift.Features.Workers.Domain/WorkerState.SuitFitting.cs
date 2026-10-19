#nullable enable
using System;

namespace CriticalShift.Features.Workers.Domain
{
    public sealed class SuitFittingRules
    {
        public SuitFittingRules(long durationMilliseconds = 20000)
        {
            if (durationMilliseconds < 15000 || durationMilliseconds > 30000)
                throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            DurationMilliseconds = durationMilliseconds;
        }
        public long DurationMilliseconds { get; }
    }
    public sealed class SuitFittingAttempt
    {
        internal SuitFittingAttempt(Guid id, Guid station, long start, long due, SuitCondition original)
        { Id = id; StationId = station; StartedAtMilliseconds = start; DueAtMilliseconds = due; OriginalSuit = original; }
        public Guid Id { get; }
        public Guid StationId { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public SuitCondition OriginalSuit { get; }
    }
    public sealed partial class WorkerState
    {
        private SuitFittingAttempt? _fitting;
        public WorkerResult BeginSuitFitting(long expectedRevision, Guid station, Guid attempt, SuitFittingRules rules, long now)
        {
            if (expectedRevision != _revision) return WorkerResult.RevisionConflict;
            if (station == Guid.Empty || attempt == Guid.Empty || rules == null || now < _lastTime ||
                now > long.MaxValue - rules.DurationMilliseconds) return WorkerResult.InvalidInput;
            if (!Snapshot.CanInteract) return WorkerResult.InvalidState;
            if (_suit == SuitCondition.Intact) return WorkerResult.NoChange;
            var next = new SuitFittingAttempt(attempt, station, now, now + rules.DurationMilliseconds, _suit);
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
            _suit = SuitCondition.Intact; _fitting = null; _revision = revision; _lastTime = now;
            return WorkerResult.Applied;
        }
    }
}
