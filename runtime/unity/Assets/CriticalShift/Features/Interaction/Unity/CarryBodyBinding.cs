using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Physical attachment state for a current logical claim; never a second holder authority.</summary>
    internal sealed class CarryBodyBinding
    {
        internal readonly Guid Id;
        internal readonly Rigidbody Body;
        private readonly bool originalKinematic, originalGravity;
        private readonly CollisionDetectionMode originalCollisionMode;
        private readonly RigidbodyInterpolation originalInterpolation;
        private readonly float massPerUnit;
        private readonly Vector3 boundScale;
        private readonly Collider[] shapes;
        private readonly Collider[] overlaps = new Collider[32];
        private bool slotted;
        private Guid appliedSlot;
        private long generation;
        private float obstructionSeconds;

        internal bool Available
        {
            get
            {
                if (Body == null || !Body.gameObject.activeInHierarchy || !Body.detectCollisions || Body.isKinematic != slotted) return false;
                Vector3 scale = Body.transform.lossyScale;
                if (!Finite(scale) || (scale - boundScale).sqrMagnitude > 0.000001f) return false;
                foreach (var shape in shapes)
                    if (shape == null || !shape.enabled || !shape.gameObject.activeInHierarchy || shape.isTrigger || shape.attachedRigidbody != Body)
                        return false;
                return true;
            }
        }

        internal CarryBodyBinding(Guid id, Rigidbody body, float physicalMassPerUnit = 0)
        {
            if (id == Guid.Empty || body == null) throw new ArgumentException("Body identity and Rigidbody are required.");
            if (body.isKinematic || !body.detectCollisions) throw new ArgumentException("Portable fixture bodies must begin dynamic with contacts enabled.");
            if (physicalMassPerUnit < 0 || float.IsNaN(physicalMassPerUnit) || float.IsInfinity(physicalMassPerUnit))
                throw new ArgumentOutOfRangeException(nameof(physicalMassPerUnit));
            Id = id; Body = body;
            massPerUnit = physicalMassPerUnit;
            originalKinematic = body.isKinematic; originalGravity = body.useGravity;
            originalCollisionMode = body.collisionDetectionMode; originalInterpolation = body.interpolation;
            boundScale = body.transform.lossyScale;
            if (!Finite(boundScale) || boundScale.x <= 0 || boundScale.y <= 0 || boundScale.z <= 0)
                throw new ArgumentException("Portable fixture scale must be finite and positive.");
            shapes = body.GetComponentsInChildren<Collider>();
            if (shapes.Length == 0) throw new ArgumentException("A portable body needs a collider.");
            foreach (var collider in shapes)
            {
                if (!collider.enabled || collider.isTrigger || collider.attachedRigidbody != body)
                    throw new ArgumentException("Portable fixture colliders must be solid and belong to this body.");
            }
            ReadPlacementBounds();
        }

        private Bounds ReadPlacementBounds()
        {
            Quaternion neutral = Quaternion.Inverse(Body.transform.rotation);
            Vector3 origin = Body.transform.position;
            Bounds bounds = default;
            bool first = true;
            foreach (var shape in shapes)
            {
                Bounds geometry;
                if (shape is BoxCollider box) geometry = new Bounds(box.center, box.size);
                else if (shape is MeshCollider mesh && mesh.sharedMesh != null) geometry = mesh.sharedMesh.bounds;
                else if (shape is SphereCollider || shape is CapsuleCollider)
                {
                    Vector3 scale = shape.transform.lossyScale;
                    scale = new Vector3(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z));
                    Vector3 center, extents;
                    if (shape is SphereCollider ball)
                    {
                        center = ball.center;
                        extents = Vector3.one * (ball.radius * Mathf.Max(scale.x, Mathf.Max(scale.y, scale.z)));
                    }
                    else
                    {
                        var capsule = (CapsuleCollider)shape;
                        center = capsule.center;
                        int axis = capsule.direction;
                        float radius = capsule.radius * Mathf.Max(scale[(axis + 1) % 3], scale[(axis + 2) % 3]);
                        float halfSegment = Mathf.Max(0, capsule.height * scale[axis] * 0.5f - radius);
                        Vector3 direction = neutral * shape.transform.TransformDirection(axis == 0 ? Vector3.right : axis == 1 ? Vector3.up : Vector3.forward);
                        extents = new Vector3(Mathf.Abs(direction.x), Mathf.Abs(direction.y), Mathf.Abs(direction.z)) * halfSegment + Vector3.one * radius;
                    }
                    geometry = new Bounds(neutral * (shape.transform.TransformPoint(center) - origin), extents * 2);
                    if (first) { bounds = geometry; first = false; } else bounds.Encapsulate(geometry);
                    continue;
                }
                else throw new InvalidOperationException("Portable placement requires box, sphere, capsule or mesh geometry.");

                // Transform the shape's own geometry, not its current world AABB: that
                // AABB already expands with rotation and cannot be unrotated afterwards.
                for (int corner = 0; corner < 8; corner++)
                {
                    Vector3 offset = Vector3.Scale(geometry.extents,
                        new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1));
                    Vector3 point = neutral * (shape.transform.TransformPoint(geometry.center + offset) - origin);
                    if (first) { bounds = new Bounds(point, Vector3.zero); first = false; } else bounds.Encapsulate(point);
                }
            }
            if (!Finite(bounds.center) || !Finite(bounds.size) || bounds.size.x <= 0 || bounds.size.y <= 0 || bounds.size.z <= 0)
                throw new InvalidOperationException("Portable fixture bounds must remain finite and non-empty.");
            return bounds;
        }

        internal void ApplyMaterialMass(MaterialView batch)
        {
            if (batch == null || massPerUnit == 0 || Body == null) return;
            // Authored fixture mapping to physical kilograms, never another quantity/accounting owner.
            Body.mass = Mathf.Clamp(batch.Units * massPerUnit, 0.25f, 250f);
        }

        internal bool CanPlace(Transform slot)
        {
            if (!Available) throw new InvalidOperationException("A registered portable body lost its required motion or collision binding: " + Id);
            // Observe current solid geometry at admission; a resized or moved compound
            // must not load using stale setup bounds. The caller synchronizes transforms.
            Bounds placementBounds = ReadPlacementBounds();
            Vector3 center = slot.position + slot.rotation * placementBounds.center;
            Vector3 half = Vector3.Max(placementBounds.extents - Vector3.one * 0.015f, Vector3.one * 0.01f);
            int count = Physics.OverlapBoxNonAlloc(center, half, overlaps, slot.rotation,
                Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            if (count == overlaps.Length) return false; // Saturated observations cannot prove clearance.
            for (int i = 0; i < count; i++)
                if (overlaps[i] != null && overlaps[i].attachedRigidbody != Body) return false;
            return true;
        }

        internal void Place(Guid slotId, Transform slot)
        {
            if (slotted && appliedSlot == slotId) return;
            RestoreFromSlot();
            if (!CanPlace(slot)) throw new InvalidOperationException("The accepted machine slot could not be physically bound.");
            Body.linearVelocity = Vector3.zero; Body.angularVelocity = Vector3.zero;
            Body.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
            Body.interpolation = RigidbodyInterpolation.None;
            Body.isKinematic = true; Body.useGravity = false;
            Body.position = slot.position; Body.rotation = slot.rotation;
            slotted = true; appliedSlot = slotId; generation = 0; obstructionSeconds = 0;
        }

        internal bool Follow(ObjectClaimView state, Transform target, float deltaSeconds)
        {
            RestoreFromSlot();
            if (generation != state.LeaseGeneration)
            {
                generation = state.LeaseGeneration;
                obstructionSeconds = 0;
            }
            Vector3 error = target.position - Body.worldCenterOfMass;
            obstructionSeconds = error.magnitude > 1.2f ? obstructionSeconds + deltaSeconds : 0;
            if (error.sqrMagnitude > 3.5f * 3.5f || obstructionSeconds > 1.5f) return false;
            Vector3 acceleration = error * 85f - Body.linearVelocity * 18f;
            Body.AddForce(Vector3.ClampMagnitude(acceleration, 60f), ForceMode.Acceleration);
            Quaternion rotation = target.rotation * Quaternion.Inverse(Body.rotation);
            rotation.ToAngleAxis(out float angle, out Vector3 axis);
            if (angle > 180f) angle -= 360f;
            if (axis.sqrMagnitude > 0.001f && !float.IsNaN(axis.x))
            {
                Vector3 torque = axis.normalized * (angle * Mathf.Deg2Rad * 25f) - Body.angularVelocity * 8f;
                Body.AddTorque(Vector3.ClampMagnitude(torque, 25f), ForceMode.Acceleration);
            }
            return true;
        }

        internal void Release()
        {
            if (Body == null) return;
            RestoreFromSlot(); generation = 0; obstructionSeconds = 0;
        }

        internal void Throw(Vector3 direction)
        {
            if (Body == null || Body.isKinematic || slotted || direction.sqrMagnitude < 0.001f)
                throw new InvalidOperationException("A throw needs the released dynamic portable body and a valid aim direction.");
            // Preserve existing momentum. A light crate receives at most 5 m/s extra speed;
            // the fixed impulse budget gives heavier loads a shorter throw.
            Body.AddForce(direction.normalized * Mathf.Min(35, Body.mass * 5), ForceMode.Impulse);
        }

        private void RestoreFromSlot()
        {
            if (!slotted) return;
            Body.isKinematic = originalKinematic; Body.useGravity = originalGravity;
            Body.collisionDetectionMode = originalCollisionMode; Body.interpolation = originalInterpolation;
            if (!Body.isKinematic) { Body.linearVelocity = Vector3.zero; Body.angularVelocity = Vector3.zero; }
            slotted = false; appliedSlot = Guid.Empty;
        }

        private static bool Finite(Vector3 value) => !float.IsNaN(value.x) && !float.IsNaN(value.y) && !float.IsNaN(value.z) &&
            !float.IsInfinity(value.x) && !float.IsInfinity(value.y) && !float.IsInfinity(value.z);
    }
}
