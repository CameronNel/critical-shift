using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Explicit fixture observations only. Reports one failure; never moves, clamps or respawns a body.</summary>
    [DisallowMultipleComponent]
    public sealed class PhysicsSafetyMonitor : MonoBehaviour
    {
        private sealed class Binding
        {
            internal readonly Rigidbody Body;
            internal readonly string Label;
            internal Binding(Rigidbody body, string label) { Body = body; Label = label; }
        }
        private readonly List<Binding> bodies = new List<Binding>(32);
        private Transform anchor;
        private Bounds region;
        private float linearLimit, angularLimit;
        private Func<bool> live;
        private Action<Exception> report;
        private bool active, initialized, ended;
        public bool FaultLatched { get; private set; }
        public string Fault { get; private set; } = "";
        public int BoundBodyCount => bodies.Count;
        public int DynamicBodyCount { get; private set; }
        public int PeakDynamicBodyCount { get; private set; }
        public float PeakLinearSpeed { get; private set; }
        public float PeakAngularSpeed { get; private set; }

        public void Initialize(Transform coordinateRoot, Bounds allowedRegion, float maximumLinearSpeed, float maximumAngularSpeed,
            Func<bool> worldLive, Action<Exception> onFailure)
        {
            if (initialized || coordinateRoot == null || !Finite(allowedRegion.center) || !Finite(allowedRegion.size) ||
                allowedRegion.size.x <= 0 || allowedRegion.size.y <= 0 || allowedRegion.size.z <= 0 ||
                !Finite(maximumLinearSpeed) || !Finite(maximumAngularSpeed) || maximumLinearSpeed <= 0 || maximumAngularSpeed <= 0)
                throw new ArgumentException("Bind one bounded physics observation region and finite positive speed limits.");
            anchor = coordinateRoot; region = allowedRegion; linearLimit = maximumLinearSpeed; angularLimit = maximumAngularSpeed;
            live = worldLive ?? throw new ArgumentNullException(nameof(worldLive));
            report = onFailure ?? throw new ArgumentNullException(nameof(onFailure)); initialized = true;
        }

        public void Bind(Rigidbody body, string label)
        {
            if (!initialized || active || ended || body == null || string.IsNullOrWhiteSpace(label) || bodies.Count >= 64)
                throw new InvalidOperationException("Bind at most 64 named physics bodies during composition.");
            foreach (var binding in bodies)
                if (binding.Body == body) throw new InvalidOperationException("A physics observation body was bound twice.");
            bodies.Add(new Binding(body, label));
        }

        public void Activate()
        {
            if (!initialized || active || ended || bodies.Count == 0 || !live())
                throw new InvalidOperationException("Start physics observation once after the composed world becomes live.");
            active = true;
        }

        public void Sample()
        {
            if (!active) return;
            try
            {
                if (!live()) { Shutdown(); return; }
                if (anchor == null || !anchor.gameObject.activeInHierarchy || (anchor.lossyScale - Vector3.one).sqrMagnitude > 0.0001f)
                    throw new InvalidOperationException("Physics observation coordinates became unavailable or changed scale.");
                int dynamicCount = 0;
                foreach (var binding in bodies)
                {
                    var body = binding.Body;
                    if (body == null || !body.gameObject.activeInHierarchy)
                        throw new InvalidOperationException("Physics body became unavailable: " + binding.Label);
                    if (!Finite(body.position) || !Finite(body.rotation))
                        throw new InvalidOperationException("Physics body pose became non-finite: " + binding.Label);
                    if (!region.Contains(anchor.InverseTransformPoint(body.position)))
                        throw new InvalidOperationException("Physics body escaped fixture bounds: " + binding.Label);
                    if (body.isKinematic) continue;
                    dynamicCount++;
                    Vector3 linear = body.linearVelocity, angular = body.angularVelocity;
                    if (!Finite(linear) || !Finite(angular))
                        throw new InvalidOperationException("Physics body velocity became non-finite: " + binding.Label);
                    float speed = linear.magnitude, spin = angular.magnitude;
                    PeakLinearSpeed = Mathf.Max(PeakLinearSpeed, speed); PeakAngularSpeed = Mathf.Max(PeakAngularSpeed, spin);
                    if (speed > linearLimit || spin > angularLimit)
                        throw new InvalidOperationException("Physics body exceeded fixture speed limits: " + binding.Label);
                }
                DynamicBodyCount = dynamicCount; PeakDynamicBodyCount = Mathf.Max(PeakDynamicBodyCount, dynamicCount);
            }
            catch (Exception exception) { Fail(exception); }
        }

        private void FixedUpdate() => Sample();
        private void Fail(Exception exception)
        {
            if (!active) return;
            active = false; ended = true; FaultLatched = true; Fault = exception.Message;
            try { report(exception); }
            finally { Shutdown(); }
        }
        public void Shutdown()
        { active = false; ended = true; DynamicBodyCount = 0; bodies.Clear(); anchor = null; live = null; report = null; }
        private void OnDisable()
        {
            if (!active) return;
            try { if (live()) Fail(new InvalidOperationException("The live physics safety monitor was disabled.")); }
            finally { Shutdown(); }
        }
        private void OnDestroy() => Shutdown();
        private static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);
        private static bool Finite(Vector3 value) => Finite(value.x) && Finite(value.y) && Finite(value.z);
        private static bool Finite(Quaternion value) => Finite(value.x) && Finite(value.y) && Finite(value.z) && Finite(value.w);
    }
}
