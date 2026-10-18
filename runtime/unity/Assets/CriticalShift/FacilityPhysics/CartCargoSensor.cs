using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded physical load observation. Counts a multi-collider Rigidbody once.</summary>
    [RequireComponent(typeof(BoxCollider))]
    public sealed class CartCargoSensor : MonoBehaviour
    {
        private readonly Dictionary<Rigidbody, int> overlaps = new Dictionary<Rigidbody, int>();
        private readonly List<Rigidbody> stale = new List<Rigidbody>();
        private Func<Rigidbody, bool> mayCount;
        private Rigidbody cart;
        public bool Saturated { get; private set; }
        public int MaximumBodies { get; set; } = 32;
        public int BodyCount { get; private set; }
        public float Mass { get; private set; }

        public void Initialize(Rigidbody cartBody, Func<Rigidbody, bool> ownershipFilter)
        {
            if (cart != null || cartBody == null) throw new InvalidOperationException("Bind one explicit cart body.");
            cart = cartBody; mayCount = ownershipFilter ?? throw new ArgumentNullException(nameof(ownershipFilter));
            var sensor = GetComponent<BoxCollider>();
            if (!sensor.isTrigger) throw new InvalidOperationException("The cargo sensor must be a trigger.");
        }

        private void OnTriggerEnter(Collider other)
        {
            var body = other.attachedRigidbody;
            if (body == null || body == cart || mayCount == null) return;
            if (overlaps.TryGetValue(body, out int count)) overlaps[body] = count + 1;
            else if (overlaps.Count < MaximumBodies) overlaps.Add(body, 1);
            else Saturated = true;
        }

        private void OnTriggerExit(Collider other)
        {
            var body = other.attachedRigidbody;
            if (body == null || !overlaps.TryGetValue(body, out int count)) return;
            if (count == 1) overlaps.Remove(body); else overlaps[body] = count - 1;
        }

        private void FixedUpdate()
        {
            Mass = 0; BodyCount = 0; stale.Clear();
            foreach (var pair in overlaps)
            {
                var body = pair.Key;
                if (body == null || !body.gameObject.activeInHierarchy) { stale.Add(body); continue; }
                if (mayCount != null && mayCount(body)) { Mass += body.mass; BodyCount++; }
            }
            foreach (var body in stale) overlaps.Remove(body);
            // Saturation stays visible until the fixture is reset: missing enter events cannot be reconstructed safely.
        }

        private void OnDisable() { overlaps.Clear(); stale.Clear(); Mass = 0; BodyCount = 0; Saturated = false; }
    }
}
