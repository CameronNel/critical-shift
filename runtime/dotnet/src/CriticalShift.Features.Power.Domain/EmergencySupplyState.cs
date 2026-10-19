#nullable enable
using System;

namespace CriticalShift.Features.Power.Domain
{
    /// <summary>Finite authored backup charges. Energy is installed only in the separate canonical PowerAccount.</summary>
    public sealed class EmergencySupplyRules
    {
        public EmergencySupplyRules(long durationMilliseconds = 5000, long reserveUnits = 12, int charges = 2)
        {
            if (durationMilliseconds < 1 || durationMilliseconds > 60000 || reserveUnits < 1 || reserveUnits > 1000000000 ||
                charges < 1 || charges > 32) throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            DurationMilliseconds = durationMilliseconds; ReserveUnits = reserveUnits; Charges = charges;
        }
        public long DurationMilliseconds { get; }
        public long ReserveUnits { get; }
        public int Charges { get; }
    }

    public sealed class EmergencySupplyState
    {
        public EmergencySupplyState(EmergencySupplyRules rules)
            : this(rules, rules?.Charges ?? 0, Guid.Empty, 0, 0, false, 0, 0, 0, 0, 0) { }
        private EmergencySupplyState(EmergencySupplyRules rules, int remaining, Guid cycle, long startedAt, long dueAt,
            bool running, int completed, int cancelled, long produced, long stored, long spilled)
        {
            Rules = rules ?? throw new ArgumentNullException(nameof(rules)); RemainingCharges = remaining;
            CycleId = cycle; StartedAtMilliseconds = startedAt; DueAtMilliseconds = dueAt; Running = running;
            CompletedCycles = completed; CancelledCycles = cancelled; ProducedUnits = produced;
            StoredUnits = stored; SpilledUnits = spilled;
        }
        public EmergencySupplyRules Rules { get; }
        public int RemainingCharges { get; }
        public Guid CycleId { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public bool Running { get; }
        public int CompletedCycles { get; }
        public int CancelledCycles { get; }
        public long ProducedUnits { get; }
        public long StoredUnits { get; }
        public long SpilledUnits { get; }
        public EmergencySupplyState Begin(Guid cycle, long now)
        {
            if (Running || RemainingCharges == 0 || cycle == Guid.Empty || cycle == CycleId || now < 0)
                throw new InvalidOperationException("A new backup cycle needs an unused charge and valid shift coordinate.");
            long due = checked(now + Rules.DurationMilliseconds);
            return new EmergencySupplyState(Rules, RemainingCharges - 1, cycle, now, due, true,
                CompletedCycles, CancelledCycles, ProducedUnits, StoredUnits, SpilledUnits);
        }
        public EmergencySupplyState Complete(long now, long stored)
        {
            if (!Running || now != DueAtMilliseconds || stored < 0 || stored > Rules.ReserveUnits)
                throw new InvalidOperationException("Complete the current backup cycle at its exact due coordinate.");
            return new EmergencySupplyState(Rules, RemainingCharges, CycleId, StartedAtMilliseconds, DueAtMilliseconds, false,
                checked(CompletedCycles + 1), CancelledCycles, checked(ProducedUnits + Rules.ReserveUnits),
                checked(StoredUnits + stored), checked(SpilledUnits + Rules.ReserveUnits - stored));
        }
        public EmergencySupplyState Cancel()
        {
            if (!Running) throw new InvalidOperationException("No backup cycle is running.");
            return new EmergencySupplyState(Rules, RemainingCharges, CycleId, StartedAtMilliseconds, DueAtMilliseconds, false,
                CompletedCycles, checked(CancelledCycles + 1), ProducedUnits, StoredUnits, SpilledUnits);
        }
    }
}
