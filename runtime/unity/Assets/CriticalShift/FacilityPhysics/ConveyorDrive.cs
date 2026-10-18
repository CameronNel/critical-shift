using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded horizontal belt acceleration for explicitly authorized free bodies.</summary>
    [DisallowMultipleComponent, RequireComponent(typeof(BoxCollider))]
    public sealed class ConveyorDrive : MonoBehaviour
    {
        private readonly Collider[] contacts = new Collider[64];
        private readonly HashSet<Rigidbody> bodies = new HashSet<Rigidbody>();
        private BoxCollider sensor;
        private Func<Rigidbody, bool> mayMove;
        private Func<bool> mayRun;
        private float stalledSeconds;
        private bool initialized;
        public bool Available => initialized && isActiveAndEnabled && sensor != null && sensor.enabled && sensor.isTrigger;
        public bool Powered { get; set; } = true;
        public bool Jammed { get; private set; }
        public bool Saturated { get; private set; }
        public bool Running { get; private set; }
        public int MovingBodyCount { get; private set; }
        public float BeltSpeed { get; set; } = 1.4f;

        public void Initialize(Func<Rigidbody, bool> ownershipFilter, Func<bool> runPermission)
        {
            if (initialized) throw new InvalidOperationException("Conveyor is already bound.");
            if (ownershipFilter == null || runPermission == null) throw new ArgumentException("Conveyor permissions are required.");
            var volume = GetComponent<BoxCollider>();
            if (!volume.isTrigger || !volume.enabled) throw new InvalidOperationException("Conveyor observation bounds must be an enabled trigger.");
            mayMove = ownershipFilter; mayRun = runPermission; sensor = volume; initialized = true;
        }

        public void ResetJam() { Jammed = false; Saturated = false; stalledSeconds = 0; }

        private void FixedUpdate()
        {
            if (!initialized) return;
            try { Step(); }
            catch { enabled = false; throw; }
        }

        private void Step()
        {
            Running = false; MovingBodyCount = 0;
            if (!Available) throw new InvalidOperationException("The bound conveyor observation volume became unavailable.");
            if (!Powered || Jammed || !mayRun()) return;
            if (BeltSpeed <= 0 || float.IsNaN(BeltSpeed) || float.IsInfinity(BeltSpeed))
                throw new InvalidOperationException("Belt speed must be finite and positive.");
            Vector3 scale = transform.lossyScale;
            Vector3 half = Vector3.Scale(sensor.size * 0.5f,
                new Vector3(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z)));
            int count = Physics.OverlapBoxNonAlloc(transform.TransformPoint(sensor.center), half,
                contacts, transform.rotation, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            if (count == contacts.Length) { Saturated = true; Jammed = true; return; }
            bodies.Clear();
            for (int i = 0; i < count; i++)
            {
                var body = contacts[i] == null ? null : contacts[i].attachedRigidbody;
                if (body != null && !body.isKinematic && mayMove(body)) bodies.Add(body);
            }
            Vector3 direction = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            bool stalled = false;
            foreach (var body in bodies)
            {
                float speed = Vector3.Dot(body.linearVelocity, direction);
                stalled |= speed < 0.1f;
                body.AddForce(direction * Mathf.Clamp((BeltSpeed - speed) * 6, -8, 8), ForceMode.Acceleration);
            }
            MovingBodyCount = bodies.Count;
            stalledSeconds = bodies.Count != 0 && stalled ? stalledSeconds + Time.fixedDeltaTime : 0;
            if (stalledSeconds >= 2) { Jammed = true; return; }
            Running = true;
        }

        private void OnDisable() { Running = false; MovingBodyCount = 0; bodies.Clear(); Array.Clear(contacts, 0, contacts.Length); }
    }
}
