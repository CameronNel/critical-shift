using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class WorkerDeadlineSettlementTests
    {
        private static WorldSession Pending(long window)
        {
            var world = new WorldSession(new WorldSessionConfiguration(7, 5000, true), new TestAccess(),
                recoveryCompletionWindowMilliseconds: window);
            world.RegisterConnection(Fixture.Id(2), Fixture.Id(1)); world.Start();
            var hit = world.ApplyWorkerImpact(world.Epoch, Fixture.Id(1), 1, WorkerImpact.Knockdown, 0, Fixture.Id(70), Fixture.Id(80));
            Assert.That(world.BeginWorkerRecovery(world.Epoch, Fixture.Id(1), hit.Worker!.RecoveryEpisode, hit.Worker.Revision).Changed, Is.True);
            return world;
        }

        [TestCase(1000, 5000)]
        [TestCase(1000, long.MaxValue)]
        [TestCase(5000, 5000)]
        [TestCase(5001, 5000)]
        public void DeadlineSettlesStoredWorkerExpiryIndependentlyOfHostSampling(long window, long finalHost)
        {
            var direct = Pending(window); var sampled = Pending(window);
            bool expires = window <= 5000;
            if (window < 5000) sampled.AdvanceTo(window);
            else sampled.AdvanceTo(4999);
            var terminal = direct.AdvanceTo(finalHost); sampled.AdvanceTo(finalHost);
            var first = direct.Debrief!.WorkersAtEnd.Single(); var second = sampled.Debrief!.WorkersAtEnd.Single();
            Assert.That(first.Pose, Is.EqualTo(expires ? WorkerPose.Down : WorkerPose.Recovering));
            Assert.That(first.Pose, Is.EqualTo(second.Pose));
            Assert.That(first.Revision, Is.EqualTo(second.Revision));
            Assert.That(first.RecoveryExpiresAtMilliseconds, Is.EqualTo(expires ? 0 : window));
            Assert.That(terminal.WorkerChanges.Count, Is.EqualTo(expires ? 1 : 0));
            Assert.That(direct.View.Outcome, Is.EqualTo(WorldOutcome.TimedOut));
            Assert.That(direct.View.ActiveClaimCount, Is.Zero); Assert.That(direct.WorkerCount, Is.Zero);
            Assert.That(terminal.Signals, Is.Empty);
            Assert.That(direct.Debrief.Incidents.StandingRecoveries, Is.Zero);
            Assert.That(direct.Trace.Records.Count(r => r.Kind == SessionTraceKind.RecoveryExpired), Is.EqualTo(expires ? 1 : 0));
            Assert.That(direct.AdvanceTo(finalHost).WorkerChanges, Is.Empty);
        }

        [Test] public void OverdueWorkerExpiryKeepsItsDeadlineSeparateFromObservationTime()
        {
            var world = Pending(1000); var result = world.AdvanceTo(2000);
            Assert.That(result.WorkerChanges.Single().Status, Is.EqualTo(WorkerStatus.RecoveryExpired));
            var expired = world.Trace.Records.Single(r => r.Kind == SessionTraceKind.RecoveryExpired);
            Assert.That(expired.OccurredAtMilliseconds, Is.EqualTo(1000));
            Assert.That(expired.ShiftMilliseconds, Is.EqualTo(2000));
            Assert.That(expired.HostMilliseconds, Is.EqualTo(2000));
            Assert.That(expired.CauseId, Is.EqualTo(Fixture.Id(80)));
        }

        [Test] public void WorkerExpiryFailureFaultsBeforePublishingTheDeadlineResult()
        {
            var world = Pending(1000);
            var owner = typeof(WorldSession).GetField("_workers", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(world)!;
            var states = (IDictionary<Guid, WorkerState>)owner.GetType().GetField("_workers", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(owner)!;
            typeof(WorkerState).GetField("_revision", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(states[Fixture.Id(1)], long.MaxValue);
            Assert.Throws<OverflowException>(() => world.AdvanceTo(5000));
            Assert.That(world.View.Outcome, Is.EqualTo(WorldOutcome.Faulted));
            Assert.That(world.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended), Is.False);
            Assert.That(world.Debrief!.World.Outcome, Is.EqualTo(WorldOutcome.Faulted));
            Assert.That(world.WorkerCount, Is.Zero); Assert.That(world.View.ConnectedPlayerCount, Is.Zero);
        }
    }
}
