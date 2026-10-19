using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ReactorRoutingTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Access : IInteractionAccessPolicy
        { internal bool Allow = true; public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => Allow ? AccessDecision.Allowed : AccessDecision.OutOfReach; }
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal readonly Access Access = new Access();
            internal ReactorView Core => World.Reactor.View!;
            internal PowerView Power => World.Reactor.PowerSummary!;
            internal Setup(long capacity = 100, long initial = 10, long shift = 10000, bool start = true, bool contract = false, int trace = 128, long backupOutput = 12)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), Access, traceCapacity: trace);
                World.RegisterConnection(Id(20), Id(10));
                World.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Fuel, 10);
                World.Reactor.Register(Id(90), new ReactorDefinition(Id(91), capacity, initial));
                World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(100, backupOutput, 2));
                if (contract) World.Contracts.Register(new ShiftContractDefinition(Id(920), "Routed windows",
                    new GridDemandWave(Id(921), "Balanced", 100, 4), new GridDemandWave(Id(922), "Grid", 200, 5), new GridDemandWave(Id(923), "Reserve", shift, 1)));
                Port = new LocalCommandPort(World, Id(20)); if (start) World.Start();
            }
            internal InteractionReply Act(ReactorAction action) => Port.OperateReactor(Id(90), action);
            internal InteractionReply Route(ReactorOutputRouting route) => Port.OperateReactor(Id(90), ReactorAction.SetOutputRouting, outputRouting: route);
            internal void Run()
            {
                Assert.That(Port.Grab(Id(30)).HasNewCommit, Is.True);
                Assert.That(Port.OperateReactor(Id(90), ReactorAction.Insert, Id(30)).HasNewCommit, Is.True);
                Assert.That(Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true).HasNewCommit, Is.True);
                Assert.That(Act(ReactorAction.Start).HasNewCommit, Is.True);
            }
        }
        private static void Balanced(PowerView p) => Assert.That(p.Initial + p.Generated, Is.EqualTo(p.Available + p.Spent + p.Delivered + p.Spilled));

        [TestCase(ReactorOutputRouting.Balanced, 17, 40)]
        [TestCase(ReactorOutputRouting.GridPriority, 7, 50)]
        [TestCase(ReactorOutputRouting.ReservePriority, 57, 0)]
        public void CoreRoutingConservesEveryNewQuantumAndFuel(ReactorOutputRouting route, int reserve, int grid)
        {
            var f = new Setup(); f.Route(route); f.Run(); f.World.AdvanceTo(1000);
            Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Exhausted)); Assert.That(f.Core.WorkMilliseconds, Is.EqualTo(1000));
            Assert.That(f.Power.Available, Is.EqualTo(reserve)); Assert.That(f.Power.Delivered, Is.EqualTo(grid)); Assert.That(f.Power.Generated, Is.EqualTo(50));
            Assert.That(f.Power.Spent, Is.EqualTo(3)); Assert.That(f.World.Production.GetBatch(Id(30))!.Kind, Is.EqualTo(MaterialKind.SpentFuel));
            Assert.That(f.World.Production.Summary.CompletedCycles, Is.EqualTo(1)); Balanced(f.Power);
        }

        [Test] public void RoutingSwitchChangesOnlyFutureCompletedQuantaAndKeepsPartialWork()
        {
            var f = new Setup(); f.Run(); f.World.AdvanceTo(100); var old = f.Core;
            var changed = f.Route(ReactorOutputRouting.GridPriority); var frozen = changed.Reactor!.Change!.State;
            Assert.That(changed.Reactor.Change.Kind, Is.EqualTo(ReactorEvent.OutputRoutingChanged)); Assert.That(changed.Reactor.Change.GeneratedUnits, Is.Zero);
            Assert.That(f.Core.WorkMilliseconds, Is.EqualTo(100)); Assert.That(f.Power.Delivered, Is.EqualTo(4)); Assert.That(old.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced));
            f.World.AdvanceTo(199); f.Route(ReactorOutputRouting.ReservePriority); f.World.AdvanceTo(200);
            Assert.That(f.Core.WorkMilliseconds, Is.EqualTo(200)); Assert.That(f.Power.Available, Is.EqualTo(13)); Assert.That(f.Power.Delivered, Is.EqualTo(4));
            Assert.That(f.Power.Generated, Is.EqualTo(10)); Assert.That(frozen.OutputRouting, Is.EqualTo(ReactorOutputRouting.GridPriority));
            f.Route(ReactorOutputRouting.GridPriority); f.World.AdvanceTo(300);
            Assert.That(f.Power.Delivered, Is.EqualTo(9)); Assert.That(f.Power.Generated, Is.EqualTo(15)); Balanced(f.Power);
        }

        [Test] public void RoutingRetriesRetainHistoricalResultWithoutRestoringTheOldValve()
        {
            var f = new Setup(); long rev = f.Core.Revision;
            Assert.That(f.Route(ReactorOutputRouting.Balanced).Reactor!.Status, Is.EqualTo(ReactorStatus.NoChange));
            Assert.That(f.Core.Revision, Is.EqualTo(rev)); var first = f.Route(ReactorOutputRouting.GridPriority);
            long sequence = f.Port.LastTerminalSequence;
            var replay = new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.SetOutputRouting, rev, outputRouting: ReactorOutputRouting.GridPriority));
            f.Route(ReactorOutputRouting.ReservePriority); long current = f.Core.Revision;
            var retry = f.World.ExecuteInteraction(Id(20), replay);
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.Reactor!.Change!.State.OutputRouting, Is.EqualTo(ReactorOutputRouting.GridPriority));
            Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.ReservePriority)); Assert.That(f.Core.Revision, Is.EqualTo(current));
            var mismatch = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.SetOutputRouting, rev, outputRouting: ReactorOutputRouting.ReservePriority)));
            Assert.That(mismatch.Status, Is.EqualTo(InteractionStatus.PayloadMismatch)); Assert.That(f.Power.Generated, Is.Zero);
            Assert.That(first.Reactor!.Change!.CauseId, Is.Not.EqualTo(Guid.Empty));
            f.World.Stop();
            Assert.That(SandboxTraceFeed.DebriefEntries(f.World.Debrief!).Where(e => e.Reactor == ReactorEvent.OutputRoutingChanged).Select(e => e.Description),
                Is.EqualTo(new[] { "Core output routing: Grid priority", "Core output routing: Reserve priority" }));
        }

        [TestCase(ReactorOutputRouting.Balanced)] [TestCase(ReactorOutputRouting.GridPriority)] [TestCase(ReactorOutputRouting.ReservePriority)]
        public void OutputRoutingNeverExportsInitialOrBackupEnergy(ReactorOutputRouting route)
        {
            var f = new Setup(initial: 0); f.Route(route); f.Act(ReactorAction.StartBackup); f.World.AdvanceTo(100);
            Assert.That(f.Power.Available, Is.EqualTo(12)); Assert.That(f.Power.Delivered, Is.Zero); Assert.That(f.Power.Generated, Is.EqualTo(12));
            f.Route(ReactorOutputRouting.GridPriority); Assert.That(f.Power.Available, Is.EqualTo(12)); Assert.That(f.Power.Delivered, Is.Zero);
            f.World.AdvanceTo(1000); Assert.That(f.Power.Delivered, Is.Zero); Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Empty)); Balanced(f.Power);
        }

        [Test] public void ReservePrioritySpillsAtCapacityWithoutCreditingTheGrid()
        {
            var f = new Setup(capacity: 12); f.Route(ReactorOutputRouting.ReservePriority); f.Run(); f.World.AdvanceTo(1000);
            Assert.That(f.Power.Available, Is.EqualTo(12)); Assert.That(f.Power.Spilled, Is.EqualTo(45)); Assert.That(f.Power.Delivered, Is.Zero); Balanced(f.Power);
        }

        [Test] public void RoutingAtDemandBoundariesKeepsTheSettledWindowAndFinalCutoff()
        {
            var f = new Setup(shift: 300, contract: true); f.Run(); f.World.AdvanceTo(100); f.Route(ReactorOutputRouting.GridPriority);
            f.World.AdvanceTo(200); f.Route(ReactorOutputRouting.ReservePriority); f.World.AdvanceTo(300);
            var demand = f.World.Debrief!.Contract!;
            Assert.That(demand.Waves.Select(w => w.DeliveredEnergyUnits), Is.EqualTo(new long[] { 4, 5, 0 }));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.Power.Generated, Is.EqualTo(15));
            Assert.That(f.Power.Delivered, Is.EqualTo(9)); Assert.That(f.Route(ReactorOutputRouting.GridPriority).HasNewCommit, Is.False); Balanced(f.Power);
        }

        [Test] public void PauseFreezesRoutingAndGenerationAndRestartDefaultsToBalanced()
        {
            var f = new Setup(); f.Run(); f.World.AdvanceTo(100); f.World.Pause(f.World.Epoch); long revision = f.Core.Revision;
            Assert.That(f.Route(ReactorOutputRouting.GridPriority).Status, Is.EqualTo(InteractionStatus.ActorUnavailable)); f.World.AdvanceTo(1000);
            Assert.That(f.Core.Revision, Is.EqualTo(revision)); Assert.That(f.Power.Generated, Is.EqualTo(5)); f.World.Resume(f.World.Epoch);
            f.Route(ReactorOutputRouting.ReservePriority); f.World.AdvanceTo(1100); Assert.That(f.Power.Delivered, Is.EqualTo(4));
            f.World.Stop(); var next = f.World.Restart(new TestAccess()); next.RegisterConnection(Id(20), Id(10));
            next.Reactor.Register(Id(90), new ReactorDefinition(Id(91))); next.Start();
            Assert.That(next.Reactor.View!.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced)); Assert.That(next.Reactor.PowerSummary!.Generated, Is.Zero);
        }

        [Test] public void RoutingUsesExistingSpatialWorkerAndRevisionAdmission()
        {
            var f = new Setup(); f.Access.Allow = false;
            Assert.That(f.Route(ReactorOutputRouting.GridPriority).Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced)); f.Access.Allow = true;
            var stale = new ReactorRequest(ReactorAction.SetOutputRouting, f.Core.Revision, outputRouting: ReactorOutputRouting.GridPriority);
            f.Route(ReactorOutputRouting.ReservePriority);
            Assert.That(f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, f.Port.LastTerminalSequence + 1,
                InteractionKind.Reactor, Id(90), reactor: stale)).Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict));
            Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.ReservePriority)); Assert.That(f.Power.Available, Is.EqualTo(10));
            var down = new Setup(); down.World.ApplyWorkerImpact(down.World.Epoch, Id(10), 1, WorkerImpact.Knockdown, 0, Id(701), Id(702));
            Assert.That(down.Route(ReactorOutputRouting.GridPriority).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(down.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced)); Assert.That(down.Power.Generated, Is.Zero);
        }

        [TestCase(99)] [TestCase(100)] [TestCase(101)]
        public void RouteSwitchAtEitherSideOfQuantumKeepsCompletedEndpointOwnership(long at)
        {
            var f = new Setup(); f.Run(); f.World.AdvanceTo(at); long oldQuanta = at / 100;
            f.Route(ReactorOutputRouting.GridPriority); f.World.AdvanceTo(200);
            Assert.That(f.Power.Delivered, Is.EqualTo(oldQuanta * 4 + (2 - oldQuanta) * 5));
            Assert.That(f.Power.Available, Is.EqualTo(7 + oldQuanta)); Assert.That(f.Power.Generated, Is.EqualTo(10)); Balanced(f.Power);
        }

        [Test] public void CoreCreditPrecedesSimultaneousBackupAndExcessReserveStillSpills()
        {
            var f = new Setup(capacity: 10, initial: 7, backupOutput: 4); f.Run(); f.Route(ReactorOutputRouting.ReservePriority);
            Assert.That(f.Act(ReactorAction.StartBackup).HasNewCommit, Is.True); f.World.AdvanceTo(100);
            Assert.That(f.Power.Available, Is.EqualTo(10)); Assert.That(f.Power.Spilled, Is.EqualTo(3)); Assert.That(f.Power.Delivered, Is.Zero);
            Assert.That(f.World.Reactor.EmergencyPowerSummary!.StoredUnits, Is.EqualTo(1));
            Assert.That(f.World.Reactor.EmergencyPowerSummary.SpilledUnits, Is.EqualTo(3)); Balanced(f.Power);
        }

        [Test] public void RoutingSurvivesTripResetRestartExhaustionAndFreshFuel()
        {
            var f = new Setup(start: false); f.World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Fuel, 10); f.World.Start();
            f.Route(ReactorOutputRouting.ReservePriority); f.Run(); f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: false);
            f.World.AdvanceTo(800); Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Tripped));
            f.Port.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true); f.World.AdvanceTo(1500); f.Act(ReactorAction.ResetTrip); f.Act(ReactorAction.Start);
            f.World.AdvanceTo(1700); Assert.That(f.Core.Mode, Is.EqualTo(ReactorMode.Exhausted));
            Assert.That(f.Act(ReactorAction.Eject).HasNewCommit, Is.True); Assert.That(f.Port.Grab(Id(31)).HasNewCommit, Is.True);
            Assert.That(f.Port.OperateReactor(Id(90), ReactorAction.Insert, Id(31)).HasNewCommit, Is.True);
            Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.ReservePriority)); Assert.That(f.Power.Delivered, Is.Zero); Balanced(f.Power);
        }

        [Test] public void PartitionedSamplingKeepsTheSameRoutedPowerAndFuelAtEveryValveChange()
        {
            var large = new Setup(); var small = new Setup(); large.Run(); small.Run(); long host = 0;
            foreach (long at in new long[] { 99, 100, 101, 300, 899, 1000 })
            {
                large.World.AdvanceTo(at);
                while (host < at) { host = Math.Min(at, host + 17); small.World.AdvanceTo(host); }
                Assert.That(new[] { small.Power.Available, small.Power.Generated, small.Power.Delivered, small.Power.Spilled, small.Core.WorkMilliseconds },
                    Is.EqualTo(new[] { large.Power.Available, large.Power.Generated, large.Power.Delivered, large.Power.Spilled, large.Core.WorkMilliseconds }));
                var route = (ReactorOutputRouting)(at % 3); large.Route(route); small.Route(route);
            }
            Balanced(large.Power); Balanced(small.Power);
        }

        [TestCase(-1)] [TestCase(3)]
        public void UndefinedRoutingIsMalformedBeforeSequenceConsumption(int value)
        {
            var f = new Setup(); var reply = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.SetOutputRouting, 0, outputRouting: (ReactorOutputRouting)value)));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(reply.IsTerminal, Is.False);
            Assert.That(f.Route(ReactorOutputRouting.GridPriority).HasNewCommit, Is.True);
        }

        [Test] public void OtherReactorActionsCannotSmuggleASecondRoutingMutation()
        {
            var f = new Setup(); var reply = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, Id(90),
                reactor: new ReactorRequest(ReactorAction.SetCooling, 0, cooling: true, outputRouting: ReactorOutputRouting.GridPriority)));
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(reply.IsTerminal, Is.False);
            Assert.That(f.Core.Cooling, Is.False); Assert.That(f.Core.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced));
        }
    }
}
