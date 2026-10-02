using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Unity
{
    [DisallowMultipleComponent]
    public sealed class ConveyorSurface : MonoBehaviour
    {
        [SerializeField] private Vector3 localVelocity = new Vector3(0, 0, 0.5f);
        [SerializeField, Min(0)] private float acceleration = 2, maximumSpeed = 3;
        private readonly Dictionary<Rigidbody, int> contacts = new Dictionary<Rigidbody, int>();
        public bool Powered { get; set; } = true;
        private void OnCollisionEnter(Collision collision)
        { if (collision.rigidbody != null) { contacts.TryGetValue(collision.rigidbody, out int n); contacts[collision.rigidbody] = n + 1; } }
        private void OnCollisionExit(Collision collision)
        { if (collision.rigidbody != null && contacts.TryGetValue(collision.rigidbody, out int n)) { if (n <= 1) contacts.Remove(collision.rigidbody); else contacts[collision.rigidbody] = n - 1; } }
        private void FixedUpdate()
        {
            if (!Powered) return;
            Vector3 target = Vector3.ClampMagnitude(transform.TransformDirection(localVelocity), maximumSpeed);
            foreach (var pair in contacts)
            {
                var body = pair.Key;
                if (body == null || body.isKinematic) continue;
                Vector3 planar = Vector3.ProjectOnPlane(body.linearVelocity, transform.up);
                body.AddForce(Vector3.ClampMagnitude((target - planar) / Time.fixedDeltaTime, acceleration), ForceMode.Acceleration);
            }
        }
        private void OnDisable() { contacts.Clear(); }
    }
}
