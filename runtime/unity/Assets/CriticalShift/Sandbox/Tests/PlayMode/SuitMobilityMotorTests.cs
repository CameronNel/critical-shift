using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    // Actual motor/controller comparisons, declared only until the pinned Unity runner executes them.
    public sealed class SuitMobilityMotorTests
    {
        private GameObject root;
        private WorldSession world;
        private readonly LocalWorkerMotor[] motors = new LocalWorkerMotor[2];
        private readonly CharacterController[] controllers = new CharacterController[2];
        private readonly Transform[] eyes = new Transform[2];
        private readonly Vector3?[] stances = new Vector3?[2];
        private readonly List<Exception> faults = new List<Exception>();
        private Collider floor;
        private float load;
        private static Guid Id(int n) => new Guid(n, 0, 0, new byte[8]);
        [UnitySetUp] public IEnumerator SetUp()
        {
            faults.Clear(); load = 20;
            root = new GameObject("Explicit suit mobility motor comparison"); root.transform.position = new Vector3(8000, 0, 8000);
            var ground = new GameObject("Explicit static support"); ground.transform.SetParent(root.transform, false);
            ground.transform.localPosition = new Vector3(0, -0.15f, 0);
            var box = ground.AddComponent<BoxCollider>(); box.size = new Vector3(50, 0.3f, 50); floor = box;
            world = new WorldSession(new WorldSessionConfiguration(42, 60000, true), new SpatialInteractionAccess(3.8f));
            for (int i = 0; i < 2; i++) world.RegisterConnection(Id(20 + i), Id(10 + i));
            for (int i = 0; i < 2; i++)
            {
                int index = i; stances[i] = null;
                var actor = new GameObject("Motor " + i); actor.transform.SetParent(root.transform, false);
                actor.transform.localPosition = new Vector3(i == 0 ? -2 : 2, 0.05f, 0);
                controllers[i] = SandboxWorkerRigBuilder.AddController(actor);
                var view = new GameObject("Eyes"); view.transform.SetParent(actor.transform, false); view.transform.localPosition = new Vector3(0, 1.55f, 0); eyes[i] = view.transform;
                motors[i] = actor.AddComponent<LocalWorkerMotor>();
                motors[i].Initialize(eyes[i], () => world.GetWorker(Id(10 + index)), () => world.View.Phase == WorldPhase.Running,
                    faults.Add, () => load, () => stances[index]);
            }
            world.Start(); Physics.SyncTransforms();
            for (int i = 0; i < 20; i++) yield return new WaitForFixedUpdate();
            Assert.That(motors[0].Grounded && motors[1].Grounded, Is.True);
        }
        private void Suit(int index, WorkerSuit suit)
        {
            var worker = world.GetWorker(Id(10 + index));
            Assert.That(world.SetWorkerEnvironment(world.Epoch, worker.Id, worker.Revision, suit, 0).Status,
                Is.AnyOf(WorkerStatus.Applied, WorkerStatus.NoChange));
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            world?.Stop(); if (root != null) UnityEngine.Object.Destroy(root); yield return null;
            Array.Clear(motors, 0, motors.Length); Array.Clear(controllers, 0, controllers.Length); Array.Clear(eyes, 0, eyes.Length);
            LogAssert.NoUnexpectedReceived(); Assert.That(faults, Is.Empty);
        }
        [UnityTest] public IEnumerator WornSuitWalkingComposesWithTheSameCarriedMass()
        {
            foreach (float payload in new[] { 20f, 68f })
            foreach (var suit in new[] { WorkerSuit.Intact, WorkerSuit.Compromised })
            {
                load = payload;
                Suit(1, suit); Vector3 a = motors[0].transform.position, b = motors[1].transform.position;
                motors[0].SetMovement(Vector2.up); motors[1].SetMovement(Vector2.up);
                for (int i = 0; i < 30; i++) yield return new WaitForFixedUpdate();
                motors[0].SetMovement(Vector2.zero); motors[1].SetMovement(Vector2.zero);
                float plain = motors[0].transform.position.z - a.z, worn = motors[1].transform.position.z - b.z;
                Assert.That(plain, Is.GreaterThan(0.1f)); Assert.That(worn / plain, Is.EqualTo(0.8f).Within(0.04f));
                float expectedCarry = payload == 20 ? 0.5f : 0.35f;
                Assert.That(motors[0].CarrySpeedScale, Is.EqualTo(expectedCarry)); Assert.That(motors[1].CarrySpeedScale, Is.EqualTo(expectedCarry));
                Assert.That(motors[1].SuitWalkSpeedScale, Is.EqualTo(0.8f)); yield return null;
            }
            // Start steering only after support is gone, so a grounded-only multiplier cannot pass.
            yield return new WaitForFixedUpdate(); yield return null;
            floor.enabled = false; Physics.SyncTransforms();
            for (int i = 0; i < 2; i++) yield return new WaitForFixedUpdate();
            Assert.That(motors[0].Grounded || motors[1].Grounded, Is.False);
            motors[0].SetMovement(Vector2.up); motors[1].SetMovement(Vector2.up);
            for (int i = 0; i < 40; i++) yield return new WaitForFixedUpdate();
            Vector3 airborne0 = motors[0].transform.position, airborne1 = motors[1].transform.position;
            for (int i = 0; i < 20; i++) yield return new WaitForFixedUpdate();
            float air0 = motors[0].transform.position.z - airborne0.z, air1 = motors[1].transform.position.z - airborne1.z;
            Assert.That(air0, Is.GreaterThan(0.1f)); Assert.That(air1 / air0, Is.EqualTo(0.8f).Within(0.04f));
            Assert.That(motors[0].transform.position.y - airborne0.y, Is.EqualTo(motors[1].transform.position.y - airborne1.y).Within(0.02f));
        }
        [UnityTest] public IEnumerator WornSuitKeepsTheSameHopLookAndIdleFalling()
        {
            Suit(1, WorkerSuit.Intact); float first = motors[0].transform.position.y, second = motors[1].transform.position.y;
            for (int i = 0; i < 2; i++) { motors[i].Look(new Vector2(20, -10)); motors[i].RequestJump(); }
            float peak0 = 0, peak1 = 0;
            for (int i = 0; i < 70; i++)
            {
                yield return new WaitForFixedUpdate();
                peak0 = Mathf.Max(peak0, motors[0].transform.position.y - first); peak1 = Mathf.Max(peak1, motors[1].transform.position.y - second);
                Assert.That((motors[0].transform.position.y - first) - (motors[1].transform.position.y - second), Is.EqualTo(0).Within(0.02f));
            }
            Assert.That(peak0, Is.GreaterThan(0.1f)); Assert.That(peak1, Is.EqualTo(peak0).Within(0.02f));
            Assert.That(Quaternion.Angle(eyes[0].rotation, eyes[1].rotation), Is.LessThan(0.01f));
            floor.enabled = false; Physics.SyncTransforms();
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            Assert.That(motors[0].transform.position.y, Is.LessThan(first - 0.1f));
            Assert.That((motors[0].transform.position.y - first) - (motors[1].transform.position.y - second), Is.EqualTo(0).Within(0.02f));
        }
        [UnityTest] public IEnumerator SuitChangeDuringFlightDoesNotMultiplyExistingMomentum()
        {
            for (int i = 0; i < 2; i++) { motors[i].SetMovement(Vector2.up); motors[i].RequestJump(); }
            for (int i = 0; i < 4; i++) yield return new WaitForFixedUpdate();
            Assert.That(motors[0].Grounded || motors[1].Grounded, Is.False);
            Suit(1, WorkerSuit.Intact); motors[0].SetMovement(Vector2.zero); motors[1].SetMovement(Vector2.zero);
            for (int i = 0; i < 8; i++)
            {
                yield return new WaitForFixedUpdate();
                Assert.That(motors[0].MeasuredVelocity.z, Is.EqualTo(motors[1].MeasuredVelocity.z).Within(0.05f));
                Assert.That(motors[0].MeasuredVelocity.y, Is.EqualTo(motors[1].MeasuredVelocity.y).Within(0.05f));
            }
        }
        [UnityTest] public IEnumerator WornSuitDoesNotSlowTheBoundCartStanceCorrection()
        {
            Suit(1, WorkerSuit.Compromised);
            Vector3 first = motors[0].transform.position, second = motors[1].transform.position;
            stances[0] = first + Vector3.forward; stances[1] = second + Vector3.forward;
            for (int i = 0; i < 20; i++) yield return new WaitForFixedUpdate();
            float a = motors[0].transform.position.z - first.z, b = motors[1].transform.position.z - second.z;
            Assert.That(a, Is.GreaterThan(0.8f)); Assert.That(b, Is.EqualTo(a).Within(0.01f));
            Assert.That(world.GetWorker(Id(11)).SuitWalkSpeedPermille, Is.EqualTo(800));
        }
    }
}
