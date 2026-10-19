#nullable enable
using System;

namespace CriticalShift.Application
{
    public enum InteractionKind { Grab, Release, Renew, Production, Reactor, Door, Medical, MedicalEgress }
    public enum AccessDecision { Allowed, OutOfReach, ActorUnavailable, TargetUnavailable }
    public enum InteractionStatus
    {
        Applied, NoChange, NotReady, WorldStopped, WorldFaulted, WrongEpoch,
        UnknownConnection, InvalidPayload, SequenceGap, TooOld, PayloadMismatch,
        OutOfReach, ActorUnavailable, TargetUnavailable, UnknownEntity, EntityRetired,
        AlreadyClaimed, ActorAlreadyHolding, NotHolder, StaleLease, RevisionConflict, EntitySlotted, UnknownSlot, SlotOccupied, SlotEmpty, ProductionRejected, ReactorRejected, DoorRejected, MedicalRejected
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
            long expectedRevision = 0, long leaseGeneration = 0, ProductionRequest? production = null, ReactorRequest? reactor = null, DoorRequest? door = null, MedicalRequest? medical = null)
        {
            Epoch = epoch;
            Sequence = sequence;
            Kind = kind;
            EntityId = entityId;
            ExpectedRevision = expectedRevision;
            LeaseGeneration = leaseGeneration; Production = production; Reactor = reactor; Door = door; Medical = medical;
        }

        public Guid Epoch { get; }
        public long Sequence { get; }
        public InteractionKind Kind { get; }
        public Guid EntityId { get; }
        public long ExpectedRevision { get; }
        public long LeaseGeneration { get; }
        public ProductionRequest? Production { get; }
        public ReactorRequest? Reactor { get; }
        public DoorRequest? Door { get; }
        public MedicalRequest? Medical { get; }

        internal bool IsWellFormed
        {
            get
            {
                if (Sequence <= 0 || EntityId == Guid.Empty) return false;
                bool headerEmpty = ExpectedRevision == 0 && LeaseGeneration == 0;
                switch (Kind)
                {
                    case InteractionKind.Medical: return headerEmpty && Medical != null && Medical.IsWellFormed && Medical.Action != MedicalAction.EmergencyEject && Door == null && Reactor == null && Production == null;
                    case InteractionKind.MedicalEgress: return headerEmpty && Medical != null && Medical.IsWellFormed && Medical.Action == MedicalAction.EmergencyEject && Door == null && Reactor == null && Production == null;
                    case InteractionKind.Door: return headerEmpty && Door?.IsWellFormed == true && Medical == null && Reactor == null && Production == null;
                    case InteractionKind.Reactor: return headerEmpty && Reactor?.IsWellFormed == true && Medical == null && Door == null && Production == null;
                    case InteractionKind.Production: return headerEmpty && Production?.IsWellFormed == true && Medical == null && Door == null && Reactor == null;
                    case InteractionKind.Grab: return Medical == null && Door == null && Reactor == null && Production == null && ExpectedRevision >= 0 && LeaseGeneration == 0;
                    case InteractionKind.Release:
                    case InteractionKind.Renew: return Medical == null && Door == null && Reactor == null && Production == null && ExpectedRevision == 0 && LeaseGeneration > 0;
                    default: return false;
                }
            }
        }

        internal bool SamePayload(InteractionCommand other) => Epoch == other.Epoch &&
            Sequence == other.Sequence && Kind == other.Kind && EntityId == other.EntityId &&
            ExpectedRevision == other.ExpectedRevision && LeaseGeneration == other.LeaseGeneration &&
            (Production == null ? other.Production == null : other.Production != null && Production.Same(other.Production)) &&
            (Reactor == null ? other.Reactor == null : other.Reactor != null && Reactor.Same(other.Reactor)) &&
            (Door == null ? other.Door == null : other.Door != null && Door.Same(other.Door)) &&
            (Medical == null ? other.Medical == null : other.Medical != null && Medical.Same(other.Medical));
    }

    /// <summary>Detached application projection; never exposes the live domain owner.</summary>
    public sealed class ObjectClaimView
    {
        internal ObjectClaimView(Guid epoch, Guid entityId, Guid? holderId, long revision,
            long leaseGeneration, long expiresAtMilliseconds, bool retired, Guid? slotId = null)
        {
            Epoch = epoch;
            EntityId = entityId;
            HolderId = holderId;
            Revision = revision;
            LeaseGeneration = leaseGeneration;
            ExpiresAtMilliseconds = expiresAtMilliseconds;
            IsRetired = retired; SlotId = slotId;
        }

        public Guid Epoch { get; }
        public Guid EntityId { get; }
        public Guid? HolderId { get; }
        public Guid? SlotId { get; }
        public long Revision { get; }
        public long LeaseGeneration { get; }
        public long ExpiresAtMilliseconds { get; }
        public bool IsRetired { get; }
    }

    public sealed class InteractionReply
    {
        internal InteractionReply(InteractionStatus status, bool terminal, ObjectClaimView? state = null, bool replay = false, ProductionReply? production = null, ReactorReply? reactor = null, DoorReply? door = null, MedicalReply? medical = null)
        {
            Status = status;
            IsTerminal = terminal;
            State = state;
            IsReplay = replay; Production = production; Reactor = reactor; Door = door; Medical = medical;
        }

        public InteractionStatus Status { get; }
        public bool IsTerminal { get; }
        public ObjectClaimView? State { get; }
        public bool IsReplay { get; }
        public ProductionReply? Production { get; }
        public ReactorReply? Reactor { get; }
        public DoorReply? Door { get; }
        public MedicalReply? Medical { get; }
        public bool Accepted => Status == InteractionStatus.Applied || Status == InteractionStatus.NoChange;
        // Only this flag may trigger a new binding side effect. Replayed acceptance is historical.
        public bool HasNewCommit => Status == InteractionStatus.Applied && !IsReplay;
        internal InteractionReply AsReplay() => new InteractionReply(Status, IsTerminal, State, true, Production, Reactor, Door, Medical);
    }
}
