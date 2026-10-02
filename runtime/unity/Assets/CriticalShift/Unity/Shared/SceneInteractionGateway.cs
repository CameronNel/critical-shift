using System;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    public abstract class SceneInteractionGateway : MonoBehaviour
    {
        public abstract bool Running { get; }
        public abstract bool CanAct(WorkerScenePort worker);
        public abstract SceneTarget Held(WorkerScenePort worker);
        public abstract bool CanUse(WorkerScenePort worker, SceneTarget target);
        public abstract string Describe(SceneTarget target);
        public abstract void RotateHeld(WorkerScenePort worker, float degrees);
        public abstract bool Execute(WorkerScenePort worker, SceneTarget target, SceneOperation operation, out string reason);
        public abstract bool RecoveryReady(WorkerScenePort worker);
        public abstract long BeginRecovery(WorkerScenePort worker);
        public abstract bool CompleteRecovery(WorkerScenePort worker, long attempt);
        public abstract void Impact(WorkerScenePort worker, Guid hazard, bool incapacitating, float delaySeconds);
        public abstract void AttachmentFailed(SceneTarget target, long generation, WorkerScenePort assistant = null);
    }
}
