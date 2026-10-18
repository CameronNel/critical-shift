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
        private readonly float massPerUnit;
        private readonly Bounds localBounds;
        private readonly Collider[] overlaps = new Collider[32];
        private bool slotted;
        private Guid appliedSlot;
        private long generation;
        private float obstructionSeconds;

        internal CarryBodyBinding(Guid id, Rigidbody body, float physicalMassPerUnit = 0)
        {
            if (id == Guid.Empty || body == null) throw new ArgumentException("Body identity and Rigidbody are required.");
            if (body.isKinematic) throw new ArgumentException("Portable fixture bodies must begin dynamic.");
            if (physicalMassPerUnit < 0 || float.IsNaN(physicalMassPerUnit) || float.IsInfinity(physicalMassPerUnit))
                throw new ArgumentOutOfRangeException(nameof(physicalMassPerUnit));
            Id = id; Body = body;
            massPerUnit = physicalMassPerUnit;
            originalKinematic = body.isKinematic; originalGravity = body.useGravity;
            var colliders = body.GetComponentsInChildren<Collider>();
            if (colliders.Length == 0) throw new ArgumentException("A portable body needs a collider.");
            Bounds worldBounds = colliders[0].bounds;
            foreach (var collider in colliders)
            {
                if (collider.isTrigger || collider.attachedRigidbody != body)
                    throw new ArgumentException("Portable fixture colliders must be solid and belong to this body.");
                worldBounds.Encapsulate(collider.bounds);
            }
            // Fixture portable bodies use axis-aligned box roots at registration.
            localBounds = new Bounds(body.transform.InverseTransformPoint(worldBounds.center), worldBounds.size);
        }

        internal void ApplyMaterialMass(MaterialView batch)
        {
            if (batch == null || massPerUnit == 0 || Body == null) return;
            // Authored fixture mapping to physical kilograms, never another quantity/accounting owner.
            Body.mass = Mathf.Clamp(batch.Units * massPerUnit, 0.25f, 250f);
        }

        internal bool CanPlace(Transform slot)
        {
            Vector3 center = slot.position + slot.rotation * localBounds.center;
            Vector3 half = Vector3.Max(localBounds.extents - Vector3.one * 0.015f, Vector3.one * 0.01f);
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
            if (!Body.isKinematic) { Body.linearVelocity = Vector3.zero; Body.angularVelocity = Vector3.zero; }
            slotted = false; appliedSlot = Guid.Empty;
        }
    }
}
