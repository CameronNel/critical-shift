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

        [Test] public void BuiltInPipelineIsPreserved() =>
            Assert.That(GraphicsSettings.defaultRenderPipeline, Is.Null);

        [Test] public void DomainReloadRemainsEnabled() =>
            Assert.That(EditorSettings.enterPlayModeOptionsEnabled, Is.False);
    }
}
