using System;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;

namespace CriticalShift.Features.Workers.Tests
{
    public sealed class MovementAnimationTests
    {
        private static MovementAnimationSelector Create()
        {
            var lengths = new float[MovementClipInfo.Count];
            for (int i = 0; i < lengths.Length; i++) lengths[i] = 1;
            return new MovementAnimationSelector(lengths);
        }

        private static float Weight(MovementAnimationBlend blend, MovementClip clip)
        {
            for (int i = 0; i < blend.Count; i++) if (blend[i].Clip == clip) return blend[i].Weight;
            return 0;
        }

        [TestCase(0, 0.63f, MovementClip.WALK_F)]
        [TestCase(0, -0.63f, MovementClip.WALK_B)]
        [TestCase(-0.40f, 0, MovementClip.WALK_L)]
        [TestCase(0.40f, 0, MovementClip.WALK_R)]
        [TestCase(0, 1.4f, MovementClip.RUN)]
        [TestCase(0, 2.6f, MovementClip.SPRINT)]
        public void AuthoredVelocitySelectsMatchingGait(float right, float forward, MovementClip clip)
        {
            var blend = Create().Step(new MovementAnimationSample(right, forward, 0, true), 0.02f);
            Assert.That(blend.Count, Is.EqualTo(1));
            Assert.That(blend[0].Clip, Is.EqualTo(clip));
            Assert.That(blend[0].Rate, Is.EqualTo(1).Within(0.0001));
        }

        [Test]
        public void ForwardGaitsBlendAtMeasuredMidpoints()
        {
            var selector = Create();
            var walkRun = selector.Step(new MovementAnimationSample(0, (0.63f + 1.4f) / 2, 0, true), 0);
            Assert.That(Weight(walkRun, MovementClip.WALK_F), Is.EqualTo(0.5f).Within(0.0001));
            Assert.That(Weight(walkRun, MovementClip.RUN), Is.EqualTo(0.5f).Within(0.0001));
            var runSprint = selector.Step(new MovementAnimationSample(0, 2, 0, true), 0);
            Assert.That(Weight(runSprint, MovementClip.RUN), Is.EqualTo(0.5f).Within(0.0001));
            Assert.That(Weight(runSprint, MovementClip.SPRINT), Is.EqualTo(0.5f).Within(0.0001));
        }

        [Test]
        public void DiagonalMovementBlendsSidesAndMatchesActualSpeed()
        {
            var sample = new MovementAnimationSample(-0.3f, 0.3f, 0, true);
            var blend = Create().Step(sample, 0.02f);
            Assert.That(Weight(blend, MovementClip.WALK_L), Is.EqualTo(0.5f));
            Assert.That(Weight(blend, MovementClip.WALK_F), Is.EqualTo(0.5f));
            Assert.That(blend[0].Rate, Is.EqualTo(sample.Speed / 0.4f).Within(0.0001));
        }

        [Test]
        public void BlendsStayNormalizedAcrossVelocityGrid()
        {
            var selector = Create();
            foreach (MovementPose pose in Enum.GetValues(typeof(MovementPose)))
                for (int x = -20; x <= 20; x++)
                    for (int z = -20; z <= 20; z++)
                    {
                        var blend = selector.Step(new MovementAnimationSample(x * 0.1f, z * 0.1f, 0, true, pose), 0);
                        float total = 0;
                        for (int i = 0; i < blend.Count; i++)
                        {
                            total += blend[i].Weight;
                            Assert.That(blend[i].Rate, Is.InRange(0, 2.5f));
                        }
                        Assert.That(total, Is.EqualTo(1).Within(0.0001));
                        Assert.That(blend.Count, Is.InRange(1, 4));
                    }
        }

        [TestCase(-48, MovementClip.TURN_L)]
        [TestCase(48, MovementClip.TURN_R)]
        public void TurnDirectionUsesUnityYawConvention(float yaw, MovementClip clip)
        {
            var blend = Create().Step(new MovementAnimationSample(0, 0, 0, true, yawDegreesPerSecond: yaw), 0.02f);
            Assert.That(blend[0].Clip, Is.EqualTo(clip));
            Assert.That(blend[0].Rate, Is.EqualTo(1));
        }

        [TestCase(MovementPose.Carry, MovementClip.CARRY_IDLE, MovementClip.CARRY_RUN, 0.96f)]
        [TestCase(MovementPose.Shovel, MovementClip.HOLD_SHOVEL, MovementClip.RUN_SHOVEL, 1.2f)]
        [TestCase(MovementPose.Pickaxe, MovementClip.HOLD_PICKAXE, MovementClip.RUN_PICKAXE, 1.2f)]
        [TestCase(MovementPose.Push, MovementClip.PUSH_IDLE, MovementClip.PUSH_WALK, 0.60f)]
        public void ContextPreservesGripAtRestAndInMotion(MovementPose pose, MovementClip idle, MovementClip gait, float speed)
        {
            var selector = Create();
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true, pose), 0)[0].Clip, Is.EqualTo(idle));
            Assert.That(selector.Step(new MovementAnimationSample(0, speed, 0, true, pose), 0)[0].Clip, Is.EqualTo(gait));
        }

        [TestCase(MovementPose.Pull, MovementClip.PULL_WALK)]
        [TestCase(MovementPose.Drag, MovementClip.DRAG_BODY)]
        public void MissingIdleFreezesHaulingPose(MovementPose pose, MovementClip clip)
        {
            var blend = Create().Step(new MovementAnimationSample(0, 0, 0, true, pose), 0.02f);
            Assert.That(blend[0].Clip, Is.EqualTo(clip));
            Assert.That(blend[0].Rate, Is.Zero);
        }

        [Test]
        public void JumpFallLandAndImmediateNewJumpFollowPhysicalObservations()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.02f);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 3, false), 0.2f)[0].Clip, Is.EqualTo(MovementClip.JUMP));
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, -1, false), 0.2f)[0].Clip, Is.EqualTo(MovementClip.FALL));
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.1f)[0].Clip, Is.EqualTo(MovementClip.LAND));
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 2, false), 0.1f)[0].Clip, Is.EqualTo(MovementClip.JUMP));
        }

        [Test]
        public void TinyGroundContactGapDoesNotStartLanding()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.02f);
            selector.Step(new MovementAnimationSample(0, 0, -0.1f, false), 0.02f);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.02f)[0].Clip, Is.EqualTo(MovementClip.IDLE));
        }

        [Test]
        public void LandingFinishesAndReturnsToCurrentCarryContext()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, -2, false), 0.2f);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.5f)[0].Clip, Is.EqualTo(MovementClip.LAND));
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.5f);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true, MovementPose.Carry), 0.02f)[0].Clip,
                Is.EqualTo(MovementClip.CARRY_IDLE));
        }

        [Test]
        public void ReplayedActionCannotRestartOrStopItsReplacement()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            Assert.That(selector.TryPlayAction(MovementClip.PICKUP, 1), Is.True);
            Assert.That(selector.TryPlayAction(MovementClip.PICKUP, 1), Is.False);
            Assert.That(selector.TryPlayAction(MovementClip.RADIO, 2), Is.True);
            Assert.That(selector.StopAction(1), Is.False);
            Assert.That(selector.ActiveAction, Is.EqualTo(MovementClip.RADIO));
            Assert.That(selector.StopAction(2), Is.True);
        }

        [Test]
        public void OneShotEndsButHeldActionWaitsForExplicitRelease()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            selector.TryPlayAction(MovementClip.PICKUP, 1);
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 1);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true, MovementPose.Carry), 0)[0].Clip,
                Is.EqualTo(MovementClip.CARRY_IDLE));
            selector.TryPlayAction(MovementClip.TURN_VALVE, 2);
            for (int i = 0; i < 10; i++) selector.Step(new MovementAnimationSample(0, 0, 0, true), 1);
            Assert.That(selector.ActiveAction, Is.EqualTo(MovementClip.TURN_VALVE));
        }

        [Test]
        public void PhysicsSuspensionCancelsActionWithoutAcceptingLateReplay()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            selector.TryPlayAction(MovementClip.GETUP_BACK, 10);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true, animated: false), 0).Count, Is.Zero);
            Assert.That(selector.ActiveAction, Is.Null);
            Assert.That(selector.TryPlayAction(MovementClip.GETUP_BACK, 11), Is.False);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true), 0)[0].Clip, Is.EqualTo(MovementClip.IDLE));
            Assert.That(selector.TryPlayAction(MovementClip.GETUP_BACK, 10), Is.False);
            selector.Reset();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            Assert.That(selector.TryPlayAction(MovementClip.GETUP_BACK, 1), Is.True);
        }

        [Test]
        public void AirborneMotionInterruptsActionAndRejectsNewAction()
        {
            var selector = Create();
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            selector.TryPlayAction(MovementClip.SHOVEL_DIG, 1);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, -2, false), 0.2f)[0].Clip, Is.EqualTo(MovementClip.FALL));
            Assert.That(selector.ActiveAction, Is.Null);
            Assert.That(selector.TryPlayAction(MovementClip.RADIO, 2), Is.False);
        }

        [Test]
        public void InvalidSamplesAndTimingAreRejected()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => new MovementAnimationSample(float.NaN, 0, 0, true));
            Assert.Throws<ArgumentOutOfRangeException>(() => new MovementAnimationSample(0, float.PositiveInfinity, 0, true));
            Assert.Throws<ArgumentOutOfRangeException>(() => new MovementAnimationSample(0, 0, 0, true, (MovementPose)99));
            var selector = Create();
            Assert.Throws<ArgumentOutOfRangeException>(() => selector.Step(default, -1));
            Assert.Throws<ArgumentOutOfRangeException>(() => selector.Step(default, float.NaN));
            Assert.Throws<ArgumentOutOfRangeException>(() => selector.Step(default, 2));
            Assert.Throws<ArgumentException>(() => new MovementAnimationSelector(new float[49]));
            Assert.Throws<ArgumentOutOfRangeException>(() => MovementClipInfo.For((MovementClip)99));
        }

        [Test]
        public void ClipCatalogueHasExactly49ValidStableIds()
        {
            Assert.That(Enum.GetValues(typeof(MovementClip)).Length, Is.EqualTo(49));
            for (int i = 0; i < 49; i++) Assert.DoesNotThrow(() => MovementClipInfo.For((MovementClip)i));
            Assert.That(MovementClipInfo.For(MovementClip.REANIM_IDLE).Loop, Is.True);
            Assert.That(MovementClipInfo.For(MovementClip.REANIM_JOLT).Loop, Is.False);
            Assert.That(MovementClipInfo.For(MovementClip.GETUP_FRONT).Action, Is.True);
        }
    }
}
