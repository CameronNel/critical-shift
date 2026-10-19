#nullable enable
using System;
using System.Globalization;
using CriticalShift.Application;

namespace CriticalShift.Presentation
{
    /// <summary>Read-only operator guidance. It never predicts admission or submits an action.</summary>
    public static class SandboxMachineReadout
    {
        internal static string Seconds(long milliseconds) => (Math.Max(0, milliseconds) / 1000m).ToString("0.###", CultureInfo.InvariantCulture) + "s";
        private static string Material(MaterialKind kind) => kind switch
        {
            MaterialKind.Ore => "ore", MaterialKind.CrushedOre => "crushed ore",
            MaterialKind.Fuel => "fuel", MaterialKind.SpentFuel => "spent fuel", _ => "material"
        };
        private static string Moisture(int value) => (value / 10m).ToString("0.#", CultureInfo.InvariantCulture) + "%";
        internal static string Recipe(MachineView state)
        {
            var recipe = state.Recipe;
            if (state.IsDrying)
                return "Safe drying: " + Seconds(recipe.DurationMilliseconds) + " · " + Material(recipe.Input) + " · up to " +
                    recipe.MaximumUnits + " units · target moisture " + Moisture(recipe.OutputMoisture) +
                    ". Quantity, contamination and suspect history stay with the material. No inspection bypass.";
            return Material(recipe.Input) + " → " + Material(recipe.Output) + " · up to " + recipe.MaximumUnits + " units\n" +
                "Normal " + Seconds(recipe.DurationMilliseconds) + " · bypass " + Seconds(recipe.BypassDurationMilliseconds) +
                " · safe moisture at most " + Moisture(recipe.MoistureTolerance) +
                ". Wet bypass jams after " + Seconds(recipe.WetJamAfterMilliseconds) + " of processing; output retains suspect inspection history.";
        }
        public static string Controls(MachineView state)
        {
            switch (state.Mode)
            {
                case ProductionMode.Jammed: return state.Powered ? "F isolate power, then R repair jam" : "R repair jam · keep power off";
                case ProductionMode.PowerPaused: return state.Powered ? "R resume cycle · F isolates power" : "F restore power, then R resume cycle";
                case ProductionMode.Processing: return "Cycle running · F isolate power to pause";
                case ProductionMode.OutputReady: return "E eject output · F " + (state.Powered ? "isolates" : "restores") + " power";
                default:
                    if (!state.ContainerId.HasValue) return "E insert a compatible held container · F " + (state.Powered ? "isolates" : "restores") + " power";
                    if (!state.Powered) return "F restore power · E eject input";
                    return state.IsDrying ? "R start safe drying · E eject input · F isolate power" :
                        "R start normal cycle · B bypass inspection · E eject input · F isolate power";
            }
        }
        public static string Result(ProductionReply reply, ProductionAction? action = null)
        {
            var machine = reply.Machine;
            switch (reply.Status)
            {
                case ProductionStatus.Applied:
                    switch (action)
                    {
                        case ProductionAction.Insert: return "Material loaded. " + Next(machine);
                        case ProductionAction.Eject: return "Material ejected.";
                        case ProductionAction.Start: return "Cycle started: " + (machine == null ? "" : Seconds(machine.DurationMilliseconds)) +
                            (machine?.BypassedInspection == true ? ". Inspection bypass: wet input jams after " + Seconds(machine.Recipe.WetJamAfterMilliseconds) +
                                " of processing; output keeps suspect history." : ".");
                        case ProductionAction.SetPower: return (machine?.Powered == true ? "Power restored. " : "Power isolated. ") + Next(machine);
                        case ProductionAction.Repair: return "Jam repaired. " + Next(machine);
                        case ProductionAction.Resume: return "Cycle resumed.";
                        case ProductionAction.CancelCycle: return "Cycle cancelled; original input retained.";
                        default: return "Machine action completed. " + Next(machine);
                    }
                case ProductionStatus.NoChange: return "No machine change. " + Next(machine);
                case ProductionStatus.UnknownMachine: return "Machine unavailable.";
                case ProductionStatus.UnknownBatch: return "This container has no available material.";
                case ProductionStatus.NoInput: return "Insert a compatible material container first.";
                case ProductionStatus.Occupied: return "Input socket occupied. Eject its container first.";
                case ProductionStatus.RevisionConflict: return "The machine or input changed. Try the action again using its current state.";
                case ProductionStatus.WrongInput: return "This machine needs " + (machine == null ? "a compatible input" : Material(machine.Recipe.Input)) + ".";
                case ProductionStatus.OverCapacity: return "Container exceeds " + (machine == null ? "machine capacity" : machine.Recipe.MaximumUnits + " units") + ".";
                case ProductionStatus.WetInput: return "Input is too wet for a safe cycle. Use the dryer; wet bypass jams and leaves suspect history.";
                case ProductionStatus.OutputTooSmall: return "Not enough input for one output unit.";
                case ProductionStatus.NoPower: return "Restore machine power before starting or resuming.";
                case ProductionStatus.InvalidState: return "This action is blocked. " + Next(machine);
                case ProductionStatus.PowerMustBeOff: return "Isolate power before repairing or cancelling.";
                case ProductionStatus.HistoryCapacityReached: return "This trial's processing history is full. Restart the fixture.";
                case ProductionStatus.CustodyRejected: return "Container unavailable for transfer. Check your grip and its socket.";
                case ProductionStatus.AlreadyConditioned: return "Material is already dry enough for this dryer.";
                case ProductionStatus.BypassUnavailable: return "This machine requires its safe cycle.";
                default: return "Machine action unavailable.";
            }
        }
        private static string Next(MachineView? machine) => machine == null ? "Check the current machine." : Controls(machine);
    }
}
