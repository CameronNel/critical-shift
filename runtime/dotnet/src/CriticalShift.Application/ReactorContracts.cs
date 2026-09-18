using System;
using CriticalShift.Features.Reactor.Domain;

namespace CriticalShift.Application
{
    public enum ReactorMode { Empty, Loaded, Running, Shutdown, Tripped, Exhausted }
    public enum ReactorAction { Insert, Eject, Start, SetCooling, Shutdown, ResetTrip, EmergencyCooling, AuxiliaryPower }
    public enum ReactorStatus { Applied, NoChange, UnknownReactor, RevisionConflict, InvalidState, NoCooling,
        Unsafe, InsufficientReserve, UnknownBatch, WrongFuel, OverCapacity, HistoryCapacityReached, CustodyRejected }
    public enum ReactorEvent { Inserted, Ejected, Started, CoolingChanged, Shutdown, Reset, EmergencyCooling,
        AuxiliaryPower, Generated, Warning, Tripped, FuelExhausted }
    public enum ReactorRisk { None, CoolingLost, SuspectFuel }

    public sealed class ReactorDefinition
    {
        public ReactorDefinition(Guid id, long reserveCapacity = 100, long initialReserve = 10,
            long startupCost = 3, long emergencyCost = 4, long auxiliaryCost = 6,
            int maximumFuelUnits = 10000, int contaminationTolerance = 500,
            long millisecondsPerFuelUnit = 100, long powerQuantumMilliseconds = 100,
            int reservePerQuantum = 1, int gridPerQuantum = 4,
            long warningMilliseconds = 400, long tripMilliseconds = 800,
            long resetMilliseconds = 100, long emergencyReliefMilliseconds = 400)
        {
            if (id == Guid.Empty) throw new ArgumentException("Definition identity required.");
            if (reserveCapacity < 1 || reserveCapacity > 1000000000 || initialReserve < 0 || initialReserve > reserveCapacity ||
                startupCost < 1 || startupCost > reserveCapacity || emergencyCost < 1 || emergencyCost > reserveCapacity ||
                auxiliaryCost < 1 || auxiliaryCost > reserveCapacity || contaminationTolerance < 0 || contaminationTolerance > 1000)
                throw new ArgumentOutOfRangeException(nameof(reserveCapacity));
            Rules = new ReactorRules(maximumFuelUnits, millisecondsPerFuelUnit, powerQuantumMilliseconds,
                reservePerQuantum, gridPerQuantum, warningMilliseconds, tripMilliseconds, resetMilliseconds, emergencyReliefMilliseconds);
            Id = id; ReserveCapacity = reserveCapacity; InitialReserve = initialReserve; StartupCost = startupCost;
            EmergencyCost = emergencyCost; AuxiliaryCost = auxiliaryCost; ContaminationTolerance = contaminationTolerance;
        }
        internal ReactorRules Rules { get; }
        public Guid Id { get; }
        public long ReserveCapacity { get; }
        public long InitialReserve { get; }
        public long StartupCost { get; }
        public long EmergencyCost { get; }
        public long AuxiliaryCost { get; }
        public int ContaminationTolerance { get; }
    }

    /// <summary>Shares the existing connection sequence and receipt window. Costs are never client supplied.</summary>
    public sealed class ReactorRequest
    {
        public ReactorRequest(ReactorAction action, long revision, Guid containerId = default,
            long objectRevision = 0, long batchRevision = 0, long leaseGeneration = 0, bool cooling = false)
        { Action = action; Revision = revision; ContainerId = containerId; ObjectRevision = objectRevision;
          BatchRevision = batchRevision; LeaseGeneration = leaseGeneration; Cooling = cooling; }
        public ReactorAction Action { get; }
        public long Revision { get; }
        public Guid ContainerId { get; }
        public long ObjectRevision { get; }
        public long BatchRevision { get; }
        public long LeaseGeneration { get; }
        public bool Cooling { get; }
        internal bool IsWellFormed => Enum.IsDefined(typeof(ReactorAction), Action) && Revision >= 0 &&
            ObjectRevision >= 0 && BatchRevision >= 0 && LeaseGeneration >= 0 &&
            (Action == ReactorAction.Insert ? ContainerId != Guid.Empty && LeaseGeneration > 0 && !Cooling :
             ContainerId == Guid.Empty && LeaseGeneration == 0 && BatchRevision == 0 &&
             (Action == ReactorAction.Eject || ObjectRevision == 0) && (Action == ReactorAction.SetCooling || !Cooling));
        internal bool Same(ReactorRequest r) => Action == r.Action && Revision == r.Revision && ContainerId == r.ContainerId &&
            ObjectRevision == r.ObjectRevision && BatchRevision == r.BatchRevision && LeaseGeneration == r.LeaseGeneration && Cooling == r.Cooling;
    }

    public sealed class PowerView
    {
        internal PowerView(long initial, long capacity, long available, long generated, long spent, long delivered, long spilled)
        { Initial = initial; Capacity = capacity; Available = available; Generated = generated; Spent = spent; Delivered = delivered; Spilled = spilled; }
        public long Initial { get; }
        public long Capacity { get; }
        public long Available { get; }
        public long Generated { get; }
        public long Spent { get; }
        public long Delivered { get; }
        public long Spilled { get; }
    }

    public sealed class ReactorView
    {
        internal ReactorView(Guid epoch, Guid id, Guid definition, long revision, ReactorMode mode, bool cooling,
            bool suspect, long work, long remaining, long instability, Guid cycle, MaterialView? fuel, PowerView power)
        { Epoch = epoch; Id = id; DefinitionId = definition; Revision = revision; Mode = mode; Cooling = cooling;
          SuspectFuel = suspect; WorkMilliseconds = work; RemainingFuelMilliseconds = remaining; InstabilityMilliseconds = instability;
          CycleId = cycle; Fuel = fuel; Power = power; }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public Guid DefinitionId { get; }
        public long Revision { get; }
        public ReactorMode Mode { get; }
        public bool Cooling { get; }
        public bool SuspectFuel { get; }
        public long WorkMilliseconds { get; }
        public long RemainingFuelMilliseconds { get; }
        public long InstabilityMilliseconds { get; }
        public Guid CycleId { get; }
        public MaterialView? Fuel { get; }
        public PowerView Power { get; }
    }

    public sealed class ReactorChange
    {
        internal ReactorChange(ReactorEvent kind, ReactorView state, long at, Guid cycle, Guid batch, Guid cause,
            ReactorRisk risk, long generated = 0, long spent = 0)
        { EventId = Guid.NewGuid(); Kind = kind; State = state; ShiftMilliseconds = at; CycleId = cycle;
          InputBatchId = batch; CauseId = cause; Risk = risk; GeneratedUnits = generated; SpentUnits = spent; }
        public Guid EventId { get; }
        public ReactorEvent Kind { get; }
        public ReactorView State { get; }
        public long ShiftMilliseconds { get; }
        public Guid CycleId { get; }
        public Guid InputBatchId { get; }
        public Guid CauseId { get; }
        public ReactorRisk Risk { get; }
        public long GeneratedUnits { get; }
        public long SpentUnits { get; }
    }

    public sealed class ReactorReply
    {
        internal ReactorReply(ReactorStatus status, ReactorView? state, ReactorChange? change)
        { Status = status; State = state; Change = change; }
        public ReactorStatus Status { get; }
        public ReactorView? State { get; }
        public ReactorChange? Change { get; }
    }
}
