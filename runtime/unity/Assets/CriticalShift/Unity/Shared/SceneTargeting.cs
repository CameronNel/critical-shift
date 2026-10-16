using System;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    // Caller-owned buffers keep look/reach queries allocation-free and avoid mutable global state.
    public static class SceneTargeting
    {
        public static bool Raycast(WorkerScenePort worker, SceneTarget held, Vector3 direction,
            float distance, int mask, RaycastHit[] hits, out RaycastHit nearest)
        {
            nearest = default;
            int count = Physics.RaycastNonAlloc(worker.Eye.position, direction, hits, distance, mask, QueryTriggerInteraction.Ignore);
            if (count == hits.Length) return false; // An incomplete query cannot establish a clear target.
            float closest = float.PositiveInfinity;
            for (int i = 0; i < count; i++)
            {
                if (Ignored(worker, held, hits[i].collider) || hits[i].distance >= closest) continue;
                closest = hits[i].distance; nearest = hits[i];
            }
            return nearest.collider != null;
        }

        public static bool CanReach(WorkerScenePort worker, SceneTarget held, SceneTarget target, int mask, RaycastHit[] hits)
        {
            Vector3 delta = target.Contact.position - worker.Eye.position;
            float distance = delta.magnitude;
            if (!float.IsFinite(distance) || !float.IsFinite(target.Reach) || distance > target.Reach) return false;
            if (distance == 0) return true;
            int count = Physics.RaycastNonAlloc(worker.Eye.position, delta / distance, hits, distance, mask, QueryTriggerInteraction.Ignore);
            if (count == hits.Length) return false;
            for (int i = 0; i < count; i++)
                if (!Ignored(worker, held, hits[i].collider) && hits[i].collider.GetComponentInParent<SceneTarget>() != target) return false;
            return true;
        }

        private static bool Ignored(WorkerScenePort worker, SceneTarget held, Collider shape) =>
            Array.IndexOf(worker.BodyColliders, shape) >= 0 ||
            (held != null && shape.GetComponentInParent<SceneTarget>() == held);
    }
}
