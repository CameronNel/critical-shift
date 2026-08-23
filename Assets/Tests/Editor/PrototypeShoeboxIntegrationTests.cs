using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeShoeboxIntegrationTests
    {
        [Test]
        public void RuntimeBuildCreatesEveryProofOfFunScopeStation()
        {
            var directorObject = new GameObject("director");
            directorObject.AddComponent<PrototypeGameDirector>();
            var playerObject = new GameObject("player");
            playerObject.AddComponent<CharacterController>();
            playerObject.AddComponent<PrototypePlayerController>();
            var runtimeObject = new GameObject("runtime");
            var runtime = runtimeObject.AddComponent<PrototypeShoeboxRuntime>();
            runtime.Build(Vector3.zero);

            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeConveyor>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeCrusher>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeReactorMachine>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeReanimationStation>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeSuitLocker>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeTntWall>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeMineCart>());
            Assert.IsNotNull(Object.FindAnyObjectByType<PrototypeAlarmBeacon>());
            Assert.IsNotNull(GameObject.Find("Contract Worker 7"));
            Assert.IsNotNull(GameObject.Find("Compliance Officer"));

            Object.DestroyImmediate(runtimeObject);
            Object.DestroyImmediate(playerObject);
            Object.DestroyImmediate(directorObject);
        }

        [Test]
        public void DryOreCanBecomeTwoPhysicalFuelLoadsAndStartReactor()
        {
            var crusherObject = new GameObject("crusher");
            var crusher = crusherObject.AddComponent<PrototypeCrusher>();
            crusher.BeginOperation();
            crusher.Tick(.3f);
            Assert.IsTrue(crusher.Accept(new PrototypeBatch { mass = 1f, grade = .8f, moisture = .05f }));
            crusher.Tick(.01f);
            crusher.Tick(2f);
            var processed = crusher.TakeOutput().AssembleFuel();

            var reactorObject = new GameObject("reactor");
            var reactor = reactorObject.AddComponent<PrototypeReactorMachine>();
            var firstObject = new GameObject("fuel-1");
            var first = firstObject.AddComponent<PrototypeFuelAssembly>();
            first.batch = processed;
            var secondObject = new GameObject("fuel-2");
            var second = secondObject.AddComponent<PrototypeFuelAssembly>();
            second.batch = processed.Clone();

            Assert.IsTrue(reactor.LoadFuel(first));
            Assert.IsTrue(reactor.LoadFuel(second));
            Assert.AreEqual(2, reactor.LoadedBatches);
            Assert.IsTrue(reactor.StartReactor());
            reactor.Tick(2f, .7f, null);
            Assert.Greater(reactor.output, 0f);

            Object.DestroyImmediate(firstObject);
            Object.DestroyImmediate(secondObject);
            Object.DestroyImmediate(reactorObject);
            Object.DestroyImmediate(crusherObject);
        }

        [Test]
        public void CrusherBypassPropagatesHiddenDefectToReactorRisk()
        {
            var crusherObject = new GameObject("crusher");
            var crusher = crusherObject.AddComponent<PrototypeCrusher>();
            crusher.BeginOperation();
            crusher.Tick(.3f);
            crusher.SetUnsafeBypass(true);
            crusher.Accept(new PrototypeBatch { mass = 1f, grade = .8f, moisture = .6f, wetShortcut = true });
            crusher.Tick(.01f);
            crusher.Tick(2f);
            var batch = crusher.TakeOutput().AssembleFuel();
            Assert.Greater(batch.hiddenDefect, 0f);

            var reactorObject = new GameObject("reactor");
            var reactor = reactorObject.AddComponent<PrototypeReactorMachine>();
            for (int i = 0; i < 2; i++)
            {
                var fuelObject = new GameObject("fuel-" + i);
                var fuel = fuelObject.AddComponent<PrototypeFuelAssembly>();
                fuel.batch = batch.Clone();
                Assert.IsTrue(reactor.LoadFuel(fuel));
                Object.DestroyImmediate(fuelObject);
            }
            Assert.IsTrue(reactor.UnsafeFuelLoaded);
            Object.DestroyImmediate(reactorObject);
            Object.DestroyImmediate(crusherObject);
        }
    }
}
