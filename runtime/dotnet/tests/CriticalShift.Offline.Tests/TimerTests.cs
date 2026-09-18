using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Features.Session.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class TimerTests
    {
        private static WorldTimerQueue Queue(int capacity = 8) => new WorldTimerQueue(Fixture.Id(500), capacity);
        private static TimerEntry Add(WorldTimerQueue queue, long delay, TimerClock clock = TimerClock.Simulation,
            int owner = 1, string signal = "warning")
        {
            Assert.That(queue.TrySchedule(Fixture.Id(owner), signal, clock, delay, out var entry), Is.True);
            return entry!;
        }

        [Test]
        public void TimerClocksAdvanceIndependently()
        {
            var q = Queue(); Add(q, 100, TimerClock.Host); Add(q, 100);
            Assert.That(q.AdvanceTo(100, 0).Select(x => x.Clock), Is.EqualTo(new[] { TimerClock.Host }));
            Assert.That(q.Count, Is.EqualTo(1));
            Assert.That(q.AdvanceTo(1000, 99), Is.Empty);
            Assert.That(q.AdvanceTo(1001, 100).Count, Is.EqualTo(1));
        }

        [Test]
        public void ZeroDelayWaitsForNextPoll()
        {
            var q = Queue(); var t = Add(q, 0);
            Assert.That(q.Count, Is.EqualTo(1));
            Assert.That(q.AdvanceTo(0, 0).Single().Sequence, Is.EqualTo(t.Sequence));
            Assert.That(q.AdvanceTo(0, 0), Is.Empty);
        }

        [Test]
        public void TimerBatchHasStableClockDeadlineAndSequenceOrder()
        {
            var q = Queue();
            var sLate = Add(q, 50); var sEarly = Add(q, 10); var hLate = Add(q, 40, TimerClock.Host);
            var hEarly = Add(q, 20, TimerClock.Host); var hTie = Add(q, 20, TimerClock.Host);
            Assert.That(q.AdvanceTo(100, 100).Select(x => x.Sequence),
                Is.EqualTo(new[] { hEarly.Sequence, hTie.Sequence, hLate.Sequence, sEarly.Sequence, sLate.Sequence }));
        }

        [Test]
        public void TimerDoesNotEmitTwice()
        {
            var q = Queue(); Add(q, 5);
            Assert.That(q.AdvanceTo(100, 100).Count, Is.EqualTo(1));
            for (int i = 0; i < 10; i++) Assert.That(q.AdvanceTo(100 + i, 100 + i), Is.Empty);
        }

        [Test]
        public void CancellationReusesCapacityNotIdentity()
        {
            var q = Queue(1); var old = Add(q, 0);
            Assert.That(q.Cancel(q.Epoch, old.Sequence), Is.True);
            Assert.That(q.Cancel(q.Epoch, old.Sequence), Is.False);
            var current = Add(q, 0);
            Assert.That(current.Sequence, Is.GreaterThan(old.Sequence));
            Assert.That(q.Cancel(q.Epoch, old.Sequence), Is.False);
            Assert.That(q.AdvanceTo(0, 0).Single().Sequence, Is.EqualTo(current.Sequence));
        }

        [Test]
        public void OwnerCancellationIsScoped()
        {
            var q = Queue(); Add(q, 0, owner: 1); Add(q, 0, owner: 1); var kept = Add(q, 0, owner: 2);
            Assert.That(q.CancelOwner(q.Epoch, Fixture.Id(1)), Is.EqualTo(2));
            Assert.That(q.CancelOwner(q.Epoch, Fixture.Id(1)), Is.Zero);
            Assert.That(q.AdvanceTo(0, 0).Single().Sequence, Is.EqualTo(kept.Sequence));
        }

        [Test]
        public void TimerCancellationRejectsOtherEpoch()
        {
            var q = Queue(); var t = Add(q, 1);
            Assert.That(q.Cancel(Fixture.Id(999), t.Sequence), Is.False);
            Assert.That(q.CancelOwner(Fixture.Id(999), t.OwnerId), Is.Zero);
            Assert.That(q.Count, Is.EqualTo(1));
        }

        [Test]
        public void TimerCapacityRejectsWithoutEvicting()
        {
            var q = Queue(1); var first = Add(q, 1);
            Assert.That(q.TrySchedule(Fixture.Id(1), "second", TimerClock.Host, 0, out var rejected), Is.False);
            Assert.That(rejected, Is.Null);
            Assert.That(q.AdvanceTo(1, 1).Single().Sequence, Is.EqualTo(first.Sequence));
        }

        [Test]
        public void TimerOverflowIsNonMutating()
        {
            var q = Queue(); q.AdvanceTo(long.MaxValue, long.MaxValue);
            Assert.Throws<OverflowException>(() => q.TrySchedule(Fixture.Id(1), "x", TimerClock.Host, 1, out _));
            Assert.That(q.Count, Is.Zero);
            Assert.That(Add(q, 0).Sequence, Is.EqualTo(1));
        }

        [Test]
        public void TimerInvalidRequestIsNonMutating()
        {
            var q = Queue();
            Assert.Throws<ArgumentException>(() => q.TrySchedule(Guid.Empty, "x", TimerClock.Host, 1, out _));
            foreach (string label in new[] { "", "  ", new string('x', 65) })
                Assert.Throws<ArgumentException>(() => q.TrySchedule(Fixture.Id(1), label, TimerClock.Host, 1, out _));
            Assert.Throws<ArgumentOutOfRangeException>(() => q.TrySchedule(Fixture.Id(1), "x", (TimerClock)99, 1, out _));
            Assert.Throws<ArgumentOutOfRangeException>(() => q.TrySchedule(Fixture.Id(1), "x", TimerClock.Host, -1, out _));
            Assert.That(q.Count, Is.Zero);
            Assert.That(Add(q, 0).Sequence, Is.EqualTo(1));
        }

        [TestCase(9, 11)]
        [TestCase(11, 9)]
        public void TimerBackwardsEitherClockIsAtomic(long host, long simulation)
        {
            var q = Queue(); q.AdvanceTo(10, 10); Add(q, 0);
            Assert.Throws<ArgumentOutOfRangeException>(() => q.AdvanceTo(host, simulation));
            Assert.That(q.HostMilliseconds, Is.EqualTo(10));
            Assert.That(q.SimulationMilliseconds, Is.EqualTo(10));
            Assert.That(q.Count, Is.EqualTo(1));
            Assert.That(q.AdvanceTo(10, 10).Count, Is.EqualTo(1));
        }

        [Test]
        public void TimerStopIsTerminalAndClears()
        {
            var q = Queue(); var t = Add(q, 0); q.Stop(); q.Stop();
            Assert.That(q.Count, Is.Zero);
            Assert.That(q.Cancel(q.Epoch, t.Sequence), Is.False);
            Assert.Throws<InvalidOperationException>(() => Add(q, 0));
            Assert.Throws<InvalidOperationException>(() => q.AdvanceTo(1, 1));
        }

        [Test]
        public void TimerSnapshotsAreReadonly()
        {
            var q = Queue(); var scheduled = Add(q, 0); var batch = q.AdvanceTo(0, 0);
            Assert.Throws<NotSupportedException>(() => ((IList<TimerEntry>)batch).Clear());
            foreach (var property in typeof(TimerEntry).GetProperties()) Assert.That(property.SetMethod, Is.Null);
            Assert.That(scheduled.Signal, Is.EqualTo("warning"));
        }

        [Test]
        public void TimerLargeJumpEmitsOnce()
        {
            var q = Queue(); for (int i = 0; i < 8; i++) Add(q, i);
            Assert.That(q.AdvanceTo(long.MaxValue, long.MaxValue).Count, Is.EqualTo(8));
            Assert.That(q.AdvanceTo(long.MaxValue, long.MaxValue), Is.Empty);
        }

        [Test]
        public void TimerQueueRejectsInvalidConstruction()
        {
            Assert.Throws<ArgumentException>(() => new WorldTimerQueue(Guid.Empty));
            Assert.Throws<ArgumentOutOfRangeException>(() => Queue(0));
            Assert.Throws<ArgumentOutOfRangeException>(() => Queue(4097));
        }

        public static IEnumerable<int> TimerSeeds => Enumerable.Range(1, 100);

        [TestCaseSource(nameof(TimerSeeds)), Category("TIMER-MODEL")]
        public void TimerModelFixedSequences(int seed)
        {
            // Independent list oracle. It never calls production scheduling or clock helpers.
            var q = Queue(8); var model = new List<(long Id, int Owner, int Clock, long Due)>();
            long host = 0, sim = 0, sequence = 0; uint random = (uint)seed;
            for (int step = 0; step < 200; step++)
            {
                random ^= random << 13; random ^= random >> 17; random ^= random << 5;
                int operation = (int)(random % 5), owner = (int)((random >> 4) % 3) + 1;
                string trace = $"timer seed={seed}, step={step}, operation={operation}";
                if (operation <= 1)
                {
                    int clock = operation; long delay = (random >> 8) % 100;
                    bool expected = model.Count < 8;
                    bool actual = q.TrySchedule(Fixture.Id(owner), "signal", (TimerClock)clock, delay, out var entry);
                    Assert.That(actual, Is.EqualTo(expected), trace);
                    if (expected)
                    {
                        sequence++;
                        model.Add((sequence, owner, clock, (clock == 0 ? host : sim) + delay));
                        Assert.That(entry!.Sequence, Is.EqualTo(sequence), trace);
                    }
                }
                else if (operation == 2)
                {
                    long id = sequence == 0 ? 1 : (random >> 8) % (sequence + 2);
                    bool expected = model.RemoveAll(x => x.Id == id) != 0;
                    Assert.That(q.Cancel(q.Epoch, id), Is.EqualTo(expected), trace);
                }
                else if (operation == 3)
                {
                    int removed = model.RemoveAll(x => x.Owner == owner);
                    Assert.That(q.CancelOwner(q.Epoch, Fixture.Id(owner)), Is.EqualTo(removed), trace);
                }
                else
                {
                    host += (random >> 8) % 101;
                    sim += (random & 0x10000) == 0 ? 0 : (random >> 20) % 51;
                    var due = model.Where(x => x.Due <= (x.Clock == 0 ? host : sim))
                        .OrderBy(x => x.Clock).ThenBy(x => x.Due).ThenBy(x => x.Id).ToArray();
                    Assert.That(q.AdvanceTo(host, sim).Select(x => x.Sequence), Is.EqualTo(due.Select(x => x.Id)), trace);
                    foreach (var item in due) model.Remove(item);
                }
                Assert.That(q.Count, Is.EqualTo(model.Count), trace);
            }
            q.Stop(); Assert.That(q.Count, Is.Zero);
        }
    }
}
