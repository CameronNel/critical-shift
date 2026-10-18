using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Container appearance follows the current batch, including conversion and inspection history.</summary>
    public sealed class MaterialContainerFeedback : MonoBehaviour
    {
        private LocalCommandPort queries;
        private Guid id;
        private Renderer surface;
        private Transform[] contents;
        private Renderer[] contentRenderers;
        private Vector3[] positions, scales;
        private Quaternion[] rotations;
        private int capacity;
        public float DisplayedFill { get; private set; }
        public int VisibleContentCount { get; private set; }
        private Guid lastBatch;
        private long lastRevision = -1;
        private readonly MaterialPropertyBlock properties = new MaterialPropertyBlock();

        public void Initialize(LocalCommandPort read, Guid container, Renderer renderer, Transform[] contentMarkers, int capacityUnits)
        {
            if (queries != null || read == null || container == Guid.Empty || renderer == null || contentMarkers == null ||
                contentMarkers.Length == 0 || contentMarkers.Length > 16 || capacityUnits < 1)
                throw new ArgumentException("Bind one explicit material-container projection and surface.");
            var unique = new HashSet<Renderer> { renderer };
            var visuals = new Renderer[contentMarkers.Length];
            for (int i = 0; i < contentMarkers.Length; i++)
            {
                var item = contentMarkers[i];
                visuals[i] = item == null ? null : item.GetComponent<Renderer>();
                if (item == null || visuals[i] == null || !unique.Add(visuals[i]) || item.GetComponent<Rigidbody>() != null)
                    throw new ArgumentException("Each bounded content marker needs its own non-physical renderer.");
                foreach (var collider in item.GetComponentsInChildren<Collider>())
                    if (collider.enabled) throw new ArgumentException("Visible contents cannot add contact colliders.");
            }
            queries = read; id = container; surface = renderer;
            contents = (Transform[])contentMarkers.Clone(); contentRenderers = visuals; capacity = capacityUnits;
            positions = new Vector3[contents.Length]; scales = new Vector3[contents.Length]; rotations = new Quaternion[contents.Length];
            for (int i = 0; i < contents.Length; i++)
            { positions[i] = contents[i].localPosition; scales[i] = contents[i].localScale; rotations[i] = contents[i].localRotation; }
        }

        private void LateUpdate()
        {
            if (queries == null) return;
            if (surface == null) { enabled = false; throw new InvalidOperationException("A bound container surface was lost."); }
            for (int i = 0; i < contents.Length; i++)
                if (contents[i] == null || contentRenderers[i] == null)
                { enabled = false; throw new InvalidOperationException("A bound content visual was lost."); }
            var batch = queries.GetBatch(id);
            if (batch == null) { Hide(); return; }
            if (batch.BatchId == lastBatch && batch.Revision == lastRevision) return;
            lastBatch = batch.BatchId; lastRevision = batch.Revision;
            Color color = batch.Kind == MaterialKind.Fuel ? new Color(0.1f, 0.65f, 0.7f) :
                batch.Kind == MaterialKind.SpentFuel ? new Color(0.3f, 0.25f, 0.32f) :
                batch.Kind == MaterialKind.CrushedOre ? new Color(0.75f, 0.55f, 0.25f) : new Color(0.6f, 0.34f, 0.16f);
            if (batch.Moisture > 500) color = Color.Lerp(color, new Color(0.15f, 0.3f, 0.5f), 0.6f);
            if (batch.Flags != MaterialFlags.None || batch.Contamination > 500) color = Color.Lerp(color, new Color(0.7f, 0.2f, 0.1f), 0.35f);
            Paint(surface, color);
            DisplayedFill = Mathf.Clamp01((float)batch.Units / capacity);
            VisibleContentCount = Mathf.CeilToInt(contents.Length * DisplayedFill);
            Vector3 shape = batch.Kind == MaterialKind.CrushedOre ? new Vector3(1.1f, 0.6f, 1.1f) :
                batch.Kind == MaterialKind.Fuel || batch.Kind == MaterialKind.SpentFuel ? new Vector3(0.65f, 1.5f, 0.65f) : Vector3.one;
            for (int i = 0; i < contents.Length; i++)
            {
                contentRenderers[i].enabled = i < VisibleContentCount;
                var position = positions[i]; position.y = -0.33f + (position.y + 0.33f) * Mathf.Lerp(0.35f, 1, DisplayedFill);
                contents[i].localPosition = position; contents[i].localScale = Vector3.Scale(scales[i], shape);
                contents[i].localRotation = rotations[i] * (batch.Kind == MaterialKind.Ore ? Quaternion.Euler(i * 13 % 25, i * 37, i * 17 % 30) :
                    batch.Kind == MaterialKind.CrushedOre ? Quaternion.Euler(0, i * 53, 0) : Quaternion.identity);
                Paint(contentRenderers[i], color);
            }
        }

        private void Paint(Renderer renderer, Color color)
        {
            renderer.GetPropertyBlock(properties); properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            renderer.SetPropertyBlock(properties);
        }
        private void Hide()
        {
            DisplayedFill = 0; VisibleContentCount = 0; lastBatch = Guid.Empty; lastRevision = -1;
            if (contentRenderers != null) foreach (var renderer in contentRenderers) if (renderer != null) renderer.enabled = false;
        }
        private void OnDisable() => Hide();
    }
}
