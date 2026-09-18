using System;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    // Tool input translation only. All rules, timing and quantities come from the real libraries.
    internal static class ProductionScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("production", out var setup)) return;
            foreach (var m in setup.GetProperty("machines").EnumerateArray())
                world.Production.RegisterMachine(Id(checked((int)Number(m, "id"))), new MachineRecipe(
                    Id(checked((int)Number(m, "recipe"))), Choice<MaterialKind>(m, "input"), Choice<MaterialKind>(m, "output"),
                    Number(m, "duration"), Number(m, "bypassDuration"), Number(m, "jamAfter"), checked((int)Number(m, "capacity")),
                    checked((int)Number(m, "yield", 1000)), checked((int)Number(m, "tolerance", 500)), checked((int)Number(m, "outputMoisture", 0))));
            foreach (var b in setup.GetProperty("batches").EnumerateArray())
                world.Production.RegisterBatch(Id(checked((int)Number(b, "container"))), Id(checked((int)Number(b, "id"))),
                    Id(checked((int)Number(b, "origin"))), Id(checked((int)Number(b, "cause"))), Choice<MaterialKind>(b, "kind"),
                    checked((int)Number(b, "units")), checked((int)Number(b, "moisture", 0)), checked((int)Number(b, "contamination", 0)));
        }
        internal static string Execute(JsonElement step, WorldSession world, Guid epoch, Guid connection)
        {
            var payload = new ProductionRequest(Choice<ProductionAction>(step, "action"), Number(step, "machineRevision"),
                step.TryGetProperty("container", out var c) ? Id(c.GetInt32()) : Guid.Empty,
                Number(step, "objectRevision", 0), Number(step, "batchRevision", 0), Number(step, "lease", 0),
                Flag(step, "bypass", false), Flag(step, "powered", false));
            var reply = world.ExecuteInteraction(connection, new InteractionCommand(epoch, Number(step, "seq"),
                InteractionKind.Production, Id(checked((int)Number(step, "machine"))), production: payload));
            return reply.Production?.Status.ToString() ?? reply.Status.ToString();
        }
        internal static bool TryRead(JsonProperty assertion, JsonElement selectors, WorldSession world,
            out object? actual, out object? expected)
        {
            var machine = world.Production.GetMachine(Id(checked((int)Number(selectors, "machine", 700))));
            var batch = world.Production.GetBatch(Id(checked((int)Number(selectors, "batch", 600))));
            var records = world.Trace.Records;
            var last = records.Count == 0 ? null : records[records.Count - 1];
            var summary = world.Production.Summary; actual = null; expected = null;
            switch (assertion.Name)
            {
                case "machine": case "batch": return true;
                case "lastProductionEvent": actual = last?.ProductionEvent?.ToString(); expected = assertion.Value.GetString(); return true;
                case "lastCyclePresent": actual = last != null && last.CycleId != Guid.Empty; expected = assertion.Value.GetBoolean(); return true;
                case "lastCycleBypassed": actual = last?.BypassedInspection; expected = assertion.Value.GetBoolean(); return true;
                case "lastOutputPresent": actual = last != null && last.OutputBatchId != Guid.Empty; expected = assertion.Value.GetBoolean(); return true;
                case "lastMaterialCause": actual = last?.MaterialCauseId; expected = Id(assertion.Value.GetInt32()); return true;
                case "lastReceiptCancelled": actual = last == null ? null : world.Production.GetConversion(last.CycleId)?.Cancelled;
                    expected = assertion.Value.GetBoolean(); return true;
                case "machineMode": actual = machine?.Mode.ToString(); expected = assertion.Value.GetString(); return true;
                case "machinePower": actual = machine?.Powered; expected = assertion.Value.GetBoolean(); return true;
                case "machineWork": actual = machine?.WorkMilliseconds; expected = assertion.Value.GetInt64(); return true;
                case "machineRevision": actual = machine?.Revision; expected = assertion.Value.GetInt64(); return true;
                case "batchKind": actual = batch?.Kind.ToString(); expected = assertion.Value.GetString(); return true;
                case "batchUnits": actual = batch?.Units; expected = assertion.Value.GetInt32(); return true;
                case "batchFlags": actual = batch?.Flags.ToString(); expected = assertion.Value.GetString(); return true;
                case "batchMoisture": actual = batch?.Moisture; expected = assertion.Value.GetInt32(); return true;
                case "slottedIn": actual = batch == null ? Guid.Empty : world.GetObject(batch.ContainerId)?.SlotId ?? Guid.Empty;
                    expected = assertion.Value.GetInt32() == 0 ? Guid.Empty : Id(assertion.Value.GetInt32()); return true;
                case "issuedUnits": actual = summary.IssuedUnits; expected = assertion.Value.GetInt64(); return true;
                case "activeUnits": actual = summary.ActiveUnits; expected = assertion.Value.GetInt64(); return true;
                case "wasteUnits": actual = summary.WasteUnits; expected = assertion.Value.GetInt64(); return true;
                case "completedCycles": actual = summary.CompletedCycles; expected = assertion.Value.GetInt32(); return true;
                case "cancelledCycles": actual = summary.CancelledCycles; expected = assertion.Value.GetInt32(); return true;
                case "pendingCycles": actual = summary.PendingCycles; expected = assertion.Value.GetInt32(); return true;
                default: return false;
            }
        }
    }
}
