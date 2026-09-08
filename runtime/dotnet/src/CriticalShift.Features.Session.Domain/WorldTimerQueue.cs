using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Session.Domain
{
    /// <summary>
    /// Bounded one-shot scheduling for a single epoch. Polls return signals, never execute code.
    /// No automatic repetitions, hidden threads, wall-clock reads or retained fired-event history.
    /// </summary>
    public sealed class WorldTimerQueue
    {
        private readonly Dictionary<long, TimerEntry> _pending = new Dictionary<long, TimerEntry>();
        private readonly int _capacity;
        private long _lastSequence;

        public WorldTimerQueue(Guid epoch, int capacity = 128)
        {
            if (epoch == Guid.Empty) throw new ArgumentException("An epoch is required.", nameof(epoch));
            if (capacity < 1 || capacity > 4096) throw new ArgumentOutOfRangeException(nameof(capacity));
            Epoch = epoch;
            _capacity = capacity;
        }

        public Guid Epoch { get; }
        public long HostMilliseconds { get; private set; }
        public long SimulationMilliseconds { get; private set; }
        public int Count => _pending.Count;
        public bool IsStopped { get; private set; }

        public bool TrySchedule(Guid ownerId, string signal, TimerClock clock, long delayMilliseconds,
            out TimerEntry? entry)
        {
            RequireActive();
            if (ownerId == Guid.Empty) throw new ArgumentException("A timer owner is required.", nameof(ownerId));
            if (string.IsNullOrWhiteSpace(signal) || signal.Length > 64)
                throw new ArgumentException("A signal must contain 1-64 meaningful characters.", nameof(signal));
            if (clock != TimerClock.Host && clock != TimerClock.Simulation)
                throw new ArgumentOutOfRangeException(nameof(clock));
            if (delayMilliseconds < 0) throw new ArgumentOutOfRangeException(nameof(delayMilliseconds));
            entry = null;
            if (_pending.Count >= _capacity) return false;
            long now = clock == TimerClock.Host ? HostMilliseconds : SimulationMilliseconds;
            // Compute all fallible arithmetic before changing sequence or storage.
            long due = checked(now + delayMilliseconds);
            long sequence = checked(_lastSequence + 1);
            var next = new TimerEntry(Epoch, sequence, ownerId, signal, clock, due);
            _pending.Add(sequence, next);
            _lastSequence = sequence;
            entry = next;
            return true;
        }

        public bool Cancel(Guid epoch, long sequence) =>
            !IsStopped && epoch == Epoch && _pending.Remove(sequence);

        public int CancelOwner(Guid epoch, Guid ownerId)
        {
            if (ownerId == Guid.Empty) throw new ArgumentException("A timer owner is required.", nameof(ownerId));
            if (IsStopped || epoch != Epoch) return 0;
            var removed = new List<long>();
            foreach (var entry in _pending.Values)
                if (entry.OwnerId == ownerId) removed.Add(entry.Sequence);
            foreach (long sequence in removed) _pending.Remove(sequence);
            return removed.Count;
        }

        public IReadOnlyList<TimerEntry> AdvanceTo(long hostMilliseconds, long simulationMilliseconds)
        {
            RequireActive();
            if (hostMilliseconds < HostMilliseconds || simulationMilliseconds < SimulationMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(hostMilliseconds), "Neither timer clock may move backwards.");
            var ready = new List<TimerEntry>();
            foreach (var entry in _pending.Values)
            {
                long now = entry.Clock == TimerClock.Host ? hostMilliseconds : simulationMilliseconds;
                if (entry.DueMilliseconds <= now) ready.Add(entry);
            }
            // There is no total real-time ordering between a paused and an unpaused clock.
            // Within each clock use deadline, then creation sequence, independent of dictionary order.
            ready.Sort((a, b) =>
            {
                int clock = a.Clock.CompareTo(b.Clock);
                if (clock != 0) return clock;
                int due = a.DueMilliseconds.CompareTo(b.DueMilliseconds);
                return due != 0 ? due : a.Sequence.CompareTo(b.Sequence);
            });
            HostMilliseconds = hostMilliseconds;
            SimulationMilliseconds = simulationMilliseconds;
            foreach (var entry in ready) _pending.Remove(entry.Sequence);
            return ready.AsReadOnly();
        }

        public void Stop()
        {
            IsStopped = true;
            _pending.Clear();
        }

        private void RequireActive()
        {
            if (IsStopped) throw new InvalidOperationException("The timer queue has stopped.");
        }
    }
}
