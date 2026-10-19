using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ReactorDiscardTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal readonly TestAccess Access = new TestAccess();
            internal ReactorView Core => World.Reactor.View!;
            internal PowerView Power => World.Reactor.PowerSummary!;
            internal Setup(int contamination = 0, int history = 4096, int trace = 128, bool prefix = false)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, 10000, true), Access, traceCapacity: trace, maxProductionCycles: history);
                World.RegisterConnection(Id(20), Id(10));
                World.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), prefix ? MaterialKind.Ore : MaterialKind.Fuel, 10, 123, contamination);
                World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Fuel, 10);
                if (prefix) World.Production.RegisterMachine(Id(40), new MachineRecipe(Id(41), MaterialKind.Ore, MaterialKind.Fuel, 1000, 500, 200, 100,
                    moistureTolerance: 1000, outputMoisture: 123));
                World.Reactor.Register(Id(90), new ReactorDefinition(Id(91)));
                World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(1000, 12, 2));
                Port = new LocalCommandPort(World, Id(20)); World.Start();
                if (prefix)
                {
                    Applied(Port.Grab(Id(30))); Applied(Port.OperateMachine(Id(40), ProductionAction.Insert, Id(30)));
                    Applied(Port.OperateMachine(Id(40), ProductionAction.Start, bypass: true)); World.AdvanceTo(500);
                    Applied(Port.OperateMachine(Id(40), ProductionAction.Eject));
                }
            }
            internal InteractionReply Act(ReactorAction action) => Port.OperateReactor(Id(90), action);
            internal void Load(int container = 30)
            { Applied(Port.Grab(Id(container))); Applied(Port.OperateReactor(Id(90), ReactorAction.Insert, Id(container))); }
            internal void Run(int container = 30)
            { Load(container); Assert.That(Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true).Accepted, Is.True); Applied(Act(ReactorAction.Start)); }
            internal void ShutdownAt(long at) { World.AdvanceTo(at); Applied(Act(ReactorAction.Shutdown)); }
        }
        private static void Applied(InteractionReply r) => Assert.That(r.HasNewCommit, Is.True, r.Status + "/" + r.Reactor?.Status);
        private static void Balanced(PowerView p) => Assert.That(p.Initial + p.Generated, Is.EqualTo(p.Available + p.Spent + p.Delivered + p.Spilled));

        [TestCase(0)] [TestCase(99)] [TestCase(250)]
        public void DiscardForfeitsAllRemainingFuelWithoutNewOutputRefundOrQuantityLoss(long at)
        {
            var f = new Setup(); f.Run(); f.ShutdownAt(at); var power = f.Power; var original = f.World.Production.GetBatch(Id(30))!; var cycle = f.Core.CycleId;
            var result = f.Act(ReactorAction.DiscardFuel); Applied(result); var change = result.Reactor!.Change!;
            Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Empty)); Assert.That(f.Core.CycleId, Is.EqualTo(Guid.Empty)); Assert.That(f.Core.Fuel, Is.Null);
            Assert.That(change.Kind, Is.EqualTo(ReactorEvent.FuelDiscarded)); Assert.That(change.CycleId, Is.EqualTo(cycle)); Assert.That(change.InputBatchId, Is.EqualTo(original.BatchId));
            Assert.That(change.CauseId, Is.EqualTo(Id(80))); Assert.That(change.DiscardedFuelMilliseconds, Is.EqualTo(1000 - at)); Assert.That(change.ShiftMilliseconds, Is.EqualTo(at));
            Assert.That(change.GeneratedUnits, Is.Zero); Assert.That(change.SpentUnits, Is.Zero);
            var spent = f.World.Production.GetBatch(Id(30))!; Assert.That(spent.Kind, Is.EqualTo(MaterialKind.SpentFuel)); Assert.That(spent.Units, Is.EqualTo(10));
            Assert.That(spent.ParentBatchId, Is.EqualTo(original.BatchId)); Assert.That(spent.Revision, Is.EqualTo(original.Revision + 1)); Assert.That(spent.Moisture, Is.EqualTo(123));
            Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.Null); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.Null);
            Assert.That(f.Power.Generated, Is.EqualTo(power.Generated)); Assert.That(f.Power.Spent, Is.EqualTo(power.Spent)); Assert.That(f.Power.Available, Is.EqualTo(power.Available));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(20)); Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
            f.World.AdvanceTo(5000); Assert.That(f.Power.Generated, Is.EqualTo(power.Generated)); Balanced(f.Power);
        }

        [TestCase(ReactorMode.Empty)] [TestCase(ReactorMode.Loaded)] [TestCase(ReactorMode.Running)] [TestCase(ReactorMode.Tripped)] [TestCase(ReactorMode.Exhausted)]
        public void DiscardCannotSkipTheExplicitShutdownState(ReactorMode mode)
        {
            var f = new Setup();
            if (mode == ReactorMode.Loaded) f.Load();
            else if (mode != ReactorMode.Empty) { f.Run(); if (mode == ReactorMode.Tripped) f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: false); if (mode == ReactorMode.Tripped || mode == ReactorMode.Exhausted) f.World.AdvanceTo(mode == ReactorMode.Tripped ? 800 : 1000); }
            Assert.That(f.Core.Mode, Is.EqualTo(mode)); var material = f.World.Production.GetBatch(Id(30))!; var power = f.Power;
            Assert.That(f.Act(ReactorAction.DiscardFuel).Reactor!.Status, Is.EqualTo(ReactorStatus.InvalidState));
            Assert.That(f.Core.Mode, Is.EqualTo(mode)); Assert.That(f.World.Production.GetBatch(Id(30))!.BatchId, Is.EqualTo(material.BatchId));
            Assert.That(f.Power.Generated, Is.EqualTo(power.Generated)); Assert.That(f.Power.Spent, Is.EqualTo(power.Spent));
        }

        [Test] public void DiscardRequiresOpenCoolingAndTheInclusiveResetThreshold()
        {
            var f = new Setup(contamination: 777); f.Run(); f.ShutdownAt(250); f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: false);
            Assert.That(f.Act(ReactorAction.DiscardFuel).Reactor!.Status, Is.EqualTo(ReactorStatus.NoCooling));
            f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true); f.World.AdvanceTo(399);
            Assert.That(f.Core.InstabilityMilliseconds, Is.EqualTo(101)); Assert.That(f.Core.CanDiscardFuel, Is.False);
            Assert.That(f.Act(ReactorAction.DiscardFuel).Reactor!.Status, Is.EqualTo(ReactorStatus.Unsafe));
            f.World.AdvanceTo(400); Assert.That(f.Core.CanDiscardFuel, Is.True); var done = f.Act(ReactorAction.DiscardFuel); Applied(done);
            Assert.That(done.Reactor!.Change!.DiscardedFuelMilliseconds, Is.EqualTo(750)); Assert.That(f.World.Production.GetBatch(Id(30))!.Contamination, Is.EqualTo(777));
        }

        [Test] public void StaleDiscardCustodyRejectsBeforeFuelConversionOrAnyOtherMutation()
        {
            var f = new Setup(); f.Run(); f.ShutdownAt(250); long seq = f.Port.LastTerminalSequence + 1; var before = f.Core; var batch = f.World.Production.GetBatch(Id(30))!;
            var rejected = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, seq, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.DiscardFuel, before.Revision, objectRevision: 1)));
            Assert.That(rejected.Reactor!.Status, Is.EqualTo(ReactorStatus.CustodyRejected)); Assert.That(f.World.Production.GetBatch(Id(30))!.BatchId, Is.EqualTo(batch.BatchId));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.Zero); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
            Assert.That(f.Core.Revision, Is.EqualTo(before.Revision)); Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.EqualTo(Id(90))); Assert.That(f.Power.Generated, Is.EqualTo(before.Power.Generated));
            var fresh = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, seq + 1, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.DiscardFuel, before.Revision, objectRevision: f.World.GetObject(Id(30))!.Revision)));
            Applied(fresh); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void ExistingReservedFuelCanBeDiscardedWithNoRemainingHistoryCapacity()
        {
            var f = new Setup(history: 1); f.Run(); f.ShutdownAt(99); Applied(f.Act(ReactorAction.DiscardFuel));
            f.Load(31); var power = f.Power; Assert.That(f.Act(ReactorAction.Start).Reactor!.Status, Is.EqualTo(ReactorStatus.HistoryCapacityReached));
            Assert.That(f.Power.Available, Is.EqualTo(power.Available)); Assert.That(f.World.Production.GetBatch(Id(31))!.Kind, Is.EqualTo(MaterialKind.Fuel));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void DiscardReplayCannotEmptyFreshFuelOrCarryOldPartialWorkIntoTheNewCycle()
        {
            var f = new Setup(); f.Run(); f.ShutdownAt(199); long revision = f.Core.Revision, claim = f.World.GetObject(Id(30))!.Revision;
            Applied(f.Act(ReactorAction.DiscardFuel)); long sequence = f.Port.LastTerminalSequence; var first = f.World.Production.GetBatch(Id(30))!;
            f.Run(31); f.World.AdvanceTo(200); Assert.That(f.Core.WorkMilliseconds, Is.EqualTo(1)); Assert.That(f.Power.Generated, Is.EqualTo(5));
            var retry = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.DiscardFuel, revision, objectRevision: claim)));
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False); Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Running)); Assert.That(f.Core.WorkMilliseconds, Is.EqualTo(1));
            Assert.That(f.World.Production.GetBatch(Id(31))!.Kind, Is.EqualTo(MaterialKind.Fuel)); Assert.That(f.World.Production.GetBatch(Id(30))!.BatchId, Is.EqualTo(first.BatchId));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.Act(ReactorAction.DiscardFuel).Reactor!.Status, Is.EqualTo(ReactorStatus.InvalidState)); Balanced(f.Power);
        }

        [Test] public void DiscardPreservesOutputRoutingAndRunningBackupWithoutCreditingLostFuel()
        {
            var f = new Setup(); f.Port.OperateReactor(Id(90), ReactorAction.SetOutputRouting, outputRouting: ReactorOutputRouting.GridPriority);
            f.Run(); Applied(f.Act(ReactorAction.StartBackup)); f.ShutdownAt(250); var power = f.Power; var backup = f.Core.EmergencyPower!;
            Applied(f.Act(ReactorAction.DiscardFuel)); Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.GridPriority)); Assert.That(f.Core.EmergencyPower!.CycleId, Is.EqualTo(backup.CycleId));
            f.World.AdvanceTo(1000); Assert.That(f.Power.Delivered, Is.EqualTo(power.Delivered)); Assert.That(f.Power.Generated, Is.EqualTo(power.Generated + 12)); Balanced(f.Power);
        }

        [Test] public void DiscardKeepsInheritedInspectionHistoryAndFullInputOutputLineage()
        {
            var f = new Setup(prefix: true); f.Run(); f.ShutdownAt(600); var fuel = f.World.Production.GetBatch(Id(30))!; var done = f.Act(ReactorAction.DiscardFuel); Applied(done);
            var conversion = done.Reactor!.Change!.DiscardedFuel!;
            Assert.That(conversion.Input.BatchId, Is.EqualTo(fuel.BatchId)); Assert.That(conversion.Input.ParentBatchId, Is.EqualTo(Id(60)));
            Assert.That(conversion.Output!.Flags, Is.EqualTo(MaterialFlags.BypassedInspection)); Assert.That(conversion.Output.ParentBatchId, Is.EqualTo(fuel.BatchId));
            Assert.That(conversion.Output.OriginId, Is.EqualTo(Id(70))); Assert.That(conversion.Output.CauseId, Is.EqualTo(Id(80))); Assert.That(conversion.Output.Units, Is.EqualTo(10));
            Assert.That(conversion.Output.Moisture, Is.EqualTo(123)); Assert.That(conversion.Output.Revision, Is.EqualTo(2)); Assert.That(conversion.Cancelled, Is.False);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(2)); Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
        }

        [TestCase(false)] [TestCase(true)]
        public void OrdinaryUnusedAndExhaustedEjectionKeepTheirExistingMaterialSemantics(bool used)
        {
            var f = new Setup(); if (used) { f.Run(); f.World.AdvanceTo(1000); } else f.Load();
            Applied(f.Act(ReactorAction.Eject)); Assert.That(f.World.Production.GetBatch(Id(30))!.Kind, Is.EqualTo(used ? MaterialKind.SpentFuel : MaterialKind.Fuel));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(used ? 1 : 0));
        }

        [Test] public void PausedDiscardAndOutOfReachDiscardCannotConsumeFuel()
        {
            var f = new Setup(); f.Run(); f.ShutdownAt(100); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(1000);
            Assert.That(f.Act(ReactorAction.DiscardFuel).Status, Is.EqualTo(InteractionStatus.ActorUnavailable)); Assert.That(f.World.Production.GetBatch(Id(30))!.Kind, Is.EqualTo(MaterialKind.Fuel));
            f.World.Resume(f.World.Epoch); f.Access.Decision = AccessDecision.OutOfReach;
            Assert.That(f.Act(ReactorAction.DiscardFuel).Status, Is.EqualTo(InteractionStatus.OutOfReach)); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
            f.Access.Decision = AccessDecision.Allowed; Applied(f.Act(ReactorAction.DiscardFuel)); Assert.That(f.World.Trace.Records.Last().ReactorChange!.ShiftMilliseconds, Is.EqualTo(100));
        }

        [Test] public void FuelCompletionHelperCannotCountItsRetainedReceiptTwice()
        {
            var f = new Setup(); f.Run(); var cycle = f.Core.CycleId; f.ShutdownAt(99); Applied(f.Act(ReactorAction.DiscardFuel));
            var finish = typeof(ProductionOperations).GetMethod("FinishFuel", BindingFlags.Instance | BindingFlags.NonPublic)!;
            finish.Invoke(f.World.Production, new object[] { cycle }); finish.Invoke(f.World.Production, new object[] { cycle });
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.World.Production.GetBatch(Id(30))!.Revision, Is.EqualTo(1));
        }

        [Test] public void DiscardSnapshotsSurviveRawTraceEvictionAndMaterialOwnerTeardown()
        {
            var f = new Setup(trace: 8); f.Run(); f.ShutdownAt(199); var result = f.Act(ReactorAction.DiscardFuel); var change = result.Reactor!.Change!;
            var output = change.DiscardedFuel!.Output!;
            for (int time = 200; time < 220; time++) f.World.AdvanceTo(time);
            Assert.That(f.World.Trace.Records.Any(r => r.ReactorEvent == ReactorEvent.FuelDiscarded), Is.False);
            f.World.Stop(); Assert.That(f.World.Production.GetConversion(change.CycleId), Is.Null);
            var row = f.World.Debrief!.Timeline.Single(r => r.ReactorEvent == ReactorEvent.FuelDiscarded);
            Assert.That(row.BatchId, Is.EqualTo(Id(60))); Assert.That(row.OutputBatchId, Is.EqualTo(output.BatchId)); Assert.That(row.MaterialCauseId, Is.EqualTo(Id(80)));
            Assert.That(row.RecipeId, Is.EqualTo(Id(91))); Assert.That(row.ReactorChange!.DiscardedFuelMilliseconds, Is.EqualTo(801));
            Assert.That(row.ReactorChange.DiscardedFuel!.Input.Kind, Is.EqualTo(MaterialKind.Fuel)); Assert.That(row.ReactorChange.DiscardedFuel.Output!.Kind, Is.EqualTo(MaterialKind.SpentFuel));
            Assert.That(SandboxTraceFeed.DebriefEntries(f.World.Debrief).Single(e => e.Reactor == ReactorEvent.FuelDiscarded).Description, Does.Contain("0.801s"));
            Assert.That(change.State.Mode, Is.EqualTo(ReactorMode.Empty)); Assert.That(output.Units, Is.EqualTo(10));
        }

        [TestCase("container")] [TestCase("lease")] [TestCase("batch")] [TestCase("cooling")] [TestCase("routing")]
        public void DiscardRejectsUnrelatedPayloadWithoutConsumingTheConnectionSequence(string field)
        {
            var f = new Setup(); f.Run(); f.ShutdownAt(99); long seq = f.Port.LastTerminalSequence + 1;
            var result = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, seq, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.DiscardFuel, f.Core.Revision, field == "container" ? Id(30) : Guid.Empty,
                    f.World.GetObject(Id(30))!.Revision, batchRevision: field == "batch" ? 1 : 0,
                    leaseGeneration: field == "lease" ? 1 : 0, cooling: field == "cooling",
                    outputRouting: field == "routing" ? ReactorOutputRouting.GridPriority : ReactorOutputRouting.Balanced)));
            Assert.That(result.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(result.IsTerminal, Is.False);
            Assert.That(f.World.Production.GetBatch(Id(30))!.Kind, Is.EqualTo(MaterialKind.Fuel));
            Applied(f.Act(ReactorAction.DiscardFuel)); Assert.That(f.Port.LastTerminalSequence, Is.EqualTo(seq));
        }

        [Test] public void DiscardGuidanceExplainsCoolingWaitAndIrreversibleLostTime()
        {
            var f = new Setup(contamination: 777); f.Run(); f.ShutdownAt(250);
            Assert.That(SandboxReactorReadout.Controls(f.Core), Does.Contain("discard waits"));
            Assert.That(SandboxReactorReadout.Result(f.Act(ReactorAction.DiscardFuel).Reactor!, ReactorAction.DiscardFuel), Does.Contain("instability at most 0.1s"));
            f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: false);
            Assert.That(SandboxReactorReadout.Controls(f.Core), Does.Contain("restore cooling before N"));
            var closed = f.Act(ReactorAction.DiscardFuel).Reactor!;
            Assert.That(SandboxReactorReadout.Result(closed, ReactorAction.DiscardFuel), Does.Contain("before discarding"));
            Assert.That(SandboxReactorReadout.Result(closed), Does.Contain("retrying this control").And.Not.Contain("starting"));
            f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true); f.World.AdvanceTo(400);
            Assert.That(SandboxReactorReadout.Controls(f.Core), Does.Contain("no refund"));
            var text = SandboxReactorReadout.Result(f.Act(ReactorAction.DiscardFuel).Reactor!, ReactorAction.DiscardFuel);
            Assert.That(text, Does.Contain("0.75s").And.Contain("spent material released").And.Contain("no reserve refund"));
        }
    }
}
