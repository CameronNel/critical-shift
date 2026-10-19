using System;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ReactorReadoutTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private static void Route(ReactorFixture f, ReactorOutputRouting route) => Assert.That(f.Send(new ReactorRequest(
            ReactorAction.SetOutputRouting, f.World.Reactor.View!.Revision, outputRouting: route)).HasNewCommit, Is.True);

        [TestCase(ReactorOutputRouting.Balanced, "grid 3 / reserve 2")]
        [TestCase(ReactorOutputRouting.GridPriority, "grid 5 / reserve 0")]
        [TestCase(ReactorOutputRouting.ReservePriority, "grid 0 / reserve 5")]
        public void ReactorInstrumentUsesAuthoredQuantumAndCurrentAllocation(ReactorOutputRouting route, string allocation)
        {
            var f = new ReactorFixture(definition: new ReactorDefinition(Id(91), reservePerQuantum: 2, gridPerQuantum: 3, powerQuantumMilliseconds: 250));
            if (route != ReactorOutputRouting.Balanced) Route(f, route);
            var text = SandboxReactorReadout.Output(f.World.Reactor.View!);
            Assert.That(text, Does.Contain(allocation)); Assert.That(text, Does.Contain("0.25s"));
            if (route == ReactorOutputRouting.ReservePriority) Assert.That(text, Does.Contain("no contract delivery"));
            if (route == ReactorOutputRouting.GridPriority) Assert.That(text, Does.Contain("does not refill"));
        }

        [Test] public void ReactorSummaryUsesAuthoredCostsBoundsAndRemainingFuel()
        {
            var f = new ReactorFixture(definition: new ReactorDefinition(Id(91), 80, 30, 5, 7,
                millisecondsPerFuelUnit: 1000, warningMilliseconds: 1000, tripMilliseconds: 2000, resetMilliseconds: 200, emergencyReliefMilliseconds: 600));
            f.Run(); f.World.AdvanceTo(1250); string text = SandboxReactorReadout.Summary(f.World.Reactor.View!);
            Assert.That(text, Does.Contain("8.75s")); Assert.That(text, Does.Contain("Start/restart 5 reserve")); Assert.That(text, Does.Contain("emergency cooling 7"));
            Assert.That(text, Does.Contain("0.6s instability")); Assert.That(text, Does.Contain("trip 2s"));
            Assert.That(text, Does.Contain("trip reset / spent-fuel eject threshold 0.2s")); Assert.That(text, Does.Contain("/80"));
        }

        [Test] public void LoadedFuelGuidanceExplainsCoolingAndTheUnusedFuelExit()
        {
            var f = new ReactorFixture(); f.Load();
            string text = SandboxReactorReadout.Controls(f.World.Reactor.View!);
            Assert.That(text, Does.Contain("F open cooling")); Assert.That(text, Does.Contain("E eject unused fuel"));
            Assert.That(SandboxReactorReadout.Result(f.Act(ReactorAction.Start).Reactor!), Does.Contain("Open cooling"));
        }

        [Test] public void TrippedGuidanceSeparatesCoolingWaitResetAndPaidRestart()
        {
            var f = new ReactorFixture(); f.Run(); f.Act(ReactorAction.SetCooling, false); f.World.AdvanceTo(800);
            Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("F restore cooling"));
            f.Act(ReactorAction.SetCooling, true); Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("Wait 0.7s"));
            f.World.AdvanceTo(1499); Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("Wait 0.001s"));
            f.World.AdvanceTo(1500); Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("R reset trip, then R restart (3 reserve)"));
            f.Act(ReactorAction.ResetTrip); Assert.That(f.World.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Shutdown));
            Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("R start reactor"));
        }

        [Test] public void ExhaustedFuelGuidanceWaitsForTheSpentMaterialInterlock()
        {
            var f = new ReactorFixture(units: 4, contamination: 1000); f.Run(); f.World.AdvanceTo(400);
            Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("Wait 0.3s"));
            f.World.AdvanceTo(700); Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("E eject spent fuel"));
        }

        [TestCase(false)] [TestCase(true)]
        public void LowReserveGuidanceDistinguishesAbsentAndAvailableBackup(bool backup)
        {
            var f = new ReactorFixture(definition: new ReactorDefinition(Id(91), initialReserve: 0), start: false);
            if (backup) f.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(1000, 12, 1)); f.World.Start();
            f.Load(); f.Act(ReactorAction.SetCooling, true);
            string text = SandboxReactorReadout.Result(f.Act(ReactorAction.Start).Reactor!, ReactorAction.Start);
            Assert.That(text, Does.Contain("needs 3, available 0")); Assert.That(text, Does.Contain(backup ? "Start finite backup" : "No backup source"));
        }

        [Test] public void BackupAdviceDetectsInsufficientHeadroomInsteadOfOfferingAnotherBlockedStart()
        {
            var f = new ReactorFixture(definition: new ReactorDefinition(Id(91), reserveCapacity: 12, initialReserve: 11, startupCost: 12), start: false);
            f.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(1000, 12, 1)); f.World.Start(); f.Load(); f.Act(ReactorAction.SetCooling, true);
            string text = SandboxReactorReadout.Controls(f.World.Reactor.View!);
            Assert.That(text, Does.Contain("Backup needs 12 free reserve capacity")); Assert.That(text, Does.Not.Contain("Start finite backup"));
        }

        [Test] public void RunningSuspectFuelExplainsThatCoolingDoesNotRemoveItsRisk()
        {
            var f = new ReactorFixture(contamination: 1000); f.Run();
            Assert.That(SandboxReactorReadout.Controls(f.World.Reactor.View!), Does.Contain("Suspect fuel continues building instability despite cooling"));
        }

        [Test] public void FrozenReactorReadoutCannotAdvanceWorkChangeRoutingOrSubmitACommand()
        {
            var f = new ReactorFixture(); f.Run(); f.World.AdvanceTo(150); var frozen = f.World.Reactor.View!;
            long revision = frozen.Revision, sequence = f.Sequence; string before = SandboxReactorReadout.Summary(frozen);
            SandboxReactorReadout.Controls(frozen); SandboxReactorReadout.Summary(frozen);
            Assert.That(f.World.Reactor.View!.Revision, Is.EqualTo(revision)); Assert.That(f.Sequence, Is.EqualTo(sequence));
            Route(f, ReactorOutputRouting.GridPriority); f.World.AdvanceTo(300);
            Assert.That(SandboxReactorReadout.Summary(frozen), Is.EqualTo(before)); Assert.That(frozen.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced));
        }
    }
}
