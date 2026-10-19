#nullable enable
using System;

namespace CriticalShift.Features.Workers.Domain
{
    public enum MedicalMode { Empty, Loaded, Treating, Ready, Interrupted }

    public sealed class MedicalRules
    {
        public MedicalRules(long durationMilliseconds, long reserveCost, int cartridges,
            long recoveryDelayMilliseconds = 500, int maximumContamination = 50)
        {
            if (durationMilliseconds < 1 || durationMilliseconds > 60000 || reserveCost < 1 || reserveCost > 100000 ||
                cartridges < 0 || cartridges > 32 || recoveryDelayMilliseconds < 0 || recoveryDelayMilliseconds > 60000 ||
                maximumContamination < 0 || maximumContamination > 100) throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            DurationMilliseconds = durationMilliseconds; ReserveCost = reserveCost; Cartridges = cartridges;
            RecoveryDelayMilliseconds = recoveryDelayMilliseconds; MaximumContamination = maximumContamination;
        }
        public long DurationMilliseconds { get; }
        public long ReserveCost { get; }
        public int Cartridges { get; }
        public long RecoveryDelayMilliseconds { get; }
        public int MaximumContamination { get; }
    }

    /// <summary>One bounded chamber cycle. Application coordinates body custody, worker condition and reserve.</summary>
    public sealed class MedicalStationState
    {
        public MedicalStationState(Guid id, MedicalRules rules)
        {
            if (id == Guid.Empty) throw new ArgumentException("Station identity is required.", nameof(id));
            Id = id; Rules = rules ?? throw new ArgumentNullException(nameof(rules)); Cartridges = rules.Cartridges;
        }
        private MedicalStationState(MedicalStationState old, MedicalMode mode, Guid body, Guid patient,
            Guid cycle, long episode, long patientRevision, long started, long due, int cartridges)
        {
            Id = old.Id; Rules = old.Rules; Revision = checked(old.Revision + 1); Mode = mode; BodyId = body;
            PatientId = patient; CycleId = cycle; PatientEpisode = episode; PatientRevision = patientRevision;
            StartedAtMilliseconds = started; DueAtMilliseconds = due; Cartridges = cartridges;
        }
        public Guid Id { get; }
        public MedicalRules Rules { get; }
        public long Revision { get; }
        public MedicalMode Mode { get; }
        public Guid BodyId { get; }
        public Guid PatientId { get; }
        public Guid CycleId { get; }
        public long PatientEpisode { get; }
        public long PatientRevision { get; }
        public long StartedAtMilliseconds { get; }
        public long DueAtMilliseconds { get; }
        public int Cartridges { get; }
        public bool CanStart => (Mode == MedicalMode.Loaded || Mode == MedicalMode.Interrupted) && Cartridges > 0;
        public bool CanEject => Mode != MedicalMode.Empty && Mode != MedicalMode.Treating;

        public MedicalStationState Load(Guid body, Guid patient)
        {
            if (Mode != MedicalMode.Empty) throw new InvalidOperationException("The chamber is occupied.");
            if (body == Guid.Empty || patient == Guid.Empty) throw new ArgumentException("A patient and registered body are required.");
            return new MedicalStationState(this, MedicalMode.Loaded, body, patient, Guid.Empty, 0, 0, 0, 0, Cartridges);
        }
        public MedicalStationState Begin(Guid cycle, long patientEpisode, long patientRevision, long now)
        {
            if (!CanStart) throw new InvalidOperationException("The chamber cannot begin a cycle.");
            if (cycle == Guid.Empty || patientEpisode < 1 || patientRevision < 0 || now < StartedAtMilliseconds ||
                now > long.MaxValue - Rules.DurationMilliseconds ||
                now + Rules.DurationMilliseconds > long.MaxValue - Rules.RecoveryDelayMilliseconds)
                throw new ArgumentOutOfRangeException(nameof(now));
            return new MedicalStationState(this, MedicalMode.Treating, BodyId, PatientId, cycle,
                patientEpisode, patientRevision, now, now + Rules.DurationMilliseconds, Cartridges - 1);
        }
        public MedicalStationState Complete(long now)
        {
            if (Mode != MedicalMode.Treating || now != DueAtMilliseconds) throw new InvalidOperationException("Complete at the exact due time.");
            return new MedicalStationState(this, MedicalMode.Ready, BodyId, PatientId, CycleId,
                PatientEpisode, PatientRevision, StartedAtMilliseconds, DueAtMilliseconds, Cartridges);
        }
        public MedicalStationState Interrupt()
        {
            if (Mode != MedicalMode.Treating) throw new InvalidOperationException("No active treatment exists.");
            return new MedicalStationState(this, MedicalMode.Interrupted, BodyId, PatientId, CycleId,
                PatientEpisode, PatientRevision, StartedAtMilliseconds, DueAtMilliseconds, Cartridges);
        }
        public MedicalStationState Eject()
        {
            if (!CanEject) throw new InvalidOperationException("Stop treatment before ejection.");
            return new MedicalStationState(this, MedicalMode.Empty, Guid.Empty, Guid.Empty, Guid.Empty, 0, 0, 0, 0, Cartridges);
        }
    }
}
