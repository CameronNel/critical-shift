using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Local fixture host: unscaled clock sampling, command admission and current-state body reconciliation.</summary>
    [DisallowMultipleComponent]
    public sealed class LocalWorldHost : MonoBehaviour
    {
        private PhysicalWorldBindings bindings;
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
        public int BoundBodyCount => bindings == null ? 0 : bindings.Count;

        public void Initialize(WorldSession session, LocalCommandPort sender, Guid actor, Func<double> clock = null)
        {
            if (world != null || session == null || sender == null || session.View.Phase != WorldPhase.Setup ||
                sender.World.Epoch != session.Epoch || actor == Guid.Empty || sender.ActorId != actor)
                throw new InvalidOperationException("Initialize exactly once with one setup-world and its local sender.");
            world = session; commands = sender; localActor = actor;
            bindings = new PhysicalWorldBindings(session);
            readClock = clock ?? (() => Time.realtimeSinceStartupAsDouble);
        }

        public void BindBody(Guid id, Rigidbody body, float physicalMassPerUnit = 0)
        {
            RequireSetup();
            bindings.BindBody(id, body, physicalMassPerUnit);
        }

        public void BindSlot(Guid id, Transform anchor)
        {
            RequireSetup();
            bindings.BindSlot(id, anchor);
        }

        public void BindCarryTarget(Guid actor, Transform target)
        {
            RequireSetup();
            bindings.BindCarryTarget(actor, target);
        }

        public void BindActorRoot(Guid actor, Transform root) { RequireSetup(); bindings.BindActorRoot(actor, root); }
        public void BindCartHandle(Guid id, Rigidbody body, Transform handle, Transform stand)
        { RequireSetup(); bindings.BindHandle(id, body, handle, stand); }
        public bool IsHandleHeld(Guid id) => active && !stopped && bindings.IsHandleHeld(localActor, id);
        public Vector3? CurrentGripStand() => active && !stopped ? bindings.GripStand(localActor) : null;

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
            if (!bindings.HasCarryTarget(localActor)) throw new InvalidOperationException("Local carry target is missing.");
            if (!bindings.HasRequiredActorRoot(localActor)) throw new InvalidOperationException("Cart gripping requires the local worker root.");
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
                    foreach (Guid id in bindings.ClaimedBy(localActor)) commands.Renew(id);
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
                    bindings.ApplyMaterialMass(change.Output);
            }
        }

        public bool IsBodyFree(Rigidbody body)
        {
            if (!active || stopped || (world.View.Phase != WorldPhase.Running && world.View.Phase != WorldPhase.Paused)) return false;
            return bindings.IsFree(body);
        }

        public bool MayIgnoreForSight(Guid actor, Guid target, Rigidbody body)
        {
            if (world == null || stopped) return false;
            return bindings.MayIgnoreForSight(actor, target, body);
        }

        public void Grab(Guid id)
        {
            if (bindings == null || !bindings.CanEnterHandle(id, localActor))
            { LastAction = "Stand behind the stationary cart to take its handle"; return; }
            RunCommand(() => commands.Grab(id));
        }
        public void Release(Guid id) => RunCommand(() => commands.Release(id));
        public void ReplayLast() => RunCommand(() => commands.ReplayLast());

        public void TransferFocused()
        {
            if (!PrepareFocused()) return;
            Guid held = HeldObject();
            if (bindings.IsHandle(focused))
            {
                if (held != Guid.Empty) Release(held); else Grab(focused);
                return;
            }
            if (held != Guid.Empty && bindings.IsHandle(held))
            { LastAction = "Release the cart handle before handling containers"; return; }
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
            return bindings.HeldObject(localActor);
        }

        public float CarriedPhysicalMass()
        {
            return world == null || stopped ? 0 : bindings.CarriedMass(localActor);
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
            if (bindings.IsHandle(focused))
            {
                FocusHint = bindings.IsHandleHeld(localActor, focused) ? "Cart handle | WASD push/steer · G release" :
                    HeldObject() != Guid.Empty ? "Cart | E release crate onto bed" : "Cart | stand behind it and press E to take handle";
                return;
            }
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
            if (!bindings.CanPlace(entity, slot))
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
            if (bindings.Reconcile(applyForces, Time.fixedDeltaTime)) LastAction = "Dropped: the held object was obstructed";
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
            bindings?.Clear(); focused = Guid.Empty; pickTarget = null; targetName = null;
        }

        private void OnDisable() => Shutdown();
        private void OnDestroy() => Shutdown();
    }
}
