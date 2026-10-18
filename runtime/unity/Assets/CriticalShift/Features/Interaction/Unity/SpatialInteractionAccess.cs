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
        private readonly Dictionary<Guid, Transform> targetPoints = new Dictionary<Guid, Transform>();
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
        public void BindTarget(Guid id, Transform root, Transform interactionPoint = null)
        {
            var point = interactionPoint == null ? root : interactionPoint;
            if (root == null || point == null || (point != root && !point.IsChildOf(root)))
                throw new ArgumentException("The interaction point must belong to its explicit collider hierarchy.");
            Bind(targets, id, root); targetPoints.Add(id, point);
        }

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
            if (!targetPoints.TryGetValue(entityId, out var point) || point == null || !point.gameObject.activeInHierarchy)
                return AccessDecision.TargetUnavailable;
            Vector3 offset = point.position - eyes.position;
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

        public Guid PickTarget(Guid actorId)
        {
            if (!actors.TryGetValue(actorId, out var eyes) || eyes == null || !eyes.gameObject.activeInHierarchy) return Guid.Empty;
            int count = Physics.RaycastNonAlloc(eyes.position, eyes.forward, hits, reach,
                Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
            if (count == hits.Length) return Guid.Empty;
            Transform nearest = null; float distance = float.PositiveInfinity;
            for (int i = 0; i < count; i++)
            {
                var hit = hits[i];
                if (hit.rigidbody != null && transparentOwnedBody != null && transparentOwnedBody(actorId, Guid.Empty, hit.rigidbody)) continue;
                if (hit.distance >= distance) continue;
                distance = hit.distance; nearest = hit.transform;
            }
            if (nearest == null) return Guid.Empty;
            foreach (var target in targets)
                if (target.Value != null && targetPoints.TryGetValue(target.Key, out var point) && point != null && point.gameObject.activeInHierarchy &&
                    (nearest == target.Value || nearest.IsChildOf(target.Value))) return target.Key;
            return Guid.Empty; // An unregistered wall in front never grants access to a target behind it.
        }

        public string DisplayName(Guid id) => targets.TryGetValue(id, out var target) && target != null ? target.name : "";

        public void Clear() { actors.Clear(); targets.Clear(); targetPoints.Clear(); Array.Clear(hits, 0, hits.Length); }
    }
}
