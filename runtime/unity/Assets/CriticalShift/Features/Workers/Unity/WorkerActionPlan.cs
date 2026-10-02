using System;
using CriticalShift.Unity.Shared;

namespace CriticalShift.Features.Workers.Unity
{
    public readonly struct WorkerActionPlan
    {
        public MovementClip Clip { get; }
        public float Cue { get; }
        public bool Repeat => MovementClipInfo.For(Clip).Loop;
        private WorkerActionPlan(MovementClip clip, float cue) { Clip = clip; Cue = cue; }
        // Provisional contact defaults for the unfinished takes; the worker Inspector supplies final cue overrides.
        public static WorkerActionPlan For(SceneOperation operation)
        {
            switch (operation)
            {
                case SceneOperation.Grab: return new WorkerActionPlan(MovementClip.PICKUP, 12f / 30);
                case SceneOperation.Release: return new WorkerActionPlan(MovementClip.DROP, 2f / 18);
                case SceneOperation.Place: return new WorkerActionPlan(MovementClip.PLACE, 18f / 30);
                case SceneOperation.ThrowUnder: return new WorkerActionPlan(MovementClip.THROW_UNDER, 14f / 28);
                case SceneOperation.ThrowOver: return new WorkerActionPlan(MovementClip.THROW_OVER, 12f / 26);
                case SceneOperation.Button: return new WorkerActionPlan(MovementClip.PRESS_BUTTON, 9f / 20);
                case SceneOperation.Lever: return new WorkerActionPlan(MovementClip.PULL_LEVER, 13f / 26);
                case SceneOperation.ValveTurn: return new WorkerActionPlan(MovementClip.TURN_VALVE, 0.5f);
                case SceneOperation.ValveHold: return new WorkerActionPlan(MovementClip.HOLD_VALVE, 0.5f);
                case SceneOperation.Open: return new WorkerActionPlan(MovementClip.OPEN, 9f / 26);
                case SceneOperation.Insert: return new WorkerActionPlan(MovementClip.INSERT, 12f / 26);
                case SceneOperation.Connect: return new WorkerActionPlan(MovementClip.CONNECT_PORT, 18f / 30);
                case SceneOperation.Point: return new WorkerActionPlan(MovementClip.POINT, 12f / 22);
                case SceneOperation.Radio: return new WorkerActionPlan(MovementClip.RADIO, 0);
                case SceneOperation.Dig: return new WorkerActionPlan(MovementClip.SHOVEL_DIG, 0.65f);
                case SceneOperation.Suit: return new WorkerActionPlan(MovementClip.SUIT_UP, 0.85f);
                case SceneOperation.LockerExit: return new WorkerActionPlan(MovementClip.LOCKER_EXIT, 0);
                case SceneOperation.Reanimation: return new WorkerActionPlan(MovementClip.PRESS_BUTTON, 0.5f);
                case SceneOperation.Help: return new WorkerActionPlan(MovementClip.CONNECT_PORT, 0.6f);
                default: throw new ArgumentOutOfRangeException(nameof(operation), "Hauling starts directly under custody.");
            }
        }
    }

    public sealed class ActionCueClock
    {
        public double Time { get; private set; }
        private double nextCue, duration;
        private bool repeat, complete;
        public bool Complete => complete;
        public void Begin(double seconds, double cue, bool repeats)
        {
            if (double.IsNaN(seconds) || double.IsInfinity(seconds) || seconds <= 0 ||
                double.IsNaN(cue) || cue < 0 || cue > 1) throw new ArgumentOutOfRangeException(nameof(seconds));
            duration = seconds; nextCue = seconds * cue; Time = 0; repeat = repeats; complete = false;
        }
        public bool Step(double delta)
        {
            if (double.IsNaN(delta) || double.IsInfinity(delta) || delta < 0 || delta > 1)
                throw new ArgumentOutOfRangeException(nameof(delta));
            if (complete) return false;
            Time += delta;
            bool fire = Time >= nextCue;
            if (fire) nextCue = repeat ? nextCue + duration : double.PositiveInfinity;
            if (!repeat && Time >= duration) complete = true;
            return fire;
        }
    }
}
