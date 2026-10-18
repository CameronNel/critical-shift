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
        private Action<Exception> reportFailure;
        private bool gripping, failed;
        private Vector2 movement;
        private Vector3 horizontalVelocity;
        private float verticalSpeed, yaw, pitch;
        private float jumpBuffer, groundGrace;
        private readonly RaycastHit[] supportHits = new RaycastHit[32];
        public float WalkSpeed { get; set; } = 3.2f;
        public bool Grounded
        {
            get
            {
                if (failed) return false;
                try { return ObserveGrounded(); }
                catch (Exception exception) { Fail(exception); return false; }
            }
        }
        public float CarrySpeedScale { get; private set; } = 1;
        public Vector3 MeasuredVelocity { get; private set; }

        public void Initialize(Transform eyePivot, Func<WorkerView> worker, Func<bool> authority, Action<Exception> onFailure,
            Func<float> readCarriedMass = null, Func<Vector3?> readGripStand = null,
            Func<Rigidbody, bool> readPushPermission = null)
        {
            if (eyes != null || eyePivot == null) throw new InvalidOperationException("Bind one explicit eye pivot.");
            if (worker == null) throw new ArgumentNullException(nameof(worker));
            if (authority == null) throw new ArgumentNullException(nameof(authority));
            if (onFailure == null) throw new ArgumentNullException(nameof(onFailure));
            var walkingController = GetComponent<CharacterController>();
            if (walkingController == null) throw new InvalidOperationException("The walking motor requires its local capsule.");
            eyes = eyePivot; readWorker = worker; canSimulate = authority;
            carriedMass = readCarriedMass;
            gripStand = readGripStand;
            mayPush = readPushPermission;
            reportFailure = onFailure;
            controller = walkingController;
            yaw = transform.eulerAngles.y;
        }

        public void SetMovement(Vector2 value)
        {
            if (!Finite(value)) throw new ArgumentException("Movement must be finite.");
            if (failed || controller == null || !controller.enabled || canSimulate == null || !canSimulate() ||
                readWorker?.Invoke()?.CanInteract != true) { movement = Vector2.zero; return; }
            movement = Vector2.ClampMagnitude(value, 1);
        }

        public void RequestJump()
        {
            if (failed || controller == null || !controller.enabled || canSimulate == null || !canSimulate() ||
                readWorker?.Invoke()?.CanInteract != true || (gripStand != null && gripStand().HasValue))
            { jumpBuffer = 0; return; }
            jumpBuffer = 0.12f;
        }

        public void Look(Vector2 delta)
        {
            if (!Finite(delta)) throw new ArgumentException("View input must be finite.");
            if (failed || eyes == null || controller == null || canSimulate == null || !canSimulate()) return;
            var worker = readWorker();
            if (worker == null || worker.Awareness != WorkerAwareness.Alert ||
                (worker.Pose == WorkerPose.Upright ? !controller.enabled : controller.enabled)) return;
            yaw = Mathf.Repeat(yaw + Mathf.Clamp(delta.x, -150, 150) * 0.2f, 360);
            pitch = Mathf.Clamp(pitch - Mathf.Clamp(delta.y, -150, 150) * 0.2f, -75, 75);
            if (worker.Pose == WorkerPose.Upright)
            {
                transform.rotation = Quaternion.Euler(0, yaw, 0); eyes.localRotation = Quaternion.Euler(pitch, 0, 0);
            }
            else eyes.rotation = Quaternion.Euler(pitch, yaw, 0); // Never rotate a dynamic ragdoll's ancestor.
        }

        private void Update()
        {
            if (failed || !isActiveAndEnabled) return;
            try { UpdateMotion(); }
            catch (Exception exception) { Fail(exception); }
        }

        private void UpdateMotion()
        {
            if (controller == null || !controller.enabled || readWorker == null || canSimulate == null || !canSimulate())
            { ClearMotion(); return; }
            var worker = readWorker();
            if (worker == null || !worker.CanInteract) { movement = Vector2.zero; ClearMotion(); return; }
            if (WalkSpeed <= 0 || float.IsNaN(WalkSpeed) || float.IsInfinity(WalkSpeed))
                throw new InvalidOperationException("Worker speed must be finite and positive.");
            // A long frame cannot become an unbounded collision-controller teleport.
            float dt = Mathf.Min(Time.deltaTime, 0.05f);
            // Keep the throwing observation inside this update's failure boundary. A public getter's
            // false return after reporting a fault must never let this same frame continue into Move.
            bool grounded = ObserveGrounded();
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
            // Explicit queries may synchronously report a binding fault and stop this world.
            if (!controller.enabled || !isActiveAndEnabled || !canSimulate() || readWorker()?.CanInteract != true || failed)
            { ClearMotion(); return; }
            Vector3 before = transform.position;
            var contacts = controller.Move((horizontalVelocity + Vector3.up * verticalSpeed) * dt);
            if ((contacts & CollisionFlags.Above) != 0 && verticalSpeed > 0) verticalSpeed = 0;
            if ((contacts & CollisionFlags.Below) != 0 && verticalSpeed < 0) verticalSpeed = -2;
            MeasuredVelocity = dt > 0 ? (transform.position - before) / dt : Vector3.zero;
        }

        public void ResetAfterRecovery()
        {
            if (failed || eyes == null || controller == null || !controller.enabled || readWorker?.Invoke()?.CanInteract != true)
                throw new InvalidOperationException("Reset locomotion only after the upright physical handoff is complete.");
            yaw = eyes.eulerAngles.y;
            pitch = Mathf.Clamp(Mathf.DeltaAngle(0, eyes.eulerAngles.x), -75, 75);
            // The recovery handoff has already ended dynamic motion. Align the upright capsule to the retained view.
            transform.rotation = Quaternion.Euler(0, yaw, 0); eyes.localRotation = Quaternion.Euler(pitch, 0, 0);
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

        private bool HasWalkableSupport()
        {
            // isGrounded describes the last Move, which may be shorter than the controller's movement threshold.
            // Observe current support instead: shrinking by the skin and casting twice that far admits only
            // one skin width of foot separation, never the much larger step offset or ledge-grace distance.
            float skin = Mathf.Min(controller.skinWidth, controller.radius * 0.5f);
            float radius = controller.radius - skin;
            Vector3 center = controller.transform.TransformPoint(controller.center);
            Vector3 foot = center - Vector3.up * Mathf.Max(0, controller.height * 0.5f - controller.radius);
            int count = Physics.SphereCastNonAlloc(foot, radius, Vector3.down, supportHits,
                skin * 2 + 0.002f, Physics.AllLayers, QueryTriggerInteraction.Ignore);
            if (count == supportHits.Length) throw new InvalidOperationException("Walking support observation bounds were saturated.");
            float minimumUp = Mathf.Cos(controller.slopeLimit * Mathf.Deg2Rad);
            for (int i = 0; i < count; i++)
            {
                var hit = supportHits[i]; var contact = hit.collider;
                if (contact == null || contact == controller || contact.transform.IsChildOf(controller.transform) ||
                    Physics.GetIgnoreLayerCollision(controller.gameObject.layer, contact.gameObject.layer) ||
                    Physics.GetIgnoreCollision(controller, contact)) continue;
                if (Vector3.Dot(hit.normal, Vector3.up) >= minimumUp) return true;
            }
            return false;
        }

        private bool ObserveGrounded() => !failed && controller != null && controller.enabled &&
            verticalSpeed <= 0 && HasWalkableSupport();

        private void Fail(Exception exception)
        {
            if (failed) return;
            failed = true; ClearMotion(); Array.Clear(supportHits, 0, supportHits.Length);
            // Latch and disable this driver before the owner callback can synchronously stop/tear down the world.
            // WorkerBodyRig still owns the physical capsule/ragdoll handoff.
            enabled = false; reportFailure?.Invoke(exception);
        }

        private static bool Finite(Vector2 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y);
        private void ClearMotion()
        { movement = Vector2.zero; verticalSpeed = 0; horizontalVelocity = Vector3.zero; jumpBuffer = 0; groundGrace = 0; gripping = false; MeasuredVelocity = Vector3.zero; }
        private void OnDisable() { movement = Vector2.zero; ClearMotion(); }
        private void OnApplicationFocus(bool focused) { if (!focused) { movement = Vector2.zero; jumpBuffer = 0; } }
    }
}
