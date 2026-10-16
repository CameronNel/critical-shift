using System;

namespace CriticalShift.Features.Interaction.Domain
{
    public enum ControlOperation { Toggle, Turn, Hold, Connect, Work }
    public sealed class ControlState
    {
        public ControlState(Guid id, ControlOperation operation, long revision = 0, bool active = false, int turns = 0, bool connected = false)
        { if (id == Guid.Empty || !Enum.IsDefined(typeof(ControlOperation), operation) || revision < 0 || turns < 0 || turns > 5) throw new ArgumentException("Invalid control.");
          Id = id; Operation = operation; Revision = revision; Active = active; Turns = turns; Connected = connected; }
        public Guid Id { get; }
        public ControlOperation Operation { get; }
        public long Revision { get; }
        public bool Active { get; }
        public int Turns { get; }
        public bool Connected { get; }
        public ControlState Apply(ControlOperation requested) => new ControlState(Id, Operation, checked(Revision + 1),
            requested == ControlOperation.Toggle ? !Active : requested == ControlOperation.Connect ? Active : true,
            requested == ControlOperation.Turn ? (Turns + 1) % 6 : Turns, Connected || requested == ControlOperation.Connect);
    }
}
