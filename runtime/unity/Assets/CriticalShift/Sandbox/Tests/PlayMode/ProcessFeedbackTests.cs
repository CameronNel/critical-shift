using System;
using System.Collections;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class ProcessFeedbackTests
    {
        private GameObject root;
        private Material material;
        private WorldSession world;
        private LocalCommandPort commands;
        private MachineFeedback machine;
        private ReactorFeedback reactor;
        private Light reactorLamp;
        private Transform[] sparks;
        private Transform fuelNeedle;
        private Transform ram;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private sealed class FixtureAccess : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }

        [SetUp] public void SetUp()
        {
            root = new GameObject("Source-backed process presentation fixture"); root.transform.position = new Vector3(3500, 1000, 3500);
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); material = new Material(shader);
            world = new WorldSession(new WorldSessionConfiguration(7, 20000, true), new FixtureAccess());
            world.RegisterConnection(Id(2), Id(1));
            world.Production.RegisterBatch(Id(10), Id(110), Id(120), Id(130), MaterialKind.Ore, 10);
            world.Production.RegisterBatch(Id(11), Id(111), Id(120), Id(131), MaterialKind.Fuel, 3);
            world.Production.RegisterMachine(Id(20), new MachineRecipe(Id(500), MaterialKind.Ore, MaterialKind.CrushedOre, 1000, 500, 100, 100));
            world.Reactor.Register(Id(30), new ReactorDefinition(Id(501), millisecondsPerFuelUnit: 1000,
                powerQuantumMilliseconds: 100, warningMilliseconds: 200, tripMilliseconds: 400));
            commands = new LocalCommandPort(world, Id(2));
            var face = Visual("Machine face", root.transform); var rotor = Child("Spindle"); var fill = Visual("Gauge fill", root.transform);
            sparks = Markers("Spark", 8);
            machine = root.AddComponent<MachineFeedback>();
            ram = Child("Process ram"); var clamps = new[] { Child("Left clamp"), Child("Right clamp") };
            clamps[0].localPosition = Vector3.left * 0.55f; clamps[1].localPosition = Vector3.right * 0.55f;
            machine.Initialize(commands, Id(20), face.GetComponent<Renderer>(), Child("Machine lamp").gameObject.AddComponent<Light>(),
                rotor, fill, sparks, Child("Power switch"), ram, clamps);
            var shell = Visual("Reactor face", root.transform); reactorLamp = Child("Reactor lamp").gameObject.AddComponent<Light>();
            reactor = root.AddComponent<ReactorFeedback>();
            fuelNeedle = Child("Fuel needle");
            reactor.Initialize(commands, shell.GetComponent<Renderer>(), reactorLamp, Child("Valve"), Markers("Vent mote", 6),
                fuelNeedle, Child("Reserve needle"));
            world.Start();
        }

        private Transform Child(string name)
        { var child = new GameObject(name); child.transform.SetParent(root.transform, false); return child.transform; }
        private Transform Visual(string name, Transform parent)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube); item.name = name; item.transform.SetParent(parent, false);
            item.GetComponent<Collider>().enabled = false; UnityEngine.Object.Destroy(item.GetComponent<Collider>());
            item.GetComponent<Renderer>().sharedMaterial = material; item.transform.localScale = Vector3.one * 0.1f; return item.transform;
        }
        private Transform[] Markers(string prefix, int count)
        {
            var origin = Child(prefix + " origin"); var items = new Transform[count];
            for (int i = 0; i < count; i++) items[i] = Visual(prefix + i, origin);
            return items;
        }

        [UnityTearDown] public IEnumerator TearDown()
        {
            world?.Stop(); if (root != null) UnityEngine.Object.Destroy(root); if (material != null) UnityEngine.Object.Destroy(material);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        private void StartMachine()
        {
            Assert.That(commands.Grab(Id(10)).HasNewCommit, Is.True);
            Assert.That(commands.OperateMachine(Id(20), ProductionAction.Insert, Id(10)).HasNewCommit, Is.True);
            Assert.That(commands.OperateMachine(Id(20), ProductionAction.SetPower, powered: true).HasNewCommit, Is.True);
            Assert.That(commands.OperateMachine(Id(20), ProductionAction.Start).HasNewCommit, Is.True);
        }

        [Test] public void ReactorVisualSetupRejectsHiddenMotionBodiesAndNestedPartsBeforeBinding()
        {
            var candidate = root.AddComponent<ReactorFeedback>(); candidate.enabled = false;
            var shell = Visual("Candidate reactor face", root.transform).GetComponent<Renderer>();
            var lamp = Child("Candidate lamp").gameObject.AddComponent<Light>();
            var valve = Child("Candidate valve"); var fuel = Child("Candidate fuel needle"); var reserve = Child("Candidate reserve needle");
            var vents = Markers("Candidate vent", 6);
            var hidden = new GameObject("Unexpected hidden motion body"); hidden.transform.SetParent(valve, false);
            hidden.AddComponent<Rigidbody>().isKinematic = true; hidden.SetActive(false);
            long revision = world.View.Revision;
            Assert.Throws<ArgumentException>(() => candidate.Initialize(commands, shell, lamp, valve, vents, fuel, reserve));
            valve = Child("Clean candidate valve"); fuel.SetParent(valve, false);
            Assert.Throws<ArgumentException>(() => candidate.Initialize(commands, shell, lamp, valve, vents, fuel, reserve));
            fuel.SetParent(root.transform, false);
            var contact = reserve.gameObject.AddComponent<BoxCollider>();
            Assert.Throws<ArgumentException>(() => candidate.Initialize(commands, shell, lamp, valve, vents, fuel, reserve));
            contact.enabled = false;
            candidate.Initialize(commands, shell, lamp, valve, vents, fuel, reserve);
            Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(candidate.VisibleMoteCount, Is.Zero);
        }

        [UnityTest] public IEnumerator PowerPauseStopsSparksAndPreservesCommittedProgress()
        {
            StartMachine(); world.AdvanceTo(250); yield return null; yield return null;
            Assert.That(machine.DisplayedProgress, Is.EqualTo(0.25f).Within(0.001f)); Assert.That(machine.VisibleMoteCount, Is.EqualTo(8));
            Vector3 committedRam = ram.localPosition; Assert.That(committedRam.y, Is.LessThan(-0.01f));
            commands.OperateMachine(Id(20), ProductionAction.SetPower, powered: false); world.AdvanceTo(4000);
            long revision = world.View.Revision; yield return null; yield return null;
            Assert.That(machine.DisplayedProgress, Is.EqualTo(0.25f).Within(0.001f)); Assert.That(machine.VisibleMoteCount, Is.Zero);
            Assert.That(commands.GetMachine(Id(20)).Mode, Is.EqualTo(ProductionMode.PowerPaused));
            Assert.That(ram.localPosition, Is.EqualTo(committedRam));
            Assert.That(world.View.Revision, Is.EqualTo(revision), "Rendering must not write gameplay state.");
        }

        [UnityTest] public IEnumerator CosmeticTrajectoryUsesPausedProcessTimeInsteadOfFrameTime()
        {
            StartMachine(); world.AdvanceTo(250); yield return null; yield return null;
            var positions = new Vector3[sparks.Length];
            Vector3 pausedRam = ram.localPosition;
            for (int i = 0; i < sparks.Length; i++) positions[i] = sparks[i].localPosition;
            world.Pause(world.Epoch); world.AdvanceTo(5000);
            for (int i = 0; i < 10; i++) yield return null;
            Assert.That(machine.VisibleMoteCount, Is.EqualTo(8));
            for (int i = 0; i < sparks.Length; i++) Assert.That(sparks[i].localPosition, Is.EqualTo(positions[i]));
            Assert.That(commands.GetMachine(Id(20)).WorkMilliseconds, Is.EqualTo(250));
            Assert.That(ram.localPosition, Is.EqualTo(pausedRam));
        }

        [UnityTest] public IEnumerator CoolingLossAndTripChangeVentFeedbackWithoutSpendingPower()
        {
            commands.Grab(Id(11)); commands.OperateReactor(Id(30), ReactorAction.Insert, Id(11));
            commands.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: true); commands.OperateReactor(Id(30), ReactorAction.Start);
            world.AdvanceTo(200); yield return null; yield return null;
            Assert.That(commands.Reactor.Mode, Is.EqualTo(ReactorMode.Running)); Assert.That(reactor.VisibleMoteCount, Is.EqualTo(2));
            commands.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: false); world.AdvanceTo(500);
            yield return null; yield return null;
            Assert.That(reactor.VisibleMoteCount, Is.EqualTo(6)); Assert.That(reactorLamp.color.r, Is.GreaterThan(reactorLamp.color.g));
            world.AdvanceTo(700); long reserve = commands.Power.Available; long spent = commands.Power.Spent;
            yield return null; yield return null;
            Assert.That(commands.Reactor.Mode, Is.EqualTo(ReactorMode.Tripped)); Assert.That(reactor.VisibleMoteCount, Is.EqualTo(6));
            Assert.That(commands.Power.Available, Is.EqualTo(reserve)); Assert.That(commands.Power.Spent, Is.EqualTo(spent));
        }

        [UnityTest] public IEnumerator ReactorInstrumentsFollowCommittedFuelAndReserveAcrossPauseAndStop()
        {
            commands.Grab(Id(11)); commands.OperateReactor(Id(30), ReactorAction.Insert, Id(11));
            commands.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: true); commands.OperateReactor(Id(30), ReactorAction.Start);
            world.AdvanceTo(1000); yield return null; yield return null;
            Assert.That(reactor.DisplayedFuelFraction, Is.EqualTo(2f / 3).Within(0.001f));
            Assert.That(reactor.DisplayedReserveFraction,
                Is.EqualTo((float)commands.Power.Available / commands.Power.Capacity).Within(0.001f));
            world.Pause(world.Epoch); world.AdvanceTo(5000);
            long revision = world.View.Revision, spent = commands.Power.Spent;
            for (int i = 0; i < 10; i++) yield return null;
            Assert.That(reactor.DisplayedFuelFraction, Is.EqualTo(2f / 3).Within(0.001f));
            Assert.That(Quaternion.Angle(Quaternion.identity, fuelNeedle.localRotation), Is.GreaterThan(1));
            Assert.That(world.View.Revision, Is.EqualTo(revision)); Assert.That(commands.Power.Spent, Is.EqualTo(spent));
            world.Stop(); yield return null; yield return null;
            Assert.That(reactor.DisplayedFuelFraction, Is.Zero); Assert.That(reactor.DisplayedReserveFraction, Is.Zero);
            Assert.That(reactor.VisibleMoteCount, Is.Zero);
        }
    }
}
