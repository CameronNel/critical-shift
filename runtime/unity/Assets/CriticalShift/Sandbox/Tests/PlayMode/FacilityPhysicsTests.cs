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
        private PhysicsSafetyMonitor safety;
        [SetUp] public void SetUp()
        {
            root = new GameObject("Facility physics regression fixture");
            root.transform.position = new Vector3(1000, 1000, 1000);
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (safety != null) safety.Shutdown();
            if (root != null) Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        private Rigidbody Body(string name, Vector3 position)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube); item.name = name;
            item.transform.SetParent(root.transform, false); item.transform.localPosition = position;
            var body = item.AddComponent<Rigidbody>(); body.useGravity = false; return body;
        }

        [Test] public void PhysicsMonitorObservesDynamicHandoffsWithoutWritingMotion()
        {
            var body = Body("Observed body", Vector3.zero); body.linearVelocity = Vector3.right * 2;
            Vector3 position = body.position, velocity = body.linearVelocity; int failures = 0;
            safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 10), 10, 10, () => true, error => failures++);
            safety.Bind(body, "Observed body"); safety.Activate(); safety.Sample();
            Assert.That(safety.DynamicBodyCount, Is.EqualTo(1)); Assert.That(safety.PeakLinearSpeed, Is.EqualTo(2).Within(0.001f));
            Assert.That(body.position, Is.EqualTo(position)); Assert.That(body.linearVelocity, Is.EqualTo(velocity));
            body.isKinematic = true; safety.Sample();
            Assert.That(safety.DynamicBodyCount, Is.Zero); Assert.That(safety.PeakDynamicBodyCount, Is.EqualTo(1));
            Assert.That(safety.BoundBodyCount, Is.EqualTo(1)); Assert.That(failures, Is.Zero);
        }

        [Test] public void PhysicsMonitorLatchesOneRunawayFailureAndLeavesMotionToItsOwner()
        {
            var body = Body("Runaway body", Vector3.zero); body.linearVelocity = Vector3.forward * 11;
            int failures = 0; string reason = "";
            safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 10), 10, 10, () => true,
                error => { failures++; reason = error.Message; });
            safety.Bind(body, "Runaway body"); safety.Activate(); safety.Sample();
            Assert.That(safety.FaultLatched, Is.True); Assert.That(failures, Is.EqualTo(1));
            Assert.That(reason, Does.Contain("Runaway body")); Assert.That(body.linearVelocity.z, Is.EqualTo(11));
            body.linearVelocity = Vector3.zero; safety.Sample(); safety.Sample();
            Assert.That(failures, Is.EqualTo(1)); safety.Shutdown(); Assert.That(safety.BoundBodyCount, Is.Zero);
        }

        private ConveyorDrive Belt(System.Func<Rigidbody, bool> filter)
        {
            var item = new GameObject("Belt observation bounds"); item.transform.SetParent(root.transform, false);
            var box = item.AddComponent<BoxCollider>(); box.isTrigger = true; box.size = Vector3.one * 10;
            var belt = item.AddComponent<ConveyorDrive>(); belt.Initialize(filter, () => true);
            Physics.SyncTransforms(); return belt;
        }

        private CartCargoSensor Cargo(System.Func<Rigidbody, Rigidbody> grouping, System.Func<Rigidbody, float> mass, int capacity = 32)
        {
            var item = new GameObject("Cart sensor owner"); item.transform.SetParent(root.transform, false);
            var cart = item.AddComponent<Rigidbody>(); cart.isKinematic = true;
            var box = item.AddComponent<BoxCollider>(); box.isTrigger = true; box.size = Vector3.one * 5;
            var sensor = item.AddComponent<CartCargoSensor>(); sensor.MaximumBodies = capacity; sensor.Initialize(cart, grouping, mass);
            Physics.SyncTransforms(); return sensor;
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
            var sensor = Cargo(candidate => candidate, group => group.mass);
            var cargo = Body("Compound cargo", Vector3.zero); cargo.mass = 7; cargo.gameObject.AddComponent<BoxCollider>();
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.EqualTo(1)); Assert.That(sensor.Mass, Is.EqualTo(7).Within(0.01f));
            cargo.gameObject.SetActive(false);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.Zero); Assert.That(sensor.Mass, Is.Zero);
        }

        [UnityTest] public IEnumerator CargoCountsOneLogicalLoadAcrossMultipleRigidbodies()
        {
            var pelvis = Body("Grouped pelvis", Vector3.left * 0.6f); pelvis.mass = 12;
            var torso = Body("Grouped torso", Vector3.right * 0.6f); torso.mass = 18;
            bool free = true;
            var sensor = Cargo(candidate => free && (candidate == pelvis || candidate == torso) ? pelvis : null, group => 68);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.EqualTo(1)); Assert.That(sensor.Mass, Is.EqualTo(68));
            free = false; yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.Zero); Assert.That(sensor.Mass, Is.Zero);
            free = true; yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.BodyCount, Is.EqualTo(1)); Assert.That(sensor.Mass, Is.EqualTo(68));
        }

        [UnityTest] public IEnumerator DisabledAndRelocatedCollidersCannotLeaveGhostCargo()
        {
            var sensor = Cargo(candidate => candidate, group => group.mass);
            var body = Body("Transient cargo collider", Vector3.zero); body.mass = 7;
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.Mass, Is.EqualTo(7)); body.GetComponent<Collider>().enabled = false;
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(body.gameObject.activeInHierarchy, Is.True); Assert.That(sensor.Mass, Is.Zero);
            body.position += Vector3.right * 20; body.GetComponent<Collider>().enabled = true; Physics.SyncTransforms();
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.Mass, Is.Zero); Assert.That(sensor.BodyCount, Is.Zero);
        }

        [UnityTest] public IEnumerator CargoObservationOverflowRemainsVisibleAfterTheVolumeClears()
        {
            var sensor = Cargo(candidate => candidate, group => group.mass, 1);
            var first = Body("Cargo A", Vector3.left * 0.6f); var second = Body("Cargo B", Vector3.right * 0.6f);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.Saturated, Is.True);
            first.gameObject.SetActive(false); second.gameObject.SetActive(false);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.Mass, Is.Zero); Assert.That(sensor.BodyCount, Is.Zero); Assert.That(sensor.Saturated, Is.True);
        }
    }
}
