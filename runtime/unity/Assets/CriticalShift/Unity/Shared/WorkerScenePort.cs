using System;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    // Engine ports shared by worker, object physics and bootstrap; these hold no gameplay rules.
    public abstract class WorkerScenePort : MonoBehaviour
    {
        [SerializeField] private string identity;
        public Guid Id => Guid.Parse(identity);
        public abstract Transform Eye { get; }
        public abstract Transform Grip { get; }
        public abstract Collider[] BodyColliders { get; }
        public abstract bool Grounded { get; }
        public abstract bool RecoveryClear { get; }
        public abstract bool Down { get; }
        public abstract Vector3 Velocity { get; }
        public virtual Rigidbody PhysicalBody => null;
        public virtual Rigidbody GripBody(Vector3 target) => PhysicalBody;
        public virtual float PhysicalMass => PhysicalBody != null ? PhysicalBody.mass : 0;
        public virtual Collider[] PhysicalColliders => BodyColliders;
        public virtual void ApplyBodyImpulse(Vector3 impulse, Vector3 point)
        { if (PhysicalBody != null && !PhysicalBody.isKinematic) PhysicalBody.AddForceAtPosition(impulse, point, ForceMode.Impulse); }
        public abstract void SetHaulPose(SceneOperation? operation);
        public abstract void PresentStation(SceneOperation operation, Transform anchor);
        public abstract void CancelSceneActions();
        public virtual void StopSceneSimulation() { CancelSceneActions(); }
        protected virtual void OnValidate()
        { if (!Guid.TryParse(identity, out var id) || id == Guid.Empty) identity = Guid.NewGuid().ToString(); }
    }
}
