using System;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        private readonly BonkOperations _bonks;
        public BonkView? GetWorkerBonk(Guid actor) => _bonks.Get(actor);
        // Geometry is a trusted host observation, never a client-provided damage assertion.
        public WorkerReply ApplyWorkerBonkContact(Guid epoch, Guid attacker, long swing, Guid target)
        {
            var observed = _bonks.Get(attacker);
            return ExecuteWorker(epoch, target, SessionTraceKind.Impact, swing, false, () =>
            {
                if (attacker == target || !_bonks.CanContact(attacker, swing, out var attack)) return new WorkerReply(WorkerStatus.InvalidState);
                long sequence = _bonks.NextObservation(target, attack!.Tool);
                var reply = _workers.Impact(_interaction, target, sequence, WorkerImpact.Knockdown,
                    BonkOperations.RecoveryDelay, _timeline.ElapsedMilliseconds, attack.Tool, attack.Cause);
                if (reply.Changed) _bonks.Consume(attack, target, sequence);
                return reply;
            }, hazardId: observed?.Tool ?? Guid.Empty, causeId: observed?.Cause ?? Guid.Empty, severity: WorkerImpact.Knockdown);
        }
        public bool CancelWorkerBonk(Guid epoch, Guid attacker, long swing)
        {
            RequireIdle(); if (Readiness(epoch).HasValue) return false;
            long next = NextRevision(); if (!_bonks.Cancel(attacker, swing)) return false; _revision = next; return true;
        }
        public bool BlockWorkerBonk(Guid epoch, Guid attacker, long swing)
        {
            RequireIdle();
            if (Readiness(epoch).HasValue || _timeline.Phase != TimelinePhase.Running || !_bonks.CanContact(attacker, swing, out var attack)) return false;
            long next = NextRevision(); _bonks.Consume(attack!); _revision = next; return true;
        }
    }
}
