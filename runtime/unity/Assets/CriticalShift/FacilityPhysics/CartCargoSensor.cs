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
        public bool Saturated { get; private set; }
        public int MaximumBodies { get; set; } = 32;
        public int BodyCount { get; private set; }
        public float Mass { get; private set; }

        public void Initialize(Rigidbody cartBody, Func<Rigidbody, Rigidbody> physicalGroup, Func<Rigidbody, float> groupMass)
        {
            if (cart != null || cartBody == null) throw new InvalidOperationException("Bind one explicit cart body.");
            cart = cartBody; groupFor = physicalGroup ?? throw new ArgumentNullException(nameof(physicalGroup));
            readMass = groupMass ?? throw new ArgumentNullException(nameof(groupMass));
            sensor = GetComponent<BoxCollider>();
            if (!sensor.isTrigger) throw new InvalidOperationException("The cargo sensor must be a trigger.");
        }

        private void FixedUpdate()
        {
            Mass = 0; BodyCount = 0; observedBodies.Clear(); groups.Clear();
            if (sensor == null || cart == null || groupFor == null) return;
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
            // Keep an overflow visible until fixture reset; its truncated load observation cannot authorize drive.
        }

        private void OnDisable()
        { observedBodies.Clear(); groups.Clear(); Array.Clear(contacts, 0, contacts.Length); Mass = 0; BodyCount = 0; Saturated = false; }
    }
}
