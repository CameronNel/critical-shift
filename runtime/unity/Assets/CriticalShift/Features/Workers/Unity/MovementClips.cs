using System;

namespace CriticalShift.Features.Workers.Unity
{
    // Exact FBX take names from claude/character-rig, revision 6792f25.
    public enum MovementClip
    {
        IDLE, RUN, HOLD_SHOVEL, HOLD_PICKAXE, RUN_SHOVEL, RUN_PICKAXE,
        WALK_F, WALK_B, WALK_L, WALK_R, TURN_L, TURN_R, SPRINT, JUMP, FALL, LAND,
        PICKUP, CARRY_IDLE, CARRY_WALK, CARRY_RUN, PLACE, DROP, THROW_UNDER, THROW_OVER,
        PUSH_IDLE, PUSH_WALK, PULL_WALK, DRAG_BODY, PRESS_BUTTON, PULL_LEVER,
        TURN_VALVE, HOLD_VALVE, OPEN, INSERT, CONNECT_PORT, POINT, RADIO,
        STAGGER_F, STAGGER_B, STAGGER_L, STAGGER_R, GETUP_FRONT, GETUP_BACK,
        SUIT_UP, LOCKER_EXIT, REANIM_IDLE, REANIM_JOLT, REANIM_EXIT, SHOVEL_DIG
    }

    public readonly struct MovementClipInfo
    {
        public const int Count = 49;
        public bool Loop { get; }
        public bool Action { get; }
        public float MetresPerSecond { get; }
        public int Strides { get; }

        private MovementClipInfo(bool loop, bool action = false, float speed = 0, int strides = 0)
        {
            Loop = loop;
            Action = action;
            MetresPerSecond = speed;
            Strides = strides;
        }

        public static MovementClipInfo For(MovementClip clip)
        {
            switch (clip)
            {
                case MovementClip.WALK_F:
                case MovementClip.WALK_B: return new MovementClipInfo(true, speed: 0.63f, strides: 1);
                case MovementClip.WALK_L:
                case MovementClip.WALK_R: return new MovementClipInfo(true, speed: 0.40f, strides: 1);
                case MovementClip.RUN: return new MovementClipInfo(true, speed: 1.4f, strides: 2);
                case MovementClip.SPRINT: return new MovementClipInfo(true, speed: 2.6f, strides: 2);
                case MovementClip.RUN_SHOVEL:
                case MovementClip.RUN_PICKAXE: return new MovementClipInfo(true, speed: 1.2f, strides: 1);
                case MovementClip.CARRY_WALK:
                case MovementClip.PULL_WALK: return new MovementClipInfo(true, speed: 0.50f, strides: 1);
                case MovementClip.CARRY_RUN: return new MovementClipInfo(true, speed: 0.96f, strides: 1);
                case MovementClip.PUSH_WALK: return new MovementClipInfo(true, speed: 0.60f, strides: 1);
                case MovementClip.DRAG_BODY: return new MovementClipInfo(true, speed: 0.33f, strides: 1);
                case MovementClip.IDLE:
                case MovementClip.HOLD_SHOVEL:
                case MovementClip.HOLD_PICKAXE:
                case MovementClip.CARRY_IDLE:
                case MovementClip.PUSH_IDLE:
                case MovementClip.TURN_L:
                case MovementClip.TURN_R:
                case MovementClip.FALL: return new MovementClipInfo(true);
                case MovementClip.JUMP:
                case MovementClip.LAND: return new MovementClipInfo(false);
                case MovementClip.TURN_VALVE:
                case MovementClip.HOLD_VALVE:
                case MovementClip.RADIO:
                case MovementClip.REANIM_IDLE:
                case MovementClip.SHOVEL_DIG: return new MovementClipInfo(true, action: true);
                default:
                    if ((int)clip < 0 || (int)clip >= Count) throw new ArgumentOutOfRangeException(nameof(clip));
                    return new MovementClipInfo(false, action: true);
            }
        }
    }

    // These are visual contexts supplied by the custody/tool/physical owner.
    public enum MovementPose { Free, Carry, Shovel, Pickaxe, Push, Pull, Drag }

    public readonly struct MovementAnimationSample
    {
        public float Right { get; }
        public float Forward { get; }
        public float Vertical { get; }
        public float YawDegreesPerSecond { get; }
        public bool Grounded { get; }
        public bool Animated { get; }
        public MovementPose Pose { get; }
        public float Speed => (float)Math.Sqrt((double)Right * Right + (double)Forward * Forward);

        // Unity local axes: +X right, +Z forward, +Y up; positive yaw turns right.
        public MovementAnimationSample(float right, float forward, float vertical, bool grounded,
            MovementPose pose = MovementPose.Free, float yawDegreesPerSecond = 0, bool animated = true)
        {
            if (!Finite(right) || !Finite(forward) || !Finite(vertical) || !Finite(yawDegreesPerSecond))
                throw new ArgumentOutOfRangeException(nameof(right), "Motion values must be finite.");
            if (Math.Abs(right) > 1000 || Math.Abs(forward) > 1000 || Math.Abs(vertical) > 1000 ||
                Math.Abs(yawDegreesPerSecond) > 10000 || !Enum.IsDefined(typeof(MovementPose), pose))
                throw new ArgumentOutOfRangeException(nameof(pose), "Motion exceeds presentation bounds.");
            Right = right; Forward = forward; Vertical = vertical;
            Grounded = grounded; Pose = pose; YawDegreesPerSecond = yawDegreesPerSecond; Animated = animated;
        }

        internal static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);
    }
}
