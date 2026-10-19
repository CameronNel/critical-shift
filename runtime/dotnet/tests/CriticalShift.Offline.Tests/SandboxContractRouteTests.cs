using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Sandbox;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SandboxContractRouteTests
    {
        [TestCase(0, false, 1320, true)]
        [TestCase(10000, false, 1280, true)]
        [TestCase(10000, true, 1280, true)]
        [TestCase(20000, true, 1120, true)]
        [TestCase(21000, false, 1104, true)]
        [TestCase(21500, true, 1096, false)]
        public void OriginalSandboxStockCanSupplyAllWindowsThroughSafeRecipes(
            int reloadMilliseconds, bool partitioned, long peakEnergy, bool succeeds)
        {
            var world = new WorldSession(SandboxGameplaySetup.Configuration(), new TestAccess());
            world.RegisterConnection(Fixture.Id(2), Fixture.Id(1));
            SandboxGameplaySetup.Register(world);
            var port = new LocalCommandPort(world, Fixture.Id(2));
            world.Start();
            Assert.That(world.Production.Summary.IssuedUnits, Is.EqualTo(120));
            Assert.That(world.Reactor.PowerSummary!.Initial, Is.EqualTo(10));
            Assert.That(world.Production.GetBatch(SandboxGameplaySetup.ContainerId(7))!.Moisture, Is.EqualTo(850));
            long host = 0;

            void Advance(long target, Guid held = default)
            {
                while (host < target)
                {
                    // Held travel renews real leases; samples otherwise vary without changing owner work.
                    host = held != Guid.Empty || partitioned ? Math.Min(target, host + 1000) : target;
                    world.AdvanceTo(host);
                    if (held != Guid.Empty && world.View.Phase == WorldPhase.Running) Applied(port.Renew(held));
                }
            }
            void Travel(Guid held, long milliseconds) => Advance(host + milliseconds, held);
            void Produce(Guid container)
            {
                Applied(port.Grab(container));
                Applied(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Insert, container));
                Applied(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Start));
                Advance(host + 6000);
                Applied(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Eject));
                Applied(port.Grab(container)); Travel(container, 10000);
                Applied(port.OperateMachine(SandboxGameplaySetup.ProcessorId, ProductionAction.Insert, container));
                Applied(port.OperateMachine(SandboxGameplaySetup.ProcessorId, ProductionAction.Start));
                Advance(host + 9000);
                Assert.That(world.Production.GetBatch(container)!.Kind, Is.EqualTo(MaterialKind.Fuel));
                Assert.That(world.Production.GetBatch(container)!.Flags, Is.EqualTo(MaterialFlags.None));
                Applied(port.OperateMachine(SandboxGameplaySetup.ProcessorId, ProductionAction.Eject));
                Applied(port.Grab(container)); Travel(container, 10000); Applied(port.Release(container));
            }
            void LoadFuel(Guid container)
            {
                Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Insert, container));
                Assert.That(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.SetCooling, cooling: true).Accepted, Is.True);
                Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Start));
            }
            void FinishFuel(long duration)
            {
                Advance(host + duration);
                Assert.That(world.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Exhausted));
                Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Eject));
            }

            // Stage one heavy dry crate and three ordinary dry crates without inspection bypass.
            for (int i = 0; i < 4; i++) Produce(SandboxGameplaySetup.ContainerId(i));
            Assert.That(host, Is.EqualTo(140000));
            Assert.That(world.Production.GetBatch(SandboxGameplaySetup.ContainerId(0))!.Units, Is.EqualTo(34));
            Assert.That(world.Production.Summary.WasteUnits, Is.EqualTo(5));
            Advance(260000); // Window energy cannot be prepaid during preparation.
            Applied(port.Grab(SandboxGameplaySetup.ContainerId(0))); LoadFuel(SandboxGameplaySetup.ContainerId(0));
            FinishFuel(170000);
            Applied(port.Grab(SandboxGameplaySetup.ContainerId(6))); Travel(SandboxGameplaySetup.ContainerId(6), reloadMilliseconds);
            LoadFuel(SandboxGameplaySetup.ContainerId(6)); FinishFuel(60000);
            Applied(port.Grab(SandboxGameplaySetup.ContainerId(1))); Travel(SandboxGameplaySetup.ContainerId(1), reloadMilliseconds);
            Advance(540000, SandboxGameplaySetup.ContainerId(1)); LoadFuel(SandboxGameplaySetup.ContainerId(1));
            FinishFuel(55000);
            Applied(port.Grab(SandboxGameplaySetup.ContainerId(2))); Travel(SandboxGameplaySetup.ContainerId(2), reloadMilliseconds);
            LoadFuel(SandboxGameplaySetup.ContainerId(2)); FinishFuel(55000);
            Applied(port.Grab(SandboxGameplaySetup.ContainerId(3))); Travel(SandboxGameplaySetup.ContainerId(3), reloadMilliseconds);
            LoadFuel(SandboxGameplaySetup.ContainerId(3)); Advance(SandboxGameplaySetup.ShiftDurationMilliseconds);

            Assert.That(world.View.Outcome, Is.EqualTo(succeeds ? WorldOutcome.Succeeded : WorldOutcome.Failed));
            var debrief = world.Debrief!;
            Assert.That(debrief.Contract!.Waves.Select(w => w.DeliveredEnergyUnits), Is.EqualTo(new long[] { 0, 800, 1040, peakEnergy }));
            Assert.That(debrief.Contract.AllPeriodsMet, Is.EqualTo(succeeds));
            Assert.That(debrief.Contract.Waves[3].ShortfallEnergyUnits, Is.EqualTo(succeeds ? 0 : 4));
            Assert.That(debrief.Incidents.BypassedConversions, Is.Zero);
            Assert.That(debrief.Incidents.MachineJams, Is.Zero);
            Assert.That(debrief.Incidents.ReactorTrips, Is.Zero);
            Assert.That(debrief.Production.ActiveUnits + debrief.Production.WasteUnits, Is.EqualTo(120));
            var power = debrief.Power!;
            Assert.That(power.Spent, Is.EqualTo(15));
            Assert.That(power.Initial + power.Generated, Is.EqualTo(power.Available + power.Spent + power.Delivered + power.Spilled));
            Assert.That(world.View.ActiveClaimCount, Is.Zero);
            Assert.That(world.View.RegisteredObjectCount, Is.Zero);
            Assert.That(world.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(world.View.PendingTimerCount, Is.Zero);
            Assert.That(world.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(world.Production.BatchCount, Is.Zero);
            Assert.That(world.Production.MachineCount, Is.Zero);
            Assert.That(world.Reactor.View, Is.Null);
            Assert.That(debrief.Contract.Complete, Is.True);
        }

        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True,
            () => reply.Status + " / " + reply.Production?.Status + " / " + reply.Reactor?.Status);
    }
}
