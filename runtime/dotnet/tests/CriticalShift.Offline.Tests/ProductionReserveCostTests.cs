using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ProductionReserveCostTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port, Other;
            internal readonly TestAccess Access = new TestAccess();
            internal Setup(long cost = 3, long initial = 10, bool reactor = true, int moisture = 100,
                int cycles = 1024, bool drying = false, long shift = 10000, int trace = 128)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), Access, traceCapacity: trace, maxProductionCycles: cycles);
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11)); World.RegisterWorkerBody(Id(11), Id(32));
                World.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Ore, 10, moisture, 35);
                World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Ore, 10, moisture, 35);
                World.Production.RegisterMachine(Id(40), drying ? MachineRecipe.Drying(Id(50), MaterialKind.Ore, 1000, 100, reserveCost: cost) :
                    new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100, repairDurationMilliseconds: 1000, reserveCost: cost));
                World.Production.RegisterMachine(Id(41), new MachineRecipe(Id(51), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100, reserveCost: cost));
                if (reactor)
                {
                    World.Reactor.Register(Id(90), new ReactorDefinition(Id(91), initialReserve: initial));
                    World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(500, 12, 2));
                }
                World.Medical.Register(Id(95), new MedicalDefinition(1000, 4, 3));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21)); World.Start();
            }
            internal MachineView State => World.Production.GetMachine(Id(40))!;
            internal MaterialView Input => World.Production.GetBatch(Id(30))!;
            internal InteractionReply Act(ProductionAction action, bool bypass = false, bool power = false) => Port.OperateMachine(Id(40), action, bypass: bypass, powered: power);
            internal void Load()
            { Applied(Port.Grab(Id(30))); Applied(Port.OperateMachine(Id(40), ProductionAction.Insert, Id(30))); }
            internal void Patient()
            {
                Assert.That(World.ApplyWorkerImpact(World.Epoch, Id(11), 1, WorkerImpact.Incapacitating, 0, Id(96), Id(97)).Changed, Is.True);
                Applied(Port.Grab(Id(32))); Applied(Port.OperateMedical(Id(95), MedicalAction.Insert, Id(32)));
            }
            internal void Balanced(long spent, long production)
            {
                var power = World.Reactor.PowerSummary!;
                Assert.That(power.Spent, Is.EqualTo(spent)); Assert.That(World.Production.Summary.ReserveSpent, Is.EqualTo(production));
                Assert.That(power.Initial + power.Generated, Is.EqualTo(power.Available + power.Spent + power.Delivered + power.Spilled));
            }
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True,
            () => reply.Status + " / " + reply.Production?.Status + " / " + reply.Medical?.Status + " / " + reply.Reactor?.Status);

        [Test] public void FreeLegacyProductionRequiresNoReactorOrReserveAndRetainsItsOriginalEventBehavior()
        {
            var f = new Setup(cost: 0, reactor: false); f.Load(); var start = f.Act(ProductionAction.Start); Applied(start);
            Assert.That(start.Production!.Change, Is.Null); Assert.That(f.World.Production.Summary.ReserveSpent, Is.Zero);
            f.World.AdvanceTo(1000); Assert.That(f.Input.Kind, Is.EqualTo(MaterialKind.CrushedOre)); Assert.That(f.World.Reactor.PowerSummary, Is.Null);
        }

        [TestCase(false, 10)] [TestCase(true, 0)] [TestCase(true, 2)]
        public void PaidStartWithoutSufficientSharedReservePreservesEveryReservationAndOwner(bool reactor, long initial)
        {
            var f = new Setup(reactor: reactor, initial: initial); f.Load(); var input = f.Input; long revision = f.State.Revision;
            var core = f.World.Reactor.View; var denied = f.Act(ProductionAction.Start);
            Assert.That(denied.Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve)); Assert.That(denied.HasNewCommit, Is.False);
            Assert.That(f.State.Revision, Is.EqualTo(revision)); Assert.That(f.State.Mode, Is.EqualTo(ProductionMode.Idle)); Assert.That(f.State.CycleId, Is.EqualTo(Guid.Empty));
            Assert.That(f.Input.BatchId, Is.EqualTo(input.BatchId)); Assert.That(f.Input.Revision, Is.EqualTo(input.Revision));
            Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.EqualTo(Id(40))); Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero);
            Assert.That(f.World.Production.Summary.ReserveSpent, Is.Zero); Assert.That(f.World.Reactor.View?.Revision, Is.EqualTo(core?.Revision));
            if (reactor) { Assert.That(f.World.Reactor.PowerSummary!.Available, Is.EqualTo(initial)); f.Balanced(0, 0); }
        }

        [Test] public void PaidStartPublishesOneOriginalCycleDebitAndHistoricalRetryCannotSpendAgain()
        {
            var f = new Setup(); f.Load(); var input = f.Input; var first = f.Act(ProductionAction.Start); Applied(first);
            var fact = first.Production!.Change!; Assert.That(fact.Kind, Is.EqualTo(ProductionEvent.Started)); Assert.That(fact.ReserveSpent, Is.EqualTo(3));
            Assert.That(fact.Input.BatchId, Is.EqualTo(input.BatchId)); Assert.That(fact.Input.CauseId, Is.EqualTo(Id(80)));
            Assert.That(fact.CycleId, Is.EqualTo(f.State.CycleId)); Assert.That(fact.RecipeId, Is.EqualTo(Id(50))); Assert.That(fact.ShiftMilliseconds, Is.Zero);
            Assert.That(fact.Output, Is.Null); Assert.That(fact.WasteUnits, Is.Zero); f.Balanced(3, 3);
            f.World.AdvanceTo(1000); var retry = f.Port.ReplayLast(); Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(retry.Production!.Change!.CycleId, Is.EqualTo(fact.CycleId)); Assert.That(retry.Production.Change.ReserveSpent, Is.EqualTo(3));
            Assert.That(f.World.Trace.Records.Count(r => r.ProductionEvent == ProductionEvent.Started), Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Last().Changed, Is.False); f.Balanced(3, 3);
        }

        [TestCase(true)] [TestCase(false)]
        public void DifferentMachinesCompeteForOneLimitedReserveWithoutChargingTheLoser(bool firstMachine)
        {
            var f = new Setup(initial: 5); f.Load(); Applied(f.Other.Grab(Id(31))); Applied(f.Other.OperateMachine(Id(41), ProductionAction.Insert, Id(31)));
            var winner = firstMachine ? f.Act(ProductionAction.Start) : f.Other.OperateMachine(Id(41), ProductionAction.Start); Applied(winner);
            var loser = firstMachine ? f.Other.OperateMachine(Id(41), ProductionAction.Start) : f.Act(ProductionAction.Start);
            Assert.That(loser.Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.EqualTo(1)); f.Balanced(3, 3); Assert.That(f.World.Reactor.PowerSummary!.Available, Is.EqualTo(2));
        }

        [Test] public void ProductionDebitInvalidatesAStaleReactorControlWithoutChargingBoth()
        {
            var f = new Setup(); f.Load(); long revision = f.World.Reactor.View!.Revision; f.Act(ProductionAction.Start);
            var result = f.World.ExecuteInteraction(Id(21), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, revision)));
            Assert.That(result.Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict)); f.Balanced(3, 3);
        }

        [TestCase(true)] [TestCase(false)]
        public void MedicalAndProductionPayFromTheSameReserveInEitherOrder(bool productionFirst)
        {
            var f = new Setup(initial: 6); f.Load(); f.Patient();
            var first = productionFirst ? f.Act(ProductionAction.Start) : f.Port.OperateMedical(Id(95), MedicalAction.Start); Applied(first);
            var denied = productionFirst ? f.Port.OperateMedical(Id(95), MedicalAction.Start) : f.Act(ProductionAction.Start);
            Assert.That(denied.HasNewCommit, Is.False);
            if (productionFirst) Assert.That(denied.Medical!.Status, Is.EqualTo(MedicalStatus.InsufficientReserve));
            else Assert.That(denied.Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve));
            f.Balanced(productionFirst ? 3 : 4, productionFirst ? 3 : 0);
            Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(productionFirst ? 0 : 1));
        }

        [Test] public void RepairPauseResumeAndCompletionCannotChargeAnotherProductionStartup()
        {
            var f = new Setup(moisture: 900); f.Load(); Applied(f.Act(ProductionAction.Start, bypass: true)); f.World.AdvanceTo(200);
            Applied(f.Act(ProductionAction.SetPower)); Applied(f.Act(ProductionAction.Repair)); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(5000);
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(6000); Applied(f.Act(ProductionAction.SetPower, power: true)); Applied(f.Act(ProductionAction.Resume));
            f.World.AdvanceTo(6300); Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); f.Balanced(3, 3);
            Assert.That(f.World.Trace.Records.Where(r => r.ProductionEvent != ProductionEvent.Started && r.ProductionEvent.HasValue).All(r => r.ProductionReserveSpent == 0), Is.True);
        }

        [Test] public void CancellingKeepsThePaidCostAndAnotherNewCyclePaysAgain()
        {
            var f = new Setup(); f.Load(); var input = f.Input; Applied(f.Act(ProductionAction.Start)); var first = f.State.CycleId;
            Applied(f.Act(ProductionAction.SetPower)); Applied(f.Act(ProductionAction.CancelCycle)); f.Balanced(3, 3);
            Assert.That(f.Input.BatchId, Is.EqualTo(input.BatchId)); Applied(f.Act(ProductionAction.SetPower, power: true)); Applied(f.Act(ProductionAction.Start));
            Assert.That(f.State.CycleId, Is.Not.EqualTo(first)); f.Balanced(6, 6);
        }

        [TestCase(999, 0)] [TestCase(1000, 1)] [TestCase(1001, 1)]
        public void PaidCostSurvivesTerminalCutoffWhetherConversionFinishes(long deadline, int completed)
        {
            var f = new Setup(shift: deadline); f.Load(); f.Act(ProductionAction.Start); f.World.AdvanceTo(2000);
            Assert.That(f.World.Debrief!.Production.ReserveSpent, Is.EqualTo(3)); Assert.That(f.World.Debrief.Production.CompletedCycles, Is.EqualTo(completed));
            Assert.That(f.World.Debrief.Production.CancelledCycles, Is.EqualTo(1 - completed)); f.Balanced(3, 3);
            var frozen = f.World.Debrief; f.World.Stop(); Assert.That(f.World.Debrief, Is.SameAs(frozen));
            var next = f.World.Restart(new TestAccess()); Assert.That(next.Production.Summary.ReserveSpent, Is.Zero); Assert.That(next.Reactor.PowerSummary, Is.Null);
        }

        [Test] public void WetDryingAndExhaustedHistoryRejectBeforeAnyDebit()
        {
            var wet = new Setup(moisture: 900); wet.Load(); Assert.That(wet.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.WetInput)); wet.Balanced(0, 0);
            var dry = new Setup(drying: true, moisture: 100); dry.Load(); Assert.That(dry.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.AlreadyConditioned)); dry.Balanced(0, 0);
            var capped = new Setup(cycles: 1); capped.Load(); Applied(capped.Act(ProductionAction.Start)); Applied(capped.Act(ProductionAction.SetPower)); Applied(capped.Act(ProductionAction.CancelCycle));
            Applied(capped.Act(ProductionAction.SetPower, power: true)); Assert.That(capped.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.HistoryCapacityReached)); capped.Balanced(3, 3);
        }

        [Test] public void BackupEnablesPaidDryingWithoutChangingItsQuantityOrContamination()
        {
            var f = new Setup(initial: 0, moisture: 850, drying: true); f.Load(); Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve));
            Applied(f.Port.OperateReactor(Id(90), ReactorAction.StartBackup)); f.World.AdvanceTo(500); Applied(f.Act(ProductionAction.Start)); f.World.AdvanceTo(1500);
            Assert.That(f.Input.Units, Is.EqualTo(10)); Assert.That(f.Input.Kind, Is.EqualTo(MaterialKind.Ore)); Assert.That(f.Input.Moisture, Is.EqualTo(100));
            Assert.That(f.Input.Contamination, Is.EqualTo(35)); f.Balanced(3, 3); Assert.That(f.World.Reactor.EmergencyPowerSummary!.UsedCharges, Is.EqualTo(1));
        }

        [Test] public void PaidStartFactsAndCategorySubtotalSurviveTraceEvictionWithoutRepeatingCharges()
        {
            var f = new Setup(trace: 8); f.Load(); var feed = new SandboxTraceFeed(f.Port); var result = f.Act(ProductionAction.Start); feed.Refresh();
            Assert.That(feed.Entries.Count(e => e.Description.Contains("spent 3 reserve")), Is.EqualTo(1));
            Assert.That(SandboxMachineReadout.Result(result.Production!, ProductionAction.Start), Does.Contain("spent 3 reserve"));
            for (int i = 1; i <= 24; i++) f.World.AdvanceTo(i);
            Assert.That(f.World.Trace.Records.Any(r => r.ProductionEvent == ProductionEvent.Started), Is.False); f.World.Stop();
            var start = f.World.Debrief!.Timeline.Single(r => r.ProductionEvent == ProductionEvent.Started);
            Assert.That(start.ProductionReserveSpent, Is.EqualTo(3)); Assert.That(start.MaterialCauseId, Is.EqualTo(Id(80))); Assert.That(start.BatchId, Is.EqualTo(Id(60)));
            Assert.That(start.CycleId, Is.EqualTo(result.Production!.Machine!.CycleId)); f.Balanced(3, 3);
        }

        [TestCase("_reserveSpent")] [TestCase("_revision")]
        public void ArithmeticFailureBeforePaidStartFaultsWithoutReservingOrSpending(string field)
        {
            var f = new Setup(); f.Load(); object owner = field == "_reserveSpent" ? (object)f.World.Production : f.World.Reactor;
            owner.GetType().GetField(field, BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(owner, long.MaxValue);
            Assert.Throws<OverflowException>(() => f.Act(ProductionAction.Start)); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.World.Reactor.PowerSummary.Available, Is.EqualTo(10));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero); Assert.That(f.World.Production.Summary.CancelledCycles, Is.Zero);
            Assert.That(f.World.Production.MachineCount, Is.Zero); Assert.That(f.World.View.RegisteredObjectCount, Is.Zero);
            Assert.That(f.World.Debrief!.Timeline.Any(r => r.ProductionEvent == ProductionEvent.Started), Is.False);
        }

        [TestCase(-1)] [TestCase(1000000001)]
        public void AuthoredProductionReserveCostRejectsOutOfBounds(long cost) => Assert.Throws<ArgumentOutOfRangeException>(() =>
            new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100, reserveCost: cost));

        [Test] public void HistoricalInsufficientReserveCannotBecomeAPaidStartAfterBackupCompletes()
        {
            var f = new Setup(initial: 0); f.Load(); long revision = f.State.Revision;
            Assert.That(f.Act(ProductionAction.Start).Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve));
            long sequence = f.Port.LastTerminalSequence; Applied(f.Port.OperateReactor(Id(90), ReactorAction.StartBackup)); f.World.AdvanceTo(500);
            var retry = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Production, Id(40),
                production: new ProductionRequest(ProductionAction.Start, revision)));
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.Production!.Status, Is.EqualTo(ProductionStatus.InsufficientReserve)); f.Balanced(0, 0);
            Applied(f.Act(ProductionAction.Start)); f.Balanced(3, 3);
        }

        [Test] public void DeniedAccessAndStaleCompetingMachineStartCannotDrainReserve()
        {
            var f = new Setup(); f.Load(); f.Access.Decision = AccessDecision.OutOfReach;
            Assert.That(f.Act(ProductionAction.Start).Status, Is.EqualTo(InteractionStatus.OutOfReach)); f.Balanced(0, 0);
            f.Access.Decision = AccessDecision.Allowed; long previous = f.State.Revision; Applied(f.Act(ProductionAction.Start));
            var stale = f.World.ExecuteInteraction(Id(21), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Production, Id(40),
                production: new ProductionRequest(ProductionAction.Start, previous)));
            Assert.That(stale.Production!.Status, Is.EqualTo(ProductionStatus.RevisionConflict)); f.Balanced(3, 3);
        }
    }
}
