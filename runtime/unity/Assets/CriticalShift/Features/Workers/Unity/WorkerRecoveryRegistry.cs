using System;
using System.Collections.Generic;
using CriticalShift.Application;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Explicit routing to each worker's physical clearance policy; missing bindings never imply Safe.</summary>
    public sealed class WorkerRecoveryRegistry : IWorkerRecoveryPolicy
    {
        private readonly Dictionary<Guid, WorkerRecoveryPlacement> policies = new Dictionary<Guid, WorkerRecoveryPlacement>();
        private Guid epoch;
        private bool sealedBindings;
        public void Bind(Guid worldEpoch, Guid worker, WorkerRecoveryPlacement placement)
        {
            if (sealedBindings || worldEpoch == Guid.Empty || worker == Guid.Empty || placement == null || policies.ContainsKey(worker) ||
                policies.Count >= 4 || (epoch != Guid.Empty && epoch != worldEpoch))
                throw new InvalidOperationException("Bind one bounded recovery policy per worker in the same world epoch.");
            epoch = worldEpoch; policies.Add(worker, placement);
        }
        public void Seal()
        {
            if (sealedBindings || policies.Count == 0) throw new InvalidOperationException("Seal the populated recovery bindings once.");
            sealedBindings = true;
        }
        public RecoveryClearance Evaluate(Guid worldEpoch, Guid workerId, long recoveryAttempt) =>
            sealedBindings && worldEpoch == epoch && policies.TryGetValue(workerId, out var policy) ?
                policy.Evaluate(worldEpoch, workerId, recoveryAttempt) : RecoveryClearance.Unavailable;
        public void Clear()
        {
            foreach (var policy in policies.Values) policy.Clear();
            policies.Clear(); epoch = Guid.Empty; sealedBindings = false;
        }
    }
}
