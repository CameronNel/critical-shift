using System;
using System.Globalization;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class MedicalReadoutTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal Setup(long reserve = 10, long shift = 10000)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), new TestAccess());
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11)); World.RegisterWorkerBody(Id(11), Id(30));
                World.Reactor.Register(Id(90), new ReactorDefinition(Id(91), initialReserve: reserve));
                World.Medical.Register(Id(95), new MedicalDefinition(1200, 4, 2, 750, 35));
                Port = new LocalCommandPort(World, Id(20)); World.Start();
            }
            internal MedicalView Station => World.Medical.View!;
            internal WorkerView Patient => World.GetWorker(Id(11))!;
            internal void Load()
            {
                Assert.That(World.ApplyWorkerImpact(World.Epoch, Id(11), 1, WorkerImpact.Incapacitating, 0, Id(80), Id(81)).Changed, Is.True);
                Assert.That(Port.Grab(Id(30)).HasNewCommit, Is.True);
                Assert.That(Port.OperateMedical(Id(95), MedicalAction.Insert, Id(30)).HasNewCommit, Is.True);
            }
            internal string Summary(MedicalView? snapshot = null, WorkerView? patient = null) => SandboxMedicalReadout.Summary(snapshot ?? Station,
                patient ?? Patient, World.View.ElapsedMilliseconds, World.View.RemainingMilliseconds, World.Reactor.PowerSummary!.Available);
            internal MedicalReply Act(MedicalAction action) => Port.OperateMedical(Id(95), action).Medical!;
        }

        [Test] public void MedicalViewAndReadoutExposeAuthoredInterlocksWithoutHardCodedDefaults()
        {
            var f = new Setup(); Assert.That(f.Station.MaximumContamination, Is.EqualTo(35)); Assert.That(f.Station.RecoveryDelayMilliseconds, Is.EqualTo(750));
            Assert.That(f.Summary(), Does.Contain("1.2s").And.Contain("cost 4 reserve").And.Contain("cartridges 2").And.Contain("35/100").And.Contain("0.75s after stabilization"));
        }

        [TestCase(MedicalPhase.Empty, "E load")]
        [TestCase(MedicalPhase.Loaded, "R request stabilization")]
        [TestCase(MedicalPhase.Treating, "cancel from panel")]
        [TestCase(MedicalPhase.Ready, "E eject")]
        [TestCase(MedicalPhase.Interrupted, "R request stabilization")]
        public void MedicalControlsDescribeTheCurrentCanonicalProcedure(MedicalPhase phase, string expected)
        {
            var f = new Setup();
            if (phase != MedicalPhase.Empty) f.Load();
            if (phase == MedicalPhase.Treating || phase == MedicalPhase.Ready || phase == MedicalPhase.Interrupted) f.Act(MedicalAction.Start);
            if (phase == MedicalPhase.Ready) f.World.AdvanceTo(1200);
            if (phase == MedicalPhase.Interrupted) f.Act(MedicalAction.Cancel);
            Assert.That(f.Station.Phase, Is.EqualTo(phase)); Assert.That(SandboxMedicalReadout.Controls(f.Station), Does.Contain(expected));
        }

        [Test] public void MedicalCountdownUsesShiftTimeAndCannotCatchUpDuringPause()
        {
            var f = new Setup(); f.Load(); f.Act(MedicalAction.Start); f.World.AdvanceTo(300);
            Assert.That(f.Summary(), Does.Contain("0.9s remaining")); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(70000);
            Assert.That(f.Summary(), Does.Contain("0.9s remaining")); f.World.Resume(f.World.Epoch); f.World.AdvanceTo(70900);
            Assert.That(f.Station.Phase, Is.EqualTo(MedicalPhase.Ready)); Assert.That(f.Summary(), Does.Not.Contain("Treatment 0.9s remaining"));
        }

        [Test] public void ReadyPatientReadoutKeepsEjectionSeparateFromCurrentRecoveryWait()
        {
            var f = new Setup(); f.Load(); f.Act(MedicalAction.Start); f.World.AdvanceTo(1300);
            Assert.That(f.Patient.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(f.Patient.Awareness, Is.EqualTo(WorkerAwareness.Alert));
            Assert.That(f.Summary(), Does.Contain("Eject before standing recovery").And.Contain("0.65s plus clearance"));
            f.World.AdvanceTo(2000); Assert.That(f.Summary(), Does.Contain("0s plus clearance"));
            Assert.That(f.World.GetWorkerBodyClaim(Id(11))!.SlotId, Is.EqualTo(Id(95)));
        }

        [Test] public void MedicalReadoutWarnsBeforeAndDuringTreatmentThatCannotFinishThisShift()
        {
            var f = new Setup(shift: 1000); f.Load();
            Assert.That(f.Summary(), Does.Contain("too short").And.Contain("still consumes its cost"));
            Assert.That(f.Act(MedicalAction.Start).Status, Is.EqualTo(MedicalStatus.Applied));
            Assert.That(f.Summary(), Does.Contain("shift will end before this treatment finishes"));
        }

        [Test] public void MedicalReadoutCannotDescribeAForeignOrMissingPatientAsTheCurrentOne()
        {
            var f = new Setup(); f.Load();
            var other = f.World.GetWorker(Id(10));
            Assert.That(SandboxMedicalReadout.Summary(f.Station, other, 0, 10000, 10), Does.Contain("Patient condition unavailable").And.Not.Contain("Patient Alert"));
            Assert.That(SandboxMedicalReadout.Summary(f.Station, null, 0, 10000, 10), Does.Contain("Patient condition unavailable"));
        }

        [Test] public void HistoricalMedicalReadoutRetainsItsOwnPaidStartWithoutChangingLiveResources()
        {
            var f = new Setup(); f.Load(); var started = f.Act(MedicalAction.Start); f.Act(MedicalAction.Cancel);
            long spent = f.World.Reactor.PowerSummary!.Spent, revision = f.World.View.Revision;
            Assert.That(SandboxMedicalReadout.Result(started), Does.Contain("spent 4 reserve and 1 cartridge"));
            Assert.That(started.Station!.Phase, Is.EqualTo(MedicalPhase.Treating)); Assert.That(f.Station.Phase, Is.EqualTo(MedicalPhase.Interrupted));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(spent)); Assert.That(f.World.View.Revision, Is.EqualTo(revision));
        }

        [Test] public void MedicalRejectionsExplainActualContaminationReserveAndStockRequirements()
        {
            var poor = new Setup(reserve: 0); poor.Load();
            Assert.That(SandboxMedicalReadout.Result(poor.Act(MedicalAction.Start)), Does.Contain("Need 4 shared reserve"));
            var dirty = new Setup(); dirty.Load(); dirty.World.SetWorkerEnvironment(dirty.World.Epoch, Id(11), dirty.Patient.Revision, WorkerSuit.None, 36);
            Assert.That(SandboxMedicalReadout.Result(dirty.Act(MedicalAction.Start)), Does.Contain("at most 35/100"));
            var empty = new Setup(); empty.Load();
            for (int i = 0; i < 2; i++) { empty.Act(MedicalAction.Start); empty.Act(MedicalAction.Cancel); }
            Assert.That(SandboxMedicalReadout.Result(empty.Act(MedicalAction.Start)), Does.Contain("no medical cartridges"));
        }

        [Test] public void MedicalCancellationAndDischargeNeverPromiseAutomaticHealingOrStanding()
        {
            var f = new Setup(); f.Load(); f.Act(MedicalAction.Start);
            Assert.That(SandboxMedicalReadout.Result(f.Act(MedicalAction.Cancel)), Does.Contain("stay spent").And.Contain("Eject"));
            Assert.That(SandboxMedicalReadout.Result(f.Act(MedicalAction.Eject)), Does.Contain("discharged down").And.Contain("standing recovery still needs"));
            Assert.That(f.Patient.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
        }

        [Test] public void ExternalAidKeepsInterruptedGuidanceConditionalAndPermitsSeparateEjection()
        {
            var f = new Setup(); f.Load(); f.Act(MedicalAction.Start);
            f.World.StabilizeWorker(f.World.Epoch, Id(11), f.Patient.Revision, 0); f.World.AdvanceTo(0);
            Assert.That(f.Station.Phase, Is.EqualTo(MedicalPhase.Interrupted)); Assert.That(f.Patient.Awareness, Is.EqualTo(WorkerAwareness.Alert));
            Assert.That(SandboxMedicalReadout.Controls(f.Station), Does.Contain("E eject patient").And.Contain("only if still unconscious"));
            Assert.That(f.Act(MedicalAction.Start).Status, Is.EqualTo(MedicalStatus.InvalidPatient));
            Assert.That(f.Act(MedicalAction.Eject).Status, Is.EqualTo(MedicalStatus.Applied));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.EqualTo(4));
        }

        [TestCase("fr-FR")] [TestCase("en-US")]
        public void MedicalReadoutKeepsFractionalTimesInvariantAcrossLocales(string locale)
        {
            var previous = CultureInfo.CurrentCulture;
            try { CultureInfo.CurrentCulture = CultureInfo.GetCultureInfo(locale); Assert.That(new Setup().Summary(), Does.Contain("1.2s").And.Contain("0.75s")); }
            finally { CultureInfo.CurrentCulture = previous; }
        }
    }
}
