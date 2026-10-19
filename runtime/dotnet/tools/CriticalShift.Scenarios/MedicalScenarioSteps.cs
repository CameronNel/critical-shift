using System;
using System.Linq;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    internal static class MedicalScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("medical", out var m)) return;
            int bodyBase = checked((int)Number(m, "bodyBase", 650));
            for (int i = 0; i < 4; i++) world.RegisterWorkerBody(Id(i + 1), Id(checked(bodyBase + i)));
            world.Medical.Register(Id(checked((int)Number(m, "id", 950))), new MedicalDefinition(
                Number(m, "duration", 1000), Number(m, "cost", 6), checked((int)Number(m, "cartridges", 2)),
                Number(m, "recoveryDelay", 100), checked((int)Number(m, "maximumContamination", 50))));
        }
        internal static string Execute(JsonElement step, WorldSession world, Guid epoch, Guid connection)
        {
            var action = Choice<MedicalAction>(step, "action");
            var request = new MedicalRequest(action, Number(step, "stationRevision"),
                step.TryGetProperty("body", out var body) ? Id(body.GetInt32()) : Guid.Empty,
                Number(step, "objectRevision", 0), Number(step, "lease", 0), Number(step, "patientRevision", 0));
            var reply = world.ExecuteInteraction(connection, new InteractionCommand(epoch, Number(step, "seq"),
                action == MedicalAction.EmergencyEject ? InteractionKind.MedicalEgress : InteractionKind.Medical,
                Id(checked((int)Number(step, "station", 950))), medical: request));
            return reply.Medical?.Status.ToString() ?? reply.Status.ToString();
        }
        internal static bool TryRead(JsonProperty a, WorldSession world, out object? actual, out object? expected)
        {
            var medical = world.Medical.View; var summary = world.Medical.Summary;
            var change = world.Trace.Records.LastOrDefault(r => r.Changed && r.MedicalChange != null)?.MedicalChange;
            actual = null; expected = null;
            switch (a.Name)
            {
                case "medicalPresent": actual = medical != null; expected = a.Value.GetBoolean(); return true;
                case "medicalPhase": actual = medical?.Phase.ToString(); expected = a.Value.GetString(); return true;
                case "medicalRevision": actual = medical?.Revision; expected = a.Value.GetInt64(); return true;
                case "medicalCartridges": actual = summary.RemainingCartridges; expected = a.Value.GetInt32(); return true;
                case "medicalUsed": actual = summary.UsedCartridges; expected = a.Value.GetInt32(); return true;
                case "medicalCompleted": actual = summary.CompletedCycles; expected = a.Value.GetInt32(); return true;
                case "medicalCancelled": actual = summary.CancelledCycles; expected = a.Value.GetInt32(); return true;
                case "medicalInterrupted": actual = summary.InterruptedCycles; expected = a.Value.GetInt32(); return true;
                case "medicalPatientPresent": actual = medical != null && medical.PatientId != Guid.Empty; expected = a.Value.GetBoolean(); return true;
                case "lastMedicalEvent": actual = change?.Kind.ToString(); expected = a.Value.GetString(); return true;
                case "lastMedicalAt": actual = change?.ShiftMilliseconds; expected = a.Value.GetInt64(); return true;
                case "lastMedicalCause": actual = change?.InjuryCauseId; expected = Id(a.Value.GetInt32()); return true;
                default: return false;
            }
        }
    }
}
