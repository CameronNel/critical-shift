using System;
using System.Collections;
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
    public sealed class WorkerPhysicsTests
    {
        private GameObject root;
        private LocalWorldHost host;
        private LocalWorkerStateHost state;
        private WorkerBodyRig rig;
        private CharacterController controller;
        private Rigidbody pelvis, cart;
        private double clock;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private WorkerView Worker => host.World.GetWorker(Id(1));

        [UnitySetUp] public IEnumerator SetUp()
        {
            clock = 0;
            root = new GameObject("Worker physics integration fixture"); root.transform.position = new Vector3(2500, 0, 2500);
            var bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.BindFixtureShader(shader);
            bootstrap.BindFixtureClock(() => clock);
            yield return null; yield return null;
            Assert.That(bootstrap.World, Is.Not.Null);
            root.GetComponentInChildren<SandboxHud>().enabled = false;
            host = root.GetComponentInChildren<LocalWorldHost>();
            var local = root.transform.Find("Local Gameplay Fixture/Local worker controller");
            state = local.GetComponent<LocalWorkerStateHost>();
            rig = local.GetComponentInChildren<WorkerBodyRig>(); controller = local.GetComponent<CharacterController>();
            pelvis = rig.transform.Find("Pelvis").GetComponent<Rigidbody>();
            cart = root.GetComponentInChildren<CartMotor>().GetComponent<Rigidbody>();
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        private void KnockDown() => Assert.That(state.ObserveKnockdown(Id(702), Vector3.zero, pelvis.position), Is.EqualTo(WorkerStatus.Applied));
        private WaitForFixedUpdate Step() { clock += Time.fixedDeltaTime; return new WaitForFixedUpdate(); }
        private int DynamicBodies()
        {
            int count = 0;
            foreach (var body in rig.GetComponentsInChildren<Rigidbody>()) if (!body.isKinematic) count++;
            return count;
        }

        [UnityTest] public IEnumerator KnockdownDropsTheClaimBeforeRagdollTakesMotion()
        {
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            KnockDown();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(Worker.CanInteract, Is.False);
            Assert.That(host.World.GetObject(Id(103)).HolderId, Is.Null);
            Assert.That(controller.enabled, Is.False); Assert.That(rig.IsRagdoll, Is.True);
            Assert.That(DynamicBodies(), Is.EqualTo(11));
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.Null);
            yield return Step();
            Assert.That(controller.enabled, Is.False);
        }

        [UnityTest] public IEnumerator MovingCartContactCausesOneKnockdownEpisode()
        {
            cart.position = controller.transform.position + new Vector3(0, 0.35f, -1.5f);
            cart.linearVelocity = Vector3.forward * 3; Physics.SyncTransforms();
            for (int i = 0; i < 30 && Worker.Pose == WorkerPose.Upright; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(Worker.LastHazardId, Is.EqualTo(Id(600))); Assert.That(Worker.LastCauseId, Is.Not.EqualTo(Guid.Empty));
            long episode = Worker.RecoveryEpisode;
            for (int i = 0; i < 25; i++) yield return Step();
            Assert.That(Worker.RecoveryEpisode, Is.EqualTo(episode));
            Assert.That(controller.enabled, Is.False); Assert.That(rig.IsRagdoll, Is.True);
        }

        [UnityTest] public IEnumerator StationaryCartContactDoesNotInventAKnockdown()
        {
            cart.position = controller.transform.position + new Vector3(0, 0.35f, -1.15f);
            cart.linearVelocity = Vector3.zero; Physics.SyncTransforms();
            for (int i = 0; i < 25; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.RecoveryEpisode, Is.Zero);
            Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
        }

        [UnityTest] public IEnumerator RecoveryHonorsDelayAndReturnsExactlyOneMotionController()
        {
            KnockDown(); state.RequestRecovery();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(state.LastAction, Does.Contain("TooEarly"));
            for (int i = 0; i < 250 && Worker.Pose != WorkerPose.Upright; i++)
            {
                yield return Step();
                if (i % 10 == 0 && Worker.Pose == WorkerPose.Down) state.RequestRecovery();
            }
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright), state.LastAction);
            Assert.That(controller.enabled, Is.True); Assert.That(rig.IsRagdoll, Is.False); Assert.That(DynamicBodies(), Is.Zero);
            Assert.That(controller.transform.position.y - root.transform.position.y, Is.InRange(0, 0.15f));
            Assert.That(Worker.CanInteract, Is.True);
        }

        [UnityTest] public IEnumerator LowCeilingRejectsRecoveryWithoutTeleportingTheWorkerRoot()
        {
            KnockDown();
            for (int i = 0; i < 90; i++) yield return Step();
            var ceiling = GameObject.CreatePrimitive(PrimitiveType.Cube); ceiling.name = "Recovery obstruction";
            ceiling.transform.SetParent(root.transform, false);
            ceiling.transform.position = new Vector3(pelvis.position.x, root.transform.position.y + 1.89f, pelvis.position.z);
            ceiling.transform.localScale = new Vector3(5, 0.16f, 5); Physics.SyncTransforms();
            Vector3 before = controller.transform.position; state.RequestRecovery();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(state.LastAction, Does.Contain("Blocked"));
            Assert.That(controller.transform.position, Is.EqualTo(before)); Assert.That(controller.enabled, Is.False);
        }

        [UnityTest] public IEnumerator MissingGroundCannotApproveAStandingPose()
        {
            KnockDown();
            var floor = root.transform.Find("Local Gameplay Fixture/Fixture floor").GetComponent<Collider>(); floor.enabled = false;
            Physics.SyncTransforms(); state.RequestRecovery();
            Assert.That(state.LastAction, Does.Contain("Blocked")); Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(controller.enabled, Is.False); yield return null;
        }

        [UnityTest] public IEnumerator ANewImpactInvalidatesThePendingRecoveryPlacement()
        {
            KnockDown();
            for (int i = 0; i < 200 && !state.Recovering; i++)
            {
                yield return Step();
                if (i % 10 == 0) state.RequestRecovery();
            }
            Assert.That(state.Recovering, Is.True, state.LastAction);
            long staleAttempt = Worker.RecoveryAttempt; KnockDown();
            var stale = host.World.CompleteWorkerRecovery(host.World.Epoch, Id(1), staleAttempt);
            Assert.That(stale.Status, Is.EqualTo(WorkerStatus.StaleRecovery));
            for (int i = 0; i < 30; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(rig.IsRagdoll, Is.True);
            Assert.That(controller.enabled, Is.False); Assert.That(state.Recovering, Is.False);
        }
    }
}
