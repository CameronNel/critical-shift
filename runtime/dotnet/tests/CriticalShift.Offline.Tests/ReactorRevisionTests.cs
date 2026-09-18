using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ReactorRevisionTests
    {
        [TestCase(ReactorMode.Empty)]
        [TestCase(ReactorMode.Loaded)]
        [TestCase(ReactorMode.Shutdown)]
        [TestCase(ReactorMode.Tripped)]
        [TestCase(ReactorMode.Exhausted)]
        public void IdleSamplesPreserveReactorRevisionAndPendingCommand(ReactorMode mode)
        {
            var f = new ReactorFixture();
            switch (mode)
            {
                case ReactorMode.Loaded: f.Load(); break;
                case ReactorMode.Shutdown:
                    f.Run(); f.World.AdvanceTo(100); f.Act(ReactorAction.Shutdown); break;
                case ReactorMode.Tripped:
                    f.Run(); f.Act(ReactorAction.SetCooling, false); f.World.AdvanceTo(800); break;
                case ReactorMode.Exhausted:
                    f.Run(); f.World.AdvanceTo(1000); break;
            }
            var before = f.World.Reactor.View!;
            Assert.That(before.Mode, Is.EqualTo(mode));
            long sampledAt = f.World.View.HostMilliseconds;
            var pending = new ReactorRequest(ReactorAction.SetCooling, before.Revision, cooling: !before.Cooling);
            foreach (long delta in new long[] { 1, 10, 100, 250 })
            {
                Assert.That(f.World.AdvanceTo(sampledAt + delta).ReactorChanges, Is.Empty);
                var after = f.World.Reactor.View!;
                Assert.That(VisibleFields(after), Is.EqualTo(VisibleFields(before)));
                Assert.That(after.Revision, Is.EqualTo(before.Revision),
                    "An internal clock sample must not invalidate an unchanged public projection.");
            }
            Assert.That(f.Send(pending).Reactor!.Status, Is.EqualTo(ReactorStatus.Applied));
            Assert.That(f.World.Reactor.View!.Revision, Is.EqualTo(before.Revision + 1));
        }

        [TestCase(false)]
        [TestCase(true)]
        public void IdleSamplesStillAdvanceTheInternalClockBeforeStarting(bool restart)
        {
            var f = new ReactorFixture();
            if (restart)
            {
                f.Run(); f.World.AdvanceTo(100); f.Act(ReactorAction.Shutdown);
            }
            else
            {
                f.Load(); f.Act(ReactorAction.SetCooling, true);
            }
            long previousWork = f.World.Reactor.View!.WorkMilliseconds;
            f.World.AdvanceTo(5000);
            Assert.That(f.Act(ReactorAction.Start).HasNewCommit, Is.True);
            long generated = f.World.Reactor.View!.Power.Generated;
            f.World.AdvanceTo(5001);
            Assert.That(f.World.Reactor.View!.WorkMilliseconds, Is.EqualTo(previousWork + 1));
            Assert.That(f.World.Reactor.View.Power.Generated, Is.EqualTo(generated),
                "Idle time must not become fuel work or generated power after startup.");
        }

        [TestCase("sub-quantum-work")]
        [TestCase("generated-power")]
        [TestCase("shutdown-cooldown")]
        [TestCase("trip-cooldown")]
        [TestCase("exhausted-cooldown")]
        public void ObservableTickChangesStillInvalidateStaleCommands(string change)
        {
            var f = change == "exhausted-cooldown"
                ? new ReactorFixture(units: 4, contamination: 1000) : new ReactorFixture();
            f.Run();
            long nextSample;
            switch (change)
            {
                case "sub-quantum-work": nextSample = 1; break;
                case "generated-power": nextSample = 100; break;
                case "shutdown-cooldown":
                    f.Act(ReactorAction.SetCooling, false); f.World.AdvanceTo(200);
                    f.Act(ReactorAction.Shutdown); f.Act(ReactorAction.SetCooling, true);
                    nextSample = 250; break;
                case "trip-cooldown":
                    f.Act(ReactorAction.SetCooling, false); f.World.AdvanceTo(800);
                    f.Act(ReactorAction.SetCooling, true); nextSample = 900; break;
                case "exhausted-cooldown": f.World.AdvanceTo(400); nextSample = 450; break;
                default: throw new ArgumentOutOfRangeException(nameof(change));
            }
            var before = f.World.Reactor.View!;
            f.World.AdvanceTo(nextSample);
            var after = f.World.Reactor.View!;
            Assert.That(VisibleFields(after), Is.Not.EqualTo(VisibleFields(before)));
            Assert.That(after.Revision, Is.EqualTo(before.Revision + 1));
            Assert.That(f.Send(new ReactorRequest(ReactorAction.AuxiliaryPower, before.Revision))
                .Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict));
            Assert.That(f.World.Reactor.View!.Power.Spent, Is.EqualTo(after.Power.Spent));
        }

        [Test]
        public void RepeatedSameClockSampleNeverChangesReactorRevision()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(100);
            var before = f.World.Reactor.View!;
            for (int i = 0; i < 20; i++)
            {
                Assert.That(f.World.AdvanceTo(100).ReactorChanges, Is.Empty);
                Assert.That(f.World.Reactor.View!.Revision, Is.EqualTo(before.Revision));
            }
            Assert.That(VisibleFields(f.World.Reactor.View!), Is.EqualTo(VisibleFields(before)));
        }

        private static object?[] VisibleFields(ReactorView view) => new object?[]
        {
            view.Epoch, view.Id, view.DefinitionId, view.Mode, view.Cooling, view.SuspectFuel,
            view.WorkMilliseconds, view.RemainingFuelMilliseconds, view.InstabilityMilliseconds,
            view.CycleId, view.Fuel?.BatchId, view.Fuel?.Revision, view.Fuel?.Kind, view.Fuel?.Units,
            view.Power.Initial, view.Power.Capacity, view.Power.Available, view.Power.Generated,
            view.Power.Spent, view.Power.Delivered, view.Power.Spilled
        };
    }
}
