using System.Reflection;
using CriticalShift.FacilityPhysics.Unity;
using CriticalShift.Unity.Shared;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.FacilityPhysics.Tests
{
    public sealed class BonkPhysicsTests
    {
        private GameObject actorObject, toolObject, otherObject, wallObject, audioObject;
        private PhysicsTestWorker actor;
        private CarryableObject carry;
        private BonkShovel shovel;
        private PhysicsTestGateway gateway;
        private Rigidbody body;
        private AudioClip sound;
        private static void Set(object target, string field, object value) => target.GetType().GetField(field, BindingFlags.Instance | BindingFlags.NonPublic).SetValue(target, value);
        [SetUp] public void Setup()
        {
            actorObject = new GameObject("bonk actor"); actor = actorObject.AddComponent<PhysicsTestWorker>(); actorObject.AddComponent<BoxCollider>();
            gateway = actorObject.AddComponent<PhysicsTestGateway>(); gateway.Swing = .2f;
            toolObject = GameObject.CreatePrimitive(PrimitiveType.Cube); toolObject.transform.position = Vector3.left * .25f;
            body = toolObject.AddComponent<Rigidbody>(); body.useGravity = false;
            carry = toolObject.AddComponent<CarryableObject>(); Set(carry, "body", body); Set(carry, "gateway", gateway); Set(carry, "kind", CarryableKind.Shovel);
            shovel = toolObject.AddComponent<BonkShovel>(); Set(shovel, "carry", carry); Set(shovel, "gateway", gateway);
            audioObject = new GameObject("bonk voice"); audioObject.transform.SetParent(toolObject.transform); Set(shovel, "impactAudio", audioObject.AddComponent<AudioSource>());
            sound = AudioClip.Create("test bonk", 2400, 1, 48000, false); Set(shovel, "bonkSound", sound);
        }
        [TearDown] public void Cleanup()
        {
            shovel.EndMotion(); carry.ClearBinding();
            Object.DestroyImmediate(toolObject); Object.DestroyImmediate(actorObject); Object.DestroyImmediate(otherObject); Object.DestroyImmediate(wallObject); Object.DestroyImmediate(sound);
        }
        [Test] public void SwingOwnsToolMotionAndRestoresDynamicCarryOnCancel()
        {
            body.interpolation = RigidbodyInterpolation.Interpolate;
            Assert.That(carry.Apply(actor, SceneOperation.Grab, 1), Is.True); Assert.That(shovel.BeginMotion(actor), Is.True);
            Assert.That(body.isKinematic, Is.True); Assert.That(shovel.Animating, Is.True);
            typeof(CarryableObject).GetMethod("FixedUpdate", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(carry, null);
            Assert.That(gateway.Failures, Is.Zero); Assert.That(carry.Holder, Is.SameAs(actor));
            shovel.EndMotion(); Assert.That(body.isKinematic, Is.False); Assert.That(body.interpolation, Is.EqualTo(RigidbodyInterpolation.Interpolate)); Assert.That(shovel.Animating, Is.False);
        }
        [Test] public void ReleasingSwingingShovelCannotLeaveKinematicTool()
        {
            carry.Apply(actor, SceneOperation.Grab, 1); shovel.BeginMotion(actor); carry.ClearBinding();
            Assert.That(body.isKinematic, Is.False); Assert.That(shovel.Animating, Is.False); Assert.That(carry.Holder, Is.Null);
        }
        [Test] public void DestroyedOwnerCannotLeaveSwingToolKinematic()
        {
            carry.Apply(actor, SceneOperation.Grab, 1); shovel.BeginMotion(actor); Object.DestroyImmediate(actorObject);
            typeof(BonkShovel).GetMethod("LateUpdate", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(shovel, null);
            Assert.That(body.isKinematic, Is.False); Assert.That(shovel.Animating, Is.False);
        }
        [Test] public void DestroyedToolBodyStopsMotionWithoutDereferencingIt()
        {
            carry.Apply(actor, SceneOperation.Grab, 1); shovel.BeginMotion(actor); Object.DestroyImmediate(body);
            Assert.DoesNotThrow(() => typeof(BonkShovel).GetMethod("LateUpdate", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(shovel, null));
            Assert.That(shovel.Animating, Is.False);
        }
        [Test] public void BonkQueryFindsPlayerAndExcludesAttackerAndShovel()
        {
            otherObject = GameObject.CreatePrimitive(PrimitiveType.Cube); otherObject.transform.position = Vector3.forward * 1.1f;
            otherObject.AddComponent<PhysicsTestWorker>(); Physics.SyncTransforms();
            var query = new BonkHitQuery();
            Assert.That(query.TryContact(actor, carry, Vector3.zero, Vector3.forward * .8f, Vector3.forward * 1.4f, .16f, ~0, out var hit, out bool complete), Is.True);
            Assert.That(complete, Is.True); Assert.That(hit.Shape.gameObject, Is.SameAs(otherObject));
        }
        [Test] public void SolidWallBlocksPlayerBonkAndTriggerDoesNot()
        {
            otherObject = GameObject.CreatePrimitive(PrimitiveType.Cube); otherObject.transform.position = Vector3.forward * 1.3f;
            wallObject = GameObject.CreatePrimitive(PrimitiveType.Cube); wallObject.transform.position = Vector3.forward * .55f; wallObject.transform.localScale = new Vector3(3, 3, .1f);
            Physics.SyncTransforms(); var query = new BonkHitQuery();
            Assert.That(query.TryContact(actor, carry, Vector3.zero, Vector3.forward * .8f, Vector3.forward * 1.4f, .16f, ~0, out var blocked, out _), Is.True);
            Assert.That(blocked.Shape.gameObject, Is.SameAs(wallObject));
            wallObject.GetComponent<Collider>().isTrigger = true; Physics.SyncTransforms();
            Assert.That(query.TryContact(actor, carry, Vector3.zero, Vector3.forward * .8f, Vector3.forward * 1.4f, .16f, ~0, out var clear, out _), Is.True);
            Assert.That(clear.Shape.gameObject, Is.SameAs(otherObject));
        }
        [Test] public void EmptySwingDoesNotInventContact()
        {
            Physics.SyncTransforms(); var query = new BonkHitQuery();
            Assert.That(query.TryContact(actor, carry, Vector3.zero, Vector3.forward * .8f, Vector3.forward * 1.4f, .16f, ~0, out _, out bool complete), Is.False);
            Assert.That(complete, Is.True);
        }
        [Test] public void StartedInsideWallBlocksRatherThanHittingThroughIt()
        {
            wallObject = GameObject.CreatePrimitive(PrimitiveType.Cube); wallObject.transform.position = Vector3.zero;
            Physics.SyncTransforms(); var query = new BonkHitQuery();
            Assert.That(query.TryContact(actor, carry, Vector3.zero, Vector3.forward * .8f, Vector3.forward * 1.4f, .16f, ~0, out var hit, out bool complete), Is.True);
            Assert.That(complete, Is.True); Assert.That(hit.Shape.gameObject, Is.SameAs(wallObject));
        }
    }
}
