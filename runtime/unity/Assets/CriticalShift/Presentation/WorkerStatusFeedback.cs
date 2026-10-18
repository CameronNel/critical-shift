using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Derived debug status cue at an explicitly supplied physical grip; no health or claim writes.</summary>
    public sealed class WorkerStatusFeedback : MonoBehaviour
    {
        private LocalCommandPort queries;
        private Guid actor;
        private Renderer marker;
        private Light lamp;
        private Func<Vector3?> point;
        private MaterialPropertyBlock properties;
        public bool Visible { get; private set; }

        public void Initialize(LocalCommandPort read, Guid worker, Renderer statusMarker, Light statusLamp, Func<Vector3?> physicalPoint)
        {
            if (queries != null || read == null || read.GetWorker(worker) == null || statusMarker == null || statusLamp == null ||
                statusMarker.GetComponentsInChildren<Rigidbody>().Length != 0 || statusLamp.transform != statusMarker.transform)
                throw new ArgumentException("Bind one worker view, non-physical status marker, colocated light and physical-point query.");
            foreach (var collider in statusMarker.GetComponentsInChildren<Collider>())
                if (collider.enabled) throw new ArgumentException("Worker status presentation cannot add contact shapes.");
            queries = read; actor = worker; marker = statusMarker; lamp = statusLamp;
            point = physicalPoint ?? throw new ArgumentNullException(nameof(physicalPoint));
            properties = new MaterialPropertyBlock(); Hide();
        }

        private void LateUpdate()
        {
            if (queries == null) return;
            if (marker == null || lamp == null)
            { enabled = false; throw new InvalidOperationException("A bound worker status presentation part was lost."); }
            var world = queries.World; var worker = queries.GetWorker(actor);
            if ((world.Phase != WorldPhase.Running && world.Phase != WorldPhase.Paused) || worker == null || worker.Pose == WorkerPose.Upright)
            { Hide(); return; }
            var position = point();
            if (!position.HasValue) { Hide(); return; }
            Vector3 anchor = position.Value;
            if (float.IsNaN(anchor.x) || float.IsNaN(anchor.y) || float.IsNaN(anchor.z) ||
                float.IsInfinity(anchor.x) || float.IsInfinity(anchor.y) || float.IsInfinity(anchor.z))
            { enabled = false; throw new InvalidOperationException("A worker status cue received a non-finite physical point."); }
            bool recovering = worker.Pose == WorkerPose.Recovering;
            Color color = recovering ? new Color(0.12f, 0.65f, 1) : worker.Awareness == WorkerAwareness.Unconscious ?
                new Color(1, 0.08f, 0.04f) : new Color(1, 0.6f, 0.12f);
            float strength = recovering ? 0.6f : 0.3f + 0.7f * (0.5f + 0.5f * Mathf.Sin(world.ElapsedMilliseconds * 0.006f));
            marker.transform.position = anchor + Vector3.up * 0.5f;
            marker.GetPropertyBlock(properties); properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            properties.SetColor("_EmissionColor", color * strength * 2); marker.SetPropertyBlock(properties);
            marker.enabled = true; lamp.color = color; lamp.intensity = strength * 0.8f; Visible = true;
        }

        private void Hide() { Visible = false; if (marker != null) marker.enabled = false; if (lamp != null) lamp.intensity = 0; }
        private void OnDisable() => Hide();
        private void OnDestroy() { Hide(); point = null; queries = null; }
    }
}
