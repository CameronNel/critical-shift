#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public enum DoorState { Closed, Open, Locked }
    public enum DoorAction { Open, Close }
    public enum DoorStatus { Applied, NoChange, UnknownDoor, RevisionConflict, Locked, NotOperable }
    public enum DoorEvacuationStatus { Applied, Duplicate, AlreadyActive, InvalidCause, WrongEpoch, NotReady, WorldEnded, WorldStopped, WorldFaulted, Paused }

    public sealed class DoorRequest
    {
        public const int CurrentVersion = 1;
        public DoorRequest(DoorAction action, long doorRevision, int version = CurrentVersion)
        { Action = action; DoorRevision = doorRevision; Version = version; }
        public DoorAction Action { get; }
        public long DoorRevision { get; }
        public int Version { get; }
        internal bool IsWellFormed => Version == CurrentVersion && DoorRevision >= 0 && (Action == DoorAction.Open || Action == DoorAction.Close);
        internal bool Same(DoorRequest other) => Action == other.Action && DoorRevision == other.DoorRevision && Version == other.Version;
    }
    public sealed class DoorView
    {
        internal DoorView(Guid epoch, Guid id, string sourceId, long revision, DoorState state, DoorState evacuationState, bool playerOperable)
        { Epoch = epoch; Id = id; SourceId = sourceId; Revision = revision; State = state; EvacuationState = evacuationState; PlayerOperable = playerOperable; }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public string SourceId { get; }
        public long Revision { get; }
        public DoorState State { get; }
        public DoorState EvacuationState { get; }
        public bool PlayerOperable { get; }
    }
    public sealed class DoorReply
    {
        internal DoorReply(DoorStatus status, DoorView? door, DoorAction? action = null, long? previousRevision = null, Guid causeId = default)
        { Status = status; Door = door; Action = action; PreviousRevision = previousRevision; CauseId = causeId; }
        public DoorStatus Status { get; }
        public DoorView? Door { get; }
        public DoorAction? Action { get; }
        public long? PreviousRevision { get; }
        public Guid CauseId { get; }
    }
    public sealed class DoorEvacuationReply
    {
        internal DoorEvacuationReply(DoorEvacuationStatus status, Guid causeId, IReadOnlyList<DoorView>? changes = null)
        { Status = status; CauseId = causeId; Changes = changes ?? Array.Empty<DoorView>(); }
        public DoorEvacuationStatus Status { get; }
        public Guid CauseId { get; }
        public bool Changed => Status == DoorEvacuationStatus.Applied;
        public IReadOnlyList<DoorView> Changes { get; }
    }
}
