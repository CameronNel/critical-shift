using System;

namespace CriticalShift.Features.Reactor.Domain
{
    public enum CoreMode { Empty, Loaded, Running, Shutdown, Tripped, Exhausted }
    public enum CoreRisk { None, CoolingLost, SuspectFuel }

    /// <summary>Fictional control-loop fixtures, not reactor engineering or approved game balance.</summary>
    public sealed class ReactorRules
    {
        public ReactorRules(int maximumFuelUnits = 10000, long millisecondsPerFuelUnit = 100,
            long powerQuantumMilliseconds = 100, int reservePerQuantum = 1, int gridPerQuantum = 4,
            long warningMilliseconds = 400, long tripMilliseconds = 800,
            long resetMilliseconds = 100, long emergencyReliefMilliseconds = 400)
        {
            if (maximumFuelUnits < 1 || maximumFuelUnits > 10000 || millisecondsPerFuelUnit < 1 ||
                millisecondsPerFuelUnit > 60000 || powerQuantumMilliseconds < 1 ||
                powerQuantumMilliseconds > 60000 || reservePerQuantum < 0 || reservePerQuantum > 1000 ||
                gridPerQuantum < 1 || gridPerQuantum > 1000 || resetMilliseconds < 0 ||
                warningMilliseconds <= resetMilliseconds || tripMilliseconds <= warningMilliseconds ||
                tripMilliseconds > 3600000 || emergencyReliefMilliseconds < 1 ||
                emergencyReliefMilliseconds > tripMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(maximumFuelUnits));
            MaximumFuelUnits = maximumFuelUnits; MillisecondsPerFuelUnit = millisecondsPerFuelUnit;
            PowerQuantumMilliseconds = powerQuantumMilliseconds; ReservePerQuantum = reservePerQuantum;
            GridPerQuantum = gridPerQuantum; WarningMilliseconds = warningMilliseconds;
            TripMilliseconds = tripMilliseconds; ResetMilliseconds = resetMilliseconds;
            EmergencyReliefMilliseconds = emergencyReliefMilliseconds;
        }
        public int MaximumFuelUnits { get; }
        public long MillisecondsPerFuelUnit { get; }
        public long PowerQuantumMilliseconds { get; }
        public int ReservePerQuantum { get; }
        public int GridPerQuantum { get; }
        public long WarningMilliseconds { get; }
        public long TripMilliseconds { get; }
        public long ResetMilliseconds { get; }
        public long EmergencyReliefMilliseconds { get; }
    }

    public sealed class CoreAdvance
    {
        internal CoreAdvance(ReactorCore state, long quanta, long? warningAt, long? stoppedAt,
            CoreRisk risk, long activeUntil)
        { State = state; Quanta = quanta; WarningAt = warningAt; StoppedAt = stoppedAt; Risk = risk; ActiveUntil = activeUntil; }
        public ReactorCore State { get; }
        public long Quanta { get; }
        public long? WarningAt { get; }
        public long? StoppedAt { get; }
        public CoreRisk Risk { get; }
        public long ActiveUntil { get; }
    }

    /// <summary>Immutable operating state. One explicit shift clock; no physics or hidden timers.</summary>
    public sealed class ReactorCore
    {
        private readonly ReactorRules _rules;
        public ReactorCore(ReactorRules rules)
            : this(rules ?? throw new ArgumentNullException(nameof(rules)), CoreMode.Empty, false, false, 0, 0, 0, 0) { }
        private ReactorCore(ReactorRules rules, CoreMode mode, bool cooling, bool suspect,
            long duration, long work, long instability, long sample)
        {
            _rules = rules; Mode = mode; Cooling = cooling; SuspectFuel = suspect;
            FuelDurationMilliseconds = duration; WorkMilliseconds = work;
            InstabilityMilliseconds = instability; SampleMilliseconds = sample;
        }
        public CoreMode Mode { get; }
        public bool Cooling { get; }
        public bool SuspectFuel { get; }
        public long FuelDurationMilliseconds { get; }
        public long WorkMilliseconds { get; }
        public long RemainingFuelMilliseconds => FuelDurationMilliseconds - WorkMilliseconds;
        public long InstabilityMilliseconds { get; }
        public long SampleMilliseconds { get; }
        public bool CanStart => (Mode == CoreMode.Loaded || Mode == CoreMode.Shutdown) && Cooling &&
            RemainingFuelMilliseconds > 0 && InstabilityMilliseconds < _rules.WarningMilliseconds;
        public bool CanReset => Mode == CoreMode.Tripped && Cooling && InstabilityMilliseconds <= _rules.ResetMilliseconds;
        public bool CanEject => Mode == CoreMode.Loaded || (Mode == CoreMode.Exhausted && InstabilityMilliseconds <= _rules.ResetMilliseconds);

        private ReactorCore Copy(CoreMode? mode = null, bool? cooling = null, long? instability = null) =>
            new ReactorCore(_rules, mode ?? Mode, cooling ?? Cooling, SuspectFuel,
                FuelDurationMilliseconds, WorkMilliseconds, instability ?? InstabilityMilliseconds, SampleMilliseconds);

        public ReactorCore Load(int units, bool suspect)
        {
            if (Mode != CoreMode.Empty) throw new InvalidOperationException("Fuel slot is occupied.");
            if (units < 1 || units > _rules.MaximumFuelUnits) throw new ArgumentOutOfRangeException(nameof(units));
            return new ReactorCore(_rules, CoreMode.Loaded, Cooling, suspect,
                checked(units * _rules.MillisecondsPerFuelUnit), 0, 0, SampleMilliseconds);
        }
        public ReactorCore Eject()
        {
            if (!CanEject) throw new InvalidOperationException("An active or partly used fuel cycle cannot be ejected in this slice.");
            return new ReactorCore(_rules, CoreMode.Empty, Cooling, false, 0, 0, 0, SampleMilliseconds);
        }
        public ReactorCore Start()
        {
            if (!CanStart) throw new InvalidOperationException("Startup interlocks are not satisfied.");
            return Copy(mode: CoreMode.Running);
        }
        public ReactorCore Shutdown() => Mode == CoreMode.Running ? Copy(mode: CoreMode.Shutdown) : this;
        public ReactorCore SetCooling(bool enabled) => Cooling == enabled ? this : Copy(cooling: enabled);
        public ReactorCore EmergencyCooling()
        {
            long risk = Math.Max(0, InstabilityMilliseconds - _rules.EmergencyReliefMilliseconds);
            return Cooling && risk == InstabilityMilliseconds ? this : Copy(cooling: true, instability: risk);
        }
        public ReactorCore ResetTrip()
        {
            if (!CanReset) throw new InvalidOperationException("Trip reset needs cooling and a safe instability level.");
            return Copy(mode: CoreMode.Shutdown);
        }

        public CoreAdvance AdvanceTo(long shiftMilliseconds)
        {
            if (shiftMilliseconds < SampleMilliseconds) throw new ArgumentOutOfRangeException(nameof(shiftMilliseconds));
            if (shiftMilliseconds == SampleMilliseconds) return new CoreAdvance(this, 0, null, null, CoreRisk.None, SampleMilliseconds);
            long delta = shiftMilliseconds - SampleMilliseconds;
            long work = WorkMilliseconds, instability = InstabilityMilliseconds, active = 0;
            long? warningAt = null, stoppedAt = null;
            CoreMode mode = Mode;
            CoreRisk risk = !Cooling ? CoreRisk.CoolingLost : SuspectFuel ? CoreRisk.SuspectFuel : CoreRisk.None;
            if (Mode == CoreMode.Running)
            {
                active = Math.Min(delta, RemainingFuelMilliseconds);
                if (risk != CoreRisk.None) active = Math.Min(active, _rules.TripMilliseconds - instability);
                work += active;
                instability = risk == CoreRisk.None ? Math.Max(0, instability - active) : instability + active;
                if (risk != CoreRisk.None && InstabilityMilliseconds < _rules.WarningMilliseconds &&
                    instability >= _rules.WarningMilliseconds)
                    warningAt = SampleMilliseconds + _rules.WarningMilliseconds - InstabilityMilliseconds;
                // Exhaustion wins an exact tie with the trip boundary: there is no further output.
                if (work == FuelDurationMilliseconds) { mode = CoreMode.Exhausted; stoppedAt = SampleMilliseconds + active; }
                else if (instability == _rules.TripMilliseconds) { mode = CoreMode.Tripped; stoppedAt = SampleMilliseconds + active; }
            }
            // Cooling continues while shut down; restoring cooling never restarts the core.
            if (mode != CoreMode.Running && Cooling) instability = Math.Max(0, instability - (delta - active));
            var state = new ReactorCore(_rules, mode, Cooling, SuspectFuel, FuelDurationMilliseconds, work, instability, shiftMilliseconds);
            long quanta = work / _rules.PowerQuantumMilliseconds - WorkMilliseconds / _rules.PowerQuantumMilliseconds;
            return new CoreAdvance(state, quanta, warningAt, stoppedAt, risk, SampleMilliseconds + active);
        }
    }
}
