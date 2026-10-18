using System;
using System.Collections;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Presentation;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class WorkerDragTests
    {
        private GameObject root;
        private SandboxBootstrap bootstrap;
        private LocalWorldHost host;
        private CharacterController player, patientController;
        private LocalWorkerMotor walker;
        private WorkerBodyRig patientRig;
        private LocalWorkerStateHost patientState;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private ObjectClaimView Claim => host.World.GetWorkerBodyClaim(Id(3));

        [UnitySetUp] public IEnumerator SetUp()
        {
            root = new GameObject("Worker dragging integration fixture"); root.transform.position = new Vector3(4000, 0, 4000);
            bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.BindFixtureShader(shader);
            yield return null; yield return null;
            Assert.That(bootstrap.World, Is.Not.Null); BindFixture();
            for (int i = 0; i < 80; i++) yield return new WaitForFixedUpdate();
        }

        private void BindFixture()
        {
            var fixture = root.transform.Find("Local Gameplay Fixture");
            fixture.GetComponent<SandboxHud>().enabled = false;
            host = fixture.GetComponent<LocalWorldHost>();
            var local = fixture.Find("Local worker controller");
            player = local.GetComponent<CharacterController>(); walker = local.GetComponent<LocalWorkerMotor>();
            var patient = fixture.Find("Fixture patient worker"); patientController = patient.GetComponent<CharacterController>();
            patientState = patient.GetComponent<LocalWorkerStateHost>(); patientRig = patient.GetComponentInChildren<WorkerBodyRig>();
        }

        private void StandNearGrip()
        {
            Vector3 point = patientRig.SuitGrip.position - Vector3.forward * 1.7f;
            point.y = root.transform.position.y + 0.1f;
            player.enabled = false; player.transform.SetPositionAndRotation(point, Quaternion.identity); player.enabled = true;
            walker.ResetAfterRecovery(); Physics.SyncTransforms();
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator SuitGripPullsTheDynamicWorkerAndSlowsTheRescuer()
        {
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            Assert.That(host.CarriedPhysicalMass(), Is.EqualTo(68).Within(0.01f));
            Vector3 before = patientRig.SuitGrip.position; walker.SetMovement(Vector2.down);
            for (int i = 0; i < 100; i++) yield return new WaitForFixedUpdate();
            walker.SetMovement(Vector2.zero);
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1)), host.LastAction);
            Assert.That(patientRig.SuitGrip.position.z, Is.LessThan(before.z - 0.3f));
            Assert.That(walker.CarrySpeedScale, Is.EqualTo(0.35f).Within(0.001f));
            Assert.That(patientRig.IsRagdoll, Is.True); Assert.That(patientController.enabled, Is.False); Assert.That(player.enabled, Is.True);
        }

        [UnityTest] public IEnumerator LostDragReachDropsOnlyItsCurrentLease()
        {
            StandNearGrip(); host.Grab(Id(650)); long oldGeneration = Claim.LeaseGeneration;
            Vector3 before = patientRig.SuitGrip.position;
            player.enabled = false; player.transform.position += Vector3.back * 8; player.enabled = true;
            for (int i = 0; i < 3; i++) yield return new WaitForFixedUpdate();
            Assert.That(Claim.HolderId, Is.Null); Assert.That(Vector3.Distance(before, patientRig.SuitGrip.position), Is.LessThan(1));
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            Assert.That(Claim.LeaseGeneration, Is.GreaterThan(oldGeneration));
            Assert.That(host.World.ReportAttachmentFailure(host.World.Epoch, Id(650), oldGeneration).Status, Is.EqualTo(InteractionStatus.StaleLease));
            yield return new WaitForFixedUpdate(); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
        }

        [UnityTest] public IEnumerator HeldWorkerCannotStandUntilTheSuitGripIsReleased()
        {
            StandNearGrip(); host.Grab(Id(650)); patientState.RequestRecovery();
            Assert.That(patientState.LastAction, Does.Contain("Release")); Assert.That(patientRig.IsRagdoll, Is.True);
            Assert.That(patientController.enabled, Is.False); host.DropHeld(); Assert.That(patientRig.IsRagdoll, Is.True);
            for (int i = 0; i < 300 && host.World.GetWorker(Id(3)).Pose != WorkerPose.Upright; i++)
            {
                yield return new WaitForFixedUpdate();
                if (i % 10 == 0) patientState.RequestRecovery();
            }
            Assert.That(host.World.GetWorker(Id(3)).Pose, Is.EqualTo(WorkerPose.Upright), patientState.LastAction);
            Assert.That(patientRig.IsRagdoll, Is.False); Assert.That(patientController.enabled, Is.True); Assert.That(Claim.HolderId, Is.Null);
            host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.Null);
        }

        [UnityTest] public IEnumerator InteractionFollowsTheMovedSuitGripInsteadOfTheOldWorkerRoot()
        {
            foreach (var body in patientRig.CopyBodySegments())
            { body.position += Vector3.forward * 6; body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; }
            StandNearGrip(); host.Grab(Id(650));
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1)), "Reach must use the moving suit grip, with the original collider hierarchy identity.");
            host.DropHeld(); yield return null;
        }

        [UnityTest] public IEnumerator FixtureTeardownClearsTheDragBeforeCreatingAFreshEpoch()
        {
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            var oldWorld = host.World; var oldEpoch = oldWorld.Epoch; var oldRig = patientRig;
            bootstrap.enabled = false;
            Assert.That(oldWorld.View.ActiveClaimCount, Is.Zero); Assert.That(oldWorld.GetWorkerBodyClaim(Id(3)), Is.Null);
            foreach (var body in oldRig.CopyBodySegments()) Assert.That(body.isKinematic, Is.True);
            yield return null; bootstrap.enabled = true; yield return null; yield return null;
            BindFixture(); Assert.That(host.World.Epoch, Is.Not.EqualTo(oldEpoch)); Assert.That(Claim.HolderId, Is.Null);
            Assert.That(host.World.View.ActiveClaimCount, Is.Zero); Assert.That(host.BoundBodyCount, Is.EqualTo(10));
        }
    }
}
