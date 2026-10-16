using System;
using System.Collections.Generic;
using CriticalShift.Features.Interaction.Domain;

namespace CriticalShift.Application
{
    public sealed class FacilityControlOperations
    {
        private readonly WorldSession world;
        private readonly Dictionary<Guid, ControlState> states = new Dictionary<Guid, ControlState>();
        private readonly Dictionary<Guid, ControlAction?> alternate = new Dictionary<Guid, ControlAction?>();
        internal FacilityControlOperations(WorldSession world) { this.world = world; }
        public ControlView? Get(Guid id) => states.TryGetValue(id, out var state) ? new ControlView(world.Epoch, state) : null;
        public void Register(Guid id, ControlAction action, ControlAction? additional = null) => world.RegisterProduction(() =>
        {
            if (states.Count >= world.Configuration.MaxObjects || states.ContainsKey(id)) throw new InvalidOperationException("Control registration capacity/identity.");
            var state = new ControlState(id, (ControlOperation)action);
            if (additional.HasValue && !Enum.IsDefined(typeof(ControlAction), additional.Value)) throw new ArgumentException("Invalid additional operation.");
            states.Add(id, state); alternate.Add(id, additional);
        });
        internal InteractionReply Apply(Guid id, ControlRequest request)
        {
            if (!states.TryGetValue(id, out var state)) return new InteractionReply(InteractionStatus.UnknownEntity, true);
            if (state.Revision != request.Revision) return new InteractionReply(InteractionStatus.RevisionConflict, true, control: new ControlView(world.Epoch, state));
            if ((ControlAction)state.Operation != request.Action && alternate[id] != request.Action) return new InteractionReply(InteractionStatus.InvalidPayload, true);
            var next = state.Apply((ControlOperation)request.Action); states[id] = next;
            return new InteractionReply(InteractionStatus.Applied, true, control: new ControlView(world.Epoch, next));
        }
        internal void Stop() { states.Clear(); alternate.Clear(); }
    }
}
