using System.Collections;
using CriticalShift.FacilityPhysics;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class FacilityPhysicsTests
    {
        private GameObject root;
        [SetUp] public void SetUp()
        {
            root = new GameObject("Facility physics regression fixture");
            root.transform.position = new Vector3(1000, 1000, 1000);
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (root != null) Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        private Rigidbody Body(string name, Vector3 position)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube); item.name = name;
            item.transform.SetParent(root.transform, false); item.transform.localPosition = position;
            var body = item.AddComponent<Rigidbody>(); body.useGravity = false; return body;
        }

        private ConveyorDrive Belt(System.Func<Rigidbody, bool> filter)
        {
            var item = new GameObject("Belt observation bounds"); item.transform.SetParent(root.transform, false);
            var box = item.AddComponent<BoxCollider>(); box.isTrigger = true; box.size = Vector3.one * 10;
            var belt = item.AddComponent<ConveyorDrive>(); belt.Initialize(filter, () => true);
            Physics.SyncTransforms(); return belt;
        }

        [UnityTest] public IEnumerator CartDriveRemainsWithinItsSpeedBudget()
        {
            var body = Body("Cart", Vector3.zero); body.mass = 35;
            var motor = body.gameObject.AddComponent<CartMotor>(); motor.Initialize(() => true, () => 20);
            motor.SetDrive(1, 0, false);
            for (int i = 0; i < 100; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.Speed, Is.GreaterThan(1));
            Assert.That(motor.Speed, Is.LessThanOrEqualTo(motor.MaximumSpeed + 0.05f));
            Assert.That(Mathf.Abs(body.linearVelocity.y), Is.LessThan(0.001f));
        }

        [UnityTest] public IEnumerator CartBrakeReducesPlanarSpeedWithoutVerticalImpulse()
        {
            var body = Body("Braking cart", Vector3.zero); body.linearVelocity = new Vector3(0, 2, 3);
            var motor = body.gameObject.AddComponent<CartMotor>(); motor.Initialize(() => true, () => 0);
            motor.SetDrive(0, 0, true);
            for (int i = 0; i < 40; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.Speed, Is.LessThan(0.3f));
            Assert.That(body.linearVelocity.y, Is.EqualTo(2).Within(0.01f));
        }

        [UnityTest] public IEnumerator ConveyorCannotAccelerateAnUnauthorizedBody()
        {
            var body = Body("Unregistered body", Vector3.zero); var belt = Belt(candidate => false);
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
            Assert.That(belt.MovingBodyCount, Is.Zero);
        }

        [UnityTest] public IEnumerator CompoundColliderBodyReceivesOneBeltDrive()
        {
            var body = Body("Compound portable body", Vector3.zero);
            body.gameObject.AddComponent<BoxCollider>();
            var belt = Belt(candidate => candidate == body);
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            Assert.That(belt.MovingBodyCount, Is.EqualTo(1));
            Assert.That(body.linearVelocity.z, Is.GreaterThan(0.1f));
            Assert.That(body.linearVelocity.z, Is.LessThanOrEqualTo(belt.BeltSpeed + 0.05f));
        }

        [UnityTest] public IEnumerator CargoSensorCountsCompoundBodyOnceAndPrunesDisabledCargo()
        {
            var item = new GameObject("Cart sensor owner"); item.transform.SetParent(root.transform, false);
            var cart = item.AddComponent<Rigidbody>(); cart.isKinematic = true;
            var box = item.AddComponent<BoxCollider>(); box.isTrigger = true; box.size = Vector3.one * 5;
            var sensor = item.AddComponent<CartCargoSensor>(); sensor.Initialize(cart, candidate => true);
            var cargo = Body("Compound cargo", Vector3.zero); cargo.mass = 7; cargo.gameObject.AddComponent<BoxCollider>();
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.EqualTo(1)); Assert.That(sensor.Mass, Is.EqualTo(7).Within(0.01f));
            cargo.gameObject.SetActive(false);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.Zero); Assert.That(sensor.Mass, Is.Zero);
        }
    }
}
