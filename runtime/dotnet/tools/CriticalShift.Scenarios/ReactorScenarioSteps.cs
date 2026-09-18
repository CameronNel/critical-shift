using System;
using System.Linq;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    // Offline input translation only. The same host command stream owns every effect.
    internal static class ReactorScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("reactor", out var r)) return;
            world.Reactor.Register(Id(checked((int)Number(r, "id", 900))), new ReactorDefinition(
                Id(checked((int)Number(r, "definition", 901))), Number(r, "capacity", 100),
                Number(r, "reserve", 10), Number(r, "startupCost", 3), Number(r, "emergencyCost", 4),
                Number(r, "auxiliaryCost", 6), checked((int)Number(r, "maximumFuelUnits", 10000)),
                checked((int)Number(r, "contaminationTolerance", 500)), Number(r, "millisecondsPerFuelUnit", 100),
                Number(r, "quantum", 100), checked((int)Number(r, "reservePerQuantum", 1)),
                checked((int)Number(r, "gridPerQuantum", 4)), Number(r, "warning", 400), Number(r, "trip", 800),
                Number(r, "reset", 100), Number(r, "emergencyRelief", 400)));
        }
        internal static string Execute(JsonElement step, WorldSession world, Guid epoch, Guid connection)
        {
            var request = new ReactorRequest(Choice<ReactorAction>(step, "action"), Number(step, "reactorRevision"),
                step.TryGetProperty("container", out var c) ? Id(c.GetInt32()) : Guid.Empty,
                Number(step, "objectRevision", 0), Number(step, "batchRevision", 0), Number(step, "lease", 0),
                Flag(step, "cooling", false));
            var reply = world.ExecuteInteraction(connection, new InteractionCommand(epoch, Number(step, "seq"),
                InteractionKind.Reactor, Id(checked((int)Number(step, "reactor", 900))), reactor: request));
            return reply.Reactor?.Status.ToString() ?? reply.Status.ToString();
        }
        internal static bool TryRead(JsonProperty a, WorldSession world, out object? actual, out object? expected)
        {
            var core = world.Reactor.View; var power = world.Reactor.PowerSummary;
            var trace = world.Trace.Records.LastOrDefault(x => x.ReactorChange != null);
            actual = null; expected = null;
            switch (a.Name)
            {
                case "reactorPresent": actual = core != null; expected = a.Value.GetBoolean(); return true;
                case "reactorMode": actual = core?.Mode.ToString(); expected = a.Value.GetString(); return true;
                case "reactorCooling": actual = core?.Cooling; expected = a.Value.GetBoolean(); return true;
                case "reactorSuspect": actual = core?.SuspectFuel; expected = a.Value.GetBoolean(); return true;
                case "reactorRevision": actual = core?.Revision; expected = a.Value.GetInt64(); return true;
                case "reactorWork": actual = core?.WorkMilliseconds; expected = a.Value.GetInt64(); return true;
                case "reactorRemaining": actual = core?.RemainingFuelMilliseconds; expected = a.Value.GetInt64(); return true;
                case "reactorInstability": actual = core?.InstabilityMilliseconds; expected = a.Value.GetInt64(); return true;
                case "reserve": actual = power?.Available; expected = a.Value.GetInt64(); return true;
                case "generatedPower": actual = power?.Generated; expected = a.Value.GetInt64(); return true;
                case "spentPower": actual = power?.Spent; expected = a.Value.GetInt64(); return true;
                case "deliveredPower": actual = power?.Delivered; expected = a.Value.GetInt64(); return true;
                case "spilledPower": actual = power?.Spilled; expected = a.Value.GetInt64(); return true;
                case "lastReactorEvent": actual = trace?.ReactorEvent?.ToString(); expected = a.Value.GetString(); return true;
                case "lastReactorRisk": actual = trace?.ReactorChange?.Risk.ToString(); expected = a.Value.GetString(); return true;
                case "lastReactorAt": actual = trace?.ReactorChange?.ShiftMilliseconds; expected = a.Value.GetInt64(); return true;
                case "lastReactorCause": actual = trace?.ReactorChange?.CauseId; expected = Id(a.Value.GetInt32()); return true;
                case "lastReactorCyclePresent": actual = trace != null && trace.ReactorChange!.CycleId != Guid.Empty;
                    expected = a.Value.GetBoolean(); return true;
                default: return false;
            }
        }
    }
}
