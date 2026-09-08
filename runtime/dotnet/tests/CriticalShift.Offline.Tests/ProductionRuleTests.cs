using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Features.Materials.Domain;
using CriticalShift.Features.Production.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ProductionRuleTests
    {
        private static BatchSnapshot Batch(int units = 100) => new BatchSnapshot(Fixture.Id(1), Fixture.Id(2), Fixture.Id(3), Fixture.Id(4), BatchKind.Ore, units, 450, 30);
        private static ConversionPlan Plan(MaterialLedger ledger, int id = 20, int yield = 800) =>
            ledger.Prepare(Fixture.Id(1), ledger.Get(Fixture.Id(1))!.Revision, Fixture.Id(id), Fixture.Id(5), Fixture.Id(6),
                Fixture.Id(100 + id), BatchKind.CrushedOre, yield, 10, true);
        [Test]
        public void MaterialPrepareAndReservationDoNotConsumeInputs()
        {
            var ledger = new MaterialLedger(1, 2); var original = Batch(); ledger.Register(original);
            var plan = Plan(ledger); Assert.That(ledger.PendingCount, Is.Zero); ledger.Reserve(plan);
            Assert.That(ledger.Get(original.ContainerId), Is.SameAs(original));
            Assert.That(ledger.ActiveUnits, Is.EqualTo(100)); Assert.That(ledger.WasteUnits, Is.Zero);
        }
        [Test]
        public void ConversionCompletionAndCancellationAreSticky()
        {
            var ledger = new MaterialLedger(1, 2); ledger.Register(Batch()); var plan = Plan(ledger); ledger.Reserve(plan);
            var first = ledger.Finish(plan.CycleId, false);
            Assert.That(ledger.Finish(plan.CycleId, false), Is.SameAs(first));
            Assert.That(ledger.Finish(plan.CycleId, true), Is.SameAs(first));
            Assert.That(ledger.WasteUnits, Is.EqualTo(20)); Assert.That(ledger.ActiveUnits, Is.EqualTo(80));
            var next = Plan(ledger, 21); ledger.Reserve(next); var cancel = ledger.Finish(next.CycleId, true);
            Assert.That(ledger.Finish(next.CycleId, false), Is.SameAs(cancel));
            Assert.That(ledger.ActiveUnits + ledger.WasteUnits, Is.EqualTo(100));
            Assert.That(ledger.ReceiptCount, Is.EqualTo(2));
        }
        [Test]
        public void ReservedCapacityGuaranteesCompletionAtBudgetLimit()
        {
            var ledger = new MaterialLedger(1, 1); ledger.Register(Batch()); var p = Plan(ledger); ledger.Reserve(p);
            Assert.That(ledger.HasCycleCapacity, Is.False);
            Assert.That(ledger.Finish(p.CycleId, false).Status, Is.EqualTo(ConversionStatus.Completed));
            Assert.Throws<InvalidOperationException>(() => Plan(ledger, 22));
        }
        [Test]
        public void ConversionInvalidInputsAndStalePlansAreNonMutating()
        {
            var ledger = new MaterialLedger(1, 4); ledger.Register(Batch());
            Assert.Throws<ArgumentOutOfRangeException>(() => Plan(ledger, yield: 1001));
            Assert.Throws<ArgumentOutOfRangeException>(() => Plan(ledger, yield: 1));
            var p = Plan(ledger); var stale = Plan(ledger, 21); ledger.Reserve(p); ledger.Finish(p.CycleId, false);
            Assert.Throws<InvalidOperationException>(() => ledger.Reserve(stale));
            Assert.That(ledger.PendingCount, Is.Zero); Assert.That(ledger.ActiveUnits, Is.EqualTo(80));
        }
        [Test]
        public void MaterialIdsAndCapacityCannotBeReused()
        {
            var ledger = new MaterialLedger(1, 2); ledger.Register(Batch());
            Assert.Throws<InvalidOperationException>(() => ledger.Register(Batch()));
            Assert.Throws<InvalidOperationException>(() => ledger.Register(new BatchSnapshot(Fixture.Id(9), Fixture.Id(8), Fixture.Id(3), Fixture.Id(4), BatchKind.Ore, 100, 0, 0)));
            Assert.That(ledger.IssuedUnits, Is.EqualTo(100));
            ledger.Clear(); Assert.That(ledger.Count, Is.Zero); Assert.That(ledger.IssuedUnits, Is.Zero);
        }
        [TestCase(1)] [TestCase(100)] [TestCase(999)] [TestCase(1000)]
        public void IntegerYieldAccountsForRoundingAsWaste(int yield)
        {
            var ledger = new MaterialLedger(1, 1); ledger.Register(Batch(1001));
            var p = Plan(ledger, yield: yield); ledger.Reserve(p); var r = ledger.Finish(p.CycleId, false);
            Assert.That(r.Plan.Output.Units, Is.EqualTo(1001L * yield / 1000));
            Assert.That(r.Plan.Output.Units + r.Plan.WasteUnits, Is.EqualTo(1001));
            Assert.That(r.Plan.Output.Flags, Is.EqualTo(BatchFlags.BypassedInspection));
        }
        [Test]
        public void TwoReservationsCannotUseTheSameContainer()
        {
            var ledger = new MaterialLedger(1, 3); ledger.Register(Batch()); var p = Plan(ledger); ledger.Reserve(p);
            Assert.Throws<InvalidOperationException>(() => Plan(ledger, 21));
            Assert.Throws<InvalidOperationException>(() => ledger.Reserve(p));
            Assert.That(ledger.PendingCount, Is.EqualTo(1));
        }
        [Test]
        public void MachineTimeIsExplicitAndImmutable()
        {
            var start = new MachineState(Fixture.Id(1)).Begin(Fixture.Id(2), 100, 0, 1000);
            var next = start.AdvanceTo(1050, out _);
            Assert.That(start.WorkMilliseconds, Is.Zero); Assert.That(next.WorkMilliseconds, Is.EqualTo(50));
            Assert.Throws<ArgumentOutOfRangeException>(() => next.AdvanceTo(1049, out _));
            Assert.That(next.AdvanceTo(1050, out _), Is.SameAs(next));
            Assert.That(next.AdvanceTo(long.MaxValue, out var signal).WorkMilliseconds, Is.EqualTo(100));
            Assert.That(signal, Is.EqualTo(MachineSignal.Completed));
        }
        [Test]
        public void MachineJamsAtThresholdNotAtOvershotCompletion()
        {
            var state = new MachineState(Fixture.Id(1)).Begin(Fixture.Id(2), 1000, 300, 0);
            state = state.AdvanceTo(5000, out var signal);
            Assert.That(signal, Is.EqualTo(MachineSignal.Jammed)); Assert.That(state.WorkMilliseconds, Is.EqualTo(300));
            state = state.SetPower(false).Repair().SetPower(true).Resume();
            state = state.AdvanceTo(5699, out signal); Assert.That(signal, Is.EqualTo(MachineSignal.None));
            state = state.AdvanceTo(5700, out signal); Assert.That(signal, Is.EqualTo(MachineSignal.Completed));
        }
        [Test]
        public void MachineInvalidTransitionsAreRejected()
        {
            var s = new MachineState(Fixture.Id(1));
            Assert.Throws<InvalidOperationException>(() => s.Resume());
            Assert.Throws<InvalidOperationException>(() => s.Repair());
            Assert.Throws<InvalidOperationException>(() => s.Reset(true));
            s = s.Begin(Fixture.Id(2), 1000, 100, 0);
            Assert.Throws<InvalidOperationException>(() => s.Reset(false));
            Assert.Throws<InvalidOperationException>(() => s.Begin(Fixture.Id(3), 100, 0, 0));
        }

        public static IEnumerable<int> MachineSeeds => Enumerable.Range(1, 100);
        [TestCaseSource(nameof(MachineSeeds))]
        public void MachineModelMatchesIndependentStateTransitions(int seed)
        {
            var actual = new MachineState(Fixture.Id(1));
            int mode = 0; bool power = true, armed = false; long now = 0, work = 0; uint rng = (uint)seed;
            for (int step = 0; step < 200; step++)
            {
                rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
                int op = (int)(rng % 6);
                if (op == 0)
                {
                    long delta = 1 + (rng >> 10) % 150; now += delta;
                    if (mode == 1)
                    {
                        work += delta;
                        if (armed && work >= 200) { work = 200; mode = 3; }
                        else if (work >= 500) { work = 500; mode = 4; }
                    }
                    actual = actual.AdvanceTo(now, out _);
                }
                else if (op == 1)
                { power = !power; if (!power && mode == 1) mode = 2; actual = actual.SetPower(power); }
                else if (op == 2 && mode == 2 && power)
                { mode = 1; actual = actual.Resume(); }
                else if (op == 3 && mode == 3 && !power)
                { armed = false; mode = 2; actual = actual.Repair(); }
                else if (op == 4 && (mode == 4 || (mode == 2 || mode == 3) && !power))
                { actual = actual.Reset(mode != 4); mode = 0; work = 0; armed = false; }
                else if (op == 5 && mode == 0 && power)
                { armed = (rng & 256) != 0; work = 0; mode = 1; actual = actual.Begin(Fixture.Id(1000 + step), 500, armed ? 200 : 0, now); }
                string trace = $"machine seed={seed} step={step} op={op}";
                Assert.That((int)actual.Mode, Is.EqualTo(mode), trace);
                Assert.That(actual.Powered, Is.EqualTo(power), trace);
                Assert.That(actual.WorkMilliseconds, Is.EqualTo(work), trace);
                Assert.That(actual.JamArmed, Is.EqualTo(armed), trace);
            }
        }
    }
}
