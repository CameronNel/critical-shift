using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    public sealed class PrototypeTntWall : MonoBehaviour
    {
        public float fuseSeconds = 3f;
        public float damageRadius = 4f;
        public bool IsArmed { get; private set; }
        public float FuseRemaining { get; private set; }
        public event Action<float> DetonationWarning;
        public event Action Detonated;
        public bool Arm() { if (IsArmed) return false; IsArmed = true; FuseRemaining = Mathf.Max(0.1f, fuseSeconds); return true; }
        void Update()
        {
            if (!IsArmed) return;
            Tick(Time.deltaTime);
        }
        public void TickForTest(float seconds) => Tick(seconds);
        void Tick(float seconds)
        {
            if (!IsArmed) return;
            FuseRemaining -= seconds; DetonationWarning?.Invoke(FuseRemaining);
            if (FuseRemaining <= 0f) { IsArmed = false; Detonated?.Invoke(); }
        }
        public void ResetWall() { IsArmed = false; FuseRemaining = 0f; }
    }
}
