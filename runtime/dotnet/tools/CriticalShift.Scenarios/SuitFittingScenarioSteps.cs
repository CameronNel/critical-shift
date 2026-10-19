using System;
using System.Linq;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    internal static class SuitFittingScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("suitStation", out var station)) return;
            world.SuitFitting.Register(Id(checked((int)Number(station, "id", 970))),
                new SuitFittingDefinition(Number(station, "duration", 20000)));
        }
        internal static string Execute(JsonElement step, WorldSession world, Guid epoch, Guid actor, Guid connection)
        {
            var action = Choice<SuitFittingAction>(step, "action");
            var worker = world.GetWorker(actor);
            var request = action == SuitFittingAction.Start ? new SuitFittingRequest(action, Number(step, "revision")) :
                new SuitFittingRequest(action, attempt: worker?.SuitFitting?.Id ?? Guid.Empty);
            var reply = world.ExecuteInteraction(connection, new InteractionCommand(epoch, Number(step, "seq"),
                InteractionKind.SuitFitting, Id(checked((int)Number(step, "station", 970))), suitFitting: request));
            return reply.SuitFitting?.Status.ToString() ?? reply.Status.ToString();
        }
        internal static bool TryRead(JsonProperty a, WorkerView? worker, WorldSession world, out object? actual, out object? expected)
        {
            var summary = world.SuitFitting.Summary;
            var change = world.Trace.Records.LastOrDefault(r => r.Changed && r.SuitFittingChange != null)?.SuitFittingChange;
            actual = null; expected = null;
            switch (a.Name)
            {
                case "canInteract": actual = worker?.CanInteract; expected = a.Value.GetBoolean(); return true;
                case "fittingPending": actual = worker?.SuitFitting != null; expected = a.Value.GetBoolean(); return true;
                case "fittingDue": actual = worker?.SuitFitting?.DueAtMilliseconds; expected = a.Value.GetInt64(); return true;
                case "fittingStarted": actual = summary.Started; expected = a.Value.GetInt64(); return true;
                case "fittingCompleted": actual = summary.Completed; expected = a.Value.GetInt64(); return true;
                case "fittingCancelled": actual = summary.Cancelled; expected = a.Value.GetInt64(); return true;
                case "fittingInterrupted": actual = summary.Interrupted; expected = a.Value.GetInt64(); return true;
                case "lastFittingEvent": actual = change?.Kind.ToString(); expected = a.Value.GetString(); return true;
                case "lastFittingAt": actual = change?.ShiftMilliseconds; expected = a.Value.GetInt64(); return true;
                default: return false;
            }
        }
    }
}
