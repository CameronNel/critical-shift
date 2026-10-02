using CriticalShift.Unity.Shared;
using CriticalShift.Application;
using UnityEngine;
using UnityEngine.Events;

namespace CriticalShift.Features.Interaction.Unity
{
    public enum ControlKind { Button, Lever, Valve, Door, ServicePort, DigSite, SuitLocker, ReanimationStation, Aid }
    [DisallowMultipleComponent]
    public sealed class FacilityControl : SceneTarget
    {
        [SerializeField] private ControlKind kind;
        [SerializeField] private Transform movingPart, workerAnchor;
        [SerializeField] private WorkerScenePort patient;
        [SerializeField] private HingeJoint doorHinge;
        [SerializeField] private Vector3 localAxis = Vector3.up;
        [SerializeField] private float travelDegrees = 85;
        [SerializeField] private UnityEvent committedEffect;
        private Quaternion rest;
        public ControlKind Kind => kind;
        public Transform WorkerAnchor => workerAnchor;
        public WorkerScenePort Patient => patient;
        public bool Active { get; private set; }
        public bool Connected { get; private set; }
        public float ValveDegrees { get; private set; }
        public void Project(ControlView state)
        { Active = state.Active; Connected = state.Connected; ValveDegrees = state.Turns * 60; }
        private void Awake() { if (movingPart != null) rest = movingPart.localRotation; }
        public override bool Supports(SceneOperation value)
        {
            switch (kind)
            {
                case ControlKind.Button: return value == SceneOperation.Button;
                case ControlKind.Lever: return value == SceneOperation.Lever;
                case ControlKind.Valve: return value == SceneOperation.ValveTurn || value == SceneOperation.ValveHold;
                case ControlKind.Door: return value == SceneOperation.Open;
                case ControlKind.ServicePort: return value == SceneOperation.Connect;
                case ControlKind.DigSite: return value == SceneOperation.Dig;
                case ControlKind.SuitLocker: return value == SceneOperation.Suit || value == SceneOperation.LockerExit;
                case ControlKind.ReanimationStation: return value == SceneOperation.Reanimation || value == SceneOperation.Connect;
                case ControlKind.Aid: return value == SceneOperation.Help;
                default: return false;
            }
        }
        public override bool Apply(WorkerScenePort worker, SceneOperation value, long generation)
        {
            if (!Supports(value)) return false;
            if (kind == ControlKind.Door)
            {
                if (doorHinge == null) return false;
                var spring = doorHinge.spring; spring.spring = 50; spring.damper = 10; spring.targetPosition = Active ? travelDegrees : 0;
                doorHinge.spring = spring; doorHinge.useSpring = true;
            }
            else if (movingPart != null && localAxis.sqrMagnitude > 0)
                movingPart.localRotation = rest * Quaternion.AngleAxis(kind == ControlKind.Valve ? ValveDegrees : Active ? travelDegrees : 0, localAxis.normalized);
            committedEffect?.Invoke(); // Cosmetic/audio only. Host operations never use this callback.
            return true;
        }
        public override void ClearBinding() { Active = Connected = false; ValveDegrees = 0; if (doorHinge != null) { var spring = doorHinge.spring; spring.targetPosition = 0; doorHinge.spring = spring; } else if (movingPart != null) movingPart.localRotation = rest; }
    }
}
