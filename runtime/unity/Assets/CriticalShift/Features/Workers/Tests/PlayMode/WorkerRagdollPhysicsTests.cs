using System;
using System.Collections.Generic;
using System.Reflection;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Unity.Shared;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Features.Workers.Tests
{
    public sealed class WorkerRagdollPhysicsTests
    {
        private readonly List<GameObject> objects = new List<GameObject>();
        private GameObject root;
        private WorkerRagdoll rig;
        private Rigidbody pelvis, limb;
        private SphereCollider pelvisShape, limbShape;
        private RagdollTuning tuning;
        private static void Set(object target, string field, object value) => target.GetType().GetField(field, BindingFlags.Instance | BindingFlags.NonPublic).SetValue(target, value);
        private GameObject Object(string name) { var go = new GameObject(name); objects.Add(go); return go; }
        [SetUp] public void Setup()
        {
            root = Object("worker fixture"); root.SetActive(false);
            var hips = Object("pelvis"); hips.transform.SetParent(root.transform); hips.transform.localPosition = new Vector3(0, .8f, 0);
            pelvis = hips.AddComponent<Rigidbody>(); pelvis.mass = 40; pelvis.isKinematic = true;
            pelvisShape = hips.AddComponent<SphereCollider>(); pelvisShape.radius = .1f;
            var child = Object("limb"); child.transform.SetParent(hips.transform); child.transform.localPosition = new Vector3(0, .3f, 0);
            limb = child.AddComponent<Rigidbody>(); limb.mass = 30; limb.isKinematic = true;
            limbShape = child.AddComponent<SphereCollider>(); limbShape.radius = .1f;
            var joint = child.AddComponent<CharacterJoint>(); joint.connectedBody = pelvis; joint.axis = Vector3.right; joint.swingAxis = Vector3.forward;
            joint.lowTwistLimit = new SoftJointLimit { limit = -20 }; joint.highTwistLimit = new SoftJointLimit { limit = 20 };
            joint.swing1Limit = joint.swing2Limit = new SoftJointLimit { limit = 30 };
            rig = root.AddComponent<WorkerRagdoll>(); tuning = new RagdollTuning { settleSeconds = 0, linearDamping = 0, angularDamping = 0 };
            Set(rig, "pelvis", pelvis); Set(rig, "bones", new[] { limb, pelvis }); Set(rig, "colliders", new Collider[] { limbShape, pelvisShape }); Set(rig, "tuning", tuning);
            root.SetActive(true);
        }
        [TearDown] public void Teardown()
        { foreach (var go in objects) if (go != null) UnityEngine.Object.DestroyImmediate(go); objects.Clear(); }
        [Test] public void AnimatedVelocityHandoffDoesNotDoubleCountRootMotion()
        {
            rig.SampleAnimatedPose(.1f); root.transform.position += Vector3.right * .1f; limb.transform.position += Vector3.forward * .02f;
            limb.transform.rotation = Quaternion.AngleAxis(5, Vector3.right); rig.SampleAnimatedPose(.1f);
            rig.Activate(Vector3.right * 2, Vector3.zero, pelvis.position);
            Assert.That(Vector3.Distance(pelvis.linearVelocity, Vector3.right * 2), Is.LessThan(.001f));
            Assert.That(Vector3.Distance(limb.linearVelocity, new Vector3(2, 0, .2f)), Is.LessThan(.001f));
            Assert.That(limb.angularVelocity.x, Is.EqualTo(50 * Mathf.Deg2Rad).Within(.001f));
        }
        [Test] public void RepeatedActivationPreservesExistingMotion()
        {
            rig.Activate(Vector3.zero); pelvis.linearVelocity = Vector3.right; limb.angularVelocity = Vector3.up;
            rig.Activate(Vector3.up * 9, Vector3.zero, pelvis.position);
            Assert.That(pelvis.linearVelocity, Is.EqualTo(Vector3.right)); Assert.That(limb.angularVelocity, Is.EqualTo(Vector3.up));
        }
        [Test] public void OversizedImpactUsesAggregateMassBudget()
        {
            var previous = Physics.simulationMode;
            try
            {
                Physics.simulationMode = SimulationMode.Script; rig.Activate(Vector3.zero); pelvis.useGravity = limb.useGravity = false;
                rig.ApplyImpulse(Vector3.right * 100000, pelvis.worldCenterOfMass); Physics.Simulate(.02f);
                Vector3 momentum = pelvis.linearVelocity * pelvis.mass + limb.linearVelocity * limb.mass;
                Assert.That(momentum.x, Is.EqualTo(70 * tuning.maximumImpactSpeed).Within(1));
                Assert.That(Mathf.Abs(momentum.y) + Mathf.Abs(momentum.z), Is.LessThan(1));
            }
            finally { Physics.simulationMode = previous; }
        }
        [Test] public void RootRepositionPreservesChildWorldPosesInReversedArray()
        {
            rig.Activate(Vector3.zero); Vector3 hips = pelvis.position, child = limb.position; Quaternion rotation = limb.rotation;
            rig.MoveRootPreservingPose(new RagdollRecoveryPose(new Vector3(4, 0, 3), Quaternion.Euler(0, 110, 0), false));
            Assert.That(Vector3.Distance(pelvis.position, hips), Is.LessThan(.0001f)); Assert.That(Vector3.Distance(limb.position, child), Is.LessThan(.0001f));
            Assert.That(Quaternion.Angle(limb.rotation, rotation), Is.LessThan(.001f));
        }
        [Test] public void RecoveryRequiresFloorAtCurrentPelvisInsteadOfOldRoot()
        {
            rig.Activate(Vector3.zero); pelvis.position = new Vector3(5, .8f, 0); Physics.SyncTransforms();
            Assert.That(rig.TryRecoveryPose(~0, 50, out _), Is.False);
            var floor = Object("floor"); floor.transform.position = new Vector3(5, -.1f, 0); var shape = floor.AddComponent<BoxCollider>(); shape.size = new Vector3(2, .2f, 2); Physics.SyncTransforms();
            Assert.That(rig.TryRecoveryPose(~0, 50, out var pose), Is.True); Assert.That(pose.Position.x, Is.EqualTo(5).Within(.001f));
            Assert.That(pose.Position.y, Is.EqualTo(.02f).Within(.001f));
        }
        [Test] public void RecoveryRejectsMovingSupport()
        {
            var floor = Object("moving floor"); floor.transform.position = new Vector3(0, -.1f, 0); var shape = floor.AddComponent<BoxCollider>(); shape.size = new Vector3(2, .2f, 2);
            var body = floor.AddComponent<Rigidbody>(); body.useGravity = false; body.linearVelocity = Vector3.right * 3;
            rig.Activate(Vector3.zero); Physics.SyncTransforms(); Assert.That(rig.TryRecoveryPose(~0, 50, out _), Is.False);
        }
        [Test] public void StandingClearanceRejectsLowCeiling()
        {
            var controller = root.AddComponent<WorkerController>(); controller.enabled = false;
            var capsule = root.GetComponent<CharacterController>(); capsule.radius = .25f; capsule.skinWidth = .03f;
            Set(controller, "capsule", capsule); Set(controller, "ragdoll", rig);
            var floor = Object("floor"); floor.transform.position = new Vector3(0, -.1f, 0); var floorShape = floor.AddComponent<BoxCollider>(); floorShape.size = new Vector3(3, .2f, 3);
            var ceiling = Object("ceiling"); ceiling.transform.position = Vector3.up; var roof = ceiling.AddComponent<BoxCollider>(); roof.size = new Vector3(3, .2f, 3);
            Physics.SyncTransforms(); Assert.That(controller.CanStandAt(Vector3.zero), Is.False);
            UnityEngine.Object.DestroyImmediate(ceiling); Physics.SyncTransforms(); Assert.That(controller.CanStandAt(Vector3.zero), Is.True);
        }
        [TestCase(90, true)] [TestCase(-90, false)] public void RecoverySelectsFrontOrBackUsingAnatomicalAxes(float roll, bool front)
        {
            var floor = Object("floor"); floor.transform.position = new Vector3(0, -.1f, 0); var shape = floor.AddComponent<BoxCollider>(); shape.size = new Vector3(3, .2f, 3);
            rig.Activate(Vector3.zero); pelvis.rotation = Quaternion.Euler(roll, 0, 0); Physics.SyncTransforms();
            Assert.That(rig.TryRecoveryPose(~0, 50, out var pose), Is.True); Assert.That(pose.FaceDown, Is.EqualTo(front));
            Assert.That(Vector3.Dot(pose.Rotation * Vector3.forward, Vector3.forward), Is.GreaterThan(.99f));
        }
        [Test] public void MissingBodyLatchesFaultAndCannotRestart()
        {
            rig.Activate(Vector3.zero); UnityEngine.Object.DestroyImmediate(limb.gameObject);
            LogAssert.Expect(LogType.Error, "Ragdoll physics stopped: An owned ragdoll shape was removed or disabled.");
            typeof(WorkerRagdoll).GetMethod("FixedUpdate", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(rig, null);
            Assert.That(rig.Faulted, Is.True); Assert.That(pelvis.isKinematic, Is.True); Assert.That(pelvisShape.enabled, Is.False);
            Assert.Throws<InvalidOperationException>(() => rig.Activate(Vector3.zero));
        }
        [Test] public void InactiveLimbCannotActivate()
        { limb.gameObject.SetActive(false); Assert.Throws<InvalidOperationException>(() => rig.Activate(Vector3.zero)); Assert.That(rig.Active, Is.False); }
        [Test] public void DisabledPhysicsOwnerCannotRestart()
        { rig.Activate(Vector3.zero); rig.enabled = false; Assert.Throws<InvalidOperationException>(() => rig.Activate(Vector3.zero)); Assert.That(pelvis.isKinematic, Is.True); }
        [Test] public void ActiveCollisionScopesRestoreBothOriginalPolicies()
        {
            rig.Activate(Vector3.zero); var scope = new CollisionIgnoreScope();
            foreach (bool baseline in new[] { false, true })
            {
                Physics.IgnoreCollision(pelvisShape, limbShape, baseline);
                for (int cycle = 0; cycle < 3; cycle++)
                { scope.Capture(new Collider[] { pelvisShape }, new Collider[] { limbShape }); Assert.That(Physics.GetIgnoreCollision(pelvisShape, limbShape), Is.True); scope.Restore(); Assert.That(Physics.GetIgnoreCollision(pelvisShape, limbShape), Is.EqualTo(baseline)); }
            }
            for (int cycle = 0; cycle < 3; cycle++)
            { rig.Freeze(); rig.Activate(Vector3.zero); Assert.That(Physics.GetIgnoreCollision(pelvisShape, limbShape), Is.True); }
            rig.Stop(); Assert.That(pelvis.isKinematic && limb.isKinematic, Is.True); Assert.That(pelvisShape.enabled || limbShape.enabled, Is.False);
        }
        [TestCase("pelvisJoint")] [TestCase("foreignJoint")] [TestCase("missingJoint")] [TestCase("duplicateBody")]
        [TestCase("rootShape")] [TestCase("undeclaredBody")] [TestCase("undeclaredShape")] [TestCase("mesh")] [TestCase("mass")] [TestCase("scale")]
        public void MalformedRigIsRejectedBeforeSimulation(string defect)
        {
            if (defect == "rootShape") root.AddComponent<BoxCollider>();
            if (defect == "pelvisJoint") pelvis.gameObject.AddComponent<FixedJoint>();
            if (defect == "foreignJoint") limb.GetComponent<CharacterJoint>().connectedBody = Object("foreign").AddComponent<Rigidbody>();
            if (defect == "missingJoint") UnityEngine.Object.DestroyImmediate(limb.GetComponent<CharacterJoint>());
            if (defect == "duplicateBody") Set(rig, "bones", new[] { pelvis, pelvis });
            if (defect == "undeclaredBody") { var extra = Object("extra"); extra.transform.SetParent(root.transform); extra.AddComponent<Rigidbody>(); }
            if (defect == "undeclaredShape") limb.gameObject.AddComponent<BoxCollider>();
            if (defect == "mesh") Set(rig, "colliders", new Collider[] { pelvisShape, limb.gameObject.AddComponent<MeshCollider>() });
            if (defect == "mass") limb.mass = 200;
            if (defect == "scale") root.transform.localScale = Vector3.one * 2;
            Assert.That(rig.TryValidate(out var reason), Is.False); Assert.That(reason, Is.Not.Empty); Assert.That(rig.Active, Is.False);
        }
    }
}
