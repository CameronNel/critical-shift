#nullable enable
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using CriticalShift.Application;

namespace CriticalShift.Presentation
{
    /// <summary>Small derived display over existing host diagnostics, never an authoritative causality ledger.</summary>
    public sealed class SandboxTraceFeed
    {
        public sealed class Entry
        {
            internal Entry(SessionTraceRecord record, Guid cause, string description)
            {
                Sequence = record.Sequence; ShiftMilliseconds = record.OccurredAtMilliseconds; EntityId = record.EntityId;
                ActorId = record.MedicalChange?.PatientId ?? record.ActorId; HazardId = record.HazardId;
                Kind = record.Kind; Production = record.ProductionEvent; Reactor = record.ReactorEvent;
                Medical = record.MedicalChange?.Kind;
                CauseId = cause; Description = description;
            }
            public long Sequence { get; }
            public long ShiftMilliseconds { get; }
            public Guid EntityId { get; }
            public Guid ActorId { get; }
            public Guid HazardId { get; }
            public Guid CauseId { get; }
            public SessionTraceKind Kind { get; }
            public ProductionEvent? Production { get; }
            public ReactorEvent? Reactor { get; }
            public MedicalEvent? Medical { get; }
            public string Description { get; }
        }

        private readonly LocalCommandPort queries;
        private readonly Guid epoch;
        private readonly List<Entry> entries = new List<Entry>(12);
        private readonly ReadOnlyCollection<Entry> rows;
        private long lastSequence;
        public IReadOnlyList<Entry> Entries => rows;
        public long SourceDroppedRecords { get; private set; }
        public bool GapDetected { get; private set; }
        public bool SequenceExhausted { get; private set; }

        public SandboxTraceFeed(LocalCommandPort read)
        {
            queries = read ?? throw new ArgumentNullException(nameof(read)); epoch = read.World.Epoch; rows = entries.AsReadOnly();
        }

        public static IReadOnlyList<Entry> DebriefEntries(ShiftDebriefView debrief)
        {
            if (debrief == null) throw new ArgumentNullException(nameof(debrief));
            var copy = new List<Entry>(debrief.Timeline.Count);
            foreach (var record in debrief.Timeline)
            {
                string? description = Describe(record);
                if (description != null) copy.Add(new Entry(record, Cause(record), description));
            }
            return copy.AsReadOnly();
        }

        private static Guid Cause(SessionTraceRecord record) => record.ReactorChange?.CauseId ??
            (record.MaterialCauseId != Guid.Empty ? record.MaterialCauseId : record.CauseId);

        public void Refresh()
        {
            var trace = queries.Trace;
            SourceDroppedRecords = trace.DroppedRecords; SequenceExhausted = trace.SequenceExhausted;
            foreach (var record in trace.Records)
            {
                if (record.Epoch != epoch) throw new InvalidOperationException("A fixture trace display cannot consume another world epoch.");
                if (record.Sequence <= lastSequence) continue;
                if (record.Sequence != lastSequence + 1) GapDetected = true;
                lastSequence = record.Sequence;
                if (!record.Changed) continue; // A historical replay cannot publish another committed display event.
                string? description = Describe(record);
                if (description == null) continue;
                Guid cause = Cause(record);
                if (entries.Count == 12) entries.RemoveAt(0);
                entries.Add(new Entry(record, cause, description));
            }
        }

        private static string? Describe(SessionTraceRecord record)
        {
            if (record.ContaminationContact != null && record.Changed)
            {
                var contact = record.ContaminationContact;
                return (contact.Kind == WorkerContaminationKind.Exposure ? "Contamination exposure" : "Decontamination") +
                    " · " + contact.Before + " -> " + contact.After;
            }
            if (record.MedicalChange != null)
            {
                var care = record.MedicalChange;
                switch (care.Kind)
                {
                    case MedicalEvent.Inserted: return "Worker loaded into stabilization chamber";
                    case MedicalEvent.Started: return "Stabilization started · spent " + care.ReserveSpent + " reserve and one cartridge";
                    case MedicalEvent.Completed: return "Worker stabilized · eject before standing recovery";
                    case MedicalEvent.Cancelled: return "Stabilization cancelled · spent resources retained";
                    case MedicalEvent.Interrupted: return "Stabilization interrupted · patient condition changed";
                    case MedicalEvent.Ejected: return "Worker ejected from stabilization chamber";
                    case MedicalEvent.PatientDisconnected: return "Disconnected patient released from stabilization chamber";
                    case MedicalEvent.EmergencyEjected: return "Awake patient opened their own chamber · standing clearance still required";
                }
            }
            if (record.DemandChange != null)
            {
                var wave = record.DemandChange.Wave;
                return "Grid window " + (wave.Met ? "met" : "missed") + " · " + wave.Label + " · " +
                    wave.DeliveredEnergyUnits + "/" + wave.RequiredEnergyUnits + " energy";
            }
            if (record.ProductionEvent.HasValue)
            {
                switch (record.ProductionEvent.Value)
                {
                    case ProductionEvent.Jammed: return "Machine jammed";
                    case ProductionEvent.Completed: return "Processing complete · " + (record.WasteUnits ?? 0) + " units to waste";
                    case ProductionEvent.Cancelled: return "Machine cycle cancelled";
                }
            }
            var reactor = record.ReactorChange;
            if (record.ReactorEvent.HasValue && reactor != null)
            {
                switch (record.ReactorEvent.Value)
                {
                    case ReactorEvent.Generated: return null; // Current output already has an instrument; do not bury incidents in generation ticks.
                    case ReactorEvent.Warning: return "Reactor warning · " + Risk(reactor.Risk);
                    case ReactorEvent.Tripped: return "Reactor tripped · " + Risk(reactor.Risk);
                    case ReactorEvent.FuelExhausted: return "Fuel exhausted · spent material retained";
                    case ReactorEvent.EmergencyCooling: return "Emergency cooling · spent " + reactor.SpentUnits + " reserve";
                    case ReactorEvent.CoolingChanged: return reactor.State.Cooling ? "Cooling opened" : "Cooling closed";
                    case ReactorEvent.Started: return "Reactor started";
                    case ReactorEvent.Shutdown: return "Reactor shut down";
                    case ReactorEvent.Reset: return "Reactor trip reset · core remains shut down";
                    case ReactorEvent.Inserted: return "Fuel loaded";
                    case ReactorEvent.Ejected: return "Fuel container ejected";
                    case ReactorEvent.AuxiliaryPower: return "Reserve power used";
                }
            }
            switch (record.Kind)
            {
                case SessionTraceKind.Impact: return "Worker impact · " + record.ImpactSeverity;
                case SessionTraceKind.Aid: return "Worker stabilized";
                case SessionTraceKind.RecoveryRequested: return "Standing recovery started";
                case SessionTraceKind.RecoveryResolved: return "Standing recovery resolved · " + record.WorkerResult;
                case SessionTraceKind.RecoveryCancelled: return "Standing recovery cancelled";
                case SessionTraceKind.RecoveryExpired: return "Standing recovery expired";
                case SessionTraceKind.Disconnected: return "Worker disconnected";
                case SessionTraceKind.Evacuation: return "Evacuation activated";
                case SessionTraceKind.AttachmentFailed: return "Grip released · physical binding failed";
                case SessionTraceKind.LeaseExpired: return "Grip released · lease expired";
                case SessionTraceKind.Started: return "Shift started";
                case SessionTraceKind.Ended: return "Shift ended · " + record.Outcome;
                case SessionTraceKind.Stopped: return "Fixture stopped";
                case SessionTraceKind.Faulted: return "World faulted";
                default: return null;
            }
        }
        private static string Risk(ReactorRisk risk) => risk == ReactorRisk.CoolingLost ? "cooling lost" :
            risk == ReactorRisk.SuspectFuel ? "suspect fuel" : "no recorded risk";
    }
}
