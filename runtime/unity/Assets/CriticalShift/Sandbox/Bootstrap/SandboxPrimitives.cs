using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace CriticalShift.Sandbox
{
    /// <summary>Owned debug geometry and materials for this fixture, never authored map assets.</summary>
    internal sealed class SandboxPrimitives : IDisposable
    {
        private readonly List<Material> materials = new List<Material>();
        internal readonly Material Floor, Steel, Dark, Yellow, Ore, Fuel, Wet, Lamp;

        internal SandboxPrimitives(Shader shader)
        {
            // Use the pipeline already configured in the project, without selecting or installing one.
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            if (pipeline != null && pipeline.GetType().FullName != "UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset")
                throw new InvalidOperationException("The fixture supports the existing Built-in profile or the owner-selected URP profile.");
            string expected = pipeline != null ? "Universal Render Pipeline/Lit" : "Standard";
            if (shader == null || shader.name != expected)
                throw new InvalidOperationException("Regenerate the fixture scene to bind the configured renderer's Lit shader.");
            Floor = CreateMaterial(shader, "Fixture floor", new Color(0.2f, 0.23f, 0.25f), 0.1f);
            Steel = CreateMaterial(shader, "Fixture painted steel", new Color(0.34f, 0.42f, 0.45f), 0.25f);
            Dark = CreateMaterial(shader, "Fixture belt and rubber", new Color(0.055f, 0.07f, 0.08f), 0.05f);
            Yellow = CreateMaterial(shader, "Fixture safety yellow", new Color(0.9f, 0.58f, 0.08f), 0.15f);
            Ore = CreateMaterial(shader, "Fixture ore crate", new Color(0.6f, 0.34f, 0.16f), 0.05f);
            Fuel = CreateMaterial(shader, "Fixture fuel crate", new Color(0.1f, 0.65f, 0.7f), 0.15f);
            Wet = CreateMaterial(shader, "Fixture wet ore", new Color(0.2f, 0.32f, 0.48f), 0.35f);
            Lamp = CreateMaterial(shader, "Fixture signal face", Color.white, 0.25f);
            Lamp.EnableKeyword("_EMISSION");
        }

        private Material CreateMaterial(Shader shader, string name, Color color, float smoothness)
        {
            var material = new Material(shader) { name = name };
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
            if (material.HasProperty("_Color")) material.SetColor("_Color", color);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", smoothness);
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", smoothness);
            materials.Add(material); return material;
        }

        internal static GameObject Empty(string name, Transform parent, Vector3 position)
        {
            var item = new GameObject(name); item.transform.SetParent(parent, false); item.transform.localPosition = position; return item;
        }

        internal static GameObject Box(string name, Transform parent, Vector3 position, Vector3 size, Material material, bool solid = true) =>
            Shape(PrimitiveType.Cube, name, parent, position, size, material, solid);

        internal static GameObject Shape(PrimitiveType kind, string name, Transform parent, Vector3 position,
            Vector3 size, Material material, bool solid = true)
        {
            var item = GameObject.CreatePrimitive(kind); item.name = name;
            item.transform.SetParent(parent, false); item.transform.localPosition = position; item.transform.localScale = size;
            item.GetComponent<Renderer>().sharedMaterial = material;
            if (!solid)
            {
                var collider = item.GetComponent<Collider>(); collider.enabled = false; UnityEngine.Object.Destroy(collider);
            }
            return item;
        }

        internal static Light PointLight(string name, Transform parent, Vector3 position, Color color, float intensity, float range)
        {
            var item = Empty(name, parent, position); var light = item.AddComponent<Light>();
            light.type = LightType.Point; light.color = color; light.intensity = intensity; light.range = range;
            light.shadows = LightShadows.None; return light;
        }

        public void Dispose()
        {
            foreach (var material in materials) if (material != null) UnityEngine.Object.Destroy(material);
            materials.Clear();
        }
    }
}
