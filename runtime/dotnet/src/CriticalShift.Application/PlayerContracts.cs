using System;

namespace CriticalShift.Application
{
    public enum PlayerTargetKind { Carryable, ProtectiveEquipment, Seat, Placement }
    public enum PlayerAction { PickUp, Drop, Sit, Stand, Equip, Unequip, Place, Take, PrepareEquipment }
    public enum PlayerAccess { Allowed, OutOfReach, ActorUnavailable, TargetUnavailable, PlacementBlocked }

    /// <summary>Trusted engine observations. Called before logical commit, never a client assertion.</summary>
    public interface IPlayerActionPolicy
    {
        PlayerAccess Evaluate(Guid epoch, Guid actor, Guid target, PlayerRequest request);
    }

    public sealed class PlayerRequest
    {
        public PlayerRequest(PlayerAction action, long objectRevision, long workerRevision,
            long leaseGeneration = 0, Guid itemId = default)
        {
            Action = action; ObjectRevision = objectRevision; WorkerRevision = workerRevision;
            LeaseGeneration = leaseGeneration; ItemId = itemId;
        }
        public PlayerAction Action { get; }
        public long ObjectRevision { get; }
        public long WorkerRevision { get; }
        public long LeaseGeneration { get; }
        public Guid ItemId { get; }
        internal bool IsWellFormed => ObjectRevision >= 0 && WorkerRevision >= 0 &&
            Action >= PlayerAction.PickUp && Action <= PlayerAction.PrepareEquipment &&
            ((Action == PlayerAction.Drop || Action == PlayerAction.Stand || Action == PlayerAction.Equip || Action == PlayerAction.Place)
                ? LeaseGeneration > 0 : LeaseGeneration == 0) &&
            ((Action == PlayerAction.Place || Action == PlayerAction.Take) ? ItemId != Guid.Empty : ItemId == Guid.Empty);
        internal bool Same(PlayerRequest other) => Action == other.Action && ObjectRevision == other.ObjectRevision &&
            WorkerRevision == other.WorkerRevision && LeaseGeneration == other.LeaseGeneration && ItemId == other.ItemId;
    }

    public sealed class PlayerPreparationView
    {
        internal PlayerPreparationView(Guid target, long generation, long due)
        { TargetId = target; LeaseGeneration = generation; DueShiftMilliseconds = due; }
        public Guid TargetId { get; }
        public long LeaseGeneration { get; }
        public long DueShiftMilliseconds { get; }
    }
}
