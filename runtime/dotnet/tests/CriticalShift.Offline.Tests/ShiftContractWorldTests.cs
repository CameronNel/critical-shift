using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Power.Domain;
using CriticalShift.Features.Session.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ShiftContractWorldTests
    {
        private static ShiftContractDefinition Definition(long firstQuota = 20, long secondQuota = 20) =>
            new ShiftContractDefinition(Fixture.Id(920), "Two grid windows",
                new GridDemandWave(Fixture.Id(921), "Startup supply", 500, firstQuota),
                new GridDemandWave(Fixture.Id(922), "Peak supply", 1000, secondQuota, 200));
        private static ReactorFixture Setup(long firstQuota = 20, long secondQuota = 20)
        {
            var f = new ReactorFixture(units: 100, shift: 1000, start: false);
            f.World.Contracts.Register(Definition(firstQuota, secondQuota)); f.World.Start(); f.Run(); return f;
        }

        [Test] public void ContractRegistrationIsSetupOnlyAndRequiresTheExactShiftDeadline()
        {
            var f = new ReactorFixture(shift: 1000, start: false); long revision = f.World.View.Revision;
            var wrong = new ShiftContractDefinition(Fixture.Id(920), "Wrong deadline", new GridDemandWave(Fixture.Id(921), "Window", 999, 1));
            Assert.Throws<ArgumentException>(() => f.World.Contracts.Register(wrong));
            Assert.That(f.World.Contracts.View, Is.Null); Assert.That(f.World.View.Revision, Is.EqualTo(revision));
            f.World.Contracts.Register(Definition()); Assert.Throws<InvalidOperationException>(() => f.World.Contracts.Register(Definition()));
            f.World.Start(); Assert.Throws<InvalidOperationException>(() => f.World.Contracts.Register(Definition()));
        }

        [Test] public void ContractUsesCanonicalPowerAndWarnsBeforeTheNextDemandWindow()
        {
            var f = Setup(); f.World.AdvanceTo(299);
            Assert.That(f.World.Contracts.View!.Upcoming, Is.Null);
            f.World.AdvanceTo(300); var progress = f.World.Contracts.View!;
            Assert.That(progress.Upcoming!.Label, Is.EqualTo("Peak supply"));
            Assert.That(progress.Upcoming.StartMilliseconds, Is.EqualTo(500));
            Assert.That(progress.DeliveredEnergyUnits, Is.EqualTo(f.World.Reactor.PowerSummary!.Delivered));
            Assert.That(progress.DeliveredEnergyUnits, Is.EqualTo(12));
            Assert.That(progress.Current!.DeliveredEnergyUnits, Is.EqualTo(12));
            Assert.That(progress.Current.Settled, Is.False); Assert.That(progress.Waves[1].DeliveredEnergyUnits, Is.Zero);
        }

        [Test] public void ExactDeadlineCreditsFinalQuantumAndPublishesOneSuccessBeforeTeardown()
        {
            var f = Setup(); var old = f.World.Contracts.View!;
            var result = f.World.AdvanceTo(1000);
            Assert.That(result.EndedThisAdvance, Is.True); Assert.That(result.World.Outcome, Is.EqualTo(WorldOutcome.Succeeded));
            Assert.That(result.DemandChanges.Count, Is.EqualTo(2));
            Assert.That(result.DemandChanges.Select(x => x.ShiftMilliseconds), Is.EqualTo(new long[] { 500, 1000 }));
            var final = f.World.Contracts.View!;
            Assert.That(final.Complete && final.AllPeriodsMet, Is.True);
            Assert.That(final.DeliveredEnergyUnits, Is.EqualTo(40)); Assert.That(final.Waves.Select(x => x.DeliveredEnergyUnits), Is.EqualTo(new long[] { 20, 20 }));
            Assert.That(f.World.Reactor.View, Is.Null); Assert.That(f.World.Reactor.PowerSummary!.Delivered, Is.EqualTo(40));
            Assert.That(old.DeliveredEnergyUnits, Is.Zero); Assert.That(old.Complete, Is.False);
            Assert.That(f.World.AdvanceTo(2000).EndedThisAdvance, Is.False);
            Assert.That(f.World.Contracts.View, Is.SameAs(final));
            Assert.That(f.World.Trace.Records.Count(x => x.Kind == SessionTraceKind.Ended), Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Count(x => x.Kind == SessionTraceKind.Contract), Is.EqualTo(2));
            Assert.That(f.World.View.ActiveClaimCount, Is.Zero); Assert.That(f.World.View.ConnectedPlayerCount, Is.Zero);
        }

        [Test] public void InsufficientDemandFailsEvenWhenAnotherWindowHasSurplus()
        {
            var f = Setup(firstQuota: 21, secondQuota: 1); f.World.AdvanceTo(1000);
            Assert.That(f.World.View.Outcome, Is.EqualTo(WorldOutcome.Failed));
            Assert.That(f.World.Contracts.View!.DeliveredEnergyUnits, Is.GreaterThan(22));
            Assert.That(f.World.Contracts.View.Waves[0].ShortfallEnergyUnits, Is.EqualTo(1));
            Assert.That(f.World.Contracts.View.Waves[1].Met, Is.True);
        }

        [Test] public void ContractCannotBePrepaidOrManuallySucceededBeforeAllWindowsSettle()
        {
            var f = Setup(1, 1); f.World.AdvanceTo(100);
            Assert.That(f.World.Contracts.View!.DeliveredEnergyUnits, Is.GreaterThan(2));
            long revision = f.World.View.Revision;
            Assert.That(f.World.Finish(f.World.Epoch, WorldEndReason.Succeeded), Is.EqualTo(WorldControlStatus.ContractIncomplete));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(f.World.View.Revision, Is.EqualTo(revision));
            Assert.That(f.World.Contracts.View.SettledPeriods, Is.Zero);
        }

        [Test] public void PauseConsumesNoDemandWindowAndResumeDoesNotCatchUp()
        {
            var f = Setup(); f.World.AdvanceTo(400); f.World.Pause(f.World.Epoch);
            f.World.AdvanceTo(10000);
            Assert.That(f.World.Contracts.View!.ElapsedMilliseconds, Is.EqualTo(400));
            Assert.That(f.World.Contracts.View.SettledPeriods, Is.Zero);
            f.World.Resume(f.World.Epoch); var result = f.World.AdvanceTo(10600);
            Assert.That(result.World.ElapsedMilliseconds, Is.EqualTo(1000)); Assert.That(result.World.Outcome, Is.EqualTo(WorldOutcome.Succeeded));
            Assert.That(f.World.Contracts.View!.DeliveredEnergyUnits, Is.EqualTo(40));
        }

        [Test] public void OversizedHostJumpAndManySamplesProduceTheSameContractAssessment()
        {
            var one = Setup(); var many = Setup();
            one.World.AdvanceTo(long.MaxValue);
            for (int time = 7; time < 1000; time += 7) many.World.AdvanceTo(time);
            many.World.AdvanceTo(1000);
            Assert.That(one.World.View.Outcome, Is.EqualTo(many.World.View.Outcome));
            Assert.That(one.World.Contracts.View!.Waves.Select(x => x.DeliveredEnergyUnits),
                Is.EqualTo(many.World.Contracts.View!.Waves.Select(x => x.DeliveredEnergyUnits)));
            Assert.That(one.World.Reactor.PowerSummary!.Generated, Is.EqualTo(many.World.Reactor.PowerSummary!.Generated));
        }

        [Test] public void NonQuantumDemandBoundaryAttributesOnlyCompletedGenerationQuanta()
        {
            var f = new ReactorFixture(shift: 1000, units: 100, start: false);
            f.World.Contracts.Register(new ShiftContractDefinition(Fixture.Id(920), "Staggered demand",
                new GridDemandWave(Fixture.Id(921), "First window", 250, 8),
                new GridDemandWave(Fixture.Id(922), "Second window", 1000, 32)));
            f.World.Start(); f.Run(); f.World.AdvanceTo(1000);
            Assert.That(f.World.View.Outcome, Is.EqualTo(WorldOutcome.Succeeded));
            Assert.That(f.World.Contracts.View!.Waves.Select(x => x.DeliveredEnergyUnits), Is.EqualTo(new long[] { 8, 32 }));
            Assert.That(f.World.Reactor.PowerSummary!.Delivered, Is.EqualTo(40));
        }

        [Test] public void FuelExhaustionLeavesLaterDemandUnpaidAndDoesNotCreateMoreEnergy()
        {
            var f = new ReactorFixture(shift: 1000, units: 2, start: false);
            f.World.Contracts.Register(Definition(8, 4)); f.World.Start(); f.Run();
            f.World.AdvanceTo(1000);
            Assert.That(f.World.View.Outcome, Is.EqualTo(WorldOutcome.Failed));
            Assert.That(f.World.Contracts.View!.Waves.Select(x => x.DeliveredEnergyUnits), Is.EqualTo(new long[] { 8, 0 }));
            Assert.That(f.World.Contracts.View.Waves[0].Met, Is.True); Assert.That(f.World.Contracts.View.Waves[1].Met, Is.False);
            Assert.That(f.World.Reactor.PowerSummary!.Delivered, Is.EqualTo(8));
        }

        [TestCase(WorldEndReason.Aborted, WorldOutcome.Aborted)]
        [TestCase(WorldEndReason.HostLost, WorldOutcome.HostLost)]
        [TestCase(WorldEndReason.Failed, WorldOutcome.Failed)]
        public void EarlyTerminalPathsRetainDetachedContractProgress(WorldEndReason reason, WorldOutcome expected)
        {
            var f = Setup(); f.World.AdvanceTo(300); f.World.Finish(f.World.Epoch, reason);
            var result = f.World.Contracts.View!; Assert.That(result.Outcome, Is.EqualTo(expected));
            Assert.That(result.DeliveredEnergyUnits, Is.EqualTo(12)); Assert.That(result.Complete, Is.False);
            f.World.Stop(); Assert.That(f.World.Contracts.View, Is.SameAs(result));
            Assert.That(f.World.Contracts.View!.Outcome, Is.EqualTo(expected));
        }

        [Test] public void RestartCreatesFreshContractProgressAndRejectsOldEpochControls()
        {
            var f = Setup(); f.World.AdvanceTo(500); var old = f.World.Contracts.View!;
            var next = f.World.Restart(new TestAccess());
            Assert.That(next.Contracts.View, Is.Null); next.Contracts.Register(Definition());
            Assert.That(next.Contracts.View!.DeliveredEnergyUnits, Is.Zero); Assert.That(next.Contracts.View.Epoch, Is.Not.EqualTo(old.Epoch));
            Assert.That(next.Finish(old.Epoch, WorldEndReason.Succeeded), Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(old.DeliveredEnergyUnits, Is.EqualTo(20));
        }

        [TestCase(false)]
        [TestCase(true)]
        public void FailedDeadlineSettlementFaultsBeforePublishingAnyTerminalSuccessOrTimeout(bool contract)
        {
            var f = new ReactorFixture(shift: 1000, units: 100, start: false);
            if (contract) f.World.Contracts.Register(Definition());
            f.World.Start(); f.Run();
            var field = typeof(ReactorOperations).GetField("_power", BindingFlags.NonPublic | BindingFlags.Instance)!;
            field.SetValue(f.World.Reactor, new PowerAccount(100, 10).Credit(0, long.MaxValue));
            Assert.Throws<OverflowException>(() => f.World.AdvanceTo(1000));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted)); Assert.That(f.World.View.Outcome, Is.EqualTo(WorldOutcome.Faulted));
            Assert.That(f.World.Trace.Records.Any(x => x.Kind == SessionTraceKind.Ended), Is.False);
            Assert.That(f.World.View.ActiveClaimCount, Is.Zero);
            if (contract) Assert.That(f.World.Contracts.View!.Outcome, Is.EqualTo(WorldOutcome.Faulted));
        }

        [Test] public void TimelinePreviewAndAssessedDeadlineAreObservationalUntilCommit()
        {
            var timeline = new SessionTimeline(Fixture.Id(940), 1, 1000, true); timeline.Start(50);
            Assert.That(timeline.PreviewElapsedAt(long.MaxValue), Is.EqualTo(1000));
            Assert.That(timeline.ElapsedMilliseconds, Is.Zero); Assert.That(timeline.Outcome, Is.EqualTo(TimelineOutcome.None));
            Assert.Throws<ArgumentOutOfRangeException>(() => timeline.AdvanceTo(1050, TimelineOutcome.Aborted));
            Assert.That(timeline.ElapsedMilliseconds, Is.Zero);
            timeline.AdvanceTo(1050, TimelineOutcome.Succeeded);
            Assert.That(timeline.Outcome, Is.EqualTo(TimelineOutcome.Succeeded));
            Assert.That(timeline.TryFinish(TimelineOutcome.Failed), Is.False);
        }
    }
}
