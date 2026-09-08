using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class WorkerWorldTests
    {
        private static Guid Actor => Fixture.Id(10);
        private static Guid Other => Fixture.Id(11);
        private static Guid Connection => Fixture.Id(20);
        private static Guid Box => Fixture.Id(30);
        private sealed class Clearance : IWorkerRecoveryPolicy
        {
            internal RecoveryClearance Result = RecoveryClearance.Safe;
            internal int Calls;
            internal Action? Callback;
            public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt)
            { Calls++; Callback?.Invoke(); return Result; }
        }
        private static WorldSession World(IWorkerRecoveryPolicy? recovery = null, int trace = 128)
        {
            var w = new WorldSession(new WorldSessionConfiguration(42, 20000, true), new TestAccess(), recovery, trace);
            Bind(w); return w;
        }
        private static void Bind(WorldSession w)
        { w.RegisterConnection(Connection, Actor); w.RegisterConnection(Fixture.Id(21), Other); w.RegisterObject(Box); w.Start(); }
        private static InteractionCommand Grab(WorldSession w, long seq = 1, long rev = 0) =>
            new InteractionCommand(w.Epoch, seq, InteractionKind.Grab, Box, expectedRevision: rev);
        private static WorkerReply Hit(WorldSession w, WorkerImpact kind = WorkerImpact.Knockdown, long seq = 1, long delay = 100) =>
            w.ApplyWorkerImpact(w.Epoch, Actor, seq, kind, delay);
        private static WorkerReply Begin(WorldSession w)
        { var s = w.GetWorker(Actor)!; return w.BeginWorkerRecovery(w.Epoch, Actor, s.RecoveryEpisode, s.Revision); }

        [TestCase(WorkerImpact.Knockdown)] [TestCase(WorkerImpact.Incapacitating)]
        public void IncapacitationReleasesExistingClaimWithoutDisconnecting(WorkerImpact kind)
        {
            var w = World(); w.ExecuteInteraction(Connection, Grab(w));
            var hit = Hit(w, kind);
            Assert.That(hit.Changed, Is.True); Assert.That(hit.ReleasedClaim!.EntityId, Is.EqualTo(Box));
            Assert.That(w.GetObject(Box)!.HolderId, Is.Null); Assert.That(w.View.ConnectedPlayerCount, Is.EqualTo(2));
            Assert.That(w.WorkerCount, Is.EqualTo(2)); Assert.That(w.View.ActiveClaimCount, Is.Zero);
        }
        [Test] public void InvalidOrRepeatedImpactDoesNotReleaseANewHolder()
        {
            var w = World(); w.ExecuteInteraction(Connection, Grab(w));
            var invalid = w.ApplyWorkerImpact(w.Epoch, Actor, 1, (WorkerImpact)99, 0);
            Assert.That(invalid.Status, Is.EqualTo(WorkerStatus.InvalidInput)); Assert.That(w.View.ActiveClaimCount, Is.EqualTo(1));
            Hit(w); w.ExecuteInteraction(Fixture.Id(21), Grab(w, rev: 2));
            Assert.That(Hit(w).Status, Is.EqualTo(WorkerStatus.Duplicate));
            Assert.That(w.GetObject(Box)!.HolderId, Is.EqualTo(Other));
        }
        [Test] public void DownWorkerCannotGrabAndRejectedSequenceDoesNotWedgeInput()
        {
            var w = World(new Clearance()); Hit(w, delay: 0);
            Assert.That(w.ExecuteInteraction(Connection, Grab(w)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Begin(w); w.CompleteWorkerRecovery(w.Epoch, Actor, 1);
            Assert.That(w.ExecuteInteraction(Connection, Grab(w, 2)).HasNewCommit, Is.True);
        }
        [Test] public void UnconsciousWorkerNeedsExplicitAidAndKeepsEnvironment()
        {
            var w = World(new Clearance()); w.SetWorkerEnvironment(w.Epoch, Actor, 0, WorkerSuit.Intact, 40);
            Hit(w, WorkerImpact.Incapacitating); w.AdvanceTo(1000);
            Assert.That(Begin(w).Status, Is.EqualTo(WorkerStatus.RequiresAid));
            Assert.That(w.StabilizeWorker(w.Epoch, Actor, 2, 100).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(Begin(w).Status, Is.EqualTo(WorkerStatus.TooEarly));
            w.AdvanceTo(1100); Begin(w); w.CompleteWorkerRecovery(w.Epoch, Actor, 1);
            Assert.That(w.GetWorker(Actor)!.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(w.GetWorker(Actor)!.Contamination, Is.EqualTo(40));
        }
        [Test] public void NoClearanceProviderCannotSilentlyStandWorker()
        {
            var w = World(); Hit(w, delay: 0); Begin(w);
            var reply = w.CompleteWorkerRecovery(w.Epoch, Actor, 1);
            Assert.That(reply.Status, Is.EqualTo(WorkerStatus.ClearanceUnavailable));
            Assert.That(reply.Changed, Is.True); Assert.That(reply.Worker!.Pose, Is.EqualTo(WorkerPose.Down));
        }
        [Test] public void StaleRecoveryCallbackNeverCallsClearancePolicy()
        {
            var policy = new Clearance(); var w = World(policy); Hit(w, delay: 0); Begin(w);
            Hit(w, WorkerImpact.Incapacitating, 2, 0);
            Assert.That(w.CompleteWorkerRecovery(w.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.StaleRecovery));
            Assert.That(policy.Calls, Is.Zero);
        }
        [Test] public void CancelRecoveryWorksWhilePausedAndOldBeginCannotRestartIt()
        {
            var w = World(); Hit(w, delay: 0); Begin(w); w.Pause(w.Epoch);
            Assert.That(w.CancelWorkerRecovery(w.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.Cancelled));
            Assert.That(w.GetWorker(Actor)!.Pose, Is.EqualTo(WorkerPose.Down)); w.Resume(w.Epoch);
            Assert.That(w.BeginWorkerRecovery(w.Epoch, Actor, 1, 1).Status, Is.EqualTo(WorkerStatus.RevisionConflict));
        }
        [Test] public void WorkerCooldownAndRecoveryWindowPauseWithShiftTime()
        {
            var w = World(); Hit(w); w.Pause(w.Epoch); w.AdvanceTo(10000);
            Assert.That(Begin(w).Status, Is.EqualTo(WorkerStatus.Paused));
            Assert.That(w.GetWorker(Actor)!.RecoveryNotBeforeMilliseconds, Is.EqualTo(100));
            w.Resume(w.Epoch); w.AdvanceTo(10100); Begin(w); w.Pause(w.Epoch); w.AdvanceTo(20000);
            Assert.That(w.GetWorker(Actor)!.Pose, Is.EqualTo(WorkerPose.Recovering));
            w.Resume(w.Epoch); var result = w.AdvanceTo(25000);
            Assert.That(result.WorkerChanges.Single().Status, Is.EqualTo(WorkerStatus.RecoveryExpired));
            Assert.That(w.GetWorker(Actor)!.Pose, Is.EqualTo(WorkerPose.Down));
        }
        [Test] public void RecoveryExpirationSurvivesDiscardedAdvisorySignals()
        {
            var w = World(); Hit(w, delay: 0); Begin(w);
            w.Schedule(w.Epoch, Actor, "optional-prompt", 10);
            w.CancelTimersForOwner(w.Epoch, Actor);
            Assert.That(w.AdvanceTo(5000).WorkerChanges.Single().Status, Is.EqualTo(WorkerStatus.RecoveryExpired));
            Assert.That(w.CompleteWorkerRecovery(w.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.StaleRecovery));
        }
        [Test] public void RestartRejectsAllOldWorkerOperationsAndRebindsClearance()
        {
            var old = World(new Clearance()); Hit(old, delay: 0); Begin(old);
            var next = old.Restart(new TestAccess()); Bind(next);
            Assert.That(next.ApplyWorkerImpact(old.Epoch, Actor, 1, WorkerImpact.Knockdown, 0).Status, Is.EqualTo(WorkerStatus.WrongEpoch));
            Assert.That(next.CompleteWorkerRecovery(old.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.WrongEpoch));
            Assert.That(old.WorkerCount, Is.Zero); Assert.That(next.GetWorker(Actor)!.CanInteract, Is.True);
            Hit(next, delay: 0); Begin(next);
            Assert.That(next.CompleteWorkerRecovery(next.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.ClearanceUnavailable));
        }
        [Test] public void DisconnectRemovesWorkerAndActorTimersWithoutTouchingPeers()
        {
            var w = World(); w.Schedule(w.Epoch, Actor, "warning", 100); w.Schedule(w.Epoch, Other, "warning", 100);
            w.Disconnect(w.Epoch, Connection);
            Assert.That(w.GetWorker(Actor), Is.Null); Assert.That(w.GetWorker(Other), Is.Not.Null);
            Assert.That(w.View.PendingTimerCount, Is.EqualTo(1));
            Assert.That(Hit(w).Status, Is.EqualTo(WorkerStatus.UnknownWorker));
        }
        [Test] public void WorkerSetupRosterReplacementDoesNotLeakState()
        {
            var w = new WorldSession(new WorldSessionConfiguration(0, 1000, maxConnections: 1), new TestAccess());
            for (int i = 1; i <= 50; i++)
            { w.RegisterConnection(Fixture.Id(100 + i), Actor); w.Disconnect(w.Epoch, Fixture.Id(100 + i)); Assert.That(w.WorkerCount, Is.Zero); }
            w.RegisterConnection(Connection, Actor); w.Start(); Assert.That(w.WorkerCount, Is.EqualTo(1));
        }
        [Test] public void InvalidWorkerRequestsLeaveSessionRevisionUnchanged()
        {
            var w = World(); long revision = w.View.Revision;
            Assert.That(w.ApplyWorkerImpact(w.Epoch, Fixture.Id(99), 1, WorkerImpact.Knockdown, 0).Status, Is.EqualTo(WorkerStatus.UnknownWorker));
            Assert.That(w.SetWorkerEnvironment(w.Epoch, Actor, 0, (WorkerSuit)99, 0).Status, Is.EqualTo(WorkerStatus.InvalidInput));
            Assert.That(w.BeginWorkerRecovery(w.Epoch, Actor, 0, 0).Status, Is.EqualTo(WorkerStatus.StaleRecovery));
            Assert.That(w.View.Revision, Is.EqualTo(revision));
        }
        [Test] public void ThrowingRecoveryPolicyFaultsAndClearsWorld()
        {
            var policy = new Clearance { Callback = () => throw new InvalidOperationException("Synthetic failure") };
            var w = World(policy); Hit(w, delay: 0); Begin(w);
            Assert.Throws<InvalidOperationException>(() => w.CompleteWorkerRecovery(w.Epoch, Actor, 1));
            Assert.That(w.View.Phase, Is.EqualTo(WorldPhase.Faulted)); Assert.That(w.WorkerCount, Is.Zero);
            Assert.That(w.View.RegisteredObjectCount, Is.Zero); Assert.That(w.Trace.Records.Last().Kind, Is.EqualTo(SessionTraceKind.Faulted));
        }
        [Test] public void ReentrantRecoveryPolicyCannotMutateOtherOwners()
        {
            var policy = new Clearance(); var w = World(policy); Hit(w, delay: 0); Begin(w);
            policy.Callback = () => w.ExecuteInteraction(Fixture.Id(21), Grab(w));
            Assert.Throws<InvalidOperationException>(() => w.CompleteWorkerRecovery(w.Epoch, Actor, 1));
            Assert.That(w.WorkerCount, Is.Zero); Assert.That(w.View.ActiveClaimCount, Is.Zero);
        }
        [Test] public void InvalidRecoveryPolicyOutcomeIsNotTreatedAsSafe()
        {
            var w = World(new Clearance { Result = (RecoveryClearance)99 }); Hit(w, delay: 0); Begin(w);
            Assert.Throws<InvalidOperationException>(() => w.CompleteWorkerRecovery(w.Epoch, Actor, 1));
            Assert.That(w.View.Outcome, Is.EqualTo(WorldOutcome.Faulted));
        }
        [Test] public void RepeatedWorkerLifetimesClearWorkersAndDiagnostics()
        {
            var w = World();
            for (int i = 0; i < 50; i++)
            {
                Hit(w, delay: 0); Begin(w); var old = w; w = w.Restart(new TestAccess()); Bind(w);
                Assert.That(old.WorkerCount, Is.Zero); Assert.That(old.View.PendingTimerCount, Is.Zero);
                Assert.That(w.GetWorker(Actor)!.Revision, Is.Zero); Assert.That(w.Trace.Records.Count, Is.EqualTo(1));
                Assert.That(w.Trace.DroppedRecords, Is.Zero);
            }
        }
        [Test] public void TraceRecordsTypedResultsAndImpactCausality()
        {
            var w = World(new Clearance()); w.ExecuteInteraction(Connection, Grab(w)); Hit(w, delay: 0); Begin(w);
            w.CompleteWorkerRecovery(w.Epoch, Actor, 1); var records = w.Trace.Records;
            var impact = records.Single(x => x.Kind == SessionTraceKind.Impact);
            var recovered = records.Single(x => x.Kind == SessionTraceKind.RecoveryResolved);
            Assert.That(impact.EntityId, Is.EqualTo(Box)); Assert.That(impact.WorkerResult, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(recovered.RelatedImpactSequence, Is.EqualTo(impact.RelatedImpactSequence));
            Assert.That(recovered.ActorId, Is.EqualTo(impact.ActorId)); Assert.That(recovered.Epoch, Is.EqualTo(impact.Epoch));
            Assert.That(recovered.WorldRevision, Is.GreaterThan(impact.WorldRevision));
        }
        [Test] public void TraceCapacityDropsOldestWithoutChangingGameplay()
        {
            var w = World(trace: 3);
            for (int i = 1; i <= 20; i++) w.AdvanceTo(i);
            var trace = w.Trace; Assert.That(trace.Records.Count, Is.EqualTo(3)); Assert.That(trace.DroppedRecords, Is.EqualTo(18));
            Assert.That(trace.Records.Select(x => x.Sequence), Is.EqualTo(new long[] { 19, 20, 21 }));
            Assert.That(w.View.ElapsedMilliseconds, Is.EqualTo(20));
            Assert.Throws<NotSupportedException>(() => ((IList<SessionTraceRecord>)trace.Records).Clear());
        }
        [Test] public void DiagnosticsCannotAdvanceWorldOrLoseDetachedEvidence()
        {
            var w = World(); Hit(w); var trace = w.Trace; var revision = w.View.Revision;
            _ = w.Trace; _ = w.Trace; Assert.That(w.View.Revision, Is.EqualTo(revision));
            w.Stop(); Assert.That(trace.Records.Last().Kind, Is.EqualTo(SessionTraceKind.Impact));
            Assert.That(w.Trace.Records.Last().Kind, Is.EqualTo(SessionTraceKind.Stopped));
        }
        [Test] public void TimeoutClearsWorkersAndCannotRecoverThem()
        {
            var w = World(); Hit(w); w.AdvanceTo(20000);
            Assert.That(w.WorkerCount, Is.Zero);
            Assert.That(w.CompleteWorkerRecovery(w.Epoch, Actor, 1).Status, Is.EqualTo(WorkerStatus.WorldEnded));
        }
        [Test] public void InvalidWorkerConfigurationFailsBeforeStarting()
        {
            var c = new WorldSessionConfiguration(1, 100);
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSession(c, new TestAccess(), traceCapacity: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSession(c, new TestAccess(), recoveryCompletionWindowMilliseconds: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorldSession(c, new TestAccess(), recoveryCompletionWindowMilliseconds: 60001));
        }
    }
}
