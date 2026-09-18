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

namespace CriticalShift.Bootstrap.Editor
{
    public static class FoundationBuild
    {
        public const string ScenePath = "Assets/CriticalShift/Bootstrap/Foundation.unity";

        [Serializable]
        private sealed class Profile
        {
            public string editor = "";
            public string testFramework = "";
            public string apiCompatibility = "";
            public string backend = "";
            public string stripping = "";
            public string productName = "";
            public string companyName = "";
        }

        private static Profile ReadProfile()
        {
            var path = Path.GetFullPath(Path.Combine(UnityApplication.dataPath, "../../toolchain.json"));
            var profile = JsonUtility.FromJson<Profile>(File.ReadAllText(path));
            if (profile == null || profile.editor != UnityApplication.unityVersion)
                throw new BuildFailedException("WP-01 requires the exact editor in runtime/toolchain.json.");
            return profile;
        }

        [MenuItem("Critical Shift/Foundation/Prepare project")]
        public static void Prepare()
        {
            if (!UnityApplication.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;
            var profile = ReadProfile();
            PlayerSettings.companyName = profile.companyName;
            PlayerSettings.productName = profile.productName;
            PlayerSettings.bundleVersion = "0.0.1";
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Standalone,
                (ApiCompatibilityLevel)Enum.Parse(typeof(ApiCompatibilityLevel), profile.apiCompatibility));
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone,
                (ScriptingImplementation)Enum.Parse(typeof(ScriptingImplementation), profile.backend));
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone,
                (ManagedStrippingLevel)Enum.Parse(typeof(ManagedStrippingLevel), profile.stripping));
            PlayerSettings.runInBackground = true;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.defaultScreenWidth = 960;
            PlayerSettings.defaultScreenHeight = 540;
            EditorSettings.serializationMode = SerializationMode.ForceText;
            EditorSettings.enterPlayModeOptionsEnabled = false;
            if (GraphicsSettings.defaultRenderPipeline != null)
                throw new BuildFailedException("An SRP asset is configured; WP-01 requires Built-in rendering.");
            if (!File.Exists(Path.Combine(UnityApplication.dataPath, "CriticalShift/Bootstrap/Foundation.unity")))
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var root = new GameObject("Critical Shift Foundation");
                var cameraComponent = root.AddComponent<Camera>();
                cameraComponent.clearFlags = CameraClearFlags.SolidColor;
                cameraComponent.backgroundColor = new Color(0.09f, 0.11f, 0.14f);
                root.AddComponent<FoundationBootstrap>();
                if (!EditorSceneManager.SaveScene(scene, ScenePath))
                    throw new BuildFailedException("Could not save the foundation scene.");
            }
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Validate();
            Debug.Log("CS_FOUNDATION_PREPARED");
        }

        public static void Validate()
        {
            var profile = ReadProfile();
            if (PlayerSettings.GetApiCompatibilityLevel(NamedBuildTarget.Standalone) !=
                    (ApiCompatibilityLevel)Enum.Parse(typeof(ApiCompatibilityLevel), profile.apiCompatibility) ||
                PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone) !=
                    (ScriptingImplementation)Enum.Parse(typeof(ScriptingImplementation), profile.backend) ||
                PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.Standalone) !=
                    (ManagedStrippingLevel)Enum.Parse(typeof(ManagedStrippingLevel), profile.stripping))
                throw new BuildFailedException("Standalone API/backend/stripping differs from the declared profile.");
            if (EditorSettings.enterPlayModeOptionsEnabled || EditorSettings.serializationMode != SerializationMode.ForceText)
                throw new BuildFailedException("Reload/serialization defaults differ from the declared profile.");
            if (EditorBuildSettings.scenes.Length != 1 || !EditorBuildSettings.scenes[0].enabled ||
                EditorBuildSettings.scenes[0].path != ScenePath)
                throw new BuildFailedException("The build scene catalogue differs from the foundation fixture.");
            var package = UnityEditor.PackageManager.PackageInfo.GetAllRegisteredPackages()
                .SingleOrDefault(p => p.name == "com.unity.test-framework");
            if (package == null || package.version != profile.testFramework)
                throw new BuildFailedException("Unexpected resolved Unity Test Framework version.");
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var roots = scene.GetRootGameObjects();
            var bootstrap = roots.SelectMany(r => r.GetComponentsInChildren<FoundationBootstrap>(true)).ToArray();
            if (bootstrap.Length != 1 || !bootstrap[0].isActiveAndEnabled ||
                !bootstrap[0].GetComponent<Camera>().enabled)
                throw new BuildFailedException("Foundation scene must have one active bootstrap and Camera.");
            if (GraphicsSettings.defaultRenderPipeline != null)
                throw new BuildFailedException("Unexpected render pipeline asset.");
            Debug.Log("CS_FOUNDATION_VALIDATED");
        }

        public static void Build()
        {
            Validate();
            var args = Environment.GetCommandLineArgs();
            int index = Array.IndexOf(args, "-csBuildPath");
            if (index < 0 || index + 1 >= args.Length)
                throw new BuildFailedException("-csBuildPath must name the output executable.");
            string path = Path.GetFullPath(args[index + 1]);
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneLinux64 && target != BuildTarget.StandaloneWindows64)
                throw new BuildFailedException("WP-01 supports Linux64/Windows64 desktop fixture builds only.");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath }, locationPathName = path, target = target,
                options = BuildOptions.Development | BuildOptions.StrictMode
            });
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new BuildFailedException("Foundation Player build did not succeed.");
            Debug.Log($"CS_FOUNDATION_BUILD_OK guid={report.summary.guid} target={target} bytes={report.summary.totalSize}");
        }
    }
}
