using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Domain;
using CriticalShift.Features.Production.Domain;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class FaultSettlementEvidenceTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        private sealed class Policies : IInteractionAccessPolicy, IWorkerRecoveryPolicy
        {
            internal bool FailSecond;
            public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind)
            {
                if (!FailSecond) return AccessDecision.Allowed;
                if (actor == Id(11)) throw new InvalidOperationException("Injected station observation failure.");
                return AccessDecision.OutOfReach;
            }
            public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => RecoveryClearance.Safe;
        }
        private static void Applied(InteractionReply r) => Assert.That(r.HasNewCommit, Is.True);
        private static WorldSession NewWorld(long duration, Policies? policies = null)
        {
            policies = policies ?? new Policies();
            var w = new WorldSession(new WorldSessionConfiguration(42, duration, true), policies, policies, recoveryCompletionWindowMilliseconds: 500);
            w.RegisterConnection(Id(20), Id(10)); w.RegisterConnection(Id(21), Id(11)); return w;
        }
        private static void OverflowWorker(WorldSession world, int actor)
        {
            var owner = typeof(WorldSession).GetField("_workers", Private)!.GetValue(world)!;
            var states = (IDictionary<Guid, WorkerState>)owner.GetType().GetField("_workers", Private)!.GetValue(owner)!;
            typeof(WorkerState).GetField("_revision", Private)!.SetValue(states[Id(actor)], long.MaxValue);
        }
        private static void Closed(WorldSession w)
        {
            Assert.That(w.View.Outcome, Is.EqualTo(WorldOutcome.Faulted)); Assert.That(w.WorkerCount, Is.Zero);
            Assert.That(w.View.ActiveClaimCount, Is.Zero); Assert.That(w.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(w.Production.MachineCount, Is.Zero); Assert.That(w.Reactor.View, Is.Null);
            Assert.That(w.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended), Is.False);
            Assert.That(w.Debrief!.Timeline.Last().Kind, Is.EqualTo(SessionTraceKind.Faulted));
        }

        [TestCase(false, 1000)] [TestCase(false, 2000)] [TestCase(true, 1000)] [TestCase(true, 2000)]
        public void EarlierCommittedConversionSurvivesALaterMachineOrReactorSettlementFailure(bool reactorFails, long duration)
        {
            var w = NewWorld(duration);
            for (int i = 0; i < 2; i++)
            {
                w.Production.RegisterBatch(Id(30 + i), Id(60 + i), Id(70), Id(80 + i), MaterialKind.Ore, 100);
                w.Production.RegisterMachine(Id(40 + i), new MachineRecipe(Id(50 + i), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100, yieldPermille: 800));
            }
            w.Reactor.Register(Id(90), new ReactorDefinition(Id(91)));
            w.Production.RegisterBatch(Id(32), Id(62), Id(70), Id(82), MaterialKind.Fuel, 10);
            var p = new LocalCommandPort(w, Id(20)); w.Start();
            for (int i = 0; i < (reactorFails ? 1 : 2); i++)
            {
                Applied(p.Grab(Id(30 + i))); Applied(p.OperateMachine(Id(40 + i), ProductionAction.Insert, Id(30 + i)));
                Applied(p.OperateMachine(Id(40 + i), ProductionAction.Start));
            }
            if (reactorFails)
            {
                Applied(p.Grab(Id(32))); Applied(p.OperateReactor(Id(90), ReactorAction.Insert, Id(32)));
                Applied(p.OperateReactor(Id(90), ReactorAction.SetCooling, cooling: true)); Applied(p.OperateReactor(Id(90), ReactorAction.Start));
                typeof(ReactorOperations).GetField("_revision", Private)!.SetValue(w.Reactor, long.MaxValue);
            }
            else
            {
                var machines = (Dictionary<Guid, MachineState>)typeof(ProductionOperations).GetField("_machines", Private)!.GetValue(w.Production)!;
                typeof(MachineState).GetField("<Revision>k__BackingField", Private)!.SetValue(machines[Id(41)], long.MaxValue);
            }
            Assert.Throws<OverflowException>(() => w.AdvanceTo(1000)); Closed(w);
            var completed = w.Debrief!.Timeline.Where(r => r.ProductionEvent == ProductionEvent.Completed).ToArray();
            Assert.That(completed.Length, Is.EqualTo(1)); var row = completed.Single();
            Assert.That(row.EntityId, Is.EqualTo(Id(40))); Assert.That(row.OccurredAtMilliseconds, Is.EqualTo(1000));
            Assert.That(row.BatchId, Is.EqualTo(Id(60))); Assert.That(row.MaterialCauseId, Is.EqualTo(Id(80))); Assert.That(row.WasteUnits, Is.EqualTo(20));
            Assert.That(row.OutputBatchId, Is.Not.EqualTo(Guid.Empty)); Assert.That(row.ProductionChange!.Output!.ParentBatchId, Is.EqualTo(Id(60)));
            Assert.That(w.Debrief.Production.CompletedCycles, Is.EqualTo(1)); Assert.That(w.Debrief.Production.CancelledCycles, Is.EqualTo(1));
            Assert.That(w.Debrief.Production.ActiveUnits + w.Debrief.Production.WasteUnits, Is.EqualTo(210));
            Assert.That(w.Debrief.Timeline.Last().OccurredAtMilliseconds, Is.EqualTo(1000)); Assert.That(w.Debrief.World.ElapsedMilliseconds, Is.Zero);
            w.Stop(); Assert.That(w.Debrief.Timeline.Count(r => r.ProductionEvent == ProductionEvent.Completed), Is.EqualTo(1));
        }

        [TestCase(false)] [TestCase(true)]
        public void EarlierSuitCompletionOrInterruptionSurvivesTheNextWorkersFailure(bool accessFailure)
        {
            var policy = new Policies(); var w = NewWorld(20000, policy);
            w.SuitFitting.Register(Id(90), new SuitFittingDefinition(15000)); w.SuitFitting.Register(Id(91), new SuitFittingDefinition(15000));
            var p = new LocalCommandPort(w, Id(20)); var other = new LocalCommandPort(w, Id(21)); w.Start();
            Applied(p.OperateSuitFitting(Id(90), SuitFittingAction.Start)); Applied(other.OperateSuitFitting(Id(91), SuitFittingAction.Start));
            if (accessFailure) policy.FailSecond = true; else OverflowWorker(w, 11);
            if (accessFailure) Assert.Throws<InvalidOperationException>(() => w.AdvanceTo(15000)); else Assert.Throws<OverflowException>(() => w.AdvanceTo(15000));
            Closed(w); var events = w.Debrief!.Timeline.Where(r => r.SuitFittingChange?.Kind == (accessFailure ? SuitFittingEvent.Interrupted : SuitFittingEvent.Completed)).ToArray();
            Assert.That(events.Length, Is.EqualTo(1)); Assert.That(events.Single().ActorId, Is.EqualTo(Id(10))); Assert.That(events.Single().OccurredAtMilliseconds, Is.EqualTo(15000));
            Assert.That(w.Debrief.SuitFitting.Completed, Is.EqualTo(accessFailure ? 0 : 1)); Assert.That(w.Debrief.SuitFitting.Interrupted, Is.EqualTo(accessFailure ? 1 : 0));
            Assert.That(w.Debrief.SuitFitting.Cancelled, Is.EqualTo(1));
        }

        [TestCase(1000)] [TestCase(2000)]
        public void EarlierRecoveryExpirySurvivesTheNextWorkersFailure(long duration)
        {
            var w = NewWorld(duration); w.Start();
            for (int i = 0; i < 2; i++)
            {
                var hit = w.ApplyWorkerImpact(w.Epoch, Id(10 + i), 1, WorkerImpact.Knockdown, 0, Id(70), Id(80 + i));
                Assert.That(w.BeginWorkerRecovery(w.Epoch, Id(10 + i), hit.Worker!.RecoveryEpisode, hit.Worker.Revision).Changed, Is.True);
            }
            OverflowWorker(w, 11); Assert.Throws<OverflowException>(() => w.AdvanceTo(1000)); Closed(w);
            var row = w.Debrief!.Timeline.Single(r => r.Kind == SessionTraceKind.RecoveryExpired);
            Assert.That(row.ActorId, Is.EqualTo(Id(10))); Assert.That(row.OccurredAtMilliseconds, Is.EqualTo(500)); Assert.That(row.CauseId, Is.EqualTo(Id(80)));
            Assert.That(w.Debrief.Timeline.Last().OccurredAtMilliseconds, Is.EqualTo(1000));
        }

        [TestCase(0)] [TestCase(1)]
        public void ExpiredClaimBatchPreparesEveryRevisionBeforeReleasingAnyHolderOrAdvancingTime(int corrupt)
        {
            var claims = new ExclusiveClaimStore(4, 100);
            for (int i = 0; i < 2; i++) { claims.Register(Id(30 + i)); Assert.That(claims.TryGrab(Id(30 + i), Id(10 + i), 0).Changed, Is.True); }
            var before = new[] { claims.Get(Id(30))!, claims.Get(Id(31))! };
            var revision = typeof(ClaimSnapshot).GetField("<Revision>k__BackingField", Private)!;
            revision.SetValue(before[corrupt], long.MaxValue);
            Assert.Throws<OverflowException>(() => claims.AdvanceTo(100));
            Assert.That(claims.NowMilliseconds, Is.Zero); Assert.That(claims.ActiveClaimCount, Is.EqualTo(2));
            for (int i = 0; i < 2; i++)
            { Assert.That(claims.Get(Id(30 + i)), Is.SameAs(before[i])); Assert.That(claims.ActorHasClaim(Id(10 + i)), Is.True); }
            revision.SetValue(before[corrupt], 1L); var released = claims.AdvanceTo(100);
            Assert.That(released.Select(c => c.EntityId), Is.EqualTo(new[] { Id(30), Id(31) }));
            Assert.That(released.All(c => c.HolderId == null && c.Revision == 2 && c.LeaseGeneration == 1), Is.True);
            Assert.That(claims.ActiveClaimCount, Is.Zero); Assert.That(claims.AdvanceTo(100), Is.Empty);
        }

        [Test] public void FailureAfterNormalSettlementPublicationCannotJournalItsFactsTwice()
        {
            var w = NewWorld(10000); w.RegisterObject(Id(100)); w.RegisterObject(Id(101));
            w.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Ore, 100);
            w.Production.RegisterMachine(Id(40), new MachineRecipe(Id(50), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100));
            var p = new LocalCommandPort(w, Id(20)); var other = new LocalCommandPort(w, Id(21)); w.Start();
            Applied(p.Grab(Id(30))); Applied(p.OperateMachine(Id(40), ProductionAction.Insert, Id(30))); Applied(p.OperateMachine(Id(40), ProductionAction.Start));
            Applied(p.Grab(Id(100))); Applied(other.Grab(Id(101)));
            var interaction = typeof(WorldSession).GetField("_interaction", Private)!.GetValue(w)!;
            var claims = (ExclusiveClaimStore)typeof(InteractionWorld).GetField("_claims", Private)!.GetValue(interaction)!;
            typeof(ClaimSnapshot).GetField("<Revision>k__BackingField", Private)!.SetValue(claims.Get(Id(101)), long.MaxValue);
            Assert.Throws<OverflowException>(() => w.AdvanceTo(3000)); Closed(w);
            Assert.That(w.Trace.Records.Count(r => r.ProductionEvent == ProductionEvent.Completed), Is.EqualTo(1));
            Assert.That(w.Debrief!.Timeline.Count(r => r.ProductionEvent == ProductionEvent.Completed), Is.EqualTo(1));
            Assert.That(w.Debrief.World.ElapsedMilliseconds, Is.EqualTo(3000));
            Assert.That(w.Debrief.Timeline.Last().OccurredAtMilliseconds, Is.EqualTo(3000));
            Assert.That(w.Debrief.Timeline.Single(r => r.ProductionEvent == ProductionEvent.Completed).OccurredAtMilliseconds, Is.EqualTo(1000));
        }
    }
}
