using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class FacilityControlTests
    {
        private sealed class Access : IInteractionAccessPolicy
        { public bool Allowed = true; public AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind) => Allowed ? AccessDecision.Allowed : AccessDecision.OutOfReach; }
        private Guid actor, control;
        private Access access = null!;
        private WorldSession Create(ControlAction action = ControlAction.Toggle, ControlAction? additional = null)
        {
            actor = Guid.NewGuid(); control = Guid.NewGuid(); access = new Access();
            var world = new WorldSession(new WorldSessionConfiguration(1, 100000, allowPause: true), access);
            world.RegisterConnection(actor, actor); world.Controls.Register(control, action, additional); world.Start(); return world;
        }
        private InteractionCommand Command(WorldSession world, long sequence, long revision, ControlAction action = ControlAction.Toggle) =>
            new InteractionCommand(world.Epoch, sequence, InteractionKind.Control, control, control: new ControlRequest(action, revision));
        [Test]
        public void ReplayedControlDoesNotToggleAgain()
        {
            var world = Create(); var command = Command(world, 1, 0);
            Assert.That(world.ExecuteInteraction(actor, command).HasNewCommit, Is.True);
            var replay = world.ExecuteInteraction(actor, command);
            Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(world.Controls.Get(control)!.Active, Is.True); Assert.That(world.Controls.Get(control)!.Revision, Is.EqualTo(1));
        }
        [Test]
        public void StaleControlRevisionCannotReverseAnotherOperation()
        {
            var world = Create(); world.ExecuteInteraction(actor, Command(world, 1, 0));
            Assert.That(world.ExecuteInteraction(actor, Command(world, 2, 0)).Status, Is.EqualTo(InteractionStatus.RevisionConflict));
            Assert.That(world.ExecuteInteraction(actor, Command(world, 3, 1)).HasNewCommit, Is.True);
            Assert.That(world.Controls.Get(control)!.Active, Is.False);
        }
        [Test]
        public void ControlRetriesIncludeTheirTypedOperation()
        {
            var world = Create(ControlAction.Toggle, ControlAction.Connect); world.ExecuteInteraction(actor, Command(world, 1, 0));
            Assert.That(world.ExecuteInteraction(actor, Command(world, 1, 0, ControlAction.Connect)).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            Assert.That(world.Controls.Get(control)!.Connected, Is.False);
        }
        [Test]
        public void ControlsRespectReachPauseAndWorkerAvailability()
        {
            var world = Create(); access.Allowed = false;
            Assert.That(world.ExecuteInteraction(actor, Command(world, 1, 0)).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            access.Allowed = true; world.Pause(world.Epoch);
            Assert.That(world.ExecuteInteraction(actor, Command(world, 2, 0)).HasNewCommit, Is.False);
            world.Resume(world.Epoch);
            world.ApplyWorkerImpact(world.Epoch, actor, 1, WorkerImpact.Knockdown, 1000, Guid.NewGuid(), Guid.NewGuid());
            Assert.That(world.ExecuteInteraction(actor, Command(world, 3, 0)).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(world.Controls.Get(control)!.Revision, Is.Zero);
        }
        [Test]
        public void ValveStepsWrapWithoutGrowingAnUnboundedCounter()
        {
            var world = Create(ControlAction.Turn);
            for (int i = 0; i < 60; i++) Assert.That(world.ExecuteInteraction(actor, Command(world, i + 1, i, ControlAction.Turn)).HasNewCommit, Is.True);
            Assert.That(world.Controls.Get(control)!.Turns, Is.Zero); Assert.That(world.Controls.Get(control)!.Revision, Is.EqualTo(60));
        }
        [Test]
        public void ConnectionDoesNotToggleTheStationPowerState()
        {
            var world = Create(ControlAction.Toggle, ControlAction.Connect);
            world.ExecuteInteraction(actor, Command(world, 1, 0, ControlAction.Connect));
            Assert.That(world.Controls.Get(control)!.Connected, Is.True); Assert.That(world.Controls.Get(control)!.Active, Is.False);
        }
        [Test]
        public void MixedControlPayloadCannotConsumeTheCommandSequence()
        {
            var world = Create(); var mixed = new InteractionCommand(world.Epoch, 1, InteractionKind.Grab, control,
                control: new ControlRequest(ControlAction.Toggle, 0));
            Assert.That(world.ExecuteInteraction(actor, mixed).IsTerminal, Is.False);
            Assert.That(world.ExecuteInteraction(actor, Command(world, 1, 0)).HasNewCommit, Is.True);
        }
        [Test]
        public void TerminalWorldClearsControlsAndRejectsOldCallbacks()
        {
            var world = Create(); world.ExecuteInteraction(actor, Command(world, 1, 0));
            world.Finish(world.Epoch, WorldEndReason.Succeeded);
            Assert.That(world.Controls.Get(control), Is.Null);
            Assert.That(world.ExecuteInteraction(actor, Command(world, 2, 1)).HasNewCommit, Is.False);
        }
    }
}
