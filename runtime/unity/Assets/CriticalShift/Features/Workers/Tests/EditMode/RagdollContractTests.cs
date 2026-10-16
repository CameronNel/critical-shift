using System;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;

namespace CriticalShift.Features.Workers.Tests
{
    public sealed class RagdollContractTests
    {
        [Test] public void DefaultRagdollBudgetIsValid() { Assert.DoesNotThrow(() => new RagdollTuning().Validate()); }
        [TestCase(float.NaN)] [TestCase(float.PositiveInfinity)] [TestCase(0)] [TestCase(201)]
        public void InvalidPhysicalMassIsRejected(float mass)
        { Assert.Throws<ArgumentException>(() => new RagdollTuning { totalMass = mass }.Validate()); }
        [Test] public void UnboundedSolverMotionAndRecoveryBudgetsAreRejected()
        {
            Assert.Throws<ArgumentException>(() => new RagdollTuning { solverIterations = 100 }.Validate());
            Assert.Throws<ArgumentException>(() => new RagdollTuning { maximumSpeed = 100 }.Validate());
            Assert.Throws<ArgumentException>(() => new RagdollTuning { maximumImpactSpeed = 13 }.Validate());
            Assert.Throws<ArgumentException>(() => new RagdollTuning { blendSeconds = 0 }.Validate());
            Assert.Throws<ArgumentException>(() => new RagdollTuning { crawlSpeed = 2 }.Validate());
        }
        [Test] public void StationTicketCannotMatchAnotherPatientEpochOrImpactEpisode()
        {
            var epoch = Guid.NewGuid(); var patient = Guid.NewGuid(); var ticket = new WorkerRecoveryTicket(epoch, patient, 2);
            Assert.That(ticket.Matches(epoch, patient, 2), Is.True);
            Assert.That(ticket.Matches(Guid.NewGuid(), patient, 2), Is.False);
            Assert.That(ticket.Matches(epoch, Guid.NewGuid(), 2), Is.False);
            Assert.That(ticket.Matches(epoch, patient, 3), Is.False);
            Assert.Throws<ArgumentException>(() => new WorkerRecoveryTicket(Guid.Empty, patient, 2));
        }
    }
}
