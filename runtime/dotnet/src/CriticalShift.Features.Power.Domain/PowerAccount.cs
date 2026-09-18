using System;

namespace CriticalShift.Features.Power.Domain
{
    /// <summary>Immutable accounting in abstract game units. The Application owner installs accepted results.</summary>
    public sealed class PowerAccount
    {
        public PowerAccount(long capacity, long initial)
            : this(capacity, initial, initial, 0, 0, 0, 0)
        {
            if (capacity < 1 || initial < 0 || initial > capacity)
                throw new ArgumentOutOfRangeException(nameof(initial));
        }

        private PowerAccount(long capacity, long initial, long available, long generated,
            long spent, long delivered, long spilled)
        {
            Capacity = capacity; Initial = initial; Available = available; Generated = generated;
            Spent = spent; Delivered = delivered; Spilled = spilled;
        }

        public long Capacity { get; }
        public long Initial { get; }
        public long Available { get; }
        public long Generated { get; }
        public long Spent { get; }
        public long Delivered { get; }
        public long Spilled { get; }

        public bool TrySpend(long cost, out PowerAccount next)
        {
            if (cost <= 0) throw new ArgumentOutOfRangeException(nameof(cost));
            next = this;
            if (cost > Available) return false;
            next = new PowerAccount(Capacity, Initial, Available - cost, Generated,
                checked(Spent + cost), Delivered, Spilled);
            return true;
        }

        public PowerAccount Credit(long reserve, long grid)
        {
            if (reserve < 0 || grid < 0) throw new ArgumentOutOfRangeException(nameof(reserve));
            if (reserve == 0 && grid == 0) return this;
            long stored = Math.Min(reserve, Capacity - Available);
            return new PowerAccount(Capacity, Initial, Available + stored,
                checked(Generated + checked(reserve + grid)), Spent,
                checked(Delivered + grid), checked(Spilled + (reserve - stored)));
        }
    }
}
