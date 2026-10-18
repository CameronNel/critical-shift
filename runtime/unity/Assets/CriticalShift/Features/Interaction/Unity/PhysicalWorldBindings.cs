using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>World-scoped physical references and reconciliation. Logical custody always comes from WorldSession.</summary>
    internal sealed class PhysicalWorldBindings
    {
        private sealed class CarryTarget
        {
            internal readonly Transform Anchor;
            private readonly Quaternion rest;
            private readonly Vector3 restPosition;
            private Guid entity;
            private long lease;
            private float yaw, pitch, distanceOffset;
            internal CarryTarget(Transform anchor) { Anchor = anchor; rest = anchor.localRotation; restPosition = anchor.localPosition; }
            internal Vector3 AimForward => (Anchor.parent == null ? rest : Anchor.parent.rotation * rest) * Vector3.forward;
            internal void Observe(ObjectClaimView claim)
            {
                if (claim == null || !claim.HolderId.HasValue || claim.LeaseGeneration < 1) { Reset(); return; }
                if (entity == claim.EntityId && lease == claim.LeaseGeneration) return;
                Reset(); entity = claim.EntityId; lease = claim.LeaseGeneration;
            }
            internal void Rotate(Vector2 delta)
            {
                yaw = Mathf.Repeat(yaw + Mathf.Clamp(delta.x, -150, 150) * 0.35f + 180, 360) - 180;
                pitch = Mathf.Clamp(pitch - Mathf.Clamp(delta.y, -150, 150) * 0.35f, -80, 80);
                Anchor.localRotation = rest * Quaternion.Euler(pitch, yaw, 0);
            }
            internal void AdjustDistance(float steps)
            {
                distanceOffset = Mathf.Clamp(distanceOffset - Mathf.Clamp(steps, -10, 10) * 0.15f, -0.75f, 0.75f);
                Anchor.localPosition = restPosition + Vector3.forward * distanceOffset;
            }
            internal void Reset()
            {
                entity = Guid.Empty; lease = 0; yaw = pitch = distanceOffset = 0;
                if (Anchor != null) { Anchor.localRotation = rest; Anchor.localPosition = restPosition; }
            }
        }

        private sealed class DragTarget
        {
            internal readonly Transform Anchor;
            private readonly Vector3 rest;
            private Guid entity;
            private long lease;
            internal bool Raised;
            internal DragTarget(Transform anchor) { Anchor = anchor; rest = anchor.localPosition; }
            internal void Observe(ObjectClaimView claim)
            {
                if (claim == null || !claim.HolderId.HasValue || claim.LeaseGeneration < 1) { Reset(); return; }
                if (entity == claim.EntityId && lease == claim.LeaseGeneration) return;
                Reset(); entity = claim.EntityId; lease = claim.LeaseGeneration;
            }
            internal void Step(float seconds)
            {
                if (Anchor == null) return;
                Vector3 position = Anchor.localPosition;
                position.y = Mathf.MoveTowards(position.y, rest.y + (Raised ? 1.5f : 0), 2.5f * Mathf.Min(seconds, 0.05f));
                Anchor.localPosition = position;
            }
            internal void Reset() { entity = Guid.Empty; lease = 0; Raised = false; if (Anchor != null) Anchor.localPosition = rest; }
        }
        private readonly WorldSession world;
        private readonly Dictionary<Guid, CarryBodyBinding> bodies = new Dictionary<Guid, CarryBodyBinding>();
        private readonly Dictionary<Guid, Transform> slots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, CarryTarget> carryTargets = new Dictionary<Guid, CarryTarget>();
        private readonly Dictionary<Guid, Transform> actorRoots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, CartGripBinding> handles = new Dictionary<Guid, CartGripBinding>();
        private readonly Dictionary<Guid, WorkerDragBinding> workers = new Dictionary<Guid, WorkerDragBinding>();
        private readonly Dictionary<Guid, DragTarget> dragTargets = new Dictionary<Guid, DragTarget>();
        internal int Count => bodies.Count + handles.Count + workers.Count;
        internal PhysicalWorldBindings(WorldSession session) => world = session ?? throw new ArgumentNullException(nameof(session));

        internal void BindBody(Guid id, Rigidbody body, float massPerUnit)
        {
            ValidateBodyIdentity(id, body);
            var binding = new CarryBodyBinding(id, body, massPerUnit);
            binding.ApplyMaterialMass(world.Production.GetBatch(id)); bodies.Add(id, binding);
        }

        private void ValidateBodyIdentity(Guid id, Rigidbody body)
        {
            if (body == null || bodies.ContainsKey(id) || handles.ContainsKey(id) || workers.ContainsKey(id)) throw new InvalidOperationException("Duplicate or missing physical body binding.");
            if (world.GetObject(id) == null) throw new InvalidOperationException("Register the logical object before its physical body.");
            foreach (var binding in bodies.Values)
                if (binding.Body == body) throw new InvalidOperationException("A Rigidbody may serve only one logical physical entity.");
            foreach (var binding in handles.Values)
                if (binding.Body == body) throw new InvalidOperationException("Cart force ownership cannot overlap a carry-body binding.");
            foreach (var binding in workers.Values)
                if (binding.Owns(body)) throw new InvalidOperationException("Worker force ownership cannot overlap another physical entity.");
        }

        internal void BindWorker(Guid id, Guid actor, Rigidbody[] segments,
            Func<ObjectClaimView, Vector3, float, bool> pull, Action release, Func<float> mass, Action<ObjectClaimView, bool> hoist)
        {
            if (world.GetWorkerForBody(id)?.Id != actor || segments == null)
                throw new InvalidOperationException("Register the worker-body linkage before its physical adapter.");
            foreach (var segment in segments) ValidateBodyIdentity(id, segment);
            workers.Add(id, new WorkerDragBinding(id, segments, pull, release, mass, hoist));
        }

        internal void BindDragTarget(Guid actor, Transform target)
        {
            if (target == null || dragTargets.ContainsKey(actor) || world.GetWorker(actor) == null)
                throw new ArgumentException("Bind one explicit drag target for a registered worker.");
            dragTargets.Add(actor, new DragTarget(target));
        }
        internal void SetWorkerHoist(Guid actor, bool raised)
        {
            if (!dragTargets.TryGetValue(actor, out var target)) return;
            Guid held = HeldObject(actor);
            if (held == Guid.Empty || !workers.TryGetValue(held, out var worker)) { target.Reset(); return; }
            var claim = world.GetObject(held);
            if (claim == null || claim.HolderId != actor || world.GetWorkerForBody(held)?.Pose != WorkerPose.Down)
            { target.Reset(); return; }
            target.Observe(claim); target.Raised = raised; worker.Hoist(claim, raised);
        }
        internal bool HasDragTarget(Guid actor) => workers.Count == 0 || dragTargets.ContainsKey(actor);
        internal Vector3? CurrentDragTarget(Guid actor) => workers.ContainsKey(HeldObject(actor)) &&
            dragTargets.TryGetValue(actor, out var target) && target.Anchor != null ? target.Anchor.position : (Vector3?)null;
        internal bool IsWorker(Guid entity) => workers.ContainsKey(entity);

        internal void BindActorRoot(Guid actor, Transform root)
        {
            if (root == null || actorRoots.ContainsKey(actor) || world.GetWorker(actor) == null)
                throw new ArgumentException("Bind one explicit root for a registered worker.");
            actorRoots.Add(actor, root);
        }

        internal void BindHandle(Guid id, Rigidbody body, Transform handle, Transform stand)
        {
            ValidateBodyIdentity(id, body); handles.Add(id, new CartGripBinding(id, body, handle, stand));
        }

        internal bool HasRequiredActorRoot(Guid actor) => handles.Count == 0 || actorRoots.ContainsKey(actor);
        internal bool IsHandle(Guid id) => handles.ContainsKey(id);
        internal bool CanEnterHandle(Guid id, Guid actor) => !handles.TryGetValue(id, out var handle) ||
            (actorRoots.TryGetValue(actor, out var root) && handle.CanEnter(root));
        internal bool IsHandleHeld(Guid actor, Guid id) => handles.TryGetValue(id, out var handle) &&
            world.GetObject(id)?.HolderId == actor && actorRoots.TryGetValue(actor, out var root) && handle.CanMaintain(root);
        internal Vector3? GripStand(Guid actor)
        {
            foreach (var handle in handles.Values)
                if (IsHandleHeld(actor, handle.Id)) return handle.Stand.position;
            return null;
        }

        internal void BindSlot(Guid id, Transform anchor)
        {
            if (id == Guid.Empty || anchor == null || slots.ContainsKey(id))
                throw new ArgumentException("A unique slot identity and explicit anchor are required.");
            if (world.Production.GetMachine(id) == null && world.Reactor.View?.Id != id)
                throw new InvalidOperationException("Register equipment before binding its physical slot.");
            slots.Add(id, anchor);
        }

        internal void BindCarryTarget(Guid actor, Transform target)
        {
            if (actor == Guid.Empty || target == null || carryTargets.ContainsKey(actor))
                throw new ArgumentException("A unique actor and explicit carry target are required.");
            if (world.GetWorker(actor) == null) throw new InvalidOperationException("Register the worker before binding its carry target.");
            foreach (var existing in carryTargets.Values)
                if (existing.Anchor == target) throw new ArgumentException("Each actor needs its own carry target.");
            carryTargets.Add(actor, new CarryTarget(target));
        }

        internal bool RotateHeld(Guid actor, Vector2 delta)
        {
            if (!CurrentPortableTarget(actor, out var target)) return false;
            target.Rotate(delta); return true;
        }
        internal bool AdjustHeldDistance(Guid actor, float steps)
        {
            if (!CurrentPortableTarget(actor, out var target)) return false;
            target.AdjustDistance(steps); return true;
        }
        private bool CurrentPortableTarget(Guid actor, out CarryTarget target)
        {
            target = null;
            if (world.View.Phase != WorldPhase.Running || world.GetWorker(actor)?.CanInteract != true ||
                !carryTargets.TryGetValue(actor, out target) || target.Anchor == null || !target.Anchor.gameObject.activeInHierarchy)
                return false;
            Guid held = HeldObject(actor);
            if (!bodies.ContainsKey(held)) return false;
            target.Observe(world.GetObject(held)); return true;
        }

        internal bool HasCarryTarget(Guid actor) => carryTargets.ContainsKey(actor);
        internal bool IsPortable(Guid entity) => bodies.ContainsKey(entity);

        internal bool ThrowReleased(Guid actor, ObjectClaimView held, ObjectClaimView released)
        {
            if (held == null || released == null || world.View.Phase != WorldPhase.Running || world.GetWorker(actor)?.CanInteract != true ||
                held.Epoch != world.Epoch || released.Epoch != world.Epoch || held.HolderId != actor ||
                held.EntityId != released.EntityId || held.LeaseGeneration != released.LeaseGeneration ||
                released.Revision != held.Revision + 1 || released.HolderId.HasValue || released.SlotId.HasValue || released.IsRetired ||
                !bodies.TryGetValue(held.EntityId, out var body) || !carryTargets.TryGetValue(actor, out var target) ||
                target.Anchor == null || !target.Anchor.gameObject.activeInHierarchy) return false;
            var current = world.GetObject(held.EntityId);
            if (current == null || current.IsRetired || current.HolderId.HasValue || current.SlotId.HasValue ||
                current.LeaseGeneration != released.LeaseGeneration || current.Revision != released.Revision) return false;
            body.Throw(target.AimForward + Vector3.up * 0.15f); return true;
        }

        internal IEnumerable<Guid> ClaimedBy(Guid actor)
        {
            foreach (var binding in bodies.Values)
                if (world.GetObject(binding.Id)?.HolderId == actor) yield return binding.Id;
            foreach (var handle in handles.Values)
                if (world.GetObject(handle.Id)?.HolderId == actor) yield return handle.Id;
            foreach (var worker in workers.Values)
                if (world.GetObject(worker.Id)?.HolderId == actor) yield return worker.Id;
        }

        internal Guid HeldObject(Guid actor)
        {
            foreach (Guid id in ClaimedBy(actor)) return id;
            return Guid.Empty;
        }

        internal float CarriedMass(Guid actor)
        {
            Guid held = HeldObject(actor);
            if (held == Guid.Empty) return 0;
            if (workers.TryGetValue(held, out var worker)) return worker.Mass;
            return bodies.TryGetValue(held, out var binding) && binding.Body != null ? binding.Body.mass : 0;
        }

        internal bool IsFree(Rigidbody body)
        {
            if (body == null || !body.gameObject.activeInHierarchy) return false;
            foreach (var binding in bodies.Values)
            {
                if (binding.Body != body) continue;
                var state = world.GetObject(binding.Id);
                return state != null && !state.IsRetired && !state.HolderId.HasValue && !state.SlotId.HasValue;
            }
            return false;
        }

        internal Rigidbody CargoGroup(Rigidbody body)
        {
            if (IsFree(body)) return body;
            foreach (var worker in workers.Values)
            {
                if (!worker.Owns(body)) continue;
                var claim = world.GetObject(worker.Id);
                var pose = world.GetWorkerForBody(worker.Id)?.Pose;
                return worker.Active && claim != null && !claim.IsRetired && !claim.HolderId.HasValue && !claim.SlotId.HasValue &&
                    (pose == WorkerPose.Down || pose == WorkerPose.Recovering) ? worker.Representative : null;
            }
            return null;
        }

        internal float CargoMass(Rigidbody representative)
        {
            if (representative == null) return 0;
            foreach (var worker in workers.Values)
                if (worker.Representative == representative) return worker.Mass;
            foreach (var body in bodies.Values)
                if (body.Body == representative) return representative.mass;
            throw new InvalidOperationException("Cargo mass was requested for an unregistered physical group.");
        }

        internal bool MayIgnoreForSight(Guid actor, Guid target, Rigidbody body)
        {
            foreach (var binding in bodies.Values)
            {
                if (binding.Body != body) continue;
                var state = world.GetObject(binding.Id);
                return state != null && (state.HolderId == actor || state.SlotId == target);
            }
            foreach (var worker in workers.Values)
                if (worker.Owns(body)) return world.GetObject(worker.Id)?.HolderId == actor;
            return false;
        }

        internal bool CanPlace(Guid entity, Guid slot) => bodies.TryGetValue(entity, out var binding) &&
            slots.TryGetValue(slot, out var anchor) && anchor != null && anchor.gameObject.activeInHierarchy && binding.CanPlace(anchor);

        internal void ApplyMaterialMass(MaterialView batch)
        {
            if (batch != null && bodies.TryGetValue(batch.ContainerId, out var binding)) binding.ApplyMaterialMass(batch);
        }

        internal bool Reconcile(bool applyForces, float deltaSeconds)
        {
            var phase = world.View.Phase;
            bool running = phase == WorldPhase.Running || phase == WorldPhase.Paused;
            bool dropped = ReconcileCarryBodies(running, applyForces, deltaSeconds);
            dropped |= ReconcileHandles(running);
            dropped |= ReconcileWorkers(running, applyForces, deltaSeconds);
            return dropped;
        }

        private bool ReconcileCarryBodies(bool running, bool applyForces, float deltaSeconds)
        {
            bool dropped = false;
            foreach (var pair in carryTargets)
            {
                Guid held = running ? HeldObject(pair.Key) : Guid.Empty;
                pair.Value.Observe(bodies.ContainsKey(held) ? world.GetObject(held) : null);
            }
            foreach (var binding in bodies.Values)
            {
                var state = running ? world.GetObject(binding.Id) : null;
                if (state == null || state.IsRetired) { binding.Release(); continue; }
                if (!binding.Available)
                    throw new InvalidOperationException("A registered portable body lost its required motion or collision binding: " + binding.Id);
                if (state.SlotId.HasValue)
                {
                    if (!slots.TryGetValue(state.SlotId.Value, out var slot) || slot == null || !slot.gameObject.activeInHierarchy)
                        throw new InvalidOperationException("An occupied logical slot has no active physical binding.");
                    binding.Place(state.SlotId.Value, slot);
                }
                else if (state.HolderId.HasValue)
                {
                    if (!carryTargets.TryGetValue(state.HolderId.Value, out var target) || target.Anchor == null ||
                        !target.Anchor.gameObject.activeInHierarchy || (applyForces && !binding.Follow(state, target.Anchor, deltaSeconds)))
                    {
                        world.ReportAttachmentFailure(world.Epoch, binding.Id, state.LeaseGeneration);
                        binding.Release(); target?.Reset(); dropped = true;
                    }
                }
                else binding.Release();
            }
            return dropped;
        }

        private bool ReconcileHandles(bool running)
        {
            bool dropped = false;
            foreach (var handle in handles.Values)
            {
                var state = running ? world.GetObject(handle.Id) : null;
                if (state == null || state.IsRetired) continue;
                if (!handle.Available)
                    throw new InvalidOperationException("A registered cart grip lost its required motion, anchors or contact geometry: " + handle.Id);
                if (state.HolderId.HasValue && (!actorRoots.TryGetValue(state.HolderId.Value, out var root) || !handle.CanMaintain(root)))
                {
                    world.ReportAttachmentFailure(world.Epoch, handle.Id, state.LeaseGeneration); dropped = true;
                }
            }
            return dropped;
        }

        private bool ReconcileWorkers(bool running, bool applyForces, float deltaSeconds)
        {
            bool dropped = false;
            foreach (var pair in dragTargets)
            {
                Guid held = running ? HeldObject(pair.Key) : Guid.Empty;
                if (held == Guid.Empty || !workers.ContainsKey(held)) pair.Value.Reset();
                else
                {
                    pair.Value.Observe(world.GetObject(held));
                    // Reconcile pause without depending on another HUD/input event.
                    if (world.View.Phase != WorldPhase.Running) pair.Value.Raised = false;
                    if (applyForces) pair.Value.Step(deltaSeconds);
                }
            }
            foreach (var worker in workers.Values)
            {
                var state = running ? world.GetObject(worker.Id) : null;
                if (state == null || state.IsRetired) { worker.Release(); continue; }
                if (!worker.Active) throw new InvalidOperationException("A registered worker body lost a physical segment.");
                if (!state.HolderId.HasValue) { worker.Release(); continue; }
                if (world.View.Phase != WorldPhase.Running) worker.Hoist(state, false);
                if (world.GetWorkerForBody(worker.Id)?.Pose != WorkerPose.Down ||
                    !dragTargets.TryGetValue(state.HolderId.Value, out var target) || target.Anchor == null || !target.Anchor.gameObject.activeInHierarchy ||
                    (applyForces && !worker.Follow(state, target.Anchor, deltaSeconds)))
                {
                    world.ReportAttachmentFailure(world.Epoch, worker.Id, state.LeaseGeneration); worker.Release(); dropped = true;
                }
            }
            return dropped;
        }

        internal void Clear()
        {
            foreach (var binding in bodies.Values) binding.Release();
            foreach (var worker in workers.Values) worker.Release();
            foreach (var target in dragTargets.Values) target.Reset();
            foreach (var target in carryTargets.Values) target.Reset();
            bodies.Clear(); slots.Clear(); carryTargets.Clear(); handles.Clear(); actorRoots.Clear(); workers.Clear(); dragTargets.Clear();
        }
    }
}
