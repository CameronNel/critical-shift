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
        private LocalWorkerMotor walker;
        private CharacterController controller;
        private Rigidbody pelvis, cart;
        private double clock;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private WorkerView Worker => host.World.GetWorker(Id(1));
        private Rigidbody HeavyCrate => root.transform.Find("Local Gameplay Fixture/Material container 1").GetComponent<Rigidbody>();

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
            walker = local.GetComponent<LocalWorkerMotor>();
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

        private void AssertJointAnchorsMeet()
        {
            foreach (var joint in rig.GetComponentsInChildren<CharacterJoint>())
            {
                var body = joint.GetComponent<Rigidbody>();
                Vector3 own = body.position + body.rotation * joint.anchor;
                Vector3 parent = joint.connectedBody.position + joint.connectedBody.rotation * joint.connectedAnchor;
                Assert.That(Vector3.Distance(own, parent), Is.LessThan(0.01f), joint.name);
            }
        }

        [UnityTest] public IEnumerator WalkingPosePreservesAnchorsBeforeOneRagdollHandoff()
        {
            Vector3 before = controller.transform.position; walker.SetMovement(Vector2.right);
            for (int i = 0; i < 30; i++) yield return Step();
            walker.SetMovement(Vector2.zero); yield return null;
            Assert.That(controller.transform.position.x, Is.GreaterThan(before.x + 0.3f));
            Assert.That(DynamicBodies(), Is.Zero); Assert.That(controller.enabled, Is.True);
            AssertJointAnchorsMeet();
            KnockDown();
            Assert.That(controller.enabled, Is.False); Assert.That(DynamicBodies(), Is.EqualTo(11));
            for (int i = 0; i < 20; i++) yield return Step();
            foreach (var body in rig.CopyBodySegments())
                Assert.That(body.linearVelocity.magnitude, Is.LessThan(20), body.name);
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(controller.enabled, Is.False);
        }

        [UnityTest] public IEnumerator CarryPoseFollowsTheClaimWithoutChangingMaterialOrMotionOwnership()
        {
            var arm = rig.transform.Find("Left upper arm").GetComponent<Rigidbody>();
            Quaternion rest = arm.rotation; var batch = host.World.Production.GetBatch(Id(103));
            long revision = Worker.Revision;
            host.Grab(Id(103));
            Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            for (int i = 0; i < 35; i++) yield return Step();
            Assert.That(Quaternion.Angle(rest, arm.rotation), Is.GreaterThan(15));
            AssertJointAnchorsMeet();
            Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            Assert.That(host.World.Production.GetBatch(Id(103)).Units, Is.EqualTo(batch.Units));
            Assert.That(Worker.Revision, Is.EqualTo(revision));
            host.Release(Id(103));
            for (int i = 0; i < 35; i++) yield return Step();
            Assert.That(Quaternion.Angle(rest, arm.rotation), Is.LessThan(2));
            Assert.That(DynamicBodies(), Is.Zero); Assert.That(controller.enabled, Is.True);
            Assert.That(host.World.Production.GetBatch(Id(103)).Units, Is.EqualTo(12));
        }

        [UnityTest] public IEnumerator FacilityConsoleAnchorsAdmitProducedFuelThroughTheFullChain()
        {
            controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(-4, 0.1f, 2);
            controller.enabled = true; walker.ResetAfterRecovery();
            var ore = root.transform.Find("Local Gameplay Fixture/Material container 4").GetComponent<Rigidbody>();
            ore.position = root.transform.position + new Vector3(-4, 1, 3); ore.linearVelocity = Vector3.zero; Physics.SyncTransforms();
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            host.OperateMachine(Id(400), ProductionAction.Insert, Id(103), false, false);
            Assert.That(host.World.GetObject(Id(103)).SlotId, Is.EqualTo(Id(400)), host.LastAction);
            host.OperateMachine(Id(400), ProductionAction.SetPower, Guid.Empty, false, true);
            host.OperateMachine(Id(400), ProductionAction.Start, Guid.Empty, false, false);
            Assert.That(host.World.Production.GetMachine(Id(400)).Mode, Is.EqualTo(ProductionMode.Processing), host.LastAction);
            clock += 6.1; host.Pump();
            Assert.That(host.World.Production.GetBatch(Id(103)).Kind, Is.EqualTo(MaterialKind.CrushedOre));
            Assert.That(host.World.Production.GetBatch(Id(103)).Units, Is.EqualTo(11));
            host.OperateMachine(Id(400), ProductionAction.Eject, Guid.Empty, false, false);
            Assert.That(host.World.GetObject(Id(103)).SlotId, Is.Null, host.LastAction);
            controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(0.5f, 0.1f, 2);
            controller.enabled = true; walker.ResetAfterRecovery();
            ore.position = root.transform.position + new Vector3(0.5f, 1, 3); ore.linearVelocity = Vector3.zero; Physics.SyncTransforms();
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            host.OperateMachine(Id(401), ProductionAction.Insert, Id(103), false, false);
            Assert.That(host.World.GetObject(Id(103)).SlotId, Is.EqualTo(Id(401)), host.LastAction);
            host.OperateMachine(Id(401), ProductionAction.SetPower, Guid.Empty, false, true);
            host.OperateMachine(Id(401), ProductionAction.Start, Guid.Empty, false, false);
            Assert.That(host.World.Production.GetMachine(Id(401)).Mode, Is.EqualTo(ProductionMode.Processing), host.LastAction);
            clock += 9.1; host.Pump();
            Assert.That(host.World.Production.GetBatch(Id(103)).Kind, Is.EqualTo(MaterialKind.Fuel));
            Assert.That(host.World.Production.GetBatch(Id(103)).Units, Is.EqualTo(11));
            host.OperateMachine(Id(401), ProductionAction.Eject, Guid.Empty, false, false);
            Assert.That(host.World.GetObject(Id(103)).SlotId, Is.Null, host.LastAction);
            controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(5.5f, 0.1f, 3);
            controller.enabled = true; walker.ResetAfterRecovery();
            ore.position = root.transform.position + new Vector3(5.5f, 1.05f, 4.1f); ore.linearVelocity = Vector3.zero; Physics.SyncTransforms();
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)));
            host.OperateReactor(Id(500), ReactorAction.Insert, Id(103), false);
            Assert.That(host.World.GetObject(Id(103)).SlotId, Is.EqualTo(Id(500)), host.LastAction);
            host.OperateReactor(Id(500), ReactorAction.SetCooling, Guid.Empty, true);
            host.OperateReactor(Id(500), ReactorAction.Start, Guid.Empty, false);
            Assert.That(host.World.Reactor.View.Mode, Is.EqualTo(ReactorMode.Running), host.LastAction);
            clock += 1.1; host.Pump();
            Assert.That(host.World.Reactor.PowerSummary.Delivered, Is.GreaterThan(0));
            Assert.That(host.World.Production.Summary.ActiveUnits + host.World.Production.Summary.WasteUnits,
                Is.EqualTo(host.World.Production.Summary.IssuedUnits));
            yield return Step();
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
            yield return null; yield return null;
            Assert.That(controller.enabled, Is.False);
            Assert.That(root.transform.Find("Local Gameplay Fixture/Local worker status marker").GetComponent<WorkerStatusFeedback>().Visible, Is.True);
        }

        [UnityTest] public IEnumerator ShortHopLandsWithTheWalkingCapsuleStillOwningMotion()
        {
            for (int i = 0; i < 20; i++) yield return Step();
            float floor = controller.transform.position.y, peak = floor;
            long revision = Worker.Revision; walker.RequestJump();
            for (int i = 0; i < 80; i++)
            { yield return Step(); peak = Mathf.Max(peak, controller.transform.position.y); }
            Assert.That(peak - floor, Is.InRange(0.25f, 0.85f));
            Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.1f));
            Assert.That(walker.Grounded, Is.True); Assert.That(DynamicBodies(), Is.Zero);
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.Revision, Is.EqualTo(revision));
        }

        [UnityTest] public IEnumerator HopHitsTheLowCeilingWithoutTunnellingOrRetainedUpwardDrive()
        {
            for (int i = 0; i < 20; i++) yield return Step();
            var ceiling = GameObject.CreatePrimitive(PrimitiveType.Cube); ceiling.name = "Walking hop ceiling";
            ceiling.transform.SetParent(root.transform, false); ceiling.transform.position = controller.transform.position + Vector3.up * 2;
            ceiling.transform.localScale = new Vector3(2, 0.2f, 2); Physics.SyncTransforms();
            float floor = controller.transform.position.y, peak = floor; walker.RequestJump();
            for (int i = 0; i < 80; i++)
            { yield return Step(); peak = Mathf.Max(peak, controller.transform.position.y); }
            Assert.That(peak - floor, Is.LessThan(0.25f));
            Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.1f));
            Assert.That(walker.Grounded, Is.True); Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
        }

        [UnityTest] public IEnumerator PauseCartGripAndKnockdownCannotQueueALaterWalkingHop()
        {
            for (int i = 0; i < 20; i++) yield return Step();
            float floor = controller.transform.position.y;
            host.World.Pause(host.World.Epoch); walker.RequestJump(); host.World.Resume(host.World.Epoch);
            for (int i = 0; i < 20; i++)
            { yield return Step(); Assert.That(controller.transform.position.y, Is.LessThan(floor + 0.1f)); }
            var stand = cart.transform.Find("Cart operator stance");
            controller.enabled = false; controller.transform.position = stand.position + Vector3.up * 0.1f;
            controller.enabled = true; walker.ResetAfterRecovery(); Physics.SyncTransforms();
            for (int i = 0; i < 15; i++) yield return Step();
            host.Grab(Id(600)); Assert.That(host.IsHandleHeld(Id(600)), Is.True);
            floor = controller.transform.position.y; walker.RequestJump();
            for (int i = 0; i < 25; i++)
            { yield return Step(); Assert.That(controller.transform.position.y, Is.LessThan(floor + 0.1f)); }
            Assert.That(host.IsHandleHeld(Id(600)), Is.True);
            host.DropHeld(); KnockDown(); walker.RequestJump();
            for (int i = 0; i < 15; i++) yield return Step();
            Assert.That(controller.enabled, Is.False); Assert.That(DynamicBodies(), Is.EqualTo(11));
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
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

        [UnityTest] public IEnumerator RegisteredHeavyFallingCrateCreatesOneKnockdownEpisode()
        {
            for (int i = 0; i < 15; i++) yield return Step();
            var heavy = HeavyCrate; Assert.That(heavy.mass, Is.EqualTo(27).Within(0.001f));
            heavy.position = controller.transform.position + Vector3.up * 3.2f;
            heavy.linearVelocity = Vector3.down * 4; Physics.SyncTransforms();
            for (int i = 0; i < 65 && Worker.Pose == WorkerPose.Upright; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(Worker.LastHazardId, Is.EqualTo(Id(100)));
            long episode = Worker.RecoveryEpisode;
            for (int i = 0; i < 30; i++) yield return Step();
            Assert.That(Worker.RecoveryEpisode, Is.EqualTo(episode)); Assert.That(controller.enabled, Is.False);
            Assert.That(DynamicBodies(), Is.EqualTo(11));
        }

        [UnityTest] public IEnumerator HeldHeavyCrateCannotReportAFreeFallingBodyImpact()
        {
            for (int i = 0; i < 15; i++) yield return Step();
            var heavy = HeavyCrate;
            heavy.position = controller.transform.position + Vector3.up + Vector3.forward * 1.3f; Physics.SyncTransforms();
            host.Grab(Id(100)); Assert.That(host.World.GetObject(Id(100)).HolderId, Is.EqualTo(Id(1)));
            heavy.position = controller.transform.position + Vector3.up * 2.1f;
            heavy.linearVelocity = Vector3.down * 4; Physics.SyncTransforms();
            for (int i = 0; i < 30; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.RecoveryEpisode, Is.Zero);
            Assert.That(host.World.GetObject(Id(100)).HolderId, Is.EqualTo(Id(1))); Assert.That(controller.enabled, Is.True);
        }

        [UnityTest] public IEnumerator RegisteredFallingSourceBelowTheMassThresholdCannotKnockDown()
        {
            for (int i = 0; i < 15; i++) yield return Step();
            var heavy = HeavyCrate;
            heavy.mass = 9; // Synthetic observation fixture for the authored physical threshold.
            heavy.position = controller.transform.position + Vector3.up * 3.2f;
            heavy.linearVelocity = Vector3.down * 4; Physics.SyncTransforms();
            for (int i = 0; i < 65; i++) yield return Step();
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
            yield return null; yield return null;
            Assert.That(root.transform.Find("Local Gameplay Fixture/Local worker status marker").GetComponent<WorkerStatusFeedback>().Visible, Is.False);
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

        [UnityTest] public IEnumerator AlertDownWorkerCrawlsWithOneMotionOwnerAndStopsDuringPause()
        {
            state.DiagnosticKnockdown();
            for (int i = 0; i < 120; i++) yield return Step();
            Vector3 before = pelvis.position; long revision = Worker.Revision; state.SetDownMovement(Vector2.right);
            for (int i = 0; i < 200; i++) yield return Step();
            Assert.That(pelvis.position.x, Is.GreaterThan(before.x + 0.1f));
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(controller.enabled, Is.False);
            Assert.That(rig.IsRagdoll, Is.True); Assert.That(Worker.Revision, Is.EqualTo(revision));
            host.World.Pause(host.World.Epoch); yield return Step();
            Assert.That(state.CrawlDriveActive, Is.False); Assert.That(Worker.Revision, Is.EqualTo(revision));
            state.SetDownMovement(Vector2.zero);
        }

        [UnityTest] public IEnumerator AlertDownLookTurnsOnlyTheEyesAndCrawlFollowsThatHeading()
        {
            KnockDown(); for (int i = 0; i < 120; i++) yield return Step();
            Assert.Throws<InvalidOperationException>(() => walker.ResetAfterRecovery());
            var eyes = controller.transform.Find("Worker eyes"); Quaternion rootRotation = controller.transform.rotation;
            var parts = rig.CopyBodySegments(); var rotations = new Quaternion[parts.Length]; var positions = new Vector3[parts.Length];
            for (int i = 0; i < parts.Length; i++) { rotations[i] = parts[i].rotation; positions[i] = parts[i].position; }
            long revision = Worker.Revision;
            for (int i = 0; i < 3; i++) walker.Look(new Vector2(150, 0));
            Assert.That(Vector3.Dot(eyes.forward, Vector3.right), Is.GreaterThan(0.99f));
            Assert.That(Quaternion.Angle(rootRotation, controller.transform.rotation), Is.LessThan(0.01f));
            for (int i = 0; i < parts.Length; i++)
            { Assert.That(parts[i].position, Is.EqualTo(positions[i])); Assert.That(Quaternion.Angle(parts[i].rotation, rotations[i]), Is.LessThan(0.01f)); }
            Vector3 before = pelvis.position; state.SetDownMovement(Vector2.up);
            for (int i = 0; i < 200; i++) yield return Step();
            state.SetDownMovement(Vector2.zero);
            Assert.That(pelvis.position.x, Is.GreaterThan(before.x + 0.1f)); Assert.That(controller.enabled, Is.False);
            Assert.That(Worker.Revision, Is.EqualTo(revision)); Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
        }

        [UnityTest] public IEnumerator RecoveryPreservesDownLookAndUnconsciousWorkersCannotLook()
        {
            KnockDown(); for (int i = 0; i < 120; i++) yield return Step();
            var eyes = controller.transform.Find("Worker eyes");
            for (int i = 0; i < 3; i++) walker.Look(new Vector2(150, 50));
            Quaternion look = eyes.rotation;
            for (int i = 0; i < 250 && Worker.Pose != WorkerPose.Upright; i++)
            { yield return Step(); if (i % 10 == 0 && Worker.Pose == WorkerPose.Down) state.RequestRecovery(); }
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright), state.LastAction);
            Assert.That(Quaternion.Angle(look, eyes.rotation), Is.LessThan(2));
            Assert.That(Mathf.Abs(Mathf.DeltaAngle(controller.transform.eulerAngles.y, eyes.eulerAngles.y)), Is.LessThan(2));
            Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
            var impact = host.World.ApplyWorkerImpact(host.World.Epoch, Id(1), 1, WorkerImpact.Incapacitating, 1500, Id(704), Id(705));
            Assert.That(impact.Status, Is.EqualTo(WorkerStatus.Applied)); look = eyes.rotation;
            long revision = Worker.Revision; walker.Look(new Vector2(150, 100)); yield return Step();
            Assert.That(Quaternion.Angle(look, eyes.rotation), Is.LessThan(0.01f)); Assert.That(Worker.Revision, Is.EqualTo(revision));
            Assert.That(Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious)); Assert.That(controller.enabled, Is.False);
        }

        [UnityTest] public IEnumerator UprightAndUnconsciousWorkersCannotUseTheCrawlForcePath()
        {
            state.SetDownMovement(Vector2.right); yield return Step();
            Assert.That(state.CrawlDriveActive, Is.False); Assert.That(controller.enabled, Is.True);
            var impact = host.World.ApplyWorkerImpact(host.World.Epoch, Id(1), 1, WorkerImpact.Incapacitating, 1500, Id(704), Id(705));
            Assert.That(impact.Status, Is.EqualTo(WorkerStatus.Applied));
            for (int i = 0; i < 120; i++) yield return Step();
            state.SetDownMovement(Vector2.right);
            for (int i = 0; i < 100; i++) yield return Step();
            Assert.That(state.CrawlDriveActive, Is.False); Assert.That(Worker.Awareness, Is.EqualTo(WorkerAwareness.Unconscious));
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(controller.enabled, Is.False);
        }

        [UnityTest] public IEnumerator ConsciousWorkerCanCrawlOutFromUnderABlockedRecoveryCeiling()
        {
            state.DiagnosticKnockdown();
            for (int i = 0; i < 120; i++) yield return Step();
            var ceiling = GameObject.CreatePrimitive(PrimitiveType.Cube); ceiling.transform.SetParent(root.transform, false);
            Vector3 center = pelvis.position;
            ceiling.transform.position = new Vector3(center.x, root.transform.position.y + 1.89f, center.z);
            ceiling.transform.localScale = new Vector3(1.4f, 0.16f, 3); Physics.SyncTransforms();
            state.RequestRecovery(); Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
            state.SetDownMovement(Vector2.right);
            for (int i = 0; i < 300 && pelvis.position.x - center.x < 1.2f; i++) yield return Step();
            state.SetDownMovement(Vector2.zero);
            Assert.That(pelvis.position.x - center.x, Is.GreaterThanOrEqualTo(1.2f));
            for (int i = 0; i < 100 && Worker.Pose != WorkerPose.Upright; i++)
            { yield return Step(); if (i % 10 == 0 && Worker.Pose == WorkerPose.Down) state.RequestRecovery(); }
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright), state.LastAction);
            Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
        }
    }
}
