using System;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Input-driven conditioning ledger; only opaque batch/cycle identities bind from accepted owner output.</summary>
    internal static class WashingSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }
        internal static int Exercise(Random random, bool omitCleaning)
        {
            int target = random.Next(0, 1000), dirty = random.Next(target + 1, 1001), moisture = random.Next(0, 1001), units = random.Next(1, 1001);
            long duration = random.Next(2, 2001), cost = random.Next(1, 6), limit = duration * 4 + 5000;
            bool inherited = random.Next(2) == 0, cancelFirst = random.Next(2) == 0;
            MaterialKind kind = inherited ? MaterialKind.CrushedOre : MaterialKind.Ore;
            var world = new WorldSession(new WorldSessionConfiguration(42, limit, true, receiptCapacity: random.Next(1, 9)), new Access(), traceCapacity: random.Next(1, 12));
            world.RegisterConnection(Id(970), Id(971));
            world.Production.RegisterBatch(Id(972), Id(973), Id(974), Id(975), MaterialKind.Ore, units, moisture, dirty);
            world.Production.RegisterMachine(Id(976), MachineRecipe.Washing(Id(977), kind, duration, 1000, target, cost));
            if (inherited) world.Production.RegisterMachine(Id(978), new MachineRecipe(Id(979), MaterialKind.Ore, MaterialKind.CrushedOre,
                2, 2, 1, 1000, moistureTolerance: 1000, outputMoisture: moisture));
            world.Reactor.Register(Id(980), new ReactorDefinition(Id(981))); var port = new LocalCommandPort(world, Id(970)); world.Start();
            long host = 0, shift = 0, work = 0, spent = 0; int steps = 0, cancelled = 0, priorCompleted = 0;
            bool pending = false, complete = false, powered = true, doingWork = false, paused = false, reloaded = false;
            Guid inputId = Id(973), cycle = Guid.Empty, outputId = Guid.Empty;
            Guid inputParent = inherited ? Id(973) : Guid.Empty;
            MaterialFlags flags = inherited ? MaterialFlags.BypassedInspection : MaterialFlags.None;
            InteractionReply Act(ProductionAction action, bool bypass = false, bool power = false) =>
                port.OperateMachine(Id(976), action, action == ProductionAction.Insert ? Id(972) : Guid.Empty, bypass, power);
            void Accepted(InteractionReply reply) => Require(reply.HasNewCommit, "Authored washing action was rejected.");
            if (inherited)
            {
                Accepted(port.Grab(Id(972))); Accepted(port.OperateMachine(Id(978), ProductionAction.Insert, Id(972)));
                Accepted(port.OperateMachine(Id(978), ProductionAction.Start, bypass: true)); world.AdvanceTo(2); host = shift = 2;
                var prefixed = world.Production.GetBatch(Id(972))!; inputId = prefixed.BatchId; priorCompleted = 1;
                Require(inputId != Id(973) && prefixed.ParentBatchId == Id(973) && prefixed.Kind == MaterialKind.CrushedOre &&
                    prefixed.Contamination == dirty && prefixed.Moisture == moisture && prefixed.Units == units &&
                    prefixed.Flags == flags && prefixed.OriginId == Id(974) && prefixed.CauseId == Id(975),
                    "Washing prefix lost its authored shortcut lineage or original properties.");
                Accepted(port.OperateMachine(Id(978), ProductionAction.Eject)); steps++;
            }
            Accepted(port.Grab(Id(972))); Accepted(Act(ProductionAction.Insert));
            bool Original(MaterialView? batch) => batch != null && batch.BatchId == inputId && batch.ParentBatchId == inputParent &&
                batch.ContainerId == Id(972) && batch.OriginId == Id(974) && batch.CauseId == Id(975) && batch.Kind == kind &&
                batch.Units == units && batch.Moisture == moisture && batch.Contamination == dirty && batch.Flags == flags && batch.Revision == (inherited ? 1 : 0);
            bool Conditioned(MaterialView? batch) => batch != null && batch.ContainerId == Id(972) && batch.ParentBatchId == inputId &&
                batch.OriginId == Id(974) && batch.CauseId == Id(975) && batch.Kind == kind && batch.Units == units && batch.Moisture == 1000 &&
                batch.Contamination == target && batch.Flags == flags && batch.Revision == (inherited ? 2 : 1);
            void Check()
            {
                var summary = world.Production.Summary; var power = world.Reactor.PowerSummary!;
                Require(summary.IssuedUnits == units && summary.ActiveUnits == units && summary.WasteUnits == 0 &&
                    summary.PendingCycles == (pending ? 1 : 0) && summary.CancelledCycles == cancelled &&
                    summary.CompletedCycles == priorCompleted + (complete ? 1 : 0), "Washing quantity/history differs from independent cycle ledger.");
                Require(summary.ReserveSpent == spent && power.Spent == spent && power.Available == 10 - spent &&
                    power.Generated == 0 && power.Delivered == 0 && power.Spilled == 0, "Washing reserve differs from independent paid-start ledger.");
                Require(world.View.ElapsedMilliseconds == shift, "Washing shift clock differs from independent pause ledger.");
                if (world.View.Phase != WorldPhase.Stopped)
                {
                    var batch = world.Production.GetBatch(Id(972))!; var machine = world.Production.GetMachine(Id(976))!;
                    Require(batch.Contamination == (complete && !omitCleaning ? target : dirty),
                        "Washing contamination differs from independently scheduled conditioning.");
                    Require(batch.Moisture == (complete ? 1000 : moisture) && batch.Units == units && batch.Kind == kind &&
                        batch.Flags == flags && batch.OriginId == Id(974) && batch.CauseId == Id(975) &&
                        (complete ? batch.ParentBatchId == inputId && batch.BatchId != inputId : Original(batch)),
                        "Washing changed independent moisture, quantity, kind or original lineage.");
                    if (complete)
                    {
                        if (outputId == Guid.Empty) outputId = batch.BatchId;
                        Require(batch.BatchId == outputId, "Washing replay replaced its already committed child identity.");
                    }
                    var mode = reloaded ? ProductionMode.Idle : complete ? ProductionMode.OutputReady : pending ? doingWork ? ProductionMode.Processing : ProductionMode.PowerPaused : ProductionMode.Idle;
                    Require(machine.Mode == mode && machine.Powered == powered && machine.WorkMilliseconds == work && !machine.BypassedInspection &&
                        world.GetObject(Id(972))!.SlotId == Id(976), "Washing mode/work/power or current custody differs from independent ledger.");
                }
                steps++;
            }
            void Start()
            {
                var started = Act(ProductionAction.Start); Accepted(started); pending = doingWork = true; work = 0; spent += cost;
                cycle = started.Production!.Machine!.CycleId; var fact = started.Production.Change;
                Require(cycle != Guid.Empty && fact?.Kind == ProductionEvent.Started && fact.ReserveSpent == cost && fact.CycleId == cycle &&
                    fact.ShiftMilliseconds == shift && Original(fact.Input) && fact.Output == null && !fact.BypassedInspection,
                    "Washing paid-start fact lost its authored cost or original input attribution."); Check();
                var retry = port.ReplayLast();
                Require(retry.IsReplay && !retry.HasNewCommit && retry.Production?.Change?.CycleId == cycle,
                    "Washing start replay was not recognized."); Check();
            }
            void Advance(long delta)
            {
                long before = shift, beforeWork = work; host += delta;
                if (!paused) shift = Math.Min(limit, shift + delta);
                bool finishes = pending && doingWork && shift - before >= duration - beforeWork;
                if (pending && doingWork) work += Math.Min(shift - before, duration - work);
                if (finishes) { pending = doingWork = false; complete = true; }
                var result = world.AdvanceTo(host); var facts = result.ProductionChanges.Where(c => c.Kind == ProductionEvent.Completed).ToArray();
                Require(result.ProductionChanges.Count == (finishes ? 1 : 0) && facts.Length == (finishes ? 1 : 0),
                    "Washing completion count differs from independent work boundary.");
                if (finishes)
                {
                    var fact = facts[0];
                    Require(fact.ShiftMilliseconds == before + duration - beforeWork && fact.CycleId == cycle && fact.RecipeId == Id(977) &&
                        Original(fact.Input) && Conditioned(fact.Output) && fact.Output!.BatchId == world.Production.GetBatch(Id(972))!.BatchId &&
                        fact.WasteUnits == 0 && !fact.BypassedInspection,
                        "Washing completion fact lost its independently timed properties or original input.");
                }
                Check();
            }
            void Power(bool value)
            {
                Accepted(Act(ProductionAction.SetPower, power: value)); powered = value;
                if (!value && pending) doingWork = false; Check();
            }
            Require(Act(ProductionAction.Start, bypass: true).Production?.Status == ProductionStatus.BypassUnavailable,
                "Washing accepted an inspection bypass."); Check(); Start();
            Advance(random.Next(1, (int)duration));
            world.Pause(world.Epoch); paused = true; Advance(random.Next(1, 2001)); world.Resume(world.Epoch); paused = false; Check();
            Power(false); Advance(random.Next(1, 501)); Power(true); Advance(random.Next(1, 501));
            Accepted(Act(ProductionAction.Resume)); doingWork = true; Check();
            if (cancelFirst)
            {
                Power(false); Accepted(Act(ProductionAction.CancelCycle)); pending = doingWork = false; work = 0; cancelled++; Check();
                var cancelledReceipt = world.Production.GetConversion(cycle)!;
                Require(cancelledReceipt.Cancelled && Original(cancelledReceipt.Input) && cancelledReceipt.Output == null && !cancelledReceipt.BypassedInspection,
                    "Cancelled washing receipt did not retain the exact dirty input and safe-cycle decision.");
                Power(true); Start();
            }
            long remaining = duration - work;
            if (remaining > 1) Advance(remaining - 1);
            Advance(1); Require(complete, "Authored washing cycle did not complete.");
            Require(port.ReplayLast().IsReplay, "Historical washing receipt was not recognized."); Check(); Advance(random.Next(1, 2001));
            var retained = world.Production.GetConversion(cycle)!;
            Require(!retained.Cancelled && retained.Output?.BatchId == outputId && Conditioned(retained.Output) &&
                Original(retained.Input) && retained.BypassedInspection == false,
                "Washing retained receipt lost original input, output or current-cycle decision.");
            Accepted(Act(ProductionAction.Eject)); Accepted(port.Grab(Id(972))); Accepted(Act(ProductionAction.Insert));
            Require(Act(ProductionAction.Start).Production?.Status == ProductionStatus.AlreadyConditioned,
                "Clean washed output could consume another paid cycle.");
            // Eject/reinsert clears process work, retaining the finished material and resource history.
            reloaded = true; work = 0; Check();
            Require(world.Production.Summary.ReserveSpent == spent && world.Reactor.PowerSummary!.Spent == spent &&
                world.Production.Summary.PendingCycles == 0, "Rejected clean washing spent resources or reserved another child."); steps++;
            world.Stop(); return steps;
        }
    }
}
