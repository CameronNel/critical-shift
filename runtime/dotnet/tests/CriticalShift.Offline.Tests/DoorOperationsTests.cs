using System;
using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class DoorOperationsTests
    {
        private static readonly Guid Actor = Fixture.Id(10), Connection = Fixture.Id(20), Door = Fixture.Id(30), Box = Fixture.Id(31);
        private static WorldSession Setup(TestAccess? access = null, int receipts = 256)
        {
            var world = new WorldSession(new WorldSessionConfiguration(18, 60000, true, receiptCapacity: receipts), access ?? new TestAccess());
            world.RegisterConnection(Connection, Actor);
            world.RegisterObject(Box);
            world.Doors.Register(Door, "SPAWN_EXIT", DoorState.Closed, DoorState.Open);
            return world;
        }
        private static InteractionCommand Command(WorldSession world, long sequence, DoorAction action, long revision = 0, Guid? target = null) =>
            new InteractionCommand(world.Epoch, sequence, InteractionKind.Door, target ?? Door, door: new DoorRequest(action, revision));

        [Test] public void DoorCommandsShareTheClaimStreamAndReturnDetachedSourceViews()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection); world.Start();
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            var closed = port.GetDoor(Door)!; long revision = world.View.Revision;
            var opened = port.OperateDoor(Door, DoorAction.Open);
            Assert.That(opened.HasNewCommit, Is.True); Assert.That(opened.Door!.Door!.State, Is.EqualTo(DoorState.Open));
            Assert.That(opened.Door.Door.SourceId, Is.EqualTo("SPAWN_EXIT")); Assert.That(opened.Door.Door.Epoch, Is.EqualTo(world.Epoch));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2)); Assert.That(world.View.Revision, Is.EqualTo(revision + 1));
            Assert.That(world.GetObject(Door), Is.Null); Assert.That(world.View.ActiveClaimCount, Is.EqualTo(1));
            Assert.That(closed.State, Is.EqualTo(DoorState.Closed)); Assert.That(closed.Revision, Is.Zero);
            Assert.That(world.Doors.GetBySourceId("SPAWN_EXIT")!.Id, Is.EqualTo(Door));
            var replay = port.ReplayLast();
            Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(replay.Door!.CauseId, Is.EqualTo(opened.Door.CauseId));
            Assert.That(world.View.Revision, Is.EqualTo(revision + 1));
            Assert.That(port.OperateDoor(Door, DoorAction.Close).HasNewCommit, Is.True);
            Assert.That(port.Grab(Door).Status, Is.EqualTo(InteractionStatus.UnknownEntity));
            var records = world.Trace.Records.Where(r => r.Changed && r.DoorResult.HasValue).ToArray();
            Assert.That(records.Length, Is.EqualTo(2)); Assert.That(records[0].ActorId, Is.EqualTo(Actor));
            Assert.That(records[0].DoorSourceId, Is.EqualTo("SPAWN_EXIT")); Assert.That(records[0].PreviousDoorRevision, Is.Zero);
            Assert.That(records[0].DoorRevision, Is.EqualTo(1)); Assert.That(records[0].CauseId, Is.Not.EqualTo(Guid.Empty));
        }

        [Test] public void LockedAndNonOperableDoorsRejectWithoutChangingRevision()
        {
            var world = Setup(); Guid locked = Fixture.Id(32), dock = Fixture.Id(33);
            world.Doors.Register(locked, "LOCKED_EXIT", DoorState.Locked, DoorState.Open);
            world.Doors.Register(dock, "DOCK_P2", DoorState.Closed, DoorState.Closed, playerOperable: false);
            var port = new LocalCommandPort(world, Connection); world.Start(); long revision = world.View.Revision;
            Assert.That(port.OperateDoor(locked, DoorAction.Open).Door!.Status, Is.EqualTo(DoorStatus.Locked));
            Assert.That(port.ReplayLast().IsReplay, Is.True);
            Assert.That(port.OperateDoor(dock, DoorAction.Open).Door!.Status, Is.EqualTo(DoorStatus.NotOperable));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2)); Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(port.GetDoor(locked)!.Revision, Is.Zero); Assert.That(port.GetDoor(dock)!.Revision, Is.Zero);
            Assert.That(port.GetDoor(dock)!.State, Is.EqualTo(DoorState.Closed)); Assert.That(world.View.ActiveClaimCount, Is.Zero);
            Assert.That(port.OperateDoor(Door, DoorAction.Open).HasNewCommit, Is.True);
        }

        [Test] public void DoorAdmissionUsesAuthenticatedActorReachPauseAndWorkerState()
        {
            var access = new TestAccess(); var world = Setup(access); world.Start(); long revision = world.View.Revision;
            Assert.That(world.ExecuteInteraction(Fixture.Id(999), Command(world, 1, DoorAction.Open)).Status, Is.EqualTo(InteractionStatus.UnknownConnection));
            Assert.That(world.ExecuteInteraction(Connection, new InteractionCommand(Fixture.Id(999), 1, InteractionKind.Door, Door,
                door: new DoorRequest(DoorAction.Open, 0))).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(access.Calls, Is.Zero); Assert.That(world.View.Revision, Is.EqualTo(revision));
            access.Decision = AccessDecision.OutOfReach;
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 1, DoorAction.Open)).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(access.LastActor, Is.EqualTo(Actor)); access.Decision = AccessDecision.Allowed;
            world.Pause(world.Epoch);
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 2, DoorAction.Open)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            world.Resume(world.Epoch);
            Assert.That(world.ApplyWorkerImpact(world.Epoch, Actor, 1, WorkerImpact.Knockdown, 1500, Fixture.Id(70), Fixture.Id(71)).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 3, DoorAction.Open)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(world.Doors.Get(Door)!.Revision, Is.Zero); Assert.That(world.Doors.Get(Door)!.State, Is.EqualTo(DoorState.Closed));
        }

        [Test] public void DoorVersionAndPayloadShapesCannotBypassExistingValidation()
        {
            var world = Setup(); world.Start();
            var valid = new DoorRequest(DoorAction.Open, 0);
            var production = new ProductionRequest(ProductionAction.SetPower, 0);
            var reactor = new ReactorRequest(ReactorAction.Start, 0);
            var invalid = new[]
            {
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, door: new DoorRequest(DoorAction.Open, 0, 2)),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, door: new DoorRequest((DoorAction)99, 0)),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, door: new DoorRequest(DoorAction.Open, -1)),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, expectedRevision: 1, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, leaseGeneration: 1, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, production: production, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Door, Door, reactor: reactor, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Grab, Box, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Release, Box, leaseGeneration: 1, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Renew, Box, leaseGeneration: 1, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Production, Box, production: production, door: valid),
                new InteractionCommand(world.Epoch, 1, InteractionKind.Reactor, Box, reactor: reactor, door: valid)
            };
            long revision = world.View.Revision;
            foreach (var command in invalid)
            {
                var reply = world.ExecuteInteraction(Connection, command);
                Assert.That(reply.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(reply.IsTerminal, Is.False);
            }
            Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 1, DoorAction.Open)).HasNewCommit, Is.True);
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 1, DoorAction.Close)).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            Assert.That(world.Doors.Get(Door)!.State, Is.EqualTo(DoorState.Open));
        }

        [Test] public void StaleDoorRevisionAndNoChangeDoNotMintCommits()
        {
            var world = Setup(); world.Start(); Assert.That(world.ExecuteInteraction(Connection, Command(world, 1, DoorAction.Open)).HasNewCommit, Is.True);
            long revision = world.View.Revision;
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 2, DoorAction.Close)).Door!.Status, Is.EqualTo(DoorStatus.RevisionConflict));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 3, DoorAction.Open, 1)).Status, Is.EqualTo(InteractionStatus.NoChange));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.Doors.Get(Door)!.Revision, Is.EqualTo(1));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 4, DoorAction.Close, 1)).HasNewCommit, Is.True);
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 5, DoorAction.Open, target: Fixture.Id(99))).Door!.Status, Is.EqualTo(DoorStatus.UnknownDoor));
            Assert.That(world.Doors.Get(Door)!.Revision, Is.EqualTo(2));
        }

        [Test] public void DoorStreamRejectsSequenceGapsAndEvictedReceipts()
        {
            var world = Setup(receipts: 2); world.Start(); var first = Command(world, 1, DoorAction.Open);
            world.ExecuteInteraction(Connection, first);
            world.ExecuteInteraction(Connection, Command(world, 2, DoorAction.Close, 1));
            world.ExecuteInteraction(Connection, Command(world, 3, DoorAction.Open, 2)); long revision = world.View.Revision;
            Assert.That(world.ExecuteInteraction(Connection, first).Status, Is.EqualTo(InteractionStatus.TooOld));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 5, DoorAction.Close, 3)).Status, Is.EqualTo(InteractionStatus.SequenceGap));
            Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(world.ExecuteInteraction(Connection, Command(world, 4, DoorAction.Close, 3)).HasNewCommit, Is.True);
        }

        [Test] public void DoorSetupRejectsDuplicateSourcesClaimAndSlotIdentitiesAndCapacity()
        {
            var world = Setup(); long revision = world.View.Revision;
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(Door, "OTHER", DoorState.Open, DoorState.Open));
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(Fixture.Id(90), "SPAWN_EXIT", DoorState.Open, DoorState.Open));
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(Box, "BOX", DoorState.Open, DoorState.Open));
            Assert.Throws<InvalidOperationException>(() => world.RegisterObject(Door));
            Assert.Throws<ArgumentException>(() => world.Doors.Register(Fixture.Id(90), " bad ", DoorState.Open, DoorState.Open));
            Assert.Throws<ArgumentOutOfRangeException>(() => world.Doors.Register(Fixture.Id(90), "BAD_MODE", (DoorState)99, DoorState.Open));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.Doors.Count, Is.EqualTo(1));
            var recipe = new MachineRecipe(Fixture.Id(91), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 100, 100);
            Assert.Throws<InvalidOperationException>(() => world.Production.RegisterMachine(Door, recipe));
            Guid slot = Fixture.Id(92); world.Production.RegisterMachine(slot, recipe);
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(slot, "SLOT", DoorState.Open, DoorState.Open));
            for (int i = 1; i < 128; i++) world.Doors.Register(Fixture.Id(1000 + i), "SOURCE_" + i, DoorState.Closed, DoorState.Open);
            Assert.That(world.Doors.Count, Is.EqualTo(128)); revision = world.View.Revision;
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(Fixture.Id(9999), "OVERFLOW", DoorState.Open, DoorState.Open));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.Doors.GetBySourceId("OVERFLOW"), Is.Null);
        }

        [Test] public void DoorTeardownClearsStateAndFreshWorldRejectsTheOldEpoch()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection);
            Assert.That(port.OperateDoor(Door, DoorAction.Open).Status, Is.EqualTo(InteractionStatus.NotReady));
            Assert.That(port.LastTerminalSequence, Is.Zero); world.Start(); port.OperateDoor(Door, DoorAction.Open);
            var retained = port.GetDoor(Door)!;
            Assert.Throws<InvalidOperationException>(() => world.Doors.Register(Fixture.Id(90), "LATE", DoorState.Open, DoorState.Open));
            var old = Command(world, 2, DoorAction.Close, 1); world.BeginEvacuation(world.Epoch, Fixture.Id(93));
            var next = world.Restart(new TestAccess());
            Assert.That(world.Doors.Count, Is.Zero); Assert.That(port.GetDoor(Door), Is.Null); Assert.That(world.Doors.EvacuationCauseId, Is.Null);
            Assert.That(retained.State, Is.EqualTo(DoorState.Open));
            next.RegisterConnection(Connection, Actor); next.Doors.Register(Door, "SPAWN_EXIT", DoorState.Closed, DoorState.Open); next.Start();
            Assert.That(next.Epoch, Is.Not.EqualTo(retained.Epoch));
            Assert.That(next.ExecuteInteraction(Connection, old).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(next.Doors.Get(Door)!.Revision, Is.Zero); Assert.That(next.Doors.Get(Door)!.State, Is.EqualTo(DoorState.Closed));
        }

        [Test] public void EvacuationAppliesAuthoredDefaultsOnceAndKeepsTheShiftRunning()
        {
            var world = Setup(); Guid dock = Fixture.Id(40), blast = Fixture.Id(41), cause = Fixture.Id(80);
            world.Doors.Register(dock, "DOCK_P2", DoorState.Closed, DoorState.Closed, false);
            world.Doors.Register(blast, "REACTOR_BLAST", DoorState.Open, DoorState.Locked);
            var port = new LocalCommandPort(world, Connection); world.Start(); long revision = world.View.Revision;
            var first = world.BeginEvacuation(world.Epoch, cause);
            Assert.That(first.Status, Is.EqualTo(DoorEvacuationStatus.Applied)); Assert.That(first.Changes.Count, Is.EqualTo(2));
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(world.View.Revision, Is.EqualTo(revision + 1));
            Assert.That(world.Doors.Get(Door)!.State, Is.EqualTo(DoorState.Open));
            Assert.That(world.Doors.Get(dock)!.State, Is.EqualTo(DoorState.Closed)); Assert.That(world.Doors.Get(dock)!.Revision, Is.Zero);
            Assert.That(world.Doors.Get(blast)!.State, Is.EqualTo(DoorState.Locked));
            Assert.That(port.OperateDoor(Door, DoorAction.Close).HasNewCommit, Is.True); revision = world.View.Revision;
            Assert.That(world.BeginEvacuation(world.Epoch, cause).Status, Is.EqualTo(DoorEvacuationStatus.Duplicate));
            Assert.That(world.BeginEvacuation(world.Epoch, Fixture.Id(81)).Status, Is.EqualTo(DoorEvacuationStatus.AlreadyActive));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.Doors.Get(Door)!.State, Is.EqualTo(DoorState.Closed));
            Assert.That(world.Doors.EvacuationCauseId, Is.EqualTo(cause));
            var changed = world.Trace.Records.Where(r => r.Kind == SessionTraceKind.Door && r.Changed).ToArray();
            Assert.That(changed.Length, Is.EqualTo(2)); Assert.That(changed.All(r => r.CauseId == cause), Is.True);
            Assert.That(changed.All(r => r.PreviousDoorRevision == 0 && r.DoorRevision == 1), Is.True);
            Assert.That(world.Trace.Records.Count(r => r.Kind == SessionTraceKind.Evacuation && r.Changed), Is.EqualTo(1));
        }

        [Test] public void EvacuationRejectsInvalidEpochCauseAndLifecycleWithoutActivation()
        {
            var world = Setup(); Guid cause = Fixture.Id(80);
            Assert.That(world.BeginEvacuation(world.Epoch, cause).Status, Is.EqualTo(DoorEvacuationStatus.NotReady)); world.Start();
            Assert.That(world.BeginEvacuation(Fixture.Id(99), cause).Status, Is.EqualTo(DoorEvacuationStatus.WrongEpoch));
            Assert.That(world.BeginEvacuation(world.Epoch, Guid.Empty).Status, Is.EqualTo(DoorEvacuationStatus.InvalidCause));
            world.Pause(world.Epoch); long revision = world.View.Revision;
            Assert.That(world.BeginEvacuation(world.Epoch, cause).Status, Is.EqualTo(DoorEvacuationStatus.Paused));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.Doors.EvacuationCauseId, Is.Null);
            world.Resume(world.Epoch); Assert.That(world.BeginEvacuation(world.Epoch, cause).Changed, Is.True); world.Stop();
            Assert.That(world.BeginEvacuation(world.Epoch, cause).Status, Is.EqualTo(DoorEvacuationStatus.WorldStopped));
            Assert.That(world.Doors.Count, Is.Zero);
        }

        [Test] public void DoorAccessReentrancyFaultClearsTheDoorOwner()
        {
            var access = new TestAccess(); var world = Setup(access); world.Start();
            access.Callback = () => world.BeginEvacuation(world.Epoch, Fixture.Id(80));
            Assert.Throws<InvalidOperationException>(() => world.ExecuteInteraction(Connection, Command(world, 1, DoorAction.Open)));
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Faulted)); Assert.That(world.Doors.Count, Is.Zero);
            Assert.That(world.Doors.Get(Door), Is.Null); Assert.That(world.View.ActiveClaimCount, Is.Zero);
        }
    }
}
