using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    // No crouch take is authored. Lower the hips after playback and keep both foot targets using two-bone IK.
    public sealed class WorkerCrouchPose : MonoBehaviour
    {
        [SerializeField] private Transform hips, leftThigh, leftShin, leftFoot, rightThigh, rightShin, rightFoot;
        public void Apply(float lowering)
        {
            if (lowering <= 0 || hips == null || leftThigh == null || leftShin == null || leftFoot == null ||
                rightThigh == null || rightShin == null || rightFoot == null) return;
            Vector3 left = leftFoot.position, right = rightFoot.position;
            Quaternion leftRotation = leftFoot.rotation, rightRotation = rightFoot.rotation;
            float limit = Mathf.Min(Vector3.Distance(leftThigh.position, leftShin.position), Vector3.Distance(rightThigh.position, rightShin.position));
            hips.position -= Vector3.up * Mathf.Min(lowering, limit);
            Solve(leftThigh, leftShin, leftFoot, left, transform.forward);
            Solve(rightThigh, rightShin, rightFoot, right, transform.forward);
            leftFoot.rotation = leftRotation; rightFoot.rotation = rightRotation;
        }
        private static void Solve(Transform upper, Transform lower, Transform foot, Vector3 target, Vector3 pole)
        {
            Vector3 origin = upper.position;
            float a = Vector3.Distance(origin, lower.position), b = Vector3.Distance(lower.position, foot.position);
            float distance = Mathf.Clamp(Vector3.Distance(origin, target), Mathf.Abs(a - b) + 0.001f, a + b - 0.001f);
            if (a < 0.001f || b < 0.001f || distance < 0.001f) return;
            Vector3 direction = (target - origin).normalized;
            Vector3 bend = Vector3.ProjectOnPlane(pole, direction).normalized;
            float along = (a * a + distance * distance - b * b) / (2 * distance);
            Vector3 knee = origin + direction * along + bend * Mathf.Sqrt(Mathf.Max(0, a * a - along * along));
            upper.rotation = Quaternion.FromToRotation(lower.position - origin, knee - origin) * upper.rotation;
            lower.rotation = Quaternion.FromToRotation(foot.position - lower.position, target - lower.position) * lower.rotation;
        }
    }
}
