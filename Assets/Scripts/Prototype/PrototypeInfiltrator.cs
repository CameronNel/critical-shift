using System;

namespace CriticalShift.Prototype
{
    public enum PrototypeInfiltratorPhase { Hidden, Arriving, Pretending, Reconnaissance, Sabotaging, Revealed, Escaping, Incapacitated, Captured }

    [Serializable]
    public sealed class PrototypeInfiltrator
    {
        public PrototypeInfiltratorPhase Phase { get; private set; }
        public bool IsLegitimateDisguise { get { return Phase != PrototypeInfiltratorPhase.Revealed && Phase != PrototypeInfiltratorPhase.Escaping && Phase != PrototypeInfiltratorPhase.Captured; } }
        public bool ObjectiveComplete { get; private set; }
        public int SuspicionClues { get; private set; }
        public string Name { get; private set; }
        public PrototypeInfiltrator(string name = "Contract Worker 7") { Name = name; Reset(); }
        public void Reset() { Phase = PrototypeInfiltratorPhase.Pretending; ObjectiveComplete = false; SuspicionClues = 0; }
        public void Tick(int ticks)
        {
            if (Phase == PrototypeInfiltratorPhase.Pretending && ticks >= 2) Phase = PrototypeInfiltratorPhase.Reconnaissance;
            else if (Phase == PrototypeInfiltratorPhase.Reconnaissance && ticks >= 4) Phase = PrototypeInfiltratorPhase.Sabotaging;
        }
        public void NoticeClue() { SuspicionClues++; }
        public void Sabotage() { if (Phase == PrototypeInfiltratorPhase.Reconnaissance || Phase == PrototypeInfiltratorPhase.Sabotaging) { Phase = PrototypeInfiltratorPhase.Sabotaging; ObjectiveComplete = true; } }
        public void Reveal() { if (Phase != PrototypeInfiltratorPhase.Incapacitated && Phase != PrototypeInfiltratorPhase.Captured) Phase = PrototypeInfiltratorPhase.Revealed; }
        public void Escape() { if (Phase == PrototypeInfiltratorPhase.Revealed || Phase == PrototypeInfiltratorPhase.Sabotaging) Phase = PrototypeInfiltratorPhase.Escaping; }
        public void Bonk() { if (Phase != PrototypeInfiltratorPhase.Captured) Phase = PrototypeInfiltratorPhase.Incapacitated; }
        public void Capture() { Phase = PrototypeInfiltratorPhase.Captured; }
    }
}
