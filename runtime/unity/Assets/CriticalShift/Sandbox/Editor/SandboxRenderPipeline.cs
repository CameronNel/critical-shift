using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.PackageManager;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace CriticalShift.Sandbox.Editor
{
    /// <summary>Explicit, idempotent preparation of the owner-selected URP trial. Never installs packages.</summary>
    public static class SandboxRenderPipeline
    {
        public const string PackageVersion = "17.4.0";
        public const string PackagePath = "Packages/com.unity.render-pipelines.universal";
        public const string Folder = "Assets/CriticalShift/Sandbox/Rendering";
        public const string RendererPath = Folder + "/TraversalRenderer.asset";
        public const string PipelinePath = Folder + "/TraversalURP.asset";
        private const string Parent = "Assets/CriticalShift/Sandbox";

        public static void Prepare()
        {
            // Inspect every existing reference and both destination assets before changing any of them.
            Inspect(false, out var renderer, out var pipeline, out var postProcess);
            int quality = QualitySettings.GetQualityLevel();
            if (!AssetDatabase.IsValidFolder(Folder))
            {
                string guid = AssetDatabase.CreateFolder(Parent, "Rendering");
                if (string.IsNullOrEmpty(guid)) throw new BuildFailedException("Could not create the sandbox rendering folder.");
            }
            if (renderer == null)
            {
                try
                {
                    renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
                    renderer.name = "TraversalRenderer";
                    renderer.postProcessData = postProcess;
                    ResourceReloader.ReloadAllNullIn(renderer, PackagePath);
                    AssetDatabase.CreateAsset(renderer, RendererPath);
                    pipeline = UniversalRenderPipelineAsset.Create(renderer);
                    pipeline.name = "TraversalURP";
                    AssetDatabase.CreateAsset(pipeline, PipelinePath);
                }
                catch
                {
                    // Dispose only transient objects. Persisted partial assets remain available for review.
                    if (pipeline != null && !AssetDatabase.Contains(pipeline)) UnityEngine.Object.DestroyImmediate(pipeline);
                    if (renderer != null && !AssetDatabase.Contains(renderer)) UnityEngine.Object.DestroyImmediate(renderer);
                    throw;
                }
            }
            GraphicsSettings.defaultRenderPipeline = pipeline;
            PlayerSettings.colorSpace = ColorSpace.Linear;
            try
            {
                for (int i = 0; i < QualitySettings.names.Length; i++)
                {
                    QualitySettings.SetQualityLevel(i, false);
                    QualitySettings.renderPipeline = null; // Every level inherits the one canonical default.
                }
            }
            finally { QualitySettings.SetQualityLevel(quality, false); }
            AssetDatabase.SaveAssets();
            Validate();
            Debug.Log("CS_SANDBOX_URP_PREPARED version=" + PackageVersion + " pipeline=" + PipelinePath);
        }

        public static void Validate()
        {
            Inspect(true, out _, out var pipeline, out _);
            if (GraphicsSettings.defaultRenderPipeline != pipeline)
                throw new BuildFailedException("Graphics Settings must reference the canonical sandbox URP asset.");
            if (PlayerSettings.colorSpace != ColorSpace.Linear)
                throw new BuildFailedException("The selected URP Lit profile requires Linear color space.");
            for (int i = 0; i < QualitySettings.names.Length; i++)
                if (QualitySettings.GetRenderPipelineAssetAt(i) != null)
                    throw new BuildFailedException("Every quality level must inherit the canonical URP asset; override at index " + i);
            Debug.Log("CS_SANDBOX_URP_VALIDATED version=" + PackageVersion + " quality_levels=" + QualitySettings.names.Length);
        }

        private static void Inspect(bool requireAssets, out UniversalRendererData renderer,
            out UniversalRenderPipelineAsset pipeline, out PostProcessData postProcess)
        {
            RequirePackages();
            if (!AssetDatabase.IsValidFolder(Parent) ||
                (AssetDatabase.AssetPathExists(Folder) && !AssetDatabase.IsValidFolder(Folder)))
                throw new BuildFailedException("The canonical sandbox parent/folder is missing or occupied by another asset.");
            renderer = ReadOwnedAsset<UniversalRendererData>(RendererPath);
            pipeline = ReadOwnedAsset<UniversalRenderPipelineAsset>(PipelinePath);
            if ((renderer == null) != (pipeline == null))
                throw new BuildFailedException("The canonical URP asset pair is incomplete. Preserve and review it before retrying.");
            if (requireAssets && renderer == null)
                throw new BuildFailedException("Prepare the canonical sandbox URP assets first.");
            postProcess = AssetDatabase.LoadAssetAtPath<PostProcessData>(PackagePath + "/Runtime/Data/PostProcessData.asset");
            if (postProcess == null) throw new BuildFailedException("The pinned URP package's default post-process resources are missing.");
            RequireGlobalSettings();
            int quality = QualitySettings.GetQualityLevel();
            if (QualitySettings.names.Length == 0 || quality < 0 || quality >= QualitySettings.names.Length)
                throw new BuildFailedException("The project has no valid current quality level.");
            if (renderer != null)
            {
                if (renderer.renderingMode != RenderingMode.Forward || renderer.rendererFeatures.Count != 0 ||
                    renderer.postProcessData != postProcess)
                    throw new BuildFailedException("The canonical renderer differs from the pinned package's default Forward/resources profile.");
                if (pipeline.rendererDataList.Length != 1 || pipeline.rendererDataList[0] != renderer ||
                    pipeline.renderScale != 1 || pipeline.msaaSampleCount != 1 || !pipeline.supportsHDR || !pipeline.useSRPBatcher)
                    throw new BuildFailedException("The canonical pipeline differs from the single-renderer stock-default trial profile.");
            }
            if (GraphicsSettings.defaultRenderPipeline != null && GraphicsSettings.defaultRenderPipeline != pipeline)
                throw new BuildFailedException("An unexpected default render pipeline is already configured; no settings were replaced.");
            for (int i = 0; i < QualitySettings.names.Length; i++)
            {
                var current = QualitySettings.GetRenderPipelineAssetAt(i);
                if (current != null && current != pipeline)
                    throw new BuildFailedException("An unexpected quality render pipeline is configured at index " + i + "; no settings were replaced.");
            }
        }

        private static T ReadOwnedAsset<T>(string path) where T : UnityEngine.Object
        {
            if (!AssetDatabase.AssetPathExists(path)) return null;
            var asset = AssetDatabase.LoadMainAssetAtPath(path);
            if (asset == null || asset.GetType() != typeof(T) || AssetDatabase.LoadAllAssetsAtPath(path).Length != 1)
                throw new BuildFailedException("An unexpected or unreadable asset occupies the canonical path: " + path);
            return (T)asset;
        }

        private static void RequirePackages()
        {
            var registered = UnityEditor.PackageManager.PackageInfo.GetAllRegisteredPackages();
            foreach (string name in new[] { "com.unity.render-pipelines.universal", "com.unity.render-pipelines.core",
                "com.unity.shadergraph", "com.unity.render-pipelines.universal-config" })
            {
                var package = registered.SingleOrDefault(item => item.name == name);
                if (package == null || package.version != PackageVersion)
                    throw new BuildFailedException("Resolve the explicitly approved " + name + " " + PackageVersion + " before preparing URP.");
            }
        }

        private static void RequireGlobalSettings()
        {
            // URP's own postprocessor/Ensure owns creation and resource population; its type and Ensure are internal.
            var settings = GraphicsSettings.GetSettingsForRenderPipeline<UniversalRenderPipeline>();
            if (settings == null || string.IsNullOrEmpty(AssetDatabase.GetAssetPath(settings)))
                throw new BuildFailedException("URP global settings are not registered as an asset. Complete the package domain reload/import before retrying.");
            // Query this explicitly registered pipeline, including before it is
            // the active default during the first preparation.
            if (!UnityEditor.Rendering.EditorGraphicsSettings.TryGetRenderPipelineSettingsForPipeline<
                URPDefaultVolumeProfileSettings, UniversalRenderPipeline>(out var profile) || profile.volumeProfile == null)
                throw new BuildFailedException("URP's default volume profile has not been populated by its package settings initialization.");
        }
    }
}
