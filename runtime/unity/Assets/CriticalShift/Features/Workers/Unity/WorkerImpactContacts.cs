using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>Bounded host contact observations for explicitly registered cart and heavy falling-body hazards.</summary>
    [DisallowMultipleComponent]
    public sealed class WorkerImpactContacts : MonoBehaviour
    {
        private const float FallingMinimumMass = 20, FallingSpeed = 2.2f, CartSpeed = 1.8f;
        private sealed class Source
        {
            internal Guid Id; internal Rigidbody Body; internal Vector3 PreviousVelocity;
            internal bool Falling; internal Func<bool> Eligible;
            internal bool ContactLatched;
        }
        private readonly List<Source> sources = new List<Source>();
        private readonly Collider[] overlaps = new Collider[32];
        private CharacterController controller;
        private Func<WorkerView> readWorker;
        private Func<bool> running;
        private Func<Vector3> readWorkerVelocity;
        private Func<Guid, Vector3, Vector3, WorkerStatus> observe;
        private Action<Exception> failure;
        private bool active;

        public void Initialize(CharacterController walkingController, Func<WorkerView> worker, Func<bool> simulationRunning,
            Func<Vector3> workerVelocity, Func<Guid, Vector3, Vector3, WorkerStatus> report, Action<Exception> onFailure)
        {
            if (controller != null || walkingController == null) throw new InvalidOperationException("Bind one worker contact observer.");
            if (worker == null) throw new ArgumentNullException(nameof(worker));
            if (simulationRunning == null) throw new ArgumentNullException(nameof(simulationRunning));
            if (workerVelocity == null) throw new ArgumentNullException(nameof(workerVelocity));
            if (report == null) throw new ArgumentNullException(nameof(report));
            if (onFailure == null) throw new ArgumentNullException(nameof(onFailure));
            controller = walkingController; readWorker = worker; running = simulationRunning;
            readWorkerVelocity = workerVelocity; observe = report; failure = onFailure;
        }

        public void BindHazard(Guid id, Rigidbody body) => BindSource(id, body, false, null);
        public void BindFallingHazard(Guid id, Rigidbody body, Func<bool> eligible) =>
            BindSource(id, body, true, eligible ?? throw new ArgumentNullException(nameof(eligible)));

        private void BindSource(Guid id, Rigidbody body, bool falling, Func<bool> eligible)
        {
            if (active || controller == null || id == Guid.Empty || body == null || body.isKinematic || sources.Count >= 8)
                throw new InvalidOperationException("Bind bounded dynamic hazard bodies before activating contact sampling.");
            foreach (var source in sources)
                if (source.Id == id || source.Body == body) throw new InvalidOperationException("Duplicate physical hazard source.");
            sources.Add(new Source { Id = id, Body = body, Falling = falling, Eligible = eligible });
        }

        public void Activate()
        {
            if (active || controller == null || sources.Count == 0) throw new InvalidOperationException("Contact sampling needs explicit hazard bindings.");
            active = true;
        }

        private void FixedUpdate()
        {
            if (!active) return;
            try
            {
                if (!running() || readWorker()?.PhysicallyUpright != true || !controller.enabled)
                {
                    // Excluded-time motion cannot become a fresh impact when gameplay resumes.
                    foreach (var source in sources) source.PreviousVelocity = Vector3.zero;
                    return;
                }
                Vector3 center = controller.transform.TransformPoint(controller.center);
                float half = Mathf.Max(0, controller.height * 0.5f - controller.radius);
                int count = Physics.OverlapCapsuleNonAlloc(center + Vector3.up * half, center - Vector3.up * half,
                    controller.radius + 0.04f, overlaps, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
                if (count == overlaps.Length) throw new InvalidOperationException("Worker impact observation bounds were saturated.");
                Vector3 workerVelocity = readWorkerVelocity();
                foreach (var source in sources)
                {
                    if (source.Body == null || !source.Body.gameObject.activeInHierarchy)
                        throw new InvalidOperationException("A registered physical hazard body was lost.");
                    Collider contact = null;
                    for (int i = 0; i < count; i++)
                        if (overlaps[i] != null && overlaps[i].attachedRigidbody == source.Body) { contact = overlaps[i]; break; }
                    Vector3 current = source.Falling ? source.Body.linearVelocity : source.Body.GetPointVelocity(center);
                    if (source.Falling && (source.Body.isKinematic || source.Body.mass < FallingMinimumMass || !source.Eligible()))
                    {
                        if (contact == null) source.ContactLatched = false;
                        // A held/slotted/light source cannot lend its velocity to a later free-body observation.
                        source.PreviousVelocity = Vector3.zero; continue;
                    }
                    if (contact == null) source.ContactLatched = false;
                    else if (!source.ContactLatched)
                    {
                        Vector3 point = contact.ClosestPoint(center);
                        Vector3 towardWorker = source.Falling ? center - point : Vector3.ProjectOnPlane(center - point, Vector3.up);
                        if (towardWorker.sqrMagnitude < 0.0001f)
                            towardWorker = source.Falling ? center - source.Body.worldCenterOfMass :
                                Vector3.ProjectOnPlane(center - source.Body.worldCenterOfMass, Vector3.up);
                        towardWorker.Normalize();
                        float closing = Mathf.Max(Vector3.Dot(current - workerVelocity, towardWorker),
                            Vector3.Dot(source.PreviousVelocity - workerVelocity, towardWorker));
                        float sourceSpeed = source.Falling ? Mathf.Max(0, Mathf.Max(-current.y, -source.PreviousVelocity.y)) :
                            Mathf.Max(Vector3.ProjectOnPlane(current, Vector3.up).magnitude,
                                Vector3.ProjectOnPlane(source.PreviousVelocity, Vector3.up).magnitude);
                        float threshold = source.Falling ? FallingSpeed : CartSpeed;
                        // A worker walking into a stationary source cannot invent source motion.
                        if (closing >= threshold && sourceSpeed >= threshold)
                        {
                            Vector3 impulse = (towardWorker + Vector3.up * 0.12f) * Mathf.Min(55, source.Body.mass * closing * 0.3f);
                            var status = observe(source.Id, impulse, point);
                            if (status == WorkerStatus.Applied) source.ContactLatched = true;
                        }
                    }
                    source.PreviousVelocity = current;
                }
            }
            catch (Exception exception) { active = false; failure(exception); }
        }

        private void OnDisable()
        {
            bool unexpected = active && readWorker != null && readWorker() != null;
            active = false;
            if (unexpected) failure?.Invoke(new InvalidOperationException("The live worker impact observer was disabled."));
        }
    }
}
