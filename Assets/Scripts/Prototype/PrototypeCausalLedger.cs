using System;
using System.Collections.Generic;

namespace CriticalShift.Prototype
{
    [Serializable]
    public sealed class PrototypeCausalEntry
    {
        public string Cause;
        public string Warning;
        public string Consequence;
        public string Recovery;
        public PrototypeCausalEntry(string cause, string warning, string consequence, string recovery = "")
        { Cause = cause; Warning = warning; Consequence = consequence; Recovery = recovery; }
    }

    public sealed class PrototypeCausalLedger
    {
        readonly List<PrototypeCausalEntry> entries = new List<PrototypeCausalEntry>();
        public IReadOnlyList<PrototypeCausalEntry> Entries { get { return entries; } }
        public void Record(string cause, string warning, string consequence, string recovery = "")
        { entries.Add(new PrototypeCausalEntry(cause, warning, consequence, recovery)); }
        public string Debrief()
        {
            if (entries.Count == 0) return "DEBRIEF: No social incidents. Stable crew, clean shift.";
            var last = entries[entries.Count - 1];
            return "DEBRIEF: " + entries.Count + " causal incident(s). Last: " + last.Cause + " -> " + last.Warning + " -> " + last.Consequence + (string.IsNullOrEmpty(last.Recovery) ? "" : " -> " + last.Recovery);
        }
        public void Reset() { entries.Clear(); }
    }
}
