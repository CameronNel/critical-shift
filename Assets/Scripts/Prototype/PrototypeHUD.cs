using UnityEngine;

namespace CriticalShift.Prototype
{
    public sealed class PrototypeHUD : MonoBehaviour
    {
        PrototypePlayerController player;
        void Start() { player = FindAnyObjectByType<PrototypePlayerController>(); }
        void OnGUI()
        {
            var game = PrototypeGameDirector.Instance; if (game == null) return;
            var facility = PrototypeFacilityRuntime.Instance;
            GUI.skin.label.wordWrap = true;
            GUI.Box(new Rect(16, 16, 720, facility != null ? 286 : 224), facility != null ? "CRITICAL SHIFT // FULL FACILITY SHIFT" : "CRITICAL SHIFT // ISOLATED TEST");
            string emergency = game.State == PrototypeShiftState.CoolingEmergency ? $"   EMERGENCY {Mathf.CeilToInt(game.EmergencySeconds)}s" : string.Empty;
            string phase = facility == null ? game.State.ToString() : facility.Phase.ToString();
            GUI.Label(new Rect(30, 44, 690, 22), $"PHASE: {phase}   SHIFT {FormatTime(game.RemainingSeconds)}{emergency}");
            if (facility != null)
            {
                string cart = facility.Cart == null ? "0/3" : $"{facility.Cart.CargoCount}/3  {facility.Cart.CurrentMass:0.0}/{facility.Cart.ratedMass:0.0}t";
                GUI.Label(new Rect(30, 68, 690, 22), $"ORE EXTRACTED {facility.ExtractedOre}/{PrototypeShiftRules.OreQuota}   CART {cart}   BATCH {facility.BatchStage}");
                GUI.Label(new Rect(30, 91, 690, 22), $"FUEL LOADED {facility.LoadedFuel}/{PrototypeShiftRules.FuelQuota}   ENERGY {facility.EnergyDelivered:0.0}/{PrototypeFacilityRuntime.EnergyTarget:0}   HEAT {game.ReactorHeat:0}%   RESERVE {facility.ReservePower}%");
                string suitStep = facility.SuitSequence != null && facility.SuitSequence.IsRunning ? " · " + facility.SuitSequence.CurrentStep + " " + Mathf.RoundToInt(facility.SuitSequence.Progress * 100f) + "%" : string.Empty;
                GUI.Label(new Rect(30, 114, 690, 22), $"SUIT {(player != null && player.WearingSuit ? (facility.SuitSafe ? "SEALED" : "COMPROMISED") : "OFF")} {suitStep}   BODY {(player != null ? player.BodyState.ToString() : "Normal")}   COOLING {(facility.PumpStarted ? "FLOWING" : "OFF")}");
                GUI.Label(new Rect(30, 138, 690, 22), $"NEXT: {facility.Objective}  →  {facility.TargetLabel}  ({facility.TargetDistance:0}m)");
                GUI.Label(new Rect(30, 162, 690, 42), game.Message);
                if (game.Social != null) GUI.Label(new Rect(30, 206, 690, 22), $"SOCIAL: {game.Social.Infiltrator.Phase} · OFFICER {game.Social.Officer.State} · SUSPICION {game.Social.Officer.Suspicion}");
                GUI.Label(new Rect(30, 232, 690, 40), "WASD move · Shift sprint · Ctrl crouch · Space jump · E operate · F unsafe shortcut · G/right mouse grab/drag · left mouse throw · R restart after result");
            }
            else
            {
                GUI.Label(new Rect(30, 68, 620, 22), $"PROCESSED ORE {game.Ore}/{PrototypeShiftRules.OreQuota}   LOADED FUEL {game.Fuel}/{PrototypeShiftRules.FuelQuota}   HEAT {game.ReactorHeat:0}%");
                GUI.Label(new Rect(30, 114, 620, 42), game.Message);
                GUI.Label(new Rect(30, 184, 620, 40), "WASD move · E use · F risky action · G grab/drag · left mouse throw");
            }
            if (player != null && !string.IsNullOrEmpty(player.FocusPrompt)) GUI.Label(new Rect(Screen.width / 2 - 190, Screen.height / 2 + 28, 520, 28), player.FocusPrompt);
            GUI.Label(new Rect(Screen.width / 2 - 90, Screen.height / 2 - 8, 180, 20), "+");
            if (game.IsTerminal && game.Social != null)
            {
                GUI.Box(new Rect(16, Screen.height - 96, Mathf.Min(Screen.width - 32, 980), 80), "CAUSAL DEBRIEF");
                GUI.Label(new Rect(30, Screen.height - 70, Mathf.Min(Screen.width - 60, 950), 48), game.Social.Debrief);
            }
        }

        static string FormatTime(float seconds)
        {
            int value = Mathf.Max(0, Mathf.CeilToInt(seconds));
            return (value / 60).ToString("00") + ":" + (value % 60).ToString("00");
        }
    }
}
