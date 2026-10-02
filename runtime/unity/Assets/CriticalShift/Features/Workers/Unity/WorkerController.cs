using System;
using CriticalShift.Unity.Shared;
using UnityEngine;
using UnityEngine.Events;

namespace CriticalShift.Features.Workers.Unity
{
    [RequireComponent(typeof(CharacterController)), DisallowMultipleComponent]
    public sealed class WorkerController : WorkerScenePort
    {
        [SerializeField] private SceneInteractionGateway gateway;
        [SerializeField] private WorkerMovementAnimator movement;
        [SerializeField] private CharacterController capsule;
        [SerializeField] private Transform eye, grip, toolGrip;
        [SerializeField] private WorkerRagdoll ragdoll;
        [SerializeField] private WorkerCrouchPose crouchPose;
        [SerializeField] private Transform leftHand, rightHand, head;
        [SerializeField] private bool localInput = true;
        [SerializeField] private LayerMask interactionMask = ~0, clearanceMask = ~0;
        [SerializeField] private Renderer[] localHeadMeshes = Array.Empty<Renderer>();
        [SerializeField] private Renderer[] suitMeshes = Array.Empty<Renderer>(), bareMeshes = Array.Empty<Renderer>();
        [SerializeField, Range(0, 31)] private int hiddenHeadLayer = 29;
        [SerializeField] private float sensitivity = 2, acceleration = 12, gravity = 15, jumpHeight = 0.35f;
        [SerializeField] private float crouchHeight = 1.05f, standingHeight = 1.55f;
        [Serializable] private struct ContactTiming
        { public SceneOperation operation; [Range(0, 1)] public float normalizedCue; }
        [SerializeField] private ContactTiming[] contactTimings = Array.Empty<ContactTiming>();
        [SerializeField] private UnityEvent<Vector3> pingEffect;
        private readonly ActionCueClock cueClock = new ActionCueClock();
        private Collider[] colliders;
        private Vector3 planar, velocity;
        private MovementPose pose;
        private SceneTarget actionTarget;
        private SceneOperation operation;
        private WorkerActionPlan plan;
        private float pitch, yawRate, vertical, airborne, jumpTime = -1, groundGrace, jumpBuffer;
        private float eyeHeight;
        private Vector3 headOffset;
        private ulong actionSequence;
        private bool acting, heldAction, crouched, focused = true, station;
        private long recoveryAttempt;
        private float recoveryRemaining, stationTime, reactionRemaining;
        public string LastFeedback { get; private set; }
        public override Transform Eye => eye;
        public override Transform Grip => (pose == MovementPose.Shovel || pose == MovementPose.Pickaxe) && toolGrip != null ? toolGrip : grip;
        public override Collider[] BodyColliders => colliders ?? (colliders = GetComponentsInChildren<Collider>());
        public override bool Grounded => capsule.enabled && capsule.isGrounded;
        public override bool Down => ragdoll != null && ragdoll.Active;
        public override Vector3 Velocity => velocity;
        public override bool RecoveryClear => ClearCapsule(transform.position, standingHeight);

        private void Start()
        {
            if (gateway == null || movement == null || movement.ModelRoot == transform || capsule == null || eye == null || grip == null || ragdoll == null || !ragdoll.Valid)
            { Debug.LogError("Assign gateway, movement, capsule, eye, grip and ragdoll.", this); enabled = false; return; }
            colliders = GetComponentsInChildren<Collider>();
            eyeHeight = eye.localPosition.y;
            if (head != null) headOffset = transform.InverseTransformVector(eye.position - head.position);
            var view = eye.GetComponent<Camera>(); if (view != null) view.enabled = localInput;
            if (localInput)
            {
                foreach (var renderer in localHeadMeshes) if (renderer != null) renderer.gameObject.layer = hiddenHeadLayer;
                var camera = eye.GetComponent<Camera>();
                if (camera != null) { camera.cullingMask &= ~(1 << hiddenHeadLayer); camera.fieldOfView = 60; }
                SetCursor(true);
            }
        }

        private void Update()
        {
            if (gateway == null || !gateway.Running || !movement.Ready) { CancelSceneActions(); return; }
            float dt = Mathf.Min(Time.deltaTime, 0.1f);
            if (station) { TickStation(dt); return; }
            if (Down) { TickRecovery(dt); return; }
            if (recoveryAttempt != 0)
            {
                recoveryRemaining -= dt;
                movement.ApplySample(new MovementAnimationSample(0, 0, 0, true), dt);
                if (recoveryRemaining <= 0)
                {
                    if (!gateway.CompleteRecovery(this, recoveryAttempt)) ragdoll.Activate(Vector3.zero);
                    recoveryAttempt = 0;
                }
                return;
            }
            reactionRemaining = Mathf.Max(0, reactionRemaining - dt);
            bool input = localInput && focused && gateway.CanAct(this) && reactionRemaining == 0;
            Vector2 axes = input ? new Vector2(Key(KeyCode.D) - Key(KeyCode.A), Key(KeyCode.W) - Key(KeyCode.S)) : Vector2.zero;
            bool sprint = input && Input.GetKey(KeyCode.LeftShift), walk = input && Input.GetKey(KeyCode.LeftAlt);
            if (input)
            {
                float yaw = Input.GetAxisRaw("Mouse X") * sensitivity;
                if (Input.GetKey(KeyCode.C)) { gateway.RotateHeld(this, yaw); yaw = 0; }
                if (acting) yaw = 0;
                transform.Rotate(0, yaw, 0); yawRate = dt > 0 ? Mathf.Clamp(yaw / dt, -1000, 1000) : 0;
                pitch = Mathf.Clamp(pitch - Input.GetAxisRaw("Mouse Y") * sensitivity, -80, 80);
                eye.localRotation = Quaternion.Euler(pitch, 0, 0);
                SetCrouch(Input.GetKey(KeyCode.LeftControl));
                if (Input.GetKeyDown(KeyCode.Space)) jumpBuffer = 0.15f;
                ReadActions();
            }
            else yawRate = 0;
            TickAction(dt);
            groundGrace = Grounded ? 0.10f : Mathf.Max(0, groundGrace - dt);
            jumpBuffer = Mathf.Max(0, jumpBuffer - dt);
            if (jumpBuffer > 0 && groundGrace > 0 && !acting && !crouched && pose == MovementPose.Free && jumpTime < 0)
            {
                if (movement.BeginJump(groundGrace > 0)) { jumpTime = 0; jumpBuffer = groundGrace = 0; }
            }
            if (jumpTime >= 0)
            {
                float before = jumpTime; jumpTime += dt;
                float spring = movement.Duration(MovementClip.JUMP) * 7f / 14;
                if (before < spring && jumpTime >= spring) vertical = Mathf.Sqrt(2 * gravity * jumpHeight);
                if (jumpTime >= movement.Duration(MovementClip.JUMP)) jumpTime = -1;
            }
            Vector3 desired = Direction(axes, sprint, walk);
            if (acting || jumpTime >= 0) desired = Vector3.zero;
            if (crouched || (input && Input.GetKey(KeyCode.B))) desired *= 0.5f;
            planar = Vector3.MoveTowards(planar, desired, acceleration * (Grounded ? 1 : 0.2f) * dt);
            if (Grounded && vertical < 0) vertical = -2;
            vertical -= gravity * dt;
            Vector3 beforePosition = transform.position;
            var flags = capsule.Move((planar + Vector3.up * vertical) * dt);
            if ((flags & CollisionFlags.Above) != 0 && vertical > 0) vertical = 0;
            velocity = dt > 0 ? (transform.position - beforePosition) / dt : Vector3.zero;
            Vector3 local = transform.InverseTransformDirection(velocity);
            movement.ApplySample(new MovementAnimationSample(local.x, local.z, velocity.y, Grounded, pose, yawRate), dt);
            if (Grounded)
            {
                if (airborne > 1.2f) gateway.Impact(this, Id, false, 1);
                airborne = 0;
            }
            else airborne += dt;
        }

        private float Key(KeyCode key) => Input.GetKey(key) ? 1 : 0;
        private void LateUpdate()
        {
            if (!enabled || !gateway || !gateway.Running || Down) return;
            ragdoll.BlendToAnimation(Time.deltaTime);
            if (crouched && crouchPose != null) crouchPose.Apply(standingHeight - crouchHeight);
            if (head != null) eye.position = head.position + transform.TransformVector(headOffset);
            if (leftHand != null && rightHand != null) grip.position = (leftHand.position + rightHand.position) * 0.5f;
        }
        private Vector3 Direction(Vector2 input, bool sprint, bool walk)
        {
            if (input.sqrMagnitude > 1) input.Normalize();
            float forward = sprint ? 2.6f : walk ? 0.63f : 1.4f, side = 0.4f, backward = 0.63f;
            if (pose == MovementPose.Carry) forward = side = backward = sprint ? 0.96f : 0.5f;
            if (pose == MovementPose.Shovel || pose == MovementPose.Pickaxe) { forward = 1.2f; input.x = 0; input.y = Mathf.Max(0, input.y); }
            if (pose == MovementPose.Push) { forward = 0.6f; input.x = 0; input.y = Mathf.Max(0, input.y); }
            if (pose == MovementPose.Pull || pose == MovementPose.Drag)
            { backward = pose == MovementPose.Pull ? 0.5f : 0.33f; input.x = 0; input.y = Mathf.Min(0, input.y); }
            return transform.right * input.x * side + transform.forward * input.y * (input.y < 0 ? backward : forward);
        }

        private void SetCrouch(bool value)
        {
            if (!value && crouched && !RecoveryClear) return;
            crouched = value;
            capsule.height = value ? crouchHeight : standingHeight;
            capsule.center = Vector3.up * capsule.height / 2;
            var p = eye.localPosition; p.y = eyeHeight - (standingHeight - capsule.height); eye.localPosition = p;
        }

        private SceneTarget LookTarget()
        {
            if (!Physics.Raycast(eye.position, eye.forward, out var hit, 2.5f, interactionMask, QueryTriggerInteraction.Ignore)) return null;
            return hit.collider.GetComponentInParent<SceneTarget>();
        }
        private void ReadActions()
        {
            if (Input.GetKeyDown(KeyCode.Escape)) { focused = false; SetCursor(false); CancelSceneActions(); return; }
            if (Input.GetKeyDown(KeyCode.G)) StartAction(gateway.Held(this), SceneOperation.Release);
            if (Input.GetKeyDown(KeyCode.V)) StartAction(gateway.Held(this), SceneOperation.Place);
            if (Input.GetKeyDown(KeyCode.T)) StartAction(gateway.Held(this), Input.GetKey(KeyCode.LeftAlt) ? SceneOperation.ThrowUnder : SceneOperation.ThrowOver);
            if (Input.GetKeyDown(KeyCode.F)) StartAction(LookTarget(), SceneOperation.Grab);
            if (Input.GetKeyDown(KeyCode.E)) { var t = LookTarget(); if (t != null) StartAction(t, t.Operation); }
            if (Input.GetKeyDown(KeyCode.P)) StartAction(null, SceneOperation.Point);
            if (Input.GetKeyDown(KeyCode.Tab)) LastFeedback = gateway.Describe(LookTarget());
            if (Input.GetKeyDown(KeyCode.R)) StartAction(null, SceneOperation.Radio);
            if (Input.GetMouseButtonDown(0) && gateway.Held(this) != null) StartAction(LookTarget(), SceneOperation.Dig);
            if (heldAction && !Input.GetKey(KeyCode.E) && !Input.GetKey(KeyCode.R) && !Input.GetMouseButton(0)) CancelSceneActions();
        }

        public bool StartAction(SceneTarget target, SceneOperation value)
        {
            if (acting || station || jumpTime >= 0 || !Grounded || !gateway.CanAct(this)) return false;
            if (target == null && value != SceneOperation.Point && value != SceneOperation.Radio) return false;
            if (target != null && (!target.Supports(value) || !gateway.CanUse(this, target))) return false;
            if (value == SceneOperation.Push || value == SceneOperation.Pull || value == SceneOperation.Drag)
            { bool ok = gateway.Execute(this, target, value, out var reason); LastFeedback = reason; return ok; }
            plan = WorkerActionPlan.For(value);
            movement.ApplySample(new MovementAnimationSample(0, 0, 0, true, pose), 0);
            if (!movement.TryPlayAction(plan.Clip, ++actionSequence)) return false;
            actionTarget = target; operation = value; acting = true; heldAction = plan.Repeat;
            float contactCue = plan.Cue;
            foreach (var timing in contactTimings) if (timing.operation == value) contactCue = timing.normalizedCue;
            cueClock.Begin(movement.Duration(plan.Clip), contactCue, plan.Repeat);
            return true;
        }

        private void TickAction(float dt)
        {
            if (!acting) return;
            if (!gateway.CanAct(this) || !Grounded || (actionTarget != null && !gateway.CanUse(this, actionTarget)))
            { CancelSceneActions(); return; }
            if (cueClock.Step(dt))
            {
                if (!gateway.Execute(this, actionTarget, operation, out var reason))
                { LastFeedback = reason; CancelSceneActions(); return; }
                if (operation == SceneOperation.Point)
                {
                    Vector3 point = Physics.Raycast(eye.position, eye.forward, out var hit, 30, interactionMask, QueryTriggerInteraction.Ignore) ? hit.point : eye.position + eye.forward * 10;
                    pingEffect?.Invoke(point);
                }
            }
            if (cueClock.Complete) { acting = heldAction = false; actionTarget = null; }
        }

        public override void SetHaulPose(SceneOperation? value)
        {
            pose = value == SceneOperation.Push ? MovementPose.Push : value == SceneOperation.Pull ? MovementPose.Pull :
                value == SceneOperation.Drag ? MovementPose.Drag : value == SceneOperation.Dig ? MovementPose.Shovel :
                value == SceneOperation.Lever ? MovementPose.Pickaxe : value.HasValue ? MovementPose.Carry : MovementPose.Free;
        }
        public void ProjectSuit(bool suited)
        { foreach (var renderer in suitMeshes) if (renderer != null) renderer.enabled = suited;
          foreach (var renderer in bareMeshes) if (renderer != null) renderer.enabled = !suited; }
        public override void CancelSceneActions()
        {
            if (movement != null && acting) movement.StopAction(actionSequence);
            acting = heldAction = false; actionTarget = null; jumpTime = -1;
            if (!gateway || !gateway.Running) { planar = velocity = Vector3.zero; station = false; recoveryAttempt = 0; }
        }

        private bool ClearCapsule(Vector3 position, float height)
        {
            float radius = capsule.radius - capsule.skinWidth;
            var hits = Physics.OverlapCapsule(position + Vector3.up * (radius + 0.02f),
                position + Vector3.up * (height - radius), radius, clearanceMask, QueryTriggerInteraction.Ignore);
            foreach (var hit in hits) if (Array.IndexOf(BodyColliders, hit) < 0) return false;
            return Physics.Raycast(position + Vector3.up * 0.1f, Vector3.down, 0.2f, clearanceMask, QueryTriggerInteraction.Ignore);
        }
        private void TickRecovery(float dt)
        {
            movement.ApplySample(default, dt);
            if (!gateway.RecoveryReady(this)) return;
            ragdoll.PrepareRoot(transform, clearanceMask);
            if (!RecoveryClear) return;
            long attempt = gateway.BeginRecovery(this);
            if (attempt == 0) return;
            bool front = ragdoll.FaceDown;
            ragdoll.BeginRecoveryBlend(); ragdoll.Freeze(); capsule.enabled = false;
            recoveryAttempt = attempt;
            var clip = front ? MovementClip.GETUP_FRONT : MovementClip.GETUP_BACK;
            recoveryRemaining = movement.Duration(clip);
            movement.PrimeGroundedAction(clip, ++actionSequence);
        }

        public void KnockDown(Vector3 impulse)
        { CancelSceneActions(); station = false; recoveryAttempt = 0; if (movement.Ready) movement.ApplySample(default, 0); capsule.enabled = false; ragdoll.Activate(impulse); }
        public void Stagger(Vector3 worldDirection)
        {
            if (!gateway.CanAct(this) || !Grounded) return;
            CancelSceneActions();
            Vector3 local = transform.InverseTransformDirection(worldDirection);
            var clip = Mathf.Abs(local.x) > Mathf.Abs(local.z) ? local.x < 0 ? MovementClip.STAGGER_L : MovementClip.STAGGER_R :
                local.z < 0 ? MovementClip.STAGGER_B : MovementClip.STAGGER_F;
            movement.TryPlayAction(clip, ++actionSequence); reactionRemaining = movement.Duration(clip);
        }
        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var hazard = hit.collider.GetComponentInParent<WorkerCollisionHazard>();
            var body = hit.collider.attachedRigidbody;
            if (hazard != null && body != null) hazard.Observe(this, body.GetPointVelocity(hit.point) - velocity);
        }
        public void BecomeUpright() { ragdoll.Freeze(); capsule.enabled = true; vertical = -2; }
        public override void PresentStation(SceneOperation value, Transform anchor)
        {
            CancelSceneActions(); ragdoll.Freeze(); capsule.enabled = false;
            transform.SetPositionAndRotation(anchor.position, anchor.rotation);
            station = true; stationTime = 0;
            if (value == SceneOperation.Reanimation) movement.PrimeGroundedAction(MovementClip.REANIM_IDLE, ++actionSequence);
            else { movement.PrimeGroundedAction(MovementClip.LOCKER_EXIT, ++actionSequence); stationTime = -movement.Duration(MovementClip.LOCKER_EXIT); }
        }
        public void ReanimationJolt()
        { movement.TryPlayAction(MovementClip.REANIM_JOLT, ++actionSequence, MovementClip.REANIM_IDLE); }
        public void ReanimationExit(long attempt)
        { recoveryAttempt = attempt; movement.TryPlayAction(MovementClip.REANIM_EXIT, ++actionSequence); stationTime = -movement.Duration(MovementClip.REANIM_EXIT); }
        private void TickStation(float dt)
        {
            movement.ApplySample(new MovementAnimationSample(0, 0, 0, true), dt);
            if (stationTime < 0)
            {
                stationTime = Mathf.Min(0, stationTime + dt);
                if (stationTime == 0)
                {
                    station = false;
                    if (recoveryAttempt == 0) BecomeUpright();
                    else if (!gateway.CompleteRecovery(this, recoveryAttempt)) KnockDown(Vector3.zero);
                    recoveryAttempt = 0;
                }
            }
        }
        private void OnApplicationFocus(bool value) { focused = value; if (!value) CancelSceneActions(); if (localInput) SetCursor(value); }
        private void OnDisable() { CancelSceneActions(); if (localInput) SetCursor(false); }
        private void OnGUI()
        { if (localInput && !string.IsNullOrEmpty(LastFeedback)) GUI.Label(new Rect(16, Screen.height - 56, Screen.width - 32, 40), LastFeedback); }
        private void SetCursor(bool value) { Cursor.lockState = value ? CursorLockMode.Locked : CursorLockMode.None; Cursor.visible = !value; }
    }
}
