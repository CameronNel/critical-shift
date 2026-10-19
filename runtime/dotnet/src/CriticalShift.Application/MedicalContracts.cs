#nullable enable
using System;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    public enum MedicalAction { Insert, Start, Cancel, Eject, EmergencyEject }
    public enum MedicalStatus { Applied, UnknownStation, RevisionConflict, InvalidState, InvalidPatient, Contaminated, NoCartridge, InsufficientReserve, CustodyRejected, InvalidTime }
    public enum MedicalPhase { Empty, Loaded, Treating, Ready, Interrupted }
    public enum MedicalEvent { Inserted, Started, Completed, Cancelled, Interrupted, Ejected, PatientDisconnected, EmergencyEjected }

    public sealed class MedicalDefinition
    {
        public MedicalDefinition(long durationMilliseconds = 3000, long reserveCost = 6, int cartridges = 2,
            long recoveryDelayMilliseconds = 500, int maximumContamination = 50)
        { Rules = new MedicalRules(durationMilliseconds, reserveCost, cartridges, recoveryDelayMilliseconds, maximumContamination); }
        internal MedicalRules Rules { get; }
        public long DurationMilliseconds => Rules.DurationMilliseconds;
        public long ReserveCost => Rules.ReserveCost;
        public int InitialCartridges => Rules.Cartridges;
        public long RecoveryDelayMilliseconds => Rules.RecoveryDelayMilliseconds;
        public int MaximumContamination => Rules.MaximumContamination;
    }
    public sealed class MedicalRequest
    {
        public const int CurrentVersion = 1;
        public MedicalRequest(MedicalAction action, long stationRevision, Guid bodyId = default,
            long objectRevision = 0, long leaseGeneration = 0, long patientRevision = 0, int version = CurrentVersion)
        { Action = action; StationRevision = stationRevision; BodyId = bodyId; ObjectRevision = objectRevision;
          LeaseGeneration = leaseGeneration; PatientRevision = patientRevision; Version = version; }
        public MedicalAction Action { get; }
        public long StationRevision { get; }
        public Guid BodyId { get; }
        public long ObjectRevision { get; }
        public long LeaseGeneration { get; }
        public long PatientRevision { get; }
        public int Version { get; }
        internal bool IsWellFormed => Version == CurrentVersion && StationRevision >= 0 && ObjectRevision >= 0 && PatientRevision >= 0 &&
            (Action == MedicalAction.Insert ? BodyId != Guid.Empty && LeaseGeneration > 0 && PatientRevision == 0 :
             BodyId == Guid.Empty && LeaseGeneration == 0 &&
             (Action == MedicalAction.Start ? ObjectRevision == 0 : PatientRevision == 0 &&
              (Action == MedicalAction.Eject || Action == MedicalAction.EmergencyEject || Action == MedicalAction.Cancel && ObjectRevision == 0)));
        internal bool Same(MedicalRequest other) => Action == other.Action && StationRevision == other.StationRevision &&
            BodyId == other.BodyId && ObjectRevision == other.ObjectRevision && LeaseGeneration == other.LeaseGeneration &&
            PatientRevision == other.PatientRevision && Version == other.Version;
    }
    public sealed class MedicalView
    {
        internal MedicalView(Guid epoch, MedicalStationState state)
        { Epoch = epoch; Id = state.Id; Revision = state.Revision; Phase = (MedicalPhase)(int)state.Mode;
          BodyId = state.BodyId; PatientId = state.PatientId; CycleId = state.CycleId; PatientEpisodeAtStart = state.PatientEpisode;
          PatientRevisionAtStart = state.PatientRevision;
          StartedAtMilliseconds = state.StartedAtMilliseconds; DueAtMilliseconds = state.DueAtMilliseconds;
          Cartridges = state.Cartridges; DurationMilliseconds = state.Rules.DurationMilliseconds; ReserveCost = state.Rules.ReserveCost; }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public long Revision { get; }
        public MedicalPhase Phase { get; }
        public Guid BodyId { get; }
        public Guid PatientId { get; }
        public Guid CycleId { get; }
        public long PatientEpisodeAtStart { get; }
        public long PatientRevisionAtStart { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public int Cartridges { get; }
        public long DurationMilliseconds { get; }
        public long ReserveCost { get; }
    }
    public sealed class MedicalChange
    {
        internal MedicalChange(MedicalEvent kind, MedicalView station, Guid cycle, Guid patient, Guid body,
            Guid injuryCause, long time, long spent = 0, int cartridges = 0, WorkerView? worker = null)
        { Kind = kind; Station = station; CycleId = cycle; PatientId = patient; BodyId = body; InjuryCauseId = injuryCause;
          ShiftMilliseconds = time; ReserveSpent = spent; CartridgesUsed = cartridges; Worker = worker; }
        public MedicalEvent Kind { get; }
        public MedicalView Station { get; }
        public Guid CycleId { get; }
        public Guid PatientId { get; }
        public Guid BodyId { get; }
        public Guid InjuryCauseId { get; }
        public long ShiftMilliseconds { get; }
        public long ReserveSpent { get; }
        public int CartridgesUsed { get; }
        public WorkerView? Worker { get; }
    }
    public sealed class MedicalReply
    {
        internal MedicalReply(MedicalStatus status, MedicalView? station, MedicalChange? change = null)
        { Status = status; Station = station; Change = change; }
        public MedicalStatus Status { get; }
        public MedicalView? Station { get; }
        public MedicalChange? Change { get; }
    }
    public sealed class MedicalSummary
    {
        internal MedicalSummary(int remaining, int used, int completed, int cancelled, int interrupted)
        { RemainingCartridges = remaining; UsedCartridges = used; CompletedCycles = completed; CancelledCycles = cancelled; InterruptedCycles = interrupted; }
        public int RemainingCartridges { get; }
        public int UsedCartridges { get; }
        public int CompletedCycles { get; }
        public int CancelledCycles { get; }
        public int InterruptedCycles { get; }
    }
}
