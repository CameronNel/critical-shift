using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    public sealed class PrototypeReanimationStation : MonoBehaviour
    {
        public float reanimationSeconds = 4f;
        public int powerCost = 25;
        public bool IsBusy { get; private set; }
        public float Progress { get; private set; }
        public int PowerSpent { get; private set; }
        PrototypeWorkerBody patient;
        public event Action<PrototypeWorkerBody, int> ReanimationStarted;
        public event Action<PrototypeWorkerBody> ReanimationCompleted;
        public event Action Reset;
        public bool TryStart(PrototypeWorkerBody worker, ref int availablePower)
        {
            if (IsBusy || worker == null || availablePower < powerCost || !worker.BeginReanimation()) return false;
            availablePower -= powerCost; PowerSpent += powerCost; patient = worker; IsBusy = true; Progress = 0f; ReanimationStarted?.Invoke(worker, powerCost); return true;
        }
        void Update()
        {
            Tick(Time.deltaTime);
        }
        public void TickForTest(float seconds) => Tick(seconds);
        void Tick(float seconds)
        {
            if (!IsBusy) return;
            Progress += seconds / Mathf.Max(0.01f, reanimationSeconds);
            if (Progress >= 1f) { patient.FinishReanimation(); ReanimationCompleted?.Invoke(patient); patient = null; IsBusy = false; }
        }
        public void ResetStation()
        {
            if (patient != null) patient.SetStateForTest(PrototypeWorkerBody.BodyState.Incapacitated);
            patient = null; IsBusy = false; Progress = 0f; PowerSpent = 0; Reset?.Invoke();
        }
    }
}
