using System;
using System.Collections.Generic;
using CriticalShift.Features.Materials.Domain;
using CriticalShift.Features.Production.Domain;

namespace CriticalShift.Application
{
    /// <summary>
    /// Production command/query port, not a second world. Mutating commands enter through
    /// WorldSession.ExecuteInteraction and share its receipts, actor validation and reentrancy guard.
    /// </summary>
    public sealed partial class ProductionOperations
    {
        private readonly WorldSession _world;
        private readonly InteractionWorld _interaction;
        private readonly MaterialLedger _materials;
        private readonly Dictionary<Guid, MachineState> _machines = new Dictionary<Guid, MachineState>();
        private readonly Dictionary<Guid, MachineRecipe> _recipes = new Dictionary<Guid, MachineRecipe>();
        private readonly int _machineCapacity;
        private int _completed, _cancelled;
        private ProductionSummary? _final;
        internal ProductionOperations(WorldSession world, InteractionWorld interaction, int objectCapacity, int machines, int cycles)
        {
            _world = world; _interaction = interaction; _machineCapacity = machines;
            _materials = new MaterialLedger(objectCapacity, cycles);
        }
        public int MachineCount => _machines.Count;
        public int BatchCount => _materials.Count;
        public ProductionSummary Summary => _final ?? new ProductionSummary(_materials.IssuedUnits,
            _materials.ActiveUnits, _materials.WasteUnits, _completed, _cancelled, _materials.PendingCount);
        public MaterialView? GetBatch(Guid container) => Project(_materials.Get(container));
        public MachineView? GetMachine(Guid id) => _machines.TryGetValue(id, out var s) ? Project(s) : null;
        public ConversionView? GetConversion(Guid cycle)
        {
            var receipt = _materials.GetReceipt(cycle);
            return receipt == null ? null : Project(receipt);
        }
        internal bool OwnsBatch(Guid container) => _materials.Get(container) != null;

        public void RegisterMachine(Guid id, MachineRecipe recipe) => _world.RegisterProduction(() =>
        {
            if (recipe == null) throw new ArgumentNullException(nameof(recipe));
            var state = new MachineState(id);
            if (_machines.Count >= _machineCapacity || _machines.ContainsKey(id))
                throw new InvalidOperationException("Machine capacity or duplicate identity.");
            _interaction.RegisterProductionSlot(id);
            _machines.Add(id, state); _recipes.Add(id, recipe);
        });

        public void RegisterBatch(Guid container, Guid batchId, Guid origin, Guid cause,
            MaterialKind kind, int units, int moisture = 0, int contamination = 0) => _world.RegisterProduction(() =>
        {
            if (!Enum.IsDefined(typeof(MaterialKind), kind)) throw new ArgumentOutOfRangeException(nameof(kind));
            var batch = new BatchSnapshot(container, batchId, origin, cause, (BatchKind)(int)kind, units, moisture, contamination);
            _materials.ValidateRegistration(batch);
            _interaction.RegisterObject(container);
            _materials.Register(batch);
        });

        internal InteractionReply Apply(Guid actor, Guid machineId, ProductionRequest request)
        {
            if (!_machines.TryGetValue(machineId, out var machine)) return Reply(ProductionStatus.UnknownMachine, null);
            if (request.MachineRevision != machine.Revision) return Reply(ProductionStatus.RevisionConflict, machine);
            switch (request.Action)
            {
                case ProductionAction.Insert: return Insert(actor, machine, request);
                case ProductionAction.Eject: return Eject(machine, request);
                case ProductionAction.Start: return Start(machine, request);
                case ProductionAction.SetPower:
                    var power = machine.SetPower(request.Powered);
                    if (ReferenceEquals(machine, power)) return Reply(ProductionStatus.NoChange, machine);
                    _machines[machine.Id] = power; return Reply(ProductionStatus.Applied, power);
                case ProductionAction.Repair:
                    if (machine.Powered) return Reply(ProductionStatus.PowerMustBeOff, machine);
                    if (machine.Mode != MachineMode.Jammed) return Reply(ProductionStatus.InvalidState, machine);
                    var repaired = machine.Repair(); _machines[machine.Id] = repaired; return Reply(ProductionStatus.Applied, repaired);
                case ProductionAction.Resume:
                    if (!machine.Powered) return Reply(ProductionStatus.NoPower, machine);
                    if (machine.Mode != MachineMode.PowerPaused) return Reply(ProductionStatus.InvalidState, machine);
                    var resumed = machine.Resume(); _machines[machine.Id] = resumed; return Reply(ProductionStatus.Applied, resumed);
                case ProductionAction.CancelCycle:
                    if (machine.Powered) return Reply(ProductionStatus.PowerMustBeOff, machine);
                    if (!machine.CanCancel) return Reply(ProductionStatus.InvalidState, machine);
                    var cancelled = machine.Reset(true);
                    var receipt = _materials.Finish(machine.CycleId, true);
                    if (receipt.Status != ConversionStatus.Cancelled)
                        throw new InvalidOperationException("A completed cycle cannot be cancelled.");
                    _machines[machine.Id] = cancelled; _cancelled++;
                    return Reply(ProductionStatus.Applied, cancelled, change: Conversion(receipt, cancelled));
                default: throw new InvalidOperationException("An unvalidated production request reached a workflow.");
            }
        }

        private InteractionReply Insert(Guid actor, MachineState machine, ProductionRequest request)
        {
            if (machine.Mode != MachineMode.Idle) return Reply(ProductionStatus.InvalidState, machine);
            if (_interaction.SlotOccupant(machine.Id).HasValue) return Reply(ProductionStatus.Occupied, machine);
            var batch = _materials.Get(request.ContainerId);
            if (batch == null) return Reply(ProductionStatus.UnknownBatch, machine);
            if (batch.Revision != request.BatchRevision) return Reply(ProductionStatus.RevisionConflict, machine);
            var recipe = _recipes[machine.Id];
            if ((int)batch.Kind != (int)recipe.Input) return Reply(ProductionStatus.WrongInput, machine);
            if (batch.Units > recipe.MaximumUnits) return Reply(ProductionStatus.OverCapacity, machine);
            var next = machine.Touch(); // overflow checked before changing custody
            var moved = _interaction.InsertBatch(request.ContainerId, actor, request.LeaseGeneration,
                request.ObjectRevision, machine.Id);
            if (!moved.HasNewCommit) return Reply(ProductionStatus.CustodyRejected, machine, moved.State, moved.Status);
            _machines[machine.Id] = next;
            return Reply(ProductionStatus.Applied, next, moved.State);
        }
        private InteractionReply Eject(MachineState machine, ProductionRequest request)
        {
            if (!machine.CanEject) return Reply(ProductionStatus.InvalidState, machine);
            if (!_interaction.SlotOccupant(machine.Id).HasValue) return Reply(ProductionStatus.NoInput, machine);
            var next = machine.Reset(false);
            var moved = _interaction.EjectBatch(machine.Id, request.ObjectRevision);
            if (!moved.HasNewCommit) return Reply(ProductionStatus.CustodyRejected, machine, moved.State, moved.Status);
            _machines[machine.Id] = next;
            return Reply(ProductionStatus.Applied, next, moved.State);
        }
        private InteractionReply Start(MachineState machine, ProductionRequest request)
        {
            if (!machine.Powered) return Reply(ProductionStatus.NoPower, machine);
            if (!machine.CanStart) return Reply(ProductionStatus.InvalidState, machine);
            var occupant = _interaction.SlotOccupant(machine.Id);
            if (!occupant.HasValue) return Reply(ProductionStatus.NoInput, machine);
            var input = _materials.Get(occupant.Value) ?? throw new InvalidOperationException("Machine custody has no material record.");
            if (input.Revision != request.BatchRevision) return Reply(ProductionStatus.RevisionConflict, machine);
            var recipe = _recipes[machine.Id];
            if ((int)input.Kind != (int)recipe.Input) return Reply(ProductionStatus.WrongInput, machine);
            if (input.Units > recipe.MaximumUnits) return Reply(ProductionStatus.OverCapacity, machine);
            bool wet = input.Moisture > recipe.MoistureTolerance;
            if (wet && !request.Bypass) return Reply(ProductionStatus.WetInput, machine);
            if ((long)input.Units * recipe.YieldPermille / 1000 == 0) return Reply(ProductionStatus.OutputTooSmall, machine);
            if (!_materials.HasCycleCapacity) return Reply(ProductionStatus.HistoryCapacityReached, machine);
            var cycle = Guid.NewGuid();
            var next = machine.Begin(cycle, request.Bypass ? recipe.BypassDurationMilliseconds : recipe.DurationMilliseconds,
                wet ? recipe.WetJamAfterMilliseconds : 0, _world.View.ElapsedMilliseconds);
            var plan = _materials.Prepare(input.ContainerId, input.Revision, cycle, machine.Id, recipe.Id, Guid.NewGuid(),
                (BatchKind)(int)recipe.Output, recipe.YieldPermille, recipe.OutputMoisture, request.Bypass);
            // All expected rejection paths above are side-effect-free. No adapter callback can run
            // between reserved output capacity and the matching process state installation.
            _materials.Reserve(plan); _machines[machine.Id] = next;
            return Reply(ProductionStatus.Applied, next);
        }
    }
}
