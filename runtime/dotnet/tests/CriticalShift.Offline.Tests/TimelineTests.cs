using System;
using CriticalShift.Features.Session.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class TimelineTests
    {
        private static SessionTimeline Timeline(long duration = 10000, bool pause = true) =>
            new SessionTimeline(Fixture.Id(500), 42, duration, pause);

        [Test]
        public void TimelineStartsAtSuppliedOriginWithoutChargingLobby()
        {
            var t = Timeline();
            Assert.That(t.Phase, Is.EqualTo(TimelinePhase.Setup));
            Assert.That(t.Seed, Is.EqualTo(42));
            t.Start(1000000);
            Assert.That(t.ElapsedMilliseconds, Is.Zero);
            t.AdvanceTo(1000123);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(123));
            Assert.That(t.RemainingMilliseconds, Is.EqualTo(9877));
        }

        [Test]
        public void TimelineRejectsInvalidConstruction()
        {
            Assert.Throws<ArgumentException>(() => new SessionTimeline(Guid.Empty, 0, 1));
            Assert.Throws<ArgumentOutOfRangeException>(() => Timeline(0));
            Assert.Throws<ArgumentOutOfRangeException>(() => Timeline(-1));
            var t = Timeline();
            Assert.Throws<ArgumentOutOfRangeException>(() => t.Start(-1));
            Assert.That(t.Phase, Is.EqualTo(TimelinePhase.Setup));
            t.Start(0);
        }

        [Test]
        public void TimelineCannotStartTwiceOrAfterStop()
        {
            var t = Timeline(); t.Start(0);
            Assert.Throws<InvalidOperationException>(() => t.Start(0));
            t.Stop();
            Assert.Throws<InvalidOperationException>(() => t.Start(0));
            Assert.Throws<InvalidOperationException>(() => t.AdvanceTo(1));
        }

        [Test]
        public void TimelinePauseDoesNotCatchUpOnResume()
        {
            var t = Timeline(); t.Start(100); t.AdvanceTo(600);
            Assert.That(t.TryPause(), Is.True);
            Assert.That(t.TryPause(), Is.False);
            t.AdvanceTo(100000);
            Assert.That(t.HostMilliseconds, Is.EqualTo(100000));
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(500));
            Assert.That(t.TryResume(), Is.True);
            Assert.That(t.TryResume(), Is.False);
            t.AdvanceTo(100250);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(750));
        }

        [Test]
        public void TimelinePauseRequiresOptIn()
        {
            var t = Timeline(pause: false); t.Start(0);
            Assert.That(t.TryPause(), Is.False);
            t.AdvanceTo(100);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(100));
        }

        [Test]
        public void TimelineBackwardsSamplePreservesState()
        {
            var t = Timeline(); t.Start(10); t.AdvanceTo(100);
            Assert.Throws<ArgumentOutOfRangeException>(() => t.AdvanceTo(99));
            Assert.That(t.HostMilliseconds, Is.EqualTo(100));
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(90));
            Assert.That(t.Phase, Is.EqualTo(TimelinePhase.Running));
        }

        [Test]
        public void TimelineDuplicateSamplesAreNoOps()
        {
            var t = Timeline(); t.Start(0);
            for (int i = 0; i < 100; i++) Assert.That(t.AdvanceTo(100), Is.False);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(100));
        }

        [Test]
        public void TimelineLargeJumpClampsSafely()
        {
            var t = Timeline(long.MaxValue); t.Start(0);
            Assert.That(t.AdvanceTo(long.MaxValue), Is.True);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(long.MaxValue));
            Assert.That(t.RemainingMilliseconds, Is.Zero);
            var shortShift = Timeline(3); shortShift.Start(1); shortShift.AdvanceTo(long.MaxValue);
            Assert.That(shortShift.ElapsedMilliseconds, Is.EqualTo(3));
        }

        [TestCase(TimelineOutcome.Succeeded)]
        [TestCase(TimelineOutcome.Failed)]
        [TestCase(TimelineOutcome.Aborted)]
        [TestCase(TimelineOutcome.HostLost)]
        public void TimelineFinishIsSticky(TimelineOutcome outcome)
        {
            var t = Timeline(); t.Start(0); t.AdvanceTo(100);
            Assert.That(t.TryFinish(outcome), Is.True);
            Assert.That(t.TryFinish(TimelineOutcome.Failed), Is.False);
            t.Fault(); t.Stop(); t.Stop();
            Assert.That(t.Outcome, Is.EqualTo(outcome));
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(100));
        }

        [Test]
        public void TimelineTimeoutWinsAndCannotBeRewritten()
        {
            var t = Timeline(100); t.Start(0);
            Assert.That(t.AdvanceTo(99), Is.False);
            Assert.That(t.AdvanceTo(100), Is.True);
            Assert.That(t.TryFinish(TimelineOutcome.Succeeded), Is.False);
            Assert.That(t.TryPause(), Is.False);
            Assert.That(t.Outcome, Is.EqualTo(TimelineOutcome.TimedOut));
        }

        [TestCase(TimelineOutcome.None)]
        [TestCase(TimelineOutcome.TimedOut)]
        [TestCase(TimelineOutcome.Faulted)]
        [TestCase((TimelineOutcome)99)]
        public void TimelineInvalidOutcomesDoNotEndShift(TimelineOutcome outcome)
        {
            var t = Timeline(); t.Start(0);
            Assert.Throws<ArgumentOutOfRangeException>(() => t.TryFinish(outcome));
            Assert.That(t.Phase, Is.EqualTo(TimelinePhase.Running));
            Assert.That(t.Outcome, Is.EqualTo(TimelineOutcome.None));
        }

        [Test]
        public void TimelineStopAndFaultHaveExplicitOutcomes()
        {
            var stopped = Timeline(); stopped.Stop(); stopped.Fault();
            Assert.That(stopped.Outcome, Is.EqualTo(TimelineOutcome.Aborted));
            var faulted = Timeline(); faulted.Start(0); faulted.Fault();
            Assert.That(faulted.Phase, Is.EqualTo(TimelinePhase.Faulted));
            Assert.That(faulted.Outcome, Is.EqualTo(TimelineOutcome.Faulted));
            faulted.Stop(); Assert.That(faulted.Outcome, Is.EqualTo(TimelineOutcome.Faulted));
        }

        [TestCase(1)]
        [TestCase(10)]
        [TestCase(100)]
        public void ClockChunkingDoesNotChangeElapsedTime(int step)
        {
            var t = Timeline(); t.Start(0);
            for (int time = step; time <= 1000; time += step) t.AdvanceTo(time);
            Assert.That(t.ElapsedMilliseconds, Is.EqualTo(1000));
            Assert.That(t.RemainingMilliseconds, Is.EqualTo(9000));
        }
    }
}
