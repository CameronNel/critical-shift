using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Explicitly composed host observations. No scene searches or client-declared reach.</summary>
    public sealed class SpatialInteractionAccess : IInteractionAccessPolicy
    {
        private readonly Dictionary<Guid, Transform> actors = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, Transform> targets = new Dictionary<Guid, Transform>();
        private readonly RaycastHit[] hits = new RaycastHit[32];
        private readonly Func<Guid, Guid, Rigidbody, bool> transparentOwnedBody;
        private readonly float reach;

        public SpatialInteractionAccess(float reachMetres = 3.5f, Func<Guid, Guid, Rigidbody, bool> transparentBody = null)
        {
            if (float.IsNaN(reachMetres) || float.IsInfinity(reachMetres) || reachMetres <= 0)
                throw new ArgumentOutOfRangeException(nameof(reachMetres));
            reach = reachMetres;
            transparentOwnedBody = transparentBody;
        }

        public void BindActor(Guid id, Transform eyes) => Bind(actors, id, eyes);
        public void BindTarget(Guid id, Transform root) => Bind(targets, id, root);

        private static void Bind(Dictionary<Guid, Transform> bindings, Guid id, Transform transform)
        {
            if (id == Guid.Empty || transform == null) throw new ArgumentException("Stable identity and a live transform are required.");
            if (bindings.ContainsKey(id)) throw new InvalidOperationException("Duplicate physical identity binding.");
            bindings.Add(id, transform);
        }

        public AccessDecision Evaluate(Guid actorId, Guid entityId, InteractionKind kind)
        {
            if (!actors.TryGetValue(actorId, out var eyes) || eyes == null || !eyes.gameObject.activeInHierarchy)
                return AccessDecision.ActorUnavailable;
            if (!targets.TryGetValue(entityId, out var target) || target == null || !target.gameObject.activeInHierarchy)
                return AccessDecision.TargetUnavailable;
            Vector3 offset = target.position - eyes.position;
            float distance = offset.magnitude;
            if (distance > reach) return AccessDecision.OutOfReach;
            if (distance > 0.01f)
            {
                int count = Physics.RaycastNonAlloc(eyes.position, offset / distance, hits, distance,
                    Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
                if (count == hits.Length) return AccessDecision.OutOfReach;
                for (int i = 0; i < count; i++)
                {
                    var hit = hits[i];
                    if (hit.transform == target || hit.transform.IsChildOf(target)) continue;
                    if (hit.rigidbody != null && transparentOwnedBody != null && transparentOwnedBody(actorId, entityId, hit.rigidbody)) continue;
                    return AccessDecision.OutOfReach;
                }
            }
            return AccessDecision.Allowed;
        }

        public void Clear() { actors.Clear(); targets.Clear(); Array.Clear(hits, 0, hits.Length); }
    }
}
