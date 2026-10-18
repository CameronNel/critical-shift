using System;
using System.Collections;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityObject = UnityEngine.Object;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class LocalWorldHostTests
    {
        private GameObject root;
        private WorldSession world;
        private LocalWorldHost host;
        private LocalCommandPort port;
        private Rigidbody body;
        private Transform target, slot;
        private double clock;
        private static Guid Id(int number) => new Guid(number, 0, 0, new byte[8]);
        private Guid Box => Id(10);
        private Guid Actor => Id(20);
        private Guid Machine => Id(30);

        private sealed class AllowedFixtureAccess : IInteractionAccessPolicy
        {
            public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed;
        }

        [SetUp] public void SetUp()
        {
            clock = 0; root = new GameObject("Local host regression fixture");
            root.transform.position = new Vector3(1000, 1000, 1000);
            world = new WorldSession(new WorldSessionConfiguration(1, 60000, true), new AllowedFixtureAccess());
            world.RegisterConnection(Id(1), Actor);
            world.Production.RegisterBatch(Box, Id(11), Id(12), Id(13), MaterialKind.Ore, 10);
            world.Production.RegisterMachine(Machine, new MachineRecipe(Id(31), MaterialKind.Ore, MaterialKind.CrushedOre,
                1000, 500, 100, 100));
            port = new LocalCommandPort(world, Id(1));
            host = root.AddComponent<LocalWorldHost>(); host.Initialize(world, port, Actor, () => clock);
            var crate = GameObject.CreatePrimitive(PrimitiveType.Cube); crate.transform.SetParent(root.transform, false);
            crate.transform.localPosition = new Vector3(0, 1, 0);
            body = crate.AddComponent<Rigidbody>(); body.useGravity = false;
            target = new GameObject("Carry target").transform; target.SetParent(root.transform, false); target.localPosition = new Vector3(0, 1, 1);
            slot = new GameObject("Machine slot").transform; slot.SetParent(root.transform, false); slot.localPosition = new Vector3(3, 1, 0);
            host.BindBody(Box, body); host.BindCarryTarget(Actor, target); host.BindSlot(Machine, slot);
            host.Activate();
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            if (host != null) host.Shutdown();
            if (root != null) UnityObject.Destroy(root);
            yield return null;
            LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator GrabUsesControlledForcesTowardsCurrentTarget()
        {
            host.Grab(Box);
            for (int i = 0; i < 35; i++) yield return new WaitForFixedUpdate();
            Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor));
            Assert.That(Vector3.Distance(body.position, target.position), Is.LessThan(0.25f));
            Assert.That(body.isKinematic, Is.False);
        }

        [UnityTest] public IEnumerator ExpiredLeaseReleasesPhysicalControl()
        {
            host.Grab(Box); clock = 3; host.Pump();
            yield return new WaitForFixedUpdate();
            Assert.That(world.GetObject(Box).HolderId, Is.Null);
            Assert.That(body.isKinematic, Is.False);
            Assert.That(world.View.ActiveClaimCount, Is.Zero);
        }

        [UnityTest] public IEnumerator ExcessiveObstructionDropsTheExactLease()
        {
            host.Grab(Box); target.localPosition = new Vector3(10, 1, 0);
            yield return new WaitForFixedUpdate(); yield return null;
            Assert.That(world.GetObject(Box).HolderId, Is.Null);
            Assert.That(host.LastAction, Does.Contain("obstructed"));
        }

        [UnityTest] public IEnumerator InsertAndEjectReconcileKinematicSlotBinding()
        {
            host.Grab(Box); host.OperateMachine(Machine, ProductionAction.Insert, Box, false, false);
            Assert.That(world.GetObject(Box).SlotId, Is.EqualTo(Machine));
            Assert.That(body.isKinematic, Is.True);
            Assert.That(Vector3.Distance(body.position, slot.position), Is.LessThan(0.001f));
            host.OperateMachine(Machine, ProductionAction.Eject, Guid.Empty, false, false);
            Assert.That(world.GetObject(Box).SlotId, Is.Null);
            Assert.That(body.isKinematic, Is.False);
            yield return null;
        }

        [UnityTest] public IEnumerator BlockedSlotCannotConsumeClaimOrCommandSequence()
        {
            var obstacle = GameObject.CreatePrimitive(PrimitiveType.Cube); obstacle.transform.SetParent(root.transform, false);
            obstacle.transform.position = slot.position;
            host.Grab(Box); long sequence = port.LastTerminalSequence;
            host.OperateMachine(Machine, ProductionAction.Insert, Box, false, false);
            Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor));
            Assert.That(world.Production.GetMachine(Machine).ContainerId, Is.Null);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(sequence));
            Assert.That(host.LastAction, Does.Contain("blocked"));
            yield return null;
        }

        [UnityTest] public IEnumerator RetryKeepsOneClaimWithoutAnotherLogicalCommit()
        {
            host.Grab(Box); long revision = world.View.Revision;
            host.ReplayLast();
            Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(world.View.ActiveClaimCount, Is.EqualTo(1));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(1));
            yield return null;
        }

        [UnityTest] public IEnumerator ShutdownClearsClaimsAndRestoresDynamicSlotBody()
        {
            host.Grab(Box); host.OperateMachine(Machine, ProductionAction.Insert, Box, false, false);
            Assert.That(body.isKinematic, Is.True);
            host.Shutdown(); host.Shutdown();
            Assert.That(body.isKinematic, Is.False);
            Assert.That(world.View.ActiveClaimCount, Is.Zero);
            Assert.That(world.View.RegisteredObjectCount, Is.Zero);
            Assert.That(host.BoundBodyCount, Is.Zero);
            yield return null;
        }

        [Test] public void ClockRegressionIsAnExplicitFailure()
        {
            clock = 1; host.Pump(); clock = 0.5;
            Assert.Throws<InvalidOperationException>(() => host.Pump());
            Assert.That(world.View.HostMilliseconds, Is.EqualTo(1000));
        }
    }
}
