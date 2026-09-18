using System;
using CriticalShift.Features.Workers.Domain;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class WorkerRuleTests
    {
        private static WorkerState New() => new WorkerState(Fixture.Id(70));
        private static WorkerState Down(long delay = 100)
        {
            var w = New(); Assert.That(w.Impact(1, ImpactSeverity.Knockdown, delay, 0), Is.EqualTo(WorkerResult.Applied)); return w;
        }
        [Test] public void WorkerStartsWithIndependentDefaultConditions()
        {
            var w = New().Snapshot;
            Assert.That(w.CanInteract, Is.True); Assert.That(w.Revision, Is.Zero);
            Assert.That(w.Suit, Is.EqualTo(SuitCondition.None)); Assert.That(w.Contamination, Is.Zero);
            Assert.That(w.RecoveryEpisode, Is.Zero); Assert.That(w.RecoveryAttempt, Is.Zero);
        }
        [TestCase(ImpactSeverity.Knockdown, Consciousness.Alert)]
        [TestCase(ImpactSeverity.Incapacitating, Consciousness.Unconscious)]
        public void WorkerImpactPreservesSuitAndContamination(ImpactSeverity impact, Consciousness expected)
        {
            var w = New(); w.SetEnvironment(0, SuitCondition.Intact, 37); w.Impact(1, impact, 100, 20);
            Assert.That(w.Snapshot.Suit, Is.EqualTo(SuitCondition.Intact)); Assert.That(w.Snapshot.Contamination, Is.EqualTo(37));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Down)); Assert.That(w.Snapshot.Consciousness, Is.EqualTo(expected));
            Assert.That(w.Snapshot.CanInteract, Is.False); Assert.That(w.Snapshot.RecoveryNotBefore, Is.EqualTo(120));
        }
        [Test] public void DuplicateImpactDoesNotExtendDeadlineOrChangeEpisode()
        {
            var w = Down(); var before = w.Snapshot;
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 100, 500), Is.EqualTo(WorkerResult.Duplicate));
            Assert.That(w.Snapshot.Revision, Is.EqualTo(before.Revision));
            Assert.That(w.Snapshot.RecoveryNotBefore, Is.EqualTo(100)); Assert.That(w.Snapshot.RecoveryEpisode, Is.EqualTo(1));
        }
        [Test] public void ImpactIdentityRejectsPayloadChangeGapAndTooOld()
        {
            var w = Down();
            Assert.That(w.Impact(1, ImpactSeverity.Incapacitating, 100, 0), Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 101, 0), Is.EqualTo(WorkerResult.PayloadMismatch));
            Assert.That(w.Impact(3, ImpactSeverity.Knockdown, 100, 0), Is.EqualTo(WorkerResult.SequenceGap));
            Assert.That(w.Impact(2, ImpactSeverity.Knockdown, 100, 0), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Impact(1, ImpactSeverity.Knockdown, 100, 0), Is.EqualTo(WorkerResult.TooOld));
            Assert.That(w.Snapshot.LastImpactSequence, Is.EqualTo(2));
        }
        [TestCase(0, 10, 0)] [TestCase(-1, 10, 0)] [TestCase(long.MaxValue, 10, 0)]
        [TestCase(1, -1, 0)] [TestCase(1, 10, -1)] [TestCase(1, 1, long.MaxValue)]
        public void InvalidWorkerImpactPreservesAllState(long seq, long delay, long now)
        {
            var w = New(); Assert.That(w.Impact(seq, ImpactSeverity.Knockdown, delay, now), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.CanInteract, Is.True); Assert.That(w.Snapshot.Revision, Is.Zero);
            Assert.That(w.Snapshot.LastImpactSequence, Is.Zero);
        }
        [Test] public void UnknownImpactAndInvalidConstructionFailExplicitly()
        {
            Assert.Throws<ArgumentException>(() => new WorkerState(Guid.Empty));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorkerState(Fixture.Id(1), 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => new WorkerState(Fixture.Id(1), 60001));
            Assert.That(New().Impact(1, (ImpactSeverity)99, 0, 0), Is.EqualTo(WorkerResult.InvalidInput));
        }
        [Test] public void MinorImpactCannotRestoreConsciousness()
        {
            var w = New(); w.Impact(1, ImpactSeverity.Incapacitating, 10, 0); w.Impact(2, ImpactSeverity.Knockdown, 0, 1);
            Assert.That(w.Snapshot.Consciousness, Is.EqualTo(Consciousness.Unconscious));
            Assert.That(w.BeginRecovery(2, w.Snapshot.Revision, 100000), Is.EqualTo(WorkerResult.RequiresAid));
        }
        [Test] public void ExplicitAidRequiresCurrentRevisionAndCreatesNewRecoveryEpisode()
        {
            var w = New(); w.Impact(1, ImpactSeverity.Incapacitating, 10, 0);
            Assert.That(w.Stabilize(0, 20, 10), Is.EqualTo(WorkerResult.RevisionConflict));
            Assert.That(w.Stabilize(1, 20, 10), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Snapshot.RecoveryNotBefore, Is.EqualTo(30)); Assert.That(w.Snapshot.RecoveryEpisode, Is.EqualTo(2));
            Assert.That(w.Stabilize(1, 20, 100), Is.EqualTo(WorkerResult.RevisionConflict));
            Assert.That(w.Stabilize(2, 20, 100), Is.EqualTo(WorkerResult.InvalidState));
            Assert.That(w.BeginRecovery(1, 2, 100), Is.EqualTo(WorkerResult.StaleRecovery));
        }
        [Test] public void InvalidAidCannotOverflowOrHeal()
        {
            var w = New(); w.Impact(1, ImpactSeverity.Incapacitating, 10, 0);
            Assert.That(w.Stabilize(1, 1, long.MaxValue), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Stabilize(1, -1, 10), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.Consciousness, Is.EqualTo(Consciousness.Unconscious)); Assert.That(w.Snapshot.Revision, Is.EqualTo(1));
        }
        [Test] public void WorkerRecoveryIsTwoPhaseAndHasExactDeadline()
        {
            var w = Down();
            Assert.That(w.BeginRecovery(1, 1, 99), Is.EqualTo(WorkerResult.TooEarly));
            Assert.That(w.BeginRecovery(1, 1, 100), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Recovering)); Assert.That(w.Snapshot.CanInteract, Is.False);
            Assert.That(w.ResolveRecovery(1, true), Is.EqualTo(WorkerResult.Applied)); Assert.That(w.Snapshot.CanInteract, Is.True);
            Assert.That(w.ResolveRecovery(1, true), Is.EqualTo(WorkerResult.StaleRecovery));
        }
        [Test] public void DuplicateRecoveryRequestDoesNotMintAnotherAttempt()
        {
            var w = Down(); w.BeginRecovery(1, 1, 100); var before = w.Snapshot;
            Assert.That(w.BeginRecovery(1, 1, 200), Is.EqualTo(WorkerResult.Duplicate));
            Assert.That(w.Snapshot.RecoveryAttempt, Is.EqualTo(1)); Assert.That(w.Snapshot.Revision, Is.EqualTo(before.Revision));
            Assert.That(w.Snapshot.RecoveryExpiresAt, Is.EqualTo(before.RecoveryExpiresAt));
        }
        [Test] public void BlockedRecoveryRequiresNewRequestRevision()
        {
            var w = Down(); w.BeginRecovery(1, 1, 100);
            Assert.That(w.ResolveRecovery(1, false), Is.EqualTo(WorkerResult.ClearanceBlocked));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Down));
            Assert.That(w.BeginRecovery(1, 1, 100), Is.EqualTo(WorkerResult.RevisionConflict));
            Assert.That(w.BeginRecovery(1, 3, 100), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.ResolveRecovery(1, true), Is.EqualTo(WorkerResult.StaleRecovery));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Recovering));
            Assert.That(w.ResolveRecovery(2, true), Is.EqualTo(WorkerResult.Applied));
        }
        [Test] public void AnotherImpactInvalidatesInFlightRecovery()
        {
            var w = Down(); w.BeginRecovery(1, 1, 100);
            w.Impact(2, ImpactSeverity.Incapacitating, 100, 100);
            Assert.That(w.ResolveRecovery(1, true), Is.EqualTo(WorkerResult.StaleRecovery));
            Assert.That(w.Snapshot.Consciousness, Is.EqualTo(Consciousness.Unconscious));
            Assert.That(w.Snapshot.RecoveryExpiresAt, Is.Zero);
        }
        [Test] public void RecoveryExpiryReturnsDownWithoutDependingOnAdvisorySignal()
        {
            var w = Down(); w.BeginRecovery(1, 1, 100);
            Assert.That(w.ExpireRecovery(5099), Is.EqualTo(WorkerResult.Duplicate));
            Assert.That(w.ExpireRecovery(5100), Is.EqualTo(WorkerResult.RecoveryExpired));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Down));
            Assert.That(w.ResolveRecovery(1, true), Is.EqualTo(WorkerResult.StaleRecovery));
            Assert.That(w.ExpireRecovery(9999), Is.EqualTo(WorkerResult.Duplicate));
        }
        [Test] public void RecoveryOverflowAndBackwardsSamplesAreNonMutating()
        {
            var w = Down(0);
            Assert.That(w.BeginRecovery(1, 1, long.MaxValue), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.Revision, Is.EqualTo(1));
            w.BeginRecovery(1, 1, 100);
            Assert.That(w.ExpireRecovery(99), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.BeginRecovery(1, 1, 99), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Recovering));
        }
        [TestCase(-1)] [TestCase(101)]
        public void InvalidContaminationDoesNotChangeCondition(int amount)
        {
            var w = New(); Assert.That(w.SetEnvironment(0, SuitCondition.Intact, amount), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.Revision, Is.Zero); Assert.That(w.Snapshot.Suit, Is.EqualTo(SuitCondition.None));
        }
        [Test] public void EnvironmentCannotOverwriteOrRepeatAgainstStaleRevision()
        {
            var w = Down();
            Assert.That(w.SetEnvironment(0, SuitCondition.Intact, 30), Is.EqualTo(WorkerResult.RevisionConflict));
            Assert.That(w.SetEnvironment(1, SuitCondition.Compromised, 30), Is.EqualTo(WorkerResult.Applied));
            Assert.That(w.SetEnvironment(2, SuitCondition.Compromised, 30), Is.EqualTo(WorkerResult.Duplicate));
            Assert.That(w.SetEnvironment(2, (SuitCondition)90, 30), Is.EqualTo(WorkerResult.InvalidInput));
            Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Down));
        }
        [Test] public void WorkerSnapshotsRemainDetachedAfterRecovery()
        {
            var w = Down(0); var old = w.Snapshot; w.BeginRecovery(1, 1, 0); w.ResolveRecovery(1, true);
            Assert.That(old.Posture, Is.EqualTo(Posture.Down)); Assert.That(w.Snapshot.Posture, Is.EqualTo(Posture.Upright));
        }
    }
}
