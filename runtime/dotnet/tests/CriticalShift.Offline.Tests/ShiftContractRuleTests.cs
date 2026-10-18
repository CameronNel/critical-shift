using System;
using System.Collections.Generic;
using CriticalShift.Features.Session.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ShiftContractRuleTests
    {
        private static DemandPeriod Period(int id, long end, long required, long warning = 0) =>
            new DemandPeriod(Fixture.Id(id), "Demand " + id, end, required, warning);
        private static ContractPlan Plan(params DemandPeriod[] periods) => new ContractPlan(Fixture.Id(900), "Grid restoration", periods);

        [Test] public void ContractPlanCopiesAuthoredPeriodsAndRejectsDuplicateOrUnorderedWindows()
        {
            var original = new[] { Period(901, 100, 0), Period(902, 200, 4, 50) };
            var plan = Plan(original); original[0] = Period(903, 50, 3);
            Assert.That(plan.Periods[0].EndMilliseconds, Is.EqualTo(100));
            Assert.That(plan.RequiredEnergyUnits, Is.EqualTo(4)); Assert.That(plan.DurationMilliseconds, Is.EqualTo(200));
            Assert.Throws<ArgumentException>(() => Plan(Period(901, 100, 1), Period(901, 200, 1)));
            Assert.Throws<ArgumentException>(() => Plan(Period(901, 100, 1), Period(902, 100, 1)));
            Assert.Throws<ArgumentException>(() => Plan(Period(901, 100, 1, 1)));
        }

        [Test] public void ContractDefinitionsHaveBoundedCountsAndCheckedQuotaArithmetic()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => Plan());
            var tooMany = new DemandPeriod[33];
            for (int i = 0; i < tooMany.Length; i++) tooMany[i] = Period(901 + i, i + 1, 1);
            Assert.Throws<ArgumentOutOfRangeException>(() => Plan(tooMany));
            Assert.Throws<OverflowException>(() => Plan(Period(901, 100, long.MaxValue), Period(902, 200, 1)));
            Assert.Throws<ArgumentException>(() => new DemandPeriod(Guid.Empty, "missing", 10, 1));
            Assert.Throws<ArgumentException>(() => new DemandPeriod(Fixture.Id(901), " ", 10, 1));
            Assert.Throws<ArgumentOutOfRangeException>(() => Period(901, 0, 1));
            Assert.Throws<ArgumentOutOfRangeException>(() => Period(901, 10, -1));
            Assert.Throws<ArgumentOutOfRangeException>(() => Period(901, 10, 1, -1));
            Assert.Throws<ArgumentNullException>(() => new ShiftContract(null!));
        }

        [Test] public void BoundaryCreditBelongsOnlyToTheEndingDemandPeriod()
        {
            var state = new ShiftContract(Plan(Period(901, 1000, 8), Period(902, 2000, 4)));
            Assert.That(state.AdvanceTo(999, 4), Is.False);
            Assert.That(state.AdvanceTo(1000, 8), Is.True);
            var first = state.Snapshot();
            Assert.That(first[0].DeliveredEnergyUnits, Is.EqualTo(8)); Assert.That(first[0].Settled, Is.True);
            Assert.That(first[1].DeliveredEnergyUnits, Is.Zero); Assert.That(state.Complete, Is.False);
            state.AdvanceTo(1500, 10); state.AdvanceTo(2000, 12);
            Assert.That(state.Snapshot()[1].DeliveredEnergyUnits, Is.EqualTo(4)); Assert.That(state.AllPeriodsMet, Is.True);
            Assert.That(first[1].DeliveredEnergyUnits, Is.Zero, "A retained snapshot cannot change with the owner.");
        }

        [Test] public void SurplusCannotPrepayALaterWindowOrRepairAMissedEarlierWindow()
        {
            var state = new ShiftContract(Plan(Period(901, 1000, 4), Period(902, 2000, 4)));
            state.AdvanceTo(1000, 100); Assert.That(state.AllPeriodsMet, Is.False);
            state.AdvanceTo(2000, 100);
            Assert.That(state.DeliveredEnergyUnits, Is.EqualTo(100)); Assert.That(state.AllPeriodsMet, Is.False);
            Assert.That(state.Snapshot()[1].ShortfallEnergyUnits, Is.EqualTo(4));
            var late = new ShiftContract(state.Plan); late.AdvanceTo(1000, 0); late.AdvanceTo(2000, 100);
            Assert.That(late.Snapshot()[0].Met, Is.False); Assert.That(late.AllPeriodsMet, Is.False);
        }

        [Test] public void SkippedBoundariesAndInvalidObservationsLeaveProgressUntouched()
        {
            var state = new ShiftContract(Plan(Period(901, 100, 2), Period(902, 200, 2)));
            Assert.Throws<InvalidOperationException>(() => state.AdvanceTo(200, 4));
            Assert.Throws<InvalidOperationException>(() => state.AdvanceTo(0, 1));
            Assert.That(state.ElapsedMilliseconds, Is.Zero); Assert.That(state.DeliveredEnergyUnits, Is.Zero);
            state.AdvanceTo(50, 1);
            Assert.Throws<ArgumentOutOfRangeException>(() => state.AdvanceTo(49, 1));
            Assert.Throws<ArgumentOutOfRangeException>(() => state.AdvanceTo(60, 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => state.AdvanceTo(201, 2));
            Assert.That(state.ElapsedMilliseconds, Is.EqualTo(50)); Assert.That(state.DeliveredEnergyUnits, Is.EqualTo(1));
        }

        [Test] public void DuplicateSamplesAndACompletedContractCannotDoubleCountPower()
        {
            var state = new ShiftContract(Plan(Period(901, 100, 2)), initialDeliveredEnergy: 10);
            state.AdvanceTo(50, 11);
            for (int i = 0; i < 100; i++) Assert.That(state.AdvanceTo(50, 11), Is.False);
            Assert.That(state.AdvanceTo(100, 12), Is.True);
            for (int i = 0; i < 100; i++) Assert.That(state.AdvanceTo(100, 12), Is.False);
            Assert.That(state.DeliveredEnergyUnits, Is.EqualTo(2)); Assert.That(state.AllPeriodsMet, Is.True);
            Assert.Throws<InvalidOperationException>(() => state.AdvanceTo(100, 13));
        }

        [Test] public void DemandSnapshotsCannotBeUsedToMutateTheOwner()
        {
            var state = new ShiftContract(Plan(Period(901, 100, 2))); var snapshot = state.Snapshot();
            Assert.Throws<NotSupportedException>(() => ((IList<DemandPeriodProgress>)snapshot).Clear());
            state.AdvanceTo(100, 2); Assert.That(snapshot[0].Settled, Is.False);
            Assert.That(snapshot[0].DeliveredEnergyUnits, Is.Zero); Assert.That(state.Snapshot()[0].Met, Is.True);
        }

        [TestCase(1)]
        [TestCase(7)]
        [TestCase(100)]
        public void ContractAssessmentIsIndependentOfSamplesWithinEachWindow(int step)
        {
            var state = new ShiftContract(Plan(Period(901, 100, 0), Period(902, 300, 8, 50), Period(903, 500, 8, 100)));
            foreach (long boundary in new long[] { 100, 300, 500 })
            {
                while (state.ElapsedMilliseconds < boundary)
                {
                    long sample = Math.Min(boundary, state.ElapsedMilliseconds + step);
                    long energy = sample <= 100 ? 0 : (sample - 100) / 25;
                    state.AdvanceTo(sample, energy);
                }
            }
            Assert.That(state.AllPeriodsMet, Is.True); Assert.That(state.DeliveredEnergyUnits, Is.EqualTo(16));
            Assert.That(state.Snapshot()[1].DeliveredEnergyUnits, Is.EqualTo(8));
            Assert.That(state.Snapshot()[2].DeliveredEnergyUnits, Is.EqualTo(8));
        }
    }
}
