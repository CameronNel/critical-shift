using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class FirstPersonWorker : MonoBehaviour
    {
        [SerializeField] private string identity = "";
        [SerializeField] private string equipmentSlot = "";
        [SerializeField] private Camera eye;
        [SerializeField] private Transform carryAnchor;
        [SerializeField] private Transform equipmentAnchor;
        [SerializeField] private bool localInput = true;
        [SerializeField, Range(1, 8)] private float walkSpeed = 4.5f;
        [SerializeField, Range(0.1f, 3)] private float mouseSensitivity = 1.5f;
        [SerializeField] private float standingHeight = 1.8f;
        [SerializeField] private float standingEye = 1.6f;
        [SerializeField] private float seatedEye = 0.75f;
        private CharacterController _capsule;
        private PlayerWorldBridge _host;
        private Vector3 _spawn, _standing, _velocity;
        private Quaternion _spawnRotation, _standingRotation;
        private float _pitch;
        private bool _captured, _seated;
        private InteractionTarget _seat;
        private CapsuleCollider _doorProbe;
        private readonly Collider[] _clearance = new Collider[32];
        public Guid Id => Guid.Parse(identity);
        public Guid EquipmentSlot => Guid.Parse(equipmentSlot);
        public Camera Eye => eye;
        public Transform CarryAnchor => carryAnchor;
        public Transform EquipmentAnchor => equipmentAnchor;
        public bool LocalInput => localInput;
        public bool Grounded => _capsule != null && _capsule.isGrounded;
        public Vector3 Velocity => _capsule != null && _capsule.enabled ? _capsule.velocity : Vector3.zero;
        public bool Crouched => _capsule != null && _capsule.height < standingHeight - 0.01f;
        public CapsuleCollider DoorProbe
        {
            get
            {
                if (_doorProbe == null || _capsule == null) return null;
                _doorProbe.center = _capsule.center; _doorProbe.height = _capsule.height; _doorProbe.radius = _capsule.radius;
                return _doorProbe;
            }
        }
        public void ConfigureCharacter(float height, float eyeHeight, float speed)
        { standingHeight = height; standingEye = eyeHeight; walkSpeed = speed; }
        public Vector3 DropPoint => eye.transform.position + eye.transform.forward * 1.0f - Vector3.up * 0.25f;

        public void Configure(Guid id, Guid slot, Camera camera, Transform carry, Transform equipment, bool readsInput = true)
        { identity = id.ToString(); equipmentSlot = slot.ToString(); eye = camera; carryAnchor = carry; equipmentAnchor = equipment; localInput = readsInput; }
        public void Bind(PlayerWorldBridge host)
        {
            if (!Guid.TryParse(identity, out var id) || id == Guid.Empty ||
                !Guid.TryParse(equipmentSlot, out var slot) || slot == Guid.Empty ||
                eye == null || carryAnchor == null || equipmentAnchor == null ||
                !eye.transform.IsChildOf(transform) || !carryAnchor.IsChildOf(transform) || !equipmentAnchor.IsChildOf(transform))
                throw new InvalidOperationException("Invalid explicit worker binding: " + name);
            _host = host; _capsule = GetComponent<CharacterController>();
            _capsule.radius = 0.3f; _capsule.height = standingHeight; _capsule.center = Vector3.up * standingHeight * 0.5f;
            _capsule.stepOffset = 0.3f; _capsule.slopeLimit = 45; _capsule.skinWidth = 0.03f;
            if (_doorProbe == null)
            {
                var probe = new GameObject("Door clearance probe"); probe.transform.SetParent(transform, false);
                _doorProbe = probe.AddComponent<CapsuleCollider>(); _doorProbe.isTrigger = true; _doorProbe.enabled = false;
            }
            if (!_captured) { _captured = true; _spawn = transform.position; _spawnRotation = transform.rotation; }
            Restore();
        }
        public void Restore()
        {
            if (!_captured) return;
            if (_capsule == null || eye == null)
            { transform.SetPositionAndRotation(_spawn, _spawnRotation); _velocity = Vector3.zero; return; }
            _capsule.enabled = false; transform.SetPositionAndRotation(_spawn, _spawnRotation);
            _capsule.height = standingHeight; _capsule.center = Vector3.up * standingHeight * 0.5f; _capsule.enabled = true;
            _velocity = Vector3.zero; _pitch = 0; _seated = false; _seat = null;
            eye.transform.localPosition = Vector3.up * standingEye; eye.transform.localRotation = Quaternion.identity;
            GetComponent<WorkerAnimation>()?.ResetProjection();
        }
        public bool CanStandAt(Vector3 position)
        {
            return CapsuleClear(position + Vector3.up * 0.35f,
                position + Vector3.up * (standingHeight - 0.35f), 0.29f);
        }
        public bool CanSitAt(Vector3 position)
        {
            // Clearance for the short seated rig, above the seat surface. A standing capsule
            // overlaps an ordinary backrest even when the seated body fits comfortably.
            return CapsuleClear(position + Vector3.up * 0.23f, position + Vector3.up * 0.85f, 0.2f);
        }
        private bool CapsuleClear(Vector3 bottom, Vector3 top, float radius)
        {
            int count = Physics.OverlapCapsuleNonAlloc(bottom, top, radius, _clearance, ~0, QueryTriggerInteraction.Ignore);
            if (count == _clearance.Length) return false;
            for (int i = 0; i < count; i++)
                if (!_clearance[i].transform.IsChildOf(transform)) return false;
            return true;
        }
        public bool TryExit(InteractionTarget seat, out Vector3 point, out Quaternion rotation)
        {
            point = seat.Exit.position; rotation = seat.Exit.rotation;
            if (CanStandAt(point)) return true;
            point = _standing; rotation = _standingRotation;
            return _seated && CanStandAt(point);
        }
        public void ProjectPosture(WorkerView worker, InteractionTarget seat)
        {
            if (worker.Pose == WorkerPose.Seated)
            {
                if (seat == null) throw new InvalidOperationException("Seated worker has no physical seat.");
                if (!_seated)
                {
                    _standing = transform.position; _standingRotation = transform.rotation;
                    transform.rotation = seat.Attachment.rotation;
                }
                _capsule.enabled = false; transform.position = seat.Attachment.position;
                eye.transform.localPosition = Vector3.up * seatedEye; _velocity = Vector3.zero; _seated = true; _seat = seat;
            }
            else if (_seated)
            {
                if (!TryExit(_seat, out var point, out var rotation))
                    throw new InvalidOperationException("Neither the seat exit nor the last standing position is clear.");
                transform.SetPositionAndRotation(point, rotation); _capsule.enabled = true;
                eye.transform.localPosition = Vector3.up * standingEye; _seated = false; _seat = null;
            }
        }
        public void Step(PlayerInputFrame input, float deltaSeconds)
        {
            if (!isActiveAndEnabled) return;
            var worker = _host.Worker(Id);
            if (worker == null || _host.View.Phase != WorldPhase.Running || worker.Awareness != WorkerAwareness.Alert) return;
            if (!Finite(deltaSeconds) || deltaSeconds <= 0 || !Finite(input.Move.x) || !Finite(input.Move.y) ||
                !Finite(input.Look.x) || !Finite(input.Look.y)) throw new ArgumentException("Non-finite player input.");
            float dt = Mathf.Min(deltaSeconds, 0.05f);
            transform.Rotate(Vector3.up, input.Look.x * mouseSensitivity);
            _pitch = Mathf.Clamp(_pitch - input.Look.y * mouseSensitivity, -80, 80);
            eye.transform.localRotation = Quaternion.Euler(_pitch, 0, 0);
            if (worker.Pose != WorkerPose.Upright || _host.Busy(Id)) { _velocity = Vector3.zero; return; }
            float height = input.Crouch ? 1.15f : standingHeight;
            if (height > _capsule.height && !CanStandAt(transform.position)) height = _capsule.height;
            _capsule.height = height; _capsule.center = Vector3.up * height * 0.5f;
            eye.transform.localPosition = Vector3.up * (height < standingHeight ? height - 0.2f : standingEye);
            float speed = walkSpeed * (height < standingHeight ? 0.55f : input.Sprint ? 1.7f : 1);
            if (_host.Held(Id) != null) speed *= 0.7f;
            if (worker.Suit != WorkerSuit.None) speed *= 0.8f;
            var move = Vector2.ClampMagnitude(input.Move, 1);
            Vector3 desired = (transform.right * move.x + transform.forward * move.y) * speed;
            float acceleration = _capsule.isGrounded ? 32 : 9;
            var horizontal = Vector3.MoveTowards(new Vector3(_velocity.x, 0, _velocity.z), desired, acceleration * dt);
            _velocity.x = horizontal.x; _velocity.z = horizontal.z;
            if (_capsule.isGrounded && _velocity.y < 0) _velocity.y = -2;
            if (_capsule.isGrounded && input.Jump && height >= standingHeight) _velocity.y = Mathf.Sqrt(2 * 18 * 0.6f);
            _velocity.y -= 18 * dt;
            var collision = _capsule.Move(_velocity * dt);
            if ((collision & CollisionFlags.Above) != 0 && _velocity.y > 0) _velocity.y = 0;
        }
        public void ReadInput()
        {
            if (!isActiveAndEnabled || !localInput || !UnityEngine.Application.isFocused || _host == null) return;
            if (Input.GetKeyDown(KeyCode.F5)) { _host.Begin(); return; }
            if (Input.GetKeyDown(KeyCode.Escape)) { _host.TogglePause(); return; }
            if (_host.View == null || _host.View.Phase != WorldPhase.Running) return;
            Step(new PlayerInputFrame(new Vector2((Input.GetKey(KeyCode.D) ? 1 : 0) - (Input.GetKey(KeyCode.A) ? 1 : 0),
                (Input.GetKey(KeyCode.W) ? 1 : 0) - (Input.GetKey(KeyCode.S) ? 1 : 0)),
                new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y")), Input.GetKeyDown(KeyCode.Space),
                Input.GetKey(KeyCode.LeftControl), Input.GetKey(KeyCode.LeftShift)), Time.unscaledDeltaTime);
            var held = _host.Held(Id); var equipment = _host.Equipment(Id);
            if (Input.GetKeyDown(KeyCode.E))
            {
                if (_host.TryUse(this)) return;
                if (_host.Worker(Id).Pose == WorkerPose.Seated) _host.Act(this, PlayerAction.Stand, _host.Target(held.EntityId));
                else
                {
                    var target = _host.Aim(this);
                    if (target != null)
                    {
                        var action = target.Kind == PlayerTargetKind.Seat ? PlayerAction.Sit :
                            target.Kind == PlayerTargetKind.Placement ? (held == null ? PlayerAction.Take : PlayerAction.Place) :
                            target.Station ? PlayerAction.PrepareEquipment : PlayerAction.PickUp;
                        _host.Act(this, action, target);
                    }
                }
            }
            else if (Input.GetKeyDown(KeyCode.Q) && held != null) _host.Act(this, PlayerAction.Drop, _host.Target(held.EntityId));
            else if (Input.GetKeyDown(KeyCode.R) && held != null) _host.Act(this, PlayerAction.Equip, _host.Target(held.EntityId));
            else if (Input.GetKeyDown(KeyCode.U) && equipment != null) _host.Act(this, PlayerAction.Unequip, _host.Target(equipment.EntityId));
        }
        private void OnGUI()
        {
            if (!localInput || _host == null) return;
            GUI.Box(new Rect(12, 12, 560, 125), "Critical Shift — shift preparation");
            var view = _host.View; var worker = _host.Worker(Id);
            GUI.Label(new Rect(25, 40, 540, 25), view == null ? "Room unavailable — press F5 after fixing its setup." :
                $"{view.Phase}   Shift: {TimeSpan.FromMilliseconds(view.RemainingMilliseconds):mm\\:ss}   Gear: {worker?.Suit}");
            GUI.Label(new Rect(25, 65, 540, 25), "WASD move · Mouse look · Space jump · Ctrl crouch · Shift sprint");
            GUI.Label(new Rect(25, 90, 540, 25), "E use/stand · Q drop · R wear · U remove · Esc pause · F5 restart");
            GUI.Label(new Rect(25, 112, 540, 25), _host.Feedback);
            if (view == null || view.Phase != WorldPhase.Running) return;
            GUI.Label(new Rect(Screen.width / 2f - 5, Screen.height / 2f - 12, 30, 30), "+");
            var target = _host.Aim(this);
            string roomPrompt = _host.UsePrompt(this);
            if (worker?.Pose == WorkerPose.Seated) GUI.Label(new Rect(Screen.width / 2f - 100, Screen.height / 2f + 25, 300, 30), "E — stand up");
            else if (!string.IsNullOrEmpty(roomPrompt)) GUI.Label(new Rect(Screen.width / 2f - 160, Screen.height / 2f + 25, 400, 30), roomPrompt);
            else if (target != null) GUI.Label(new Rect(Screen.width / 2f - 100, Screen.height / 2f + 25, 300, 30), "E — " + target.Label);
        }
        private static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);
    }
}
