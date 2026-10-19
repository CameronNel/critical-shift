using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Features.Materials.Domain;
using CriticalShift.Presentation;
using CriticalShift.Sandbox;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class OreWashingTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal Guid Washer => Id(40);
            internal Guid Box => Id(30);
            internal MaterialView Batch => World.Production.GetBatch(Box)!;
            internal Setup(int contamination = 800, int moisture = 100, long reserve = 10, int cycles = 1024,
                long shift = 20000, bool start = true, MaterialKind kind = MaterialKind.Ore)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), new TestAccess(), maxProductionCycles: cycles);
                World.RegisterConnection(Id(20), Id(10));
                World.Production.RegisterBatch(Box, Id(60), Id(70), Id(80), MaterialKind.Ore, 100, moisture, contamination);
                World.Production.RegisterMachine(Washer, MachineRecipe.Washing(Id(50), kind, 1000, 1000, 100, reserveCost: 1));
                World.Reactor.Register(Id(90), new ReactorDefinition(Id(91), initialReserve: reserve));
                Port = new LocalCommandPort(World, Id(20)); if (start) World.Start();
            }
            internal InteractionReply Act(ProductionAction action, bool bypass = false, bool powered = false) =>
                Port.OperateMachine(Washer, action, action == ProductionAction.Insert ? Box : Guid.Empty, bypass, powered);
            internal void Load() { Applied(Port.Grab(Box)); Applied(Act(ProductionAction.Insert)); }
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True,
            () => reply.Status + " / " + reply.Production?.Status + " / " + reply.Reactor?.Status);

        [TestCase(0)] [TestCase(850)] [TestCase(1000)]
        public void WashingInstallsOneWetCleanerChildOnlyAtCompletionWithoutQuantityLoss(int originalMoisture)
        {
            var f = new Setup(moisture: originalMoisture); var original = f.Batch; f.Load();
            var machine = f.World.Production.GetMachine(f.Washer)!;
            Assert.That(machine.IsDrying, Is.False); Assert.That(machine.Recipe.IsWashing, Is.True);
            Assert.That(machine.WashingTargetContamination, Is.EqualTo(100)); Assert.That(machine.Recipe.SupportsInspectionBypass, Is.False);
            var first = f.Act(ProductionAction.Start); Applied(first); var cycle = first.Production!.Machine!.CycleId;
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1)); Assert.That(f.World.Production.Summary.ReserveSpent, Is.EqualTo(1));
            f.World.AdvanceTo(999); Assert.That(f.Batch.BatchId, Is.EqualTo(original.BatchId)); Assert.That(f.Batch.Contamination, Is.EqualTo(800));
            var change = f.World.AdvanceTo(1000).ProductionChanges.Single(); var output = change.Output!;
            Assert.That(output.Kind, Is.EqualTo(MaterialKind.Ore)); Assert.That(output.Units, Is.EqualTo(100));
            Assert.That(output.Contamination, Is.EqualTo(100)); Assert.That(output.Moisture, Is.EqualTo(1000));
            Assert.That(output.ParentBatchId, Is.EqualTo(original.BatchId)); Assert.That(output.BatchId, Is.Not.EqualTo(original.BatchId));
            Assert.That(output.ContainerId, Is.EqualTo(original.ContainerId)); Assert.That(output.OriginId, Is.EqualTo(original.OriginId));
            Assert.That(output.CauseId, Is.EqualTo(original.CauseId)); Assert.That(output.Revision, Is.EqualTo(original.Revision + 1));
            Assert.That(output.Flags, Is.EqualTo(MaterialFlags.None)); Assert.That(change.BypassedInspection, Is.False); Assert.That(change.WasteUnits, Is.Zero);
            Assert.That(f.World.Production.GetConversion(cycle)!.Output!.BatchId, Is.EqualTo(output.BatchId));
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100)); Assert.That(f.World.Production.Summary.IssuedUnits, Is.EqualTo(100));
            var retry = f.Port.ReplayLast(); Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(f.Batch.BatchId, Is.EqualTo(output.BatchId)); Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(1));
            f.World.AdvanceTo(5000); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [TestCase(0)] [TestCase(100)]
        public void AlreadyCleanOreRejectsBeforeAnExhaustedHistoryBudgetOrAnotherDebit(int contamination)
        {
            var f = new Setup(cycles: 1, start: false);
            f.World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Ore, 12, 100, contamination); f.World.Start();
            f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1000); Applied(f.Act(ProductionAction.Eject));
            Applied(f.Port.Grab(Id(31))); Applied(f.Port.OperateMachine(f.Washer, ProductionAction.Insert, Id(31)));
            long revision = f.World.Production.GetMachine(f.Washer)!.Revision;
            var denied = f.Act(ProductionAction.Start); Assert.That(denied.Production!.Status, Is.EqualTo(ProductionStatus.AlreadyConditioned));
            Assert.That(f.World.Production.GetMachine(f.Washer)!.Revision, Is.EqualTo(revision)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1)); Assert.That(f.World.Production.GetBatch(Id(31))!.BatchId, Is.EqualTo(Id(61)));
            Assert.That(SandboxMachineReadout.Result(denied.Production), Does.Contain("already clean enough").And.Not.Contain("dry enough"));
        }

        [Test] public void WasherBypassAndInsufficientReserveCannotReserveOutputOrRepeatTheirRejections()
        {
            var f = new Setup(reserve: 0); f.Load(); var input = f.Batch;
            var bypass = f.Act(ProductionAction.Start, bypass: true); Assert.That(bypass.Production!.Status, Is.EqualTo(ProductionStatus.BypassUnavailable));
            Assert.That(f.Port.ReplayLast().Production!.Status, Is.EqualTo(ProductionStatus.BypassUnavailable));
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero); Assert.That(f.World.Production.Summary.ReserveSpent, Is.Zero);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.Batch.BatchId, Is.EqualTo(input.BatchId));
            Assert.That(f.World.Production.GetMachine(f.Washer)!.Mode, Is.EqualTo(ProductionMode.Idle));
        }

        [Test] public void DirtyOreCannotReserveOrSpendBeyondTheExistingHistoryLimit()
        {
            var f = new Setup(cycles: 1, start: false);
            f.World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Ore, 12, 400, 800); f.World.Start();
            f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1000); Applied(f.Act(ProductionAction.Eject));
            Applied(f.Port.Grab(Id(31))); Applied(f.Port.OperateMachine(f.Washer, ProductionAction.Insert, Id(31)));
            var input = f.World.Production.GetBatch(Id(31))!; var claim = f.World.GetObject(Id(31))!; long revision = f.World.Production.GetMachine(f.Washer)!.Revision;
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.HistoryCapacityReached));
            Assert.That(f.World.Production.GetBatch(Id(31))!.BatchId, Is.EqualTo(input.BatchId));
            Assert.That(f.World.Production.GetBatch(Id(31))!.Contamination, Is.EqualTo(800)); Assert.That(f.World.Production.GetBatch(Id(31))!.Moisture, Is.EqualTo(400));
            Assert.That(f.World.GetObject(Id(31))!.Revision, Is.EqualTo(claim.Revision)); Assert.That(f.World.GetObject(Id(31))!.SlotId, Is.EqualTo(f.Washer));
            Assert.That(f.World.Production.GetMachine(f.Washer)!.Revision, Is.EqualTo(revision)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1)); Assert.That(f.World.Production.Summary.ReserveSpent, Is.EqualTo(1));
        }

        [TestCase(false)] [TestCase(true)]
        public void PausedWashingKeepsDirtyInputAndCurrentWorkWithoutChargingAgain(bool worldPause)
        {
            var f = new Setup(); f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(400);
            if (worldPause) f.World.Pause(f.World.Epoch); else Applied(f.Act(ProductionAction.SetPower));
            f.World.AdvanceTo(5000); Assert.That(f.Batch.Contamination, Is.EqualTo(800));
            Assert.That(f.World.Production.GetMachine(f.Washer)!.WorkMilliseconds, Is.EqualTo(400));
            if (worldPause) f.World.Resume(f.World.Epoch);
            else { Applied(f.Act(ProductionAction.SetPower, powered: true)); Applied(f.Act(ProductionAction.Resume)); }
            f.World.AdvanceTo(5599); Assert.That(f.Batch.Contamination, Is.EqualTo(800)); f.World.AdvanceTo(5600);
            Assert.That(f.Batch.Contamination, Is.EqualTo(100)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1));
        }

        [Test] public void CancellingWashingRetainsExactDirtyInputAndCommittedCost()
        {
            var f = new Setup(); var original = f.Batch; f.Load(); Applied(f.Act(ProductionAction.Start));
            var cycle = f.World.Production.GetMachine(f.Washer)!.CycleId; f.World.AdvanceTo(400);
            Assert.That(f.Act(ProductionAction.CancelCycle).Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            Applied(f.Act(ProductionAction.SetPower)); Applied(f.Act(ProductionAction.CancelCycle)); f.World.AdvanceTo(10000);
            Assert.That(f.Batch.BatchId, Is.EqualTo(original.BatchId)); Assert.That(f.Batch.Contamination, Is.EqualTo(800));
            Assert.That(f.Batch.Moisture, Is.EqualTo(100)); Assert.That(f.World.Production.GetConversion(cycle)!.Cancelled, Is.True);
            Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1));
        }

        [TestCase(999, false)] [TestCase(1000, true)] [TestCase(1001, true)]
        public void WashingDeadlinePublishesOnlyCompletionAtOrBeforeTheCutoff(long shift, bool completes)
        {
            var f = new Setup(shift: shift); f.Load(); Applied(f.Act(ProductionAction.Start)); var changes = f.World.AdvanceTo(10000).ProductionChanges;
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(completes ? 1 : 0));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(completes ? 0 : 1)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100)); Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(1));
            var done = changes.SingleOrDefault(c => c.Kind == ProductionEvent.Completed);
            Assert.That(done != null, Is.EqualTo(completes)); if (done != null) { Assert.That(done.Output!.Contamination, Is.EqualTo(100)); Assert.That(done.Output.Moisture, Is.EqualTo(1000)); }
        }

        [TestCase(false)] [TestCase(true)]
        public void CanonicalDirtySpareOreCanWashDryProduceAndDeliverSafeGridEnergy(bool partitioned)
        {
            var world = new WorldSession(SandboxGameplaySetup.Configuration(), new TestAccess()); world.RegisterConnection(Id(2), Id(1));
            SandboxGameplaySetup.Register(world); var port = new LocalCommandPort(world, Id(2)); world.Start();
            Guid crate = SandboxGameplaySetup.ContainerId(5); var original = world.Production.GetBatch(crate)!; long host = 0;
            void Advance(long duration) { long target = host + duration; while (host < target) { host = partitioned ? Math.Min(target, host + 137) : target; world.AdvanceTo(host); } }
            void Process(Guid machine, long duration)
            {
                Applied(port.Grab(crate)); Applied(port.OperateMachine(machine, ProductionAction.Insert, crate));
                Applied(port.OperateMachine(machine, ProductionAction.Start)); Advance(duration); Applied(port.OperateMachine(machine, ProductionAction.Eject));
            }
            Assert.That(original.Contamination, Is.EqualTo(800)); Process(SandboxGameplaySetup.WasherId, 10000);
            var washed = world.Production.GetBatch(crate)!; Assert.That(washed.Contamination, Is.EqualTo(100)); Assert.That(washed.Moisture, Is.EqualTo(1000));
            Applied(port.Grab(crate)); Applied(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Insert, crate));
            Assert.That(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.WetInput));
            Applied(port.OperateMachine(SandboxGameplaySetup.CrusherId, ProductionAction.Eject));
            Process(SandboxGameplaySetup.DryerId, 8000); Process(SandboxGameplaySetup.CrusherId, 6000); Process(SandboxGameplaySetup.ProcessorId, 9000);
            var fuel = world.Production.GetBatch(crate)!; Assert.That(fuel.Kind, Is.EqualTo(MaterialKind.Fuel)); Assert.That(fuel.Units, Is.EqualTo(11));
            Assert.That(fuel.Contamination, Is.EqualTo(100)); Assert.That(fuel.Flags, Is.EqualTo(MaterialFlags.None));
            Assert.That(fuel.OriginId, Is.EqualTo(original.OriginId)); Assert.That(fuel.CauseId, Is.EqualTo(original.CauseId));
            Applied(port.Grab(crate)); Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Insert, crate));
            Assert.That(world.Reactor.View!.SuspectFuel, Is.False); Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.SetCooling, cooling: true));
            Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Start)); Advance(55000);
            Assert.That(world.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Exhausted)); Assert.That(world.Reactor.PowerSummary!.Delivered, Is.EqualTo(440));
            Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(8)); Assert.That(world.Production.Summary.ReserveSpent, Is.EqualTo(5));
            var spent = world.Production.GetBatch(crate)!; Assert.That(spent.Kind, Is.EqualTo(MaterialKind.SpentFuel)); Assert.That(spent.Contamination, Is.EqualTo(100));
            Assert.That(world.Production.Summary.ActiveUnits + world.Production.Summary.WasteUnits, Is.EqualTo(120)); Assert.That(world.Production.Summary.WasteUnits, Is.EqualTo(1));
            Assert.That(world.Reactor.EmergencyPowerSummary!.UsedCharges, Is.Zero); world.Stop(); Assert.That(world.Debrief!.Incidents.BypassedConversions, Is.Zero);
        }

        [Test] public void WashingAndDryingCannotLaunderInheritedBypassBeforeReactorAdmission()
        {
            var f = new Setup(start: false, kind: MaterialKind.Fuel);
            f.World.Production.RegisterMachine(Id(41), new MachineRecipe(Id(51), MaterialKind.Ore, MaterialKind.Fuel, 1000, 500, 200, 1000));
            f.World.Production.RegisterMachine(Id(42), MachineRecipe.Drying(Id(52), MaterialKind.Fuel, 1000, 1000)); f.World.Start();
            Applied(f.Port.Grab(f.Box)); Applied(f.Port.OperateMachine(Id(41), ProductionAction.Insert, f.Box));
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Start, bypass: true)); f.World.AdvanceTo(500); var suspect = f.Batch;
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Eject)); f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1500);
            var washed = f.Batch; Assert.That(washed.ParentBatchId, Is.EqualTo(suspect.BatchId)); Assert.That(washed.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Assert.That(f.World.Production.GetMachine(f.Washer)!.BypassedInspection, Is.False); Applied(f.Act(ProductionAction.Eject));
            Applied(f.Port.Grab(f.Box)); Applied(f.Port.OperateMachine(Id(42), ProductionAction.Insert, f.Box)); Applied(f.Port.OperateMachine(Id(42), ProductionAction.Start));
            f.World.AdvanceTo(2500); Assert.That(f.Batch.ParentBatchId, Is.EqualTo(washed.BatchId)); Assert.That(f.Batch.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Applied(f.Port.OperateMachine(Id(42), ProductionAction.Eject)); Applied(f.Port.Grab(f.Box)); Applied(f.Port.OperateReactor(Id(90), ReactorAction.Insert, f.Box));
            Assert.That(f.World.Reactor.View!.SuspectFuel, Is.True); Assert.That(f.World.Reactor.View.Fuel!.Contamination, Is.EqualTo(100));
        }

        [Test] public void WasherReadoutUsesCurrentRecipeAndKeepsTheWetOutputConsequenceVisible()
        {
            var f = new Setup(); f.Load(); var machine = f.World.Production.GetMachine(f.Washer)!;
            Assert.That(SandboxMachineReadout.Recipe(machine), Does.Contain("Safe washing").And.Contain("100/1000").And.Contain("Output stays wet").And.Contain("startup 1 reserve"));
            Assert.That(SandboxMachineReadout.Controls(machine), Does.Contain("R start safe washing").And.Not.Contain("B bypass"));
        }

        [TestCase(1, 100, 100, 0)] [TestCase(1000, 0, 100, 0)] [TestCase(1000, 100, -1, 0)]
        [TestCase(1000, 100, 1000, 0)] [TestCase(1000, 100, 100, -1)]
        public void InvalidWashingDefinitionsCannotCreateMeaninglessOrUnboundedWork(long duration, int capacity, int target, long cost) =>
            Assert.Throws<ArgumentOutOfRangeException>(() => MachineRecipe.Washing(Id(50), MaterialKind.Ore, duration, capacity, target, cost));

        [TestCase(800, 1000, 1000, false)] [TestCase(900, 1000, 1000, false)] [TestCase(-1, 1000, 1000, false)]
        [TestCase(100, 900, 1000, false)] [TestCase(100, 1000, 100, false)] [TestCase(100, 1000, 1000, true)]
        public void MaterialWashingPreparationRejectsRaisingContaminationLossDryOutputOrNewBypass(int target, int yield, int moisture, bool bypass)
        {
            var ledger = new MaterialLedger(1, 1); var input = new BatchSnapshot(Id(30), Id(60), Id(70), Id(80), BatchKind.Ore, 12, 100, 800);
            ledger.Register(input);
            Assert.Throws<ArgumentException>(() => ledger.Prepare(Id(30), 0, Id(1), Id(2), Id(3), Id(4), BatchKind.Ore, yield, moisture, bypass, target));
            Assert.That(ledger.PendingCount, Is.Zero); Assert.That(ledger.Get(Id(30)), Is.SameAs(input)); Assert.That(ledger.HasCycleCapacity, Is.True);
        }
    }
}
