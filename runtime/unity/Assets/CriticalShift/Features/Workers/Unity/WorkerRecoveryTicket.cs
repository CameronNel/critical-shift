using System;

namespace CriticalShift.Features.Workers.Unity
{
    // Detached admission snapshot. A timer cannot authorize aid for a later injury or another patient.
    public readonly struct WorkerRecoveryTicket
    {
        public Guid Epoch { get; }
        public Guid Patient { get; }
        public long Episode { get; }
        public WorkerRecoveryTicket(Guid epoch, Guid patient, long episode)
        {
            if (epoch == Guid.Empty || patient == Guid.Empty || episode <= 0) throw new ArgumentException("A station ticket requires an epoch, patient and injury episode.");
            Epoch = epoch; Patient = patient; Episode = episode;
        }
        public bool Matches(Guid epoch, Guid patient, long episode) => Epoch == epoch && Patient == patient && Episode == episode;
    }
}
