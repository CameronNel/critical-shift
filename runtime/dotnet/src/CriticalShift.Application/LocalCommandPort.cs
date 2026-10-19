#nullable enable
using System;

namespace CriticalShift.Application
{
    /// <summary>
    /// One local fixture sender for an already registered connection. It builds intentions
    /// from current projections; the existing WorldSession still validates and owns outcomes.
    /// Compose exactly one port per connection before Start. This is not a network transport.
    /// </summary>
    public sealed class LocalCommandPort
    {
        private readonly WorldSession _world;
        private readonly Guid _connection;
        private long _sequence;
        private InteractionCommand? _lastTerminalCommand;

        public LocalCommandPort(WorldSession world, Guid connection)
        {
            _world = world ?? throw new ArgumentNullException(nameof(world));
            if (connection == Guid.Empty) throw new ArgumentException("A registered connection is required.", nameof(connection));
            if (world.View.Phase != WorldPhase.Setup)
                throw new InvalidOperationException("Compose the local sender before starting its world.");
            ActorId = world.ConnectedActorForComposition(connection) ??
                throw new ArgumentException("Register the local connection before composing its sender.", nameof(connection));
            _connection = connection;
        }

        public WorldSessionView World => _world.View;
        public Guid ActorId { get; }
        public long LastTerminalSequence => _sequence;
        public bool CanReplayLast => _lastTerminalCommand != null;
        public ObjectClaimView? GetObject(Guid id) => _world.GetObject(id);
        public WorkerView? GetWorker(Guid id) => _world.GetWorker(id);
        public ObjectClaimView? GetWorkerBodyClaim(Guid actor) => _world.GetWorkerBodyClaim(actor);
        public WorkerView? GetWorkerForBody(Guid entity) => _world.GetWorkerForBody(entity);
        public MachineView? GetMachine(Guid id) => _world.Production.GetMachine(id);
        public DoorView? GetDoor(Guid id) => _world.Doors.Get(id);
        public MaterialView? GetBatch(Guid id) => _world.Production.GetBatch(id);
        public ProductionSummary ProductionSummary => _world.Production.Summary;
        public ReactorView? Reactor => _world.Reactor.View;
        public PowerView? Power => _world.Reactor.PowerSummary;
        public ShiftContractView? Contract => _world.Contracts.View;
        public ShiftDebriefView? Debrief => _world.Debrief;
        public MedicalView? Medical => _world.Medical.View;
        public MedicalSummary MedicalSummary => _world.Medical.Summary;
        public SessionTraceView Trace => _world.Trace;

        public InteractionReply Grab(Guid entity) => Send(new InteractionCommand(_world.Epoch,
            NextSequence(), InteractionKind.Grab, entity, _world.GetObject(entity)?.Revision ?? 0));

        public InteractionReply Release(Guid entity) => Lease(entity, InteractionKind.Release);
        public InteractionReply Renew(Guid entity) => Lease(entity, InteractionKind.Renew, false);
        public InteractionReply OperateDoor(Guid doorId, DoorAction action) => Send(new InteractionCommand(
            _world.Epoch, NextSequence(), InteractionKind.Door, doorId,
            door: new DoorRequest(action, _world.Doors.Get(doorId)?.Revision ?? 0)));

        private InteractionReply Lease(Guid entity, InteractionKind kind, bool remember = true) => Send(new InteractionCommand(
            _world.Epoch, NextSequence(), kind, entity,
            leaseGeneration: _world.GetObject(entity)?.LeaseGeneration ?? 0), remember);

        public InteractionReply OperateMachine(Guid machineId, ProductionAction action,
            Guid container = default, bool bypass = false, bool powered = false)
        {
            var machine = _world.Production.GetMachine(machineId);
            Guid batchContainer = action == ProductionAction.Insert ? container : machine?.ContainerId ?? Guid.Empty;
            var custody = _world.GetObject(batchContainer);
            var batch = _world.Production.GetBatch(batchContainer);
            var request = new ProductionRequest(action, machine?.Revision ?? 0,
                action == ProductionAction.Insert ? container : Guid.Empty,
                action == ProductionAction.Insert || action == ProductionAction.Eject ? custody?.Revision ?? 0 : 0,
                action == ProductionAction.Insert || action == ProductionAction.Start ? batch?.Revision ?? 0 : 0,
                action == ProductionAction.Insert ? custody?.LeaseGeneration ?? 0 : 0,
                action == ProductionAction.Start && bypass, action == ProductionAction.SetPower && powered);
            return Send(new InteractionCommand(_world.Epoch, NextSequence(), InteractionKind.Production,
                machineId, production: request));
        }

        public InteractionReply OperateReactor(Guid reactorId, ReactorAction action,
            Guid container = default, bool cooling = false, ReactorOutputRouting outputRouting = ReactorOutputRouting.Balanced)
        {
            var reactor = _world.Reactor.View;
            Guid batchContainer = action == ReactorAction.Insert ? container : reactor?.Fuel?.ContainerId ?? Guid.Empty;
            var custody = _world.GetObject(batchContainer);
            var request = new ReactorRequest(action, reactor?.Revision ?? 0,
                action == ReactorAction.Insert ? container : Guid.Empty,
                action == ReactorAction.Insert || action == ReactorAction.Eject || action == ReactorAction.DiscardFuel ? custody?.Revision ?? 0 : 0,
                action == ReactorAction.Insert ? _world.Production.GetBatch(batchContainer)?.Revision ?? 0 : 0,
                action == ReactorAction.Insert ? custody?.LeaseGeneration ?? 0 : 0,
                action == ReactorAction.SetCooling && cooling,
                action == ReactorAction.SetOutputRouting ? outputRouting : ReactorOutputRouting.Balanced);
            return Send(new InteractionCommand(_world.Epoch, NextSequence(), InteractionKind.Reactor,
                reactorId, reactor: request));
        }

        public InteractionReply OperateMedical(Guid stationId, MedicalAction action, Guid body = default)
        {
            var station = _world.Medical.View;
            var claim = _world.GetObject(action == MedicalAction.Insert ? body : station?.BodyId ?? Guid.Empty);
            var request = new MedicalRequest(action, station?.Revision ?? 0,
                action == MedicalAction.Insert ? body : Guid.Empty,
                action == MedicalAction.Insert || action == MedicalAction.Eject || action == MedicalAction.EmergencyEject ? claim?.Revision ?? 0 : 0,
                action == MedicalAction.Insert ? claim?.LeaseGeneration ?? 0 : 0,
                action == MedicalAction.Start ? _world.GetWorker(station?.PatientId ?? Guid.Empty)?.Revision ?? 0 : 0);
            return Send(new InteractionCommand(_world.Epoch, NextSequence(),
                action == MedicalAction.EmergencyEject ? InteractionKind.MedicalEgress : InteractionKind.Medical, stationId, medical: request));
        }

        public SuitFittingSummary SuitFittingSummary => _world.SuitFitting.Summary;
        public InteractionReply OperateSuitFitting(Guid station, SuitFittingAction action)
        {
            var worker = _world.GetWorker(ActorId);
            return Send(new InteractionCommand(_world.Epoch, NextSequence(), InteractionKind.SuitFitting, station,
                suitFitting: new SuitFittingRequest(action, action == SuitFittingAction.Start || action == SuitFittingAction.Remove ? worker?.Revision ?? 0 : 0,
                    action == SuitFittingAction.Cancel ? worker?.SuitFitting?.Id ?? Guid.Empty : Guid.Empty)));
        }

        /// <summary>Resends the identical retained intent; its receipt never authorizes another physical effect.</summary>
        public InteractionReply ReplayLast()
        {
            if (_lastTerminalCommand == null) throw new InvalidOperationException("No terminal command is available to replay.");
            return _world.ExecuteInteraction(_connection, _lastTerminalCommand);
        }

        private long NextSequence() => checked(_sequence + 1);

        private InteractionReply Send(InteractionCommand command, bool remember = true)
        {
            var reply = _world.ExecuteInteraction(_connection, command);
            // Gameplay rejection finalizes the stream too. Pre-admission rejection does not.
            if (reply.IsTerminal)
            {
                _sequence = command.Sequence;
                if (remember) _lastTerminalCommand = command;
            }
            return reply;
        }
    }
}
