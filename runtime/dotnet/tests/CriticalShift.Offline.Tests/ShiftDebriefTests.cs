using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class ShiftDebriefTests
    {
        private sealed class Clearance : IWorkerRecoveryPolicy
        {
            internal RecoveryClearance Result = RecoveryClearance.Safe;
            public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => Result;
        }
        private static WorldSession World(int capacity = 128, IWorkerRecoveryPolicy? clearance = null)
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, 5000, true), new TestAccess(), clearance, capacity);
            world.RegisterConnection(Fixture.Id(20), Fixture.Id(10)); world.RegisterObject(Fixture.Id(30)); world.Start(); return world;
        }
        private static WorkerReply Hit(WorldSession world, long sequence = 1, WorkerImpact severity = WorkerImpact.Knockdown) =>
            world.ApplyWorkerImpact(world.Epoch, Fixture.Id(10), sequence, severity, 0, Fixture.Id(70), Fixture.Id(80));

        [Test] public void DebriefFreezesTheFirstTerminalResultAndCanonicalResourceTotals()
        {
            var f = new ReactorFixture(shift: 1000, start: false);
            f.World.Contracts.Register(new ShiftContractDefinition(Fixture.Id(920), "Grid supply",
                new GridDemandWave(Fixture.Id(921), "Supply", 1000, 40)));
            f.World.Start(); f.Run(); Assert.That(f.World.Debrief, Is.Null);
            f.World.AdvanceTo(5000); var result = f.World.Debrief!;
            Assert.That(result.World.Outcome, Is.EqualTo(WorldOutcome.Succeeded));
            Assert.That(result.Power!.Delivered, Is.EqualTo(40)); Assert.That(result.Production.CompletedCycles, Is.EqualTo(1));
            Assert.That(result.Contract!.AllPeriodsMet, Is.True); Assert.That(result.WorkersAtEnd.Count, Is.EqualTo(2));
            Assert.That(result.World.ConnectedPlayerCount, Is.Zero); Assert.That(result.World.ActiveClaimCount, Is.Zero);
            Assert.That(result.Timeline.Last().Kind, Is.EqualTo(SessionTraceKind.Ended));
            for (int i = 0; i < 10; i++) { f.World.Stop(); f.World.AdvanceTo(5000); }
            Assert.That(f.World.Debrief, Is.SameAs(result)); Assert.That(result.World.Phase, Is.EqualTo(WorldPhase.Ended));
            var successor = f.World.Restart(new TestAccess()); Assert.That(successor.Debrief, Is.Null);
            Assert.That(result.Power.Delivered, Is.EqualTo(40)); Assert.That(result.WorkersAtEnd.Count, Is.EqualTo(2));
        }

        [Test] public void IncidentTotalsSurviveTraceEvictionAndIgnoreDuplicateImpacts()
        {
            var world = World(capacity: 1);
            for (int i = 1; i <= 50; i++)
            {
                Assert.That(Hit(world, i).Changed, Is.True);
                for (int retry = 0; retry < 3; retry++) Assert.That(Hit(world, i).Status, Is.EqualTo(WorkerStatus.Duplicate));
            }
            world.Stop(); var result = world.Debrief!;
            Assert.That(result.Incidents.WorkerImpacts, Is.EqualTo(50)); Assert.That(result.Incidents.Incapacitations, Is.Zero);
            Assert.That(result.Timeline.Count, Is.EqualTo(1)); Assert.That(result.DroppedIncidents, Is.EqualTo(51));
            Assert.That(result.WorkersAtEnd.Single().Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(world.Trace.DroppedRecords, Is.GreaterThan(150));
        }

        [Test] public void AidAndStandingRecoveryCountOnlyTheirSuccessfulCommits()
        {
            var clearance = new Clearance(); var world = World(clearance: clearance);
            Hit(world, severity: WorkerImpact.Incapacitating);
            var worker = world.GetWorker(Fixture.Id(10))!;
            Assert.That(world.BeginWorkerRecovery(world.Epoch, worker.Id, worker.RecoveryEpisode, worker.Revision).Status, Is.EqualTo(WorkerStatus.RequiresAid));
            Assert.That(world.StabilizeWorker(world.Epoch, worker.Id, worker.Revision, 0).Changed, Is.True);
            worker = world.GetWorker(worker.Id)!;
            var begin = world.BeginWorkerRecovery(world.Epoch, worker.Id, worker.RecoveryEpisode, worker.Revision);
            long attempt = begin.Worker!.RecoveryAttempt;
            Assert.That(world.CompleteWorkerRecovery(world.Epoch, worker.Id, attempt).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(world.CompleteWorkerRecovery(world.Epoch, worker.Id, attempt).Status, Is.EqualTo(WorkerStatus.StaleRecovery));
            Hit(world, 2); worker = world.GetWorker(worker.Id)!;
            begin = world.BeginWorkerRecovery(world.Epoch, worker.Id, worker.RecoveryEpisode, worker.Revision);
            clearance.Result = RecoveryClearance.Blocked;
            Assert.That(world.CompleteWorkerRecovery(world.Epoch, worker.Id, begin.Worker!.RecoveryAttempt).Changed, Is.True);
            world.Stop(); var totals = world.Debrief!.Incidents;
            Assert.That(totals.WorkerImpacts, Is.EqualTo(2)); Assert.That(totals.Incapacitations, Is.EqualTo(1));
            Assert.That(totals.Stabilizations, Is.EqualTo(1)); Assert.That(totals.StandingRecoveries, Is.EqualTo(1));
        }

        [Test] public void JammedAndCancelledBypassDoesNotCountAsACompletedBypassConversion()
        {
            var f = new ProductionFixture(moisture: 900);
            f.Load(); f.Act(ProductionAction.Start, bypass: true); f.World.AdvanceTo(200);
            f.Act(ProductionAction.SetPower); f.Act(ProductionAction.CancelCycle); f.World.Stop();
            Assert.That(f.World.Debrief!.Incidents.MachineJams, Is.EqualTo(1));
            Assert.That(f.World.Debrief.Incidents.BypassedConversions, Is.Zero);
            Assert.That(f.World.Debrief.Production.CancelledCycles, Is.EqualTo(1));
        }

        [Test] public void CompletedBypassIsCountedOnceDespiteHistoricalStartRetries()
        {
            var f = new ProductionFixture(start: false); var port = new LocalCommandPort(f.World, f.Connection); f.World.Start();
            port.Grab(f.Box); port.OperateMachine(f.Machine, ProductionAction.Insert, f.Box);
            port.OperateMachine(f.Machine, ProductionAction.Start, bypass: true);
            for (int i = 0; i < 20; i++) Assert.That(port.ReplayLast().IsReplay, Is.True);
            f.World.AdvanceTo(500);
            for (int i = 0; i < 20; i++) { port.ReplayLast(); f.World.AdvanceTo(500); }
            f.World.Stop(); Assert.That(port.Debrief!.Incidents.BypassedConversions, Is.EqualTo(1));
            Assert.That(port.Debrief.Production.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void LargeSampleDebriefOrdersTypedOccurrencesAcrossReactorMachineAndDemand()
        {
            var f = new ProductionFixture(start: false, shift: 5000);
            f.World.Reactor.Register(Fixture.Id(90), new ReactorDefinition(Fixture.Id(91)));
            f.World.Production.RegisterBatch(Fixture.Id(31), Fixture.Id(61), Fixture.Id(71), Fixture.Id(81), MaterialKind.Fuel, 100);
            f.World.Contracts.Register(new ShiftContractDefinition(Fixture.Id(920), "Supply",
                new GridDemandWave(Fixture.Id(921), "First", 2500, 0), new GridDemandWave(Fixture.Id(922), "Last", 5000, 0)));
            var port = new LocalCommandPort(f.World, f.Connection); f.World.Start();
            port.Grab(f.Box); port.OperateMachine(f.Machine, ProductionAction.Insert, f.Box); port.OperateMachine(f.Machine, ProductionAction.Start);
            port.Grab(Fixture.Id(31)); port.OperateReactor(Fixture.Id(90), ReactorAction.Insert, Fixture.Id(31));
            port.OperateReactor(Fixture.Id(90), ReactorAction.SetCooling, cooling: true); port.OperateReactor(Fixture.Id(90), ReactorAction.Start);
            port.OperateReactor(Fixture.Id(90), ReactorAction.SetCooling);
            f.World.AdvanceTo(5000); var rows = f.World.Debrief!.Timeline;
            Assert.That(rows.Select(r => r.OccurredAtMilliseconds), Is.Ordered);
            Assert.That(rows.Single(r => r.ReactorEvent == ReactorEvent.Warning).OccurredAtMilliseconds, Is.EqualTo(400));
            Assert.That(rows.Single(r => r.ReactorEvent == ReactorEvent.Tripped).OccurredAtMilliseconds, Is.EqualTo(800));
            Assert.That(rows.Single(r => r.ProductionEvent == ProductionEvent.Completed).OccurredAtMilliseconds, Is.EqualTo(1000));
            Assert.That(rows.Where(r => r.DemandChange != null).Select(r => r.OccurredAtMilliseconds), Is.EqualTo(new long[] { 2500, 5000 }));
            Assert.That(f.World.Debrief.Incidents.ReactorTrips, Is.EqualTo(1));
        }

        [Test] public void ExhaustedTraceSequenceStillCountsNewIncidentsWithoutFaultingGameplay()
        {
            var world = World();
            var diagnostics = typeof(WorldSession).GetField("_diagnostics", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(world)!;
            diagnostics.GetType().GetField("_sequence", BindingFlags.NonPublic | BindingFlags.Instance)!.SetValue(diagnostics, long.MaxValue);
            Hit(world); world.Stop();
            Assert.That(world.Debrief!.Incidents.WorkerImpacts, Is.EqualTo(1));
            Assert.That(world.Debrief.DroppedIncidents, Is.EqualTo(2)); Assert.That(world.Debrief.World.Outcome, Is.EqualTo(WorldOutcome.Aborted));
        }

        [TestCase(WorldEndReason.Aborted, WorldOutcome.Aborted)]
        [TestCase(WorldEndReason.HostLost, WorldOutcome.HostLost)]
        [TestCase(WorldEndReason.Failed, WorldOutcome.Failed)]
        public void DebriefRetainsExplicitTerminalReasons(WorldEndReason reason, WorldOutcome expected)
        {
            var world = World(); world.Finish(world.Epoch, reason);
            Assert.That(world.Debrief!.World.Outcome, Is.EqualTo(expected));
            world.Stop(); Assert.That(world.Debrief.World.Outcome, Is.EqualTo(expected));
        }

        [Test] public void DebriefCollectionsCannotBeUsedToMutateTheTerminalEvidence()
        {
            var world = World(); world.Stop(); var result = world.Debrief!;
            Assert.Throws<NotSupportedException>(() => ((IList<WorkerView>)result.WorkersAtEnd).Clear());
            Assert.Throws<NotSupportedException>(() => ((IList<SessionTraceRecord>)result.Timeline).Clear());
        }
    }
}
