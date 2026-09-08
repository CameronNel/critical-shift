using System;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ClaimLifecycleTests
    {
        [Test, Category("HOLD-01")]
        public void ContentionHasOneLogicalWinner()
        {
            var f = new Fixture();
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Accepted, Is.True);
            Assert.That(f.World.Execute(f.C2, f.Grab(1, 1)).Status, Is.EqualTo(InteractionStatus.AlreadyClaimed));
            Assert.That(f.World.ActiveClaimCount, Is.EqualTo(1)); f.Holder(f.A);
        }

        [Test, Category("HOLD-02")]
        public void StaleReleaseAndBindingFailureCannotDropNewHolder()
        {
            var f = new Fixture();
            f.World.Execute(f.C1, f.Grab(1)); f.World.Execute(f.C1, f.Release(2));
            f.World.Execute(f.C2, f.Grab(1, 2));
            Assert.That(f.World.Execute(f.C1, f.Release(3, 1)).Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(f.World.ReportAttachmentFailure(f.Epoch, f.Box, 1).Status, Is.EqualTo(InteractionStatus.StaleLease));
            f.Holder(f.B);
        }

        [Test, Category("HOLD-02")]
        public void MatchingGenerationStillRequiresCorrectActor()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            Assert.That(f.World.Execute(f.C2, f.Release(1)).Status, Is.EqualTo(InteractionStatus.NotHolder));
            Assert.That(f.World.Execute(f.C2, f.Renew(2)).Status, Is.EqualTo(InteractionStatus.NotHolder));
            f.Holder(f.A);
        }

        [Test, Category("HOLD-03")]
        public void ExactExpiryBoundaryReleasesAndCannotBeRenewed()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            Assert.That(f.World.AdvanceTo(2999).Count, Is.Zero); f.Holder(f.A);
            Assert.That(f.World.AdvanceTo(3000).Count, Is.EqualTo(1)); f.Holder(null);
            Assert.That(f.World.Execute(f.C1, f.Renew(2)).Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(f.World.AdvanceTo(3000).Count, Is.Zero);
        }

        [Test, Category("HOLD-03")]
        public void RenewalExtendsDeadlineWithoutChangingLeaseGeneration()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1)); f.World.AdvanceTo(1000);
            var command = f.Renew(2); var renewal = f.World.Execute(f.C1, command);
            Assert.That(renewal.State!.ExpiresAtMilliseconds, Is.EqualTo(4000));
            Assert.That(renewal.State.LeaseGeneration, Is.EqualTo(1));
            f.World.AdvanceTo(2000);
            Assert.That(f.World.Execute(f.C1, command).HasNewCommit, Is.False);
            Assert.That(f.World.GetObject(f.Box)!.ExpiresAtMilliseconds, Is.EqualTo(4000));
            f.World.AdvanceTo(4000); f.Holder(null);
        }

        [Test]
        public void RenewalWithoutTimeChangeHasNoNewCommit()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            var reply = f.World.Execute(f.C1, f.Renew(2));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.NoChange));
            Assert.That(reply.IsTerminal, Is.True); Assert.That(reply.HasNewCommit, Is.False);
        }

        [Test, Category("HOLD-03")]
        public void DisconnectReleasesAndClearsOnlyItsReceipts()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            f.World.Execute(f.C2, f.Grab(1, box: f.Other));
            Assert.That(f.World.Disconnect(f.C1)!.HolderId, Is.Null);
            Assert.That(f.World.Disconnect(f.C1), Is.Null);
            Assert.That(f.World.RetainedReceiptCount(f.C1), Is.Zero);
            Assert.That(f.World.RetainedReceiptCount(f.C2), Is.EqualTo(1));
            Assert.That(f.World.Execute(f.C1, f.Grab(2, 2)).Status, Is.EqualTo(InteractionStatus.UnknownConnection));
            Assert.That(f.World.GetObject(f.Other)!.HolderId, Is.EqualTo(f.B));
        }

        [Test, Category("HOLD-03")]
        public void FailedAttachmentReleasesOnlyCurrentGeneration()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            Assert.That(f.World.ReportAttachmentFailure(f.Epoch, f.Box, 1).HasNewCommit, Is.True);
            Assert.That(f.World.ReportAttachmentFailure(f.Epoch, f.Box, 1).HasNewCommit, Is.False);
            f.Holder(null);
        }

        [Test]
        public void ReleaseRemainsAvailableWhenOutOfReach()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1)); f.Access.Decision = AccessDecision.OutOfReach;
            Assert.That(f.World.Execute(f.C1, f.Release(2)).Accepted, Is.True); f.Holder(null);
            Assert.That(f.Access.Calls, Is.EqualTo(1));
        }

        [Test]
        public void OneHandScopeRejectsSecondObjectWithoutChangingIt()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            Assert.That(f.World.Execute(f.C1, f.Grab(2, box: f.Other)).Status, Is.EqualTo(InteractionStatus.ActorAlreadyHolding));
            Assert.That(f.World.GetObject(f.Other)!.Revision, Is.Zero);
        }

        [Test]
        public void RevisionConflictDoesNotClaimObject()
        {
            var f = new Fixture();
            Assert.That(f.World.Execute(f.C1, f.Grab(1, 99)).Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(f.World.Execute(f.C1, f.Grab(2)).Accepted, Is.True);
        }

        [Test, Category("LIFE-02")]
        public void OldEpochCannotMutateNewWorldWithSameEntityIds()
        {
            var old = new Fixture(); old.World.Execute(old.C1, old.Grab(1)); old.World.Stop();
            var next = new Fixture(epoch: 2);
            Assert.That(next.World.Execute(next.C1, old.Grab(1)).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(next.World.ReportAttachmentFailure(old.Epoch, next.Box, 1).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(old.World.Execute(old.C1, old.Grab(2)).Status, Is.EqualTo(InteractionStatus.WorldStopped));
            Assert.That(next.World.Execute(next.C1, next.Grab(1)).Accepted, Is.True);
        }

        [Test, Category("LIFE-01"), Category("SHIFT-01")]
        public void TenIndependentLifetimesReturnOwnedCountsToZero()
        {
            for (int i = 1; i <= 10; i++)
            {
                var f = new Fixture(epoch: i);
                f.World.Execute(f.C1, f.Grab(1)); f.World.Stop(); f.World.Stop();
                Assert.That(f.World.RegisteredCount, Is.Zero);
                Assert.That(f.World.ActiveClaimCount, Is.Zero);
                Assert.That(f.World.RetainedReceiptCount(f.C1), Is.Zero);
                Assert.That(f.World.GetObject(f.Box), Is.Null);
            }
        }

        [Test]
        public void RetiredEntityCannotBeReclaimedOrReused()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1));
            Assert.That(f.World.RetireObject(f.Epoch, f.Box).HasNewCommit, Is.True);
            Assert.That(f.World.ActiveClaimCount, Is.Zero);
            Assert.That(f.World.Execute(f.C2, f.Grab(1, 2)).Status, Is.EqualTo(InteractionStatus.EntityRetired));
            var store = new ExclusiveClaimStore(1, 3000); store.Register(f.Box); store.Retire(f.Box);
            Assert.Throws<InvalidOperationException>(() => store.Register(f.Box));
        }

        [Test]
        public void SnapshotsRemainDetachedAfterLaterMutations()
        {
            var f = new Fixture(); var before = f.World.GetObject(f.Box)!;
            f.World.Execute(f.C1, f.Grab(1));
            Assert.That(before.HolderId, Is.Null); Assert.That(before.Revision, Is.Zero);
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.A));
        }

        [Test]
        public void BackwardsClockAndOverflowDoNotSilentlyCorruptClaims()
        {
            var f = new Fixture(); f.World.Execute(f.C1, f.Grab(1)); f.World.AdvanceTo(1000);
            Assert.Throws<ArgumentOutOfRangeException>(() => f.World.AdvanceTo(999)); f.Holder(f.A);
            var late = new Fixture(); late.World.AdvanceTo(long.MaxValue);
            Assert.Throws<OverflowException>(() => late.World.Execute(late.C1, late.Grab(1)));
            Assert.That(late.World.IsFaulted, Is.True); late.Holder(null);
        }

        [Test]
        public void SetupRejectsInvalidIdentitiesDuplicatesCapacityAndLateJoin()
        {
            var access = new TestAccess(); var epoch = Fixture.Id(1);
            Assert.Throws<ArgumentException>(() => new InteractionWorld(Guid.Empty, access));
            Assert.Throws<ArgumentNullException>(() => new InteractionWorld(epoch, null!));
            Assert.Throws<ArgumentOutOfRangeException>(() => new InteractionWorld(epoch, access, maxConnections: 5));
            Assert.Throws<ArgumentOutOfRangeException>(() => new InteractionWorld(epoch, access, receiptCapacity: 0));
            var world = new InteractionWorld(epoch, access, maxEntities: 1, maxConnections: 1);
            Assert.Throws<InvalidOperationException>(() => world.Start());
            Assert.Throws<ArgumentException>(() => world.RegisterConnection(Guid.Empty, Fixture.Id(10)));
            world.RegisterConnection(Fixture.Id(20), Fixture.Id(10));
            Assert.Throws<InvalidOperationException>(() => world.RegisterConnection(Fixture.Id(20), Fixture.Id(11)));
            Assert.Throws<InvalidOperationException>(() => world.RegisterConnection(Fixture.Id(21), Fixture.Id(10)));
            Assert.Throws<InvalidOperationException>(() => world.RegisterConnection(Fixture.Id(21), Fixture.Id(11)));
            Assert.Throws<ArgumentException>(() => world.RegisterObject(Guid.Empty));
            world.RegisterObject(Fixture.Id(30));
            Assert.Throws<InvalidOperationException>(() => world.RegisterObject(Fixture.Id(31)));
            Assert.That(world.Execute(Fixture.Id(20), new InteractionCommand(epoch, 1, InteractionKind.Grab, Fixture.Id(30))).Status,
                Is.EqualTo(InteractionStatus.NotReady));
            world.Start();
            Assert.Throws<InvalidOperationException>(() => world.RegisterConnection(Fixture.Id(21), Fixture.Id(11)));
            Assert.Throws<InvalidOperationException>(() => world.RegisterObject(Fixture.Id(31)));
        }
    }
}
