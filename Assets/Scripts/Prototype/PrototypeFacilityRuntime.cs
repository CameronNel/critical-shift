using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeFacilityPhase
    {
        Briefing, SuitPreparation, MineExtraction, CartLoading, CartHaulage,
        HopperUnload, Crusher, Sorter, Processor, Dryer, FuelAssembly, Inspection,
        FuelDelivery, CoolingStartup, ReactorStartup, GridDemand, PowerGeneration,
        CoolingEmergency, Complete, Failed
    }

    /// <summary>
    /// Binds the playable shift to the authored fourteen-zone facility. The mine,
    /// haulage route, refinery line, fuel corridor and reactor hall are the game;
    /// no detached prototype arena is created when this runtime is active.
    /// </summary>
    public sealed class PrototypeFacilityRuntime : MonoBehaviour
    {
        public static PrototypeFacilityRuntime Instance { get; private set; }

        public const float EnergyTarget = 12f;
        public PrototypeFacilityPhase Phase { get; private set; } = PrototypeFacilityPhase.Briefing;
        public int ExtractedOre { get; private set; }
        public int LoadedFuel { get { return reactor == null ? 0 : reactor.LoadedBatches; } }
        public int ReservePower { get; private set; } = 100;
        public float EnergyDelivered { get; private set; }
        public bool SuitSafe { get; private set; }
        public bool PumpStarted { get; private set; }
        public bool GridConnected { get; private set; }
        public string BatchStage { get; private set; } = "NONE";
        public string Objective { get { return guidance == null ? string.Empty : guidance.ObjectiveLabel; } }
        public string TargetLabel { get { return guidance == null ? string.Empty : guidance.TargetLabel; } }
        public float TargetDistance
        {
            get
            {
                if (guidance == null || guidance.Model == null || !guidance.Model.HasTarget || player == null) return 0f;
                Vector3 delta = guidance.Model.TargetWorldPosition - player.transform.position;
                delta.y = 0f;
                return delta.magnitude;
            }
        }
        public PrototypeFacilityCart Cart { get { return cart; } }
        public PrototypeCrusher Crusher { get { return crusher; } }
        public PrototypeSuitSequence SuitSequence { get { return suitSequence; } }
        public PrototypeBatch CurrentBatch { get { return currentBatch; } }

        static readonly Vector3 PlayerSpawn = new Vector3(-72f, .06f, -40.2f);
        static readonly Vector3 BriefingPosition = new Vector3(-72f, .25f, -35.34f);
        static readonly Vector3 SuitPosition = new Vector3(-59.16f, 0f, -49.5f);
        static readonly Vector3 MinePosition = new Vector3(-88.8f, -1.2f, 2.4f);
        static readonly Vector3 CartPosition = new Vector3(-81.6f, -1.2f, -.6f);
        static readonly Vector3 HopperPosition = new Vector3(-43.8f, 0f, -28.2f);
        static readonly Vector3 CrusherPosition = new Vector3(-39.6f, 0f, -28.2f);
        static readonly Vector3 SorterPosition = new Vector3(-27.6f, 0f, -31.2f);
        static readonly Vector3 ProcessorPosition = new Vector3(-19.2f, 0f, -31.2f);
        static readonly Vector3 DryerPosition = new Vector3(-12f, 0f, -31.2f);
        static readonly Vector3 AssemblyPosition = new Vector3(-1.2f, 0f, -31.2f);
        static readonly Vector3 InspectionPosition = new Vector3(6f, 0f, -31.2f);
        static readonly Vector3 FuelReceivingPosition = new Vector3(-4.2f, 0f, -7.8f);
        static readonly Vector3 PumpPosition = new Vector3(-4.8f, 0f, 7.8f);
        static readonly Vector3 ReactorControlPosition = new Vector3(2.4f, 0f, -7.8f);
        static readonly Vector3 DemandPosition = new Vector3(7.2f, 0f, -4.5f);
        static readonly Vector3 EmergencyCoolingPosition = new Vector3(3f, 0f, 7.8f);

        readonly List<GameObject> runtimeCargo = new List<GameObject>();
        readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();
        PrototypeGameDirector director;
        PrototypePlayerController player;
        PrototypeFacilityGuidance guidance;
        PrototypeFacilityCart cart;
        PrototypeFacilityCartRouteDriver cartDriver;
        PrototypeSuitSequence suitSequence;
        PrototypeCrusher crusher;
        PrototypeSorter sorter;
        PrototypeProcessor processor;
        PrototypeDryer dryer;
        PrototypeFuelAssemblyStation assembler;
        PrototypeInspectionStation inspection;
        PrototypeReactorMachine reactor;
        PrototypeCoolingValve coolingValve;
        PrototypeDemandGauge demandGauge;
        PrototypeReanimationStation ocru;
        PrototypeTntWall tnt;
        PrototypeWorkerBody trainingWorker;
        PrototypeWorkerBody infiltratorBody;
        PrototypeBatch currentBatch;
        GameObject batchToken;
        Renderer batchTokenRenderer;
        Light reactorGlow;
        Vector3 cartStart;
        Vector3 workerStart;
        Vector3 infiltratorStart;
        bool built;
        bool crusherFaultAnnounced;
        bool emergencyAnnounced;
        bool sabotageApplied;

        void Awake()
        {
            if (Instance != null && Instance != this) { DestroyRuntimeObject(gameObject); return; }
            Instance = this;
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        public void Build()
        {
            if (built) return;
            built = true;
            if (Instance == null) Instance = this;
            director = PrototypeGameDirector.Instance ?? FindAnyObjectByType<PrototypeGameDirector>();
            director?.EnsureRuntimeReady();
            player = FindAnyObjectByType<PrototypePlayerController>();
            BuildGuidance();
            BindArrival();
            BindMineAndCart();
            BindRefinery();
            BindReactor();
            BindRecoveryAndSocial();
            ResetWorld(false);
            Debug.Log("[PrototypeFacility] Full route online: Arrival -> Gullet Mine -> Cart Haulage -> Crusher -> Sorter -> Processor -> Dryer -> Fuel -> Reactor.");
        }

        void BuildGuidance()
        {
            var beaconObject = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            beaconObject.name = "[GUIDANCE] Current Full-Map Objective";
            beaconObject.transform.SetParent(transform);
            beaconObject.transform.localScale = new Vector3(.18f, 2.5f, .18f);
            beaconObject.GetComponent<Renderer>().sharedMaterial = MaterialFor("guidance", new Color(.05f, .8f, 1f), true);
            DestroyRuntimeObject(beaconObject.GetComponent<Collider>());
            beaconObject.AddComponent<PrototypeFacilityGuidanceBeacon>();
            guidance = gameObject.AddComponent<PrototypeFacilityGuidance>();
        }

        void BindArrival()
        {
            BindStation("[MACHINE] BRIEFING BOARD", PrototypeStation.FacilityBriefing,
                "accept the 25-minute power contract", null, BriefingPosition);
            var suitObject = BindStation("[MACHINE] SUIT INTEGRITY TEST", PrototypeStation.FacilitySuit,
                "run the complete suit sequence", "skip the suit for speed", SuitPosition);
            suitSequence = GetOrAdd<PrototypeSuitSequence>(suitObject);
            // Four authored steps at four seconds each keeps the safe route inside the
            // spec's 15-30 second target while the unsafe bypass remains immediate.
            suitSequence.stepSeconds = 4f;
            suitSequence.StepChanged += step =>
            {
                SetMessage("SUIT PROCEDURE: " + suitSequence.CurrentStep + "  " + Mathf.RoundToInt(suitSequence.Progress * 100f) + "%");
            };
            suitSequence.Completed += result =>
            {
                SuitSafe = result == PrototypeSuitSequence.Result.SafeComplete;
                player?.SetSuitState(true);
                if (!SuitSafe)
                {
                    director?.Social?.Incidents.AddPlayerPressure(2);
                    Ledger("Crew skipped the suit integrity test", "Telemetry showed an incomplete seal", "Contamination and compliance risk increased", "Use decontamination before the next shift");
                }
                SetPhase(PrototypeFacilityPhase.MineExtraction, PrototypeShiftState.Mining,
                    "Extract three physical ore chunks from the GULLET MINE. [E] drill, [F] mine the wet seam.",
                    "EXTRACT ORE IN GULLET MINE", MinePosition);
            };
        }

        void BindMineAndCart()
        {
            BindStation("[MACHINE] DRILL RIG", PrototypeStation.FacilityMineFace,
                "drill one dry ore chunk", "blast the wet seam (fast / risky)", MinePosition);
            var cartObject = FindClosestNamed("mine.cart.parked", CartPosition);
            if (cartObject == null) cartObject = CreateFallbackBlock("mine.cart.parked", CartPosition, new Vector3(1.2f, 1.2f, 1.8f), "cart");
            cartStart = cartObject.transform.position;
            var body = GetOrAdd<Rigidbody>(cartObject);
            body.mass = 95f;
            body.linearDamping = 2f;
            body.angularDamping = 4f;
            body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            cart = GetOrAdd<PrototypeFacilityCart>(cartObject);
            cart.ratedMass = 3f;
            cart.pushImpulse = 5f;
            cart.OreLoaded += OnCartLoaded;
            cart.OverloadWarning += excess =>
            {
                SetMessage("CART OVERLOAD " + excess.ToString("0.0") + "t — wheel squeal and derailment risk. Push carefully.");
                Ledger("Crew overloaded the ore cart", "Suspension compressed and wheels squealed", "Transport stability decreased", "Unload excess ore or accept the risk");
                director?.Social?.Incidents.AddPlayerPressure(1);
            };
            var loadTrigger = new GameObject("Physical Ore Cart Loading Volume");
            loadTrigger.transform.SetParent(cartObject.transform, false);
            loadTrigger.transform.localPosition = new Vector3(0f, .8f, 0f);
            var loadCollider = loadTrigger.AddComponent<BoxCollider>();
            loadCollider.isTrigger = true;
            loadCollider.size = new Vector3(1.8f, 1.4f, 2.2f);
            var cartTrigger = loadTrigger.AddComponent<PrototypeFacilityCartLoadTrigger>();
            cartTrigger.runtime = this;
            cartTrigger.cart = cart;
            var cartInteractable = GetOrAdd<PrototypeInteractable>(cartObject);
            cartInteractable.station = PrototypeStation.FacilityCart;
            cartInteractable.prompt = "release the brake and push the loaded cart to the refinery";
            cartDriver = cartObject.AddComponent<PrototypeFacilityCartRouteDriver>();
            cartDriver.Configure(cart, new[]
            {
                cartStart,
                new Vector3(-75.6f, -1.2f, 0f),
                new Vector3(-69f, -.2f, 0f),
                new Vector3(-63.6f, .8f, 0f),
                new Vector3(-60f, .8f, -12f),
                new Vector3(-43.8f, .8f, -12f),
                new Vector3(-43.8f, .8f, -28.2f)
            });
            cartDriver.Arrived += OnCartArrived;
            BindStation("[MACHINE] RECEIVING HOPPER", PrototypeStation.FacilityHopper,
                "tip the cart into the receiving hopper", null, new Vector3(-43.8f, -2f, -34.5f));
            // The authored hopper body sits below the deck and is outside the player's
            // interaction reach. Keep that real machine as the visual target and add a
            // compact deck-side tip control where the cart route actually terminates.
            var hopperControl = CreateFallbackBlock("[CONTROL] HOPPER TIP LEVER",
                HopperPosition + new Vector3(0f, 1.1f, 0f), new Vector3(.8f, 1.2f, .8f), "control");
            BindExisting(hopperControl, PrototypeStation.FacilityHopper, "tip the cart into the receiving hopper", null);
        }

        void BindRefinery()
        {
            var crusherObject = BindStation("[MACHINE] PRIMARY CRUSHER", PrototypeStation.FacilityCrusher,
                "start or clear the primary crusher", "bypass the wet-ore interlock", CrusherPosition);
            crusher = GetOrAdd<PrototypeCrusher>(crusherObject);
            crusher.processSeconds = 3f;
            crusher.capacity = 4.5f;
            crusher.BeginOperation();
            var crusherAudio = GetOrAdd<PrototypeMachineAudio>(crusherObject);
            crusherAudio.Bind(crusher);

            var sorterObject = BindStation("[MACHINE] SORTER", PrototypeStation.FacilitySorter,
                "sort the crushed batch", "reduce scanning and run fast", SorterPosition);
            sorter = GetOrAdd<PrototypeSorter>(sorterObject);
            sorter.processSeconds = 2.5f; sorter.BeginOperation();
            GetOrAdd<PrototypeMachineAudio>(sorterObject).Bind(sorter);

            var processorObject = BindStation("[MACHINE] PROCESSOR", PrototypeStation.FacilityProcessor,
                "process the sorted material", "shorten the pressure cycle", ProcessorPosition);
            processor = GetOrAdd<PrototypeProcessor>(processorObject);
            processor.processSeconds = 3f; processor.BeginOperation();
            GetOrAdd<PrototypeMachineAudio>(processorObject).Bind(processor);

            var dryerObject = BindStation("[MACHINE] DRYER", PrototypeStation.FacilityDryer,
                "dry the processed material", "bypass the moisture filter", DryerPosition);
            dryer = GetOrAdd<PrototypeDryer>(dryerObject);
            dryer.processSeconds = 2.5f; dryer.BeginOperation();
            GetOrAdd<PrototypeMachineAudio>(dryerObject).Bind(dryer);

            var assemblyObject = BindStation("[MACHINE] FUEL ASSEMBLY", PrototypeStation.FacilityFuelAssembly,
                "press two reactor fuel assemblies", "reduce casing seal time", AssemblyPosition);
            assembler = GetOrAdd<PrototypeFuelAssemblyStation>(assemblyObject);
            assembler.processSeconds = 3f; assembler.BeginOperation();
            GetOrAdd<PrototypeMachineAudio>(assemblyObject).Bind(assembler);

            var inspectionObject = BindStation("[MACHINE] INSPECTION", PrototypeStation.FacilityInspection,
                "inspect and release the fuel", "approve with reduced confidence", InspectionPosition);
            inspection = GetOrAdd<PrototypeInspectionStation>(inspectionObject);
            inspection.processSeconds = 2f; inspection.BeginOperation();
            GetOrAdd<PrototypeMachineAudio>(inspectionObject).Bind(inspection);
        }

        void BindReactor()
        {
            var receiving = BindStation("[MACHINE] FUEL RECEIVING", PrototypeStation.FacilityFuelReceiving,
                "insert carried fuel into the reactor rack", null, FuelReceivingPosition);
            var portObject = new GameObject("Physical Reactor Fuel Receiving Port");
            portObject.transform.position = FuelReceivingPosition + Vector3.up;
            var port = portObject.AddComponent<BoxCollider>();
            port.isTrigger = true; port.size = new Vector3(3f, 2.4f, 3f);
            portObject.AddComponent<PrototypeFacilityFuelReceivingPort>().runtime = this;
            portObject.transform.SetParent(receiving.transform, true);

            var reactorObject = GameObject.Find("[MACHINE] REACTOR CORE");
            if (reactorObject == null)
                reactorObject = CreateFallbackBlock("[MACHINE] REACTOR CORE", Vector3.zero, new Vector3(4f, 3f, 4f), "reactor");
            reactor = GetOrAdd<PrototypeReactorMachine>(reactorObject);
            reactor.shortcutDelay = 8f;
            reactor.StageChanged += OnReactorStageChanged;
            GetOrAdd<PrototypeMachineAudio>(reactorObject).Bind(reactor);

            var pumpObject = BindStation("[MACHINE] COOLANT PUMP", PrototypeStation.FacilityReactorPump,
                "start the primary coolant pump", null, PumpPosition);
            var valveObject = BindStation("[MACHINE] COOLANT VALVES", PrototypeStation.FacilityCoolingValve,
                "open emergency coolant valves", null, new Vector3(-1.2f, 0f, 8.4f));
            coolingValve = GetOrAdd<PrototypeCoolingValve>(valveObject);
            coolingValve.opening = 0f;
            BindStation("[MACHINE] EMERGENCY COOLING", PrototypeStation.FacilityEmergencyCooling,
                "inject emergency cooling", null, EmergencyCoolingPosition);
            BindStation("[MACHINE] CONTROL POSITION", PrototypeStation.FacilityReactorControl,
                "raise control banks and start the reactor", "raise output too quickly", ReactorControlPosition);
            var demandObject = BindStation("[MACHINE] GRID DEMAND", PrototypeStation.FacilityGridDemand,
                "close the grid breaker and accept demand", "accept peak demand immediately", DemandPosition);
            demandGauge = GetOrAdd<PrototypeDemandGauge>(demandObject);
            demandGauge.demand = .35f;

            var glowObject = new GameObject("Reactor Operational Glow");
            glowObject.transform.position = new Vector3(0f, 2.2f, 0f);
            reactorGlow = glowObject.AddComponent<Light>();
            reactorGlow.type = LightType.Point;
            reactorGlow.color = new Color(.15f, .8f, 1f);
            reactorGlow.range = 18f;
            reactorGlow.intensity = 0f;
            glowObject.transform.SetParent(reactorObject.transform, true);
        }

        void BindRecoveryAndSocial()
        {
            var ocruObject = BindStation("[MACHINE] REANIMATION BAY", PrototypeStation.FacilityReanimation,
                "reanimate a nearby incapacitated worker (25 reserve power)", null, new Vector3(-18f, 0f, 31.2f));
            ocru = GetOrAdd<PrototypeReanimationStation>(ocruObject);
            ocru.ReanimationStarted += (body, cost) => Ledger("Worker was biologically offline", "OCRU requested reserve power", cost + "% reserve power was diverted", "Reanimation cycle started");
            ocru.ReanimationCompleted += body => SetMessage("OCRU COMPLETE — worker returned to service in recovery state.");

            trainingWorker = CreateWorker("Haulage Training Worker", new Vector3(-43.8f, 1f, -18f), new Color(.76f, .62f, .22f), PrototypeStation.LegitimateWorker,
                "check the worker's condition", null);
            workerStart = trainingWorker.transform.position;

            infiltratorBody = CreateWorker("Contract Worker 7", new Vector3(-24f, 1f, -22.8f), new Color(.22f, .58f, .52f), PrototypeStation.Infiltrator,
                "inspect worker credentials", "nonlethal bonk");
            infiltratorStart = infiltratorBody.transform.position;
            CreateWorker("Mara Voss // legitimate", new Vector3(2.4f, 1f, -22.8f), new Color(.62f, .56f, .22f), PrototypeStation.LegitimateWorker,
                "inspect suspicious legitimate worker", null);
            CreateWorker("Compliance Officer", new Vector3(9f, 1f, -24f), new Color(.28f, .4f, .68f), PrototypeStation.ComplianceOfficer,
                "cooperate with the inspection", "distract the officer");
            var evidence = CreateFallbackBlock("Evidence Locker", new Vector3(7f, .75f, -22f), new Vector3(1.2f, 1.5f, .8f), "evidence");
            BindExisting(evidence, PrototypeStation.EvidenceLocker, "hide recorded evidence", null);

            var tntObject = CreateFallbackBlock("Mine TNT Charge", new Vector3(-85.2f, -.3f, -9f), new Vector3(1.2f, 1.2f, .6f), "danger");
            BindExisting(tntObject, PrototypeStation.FacilityTnt, "arm a controlled TNT charge", "overcharge the wet seam");
            tnt = tntObject.AddComponent<PrototypeTntWall>();
            tnt.fuseSeconds = 3f; tnt.damageRadius = 7f;
            tnt.Detonated += OnTntDetonated;
        }

        void Update() { Tick(Time.deltaTime); }
        public void TickForTest(float seconds)
        {
            crusher?.Tick(seconds);
            demandGauge?.Tick(seconds);
            reactor?.Tick(seconds, demandGauge == null ? 0f : demandGauge.demand, coolingValve);
            Tick(seconds);
        }

        public void TickCartForTest(float seconds) { cartDriver?.TickForTest(seconds); }

        void Tick(float dt)
        {
            if (!built) return;
            if (guidance != null && guidance.Beacon != null) guidance.Beacon.UpdateDistance(player == null ? null : player.transform);
            sorter?.Tick(dt); processor?.Tick(dt); dryer?.Tick(dt); assembler?.Tick(dt); inspection?.Tick(dt);
            if (batchToken != null) batchToken.transform.Rotate(0f, 35f * dt, 0f, Space.World);
            CompleteFacilityMachineOutputs();

            if (crusher != null && crusher.state == CrusherState.Faulted && !crusherFaultAnnounced)
            {
                crusherFaultAnnounced = true;
                SetMessage("CRUSHER JAM — wet ore stopped the line. [E] clear and dry it, or [F] bypass the interlock.");
                Ledger("Wet ore entered the primary crusher", "Motor rhythm fell into a failure tone", "Crusher jam stopped the production line", "Clear and dry the batch or enable the bypass");
            }
            if (Phase == PrototypeFacilityPhase.Crusher && crusher != null && crusher.state == CrusherState.OutputReady)
            {
                currentBatch = crusher.TakeOutput();
                BatchStage = "CRUSHED";
                UpdateBatchToken("CRUSHED ORE", new Vector3(-32.4f, 5.6f, -31.2f), new Color(.58f, .43f, .25f));
                SetPhase(PrototypeFacilityPhase.Sorter, PrototypeShiftState.Refining,
                    "Crusher output is visible on the raised line. Reach SORTER and start the scan.", "START SORTER", SorterPosition);
            }

            if (reactor != null && reactor.IsRunning && GridConnected && (director == null || !director.IsTerminal))
            {
                EnergyDelivered += reactor.output * dt;
                director.SetPhysicalHeat(reactor.heat);
                if (reactorGlow != null) reactorGlow.intensity = 2.2f + Mathf.Sin(Time.time * 4f) * .8f;
                if (reactor.stage >= ReactorCrisisStage.CoolingEmergency && reactor.stage < ReactorCrisisStage.Contained && !emergencyAnnounced)
                {
                    emergencyAnnounced = true;
                    SetPhase(PrototypeFacilityPhase.CoolingEmergency, PrototypeShiftState.CoolingEmergency,
                        "DELAYED CONSEQUENCE — upstream defects overheated the reactor. Reach EMERGENCY COOLING.",
                        "INJECT EMERGENCY COOLING", EmergencyCoolingPosition);
                    Ledger("Unsafe refinery shortcuts produced defective fuel", "Heat, stability and alarm states crossed warning bands", "Cooling emergency entered", "Open emergency cooling in the reactor hall");
                }
                if (reactor.stage == ReactorCrisisStage.CriticalMeltdown)
                {
                    Phase = PrototypeFacilityPhase.Failed;
                    director.Fail("CRITICAL MELTDOWN — upstream warnings were ignored. " + director.Social.Debrief);
                }
                else if (Phase == PrototypeFacilityPhase.PowerGeneration && EnergyDelivered >= EnergyTarget)
                    CompleteShift(false, "Power quota delivered through the complete mine-to-reactor chain.");
            }

            if (!sabotageApplied && director.Social != null && director.Social.Infiltrator.Phase == PrototypeInfiltratorPhase.Sabotaging && Phase >= PrototypeFacilityPhase.Sorter)
            {
                sabotageApplied = true;
                director.Social.SabotageInfiltrator();
                if (currentBatch != null) currentBatch.hiddenDefect = Mathf.Clamp01(currentBatch.hiddenDefect + .08f);
                SetMessage("SABOTAGE WARNING — Contract Worker 7 was near the production line. Inspect both workers before accusing anyone.");
            }
        }

        void CompleteFacilityMachineOutputs()
        {
            if (Phase == PrototypeFacilityPhase.Sorter && sorter != null && sorter.state == FacilityMachineState.OutputReady)
            {
                currentBatch = sorter.TakeOutput(); BatchStage = "SORTED";
                UpdateBatchToken("SORTED BATCH", new Vector3(-22.5f, 5.8f, -31.2f), new Color(.58f, .68f, .42f));
                SetPhase(PrototypeFacilityPhase.Processor, PrototypeShiftState.Refining,
                    "Sorted batch moved downstream. Start PROCESSOR.", "START PROCESSOR", ProcessorPosition);
            }
            else if (Phase == PrototypeFacilityPhase.Processor && processor != null && processor.state == FacilityMachineState.OutputReady)
            {
                currentBatch = processor.TakeOutput(); BatchStage = "PROCESSED";
                UpdateBatchToken("PROCESSED MATERIAL", new Vector3(-14.7f, 6.3f, -31.2f), new Color(.28f, .72f, .58f));
                SetPhase(PrototypeFacilityPhase.Dryer, PrototypeShiftState.Refining,
                    "Processed material entered the next belt. Start DRYER.", "START DRYER", DryerPosition);
            }
            else if (Phase == PrototypeFacilityPhase.Dryer && dryer != null && dryer.state == FacilityMachineState.OutputReady)
            {
                currentBatch = dryer.TakeOutput(); BatchStage = "DRIED";
                UpdateBatchToken("DRIED MATERIAL", new Vector3(-6f, 5.3f, -31.2f), new Color(.72f, .66f, .34f));
                SetPhase(PrototypeFacilityPhase.FuelAssembly, PrototypeShiftState.Refining,
                    "Dry material reached FUEL ASSEMBLY. Press two reactor loads.", "ASSEMBLE FUEL", AssemblyPosition);
            }
            else if (Phase == PrototypeFacilityPhase.FuelAssembly && assembler != null && assembler.state == FacilityMachineState.OutputReady)
            {
                currentBatch = assembler.TakeOutput(); BatchStage = "ASSEMBLED";
                UpdateBatchToken("FUEL COMPONENTS", new Vector3(3.9f, 4.4f, -31.2f), new Color(.92f, .64f, .15f));
                SetPhase(PrototypeFacilityPhase.Inspection, PrototypeShiftState.Refining,
                    "Fuel components reached INSPECTION. Verify them before release.", "INSPECT FUEL", InspectionPosition);
            }
            else if (Phase == PrototypeFacilityPhase.Inspection && inspection != null && inspection.state == FacilityMachineState.OutputReady)
            {
                currentBatch = inspection.TakeOutput(); BatchStage = "INSPECTED";
                if (batchToken != null) { DestroyRuntimeObject(batchToken); batchToken = null; }
                SpawnFuelAssemblies(currentBatch);
                SetPhase(PrototypeFacilityPhase.FuelDelivery, PrototypeShiftState.Refining,
                    "Two physical fuel assemblies released. Carry both through the FUEL CORRIDOR to REACTOR FUEL RECEIVING.",
                    "DELIVER 2 FUEL ASSEMBLIES", FuelReceivingPosition);
            }
        }

        public bool HandleInteraction(PrototypeStation station, bool shortcut)
        {
            switch (station)
            {
                case PrototypeStation.FacilityBriefing: BeginShift(); return true;
                case PrototypeStation.FacilitySuit: UseSuit(shortcut); return true;
                case PrototypeStation.FacilityMineFace: ExtractOre(shortcut); return true;
                case PrototypeStation.FacilityCart: PushCart(); return true;
                case PrototypeStation.FacilityHopper: UnloadCart(); return true;
                case PrototypeStation.FacilityCrusher: UseCrusher(shortcut); return true;
                case PrototypeStation.FacilitySorter: UseSorter(shortcut); return true;
                case PrototypeStation.FacilityProcessor: UseProcessor(shortcut); return true;
                case PrototypeStation.FacilityDryer: UseDryer(shortcut); return true;
                case PrototypeStation.FacilityFuelAssembly: UseAssembler(shortcut); return true;
                case PrototypeStation.FacilityInspection: UseInspection(shortcut); return true;
                case PrototypeStation.FacilityFuelReceiving: SetMessage("DROP a carried fuel assembly into the highlighted receiving port."); return true;
                case PrototypeStation.FacilityReactorPump: StartPump(); return true;
                case PrototypeStation.FacilityCoolingValve:
                case PrototypeStation.FacilityEmergencyCooling: UseEmergencyCooling(); return true;
                case PrototypeStation.FacilityReactorControl: StartReactor(shortcut); return true;
                case PrototypeStation.FacilityGridDemand: AcceptGridDemand(shortcut); return true;
                case PrototypeStation.FacilityReanimation: TryReanimate(); return true;
                case PrototypeStation.FacilityTnt: ArmTnt(shortcut); return true;
                case PrototypeStation.Infiltrator: HandleInfiltrator(shortcut); return true;
                case PrototypeStation.LegitimateWorker: InspectLegitimateWorker(); return true;
                case PrototypeStation.ComplianceOfficer: HandleOfficer(shortcut); return true;
                case PrototypeStation.EvidenceLocker: HideEvidence(); return true;
                case PrototypeStation.OfficerBonk: BonkOfficer(); return true;
                default: return false;
            }
        }

        void BeginShift()
        {
            if (Phase != PrototypeFacilityPhase.Briefing) { SetMessage("SHIFT ALREADY ACTIVE — follow the cyan objective beacon."); return; }
            director?.SetRuntimeState(PrototypeShiftState.Mining,
                "CONTRACT ACCEPTED — suit up, extract three chunks, haul them to the refinery and deliver two fuel assemblies to the reactor.");
            director?.Social?.Officer.BeginInspection();
            SetPhase(PrototypeFacilityPhase.SuitPreparation, PrototypeShiftState.Mining,
                "Go to the LOCKER ROOM and run the suit procedure. [F] skips it for speed and creates evidence.",
                "PUT ON PROTECTIVE SUIT", SuitPosition);
        }

        void UseSuit(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.SuitPreparation) { SetMessage("Suit station is not the current objective."); return; }
            if (shortcut)
            {
                SuitSafe = false; player?.SetSuitState(false);
                director?.Social?.Incidents.AddPlayerPressure(2);
                Ledger("Crew skipped protective equipment", "Suit telemetry remained offline", "Movement improved but radiation/compliance risk increased", "Return through decontamination before shift end");
                SetPhase(PrototypeFacilityPhase.MineExtraction, PrototypeShiftState.Mining,
                    "SUIT SKIPPED — move faster, but the mine and officer will record it. Extract three chunks.",
                    "EXTRACT ORE IN GULLET MINE", MinePosition);
                return;
            }
            if (!suitSequence.IsRunning)
            {
                suitSequence.Begin();
                SetMessage("SUIT PROCEDURE STARTED — equip layer, seal helmet, test integrity, collect dosimeter.");
            }
        }

        void ExtractOre(bool wetShortcut)
        {
            if (Phase != PrototypeFacilityPhase.MineExtraction && Phase != PrototypeFacilityPhase.CartLoading)
            { SetMessage("MINE LOCKED — complete the current production objective first."); return; }
            if (ExtractedOre >= PrototypeShiftRules.OreQuota) { SetMessage("ORE QUOTA EXTRACTED — physically load the cart."); return; }
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = wetShortcut ? "Gullet Wet Ore Chunk" : "Gullet Dry Ore Chunk";
            go.transform.position = new Vector3(-87.6f + ExtractedOre * .7f, -.7f, -2.4f);
            go.transform.localScale = wetShortcut ? new Vector3(1.05f, .78f, .9f) : new Vector3(.82f, .65f, .74f);
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(wetShortcut ? "wetOre" : "ore", wetShortcut ? new Color(.16f, .42f, .38f) : new Color(.38f, .28f, .2f));
            var ore = go.AddComponent<PrototypeOre>();
            ore.batch = new PrototypeBatch
            {
                id = "gullet-" + (ExtractedOre + 1), mass = wetShortcut ? 1.35f : .85f,
                grade = wetShortcut ? .82f : .68f, rock = .22f,
                moisture = wetShortcut ? .65f : .06f, contamination = wetShortcut ? .08f : .02f,
                wetShortcut = wetShortcut
            };
            ore.Body.mass = ore.batch.mass * 4f;
            go.AddComponent<PrototypeCarryable>();
            runtimeCargo.Add(go);
            ExtractedOre++;
            if (wetShortcut)
            {
                director?.Social?.Incidents.AddPlayerPressure(2);
                Ledger("Crew mined the wet seam without drainage", "Ore glistened and weighed more", "Cart overload and crusher jam risk increased", "Dry the batch or accept a downstream bypass");
            }
            director?.SetProductionCounts(ExtractedOre, LoadedFuel);
            if (ExtractedOre >= PrototypeShiftRules.OreQuota)
                SetPhase(PrototypeFacilityPhase.CartLoading, PrototypeShiftState.Mining,
                    "Three chunks extracted. Grab each with [G/right mouse] and drop it into the parked mine cart.",
                    "LOAD 3 ORE INTO CART", cart.transform.position);
            else SetMessage("ORE EXTRACTED " + ExtractedOre + "/" + PrototypeShiftRules.OreQuota + " — the chunk is physical; carry it to the parked cart.");
        }

        public bool TryLoadCartOre(PrototypeOre ore)
        {
            if ((Phase != PrototypeFacilityPhase.MineExtraction && Phase != PrototypeFacilityPhase.CartLoading) ||
                ore == null || cart == null) return false;
            ReleaseHeld(ore.gameObject);
            return cart.TryLoad(ore);
        }

        void OnCartLoaded(PrototypeOre ore)
        {
            SetMessage("CART LOAD " + cart.CargoCount + "/" + PrototypeShiftRules.OreQuota + "  MASS " + cart.CurrentMass.ToString("0.0") + "/" + cart.ratedMass.ToString("0.0") + "t");
            if (cart.CargoCount >= PrototypeShiftRules.OreQuota)
                SetWorldObjective("PUSH LOADED CART TO CRUSHER", "LOADED MINE CART", cart.transform.position);
        }

        void PushCart()
        {
            if (Phase == PrototypeFacilityPhase.CartLoading)
            {
                if (cart.CargoCount < PrototypeShiftRules.OreQuota) { SetMessage("CART NEEDS 3 ORE CHUNKS BEFORE DEPARTURE."); return; }
                Phase = PrototypeFacilityPhase.CartHaulage;
                director?.SetRuntimeState(PrototypeShiftState.Mining, "CART ROLLING — follow it through haulage to the crusher tipping deck.");
                SetWorldObjective("FOLLOW CART TO RECEIVING HOPPER", "MOVING ORE CART", HopperPosition);
                cartDriver.BeginRoute(cart.IsOverloaded ? .78f : 1f);
            }
            else if (Phase == PrototypeFacilityPhase.CartHaulage) cartDriver.BeginRoute(cart.IsOverloaded ? .78f : 1f);
            else SetMessage("CART BRAKE LOCKED FOR THE CURRENT PHASE.");
        }

        void OnCartArrived()
        {
            SetPhase(PrototypeFacilityPhase.HopperUnload, PrototypeShiftState.Mining,
                "Cart reached the crusher deck. [E] at RECEIVING HOPPER to tip and merge the ore batch.",
                "TIP CART INTO HOPPER", HopperPosition);
        }

        void UnloadCart()
        {
            if (Phase != PrototypeFacilityPhase.HopperUnload) { SetMessage("HOPPER WAITING FOR THE LOADED MINE CART."); return; }
            if (cart.CargoCount == 0) { SetMessage("CART IS EMPTY."); return; }
            currentBatch = AggregateCartBatch(cart.Cargo);
            var unloaded = new List<PrototypeOre>(cart.Cargo);
            var hopperTarget = new GameObject("Hopper Batch Drop").transform;
            hopperTarget.position = new Vector3(-43.8f, -2f, -34.5f);
            runtimeCargo.Add(hopperTarget.gameObject);
            cart.UnloadBatch(hopperTarget);
            foreach (var ore in unloaded) if (ore != null) { runtimeCargo.Remove(ore.gameObject); DestroyRuntimeObject(ore.gameObject, 1.2f); }
            BatchStage = "RAW BATCH";
            UpdateBatchToken("RAW ORE BATCH", new Vector3(-42f, -2.4f, -29.4f), new Color(.42f, .3f, .2f));
            SetPhase(PrototypeFacilityPhase.Crusher, PrototypeShiftState.Refining,
                "Ore merged in the hopper. Start PRIMARY CRUSHER; wet ore may jam unless bypassed.",
                "START PRIMARY CRUSHER", CrusherPosition);
        }

        void UseCrusher(bool unsafeBypass)
        {
            if (Phase != PrototypeFacilityPhase.Crusher || currentBatch == null) { SetMessage("CRUSHER HAS NO CURRENT BATCH."); return; }
            if (crusher.state == CrusherState.Faulted)
            {
                crusher.Repair(); crusher.FinishRepair();
                crusherFaultAnnounced = false;
                if (!unsafeBypass) currentBatch = currentBatch.Dry();
            }
            crusher.SetUnsafeBypass(unsafeBypass);
            if (crusher.state == CrusherState.Starting) { SetMessage("CRUSHER STARTING — wait for idle tone."); return; }
            if (crusher.state == CrusherState.Idle && crusher.Accept(currentBatch))
            {
                if (unsafeBypass)
                {
                    director?.Social?.Incidents.AddPlayerPressure(2);
                    Ledger("Crew bypassed the crusher moisture interlock", "Warning tone acknowledged the disabled gate", "Hidden fuel defect entered the production chain", "Inspection or emergency cooling can still catch the consequence");
                }
                SetMessage(unsafeBypass ? "CRUSHER BYPASS ACTIVE — throughput restored, hidden defect possible." : "PRIMARY CRUSHER RUNNING — listen and watch the batch status.");
            }
        }

        void UseSorter(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.Sorter) { SetMessage("SORTER WAITING FOR CRUSHED MATERIAL."); return; }
            sorter.SetUnsafeShortcut(shortcut);
            if (sorter.Accept(currentBatch)) SetMessage(shortcut ? "SORTER FAST SCAN — mixed material risk." : "SORTER SCANNING — rock fraction is visibly separating.");
        }

        void UseProcessor(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.Processor) { SetMessage("PROCESSOR WAITING FOR SORTED MATERIAL."); return; }
            processor.SetUnsafeShortcut(shortcut);
            if (processor.Accept(currentBatch)) SetMessage(shortcut ? "PROCESSOR SHORT CYCLE — pressure warning acknowledged." : "PROCESSOR RUNNING CONTROLLED TEMPERATURE/PRESSURE CYCLE.");
        }

        void UseDryer(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.Dryer) { SetMessage("DRYER WAITING FOR PROCESSED MATERIAL."); return; }
            dryer.SetUnsafeShortcut(shortcut);
            if (dryer.Accept(currentBatch)) SetMessage(shortcut ? "DRYER FILTER BYPASSED — retained moisture possible." : "DRYER RUNNING — moisture is leaving the batch.");
        }

        void UseAssembler(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.FuelAssembly) { SetMessage("ASSEMBLY STATION WAITING FOR DRIED MATERIAL."); return; }
            assembler.SetUnsafeShortcut(shortcut);
            if (assembler.Accept(currentBatch)) SetMessage(shortcut ? "HIGH-SPEED FUEL PRESS — casing confidence reduced." : "FUEL ASSEMBLY PRESS RUNNING — two physical loads will be released.");
        }

        void UseInspection(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.Inspection) { SetMessage("INSPECTION WAITING FOR ASSEMBLED FUEL."); return; }
            inspection.SetUnsafeShortcut(shortcut);
            if (inspection.Accept(currentBatch)) SetMessage(shortcut ? "FUEL APPROVED WITH LOW CONFIDENCE — downstream risk accepted." : "FUEL INSPECTION RUNNING — quality and hidden-defect confidence checked.");
        }

        public bool TryLoadFuel(PrototypeFuelAssembly fuel)
        {
            if (Phase != PrototypeFacilityPhase.FuelDelivery || fuel == null || reactor == null) return false;
            ReleaseHeld(fuel.gameObject);
            if (!reactor.LoadFuel(fuel)) return false;
            runtimeCargo.Remove(fuel.gameObject);
            DestroyRuntimeObject(fuel.gameObject);
            director?.SetProductionCounts(ExtractedOre, reactor.LoadedBatches);
            SetMessage("REACTOR FUEL RECEIVING " + reactor.LoadedBatches + "/" + PrototypeShiftRules.FuelQuota);
            if (reactor.LoadedBatches >= PrototypeShiftRules.FuelQuota)
                SetPhase(PrototypeFacilityPhase.CoolingStartup, PrototypeShiftState.Reactor,
                    "Both fuel assemblies are in the rack. Confirm cooling by starting the COOLANT PUMP.",
                    "START REACTOR COOLANT PUMP", PumpPosition);
            return true;
        }

        void StartPump()
        {
            if (Phase != PrototypeFacilityPhase.CoolingStartup) { SetMessage("PUMP CONTROL NOT REQUIRED FOR CURRENT PHASE."); return; }
            PumpStarted = true; coolingValve.opening = 1f;
            SetPhase(PrototypeFacilityPhase.ReactorStartup, PrototypeShiftState.Reactor,
                "COOLING FLOW CONFIRMED — go to CONTROL POSITION and start the reactor.",
                "START REACTOR", ReactorControlPosition);
        }

        void StartReactor(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.ReactorStartup || !PumpStarted) { SetMessage("REACTOR REFUSED — load 2 fuel and confirm cooling first."); return; }
            if (shortcut) reactor.UseUnsafeShortcut();
            if (!reactor.StartReactor()) { SetMessage("REACTOR START REFUSED — check fuel receiving."); return; }
            SetPhase(PrototypeFacilityPhase.GridDemand, PrototypeShiftState.Reactor,
                "REACTOR HUM ONLINE — close GRID DEMAND breaker to begin contract delivery.",
                "CONNECT REACTOR TO GRID", DemandPosition);
        }

        void AcceptGridDemand(bool shortcut)
        {
            if (Phase != PrototypeFacilityPhase.GridDemand) { SetMessage("GRID BREAKER ALREADY SET OR REACTOR OFFLINE."); return; }
            GridConnected = true;
            demandGauge.demand = shortcut ? .9f : .62f;
            if (shortcut)
            {
                reactor.UseUnsafeShortcut();
                director?.Social?.Incidents.AddPlayerPressure(2);
                Ledger("Crew accepted peak grid demand immediately", "Demand gauge jumped into the red band", "Reactor heat margin narrowed", "Reduce risk with clean fuel and active cooling");
            }
            SetPhase(PrototypeFacilityPhase.PowerGeneration, PrototypeShiftState.Reactor,
                "POWER FLOWING — watch output, demand, heat and stability until the quota is met.",
                "MONITOR OPERATING REACTOR", Vector3.zero);
            guidance.SetWorldTarget("OPERATING REACTOR", Vector3.zero, "DELIVER " + EnergyTarget.ToString("0") + " ENERGY");
        }

        void UseEmergencyCooling()
        {
            if (Phase != PrototypeFacilityPhase.CoolingEmergency) { SetMessage("EMERGENCY COOLING ARMED — no crisis currently requires injection."); return; }
            coolingValve.opening = 1f;
            if (reactor.EmergencyCooling() && reactor.stage == ReactorCrisisStage.Contained)
            {
                Ledger("Crew reached emergency cooling", "Manual injection dropped core heat", "Containment recovered", "Dirty contract success preserved the facility");
                CompleteShift(true, "Emergency cooling contained the delayed upstream fuel defect.");
            }
            else SetMessage("COOLING INJECTION ACTIVE — remain at the controls until heat drops below containment threshold.");
        }

        void CompleteShift(bool dirty, string reason)
        {
            Phase = PrototypeFacilityPhase.Complete;
            if (reactorGlow != null) reactorGlow.intensity = 1.2f;
            director?.CompletePhysicalShift(dirty, reason + " " + director.Social.Debrief);
            guidance?.SetWorldTarget("SHIFT DEBRIEF", BriefingPosition, "SHIFT COMPLETE — PRESS R TO RESTART");
        }

        void TryReanimate()
        {
            if (ocru == null) return;
            PrototypeWorkerBody patient = null;
            float nearest = 4.5f;
            foreach (var body in FindObjectsByType<PrototypeWorkerBody>())
            {
                if (body == null || body.State != PrototypeWorkerBody.BodyState.Incapacitated) continue;
                float distance = Vector3.Distance(body.transform.position, ocru.transform.position);
                if (distance < nearest) { nearest = distance; patient = body; }
            }
            if (patient == null) { SetMessage("OCRU EMPTY — drag an incapacitated worker into the medical bay."); return; }
            int power = ReservePower;
            if (!ocru.TryStart(patient, ref power)) { SetMessage("OCRU REFUSED — patient or reserve power unavailable."); return; }
            ReservePower = power;
        }

        void ArmTnt(bool overcharge)
        {
            if (tnt == null || !tnt.Arm()) { SetMessage("TNT CHARGE ALREADY ARMED."); return; }
            if (overcharge) tnt.damageRadius = 10f;
            director?.Social?.Incidents.AddPlayerPressure(overcharge ? 3 : 1);
            SetMessage(overcharge ? "TNT OVERCHARGED — CLEAR THE MINE!" : "TNT ARMED — THREE-SECOND FUSE.");
        }

        void OnTntDetonated()
        {
            foreach (var hit in Physics.OverlapSphere(tnt.transform.position, tnt.damageRadius))
            {
                var worker = hit.GetComponentInParent<PrototypeWorkerBody>();
                if (worker != null && worker.GetComponent<PrototypePlayerController>() == null) worker.Incapacitate();
            }
            Ledger("Crew detonated the mine charge", "Fuse and warning beacon counted down", "Nearby workers and ground were affected", "Drag casualties to the medical OCRU");
            SetMessage("MINE BLAST COMPLETE — check workers and rails before continuing.");
        }

        void HandleInfiltrator(bool bonk)
        {
            if (director?.Social == null) return;
            if (bonk)
            {
                bool proof = director.Social.Infiltrator.SuspicionClues >= 2 || director.Social.Infiltrator.Phase == PrototypeInfiltratorPhase.Revealed;
                director.Social.BonkInfiltrator(); infiltratorBody?.Incapacitate();
                if (!proof) director.Social.Officer.AddSuspicion(2, "worker attacked without sufficient evidence");
                SetMessage(proof ? "INFILTRATOR INCAPACITATED — disposition remains a compliance issue." : "WORKER BONKED WITHOUT PROOF — suspicion increased.");
            }
            else
            {
                director.Social.IdentifyInfiltrator();
                SetMessage(director.Social.Infiltrator.SuspicionClues >= 2 ? "TWO CLUES MATCH — infiltrator revealed." : "ONE CLUE FOUND — inspect again before acting.");
            }
        }

        void InspectLegitimateWorker()
        {
            director?.Social?.Officer.AddEvidence(new PrototypeEvidence(PrototypeEvidenceType.SuspiciousBehaviour, "legitimate route deviation verified", 0));
            Ledger("Crew inspected Mara Voss", "Her route looked unusual", "Credentials verified legitimate", "Evidence prevented a false accusation");
            SetMessage("MARA VOSS VERIFIED LEGITIMATE — suspicious behaviour was operational, not sabotage.");
        }

        void HandleOfficer(bool distract)
        {
            director?.Social?.PlayerResponse(distract ? PrototypeOfficerResponse.Distract : PrototypeOfficerResponse.Cooperate);
            SetMessage(distract ? "OFFICER DISTRACTED — temporary relief, scrutiny remains." : "ROUTINE INSPECTION COOPERATIVE — suspicion reduced.");
        }

        void HideEvidence()
        {
            director?.Social?.PlayerResponse(PrototypeOfficerResponse.HideEvidence);
            SetMessage("EVIDENCE HIDDEN — immediate exposure reduced, later discovery risk increased.");
        }

        void BonkOfficer()
        {
            director?.Social?.PlayerResponse(PrototypeOfficerResponse.Bonk);
            Ledger("Crew disabled a compliance officer", "Audit ended abruptly", "Enforcement escalation increased", "Finish the shift before backup arrives");
            SetMessage("OFFICER DISABLED — MAJOR ESCALATION RECORDED.");
        }

        void OnReactorStageChanged(ReactorCrisisStage stage)
        {
            SetMessage("REACTOR STATE: " + stage.ToString().ToUpperInvariant());
        }

        public void ResetWorld(bool teleportPlayer = true)
        {
            foreach (var cargo in runtimeCargo) if (cargo != null) DestroyRuntimeObject(cargo);
            runtimeCargo.Clear();
            if (batchToken != null) DestroyRuntimeObject(batchToken);
            batchToken = null; batchTokenRenderer = null; currentBatch = null;
            ExtractedOre = 0; EnergyDelivered = 0f; ReservePower = 100; SuitSafe = false;
            PumpStarted = false; GridConnected = false; BatchStage = "NONE";
            crusherFaultAnnounced = false; emergencyAnnounced = false; sabotageApplied = false;
            suitSequence?.ResetSequence();
            cartDriver?.ResetRoute();
            cart?.ResetCart();
            if (cart != null) { cart.transform.position = cartStart; cart.transform.rotation = Quaternion.Euler(0f, 16f, 0f); }
            crusher?.ResetMachine();
            sorter?.ResetMachine(); processor?.ResetMachine(); dryer?.ResetMachine(); assembler?.ResetMachine(); inspection?.ResetMachine();
            reactor?.ResetReactor(); demandGauge?.ResetGauge();
            if (demandGauge != null) demandGauge.demand = .35f;
            if (coolingValve != null) coolingValve.opening = 0f;
            ocru?.ResetStation(); tnt?.ResetWall();
            if (trainingWorker != null) { trainingWorker.transform.position = workerStart; trainingWorker.SetStateForTest(PrototypeWorkerBody.BodyState.Normal); }
            if (infiltratorBody != null) { infiltratorBody.transform.position = infiltratorStart; infiltratorBody.SetStateForTest(PrototypeWorkerBody.BodyState.Normal); }
            if (reactorGlow != null) reactorGlow.intensity = 0f;
            player?.SetSuitState(false);
            if (teleportPlayer && player != null)
            {
                var controller = player.GetComponent<CharacterController>();
                if (controller != null) controller.enabled = false;
                player.transform.position = PlayerSpawn;
                player.transform.rotation = Quaternion.Euler(0f, 0f, 0f);
                if (controller != null) controller.enabled = true;
            }
            Phase = PrototypeFacilityPhase.Briefing;
            guidance?.ResetGuidance();
            guidance?.SetWorldTarget("BRIEFING BOARD", BriefingPosition, "OPEN SHIFT BRIEFING");
        }

        public void ForceCartArrivalForTest() { cartDriver?.ForceArrival(); }

        void SetPhase(PrototypeFacilityPhase phase, PrototypeShiftState broadState, string message, string objective, Vector3 target)
        {
            Phase = phase;
            director?.SetRuntimeState(broadState, message);
            SetWorldObjective(objective, objective, target);
        }

        void SetWorldObjective(string objective, string label, Vector3 target)
        {
            guidance?.SetWorldTarget(label, target + Vector3.up * 2.5f, objective);
        }

        void SetMessage(string message) { director?.SetMessage(message); }
        void Ledger(string cause, string warning, string consequence, string recovery)
        { director?.Social?.Ledger.Record(cause, warning, consequence, recovery); }

        GameObject BindStation(string objectName, PrototypeStation station, string prompt, string alternate, Vector3 fallbackPosition)
        {
            var go = FindClosestNamed(objectName, fallbackPosition) ??
                CreateFallbackBlock(objectName, fallbackPosition + Vector3.up, new Vector3(2f, 2f, 2f), "fallback");
            BindExisting(go, station, prompt, alternate);
            return go;
        }

        static GameObject FindClosestNamed(string objectName, Vector3 expectedPosition)
        {
            GameObject closest = null;
            float closestDistance = float.PositiveInfinity;
            foreach (var candidate in FindObjectsByType<Transform>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (candidate == null || candidate.name != objectName) continue;
                float distance = (candidate.position - expectedPosition).sqrMagnitude;
                if (distance >= closestDistance) continue;
                closest = candidate.gameObject;
                closestDistance = distance;
            }
            return closest;
        }

        static void BindExisting(GameObject go, PrototypeStation station, string prompt, string alternate)
        {
            var target = GetOrAdd<PrototypeInteractable>(go);
            target.station = station; target.prompt = prompt; target.alternatePrompt = alternate;
        }

        static T GetOrAdd<T>(GameObject go) where T : Component
        {
            var component = go.GetComponent<T>();
            if (component == null) component = go.AddComponent<T>();
            return component;
        }

        static void DestroyRuntimeObject(UnityEngine.Object value, float delay = 0f)
        {
            if (value == null) return;
#if UNITY_EDITOR
            if (!Application.isPlaying) { DestroyImmediate(value); return; }
#endif
            Destroy(value, delay);
        }

        GameObject CreateFallbackBlock(string name, Vector3 position, Vector3 scale, string material)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name; go.transform.position = position; go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(material, new Color(.28f, .36f, .4f));
            return go;
        }

        PrototypeWorkerBody CreateWorker(string name, Vector3 position, Color color, PrototypeStation station, string prompt, string alternate)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            go.name = name; go.transform.position = position; go.transform.localScale = new Vector3(.72f, 1f, .72f);
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(name, color);
            var body = go.AddComponent<Rigidbody>(); body.mass = 70f; body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            var worker = go.AddComponent<PrototypeWorkerBody>();
            BindExisting(go, station, prompt, alternate);
            var label = new GameObject("Worker Label").AddComponent<TextMesh>();
            label.transform.SetParent(go.transform); label.transform.localPosition = new Vector3(0f, 1.5f, 0f);
            label.transform.localRotation = Quaternion.Euler(0f, 180f, 0f); label.text = name; label.characterSize = .12f; label.anchor = TextAnchor.MiddleCenter; label.color = color;
            return worker;
        }

        Material MaterialFor(string key, Color color, bool emissive = false)
        {
            Material material;
            if (materials.TryGetValue(key, out material)) return material;
            var shader = Shader.Find("Standard") ?? Shader.Find("Universal Render Pipeline/Lit");
            material = shader == null ? null : new Material(shader) { color = color };
            if (material != null && emissive) { material.EnableKeyword("_EMISSION"); material.SetColor("_EmissionColor", color * 2f); }
            materials[key] = material;
            return material;
        }

        void UpdateBatchToken(string label, Vector3 position, Color color)
        {
            if (batchToken == null)
            {
                batchToken = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                batchToken.name = "Visible Transforming Production Batch";
                batchToken.transform.localScale = new Vector3(.75f, .4f, .75f);
                DestroyRuntimeObject(batchToken.GetComponent<Collider>());
                batchTokenRenderer = batchToken.GetComponent<Renderer>();
                var text = new GameObject("Batch Label").AddComponent<TextMesh>();
                text.transform.SetParent(batchToken.transform); text.transform.localPosition = new Vector3(0f, 1.7f, 0f);
                text.transform.localRotation = Quaternion.Euler(0f, 180f, 0f); text.anchor = TextAnchor.MiddleCenter; text.characterSize = .16f;
            }
            batchToken.transform.position = position;
            batchTokenRenderer.sharedMaterial = MaterialFor("batch-" + label, color, true);
            var mesh = batchToken.GetComponentInChildren<TextMesh>(); if (mesh != null) { mesh.text = label; mesh.color = color; }
        }

        void SpawnFuelAssemblies(PrototypeBatch source)
        {
            for (int i = 0; i < PrototypeShiftRules.FuelQuota; i++)
            {
                var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                go.name = "Inspected Carryable Fuel Assembly " + (i + 1);
                go.transform.position = new Vector3(5.2f + i * 1.4f, 1.1f, -27.6f);
                go.transform.localScale = new Vector3(.45f, .9f, .45f);
                go.GetComponent<Renderer>().sharedMaterial = MaterialFor("fuel", new Color(.95f, .65f, .12f), true);
                var fuel = go.AddComponent<PrototypeFuelAssembly>();
                fuel.batch = source.Clone(); fuel.batch.mass = Mathf.Max(.45f, source.mass * .5f); fuel.inspected = true; fuel.Body.mass = 5f;
                runtimeCargo.Add(go);
            }
        }

        static PrototypeBatch AggregateCartBatch(IReadOnlyList<PrototypeOre> cargo)
        {
            float mass = 0f, grade = 0f, rock = 0f, moisture = 0f, contamination = 0f; bool wet = false;
            for (int i = 0; i < cargo.Count; i++)
            {
                var batch = cargo[i].batch; float weight = Mathf.Max(.01f, batch.mass); mass += weight;
                grade += batch.grade * weight; rock += batch.rock * weight; moisture += batch.moisture * weight; contamination += batch.contamination * weight; wet |= batch.wetShortcut;
            }
            float divisor = Mathf.Max(.01f, mass);
            return new PrototypeBatch { id = "gullet-cart-batch", mass = mass, grade = grade / divisor, rock = rock / divisor, moisture = moisture / divisor, contamination = contamination / divisor, wetShortcut = wet };
        }

        static void ReleaseHeld(GameObject item)
        {
            var carryable = item == null ? null : item.GetComponent<PrototypeCarryable>();
            var interactor = FindAnyObjectByType<PrototypePhysicsInteractor>();
            if (carryable != null && interactor != null) interactor.ReleaseIfHolding(carryable);
        }
    }

    public sealed class PrototypeFacilityCartLoadTrigger : MonoBehaviour
    {
        public PrototypeFacilityRuntime runtime;
        public PrototypeFacilityCart cart;
        void OnTriggerEnter(Collider other)
        {
            var ore = other.GetComponentInParent<PrototypeOre>();
            if (ore != null && runtime != null) runtime.TryLoadCartOre(ore);
        }
        void OnTriggerStay(Collider other) { OnTriggerEnter(other); }
    }

    [RequireComponent(typeof(Rigidbody))]
    public sealed class PrototypeFacilityCartRouteDriver : MonoBehaviour
    {
        PrototypeFacilityCart cart;
        Vector3[] route;
        int index;
        float speedMultiplier = 1f;
        public bool IsRolling { get; private set; }
        public float speed = 5.2f;
        public event Action Arrived;

        public void Configure(PrototypeFacilityCart target, Vector3[] waypoints)
        { cart = target; route = waypoints; index = 1; }

        public void BeginRoute(float multiplier = 1f)
        {
            if (route == null || route.Length < 2) return;
            if (index >= route.Length) index = 1;
            speedMultiplier = Mathf.Max(.1f, multiplier);
            if (cart != null && cart.Body != null)
            {
                cart.Body.isKinematic = true;
                cart.Body.useGravity = false;
            }
            IsRolling = true;
        }

        void FixedUpdate() { Tick(Time.fixedDeltaTime, false); }
        public void TickForTest(float seconds) { Tick(Mathf.Max(0f, seconds), true); }
        void Tick(float seconds, bool immediate)
        {
            if (!IsRolling || cart == null || cart.Body == null || route == null || index >= route.Length) return;
            Vector3 target = route[index];
            Vector3 delta = target - cart.Body.position;
            if (delta.magnitude < .65f)
            {
                index++;
                if (index >= route.Length)
                {
                    IsRolling = false;
                    cart.Body.linearVelocity = Vector3.zero;
                    cart.Body.isKinematic = false;
                    cart.Body.useGravity = true;
                    Arrived?.Invoke();
                    return;
                }
                target = route[index]; delta = target - cart.Body.position;
            }
            Vector3 step = delta.normalized * speed * speedMultiplier * seconds;
            if (step.magnitude > delta.magnitude) step = delta;
            Vector3 nextPosition = cart.Body.position + step;
            Quaternion nextRotation = delta.sqrMagnitude > .01f
                ? Quaternion.Slerp(cart.Body.rotation, Quaternion.LookRotation(delta.normalized, Vector3.up), .18f)
                : cart.Body.rotation;
            if (immediate) { cart.Body.position = nextPosition; cart.Body.rotation = nextRotation; }
            else { cart.Body.MovePosition(nextPosition); cart.Body.MoveRotation(nextRotation); }
        }

        public void ForceArrival()
        {
            if (route == null || route.Length == 0 || cart == null || cart.Body == null) return;
            cart.Body.position = route[route.Length - 1]; index = route.Length; IsRolling = false;
            cart.Body.isKinematic = false; cart.Body.useGravity = true; Arrived?.Invoke();
        }

        public void ResetRoute()
        {
            IsRolling = false; index = 1;
            if (cart != null && cart.Body != null) { cart.Body.isKinematic = false; cart.Body.useGravity = true; }
        }
    }

    public sealed class PrototypeFacilityFuelReceivingPort : MonoBehaviour
    {
        public PrototypeFacilityRuntime runtime;
        void OnTriggerEnter(Collider other)
        {
            var fuel = other.GetComponentInParent<PrototypeFuelAssembly>();
            if (fuel != null && runtime != null) runtime.TryLoadFuel(fuel);
        }
        void OnTriggerStay(Collider other) { OnTriggerEnter(other); }
    }
}
