using System;
using UnityEngine;

namespace CriticalShift.Presentation
{
    internal enum ProcessMoteStyle { Sparks, Vapour }

    /// <summary>Small prebound cosmetic pool. Uses supplied process time, with no random stream, colliders or gameplay callbacks.</summary>
    internal sealed class ProcessVisualPool
    {
        private readonly Transform[] markers;
        private readonly Renderer[] surfaces;
        private readonly Vector3[] sizes;
        private readonly MaterialPropertyBlock[] properties;
        private readonly ProcessMoteStyle style;
        internal int VisibleCount { get; private set; }
        internal bool Available
        {
            get
            {
                for (int i = 0; i < markers.Length; i++)
                    if (markers[i] == null || surfaces[i] == null) return false;
                return true;
            }
        }

        internal ProcessVisualPool(Transform owner, Transform[] items, ProcessMoteStyle motion)
        {
            if (items == null || items.Length == 0 || items.Length > 16) throw new ArgumentException("Bind a bounded cosmetic marker pool.");
            MovingVisualBindings.Validate(owner, items);
            markers = (Transform[])items.Clone(); surfaces = new Renderer[items.Length]; sizes = new Vector3[items.Length];
            properties = new MaterialPropertyBlock[items.Length]; style = motion;
            for (int i = 0; i < items.Length; i++)
            {
                if (items[i].GetComponent<Renderer>() == null)
                    throw new ArgumentException("Each cosmetic marker must have a renderer.");
                surfaces[i] = items[i].GetComponent<Renderer>(); sizes[i] = items[i].localScale;
                properties[i] = new MaterialPropertyBlock();
            }
            Hide();
        }

        internal void Show(double processSeconds, float amount, Color color)
        {
            if (double.IsNaN(processSeconds) || double.IsInfinity(processSeconds) || processSeconds < 0 ||
                float.IsNaN(amount) || float.IsInfinity(amount)) throw new ArgumentException("Cosmetic time and amount must be finite.");
            int visible = Mathf.CeilToInt(Mathf.Clamp01(amount) * markers.Length); VisibleCount = visible;
            float clock = (float)(processSeconds % 1000);
            for (int i = 0; i < markers.Length; i++)
            {
                bool show = i < visible;
                if (markers[i] == null || surfaces[i] == null) throw new InvalidOperationException("A bound process visual was lost.");
                if (markers[i].gameObject.activeSelf != show) markers[i].gameObject.SetActive(show);
                if (!show) continue;
                float age = Mathf.Repeat(clock * (style == ProcessMoteStyle.Sparks ? 2.4f : 0.65f) + i * 0.173f, 1);
                float angle = i * 2.399963f;
                if (style == ProcessMoteStyle.Sparks)
                {
                    markers[i].localPosition = new Vector3(Mathf.Sin(angle) * age * 0.35f, age * 0.35f - age * age * 0.65f, -age * 0.3f);
                    markers[i].localRotation = Quaternion.Euler(age * 340, i * 47, age * 170);
                    markers[i].localScale = sizes[i] * Mathf.Lerp(1, 0.15f, age);
                }
                else
                {
                    markers[i].localPosition = new Vector3(Mathf.Sin(angle + age) * age * 0.18f, age * 0.9f, Mathf.Cos(angle + age) * age * 0.18f);
                    markers[i].localScale = sizes[i] * Mathf.Lerp(0.5f, 1.8f, age);
                }
                surfaces[i].GetPropertyBlock(properties[i]);
                properties[i].SetColor("_BaseColor", color); properties[i].SetColor("_Color", color);
                properties[i].SetColor("_EmissionColor", color * (style == ProcessMoteStyle.Sparks ? 1.5f : 0.05f));
                surfaces[i].SetPropertyBlock(properties[i]);
            }
        }

        internal void Hide()
        {
            VisibleCount = 0;
            foreach (var marker in markers) if (marker != null) marker.gameObject.SetActive(false);
        }
    }
}
