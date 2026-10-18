using System.Text.Json;
using CriticalShift.Application;

namespace CriticalShift.Scenarios
{
    internal static class DebriefScenarioSteps
    {
        internal static bool TryRead(JsonProperty a, WorldSession world, out object? actual, out object? expected)
        {
            var debrief = world.Debrief; var totals = debrief?.Incidents; actual = null; expected = null;
            switch (a.Name)
            {
                case "debriefPresent": actual = debrief != null; expected = a.Value.GetBoolean(); return true;
                case "debriefOutcome": actual = debrief?.World.Outcome.ToString(); expected = a.Value.GetString(); return true;
                case "debriefElapsed": actual = debrief?.World.ElapsedMilliseconds; expected = a.Value.GetInt64(); return true;
                case "debriefDelivered": actual = debrief?.Power?.Delivered; expected = a.Value.GetInt64(); return true;
                case "terminalWorkers": actual = debrief?.WorkersAtEnd.Count; expected = a.Value.GetInt32(); return true;
                case "recordedImpacts": actual = totals?.WorkerImpacts; expected = a.Value.GetInt64(); return true;
                case "recordedIncapacitations": actual = totals?.Incapacitations; expected = a.Value.GetInt64(); return true;
                case "recordedRecoveries": actual = totals?.StandingRecoveries; expected = a.Value.GetInt64(); return true;
                case "recordedJams": actual = totals?.MachineJams; expected = a.Value.GetInt64(); return true;
                case "recordedBypassConversions": actual = totals?.BypassedConversions; expected = a.Value.GetInt64(); return true;
                case "recordedTrips": actual = totals?.ReactorTrips; expected = a.Value.GetInt64(); return true;
                case "incidentDetailsDropped": actual = debrief?.DroppedIncidents > 0; expected = a.Value.GetBoolean(); return true;
                default: return false;
            }
        }
    }
}
