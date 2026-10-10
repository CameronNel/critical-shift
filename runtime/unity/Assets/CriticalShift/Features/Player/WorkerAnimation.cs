using System;
using CriticalShift.Application;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Features.Player.Unity
{
    [Serializable]
    public sealed class WorkerMesh
    {
        public Renderer Renderer;
        public bool Suit, Head, Covered;
    }

    // Animator owns only the visible rig. CharacterController remains the sole locomotion writer.
    public sealed class WorkerAnimation : MonoBehaviour
    {
        [SerializeField] private Animator animator;
        [SerializeField] private Transform visual;
        [SerializeField] private FirstPersonWorker worker;
        [SerializeField] private LocalShiftHost host;
        [SerializeField] private WorkerMesh[] meshes = Array.Empty<WorkerMesh>();
        [SerializeField] private float seatedSupportHeight = 0.34f;
        private string _state = "";
        private float _gestureEnds;
        private bool _grounded = true;
        public void Configure(Animator rig, Transform model, FirstPersonWorker actor, LocalShiftHost session, WorkerMesh[] outfit, float supportHeight = 0.34f)
        {
            if (float.IsNaN(supportHeight) || float.IsInfinity(supportHeight) || supportHeight < 0.2f || supportHeight > 0.6f)
                throw new ArgumentException("Invalid exported seated support height.");
            animator = rig; visual = model; worker = actor; host = session; meshes = (WorkerMesh[])outfit.Clone();
            seatedSupportHeight = supportHeight; animator.applyRootMotion = false;
        }
        public void Action(PlayerAction action)
        {
            switch (action)
            {
                case PlayerAction.PrepareEquipment: Gesture("SUIT_UP"); break;
                case PlayerAction.Sit: Gesture("SPAWN_SIT_DOWN"); break;
                case PlayerAction.Stand: Gesture("SPAWN_STAND_UP"); break;
                case PlayerAction.PickUp: case PlayerAction.Take: Gesture("PICKUP"); break;
                case PlayerAction.Place: Gesture("PLACE"); break;
                case PlayerAction.Drop: Gesture("DROP"); break;
                case PlayerAction.Unequip: Gesture("SUIT_UP"); break;
            }
        }
        public void ResetProjection()
        {
            if (animator == null || visual == null) return;
            foreach (var mesh in meshes)
            {
                if (mesh.Renderer == null) continue;
                mesh.Renderer.enabled = !mesh.Suit;
                mesh.Renderer.shadowCastingMode = worker.LocalInput && mesh.Head ? ShadowCastingMode.ShadowsOnly : ShadowCastingMode.On;
            }
            visual.localPosition = Vector3.zero; _gestureEnds = 0; _state = "IDLE"; _grounded = true; animator.speed = 1;
            if (animator.isActiveAndEnabled && animator.HasState(0, Animator.StringToHash("IDLE"))) animator.Play("IDLE", 0, 0);
        }
        public void Gesture(string state)
        {
            if (animator == null || !animator.HasState(0, Animator.StringToHash(state))) return;
            animator.speed = 1; animator.CrossFadeInFixedTime(state, 0.12f); _state = state;
            // Use the imported clip's real duration; pause freezes Time.time and Animator together.
            float duration = 0;
            foreach (var clip in animator.runtimeAnimatorController.animationClips)
                if (clip.name == state) { duration = clip.length; break; }
            _gestureEnds = Time.time + duration;
        }
        private void LateUpdate()
        {
            if (host == null || animator == null || worker == null || host.View == null) return;
            var actor = host.Worker(worker.Id);
            if (actor == null) { animator.speed = 0; return; }
            // Preview the outfit during preparation; protection still requires the canonical equipment commit.
            bool suited = host.Equipment(worker.Id) != null || host.Preparation(worker.Id) != null;
            foreach (var mesh in meshes)
            {
                if (mesh.Renderer == null) continue;
                mesh.Renderer.enabled = mesh.Suit ? suited : !(suited && mesh.Covered);
                mesh.Renderer.shadowCastingMode = worker.LocalInput && mesh.Head ? ShadowCastingMode.ShadowsOnly : ShadowCastingMode.On;
            }
            visual.localPosition = actor.Pose == WorkerPose.Seated ? Vector3.down * seatedSupportHeight : Vector3.zero;
            if (host.View.Phase != WorldPhase.Running) { animator.speed = 0; return; }
            if (Time.time < _gestureEnds) { animator.speed = 1; return; }
            if (host.Preparation(worker.Id) != null)
            { animator.speed = 0; return; } // Hold the completed suit-up pose until the host's preparation deadline.
            var velocity = worker.transform.InverseTransformDirection(worker.Velocity);
            float speed = new Vector2(velocity.x, velocity.z).magnitude;
            bool grounded = worker.Grounded;
            if (grounded && !_grounded && actor.Pose == WorkerPose.Upright) { _grounded = grounded; Gesture("LAND"); return; }
            _grounded = grounded;
            string next; float stride = 1;
            if (actor.Pose == WorkerPose.Seated) next = "SPAWN_SEATED_IDLE";
            else if (!grounded) next = velocity.y > 0 ? "JUMP" : "FALL";
            else if (speed < 0.08f) next = host.Held(worker.Id) == null ? "IDLE" : "CARRY_IDLE";
            else if (host.Held(worker.Id) != null) { next = speed > 1.2f ? "CARRY_RUN" : "CARRY_WALK"; stride = next == "CARRY_RUN" ? 1.08f : 0.58f; }
            else if (speed > 2) { next = "SPRINT"; stride = 2.75f; }
            else if (Mathf.Abs(velocity.x) > Mathf.Abs(velocity.z)) { next = velocity.x > 0 ? "WALK_R" : "WALK_L"; stride = 0.44f; }
            else { next = velocity.z < 0 ? "WALK_B" : "WALK_F"; stride = 0.73f; }
            if (_state != next) { animator.CrossFadeInFixedTime(next, 0.15f); _state = next; }
            animator.speed = speed < 0.08f || !grounded || actor.Pose == WorkerPose.Seated ? 1 : Mathf.Clamp(speed / stride, 0.25f, 3);
        }
    }
}
