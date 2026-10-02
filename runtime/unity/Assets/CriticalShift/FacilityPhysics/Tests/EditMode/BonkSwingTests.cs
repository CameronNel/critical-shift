using System;
using CriticalShift.Unity.Shared;
using NUnit.Framework;

namespace CriticalShift.FacilityPhysics.Tests
{
    public sealed class BonkSwingTests
    {
        [Test] public void ProceduralBonkHasAnticipationStrikeAndReturnsToRest()
        {
            var rest = BonkSwingPose.Sample(0); var windup = BonkSwingPose.Sample(.257f); var strike = BonkSwingPose.Sample(.457f); var end = BonkSwingPose.Sample(1);
            Assert.That(windup.Tilt, Is.LessThan(-60)); Assert.That(windup.Lift, Is.GreaterThan(.15));
            Assert.That(strike.Tilt, Is.GreaterThan(45)); Assert.That(strike.Forward, Is.GreaterThan(rest.Forward));
            Assert.That(end.Tilt, Is.Zero.Within(.001)); Assert.That(end.Lift, Is.Zero.Within(.001)); Assert.That(end.Forward, Is.Zero.Within(.001));
        }
        [Test] public void ProceduralBonkStaysBoundedAndContinuousAtEveryKeyframe()
        {
            foreach (float key in new[] { .257f, .457f, .64f })
                Assert.That(Math.Abs(BonkSwingPose.Sample(key - .0001f).Tilt - BonkSwingPose.Sample(key + .0001f).Tilt), Is.LessThan(.1));
            for (int i = 0; i <= 1000; i++)
            { var pose = BonkSwingPose.Sample(i / 1000f); Assert.That(Math.Abs(pose.Tilt), Is.LessThanOrEqualTo(75)); Assert.That(Math.Abs(pose.Lift), Is.LessThanOrEqualTo(.23)); }
        }
        [Test] public void ContactRecoilReturnsDirectlyToRestWithoutFurtherForwardSwing()
        {
            var contact = BonkSwingPose.Sample(.3f); var recovered = BonkSwingPose.Recover(.3f, .8f); var end = BonkSwingPose.Recover(.3f, 1);
            Assert.That(Math.Abs(recovered.Tilt), Is.LessThan(Math.Abs(contact.Tilt)));
            Assert.That(BonkSwingPose.Recover(.3f, .3f).Tilt, Is.EqualTo(contact.Tilt)); Assert.That(end.Tilt, Is.Zero.Within(.001));
        }
        [TestCase(float.NaN)] [TestCase(float.PositiveInfinity)] public void NonFiniteSwingPhaseIsRejected(float phase)
        { Assert.Throws<ArgumentException>(() => BonkSwingPose.Sample(phase)); }
    }
}
