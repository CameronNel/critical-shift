using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Tests.EditMode
{
    public sealed class ProcessLifetimeTests
    {
        [Test] public void NewProcessStartsCreated() =>
            Assert.That(new ProcessLifetime().Phase, Is.EqualTo(ProcessPhase.Created));

        [Test] public void ReadyIsExplicit()
        {
            var process = new ProcessLifetime();
            process.MarkReady();
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Ready));
        }

        [Test] public void DuplicateReadyIsRejected()
        {
            var process = new ProcessLifetime();
            process.MarkReady();
            Assert.Throws<InvalidOperationException>(() => process.MarkReady());
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Ready));
        }

        [Test] public void StopBeforeReadyIsSafe()
        {
            var process = new ProcessLifetime();
            Assert.That(process.Stop(), Is.True);
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Stopped));
        }

        [Test] public void StopAfterReadyIsSafe()
        {
            var process = new ProcessLifetime();
            process.MarkReady();
            Assert.That(process.Stop(), Is.True);
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Stopped));
        }

        [Test] public void StopIsIdempotent()
        {
            var process = new ProcessLifetime();
            process.MarkReady();
            process.Stop();
            Assert.That(process.Stop(), Is.False);
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Stopped));
        }

        [Test] public void StoppedProcessCannotBecomeReady()
        {
            var process = new ProcessLifetime();
            process.Stop();
            Assert.Throws<InvalidOperationException>(() => process.MarkReady());
            Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Stopped));
        }

        [Test] public void RepeatedFreshProcessesDoNotShareState()
        {
            for (int i = 0; i < 10; i++)
            {
                var process = new ProcessLifetime();
                Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Created));
                process.MarkReady();
                process.Stop();
            }
            Assert.That(new ProcessLifetime().Phase, Is.EqualTo(ProcessPhase.Created));
        }
    }
}
