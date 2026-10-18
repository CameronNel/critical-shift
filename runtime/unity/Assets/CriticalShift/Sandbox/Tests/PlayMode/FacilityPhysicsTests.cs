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
            Vector3 position = body.position, velocity = body.linearVelocity; int failures = 0; bool live = true;
            safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 10),
                maximumLinearSpeed: 10, maximumRotationalEnergyPerMass: 50, () => live, error => failures++);
            safety.Bind(body, "Observed body"); safety.Activate(); safety.Sample();
            Assert.That(safety.DynamicBodyCount, Is.EqualTo(1)); Assert.That(safety.PeakLinearSpeed, Is.EqualTo(2).Within(0.001f));
            Assert.That(body.position, Is.EqualTo(position)); Assert.That(body.linearVelocity, Is.EqualTo(velocity));
            body.isKinematic = true; safety.Sample();
            Assert.That(safety.DynamicBodyCount, Is.Zero); Assert.That(safety.PeakDynamicBodyCount, Is.EqualTo(1));
            Assert.That(safety.BoundBodyCount, Is.EqualTo(1)); Assert.That(failures, Is.Zero);
            live = false; safety.Sample();
            Assert.That(safety.BoundBodyCount, Is.Zero); Assert.That(safety.DynamicBodyCount, Is.Zero);
            Assert.That(body.isKinematic, Is.True); Assert.That(failures, Is.Zero);
        }

        [Test] public void PhysicsMonitorLatchesOneRunawayFailureAndLeavesMotionToItsOwner()
        {
            var body = Body("Runaway body", Vector3.zero); body.linearVelocity = Vector3.forward * 11;
            int failures = 0; string reason = "";
            safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 10),
                maximumLinearSpeed: 10, maximumRotationalEnergyPerMass: 50, () => true,
                error => { failures++; reason = error.Message; });
            safety.Bind(body, "Runaway body"); safety.Activate(); safety.Sample();
            Assert.That(safety.FaultLatched, Is.True); Assert.That(failures, Is.EqualTo(1));
            Assert.That(reason, Does.Contain("Runaway body")); Assert.That(body.linearVelocity.z, Is.EqualTo(11));
            body.linearVelocity = Vector3.zero; safety.Sample(); safety.Sample();
            Assert.That(failures, Is.EqualTo(1)); safety.Shutdown(); Assert.That(safety.BoundBodyCount, Is.Zero);
        }

        [Test] public void PhysicsMonitorDistinguishesNativeRotationalEnergyAtTheSameAngularSpeed()
        {
            var small = Body("Small solid cube", Vector3.left * 4); small.mass = 1;
            var large = Body("Large solid cube", Vector3.right * 4); large.mass = 1;
            small.GetComponent<BoxCollider>().size = Vector3.one * 0.2f;
            large.GetComponent<BoxCollider>().size = Vector3.one * 4;
            Physics.SyncTransforms(); small.ResetInertiaTensor(); large.ResetInertiaTensor();
            Assert.That(small.inertiaTensor.y, Is.EqualTo(0.2 * 0.2 / 6).Within(0.0001));
            Assert.That(large.inertiaTensor.y, Is.EqualTo(4.0 * 4 / 6).Within(0.0001));
            small.angularVelocity = Vector3.up * 30; large.angularVelocity = Vector3.up * 30;
            Assert.That(small.angularVelocity.y, Is.EqualTo(30)); Assert.That(large.angularVelocity.y, Is.EqualTo(30));
            Vector3 smallPosition = small.position, largePosition = large.position;
            Quaternion smallRotation = small.rotation, largeRotation = large.rotation;
            int failures = 0; string reason = "";
            safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 30),
                maximumLinearSpeed: 25, maximumRotationalEnergyPerMass: 312.5,
                () => true, error => { failures++; reason = error.Message; });
            safety.Bind(small, "Small solid cube"); safety.Bind(large, "Large solid cube");
            // Observe the small native body first while the large body is temporarily kinematic.
            large.isKinematic = true; safety.Activate(); safety.Sample();
            Assert.That(failures, Is.Zero); Assert.That(safety.PeakAngularSpeed, Is.EqualTo(30).Within(0.0001));
            Assert.That(safety.PeakRotationalEnergyPerMass, Is.EqualTo(3).Within(0.001));
            large.isKinematic = false; large.angularVelocity = Vector3.up * 30; safety.Sample();
            Assert.That(failures, Is.EqualTo(1)); Assert.That(safety.FaultLatched, Is.True);
            Assert.That(reason, Does.Contain("Large solid cube")); Assert.That(reason, Does.Contain("rotationalEnergyPerMass="));
            Assert.That(safety.PeakRotationalEnergyPerMass, Is.EqualTo(1200).Within(0.01));
            Assert.That(small.angularVelocity.y, Is.EqualTo(30)); Assert.That(large.angularVelocity.y, Is.EqualTo(30));
            Assert.That(small.position, Is.EqualTo(smallPosition)); Assert.That(large.position, Is.EqualTo(largePosition));
            Assert.That(small.rotation, Is.EqualTo(smallRotation)); Assert.That(large.rotation, Is.EqualTo(largeRotation));
            safety.Sample(); safety.Sample(); Assert.That(failures, Is.EqualTo(1)); Assert.That(safety.BoundBodyCount, Is.Zero);
        }

        [Test] public void PhysicsMonitorUsesTheNativePrincipalInertiaFrame()
        {
            var item = new GameObject("Rotated principal inertia body"); item.transform.SetParent(root.transform, false);
            item.transform.localRotation = Quaternion.Euler(19, 37, 11);
            var body = item.AddComponent<Rigidbody>(); body.useGravity = false; body.mass = 1;
            var contact = new GameObject("Rotated solid box"); contact.transform.SetParent(item.transform, false);
            contact.transform.localRotation = Quaternion.Euler(23, 41, 17);
            contact.AddComponent<BoxCollider>().size = new Vector3(0.2f, 2, 4);
            Physics.SyncTransforms(); body.ResetInertiaTensor();
            Vector3 tensor = body.inertiaTensor;
            Assert.That(Quaternion.Angle(body.inertiaTensorRotation, Quaternion.identity), Is.GreaterThan(5));
            int low = tensor.x < tensor.y ? 0 : 1; if (tensor.z < tensor[low]) low = 2;
            int high = tensor.x > tensor.y ? 0 : 1; if (tensor.z > tensor[high]) high = 2;
            Assert.That(0.5 * tensor[low] * 900, Is.LessThan(312.5));
            Assert.That(0.5 * tensor[high] * 900, Is.GreaterThan(312.5));
            Vector3 axis = Vector3.zero; axis[low] = 1;
            Quaternion principal = body.rotation * body.inertiaTensorRotation;
            body.angularVelocity = principal * axis * 30;
            int failures = 0; safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 30),
                maximumLinearSpeed: 25, maximumRotationalEnergyPerMass: 312.5, () => true, error => failures++);
            safety.Bind(body, "Rotated principal inertia body"); safety.Activate(); safety.Sample();
            Assert.That(failures, Is.Zero);
            Assert.That(safety.PeakRotationalEnergyPerMass, Is.EqualTo(0.5 * tensor[low] * 900).Within(0.001));
            axis = Vector3.zero; axis[high] = 1; body.angularVelocity = principal * axis * 30; safety.Sample();
            Assert.That(failures, Is.EqualTo(1)); Assert.That(safety.FaultLatched, Is.True);
            Assert.That(safety.PeakRotationalEnergyPerMass, Is.EqualTo(0.5 * tensor[high] * 900).Within(0.001));
        }

        [Test] public void PhysicsMonitorAcceptsHealthyNativeInfiniteInertiaConstraints()
        {
            var body = Body("Infinite inertia body", Vector3.zero); body.mass = 1;
            body.inertiaTensor = Vector3.zero; body.angularVelocity = Vector3.zero;
            Assert.That(body.inertiaTensor, Is.EqualTo(Vector3.zero));
            int failures = 0; safety = root.AddComponent<PhysicsSafetyMonitor>();
            safety.Initialize(root.transform, new Bounds(Vector3.zero, Vector3.one * 10),
                maximumLinearSpeed: 25, maximumRotationalEnergyPerMass: 312.5,
                () => true, error => failures++);
            safety.Bind(body, "Infinite inertia body"); safety.Activate(); safety.Sample();
            Assert.That(failures, Is.Zero); Assert.That(safety.PeakRotationalEnergyPerMass, Is.Zero);
            body.rotation = Quaternion.Euler(19, 37, 11);
            body.inertiaTensorRotation = Quaternion.Euler(23, 41, 17);
            body.inertiaTensor = new Vector3(0, 1, 0);
            body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            body.angularVelocity = (body.rotation * body.inertiaTensorRotation) * Vector3.up * 2;
            Assert.That(body.inertiaTensor.x, Is.Zero); Assert.That(body.inertiaTensor.z, Is.Zero);
            Vector3 velocity = body.angularVelocity; Assert.That(velocity.magnitude, Is.EqualTo(2).Within(0.0001));
            safety.Sample(); Assert.That(failures, Is.Zero); Assert.That(safety.FaultLatched, Is.False);
            Assert.That(safety.PeakRotationalEnergyPerMass, Is.EqualTo(2).Within(0.001));
            Assert.That(body.angularVelocity, Is.EqualTo(velocity), "Native constrained motion is observed, never repaired.");
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
            var pivots = WheelPivots(body.transform);
            body.gameObject.AddComponent<CartWheelMotion>().Initialize(motor, pivots);
            motor.SetDrive(1, 0, false);
            float observedRoll = 0;
            for (int i = 0; i < 100; i++)
            {
                yield return new WaitForFixedUpdate();
                observedRoll = Mathf.Max(observedRoll, Quaternion.Angle(Quaternion.identity, pivots[0].localRotation));
            }
            Assert.That(motor.Speed, Is.GreaterThan(1));
            Assert.That(motor.Speed, Is.LessThanOrEqualTo(motor.MaximumSpeed + 0.05f));
            Assert.That(Mathf.Abs(body.linearVelocity.y), Is.LessThan(0.001f));
            motor.SetDrive(0, 0, true);
            for (int i = 0; i < 40; i++) yield return new WaitForFixedUpdate();
            yield return null;
            Assert.That(observedRoll, Is.GreaterThan(15));
            for (int i = 1; i < pivots.Length; i++)
                Assert.That(Quaternion.Angle(pivots[0].localRotation, pivots[i].localRotation), Is.LessThan(0.01f));
        }

        private Transform[] WheelPivots(Transform cart)
        {
            var pivots = new Transform[4];
            for (int i = 0; i < pivots.Length; i++)
            {
                pivots[i] = new GameObject("Visual wheel pivot " + i).transform;
                pivots[i].SetParent(cart, false);
            }
            return pivots;
        }

        [Test] public void WheelAnimationRejectsContactShapesDuplicatePivotsAndOtherCarts()
        {
            var body = Body("Wheel binding cart", Vector3.zero);
            var motor = body.gameObject.AddComponent<CartMotor>(); motor.Initialize(() => true, () => 0);
            var animation = body.gameObject.AddComponent<CartWheelMotion>();
            var pivots = WheelPivots(body.transform);
            var contact = pivots[0].gameObject.AddComponent<BoxCollider>();
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(motor, pivots));
            contact.enabled = false;
            var duplicate = (Transform[])pivots.Clone(); duplicate[1] = duplicate[0];
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(motor, duplicate));
            pivots[1].SetParent(pivots[0], false);
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(motor, pivots));
            pivots[1].SetParent(root.transform, false);
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(motor, pivots));
            pivots[1].SetParent(body.transform, false);
            animation.Initialize(motor, pivots);
            Assert.That(body.position, Is.EqualTo(root.transform.position));
            Assert.That(contact.enabled, Is.False);
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

        [UnityTest] public IEnumerator RejectedCartSetupCannotDriveUntilItsBindingIsCorrected()
        {
            var body = Body("Rejected cart motor body", Vector3.zero); body.isKinematic = true;
            var motor = body.gameObject.AddComponent<CartMotor>(); motor.SetDrive(1, 0, false);
            Assert.Throws<System.InvalidOperationException>(() => motor.Initialize(() => true, () => 0));
            body.isKinematic = false; Assert.That(motor.HasDriveAuthority, Is.False);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
            motor.Initialize(() => true, () => 0); motor.SetDrive(1, 0, false);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.HasDriveAuthority, Is.True); Assert.That(motor.Speed, Is.GreaterThan(0.01f));
            body.detectCollisions = false; Assert.That(motor.HasDriveAuthority, Is.False);
        }

        [UnityTest] public IEnumerator CartAuthorityLossRequiresFreshDriveInputAfterPermissionReturns()
        {
            var body = Body("Cart authority reset", Vector3.zero); bool permitted = false;
            var motor = body.gameObject.AddComponent<CartMotor>(); motor.Initialize(() => permitted, () => 0);
            motor.SetDrive(1, 1, false); permitted = true;
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.HasDriveAuthority, Is.True); Assert.That(motor.Speed, Is.LessThan(0.001f));
            Assert.That(motor.Steering, Is.Zero);
            motor.SetDrive(1, 1, false);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.Speed, Is.GreaterThan(0.01f));
            permitted = false; yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            body.linearVelocity = Vector3.zero; body.angularVelocity = Vector3.zero; permitted = true;
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.Speed, Is.LessThan(0.001f)); Assert.That(motor.Steering, Is.Zero);
            motor.SetDrive(1, 0, false);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motor.Speed, Is.GreaterThan(0.01f));
        }

        [UnityTest] public IEnumerator InvalidCartObservationsDisableDriveWithoutApplyingForces()
        {
            float[] invalidMasses = { -1, float.NaN, float.PositiveInfinity, float.NegativeInfinity };
            for (int i = 0; i <= invalidMasses.Length; i++)
            {
                var body = Body("Invalid cargo observation " + i, Vector3.right * (i * 2)); int observations = 0;
                var motor = body.gameObject.AddComponent<CartMotor>();
                motor.Initialize(() => true, () =>
                {
                    observations++;
                    if (i == invalidMasses.Length) throw new System.InvalidOperationException("Cargo callback failed.");
                    return invalidMasses[i];
                });
                motor.SetDrive(1, 0, false);
                Assert.Throws<System.InvalidOperationException>(() => { _ = motor.CargoMass; });
                Assert.That(motor.enabled, Is.False); Assert.That(motor.HasDriveAuthority, Is.False);
                Assert.That(motor.CargoMass, Is.Zero);
                yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
                Assert.That(observations, Is.EqualTo(1)); Assert.That(body.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
            }
            var authorityBody = Body("Throwing cart authority", Vector3.back * 2); int permissions = 0;
            var authorityMotor = authorityBody.gameObject.AddComponent<CartMotor>();
            authorityMotor.Initialize(() => { permissions++; throw new System.InvalidOperationException("Authority callback failed."); }, () => 0);
            Assert.Throws<System.InvalidOperationException>(() => authorityMotor.SetDrive(1, 1, false));
            Assert.That(authorityMotor.enabled, Is.False); Assert.That(authorityMotor.HasDriveAuthority, Is.False);
            authorityMotor.SetDrive(1, 1, false);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(permissions, Is.EqualTo(1)); Assert.That(authorityBody.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
        }

        [UnityTest] public IEnumerator BeltAnimationRejectsUnsafeBindingsBeforeInstallingItsMotion()
        {
            var owner = new GameObject("Belt visual owner"); owner.transform.SetParent(root.transform, false);
            var sensor = new GameObject("Belt visual drive"); sensor.transform.SetParent(owner.transform, false);
            var volume = sensor.AddComponent<BoxCollider>(); volume.isTrigger = true;
            var drive = sensor.AddComponent<ConveyorDrive>(); drive.Initialize(body => false, () => true);
            var animation = owner.AddComponent<ConveyorBeltMotion>();
            var visuals = new Transform[4];
            for (int i = 0; i < visuals.Length; i++)
            {
                visuals[i] = new GameObject("Belt visual " + i).transform; visuals[i].SetParent(owner.transform, false);
            }
            var treads = new[] { visuals[0], visuals[1] }; var rollers = new[] { visuals[2], visuals[3] };
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(drive, new[] { treads[0], treads[0] }, 4, rollers, 0.16f));
            visuals[1].SetParent(visuals[0], false);
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(drive, treads, 4, rollers, 0.16f));
            visuals[1].SetParent(root.transform, false);
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(drive, treads, 4, rollers, 0.16f));
            visuals[1].SetParent(owner.transform, false);
            var hidden = new GameObject("Inactive physical descendant"); hidden.transform.SetParent(visuals[0], false); hidden.SetActive(false);
            var contact = hidden.AddComponent<BoxCollider>();
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(drive, treads, 4, rollers, 0.16f));
            contact.enabled = false; var physical = hidden.AddComponent<Rigidbody>(); physical.useGravity = false;
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(drive, treads, 4, rollers, 0.16f));
            hidden.transform.SetParent(root.transform, false);
            var otherBelt = Belt(body => false);
            Assert.Throws<System.ArgumentException>(() => animation.Initialize(otherBelt, treads, 4, rollers, 0.16f));
            animation.Initialize(drive, treads, 4, rollers, 0.16f);
            Vector3 physicalPosition = hidden.transform.position;
            for (int i = 0; i < 4; i++) { yield return new WaitForFixedUpdate(); yield return null; }
            Assert.That(drive.Running, Is.True); Assert.That(treads[0].localPosition.z, Is.GreaterThan(0));
            Assert.That(Quaternion.Angle(Quaternion.identity, rollers[0].localRotation), Is.GreaterThan(0));
            Assert.That(hidden.transform.position, Is.EqualTo(physicalPosition)); Assert.That(contact.enabled, Is.False);
        }

        [UnityTest] public IEnumerator ConveyorCannotAccelerateAnUnauthorizedBody()
        {
            var body = Body("Unregistered body", Vector3.zero); var belt = Belt(candidate => false);
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
            Assert.That(belt.MovingBodyCount, Is.Zero);
        }

        [UnityTest] public IEnumerator RejectedConveyorSetupCannotDriveBeforeACorrectedBinding()
        {
            var body = Body("Portable beside rejected conveyor", Vector3.zero);
            var owner = new GameObject("Rejected conveyor observation bounds"); owner.transform.SetParent(root.transform, false);
            var volume = owner.AddComponent<BoxCollider>(); volume.size = Vector3.one * 10; volume.enabled = false;
            var belt = owner.AddComponent<ConveyorDrive>();
            Assert.Throws<System.InvalidOperationException>(() => belt.Initialize(candidate => candidate == body, () => true));
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.sqrMagnitude, Is.LessThan(0.0001f));
            Assert.That(belt.Available, Is.False); Assert.That(belt.Running, Is.False);
            volume.isTrigger = true; volume.enabled = true; belt.Initialize(candidate => candidate == body, () => true);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(belt.Available, Is.True); Assert.That(belt.MovingBodyCount, Is.EqualTo(1));
            Assert.That(body.linearVelocity.z, Is.GreaterThan(0.01f));
            belt.enabled = false; Assert.That(belt.Available, Is.False); Assert.That(belt.Running, Is.False); Assert.That(belt.MovingBodyCount, Is.Zero);
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
            sensor.enabled = false; Assert.That(sensor.Available, Is.False); Assert.That(sensor.Saturated, Is.True);
            sensor.enabled = true; Assert.That(sensor.Available, Is.False); Assert.That(sensor.Saturated, Is.True);
            yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
            Assert.That(sensor.Available, Is.True); Assert.That(sensor.Saturated, Is.True);
        }

        [UnityTest] public IEnumerator CartDriveRequiresAFreshAvailableCargoSample()
        {
            var sensor = Cargo(candidate => candidate, group => group.mass);
            var body = sensor.GetComponent<Rigidbody>(); body.isKinematic = false; body.useGravity = false;
            var motor = body.gameObject.AddComponent<CartMotor>();
            motor.Initialize(() => sensor.Available && !sensor.Saturated, () => sensor.Mass); motor.SetDrive(1, 0, false);
            Assert.That(sensor.Available, Is.False); Assert.That(motor.HasDriveAuthority, Is.False);
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.Available, Is.True); Assert.That(motor.HasDriveAuthority, Is.True);
            sensor.enabled = false; Assert.That(motor.HasDriveAuthority, Is.False); Assert.That(sensor.Mass, Is.Zero);
            yield return new WaitForFixedUpdate();
            sensor.enabled = true; Assert.That(sensor.Available, Is.False); Assert.That(motor.HasDriveAuthority, Is.False);
            for (int i = 0; i < 3; i++) yield return new WaitForFixedUpdate();
            Assert.That(sensor.Available, Is.True); Assert.That(motor.HasDriveAuthority, Is.True);
        }
    }
}
