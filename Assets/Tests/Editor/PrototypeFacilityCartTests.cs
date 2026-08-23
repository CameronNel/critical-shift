using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeFacilityCartTests
    {
        [Test]
        public void CartLoadsVisibleOreAndReportsOverload()
        {
            var cartObject = new GameObject("cart");
            var cart = cartObject.AddComponent<PrototypeFacilityCart>();
            cart.ratedMass = 1f; cart.cargoSlotCount = 2;
            var oreObject = new GameObject("ore");
            var ore = oreObject.AddComponent<PrototypeOre>(); ore.batch.mass = 2f;
            bool warned = false; cart.OverloadWarning += _ => warned = true;
            Assert.IsTrue(cart.TryLoad(ore));
            Assert.AreEqual(1, cart.CargoCount); Assert.AreEqual(2f, cart.CurrentMass); Assert.IsTrue(warned);
            Assert.AreSame(cart.transform.GetChild(0), ore.transform.parent);
            Object.DestroyImmediate(cartObject); Object.DestroyImmediate(oreObject);
        }

        [Test]
        public void CartUnloadsBatchAndResetClearsCargo()
        {
            var cart = new GameObject("cart").AddComponent<PrototypeFacilityCart>();
            var oreObject = new GameObject("ore"); var ore = oreObject.AddComponent<PrototypeOre>(); ore.batch.mass = 1f;
            Assert.IsTrue(cart.TryLoad(ore));
            var hopper = new GameObject("hopper").transform;
            Assert.AreEqual(1, cart.UnloadBatch(hopper)); Assert.AreEqual(0, cart.CargoCount); Assert.AreEqual(0f, cart.CurrentMass);
            Assert.IsFalse(ore.Body.isKinematic);
            Object.DestroyImmediate(cart.gameObject); Object.DestroyImmediate(oreObject); Object.DestroyImmediate(hopper.gameObject);
        }

        [Test]
        public void HighSpeedCartHitCannotSoftLockTheOnlyPlayer()
        {
            var cart = new GameObject("cart").AddComponent<PrototypeFacilityCart>();
            var player = new GameObject("player");
            player.AddComponent<CharacterController>();
            player.AddComponent<PrototypePlayerController>();
            var worker = player.AddComponent<PrototypeWorkerBody>();
            cart.ApplyImpactForTest(worker, 100f);
            Assert.AreEqual(PrototypeWorkerBody.BodyState.KnockedDown, worker.State);
            Object.DestroyImmediate(cart.gameObject); Object.DestroyImmediate(player);
        }
    }
}
