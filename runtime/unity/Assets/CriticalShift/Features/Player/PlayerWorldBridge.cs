using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Player.Unity
{
    // The controller sees detached views and submits intent. Bootstrap alone composes the owners.
    public abstract class PlayerWorldBridge : MonoBehaviour
    {
        public abstract WorldSessionView View { get; }
        public abstract WorkerView Worker(Guid actor);
        public abstract ObjectClaimView Held(Guid actor);
        public abstract ObjectClaimView Equipment(Guid actor);
        public abstract ObjectClaimView Placed(Guid target);
        public abstract InteractionTarget Target(Guid id);
        public abstract InteractionTarget Aim(FirstPersonWorker worker);
        public abstract void Act(FirstPersonWorker worker, PlayerAction action, InteractionTarget target);
        public virtual bool TryUse(FirstPersonWorker worker) => false;
        public virtual bool Busy(Guid actor) => false;
        public virtual bool Preparing(Guid actor) => false;
        public virtual string UsePrompt(FirstPersonWorker worker) => "";
        public abstract void TogglePause();
        public abstract void Begin();
        public abstract string Feedback { get; }
    }

    public readonly struct PlayerInputFrame
    {
        public PlayerInputFrame(Vector2 move, Vector2 look, bool jump, bool crouch, bool sprint)
        { Move = move; Look = look; Jump = jump; Crouch = crouch; Sprint = sprint; }
        public Vector2 Move { get; }
        public Vector2 Look { get; }
        public bool Jump { get; }
        public bool Crouch { get; }
        public bool Sprint { get; }
    }
}
