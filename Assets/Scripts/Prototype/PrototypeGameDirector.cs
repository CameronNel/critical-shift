using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeShiftState { Briefing, Mining, Refining, Reactor, CoolingEmergency, Won, Failed }

    /// Host-local state owner for the single-player proof-of-fun loop. Networking can
    /// later replicate this explicit state without coupling the interactions to UI.
    public sealed class PrototypeGameDirector : MonoBehaviour
    {
        public static PrototypeGameDirector Instance { get; private set; }
        public PrototypeShiftState State { get; private set; } = PrototypeShiftState.Briefing;
        public int Ore { get; private set; }
        public int Fuel { get; private set; }
        public float ReactorHeat { get; private set; }
        public float RemainingSeconds { get; private set; } = PrototypeShiftRules.ShiftSeconds;
        public float EmergencySeconds { get; private set; } = PrototypeShiftRules.EmergencySeconds;
        public bool UnsafeShortcut { get; private set; }
        public PrototypeSocialSystem Social { get; private set; }
        public string Message { get; private set; } = "Open the authored BRIEFING BOARD in Arrival. The shift clock is already running.";
        public bool IsTerminal => State == PrototypeShiftState.Won || State == PrototypeShiftState.Failed;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            EnsureRuntimeReady();
        }

        public void EnsureRuntimeReady()
        {
            if (Instance != null && Instance != this) return;
            Instance = this;
            if (Social == null) Social = new PrototypeSocialSystem();
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        void Update()
        {
            if (IsTerminal) return;
            RemainingSeconds -= Time.deltaTime;
            if (RemainingSeconds <= 0f) Fail("SHIFT EXPIRED — quota missed.");
            if (State != PrototypeShiftState.Briefing && Social != null) Social.Tick(Time.deltaTime);

            if (State == PrototypeShiftState.CoolingEmergency)
            {
                EmergencySeconds -= Time.deltaTime;
                if (EmergencySeconds <= 0f)
                    Fail("CONTAINMENT FAILURE — the unsafe fuel overheated the core.");
            }
        }

        public void StartShift()
        {
            if (State != PrototypeShiftState.Briefing) return;
            State = PrototypeShiftState.Mining;
            Message = PrototypeShoeboxRuntime.Instance != null
                ? "Carry 3 ore rocks onto the conveyor. [G/right mouse] grab; [left mouse] throw."
                : "Mine 3 ore batches at the ORE LOADER. Follow the cyan worker route west.";
            if (Social != null) Social.Officer.BeginInspection();
        }

        public void MineOre()
        {
            if (State != PrototypeShiftState.Mining) return;
            Ore++;
            if (Ore >= PrototypeShiftRules.OreQuota)
            {
                State = PrototypeShiftState.Refining;
                Message = "Ore quota met. Refine 2 fuel batches — [E] at the refinery.";
            }
            else Message = $"Ore batch secured ({Ore}/{PrototypeShiftRules.OreQuota}).";
        }

        public void RefineFuel(bool shortcut)
        {
            if (State != PrototypeShiftState.Refining || Ore <= 0) return;
            Ore--;
            Fuel += shortcut ? 2 : 1;
            UnsafeShortcut |= shortcut;
            if (PrototypeShiftRules.HasFuelQuota(Fuel))
            {
                State = PrototypeShiftState.Reactor;
                Message = shortcut
                    ? "BYPASS COMPLETE — two fuel batches at once. Start the reactor; hidden instability is possible."
                    : "Fuel quota met. Take the production route to CONTROL POSITION in the reactor.";
            }
            else Message = $"Fuel batch ready ({Fuel}/{PrototypeShiftRules.FuelQuota}).";
        }

        public bool RecordPhysicalFuel(bool unsafeFuel)
        {
            if (State != PrototypeShiftState.Refining || Ore <= 0) return false;
            Ore--;
            Fuel++;
            UnsafeShortcut |= unsafeFuel;
            if (PrototypeShiftRules.HasFuelQuota(Fuel))
            {
                State = PrototypeShiftState.Reactor;
                Message = unsafeFuel
                    ? "Fuel quota loaded, but telemetry is suspicious. Start the reactor and watch for delayed consequences."
                    : "Two physical fuel assemblies loaded. Start the reactor control.";
            }
            else Message = $"Physical fuel assembly loaded ({Fuel}/{PrototypeShiftRules.FuelQuota}).";
            return true;
        }

        public void StartReactor()
        {
            if (State != PrototypeShiftState.Reactor) return;
            if (PrototypeShoeboxRuntime.Instance != null)
            {
                if (PrototypeShoeboxRuntime.Instance.TryStartReactor())
                    Message = "REACTOR ONLINE — meet demand. Watch the physical heat and stability board.";
                else Message = "REACTOR REFUSED — physically load two fuel assemblies first.";
                return;
            }
            ReactorHeat = PrototypeShiftRules.ReactorHeatFor(Fuel, UnsafeShortcut);
            if (PrototypeShiftRules.IsMeltdown(ReactorHeat))
            {
                State = PrototypeShiftState.CoolingEmergency;
                EmergencySeconds = PrototypeShiftRules.EmergencySeconds;
                Message = "DELAYED CONSEQUENCE — bypass fuel is overheating. Reach EMERGENCY SHUTDOWN before containment fails.";
            }
            else
            {
                State = PrototypeShiftState.Won;
                Message = "CLEAN SHIFT COMPLETE — power delivered. Press R to run it again.";
            }
        }

        public void ResolveCoolingEmergency()
        {
            if (State != PrototypeShiftState.CoolingEmergency) return;
            ReactorHeat = PrototypeShiftRules.RecoveredHeat;
            State = PrototypeShiftState.Won;
            Message = "DIRTY SUCCESS — emergency cooling saved the reactor. Press R to run it again.";
        }

        public void Fail(string reason) { State = PrototypeShiftState.Failed; Message = reason + " Press R to reset."; }

        public void SetMessage(string message) { Message = message; }
        public void SetRuntimeState(PrototypeShiftState state, string message)
        {
            if (IsTerminal && state != PrototypeShiftState.Briefing) return;
            State = state;
            if (!string.IsNullOrEmpty(message)) Message = message;
        }
        public void SetProductionCounts(int ore, int fuel)
        { Ore = Mathf.Max(0, ore); Fuel = Mathf.Max(0, fuel); }
        public void SetPhysicalHeat(float normalizedHeat) { ReactorHeat = Mathf.Clamp(normalizedHeat * 100f, 0f, 150f); }
        public void BeginPhysicalEmergency(string cause)
        {
            if (IsTerminal || State == PrototypeShiftState.CoolingEmergency) return;
            State = PrototypeShiftState.CoolingEmergency;
            EmergencySeconds = PrototypeShiftRules.EmergencySeconds;
            Message = cause;
        }
        public void CompletePhysicalShift(bool dirty, string explanation)
        {
            if (IsTerminal) return;
            State = PrototypeShiftState.Won;
            Message = (dirty ? "DIRTY SUCCESS — " : "CLEAN SHIFT COMPLETE — ") + explanation + " Press R to run it again.";
        }

        public void ResetShift()
        {
            Ore = 0; Fuel = 0; ReactorHeat = 0f; UnsafeShortcut = false;
            RemainingSeconds = PrototypeShiftRules.ShiftSeconds;
            EmergencySeconds = PrototypeShiftRules.EmergencySeconds;
            State = PrototypeShiftState.Briefing;
            Message = "Open the authored BRIEFING BOARD in Arrival. The shift clock is already running.";
            if (Social != null) Social.ResetRound();
            if (PrototypeFacilityRuntime.Instance != null) PrototypeFacilityRuntime.Instance.ResetWorld();
            else PrototypeShoeboxRuntime.Instance?.ResetWorld();
        }
    }
}
