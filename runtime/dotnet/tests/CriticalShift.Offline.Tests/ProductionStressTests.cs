using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ProductionStressTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private static MachineRecipe Crusher() => new MachineRecipe(Id(800), MaterialKind.Ore, MaterialKind.CrushedOre, 10, 5, 2, 1000, 800);
        private static MachineRecipe Press() => new MachineRecipe(Id(801), MaterialKind.CrushedOre, MaterialKind.Fuel, 10, 5, 2, 1000, 750);
        private static InteractionReply Command(WorldSession world, int actor, long sequence, int machine, ProductionAction action, int container = 0)
        {
            var claim = container == 0 ? null : world.GetObject(Id(container));
            var material = container == 0 ? null : world.Production.GetBatch(Id(container));
            var request = new ProductionRequest(action, world.Production.GetMachine(Id(machine))!.Revision,
                action == ProductionAction.Insert ? Id(container) : Guid.Empty,
                action == ProductionAction.Insert || action == ProductionAction.Eject ? claim!.Revision : 0,
                action == ProductionAction.Insert || action == ProductionAction.Start ? material!.Revision : 0,
                action == ProductionAction.Insert ? claim!.LeaseGeneration : 0);
            return world.ExecuteInteraction(Id(100 + actor), new InteractionCommand(world.Epoch, sequence,
                InteractionKind.Production, Id(machine), production: request));
        }
        private static InteractionReply Grab(WorldSession w, int actor, long sequence, int container) =>
            w.ExecuteInteraction(Id(100 + actor), new InteractionCommand(w.Epoch, sequence, InteractionKind.Grab,
                Id(container), w.GetObject(Id(container))!.Revision));
        private static void RegisterBatch(WorldSession w, int n) => w.Production.RegisterBatch(Id(n), Id(1000 + n), Id(900), Id(901), MaterialKind.Ore, 100);

        [Test]
        public void TwoPlayersLoadingOnePortLeaveTheLosingBatchHeldAndUnchanged()
        {
            var w = new WorldSession(new WorldSessionConfiguration(42, 100000), new TestAccess());
            w.RegisterConnection(Id(101), Id(1)); w.RegisterConnection(Id(102), Id(2));
            w.Production.RegisterMachine(Id(700), Crusher()); RegisterBatch(w, 600); RegisterBatch(w, 601); w.Start();
            Assert.That(Grab(w, 1, 1, 600).HasNewCommit, Is.True);
            Assert.That(Grab(w, 2, 1, 601).HasNewCommit, Is.True);
            Assert.That(Command(w, 1, 2, 700, ProductionAction.Insert, 600).HasNewCommit, Is.True);
            Assert.That(Command(w, 2, 2, 700, ProductionAction.Insert, 601).Production!.Status, Is.EqualTo(ProductionStatus.Occupied));
            Assert.That(w.GetObject(Id(600))!.SlotId, Is.EqualTo(Id(700)));
            Assert.That(w.GetObject(Id(601))!.HolderId, Is.EqualTo(Id(2)));
            Assert.That(w.Production.Summary.ActiveUnits, Is.EqualTo(200));
            Assert.That(w.View.ActiveClaimCount, Is.EqualTo(1));
            w.Stop();
        }
        [Test]
        public void ExpiredLeaseCannotInsertAndOldAttachmentCannotEjectSlottedMaterial()
        {
            var f = new ProductionFixture(); f.Grab(); f.World.AdvanceTo(3000);
            var stale = new ProductionRequest(ProductionAction.Insert, 0, f.Box, 1, 0, 1);
            var rejected = f.World.ExecuteInteraction(f.Connection, new InteractionCommand(f.World.Epoch, 2,
                InteractionKind.Production, f.Machine, production: stale));
            Assert.That(rejected.Status, Is.EqualTo(InteractionStatus.StaleLease));
            Assert.That(f.World.ExecuteInteraction(f.Connection, new InteractionCommand(f.World.Epoch, 3,
                InteractionKind.Grab, f.Box, 2)).HasNewCommit, Is.True);
            var valid = new ProductionRequest(ProductionAction.Insert, 0, f.Box, 3, 0, 2);
            Assert.That(f.World.ExecuteInteraction(f.Connection, new InteractionCommand(f.World.Epoch, 4,
                InteractionKind.Production, f.Machine, production: valid)).HasNewCommit, Is.True);
            Assert.That(f.World.ReportAttachmentFailure(f.World.Epoch, f.Box, 1).HasNewCommit, Is.False);
            Assert.That(f.World.ReportAttachmentFailure(f.World.Epoch, f.Box, 2).HasNewCommit, Is.False);
            Assert.That(f.World.GetObject(f.Box)!.SlotId, Is.EqualTo(f.Machine));
        }
        [Test]
        public void ProductionAccessDenialCannotTransferOrReserveMaterial()
        {
            var access = new TestAccess(); var f = new ProductionFixture(policy: access); f.Grab();
            access.Decision = AccessDecision.OutOfReach;
            Assert.That(f.Act(ProductionAction.Insert).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            access.Decision = AccessDecision.Allowed;
            Assert.That(f.Act(ProductionAction.Insert).HasNewCommit, Is.True);
        }
        [Test]
        public void HundredConversionsStayBalancedAfterReceiptEvictionAndRepeatTicks()
        {
            var w = new WorldSession(new WorldSessionConfiguration(42, 100000, receiptCapacity: 7),
                new TestAccess(), maxProductionCycles: 100);
            w.RegisterConnection(Id(101), Id(1)); w.Production.RegisterMachine(Id(700), Crusher()); w.Production.RegisterMachine(Id(702), Press());
            for (int n = 600; n < 650; n++) RegisterBatch(w, n);
            w.Start(); long seq = 0, time = 0;
            for (int n = 600; n < 650; n++)
            {
                foreach (int machine in new[] { 700, 702 })
                {
                    Assert.That(Grab(w, 1, ++seq, n).HasNewCommit, Is.True);
                    Assert.That(Command(w, 1, ++seq, machine, ProductionAction.Insert, n).HasNewCommit, Is.True);
                    Assert.That(Command(w, 1, ++seq, machine, ProductionAction.Start, n).HasNewCommit, Is.True);
                    Assert.That(w.AdvanceTo(time += 10).ProductionChanges.Count, Is.EqualTo(1));
                    Assert.That(w.AdvanceTo(time).ProductionChanges.Count, Is.Zero);
                    Assert.That(Command(w, 1, ++seq, machine, ProductionAction.Eject, n).HasNewCommit, Is.True);
                    Assert.That(w.Production.Summary.ActiveUnits + w.Production.Summary.WasteUnits, Is.EqualTo(5000));
                }
                Assert.That(w.Production.GetBatch(Id(n))!.Units, Is.EqualTo(60));
                Assert.That(w.Production.GetBatch(Id(n))!.Kind, Is.EqualTo(MaterialKind.Fuel));
            }
            Assert.That(w.Production.Summary.CompletedCycles, Is.EqualTo(100));
            Assert.That(w.Production.Summary.WasteUnits, Is.EqualTo(2000));
            Assert.That(w.Production.Summary.ActiveUnits, Is.EqualTo(3000));
            Assert.That(w.ExecuteInteraction(Id(101), new InteractionCommand(w.Epoch, 1, InteractionKind.Grab, Id(600))).Status,
                Is.EqualTo(InteractionStatus.TooOld));
            w.Stop();
            Assert.That(w.Production.BatchCount, Is.Zero); Assert.That(w.Production.MachineCount, Is.Zero);
            Assert.That(w.Production.Summary.CompletedCycles, Is.EqualTo(100));
        }
    }
}
