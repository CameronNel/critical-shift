using System;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Unity.Shared;
using NUnit.Framework;

namespace CriticalShift.Features.Workers.Tests
{
    public sealed class WorkerMechanicsTests
    {
        private static float[] Durations()
        { var result = new float[49]; for (int i = 0; i < result.Length; i++) result[i] = 1; result[(int)MovementClip.RUN] = 32f / 24; return result; }
        [Test]
        public void MixedStrideClockMatchesBlendedFloorDistance()
        {
            var weights = new float[49]; var lengths = Durations();
            weights[(int)MovementClip.WALK_F] = weights[(int)MovementClip.RUN] = 0.5f;
            double frequency = GaitCalibration.Frequency(1.015f, weights, lengths, MovementPose.Free);
            double floorSpeed = frequency * (0.5 * 0.63 * lengths[(int)MovementClip.WALK_F] +
                0.5 * 1.4 * lengths[(int)MovementClip.RUN] / 2);
            Assert.That(floorSpeed, Is.EqualTo(1.015).Within(0.000001));
        }
        [Test]
        public void DiagonalStrideClockMatchesVectorFloorDistance()
        {
            var weights = new float[49]; var lengths = Durations();
            weights[(int)MovementClip.WALK_F] = weights[(int)MovementClip.WALK_R] = 0.5f;
            double frequency = GaitCalibration.Frequency(0.5f, weights, lengths, MovementPose.Free);
            Assert.That(frequency * Math.Sqrt(0.315 * 0.315 + 0.2 * 0.2), Is.EqualTo(0.5).Within(0.000001));
        }
        [Test]
        public void ReanimationJoltResumesTheSlumpedCabinetLoop()
        {
            var selector = new MovementAnimationSelector(Durations()); var grounded = new MovementAnimationSample(0, 0, 0, true);
            selector.Step(grounded, 0); selector.TryPlayAction(MovementClip.REANIM_IDLE, 1);
            Assert.That(selector.TryPlayAction(MovementClip.REANIM_JOLT, 2, MovementClip.REANIM_IDLE), Is.True);
            selector.Step(grounded, 1);
            Assert.That(selector.Step(grounded, 0)[0].Clip, Is.EqualTo(MovementClip.REANIM_IDLE));
            Assert.That(selector.TryPlayAction(MovementClip.REANIM_JOLT, 2), Is.False);
            Assert.That(selector.StopAction(2), Is.True);
            Assert.That(selector.Step(grounded, 0)[0].Clip, Is.EqualTo(MovementClip.IDLE));
        }
        [Test]
        public void JumpAnticipationStartsWhileGroundedAndSurvivesTakeoff()
        {
            var selector = new MovementAnimationSelector(Durations()); selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            Assert.That(selector.BeginJump(), Is.True); Assert.That(selector.BeginJump(), Is.False);
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 0, true), 0.2f)[0].Clip, Is.EqualTo(MovementClip.JUMP));
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, 2, false), 0.4f)[0].Clip, Is.EqualTo(MovementClip.JUMP));
            Assert.That(selector.Step(new MovementAnimationSample(0, 0, -1, false), 0.6f)[0].Clip, Is.EqualTo(MovementClip.FALL));
        }
        [Test]
        public void CueCrossingFiresOnceEvenAcrossAFrameHitch()
        {
            var clock = new ActionCueClock(); clock.Begin(1, 0.4, false);
            Assert.That(clock.Step(0.39), Is.False); Assert.That(clock.Step(0.6), Is.True);
            Assert.That(clock.Step(0.1), Is.False); Assert.That(clock.Complete, Is.True); Assert.That(clock.Step(1), Is.False);
        }
        [Test]
        public void LoopCuesRemainSpacedByTheImportedDuration()
        {
            var clock = new ActionCueClock(); clock.Begin(1, 0.5, true);
            Assert.That(clock.Step(0.5), Is.True); Assert.That(clock.Step(0.9), Is.False);
            Assert.That(clock.Step(0.1), Is.True); Assert.That(clock.Complete, Is.False);
        }
        [Test]
        public void InteractionProfilesHaveValidContactsAndExplicitHauling()
        {
            foreach (SceneOperation operation in Enum.GetValues(typeof(SceneOperation)))
            {
                if (operation == SceneOperation.Push || operation == SceneOperation.Pull || operation == SceneOperation.Drag)
                { Assert.Throws<ArgumentOutOfRangeException>(() => WorkerActionPlan.For(operation)); continue; }
                var plan = WorkerActionPlan.For(operation); Assert.That(plan.Cue, Is.InRange(0, 1));
                Assert.That(MovementClipInfo.For(plan.Clip).Action, Is.True);
            }
        }
        [Test]
        public void CueAndGaitClocksRejectInvalidTiming()
        {
            var clock = new ActionCueClock();
            Assert.Throws<ArgumentOutOfRangeException>(() => clock.Begin(0, 0.5, false));
            Assert.Throws<ArgumentOutOfRangeException>(() => clock.Begin(1, double.NaN, false));
            clock.Begin(1, 0.5, false);
            Assert.Throws<ArgumentOutOfRangeException>(() => clock.Step(double.PositiveInfinity));
            Assert.Throws<ArgumentException>(() => GaitCalibration.Frequency(float.NaN, new float[49], Durations(), MovementPose.Free));
        }
    }
}
