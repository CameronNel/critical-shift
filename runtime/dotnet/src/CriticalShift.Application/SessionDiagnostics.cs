using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public enum SessionTraceKind
    {
        Started, Advanced, Interaction, Impact, Aid, Environment,
        RecoveryRequested, RecoveryResolved, RecoveryCancelled, RecoveryExpired,
        Disconnected, Ended, Stopped, Faulted
    }

    /// <summary>Bounded typed diagnostic data. No arbitrary message, exception text, credential or callback.</summary>
    public sealed class SessionTraceRecord
    {
        internal SessionTraceRecord(long sequence, WorldSessionView world, Guid requestEpoch, SessionTraceKind kind,
            Guid actorId, Guid entityId, long inputSequence, bool changed, WorkerReply? worker, InteractionReply? interaction, long? previousWorkerRevision)
        {
            Sequence = sequence; Epoch = world.Epoch; RequestEpoch = requestEpoch; Kind = kind;
            ActorId = actorId; EntityId = entityId; InputSequence = inputSequence; Changed = changed;
            WorldRevision = world.Revision; HostMilliseconds = world.HostMilliseconds;
            ShiftMilliseconds = world.ElapsedMilliseconds; Phase = world.Phase; Outcome = world.Outcome;
            WorkerResult = worker?.Status; InteractionResult = interaction?.Status;
            RelatedImpactSequence = worker?.Worker?.LastImpactSequence;
            WorkerRevision = worker?.Worker?.Revision; PreviousWorkerRevision = previousWorkerRevision;
            RecoveryEpisode = worker?.Worker?.RecoveryEpisode; RecoveryAttempt = worker?.Worker?.RecoveryAttempt;
        }
        public long Sequence { get; }
        public Guid Epoch { get; }
        public Guid RequestEpoch { get; }
        public SessionTraceKind Kind { get; }
        public Guid ActorId { get; }
        public Guid EntityId { get; }
        public long InputSequence { get; }
        public bool Changed { get; }
        public long WorldRevision { get; }
        public long HostMilliseconds { get; }
        public long ShiftMilliseconds { get; }
        public WorldPhase Phase { get; }
        public WorldOutcome Outcome { get; }
        public WorkerStatus? WorkerResult { get; }
        public InteractionStatus? InteractionResult { get; }
        public long? RelatedImpactSequence { get; }
        public long? WorkerRevision { get; }
        public long? PreviousWorkerRevision { get; }
        public long? RecoveryEpisode { get; }
        public long? RecoveryAttempt { get; }
    }

    public sealed class SessionTraceView
    {
        internal SessionTraceView(IReadOnlyList<SessionTraceRecord> records, long dropped, bool exhausted)
        { Records = records; DroppedRecords = dropped; SequenceExhausted = exhausted; }
        public IReadOnlyList<SessionTraceRecord> Records { get; }
        public long DroppedRecords { get; }
        public bool SequenceExhausted { get; }
    }

    internal sealed class SessionDiagnostics
    {
        private readonly SessionTraceRecord?[] _records;
        private int _first, _count;
        private long _sequence, _dropped;
        internal SessionDiagnostics(int capacity)
        {
            if (capacity < 1 || capacity > 4096) throw new ArgumentOutOfRangeException(nameof(capacity));
            _records = new SessionTraceRecord[capacity];
        }
        internal int Capacity => _records.Length;
        internal SessionTraceView View
        {
            get
            {
                var copy = new List<SessionTraceRecord>(_count);
                for (int i = 0; i < _count; i++) copy.Add(_records[(_first + i) % Capacity]!);
                return new SessionTraceView(copy.AsReadOnly(), _dropped, _sequence == long.MaxValue);
            }
        }
        internal void Append(WorldSessionView world, Guid requestEpoch, SessionTraceKind kind,
            Guid actor = default, Guid entity = default, long input = 0, bool changed = false,
            WorkerReply? worker = null, InteractionReply? interaction = null, long? previousWorkerRevision = null)
        {
            // Exhausting diagnostics must not overflow and replay or reject a gameplay transaction.
            if (_sequence == long.MaxValue) { if (_dropped < long.MaxValue) _dropped++; return; }
            var record = new SessionTraceRecord(++_sequence, world, requestEpoch, kind,
                actor, entity, input, changed, worker, interaction, previousWorkerRevision);
            if (_count == Capacity)
            {
                _records[_first] = record; _first = (_first + 1) % Capacity;
                if (_dropped < long.MaxValue) _dropped++;
            }
            else { _records[(_first + _count) % Capacity] = record; _count++; }
        }
    }
}
