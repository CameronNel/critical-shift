#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Workers.Domain
{
    public enum ContaminationMode { Exposure, Decontamination }

    /// <summary>Authored discrete game contacts, not dose rates or material contamination units.</summary>
    public sealed class ContaminationRules
    {
        public ContaminationRules(ContaminationMode mode, int units, long cooldownMilliseconds = 500)
        {
            if (mode != ContaminationMode.Exposure && mode != ContaminationMode.Decontamination)
                throw new ArgumentOutOfRangeException(nameof(mode));
            if (units < 1 || units > 100) throw new ArgumentOutOfRangeException(nameof(units));
            if (cooldownMilliseconds < 1 || cooldownMilliseconds > 60000)
                throw new ArgumentOutOfRangeException(nameof(cooldownMilliseconds));
            Mode = mode; Units = units; CooldownMilliseconds = cooldownMilliseconds;
        }
        public ContaminationMode Mode { get; }
        public int Units { get; }
        public long CooldownMilliseconds { get; }
        internal bool Same(ContaminationRules other) => Mode == other.Mode && Units == other.Units && CooldownMilliseconds == other.CooldownMilliseconds;
        internal int Effective(SuitCondition suit) => Mode == ContaminationMode.Decontamination ? Units :
            suit == SuitCondition.Intact ? (Units + 3) / 4 : suit == SuitCondition.Compromised ? (Units + 1) / 2 : Units;
    }

    public sealed class ContaminationContact
    {
        internal ContaminationContact(Guid source, Guid cause, long sequence, long sample, ContaminationRules rules,
            int before, int after, int effective, long nextEligibleAt, WorkerResult outcome)
        { SourceId = source; CauseId = cause; Sequence = sequence; SampleShiftMilliseconds = sample; Rules = rules;
          Before = before; After = after; EffectiveUnits = effective; NextEligibleAtMilliseconds = nextEligibleAt; Outcome = outcome; }
        public Guid SourceId { get; }
        public Guid CauseId { get; }
        public long Sequence { get; }
        public long SampleShiftMilliseconds { get; }
        public ContaminationRules Rules { get; }
        public int Before { get; }
        public int After { get; }
        public int EffectiveUnits { get; }
        public long NextEligibleAtMilliseconds { get; }
        public WorkerResult Outcome { get; }
    }
    public sealed class ContaminationResult
    {
        internal ContaminationResult(WorkerResult status, ContaminationContact? contact = null) { Status = status; Contact = contact; }
        public WorkerResult Status { get; }
        public ContaminationContact? Contact { get; }
    }

    public sealed partial class WorkerState
    {
        private readonly Dictionary<Guid, ContaminationContact> _contacts = new Dictionary<Guid, ContaminationContact>();
        public const int ContaminationSourceCapacity = 32;

        public ContaminationResult ObserveContamination(Guid source, long sequence, Guid cause,
            ContaminationRules rules, long sampledShiftMilliseconds, long authoritativeShiftMilliseconds)
        {
            if (source == Guid.Empty || cause == Guid.Empty || rules == null || sequence < 1 || sequence == long.MaxValue ||
                sampledShiftMilliseconds < 0 || authoritativeShiftMilliseconds < 0)
                return new ContaminationResult(WorkerResult.InvalidInput);
            _contacts.TryGetValue(source, out var previous);
            long last = previous?.Sequence ?? 0;
            // Historical identity is checked before current time, suit or contamination can reinterpret it.
            if (sequence == last)
                return new ContaminationResult(previous!.CauseId == cause && previous.SampleShiftMilliseconds == sampledShiftMilliseconds &&
                    previous.Rules.Same(rules) ? WorkerResult.Duplicate : WorkerResult.PayloadMismatch, previous);
            if (sequence < last) return new ContaminationResult(WorkerResult.TooOld);
            if (sequence != last + 1) return new ContaminationResult(WorkerResult.SequenceGap);
            if (previous != null && !previous.Rules.Same(rules)) return new ContaminationResult(WorkerResult.InvalidInput);
            if (previous == null && _contacts.Count >= ContaminationSourceCapacity) return new ContaminationResult(WorkerResult.SourceCapacityReached);
            if (sampledShiftMilliseconds != authoritativeShiftMilliseconds || sampledShiftMilliseconds < _lastTime)
                return new ContaminationResult(WorkerResult.StaleObservation);
            bool cooling = previous != null && sampledShiftMilliseconds < previous.NextEligibleAtMilliseconds;
            if (!cooling && rules.CooldownMilliseconds > long.MaxValue - sampledShiftMilliseconds)
                return new ContaminationResult(WorkerResult.InvalidInput);
            int effective = cooling ? 0 : rules.Effective(_suit);
            int after = rules.Mode == ContaminationMode.Exposure ? Math.Min(100, _contamination + effective) : Math.Max(0, _contamination - effective);
            var status = cooling ? WorkerResult.CoolingDown : after == _contamination ? WorkerResult.NoChange : WorkerResult.Applied;
            long revision = status == WorkerResult.Applied ? checked(_revision + 1) : _revision;
            long nextEligible = cooling ? previous!.NextEligibleAtMilliseconds : sampledShiftMilliseconds + rules.CooldownMilliseconds;
            var contact = new ContaminationContact(source, cause, sequence, sampledShiftMilliseconds, rules,
                _contamination, after, effective, nextEligible, status);
            _contacts[source] = contact; _contamination = after; _revision = revision; _lastTime = sampledShiftMilliseconds;
            return new ContaminationResult(status, contact);
        }
    }
}
