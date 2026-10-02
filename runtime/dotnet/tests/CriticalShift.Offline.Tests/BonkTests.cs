using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class BonkTests
    {
        private static Guid A => Fixture.Id(10);
        private static Guid B => Fixture.Id(11);
        private static Guid C1 => Fixture.Id(20);
        private static Guid C2 => Fixture.Id(21);
        private static Guid Tool => Fixture.Id(30);
        private static Guid Cargo => Fixture.Id(31);
        private static WorldSession World(TestAccess? access = null)
        {
            var world = new WorldSession(new WorldSessionConfiguration(7, 30000, true), access ?? new TestAccess());
            world.RegisterConnection(C1, A); world.RegisterConnection(C2, B);
            world.RegisterObject(Tool, allowBonk: true); world.RegisterObject(Cargo); world.Start();
            world.ExecuteInteraction(C1, new InteractionCommand(world.Epoch, 1, InteractionKind.Grab, Tool)); return world;
        }
        private static InteractionCommand Intent(WorldSession w, long sequence = 2, long lease = 1) =>
            new InteractionCommand(w.Epoch, sequence, InteractionKind.Bonk, Tool, leaseGeneration: lease);
        [Test] public void BonkReceiptsReplayWithoutAnotherSwingOrCause()
        {
            var w = World(); var first = w.ExecuteInteraction(C1, Intent(w)); var replay = w.ExecuteInteraction(C1, Intent(w));
            Assert.That(first.HasNewCommit, Is.True); Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(replay.Bonk!.Sequence, Is.EqualTo(first.Bonk!.Sequence)); Assert.That(replay.Bonk.Cause, Is.EqualTo(first.Bonk.Cause));
            Assert.That(w.GetWorkerBonk(A)!.Sequence, Is.EqualTo(1));
        }
        [Test] public void BonkKnocksDownOtherPlayerAndReleasesTheirCargoOnce()
        {
            var w = World(); w.ExecuteInteraction(C2, new InteractionCommand(w.Epoch, 1, InteractionKind.Grab, Cargo));
            w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180); var hit = w.ApplyWorkerBonkContact(w.Epoch, A, 1, B);
            Assert.That(hit.Changed, Is.True); Assert.That(hit.Worker!.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(hit.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert)); Assert.That(hit.Worker.RecoveryNotBeforeMilliseconds, Is.EqualTo(2180));
            Assert.That(hit.Worker.LastHazardId, Is.EqualTo(Tool)); Assert.That(hit.Worker.LastCauseId, Is.EqualTo(w.GetWorkerBonk(A)!.Cause));
            Assert.That(hit.ReleasedClaim!.EntityId, Is.EqualTo(Cargo)); Assert.That(w.GetObject(Cargo)!.HolderId, Is.Null);
            long revision = hit.Worker.Revision;
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False); Assert.That(w.GetWorker(B)!.Revision, Is.EqualTo(revision));
        }
        [TestCase(0)] [TestCase(179)] [TestCase(321)] [TestCase(701)]
        public void ContactsOutsideStrikeWindowCannotDamage(long time)
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(time);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False); Assert.That(w.GetWorker(B)!.Pose, Is.EqualTo(WorkerPose.Upright));
        }
        [Test] public void SwingCooldownConsumesRejectionReceiptWithoutWedgingInput()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w));
            Assert.That(w.ExecuteInteraction(C1, Intent(w, 3)).Status, Is.EqualTo(InteractionStatus.AttackCoolingDown));
            w.AdvanceTo(950); Assert.That(w.ExecuteInteraction(C1, Intent(w, 4)).Bonk!.Sequence, Is.EqualTo(2));
        }
        [Test] public void SelfUnknownAndStaleSwingCannotDamageOrConsumeCurrentHit()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, A).Changed, Is.False);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, Fixture.Id(90)).Changed, Is.False);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 99, B).Changed, Is.False);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.True);
        }
        [Test] public void WallContactConsumesStrikeWithoutWorkerDamage()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180);
            Assert.That(w.BlockWorkerBonk(w.Epoch, A, 1), Is.True); Assert.That(w.BlockWorkerBonk(w.Epoch, A, 1), Is.False);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False);
        }
        [Test] public void ReleaseReacquireCannotReuseOldSwingLease()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.ExecuteInteraction(C1, new InteractionCommand(w.Epoch, 3, InteractionKind.Release, Tool, leaseGeneration: 1));
            var state = w.GetObject(Tool)!; w.ExecuteInteraction(C1, new InteractionCommand(w.Epoch, 4, InteractionKind.Grab, Tool, state.Revision)); w.AdvanceTo(180);
            Assert.That(w.GetWorkerBonk(A), Is.Null); Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False);
        }
        [Test] public void AttackerImpactCancelDisconnectAndExpiryPreventHits()
        {
            foreach (string stop in new[] { "impact", "cancel", "disconnect", "expiry" })
            {
                var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180);
                if (stop == "impact") w.ApplyWorkerImpact(w.Epoch, A, 1, WorkerImpact.Knockdown, 2000);
                if (stop == "cancel") Assert.That(w.CancelWorkerBonk(w.Epoch, A, 1), Is.True);
                if (stop == "disconnect") w.Disconnect(w.Epoch, C1);
                if (stop == "expiry") w.AdvanceTo(3000);
                Assert.That(w.GetWorkerBonk(A), Is.Null, stop); Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False, stop);
            }
        }
        [Test] public void OnlyRegisteredHeldShovelAndCurrentLeaseCanStart()
        {
            var w = World(); Assert.That(w.ExecuteInteraction(C2, Intent(w, 1)).Status, Is.EqualTo(InteractionStatus.NotHolder));
            Assert.That(w.ExecuteInteraction(C1, Intent(w, lease: 2)).Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(w.ExecuteInteraction(C1, new InteractionCommand(w.Epoch, 3, InteractionKind.Bonk, Cargo, leaseGeneration: 1)).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(w.GetWorkerBonk(A), Is.Null);
        }
        [Test] public void PausedAndWrongEpochBonksCannotChangeHealth()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180); w.Pause(w.Epoch);
            Assert.That(w.GetWorkerBonk(A), Is.Null);
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Status, Is.EqualTo(WorkerStatus.Paused));
            Assert.That(w.ExecuteInteraction(C1, Intent(w, 3)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            w.Resume(w.Epoch); Assert.That(w.ApplyWorkerBonkContact(Guid.NewGuid(), A, 1, B).Status, Is.EqualTo(WorkerStatus.WrongEpoch));
            Assert.That(w.ApplyWorkerBonkContact(w.Epoch, A, 1, B).Changed, Is.False);
            Assert.That(w.GetWorker(B)!.Pose, Is.EqualTo(WorkerPose.Upright));
        }
        [Test] public void RepeatedValidSwingsUseOrderedHazardObservationsAndNeverHeal()
        {
            var w = World(); w.ExecuteInteraction(C1, Intent(w)); w.AdvanceTo(180); w.ApplyWorkerBonkContact(w.Epoch, A, 1, B);
            w.ApplyWorkerImpact(w.Epoch, B, 1, WorkerImpact.Incapacitating, 0); w.AdvanceTo(950); w.ExecuteInteraction(C1, Intent(w, 3)); w.AdvanceTo(1130);
            var hit = w.ApplyWorkerBonkContact(w.Epoch, A, 2, B);
            Assert.That(hit.Changed, Is.True); Assert.That(hit.Worker!.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            Assert.That(hit.Worker.LastHazardId, Is.EqualTo(Tool));
        }
    }
}
