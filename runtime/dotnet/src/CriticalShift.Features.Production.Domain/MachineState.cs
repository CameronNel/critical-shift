#nullable enable
using System;

namespace CriticalShift.Features.Production.Domain
{
    public enum MachineMode { Idle, Processing, PowerPaused, Jammed, OutputReady, Repairing }
    public enum MachineSignal { None, Jammed, Completed, RepairCompleted }

    /// <summary>Immutable process state. Returned replacements are installed by the Application workflow.</summary>
    public sealed class MachineState
    {
        public MachineState(Guid id)
        {
            if (id == Guid.Empty) throw new ArgumentException("Machine identity is required.", nameof(id));
            Id = id; Powered = true;
        }
        private MachineState(MachineState old, MachineMode mode, bool power, long revision, Guid cycle,
            long duration, long work, long lastTime, long jamAt, bool jamArmed, long repairDuration, long repairWork)
        {
            Id = old.Id; Mode = mode; Powered = power; Revision = revision; CycleId = cycle;
            DurationMilliseconds = duration; WorkMilliseconds = work; LastSampleMilliseconds = lastTime;
            JamAtMilliseconds = jamAt; JamArmed = jamArmed;
            RepairDurationMilliseconds = repairDuration; RepairWorkMilliseconds = repairWork;
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
        public long RepairDurationMilliseconds { get; }
        public long RepairWorkMilliseconds { get; }
        public bool CanStart => Mode == MachineMode.Idle && Powered;
        public bool CanEject => Mode == MachineMode.Idle || Mode == MachineMode.OutputReady;
        public bool CanCancel => !Powered && (Mode == MachineMode.Processing || Mode == MachineMode.PowerPaused || Mode == MachineMode.Jammed || Mode == MachineMode.Repairing);

        public MachineState Begin(Guid cycle, long duration, long jamAt, long now)
        {
            if (!CanStart) throw new InvalidOperationException("Machine is not ready.");
            if (cycle == Guid.Empty || duration < 1 || jamAt < 0 || jamAt >= duration || now < LastSampleMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(duration));
            return Copy(MachineMode.Processing, Powered, cycle, duration, 0, now, jamAt, jamAt > 0, 0, 0);
        }
        public MachineState AdvanceTo(long now, out MachineSignal signal)
        {
            if (now < LastSampleMilliseconds) throw new ArgumentOutOfRangeException(nameof(now));
            signal = MachineSignal.None;
            if (now == LastSampleMilliseconds) return this;
            long delta = Mode == MachineMode.Processing ? Math.Min(now - LastSampleMilliseconds, DurationMilliseconds - WorkMilliseconds) : 0;
            long work = WorkMilliseconds + delta;
            long repairDelta = Mode == MachineMode.Repairing ? Math.Min(now - LastSampleMilliseconds, RepairDurationMilliseconds - RepairWorkMilliseconds) : 0;
            long repairWork = RepairWorkMilliseconds + repairDelta;
            var mode = Mode;
            bool armed = JamArmed;
            if (Mode == MachineMode.Repairing && repairWork == RepairDurationMilliseconds)
            { mode = MachineMode.PowerPaused; armed = false; signal = MachineSignal.RepairCompleted; }
            else if (Mode == MachineMode.Processing && JamArmed && work >= JamAtMilliseconds)
            { work = JamAtMilliseconds; mode = MachineMode.Jammed; signal = MachineSignal.Jammed; }
            else if (Mode == MachineMode.Processing && work == DurationMilliseconds)
            { mode = MachineMode.OutputReady; signal = MachineSignal.Completed; }
            // Updating an idle clock coordinate is not a gameplay mutation requiring a revision.
            long revision = work != WorkMilliseconds || repairWork != RepairWorkMilliseconds || mode != Mode ? checked(Revision + 1) : Revision;
            return new MachineState(this, mode, Powered, revision, CycleId, DurationMilliseconds, work, now, JamAtMilliseconds, armed,
                RepairDurationMilliseconds, repairWork);
        }
        public MachineState SetPower(bool power)
        {
            if (power && Mode == MachineMode.Repairing) throw new InvalidOperationException("Keep power isolated during jam clearing.");
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
        public MachineState Repair(long durationMilliseconds = 0)
        {
            if (Powered || Mode != MachineMode.Jammed) throw new InvalidOperationException("Repair requires isolated power and a jam.");
            if (durationMilliseconds < 0 || durationMilliseconds > 60000) throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            return Copy(durationMilliseconds == 0 ? MachineMode.PowerPaused : MachineMode.Repairing, Powered, CycleId, DurationMilliseconds, WorkMilliseconds,
                LastSampleMilliseconds, JamAtMilliseconds, durationMilliseconds != 0 && JamArmed, durationMilliseconds, 0);
        }
        public MachineState Reset(bool cancel)
        {
            if (cancel ? !CanCancel : !CanEject) throw new InvalidOperationException("Unsafe machine reset.");
            return Copy(MachineMode.Idle, Powered, Guid.Empty, 0, 0, LastSampleMilliseconds, 0, false, 0, 0);
        }
        public MachineState Touch() => Copy(Mode, Powered, CycleId, DurationMilliseconds,
            WorkMilliseconds, LastSampleMilliseconds, JamAtMilliseconds, JamArmed);
        private MachineState Copy(MachineMode mode, bool power, Guid cycle, long duration, long work, long time, long jamAt, bool armed,
            long? repairDuration = null, long? repairWork = null) =>
            new MachineState(this, mode, power, checked(Revision + 1), cycle, duration, work, time, jamAt, armed,
                repairDuration ?? RepairDurationMilliseconds, repairWork ?? RepairWorkMilliseconds);
    }
}
