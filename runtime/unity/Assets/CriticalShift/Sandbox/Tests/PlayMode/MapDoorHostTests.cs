using System;
using System.Collections;
using System.Collections.Generic;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace CriticalShift.Sandbox.Tests
{
    public sealed class MapDoorHostTests
    {
        private GameObject root;
        private WorldSession world;
        private LocalCommandPort commands;
        private LocalWorldHost host;
        private MapDoorHost doors;
        private readonly List<Exception> faults = new List<Exception>();
        private int stops;
        private bool clear;
        private IReadOnlyList<DoorView> delivered;
        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        private sealed class FixtureAccess : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid target, InteractionKind kind) => AccessDecision.Allowed; }
        [SetUp] public void SetUp()
        {
            faults.Clear(); clear = true; stops = 0;
            root = new GameObject("Map door command-delivery fixture");
            world = new WorldSession(new WorldSessionConfiguration(18, 60000, true), new FixtureAccess());
            world.RegisterConnection(Id(1), Id(2)); world.RegisterObject(Id(4));
            world.Doors.Register(Id(3), "CONDENSER_W_ESCAPE", DoorState.Open, DoorState.Open);
            world.Doors.Register(Id(5), "REACTOR_BLAST", DoorState.Open, DoorState.Closed);
            commands = new LocalCommandPort(world, Id(1)); host = root.AddComponent<LocalWorldHost>();
            host.Initialize(world, commands, Id(2), () => 0, faults.Add);
            var carry = new GameObject("Explicit local carry target").transform; carry.SetParent(root.transform, false);
            host.BindCarryTarget(Id(2), carry); doors = root.AddComponent<MapDoorHost>();
            doors.Initialize(host, new[] { Id(3), Id(5) }, () => Id(3), state => delivered = state, () => stops++, id => clear);
            host.Activate(); doors.Activate();
        }
        [UnityTearDown] public IEnumerator TearDown()
        {
            if (doors != null) doors.Shutdown(); if (host != null) host.Shutdown();
            if (root != null) UnityEngine.Object.Destroy(root);
            yield return null; LogAssert.NoUnexpectedReceived(); Assert.That(faults, Is.Empty);
        }
        [Test] public void OccupiedClosingPreservesTheCommandStreamBeforeFreshDoorAndEvacuationCommits()
        {
            clear = false; doors.OperateFocused();
            Assert.That(commands.LastTerminalSequence, Is.Zero); Assert.That(world.Doors.Get(Id(3)).State, Is.EqualTo(DoorState.Open));
            Assert.That(doors.LastAction, Does.Contain("occupied"));
            clear = true; doors.OperateFocused();
            Assert.That(commands.LastTerminalSequence, Is.EqualTo(1)); Assert.That(delivered[0].State, Is.EqualTo(DoorState.Closed));
            long revision = world.Doors.Get(Id(3)).Revision;
            Assert.That(commands.ReplayLast().IsReplay, Is.True); Assert.That(world.Doors.Get(Id(3)).Revision, Is.EqualTo(revision));
            doors.BeginEvacuationExercise(); Assert.That(delivered[0].State, Is.EqualTo(DoorState.Open));
            Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Running));
            Guid cause = world.Doors.EvacuationCauseId.Value; doors.OperateFocused();
            Assert.That(delivered[0].State, Is.EqualTo(DoorState.Closed)); revision = delivered[0].Revision;
            doors.BeginEvacuationExercise();
            Assert.That(delivered[0].State, Is.EqualTo(DoorState.Closed)); Assert.That(delivered[0].Revision, Is.EqualTo(revision));
            Assert.That(world.Doors.EvacuationCauseId, Is.EqualTo(cause)); Assert.That(stops, Is.Zero);
        }
        [Test] public void UnexpectedDoorHostDisableStopsItsWorldAndReportsOneFailure()
        {
            Assert.That(commands.Grab(Id(4)).HasNewCommit, Is.True); doors.enabled = false;
            Assert.That(stops, Is.EqualTo(1)); Assert.That(world.View.Phase, Is.EqualTo(WorldPhase.Stopped));
            Assert.That(world.View.ActiveClaimCount, Is.Zero); Assert.That(world.Doors.Count, Is.Zero); Assert.That(doors.Focused, Is.Null);
            Assert.That(faults.Count, Is.EqualTo(1)); Assert.That(faults[0].Message, Does.Contain("live map door host was disabled")); faults.Clear();
            doors.Shutdown(); Assert.That(stops, Is.EqualTo(1));
        }
        [Test] public void OccupiedEvacuationClosureLeavesTheCauseAndAllDoorStatesUncommitted()
        {
            clear = false; doors.BeginEvacuationExercise();
            Assert.That(world.Doors.EvacuationCauseId, Is.Null);
            Assert.That(world.Doors.Get(Id(3)).Revision, Is.Zero); Assert.That(world.Doors.Get(Id(5)).Revision, Is.Zero);
            Assert.That(world.Doors.Get(Id(5)).State, Is.EqualTo(DoorState.Open));
            Assert.That(doors.LastAction, Does.Contain("clear REACTOR_BLAST"));
            Assert.That(commands.LastTerminalSequence, Is.Zero);
            clear = true; doors.BeginEvacuationExercise();
            Assert.That(world.Doors.EvacuationCauseId, Is.Not.Null);
            Assert.That(world.Doors.Get(Id(5)).State, Is.EqualTo(DoorState.Closed));
            Assert.That(delivered[1].State, Is.EqualTo(DoorState.Closed)); Assert.That(stops, Is.Zero);
            Assert.That(commands.OperateDoor(Id(5), DoorAction.Open).HasNewCommit, Is.True);
            clear = false; doors.BeginEvacuationExercise();
            Assert.That(doors.LastAction, Does.Contain("Duplicate"));
            Assert.That(delivered[1].State, Is.EqualTo(DoorState.Open), "A retry must not reapply defaults or depend on fresh closure observations.");
        }
    }
}
