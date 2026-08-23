namespace CriticalShift.Prototype
{
    /// Host-local orchestration seam. A future network authority can replicate intents and
    /// resulting snapshots here; this prototype deliberately has no client authority.
    public sealed class PrototypeSocialSystem
    {
        public PrototypeInfiltrator Infiltrator { get; private set; }
        public PrototypeComplianceOfficer Officer { get; private set; }
        public PrototypeIncidentDirector Incidents { get; private set; }
        public PrototypeCausalLedger Ledger { get; private set; }
        public string LegitimateSuspiciousWorker { get; private set; }
        public string Debrief { get { return Ledger.Debrief(); } }
        int ticks;
        float tickAccumulator;
        bool reconLogged;
        public PrototypeSocialSystem() { ResetRound(); }
        public void ResetRound()
        { Infiltrator = new PrototypeInfiltrator(); Officer = new PrototypeComplianceOfficer(); Incidents = new PrototypeIncidentDirector(); Ledger = new PrototypeCausalLedger(); LegitimateSuspiciousWorker = "Mara Voss (legitimate, under review)"; ticks = 0; tickAccumulator = 0f; reconLogged = false; }
        public void Tick(float seconds)
        {
            tickAccumulator += seconds;
            if (tickAccumulator < 4f) return;
            tickAccumulator -= 4f;
            ticks++;
            Infiltrator.Tick(ticks);
            if (ticks == 2 && Officer.State == PrototypeOfficerState.Arriving) Officer.BeginInspection();
            if (ticks >= 4 && !reconLogged)
            {
                reconLogged = true;
                Ledger.Record("Infiltrator reconned a restricted route", "Scanner showed a badge mismatch", "Officer opened an investigation", "Crew can inspect both suspicious workers");
            }
        }
        public void PlayerResponse(PrototypeOfficerResponse response)
        { Officer.Respond(response); Incidents.AddPlayerPressure(response == PrototypeOfficerResponse.Bonk ? 2 : 1); Ledger.Record("Player chose " + response, "Officer response changed", response == PrototypeOfficerResponse.Cooperate ? "Inspection stayed routine" : "Compliance pressure increased", "Crew can still recover"); }
        public void IdentifyInfiltrator()
        {
            Infiltrator.NoticeClue();
            Officer.AddSuspicion(1, "inconsistent worker telemetry");
            if (Infiltrator.SuspicionClues >= 2) Infiltrator.Reveal();
        }
        public void SabotageInfiltrator() { Infiltrator.Sabotage(); Incidents.AddPlayerPressure(2); Ledger.Record("Infiltrator tampered with equipment", "Power draw spiked", "Production interruption", "Repair and verify the line"); }
        public void BonkInfiltrator() { Infiltrator.Bonk(); Officer.AddEvidence(new PrototypeEvidence(PrototypeEvidenceType.UnconsciousInfiltrator, "production floor", 1)); Ledger.Record("Crew used a nonlethal bonk", "Disguise failed", "Infiltrator incapacitated", "Drag the worker to OCRU or restraint"); }
    }
}
