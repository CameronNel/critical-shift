using System;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics.Unity;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Bootstrap
{
    [DefaultExecutionOrder(-200), DisallowMultipleComponent]
    public sealed class FacilitySceneHost : SceneInteractionGateway, IInteractionAccessPolicy, IWorkerRecoveryPolicy
    {
        [SerializeField] private WorkerController[] workers = Array.Empty<WorkerController>();
        [SerializeField] private SceneTarget[] targets = Array.Empty<SceneTarget>();
        [SerializeField] private int seed = 1, shiftSeconds = 1200;
        [SerializeField] private LayerMask obstructionMask = ~0;
        private readonly Dictionary<Guid, WorkerController> actors = new Dictionary<Guid, WorkerController>();
        private readonly Dictionary<Guid, SceneTarget> entities = new Dictionary<Guid, SceneTarget>();
        private readonly Dictionary<Guid, long> sequences = new Dictionary<Guid, long>();
        private readonly Dictionary<string, long> impacts = new Dictionary<string, long>();
        private readonly Dictionary<Guid, FacilityControl> stations = new Dictionary<Guid, FacilityControl>();
        private readonly Dictionary<Guid, WorldTimerHandle> stationTimers = new Dictionary<Guid, WorldTimerHandle>();
        private readonly List<Guid> disconnected = new List<Guid>(4);
        private readonly List<Guid> cancelledStations = new List<Guid>(4);
        private WorldSession world;
        private double origin;
        private long renewAt;
        private SceneTarget policyContact;
        private Guid policyActor;
        public override bool Running => world != null && world.View.Phase == WorldPhase.Running;
        public WorldSessionView Snapshot => world?.View;

        private void Start()
        {
            try
            {
                if (workers.Length < 1 || workers.Length > 4 || shiftSeconds < 1) throw new InvalidOperationException("Assign one to four workers and a positive shift duration.");
                world = new WorldSession(new WorldSessionConfiguration(seed, (long)shiftSeconds * 1000,
                    maxObjects: Math.Max(128, targets.Length + 1)), this, this);
                foreach (var worker in workers)
                {
                    if (worker == null) throw new InvalidOperationException("Missing worker binding.");
                    actors.Add(worker.Id, worker); sequences.Add(worker.Id, 0);
                    world.RegisterConnection(worker.Id, worker.Id);
                }
                foreach (var target in targets)
                {
                    if (target == null) throw new InvalidOperationException("Missing object/control binding.");
                    if (target is CarryableObject item && item.Body == null) throw new InvalidOperationException("Assign every object's Rigidbody.");
                    entities.Add(target.Id, target);
                    if (target is MachineBinding machine)
                    {
                        if (machine.Machine != machine) continue;
                        if (machine.Slot == null) throw new InvalidOperationException("Assign each machine's output/input slot anchor.");
                        if (machine.Kind == MachineBindingKind.Production) world.Production.RegisterMachine(machine.Id, machine.Recipe);
                        else world.Reactor.Register(machine.Id, machine.Definition);
                    }
                    else if (target is FacilityControl control) world.Controls.Register(target.Id, ControlActionFor(control.Operation),
                        control.Kind == ControlKind.ReanimationStation ? ControlAction.Connect : control.Kind == ControlKind.Valve ? ControlAction.Hold : (ControlAction?)null);
                    else
                    {
                        var batch = target.GetComponent<MaterialBinding>();
                        bool shared = target is CarryableObject cargo && cargo.AllowAssistance;
                        if (batch == null) world.RegisterObject(target.Id, shared);
                        else world.Production.RegisterBatch(target.Id, Guid.NewGuid(), target.Id, target.Id,
                            batch.Kind, batch.Units, batch.Moisture, batch.Contamination, shared);
                    }
                }
                world.Start(); origin = Time.realtimeSinceStartupAsDouble;
            }
            catch (Exception error) { Debug.LogException(error, this); Shutdown(); enabled = false; }
        }

        private void Update()
        {
            if (!Running) return;
            disconnected.Clear();
            foreach (var actor in actors) if (actor.Value == null || !actor.Value.isActiveAndEnabled) disconnected.Add(actor.Key);
            foreach (var id in disconnected) { actors.Remove(id); world.Disconnect(world.Epoch, id); }
            cancelledStations.Clear();
            foreach (var binding in stations) if (binding.Value == null || !binding.Value.isActiveAndEnabled || binding.Value.Patient == null)
                cancelledStations.Add(binding.Key);
            foreach (var id in cancelledStations)
            {
                if (stationTimers.TryGetValue(id, out var timer)) world.CancelTimer(timer);
                var station = stations[id];
                if (station != null && station.Patient != null) actors[station.Patient.Id].KnockDown(Vector3.zero);
                stations.Remove(id); stationTimers.Remove(id);
            }
            var advance = world.AdvanceTo((long)((Time.realtimeSinceStartupAsDouble - origin) * 1000));
            foreach (var signal in advance.Signals)
            {
                if (signal.Signal == "reanimation" && stations.TryGetValue(signal.OwnerId, out var station)) FinishStation(station);
            }
            SynchronizeBindings();
            if (!Running) { ClearPhysicalBindings(); return; }
            if (world.View.HostMilliseconds >= renewAt)
            {
                renewAt = world.View.HostMilliseconds + 1000;
                foreach (var target in targets) if (target is CarryableObject carry && carry.Holder != null)
                {
                    var reply = Command(carry.Holder, carry.Id, InteractionKind.Renew, lease: carry.Generation);
                    if (!reply.Accepted) AttachmentFailed(carry, carry.Generation);
                }
            }
        }
        public override bool CanAct(WorkerScenePort worker) => Running && worker != null &&
            actors.TryGetValue(worker.Id, out var bound) && bound == worker && bound.isActiveAndEnabled &&
            world.GetWorker(worker.Id)?.CanInteract == true;
        public override SceneTarget Held(WorkerScenePort worker)
        {
            foreach (var target in targets) if (target is CarryableObject carry && (carry.Holder == worker || carry.Assistant == worker)) return target;
            return null;
        }
        public override bool CanUse(WorkerScenePort worker, SceneTarget target)
        {
            if (worker == null || target == null || !target.isActiveAndEnabled || !entities.TryGetValue(target.Id, out var bound) || bound != target) return false;
            if (Held(worker) == target) return true;
            Vector3 delta = target.Contact.position - worker.Eye.position;
            if (delta.magnitude > target.Reach) return false;
            var hits = Physics.RaycastAll(worker.Eye.position, delta.normalized, delta.magnitude,
                obstructionMask, QueryTriggerInteraction.Ignore);
            foreach (var hit in hits)
            {
                if (Array.IndexOf(worker.BodyColliders, hit.collider) >= 0) continue;
                if (hit.collider.GetComponentInParent<SceneTarget>() != target) return false;
            }
            return true;
        }
        public override string Describe(SceneTarget target)
        {
            if (!Running || target == null) return "";
            if (target is MachineBinding machine)
            {
                if (machine.Kind == MachineBindingKind.Reactor) { var reactor = world.Reactor.View; return reactor == null ? "Unavailable" : reactor.Mode + " | reserve " + reactor.Power.Available + " | cooling " + reactor.Cooling; }
                var state = world.Production.GetMachine(machine.Machine.Id); return state == null ? "Unavailable" : state.Mode + " | powered " + state.Powered;
            }
            var batch = world.Production.GetBatch(target.Id);
            if (batch != null) return batch.Kind + " | units " + batch.Units + " | moisture " + batch.Moisture + " | contamination " + batch.Contamination;
            var control = world.Controls.Get(target.Id);
            return control == null ? target.name : target.name + " | active " + control.Active + " | connected " + control.Connected;
        }
        public override void RotateHeld(WorkerScenePort worker, float degrees)
        {
            if (!CanAct(worker) || !float.IsFinite(degrees) || Mathf.Abs(degrees) > 180 || !(Held(worker) is CarryableObject item) || item.Holder != worker) return;
            var state = world.GetObject(item.Id);
            if (state?.HolderId == worker.Id && state.LeaseGeneration == item.Generation) item.RotateGrip(degrees);
        }
        AccessDecision IInteractionAccessPolicy.Evaluate(Guid actor, Guid entity, InteractionKind kind)
        {
            if (!actors.TryGetValue(actor, out var worker) || !worker.isActiveAndEnabled) return AccessDecision.ActorUnavailable;
            if (!entities.TryGetValue(entity, out var target) || !target.isActiveAndEnabled) return AccessDecision.TargetUnavailable;
            if (policyActor == actor && policyContact is MachineBinding control && control.Machine.Id == entity) target = policyContact;
            return CanUse(worker, target) ? AccessDecision.Allowed : AccessDecision.OutOfReach;
        }
        RecoveryClearance IWorkerRecoveryPolicy.Evaluate(Guid epoch, Guid worker, long attempt)
        {
            if (world == null || world.Epoch != epoch || !actors.TryGetValue(worker, out var actor) || !actor.isActiveAndEnabled ||
                world.GetWorker(worker)?.RecoveryAttempt != attempt) return RecoveryClearance.Unavailable;
            return actor.RecoveryClear && !BodyHeld(actor) ? RecoveryClearance.Safe : RecoveryClearance.Blocked;
        }
        private bool BodyHeld(WorkerScenePort worker)
        { foreach (var target in targets) if (target is CarryableObject carry && carry.WorkerBody == worker && (carry.Holder != null || world.GetObject(carry.Id)?.SlotId != null)) return true; return false; }

        public override bool Execute(WorkerScenePort worker, SceneTarget target, SceneOperation operation, out string reason)
        {
            try { return ExecuteBound(worker, target, operation, out reason); }
            catch { Shutdown(); throw; }
        }
        private bool ExecuteBound(WorkerScenePort worker, SceneTarget target, SceneOperation operation, out string reason)
        {
            reason = "Interaction unavailable.";
            if (!CanAct(worker)) return false;
            if (operation == SceneOperation.Point || operation == SceneOperation.Radio) { reason = ""; return true; }
            if (!CanUse(worker, target) || !target.Supports(operation)) return false;
            if (target is CarryableObject carry) return Carry(worker, carry, operation, out reason);
            if (target is MachineBinding machine) return Machine(worker, machine, out reason);
            if (!(target is FacilityControl control)) return false;
            if (operation == SceneOperation.Dig && !(Held(worker) is CarryableObject tool && tool.Kind == CarryableKind.Shovel))
            { reason = "Hold a shovel to dig."; return false; }
            if (operation == SceneOperation.Help && (control.Patient == null || !control.Patient.Down))
            { reason = "No downed worker at this aid point."; return false; }
            if (operation == SceneOperation.LockerExit && (control.WorkerAnchor == null || Held(worker) != null)) return false;
            if (operation == SceneOperation.Reanimation && (!control.Connected || control.Patient == null ||
                !control.Patient.Down || control.WorkerAnchor == null || stations.ContainsKey(control.Id) || BodyHeld(control.Patient)))
            { reason = "Connect a service port and release the patient at the chamber first."; return false; }
            var view = world.Controls.Get(target.Id);
            var reply = Command(worker, target.Id, InteractionKind.Control, control: new ControlRequest(ControlActionFor(operation), view.Revision));
            reason = reply.Status.ToString();
            if (!reply.HasNewCommit) return reply.Accepted;
            if (operation == SceneOperation.Suit)
            {
                var state = world.GetWorker(worker.Id);
                var suited = world.SetWorkerEnvironment(world.Epoch, worker.Id, state.Revision, WorkerSuit.Intact, state.Contamination);
                if (!suited.Changed) { reason = suited.Status.ToString(); return false; }
            }
            if (operation == SceneOperation.Help)
            {
                var patient = world.GetWorker(control.Patient.Id);
                var aid = world.StabilizeWorker(world.Epoch, patient.Id, patient.Revision, 1000);
                if (!aid.Changed) { reason = aid.Status.ToString(); return false; }
            }
            control.Project(reply.Control);
            if (!target.Apply(worker, operation, 0)) return false;
            if (operation == SceneOperation.LockerExit) worker.PresentStation(operation, control.WorkerAnchor);
            if (operation == SceneOperation.Reanimation)
            {
                control.Patient.PresentStation(operation, control.WorkerAnchor);
                actors[control.Patient.Id].ReanimationJolt();
                var timer = world.Schedule(world.Epoch, control.Id, "reanimation", WorldTimeBasis.ShiftTime, 3000);
                if (timer.Status != WorldControlStatus.Applied) { reason = timer.Status.ToString(); Shutdown(); return false; }
                stations.Add(control.Id, control); stationTimers.Add(control.Id, timer.Handle);
            }
            return true;
        }

        private InteractionReply Command(WorkerScenePort worker, Guid entity, InteractionKind kind,
            long revision = 0, long lease = 0, ProductionRequest production = null, ReactorRequest reactor = null, ControlRequest control = null, SceneTarget contact = null)
        {
            long next = checked(sequences[worker.Id] + 1);
            policyContact = contact; policyActor = worker.Id;
            try
            {
                var reply = world.ExecuteInteraction(worker.Id, new InteractionCommand(world.Epoch, next, kind, entity,
                    revision, lease, production, reactor, control));
                if (reply.IsTerminal) sequences[worker.Id] = next;
                return reply;
            }
            finally { policyContact = null; policyActor = Guid.Empty; }
        }
        private bool Carry(WorkerScenePort worker, CarryableObject item, SceneOperation operation, out string reason)
        {
            reason = "Object unavailable.";
            var current = world.GetObject(item.Id);
            if (current == null || item.Body == null || (item.WorkerBody != null && !item.WorkerBody.Down)) return false;
            bool grab = operation == SceneOperation.Grab || operation == SceneOperation.Push || operation == SceneOperation.Pull || operation == SceneOperation.Drag;
            bool assist = grab && current.HolderId.HasValue && current.HolderId != worker.Id;
            var reply = Command(worker, item.Id, assist ? InteractionKind.Assist : grab ? InteractionKind.Grab : InteractionKind.Release,
                grab ? current.Revision : 0, grab && !assist ? 0 : current.LeaseGeneration);
            reason = reply.Status.ToString();
            if (!reply.HasNewCommit) return reply.Accepted;
            if (!item.Apply(worker, operation, current.LeaseGeneration + (grab && !assist ? 1 : 0)))
            { if (grab) AttachmentFailed(item, reply.State.LeaseGeneration); reason = "Physics attachment failed."; return false; }
            return true;
        }
        private bool Machine(WorkerScenePort worker, MachineBinding control, out string reason)
        {
            var machine = control.Machine;
            var held = Held(worker);
            var heldState = held != null ? world.GetObject(held.Id) : null;
            var heldBatch = held != null ? world.Production.GetBatch(held.Id) : null;
            bool insertion = machine.Kind == MachineBindingKind.Production ? control.ProductionAction == ProductionAction.Insert : control.ReactorAction == ReactorAction.Insert;
            if (insertion && (!(held is CarryableObject carried) || !SlotClear(worker, carried, machine)))
            { reason = "Move the container to a clear, reachable input slot."; return false; }
            InteractionReply reply;
            if (machine.Kind == MachineBindingKind.Production)
            {
                var state = world.Production.GetMachine(machine.Id);
                if (state == null) { reason = "Unregistered machine."; return false; }
                var input = state.ContainerId.HasValue ? world.Production.GetBatch(state.ContainerId.Value) : null;
                var occupant = state.ContainerId.HasValue ? world.GetObject(state.ContainerId.Value) : null;
                bool insert = control.ProductionAction == ProductionAction.Insert;
                if (insert && (heldBatch == null || heldState == null)) { reason = "Hold a material container."; return false; }
                reply = Command(worker, machine.Id, InteractionKind.Production, contact: control, production: new ProductionRequest(control.ProductionAction,
                    state.Revision, insert ? held.Id : Guid.Empty, insert ? heldState.Revision : control.ProductionAction == ProductionAction.Eject ? occupant?.Revision ?? 0 : 0,
                    insert ? heldBatch.Revision : control.ProductionAction == ProductionAction.Start ? input?.Revision ?? 0 : 0,
                    insert ? heldState.LeaseGeneration : 0, control.ProductionAction == ProductionAction.Start && control.BypassInspection,
                    control.ProductionAction == ProductionAction.SetPower && control.PoweredValue));
            }
            else
            {
                var state = world.Reactor.View;
                if (state == null || state.Id != machine.Id) { reason = "Unregistered reactor."; return false; }
                bool insert = control.ReactorAction == ReactorAction.Insert;
                if (insert && (heldBatch == null || heldState == null)) { reason = "Hold a fuel container."; return false; }
                var occupant = state.Fuel != null ? world.GetObject(state.Fuel.ContainerId) : null;
                reply = Command(worker, machine.Id, InteractionKind.Reactor, contact: control, reactor: new ReactorRequest(control.ReactorAction, state.Revision,
                    insert ? held.Id : Guid.Empty, insert ? heldState.Revision : control.ReactorAction == ReactorAction.Eject ? occupant?.Revision ?? 0 : 0,
                    insert ? heldBatch.Revision : 0, insert ? heldState.LeaseGeneration : 0,
                    control.ReactorAction == ReactorAction.SetCooling && control.PoweredValue));
            }
            reason = reply.Production != null ? reply.Production.Status.ToString() : reply.Reactor?.Status.ToString() ?? reply.Status.ToString();
            if (!reply.HasNewCommit) return reply.Accepted;
            SynchronizeBindings(); return true;
        }

        private bool SlotClear(WorkerScenePort worker, CarryableObject item, MachineBinding machine)
        {
            if (machine.Slot == null || Vector3.Distance(item.Body.position, machine.Slot.position) > 0.8f) return false;
            var shapes = item.GetComponentsInChildren<Collider>();
            if (shapes.Length == 0) return false;
            Bounds bounds = shapes[0].bounds; foreach (var shape in shapes) bounds.Encapsulate(shape.bounds);
            var overlaps = Physics.OverlapBox(machine.Slot.position, bounds.extents, Quaternion.identity, obstructionMask, QueryTriggerInteraction.Ignore);
            foreach (var shape in overlaps)
                if (Array.IndexOf(shapes, shape) < 0 && Array.IndexOf(worker.BodyColliders, shape) < 0) return false;
            Vector3 path = machine.Slot.position - bounds.center;
            foreach (var hit in Physics.BoxCastAll(bounds.center, bounds.extents * 0.9f, path.normalized, Quaternion.identity,
                path.magnitude, obstructionMask, QueryTriggerInteraction.Ignore))
                if (Array.IndexOf(shapes, hit.collider) < 0 && Array.IndexOf(worker.BodyColliders, hit.collider) < 0) return false;
            return true;
        }

        private void SynchronizeBindings()
        {
            foreach (var target in targets) if (target is CarryableObject item)
            {
                var claim = world.GetObject(item.Id);
                if (item.Holder != null && (claim == null || claim.HolderId != item.Holder.Id || claim.LeaseGeneration != item.Generation)) item.ClearBinding();
                WorkerScenePort helper = null;
                if (claim?.AssistantId != null && actors.TryGetValue(claim.AssistantId.Value, out var actor)) helper = actor;
                item.SynchronizeAssistant(helper);
                Transform anchor = null;
                if (claim?.SlotId != null && entities.TryGetValue(claim.SlotId.Value, out var slot) && slot is MachineBinding machine) anchor = machine.Slot;
                item.SynchronizeSlot(anchor);
            }
            foreach (var worker in workers)
            {
                if (worker == null || !worker.isActiveAndEnabled) continue;
                var state = world.GetWorker(worker.Id);
                if (state == null) continue;
                worker.ProjectSuit(state.Suit != WorkerSuit.None);
                if (state.Pose == WorkerPose.Down && !worker.Down && !IsInStation(worker)) worker.KnockDown(Vector3.zero);
                if (state.Pose == WorkerPose.Upright && worker.Down) worker.BecomeUpright();
            }
        }
        private bool IsInStation(WorkerScenePort worker)
        { foreach (var station in stations.Values) if (station.Patient == worker) return true; return false; }
        public override void AttachmentFailed(SceneTarget target, long generation)
        {
            if (world == null) { target.ClearBinding(); return; }
            var reply = world.ReportAttachmentFailure(world.Epoch, target.Id, generation);
            if (reply.HasNewCommit || !Running) target.ClearBinding();
        }
        public override bool RecoveryReady(WorkerScenePort worker)
        {
            var state = world?.GetWorker(worker.Id);
            return Running && state != null && state.Pose == WorkerPose.Down && state.Awareness == WorkerAwareness.Alert &&
                world.View.ElapsedMilliseconds >= state.RecoveryNotBeforeMilliseconds && !BodyHeld(worker) && !IsInStation(worker);
        }
        public override long BeginRecovery(WorkerScenePort worker)
        {
            var state = world.GetWorker(worker.Id);
            var reply = world.BeginWorkerRecovery(world.Epoch, worker.Id, state.RecoveryEpisode, state.Revision);
            return reply.Changed ? reply.Worker.RecoveryAttempt : 0;
        }
        public override bool CompleteRecovery(WorkerScenePort worker, long attempt)
        {
            var reply = world.CompleteWorkerRecovery(world.Epoch, worker.Id, attempt);
            if (reply.Changed && reply.Worker.Pose == WorkerPose.Upright) { actors[worker.Id].BecomeUpright(); return true; }
            return false;
        }
        public override void Impact(WorkerScenePort worker, Guid hazard, bool incapacitating, float delaySeconds)
        {
            if (!Running || !actors.ContainsKey(worker.Id) || !float.IsFinite(delaySeconds) || delaySeconds < 0) return;
            string key = worker.Id + ":" + hazard;
            impacts.TryGetValue(key, out long before);
            var reply = world.ApplyWorkerImpact(world.Epoch, worker.Id, before + 1,
                incapacitating ? WorkerImpact.Incapacitating : WorkerImpact.Knockdown, (long)(delaySeconds * 1000), hazard, Guid.NewGuid());
            if (reply.Changed) { impacts[key] = before + 1; SynchronizeBindings(); }
        }
        private void FinishStation(FacilityControl station)
        {
            stations.Remove(station.Id); stationTimers.Remove(station.Id);
            if (station.Patient == null || !actors.ContainsKey(station.Patient.Id)) return;
            var state = world.GetWorker(station.Patient.Id);
            if (state == null) return;
            if (state.Awareness == WorkerAwareness.Unconscious)
            {
                var reply = world.StabilizeWorker(world.Epoch, state.Id, state.Revision, 0);
                if (!reply.Changed) return;
            }
            long attempt = BeginRecovery(station.Patient);
            if (attempt != 0) actors[station.Patient.Id].ReanimationExit(attempt);
            else actors[station.Patient.Id].KnockDown(Vector3.zero);
        }
        private static ControlAction ControlActionFor(SceneOperation value) => value == SceneOperation.ValveTurn ? ControlAction.Turn :
            value == SceneOperation.ValveHold ? ControlAction.Hold : value == SceneOperation.Connect ? ControlAction.Connect :
            value == SceneOperation.Dig ? ControlAction.Work : ControlAction.Toggle;
        private void ClearPhysicalBindings()
        { foreach (var target in targets) if (target != null) { if (target is CarryableObject item) item.SynchronizeSlot(null); target.ClearBinding(); }
          foreach (var worker in workers) if (worker != null) worker.CancelSceneActions(); stations.Clear(); stationTimers.Clear(); }
        private void Shutdown() { world?.Stop(); ClearPhysicalBindings(); }
        private void OnDisable() { Shutdown(); }
    }
}
