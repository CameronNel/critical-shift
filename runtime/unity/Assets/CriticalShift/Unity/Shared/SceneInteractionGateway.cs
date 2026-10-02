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
        public virtual bool BeginBonk(WorkerScenePort worker, out string reason) { reason = "Hold a bonk shovel first."; return false; }
        public virtual float BonkPhase(WorkerScenePort worker) => -1;
        public virtual BonkSwingPose BonkPose(WorkerScenePort worker) => BonkSwingPose.Sample(Mathf.Max(0, BonkPhase(worker)));
        public virtual void CancelBonk(WorkerScenePort worker) { }
        public abstract bool RecoveryReady(WorkerScenePort worker);
        public abstract long BeginRecovery(WorkerScenePort worker);
        public abstract bool CompleteRecovery(WorkerScenePort worker, long attempt);
        public virtual void CancelRecovery(WorkerScenePort worker, long attempt) { }
        public abstract void Impact(WorkerScenePort worker, Guid hazard, bool incapacitating, float delaySeconds,
            Vector3 impulse = default, Vector3? contactPoint = null);
        public virtual bool ConsciousDown(WorkerScenePort worker) => false;
        public abstract void AttachmentFailed(SceneTarget target, long generation, WorkerScenePort assistant = null);
    }
}
