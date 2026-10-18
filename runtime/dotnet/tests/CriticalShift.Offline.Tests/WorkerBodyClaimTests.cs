using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class WorkerBodyClaimTests
    {
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private Guid Rescuer => Id(1);
        private Guid Patient => Id(2);
        private Guid Other => Id(3);
        private Guid Body => Id(200);
        private Guid Crate => Id(100);
        private sealed class Clearance : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid actor, long attempt) => RecoveryClearance.Safe; }

        private WorldSession Setup()
        {
            var world = new WorldSession(new WorldSessionConfiguration(7, 20000, true), new TestAccess(), new Clearance());
            world.RegisterConnection(Id(11), Rescuer); world.RegisterConnection(Id(12), Patient); world.RegisterConnection(Id(13), Other);
            world.RegisterWorkerBody(Patient, Body); world.RegisterObject(Crate);
            return world;
        }
        private WorkerReply Down(WorldSession world, Guid actor, long sequence = 1) =>
            world.ApplyWorkerImpact(world.Epoch, actor, sequence, WorkerImpact.Knockdown, 0, Id(90), Id(90 + (int)sequence));
        private WorkerReply Begin(WorldSession world)
        {
            var worker = world.GetWorker(Patient)!;
            return world.BeginWorkerRecovery(world.Epoch, Patient, worker.RecoveryEpisode, worker.Revision);
        }

        [Test] public void WorkerBodyRegistrationIsUniqueSetupOnlyAndAtomicOnCollision()
        {
            var world = Setup(); long revision = world.View.Revision;
            Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerBody(Patient, Id(201)));
            Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerBody(Other, Body));
            Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerBody(Other, Crate));
            Assert.That(world.GetWorkerBodyClaim(Other), Is.Null); Assert.That(world.GetWorkerForBody(Body)!.Id, Is.EqualTo(Patient));
            Assert.That(world.View.Revision, Is.EqualTo(revision));
            world.Start(); Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerBody(Other, Id(201)));
        }

        [Test] public void UprightBodyRejectionConsumesTheStreamBeforeADownBodyCanBeGrabbed()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start();
            Assert.That(port.Grab(Body).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(1)); Down(world, Patient);
            Assert.That(port.Grab(Body).HasNewCommit, Is.True); Assert.That(port.LastTerminalSequence, Is.EqualTo(2));
            Assert.That(port.GetWorkerBodyClaim(Patient)!.HolderId, Is.EqualTo(Rescuer));
            Assert.That(port.GetWorkerForBody(Body)!.Pose, Is.EqualTo(WorkerPose.Down));
        }

        [Test] public void WorkerDraggingUsesTheSameExclusiveClaimAndPreservesConditions()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start();
            world.SetWorkerEnvironment(world.Epoch, Patient, 0, WorkerSuit.Compromised, 70); Down(world, Patient);
            Assert.That(port.Grab(Body).HasNewCommit, Is.True);
            Assert.That(port.Grab(Crate).Status, Is.EqualTo(InteractionStatus.ActorAlreadyHolding));
            Assert.That(world.GetObject(Crate)!.HolderId, Is.Null); Assert.That(world.View.ActiveClaimCount, Is.EqualTo(1));
            var patient = world.GetWorker(Patient)!;
            Assert.That(patient.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(patient.Suit, Is.EqualTo(WorkerSuit.Compromised));
            Assert.That(patient.Contamination, Is.EqualTo(70));
        }

        [Test] public void HeldWorkerBodyBlocksRecoveryUntilTheGripIsReleased()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            long revision = world.GetWorker(Patient)!.Revision;
            Assert.That(Begin(world).Status, Is.EqualTo(WorkerStatus.BodyClaimed));
            Assert.That(world.GetWorker(Patient)!.Revision, Is.EqualTo(revision));
            port.Release(Body); Assert.That(Begin(world).Status, Is.EqualTo(WorkerStatus.Applied));
            long attempt = world.GetWorker(Patient)!.RecoveryAttempt;
            Assert.That(world.CompleteWorkerRecovery(world.Epoch, Patient, attempt).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(port.Grab(Body).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
        }

        [Test] public void UnconsciousWorkerCanBeDraggedWithoutBeingRevived()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start();
            world.ApplyWorkerImpact(world.Epoch, Patient, 1, WorkerImpact.Incapacitating, 0, Id(95), Id(96));
            Assert.That(port.Grab(Body).HasNewCommit, Is.True); Assert.That(world.GetWorker(Patient)!.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            port.Release(Body); Assert.That(Begin(world).Status, Is.EqualTo(WorkerStatus.RequiresAid));
            Assert.That(world.GetWorker(Patient)!.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
        }

        [Test] public void RecoveringBodyCannotAcquireANewDragClaim()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); Begin(world);
            Assert.That(port.Grab(Body).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.Null);
            Assert.That(world.GetWorker(Patient)!.Pose, Is.EqualTo(WorkerPose.Recovering));
        }

        [Test] public void TwoRescuersCannotOwnOneWorkerBody()
        {
            var world = Setup(); var first = new LocalCommandPort(world, Id(11)); var second = new LocalCommandPort(world, Id(13));
            world.Start(); Down(world, Patient);
            Assert.That(first.Grab(Body).HasNewCommit, Is.True); Assert.That(second.Grab(Body).Status, Is.EqualTo(InteractionStatus.AlreadyClaimed));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.EqualTo(Rescuer)); Assert.That(world.View.ActiveClaimCount, Is.EqualTo(1));
        }

        [Test] public void KnockingDownTheRescuerReleasesTheDraggedBody()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            var impact = Down(world, Rescuer);
            Assert.That(impact.ReleasedClaim!.EntityId, Is.EqualTo(Body)); Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.Null);
            Assert.That(world.GetWorker(Patient)!.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(world.View.ActiveClaimCount, Is.Zero);
        }

        [Test] public void AnotherPatientImpactDoesNotStealTheRescuersLease()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            long generation = world.GetWorkerBodyClaim(Patient)!.LeaseGeneration; Down(world, Patient, 2);
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.EqualTo(Rescuer));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.LeaseGeneration, Is.EqualTo(generation));
            Assert.That(world.GetWorker(Patient)!.RecoveryEpisode, Is.EqualTo(2));
        }

        [Test] public void ExpiredDragLeaseCannotReleaseTheReacquiredBody()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            long old = world.GetWorkerBodyClaim(Patient)!.LeaseGeneration; world.AdvanceTo(3000);
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.Null); Assert.That(port.Grab(Body).HasNewCommit, Is.True);
            Assert.That(world.ReportAttachmentFailure(world.Epoch, Body, old).Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.EqualTo(Rescuer));
        }

        [Test] public void DisconnectingThePatientRetiresItsBodyAndReleasesTheRescuer()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            world.Schedule(world.Epoch, Body, "body-prompt", 100); world.Schedule(world.Epoch, Patient, "worker-prompt", 100);
            world.Disconnect(world.Epoch, Id(12));
            Assert.That(world.GetWorker(Patient), Is.Null); Assert.That(world.GetWorkerForBody(Body), Is.Null);
            Assert.That(world.GetObject(Body)!.IsRetired, Is.True); Assert.That(world.GetObject(Body)!.HolderId, Is.Null);
            Assert.That(world.View.PendingTimerCount, Is.Zero);
            var replay = port.ReplayLast(); Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(port.Grab(Crate).HasNewCommit, Is.True);
        }

        [Test] public void DisconnectingTheRescuerKeepsThePatientDownAndFree()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            world.Disconnect(world.Epoch, Id(11));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.Null); Assert.That(world.GetWorker(Patient)!.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(world.View.ConnectedPlayerCount, Is.EqualTo(2));
        }

        [Test] public void WorkerBodyBindingsDoNotSurviveAFreshWorld()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            var next = world.Restart(new TestAccess(), new Clearance());
            Assert.That(world.GetWorkerBodyClaim(Patient), Is.Null); Assert.That(next.GetWorkerForBody(Body), Is.Null);
            next.RegisterConnection(Id(11), Rescuer); next.RegisterConnection(Id(12), Patient); next.RegisterWorkerBody(Patient, Body); next.Start();
            Assert.That(next.GetWorkerBodyClaim(Patient)!.HolderId, Is.Null); Assert.That(next.View.ActiveClaimCount, Is.Zero);
            Assert.That(next.RetireObject(world.Epoch, Body).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(port.Release(Body).HasNewCommit, Is.False);
        }

        [Test] public void MachinesAndUnrelatedRetirementCannotConsumeAWorkerBody()
        {
            var world = Setup(); world.Production.RegisterMachine(Id(300), new MachineRecipe(Id(301), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 100, 100));
            world.Reactor.Register(Id(400), new ReactorDefinition(Id(401)));
            var port = new LocalCommandPort(world, Id(11)); world.Start(); Down(world, Patient); port.Grab(Body);
            Assert.That(port.OperateMachine(Id(300), ProductionAction.Insert, Body).Accepted, Is.False);
            Assert.That(port.OperateReactor(Id(400), ReactorAction.Insert, Body).Accepted, Is.False);
            Assert.That(world.RetireObject(world.Epoch, Body).Status, Is.EqualTo(InteractionStatus.TargetUnavailable));
            Assert.That(world.GetWorkerBodyClaim(Patient)!.HolderId, Is.EqualTo(Rescuer)); Assert.That(world.GetObject(Body)!.IsRetired, Is.False);
        }
    }
}
