using CriticalShift.Bootstrap.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine.Rendering;

namespace CriticalShift.Tests.EditMode
{
    public sealed class FoundationProjectTests
    {
        [Test] public void PreparedSceneAndPackageAreValid() => FoundationBuild.Validate();

        [Test] public void BuildContainsOnlyTheFoundationScene()
        {
            Assert.That(EditorBuildSettings.scenes, Has.Length.EqualTo(1));
            Assert.That(EditorBuildSettings.scenes[0].enabled, Is.True);
            Assert.That(EditorBuildSettings.scenes[0].path, Is.EqualTo(FoundationBuild.ScenePath));
        }

        [Test] public void OwnerSelectedUniversalPipelineIsConfigured()
        {
            Assert.That(GraphicsSettings.defaultRenderPipeline, Is.Not.Null);
            Assert.That(GraphicsSettings.defaultRenderPipeline.GetType().FullName,
                Is.EqualTo("UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset"));
            Assert.That(PlayerSettings.colorSpace, Is.EqualTo(UnityEngine.ColorSpace.Linear));
            for (int i = 0; i < UnityEngine.QualitySettings.names.Length; i++)
                Assert.That(UnityEngine.QualitySettings.GetRenderPipelineAssetAt(i), Is.Null);
        }

        [Test] public void DomainReloadRemainsEnabled() =>
            Assert.That(EditorSettings.enterPlayModeOptionsEnabled, Is.False);
    }
}
