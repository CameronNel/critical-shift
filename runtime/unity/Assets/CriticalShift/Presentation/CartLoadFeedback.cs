using System;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Physical-load warning from injected observations, without a dependency on the cart implementation.</summary>
    public sealed class CartLoadFeedback : MonoBehaviour
    {
        private Renderer surface;
        private Light lamp;
        private Func<bool> overloaded, unavailable;
        private MaterialPropertyBlock properties;

        public void Initialize(Renderer face, Light beacon, Func<bool> readOverload, Func<bool> readUnavailable)
        {
            if (surface != null || face == null || beacon == null) throw new ArgumentException("Bind one explicit load-warning face and light.");
            surface = face; lamp = beacon;
            overloaded = readOverload ?? throw new ArgumentNullException(nameof(readOverload));
            unavailable = readUnavailable ?? throw new ArgumentNullException(nameof(readUnavailable));
            properties = new MaterialPropertyBlock();
        }

        private void LateUpdate()
        {
            if (overloaded == null || unavailable == null) return;
            if (surface == null || lamp == null)
            { enabled = false; throw new InvalidOperationException("A bound cart load presentation part was lost."); }
            bool missing = unavailable(), heavy = overloaded();
            Color color = missing ? new Color(1, 0.08f, 0.02f) : heavy ? new Color(1, 0.55f, 0.02f) : new Color(0.1f, 0.65f, 0.3f);
            float strength = missing ? 0.3f + Mathf.Abs(Mathf.Sin(Time.unscaledTime * 8)) : heavy ? 0.8f : 0.15f;
            surface.GetPropertyBlock(properties); properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            properties.SetColor("_EmissionColor", color * strength); surface.SetPropertyBlock(properties);
            lamp.color = color; lamp.intensity = strength;
        }

        private void OnDisable() { if (lamp != null) lamp.intensity = 0; }
    }
}
