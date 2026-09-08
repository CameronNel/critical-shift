using System;

namespace CriticalShift.Features.Workers.Domain
{
    /// <summary>
    /// One worker's conditions and recovery protocol. The caller supplies shift milliseconds;
    /// these deadlines do not depend on delivery of advisory timer notifications.
    /// </summary>
    public sealed class WorkerState
    {
        private readonly Guid _id;
        private readonly long _completionWindow;
        private long _attemptExpiresAt;
        private long _revision, _impact, _episode, _attempt, _readyAt, _lastTime;
        private long _lastImpactDelay, _beginRevision;
        private ImpactSeverity _lastSeverity;
        private Consciousness _consciousness;
        private Posture _posture;
        private SuitCondition _suit;
        private int _contamination;

        public WorkerState(Guid id, long completionWindowMilliseconds = 5000)
        {
            if (id == Guid.Empty) throw new ArgumentException("Worker identity is required.", nameof(id));
            if (completionWindowMilliseconds < 1 || completionWindowMilliseconds > 60000)
                throw new ArgumentOutOfRangeException(nameof(completionWindowMilliseconds));
            _id = id; _completionWindow = completionWindowMilliseconds;
        }

        public WorkerSnapshot Snapshot => new WorkerSnapshot(_id, _revision, _consciousness, _posture,
            _suit, _contamination, _impact, _episode, _attempt, _readyAt, _attemptExpiresAt);

        public WorkerResult Impact(long sequence, ImpactSeverity severity, long recoveryDelay, long shiftTime)
        {
            if (sequence < 1 || sequence == long.MaxValue || recoveryDelay < 0 ||
                (severity != ImpactSeverity.Knockdown && severity != ImpactSeverity.Incapacitating) || shiftTime < _lastTime)
                return WorkerResult.InvalidInput;
            if (sequence == _impact)
                return severity == _lastSeverity && recoveryDelay == _lastImpactDelay ?
                    WorkerResult.Duplicate : WorkerResult.PayloadMismatch;
            if (sequence < _impact) return WorkerResult.TooOld;
            if (sequence != _impact + 1) return WorkerResult.SequenceGap;
            // Validate arithmetic before mutation, including when the impact interrupts recovery.
            if (recoveryDelay > long.MaxValue - shiftTime) return WorkerResult.InvalidInput;
            long revision = checked(_revision + 1), episode = checked(_episode + 1);
            _readyAt = shiftTime + recoveryDelay;
            if (severity == ImpactSeverity.Incapacitating) _consciousness = Consciousness.Unconscious;
            // A mild impact cannot cure an unconscious worker.
            _posture = Posture.Down; _attemptExpiresAt = 0; _episode = episode; _revision = revision; _lastTime = shiftTime;
            _impact = sequence; _lastSeverity = severity; _lastImpactDelay = recoveryDelay;
            return WorkerResult.Applied;
        }

        /// <summary>Validated external aid only; no resource cost or reanimation mechanics are invented here.</summary>
        public WorkerResult Stabilize(long expectedRevision, long recoveryDelay, long shiftTime)
        {
            if (expectedRevision != _revision) return WorkerResult.RevisionConflict;
            if (_consciousness != Consciousness.Unconscious || _posture != Posture.Down) return WorkerResult.InvalidState;
            if (shiftTime < _lastTime || recoveryDelay < 0 || recoveryDelay > long.MaxValue - shiftTime)
                return WorkerResult.InvalidInput;
            long revision = checked(_revision + 1), episode = checked(_episode + 1);
            _consciousness = Consciousness.Alert; _readyAt = shiftTime + recoveryDelay;
            _lastTime = shiftTime; _revision = revision; _episode = episode;
            return WorkerResult.Applied;
        }

        public WorkerResult SetEnvironment(long expectedRevision, SuitCondition suit, int contamination)
        {
            if (expectedRevision != _revision) return WorkerResult.RevisionConflict;
            if ((suit != SuitCondition.None && suit != SuitCondition.Intact && suit != SuitCondition.Compromised) ||
                contamination < 0 || contamination > 100) return WorkerResult.InvalidInput;
            if (_suit == suit && _contamination == contamination) return WorkerResult.Duplicate;
            long revision = checked(_revision + 1);
            _suit = suit; _contamination = contamination; _revision = revision;
            return WorkerResult.Applied;
        }

        public WorkerResult BeginRecovery(long episode, long expectedRevision, long shiftTime)
        {
            if (episode <= 0 || episode != _episode) return WorkerResult.StaleRecovery;
            if (shiftTime < _lastTime) return WorkerResult.InvalidInput;
            if (_consciousness != Consciousness.Alert) return WorkerResult.RequiresAid;
            if (_posture == Posture.Recovering && expectedRevision == _beginRevision) return WorkerResult.Duplicate;
            if (expectedRevision != _revision) return WorkerResult.RevisionConflict;
            if (_posture != Posture.Down) return WorkerResult.InvalidState;
            if (shiftTime < _readyAt) return WorkerResult.TooEarly;
            if (_completionWindow > long.MaxValue - shiftTime) return WorkerResult.InvalidInput;
            long revision = checked(_revision + 1), attempt = checked(_attempt + 1);
            _attemptExpiresAt = shiftTime + _completionWindow;
            _beginRevision = expectedRevision; _posture = Posture.Recovering; _attempt = attempt; _lastTime = shiftTime; _revision = revision;
            return WorkerResult.Applied;
        }

        public WorkerResult ExpireRecovery(long shiftTime)
        {
            if (shiftTime < _lastTime) return WorkerResult.InvalidInput;
            if (_posture != Posture.Recovering || shiftTime < _attemptExpiresAt) return WorkerResult.Duplicate;
            long revision = checked(_revision + 1);
            _posture = Posture.Down; _attemptExpiresAt = 0; _lastTime = shiftTime; _revision = revision;
            return WorkerResult.RecoveryExpired;
        }

        public bool IsPending(long attempt) => attempt > 0 && attempt == _attempt &&
            _consciousness == Consciousness.Alert && _posture == Posture.Recovering;

        /// <summary>A trusted adapter confirms a usable pose. A negative answer returns to Down for retry.</summary>
        public WorkerResult ResolveRecovery(long attempt, bool clearanceConfirmed)
        {
            if (!IsPending(attempt)) return WorkerResult.StaleRecovery;
            long revision = checked(_revision + 1);
            _posture = clearanceConfirmed ? Posture.Upright : Posture.Down; _attemptExpiresAt = 0;
            _revision = revision;
            return clearanceConfirmed ? WorkerResult.Applied : WorkerResult.ClearanceBlocked;
        }
    }
}
