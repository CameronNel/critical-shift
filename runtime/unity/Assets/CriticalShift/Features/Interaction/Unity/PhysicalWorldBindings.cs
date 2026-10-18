using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>World-scoped physical references and reconciliation. Logical custody always comes from WorldSession.</summary>
    internal sealed class PhysicalWorldBindings
    {
        private readonly WorldSession world;
        private readonly Dictionary<Guid, CarryBodyBinding> bodies = new Dictionary<Guid, CarryBodyBinding>();
        private readonly Dictionary<Guid, Transform> slots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, Transform> carryTargets = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, Transform> actorRoots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, CartGripBinding> handles = new Dictionary<Guid, CartGripBinding>();
        internal int Count => bodies.Count + handles.Count;
        internal PhysicalWorldBindings(WorldSession session) => world = session ?? throw new ArgumentNullException(nameof(session));

        internal void BindBody(Guid id, Rigidbody body, float massPerUnit)
        {
            ValidateBodyIdentity(id, body);
            var binding = new CarryBodyBinding(id, body, massPerUnit);
            binding.ApplyMaterialMass(world.Production.GetBatch(id)); bodies.Add(id, binding);
        }

        private void ValidateBodyIdentity(Guid id, Rigidbody body)
        {
            if (body == null || bodies.ContainsKey(id) || handles.ContainsKey(id)) throw new InvalidOperationException("Duplicate or missing physical body binding.");
            if (world.GetObject(id) == null) throw new InvalidOperationException("Register the logical object before its physical body.");
            foreach (var binding in bodies.Values)
                if (binding.Body == body) throw new InvalidOperationException("A Rigidbody may serve only one logical physical entity.");
            foreach (var binding in handles.Values)
                if (binding.Body == body) throw new InvalidOperationException("Cart force ownership cannot overlap a carry-body binding.");
        }

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
            carryTargets.Add(actor, target);
        }

        internal bool HasCarryTarget(Guid actor) => carryTargets.ContainsKey(actor);

        internal IEnumerable<Guid> ClaimedBy(Guid actor)
        {
            foreach (var binding in bodies.Values)
                if (world.GetObject(binding.Id)?.HolderId == actor) yield return binding.Id;
            foreach (var handle in handles.Values)
                if (world.GetObject(handle.Id)?.HolderId == actor) yield return handle.Id;
        }

        internal Guid HeldObject(Guid actor)
        {
            foreach (Guid id in ClaimedBy(actor)) return id;
            return Guid.Empty;
        }

        internal float CarriedMass(Guid actor)
        {
            Guid held = HeldObject(actor);
            return held != Guid.Empty && bodies.TryGetValue(held, out var binding) && binding.Body != null ? binding.Body.mass : 0;
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

        internal bool MayIgnoreForSight(Guid actor, Guid target, Rigidbody body)
        {
            foreach (var binding in bodies.Values)
            {
                if (binding.Body != body) continue;
                var state = world.GetObject(binding.Id);
                return state != null && (state.HolderId == actor || state.SlotId == target);
            }
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
            bool running = world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused;
            bool dropped = false;
            foreach (var binding in bodies.Values)
            {
                var state = running ? world.GetObject(binding.Id) : null;
                if (state == null || state.IsRetired) { binding.Release(); continue; }
                if (binding.Body == null || !binding.Body.gameObject.activeInHierarchy)
                    throw new InvalidOperationException("A registered physical body was destroyed or disabled.");
                if (state.SlotId.HasValue)
                {
                    if (!slots.TryGetValue(state.SlotId.Value, out var slot) || slot == null || !slot.gameObject.activeInHierarchy)
                        throw new InvalidOperationException("An occupied logical slot has no active physical binding.");
                    binding.Place(state.SlotId.Value, slot);
                }
                else if (state.HolderId.HasValue)
                {
                    if (!carryTargets.TryGetValue(state.HolderId.Value, out var target) || target == null ||
                        !target.gameObject.activeInHierarchy || (applyForces && !binding.Follow(state, target, deltaSeconds)))
                    {
                        world.ReportAttachmentFailure(world.Epoch, binding.Id, state.LeaseGeneration);
                        binding.Release(); dropped = true;
                    }
                }
                else binding.Release();
            }
            foreach (var handle in handles.Values)
            {
                var state = running ? world.GetObject(handle.Id) : null;
                if (state == null || state.IsRetired) continue;
                if (handle.Body == null || !handle.Body.gameObject.activeInHierarchy)
                    throw new InvalidOperationException("A registered cart-handle body was destroyed or disabled.");
                if (state.HolderId.HasValue && (!actorRoots.TryGetValue(state.HolderId.Value, out var root) || !handle.CanMaintain(root)))
                {
                    world.ReportAttachmentFailure(world.Epoch, handle.Id, state.LeaseGeneration); dropped = true;
                }
            }
            return dropped;
        }

        internal void Clear()
        {
            foreach (var binding in bodies.Values) binding.Release();
            bodies.Clear(); slots.Clear(); carryTargets.Clear(); handles.Clear(); actorRoots.Clear();
        }
    }
}
