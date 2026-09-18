using System;

namespace CriticalShift.Features.Production.Domain
{
    public enum MachineMode { Idle, Processing, PowerPaused, Jammed, OutputReady }
    public enum MachineSignal { None, Jammed, Completed }

    /// <summary>Immutable process state. Returned replacements are installed by the Application workflow.</summary>
    public sealed class MachineState
    {
        public MachineState(Guid id)
        {
            if (id == Guid.Empty) throw new ArgumentException("Machine identity is required.", nameof(id));
            Id = id; Powered = true;
        }
        private MachineState(MachineState old, MachineMode mode, bool power, long revision, Guid cycle,
            long duration, long work, long lastTime, long jamAt, bool jamArmed)
        {
            Id = old.Id; Mode = mode; Powered = power; Revision = revision; CycleId = cycle;
            DurationMilliseconds = duration; WorkMilliseconds = work; LastSampleMilliseconds = lastTime;
            JamAtMilliseconds = jamAt; JamArmed = jamArmed;
        }
        public Guid Id { get; }
        public MachineMode Mode { get; }
        public bool Powered { get; }
        public long Revision { get; }
        public Guid CycleId { get; }
        public long DurationMilliseconds { get; }
        public long WorkMilliseconds { get; }
        public long LastSampleMilliseconds { get; }
        public long JamAtMilliseconds { get; }
        public bool JamArmed { get; }
        public bool CanStart => Mode == MachineMode.Idle && Powered;
        public bool CanEject => Mode == MachineMode.Idle || Mode == MachineMode.OutputReady;
        public bool CanCancel => !Powered && (Mode == MachineMode.Processing || Mode == MachineMode.PowerPaused || Mode == MachineMode.Jammed);

        public MachineState Begin(Guid cycle, long duration, long jamAt, long now)
        {
            if (!CanStart) throw new InvalidOperationException("Machine is not ready.");
            if (cycle == Guid.Empty || duration < 1 || jamAt < 0 || jamAt >= duration || now < LastSampleMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(duration));
            return Copy(MachineMode.Processing, Powered, cycle, duration, 0, now, jamAt, jamAt > 0);
        }
        public MachineState AdvanceTo(long now, out MachineSignal signal)
        {
            if (now < LastSampleMilliseconds) throw new ArgumentOutOfRangeException(nameof(now));
            signal = MachineSignal.None;
            if (now == LastSampleMilliseconds) return this;
            long delta = Mode == MachineMode.Processing ? Math.Min(now - LastSampleMilliseconds, DurationMilliseconds - WorkMilliseconds) : 0;
            long work = WorkMilliseconds + delta;
            var mode = Mode;
            if (Mode == MachineMode.Processing && JamArmed && work >= JamAtMilliseconds)
            { work = JamAtMilliseconds; mode = MachineMode.Jammed; signal = MachineSignal.Jammed; }
            else if (Mode == MachineMode.Processing && work == DurationMilliseconds)
            { mode = MachineMode.OutputReady; signal = MachineSignal.Completed; }
            // Updating an idle clock coordinate is not a gameplay mutation requiring a revision.
            long revision = work != WorkMilliseconds || mode != Mode ? checked(Revision + 1) : Revision;
            return new MachineState(this, mode, Powered, revision, CycleId, DurationMilliseconds, work, now, JamAtMilliseconds, JamArmed);
        }
        public MachineState SetPower(bool power)
        {
            if (power == Powered) return this;
            return Copy(!power && Mode == MachineMode.Processing ? MachineMode.PowerPaused : Mode,
                power, CycleId, DurationMilliseconds, WorkMilliseconds, LastSampleMilliseconds, JamAtMilliseconds, JamArmed);
        }
        public MachineState Resume()
        {
            if (!Powered || Mode != MachineMode.PowerPaused) throw new InvalidOperationException("Cannot resume this machine.");
            return Copy(MachineMode.Processing, Powered, CycleId, DurationMilliseconds, WorkMilliseconds,
                LastSampleMilliseconds, JamAtMilliseconds, JamArmed);
        }
        public MachineState Repair()
        {
            if (Powered || Mode != MachineMode.Jammed) throw new InvalidOperationException("Repair requires isolated power and a jam.");
            return Copy(MachineMode.PowerPaused, Powered, CycleId, DurationMilliseconds, WorkMilliseconds,
                LastSampleMilliseconds, JamAtMilliseconds, false);
        }
        public MachineState Reset(bool cancel)
        {
            if (cancel ? !CanCancel : !CanEject) throw new InvalidOperationException("Unsafe machine reset.");
            return Copy(MachineMode.Idle, Powered, Guid.Empty, 0, 0, LastSampleMilliseconds, 0, false);
        }
        public MachineState Touch() => Copy(Mode, Powered, CycleId, DurationMilliseconds,
            WorkMilliseconds, LastSampleMilliseconds, JamAtMilliseconds, JamArmed);
        private MachineState Copy(MachineMode mode, bool power, Guid cycle, long duration, long work, long time, long jamAt, bool armed) =>
            new MachineState(this, mode, power, checked(Revision + 1), cycle, duration, work, time, jamAt, armed);
    }
}
