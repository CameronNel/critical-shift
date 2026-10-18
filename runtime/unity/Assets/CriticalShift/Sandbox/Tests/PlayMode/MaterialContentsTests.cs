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
    public sealed class MaterialContentsTests
    {
        private GameObject root;
        private Material material;
        private WorldSession world;
        private LocalCommandPort commands;
        private MaterialContainerFeedback ore, fuel;
        private Transform[] fuelMarkers;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private sealed class FixtureAccess : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }

        [SetUp] public void SetUp()
        {
            root = new GameObject("Material contents presentation fixture"); root.transform.position = new Vector3(4500, 1000, 4500);
            var pipeline = QualitySettings.renderPipeline != null ? QualitySettings.renderPipeline : GraphicsSettings.defaultRenderPipeline;
            var shader = Shader.Find(pipeline == null ? "Standard" : "Universal Render Pipeline/Lit");
            Assert.That(shader, Is.Not.Null); material = new Material(shader);
            world = new WorldSession(new WorldSessionConfiguration(7, 20000, true), new FixtureAccess());
            world.RegisterConnection(Id(2), Id(1));
            world.Production.RegisterBatch(Id(10), Id(110), Id(120), Id(130), MaterialKind.Ore, 10);
            world.Production.RegisterBatch(Id(11), Id(111), Id(120), Id(131), MaterialKind.Fuel, 2);
            world.Production.RegisterMachine(Id(20), new MachineRecipe(Id(500), MaterialKind.Ore, MaterialKind.CrushedOre,
                1000, 500, 100, 100, yieldPermille: 800));
            world.Reactor.Register(Id(30), new ReactorDefinition(Id(501), millisecondsPerFuelUnit: 1000));
            commands = new LocalCommandPort(world, Id(2));
            ore = root.AddComponent<MaterialContainerFeedback>();
            ore.Initialize(commands, Id(10), Visual("Ore status").GetComponent<Renderer>(), Markers("Ore"), 10);
            fuel = root.AddComponent<MaterialContainerFeedback>(); fuelMarkers = Markers("Fuel");
            fuel.Initialize(commands, Id(11), Visual("Fuel status").GetComponent<Renderer>(), fuelMarkers, 2);
            world.Start();
        }

        private Transform Visual(string name)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube); item.name = name; item.transform.SetParent(root.transform, false);
            item.GetComponent<Renderer>().sharedMaterial = material;
            item.GetComponent<Collider>().enabled = false; UnityEngine.Object.Destroy(item.GetComponent<Collider>());
            item.transform.localScale = new Vector3(0.3f, 0.28f, 0.3f); return item.transform;
        }
        private Transform[] Markers(string name)
        {
            var markers = new Transform[8];
            for (int i = 0; i < markers.Length; i++)
            { markers[i] = Visual(name + i); markers[i].localPosition = new Vector3(i % 2 * 0.48f - 0.24f, i < 4 ? -0.22f : 0.1f, i % 4 < 2 ? -0.24f : 0.24f); }
            return markers;
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            world?.Stop(); if (root != null) UnityEngine.Object.Destroy(root); if (material != null) UnityEngine.Object.Destroy(material);
            yield return null; LogAssert.NoUnexpectedReceived();
        }

        [UnityTest] public IEnumerator ConversionUpdatesTheExistingVisiblePileWithoutAnotherMaterialCommit()
        {
            yield return null; yield return null;
            Assert.That(ore.VisibleContentCount, Is.EqualTo(8)); Assert.That(ore.DisplayedFill, Is.EqualTo(1));
            commands.Grab(Id(10)); commands.OperateMachine(Id(20), ProductionAction.Insert, Id(10));
            commands.OperateMachine(Id(20), ProductionAction.SetPower, powered: true); commands.OperateMachine(Id(20), ProductionAction.Start);
            world.AdvanceTo(1000); var batch = commands.GetBatch(Id(10)); long revision = world.View.Revision;
            yield return null; yield return null;
            Assert.That(batch.Kind, Is.EqualTo(MaterialKind.CrushedOre)); Assert.That(batch.Units, Is.EqualTo(8));
            Assert.That(ore.DisplayedFill, Is.EqualTo(0.8f).Within(0.001f)); Assert.That(ore.VisibleContentCount, Is.EqualTo(7));
            Assert.That(commands.GetBatch(Id(10)).BatchId, Is.EqualTo(batch.BatchId)); Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(root.GetComponentsInChildren<Rigidbody>().Length, Is.Zero); Assert.That(root.GetComponentsInChildren<Collider>().Length, Is.Zero);
        }

        [UnityTest] public IEnumerator ExhaustionShowsSpentFuelWithoutDeletingItsAccountedQuantity()
        {
            commands.Grab(Id(11)); commands.OperateReactor(Id(30), ReactorAction.Insert, Id(11));
            commands.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: true); commands.OperateReactor(Id(30), ReactorAction.Start);
            yield return null; yield return null;
            var properties = new MaterialPropertyBlock(); fuelMarkers[0].GetComponent<Renderer>().GetPropertyBlock(properties);
            string colorProperty = material.HasProperty("_BaseColor") ? "_BaseColor" : "_Color";
            Color before = properties.GetColor(colorProperty);
            world.AdvanceTo(2000); long revision = world.View.Revision;
            yield return null; yield return null;
            Assert.That(commands.Reactor.Mode, Is.EqualTo(ReactorMode.Exhausted));
            Assert.That(commands.GetBatch(Id(11)).Kind, Is.EqualTo(MaterialKind.SpentFuel)); Assert.That(commands.GetBatch(Id(11)).Units, Is.EqualTo(2));
            Assert.That(fuel.VisibleContentCount, Is.EqualTo(8)); Assert.That(fuel.DisplayedFill, Is.EqualTo(1));
            fuelMarkers[0].GetComponent<Renderer>().GetPropertyBlock(properties); Assert.That(properties.GetColor(colorProperty), Is.Not.EqualTo(before));
            Assert.That(world.View.Revision, Is.EqualTo(revision));
        }

        [UnityTest] public IEnumerator PausedReenableRebuildsTheProjectionAndStoppedWorldHidesThePile()
        {
            yield return null; yield return null; int objects = root.transform.childCount;
            world.Pause(world.Epoch); long revision = world.View.Revision;
            ore.enabled = false; Assert.That(ore.VisibleContentCount, Is.Zero); ore.enabled = true;
            yield return null; yield return null;
            Assert.That(ore.VisibleContentCount, Is.EqualTo(8)); Assert.That(world.View.Revision, Is.EqualTo(revision));
            Assert.That(root.transform.childCount, Is.EqualTo(objects));
            world.Stop(); yield return null; yield return null;
            Assert.That(ore.VisibleContentCount, Is.Zero); Assert.That(fuel.VisibleContentCount, Is.Zero);
            foreach (var marker in fuelMarkers) Assert.That(marker.GetComponent<Renderer>().enabled, Is.False);
        }
    }
}
