using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using CriticalShift.Presentation;
using CriticalShift.Sandbox;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class CarriedMaterialExposureTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class SafeRecovery : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid actor, long attempt) => RecoveryClearance.Safe; }
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port, Other;
            internal readonly CarriedMaterialExposureFeed Feed;
            internal WorkerView Worker => World.GetWorker(Id(10))!;
            internal Setup(int contamination = 800, WorkerSuit suit = WorkerSuit.None, long lease = 3000, bool start = true, int trace = 128,
                bool bindOther = true)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, 30000, true, leaseMilliseconds: lease), new TestAccess(), new SafeRecovery(), traceCapacity: trace);
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11));
                World.Production.RegisterBatch(Id(30), Id(60), Id(70), Id(80), MaterialKind.Ore, 12, 100, contamination);
                World.Production.RegisterBatch(Id(31), Id(61), Id(70), Id(81), MaterialKind.Ore, 12, 100, 800);
                World.Production.RegisterMachine(Id(40), MachineRecipe.Washing(Id(50), MaterialKind.Ore, 1000, 100, 100));
                World.Production.RegisterMachine(Id(41), new MachineRecipe(Id(51), MaterialKind.Ore, MaterialKind.Fuel, 1000, 500, 200, 100));
                World.Reactor.Register(Id(95), new ReactorDefinition(Id(96)));
                World.RegisterWorkerContaminationSource(Id(90), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 12, 1000));
                World.RegisterWorkerContaminationSource(Id(92), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 12, 1000));
                World.RegisterWorkerContaminationSource(Id(91), new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 25, 1000));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21));
                Feed = new CarriedMaterialExposureFeed(World, bindOther ? new[] { Id(10), Id(11) } : new[] { Id(10) },
                    new[] { new CarriedMaterialExposureSource(Id(30), Id(90), 500, "Dirty test crate"), new CarriedMaterialExposureSource(Id(31), Id(92), 500, "Second test crate") });
                if (start) { World.Start(); World.SetWorkerEnvironment(World.Epoch, Id(10), Worker.Revision, suit, 0); }
            }
            internal void Grab() => Applied(Port.Grab(Id(30)));
        }
        private static void Applied(InteractionReply reply) => Assert.That(reply.HasNewCommit, Is.True, reply.Status + " / " + reply.Production?.Status);

        [TestCase(WorkerSuit.None, 12)] [TestCase(WorkerSuit.Compromised, 6)] [TestCase(WorkerSuit.Intact, 3)]
        public void DirtyCargoUsesCurrentHolderPpeAndPreservesMaterialsCustodyPowerAndInjury(WorkerSuit suit, int load)
        {
            var f = new Setup(suit: suit); f.Grab(); var batch = f.World.Production.GetBatch(Id(30))!; var claim = f.World.GetObject(Id(30))!;
            var old = f.Worker; var sample = f.Feed.Sample().Single();
            Assert.That(sample.Status, Is.EqualTo(WorkerStatus.Applied)); Assert.That(f.Worker.Contamination, Is.EqualTo(load));
            Assert.That(sample.ContaminationContact!.RawUnits, Is.EqualTo(12)); Assert.That(sample.ContaminationContact.EffectiveUnits, Is.EqualTo(load));
            Assert.That(f.Worker.LastCauseId, Is.EqualTo(old.LastCauseId)); Assert.That(f.Worker.LastHazardId, Is.EqualTo(old.LastHazardId));
            Assert.That(f.Worker.Suit, Is.EqualTo(suit)); Assert.That(f.World.GetWorker(Id(11))!.Contamination, Is.Zero);
            Assert.That(f.World.Production.GetBatch(Id(30))!.BatchId, Is.EqualTo(batch.BatchId)); Assert.That(f.World.Production.GetBatch(Id(30))!.Contamination, Is.EqualTo(800));
            Assert.That(f.World.GetObject(Id(30))!.Revision, Is.EqualTo(claim.Revision)); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.EqualTo(Id(10)));
            Assert.That(f.World.Reactor.PowerSummary!.Spent, Is.Zero); Assert.That(f.World.Production.Summary.ReserveSpent, Is.Zero);
            Assert.That(f.World.Production.Summary.ActiveUnits, Is.EqualTo(24));
        }

        [TestCase(0, 0)] [TestCase(500, 0)] [TestCase(501, 1)] [TestCase(1000, 1)]
        public void CarriedMaterialThresholdIsStrictAndReadoutCannotObserveForTheCaller(int contamination, int samples)
        {
            var f = new Setup(contamination); f.Grab(); long sequence = f.Port.LastTerminalSequence, revision = f.Worker.Revision;
            string cue = f.Feed.Describe(Id(10)); f.Feed.Describe(Id(10));
            Assert.That(f.Worker.Revision, Is.EqualTo(revision)); Assert.That(f.Port.LastTerminalSequence, Is.EqualTo(sequence));
            Assert.That(cue.Contains("Dirty test crate"), Is.EqualTo(samples == 1)); Assert.That(f.Feed.Sample().Count, Is.EqualTo(samples));
        }

        [Test] public void UnchangedHeldBatchProducesOneCurrentContactAtEachDueTimeWithoutCatchup()
        {
            var f = new Setup(lease: 20000); f.Grab(); var original = f.World.Production.GetBatch(Id(30))!;
            Assert.That(f.Feed.Sample().Single().ContaminationContact!.Sequence, Is.EqualTo(1)); Assert.That(f.Feed.Sample(), Is.Empty);
            f.World.AdvanceTo(999); Assert.That(f.Feed.Sample(), Is.Empty); f.World.AdvanceTo(1000);
            Assert.That(f.Feed.Sample().Single().ContaminationContact!.Sequence, Is.EqualTo(2)); f.World.AdvanceTo(10000);
            var delayed = f.Feed.Sample().Single().ContaminationContact!; Assert.That(delayed.Sequence, Is.EqualTo(3));
            Assert.That(delayed.SampleShiftMilliseconds, Is.EqualTo(10000)); Assert.That(f.Worker.Contamination, Is.EqualTo(36));
            Assert.That(f.World.Production.GetBatch(Id(30))!.BatchId, Is.EqualTo(original.BatchId)); Assert.That(f.Feed.Sample(), Is.Empty);
        }

        [Test] public void DropRegrabAndHolderChangesRetainSeparateWorkerSourceCooldowns()
        {
            var f = new Setup(); f.Grab(); f.Feed.Sample(); f.World.AdvanceTo(500);
            Applied(f.Port.Release(Id(30))); f.Grab(); Assert.That(f.Feed.Sample(), Is.Empty);
            Applied(f.Port.Release(Id(30))); Applied(f.Other.Grab(Id(30)));
            Assert.That(f.Feed.Sample().Single().Worker!.Id, Is.EqualTo(Id(11))); Assert.That(f.World.GetWorker(Id(11))!.Contamination, Is.EqualTo(12));
            Applied(f.Other.Release(Id(30))); f.Grab(); Assert.That(f.Feed.Sample(), Is.Empty); f.World.AdvanceTo(1000);
            Assert.That(f.Feed.Sample().Single().ContaminationContact!.Sequence, Is.EqualTo(2)); Assert.That(f.Worker.Contamination, Is.EqualTo(24));
        }

        [Test] public void AnotherContainerHasItsOwnCooldownAndInsertionStopsCurrentHandling()
        {
            var f = new Setup(); f.Grab(); f.Feed.Sample(); Applied(f.Port.Release(Id(30))); Applied(f.Port.Grab(Id(31)));
            Assert.That(f.Feed.Sample().Single().ContaminationContact!.SourceId, Is.EqualTo(Id(92)));
            Applied(f.Port.OperateMachine(Id(40), ProductionAction.Insert, Id(31))); f.World.AdvanceTo(1000);
            Assert.That(f.Feed.Sample(), Is.Empty); Assert.That(f.Worker.Contamination, Is.EqualTo(24));
        }

        [Test] public void PauseFreezesExposureButHostLeaseExpiryStillRemovesTheHolder()
        {
            var f = new Setup(lease: 1000); f.Grab(); f.Feed.Sample(); f.World.Pause(f.World.Epoch); f.World.AdvanceTo(500);
            Assert.That(f.Feed.Sample(), Is.Empty); Assert.That(f.Worker.Contamination, Is.EqualTo(12));
            f.World.AdvanceTo(1001); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.Null); f.World.Resume(f.World.Epoch);
            Assert.That(f.Feed.Sample(), Is.Empty); f.Grab(); Assert.That(f.Feed.Sample(), Is.Empty);
            f.World.AdvanceTo(2001); Assert.That(f.World.GetObject(Id(30))!.HolderId, Is.Null); Assert.That(f.Feed.Sample(), Is.Empty);
        }

        [Test] public void WashingStopsDirtyHandlingWhileRetainedTraceKeepsOriginalMaterialAttribution()
        {
            var f = new Setup(trace: 4); f.Grab(); f.Feed.Sample();
            var contact = f.World.Trace.Records.Last(r => r.ContaminationContact != null); var input = contact.CarriedMaterial!;
            Assert.That(contact.EntityId, Is.EqualTo(Id(30))); Assert.That(contact.BatchId, Is.EqualTo(Id(60))); Assert.That(contact.MaterialCauseId, Is.EqualTo(Id(80)));
            Applied(f.Port.OperateMachine(Id(40), ProductionAction.Insert, Id(30))); Applied(f.Port.OperateMachine(Id(40), ProductionAction.Start));
            f.World.AdvanceTo(1000); Applied(f.Port.OperateMachine(Id(40), ProductionAction.Eject)); f.Grab();
            Assert.That(f.World.Production.GetBatch(Id(30))!.Contamination, Is.EqualTo(100)); Assert.That(f.Feed.Sample(), Is.Empty);
            Assert.That(input.Contamination, Is.EqualTo(800)); Assert.That(input.BatchId, Is.EqualTo(Id(60))); Assert.That(input.Flags, Is.EqualTo(MaterialFlags.None));
            f.World.Stop(); var retained = f.World.Debrief!.Timeline.Single(r => r.CarriedMaterial != null);
            Assert.That(retained.CarriedMaterial!.Contamination, Is.EqualTo(800)); Assert.That(retained.MaterialCauseId, Is.EqualTo(Id(80)));
            var row = SandboxTraceFeed.DebriefEntries(f.World.Debrief).Single(e => e.Description.Contains("Dirty cargo exposure"));
            Assert.That(row.Description, Does.Contain("800/1000")); Assert.That(row.CauseId, Is.EqualTo(Id(80)));
        }

        [Test] public void DirtyConversionDoesNotResetTheContainerSourceOrLaunderItsExposure()
        {
            var f = new Setup(); f.Grab(); f.Feed.Sample();
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Insert, Id(30))); Applied(f.Port.OperateMachine(Id(41), ProductionAction.Start)); f.World.AdvanceTo(1000);
            Applied(f.Port.OperateMachine(Id(41), ProductionAction.Eject)); f.Grab();
            var dose = f.Feed.Sample().Single(); Assert.That(dose.ContaminationContact!.Sequence, Is.EqualTo(2));
            Assert.That(f.Worker.Contamination, Is.EqualTo(24)); Assert.That(f.World.Trace.Records.Last().CarriedMaterial!.Kind, Is.EqualTo(MaterialKind.Fuel));
        }

        [Test] public void ReplayedHandlingReceiptsCannotRestoreDroppedOrSlottedHistoricalCustody()
        {
            var f = new Setup(); f.Grab(); f.Feed.Sample(); Applied(f.Port.Release(Id(30))); f.World.AdvanceTo(1000);
            Assert.That(f.Port.ReplayLast().IsReplay, Is.True); Assert.That(f.Feed.Sample(), Is.Empty);
            f.Grab(); Applied(f.Port.OperateMachine(Id(40), ProductionAction.Insert, Id(30))); f.World.AdvanceTo(2000);
            Assert.That(f.Port.ReplayLast().IsReplay, Is.True); Assert.That(f.Feed.Sample(), Is.Empty); Assert.That(f.Worker.Contamination, Is.EqualTo(12));
        }

        [Test] public void DisconnectRetiresOnlyThatWorkersFeedsAndTerminalClearCannotRebindToRestart()
        {
            var f = new Setup(); f.Grab(); f.Feed.Sample(); f.World.Disconnect(f.World.Epoch, Id(20)); f.Feed.Sample();
            Assert.That(f.Feed.BoundFeedCount, Is.EqualTo(2)); Applied(f.Other.Grab(Id(30))); Assert.That(f.Feed.Sample().Single().Worker!.Id, Is.EqualTo(Id(11)));
            f.World.AdvanceTo(30000); Assert.That(f.Feed.Sample(), Is.Empty); Assert.That(f.Feed.BoundFeedCount, Is.Zero); f.Feed.Clear();
            var next = f.World.Restart(new TestAccess()); next.RegisterConnection(Id(20), Id(10)); next.Start();
            Assert.That(f.Feed.Sample(), Is.Empty); Assert.That(next.GetWorker(Id(10))!.Contamination, Is.Zero); Assert.That(f.Feed.Epoch, Is.Not.EqualTo(next.Epoch));
        }

        [Test] public void UnknownLiveHolderAndCompetingProducerFailOnceWithoutInventingANewReceipt()
        {
            var unknown = new Setup(bindOther: false); Applied(unknown.Other.Grab(Id(30)));
            Assert.Throws<InvalidOperationException>(() => unknown.Feed.Sample()); Assert.That(unknown.Feed.Failed, Is.True);
            Assert.That(unknown.Feed.BoundFeedCount, Is.Zero); Assert.That(unknown.Feed.Sample(), Is.Empty); Assert.That(unknown.World.GetWorker(Id(11))!.Contamination, Is.Zero);
            var f = new Setup(); f.Grab(); f.World.ObserveWorkerContamination(f.World.Epoch, Id(10), Id(90), 1, Id(999), 0);
            Assert.Throws<InvalidOperationException>(() => f.Feed.Sample()); Assert.That(f.Feed.Failed, Is.True); Assert.That(f.Feed.Sample(), Is.Empty);
            Assert.That(f.Worker.Contamination, Is.EqualTo(12));
        }

        [Test] public void SetupSamplingAndCallerListMutationCannotEraseOrChangePreparedBindings()
        {
            var f = new Setup(start: false); var workers = new[] { Id(10) };
            var sources = new[] { new CarriedMaterialExposureSource(Id(30), Id(90), 500, "Original crate") };
            var feed = new CarriedMaterialExposureFeed(f.World, workers, sources); workers[0] = Id(11);
            sources[0] = new CarriedMaterialExposureSource(Id(31), Id(92), 500, "Changed crate");
            Assert.That(feed.Sample(), Is.Empty); Assert.That(feed.BoundFeedCount, Is.EqualTo(1)); f.World.Start(); f.Grab();
            Assert.That(feed.Sample().Single().Worker!.Id, Is.EqualTo(Id(10))); Assert.That(feed.Describe(Id(10)), Does.Contain("Original crate"));
        }

        [TestCase("unknown-source")] [TestCase("wash-source")] [TestCase("unknown-container")]
        [TestCase("duplicate-container")] [TestCase("duplicate-source")] [TestCase("duplicate-worker")]
        public void InvalidCarriedExposureSetupCannotCreateAProducer(string variant)
        {
            var f = new Setup(start: false); var workers = new List<Guid> { Id(10) };
            var sources = new List<CarriedMaterialExposureSource> { new CarriedMaterialExposureSource(Id(30), Id(90), 500, "First") };
            if (variant == "unknown-source" || variant == "wash-source") sources[0] = new CarriedMaterialExposureSource(Id(30), Id(variant == "wash-source" ? 91 : 999), 500, "Invalid source");
            if (variant == "unknown-container") sources[0] = new CarriedMaterialExposureSource(Id(99), Id(90), 500, "Missing material");
            if (variant == "duplicate-container") sources.Add(new CarriedMaterialExposureSource(Id(30), Id(92), 500, "Duplicate"));
            if (variant == "duplicate-source") sources.Add(new CarriedMaterialExposureSource(Id(31), Id(90), 500, "Duplicate"));
            if (variant == "duplicate-worker") workers.Add(Id(10));
            Assert.Throws<ArgumentException>(() => new CarriedMaterialExposureFeed(f.World, workers, sources));
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.World.Production.Summary.ReserveSpent, Is.Zero);
        }

        [Test] public void SaturatedWorkerStillConsumesOneCooledNoChangeObservation()
        {
            var f = new Setup(); f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), f.Worker.Revision, WorkerSuit.None, 100); f.Grab();
            var noChange = f.Feed.Sample().Single(); Assert.That(noChange.Status, Is.EqualTo(WorkerStatus.NoChange));
            Assert.That(noChange.ContaminationContact!.Sequence, Is.EqualTo(1)); Assert.That(f.Feed.Sample(), Is.Empty);
            f.World.AdvanceTo(1000); Assert.That(f.Feed.Sample().Single().ContaminationContact!.Sequence, Is.EqualTo(2)); Assert.That(f.Worker.Contamination, Is.EqualTo(100));
        }

        [Test] public void CargoContactPreservesARealEarlierInjuryAfterAidAndStandingRecovery()
        {
            var f = new Setup(); f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, WorkerImpact.Incapacitating, 0, Id(701), Id(702));
            f.World.StabilizeWorker(f.World.Epoch, Id(10), f.Worker.Revision, 0);
            var ready = f.Worker; Assert.That(f.World.BeginWorkerRecovery(f.World.Epoch, Id(10), ready.RecoveryEpisode, ready.Revision).Changed, Is.True);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, Id(10), f.Worker.RecoveryAttempt).Changed, Is.True);
            f.Grab(); f.Feed.Sample(); Assert.That(f.Worker.LastCauseId, Is.EqualTo(Id(702))); Assert.That(f.Worker.LastHazardId, Is.EqualTo(Id(701)));
            var row = f.World.Trace.Records.Last(r => r.CarriedMaterial != null);
            Assert.That(row.MaterialCauseId, Is.EqualTo(Id(80))); Assert.That(row.CauseId, Is.Not.EqualTo(Id(702)));
            Assert.That(f.Worker.LastImpactSequence, Is.EqualTo(1)); Assert.That(f.Worker.Pose, Is.EqualTo(WorkerPose.Upright));
        }
    }
}
