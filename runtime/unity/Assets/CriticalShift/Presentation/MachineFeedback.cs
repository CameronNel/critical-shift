using System;
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
        private Quaternion rotorRest;
        private readonly MaterialPropertyBlock properties = new MaterialPropertyBlock();

        public void Initialize(LocalCommandPort read, Guid machine, Renderer statusFace, Light statusLamp, Transform spindle)
        {
            if (queries != null || read == null || machine == Guid.Empty || statusFace == null || statusLamp == null || spindle == null)
                throw new ArgumentException("Machine feedback needs explicit query, renderer, light and spindle bindings.");
            queries = read; id = machine; face = statusFace; lamp = statusLamp; rotor = spindle; rotorRest = spindle.localRotation;
        }

        private void LateUpdate()
        {
            if (queries == null || face == null || lamp == null || rotor == null) return;
            var state = queries.GetMachine(id);
            Color color = new Color(0.15f, 0.2f, 0.25f); float strength = 0.1f;
            if (state != null && state.Powered)
            {
                color = new Color(0.2f, 0.8f, 0.45f); strength = 0.65f;
                if (state.Mode == ProductionMode.Processing) { color = new Color(0.95f, 0.65f, 0.15f); strength = 1.1f; }
                if (state.Mode == ProductionMode.OutputReady) { color = new Color(0.2f, 0.65f, 1f); strength = 1.2f; }
                if (state.Mode == ProductionMode.Jammed)
                {
                    color = new Color(1f, 0.12f, 0.04f);
                    strength = 0.5f + 0.9f * (0.5f + 0.5f * Mathf.Sin(queries.World.ElapsedMilliseconds * 0.012f));
                }
            }
            face.GetPropertyBlock(properties);
            properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            properties.SetColor("_EmissionColor", color * strength);
            face.SetPropertyBlock(properties); lamp.color = color; lamp.intensity = strength;
            if (state != null)
            {
                Quaternion target = rotorRest * Quaternion.AngleAxis((state.WorkMilliseconds % 6000) * 0.12f, Vector3.forward);
                rotor.localRotation = Quaternion.RotateTowards(rotor.localRotation, target, 900 * Time.deltaTime);
            }
        }

        private void OnDisable() { if (lamp != null) lamp.intensity = 0; }
    }
}
