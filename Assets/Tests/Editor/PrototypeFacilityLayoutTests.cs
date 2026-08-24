using System.Collections.Generic;
using CriticalShift.Prototype;
using NUnit.Framework;
using UnityEngine;

namespace CriticalShift.Prototype.Tests
{
    public sealed class PrototypeFacilityLayoutTests
    {
        readonly List<GameObject> created = new List<GameObject>();

        [TearDown]
        public void TearDown()
        {
            foreach (GameObject go in created)
                if (go != null) Object.DestroyImmediate(go);
            created.Clear();
        }

        [Test]
        public void AuthoredSpawnOverridesFallbackPositionAndRotation()
        {
            GameObject marker = Create(PrototypeFacilityLayout.PlayerSpawnMarker);
            marker.transform.position = new Vector3(12f, .06f, -8f);
            marker.transform.rotation = Quaternion.Euler(0f, 180f, 0f);

            Assert.AreEqual(marker.transform.position,
                PrototypeFacilityLayout.ResolvePosition(PrototypeFacilityLayout.PlayerSpawnMarker, Vector3.zero));
            Assert.Less(Quaternion.Angle(marker.transform.rotation,
                PrototypeFacilityLayout.ResolveRotation(PrototypeFacilityLayout.PlayerSpawnMarker, Quaternion.identity)), .01f);
        }

        [Test]
        public void AuthoredCartRouteUsesSiblingOrder()
        {
            Transform route = Create(PrototypeFacilityLayout.CartRouteMarker).transform;
            Vector3[] expected =
            {
                new Vector3(-4f, .8f, 2f),
                new Vector3(3f, .8f, -1f),
                new Vector3(9f, .8f, -7f)
            };
            for (int i = 0; i < expected.Length; i++)
            {
                GameObject waypoint = Create("Waypoint " + i);
                waypoint.transform.SetParent(route, false);
                waypoint.transform.position = expected[i];
            }

            Vector3[] resolved = PrototypeFacilityLayout.ResolveRoute(
                PrototypeFacilityLayout.CartRouteMarker, new[] { Vector3.zero, Vector3.one });

            CollectionAssert.AreEqual(expected, resolved);
        }

        [Test]
        public void MissingCartRouteKeepsOriginalFallback()
        {
            var fallback = new[] { Vector3.left, Vector3.right };
            Vector3[] resolved = PrototypeFacilityLayout.ResolveRoute("[ROUTE] Missing", fallback);

            CollectionAssert.AreEqual(fallback, resolved);
            Assert.AreNotSame(fallback, resolved);
        }

        GameObject Create(string name)
        {
            var go = new GameObject(name);
            created.Add(go);
            return go;
        }
    }
}
