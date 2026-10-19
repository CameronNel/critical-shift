#nullable enable
using System;
using CriticalShift.Features.Materials.Domain;

namespace CriticalShift.Application
{
    public sealed partial class ProductionOperations
    {
        // Reactor fuel uses the SAME material ledger and bounded conversion history as production.
        // These ports are internal to the guarded Application transaction, never public mutations.
        internal bool HasFuelHistoryCapacity => _materials.HasCycleCapacity;
        internal ConversionPlan PrepareFuel(Guid container, long revision, Guid cycle, Guid reactor, Guid definition)
        {
            var input = _materials.Get(container) ?? throw new InvalidOperationException("Fuel input disappeared.");
            if (input.Kind != BatchKind.Fuel) throw new InvalidOperationException("Only fuel can enter a reactor cycle.");
            return _materials.Prepare(container, revision, cycle, reactor, definition, Guid.NewGuid(),
                BatchKind.SpentFuel, 1000, input.Moisture, false);
        }
        internal void ReserveFuel(ConversionPlan plan) => _materials.Reserve(plan);
        internal void ValidateFuelCompletion(Guid cycle, Guid reactor, Guid definition, MaterialView expected)
        {
            var plan = _materials.GetPending(cycle);
            if (expected.Epoch != _world.Epoch || plan == null || plan.MachineId != reactor || plan.RecipeId != definition ||
                plan.Input.ContainerId != expected.ContainerId || plan.Input.BatchId != expected.BatchId || plan.Input.Revision != expected.Revision ||
                plan.Input.Kind != BatchKind.Fuel || plan.Output.Kind != BatchKind.SpentFuel || plan.WasteUnits != 0 ||
                !ReferenceEquals(_materials.Get(expected.ContainerId), plan.Input))
                throw new InvalidOperationException("Fuel completion lost its exact reserved input or full-yield spent output.");
            _ = checked(_completed + 1);
        }
        internal void FinishFuel(Guid cycle)
        {
            // A retained completed receipt cannot increment accounting again.
            var previous = _materials.GetReceipt(cycle);
            if (previous?.Status == ConversionStatus.Completed) return;
            int completed = checked(_completed + 1);
            var receipt = _materials.Finish(cycle, false);
            if (receipt.Status != ConversionStatus.Completed) throw new InvalidOperationException("Cancelled fuel cycle cannot finish.");
            _completed = completed;
        }
    }
}
