using System;
using System.Collections;
using System.Text.RegularExpressions;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class CombinedMapLifetimeTests
    {
        private GameObject root;
        private CombinedMapBootstrap bootstrap;
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (root != null)
            {
                if (bootstrap != null) bootstrap.enabled = false;
                UnityEngine.Object.Destroy(root);
            }
            yield return null; yield return null; LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator DoorEvacuationProjectsIntoTheOwnedCloneAndTeardownReleasesItsContacts()
        {
            CreateFixture(); yield return null; yield return null;
            Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Running));
            var binding = root.GetComponentInChildren<CombinedMapDoorBindings>();
            Assert.That(binding.BoundDoorCount, Is.EqualTo(1));
            var authoring = binding.GetComponent<CombinedMapAuthoring>();
            var door = authoring.CopyDoorReferences()[0];
            Assert.That(door.blocker.enabled, Is.True); Assert.That(door.threshold.enabled, Is.True);
            var host = root.GetComponentInChildren<LocalWorldHost>();
            Guid id = CombinedMapBootstrap.DoorIdentity("TEST_EXIT");
            Assert.That(host.Commands.GetDoor(id).State, Is.EqualTo(DoorState.Closed));
            root.GetComponentInChildren<MapDoorHost>().BeginEvacuationExercise();
            Assert.That(host.Commands.GetDoor(id).State, Is.EqualTo(DoorState.Open));
            Assert.That(door.blocker.enabled, Is.False); Assert.That(door.threshold.enabled, Is.True);
            for (int i = 0; i < 20; i++) yield return new WaitForFixedUpdate();
            Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Running));
            var rig = root.GetComponentInChildren<WorkerBodyRig>();
            bootstrap.enabled = false;
            Assert.That(bootstrap.World, Is.Null); Assert.That(binding.BoundDoorCount, Is.Zero);
            Assert.That(door.blocker.enabled, Is.False); Assert.That(door.threshold.enabled, Is.False);
            foreach (var body in rig.CopyBodySegments()) Assert.That(body.isKinematic, Is.True);
            yield return null; yield return null;
        }

        [UnityTest] public IEnumerator ImmediateRestartKeepsDeferredOldHudCleanupInsideItsOriginalWorld()
        {
            CreateFixture(); yield return null; yield return null;
            Guid previous = bootstrap.World.Epoch;
            for (int i = 0; i < 3; i++)
            {
                bootstrap.enabled = false; ExpectReady(); bootstrap.enabled = true;
                yield return null; yield return null;
                Assert.That(bootstrap.World, Is.Not.Null);
                Assert.That(bootstrap.World.Epoch, Is.Not.EqualTo(previous)); previous = bootstrap.World.Epoch;
                Assert.That(bootstrap.World.Phase, Is.EqualTo(WorldPhase.Running));
                Assert.That(root.GetComponentsInChildren<MapDoorHost>().Length, Is.EqualTo(1));
                Assert.That(root.GetComponentsInChildren<WorkerBodyRig>().Length, Is.EqualTo(1));
                Assert.That(root.GetComponentInChildren<CombinedMapDoorBindings>().BoundDoorCount, Is.EqualTo(1));
                LogAssert.NoUnexpectedReceived();
            }
        }

        private void CreateFixture()
        {
            ExpectReady();
            root = new GameObject("Synthetic combined-map lifetime fixture"); root.transform.position = new Vector3(1800, 0, 1800);
            bootstrap = root.AddComponent<CombinedMapBootstrap>();
            var model = Child("Inactive generated template", root.transform, Vector3.zero);
            model.transform.localRotation = Quaternion.Euler(0, 180, 0);
            var authoring = model.AddComponent<CombinedMapAuthoring>();
            var floor = Child("Synthetic floor", model.transform, new Vector3(0, -0.1f, 0)).AddComponent<BoxCollider>();
            floor.size = new Vector3(12, 0.2f, 12);
            var frame = Child("Synthetic exit", model.transform, new Vector3(3, 0, 0)).transform;
            var anchor = Child("Anchor", frame, Vector3.zero).transform;
            var control = Child("Interaction point", frame, Vector3.up).transform;
            var blocker = Child("Blocker", frame, Vector3.up).AddComponent<BoxCollider>(); blocker.size = new Vector3(0.2f, 2, 2);
            var threshold = Child("Threshold", frame, Vector3.up).AddComponent<BoxCollider>();
            threshold.size = new Vector3(1, 2, 2); threshold.isTrigger = true;
            authoring.Configure(new[] { new CombinedMapDoorReference
            {
                definition = new CombinedDoorRow { id = "TEST_EXIT", state = "closed", evac_state = "open", clear_w = 2, clear_h = 2 },
                anchor = anchor, interactionPoint = control, blocker = blocker, threshold = threshold
            } }, new Vector3(0, 0.08f, 0), new Bounds(Vector3.up * 2, new Vector3(16, 12, 16)), new string('a', 64));
            model.SetActive(false);
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); bootstrap.Configure(authoring, shader);
        }
        private static void ExpectReady() => LogAssert.Expect(LogType.Log,
            new Regex("^CS_COMBINED_MAP_READY epoch=[0-9a-f]{32} doors=1 art_accepted=false$"));
        private static GameObject Child(string name, Transform parent, Vector3 position)
        {
            var child = new GameObject(name); child.transform.SetParent(parent, false); child.transform.localPosition = position; return child;
        }
    }
}
