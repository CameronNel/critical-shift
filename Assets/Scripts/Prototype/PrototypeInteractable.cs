using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeStation
    {
        Briefing, Mine, Refinery, Reactor, EmergencyCooling,
        OrePile, Crusher, CoolingValve, SuitLocker, TntWall, Reanimation,
        Infiltrator, LegitimateWorker, ComplianceOfficer, EvidenceLocker,
        OfficerBonk, MineCart
    }

    public sealed class PrototypeInteractable : MonoBehaviour
    {
        public PrototypeStation station;
        public string prompt;
        public string alternatePrompt;
        public bool unsafeShortcut;

        public string Prompt => string.IsNullOrEmpty(prompt) ? station.ToString() : prompt;
        public string AlternatePrompt => string.IsNullOrEmpty(alternatePrompt) ? "take risky alternative" : alternatePrompt;
        public bool SupportsShortcut => station == PrototypeStation.Refinery || station == PrototypeStation.OrePile ||
            station == PrototypeStation.Crusher || station == PrototypeStation.Infiltrator ||
            station == PrototypeStation.ComplianceOfficer;

        public void Interact(bool forceShortcut = false)
        {
            var game = PrototypeGameDirector.Instance;
            if (game == null) return;
            var shoebox = PrototypeShoeboxRuntime.Instance;
            switch (station)
            {
                case PrototypeStation.Briefing: game.StartShift(); break;
                case PrototypeStation.Mine: game.MineOre(); break;
                case PrototypeStation.Refinery: game.RefineFuel(unsafeShortcut || forceShortcut); break;
                case PrototypeStation.Reactor: game.StartReactor(); break;
                case PrototypeStation.EmergencyCooling: game.ResolveCoolingEmergency(); break;
                case PrototypeStation.OrePile: shoebox?.SpawnOre(forceShortcut); break;
                case PrototypeStation.Crusher: shoebox?.UseCrusher(forceShortcut); break;
                case PrototypeStation.CoolingValve: shoebox?.UseEmergencyCooling(); break;
                case PrototypeStation.SuitLocker: shoebox?.ToggleSuit(); break;
                case PrototypeStation.TntWall: shoebox?.ArmTnt(); break;
                case PrototypeStation.Reanimation: shoebox?.TryReanimate(); break;
                case PrototypeStation.Infiltrator: shoebox?.HandleInfiltrator(forceShortcut); break;
                case PrototypeStation.LegitimateWorker: shoebox?.InspectLegitimateWorker(); break;
                case PrototypeStation.ComplianceOfficer: shoebox?.HandleOfficer(forceShortcut); break;
                case PrototypeStation.EvidenceLocker: shoebox?.HideEvidence(); break;
                case PrototypeStation.OfficerBonk: shoebox?.BonkOfficer(); break;
                case PrototypeStation.MineCart: shoebox?.PushCart(); break;
            }
        }
    }
}
