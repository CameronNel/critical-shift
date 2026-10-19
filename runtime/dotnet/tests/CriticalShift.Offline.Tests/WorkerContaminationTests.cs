using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class WorkerContaminationTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Clearance : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => RecoveryClearance.Safe; }
        private sealed class Clinic
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Operator;
            internal Guid Patient => Id(10);
            internal Guid Body => Id(30);
            internal Guid Station => Id(90);
            internal WorkerView Worker => World.GetWorker(Patient)!;
            internal Clinic(int exposure = 100, int wash = 60, int traceCapacity = 32)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, 12000, true), new TestAccess(), new Clearance(), traceCapacity: traceCapacity);
                World.RegisterConnection(Id(20), Patient); World.RegisterWorkerBody(Patient, Body);
                World.RegisterConnection(Id(21), Id(11));
                World.RegisterWorkerContaminationSource(Id(70), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, exposure));
                World.RegisterWorkerContaminationSource(Id(71), new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, wash));
                World.Reactor.Register(Id(80), new ReactorDefinition(Id(81), reserveCapacity: 100, initialReserve: 20));
                World.Medical.Register(Station, new MedicalDefinition());
                Operator = new LocalCommandPort(World, Id(21)); World.Start();
            }
            internal WorkerReply Contact(int source, long sequence = 1, int cause = 200, long? sample = null) =>
                World.ObserveWorkerContamination(World.Epoch, Patient, Id(source), sequence, Id(cause), sample ?? World.View.ElapsedMilliseconds);
            internal void Load()
            {
                World.ApplyWorkerImpact(World.Epoch, Patient, 1, WorkerImpact.Incapacitating, 0, Id(60), Id(61));
                Assert.That(Operator.Grab(Body).HasNewCommit, Is.True);
                Assert.That(Operator.OperateMedical(Station, MedicalAction.Insert, Body).HasNewCommit, Is.True);
            }
        }

        [TestCase(SuitCondition.None, 1, 1)] [TestCase(SuitCondition.Compromised, 1, 1)] [TestCase(SuitCondition.Intact, 1, 1)]
        [TestCase(SuitCondition.None, 5, 5)] [TestCase(SuitCondition.Compromised, 5, 3)] [TestCase(SuitCondition.Intact, 5, 2)]
        [TestCase(SuitCondition.None, 100, 100)] [TestCase(SuitCondition.Compromised, 100, 50)] [TestCase(SuitCondition.Intact, 100, 25)]
        public void AuthoredContactsRespectSuitProtectionAndUpwardDiscreteRounding(SuitCondition suit, int raw, int expected)
        {
            var worker = new WorkerState(Id(10)); worker.SetEnvironment(0, suit, 0);
            var before = worker.Snapshot;
            var reply = worker.ObserveContamination(Id(70), 1, Id(200), new ContaminationRules(ContaminationMode.Exposure, raw), 0, 0);
            Assert.That(reply.Status, Is.EqualTo(WorkerResult.Applied));
            Assert.That(worker.Snapshot.Contamination, Is.EqualTo(expected)); Assert.That(reply.Contact!.EffectiveUnits, Is.EqualTo(expected));
            Assert.That(worker.Snapshot.Suit, Is.EqualTo(suit)); Assert.That(worker.Snapshot.Posture, Is.EqualTo(before.Posture));
            Assert.That(worker.Snapshot.RecoveryEpisode, Is.EqualTo(before.RecoveryEpisode));
        }

        [Test] public void ContactRetryAfterWashingSuitChangeAndTimeAdvanceCannotRecontaminate()
        {
            var f = new Clinic(); var original = f.Contact(70); Assert.That(original.Worker!.Contamination, Is.EqualTo(100));
            f.Contact(71); f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.Intact, 0);
            f.World.AdvanceTo(500); long revision = f.Worker.Revision;
            var replay = f.Contact(70, sample: 0);
            Assert.That(replay.Status, Is.EqualTo(WorkerStatus.Duplicate)); Assert.That(replay.Changed, Is.False);
            Assert.That(replay.ContaminationContact!.Before, Is.Zero); Assert.That(replay.ContaminationContact.After, Is.EqualTo(100));
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.Worker.Revision, Is.EqualTo(revision));
            Assert.That(f.Contact(70, 2, 201).Worker!.Contamination, Is.EqualTo(25));
        }

        [Test] public void ContactCooldownFinalizesSamplesWithoutSlidingTheEligibleDeadline()
        {
            var f = new Clinic(exposure: 10); f.Contact(70); f.World.AdvanceTo(499);
            var early = f.Contact(70, 2, 201);
            Assert.That(early.Status, Is.EqualTo(WorkerStatus.CoolingDown)); Assert.That(early.Changed, Is.False);
            Assert.That(early.ContaminationContact!.NextEligibleAtMilliseconds, Is.EqualTo(500));
            f.World.AdvanceTo(500);
            var replay = f.Contact(70, 2, 201, 499);
            Assert.That(replay.Status, Is.EqualTo(WorkerStatus.Duplicate)); Assert.That(replay.ContaminationContact!.OriginalOutcome, Is.EqualTo(WorkerStatus.CoolingDown));
            Assert.That(f.Contact(70, 3, 202).Status, Is.EqualTo(WorkerStatus.Applied)); Assert.That(f.Worker.Contamination, Is.EqualTo(20));
        }

        [Test] public void CleanAndSaturatedContactsProgressReceiptsWithoutMutatingCondition()
        {
            var f = new Clinic(); var clean = f.Contact(71);
            Assert.That(clean.Status, Is.EqualTo(WorkerStatus.NoChange)); Assert.That(clean.Changed, Is.False);
            Assert.That(f.Contact(71).Status, Is.EqualTo(WorkerStatus.Duplicate));
            f.Contact(70); f.World.AdvanceTo(500); long revision = f.Worker.Revision;
            Assert.That(f.Contact(70, 2, 201).Status, Is.EqualTo(WorkerStatus.NoChange));
            Assert.That(f.Worker.Revision, Is.EqualTo(revision)); f.World.AdvanceTo(1000);
            Assert.That(f.Contact(70, 3, 202).Status, Is.EqualTo(WorkerStatus.NoChange));
            Assert.That(f.Contact(71, 2, 203).Worker!.Contamination, Is.EqualTo(40));
        }

        [Test] public void ContactIdentityRejectsChangedCauseTimeRulesOldSequenceAndGaps()
        {
            var worker = new WorkerState(Id(10)); var rules = new ContaminationRules(ContaminationMode.Exposure, 10);
            worker.ObserveContamination(Id(70), 1, Id(200), rules, 0, 0);
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(201), rules, 0, 0).Status, Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), rules, 1, 1).Status, Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), new ContaminationRules(ContaminationMode.Decontamination, 10), 0, 0).Status, Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), new ContaminationRules(ContaminationMode.Exposure, 11), 0, 0).Status, Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), new ContaminationRules(ContaminationMode.Exposure, 10, 501), 0, 0).Status, Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(worker.ObserveContamination(Id(70), 3, Id(200), rules, 500, 500).Status, Is.EqualTo(WorkerResult.SequenceGap));
            Assert.That(worker.ObserveContamination(Id(70), 2, Id(201), rules, 500, 500).Status, Is.EqualTo(WorkerResult.Applied));
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), rules, 0, 500).Status, Is.EqualTo(WorkerResult.TooOld));
            Assert.That(worker.Snapshot.Contamination, Is.EqualTo(20));
        }

        [TestCase(-1)] [TestCase(1)]
        public void NewContactRequiresTheCurrentShiftCoordinateAndDoesNotConsumeARejectedSequence(long sample)
        {
            var f = new Clinic(); var reply = f.Contact(70, sample: sample);
            Assert.That(reply.Status, Is.EqualTo(sample < 0 ? WorkerStatus.InvalidInput : WorkerStatus.StaleObservation));
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.Applied));
        }

        [Test] public void ContactAdmissionKeepsEpochPauseUnknownSourceAndTerminalGates()
        {
            var f = new Clinic();
            Assert.That(f.World.ObserveWorkerContamination(Guid.NewGuid(), f.Patient, Id(70), 1, Id(200), 0).Status, Is.EqualTo(WorkerStatus.WrongEpoch));
            Assert.That(f.Contact(72).Status, Is.EqualTo(WorkerStatus.UnknownSource));
            f.World.Pause(f.World.Epoch); Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.Paused));
            f.World.AdvanceTo(1000); f.World.Resume(f.World.Epoch);
            Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.Applied));
            f.World.AdvanceTo(13000);
            Assert.That(f.Contact(70, 2, 201).Status, Is.EqualTo(WorkerStatus.WorldEnded));
        }

        [Test] public void SourceBudgetsAreBoundedAndIndependentOfImpactStreams()
        {
            var worker = new WorkerState(Id(10)); var rules = new ContaminationRules(ContaminationMode.Exposure, 1);
            for (int i = 0; i < WorkerState.ContaminationSourceCapacity; i++)
                Assert.That(worker.ObserveContamination(Id(100 + i), 1, Id(200), rules, 0, 0).Status, Is.EqualTo(WorkerResult.Applied));
            Assert.That(worker.ObserveContamination(Id(500), 1, Id(200), rules, 0, 0).Status, Is.EqualTo(WorkerResult.SourceCapacityReached));
            Assert.That(worker.Impact(1, ImpactSeverity.Knockdown, 0, 0, Id(100), Id(300)), Is.EqualTo(WorkerResult.Applied));
            Assert.That(worker.Snapshot.Contamination, Is.EqualTo(32));
        }

        [Test] public void ContaminationSetupIsBoundedUniqueAndSetupOnly()
        {
            var world = new WorldSession(new WorldSessionConfiguration(42, 12000), new TestAccess()); world.RegisterConnection(Id(20), Id(10));
            var rules = new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 1);
            for (int i = 0; i < 32; i++) world.RegisterWorkerContaminationSource(Id(100 + i), rules);
            Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerContaminationSource(Id(500), rules));
            Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerContaminationSource(Id(100), rules));
            world.Start(); Assert.Throws<InvalidOperationException>(() => world.RegisterWorkerContaminationSource(Id(501), rules));
        }

        [TestCase(0, 500)] [TestCase(101, 500)] [TestCase(1, 0)] [TestCase(1, 60001)]
        public void InvalidContactDefinitionsFailExplicitly(int units, long cooldown) =>
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, units, cooldown));

        [Test] public void WashingPreservesSlottedIncapacitatedPatientsAndOriginalInjuryAttribution()
        {
            var f = new Clinic(); f.Load(); var before = f.Worker; var claim = f.World.GetObject(f.Body)!;
            f.Contact(70); var washed = f.Contact(71);
            Assert.That(washed.Worker!.Contamination, Is.EqualTo(40)); Assert.That(f.Worker.Awareness, Is.EqualTo(before.Awareness));
            Assert.That(f.Worker.Pose, Is.EqualTo(before.Pose)); Assert.That(f.Worker.RecoveryEpisode, Is.EqualTo(before.RecoveryEpisode));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(61))); Assert.That(f.Worker.LastHazardId, Is.EqualTo(Id(60)));
            Assert.That(f.World.GetObject(f.Body)!.Revision, Is.EqualTo(claim.Revision)); Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station));
        }

        [TestCase(false)] [TestCase(true)]
        public void UnsafeContactOrAbsoluteEnvironmentInterruptsBeforeWashingCanHideTheExcursion(bool absolute)
        {
            var f = new Clinic(wash: 100); f.Load(); var cycle = f.Operator.OperateMedical(f.Station, MedicalAction.Start).Medical!.Change!;
            var unsafeChange = absolute ? f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.None, 100) : f.Contact(70);
            Assert.That(unsafeChange.MedicalChange!.Kind, Is.EqualTo(MedicalEvent.Interrupted));
            Assert.That(unsafeChange.MedicalChange.InjuryCauseId, Is.EqualTo(Id(61))); Assert.That(unsafeChange.MedicalChange.CycleId, Is.EqualTo(cycle.CycleId));
            var interrupted = f.World.Trace.Records.Single(r => r.MedicalChange?.Kind == MedicalEvent.Interrupted);
            Assert.That(interrupted.EntityId, Is.EqualTo(f.Station)); Assert.That(interrupted.WorldRevision, Is.EqualTo(f.World.View.Revision));
            Assert.That(interrupted.CycleId, Is.EqualTo(cycle.CycleId));
            Assert.That(interrupted.CauseId, Is.EqualTo(absolute ? Id(61) : Id(200)));
            f.Contact(71); Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Interrupted));
            Assert.That(f.World.AdvanceTo(3000).MedicalChanges.Count, Is.Zero); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Start).HasNewCommit, Is.True);
            f.World.AdvanceTo(6000); Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(12));
        }

        [TestCase(2999, false)] [TestCase(3000, true)]
        public void ContactOrderingCannotRetroactivelyCancelACompletedTreatment(long contactTime, bool completed)
        {
            var f = new Clinic(); f.Load(); f.Operator.OperateMedical(f.Station, MedicalAction.Start); f.World.AdvanceTo(contactTime);
            var reply = f.Contact(70); Assert.That(reply.MedicalChange != null, Is.EqualTo(!completed));
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(completed ? 1 : 0));
            Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(completed ? 0 : 1));
            Assert.That(f.Worker.Awareness, Is.EqualTo(completed ? WorkerAwareness.Alert : WorkerAwareness.Unconscious));
        }

        [Test] public void DecontaminationEnablesPaidStabilizationThenSeparateStandingRecovery()
        {
            var f = new Clinic(); f.Load(); f.Contact(70);
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Start).Medical!.Status, Is.EqualTo(MedicalStatus.Contaminated));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); f.Contact(71);
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Start).HasNewCommit, Is.True); f.World.AdvanceTo(3000);
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Eject).HasNewCommit, Is.True); f.World.AdvanceTo(3500);
            var begin = f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Patient, begin.Worker!.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.Worker.CanInteract, Is.True); Assert.That(f.Worker.Contamination, Is.EqualTo(40));
        }

        [Test] public void ContactCausalitySurvivesRawTraceEvictionWithoutReplacingTheInjuryCause()
        {
            var f = new Clinic(traceCapacity: 2); f.Contact(70); f.Contact(71, cause: 201);
            for (int i = 0; i < 20; i++) f.Contact(71, cause: 201);
            f.World.Stop(); var contacts = f.World.Debrief!.Timeline.Where(r => r.ContaminationContact != null).ToArray();
            Assert.That(contacts.Length, Is.EqualTo(1)); // The bounded two-row journal retains the latest contact plus Stop.
            Assert.That(contacts[0].CauseId, Is.EqualTo(Id(201))); Assert.That(contacts[0].HazardId, Is.EqualTo(Id(71)));
            Assert.That(contacts[0].ContaminationContact!.Before, Is.EqualTo(100)); Assert.That(contacts[0].ContaminationContact!.After, Is.EqualTo(40));
            Assert.That(f.World.Debrief.WorkersAtEnd.Single(w => w.Id == f.Patient).LastCauseId, Is.EqualTo(Guid.Empty));
        }

        [Test] public void OverflowingContactRevisionOrCooldownCannotConsumeTheObservation()
        {
            var worker = new WorkerState(Id(10)); var rules = new ContaminationRules(ContaminationMode.Exposure, 1);
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), rules, long.MaxValue, long.MaxValue).Status, Is.EqualTo(WorkerResult.InvalidInput));
            typeof(WorkerState).GetField("_revision", BindingFlags.NonPublic | BindingFlags.Instance)!.SetValue(worker, long.MaxValue);
            Assert.Throws<OverflowException>(() => worker.ObserveContamination(Id(70), 1, Id(200), rules, 0, 0));
            Assert.That(worker.Snapshot.Contamination, Is.Zero);
            typeof(WorkerState).GetField("_revision", BindingFlags.NonPublic | BindingFlags.Instance)!.SetValue(worker, 0L);
            Assert.That(worker.ObserveContamination(Id(70), 1, Id(200), rules, 0, 0).Status, Is.EqualTo(WorkerResult.Applied));
        }

        [Test] public void ContactReadoutProjectsExposureAndWashingOnceWithTheirActualCauses()
        {
            var f = new Clinic(); var feed = new SandboxTraceFeed(f.Operator);
            f.Contact(70); f.Contact(71, cause: 201);
            for (int i = 0; i < 10; i++) f.Contact(71, cause: 201);
            feed.Refresh(); var rows = feed.Entries.Where(e => e.Kind == SessionTraceKind.Contamination).ToArray();
            Assert.That(rows.Length, Is.EqualTo(2)); Assert.That(rows[0].Description, Does.Contain("exposure"));
            Assert.That(rows[1].Description, Does.Contain("Decontamination")); Assert.That(rows[1].CauseId, Is.EqualTo(Id(201)));
            Assert.That(rows[1].HazardId, Is.EqualTo(Id(71))); Assert.That(rows[1].ActorId, Is.EqualTo(f.Patient));
            f.World.Stop(); Assert.That(SandboxTraceFeed.DebriefEntries(f.World.Debrief!).Count(e => e.Kind == SessionTraceKind.Contamination), Is.EqualTo(2));
        }

        [TestCase(-1)] [TestCase(1)]
        public void NewNonnegativePastOrFutureSamplesCannotBackdateAContact(long offset)
        {
            var f = new Clinic(); f.World.AdvanceTo(100);
            Assert.That(f.Contact(70, sample: 100 + offset).Status, Is.EqualTo(WorkerStatus.StaleObservation));
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.Applied));
        }

        [TestCase("zero-sequence")] [TestCase("max-sequence")] [TestCase("missing-cause")]
        public void MalformedContactSamplesCannotMutateConditionOrConsumeTheFirstReceipt(string variant)
        {
            var f = new Clinic(); long sequence = variant == "zero-sequence" ? 0 : variant == "max-sequence" ? long.MaxValue : 1;
            var reply = f.World.ObserveWorkerContamination(f.World.Epoch, f.Patient, Id(70), sequence,
                variant == "missing-cause" ? Guid.Empty : Id(200), 0);
            Assert.That(reply.Status, Is.EqualTo(WorkerStatus.InvalidInput)); Assert.That(reply.Changed, Is.False);
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.Worker.Revision, Is.Zero);
            Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.Applied));
        }

        [Test] public void WorkersSharingOneSourceHaveIndependentSequencesAndCooldowns()
        {
            var f = new Clinic(exposure: 10); f.Contact(70);
            var other = f.World.ObserveWorkerContamination(f.World.Epoch, Id(11), Id(70), 1, Id(200), 0);
            Assert.That(other.Status, Is.EqualTo(WorkerStatus.Applied)); Assert.That(other.Worker!.Contamination, Is.EqualTo(10));
            Assert.That(f.Contact(70, 2, 201).Status, Is.EqualTo(WorkerStatus.CoolingDown));
            Assert.That(f.World.ObserveWorkerContamination(f.World.Epoch, Id(11), Id(70), 2, Id(201), 0).Status, Is.EqualTo(WorkerStatus.CoolingDown));
            f.World.AdvanceTo(500);
            Assert.That(f.Contact(70, 3, 202).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.World.ObserveWorkerContamination(f.World.Epoch, Id(11), Id(70), 3, Id(202), 500).Worker!.Contamination, Is.EqualTo(20));
        }

        [Test] public void DisconnectAndRestartRetireReceiptsAndOldEpochCannotContaminateTheSuccessor()
        {
            var f = new Clinic(); f.Contact(70); var epoch = f.World.Epoch; var old = f.Worker;
            f.World.Disconnect(epoch, Id(20)); Assert.That(f.Contact(70).Status, Is.EqualTo(WorkerStatus.UnknownWorker));
            f.World.Stop(); var next = f.World.Restart(new TestAccess());
            next.RegisterConnection(Id(20), f.Patient);
            next.RegisterWorkerContaminationSource(Id(70), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 10)); next.Start();
            Assert.That(next.ObserveWorkerContamination(epoch, f.Patient, Id(70), 1, Id(200), 0).Status, Is.EqualTo(WorkerStatus.WrongEpoch));
            Assert.That(next.ObserveWorkerContamination(next.Epoch, f.Patient, Id(70), 1, Id(200), 0).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(next.GetWorker(f.Patient)!.Contamination, Is.EqualTo(10)); Assert.That(old.Contamination, Is.EqualTo(100));
        }

        [Test] public void SafeContactsPreserveAPendingStandingAttemptAndItsClearanceProtocol()
        {
            var f = new Clinic(exposure: 10);
            f.World.ApplyWorkerImpact(f.World.Epoch, f.Patient, 1, WorkerImpact.Knockdown, 0, Id(60), Id(61));
            var begin = f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision).Worker!;
            f.Contact(70); f.Contact(71);
            Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Recovering)); Assert.That(f.Worker.RecoveryAttempt, Is.EqualTo(begin.RecoveryAttempt));
            Assert.That(f.Worker.RecoveryExpiresAtMilliseconds, Is.EqualTo(begin.RecoveryExpiresAtMilliseconds));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(61)));
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Patient, begin.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
        }
    }
}
