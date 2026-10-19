#nullable enable
using System;

namespace CriticalShift.Application
{
    /// <summary>
    /// One trusted host producer per worker/source pair. Presence is observed by the
    /// engine adapter; Workers owns receipts and condition. This is not a client port.
    /// </summary>
    public sealed class WorkerContaminationFeed
    {
        private readonly WorldSession world;
        private long sequence, nextEligibleAt;
        private bool failed;
        public WorkerContaminationFeed(WorldSession session, Guid worker, Guid source)
        {
            world = session ?? throw new ArgumentNullException(nameof(session));
            if (session.View.Phase != WorldPhase.Setup || session.GetWorker(worker) == null || !session.HasWorkerContaminationSource(source))
                throw new InvalidOperationException("Bind a registered worker/source pair before starting its world.");
            WorkerId = worker; SourceId = source; Epoch = session.Epoch;
        }
        public Guid WorkerId { get; }
        public Guid SourceId { get; }
        public Guid Epoch { get; }
        public long LastAcceptedSequence => sequence;
        public long NextEligibleAtMilliseconds => nextEligibleAt;

        /// <summary>Called only after trusted current presence was observed. No historical catch-up.</summary>
        public WorkerReply? ObserveIfDue()
        {
            if (failed) throw new InvalidOperationException("A failed contamination feed cannot manufacture a retry.");
            if (world.View.Phase != WorldPhase.Running || world.GetWorker(WorkerId) == null || world.View.ElapsedMilliseconds < nextEligibleAt)
                return null;
            try
            {
                long next = checked(sequence + 1), at = world.View.ElapsedMilliseconds;
                Guid cause = Guid.NewGuid();
                var reply = world.ObserveWorkerContamination(Epoch, WorkerId, SourceId, next, cause, at);
                var contact = reply.ContaminationContact;
                if ((reply.Status != WorkerStatus.Applied && reply.Status != WorkerStatus.NoChange && reply.Status != WorkerStatus.CoolingDown) ||
                    contact == null || contact.Sequence != next || contact.SourceId != SourceId || contact.CauseId != cause ||
                    contact.SampleShiftMilliseconds != at || contact.OriginalOutcome != reply.Status || reply.Worker?.Id != WorkerId ||
                    contact.NextEligibleAtMilliseconds < at)
                    throw new InvalidOperationException("The trusted contamination observation stream lost its sole producer or binding.");
                sequence = next; nextEligibleAt = contact.NextEligibleAtMilliseconds; return reply;
            }
            catch { failed = true; throw; }
        }
    }
}
