using System;

namespace CriticalShift.Features.Session.Domain
{
    public enum TimelinePhase { Setup, Running, Paused, Ended, Stopped, Faulted }
    public enum TimelineOutcome { None, Succeeded, Failed, TimedOut, Aborted, HostLost, Faulted }

    /// <summary>
    /// One shift's state and two clock coordinates. No clock is read here: the trusted host
    /// supplies nonnegative, monotonic milliseconds. All calls belong to one simulation thread.
    /// </summary>
    public sealed class SessionTimeline
    {
        public SessionTimeline(Guid epoch, int seed, long durationMilliseconds, bool allowPause = false)
        {
            if (epoch == Guid.Empty) throw new ArgumentException("An epoch is required.", nameof(epoch));
            if (durationMilliseconds <= 0) throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            Epoch = epoch;
            Seed = seed;
            DurationMilliseconds = durationMilliseconds;
            AllowPause = allowPause;
        }

        public Guid Epoch { get; }
        public int Seed { get; }
        public long DurationMilliseconds { get; }
        public bool AllowPause { get; }
        public TimelinePhase Phase { get; private set; }
        public TimelineOutcome Outcome { get; private set; }
        public long HostMilliseconds { get; private set; }
        public long ElapsedMilliseconds { get; private set; }
        public long RemainingMilliseconds => DurationMilliseconds - ElapsedMilliseconds;
        public bool IsActive => Phase == TimelinePhase.Running || Phase == TimelinePhase.Paused;

        public void Start(long hostMilliseconds)
        {
            if (Phase != TimelinePhase.Setup) throw new InvalidOperationException("A timeline can start only once.");
            ValidateTime(hostMilliseconds);
            // Lobby time is not charged to the shift. This sample establishes the running origin.
            HostMilliseconds = hostMilliseconds;
            Phase = TimelinePhase.Running;
        }

        /// <returns>True only on the advancement that first reaches the shift deadline.</returns>
        public bool AdvanceTo(long hostMilliseconds)
        {
            if (!IsActive) throw new InvalidOperationException("The timeline is not active.");
            ValidateTime(hostMilliseconds);
            long delta = hostMilliseconds - HostMilliseconds;
            if (Phase == TimelinePhase.Running)
            {
                // Clamp before addition: a large host jump cannot overflow the shift clock.
                ElapsedMilliseconds += Math.Min(delta, RemainingMilliseconds);
            }
            HostMilliseconds = hostMilliseconds;
            if (ElapsedMilliseconds != DurationMilliseconds) return false;
            Phase = TimelinePhase.Ended;
            Outcome = TimelineOutcome.TimedOut;
            return true;
        }

        // Controls take effect at the last processed host sample. Call AdvanceTo before controls
        // when applying newly sampled time; pause/resume never silently drain scheduled events.
        public bool TryPause()
        {
            if (!AllowPause || Phase != TimelinePhase.Running) return false;
            Phase = TimelinePhase.Paused;
            return true;
        }

        public bool TryResume()
        {
            if (Phase != TimelinePhase.Paused) return false;
            Phase = TimelinePhase.Running;
            return true;
        }

        public bool TryFinish(TimelineOutcome outcome)
        {
            if (outcome != TimelineOutcome.Succeeded && outcome != TimelineOutcome.Failed &&
                outcome != TimelineOutcome.Aborted && outcome != TimelineOutcome.HostLost)
                throw new ArgumentOutOfRangeException(nameof(outcome), "Timeout and fault are owned by their transition paths.");
            if (!IsActive) return false;
            Outcome = outcome;
            Phase = TimelinePhase.Ended;
            return true;
        }

        public void Stop()
        {
            if (Phase == TimelinePhase.Stopped) return;
            if (Outcome == TimelineOutcome.None) Outcome = TimelineOutcome.Aborted;
            Phase = TimelinePhase.Stopped;
        }

        public void Fault()
        {
            // An already published terminal result is immutable.
            if (Outcome != TimelineOutcome.None) return;
            Outcome = TimelineOutcome.Faulted;
            Phase = TimelinePhase.Faulted;
        }

        private void ValidateTime(long value)
        {
            if (value < HostMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(value), "Host time must be nonnegative and monotonic.");
        }
    }
}
