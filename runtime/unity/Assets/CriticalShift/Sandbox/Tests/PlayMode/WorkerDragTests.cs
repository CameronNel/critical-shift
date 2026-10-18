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
    public sealed class WorkerDragTests
    {
        private GameObject root;
        private SandboxBootstrap bootstrap;
        private LocalWorldHost host;
        private CharacterController player, patientController;
        private LocalWorkerMotor walker;
        private WorkerBodyRig patientRig;
        private LocalWorkerStateHost patientState;
        private double clock;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private ObjectClaimView Claim => host.World.GetWorkerBodyClaim(Id(3));

        [UnitySetUp] public IEnumerator SetUp()
        {
            clock = 0;
            root = new GameObject("Worker dragging integration fixture"); root.transform.position = new Vector3(4000, 0, 4000);
            bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.BindFixtureShader(shader);
            bootstrap.BindFixtureClock(() => clock);
            yield return null; yield return null;
            Assert.That(bootstrap.World, Is.Not.Null); BindFixture();
            for (int i = 0; i < 80; i++) yield return Step();
        }

        private WaitForFixedUpdate Step() { clock += Time.fixedDeltaTime; return new WaitForFixedUpdate(); }
        private float BodyCenterHeight()
        {
            float weighted = 0;
            foreach (var body in patientRig.CopyBodySegments()) weighted += body.worldCenterOfMass.y * body.mass;
            return weighted / patientRig.TotalPhysicalMass;
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
            var carry = player.transform.Find("Worker eyes/Current-claim carry target"); Quaternion rest = carry.localRotation;
            Vector3 position = carry.localPosition; host.RotateHeld(new Vector2(120, 100)); host.AdjustHeldDistance(-100);
            host.ThrowHeld(); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            Assert.That(Quaternion.Angle(rest, carry.localRotation), Is.LessThan(0.01f));
            Assert.That(carry.localPosition, Is.EqualTo(position));
            Vector3 before = patientRig.SuitGrip.position; walker.SetMovement(Vector2.down);
            for (int i = 0; i < 100; i++) yield return Step();
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
            for (int i = 0; i < 3; i++) yield return Step();
            Assert.That(Claim.HolderId, Is.Null); Assert.That(Vector3.Distance(before, patientRig.SuitGrip.position), Is.LessThan(1));
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            Assert.That(Claim.LeaseGeneration, Is.GreaterThan(oldGeneration));
            Assert.That(host.World.ReportAttachmentFailure(host.World.Epoch, Id(650), oldGeneration).Status, Is.EqualTo(InteractionStatus.StaleLease));
            yield return Step(); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
        }

        [UnityTest] public IEnumerator HeldWorkerCannotStandUntilTheSuitGripIsReleased()
        {
            StandNearGrip(); host.Grab(Id(650)); patientState.RequestRecovery();
            Assert.That(patientState.LastAction, Does.Contain("Release")); Assert.That(patientRig.IsRagdoll, Is.True);
            Assert.That(patientController.enabled, Is.False); host.DropHeld(); Assert.That(patientRig.IsRagdoll, Is.True);
            for (int i = 0; i < 300 && host.World.GetWorker(Id(3)).Pose != WorkerPose.Upright; i++)
            {
                yield return Step();
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

        [UnityTest] public IEnumerator FreeWorkerSegmentsShareOneCargoGroupAndHeldSegmentsHaveNone()
        {
            var parts = patientRig.CopyBodySegments();
            var group = host.PhysicalCargoGroup(parts[0]); Assert.That(group, Is.Not.Null);
            Assert.That(host.PhysicalCargoGroup(parts[1]), Is.SameAs(group)); Assert.That(host.PhysicalCargoMass(group), Is.EqualTo(68));
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.HolderId, Is.EqualTo(Id(1)));
            Assert.That(host.PhysicalCargoGroup(parts[0]), Is.Null); Assert.That(host.PhysicalCargoGroup(parts[1]), Is.Null);
            patientState.SetDownMovement(Vector2.right); yield return Step();
            Assert.That(patientState.CrawlDriveActive, Is.False); patientState.SetDownMovement(Vector2.zero);
            host.DropHeld(); Assert.That(host.PhysicalCargoGroup(parts[1]), Is.SameAs(group));
            yield return null;
        }

        [UnityTest] public IEnumerator HoistingRaisesTheWorkerUnderTheSameLeaseAndPreservesDownState()
        {
            StandNearGrip(); host.Grab(Id(650)); long generation = Claim.LeaseGeneration;
            float before = patientRig.SuitGrip.position.y, center = BodyCenterHeight(); host.SetWorkerHoist(true);
            for (int i = 0; i < 200; i++) yield return Step();
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1)), host.LastAction); Assert.That(Claim.LeaseGeneration, Is.EqualTo(generation));
            Assert.That(patientRig.SuitGrip.position.y, Is.GreaterThan(before + 0.65f));
            Assert.That(BodyCenterHeight(), Is.GreaterThan(center + 0.35f));
            Assert.That(host.CurrentWorkerDragTarget().Value.y - player.transform.position.y, Is.EqualTo(2.05f).Within(0.001f));
            Assert.That(host.World.GetWorker(Id(3)).Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(patientController.enabled, Is.False);
            Assert.That(host.CarriedPhysicalMass(), Is.EqualTo(68));
            host.World.Pause(host.World.Epoch); host.SetWorkerHoist(true);
            for (int i = 0; i < 40; i++) yield return Step();
            Assert.That(host.CurrentWorkerDragTarget().Value.y - player.transform.position.y, Is.EqualTo(0.55f).Within(0.001f));
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1))); Assert.That(Claim.LeaseGeneration, Is.EqualTo(generation));
            Assert.That(host.World.GetWorker(Id(3)).Pose, Is.EqualTo(WorkerPose.Down));
        }

        [UnityTest] public IEnumerator ReleasedOrStaleHoistInputCannotRaiseTheNextLeaseTarget()
        {
            StandNearGrip(); host.Grab(Id(650)); var previous = Claim; host.SetWorkerHoist(true);
            for (int i = 0; i < 80; i++) yield return Step();
            Assert.That(host.CurrentWorkerDragTarget().Value.y - player.transform.position.y, Is.GreaterThan(1.8f));
            host.DropHeld(); Assert.That(host.CurrentWorkerDragTarget().HasValue, Is.False);
            for (int i = 0; i < 200; i++) yield return Step();
            StandNearGrip(); host.Grab(Id(650)); Assert.That(Claim.LeaseGeneration, Is.GreaterThan(previous.LeaseGeneration));
            patientRig.SetBodyHoist(previous, true); // A retained observation cannot authorize forces for this new lease.
            for (int i = 0; i < 30; i++) yield return Step();
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1))); Assert.That(host.CurrentWorkerDragTarget().Value.y - player.transform.position.y,
                Is.EqualTo(0.55f).Within(0.001f));
            float center = BodyCenterHeight(); host.SetWorkerHoist(true);
            for (int i = 0; i < 200; i++)
            { patientRig.SetBodyHoist(previous, false); yield return Step(); }
            Assert.That(BodyCenterHeight(), Is.GreaterThan(center + 0.35f), "Old input must not cancel the new lease's hoist.");
        }

        [UnityTest] public IEnumerator AHoistedWorkerReleasedOverTheCartBecomesOneObservedLoad()
        {
            StandNearGrip(); host.Grab(Id(650)); host.SetWorkerHoist(true);
            for (int i = 0; i < 200; i++) yield return Step();
            Assert.That(Claim.HolderId, Is.EqualTo(Id(1)), host.LastAction);
            var cart = root.GetComponentInChildren<CartMotor>().GetComponent<Rigidbody>();
            Vector3 grip = patientRig.SuitGrip.position;
            // Choose this test's cart starting pose beneath the already physically hoisted worker.
            cart.position = new Vector3(grip.x, root.transform.position.y + 0.45f, grip.z + 0.4f);
            cart.linearVelocity = Vector3.zero; cart.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            host.DropHeld();
            for (int i = 0; i < 150; i++) yield return Step();
            var sensor = cart.GetComponentInChildren<CartCargoSensor>();
            Assert.That(Claim.HolderId, Is.Null); Assert.That(sensor.BodyCount, Is.EqualTo(1));
            Assert.That(sensor.Mass, Is.EqualTo(68).Within(0.01f)); Assert.That(sensor.Saturated, Is.False);
            Assert.That(patientRig.IsRagdoll, Is.True); Assert.That(patientController.enabled, Is.False);
        }
    }
}
