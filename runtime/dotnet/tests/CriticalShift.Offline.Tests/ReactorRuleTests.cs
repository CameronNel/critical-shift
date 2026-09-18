using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Features.Power.Domain;
using CriticalShift.Features.Reactor.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class ReactorRuleTests
    {
        public static IEnumerable<int> Seeds => Enumerable.Range(1, 100);

        [TestCaseSource(nameof(Seeds))]
        public void CoreSafeMatchesIndependentClockModel(int seed)
        {
            int units = 1 + seed % 70;
            var core = new ReactorCore(new ReactorRules()).Load(units, false).SetCooling(true).Start();
            uint random = (uint)seed; long now = 0, quanta = 0;
            for (int i = 0; i < 200; i++)
            {
                random ^= random << 13; random ^= random >> 17; random ^= random << 5;
                now += random % 91;
                var step = core.AdvanceTo(now); quanta += step.Quanta; core = step.State;
                long expectedWork = Math.Min(now, units * 100L);
                Assert.That(core.WorkMilliseconds, Is.EqualTo(expectedWork), $"seed={seed},step={i}");
                Assert.That(quanta, Is.EqualTo(expectedWork / 100));
                Assert.That(core.RemainingFuelMilliseconds, Is.EqualTo(units * 100L - expectedWork));
                Assert.That(core.InstabilityMilliseconds, Is.Zero);
                Assert.That(core.Mode, Is.EqualTo(expectedWork == units * 100L ? CoreMode.Exhausted : CoreMode.Running));
            }
        }

        [TestCase(false)] [TestCase(true)]
        public void CoreTripTimingIndependentOfClockPartition(bool lostCooling)
        {
            var initial = new ReactorCore(new ReactorRules()).Load(100, !lostCooling).SetCooling(true).Start();
            if (lostCooling) initial = initial.SetCooling(false);
            var direct = initial.AdvanceTo(2000);
            var core = initial; long sum = 0; var warnings = new List<long>(); var trips = new List<long>();
            foreach (long time in new long[] { 3, 99, 399, 400, 799, 800, 1201, 2000 })
            {
                var step = core.AdvanceTo(time); core = step.State; sum += step.Quanta;
                if (step.WarningAt.HasValue) warnings.Add(step.WarningAt.Value);
                if (step.StoppedAt.HasValue) trips.Add(step.StoppedAt.Value);
            }
            Assert.That(warnings, Is.EqualTo(new long[] { 400 }));
            Assert.That(trips, Is.EqualTo(new long[] { 800 }));
            Assert.That(sum, Is.EqualTo(direct.Quanta));
            Assert.That(core.Mode, Is.EqualTo(CoreMode.Tripped));
            Assert.That(core.WorkMilliseconds, Is.EqualTo(direct.State.WorkMilliseconds));
            Assert.That(core.InstabilityMilliseconds, Is.EqualTo(direct.State.InstabilityMilliseconds));
        }

        [Test] public void CoreExhaustionPrecedesTripOnExactTie()
        {
            var core = new ReactorCore(new ReactorRules()).Load(8, true).SetCooling(true).Start();
            var step = core.AdvanceTo(800);
            Assert.That(step.State.Mode, Is.EqualTo(CoreMode.Exhausted));
            Assert.That(step.Quanta, Is.EqualTo(8));
            Assert.That(step.State.CanEject, Is.False, "Unstable spent fuel remains interlocked.");
            Assert.That(step.State.AdvanceTo(1500).State.CanEject, Is.True);
        }

        [Test] public void CoreRejectsBackwardsTimeWithoutMutation()
        {
            var core = new ReactorCore(new ReactorRules()).AdvanceTo(100).State;
            Assert.Throws<ArgumentOutOfRangeException>(() => core.AdvanceTo(99));
            Assert.That(core.SampleMilliseconds, Is.EqualTo(100));
            Assert.That(core.AdvanceTo(100).State, Is.SameAs(core));
        }

        [Test] public void CoreCooldownRequiresExplicitTripResetAndRestart()
        {
            var core = new ReactorCore(new ReactorRules()).Load(100, true).SetCooling(true).Start().AdvanceTo(2000).State;
            Assert.That(core.Mode, Is.EqualTo(CoreMode.Tripped));
            Assert.That(core.InstabilityMilliseconds, Is.Zero);
            Assert.That(core.CanStart, Is.False);
            var reset = core.ResetTrip();
            Assert.That(reset.Mode, Is.EqualTo(CoreMode.Shutdown));
            Assert.That(reset.Start().WorkMilliseconds, Is.EqualTo(800));
        }

        [Test] public void CoreDoesNotBurnBeforeStart()
        {
            var core = new ReactorCore(new ReactorRules()).AdvanceTo(10000).State.Load(10, false);
            core = core.AdvanceTo(20000).State.SetCooling(true).Start();
            Assert.That(core.AdvanceTo(20100).State.WorkMilliseconds, Is.EqualTo(100));
        }

        [Test] public void InvalidReactorDefinitionsAreRejected()
        {
            Assert.Throws<ArgumentException>(() => new ReactorDefinition(Guid.Empty));
            Assert.Throws<ArgumentOutOfRangeException>(() => new ReactorDefinition(Fixture.Id(1), initialReserve: -1));
            Assert.Throws<ArgumentOutOfRangeException>(() => new ReactorDefinition(Fixture.Id(1), startupCost: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new ReactorRules(warningMilliseconds: 900));
            Assert.Throws<ArgumentOutOfRangeException>(() => new ReactorRules(powerQuantumMilliseconds: 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new ReactorRules(maximumFuelUnits: 10001));
            Assert.Throws<ArgumentNullException>(() => new ReactorCore(null!));
        }

        [Test] public void PowerAccountConservesCreditsAndSpend()
        {
            var power = new PowerAccount(10, 8).Credit(7, 20);
            Assert.That(power.Available, Is.EqualTo(10)); Assert.That(power.Spilled, Is.EqualTo(5));
            Assert.That(power.TrySpend(6, out var after), Is.True);
            Assert.That(after.Initial + after.Generated, Is.EqualTo(after.Available + after.Spent + after.Delivered + after.Spilled));
            Assert.That(after.Available, Is.EqualTo(4)); Assert.That(power.Available, Is.EqualTo(10));
        }

        [Test] public void PowerAccountRejectsInvalidAndUnfundedCosts()
        {
            var power = new PowerAccount(10, 0);
            Assert.That(power.TrySpend(1, out var after), Is.False); Assert.That(after, Is.SameAs(power));
            Assert.Throws<ArgumentOutOfRangeException>(() => power.TrySpend(0, out _));
            Assert.Throws<ArgumentOutOfRangeException>(() => power.Credit(-1, 0));
            Assert.Throws<OverflowException>(() => power.Credit(long.MaxValue, 1));
            Assert.That(power.Generated, Is.Zero);
        }

        [Test] public void ProcessAndGameplayAssembliesComposeWithoutCollision()
        {
            Assert.That(typeof(ProcessLifetime).Assembly.GetName().Name, Is.EqualTo("CriticalShift.ProcessLifetime"));
            Assert.That(typeof(WorldSession).Assembly.GetName().Name, Is.EqualTo("CriticalShift.Application"));
            var process = new ProcessLifetime(); process.MarkReady();
            for (int i = 0; i < 10; i++)
            {
                var world = new WorldSession(new WorldSessionConfiguration(i, 1000), new TestAccess());
                world.RegisterConnection(Fixture.Id(20), Fixture.Id(10)); world.Start(); world.Stop();
                Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped));
                Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Ready));
            }
            process.Stop(); Assert.That(process.Phase, Is.EqualTo(ProcessPhase.Stopped));
        }
    }
}
