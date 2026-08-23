using NUnit.Framework;
using UnityEngine;
using CriticalShift.Prototype;

public sealed class PrototypeFacilityGuidanceTests
{
    [Test]
    public void PhaseUpdatesObjectiveAndTarget()
    {
        var model = new PrototypeFacilityGuidanceModel();
        Assert.AreEqual(PrototypeFacilityWaypointId.Briefing, model.TargetId);
        model.SetPhase(PrototypeShiftState.Mining);
        Assert.AreEqual(PrototypeFacilityWaypointId.Mine, model.TargetId);
        Assert.AreEqual("Mine ore", model.ObjectiveLabel);
        Assert.AreEqual("GULLET MINE DRILL", model.TargetLabel);
    }

    [Test]
    public void WorldTargetAndCustomObjectiveUpdate()
    {
        var model = new PrototypeFacilityGuidanceModel();
        var position = new Vector3(3f, 2f, -4f);
        model.SetWorldTarget("SABOTAGE CLUE", position, "Inspect the suspicious route");
        Assert.IsTrue(model.HasTarget);
        Assert.IsNull(model.TargetId);
        Assert.AreEqual(position, model.TargetWorldPosition);
        Assert.AreEqual("Inspect the suspicious route", model.ObjectiveLabel);
    }

    [Test]
    public void ResetReturnsBriefingTarget()
    {
        var model = new PrototypeFacilityGuidanceModel();
        model.SetPhase(PrototypeShiftState.CoolingEmergency);
        model.Reset();
        Assert.AreEqual(PrototypeShiftState.Briefing, model.Phase);
        Assert.AreEqual(PrototypeFacilityWaypointId.Briefing, model.TargetId);
        Assert.AreEqual("Open briefing", model.ObjectiveLabel);
    }
}
