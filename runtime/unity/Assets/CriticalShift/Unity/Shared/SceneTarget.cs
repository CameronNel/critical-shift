using System;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    public abstract class SceneTarget : MonoBehaviour
    {
        [SerializeField] private string identity;
        [SerializeField] private Transform contact;
        [SerializeField, Min(0.1f)] private float reach = 1.8f;
        [SerializeField] private SceneOperation operation = SceneOperation.Button;
        public Guid Id => Guid.Parse(identity);
        public virtual Transform Contact => contact != null ? contact : transform;
        public float Reach => reach;
        public SceneOperation Operation => operation;
        public abstract bool Supports(SceneOperation value);
        // Called only by the host after the command has committed. Never an authoritative UnityEvent.
        public abstract bool Apply(WorkerScenePort worker, SceneOperation value, long generation);
        public abstract void ClearBinding();
        protected virtual void OnValidate()
        { if (!Guid.TryParse(identity, out var id) || id == Guid.Empty) identity = Guid.NewGuid().ToString(); }
    }
}
