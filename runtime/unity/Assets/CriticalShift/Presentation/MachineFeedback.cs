using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Machine lamp, emissive face and rotor animation derived from committed projections.</summary>
    public sealed class MachineFeedback : MonoBehaviour
    {
        private LocalCommandPort queries;
        private Guid id;
        private Renderer face;
        private Light lamp;
        private Transform rotor;
        private Transform progress;
        private Transform powerLever;
        private Transform ram;
        private Transform[] clamps;
        private Vector3 ramRest;
        private Vector3[] clampRest;
        private Quaternion leverRest;
        private Vector3 progressSize, progressLeft;
        private ProcessVisualPool sparks;
        public float DisplayedProgress { get; private set; }
        public int VisibleMoteCount => sparks == null ? 0 : sparks.VisibleCount;
        private Quaternion rotorRest;
        private readonly MaterialPropertyBlock properties = new MaterialPropertyBlock();

        public void Initialize(LocalCommandPort read, Guid machine, Renderer statusFace, Light statusLamp, Transform spindle,
            Transform progressFill, Transform[] processSparks, Transform powerSwitch, Transform processRam, Transform[] loadingClamps)
        {
            if (queries != null || read == null || machine == Guid.Empty || statusFace == null || statusLamp == null || spindle == null ||
                progressFill == null || powerSwitch == null || processRam == null || loadingClamps == null || loadingClamps.Length != 2 ||
                loadingClamps[0] == null || loadingClamps[1] == null || loadingClamps[0] == loadingClamps[1] ||
                loadingClamps[0] == processRam || loadingClamps[1] == processRam)
                throw new ArgumentException("Machine feedback needs explicit query, renderer, light and spindle bindings.");
            var moving = new HashSet<Transform> { spindle, progressFill, powerSwitch, processRam, loadingClamps[0], loadingClamps[1] };
            if (moving.Count != 6) throw new ArgumentException("Each moving machine visual needs its own transform.");
            foreach (var pivot in moving)
            {
                if (pivot.GetComponentsInChildren<Rigidbody>().Length != 0) throw new ArgumentException("Machine presentation cannot move physical bodies.");
                foreach (var collider in pivot.GetComponentsInChildren<Collider>())
                    if (collider.enabled) throw new ArgumentException("Moving machine visuals must be non-contacting.");
            }
            queries = read; id = machine; face = statusFace; lamp = statusLamp; rotor = spindle; rotorRest = spindle.localRotation;
            progress = progressFill; progressSize = progress.localScale;
            powerLever = powerSwitch; leverRest = powerSwitch.localRotation;
            ram = processRam; ramRest = ram.localPosition; clamps = (Transform[])loadingClamps.Clone();
            clampRest = new[] { clamps[0].localPosition, clamps[1].localPosition };
            progressLeft = progress.localPosition - Vector3.right * progressSize.x * 0.5f;
            sparks = new ProcessVisualPool(processSparks, ProcessMoteStyle.Sparks);
        }

        private void LateUpdate()
        {
            if (queries == null || face == null || lamp == null || rotor == null || progress == null || powerLever == null ||
                ram == null || clamps[0] == null || clamps[1] == null) return;
            var state = queries.GetMachine(id);
            var world = queries.World;
            bool live = world.Phase == WorldPhase.Running || world.Phase == WorldPhase.Paused;
            Color color = new Color(0.15f, 0.2f, 0.25f); float strength = 0.1f;
            if (live && state != null && state.Powered)
            {
                color = new Color(0.2f, 0.8f, 0.45f); strength = 0.65f;
                if (state.Mode == ProductionMode.Processing) { color = new Color(0.95f, 0.65f, 0.15f); strength = 1.1f; }
                if (state.Mode == ProductionMode.OutputReady) { color = new Color(0.2f, 0.65f, 1f); strength = 1.2f; }
            }
            if (live && state != null && state.Mode == ProductionMode.Jammed)
            {
                color = new Color(1f, 0.12f, 0.04f);
                strength = state.Powered ? 0.5f + 0.9f * (0.5f + 0.5f * Mathf.Sin(world.ElapsedMilliseconds * 0.012f)) : 0.05f;
            }
            face.GetPropertyBlock(properties);
            properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            properties.SetColor("_EmissionColor", color * strength);
            face.SetPropertyBlock(properties); lamp.color = color; lamp.intensity = strength;
            UpdateMotion(state, live);
        }

        private void UpdateMotion(MachineView state, bool live)
        {
            Quaternion leverTarget = leverRest * Quaternion.AngleAxis(live && state != null && state.Powered ? 40 : -40, Vector3.forward);
            powerLever.localRotation = Quaternion.RotateTowards(powerLever.localRotation, leverTarget, 240 * Mathf.Min(Time.deltaTime, 0.05f));
            DisplayedProgress = !live || state == null || state.DurationMilliseconds <= 0 ? 0 :
                Mathf.Clamp01((float)((double)state.WorkMilliseconds / state.DurationMilliseconds));
            float width = progressSize.x * Mathf.Max(0.001f, DisplayedProgress);
            progress.localScale = new Vector3(width, progressSize.y, progressSize.z);
            progress.localPosition = progressLeft + Vector3.right * width * 0.5f;
            bool loaded = live && state != null && state.ContainerId.HasValue;
            for (int i = 0; i < clamps.Length; i++)
            {
                Vector3 target = clampRest[i] + Vector3.right * (loaded ? (i == 0 ? 0.18f : -0.18f) : 0);
                clamps[i].localPosition = Vector3.MoveTowards(clamps[i].localPosition, target, 3 * Mathf.Min(Time.deltaTime, 0.05f));
            }
            bool cycleHeld = loaded && (state.Mode == ProductionMode.Processing || state.Mode == ProductionMode.PowerPaused || state.Mode == ProductionMode.Jammed);
            float stroke = cycleHeld ? 0.08f * (0.5f - 0.5f * Mathf.Cos((state.WorkMilliseconds % 800) * (Mathf.PI * 2 / 800))) : 0;
            ram.localPosition = ramRest + Vector3.down * stroke;
            if (live && state != null && state.Mode == ProductionMode.Processing && state.Powered)
                sparks.Show(state.WorkMilliseconds * 0.001, 1, new Color(1, 0.65f, 0.12f));
            else sparks.Hide();
            if (state != null)
            {
                Quaternion target = rotorRest * Quaternion.AngleAxis((state.WorkMilliseconds % 6000) * 0.12f, Vector3.forward);
                rotor.localRotation = Quaternion.RotateTowards(rotor.localRotation, target, 900 * Time.deltaTime);
            }
        }

        private void OnDisable() { if (lamp != null) lamp.intensity = 0; sparks?.Hide(); }
    }
}
