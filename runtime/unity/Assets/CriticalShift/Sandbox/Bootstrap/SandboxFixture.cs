using System;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics;
using CriticalShift.Features.Interaction.Unity;
using CriticalShift.Features.Workers.Unity;
using CriticalShift.Presentation;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    /// <summary>Constructs only this bounded fixture and wires explicit dependencies. No game-loop ownership.</summary>
    internal sealed class SandboxFixture : IDisposable
    {
        private GameObject root;
        private SandboxPrimitives shapes;
        private SpatialInteractionAccess access;
        private WorldSession world;
        private LocalCommandPort commands;
        private LocalWorldHost host;
        private LocalWorkerMotor walker;
        private LocalWorkerStateHost workerState;
        private WorkerImpactContacts workerContacts;
        private LocalWorkerStateHost patientState;
        private WorkerImpactContacts patientContacts;
        private WorkerBodyRig localRig, patientRig;
        private Collider floorSupport;
        private WorkerContaminationZones contaminationZones;
        private WorkerRecoveryRegistry recovery;
        private CartMotor cart;
        private CartCargoSensor cargo;
        private ConveyorDrive belt;
        private PhysicsSafetyMonitor safety;
        private SandboxHud hud;
        private Rigidbody playerExerciseBody;
        private Transform playerExerciseTarget;
        private SandboxPlayerExercise playerExercise;
        private bool disposed;
        private readonly Guid actor = Id(1), connection = Id(2), reactor = SandboxGameplaySetup.ReactorId, cartId = Id(600);
        private readonly Guid patient = Id(3), patientConnection = Id(4), patientBody = Id(650), localBody = Id(651);
        private readonly Guid[] containers = new Guid[SandboxGameplaySetup.ContainerCount],
            machines = { SandboxGameplaySetup.CrusherId, SandboxGameplaySetup.ProcessorId, SandboxGameplaySetup.DryerId };
        internal Guid Epoch => world.Epoch;
        internal WorldSessionView Snapshot => world.View;
        internal int PhysicalBindingCount => host == null ? 0 : host.BoundBodyCount;
        internal int PhysicsObservationCount => safety == null ? 0 : safety.BoundBodyCount;

        internal SandboxFixture(Transform parent, Shader fixtureShader, Action requestReset, Func<double> clock = null,
            Action<Exception> diagnosticSink = null, Material litTemplate = null, Material emissionTemplate = null)
        {
            root = SandboxPrimitives.Empty("Local Gameplay Fixture", parent, Vector3.zero);
            try
            {
                shapes = new SandboxPrimitives(fixtureShader, litTemplate, emissionTemplate);
                access = new SpatialInteractionAccess(3.8f,
                    (actorId, targetId, body) => host != null && host.MayIgnoreForSight(actorId, targetId, body));
                recovery = new WorkerRecoveryRegistry();
                world = new WorldSession(SandboxGameplaySetup.Configuration(), access, recovery);
                world.RegisterConnection(connection, actor);
                world.RegisterWorkerBody(actor, localBody);
                world.RegisterConnection(patientConnection, patient); world.RegisterWorkerBody(patient, patientBody);
                SandboxGameplaySetup.Register(world);
                commands = new LocalCommandPort(world, connection);
                host = root.AddComponent<LocalWorldHost>(); host.Initialize(world, commands, actor, clock, diagnosticSink);
                host.BindMachineReadout(SandboxMachineReadout.Controls, SandboxMachineReadout.Result);
                host.BindMedicalReadout(SandboxMedicalReadout.Controls, SandboxMedicalReadout.Result);
                safety = root.AddComponent<PhysicsSafetyMonitor>();
                safety.Initialize(root.transform, new Bounds(new Vector3(0, 2, 3), new Vector3(34, 20, 32)),
                    maximumLinearSpeed: 25, maximumRotationalEnergyPerMass: 312.5,
                    () => world.View.Phase == WorldPhase.Running || world.View.Phase == WorldPhase.Paused, host.ReportExternalFailure);
                host.BindFocus(() => access.PickTarget(actor), access.DisplayName);
                BuildRoom(); BuildWorker(); BuildPatient(); BuildContainers(); BuildMachines(); BuildReactor(); BuildSuitStation(); BuildMedical(); BuildCart(); BuildConveyor();
                BuildContaminationZones();
                hud = root.AddComponent<SandboxHud>();
                hud.Initialize(commands, actor, containers, machines, reactor, patient, () => host.FocusHint + "\n" + host.LastAction,
                    () => "Cart " + cart.Speed.ToString("F1") + " m/s · cargo " + cargo.Mass.ToString("F0") + " kg" +
                        (cart.Overloaded ? " OVERLOADED" : "") + (cargo.Saturated ? " SENSOR SATURATED" : !cargo.Available ? " SENSOR UNAVAILABLE" : "") +
                        "\nBelt " + (!belt.Available ? "UNAVAILABLE" : belt.Jammed ? "BLOCKED" : belt.Running ? "moving" : "stopped") + " · bodies " + belt.MovingBodyCount +
                        "\nCarry/drag movement " + (walker.CarrySpeedScale * 100).ToString("F0") + "%" +
                        "\nPhysics " + safety.DynamicBodyCount + "/" + safety.BoundBodyCount + " dynamic · peak " + safety.PeakLinearSpeed.ToString("F1") + " m/s" +
                        (safety.FaultLatched ? "\nPHYSICS STOP: " + safety.Fault : "") +
                        "\n" + workerState.LastAction + (workerState.CrawlDriveActive ? " · crawling" : "") + "\nPatient: " + patientState.LastAction,
                    access.DisplayName, SandboxGameplaySetup.SuitStationId, SandboxGameplaySetup.MedicalStationId);
                hud.BindExposureCue(() => contaminationZones.Describe(actor));
                hud.GrabRequested += host.Grab; hud.ReleaseRequested += host.Release;
                hud.MachineRequested += host.OperateMachine; hud.ReactorRequested += host.OperateReactor;
                hud.SuitFittingRequested += host.OperateSuitFitting;
                hud.MedicalRequested += host.OperateMedical;
                hud.ReplayRequested += host.ReplayLast; hud.PauseRequested += host.ToggleClockPause;
                hud.ResetRequested += requestReset; hud.BeltResetRequested += belt.ResetJam;
                hud.MovementRequested += walker.SetMovement; hud.LookRequested += walker.Look;
                hud.JumpRequested += walker.RequestJump;
                hud.CarryRotationRequested += host.RotateHeld;
                hud.CarryDistanceRequested += host.AdjustHeldDistance;
                hud.ThrowRequested += host.ThrowHeld;
                hud.MovementRequested += workerState.SetDownMovement;
                hud.CartDriveRequested += cart.SetDrive;
                hud.TransferFocusedRequested += host.TransferFocused; hud.DropHeldRequested += host.DropHeld;
                hud.StartFocusedRequested += host.StartFocused; hud.ToggleFocusedPowerRequested += host.ToggleFocusedPower;
                hud.BypassFocusedRequested += host.BypassFocused;
                hud.ShutdownFocusedRequested += host.ShutdownFocused; hud.EmergencyCoolingFocusedRequested += host.EmergencyCoolingFocused;
                hud.WorkerHoistRequested += host.SetWorkerHoist;
                hud.RecoveryRequested += workerState.RequestRecovery; hud.DiagnosticKnockdownRequested += workerState.DiagnosticKnockdown;
                hud.PatientRecoveryRequested += patientState.RequestRecovery; hud.PatientKnockdownRequested += patientState.DiagnosticKnockdown;
                hud.PatientIncapacitateRequested += patientState.DiagnosticIncapacitate;
                recovery.Seal(); host.Activate(); workerState.Activate(); patientState.Activate();
                workerContacts.Activate(); patientContacts.Activate(); patientState.DiagnosticKnockdown(); contaminationZones.Activate(); safety.Activate(); hud.Activate();
            }
            catch { Dispose(); throw; }
        }

        private void BuildRoom()
        {
            floorSupport = SandboxPrimitives.Box("Fixture floor", root.transform, new Vector3(0, -0.15f, 3), new Vector3(24, 0.3f, 22), shapes.Floor).GetComponent<Collider>();
            SandboxPrimitives.Box("West boundary", root.transform, new Vector3(-12, 1.5f, 3), new Vector3(0.3f, 3, 22), shapes.Steel);
            SandboxPrimitives.Box("East boundary", root.transform, new Vector3(12, 1.5f, 3), new Vector3(0.3f, 3, 22), shapes.Steel);
            SandboxPrimitives.Box("North boundary", root.transform, new Vector3(0, 1.5f, 14), new Vector3(24, 3, 0.3f), shapes.Steel);
            SandboxPrimitives.Box("South boundary", root.transform, new Vector3(0, 1.5f, -8), new Vector3(24, 3, 0.3f), shapes.Steel);
            for (int i = 0; i < 10; i++)
                SandboxPrimitives.Box("Floor lane marker " + i, root.transform, new Vector3(-9 + i * 2, 0.008f, 1.5f),
                    new Vector3(1, 0.012f, 0.08f), shapes.Yellow, false);
            var sun = SandboxPrimitives.Empty("Fixture daylight", root.transform, Vector3.zero).AddComponent<Light>();
            sun.type = LightType.Directional; sun.intensity = 1.1f; sun.color = new Color(0.9f, 0.95f, 1);
            sun.transform.localRotation = Quaternion.Euler(55, -35, 0); sun.shadows = LightShadows.Soft;
            SandboxPrimitives.PointLight("Work light", root.transform, new Vector3(-3, 4, 4), new Color(1, 0.8f, 0.55f), 2, 12);
        }

        private void BuildWorker()
        {
            var player = SandboxPrimitives.Empty("Local worker controller", root.transform, new Vector3(-6, 0.1f, -4));
            var controller = SandboxWorkerRigBuilder.AddController(player);
            var eyes = SandboxPrimitives.Empty("Worker eyes", player.transform, new Vector3(0, 1.55f, 0));
            var camera = eyes.AddComponent<Camera>(); camera.fieldOfView = 72; camera.nearClipPlane = 0.05f; camera.farClipPlane = 100;
            camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(0.12f, 0.17f, 0.21f);
            eyes.tag = "MainCamera";
            var carry = SandboxPrimitives.Empty("Current-claim carry target", eyes.transform, new Vector3(0, -0.15f, 1.75f));
            playerExerciseTarget = carry.transform;
            walker = player.AddComponent<LocalWorkerMotor>();
            walker.Initialize(eyes.transform, () => commands.GetWorker(actor), () => world.View.Phase == WorldPhase.Running,
                host.ReportExternalFailure, host.CarriedPhysicalMass, host.CurrentGripStand, host.IsBodyFree);
            access.BindActor(actor, eyes.transform); host.BindCarryTarget(actor, carry.transform);
            var drag = SandboxPrimitives.Empty("Worker suit-grip drag target", player.transform, new Vector3(0, 0.55f, 1.2f));
            host.BindDragTarget(actor, drag.transform);
            host.BindActorRoot(actor, player.transform);
            var rig = SandboxWorkerRigBuilder.Build(world.Epoch, actor, controller, eyes.transform, shapes, hideLocalHead: true);
            localRig = rig;
            rig.BindDragEntity(localBody);
            host.BindWorkerBody(localBody, actor, rig.CopyBodySegments(), rig.PullBodyClaim, rig.ReleaseBodyClaim, () => rig.TotalPhysicalMass, rig.SetBodyHoist);
            BindMedicalPatient(localBody, rig);
            access.BindTarget(localBody, player.transform, rig.SuitGrip);
            foreach (var segment in rig.CopyBodySegments()) safety.Bind(segment, "Local worker / " + segment.name);
            rig.BindNormalHands(() => host.CarriedPhysicalMass() > 0 || host.CurrentGripStand().HasValue);
            BuildWorkerSignal(actor, rig, "Local worker status marker");
            var placement = new WorkerRecoveryPlacement(); placement.Bind(rig); recovery.Bind(world.Epoch, actor, placement);
            workerState = player.AddComponent<LocalWorkerStateHost>();
            workerState.Initialize(world, actor, rig, placement, host.Pump, walker.ResetAfterRecovery, host.ReportExternalFailure);
            workerState.BindHazard(cartId); workerState.BindHazard(Id(702), diagnostic: true);
            workerContacts = player.AddComponent<WorkerImpactContacts>();
            workerContacts.Initialize(controller, () => commands.GetWorker(actor), () => world.View.Phase == WorldPhase.Running,
                () => walker.MeasuredVelocity, workerState.ObserveKnockdown, host.ReportExternalFailure);
        }

        private void BuildPatient()
        {
            var worker = SandboxPrimitives.Empty("Fixture patient worker", root.transform, new Vector3(-9, 0.1f, 4));
            var controller = SandboxWorkerRigBuilder.AddController(worker);
            var eyes = SandboxPrimitives.Empty("Patient observation anchor", worker.transform, new Vector3(0, 1.55f, 0));
            var rig = SandboxWorkerRigBuilder.Build(world.Epoch, patient, controller, eyes.transform, shapes, hideLocalHead: false);
            patientRig = rig;
            foreach (var segment in rig.CopyBodySegments()) safety.Bind(segment, "Patient worker / " + segment.name);
            rig.BindDragEntity(patientBody);
            BuildWorkerSignal(patient, rig, "Patient worker status marker");
            host.BindWorkerBody(patientBody, patient, rig.CopyBodySegments(), rig.PullBodyClaim, rig.ReleaseBodyClaim, () => rig.TotalPhysicalMass, rig.SetBodyHoist);
            BindMedicalPatient(patientBody, rig);
            access.BindActor(patient, eyes.transform);
            access.BindTarget(patientBody, worker.transform, rig.SuitGrip);
            var placement = new WorkerRecoveryPlacement(); placement.Bind(rig); recovery.Bind(world.Epoch, patient, placement);
            patientState = worker.AddComponent<LocalWorkerStateHost>();
            patientState.Initialize(world, patient, rig, placement, host.Pump, () => { }, host.ReportExternalFailure);
            patientState.BindHazard(cartId); patientState.BindHazard(Id(703), diagnostic: true);
            patientContacts = worker.AddComponent<WorkerImpactContacts>();
            patientContacts.Initialize(controller, () => commands.GetWorker(patient), () => world.View.Phase == WorldPhase.Running,
                () => Vector3.zero, patientState.ObserveKnockdown, host.ReportExternalFailure);
        }

        private void BuildWorkerSignal(Guid worker, WorkerBodyRig rig, string name)
        {
            var marker = SandboxPrimitives.Shape(PrimitiveType.Sphere, name, root.transform, Vector3.zero,
                Vector3.one * 0.12f, shapes.Lamp, false);
            var light = marker.AddComponent<Light>(); light.type = LightType.Point; light.range = 1.8f;
            light.shadows = LightShadows.None; light.intensity = 0;
            marker.AddComponent<WorkerStatusFeedback>().Initialize(commands, worker, marker.GetComponent<Renderer>(), light,
                () => rig == null || rig.SuitGrip == null ? (Vector3?)null : rig.SuitGrip.position);
        }

        private void BindMedicalPatient(Guid body, WorkerBodyRig rig)
        {
            var placement = new WorkerMedicalPlacement(); placement.Bind(rig);
            host.BindMedicalWorker(body, placement.Prepare, placement.Reconcile, placement.CancelStage, placement.Clear);
        }

        private void BuildMedical()
        {
            var station = SandboxPrimitives.Empty("Powered medical stabilization", root.transform, new Vector3(9, 0, 10));
            var bed = SandboxPrimitives.Box("Medical bed support", station.transform, new Vector3(0, 0.55f, 0),
                new Vector3(1.5f, 0.3f, 2.5f), shapes.Steel);
            var pose = SandboxPrimitives.Empty("Explicit supine patient pose", station.transform, new Vector3(0, 0.7f, 0));
            var discharge = SandboxPrimitives.Empty("Explicit floor discharge pose", station.transform, new Vector3(0, 0, -3));
            SandboxPrimitives.Box("Medical discharge clearance marker", discharge.transform, new Vector3(0, 0.008f, 0),
                new Vector3(1.5f, 0.012f, 2.5f), shapes.Yellow, false);
            var console = SandboxPrimitives.Box("Medical console", station.transform, new Vector3(-1.6f, 0.7f, 0),
                new Vector3(0.35f, 1.4f, 0.35f), shapes.Dark);
            // Keep bound anchors unit-scale: the console primitive itself is deliberately scaled geometry.
            var consolePoint = SandboxPrimitives.Empty("Explicit medical control anchor", station.transform, new Vector3(-1.6f, 1.1f, 0));
            host.BindMedicalSlot(SandboxGameplaySetup.MedicalStationId, pose.transform, bed.GetComponent<Collider>(),
                discharge.transform, floorSupport, consolePoint.transform);
            access.BindTarget(SandboxGameplaySetup.MedicalStationId, station.transform, consolePoint.transform);
        }

        private void BuildContainers()
        {
            for (int i = 0; i < containers.Length; i++)
            {
                containers[i] = SandboxGameplaySetup.ContainerId(i);
                var batch = world.Production.GetBatch(containers[i]);
                if (batch == null) throw new InvalidOperationException("The canonical sandbox stock is missing.");
                bool fuel = batch.Kind == MaterialKind.Fuel, wet = batch.Moisture > 500;
                int units = batch.Units;
                var crate = SandboxPrimitives.Box("Material container " + (i + 1), root.transform,
                    new Vector3(-8 + i % 4 * 0.85f, 0.65f, -0.5f + i / 4 * 0.9f),
                    new Vector3(0.55f, 0.6f, 0.55f), fuel ? shapes.Fuel : wet ? shapes.Wet : shapes.Ore);
                var body = crate.AddComponent<Rigidbody>(); body.mass = units * 0.75f;
                body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
                body.maxAngularVelocity = 10;
                if (i == 2) playerExerciseBody = body;
                host.BindBody(containers[i], body, 0.75f); access.BindTarget(containers[i], crate.transform);
                safety.Bind(body, "Material container " + (i + 1));
                if (i == 0)
                {
                    workerState.BindHazard(containers[i]); patientState.BindHazard(containers[i]);
                    workerContacts.BindFallingHazard(containers[i], body, () => host.IsBodyFree(body));
                    patientContacts.BindFallingHazard(containers[i], body, () => host.IsBodyFree(body));
                }
                // Bind solid bounds before adding non-contacting decorative primitives.
                crate.GetComponent<Renderer>().enabled = false;
                SandboxPrimitives.Box("Crate bottom", crate.transform, new Vector3(0, -0.43f, 0), new Vector3(1, 0.14f, 1), shapes.Dark, false);
                SandboxPrimitives.Box("Crate left wall", crate.transform, new Vector3(-0.46f, 0, 0), new Vector3(0.08f, 0.8f, 1), shapes.Steel, false);
                SandboxPrimitives.Box("Crate right wall", crate.transform, new Vector3(0.46f, 0, 0), new Vector3(0.08f, 0.8f, 1), shapes.Steel, false);
                var face = SandboxPrimitives.Box("Crate front wall", crate.transform, new Vector3(0, 0, -0.46f),
                    new Vector3(0.84f, 0.8f, 0.08f), fuel ? shapes.Fuel : wet ? shapes.Wet : shapes.Ore, false);
                SandboxPrimitives.Box("Crate rear wall", crate.transform, new Vector3(0, 0, 0.46f), new Vector3(0.84f, 0.8f, 0.08f), shapes.Steel, false);
                SandboxPrimitives.Box("Crate orientation stripe", crate.transform, new Vector3(0, 0.05f, -0.51f),
                    new Vector3(0.12f, 0.5f, 0.025f), shapes.Dark, false);
                SandboxPrimitives.Box("Crate orientation head", crate.transform, new Vector3(0, 0.3f, -0.51f),
                    new Vector3(0.4f, 0.08f, 0.025f), shapes.Yellow, false);
                if (i == 0)
                    for (int band = -1; band <= 1; band += 2)
                        SandboxPrimitives.Box("Heavy crate warning band " + band, crate.transform, new Vector3(band * 0.3f, 0, -0.51f),
                            new Vector3(0.075f, 0.7f, 0.025f), shapes.Yellow, false);
                var contents = new Transform[8];
                for (int piece = 0; piece < contents.Length; piece++)
                    contents[piece] = SandboxPrimitives.Box("Bounded material visual " + piece, crate.transform,
                        new Vector3(piece % 2 == 0 ? -0.24f : 0.24f, piece < 4 ? -0.22f : 0.1f, piece % 4 < 2 ? -0.24f : 0.24f),
                        new Vector3(0.3f, 0.28f, 0.3f), shapes.Ore, false).transform;
                crate.AddComponent<MaterialContainerFeedback>().Initialize(commands, containers[i], face.GetComponent<Renderer>(), contents, units);
            }
        }

        private void BuildMachines()
        {
            BuildMachine(machines[0], "Crusher", new Vector3(-4, 0, 5));
            BuildMachine(machines[1], "Fuel processor", new Vector3(0.5f, 0, 5));
            BuildMachine(machines[2], "Ore dryer", new Vector3(-8.5f, 0, 9));
        }

        private void BuildMachine(Guid id, string name, Vector3 position)
        {
            var machine = SandboxPrimitives.Empty(name, root.transform, position);
            SandboxPrimitives.Box("Machine case", machine.transform, new Vector3(0, 0.9f, 0), new Vector3(1.5f, 1.8f, 1.2f), shapes.Steel);
            SandboxPrimitives.Box("Loading support", machine.transform, new Vector3(0, 0.65f, -1.1f), new Vector3(0.85f, 0.12f, 0.85f), shapes.Yellow);
            var slot = SandboxPrimitives.Empty("Explicit loading slot", machine.transform, new Vector3(0, 1.05f, -1.1f));
            host.BindSlot(id, slot.transform);
            var face = SandboxPrimitives.Box("Status face", machine.transform, new Vector3(0, 1.5f, -0.62f), new Vector3(0.7f, 0.25f, 0.04f), shapes.Lamp, false);
            access.BindTarget(id, machine.transform, face.transform);
            var rotor = SandboxPrimitives.Empty("Process spindle pivot", machine.transform, new Vector3(0.45f, 1, -0.68f));
            var rotorDisc = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Process spindle disc", rotor.transform,
                Vector3.zero, new Vector3(0.5f, 0.1f, 0.5f), shapes.Dark, false);
            rotorDisc.transform.localRotation = Quaternion.Euler(90, 0, 0);
            SandboxPrimitives.Box("Spindle rotation marker", rotor.transform, new Vector3(0, 0, -0.11f),
                new Vector3(0.36f, 0.055f, 0.025f), shapes.Yellow, false);
            var light = SandboxPrimitives.PointLight("Status lamp", machine.transform, new Vector3(0, 1.8f, -0.85f), Color.green, 0.5f, 2.5f);
            SandboxPrimitives.Box("Process gauge backing", machine.transform, new Vector3(0, 1.26f, -0.63f), new Vector3(0.95f, 0.12f, 0.04f), shapes.Dark, false);
            var gauge = SandboxPrimitives.Box("Process gauge fill", machine.transform, new Vector3(0, 1.26f, -0.66f),
                new Vector3(0.9f, 0.07f, 0.025f), shapes.Yellow, false);
            var sparkOrigin = SandboxPrimitives.Empty("Process spark origin", machine.transform, new Vector3(0.45f, 1, -0.8f));
            var sparks = new Transform[8];
            for (int i = 0; i < sparks.Length; i++)
                sparks[i] = SandboxPrimitives.Box("Pooled process spark " + i, sparkOrigin.transform, Vector3.zero,
                    new Vector3(0.012f, 0.035f, 0.012f), shapes.Lamp, false).transform;
            SandboxPrimitives.Box("Power switch plate", machine.transform, new Vector3(-0.52f, 0.85f, -0.68f), new Vector3(0.26f, 0.45f, 0.055f), shapes.Dark, false);
            var powerSwitch = SandboxPrimitives.Empty("Power switch pivot", machine.transform, new Vector3(-0.52f, 0.8f, -0.75f));
            SandboxPrimitives.Box("Power switch arm", powerSwitch.transform, new Vector3(0, 0.12f, 0), new Vector3(0.035f, 0.24f, 0.035f), shapes.Steel, false);
            SandboxPrimitives.Shape(PrimitiveType.Sphere, "Power switch grip", powerSwitch.transform, new Vector3(0, 0.26f, 0), Vector3.one * 0.1f, shapes.Yellow, false);
            var clamps = new Transform[2];
            for (int i = 0; i < clamps.Length; i++)
            {
                var clamp = SandboxPrimitives.Empty("Loading clamp " + i, machine.transform, new Vector3(i == 0 ? -0.55f : 0.55f, 1.05f, -1.1f));
                SandboxPrimitives.Box("Loading clamp jaw", clamp.transform, Vector3.zero, new Vector3(0.12f, 0.35f, 0.65f), shapes.Dark, false);
                clamps[i] = clamp.transform;
                SandboxPrimitives.Box("Loading gantry upright " + i, machine.transform, new Vector3(i == 0 ? -0.6f : 0.6f, 1.25f, -1.1f),
                    new Vector3(0.075f, 1.1f, 0.075f), shapes.Yellow, false);
            }
            SandboxPrimitives.Box("Loading gantry crossmember", machine.transform, new Vector3(0, 1.8f, -1.1f),
                new Vector3(1.3f, 0.1f, 0.1f), shapes.Yellow, false);
            var ram = SandboxPrimitives.Empty("Process ram pivot", machine.transform, new Vector3(0, 1.7f, -1.1f));
            SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Process ram shaft", ram.transform, new Vector3(0, 0.12f, 0),
                new Vector3(0.08f, 0.16f, 0.08f), shapes.Steel, false);
            SandboxPrimitives.Box("Process ram head", ram.transform, new Vector3(0, -0.1f, 0), new Vector3(0.7f, 0.12f, 0.7f), shapes.Dark, false);
            machine.AddComponent<MachineFeedback>().Initialize(commands, id, face.GetComponent<Renderer>(), light, rotor.transform,
                gauge.transform, sparks, powerSwitch.transform, ram.transform, clamps);
        }

        private void BuildReactor()
        {
            var room = SandboxPrimitives.Empty("Reactor fixture", root.transform, new Vector3(5.5f, 0, 6));
            SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Core housing", room.transform, new Vector3(0, 1.4f, 0),
                new Vector3(1.5f, 1.4f, 1.5f), shapes.Steel);
            SandboxPrimitives.Box("Fuel loading support", room.transform, new Vector3(0, 0.65f, -1.3f), new Vector3(0.85f, 0.12f, 0.85f), shapes.Yellow);
            var slot = SandboxPrimitives.Empty("Reactor fuel slot", room.transform, new Vector3(0, 1.05f, -1.3f));
            host.BindSlot(reactor, slot.transform);
            var face = SandboxPrimitives.Box("Reactor status", room.transform, new Vector3(0, 2.2f, -0.78f), new Vector3(0.8f, 0.3f, 0.05f), shapes.Lamp, false);
            access.BindTarget(reactor, room.transform, face.transform);
            var valve = SandboxPrimitives.Empty("Cooling valve pivot", room.transform, new Vector3(1.2f, 1.1f, -0.5f));
            var valveDisc = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Cooling valve wheel", valve.transform,
                Vector3.zero, new Vector3(0.5f, 0.08f, 0.5f), shapes.Yellow, false);
            valveDisc.transform.localRotation = Quaternion.Euler(90, 0, 0);
            SandboxPrimitives.Box("Cooling valve position marker", valve.transform, new Vector3(0, 0, -0.095f),
                new Vector3(0.35f, 0.055f, 0.025f), shapes.Dark, false);
            var light = SandboxPrimitives.PointLight("Reactor warning beacon", room.transform, new Vector3(0, 3.1f, 0), Color.cyan, 0.5f, 4);
            var vent = SandboxPrimitives.Empty("Reactor vent origin", room.transform, new Vector3(0.35f, 2.9f, 0));
            var motes = new Transform[6];
            for (int i = 0; i < motes.Length; i++)
                motes[i] = SandboxPrimitives.Shape(PrimitiveType.Sphere, "Pooled vent mote " + i, vent.transform, Vector3.zero,
                    Vector3.one * 0.11f, shapes.Lamp, false).transform;
            SandboxPrimitives.Box("Reactor instrument panel", room.transform, new Vector3(0, 1.65f, -0.81f),
                new Vector3(1.2f, 0.55f, 0.08f), shapes.Dark, false);
            var fuelNeedle = Dial("Fuel remaining", new Vector3(-0.31f, 1.65f, -0.87f), shapes.Fuel);
            var reserveNeedle = Dial("Reserve power", new Vector3(0.31f, 1.65f, -0.87f), shapes.Yellow);
            room.AddComponent<ReactorFeedback>().Initialize(commands, face.GetComponent<Renderer>(), light, valve.transform, motes,
                fuelNeedle, reserveNeedle);

            Transform Dial(string name, Vector3 position, Material color)
            {
                var dial = SandboxPrimitives.Empty(name + " dial", room.transform, position);
                var disc = SandboxPrimitives.Shape(PrimitiveType.Cylinder, name + " face", dial.transform, Vector3.zero,
                    new Vector3(0.43f, 0.012f, 0.43f), shapes.Steel, false);
                disc.transform.localRotation = Quaternion.Euler(90, 0, 0);
                for (int i = 0; i < 9; i++)
                {
                    float angle = Mathf.Lerp(-120, 120, i / 8f);
                    Quaternion rotation = Quaternion.AngleAxis(angle, Vector3.back);
                    var tick = SandboxPrimitives.Box(name + " tick " + i, dial.transform,
                        rotation * new Vector3(0, 0.17f, -0.018f), new Vector3(0.015f, 0.035f, 0.012f), shapes.Dark, false);
                    tick.transform.localRotation = rotation;
                }
                var pivot = SandboxPrimitives.Empty(name + " needle", dial.transform, new Vector3(0, 0, -0.035f));
                SandboxPrimitives.Box(name + " pointer", pivot.transform, new Vector3(0, 0.07f, 0),
                    new Vector3(0.025f, 0.17f, 0.018f), color, false);
                return pivot.transform;
            }
        }

        private void BuildSuitStation()
        {
            var station = SandboxPrimitives.Empty("Protective suit fitting station", root.transform, new Vector3(-9, 0, -5));
            SandboxPrimitives.Box("Suit station case", station.transform, new Vector3(0, 1, 0), new Vector3(1.2f, 2, 0.6f), shapes.Steel);
            var face = SandboxPrimitives.Box("Suit fitting interaction panel", station.transform, new Vector3(0, 1.4f, 0.33f),
                new Vector3(0.8f, 0.35f, 0.05f), shapes.Yellow, false);
            access.BindTarget(SandboxGameplaySetup.SuitStationId, station.transform, face.transform);
        }

        private void BuildContaminationZones()
        {
            contaminationZones = root.AddComponent<WorkerContaminationZones>();
            contaminationZones.Initialize(world, host.Pump, host.ReportExternalFailure);
            contaminationZones.BindWorker(actor, localRig); contaminationZones.BindWorker(patient, patientRig);
            BindArea(SandboxGameplaySetup.ExposureSourceId, new Vector3(0, 1.5f, -4.5f), "Exposure area", shapes.Yellow);
            BindArea(SandboxGameplaySetup.WashSourceId, new Vector3(5, 1.5f, -4.5f), "Wash area", shapes.Fuel);
            contaminationZones.Seal();
        }
        private void BindArea(Guid source, Vector3 center, string label, Material material)
        {
            var frame = SandboxPrimitives.Empty(label, root.transform, center);
            SandboxPrimitives.Box(label + " floor marking", frame.transform, new Vector3(0, -1.48f, 0),
                new Vector3(2.5f, 0.02f, 2.5f), material, false);
            contaminationZones.BindArea(source, frame.transform, new Vector3(1.25f, 1.5f, 1.25f), label);
        }

        private void BuildCart()
        {
            world.RegisterObject(cartId);
            var rig = SandboxPrimitives.Empty("Physical ore cart", root.transform, new Vector3(5, 0.45f, -1.5f));
            var body = rig.AddComponent<Rigidbody>(); body.mass = 35; body.centerOfMass = new Vector3(0, -0.15f, 0);
            safety.Bind(body, "Ore cart");
            body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            SandboxPrimitives.Box("Cart bed", rig.transform, Vector3.zero, new Vector3(1.2f, 0.18f, 1.8f), shapes.Steel);
            SandboxPrimitives.Box("Left cargo rail", rig.transform, new Vector3(-0.62f, 0.35f, 0), new Vector3(0.1f, 0.7f, 1.8f), shapes.Yellow);
            SandboxPrimitives.Box("Right cargo rail", rig.transform, new Vector3(0.62f, 0.35f, 0), new Vector3(0.1f, 0.7f, 1.8f), shapes.Yellow);
            SandboxPrimitives.Box("Cart rear rail", rig.transform, new Vector3(0, 0.35f, -0.92f), new Vector3(1.2f, 0.7f, 0.1f), shapes.Steel);
            var handle = SandboxPrimitives.Empty("Cart rear grip", rig.transform, new Vector3(0, 0.9f, -1.15f));
            SandboxPrimitives.Box("Cart handle bar", handle.transform, Vector3.zero, new Vector3(1.1f, 0.08f, 0.08f), shapes.Dark);
            var stand = SandboxPrimitives.Empty("Cart operator stance", rig.transform, new Vector3(0, -0.45f, -2));
            var sensor = SandboxPrimitives.Empty("Cargo observation bounds", rig.transform, new Vector3(0, 0.65f, 0));
            var bounds = sensor.AddComponent<BoxCollider>(); bounds.isTrigger = true; bounds.size = new Vector3(1.1f, 1.1f, 1.65f);
            cargo = sensor.AddComponent<CartCargoSensor>(); cargo.Initialize(body, host.PhysicalCargoGroup, host.PhysicalCargoMass);
            cart = rig.AddComponent<CartMotor>(); cart.SafeCargoMass = 35;
            cart.Initialize(() => world.View.Phase == WorldPhase.Running && host.IsHandleHeld(cartId) && cargo.Available && !cargo.Saturated, () => cargo.Mass);
            workerContacts.BindHazard(cartId, body);
            patientContacts.BindHazard(cartId, body);
            var loadFace = SandboxPrimitives.Box("Cart load warning face", rig.transform, new Vector3(0.48f, 0.8f, -0.96f),
                new Vector3(0.16f, 0.16f, 0.04f), shapes.Lamp, false);
            var loadLamp = SandboxPrimitives.PointLight("Cart overload beacon", rig.transform, new Vector3(0.48f, 0.95f, -0.95f), Color.green, 0.2f, 1.6f);
            rig.AddComponent<CartLoadFeedback>().Initialize(loadFace.GetComponent<Renderer>(), loadLamp,
                () => cart.Overloaded, () => !cargo.Available || cargo.Saturated);
            var wheels = new Transform[4];
            for (int i = 0; i < wheels.Length; i++)
            {
                var contact = SandboxPrimitives.Empty("Wheel collision anchor " + i, rig.transform,
                    new Vector3(i % 2 == 0 ? -0.65f : 0.65f, -0.22f, i < 2 ? 0.65f : -0.65f));
                var wheelContact = contact.AddComponent<SphereCollider>(); wheelContact.radius = 0.22f;
                wheelContact.sharedMaterial = shapes.WheelContact;
                var pivot = SandboxPrimitives.Empty("Wheel animation pivot " + i, contact.transform, Vector3.zero);
                var visual = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Wheel visual", pivot.transform, Vector3.zero,
                    new Vector3(0.44f, 0.06f, 0.44f), shapes.Dark, false);
                visual.transform.localRotation = Quaternion.Euler(0, 0, 90);
                SandboxPrimitives.Box("Wheel rotation marker", pivot.transform, new Vector3(i % 2 == 0 ? -0.065f : 0.065f, 0, 0),
                    new Vector3(0.018f, 0.34f, 0.04f), shapes.Yellow, false);
                wheels[i] = pivot.transform;
            }
            rig.AddComponent<CartWheelMotion>().Initialize(cart, wheels);
            // Capture required contacts only after the bed, rails, handle and wheel shapes exist.
            host.BindCartHandle(cartId, body, handle.transform, stand.transform); access.BindTarget(cartId, rig.transform, handle.transform);
        }

        private void BuildConveyor()
        {
            var rig = SandboxPrimitives.Empty("Conveyor fixture", root.transform, new Vector3(-1, 0.45f, -0.5f));
            SandboxPrimitives.Box("Belt support", rig.transform, Vector3.zero, new Vector3(1.8f, 0.2f, 4), shapes.Dark);
            SandboxPrimitives.Box("Belt west rail", rig.transform, new Vector3(-0.95f, 0.15f, 0), new Vector3(0.1f, 0.35f, 4), shapes.Yellow);
            SandboxPrimitives.Box("Belt east rail", rig.transform, new Vector3(0.95f, 0.15f, 0), new Vector3(0.1f, 0.35f, 4), shapes.Yellow);
            SandboxPrimitives.Box("End obstruction", rig.transform, new Vector3(0, 0.35f, 2.05f), new Vector3(1.8f, 0.7f, 0.1f), shapes.Steel);
            var sensor = SandboxPrimitives.Empty("Belt observation bounds", rig.transform, new Vector3(0, 0.7f, 0));
            var bounds = sensor.AddComponent<BoxCollider>(); bounds.isTrigger = true; bounds.size = new Vector3(1.8f, 1.3f, 4);
            belt = sensor.AddComponent<ConveyorDrive>(); belt.Initialize(host.IsBodyFree, () => world.View.Phase == WorldPhase.Running);
            var markers = new Transform[16];
            for (int i = 0; i < markers.Length; i++)
                markers[i] = SandboxPrimitives.Box("Belt tread " + i, rig.transform, new Vector3(0, 0.112f, -1.9f + i * 0.25f),
                    new Vector3(1.7f, 0.01f, 0.055f), shapes.Yellow, false).transform;
            var rollers = new Transform[2];
            for (int i = 0; i < rollers.Length; i++)
            {
                var roller = SandboxPrimitives.Empty("Belt end roller pivot " + i, rig.transform, new Vector3(0, -0.05f, i == 0 ? -1.9f : 1.9f));
                var drum = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Belt end roller drum", roller.transform, Vector3.zero,
                    new Vector3(0.32f, 0.9f, 0.32f), shapes.Dark, false);
                drum.transform.localRotation = Quaternion.Euler(0, 0, 90);
                SandboxPrimitives.Box("Belt roller rotation stripe", roller.transform, new Vector3(0, 0.17f, 0),
                    new Vector3(1.5f, 0.02f, 0.03f), shapes.Yellow, false);
                rollers[i] = roller.transform;
            }
            rig.AddComponent<ConveyorBeltMotion>().Initialize(belt, markers, 4, rollers, 0.16f);
        }

        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);

        internal int PreparePlayerSmoke()
        {
            hud.enabled = false;
            // This is the explicitly owned fixture subtree, never a global scene search.
            var meshes = root.GetComponentsInChildren<MeshFilter>(true);
            if (meshes.Length == 0) throw new InvalidOperationException("The sandbox Player has no generated meshes.");
            foreach (var filter in meshes)
            {
                var renderer = filter.GetComponent<MeshRenderer>();
                if (filter.sharedMesh == null || filter.sharedMesh.vertexCount == 0 || renderer == null ||
                    renderer.sharedMaterial == null || renderer.sharedMaterial.shader == null)
                    throw new InvalidOperationException("A generated sandbox Player mesh or material dependency is missing.");
            }
            return meshes.Length;
        }

        internal void ObservePlayerSmoke(bool requirePhysicalSensors = false)
            => ObservePlayerSmokeState(requirePhysicalSensors, false);

        internal void PreparePlayerExercise()
        {
            if (playerExercise != null || disposed) throw new InvalidOperationException("Prepare the explicit Player exercise once in its live fixture.");
            playerExercise = new SandboxPlayerExercise(world, commands, host, access, actor, containers[2], containers[6],
                playerExerciseBody, playerExerciseTarget);
        }

        internal bool PlayerExerciseCompleted => playerExercise != null && playerExercise.Completed;
        internal string PlayerExerciseStage => playerExercise == null ? "Setup" : playerExercise.Stage;

        internal void CheckPlayerExerciseDeadline() => playerExercise?.CheckDeadline();

        internal void ObservePlayerExercise()
        {
            if (playerExercise == null) throw new InvalidOperationException("The explicit Player exercise has not been prepared.");
            ObservePlayerSmokeState(false, playerExercise.Holding);
            playerExercise.Step();
        }

        private void ObservePlayerSmokeState(bool requirePhysicalSensors, bool exerciseHolding)
        {
            safety.Sample();
            var view = world.View;
            // Only this opt-in driver's exact current body/actor claim may replace the ordinary zero-claim baseline.
            var exercisedClaim = exerciseHolding ? world.GetObject(containers[2]) : null;
            if (exerciseHolding && (playerExercise == null || !playerExercise.Holding || exercisedClaim == null ||
                exercisedClaim.Epoch != Epoch || exercisedClaim.EntityId != containers[2] || exercisedClaim.HolderId != actor ||
                exercisedClaim.IsRetired || exercisedClaim.SlotId.HasValue))
                throw new InvalidOperationException("The opt-in exercise lost its sole expected current-world portable claim.");
            if (disposed || view.Phase != WorldPhase.Running || view.ActiveClaimCount != (exerciseHolding ? 1 : 0) || view.ConnectedPlayerCount != 2 ||
                view.RegisteredObjectCount != 11 || PhysicalBindingCount != 11 || PhysicsObservationCount != 31 || safety.FaultLatched ||
                safety.DynamicBodyCount != 20 || world.GetWorker(actor)?.Pose != WorkerPose.Upright ||
                world.GetWorker(patient)?.Pose != WorkerPose.Down || world.Reactor.View?.Mode != ReactorMode.Empty)
                throw new InvalidOperationException("The sandbox Player lost its declared running-world or physical fixture invariants.");
            foreach (var container in containers)
                if (world.GetObject(container) == null || world.Production.GetBatch(container) == null)
                    throw new InvalidOperationException("The sandbox Player lost a material/container binding.");
            foreach (var machine in machines)
                if (world.Production.GetMachine(machine)?.Mode != ProductionMode.Idle)
                    throw new InvalidOperationException("The untouched sandbox Player machine baseline changed.");
            if (requirePhysicalSensors && (!cargo.Available || cargo.Saturated || cargo.BodyCount != 0 || cargo.Mass != 0 ||
                !belt.Available || !belt.Running || belt.Jammed || belt.MovingBodyCount != 0))
                throw new InvalidOperationException("The untouched sandbox Player lost its sampled cargo/belt observation baseline.");
        }

        public void Dispose()
        {
            if (disposed) return;
            disposed = true;
            if (contaminationZones != null) contaminationZones.Shutdown();
            if (safety != null) safety.Shutdown();
            if (host != null) host.Shutdown();
            else world?.Stop(); // Setup can fail before the host is composed.
            if (workerState != null) workerState.Shutdown();
            if (patientState != null) patientState.Shutdown();
            if (root != null) { root.SetActive(false); UnityEngine.Object.Destroy(root); }
            access?.Clear(); recovery?.Clear(); shapes?.Dispose();
            playerExercise = null; playerExerciseBody = null; playerExerciseTarget = null;
            localRig = null; patientRig = null;
            floorSupport = null;
        }
    }
}
