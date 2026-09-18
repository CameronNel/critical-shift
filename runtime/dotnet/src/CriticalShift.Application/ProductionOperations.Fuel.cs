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
        internal void FinishFuel(Guid cycle)
        {
            // Caller invokes once at the operating-state exhaustion transition, not on a repeated tick.
            var receipt = _materials.Finish(cycle, false);
            if (receipt.Status != ConversionStatus.Completed) throw new InvalidOperationException("Cancelled fuel cycle cannot finish.");
            _completed++;
        }
    }
}
