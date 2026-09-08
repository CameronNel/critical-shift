using System;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Offline.Tests
{
    // Existing single-hazard fixtures use one explicit test source. Multi-hazard cases pass IDs directly.
    // This convenience adapter exists only in tests, never in a production assembly.
    internal static class TestHazards
    {
        internal static WorkerResult Impact(this WorkerState worker, long sequence, ImpactSeverity severity, long delay, long now) =>
            worker.Impact(sequence, severity, delay, now, Fixture.Id(800), Fixture.Id(900));
        internal static WorkerReply ApplyWorkerImpact(this WorldSession world, Guid epoch, Guid actor, long sequence, WorkerImpact severity, long delay) =>
            world.ApplyWorkerImpact(epoch, actor, sequence, severity, delay, Fixture.Id(800), Fixture.Id(900));
    }
}
