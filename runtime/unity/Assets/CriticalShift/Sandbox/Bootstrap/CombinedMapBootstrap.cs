using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Presentation;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    /// <summary>Explicit composition of the provisional combined-map traversal derivative.</summary>
    [DisallowMultipleComponent]
    public sealed class CombinedMapBootstrap : MonoBehaviour
    {
        [SerializeField] private CombinedMapAuthoring mapTemplate;
        [SerializeField] private Shader fixtureShader;
        [SerializeField] private Material fixtureLitTemplate, fixtureEmissionTemplate;
        private GameObject owned;
        private WorldSession world;
        private LocalWorldHost host;
        private LocalWorkerStateHost worker;
        private MapDoorHost doorHost;
        private CombinedMapDoorBindings physicalDoors;
        private PhysicsSafetyMonitor safety;
        private SpatialInteractionAccess access;
        private WorkerRecoveryRegistry recovery;
        private SandboxPrimitives palette;
        private bool started, resetRequested;
        public WorldSessionView World => world == null ? null : world.View;

        public void Configure(CombinedMapAuthoring template, Shader shader, Material litTemplate = null, Material emissionTemplate = null)
        {
            if (started || template == null || shader == null || !template.transform.IsChildOf(transform))
                throw new ArgumentException("Configure the generated map template before startup.");
            if (litTemplate != null || emissionTemplate != null)
                SandboxPrimitives.ValidateMaterialTemplates(shader, litTemplate, emissionTemplate);
            mapTemplate = template; fixtureShader = shader;
            fixtureLitTemplate = litTemplate; fixtureEmissionTemplate = emissionTemplate;
        }
        public static Guid DoorIdentity(string sourceId)
        {
            if (string.IsNullOrWhiteSpace(sourceId)) throw new ArgumentException("A map door source identity is required.");
            using (var digest = SHA256.Create())
            {
                byte[] hash = digest.ComputeHash(Encoding.UTF8.GetBytes("critical-shift/combined-map/door/v1/" + sourceId));
                byte[] identity = new byte[16]; Array.Copy(hash, identity, identity.Length); return new Guid(identity);
            }
        }
        private void Start() { started = true; StartWorld(); }
        private void OnEnable() { if (started && owned == null) StartWorld(); }
        private void LateUpdate()
        {
            if (!resetRequested) return;
            resetRequested = false; StopWorld(); StartWorld();
        }
        private void StartWorld()
        {
            try
            {
                if (mapTemplate == null || fixtureShader == null) throw new InvalidOperationException("Generate the combined-map traversal scene first.");
                owned = new GameObject("Combined map traversal world"); owned.transform.SetParent(transform, false);
                var model = Instantiate(mapTemplate, owned.transform); model.name = "Combined map collision derivative"; model.gameObject.SetActive(true);
                palette = new SandboxPrimitives(fixtureShader, fixtureLitTemplate, fixtureEmissionTemplate); recovery = new WorkerRecoveryRegistry();
                access = new SpatialInteractionAccess(3.2f, includeRegisteredTriggersInFocus: true);
                world = new WorldSession(new WorldSessionConfiguration(7, 720000, true), access, recovery);
                Guid actor = new Guid(9001, 0, 0, new byte[8]), connection = new Guid(9002, 0, 0, new byte[8]);
                world.RegisterConnection(connection, actor); var commands = new LocalCommandPort(world, connection);
                host = owned.AddComponent<LocalWorldHost>(); host.Initialize(world, commands, actor);
                safety = model.gameObject.AddComponent<PhysicsSafetyMonitor>();
                safety.Initialize(model.transform, model.LocalSafetyBounds,
                    maximumLinearSpeed: 25, maximumRotationalEnergyPerMass: 312.5,
                    () => world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused, host.ReportExternalFailure);
                physicalDoors = model.gameObject.AddComponent<CombinedMapDoorBindings>();
                var bindings = model.CopyDoorReferences(); var ids = new Guid[bindings.Length];
                var physical = new DoorCollisionBinding[bindings.Length];
                for (int i = 0; i < bindings.Length; i++)
                {
                    var binding = bindings[i]; var definition = binding.definition; Guid id = DoorIdentity(definition.id); ids[i] = id;
                    world.Doors.Register(id, definition.id, State(definition.state), State(definition.evac_state), definition.id != "DOCK_P2");
                    access.BindTarget(id, binding.anchor.parent, binding.interactionPoint);
                    physical[i] = new DoorCollisionBinding(Project(world.Doors.Get(id)), binding.anchor, binding.blocker, binding.threshold);
                }
                physicalDoors.Initialize(world.Epoch, physical, host.ReportExternalFailure);
                var player = SandboxPrimitives.Empty("Combined map worker", owned.transform, Vector3.zero);
                player.transform.position = model.StartPoint;
                var controller = SandboxWorkerRigBuilder.AddController(player);
                var eyes = SandboxPrimitives.Empty("Worker eyes", player.transform, new Vector3(0, 1.55f, 0));
                var camera = eyes.AddComponent<Camera>(); camera.nearClipPlane = 0.05f; camera.farClipPlane = 180; camera.fieldOfView = 72;
                camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(0.13f, 0.17f, 0.2f);
                var carry = SandboxPrimitives.Empty("Carry target", eyes.transform, new Vector3(0, -0.15f, 1.75f));
                host.BindCarryTarget(actor, carry.transform); access.BindActor(actor, eyes.transform);
                var motor = player.AddComponent<LocalWorkerMotor>();
                motor.Initialize(eyes.transform, () => commands.GetWorker(actor), () => world.View.Phase == WorldPhase.Running, host.ReportExternalFailure);
                var rig = SandboxWorkerRigBuilder.Build(world.Epoch, actor, controller, eyes.transform, palette, true);
                foreach (var part in rig.CopyBodySegments()) safety.Bind(part, "Combined-map worker / " + part.name);
                var placement = new WorkerRecoveryPlacement(); placement.Bind(rig); recovery.Bind(world.Epoch, actor, placement);
                worker = player.AddComponent<LocalWorkerStateHost>();
                worker.Initialize(world, actor, rig, placement, host.Pump, motor.ResetAfterRecovery, host.ReportExternalFailure);
                doorHost = owned.AddComponent<MapDoorHost>();
                doorHost.Initialize(host, ids, () => access.PickTarget(actor), views =>
                {
                    var changes = new DoorCollisionProjection[views.Count];
                    for (int i = 0; i < changes.Length; i++) changes[i] = Project(views[i]);
                    var result = physicalDoors.ApplyBatch(changes);
                    if (result != DoorCollisionApplyStatus.Applied && result != DoorCollisionApplyStatus.NoChange)
                    {
                        // A lost contact already reports through the bound failure callback.
                        if (result == DoorCollisionApplyStatus.Unavailable &&
                            (world.View.Phase == WorldPhase.Stopped || world.View.Phase == WorldPhase.Faulted)) return;
                        throw new InvalidOperationException("Map door collision rejected its current projection: " + result);
                    }
                    for (int i = 0; i < views.Count; i++)
                    {
                        var surface = bindings[i].blocker.GetComponent<Renderer>();
                        if (surface != null) surface.enabled = views[i].State != DoorState.Open;
                    }
                }, physicalDoors.Shutdown, id =>
                {
                    var door = world.Doors.Get(id);
                    return door != null && physicalDoors.CanClose(door.SourceId);
                });
                var hud = owned.AddComponent<MapTraversalHud>();
                var workerInput = worker;
                hud.Initialize(input => { motor.SetMovement(input); workerInput.SetDownMovement(input); }, motor.Look, motor.RequestJump,
                    doorHost.OperateFocused, worker.RequestRecovery, doorHost.BeginEvacuationExercise,
                    () => resetRequested = true, () =>
                    {
                        var focus = doorHost.Focused;
                        return world.View.Phase + " · " + (focus == null ? "Look at a door" : focus.SourceId + " · " + focus.State) +
                            "\n" + doorHost.LastAction + "\n" + host.LastAction + "\n" + worker.LastAction + "\nSource " + model.SourceSha256.Substring(0, 12);
                    });
                recovery.Seal(); host.Activate(); worker.Activate(); doorHost.Activate(); safety.Activate();
                Debug.Log("CS_COMBINED_MAP_READY epoch=" + world.Epoch.ToString("N") + " doors=" + bindings.Length + " art_accepted=false");
            }
            catch (Exception exception)
            {
                try { StopWorld(); } catch (Exception cleanup) { Debug.LogException(cleanup, this); }
                Debug.LogException(exception, this); enabled = false;
            }
        }
        private static DoorState State(string value)
        {
            if (!Enum.TryParse(value, true, out DoorState state) || !Enum.IsDefined(typeof(DoorState), state))
                throw new ArgumentException("Unknown authored door state: " + value);
            return state;
        }
        private static DoorCollisionProjection Project(DoorView view)
        {
            var state = view.State == DoorState.Open ? DoorCollisionState.Open :
                view.State == DoorState.Closed ? DoorCollisionState.Closed : DoorCollisionState.Locked;
            return new DoorCollisionProjection(view.Epoch, view.SourceId, view.Revision, state);
        }
        private void StopWorld()
        {
            safety?.Shutdown(); doorHost?.Shutdown(); physicalDoors?.Shutdown(); host?.Shutdown(); worker?.Shutdown(); world?.Stop();
            if (owned != null) { owned.SetActive(false); Destroy(owned); }
            access?.Clear(); recovery?.Clear(); palette?.Dispose();
            owned = null; world = null; host = null; worker = null; doorHost = null; physicalDoors = null; safety = null;
            access = null; recovery = null; palette = null;
        }
        private void OnApplicationQuit() => StopWorld();
        private void OnDisable() => StopWorld();
        private void OnDestroy() => StopWorld();
    }
}
