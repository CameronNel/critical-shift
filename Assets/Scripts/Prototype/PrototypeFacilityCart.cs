using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Host-local prototype boundary: a future network host must own loading, pushing, and impacts.
    [RequireComponent(typeof(Rigidbody))]
    public sealed class PrototypeFacilityCart : MonoBehaviour
    {
        [Min(0.1f)] public float ratedMass = 12f;
        public int cargoSlotCount = 4;
        public float pushImpulse = 2.5f;
        public float knockdownSpeed = 1.5f;
        public float incapacitateSpeed = 5f;
        public Transform hopper;
        readonly List<PrototypeOre> cargo = new List<PrototypeOre>();
        readonly List<Transform> slots = new List<Transform>();
        Rigidbody body;
        public float CurrentMass { get; private set; }
        public int CargoCount => cargo.Count;
        public bool IsOverloaded => CurrentMass > ratedMass;
        public Rigidbody Body { get { EnsureInitialized(); return body; } }
        public IReadOnlyList<PrototypeOre> Cargo => cargo;
        public event Action<float> OverloadWarning;
        public event Action<PrototypeOre> OreLoaded;
        public event Action<int, float> BatchUnloaded;
        public event Action ResetCompleted;

        void Awake() { EnsureInitialized(); }

        void EnsureInitialized()
        {
            if (body == null) body = GetComponent<Rigidbody>();
            if (body == null) body = gameObject.AddComponent<Rigidbody>();
            if (slots.Count > 0) return;
            for (int i = 0; i < Mathf.Max(0, cargoSlotCount); i++)
            {
                var slot = new GameObject("CargoSlot_" + i).transform;
                slot.SetParent(transform, false);
                int row = i / 2, column = i % 2;
                slot.localPosition = new Vector3((column - .5f) * .65f, .65f + row * .35f, 0f);
                slots.Add(slot);
            }
        }

        public bool TryLoad(PrototypeOre ore)
        {
            EnsureInitialized();
            if (!ore || cargo.Contains(ore) || cargo.Count >= slots.Count || ore.Body == null) return false;
            float mass = Mathf.Max(0.01f, ore.batch.mass);
            cargo.Add(ore); CurrentMass += mass;
            ore.transform.SetParent(slots[cargo.Count - 1], false);
            ore.transform.localPosition = Vector3.zero;
            ore.Body.isKinematic = true;
            OreLoaded?.Invoke(ore);
            if (IsOverloaded) OverloadWarning?.Invoke(CurrentMass - ratedMass);
            return true;
        }

        public int UnloadBatch(Transform target, int maxItems = -1)
        {
            EnsureInitialized();
            if (!target) return 0;
            int unloaded = 0;
            int limit = maxItems < 0 ? cargo.Count : maxItems;
            while (unloaded < limit && cargo.Count > 0)
            {
                var ore = cargo[0]; cargo.RemoveAt(0);
                if (ore)
                {
                    ore.transform.SetParent(null, true);
                    ore.transform.position = target.position + Vector3.up * (.2f + unloaded * .15f);
                    if (ore.Body != null) ore.Body.isKinematic = false;
                    CurrentMass -= Mathf.Max(0.01f, ore.batch.mass);
                }
                unloaded++;
            }
            RefreshSlotParents();
            if (unloaded > 0) BatchUnloaded?.Invoke(unloaded, CurrentMass);
            return unloaded;
        }

        public int UnloadBatch(PrototypeConveyor hopper, int maxItems = -1)
        {
            EnsureInitialized();
            if (!hopper) return 0;
            int unloaded = 0;
            int limit = maxItems < 0 ? cargo.Count : maxItems;
            while (unloaded < limit && cargo.Count > 0)
            {
                var ore = cargo[0];
                if (!ore || !hopper.TryAccept(ore)) break;
                cargo.RemoveAt(0); CurrentMass -= Mathf.Max(0.01f, ore.batch.mass); unloaded++;
            }
            RefreshSlotParents();
            if (unloaded > 0) BatchUnloaded?.Invoke(unloaded, CurrentMass);
            return unloaded;
        }

        public void Push(Vector3 direction, float multiplier = 1f)
        {
            EnsureInitialized();
            if (body != null) body.AddForce(direction.normalized * pushImpulse * Mathf.Max(0f, multiplier), ForceMode.Impulse);
        }

        void OnCollisionEnter(Collision collision)
        {
            var worker = collision.collider.GetComponentInParent<PrototypeWorkerBody>();
            if (!worker) return;
            ApplyImpact(worker, collision.relativeVelocity.magnitude);
        }

        public void ApplyImpactForTest(PrototypeWorkerBody worker, float impact) { ApplyImpact(worker, impact); }

        void ApplyImpact(PrototypeWorkerBody worker, float impact)
        {
            if (worker == null) return;
            // The one-player proof cannot reanimate itself. High-speed cart hits remain
            // funny and disruptive, but always recover for the local operator.
            if (worker.GetComponent<PrototypePlayerController>() != null)
            {
                if (impact >= knockdownSpeed) worker.KnockDown(Mathf.Lerp(1.5f, 3f, impact / Mathf.Max(.1f, incapacitateSpeed)));
                return;
            }
            if (impact >= incapacitateSpeed) worker.Incapacitate();
            else if (impact >= knockdownSpeed) worker.KnockDown(Mathf.Lerp(1.5f, 3f, impact / incapacitateSpeed));
        }

        public void ResetCart()
        {
            EnsureInitialized();
            for (int i = cargo.Count - 1; i >= 0; i--)
            {
                var ore = cargo[i];
                if (ore) { ore.transform.SetParent(null, true); if (ore.Body != null) ore.Body.isKinematic = false; }
            }
            cargo.Clear(); CurrentMass = 0f;
            if (body != null) { body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; }
            RefreshSlotParents(); ResetCompleted?.Invoke();
        }

        void RefreshSlotParents()
        {
            for (int i = 0; i < cargo.Count; i++)
            {
                if (!cargo[i]) continue;
                cargo[i].transform.SetParent(slots[i], false);
                cargo[i].transform.localPosition = Vector3.zero;
            }
        }
    }
}
