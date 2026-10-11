using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    public sealed class InteractionTarget : MonoBehaviour
    {
        [SerializeField] private string identity = "";
        [SerializeField] private string slotIdentity = "";
        [SerializeField] private PlayerTargetKind kind;
        [SerializeField] private string displayName = "Object";
        [SerializeField] private Collider shape;
        [SerializeField] private Rigidbody body;
        [SerializeField] private Transform attachment;
        [SerializeField] private Transform exit;
        [SerializeField] private Transform stationVisual;
        [SerializeField] private Transform stationPose;
        [SerializeField] private int preparationMilliseconds;
        private Vector3 _spawn;
        private Quaternion _rotation;
        private Transform _parent;
        private bool _captured, _kinematic, _gravity, _collidable, _attached;
        public Guid Id => Guid.Parse(identity);
        public Guid Slot => Guid.Parse(slotIdentity);
        public PlayerTargetKind Kind => kind;
        public string Label => displayName;
        public Collider Shape => shape;
        public Transform Attachment => attachment;
        public Transform Exit => exit;
        public bool Portable => kind == PlayerTargetKind.Carryable || kind == PlayerTargetKind.ProtectiveEquipment;
        public float Radius { get; private set; }
        public int PreparationMilliseconds => preparationMilliseconds;
        public bool Station => preparationMilliseconds > 0;
        public Transform StationPose => stationPose;
        public void ConfigureStation(Transform hangingSuit, Transform standingPose, int delayMilliseconds = 15000)
        { stationVisual = hangingSuit; stationPose = standingPose; preparationMilliseconds = delayMilliseconds; }
        public void ProjectStation(bool available)
        { if (stationVisual == null) throw new InvalidOperationException("Missing station suit projection."); stationVisual.gameObject.SetActive(available); }

        public void Configure(Guid id, PlayerTargetKind type, string label, Collider collider,
            Rigidbody rigidbody = null, Transform anchor = null, Transform exitPose = null, Guid slot = default)
        {
            identity = id.ToString(); kind = type; displayName = label; shape = collider;
            body = rigidbody; attachment = anchor; exit = exitPose; slotIdentity = slot.ToString();
        }
        public void Capture()
        {
            if ((Station && (stationVisual == null || stationPose == null || !stationPose.gameObject.activeInHierarchy ||
                    kind != PlayerTargetKind.ProtectiveEquipment ||
                    preparationMilliseconds < 15000 || preparationMilliseconds > 30000 || stationVisual.IsChildOf(transform))) ||
                !Guid.TryParse(identity, out var id) || id == Guid.Empty || shape == null ||
                !shape.transform.IsChildOf(transform) || !isActiveAndEnabled || !shape.enabled ||
                (Portable && (body == null || body.transform != transform || GetComponentsInChildren<Collider>(true).Length != 1)) ||
                ((kind == PlayerTargetKind.Seat || kind == PlayerTargetKind.Placement) && attachment == null) ||
                (kind == PlayerTargetKind.Seat && exit == null) ||
                (kind == PlayerTargetKind.Placement && (!Guid.TryParse(slotIdentity, out var slot) || slot == Guid.Empty)))
                throw new InvalidOperationException("Invalid explicit player target binding: " + name);
            Radius = shape.bounds.extents.magnitude;
            if (Portable && (Radius < 0.01f || Radius > 0.6f))
                throw new InvalidOperationException("The local carry fixture supports objects with radius <= 0.6m.");
            if (_captured) return;
            _captured = true; _spawn = transform.position; _rotation = transform.rotation; _parent = transform.parent;
            _collidable = shape.enabled;
            if (body != null) { _kinematic = body.isKinematic; _gravity = body.useGravity; }
        }
        // Physical projection only. This component never stores holder, lease, slot or worker state.
        public void Project(Transform destination)
        {
            if (!Portable) return;
            if (destination != null)
            {
                body.isKinematic = true; body.useGravity = false; shape.enabled = false;
                transform.SetParent(destination, false); transform.localPosition = Vector3.zero;
                transform.localRotation = Quaternion.identity; _attached = true;
            }
            else if (_attached)
            {
                transform.SetParent(_parent, true);
                if (shape != null) shape.enabled = _collidable;
                if (body != null)
                {
                    body.isKinematic = _kinematic; body.useGravity = _gravity;
                    if (!body.isKinematic) { body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; }
                }
                _attached = false;
            }
        }
        public void Restore()
        {
            if (!_captured) return;
            if (Station) ProjectStation(true);
            Project(null); transform.SetParent(_parent, true); transform.SetPositionAndRotation(_spawn, _rotation);
            if (shape != null) shape.enabled = _collidable;
            if (body != null)
            {
                body.isKinematic = _kinematic; body.useGravity = _gravity;
                if (!body.isKinematic) { body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; }
            }
        }
    }
}
