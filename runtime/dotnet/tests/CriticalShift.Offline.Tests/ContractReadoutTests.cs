using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ContractReadoutTests
    {
        private static WorldSession World()
        {
            var fixture = new ReactorFixture(shift: 6000, start: false);
            fixture.World.Contracts.Register(new ShiftContractDefinition(Fixture.Id(920), "City supply",
                new GridDemandWave(Fixture.Id(921), "Preparation", 2000, 0),
                new GridDemandWave(Fixture.Id(922), "Morning request", 4000, 10, 1000),
                new GridDemandWave(Fixture.Id(923), "Peak request", 6000, 20, 1000)));
            fixture.World.Start(); return fixture.World;
        }

        [Test] public void CompactContractShowsCurrentCountdownAndNoPrematureWarning()
        {
            var world = World(); string text = SandboxContractReadout.Compact(world.Contracts.View!);
            Assert.That(text, Does.Contain("City supply\nPreparation"));
            Assert.That(text, Does.Contain("0/0 energy · 00:02 left"));
            Assert.That(text, Does.Not.Contain("Next:")); Assert.That(text, Does.Not.Contain("Missed"));
            world.AdvanceTo(999);
            Assert.That(SandboxContractReadout.Upcoming(world.Contracts.View!), Is.Empty);
        }

        [Test] public void CompactContractShowsAuthoredNextWarningAcrossWindowBoundary()
        {
            var world = World(); world.AdvanceTo(1000);
            Assert.That(SandboxContractReadout.Compact(world.Contracts.View!), Does.Contain("Next: Morning request in 00:01 · 10 energy in that window"));
            world.AdvanceTo(2000);
            Assert.That(SandboxContractReadout.Progress(world.Contracts.View!), Does.Contain("Morning request · 0/10 energy · 00:02 left"));
            Assert.That(SandboxContractReadout.Upcoming(world.Contracts.View!), Is.Empty);
            world.AdvanceTo(3000);
            Assert.That(SandboxContractReadout.Upcoming(world.Contracts.View!), Does.Contain("Next: Peak request in 00:01"));
            world.AdvanceTo(4000);
            Assert.That(SandboxContractReadout.Upcoming(world.Contracts.View!), Is.Empty);
        }

        [Test] public void CompactContractReportsOnlySettledMissesAndLatestShortfall()
        {
            var world = World(); world.AdvanceTo(3000);
            Assert.That(SandboxContractReadout.LatestMissed(world.Contracts.View!), Is.Empty);
            world.AdvanceTo(4000);
            Assert.That(SandboxContractReadout.Compact(world.Contracts.View!), Does.Contain("Missed 1 window · Morning request short by 10 energy"));
            world.AdvanceTo(6000); string final = SandboxContractReadout.Compact(world.Contracts.View!);
            Assert.That(final, Does.Contain("Contract Failed"));
            Assert.That(final, Does.Contain("Missed 2 windows · Peak request short by 20 energy"));
            Assert.That(final, Does.Not.Contain("Next:"));
        }

        [TestCase(WorldEndReason.Aborted)]
        [TestCase(WorldEndReason.HostLost)]
        [TestCase(WorldEndReason.Failed)]
        public void TerminalCompactContractHidesFutureCountdowns(WorldEndReason reason)
        {
            var world = World(); world.AdvanceTo(1000);
            Assert.That(SandboxContractReadout.Upcoming(world.Contracts.View!), Is.Not.Empty);
            world.Finish(world.Epoch, reason); var snapshot = world.Contracts.View!;
            Assert.That(snapshot.Current, Is.Not.Null); // An early terminal contract can still have an unfinished current window.
            string text = SandboxContractReadout.Compact(snapshot);
            Assert.That(text, Does.Contain("Contract " + world.View.Outcome));
            Assert.That(text, Does.Not.Contain(" left")); Assert.That(text, Does.Not.Contain("Next:"));
        }

        [Test] public void ContractReadoutReadsFrozenSnapshotsAndPauseWithoutMutation()
        {
            var world = World(); var old = world.Contracts.View!;
            string oldText = SandboxContractReadout.Compact(old);
            world.AdvanceTo(1000); world.Pause(world.Epoch);
            string paused = SandboxContractReadout.Compact(world.Contracts.View!);
            world.AdvanceTo(1000000); long revision = world.View.Revision;
            for (int i = 0; i < 20; i++)
            {
                Assert.That(SandboxContractReadout.Compact(world.Contracts.View!), Is.EqualTo(paused));
                Assert.That(SandboxContractReadout.Compact(old), Is.EqualTo(oldText));
            }
            Assert.That(world.View.Revision, Is.EqualTo(revision));
        }
    }
}
