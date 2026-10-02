using System;
using System.Collections;
using System.Reflection;
using CriticalShift.FacilityPhysics.Unity;
using CriticalShift.Unity.Shared;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.FacilityPhysics.Tests
{
    public sealed class PhysicsTestWorker : WorkerScenePort
    {
        public SceneOperation? Pose;
        public override Transform Eye => transform;
        public override Transform Grip => transform;
        public override Collider[] BodyColliders => GetComponents<Collider>();
        public override bool Grounded => true;
        public override bool RecoveryClear => true;
        public override bool Down => false;
        public override Vector3 Velocity => Vector3.zero;
        public override void SetHaulPose(SceneOperation? operation) { Pose = operation; }
        public override void PresentStation(SceneOperation operation, Transform anchor) { }
        public override void CancelSceneActions() { }
    }
    public sealed class PhysicsTestGateway : SceneInteractionGateway
    {
        public int Failures, AssistantFailures;
        public override bool Running => true;
        public override bool CanAct(WorkerScenePort worker) => true;
        public override SceneTarget Held(WorkerScenePort worker) => null;
        public override bool CanUse(WorkerScenePort worker, SceneTarget target) => true;
        public override string Describe(SceneTarget target) => "";
        public override void RotateHeld(WorkerScenePort worker, float degrees) { }
        public override bool Execute(WorkerScenePort worker, SceneTarget target, SceneOperation operation, out string reason) { reason = ""; return true; }
        public override bool RecoveryReady(WorkerScenePort worker) => false;
        public override long BeginRecovery(WorkerScenePort worker) => 0;
        public override bool CompleteRecovery(WorkerScenePort worker, long attempt) => false;
        public override void Impact(WorkerScenePort worker, Guid hazard, bool incapacitating, float delaySeconds) { }
        public override void AttachmentFailed(SceneTarget target, long generation, WorkerScenePort assistant = null)
        {
            if (assistant != null) { AssistantFailures++; ((CarryableObject)target).SynchronizeAssistant(null); }
            else { Failures++; target.ClearBinding(); }
        }
    }
    public sealed class CarryPhysicsTests
    {
        private GameObject workerObject, cargoObject, gatewayObject, helperObject, targetObject, wallObject;
        private PhysicsTestWorker worker;
        private CarryableObject item;
        private PhysicsTestGateway gateway;
        private Rigidbody body;
        private static void Set(object target, string field, object value) =>
            target.GetType().GetField(field, BindingFlags.Instance | BindingFlags.NonPublic).SetValue(target, value);
        [SetUp]
        public void Setup()
        {
            workerObject = new GameObject("Physics test worker"); worker = workerObject.AddComponent<PhysicsTestWorker>();
            workerObject.transform.position = Vector3.left * 2;
            workerObject.AddComponent<BoxCollider>();
            gatewayObject = new GameObject("Physics test gateway"); gateway = gatewayObject.AddComponent<PhysicsTestGateway>();
            cargoObject = GameObject.CreatePrimitive(PrimitiveType.Cube); body = cargoObject.AddComponent<Rigidbody>(); body.useGravity = false;
            item = cargoObject.AddComponent<CarryableObject>(); Set(item, "body", body); Set(item, "gateway", gateway);
        }
        [TearDown]
        public void Cleanup()
        {
            if (item != null) item.ClearBinding();
            UnityEngine.Object.DestroyImmediate(cargoObject); UnityEngine.Object.DestroyImmediate(workerObject); UnityEngine.Object.DestroyImmediate(gatewayObject);
            UnityEngine.Object.DestroyImmediate(helperObject); UnityEngine.Object.DestroyImmediate(targetObject); UnityEngine.Object.DestroyImmediate(wallObject);
        }
        [Test]
        public void StalePhysicsReleaseCannotDetachTheCurrentHolder()
        {
            Assert.That(item.Apply(worker, SceneOperation.Grab, 4), Is.True);
            Assert.That(item.Apply(worker, SceneOperation.Release, 3), Is.False);
            Assert.That(item.Holder, Is.SameAs(worker));
            Assert.That(item.Apply(worker, SceneOperation.Release, 4), Is.True);
            Assert.That(item.Holder, Is.Null);
        }
        [Test]
        public void DetachRestoresWorkerObjectCollisions()
        {
            var cargo = cargoObject.GetComponent<Collider>(); var actor = workerObject.GetComponent<Collider>();
            item.Apply(worker, SceneOperation.Grab, 1); Assert.That(Physics.GetIgnoreCollision(cargo, actor), Is.True);
            item.ClearBinding(); Assert.That(Physics.GetIgnoreCollision(cargo, actor), Is.False);
        }
        [UnityTest]
        public IEnumerator ObstructionBreaksTheAttachmentInsteadOfTeleportingCargo()
        {
            workerObject.transform.position = Vector3.right * 3;
            item.Apply(worker, SceneOperation.Grab, 1);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(gateway.Failures, Is.EqualTo(1)); Assert.That(item.Holder, Is.Null);
            Assert.That(body.position.x, Is.LessThan(0.1f));
        }
        [UnityTest]
        public IEnumerator UnderhandReleaseUsesTheAuthoredThrowVelocity()
        {
            item.Apply(worker, SceneOperation.Grab, 1); item.Apply(worker, SceneOperation.ThrowUnder, 1);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.z, Is.EqualTo(2.6f).Within(0.05f)); Assert.That(body.linearVelocity.y, Is.EqualTo(3.2f).Within(0.05f));
        }
        private PhysicsTestWorker AddHelper()
        {
            helperObject = new GameObject("Carry helper"); var helper = helperObject.AddComponent<PhysicsTestWorker>(); helperObject.AddComponent<BoxCollider>();
            Set(item, "allowAssistance", true); return helper;
        }
        [UnityTest]
        public IEnumerator HelperGripFailurePreservesPrimaryAndRestoresOnlyHelperCollisions()
        {
            workerObject.transform.position = Vector3.zero;
            var helper = AddHelper(); helperObject.transform.position = Vector3.right * 3;
            item.Apply(worker, SceneOperation.Grab, 4); item.Apply(helper, SceneOperation.Grab, 4);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(gateway.AssistantFailures, Is.EqualTo(1)); Assert.That(gateway.Failures, Is.Zero);
            Assert.That(item.Holder, Is.SameAs(worker)); Assert.That(item.Assistant, Is.Null); Assert.That(item.Generation, Is.EqualTo(4));
            var cargo = cargoObject.GetComponent<Collider>();
            Assert.That(Physics.GetIgnoreCollision(cargo, workerObject.GetComponent<Collider>()), Is.True);
            Assert.That(Physics.GetIgnoreCollision(cargo, helperObject.GetComponent<Collider>()), Is.False);
        }
        [Test]
        public void CartGripModeChangesPreserveTheLeaseAndRejectStaleModes()
        {
            Set(item, "kind", CarryableKind.Cart); item.Apply(worker, SceneOperation.Push, 4);
            Assert.That(item.Apply(worker, SceneOperation.Pull, 3), Is.False); Assert.That(worker.Pose, Is.EqualTo(SceneOperation.Push));
            Assert.That(item.Apply(worker, SceneOperation.Pull, 4), Is.True); Assert.That(worker.Pose, Is.EqualTo(SceneOperation.Pull));
            Assert.That(item.Holder, Is.SameAs(worker)); Assert.That(item.Generation, Is.EqualTo(4));
        }
        [Test]
        public void ReapplyingPrimaryGripDoesNotDetachTheAcceptedHelper()
        {
            var helper = AddHelper(); item.Apply(worker, SceneOperation.Grab, 4); item.Apply(helper, SceneOperation.Grab, 4);
            Assert.That(item.Apply(worker, SceneOperation.Grab, 4), Is.True);
            Assert.That(item.Assistant, Is.SameAs(helper)); Assert.That(item.Generation, Is.EqualTo(4));
        }
        private CarryableObject RayFixture()
        {
            workerObject.transform.position = Vector3.zero;
            var own = workerObject.GetComponent<BoxCollider>(); own.center = Vector3.forward * 0.3f; own.size = Vector3.one * 0.2f;
            cargoObject.transform.position = Vector3.forward * 0.8f; cargoObject.transform.localScale = Vector3.one * 0.2f;
            targetObject = GameObject.CreatePrimitive(PrimitiveType.Cube); targetObject.transform.position = Vector3.forward * 1.6f;
            targetObject.transform.localScale = Vector3.one * 0.2f;
            var target = targetObject.AddComponent<CarryableObject>(); Physics.SyncTransforms(); return target;
        }
        [Test]
        public void InteractionRayAndReachIgnoreOwnShapeAndCarriedCargo()
        {
            var target = RayFixture(); var hits = new RaycastHit[64];
            Assert.That(SceneTargeting.Raycast(worker, item, Vector3.forward, 2.5f, ~0, hits, out var hit), Is.True);
            Assert.That(hit.collider.GetComponentInParent<SceneTarget>(), Is.SameAs(target));
            Assert.That(SceneTargeting.CanReach(worker, item, target, ~0, hits), Is.True);
        }
        [Test]
        public void SolidWallBlocksInteractionRayAndReachBehindCarriedCargo()
        {
            var target = RayFixture(); wallObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wallObject.transform.position = Vector3.forward * 1.2f; wallObject.transform.localScale = Vector3.one * 0.1f; Physics.SyncTransforms();
            var hits = new RaycastHit[64];
            Assert.That(SceneTargeting.Raycast(worker, item, Vector3.forward, 2.5f, ~0, hits, out var hit), Is.True);
            Assert.That(hit.collider, Is.SameAs(wallObject.GetComponent<Collider>()));
            Assert.That(SceneTargeting.CanReach(worker, item, target, ~0, hits), Is.False);
        }
        [Test]
        public void SaturatedInteractionQueryCannotEstablishATargetOrClearReach()
        {
            var target = RayFixture(); var hits = new RaycastHit[1];
            Assert.That(SceneTargeting.Raycast(worker, item, Vector3.forward, 2.5f, ~0, hits, out _), Is.False);
            Assert.That(SceneTargeting.CanReach(worker, item, target, ~0, hits), Is.False);
        }
    }
}
