using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class WorldSessionTests
    {
        private static Guid Actor => Fixture.Id(10);
        private static Guid Connection => Fixture.Id(20);
        private static Guid Box => Fixture.Id(30);
        private static WorldSession New(long duration = 10000, bool pause = true, int timers = 8,
            TestAccess? access = null, bool start = true)
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, duration, pause, timers), access ?? new TestAccess());
            if (start) BindAndStart(world);
            return world;
        }
        private static void BindAndStart(WorldSession world)
        { world.RegisterConnection(Connection, Actor); world.RegisterObject(Box); world.Start(); }
        private static InteractionCommand Grab(WorldSession w, long seq = 1) =>
            new InteractionCommand(w.Epoch, seq, InteractionKind.Grab, Box);
        private static WorldTimerHandle Schedule(WorldSession w, long delay = 100,
            WorldTimeBasis basis = WorldTimeBasis.ShiftTime, Guid? owner = null)
        {
            var reply = w.Schedule(w.Epoch, owner ?? Box, "signal", delay, basis);
            Assert.That(reply.Status, Is.EqualTo(WorldControlStatus.Applied));
            return reply.Handle!;
        }

        [Test]
        public void SessionStartsOnlyWithConfiguredRoster()
        {
            var w = New(start: false);
            Assert.That(w.Schedule(w.Epoch, Box, "x", 0).Status, Is.EqualTo(WorldControlStatus.NotReady));
            Assert.Throws<InvalidOperationException>(() => w.Start());
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Setup));
            BindAndStart(w);
            Assert.Throws<InvalidOperationException>(() => w.Start());
            Assert.Throws<InvalidOperationException>(() => w.RegisterObject(Fixture.Id(999)));
        }

        [Test]
        public void SessionUsesSeedButDifferentEpoch()
        {
            var a = New(); var b = New();
            Assert.That(a.Epoch, Is.Not.EqualTo(b.Epoch));
            Assert.That(a.View.Seed, Is.EqualTo(b.View.Seed));
            Assert.That(a.ExecuteInteraction(Connection, Grab(b)).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
        }

        [Test]
        public void SessionTickDrivesBothTimerBases()
        {
            var w = New(); w.AdvanceTo(100);
            Schedule(w, 200, WorldTimeBasis.RealTime); Schedule(w, 200);
            w.Pause(w.Epoch);
            var paused = w.AdvanceTo(400);
            Assert.That(paused.Signals.Select(x => x.Basis), Is.EqualTo(new[] { WorldTimeBasis.RealTime }));
            Assert.That(paused.World.ElapsedMilliseconds, Is.EqualTo(100));
            w.Resume(w.Epoch);
            var resumed = w.AdvanceTo(600);
            Assert.That(resumed.Signals.Select(x => x.Basis), Is.EqualTo(new[] { WorldTimeBasis.ShiftTime }));
            Assert.That(resumed.World.ElapsedMilliseconds, Is.EqualTo(300));
            Assert.That(resumed.World.RemainingMilliseconds, Is.EqualTo(9700));
        }

        [Test]
        public void PausedSessionStopsShiftButExpiresClaimsAndRealTimers()
        {
            var w = New(); w.ExecuteInteraction(Connection, Grab(w));
            Schedule(w, 50); Schedule(w, 50, WorldTimeBasis.RealTime);
            w.Pause(w.Epoch);
            var tick = w.AdvanceTo(3000);
            Assert.That(tick.World.ElapsedMilliseconds, Is.Zero);
            Assert.That(tick.World.ActiveClaimCount, Is.Zero);
            Assert.That(tick.ReleasedClaims.Single().EntityId, Is.EqualTo(Box));
            Assert.That(tick.Signals.Single().Basis, Is.EqualTo(WorldTimeBasis.RealTime));
            Assert.That(tick.World.PendingTimerCount, Is.EqualTo(1));
        }

        [Test]
        public void PausedGrabRejectionDoesNotBlockNextCommand()
        {
            var w = New(); w.Pause(w.Epoch);
            var rejected = w.ExecuteInteraction(Connection, Grab(w));
            Assert.That(rejected.Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(rejected.IsTerminal, Is.True);
            w.Resume(w.Epoch);
            Assert.That(w.ExecuteInteraction(Connection, Grab(w, 2)).HasNewCommit, Is.True);
        }

        [Test]
        public void SessionAllowsReleaseAndRenewalDuringPause()
        {
            var w = New(); w.ExecuteInteraction(Connection, Grab(w)); w.Pause(w.Epoch); w.AdvanceTo(500);
            var renew = w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 2,
                InteractionKind.Renew, Box, leaseGeneration: 1));
            Assert.That(renew.State!.ExpiresAtMilliseconds, Is.EqualTo(3500));
            var release = w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 3,
                InteractionKind.Release, Box, leaseGeneration: 1));
            Assert.That(release.HasNewCommit, Is.True);
            Assert.That(w.View.ActiveClaimCount, Is.Zero);
        }

        [Test]
        public void SessionEndsOnlyOnceAtDeadline()
        {
            var w = New(100); w.ExecuteInteraction(Connection, Grab(w));
            Schedule(w, 50); Schedule(w, 100, WorldTimeBasis.RealTime);
            var result = w.AdvanceTo(100);
            Assert.That(result.EndedThisAdvance, Is.True);
            Assert.That(result.World.Outcome, Is.EqualTo(WorldOutcome.TimedOut));
            Assert.That(result.World.RemainingMilliseconds, Is.Zero);
            Assert.That(result.Signals, Is.Empty);
            Assert.That(result.World.ActiveClaimCount, Is.Zero);
            Assert.That(result.World.RegisteredObjectCount, Is.Zero);
            Assert.That(result.World.PendingTimerCount, Is.Zero);
            Assert.That(w.AdvanceTo(1000).EndedThisAdvance, Is.False);
            Assert.That(w.Finish(w.Epoch, WorldEndReason.Succeeded), Is.EqualTo(WorldControlStatus.Ended));
            Assert.That(w.ExecuteInteraction(Connection, Grab(w, 2)).Status, Is.EqualTo(InteractionStatus.WorldStopped));
            Assert.That(w.Schedule(w.Epoch, Box, "late", 0).Status, Is.EqualTo(WorldControlStatus.Ended));
        }

        [TestCase(WorldEndReason.Succeeded, WorldOutcome.Succeeded)]
        [TestCase(WorldEndReason.Failed, WorldOutcome.Failed)]
        [TestCase(WorldEndReason.Aborted, WorldOutcome.Aborted)]
        [TestCase(WorldEndReason.HostLost, WorldOutcome.HostLost)]
        public void SessionFinishClearsTimersClaimsAndRegistry(WorldEndReason reason, WorldOutcome expected)
        {
            var w = New(); w.ExecuteInteraction(Connection, Grab(w)); Schedule(w);
            Assert.That(w.Finish(w.Epoch, reason), Is.EqualTo(WorldControlStatus.Applied));
            Assert.That(w.Finish(w.Epoch, WorldEndReason.Failed), Is.EqualTo(WorldControlStatus.Ended));
            Assert.That(w.View.Outcome, Is.EqualTo(expected));
            Assert.That(w.View.PendingTimerCount, Is.Zero);
            Assert.That(w.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(w.View.RegisteredObjectCount, Is.Zero);
            w.Stop(); w.Stop(); Assert.That(w.View.Outcome, Is.EqualTo(expected));
        }

        [Test]
        public void SessionRejectsOldControlsAndTimers()
        {
            var w = New(); var wrong = Fixture.Id(999);
            Assert.That(w.Pause(wrong), Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(w.Resume(wrong), Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(w.Finish(wrong, WorldEndReason.Failed), Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(w.Schedule(wrong, Box, "late", 0).Status, Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Running));
        }

        [Test]
        public void RestartDropsEverythingExceptConfiguration()
        {
            var old = New(); old.ExecuteInteraction(Connection, Grab(old)); Schedule(old); old.AdvanceTo(100);
            var next = old.Restart(new TestAccess());
            Assert.That(old.View.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(old.View.RegisteredObjectCount, Is.Zero);
            Assert.That(old.View.PendingTimerCount, Is.Zero);
            Assert.That(next.Epoch, Is.Not.EqualTo(old.Epoch));
            Assert.That(next.View.Phase, Is.EqualTo(WorldPhase.Setup));
            Assert.That(next.View.ElapsedMilliseconds, Is.Zero);
            Assert.That(next.Configuration, Is.SameAs(old.Configuration));
            Assert.That(next.View.ActiveClaimCount, Is.Zero);
            Assert.Throws<InvalidOperationException>(() => old.Restart(new TestAccess()));
            BindAndStart(next);
            Assert.That(next.ExecuteInteraction(Connection, Grab(next)).HasNewCommit, Is.True);
        }

        [Test]
        public void RepeatedRestartsNeverAccumulateOwnership()
        {
            var w = New(); var epochs = new HashSet<Guid>();
            for (int i = 0; i < 50; i++)
            {
                Assert.That(epochs.Add(w.Epoch), Is.True);
                w.ExecuteInteraction(Connection, Grab(w)); Schedule(w, 0);
                var previous = w; w = w.Restart(new TestAccess());
                Assert.That(previous.View.PendingTimerCount, Is.Zero);
                Assert.That(previous.View.ActiveClaimCount, Is.Zero);
                Assert.That(previous.View.ConnectedPlayerCount, Is.Zero);
                Assert.That(previous.AdvanceTo(0).Signals, Is.Empty);
                BindAndStart(w);
            }
        }

        [Test]
        public void OldSignalCannotScheduleOrReleaseInSuccessor()
        {
            var old = New(); Schedule(old, 0); var signal = old.AdvanceTo(0).Signals.Single();
            var next = old.Restart(new TestAccess()); BindAndStart(next);
            next.ExecuteInteraction(Connection, Grab(next));
            Assert.That(next.Schedule(signal.Handle.Epoch, Box, "old", 0).Status, Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(next.ReportAttachmentFailure(old.Epoch, Box, 1).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(next.ExecuteInteraction(Connection, new InteractionCommand(old.Epoch, 2,
                InteractionKind.Release, Box, leaseGeneration: 1)).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(next.View.ActiveClaimCount, Is.EqualTo(1));
        }

        [Test]
        public void SessionCanBeStoppedBeforeStart()
        {
            var w = New(start: false); w.Stop(); w.Stop();
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(w.View.Outcome, Is.EqualTo(WorldOutcome.Aborted));
            Assert.Throws<InvalidOperationException>(() => w.Start());
            Assert.That(w.AdvanceTo(10).Signals, Is.Empty);
        }

        [Test]
        public void SessionReadOnlyProjectionDetached()
        {
            var w = New(); var before = w.View; Schedule(w, 0);
            var tick = w.AdvanceTo(100); w.Stop();
            Assert.That(before.Phase, Is.EqualTo(WorldPhase.Running));
            Assert.That(before.ElapsedMilliseconds, Is.Zero);
            Assert.That(before.PendingTimerCount, Is.Zero);
            Assert.That(tick.World.ElapsedMilliseconds, Is.EqualTo(100));
            Assert.Throws<NotSupportedException>(() => ((IList<WorldTimerSignal>)tick.Signals).Clear());
        }

        [Test]
        public void SessionRejectsReentrantPolicyAndFaultsCleanly()
        {
            var policy = new TestAccess(); var w = New(access: policy); Schedule(w);
            policy.Callback = () => w.AdvanceTo(1);
            Assert.Throws<InvalidOperationException>(() => w.ExecuteInteraction(Connection, Grab(w)));
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(w.View.Outcome, Is.EqualTo(WorldOutcome.Faulted));
            Assert.That(w.View.PendingTimerCount, Is.Zero);
            Assert.That(w.View.RegisteredObjectCount, Is.Zero);
            Assert.That(w.ExecuteInteraction(Connection, Grab(w)).Status, Is.EqualTo(InteractionStatus.WorldFaulted));
        }

        [Test]
        public void SessionUnexpectedPolicyExceptionClearsResources()
        {
            var policy = new TestAccess(); var w = New(access: policy); Schedule(w);
            policy.Callback = () => throw new InvalidOperationException("Test host observation failure");
            Assert.Throws<InvalidOperationException>(() => w.ExecuteInteraction(Connection, Grab(w)));
            Assert.That(w.View.ActiveClaimCount, Is.Zero);
            Assert.That(w.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(w.View.Outcome, Is.EqualTo(WorldOutcome.Faulted));
        }

        [Test]
        public void InvalidSessionTimesAndSchedulesPreserveState()
        {
            var w = New(); w.AdvanceTo(100); long revision = w.View.Revision;
            Assert.Throws<ArgumentOutOfRangeException>(() => w.AdvanceTo(99));
            Assert.Throws<ArgumentOutOfRangeException>(() => w.Schedule(w.Epoch, Box, "x", -1));
            Assert.Throws<ArgumentOutOfRangeException>(() => w.Finish(w.Epoch, (WorldEndReason)99));
            Assert.Throws<ArgumentNullException>(() => w.Restart(null!));
            Assert.That(w.View.ElapsedMilliseconds, Is.EqualTo(100));
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Running));
            Assert.That(w.View.Revision, Is.EqualTo(revision));
        }

        [Test]
        public void SessionTimerCapacityAndOwnerCleanup()
        {
            var w = New(timers: 2); Schedule(w); Schedule(w);
            Assert.That(w.Schedule(w.Epoch, Box, "full", 0).Status, Is.EqualTo(WorldControlStatus.TimerCapacityReached));
            Assert.That(w.CancelTimersForOwner(Fixture.Id(999), Box), Is.Zero);
            Assert.That(w.CancelTimersForOwner(w.Epoch, Box), Is.EqualTo(2));
            Assert.That(w.View.PendingTimerCount, Is.Zero);
            Schedule(w);
        }

        [Test]
        public void SessionPauseDisabledByDefault()
        {
            var w = new WorldSession(new WorldSessionConfiguration(1, 1000), new TestAccess()); BindAndStart(w);
            Assert.That(w.Pause(w.Epoch), Is.EqualTo(WorldControlStatus.PauseDisabled));
            Assert.That(w.AdvanceTo(100).World.ElapsedMilliseconds, Is.EqualTo(100));
        }

        [Test]
        public void WrongEpochCannotCancelAnotherWorldsTimerWithSameNumber()
        {
            var a = New(); var first = Schedule(a);
            var b = a.Restart(new TestAccess()); BindAndStart(b); var second = Schedule(b);
            Assert.That(first.Sequence, Is.EqualTo(second.Sequence));
            Assert.That(b.CancelTimer(first), Is.EqualTo(WorldControlStatus.WrongEpoch));
            Assert.That(b.View.PendingTimerCount, Is.EqualTo(1));
            Assert.That(b.CancelTimer(second), Is.EqualTo(WorldControlStatus.Applied));
            Assert.That(b.CancelTimer(second), Is.EqualTo(WorldControlStatus.NoChange));
        }

        [Test]
        public void SetupReplacementReclaimsSlotAndRetainsReusedIdProtection()
        {
            var w = new InteractionWorld(Fixture.Id(500), new TestAccess(), maxConnections: 1);
            w.RegisterConnection(Connection, Actor); w.Disconnect(Connection);
            w.RegisterConnection(Fixture.Id(21), Fixture.Id(11));
            Assert.That(w.ConnectedCount, Is.EqualTo(1));
            Assert.That(w.RetainedConnectionIdentityCount, Is.EqualTo(2));
            Assert.Throws<InvalidOperationException>(() => w.RegisterConnection(Connection, Actor));
            w.RegisterObject(Box); w.Start();
            Assert.That(w.Execute(Connection, new InteractionCommand(w.Epoch, 1, InteractionKind.Grab, Box)).Status,
                Is.EqualTo(InteractionStatus.UnknownConnection));
        }

        [Test]
        public void SetupIdentityHistoryIsBounded()
        {
            var w = new InteractionWorld(Fixture.Id(500), new TestAccess(), maxConnections: 1, maxConnectionIdentities: 2);
            for (int i = 0; i < 2; i++)
            { var connection = Fixture.Id(20 + i); w.RegisterConnection(connection, Actor); w.Disconnect(connection); }
            Assert.Throws<InvalidOperationException>(() => w.RegisterConnection(Fixture.Id(22), Actor));
            Assert.That(w.RetainedConnectionIdentityCount, Is.EqualTo(2));
            Assert.That(w.ConnectedCount, Is.Zero);
            w.Stop(); Assert.That(w.RetainedConnectionIdentityCount, Is.Zero);
        }

        [Test]
        public void SameActorCanRejoinSetupWithFreshConnection()
        {
            var w = New(start: false); w.RegisterConnection(Connection, Actor); w.Disconnect(w.Epoch, Connection);
            w.RegisterConnection(Fixture.Id(21), Actor); w.RegisterObject(Box); w.Start();
            Assert.That(w.ExecuteInteraction(Fixture.Id(21), Grab(w)).HasNewCommit, Is.True);
        }

        [Test]
        public void SnapshotRevisionMonotonicAndReadHasNoSideEffects()
        {
            var w = New(); var first = w.View;
            Assert.That(w.View.Revision, Is.EqualTo(first.Revision));
            w.Pause(w.Epoch); var paused = w.View;
            Assert.That(paused.HostMilliseconds, Is.EqualTo(first.HostMilliseconds));
            Assert.That(paused.Revision, Is.GreaterThan(first.Revision));
            w.Resume(w.Epoch); long before = w.View.Revision; var timer = Schedule(w);
            Assert.That(w.View.Revision, Is.GreaterThan(before));
            before = w.View.Revision; w.CancelTimer(timer);
            Assert.That(w.View.Revision, Is.GreaterThan(before));
            before = w.View.Revision; w.Stop(); Assert.That(w.View.Revision, Is.GreaterThan(before));
            before = w.View.Revision; w.Stop(); Assert.That(w.View.Revision, Is.EqualTo(before));
        }

        [Test]
        public void RestartRequiresExplicitPolicyRebinding()
        {
            var oldPolicy = new TestAccess(); var old = New(access: oldPolicy);
            var nextPolicy = new TestAccess { Decision = AccessDecision.OutOfReach };
            var next = old.Restart(nextPolicy); BindAndStart(next);
            Assert.That(next.ExecuteInteraction(Connection, Grab(next)).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(oldPolicy.Calls, Is.Zero);
            Assert.That(nextPolicy.Calls, Is.EqualTo(1));
        }

        [Test]
        public void StaleDisconnectCannotRemoveNewWorldPlayer()
        {
            var old = New(); var next = old.Restart(new TestAccess()); BindAndStart(next);
            next.ExecuteInteraction(Connection, Grab(next));
            Assert.That(next.Disconnect(old.Epoch, Connection), Is.Null);
            Assert.That(next.View.ConnectedPlayerCount, Is.EqualTo(1));
            Assert.That(next.View.ActiveClaimCount, Is.EqualTo(1));
            Assert.That(next.Disconnect(next.Epoch, Connection)!.HolderId, Is.Null);
            Assert.That(next.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(next.View.ActiveClaimCount, Is.Zero);
        }

        [Test]
        public void RetiringObjectCancelsOnlyItsTimers()
        {
            var w = New(); Schedule(w); Schedule(w, owner: Actor);
            w.ExecuteInteraction(Connection, Grab(w));
            Assert.That(w.RetireObject(w.Epoch, Box).HasNewCommit, Is.True);
            Assert.That(w.GetObject(Box)!.IsRetired, Is.True);
            Assert.That(w.View.ActiveClaimCount, Is.Zero);
            Assert.That(w.View.PendingTimerCount, Is.EqualTo(1));
            Assert.That(w.AdvanceTo(100).Signals.Single().OwnerId, Is.EqualTo(Actor));
        }

        [Test]
        public void InvalidConfigurationIsRejectedBeforeCreatingWorld()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, timerCapacity: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, timerCapacity: 4097));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, maxObjects: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, maxConnections: 5));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, receiptCapacity: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSessionConfiguration(1, 1, leaseMilliseconds: 0));
            Assert.Throws<ArgumentNullException>(() => new WorldSession(null!, new TestAccess()));
            Assert.Throws<ArgumentNullException>(() => new WorldSession(new WorldSessionConfiguration(1, 1), null!));
        }

        [Test]
        public void StartOriginAppliesToClaimsAndRealTimers()
        {
            var w = New(start: false); w.RegisterConnection(Connection, Actor); w.RegisterObject(Box); w.Start(1000000);
            Assert.That(w.ExecuteInteraction(Connection, Grab(w)).State!.ExpiresAtMilliseconds, Is.EqualTo(1003000));
            Schedule(w, 10, WorldTimeBasis.RealTime);
            Assert.That(w.AdvanceTo(1000010).Signals.Single().DueMilliseconds, Is.EqualTo(1000010));
            Assert.That(w.View.ElapsedMilliseconds, Is.EqualTo(10));
        }

        [Test]
        public void ReplayedAcceptanceDoesNotAdvanceSessionRevision()
        {
            var w = New(); w.ExecuteInteraction(Connection, Grab(w)); long revision = w.View.Revision;
            Assert.That(w.ExecuteInteraction(Connection, Grab(w)).HasNewCommit, Is.False);
            Assert.That(w.View.Revision, Is.EqualTo(revision));
            w.AdvanceTo(0); Assert.That(w.View.Revision, Is.EqualTo(revision));
        }
    }
}
