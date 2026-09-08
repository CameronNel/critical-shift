using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class HazardAttributionTests
    {
        [Test]
        public void IndependentHazardStreamsDoNotCollide()
        {
            var w = new WorkerState(Fixture.Id(1));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 10, 0, Fixture.Id(2), Fixture.Id(3)), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Impact(1, ImpactSeverity.Incapacitating, 20, 1, Fixture.Id(4), Fixture.Id(5)), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 10, 2, Fixture.Id(2), Fixture.Id(3)), Is.EqualTo(WorkerResult.Duplicate));
            Assert.That(w.Snapshot.LastHazardId, Is.EqualTo(Fixture.Id(4))); Assert.That(w.Snapshot.LastCauseId, Is.EqualTo(Fixture.Id(5)));
            Assert.That(w.Snapshot.Consciousness, Is.EqualTo(Consciousness.Unconscious));
        }
        [Test]
        public void HazardCauseIsPartOfReplayPayload()
        {
            var w = new WorkerState(Fixture.Id(1)); w.Impact(1, ImpactSeverity.Knockdown, 10, 0, Fixture.Id(2), Fixture.Id(3));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 10, 0, Fixture.Id(2), Fixture.Id(4)), Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(w.Snapshot.Revision, Is.EqualTo(1));
        }
        [Test]
        public void HazardSourceHistoryIsBoundedWithoutEvictingReplayProtection()
        {
            var w = new WorkerState(Fixture.Id(1));
            for (int i = 1; i <= WorkerState.HazardSourceCapacity; i++)
                Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 0, i, Fixture.Id(i), Fixture.Id(500)), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 0, 100, Fixture.Id(400), Fixture.Id(500)), Is.EqualTo(WorkerResult.SourceCapacityReached));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 0, 100, Fixture.Id(1), Fixture.Id(500)), Is.EqualTo(WorkerResult.Duplicate));
        }
        [Test]
        public void HazardTraceKeepsSourceCauseAndSeveritySeparateFromReleasedObject()
        {
            var f = new ProductionFixture(); f.Grab();
            var reply = f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Incapacitating, 10, Fixture.Id(800), Fixture.Id(900));
            var trace = f.World.Trace.Records.Last();
            Assert.That(trace.HazardId, Is.EqualTo(Fixture.Id(800))); Assert.That(trace.CauseId, Is.EqualTo(Fixture.Id(900)));
            Assert.That(trace.ImpactSeverity, Is.EqualTo(WorkerImpact.Incapacitating)); Assert.That(trace.EntityId, Is.EqualTo(f.Box));
            Assert.That(reply.Worker!.LastCauseId, Is.EqualTo(Fixture.Id(900)));
        }
        [Test]
        public void EmptyHazardIdentityIsRejectedWithoutReleasingCustody()
        {
            var f = new ProductionFixture(); f.Grab();
            Assert.That(f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Knockdown, 0, Guid.Empty, Fixture.Id(900)).Status,
                Is.EqualTo(WorkerStatus.InvalidInput));
            Assert.That(f.World.GetObject(f.Box)!.HolderId, Is.EqualTo(f.Actor));
        }
    }
}
