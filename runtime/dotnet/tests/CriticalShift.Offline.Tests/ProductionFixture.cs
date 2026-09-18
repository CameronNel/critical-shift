using System;
using CriticalShift.Application;

namespace CriticalShift.Offline.Tests
{
    internal sealed class ProductionFixture
    {
        internal WorldSession World { get; }
        internal Guid Box => Fixture.Id(30);
        internal Guid Machine => Fixture.Id(40);
        internal Guid Press => Fixture.Id(41);
        internal Guid Actor => Fixture.Id(10);
        internal Guid Connection => Fixture.Id(20);
        private long _sequence;
        internal ProductionFixture(int units = 100, int moisture = 0, int cycles = 1024,
            long shift = 20000, bool start = true, int maximum = 1000, int yield = 800,
            IInteractionAccessPolicy? policy = null)
        {
            World = new WorldSession(new WorldSessionConfiguration(42, shift, true), policy ?? new TestAccess(), maxProductionCycles: cycles);
            World.RegisterConnection(Connection, Actor);
            World.Production.RegisterMachine(Machine, new MachineRecipe(Fixture.Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, maximum, yield));
            World.Production.RegisterMachine(Press, new MachineRecipe(Fixture.Id(51), MaterialKind.CrushedOre, MaterialKind.Fuel, 1000, 500, 200, maximum, 750));
            World.Production.RegisterBatch(Box, Fixture.Id(60), Fixture.Id(70), Fixture.Id(80), MaterialKind.Ore, units, moisture, 35);
            if (start) World.Start();
        }
        internal InteractionReply Grab() => World.ExecuteInteraction(Connection, new InteractionCommand(World.Epoch,
            ++_sequence, InteractionKind.Grab, Box, World.GetObject(Box)!.Revision));
        internal InteractionReply Act(ProductionAction action, Guid? machine = null, bool bypass = false, bool power = false)
        {
            Guid id = machine ?? Machine;
            var item = World.GetObject(Box)!;
            var request = new ProductionRequest(action, World.Production.GetMachine(id)!.Revision,
                action == ProductionAction.Insert ? Box : Guid.Empty,
                action == ProductionAction.Insert || action == ProductionAction.Eject ? item.Revision : 0,
                action == ProductionAction.Insert || action == ProductionAction.Start ? World.Production.GetBatch(Box)!.Revision : 0,
                action == ProductionAction.Insert ? item.LeaseGeneration : 0, bypass, power);
            return World.ExecuteInteraction(Connection, new InteractionCommand(World.Epoch, ++_sequence, InteractionKind.Production, id, production: request));
        }
        internal void Load() { NUnit.Framework.Assert.That(Grab().HasNewCommit, NUnit.Framework.Is.True); NUnit.Framework.Assert.That(Act(ProductionAction.Insert).HasNewCommit, NUnit.Framework.Is.True); }
    }
}
