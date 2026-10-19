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

        private void AdvanceProductionTo(long elapsed, List<ProductionChange> productionChanges,
            List<ReactorChange> reactorChanges, List<GridDemandChange> demandChanges,
            List<MedicalChange> medicalChanges, List<SuitFittingChange> fittingChanges)
        {
            // The caller owns these buffers across exceptions. Each owner appends only
            // after its own complete transaction; later failures cannot erase committed facts.
            SuitFitting.SampleAccessAt(elapsed, fittingChanges);
            while (true)
            {
                // A cumulative end-only power sample cannot recover how much was
                // supplied in each skipped window. Evaluate the existing owners at
                // every boundary instead; a quantum at the endpoint closes that wave.
                long boundary = Math.Min(elapsed, Math.Min(Contracts.NextBoundary, Math.Min(Reactor.NextBackupBoundary, SuitFitting.NextBoundary)));
                Production.AdvanceTo(boundary, productionChanges);
                reactorChanges.AddRange(Reactor.AdvanceTo(boundary));
                // At the same coordinate core output precedes backup credit; an earlier
                // backup due time must settle before any later core output can take headroom.
                var backup = Reactor.CompleteBackupAt(boundary);
                if (backup != null) reactorChanges.Add(backup);
                var change = Contracts.Observe(boundary);
                if (change != null) demandChanges.Add(change);
                SuitFitting.AdvanceTo(boundary, fittingChanges);
                var care = Medical.AdvanceTo(boundary);
                if (care != null) medicalChanges.Add(care);
                if (boundary == elapsed) break;
            }
        }
    }
}
