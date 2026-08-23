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
            GUI.Box(new Rect(16, 16, 520, 138), "CRITICAL SHIFT // NIGHT SHIFT PROTOTYPE");
            string emergency = game.State == PrototypeShiftState.CoolingEmergency ? $"   EMERGENCY {Mathf.CeilToInt(game.EmergencySeconds)}s" : string.Empty;
            GUI.Label(new Rect(30, 44, 490, 22), $"OBJECTIVE: {game.State}   SHIFT {Mathf.CeilToInt(game.RemainingSeconds)}s{emergency}");
            GUI.Label(new Rect(30, 68, 490, 22), $"ORE {game.Ore}/{PrototypeShiftRules.OreQuota}   FUEL {game.Fuel}/{PrototypeShiftRules.FuelQuota}   HEAT {game.ReactorHeat:0}%");
            GUI.Label(new Rect(30, 92, 490, 42), game.Message);
            GUI.Label(new Rect(30, 130, 490, 20), "WASD move · Shift sprint · Ctrl crouch · Space jump · E interact · R reset after shift");
            if (player != null && !string.IsNullOrEmpty(player.FocusPrompt)) GUI.Label(new Rect(Screen.width / 2 - 190, Screen.height / 2 + 28, 520, 28), player.FocusPrompt);
            GUI.Label(new Rect(Screen.width / 2 - 90, Screen.height / 2 - 8, 180, 20), "+");
        }
    }
}
