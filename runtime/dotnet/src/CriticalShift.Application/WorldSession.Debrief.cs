#nullable enable
using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        private IReadOnlyList<WorkerView>? closingRoster;
        public ShiftDebriefView? Debrief { get; private set; }

        private void CaptureDebrief()
        {
            if (Debrief != null) return;
            Debrief = new ShiftDebriefView(View, Contracts.View, Production.Summary, Reactor.PowerSummary,
                closingRoster ?? Array.Empty<WorkerView>(), _diagnostics.Incidents,
                _diagnostics.IncidentTimeline, _diagnostics.DroppedIncidents);
        }
    }
}
