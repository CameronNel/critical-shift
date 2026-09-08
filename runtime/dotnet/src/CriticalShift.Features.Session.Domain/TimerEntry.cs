using System;

namespace CriticalShift.Features.Session.Domain
{
    // Ordering is intentional: host-time signals precede simulation-time signals in a batch.
    public enum TimerClock { Host, Simulation }

    /// <summary>Detached, immutable one-shot signal. It contains no delegate or mutable owner.</summary>
    public sealed class TimerEntry
    {
        internal TimerEntry(Guid epoch, long sequence, Guid ownerId, string signal,
            TimerClock clock, long dueMilliseconds)
        {
            Epoch = epoch;
            Sequence = sequence;
            OwnerId = ownerId;
            Signal = signal;
            Clock = clock;
            DueMilliseconds = dueMilliseconds;
        }

        public Guid Epoch { get; }
        public long Sequence { get; }
        public Guid OwnerId { get; }
        public string Signal { get; }
        public TimerClock Clock { get; }
        public long DueMilliseconds { get; }
    }
}
