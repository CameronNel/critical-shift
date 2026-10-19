#nullable enable
using System;
using CriticalShift.Application;

namespace CriticalShift.Presentation
{
    /// <summary>Read-only clinical guidance over detached canonical state. Never admits or performs treatment.</summary>
    public static class SandboxMedicalReadout
    {
        public static string Controls(MedicalView station) => station.Phase switch
        {
            MedicalPhase.Empty => "E load a held unconscious down worker",
            MedicalPhase.Treating => "Treatment running · cancel from panel before ejection",
            MedicalPhase.Ready => "E eject patient safely · standing recovery follows separately",
            _ => "E eject patient · R request stabilization only if still unconscious (" + station.ReserveCost + " reserve + 1 cartridge)"
        };

        public static string Summary(MedicalView station, WorkerView? patient, long elapsed, long remaining, long availableReserve)
        {
            long now = Math.Max(0, elapsed), shiftLeft = Math.Max(0, remaining);
            string text = "Medical " + station.Phase + " · cartridges " + station.Cartridges + "\n" +
                "Stabilization " + SandboxMachineReadout.Seconds(station.DurationMilliseconds) + " · cost " + station.ReserveCost +
                " reserve (available " + Math.Max(0, availableReserve) + ") + 1 cartridge\n" +
                "Patient contamination must be at most " + station.MaximumContamination + "/100.\n" +
                "Recovery delay " + SandboxMachineReadout.Seconds(station.RecoveryDelayMilliseconds) + " after stabilization; eject and check clearance before standing.";
            bool matched = patient != null && patient.Epoch == station.Epoch && patient.Id == station.PatientId;
            if (matched)
                text += "\nPatient " + patient!.Awareness + " / " + patient.Pose + " · contamination " + patient.Contamination + "/100.";
            else if (station.Phase != MedicalPhase.Empty) text += "\nPatient condition unavailable.";
            if (station.Phase == MedicalPhase.Treating)
            {
                long workLeft = station.DueAtMilliseconds > now ? station.DueAtMilliseconds - now : 0;
                text += "\nTreatment " + SandboxMachineReadout.Seconds(workLeft) + " remaining on the shift clock.";
                if (workLeft > shiftLeft) text += " The shift will end before this treatment finishes.";
            }
            else if ((station.Phase == MedicalPhase.Loaded || station.Phase == MedicalPhase.Interrupted) && station.DurationMilliseconds > shiftLeft)
                text += "\nThe remaining shift is too short to finish a new treatment; starting still consumes its cost.";
            if (station.Phase == MedicalPhase.Ready && matched)
            {
                long recoveryLeft = patient!.RecoveryNotBeforeMilliseconds > now ? patient.RecoveryNotBeforeMilliseconds - now : 0;
                text += "\nEject before standing recovery · current recovery wait " + SandboxMachineReadout.Seconds(recoveryLeft) + " plus clearance checks.";
            }
            return text;
        }

        public static string Result(MedicalReply reply)
        {
            var station = reply.Station;
            switch (reply.Status)
            {
                case MedicalStatus.Applied:
                    switch (reply.Change?.Kind)
                    {
                        case MedicalEvent.Inserted: return "Patient loaded. " + (station == null ? "" : Controls(station));
                        case MedicalEvent.Started: return "Stabilization started · spent " + reply.Change.ReserveSpent + " reserve and 1 cartridge.";
                        case MedicalEvent.Cancelled: return "Treatment cancelled; consumed reserve and cartridge stay spent. Eject the patient before recovery.";
                        case MedicalEvent.Ejected: case MedicalEvent.EmergencyEjected: return "Patient discharged down; standing recovery still needs its delay and clear space.";
                        default: return "Medical action completed.";
                    }
                case MedicalStatus.UnknownStation: return "Medical station unavailable.";
                case MedicalStatus.RevisionConflict: return "The patient or chamber changed. Check current state and try again.";
                case MedicalStatus.InvalidPatient: return "Load an unconscious down worker. An alert down worker needs separate standing recovery.";
                case MedicalStatus.Contaminated: return "Wash the patient to at most " + (station?.MaximumContamination ?? 0) + "/100 contamination before stabilization.";
                case MedicalStatus.NoCartridge: return "This chamber has no medical cartridges left.";
                case MedicalStatus.InsufficientReserve: return "Need " + (station?.ReserveCost ?? 0) + " shared reserve. Generate power or use backup.";
                case MedicalStatus.CustodyRejected: return "Patient custody changed. Check the current suit grip and chamber.";
                case MedicalStatus.InvalidTime: return "Treatment timing is unavailable.";
                default: return "Medical action blocked. " + (station == null ? "Check the current chamber." : Controls(station));
            }
        }
    }
}
