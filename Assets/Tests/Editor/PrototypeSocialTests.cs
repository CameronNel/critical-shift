using NUnit.Framework;
using CriticalShift.Prototype;

public sealed class PrototypeSocialTests
{
    [Test] public void SuspicionMovesOfficerTowardAudit()
    {
        var officer = new PrototypeComplianceOfficer(); officer.BeginInspection(); officer.AddSuspicion(6, "missing log");
        Assert.AreEqual(PrototypeOfficerState.FormalAudit, officer.State); Assert.GreaterOrEqual(officer.Evidence.Count, 1);
    }

    [Test] public void IncidentRequiresEstablishedLoopAndPlayerPressure()
    {
        var director = new PrototypeIncidentDirector(); director.AddPlayerPressure(2);
        Assert.IsFalse(director.IsEligible(PrototypeIncidentSeverity.Major, false, false));
        Assert.IsTrue(director.IsEligible(PrototypeIncidentSeverity.Major, true, false));
        Assert.IsFalse(director.IsEligible(PrototypeIncidentSeverity.Major, true, true));
    }

    [Test] public void InfiltratorTransitionsAndLegitimateSuspiciousWorkerExists()
    {
        var social = new PrototypeSocialSystem();
        social.ResetRound(); social.Infiltrator.Tick(2); Assert.AreEqual(PrototypeInfiltratorPhase.Reconnaissance, social.Infiltrator.Phase);
        social.Infiltrator.Sabotage(); Assert.IsTrue(social.Infiltrator.ObjectiveComplete);
        Assert.IsFalse(string.IsNullOrEmpty(social.LegitimateSuspiciousWorker));
    }

    [Test] public void DebriefPreservesCauseWarningConsequenceRecovery()
    {
        var ledger = new PrototypeCausalLedger(); ledger.Record("shortcut", "heat climbed", "cooling emergency", "manual shutdown");
        StringAssert.Contains("shortcut -> heat climbed -> cooling emergency -> manual shutdown", ledger.Debrief());
    }

    [Test] public void SocialResetReturnsActorsAndLedgerToInitialState()
    {
        var social = new PrototypeSocialSystem(); social.ResetRound(); social.SabotageInfiltrator(); social.BonkInfiltrator();
        social.ResetRound();
        Assert.AreEqual(PrototypeInfiltratorPhase.Pretending, social.Infiltrator.Phase);
        Assert.AreEqual(PrototypeOfficerState.Arriving, social.Officer.State);
        Assert.AreEqual(0, social.Ledger.Entries.Count);
    }
}
