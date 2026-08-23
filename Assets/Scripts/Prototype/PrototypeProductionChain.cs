using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    // Host-local now; the small deterministic APIs are deliberately separable for future authority.
    public enum OreForm { Raw, Crushed, Sorted, Processed, Dried }
    public enum MachineAudioState { Idle, Starting, Running, Stressed, Warning, Failure, Shutdown, Repair }
    public enum CrusherState { Offline, Starting, Idle, AcceptingInput, Processing, OutputReady, Stressed, Faulted, EmergencyStop, Repairing }
    public enum ReactorCrisisStage { Stable, Stressed, Unstable, CoolingEmergency, EmergencyShutdown, CoreDamage, CriticalMeltdown, Contained }

    [Serializable]
    public class PrototypeBatch
    {
        public string id = Guid.NewGuid().ToString("N");
        public OreForm form = OreForm.Raw;
        public float mass = 1f, grade = .5f, rock = .2f, moisture, contamination;
        public float fuelQuality, hiddenDefect, inspectionConfidence = 1f;
        public bool wetShortcut;
        public PrototypeBatch Clone() { return (PrototypeBatch)MemberwiseClone(); }

        public PrototypeBatch Crush(bool unsafeBypass)
        {
            var result = Clone(); result.form = OreForm.Crushed;
            result.rock = Mathf.Clamp01(result.rock * .65f); result.contamination = Mathf.Clamp01(result.contamination + result.rock * .08f);
            if (unsafeBypass) { result.mass *= 1.08f; result.hiddenDefect = Mathf.Clamp01(result.hiddenDefect + .2f); }
            return result;
        }
        public PrototypeBatch Dry() { var result = Clone(); result.form = OreForm.Dried; result.mass *= 1f - result.moisture * .08f; result.moisture = 0f; return result; }
        public PrototypeBatch AssembleFuel()
        {
            var result = Clone(); result.fuelQuality = Mathf.Clamp01(result.grade * (1f - result.contamination) * (1f - result.moisture * .35f) * (1f - result.hiddenDefect * .4f)); return result;
        }
    }

    public sealed class PrototypeOre : MonoBehaviour
    {
        public PrototypeBatch batch = new PrototypeBatch();
        public Rigidbody Body { get; private set; }
        void Awake() { Body = GetComponent<Rigidbody>() ?? gameObject.AddComponent<Rigidbody>(); Body.mass = Mathf.Max(.1f, batch.mass); }
    }

    public sealed class PrototypeFuelAssembly : MonoBehaviour
    {
        public PrototypeBatch batch;
        public bool inspected;
        public Rigidbody Body { get; private set; }
        public float Quality { get { return batch == null ? 0f : batch.fuelQuality; } }
        void Awake()
        {
            Body = GetComponent<Rigidbody>() ?? gameObject.AddComponent<Rigidbody>();
            if (GetComponent<PrototypeCarryable>() == null) gameObject.AddComponent<PrototypeCarryable>();
        }
    }

    public sealed class PrototypeConveyor : MonoBehaviour
    {
        public float speed = 1.4f, capacity = 4f;
        public Transform output;
        readonly List<PrototypeOre> items = new List<PrototypeOre>();
        public event Action<PrototypeOre> OreDelivered;
        public float CurrentMass { get { float m = 0f; foreach (var i in items) if (i) m += i.batch.mass; return m; } }
        public bool TryAccept(PrototypeOre ore)
        {
            if (!ore || items.Contains(ore) || CurrentMass + ore.batch.mass > capacity) return false;
            items.Add(ore); ore.Body.isKinematic = true; return true;
        }
        void FixedUpdate()
        {
            for (int i = items.Count - 1; i >= 0; --i)
            {
                var ore = items[i];
                if (!ore) { items.RemoveAt(i); continue; }
                ore.transform.position += transform.forward * speed * Time.fixedDeltaTime;
                if (output && Vector3.Dot(output.position - ore.transform.position, transform.forward) <= .1f)
                {
                    ore.transform.position = output.position;
                    ore.Body.isKinematic = false;
                    items.RemoveAt(i);
                    OreDelivered?.Invoke(ore);
                }
            }
        }

        void OnTriggerEnter(Collider other)
        {
            var ore = other.GetComponentInParent<PrototypeOre>();
            if (ore != null) TryAccept(ore);
        }

        public void ResetConveyor()
        {
            foreach (var ore in items) if (ore != null && ore.Body != null) ore.Body.isKinematic = false;
            items.Clear();
        }
    }

    public sealed class PrototypeCrusher : MonoBehaviour
    {
        public CrusherState state = CrusherState.Offline;
        public MachineAudioState audioState = MachineAudioState.Idle;
        public float processSeconds = 1.5f, damage, capacity = 3f;
        public bool safetyBypass;
        public PrototypeBatch input, output;
        float elapsed; public bool WetJam { get; private set; }
        public event Action<MachineAudioState> AudioStateChanged;
        void SetAudio(MachineAudioState value) { audioState = value; AudioStateChanged?.Invoke(value); }
        public bool BeginOperation() { if (state != CrusherState.Offline && state != CrusherState.Idle) return false; state = CrusherState.Starting; elapsed = 0f; SetAudio(MachineAudioState.Starting); return true; }
        public bool Accept(PrototypeBatch batch) { if (state != CrusherState.Idle && state != CrusherState.AcceptingInput || input != null || batch == null || batch.mass > capacity) return false; input = batch; state = CrusherState.AcceptingInput; return true; }
        public void SetUnsafeBypass(bool enabled) { safetyBypass = enabled; }
        public void Tick(float dt)
        {
            dt = Mathf.Max(0f, dt);
            if (state == CrusherState.Starting)
            {
                elapsed += dt;
                if (elapsed >= .25f) { state = CrusherState.Idle; elapsed = 0f; SetAudio(MachineAudioState.Idle); }
            }
            if (state == CrusherState.AcceptingInput && input != null)
            {
                state = CrusherState.Processing;
                elapsed = 0f;
                SetAudio(MachineAudioState.Running);
            }
            if (state == CrusherState.Processing)
            {
                elapsed += dt;
                if (elapsed >= processSeconds)
                {
                    if (input.wetShortcut && !safetyBypass) { WetJam = true; state = CrusherState.Faulted; damage += .2f; SetAudio(MachineAudioState.Failure); }
                    else { output = input.Crush(safetyBypass); input = null; state = CrusherState.OutputReady; SetAudio(MachineAudioState.Idle); }
                }
            }
        }
        public PrototypeBatch TakeOutput() { var result = output; output = null; if (state == CrusherState.OutputReady) state = CrusherState.Idle; return result; }
        public void ResetMachine() { input = null; output = null; WetJam = false; damage = 0f; elapsed = 0f; state = CrusherState.Idle; SetAudio(MachineAudioState.Idle); }
        public bool Repair() { if (state != CrusherState.Faulted) return false; state = CrusherState.Repairing; SetAudio(MachineAudioState.Repair); return true; }
        public void FinishRepair() { if (state == CrusherState.Repairing) ResetMachine(); }
        void Update() { Tick(Time.deltaTime); }
    }

    public sealed class PrototypeCoolingValve : MonoBehaviour
    {
        [Range(0f, 1f)] public float opening = 1f; public bool manualOverride;
        public void SetOpening(float value) { opening = Mathf.Clamp01(value); }
    }

    public sealed class PrototypeDemandGauge : MonoBehaviour
    {
        [Range(0f, 1f)] public float demand = .55f; public float waveSpeed = .025f;
        public void Tick(float dt) { demand = Mathf.Clamp01(demand + waveSpeed * dt); }
        public void ResetGauge() { demand = .55f; }
        void Update() { Tick(Time.deltaTime); }
    }

    public sealed class PrototypeReactorMachine : MonoBehaviour
    {
        public ReactorCrisisStage stage = ReactorCrisisStage.Stable;
        public MachineAudioState audioState = MachineAudioState.Idle;
        public float heat, stability = 1f, cooling = 1f, fuelRemaining, output;
        public float shortcutDelay = 4f;
        public bool IsRunning { get; private set; }
        public int LoadedBatches { get; private set; }
        public bool UnsafeFuelLoaded { get { return unsafeFuel; } }
        float consequenceTimer = -1f; bool unsafeFuel;
        public event Action<MachineAudioState> AudioStateChanged; public event Action<ReactorCrisisStage> StageChanged;
        void SetAudio(MachineAudioState v) { audioState = v; AudioStateChanged?.Invoke(v); }
        void SetStage(ReactorCrisisStage v) { if (stage == v) return; stage = v; StageChanged?.Invoke(v); SetAudio(v >= ReactorCrisisStage.CoolingEmergency ? MachineAudioState.Warning : MachineAudioState.Stressed); }
        public bool LoadFuel(PrototypeFuelAssembly fuel)
        {
            if (!fuel || LoadedBatches >= PrototypeShiftRules.FuelQuota) return false;
            fuelRemaining += Mathf.Max(.35f, fuel.batch == null ? .5f : fuel.batch.mass);
            LoadedBatches++;
            bool risky = fuel.Quality < .45f || (fuel.batch != null && fuel.batch.hiddenDefect > 0f);
            unsafeFuel |= risky;
            if (risky && consequenceTimer < 0f) consequenceTimer = shortcutDelay;
            return true;
        }
        public bool StartReactor()
        {
            if (IsRunning || LoadedBatches < PrototypeShiftRules.FuelQuota) return false;
            IsRunning = true;
            SetAudio(MachineAudioState.Starting);
            return true;
        }
        public void UseUnsafeShortcut() { unsafeFuel = true; consequenceTimer = shortcutDelay; SetAudio(MachineAudioState.Warning); }
        public void Tick(float dt, float demand, PrototypeCoolingValve valve)
        {
            dt = Mathf.Max(0f, dt); demand = Mathf.Clamp01(demand);
            if (!IsRunning)
            {
                heat = Mathf.Max(0f, heat - dt * .04f);
                output = Mathf.MoveTowards(output, 0f, dt);
                return;
            }
            if (consequenceTimer >= 0f) { consequenceTimer -= dt; if (consequenceTimer <= 0f) { heat += .25f; stability -= .25f; consequenceTimer = -1f; } }
            if (fuelRemaining > 0f) { fuelRemaining = Mathf.Max(0f, fuelRemaining - dt * (.025f + demand * .035f)); output = Mathf.Lerp(output, demand, Mathf.Clamp01(dt)); }
            else output = Mathf.MoveTowards(output, 0f, dt * .5f);
            cooling = Mathf.Lerp(cooling, valve == null ? 1f : valve.opening, dt * 2f); heat += (demand * .16f + (unsafeFuel ? .08f : 0f)) * dt - cooling * .1f * dt; stability -= Mathf.Max(0f, heat - .65f) * .08f * dt;
            heat = Mathf.Max(0f, heat);
            if (stage == ReactorCrisisStage.Stable && (heat > .35f || demand > .75f)) SetStage(ReactorCrisisStage.Stressed);
            if (stage <= ReactorCrisisStage.Stressed && (heat > .6f || stability < .75f)) SetStage(ReactorCrisisStage.Unstable);
            if (stage <= ReactorCrisisStage.Unstable && (heat > .78f || cooling < .3f)) SetStage(ReactorCrisisStage.CoolingEmergency);
            if (stage == ReactorCrisisStage.CoolingEmergency && heat > .9f) SetStage(ReactorCrisisStage.EmergencyShutdown);
            if (stage == ReactorCrisisStage.EmergencyShutdown && heat > 1.05f) SetStage(ReactorCrisisStage.CoreDamage);
            if (stage == ReactorCrisisStage.CoreDamage && heat > 1.2f) SetStage(ReactorCrisisStage.CriticalMeltdown);
        }
        public bool EmergencyCooling() { if (stage < ReactorCrisisStage.CoolingEmergency) return false; cooling = 1f; heat = Mathf.Max(0f, heat - .35f); if (heat < .7f) SetStage(ReactorCrisisStage.Contained); return true; }
        public void ResetReactor() { stage = ReactorCrisisStage.Stable; heat = 0f; stability = 1f; cooling = 1f; fuelRemaining = 0f; output = 0f; unsafeFuel = false; consequenceTimer = -1f; IsRunning = false; LoadedBatches = 0; SetAudio(MachineAudioState.Shutdown); }
        void Update() { var gauge = FindAnyObjectByType<PrototypeDemandGauge>(); var valve = FindAnyObjectByType<PrototypeCoolingValve>(); Tick(Time.deltaTime, gauge ? gauge.demand : 0f, valve); }
    }

    public static class PrototypeMachineSceneBuilder
    {
        public static GameObject BuildProductionShoebox(Vector3 origin)
        {
            var root = new GameObject("Prototype Production Shoebox"); root.transform.position = origin;
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube); floor.name = "Production Floor"; floor.transform.SetParent(root.transform); floor.transform.localPosition = new Vector3(0f, -.1f, 0f); floor.transform.localScale = new Vector3(14f, .2f, 7f);
            var conveyorGo = new GameObject("Ore Conveyor"); conveyorGo.transform.SetParent(root.transform); conveyorGo.transform.localPosition = new Vector3(-4f, .6f, 0f); var conveyor = conveyorGo.AddComponent<PrototypeConveyor>(); conveyor.output = conveyorGo.transform; conveyorGo.transform.forward = Vector3.right;
            var crusherGo = new GameObject("Crusher"); crusherGo.transform.SetParent(root.transform); crusherGo.transform.localPosition = new Vector3(0f, 1f, 0f); crusherGo.AddComponent<PrototypeCrusher>();
            var reactorGo = new GameObject("Reactor"); reactorGo.transform.SetParent(root.transform); reactorGo.transform.localPosition = new Vector3(4f, 1f, 0f); reactorGo.AddComponent<PrototypeReactorMachine>();
            var valveGo = new GameObject("Cooling Valve"); valveGo.transform.SetParent(root.transform); valveGo.transform.localPosition = new Vector3(4f, .8f, 2f); valveGo.AddComponent<PrototypeCoolingValve>();
            var gaugeGo = new GameObject("Demand Gauge"); gaugeGo.transform.SetParent(root.transform); gaugeGo.transform.localPosition = new Vector3(4f, 1.6f, 1.2f); gaugeGo.AddComponent<PrototypeDemandGauge>();
            return root;
        }
    }
}
