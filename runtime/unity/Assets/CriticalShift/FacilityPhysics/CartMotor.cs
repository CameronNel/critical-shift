using System;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded local-host cart forces. Cargo measurements influence handling, never material accounting.</summary>
    [DisallowMultipleComponent, RequireComponent(typeof(Rigidbody))]
    public sealed class CartMotor : MonoBehaviour
    {
        private Rigidbody body;
        private Func<bool> maySimulate;
        private Func<float> readCargoMass;
        private float throttle, steering;
        private bool brake;
        public float MaximumSpeed { get; set; } = 3.5f;
        public float SafeCargoMass { get; set; } = 80f;
        public bool HasDriveAuthority => isActiveAndEnabled && body != null && !body.isKinematic && body.detectCollisions && maySimulate != null && maySimulate();
        public float Steering => HasDriveAuthority ? steering : 0;
        public float CargoMass => readCargoMass == null ? 0 : Mathf.Max(0, readCargoMass());
        public bool Overloaded => CargoMass > SafeCargoMass;
        public float Speed => body == null ? 0 : Vector3.ProjectOnPlane(body.linearVelocity, Vector3.up).magnitude;

        public void Initialize(Func<bool> authority, Func<float> cargo)
        {
            if (maySimulate != null) throw new InvalidOperationException("Cart motor was already bound.");
            if (authority == null || cargo == null) throw new ArgumentException("Cart authority and cargo observations are required.");
            var candidate = GetComponent<Rigidbody>();
            if (candidate == null || candidate.isKinematic || !candidate.detectCollisions)
                throw new InvalidOperationException("The cart requires a dynamic Rigidbody with collision detection enabled.");
            body = candidate; maySimulate = authority; readCargoMass = cargo;
        }

        public void SetDrive(float forward, float turn, bool braking)
        {
            if (float.IsNaN(forward) || float.IsInfinity(forward) || float.IsNaN(turn) || float.IsInfinity(turn))
                throw new ArgumentException("Cart controls must be finite.");
            throttle = Mathf.Clamp(forward, -1, 1); steering = Mathf.Clamp(turn, -1, 1); brake = braking;
        }

        private void FixedUpdate()
        {
            if (!HasDriveAuthority) return;
            if (MaximumSpeed <= 0 || SafeCargoMass <= 0 || float.IsNaN(MaximumSpeed) || float.IsInfinity(MaximumSpeed) ||
                float.IsNaN(SafeCargoMass) || float.IsInfinity(SafeCargoMass))
                throw new InvalidOperationException("Cart speed and load budgets must be positive.");
            Vector3 planar = Vector3.ProjectOnPlane(body.linearVelocity, Vector3.up);
            Vector3 forward = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            float load = Mathf.Clamp(CargoMass / SafeCargoMass, 0, 3);
            float targetSpeed = throttle * MaximumSpeed / (1 + load * 0.35f);
            Vector3 acceleration;
            if (brake) acceleration = Vector3.ClampMagnitude(-planar * 8, 12);
            else
            {
                float along = Vector3.Dot(planar, forward);
                Vector3 sideways = planar - forward * along;
                acceleration = forward * Mathf.Clamp((targetSpeed - along) * 4, -5, 5) - sideways * 4;
            }
            body.AddForce(Vector3.ClampMagnitude(acceleration, 12), ForceMode.Acceleration);
            float direction = Mathf.Abs(throttle) > 0.05f ? Mathf.Sign(throttle) : Mathf.Sign(Vector3.Dot(planar, forward));
            float desiredTurn = brake ? 0 : steering * direction * Mathf.Clamp01(planar.magnitude) / (1 + load * 0.25f);
            body.AddTorque(Vector3.up * Mathf.Clamp((desiredTurn - body.angularVelocity.y) * 5, -4, 4), ForceMode.Acceleration);
            if (planar.magnitude > MaximumSpeed)
                body.linearVelocity = Vector3.ClampMagnitude(planar, MaximumSpeed) + Vector3.up * body.linearVelocity.y;
        }

        private void OnDisable() { throttle = 0; steering = 0; brake = true; }
        private void OnApplicationFocus(bool focused) { if (!focused) SetDrive(0, 0, true); }
    }
}
