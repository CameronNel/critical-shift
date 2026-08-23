using UnityEngine;

namespace CriticalShift.Prototype
{
    public sealed class PrototypeAlarmBeacon : MonoBehaviour
    {
        public bool Active { get; private set; }
        Light beacon;
        Renderer surface;
        Vector3 baseScale;

        void Awake()
        {
            surface = GetComponent<Renderer>();
            baseScale = transform.localScale;
            beacon = new GameObject("Alarm Point Light").AddComponent<Light>();
            beacon.transform.SetParent(transform);
            beacon.transform.localPosition = Vector3.up * .4f;
            beacon.type = LightType.Point;
            beacon.range = 8f;
            beacon.color = new Color(1f, .08f, .03f);
            beacon.enabled = false;
        }

        public void SetActive(bool active)
        {
            Active = active;
            if (beacon != null) beacon.enabled = active;
        }

        void Update()
        {
            if (!Active || beacon == null) return;
            beacon.intensity = 2.5f + Mathf.Sin(Time.time * 11f) * 1.7f;
            if (surface != null) surface.transform.localScale = baseScale * (1f + Mathf.Sin(Time.time * 11f) * .08f);
        }
    }
}
