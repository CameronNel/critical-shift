using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public enum MaterialKind { Ore, CrushedOre, Fuel }
    [Flags] public enum MaterialFlags { None = 0, BypassedInspection = 1 }
    public enum ProductionAction { Insert, Eject, Start, SetPower, Repair, Resume, CancelCycle }
    public enum ProductionMode { Idle, Processing, PowerPaused, Jammed, OutputReady }
    public enum ProductionStatus
    {
        Applied, NoChange, UnknownMachine, UnknownBatch, NoInput, Occupied, RevisionConflict,
        WrongInput, OverCapacity, WetInput, OutputTooSmall, NoPower, InvalidState, PowerMustBeOff,
        HistoryCapacityReached, CustodyRejected
    }
    public enum ProductionEvent { Jammed, Completed, Cancelled }

    /// <summary>Authored game recipe. Values are offline fixtures, not real industrial process parameters.</summary>
    public sealed class MachineRecipe
    {
        public MachineRecipe(Guid id, MaterialKind input, MaterialKind output, long durationMilliseconds,
            long bypassDurationMilliseconds, long wetJamAfterMilliseconds, int maximumUnits,
            int yieldPermille = 1000, int moistureTolerance = 500, int outputMoisture = 0)
        {
            if (id == Guid.Empty) throw new ArgumentException("Recipe identity required.");
            if (!Enum.IsDefined(typeof(MaterialKind), input) || !Enum.IsDefined(typeof(MaterialKind), output) || input == output ||
                durationMilliseconds < 2 || bypassDurationMilliseconds < 2 || bypassDurationMilliseconds > durationMilliseconds ||
                wetJamAfterMilliseconds < 1 || wetJamAfterMilliseconds >= bypassDurationMilliseconds ||
                maximumUnits < 1 || maximumUnits > 1000000 || yieldPermille < 1 || yieldPermille > 1000 ||
                moistureTolerance < 0 || moistureTolerance > 1000 || outputMoisture < 0 || outputMoisture > 1000)
                throw new ArgumentOutOfRangeException(nameof(durationMilliseconds));
            Id = id; Input = input; Output = output; DurationMilliseconds = durationMilliseconds;
            BypassDurationMilliseconds = bypassDurationMilliseconds; WetJamAfterMilliseconds = wetJamAfterMilliseconds;
            MaximumUnits = maximumUnits; YieldPermille = yieldPermille; MoistureTolerance = moistureTolerance; OutputMoisture = outputMoisture;
        }
        public Guid Id { get; }
        public MaterialKind Input { get; }
        public MaterialKind Output { get; }
        public long DurationMilliseconds { get; }
        public long BypassDurationMilliseconds { get; }
        public long WetJamAfterMilliseconds { get; }
        public int MaximumUnits { get; }
        public int YieldPermille { get; }
        public int MoistureTolerance { get; }
        public int OutputMoisture { get; }
    }

    /// <summary>Typed payload carried by the EXISTING per-connection command stream.</summary>
    public sealed class ProductionRequest
    {
        public ProductionRequest(ProductionAction action, long machineRevision, Guid containerId = default,
            long objectRevision = 0, long batchRevision = 0, long leaseGeneration = 0, bool bypass = false, bool powered = false)
        {
            Action = action; MachineRevision = machineRevision; ContainerId = containerId;
            ObjectRevision = objectRevision; BatchRevision = batchRevision; LeaseGeneration = leaseGeneration;
            Bypass = bypass; Powered = powered;
        }
        public ProductionAction Action { get; }
        public long MachineRevision { get; }
        public Guid ContainerId { get; }
        public long ObjectRevision { get; }
        public long BatchRevision { get; }
        public long LeaseGeneration { get; }
        public bool Bypass { get; }
        public bool Powered { get; }
        internal bool IsWellFormed => Enum.IsDefined(typeof(ProductionAction), Action) && MachineRevision >= 0 &&
            ObjectRevision >= 0 && BatchRevision >= 0 && LeaseGeneration >= 0 &&
            (Action == ProductionAction.Insert ? ContainerId != Guid.Empty && LeaseGeneration > 0 && !Bypass && !Powered :
             ContainerId == Guid.Empty && LeaseGeneration == 0 &&
             (Action == ProductionAction.Start || (!Bypass && BatchRevision == 0)) &&
             (Action == ProductionAction.SetPower || !Powered) &&
             (Action == ProductionAction.Eject || ObjectRevision == 0));
        internal bool Same(ProductionRequest p) => Action == p.Action && MachineRevision == p.MachineRevision &&
            ContainerId == p.ContainerId && ObjectRevision == p.ObjectRevision && BatchRevision == p.BatchRevision &&
            LeaseGeneration == p.LeaseGeneration && Bypass == p.Bypass && Powered == p.Powered;
    }

    public sealed class MaterialView
    {
        internal MaterialView(Guid epoch, Guid container, Guid batch, Guid parent, Guid origin, Guid cause,
            MaterialKind kind, int units, int moisture, int contamination, long revision, MaterialFlags flags)
        {
            Epoch = epoch; ContainerId = container; BatchId = batch; ParentBatchId = parent; OriginId = origin; CauseId = cause;
            Kind = kind; Units = units; Moisture = moisture; Contamination = contamination; Revision = revision; Flags = flags;
        }
        public Guid Epoch { get; }
        public Guid ContainerId { get; }
        public Guid BatchId { get; }
        public Guid ParentBatchId { get; }
        public Guid OriginId { get; }
        public Guid CauseId { get; }
        public MaterialKind Kind { get; }
        public int Units { get; }
        public int Moisture { get; }
        public int Contamination { get; }
        public long Revision { get; }
        public MaterialFlags Flags { get; }
    }
    public sealed class MachineView
    {
        internal MachineView(Guid epoch, Guid id, Guid recipe, long revision, ProductionMode mode, bool power,
            Guid cycle, Guid? container, long duration, long work)
        { Epoch = epoch; Id = id; RecipeId = recipe; Revision = revision; Mode = mode; Powered = power;
          CycleId = cycle; ContainerId = container; DurationMilliseconds = duration; WorkMilliseconds = work; }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public Guid RecipeId { get; }
        public long Revision { get; }
        public ProductionMode Mode { get; }
        public bool Powered { get; }
        public Guid CycleId { get; }
        public Guid? ContainerId { get; }
        public long DurationMilliseconds { get; }
        public long WorkMilliseconds { get; }
    }
    public sealed class ProductionReply
    {
        internal ProductionReply(ProductionStatus status, MachineView? machine, MaterialView? batch = null)
        { Status = status; Machine = machine; Batch = batch; }
        public ProductionStatus Status { get; }
        public MachineView? Machine { get; }
        public MaterialView? Batch { get; }
    }
    public sealed class ConversionView
    {
        internal ConversionView(Guid cycle, Guid machine, Guid recipe, bool cancelled, MaterialView input, MaterialView? output, int waste)
        { CycleId = cycle; MachineId = machine; RecipeId = recipe; Cancelled = cancelled; Input = input; Output = output; WasteUnits = waste; }
        public Guid CycleId { get; }
        public Guid MachineId { get; }
        public Guid RecipeId { get; }
        public bool Cancelled { get; }
        public MaterialView Input { get; }
        public MaterialView? Output { get; }
        public int WasteUnits { get; }
    }
    public sealed class ProductionChange
    {
        internal ProductionChange(ProductionEvent kind, MachineView machine, MaterialView input, MaterialView? output, int waste)
        { Kind = kind; Machine = machine; Input = input; Output = output; WasteUnits = waste; }
        public ProductionEvent Kind { get; }
        public MachineView Machine { get; }
        public MaterialView Input { get; }
        public MaterialView? Output { get; }
        public int WasteUnits { get; }
    }
    public sealed class ProductionSummary
    {
        internal ProductionSummary(long issued, long active, long waste, int completed, int cancelled, int pending)
        { IssuedUnits = issued; ActiveUnits = active; WasteUnits = waste; CompletedCycles = completed; CancelledCycles = cancelled; PendingCycles = pending; }
        public long IssuedUnits { get; }
        public long ActiveUnits { get; }
        public long WasteUnits { get; }
        public int CompletedCycles { get; }
        public int CancelledCycles { get; }
        public int PendingCycles { get; }
    }
}
