using System;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ProductionWorldTests
    {
        [Test]
        public void OreToFuelPreservesQuantityLineageAndOriginalCause()
        {
            var f = new ProductionFixture(); f.Load();
            var original = f.World.Production.GetBatch(f.Box)!;
            var start = f.Act(ProductionAction.Start); var cycle = start.Production!.Machine!.CycleId;
            Assert.That(f.World.AdvanceTo(999).ProductionChanges, Is.Empty);
            Assert.That(f.World.Production.GetBatch(f.Box)!.BatchId, Is.EqualTo(original.BatchId));
            var done = f.World.AdvanceTo(1000).ProductionChanges.Single();
            Assert.That(done.Output!.Units, Is.EqualTo(80)); Assert.That(done.WasteUnits, Is.EqualTo(20));
            Assert.That(done.Output.ParentBatchId, Is.EqualTo(original.BatchId));
            Assert.That(done.Output.CauseId, Is.EqualTo(original.CauseId));
            Assert.That(f.Act(ProductionAction.Eject).HasNewCommit, Is.True);
            Assert.That(f.Grab().HasNewCommit, Is.True);
            Assert.That(f.Act(ProductionAction.Insert, f.Press).HasNewCommit, Is.True);
            Assert.That(f.Act(ProductionAction.Start, f.Press).HasNewCommit, Is.True);
            var final = f.World.AdvanceTo(2000).ProductionChanges.Single().Output!;
            Assert.That(final.Kind, Is.EqualTo(MaterialKind.Fuel)); Assert.That(final.Units, Is.EqualTo(60));
            Assert.That(final.ParentBatchId, Is.EqualTo(done.Output.BatchId));
            Assert.That(final.OriginId, Is.EqualTo(original.OriginId));
            Assert.That(final.Contamination, Is.EqualTo(35));
            Assert.That(f.World.Production.GetConversion(cycle)!.Output!.BatchId, Is.EqualTo(done.Output.BatchId));
            Assert.That(f.World.Production.Summary.ActiveUnits + f.World.Production.Summary.WasteUnits, Is.EqualTo(100));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(2));
        }
        [Test]
        public void SlotIsTheOnlyCustodyOwnerAndCannotBeGrabbedOrRetired()
        {
            var f = new ProductionFixture(); f.Load();
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Machine));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.Null);
            Assert.That(f.World.View.ActiveClaimCount, Is.Zero);
            Assert.That(f.Grab().Status, Is.EqualTo(InteractionStatus.EntitySlotted));
            Assert.That(f.World.RetireObject(f.World.Epoch, f.Box).HasNewCommit, Is.False);
            Assert.That(f.Act(ProductionAction.Eject).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.Null);
            Assert.That(f.Grab().HasNewCommit, Is.True);
        }
        [Test]
        public void MachineAndGrabShareOneReplayStream()
        {
            var f = new ProductionFixture(); f.Load();
            var c = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Start, 1));
            var first = f.World.ExecuteInteraction(f.Connection, c);
            Assert.That(first.HasNewCommit, Is.True);
            var retry = f.World.ExecuteInteraction(f.Connection, c);
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(retry.Production!.Machine!.CycleId, Is.EqualTo(first.Production!.Machine!.CycleId));
            var changed = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Start, 1, bypass: true));
            Assert.That(f.World.ExecuteInteraction(f.Connection, changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            var grabOld = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Grab, f.Box);
            Assert.That(f.World.ExecuteInteraction(f.Connection, grabOld).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            f.World.AdvanceTo(1000);
            Assert.That(f.World.ExecuteInteraction(f.Connection, c).HasNewCommit, Is.False);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }
        [Test]
        public void WetSafeRejectionThenBypassJamRepairAndCompletion()
        {
            var f = new ProductionFixture(moisture: 900); f.Load();
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.WetInput));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.Act(ProductionAction.Start, bypass: true).HasNewCommit, Is.True);
            var jam = f.World.AdvanceTo(500).ProductionChanges.Single();
            Assert.That(jam.Kind, Is.EqualTo(ProductionEvent.Jammed));
            Assert.That(jam.Machine.WorkMilliseconds, Is.EqualTo(200));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Units, Is.EqualTo(100));
            Assert.That(f.Act(ProductionAction.Repair).Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.Repair);
            Assert.That(f.Act(ProductionAction.Resume).Production!.Status, Is.EqualTo(ProductionStatus.NoPower));
            f.Act(ProductionAction.SetPower, power: true); f.Act(ProductionAction.Resume);
            Assert.That(f.World.AdvanceTo(799).ProductionChanges, Is.Empty);
            var output = f.World.AdvanceTo(800).ProductionChanges.Single().Output!;
            Assert.That(output.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Assert.That(output.Moisture, Is.Zero); Assert.That(output.Units, Is.EqualTo(80));
            Assert.That(f.World.AdvanceTo(1000).ProductionChanges, Is.Empty);
        }
        [Test]
        public void PowerLossStopsWorkAndRestorationRequiresExplicitResume()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(400);
            f.Act(ProductionAction.SetPower, power: false); f.World.AdvanceTo(2000);
            Assert.That(f.World.Production.GetMachine(f.Machine)!.WorkMilliseconds, Is.EqualTo(400));
            f.Act(ProductionAction.SetPower, power: true); f.World.AdvanceTo(3000);
            Assert.That(f.World.Production.GetMachine(f.Machine)!.Mode, Is.EqualTo(ProductionMode.PowerPaused));
            f.Act(ProductionAction.Resume);
            Assert.That(f.World.AdvanceTo(3600).ProductionChanges.Single().Kind, Is.EqualTo(ProductionEvent.Completed));
        }
        [Test]
        public void WorldPauseStopsProcessClockAndRejectsMachineCommands()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(400);
            f.World.Pause(f.World.Epoch); f.World.AdvanceTo(5000);
            Assert.That(f.World.Production.GetMachine(f.Machine)!.WorkMilliseconds, Is.EqualTo(400));
            Assert.That(f.Act(ProductionAction.SetPower, power: false).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            f.World.Resume(f.World.Epoch); Assert.That(f.Act(ProductionAction.SetPower, power: false).HasNewCommit, Is.True);
        }
        [Test]
        public void CancellationKeepsInputAndCannotManufactureOutputLater()
        {
            var f = new ProductionFixture(); f.Load(); var original = f.World.Production.GetBatch(f.Box)!;
            var cycle = f.Act(ProductionAction.Start).Production!.Machine!.CycleId;
            Assert.That(f.Act(ProductionAction.CancelCycle).Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            f.Act(ProductionAction.SetPower, power: false);
            Assert.That(f.Act(ProductionAction.CancelCycle).HasNewCommit, Is.True);
            Assert.That(f.World.Production.GetConversion(cycle)!.Cancelled, Is.True);
            Assert.That(f.World.Production.GetBatch(f.Box)!.BatchId, Is.EqualTo(original.BatchId));
            Assert.That(f.World.AdvanceTo(5000).ProductionChanges, Is.Empty);
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.Act(ProductionAction.Eject).HasNewCommit, Is.True);
        }
        [Test]
        public void IncapacitationDoesNotEjectAnAlreadySlottedBatch()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start);
            f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Incapacitating, 100, Fixture.Id(800), Fixture.Id(900));
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Machine));
            Assert.That(f.Act(ProductionAction.SetPower, power: false).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(f.World.AdvanceTo(1000).ProductionChanges.Count, Is.EqualTo(1));
        }
        [Test]
        public void DisconnectDoesNotAbortCommittedMachineProcess()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start);
            f.World.Disconnect(f.World.Epoch, f.Connection);
            Assert.That(f.World.AdvanceTo(1000).ProductionChanges.Count, Is.EqualTo(1));
            Assert.That(f.World.View.ConnectedPlayerCount, Is.Zero);
        }
        [Test]
        public void FullPortAndWrongMachineAreNonDestructive()
        {
            var f = new ProductionFixture(); f.Load();
            Assert.That(f.Act(ProductionAction.Insert).Production!.Status, Is.EqualTo(ProductionStatus.Occupied));
            f.Act(ProductionAction.Eject); f.Grab();
            Assert.That(f.Act(ProductionAction.Insert, f.Press).Production!.Status, Is.EqualTo(ProductionStatus.WrongInput));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100));
        }
        [Test]
        public void OverCapacityLoadLeavesHeldItemUnchanged()
        {
            var f = new ProductionFixture(units: 101, maximum: 100); f.Grab(); var before = f.World.GetObject(f.Box)!;
            Assert.That(f.Act(ProductionAction.Insert).Production!.Status, Is.EqualTo(ProductionStatus.OverCapacity));
            Assert.That(f.World.GetObject(f.Box)!.Revision, Is.EqualTo(before.Revision));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
        }
        [Test]
        public void RoundedZeroOutputIsRejectedBeforeReservingOrConsuming()
        {
            var f = new ProductionFixture(units: 1, yield: 1); f.Load();
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.OutputTooSmall));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.GetMachine(f.Machine)!.Mode, Is.EqualTo(ProductionMode.Idle));
        }
        [Test]
        public void HistoryCapacityIsReservedBeforeCycleStarts()
        {
            var f = new ProductionFixture(cycles: 1); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(1000);
            f.Act(ProductionAction.Eject); f.Grab(); f.Act(ProductionAction.Insert, f.Press);
            Assert.That(f.Act(ProductionAction.Start, f.Press).Production!.Status, Is.EqualTo(ProductionStatus.HistoryCapacityReached));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Kind, Is.EqualTo(MaterialKind.CrushedOre));
        }
        [TestCase(999, 0)]
        [TestCase(1000, 1)]
        [TestCase(1001, 1)]
        public void ShiftDeadlineCommitsDueProductionBeforeCleanup(long duration, int completions)
        {
            var f = new ProductionFixture(shift: duration); f.Load(); f.Act(ProductionAction.Start);
            var result = f.World.AdvanceTo(100000);
            Assert.That(result.EndedThisAdvance, Is.True);
            Assert.That(result.ProductionChanges.Count, Is.EqualTo(completions));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(completions));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1 - completions));
            Assert.That(f.World.Production.Summary.ActiveUnits + f.World.Production.Summary.WasteUnits, Is.EqualTo(100));
            Assert.That(f.World.Production.MachineCount, Is.Zero); Assert.That(f.World.Production.BatchCount, Is.Zero);
            Assert.That(f.World.AdvanceTo(100000).ProductionChanges, Is.Empty);
        }
        [Test]
        public void ProductionRestartClearsLiveDataAndRetainsOnlyTerminalSummary()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start);
            var next = f.World.Restart(new TestAccess());
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(next.Production.Summary.IssuedUnits, Is.Zero);
            Assert.That(next.Production.MachineCount, Is.Zero); Assert.That(next.Production.BatchCount, Is.Zero);
            Assert.That(f.World.Production.GetBatch(f.Box), Is.Null);
            Assert.That(next.Epoch, Is.Not.EqualTo(f.World.Epoch));
            next.Stop();
        }
        [Test]
        public void ProductionSetupCannotMutateAfterStartOrUseCollidingIds()
        {
            var f = new ProductionFixture(start: false);
            Assert.Throws<InvalidOperationException>(() => f.World.RegisterObject(f.Machine));
            Assert.Throws<InvalidOperationException>(() => f.World.Production.RegisterBatch(f.Box, Fixture.Id(61), Fixture.Id(71), Fixture.Id(81), MaterialKind.Ore, 10));
            Assert.That(f.World.Production.Summary.IssuedUnits, Is.EqualTo(100));
            f.World.Start();
            Assert.Throws<InvalidOperationException>(() => f.World.Production.RegisterBatch(Fixture.Id(31), Fixture.Id(61), Fixture.Id(71), Fixture.Id(81), MaterialKind.Ore, 10));
        }
        [Test]
        public void WrongEpochProductionRequestDoesNotCallPolicy()
        {
            var policy = new TestAccess(); var f = new ProductionFixture(policy: policy);
            var command = new InteractionCommand(Guid.NewGuid(), 1, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Start, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, command).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(policy.Calls, Is.Zero);
        }
        [Test]
        public void StaleMachineOrObjectRevisionCannotMoveMaterial()
        {
            var f = new ProductionFixture(); f.Grab();
            var request = new ProductionRequest(ProductionAction.Insert, 0, f.Box, objectRevision: 999, leaseGeneration: 1);
            var reply = f.World.ExecuteInteraction(f.Connection, new InteractionCommand(f.World.Epoch, 2, InteractionKind.Production, f.Machine, production: request));
            Assert.That(reply.Production!.Status, Is.EqualTo(ProductionStatus.CustodyRejected));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Production.GetMachine(f.Machine)!.Revision, Is.Zero);
        }
        [Test]
        public void CannotEjectWhileProcessingOrJammed()
        {
            var f = new ProductionFixture(moisture: 900); f.Load(); f.Act(ProductionAction.Start, bypass: true);
            Assert.That(f.Act(ProductionAction.Eject).Production!.Status, Is.EqualTo(ProductionStatus.InvalidState));
            f.World.AdvanceTo(200);
            Assert.That(f.Act(ProductionAction.Eject).Production!.Status, Is.EqualTo(ProductionStatus.InvalidState));
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Machine));
        }
        [Test]
        public void MalformedProductionPayloadDoesNotConsumeSequence()
        {
            var f = new ProductionFixture();
            var invalid = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.Insert, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, invalid).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            Assert.That(f.Grab().HasNewCommit, Is.True);
        }
        [Test]
        public void UnknownMachineIsTerminalAndDoesNotJamInputSequence()
        {
            var f = new ProductionFixture();
            var c = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Production, Fixture.Id(999), production: new ProductionRequest(ProductionAction.Start, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, c).Production!.Status, Is.EqualTo(ProductionStatus.UnknownMachine));
            Assert.That(f.World.ExecuteInteraction(f.Connection, new InteractionCommand(f.World.Epoch, 2, InteractionKind.Grab, f.Box)).HasNewCommit, Is.True);
        }
        [Test]
        public void ProductionReadViewsCannotMutateOwners()
        {
            var f = new ProductionFixture(); f.Load(); var before = f.World.Production.GetMachine(f.Machine)!;
            var batch = f.World.Production.GetBatch(f.Box)!; f.Act(ProductionAction.Start); f.World.AdvanceTo(1000);
            Assert.That(before.Mode, Is.EqualTo(ProductionMode.Idle)); Assert.That(batch.Kind, Is.EqualTo(MaterialKind.Ore));
            foreach (var type in new[] { typeof(MaterialView), typeof(MachineView), typeof(ProductionRequest), typeof(MachineRecipe), typeof(ProductionSummary), typeof(ConversionView), typeof(ProductionChange) })
                foreach (var p in type.GetProperties()) Assert.That(p.SetMethod, Is.Null, p.Name);
        }
    }
}
