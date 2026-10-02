using System;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SharedCarryTests
    {
        private readonly Guid item = Guid.NewGuid(), primary = Guid.NewGuid(), helper = Guid.NewGuid(), other = Guid.NewGuid();
        private ExclusiveClaimStore Store(bool shared = true)
        { var store = new ExclusiveClaimStore(10, 1000); store.Register(item, shared); store.TryGrab(item, primary, 0); return store; }
        [Test]
        public void TaggedObjectAcceptsOneHelperUnderTheExistingLease()
        {
            var store = Store(); var before = store.Get(item)!;
            var result = store.TryAssist(item, helper, before.Revision, before.LeaseGeneration);
            Assert.That(result.Changed, Is.True); Assert.That(result.Snapshot!.HolderId, Is.EqualTo(primary));
            Assert.That(result.Snapshot.AssistantId, Is.EqualTo(helper)); Assert.That(result.Snapshot.LeaseGeneration, Is.EqualTo(before.LeaseGeneration));
            Assert.That(store.ActiveClaimCount, Is.EqualTo(2));
            Assert.That(store.TryAssist(item, other, result.Snapshot.Revision, result.Snapshot.LeaseGeneration).Error, Is.EqualTo(ClaimError.AlreadyClaimed));
        }
        [Test]
        public void UntaggedObjectRejectsAssistanceWithoutMutatingCustody()
        {
            var store = Store(false); var before = store.Get(item)!;
            Assert.That(store.TryAssist(item, helper, before.Revision, before.LeaseGeneration).Error, Is.EqualTo(ClaimError.AssistanceDisabled));
            Assert.That(store.Get(item), Is.SameAs(before));
        }
        [Test]
        public void HelperDisconnectPreservesPrimaryCustody()
        {
            var store = Store(); store.TryAssist(item, helper, 1, 1); store.ReleaseActor(helper);
            Assert.That(store.Get(item)!.HolderId, Is.EqualTo(primary)); Assert.That(store.Get(item)!.AssistantId, Is.Null);
            Assert.That(store.ActiveClaimCount, Is.EqualTo(1));
        }
        [Test]
        public void PrimaryReleaseAndExpiryFreeBothParticipants()
        {
            var store = Store(); store.TryAssist(item, helper, 1, 1); store.TryRelease(item, primary, 1);
            Assert.That(store.ActiveClaimCount, Is.Zero); Assert.That(store.Get(item)!.AssistantId, Is.Null);
            store.TryGrab(item, primary, store.Get(item)!.Revision);
            var held = store.Get(item)!; store.TryAssist(item, helper, held.Revision, held.LeaseGeneration);
            Assert.That(store.AdvanceTo(1000).Count, Is.EqualTo(1)); Assert.That(store.ActiveClaimCount, Is.Zero);
        }
        [Test]
        public void HelperRenewalCannotBecomePrimaryOrLoseTheHelper()
        {
            var store = Store(); store.TryAssist(item, helper, 1, 1); store.AdvanceTo(500); store.TryRenew(item, helper, 1);
            Assert.That(store.Get(item)!.HolderId, Is.EqualTo(primary)); Assert.That(store.Get(item)!.AssistantId, Is.EqualTo(helper));
            Assert.That(store.Get(item)!.ExpiresAtMilliseconds, Is.EqualTo(1500));
        }
        [Test]
        public void SharedCargoRequiresHelperReleaseBeforeMachineInsertion()
        {
            var store = Store(); var slot = Guid.NewGuid(); store.RegisterSlot(slot); store.TryAssist(item, helper, 1, 1);
            Assert.That(store.TryInsert(item, primary, 1, 2, slot).Error, Is.EqualTo(ClaimError.AlreadyClaimed));
            store.TryRelease(item, helper, 1);
            Assert.That(store.TryInsert(item, primary, 1, store.Get(item)!.Revision, slot).Changed, Is.True);
        }
        [Test]
        public void HelperCannotCarryAnotherObjectOrReleaseANewGeneration()
        {
            var store = Store(); store.Register(other); store.TryAssist(item, helper, 1, 1);
            Assert.That(store.TryGrab(other, helper, 0).Error, Is.EqualTo(ClaimError.ActorAlreadyHolding));
            store.TryRelease(item, primary, 1); store.TryGrab(item, primary, store.Get(item)!.Revision);
            Assert.That(store.TryRelease(item, helper, 1).Error, Is.EqualTo(ClaimError.StaleLease));
        }
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }
        [Test]
        public void AssistanceSharesTheCommandReceiptAndImpactCleanup()
        {
            var world = new WorldSession(new WorldSessionConfiguration(1, 10000), new Access());
            world.RegisterConnection(primary, primary); world.RegisterConnection(helper, helper); world.RegisterObject(item, true); world.Start();
            world.ExecuteInteraction(primary, new InteractionCommand(world.Epoch, 1, InteractionKind.Grab, item));
            var command = new InteractionCommand(world.Epoch, 1, InteractionKind.Assist, item, 1, 1);
            Assert.That(world.ExecuteInteraction(helper, command).HasNewCommit, Is.True);
            Assert.That(world.ExecuteInteraction(helper, command).HasNewCommit, Is.False);
            world.ApplyWorkerImpact(world.Epoch, helper, 1, WorkerImpact.Knockdown, 1000, Guid.NewGuid(), Guid.NewGuid());
            Assert.That(world.GetObject(item)!.HolderId, Is.EqualTo(primary)); Assert.That(world.GetObject(item)!.AssistantId, Is.Null);
        }
        [Test]
        public void HelperAttachmentReleaseIsFencedByReceiptAndGeneration()
        {
            var world = new WorldSession(new WorldSessionConfiguration(1, 10000), new Access());
            world.RegisterConnection(primary, primary); world.RegisterConnection(helper, helper); world.RegisterObject(item, true); world.Start();
            world.ExecuteInteraction(primary, new InteractionCommand(world.Epoch, 1, InteractionKind.Grab, item));
            world.ExecuteInteraction(helper, new InteractionCommand(world.Epoch, 1, InteractionKind.Assist, item, 1, 1));
            var release = new InteractionCommand(world.Epoch, 2, InteractionKind.Release, item, 0, 1);
            Assert.That(world.ExecuteInteraction(helper, release).HasNewCommit, Is.True);
            var claim = world.GetObject(item)!;
            Assert.That(claim.HolderId, Is.EqualTo(primary)); Assert.That(claim.AssistantId, Is.Null);
            Assert.That(claim.LeaseGeneration, Is.EqualTo(1));
            world.ExecuteInteraction(helper, new InteractionCommand(world.Epoch, 3, InteractionKind.Assist, item, claim.Revision, 1));
            Assert.That(world.ExecuteInteraction(helper, release).HasNewCommit, Is.False);
            Assert.That(world.GetObject(item)!.AssistantId, Is.EqualTo(helper));
            world.ExecuteInteraction(primary, new InteractionCommand(world.Epoch, 2, InteractionKind.Release, item, 0, 1));
            claim = world.GetObject(item)!;
            world.ExecuteInteraction(primary, new InteractionCommand(world.Epoch, 3, InteractionKind.Grab, item, claim.Revision));
            var stale = world.ExecuteInteraction(helper, new InteractionCommand(world.Epoch, 4, InteractionKind.Release, item, 0, 1));
            Assert.That(stale.Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(world.GetObject(item)!.HolderId, Is.EqualTo(primary));
        }
    }
}
