using System;
using System.Collections.Generic;

namespace CriticalShift.Prototype
{
    public enum PrototypeOfficerState { Arriving, RoutineInspection, Investigating, CollectingEvidence, Distracted, Suspicious, FormalAudit, Enforcement, Disabled, Departing }
    public enum PrototypeOfficerResponse { Cooperate, Distract, HideEvidence, Bonk }

    [Serializable]
    public sealed class PrototypeComplianceOfficer
    {
        readonly List<PrototypeEvidence> evidence = new List<PrototypeEvidence>();
        public PrototypeOfficerState State { get; private set; }
        public int Suspicion { get; private set; }
        public int Escalation { get; private set; }
        public IReadOnlyList<PrototypeEvidence> Evidence { get { return evidence; } }
        public void Reset() { State = PrototypeOfficerState.Arriving; Suspicion = 0; Escalation = 0; evidence.Clear(); }
        public PrototypeComplianceOfficer() { Reset(); }
        public void BeginInspection() { State = PrototypeOfficerState.RoutineInspection; }
        public void AddSuspicion(int amount, string reason)
        {
            Suspicion += amount;
            if (amount > 0) evidence.Add(new PrototypeEvidence(PrototypeEvidenceType.SuspiciousBehaviour, reason, amount));
            State = Suspicion >= 6 ? PrototypeOfficerState.FormalAudit : PrototypeOfficerState.Suspicious;
        }
        public void AddEvidence(PrototypeEvidence item)
        {
            evidence.Add(item);
            Suspicion += item.ComplianceValue;
            if (State == PrototypeOfficerState.Enforcement || State == PrototypeOfficerState.Disabled) return;
            if (Suspicion >= 6) State = PrototypeOfficerState.FormalAudit;
            else State = PrototypeOfficerState.CollectingEvidence;
        }
        public void Respond(PrototypeOfficerResponse response)
        {
            if (response == PrototypeOfficerResponse.Cooperate) { Suspicion = Math.Max(0, Suspicion - 1); State = PrototypeOfficerState.Investigating; }
            else if (response == PrototypeOfficerResponse.Distract) { State = PrototypeOfficerState.Distracted; }
            else if (response == PrototypeOfficerResponse.HideEvidence) { for (int i = 0; i < evidence.Count; i++) evidence[i].Hidden = true; State = PrototypeOfficerState.Suspicious; Escalation++; }
            else { State = PrototypeOfficerState.Disabled; Escalation++; }
            if (Escalation >= 3) State = PrototypeOfficerState.Enforcement;
        }
        public void ResetAfterBonk() { if (State == PrototypeOfficerState.Disabled) State = PrototypeOfficerState.Arriving; }
    }
}
