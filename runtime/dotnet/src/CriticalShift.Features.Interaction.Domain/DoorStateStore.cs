#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Interaction.Domain
{
    public enum DoorMode { Closed, Open, Locked }
    public enum DoorError { None, UnknownDoor, RevisionConflict, Locked, NotOperable, StoreStopped }
    public enum EvacuationResultKind { Applied, Duplicate, AlreadyActive, StoreStopped }

    public sealed class DoorSnapshot
    {
        internal DoorSnapshot(Guid id, string sourceId, DoorMode mode, DoorMode evacuationMode, bool playerOperable, long revision)
        { Id = id; SourceId = sourceId; Mode = mode; EvacuationMode = evacuationMode; PlayerOperable = playerOperable; Revision = revision; }
        public Guid Id { get; }
        public string SourceId { get; }
        public DoorMode Mode { get; }
        public DoorMode EvacuationMode { get; }
        public bool PlayerOperable { get; }
        public long Revision { get; }
        internal DoorSnapshot WithMode(DoorMode mode) => new DoorSnapshot(Id, SourceId, mode, EvacuationMode, PlayerOperable, checked(Revision + 1));
    }

    public sealed class DoorResult
    {
        internal DoorResult(DoorError error, DoorSnapshot? state, bool changed = false)
        { Error = error; State = state; Changed = changed; }
        public DoorError Error { get; }
        public DoorSnapshot? State { get; }
        public bool Changed { get; }
    }

    public sealed class DoorEvacuationResult
    {
        internal DoorEvacuationResult(EvacuationResultKind kind, Guid causeId, IReadOnlyList<DoorSnapshot> changes)
        { Kind = kind; CauseId = causeId; Changes = changes; }
        public EvacuationResultKind Kind { get; }
        public Guid CauseId { get; }
        public IReadOnlyList<DoorSnapshot> Changes { get; }
    }

    /// <summary>One world's bounded logical doors; no poses, physics, claims, clock or event subscriptions.</summary>
    public sealed class DoorStateStore
    {
        private readonly Dictionary<Guid, DoorSnapshot> _doors = new Dictionary<Guid, DoorSnapshot>();
        private readonly Dictionary<string, Guid> _sources = new Dictionary<string, Guid>(StringComparer.Ordinal);
        private readonly int _capacity;
        private bool _stopped;
        public DoorStateStore(int capacity = 128)
        {
            if (capacity < 1 || capacity > 128) throw new ArgumentOutOfRangeException(nameof(capacity));
            _capacity = capacity;
        }
        public int Count => _doors.Count;
        public Guid? EvacuationCauseId { get; private set; }
        public DoorSnapshot? Get(Guid id) => _doors.TryGetValue(id, out var door) ? door : null;
        public DoorSnapshot? GetBySourceId(string sourceId) => sourceId != null && _sources.TryGetValue(sourceId, out var id) ? Get(id) : null;
        public void Register(Guid id, string sourceId, DoorMode initial, DoorMode evacuation, bool playerOperable)
        {
            if (id == Guid.Empty || string.IsNullOrWhiteSpace(sourceId) || sourceId.Length > 128 || sourceId != sourceId.Trim())
                throw new ArgumentException("Stable door and bounded source identities are required.");
            foreach (char value in sourceId) if (char.IsControl(value)) throw new ArgumentException("Door source identities cannot contain control characters.");
            if (!Enum.IsDefined(typeof(DoorMode), initial) || !Enum.IsDefined(typeof(DoorMode), evacuation))
                throw new ArgumentOutOfRangeException(nameof(initial));
            if (_stopped || EvacuationCauseId.HasValue || _doors.Count >= _capacity || _doors.ContainsKey(id) || _sources.ContainsKey(sourceId))
                throw new InvalidOperationException("Door registration is duplicate, stopped or capacity exhausted.");
            var state = new DoorSnapshot(id, sourceId, initial, evacuation, playerOperable, 0);
            _doors.Add(id, state); _sources.Add(sourceId, id);
        }
        public DoorResult TrySetOpen(Guid id, long revision, bool open)
        {
            var current = Get(id);
            if (_stopped) return new DoorResult(DoorError.StoreStopped, current);
            if (current == null) return new DoorResult(DoorError.UnknownDoor, null);
            if (revision != current.Revision) return new DoorResult(DoorError.RevisionConflict, current);
            if (!current.PlayerOperable) return new DoorResult(DoorError.NotOperable, current);
            if (current.Mode == DoorMode.Locked) return new DoorResult(DoorError.Locked, current);
            DoorMode mode = open ? DoorMode.Open : DoorMode.Closed;
            if (current.Mode == mode) return new DoorResult(DoorError.None, current);
            var next = current.WithMode(mode); _doors[id] = next;
            return new DoorResult(DoorError.None, next, true);
        }
        public DoorEvacuationResult BeginEvacuation(Guid causeId)
        {
            if (causeId == Guid.Empty) throw new ArgumentException("An evacuation cause is required.", nameof(causeId));
            if (_stopped) return Empty(EvacuationResultKind.StoreStopped, causeId);
            if (EvacuationCauseId.HasValue) return Empty(EvacuationCauseId.Value == causeId ? EvacuationResultKind.Duplicate : EvacuationResultKind.AlreadyActive, EvacuationCauseId.Value);
            var changes = new List<DoorSnapshot>();
            foreach (var door in _doors.Values) if (door.Mode != door.EvacuationMode) changes.Add(door.WithMode(door.EvacuationMode));
            changes.Sort((a, b) => a.Id.CompareTo(b.Id));
            // Compute every revision before installing any authored evacuation state.
            foreach (var next in changes) _doors[next.Id] = next;
            EvacuationCauseId = causeId;
            return new DoorEvacuationResult(EvacuationResultKind.Applied, causeId, changes.AsReadOnly());
        }
        private static DoorEvacuationResult Empty(EvacuationResultKind kind, Guid cause) => new DoorEvacuationResult(kind, cause, Array.Empty<DoorSnapshot>());
        public void Stop() { _stopped = true; _doors.Clear(); _sources.Clear(); EvacuationCauseId = null; }
    }
}
