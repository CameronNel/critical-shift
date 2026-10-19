using System;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Authored output, clock, running-work and reserve ledger; no expected allocation is learned from replies.</summary>
    internal static class ReactorRoutingSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }
        internal static int Exercise(Random random, bool ignoreFirstRouting)
        {
            long quantum = random.Next(2, 251), fuelDuration = quantum * 100;
            int reserveRate = random.Next(0, 9), gridRate = random.Next(1, 9); long capacity = random.Next(20, 101);
            var world = new WorldSession(new WorldSessionConfiguration(42, 1000000, true), new Access());
            world.RegisterConnection(Id(1050), Id(1051));
            world.Production.RegisterBatch(Id(1052), Id(1053), Id(1054), Id(1055), MaterialKind.Fuel, 100);
            world.Reactor.Register(Id(1056), new ReactorDefinition(Id(1057), capacity, 10, millisecondsPerFuelUnit: quantum,
                powerQuantumMilliseconds: quantum, reservePerQuantum: reserveRate, gridPerQuantum: gridRate));
            world.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(quantum, 4, 1));
            var port = new LocalCommandPort(world, Id(1050)); world.Start();
            long host = 0, shift = 0, work = 0, available = 10, generated = 0, spent = 0, delivered = 0, spilled = 0;
            bool paused = false, backupPending = false, controlUsed = false; int steps = 0;
            var route = ReactorOutputRouting.Balanced; var mode = ReactorMode.Loaded;
            InteractionReply Act(ReactorAction action) => port.OperateReactor(Id(1056), action);
            void Accepted(InteractionReply reply) => Require(reply.HasNewCommit, "Authored reactor routing action rejected.");
            Accepted(port.Grab(Id(1052))); Accepted(port.OperateReactor(Id(1056), ReactorAction.Insert, Id(1052)));
            Accepted(port.OperateReactor(Id(1056), ReactorAction.SetCooling, cooling: true));
            void Check()
            {
                var state = world.Reactor.View!; var power = state.Power; var fuel = world.Production.GetBatch(Id(1052))!;
                Require(power.Available == available && power.Generated == generated && power.Spent == spent && power.Delivered == delivered && power.Spilled == spilled,
                    "Reactor output allocation differs from independent routed-quanta ledger.");
                Require(state.OutputRouting == route && state.Mode == mode && state.WorkMilliseconds == work && state.RemainingFuelMilliseconds == fuelDuration - work &&
                    state.Cooling && state.InstabilityMilliseconds == 0 && world.View.ElapsedMilliseconds == shift && world.View.HostMilliseconds == host,
                    "Routing changed independent fuel work, thermal state, valve or clocks.");
                Require(power.Initial == 10 && power.Capacity == capacity && power.Initial + power.Generated == power.Available + power.Spent + power.Delivered + power.Spilled &&
                    fuel.Units == 100 && fuel.CauseId == Id(1055) && fuel.OriginId == Id(1054) &&
                    fuel.Kind == (mode == ReactorMode.Exhausted ? MaterialKind.SpentFuel : MaterialKind.Fuel) &&
                    fuel.Revision == (mode == ReactorMode.Exhausted ? 1 : 0) &&
                    fuel.ParentBatchId == (mode == ReactorMode.Exhausted ? Id(1053) : Guid.Empty) &&
                    (mode == ReactorMode.Exhausted ? fuel.BatchId != Id(1053) : fuel.BatchId == Id(1053)),
                    "Routed output lost power balance or original material quantity/attribution."); steps++;
            }
            void Credit(long reserve, long grid)
            { long stored = Math.Min(reserve, capacity - available); available += stored; generated += reserve + grid; delivered += grid; spilled += reserve - stored; }
            void Advance(long delta)
            {
                host += delta;
                if (!paused)
                {
                    shift += delta;
                    if (mode == ReactorMode.Running)
                    {
                        long before = work; work += Math.Min(delta, fuelDuration - work); long quanta = work / quantum - before / quantum;
                        var effective = ignoreFirstRouting && !controlUsed && quanta > 0 ? ReactorOutputRouting.Balanced : route;
                        if (quanta > 0) controlUsed = true;
                        long total = quanta * (reserveRate + gridRate), reserve = effective == ReactorOutputRouting.GridPriority ? 0 :
                            effective == ReactorOutputRouting.ReservePriority ? total : quanta * reserveRate;
                        Credit(reserve, total - reserve); if (work == fuelDuration) mode = ReactorMode.Exhausted;
                    }
                    if (backupPending && shift >= quantum) { Credit(4, 0); backupPending = false; }
                }
                world.AdvanceTo(host); Check();
            }
            void Route(ReactorOutputRouting value)
            {
                var result = port.OperateReactor(Id(1056), ReactorAction.SetOutputRouting, outputRouting: value);
                Require(result.Reactor?.Status == (route == value ? ReactorStatus.NoChange : ReactorStatus.Applied), "Routing valve outcome differs from input ledger.");
                route = value; Check(); var retry = port.ReplayLast(); Require(retry.IsReplay && !retry.HasNewCommit, "Routing retry was not historical."); Check();
            }
            void Start()
            {
                var reply = Act(ReactorAction.Start);
                var outcome = mode == ReactorMode.Running ? ReactorStatus.NoChange : mode == ReactorMode.Exhausted ? ReactorStatus.InvalidState :
                    available < 3 ? ReactorStatus.InsufficientReserve : ReactorStatus.Applied;
                Require(reply.Reactor?.Status == outcome, "Routed core restart disagrees with independent reserve/mode admission.");
                if (outcome == ReactorStatus.Applied) { available -= 3; spent += 3; mode = ReactorMode.Running; } Check();
            }
            void Pause()
            { if (paused) world.Resume(world.Epoch); else world.Pause(world.Epoch); paused = !paused; Check(); }
            Accepted(Act(ReactorAction.StartBackup)); backupPending = true; Start(); Route(ReactorOutputRouting.ReservePriority); Advance(quantum);
            // A guaranteed nondefault quantum makes the omitted-route control fail in the power ledger.
            for (int operation = 0; operation < 48; operation++)
            {
                int choice = random.Next(6);
                if (choice == 0) Advance(random.Next(0, (int)(quantum * 4 + 1)));
                else if (choice == 1) Pause();
                else if (choice == 2 && !paused) Route((ReactorOutputRouting)random.Next(3));
                else if (choice == 3 && !paused) Start();
                else if (choice == 4 && !paused)
                {
                    var result = Act(ReactorAction.Shutdown); bool changes = mode == ReactorMode.Running;
                    Require(result.Reactor?.Status == (changes ? ReactorStatus.Applied : ReactorStatus.NoChange), "Routing shutdown disagrees with independent running state.");
                    if (changes) mode = ReactorMode.Shutdown; Check();
                }
                else Check();
            }
            if (paused) Pause();
            Route(ReactorOutputRouting.ReservePriority); Start();
            if (mode == ReactorMode.Running) Advance(fuelDuration - work);
            Require(world.Reactor.EmergencyPowerSummary!.ProducedUnits == 4, "Routing changed the independent reserve-only backup output.");
            world.Stop(); Require(world.Reactor.View == null, "Routing retained a live terminal reactor."); return steps + 1;
        }
    }
}
