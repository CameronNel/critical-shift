using NUnit.Framework;
using UnityEngine;
using CriticalShift.Prototype;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeProductionChainTests
    {
        [Test] public void BatchTransformPreservesTraceAndCalculatesFuelQuality()
        {
            var raw = new PrototypeBatch { id = "wet-7", mass = 10f, grade = .8f, rock = .4f, moisture = .5f, contamination = .1f, wetShortcut = true };
            var dry = raw.Dry(); var fuel = dry.Crush(false).AssembleFuel();
            Assert.AreEqual("wet-7", fuel.id); Assert.AreEqual(OreForm.Crushed, fuel.form); Assert.Less(dry.mass, raw.mass); Assert.Greater(fuel.fuelQuality, .4f);
        }

        [Test] public void WetBatchJamsCrusherUnlessUnsafeBypassIsEnabled()
        {
            var go = new GameObject("crusher-test"); var crusher = go.AddComponent<PrototypeCrusher>();
            crusher.BeginOperation(); crusher.Tick(.3f); crusher.Accept(new PrototypeBatch { wetShortcut = true }); crusher.Tick(.1f); crusher.Tick(2f);
            Assert.AreEqual(CrusherState.Faulted, crusher.state); Assert.IsTrue(crusher.WetJam);
            crusher.Repair(); crusher.FinishRepair(); crusher.SetUnsafeBypass(true); crusher.Accept(new PrototypeBatch { wetShortcut = true }); crusher.Tick(2f); Assert.IsNotNull(crusher.output); Object.DestroyImmediate(go);
        }

        [Test] public void ShortcutHasDelayedReadableConsequence()
        {
            var go = new GameObject("reactor-test"); var reactor = go.AddComponent<PrototypeReactorMachine>(); var valve = go.AddComponent<PrototypeCoolingValve>();
            LoadTwoFuel(reactor); reactor.UseUnsafeShortcut(); Assert.IsTrue(reactor.StartReactor()); reactor.Tick(1f, 0f, valve); Assert.AreEqual(1f, reactor.stability); reactor.Tick(4f, 0f, valve); Assert.LessOrEqual(reactor.stability, .75f); Object.DestroyImmediate(go);
        }

        [Test] public void ReactorEscalatesAndCoolingCanContain()
        {
            var go = new GameObject("reactor-test"); var reactor = go.AddComponent<PrototypeReactorMachine>(); var valve = go.AddComponent<PrototypeCoolingValve>(); valve.opening = 0f;
            LoadTwoFuel(reactor); reactor.StartReactor();
            for (int i = 0; i < 12; i++) reactor.Tick(.5f, 1f, valve);
            Assert.GreaterOrEqual((int)reactor.stage, (int)ReactorCrisisStage.CoolingEmergency); reactor.heat = .8f; valve.opening = 1f; reactor.EmergencyCooling(); Assert.AreEqual(ReactorCrisisStage.Contained, reactor.stage); Object.DestroyImmediate(go);
        }

        static void LoadTwoFuel(PrototypeReactorMachine reactor)
        {
            for (int i = 0; i < 2; i++)
            {
                var fuel = new GameObject("fuel-" + i).AddComponent<PrototypeFuelAssembly>();
                fuel.batch = new PrototypeBatch { mass = .5f, grade = .8f, fuelQuality = .75f };
                reactor.LoadFuel(fuel);
                Object.DestroyImmediate(fuel.gameObject);
            }
        }

        [Test] public void ResetReturnsCrusherAndReactorToKnownState()
        {
            var cg = new GameObject("crusher"); var crusher = cg.AddComponent<PrototypeCrusher>(); crusher.damage = 1f; crusher.ResetMachine(); Assert.AreEqual(CrusherState.Idle, crusher.state); Assert.AreEqual(0f, crusher.damage);
            var rg = new GameObject("reactor"); var reactor = rg.AddComponent<PrototypeReactorMachine>(); reactor.heat = 1f; reactor.ResetReactor(); Assert.AreEqual(ReactorCrisisStage.Stable, reactor.stage); Assert.AreEqual(1f, reactor.stability); Object.DestroyImmediate(cg); Object.DestroyImmediate(rg);
        }
    }
}
