using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class DownedGripTests
    {
        private static Guid Actor => Fixture.Id(10);
        private static Guid Connection => Fixture.Id(20);
        private static Guid Handle => Fixture.Id(30);
        private static Guid Cargo => Fixture.Id(31);
        private static WorldSession World(TestAccess? access = null)
        {
            var w = new WorldSession(new WorldSessionConfiguration(7, 20000, true), access ?? new TestAccess());
            w.RegisterConnection(Connection, Actor); w.RegisterConnection(Fixture.Id(21), Fixture.Id(11));
            w.RegisterObject(Handle, allowDownedGrip: true); w.RegisterObject(Cargo); w.Start(); return w;
        }
        private static WorkerReply Hit(WorldSession w, long sequence = 1, WorkerImpact severity = WorkerImpact.Knockdown, long delay = 0) =>
            w.ApplyWorkerImpact(w.Epoch, Actor, sequence, severity, delay);
        private static InteractionReply Grip(WorldSession w, long sequence = 1, Guid? target = null, long revision = 0) =>
            w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, sequence, InteractionKind.GripHandle, target ?? Handle, revision));
        private static WorkerReply Begin(WorldSession w)
        { var state = w.GetWorker(Actor)!; return w.BeginWorkerRecovery(w.Epoch, Actor, state.RecoveryEpisode, state.Revision); }

        [Test] public void ConsciousDownGripsOnlyTaggedHandleThroughExistingClaim()
        {
            var w = World(); Hit(w);
            Assert.That(Grip(w).HasNewCommit, Is.True);
            Assert.That(w.GetObject(Handle)!.HolderId, Is.EqualTo(Actor));
            Assert.That(w.GetWorker(Actor)!.CanInteract, Is.False);
            Assert.That(w.View.ActiveClaimCount, Is.EqualTo(1));
        }
        [TestCase(WorkerImpact.Knockdown)] [TestCase(WorkerImpact.Incapacitating)]
        public void UprightUnconsciousRecoveringAndPausedCannotGrip(WorkerImpact severity)
        {
            var w = World(); Assert.That(Grip(w).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Hit(w, severity: severity);
            if (severity == WorkerImpact.Incapacitating)
            { Assert.That(Grip(w, 2).Status, Is.EqualTo(InteractionStatus.ActorUnavailable)); return; }
            w.Pause(w.Epoch); Assert.That(Grip(w, 2).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            w.Resume(w.Epoch); Assert.That(Begin(w).Changed, Is.True);
            Assert.That(Grip(w, 3).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
        }
        [Test] public void UntaggedCargoAndNormalGrabCannotBypassDownedGate()
        {
            var w = World(); Hit(w);
            Assert.That(Grip(w, target: Cargo).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 2, InteractionKind.Grab, Handle)).Accepted, Is.False);
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 3, InteractionKind.Grab, Cargo)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(w.View.ActiveClaimCount, Is.Zero);
        }
        [Test] public void GripStillRequiresPhysicalAccessAndCurrentObjectRevision()
        {
            var access = new TestAccess { Decision = AccessDecision.OutOfReach }; var w = World(access); Hit(w);
            Assert.That(Grip(w).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            access.Decision = AccessDecision.Allowed;
            Assert.That(Grip(w, 2, revision: 1).Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(Grip(w, 3).HasNewCommit, Is.True);
        }
        [Test] public void GripReplayMalformedPayloadAndContentionUseExistingReceiptStream()
        {
            var w = World(); Hit(w); var applied = Grip(w);
            Assert.That(Grip(w).HasNewCommit, Is.False);
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 2, InteractionKind.GripHandle, Handle, leaseGeneration: 1)).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            w.ApplyWorkerImpact(w.Epoch, Fixture.Id(11), 1, WorkerImpact.Knockdown, 0);
            Assert.That(w.ExecuteInteraction(Fixture.Id(21), new InteractionCommand(w.Epoch, 1, InteractionKind.GripHandle, Handle, applied.State!.Revision)).Status, Is.EqualTo(InteractionStatus.AlreadyClaimed));
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 2, InteractionKind.Release, Handle, leaseGeneration: applied.State.LeaseGeneration)).HasNewCommit, Is.True);
        }
        [Test] public void DownedLeaseRenewalAndStaleReleasePreserveGeneration()
        {
            var w = World(); Hit(w); long lease = Grip(w).State!.LeaseGeneration;
            w.AdvanceTo(1000);
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 2, InteractionKind.Renew, Handle, leaseGeneration: lease)).HasNewCommit, Is.True);
            Assert.That(w.ExecuteInteraction(Connection, new InteractionCommand(w.Epoch, 3, InteractionKind.Release, Handle, leaseGeneration: lease + 1)).Accepted, Is.False);
            Assert.That(w.GetObject(Handle)!.HolderId, Is.EqualTo(Actor));
            w.AdvanceTo(1000 + w.Configuration.LeaseMilliseconds);
            Assert.That(w.GetObject(Handle)!.HolderId, Is.Null);
        }
        [Test] public void AcceptedNewImpactReleasesGripButDuplicatePreservesReplacement()
        {
            var w = World(); Hit(w); Grip(w); var hit = Hit(w, 2);
            Assert.That(hit.ReleasedClaim!.EntityId, Is.EqualTo(Handle));
            var state = w.GetObject(Handle)!; Grip(w, 2, revision: state.Revision);
            Assert.That(Hit(w, 2).Status, Is.EqualTo(WorkerStatus.Duplicate));
            Assert.That(w.GetObject(Handle)!.HolderId, Is.EqualTo(Actor));
        }
        [Test] public void RecoveryBeginReleasesGripOnlyAfterAcceptedTransition()
        {
            var w = World(); Hit(w, delay: 1000); Grip(w);
            Assert.That(Begin(w).Status, Is.EqualTo(WorkerStatus.TooEarly)); Assert.That(w.GetObject(Handle)!.HolderId, Is.EqualTo(Actor));
            w.AdvanceTo(1000); var begin = Begin(w);
            Assert.That(begin.Changed, Is.True); Assert.That(begin.ReleasedClaim!.EntityId, Is.EqualTo(Handle));
            Assert.That(w.GetObject(Handle)!.HolderId, Is.Null);
        }
        [Test] public void DisconnectAndStopClearDownedGripCustody()
        {
            var w = World(); Hit(w); Grip(w); w.Disconnect(w.Epoch, Connection);
            Assert.That(w.GetObject(Handle)!.HolderId, Is.Null);
            var other = World(); Hit(other); Grip(other); other.Stop(); Assert.That(other.View.ActiveClaimCount, Is.Zero);
        }
        [Test] public void FixedHandlesRejectSharedCargoCapabilityAndLateRegistration()
        {
            var w = new WorldSession(new WorldSessionConfiguration(1, 10000), new TestAccess());
            Assert.Throws<ArgumentException>(() => w.RegisterObject(Handle, true, true));
            Assert.That(w.GetObject(Handle), Is.Null);
            w.RegisterConnection(Connection, Actor); w.Start();
            Assert.Throws<InvalidOperationException>(() => w.RegisterObject(Handle, allowDownedGrip: true));
        }
    }
}
