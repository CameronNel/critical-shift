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
        private Func<float> carriedMass;
        private Func<Vector3?> gripStand;
        private Func<Rigidbody, bool> mayPush;
        private bool gripping;
        private Vector2 movement;
        private Vector3 horizontalVelocity;
        private float verticalSpeed, yaw, pitch;
        private float jumpBuffer, groundGrace;
        public float WalkSpeed { get; set; } = 3.2f;
        public bool Grounded => controller != null && controller.isGrounded;
        public float CarrySpeedScale { get; private set; } = 1;
        public Vector3 MeasuredVelocity { get; private set; }

        public void Initialize(Transform eyePivot, Func<WorkerView> worker, Func<bool> authority,
            Func<float> readCarriedMass = null, Func<Vector3?> readGripStand = null,
            Func<Rigidbody, bool> readPushPermission = null)
        {
            if (eyes != null || eyePivot == null) throw new InvalidOperationException("Bind one explicit eye pivot.");
            eyes = eyePivot; readWorker = worker ?? throw new ArgumentNullException(nameof(worker));
            canSimulate = authority ?? throw new ArgumentNullException(nameof(authority));
            carriedMass = readCarriedMass;
            gripStand = readGripStand;
            mayPush = readPushPermission;
            controller = GetComponent<CharacterController>();
            yaw = transform.eulerAngles.y;
        }

        public void SetMovement(Vector2 value)
        {
            if (!Finite(value)) throw new ArgumentException("Movement must be finite.");
            movement = Vector2.ClampMagnitude(value, 1);
        }

        public void RequestJump()
        {
            if (controller == null || !controller.enabled || canSimulate == null || !canSimulate() ||
                readWorker?.Invoke()?.CanInteract != true || (gripStand != null && gripStand().HasValue))
            { jumpBuffer = 0; return; }
            jumpBuffer = 0.12f;
        }

        public void Look(Vector2 delta)
        {
            if (!Finite(delta)) throw new ArgumentException("View input must be finite.");
            if (eyes == null || canSimulate == null || !canSimulate() || readWorker()?.CanInteract != true) return;
            yaw += Mathf.Clamp(delta.x, -150, 150) * 0.2f;
            pitch = Mathf.Clamp(pitch - Mathf.Clamp(delta.y, -150, 150) * 0.2f, -75, 75);
            transform.rotation = Quaternion.Euler(0, yaw, 0);
            eyes.localRotation = Quaternion.Euler(pitch, 0, 0);
        }

        private void Update()
        {
            if (controller == null || !controller.enabled || readWorker == null || canSimulate == null || !canSimulate())
            { ClearMotion(); return; }
            var worker = readWorker();
            if (worker == null || !worker.CanInteract) { movement = Vector2.zero; ClearMotion(); return; }
            if (WalkSpeed <= 0 || float.IsNaN(WalkSpeed) || float.IsInfinity(WalkSpeed))
                throw new InvalidOperationException("Worker speed must be finite and positive.");
            // A long frame cannot become an unbounded collision-controller teleport.
            float dt = Mathf.Min(Time.deltaTime, 0.05f);
            bool grounded = controller.isGrounded;
            groundGrace = grounded ? 0.1f : Mathf.Max(0, groundGrace - dt);
            if (grounded && verticalSpeed < 0) verticalSpeed = -2;
            verticalSpeed = Mathf.Max(verticalSpeed - 20 * dt, -30);
            float load = carriedMass == null ? 0 : carriedMass();
            if (float.IsNaN(load) || float.IsInfinity(load) || load < 0)
                throw new InvalidOperationException("Carried physical mass must be finite and nonnegative.");
            CarrySpeedScale = Mathf.Clamp(1 / (1 + load / 20), 0.35f, 1);
            Vector3 motion = transform.right * movement.x + transform.forward * movement.y;
            Vector3? stand = gripStand == null ? null : gripStand();
            gripping = stand.HasValue;
            if (stand.HasValue)
            {
                jumpBuffer = 0; groundGrace = 0;
                Vector3 correction = Vector3.ProjectOnPlane(stand.Value - transform.position, Vector3.up);
                motion = Vector3.ClampMagnitude(correction * 10, 6);
                horizontalVelocity = motion;
            }
            else
            {
                motion *= WalkSpeed * CarrySpeedScale;
                if (jumpBuffer > 0 && groundGrace > 0)
                { verticalSpeed = 4.8f * Mathf.Sqrt(CarrySpeedScale); jumpBuffer = 0; groundGrace = 0; }
                horizontalVelocity = grounded ? motion : Vector3.MoveTowards(horizontalVelocity, motion, 4 * dt);
            }
            jumpBuffer = Mathf.Max(0, jumpBuffer - dt);
            Vector3 before = transform.position;
            var contacts = controller.Move((horizontalVelocity + Vector3.up * verticalSpeed) * dt);
            if ((contacts & CollisionFlags.Above) != 0 && verticalSpeed > 0) verticalSpeed = 0;
            if ((contacts & CollisionFlags.Below) != 0 && verticalSpeed < 0) verticalSpeed = -2;
            MeasuredVelocity = dt > 0 ? (transform.position - before) / dt : Vector3.zero;
        }

        public void ResetAfterRecovery()
        {
            if (eyes == null) throw new InvalidOperationException("Locomotion is not bound.");
            yaw = transform.eulerAngles.y;
            pitch = Mathf.DeltaAngle(0, eyes.localEulerAngles.x);
            movement = Vector2.zero; ClearMotion(); verticalSpeed = -2;
        }

        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var body = hit.rigidbody;
            if (body == null || body.isKinematic || hit.moveDirection.y < -0.3f || movement.sqrMagnitude < 0.01f ||
                gripping || canSimulate == null || !canSimulate() || readWorker()?.CanInteract != true ||
                mayPush == null || !mayPush(body)) return;
            Vector3 direction = Vector3.ProjectOnPlane(hit.moveDirection, Vector3.up).normalized;
            body.AddForceAtPosition(direction * 1.5f, hit.point, ForceMode.Force);
        }

        private static bool Finite(Vector2 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y);
        private void ClearMotion()
        { verticalSpeed = 0; horizontalVelocity = Vector3.zero; jumpBuffer = 0; groundGrace = 0; gripping = false; MeasuredVelocity = Vector3.zero; }
        private void OnDisable() { movement = Vector2.zero; ClearMotion(); }
        private void OnApplicationFocus(bool focused) { if (!focused) { movement = Vector2.zero; jumpBuffer = 0; } }
    }
}
