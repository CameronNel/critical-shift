using System;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Input-driven isolation/work ledger, independent of production state transitions.</summary>
    internal static class TimedRepairSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid target, InteractionKind kind) => AccessDecision.Allowed; }

        internal static int Exercise(Random random, bool omitRepairCompletion)
        {
            long processing = random.Next(100, 1001), jam = random.Next(1, (int)processing);
            long clearing = random.Next(2, 60001), limit = jam + clearing + random.Next(1, 8001);
            var world = new WorldSession(new WorldSessionConfiguration(42, limit, true), new Access(), traceCapacity: 8);
            world.RegisterConnection(Id(960), Id(961));
            world.Production.RegisterBatch(Id(962), Id(963), Id(964), Id(965), MaterialKind.Ore, 10, 900, 35);
            world.Production.RegisterMachine(Id(966), new MachineRecipe(Id(967), MaterialKind.Ore, MaterialKind.CrushedOre,
                processing * 2, processing, jam, 100, yieldPermille: 800, repairDurationMilliseconds: clearing));
            var port = new LocalCommandPort(world, Id(960)); world.Start();
            Require(port.Grab(Id(962)).HasNewCommit && port.OperateMachine(Id(966), ProductionAction.Insert, Id(962)).HasNewCommit,
                "Repair model input setup failed.");
            var started = port.OperateMachine(Id(966), ProductionAction.Start, bypass: true);
            Require(started.HasNewCommit && started.Production!.Machine!.CycleId != Guid.Empty, "Repair model process start failed.");
            // Only this opaque committed identifier is bound from a reply; all expected timing/state comes from inputs.
            Guid cycle = started.Production!.Machine!.CycleId;
            long host = 0, shift = 0, work = 0, repairWork = 0, repairDuration = 0, revision = 2;
            var mode = ProductionMode.Processing;
            bool power = true, armed = true, paused = false, ended = false, pending = true;
            int completed = 0, cancelled = 0, steps = 0;
            void Check()
            {
                var summary = world.Production.Summary;
                Require(summary.CompletedCycles == completed && summary.CancelledCycles == cancelled && summary.PendingCycles == (pending ? 1 : 0) &&
                    summary.ActiveUnits == (completed == 0 ? 10 : 8) && summary.WasteUnits == (completed == 0 ? 0 : 2) && summary.IssuedUnits == 10,
                    "Repair material outcomes differ from independent reserved-input ledger.");
                Require(world.View.ElapsedMilliseconds == shift, "Repair shift clock differs from independent pause ledger.");
                if (!ended)
                {
                    var machine = world.Production.GetMachine(Id(966))!; var batch = world.Production.GetBatch(Id(962))!;
                    Require(machine.Mode == mode, "Repair mode differs from independent isolation ledger.");
                    Require(machine.Powered == power && machine.Revision == revision && machine.WorkMilliseconds == work &&
                        machine.RepairDurationMilliseconds == repairDuration && machine.RepairWorkMilliseconds == repairWork &&
                        machine.RepairRemainingMilliseconds == repairDuration - repairWork,
                        "Repair power, revision or separate work differs from independent ledger.");
                    Require(machine.CycleId == (mode == ProductionMode.Idle ? Guid.Empty : cycle) && machine.ContainerId == Id(962) &&
                        world.GetObject(Id(962))!.SlotId == Id(966), "Repair changed active cycle identity or original input custody.");
                    Require(batch.CauseId == Id(965) && batch.OriginId == Id(964) && batch.Contamination == 35 &&
                        batch.Kind == (completed == 0 ? MaterialKind.Ore : MaterialKind.CrushedOre) &&
                        batch.Units == (completed == 0 ? 10 : 8) && batch.Moisture == (completed == 0 ? 900 : 0) &&
                        batch.Flags == (completed == 0 ? MaterialFlags.None : MaterialFlags.BypassedInspection) &&
                        (completed == 0 ? batch.BatchId == Id(963) : batch.ParentBatchId == Id(963) && batch.BatchId != Id(963)),
                        "Repair changed material identity, quantity, contamination or shortcut lineage prematurely.");
                }
                steps++;
            }
            void Fact(ProductionChange fact, ProductionEvent kind, long at)
            {
                Require(fact.Kind == kind && fact.ShiftMilliseconds == at && fact.CycleId == cycle && fact.RecipeId == Id(967) &&
                    fact.Input.BatchId == Id(963) && fact.Input.CauseId == Id(965) && fact.BypassedInspection &&
                    (kind == ProductionEvent.Completed ? fact.Output?.Units == 8 && fact.WasteUnits == 2 : fact.Output == null && fact.WasteUnits == 0),
                    "Repair process fact lost its independently scheduled occurrence or original cycle attribution.");
            }
            void Advance(long delta)
            {
                host += delta; long target = paused ? shift : Math.Min(limit, shift + delta);
                ProductionEvent? expectedEvent = null; long eventAt = 0;
                if (mode == ProductionMode.Repairing)
                {
                    long credited = Math.Min(target - shift, clearing - repairWork);
                    if (credited > 0) revision++;
                    repairWork += credited;
                    if (repairWork == clearing)
                    {
                        expectedEvent = ProductionEvent.RepairCompleted; eventAt = shift + credited; armed = false;
                        if (!omitRepairCompletion) mode = ProductionMode.PowerPaused;
                    }
                }
                else if (mode == ProductionMode.Processing)
                {
                    long boundary = armed ? jam : processing;
                    long credited = Math.Min(target - shift, boundary - work);
                    if (credited > 0) revision++;
                    work += credited;
                    if (work == boundary)
                    {
                        eventAt = shift + credited;
                        if (armed) { mode = ProductionMode.Jammed; expectedEvent = ProductionEvent.Jammed; }
                        else { mode = ProductionMode.OutputReady; expectedEvent = ProductionEvent.Completed; completed++; pending = false; }
                    }
                }
                shift = target;
                if (shift == limit) { ended = true; if (pending) { pending = false; cancelled++; } }
                var result = world.AdvanceTo(host);
                Require(result.ProductionChanges.Count == (expectedEvent.HasValue ? 1 : 0), "Repair process publication count differs from independent schedule.");
                if (expectedEvent.HasValue) Fact(result.ProductionChanges.Single(), expectedEvent.Value, eventAt);
                Check();
            }
            void Act(ProductionAction action, bool requestedPower = false)
            {
                if (paused)
                {
                    var denied = port.OperateMachine(Id(966), action, powered: requestedPower);
                    Require(denied.Status == InteractionStatus.ActorUnavailable && denied.IsTerminal && !denied.HasNewCommit,
                        "Paused repair command escaped admission or wedged its receipt."); Check(); return;
                }
                ProductionStatus expected; ProductionEvent? fact = null;
                switch (action)
                {
                    case ProductionAction.SetPower:
                        expected = requestedPower && mode == ProductionMode.Repairing ? ProductionStatus.RepairInProgress :
                            requestedPower == power ? ProductionStatus.NoChange : ProductionStatus.Applied;
                        if (expected == ProductionStatus.Applied)
                        { power = requestedPower; if (!power && mode == ProductionMode.Processing) mode = ProductionMode.PowerPaused; }
                        break;
                    case ProductionAction.Repair:
                        expected = power ? ProductionStatus.PowerMustBeOff : mode == ProductionMode.Repairing ? ProductionStatus.NoChange :
                            mode == ProductionMode.Jammed ? ProductionStatus.Applied : ProductionStatus.InvalidState;
                        if (expected == ProductionStatus.Applied)
                        { mode = ProductionMode.Repairing; repairDuration = clearing; repairWork = 0; fact = ProductionEvent.RepairStarted; }
                        break;
                    case ProductionAction.Resume:
                        expected = mode == ProductionMode.Repairing ? ProductionStatus.RepairInProgress : !power ? ProductionStatus.NoPower :
                            mode == ProductionMode.PowerPaused ? ProductionStatus.Applied : ProductionStatus.InvalidState;
                        if (expected == ProductionStatus.Applied) mode = ProductionMode.Processing;
                        break;
                    case ProductionAction.CancelCycle:
                        expected = power ? ProductionStatus.PowerMustBeOff : pending ? ProductionStatus.Applied : ProductionStatus.InvalidState;
                        if (expected == ProductionStatus.Applied)
                        { mode = ProductionMode.Idle; pending = false; cancelled++; work = repairWork = repairDuration = 0; fact = ProductionEvent.Cancelled; }
                        break;
                    default: throw new InvalidOperationException("Unmodelled repair action.");
                }
                if (expected == ProductionStatus.Applied) revision++;
                var result = port.OperateMachine(Id(966), action, powered: requestedPower);
                Require(result.Production?.Status == expected && result.HasNewCommit == (expected == ProductionStatus.Applied),
                    "Repair admission differs from independent isolation/progress ledger.");
                Require((result.Production!.Change != null) == fact.HasValue, "Repair command invented or omitted a process fact.");
                if (fact.HasValue) Fact(result.Production.Change!, fact.Value, shift);
                Check();
            }
            void TogglePause()
            {
                var result = paused ? world.Resume(world.Epoch) : world.Pause(world.Epoch);
                Require(result == WorldControlStatus.Applied, "Repair model pause control failed."); paused = !paused; Check();
            }
            Check(); Advance(jam); Act(ProductionAction.SetPower); Act(ProductionAction.Repair);
            Advance(clearing / 2); Act(ProductionAction.SetPower, true); Act(ProductionAction.Repair);
            TogglePause(); Advance(random.Next(1, 5001)); Act(ProductionAction.Resume); TogglePause();
            Advance(clearing - clearing / 2);
            Act(ProductionAction.SetPower, true); Act(ProductionAction.Resume);
            for (int i = 0; i < 48 && !ended; i++)
            {
                int op = random.Next(9);
                if (op < 3) Advance(random.Next(1, 501));
                else if (op == 3) Act(ProductionAction.SetPower, random.Next(2) == 0);
                else if (op == 4) Act(ProductionAction.Repair);
                else if (op == 5) Act(ProductionAction.Resume);
                else if (op == 6) Act(ProductionAction.CancelCycle);
                else if (op == 7) TogglePause();
                else if (port.CanReplayLast)
                { var reply = port.ReplayLast(); Require(reply.IsReplay && !reply.HasNewCommit, "Repair retry committed another mutation."); Check(); }
            }
            if (!ended) { if (paused) TogglePause(); Advance(limit + 1); }
            var terminal = world.Debrief; world.Stop(); world.Stop();
            Require(ReferenceEquals(terminal, world.Debrief) && world.Production.MachineCount == 0 && world.View.RegisteredObjectCount == 0 &&
                world.View.ActiveClaimCount == 0 && terminal!.Production.CompletedCycles == completed && terminal.Production.CancelledCycles == cancelled,
                "Repair terminal cleanup retained live ownership or rewrote frozen outcomes.");
            Check(); return steps;
        }
    }
}
