#nullable enable
using System;
using CriticalShift.Application;

namespace CriticalShift.Presentation
{
    /// <summary>Read-only supply objective text shared by the full and hidden-panel HUD.</summary>
    internal static class SandboxContractReadout
    {
        private static bool Active(ShiftContractView contract) => contract.Phase == WorldPhase.Setup ||
            contract.Phase == WorldPhase.Running || contract.Phase == WorldPhase.Paused;

        internal static string Progress(ShiftContractView contract)
        {
            var current = contract.Current;
            if (!Active(contract) || current == null)
                return "Contract " + contract.Outcome + " · delivered " + contract.DeliveredEnergyUnits + " energy";
            return current.Label + " · " + current.DeliveredEnergyUnits + "/" + current.RequiredEnergyUnits +
                " energy · " + Clock(current.EndMilliseconds - contract.ElapsedMilliseconds) + " left";
        }

        internal static string Upcoming(ShiftContractView contract)
        {
            var upcoming = contract.Upcoming;
            if (!Active(contract) || upcoming == null) return "";
            return "Next: " + upcoming.Label + " in " + Clock(upcoming.StartMilliseconds - contract.ElapsedMilliseconds) +
                " · " + upcoming.RequiredEnergyUnits + " energy in that window";
        }

        internal static string LatestMissed(ShiftContractView contract)
        {
            GridDemandView? latest = null; int missed = 0;
            foreach (var wave in contract.Waves)
                if (wave.Settled && !wave.Met) { latest = wave; missed++; }
            return latest == null ? "" : "Missed " + missed + (missed == 1 ? " window" : " windows") + " · " +
                latest.Label + " short by " + latest.ShortfallEnergyUnits + " energy";
        }

        internal static string Compact(ShiftContractView contract)
        {
            string text = contract.Title + "\n" + Progress(contract);
            string next = Upcoming(contract), missed = LatestMissed(contract);
            if (next.Length != 0) text += "\n" + next;
            if (missed.Length != 0) text += "\n" + missed;
            return text;
        }

        internal static string Clock(long milliseconds)
        {
            long seconds = Math.Max(0, milliseconds) / 1000;
            return (seconds / 60).ToString("D2") + ":" + (seconds % 60).ToString("D2");
        }
    }
}
