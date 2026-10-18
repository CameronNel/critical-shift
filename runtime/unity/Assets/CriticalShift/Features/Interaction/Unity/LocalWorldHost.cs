using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Local fixture host: unscaled clock sampling, command admission and current-state body reconciliation.</summary>
    [DisallowMultipleComponent]
    public sealed class LocalWorldHost : MonoBehaviour
    {
        private readonly Dictionary<Guid, CarryBodyBinding> bodies = new Dictionary<Guid, CarryBodyBinding>();
        private readonly Dictionary<Guid, Transform> slots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, Transform> carryTargets = new Dictionary<Guid, Transform>();
        private WorldSession world;
        private LocalCommandPort commands;
        private Guid localActor;
        private Func<double> readClock;
        private double realOrigin, lastClock;
        private long hostOrigin, renewAt;
        private bool active, stopped;
        private Func<Guid> pickTarget;
        private Func<Guid, string> targetName;
        private Guid focused;
        public string LastAction { get; private set; } = "Preparing local fixture";
        public string FocusHint { get; private set; } = "Look at a nearby crate or machine";
        public WorldSession World => world;
        public LocalCommandPort Commands => commands;
        public int BoundBodyCount => bodies.Count;

        public void Initialize(WorldSession session, LocalCommandPort sender, Guid actor, Func<double> clock = null)
        {
            if (world != null || session == null || sender == null || session.View.Phase != WorldPhase.Setup ||
                sender.World.Epoch != session.Epoch || actor == Guid.Empty || sender.ActorId != actor)
                throw new InvalidOperationException("Initialize exactly once with one setup-world and its local sender.");
            world = session; commands = sender; localActor = actor;
            readClock = clock ?? (() => Time.realtimeSinceStartupAsDouble);
        }

        public void BindBody(Guid id, Rigidbody body, float physicalMassPerUnit = 0)
        {
            RequireSetup();
            if (bodies.ContainsKey(id)) throw new InvalidOperationException("Duplicate portable body binding.");
            var binding = new CarryBodyBinding(id, body, physicalMassPerUnit);
            binding.ApplyMaterialMass(world.Production.GetBatch(id)); bodies.Add(id, binding);
        }

        public void BindSlot(Guid id, Transform anchor)
        {
            RequireSetup();
            if (id == Guid.Empty || anchor == null || slots.ContainsKey(id))
                throw new ArgumentException("A unique slot identity and explicit anchor are required.");
            slots.Add(id, anchor);
        }

        public void BindCarryTarget(Guid actor, Transform target)
        {
            RequireSetup();
            if (actor == Guid.Empty || target == null || carryTargets.ContainsKey(actor))
                throw new ArgumentException("A unique actor and explicit carry target are required.");
            carryTargets.Add(actor, target);
        }

        public void BindFocus(Func<Guid> query, Func<Guid, string> displayName)
        {
            RequireSetup();
            if (pickTarget != null) throw new InvalidOperationException("Focus observations are already bound.");
            pickTarget = query ?? throw new ArgumentNullException(nameof(query));
            targetName = displayName ?? throw new ArgumentNullException(nameof(displayName));
        }

        public void Activate()
        {
            RequireSetup();
            if (!carryTargets.ContainsKey(localActor)) throw new InvalidOperationException("Local carry target is missing.");
            realOrigin = readClock();
            if (double.IsNaN(realOrigin) || double.IsInfinity(realOrigin) || realOrigin < 0)
                throw new InvalidOperationException("The host clock must provide finite nonnegative seconds.");
            lastClock = realOrigin;
            world.Start();
            hostOrigin = world.View.HostMilliseconds;
            active = true; LastAction = "Local shift started";
        }

        private void RequireSetup()
        {
            if (world == null || active || stopped || world.View.Phase != WorldPhase.Setup)
                throw new InvalidOperationException("Physical composition is setup-only.");
        }

        private void Update()
        {
            if (!active || stopped) return;
            try
            {
                Pump();
                if (world.View.HostMilliseconds >= renewAt)
                {
                    renewAt = checked(world.View.HostMilliseconds + 800);
                    foreach (var binding in bodies.Values)
                    {
                        var state = world.GetObject(binding.Id);
                        if (state?.HolderId == localActor) commands.Renew(binding.Id);
                    }
                }
                Reconcile(false);
                RefreshFocus();
            }
            catch (Exception exception) { StopAfterFailure(exception); }
        }

        private void FixedUpdate()
        {
            if (!active || stopped) return;
            try { Pump(); Reconcile(true); }
            catch (Exception exception) { StopAfterFailure(exception); }
        }

        public void Pump()
        {
            if (!active || stopped) return;
            double now = readClock();
            if (double.IsNaN(now) || double.IsInfinity(now) || now < lastClock)
                throw new InvalidOperationException("The host clock moved backwards or returned a non-finite value.");
            lastClock = now;
            double elapsed = now - realOrigin;
            long sample = checked(hostOrigin + (long)Math.Floor(elapsed * 1000));
            if (sample > world.View.HostMilliseconds)
            {
                var result = world.AdvanceTo(sample);
                foreach (var change in result.ProductionChanges)
                    if (change.Output != null && bodies.TryGetValue(change.Output.ContainerId, out var binding))
                        binding.ApplyMaterialMass(change.Output);
            }
        }

        public bool IsBodyFree(Rigidbody body)
        {
            if (!active || stopped || (world.View.Phase != WorldPhase.Running && world.View.Phase != WorldPhase.Paused)) return false;
            foreach (var binding in bodies.Values)
            {
                if (binding.Body != body) continue;
                var state = world.GetObject(binding.Id);
                return state != null && !state.IsRetired && !state.HolderId.HasValue && !state.SlotId.HasValue;
            }
            return false; // Unknown bodies never gain conveyor authority by default.
        }

        public bool MayIgnoreForSight(Guid actor, Guid target, Rigidbody body)
        {
            if (world == null || stopped) return false;
            foreach (var binding in bodies.Values)
            {
                if (binding.Body != body) continue;
                var state = world.GetObject(binding.Id);
                return state != null && (state.HolderId == actor || state.SlotId == target);
            }
            return false;
        }

        public void Grab(Guid id) => RunCommand(() => commands.Grab(id));
        public void Release(Guid id) => RunCommand(() => commands.Release(id));
        public void ReplayLast() => RunCommand(() => commands.ReplayLast());

        public void TransferFocused()
        {
            if (!PrepareFocused()) return;
            Guid held = HeldObject();
            var machine = world.Production.GetMachine(focused);
            var reactor = world.Reactor.View;
            if (machine != null)
            {
                OperateMachine(focused, held != Guid.Empty ? ProductionAction.Insert : ProductionAction.Eject, held, false, false);
            }
            else if (reactor != null && reactor.Id == focused)
            {
                OperateReactor(focused, held != Guid.Empty ? ReactorAction.Insert : ReactorAction.Eject, held, false);
            }
            else Grab(focused);
        }

        public void DropHeld()
        {
            Guid held = HeldObject();
            if (held != Guid.Empty) Release(held); else LastAction = "You are not holding a crate";
        }

        public void StartFocused()
        {
            if (!PrepareFocused()) return;
            if (world.Production.GetMachine(focused) != null) OperateMachine(focused, ProductionAction.Start, Guid.Empty, false, false);
            else if (world.Reactor.View?.Id == focused) OperateReactor(focused, ReactorAction.Start, Guid.Empty, false);
        }

        public void ToggleFocusedPower()
        {
            if (!PrepareFocused()) return;
            var machine = world.Production.GetMachine(focused);
            if (machine != null) OperateMachine(focused, ProductionAction.SetPower, Guid.Empty, false, !machine.Powered);
            else if (world.Reactor.View?.Id == focused)
                OperateReactor(focused, ReactorAction.SetCooling, Guid.Empty, !world.Reactor.View.Cooling);
        }

        private Guid HeldObject()
        {
            if (world == null || stopped) return Guid.Empty;
            foreach (var binding in bodies.Values)
                if (world.GetObject(binding.Id)?.HolderId == localActor) return binding.Id;
            return Guid.Empty;
        }

        public float CarriedPhysicalMass()
        {
            Guid held = HeldObject();
            return held != Guid.Empty && bodies.TryGetValue(held, out var binding) && binding.Body != null ? binding.Body.mass : 0;
        }

        private bool PrepareFocused()
        {
            if (!active || stopped) return false;
            if (world.View.Phase != WorldPhase.Running)
            {
                LastAction = world.View.Phase == WorldPhase.Paused ? "Resume the process clock before transferring or starting equipment" : "The shift has ended; restart the fixture";
                return false;
            }
            try { Pump(); Physics.SyncTransforms(); RefreshFocus(); }
            catch (Exception exception) { StopAfterFailure(exception); return false; }
            if (focused != Guid.Empty) return true;
            LastAction = "Look directly at a nearby crate or machine"; return false;
        }

        private void RefreshFocus()
        {
            if (world.View.Phase != WorldPhase.Running && world.View.Phase != WorldPhase.Paused)
            { focused = Guid.Empty; FocusHint = "Shift ended · restart the fixture"; return; }
            focused = pickTarget == null ? Guid.Empty : pickTarget();
            var custody = world.GetObject(focused);
            if (custody?.SlotId != null) focused = custody.SlotId.Value;
            if (focused == Guid.Empty) { FocusHint = "Look at a nearby crate or machine"; return; }
            bool equipment = world.Production.GetMachine(focused) != null || world.Reactor.View?.Id == focused;
            FocusHint = (targetName == null ? "Target" : targetName(focused)) +
                (equipment ? " | E transfer · F power/cooling · R start" : " | E grab · G drop");
        }

        public void OperateMachine(Guid id, ProductionAction action, Guid container, bool bypass, bool powered)
        {
            if (action == ProductionAction.Insert && !CanPlace(container, id)) return;
            RunCommand(() => commands.OperateMachine(id, action, container, bypass, powered));
        }

        public void OperateReactor(Guid id, ReactorAction action, Guid container, bool cooling)
        {
            if (action == ReactorAction.Insert && !CanPlace(container, id)) return;
            RunCommand(() => commands.OperateReactor(id, action, container, cooling));
        }

        private bool CanPlace(Guid entity, Guid slot)
        {
            Physics.SyncTransforms();
            if (!bodies.TryGetValue(entity, out var binding) || !slots.TryGetValue(slot, out var anchor) ||
                anchor == null || !binding.CanPlace(anchor))
            {
                LastAction = "The loading position is blocked or unavailable";
                return false;
            }
            return true;
        }

        private void RunCommand(Func<InteractionReply> operation)
        {
            if (!active || stopped) return;
            try
            {
                Pump();
                Physics.SyncTransforms();
                var reply = operation();
                LastAction = reply.Production != null ? reply.Production.Status.ToString() :
                    reply.Reactor != null ? reply.Reactor.Status.ToString() : reply.Status.ToString();
                if (reply.IsReplay) LastAction += " (previous result; no repeated effect)";
                Reconcile(false);
            }
            catch (Exception exception) { StopAfterFailure(exception); }
        }

        private void Reconcile(bool applyForces)
        {
            bool running = world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused;
            foreach (var binding in bodies.Values)
            {
                var state = running ? world.GetObject(binding.Id) : null;
                if (state == null || state.IsRetired) { binding.Release(); continue; }
                if (binding.Body == null) throw new InvalidOperationException("A registered physical body was destroyed.");
                if (state.SlotId.HasValue)
                {
                    if (!slots.TryGetValue(state.SlotId.Value, out var slot) || slot == null)
                        throw new InvalidOperationException("An occupied logical slot has no physical binding.");
                    binding.Place(state.SlotId.Value, slot);
                }
                else if (state.HolderId.HasValue)
                {
                    if (!carryTargets.TryGetValue(state.HolderId.Value, out var target) || target == null ||
                        (applyForces && !binding.Follow(state, target, Time.fixedDeltaTime)))
                    {
                        world.ReportAttachmentFailure(world.Epoch, binding.Id, state.LeaseGeneration);
                        binding.Release(); LastAction = "Dropped: the held object was obstructed";
                    }
                }
                else binding.Release();
            }
        }

        public void ToggleClockPause()
        {
            if (!active || stopped) return;
            try
            {
                Pump();
                LastAction = (world.View.Phase == WorldPhase.Paused ? world.Resume(world.Epoch) : world.Pause(world.Epoch)).ToString();
            }
            catch (Exception exception) { StopAfterFailure(exception); }
        }

        private void StopAfterFailure(Exception exception)
        {
            LastAction = "Fixture stopped after an error; inspect the Unity log";
            Shutdown(); Debug.LogException(exception, this);
        }

        public void Shutdown()
        {
            if (stopped) return;
            stopped = true; active = false;
            if (world != null) world.Stop();
            foreach (var binding in bodies.Values) binding.Release();
            bodies.Clear(); slots.Clear(); carryTargets.Clear(); focused = Guid.Empty; pickTarget = null; targetName = null;
        }

        private void OnDisable() => Shutdown();
        private void OnDestroy() => Shutdown();
    }
}
