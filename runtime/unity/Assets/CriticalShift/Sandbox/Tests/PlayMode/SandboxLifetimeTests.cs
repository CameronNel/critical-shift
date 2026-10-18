using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Presentation;
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
                Assert.That(bootstrap.PhysicalBindingCount, Is.EqualTo(10));
                var workerRigs = root.GetComponentsInChildren<WorkerBodyRig>();
                Assert.That(workerRigs.Length, Is.EqualTo(2));
                foreach (var workerRig in workerRigs) Assert.That(workerRig.BodyCount, Is.EqualTo(11));
                bootstrap.enabled = false;
                foreach (var workerRig in workerRigs)
                    foreach (var body in workerRig.GetComponentsInChildren<Rigidbody>(true)) Assert.That(body.isKinematic, Is.True);
                Assert.That(bootstrap.World, Is.Null);
                Assert.That(bootstrap.PhysicalBindingCount, Is.Zero);
                Assert.That(bootstrap.LastStoppedPhysicalBindings, Is.Zero);
                Assert.That(bootstrap.LastStoppedPhysicsObservations, Is.Zero);
                Assert.That(bootstrap.LastStoppedWorld.Phase, Is.EqualTo(WorldPhase.Stopped));
                Assert.That(bootstrap.LastStoppedWorld.ActiveClaimCount, Is.Zero);
                Assert.That(bootstrap.LastStoppedWorld.RegisteredObjectCount, Is.Zero);
                yield return null;
                bootstrap.enabled = true; yield return null;
            }
        }

        [UnityTest] public IEnumerator GroundedFixtureCartDrivesWhileItsWorkerMaintainsTheHandle()
        {
            root = new GameObject("Grounded cart integration fixture"); root.transform.position = new Vector3(1500, 0, 1500);
            var bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            bootstrap.BindFixtureShader(Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit"));
            yield return null; yield return null;
            Assert.That(bootstrap.World, Is.Not.Null);
            root.GetComponentInChildren<SandboxHud>().enabled = false; // Supply drive samples directly for this test.
            var host = root.GetComponentInChildren<LocalWorldHost>();
            var motor = root.GetComponentInChildren<CartMotor>();
            var controller = root.transform.Find("Local Gameplay Fixture/Local worker controller").GetComponent<CharacterController>();
            var stand = motor.transform.Find("Cart operator stance");
            Assert.That(stand, Is.Not.Null);
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            controller.enabled = false; controller.transform.position = stand.position + Vector3.up * 0.1f; controller.enabled = true;
            var cartId = new Guid(600, 0, 0, new byte[8]);
            host.Grab(cartId); Assert.That(host.IsHandleHeld(cartId), Is.True);
            Vector3 initial = motor.transform.position; motor.SetDrive(1, 0, false);
            for (int i = 0; i < 100; i++) yield return new WaitForFixedUpdate();
            Assert.That(host.IsHandleHeld(cartId), Is.True, "The colliding worker must keep up with its cart stance.");
            Assert.That(motor.Speed, Is.GreaterThan(0.75f), "Ground friction must permit bounded cart drive.");
            Assert.That(motor.transform.position.z - initial.z, Is.GreaterThan(1));
            Assert.That(motor.transform.position.y - root.transform.position.y, Is.InRange(0.3f, 0.7f));
            Assert.That(Vector3.Distance(controller.transform.position, stand.position), Is.LessThan(1));
            host.DropHeld(); Assert.That(host.IsHandleHeld(cartId), Is.False);
        }

        [UnityTest] public IEnumerator EscapedFixtureCargoStopsTheWorldAndClearsItsCurrentClaim()
        {
            root = new GameObject("Physics observation containment fixture"); root.transform.position = new Vector3(1500, 0, 1500);
            var bootstrap = root.AddComponent<SandboxBootstrap>();
            Exception failure = null; bootstrap.BindFixtureDiagnostics(error => failure = error);
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            bootstrap.BindFixtureShader(Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit"));
            yield return null; yield return null;
            Assert.That(bootstrap.World, Is.Not.Null); root.GetComponentInChildren<SandboxHud>().enabled = false;
            var host = root.GetComponentInChildren<LocalWorldHost>(); var safety = root.GetComponentInChildren<PhysicsSafetyMonitor>();
            Assert.That(safety.BoundBodyCount, Is.EqualTo(31));
            var crate = root.transform.Find("Local Gameplay Fixture/Material container 4").GetComponent<Rigidbody>();
            var id = new Guid(103, 0, 0, new byte[8]); host.Grab(id);
            Assert.That(bootstrap.World.GetObject(id).HolderId, Is.Not.Null);
            crate.position = root.transform.position + Vector3.down * 30; Physics.SyncTransforms();
            safety.Sample();
            Assert.That(failure, Is.TypeOf<InvalidOperationException>());
            Assert.That(failure.Message, Does.Contain("Physics body escaped fixture bounds: Material container 4"));
            Assert.That(safety.FaultLatched, Is.True); Assert.That(bootstrap.World.View.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(bootstrap.World.View.ActiveClaimCount, Is.Zero); Assert.That(host.BoundBodyCount, Is.Zero);
            yield return null;
        }
    }
}
