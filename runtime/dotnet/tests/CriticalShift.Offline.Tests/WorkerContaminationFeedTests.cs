using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Sandbox;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class WorkerContaminationFeedTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly WorkerContaminationFeed Exposure, Wash, OtherExposure;
            internal readonly LocalCommandPort Port, Other;
            internal WorkerView Worker => World.GetWorker(Id(10))!;
            internal Setup(long duration = 60000, bool start = true)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, duration, true), new TestAccess());
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11)); World.RegisterWorkerBody(Id(10), Id(30));
                World.RegisterWorkerContaminationSource(Id(90), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 12, 1000));
                World.RegisterWorkerContaminationSource(Id(91), new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 25, 1000));
                World.SuitFitting.Register(Id(80), new SuitFittingDefinition(15000));
                Exposure = new WorkerContaminationFeed(World, Id(10), Id(90)); Wash = new WorkerContaminationFeed(World, Id(10), Id(91));
                OtherExposure = new WorkerContaminationFeed(World, Id(11), Id(90));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21)); if (start) World.Start();
            }
        }

        [TestCase(WorkerSuit.None, 12)] [TestCase(WorkerSuit.Compromised, 6)] [TestCase(WorkerSuit.Intact, 3)]
        public void TrustedFeedUsesCanonicalPpeAndReceiptCadence(WorkerSuit suit, int expected)
        {
            var f = new Setup(); f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), f.Worker.Revision, suit, 7);
            var first = f.Exposure.ObserveIfDue()!; Assert.That(first.Status, Is.EqualTo(WorkerStatus.Applied));
            Assert.That(f.Worker.Contamination, Is.EqualTo(7 + expected)); Assert.That(first.ContaminationContact!.EffectiveUnits, Is.EqualTo(expected));
            Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1)); Assert.That(f.Exposure.NextEligibleAtMilliseconds, Is.EqualTo(1000));
            Assert.That(f.Exposure.ObserveIfDue(), Is.Null); f.World.AdvanceTo(999); Assert.That(f.Exposure.ObserveIfDue(), Is.Null);
            f.World.AdvanceTo(1000); var second = f.Exposure.ObserveIfDue()!;
            Assert.That(second.ContaminationContact!.Sequence, Is.EqualTo(2)); Assert.That(second.ContaminationContact.CauseId, Is.Not.EqualTo(first.ContaminationContact.CauseId));
            Assert.That(second.ContaminationContact.SampleShiftMilliseconds, Is.EqualTo(1000)); Assert.That(f.Worker.Contamination, Is.EqualTo(7 + expected * 2));
        }

        [Test] public void TrustedFeedConsumesSaturatedAndCleanReceiptsWithoutInventingConditionCommits()
        {
            var f = new Setup(); f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), 0, WorkerSuit.None, 100);
            long revision = f.Worker.Revision; var capped = f.Exposure.ObserveIfDue()!;
            Assert.That(capped.Status, Is.EqualTo(WorkerStatus.NoChange)); Assert.That(capped.Changed, Is.False);
            Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1)); Assert.That(f.Worker.Revision, Is.EqualTo(revision));
            f.World.AdvanceTo(1000); Assert.That(f.Exposure.ObserveIfDue()!.ContaminationContact!.Sequence, Is.EqualTo(2));
            var clean = new Setup(); Assert.That(clean.Wash.ObserveIfDue()!.Status, Is.EqualTo(WorkerStatus.NoChange));
            clean.Exposure.ObserveIfDue(); Assert.That(clean.Wash.ObserveIfDue(), Is.Null);
            clean.World.AdvanceTo(1000); var washed = clean.Wash.ObserveIfDue()!;
            Assert.That(washed.Status, Is.EqualTo(WorkerStatus.Applied)); Assert.That(washed.ContaminationContact!.Sequence, Is.EqualTo(2));
            Assert.That(clean.Worker.Contamination, Is.Zero);
        }

        [Test] public void LostDerivedEligibilityHintStillUsesCanonicalCooldownAndConsumesItsReceipt()
        {
            var f = new Setup(); f.Exposure.ObserveIfDue(); f.World.AdvanceTo(100);
            typeof(WorkerContaminationFeed).GetField("nextEligibleAt", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(f.Exposure, 0L);
            var cooling = f.Exposure.ObserveIfDue()!; Assert.That(cooling.Status, Is.EqualTo(WorkerStatus.CoolingDown));
            Assert.That(cooling.Changed, Is.False); Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(2));
            Assert.That(f.Exposure.NextEligibleAtMilliseconds, Is.EqualTo(1000)); Assert.That(f.Worker.Contamination, Is.EqualTo(12));
            Assert.That(f.Worker.Revision, Is.EqualTo(1)); Assert.That(f.Exposure.ObserveIfDue(), Is.Null);
            f.World.AdvanceTo(1000); Assert.That(f.Exposure.ObserveIfDue()!.ContaminationContact!.Sequence, Is.EqualTo(3));
        }

        [Test] public void SourceExitPauseAndReentryCannotResetCooldownOrCatchUpMissedContacts()
        {
            var f = new Setup(); f.Exposure.ObserveIfDue(); f.World.AdvanceTo(500);
            f.World.Pause(f.World.Epoch); f.World.AdvanceTo(30000);
            Assert.That(f.Exposure.ObserveIfDue(), Is.Null); Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1));
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(30499); Assert.That(f.Exposure.ObserveIfDue(), Is.Null);
            f.World.AdvanceTo(30500); Assert.That(f.Exposure.ObserveIfDue()!.ContaminationContact!.Sequence, Is.EqualTo(2));
            f.World.AdvanceTo(59500); var late = f.Exposure.ObserveIfDue()!;
            Assert.That(late.ContaminationContact!.SampleShiftMilliseconds, Is.EqualTo(30000));
            Assert.That(late.ContaminationContact.Sequence, Is.EqualTo(3)); Assert.That(f.Worker.Contamination, Is.EqualTo(36));
            Assert.That(f.Exposure.NextEligibleAtMilliseconds, Is.EqualTo(31000)); Assert.That(f.Exposure.ObserveIfDue(), Is.Null);
        }

        [Test] public void EachBoundWorkerSourcePairKeepsIndependentReceiptAndEligibility()
        {
            var f = new Setup(); f.Exposure.ObserveIfDue(); f.OtherExposure.ObserveIfDue(); f.Wash.ObserveIfDue();
            Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1)); Assert.That(f.OtherExposure.LastAcceptedSequence, Is.EqualTo(1));
            Assert.That(f.Wash.LastAcceptedSequence, Is.EqualTo(1)); Assert.That(f.Worker.Contamination, Is.Zero);
            Assert.That(f.World.GetWorker(Id(11))!.Contamination, Is.EqualTo(12));
            f.World.AdvanceTo(1000); f.Exposure.ObserveIfDue();
            Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(2)); Assert.That(f.OtherExposure.LastAcceptedSequence, Is.EqualTo(1));
        }

        [Test] public void FittingDoesNotExcludeExposureAndCurrentDueProtectionPrecedesTheNewSample()
        {
            var f = new Setup(); Assert.That(f.Port.OperateSuitFitting(Id(80), SuitFittingAction.Start).HasNewCommit, Is.True);
            var attempt = f.Worker.SuitFitting!.Id; Assert.That(f.Worker.CanInteract, Is.False);
            f.Exposure.ObserveIfDue(); Assert.That(f.Worker.Contamination, Is.EqualTo(12)); Assert.That(f.Worker.SuitFitting!.Id, Is.EqualTo(attempt));
            f.World.AdvanceTo(15000); var after = f.Exposure.ObserveIfDue()!;
            Assert.That(after.ContaminationContact!.EffectiveUnits, Is.EqualTo(3)); Assert.That(after.ContaminationContact.Sequence, Is.EqualTo(2));
            Assert.That(f.Worker.Contamination, Is.EqualTo(15)); Assert.That(f.Worker.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.World.SuitFitting.Summary.Completed, Is.EqualTo(1));
        }

        [TestCase(WorkerImpact.Knockdown)] [TestCase(WorkerImpact.Incapacitating)]
        public void DownUnconsciousAndDraggedWorkersRemainEligibleWithoutCustodyOrInjuryChanges(WorkerImpact severity)
        {
            var f = new Setup(); f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, severity, 0, Id(100), Id(101));
            Assert.That(f.Other.Grab(Id(30)).HasNewCommit, Is.True); var before = f.Worker; var custody = f.World.GetObject(Id(30))!;
            f.Exposure.ObserveIfDue(); f.Wash.ObserveIfDue(); var after = f.Worker;
            Assert.That(after.Contamination, Is.Zero); Assert.That(after.Revision, Is.EqualTo(before.Revision + 2));
            Assert.That(after.Awareness, Is.EqualTo(before.Awareness)); Assert.That(after.Pose, Is.EqualTo(before.Pose));
            Assert.That(after.LastHazardId, Is.EqualTo(Id(100))); Assert.That(after.LastCauseId, Is.EqualTo(Id(101)));
            Assert.That(after.RecoveryEpisode, Is.EqualTo(before.RecoveryEpisode)); Assert.That(after.RecoveryAttempt, Is.EqualTo(before.RecoveryAttempt));
            Assert.That(f.World.GetObject(Id(30))!.Revision, Is.EqualTo(custody.Revision)); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.EqualTo(Id(11)));
        }

        [Test] public void UnsafeSampleImmediatelyInterruptsPaidCareAndWashingCannotHideTheExcursion()
        {
            var f = new Setup(start: false);
            f.World.Reactor.Register(Id(50), new ReactorDefinition(Id(51), initialReserve: 20)); f.World.Medical.Register(Id(60), new MedicalDefinition());
            f.World.Start(); f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, WorkerImpact.Incapacitating, 0, Id(100), Id(101));
            f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), f.Worker.Revision, WorkerSuit.None, 40);
            Assert.That(f.Other.Grab(Id(30)).HasNewCommit, Is.True); Assert.That(f.Other.OperateMedical(Id(60), MedicalAction.Insert, Id(30)).HasNewCommit, Is.True);
            Assert.That(f.Other.OperateMedical(Id(60), MedicalAction.Start).HasNewCommit, Is.True); var custody = f.World.GetObject(Id(30))!;
            f.Exposure.ObserveIfDue(); Assert.That(f.Worker.Contamination, Is.EqualTo(52)); Assert.That(f.World.Medical.View!.Phase, Is.EqualTo(MedicalPhase.Interrupted));
            f.Wash.ObserveIfDue(); Assert.That(f.Worker.Contamination, Is.EqualTo(27)); Assert.That(f.World.Medical.Summary.InterruptedCycles, Is.EqualTo(1));
            Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(1)); Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(6));
            Assert.That(f.World.GetObject(Id(30))!.Revision, Is.EqualTo(custody.Revision)); Assert.That(f.World.GetObject(Id(30))!.SlotId, Is.EqualTo(Id(60)));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(101))); f.World.AdvanceTo(1000); Assert.That(f.World.Medical.Summary.CompletedCycles, Is.Zero);
        }

        [Test] public void CompetingTrustedProducerFailsTheFeedWithoutManufacturingFreshRetries()
        {
            var f = new Setup(); f.World.ObserveWorkerContamination(f.World.Epoch, Id(10), Id(90), 1, Id(999), 0);
            long revision = f.Worker.Revision; Assert.Throws<InvalidOperationException>(() => f.Exposure.ObserveIfDue());
            Assert.That(f.Worker.Revision, Is.EqualTo(revision)); Assert.That(f.Worker.Contamination, Is.EqualTo(12));
            Assert.That(f.Exposure.LastAcceptedSequence, Is.Zero); f.World.AdvanceTo(1000);
            Assert.Throws<InvalidOperationException>(() => f.Exposure.ObserveIfDue()); Assert.That(f.Worker.Contamination, Is.EqualTo(12));
        }

        [Test] public void TerminalAndOldFeedCannotChangeFrozenOrSuccessorWorkerConditions()
        {
            var f = new Setup(duration: 1000); f.Exposure.ObserveIfDue(); f.World.AdvanceTo(1000); var frozen = f.World.Debrief;
            Assert.That(f.Exposure.ObserveIfDue(), Is.Null); Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1));
            Assert.That(frozen!.WorkersAtEnd.Single(w => w.Id == Id(10)).Contamination, Is.EqualTo(12));
            var successor = f.World.Restart(new TestAccess()); successor.RegisterConnection(Id(20), Id(10));
            successor.RegisterWorkerContaminationSource(Id(90), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 12, 1000));
            var feed = new WorkerContaminationFeed(successor, Id(10), Id(90)); successor.Start(); Assert.That(f.Exposure.ObserveIfDue(), Is.Null);
            Assert.That(feed.ObserveIfDue()!.ContaminationContact!.Sequence, Is.EqualTo(1)); Assert.That(successor.GetWorker(Id(10))!.Contamination, Is.EqualTo(12));
            Assert.That(feed.Epoch, Is.Not.EqualTo(f.Exposure.Epoch)); Assert.That(f.World.Debrief, Is.SameAs(frozen));
        }

        [Test] public void DisconnectedFeedRetiresWithoutConsumingAnotherObservation()
        {
            var f = new Setup(); f.Exposure.ObserveIfDue(); f.World.Disconnect(f.World.Epoch, Id(20)); f.World.AdvanceTo(1000);
            Assert.That(f.Exposure.ObserveIfDue(), Is.Null); Assert.That(f.Exposure.LastAcceptedSequence, Is.EqualTo(1));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(f.World.GetWorker(Id(11))!.Contamination, Is.Zero);
        }

        [TestCase("worker")] [TestCase("source")] [TestCase("started")]
        public void FeedBindingRequiresTheActualSetupWorkerAndRegisteredSource(string invalid)
        {
            var f = new Setup(start: invalid == "started");
            Assert.Throws<InvalidOperationException>(() => new WorkerContaminationFeed(f.World, invalid == "worker" ? Id(999) : Id(10), invalid == "source" ? Id(999) : Id(90)));
        }

        [Test] public void CanonicalSandboxDefinesAPlayablePpeExposureAndWashRoute()
        {
            var world = new WorldSession(SandboxGameplaySetup.Configuration(), new TestAccess()); world.RegisterConnection(Id(2), Id(1));
            SandboxGameplaySetup.Register(world); var exposure = new WorkerContaminationFeed(world, Id(1), SandboxGameplaySetup.ExposureSourceId);
            var wash = new WorkerContaminationFeed(world, Id(1), SandboxGameplaySetup.WashSourceId); var port = new LocalCommandPort(world, Id(2)); world.Start();
            exposure.ObserveIfDue(); Assert.That(world.GetWorker(Id(1))!.Contamination, Is.EqualTo(12));
            Assert.That(port.OperateSuitFitting(SandboxGameplaySetup.SuitStationId, SuitFittingAction.Start).HasNewCommit, Is.True);
            world.AdvanceTo(20000); exposure.ObserveIfDue(); Assert.That(world.GetWorker(Id(1))!.Contamination, Is.EqualTo(15));
            wash.ObserveIfDue(); Assert.That(world.GetWorker(Id(1))!.Contamination, Is.Zero); Assert.That(world.GetWorker(Id(1))!.Suit, Is.EqualTo(WorkerSuit.Intact));
            Assert.That(world.View.ActiveClaimCount, Is.Zero); Assert.That(world.Contracts.View!.Waves.First().DeliveredEnergyUnits, Is.Zero);
            world.Stop(); Assert.That(world.Debrief!.SuitFitting.Completed, Is.EqualTo(1));
        }
    }
}
