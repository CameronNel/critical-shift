#nullable enable
using System;
using CriticalShift.Features.Workers.Domain;

namespace CriticalShift.Application
{
    public enum WorkerContaminationKind { Exposure, Decontamination }
    public sealed class WorkerContaminationDefinition
    {
        public WorkerContaminationDefinition(WorkerContaminationKind kind, int units, long cooldownMilliseconds = 500)
        { Rules = new ContaminationRules((ContaminationMode)(int)kind, units, cooldownMilliseconds); }
        internal ContaminationRules Rules { get; }
        public WorkerContaminationKind Kind => (WorkerContaminationKind)(int)Rules.Mode;
        public int Units => Rules.Units;
        public long CooldownMilliseconds => Rules.CooldownMilliseconds;
    }
    public sealed class WorkerContaminationContact
    {
        internal WorkerContaminationContact(ContaminationContact contact)
        { SourceId = contact.SourceId; CauseId = contact.CauseId; Sequence = contact.Sequence;
          SampleShiftMilliseconds = contact.SampleShiftMilliseconds; Kind = (WorkerContaminationKind)(int)contact.Rules.Mode;
          RawUnits = contact.Rules.Units; EffectiveUnits = contact.EffectiveUnits; Before = contact.Before; After = contact.After;
          NextEligibleAtMilliseconds = contact.NextEligibleAtMilliseconds; OriginalOutcome = WorkerWorkflow.Map(contact.Outcome); }
        public Guid SourceId { get; }
        public Guid CauseId { get; }
        public long Sequence { get; }
        public long SampleShiftMilliseconds { get; }
        public WorkerContaminationKind Kind { get; }
        public int RawUnits { get; }
        public int EffectiveUnits { get; }
        public int Before { get; }
        public int After { get; }
        public long NextEligibleAtMilliseconds { get; }
        public WorkerStatus OriginalOutcome { get; }
    }
}
