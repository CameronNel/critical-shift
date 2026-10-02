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
        public abstract void SetHaulPose(SceneOperation? operation);
        public abstract void PresentStation(SceneOperation operation, Transform anchor);
        public abstract void CancelSceneActions();
        protected virtual void OnValidate()
        { if (!Guid.TryParse(identity, out var id) || id == Guid.Empty) identity = Guid.NewGuid().ToString(); }
    }
}
