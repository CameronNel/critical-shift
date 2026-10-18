using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    public enum DoorCollisionState { Open, Closed, Locked }
    public enum DoorCollisionApplyStatus { Applied, NoChange, Unavailable, WrongEpoch, UnknownDoor, StaleRevision, RevisionConflict }

    /// <summary>A supplied physical projection, not a door command or a logical state owner.</summary>
    public sealed class DoorCollisionProjection
    {
        public DoorCollisionProjection(Guid epoch, string doorId, long revision, DoorCollisionState state)
        {
            if (epoch == Guid.Empty || string.IsNullOrWhiteSpace(doorId) || revision < 0 ||
                (state != DoorCollisionState.Open && state != DoorCollisionState.Closed && state != DoorCollisionState.Locked))
                throw new ArgumentException("A door projection requires its world epoch, stable ID, nonnegative revision and known collision state.");
            Epoch = epoch; DoorId = doorId; Revision = revision; State = state;
        }
        public Guid Epoch { get; }
        public string DoorId { get; }
        public long Revision { get; }
        public DoorCollisionState State { get; }
    }

    /// <summary>Explicit scene references and their supplied initial projection; imported object names are not identity.</summary>
    public sealed class DoorCollisionBinding
    {
        public DoorCollisionBinding(DoorCollisionProjection initialProjection, Transform anchor, Collider blocker, Collider threshold)
        { InitialProjection = initialProjection; Anchor = anchor; Blocker = blocker; Threshold = threshold; }
        public DoorCollisionProjection InitialProjection { get; }
        public Transform Anchor { get; }
        public Collider Blocker { get; }
        public Collider Threshold { get; }
    }

    /// <summary>Applies supplied door projections to static contacts only. Owns no commands, evacuation rule or visual animation.</summary>
    [DisallowMultipleComponent]
    public sealed class CombinedMapDoorBindings : MonoBehaviour
    {
        private sealed class ShapeSignature
        {
            private readonly Vector3 center, size;
            private readonly float radius, height;
            private readonly int direction, vertexCount, subMeshCount;
            private readonly Mesh mesh;
            private readonly Bounds meshBounds;
            private readonly bool convex;
            internal ShapeSignature(Collider shape)
            {
                if (shape is BoxCollider box) { center = box.center; size = box.size; }
                else if (shape is SphereCollider sphere) { center = sphere.center; radius = sphere.radius; }
                else if (shape is CapsuleCollider capsule)
                { center = capsule.center; radius = capsule.radius; height = capsule.height; direction = capsule.direction; }
                else if (shape is MeshCollider contact)
                {
                    mesh = contact.sharedMesh; convex = contact.convex; meshBounds = mesh.bounds;
                    vertexCount = mesh.vertexCount; subMeshCount = mesh.subMeshCount;
                }
            }
            internal bool Matches(Collider shape)
            {
                if (shape is BoxCollider box) return center.Equals(box.center) && size.Equals(box.size);
                if (shape is SphereCollider sphere) return center.Equals(sphere.center) && radius == sphere.radius;
                if (shape is CapsuleCollider capsule) return center.Equals(capsule.center) && radius == capsule.radius &&
                    height == capsule.height && direction == capsule.direction;
                return shape is MeshCollider contact && mesh == contact.sharedMesh && convex == contact.convex &&
                    meshBounds.Equals(mesh.bounds) && vertexCount == mesh.vertexCount && subMeshCount == mesh.subMeshCount;
            }
        }
        private sealed class AppliedDoor
        {
            internal readonly DoorCollisionBinding Binding;
            internal DoorCollisionProjection Projection;
            private readonly Matrix4x4 anchorPose, blockerPose, thresholdPose;
            private readonly ShapeSignature blockerShape, thresholdShape;
            internal AppliedDoor(DoorCollisionBinding binding, CombinedMapDoorBindings owner)
            {
                Binding = binding; Projection = binding.InitialProjection;
                anchorPose = owner.RelativePose(binding.Anchor, Projection.DoorId);
                blockerPose = owner.RelativePose(binding.Blocker.transform, Projection.DoorId);
                thresholdPose = owner.RelativePose(binding.Threshold.transform, Projection.DoorId);
                blockerShape = new ShapeSignature(binding.Blocker); thresholdShape = new ShapeSignature(binding.Threshold);
            }
            internal bool Unchanged(CombinedMapDoorBindings owner) =>
                anchorPose.Equals(owner.RelativePose(Binding.Anchor, Projection.DoorId)) &&
                blockerPose.Equals(owner.RelativePose(Binding.Blocker.transform, Projection.DoorId)) &&
                thresholdPose.Equals(owner.RelativePose(Binding.Threshold.transform, Projection.DoorId)) &&
                blockerShape.Matches(Binding.Blocker) && thresholdShape.Matches(Binding.Threshold);
        }
        private Dictionary<string, AppliedDoor> doors;
        private AppliedDoor[] ordered;
        private readonly Collider[] closureContacts = new Collider[64];
        private Action<Exception> report;
        private bool initialized, ended;
        public Guid Epoch { get; private set; }
        public int BoundDoorCount => ordered == null ? 0 : ordered.Length;
        public bool IsBound => ordered != null && !ended;
        public bool FaultLatched { get; private set; }
        public string Fault { get; private set; } = "";

        public void Initialize(Guid worldEpoch, IReadOnlyList<DoorCollisionBinding> bindings, Action<Exception> onFailure = null)
        {
            if (initialized || ended || worldEpoch == Guid.Empty || !isActiveAndEnabled || bindings == null || bindings.Count < 1 || bindings.Count > 128)
                throw new ArgumentException("Bind one active door adapter to one world and between one and 128 doors.");
            var candidates = new AppliedDoor[bindings.Count];
            var lookup = new Dictionary<string, AppliedDoor>(StringComparer.Ordinal);
            var anchors = new HashSet<Transform>(); var contacts = new HashSet<Collider>();
            for (int i = 0; i < candidates.Length; i++)
            {
                var binding = bindings[i];
                if (binding == null || binding.InitialProjection == null || binding.InitialProjection.Epoch != worldEpoch)
                    throw new ArgumentException("Every door binding requires an initial projection for this world.");
                string id = binding.InitialProjection.DoorId;
                if (lookup.ContainsKey(id) || !anchors.Add(binding.Anchor) || !contacts.Add(binding.Blocker) || !contacts.Add(binding.Threshold))
                    throw new ArgumentException("Door IDs, anchors and contact references must be unique: " + id);
                ValidateReferences(binding, id);
                var candidate = new AppliedDoor(binding, this); candidates[i] = candidate; lookup.Add(id, candidate);
            }
            // No live references or contact changes exist until the complete batch has passed validation.
            ordered = candidates; doors = lookup; Epoch = worldEpoch; initialized = true;
            report = onFailure ?? (error => Debug.LogException(error, this));
            try
            {
                foreach (var door in ordered)
                {
                    door.Binding.Blocker.enabled = door.Projection.State != DoorCollisionState.Open;
                    door.Binding.Threshold.enabled = true;
                }
            }
            catch { Shutdown(); throw; }
        }

        public DoorCollisionApplyStatus Apply(DoorCollisionProjection projection) => ApplyBatch(new[] { projection });

        /// <summary>Conservative current-physics observation only; the caller still owns command admission and logical closing.</summary>
        public bool CanClose(string doorId)
        {
            if (!IsBound || string.IsNullOrWhiteSpace(doorId) || !doors.TryGetValue(doorId, out var door)) return false;
            if (!CheckBindings()) return false;
            try
            {
                // This is the active threshold's actual world bounds, never a JSON AABB or a temporarily enabled blocker.
                Bounds bounds = door.Binding.Threshold.bounds;
                if (!Finite(bounds.center) || !FinitePositive(bounds.extents.x) || !FinitePositive(bounds.extents.y) || !FinitePositive(bounds.extents.z))
                    throw new InvalidOperationException("A combined-map door lost its usable closure observation volume: " + doorId);
                int count = Physics.OverlapBoxNonAlloc(bounds.center, bounds.extents, closureContacts, Quaternion.identity,
                    Physics.AllLayers, QueryTriggerInteraction.Ignore);
                if (count == closureContacts.Length) return false;
                for (int i = 0; i < count; i++)
                {
                    var contact = closureContacts[i];
                    if (contact == null || !contact.enabled || !contact.gameObject.activeInHierarchy || contact.isTrigger ||
                        contact == door.Binding.Blocker || contact == door.Binding.Threshold) continue;
                    // Static frames and walls do not represent an occupant; disabled walking capsules and triggers do not either.
                    if (contact.attachedRigidbody != null || contact is CharacterController) return false;
                }
                return true;
            }
            catch (Exception error) { Fail(error); return false; }
            finally { Array.Clear(closureContacts, 0, closureContacts.Length); }
        }

        public DoorCollisionApplyStatus ApplyBatch(IReadOnlyList<DoorCollisionProjection> projections)
        {
            if (projections == null || projections.Count < 1 || projections.Count > 128)
                throw new ArgumentException("Supply between one and 128 explicit door projections.");
            var incoming = new DoorCollisionProjection[projections.Count]; var ids = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < incoming.Length; i++)
            {
                incoming[i] = projections[i];
                if (incoming[i] == null || !ids.Add(incoming[i].DoorId))
                    throw new ArgumentException("An update batch requires present projections with unique door IDs.");
            }
            if (!IsBound) return DoorCollisionApplyStatus.Unavailable;
            bool changed = false;
            foreach (var projection in incoming)
            {
                if (projection.Epoch != Epoch) return DoorCollisionApplyStatus.WrongEpoch;
                if (!doors.TryGetValue(projection.DoorId, out var door)) return DoorCollisionApplyStatus.UnknownDoor;
                if (projection.Revision < door.Projection.Revision) return DoorCollisionApplyStatus.StaleRevision;
                if (projection.Revision == door.Projection.Revision && projection.State != door.Projection.State)
                    return DoorCollisionApplyStatus.RevisionConflict;
                changed |= projection.Revision > door.Projection.Revision;
            }
            if (!CheckBindings()) return DoorCollisionApplyStatus.Unavailable;
            if (!changed) return DoorCollisionApplyStatus.NoChange;
            try
            {
                foreach (var projection in incoming)
                {
                    var door = doors[projection.DoorId];
                    if (projection.Revision == door.Projection.Revision) continue;
                    door.Binding.Blocker.enabled = projection.State != DoorCollisionState.Open;
                    door.Projection = projection; // Retained only to fence duplicate/stale physical deliveries.
                }
                return DoorCollisionApplyStatus.Applied;
            }
            catch (Exception error) { Fail(error); return DoorCollisionApplyStatus.Unavailable; }
        }

        public void Sample() { if (IsBound) CheckBindings(); }
        private void FixedUpdate() => Sample();
        private bool CheckBindings()
        {
            try
            {
                foreach (var door in ordered)
                {
                    ValidateReferences(door.Binding, door.Projection.DoorId);
                    if (!door.Unchanged(this))
                        throw new InvalidOperationException("A combined-map door's static geometry or relative pose changed: " + door.Projection.DoorId);
                    if (!door.Binding.Threshold.enabled || door.Binding.Blocker.enabled != (door.Projection.State != DoorCollisionState.Open))
                        throw new InvalidOperationException("A combined-map door lost its applied contact state: " + door.Projection.DoorId);
                }
                return true;
            }
            catch (Exception error) { Fail(error); return false; }
        }

        private void ValidateReferences(DoorCollisionBinding binding, string id)
        {
            if (!gameObject.activeInHierarchy || !Finite(transform.position) || !Finite(transform.rotation) || !Nonsingular(transform.lossyScale) ||
                !Descendant(binding.Anchor) || binding.Anchor.GetComponentInParent<Rigidbody>() != null ||
                binding.Anchor.GetComponentsInChildren<Rigidbody>(true).Length != 0 || binding.Blocker == null || binding.Threshold == null ||
                !Descendant(binding.Blocker.transform) || !Descendant(binding.Threshold.transform) ||
                binding.Blocker.isTrigger || !binding.Threshold.isTrigger || binding.Blocker.attachedRigidbody != null || binding.Threshold.attachedRigidbody != null)
                throw new InvalidOperationException("A combined-map door requires active owned anchors, a static solid blocker and a static trigger: " + id);
            ValidateShape(binding.Blocker, id); ValidateShape(binding.Threshold, id);
        }
        private bool Descendant(Transform item) => item != null && item != transform && item.IsChildOf(transform) && item.gameObject.activeInHierarchy;
        private Matrix4x4 RelativePose(Transform item, string id)
        {
            Matrix4x4 relative = Matrix4x4.identity;
            // Compose only local transforms below this owner. Its world translation/rotation cannot introduce comparison rounding or drift.
            for (var node = item; node != transform; node = node.parent)
            {
                if (node == null || !Finite(node.localPosition) || !Finite(node.localRotation) || !Nonsingular(node.localScale))
                    throw new InvalidOperationException("A combined-map door requires finite nonsingular relative transforms: " + id);
                relative = Matrix4x4.TRS(node.localPosition, node.localRotation, node.localScale) * relative;
            }
            for (int i = 0; i < 16; i++)
                if (float.IsNaN(relative[i]) || float.IsInfinity(relative[i]))
                    throw new InvalidOperationException("A combined-map door relative transform exceeded its finite range: " + id);
            float determinant = relative.determinant;
            if (determinant == 0 || float.IsNaN(determinant) || float.IsInfinity(determinant))
                throw new InvalidOperationException("A combined-map door relative transform became singular: " + id);
            return relative;
        }
        private static void ValidateShape(Collider shape, string id)
        {
            bool valid = shape is BoxCollider box ? Finite(box.center) && FinitePositive(box.size.x) && FinitePositive(box.size.y) && FinitePositive(box.size.z) :
                shape is SphereCollider sphere ? Finite(sphere.center) && FinitePositive(sphere.radius) :
                shape is CapsuleCollider capsule ? Finite(capsule.center) && FinitePositive(capsule.radius) && FinitePositive(capsule.height) :
                shape is MeshCollider mesh && mesh.sharedMesh != null && mesh.sharedMesh.vertexCount > 0 &&
                    Finite(mesh.sharedMesh.bounds.center) && Finite(mesh.sharedMesh.bounds.size) && (!mesh.isTrigger || mesh.convex);
            if (!valid) throw new InvalidOperationException("A combined-map door requires a usable box, sphere, capsule or mesh contact shape: " + id);
        }
        private static bool FinitePositive(float value) => value > 0 && !float.IsNaN(value) && !float.IsInfinity(value);
        private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsInfinity(value.x) &&
            !float.IsNaN(value.y) && !float.IsInfinity(value.y) && !float.IsNaN(value.z) && !float.IsInfinity(value.z);
        private static bool Finite(Quaternion value) => !float.IsNaN(value.x) && !float.IsInfinity(value.x) &&
            !float.IsNaN(value.y) && !float.IsInfinity(value.y) && !float.IsNaN(value.z) && !float.IsInfinity(value.z) &&
            !float.IsNaN(value.w) && !float.IsInfinity(value.w);
        private static bool Nonsingular(Vector3 value) => Finite(value) && value.x != 0 && value.y != 0 && value.z != 0;

        private void Fail(Exception error)
        {
            if (!IsBound) return;
            var callback = report; FaultLatched = true; Fault = error.Message;
            Shutdown(); enabled = false; callback(error);
        }
        public void Shutdown()
        {
            ended = true;
            if (ordered != null)
                foreach (var door in ordered)
                {
                    if (door.Binding.Blocker != null) door.Binding.Blocker.enabled = false;
                    if (door.Binding.Threshold != null) door.Binding.Threshold.enabled = false;
                }
            ordered = null; doors = null; Epoch = Guid.Empty; report = null;
            Array.Clear(closureContacts, 0, closureContacts.Length);
        }
        private void OnDisable() { if (IsBound) Fail(new InvalidOperationException("The live combined-map door adapter was disabled.")); }
        private void OnDestroy() => Shutdown();
    }
}
