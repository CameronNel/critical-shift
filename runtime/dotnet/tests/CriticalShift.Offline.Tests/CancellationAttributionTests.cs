using System;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class CancellationAttributionTests
    {
        [Test]
        public void CancelledJammedCycleKeepsItsIdentityInThePublicTrace()
        {
            var f = new ProductionFixture(moisture: 900);
            f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.World.AdvanceTo(500);
            f.Act(ProductionAction.SetPower, power: false);
            Assert.That(f.Act(ProductionAction.CancelCycle).HasNewCommit, Is.True);
            var record = f.World.Trace.Records.Last();
            Assert.That(record.CycleId, Is.EqualTo(cycle), "Resetting the machine must not erase the cancelled cycle.");
            Assert.That(record.ProductionEvent, Is.EqualTo(ProductionEvent.Cancelled));
            Assert.That(record.MaterialCauseId, Is.EqualTo(Fixture.Id(80)));
            Assert.That(record.OutputBatchId, Is.EqualTo(Guid.Empty));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Units, Is.EqualTo(100));
            Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
        }

        [TestCase(0, false)]
        [TestCase(0, true)]
        [TestCase(900, true)]
        public void CancellationRetainsItsOwnChoiceWithoutPublishingUnmadeOutput(int moisture, bool bypass)
        {
            var f = new ProductionFixture(moisture: moisture); f.Load();
            var original = f.World.Production.GetBatch(f.Box)!;
            var cycle = f.Act(ProductionAction.Start, bypass: bypass).Production!.Machine!.CycleId;
            f.World.AdvanceTo(moisture == 900 ? 500 : 100);
            f.Act(ProductionAction.SetPower, power: false);
            var reply = f.Act(ProductionAction.CancelCycle);
            var change = reply.Production!.Change!;
            var receipt = f.World.Production.GetConversion(cycle)!;
            Assert.Multiple(() =>
            {
                Assert.That(change.Kind, Is.EqualTo(ProductionEvent.Cancelled));
                Assert.That(change.CycleId, Is.EqualTo(cycle));
                Assert.That(change.RecipeId, Is.EqualTo(Fixture.Id(50)));
                Assert.That(change.BypassedInspection, Is.EqualTo(bypass));
                Assert.That(change.Machine.CycleId, Is.EqualTo(Guid.Empty));
                Assert.That(change.Machine.Mode, Is.EqualTo(ProductionMode.Idle));
                Assert.That(change.Input.BatchId, Is.EqualTo(original.BatchId));
                Assert.That(change.Input.OriginId, Is.EqualTo(original.OriginId));
                Assert.That(change.Input.CauseId, Is.EqualTo(original.CauseId));
                Assert.That(change.Input.Flags, Is.EqualTo(MaterialFlags.None));
                Assert.That(change.Output, Is.Null);
                Assert.That(change.WasteUnits, Is.Zero);
                Assert.That(receipt.Cancelled, Is.True);
                Assert.That(receipt.BypassedInspection, Is.EqualTo(bypass));
                Assert.That(receipt.Output, Is.Null);
                Assert.That(f.World.Trace.Records.Last().BypassedInspection, Is.EqualTo(bypass));
                Assert.That(f.World.Trace.Records.Last().RecipeId, Is.EqualTo(change.RecipeId));
                Assert.That(f.World.Production.GetBatch(f.Box)!.BatchId, Is.EqualTo(original.BatchId));
            });
            Assert.That(f.World.AdvanceTo(1000).ProductionChanges, Is.Empty);
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
        }

        [Test]
        public void ReplayedCancellationPreservesHistoricalDataButDoesNotPublishASecondEvent()
        {
            var f = new ProductionFixture(); f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, power: false);
            var command = new InteractionCommand(f.World.Epoch, 5, InteractionKind.Production, f.Machine,
                production: new ProductionRequest(ProductionAction.CancelCycle, f.World.Production.GetMachine(f.Machine)!.Revision));
            var first = f.World.ExecuteInteraction(f.Connection, command);
            long revision = f.World.View.Revision;
            var replay = f.World.ExecuteInteraction(f.Connection, command);
            Assert.That(replay.IsReplay, Is.True);
            Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(replay.Production!.Change, Is.SameAs(first.Production!.Change));
            Assert.That(replay.Production.Change!.CycleId, Is.EqualTo(cycle));
            Assert.That(f.World.Trace.Records.Count(x => x.ProductionEvent == ProductionEvent.Cancelled), Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Last().ProductionEvent, Is.Null);
            Assert.That(f.World.Trace.Records.Last().CycleId, Is.EqualTo(cycle));
            Assert.That(f.World.Trace.Records.Last().Changed, Is.False);
            Assert.That(f.World.View.Revision, Is.EqualTo(revision));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
        }

        [Test]
        public void LaterCycleCannotOverwriteCancelledReceiptOrItsCause()
        {
            var f = new ProductionFixture(); f.Load();
            var cancelledCycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, power: false);
            var cancelledChange = f.Act(ProductionAction.CancelCycle).Production!.Change!;
            f.Act(ProductionAction.SetPower, power: true);
            var nextCycle = f.Act(ProductionAction.Start).Production!.Machine!.CycleId;
            f.World.AdvanceTo(1000);
            var receipt = f.World.Production.GetConversion(cancelledCycle)!;
            Assert.That(nextCycle, Is.Not.EqualTo(cancelledCycle));
            Assert.That(receipt.Cancelled, Is.True);
            Assert.That(receipt.BypassedInspection, Is.True);
            Assert.That(receipt.Output, Is.Null);
            Assert.That(cancelledChange.CycleId, Is.EqualTo(cancelledCycle));
            Assert.That(cancelledChange.Input.CauseId, Is.EqualTo(Fixture.Id(80)));
            Assert.That(f.World.Production.GetConversion(nextCycle)!.BypassedInspection, Is.False);
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
        }

        [Test]
        public void InheritedBypassFlagDoesNotMisattributeTheCurrentCycleChoice()
        {
            var f = new ProductionFixture(); f.Load();
            f.Act(ProductionAction.Start, bypass: true); f.World.AdvanceTo(500);
            f.Act(ProductionAction.Eject); f.Grab(); f.Act(ProductionAction.Insert, f.Press);
            var cycle = f.Act(ProductionAction.Start, f.Press).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, f.Press, power: false);
            var change = f.Act(ProductionAction.CancelCycle, f.Press).Production!.Change!;
            Assert.That(change.Input.Flags, Is.EqualTo(MaterialFlags.BypassedInspection));
            Assert.That(change.BypassedInspection, Is.False, "The press did not bypass its own inspection.");
            Assert.That(f.World.Production.GetConversion(cycle)!.BypassedInspection, Is.False);
            Assert.That(f.World.Trace.Records.Last().BypassedInspection, Is.False);
            Assert.That(change.Output, Is.Null);
            Assert.That(change.WasteUnits, Is.Zero);
        }

        [Test]
        public void JamAndCompletionExposeTheSameCycleDecision()
        {
            var f = new ProductionFixture(moisture: 900); f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            var jam = f.World.AdvanceTo(500).ProductionChanges.Single();
            Assert.That(jam.CycleId, Is.EqualTo(cycle));
            Assert.That(jam.BypassedInspection, Is.True);
            Assert.That(jam.Output, Is.Null);
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.Repair);
            f.Act(ProductionAction.SetPower, power: true); f.Act(ProductionAction.Resume);
            var complete = f.World.AdvanceTo(800).ProductionChanges.Single();
            Assert.That(complete.CycleId, Is.EqualTo(cycle));
            Assert.That(complete.RecipeId, Is.EqualTo(jam.RecipeId));
            Assert.That(complete.BypassedInspection, Is.True);
            Assert.That(complete.Output!.Units, Is.EqualTo(80));
            Assert.That(f.World.Production.GetConversion(cycle)!.BypassedInspection, Is.True);
        }

        [Test]
        public void RejectedCancellationDoesNotPublishCommittedMetadata()
        {
            var f = new ProductionFixture(); f.Load(); f.Act(ProductionAction.Start, bypass: true);
            var rejected = f.Act(ProductionAction.CancelCycle);
            Assert.That(rejected.Production!.Status, Is.EqualTo(ProductionStatus.PowerMustBeOff));
            Assert.That(rejected.Production.Change, Is.Null);
            Assert.That(f.World.Trace.Records.Last().ProductionEvent, Is.Null);
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.Zero);
            Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1));
        }

        [Test]
        public void ConversionReceiptSurvivesDiagnosticRingEviction()
        {
            var f = new ProductionFixture(); f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.CancelCycle);
            for (int time = 1; time <= 150; time++) f.World.AdvanceTo(time);
            Assert.That(f.World.Trace.DroppedRecords, Is.GreaterThan(0));
            Assert.That(f.World.Trace.Records.Any(x => x.ProductionEvent == ProductionEvent.Cancelled), Is.False);
            var receipt = f.World.Production.GetConversion(cycle)!;
            Assert.That(receipt.Cancelled, Is.True);
            Assert.That(receipt.BypassedInspection, Is.True);
            Assert.That(receipt.Input.CauseId, Is.EqualTo(Fixture.Id(80)));
        }

        [Test]
        public void CancellationMetadataDoesNotRequireSpareHistoryCapacity()
        {
            var f = new ProductionFixture(cycles: 1); f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, power: false); f.Act(ProductionAction.CancelCycle);
            f.Act(ProductionAction.SetPower, power: true);
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.HistoryCapacityReached));
            Assert.That(f.World.Production.GetConversion(cycle)!.BypassedInspection, Is.True);
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(100));
        }

        [Test]
        public void CancelledEvidenceIsDetachedAcrossStopAndRestart()
        {
            var f = new ProductionFixture(); f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.Act(ProductionAction.SetPower, power: false);
            var evidence = f.Act(ProductionAction.CancelCycle).Production!.Change!;
            var trace = f.World.Trace;
            var next = f.World.Restart(new TestAccess());
            Assert.That(evidence.CycleId, Is.EqualTo(cycle));
            Assert.That(evidence.BypassedInspection, Is.True);
            Assert.That(trace.Records.Last().ProductionEvent, Is.EqualTo(ProductionEvent.Cancelled));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(next.Production.GetConversion(cycle), Is.Null);
            Assert.That(next.Trace.Records, Is.Empty);
            next.Stop();
        }
    }
}
