using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    public sealed class PrototypeSuitLocker : MonoBehaviour
    {
        public bool SuitOn { get; private set; } = true;
        public bool SafetyCompromised => !SuitOn;
        public event Action<bool> SuitChanged;
        public bool ToggleSuit() { SuitOn = !SuitOn; SuitChanged?.Invoke(SuitOn); return SuitOn; }
        public void SetSuit(bool on) { if (SuitOn == on) return; SuitOn = on; SuitChanged?.Invoke(on); }
    }
}
