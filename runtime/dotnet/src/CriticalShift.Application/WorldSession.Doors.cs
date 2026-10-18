#nullable enable
using System;

namespace CriticalShift.Application
{
    public sealed partial class WorldSession
    {
        internal void RegisterDoor(Guid id, string sourceId, DoorState initial, DoorState evacuation, bool playerOperable)
        {
            RequireIdle();
            if (View.Phase != WorldPhase.Setup) throw new InvalidOperationException("Door definitions are setup-only.");
            long next = NextRevision();
            _interaction.RegisterDoor(id, sourceId, initial, evacuation, playerOperable); _revision = next;
        }

        /// <summary>Explicit host operation. No reactor mode, timer or collision can infer this transition.</summary>
        public DoorEvacuationReply BeginEvacuation(Guid epoch, Guid causeId)
        {
            RequireIdle();
            var readiness = Readiness(epoch);
            DoorEvacuationStatus? rejection = readiness switch
            {
                WorldControlStatus.WrongEpoch => DoorEvacuationStatus.WrongEpoch,
                WorldControlStatus.NotReady => DoorEvacuationStatus.NotReady,
                WorldControlStatus.Ended => DoorEvacuationStatus.WorldEnded,
                WorldControlStatus.Stopped => DoorEvacuationStatus.WorldStopped,
                WorldControlStatus.Faulted => DoorEvacuationStatus.WorldFaulted,
                null => (DoorEvacuationStatus?)null,
                _ => throw new InvalidOperationException("Unmapped evacuation readiness.")
            };
            if (!rejection.HasValue && causeId == Guid.Empty) rejection = DoorEvacuationStatus.InvalidCause;
            if (!rejection.HasValue && View.Phase == WorldPhase.Paused) rejection = DoorEvacuationStatus.Paused;
            if (rejection.HasValue)
            {
                var denied = new DoorEvacuationReply(rejection.Value, causeId);
                _diagnostics.Append(View, epoch, SessionTraceKind.Evacuation, causeId: causeId, evacuation: denied);
                return denied;
            }
            long next = NextRevision(); _executing = true;
            try
            {
                var reply = Doors.Evacuate(causeId);
                if (reply.Changed) _revision = next;
                _diagnostics.Append(View, epoch, SessionTraceKind.Evacuation, changed: reply.Changed, causeId: reply.CauseId, evacuation: reply);
                foreach (var door in reply.Changes)
                    _diagnostics.Append(View, epoch, SessionTraceKind.Door, entity: door.Id, changed: true, causeId: causeId,
                        interaction: new InteractionReply(InteractionStatus.Applied, false,
                            door: new DoorReply(DoorStatus.Applied, door, previousRevision: door.Revision - 1, causeId: causeId)));
                return reply;
            }
            catch { FailClosed(); throw; }
            finally { _executing = false; }
        }
    }
}
