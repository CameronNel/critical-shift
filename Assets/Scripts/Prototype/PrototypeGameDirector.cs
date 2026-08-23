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
        public string Message { get; private set; } = "Open the BRIEFING BOARD in Arrival. [E] interact";
        public bool IsTerminal => State == PrototypeShiftState.Won || State == PrototypeShiftState.Failed;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        void Update()
        {
            if (IsTerminal) return;
            RemainingSeconds -= Time.deltaTime;
            if (RemainingSeconds <= 0f) Fail("SHIFT EXPIRED — quota missed.");

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
            Message = "Mine 3 ore batches at the ORE LOADER. Follow the cyan worker route west.";
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

        public void StartReactor()
        {
            if (State != PrototypeShiftState.Reactor) return;
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

        public void ResetShift()
        {
            Ore = 0; Fuel = 0; ReactorHeat = 0f; UnsafeShortcut = false;
            RemainingSeconds = PrototypeShiftRules.ShiftSeconds;
            EmergencySeconds = PrototypeShiftRules.EmergencySeconds;
            State = PrototypeShiftState.Briefing;
            Message = "Open the BRIEFING BOARD in Arrival. [E] interact";
        }
    }
}
