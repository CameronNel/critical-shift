using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Interaction.Domain
{
    /// <summary>
    /// One world's exclusive logical claims. Call on one simulation thread, not concurrently.
    /// Time is supplied explicitly in monotonic milliseconds; this class never reads a clock.
    /// </summary>
    public sealed class ExclusiveClaimStore
    {
        private readonly Dictionary<Guid, ClaimSnapshot> _objects = new Dictionary<Guid, ClaimSnapshot>();
        private readonly Dictionary<Guid, Guid> _heldByActor = new Dictionary<Guid, Guid>();
        private readonly Dictionary<Guid, Guid?> _slots = new Dictionary<Guid, Guid?>();
        private readonly HashSet<Guid> _assistable = new HashSet<Guid>();
        private readonly int _capacity;
        private readonly long _leaseMilliseconds;
        private bool _stopped;

        public ExclusiveClaimStore(int capacity, long leaseMilliseconds)
        {
            if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
            if (leaseMilliseconds <= 0) throw new ArgumentOutOfRangeException(nameof(leaseMilliseconds));
            _capacity = capacity;
            _leaseMilliseconds = leaseMilliseconds;
        }

        public long NowMilliseconds { get; private set; }
        public int RegisteredCount => _objects.Count;
        public int ActiveClaimCount => _heldByActor.Count;

        public void Register(Guid entityId, bool allowAssistance = false)
        {
            RequireId(entityId, nameof(entityId));
            if (_stopped) throw new InvalidOperationException("The claim store has stopped.");
            if (_objects.ContainsKey(entityId) || _slots.ContainsKey(entityId)) throw new InvalidOperationException("Entity IDs cannot be reused within a world.");
            if (_objects.Count >= _capacity) throw new InvalidOperationException("Entity capacity reached.");
            _objects.Add(entityId, new ClaimSnapshot(entityId, null, 0, 0, 0, false));
            if (allowAssistance) _assistable.Add(entityId);
        }

        public ClaimSnapshot? Get(Guid entityId)
        {
            return _objects.TryGetValue(entityId, out var state) ? state : null;
        }

        public ClaimResult TryGrab(Guid entityId, Guid actorId, long expectedRevision)
        {
            RequireId(actorId, nameof(actorId));
            var error = Inspect(entityId, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            if (state!.Revision != expectedRevision) return new ClaimResult(ClaimError.RevisionConflict, state);
            if (state.SlotId.HasValue) return new ClaimResult(ClaimError.EntitySlotted, state);
            if (state.HolderId.HasValue) return new ClaimResult(ClaimError.AlreadyClaimed, state);
            if (_heldByActor.ContainsKey(actorId)) return new ClaimResult(ClaimError.ActorAlreadyHolding, state);

            // Compute all fallible arithmetic before changing either index.
            long revision = checked(state.Revision + 1);
            long generation = checked(state.LeaseGeneration + 1);
            long expiry = checked(NowMilliseconds + _leaseMilliseconds);
            var next = new ClaimSnapshot(entityId, actorId, revision, generation, expiry, false);
            _heldByActor.Add(actorId, entityId);
            _objects[entityId] = next;
            return new ClaimResult(ClaimError.None, next, true);
        }

        public ClaimResult TryRelease(Guid entityId, Guid actorId, long generation)
        {
            var error = InspectLease(entityId, actorId, generation, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            return new ClaimResult(ClaimError.None, state!.AssistantId == actorId ? DetachAssistant(state) : Free(state, false), true);
        }

        public ClaimResult TryAssist(Guid entityId, Guid actorId, long expectedRevision, long generation)
        {
            RequireId(actorId, nameof(actorId));
            var error = Inspect(entityId, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            if (!_assistable.Contains(entityId)) return new ClaimResult(ClaimError.AssistanceDisabled, state);
            if (state!.Revision != expectedRevision) return new ClaimResult(ClaimError.RevisionConflict, state);
            if (!state.HolderId.HasValue || state.LeaseGeneration != generation) return new ClaimResult(ClaimError.StaleLease, state);
            if (state.AssistantId.HasValue) return new ClaimResult(ClaimError.AlreadyClaimed, state);
            if (_heldByActor.ContainsKey(actorId)) return new ClaimResult(ClaimError.ActorAlreadyHolding, state);
            var next = new ClaimSnapshot(entityId, state.HolderId, checked(state.Revision + 1), generation,
                state.ExpiresAtMilliseconds, false, assistantId: actorId);
            _heldByActor.Add(actorId, entityId); _objects[entityId] = next;
            return new ClaimResult(ClaimError.None, next, true);
        }

        public ClaimResult TryRenew(Guid entityId, Guid actorId, long generation)
        {
            var error = InspectLease(entityId, actorId, generation, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            long expiry = checked(NowMilliseconds + _leaseMilliseconds);
            if (expiry == state!.ExpiresAtMilliseconds) return new ClaimResult(ClaimError.None, state);
            var next = new ClaimSnapshot(entityId, state.HolderId, checked(state.Revision + 1),
                generation, expiry, false, assistantId: state.AssistantId);
            _objects[entityId] = next;
            return new ClaimResult(ClaimError.None, next, true);
        }

        public IReadOnlyList<ClaimSnapshot> AdvanceTo(long nowMilliseconds)
        {
            if (nowMilliseconds < NowMilliseconds) throw new ArgumentOutOfRangeException(nameof(nowMilliseconds), "Clock cannot move backwards.");
            if (_stopped) throw new InvalidOperationException("The claim store has stopped.");
            var expired = new List<ClaimSnapshot>();
            foreach (var state in _objects.Values)
                if (state.HolderId.HasValue && state.ExpiresAtMilliseconds <= nowMilliseconds)
                    expired.Add(state);
            // Stable ordering makes diagnostics and future binding cleanup reproducible.
            expired.Sort((a, b) => a.EntityId.CompareTo(b.EntityId));
            NowMilliseconds = nowMilliseconds;
            for (int i = 0; i < expired.Count; i++) expired[i] = Free(expired[i], false);
            return expired.AsReadOnly();
        }

        public ClaimSnapshot? ReleaseActor(Guid actorId)
        {
            if (_stopped) return null;
            if (!_heldByActor.TryGetValue(actorId, out var id)) return null;
            var state = _objects[id]; return state.AssistantId == actorId ? DetachAssistant(state) : Free(state, false);
        }

        public ClaimResult Retire(Guid entityId)
        {
            var error = Inspect(entityId, out var state);
            if (error == ClaimError.None && state!.SlotId.HasValue) return new ClaimResult(ClaimError.EntitySlotted, state);
            return error == ClaimError.None
                ? new ClaimResult(ClaimError.None, Free(state!, true), true)
                : new ClaimResult(error, state);
        }

        public void RegisterSlot(Guid slotId)
        {
            RequireId(slotId, nameof(slotId));
            if (_stopped || _slots.ContainsKey(slotId) || _objects.ContainsKey(slotId) || _slots.Count >= _capacity)
                throw new InvalidOperationException("Invalid, duplicate or capacity-exhausted slot registration.");
            _slots.Add(slotId, null);
        }
        public Guid? GetSlotOccupant(Guid slotId) => _slots.TryGetValue(slotId, out var occupant) ? occupant : null;

        public ClaimResult TryInsert(Guid entity, Guid actor, long lease, long revision, Guid slot)
        {
            var error = InspectLease(entity, actor, lease, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            if (state!.AssistantId.HasValue || state.HolderId != actor) return new ClaimResult(ClaimError.AlreadyClaimed, state);
            if (state!.Revision != revision) return new ClaimResult(ClaimError.RevisionConflict, state);
            if (!_slots.TryGetValue(slot, out var occupant)) return new ClaimResult(ClaimError.UnknownSlot, state);
            if (occupant.HasValue) return new ClaimResult(ClaimError.SlotOccupied, state);
            var next = new ClaimSnapshot(entity, null, checked(state.Revision + 1), state.LeaseGeneration, 0, false, slot);
            _heldByActor.Remove(actor); _objects[entity] = next; _slots[slot] = entity;
            return new ClaimResult(ClaimError.None, next, true);
        }
        public ClaimResult TryEject(Guid slot, long revision)
        {
            if (_stopped) return new ClaimResult(ClaimError.StoreStopped, null);
            if (!_slots.TryGetValue(slot, out var occupant)) return new ClaimResult(ClaimError.UnknownSlot, null);
            if (!occupant.HasValue) return new ClaimResult(ClaimError.SlotEmpty, null);
            var current = _objects[occupant.Value];
            if (current.Revision != revision) return new ClaimResult(ClaimError.RevisionConflict, current);
            var next = new ClaimSnapshot(current.EntityId, null, checked(current.Revision + 1), current.LeaseGeneration, 0, false);
            _objects[current.EntityId] = next; _slots[slot] = null;
            return new ClaimResult(ClaimError.None, next, true);
        }

        public void Stop()
        {
            _stopped = true;
            _heldByActor.Clear();
            _objects.Clear(); _slots.Clear(); _assistable.Clear();
        }

        private ClaimSnapshot Free(ClaimSnapshot previous, bool retired)
        {
            var next = new ClaimSnapshot(previous.EntityId, null, checked(previous.Revision + 1),
                previous.LeaseGeneration, 0, retired);
            if (previous.HolderId.HasValue) _heldByActor.Remove(previous.HolderId.Value);
            if (previous.AssistantId.HasValue) _heldByActor.Remove(previous.AssistantId.Value);
            _objects[previous.EntityId] = next;
            return next;
        }

        private ClaimSnapshot DetachAssistant(ClaimSnapshot state)
        {
            var next = new ClaimSnapshot(state.EntityId, state.HolderId, checked(state.Revision + 1), state.LeaseGeneration,
                state.ExpiresAtMilliseconds, false);
            _heldByActor.Remove(state.AssistantId!.Value); _objects[state.EntityId] = next; return next;
        }

        private ClaimError Inspect(Guid entityId, out ClaimSnapshot? state)
        {
            state = Get(entityId);
            if (_stopped) return ClaimError.StoreStopped;
            if (state == null) return ClaimError.UnknownEntity;
            return state.IsRetired ? ClaimError.EntityRetired : ClaimError.None;
        }

        private ClaimError InspectLease(Guid entityId, Guid actorId, long generation, out ClaimSnapshot? state)
        {
            RequireId(actorId, nameof(actorId));
            var error = Inspect(entityId, out state);
            if (error != ClaimError.None) return error;
            if (!state!.HolderId.HasValue || generation <= 0 || state.LeaseGeneration != generation)
                return ClaimError.StaleLease;
            return state.HolderId == actorId || state.AssistantId == actorId ? ClaimError.None : ClaimError.NotHolder;
        }

        private static void RequireId(Guid value, string name)
        {
            if (value == Guid.Empty) throw new ArgumentException("An ID must not be empty.", name);
        }
    }
}
