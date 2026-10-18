using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.Application;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class SandboxLifetimeTests
    {
        private GameObject root;
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator TenEnableDisableCyclesUseFreshEpochsAndClearAllBindings()
        {
            root = new GameObject("Sandbox lifetime regression fixture"); root.transform.position = new Vector3(1500, 0, 1500);
            var bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.BindFixtureShader(shader);
            yield return null; yield return null;
            var epochs = new HashSet<Guid>();
            for (int i = 0; i < 10; i++)
            {
                Assert.That(bootstrap.World, Is.Not.Null); Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Running));
                Assert.That(epochs.Add(bootstrap.World.Epoch), Is.True);
                Assert.That(bootstrap.PhysicalBindingCount, Is.EqualTo(8));
                bootstrap.enabled = false;
                Assert.That(bootstrap.World, Is.Null);
                Assert.That(bootstrap.PhysicalBindingCount, Is.Zero);
                Assert.That(bootstrap.LastStoppedWorld.Phase, Is.EqualTo(WorldPhase.Stopped));
                Assert.That(bootstrap.LastStoppedWorld.ActiveClaimCount, Is.Zero);
                Assert.That(bootstrap.LastStoppedWorld.RegisteredObjectCount, Is.Zero);
                yield return null;
                bootstrap.enabled = true; yield return null;
            }
        }
    }
}
