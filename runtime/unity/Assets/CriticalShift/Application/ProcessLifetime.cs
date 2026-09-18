using System;

namespace CriticalShift.Application
{
    public enum ProcessPhase { Created, Ready, Stopped }

    /// <summary>Process startup/stop only. This is not a gameplay world or shift owner.</summary>
    public sealed class ProcessLifetime
    {
        public ProcessPhase Phase { get; private set; } = ProcessPhase.Created;

        public void MarkReady()
        {
            if (Phase != ProcessPhase.Created)
                throw new InvalidOperationException("Only a newly created process can become ready.");
            Phase = ProcessPhase.Ready;
        }

        public bool Stop()
        {
            if (Phase == ProcessPhase.Stopped) return false;
            Phase = ProcessPhase.Stopped;
            return true;
        }
    }
}
