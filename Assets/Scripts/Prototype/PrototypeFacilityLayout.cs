using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    /// <summary>
    /// Resolves optional scene-authored layout markers while preserving the original
    /// FacilityGreybox coordinates as deterministic fallbacks.
    /// </summary>
    public static class PrototypeFacilityLayout
    {
        public const string PlayerSpawnMarker = "[SPAWN] Player Start";
        public const string CartRouteMarker = "[ROUTE] Facility Cart";
        public const string OreOutputMarker = "[SPAWN] Ore Output";
        public const string MineTntMarker = "[SPAWN] Mine TNT Charge";
        public const string HopperDeckMarker = "[TARGET] Hopper Deck";

        public static Transform FindNamedTransform(string objectName)
        {
            foreach (Transform candidate in Object.FindObjectsByType<Transform>(
                         FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (candidate != null && candidate.name == objectName) return candidate;
            }
            return null;
        }

        public static Vector3 ResolvePosition(string objectName, Vector3 fallback)
        {
            Transform target = FindNamedTransform(objectName);
            return target == null ? fallback : target.position;
        }

        public static Quaternion ResolveRotation(string objectName, Quaternion fallback)
        {
            Transform target = FindNamedTransform(objectName);
            return target == null ? fallback : target.rotation;
        }

        public static Vector3[] ResolveRoute(string routeName, IReadOnlyList<Vector3> fallback)
        {
            Transform route = FindNamedTransform(routeName);
            if (route == null || route.childCount < 2) return Copy(fallback);

            var points = new Vector3[route.childCount];
            for (int i = 0; i < route.childCount; i++) points[i] = route.GetChild(i).position;
            return points;
        }

        static Vector3[] Copy(IReadOnlyList<Vector3> source)
        {
            var copy = new Vector3[source.Count];
            for (int i = 0; i < source.Count; i++) copy[i] = source[i];
            return copy;
        }
    }
}
