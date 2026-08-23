using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    /// <summary>
    /// Integrates the proof-of-fun systems into one compact, physical training annex.
    /// This is deliberately host-local: future clients will submit intentions to a host
    /// that owns these same state transitions and rigidbodies.
    /// </summary>
    public sealed class PrototypeShoeboxRuntime : MonoBehaviour
    {
        public static PrototypeShoeboxRuntime Instance { get; private set; }

        public int ReservePower { get; private set; } = 100;
        public int FuelAssembliesProduced { get; private set; }
        public float EnergyDelivered { get; private set; }
        public bool ReactorStarted { get; private set; }

        GameObject annexRoot;
        PrototypeConveyor conveyor;
        PrototypeCrusher crusher;
        PrototypeReactorMachine reactor;
        PrototypeCoolingValve coolingValve;
        PrototypeDemandGauge demandGauge;
        PrototypeReanimationStation ocru;
        PrototypeSuitLocker suitLocker;
        PrototypeTntWall tntWall;
        PrototypeAlarmBeacon alarm;
        PrototypeWorkerBody trainingWorker;
        PrototypeWorkerBody infiltratorBody;
        PrototypeMineCart mineCart;
        PrototypePlayerController player;
        Vector3 trainingWorkerStart;
        Vector3 infiltratorStart;
        Vector3 cartStart;
        bool built;
        bool sabotageTriggered;
        bool emergencyAnnounced;
        float incidentTimer;
        readonly List<GameObject> runtimeCargo = new List<GameObject>();
        readonly Dictionary<string, Material> materials = new Dictionary<string, Material>();

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        public void Build(Vector3 origin)
        {
            if (built) return;
            built = true;
            player = FindAnyObjectByType<PrototypePlayerController>();
            annexRoot = new GameObject("[PROTOTYPE] Radioactive Shoebox Annex");
            annexRoot.transform.SetParent(transform);
            annexRoot.transform.position = origin;

            CreateBlock("Annex Floor", new Vector3(0f, -.18f, 0f), new Vector3(28f, .35f, 18f), "floor");
            CreateBlock("North Guard", new Vector3(0f, 1.25f, 8.7f), new Vector3(28f, 2.5f, .25f), "wall");
            CreateBlock("South Guard", new Vector3(0f, 1.25f, -8.7f), new Vector3(28f, 2.5f, .25f), "wall");
            CreateBlock("East Guard", new Vector3(13.8f, 1.25f, 0f), new Vector3(.25f, 2.5f, 18f), "wall");
            CreateLabel("RADIOACTIVE SHOEBOX // PHYSICAL TRAINING ANNEX", new Vector3(0f, 2.8f, 8.45f), 0.32f, Color.white);

            CreateStation("Shift Briefing", PrototypeStation.Briefing, new Vector3(-11.5f, .75f, -6.8f),
                "open the shift briefing", null, "briefing");
            CreateStation("Suit Locker", PrototypeStation.SuitLocker, new Vector3(-8.8f, .75f, -6.8f),
                "toggle protective suit (safe / slower)", null, "safety");
            CreateStation("TNT Test Wall", PrototypeStation.TntWall, new Vector3(-6.1f, .75f, -6.8f),
                "arm the TNT test wall", null, "hazard");

            BuildProductionRow();
            BuildRecoveryArea();
            BuildSocialArea();
            ResetWorld();
            Debug.Log("[PrototypeShoebox] Built physical annex: conveyor, crusher, reactor, cooling, alarm, cart, TNT, OCRU, suit, infiltrator and compliance stations.");
        }

        void BuildProductionRow()
        {
            CreateStation("Ore Pile", PrototypeStation.OrePile, new Vector3(-11f, .65f, 3.7f),
                "release one dry ore rock", "release wet ore (fast / jam risk)", "ore");

            var conveyorObject = CreateBlock("Physical Ore Conveyor", new Vector3(-5.7f, .45f, 3.7f), new Vector3(7.2f, .45f, 2f), "conveyor");
            conveyorObject.transform.localRotation = Quaternion.Euler(0f, 90f, 0f);
            var conveyorCollider = conveyorObject.GetComponent<BoxCollider>();
            conveyorCollider.isTrigger = true;
            conveyor = conveyorObject.AddComponent<PrototypeConveyor>();
            conveyor.speed = 1.55f;
            var output = new GameObject("Conveyor Output").transform;
            output.SetParent(annexRoot.transform);
            output.localPosition = new Vector3(-2.2f, .8f, 3.7f);
            conveyor.output = output;
            conveyor.OreDelivered += OnOreDelivered;
            CreateLabel("DROP ORE ON BELT", new Vector3(-5.7f, 1.35f, 3.7f), .2f, new Color(.7f, 1f, 1f));

            var crusherObject = CreateStation("Crusher", PrototypeStation.Crusher, new Vector3(.2f, .9f, 3.7f),
                "repair or inspect crusher", "toggle safety bypass", "crusher");
            crusher = crusherObject.AddComponent<PrototypeCrusher>();
            crusher.BeginOperation();
            crusher.AudioStateChanged += state => SetMessage("CRUSHER AUDIO: " + state);
            crusherObject.AddComponent<PrototypeMachineAudio>().Bind(crusher);

            var port = CreateBlock("Reactor Fuel Port", new Vector3(6.2f, .55f, 3.7f), new Vector3(2.2f, 1.1f, 2.2f), "fuel");
            port.GetComponent<BoxCollider>().isTrigger = true;
            port.AddComponent<PrototypeFuelPort>();
            CreateLabel("DROP 2 FUEL HERE", new Vector3(6.2f, 1.45f, 3.7f), .2f, new Color(1f, .86f, .35f));

            var reactorObject = CreateStation("Reactor Control", PrototypeStation.Reactor, new Vector3(9.5f, 1f, 3.7f),
                "start reactor after two fuel loads", null, "reactor");
            reactor = reactorObject.AddComponent<PrototypeReactorMachine>();
            reactor.AudioStateChanged += state => SetMessage("REACTOR AUDIO: " + state);
            reactor.StageChanged += OnReactorStageChanged;
            reactorObject.AddComponent<PrototypeMachineAudio>().Bind(reactor);

            var valveObject = CreateStation("Emergency Cooling Valve", PrototypeStation.CoolingValve, new Vector3(11.7f, .75f, .4f),
                "open emergency cooling", null, "cooling");
            coolingValve = valveObject.AddComponent<PrototypeCoolingValve>();
            coolingValve.opening = 1f;

            var gaugeObject = CreateBlock("Demand Gauge", new Vector3(9.1f, 1.35f, .4f), new Vector3(2.7f, 2.7f, .5f), "gauge");
            demandGauge = gaugeObject.AddComponent<PrototypeDemandGauge>();
            CreateLabel("DEMAND / HEAT", new Vector3(9.1f, 2.9f, .1f), .2f, Color.white);
            var alarmObject = CreateBlock("Reactor Alarm Beacon", new Vector3(12f, 2.35f, 3.7f), new Vector3(.55f, .55f, .55f), "danger");
            alarm = alarmObject.AddComponent<PrototypeAlarmBeacon>();
        }

        void BuildRecoveryArea()
        {
            var cartObject = CreateBlock("Pushable Mine Cart", new Vector3(-7.5f, .65f, -1.2f), new Vector3(2.4f, 1.3f, 1.7f), "cart");
            var cartBody = cartObject.AddComponent<Rigidbody>();
            cartBody.mass = 85f;
            cartBody.linearDamping = 1.5f;
            mineCart = cartObject.AddComponent<PrototypeMineCart>();
            var cartInteraction = cartObject.AddComponent<PrototypeInteractable>();
            cartInteraction.station = PrototypeStation.MineCart;
            cartInteraction.prompt = "shove cart toward the training worker";
            cartStart = cartObject.transform.position;

            var workerObject = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            workerObject.name = "Training Worker Body";
            workerObject.transform.SetParent(annexRoot.transform);
            workerObject.transform.localPosition = new Vector3(-2.4f, 1f, -1.2f);
            workerObject.transform.localScale = new Vector3(.75f, 1f, .75f);
            workerObject.GetComponent<Renderer>().sharedMaterial = MaterialFor("worker", new Color(.78f, .66f, .28f));
            var workerBody = workerObject.AddComponent<Rigidbody>();
            workerBody.mass = 70f;
            workerBody.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            trainingWorker = workerObject.AddComponent<PrototypeWorkerBody>();
            trainingWorkerStart = workerObject.transform.position;
            CreateWorldLabel(workerObject.transform, "TRAINING WORKER", new Color(1f, .9f, .45f));

            var ocruObject = CreateStation("OCRU Reanimation Cabinet", PrototypeStation.Reanimation, new Vector3(9.5f, 1.1f, -2f),
                "reanimate a nearby incapacitated worker (25 power)", null, "ocru");
            ocru = ocruObject.AddComponent<PrototypeReanimationStation>();
            ocru.ReanimationStarted += (body, cost) =>
            {
                SetMessage("OCRU DRAWING " + cost + " RESERVE POWER — patient vulnerable.");
                Ledger("Worker incapacitated", "OCRU requested reserve power", "Emergency reserve reduced", "Reanimation cycle started");
            };
            ocru.ReanimationCompleted += body =>
            {
                SetMessage("WORKER RETURNED TO SERVICE — temporary recovery in progress.");
                Ledger("Crew completed physical recovery", "OCRU cycle reached 100%", "Worker recommissioned", "Reserve power preserved cooling margin");
            };

            var tntObject = GameObject.Find("TNT Test Wall");
            tntWall = tntObject.AddComponent<PrototypeTntWall>();
            tntWall.damageRadius = 8f;
            tntWall.DetonationWarning += remaining => { if (remaining < 1.1f) SetMessage("TNT DETONATION IMMINENT — clear the marked wall!"); };
            tntWall.Detonated += OnTntDetonated;

            var suitObject = GameObject.Find("Suit Locker");
            suitLocker = suitObject.AddComponent<PrototypeSuitLocker>();
        }

        void BuildSocialArea()
        {
            infiltratorBody = CreateWorker("Contract Worker 7", new Vector3(-1f, 1f, -5.2f), new Color(.28f, .62f, .55f), PrototypeStation.Infiltrator,
                "inspect worker credentials", "nonlethal bonk");
            infiltratorStart = infiltratorBody.transform.position;
            CreateWorker("Mara Voss // legitimate", new Vector3(2.2f, 1f, -5.2f), new Color(.65f, .58f, .24f), PrototypeStation.LegitimateWorker,
                "inspect suspicious legitimate worker", null);
            CreateStation("Compliance Officer", PrototypeStation.ComplianceOfficer, new Vector3(5.4f, 1f, -5.2f),
                "cooperate with routine inspection", "distract the officer", "compliance");
            CreateStation("Evidence Locker", PrototypeStation.EvidenceLocker, new Vector3(8.3f, .75f, -5.2f),
                "hide recorded evidence", null, "evidence");
            CreateStation("Compliance Bonk Control", PrototypeStation.OfficerBonk, new Vector3(11.2f, .75f, -5.2f),
                "nonlethally disable the officer (major escalation)", null, "danger");
        }

        PrototypeWorkerBody CreateWorker(string name, Vector3 localPosition, Color color, PrototypeStation station, string prompt, string alternate)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            go.name = name;
            go.transform.SetParent(annexRoot.transform);
            go.transform.localPosition = localPosition;
            go.transform.localScale = new Vector3(.72f, 1f, .72f);
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(name, color);
            var body = go.AddComponent<Rigidbody>();
            body.mass = 70f;
            body.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            var worker = go.AddComponent<PrototypeWorkerBody>();
            var interactable = go.AddComponent<PrototypeInteractable>();
            interactable.station = station;
            interactable.prompt = prompt;
            interactable.alternatePrompt = alternate;
            CreateWorldLabel(go.transform, name, color);
            return worker;
        }

        public void SpawnOre(bool wetShortcut)
        {
            var director = PrototypeGameDirector.Instance;
            if (director == null || director.State != PrototypeShiftState.Mining)
            {
                SetMessage("ORE RELEASE LOCKED — read briefing or finish the active production stage.");
                return;
            }
            int liveOre = 0;
            foreach (var cargo in runtimeCargo) if (cargo != null && cargo.GetComponent<PrototypeOre>() != null) liveOre++;
            if (liveOre >= 4) { SetMessage("ORE PILE INTERLOCK — clear existing rocks before releasing more."); return; }

            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = wetShortcut ? "Wet Ore Batch" : "Dry Ore Batch";
            go.transform.position = annexRoot.transform.TransformPoint(new Vector3(-10.2f, 1.3f, 3.7f));
            go.transform.localScale = new Vector3(.85f, .65f, .75f);
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(wetShortcut ? "wetOre" : "ore", wetShortcut ? new Color(.2f, .42f, .38f) : new Color(.38f, .33f, .28f));
            var body = go.AddComponent<Rigidbody>();
            body.mass = 4f;
            var ore = go.AddComponent<PrototypeOre>();
            go.AddComponent<PrototypeCarryable>();
            ore.batch = new PrototypeBatch
            {
                mass = 1f,
                grade = wetShortcut ? .82f : .7f,
                rock = .24f,
                moisture = wetShortcut ? .65f : .08f,
                wetShortcut = wetShortcut
            };
            runtimeCargo.Add(go);
            if (wetShortcut)
            {
                PrototypeGameDirector.Instance.Social.Incidents.AddPlayerPressure(2);
                Ledger("Crew released wet ore for a faster yield", "Ore surface visibly glistened", "Crusher jam or hidden fuel defect is now possible", "Dry it or knowingly bypass the crusher interlock");
            }
            SetMessage(wetShortcut ? "WET ORE RELEASED — faster grade, visible jam warning." : "DRY ORE RELEASED — grab it and place it on the moving belt.");
        }

        void OnOreDelivered(PrototypeOre ore)
        {
            if (ore == null) return;
            if (!crusher.Accept(ore.batch))
            {
                SetMessage("CRUSHER BUSY — delivered ore dropped at the output. Reload it when the crusher is idle.");
                return;
            }
            runtimeCargo.Remove(ore.gameObject);
            Destroy(ore.gameObject);
            SetMessage("ORE ENTERED CRUSHER — listen for output or a wet-jam failure.");
        }

        void Update()
        {
            if (!built) return;
            var director = PrototypeGameDirector.Instance;
            if (director == null) return;

            if (crusher != null && crusher.state == CrusherState.OutputReady && crusher.output != null)
            {
                var batch = crusher.TakeOutput();
                FuelAssembliesProduced++;
                director.MineOre();
                SpawnFuel(batch.AssembleFuel());
                SetMessage("FUEL ASSEMBLY READY — physically carry it to the yellow reactor port.");
            }

            if (!sabotageTriggered && director.Social != null && director.Social.Infiltrator.Phase == PrototypeInfiltratorPhase.Sabotaging)
            {
                sabotageTriggered = true;
                director.Social.SabotageInfiltrator();
                crusher.damage = Mathf.Clamp01(crusher.damage + .25f);
                SetMessage("POWER SPIKE — one worker was near the crusher. Inspect both suspicious employees before blaming anyone.");
            }

            incidentTimer += Time.deltaTime;
            if (incidentTimer >= 15f && director.Social != null)
            {
                incidentTimer = 0f;
                var severity = director.Social.Incidents.Evaluate(director.Ore > 0, director.State == PrototypeShiftState.CoolingEmergency);
                if (severity == PrototypeIncidentSeverity.Medium)
                {
                    demandGauge.demand = Mathf.Clamp01(demandGauge.demand + .12f);
                    SetMessage("INCIDENT: contract demand spiked after suspicious production telemetry.");
                    Ledger("Player pressure attracted contract scrutiny", "Demand gauge stepped upward", "Reactor margin narrowed", "Use clean fuel and preserve cooling");
                }
                else if (severity == PrototypeIncidentSeverity.Major)
                {
                    demandGauge.demand = Mathf.Clamp01(demandGauge.demand + .2f);
                    director.Social.Officer.AddSuspicion(1, "production anomaly during inspection");
                    SetMessage("MAJOR INCIDENT: demand spike and compliance inquiry arrived together.");
                    Ledger("Accumulated shortcuts triggered a major incident", "Demand and officer suspicion rose together", "Production, safety and concealment are all under pressure", "Cooperate, recover machinery and avoid another shortcut");
                }
            }

            if (!ReactorStarted || reactor == null) return;
            director.SetPhysicalHeat(reactor.heat);
            EnergyDelivered += reactor.output * Time.deltaTime;

            if (reactor.stage >= ReactorCrisisStage.CoolingEmergency && reactor.stage < ReactorCrisisStage.Contained && !emergencyAnnounced)
            {
                emergencyAnnounced = true;
                director.BeginPhysicalEmergency("DELAYED CONSEQUENCE — unsafe fuel is overheating. Open EMERGENCY COOLING before core damage.");
                Ledger("Unsafe ore or crusher bypass created defective fuel", "Heat and stability gauges crossed warning bands", "Cooling emergency entered", "Open the physical coolant valve");
            }
            if (reactor.stage == ReactorCrisisStage.CriticalMeltdown)
            {
                director.Fail("CRITICAL MELTDOWN — warnings were ignored. " + director.Social.Debrief);
                return;
            }
            if (!reactor.UnsafeFuelLoaded && director.State == PrototypeShiftState.Reactor && EnergyDelivered >= 6f)
                director.CompletePhysicalShift(false, "quota met with inspected fuel. " + director.Social.Debrief);
        }

        void SpawnFuel(PrototypeBatch batch)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "Carryable Fuel Assembly " + FuelAssembliesProduced;
            go.transform.position = annexRoot.transform.TransformPoint(new Vector3(2.7f, 1.25f, 3.7f));
            go.transform.localScale = new Vector3(.45f, .8f, .45f);
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor("fuelAssembly", new Color(.82f, .65f, .18f));
            var fuel = go.AddComponent<PrototypeFuelAssembly>();
            fuel.batch = batch;
            runtimeCargo.Add(go);
        }

        public bool TryLoadFuel(PrototypeFuelAssembly fuel)
        {
            var director = PrototypeGameDirector.Instance;
            if (fuel == null || director == null || director.State != PrototypeShiftState.Refining)
            {
                SetMessage("FUEL PORT LOCKED — process three ore batches before loading fuel.");
                return false;
            }
            bool unsafeFuel = fuel.Quality < .45f || (fuel.batch != null && fuel.batch.hiddenDefect > 0f);
            if (!reactor.LoadFuel(fuel) || !director.RecordPhysicalFuel(unsafeFuel)) return false;
            runtimeCargo.Remove(fuel.gameObject);
            Destroy(fuel.gameObject);
            SetMessage("FUEL PHYSICALLY LOADED (" + reactor.LoadedBatches + "/" + PrototypeShiftRules.FuelQuota + ").");
            return true;
        }

        public bool TryStartReactor()
        {
            if (reactor == null || !reactor.StartReactor()) return false;
            ReactorStarted = true;
            EnergyDelivered = 0f;
            return true;
        }

        public void UseCrusher(bool unsafeBypass)
        {
            if (crusher == null) return;
            if (unsafeBypass)
            {
                crusher.SetUnsafeBypass(!crusher.safetyBypass);
                PrototypeGameDirector.Instance.Social.Incidents.AddPlayerPressure(2);
                Ledger("Crew changed the crusher safety bypass", "Amber bypass lamp illuminated", crusher.safetyBypass ? "Wet ore can pass with a hidden defect" : "Safety interlock restored", "Inspect fuel or prepare emergency cooling");
                SetMessage(crusher.safetyBypass ? "CRUSHER BYPASS ON — fast, legal safeguards disabled." : "CRUSHER BYPASS OFF — wet ore will jam visibly.");
                return;
            }
            if (crusher.state == CrusherState.Faulted)
            {
                crusher.Repair();
                crusher.FinishRepair();
                SetMessage("CRUSHER JAM CLEARED — failed batch was discarded; reload ore.");
                Ledger("Wet ore jammed the crusher", "Motor entered failure audio state", "Production stopped", "Crew cleared the jam and restored the interlock");
            }
            else SetMessage("CRUSHER STATUS: " + crusher.state + " // DAMAGE " + Mathf.RoundToInt(crusher.damage * 100f) + "%.");
        }

        public void UseEmergencyCooling()
        {
            coolingValve.SetOpening(1f);
            if (!reactor.EmergencyCooling())
            {
                SetMessage("COOLING VALVE OPEN — no active emergency; reserve remains available.");
                return;
            }
            if (reactor.stage == ReactorCrisisStage.Contained)
            {
                Ledger("Crew opened emergency cooling", "Coolant flow recovered", "Core returned below emergency heat", "Dirty quota accepted with damage report");
                PrototypeGameDirector.Instance.ResolveCoolingEmergency();
            }
        }

        public void ToggleSuit()
        {
            bool suitOn = suitLocker.ToggleSuit();
            player?.SetSuitState(suitOn);
            if (!suitOn)
            {
                PrototypeGameDirector.Instance.Social.Officer.AddEvidence(new PrototypeEvidence(PrototypeEvidenceType.IllegalModification, "suit telemetry", 2));
                PrototypeGameDirector.Instance.Social.Incidents.AddPlayerPressure(1);
                Ledger("Worker skipped protective suit", "Suit telemetry went offline", "Movement improved but compliance and contamination risk rose", "Return to locker before hazardous work");
            }
            SetMessage(suitOn ? "PROTECTIVE SUIT SEALED — safe, normal movement." : "SUIT SKIPPED — 15% faster, telemetry violation recorded.");
        }

        public void ArmTnt()
        {
            if (tntWall.Arm())
            {
                PrototypeGameDirector.Instance.Social.Incidents.AddPlayerPressure(2);
                Ledger("Crew armed excess TNT", "Three-second fuse sounded", "Nearby workers may be incapacitated", "Clear the wall or recover casualties through OCRU");
                SetMessage("TNT ARMED — THREE-SECOND FUSE. This is a recoverable training casualty.");
            }
        }

        void OnTntDetonated()
        {
            if (trainingWorker != null && Vector3.Distance(trainingWorker.transform.position, tntWall.transform.position) <= tntWall.damageRadius)
                trainingWorker.Incapacitate();
            SetMessage("TNT DETONATED — training worker biologically offline. Drag them to OCRU with [G/right mouse].");
        }

        public void TryReanimate()
        {
            PrototypeWorkerBody patient = NearestIncapacitatedWorker();
            if (patient == null)
            {
                SetMessage("OCRU EMPTY — drag an incapacitated worker within the marked cabinet radius.");
                return;
            }
            int power = ReservePower;
            if (!ocru.TryStart(patient, ref power))
            {
                SetMessage("OCRU REFUSED — insufficient reserve power or patient not ready.");
                return;
            }
            ReservePower = power;
        }

        PrototypeWorkerBody NearestIncapacitatedWorker()
        {
            PrototypeWorkerBody best = null;
            float bestDistance = 3.5f;
            foreach (var candidate in new[] { trainingWorker, infiltratorBody })
            {
                if (candidate == null || candidate.State != PrototypeWorkerBody.BodyState.Incapacitated) continue;
                float distance = Vector3.Distance(candidate.transform.position, ocru.transform.position);
                if (distance < bestDistance) { best = candidate; bestDistance = distance; }
            }
            return best;
        }

        public void HandleInfiltrator(bool bonk)
        {
            var social = PrototypeGameDirector.Instance.Social;
            if (bonk)
            {
                bool hadProof = social.Infiltrator.SuspicionClues >= 2 || social.Infiltrator.Phase == PrototypeInfiltratorPhase.Revealed;
                social.BonkInfiltrator();
                infiltratorBody.Incapacitate();
                if (!hadProof) social.Officer.AddSuspicion(2, "crew assaulted a credentialed worker before confirming identity");
                SetMessage(hadProof ? "INFILTRATOR INCAPACITATED — drag or reanimate for disposition." : "WORKER BONKED WITHOUT PROOF — compliance suspicion increased.");
            }
            else
            {
                social.IdentifyInfiltrator();
                SetMessage(social.Infiltrator.SuspicionClues >= 2
                    ? "IDENTITY MISMATCH CONFIRMED — Contract Worker 7 is revealed."
                    : "CLUE: badge telemetry timestamp is inconsistent. Compare another inspection before acting.");
            }
        }

        public void InspectLegitimateWorker()
        {
            SetMessage("MARA VOSS: suspicious route, valid badge and medical telemetry. Legitimate employee — do not attack every odd worker.");
            Ledger("Crew inspected a suspicious legitimate worker", "Her route looked unusual", "Credentials verified clean", "Paranoia reduced through evidence");
        }

        public void HandleOfficer(bool distract)
        {
            var response = distract ? PrototypeOfficerResponse.Distract : PrototypeOfficerResponse.Cooperate;
            PrototypeGameDirector.Instance.Social.PlayerResponse(response);
            SetMessage(distract ? "OFFICER DISTRACTED — temporary relief, scrutiny remains." : "ROUTINE INSPECTION COOPERATIVE — suspicion reduced.");
        }

        public void HideEvidence()
        {
            PrototypeGameDirector.Instance.Social.PlayerResponse(PrototypeOfficerResponse.HideEvidence);
            SetMessage("EVIDENCE HIDDEN — immediate discovery reduced, obstruction escalation recorded.");
        }

        public void BonkOfficer()
        {
            PrototypeGameDirector.Instance.Social.PlayerResponse(PrototypeOfficerResponse.Bonk);
            PrototypeGameDirector.Instance.Social.Officer.AddEvidence(new PrototypeEvidence(PrototypeEvidenceType.DisabledOfficer, "annex floor", 3));
            SetMessage("COMPLIANCE OFFICER DISABLED — facility escalation increased. This was not consequence-free.");
        }

        public void PushCart()
        {
            var body = mineCart.GetComponent<Rigidbody>();
            var target = trainingWorker != null ? trainingWorker.transform.position : mineCart.transform.position + Vector3.right;
            var direction = (target - mineCart.transform.position).normalized;
            direction.y = 0f;
            body.AddForce(direction * 8f, ForceMode.VelocityChange);
            SetMessage("CART SHOVED — clear the red lane or recover the knocked-down worker.");
        }

        void OnReactorStageChanged(ReactorCrisisStage stage)
        {
            alarm?.SetActive(stage >= ReactorCrisisStage.CoolingEmergency && stage != ReactorCrisisStage.Contained);
            SetMessage("REACTOR STATE: " + stage + " // HEAT " + Mathf.RoundToInt(reactor.heat * 100f) + "%.");
        }

        public void ResetWorld()
        {
            if (!built) return;
            var interactor = player != null ? player.GetComponent<PrototypePhysicsInteractor>() : null;
            interactor?.Release(false);
            foreach (var cargo in runtimeCargo) if (cargo != null) DestroyRuntimeObject(cargo);
            runtimeCargo.Clear();
            conveyor?.ResetConveyor();
            crusher?.ResetMachine();
            reactor?.ResetReactor();
            demandGauge?.ResetGauge();
            if (coolingValve != null) coolingValve.SetOpening(1f);
            ocru?.ResetStation();
            tntWall?.ResetWall();
            alarm?.SetActive(false);
            suitLocker?.SetSuit(true);
            player?.SetSuitState(true);
            player?.GetComponent<PrototypeWorkerBody>()?.SetStateForTest(PrototypeWorkerBody.BodyState.Normal);
            RestoreWorker(trainingWorker, trainingWorkerStart);
            RestoreWorker(infiltratorBody, infiltratorStart);
            if (mineCart != null)
            {
                var body = mineCart.GetComponent<Rigidbody>();
                body.position = cartStart;
                body.rotation = Quaternion.identity;
                body.linearVelocity = Vector3.zero;
                body.angularVelocity = Vector3.zero;
            }
            ReservePower = 100;
            FuelAssembliesProduced = 0;
            EnergyDelivered = 0f;
            ReactorStarted = false;
            sabotageTriggered = false;
            emergencyAnnounced = false;
            incidentTimer = 0f;
        }

        static void RestoreWorker(PrototypeWorkerBody worker, Vector3 position)
        {
            if (worker == null) return;
            worker.SetStateForTest(PrototypeWorkerBody.BodyState.Normal);
            worker.transform.position = position;
            worker.transform.rotation = Quaternion.identity;
            if (worker.PhysicsBody != null)
            {
                worker.PhysicsBody.isKinematic = false;
                worker.PhysicsBody.linearVelocity = Vector3.zero;
                worker.PhysicsBody.angularVelocity = Vector3.zero;
            }
        }

        GameObject CreateStation(string name, PrototypeStation station, Vector3 localPosition, string prompt, string alternate, string materialKey)
        {
            var color = StationColor(materialKey);
            var go = CreateBlock(name, localPosition, new Vector3(1.65f, 1.5f, 1.2f), materialKey, color);
            var interactable = go.AddComponent<PrototypeInteractable>();
            interactable.station = station;
            interactable.prompt = prompt;
            interactable.alternatePrompt = alternate;
            CreateWorldLabel(go.transform, name.ToUpperInvariant(), color);
            return go;
        }

        GameObject CreateBlock(string name, Vector3 localPosition, Vector3 scale, string materialKey, Color? overrideColor = null)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(annexRoot.transform);
            go.transform.localPosition = localPosition;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = MaterialFor(materialKey, overrideColor ?? StationColor(materialKey));
            return go;
        }

        void CreateWorldLabel(Transform parent, string text, Color color)
        {
            var label = new GameObject(text + " Label");
            label.transform.SetParent(parent);
            label.transform.localPosition = new Vector3(0f, .95f, -.66f);
            label.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            var mesh = label.AddComponent<TextMesh>();
            mesh.text = text;
            mesh.fontSize = 48;
            mesh.characterSize = .045f;
            mesh.anchor = TextAnchor.MiddleCenter;
            mesh.alignment = TextAlignment.Center;
            mesh.color = Color.white;
        }

        void CreateLabel(string text, Vector3 localPosition, float size, Color color)
        {
            var label = new GameObject(text);
            label.transform.SetParent(annexRoot.transform);
            label.transform.localPosition = localPosition;
            label.transform.localRotation = Quaternion.Euler(0f, 180f, 0f);
            var mesh = label.AddComponent<TextMesh>();
            mesh.text = text;
            mesh.fontSize = 48;
            mesh.characterSize = size / 4f;
            mesh.anchor = TextAnchor.MiddleCenter;
            mesh.color = color;
        }

        Material MaterialFor(string key, Color color)
        {
            if (materials.TryGetValue(key, out var existing)) return existing;
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var material = new Material(shader) { color = color };
            materials[key] = material;
            return material;
        }

        static Color StationColor(string key)
        {
            switch (key)
            {
                case "briefing": return new Color(.82f, .68f, .22f);
                case "safety": return new Color(.2f, .55f, .65f);
                case "hazard": case "danger": return new Color(.7f, .2f, .15f);
                case "ore": return new Color(.35f, .32f, .28f);
                case "conveyor": return new Color(.22f, .3f, .32f);
                case "crusher": return new Color(.55f, .35f, .16f);
                case "fuel": return new Color(.72f, .58f, .17f);
                case "reactor": return new Color(.18f, .48f, .58f);
                case "cooling": return new Color(.12f, .58f, .68f);
                case "ocru": return new Color(.65f, .7f, .66f);
                case "compliance": return new Color(.46f, .35f, .55f);
                case "evidence": return new Color(.34f, .27f, .35f);
                case "cart": return new Color(.45f, .28f, .13f);
                case "floor": return new Color(.12f, .15f, .17f);
                case "wall": return new Color(.2f, .24f, .25f);
                case "gauge": return new Color(.14f, .2f, .23f);
                default: return new Color(.35f, .4f, .4f);
            }
        }

        void Ledger(string cause, string warning, string consequence, string recovery)
        {
            PrototypeGameDirector.Instance?.Social?.Ledger.Record(cause, warning, consequence, recovery);
        }

        void SetMessage(string message) { PrototypeGameDirector.Instance?.SetMessage(message); }

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
            foreach (var material in materials.Values) if (material != null) DestroyRuntimeObject(material);
        }

        static void DestroyRuntimeObject(Object target)
        {
            if (target == null) return;
            if (Application.isPlaying) Destroy(target); else DestroyImmediate(target);
        }
    }

    public sealed class PrototypeFuelPort : MonoBehaviour
    {
        void OnTriggerEnter(Collider other)
        {
            var fuel = other.GetComponentInParent<PrototypeFuelAssembly>();
            if (fuel != null) PrototypeShoeboxRuntime.Instance?.TryLoadFuel(fuel);
        }
    }
}
