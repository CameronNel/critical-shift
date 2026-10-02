using System;
using CriticalShift.Features.Interaction.Domain;

namespace CriticalShift.Application
{
    public enum ControlAction { Toggle, Turn, Hold, Connect, Work }
    public sealed class ControlRequest
    {
        public ControlRequest(ControlAction action, long revision) { Action = action; Revision = revision; }
        public ControlAction Action { get; }
        public long Revision { get; }
        internal bool IsWellFormed => Enum.IsDefined(typeof(ControlAction), Action) && Revision >= 0;
        internal bool Same(ControlRequest other) => Action == other.Action && Revision == other.Revision;
    }
    public sealed class ControlView
    {
        internal ControlView(Guid epoch, ControlState state)
        { Epoch = epoch; Id = state.Id; Revision = state.Revision; Active = state.Active; Turns = state.Turns; Connected = state.Connected; Action = (ControlAction)state.Operation; }
        public Guid Epoch { get; }
        public Guid Id { get; }
        public long Revision { get; }
        public bool Active { get; }
        public int Turns { get; }
        public bool Connected { get; }
        public ControlAction Action { get; }
    }
}
