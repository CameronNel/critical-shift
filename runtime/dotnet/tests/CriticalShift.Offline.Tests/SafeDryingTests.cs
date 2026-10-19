using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Sandbox;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SafeDryingTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal Guid Dryer => Id(40);
            internal Guid Box => Id(30);
            internal Setup(int moisture = 850, int contamination = 700, int cycles = 1024,
                long shift = 20000, bool start = true, MaterialKind kind = MaterialKind.Ore)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), new TestAccess(), maxProductionCycles: cycles);
                World.RegisterConnection(Id(20), Id(10));
                World.Production.RegisterBatch(Box, Id(60), Id(70), Id(80), MaterialKind.Ore, 100, moisture, contamination);
                World.Production.RegisterMachine(Dryer, MachineRecipe.Drying(Id(50), kind, 1000, 1000, 100));
                Port = new LocalCommandPort(World, Id(20)); if (start) World.Start();
            }
            internal MaterialView Batch => World.Production.GetBatch(Box)!;
            internal InteractionReply Act(ProductionAction action, bool bypass = false, bool powered = false) =>
                Port.OperateMachine(Dryer, action, action == ProductionAction.Insert ? Box : Guid.Empty, bypass, powered);
            internal void Load() { Applied(Port.Grab(Box)); Applied(Act(ProductionAction.Insert)); }
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True,
            () => reply.Status + " / " + reply.Production?.Status + " / " + reply.Reactor?.Status);

        [Test] public void SafeDryingConservesQuantityAndPreservesContaminationCauseAndParentLineage()
        {
            var f = new Setup(); var original = f.Batch; f.Load();
            Assert.That(f.World.Production.GetMachine(f.Dryer)!.IsDrying, Is.True);
            Assert.That(f.World.Production.GetMachine(f.Dryer)!.DryingTargetMoisture, Is.EqualTo(100));
            var start = f.Act(ProductionAction.Start); Applied(start); var cycle = start.Production!.Machine!.CycleId;
            Assert.That(f.World.AdvanceTo(999).ProductionChanges, Is.Empty); Assert.That(f.Batch.BatchId, Is.EqualTo(original.BatchId));
            var complete = f.World.AdvanceTo(1000).ProductionChanges.Single(); var output = complete.Output!;
            Assert.That(output.Kind, Is.EqualTo(MaterialKind.Ore)); Assert.That(output.Units, Is.EqualTo(100)); Assert.That(output.Moisture, Is.EqualTo(100));
            Assert.That(output.Contamination, Is.EqualTo(700)); Assert.That(output.ParentBatchId, Is.EqualTo(original.BatchId));
            Assert.That(output.BatchId, Is.Not.EqualTo(original.BatchId)); Assert.That(output.ContainerId, Is.EqualTo(original.ContainerId));
            Assert.That(output.CauseId, Is.EqualTo(original.CauseId)); Assert.That(output.OriginId, Is.EqualTo(original.OriginId));
            Assert.That(output.Flags, Is.EqualTo(MaterialFlags.None)); Assert.That(output.Revision, Is.EqualTo(original.Revision + 1));
            Assert.That(complete.WasteUnits, Is.Zero); Assert.That(complete.BypassedInspection, Is.False);
            Assert.That(f.World.Production.GetConversion(cycle)!.Output!.BatchId, Is.EqualTo(output.BatchId));
            Assert.That(f.World.Production.Summary.IssuedUnits, Is.EqualTo(100)); Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100));
            Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero); Assert.That(f.World.AdvanceTo(2000).ProductionChanges, Is.Empty);
        }

        [TestCase(0)] [TestCase(100)]
        public void AlreadyDryInputRejectsBeforeAnExhaustedConversionBudget(int moisture)
        {
            var f = new Setup(cycles: 1, start: false);
            f.World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Ore, 10, moisture); f.World.Start();
            f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1000); Applied(f.Act(ProductionAction.Eject));
            Applied(f.Port.Grab(Id(31))); Applied(f.Port.OperateMachine(f.Dryer, ProductionAction.Insert, Id(31)));
            long revision = f.World.Production.GetMachine(f.Dryer)!.Revision;
            var denied = f.Port.OperateMachine(f.Dryer, ProductionAction.Start);
            Assert.That(denied.Production!.Status, Is.EqualTo(ProductionStatus.AlreadyConditioned));
            Assert.That(f.World.Production.GetMachine(f.Dryer)!.Revision, Is.EqualTo(revision));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.GetBatch(Id(31))!.BatchId, Is.EqualTo(Id(61)));
        }

        [Test] public void DryingCannotBypassInspectionAndRejectedRetryCannotStartWorkLater()
        {
            var f = new Setup(); f.Load(); long revision = f.World.Production.GetMachine(f.Dryer)!.Revision;
            var denied = f.Act(ProductionAction.Start, bypass: true);
            Assert.That(denied.Production!.Status, Is.EqualTo(ProductionStatus.BypassUnavailable)); Assert.That(denied.IsTerminal, Is.True);
            Assert.That(f.World.Production.GetMachine(f.Dryer)!.Revision, Is.EqualTo(revision)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            var retry = f.Port.ReplayLast(); Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(retry.Production!.Status, Is.EqualTo(ProductionStatus.BypassUnavailable));
            Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1000); Assert.That(f.Batch.Flags, Is.EqualTo(MaterialFlags.None));
        }

        [Test] public void HistoricalDryingStartCannotCompleteOrRewriteTheResultAgain()
        {
            var f = new Setup(); f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1000);
            var output = f.Batch; var retry = f.Port.ReplayLast(); Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(f.Batch.BatchId, Is.EqualTo(output.BatchId)); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
            Applied(f.Act(ProductionAction.Eject)); f.Load();
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.AlreadyConditioned));
            Assert.That(f.Batch.BatchId, Is.EqualTo(output.BatchId)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
        }

        [TestCase(false)] [TestCase(true)]
        public void DryingPreservesWorkAcrossWorldOrMachinePowerPause(bool worldPause)
        {
            var f = new Setup(); f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(400);
            if (worldPause)
            {
                f.World.Pause(f.World.Epoch); f.World.AdvanceTo(5000); Assert.That(f.Batch.Moisture, Is.EqualTo(850));
                Assert.That(f.Act(ProductionAction.Start).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
                f.World.Resume(f.World.Epoch); f.World.AdvanceTo(5599); Assert.That(f.Batch.Moisture, Is.EqualTo(850)); f.World.AdvanceTo(5600);
            }
            else
            {
                Applied(f.Act(ProductionAction.SetPower)); f.World.AdvanceTo(5000); Assert.That(f.Batch.Moisture, Is.EqualTo(850));
                Assert.That(f.World.Production.GetMachine(f.Dryer)!.WorkMilliseconds, Is.EqualTo(400));
                Applied(f.Act(ProductionAction.SetPower, powered: true)); Applied(f.Act(ProductionAction.Resume));
                f.World.AdvanceTo(5599); Assert.That(f.Batch.Moisture, Is.EqualTo(850)); f.World.AdvanceTo(5600);
            }
            Assert.That(f.Batch.Moisture, Is.EqualTo(100)); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void CancellingDryingKeepsTheExactWetInputAndCannotProduceOutputLater()
        {
            var f = new Setup(); var original = f.Batch; f.Load(); var start = f.Act(ProductionAction.Start); Applied(start);
            f.World.AdvanceTo(400); Assert.That(f.Act(ProductionAction.CancelCycle).Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            Applied(f.Act(ProductionAction.SetPower)); Applied(f.Act(ProductionAction.CancelCycle)); f.World.AdvanceTo(10000);
            Assert.That(f.Batch.BatchId, Is.EqualTo(original.BatchId)); Assert.That(f.Batch.Moisture, Is.EqualTo(850));
            Assert.That(f.Batch.Units, Is.EqualTo(100)); Assert.That(f.Batch.Contamination, Is.EqualTo(700));
            Assert.That(f.World.Production.GetConversion(start.Production!.Machine!.CycleId)!.Cancelled, Is.True);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.Zero); Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
        }

        [TestCase(999, false)] [TestCase(1000, true)] [TestCase(1001, true)]
        public void DryingDeadlineCountsOnlyCompletionAtOrBeforeTheCutoff(long shift, bool completes)
        {
            var f = new Setup(shift: shift); f.Load(); Applied(f.Act(ProductionAction.Start)); var result = f.World.AdvanceTo(10000);
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.World.Production.BatchCount, Is.Zero);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(completes ? 1 : 0));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(completes ? 0 : 1)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100)); Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
            Assert.That(result.ProductionChanges.Count(c => c.Kind == ProductionEvent.Completed), Is.EqualTo(completes ? 1 : 0));
            if (completes) Assert.That(result.ProductionChanges.Single().Output!.Moisture, Is.EqualTo(100));
        }

        [Test] public void DryingCannotLaunderInheritedInspectionBypassBeforeTheReactor()
        {
            var f = new Setup(moisture: 100, contamination: 35, start: false, kind: MaterialKind.Fuel);
            f.World.Production.RegisterMachine(Id(41), new MachineRecipe(Id(51), MaterialKind.Ore, MaterialKind.Fuel, 1000, 500, 200, 1000, outputMoisture: 850));
            f.World.Reactor.Register(Id(90), new ReactorDefinition(Id(91))); f.World.Start();
            Applied(f.Port.Grab(f.Box)); Applied(f.Port.OperateMachine(Id(41), ProductionAction.Insert, f.Box));
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Start, bypass: true)); f.World.AdvanceTo(500);
            var suspect = f.Batch; Assert.That(suspect.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Eject)); f.Load(); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1500);
            Assert.That(f.Batch.Moisture, Is.EqualTo(100)); Assert.That(f.Batch.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Assert.That(f.Batch.ParentBatchId, Is.EqualTo(suspect.BatchId)); Assert.That(f.Batch.CauseId, Is.EqualTo(suspect.CauseId));
            Applied(f.Act(ProductionAction.Eject)); Applied(f.Port.Grab(f.Box)); Applied(f.Port.OperateReactor(Id(90), ReactorAction.Insert, f.Box));
            Assert.That(f.World.Reactor.View!.SuspectFuel, Is.True); Assert.That(f.World.Reactor.View.Fuel!.Contamination, Is.EqualTo(35));
        }

        [TestCase(false)] [TestCase(true)]
        public void CanonicalWetSandboxCrateCanSafelyReachFuelAndGridDelivery(bool partitioned)
        {
            var world = new WorldSession(SandboxGameplaySetup.Configuration(), new TestAccess()); world.RegisterConnection(Id(2), Id(1));
            SandboxGameplaySetup.Register(world); var port = new LocalCommandPort(world, Id(2)); world.Start();
            Guid crate = SandboxGameplaySetup.ContainerId(7); var original = world.Production.GetBatch(crate)!; long now = 0;
            void Advance(long duration)
            {
                long target = now + duration;
                while (now < target) { now = partitioned ? Math.Min(target, now + 137) : target; world.AdvanceTo(now); }
            }
            void Process(Guid machine, long duration)
            {
                Applied(port.Grab(crate)); Applied(port.OperateMachine(machine, ProductionAction.Insert, crate));
                Applied(port.OperateMachine(machine, ProductionAction.Start)); Advance(duration); Applied(port.OperateMachine(machine, ProductionAction.Eject));
            }
            Assert.That(original.Moisture, Is.EqualTo(850));
            Process(SandboxGameplaySetup.DryerId, 8000); Assert.That(world.Production.GetBatch(crate)!.Units, Is.EqualTo(12));
            Assert.That(world.Production.GetBatch(crate)!.Moisture, Is.EqualTo(100)); Process(SandboxGameplaySetup.CrusherId, 6000);
            Process(SandboxGameplaySetup.ProcessorId, 9000); var fuel = world.Production.GetBatch(crate)!;
            Assert.That(fuel.Kind, Is.EqualTo(MaterialKind.Fuel)); Assert.That(fuel.Units, Is.EqualTo(11)); Assert.That(fuel.Flags, Is.EqualTo(MaterialFlags.None));
            Assert.That(fuel.OriginId, Is.EqualTo(original.OriginId)); Assert.That(fuel.CauseId, Is.EqualTo(original.CauseId));
            Applied(port.Grab(crate)); Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Insert, crate));
            Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.SetCooling, cooling: true));
            Applied(port.OperateReactor(SandboxGameplaySetup.ReactorId, ReactorAction.Start)); Advance(55000);
            Assert.That(world.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Exhausted)); Assert.That(world.Reactor.PowerSummary!.Delivered, Is.EqualTo(440));
            Assert.That(world.Production.GetBatch(crate)!.Kind, Is.EqualTo(MaterialKind.SpentFuel)); Assert.That(world.Production.GetBatch(crate)!.Units, Is.EqualTo(11));
            Assert.That(world.Production.Summary.WasteUnits, Is.EqualTo(1)); Assert.That(world.Production.Summary.ActiveUnits + world.Production.Summary.WasteUnits, Is.EqualTo(120));
            Assert.That(world.Reactor.EmergencyPowerSummary!.UsedCharges, Is.Zero);
            Assert.That(world.Trace.Records.Any(r => r.ProductionEvent == ProductionEvent.Jammed || r.ReactorEvent == ReactorEvent.Tripped), Is.False);
            world.Stop(); Assert.That(world.Debrief!.Incidents.BypassedConversions, Is.Zero);
        }

        [Test] public void OrdinaryConversionStillRequiresDifferentKindsAndDryingIsExplicit()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.Ore, 1000, 500, 200, 1000));
            var recipe = MachineRecipe.Drying(Id(50), MaterialKind.Ore, 1000, 1000, 100);
            Assert.That(recipe.Input, Is.EqualTo(recipe.Output)); Assert.That(recipe.YieldPermille, Is.EqualTo(1000));
            Assert.That(recipe.MoistureTolerance, Is.EqualTo(1000)); Assert.That(recipe.IsDrying, Is.True);
        }

        [TestCase(1, 1000, 100)] [TestCase(1000, 0, 100)] [TestCase(1000, 1000, -1)] [TestCase(1000, 1000, 1000)]
        public void InvalidDryingRulesCannotCreateAnUnboundedOrMeaninglessCycle(long duration, int capacity, int target) =>
            Assert.Throws<ArgumentOutOfRangeException>(() => MachineRecipe.Drying(Id(50), MaterialKind.Ore, duration, capacity, target));
    }
}
