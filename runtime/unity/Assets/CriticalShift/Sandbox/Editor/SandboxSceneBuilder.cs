using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityApplication = UnityEngine.Application;

namespace CriticalShift.Sandbox.Editor
{
    /// <summary>Explicit scratch-scene generation. Never imports or rewrites a map or authored room.</summary>
    public static class SandboxSceneBuilder
    {
        public const string ScenePath = "Assets/CriticalShift/Sandbox/Generated/GameplaySandbox.unity";
        [Serializable] private sealed class Profile
        {
            public string editor = "";
            public string apiCompatibility = "";
            public string backend = "";
            public string stripping = "";
        }

        private static Profile ReadProfile()
        {
            string path = Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "../../toolchain.json"));
            var profile = JsonUtility.FromJson<Profile>(File.ReadAllText(path));
            if (profile == null || profile.editor != UnityApplication.unityVersion)
                throw new BuildFailedException("Use the exact Unity version in runtime/toolchain.json for this fixture.");
            return profile;
        }

        [MenuItem("Critical Shift/Sandbox/Create isolated gameplay scene")]
        public static void Prepare()
        {
            var profile = ReadProfile();
            SandboxAssemblyGraph.Validate();
            if (!UnityApplication.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            SandboxRenderPipeline.Prepare();
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Standalone,
                (ApiCompatibilityLevel)Enum.Parse(typeof(ApiCompatibilityLevel), profile.apiCompatibility));
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone,
                (ScriptingImplementation)Enum.Parse(typeof(ScriptingImplementation), profile.backend));
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone,
                (ManagedStrippingLevel)Enum.Parse(typeof(ManagedStrippingLevel), profile.stripping));
            EditorSettings.serializationMode = SerializationMode.ForceText;
            EditorSettings.enterPlayModeOptionsEnabled = false;
            const string parent = "Assets/CriticalShift/Sandbox";
            if (!AssetDatabase.IsValidFolder(parent + "/Generated")) AssetDatabase.CreateFolder(parent, "Generated");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var bootstrap = new GameObject("Critical Shift Gameplay Sandbox").AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            if (shader == null) throw new BuildFailedException("The configured renderer's Lit shader is missing.");
            // Serialized shader reference is a Player dependency root, avoiding a string-only Shader.Find dependency.
            bootstrap.BindFixtureShader(shader);
            SandboxMaterialTemplates.Prepare(shader, out var litTemplate, out var emissionTemplate);
            bootstrap.BindFixtureMaterials(litTemplate, emissionTemplate);
            var capture = bootstrap.gameObject.AddComponent<SandboxPlayerCapture>();
            capture.Configure(bootstrap); bootstrap.BindPlayerCapture(capture);
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new BuildFailedException("The sandbox scene could not be saved.");
            AssetDatabase.SaveAssets();
            // The explicit URP trial configures rendering above; authored scene catalogues stay owned by their importers.
            Debug.Log("CS_SANDBOX_PREPARED scene=" + ScenePath + " unity=" + UnityApplication.unityVersion);
        }

        public static void Build()
        {
            var profile = ReadProfile();
            SandboxRenderPipeline.Validate();
            if (PlayerSettings.GetApiCompatibilityLevel(NamedBuildTarget.Standalone) !=
                    (ApiCompatibilityLevel)Enum.Parse(typeof(ApiCompatibilityLevel), profile.apiCompatibility) ||
                PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone) !=
                    (ScriptingImplementation)Enum.Parse(typeof(ScriptingImplementation), profile.backend) ||
                PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.Standalone) !=
                    (ManagedStrippingLevel)Enum.Parse(typeof(ManagedStrippingLevel), profile.stripping))
                throw new BuildFailedException("The sandbox API/backend/stripping must match runtime/toolchain.json.");
            if (!File.Exists(ScenePath)) throw new BuildFailedException("Prepare the isolated sandbox scene first.");
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            if (pipeline == null || pipeline.GetType().FullName != "UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset")
                throw new BuildFailedException("The owner-selected URP pipeline must be configured before sandbox Player acceptance.");
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var bootstraps = scene.GetRootGameObjects().SelectMany(item => item.GetComponentsInChildren<SandboxBootstrap>(true)).ToArray();
            if (bootstraps.Length != 1 || bootstraps[0].FixtureShader == null ||
                bootstraps[0].FixtureShader.name != "Universal Render Pipeline/Lit")
                throw new BuildFailedException("Regenerate the isolated scene under URP so its shader reference is retained in the Player.");
            SandboxMaterialTemplates.Validate(bootstraps[0].FixtureShader, bootstraps[0].FixtureLitTemplate,
                bootstraps[0].FixtureEmissionTemplate);
            var captures = scene.GetRootGameObjects().SelectMany(item => item.GetComponentsInChildren<SandboxPlayerCapture>(true)).ToArray();
            if (captures.Length != 1 || captures[0].Owner != bootstraps[0] || bootstraps[0].PlayerCapture != captures[0] ||
                !captures[0].isActiveAndEnabled)
                throw new BuildFailedException("Regenerate the sandbox scene with its one explicitly bound Player capture component.");
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-csSandboxBuildPath");
            if (index < 0 || index + 1 >= args.Length) throw new BuildFailedException("Pass -csSandboxBuildPath with the output executable.");
            var target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneWindows64 && target != BuildTarget.StandaloneLinux64)
                throw new BuildFailedException("The sandbox currently supports Win64 or Linux64 desktop builds.");
            string path = Path.GetFullPath(args[index + 1]); Directory.CreateDirectory(Path.GetDirectoryName(path));
            bool previousStrictMatching = PlayerSettings.strictShaderVariantMatching;
            try
            {
                // The rendered diagnostic Player must expose missing Lit/emissive variants instead of silently substituting one.
                PlayerSettings.strictShaderVariantMatching = true;
                if (!PlayerSettings.strictShaderVariantMatching)
                    throw new BuildFailedException("The sandbox Development Player requires strict shader variant matching.");
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { ScenePath }, locationPathName = path, target = target,
                    options = BuildOptions.Development | BuildOptions.StrictMode
                });
                if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                    throw new BuildFailedException("Sandbox Player build failed; preserve the native build log.");
                if (!PlayerSettings.strictShaderVariantMatching)
                    throw new BuildFailedException("Strict shader variant matching changed during the sandbox build.");
                Debug.Log("CS_SANDBOX_BUILD_STRICT_VARIANTS guid=" + report.summary.guid + " enabled=1 target=" + target);
                Debug.Log("CS_SANDBOX_BUILD_OK guid=" + report.summary.guid + " target=" + target);
            }
            finally { PlayerSettings.strictShaderVariantMatching = previousStrictMatching; }
        }
    }
}
