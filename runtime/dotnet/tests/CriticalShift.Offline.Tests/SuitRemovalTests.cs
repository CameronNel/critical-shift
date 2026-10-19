using System;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SuitRemovalTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Clearance : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid actor, long attempt) => RecoveryClearance.Safe; }
        private sealed class Setup
        {
            internal readonly TestAccess Access = new TestAccess();
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port, Other;
            internal readonly WorkerContaminationFeed Feed;
            internal WorkerView Worker => World.GetWorker(Id(10))!;
            internal Setup(WorkerSuit suit = WorkerSuit.Intact, long shift = 60000, int contamination = 43, long removal = 5000)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), Access, new Clearance());
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11)); World.RegisterObject(Id(30));
                World.SuitFitting.Register(Id(90), new SuitFittingDefinition(15000, removal));
                World.RegisterWorkerContaminationSource(Id(95), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20, 1000));
                World.Reactor.Register(Id(50), new ReactorDefinition(Id(51)));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21));
                Feed = new WorkerContaminationFeed(World, Id(10), Id(95)); World.Start();
                World.SetWorkerEnvironment(World.Epoch, Id(10), Worker.Revision, suit, contamination);
            }
            internal InteractionReply Remove() => Port.OperateSuitFitting(Id(90), SuitFittingAction.Remove);
            internal InteractionReply Cancel() => Port.OperateSuitFitting(Id(90), SuitFittingAction.Cancel);
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True, reply.Status + "/" + reply.SuitFitting?.Status);

        [TestCase(WorkerSuit.Intact)] [TestCase(WorkerSuit.Compromised)]
        public void RemovalRetainsOriginalProtectionAndMobilityUntilExactCompletion(WorkerSuit suit)
        {
            var f = new Setup(suit); var before = f.Worker; Applied(f.Remove()); var attempt = f.Worker.SuitFitting!;
            Assert.That(attempt.OriginalSuit, Is.EqualTo(suit)); Assert.That(attempt.TargetSuit, Is.EqualTo(WorkerSuit.None)); Assert.That(attempt.DueAtMilliseconds, Is.EqualTo(5000));
            f.World.AdvanceTo(4999); Assert.That(f.Worker.Suit, Is.EqualTo(suit)); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(800)); Assert.That(f.Worker.CanInteract, Is.False);
            var done = f.World.AdvanceTo(5000).SuitFittingChanges.Single(); Assert.That(done.Kind, Is.EqualTo(SuitFittingEvent.Completed));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(1000)); Assert.That(f.Worker.CanInteract, Is.True);
            Assert.That(f.Worker.Contamination, Is.EqualTo(43)); Assert.That(f.Worker.LastCauseId, Is.EqualTo(before.LastCauseId)); Assert.That(f.Worker.LastHazardId, Is.EqualTo(before.LastHazardId));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.World.View.ActiveClaimCount, Is.Zero); Assert.That(attempt.OriginalSuit, Is.EqualTo(suit));
        }

        [TestCase(WorkerSuit.Intact, 5)] [TestCase(WorkerSuit.Compromised, 10)]
        public void RemovalCompletionChangesOnlyFuturePpeAndDoesNotResetExposureCooldown(WorkerSuit suit, int originalLoad)
        {
            var f = new Setup(suit, contamination: 0); Applied(f.Remove()); f.World.AdvanceTo(4999);
            Assert.That(f.Feed.ObserveIfDue()!.ContaminationContact!.EffectiveUnits, Is.EqualTo(originalLoad));
            f.World.AdvanceTo(5000); Assert.That(f.Feed.ObserveIfDue(), Is.Null); Assert.That(f.Worker.Contamination, Is.EqualTo(originalLoad));
            f.World.AdvanceTo(5999); var contact = f.Feed.ObserveIfDue()!.ContaminationContact!;
            Assert.That(contact.EffectiveUnits, Is.EqualTo(20)); Assert.That(contact.Sequence, Is.EqualTo(2)); Assert.That(f.Worker.Contamination, Is.EqualTo(originalLoad + 20));
        }

        [Test] public void AlreadyUnsuitedRemovalIsNoChangeWithoutClockOrCounterMutation()
        {
            var f = new Setup(WorkerSuit.None); var before = f.Worker; var result = f.Remove();
            Assert.That(result.SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.NoChange)); Assert.That(f.Worker.Revision, Is.EqualTo(before.Revision));
            Assert.That(f.World.SuitFitting.Summary.Started, Is.Zero); Assert.That(f.World.View.ElapsedMilliseconds, Is.Zero); Assert.That(f.Worker.Contamination, Is.EqualTo(43));
        }

        [TestCase("hands")] [TestCase("station")] [TestCase("range")]
        public void RemovalRetainsTheExistingFreeHandsOccupancyAndSpatialAdmission(string blocked)
        {
            var f = new Setup();
            if (blocked == "hands") Applied(f.Port.Grab(Id(30)));
            if (blocked == "station") Applied(f.Other.OperateSuitFitting(Id(90), SuitFittingAction.Start));
            if (blocked == "range") f.Access.Decision = AccessDecision.OutOfReach;
            var result = f.Remove(); Assert.That(result.HasNewCommit, Is.False);
            if (blocked == "range") Assert.That(result.Status, Is.EqualTo(InteractionStatus.OutOfReach));
            else Assert.That(result.SuitFitting!.Status, Is.EqualTo(blocked == "hands" ? SuitFittingStatus.HandsOccupied : SuitFittingStatus.StationOccupied));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact)); Assert.That(f.Worker.SuitFitting, Is.Null);
        }

        [Test] public void RemovalCannotBypassBusyWorkEvenWhenItsTargetWouldAlreadyMatch()
        {
            var f = new Setup(WorkerSuit.None); Applied(f.Port.OperateSuitFitting(Id(90), SuitFittingAction.Start)); var attempt = f.Worker.SuitFitting!;
            Assert.That(f.Remove().Status, Is.EqualTo(InteractionStatus.ActorUnavailable)); Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(attempt.Id));
            Assert.That(f.Worker.SuitFitting.TargetSuit, Is.EqualTo(WorkerSuit.Intact));
        }

        [Test] public void PausedRemovalFreezesItsDeadlineAndOwnCancellationKeepsTheOriginalSuit()
        {
            var f = new Setup(); Applied(f.Remove()); f.World.AdvanceTo(2000); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(12000);
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact)); Assert.That(f.Worker.SuitFitting!.DueAtMilliseconds, Is.EqualTo(5000));
            Applied(f.Cancel()); Assert.That(f.Worker.CanInteract, Is.True); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(15000); Assert.That(f.World.SuitFitting.Summary.Completed, Is.Zero);
        }

        [Test] public void SampledAccessLossAfterTheDueTimeInterruptsAtCurrentObservationWithoutBackdating()
        {
            var f = new Setup(); Applied(f.Remove()); f.Access.Decision = AccessDecision.OutOfReach;
            var result = f.World.AdvanceTo(6000).SuitFittingChanges.Single();
            Assert.That(result.Kind, Is.EqualTo(SuitFittingEvent.Interrupted)); Assert.That(result.ShiftMilliseconds, Is.EqualTo(6000));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact)); Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.World.SuitFitting.Summary.Completed, Is.Zero);
        }

        [TestCase(WorkerImpact.Knockdown)] [TestCase(WorkerImpact.Incapacitating)]
        public void ImpactInterruptsRemovalOnceAndRetainsOriginalGearAndInjuryCause(WorkerImpact severity)
        {
            var f = new Setup(); Applied(f.Remove()); var attempt = f.Worker.SuitFitting!;
            f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, severity, 0, Id(701), Id(702));
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact)); Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(702)));
            Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.EqualTo(1));
            var row = f.World.Trace.Records.Single(r => r.SuitFittingChange?.Kind == SuitFittingEvent.Interrupted);
            Assert.That(row.SuitFittingChange!.Attempt.TargetSuit, Is.EqualTo(WorkerSuit.None)); Assert.That(row.CycleId, Is.EqualTo(attempt.Id)); Assert.That(row.CauseId, Is.EqualTo(Id(702)));
            f.World.AdvanceTo(6000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
        }

        [Test] public void TrustedSuitReplacementInterruptsRemovalEvenIfTheOriginalGearIsRestoredBeforePolling()
        {
            var f = new Setup(); Applied(f.Remove());
            f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), f.Worker.Revision, WorkerSuit.Compromised, 43);
            f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), f.Worker.Revision, WorkerSuit.Intact, 43); f.World.AdvanceTo(5000);
            Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.EqualTo(1)); Assert.That(f.World.SuitFitting.Summary.Completed, Is.Zero); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
        }

        [Test] public void OldRemovalReplayAndCancellationCannotRemoveOrCancelANewFitting()
        {
            var f = new Setup(); long revision = f.Worker.Revision; Applied(f.Remove()); var old = f.Worker.SuitFitting!; f.World.AdvanceTo(5000);
            Applied(f.Port.OperateSuitFitting(Id(90), SuitFittingAction.Start)); var current = f.Worker.SuitFitting!;
            var stale = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 3, InteractionKind.SuitFitting, Id(90),
                suitFitting: new SuitFittingRequest(SuitFittingAction.Cancel, attempt: old.Id)));
            Assert.That(stale.SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.StaleAttempt)); Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(current.Id));
            f.World.AdvanceTo(20000);
            var retry = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.SuitFitting, Id(90),
                suitFitting: new SuitFittingRequest(SuitFittingAction.Remove, revision)));
            Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False); Assert.That(retry.SuitFitting!.Change!.Attempt.TargetSuit, Is.EqualTo(WorkerSuit.None));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact)); Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(2));
        }

        [Test] public void SameSequenceCannotChangeRemovalIntoAFitting()
        {
            var f = new Setup(); long revision = f.Worker.Revision; Applied(f.Remove());
            var changed = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.SuitFitting, Id(90),
                suitFitting: new SuitFittingRequest(SuitFittingAction.Start, revision)));
            Assert.That(changed.Status, Is.EqualTo(InteractionStatus.PayloadMismatch)); Assert.That(f.Worker.SuitFitting!.TargetSuit, Is.EqualTo(WorkerSuit.None));
        }

        [TestCase(4999, false)] [TestCase(5000, true)] [TestCase(5001, true)]
        public void RemovalDeadlineSettlesOnlyExactCompletedWorkBeforeCutoff(long deadline, bool completed)
        {
            var f = new Setup(shift: deadline); Applied(f.Remove()); f.World.AdvanceTo(6000); var worker = f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == Id(10));
            Assert.That(worker.Suit, Is.EqualTo(completed ? WorkerSuit.None : WorkerSuit.Intact)); Assert.That(worker.Contamination, Is.EqualTo(43));
            Assert.That(f.World.Debrief.SuitFitting.Completed, Is.EqualTo(completed ? 1 : 0)); Assert.That(f.World.Debrief.SuitFitting.Cancelled, Is.EqualTo(completed ? 0 : 1));
        }

        [Test] public void RemovalUsesItsOwnShorterDurationAtTheMaximumShiftClock()
        {
            var f = new Setup(shift: long.MaxValue); f.World.AdvanceTo(long.MaxValue - 5000); Applied(f.Remove());
            Assert.That(f.Worker.SuitFitting!.DueAtMilliseconds, Is.EqualTo(long.MaxValue)); f.World.AdvanceTo(long.MaxValue);
            Assert.That(f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == Id(10)).Suit, Is.EqualTo(WorkerSuit.None));
        }

        [TestCase("negative-revision")] [TestCase("unexpected-attempt")] [TestCase("version")]
        public void MalformedRemovalCannotConsumeTheNextSequence(string variant)
        {
            var f = new Setup(); var request = new SuitFittingRequest(SuitFittingAction.Remove,
                variant == "negative-revision" ? -1 : f.Worker.Revision, variant == "unexpected-attempt" ? Id(999) : Guid.Empty,
                variant == "version" ? 0 : SuitFittingRequest.CurrentVersion);
            var denied = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.SuitFitting, Id(90), suitFitting: request));
            Assert.That(denied.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(denied.IsTerminal, Is.False); Applied(f.Remove());
        }

        [TestCase(0)] [TestCase(999)] [TestCase(15001)]
        public void RemovalDurationBoundsDoNotRelaxTheExistingFittingBounds(long removal)
        { Assert.Throws<ArgumentOutOfRangeException>(() => new SuitFittingDefinition(15000, removal)); Assert.Throws<ArgumentOutOfRangeException>(() => new SuitFittingDefinition(5000, 5000)); }

        [TestCase(SuitCondition.Compromised)] [TestCase((SuitCondition)99)]
        public void DomainCannotUseRemovalToCreateAClientChosenDamagedOrUnknownSuit(SuitCondition target)
        {
            var state = new WorkerState(Id(10)); state.SetEnvironment(0, SuitCondition.Intact, 12);
            Assert.That(state.BeginSuitFitting(state.Snapshot.Revision, Id(90), Id(91), new SuitFittingRules(), 0, target), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(state.Snapshot.Suit, Is.EqualTo(SuitCondition.Intact)); Assert.That(state.Snapshot.SuitFitting, Is.Null);
        }

        [Test] public void RemovalTraceAndDebriefDistinguishTheOperationAndPreservePriorInjury()
        {
            var f = new Setup(); f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, WorkerImpact.Knockdown, 0, Id(701), Id(702));
            var down = f.Worker; f.World.BeginWorkerRecovery(f.World.Epoch, Id(10), down.RecoveryEpisode, down.Revision);
            f.World.CompleteWorkerRecovery(f.World.Epoch, Id(10), f.Worker.RecoveryAttempt); Applied(f.Remove()); f.World.AdvanceTo(5000); f.World.Stop();
            var rows = SandboxTraceFeed.DebriefEntries(f.World.Debrief!);
            Assert.That(rows.Count(e => e.Description.Contains("Suit removal started")), Is.EqualTo(1));
            Assert.That(rows.Count(e => e.Description.Contains("Protective suit removed")), Is.EqualTo(1));
            var end = f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == Id(10)); Assert.That(end.LastCauseId, Is.EqualTo(Id(702))); Assert.That(end.LastHazardId, Is.EqualTo(Id(701)));
            Assert.That(end.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(end.Contamination, Is.EqualTo(43));
        }
    }
}
