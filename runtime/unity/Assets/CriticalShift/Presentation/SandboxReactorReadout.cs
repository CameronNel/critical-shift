#nullable enable
using System;
using CriticalShift.Application;

namespace CriticalShift.Presentation
{
    /// <summary>Current immutable instruments and next-step guidance, never a command admission decision.</summary>
    public static class SandboxReactorReadout
    {
        public static string RoutingName(ReactorOutputRouting route) => route switch
        { ReactorOutputRouting.GridPriority => "Grid priority", ReactorOutputRouting.ReservePriority => "Reserve priority", _ => "Balanced" };

        public static string Output(ReactorView state)
        {
            long total = (long)state.Definition.ReservePerQuantum + state.Definition.GridPerQuantum;
            long reserve = state.OutputRouting == ReactorOutputRouting.GridPriority ? 0 :
                state.OutputRouting == ReactorOutputRouting.ReservePriority ? total : state.Definition.ReservePerQuantum;
            return RoutingName(state.OutputRouting) + ": grid " + (total - reserve) + " / reserve " + reserve + " each " +
                SandboxMachineReadout.Seconds(state.Definition.PowerQuantumMilliseconds) + " of running work. " +
                (state.OutputRouting == ReactorOutputRouting.GridPriority ? "New output does not refill the emergency reserve." :
                 state.OutputRouting == ReactorOutputRouting.ReservePriority ? "New output makes no contract delivery; a full reserve spills excess." : "A full reserve spills its share.");
        }

        public static string Summary(ReactorView state) =>
            "Fuel running time " + SandboxMachineReadout.Seconds(state.RemainingFuelMilliseconds) +
            " · reserve " + state.Power.Available + "/" + state.Power.Capacity + " · grid " + state.Power.Delivered + " · spilled " + state.Power.Spilled +
            "\nStart/restart " + state.Definition.StartupCost + " reserve · emergency cooling " + state.Definition.EmergencyCost +
            " reserve removes up to " + SandboxMachineReadout.Seconds(state.Definition.EmergencyReliefMilliseconds) + " instability." +
            "\nInstability " + SandboxMachineReadout.Seconds(state.InstabilityMilliseconds) + " · trip " + SandboxMachineReadout.Seconds(state.Definition.TripMilliseconds) +
            " · trip reset / spent-fuel eject threshold " + SandboxMachineReadout.Seconds(state.Definition.ResetMilliseconds) + ".\n" + Output(state);

        public static string Controls(ReactorView state)
        {
            string controls;
            switch (state.Mode)
            {
                case ReactorMode.Empty: controls = "E load held fuel"; break;
                case ReactorMode.Tripped:
                    controls = !state.Cooling ? "F restore cooling; trip reset requires cooling" : state.CanResetTrip ?
                        "R reset trip, then R restart (" + state.Definition.StartupCost + " reserve)" :
                        "Wait " + SandboxMachineReadout.Seconds(Math.Max(0, state.InstabilityMilliseconds - state.Definition.ResetMilliseconds)) +
                        " on the shift clock before R resets; C emergency cooling costs " + state.Definition.EmergencyCost + " reserve";
                    break;
                case ReactorMode.Exhausted:
                    controls = state.CanEject ? "E eject spent fuel, then load fresh fuel" : !state.Cooling ?
                        "F restore cooling before the spent-fuel ejection interlock clears" :
                        "Wait " + SandboxMachineReadout.Seconds(Math.Max(0, state.InstabilityMilliseconds - state.Definition.ResetMilliseconds)) + " before E ejects spent fuel";
                    break;
                case ReactorMode.Running:
                    controls = !state.Cooling ? "Cooling lost: F restore cooling · X shut down · C emergency cooling" :
                        state.SuspectFuel ? "Suspect fuel continues building instability despite cooling · X shut down · C emergency cooling" :
                        "Core running · X shut down · F closes cooling";
                    break;
                default:
                    controls = !state.Cooling ? "F open cooling before R starts" : !state.CanStart ?
                        "Wait for instability below " + SandboxMachineReadout.Seconds(state.Definition.WarningMilliseconds) + " before R starts" :
                        state.Power.Available < state.Definition.StartupCost ? "Startup needs " + state.Definition.StartupCost +
                        " reserve; available " + state.Power.Available + ". " + Backup(state) :
                        "R start reactor (" + state.Definition.StartupCost + " reserve) · X shut down";
                    break;
            }
            if (state.Mode == ReactorMode.Loaded) controls += " · E eject unused fuel";
            return controls + " · V cycle output routing (" + RoutingName(state.OutputRouting) + ")";
        }

        private static string Backup(ReactorView state) => state.EmergencyPower == null ? "No backup source is installed." :
            state.EmergencyPower.Running ? "Backup is running; wait for its reserve output." :
            state.EmergencyPower.RemainingCharges <= 0 ? "No backup charges remain." :
            state.Power.Capacity - state.Power.Available < state.EmergencyPower.ReserveUnitsPerCharge ?
                "Backup needs " + state.EmergencyPower.ReserveUnitsPerCharge + " free reserve capacity; use reserve first." :
                "Start finite backup from the reactor panel.";

        public static string Result(ReactorReply reply, ReactorAction? action = null)
        {
            var state = reply.State;
            string next = state == null ? "Reactor unavailable." : Controls(state);
            switch (reply.Status)
            {
                case ReactorStatus.Applied:
                    if (reply.Change?.Kind == ReactorEvent.OutputRoutingChanged) return "Output routing changed. " + (state == null ? "" : Output(state));
                    return "Reactor control applied. " + next;
                case ReactorStatus.NoChange: return "Control already in that state. " + next;
                case ReactorStatus.NoCooling: return "Open cooling before starting the reactor.";
                case ReactorStatus.Unsafe: return "Thermal interlock blocked this control. " + next;
                case ReactorStatus.InsufficientReserve:
                    long cost = state == null ? 0 : action == ReactorAction.Start ? state.Definition.StartupCost :
                        action == ReactorAction.EmergencyCooling ? state.Definition.EmergencyCost : action == ReactorAction.AuxiliaryPower ? state.Definition.AuxiliaryCost : 0;
                    return "Insufficient reserve" + (cost == 0 || state == null ? "." : ": needs " + cost + ", available " + state.Power.Available + ".") +
                        (state == null ? "" : " " + Backup(state));
                case ReactorStatus.WrongFuel: return "Load fuel, not ore or spent fuel.";
                case ReactorStatus.HistoryCapacityReached: return "This trial's material history is full; restart the fixture.";
                case ReactorStatus.CustodyRejected: return "Fuel transfer blocked; check the current grip and reactor socket.";
                case ReactorStatus.NoBackupCharge: return "No backup charges remain.";
                case ReactorStatus.InsufficientHeadroom: return "Use some reserve before starting backup; its complete output must fit at startup.";
                default: return "Reactor control blocked (" + reply.Status + "). " + next;
            }
        }
    }
}
