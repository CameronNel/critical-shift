using UnityEngine;

namespace CriticalShift.Prototype
{
    [RequireComponent(typeof(Rigidbody))]
    public sealed class PrototypeMineCart : MonoBehaviour
    {
        public float knockdownSpeed = 1.5f;
        public float incapacitateSpeed = 5f;
        void OnCollisionEnter(Collision collision)
        {
            var worker = collision.collider.GetComponentInParent<PrototypeWorkerBody>();
            if (worker == null) return;
            float impact = collision.relativeVelocity.magnitude;
            if (impact >= incapacitateSpeed && worker.GetComponent<PrototypePlayerController>() == null) worker.Incapacitate();
            else if (impact >= knockdownSpeed) worker.KnockDown(Mathf.Lerp(1.5f, 3f, impact / incapacitateSpeed));
        }
    }
}
