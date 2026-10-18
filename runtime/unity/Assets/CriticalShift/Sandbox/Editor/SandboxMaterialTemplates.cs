using System;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace CriticalShift.Sandbox.Editor
{
    /// <summary>Serialized dependency roots for the two Lit keyword combinations created by the fixture at runtime.</summary>
    internal static class SandboxMaterialTemplates
    {
        internal const string LitPath = SandboxRenderPipeline.Folder + "/TraversalLit.mat";
        internal const string EmissionPath = SandboxRenderPipeline.Folder + "/TraversalEmission.mat";

        internal static void Prepare(Shader shader, out Material lit, out Material emission)
        {
            if (shader == null || shader.name != "Universal Render Pipeline/Lit" || !AssetDatabase.IsValidFolder(SandboxRenderPipeline.Folder))
                throw new BuildFailedException("Prepare the sandbox URP renderer and Lit shader before its material templates.");
            // Inspect the complete existing pair before creating assets or altering any existing reference.
            lit = Read(LitPath); emission = Read(EmissionPath);
            if ((lit == null) != (emission == null))
                throw new BuildFailedException("The fixture material-template pair is incomplete; preserve it for review.");
            if (lit == null)
            {
                lit = Create(shader, LitPath, "Traversal Lit template", false);
                emission = Create(shader, EmissionPath, "Traversal emission template", true);
                AssetDatabase.SaveAssets();
            }
            Validate(shader, lit, emission);
        }

        internal static void Validate(Shader shader, Material lit, Material emission)
        {
            if (shader == null || shader.name != "Universal Render Pipeline/Lit" || lit == null || emission == null || lit == emission ||
                lit != Read(LitPath) || emission != Read(EmissionPath) || lit.shader != shader || emission.shader != shader ||
                lit.shaderKeywords.Length != 0 || emission.shaderKeywords.Length != 1 || !emission.IsKeywordEnabled("_EMISSION") ||
                (emission.globalIlluminationFlags & MaterialGlobalIlluminationFlags.AnyEmissive) == 0 ||
                !emission.HasProperty("_EmissionColor"))
                throw new BuildFailedException("Regenerate the scene with the canonical ordinary/emissive URP Lit material dependency roots.");
        }

        private static Material Read(string path)
        {
            if (!AssetDatabase.AssetPathExists(path)) return null;
            var material = AssetDatabase.LoadMainAssetAtPath(path) as Material;
            var assets = AssetDatabase.LoadAllAssetsAtPath(path);
            if (material == null || assets.Length < 1 || assets.Length > 2)
                throw new BuildFailedException("An unexpected asset occupies the fixture material-template path: " + path);
            // URP 17.4's material postprocessor owns one hidden version subasset. Preserve that native metadata.
            foreach (var asset in assets)
                if (asset != material && (asset == null || !AssetDatabase.IsSubAsset(asset) ||
                    asset.GetType().FullName != "UnityEditor.Rendering.Universal.AssetVersion" ||
                    asset.GetType().Assembly.GetName().Name != "Unity.RenderPipelines.Universal.Editor" ||
                    asset.hideFlags != (HideFlags.HideInHierarchy | HideFlags.HideInInspector | HideFlags.NotEditable)))
                    throw new BuildFailedException("Unexpected material subasset at the fixture template path: " + path);
            return material;
        }

        private static Material Create(Shader shader, string path, string name, bool emissive)
        {
            Material material = null;
            try
            {
                material = new Material(shader) { name = name, shaderKeywords = Array.Empty<string>() };
                if (emissive)
                {
                    material.SetColor("_EmissionColor", Color.white);
                    // URP's importer derives _EMISSION from these flags; this template retains a variant, it runs no bake.
                    material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                    MaterialEditor.FixupEmissiveFlag(material);
                    material.EnableKeyword("_EMISSION");
                }
                AssetDatabase.CreateAsset(material, path);
                return material;
            }
            catch
            {
                if (material != null && !AssetDatabase.Contains(material)) UnityEngine.Object.DestroyImmediate(material);
                throw;
            }
        }
    }
}
