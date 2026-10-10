using System;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        public PlayerOperations Players { get; }

        internal void RegisterPlayer(Action registration)
        {
            RequireIdle();
            if (_timeline.Phase != Features.Session.Domain.TimelinePhase.Setup)
                throw new InvalidOperationException("Player setup has closed.");
            long next = NextRevision();
            registration(); _revision = next;
        }
    }
}
