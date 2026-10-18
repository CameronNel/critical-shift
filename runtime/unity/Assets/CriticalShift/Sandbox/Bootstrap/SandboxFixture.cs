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
        private CartMotor cart;
        private CartCargoSensor cargo;
        private ConveyorDrive belt;
        private bool disposed;
        private readonly Guid actor = Id(1), connection = Id(2), reactor = Id(500), cartId = Id(600);
        private readonly Guid[] containers = new Guid[8], machines = { Id(400), Id(401) };
        internal Guid Epoch => world.Epoch;
        internal WorldSessionView Snapshot => world.View;
        internal int PhysicalBindingCount => host == null ? 0 : host.BoundBodyCount;

        internal SandboxFixture(Transform parent, Shader fixtureShader, Action requestReset)
        {
            root = SandboxPrimitives.Empty("Local Gameplay Fixture", parent, Vector3.zero);
            try
            {
                shapes = new SandboxPrimitives(fixtureShader);
                access = new SpatialInteractionAccess(3.8f,
                    (actorId, targetId, body) => host != null && host.MayIgnoreForSight(actorId, targetId, body));
                world = new WorldSession(new WorldSessionConfiguration(7, 12 * 60 * 1000, true, maxObjects: 32), access);
                world.RegisterConnection(connection, actor);
                commands = new LocalCommandPort(world, connection);
                host = root.AddComponent<LocalWorldHost>(); host.Initialize(world, commands, actor);
                host.BindFocus(() => access.PickTarget(actor), access.DisplayName);
                BuildRoom(); BuildWorker(); BuildContainers(); BuildMachines(); BuildReactor(); BuildCart(); BuildConveyor();
                var hud = root.AddComponent<SandboxHud>();
                hud.Initialize(commands, actor, containers, machines, reactor, () => host.FocusHint + "\n" + host.LastAction,
                    () => "Cart " + cart.Speed.ToString("F1") + " m/s · cargo " + cargo.Mass.ToString("F0") + " kg" +
                        (cart.Overloaded ? " OVERLOADED" : "") + (cargo.Saturated ? " SENSOR SATURATED" : "") +
                        "\nBelt " + (belt.Jammed ? "BLOCKED" : belt.Running ? "moving" : "stopped") + " · bodies " + belt.MovingBodyCount +
                        "\nCarrying movement " + (walker.CarrySpeedScale * 100).ToString("F0") + "%");
                hud.GrabRequested += host.Grab; hud.ReleaseRequested += host.Release;
                hud.MachineRequested += host.OperateMachine; hud.ReactorRequested += host.OperateReactor;
                hud.ReplayRequested += host.ReplayLast; hud.PauseRequested += host.ToggleClockPause;
                hud.ResetRequested += requestReset; hud.BeltResetRequested += belt.ResetJam;
                hud.MovementRequested += walker.SetMovement; hud.LookRequested += walker.Look;
                hud.CartDriveRequested += cart.SetDrive;
                hud.TransferFocusedRequested += host.TransferFocused; hud.DropHeldRequested += host.DropHeld;
                hud.StartFocusedRequested += host.StartFocused; hud.ToggleFocusedPowerRequested += host.ToggleFocusedPower;
                host.Activate(); hud.Activate();
            }
            catch { Dispose(); throw; }
        }

        private void BuildRoom()
        {
            SandboxPrimitives.Box("Fixture floor", root.transform, new Vector3(0, -0.15f, 3), new Vector3(24, 0.3f, 22), shapes.Floor);
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
            var controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f; controller.radius = 0.32f; controller.center = new Vector3(0, 0.9f, 0);
            controller.stepOffset = 0.25f; controller.slopeLimit = 45; controller.skinWidth = 0.03f;
            var eyes = SandboxPrimitives.Empty("Worker eyes", player.transform, new Vector3(0, 1.55f, 0));
            var camera = eyes.AddComponent<Camera>(); camera.fieldOfView = 72; camera.nearClipPlane = 0.05f; camera.farClipPlane = 100;
            camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(0.12f, 0.17f, 0.21f);
            eyes.tag = "MainCamera";
            var carry = SandboxPrimitives.Empty("Current-claim carry target", eyes.transform, new Vector3(0, -0.15f, 1.75f));
            walker = player.AddComponent<LocalWorkerMotor>();
            walker.Initialize(eyes.transform, () => commands.GetWorker(actor), () => world.View.Phase == WorldPhase.Running,
                host.CarriedPhysicalMass, host.CurrentGripStand);
            access.BindActor(actor, eyes.transform); host.BindCarryTarget(actor, carry.transform);
            host.BindActorRoot(actor, player.transform);
        }

        private void BuildContainers()
        {
            for (int i = 0; i < containers.Length; i++)
            {
                containers[i] = Id(100 + i);
                bool fuel = i == 6, wet = i == 7;
                world.Production.RegisterBatch(containers[i], Id(200 + i), Id(300), Id(310 + i),
                    fuel ? MaterialKind.Fuel : MaterialKind.Ore, 12, moisture: wet ? 850 : 100);
                var crate = SandboxPrimitives.Box("Material container " + (i + 1), root.transform,
                    new Vector3(-8 + i % 4 * 0.85f, 0.65f, -0.5f + i / 4 * 0.9f),
                    new Vector3(0.55f, 0.6f, 0.55f), fuel ? shapes.Fuel : wet ? shapes.Wet : shapes.Ore);
                var body = crate.AddComponent<Rigidbody>(); body.mass = 9;
                body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
                body.maxAngularVelocity = 10;
                host.BindBody(containers[i], body, 0.75f); access.BindTarget(containers[i], crate.transform);
                crate.AddComponent<MaterialContainerFeedback>().Initialize(commands, containers[i], crate.GetComponent<Renderer>());
            }
        }

        private void BuildMachines()
        {
            world.Production.RegisterMachine(machines[0], new MachineRecipe(Id(450), MaterialKind.Ore, MaterialKind.CrushedOre,
                6000, 3000, 1500, 128, yieldPermille: 950));
            world.Production.RegisterMachine(machines[1], new MachineRecipe(Id(451), MaterialKind.CrushedOre, MaterialKind.Fuel,
                9000, 4500, 1500, 128));
            BuildMachine(machines[0], "Crusher", new Vector3(-4, 0, 5));
            BuildMachine(machines[1], "Fuel processor", new Vector3(0.5f, 0, 5));
        }

        private void BuildMachine(Guid id, string name, Vector3 position)
        {
            var machine = SandboxPrimitives.Empty(name, root.transform, position);
            SandboxPrimitives.Box("Machine case", machine.transform, new Vector3(0, 0.9f, 0), new Vector3(1.5f, 1.8f, 1.2f), shapes.Steel);
            SandboxPrimitives.Box("Loading support", machine.transform, new Vector3(0, 0.65f, -1.1f), new Vector3(0.85f, 0.12f, 0.85f), shapes.Yellow);
            var slot = SandboxPrimitives.Empty("Explicit loading slot", machine.transform, new Vector3(0, 1.05f, -1.1f));
            host.BindSlot(id, slot.transform); access.BindTarget(id, machine.transform);
            var face = SandboxPrimitives.Box("Status face", machine.transform, new Vector3(0, 1.5f, -0.62f), new Vector3(0.7f, 0.25f, 0.04f), shapes.Lamp, false);
            var rotor = SandboxPrimitives.Empty("Process spindle pivot", machine.transform, new Vector3(0.45f, 1, -0.68f));
            var rotorDisc = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Process spindle disc", rotor.transform,
                Vector3.zero, new Vector3(0.5f, 0.1f, 0.5f), shapes.Dark, false);
            rotorDisc.transform.localRotation = Quaternion.Euler(90, 0, 0);
            SandboxPrimitives.Box("Spindle rotation marker", rotor.transform, new Vector3(0, 0, -0.11f),
                new Vector3(0.36f, 0.055f, 0.025f), shapes.Yellow, false);
            var light = SandboxPrimitives.PointLight("Status lamp", machine.transform, new Vector3(0, 1.8f, -0.85f), Color.green, 0.5f, 2.5f);
            machine.AddComponent<MachineFeedback>().Initialize(commands, id, face.GetComponent<Renderer>(), light, rotor.transform);
        }

        private void BuildReactor()
        {
            world.Reactor.Register(reactor, new ReactorDefinition(Id(501), millisecondsPerFuelUnit: 5000,
                powerQuantumMilliseconds: 500, warningMilliseconds: 6000, tripMilliseconds: 12000,
                resetMilliseconds: 1000, emergencyReliefMilliseconds: 5000));
            var room = SandboxPrimitives.Empty("Reactor fixture", root.transform, new Vector3(5.5f, 0, 6));
            SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Core housing", room.transform, new Vector3(0, 1.4f, 0),
                new Vector3(1.5f, 1.4f, 1.5f), shapes.Steel);
            SandboxPrimitives.Box("Fuel loading support", room.transform, new Vector3(0, 0.65f, -1.3f), new Vector3(0.85f, 0.12f, 0.85f), shapes.Yellow);
            var slot = SandboxPrimitives.Empty("Reactor fuel slot", room.transform, new Vector3(0, 1.05f, -1.3f));
            host.BindSlot(reactor, slot.transform); access.BindTarget(reactor, room.transform);
            var face = SandboxPrimitives.Box("Reactor status", room.transform, new Vector3(0, 2.2f, -0.78f), new Vector3(0.8f, 0.3f, 0.05f), shapes.Lamp, false);
            var valve = SandboxPrimitives.Empty("Cooling valve pivot", room.transform, new Vector3(1.2f, 1.1f, -0.5f));
            var valveDisc = SandboxPrimitives.Shape(PrimitiveType.Cylinder, "Cooling valve wheel", valve.transform,
                Vector3.zero, new Vector3(0.5f, 0.08f, 0.5f), shapes.Yellow, false);
            valveDisc.transform.localRotation = Quaternion.Euler(90, 0, 0);
            SandboxPrimitives.Box("Cooling valve position marker", valve.transform, new Vector3(0, 0, -0.095f),
                new Vector3(0.35f, 0.055f, 0.025f), shapes.Dark, false);
            var light = SandboxPrimitives.PointLight("Reactor warning beacon", room.transform, new Vector3(0, 3.1f, 0), Color.cyan, 0.5f, 4);
            room.AddComponent<ReactorFeedback>().Initialize(commands, face.GetComponent<Renderer>(), light, valve.transform);
        }

        private void BuildCart()
        {
            world.RegisterObject(cartId);
            var rig = SandboxPrimitives.Empty("Physical ore cart", root.transform, new Vector3(5, 0.45f, -1.5f));
            var body = rig.AddComponent<Rigidbody>(); body.mass = 35; body.centerOfMass = new Vector3(0, -0.15f, 0);
            body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            SandboxPrimitives.Box("Cart bed", rig.transform, Vector3.zero, new Vector3(1.2f, 0.18f, 1.8f), shapes.Steel);
            SandboxPrimitives.Box("Left cargo rail", rig.transform, new Vector3(-0.62f, 0.35f, 0), new Vector3(0.1f, 0.7f, 1.8f), shapes.Yellow);
            SandboxPrimitives.Box("Right cargo rail", rig.transform, new Vector3(0.62f, 0.35f, 0), new Vector3(0.1f, 0.7f, 1.8f), shapes.Yellow);
            SandboxPrimitives.Box("Cart rear rail", rig.transform, new Vector3(0, 0.35f, -0.92f), new Vector3(1.2f, 0.7f, 0.1f), shapes.Steel);
            var handle = SandboxPrimitives.Empty("Cart rear grip", rig.transform, new Vector3(0, 0.9f, -1.15f));
            SandboxPrimitives.Box("Cart handle bar", handle.transform, Vector3.zero, new Vector3(1.1f, 0.08f, 0.08f), shapes.Dark);
            var stand = SandboxPrimitives.Empty("Cart operator stance", rig.transform, new Vector3(0, -0.45f, -2));
            host.BindCartHandle(cartId, body, handle.transform, stand.transform); access.BindTarget(cartId, rig.transform);
            var sensor = SandboxPrimitives.Empty("Cargo observation bounds", rig.transform, new Vector3(0, 0.65f, 0));
            var bounds = sensor.AddComponent<BoxCollider>(); bounds.isTrigger = true; bounds.size = new Vector3(1.1f, 1.1f, 1.65f);
            cargo = sensor.AddComponent<CartCargoSensor>(); cargo.Initialize(body, host.IsBodyFree);
            cart = rig.AddComponent<CartMotor>(); cart.SafeCargoMass = 35;
            cart.Initialize(() => world.View.Phase == WorldPhase.Running && host.IsHandleHeld(cartId) && !cargo.Saturated, () => cargo.Mass);
            var loadFace = SandboxPrimitives.Box("Cart load warning face", rig.transform, new Vector3(0.48f, 0.8f, -0.96f),
                new Vector3(0.16f, 0.16f, 0.04f), shapes.Lamp, false);
            var loadLamp = SandboxPrimitives.PointLight("Cart overload beacon", rig.transform, new Vector3(0.48f, 0.95f, -0.95f), Color.green, 0.2f, 1.6f);
            rig.AddComponent<CartLoadFeedback>().Initialize(loadFace.GetComponent<Renderer>(), loadLamp,
                () => cart.Overloaded, () => cargo.Saturated);
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
            rig.AddComponent<ConveyorBeltMotion>().Initialize(belt, markers, 4);
        }

        private static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);

        public void Dispose()
        {
            if (disposed) return;
            disposed = true;
            if (host != null) host.Shutdown();
            if (root != null) { root.SetActive(false); UnityEngine.Object.Destroy(root); }
            access?.Clear(); shapes?.Dispose();
        }
    }
}
