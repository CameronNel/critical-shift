#nullable enable
using System;
using System.Collections.Generic;
using CriticalShift.Features.Interaction.Domain;

namespace CriticalShift.Application
{
    /// <summary>Door command/query facade; Interaction owns the store and WorldSession owns its lifetime.</summary>
    public sealed class DoorOperations
    {
        private readonly WorldSession _world;
        private readonly InteractionWorld _interaction;
        internal DoorOperations(WorldSession world, InteractionWorld interaction) { _world = world; _interaction = interaction; }
        public int Count => _interaction.DoorCount;
        public Guid? EvacuationCauseId => _interaction.EvacuationCauseId;
        public DoorView? Get(Guid id) => Project(_interaction.GetDoor(id));
        public DoorView? GetBySourceId(string sourceId) => Project(_interaction.GetDoorBySourceId(sourceId));
        public void Register(Guid id, string sourceId, DoorState initialState, DoorState evacuationState, bool playerOperable = true) =>
            _world.RegisterDoor(id, sourceId, initialState, evacuationState, playerOperable);
        internal InteractionReply Apply(Guid id, DoorRequest request)
        {
            var before = _interaction.GetDoor(id);
            var result = _interaction.SetDoorOpen(id, request.DoorRevision, request.Action == DoorAction.Open);
            var status = result.Error switch
            {
                DoorError.None => result.Changed ? DoorStatus.Applied : DoorStatus.NoChange,
                DoorError.UnknownDoor => DoorStatus.UnknownDoor,
                DoorError.RevisionConflict => DoorStatus.RevisionConflict,
                DoorError.Locked => DoorStatus.Locked,
                DoorError.NotOperable => DoorStatus.NotOperable,
                _ => throw new InvalidOperationException("A stopped door store reached active command admission.")
            };
            var reply = new DoorReply(status, Project(result.State), request.Action, before?.Revision, result.Changed ? Guid.NewGuid() : Guid.Empty);
            return new InteractionReply(result.Changed ? InteractionStatus.Applied : status == DoorStatus.NoChange ? InteractionStatus.NoChange : InteractionStatus.DoorRejected,
                true, door: reply);
        }
        internal DoorEvacuationReply Evacuate(Guid causeId)
        {
            var result = _interaction.EvacuateDoors(causeId);
            var status = result.Kind switch
            {
                EvacuationResultKind.Applied => DoorEvacuationStatus.Applied,
                EvacuationResultKind.Duplicate => DoorEvacuationStatus.Duplicate,
                EvacuationResultKind.AlreadyActive => DoorEvacuationStatus.AlreadyActive,
                _ => throw new InvalidOperationException("A stopped door store reached active evacuation admission.")
            };
            var changes = new List<DoorView>(result.Changes.Count);
            foreach (var state in result.Changes) changes.Add(Project(state)!);
            return new DoorEvacuationReply(status, result.CauseId, changes.AsReadOnly());
        }
        private DoorView? Project(DoorSnapshot? state) => state == null ? null : new DoorView(_world.Epoch, state.Id,
            state.SourceId, state.Revision, (DoorState)(int)state.Mode, (DoorState)(int)state.EvacuationMode, state.PlayerOperable);
    }
}
