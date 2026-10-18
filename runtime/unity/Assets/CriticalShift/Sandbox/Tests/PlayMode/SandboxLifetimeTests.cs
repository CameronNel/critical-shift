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
            int materialBaseline = FixtureAssets<Material>(), physicsMaterialBaseline = FixtureAssets<PhysicsMaterial>();
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
                yield return null; yield return null;
                Assert.That(FixtureAssets<Material>(), Is.EqualTo(materialBaseline), "Native fixture materials leaked across teardown.");
                Assert.That(FixtureAssets<PhysicsMaterial>(), Is.EqualTo(physicsMaterialBaseline), "Native fixture contact materials leaked across teardown.");
                if (i < 9) { bootstrap.enabled = true; yield return null; }
            }
        }

        private static int FixtureAssets<T>() where T : UnityEngine.Object
        {
            // Global native-object enumeration belongs to this leak diagnostic only, never runtime binding discovery.
            int count = 0;
            foreach (var item in Resources.FindObjectsOfTypeAll<T>())
                if (item != null && item.name.StartsWith("Fixture ", StringComparison.Ordinal)) count++;
            return count;
        }

        [UnityTest] public IEnumerator DeadlineKeepsTerminalFeedbackAndRestartsWithFreshPhysicalBindings()
        {
            root = new GameObject("Sandbox deadline lifecycle fixture"); root.transform.position = new Vector3(1500, 0, 1500);
            var bootstrap = root.AddComponent<SandboxBootstrap>(); double clock = 0;
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            bootstrap.BindFixtureShader(Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit"));
            bootstrap.BindFixtureClock(() => clock); yield return null; yield return null;
            var epoch = bootstrap.World.Epoch; var host = root.GetComponentInChildren<LocalWorldHost>();
            var safety = root.GetComponentInChildren<PhysicsSafetyMonitor>();
            clock = 720; host.Pump(); safety.Sample();
            Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(bootstrap.World.Outcome, Is.EqualTo(WorldOutcome.TimedOut));
            Assert.That(host.BoundBodyCount, Is.Zero); Assert.That(safety.BoundBodyCount, Is.Zero);
            Assert.That(bootstrap.World.ActiveClaimCount, Is.Zero); Assert.That(bootstrap.World.RegisteredObjectCount, Is.Zero);
            Assert.That(bootstrap.World.PendingTimerCount, Is.Zero); Assert.That(bootstrap.World.ConnectedPlayerCount, Is.Zero);
            var totals = host.Commands.ProductionSummary; var power = host.Commands.Power;
            Assert.That(totals.IssuedUnits, Is.EqualTo(120)); Assert.That(totals.ActiveUnits + totals.WasteUnits, Is.EqualTo(120));
            Assert.That(totals.PendingCycles, Is.Zero); Assert.That(power, Is.Not.Null);
            Assert.That(power.Initial + power.Generated, Is.EqualTo(power.Available + power.Spent + power.Delivered + power.Spilled));
            yield return null; yield return null;
            Assert.That(root.GetComponentInChildren<SandboxHud>().isActiveAndEnabled, Is.True);
            foreach (var rig in root.GetComponentsInChildren<WorkerBodyRig>())
                foreach (var body in rig.CopyBodySegments()) Assert.That(body.isKinematic, Is.True);
            bootstrap.enabled = false;
            Assert.That(bootstrap.LastStoppedWorld.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(bootstrap.LastStoppedPhysicalBindings, Is.Zero); Assert.That(bootstrap.LastStoppedPhysicsObservations, Is.Zero);
            yield return null; bootstrap.enabled = true; yield return null; yield return null;
            Assert.That(bootstrap.World.Epoch, Is.Not.EqualTo(epoch)); Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Running));
            Assert.That(bootstrap.PhysicalBindingCount, Is.EqualTo(10));
            Assert.That(root.GetComponentInChildren<PhysicsSafetyMonitor>().BoundBodyCount, Is.EqualTo(31));
            Assert.That(bootstrap.World.RemainingMilliseconds, Is.EqualTo(720000));
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
            var cargo = root.transform.Find("Local Gameplay Fixture/Material container 5").GetComponent<Rigidbody>();
            cargo.position = motor.transform.position + Vector3.up * 0.42f; cargo.linearVelocity = Vector3.zero;
            Physics.SyncTransforms();
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
            Assert.That(host.World.GetObject(id).HolderId, Is.Not.Null);
            crate.position = root.transform.position + Vector3.down * 30; Physics.SyncTransforms();
            safety.Sample();
            Assert.That(failure, Is.TypeOf<InvalidOperationException>());
            Assert.That(failure.Message, Does.Contain("Physics body escaped fixture bounds: Material container 4"));
            Assert.That(safety.FaultLatched, Is.True); Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(bootstrap.World.ActiveClaimCount, Is.Zero); Assert.That(host.BoundBodyCount, Is.Zero);
            yield return null;
        }
    }
}
