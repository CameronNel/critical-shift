using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded current-volume observation. Explicit physical groups count once, without owning cargo custody.</summary>
    [RequireComponent(typeof(BoxCollider))]
    public sealed class CartCargoSensor : MonoBehaviour
    {
        private readonly Collider[] contacts = new Collider[64];
        private readonly HashSet<Rigidbody> observedBodies = new HashSet<Rigidbody>();
        private readonly HashSet<Rigidbody> groups = new HashSet<Rigidbody>();
        private Func<Rigidbody, Rigidbody> groupFor;
        private Func<Rigidbody, float> readMass;
        private Rigidbody cart;
        private BoxCollider sensor;
        private bool initialized, sampled;
        public bool Available => sampled && isActiveAndEnabled && cart != null && cart.gameObject.activeInHierarchy &&
            sensor != null && sensor.enabled && sensor.isTrigger && sensor.gameObject.activeInHierarchy && sensor.attachedRigidbody == cart;
        public bool Saturated { get; private set; }
        public int MaximumBodies { get; set; } = 32;
        public int BodyCount { get; private set; }
        public float Mass { get; private set; }

        public void Initialize(Rigidbody cartBody, Func<Rigidbody, Rigidbody> physicalGroup, Func<Rigidbody, float> groupMass)
        {
            if (initialized || cartBody == null) throw new InvalidOperationException("Bind one explicit cart body.");
            cart = cartBody; groupFor = physicalGroup ?? throw new ArgumentNullException(nameof(physicalGroup));
            readMass = groupMass ?? throw new ArgumentNullException(nameof(groupMass));
            sensor = GetComponent<BoxCollider>();
            if (!sensor.isTrigger || !sensor.enabled || sensor.attachedRigidbody != cart)
                throw new InvalidOperationException("The cargo sensor must be an enabled trigger belonging to its cart body.");
            initialized = true;
        }

        private void FixedUpdate()
        {
            if (!initialized) return;
            try { Sample(); }
            catch { enabled = false; throw; }
        }

        private void Sample()
        {
            sampled = false;
            Mass = 0; BodyCount = 0; observedBodies.Clear(); groups.Clear();
            if (sensor == null || cart == null || !sensor.enabled || !sensor.isTrigger || sensor.attachedRigidbody != cart || !cart.gameObject.activeInHierarchy)
                throw new InvalidOperationException("The bound cart cargo observation volume became unavailable.");
            if (MaximumBodies < 1 || MaximumBodies > 64)
            { Saturated = true; throw new InvalidOperationException("Cargo observation capacity must be between one and 64 physical bodies."); }
            Vector3 scale = transform.lossyScale;
            Vector3 half = Vector3.Scale(sensor.size * 0.5f, new Vector3(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z)));
            int count = Physics.OverlapBoxNonAlloc(transform.TransformPoint(sensor.center), half, contacts,
                transform.rotation, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            if (count == contacts.Length) Saturated = true;
            for (int i = 0; i < count; i++)
            {
                var body = contacts[i] == null ? null : contacts[i].attachedRigidbody;
                if (body == null || body == cart || !body.gameObject.activeInHierarchy || !observedBodies.Add(body)) continue;
                if (observedBodies.Count > MaximumBodies) { Saturated = true; continue; }
                var group = groupFor(body);
                if (group == null || group == cart || !group.gameObject.activeInHierarchy || !groups.Add(group)) continue;
                float mass = readMass(group);
                if (mass <= 0 || float.IsNaN(mass) || float.IsInfinity(mass))
                { Saturated = true; throw new InvalidOperationException("Cargo group mass must be finite and positive."); }
                float total = Mass + mass;
                if (float.IsInfinity(total))
                { Saturated = true; throw new InvalidOperationException("Cargo observation exceeded its finite mass range."); }
                Mass = total; BodyCount++;
            }
            sampled = true;
            // Keep an overflow visible until fixture reset; its truncated load observation cannot authorize drive.
        }

        private void OnDisable()
        { sampled = false; observedBodies.Clear(); groups.Clear(); Array.Clear(contacts, 0, contacts.Length); Mass = 0; BodyCount = 0; }
    }
}
