using System;

namespace CriticalShift.Prototype
{
    public enum PrototypeIncidentSeverity { None, Minor, Medium, Major }
    public sealed class PrototypeIncidentDirector
    {
        readonly int seed; int counter; public int PlayerPressure { get; private set; }
        public PrototypeIncidentSeverity LastSeverity { get; private set; }
        public PrototypeIncidentDirector(int seed = 7) { this.seed = seed; Reset(); }
        public void Reset() { counter = 0; PlayerPressure = 0; LastSeverity = PrototypeIncidentSeverity.None; }
        public void AddPlayerPressure(int amount) { PlayerPressure += amount; }
        public bool IsEligible(PrototypeIncidentSeverity severity, bool basicLoopEstablished, bool unrecoverableCrisis)
        { return severity != PrototypeIncidentSeverity.None && basicLoopEstablished && !unrecoverableCrisis && (severity != PrototypeIncidentSeverity.Major || PlayerPressure >= 2); }
        public PrototypeIncidentSeverity Evaluate(bool basicLoopEstablished, bool unrecoverableCrisis)
        {
            counter++; if (!basicLoopEstablished || unrecoverableCrisis) return PrototypeIncidentSeverity.None;
            var roll = Math.Abs(seed + counter * 31 + PlayerPressure * 13) % 10;
            var result = PlayerPressure >= 3 ? (roll < 3 ? PrototypeIncidentSeverity.Major : PrototypeIncidentSeverity.Medium) : (roll < 6 ? PrototypeIncidentSeverity.Minor : PrototypeIncidentSeverity.None);
            LastSeverity = result; return result;
        }
    }
}
