using System;
using System.Text.Json;

namespace CriticalShift.Scenarios
{
    internal static class ScenarioInput
    {
        internal static Guid Id(int value) => new Guid(value, 0, 0, new byte[8]);
        internal static string Text(JsonElement s, string key) =>
            s.GetProperty(key).GetString() ?? throw new ArgumentException("Missing string: " + key);
        internal static long Number(JsonElement s, string key, long? fallback = null) =>
            s.TryGetProperty(key, out var value) ? value.GetInt64() : fallback ?? throw new ArgumentException("Missing number: " + key);
        internal static bool Flag(JsonElement s, string key, bool fallback) => s.TryGetProperty(key, out var v) ? v.GetBoolean() : fallback;
        internal static T Choice<T>(JsonElement s, string key) where T : struct, Enum
        {
            string input = Text(s, key);
            return Enum.TryParse<T>(input, out var value) && Enum.IsDefined(typeof(T), value) && value.ToString() == input ?
                value : throw new ArgumentException("Invalid enum value for " + key);
        }

    }
}
