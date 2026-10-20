using System;
using System.Linq;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    internal static class ContractScenarioSteps
    {
        internal static void Bind(JsonElement spec, WorldSession world)
        {
            if (!spec.TryGetProperty("contract", out var contract)) return;
            var waves = contract.GetProperty("waves").EnumerateArray().Select(w => new GridDemandWave(
                Id(checked((int)Number(w, "id"))), Text(w, "label"), Number(w, "end"), Number(w, "energy"),
                Number(w, "warning", 0))).ToArray();
            world.Contracts.Register(new ShiftContractDefinition(Id(checked((int)Number(contract, "id"))),
                Text(contract, "title"), waves));
        }

        internal static bool TryRead(JsonProperty a, JsonElement assertions, WorldSession world,
            out object? actual, out object? expected)
        {
            var contract = world.Contracts.View;
            var wave = assertions.TryGetProperty("wave", out var selector)
                ? contract?.Waves.SingleOrDefault(w => w.Id == Id(selector.GetInt32())) : contract?.Current;
            actual = null; expected = null;
            switch (a.Name)
            {
                case "wave": return true;
                case "contractPresent": actual = contract != null; expected = a.Value.GetBoolean(); return true;
                case "contractComplete": actual = contract?.Complete; expected = a.Value.GetBoolean(); return true;
                case "contractMet": actual = contract?.AllPeriodsMet; expected = a.Value.GetBoolean(); return true;
                case "contractDelivered": actual = contract?.DeliveredEnergyUnits; expected = a.Value.GetInt64(); return true;
                case "contractSettled": actual = contract?.SettledPeriods; expected = a.Value.GetInt32(); return true;
                case "contractOutcome": actual = contract?.Outcome.ToString(); expected = a.Value.GetString(); return true;
                case "currentWave": actual = contract?.Current?.Id; expected = Id(a.Value.GetInt32()); return true;
                case "upcomingWave": actual = contract?.Upcoming?.Id; expected = Id(a.Value.GetInt32()); return true;
                case "upcomingVisible": actual = contract?.Upcoming != null; expected = a.Value.GetBoolean(); return true;
                case "waveDelivered": actual = wave?.DeliveredEnergyUnits; expected = a.Value.GetInt64(); return true;
                case "waveMet": actual = wave?.Met; expected = a.Value.GetBoolean(); return true;
                case "waveSettled": actual = wave?.Settled; expected = a.Value.GetBoolean(); return true;
                case "waveShortfall": actual = wave?.ShortfallEnergyUnits; expected = a.Value.GetInt64(); return true;
                default: return false;
            }
        }
    }
}
