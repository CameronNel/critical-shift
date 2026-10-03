using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    [DisallowMultipleComponent]
    public sealed class RagdollCollisionRelay : MonoBehaviour
    {
        [SerializeField] private WorkerCollisionHazard hazard;
        private void OnCollisionEnter(Collision collision) { if (hazard != null) hazard.ObserveCollision(collision); }
    }
}
