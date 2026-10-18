using System;
using System.Collections.Generic;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Local door intents and projection delivery. Application owns every logical transition.</summary>
    [DisallowMultipleComponent]
    public sealed class MapDoorHost : MonoBehaviour
    {
        private LocalWorldHost host;
        private Guid[] doorIds;
        private Func<Guid> pick;
        private Func<Guid, bool> mayClose;
        private Action<IReadOnlyList<DoorView>> apply;
        private Action stopPhysical;
        private Guid evacuationCause;
        private double refreshAt;
        private bool active;
        public string LastAction { get; private set; } = "Look at a door and press E";
        public DoorView Focused => active ? host.Commands.GetDoor(pick()) : null;

        public void Initialize(LocalWorldHost worldHost, Guid[] ids, Func<Guid> focus,
            Action<IReadOnlyList<DoorView>> deliver, Action stop, Func<Guid, bool> closeClearance)
        {
            if (host != null || worldHost == null || worldHost.World == null || worldHost.World.View.Phase != WorldPhase.Setup ||
                ids == null || ids.Length == 0 || ids.Length > 128 ||
                focus == null || deliver == null || stop == null || closeClearance == null) throw new ArgumentException("Bind one local map door adapter.");
            var unique = new HashSet<Guid>();
            foreach (var id in ids) if (id == Guid.Empty || !unique.Add(id) || worldHost.World.Doors.Get(id) == null)
                throw new ArgumentException("Door bindings require unique registered logical IDs.");
            host = worldHost; doorIds = (Guid[])ids.Clone(); pick = focus; apply = deliver; stopPhysical = stop; mayClose = closeClearance;
        }

        public void Activate()
        {
            if (host == null || active || host.World.View.Phase != WorldPhase.Running)
                throw new InvalidOperationException("Activate map doors after world startup.");
            Deliver(); active = true;
        }

        public void OperateFocused()
        {
            if (!active) return;
            try
            {
                host.Pump(); if (!Running()) return;
                Physics.SyncTransforms(); var door = Focused;
                if (door == null) { LastAction = "Look at a nearby door"; return; }
                if (door.State == DoorState.Open && !mayClose(door.Id)) { LastAction = "Doorway occupied · clear the opening before closing"; return; }
                var reply = host.Commands.OperateDoor(door.Id, door.State == DoorState.Open ? DoorAction.Close : DoorAction.Open);
                LastAction = door.SourceId + ": " + (reply.Door == null ? reply.Status.ToString() : reply.Door.Status.ToString());
                Deliver();
            }
            catch (Exception exception) { Fail(exception); }
        }

        public void BeginEvacuationExercise()
        {
            if (!active) return;
            try
            {
                host.Pump(); if (!Running()) return;
                if (!host.World.Doors.EvacuationCauseId.HasValue)
                {
                    Physics.SyncTransforms();
                    foreach (var id in doorIds)
                    {
                        var door = host.World.Doors.Get(id) ?? throw new InvalidOperationException("A map door lost its logical binding.");
                        if (door.State == DoorState.Open && door.EvacuationState != DoorState.Open && !mayClose(id))
                        { LastAction = "Evacuation exercise waiting · clear " + door.SourceId + " before its blast door closes"; return; }
                    }
                }
                if (evacuationCause == Guid.Empty) evacuationCause = Guid.NewGuid();
                var result = host.World.BeginEvacuation(host.World.Epoch, evacuationCause);
                LastAction = "Evacuation exercise: " + result.Status + " · ladder route unavailable";
                Deliver();
            }
            catch (Exception exception) { Fail(exception); }
        }

        private bool Running()
        {
            var phase = host.World.View.Phase;
            if (phase == WorldPhase.Running) return true;
            LastAction = phase == WorldPhase.Paused ? "Resume the shift before operating doors" : "Shift ended · restart traversal";
            return false;
        }

        private void LateUpdate()
        {
            if (!active) return;
            try
            {
                var phase = host.World.View.Phase;
                if (phase != WorldPhase.Running && phase != WorldPhase.Paused) { Shutdown(); return; }
                if (Time.realtimeSinceStartupAsDouble < refreshAt) return;
                refreshAt = Time.realtimeSinceStartupAsDouble + 0.25; Deliver();
            }
            catch (Exception exception) { Fail(exception); }
        }

        private void Deliver()
        {
            var views = new DoorView[doorIds.Length];
            for (int i = 0; i < views.Length; i++)
                views[i] = host.World.Doors.Get(doorIds[i]) ?? throw new InvalidOperationException("A map door lost its logical binding.");
            apply(views);
        }
        private void Fail(Exception exception)
        {
            try { Shutdown(); }
            finally { host?.ReportExternalFailure(exception); }
        }
        public void Shutdown()
        {
            active = false;
            var stop = stopPhysical; stopPhysical = null; pick = null; apply = null; doorIds = null; mayClose = null;
            stop?.Invoke();
        }
        private void OnDisable()
        {
            if (active) Fail(new InvalidOperationException("The live map door host was disabled."));
            else Shutdown();
        }
        private void OnDestroy() => Shutdown();
    }
}
