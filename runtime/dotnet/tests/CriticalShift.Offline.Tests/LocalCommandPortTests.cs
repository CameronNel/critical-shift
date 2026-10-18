using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class LocalCommandPortTests
    {
        private static readonly Guid Connection = Fixture.Id(20);
        private static readonly Guid Actor = Fixture.Id(10);
        private static readonly Guid Box = Fixture.Id(30);

        private static WorldSession Setup(TestAccess? access = null)
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, 10000, true), access ?? new TestAccess());
            world.RegisterConnection(Connection, Actor);
            world.RegisterObject(Box);
            return world;
        }

        [Test] public void LocalSenderUsesCurrentRevisionAndLeaseAfterRelease()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection); world.Start();
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.Release(Box).HasNewCommit, Is.True);
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.GetObject(Box)!.LeaseGeneration, Is.EqualTo(2));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(3));
        }

        [Test] public void LocalGameplayRejectionDoesNotWedgeNextIntent()
        {
            var access = new TestAccess { Decision = AccessDecision.OutOfReach };
            var world = Setup(access); var port = new LocalCommandPort(world, Connection); world.Start();
            Assert.That(port.Grab(Box).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            access.Decision = AccessDecision.Allowed;
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2));
        }

        [Test] public void LocalMalformedIntentDoesNotConsumeSequence()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection); world.Start();
            Assert.That(port.Release(Box).Status, Is.EqualTo(InteractionStatus.InvalidPayload));
            Assert.That(port.LastTerminalSequence, Is.Zero);
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(1));
        }

        [Test] public void LocalReplayDoesNotRegrabReleasedObject()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection); world.Start();
            port.Grab(Box); port.Release(Box);
            var replay = port.ReplayLast();
            Assert.That(replay.IsReplay, Is.True);
            Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2));
            Assert.That(port.GetObject(Box)!.HolderId, Is.Null);
        }

        [Test] public void LocalOldPortCannotAffectRestartedWorld()
        {
            var old = Setup(); var port = new LocalCommandPort(old, Connection); old.Start(); port.Grab(Box);
            var next = old.Restart(new TestAccess()); next.RegisterConnection(Connection, Actor); next.RegisterObject(Box); next.Start();
            Assert.That(port.Release(Box).Status, Is.EqualTo(InteractionStatus.WorldStopped));
            Assert.That(next.GetObject(Box)!.HolderId, Is.Null);
            Assert.That(next.GetObject(Box)!.Revision, Is.Zero);
        }

        [Test] public void LocalSenderRejectsInvalidCompositionAndEmptyReplay()
        {
            var world = Setup();
            Assert.Throws<ArgumentNullException>(() => new LocalCommandPort(null!, Connection));
            Assert.Throws<ArgumentException>(() => new LocalCommandPort(world, Guid.Empty));
            Assert.Throws<ArgumentException>(() => new LocalCommandPort(world, Fixture.Id(999)));
            var port = new LocalCommandPort(world, Connection);
            Assert.That(port.ActorId, Is.EqualTo(Actor));
            Assert.Throws<InvalidOperationException>(() => port.ReplayLast());
            world.Start();
            Assert.Throws<InvalidOperationException>(() => new LocalCommandPort(world, Connection));
        }

        [Test] public void AutomaticRenewalDoesNotReplaceTheLastUserIntent()
        {
            var world = Setup(); var port = new LocalCommandPort(world, Connection); world.Start();
            port.Grab(Box); world.AdvanceTo(1000); port.Renew(Box);
            long revision = world.View.Revision;
            var replay = port.ReplayLast();
            Assert.That(replay.IsReplay, Is.True);
            Assert.That(replay.State!.ExpiresAtMilliseconds, Is.EqualTo(3000));
            Assert.That(port.GetObject(Box)!.ExpiresAtMilliseconds, Is.EqualTo(4000));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2));
            Assert.That(world.View.Revision, Is.EqualTo(revision));
        }

        [Test] public void LocalMachineSenderTracksCurrentRevisionsThroughConversion()
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, 10000), new TestAccess());
            world.RegisterConnection(Connection, Actor);
            world.Production.RegisterBatch(Box, Fixture.Id(50), Fixture.Id(51), Fixture.Id(52), MaterialKind.Ore, 10);
            Guid machine = Fixture.Id(60);
            world.Production.RegisterMachine(machine, new MachineRecipe(Fixture.Id(61), MaterialKind.Ore, MaterialKind.CrushedOre,
                1000, 500, 100, 100));
            var port = new LocalCommandPort(world, Connection); world.Start();
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.OperateMachine(machine, ProductionAction.Insert, Box).HasNewCommit, Is.True);
            Assert.That(port.OperateMachine(machine, ProductionAction.SetPower, powered: true).HasNewCommit, Is.True);
            Assert.That(port.OperateMachine(machine, ProductionAction.Start).HasNewCommit, Is.True);
            world.AdvanceTo(1000);
            Assert.That(port.GetBatch(Box)!.Kind, Is.EqualTo(MaterialKind.CrushedOre));
            Assert.That(port.OperateMachine(machine, ProductionAction.Eject).HasNewCommit, Is.True);
            Assert.That(port.Grab(Box).HasNewCommit, Is.True);
            Assert.That(port.GetObject(Box)!.LeaseGeneration, Is.EqualTo(2));
        }

        [Test] public void LocalReactorSenderUsesCurrentCoreStateWithoutRepeatingStartupCost()
        {
            var fixture = new ReactorFixture(start: false);
            var port = new LocalCommandPort(fixture.World, fixture.Connection); fixture.World.Start();
            Assert.That(port.Grab(fixture.Box).HasNewCommit, Is.True);
            Assert.That(port.OperateReactor(fixture.Reactor, ReactorAction.Insert, fixture.Box).HasNewCommit, Is.True);
            Assert.That(port.OperateReactor(fixture.Reactor, ReactorAction.SetCooling, cooling: true).HasNewCommit, Is.True);
            Assert.That(port.OperateReactor(fixture.Reactor, ReactorAction.Start).HasNewCommit, Is.True);
            fixture.World.AdvanceTo(100);
            var power = port.Power!;
            long spent = power.Spent, delivered = power.Delivered;
            Assert.That(port.ReplayLast().IsReplay, Is.True);
            var afterReplay = port.Power!;
            Assert.That(afterReplay.Spent, Is.EqualTo(spent)); Assert.That(afterReplay.Delivered, Is.EqualTo(delivered));
            Assert.That(port.OperateReactor(fixture.Reactor, ReactorAction.Shutdown).HasNewCommit, Is.True);
        }
    }
}
