using NUnit.Framework;
using UnityEngine;
using CriticalShift.Prototype;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeFacilityMachineTests
    {
        static T Make<T>() where T : PrototypeFacilityMachine { var go = new GameObject(typeof(T).Name); var value = go.AddComponent<T>(); value.BeginOperation(); value.Tick(.3f); return value; }

        [Test] public void FullRefineryChainProducesInspectedFuel()
        {
            var raw = new PrototypeBatch { form = OreForm.Crushed, grade = .8f, rock = .2f, contamination = .05f, moisture = .2f };
            var s = Make<PrototypeSorter>(); Assert.IsTrue(s.Accept(raw)); s.Tick(2f); var sorted = s.TakeOutput();
            var p = Make<PrototypeProcessor>(); Assert.IsTrue(p.Accept(sorted)); p.Tick(2f); var processed = p.TakeOutput();
            var d = Make<PrototypeDryer>(); Assert.IsTrue(d.Accept(processed)); d.Tick(2f); var dried = d.TakeOutput();
            var a = Make<PrototypeFuelAssemblyStation>(); Assert.IsTrue(a.Accept(dried)); a.Tick(2f); var fuel = a.TakeOutput();
            var i = Make<PrototypeInspectionStation>(); Assert.IsTrue(i.Accept(fuel)); i.Tick(2f); var inspected = i.TakeOutput();
            Assert.AreEqual(OreForm.Sorted, sorted.form); Assert.AreEqual(OreForm.Processed, processed.form); Assert.AreEqual(OreForm.Dried, dried.form); Assert.AreEqual(OreForm.Dried, inspected.form); Assert.Greater(inspected.fuelQuality, .4f); Assert.Greater(inspected.inspectionConfidence, .5f); Object.DestroyImmediate(s.gameObject); Object.DestroyImmediate(p.gameObject); Object.DestroyImmediate(d.gameObject); Object.DestroyImmediate(a.gameObject); Object.DestroyImmediate(i.gameObject);
        }

        [Test] public void UnsafeShortcutsPropagateDefectAndWarning()
        {
            var go = new GameObject("sorter"); var s = go.AddComponent<PrototypeSorter>(); s.BeginOperation(); s.Tick(.3f); bool warned = false; s.WarningRaised += _ => warned = true; s.SetUnsafeShortcut(true); s.Accept(new PrototypeBatch { form = OreForm.Crushed, hiddenDefect = .1f }); s.Tick(2f); Assert.IsTrue(warned); Assert.Greater(s.TakeOutput().hiddenDefect, .1f); Object.DestroyImmediate(go);
        }

        [Test] public void ResetClearsStageAndShortcut()
        {
            var go = new GameObject("dryer"); var d = go.AddComponent<PrototypeDryer>(); d.BeginOperation(); d.Tick(.3f); d.SetUnsafeShortcut(true); d.Accept(new PrototypeBatch { form = OreForm.Processed }); d.ResetMachine(); Assert.AreEqual(FacilityMachineState.Idle, d.state); Assert.IsFalse(d.unsafeShortcut); Assert.IsNull(d.input); Assert.IsNull(d.output); Object.DestroyImmediate(go);
        }

        [Test] public void InspectionConfidenceReflectsHiddenDefect()
        {
            var go = new GameObject("inspection"); var i = go.AddComponent<PrototypeInspectionStation>(); i.BeginOperation(); i.Tick(.3f); i.Accept(new PrototypeBatch { form = OreForm.Dried, fuelQuality = .8f, hiddenDefect = .8f }); i.Tick(2f); var result = i.TakeOutput(); Assert.Less(result.inspectionConfidence, .6f); Object.DestroyImmediate(go);
        }
    }
}
