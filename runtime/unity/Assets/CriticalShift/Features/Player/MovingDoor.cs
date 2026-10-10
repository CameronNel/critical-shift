using System;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    [Serializable]
    public sealed class DoorLeaf
    {
        public Transform Root;
        public BoxCollider Shape;
        public Collider[] PhysicalShapes = Array.Empty<Collider>();
        public Vector3 ClosedPosition, OpenPosition;
        public Quaternion ClosedRotation, OpenRotation;
    }

    // Owns local physical motion only. The map's authored pivots and poses are explicit inputs.
    public sealed class MovingDoor : MonoBehaviour
    {
        [SerializeField] private DoorLeaf[] leaves = Array.Empty<DoorLeaf>();
        [SerializeField] private bool initiallyOpen;
        [SerializeField] private float seconds = 1.3f;
        private readonly Collider[] _hits = new Collider[32];
        private float _progress;
        private bool _requestedOpen, _captured;
        public bool Open => _progress >= 0.999f;
        public bool Closed => _progress <= 0.001f;
        public bool Blocked { get; private set; }
        public bool Matches(Collider shape)
        {
            foreach (var leaf in leaves)
            {
                if (leaf.Shape.enabled && leaf.Shape == shape) return true;
                foreach (var physical in leaf.PhysicalShapes) if (physical == shape) return true;
            }
            return false;
        }
        public void Configure(DoorLeaf[] bindings, bool open = false, float duration = 1.3f)
        { leaves = (DoorLeaf[])bindings.Clone(); initiallyOpen = open; seconds = duration; }
        public void Capture()
        {
            if (leaves.Length < 1 || leaves.Length > 2 || seconds < 0.3f || seconds > 5)
                throw new InvalidOperationException("Invalid authored door binding.");
            foreach (var leaf in leaves)
                if (leaf == null || leaf.Root == null || leaf.Shape == null || !leaf.Shape.transform.IsChildOf(leaf.Root))
                    throw new InvalidOperationException("Missing door leaf/pivot/collider.");
            _captured = true; ResetDoor();
        }
        public void SetOpen(bool open) { _requestedOpen = open; Blocked = false; }
        public void Toggle() { SetOpen(!_requestedOpen); }
        public void ResetDoor()
        {
            if (!_captured) return;
            _requestedOpen = initiallyOpen; _progress = initiallyOpen ? 1 : 0; Blocked = false; Apply(_progress);
        }
        public void Step(float delta)
        {
            if (!_captured || delta <= 0) return;
            float target = _requestedOpen ? 1 : 0;
            // Check intermediate poses, including a long frame; do not tunnel through a worker or carried item.
            float next = Mathf.MoveTowards(_progress, target, Mathf.Min(delta, 0.05f) / seconds);
            int steps = Mathf.Max(1, Mathf.CeilToInt(Mathf.Abs(next - _progress) * 240));
            float start = _progress;
            for (int step = 1; step <= steps; step++)
            {
                float proposed = Mathf.Lerp(start, next, step / (float)steps);
                Apply(proposed); Physics.SyncTransforms();
                if (Obstructed())
                {
                    Apply(_progress); Physics.SyncTransforms(); Blocked = true;
                    if (!_requestedOpen) _requestedOpen = true; // Reopen instead of crushing an occupant.
                    return;
                }
                _progress = proposed;
            }
            Blocked = false;
        }
        private void Apply(float progress)
        {
            foreach (var leaf in leaves)
            {
                leaf.Root.localPosition = Vector3.Lerp(leaf.ClosedPosition, leaf.OpenPosition, progress);
                leaf.Root.localRotation = Quaternion.Slerp(leaf.ClosedRotation, leaf.OpenRotation, progress);
            }
        }
        private bool Obstructed()
        {
            foreach (var leaf in leaves)
            {
                var scale = leaf.Shape.transform.lossyScale;
                var half = Vector3.Scale(leaf.Shape.size * 0.5f, new Vector3(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z)));
                int count = Physics.OverlapBoxNonAlloc(leaf.Shape.transform.TransformPoint(leaf.Shape.center), half,
                    _hits, leaf.Shape.transform.rotation, ~0, QueryTriggerInteraction.Ignore);
                if (count == _hits.Length) return true;
                for (int i = 0; i < count; i++)
                {
                    var hit = _hits[i];
                    bool ownLeaf = false;
                    foreach (var other in leaves) if (hit.transform.IsChildOf(other.Root)) { ownLeaf = true; break; }
                    if (ownLeaf || (hit.GetComponentInParent<FirstPersonWorker>() == null && hit.attachedRigidbody == null)) continue;
                    if (!(hit is CapsuleCollider) && !(hit is CharacterController) && !(hit is BoxCollider) && !(hit is SphereCollider) &&
                        !(hit is MeshCollider convex && convex.convex)) return true;
                    // Curved pod leaves need their actual mesh: a bounding box also covers the empty chamber interior.
                    if (leaf.PhysicalShapes.Length == 0)
                    { if (Penetrates(hit, leaf.Shape)) return true; }
                    else foreach (var physical in leaf.PhysicalShapes) if (Penetrates(hit, physical)) return true;
                }
            }
            return false;
        }
        private static bool Penetrates(Collider occupant, Collider leaf)
        {
            if (occupant is CharacterController)
            {
                // ComputePenetration accepts primitive colliders, rather than CharacterController itself.
                occupant = occupant.GetComponent<FirstPersonWorker>()?.DoorProbe;
                if (occupant == null) return true;
            }
            return Physics.ComputePenetration(occupant, occupant.transform.position, occupant.transform.rotation,
                leaf, leaf.transform.position, leaf.transform.rotation, out _, out var distance) && distance > 0.003f;
        }
    }
}
