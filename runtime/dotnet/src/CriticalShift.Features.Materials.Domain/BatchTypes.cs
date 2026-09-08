using System;

namespace CriticalShift.Features.Materials.Domain
{
    // Quantities and properties are fictional game units, not nuclear process data.
    public enum BatchKind { Ore, CrushedOre, Fuel }
    [Flags] public enum BatchFlags { None = 0, BypassedInspection = 1 }
    public enum ConversionStatus { Completed, Cancelled }

    public sealed class BatchSnapshot
    {
        public BatchSnapshot(Guid containerId, Guid batchId, Guid originId, Guid causeId, BatchKind kind,
            int units, int moisture, int contamination, Guid parentId = default, long revision = 0,
            BatchFlags flags = BatchFlags.None)
        {
            if (containerId == Guid.Empty || batchId == Guid.Empty || originId == Guid.Empty || causeId == Guid.Empty)
                throw new ArgumentException("Batch, container, origin and cause identities are required.");
            if (!Enum.IsDefined(typeof(BatchKind), kind) || units < 1 || units > 1000000 ||
                moisture < 0 || moisture > 1000 || contamination < 0 || contamination > 1000 || revision < 0 ||
                (flags & ~BatchFlags.BypassedInspection) != 0) throw new ArgumentOutOfRangeException(nameof(units));
            ContainerId = containerId; BatchId = batchId; OriginId = originId; CauseId = causeId;
            Kind = kind; Units = units; Moisture = moisture; Contamination = contamination;
            ParentId = parentId; Revision = revision; Flags = flags;
        }
        public Guid ContainerId { get; }
        public Guid BatchId { get; }
        public Guid ParentId { get; }
        public Guid OriginId { get; }
        public Guid CauseId { get; }
        public BatchKind Kind { get; }
        public int Units { get; }
        public int Moisture { get; }
        public int Contamination { get; }
        public long Revision { get; }
        public BatchFlags Flags { get; }
    }

    public sealed class ConversionPlan
    {
        internal ConversionPlan(Guid cycle, Guid machine, Guid recipe, BatchSnapshot input, BatchSnapshot output)
        { CycleId = cycle; MachineId = machine; RecipeId = recipe; Input = input; Output = output; }
        public Guid CycleId { get; }
        public Guid MachineId { get; }
        public Guid RecipeId { get; }
        public BatchSnapshot Input { get; }
        public BatchSnapshot Output { get; }
        public int WasteUnits => Input.Units - Output.Units;
    }

    public sealed class ConversionReceipt
    {
        internal ConversionReceipt(ConversionPlan plan, ConversionStatus status)
        { Plan = plan; Status = status; }
        public ConversionPlan Plan { get; }
        public ConversionStatus Status { get; }
    }
}
