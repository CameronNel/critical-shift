using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SuitFittingTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Clearance : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => RecoveryClearance.Safe; }
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly TestAccess Access = new TestAccess();
            internal readonly LocalCommandPort Port, Other;
            internal Guid Station => Id(90);
            internal Guid Actor => Id(10);
            internal WorkerView Worker => World.GetWorker(Actor)!;
            internal Setup(long shift = 60000, bool start = true, int trace = 128)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), Access, new Clearance(), traceCapacity: trace);
                World.RegisterConnection(Id(20), Actor); World.RegisterConnection(Id(21), Id(11)); World.RegisterObject(Id(30));
                World.Production.RegisterBatch(Id(31), Id(61), Id(71), Id(81), MaterialKind.Ore, 10);
                World.Production.RegisterMachine(Id(40), new MachineRecipe(Id(41), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 200, 100));
                World.Reactor.Register(Id(50), new ReactorDefinition(Id(51))); World.Medical.Register(Id(60), new MedicalDefinition());
                World.Doors.Register(Id(70), "fit-door", DoorState.Closed, DoorState.Open);
                World.SuitFitting.Register(Station, new SuitFittingDefinition(15000));
                World.RegisterWorkerContaminationSource(Id(95), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21)); if (start) World.Start();
            }
            internal InteractionReply Start() => Port.OperateSuitFitting(Station, SuitFittingAction.Start);
            internal InteractionReply Cancel() => Port.OperateSuitFitting(Station, SuitFittingAction.Cancel);
            internal WorkerReply Contact(long sequence) => World.ObserveWorkerContamination(World.Epoch, Actor, Id(95), sequence, Id(100 + (int)sequence), World.View.ElapsedMilliseconds);
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True,
            () => reply.Status + " / " + reply.SuitFitting?.Status);

        [TestCase(WorkerSuit.None, 20)] [TestCase(WorkerSuit.Compromised, 10)]
        public void FittingRetainsOriginalProtectionUntilExactCompletionAndPreservesContamination(WorkerSuit original, int beforeLoad)
        {
            var f = new Setup(); f.World.SetWorkerEnvironment(f.World.Epoch, f.Actor, f.Worker.Revision, original, 0);
            int originalSpeed = original == WorkerSuit.None ? 1000 : 800;
            var beforeFitting = f.Worker; Assert.That(beforeFitting.SuitWalkSpeedPermille, Is.EqualTo(originalSpeed));
            f.Contact(1); Assert.That(f.Worker.Contamination, Is.EqualTo(beforeLoad)); long revision = f.Worker.Revision;
            var started = f.Start(); Applied(started); var attempt = f.Worker.SuitFitting!;
            Assert.That(f.Worker.Revision, Is.EqualTo(revision + 1)); Assert.That(f.Worker.CanInteract, Is.False); Assert.That(f.Worker.PhysicallyUpright, Is.True);
            Assert.That(f.Worker.Suit, Is.EqualTo(original)); Assert.That(attempt.OriginalSuit, Is.EqualTo(original));
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(originalSpeed));
            Assert.That(f.World.AdvanceTo(14999).SuitFittingChanges, Is.Empty); Assert.That(f.Worker.Suit, Is.EqualTo(original));
            var done = f.World.AdvanceTo(15000).SuitFittingChanges.Single();
            Assert.That(done.Kind, Is.EqualTo(SuitFittingEvent.Completed)); Assert.That(done.Attempt.Id, Is.EqualTo(attempt.Id));
            Assert.That(done.ShiftMilliseconds, Is.EqualTo(15000)); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(800)); Assert.That(done.Worker.SuitWalkSpeedPermille, Is.EqualTo(800));
            Assert.That(beforeFitting.SuitWalkSpeedPermille, Is.EqualTo(originalSpeed));
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.Worker.CanInteract, Is.True); Assert.That(f.Worker.Contamination, Is.EqualTo(beforeLoad));
            f.Contact(2); Assert.That(f.Worker.Contamination, Is.EqualTo(beforeLoad + 5));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(Guid.Empty)); Assert.That(f.Worker.LastHazardId, Is.EqualTo(Guid.Empty));
            Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(1)); Assert.That(f.World.AdvanceTo(16000).SuitFittingChanges, Is.Empty);
        }

        [TestCase("grab")] [TestCase("machine")] [TestCase("reactor")] [TestCase("door")] [TestCase("medical")] [TestCase("fitting")]
        public void FittingBusyRejectsIncompatibleWorkWithoutChangingItsTarget(string operation)
        {
            var f = new Setup(); Applied(f.Start()); long revision = f.Worker.Revision;
            var denied = operation switch
            {
                "grab" => f.Port.Grab(Id(30)), "machine" => f.Port.OperateMachine(Id(40), ProductionAction.Start),
                "reactor" => f.Port.OperateReactor(Id(50), ReactorAction.AuxiliaryPower), "door" => f.Port.OperateDoor(Id(70), DoorAction.Open),
                "medical" => f.Port.OperateMedical(Id(60), MedicalAction.Start), _ => f.Start()
            };
            Assert.That(denied.Status, Is.EqualTo(InteractionStatus.ActorUnavailable)); Assert.That(denied.IsTerminal, Is.True);
            Assert.That(f.Worker.Revision, Is.EqualTo(revision)); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.Null);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.World.Doors.Get(Id(70))!.State, Is.EqualTo(DoorState.Closed));
            Assert.That(f.World.Production.Summary.PendingCycles, Is.Zero); Assert.That(f.World.Medical.Summary.UsedCartridges, Is.Zero);
            Applied(f.Cancel()); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.Worker.CanInteract, Is.True);
            Applied(f.Port.Grab(Id(30)));
        }

        [Test] public void FittingRequiresEmptyHandsAndOneWorkerPerStation()
        {
            var f = new Setup(start: false); f.World.SuitFitting.Register(Id(91), new SuitFittingDefinition(15000)); f.World.Start();
            Applied(f.Port.Grab(Id(30))); Assert.That(f.Start().SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.HandsOccupied));
            Assert.That(f.World.SuitFitting.Summary.Started, Is.Zero); Applied(f.Port.Release(Id(30))); Applied(f.Start());
            Assert.That(f.Other.OperateSuitFitting(f.Station, SuitFittingAction.Start).SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.StationOccupied));
            Applied(f.Other.OperateSuitFitting(Id(91), SuitFittingAction.Start));
            var done = f.World.AdvanceTo(15000).SuitFittingChanges;
            Assert.That(done.Count, Is.EqualTo(2)); Assert.That(done.Select(c => c.Worker.Id), Is.EquivalentTo(new[] { f.Actor, Id(11) }));
            Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(2)); Assert.That(f.World.SuitFitting.Summary.Pending, Is.Zero);
        }

        [Test] public void AlreadyIntactWorkerCannotCreateAnotherFittingOrConsumeItsClock()
        {
            var f = new Setup(); f.World.SetWorkerEnvironment(f.World.Epoch, f.Actor, 0, WorkerSuit.Intact, 42); long revision = f.Worker.Revision;
            var result = f.Start(); Assert.That(result.Status, Is.EqualTo(InteractionStatus.NoChange)); Assert.That(result.SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.NoChange));
            Assert.That(f.Worker.Revision, Is.EqualTo(revision)); Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.World.SuitFitting.Summary.Started, Is.Zero);
            Assert.That(f.Worker.Contamination, Is.EqualTo(42));
        }

        [Test] public void HistoricalFittingRetryCannotReopenTheCompletedAttemptOrRepeatItsEvent()
        {
            var f = new Setup(); var feed = new SandboxTraceFeed(f.Port); long before = f.Worker.Revision;
            var first = f.Start(); Applied(first); var attempt = f.Worker.SuitFitting!; feed.Refresh(); f.World.AdvanceTo(15000); feed.Refresh();
            var retry = f.Port.ReplayLast(); feed.Refresh(); Assert.That(retry.IsReplay, Is.True); Assert.That(retry.HasNewCommit, Is.False);
            Assert.That(retry.SuitFitting!.Worker!.SuitFitting!.Id, Is.EqualTo(attempt.Id)); Assert.That(retry.SuitFitting.Worker.Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(retry.SuitFitting.Worker.SuitWalkSpeedPermille, Is.EqualTo(1000)); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(800));
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(f.World.SuitFitting.Summary.Started, Is.EqualTo(1)); Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(1));
            Assert.That(feed.Entries.Count(e => e.Description.Contains("fitting started")), Is.EqualTo(1));
            var changed = new InteractionCommand(f.World.Epoch, 1, InteractionKind.SuitFitting, f.Station,
                suitFitting: new SuitFittingRequest(SuitFittingAction.Start, before + 1));
            Assert.That(f.World.ExecuteInteraction(Id(20), changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
        }

        [Test] public void StaleFittingCancellationCannotStopTheNextFullDurationAttempt()
        {
            var f = new Setup(); Applied(f.Start()); var first = f.Worker.SuitFitting!; f.World.AdvanceTo(1000); Applied(f.Cancel());
            Applied(f.Start()); var current = f.Worker.SuitFitting!; Assert.That(current.Id, Is.Not.EqualTo(first.Id));
            Assert.That(current.DueAtMilliseconds, Is.EqualTo(16000));
            var old = new InteractionCommand(f.World.Epoch, f.Port.LastTerminalSequence + 1, InteractionKind.SuitFitting, f.Station,
                suitFitting: new SuitFittingRequest(SuitFittingAction.Cancel, attempt: first.Id));
            Assert.That(f.World.ExecuteInteraction(Id(20), old).SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.StaleAttempt));
            f.World.AdvanceTo(15000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(current.Id)); f.World.AdvanceTo(16000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(f.World.SuitFitting.Summary.Cancelled, Is.EqualTo(1)); Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(1));
        }

        [Test] public void AnotherAuthenticatedWorkerCannotCancelOrCompleteTheWearersAttempt()
        {
            var f = new Setup(); Applied(f.Start()); var attempt = f.Worker.SuitFitting!;
            var foreign = new InteractionCommand(f.World.Epoch, 1, InteractionKind.SuitFitting, f.Station,
                suitFitting: new SuitFittingRequest(SuitFittingAction.Cancel, attempt: attempt.Id));
            Assert.That(f.World.ExecuteInteraction(Id(21), foreign).SuitFitting!.Status, Is.EqualTo(SuitFittingStatus.StaleAttempt));
            Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(attempt.Id)); Assert.That(f.World.GetWorker(Id(11))!.Suit, Is.EqualTo(WorkerSuit.None));
            f.World.AdvanceTo(15000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
        }

        [Test] public void PauseFreezesFittingAndOwnCancellationRemainsUsableOutOfReach()
        {
            var f = new Setup(); Applied(f.Start()); f.World.AdvanceTo(5000); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(50000);
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.World.View.ElapsedMilliseconds, Is.EqualTo(5000));
            f.Access.Decision = AccessDecision.OutOfReach; int calls = f.Access.Calls; long revision = f.Worker.Revision;
            Applied(f.Cancel()); Assert.That(f.Access.Calls, Is.EqualTo(calls)); Assert.That(f.Worker.Revision, Is.EqualTo(revision + 1));
            Assert.That(f.Worker.CanInteract, Is.True); Assert.That(f.World.SuitFitting.Summary.Cancelled, Is.EqualTo(1));
            f.Access.Decision = AccessDecision.Allowed; f.World.Resume(f.World.Epoch); Applied(f.Start());
            f.World.AdvanceTo(64999); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None));
            f.World.AdvanceTo(65000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
        }

        [TestCase(AccessDecision.OutOfReach)] [TestCase(AccessDecision.ActorUnavailable)] [TestCase(AccessDecision.TargetUnavailable)]
        public void LostCurrentStationAccessInterruptsFittingOnceBeforeProtection(AccessDecision decision)
        {
            var f = new Setup(); Applied(f.Start()); var attempt = f.Worker.SuitFitting!; f.Access.Decision = decision;
            var interrupted = f.World.AdvanceTo(500).SuitFittingChanges.Single();
            Assert.That(interrupted.Kind, Is.EqualTo(SuitFittingEvent.Interrupted)); Assert.That(interrupted.Attempt.Id, Is.EqualTo(attempt.Id));
            Assert.That(interrupted.ShiftMilliseconds, Is.EqualTo(500)); Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.Worker.CanInteract, Is.True);
            f.World.AdvanceTo(15000); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.EqualTo(1));
        }

        [TestCase(false)] [TestCase(true)]
        public void SkippedPollAttributesObservedAccessLossToCurrentTimeRegardlessOfOtherBoundaries(bool backup)
        {
            var f = new Setup(start: false);
            if (backup) f.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(5000, 12, 1));
            f.World.Start(); Applied(f.Start());
            if (backup) Assert.That(f.Other.OperateReactor(Id(50), ReactorAction.StartBackup).HasNewCommit, Is.True);
            f.Access.Decision = AccessDecision.OutOfReach; int before = f.Access.Calls;
            var poll = f.World.AdvanceTo(30000); var interrupted = poll.SuitFittingChanges.Single();
            Assert.That(interrupted.Kind, Is.EqualTo(SuitFittingEvent.Interrupted));
            Assert.That(interrupted.ShiftMilliseconds, Is.EqualTo(30000)); Assert.That(f.Access.Calls, Is.EqualTo(before + 1));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.Worker.SuitFitting, Is.Null);
            Assert.That(f.World.Trace.Records.Single(r => r.SuitFittingChange?.Kind == SuitFittingEvent.Interrupted).OccurredAtMilliseconds, Is.EqualTo(30000));
            if (backup) Assert.That(poll.ReactorChanges.Single().ShiftMilliseconds, Is.EqualTo(5000));
        }

        [Test] public void PausedAccessLossUsesFrozenShiftCoordinateWithoutAdvancingProtection()
        {
            var f = new Setup(); Applied(f.Start()); f.World.AdvanceTo(5000); f.World.Pause(f.World.Epoch);
            f.Access.Decision = AccessDecision.OutOfReach;
            var change = f.World.AdvanceTo(50000).SuitFittingChanges.Single();
            Assert.That(change.ShiftMilliseconds, Is.EqualTo(5000)); Assert.That(f.World.View.ElapsedMilliseconds, Is.EqualTo(5000));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None)); Assert.That(f.Worker.CanInteract, Is.True);
        }

        [Test] public void FittingTraceRetainsEachAcceptedWorkerRevisionAfterTraceEviction()
        {
            var f = new Setup(trace: 8); long initial = f.Worker.Revision;
            Applied(f.Start()); Applied(f.Cancel()); Applied(f.Start()); f.World.AdvanceTo(15000);
            var events = f.World.Trace.Records.Where(r => r.SuitFittingChange != null).ToArray();
            Assert.That(events.Select(r => r.SuitFittingChange!.Kind), Is.EqualTo(new[]
                { SuitFittingEvent.Started, SuitFittingEvent.Cancelled, SuitFittingEvent.Started, SuitFittingEvent.Completed }));
            for (int i = 0; i < events.Length; i++)
            {
                Assert.That(events[i].PreviousWorkerRevision, Is.EqualTo(initial + i));
                Assert.That(events[i].WorkerRevision, Is.EqualTo(initial + i + 1));
            }
            for (int i = 15001; i <= 15020; i++) f.World.AdvanceTo(i);
            Assert.That(f.World.Trace.Records.Any(r => r.SuitFittingChange != null), Is.False);
            f.World.Stop(); var retained = f.World.Debrief!.Timeline.Where(r => r.SuitFittingChange != null).ToArray();
            Assert.That(retained.Select(r => r.Sequence), Is.EqualTo(events.Select(r => r.Sequence)));
            Assert.That(f.World.Debrief.SuitFitting.Started, Is.EqualTo(2));
            Assert.That(f.World.Debrief.SuitFitting.Completed, Is.EqualTo(1)); Assert.That(f.World.Debrief.SuitFitting.Cancelled, Is.EqualTo(1));
        }

        [Test] public void SafeContaminationRevisionsPreserveProgressAndExactCancellationStillWorks()
        {
            var f = new Setup(); Applied(f.Start()); var attempt = f.Worker.SuitFitting!; f.Contact(1);
            f.World.SetWorkerEnvironment(f.World.Epoch, f.Actor, f.Worker.Revision, WorkerSuit.None, 42);
            Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(attempt.Id)); Assert.That(f.Worker.Contamination, Is.EqualTo(42));
            Applied(f.Cancel()); Assert.That(f.Worker.Contamination, Is.EqualTo(42)); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.Zero);
        }

        [TestCase(false)] [TestCase(true)]
        public void ImpactOrTrustedSuitReplacementImmediatelyInterruptsWithoutChangingInjuryAttribution(bool replacement)
        {
            var f = new Setup(); Applied(f.Start()); var attempt = f.Worker.SuitFitting!;
            if (replacement) f.World.SetWorkerEnvironment(f.World.Epoch, f.Actor, f.Worker.Revision, WorkerSuit.Compromised, 42);
            else
            {
                f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Knockdown, 0, Id(100), Id(101));
                Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(101))); Assert.That(f.Worker.LastHazardId, Is.EqualTo(Id(100)));
                Assert.That(f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Knockdown, 0, Id(100), Id(101)).Status, Is.EqualTo(WorkerStatus.Duplicate));
            }
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.EqualTo(1));
            var record = f.World.Trace.Records.Single(r => r.SuitFittingChange?.Kind == SuitFittingEvent.Interrupted);
            Assert.That(record.CycleId, Is.EqualTo(attempt.Id)); Assert.That(record.CauseId, Is.EqualTo(replacement ? attempt.Id : Id(101)));
            Assert.That(record.HazardId, Is.EqualTo(replacement ? Guid.Empty : Id(100))); Assert.That(record.EntityId, Is.EqualTo(f.Station));
            Assert.That(record.WorkerRevision, Is.EqualTo(f.Worker.Revision)); Assert.That(record.PreviousWorkerRevision, Is.EqualTo(f.Worker.Revision - 1));
            Assert.That(record.WorldRevision, Is.EqualTo(f.World.View.Revision)); f.World.AdvanceTo(15000);
            Assert.That(f.Worker.Suit, Is.EqualTo(replacement ? WorkerSuit.Compromised : WorkerSuit.None));
            Assert.That(f.World.SuitFitting.Summary.Completed, Is.Zero);
        }

        [Test] public void FittingPreservesPriorStandingRecoveryAndOriginalImpactHistory()
        {
            var f = new Setup(); f.World.ApplyWorkerImpact(f.World.Epoch, f.Actor, 1, WorkerImpact.Knockdown, 0, Id(100), Id(101));
            var down = f.Worker; Assert.That(f.World.BeginWorkerRecovery(f.World.Epoch, f.Actor, down.RecoveryEpisode, down.Revision).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Actor, f.Worker.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
            var original = f.Worker; Applied(f.Start()); f.Contact(1); f.World.AdvanceTo(15000);
            Assert.That(f.Worker.Awareness, Is.EqualTo(original.Awareness)); Assert.That(f.Worker.Pose, Is.EqualTo(original.Pose));
            Assert.That(f.Worker.RecoveryEpisode, Is.EqualTo(original.RecoveryEpisode)); Assert.That(f.Worker.RecoveryAttempt, Is.EqualTo(original.RecoveryAttempt));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(original.LastCauseId)); Assert.That(f.Worker.LastHazardId, Is.EqualTo(original.LastHazardId));
            Assert.That(f.Worker.Contamination, Is.EqualTo(20)); Assert.That(f.World.View.ActiveClaimCount, Is.Zero);
        }

        [TestCase(14999, false)] [TestCase(15000, true)] [TestCase(15001, true)]
        public void FittingDeadlineSettlesExactDueBeforeFreezingTheCutoffRoster(long deadline, bool complete)
        {
            var f = new Setup(shift: deadline); Applied(f.Start()); var result = f.World.AdvanceTo(100000);
            Assert.That(result.World.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.World.WorkerCount, Is.Zero); Assert.That(f.World.SuitFitting.StationCount, Is.Zero);
            var final = f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == f.Actor);
            Assert.That(final.Suit, Is.EqualTo(complete ? WorkerSuit.Intact : WorkerSuit.None)); Assert.That(final.SuitFitting == null, Is.EqualTo(complete));
            Assert.That(f.World.Debrief.SuitFitting.Completed, Is.EqualTo(complete ? 1 : 0)); Assert.That(f.World.Debrief.SuitFitting.Cancelled, Is.EqualTo(complete ? 0 : 1));
            Assert.That(f.World.Debrief.SuitFitting.Pending, Is.Zero); Assert.That(result.SuitFittingChanges.Count, Is.EqualTo(complete ? 1 : 0));
            if (complete) Assert.That(result.SuitFittingChanges.Single().ShiftMilliseconds, Is.EqualTo(15000));
            var frozen = f.World.Debrief; f.World.AdvanceTo(200000); f.World.Stop(); Assert.That(f.World.Debrief, Is.SameAs(frozen));
        }

        [Test] public void DisconnectAndRestartRetirePendingFittingAndRejectOldEpochIntentions()
        {
            var f = new Setup(); Applied(f.Start()); var epoch = f.World.Epoch; var attempt = f.Worker.SuitFitting!;
            f.World.Disconnect(epoch, Id(20)); Assert.That(f.World.GetWorker(f.Actor), Is.Null); Assert.That(f.World.SuitFitting.Summary.Interrupted, Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Single(r => r.SuitFittingChange?.Kind == SuitFittingEvent.Interrupted).WorldRevision, Is.EqualTo(f.World.View.Revision));
            f.World.AdvanceTo(15000); Assert.That(f.World.SuitFitting.Summary.Completed, Is.Zero); f.World.Stop();
            var successor = f.World.Restart(new TestAccess()); successor.RegisterConnection(Id(20), f.Actor);
            successor.SuitFitting.Register(f.Station, new SuitFittingDefinition(15000)); successor.Start();
            var stale = new InteractionCommand(epoch, 2, InteractionKind.SuitFitting, f.Station,
                suitFitting: new SuitFittingRequest(SuitFittingAction.Cancel, attempt: attempt.Id));
            Assert.That(successor.ExecuteInteraction(Id(20), stale).Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(successor.GetWorker(f.Actor)!.SuitFitting, Is.Null); Assert.That(successor.SuitFitting.Summary.Started, Is.Zero);
        }

        [Test] public void ReentrantStationObservationFaultsWithoutGrantingProtectionOrSuccessfulDeadline()
        {
            var f = new Setup(shift: 15000); Applied(f.Start()); f.Access.Callback = () => f.World.Stop();
            Assert.Throws<InvalidOperationException>(() => f.World.AdvanceTo(15000));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted)); Assert.That(f.World.WorkerCount, Is.Zero);
            Assert.That(f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == f.Actor).Suit, Is.EqualTo(WorkerSuit.None));
            Assert.That(f.World.Debrief.SuitFitting.Cancelled, Is.EqualTo(1)); Assert.That(f.World.Debrief.SuitFitting.Pending, Is.Zero);
            Assert.That(f.World.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended || r.SuitFittingChange?.Kind == SuitFittingEvent.Completed), Is.False);
        }

        [Test] public void CompletionRevisionOverflowDoesNotRepeatCheckedCancellationDuringFaultCleanup()
        {
            var f = new Setup(shift: 15000); Applied(f.Start());
            var workflow = typeof(WorldSession).GetField("_workers", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(f.World)!;
            var states = (Dictionary<Guid, WorkerState>)workflow.GetType().GetField("_workers", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(workflow)!;
            typeof(WorkerState).GetField("_revision", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(states[f.Actor], long.MaxValue);
            Assert.Throws<OverflowException>(() => f.World.AdvanceTo(15000)); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(f.World.WorkerCount, Is.Zero); Assert.That(f.World.SuitFitting.StationCount, Is.Zero); Assert.That(f.World.Debrief!.SuitFitting.Cancelled, Is.EqualTo(1));
            Assert.That(f.World.Debrief.SuitFitting.Completed, Is.Zero); Assert.That(f.World.Debrief.WorkersAtEnd.Single(w => w.Id == f.Actor).Suit, Is.EqualTo(WorkerSuit.None));
        }

        [TestCase("mixed-kind")] [TestCase("mixed-medical")] [TestCase("version")] [TestCase("start-attempt")] [TestCase("cancel-revision")] [TestCase("missing-attempt")]
        public void MalformedFittingPayloadCannotConsumeASequenceOrBypassTheOriginalCommandKind(string variant)
        {
            var f = new Setup(); var request = variant switch
            {
                "version" => new SuitFittingRequest(SuitFittingAction.Start, version: 0),
                "start-attempt" => new SuitFittingRequest(SuitFittingAction.Start, attempt: Id(1)),
                "cancel-revision" => new SuitFittingRequest(SuitFittingAction.Cancel, 1, Id(1)),
                "missing-attempt" => new SuitFittingRequest(SuitFittingAction.Cancel), _ => new SuitFittingRequest(SuitFittingAction.Start)
            };
            var command = new InteractionCommand(f.World.Epoch, 1, variant == "mixed-kind" ? InteractionKind.Grab : InteractionKind.SuitFitting, f.Station,
                medical: variant == "mixed-medical" ? new MedicalRequest(MedicalAction.Start, 0) : null, suitFitting: request);
            var denied = f.World.ExecuteInteraction(Id(20), command); Assert.That(denied.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(denied.IsTerminal, Is.False);
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.World.SuitFitting.Summary.Started, Is.Zero); Applied(f.Start());
        }

        [TestCase(14999)] [TestCase(30001)]
        public void FittingDefinitionsKeepTheAuthoredPreparationWindowBounded(long duration) =>
            Assert.Throws<ArgumentOutOfRangeException>(() => new SuitFittingDefinition(duration));

        [Test] public void CancellationCounterOverflowStillRetiresAllOwnersAndMarksSaturatedTerminalEvidence()
        {
            var f = new Setup(); Applied(f.Start());
            typeof(SuitFittingOperations).GetField("cancelled", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(f.World.SuitFitting, long.MaxValue);
            Assert.Throws<OverflowException>(() => f.Cancel()); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted));
            Assert.That(f.World.WorkerCount, Is.Zero); Assert.That(f.World.View.ConnectedPlayerCount, Is.Zero);
            Assert.That(f.World.View.RegisteredObjectCount, Is.Zero); Assert.That(f.World.View.PendingTimerCount, Is.Zero);
            Assert.That(f.World.SuitFitting.StationCount, Is.Zero); Assert.That(f.World.Production.MachineCount, Is.Zero);
            Assert.That(f.World.Medical.View, Is.Null); Assert.That(f.World.Reactor.View, Is.Null);
            Assert.That(f.World.Debrief!.SuitFitting.Cancelled, Is.EqualTo(long.MaxValue));
            Assert.That(f.World.Debrief.SuitFitting.CountersSaturated, Is.True); Assert.That(f.World.Debrief.SuitFitting.Pending, Is.Zero);
            var final = f.World.Debrief; f.World.Stop(); Assert.That(f.World.Debrief, Is.SameAs(final));
        }
    }
}
