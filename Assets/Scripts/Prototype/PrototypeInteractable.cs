using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeStation
    {
        Briefing, Mine, Refinery, Reactor, EmergencyCooling,
        OrePile, Crusher, CoolingValve, SuitLocker, TntWall, Reanimation,
        Infiltrator, LegitimateWorker, ComplianceOfficer, EvidenceLocker,
        OfficerBonk, MineCart,
        FacilityBriefing, FacilitySuit, FacilityMineFace, FacilityCart, FacilityHopper,
        FacilityCrusher, FacilitySorter, FacilityProcessor, FacilityDryer,
        FacilityFuelAssembly, FacilityInspection, FacilityFuelReceiving,
        FacilityReactorPump, FacilityCoolingValve, FacilityEmergencyCooling,
        FacilityReactorControl, FacilityGridDemand, FacilityReanimation, FacilityTnt
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
            station == PrototypeStation.ComplianceOfficer || station == PrototypeStation.FacilitySuit ||
            station == PrototypeStation.FacilityMineFace || station == PrototypeStation.FacilityCrusher ||
            station == PrototypeStation.FacilitySorter || station == PrototypeStation.FacilityProcessor ||
            station == PrototypeStation.FacilityDryer || station == PrototypeStation.FacilityFuelAssembly ||
            station == PrototypeStation.FacilityInspection || station == PrototypeStation.FacilityReactorControl ||
            station == PrototypeStation.FacilityGridDemand || station == PrototypeStation.FacilityTnt;

        public void Interact(bool forceShortcut = false)
        {
            var game = PrototypeGameDirector.Instance;
            if (game == null) return;
            var facility = PrototypeFacilityRuntime.Instance;
            if (facility != null && facility.HandleInteraction(station, forceShortcut)) return;
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
