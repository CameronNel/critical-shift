using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class PlayerSliceTests
    {
        private sealed class Policy : IPlayerActionPolicy
        {
            internal PlayerAccess Decision = PlayerAccess.Allowed;
            internal Action? Callback;
            public PlayerAccess Evaluate(Guid epoch, Guid actor, Guid target, PlayerRequest request)
            { Callback?.Invoke(); return Decision; }
        }
        private sealed class Scene
        {
            internal readonly Guid A = Fixture.Id(1), B = Fixture.Id(2), C1 = Fixture.Id(3), C2 = Fixture.Id(4);
            internal readonly Guid Seat = Fixture.Id(5), Suit = Fixture.Id(6), Box = Fixture.Id(7), Place = Fixture.Id(8);
            internal readonly Policy Access = new Policy();
            internal readonly WorldSession World;
            internal long Sequence;
            internal Scene(bool start = true, long stationDelay = 0, long lease = 3000)
            {
                World = new WorldSession(new WorldSessionConfiguration(1, 60000, true, leaseMilliseconds: lease), new TestAccess(), playerActions: Access);
                World.RegisterConnection(C1, A); World.RegisterConnection(C2, B);
                World.Players.RegisterActor(A, Fixture.Id(11)); World.Players.RegisterActor(B, Fixture.Id(12));
                World.Players.RegisterTarget(Seat, PlayerTargetKind.Seat);
                World.Players.RegisterTarget(Suit, PlayerTargetKind.ProtectiveEquipment, stationPreparationMilliseconds: stationDelay);
                World.Players.RegisterTarget(Box, PlayerTargetKind.Carryable);
                World.Players.RegisterTarget(Place, PlayerTargetKind.Placement, Fixture.Id(13));
                if (start) World.Start();
            }
            internal InteractionCommand Command(PlayerAction action, Guid target, long sequence, Guid? actor = null, Guid item = default)
            {
                var state = World.GetObject(item == Guid.Empty ? target : item)!;
                return new InteractionCommand(World.Epoch, sequence, InteractionKind.Player, target,
                    player: new PlayerRequest(action, state.Revision, World.GetWorker(actor ?? A)!.Revision,
                        action == PlayerAction.Drop || action == PlayerAction.Stand || action == PlayerAction.Equip || action == PlayerAction.Place ? state.LeaseGeneration : 0, item));
            }
            internal InteractionReply Do(PlayerAction action, Guid target, Guid item = default) =>
                World.ExecuteInteraction(C1, Command(action, target, ++Sequence, item: item));
        }

        [Test] public void PlayerCommandsShareReceiptsAndRejectChangedRetries()
        {
            var s = new Scene(); var command = s.Command(PlayerAction.Sit, s.Seat, 1);
            Assert.That(s.World.ExecuteInteraction(s.C1, command).HasNewCommit, Is.True);
            long revision = s.World.GetWorker(s.A)!.Revision;
            Assert.That(s.World.ExecuteInteraction(s.C1, command).IsReplay, Is.True);
            Assert.That(s.World.GetWorker(s.A)!.Revision, Is.EqualTo(revision));
            var changed = new InteractionCommand(s.World.Epoch, 1, InteractionKind.Player, s.Seat,
                player: new PlayerRequest(PlayerAction.Stand, 1, revision, 1));
            Assert.That(s.World.ExecuteInteraction(s.C1, changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
        }
        [Test] public void StationPreparationClaimsOnceAndCannotEquipEarly()
        {
            var s = new Scene(stationDelay: 15000, lease: 30000);
            var command = s.Command(PlayerAction.PrepareEquipment, s.Suit, 1);
            Assert.That(s.World.ExecuteInteraction(s.C1, command).HasNewCommit, Is.True); s.Sequence = 1;
            Assert.That(s.World.ExecuteInteraction(s.C1, command).IsReplay, Is.True);
            Assert.That(s.World.Players.GetPreparation(s.A)!.DueShiftMilliseconds, Is.EqualTo(15000));
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(s.World.Players.GetEquipment(s.A), Is.Null);
            s.World.AdvanceTo(15000);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).HasNewCommit, Is.True);
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(s.World.Players.GetPreparation(s.A), Is.Null);
            Assert.That(s.World.Players.GetHeld(s.A), Is.Null);
        }
        [Test] public void StationPreparationPausesWithShiftAndRequiresLiveClaim()
        {
            var s = new Scene(stationDelay: 15000, lease: 30000);
            s.Do(PlayerAction.PrepareEquipment, s.Suit); s.World.AdvanceTo(1000); s.World.Pause(s.World.Epoch);
            s.World.AdvanceTo(16000); s.World.Resume(s.World.Epoch);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            s.World.AdvanceTo(29999);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            // At host time 30000 the unrenewed lease expires, although 15 seconds of shift time also elapsed.
            s.World.AdvanceTo(30000);
            Assert.That(s.World.Players.GetPreparation(s.A), Is.Null);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Accepted, Is.False);
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.None));
        }
        [Test] public void StationPreparationHasOneWinnerAndBlocksBypasses()
        {
            var s = new Scene(stationDelay: 15000, lease: 30000);
            Assert.That(s.Do(PlayerAction.PickUp, s.Suit).Accepted, Is.False);
            Assert.That(s.Do(PlayerAction.PrepareEquipment, s.Suit).Accepted, Is.True);
            Assert.That(s.World.ExecuteInteraction(s.C2, s.Command(PlayerAction.PrepareEquipment, s.Suit, 1, s.B)).Status,
                Is.EqualTo(InteractionStatus.AlreadyClaimed));
            Assert.That(s.World.Players.GetPreparation(s.B), Is.Null);
            Assert.That(s.Do(PlayerAction.Sit, s.Seat).Accepted, Is.False);
            Assert.That(s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, ++s.Sequence, InteractionKind.Release,
                s.Suit, leaseGeneration: s.World.GetObject(s.Suit)!.LeaseGeneration)).Accepted, Is.False);
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.EqualTo(s.A));
        }
        [Test] public void CancelledStationPreparationCannotUseAnOldDeadline()
        {
            var s = new Scene(stationDelay: 15000, lease: 30000);
            s.Do(PlayerAction.PrepareEquipment, s.Suit);
            var cancelled = s.World.Players.GetPreparation(s.A)!;
            Assert.That(s.Do(PlayerAction.Drop, s.Suit).Accepted, Is.True);
            s.World.AdvanceTo(1000); s.Do(PlayerAction.PrepareEquipment, s.Suit);
            Assert.That(s.World.Players.GetPreparation(s.A)!.LeaseGeneration, Is.GreaterThan(cancelled.LeaseGeneration));
            s.World.AdvanceTo(15000);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Accepted, Is.False);
            s.World.AdvanceTo(16000);
            Assert.That(s.Do(PlayerAction.Equip, s.Suit).Accepted, Is.True);
        }
        [Test] public void StationSuitCannotMoveToAPlacementSlot()
        {
            var s = new Scene(stationDelay: 15000, lease: 30000);
            s.Do(PlayerAction.PrepareEquipment, s.Suit); s.World.AdvanceTo(15000); s.Do(PlayerAction.Equip, s.Suit);
            Assert.That(s.Do(PlayerAction.Unequip, s.Suit).Accepted, Is.True);
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.Null);
            Assert.That(s.World.GetObject(s.Suit)!.SlotId, Is.Null);
            Assert.That(s.Do(PlayerAction.PickUp, s.Suit).Accepted, Is.False);
            Assert.That(s.Do(PlayerAction.Place, s.Place, s.Suit).Accepted, Is.False);
            Assert.That(s.World.Players.GetPlaced(s.Place), Is.Null);
        }
        [Test] public void InvalidStationDelayCannotPartiallyRegister()
        {
            var s = new Scene(false); var id = Fixture.Id(44);
            Assert.Throws<ArgumentException>(() => s.World.Players.RegisterTarget(id, PlayerTargetKind.ProtectiveEquipment,
                stationPreparationMilliseconds: 100));
            Assert.That(s.World.GetObject(id), Is.Null);
            Assert.That(s.World.Players.GetKind(id), Is.Null);
        }
        [Test] public void StationPreparationDisconnectAndStopClearIntention()
        {
            var s = new Scene(stationDelay: 15000); s.Do(PlayerAction.PrepareEquipment, s.Suit);
            s.World.Disconnect(s.World.Epoch, s.C1);
            Assert.That(s.World.Players.GetPreparation(s.A), Is.Null);
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.Null);
            s.World.Stop(); Assert.That(s.World.View.ActiveClaimCount, Is.Zero);
        }
        [Test] public void FullHandsCannotStartOrReserveStationPreparation()
        {
            var s = new Scene(stationDelay: 15000); s.Do(PlayerAction.PickUp, s.Box);
            Assert.That(s.Do(PlayerAction.PrepareEquipment, s.Suit).Status, Is.EqualTo(InteractionStatus.ActorAlreadyHolding));
            Assert.That(s.World.Players.GetPreparation(s.A), Is.Null);
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.Null);
            Assert.That(s.World.GetObject(s.Box)!.HolderId, Is.EqualTo(s.A));
        }
        [TestCase(true)] [TestCase(false)] public void StationPreparationImpactOrAttachmentFailureClearsIntention(bool impact)
        {
            var s = new Scene(stationDelay: 15000); s.Do(PlayerAction.PrepareEquipment, s.Suit);
            if (impact) s.World.ApplyWorkerImpact(s.World.Epoch, s.A, 1, WorkerImpact.Incapacitating, 1000, Fixture.Id(40), Fixture.Id(41));
            else s.World.ReportAttachmentFailure(s.World.Epoch, s.Suit, s.World.GetObject(s.Suit)!.LeaseGeneration);
            Assert.That(s.World.Players.GetPreparation(s.A), Is.Null);
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.Null);
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.None));
        }
        [Test] public void SeatContentionHasOneWinnerAndStandFreesIt()
        {
            var s = new Scene(); Assert.That(s.Do(PlayerAction.Sit, s.Seat).Accepted, Is.True);
            var lose = s.World.ExecuteInteraction(s.C2, s.Command(PlayerAction.Sit, s.Seat, 1, s.B));
            Assert.That(lose.Status, Is.EqualTo(InteractionStatus.AlreadyClaimed));
            Assert.That(s.World.GetWorker(s.B)!.Pose, Is.EqualTo(WorkerPose.Upright));
            Assert.That(s.Do(PlayerAction.Stand, s.Seat).Accepted, Is.True);
            Assert.That(s.World.Players.GetSeat(s.A), Is.Null);
            Assert.That(s.World.ExecuteInteraction(s.C2, s.Command(PlayerAction.Sit, s.Seat, 2, s.B)).Accepted, Is.True);
        }
        [Test] public void FullHandsAndBlockedExitPreserveSeatState()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Box);
            Assert.That(s.Do(PlayerAction.Sit, s.Seat).Status, Is.EqualTo(InteractionStatus.ActorAlreadyHolding));
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Upright));
            s.Do(PlayerAction.Drop, s.Box); s.Do(PlayerAction.Sit, s.Seat);
            s.Access.Decision = PlayerAccess.PlacementBlocked;
            Assert.That(s.Do(PlayerAction.Stand, s.Seat).Status, Is.EqualTo(InteractionStatus.PlacementBlocked));
            Assert.That(s.World.Players.GetSeat(s.A), Is.Not.Null);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Seated));
        }
        [Test] public void LegacyCommandsCannotBypassSeatClearance()
        {
            var s = new Scene();
            Assert.That(s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, 1, InteractionKind.Grab, s.Seat)).Accepted, Is.False);
            s.Sequence = 1; s.Do(PlayerAction.Sit, s.Seat);
            Assert.That(s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, 3, InteractionKind.Release, s.Seat, leaseGeneration: 1)).Accepted, Is.False);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Seated));
        }
        [Test] public void SeatExpiryAndAttachmentFailureRestoreWorkerPosture()
        {
            var s = new Scene(); s.Do(PlayerAction.Sit, s.Seat); s.World.AdvanceTo(3000);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Upright));
            s.Do(PlayerAction.Sit, s.Seat);
            Assert.That(s.World.ReportAttachmentFailure(s.World.Epoch, s.Seat, s.World.GetObject(s.Seat)!.LeaseGeneration).Accepted, Is.True);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Upright));
        }
        [Test] public void SeatRenewalKeepsTheSameLease()
        {
            var s = new Scene(); s.Do(PlayerAction.Sit, s.Seat); s.World.AdvanceTo(1000);
            Assert.That(s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, 2, InteractionKind.Renew, s.Seat, leaseGeneration: 1)).Accepted, Is.True);
            s.World.AdvanceTo(3000);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Seated));
            Assert.That(s.World.GetObject(s.Seat)!.LeaseGeneration, Is.EqualTo(1));
        }
        [Test] public void ImpactReleasesSeatWithoutRestoringAnIncapacitatedWorker()
        {
            var s = new Scene(); s.Do(PlayerAction.Sit, s.Seat);
            s.World.ApplyWorkerImpact(s.World.Epoch, s.A, 1, WorkerImpact.Incapacitating, 1000, Fixture.Id(40), Fixture.Id(41));
            Assert.That(s.World.Players.GetSeat(s.A), Is.Null);
            Assert.That(s.World.GetWorker(s.A)!.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(s.World.GetWorker(s.A)!.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
        }
        [Test] public void EquipmentUsesCustodySlotAndLeavesHandsAvailable()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Suit); var equip = s.Command(PlayerAction.Equip, s.Suit, 2);
            Assert.That(s.World.ExecuteInteraction(s.C1, equip).HasNewCommit, Is.True); s.Sequence = 2;
            Assert.That(s.World.ExecuteInteraction(s.C1, equip).IsReplay, Is.True);
            Assert.That(s.World.Players.GetHeld(s.A), Is.Null);
            Assert.That(s.World.Players.GetEquipment(s.A)!.EntityId, Is.EqualTo(s.Suit));
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(s.Do(PlayerAction.PickUp, s.Box).Accepted, Is.True);
            Assert.That(s.Do(PlayerAction.Unequip, s.Suit).Accepted, Is.True);
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(s.World.Players.GetEquipment(s.A), Is.Null);
        }
        [Test] public void EquipmentRequiresCorrectHolderAndWorkerRevision()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Suit);
            var stolen = s.Command(PlayerAction.Equip, s.Suit, 1, s.B);
            Assert.That(s.World.ExecuteInteraction(s.C2, stolen).Status, Is.EqualTo(InteractionStatus.NotHolder));
            var stale = s.Command(PlayerAction.Equip, s.Suit, 2);
            s.World.SetWorkerEnvironment(s.World.Epoch, s.A, 0, WorkerSuit.None, 10);
            Assert.That(s.World.ExecuteInteraction(s.C1, stale).Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(s.World.GetObject(s.Suit)!.HolderId, Is.EqualTo(s.A));
            Assert.That(s.World.Players.GetEquipment(s.A), Is.Null);
        }
        [Test] public void BlockedPlacementCannotLoseTheHeldObject()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Box); s.Access.Decision = PlayerAccess.PlacementBlocked;
            Assert.That(s.Do(PlayerAction.Place, s.Place, s.Box).Status, Is.EqualTo(InteractionStatus.PlacementBlocked));
            Assert.That(s.World.GetObject(s.Box)!.HolderId, Is.EqualTo(s.A));
            Assert.That(s.World.Players.GetPlaced(s.Place), Is.Null);
        }
        [Test] public void PlacementTakeIsAtomicWhenHandsAreFull()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Box); s.Do(PlayerAction.Place, s.Place, s.Box);
            s.Do(PlayerAction.PickUp, s.Suit);
            Assert.That(s.Do(PlayerAction.Take, s.Place, s.Box).Status, Is.EqualTo(InteractionStatus.ActorAlreadyHolding));
            Assert.That(s.World.Players.GetPlaced(s.Place)!.EntityId, Is.EqualTo(s.Box));
            s.Do(PlayerAction.Drop, s.Suit);
            Assert.That(s.Do(PlayerAction.Take, s.Place, s.Box).Accepted, Is.True);
            Assert.That(s.World.Players.GetPlaced(s.Place), Is.Null);
            Assert.That(s.World.GetObject(s.Box)!.HolderId, Is.EqualTo(s.A));
        }
        [Test] public void DisconnectEjectsEquipmentAndReleasesSeat()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Suit); s.Do(PlayerAction.Equip, s.Suit); s.Do(PlayerAction.Sit, s.Seat);
            s.World.Disconnect(s.World.Epoch, s.C1);
            Assert.That(s.World.GetObject(s.Suit)!.SlotId, Is.Null);
            Assert.That(s.World.GetObject(s.Seat)!.HolderId, Is.Null);
            Assert.That(s.World.GetWorker(s.A), Is.Null);
            Assert.That(s.World.Players.GetEquipment(s.A), Is.Null);
        }
        [Test] public void PausedAndOldEpochPlayerCommandsCannotMutate()
        {
            var s = new Scene(); s.World.Pause(s.World.Epoch);
            Assert.That(s.Do(PlayerAction.PickUp, s.Box).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            s.World.Resume(s.World.Epoch);
            Assert.That(s.Do(PlayerAction.PickUp, s.Box).Accepted, Is.True);
            var stale = new InteractionCommand(Guid.NewGuid(), 3, InteractionKind.Player, s.Seat,
                player: new PlayerRequest(PlayerAction.Sit, 0, 0));
            Assert.That(s.World.ExecuteInteraction(s.C1, stale).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
        }
        [Test] public void MissingOrThrowingPlayerPolicyNeverFabricatesSuccess()
        {
            var world = new WorldSession(new WorldSessionConfiguration(1, 60000), new TestAccess());
            world.RegisterConnection(Fixture.Id(80), Fixture.Id(81)); world.Players.RegisterActor(Fixture.Id(81), Fixture.Id(82));
            world.Players.RegisterTarget(Fixture.Id(83), PlayerTargetKind.Seat); world.Start();
            Assert.That(world.ExecuteInteraction(Fixture.Id(80), new InteractionCommand(world.Epoch, 1, InteractionKind.Player,
                Fixture.Id(83), player: new PlayerRequest(PlayerAction.Sit, 0, 0))).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(world.View.ActiveClaimCount, Is.Zero);
            var s = new Scene(); s.Access.Callback = () => throw new InvalidOperationException("intentional policy failure");
            Assert.Throws<InvalidOperationException>(() => s.Do(PlayerAction.Sit, s.Seat));
            Assert.That(s.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(s.World.View.ActiveClaimCount, Is.Zero);
            Assert.That(s.World.WorkerCount, Is.Zero);
        }
        [Test] public void StalePlayerReleaseCannotChangeCurrentCustody()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Box);
            var command = s.Command(PlayerAction.Drop, s.Box, 2);
            s.World.AdvanceTo(1000);
            s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, 2, InteractionKind.Renew, s.Box, leaseGeneration: 1));
            var stale = new InteractionCommand(s.World.Epoch, 3, InteractionKind.Player, s.Box, player: command.Player);
            Assert.That(s.World.ExecuteInteraction(s.C1, stale).Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(s.World.GetObject(s.Box)!.HolderId, Is.EqualTo(s.A));
        }
        [Test] public void EnvironmentCannotRemoveAnOccupiedEquipmentSlot()
        {
            var s = new Scene(); s.Do(PlayerAction.PickUp, s.Suit); s.Do(PlayerAction.Equip, s.Suit);
            var worker = s.World.GetWorker(s.A)!;
            Assert.That(s.World.SetWorkerEnvironment(s.World.Epoch, s.A, worker.Revision, WorkerSuit.None, 0).Status,
                Is.EqualTo(WorkerStatus.InvalidState));
            Assert.That(s.World.GetWorker(s.A)!.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(s.World.SetWorkerEnvironment(s.World.Epoch, s.A, worker.Revision, WorkerSuit.Compromised, 1).Changed, Is.True);
            Assert.That(s.World.Players.GetEquipment(s.A)!.EntityId, Is.EqualTo(s.Suit));
        }
        [Test] public void RestartRequiresExplicitPlayerPolicyRebinding()
        {
            var s = new Scene(); var next = s.World.Restart(new TestAccess(), nextPlayerActions: s.Access);
            next.RegisterConnection(s.C1, s.A); next.Players.RegisterActor(s.A, Fixture.Id(11));
            next.Players.RegisterTarget(s.Seat, PlayerTargetKind.Seat); next.Start();
            Assert.That(next.ExecuteInteraction(s.C1, new InteractionCommand(next.Epoch, 1, InteractionKind.Player, s.Seat,
                player: new PlayerRequest(PlayerAction.Sit, 0, 0))).Accepted, Is.True);
            Assert.That(s.World.Players.GetSeat(s.A), Is.Null);
        }
        [Test] public void MalformedPlayerPayloadsDoNotConsumeTheCommandSequence()
        {
            var s = new Scene();
            var invalid = new[] { new PlayerRequest((PlayerAction)99, 0, 0), new PlayerRequest(PlayerAction.Sit, -1, 0),
                new PlayerRequest(PlayerAction.Sit, 0, -1), new PlayerRequest(PlayerAction.Drop, 0, 0),
                new PlayerRequest(PlayerAction.PickUp, 0, 0, 1), new PlayerRequest(PlayerAction.Place, 0, 0, 1),
                new PlayerRequest(PlayerAction.Take, 0, 0), new PlayerRequest(PlayerAction.Sit, 0, 0, itemId: s.Box) };
            foreach (var payload in invalid)
                Assert.That(s.World.ExecuteInteraction(s.C1, new InteractionCommand(s.World.Epoch, 1, InteractionKind.Player,
                    s.Seat, player: payload)).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            Assert.That(s.Do(PlayerAction.Sit, s.Seat).Accepted, Is.True);
        }
        [Test] public void TenPlayerSessionTeardownsClearAllOwnedState()
        {
            for (int i = 0; i < 10; i++)
            {
                var s = new Scene(); s.Do(PlayerAction.PickUp, s.Suit); s.Do(PlayerAction.Equip, s.Suit); s.Do(PlayerAction.Sit, s.Seat);
                s.World.Stop(); s.World.Stop();
                Assert.That(s.World.View.RegisteredObjectCount, Is.Zero);
                Assert.That(s.World.View.ActiveClaimCount, Is.Zero);
                Assert.That(s.World.Players.GetEquipment(s.A), Is.Null);
                Assert.That(s.World.WorkerCount, Is.Zero);
            }
        }
        [Test] public void InvalidPlayerRegistrationHasNoPartialObject()
        {
            var s = new Scene(false);
            Assert.Throws<InvalidOperationException>(() => s.World.Players.RegisterTarget(Fixture.Id(50), PlayerTargetKind.Placement, s.Box));
            Assert.That(s.World.GetObject(Fixture.Id(50)), Is.Null);
            s.World.Start();
            Assert.Throws<InvalidOperationException>(() => s.World.Players.RegisterTarget(Fixture.Id(51), PlayerTargetKind.Seat));
        }
    }
}
