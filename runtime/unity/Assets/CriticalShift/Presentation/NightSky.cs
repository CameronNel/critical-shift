using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>
    /// Turns the night sky: rotates the stars about the celestial pole, moves the Moon along its arc with its phase, and aims and dims the
    /// moonlight to match. Cosmetic and local: each machine runs its own sky clock and no game rule reads it. While enabled it is the
    /// scene's only writer of RenderSettings.skybox, RenderSettings.sun and the _CS_* sky globals. See Content/Sky/README.md.
    /// </summary>
    [ExecuteAlways]
    [DisallowMultipleComponent]
    public sealed class NightSky : MonoBehaviour
    {
        const double SiderealDegreesPerHour = 360.0 / 23.9344696;   // the stars: one turn per sidereal day
        const double MoonDegreesPerHour = 360.0 / 24.8412;          // the Moon: a day plus its own eastward drift

        static readonly int SkyFromWorld = Shader.PropertyToID("_CS_SkyFromWorld");
        static readonly int MoonDir = Shader.PropertyToID("_CS_MoonDir");
        static readonly int MoonNorth = Shader.PropertyToID("_CS_MoonNorth");
        static readonly int SunDir = Shader.PropertyToID("_CS_SunDir");
        static readonly int SkyTime = Shader.PropertyToID("_CS_SkyTime");
        static readonly int Extinction = Shader.PropertyToID("_Extinction");

        [SerializeField, Tooltip("A material using the CriticalShift/NightSky shader.")] Material skyMaterial;
        [SerializeField, Tooltip("The directional light that plays the Moon.")] Light moonLight;

        [Header("Place")]
        [SerializeField, Range(-80f, 80f), Tooltip("Latitude in degrees: how high the celestial pole stands.")] float latitude = 52f;
        [SerializeField, Range(-180f, 180f), Tooltip("World yaw of true north in degrees (0 = +Z).")] float northHeading;

        [Header("Clock")]
        [SerializeField, Range(0f, 24f), Tooltip("Sky time when play starts, in hours.")] float startHour = 20f;
        [SerializeField, Min(0f), Tooltip("Sky seconds per real second. 20 runs 20:00 to 06:00 in a 30-minute shift.")] float timeScale = 20f;
        [SerializeField, Range(0f, 360f), Tooltip("Turns the star field: which constellations are up.")] float starRotation;

        [Header("Moon")]
        [SerializeField, Range(0f, 1f), Tooltip("Illuminated fraction: 0 new, 0.5 half, 1 full. It also sets when the Moon is up: a full Moon is up all night, a half Moon half of it.")] float moonIllumination = 0.97f;
        [SerializeField, Tooltip("Waxing: lit from the west, up in the evening. Waning: lit from the east, up in the morning.")] bool waxing = true;
        [SerializeField, Range(-28f, 28f), Tooltip("Declination in degrees: how high the Moon's arc runs.")] float moonDeclination = 15f;
        [SerializeField, Min(0f), Tooltip("Light intensity of a full Moon high in the sky.")] float fullMoonIntensity = 0.35f;
        [SerializeField] Color moonLightColor = new Color(0.78f, 0.86f, 1f);
        [SerializeField, Min(0f), Tooltip("Seconds between moonlight updates; 0 every frame. Raise it if the moving shadows shimmer.")] float lightUpdateInterval;

        double nextLightUpdate;

        /// <summary>Current sky time in hours since midnight of the first night (may exceed 24).</summary>
        public double SkyHours { get; private set; }

        void OnEnable()
        {
            if (skyMaterial == null || moonLight == null)
                Debug.LogWarning("NightSky needs a sky material and a moon light; the missing part is skipped.", this);
            if (skyMaterial != null) RenderSettings.skybox = skyMaterial;
            if (moonLight != null) RenderSettings.sun = moonLight;
            nextLightUpdate = 0.0;
            Apply();
            DynamicGI.UpdateEnvironment();
        }

        void OnDisable()
        {
            // Back to the shader's fixed sky; RenderSettings stay as they are for whoever takes over.
            Shader.SetGlobalVector(MoonDir, Vector4.zero);
            Shader.SetGlobalMatrix(SkyFromWorld, Matrix4x4.zero);
        }

        void OnValidate()
        {
            if (isActiveAndEnabled) { nextLightUpdate = 0.0; Apply(); }
        }

        void Update() => Apply();

        void Apply()
        {
            double seconds = Application.isPlaying ? Time.timeAsDouble : 0.0;
            SkyHours = startHour + seconds * timeScale / 3600.0;

            Quaternion northYaw = Quaternion.Euler(0f, northHeading, 0f);
            float lat = latitude * Mathf.Deg2Rad;
            Vector3 pole = northYaw * new Vector3(0f, Mathf.Sin(lat), Mathf.Cos(lat));
            Vector3 equatorSouth = northYaw * new Vector3(0f, Mathf.Cos(lat), -Mathf.Sin(lat));   // the celestial equator on the meridian

            float starAngle = (float)((SkyHours * SiderealDegreesPerHour + starRotation) % 360.0);
            Quaternion skyFromWorld = Quaternion.FromToRotation(pole, Vector3.up) * Quaternion.AngleAxis(-starAngle, pole);
            Shader.SetGlobalMatrix(SkyFromWorld, Matrix4x4.Rotate(skyFromWorld));

            // The Sun follows the clock (highest at 12:00) and is never drawn; the Moon sits its elongation east of it when waxing, west when
            // waning, so the phase also sets when the Moon is up. A full Moon stands opposite the Sun, below it on the ecliptic and vice versa.
            float elongation = 180f - Mathf.Acos(Mathf.Clamp(2f * moonIllumination - 1f, -1f, 1f)) * Mathf.Rad2Deg;   // Sun-Earth-Moon angle
            float sunHourAngle = (float)(((SkyHours - 12.0) * 15.0) % 360.0);
            float moonHourAngle = (float)(((SkyHours - 12.0) * MoonDegreesPerHour - (waxing ? elongation : -elongation)) % 360.0);
            Vector3 moon = OnSky(pole, equatorSouth, moonDeclination, moonHourAngle);
            Vector3 sun = OnSky(pole, equatorSouth, moonDeclination * Mathf.Cos(elongation * Mathf.Deg2Rad), sunHourAngle);
            float phaseAngle = Mathf.Acos(Mathf.Clamp(Vector3.Dot(sun, -moon), -1f, 1f)) * Mathf.Rad2Deg;              // Sun-Moon-Earth angle
            Vector3 moonNorth = Vector3.ProjectOnPlane(pole, moon).normalized;
            Shader.SetGlobalVector(MoonDir, moon);
            Shader.SetGlobalVector(MoonNorth, moonNorth);
            Shader.SetGlobalVector(SunDir, sun);
            Shader.SetGlobalVector(SkyTime, new Vector4((float)(Time.timeAsDouble % 600.0), 0f, 0f, 0f));

            if (moonLight == null || seconds < nextLightUpdate) return;
            nextLightUpdate = seconds + lightUpdateInterval;
            moonLight.transform.rotation = Quaternion.LookRotation(-moon, moonNorth);
            // Brightness against phase (Allen's lunar phase law), then through the air like the shader's starlight.
            float phaseMagnitude = 0.026f * phaseAngle + 4e-9f * Mathf.Pow(phaseAngle, 4f);
            Vector4 extinction = skyMaterial != null && skyMaterial.HasProperty(Extinction) ? skyMaterial.GetVector(Extinction) : new Vector4(0.11f, 0.17f, 0.30f, 0f);
            float airmass = Airmass(moon.y);
            Color through = new Color(Mathf.Exp(-extinction.x * airmass), Mathf.Exp(-extinction.y * airmass), Mathf.Exp(-extinction.z * airmass));
            float strength = through.maxColorComponent;
            moonLight.color = moonLightColor * (strength > 0f ? through / strength : Color.white);
            moonLight.intensity = fullMoonIntensity * Mathf.Pow(10f, -0.4f * phaseMagnitude) * strength * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(-0.03f, 0.05f, moon.y));
        }

        /// <summary>World direction of a body at the given declination and hour angle (degrees, growing westward with time).</summary>
        static Vector3 OnSky(Vector3 pole, Vector3 equatorSouth, float declination, float hourAngle)
        {
            float dec = declination * Mathf.Deg2Rad;
            Vector3 onMeridian = Mathf.Cos(dec) * equatorSouth + Mathf.Sin(dec) * pole;
            return Quaternion.AngleAxis(hourAngle, pole) * onMeridian;
        }

        /// <summary>Same airmass as the shader (Kasten and Young 1989).</summary>
        static float Airmass(float sinAltitude)
        {
            float s = Mathf.Clamp01(sinAltitude);
            return 1f / (s + 0.50572f * Mathf.Pow(Mathf.Asin(s) * Mathf.Rad2Deg + 6.07995f, -1.6364f));
        }
    }
}
