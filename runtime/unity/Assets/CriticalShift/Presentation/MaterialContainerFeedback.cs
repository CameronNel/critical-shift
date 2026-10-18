using System;
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
        private Guid lastBatch;
        private long lastRevision = -1;
        private readonly MaterialPropertyBlock properties = new MaterialPropertyBlock();

        public void Initialize(LocalCommandPort read, Guid container, Renderer renderer)
        {
            if (queries != null || read == null || container == Guid.Empty || renderer == null)
                throw new ArgumentException("Bind one explicit material-container projection and surface.");
            queries = read; id = container; surface = renderer;
        }

        private void LateUpdate()
        {
            if (queries == null || surface == null) return;
            var batch = queries.GetBatch(id);
            if (batch == null || (batch.BatchId == lastBatch && batch.Revision == lastRevision)) return;
            lastBatch = batch.BatchId; lastRevision = batch.Revision;
            Color color = batch.Kind == MaterialKind.Fuel ? new Color(0.1f, 0.65f, 0.7f) :
                batch.Kind == MaterialKind.SpentFuel ? new Color(0.3f, 0.25f, 0.32f) :
                batch.Kind == MaterialKind.CrushedOre ? new Color(0.75f, 0.55f, 0.25f) : new Color(0.6f, 0.34f, 0.16f);
            if (batch.Moisture > 500) color = Color.Lerp(color, new Color(0.15f, 0.3f, 0.5f), 0.6f);
            if (batch.Flags != MaterialFlags.None || batch.Contamination > 500) color = Color.Lerp(color, new Color(0.7f, 0.2f, 0.1f), 0.35f);
            surface.GetPropertyBlock(properties); properties.SetColor("_BaseColor", color); properties.SetColor("_Color", color);
            surface.SetPropertyBlock(properties);
        }
    }
}
