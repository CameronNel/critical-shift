using System;
using UnityEngine;

namespace CriticalShift.Prototype
{
    // These machines are host-local today. Their explicit transitions and pure batch
    // transforms are intentionally suitable for a future host-authoritative adapter.
    public enum FacilityMachineState { Offline, Starting, Idle, AcceptingInput, Processing, OutputReady, Stressed, Faulted, Repairing }
    public enum PrototypeFacilityProductStage { None, Sorted, Processed, Dried, Assembled, Inspected }

    public abstract class PrototypeFacilityMachine : MonoBehaviour
    {
        public FacilityMachineState state = FacilityMachineState.Offline;
        public MachineAudioState audioState = MachineAudioState.Idle;
        public float processSeconds = 1f;
        public bool unsafeShortcut;
        public PrototypeFacilityProductStage outputStage = PrototypeFacilityProductStage.None;
        protected float elapsed;
        public event Action<MachineAudioState> AudioStateChanged;
        public event Action<string> WarningRaised;
        public event Action<string> FailureRaised;
        protected void SetAudio(MachineAudioState value) { audioState = value; AudioStateChanged?.Invoke(value); }
        protected void Warn(string message) { WarningRaised?.Invoke(message); SetAudio(MachineAudioState.Warning); }
        protected void Fail(string message) { state = FacilityMachineState.Faulted; FailureRaised?.Invoke(message); SetAudio(MachineAudioState.Failure); }
        public virtual bool BeginOperation() { if (state != FacilityMachineState.Offline && state != FacilityMachineState.Idle) return false; state = FacilityMachineState.Starting; elapsed = 0f; SetAudio(MachineAudioState.Starting); return true; }
        public void SetUnsafeShortcut(bool enabled) { unsafeShortcut = enabled; if (enabled) Warn("UNSAFE BYPASS ENABLED"); }
        protected bool BeginProcessing() { if (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput) return false; state = FacilityMachineState.Processing; elapsed = 0f; SetAudio(MachineAudioState.Running); return true; }
        protected bool Advance(float dt) { elapsed += Mathf.Max(0f, dt); if (state == FacilityMachineState.Starting && elapsed >= .25f) { state = FacilityMachineState.Idle; elapsed = 0f; SetAudio(MachineAudioState.Idle); } return state == FacilityMachineState.Processing && elapsed >= processSeconds; }
        public abstract void Tick(float dt);
        public abstract void ResetMachine();
    }

    public sealed class PrototypeSorter : PrototypeFacilityMachine
    {
        public PrototypeBatch input, output;
        public bool Accept(PrototypeBatch batch) { if (batch == null || input != null || (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput)) return false; input = batch; state = FacilityMachineState.AcceptingInput; return true; }
        public override void Tick(float dt) { if (state == FacilityMachineState.Starting) { Advance(dt); return; } if (state == FacilityMachineState.AcceptingInput) BeginProcessing(); if (Advance(dt)) { output = input.Clone(); output.form = OreForm.Sorted; output.rock = Mathf.Clamp01(output.rock * (unsafeShortcut ? .9f : .7f)); if (unsafeShortcut) { output.hiddenDefect = Mathf.Clamp01(output.hiddenDefect + .12f); Warn("SORT REDUCED: scanner shortcut left mixed material"); } input = null; outputStage = PrototypeFacilityProductStage.Sorted; state = FacilityMachineState.OutputReady; SetAudio(MachineAudioState.Idle); } }
        public PrototypeBatch TakeOutput() { var value = output; output = null; if (state == FacilityMachineState.OutputReady) state = FacilityMachineState.Idle; return value; }
        public override void ResetMachine() { input = null; output = null; elapsed = 0f; unsafeShortcut = false; outputStage = PrototypeFacilityProductStage.None; state = FacilityMachineState.Idle; SetAudio(MachineAudioState.Idle); }
    }

    public sealed class PrototypeProcessor : PrototypeFacilityMachine
    {
        public PrototypeBatch input, output;
        public float temperature = .5f, pressure = .5f;
        public bool Accept(PrototypeBatch batch) { if (batch == null || input != null || (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput) || batch.form != OreForm.Sorted) return false; input = batch; state = FacilityMachineState.AcceptingInput; return true; }
        public override void Tick(float dt) { if (state == FacilityMachineState.Starting) { Advance(dt); return; } if (state == FacilityMachineState.AcceptingInput) BeginProcessing(); if (Advance(dt)) { output = input.Clone(); output.form = OreForm.Processed; output.grade = Mathf.Clamp01(output.grade + .08f - output.rock * .08f); output.contamination = Mathf.Clamp01(output.contamination + (unsafeShortcut ? .15f : .01f)); if (unsafeShortcut) { output.hiddenDefect = Mathf.Clamp01(output.hiddenDefect + .18f); Warn("PROCESS CYCLE SHORTENED: contamination risk increased"); } input = null; outputStage = PrototypeFacilityProductStage.Processed; state = FacilityMachineState.OutputReady; SetAudio(MachineAudioState.Idle); } }
        public PrototypeBatch TakeOutput() { var value = output; output = null; if (state == FacilityMachineState.OutputReady) state = FacilityMachineState.Idle; return value; }
        public override void ResetMachine() { input = null; output = null; elapsed = 0f; unsafeShortcut = false; outputStage = PrototypeFacilityProductStage.None; temperature = .5f; pressure = .5f; state = FacilityMachineState.Idle; SetAudio(MachineAudioState.Idle); }
    }

    public sealed class PrototypeDryer : PrototypeFacilityMachine
    {
        public PrototypeBatch input, output;
        public float heat = .5f;
        public bool Accept(PrototypeBatch batch) { if (batch == null || input != null || (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput) || batch.form != OreForm.Processed) return false; input = batch; state = FacilityMachineState.AcceptingInput; return true; }
        public override void Tick(float dt) { if (state == FacilityMachineState.Starting) { Advance(dt); return; } if (state == FacilityMachineState.AcceptingInput) BeginProcessing(); if (Advance(dt)) { output = input.Clone(); output.form = OreForm.Dried; if (unsafeShortcut) { output.moisture = Mathf.Min(.2f, output.moisture + .08f); output.hiddenDefect = Mathf.Clamp01(output.hiddenDefect + .1f); Warn("DRYER FILTER BYPASS: retained moisture warning"); } else output.moisture = 0f; input = null; outputStage = PrototypeFacilityProductStage.Dried; state = FacilityMachineState.OutputReady; SetAudio(MachineAudioState.Idle); } }
        public PrototypeBatch TakeOutput() { var value = output; output = null; if (state == FacilityMachineState.OutputReady) state = FacilityMachineState.Idle; return value; }
        public override void ResetMachine() { input = null; output = null; elapsed = 0f; unsafeShortcut = false; outputStage = PrototypeFacilityProductStage.None; heat = .5f; state = FacilityMachineState.Idle; SetAudio(MachineAudioState.Idle); }
    }

    public sealed class PrototypeFuelAssemblyStation : PrototypeFacilityMachine
    {
        public PrototypeBatch input, output;
        public bool Accept(PrototypeBatch batch) { if (batch == null || input != null || (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput) || batch.form != OreForm.Dried) return false; input = batch; state = FacilityMachineState.AcceptingInput; return true; }
        public override void Tick(float dt) { if (state == FacilityMachineState.Starting) { Advance(dt); return; } if (state == FacilityMachineState.AcceptingInput) BeginProcessing(); if (Advance(dt)) { output = input.Clone(); output.form = OreForm.Dried; output.fuelQuality = Mathf.Clamp01(output.grade * (1f - output.contamination) * (1f - output.moisture * .35f) * (1f - output.hiddenDefect * .4f)); if (unsafeShortcut) { output.hiddenDefect = Mathf.Clamp01(output.hiddenDefect + .2f); output.fuelQuality = Mathf.Clamp01(output.fuelQuality - .12f); Warn("FUEL CASING SHORTCUT: assembly defect is hidden"); } input = null; outputStage = PrototypeFacilityProductStage.Assembled; state = FacilityMachineState.OutputReady; SetAudio(MachineAudioState.Idle); } }
        public PrototypeBatch TakeOutput() { var value = output; output = null; if (state == FacilityMachineState.OutputReady) state = FacilityMachineState.Idle; return value; }
        public override void ResetMachine() { input = null; output = null; elapsed = 0f; unsafeShortcut = false; outputStage = PrototypeFacilityProductStage.None; state = FacilityMachineState.Idle; SetAudio(MachineAudioState.Idle); }
    }

    public sealed class PrototypeInspectionStation : PrototypeFacilityMachine
    {
        public PrototypeBatch input, output;
        [Range(0f, 1f)] public float confidence = .9f;
        public bool Accept(PrototypeBatch batch) { if (batch == null || input != null || (state != FacilityMachineState.Idle && state != FacilityMachineState.AcceptingInput) || batch.form != OreForm.Dried) return false; input = batch; state = FacilityMachineState.AcceptingInput; return true; }
        public override void Tick(float dt) { if (state == FacilityMachineState.Starting) { Advance(dt); return; } if (state == FacilityMachineState.AcceptingInput) BeginProcessing(); if (Advance(dt)) { output = input.Clone(); output.inspectionConfidence = Mathf.Clamp01(confidence - output.hiddenDefect * .45f); output.fuelQuality = Mathf.Clamp01(output.fuelQuality); if (unsafeShortcut) { output.inspectionConfidence = Mathf.Clamp01(output.inspectionConfidence - .25f); Warn("INSPECTION SHORTCUT: confidence reduced"); } input = null; outputStage = PrototypeFacilityProductStage.Inspected; state = FacilityMachineState.OutputReady; SetAudio(MachineAudioState.Idle); } }
        public PrototypeBatch TakeOutput() { var value = output; output = null; if (state == FacilityMachineState.OutputReady) state = FacilityMachineState.Idle; return value; }
        public override void ResetMachine() { input = null; output = null; elapsed = 0f; unsafeShortcut = false; outputStage = PrototypeFacilityProductStage.None; confidence = .9f; state = FacilityMachineState.Idle; SetAudio(MachineAudioState.Idle); }
    }
}
