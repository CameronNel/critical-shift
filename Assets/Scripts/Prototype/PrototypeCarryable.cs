using UnityEngine;

namespace CriticalShift.Prototype
{
    [RequireComponent(typeof(Rigidbody))]
    public sealed class PrototypeCarryable : MonoBehaviour
    {
        public float holdDistance = 2.25f;
        public float maxHoldDistance = 3.5f;
        public float throwImpulse = 7f;
        public bool IsHeld { get; internal set; }
        public Rigidbody Body { get; private set; }
        void Awake() => Body = GetComponent<Rigidbody>();
    }
}
