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
            GUI.skin.label.wordWrap = true;
            GUI.Box(new Rect(16, 16, 650, 224), "CRITICAL SHIFT // RADIOACTIVE SHOEBOX");
            string emergency = game.State == PrototypeShiftState.CoolingEmergency ? $"   EMERGENCY {Mathf.CeilToInt(game.EmergencySeconds)}s" : string.Empty;
            GUI.Label(new Rect(30, 44, 620, 22), $"OBJECTIVE: {game.State}   SHIFT {Mathf.CeilToInt(game.RemainingSeconds)}s{emergency}");
            GUI.Label(new Rect(30, 68, 620, 22), $"PROCESSED ORE {game.Ore}/{PrototypeShiftRules.OreQuota}   LOADED FUEL {game.Fuel}/{PrototypeShiftRules.FuelQuota}   HEAT {game.ReactorHeat:0}%");
            var shoebox = PrototypeShoeboxRuntime.Instance;
            if (shoebox != null)
                GUI.Label(new Rect(30, 91, 620, 22), $"ENERGY {shoebox.EnergyDelivered:0.0}/6.0   RESERVE {shoebox.ReservePower}%   SUIT {(player != null && player.WearingSuit ? "SEALED" : "SKIPPED")}   BODY {(player != null ? player.BodyState.ToString() : "Normal")}");
            GUI.Label(new Rect(30, 114, 620, 42), game.Message);
            if (game.Social != null) GUI.Label(new Rect(30, 158, 620, 22), $"SOCIAL: {game.Social.Infiltrator.Phase} · OFFICER {game.Social.Officer.State} · SUSPICION {game.Social.Officer.Suspicion}");
            GUI.Label(new Rect(30, 184, 620, 40), "WASD move · Shift sprint · Ctrl crouch · Space jump · E use · F risky/alternate · G/right mouse grab/drag · left mouse throw · R restart after result");
            if (player != null && !string.IsNullOrEmpty(player.FocusPrompt)) GUI.Label(new Rect(Screen.width / 2 - 190, Screen.height / 2 + 28, 520, 28), player.FocusPrompt);
            GUI.Label(new Rect(Screen.width / 2 - 90, Screen.height / 2 - 8, 180, 20), "+");
            if (game.IsTerminal && game.Social != null)
            {
                GUI.Box(new Rect(16, Screen.height - 96, Mathf.Min(Screen.width - 32, 980), 80), "CAUSAL DEBRIEF");
                GUI.Label(new Rect(30, Screen.height - 70, Mathf.Min(Screen.width - 60, 950), 48), game.Social.Debrief);
            }
        }
    }
}
