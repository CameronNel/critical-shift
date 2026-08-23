using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeStation { Briefing, Mine, Refinery, Reactor, EmergencyCooling }

    public sealed class PrototypeInteractable : MonoBehaviour
    {
        public PrototypeStation station;
        public string prompt;
        public bool unsafeShortcut;

        public string Prompt => string.IsNullOrEmpty(prompt) ? station.ToString() : prompt;
        public bool SupportsShortcut => station == PrototypeStation.Refinery;

        public void Interact(bool forceShortcut = false)
        {
            var game = PrototypeGameDirector.Instance;
            if (game == null) return;
            switch (station)
            {
                case PrototypeStation.Briefing: game.StartShift(); break;
                case PrototypeStation.Mine: game.MineOre(); break;
                case PrototypeStation.Refinery: game.RefineFuel(unsafeShortcut || forceShortcut); break;
                case PrototypeStation.Reactor: game.StartReactor(); break;
                case PrototypeStation.EmergencyCooling: game.ResolveCoolingEmergency(); break;
            }
        }
    }
}
