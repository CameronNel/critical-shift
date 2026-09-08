using System;

namespace CriticalShift.Application
{
    public enum WorkerAwareness { Alert, Unconscious }
    public enum WorkerPose { Upright, Down, Recovering }
    public enum WorkerSuit { None, Intact, Compromised }
    public enum WorkerImpact { Knockdown, Incapacitating }
    public enum RecoveryClearance { Safe, Blocked, Unavailable }
    public enum WorkerStatus
    {
        Applied, Duplicate, InvalidInput, SequenceGap, TooOld, PayloadMismatch,
        RevisionConflict, StaleRecovery, TooEarly, RequiresAid, InvalidState,
        ClearanceBlocked, ClearanceUnavailable, Cancelled, RecoveryExpired, UnknownWorker,
        WrongEpoch, NotReady, Paused, WorldEnded, WorldStopped, WorldFaulted
    }

    /// <summary>
    /// Trusted physical-recovery observation boundary. No production default returns Safe.
    /// An adapter must check the actor, attempted placement and current world binding.
    /// </summary>
    public interface IWorkerRecoveryPolicy
    {
        RecoveryClearance Evaluate(Guid epoch, Guid workerId, long recoveryAttempt);
    }

    public sealed class WorkerView
    {
        internal WorkerView(Guid epoch, Guid id, long revision, WorkerAwareness awareness,
            WorkerPose pose, WorkerSuit suit, int contamination, long impact, long episode,
            long attempt, long recoveryNotBefore, long recoveryExpiresAt)
        {
            Epoch = epoch; Id = id; Revision = revision; Awareness = awareness;
            Pose = pose; Suit = suit; Contamination = contamination; LastImpactSequence = impact;
            RecoveryEpisode = episode; RecoveryAttempt = attempt; RecoveryNotBeforeMilliseconds = recoveryNotBefore; RecoveryExpiresAtMilliseconds = recoveryExpiresAt;
        }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public long Revision { get; }
        public WorkerAwareness Awareness { get; }
        public WorkerPose Pose { get; }
        public WorkerSuit Suit { get; }
        public int Contamination { get; }
        public long LastImpactSequence { get; }
        public long RecoveryEpisode { get; }
        public long RecoveryAttempt { get; }
        public long RecoveryNotBeforeMilliseconds { get; }
        public long RecoveryExpiresAtMilliseconds { get; }
        public bool CanInteract => Awareness == WorkerAwareness.Alert && Pose == WorkerPose.Upright;
    }

    public sealed class WorkerReply
    {
        internal WorkerReply(WorkerStatus status, bool changed = false, WorkerView? worker = null,
            ObjectClaimView? releasedClaim = null)
        { Status = status; Changed = changed; Worker = worker; ReleasedClaim = releasedClaim; }
        public WorkerStatus Status { get; }
        public bool Changed { get; }
        public WorkerView? Worker { get; }
        public ObjectClaimView? ReleasedClaim { get; }
    }
}
