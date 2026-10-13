using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CriticalShift.Bootstrap.Player.Editor
{
    public static class PlayerRoomBuild
    {
        public const string ScenePath = "Assets/CriticalShift/Generated/PlayerRoom.unity";
        [MenuItem("Critical Shift/Player Room/Create test scene")]
        public static void Prepare()
        {
            if (UnityEngine.Application.unityVersion != "6000.4.3f1") throw new BuildFailedException("Use the repository's pinned Unity editor.");
            if (!UnityEngine.Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            PlayerRoomFactory.Create();
            if (!AssetDatabase.IsValidFolder("Assets/CriticalShift/Generated")) AssetDatabase.CreateFolder("Assets/CriticalShift", "Generated");
            if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new BuildFailedException("Cannot save player fixture.");
            // Keep the foundation scene catalogue intact. Builds below select this scene explicitly.
            AssetDatabase.SaveAssets(); Debug.Log("CS_PLAYER_ROOM_PREPARED");
        }
        public static void Build()
        {
            Prepare();
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-csBuildPath");
            if (index < 0 || index + 1 >= args.Length) throw new BuildFailedException("-csBuildPath must name the executable.");
            var path = Path.GetFullPath(args[index + 1]); Directory.CreateDirectory(Path.GetDirectoryName(path));
            var target = EditorUserBuildSettings.activeBuildTarget;
            if (target != BuildTarget.StandaloneLinux64 && target != BuildTarget.StandaloneWindows64)
                throw new BuildFailedException("Only Linux64/Windows64 are in this fixture scope.");
            var named = NamedBuildTarget.Standalone;
            PlayerSettings.SetApiCompatibilityLevel(named, ApiCompatibilityLevel.NET_Standard);
            PlayerSettings.SetScriptingBackend(named, ScriptingImplementation.Mono2x);
            PlayerSettings.SetManagedStrippingLevel(named, ManagedStrippingLevel.Disabled);
            if (UnityEngine.Rendering.GraphicsSettings.defaultRenderPipeline != null)
                throw new BuildFailedException("This fixture requires Built-in rendering.");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { ScenePath },
                target = target, locationPathName = path, options = BuildOptions.Development | BuildOptions.StrictMode });
            if (report.summary.result != BuildResult.Succeeded || report.summary.totalErrors != 0)
                throw new BuildFailedException("Player room build failed.");
            Debug.Log("CS_PLAYER_ROOM_BUILD_OK");
        }
    }
}
