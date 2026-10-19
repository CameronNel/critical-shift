#nullable enable
using System;
using System.Collections.Generic;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        internal void RegisterContract(ShiftContractDefinition definition)
        {
            RequireIdle();
            if (_timeline.Phase != TimelinePhase.Setup) throw new InvalidOperationException("Contract setup has closed.");
            long next = NextRevision(); Contracts.Configure(definition); _revision = next;
        }

        private void AdvanceProductionTo(long elapsed, out IReadOnlyList<ProductionChange> production,
            out IReadOnlyList<ReactorChange> reactor, out IReadOnlyList<GridDemandChange> demand, out IReadOnlyList<MedicalChange> medical)
        {
            var productionChanges = new List<ProductionChange>(); var reactorChanges = new List<ReactorChange>();
            var demandChanges = new List<GridDemandChange>();
            var medicalChanges = new List<MedicalChange>();
            while (true)
            {
                // A cumulative end-only power sample cannot recover how much was
                // supplied in each skipped window. Evaluate the existing owners at
                // every boundary instead; a quantum at the endpoint closes that wave.
                long boundary = Math.Min(elapsed, Contracts.NextBoundary);
                productionChanges.AddRange(Production.AdvanceTo(boundary));
                reactorChanges.AddRange(Reactor.AdvanceTo(boundary));
                var change = Contracts.Observe(boundary);
                if (change != null) demandChanges.Add(change);
                var care = Medical.AdvanceTo(boundary);
                if (care != null) medicalChanges.Add(care);
                if (boundary == elapsed) break;
            }
            production = productionChanges.AsReadOnly(); reactor = reactorChanges.AsReadOnly(); demand = demandChanges.AsReadOnly();
            medical = medicalChanges.AsReadOnly();
        }
    }
}
