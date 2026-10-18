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
        private float linearLimit;
        private double rotationalEnergyPerMassLimit;
        private Func<bool> live;
        private Action<Exception> report;
        private bool active, initialized, ended;
        public bool FaultLatched { get; private set; }
        public string Fault { get; private set; } = "";
        public int BoundBodyCount => bodies.Count;
        public int DynamicBodyCount { get; private set; }
        public int PeakDynamicBodyCount { get; private set; }
        public double PeakLinearSpeed { get; private set; }
        public double PeakAngularSpeed { get; private set; }
        public double PeakRotationalEnergyPerMass { get; private set; }

        public void Initialize(Transform coordinateRoot, Bounds allowedRegion, float maximumLinearSpeed, double maximumRotationalEnergyPerMass,
            Func<bool> worldLive, Action<Exception> onFailure)
        {
            if (initialized || coordinateRoot == null || !Finite(allowedRegion.center) || !Finite(allowedRegion.size) ||
                allowedRegion.size.x <= 0 || allowedRegion.size.y <= 0 || allowedRegion.size.z <= 0 ||
                !Finite(maximumLinearSpeed) || !Finite(maximumRotationalEnergyPerMass) ||
                maximumLinearSpeed <= 0 || maximumRotationalEnergyPerMass <= 0)
                throw new ArgumentException("Bind one bounded physics region, positive linear speed and specific rotational energy limits.");
            anchor = coordinateRoot; region = allowedRegion; linearLimit = maximumLinearSpeed;
            rotationalEnergyPerMassLimit = maximumRotationalEnergyPerMass;
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
                    Quaternion rotation = body.rotation;
                    if (!Finite(body.position) || !ValidRotation(rotation))
                        throw new InvalidOperationException("Physics body pose became non-finite or invalid: " + binding.Label);
                    if (!region.Contains(anchor.InverseTransformPoint(body.position)))
                        throw new InvalidOperationException("Physics body escaped fixture bounds: " + binding.Label);
                    if (body.isKinematic) continue;
                    dynamicCount++;
                    Vector3 linear = body.linearVelocity, angular = body.angularVelocity;
                    if (!Finite(linear) || !Finite(angular))
                        throw new InvalidOperationException("Physics body velocity became non-finite: " + binding.Label);
                    double speed = Magnitude(linear), spin = Magnitude(angular);
                    PeakLinearSpeed = Math.Max(PeakLinearSpeed, speed); PeakAngularSpeed = Math.Max(PeakAngularSpeed, spin);
                    double energy = SpecificRotationalEnergy(body, rotation, angular, binding.Label);
                    PeakRotationalEnergyPerMass = Math.Max(PeakRotationalEnergyPerMass, energy);
                    if (speed > linearLimit || energy > rotationalEnergyPerMassLimit)
                        throw new InvalidOperationException("Physics body exceeded fixture linear speed or specific rotational energy limits: " + binding.Label +
                            " linear=" + speed.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                            "/" + linearLimit.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                            " angular=" + spin.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                            " rotationalEnergyPerMass=" + energy.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                            "/" + rotationalEnergyPerMassLimit.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + " J/kg");
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
        private static double SpecificRotationalEnergy(Rigidbody body, Quaternion rotation, Vector3 angular, string label)
        {
            float mass = body.mass; Vector3 inertia = body.inertiaTensor; Quaternion tensorRotation = body.inertiaTensorRotation;
            if (!Finite(mass) || mass <= 0 || !Finite(inertia) || inertia.x < 0 || inertia.y < 0 || inertia.z < 0 ||
                !ValidRotation(tensorRotation))
                throw new InvalidOperationException("Physics body mass or native inertia became invalid: " + label);
            // Native tensor components are principal moments about COM. Rotate world angular velocity
            // by inverse(body.rotation * inertiaTensorRotation), doing the vector products in double.
            // The tiny quaternion normalization handles native roundoff; no observed motion is changed.
            Quaternion inverse = Quaternion.Inverse(rotation * tensorRotation);
            double norm = Math.Sqrt((double)inverse.x * inverse.x + (double)inverse.y * inverse.y +
                (double)inverse.z * inverse.z + (double)inverse.w * inverse.w);
            double x = inverse.x / norm, y = inverse.y / norm, z = inverse.z / norm, w = inverse.w / norm;
            double tx = 2 * (y * angular.z - z * angular.y), ty = 2 * (z * angular.x - x * angular.z),
                tz = 2 * (x * angular.y - y * angular.x);
            double ox = angular.x + w * tx + y * tz - z * ty;
            double oy = angular.y + w * ty + z * tx - x * tz;
            double oz = angular.z + w * tz + x * ty - y * tx;
            // Unity encodes infinite inertia (including locked rotational axes) as zero, not zero energy.
            // The input world omega and native frames are floats. Permit only projection roundoff:
            // eight float machine-epsilon units, with a 1 rad/s scale floor for the absolute term.
            // Raw angular velocity/peak stay intact; this never writes or clamps physical motion.
            double roundoff = 8 * 1.1920928955078125e-7 * Math.Max(1, Magnitude(angular));
            if ((inertia.x == 0 && Math.Abs(ox) > roundoff) || (inertia.y == 0 && Math.Abs(oy) > roundoff) ||
                (inertia.z == 0 && Math.Abs(oz) > roundoff))
                throw new InvalidOperationException("Physics body rotates about an infinite-inertia axis: " + label);
            double energy = 0.5 * ((double)inertia.x * ox * ox + (double)inertia.y * oy * oy +
                (double)inertia.z * oz * oz) / mass;
            if (!Finite(energy)) throw new InvalidOperationException("Physics body specific rotational energy became non-finite: " + label);
            return energy;
        }
        private static double Magnitude(Vector3 value) => Math.Sqrt((double)value.x * value.x +
            (double)value.y * value.y + (double)value.z * value.z);
        private static bool ValidRotation(Quaternion value)
        {
            if (!Finite(value)) return false;
            double length = (double)value.x * value.x + (double)value.y * value.y +
                (double)value.z * value.z + (double)value.w * value.w;
            return Math.Abs(length - 1) <= 0.0001;
        }
        private static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);
        private static bool Finite(double value) => !double.IsNaN(value) && !double.IsInfinity(value);
        private static bool Finite(Vector3 value) => Finite(value.x) && Finite(value.y) && Finite(value.z);
        private static bool Finite(Quaternion value) => Finite(value.x) && Finite(value.y) && Finite(value.z) && Finite(value.w);
    }
}
