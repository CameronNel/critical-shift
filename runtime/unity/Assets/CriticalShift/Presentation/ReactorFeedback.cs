using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Source-backed reactor beacon and cooling-valve presentation, with no gameplay writes.</summary>
    public sealed class ReactorFeedback : MonoBehaviour
    {
        private LocalCommandPort queries;
        private Renderer shell;
        private Light beacon;
        private Transform valve;
        private Quaternion valveRest;
        private ProcessVisualPool vapour;
        public int VisibleMoteCount => vapour == null ? 0 : vapour.VisibleCount;
        private readonly MaterialPropertyBlock properties = new MaterialPropertyBlock();

        public void Initialize(LocalCommandPort read, Renderer statusShell, Light warningBeacon, Transform coolingValve, Transform[] ventMotes)
        {
            if (queries != null || read == null || statusShell == null || warningBeacon == null || coolingValve == null)
                throw new ArgumentException("Reactor feedback requires explicit bindings.");
            queries = read; shell = statusShell; beacon = warningBeacon; valve = coolingValve; valveRest = valve.localRotation;
            vapour = new ProcessVisualPool(ventMotes, ProcessMoteStyle.Vapour);
        }

        private void LateUpdate()
        {
            if (queries == null || shell == null || beacon == null || valve == null) return;
            var state = queries.Reactor;
            var world = queries.World;
            bool live = world.Phase == WorldPhase.Running || world.Phase == WorldPhase.Paused;
            bool warning = live && state != null && (state.InstabilityMilliseconds > 0 || state.Mode == ReactorMode.Tripped);
            bool running = live && state != null && state.Mode == ReactorMode.Running;
            Color color = warning ? new Color(1f, 0.12f, 0.02f) : running ? new Color(0.1f, 0.75f, 0.85f) : new Color(0.2f, 0.3f, 0.35f);
            float pulse = warning ? 0.4f + 1.1f * Mathf.Abs(Mathf.Sin(world.ElapsedMilliseconds * 0.009f)) : running ? 0.8f : 0.1f;
            shell.GetPropertyBlock(properties); properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            properties.SetColor("_EmissionColor", color * pulse); shell.SetPropertyBlock(properties);
            beacon.color = color; beacon.intensity = pulse;
            if (live && state != null && (warning || running))
                vapour.Show(world.ElapsedMilliseconds * 0.001, warning ? 1 : 0.3f,
                    warning ? new Color(0.75f, 0.5f, 0.45f) : new Color(0.6f, 0.75f, 0.8f));
            else vapour.Hide();
            Quaternion target = valveRest * Quaternion.AngleAxis(state != null && state.Cooling ? 90 : 0, Vector3.forward);
            valve.localRotation = Quaternion.RotateTowards(valve.localRotation, target, 180 * Time.deltaTime);
        }

        private void OnDisable() { if (beacon != null) beacon.intensity = 0; vapour?.Hide(); }
    }
}
