using System;
using System.Collections.Generic;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    // Attach to carts, doors, falling cargo or dangerous trigger volumes.
    public sealed class WorkerCollisionHazard : MonoBehaviour
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private string identity;
        [SerializeField] private float staggerSpeed = 1.5f, knockdownSpeed = 3, incapacitateSpeed = 7, recoveryDelay = 2;
        [SerializeField] private bool dangerousTrigger;
        private readonly Dictionary<Guid, float> nextImpact = new Dictionary<Guid, float>();
        public void Observe(WorkerController worker, Vector3 relativeVelocity)
        {
            if (worker == null || gateway == null || !gateway.Running || relativeVelocity.magnitude < staggerSpeed) return;
            if (nextImpact.TryGetValue(worker.Id, out float next) && Time.time < next) return;
            nextImpact[worker.Id] = Time.time + 0.75f;
            if (relativeVelocity.magnitude < knockdownSpeed) worker.Stagger(relativeVelocity);
            else gateway.Impact(worker, Guid.Parse(identity), relativeVelocity.magnitude >= incapacitateSpeed, recoveryDelay);
        }
        private void OnCollisionEnter(Collision collision)
        { Observe(collision.collider.GetComponentInParent<WorkerController>(), collision.relativeVelocity); }
        private void OnTriggerEnter(Collider other)
        { if (dangerousTrigger) Observe(other.GetComponentInParent<WorkerController>(), Vector3.up * incapacitateSpeed); }
        private void OnValidate() { if (!Guid.TryParse(identity, out var id) || id == Guid.Empty) identity = Guid.NewGuid().ToString(); }
        private void OnDisable() { nextImpact.Clear(); }
    }
}
