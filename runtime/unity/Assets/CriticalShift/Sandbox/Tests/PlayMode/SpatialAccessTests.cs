using System;
using System.Collections;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class SpatialAccessTests
    {
        private GameObject root, target;
        private Transform eyes;
        private SpatialInteractionAccess policy;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);

        [SetUp] public void SetUp()
        {
            root = new GameObject("Spatial access fixture"); root.transform.position = new Vector3(1200, 1200, 1200);
            eyes = new GameObject("Actor observation origin").transform; eyes.SetParent(root.transform, false);
            target = GameObject.CreatePrimitive(PrimitiveType.Cube); target.transform.SetParent(root.transform, false);
            target.transform.localPosition = new Vector3(0, 0, 2.5f); target.transform.localScale = Vector3.one * 0.5f;
            policy = new SpatialInteractionAccess(3.5f); policy.BindActor(Id(1), eyes); policy.BindTarget(Id(2), target.transform);
            Physics.SyncTransforms();
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            policy.Clear(); if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        [Test] public void CurrentTargetColliderDoesNotBlockItsOwnInteraction()
        {
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Grab), Is.EqualTo(AccessDecision.Allowed));
        }

        [Test] public void SolidOccluderAndExcessiveReachRejectInteraction()
        {
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube); wall.transform.SetParent(root.transform, false);
            wall.transform.localPosition = new Vector3(0, 0, 1); Physics.SyncTransforms();
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Grab), Is.EqualTo(AccessDecision.OutOfReach));
            wall.SetActive(false); target.transform.localPosition = new Vector3(0, 0, 5); Physics.SyncTransforms();
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Grab), Is.EqualTo(AccessDecision.OutOfReach));
        }

        [Test] public void OnlyExplicitlyApprovedOwnedBodyIsTransparentForSight()
        {
            var carried = GameObject.CreatePrimitive(PrimitiveType.Cube); carried.transform.SetParent(root.transform, false);
            carried.transform.localPosition = new Vector3(0, 0, 1); var body = carried.AddComponent<Rigidbody>(); body.isKinematic = true;
            Physics.SyncTransforms();
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Production), Is.EqualTo(AccessDecision.OutOfReach));
            policy.Clear(); policy = new SpatialInteractionAccess(3.5f, (actor, targetId, candidate) => actor == Id(1) && targetId == Id(2) && candidate == body);
            policy.BindActor(Id(1), eyes); policy.BindTarget(Id(2), target.transform);
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Production), Is.EqualTo(AccessDecision.Allowed));
        }

        [Test] public void MissingOrDisabledBindingsCannotGrantAccess()
        {
            Assert.That(policy.Evaluate(Id(9), Id(2), InteractionKind.Grab), Is.EqualTo(AccessDecision.ActorUnavailable));
            Assert.That(policy.Evaluate(Id(1), Id(9), InteractionKind.Grab), Is.EqualTo(AccessDecision.TargetUnavailable));
            target.SetActive(false);
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Grab), Is.EqualTo(AccessDecision.TargetUnavailable));
        }

        [Test] public void FocusPicksTheCurrentRegisteredRayTarget()
        {
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Id(2)));
            target.transform.localPosition = new Vector3(2, 0, 2.5f); Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Guid.Empty));
        }

        [Test] public void DetachedInteractionPointCannotAuthorizeOrFocusItsFormerEquipment()
        {
            var point = new GameObject("Explicit equipment control").transform;
            point.SetParent(target.transform, false);
            policy.Clear(); policy.BindActor(Id(1), eyes); policy.BindTarget(Id(2), target.transform, point);
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Production), Is.EqualTo(AccessDecision.Allowed));
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Id(2)));

            // Reparenting a control near the actor must not shorten reach to its old equipment.
            point.SetParent(root.transform, false); point.localPosition = Vector3.forward * 0.25f;
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Production), Is.EqualTo(AccessDecision.TargetUnavailable));
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Guid.Empty));

            point.SetParent(target.transform, false); point.localPosition = Vector3.zero;
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Production), Is.EqualTo(AccessDecision.Allowed));
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Id(2)));
        }

        [Test] public void UnregisteredWallBlocksFocusBehindIt()
        {
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube); wall.transform.SetParent(root.transform, false);
            wall.transform.localPosition = new Vector3(0, 0, 1); Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Guid.Empty));
        }

        [Test] public void FocusCanLookPastAnExplicitlyApprovedHeldBody()
        {
            var carried = GameObject.CreatePrimitive(PrimitiveType.Cube); carried.transform.SetParent(root.transform, false);
            carried.transform.localPosition = new Vector3(0, 0, 1); var body = carried.AddComponent<Rigidbody>(); body.isKinematic = true;
            policy.Clear(); policy = new SpatialInteractionAccess(3.5f, (actor, targetId, candidate) => actor == Id(1) && candidate == body);
            policy.BindActor(Id(1), eyes); policy.BindTarget(Id(2), target.transform); Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Id(2)));
        }

        [Test] public void RegisteredOpenDoorThresholdsRemainFocusableWithoutMakingUnknownTriggersOcclude()
        {
            target.GetComponent<Collider>().isTrigger = true; Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Guid.Empty));
            policy.Clear(); policy = new SpatialInteractionAccess(3.5f, includeRegisteredTriggersInFocus: true);
            policy.BindActor(Id(1), eyes); policy.BindTarget(Id(2), target.transform);
            var unrelated = GameObject.CreatePrimitive(PrimitiveType.Cube); unrelated.transform.SetParent(root.transform, false);
            unrelated.transform.localPosition = Vector3.forward; unrelated.GetComponent<Collider>().isTrigger = true; Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Id(2)));
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Door), Is.EqualTo(AccessDecision.Allowed));
            unrelated.GetComponent<Collider>().isTrigger = false; Physics.SyncTransforms();
            Assert.That(policy.PickTarget(Id(1)), Is.EqualTo(Guid.Empty));
            Assert.That(policy.Evaluate(Id(1), Id(2), InteractionKind.Door), Is.EqualTo(AccessDecision.OutOfReach));
        }
    }
}
