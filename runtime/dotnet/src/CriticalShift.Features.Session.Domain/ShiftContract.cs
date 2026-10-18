#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Session.Domain
{
    /// <summary>A contiguous demand period ends at this shift-clock coordinate.</summary>
    public sealed class DemandPeriod
    {
        public DemandPeriod(Guid id, string label, long endMilliseconds, long requiredEnergyUnits,
            long warningMilliseconds = 0)
        {
            if (id == Guid.Empty) throw new ArgumentException("A demand-period identity is required.", nameof(id));
            if (string.IsNullOrWhiteSpace(label) || label.Length > 80) throw new ArgumentException("A short demand label is required.", nameof(label));
            if (endMilliseconds <= 0 || requiredEnergyUnits < 0 || warningMilliseconds < 0)
                throw new ArgumentOutOfRangeException(nameof(endMilliseconds));
            Id = id; Label = label; EndMilliseconds = endMilliseconds;
            RequiredEnergyUnits = requiredEnergyUnits; WarningMilliseconds = warningMilliseconds;
        }
        public Guid Id { get; }
        public string Label { get; }
        public long EndMilliseconds { get; }
        public long RequiredEnergyUnits { get; }
        public long WarningMilliseconds { get; }
    }

    public sealed class ContractPlan
    {
        public ContractPlan(Guid id, string title, IReadOnlyList<DemandPeriod> periods)
        {
            if (id == Guid.Empty) throw new ArgumentException("A contract identity is required.", nameof(id));
            if (string.IsNullOrWhiteSpace(title) || title.Length > 120) throw new ArgumentException("A short contract title is required.", nameof(title));
            if (periods == null) throw new ArgumentNullException(nameof(periods));
            if (periods.Count < 1 || periods.Count > 32) throw new ArgumentOutOfRangeException(nameof(periods));
            var copy = new DemandPeriod[periods.Count]; var identities = new HashSet<Guid>();
            long end = 0, total = 0;
            for (int i = 0; i < copy.Length; i++)
            {
                var period = periods[i] ?? throw new ArgumentException("Demand periods cannot be null.", nameof(periods));
                if (!identities.Add(period.Id) || period.EndMilliseconds <= end || period.WarningMilliseconds > end)
                    throw new ArgumentException("Demand periods require unique identities, increasing endpoints and a warning within the preceding shift.", nameof(periods));
                total = checked(total + period.RequiredEnergyUnits); end = period.EndMilliseconds;
                copy[i] = period;
            }
            Id = id; Title = title; Periods = Array.AsReadOnly(copy);
            DurationMilliseconds = end; RequiredEnergyUnits = total;
        }
        public Guid Id { get; }
        public string Title { get; }
        public IReadOnlyList<DemandPeriod> Periods { get; }
        public long DurationMilliseconds { get; }
        public long RequiredEnergyUnits { get; }
    }

    public sealed class DemandPeriodProgress
    {
        internal DemandPeriodProgress(DemandPeriod period, long start, long delivered, bool settled)
        { Period = period; StartMilliseconds = start; DeliveredEnergyUnits = delivered; Settled = settled; }
        public DemandPeriod Period { get; }
        public long StartMilliseconds { get; }
        public long DeliveredEnergyUnits { get; }
        public bool Settled { get; }
        public bool Met => DeliveredEnergyUnits >= Period.RequiredEnergyUnits;
        public long ShortfallEnergyUnits => Math.Max(0, Period.RequiredEnergyUnits - DeliveredEnergyUnits);
    }

    /// <summary>
    /// Session-owned objective assessment over observations of the Power owner's
    /// cumulative grid delivery. It never generates, transfers or spends energy.
    /// </summary>
    public sealed class ShiftContract
    {
        private readonly long[] delivered;
        private long previousDelivery;
        private int settled;

        public ShiftContract(ContractPlan plan, long initialDeliveredEnergy = 0)
        {
            Plan = plan ?? throw new ArgumentNullException(nameof(plan));
            if (initialDeliveredEnergy < 0) throw new ArgumentOutOfRangeException(nameof(initialDeliveredEnergy));
            previousDelivery = initialDeliveredEnergy; delivered = new long[plan.Periods.Count];
        }
        public ContractPlan Plan { get; }
        public long ElapsedMilliseconds { get; private set; }
        public int SettledPeriods => settled;
        public bool Complete => settled == delivered.Length;
        public long NextBoundaryMilliseconds => Complete ? Plan.DurationMilliseconds : Plan.Periods[settled].EndMilliseconds;
        public long DeliveredEnergyUnits { get; private set; }
        public bool AllPeriodsMet
        {
            get
            {
                if (!Complete) return false;
                for (int i = 0; i < delivered.Length; i++)
                    if (delivered[i] < Plan.Periods[i].RequiredEnergyUnits) return false;
                return true;
            }
        }
        public IReadOnlyList<DemandPeriodProgress> Snapshot()
        {
            var copy = new DemandPeriodProgress[delivered.Length]; long start = 0;
            for (int i = 0; i < copy.Length; i++)
            {
                copy[i] = new DemandPeriodProgress(Plan.Periods[i], start, delivered[i], i < settled);
                start = Plan.Periods[i].EndMilliseconds;
            }
            return Array.AsReadOnly(copy);
        }

        /// <returns>True only when this observation settles one demand period.</returns>
        public bool AdvanceTo(long shiftMilliseconds, long cumulativeDeliveredEnergy)
        {
            if (shiftMilliseconds < ElapsedMilliseconds || shiftMilliseconds > Plan.DurationMilliseconds ||
                cumulativeDeliveredEnergy < previousDelivery)
                throw new ArgumentOutOfRangeException(nameof(shiftMilliseconds), "Contract observations must be monotonic and within the shift.");
            if (Complete)
            {
                if (shiftMilliseconds == ElapsedMilliseconds && cumulativeDeliveredEnergy == previousDelivery) return false;
                throw new InvalidOperationException("A completed contract cannot accept later delivery.");
            }
            if (shiftMilliseconds > NextBoundaryMilliseconds)
                throw new InvalidOperationException("Observe delivery at every demand boundary before advancing beyond it.");
            long delta = cumulativeDeliveredEnergy - previousDelivery;
            if (shiftMilliseconds == ElapsedMilliseconds && delta != 0)
                throw new InvalidOperationException("Delivery cannot increase without advancing the shift clock.");
            long periodTotal = checked(delivered[settled] + delta);
            long total = checked(DeliveredEnergyUnits + delta);
            delivered[settled] = periodTotal; DeliveredEnergyUnits = total;
            previousDelivery = cumulativeDeliveredEnergy; ElapsedMilliseconds = shiftMilliseconds;
            if (shiftMilliseconds != NextBoundaryMilliseconds) return false;
            settled++; return true;
        }
    }
}
