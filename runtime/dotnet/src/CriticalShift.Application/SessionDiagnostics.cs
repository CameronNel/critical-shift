#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public enum SessionTraceKind
    {
        Started, Advanced, Interaction, Impact, Aid, Environment,
        RecoveryRequested, RecoveryResolved, RecoveryCancelled, RecoveryExpired,
        Disconnected, Ended, Stopped, Faulted, Production, Reactor, AttachmentFailed, LeaseExpired, Door, Evacuation, Contract, Medical
    }

    /// <summary>Bounded typed diagnostic data. No arbitrary message, exception text, credential or callback.</summary>
    public sealed class SessionTraceRecord
    {
        internal SessionTraceRecord(long sequence, WorldSessionView world, Guid requestEpoch, SessionTraceKind kind,
            Guid actorId, Guid entityId, long inputSequence, bool changed, WorkerReply? worker, InteractionReply? interaction, long? previousWorkerRevision, Guid hazardId, Guid causeId, WorkerImpact? severity, ProductionChange? production, ReactorChange? reactor, long? previousClaimRevision, DoorEvacuationReply? evacuation, GridDemandChange? demand, MedicalChange? medical)
        {
            DemandChange = demand;
            MedicalChange = medical ?? interaction?.Medical?.Change;
            HazardId = hazardId != Guid.Empty ? hazardId : worker?.Worker?.LastHazardId ?? Guid.Empty;
            CauseId = causeId != Guid.Empty ? causeId : MedicalChange?.InjuryCauseId ?? interaction?.Door?.CauseId ?? worker?.Worker?.LastCauseId ?? Guid.Empty;
            DoorResult = interaction?.Door?.Status; DoorAction = interaction?.Door?.Action;
            DoorRevision = interaction?.Door?.Door?.Revision; PreviousDoorRevision = interaction?.Door?.PreviousRevision;
            DoorState = interaction?.Door?.Door?.State; DoorSourceId = interaction?.Door?.Door?.SourceId;
            EvacuationResult = evacuation?.Status;
            ImpactSeverity = severity;
            ReactorChange = reactor ?? interaction?.Reactor?.Change;
            ReactorEvent = changed ? ReactorChange?.Kind : null;
            ReactorResult = interaction?.Reactor?.Status;
            var change = production ?? interaction?.Production?.Change;
            OccurredAtMilliseconds = MedicalChange?.ShiftMilliseconds ?? demand?.ShiftMilliseconds ?? ReactorChange?.ShiftMilliseconds ??
                change?.ShiftMilliseconds ?? world.ElapsedMilliseconds;
            ProductionResult = interaction?.Production?.Status;
            // Replays retain historical attribution, but cannot publish a second committed event.
            ProductionEvent = changed ? change?.Kind : null;
            CycleId = MedicalChange?.CycleId ?? change?.CycleId ?? interaction?.Production?.Machine?.CycleId ?? Guid.Empty;
            RecipeId = change?.RecipeId ?? interaction?.Production?.Machine?.RecipeId ?? Guid.Empty;
            BypassedInspection = change?.BypassedInspection;
            BatchId = change?.Input.BatchId ?? interaction?.Production?.Batch?.BatchId ?? Guid.Empty;
            OutputBatchId = change?.Output?.BatchId ?? Guid.Empty;
            MaterialCauseId = change?.Input.CauseId ?? interaction?.Production?.Batch?.CauseId ?? Guid.Empty;
            WasteUnits = change?.WasteUnits;
            Sequence = sequence; Epoch = world.Epoch; RequestEpoch = requestEpoch; Kind = kind;
            ActorId = actorId; EntityId = entityId; InputSequence = inputSequence; Changed = changed;
            WorldRevision = world.Revision; HostMilliseconds = world.HostMilliseconds;
            ShiftMilliseconds = world.ElapsedMilliseconds; Phase = world.Phase; Outcome = world.Outcome;
            WorkerResult = worker?.Status; InteractionResult = interaction?.Status;
            PreviousClaimRevision = previousClaimRevision; ClaimRevision = interaction?.State?.Revision;
            ClaimLeaseGeneration = interaction?.State?.LeaseGeneration;
            RelatedImpactSequence = worker?.Worker?.LastImpactSequence;
            WorkerRevision = worker?.Worker?.Revision; PreviousWorkerRevision = previousWorkerRevision;
            RecoveryEpisode = worker?.Worker?.RecoveryEpisode; RecoveryAttempt = worker?.Worker?.RecoveryAttempt;
        }
        public long Sequence { get; }
        public long OccurredAtMilliseconds { get; }
        public Guid Epoch { get; }
        public Guid RequestEpoch { get; }
        public SessionTraceKind Kind { get; }
        public Guid HazardId { get; }
        public Guid CauseId { get; }
        public GridDemandChange? DemandChange { get; }
        public MedicalChange? MedicalChange { get; }
        public DoorStatus? DoorResult { get; }
        public DoorAction? DoorAction { get; }
        public DoorState? DoorState { get; }
        public string? DoorSourceId { get; }
        public long? PreviousDoorRevision { get; }
        public long? DoorRevision { get; }
        public DoorEvacuationStatus? EvacuationResult { get; }
        public WorkerImpact? ImpactSeverity { get; }
        public ProductionStatus? ProductionResult { get; }
        public ReactorChange? ReactorChange { get; }
        public ReactorEvent? ReactorEvent { get; }
        public ReactorStatus? ReactorResult { get; }
        public ProductionEvent? ProductionEvent { get; }
        public Guid CycleId { get; }
        public Guid RecipeId { get; }
        public bool? BypassedInspection { get; }
        public Guid BatchId { get; }
        public Guid OutputBatchId { get; }
        public Guid MaterialCauseId { get; }
        public int? WasteUnits { get; }
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
        public long? PreviousClaimRevision { get; }
        public long? ClaimRevision { get; }
        public long? ClaimLeaseGeneration { get; }
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
        private readonly ShiftIncidentJournal _incidents;
        private int _first, _count;
        private long _sequence, _dropped;
        internal SessionDiagnostics(int capacity)
        {
            if (capacity < 1 || capacity > 4096) throw new ArgumentOutOfRangeException(nameof(capacity));
            _records = new SessionTraceRecord[capacity];
            _incidents = new ShiftIncidentJournal(capacity);
        }
        internal ShiftIncidentTotals Incidents => _incidents.Totals;
        internal IReadOnlyList<SessionTraceRecord> IncidentTimeline => _incidents.Timeline;
        internal long DroppedIncidents => _incidents.Dropped;
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
            WorkerReply? worker = null, InteractionReply? interaction = null, long? previousWorkerRevision = null, Guid hazardId = default, Guid causeId = default, WorkerImpact? severity = null, ProductionChange? production = null, ReactorChange? reactor = null, long? previousClaimRevision = null, DoorEvacuationReply? evacuation = null, GridDemandChange? demand = null, MedicalChange? medical = null)
        {
            // Exhausting diagnostics must not overflow and replay or reject a gameplay transaction.
            bool exhausted = _sequence == long.MaxValue;
            var record = new SessionTraceRecord(exhausted ? _sequence : ++_sequence, world, requestEpoch, kind,
                actor, entity, input, changed, worker, interaction, previousWorkerRevision, hazardId, causeId, severity, production, reactor, previousClaimRevision, evacuation, demand, medical);
            _incidents.Observe(record, !exhausted);
            if (exhausted) { if (_dropped < long.MaxValue) _dropped++; return; }
            if (_count == Capacity)
            {
                _records[_first] = record; _first = (_first + 1) % Capacity;
                if (_dropped < long.MaxValue) _dropped++;
            }
            else { _records[(_first + _count) % Capacity] = record; _count++; }
        }
    }
}
