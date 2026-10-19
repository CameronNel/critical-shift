#nullable enable
using System;
using CriticalShift.Features.Power.Domain;

namespace CriticalShift.Application
{
    public sealed class EmergencyPowerDefinition
    {
        public EmergencyPowerDefinition(long durationMilliseconds = 5000, long reserveUnits = 12, int charges = 2)
        { Rules = new EmergencySupplyRules(durationMilliseconds, reserveUnits, charges); }
        internal EmergencySupplyRules Rules { get; }
        public long DurationMilliseconds => Rules.DurationMilliseconds;
        public long ReserveUnits => Rules.ReserveUnits;
        public int Charges => Rules.Charges;
    }
    public sealed class EmergencyPowerView
    {
        internal EmergencyPowerView(Guid epoch, EmergencySupplyState state)
        {
            Epoch = epoch; RemainingCharges = state.RemainingCharges; UsedCharges = state.Rules.Charges - state.RemainingCharges;
            Running = state.Running; CycleId = state.CycleId; StartedAtMilliseconds = state.StartedAtMilliseconds;
            DueAtMilliseconds = state.DueAtMilliseconds; DurationMilliseconds = state.Rules.DurationMilliseconds;
            ReserveUnitsPerCharge = state.Rules.ReserveUnits; CompletedCycles = state.CompletedCycles;
            CancelledCycles = state.CancelledCycles; ProducedUnits = state.ProducedUnits; StoredUnits = state.StoredUnits;
            SpilledUnits = state.SpilledUnits;
        }
        public Guid Epoch { get; }
        public int RemainingCharges { get; }
        public int UsedCharges { get; }
        public bool Running { get; }
        public Guid CycleId { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public long DurationMilliseconds { get; }
        public long ReserveUnitsPerCharge { get; }
        public int CompletedCycles { get; }
        public int CancelledCycles { get; }
        public long ProducedUnits { get; }
        public long StoredUnits { get; }
        public long SpilledUnits { get; }
    }
}
