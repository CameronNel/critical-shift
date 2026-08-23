using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Pure, deterministic rules for the tiny vertical-slice shift loop.
    public static class PrototypeShiftRules
    {
        public const int OreQuota = 3;
        public const int FuelQuota = 2;
        public const float ShiftSeconds = 420f;
        public const float EmergencySeconds = 25f;
        public const float RecoveredHeat = 68f;

        public static bool HasFuelQuota(int fuel) => fuel >= FuelQuota;
        public static float ReactorHeatFor(int fuel, bool unsafeShortcut) =>
            Mathf.Clamp(20f + (fuel * 18f) + (unsafeShortcut ? 50f : 0f), 0f, 120f);
        public static bool IsMeltdown(float heat) => heat >= 100f;
    }
}
