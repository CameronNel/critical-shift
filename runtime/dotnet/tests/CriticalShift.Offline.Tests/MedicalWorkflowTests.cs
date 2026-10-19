using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class MedicalWorkflowTests
    {
        private sealed class Clearance : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => RecoveryClearance.Safe; }
        private sealed class Clinic
        {
            internal WorldSession World { get; }
            internal LocalCommandPort Operator { get; }
            internal LocalCommandPort Other { get; }
            internal LocalCommandPort PatientCommands { get; }
            internal Guid Patient => Fixture.Id(10);
            internal Guid Body => Fixture.Id(30);
            internal Guid Station => Fixture.Id(90);
            internal Clinic(long duration = 3000, long shift = 12000, long reserve = 10, int cartridges = 2,
                IInteractionAccessPolicy? access = null, bool start = true)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true, receiptCapacity: 2), access ?? new TestAccess(), new Clearance());
                World.RegisterConnection(Fixture.Id(20), Patient); World.RegisterWorkerBody(Patient, Body);
                World.RegisterConnection(Fixture.Id(21), Fixture.Id(11)); World.RegisterWorkerBody(Fixture.Id(11), Fixture.Id(31));
                World.RegisterConnection(Fixture.Id(22), Fixture.Id(12));
                World.RegisterWorkerBody(Fixture.Id(12), Fixture.Id(33));
                World.Reactor.Register(Fixture.Id(80), new ReactorDefinition(Fixture.Id(81), reserveCapacity: 100, initialReserve: reserve));
                World.Production.RegisterBatch(Fixture.Id(32), Fixture.Id(52), Fixture.Id(53), Fixture.Id(54), MaterialKind.Fuel, 100);
                World.Medical.Register(Station, new MedicalDefinition(duration, cartridges: cartridges));
                Operator = new LocalCommandPort(World, Fixture.Id(21)); Other = new LocalCommandPort(World, Fixture.Id(22));
                PatientCommands = new LocalCommandPort(World, Fixture.Id(20));
                if (start) World.Start();
            }
            internal void Hit(long sequence = 1, int cause = 60) =>
                Assert.That(World.ApplyWorkerImpact(World.Epoch, Patient, sequence, WorkerImpact.Incapacitating, 0, Fixture.Id(70), Fixture.Id(cause)).Status, Is.EqualTo(WorkerStatus.Applied));
            internal void Load()
            { Hit(); Assert.That(Operator.Grab(Body).HasNewCommit, Is.True); Assert.That(Operator.OperateMedical(Station, MedicalAction.Insert, Body).HasNewCommit, Is.True); }
            internal InteractionReply Start() => Operator.OperateMedical(Station, MedicalAction.Start);
            internal WorkerView Worker => World.GetWorker(Patient)!;
        }

        [Test] public void MedicalCycleSpendsOnceAndRequiresEjectionBeforeSeparateStandingRecovery()
        {
            var f = new Clinic(); f.Load(); var loaded = f.World.Medical.View!;
            var begin = f.Start(); Assert.That(begin.Medical!.Status, Is.EqualTo(MedicalStatus.Applied));
            Assert.That(f.World.Reactor.PowerSummary!.Available, Is.EqualTo(4)); Assert.That(f.World.Medical.View!.Cartridges, Is.EqualTo(1));
            for (int i = 0; i < 20; i++) Assert.That(f.Operator.ReplayLast().IsReplay, Is.True);
            f.World.AdvanceTo(2999); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            var advance = f.World.AdvanceTo(3000); Assert.That(advance.MedicalChanges.Single().ShiftMilliseconds, Is.EqualTo(3000));
            Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert)); Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Ready));
            Assert.That(f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision).Status, Is.EqualTo(WorkerStatus.BodySlotted));
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Eject).HasNewCommit, Is.True);
            Assert.That(f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision).Status, Is.EqualTo(WorkerStatus.TooEarly));
            f.World.AdvanceTo(3500);
            var recovery = f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Patient, recovery.Worker!.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.Worker.CanInteract, Is.True); Assert.That(loaded.Cartridges, Is.EqualTo(2));
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(6));
        }

        [Test] public void InsufficientReserveAndStalePatientRejectBeforeStockOrPowerMutation()
        {
            var f = new Clinic(reserve: 5); f.Load(); long revision = f.World.Medical.View!.Revision;
            Assert.That(f.Start().Medical!.Status, Is.EqualTo(MedicalStatus.InsufficientReserve));
            Assert.That(f.World.Medical.View.Revision, Is.EqualTo(revision)); Assert.That(f.World.Medical.View.Cartridges, Is.EqualTo(2));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
            var g = new Clinic(); g.Load(); var old = g.Worker;
            g.World.SetWorkerEnvironment(g.World.Epoch, g.Patient, old.Revision, WorkerSuit.Intact, 10);
            var stale = new InteractionCommand(g.World.Epoch, 3, InteractionKind.Medical, g.Station,
                medical: new MedicalRequest(MedicalAction.Start, 1, patientRevision: old.Revision));
            Assert.That(g.World.ExecuteInteraction(Fixture.Id(21), stale).Medical!.Status, Is.EqualTo(MedicalStatus.RevisionConflict));
            Assert.That(g.World.Medical.View!.Cartridges, Is.EqualTo(2)); Assert.That(g.World.Reactor.PowerSummary!.Spent, Is.Zero);
        }

        [Test] public void MedicalAndEmergencyCoolingCompeteForTheSameReserve()
        {
            var f = new Clinic(); f.Operator.Grab(Fixture.Id(32)); f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.Insert, Fixture.Id(32));
            f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.SetCooling, cooling: true);
            f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.Start); f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.SetCooling);
            f.Load(); Assert.That(f.Start().HasNewCommit, Is.True);
            Assert.That(f.World.Reactor.PowerSummary!.Available, Is.EqualTo(1));
            Assert.That(f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.EmergencyCooling).Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientReserve));
            Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(9));
        }

        [Test] public void TwoOperatorsCannotPayForOrStartTheSameCycleTwice()
        {
            var f = new Clinic(reserve: 20); f.Load(); var patient = f.Worker;
            var competing = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Medical, f.Station,
                medical: new MedicalRequest(MedicalAction.Start, 1, patientRevision: patient.Revision));
            Assert.That(f.Start().HasNewCommit, Is.True);
            Assert.That(f.World.ExecuteInteraction(Fixture.Id(22), competing).Medical!.Status, Is.EqualTo(MedicalStatus.RevisionConflict));
            Assert.That(f.World.Medical.View!.Cartridges, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
        }

        [Test] public void PauseFreezesTreatmentAndResumeDoesNotCatchUp()
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.AdvanceTo(1000); f.World.Pause(f.World.Epoch);
            f.World.AdvanceTo(20000); Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Treating));
            Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(21999); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            f.World.AdvanceTo(22000); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert));
        }

        [TestCase(2999, false)] [TestCase(3000, true)] [TestCase(3001, true)]
        public void CappedDeadlineSettlesOnlyTreatmentsDueByTheCutoff(long shift, bool completed)
        {
            var f = new Clinic(shift: shift); f.Load(); f.Start(); var result = f.World.AdvanceTo(long.MaxValue);
            Assert.That(result.World.ElapsedMilliseconds, Is.EqualTo(shift));
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(completed ? 1 : 0));
            Assert.That(f.World.Medical.Summary.CancelledCycles, Is.EqualTo(completed ? 0 : 1));
            var patient = f.World.Debrief!.WorkersAtEnd.Single(w => w.Id == f.Patient);
            Assert.That(patient.Awareness, Is.EqualTo(completed ? WorkerAwareness.Alert : WorkerAwareness.Unconscious));
            Assert.That(f.World.Medical.View, Is.Null); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
        }

        [Test] public void NewInjuryEpisodeInterruptsOnceWithoutRefundOrRewritingOriginalCause()
        {
            var f = new Clinic(); f.Load(); var start = f.Start().Medical!.Change!;
            f.World.AdvanceTo(1000); f.Hit(2, 61); var advance = f.World.AdvanceTo(2000);
            var change = advance.MedicalChanges.Single(); Assert.That(change.Kind, Is.EqualTo(MedicalEvent.Interrupted));
            Assert.That(change.InjuryCauseId, Is.EqualTo(Fixture.Id(60))); Assert.That(change.CycleId, Is.EqualTo(start.CycleId));
            Assert.That(f.World.AdvanceTo(4000).MedicalChanges.Count, Is.Zero);
            Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(1)); Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(1));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6)); Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station));
        }

        [Test] public void SuitAndSafeContaminationChangesSurviveStabilization()
        {
            var f = new Clinic(); f.Load(); f.Start();
            Assert.That(f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.Compromised, 30).Changed, Is.True);
            f.World.AdvanceTo(3000); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert));
            Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Compromised)); Assert.That(f.Worker.Contamination, Is.EqualTo(30));
        }

        [Test] public void ContaminationAboveTheAuthoredLimitRejectsOrInterruptsWithoutHealing()
        {
            var f = new Clinic(); f.Load(); f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.None, 51);
            Assert.That(f.Start().Medical!.Status, Is.EqualTo(MedicalStatus.Contaminated)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
            f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.None, 50); Assert.That(f.Start().HasNewCommit, Is.True);
            f.World.SetWorkerEnvironment(f.World.Epoch, f.Patient, f.Worker.Revision, WorkerSuit.Intact, 51); f.World.AdvanceTo(3000);
            Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious)); Assert.That(f.Worker.Contamination, Is.EqualTo(51));
            Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(1));
        }

        [Test] public void CancellationKeepsCostsAndBodyAndASecondCycleUsesAnotherCartridge()
        {
            var f = new Clinic(reserve: 20); f.Load(); var first = f.Start().Medical!.Change!;
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Eject).Medical!.Status, Is.EqualTo(MedicalStatus.InvalidState));
            Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Cancel).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
            var second = f.Start().Medical!.Change!; Assert.That(second.CycleId, Is.Not.EqualTo(first.CycleId));
            Assert.That(f.World.Medical.View!.Cartridges, Is.Zero); f.World.AdvanceTo(3000);
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(1)); Assert.That(f.World.Medical.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.World.Reactor.PowerSummary.Spent, Is.EqualTo(12));
        }

        [Test] public void PatientDisconnectCancelsAndEjectsBeforeRetirementWithoutFaultingPeers()
        {
            var f = new Clinic(); f.Load(); var cycle = f.Start().Medical!.Change!.CycleId;
            f.World.Disconnect(f.World.Epoch, Fixture.Id(20));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(f.World.GetWorker(f.Patient), Is.Null);
            Assert.That(f.World.GetObject(f.Body)!.IsRetired, Is.True); Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null);
            Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Empty)); Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(1));
            Assert.That(f.World.GetWorker(Fixture.Id(11)), Is.Not.Null); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
            Assert.That(f.World.Trace.Records.Single(r => r.MedicalChange?.Kind == MedicalEvent.PatientDisconnected).CycleId, Is.EqualTo(cycle));
            Assert.That(f.World.Trace.Records.Single(r => r.MedicalChange?.Kind == MedicalEvent.PatientDisconnected).WorldRevision, Is.EqualTo(f.World.View.Revision));
            Assert.That(f.World.Trace.Records.Last(r => r.Kind == SessionTraceKind.Disconnected).WorldRevision, Is.EqualTo(f.World.View.Revision));
            f.World.AdvanceTo(4000); Assert.That(f.World.Medical.Summary.CompletedCycles, Is.Zero);
        }

        [TestCase(false)] [TestCase(true)] public void LoadedAndReadyPatientDisconnectsReleaseChamber(bool ready)
        {
            var f = new Clinic(); f.Load(); if (ready) { f.Start(); f.World.AdvanceTo(3000); }
            f.World.Disconnect(f.World.Epoch, Fixture.Id(20)); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Running));
            Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Empty)); Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.Zero);
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(ready ? 1 : 0));
        }

        [Test] public void OperatorDisconnectDoesNotCancelAnAlreadyCommittedAutonomousCycle()
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.Disconnect(f.World.Epoch, Fixture.Id(21));
            f.World.AdvanceTo(3000); Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert));
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(1));
        }

        [Test] public void InvalidPatientInsertionPreservesTheHeldBody()
        {
            var f = new Clinic(); f.World.ApplyWorkerImpact(f.World.Epoch, f.Patient, 1, WorkerImpact.Knockdown, 0, Fixture.Id(70), Fixture.Id(60));
            f.Operator.Grab(f.Body); Assert.That(f.Operator.OperateMedical(f.Station, MedicalAction.Insert, f.Body).Medical!.Status, Is.EqualTo(MedicalStatus.InvalidPatient));
            Assert.That(f.World.GetObject(f.Body)!.HolderId, Is.EqualTo(Fixture.Id(11)));
            Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Empty)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
        }

        [Test] public void OverflowingCycleDeadlineIsAResourceNeutralGameplayRejection()
        {
            var f = new Clinic(shift: long.MaxValue); f.Load(); f.World.AdvanceTo(long.MaxValue - 2000);
            Assert.That(f.Start().Medical!.Status, Is.EqualTo(MedicalStatus.InvalidTime));
            Assert.That(f.World.Medical.View!.Cartridges, Is.EqualTo(2)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
        }

        [Test] public void MedicalRegistrationIsSetupOnlyAndSnapshotsStayDetachedAcrossRestart()
        {
            var f = new Clinic(); Assert.Throws<InvalidOperationException>(() => f.World.Medical.Register(Fixture.Id(91), new MedicalDefinition()));
            f.Load(); f.Start(); f.World.AdvanceTo(3000); var old = f.World.Medical.View!; f.World.Stop(); var final = f.World.Medical.Summary;
            Assert.That(f.World.Debrief!.Medical, Is.SameAs(final)); Assert.That(f.World.Medical.Summary, Is.SameAs(final));
            var successor = f.World.Restart(new TestAccess()); Assert.That(successor.Medical.View, Is.Null);
            successor.Medical.Register(f.Station, new MedicalDefinition()); Assert.That(successor.Medical.View!.Cartridges, Is.EqualTo(2));
            Assert.That(successor.Medical.View.Epoch, Is.Not.EqualTo(old.Epoch)); Assert.That(old.Cartridges, Is.EqualTo(1));
        }

        [Test] public void ImmutableStationRulesKeepCancellationAndOverflowNonDestructive()
        {
            var empty = new MedicalStationState(Fixture.Id(90), new MedicalRules(3000, 6, 2));
            var loaded = empty.Load(Fixture.Id(30), Fixture.Id(10));
            Assert.Throws<ArgumentOutOfRangeException>(() => loaded.Begin(Fixture.Id(100), 1, 1, long.MaxValue - 2000));
            Assert.That(loaded.Cartridges, Is.EqualTo(2)); var treating = loaded.Begin(Fixture.Id(100), 1, 1, 1000);
            Assert.Throws<InvalidOperationException>(() => treating.Complete(3999)); Assert.Throws<InvalidOperationException>(() => treating.Eject());
            var interrupted = treating.Interrupt(); Assert.That(interrupted.CycleId, Is.EqualTo(treating.CycleId)); Assert.That(interrupted.Cartridges, Is.EqualTo(1));
            Assert.Throws<ArgumentOutOfRangeException>(() => interrupted.Begin(Fixture.Id(101), 1, 1, 999));
            var retry = interrupted.Begin(Fixture.Id(101), 1, 1, 2000); Assert.That(retry.Cartridges, Is.Zero);
            Assert.That(retry.Complete(5000).Eject().Cartridges, Is.Zero); Assert.That(empty.Mode, Is.EqualTo(MedicalMode.Empty));
        }

        [TestCase("missing")] [TestCase("version")] [TestCase("action")] [TestCase("header")]
        [TestCase("mixed")] [TestCase("lease")] [TestCase("patient")] [TestCase("station")]
        [TestCase("cancel")] [TestCase("eject")] [TestCase("egress-start")] [TestCase("medical-egress")]
        public void MalformedMedicalPayloadDoesNotConsumeTheNextSequenceOrResources(string variant)
        {
            var f = new Clinic(); f.Load(); var request = new MedicalRequest(MedicalAction.Start, 1, patientRevision: 1);
            switch (variant)
            {
                case "missing": request = null!; break;
                case "version": request = new MedicalRequest(MedicalAction.Start, 1, patientRevision: 1, version: 2); break;
                case "action": request = new MedicalRequest((MedicalAction)999, 1); break;
                case "lease": request = new MedicalRequest(MedicalAction.Start, 1, leaseGeneration: 1, patientRevision: 1); break;
                case "patient": request = new MedicalRequest(MedicalAction.Start, 1, patientRevision: -1); break;
                case "station": request = new MedicalRequest(MedicalAction.Start, -1, patientRevision: 1); break;
                case "cancel": request = new MedicalRequest(MedicalAction.Cancel, 1, objectRevision: 1); break;
                case "eject": request = new MedicalRequest(MedicalAction.Eject, 1, patientRevision: 1); break;
                case "medical-egress": request = new MedicalRequest(MedicalAction.EmergencyEject, 1); break;
            }
            long revision = f.World.View.Revision;
            var invalid = new InteractionCommand(f.World.Epoch, 3, variant == "egress-start" ? InteractionKind.MedicalEgress : InteractionKind.Medical, f.Station,
                expectedRevision: variant == "header" ? 1 : 0,
                reactor: variant == "mixed" ? new ReactorRequest(ReactorAction.Start, 0) : null, medical: request);
            var reply = f.World.ExecuteInteraction(Fixture.Id(21), invalid);
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(reply.IsTerminal, Is.False);
            Assert.That(f.World.View.Revision, Is.EqualTo(revision)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
            Assert.That(f.World.Medical.View!.Cartridges, Is.EqualTo(2)); Assert.That(f.Start().HasNewCommit, Is.True);
        }

        [Test] public void EvictedOrChangedMedicalRetriesCannotChargeOrStartAnotherCycle()
        {
            var f = new Clinic(); f.Load(); var original = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Medical, f.Station,
                medical: new MedicalRequest(MedicalAction.Start, 1, patientRevision: 1));
            f.Start();
            var changed = new InteractionCommand(f.World.Epoch, 3, InteractionKind.Medical, f.Station,
                medical: new MedicalRequest(MedicalAction.Start, 1, patientRevision: 2));
            Assert.That(f.World.ExecuteInteraction(Fixture.Id(21), changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
            f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.AuxiliaryPower);
            f.Operator.OperateReactor(Fixture.Id(80), ReactorAction.AuxiliaryPower);
            Assert.That(f.World.ExecuteInteraction(Fixture.Id(21), original).Status, Is.EqualTo(InteractionStatus.TooOld));
            Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
        }

        [Test] public void MedicalAccessDenialPreservesResourcesAndDoesNotWedgeTheNextIntent()
        {
            var access = new TestAccess(); var f = new Clinic(access: access); f.Load(); access.Decision = AccessDecision.OutOfReach;
            Assert.That(f.Start().Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(f.World.Medical.View!.Cartridges, Is.EqualTo(2)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
            access.Decision = AccessDecision.Allowed; Assert.That(f.Start().HasNewCommit, Is.True);
        }

        [TestCase(false)] [TestCase(true)]
        public void FailedMedicalCompletionFaultsBeforePublishingADeadlineOutcome(bool deadline)
        {
            var f = new Clinic(shift: deadline ? 3000 : 12000); f.Load(); f.Start();
            var workflow = typeof(WorldSession).GetField("_workers", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(f.World)!;
            var states = (IDictionary<Guid, WorkerState>)workflow.GetType().GetField("_workers", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(workflow)!;
            typeof(WorkerState).GetField("_revision", BindingFlags.NonPublic | BindingFlags.Instance)!.SetValue(states[f.Patient], long.MaxValue);
            Assert.Throws<OverflowException>(() => f.World.AdvanceTo(3000));
            Assert.That(f.World.View.Outcome, Is.EqualTo(WorldOutcome.Faulted)); Assert.That(f.World.WorkerCount, Is.Zero);
            Assert.That(f.World.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended || r.MedicalChange?.Kind == MedicalEvent.Completed), Is.False);
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.Zero); Assert.That(f.World.Medical.Summary.CancelledCycles, Is.EqualTo(1));
            Assert.That(f.World.Debrief!.Medical.UsedCartridges, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
        }

        [Test] public void EmptyMedicalStockRejectsBeforeAnyReserveDebit()
        {
            var f = new Clinic(cartridges: 0); f.Load();
            Assert.That(f.Start().Medical!.Status, Is.EqualTo(MedicalStatus.NoCartridge));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.World.Medical.Summary.UsedCartridges, Is.Zero);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station));
        }

        [Test] public void MedicalInsertionRejectsAFormerLeaseWithoutTakingTheCurrentHold()
        {
            var f = new Clinic(); f.Hit(); f.Operator.Grab(f.Body); long oldLease = f.World.GetObject(f.Body)!.LeaseGeneration;
            f.Operator.Release(f.Body); f.Operator.Grab(f.Body); var current = f.World.GetObject(f.Body)!;
            var stale = new InteractionCommand(f.World.Epoch, 4, InteractionKind.Medical, f.Station,
                medical: new MedicalRequest(MedicalAction.Insert, 0, f.Body, current.Revision, oldLease));
            var reply = f.World.ExecuteInteraction(Fixture.Id(21), stale);
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.StaleLease)); Assert.That(reply.HasNewCommit, Is.False);
            Assert.That(f.World.GetObject(f.Body)!.LeaseGeneration, Is.EqualTo(current.LeaseGeneration));
            Assert.That(f.World.GetObject(f.Body)!.HolderId, Is.EqualTo(Fixture.Id(11)));
            Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Empty)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero);
        }

        [Test] public void SoleSurvivingPatientCanLeaveTheirReadyChamberAndRecoverWithoutAnOperator()
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.Disconnect(f.World.Epoch, Fixture.Id(21)); f.World.Disconnect(f.World.Epoch, Fixture.Id(22));
            Assert.That(f.World.View.ConnectedPlayerCount, Is.EqualTo(1)); f.World.AdvanceTo(3000);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null); Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Empty));
            Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(f.Worker.CanInteract, Is.False);
            f.World.AdvanceTo(3500); var recovery = f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Patient, recovery.Worker!.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.Worker.CanInteract, Is.True); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
        }

        [Test] public void EmergencyMedicalEgressCannotReleaseAnotherPatientOrAnUnfinishedTreatment()
        {
            var f = new Clinic(); f.Load(); f.Start();
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            f.World.AdvanceTo(3000);
            Assert.That(f.Other.OperateMedical(f.Station, MedicalAction.EmergencyEject).Medical!.Status, Is.EqualTo(MedicalStatus.InvalidPatient));
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station));
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.Start).Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
        }

        [Test] public void HistoricalEmergencyEgressCannotReleaseTheNextPatientInTheSameChamber()
        {
            var f = new Clinic(reserve: 20); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
            f.World.ApplyWorkerImpact(f.World.Epoch, Fixture.Id(12), 1, WorkerImpact.Incapacitating, 0, Fixture.Id(71), Fixture.Id(61));
            f.Operator.Grab(Fixture.Id(33)); f.Operator.OperateMedical(f.Station, MedicalAction.Insert, Fixture.Id(33));
            Assert.That(f.Start().HasNewCommit, Is.True); var second = f.World.Medical.View!;
            for (int i = 0; i < 20; i++)
            {
                var historical = f.PatientCommands.ReplayLast(); Assert.That(historical.IsReplay, Is.True);
                Assert.That(historical.HasNewCommit, Is.False);
            }
            Assert.That(f.World.Medical.View!.CycleId, Is.EqualTo(second.CycleId)); Assert.That(f.World.Medical.View.Phase, Is.EqualTo(MedicalPhase.Treating));
            Assert.That(f.World.GetObject(Fixture.Id(33))!.SlotId, Is.EqualTo(f.Station)); Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null);
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(12)); Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(2));
        }

        [Test] public void MedicalDebitInvalidatesStaleReactorControlWithoutSpendingTwice()
        {
            var f = new Clinic(reserve: 20); f.Load(); long reactorRevision = f.World.Reactor.View!.Revision;
            var pending = new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, Fixture.Id(80),
                reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, reactorRevision));
            f.Start(); Assert.That(f.World.Reactor.View!.Revision, Is.GreaterThan(reactorRevision));
            Assert.That(f.World.ExecuteInteraction(Fixture.Id(22), pending).Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6)); Assert.That(f.World.Reactor.PowerSummary.Available, Is.EqualTo(14));
        }

        [TestCase(false)] [TestCase(true)]
        public void ExternallyAidedSolePatientCanLeaveALoadedOrInterruptedChamber(bool started)
        {
            var f = new Clinic(); f.Load(); if (started) f.Start();
            Assert.That(f.World.StabilizeWorker(f.World.Epoch, f.Patient, f.Worker.Revision, 0).Status, Is.EqualTo(WorkerStatus.Applied));
            f.World.Disconnect(f.World.Epoch, Fixture.Id(21)); f.World.Disconnect(f.World.Epoch, Fixture.Id(22));
            if (started)
            {
                Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).Medical!.Status, Is.EqualTo(MedicalStatus.InvalidState));
                f.World.AdvanceTo(0); Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Interrupted));
            }
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null); Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(started ? 6 : 0));
            var recovery = f.World.BeginWorkerRecovery(f.World.Epoch, f.Patient, f.Worker.RecoveryEpisode, f.Worker.Revision);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, f.Patient, recovery.Worker!.RecoveryAttempt).Status, Is.EqualTo(WorkerStatus.Applied));
        }

        [Test] public void PausedEmergencyEgressIsFinalizedWithoutReleasingAndRequiresANewIntentAfterResume()
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            var station = f.World.Medical.View!; var body = f.World.GetObject(f.Body)!; var worker = f.Worker;
            f.World.Pause(f.World.Epoch);
            var denied = f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject);
            Assert.That(denied.Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            Assert.That(denied.IsTerminal, Is.True); Assert.That(denied.HasNewCommit, Is.False);
            AssertReadyPatientUnchanged(f, station, body, worker);
            f.World.Resume(f.World.Epoch);
            var historical = f.PatientCommands.ReplayLast();
            Assert.That(historical.IsReplay, Is.True); Assert.That(historical.Status, Is.EqualTo(denied.Status));
            Assert.That(historical.HasNewCommit, Is.False); AssertReadyPatientUnchanged(f, station, body, worker);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null);
        }

        [TestCase(AccessDecision.ActorUnavailable, InteractionStatus.ActorUnavailable)]
        [TestCase(AccessDecision.TargetUnavailable, InteractionStatus.TargetUnavailable)]
        [TestCase(AccessDecision.OutOfReach, InteractionStatus.OutOfReach)]
        public void EmergencyEgressStillRequiresCurrentTrustedAccessAndDenialCannotTurnIntoAHistoricalRelease(
            AccessDecision decision, InteractionStatus expected)
        {
            var access = new TestAccess(); var f = new Clinic(access: access); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            var station = f.World.Medical.View!; var body = f.World.GetObject(f.Body)!; var worker = f.Worker;
            access.Decision = decision;
            var denied = f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject);
            Assert.That(denied.Status, Is.EqualTo(expected)); Assert.That(denied.IsTerminal, Is.True);
            Assert.That(denied.HasNewCommit, Is.False); Assert.That(access.LastActor, Is.EqualTo(f.Patient));
            AssertReadyPatientUnchanged(f, station, body, worker); int calls = access.Calls;
            access.Decision = AccessDecision.Allowed;
            var replay = f.PatientCommands.ReplayLast();
            Assert.That(replay.IsReplay, Is.True); Assert.That(replay.Status, Is.EqualTo(expected));
            Assert.That(replay.HasNewCommit, Is.False); Assert.That(access.Calls, Is.EqualTo(calls));
            AssertReadyPatientUnchanged(f, station, body, worker);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null);
        }

        [TestCase(true)] [TestCase(false)]
        public void EmergencyEgressRejectsStaleStationOrBodyRevisionWithoutChangingAnyOwner(bool staleStation)
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            var station = f.World.Medical.View!; var body = f.World.GetObject(f.Body)!; var worker = f.Worker;
            var stale = new InteractionCommand(f.World.Epoch, 1, InteractionKind.MedicalEgress, f.Station,
                medical: new MedicalRequest(MedicalAction.EmergencyEject,
                    station.Revision - (staleStation ? 1 : 0), objectRevision: body.Revision - (staleStation ? 0 : 1)));
            var reply = f.World.ExecuteInteraction(Fixture.Id(20), stale);
            Assert.That(reply.Medical!.Status, Is.EqualTo(staleStation ? MedicalStatus.RevisionConflict : MedicalStatus.CustodyRejected));
            Assert.That(reply.Status, Is.EqualTo(staleStation ? InteractionStatus.MedicalRejected : InteractionStatus.RevisionConflict));
            Assert.That(reply.IsTerminal, Is.True); Assert.That(reply.HasNewCommit, Is.False);
            AssertReadyPatientUnchanged(f, station, body, worker);
            var replay = f.World.ExecuteInteraction(Fixture.Id(20), stale);
            Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            AssertReadyPatientUnchanged(f, station, body, worker);
            var current = new InteractionCommand(f.World.Epoch, 2, InteractionKind.MedicalEgress, f.Station,
                medical: new MedicalRequest(MedicalAction.EmergencyEject, station.Revision, objectRevision: body.Revision));
            Assert.That(f.World.ExecuteInteraction(Fixture.Id(20), current).HasNewCommit, Is.True);
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.Null);
        }

        [Test] public void EmergencyEgressCannotUseAnUnregisteredStationToReleaseThePatientsCurrentBody()
        {
            var f = new Clinic(); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            var station = f.World.Medical.View!; var body = f.World.GetObject(f.Body)!; var worker = f.Worker;
            var reply = f.PatientCommands.OperateMedical(Fixture.Id(91), MedicalAction.EmergencyEject);
            Assert.That(reply.Medical!.Status, Is.EqualTo(MedicalStatus.UnknownStation));
            Assert.That(reply.IsTerminal, Is.True); Assert.That(reply.HasNewCommit, Is.False);
            AssertReadyPatientUnchanged(f, station, body, worker);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
        }

        [Test] public void OldEpochEmergencyEgressCannotReleaseAReusedStationOrConsumeTheNewPatientSequence()
        {
            var previous = new Clinic(); previous.Load(); previous.Start(); previous.World.AdvanceTo(3000);
            var old = new InteractionCommand(previous.World.Epoch, 1, InteractionKind.MedicalEgress, previous.Station,
                medical: new MedicalRequest(MedicalAction.EmergencyEject, previous.World.Medical.View!.Revision,
                    objectRevision: previous.World.GetObject(previous.Body)!.Revision));
            previous.World.Stop();
            var f = new Clinic(); f.Load(); f.Start(); f.World.AdvanceTo(3000);
            var station = f.World.Medical.View!; var body = f.World.GetObject(f.Body)!; var worker = f.Worker;
            Assert.That(f.World.Epoch, Is.Not.EqualTo(previous.World.Epoch));
            var reply = f.World.ExecuteInteraction(Fixture.Id(20), old);
            Assert.That(reply.Status, Is.EqualTo(InteractionStatus.WrongEpoch));
            Assert.That(reply.IsTerminal, Is.False); Assert.That(reply.HasNewCommit, Is.False);
            AssertReadyPatientUnchanged(f, station, body, worker);
            Assert.That(f.PatientCommands.OperateMedical(f.Station, MedicalAction.EmergencyEject).HasNewCommit, Is.True);
        }

        private static void AssertReadyPatientUnchanged(Clinic f, MedicalView station, ObjectClaimView body, WorkerView worker)
        {
            Assert.That(f.World.Medical.View!.Revision, Is.EqualTo(station.Revision));
            Assert.That(f.World.Medical.View.Phase, Is.EqualTo(MedicalPhase.Ready));
            Assert.That(f.World.Medical.View.CycleId, Is.EqualTo(station.CycleId));
            Assert.That(f.World.GetObject(f.Body)!.Revision, Is.EqualTo(body.Revision));
            Assert.That(f.World.GetObject(f.Body)!.SlotId, Is.EqualTo(f.Station));
            Assert.That(f.Worker.Revision, Is.EqualTo(worker.Revision));
            Assert.That(f.Worker.Awareness, Is.EqualTo(WorkerAwareness.Alert)); Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
            Assert.That(f.World.Reactor.PowerSummary.Available, Is.EqualTo(4));
            Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(1));
            Assert.That(f.World.Medical.Summary.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.World.Medical.Summary.CancelledCycles, Is.Zero); Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.Zero);
        }
    }
}
