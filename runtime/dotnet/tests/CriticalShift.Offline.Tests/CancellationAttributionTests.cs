using System.Linq;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class CancellationAttributionTests
    {
        [Test]
        public void CancelledJammedCycleKeepsItsIdentityInThePublicTrace()
        {
            var f = new ProductionFixture(moisture: 900);
            f.Load();
            var cycle = f.Act(ProductionAction.Start, bypass: true).Production!.Machine!.CycleId;
            f.World.AdvanceTo(500);
            f.Act(ProductionAction.SetPower, power: false);
            Assert.That(f.Act(ProductionAction.CancelCycle).HasNewCommit, Is.True);
            var record = f.World.Trace.Records.Last();
            Assert.That(record.CycleId, Is.EqualTo(cycle), "Resetting the machine must not erase the cancelled cycle.");
            Assert.That(record.ProductionEvent, Is.EqualTo(ProductionEvent.Cancelled));
            Assert.That(record.MaterialCauseId, Is.EqualTo(Fixture.Id(80)));
            Assert.That(record.OutputBatchId, Is.EqualTo(System.Guid.Empty));
            Assert.That(f.World.Production.GetBatch(f.Box)!.Units, Is.EqualTo(100));
            Assert.That(f.World.Production.Summary.WasteUnits, Is.Zero);
        }
    }
}
