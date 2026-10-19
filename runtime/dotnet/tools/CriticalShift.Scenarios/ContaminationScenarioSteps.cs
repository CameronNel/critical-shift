using System;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    internal static class ContaminationScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("contaminationSources", out var sources)) return;
            if (sources.ValueKind != JsonValueKind.Array || sources.GetArrayLength() > 32)
                throw new ArgumentException("Contamination sources must be a bounded array.");
            foreach (var source in sources.EnumerateArray())
                world.RegisterWorkerContaminationSource(Id(checked((int)Number(source, "id"))),
                    new WorkerContaminationDefinition(Choice<WorkerContaminationKind>(source, "kind"),
                        checked((int)Number(source, "units")), Number(source, "cooldown", 500)));
        }
        internal static string Execute(JsonElement step, WorldSession world, Guid epoch, Guid actor) =>
            world.ObserveWorkerContamination(epoch, actor, Id(checked((int)Number(step, "source"))), Number(step, "seq"),
                Id(checked((int)Number(step, "cause"))), Number(step, "sample", world.View.ElapsedMilliseconds)).Status.ToString();
    }
}
