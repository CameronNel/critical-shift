using System;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.Features.Player.Unity;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    // Local session/clock adapter. Bootstrap supplies the world factory; this adapter owns its lifetime.
    public sealed class LocalShiftHost : PlayerWorldBridge, IInteractionAccessPolicy, IPlayerActionPolicy
    {
        [SerializeField] private FirstPersonWorker[] workers = Array.Empty<FirstPersonWorker>();
        [SerializeField] private InteractionTarget[] targets = Array.Empty<InteractionTarget>();
        [SerializeField, Range(30, 3600)] private int shiftSeconds = 1200;
        private readonly Dictionary<Guid, FirstPersonWorker> _actors = new Dictionary<Guid, FirstPersonWorker>();
        private readonly Dictionary<Guid, InteractionTarget> _targets = new Dictionary<Guid, InteractionTarget>();
        private readonly Dictionary<Guid, Transform> _slots = new Dictionary<Guid, Transform>();
        private readonly Dictionary<Guid, Guid> _connections = new Dictionary<Guid, Guid>();
        private readonly Dictionary<Guid, long> _sequences = new Dictionary<Guid, long>();
        private readonly Collider[] _overlap = new Collider[32];
        private readonly RaycastHit[] _hits = new RaycastHit[32];
        private WorldSession _world;
        private Func<WorldSession> _worldFactory;
        private double _origin;
        private long _nextRenew;
        private bool _ownsGlobals, _terminalProjected;
        private float _previousTimeScale;
        private CursorLockMode _previousCursor;
        private bool _previousCursorVisible;
        private string _feedback = "";
        public override WorldSessionView View => _world?.View;
        public override string Feedback => _feedback;
        public override WorkerView Worker(Guid actor) => _world?.GetWorker(actor);
        public override ObjectClaimView Held(Guid actor) => _world?.Players.GetHeld(actor);
        public override ObjectClaimView Equipment(Guid actor) => _world?.Players.GetEquipment(actor);
        public override ObjectClaimView Placed(Guid target) => _world?.Players.GetPlaced(target);
        public override InteractionTarget Target(Guid id) => _targets.TryGetValue(id, out var target) ? target : null;
        public ObjectClaimView Object(Guid id) => _world?.GetObject(id);

        public void Configure(FirstPersonWorker[] players, InteractionTarget[] interactables, Func<WorldSession> worldFactory, int durationSeconds = 1200)
        {
            if (_world != null) throw new InvalidOperationException("Cannot reconfigure an active fixture.");
            _worldFactory = worldFactory ?? throw new ArgumentNullException(nameof(worldFactory));
            workers = (FirstPersonWorker[])players.Clone(); targets = (InteractionTarget[])interactables.Clone(); shiftSeconds = durationSeconds;
        }
        public override void Begin()
        {
            Shutdown(); _actors.Clear(); _targets.Clear(); _slots.Clear(); _connections.Clear(); _sequences.Clear();
            try
            {
#if ENABLE_INPUT_SYSTEM && !ENABLE_LEGACY_INPUT_MANAGER
                throw new InvalidOperationException("This local fixture requires Input Manager (Old) or Both in Player Settings.");
#endif
                if (workers.Length < 1 || workers.Length > 4 || targets.Length < 1 || targets.Length > 64 ||
                    shiftSeconds < 30 || shiftSeconds > 3600) throw new InvalidOperationException("Invalid local fixture capacity.");
                int localPlayers = 0;
                foreach (var worker in workers)
                {
                    if (worker == null || !worker.isActiveAndEnabled) throw new InvalidOperationException("Missing worker binding.");
                    worker.Bind(this); _actors.Add(worker.Id, worker); _slots.Add(worker.EquipmentSlot, worker.EquipmentAnchor);
                    _connections.Add(worker.Id, Guid.NewGuid()); _sequences.Add(worker.Id, 0);
                    if (worker.LocalInput) localPlayers++;
                }
                if (localPlayers != 1) throw new InvalidOperationException("The local room needs exactly one keyboard/mouse player.");
                foreach (var target in targets)
                {
                    if (target == null) throw new InvalidOperationException("Missing target binding.");
                    target.Capture(); _targets.Add(target.Id, target);
                    if (target.Kind == PlayerTargetKind.Placement) _slots.Add(target.Slot, target.Attachment);
                }
                Physics.SyncTransforms();
                foreach (var worker in workers)
                    if (!worker.CanStandAt(worker.transform.position)) throw new InvalidOperationException("Worker spawn is obstructed.");
                if (_worldFactory == null) throw new InvalidOperationException("Bootstrap has not supplied a world factory.");
                _world = _worldFactory();
                foreach (var worker in workers)
                { _world.RegisterConnection(_connections[worker.Id], worker.Id); _world.Players.RegisterActor(worker.Id, worker.EquipmentSlot); }
                foreach (var target in targets)
                    _world.Players.RegisterTarget(target.Id, target.Kind, target.Kind == PlayerTargetKind.Placement ? target.Slot : (Guid?)null);
                _world.Start(); _origin = Time.realtimeSinceStartupAsDouble; _nextRenew = 1000; _terminalProjected = false;
                _previousTimeScale = Time.timeScale; _previousCursor = Cursor.lockState; _previousCursorVisible = Cursor.visible;
                _ownsGlobals = true; Time.timeScale = 1; SetCursor(true); _feedback = "Shift started.";
            }
            catch (Exception error) { Fault(error); }
        }
        private void Update()
        {
            if (_world == null) return;
            try
            {
                Pump();
                foreach (var worker in workers) worker.ReadInput();
                if (View.Phase == WorldPhase.Running || View.Phase == WorldPhase.Paused) Project();
            }
            catch (Exception error) { Fault(error); }
        }
        private void Pump()
        {
            if (View.Phase != WorldPhase.Running && View.Phase != WorldPhase.Paused) return;
            long now = Math.Max(View.HostMilliseconds, (long)((Time.realtimeSinceStartupAsDouble - _origin) * 1000));
            _world.AdvanceTo(now);
            if (View.Phase == WorldPhase.Ended || View.Phase == WorldPhase.Faulted)
            {
                if (!_terminalProjected) { RestoreBindings(); ReleaseGlobals(); _terminalProjected = true; }
                _feedback = "Shift ended. Press F5 to restart."; return;
            }
            if (now >= _nextRenew)
            {
                foreach (var worker in workers)
                {
                    var held = Held(worker.Id);
                    if (held != null) Send(worker, new InteractionCommand(_world.Epoch, Next(worker.Id), InteractionKind.Renew,
                        held.EntityId, leaseGeneration: held.LeaseGeneration));
                }
                _nextRenew = checked(now + 1000);
            }
            Project();
        }
        public override void TogglePause()
        {
            if (_world == null) return;
            Pump();
            if (View.Phase == WorldPhase.Running) { _world.Pause(_world.Epoch); Time.timeScale = 0; SetCursor(false); }
            else if (View.Phase == WorldPhase.Paused) { _world.Resume(_world.Epoch); Time.timeScale = 1; SetCursor(true); }
        }
        private void OnApplicationFocus(bool focus) { if (!focus && View?.Phase == WorldPhase.Running) TogglePause(); }
        public override void Act(FirstPersonWorker worker, PlayerAction action, InteractionTarget target)
        {
            if (_world == null || View.Phase != WorldPhase.Running || worker == null || target == null ||
                !_actors.TryGetValue(worker.Id, out var bound) || bound != worker || Target(target.Id) != target) return;
            try
            {
                Pump();
                Guid item = action == PlayerAction.Place ? Held(worker.Id)?.EntityId ?? Guid.Empty :
                    action == PlayerAction.Take ? Placed(target.Id)?.EntityId ?? Guid.Empty : Guid.Empty;
                if ((action == PlayerAction.Place || action == PlayerAction.Take) && item == Guid.Empty)
                { _feedback = "There is no item to move."; return; }
                var state = Object(item == Guid.Empty ? target.Id : item); var actor = Worker(worker.Id);
                if (state == null || actor == null) return;
                var request = new PlayerRequest(action, state.Revision, actor.Revision,
                    action == PlayerAction.Drop || action == PlayerAction.Stand || action == PlayerAction.Equip || action == PlayerAction.Place ? state.LeaseGeneration : 0, item);
                var reply = Send(worker, new InteractionCommand(_world.Epoch, Next(worker.Id), InteractionKind.Player, target.Id, player: request));
                if (reply.HasNewCommit && (action == PlayerAction.Drop || action == PlayerAction.Unequip))
                    target.transform.position = worker.DropPoint;
                _feedback = Describe(reply.Status); Project();
            }
            catch (Exception error) { Fault(error); }
        }
        private long Next(Guid actor) => checked(_sequences[actor] + 1);
        private InteractionReply Send(FirstPersonWorker worker, InteractionCommand command)
        {
            var reply = _world.ExecuteInteraction(_connections[worker.Id], command);
            if (reply.IsTerminal) _sequences[worker.Id] = command.Sequence;
            return reply;
        }
        public override InteractionTarget Aim(FirstPersonWorker worker)
        {
            if (worker == null || !Physics.Raycast(worker.Eye.transform.position, worker.Eye.transform.forward,
                out var hit, 3, ~0, QueryTriggerInteraction.Ignore)) return null;
            foreach (var target in targets) if (target.Shape == hit.collider && target.isActiveAndEnabled) return target;
            return null;
        }
        public AccessDecision Evaluate(Guid actor, Guid target, InteractionKind kind)
        {
            if (kind != InteractionKind.Renew || !_actors.ContainsKey(actor) || !IsAvailable(Target(target))) return AccessDecision.TargetUnavailable;
            return Worker(actor)?.CanInteract == true ? AccessDecision.Allowed : AccessDecision.ActorUnavailable;
        }
        public PlayerAccess Evaluate(Guid epoch, Guid actor, Guid id, PlayerRequest request)
        {
            if (_world == null || epoch != _world.Epoch || !_actors.TryGetValue(actor, out var worker)) return PlayerAccess.ActorUnavailable;
            var target = Target(id);
            if (!IsAvailable(target)) return PlayerAccess.TargetUnavailable;
            if (request.Action == PlayerAction.Stand)
                return worker.TryExit(target, out _, out _) ? PlayerAccess.Allowed : PlayerAccess.PlacementBlocked;
            if (request.Action == PlayerAction.Drop || request.Action == PlayerAction.Unequip)
                return ClearItem(worker, target, worker.DropPoint) ? PlayerAccess.Allowed : PlayerAccess.PlacementBlocked;
            if (request.Action == PlayerAction.Equip) return PlayerAccess.Allowed;
            if (Vector3.Distance(worker.Eye.transform.position, target.Shape.bounds.ClosestPoint(worker.Eye.transform.position)) > 3)
                return PlayerAccess.OutOfReach;
            if (!Physics.Raycast(worker.Eye.transform.position, (target.Shape.bounds.center - worker.Eye.transform.position).normalized,
                out var visible, 3.7f, ~0, QueryTriggerInteraction.Ignore) || visible.collider != target.Shape)
                return PlayerAccess.OutOfReach;
            if (request.Action == PlayerAction.Sit && !worker.CanStandAt(target.Attachment.position)) return PlayerAccess.PlacementBlocked;
            if (request.Action == PlayerAction.Place)
            {
                var item = Target(request.ItemId);
                if (item == null || !ClearItem(worker, item, target.Attachment.position)) return PlayerAccess.PlacementBlocked;
            }
            if (request.Action == PlayerAction.PickUp || request.Action == PlayerAction.Take)
            {
                var item = request.Action == PlayerAction.Take ? Target(request.ItemId) : target;
                if (item == null || !ClearItem(worker, item, worker.CarryAnchor.position)) return PlayerAccess.PlacementBlocked;
            }
            return PlayerAccess.Allowed;
        }
        private static bool IsAvailable(InteractionTarget target) => target != null && target.isActiveAndEnabled && target.Shape != null;
        private bool ClearItem(FirstPersonWorker worker, InteractionTarget item, Vector3 point)
        {
            int count = Physics.OverlapSphereNonAlloc(point, item.Radius + 0.02f, _overlap, ~0, QueryTriggerInteraction.Ignore);
            if (count == _overlap.Length) return false;
            for (int i = 0; i < count; i++)
                if (_overlap[i] != item.Shape && !_overlap[i].transform.IsChildOf(worker.transform)) return false;
            return true;
        }
        private void Project()
        {
            Physics.SyncTransforms();
            foreach (var worker in workers)
            {
                if (worker == null || !worker.isActiveAndEnabled)
                    throw new InvalidOperationException("A required worker binding became unavailable.");
                var actor = Worker(worker.Id); if (actor == null) continue;
                var seat = _world.Players.GetSeat(worker.Id);
                worker.ProjectPosture(actor, seat == null ? null : Target(seat.EntityId));
                var held = Held(worker.Id);
                if (held != null && Target(held.EntityId).Portable)
                {
                    var item = Target(held.EntityId);
                    var origin = worker.Eye.transform.position; var forward = worker.Eye.transform.forward;
                    float distance = 1.1f;
                    int count = Physics.SphereCastNonAlloc(origin, item.Radius, forward, _hits, distance, ~0, QueryTriggerInteraction.Ignore);
                    if (count == _hits.Length) throw new InvalidOperationException("Carry sweep capacity exceeded.");
                    for (int i = 0; i < count; i++)
                        if (_hits[i].collider != item.Shape && !_hits[i].collider.transform.IsChildOf(worker.transform))
                            distance = Mathf.Min(distance, Mathf.Max(0, _hits[i].distance - 0.03f));
                    worker.CarryAnchor.position = origin + forward * distance;
                }
            }
            foreach (var target in targets)
            {
                if (!IsAvailable(target)) throw new InvalidOperationException("A required target binding became unavailable.");
                if (!target.Portable) continue;
                var state = Object(target.Id);
                Transform destination = state?.HolderId != null ? _actors[state.HolderId.Value].CarryAnchor :
                    state?.SlotId != null ? _slots[state.SlotId.Value] : null;
                if (destination == null && target.transform.parent != null &&
                    (target.GetComponentInParent<FirstPersonWorker>() != null || _slots.ContainsValue(target.transform.parent)))
                {
                    // Unplanned lease loss: detach only into a clear pose; otherwise terminate safely.
                    var former = target.GetComponentInParent<FirstPersonWorker>();
                    if (former != null)
                    {
                        if (!ClearItem(former, target, former.DropPoint)) throw new InvalidOperationException("Lost item lease has no clear drop pose.");
                        target.transform.position = former.DropPoint;
                    }
                }
                target.Project(destination);
            }
        }
        public void Shutdown()
        {
            try { _world?.Stop(); }
            finally { try { RestoreBindings(); } finally { ReleaseGlobals(); } }
        }
        private void RestoreBindings()
        {
            foreach (var target in targets)
                if (target != null) { try { target.Restore(); } catch (Exception error) { Debug.LogException(error, this); } }
            foreach (var worker in workers)
                if (worker != null) { try { worker.Restore(); } catch (Exception error) { Debug.LogException(error, this); } }
        }
        private void ReleaseGlobals()
        {
            if (!_ownsGlobals) return;
            Time.timeScale = _previousTimeScale; Cursor.lockState = _previousCursor; Cursor.visible = _previousCursorVisible; _ownsGlobals = false;
        }
        private void SetCursor(bool playing)
        { Cursor.lockState = playing && UnityEngine.Application.isFocused ? CursorLockMode.Locked : CursorLockMode.None; Cursor.visible = !playing || !UnityEngine.Application.isFocused; }
        private void Fault(Exception error)
        { Shutdown(); _feedback = "Session stopped. Check the room setup, then press F5 to restart."; Debug.LogException(error, this); }
        private void OnDisable() { Shutdown(); }
        private void OnDestroy() { Shutdown(); }
        private static string Describe(InteractionStatus status)
        {
            switch (status)
            {
                case InteractionStatus.Applied: return "Done.";
                case InteractionStatus.NoChange: return "Already done.";
                case InteractionStatus.AlreadyClaimed: return "Someone is using that.";
                case InteractionStatus.ActorAlreadyHolding: return "Free your hands first.";
                case InteractionStatus.OutOfReach: return "Move closer and keep a clear line of sight.";
                case InteractionStatus.PlacementBlocked: return "There is not enough room.";
                case InteractionStatus.SlotOccupied: return "That spot is occupied.";
                case InteractionStatus.ActorUnavailable: return "Stand up before using another object.";
                default: return "That action is unavailable.";
            }
        }
    }
}
