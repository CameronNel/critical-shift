using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeSuitSequenceTests
    {
        [Test]
        public void FullSequenceCompletesSafely()
        {
            var sequence = new GameObject("suit").AddComponent<PrototypeSuitSequence>();
            sequence.stepSeconds = 1f; Assert.IsTrue(sequence.Begin());
            sequence.TickForTest(4f);
            Assert.AreEqual(PrototypeSuitSequence.Step.Complete, sequence.CurrentStep);
            Assert.AreEqual(PrototypeSuitSequence.Result.SafeComplete, sequence.FinalResult);
            Object.DestroyImmediate(sequence.gameObject);
        }

        [Test]
        public void IntegrityCanBeSkippedButResultIsMarkedUnsafe()
        {
            var sequence = new GameObject("suit").AddComponent<PrototypeSuitSequence>();
            sequence.stepSeconds = 1f; sequence.Begin(); sequence.TickForTest(2f);
            Assert.AreEqual(PrototypeSuitSequence.Step.Integrity, sequence.CurrentStep);
            Assert.IsTrue(sequence.SkipIntegrity()); sequence.TickForTest(1f);
            Assert.AreEqual(PrototypeSuitSequence.Step.Complete, sequence.CurrentStep);
            Assert.AreEqual(PrototypeSuitSequence.Result.IntegritySkipped, sequence.FinalResult);
            Object.DestroyImmediate(sequence.gameObject);
        }
    }
}
