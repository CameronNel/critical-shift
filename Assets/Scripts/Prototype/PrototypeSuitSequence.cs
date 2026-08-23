using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Host-local prototype boundary: suit completion must be host-authorised in multiplayer.
    public sealed class PrototypeSuitSequence : MonoBehaviour
    {
        public enum Step { Idle, Equip, Helmet, Integrity, Dosimeter, Complete, SkippedIntegrity }
        public enum Result { None, SafeComplete, IntegritySkipped }
        public float stepSeconds = 0.75f;
        public Step CurrentStep { get; private set; } = Step.Idle;
        public Result FinalResult { get; private set; } = Result.None;
        public float Progress { get; private set; }
        public bool IsRunning => CurrentStep == Step.Equip || CurrentStep == Step.Helmet || CurrentStep == Step.Integrity || CurrentStep == Step.Dosimeter;
        public event Action<Step> StepChanged;
        public event Action<Result> Completed;

        public bool Begin()
        {
            if (IsRunning) return false;
            FinalResult = Result.None; Progress = 0f; SetStep(Step.Equip); return true;
        }

        public bool SkipIntegrity()
        {
            if (CurrentStep != Step.Integrity) return false;
            Progress = 0f; FinalResult = Result.IntegritySkipped; SetStep(Step.SkippedIntegrity); SetStep(Step.Dosimeter); return true;
        }

        void Update() { if (IsRunning) Tick(Time.deltaTime); }
        public void TickForTest(float seconds) => Tick(seconds);
        void Tick(float seconds)
        {
            if (!IsRunning) return;
            Progress += seconds / Mathf.Max(.01f, stepSeconds);
            int transitions = 0;
            while (Progress >= 1f && IsRunning && transitions++ < 8)
            {
                Progress -= 1f;
                switch (CurrentStep)
                {
                    case Step.Equip: SetStep(Step.Helmet); break;
                    case Step.Helmet: SetStep(Step.Integrity); break;
                    case Step.Integrity: SetStep(Step.Dosimeter); break;
                    case Step.Dosimeter: if (FinalResult == Result.None) FinalResult = Result.SafeComplete; SetStep(Step.Complete); Completed?.Invoke(FinalResult); break;
                }
            }
        }

        public void ResetSequence() { CurrentStep = Step.Idle; FinalResult = Result.None; Progress = 0f; StepChanged?.Invoke(CurrentStep); }
        void SetStep(Step step) { CurrentStep = step; StepChanged?.Invoke(step); }
    }
}
