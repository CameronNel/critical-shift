using System;
using System.Collections.Generic;
using CriticalShift.Features.Power.Domain;
using CriticalShift.Features.Reactor.Domain;

namespace CriticalShift.Application
{
    /// <summary>One bounded reactor and reserve per world. Commands enter through the existing interaction stream.</summary>
    public sealed class ReactorOperations
    {
        private readonly WorldSession _world;
        private readonly InteractionWorld _interaction;
        private ReactorDefinition? _definition;
        private ReactorCore? _core;
        private PowerAccount? _power;
        private MaterialView? _input;
        private PowerView? _terminalPower;
        private Guid _id, _cycle, _coolingCause;
        private long _revision;
        internal ReactorOperations(WorldSession world, InteractionWorld interaction)
        { _world = world; _interaction = interaction; }

        public ReactorView? View => _core == null ? null : new ReactorView(_world.Epoch, _id, _definition!.Id,
            _revision, (ReactorMode)(int)_core.Mode, _core.Cooling, _core.SuspectFuel, _core.WorkMilliseconds,
            _core.RemainingFuelMilliseconds, _core.InstabilityMilliseconds, _cycle,
            _input == null ? null : _world.Production.GetBatch(_input.ContainerId), ProjectPower(_power!));
        public PowerView? PowerSummary => _power == null ? _terminalPower : ProjectPower(_power);

        public void Register(Guid id, ReactorDefinition definition) => _world.RegisterProduction(() =>
        {
            if (definition == null) throw new ArgumentNullException(nameof(definition));
            if (_core != null) throw new InvalidOperationException("This slice permits one reactor per world.");
            var core = new ReactorCore(definition.Rules);
            var power = new PowerAccount(definition.ReserveCapacity, definition.InitialReserve);
            _interaction.RegisterProductionSlot(id);
            _id = id; _definition = definition; _core = core; _power = power;
        });

        internal InteractionReply Apply(Guid actor, Guid id, ReactorRequest request)
        {
            if (_core == null || id != _id) return Reply(ReactorStatus.UnknownReactor);
            if (request.Revision != _revision) return Reply(ReactorStatus.RevisionConflict);
            switch (request.Action)
            {
                case ReactorAction.Insert: return Insert(actor, request);
                case ReactorAction.Eject: return Eject(request);
                case ReactorAction.Start: return Start();
                case ReactorAction.SetCooling: return Commit(_core.SetCooling(request.Cooling), _power!, ReactorEvent.CoolingChanged);
                case ReactorAction.Shutdown: return Commit(_core.Shutdown(), _power!, ReactorEvent.Shutdown);
                case ReactorAction.ResetTrip:
                    return !_core.CanReset ? Reply(ReactorStatus.Unsafe) : Commit(_core.ResetTrip(), _power!, ReactorEvent.Reset);
                case ReactorAction.EmergencyCooling:
                    if (_core.Mode == CoreMode.Empty || _core.Mode == CoreMode.Exhausted) return Reply(ReactorStatus.InvalidState);
                    var cooled = _core.EmergencyCooling();
                    if (ReferenceEquals(cooled, _core)) return Reply(ReactorStatus.NoChange);
                    if (!_power!.TrySpend(_definition!.EmergencyCost, out var afterCooling)) return Reply(ReactorStatus.InsufficientReserve);
                    return Commit(cooled, afterCooling, ReactorEvent.EmergencyCooling, _definition.EmergencyCost);
                case ReactorAction.AuxiliaryPower:
                    if (!_power!.TrySpend(_definition!.AuxiliaryCost, out var afterAuxiliary)) return Reply(ReactorStatus.InsufficientReserve);
                    return Commit(_core, afterAuxiliary, ReactorEvent.AuxiliaryPower, _definition.AuxiliaryCost);
                default: throw new InvalidOperationException("Unvalidated reactor action reached the owner.");
            }
        }

        private InteractionReply Insert(Guid actor, ReactorRequest request)
        {
            if (_core!.Mode != CoreMode.Empty) return Reply(ReactorStatus.InvalidState);
            var fuel = _world.Production.GetBatch(request.ContainerId);
            if (fuel == null) return Reply(ReactorStatus.UnknownBatch);
            if (fuel.Revision != request.BatchRevision) return Reply(ReactorStatus.RevisionConflict);
            if (fuel.Kind != MaterialKind.Fuel) return Reply(ReactorStatus.WrongFuel);
            if (fuel.Units > _definition!.Rules.MaximumFuelUnits) return Reply(ReactorStatus.OverCapacity);
            var next = _core.Load(fuel.Units, fuel.Contamination > _definition.ContaminationTolerance ||
                (fuel.Flags & MaterialFlags.BypassedInspection) != 0);
            long revision = checked(_revision + 1);
            var custody = _interaction.InsertBatch(request.ContainerId, actor, request.LeaseGeneration, request.ObjectRevision, _id);
            if (!custody.HasNewCommit) return Reply(ReactorStatus.CustodyRejected, custody: custody);
            _core = next; _input = fuel; _revision = revision;
            return Reply(ReactorStatus.Applied, Change(ReactorEvent.Inserted, _world.View.ElapsedMilliseconds), custody);
        }

        private InteractionReply Eject(ReactorRequest request)
        {
            if (!_core!.CanEject || _input == null) return Reply(ReactorStatus.InvalidState);
            var next = _core.Eject();
            long revision = checked(_revision + 1);
            var fuel = _input; var cycle = _cycle;
            var custody = _interaction.EjectBatch(_id, request.ObjectRevision);
            if (!custody.HasNewCommit) return Reply(ReactorStatus.CustodyRejected, custody: custody);
            _core = next; _input = null; _cycle = Guid.Empty; _revision = revision;
            // Preserve the original input and cycle separately from the resulting empty live view.
            return Reply(ReactorStatus.Applied, Change(ReactorEvent.Ejected, _world.View.ElapsedMilliseconds,
                fuel: fuel, cycle: cycle), custody);
        }

        private InteractionReply Start()
        {
            if (_core!.Mode == CoreMode.Running) return Reply(ReactorStatus.NoChange);
            if (_core.Mode != CoreMode.Loaded && _core.Mode != CoreMode.Shutdown) return Reply(ReactorStatus.InvalidState);
            if (!_core.Cooling) return Reply(ReactorStatus.NoCooling);
            if (!_core.CanStart) return Reply(ReactorStatus.Unsafe);
            if (!_power!.TrySpend(_definition!.StartupCost, out var nextPower)) return Reply(ReactorStatus.InsufficientReserve);
            bool firstStart = _cycle == Guid.Empty;
            if (firstStart && !_world.Production.HasFuelHistoryCapacity) return Reply(ReactorStatus.HistoryCapacityReached);
            var next = _core.Start();
            long revision = checked(_revision + 1);
            Guid cycle = firstStart ? Guid.NewGuid() : _cycle;
            if (firstStart)
            {
                var plan = _world.Production.PrepareFuel(_input!.ContainerId, _input.Revision, cycle, _id, _definition.Id);
                _world.Production.ReserveFuel(plan);
            }
            // No callbacks or awaits between material reservation, reserve spending and core state installation.
            _core = next; _power = nextPower; _cycle = cycle; _revision = revision;
            return Reply(ReactorStatus.Applied, Change(ReactorEvent.Started, _world.View.ElapsedMilliseconds, spent: _definition.StartupCost));
        }

        private InteractionReply Commit(ReactorCore core, PowerAccount power, ReactorEvent kind, long spent = 0)
        {
            if (ReferenceEquals(core, _core) && ReferenceEquals(power, _power)) return Reply(ReactorStatus.NoChange);
            long revision = checked(_revision + 1);
            if (kind == ReactorEvent.CoolingChanged && !core.Cooling) _coolingCause = Guid.NewGuid();
            _core = core; _power = power; _revision = revision;
            return Reply(ReactorStatus.Applied, Change(kind, _world.View.ElapsedMilliseconds,
                kind == ReactorEvent.CoolingChanged && !core.Cooling ? ReactorRisk.CoolingLost : ReactorRisk.None, spent: spent));
        }

        internal IReadOnlyList<ReactorChange> AdvanceTo(long shiftMilliseconds)
        {
            if (_core == null) return Array.Empty<ReactorChange>();
            var step = _core.AdvanceTo(shiftMilliseconds);
            if (ReferenceEquals(step.State, _core)) return Array.Empty<ReactorChange>();
            // Sampling an idle core advances its private clock, not the public command revision.
            // Compare projected state, not event count: sub-quantum work and cooldown are visible
            // changes even when no generated-power, warning or stop event is emitted.
            bool projectionChanged = step.State.Mode != _core.Mode || step.State.Cooling != _core.Cooling ||
                step.State.SuspectFuel != _core.SuspectFuel || step.State.WorkMilliseconds != _core.WorkMilliseconds ||
                step.State.RemainingFuelMilliseconds != _core.RemainingFuelMilliseconds ||
                step.State.InstabilityMilliseconds != _core.InstabilityMilliseconds || step.Quanta != 0 ||
                step.WarningAt.HasValue || step.StoppedAt.HasValue;
            if (!projectionChanged)
            {
                _core = step.State;
                return Array.Empty<ReactorChange>();
            }
            long reserve = checked(step.Quanta * _definition!.Rules.ReservePerQuantum);
            long grid = checked(step.Quanta * _definition.Rules.GridPerQuantum);
            var power = _power!.Credit(reserve, grid);
            long revision = checked(_revision + 1);
            bool exhausted = step.StoppedAt.HasValue && step.State.Mode == CoreMode.Exhausted;
            if (exhausted) _world.Production.FinishFuel(_cycle);
            _core = step.State; _power = power; _revision = revision;
            var changes = new List<ReactorChange>(3);
            if (step.Quanta > 0) changes.Add(Change(ReactorEvent.Generated, step.ActiveUntil, generated: checked(reserve + grid)));
            if (step.WarningAt.HasValue) changes.Add(Change(ReactorEvent.Warning, step.WarningAt.Value, (ReactorRisk)(int)step.Risk));
            if (step.StoppedAt.HasValue) changes.Add(Change(exhausted ? ReactorEvent.FuelExhausted : ReactorEvent.Tripped,
                step.StoppedAt.Value, exhausted ? ReactorRisk.None : (ReactorRisk)(int)step.Risk));
            changes.Sort((a, b) => { int time = a.ShiftMilliseconds.CompareTo(b.ShiftMilliseconds); return time != 0 ? time : a.Kind.CompareTo(b.Kind); });
            return changes.AsReadOnly();
        }

        internal void Clear()
        {
            if (_power != null) _terminalPower = ProjectPower(_power);
            _core = null; _power = null; _definition = null; _input = null;
            _id = Guid.Empty; _cycle = Guid.Empty; _coolingCause = Guid.Empty;
        }
        private ReactorChange Change(ReactorEvent kind, long at, ReactorRisk risk = ReactorRisk.None,
            long generated = 0, long spent = 0, MaterialView? fuel = null, Guid? cycle = null)
        {
            fuel = fuel ?? _input;
            Guid cause = risk == ReactorRisk.CoolingLost ? _coolingCause : fuel?.CauseId ?? Guid.NewGuid();
            if (cause == Guid.Empty) throw new InvalidOperationException("A committed reactor event requires a cause.");
            return new ReactorChange(kind, View!, at, cycle ?? _cycle, fuel?.BatchId ?? Guid.Empty, cause, risk, generated, spent);
        }
        private InteractionReply Reply(ReactorStatus status, ReactorChange? change = null, InteractionReply? custody = null)
        {
            var outcome = status == ReactorStatus.Applied ? InteractionStatus.Applied :
                status == ReactorStatus.NoChange ? InteractionStatus.NoChange : InteractionStatus.ReactorRejected;
            return new InteractionReply(outcome, true, custody?.State, reactor: new ReactorReply(status, View, change));
        }
        private static PowerView ProjectPower(PowerAccount p) =>
            new PowerView(p.Initial, p.Capacity, p.Available, p.Generated, p.Spent, p.Delivered, p.Spilled);
    }
}
