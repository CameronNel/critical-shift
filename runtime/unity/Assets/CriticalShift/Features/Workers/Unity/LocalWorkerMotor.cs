using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Local fixture locomotion only. Does not claim ragdoll, recovery or production input acceptance.</summary>
    [DisallowMultipleComponent, RequireComponent(typeof(CharacterController))]
    public sealed class LocalWorkerMotor : MonoBehaviour
    {
        private CharacterController controller;
        private Transform eyes;
        private Func<WorkerView> readWorker;
        private Func<bool> canSimulate;
        private Vector2 movement;
        private float verticalSpeed, yaw, pitch;
        public float WalkSpeed { get; set; } = 3.2f;
        public bool Grounded => controller != null && controller.isGrounded;

        public void Initialize(Transform eyePivot, Func<WorkerView> worker, Func<bool> authority)
        {
            if (eyes != null || eyePivot == null) throw new InvalidOperationException("Bind one explicit eye pivot.");
            eyes = eyePivot; readWorker = worker ?? throw new ArgumentNullException(nameof(worker));
            canSimulate = authority ?? throw new ArgumentNullException(nameof(authority));
            controller = GetComponent<CharacterController>();
            yaw = transform.eulerAngles.y;
        }

        public void SetMovement(Vector2 value)
        {
            if (!Finite(value)) throw new ArgumentException("Movement must be finite.");
            movement = Vector2.ClampMagnitude(value, 1);
        }

        public void Look(Vector2 delta)
        {
            if (!Finite(delta)) throw new ArgumentException("View input must be finite.");
            if (eyes == null || canSimulate == null || !canSimulate()) return;
            yaw += Mathf.Clamp(delta.x, -150, 150) * 0.2f;
            pitch = Mathf.Clamp(pitch - Mathf.Clamp(delta.y, -150, 150) * 0.2f, -75, 75);
            transform.rotation = Quaternion.Euler(0, yaw, 0);
            eyes.localRotation = Quaternion.Euler(pitch, 0, 0);
        }

        private void Update()
        {
            if (controller == null || readWorker == null || canSimulate == null || !canSimulate()) return;
            var worker = readWorker();
            if (worker == null || !worker.CanInteract) { movement = Vector2.zero; return; }
            if (WalkSpeed <= 0 || float.IsNaN(WalkSpeed) || float.IsInfinity(WalkSpeed))
                throw new InvalidOperationException("Worker speed must be finite and positive.");
            // A long frame cannot become an unbounded collision-controller teleport.
            float dt = Mathf.Min(Time.deltaTime, 0.05f);
            if (controller.isGrounded && verticalSpeed < 0) verticalSpeed = -2;
            verticalSpeed = Mathf.Max(verticalSpeed - 20 * dt, -30);
            Vector3 motion = transform.right * movement.x + transform.forward * movement.y;
            controller.Move((motion * WalkSpeed + Vector3.up * verticalSpeed) * dt);
        }

        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var body = hit.rigidbody;
            if (body == null || body.isKinematic || hit.moveDirection.y < -0.3f || movement.sqrMagnitude < 0.01f) return;
            Vector3 direction = Vector3.ProjectOnPlane(hit.moveDirection, Vector3.up).normalized;
            body.AddForceAtPosition(direction * 1.5f, hit.point, ForceMode.Force);
        }

        private static bool Finite(Vector2 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y);
        private void OnDisable() { movement = Vector2.zero; verticalSpeed = 0; }
        private void OnApplicationFocus(bool focused) { if (!focused) movement = Vector2.zero; }
    }
}
