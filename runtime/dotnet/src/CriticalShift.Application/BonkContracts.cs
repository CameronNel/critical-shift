using System;

namespace CriticalShift.Application
{
    public sealed class BonkView
    {
        public const long WindupMilliseconds = 180, StrikeEndMilliseconds = 320, DurationMilliseconds = 700, CooldownMilliseconds = 950;
        internal BonkView(Guid actor, Guid tool, long sequence, long lease, long started, Guid cause, bool consumed, bool cancelled = false)
        { Actor = actor; Tool = tool; Sequence = sequence; LeaseGeneration = lease; StartedMilliseconds = started; Cause = cause; ContactConsumed = consumed; Cancelled = cancelled; }
        public Guid Actor { get; }
        public Guid Tool { get; }
        public long Sequence { get; }
        public long LeaseGeneration { get; }
        public long StartedMilliseconds { get; }
        public Guid Cause { get; }
        public bool ContactConsumed { get; }
        public bool Cancelled { get; }
    }
}
