using System.Collections.Generic;
using System.IO;
using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeFullFacilityIntegrationTests
    {
        static readonly string[] RequiredSceneObjects =
        {
            "[MACHINE] BRIEFING BOARD", "[MACHINE] SUIT INTEGRITY TEST", "[MACHINE] DRILL RIG",
            "mine.cart.parked", "[MACHINE] RECEIVING HOPPER", "[MACHINE] PRIMARY CRUSHER",
            "[MACHINE] SORTER", "[MACHINE] PROCESSOR", "[MACHINE] DRYER", "[MACHINE] FUEL ASSEMBLY",
            "[MACHINE] INSPECTION", "[MACHINE] FUEL RECEIVING", "[MACHINE] REACTOR CORE",
            "[MACHINE] COOLANT PUMP", "[MACHINE] COOLANT VALVES", "[MACHINE] EMERGENCY COOLING",
            "[MACHINE] CONTROL POSITION", "[MACHINE] GRID DEMAND", "[MACHINE] REANIMATION BAY"
        };

        [TestCase("Assets/Scenes/FacilityGreybox.unity")]
        [TestCase("Assets/Scenes/GrokShiftMap.unity")]
        public void AuthoredScenesContainEveryFullShiftRouteMarker(string scenePath)
        {
            string scene = File.ReadAllText(Path.GetFullPath(scenePath));
            foreach (string objectName in RequiredSceneObjects)
                StringAssert.Contains(objectName, scene, objectName + " must remain authored into " + scenePath + ".");
        }

        [Test]
        public void GrokMapContainsConvertedEnvironmentAndLayoutMarkers()
        {
            string scene = File.ReadAllText(Path.GetFullPath("Assets/Scenes/GrokShiftMap.unity"));
            StringAssert.Contains("[GROK] Arrival Mine Haulage Environment", scene);
            StringAssert.Contains(PrototypeFacilityLayout.PlayerSpawnMarker, scene);
            StringAssert.Contains(PrototypeFacilityLayout.CartRouteMarker, scene);
            StringAssert.Contains(PrototypeFacilityLayout.OreOutputMarker, scene);
            StringAssert.Contains(PrototypeFacilityLayout.MineTntMarker, scene);
            StringAssert.Contains(PrototypeFacilityLayout.HopperDeckMarker, scene);
        }

        [Test]
        public void SafeRouteRunsFromBriefingThroughPhysicalFuelToCleanPowerAndReset()
        {
            var originalObjects = new HashSet<GameObject>();
            foreach (var existing in Object.FindObjectsByType<GameObject>()) originalObjects.Add(existing);

            try
            {
                var directorObject = new GameObject("Full Facility Test Director");
                var director = directorObject.AddComponent<PrototypeGameDirector>();
                var playerObject = new GameObject("Full Facility Test Player");
                playerObject.AddComponent<CharacterController>();
                playerObject.AddComponent<PrototypePlayerController>();

                CreateAuthoredRouteMocks(out var correctDemand, out var distantDemand);
                var runtime = new GameObject("Full Facility Test Runtime").AddComponent<PrototypeFacilityRuntime>();
                runtime.Build();

                var correctDemandInteraction = correctDemand.GetComponent<PrototypeInteractable>();
                Assert.IsNotNull(correctDemandInteraction, "Nearest authored demand gauge should be bound.");
                Assert.AreEqual(PrototypeStation.FacilityGridDemand, correctDemandInteraction.station);
                Assert.IsNull(distantDemand.GetComponent<PrototypeInteractable>(), "Duplicate control-room label must not steal the reactor demand binding.");

                runtime.TickForTest(.3f);

                runtime.HandleInteraction(PrototypeStation.FacilityBriefing, false);
                runtime.HandleInteraction(PrototypeStation.FacilitySuit, false);
                runtime.SuitSequence.TickForTest(20f);
                Assert.AreEqual(PrototypeFacilityPhase.MineExtraction, runtime.Phase);
                Assert.IsTrue(runtime.SuitSafe);

                for (int i = 0; i < PrototypeShiftRules.OreQuota; i++)
                {
                    runtime.HandleInteraction(PrototypeStation.FacilityMineFace, false);
                    var ore = FindUnloadedOre(runtime);
                    Assert.IsTrue(runtime.TryLoadCartOre(ore));
                }
                Assert.AreEqual(PrototypeShiftRules.OreQuota, runtime.Cart.CargoCount);

                runtime.HandleInteraction(PrototypeStation.FacilityCart, false);
                Assert.AreEqual(PrototypeFacilityPhase.CartHaulage, runtime.Phase);
                for (int i = 0; i < 400 && runtime.Phase == PrototypeFacilityPhase.CartHaulage; i++)
                    runtime.TickCartForTest(.1f);
                Assert.AreEqual(PrototypeFacilityPhase.HopperUnload, runtime.Phase);
                runtime.HandleInteraction(PrototypeStation.FacilityHopper, false);
                Assert.AreEqual(PrototypeFacilityPhase.Crusher, runtime.Phase);

                Assert.AreEqual(CrusherState.Idle, runtime.Crusher.state);
                Assert.LessOrEqual(runtime.CurrentBatch.mass, runtime.Crusher.capacity);
                runtime.HandleInteraction(PrototypeStation.FacilityCrusher, false);
                Assert.AreEqual(CrusherState.AcceptingInput, runtime.Crusher.state);
                runtime.TickForTest(4f);
                Assert.AreEqual(PrototypeFacilityPhase.Sorter, runtime.Phase);

                AdvanceMachine(runtime, PrototypeStation.FacilitySorter, PrototypeFacilityPhase.Processor);
                AdvanceMachine(runtime, PrototypeStation.FacilityProcessor, PrototypeFacilityPhase.Dryer);
                AdvanceMachine(runtime, PrototypeStation.FacilityDryer, PrototypeFacilityPhase.FuelAssembly);
                AdvanceMachine(runtime, PrototypeStation.FacilityFuelAssembly, PrototypeFacilityPhase.Inspection);
                AdvanceMachine(runtime, PrototypeStation.FacilityInspection, PrototypeFacilityPhase.FuelDelivery);

                var fuelLoads = Object.FindObjectsByType<PrototypeFuelAssembly>();
                Assert.AreEqual(PrototypeShiftRules.FuelQuota, fuelLoads.Length);
                foreach (var fuel in fuelLoads) Assert.IsTrue(runtime.TryLoadFuel(fuel));
                Assert.AreEqual(PrototypeFacilityPhase.CoolingStartup, runtime.Phase);

                runtime.HandleInteraction(PrototypeStation.FacilityReactorPump, false);
                runtime.HandleInteraction(PrototypeStation.FacilityReactorControl, false);
                runtime.HandleInteraction(PrototypeStation.FacilityGridDemand, false);
                Assert.AreEqual(PrototypeFacilityPhase.PowerGeneration, runtime.Phase);

                for (int i = 0; i < 160 && runtime.Phase != PrototypeFacilityPhase.Complete; i++)
                    runtime.TickForTest(.25f);

                Assert.AreEqual(PrototypeFacilityPhase.Complete, runtime.Phase);
                Assert.AreEqual(PrototypeShiftState.Won, director.State);
                Assert.GreaterOrEqual(runtime.EnergyDelivered, PrototypeFacilityRuntime.EnergyTarget);

                director.ResetShift();
                Assert.AreEqual(PrototypeFacilityPhase.Briefing, runtime.Phase);
                Assert.AreEqual(0, runtime.Cart.CargoCount);
                Assert.AreEqual(0, runtime.LoadedFuel);
                Assert.AreEqual("NONE", runtime.BatchStage);
            }
            finally
            {
                foreach (var created in Object.FindObjectsByType<GameObject>())
                    if (created != null && !originalObjects.Contains(created)) Object.DestroyImmediate(created);
            }
        }

        static void AdvanceMachine(PrototypeFacilityRuntime runtime, PrototypeStation station, PrototypeFacilityPhase expected)
        {
            Assert.IsTrue(runtime.HandleInteraction(station, false));
            runtime.TickForTest(4f);
            Assert.AreEqual(expected, runtime.Phase);
        }

        static PrototypeOre FindUnloadedOre(PrototypeFacilityRuntime runtime)
        {
            foreach (var ore in Object.FindObjectsByType<PrototypeOre>())
            {
                bool loaded = false;
                foreach (var cargo in runtime.Cart.Cargo) if (cargo == ore) { loaded = true; break; }
                if (!loaded) return ore;
            }
            return null;
        }

        static void CreateAuthoredRouteMocks(out GameObject correctDemand, out GameObject distantDemand)
        {
            foreach (string objectName in RequiredSceneObjects)
            {
                if (objectName == "[MACHINE] GRID DEMAND" || objectName == "mine.cart.parked") continue;
                new GameObject(objectName);
            }

            var cart = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cart.name = "mine.cart.parked";
            cart.transform.position = new Vector3(-81.6f, -1.2f, -.6f);

            correctDemand = new GameObject("[MACHINE] GRID DEMAND");
            correctDemand.transform.position = new Vector3(7.2f, 0f, -4.5f);
            distantDemand = new GameObject("[MACHINE] GRID DEMAND");
            distantDemand.transform.position = new Vector3(28.8f, 10f, 4.8f);
        }
    }
}
