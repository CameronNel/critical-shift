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
        internal readonly PhysicsMaterial WheelContact, WorkerContact;

        internal SandboxPrimitives(Shader shader, Material litTemplate = null, Material emissionTemplate = null)
        {
            // Use the pipeline already configured in the project, without selecting or installing one.
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            if (pipeline != null && pipeline.GetType().FullName != "UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset")
                throw new InvalidOperationException("The fixture supports the existing Built-in profile or the owner-selected URP profile.");
            string expected = pipeline != null ? "Universal Render Pipeline/Lit" : "Standard";
            if (shader == null || shader.name != expected)
                throw new InvalidOperationException("Regenerate the fixture scene to bind the configured renderer's Lit shader.");
            if (litTemplate != null || emissionTemplate != null)
                ValidateMaterialTemplates(shader, litTemplate, emissionTemplate);
            else if (!UnityEngine.Application.isEditor)
                throw new InvalidOperationException("Regenerate the Player scene with both serialized Lit material variants.");
            try
            {
                Floor = CreateMaterial(shader, litTemplate, "Fixture floor", new Color(0.2f, 0.23f, 0.25f), 0.1f);
                Steel = CreateMaterial(shader, litTemplate, "Fixture painted steel", new Color(0.34f, 0.42f, 0.45f), 0.25f);
                Dark = CreateMaterial(shader, litTemplate, "Fixture belt and rubber", new Color(0.055f, 0.07f, 0.08f), 0.05f);
                Yellow = CreateMaterial(shader, litTemplate, "Fixture safety yellow", new Color(0.9f, 0.58f, 0.08f), 0.15f);
                Ore = CreateMaterial(shader, litTemplate, "Fixture ore crate", new Color(0.6f, 0.34f, 0.16f), 0.05f);
                Fuel = CreateMaterial(shader, litTemplate, "Fixture fuel crate", new Color(0.1f, 0.65f, 0.7f), 0.15f);
                Wet = CreateMaterial(shader, litTemplate, "Fixture wet ore", new Color(0.2f, 0.32f, 0.48f), 0.35f);
                Lamp = CreateMaterial(shader, emissionTemplate, "Fixture signal face", Color.white, 0.25f);
                Lamp.EnableKeyword("_EMISSION");
                Lamp.SetColor("_EmissionColor", Color.black);
                // Track native objects before configuring them so failed setup still owns cleanup.
                WheelContact = new PhysicsMaterial("Fixture wheel rolling resistance");
                WheelContact.staticFriction = 0.02f; WheelContact.dynamicFriction = 0.02f; WheelContact.bounciness = 0;
                WheelContact.frictionCombine = PhysicsMaterialCombine.Minimum; WheelContact.bounceCombine = PhysicsMaterialCombine.Minimum;
                WorkerContact = new PhysicsMaterial("Fixture worker suit contact");
                WorkerContact.staticFriction = 0.18f; WorkerContact.dynamicFriction = 0.15f; WorkerContact.bounciness = 0;
                WorkerContact.frictionCombine = PhysicsMaterialCombine.Minimum; WorkerContact.bounceCombine = PhysicsMaterialCombine.Minimum;
            }
            catch { Dispose(); throw; }
        }

        internal static void ValidateMaterialTemplates(Shader shader, Material litTemplate, Material emissionTemplate)
        {
            if (shader == null || shader.name != "Universal Render Pipeline/Lit" || litTemplate == null || emissionTemplate == null ||
                litTemplate == emissionTemplate || litTemplate.shader != shader || emissionTemplate.shader != shader ||
                litTemplate.shaderKeywords.Length != 0 || emissionTemplate.shaderKeywords.Length != 1 ||
                (emissionTemplate.globalIlluminationFlags & MaterialGlobalIlluminationFlags.AnyEmissive) == 0 ||
                !emissionTemplate.IsKeywordEnabled("_EMISSION") || !emissionTemplate.HasProperty("_EmissionColor"))
                throw new InvalidOperationException("Bind distinct ordinary and emissive URP Lit templates with only their retained keyword combinations.");
        }

        private Material CreateMaterial(Shader shader, Material template, string name, Color color, float smoothness)
        {
            // Templates are serialized dependency roots. This fixture owns and later destroys only these runtime clones.
            var material = template == null ? new Material(shader) : new Material(template);
            materials.Add(material); material.name = name;
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
            if (material.HasProperty("_Color")) material.SetColor("_Color", color);
            if (material.HasProperty("_Smoothness")) material.SetFloat("_Smoothness", smoothness);
            if (material.HasProperty("_Glossiness")) material.SetFloat("_Glossiness", smoothness);
            return material;
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
            if (kind != PrimitiveType.Cube && kind != PrimitiveType.Sphere && kind != PrimitiveType.Capsule && kind != PrimitiveType.Cylinder)
                throw new ArgumentException("This fixture only uses box, sphere, capsule and cylinder primitives.");
            var item = GameObject.CreatePrimitive(kind); item.name = name;
            item.transform.SetParent(parent, false); item.transform.localPosition = position; item.transform.localScale = size;
            // Concrete references keep runtime-created primitive components visible to Player stripping.
            var renderer = item.GetComponent<MeshRenderer>(); var filter = item.GetComponent<MeshFilter>();
            if (renderer == null || filter == null || filter.sharedMesh == null || filter.sharedMesh.vertexCount == 0)
                throw new InvalidOperationException("A fixture primitive lost its mesh components in this runtime: " + kind);
            renderer.sharedMaterial = material;
            Collider collider = kind == PrimitiveType.Cube ? (Collider)item.GetComponent<BoxCollider>() :
                kind == PrimitiveType.Sphere ? (Collider)item.GetComponent<SphereCollider>() : item.GetComponent<CapsuleCollider>();
            if (collider == null) throw new InvalidOperationException("A fixture primitive lost its expected collision component: " + kind);
            if (!solid)
            {
                collider.enabled = false; UnityEngine.Object.Destroy(collider);
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
            if (WheelContact != null) UnityEngine.Object.Destroy(WheelContact);
            if (WorkerContact != null) UnityEngine.Object.Destroy(WorkerContact);
        }
    }
}
