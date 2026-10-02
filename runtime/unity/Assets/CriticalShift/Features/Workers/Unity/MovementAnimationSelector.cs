using System;

namespace CriticalShift.Features.Workers.Unity
{
    public readonly struct MovementClipWeight
    {
        public MovementClip Clip { get; }
        public float Weight { get; }
        public float Rate { get; }
        public MovementClipWeight(MovementClip clip, float weight, float rate = 1)
        { Clip = clip; Weight = weight; Rate = rate; }
    }

    // At most four simultaneous target clips; no per-frame arrays or lists.
    public struct MovementAnimationBlend
    {
        private MovementClipWeight a, b, c, d;
        public int Count { get; private set; }
        public MovementClipWeight this[int index]
        {
            get
            {
                if (index < 0 || index >= Count) throw new ArgumentOutOfRangeException(nameof(index));
                switch (index) { case 0: return a; case 1: return b; case 2: return c; default: return d; }
            }
        }
        internal void Add(MovementClip clip, float weight, float rate = 1)
        {
            if (weight <= 0) return;
            var entry = new MovementClipWeight(clip, weight, rate);
            switch (Count)
            {
                case 0: a = entry; break; case 1: b = entry; break;
                case 2: c = entry; break; case 3: d = entry; break;
                default: throw new InvalidOperationException("Movement blend exceeds four targets.");
            }
            Count++;
        }
    }

    // Owns visual transition history only. Never integrates transforms or commits gameplay.
    public sealed class MovementAnimationSelector
    {
        private readonly float[] durations;
        private bool wasAirborne, wasAnimated;
        private float airTime, landingTime, actionTime, jumpTime = -1;
        private MovementClip? action, resumeAction;
        private ulong lastActionSequence;
        public MovementClip? ActiveAction => action;
        public ulong ActionSequence => lastActionSequence;
        public const float MoveDeadzone = 0.02f;
        public const float FullMovementBlendSpeed = 0.20f;

        public MovementAnimationSelector(float[] clipDurations)
        {
            if (clipDurations == null || clipDurations.Length != MovementClipInfo.Count)
                throw new ArgumentException("Supply all 49 imported clip lengths.", nameof(clipDurations));
            durations = (float[])clipDurations.Clone();
            foreach (float length in durations)
                if (!MovementAnimationSample.Finite(length) || length <= 0)
                    throw new ArgumentException("Clip lengths must be finite and positive.", nameof(clipDurations));
        }

        // Sequence is increasing within this worker binding. Duplicate/old presentation events do not restart a clip.
        public bool TryPlayAction(MovementClip clip, ulong sequence, MovementClip? resume = null)
        {
            if (resume.HasValue && (!MovementClipInfo.For(resume.Value).Action || !MovementClipInfo.For(resume.Value).Loop))
                throw new ArgumentException("A resumed action must be a held loop.", nameof(resume));
            if (!MovementClipInfo.For(clip).Action || !wasAnimated || wasAirborne ||
                sequence == 0 || sequence <= lastActionSequence) return false;
            lastActionSequence = sequence;
            action = clip;
            resumeAction = resume;
            actionTime = 0;
            landingTime = 0;
            return true;
        }

        public bool StopAction(ulong sequence)
        {
            if (sequence != lastActionSequence || !action.HasValue) return false;
            action = null;
            resumeAction = null;
            return true;
        }

        public bool BeginJump(bool allowCoyote = false)
        {
            if (!wasAnimated || (wasAirborne && !allowCoyote) || action.HasValue || jumpTime >= 0) return false;
            jumpTime = 0;
            landingTime = 0;
            return true;
        }

        public void CancelJump() { jumpTime = -1; }

        public void Reset()
        {
            wasAirborne = wasAnimated = false;
            airTime = landingTime = actionTime = 0;
            action = null;
            resumeAction = null;
            jumpTime = -1;
            lastActionSequence = 0;
        }

        public MovementAnimationBlend Step(MovementAnimationSample sample, float deltaTime)
        {
            if (!MovementAnimationSample.Finite(deltaTime) || deltaTime < 0 || deltaTime > 1)
                throw new ArgumentOutOfRangeException(nameof(deltaTime), "Use a finite frame delta between 0 and 1 second.");
            if (!sample.Animated)
            {
                wasAirborne = wasAnimated = false;
                airTime = landingTime = 0;
                action = null;
                resumeAction = null;
                jumpTime = -1;
                return default;
            }
            bool first = !wasAnimated;
            wasAnimated = true;
            if (jumpTime >= 0)
            {
                jumpTime += deltaTime;
                if (jumpTime <= durations[(int)MovementClip.JUMP])
                {
                    wasAirborne = !sample.Grounded;
                    if (wasAirborne) airTime += deltaTime;
                    return Single(MovementClip.JUMP);
                }
                jumpTime = -1;
            }
            if (!sample.Grounded)
            {
                if (!wasAirborne) airTime = 0;
                wasAirborne = true;
                airTime += deltaTime;
                action = null;
                resumeAction = null;
                landingTime = 0;
                return Single(sample.Vertical > 0.1f && airTime < durations[(int)MovementClip.JUMP]
                    ? MovementClip.JUMP : MovementClip.FALL);
            }
            bool landed = wasAirborne && !first && airTime >= 0.1f;
            wasAirborne = false;
            airTime = 0;
            if (landed) landingTime = durations[(int)MovementClip.LAND];
            if (action.HasValue)
            {
                if (MovementClipInfo.For(action.Value).Loop || actionTime < durations[(int)action.Value])
                {
                    actionTime += deltaTime;
                    return Single(action.Value);
                }
                action = resumeAction;
                resumeAction = null;
                actionTime = 0;
                if (action.HasValue) return Single(action.Value);
            }
            if (landingTime > 0)
            {
                landingTime = Math.Max(0, landingTime - deltaTime);
                return Single(MovementClip.LAND);
            }
            return Locomotion(sample);
        }

        private static MovementAnimationBlend Single(MovementClip clip)
        { var blend = new MovementAnimationBlend(); blend.Add(clip, 1); return blend; }

        private static float Rate(MovementClip clip, float speed)
        {
            float authoredSpeed = MovementClipInfo.For(clip).MetresPerSecond;
            return authoredSpeed > 0 ? Math.Min(2.5f, Math.Max(0, speed / authoredSpeed)) : 1;
        }

        private static MovementAnimationBlend Locomotion(MovementAnimationSample sample)
        {
            float speed = sample.Speed;
            if (sample.Pose == MovementPose.Free && speed <= MoveDeadzone)
            {
                if (Math.Abs(sample.YawDegreesPerSecond) < 12) return Single(MovementClip.IDLE);
                var turning = new MovementAnimationBlend();
                turning.Add(sample.YawDegreesPerSecond < 0 ? MovementClip.TURN_L : MovementClip.TURN_R,
                    1, Math.Min(2.5f, Math.Abs(sample.YawDegreesPerSecond) / 48f));
                return turning;
            }
            switch (sample.Pose)
            {
                case MovementPose.Carry: return Pair(speed, MovementClip.CARRY_IDLE, MovementClip.CARRY_WALK, MovementClip.CARRY_RUN);
                case MovementPose.Shovel: return Pair(speed, MovementClip.HOLD_SHOVEL, MovementClip.RUN_SHOVEL, MovementClip.RUN_SHOVEL);
                case MovementPose.Pickaxe: return Pair(speed, MovementClip.HOLD_PICKAXE, MovementClip.RUN_PICKAXE, MovementClip.RUN_PICKAXE);
                case MovementPose.Push: return Pair(speed, MovementClip.PUSH_IDLE, MovementClip.PUSH_WALK, MovementClip.PUSH_WALK);
                // No pull/drag idle is authored. Freeze the moving pose at zero speed, keeping the grip.
                case MovementPose.Pull: return MovingOnly(speed, MovementClip.PULL_WALK);
                case MovementPose.Drag: return MovingOnly(speed, MovementClip.DRAG_BODY);
                default: return Directional(sample, speed);
            }
        }

        private static MovementAnimationBlend MovingOnly(float speed, MovementClip clip)
        { var blend = new MovementAnimationBlend(); blend.Add(clip, 1, Rate(clip, speed)); return blend; }

        private static MovementAnimationBlend Pair(float speed, MovementClip idle, MovementClip walk, MovementClip run)
        {
            var blend = new MovementAnimationBlend();
            float moving = speed <= MoveDeadzone ? 0 : Math.Min(1, speed / FullMovementBlendSpeed);
            blend.Add(idle, 1 - moving);
            AddGaits(ref blend, walk, run, speed, moving);
            return blend;
        }

        private static void AddGaits(ref MovementAnimationBlend blend, MovementClip walk, MovementClip run,
            float speed, float weight)
        {
            if (walk == run) { blend.Add(walk, weight, Rate(walk, speed)); return; }
            float low = MovementClipInfo.For(walk).MetresPerSecond;
            float high = MovementClipInfo.For(run).MetresPerSecond;
            float mix = Math.Min(1, Math.Max(0, (speed - low) / (high - low)));
            blend.Add(walk, weight * (1 - mix), Rate(walk, speed));
            blend.Add(run, weight * mix, Rate(run, speed));
        }

        private static MovementAnimationBlend Directional(MovementAnimationSample sample, float speed)
        {
            var blend = new MovementAnimationBlend();
            if (speed <= MoveDeadzone) return Single(MovementClip.IDLE);
            float moving = Math.Min(1, speed / FullMovementBlendSpeed);
            float side = Math.Abs(sample.Right) / (Math.Abs(sample.Right) + Math.Abs(sample.Forward));
            blend.Add(MovementClip.IDLE, 1 - moving);
            var strafe = sample.Right < 0 ? MovementClip.WALK_L : MovementClip.WALK_R;
            blend.Add(strafe, moving * side, Rate(strafe, speed));
            float forwardWeight = moving * (1 - side);
            if (sample.Forward < 0) blend.Add(MovementClip.WALK_B, forwardWeight, Rate(MovementClip.WALK_B, speed));
            else if (speed < 1.4f) AddGaits(ref blend, MovementClip.WALK_F, MovementClip.RUN, speed, forwardWeight);
            else AddGaits(ref blend, MovementClip.RUN, MovementClip.SPRINT, speed, forwardWeight);
            return blend;
        }
    }
}
