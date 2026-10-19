using System;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Predicts partial fuel loss, conversion, clocks and both cycles' output from authored inputs.</summary>
    internal static class ReactorDiscardSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }
        internal static int Exercise(Random random, bool omitSpent)
        {
            int units = random.Next(2, 101), nextUnits = random.Next(2, 51), contamination = random.Next(1001), moisture = random.Next(1001);
            long perUnit = random.Next(2, 201), quantum = random.Next(1, (int)perUnit + 1), duration = units * perUnit;
            long burn = random.Next(0, (int)duration), reset = random.Next(0, 1001), capacity = random.Next(20, 101);
            int reserveRate = random.Next(9), gridRate = random.Next(1, 9); var route = (ReactorOutputRouting)random.Next(3);
            var world = new WorldSession(new WorldSessionConfiguration(42, 1000000, true), new Access());
            world.RegisterConnection(Id(1100), Id(1101));
            world.Production.RegisterBatch(Id(1102), Id(1103), Id(1104), Id(1105), MaterialKind.Fuel, units, moisture, contamination);
            world.Production.RegisterBatch(Id(1106), Id(1107), Id(1104), Id(1108), MaterialKind.Fuel, nextUnits);
            world.Reactor.Register(Id(1109), new ReactorDefinition(Id(1110), capacity, 10, millisecondsPerFuelUnit: perUnit,
                powerQuantumMilliseconds: quantum, reservePerQuantum: reserveRate, gridPerQuantum: gridRate,
                warningMilliseconds: 1000000, tripMilliseconds: 2000000, resetMilliseconds: reset));
            var port = new LocalCommandPort(world, Id(1100)); world.Start(); int steps = 0;
            long host = 0, shift = 0, available = 10, generated = 0, delivered = 0, spent = 0, spilled = 0;
            void Applied(InteractionReply reply) => Require(reply.HasNewCommit, "Authored fuel discard action rejected.");
            InteractionReply Act(ReactorAction action) => port.OperateReactor(Id(1109), action);
            void Power()
            {
                var p = world.Reactor.PowerSummary!;
                Require(p.Initial == 10 && p.Capacity == capacity && p.Available == available && p.Generated == generated &&
                    p.Delivered == delivered && p.Spent == spent && p.Spilled == spilled &&
                    p.Initial + p.Generated == p.Available + p.Delivered + p.Spent + p.Spilled,
                    "Discard power differs from independent lost-fuel ledger.");
                Require(world.View.HostMilliseconds == host && world.View.ElapsedMilliseconds == shift,
                    "Discard changed independently predicted host or shift clock."); steps++;
            }
            void Credit(long quanta)
            {
                long total = quanta * (reserveRate + gridRate), reserve = route == ReactorOutputRouting.GridPriority ? 0 :
                    route == ReactorOutputRouting.ReservePriority ? total : quanta * reserveRate;
                long store = Math.Min(reserve, capacity - available); generated += total; available += store; delivered += total - reserve; spilled += reserve - store;
            }
            void Start(int container)
            {
                Applied(port.Grab(Id(container))); Applied(port.OperateReactor(Id(1109), ReactorAction.Insert, Id(container)));
                Applied(Act(ReactorAction.Start)); available -= 3; spent += 3; Power();
            }
            Applied(port.OperateReactor(Id(1109), ReactorAction.SetCooling, cooling: true));
            var routing = port.OperateReactor(Id(1109), ReactorAction.SetOutputRouting, outputRouting: route);
            Require(routing.Reactor?.Status == (route == ReactorOutputRouting.Balanced ? ReactorStatus.NoChange : ReactorStatus.Applied), "Discard route setup rejected.");
            Start(1102); host += burn; shift += burn; world.AdvanceTo(host); Credit(burn / quantum); Power();
            Applied(Act(ReactorAction.Shutdown));
            world.Pause(world.Epoch); host += random.Next(1, 1001); world.AdvanceTo(host);
            Require(Act(ReactorAction.DiscardFuel).Status == InteractionStatus.ActorUnavailable, "Paused discard consumed fuel."); Power(); world.Resume(world.Epoch);
            Applied(port.OperateReactor(Id(1109), ReactorAction.SetCooling, cooling: false));
            Require(Act(ReactorAction.DiscardFuel).Reactor?.Status == ReactorStatus.NoCooling, "Closed cooling admitted discard.");
            Applied(port.OperateReactor(Id(1109), ReactorAction.SetCooling, cooling: true));
            long instability = contamination > 500 ? burn : 0;
            if (instability > reset)
            {
                Require(Act(ReactorAction.DiscardFuel).Reactor?.Status == ReactorStatus.Unsafe, "Hot core admitted discard.");
                long wait = instability - reset; host += wait; shift += wait; world.AdvanceTo(host);
            }
            var before = world.Reactor.View!; var oldCycle = before.CycleId; long revision = before.Revision, claim = world.GetObject(Id(1102))!.Revision;
            var result = Act(ReactorAction.DiscardFuel); Applied(result); long sequence = port.LastTerminalSequence; var change = result.Reactor!.Change!;
            var batch = world.Production.GetBatch(Id(1102))!; var current = world.Reactor.View!;
            Require(batch.Kind == (omitSpent ? MaterialKind.Fuel : MaterialKind.SpentFuel), "Discard material differs from independent spent-fuel ledger.");
            Require(batch.Units == units && batch.Moisture == moisture && batch.Contamination == contamination && batch.Revision == 1 &&
                batch.ParentBatchId == Id(1103) && batch.CauseId == Id(1105) && batch.OriginId == Id(1104) && batch.BatchId != Id(1103) &&
                world.Production.Summary.CompletedCycles == 1 && world.Production.Summary.PendingCycles == 0 && world.Production.Summary.WasteUnits == 0 &&
                world.Production.Summary.ActiveUnits == units + nextUnits && world.GetObject(Id(1102))!.HolderId == null && world.GetObject(Id(1102))!.SlotId == null,
                "Discard lost independent conversion quantity, history or custody.");
            Require(current.Mode == ReactorMode.Empty && current.WorkMilliseconds == 0 && current.CycleId == Guid.Empty && current.Fuel == null &&
                current.Cooling && current.OutputRouting == route && current.InstabilityMilliseconds == 0 &&
                change.Kind == ReactorEvent.FuelDiscarded && change.CycleId == oldCycle && change.InputBatchId == Id(1103) && change.CauseId == Id(1105) &&
                change.DiscardedFuelMilliseconds == duration - burn && change.ShiftMilliseconds == shift && change.GeneratedUnits == 0 && change.SpentUnits == 0 &&
                change.DiscardedFuel?.Input.BatchId == Id(1103) && change.DiscardedFuel.Output?.BatchId == batch.BatchId &&
                world.Trace.Records.Count(r => r.ReactorEvent == ReactorEvent.FuelDiscarded) == 1,
                "Discard event differs from independent partial-cycle remainder and lineage."); Power();
            Start(1106); host += quantum - 1; shift += quantum - 1; world.AdvanceTo(host); Power();
            Require(world.Reactor.View!.WorkMilliseconds == quantum - 1, "Discard carried prior work into fresh fuel.");
            host++; shift++; world.AdvanceTo(host); Credit(1); Power();
            var replay = world.ExecuteInteraction(Id(1100), new InteractionCommand(world.Epoch, sequence, InteractionKind.Reactor, Id(1109),
                reactor: new ReactorRequest(ReactorAction.DiscardFuel, revision, objectRevision: claim)));
            Require(replay.IsReplay && !replay.HasNewCommit && world.Reactor.View!.Mode == ReactorMode.Running && world.Reactor.View.WorkMilliseconds == quantum &&
                world.Production.GetBatch(Id(1106))!.Kind == MaterialKind.Fuel && world.Production.Summary.CompletedCycles == 1,
                "Historical discard changed fresh fuel."); Power();
            world.Stop(); Require(world.Reactor.View == null && world.Production.GetConversion(oldCycle) == null &&
                world.Debrief!.Timeline.Count(r => r.ReactorEvent == ReactorEvent.FuelDiscarded && r.ReactorChange!.DiscardedFuelMilliseconds == duration - burn) == 1 &&
                change.DiscardedFuel!.Output!.Units == units, "Discard lost detached terminal incident evidence.");
            return steps + 8;
        }
    }
}
