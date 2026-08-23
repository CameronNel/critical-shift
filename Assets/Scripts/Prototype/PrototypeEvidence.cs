using System;

namespace CriticalShift.Prototype
{
    public enum PrototypeEvidenceType { SuspiciousBehaviour, IllegalModification, MissingSignal, Contraband, DisabledOfficer, UnconsciousInfiltrator, FalsifiedLog }

    [Serializable]
    public sealed class PrototypeEvidence
    {
        public PrototypeEvidenceType Type;
        public string Location;
        public int ComplianceValue;
        public bool Hidden;
        public bool Discovered;

        public PrototypeEvidence(PrototypeEvidenceType type, string location, int value = 1)
        { Type = type; Location = location ?? "unknown"; ComplianceValue = value; }
    }
}
