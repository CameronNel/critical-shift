using System;

namespace CriticalShift.Unity.Shared
{
    // Presentation keyframes only; the host's action clock owns hit/cooldown eligibility.
    public readonly struct BonkSwingPose
    {
        public readonly float Lift, Forward, Tilt, Twist;
        private BonkSwingPose(float lift, float forward, float tilt, float twist)
        { Lift = lift; Forward = forward; Tilt = tilt; Twist = twist; }
        public static BonkSwingPose Sample(float phase)
        {
            if (float.IsNaN(phase) || float.IsInfinity(phase)) throw new ArgumentException("Swing phase must be finite.");
            phase = Math.Max(0, Math.Min(1, phase));
            var rest = new BonkSwingPose(0, 0, 0, 0); var ready = new BonkSwingPose(.22f, -.08f, -75, -12);
            var strike = new BonkSwingPose(-.16f, .12f, 58, 16); var follow = new BonkSwingPose(-.2f, .05f, 70, 10);
            if (phase <= .257f) return Blend(rest, ready, phase / .257f);
            if (phase <= .457f) return Blend(ready, strike, (phase - .257f) / .2f);
            if (phase <= .64f) return Blend(strike, follow, (phase - .457f) / .183f);
            return Blend(follow, rest, (phase - .64f) / .36f);
        }
        public static BonkSwingPose Recover(float contactPhase, float phase)
        {
            if (float.IsNaN(contactPhase) || float.IsInfinity(contactPhase) || float.IsNaN(phase) || float.IsInfinity(phase)) throw new ArgumentException("Swing phase must be finite.");
            contactPhase = Math.Max(0, Math.Min(.999f, contactPhase));
            float t = Math.Max(0, Math.Min(1, (phase - contactPhase) / (1 - contactPhase)));
            return Blend(Sample(contactPhase), new BonkSwingPose(0, 0, 0, 0), t);
        }
        private static BonkSwingPose Blend(BonkSwingPose a, BonkSwingPose b, float t)
        {
            t = t * t * (3 - 2 * t);
            return new BonkSwingPose(a.Lift + (b.Lift - a.Lift) * t, a.Forward + (b.Forward - a.Forward) * t,
                a.Tilt + (b.Tilt - a.Tilt) * t, a.Twist + (b.Twist - a.Twist) * t);
        }
    }
}
