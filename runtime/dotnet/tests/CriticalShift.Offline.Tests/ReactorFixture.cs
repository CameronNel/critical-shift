using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    internal sealed class ReactorFixture
    {
        internal WorldSession World { get; }
        internal Guid Box => Fixture.Id(30);
        internal Guid Reactor => Fixture.Id(90);
        internal Guid Connection => Fixture.Id(20);
        internal Guid Actor => Fixture.Id(10);
        internal long Sequence { get; private set; }
        internal ReactorFixture(int units = 10, int contamination = 0, long shift = 100000,
            ReactorDefinition? definition = null, bool start = true, MaterialKind kind = MaterialKind.Fuel,
            int cycles = 1024, int receipts = 256, IInteractionAccessPolicy? policy = null)
        {
            World = new WorldSession(new WorldSessionConfiguration(42, shift, true, receiptCapacity: receipts),
                policy ?? new TestAccess(), maxProductionCycles: cycles);
            World.RegisterConnection(Connection, Actor); World.RegisterConnection(Fixture.Id(21), Fixture.Id(11));
            World.Production.RegisterBatch(Box, Fixture.Id(60), Fixture.Id(70), Fixture.Id(80), kind, units, contamination: contamination);
            World.Reactor.Register(Reactor, definition ?? new ReactorDefinition(Fixture.Id(91)));
            if (start) World.Start();
        }
        internal InteractionReply Send(ReactorRequest request) => World.ExecuteInteraction(Connection,
            new InteractionCommand(World.Epoch, ++Sequence, InteractionKind.Reactor, Reactor, reactor: request));
        internal InteractionReply Act(ReactorAction action, bool cooling = false, Guid? box = null)
        {
            var id = box ?? Box; var item = World.GetObject(id)!;
            return Send(new ReactorRequest(action, World.Reactor.View!.Revision,
                action == ReactorAction.Insert ? id : Guid.Empty,
                action == ReactorAction.Insert || action == ReactorAction.Eject ? item.Revision : 0,
                action == ReactorAction.Insert ? World.Production.GetBatch(id)!.Revision : 0,
                action == ReactorAction.Insert ? item.LeaseGeneration : 0, cooling));
        }
        internal InteractionReply Grab(Guid? box = null)
        {
            var id = box ?? Box;
            return World.ExecuteInteraction(Connection, new InteractionCommand(World.Epoch, ++Sequence,
                InteractionKind.Grab, id, World.GetObject(id)!.Revision));
        }
        internal void Load()
        {
            Assert.That(Grab().HasNewCommit, Is.True);
            Assert.That(Act(ReactorAction.Insert).HasNewCommit, Is.True);
        }
        internal void Run()
        {
            Load(); Assert.That(Act(ReactorAction.SetCooling, true).HasNewCommit, Is.True);
            Assert.That(Act(ReactorAction.Start).HasNewCommit, Is.True);
        }
        internal InteractionReply Production(ProductionAction action, int machine, bool bypass = false)
        {
            var item = World.GetObject(Box)!;
            var request = new ProductionRequest(action, World.Production.GetMachine(Fixture.Id(machine))!.Revision,
                action == ProductionAction.Insert ? Box : Guid.Empty,
                action == ProductionAction.Insert || action == ProductionAction.Eject ? item.Revision : 0,
                action == ProductionAction.Insert || action == ProductionAction.Start ? World.Production.GetBatch(Box)!.Revision : 0,
                action == ProductionAction.Insert ? item.LeaseGeneration : 0, bypass);
            return World.ExecuteInteraction(Connection, new InteractionCommand(World.Epoch, ++Sequence,
                InteractionKind.Production, Fixture.Id(machine), production: request));
        }
    }
}
