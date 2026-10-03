using System;
using CriticalShift.Unity.Shared;
using UnityEngine;
using UnityEngine.Events;

namespace CriticalShift.Features.Workers.Unity
{
    [RequireComponent(typeof(CharacterController)), DisallowMultipleComponent]
    public sealed partial class WorkerController : WorkerScenePort
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
        private readonly WorkerInputState inputState = new WorkerInputState();
        private readonly RaycastHit[] lookHits = new RaycastHit[64];
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
        private bool acting, heldAction, crouched, station;
        private double feedbackUntil;
        private SceneTarget lookTarget;
        private long recoveryAttempt;
        private float recoveryRemaining, stationTime, reactionRemaining;
        public string LastFeedback { get; private set; }
        public override Transform Eye => eye;
        public override Transform Grip => (pose == MovementPose.Shovel || pose == MovementPose.Pickaxe) && toolGrip != null ? toolGrip : grip;
        public override Collider[] BodyColliders => colliders ?? (colliders = GetComponentsInChildren<Collider>());
        public override bool Grounded => capsule.enabled && capsule.isGrounded;
        public override bool Down => ragdoll != null && ragdoll.Active;
        public override Vector3 Velocity => Down ? ragdoll.Pelvis.linearVelocity : velocity;
        public override Rigidbody PhysicalBody => ragdoll != null ? ragdoll.Pelvis : null;
        public override float PhysicalMass => ragdoll != null ? ragdoll.TotalMass : 0;
        public override Collider[] PhysicalColliders => ragdoll != null ? ragdoll.Colliders : BodyColliders;
        public override bool RecoveryClear => ClearCapsule(transform.position, standingHeight);

        private void Start()
        {
            if (gateway == null || movement == null || movement.transform != transform || movement.ModelRoot == null ||
                movement.ModelRoot == transform || !movement.ModelRoot.IsChildOf(transform) || capsule == null || capsule.transform != transform ||
                eye == null || !eye.IsChildOf(transform) || grip == null || !grip.IsChildOf(transform) || ragdoll == null || ragdoll.transform != transform || !ragdoll.Valid ||
                !float.IsFinite(standingHeight) || standingHeight <= capsule.radius * 2 || !float.IsFinite(crouchHeight) || crouchHeight < capsule.radius * 2 || crouchHeight > standingHeight)
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
                inputState.SetApplicationFocus(UnityEngine.Application.isFocused);
                SetCursor(inputState.Captured);
            }
        }

        private void Update()
        {
            RestoreBonkGrip();
            bool captureChanged = localInput && inputState.UpdateCapture(Input.GetKeyDown(KeyCode.Escape),
                Input.GetMouseButtonDown(0) || Input.GetKeyDown(KeyCode.Return));
            if (captureChanged) { SetCursor(inputState.Captured); CancelSceneActions(); }
            if (Time.realtimeSinceStartupAsDouble >= feedbackUntil) LastFeedback = "";
            if (gateway == null || !gateway.Running || !movement.Ready) { StopSceneSimulation(); return; }
            if (ragdoll.Faulted) { StopSceneSimulation(); enabled = false; return; }
            lookTarget = null;
            float dt = Mathf.Min(Time.deltaTime, 0.1f);
            if (station) { TickStation(); return; }
            if (Down) { TickDowned(); TickRecovery(); return; }
            if (recoveryAttempt != 0)
            {
                float phase = PhaseDelta();
                ApplyPhaseSample(Mathf.Min(phase, recoveryRemaining)); recoveryRemaining -= phase;
                if (recoveryRemaining <= 0)
                {
                    if (!gateway.CompleteRecovery(this, recoveryAttempt)) KnockDown(Vector3.zero);
                    recoveryAttempt = 0;
                }
                return;
            }
            reactionRemaining = Mathf.Max(0, reactionRemaining - dt);
            bool input = localInput && inputState.Captured && !captureChanged && gateway.CanAct(this) && reactionRemaining == 0;
            Vector2 axes = input ? new Vector2(Key(KeyCode.D) - Key(KeyCode.A), Key(KeyCode.W) - Key(KeyCode.S)) : Vector2.zero;
            bool sprint = input && Input.GetKey(KeyCode.LeftShift), walk = input && Input.GetKey(KeyCode.LeftAlt);
            if (input)
            {
                float yaw = Input.GetAxisRaw("Mouse X") * sensitivity;
                if (Input.GetKey(KeyCode.C)) { gateway.RotateHeld(this, yaw); yaw = 0; }
                if (acting || Bonking) yaw = 0;
                transform.Rotate(0, yaw, 0); yawRate = dt > 0 ? Mathf.Clamp(yaw / dt, -1000, 1000) : 0;
                pitch = Mathf.Clamp(pitch - Input.GetAxisRaw("Mouse Y") * sensitivity, -80, 80);
                eye.localRotation = Quaternion.Euler(pitch, 0, 0);
                SetCrouch(Input.GetKey(KeyCode.LeftControl));
                if (Input.GetKeyDown(KeyCode.Space)) jumpBuffer = 0.15f;
                lookTarget = LookTarget();
                ReadActions();
            }
            else yawRate = 0;
            TickAction(dt);
            if (station || Down || recoveryAttempt != 0 || !capsule.enabled || !gateway.Running) return;
            groundGrace = Grounded ? 0.10f : Mathf.Max(0, groundGrace - dt);
            jumpBuffer = Mathf.Max(0, jumpBuffer - dt);
            if (jumpBuffer > 0 && groundGrace > 0 && !acting && !Bonking && !crouched && pose == MovementPose.Free && jumpTime < 0)
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
            if (Bonking) desired *= .35f;
            if (crouched || (input && Input.GetKey(KeyCode.B))) desired *= 0.5f;
            planar = Vector3.MoveTowards(planar, desired, acceleration * (Grounded ? 1 : 0.2f) * dt);
            if (Grounded && vertical < 0) vertical = -2;
            vertical -= gravity * dt;
            Vector3 beforePosition = transform.position;
            CollisionFlags flags;
            movingCapsule = true;
            try { flags = capsule.Move((planar + Vector3.up * vertical) * dt); }
            finally { movingCapsule = false; }
            if ((flags & CollisionFlags.Above) != 0 && vertical > 0) vertical = 0;
            velocity = dt > 0 ? (transform.position - beforePosition) / dt : Vector3.zero;
            if (pendingKnockdown) { var force = pendingImpulse; var point = pendingPoint; pendingKnockdown = false; pendingImpulse = Vector3.zero; pendingPoint = null; KnockDown(force, point); return; }
            if (Down || !capsule.enabled || !gateway.Running) return;
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
            if (!enabled || !gateway || !gateway.Running) return;
            if (Down) { TrackDownedCamera(); return; }
            ragdoll.BlendToAnimation(Time.deltaTime);
            if (crouched && crouchPose != null) crouchPose.Apply(standingHeight - crouchHeight);
            if (head != null) eye.position = head.position + transform.TransformVector(headOffset);
            if (leftHand != null && rightHand != null) grip.position = (leftHand.position + rightHand.position) * 0.5f;
            ApplyBonkPose();
            ragdoll.SampleAnimatedPose(Time.deltaTime);
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
            if (!SceneTargeting.Raycast(this, gateway.Held(this), eye.forward, 2.5f, interactionMask, lookHits, out var hit)) return null;
            return hit.collider.GetComponentInParent<SceneTarget>();
        }
        private void ReadActions()
        {
            if (heldAction && inputState.HoldReleased(Input.GetKey(KeyCode.E), Input.GetKey(KeyCode.R), Input.GetMouseButton(0))) CancelSceneActions();
            if (Input.GetKeyDown(KeyCode.G)) StartAction(gateway.Held(this), SceneOperation.Release);
            if (Input.GetKeyDown(KeyCode.V)) StartAction(gateway.Held(this), SceneOperation.Place);
            if (Input.GetKeyDown(KeyCode.T)) StartAction(gateway.Held(this), Input.GetKey(KeyCode.LeftAlt) ? SceneOperation.ThrowUnder : SceneOperation.ThrowOver);
            if (Input.GetKeyDown(KeyCode.F)) StartAction(lookTarget, SceneOperation.Grab);
            if (Input.GetKeyDown(KeyCode.E))
            {
                var target = lookTarget != null ? lookTarget : gateway.Held(this);
                bool alternate = Input.GetKey(KeyCode.LeftAlt);
                if (target != null) StartAction(target, alternate && target.Supports(SceneOperation.Connect) ? SceneOperation.Connect :
                    alternate && target.Supports(SceneOperation.Pull) ? SceneOperation.Pull : target.Operation, WorkerActionInput.Interact);
            }
            if (Input.GetKeyDown(KeyCode.P)) StartAction(null, SceneOperation.Point);
            if (Input.GetKeyDown(KeyCode.Tab)) ShowFeedback(gateway.Describe(lookTarget));
            if (Input.GetKeyDown(KeyCode.R)) StartAction(null, SceneOperation.Radio, WorkerActionInput.Radio);
            if (Input.GetMouseButtonDown(0) && gateway.Held(this) != null && BonkReady)
            { if (!gateway.BeginBonk(this, out var reason)) ShowFeedback(reason); }
        }

        public bool StartAction(SceneTarget target, SceneOperation value) => StartAction(target, value, WorkerActionInput.Script);

        private bool StartAction(SceneTarget target, SceneOperation value, WorkerActionInput source)
        {
            if (acting || Bonking || station || jumpTime >= 0 || !Grounded || !gateway.CanAct(this)) return false;
            if (target == null && value != SceneOperation.Point && value != SceneOperation.Radio) return false;
            if (target != null && (!target.Supports(value) || !gateway.CanUse(this, target))) return false;
            if (value == SceneOperation.Push || value == SceneOperation.Pull || value == SceneOperation.Drag)
            { bool ok = gateway.Execute(this, target, value, out var reason); ShowFeedback(ok ? "" : reason); return ok; }
            plan = WorkerActionPlan.For(value);
            movement.ApplySample(new MovementAnimationSample(0, 0, 0, true, pose), 0);
            if (!movement.TryPlayAction(plan.Clip, ++actionSequence)) return false;
            actionTarget = target; operation = value; acting = true; heldAction = plan.Repeat;
            inputState.BindHold(plan.Repeat ? source : WorkerActionInput.Script);
            float contactCue = plan.Cue;
            foreach (var timing in contactTimings) if (timing.operation == value) contactCue = timing.normalizedCue;
            cueClock.Begin(movement.Duration(plan.Clip), contactCue, plan.Repeat);
            return true;
        }

        private void TickAction(float dt)
        {
            if (!acting) return;
            bool requiresTarget = operation != SceneOperation.Point && operation != SceneOperation.Radio;
            if (!gateway.CanAct(this) || !Grounded || (requiresTarget && (actionTarget == null || !gateway.CanUse(this, actionTarget))))
            { CancelSceneActions(); return; }
            if (cueClock.Step(dt))
            {
                if (!gateway.Execute(this, actionTarget, operation, out var reason))
                { ShowFeedback(reason); CancelSceneActions(); return; }
                if (operation == SceneOperation.Point)
                {
                    Vector3 point = SceneTargeting.Raycast(this, gateway.Held(this), eye.forward, 30, interactionMask, lookHits, out var hit) ? hit.point : eye.position + eye.forward * 10;
                    pingEffect?.Invoke(point);
                }
            }
            if (cueClock.Complete) { acting = heldAction = false; actionTarget = null; inputState.ClearHold(); }
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
            RestoreBonkGrip();
            if (gateway != null) gateway.CancelBonk(this);
            if (movement != null && acting) movement.StopAction(actionSequence);
            if (movement != null && jumpTime >= 0) movement.CancelJump();
            inputState.ClearHold(); jumpBuffer = 0;
            acting = heldAction = false; actionTarget = null; jumpTime = -1;
            if (!gateway || !gateway.Running) { planar = velocity = Vector3.zero; station = false; recoveryAttempt = 0; }
        }

        private void OnApplicationFocus(bool value)
        { inputState.SetApplicationFocus(value); if (!value) CancelSceneActions(); if (localInput) SetCursor(inputState.Captured); }
        private void OnDisable() { StopSceneSimulation(); if (localInput) SetCursor(false); }
        private void ShowFeedback(string message)
        { LastFeedback = message; feedbackUntil = Time.realtimeSinceStartupAsDouble + 3.5; }
        private void OnGUI()
        {
            if (!localInput || !enabled) return;
            if (!inputState.Captured)
            { GUI.Label(new Rect(16, Screen.height - 48, Screen.width - 32, 32), "Click, Enter or Escape to resume."); return; }
            if (!string.IsNullOrEmpty(LastFeedback)) GUI.Label(new Rect(16, Screen.height - 56, Screen.width - 32, 40), LastFeedback);
            if (gateway == null || !gateway.Running) return;
            if (Down) { if (gateway.ConsciousDown(this)) GUI.Label(new Rect(16, Screen.height - 96, Screen.width - 32, 32), "WASD: Crawl   B: Brace   E: Grip/release handle   G: Release   H/P: Help beacon"); return; }
            if (station) return;
            var held = gateway.Held(this);
            if (held != null && !string.IsNullOrEmpty(held.PrimaryActionHint)) GUI.Label(new Rect(16, Screen.height - 124, Screen.width - 32, 28), held.PrimaryActionHint);
            GUI.Label(new Rect(Screen.width / 2f - 5, Screen.height / 2f - 10, 20, 20), "+");
            if (lookTarget != null && gateway.CanUse(this, lookTarget))
            {
                string prompt = lookTarget.name + "   E: " + ActionVerb(lookTarget.Operation) + "   Tab: Inspect";
                if (lookTarget.Supports(SceneOperation.Connect)) prompt += "   Alt+E: Connect";
                else if (lookTarget.Supports(SceneOperation.Pull)) prompt += "   Alt+E: Pull";
                if (lookTarget.Supports(SceneOperation.Grab)) prompt += "   F: Pick up / assist";
                GUI.Label(new Rect(16, Screen.height - 96, Screen.width - 32, 32), prompt);
            }
        }
        private static string ActionVerb(SceneOperation value)
        {
            switch (value)
            {
                case SceneOperation.Grab: return "Pick up";
                case SceneOperation.Push: return "Push";
                case SceneOperation.Pull: return "Pull";
                case SceneOperation.Drag: return "Drag";
                case SceneOperation.Button: return "Press";
                case SceneOperation.Lever: return "Pull lever";
                case SceneOperation.ValveTurn: return "Hold to turn valve";
                case SceneOperation.ValveHold: return "Hold valve";
                case SceneOperation.Open: return "Open";
                case SceneOperation.Insert: return "Insert container";
                case SceneOperation.Connect: return "Connect";
                case SceneOperation.Dig: return "Hold to dig";
                case SceneOperation.Suit: return "Put on suit";
                case SceneOperation.LockerExit: return "Leave locker";
                case SceneOperation.Reanimation: return "Recommission worker";
                case SceneOperation.Help: return "Help worker";
                default: return "Use";
            }
        }
        private void SetCursor(bool value) { Cursor.lockState = value ? CursorLockMode.Locked : CursorLockMode.None; Cursor.visible = !value; }
    }
}
