using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Trusted sampled pelvis presence in authored boxes. No trigger, dose integration or health ownership.</summary>
    [DisallowMultipleComponent]
    public sealed class WorkerContaminationZones : MonoBehaviour
    {
        private sealed class Area
        {
            internal Guid Source; internal Transform Frame; internal Vector3 Half;
            internal string Label;
        }
        private sealed class Binding
        {
            internal Guid Worker; internal WorkerBodyRig Rig; internal WorkerContaminationFeed[] Feeds;
            internal string Cue = "Outside marked exposure/wash areas";
        }
        private WorldSession world;
        private Guid epoch;
        private Action pump;
        private Action<Exception> failure;
        private readonly List<Area> areas = new List<Area>();
        private readonly List<Binding> workers = new List<Binding>();
        private bool initialized, sealedBindings, active;

        public void Initialize(WorldSession session, Action sampleClock, Action<Exception> onFailure)
        {
            if (initialized || session == null || session.View.Phase != WorldPhase.Setup)
                throw new InvalidOperationException("Compose one contamination sampler before world startup.");
            if (sampleClock == null) throw new ArgumentNullException(nameof(sampleClock));
            if (onFailure == null) throw new ArgumentNullException(nameof(onFailure));
            initialized = true; world = session; epoch = session.Epoch; pump = sampleClock; failure = onFailure;
        }
        public void BindArea(Guid source, Transform frame, Vector3 halfExtents, string label)
        {
            RequireSetup();
            if (source == Guid.Empty || frame == null || !ValidHalf(halfExtents) || string.IsNullOrWhiteSpace(label) || label.Length > 64 || areas.Count >= 8)
                throw new ArgumentException("Bind a bounded, named authored source box.");
            foreach (var area in areas) if (area.Source == source || area.Frame == frame) throw new InvalidOperationException("Duplicate contamination source area.");
            ValidateFrame(frame);
            areas.Add(new Area { Source = source, Frame = frame, Half = halfExtents, Label = label });
        }
        public void BindWorker(Guid actor, WorkerBodyRig rig)
        {
            RequireSetup();
            if (actor == Guid.Empty || rig == null || rig.Actor != actor || rig.Epoch != epoch || world.GetWorker(actor) == null || workers.Count >= 4)
                throw new ArgumentException("Bind a current, explicitly identified worker rig.");
            foreach (var worker in workers) if (worker.Worker == actor || worker.Rig == rig) throw new InvalidOperationException("Duplicate contamination worker binding.");
            workers.Add(new Binding { Worker = actor, Rig = rig });
        }
        public void Seal()
        {
            RequireSetup();
            if (areas.Count == 0 || workers.Count == 0) throw new InvalidOperationException("Contamination sampling needs explicit sources and workers.");
            areas.Sort((a, b) => a.Source.CompareTo(b.Source));
            workers.Sort((a, b) => a.Worker.CompareTo(b.Worker));
            foreach (var worker in workers)
            {
                worker.Feeds = new WorkerContaminationFeed[areas.Count];
                for (int i = 0; i < areas.Count; i++) worker.Feeds[i] = new WorkerContaminationFeed(world, worker.Worker, areas[i].Source);
            }
            sealedBindings = true;
        }
        public void Activate()
        {
            if (!sealedBindings || active || world == null || world.Epoch != epoch || world.View.Phase != WorldPhase.Running)
                throw new InvalidOperationException("Activate prepared contamination sampling after world startup.");
            active = true;
        }
        public string Describe(Guid actor)
        {
            foreach (var worker in workers) if (worker.Worker == actor) return worker.Cue;
            return "No active exposure/wash sampling";
        }
        private void FixedUpdate() => Sample();
        public void Sample()
        {
            if (!active) return;
            try
            {
                pump();
                if (world == null || world.Epoch != epoch) throw new InvalidOperationException("Contamination sampler lost its world binding.");
                if (world.View.Phase != WorldPhase.Running && world.View.Phase != WorldPhase.Paused) { Shutdown(); return; }
                if (world.View.Phase == WorldPhase.Paused) return;
                foreach (var area in areas) ValidateFrame(area.Frame);
                for (int w = workers.Count - 1; w >= 0; w--)
                {
                    var worker = workers[w];
                    if (world.GetWorker(worker.Worker) == null) { workers.RemoveAt(w); continue; }
                    if (worker.Rig == null || worker.Rig.Epoch != epoch || worker.Rig.Actor != worker.Worker || !worker.Rig.Available)
                        throw new InvalidOperationException("A live contamination worker lost its explicit physical rig.");
                    // Rigidbody.position follows down/dragged bodies without relying on an interpolated visual root.
                    Vector3 pelvis = worker.Rig.Pelvis.position;
                    if (!Finite(pelvis)) throw new InvalidOperationException("The contamination pelvis sample is nonfinite.");
                    worker.Cue = "Outside marked exposure/wash areas";
                    for (int i = 0; i < areas.Count; i++)
                    {
                        var area = areas[i]; Vector3 point = area.Frame.InverseTransformPoint(pelvis);
                        if (!Finite(point)) throw new InvalidOperationException("The authored contamination box transform is invalid.");
                        if (Mathf.Abs(point.x) > area.Half.x || Mathf.Abs(point.y) > area.Half.y || Mathf.Abs(point.z) > area.Half.z) continue;
                        worker.Cue = worker.Cue == "Outside marked exposure/wash areas" ? area.Label : worker.Cue + " + " + area.Label;
                        worker.Feeds[i].ObserveIfDue();
                    }
                }
            }
            catch (Exception exception) { Fail(exception); }
        }
        private void RequireSetup()
        {
            if (world == null || world.View.Phase != WorldPhase.Setup || sealedBindings)
                throw new InvalidOperationException("Contamination bindings are setup-only and close at Seal.");
        }
        private static void ValidateFrame(Transform frame)
        {
            if (frame == null || !frame.gameObject.activeInHierarchy || !Finite(frame.position))
                throw new InvalidOperationException("An authored contamination area lost its live frame.");
            // Unit local scales throughout the hierarchy exclude reflection, singular frames and shear.
            for (Transform current = frame; current != null; current = current.parent)
                if (!Finite(current.localScale) || Mathf.Abs(current.localScale.x - 1) > 0.0001f ||
                    Mathf.Abs(current.localScale.y - 1) > 0.0001f || Mathf.Abs(current.localScale.z - 1) > 0.0001f)
                    throw new InvalidOperationException("Contamination area frames require unit-scale hierarchies.");
        }
        private static bool ValidHalf(Vector3 half) => Finite(half) && half.x > 0 && half.y > 0 && half.z > 0;
        private static bool Finite(Vector3 point) => !float.IsNaN(point.x) && !float.IsInfinity(point.x) &&
            !float.IsNaN(point.y) && !float.IsInfinity(point.y) && !float.IsNaN(point.z) && !float.IsInfinity(point.z);
        private void Fail(Exception exception)
        {
            var report = failure; Shutdown(); report?.Invoke(exception);
        }
        public void Shutdown()
        {
            active = false; areas.Clear(); workers.Clear(); world = null; pump = null; failure = null;
        }
        private void OnDisable()
        {
            if (active && world != null && (world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused))
                Fail(new InvalidOperationException("The live contamination area sampler was disabled."));
            else Shutdown();
        }
        private void OnDestroy() => Shutdown();
    }
}
