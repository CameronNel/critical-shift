using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypePhysicsRecoveryTests
    {
        [Test]
        public void WorkerTransitionsThroughKnockdownAndRecovery()
        {
            var go = new GameObject("worker");
            var worker = go.AddComponent<PrototypeWorkerBody>();
            Assert.IsTrue(worker.KnockDown(1f));
            Assert.AreEqual(PrototypeWorkerBody.BodyState.KnockedDown, worker.State);
            Assert.IsTrue(worker.RestoreNormal());
            Assert.AreEqual(PrototypeWorkerBody.BodyState.Normal, worker.State);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void ReanimationConsumesPowerAndCompletesAfterDelay()
        {
            var bodyGo = new GameObject("body");
            var body = bodyGo.AddComponent<PrototypeWorkerBody>();
            body.Incapacitate();
            var station = new GameObject("station").AddComponent<PrototypeReanimationStation>();
            int power = 30;
            Assert.IsTrue(station.TryStart(body, ref power));
            Assert.AreEqual(5, power);
            station.TickForTest(3.9f);
            Assert.AreEqual(PrototypeWorkerBody.BodyState.Reanimating, body.State);
            station.TickForTest(0.2f);
            Assert.AreEqual(PrototypeWorkerBody.BodyState.Recovering, body.State);
            Object.DestroyImmediate(bodyGo); Object.DestroyImmediate(station.gameObject);
        }

        [Test]
        public void TntEmitsDelayedDetonation()
        {
            var wall = new GameObject("tnt").AddComponent<PrototypeTntWall>();
            wall.fuseSeconds = 2f;
            bool detonated = false; wall.Detonated += () => detonated = true;
            Assert.IsTrue(wall.Arm());
            wall.TickForTest(1.9f); Assert.IsFalse(detonated);
            wall.TickForTest(0.2f); Assert.IsTrue(detonated);
            Object.DestroyImmediate(wall.gameObject);
        }
    }
}
