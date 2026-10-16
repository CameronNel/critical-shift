using System;

namespace CriticalShift.Features.Workers.Unity
{
    [Serializable]
    public sealed class RagdollTuning
    {
        public float totalMass = 70, linearDamping = 0.2f, angularDamping = 1.2f;
        public float maximumSpeed = 12, maximumAngularSpeed = 18, maximumImpactSpeed = 7;
        public float settleSpeed = 0.8f, settleAngularSpeed = 2, settleSeconds = 0.3f;
        public float blendSeconds = 0.2f, crawlSpeed = 0.25f, crawlAcceleration = 0.8f;
        public int solverIterations = 12, solverVelocityIterations = 4;
        public bool selfCollision;
        public void Validate()
        {
            if (!Range(totalMass, 10, 200) || !Range(linearDamping, 0, 10) || !Range(angularDamping, 0, 20) ||
                !Range(maximumSpeed, 1, 30) || !Range(maximumAngularSpeed, 1, 40) || !Range(maximumImpactSpeed, 0, maximumSpeed) ||
                !Range(settleSpeed, 0.05f, 3) || !Range(settleAngularSpeed, 0.1f, 10) || !Range(settleSeconds, 0, 2) ||
                !Range(blendSeconds, 0.05f, 1) || !Range(crawlSpeed, 0, 0.5f) || !Range(crawlAcceleration, 0, 2) ||
                solverIterations < 1 || solverIterations > 32 || solverVelocityIterations < 1 || solverVelocityIterations > 16)
                throw new ArgumentException("Ragdoll tuning must have finite, bounded mass, motion, solver and recovery values.");
        }
        private static bool Range(float value, float minimum, float maximum) =>
            !float.IsNaN(value) && !float.IsInfinity(value) && value >= minimum && value <= maximum;
    }
}
