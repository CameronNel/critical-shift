using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class CommandTests
    {
        [Test, Category("CMD-02")]
        public void MatchingRetryIsHistoricalWithoutSecondCommit()
        {
            var f = new Fixture();
            var command = f.Grab(1);
            var first = f.World.Execute(f.C1, command);
            var retry = f.World.Execute(f.C1, command);
            Assert.That(first.HasNewCommit, Is.True);
            Assert.That(retry.Accepted, Is.True);
            Assert.That(retry.IsReplay, Is.True);
            Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(f.Access.Calls, Is.EqualTo(1));
            Assert.That(f.World.GetObject(f.Box)!.Revision, Is.EqualTo(1));
        }

        [Test, Category("CMD-02")]
        public void RetryAfterReleaseDoesNotReacquireOrReattach()
        {
            var f = new Fixture();
            f.World.Execute(f.C1, f.Grab(1));
            f.World.Execute(f.C1, f.Release(2));
            var reply = f.World.Execute(f.C1, f.Grab(1));
            Assert.That(reply.Accepted && reply.IsReplay, Is.True);
            Assert.That(reply.HasNewCommit, Is.False);
            Assert.That(reply.State!.Revision, Is.LessThan(f.World.GetObject(f.Box)!.Revision));
            f.Holder(null);
        }

        [Test, Category("CMD-02")]
        public void ChangedPayloadCannotReuseRetainedSequence()
        {
            var f = new Fixture();
            f.World.Execute(f.C1, f.Grab(1));
            var changed = f.World.Execute(f.C1, f.Grab(1, box: f.Other));
            Assert.That(changed.Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            Assert.That(changed.IsTerminal, Is.False);
            Assert.That(f.World.GetObject(f.Other)!.HolderId, Is.Null);
            f.Holder(f.A);
        }

        [Test, Category("CMD-03")]
        public void EvictedReceiptNeverExecutesAgain()
        {
            var f = new Fixture(receipts: 2);
            f.World.Execute(f.C1, f.Grab(1));
            f.World.Execute(f.C1, f.Release(2));
            f.World.Execute(f.C1, f.Grab(3, 2));
            var old = f.World.Execute(f.C1, f.Grab(1));
            Assert.That(old.Status, Is.EqualTo(InteractionStatus.TooOld));
            Assert.That(f.World.LastSequence(f.C1), Is.EqualTo(3));
            Assert.That(f.World.RetainedReceiptCount(f.C1), Is.EqualTo(2));
            Assert.That(f.World.GetObject(f.Box)!.LeaseGeneration, Is.EqualTo(2));
        }

        [Test, Category("CMD-03")]
        public void SequenceGapDoesNotConsumeTheMissingSequence()
        {
            var f = new Fixture();
            Assert.That(f.World.Execute(f.C1, f.Grab(2)).Status, Is.EqualTo(InteractionStatus.SequenceGap));
            Assert.That(f.World.LastSequence(f.C1), Is.Zero);
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Accepted, Is.True);
        }

        [Test, Category("CMD-03")]
        public void MaximumSequenceIsRejectedWithoutArithmeticOverflow()
        {
            var f = new Fixture();
            Assert.That(f.World.Execute(f.C1, f.Grab(long.MaxValue)).Status, Is.EqualTo(InteractionStatus.SequenceGap));
            Assert.That(f.World.IsFaulted, Is.False);
        }

        [Test, Category("CMD-04")]
        public void GameplayRejectionAdvancesStreamAndIsReplayable()
        {
            var f = new Fixture();
            f.Access.Decision = AccessDecision.OutOfReach;
            var bad = f.World.Execute(f.C1, f.Grab(1));
            Assert.That(bad.Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(bad.IsTerminal, Is.True);
            f.Access.Decision = AccessDecision.Allowed;
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            f.Holder(null);
            Assert.That(f.World.Execute(f.C1, f.Grab(2)).HasNewCommit, Is.True);
        }

        [Test, Category("CMD-04")]
        public void UnknownTargetIsTerminalButDoesNotMutateOtherObjects()
        {
            var f = new Fixture();
            var reply = f.World.Execute(f.C1, f.Grab(1, box: Fixture.Id(999)));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.UnknownEntity));
            Assert.That(reply.IsTerminal, Is.True);
            Assert.That(f.World.Execute(f.C1, f.Grab(2)).Accepted, Is.True);
        }

        [Test, Category("CMD-01")]
        public void WrongEpochAndUnknownConnectionCannotAdvanceStream()
        {
            var f = new Fixture();
            var wrong = new InteractionCommand(Fixture.Id(999), 1, InteractionKind.Grab, f.Box);
            Assert.That(f.World.Execute(f.C1, wrong).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(f.World.Execute(Fixture.Id(999), f.Grab(1)).Status, Is.EqualTo(InteractionStatus.UnknownConnection));
            Assert.That(f.World.LastSequence(f.C1), Is.Zero);
            f.Holder(null);
        }

        [Test, Category("CMD-01")]
        public void ActorComesFromTrustedConnectionNotPayload()
        {
            var f = new Fixture();
            Assert.That(typeof(InteractionCommand).GetProperty("ActorId"), Is.Null);
            Assert.That(f.World.Execute(f.C2, f.Grab(1)).Accepted, Is.True);
            Assert.That(f.Access.LastActor, Is.EqualTo(f.B));
            f.Holder(f.B);
        }

        [TestCase(0L, InteractionKind.Grab, 0L, 0L)]
        [TestCase(-1L, InteractionKind.Grab, 0L, 0L)]
        [TestCase(1L, (InteractionKind)77, 0L, 0L)]
        [TestCase(1L, InteractionKind.Grab, -1L, 0L)]
        [TestCase(1L, InteractionKind.Grab, 0L, 1L)]
        [TestCase(1L, InteractionKind.Release, 0L, 0L)]
        [TestCase(1L, InteractionKind.Renew, 0L, -1L)]
        [TestCase(1L, InteractionKind.Release, 1L, 1L)]
        [Category("CMD-01")]
        public void MalformedCommandsDoNotConsumeSequence(long sequence, InteractionKind kind, long revision, long lease)
        {
            var f = new Fixture();
            var bad = new InteractionCommand(f.Epoch, sequence, kind, f.Box, revision, lease);
            Assert.That(f.World.Execute(f.C1, bad).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            Assert.That(f.World.LastSequence(f.C1), Is.Zero);
            Assert.That(f.Access.Calls, Is.Zero);
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Accepted, Is.True);
        }

        [Test, Category("CMD-01")]
        public void EmptyTargetAndNullCommandFailWithoutMutation()
        {
            var f = new Fixture();
            var bad = new InteractionCommand(f.Epoch, 1, InteractionKind.Grab, Guid.Empty);
            Assert.That(f.World.Execute(f.C1, bad).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            Assert.Throws<ArgumentNullException>(() => f.World.Execute(f.C1, null!));
            Assert.That(f.World.ActiveClaimCount, Is.Zero);
        }

        [Test, Category("CMD-04")]
        public void ConnectionsHaveIndependentSequences()
        {
            var f = new Fixture();
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Accepted, Is.True);
            Assert.That(f.World.Execute(f.C2, f.Grab(1, box: f.Other)).Accepted, Is.True);
            Assert.That(f.World.LastSequence(f.C1), Is.EqualTo(1));
            Assert.That(f.World.LastSequence(f.C2), Is.EqualTo(1));
        }

        [TestCase(AccessDecision.ActorUnavailable, InteractionStatus.ActorUnavailable)]
        [TestCase(AccessDecision.TargetUnavailable, InteractionStatus.TargetUnavailable)]
        public void HostPolicyDenialIsSideEffectFree(AccessDecision decision, InteractionStatus status)
        {
            var f = new Fixture(); f.Access.Decision = decision;
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Status, Is.EqualTo(status));
            Assert.That(f.World.GetObject(f.Box)!.Revision, Is.Zero);
        }

        [Test, Category("CI-02")]
        public void UnexpectedPolicyFailureFaultsWorldAndCannotBeRetried()
        {
            var f = new Fixture();
            f.Access.Callback = () => throw new InvalidOperationException("Injected observer failure.");
            Assert.Throws<InvalidOperationException>(() => f.World.Execute(f.C1, f.Grab(1)));
            Assert.That(f.World.IsFaulted, Is.True);
            f.Access.Callback = null;
            Assert.That(f.World.Execute(f.C1, f.Grab(1)).Status, Is.EqualTo(InteractionStatus.WorldFaulted));
            f.Holder(null);
            f.World.Stop();
            Assert.That(f.World.RegisteredCount, Is.Zero);
        }

        [Test]
        public void ReentrantMutationIsRejectedAndFaultReported()
        {
            var f = new Fixture();
            f.Access.Callback = () => f.World.Disconnect(f.C1);
            Assert.Throws<InvalidOperationException>(() => f.World.Execute(f.C1, f.Grab(1)));
            Assert.That(f.World.IsFaulted, Is.True);
            f.Holder(null);
        }
    }
}
