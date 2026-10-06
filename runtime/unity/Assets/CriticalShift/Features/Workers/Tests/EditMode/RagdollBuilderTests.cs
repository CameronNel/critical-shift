using System;
using System.Collections.Generic;
using CriticalShift.Features.Workers.Editor;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Features.Workers.Tests
{
    public sealed class RagdollBuilderTests
    {
        private GameObject root;
        [TearDown] public void Teardown() { if (root != null) UnityEngine.Object.DestroyImmediate(root); }
        private static Transform Bone(Transform parent, string name, Vector3 local)
        { var go = new GameObject(name); go.transform.SetParent(parent, false); go.transform.localPosition = local; return go.transform; }
        [Test] public void BuilderIsRepeatablePreservesSkeletonAndCalibratesFlexAxes()
        {
            root = new GameObject("worker"); root.SetActive(false); var worker = root.AddComponent<WorkerController>(); var rig = root.AddComponent<WorkerRagdoll>();
            var visual = Bone(root.transform, "visual", Vector3.zero); var animator = visual.gameObject.AddComponent<Animator>();
            var hips = Bone(visual, "Hips", new Vector3(0, .8f, 0)); var spine = Bone(hips, "Spine", new Vector3(0, .2f, 0)); var chest = Bone(spine, "Chest", new Vector3(0, .2f, 0));
            Bone(chest, "Head", new Vector3(0, .25f, 0));
            foreach (string side in new[] { "Left", "Right" })
            {
                float sign = side == "Left" ? -1 : 1;
                var upper = Bone(chest, side + "UpperArm", new Vector3(sign * .18f, 0, 0));
                var lower = Bone(upper, side + "LowerArm", new Vector3(sign * .07f, -.2f, 0));
                Bone(lower, side + "Hand", new Vector3(sign * .04f, -.185f, .035f));
                var thigh = Bone(hips, side + "UpperLeg", new Vector3(sign * .1f, -.05f, 0));
                var shin = Bone(thigh, side + "LowerLeg", new Vector3(0, -.35f, 0)); Bone(shin, side + "Foot", new Vector3(0, -.35f, 0));
            }
            var positions = new Dictionary<Transform, Vector3>(); var rotations = new Dictionary<Transform, Quaternion>();
            foreach (var bone in visual.GetComponentsInChildren<Transform>(true)) { positions.Add(bone, bone.localPosition); rotations.Add(bone, bone.localRotation); }
            WorkerRagdollBuilder.Build(worker, animator, rig); WorkerRagdollBuilder.Build(worker, animator, rig);
            Assert.That(root.GetComponentsInChildren<Rigidbody>(true).Length, Is.EqualTo(16));
            Assert.That(root.GetComponentsInChildren<Collider>(true).Length, Is.EqualTo(17)); // 16 limbs and one capsule root.
            Assert.That(root.GetComponentsInChildren<CharacterJoint>(true).Length, Is.EqualTo(15)); Assert.That(rig.TotalMass, Is.EqualTo(70).Within(.01)); Assert.That(rig.Valid, Is.True);
            Assert.That(root.GetComponent<Rigidbody>(), Is.Null);
            foreach (var pair in positions) { Assert.That(pair.Key.localPosition, Is.EqualTo(pair.Value)); Assert.That(pair.Key.localRotation, Is.EqualTo(rotations[pair.Key])); }
            foreach (var joint in root.GetComponentsInChildren<CharacterJoint>(true))
            {
                if (joint.name.EndsWith("LowerLeg"))
                {
                    var foot = joint.transform.GetChild(0); var shin = foot.position - joint.transform.position; var kneeAxis = joint.transform.TransformDirection(joint.axis);
                    Assert.That(Mathf.Abs(Vector3.Dot(kneeAxis, shin.normalized)), Is.LessThan(.001f));
                    Assert.That(Vector3.Dot(Quaternion.AngleAxis(60, kneeAxis) * shin, Vector3.forward), Is.LessThan(Vector3.Dot(shin, Vector3.forward)));
                }
                if (!joint.name.EndsWith("LowerArm")) continue;
                var hand = joint.transform.GetChild(0); var forearm = hand.position - joint.transform.position;
                var axis = joint.transform.TransformDirection(joint.axis);
                Assert.That(Mathf.Abs(Vector3.Dot(axis, forearm.normalized)), Is.LessThan(.001f));
                Assert.That(Vector3.Dot(Quaternion.AngleAxis(60, axis) * forearm, Vector3.forward), Is.GreaterThan(Vector3.Dot(forearm, Vector3.forward)));
                Assert.That(joint.highTwistLimit.limit, Is.EqualTo(120));
            }
        }
        [Test] public void IncompleteSkeletonFailsBeforePhysicsComponentsAreAdded()
        {
            root = new GameObject("worker"); root.SetActive(false); var worker = root.AddComponent<WorkerController>(); var rig = root.AddComponent<WorkerRagdoll>();
            var visual = Bone(root.transform, "visual", Vector3.zero); var animator = visual.gameObject.AddComponent<Animator>(); Bone(visual, "Hips", Vector3.up);
            Assert.Throws<InvalidOperationException>(() => WorkerRagdollBuilder.Build(worker, animator, rig));
            Assert.That(root.GetComponentsInChildren<Rigidbody>(true), Is.Empty); Assert.That(root.GetComponentsInChildren<Joint>(true), Is.Empty);
        }
    }
}
