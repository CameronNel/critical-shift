using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Host-local prototype boundary: a future network host must authorise these transitions.
    public sealed class PrototypeWorkerBody : MonoBehaviour
    {
        public enum BodyState { Normal, KnockedDown, Incapacitated, BeingDragged, Reanimating, Recovering }
        [SerializeField] BodyState state = BodyState.Normal;
        [SerializeField] float recoverySeconds = 1.25f;
        public Rigidbody PhysicsBody { get; private set; }
        float recoveryRemaining;
        BodyState stateBeforeDrag;
        public BodyState State => state;
        public bool CanBeMoved => state == BodyState.Incapacitated || state == BodyState.KnockedDown;
        public event Action<BodyState, BodyState> StateChanged;
        void Awake() => PhysicsBody = GetComponent<Rigidbody>();

        public bool KnockDown(float seconds = 1.25f)
        {
            if (state == BodyState.Reanimating) return false;
            recoveryRemaining = Mathf.Max(0.1f, seconds);
            return SetState(BodyState.KnockedDown);
        }
        public bool Incapacitate() => SetState(BodyState.Incapacitated);
        public bool BeginDrag()
        {
            if (!CanBeMoved) return false;
            stateBeforeDrag = state;
            return SetState(BodyState.BeingDragged);
        }
        public bool EndDrag(bool needsRecovery = true)
        {
            if (state != BodyState.BeingDragged) return false;
            if (stateBeforeDrag == BodyState.Incapacitated) return SetState(BodyState.Incapacitated);
            recoveryRemaining = needsRecovery ? recoverySeconds : 0f;
            return SetState(needsRecovery ? BodyState.Recovering : BodyState.Normal);
        }
        public bool BeginReanimation() => state == BodyState.Incapacitated && SetState(BodyState.Reanimating);
        public bool FinishReanimation()
        {
            if (state != BodyState.Reanimating) return false;
            recoveryRemaining = recoverySeconds;
            return SetState(BodyState.Recovering);
        }
        public bool RestoreNormal() => (state == BodyState.Recovering || state == BodyState.KnockedDown) && SetState(BodyState.Normal);
        public bool SetStateForTest(BodyState next) => SetState(next);

        void Update()
        {
            if (state == BodyState.KnockedDown && recoveryRemaining > 0f && (recoveryRemaining -= Time.deltaTime) <= 0f)
            {
                recoveryRemaining = recoverySeconds;
                SetState(BodyState.Recovering);
            }
            else if (state == BodyState.Recovering && recoveryRemaining > 0f && (recoveryRemaining -= Time.deltaTime) <= 0f)
                SetState(BodyState.Normal);
        }
        bool SetState(BodyState next)
        {
            if (state == next) return false;
            var old = state; state = next; StateChanged?.Invoke(old, next); return true;
        }
    }
}
