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
    public sealed class WorkerPhysicsTests
    {
        private GameObject root;
        private LocalWorldHost host;
        private LocalWorkerStateHost state;
        private WorkerBodyRig rig;
        private LocalWorkerMotor walker;
        private CharacterController controller;
        private Rigidbody pelvis, cart;
        private List<Exception> faults;
        private double clock;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private WorkerView Worker
        {
            get
            {
                var world = host == null ? null : host.World;
                var worker = world == null ? null : world.GetWorker(Id(1));
                Assert.That(worker, Is.Not.Null, "Worker observation was removed; world=" +
                    (world == null ? "unavailable" : world.View.Phase.ToString()) + "; recorded fixture faults:\n" +
                    (faults == null ? "unavailable" : string.Join("\n", faults)));
                return worker;
            }
        }
        private Rigidbody HeavyCrate => root.transform.Find("Local Gameplay Fixture/Material container 1").GetComponent<Rigidbody>();

        [UnitySetUp] public IEnumerator SetUp()
        {
            clock = 0; faults = new List<Exception>();
            root = new GameObject("Worker physics integration fixture"); root.transform.position = new Vector3(2500, 0, 2500);
            var bootstrap = root.AddComponent<SandboxBootstrap>();
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.BindFixtureShader(shader);
            bootstrap.BindFixtureClock(() => clock);
            bootstrap.BindFixtureDiagnostics(faults.Add);
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
            if (root != null)
            {
                root.GetComponent<SandboxBootstrap>().enabled = false;
                UnityEngine.Object.Destroy(root);
            }
            yield return null; LogAssert.NoUnexpectedReceived();
            Assert.That(faults, Is.Empty, "Unexpected worker fixture fault.");
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
                Vector3 visibleOwn = body.transform.TransformPoint(joint.anchor);
                Vector3 visibleParent = joint.connectedBody.transform.TransformPoint(joint.connectedAnchor);
                string observation = joint.name + " physical=" + own.ToString("F5") + " / " + parent.ToString("F5") +
                    " visible=" + visibleOwn.ToString("F5") + " / " + visibleParent.ToString("F5") +
                    " root=" + controller.transform.position.ToString("F5") + " velocity=" + walker.MeasuredVelocity.ToString("F5");
                Assert.That(Vector3.Distance(own, parent), Is.LessThan(0.01f), observation);
                Assert.That(Vector3.Distance(visibleOwn, visibleParent), Is.LessThan(0.01f), observation);
                Assert.That(Vector3.Distance(own, visibleOwn), Is.LessThan(0.001f), observation);
                Assert.That(Vector3.Distance(parent, visibleParent), Is.LessThan(0.001f), observation);
            }
        }

        private string WalkingContactObservation()
        {
            var floor = root.transform.Find("Local Gameplay Fixture/Fixture floor").GetComponent<Collider>();
            return "y=" + controller.transform.position.y.ToString("F6") + " floor=" + floor.bounds.max.y.ToString("F6") +
                " grounded=" + walker.Grounded + " nativeGrounded=" + controller.isGrounded + " flags=" + controller.collisionFlags +
                " nativeVelocity=" + controller.velocity.ToString("F5") + " measuredVelocity=" + walker.MeasuredVelocity.ToString("F5") +
                " minMoveDistance=" + controller.minMoveDistance + " skinWidth=" + controller.skinWidth + " dt=" + Time.deltaTime;
        }

        private WorkerBodyRig CreateIsolatedRig(out CharacterController capsule, out Transform eyes,
            out Rigidbody[] parts, out Collider[] contacts)
        {
            var worker = new GameObject("Isolated worker setup fixture"); worker.transform.SetParent(root.transform, false);
            worker.transform.localPosition = new Vector3(0, 6, 0);
            capsule = worker.AddComponent<CharacterController>();
            eyes = new GameObject("Isolated worker eyes").transform; eyes.SetParent(worker.transform, false);
            parts = new Rigidbody[2]; contacts = new Collider[2];
            for (int i = 0; i < parts.Length; i++)
            {
                var segment = new GameObject("Isolated worker segment " + i); segment.transform.SetParent(worker.transform, false);
                segment.transform.localPosition = Vector3.up * (i + 1);
                contacts[i] = segment.AddComponent<SphereCollider>();
                parts[i] = segment.AddComponent<Rigidbody>(); parts[i].useGravity = false;
            }
            var grip = new GameObject("Isolated worker grip").transform; grip.SetParent(parts[1].transform, false);
            return worker.AddComponent<WorkerBodyRig>();
        }

        [UnityTest] public IEnumerator BodyRigRejectsNonContactingSegmentsBeforeChangingMotionOwnership()
        {
            var body = CreateIsolatedRig(out var capsule, out var eyes, out var parts, out var contacts);
            var grip = parts[1].transform.Find("Isolated worker grip"); parts[1].detectCollisions = false;
            Assert.Throws<ArgumentException>(() => body.Initialize(Id(800), Id(801), capsule, eyes, parts[0], parts[1].transform, grip, parts, contacts));
            Assert.That(body.BodyCount, Is.Zero); Assert.That(capsule.enabled, Is.True);
            foreach (var part in parts) Assert.That(part.isKinematic, Is.False);
            foreach (var contact in contacts) Assert.That(contact.enabled, Is.True);
            parts[1].detectCollisions = true;
            foreach (var contact in contacts) contact.enabled = false;
            var ownContact = contacts[1]; contacts[1] = contacts[0];
            Assert.Throws<ArgumentException>(() => body.Initialize(Id(800), Id(801), capsule, eyes, parts[0], parts[1].transform, grip, parts, contacts),
                "A disabled contact still requires its own structural motion owner.");
            Assert.That(body.BodyCount, Is.Zero); contacts[1] = ownContact;
            body.Initialize(Id(800), Id(801), capsule, eyes, parts[0], parts[1].transform, grip, parts, contacts);
            Assert.That(body.BodyCount, Is.EqualTo(2)); Assert.That(capsule.enabled, Is.True);
            foreach (var part in parts) Assert.That(part.isKinematic, Is.True);
            foreach (var contact in contacts) Assert.That(contact.enabled, Is.False);
            UnityEngine.Object.Destroy(body.gameObject); yield return null;
        }

        [UnityTest] public IEnumerator RejectedWorkerAdapterSetupLeavesNoLiveBindingAndAllowsCorrection()
        {
            var body = CreateIsolatedRig(out var capsule, out var eyes, out var parts, out var contacts);
            var recovery = new WorkerRecoveryPlacement();
            var setupWorld = new WorldSession(new WorldSessionConfiguration(18, 60000, true), new SpatialInteractionAccess(), recovery);
            setupWorld.RegisterConnection(Id(810), Id(811));
            body.Initialize(setupWorld.Epoch, Id(811), capsule, eyes, parts[0], parts[1].transform,
                parts[1].transform.Find("Isolated worker grip"), parts, contacts);
            recovery.Bind(body);
            var motor = body.gameObject.AddComponent<LocalWorkerMotor>();
            Func<WorkerView> read = () => setupWorld.GetWorker(Id(811));
            Func<bool> running = () => setupWorld.View.Phase == WorldPhase.Running;
            Assert.Throws<ArgumentNullException>(() => motor.Initialize(eyes, read, null, faults.Add));
            Assert.Throws<ArgumentNullException>(() => motor.Initialize(eyes, read, running, null));
            motor.Initialize(eyes, read, running, faults.Add);
            var adapter = body.gameObject.AddComponent<LocalWorkerStateHost>();
            Assert.Throws<ArgumentNullException>(() => adapter.Initialize(setupWorld, Id(811), body, recovery, () => { }, () => { }, null));
            Assert.That(adapter.Worker, Is.Null); Assert.Throws<InvalidOperationException>(() => adapter.BindHazard(Id(812)));
            adapter.Initialize(setupWorld, Id(811), body, recovery, () => { }, motor.ResetAfterRecovery, faults.Add);
            adapter.BindHazard(Id(812));
            var observer = body.gameObject.AddComponent<WorkerImpactContacts>();
            Assert.Throws<ArgumentNullException>(() => observer.Initialize(capsule, read, running, () => Vector3.zero,
                adapter.ObserveKnockdown, null));
            Assert.Throws<InvalidOperationException>(() => observer.BindHazard(Id(812), cart));
            observer.Initialize(capsule, read, running, () => Vector3.zero, adapter.ObserveKnockdown, faults.Add);
            observer.BindHazard(Id(812), cart);
            setupWorld.Start(); adapter.Activate(); observer.Activate();
            Assert.That(capsule.enabled, Is.True); Assert.That(adapter.Worker.Pose, Is.EqualTo(WorkerPose.Upright));
            Assert.That(setupWorld.View.Phase, Is.EqualTo(WorldPhase.Running));
            setupWorld.Stop(); adapter.Shutdown(); UnityEngine.Object.Destroy(body.gameObject); yield return null;
        }

        [UnityTest] public IEnumerator SaturatedWalkingSupportUpdateStopsTheWorldBeforeMoving()
        { yield return VerifySaturatedWalkingSupportStopsMotor(false); }

        [UnityTest] public IEnumerator SaturatedWalkingSupportGetterStopsTheWorldOnce()
        { yield return VerifySaturatedWalkingSupportStopsMotor(true); }

        private IEnumerator VerifySaturatedWalkingSupportStopsMotor(bool fromGetter)
        {
            for (int i = 0; i < 15; i++) yield return Step();
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation());
            var floor = root.transform.Find("Local Gameplay Fixture/Fixture floor").GetComponent<Collider>();
            for (int i = 0; i < 32; i++)
            {
                var support = new GameObject("Saturated walking support " + i).AddComponent<BoxCollider>();
                support.transform.SetParent(root.transform, false);
                support.transform.position = new Vector3(controller.transform.position.x, floor.bounds.max.y - 0.05f, controller.transform.position.z);
                support.size = new Vector3(2, 0.1f, 2);
            }
            Physics.SyncTransforms();
            float skin = Mathf.Min(controller.skinWidth, controller.radius * 0.5f);
            Vector3 foot = controller.transform.TransformPoint(controller.center) -
                Vector3.up * Mathf.Max(0, controller.height * 0.5f - controller.radius);
            var observations = new RaycastHit[32];
            int observed = Physics.SphereCastNonAlloc(foot, controller.radius - skin, Vector3.down, observations,
                skin * 2 + 0.002f, Physics.AllLayers, QueryTriggerInteraction.Ignore);
            Assert.That(observed, Is.EqualTo(observations.Length), "Fixture must saturate the real native walking-support query.");
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Running));
            walker.SetMovement(Vector2.right); walker.RequestJump();
            Vector3 before = controller.transform.position;
            if (fromGetter)
            {
                bool grounded = true;
                Assert.DoesNotThrow(() => grounded = walker.Grounded);
                Assert.That(grounded, Is.False);
            }
            else walker.SendMessage("Update", SendMessageOptions.RequireReceiver);
            Assert.That(faults.Count, Is.EqualTo(1));
            Assert.That(faults[0].Message, Does.Contain("Walking support observation bounds were saturated")); faults.Clear();
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(host.BoundBodyCount, Is.Zero);
            Assert.That(host.World.View.ActiveClaimCount, Is.Zero); Assert.That(walker.enabled, Is.False);
            Assert.That(walker.MeasuredVelocity, Is.EqualTo(Vector3.zero));
            Assert.That(controller.transform.position, Is.EqualTo(before), "Fault reporting must not resume this update into controller.Move.");
            // Public callbacks can still be invoked on a disabled component; they cannot reacquire or report again.
            for (int i = 0; i < 3; i++)
            {
                Assert.That(walker.Grounded, Is.False); walker.SetMovement(Vector2.right); walker.RequestJump();
                walker.SendMessage("Update", SendMessageOptions.RequireReceiver);
            }
            yield return null; yield return Step();
            Assert.That(faults, Is.Empty); Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(controller.transform.position, Is.EqualTo(before)); Assert.That(walker.MeasuredVelocity, Is.EqualTo(Vector3.zero));
            Assert.That(controller.enabled, Is.False, "The existing worker body owner completes physical shutdown.");
            Assert.That(DynamicBodies(), Is.Zero);
        }

        [UnityTest] public IEnumerator LosingRagdollCollisionDetectionStopsTheWorldBeforeRecovery()
        {
            KnockDown(); var parts = rig.CopyBodySegments(); parts[4].detectCollisions = false;
            yield return null; yield return Step();
            Assert.That(faults.Count, Is.EqualTo(1)); Assert.That(faults[0].Message, Does.Contain("physical rig binding")); faults.Clear();
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(host.World.View.ActiveClaimCount, Is.Zero);
            Assert.That(host.BoundBodyCount, Is.Zero); Assert.That(controller.enabled, Is.False);
            Assert.That(parts[4].detectCollisions, Is.False, "Cleanup cannot silently repair the lost contact setting.");
            foreach (var part in parts) Assert.That(part.isKinematic, Is.True);
            state.RequestRecovery(); yield return null;
            Assert.That(controller.enabled, Is.False); Assert.That(DynamicBodies(), Is.Zero);
        }

        [UnityTest] public IEnumerator ReparentedWorkerSegmentStopsTheWorldBeforePosePublication()
        { yield return VerifyWorkerHierarchyMutationStopsPublication(false); }

        [UnityTest] public IEnumerator ReparentedWorkerIntermediateStopsTheWorldBeforePosePublication()
        { yield return VerifyWorkerHierarchyMutationStopsPublication(true); }

        private IEnumerator VerifyWorkerHierarchyMutationStopsPublication(bool intermediate)
        {
            walker.SetMovement(Vector2.right);
            for (int i = 0; i < 15; i++) yield return Step();
            // The controller itself may move/reparent with its complete owned hierarchy. Its parent is outside the fence.
            var outer = new GameObject("Allowed whole-worker parent").transform;
            outer.SetParent(controller.transform.parent, false); controller.transform.SetParent(outer, true);
            Physics.SyncTransforms(); rig.UpdatePresentation();
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Running)); Assert.That(faults, Is.Empty);
            walker.SetMovement(Vector2.zero);
            var parts = rig.CopyBodySegments();
            if (intermediate)
            {
                var bridge = new GameObject("Unexpected in-worker intermediate").transform;
                bridge.SetParent(controller.transform, false); rig.transform.SetParent(bridge, true);
            }
            else parts[1].transform.SetParent(parts[2].transform, true); // Torso now follows Head, reversing their cached order.
            Physics.SyncTransforms();
            var positions = new Vector3[parts.Length]; var rotations = new Quaternion[parts.Length];
            for (int i = 0; i < parts.Length; i++) { positions[i] = parts[i].position; rotations[i] = parts[i].rotation; }
            Vector3 rootBefore = controller.transform.position;
            // The public presentation path must reject before advancing the current walking pose or publishing a segment.
            rig.UpdatePresentation(); AssertUnchanged();
            // Exercise the real adapter failure boundary: one external failure stops the existing local world.
            state.SendMessage("LateUpdate", SendMessageOptions.RequireReceiver);
            Assert.That(faults.Count, Is.EqualTo(1)); Assert.That(faults[0].Message, Does.Contain("physical rig binding")); faults.Clear();
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(host.BoundBodyCount, Is.Zero);
            Assert.That(host.World.View.ActiveClaimCount, Is.Zero); Assert.That(controller.enabled, Is.False);
            Assert.That(DynamicBodies(), Is.Zero); AssertUnchanged();
            state.SendMessage("LateUpdate", SendMessageOptions.RequireReceiver); rig.UpdatePresentation(); AssertUnchanged();
            yield return null; yield return Step();
            Assert.That(faults, Is.Empty); Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped)); AssertUnchanged();

            void AssertUnchanged()
            {
                Assert.That(controller.transform.position, Is.EqualTo(rootBefore));
                for (int i = 0; i < parts.Length; i++)
                {
                    Assert.That(parts[i].position, Is.EqualTo(positions[i]), parts[i].name);
                    Assert.That(Quaternion.Angle(parts[i].rotation, rotations[i]), Is.LessThan(0.001f), parts[i].name);
                }
            }
        }

        [UnityTest] public IEnumerator WalkingPosePreservesAnchorsBeforeOneRagdollHandoff()
        {
            foreach (var part in rig.CopyBodySegments())
            {
                var contact = part.GetComponent<Collider>();
                Assert.That(contact.enabled, Is.False); Assert.That(contact.isTrigger, Is.False);
                Assert.That(contact.GetComponentInParent<Rigidbody>(), Is.SameAs(part), part.name);
            }
            Vector3 before = controller.transform.position; walker.SetMovement(Vector2.right);
            for (int i = 0; i < 30; i++) { yield return Step(); AssertJointAnchorsMeet(); }
            walker.SetMovement(Vector2.zero); yield return null;
            Assert.That(controller.transform.position.x, Is.GreaterThan(before.x + 0.3f));
            Assert.That(DynamicBodies(), Is.Zero); Assert.That(controller.enabled, Is.True);
            AssertJointAnchorsMeet();
            KnockDown();
            AssertJointAnchorsMeet(); // The physical handoff must retain that exact coherent chain before simulation.
            Assert.That(controller.enabled, Is.False); Assert.That(DynamicBodies(), Is.EqualTo(11));
            foreach (var part in rig.CopyBodySegments())
            {
                var contact = part.GetComponent<Collider>();
                Assert.That(contact.enabled, Is.True); Assert.That(part.detectCollisions, Is.True);
                Assert.That(contact.attachedRigidbody, Is.SameAs(part), part.name);
            }
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
            void PlaceOre(Vector3 position)
            {
                // Explicit test relocation must update the interpolated query transform as well as the physical pose.
                ore.position = position; ore.transform.position = position;
                ore.linearVelocity = Vector3.zero; ore.angularVelocity = Vector3.zero; Physics.SyncTransforms();
                var eyes = controller.transform.Find("Worker eyes");
                Assert.That(Vector3.Distance(ore.position, ore.transform.position), Is.LessThan(0.001f), "Ore physical/query poses must agree.");
                Assert.That(Vector3.Distance(eyes.position, ore.transform.position), Is.LessThan(3.8f), "Relocated ore must be inside authored interaction reach.");
            }
            PlaceOre(root.transform.position + new Vector3(-4, 1, 3));
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
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
            PlaceOre(root.transform.position + new Vector3(0.5f, 1, 3));
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
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
            PlaceOre(root.transform.position + new Vector3(5.5f, 1.05f, 4.1f));
            host.Grab(Id(103)); Assert.That(host.World.GetObject(Id(103)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
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

        [UnityTest] public IEnumerator OreWasherUsesItsPhysicalSocketAndRetainsWetOutputForTheDryer()
        {
            var crate = root.transform.Find("Local Gameplay Fixture/Material container 6").GetComponent<Rigidbody>();
            var original = host.World.Production.GetBatch(Id(105));
            void PlaceNear(float x)
            {
                controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(x, 0.1f, 6);
                controller.enabled = true; walker.ResetAfterRecovery();
                crate.position = root.transform.position + new Vector3(x, 1, 7); crate.transform.position = crate.position;
                crate.linearVelocity = Vector3.zero; crate.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            }
            PlaceNear(-3.5f); host.Grab(Id(105)); Assert.That(host.World.GetObject(Id(105)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
            host.OperateMachine(Id(403), ProductionAction.Insert, Id(105), false, false);
            Assert.That(host.World.GetObject(Id(105)).SlotId, Is.EqualTo(Id(403)), host.LastAction);
            host.OperateMachine(Id(403), ProductionAction.Start, Guid.Empty, true, false);
            Assert.That(host.World.Production.GetMachine(Id(403)).Mode, Is.EqualTo(ProductionMode.Idle), host.LastAction);
            Assert.That(host.LastAction, Does.Contain("safe cycle"));
            host.OperateMachine(Id(403), ProductionAction.Start, Guid.Empty, false, false); clock += 10.1; host.Pump();
            var washed = host.World.Production.GetBatch(Id(105));
            Assert.That(washed.Contamination, Is.EqualTo(100)); Assert.That(washed.Moisture, Is.EqualTo(1000)); Assert.That(washed.Units, Is.EqualTo(12));
            Assert.That(washed.ParentBatchId, Is.EqualTo(original.BatchId)); Assert.That(washed.CauseId, Is.EqualTo(original.CauseId));
            host.OperateMachine(Id(403), ProductionAction.Eject, Guid.Empty, false, false);
            Assert.That(host.World.GetObject(Id(105)).SlotId, Is.Null, host.LastAction);
            PlaceNear(-8.5f); host.Grab(Id(105)); host.OperateMachine(Id(402), ProductionAction.Insert, Id(105), false, false);
            Assert.That(host.World.GetObject(Id(105)).SlotId, Is.EqualTo(Id(402)), host.LastAction);
            host.OperateMachine(Id(402), ProductionAction.Start, Guid.Empty, false, false); clock += 8.1; host.Pump();
            var dried = host.World.Production.GetBatch(Id(105)); Assert.That(dried.Moisture, Is.EqualTo(100)); Assert.That(dried.Contamination, Is.EqualTo(100));
            Assert.That(dried.ParentBatchId, Is.EqualTo(washed.BatchId)); Assert.That(host.World.Production.Summary.ReserveSpent, Is.EqualTo(2));
            Assert.That(host.BoundBodyCount, Is.EqualTo(11)); yield return Step();
        }

        [UnityTest] public IEnumerator ReactorRoutingConsoleSettlesPriorOutputBeforeChangingTheValve()
        {
            host.SetReactorOutputRouting(Id(500), ReactorOutputRouting.GridPriority);
            Assert.That(host.World.Reactor.View.OutputRouting, Is.EqualTo(ReactorOutputRouting.Balanced), "The remote console request must still require spatial admission.");
            controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(5.5f, 0.1f, 3);
            controller.enabled = true; walker.ResetAfterRecovery(); rig.UpdatePresentation();
            var fuel = root.transform.Find("Local Gameplay Fixture/Material container 7").GetComponent<Rigidbody>();
            fuel.position = root.transform.position + new Vector3(5.5f, 1.05f, 4.1f); fuel.transform.position = fuel.position;
            fuel.linearVelocity = Vector3.zero; fuel.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            host.Grab(Id(106)); host.OperateReactor(Id(500), ReactorAction.Insert, Id(106), false);
            Assert.That(host.World.GetObject(Id(106)).SlotId, Is.EqualTo(Id(500)), host.LastAction);
            host.OperateReactor(Id(500), ReactorAction.SetCooling, Guid.Empty, true); host.OperateReactor(Id(500), ReactorAction.Start, Guid.Empty, false);
            clock += 0.5; host.SetReactorOutputRouting(Id(500), ReactorOutputRouting.GridPriority);
            Assert.That(host.World.Reactor.PowerSummary.Delivered, Is.EqualTo(4)); Assert.That(host.LastAction, Does.Contain("Grid priority"));
            clock += 0.5; host.SetReactorOutputRouting(Id(500), ReactorOutputRouting.ReservePriority);
            Assert.That(host.World.Reactor.PowerSummary.Delivered, Is.EqualTo(9)); clock += 0.5; host.Pump();
            var power = host.World.Reactor.PowerSummary;
            Assert.That(power.Generated, Is.EqualTo(15)); Assert.That(power.Available, Is.EqualTo(13)); Assert.That(power.Delivered, Is.EqualTo(9));
            Assert.That(power.Initial + power.Generated, Is.EqualTo(power.Available + power.Spent + power.Delivered + power.Spilled)); yield return null;
        }

        private void GrabDirtyCargoAtWashArea()
        {
            controller.enabled = false; controller.transform.position = root.transform.position + new Vector3(5, 0.1f, -4.5f);
            controller.enabled = true; walker.ResetAfterRecovery(); rig.UpdatePresentation();
            var crate = root.transform.Find("Local Gameplay Fixture/Material container 6").GetComponent<Rigidbody>();
            crate.position = controller.transform.position + new Vector3(0, 1, 1.2f); crate.transform.position = crate.position;
            crate.linearVelocity = Vector3.zero; crate.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            host.Grab(Id(105)); Assert.That(host.World.GetObject(Id(105)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
        }

        [UnityTest] public IEnumerator WashingSamplesBeforeDirtyCargoAndCueReadsCannotAddExposure()
        {
            GrabDirtyCargoAtWashArea();
            var zones = root.GetComponentInChildren<WorkerContaminationZones>();
            zones.Sample(); Assert.That(Worker.Contamination, Is.EqualTo(12));
            Assert.That(zones.Describe(Id(1)), Does.Contain("Wash area")); Assert.That(zones.Describe(Id(1)), Does.Contain("Crate 6"));
            long revision = Worker.Revision;
            zones.Describe(Id(1)); zones.Describe(Id(1)); zones.Sample(); Assert.That(Worker.Revision, Is.EqualTo(revision));
            clock += 1; zones.Sample();
            Assert.That(Worker.Contamination, Is.EqualTo(12), "The due wash removes12 before the new handling contact adds12.");
            Assert.That(Worker.Revision, Is.EqualTo(revision + 2));
            Assert.That(host.World.Production.GetBatch(Id(105)).Contamination, Is.EqualTo(800));
            host.Release(Id(105)); clock += 1; zones.Sample(); Assert.That(Worker.Contamination, Is.Zero);
            Assert.That(zones.Describe(Id(1)), Does.Not.Contain("Crate 6")); yield return null;
        }

        [UnityTest] public IEnumerator PausedCargoSamplingExpiresRealtimeCustodyWithoutAddingAnotherDose()
        {
            GrabDirtyCargoAtWashArea(); var zones = root.GetComponentInChildren<WorkerContaminationZones>(); zones.Sample();
            Assert.That(Worker.Contamination, Is.EqualTo(12)); host.World.Pause(host.World.Epoch);
            long shift = host.World.View.ElapsedMilliseconds, revision = Worker.Revision;
            clock += 10; zones.Sample();
            Assert.That(host.World.View.ElapsedMilliseconds, Is.EqualTo(shift)); Assert.That(Worker.Revision, Is.EqualTo(revision));
            Assert.That(host.World.GetObject(Id(105)).HolderId, Is.Null);
            host.World.Resume(host.World.Epoch); zones.Sample(); Assert.That(Worker.Contamination, Is.EqualTo(12));
            Assert.That(zones.Describe(Id(1)), Does.Not.Contain("Crate 6")); yield return null;
        }

        [UnityTest] public IEnumerator CompetingCargoProducerStopsTheFixtureOnceAndClearsItsBindings()
        {
            GrabDirtyCargoAtWashArea();
            Assert.That(host.World.ObserveWorkerContamination(host.World.Epoch, Id(1), Id(745), 1, Id(799), 0).Status, Is.EqualTo(WorkerStatus.Applied));
            var zones = root.GetComponentInChildren<WorkerContaminationZones>(); zones.Sample();
            Assert.That(faults.Count, Is.EqualTo(1)); faults.Clear();
            Assert.That(host.World.View.Phase, Is.EqualTo(WorldPhase.Stopped)); Assert.That(host.BoundBodyCount, Is.Zero);
            Assert.That(zones.Describe(Id(1)), Is.EqualTo("No active exposure/wash sampling"));
            zones.Sample(); zones.Sample(); yield return null; Assert.That(faults, Is.Empty);
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
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation());
            Assert.That(controller.minMoveDistance, Is.Zero);
            float floor = controller.transform.position.y, peak = floor;
            long revision = Worker.Revision; walker.RequestJump();
            for (int i = 0; i < 80; i++)
            {
                yield return Step(); peak = Mathf.Max(peak, controller.transform.position.y);
                if (i >= 60)
                {
                    string observation = WalkingContactObservation();
                    Assert.That(walker.Grounded, Is.True, observation);
                    Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.01f), observation);
                    Assert.That(Mathf.Abs(walker.MeasuredVelocity.y), Is.LessThan(0.05f), observation);
                }
            }
            Assert.That(peak - floor, Is.InRange(0.25f, 0.85f));
            Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.1f));
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation()); Assert.That(DynamicBodies(), Is.Zero);
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.Revision, Is.EqualTo(revision));
            var support = root.transform.Find("Local Gameplay Fixture/Fixture floor").GetComponent<Collider>();
            Physics.IgnoreCollision(controller, support, true);
            Assert.That(walker.Grounded, Is.False, "An ignored collision pair cannot remain walking support: " + WalkingContactObservation());
            Physics.IgnoreCollision(controller, support, false);
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation());
            support.enabled = false; Physics.SyncTransforms();
            Assert.That(walker.Grounded, Is.False, "Support must be observed now, rather than latched from the landing Move.");
            for (int i = 0; i < 10; i++) { yield return Step(); Assert.That(walker.Grounded, Is.False, WalkingContactObservation()); }
            Assert.That(controller.transform.position.y, Is.LessThan(floor - 0.1f), WalkingContactObservation());
        }

        [UnityTest] public IEnumerator HopHitsTheLowCeilingWithoutTunnellingOrRetainedUpwardDrive()
        {
            for (int i = 0; i < 20; i++) yield return Step();
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation());
            var ceiling = GameObject.CreatePrimitive(PrimitiveType.Cube); ceiling.name = "Walking hop ceiling";
            ceiling.transform.SetParent(root.transform, false); ceiling.transform.position = controller.transform.position + Vector3.up * 2;
            ceiling.transform.localScale = new Vector3(2, 0.2f, 2); Physics.SyncTransforms();
            float floor = controller.transform.position.y, peak = floor; walker.RequestJump();
            for (int i = 0; i < 80; i++)
            {
                yield return Step(); peak = Mathf.Max(peak, controller.transform.position.y);
                if (i >= 60)
                {
                    string observation = WalkingContactObservation();
                    Assert.That(walker.Grounded, Is.True, observation);
                    Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.01f), observation);
                    Assert.That(Mathf.Abs(walker.MeasuredVelocity.y), Is.LessThan(0.05f), observation);
                }
            }
            Assert.That(peak - floor, Is.LessThan(0.25f));
            Assert.That(controller.transform.position.y, Is.EqualTo(floor).Within(0.1f));
            Assert.That(walker.Grounded, Is.True, WalkingContactObservation()); Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
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

        [UnityTest] public IEnumerator ResumingWalkingRequiresFreshMovementAfterPause()
        {
            for (int i = 0; i < 15; i++) yield return Step();
            walker.SetMovement(Vector2.right);
            for (int i = 0; i < 15; i++) yield return Step();
            host.World.Pause(host.World.Epoch);
            // Input during a paused frame cannot replace the pre-pause direction with another queued move.
            walker.SetMovement(Vector2.up); yield return Step();
            host.World.Resume(host.World.Epoch); Vector3 resumed = controller.transform.position;
            for (int i = 0; i < 15; i++) yield return Step();
            Assert.That(Vector3.ProjectOnPlane(controller.transform.position - resumed, Vector3.up).magnitude, Is.LessThan(0.03f));
            walker.SetMovement(Vector2.right);
            for (int i = 0; i < 15; i++) yield return Step();
            walker.SetMovement(Vector2.zero);
            Assert.That(controller.transform.position.x, Is.GreaterThan(resumed.x + 0.1f));
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(controller.enabled, Is.True);
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
            heavy.position = controller.transform.position + Vector3.up + Vector3.forward * 1.3f;
            heavy.transform.position = heavy.position; heavy.linearVelocity = Vector3.zero; heavy.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            var eyes = controller.transform.Find("Worker eyes");
            Assert.That(Vector3.Distance(heavy.position, heavy.transform.position), Is.LessThan(0.001f), "Heavy crate physical/query poses must agree.");
            Assert.That(Vector3.Distance(eyes.position, heavy.transform.position), Is.LessThan(3.8f), "Relocated heavy crate must be inside authored interaction reach.");
            host.Grab(Id(100)); Assert.That(host.World.GetObject(Id(100)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
            heavy.position = controller.transform.position + Vector3.up * 2.1f; heavy.transform.position = heavy.position;
            heavy.linearVelocity = Vector3.down * 4; Physics.SyncTransforms();
            for (int i = 0; i < 30; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.RecoveryEpisode, Is.Zero);
            Assert.That(host.World.GetObject(Id(100)).HolderId, Is.EqualTo(Id(1)), host.LastAction); Assert.That(controller.enabled, Is.True);
        }

        [UnityTest] public IEnumerator ExcludedImpactMotionCannotKnockDownAfterReleaseOrResume()
        {
            for (int i = 0; i < 15; i++) yield return Step();
            var heavy = HeavyCrate; var observer = controller.GetComponent<WorkerImpactContacts>();
            heavy.position = controller.transform.position + Vector3.up + Vector3.forward * 1.3f;
            heavy.transform.position = heavy.position; heavy.linearVelocity = Vector3.zero; heavy.angularVelocity = Vector3.zero; Physics.SyncTransforms();
            var eyes = controller.transform.Find("Worker eyes");
            Assert.That(Vector3.Distance(heavy.position, heavy.transform.position), Is.LessThan(0.001f), "Heavy crate physical/query poses must agree.");
            Assert.That(Vector3.Distance(eyes.position, heavy.transform.position), Is.LessThan(3.8f), "Relocated heavy crate must be inside authored interaction reach.");
            host.Grab(Id(100)); Assert.That(host.World.GetObject(Id(100)).HolderId, Is.EqualTo(Id(1)), host.LastAction);
            heavy.position = controller.transform.position + Vector3.up * 2.1f; heavy.transform.position = heavy.position;
            heavy.linearVelocity = Vector3.down * 4; Physics.SyncTransforms();
            // Sample the contact boundary without another physics step moving the held source away.
            observer.SendMessage("FixedUpdate", SendMessageOptions.RequireReceiver);
            host.DropHeld(); heavy.linearVelocity = Vector3.zero;
            observer.SendMessage("FixedUpdate", SendMessageOptions.RequireReceiver);
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.RecoveryEpisode, Is.Zero);
            host.World.Pause(host.World.Epoch); heavy.linearVelocity = Vector3.down * 4;
            observer.SendMessage("FixedUpdate", SendMessageOptions.RequireReceiver);
            heavy.linearVelocity = Vector3.zero; host.World.Resume(host.World.Epoch);
            observer.SendMessage("FixedUpdate", SendMessageOptions.RequireReceiver);
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright)); Assert.That(Worker.RecoveryEpisode, Is.Zero);
            Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
            heavy.position += Vector3.forward * 3; heavy.transform.position = heavy.position; Physics.SyncTransforms(); yield return null;
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
            Vector3 before = controller.transform.position;
            foreach (int layer in new[] { 0, 2 })
            {
                ceiling.layer = layer; Physics.SyncTransforms(); state.RequestRecovery();
                Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down), "Ceiling layer=" + layer);
                Assert.That(state.LastAction, Does.Contain("Blocked"));
                Assert.That(controller.transform.position, Is.EqualTo(before)); Assert.That(controller.enabled, Is.False);
            }
        }

        [UnityTest] public IEnumerator WalkableInclineAllowsRecoveryAndPendingSteepeningBlocksIt()
        {
            KnockDown(); for (int i = 0; i < 90; i++) yield return Step();
            Vector3 support = new Vector3(pelvis.position.x, root.transform.position.y + 3, pelvis.position.z);
            var ramp = GameObject.CreatePrimitive(PrimitiveType.Cube); ramp.name = "Recovery slope clearance fixture";
            ramp.transform.SetParent(root.transform, false); ramp.transform.localScale = new Vector3(6, 0.2f, 6);
            ramp.transform.rotation = Quaternion.Euler(30, 0, 0);
            ramp.transform.position = support - ramp.transform.up * 0.1f;
            Vector3 shift = support + Vector3.up * 0.55f - pelvis.position;
            // Hold an already settled physical pose while testing clearance, so
            // sliding/impacts do not decide this geometric recovery regression.
            var parts = rig.CopyBodySegments(); var constraints = new RigidbodyConstraints[parts.Length];
            for (int i = 0; i < parts.Length; i++)
            {
                constraints[i] = parts[i].constraints;
                parts[i].linearVelocity = Vector3.zero; parts[i].angularVelocity = Vector3.zero;
                parts[i].position += shift; parts[i].constraints = RigidbodyConstraints.FreezeAll;
            }
            Physics.SyncTransforms(); state.RequestRecovery();
            Assert.That(state.Recovering, Is.True, state.LastAction);
            ramp.transform.rotation = Quaternion.Euler(60, 0, 0); ramp.transform.position = support - ramp.transform.up * 0.1f;
            Physics.SyncTransforms();
            var blocked = host.World.CompleteWorkerRecovery(host.World.Epoch, Id(1), Worker.RecoveryAttempt);
            Assert.That(blocked.Status, Is.EqualTo(WorkerStatus.ClearanceBlocked));
            Assert.That(controller.enabled, Is.False); Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
            yield return null;
            ramp.transform.rotation = Quaternion.Euler(30, 0, 0); ramp.transform.position = support - ramp.transform.up * 0.1f;
            Physics.SyncTransforms(); state.RequestRecovery(); Assert.That(state.Recovering, Is.True, state.LastAction);
            for (int i = 0; i < 40 && Worker.Pose != WorkerPose.Upright; i++) yield return Step();
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Upright), state.LastAction);
            Assert.That(controller.enabled, Is.True); Assert.That(DynamicBodies(), Is.Zero);
            for (int i = 0; i < parts.Length; i++) parts[i].constraints = constraints[i];
        }

        [UnityTest] public IEnumerator AStationaryPelvisCannotApproveRecoveryWhileAnotherLimbIsMoving()
        {
            KnockDown(); for (int i = 0; i < 120; i++) yield return Step();
            var parts = rig.CopyBodySegments();
            foreach (var part in parts) { part.linearVelocity = Vector3.zero; part.angularVelocity = Vector3.zero; }
            parts[4].angularVelocity = Vector3.right * 4;
            Vector3 before = controller.transform.position; long revision = Worker.Revision;
            state.RequestRecovery();
            Assert.That(state.LastAction, Does.Contain("Blocked")); Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down));
            Assert.That(Worker.Revision, Is.EqualTo(revision)); Assert.That(controller.transform.position, Is.EqualTo(before));
            Assert.That(controller.enabled, Is.False); Assert.That(DynamicBodies(), Is.EqualTo(11));
            parts[4].angularVelocity = Vector3.zero; state.RequestRecovery();
            Assert.That(state.Recovering, Is.True, state.LastAction);
            parts[4].linearVelocity = Vector3.right * 2;
            var result = host.World.CompleteWorkerRecovery(host.World.Epoch, Id(1), Worker.RecoveryAttempt);
            Assert.That(result.Status, Is.EqualTo(WorkerStatus.ClearanceBlocked));
            Assert.That(Worker.Pose, Is.EqualTo(WorkerPose.Down)); Assert.That(controller.enabled, Is.False);
            Assert.That(controller.transform.position, Is.EqualTo(before)); Assert.That(DynamicBodies(), Is.EqualTo(11));
            yield return null;
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
            host.World.Pause(host.World.Epoch); state.SetDownMovement(Vector2.right); yield return Step();
            Assert.That(state.CrawlDriveActive, Is.False); Assert.That(Worker.Revision, Is.EqualTo(revision));
            host.World.Resume(host.World.Epoch);
            for (int i = 0; i < 10; i++) { yield return Step(); Assert.That(state.CrawlDriveActive, Is.False); }
            state.SetDownMovement(Vector2.right); yield return Step();
            Assert.That(state.CrawlDriveActive, Is.True, "Fresh input can reacquire crawl after resume.");
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
