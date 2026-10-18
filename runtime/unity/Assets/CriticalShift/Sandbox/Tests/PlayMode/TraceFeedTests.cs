using System;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class TraceFeedTests
    {
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private sealed class FixtureAccess : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }

        private static WorldSession World(int traceCapacity = 128)
        {
            var world = new WorldSession(new WorldSessionConfiguration(7, 20000, true), new FixtureAccess(), traceCapacity: traceCapacity);
            world.RegisterConnection(Id(2), Id(1));
            world.Production.RegisterBatch(Id(10), Id(110), Id(120), Id(130), MaterialKind.Ore, 10, moisture: 850);
            world.Production.RegisterMachine(Id(20), new MachineRecipe(Id(500), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 100, 100));
            world.Reactor.Register(Id(30), new ReactorDefinition(Id(501))); return world;
        }

        [Test] public void WetJamRetainsItsRecordedCauseAndReplayCannotPublishItAgain()
        {
            var world = World(); var commands = new LocalCommandPort(world, Id(2)); var feed = new SandboxTraceFeed(commands);
            world.Start(); feed.Refresh();
            commands.Grab(Id(10)); commands.OperateMachine(Id(20), ProductionAction.Insert, Id(10));
            commands.OperateMachine(Id(20), ProductionAction.SetPower, powered: true);
            commands.OperateMachine(Id(20), ProductionAction.Start, bypass: true); world.AdvanceTo(150);
            feed.Refresh(); long revision = world.View.Revision; int jams = 0;
            foreach (var row in feed.Entries)
                if (row.Production == ProductionEvent.Jammed)
                { jams++; Assert.That(row.CauseId, Is.EqualTo(Id(130))); Assert.That(row.EntityId, Is.EqualTo(Id(20))); }
            Assert.That(jams, Is.EqualTo(1)); int count = feed.Entries.Count;
            commands.ReplayLast(); feed.Refresh(); feed.Refresh();
            Assert.That(feed.Entries.Count, Is.EqualTo(count)); Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(commands.GetBatch(Id(10)).Units, Is.EqualTo(10)); world.Stop();
        }

        [Test] public void SourceEvictionExposesAGapWithoutInventingAnIncident()
        {
            var world = World(4); var commands = new LocalCommandPort(world, Id(2)); var feed = new SandboxTraceFeed(commands);
            world.Start(); feed.Refresh(); int count = feed.Entries.Count;
            for (int i = 1; i <= 20; i++) world.AdvanceTo(i);
            long revision = world.View.Revision; feed.Refresh();
            Assert.That(feed.GapDetected, Is.True); Assert.That(feed.SourceDroppedRecords, Is.GreaterThan(0));
            Assert.That(feed.Entries.Count, Is.EqualTo(count)); Assert.That(world.View.Revision, Is.EqualTo(revision)); world.Stop();
        }

        [Test] public void GripDropsPublishOnceForBindingFailureAndLeaseExpiry()
        {
            var world = World(); var commands = new LocalCommandPort(world, Id(2)); var feed = new SandboxTraceFeed(commands);
            world.Start(); commands.Grab(Id(10)); var held = commands.GetObject(Id(10));
            world.ReportAttachmentFailure(world.Epoch, Id(10), held.LeaseGeneration); feed.Refresh();
            var drop = feed.Entries[feed.Entries.Count - 1];
            Assert.That(drop.Kind, Is.EqualTo(SessionTraceKind.AttachmentFailed)); Assert.That(drop.ActorId, Is.EqualTo(Id(1)));
            Assert.That(drop.EntityId, Is.EqualTo(Id(10))); Assert.That(drop.CauseId, Is.EqualTo(Guid.Empty));
            Assert.That(drop.Description, Does.Contain("Grip released")); int count = feed.Entries.Count;
            commands.Grab(Id(10)); long revision = world.View.Revision;
            world.ReportAttachmentFailure(world.Epoch, Id(10), held.LeaseGeneration); feed.Refresh(); feed.Refresh();
            Assert.That(feed.Entries.Count, Is.EqualTo(count)); Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(commands.GetObject(Id(10)).HolderId, Is.EqualTo(Id(1)));
            world.AdvanceTo(3000); feed.Refresh();
            Assert.That(feed.Entries.Count, Is.EqualTo(count + 1));
            drop = feed.Entries[feed.Entries.Count - 1];
            Assert.That(drop.Kind, Is.EqualTo(SessionTraceKind.LeaseExpired)); Assert.That(drop.EntityId, Is.EqualTo(Id(10)));
            Assert.That(drop.ActorId, Is.EqualTo(Guid.Empty)); Assert.That(drop.Description, Does.Contain("lease expired"));
            world.AdvanceTo(3000); feed.Refresh(); Assert.That(feed.Entries.Count, Is.EqualTo(count + 1)); world.Stop();
        }

        [Test] public void FeedStaysBoundedAndReadsTheStoppedWorldWithoutMutatingIt()
        {
            var world = World(); var commands = new LocalCommandPort(world, Id(2)); var feed = new SandboxTraceFeed(commands);
            world.Start();
            for (int i = 0; i < 40; i++) commands.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: i % 2 == 0);
            long revision = world.View.Revision; feed.Refresh();
            Assert.That(feed.Entries.Count, Is.EqualTo(12)); Assert.That(feed.GapDetected, Is.False);
            Assert.That(world.View.Revision, Is.EqualTo(revision)); world.Stop(); revision = world.View.Revision;
            feed.Refresh(); Assert.That(feed.Entries.Count, Is.EqualTo(12));
            Assert.That(feed.Entries[feed.Entries.Count - 1].Kind, Is.EqualTo(SessionTraceKind.Stopped));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(world.View.ActiveClaimCount, Is.Zero);
        }
    }
}
