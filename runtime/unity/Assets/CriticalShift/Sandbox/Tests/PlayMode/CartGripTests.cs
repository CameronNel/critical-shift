using System;
using System.Collections;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics;
using CriticalShift.Features.Interaction.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class CartGripTests
    {
        private GameObject root;
        private WorldSession world;
        private LocalCommandPort port;
        private LocalWorldHost host;
        private Rigidbody cart, box;
        private Transform actorRoot, stand;
        private Guid focus;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private Guid Actor => Id(1);
        private Guid Cart => Id(10);
        private Guid Box => Id(11);
        private sealed class FixtureAccess : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid target, InteractionKind kind) => AccessDecision.Allowed; }

        [SetUp] public void SetUp()
        {
            root = new GameObject("Cart grip regression fixture"); root.transform.position = new Vector3(2000, 1000, 2000);
            world = new WorldSession(new WorldSessionConfiguration(1, 60000), new FixtureAccess());
            world.RegisterConnection(Id(2), Actor); world.RegisterObject(Cart); world.RegisterObject(Box);
            port = new LocalCommandPort(world, Id(2)); host = root.AddComponent<LocalWorldHost>();
            host.Initialize(world, port, Actor, () => 0);
            actorRoot = Child("Actor root", root.transform, new Vector3(0, 0, -2)); host.BindActorRoot(Actor, actorRoot);
            var carry = Child("Carry target", actorRoot, new Vector3(0, 1.5f, 1.75f)); host.BindCarryTarget(Actor, carry);
            cart = Body("Cart", new Vector3(0, 1, 0)); cart.mass = 35;
            var handle = Child("Rear handle", cart.transform, new Vector3(0, 0.5f, -1.1f));
            stand = Child("Operator stance", cart.transform, new Vector3(0, -1, -2));
            host.BindCartHandle(Cart, cart, handle, stand);
            box = Body("Portable crate", new Vector3(3, 1, 0)); host.BindBody(Box, box);
            host.BindFocus(() => focus, id => "Cart fixture target"); focus = Cart;
        }

        private Transform Child(string name, Transform parent, Vector3 position)
        { var item = new GameObject(name); item.transform.SetParent(parent, false); item.transform.localPosition = position; return item.transform; }
        private Rigidbody Body(string name, Vector3 position)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube); item.name = name;
            item.transform.SetParent(root.transform, false); item.transform.localPosition = position;
            var body = item.AddComponent<Rigidbody>(); body.useGravity = false; return body;
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            if (host != null) host.Shutdown(); if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator CartHandleClaimDoesNotSpringCarryItsBody()
        {
            host.Activate(); Vector3 initial = cart.position; host.Grab(Cart);
            Assert.That(world.GetObject(Cart).HolderId, Is.EqualTo(Actor));
            Assert.That(host.IsHandleHeld(Cart), Is.True); Assert.That(host.CarriedPhysicalMass(), Is.Zero);
            Assert.That(host.CurrentGripStand().Value, Is.EqualTo(stand.position));
            var carry = actorRoot.Find("Carry target"); Quaternion rest = carry.localRotation;
            host.RotateHeld(new Vector2(120, 100));
            host.ThrowHeld(); Assert.That(world.GetObject(Cart).HolderId, Is.EqualTo(Actor));
            Assert.That(Quaternion.Angle(rest, carry.localRotation), Is.LessThan(0.01f));
            for (int i = 0; i < 15; i++) yield return new WaitForFixedUpdate();
            Assert.That(Vector3.Distance(cart.position, initial), Is.LessThan(0.01f));
            Assert.That(cart.isKinematic, Is.False);
        }

        [UnityTest] public IEnumerator HandleEntryRejectsWrongSideAndExcessiveCartSpeed()
        {
            host.Activate(); actorRoot.localPosition = new Vector3(0, 0, 2); host.Grab(Cart);
            Assert.That(world.GetObject(Cart).HolderId, Is.Null); Assert.That(port.LastTerminalSequence, Is.Zero);
            actorRoot.position = stand.position; cart.linearVelocity = Vector3.forward * 2; host.Grab(Cart);
            Assert.That(world.GetObject(Cart).HolderId, Is.Null); Assert.That(port.LastTerminalSequence, Is.Zero);
            cart.linearVelocity = Vector3.zero; host.Grab(Cart);
            Assert.That(world.GetObject(Cart).HolderId, Is.EqualTo(Actor)); yield return null;
        }

        [UnityTest] public IEnumerator LostGripProximityReleasesItsExactLease()
        {
            host.Activate(); host.Grab(Cart); actorRoot.localPosition = new Vector3(8, 0, -2);
            Assert.That(host.IsHandleHeld(Cart), Is.False);
            yield return new WaitForFixedUpdate(); yield return null;
            Assert.That(world.GetObject(Cart).HolderId, Is.Null);
            Assert.That(host.CurrentGripStand().HasValue, Is.False);
            Assert.That(actorRoot.localPosition.x, Is.EqualTo(8).Within(0.001f));
        }

        [UnityTest] public IEnumerator CartGripAndCrateCarryShareOneExclusiveActorClaim()
        {
            host.Activate(); host.Grab(Cart); host.Grab(Box);
            Assert.That(world.GetObject(Cart).HolderId, Is.EqualTo(Actor)); Assert.That(world.GetObject(Box).HolderId, Is.Null);
            host.DropHeld(); host.Grab(Box);
            Assert.That(world.GetObject(Cart).HolderId, Is.Null); Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor));
            yield return null;
        }

        [UnityTest] public IEnumerator ContextCartTransferReleasesCargoThenTakesAndDropsHandle()
        {
            host.Activate(); host.Grab(Box); host.TransferFocused();
            Assert.That(world.GetObject(Box).HolderId, Is.Null); Assert.That(world.GetObject(Cart).HolderId, Is.Null);
            host.TransferFocused(); Assert.That(world.GetObject(Cart).HolderId, Is.EqualTo(Actor));
            host.TransferFocused(); Assert.That(world.GetObject(Cart).HolderId, Is.Null);
            Assert.That(world.View.ActiveClaimCount, Is.Zero); yield return null;
        }

        [Test] public void OneRigidbodyCannotBeBothHandleAndCarriedEntity()
        {
            Guid alias = Id(12); world.RegisterObject(alias);
            Assert.Throws<InvalidOperationException>(() => host.BindBody(alias, cart));
            Assert.That(host.BoundBodyCount, Is.EqualTo(2));
        }

        [UnityTest] public IEnumerator CartMotorRequiresTheCurrentHandleLease()
        {
            var motor = cart.gameObject.AddComponent<CartMotor>(); motor.Initialize(() => host.IsHandleHeld(Cart), () => 0);
            host.Activate(); motor.SetDrive(1, 0, false); Vector3 initial = cart.position;
            for (int i = 0; i < 10; i++) yield return new WaitForFixedUpdate();
            Assert.That(Vector3.Distance(cart.position, initial), Is.LessThan(0.01f));
            host.Grab(Cart);
            for (int i = 0; i < 20; i++) yield return new WaitForFixedUpdate();
            Assert.That(cart.position.z, Is.GreaterThan(initial.z + 0.05f));
            host.DropHeld(); Assert.That(host.IsHandleHeld(Cart), Is.False);
            motor.SetDrive(1, 1, false); Assert.That(motor.HasDriveAuthority, Is.False); Assert.That(motor.Steering, Is.Zero);
        }
    }
}
