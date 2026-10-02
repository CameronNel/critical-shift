using System;

namespace CriticalShift.Application
{
    public enum InteractionKind { Grab, Release, Renew, Production, Reactor, Control, Assist, GripHandle }
    public enum AccessDecision { Allowed, OutOfReach, ActorUnavailable, TargetUnavailable }
    public enum InteractionStatus
    {
        Applied, NoChange, NotReady, WorldStopped, WorldFaulted, WrongEpoch,
        UnknownConnection, InvalidPayload, SequenceGap, TooOld, PayloadMismatch,
        OutOfReach, ActorUnavailable, TargetUnavailable, UnknownEntity, EntityRetired,
        AlreadyClaimed, ActorAlreadyHolding, NotHolder, StaleLease, RevisionConflict, EntitySlotted, UnknownSlot, SlotOccupied, SlotEmpty, ProductionRejected, ReactorRejected, AssistanceDisabled
    }

    /// <summary>
    /// Trusted host observation boundary, not a client assertion. Must be side-effect-free.
    /// There is deliberately no permissive default implementation.
    /// </summary>
    public interface IInteractionAccessPolicy
    {
        AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind);
    }

    /// <summary>Immutable intent. Sender identity is resolved from a registered connection, not this payload.</summary>
    public sealed class InteractionCommand
    {
        public InteractionCommand(Guid epoch, long sequence, InteractionKind kind, Guid entityId,
            long expectedRevision = 0, long leaseGeneration = 0, ProductionRequest? production = null, ReactorRequest? reactor = null, ControlRequest? control = null)
        {
            Epoch = epoch;
            Sequence = sequence;
            Kind = kind;
            EntityId = entityId;
            ExpectedRevision = expectedRevision;
            LeaseGeneration = leaseGeneration; Production = production; Reactor = reactor; Control = control;
        }

        public Guid Epoch { get; }
        public long Sequence { get; }
        public InteractionKind Kind { get; }
        public Guid EntityId { get; }
        public long ExpectedRevision { get; }
        public long LeaseGeneration { get; }
        public ProductionRequest? Production { get; }
        public ReactorRequest? Reactor { get; }
        public ControlRequest? Control { get; }

        internal bool IsWellFormed => Sequence > 0 && EntityId != Guid.Empty &&
            (Kind == InteractionKind.Control ? Control != null && Control.IsWellFormed && Reactor == null && Production == null && ExpectedRevision == 0 && LeaseGeneration == 0 :
             Control == null && (Kind == InteractionKind.Reactor ? Reactor != null && Reactor.IsWellFormed && Production == null && ExpectedRevision == 0 && LeaseGeneration == 0 :
             Reactor == null && (Kind == InteractionKind.Production ? Production != null && Production.IsWellFormed && ExpectedRevision == 0 && LeaseGeneration == 0 :
             Production == null && ((Kind == InteractionKind.Grab || Kind == InteractionKind.GripHandle) ? ExpectedRevision >= 0 && LeaseGeneration == 0 :
             Kind == InteractionKind.Assist ? ExpectedRevision >= 0 && LeaseGeneration > 0 :
             (Kind == InteractionKind.Release || Kind == InteractionKind.Renew) && ExpectedRevision == 0 && LeaseGeneration > 0))));

        internal bool SamePayload(InteractionCommand other) => Epoch == other.Epoch &&
            Sequence == other.Sequence && Kind == other.Kind && EntityId == other.EntityId &&
            ExpectedRevision == other.ExpectedRevision && LeaseGeneration == other.LeaseGeneration &&
            (Production == null ? other.Production == null : other.Production != null && Production.Same(other.Production)) &&
            (Reactor == null ? other.Reactor == null : other.Reactor != null && Reactor.Same(other.Reactor)) &&
            (Control == null ? other.Control == null : other.Control != null && Control.Same(other.Control));
    }

    /// <summary>Detached application projection; never exposes the live domain owner.</summary>
    public sealed class ObjectClaimView
    {
        internal ObjectClaimView(Guid epoch, Guid entityId, Guid? holderId, long revision,
            long leaseGeneration, long expiresAtMilliseconds, bool retired, Guid? slotId = null, Guid? assistantId = null)
        {
            Epoch = epoch;
            EntityId = entityId;
            HolderId = holderId;
            Revision = revision;
            LeaseGeneration = leaseGeneration;
            ExpiresAtMilliseconds = expiresAtMilliseconds;
            IsRetired = retired; SlotId = slotId; AssistantId = assistantId;
        }

        public Guid Epoch { get; }
        public Guid EntityId { get; }
        public Guid? HolderId { get; }
        public Guid? SlotId { get; }
        public Guid? AssistantId { get; }
        public long Revision { get; }
        public long LeaseGeneration { get; }
        public long ExpiresAtMilliseconds { get; }
        public bool IsRetired { get; }
    }

    public sealed class InteractionReply
    {
        internal InteractionReply(InteractionStatus status, bool terminal, ObjectClaimView? state = null, bool replay = false, ProductionReply? production = null, ReactorReply? reactor = null, ControlView? control = null)
        {
            Status = status;
            IsTerminal = terminal;
            State = state;
            IsReplay = replay; Production = production; Reactor = reactor; Control = control;
        }

        public InteractionStatus Status { get; }
        public bool IsTerminal { get; }
        public ObjectClaimView? State { get; }
        public bool IsReplay { get; }
        public ProductionReply? Production { get; }
        public ReactorReply? Reactor { get; }
        public ControlView? Control { get; }
        public bool Accepted => Status == InteractionStatus.Applied || Status == InteractionStatus.NoChange;
        // Only this flag may trigger a new binding side effect. Replayed acceptance is historical.
        public bool HasNewCommit => Status == InteractionStatus.Applied && !IsReplay;
        internal InteractionReply AsReplay() => new InteractionReply(Status, IsTerminal, State, true, Production, Reactor, Control);
    }
}
