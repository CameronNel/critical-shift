#nullable enable
using System;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        internal void RegisterMedical(Guid id, MedicalDefinition definition)
        {
            RequireIdle();
            if (_timeline.Phase != TimelinePhase.Setup) throw new InvalidOperationException("Medical station setup has closed.");
            long next = NextRevision(); Medical.Configure(id, definition); _revision = next;
        }
    }
}
