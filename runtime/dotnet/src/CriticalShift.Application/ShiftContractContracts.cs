#nullable enable
using System;
using System.Collections.Generic;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    /// <summary>Authored energy within a window, not a continuous minimum-power requirement.</summary>
    public sealed class GridDemandWave
    {
        public GridDemandWave(Guid id, string label, long endMilliseconds, long requiredEnergyUnits,
            long warningMilliseconds = 0)
        { Rules = new DemandPeriod(id, label, endMilliseconds, requiredEnergyUnits, warningMilliseconds); }
        internal DemandPeriod Rules { get; }
    }

    public sealed class ShiftContractDefinition
    {
        public ShiftContractDefinition(Guid id, string title, params GridDemandWave[] waves)
        {
            if (waves == null) throw new ArgumentNullException(nameof(waves));
            var periods = new DemandPeriod[waves.Length];
            for (int i = 0; i < periods.Length; i++)
                periods[i] = waves[i]?.Rules ?? throw new ArgumentException("Demand waves cannot be null.", nameof(waves));
            Rules = new ContractPlan(id, title, periods);
        }
        internal ContractPlan Rules { get; }
        public Guid Id => Rules.Id;
        public string Title => Rules.Title;
        public long DurationMilliseconds => Rules.DurationMilliseconds;
        public long RequiredEnergyUnits => Rules.RequiredEnergyUnits;
    }

    public sealed class GridDemandView
    {
        internal GridDemandView(DemandPeriodProgress progress)
        {
            Id = progress.Period.Id; Label = progress.Period.Label;
            StartMilliseconds = progress.StartMilliseconds; EndMilliseconds = progress.Period.EndMilliseconds;
            WarningAtMilliseconds = StartMilliseconds - progress.Period.WarningMilliseconds;
            RequiredEnergyUnits = progress.Period.RequiredEnergyUnits; DeliveredEnergyUnits = progress.DeliveredEnergyUnits;
            Settled = progress.Settled; Met = progress.Met; ShortfallEnergyUnits = progress.ShortfallEnergyUnits;
        }
        public Guid Id { get; }
        public string Label { get; }
        public long StartMilliseconds { get; }
        public long EndMilliseconds { get; }
        public long WarningAtMilliseconds { get; }
        public long RequiredEnergyUnits { get; }
        public long DeliveredEnergyUnits { get; }
        public long ShortfallEnergyUnits { get; }
        public bool Settled { get; }
        public bool Met { get; }
    }

    public sealed class ShiftContractView
    {
        internal ShiftContractView(Guid epoch, ShiftContract state, WorldPhase phase, WorldOutcome outcome)
        {
            Epoch = epoch; Id = state.Plan.Id; Title = state.Plan.Title; ElapsedMilliseconds = state.ElapsedMilliseconds;
            DurationMilliseconds = state.Plan.DurationMilliseconds; DeliveredEnergyUnits = state.DeliveredEnergyUnits;
            RequiredEnergyUnits = state.Plan.RequiredEnergyUnits; SettledPeriods = state.SettledPeriods;
            Complete = state.Complete; AllPeriodsMet = state.AllPeriodsMet; Phase = phase; Outcome = outcome;
            var periods = state.Snapshot(); var copy = new GridDemandView[periods.Count];
            for (int i = 0; i < copy.Length; i++) copy[i] = new GridDemandView(periods[i]);
            Waves = Array.AsReadOnly(copy);
        }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public string Title { get; }
        public long ElapsedMilliseconds { get; }
        public long DurationMilliseconds { get; }
        public long DeliveredEnergyUnits { get; }
        public long RequiredEnergyUnits { get; }
        public int SettledPeriods { get; }
        public bool Complete { get; }
        public bool AllPeriodsMet { get; }
        public WorldPhase Phase { get; }
        public WorldOutcome Outcome { get; }
        public IReadOnlyList<GridDemandView> Waves { get; }
        public GridDemandView? Current => Complete ? null : Waves[SettledPeriods];
        public GridDemandView? Upcoming
        {
            get
            {
                int next = SettledPeriods + 1;
                return next < Waves.Count && ElapsedMilliseconds >= Waves[next].WarningAtMilliseconds ? Waves[next] : null;
            }
        }
    }

    public sealed class GridDemandChange
    {
        internal GridDemandChange(Guid epoch, Guid contract, GridDemandView wave)
        { Epoch = epoch; ContractId = contract; Wave = wave; }
        public Guid Epoch { get; }
        public Guid ContractId { get; }
        public GridDemandView Wave { get; }
        public long ShiftMilliseconds => Wave.EndMilliseconds;
    }
}
