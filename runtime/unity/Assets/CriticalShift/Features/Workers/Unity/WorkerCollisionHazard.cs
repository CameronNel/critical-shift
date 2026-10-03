using System;
using System.Collections.Generic;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    // Host observations from carts, doors, falling cargo and relayed ragdoll limbs.
    public sealed class WorkerCollisionHazard : MonoBehaviour
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private string identity;
        [SerializeField] private float staggerSpeed = 1.5f, knockdownSpeed = 3, incapacitateSpeed = 7, recoveryDelay = 2;
        [SerializeField] private bool dangerousTrigger;
        private readonly Dictionary<Guid, double> nextImpact = new Dictionary<Guid, double>();
        private void Awake()
        {
            if (!Guid.TryParse(identity, out var id) || id == Guid.Empty || !float.IsFinite(staggerSpeed) || !float.IsFinite(knockdownSpeed) ||
                !float.IsFinite(incapacitateSpeed) || !float.IsFinite(recoveryDelay) || staggerSpeed <= 0 || knockdownSpeed < staggerSpeed ||
                incapacitateSpeed < knockdownSpeed || recoveryDelay < 0 || recoveryDelay > 60)
            { Debug.LogError("Assign a hazard identity and ordered finite impact thresholds/delay.", this); enabled = false; }
        }
        public void Observe(WorkerController worker, Vector3 relativeVelocity, Vector3? point = null, Vector3? normal = null)
        {
            if (!isActiveAndEnabled || worker == null || gateway == null || !gateway.Running || !Finite(relativeVelocity)) return;
            if (GetComponentInParent<WorkerController>() == worker) return;
            Vector3 direction = normal.HasValue ? normal.Value.normalized : relativeVelocity.normalized;
            if (!Finite(direction)) return;
            float closing = Mathf.Max(0, Vector3.Dot(relativeVelocity, direction));
            if (closing < staggerSpeed) return;
            double now = Time.realtimeSinceStartupAsDouble;
            if (nextImpact.TryGetValue(worker.Id, out double next) && now < next) return;
            if (!nextImpact.ContainsKey(worker.Id) && nextImpact.Count >= 4) return;
            nextImpact[worker.Id] = now + .75;
            if (closing < knockdownSpeed) worker.Stagger(direction * closing);
            else
            {
                float mass = worker.PhysicalMass;
                var sourceWorker = GetComponentInParent<WorkerController>(); var sourceBody = GetComponentInParent<Rigidbody>();
                float sourceMass = sourceWorker != null ? sourceWorker.PhysicalMass : sourceBody != null && !sourceBody.isKinematic ? sourceBody.mass : mass;
                float reducedMass = sourceMass > 0 && mass > 0 ? sourceMass * mass / (sourceMass + mass) : 0;
                // Dynamic ragdoll contact already receives the solver impulse; do not apply it twice.
                Vector3 impulse = worker.Down ? Vector3.zero : direction * closing * reducedMass;
                gateway.Impact(worker, Guid.Parse(identity), closing >= incapacitateSpeed, recoveryDelay, impulse, point);
            }
        }
        public void ObserveCollision(Collision collision)
        {
            if (collision.contactCount == 0) return;
            var contact = collision.GetContact(0);
            Observe(collision.collider.GetComponentInParent<WorkerController>(), collision.relativeVelocity, contact.point, -contact.normal);
        }
        private void OnCollisionEnter(Collision collision) { ObserveCollision(collision); }
        private void OnTriggerEnter(Collider other)
        { if (dangerousTrigger) Observe(other.GetComponentInParent<WorkerController>(), Vector3.up * incapacitateSpeed); }
        private static bool Finite(Vector3 value) => float.IsFinite(value.x) && float.IsFinite(value.y) && float.IsFinite(value.z);
        private void OnValidate() { if (!Guid.TryParse(identity, out var id) || id == Guid.Empty) identity = Guid.NewGuid().ToString(); }
        private void OnDisable() { nextImpact.Clear(); }
    }
}
