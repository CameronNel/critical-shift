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
        private Guid focus;
        private static Guid Id(int number) => new Guid(number, 0, 0, new byte[8]);
        private Guid Box => Id(10);
        private Guid Actor => Id(20);
        private Guid Machine => Id(30);
        private Guid WetBox => Id(50);
        private Guid Reactor => Id(60);
        private Guid Fuel => Id(70);

        private sealed class AllowedFixtureAccess : IInteractionAccessPolicy
        {
            public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed;
        }

        [SetUp] public void SetUp()
        {
            clock = 0; focus = Guid.Empty; root = new GameObject("Local host regression fixture");
            root.transform.position = new Vector3(1000, 1000, 1000);
            world = new WorldSession(new WorldSessionConfiguration(1, 60000, true), new AllowedFixtureAccess());
            world.RegisterConnection(Id(1), Actor);
            world.Production.RegisterBatch(Box, Id(11), Id(12), Id(13), MaterialKind.Ore, 10);
            world.Production.RegisterBatch(WetBox, Id(51), Id(12), Id(53), MaterialKind.Ore, 10, moisture: 850);
            world.Production.RegisterMachine(Machine, new MachineRecipe(Id(31), MaterialKind.Ore, MaterialKind.CrushedOre,
                1000, 500, 100, 100, yieldPermille: 800));
            world.Production.RegisterBatch(Fuel, Id(71), Id(12), Id(73), MaterialKind.Fuel, 3);
            world.Reactor.Register(Reactor, new ReactorDefinition(Id(61), millisecondsPerFuelUnit: 1000,
                warningMilliseconds: 200, tripMilliseconds: 400, resetMilliseconds: 100));
            port = new LocalCommandPort(world, Id(1));
            host = root.AddComponent<LocalWorldHost>(); host.Initialize(world, port, Actor, () => clock);
            host.BindFocus(() => focus, id => "Fixture target");
            var crate = GameObject.CreatePrimitive(PrimitiveType.Cube); crate.transform.SetParent(root.transform, false);
            crate.transform.localPosition = new Vector3(0, 1, 0);
            body = crate.AddComponent<Rigidbody>(); body.useGravity = false;
            target = new GameObject("Carry target").transform; target.SetParent(root.transform, false); target.localPosition = new Vector3(0, 1, 1);
            slot = new GameObject("Machine slot").transform; slot.SetParent(root.transform, false); slot.localPosition = new Vector3(3, 1, 0);
            host.BindBody(Box, body, 0.5f); host.BindCarryTarget(Actor, target); host.BindSlot(Machine, slot);
            var wet = GameObject.CreatePrimitive(PrimitiveType.Cube); wet.transform.SetParent(root.transform, false);
            wet.transform.localPosition = new Vector3(-3, 1, 0);
            var wetBody = wet.AddComponent<Rigidbody>(); wetBody.useGravity = false; host.BindBody(WetBox, wetBody, 0.5f);
            var fuel = GameObject.CreatePrimitive(PrimitiveType.Cube); fuel.transform.SetParent(root.transform, false);
            fuel.transform.localPosition = new Vector3(6, 1, 0);
            var fuelBody = fuel.AddComponent<Rigidbody>(); fuelBody.useGravity = false; host.BindBody(Fuel, fuelBody, 0.5f);
            var fuelSlot = new GameObject("Reactor loading slot").transform; fuelSlot.SetParent(root.transform, false);
            fuelSlot.localPosition = new Vector3(6, 1, 2); host.BindSlot(Reactor, fuelSlot);
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

        [UnityTest] public IEnumerator RotatingHeldCrateUsesTorqueWithoutAnotherLogicalMutation()
        {
            host.Grab(Box); var claim = world.GetObject(Box); Quaternion before = body.rotation;
            long sequence = port.LastTerminalSequence; host.RotateHeld(new Vector2(120, 40));
            Assert.That(Quaternion.Angle(before, body.rotation), Is.LessThan(0.01f), "Input changes the force target, not the body pose.");
            Assert.That(Quaternion.Angle(Quaternion.identity, target.localRotation), Is.GreaterThan(30));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(sequence));
            for (int i = 0; i < 100; i++) yield return new WaitForFixedUpdate();
            Assert.That(Quaternion.Angle(before, body.rotation), Is.GreaterThan(20));
            Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor));
            Assert.That(world.GetObject(Box).LeaseGeneration, Is.EqualTo(claim.LeaseGeneration));
            Assert.That(world.Production.GetBatch(Box).Units, Is.EqualTo(10)); Assert.That(body.isKinematic, Is.False);
        }

        [UnityTest] public IEnumerator CarryRotationStopsDuringPauseAndResetsAcrossReleaseLeaseAndTeardown()
        {
            Quaternion rest = target.localRotation;
            host.Grab(Box); host.RotateHeld(new Vector2(100, 100)); Quaternion paused = target.localRotation;
            world.Pause(world.Epoch); host.RotateHeld(new Vector2(100, -100));
            Assert.That(Quaternion.Angle(paused, target.localRotation), Is.LessThan(0.01f));
            host.Release(Box); Assert.That(Quaternion.Angle(rest, target.localRotation), Is.LessThan(0.01f));
            world.Resume(world.Epoch); host.Grab(WetBox);
            Assert.That(Quaternion.Angle(rest, target.localRotation), Is.LessThan(0.01f));
            host.RotateHeld(new Vector2(-100, 0)); Assert.That(Quaternion.Angle(rest, target.localRotation), Is.GreaterThan(20));
            host.Shutdown(); Assert.That(Quaternion.Angle(rest, target.localRotation), Is.LessThan(0.01f));
            Assert.That(world.View.ActiveClaimCount, Is.Zero); yield return null;
        }

        [UnityTest] public IEnumerator ThrowReleasesOnceAndReplayCannotApplyAnotherImpulse()
        {
            host.Grab(Box); host.RotateHeld(new Vector2(120, 0)); host.ThrowHeld();
            Assert.That(world.GetObject(Box).HolderId, Is.Null); Assert.That(world.View.ActiveClaimCount, Is.Zero);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2)); Assert.That(body.isKinematic, Is.False);
            for (int i = 0; i < 3; i++) yield return new WaitForFixedUpdate();
            Vector3 once = body.linearVelocity;
            Assert.That(once.magnitude, Is.InRange(0.5f, 5.1f)); Assert.That(once.z, Is.GreaterThan(0.5f));
            Assert.That(Mathf.Abs(once.x), Is.LessThan(0.01f), "Crate orientation must not rotate the worker's throw aim.");
            host.ReplayLast(); host.ReplayLast(); host.ThrowHeld();
            for (int i = 0; i < 3; i++) yield return new WaitForFixedUpdate();
            Assert.That(Vector3.Distance(once, body.linearVelocity), Is.LessThan(0.01f));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(2)); Assert.That(world.Production.GetBatch(Box).Units, Is.EqualTo(10));
        }

        [UnityTest] public IEnumerator PausedOrExpiredGripCannotLaunchItsFormerCrate()
        {
            host.Grab(Box); world.Pause(world.Epoch); host.ThrowHeld();
            Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor)); Assert.That(port.LastTerminalSequence, Is.EqualTo(1));
            world.Resume(world.Epoch); clock = 3; host.ThrowHeld();
            Assert.That(world.GetObject(Box).HolderId, Is.Null); Assert.That(port.LastTerminalSequence, Is.EqualTo(1));
            for (int i = 0; i < 3; i++) yield return new WaitForFixedUpdate();
            Assert.That(body.linearVelocity.magnitude, Is.LessThan(0.01f));
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

        [UnityTest] public IEnumerator ContextTransferUsesTheSameClaimAndSlotCommands()
        {
            focus = Box; host.TransferFocused();
            Assert.That(world.GetObject(Box).HolderId, Is.EqualTo(Actor));
            focus = Machine; host.TransferFocused();
            Assert.That(world.GetObject(Box).SlotId, Is.EqualTo(Machine));
            focus = Box; host.TransferFocused(); // Looking at the loaded crate resolves its equipment slot.
            Assert.That(world.GetObject(Box).SlotId, Is.Null);
            Assert.That(body.isKinematic, Is.False);
            Assert.That(port.LastTerminalSequence, Is.EqualTo(3));
            yield return null;
        }

        [UnityTest] public IEnumerator ContextPowerAndStartUseCurrentMachineRevision()
        {
            host.Grab(Box); host.OperateMachine(Machine, ProductionAction.Insert, Box, false, false);
            focus = Machine; host.ToggleFocusedPower(); host.StartFocused();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.Processing));
            clock = 1; host.Pump();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.OutputReady));
            Assert.That(world.Production.GetBatch(Box).Kind, Is.EqualTo(MaterialKind.CrushedOre));
            yield return null;
        }

        [UnityTest] public IEnumerator ContextDropRemainsAvailableDuringProcessPause()
        {
            host.Grab(Box); world.Pause(world.Epoch); host.DropHeld();
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Paused));
            Assert.That(world.GetObject(Box).HolderId, Is.Null);
            Assert.That(world.View.ActiveClaimCount, Is.Zero);
            yield return null;
        }

        [UnityTest] public IEnumerator PhysicalMassTracksCommittedConversionOutput()
        {
            Assert.That(body.mass, Is.EqualTo(5).Within(0.001f));
            host.Grab(Box); host.OperateMachine(Machine, ProductionAction.Insert, Box, false, false);
            host.OperateMachine(Machine, ProductionAction.SetPower, Guid.Empty, false, true);
            host.OperateMachine(Machine, ProductionAction.Start, Guid.Empty, false, false);
            clock = 1; host.Pump();
            Assert.That(world.Production.GetBatch(Box).Units, Is.EqualTo(8));
            Assert.That(body.mass, Is.EqualTo(4).Within(0.001f));
            Assert.That(world.Production.Summary.ActiveUnits + world.Production.Summary.WasteUnits,
                Is.EqualTo(world.Production.Summary.IssuedUnits));
            yield return null;
        }

        [UnityTest] public IEnumerator ContextBypassJamRequiresPowerIsolationBeforeRepairAndResume()
        {
            host.Grab(WetBox); focus = Machine; host.TransferFocused(); host.ToggleFocusedPower(); host.BypassFocused();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.Processing));
            clock = 0.15; host.Pump(); Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.Jammed));
            host.StartFocused(); Assert.That(host.LastAction, Is.EqualTo("PowerMustBeOff"));
            Assert.That(world.GetObject(WetBox).SlotId, Is.EqualTo(Machine));
            host.ToggleFocusedPower(); host.StartFocused();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.PowerPaused));
            host.ToggleFocusedPower(); host.StartFocused();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.Processing));
            clock = 1; host.Pump();
            var output = world.Production.GetBatch(WetBox);
            Assert.That(output.Kind, Is.EqualTo(MaterialKind.CrushedOre)); Assert.That(output.Units, Is.EqualTo(8));
            Assert.That(output.Flags, Is.EqualTo(MaterialFlags.BypassedInspection)); Assert.That(output.CauseId, Is.EqualTo(Id(53)));
            yield return null;
        }

        [UnityTest] public IEnumerator ContextResumeRetainsTheSameCycleAndCommittedWork()
        {
            host.Grab(Box); focus = Machine; host.TransferFocused(); host.ToggleFocusedPower(); host.StartFocused();
            var cycle = world.Production.GetMachine(Machine).CycleId;
            clock = 0.25; host.Pump(); host.ToggleFocusedPower(); host.ToggleFocusedPower(); host.StartFocused();
            var resumed = world.Production.GetMachine(Machine);
            Assert.That(resumed.Mode, Is.EqualTo(ProductionMode.Processing)); Assert.That(resumed.CycleId, Is.EqualTo(cycle));
            Assert.That(resumed.WorkMilliseconds, Is.EqualTo(250));
            clock = 1.25; host.Pump();
            Assert.That(world.Production.GetMachine(Machine).Mode, Is.EqualTo(ProductionMode.OutputReady));
            Assert.That(world.Production.GetBatch(Box).Units, Is.EqualTo(8)); yield return null;
        }

        [UnityTest] public IEnumerator FocusedEmergencyCoolingSpendsOnceAndTripResetDoesNotRestartTheCore()
        {
            host.Grab(Fuel); focus = Reactor; host.TransferFocused(); host.ToggleFocusedPower(); host.StartFocused();
            Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Running));
            host.ToggleFocusedPower(); clock = 0.4; host.Pump();
            Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Tripped));
            host.StartFocused(); Assert.That(host.LastAction, Is.EqualTo("Unsafe"));
            long spent = world.Reactor.PowerSummary.Spent;
            host.EmergencyCoolingFocused();
            Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(spent + 4));
            Assert.That(world.Reactor.View.Cooling, Is.True);
            host.ReplayLast(); Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(spent + 4));
            host.StartFocused(); Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Shutdown));
            long work = world.Reactor.View.WorkMilliseconds;
            host.StartFocused(); Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Running));
            host.ShutdownFocused(); Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Shutdown));
            Assert.That(world.Reactor.View.WorkMilliseconds, Is.EqualTo(work)); yield return null;
        }

        [UnityTest] public IEnumerator FocusedReactorControlsRespectTargetAndProcessPause()
        {
            focus = Machine; long sequence = port.LastTerminalSequence, spent = world.Reactor.PowerSummary.Spent;
            host.EmergencyCoolingFocused(); host.ShutdownFocused();
            Assert.That(port.LastTerminalSequence, Is.EqualTo(sequence));
            Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(spent));
            focus = Reactor; world.Pause(world.Epoch);
            host.EmergencyCoolingFocused(); host.ShutdownFocused(); host.StartFocused();
            Assert.That(port.LastTerminalSequence, Is.EqualTo(sequence));
            Assert.That(world.Reactor.View.Mode, Is.EqualTo(ReactorMode.Empty));
            world.Resume(world.Epoch); host.EmergencyCoolingFocused();
            Assert.That(host.LastAction, Is.EqualTo("InvalidState"));
            Assert.That(port.LastTerminalSequence, Is.EqualTo(sequence + 1));
            Assert.That(world.Reactor.PowerSummary.Spent, Is.EqualTo(spent)); yield return null;
        }
    }
}
