using System;
using System.Collections.Generic;

namespace CriticalShift.Features.Materials.Domain
{
    /// <summary>Owns material quantities and lineage, never physical custody. One simulation thread.</summary>
    public sealed class MaterialLedger
    {
        private readonly int _containers, _cycles;
        private readonly Dictionary<Guid, BatchSnapshot> _current = new Dictionary<Guid, BatchSnapshot>();
        private readonly Dictionary<Guid, ConversionPlan> _pending = new Dictionary<Guid, ConversionPlan>();
        private readonly Dictionary<Guid, ConversionReceipt> _receipts = new Dictionary<Guid, ConversionReceipt>();
        private readonly HashSet<Guid> _batchIds = new HashSet<Guid>();
        private readonly HashSet<Guid> _reservedContainers = new HashSet<Guid>();
        private long _issued, _waste;
        public MaterialLedger(int containerCapacity, int cycleCapacity)
        {
            if (containerCapacity < 1 || cycleCapacity < 1 || cycleCapacity > 4096)
                throw new ArgumentOutOfRangeException(nameof(containerCapacity));
            _containers = containerCapacity; _cycles = cycleCapacity;
        }
        public int Count => _current.Count;
        public int PendingCount => _pending.Count;
        public int ReceiptCount => _receipts.Count;
        public long IssuedUnits => _issued;
        public long WasteUnits => _waste;
        public long ActiveUnits { get { long units = 0; foreach (var b in _current.Values) units += b.Units; return units; } }
        public BatchSnapshot? Get(Guid container) => _current.TryGetValue(container, out var b) ? b : null;
        public bool HasCycleCapacity => _pending.Count + _receipts.Count < _cycles;
        public ConversionReceipt? GetReceipt(Guid cycle) => _receipts.TryGetValue(cycle, out var r) ? r : null;
        public void ValidateRegistration(BatchSnapshot batch)
        {
            if (batch == null) throw new ArgumentNullException(nameof(batch));
            if (_current.ContainsKey(batch.ContainerId) || _batchIds.Contains(batch.BatchId))
                throw new InvalidOperationException("Material identity already exists.");
            if (_current.Count >= _containers) throw new InvalidOperationException("Material capacity reached.");
        }
        public void Register(BatchSnapshot batch)
        {
            ValidateRegistration(batch);
            long issued = checked(_issued + batch.Units);
            _current.Add(batch.ContainerId, batch); _batchIds.Add(batch.BatchId); _issued = issued;
        }

        /// <summary>Prepare without mutation. Reserve capacity before machine startup, not at completion.</summary>
        public ConversionPlan Prepare(Guid container, long expectedRevision, Guid cycle, Guid machine, Guid recipe,
            Guid outputId, BatchKind outputKind, int yieldPermille, int outputMoisture, bool bypass)
        {
            var input = Get(container) ?? throw new InvalidOperationException("Unknown material.");
            if (input.Revision != expectedRevision || _reservedContainers.Contains(container))
                throw new InvalidOperationException("Material revision conflict or reserved input.");
            if (!HasCycleCapacity) throw new InvalidOperationException("Conversion history budget exhausted.");
            if (cycle == Guid.Empty || machine == Guid.Empty || recipe == Guid.Empty || outputId == Guid.Empty ||
                _pending.ContainsKey(cycle) || _receipts.ContainsKey(cycle) || _batchIds.Contains(outputId))
                throw new ArgumentException("A new conversion identity is required.");
            if (yieldPermille < 1 || yieldPermille > 1000) throw new ArgumentOutOfRangeException(nameof(yieldPermille));
            int quantity = checked((int)((long)input.Units * yieldPermille / 1000));
            var output = new BatchSnapshot(container, outputId, input.OriginId, input.CauseId,
                outputKind, quantity, outputMoisture, input.Contamination, input.BatchId,
                checked(input.Revision + 1), input.Flags | (bypass ? BatchFlags.BypassedInspection : BatchFlags.None));
            return new ConversionPlan(cycle, machine, recipe, input, output);
        }
        public void Reserve(ConversionPlan plan)
        {
            if (plan == null) throw new ArgumentNullException(nameof(plan));
            if (!HasCycleCapacity || !ReferenceEquals(Get(plan.Input.ContainerId), plan.Input) ||
                _reservedContainers.Contains(plan.Input.ContainerId) || _pending.ContainsKey(plan.CycleId) ||
                _receipts.ContainsKey(plan.CycleId) || _batchIds.Contains(plan.Output.BatchId))
                throw new InvalidOperationException("Stale conversion plan.");
            _pending.Add(plan.CycleId, plan); _reservedContainers.Add(plan.Input.ContainerId);
            _batchIds.Add(plan.Output.BatchId);
        }
        public ConversionReceipt Finish(Guid cycle, bool cancel)
        {
            if (_receipts.TryGetValue(cycle, out var previous)) return previous;
            if (!_pending.TryGetValue(cycle, out var plan)) throw new InvalidOperationException("No prepared conversion.");
            if (!ReferenceEquals(Get(plan.Input.ContainerId), plan.Input)) throw new InvalidOperationException("Input changed in flight.");
            long waste = cancel ? _waste : checked(_waste + plan.WasteUnits);
            var receipt = new ConversionReceipt(plan, cancel ? ConversionStatus.Cancelled : ConversionStatus.Completed);
            // No user code, physics, event listeners or awaits inside this commit.
            _receipts.Add(cycle, receipt);
            if (!cancel) _current[plan.Input.ContainerId] = plan.Output;
            _waste = waste; _pending.Remove(cycle); _reservedContainers.Remove(plan.Input.ContainerId);
            return receipt;
        }
        public void Clear()
        {
            _current.Clear(); _pending.Clear(); _receipts.Clear(); _batchIds.Clear();
            _reservedContainers.Clear(); _issued = 0; _waste = 0;
        }
    }
}
