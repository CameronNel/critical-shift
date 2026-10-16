using System;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    public readonly struct BonkContact
    {
        public readonly Collider Shape;
        public readonly Vector3 Position, Normal;
        public BonkContact(Collider shape, Vector3 position, Vector3 normal) { Shape = shape; Position = position; Normal = normal; }
    }
    public sealed class BonkHitQuery
    {
        private readonly RaycastHit[] hits = new RaycastHit[64];
        private readonly Collider[] overlaps = new Collider[64];
        // Check radial obstruction as well as the moving blade path; walls take priority over a worker behind them.
        public bool TryContact(WorkerScenePort actor, SceneTarget tool, Vector3 origin, Vector3 from, Vector3 to,
            float radius, int mask, out BonkContact contact, out bool complete)
        {
            contact = default; complete = true;
            if (!Cast(actor, tool, origin, to, radius, mask, out var radial, out complete)) return false;
            if (!complete) return false;
            if (radial.Shape != null) { contact = radial; return true; }
            if (!Cast(actor, tool, from, to, radius, mask, out contact, out complete)) return false;
            if (contact.Shape == null) return false;
            // A swept side hit must also be visible from the worker, preventing corner/door penetration.
            if (!Cast(actor, tool, origin, contact.Position, radius, mask, out var visible, out complete) || !complete) return false;
            if (visible.Shape != null && visible.Shape != contact.Shape) contact = visible;
            return true;
        }
        private bool Cast(WorkerScenePort actor, SceneTarget tool, Vector3 from, Vector3 to, float radius, int mask,
            out BonkContact contact, out bool complete)
        {
            contact = default; complete = true; Vector3 delta = to - from;
            int count = Physics.OverlapSphereNonAlloc(from, radius, overlaps, mask, QueryTriggerInteraction.Ignore);
            if (count == overlaps.Length) { complete = false; return false; }
            for (int i = 0; i < count; i++) if (!Excluded(overlaps[i], actor, tool))
            { contact = new BonkContact(overlaps[i], overlaps[i].ClosestPoint(from), -delta.normalized); return true; }
            if (delta.sqrMagnitude < .000001f) return true;
            count = Physics.SphereCastNonAlloc(from, radius, delta.normalized, hits, delta.magnitude, mask, QueryTriggerInteraction.Ignore);
            if (count == hits.Length) { complete = false; return false; }
            float nearest = float.PositiveInfinity;
            for (int i = 0; i < count; i++) if (!Excluded(hits[i].collider, actor, tool) && hits[i].distance < nearest)
            { nearest = hits[i].distance; contact = new BonkContact(hits[i].collider, hits[i].point, hits[i].normal); }
            return true;
        }
        private static bool Excluded(Collider shape, WorkerScenePort actor, SceneTarget tool) => shape == null ||
            Array.IndexOf(actor.BodyColliders, shape) >= 0 || shape.transform.IsChildOf(actor.transform) ||
            tool != null && shape.transform.IsChildOf(tool.transform);
    }
}
