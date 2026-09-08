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

        public void Register(Guid entityId)
        {
            RequireId(entityId, nameof(entityId));
            if (_stopped) throw new InvalidOperationException("The claim store has stopped.");
            if (_objects.ContainsKey(entityId)) throw new InvalidOperationException("Entity IDs cannot be reused within a world.");
            if (_objects.Count >= _capacity) throw new InvalidOperationException("Entity capacity reached.");
            _objects.Add(entityId, new ClaimSnapshot(entityId, null, 0, 0, 0, false));
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
            return new ClaimResult(ClaimError.None, Free(state!, false), true);
        }

        public ClaimResult TryRenew(Guid entityId, Guid actorId, long generation)
        {
            var error = InspectLease(entityId, actorId, generation, out var state);
            if (error != ClaimError.None) return new ClaimResult(error, state);
            long expiry = checked(NowMilliseconds + _leaseMilliseconds);
            if (expiry == state!.ExpiresAtMilliseconds) return new ClaimResult(ClaimError.None, state);
            var next = new ClaimSnapshot(entityId, actorId, checked(state.Revision + 1),
                generation, expiry, false);
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
            return _heldByActor.TryGetValue(actorId, out var id) ? Free(_objects[id], false) : null;
        }

        public ClaimResult Retire(Guid entityId)
        {
            var error = Inspect(entityId, out var state);
            return error == ClaimError.None
                ? new ClaimResult(ClaimError.None, Free(state!, true), true)
                : new ClaimResult(error, state);
        }

        public void Stop()
        {
            _stopped = true;
            _heldByActor.Clear();
            _objects.Clear();
        }

        private ClaimSnapshot Free(ClaimSnapshot previous, bool retired)
        {
            var next = new ClaimSnapshot(previous.EntityId, null, checked(previous.Revision + 1),
                previous.LeaseGeneration, 0, retired);
            if (previous.HolderId.HasValue) _heldByActor.Remove(previous.HolderId.Value);
            _objects[previous.EntityId] = next;
            return next;
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
            return state.HolderId == actorId ? ClaimError.None : ClaimError.NotHolder;
        }

        private static void RequireId(Guid value, string name)
        {
            if (value == Guid.Empty) throw new ArgumentException("An ID must not be empty.", name);
        }
    }
}
