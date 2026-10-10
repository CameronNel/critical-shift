using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    /// <summary>Player use cases over the existing custody and worker owners. No independent inventory.</summary>
    public sealed class PlayerOperations
    {
        private readonly WorldSession _world;
        private readonly InteractionWorld _interaction;
        private readonly WorkerWorkflow _workers;
        private readonly IPlayerActionPolicy? _policy;
        private readonly Dictionary<Guid, PlayerTargetKind> _targets = new Dictionary<Guid, PlayerTargetKind>();
        private readonly Dictionary<Guid, Guid> _placements = new Dictionary<Guid, Guid>();
        private readonly Dictionary<Guid, Guid> _equipment = new Dictionary<Guid, Guid>();

        internal PlayerOperations(WorldSession world, InteractionWorld interaction, WorkerWorkflow workers, IPlayerActionPolicy? policy)
        { _world = world; _interaction = interaction; _workers = workers; _policy = policy; }

        public void RegisterActor(Guid actor, Guid equipmentSlot)
        {
            _world.RegisterPlayer(() =>
            {
                if (_workers.Get(actor) == null || _equipment.ContainsKey(actor))
                    throw new InvalidOperationException("A unique connected worker is required.");
                _interaction.ValidatePlayerSlot(equipmentSlot);
                _interaction.RegisterProductionSlot(equipmentSlot);
                _equipment.Add(actor, equipmentSlot);
            });
        }

        public void RegisterTarget(Guid entity, PlayerTargetKind kind, Guid? placementSlot = null)
        {
            _world.RegisterPlayer(() =>
            {
                if (kind < PlayerTargetKind.Carryable || kind > PlayerTargetKind.Placement || _targets.ContainsKey(entity) ||
                    ((kind == PlayerTargetKind.Placement) != placementSlot.HasValue))
                    throw new ArgumentException("Invalid or duplicate player target definition.");
                _interaction.ValidatePlayerRegistration(entity, placementSlot);
                _interaction.RegisterObject(entity);
                if (placementSlot.HasValue)
                { _interaction.RegisterProductionSlot(placementSlot.Value); _placements.Add(entity, placementSlot.Value); }
                _targets.Add(entity, kind);
            });
        }

        public PlayerTargetKind? GetKind(Guid entity) => _targets.TryGetValue(entity, out var kind) ? kind : (PlayerTargetKind?)null;
        public ObjectClaimView? GetHeld(Guid actor) => _interaction.GetHeldObject(actor);
        public ObjectClaimView? GetSeat(Guid actor)
        {
            var held = GetHeld(actor);
            return held != null && GetKind(held.EntityId) == PlayerTargetKind.Seat ? held : null;
        }
        public ObjectClaimView? GetEquipment(Guid actor) => _equipment.TryGetValue(actor, out var slot) ? Occupant(slot) : null;
        public ObjectClaimView? GetPlaced(Guid target) => _placements.TryGetValue(target, out var slot) ? Occupant(slot) : null;

        internal bool AllowsLegacy(Guid entity, InteractionKind kind) => GetKind(entity) != PlayerTargetKind.Seat || kind == InteractionKind.Renew;

        internal InteractionReply Apply(Guid actor, Guid target, PlayerRequest request)
        {
            var worker = _workers.Get(actor);
            if (_world.View.Phase != WorldPhase.Running || worker == null || !worker.CanInteract || !_equipment.ContainsKey(actor))
                return Reject(InteractionStatus.ActorUnavailable);
            if (worker.Revision != request.WorkerRevision) return Reject(InteractionStatus.RevisionConflict);
            if (worker.Pose == WorkerPose.Seated && request.Action != PlayerAction.Stand)
                return Reject(InteractionStatus.ActorUnavailable);
            if (!_targets.TryGetValue(target, out var kind)) return Reject(InteractionStatus.TargetUnavailable);
            if (((request.Action == PlayerAction.PickUp || request.Action == PlayerAction.Drop) && !Portable(kind)) ||
                (request.Action == PlayerAction.Equip && kind != PlayerTargetKind.ProtectiveEquipment) ||
                ((request.Action == PlayerAction.Sit || request.Action == PlayerAction.Stand) && kind != PlayerTargetKind.Seat) ||
                ((request.Action == PlayerAction.Place || request.Action == PlayerAction.Take) && kind != PlayerTargetKind.Placement))
                return Reject(InteractionStatus.TargetUnavailable);
            if ((request.Action == PlayerAction.Drop || request.Action == PlayerAction.Stand) &&
                _interaction.GetObject(target)?.Revision != request.ObjectRevision)
                return Reject(InteractionStatus.RevisionConflict);
            var access = _policy?.Evaluate(_world.Epoch, actor, target, request) ?? PlayerAccess.TargetUnavailable;
            switch (access)
            {
                case PlayerAccess.OutOfReach: return Reject(InteractionStatus.OutOfReach);
                case PlayerAccess.ActorUnavailable: return Reject(InteractionStatus.ActorUnavailable);
                case PlayerAccess.TargetUnavailable: return Reject(InteractionStatus.TargetUnavailable);
                case PlayerAccess.PlacementBlocked: return Reject(InteractionStatus.PlacementBlocked);
                case PlayerAccess.Allowed: break;
                default: throw new InvalidOperationException("Invalid player policy result.");
            }
            switch (request.Action)
            {
                case PlayerAction.PickUp:
                    return Portable(kind) ? _interaction.GrabPlayerObject(target, actor, request.ObjectRevision) : Reject(InteractionStatus.TargetUnavailable);
                case PlayerAction.Drop:
                    return Portable(kind) ? _interaction.ReleasePlayerObject(target, actor, request.LeaseGeneration) : Reject(InteractionStatus.TargetUnavailable);
                case PlayerAction.Sit:
                    if (kind != PlayerTargetKind.Seat || worker.Pose != WorkerPose.Upright) return Reject(InteractionStatus.ActorUnavailable);
                    var sit = _interaction.GrabPlayerObject(target, actor, request.ObjectRevision);
                    if (sit.HasNewCommit) RequireChanged(_workers.Seat(actor, worker.Revision, true));
                    return sit;
                case PlayerAction.Stand:
                    if (kind != PlayerTargetKind.Seat || worker.Pose != WorkerPose.Seated) return Reject(InteractionStatus.ActorUnavailable);
                    var stand = _interaction.ReleasePlayerObject(target, actor, request.LeaseGeneration);
                    if (stand.HasNewCommit) RequireChanged(_workers.Seat(actor, worker.Revision, false));
                    return stand;
                case PlayerAction.Equip:
                    if (kind != PlayerTargetKind.ProtectiveEquipment || worker.Suit != WorkerSuit.None)
                        return Reject(InteractionStatus.TargetUnavailable);
                    var equip = _interaction.InsertBatch(target, actor, request.LeaseGeneration, request.ObjectRevision, _equipment[actor]);
                    if (equip.HasNewCommit) RequireChanged(_workers.Environment(actor, worker.Revision, WorkerSuit.Intact, worker.Contamination));
                    return equip;
                case PlayerAction.Unequip:
                    if (GetEquipment(actor)?.EntityId != target) return Reject(InteractionStatus.NotHolder);
                    var remove = _interaction.EjectBatch(_equipment[actor], request.ObjectRevision);
                    if (remove.HasNewCommit) RequireChanged(_workers.Environment(actor, worker.Revision, WorkerSuit.None, worker.Contamination));
                    return remove;
                case PlayerAction.Place:
                    if (kind != PlayerTargetKind.Placement || !Portable(GetKind(request.ItemId))) return Reject(InteractionStatus.TargetUnavailable);
                    return _interaction.InsertBatch(request.ItemId, actor, request.LeaseGeneration, request.ObjectRevision, _placements[target]);
                case PlayerAction.Take:
                    if (kind != PlayerTargetKind.Placement || GetPlaced(target)?.EntityId != request.ItemId)
                        return Reject(InteractionStatus.TargetUnavailable);
                    return _interaction.TakePlayerObject(_placements[target], actor, request.ObjectRevision);
                default: throw new InvalidOperationException("An invalid player action passed admission.");
            }
        }

        // Lease loss, physical-binding failure, retirement and impacts cannot leave a seated worker
        // without its seat. Physical clearance/fallback remains the Unity binding's responsibility.
        internal void ReconcileSeats()
        {
            foreach (var actor in _equipment.Keys)
            {
                var worker = _workers.Get(actor);
                if (worker?.Pose == WorkerPose.Seated && GetSeat(actor) == null)
                    RequireChanged(_workers.Seat(actor, worker.Revision, false));
            }
        }

        internal void Disconnect(Guid actor)
        {
            var equipment = GetEquipment(actor);
            if (equipment != null)
            {
                var reply = _interaction.EjectBatch(_equipment[actor], equipment.Revision);
                if (!reply.HasNewCommit) throw new InvalidOperationException("Disconnected equipment could not be released.");
            }
            _equipment.Remove(actor);
        }
        internal void Clear() { _targets.Clear(); _placements.Clear(); _equipment.Clear(); }
        private ObjectClaimView? Occupant(Guid slot)
        { var item = _interaction.SlotOccupant(slot); return item.HasValue ? _interaction.GetObject(item.Value) : null; }
        private static bool Portable(PlayerTargetKind? kind) => kind == PlayerTargetKind.Carryable || kind == PlayerTargetKind.ProtectiveEquipment;
        private static InteractionReply Reject(InteractionStatus status) => new InteractionReply(status, true);
        private static void RequireChanged(WorkerReply reply)
        { if (!reply.Changed) throw new InvalidOperationException("A prevalidated player transaction could not commit its worker state."); }
    }
}
