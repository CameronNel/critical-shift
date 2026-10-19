using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Production.Domain;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class TimedJamClearingTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port, Other;
            internal Guid Machine => Id(40);
            internal MachineView State => World.Production.GetMachine(Machine)!;
            internal MaterialView Input => World.Production.GetBatch(Id(30))!;
            internal Setup(long shift = 10000, long repair = 1000, int trace = 128)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), new TestAccess(), traceCapacity: trace);
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11));
                World.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Ore, 10, 900, 35);
                World.Production.RegisterMachine(Machine, new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre,
                    1000, 500, 200, 100, yieldPermille: 800, repairDurationMilliseconds: repair));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21)); World.Start();
            }
            internal InteractionReply Act(ProductionAction action, bool power = false) => Port.OperateMachine(Machine, action, powered: power);
            internal void Jam()
            {
                Assert.That(Port.Grab(Id(30)).HasNewCommit, Is.True); Assert.That(Port.OperateMachine(Machine, ProductionAction.Insert, Id(30)).HasNewCommit, Is.True);
                Assert.That(Port.OperateMachine(Machine, ProductionAction.Start, bypass: true).HasNewCommit, Is.True);
                World.AdvanceTo(World.View.HostMilliseconds + 200); Assert.That(State.Mode, Is.EqualTo(ProductionMode.Jammed));
            }
            internal InteractionReply Begin()
            { Jam(); Act(ProductionAction.SetPower); return Act(ProductionAction.Repair); }
        }

        [Test] public void JamClearingPreservesTheReservedCycleAndNeedsExplicitPowerAndResumeAfterItsExactDue()
        {
            var f = new Setup(); var input = f.Input; var started = f.Begin(); var cycle = f.State.CycleId;
            Assert.That(started.Production!.Change!.Kind, Is.EqualTo(ProductionEvent.RepairStarted));
            Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.Repairing)); Assert.That(f.State.Powered, Is.False);
            Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200)); Assert.That(f.State.RepairRemainingMilliseconds, Is.EqualTo(1000));
            f.World.AdvanceTo(1199); Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(999)); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
            var completed = f.World.AdvanceTo(1200).ProductionChanges.Single();
            Assert.That(completed.Kind, Is.EqualTo(ProductionEvent.RepairCompleted)); Assert.That(completed.ShiftMilliseconds, Is.EqualTo(1200));
            Assert.That(completed.CycleId, Is.EqualTo(cycle)); Assert.That(completed.Input.BatchId, Is.EqualTo(input.BatchId)); Assert.That(completed.Output, Is.Null);
            Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.PowerPaused)); Assert.That(f.State.Powered, Is.False); Assert.That(f.State.RepairRemainingMilliseconds, Is.Zero);
            Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200)); Assert.That(f.Input.BatchId, Is.EqualTo(input.BatchId));
            Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.EqualTo(f.Machine)); Assert.That(f.World.Production.Summary.CompletedCycles, Is.Zero);
            Assert.That(f.World.Production.GetConversion(cycle), Is.Null); f.World.AdvanceTo(5000);
            Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200)); Assert.That(f.Act(ProductionAction.Resume).Production!.Status, Is.EqualTo(ProductionStatus.NoPower));
            f.Act(ProductionAction.SetPower, true); f.Act(ProductionAction.Resume); f.World.AdvanceTo(5299); Assert.That(f.World.Production.Summary.CompletedCycles, Is.Zero);
            f.World.AdvanceTo(5300); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.Input.Units, Is.EqualTo(8)); Assert.That(f.Input.ParentBatchId, Is.EqualTo(input.BatchId)); Assert.That(f.Input.CauseId, Is.EqualTo(input.CauseId));
            Assert.That(f.Input.OriginId, Is.EqualTo(input.OriginId)); Assert.That(f.Input.Contamination, Is.EqualTo(35));
            Assert.That(f.Input.Flags, Is.EqualTo(MaterialFlags.BypassedInspection)); Assert.That(f.World.Production.Summary.WasteUnits, Is.EqualTo(2));
        }

        [TestCase(ProductionAction.SetPower)] [TestCase(ProductionAction.Resume)] [TestCase(ProductionAction.Eject)] [TestCase(ProductionAction.Start)]
        public void InProgressClearingRejectsEarlyPowerResumeEjectionAndNewProcessing(ProductionAction action)
        {
            var f = new Setup(); f.Begin(); f.World.AdvanceTo(700); long revision = f.State.Revision; var cycle = f.State.CycleId;
            var result = f.Act(action, action == ProductionAction.SetPower);
            Assert.That(result.HasNewCommit, Is.False); Assert.That(result.Production!.Status,
                Is.EqualTo(action == ProductionAction.Eject ? ProductionStatus.InvalidState : ProductionStatus.RepairInProgress));
            Assert.That(f.State.Revision, Is.EqualTo(revision)); Assert.That(f.State.CycleId, Is.EqualTo(cycle));
            Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(500)); Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200));
            Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.EqualTo(f.Machine)); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
        }

        [Test] public void FreshRepeatedRepairAndHistoricalStartRetryCannotResetOrRepeatClearing()
        {
            var f = new Setup(); f.Jam(); f.Act(ProductionAction.SetPower); long before = f.State.Revision;
            var first = f.Act(ProductionAction.Repair); long sequence = f.Port.LastTerminalSequence; f.World.AdvanceTo(700);
            Assert.That(f.Other.OperateMachine(f.Machine, ProductionAction.Repair).Status, Is.EqualTo(InteractionStatus.NoChange));
            Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(500)); f.World.AdvanceTo(1200); long revision = f.World.View.Revision;
            var retry = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Repair, before)));
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False); Assert.That(f.World.View.Revision, Is.EqualTo(revision));
            Assert.That(retry.Production!.Machine!.Mode, Is.EqualTo(ProductionMode.Repairing)); Assert.That(retry.Production.Machine.RepairWorkMilliseconds, Is.Zero);
            Assert.That(retry.Production.Change!.CycleId, Is.EqualTo(first.Production!.Change!.CycleId));
            Assert.That(f.World.Trace.Records.Count(r => r.Changed && r.ProductionEvent == ProductionEvent.RepairStarted), Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Count(r => r.Changed && r.ProductionEvent == ProductionEvent.RepairCompleted), Is.EqualTo(1));
        }

        [Test] public void StaleMachineRevisionCannotRestartTheRepairOrAdvanceItsProgress()
        {
            var f = new Setup(); f.Begin(); long previous = f.State.Revision; f.World.AdvanceTo(700);
            var stale = f.World.ExecuteInteraction(Id(21), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Repair, previous)));
            Assert.That(stale.Production!.Status, Is.EqualTo(ProductionStatus.RevisionConflict)); Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(500));
            f.World.AdvanceTo(1200); Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.PowerPaused));
        }

        [Test] public void CancellingDuringClearingKeepsTheExactInputAndDiscardsAllRepairProgress()
        {
            var f = new Setup(); var original = f.Input; f.Begin(); var cycle = f.State.CycleId; f.World.AdvanceTo(700);
            Assert.That(f.Act(ProductionAction.CancelCycle).HasNewCommit, Is.True); Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.Idle));
            Assert.That(f.State.RepairDurationMilliseconds, Is.Zero); Assert.That(f.State.RepairWorkMilliseconds, Is.Zero); Assert.That(f.State.CycleId, Is.EqualTo(Guid.Empty));
            Assert.That(f.Input.BatchId, Is.EqualTo(original.BatchId)); Assert.That(f.Input.Units, Is.EqualTo(10)); Assert.That(f.Input.Moisture, Is.EqualTo(900));
            Assert.That(f.Input.Contamination, Is.EqualTo(35)); Assert.That(f.Input.CauseId, Is.EqualTo(original.CauseId)); Assert.That(f.Input.Flags, Is.EqualTo(original.Flags));
            Assert.That(f.World.Production.GetConversion(cycle)!.Cancelled, Is.True); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            f.World.AdvanceTo(5000); Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1)); Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
            Assert.That(f.World.Trace.Records.Any(r => r.ProductionEvent == ProductionEvent.RepairCompleted), Is.False);
        }

        [Test] public void PauseFreezesClearingAndAResumedClockSettlesItsExactOccurrence()
        {
            var f = new Setup(); f.Begin(); f.World.AdvanceTo(700); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(70000);
            Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(500)); Assert.That(f.World.View.ElapsedMilliseconds, Is.EqualTo(700));
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(70499); Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.Repairing));
            var result = f.World.AdvanceTo(70500); Assert.That(result.ProductionChanges.Single().ShiftMilliseconds, Is.EqualTo(1200));
            Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.PowerPaused)); Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200));
        }

        [Test] public void SkippedAndPartitionedClockStepsKeepRepairAttributionAndFrozenProcessingEquivalent()
        {
            var leap = new Setup(); var small = new Setup(); leap.Begin(); small.Begin(); leap.World.AdvanceTo(5000);
            foreach (long time in new[] { 400L, 700, 1199, 1200, 1800, 5000 }) small.World.AdvanceTo(time);
            foreach (var f in new[] { leap, small })
            {
                Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.PowerPaused)); Assert.That(f.State.RepairWorkMilliseconds, Is.EqualTo(1000));
                Assert.That(f.State.WorkMilliseconds, Is.EqualTo(200)); Assert.That(f.Input.Kind, Is.EqualTo(MaterialKind.Ore));
                Assert.That(f.World.Trace.Records.Single(r => r.ProductionEvent == ProductionEvent.RepairCompleted).OccurredAtMilliseconds, Is.EqualTo(1200));
                Assert.That(f.World.Production.Summary.CompletedCycles, Is.Zero); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
            }
        }

        [TestCase(1199, false)] [TestCase(1200, true)] [TestCase(1201, true)]
        public void RepairDeadlineSettlesOnlyDueClearingBeforeCancellingTheUnfinishedConversion(long deadline, bool repairDone)
        {
            var f = new Setup(shift: deadline); f.Begin(); var result = f.World.AdvanceTo(100000);
            Assert.That(result.World.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.World.Production.MachineCount, Is.Zero);
            Assert.That(result.ProductionChanges.Count(c => c.Kind == ProductionEvent.RepairCompleted), Is.EqualTo(repairDone ? 1 : 0));
            if (repairDone) Assert.That(result.ProductionChanges.Single().ShiftMilliseconds, Is.EqualTo(1200));
            Assert.That(f.World.Debrief!.Production.CompletedCycles, Is.Zero); Assert.That(f.World.Debrief.Production.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.World.Debrief.Production.ActiveUnits, Is.EqualTo(10)); Assert.That(f.World.Debrief.Production.WasteUnits, Is.Zero);
            var frozen = f.World.Debrief; f.World.Stop(); f.World.AdvanceTo(200000); Assert.That(f.World.Debrief, Is.SameAs(frozen));
        }

        [Test] public void OperatorImpactAndDisconnectLeaveStartedMachineClearingAutonomous()
        {
            var f = new Setup(); f.Begin(); f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, WorkerImpact.Incapacitating, 0, Id(90), Id(91));
            f.World.Disconnect(f.World.Epoch, Id(20)); f.World.AdvanceTo(1200);
            Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.PowerPaused)); Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
            Assert.That(f.Other.OperateMachine(f.Machine, ProductionAction.SetPower, powered: true).HasNewCommit, Is.True);
            Assert.That(f.Other.OperateMachine(f.Machine, ProductionAction.Resume).HasNewCommit, Is.True); f.World.AdvanceTo(1500);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void RepairFactsAndReadoutSurviveTraceEvictionWithOriginalMaterialAttribution()
        {
            var f = new Setup(trace: 8); var feed = new SandboxTraceFeed(f.Port); var started = f.Begin(); feed.Refresh();
            Assert.That(SandboxMachineReadout.Result(started.Production!, ProductionAction.Repair), Does.Contain("clearing started"));
            Assert.That(SandboxMachineReadout.Controls(f.State), Does.Contain("1s left").And.Contain("keep power isolated"));
            f.World.AdvanceTo(1200); feed.Refresh(); var cycle = f.State.CycleId;
            Assert.That(feed.Entries.Count(e => e.Description.Contains("Jam cleared")), Is.EqualTo(1));
            for (int time = 1201; time <= 1220; time++) f.World.AdvanceTo(time);
            Assert.That(f.World.Trace.Records.Any(r => r.ProductionEvent == ProductionEvent.RepairCompleted), Is.False); f.World.Stop();
            var events = f.World.Debrief!.Timeline.Where(r => r.ProductionEvent == ProductionEvent.RepairStarted || r.ProductionEvent == ProductionEvent.RepairCompleted).ToArray();
            Assert.That(events.Length, Is.EqualTo(2)); Assert.That(events.All(r => r.CycleId == cycle && r.MaterialCauseId == Id(80) && r.BatchId == Id(60) && r.OutputBatchId == Guid.Empty), Is.True);
            Assert.That(events.Select(r => r.OccurredAtMilliseconds), Is.EqualTo(new[] { 200L, 1200 }));
        }

        [Test] public void ClearingWithUnrepresentableAbsoluteDueStillUsesBoundedWorkAtTheTerminalCutoff()
        {
            var f = new Setup(shift: long.MaxValue); f.Jam(); f.Act(ProductionAction.SetPower);
            f.World.AdvanceTo(long.MaxValue - 800); f.Act(ProductionAction.Repair);
            var result = f.World.AdvanceTo(long.MaxValue); Assert.That(result.World.Phase, Is.EqualTo(WorldPhase.Ended));
            Assert.That(result.ProductionChanges.Any(c => c.Kind == ProductionEvent.RepairCompleted), Is.False);
            Assert.That(f.World.Debrief!.Production.CancelledCycles, Is.EqualTo(1)); Assert.That(f.World.Debrief.Production.WasteUnits, Is.Zero);
        }

        [Test] public void RepairProgressOverflowFaultsBeforeDeadlinePublicationAndRetiresTheReservedCycle()
        {
            var f = new Setup(shift: 1200); f.Begin();
            var states = (Dictionary<Guid, MachineState>)typeof(ProductionOperations).GetField("_machines", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(f.World.Production)!;
            typeof(MachineState).GetField("<Revision>k__BackingField", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(states[f.Machine], long.MaxValue);
            Assert.Throws<OverflowException>(() => f.World.AdvanceTo(1200)); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(f.World.Production.MachineCount, Is.Zero); Assert.That(f.World.WorkerCount, Is.Zero); Assert.That(f.World.View.ActiveClaimCount, Is.Zero);
            Assert.That(f.World.Debrief!.Production.CancelledCycles, Is.EqualTo(1)); Assert.That(f.World.Debrief.Production.WasteUnits, Is.Zero);
            Assert.That(f.World.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended || r.ProductionEvent == ProductionEvent.RepairCompleted), Is.False);
        }

        [TestCase(-1)] [TestCase(60001)]
        public void AuthoredRepairDurationRemainsBounded(long duration) => Assert.Throws<ArgumentOutOfRangeException>(() =>
            new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100, repairDurationMilliseconds: duration));
    }
}
