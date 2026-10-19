using System;
using CriticalShift.Application;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    public sealed class SuitMobilityTests
    {
        private static Guid Id(int n) => Fixture.Id(n);
        private sealed class SafeRecovery : IWorkerRecoveryPolicy
        { public RecoveryClearance Evaluate(Guid epoch, Guid actor, long attempt) => RecoveryClearance.Safe; }
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port;
            internal WorkerView Worker => World.GetWorker(Id(10))!;
            internal Setup(WorkerSuit suit)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, 60000, true), new TestAccess(), new SafeRecovery());
                World.RegisterConnection(Id(20), Id(10)); World.SuitFitting.Register(Id(80), new SuitFittingDefinition(15000));
                World.RegisterWorkerContaminationSource(Id(90), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20, 1));
                World.RegisterWorkerContaminationSource(Id(91), new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 100, 1));
                Port = new LocalCommandPort(World, Id(20)); World.Start();
                World.SetWorkerEnvironment(World.Epoch, Id(10), Worker.Revision, suit, 0);
            }
        }

        [TestCase(WorkerSuit.None, 1000, 20)]
        [TestCase(WorkerSuit.Intact, 800, 5)]
        [TestCase(WorkerSuit.Compromised, 800, 10)]
        public void SuitWalkingTradeoffAndExposureProtectionStayIndependentThroughWashing(WorkerSuit suit, int speed, int contamination)
        {
            var f = new Setup(suit); var before = f.Worker;
            f.World.ObserveWorkerContamination(f.World.Epoch, Id(10), Id(90), 1, Id(101), 0);
            Assert.That(f.Worker.Contamination, Is.EqualTo(contamination)); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed));
            Assert.That(f.Worker.PhysicallyUpright, Is.True); Assert.That(f.Worker.CanInteract, Is.True);
            f.World.ObserveWorkerContamination(f.World.Epoch, Id(10), Id(91), 1, Id(102), 0);
            Assert.That(f.Worker.Contamination, Is.Zero); Assert.That(f.Worker.Suit, Is.EqualTo(suit));
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed)); Assert.That(before.Contamination, Is.Zero);
            Assert.That(before.SuitWalkSpeedPermille, Is.EqualTo(speed));
        }

        [TestCase(WorkerSuit.None, 1000)] [TestCase(WorkerSuit.Compromised, 800)]
        public void FittingCancellationAndInjuryCannotApplyTheFutureSuitsWalkingCost(WorkerSuit suit, int speed)
        {
            var f = new Setup(suit); var before = f.Worker;
            Assert.That(f.Port.OperateSuitFitting(Id(80), SuitFittingAction.Start).HasNewCommit, Is.True);
            f.World.AdvanceTo(14999); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed));
            Assert.That(f.Port.OperateSuitFitting(Id(80), SuitFittingAction.Cancel).HasNewCommit, Is.True);
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed));
            Assert.That(f.Port.OperateSuitFitting(Id(80), SuitFittingAction.Start).HasNewCommit, Is.True);
            f.World.ApplyWorkerImpact(f.World.Epoch, Id(10), 1, WorkerImpact.Incapacitating, 0);
            Assert.That(f.Worker.SuitFitting, Is.Null); Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed));
            Assert.That(f.Worker.CanInteract, Is.False); f.World.StabilizeWorker(f.World.Epoch, Id(10), f.Worker.Revision, 0);
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed)); var current = f.Worker;
            Assert.That(f.World.BeginWorkerRecovery(f.World.Epoch, Id(10), current.RecoveryEpisode, current.Revision).Changed, Is.True);
            Assert.That(f.World.CompleteWorkerRecovery(f.World.Epoch, Id(10), f.Worker.RecoveryAttempt).Changed, Is.True);
            Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(speed)); Assert.That(f.Worker.CanInteract, Is.True);
            Assert.That(before.SuitWalkSpeedPermille, Is.EqualTo(speed)); Assert.That(before.Suit, Is.EqualTo(suit));
        }

        [Test] public void WorkerWalkingProjectionIsImmutableAndFreshWorldHasNoWornBulk()
        {
            var f = new Setup(WorkerSuit.None); var original = f.Worker;
            f.World.SetWorkerEnvironment(f.World.Epoch, Id(10), original.Revision, WorkerSuit.Intact, 40);
            long revision = f.Worker.Revision, sequence = f.Port.LastTerminalSequence;
            for (int i = 0; i < 10; i++) Assert.That(f.Worker.SuitWalkSpeedPermille, Is.EqualTo(800));
            Assert.That(original.SuitWalkSpeedPermille, Is.EqualTo(1000)); Assert.That(f.Worker.Revision, Is.EqualTo(revision));
            Assert.That(f.Port.LastTerminalSequence, Is.EqualTo(sequence)); f.World.Stop();
            var fresh = new Setup(WorkerSuit.None); Assert.That(fresh.Worker.Epoch, Is.Not.EqualTo(original.Epoch));
            Assert.That(fresh.Worker.SuitWalkSpeedPermille, Is.EqualTo(1000));
        }
    }
}
