using System;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ReactorWorldTests
    {
        private static void Balanced(PowerView power) => Assert.That(power.Initial + power.Generated,
            Is.EqualTo(power.Available + power.Spent + power.Delivered + power.Spilled));
        private static ReactorFixture MakeFuel(bool bypass = false)
        {
            var f = new ReactorFixture(units: 100, kind: MaterialKind.Ore, start: false);
            f.World.Production.RegisterMachine(Fixture.Id(40), new MachineRecipe(Fixture.Id(50), MaterialKind.Ore,
                MaterialKind.CrushedOre, 1000, 500, 200, 1000, 800));
            f.World.Production.RegisterMachine(Fixture.Id(41), new MachineRecipe(Fixture.Id(51), MaterialKind.CrushedOre,
                MaterialKind.Fuel, 1000, 500, 200, 1000, 750));
            f.World.Start();
            Assert.That(f.Grab().HasNewCommit, Is.True);
            Assert.That(f.Production(ProductionAction.Insert, 40).HasNewCommit, Is.True);
            Assert.That(f.Production(ProductionAction.Start, 40, bypass).HasNewCommit, Is.True);
            f.World.AdvanceTo(1000);
            Assert.That(f.Production(ProductionAction.Eject, 40).HasNewCommit, Is.True);
            Assert.That(f.Grab().HasNewCommit, Is.True);
            Assert.That(f.Production(ProductionAction.Insert, 41).HasNewCommit, Is.True);
            Assert.That(f.Production(ProductionAction.Start, 41).HasNewCommit, Is.True);
            f.World.AdvanceTo(2000);
            Assert.That(f.Production(ProductionAction.Eject, 41).HasNewCommit, Is.True);
            return f;
        }

        [Test] public void ProducedFuelReachesReactorAndBecomesSpentFuel()
        {
            var f = MakeFuel(); f.Run(); var cycle = f.World.Reactor.View!.CycleId;
            f.World.AdvanceTo(8000);
            Assert.That(f.World.Production.GetBatch(f.Box)!.Kind, Is.EqualTo(MaterialKind.SpentFuel));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Units, Is.EqualTo(60));
            Assert.That(f.World.Production.GetConversion(cycle)!.Input.CauseId, Is.EqualTo(Fixture.Id(80)));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(3));
            Assert.That(f.World.Production.Summary.WasteUnits, Is.EqualTo(40));
            Assert.That(f.World.Reactor.View!.Power.Delivered, Is.EqualTo(240));
            Assert.That(f.World.Reactor.View.Power.Generated, Is.EqualTo(300)); Balanced(f.World.Reactor.View.Power);
        }

        [Test] public void BypassedProductionCarriesRiskToReactor()
        {
            var f = MakeFuel(true); f.Run();
            Assert.That(f.World.Reactor.View!.SuspectFuel, Is.True);
            var changes = f.World.AdvanceTo(2800).ReactorChanges;
            Assert.That(changes.Single(c => c.Kind == ReactorEvent.Warning).CauseId, Is.EqualTo(Fixture.Id(80)));
            Assert.That(f.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Tripped));
        }

        [Test] public void FuelCycleCompletionCannotRunTwice()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(1000);
            var power = f.World.Reactor.View!.Power;
            Assert.That(f.World.AdvanceTo(1000).ReactorChanges, Is.Empty);
            Assert.That(f.World.AdvanceTo(2000).ReactorChanges, Is.Empty);
            Assert.That(f.World.Reactor.View!.Power.Generated, Is.EqualTo(power.Generated));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Revision, Is.EqualTo(1));
        }

        [Test] public void StartupInterlocksPreserveReserveOnRejection()
        {
            var f = new ReactorFixture(); f.Load();
            Assert.That(f.Act(ReactorAction.Start).Reactor!.Status, Is.EqualTo(ReactorStatus.NoCooling));
            Assert.That(f.World.Reactor.View!.Power.Available, Is.EqualTo(10));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            f.Act(ReactorAction.SetCooling, true); f.Act(ReactorAction.AuxiliaryPower);
            var denied = f.Act(ReactorAction.AuxiliaryPower);
            Assert.That(denied.Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientReserve));
            Assert.That(f.Act(ReactorAction.Start).HasNewCommit, Is.True);
            Assert.That(f.World.Reactor.View.Power.Available, Is.EqualTo(1));
        }

        [Test] public void MatchingRetryDoesNotChargeOrCreateAnotherEvent()
        {
            var f = new ReactorFixture(); f.Load(); f.Act(ReactorAction.SetCooling, true);
            var revision = f.World.Reactor.View!.Revision;
            var command = new InteractionCommand(f.World.Epoch, f.Sequence + 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.Start, revision));
            var first = f.World.ExecuteInteraction(f.Connection, command);
            var replay = f.World.ExecuteInteraction(f.Connection, command);
            Assert.That(first.HasNewCommit, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(replay.IsReplay, Is.True);
            Assert.That(replay.Reactor!.Change!.EventId, Is.EqualTo(first.Reactor!.Change!.EventId));
            Assert.That(f.World.Reactor.View!.Power.Spent, Is.EqualTo(3));
            Assert.That(f.World.Trace.Records.Last().ReactorEvent, Is.Null);
            Assert.That(f.World.Trace.Records.Last().ReactorChange!.EventId, Is.EqualTo(first.Reactor.Change.EventId));
        }

        [Test] public void ChangedRetryPayloadAndForwardGapAreRejected()
        {
            var f = new ReactorFixture(); f.Act(ReactorAction.AuxiliaryPower);
            var changed = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.SetCooling, 0, cooling: true));
            Assert.That(f.World.ExecuteInteraction(f.Connection, changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            var gap = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, 1));
            Assert.That(f.World.ExecuteInteraction(f.Connection, gap).Status, Is.EqualTo(InteractionStatus.SequenceGap));
            Assert.That(f.World.Reactor.View!.Power.Spent, Is.EqualTo(6));
        }

        [Test] public void OldEvictedCommandsDoNotSpendAgain()
        {
            var f = new ReactorFixture(receipts: 2); f.Act(ReactorAction.AuxiliaryPower);
            for (int i = 0; i < 10000; i++) f.Act(ReactorAction.AuxiliaryPower);
            var old = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, old).Status, Is.EqualTo(InteractionStatus.TooOld));
            Assert.That(f.World.Reactor.View!.Power.Available, Is.EqualTo(4));
            Assert.That(f.World.Reactor.View.Power.Spent, Is.EqualTo(6));
        }

        [Test] public void CompetingConsumersCannotOverspend()
        {
            var f = new ReactorFixture(); f.Act(ReactorAction.AuxiliaryPower);
            InteractionReply Other(long seq, long rev) => f.World.ExecuteInteraction(Fixture.Id(21),
                new InteractionCommand(f.World.Epoch, seq, InteractionKind.Reactor, f.Reactor,
                    reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, rev)));
            Assert.That(Other(1, 0).Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict));
            Assert.That(Other(2, 1).Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientReserve));
            Assert.That(f.World.Reactor.View!.Power.Available, Is.EqualTo(4)); Balanced(f.World.Reactor.View.Power);
        }

        [Test] public void StaleRevisionCannotControlReactor()
        {
            var f = new ReactorFixture(); f.Act(ReactorAction.SetCooling, true);
            Assert.That(f.Send(new ReactorRequest(ReactorAction.SetCooling, 0)).Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict));
            Assert.That(f.World.Reactor.View!.Cooling, Is.True);
        }

        [Test] public void InvalidMixedPayloadDoesNotConsumeSequence()
        {
            var f = new ReactorFixture();
            var invalid = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Grab, f.Box,
                reactor: new ReactorRequest(ReactorAction.Start, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, invalid).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            invalid = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor,
                production: new ProductionRequest(ProductionAction.Start, 0), reactor: new ReactorRequest(ReactorAction.Start, 0));
            Assert.That(f.World.ExecuteInteraction(f.Connection, invalid).IsTerminal, Is.False);
            Assert.That(f.Grab().HasNewCommit, Is.True);
        }

        [Test] public void RestartRetainsNoCoreReserveOrClaims()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(200); var previous = f.World.Epoch;
            var old = new InteractionCommand(previous, f.Sequence + 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.Shutdown, f.World.Reactor.View!.Revision));
            f.World.Stop(); var next = f.World.Restart(new TestAccess());
            Assert.That(next.Reactor.View, Is.Null); Assert.That(next.Reactor.PowerSummary, Is.Null);
            next.RegisterConnection(f.Connection, f.Actor); next.Reactor.Register(f.Reactor, new ReactorDefinition(Fixture.Id(91))); next.Start();
            Assert.That(next.ExecuteInteraction(f.Connection, old).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(next.Reactor.View!.Power.Available, Is.EqualTo(10)); Assert.That(next.View.ActiveClaimCount, Is.Zero);
        }

        [TestCase(999, 9, false)] [TestCase(1000, 10, true)] [TestCase(1001, 10, true)]
        public void DeadlineCountsOnlyEnergyUpToCutoff(long deadline, int quanta, bool complete)
        {
            var f = new ReactorFixture(shift: deadline); f.Run();
            Assert.That(f.World.AdvanceTo(100000).EndedThisAdvance, Is.True);
            Assert.That(f.World.Reactor.View, Is.Null);
            Assert.That(f.World.Reactor.PowerSummary!.Generated, Is.EqualTo(quanta * 5));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(complete ? 1 : 0));
            Assert.That(f.World.Production.Summary.CancelledCycles, Is.EqualTo(complete ? 0 : 1));
            Balanced(f.World.Reactor.PowerSummary);
        }

        [Test] public void PauseStopsReactorWorkButNotReceiptProgress()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(200); f.World.Pause(f.World.Epoch);
            f.World.AdvanceTo(10000);
            Assert.That(f.World.Reactor.View!.WorkMilliseconds, Is.EqualTo(200));
            Assert.That(f.Act(ReactorAction.Shutdown).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(10100);
            Assert.That(f.World.Reactor.View.WorkMilliseconds, Is.EqualTo(300));
            Assert.That(f.Act(ReactorAction.Shutdown).HasNewCommit, Is.True);
        }

        [Test] public void LostCoolingWarnsAndTripsWithStableCause()
        {
            var f = new ReactorFixture(); f.Run(); var loss = f.Act(ReactorAction.SetCooling);
            var cause = loss.Reactor!.Change!.CauseId; var changes = f.World.AdvanceTo(5000).ReactorChanges;
            Assert.That(changes.Single(c => c.Kind == ReactorEvent.Warning).ShiftMilliseconds, Is.EqualTo(400));
            var trip = changes.Single(c => c.Kind == ReactorEvent.Tripped);
            Assert.That(trip.ShiftMilliseconds, Is.EqualTo(800)); Assert.That(trip.CauseId, Is.EqualTo(cause));
            Assert.That(trip.Risk, Is.EqualTo(ReactorRisk.CoolingLost));
            Assert.That(f.World.Reactor.View!.WorkMilliseconds, Is.EqualTo(800));
            Assert.That(f.World.Reactor.View.Power.Generated, Is.EqualTo(40));
        }

        [Test] public void SuspectFuelWarnsAtItsOwnBatchCause()
        {
            var f = new ReactorFixture(contamination: 900); f.Run();
            var changes = f.World.AdvanceTo(800).ReactorChanges;
            foreach (var change in changes.Where(c => c.Kind == ReactorEvent.Warning || c.Kind == ReactorEvent.Tripped))
            {
                Assert.That(change.CauseId, Is.EqualTo(Fixture.Id(80))); Assert.That(change.InputBatchId, Is.EqualTo(Fixture.Id(60)));
                Assert.That(change.Risk, Is.EqualTo(ReactorRisk.SuspectFuel));
            }
        }

        [Test] public void ShutdownAndRestartPreserveCycleAndFuelWork()
        {
            var f = new ReactorFixture(); f.Run(); var cycle = f.World.Reactor.View!.CycleId;
            f.World.AdvanceTo(333); f.Act(ReactorAction.Shutdown); f.World.AdvanceTo(1000);
            Assert.That(f.World.Reactor.View!.WorkMilliseconds, Is.EqualTo(333));
            f.Act(ReactorAction.Start); f.World.AdvanceTo(1667);
            Assert.That(f.World.Reactor.View!.CycleId, Is.EqualTo(cycle));
            Assert.That(f.World.Reactor.View.Power.Generated, Is.EqualTo(50));
            Assert.That(f.World.Reactor.View.Power.Spent, Is.EqualTo(6));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void PartUsedFuelCannotBeEjectedToRecharge()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(200); f.Act(ReactorAction.Shutdown);
            Assert.That(f.Act(ReactorAction.Eject).Reactor!.Status, Is.EqualTo(ReactorStatus.InvalidState));
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Reactor));
            Assert.That(f.World.Reactor.View!.WorkMilliseconds, Is.EqualTo(200));
        }

        [Test] public void SpentFuelCannotBeReused()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(1000); f.Act(ReactorAction.Eject); f.Grab();
            Assert.That(f.Act(ReactorAction.Insert).Reactor!.Status, Is.EqualTo(ReactorStatus.WrongFuel));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Reactor.View!.Power.Generated, Is.EqualTo(50));
        }

        [Test] public void IsolatedFuelCannotBeGrabbedByAnotherWorker()
        {
            var f = new ReactorFixture(); f.Run();
            var reply = f.World.ExecuteInteraction(Fixture.Id(21), new InteractionCommand(f.World.Epoch, 1,
                InteractionKind.Grab, f.Box, f.World.GetObject(f.Box)!.Revision));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.EntitySlotted));
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Reactor));
        }

        [Test] public void DeniedAccessDoesNotControlReactor()
        {
            var access = new TestAccess { Decision = AccessDecision.OutOfReach }; var f = new ReactorFixture(policy: access);
            Assert.That(f.Act(ReactorAction.AuxiliaryPower).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(f.World.Reactor.View!.Power.Spent, Is.Zero);
        }

        [Test] public void HistoryCapacityRejectsStartBeforeDebit()
        {
            var f = new ReactorFixture(cycles: 1, start: false); var other = Fixture.Id(31);
            f.World.Production.RegisterBatch(other, Fixture.Id(61), Fixture.Id(71), Fixture.Id(81), MaterialKind.Fuel, 10);
            f.World.Start(); f.Run(); f.World.AdvanceTo(1000); f.Act(ReactorAction.Eject);
            f.Grab(other); f.Act(ReactorAction.Insert, box: other);
            var power = f.World.Reactor.View!.Power;
            Assert.That(f.Act(ReactorAction.Start).Reactor!.Status, Is.EqualTo(ReactorStatus.HistoryCapacityReached));
            Assert.That(f.World.Reactor.View.Power.Spent, Is.EqualTo(power.Spent));
            Assert.That(f.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Loaded));
        }

        [Test] public void FailedInsertDoesNotTakeInputFromOtherActor()
        {
            var f = new ReactorFixture(); f.Grab(); var item = f.World.GetObject(f.Box)!;
            var request = new ReactorRequest(ReactorAction.Insert, 0, f.Box, item.Revision, 0, item.LeaseGeneration);
            var reply = f.World.ExecuteInteraction(Fixture.Id(21), new InteractionCommand(f.World.Epoch, 1,
                InteractionKind.Reactor, f.Reactor, reactor: request));
            Assert.That(reply.Reactor!.Status, Is.EqualTo(ReactorStatus.CustodyRejected));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Empty));
        }

        [Test] public void DuplicateRegistrationDoesNotDamageExistingSetup()
        {
            var f = new ReactorFixture(start: false); var initial = f.World.Reactor.View;
            Assert.Throws<InvalidOperationException>(() => f.World.Reactor.Register(Fixture.Id(92), new ReactorDefinition(Fixture.Id(93))));
            Assert.That(f.World.Reactor.View!.Id, Is.EqualTo(initial!.Id)); f.World.Start(); f.Run();
            Assert.That(f.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Running));
        }

        [TestCase(MaterialKind.Ore, 10, ReactorStatus.WrongFuel)]
        [TestCase(MaterialKind.SpentFuel, 10, ReactorStatus.WrongFuel)]
        [TestCase(MaterialKind.Fuel, 10001, ReactorStatus.OverCapacity)]
        public void FuelValidationPreservesCustody(MaterialKind kind, int units, ReactorStatus expected)
        {
            var f = new ReactorFixture(kind: kind, units: units); f.Grab();
            Assert.That(f.Act(ReactorAction.Insert).Reactor!.Status, Is.EqualTo(expected));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Units, Is.EqualTo(units));
        }

        [Test] public void PowerSummaryIsDetachedAfterTerminalTeardown()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(200);
            var before = f.World.Reactor.View!; f.World.Stop(); var summary = f.World.Reactor.PowerSummary;
            Assert.That(summary!.Generated, Is.EqualTo(10)); Assert.That(before.Power.Generated, Is.EqualTo(10));
            f.World.Stop(); f.World.AdvanceTo(5000);
            Assert.That(f.World.Reactor.PowerSummary, Is.SameAs(summary));
            Assert.That(f.World.Reactor.View, Is.Null); Assert.That(f.World.View.RegisteredObjectCount, Is.Zero);
        }

        [Test] public void EmergencyCoolingChargesOnceAndDoesNotRestart()
        {
            var f = new ReactorFixture(); f.Run(); f.Act(ReactorAction.SetCooling); f.World.AdvanceTo(800);
            var request = new ReactorRequest(ReactorAction.EmergencyCooling, f.World.Reactor.View!.Revision);
            var command = new InteractionCommand(f.World.Epoch, f.Sequence + 1, InteractionKind.Reactor, f.Reactor, reactor: request);
            Assert.That(f.World.ExecuteInteraction(f.Connection, command).HasNewCommit, Is.True);
            Assert.That(f.World.ExecuteInteraction(f.Connection, command).IsReplay, Is.True);
            Assert.That(f.World.Reactor.View!.Power.Spent, Is.EqualTo(7));
            Assert.That(f.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Tripped));
            Assert.That(f.World.Reactor.View.InstabilityMilliseconds, Is.EqualTo(400));
            f.World.AdvanceTo(1100);
            var reset = new InteractionCommand(f.World.Epoch, f.Sequence + 2, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.ResetTrip, f.World.Reactor.View.Revision));
            Assert.That(f.World.ExecuteInteraction(f.Connection, reset).HasNewCommit, Is.True);
            Assert.That(f.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Shutdown));
        }

        [Test] public void FinalFuelEjectionRetainsOriginalCycleAttribution()
        {
            var f = new ReactorFixture(); f.Run(); var cycle = f.World.Reactor.View!.CycleId;
            f.World.AdvanceTo(1000); var reply = f.Act(ReactorAction.Eject);
            Assert.That(reply.Reactor!.State!.CycleId, Is.EqualTo(Guid.Empty));
            Assert.That(reply.Reactor.Change!.CycleId, Is.EqualTo(cycle));
            Assert.That(reply.Reactor.Change.InputBatchId, Is.EqualTo(Fixture.Id(60)));
            Assert.That(reply.Reactor.Change.CauseId, Is.EqualTo(Fixture.Id(80)));
        }

        [Test] public void UnexpectedAccessFailureFaultsWorldAndPreservesAccounting()
        {
            var access = new TestAccess(); var f = new ReactorFixture(policy: access); f.Run(); f.World.AdvanceTo(200);
            access.Callback = () => throw new InvalidOperationException("Synthetic observation failure");
            Assert.Throws<InvalidOperationException>(() => f.Act(ReactorAction.AuxiliaryPower));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(f.World.Reactor.View, Is.Null); Assert.That(f.World.Reactor.PowerSummary!.Generated, Is.EqualTo(10));
            Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(3));
        }
    }
}
