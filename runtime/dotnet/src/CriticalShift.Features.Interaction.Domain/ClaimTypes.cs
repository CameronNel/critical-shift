using System;

namespace CriticalShift.Features.Interaction.Domain
{
    public enum ClaimError
    {
        None,
        UnknownEntity,
        EntityRetired,
        AlreadyClaimed,
        ActorAlreadyHolding,
        NotHolder,
        StaleLease,
        RevisionConflict,
        StoreStopped
    }

    /// <summary>Detached logical state. A holder does not imply a successful physics attachment.</summary>
    public sealed class ClaimSnapshot
    {
        internal ClaimSnapshot(Guid entityId, Guid? holderId, long revision, long generation,
            long expiresAtMilliseconds, bool retired)
        {
            EntityId = entityId;
            HolderId = holderId;
            Revision = revision;
            LeaseGeneration = generation;
            ExpiresAtMilliseconds = expiresAtMilliseconds;
            IsRetired = retired;
        }

        public Guid EntityId { get; }
        public Guid? HolderId { get; }
        public long Revision { get; }
        public long LeaseGeneration { get; }
        public long ExpiresAtMilliseconds { get; }
        public bool IsRetired { get; }
    }

    public sealed class ClaimResult
    {
        internal ClaimResult(ClaimError error, ClaimSnapshot? snapshot, bool changed = false)
        {
            Error = error;
            Snapshot = snapshot;
            Changed = changed;
        }

        public ClaimError Error { get; }
        public ClaimSnapshot? Snapshot { get; }
        public bool Accepted => Error == ClaimError.None;
        public bool Changed { get; }
    }
}
