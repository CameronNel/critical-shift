using UnityEngine;

namespace CriticalShift.Content.Editor
{
    /// <summary>Blender module frame to Unity, matching how the bake's FBX lands (Blender export axis_forward -Z, axis_up Y, unit scale applied;
    /// Unity's importer mirrors X to go from right- to left-handed). A Blender point (x, y, z) is Unity (-x, z, -y).
    /// Light units are starting values derived for a white diffuse surface, not a calibration: retune against the bake's compare renders.</summary>
    internal static class BlenderToUnity
    {
        public static Vector3 Point(double x, double y, double z) => new Vector3((float)-x, (float)z, (float)-y);

        /// <summary>A Blender rotation about +Z (degrees) as a Unity rotation: about +Y, the other way round, because the X mirror flips handedness.</summary>
        public static Quaternion MapYaw(double zDeg) => Quaternion.Euler(0f, (float)-zDeg, 0f);

        /// <summary>World rotation of a Blender light (its XYZ Euler, degrees) as a Unity rotation. Blender lights shine along their local -Z
        /// with +Y up; Unity lights shine along +Z.</summary>
        public static Quaternion LightRotation(double rxDeg, double ryDeg, double rzDeg)
        {
            float cx = Mathf.Cos((float)rxDeg * Mathf.Deg2Rad), sx = Mathf.Sin((float)rxDeg * Mathf.Deg2Rad);
            float cy = Mathf.Cos((float)ryDeg * Mathf.Deg2Rad), sy = Mathf.Sin((float)ryDeg * Mathf.Deg2Rad);
            float cz = Mathf.Cos((float)rzDeg * Mathf.Deg2Rad), sz = Mathf.Sin((float)rzDeg * Mathf.Deg2Rad);
            // R = Rz * Ry * Rx (Blender 'XYZ' order); columns 1 and 2 are the light's local Y and Z axes in the Blender world.
            var localY = new Vector3(cz * sy * sx - sz * cx, sz * sy * sx + cz * cx, cy * sx);
            var localZ = new Vector3(cz * sy * cx + sz * sx, sz * sy * cx - cz * sx, cy * cx);
            Vector3 forward = Point(-localZ.x, -localZ.y, -localZ.z), up = Point(localY.x, localY.y, localY.z);
            return Quaternion.LookRotation(forward, up);
        }

        /// <summary>Blender colours are scene-linear. Unity converts material and light colours from gamma to linear in a Linear project,
        /// so pass the gamma encoding of the linear value (this also keeps HDR values above 1 correct).</summary>
        public static Color LinearColor(double r, double g, double b, double a = 1.0) =>
            new Color(Mathf.LinearToGammaSpace((float)r), Mathf.LinearToGammaSpace((float)g), Mathf.LinearToGammaSpace((float)b), (float)a);

        // Cycles: a white diffuse surface d metres in front of the light reads P / (4 pi^2 d^2) for a point or spot of P watts,
        // P / (pi^2 d^2) per square metre of a small area light, and S / pi for a sun of strength S. URP (no 1/pi in its diffuse term,
        // inverse-square falloff) reads I / d^2 and I for a directional light, so these are the matching intensities.
        public static float PointIntensity(double watts) => (float)(watts / (4.0 * Mathf.PI * Mathf.PI));
        public static float AreaIntensity(double watts, double areaM2) => (float)(watts / (Mathf.PI * Mathf.PI * System.Math.Max(areaM2, 1e-4)));
        public static float SunIntensity(double strength) => (float)(strength / Mathf.PI);

        /// <summary>Range where the light falls to about 1 % of a unit-intensity light, clamped: keeps Forward+ light lists short.</summary>
        public static float Range(float intensity) => Mathf.Clamp(10f * Mathf.Sqrt(Mathf.Max(intensity, 0f)), 1f, 40f);
    }
}
