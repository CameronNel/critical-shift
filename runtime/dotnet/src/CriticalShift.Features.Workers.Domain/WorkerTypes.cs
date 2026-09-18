using System;

namespace CriticalShift.Features.Workers.Domain
{
    public enum Consciousness { Alert, Unconscious }
    public enum Posture { Upright, Down, Recovering }
    public enum SuitCondition { None, Intact, Compromised }
    public enum ImpactSeverity { Knockdown, Incapacitating }
    public enum WorkerResult
    {
        Applied, Duplicate, InvalidInput, SequenceGap, TooOld, PayloadMismatch,
        RevisionConflict, StaleRecovery, TooEarly, RequiresAid, InvalidState, ClearanceBlocked, RecoveryExpired, SourceCapacityReached
    }

    /// <summary>Detached worker facts; possession and physical pose are intentionally absent.</summary>
    public sealed class WorkerSnapshot
    {
        internal WorkerSnapshot(Guid id, long revision, Consciousness consciousness, Posture posture,
            SuitCondition suit, int contamination, long impact, long episode, long attempt, long readyAt, long attemptExpiresAt, Guid hazardId, Guid causeId)
        {
            LastHazardId = hazardId; LastCauseId = causeId;
            Id = id; Revision = revision; Consciousness = consciousness; Posture = posture;
            Suit = suit; Contamination = contamination; LastImpactSequence = impact;
            RecoveryEpisode = episode; RecoveryAttempt = attempt; RecoveryNotBefore = readyAt; RecoveryExpiresAt = attemptExpiresAt;
        }
        public Guid Id { get; }
        public long Revision { get; }
        public Consciousness Consciousness { get; }
        public Posture Posture { get; }
        public SuitCondition Suit { get; }
        public int Contamination { get; }
        public long LastImpactSequence { get; }
        public Guid LastHazardId { get; }
        public Guid LastCauseId { get; }
        public long RecoveryEpisode { get; }
        public long RecoveryAttempt { get; }
        public long RecoveryNotBefore { get; }
        public long RecoveryExpiresAt { get; }
        public bool CanInteract => Consciousness == Consciousness.Alert && Posture == Posture.Upright;
    }
}
