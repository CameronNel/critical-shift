#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    /// <summary>Facts collected from committed changes. Standing recovery is distinct from medical reanimation.</summary>
    public sealed class ShiftIncidentTotals
    {
        internal ShiftIncidentTotals(long impacts, long incapacitations, long aids, long recoveries, long jams,
            long bypasses, long warnings, long trips, long emergencyCooling, bool saturated)
        {
            WorkerImpacts = impacts; Incapacitations = incapacitations; Stabilizations = aids;
            StandingRecoveries = recoveries; MachineJams = jams; BypassedConversions = bypasses;
            ReactorWarnings = warnings; ReactorTrips = trips; EmergencyCoolingUses = emergencyCooling;
            Saturated = saturated;
        }
        public long WorkerImpacts { get; }
        public long Incapacitations { get; }
        public long Stabilizations { get; }
        public long StandingRecoveries { get; }
        public long MachineJams { get; }
        public long BypassedConversions { get; }
        public long ReactorWarnings { get; }
        public long ReactorTrips { get; }
        public long EmergencyCoolingUses { get; }
        public bool Saturated { get; }
    }

    /// <summary>Detached terminal projection. Reading it cannot repeat a cost, conversion, objective or injury.</summary>
    public sealed class ShiftDebriefView
    {
        internal ShiftDebriefView(WorldSessionView world, ShiftContractView? contract, ProductionSummary production,
            PowerView? power, IReadOnlyList<WorkerView> workers, ShiftIncidentTotals incidents,
            IReadOnlyList<SessionTraceRecord> timeline, long droppedIncidents, MedicalSummary medical, EmergencyPowerView? emergencyPower)
        {
            World = world; Contract = contract; Production = production; Power = power;
            WorkersAtEnd = workers; Incidents = incidents; Timeline = timeline; DroppedIncidents = droppedIncidents;
            Medical = medical; EmergencyPower = emergencyPower;
        }
        public WorldSessionView World { get; }
        public ShiftContractView? Contract { get; }
        public ProductionSummary Production { get; }
        public PowerView? Power { get; }
        public MedicalSummary Medical { get; }
        public EmergencyPowerView? EmergencyPower { get; }
        public IReadOnlyList<WorkerView> WorkersAtEnd { get; }
        public ShiftIncidentTotals Incidents { get; }
        /// <summary>Retained incidents sorted by occurrence time, then recording sequence. Bounded and explicitly incomplete when dropped.</summary>
        public IReadOnlyList<SessionTraceRecord> Timeline { get; }
        public long DroppedIncidents { get; }
    }

    // Diagnostic observer only. These counters never authorize gameplay or own resource balances.
    internal sealed class ShiftIncidentJournal
    {
        private readonly List<SessionTraceRecord> records;
        private readonly int capacity;
        private long dropped, impacts, incapacitations, aids, recoveries, jams, bypasses, warnings, trips, emergency;
        private bool saturated;
        internal ShiftIncidentJournal(int maximum)
        { capacity = Math.Min(maximum, 128); records = new List<SessionTraceRecord>(capacity); }
        internal long Dropped => dropped;
        internal ShiftIncidentTotals Totals => new ShiftIncidentTotals(impacts, incapacitations, aids,
            recoveries, jams, bypasses, warnings, trips, emergency, saturated);
        internal IReadOnlyList<SessionTraceRecord> Timeline => Array.AsReadOnly(records.ToArray());
        internal void Observe(SessionTraceRecord record, bool retainDetail)
        {
            if (!record.Changed) return;
            bool retain = false;
            if (record.Kind == SessionTraceKind.Impact)
            {
                Increment(ref impacts); retain = true;
                if (record.ImpactSeverity == WorkerImpact.Incapacitating) Increment(ref incapacitations);
            }
            if (record.Kind == SessionTraceKind.Aid && record.WorkerResult == WorkerStatus.Applied)
            { Increment(ref aids); retain = true; }
            if (record.Kind == SessionTraceKind.RecoveryResolved && record.WorkerResult == WorkerStatus.Applied)
            { Increment(ref recoveries); retain = true; }
            if (record.ProductionEvent == ProductionEvent.Jammed) Increment(ref jams);
            if (record.ProductionEvent == ProductionEvent.Completed && record.BypassedInspection == true) Increment(ref bypasses);
            if (record.ProductionEvent.HasValue) retain = true;
            if (record.ReactorEvent == ReactorEvent.Warning) Increment(ref warnings);
            if (record.ReactorEvent == ReactorEvent.Tripped) Increment(ref trips);
            if (record.ReactorEvent == ReactorEvent.EmergencyCooling) Increment(ref emergency);
            if (record.ReactorEvent.HasValue && record.ReactorEvent != ReactorEvent.Generated) retain = true;
            if (record.ContaminationContact != null || record.MedicalChange != null || record.DemandChange != null || record.Kind == SessionTraceKind.Disconnected ||
                record.Kind == SessionTraceKind.Evacuation || record.Kind == SessionTraceKind.Started ||
                record.Kind == SessionTraceKind.Ended || record.Kind == SessionTraceKind.Stopped ||
                record.Kind == SessionTraceKind.Faulted) retain = true;
            if (!retain) return;
            if (!retainDetail) { Increment(ref dropped); return; }
            int index = records.BinarySearch(record, IncidentOrder.Instance);
            if (index < 0) index = ~index;
            records.Insert(index, record);
            // Keep the most recent occurrences even when owners report different event types out of order.
            if (records.Count > capacity) { records.RemoveAt(0); Increment(ref dropped); }
        }
        private void Increment(ref long value) { if (value == long.MaxValue) saturated = true; else value++; }
        private sealed class IncidentOrder : IComparer<SessionTraceRecord>
        {
            internal static IncidentOrder Instance { get; } = new IncidentOrder();
            public int Compare(SessionTraceRecord? a, SessionTraceRecord? b)
            {
                if (a == null || b == null) throw new ArgumentNullException(nameof(a));
                int time = a.OccurredAtMilliseconds.CompareTo(b.OccurredAtMilliseconds);
                return time != 0 ? time : a.Sequence.CompareTo(b.Sequence);
            }
        }
    }
}
