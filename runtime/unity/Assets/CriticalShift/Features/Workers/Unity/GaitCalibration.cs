using System;

namespace CriticalShift.Features.Workers.Unity
{
    // A common phase must divide measured speed by blended stride distance, not average clip frequencies.
    public static class GaitCalibration
    {
        public static double Frequency(float speed, float[] weights, float[] lengths, MovementPose pose)
        {
            if (!MovementAnimationSample.Finite(speed) || speed < 0 || weights == null || lengths == null ||
                weights.Length != MovementClipInfo.Count || lengths.Length != MovementClipInfo.Count)
                throw new ArgumentException("Supply a finite speed and complete gait tables.");
            double x = 0, z = 0;
            for (int i = 0; i < weights.Length; i++)
            {
                var clip = (MovementClip)i;
                var info = MovementClipInfo.For(clip);
                if (info.Strides == 0 || weights[i] <= 0) continue;
                if (!MovementAnimationSample.Finite(lengths[i]) || lengths[i] <= 0)
                    throw new ArgumentException("Gait durations must be positive.");
                double distance = weights[i] * info.MetresPerSecond * lengths[i] / info.Strides;
                if (pose == MovementPose.Free && clip == MovementClip.WALK_L) x -= distance;
                else if (pose == MovementPose.Free && clip == MovementClip.WALK_R) x += distance;
                else z += distance * (clip == MovementClip.WALK_B ? -1 : 1);
            }
            double stride = Math.Sqrt(x * x + z * z);
            return stride > 0.000001 ? speed / stride : 0;
        }
    }
}
