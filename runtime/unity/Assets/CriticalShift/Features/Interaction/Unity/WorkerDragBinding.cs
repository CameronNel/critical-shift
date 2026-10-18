using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Delegates physical pulling to the bound worker rig. Owns no health state or Rigidbody force path.</summary>
    internal sealed class WorkerDragBinding
    {
        internal readonly Guid Id;
        internal readonly Rigidbody Representative;
        private readonly HashSet<Rigidbody> segments;
        private readonly Func<ObjectClaimView, Vector3, float, bool> pull;
        private readonly Action release;
        private readonly Action<ObjectClaimView, bool> setHoist;
        private readonly Func<float> readMass;
        internal WorkerDragBinding(Guid id, Rigidbody[] bodies, Func<ObjectClaimView, Vector3, float, bool> applyPull,
            Action releasePull, Func<float> physicalMass, Action<ObjectClaimView, bool> hoistMode)
        {
            if (id == Guid.Empty || bodies == null || bodies.Length < 2 || bodies.Length > 16)
                throw new ArgumentException("Bind a bounded worker body's explicit physical segments.");
            segments = new HashSet<Rigidbody>();
            foreach (var body in bodies)
                if (body == null || !segments.Add(body)) throw new ArgumentException("Worker physical segments must be unique and present.");
            Id = id; Representative = bodies[0]; pull = applyPull ?? throw new ArgumentNullException(nameof(applyPull));
            release = releasePull ?? throw new ArgumentNullException(nameof(releasePull));
            readMass = physicalMass ?? throw new ArgumentNullException(nameof(physicalMass));
            setHoist = hoistMode ?? throw new ArgumentNullException(nameof(hoistMode));
        }
        internal bool Owns(Rigidbody body) => body != null && segments.Contains(body);
        internal bool Active
        {
            get { foreach (var body in segments) if (body == null || !body.gameObject.activeInHierarchy) return false; return true; }
        }
        internal float Mass
        {
            get
            {
                float mass = readMass();
                if (mass <= 0 || float.IsNaN(mass) || float.IsInfinity(mass)) throw new InvalidOperationException("Worker physical mass must remain finite and positive.");
                return mass;
            }
        }
        internal bool Follow(ObjectClaimView claim, Transform target, float seconds) => pull(claim, target.position, seconds);
        internal void Hoist(ObjectClaimView claim, bool raised) => setHoist(claim, raised);
        internal void Release() => release();
    }
}
