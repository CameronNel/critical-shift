using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Prototype
{
    public enum PrototypeFacilityWaypointId
    {
        Briefing, Preparation, Mine, Refinery, Reactor, Compliance, Recovery, Cooling, Debrief
    }

    [Serializable]
    public struct PrototypeFacilityWaypoint
    {
        public PrototypeFacilityWaypointId id;
        public string label;
        public Vector3 worldPosition;

        public PrototypeFacilityWaypoint(PrototypeFacilityWaypointId id, string label, Vector3 worldPosition)
        { this.id = id; this.label = label; this.worldPosition = worldPosition; }
    }

    /// Deterministic full-map objective/waypoint state. Kept independent of scene objects
    /// so host-local tests and a future replicated intent layer can use the same model.
    public sealed class PrototypeFacilityGuidanceModel
    {
        readonly Dictionary<PrototypeFacilityWaypointId, PrototypeFacilityWaypoint> waypoints =
            new Dictionary<PrototypeFacilityWaypointId, PrototypeFacilityWaypoint>();
        bool hasTarget;
        public PrototypeShiftState Phase { get; private set; }
        public PrototypeFacilityWaypointId? TargetId { get; private set; }
        public string ObjectiveLabel { get; private set; }
        public string TargetLabel { get; private set; }
        public Vector3 TargetWorldPosition { get; private set; }
        public bool HasTarget { get { return hasTarget; } }
        public IReadOnlyDictionary<PrototypeFacilityWaypointId, PrototypeFacilityWaypoint> Waypoints { get { return waypoints; } }

        public PrototypeFacilityGuidanceModel()
        {
            RegisterDefaults();
            Reset();
        }

        public void Register(PrototypeFacilityWaypoint waypoint) { waypoints[waypoint.id] = waypoint; }

        public void RegisterDefaults()
        {
            // Coordinates match the authored FacilityGreybox route landmarks.
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Briefing, "BRIEFING BOARD", new Vector3(-72f, .25f, -35.34f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Preparation, "SUIT / TOOL PREPARATION", new Vector3(-59.16f, 0f, -49.5f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Mine, "GULLET MINE DRILL", new Vector3(-88.8f, -1.2f, 2.4f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Refinery, "REFINERY LINE", new Vector3(-27.6f, 0f, -31.2f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Reactor, "REACTOR CONTROL", new Vector3(2.4f, 0f, -7.8f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Compliance, "COMPLIANCE ROAD", new Vector3(6f, .25f, -68.4f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Recovery, "REANIMATION / RECOVERY", new Vector3(-18f, 0f, 31.2f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Cooling, "EMERGENCY COOLING", new Vector3(3f, 0f, 7.8f)));
            Register(new PrototypeFacilityWaypoint(PrototypeFacilityWaypointId.Debrief, "SHIFT DEBRIEF", new Vector3(-72f, .25f, -35.34f)));
        }

        public bool SetPhase(PrototypeShiftState phase)
        {
            Phase = phase;
            switch (phase)
            {
                case PrototypeShiftState.Briefing: return SetTarget(PrototypeFacilityWaypointId.Briefing, "Open briefing");
                case PrototypeShiftState.Mining: return SetTarget(PrototypeFacilityWaypointId.Mine, "Mine ore");
                case PrototypeShiftState.Refining: return SetTarget(PrototypeFacilityWaypointId.Refinery, "Refine fuel");
                case PrototypeShiftState.Reactor: return SetTarget(PrototypeFacilityWaypointId.Reactor, "Start reactor");
                case PrototypeShiftState.CoolingEmergency: return SetTarget(PrototypeFacilityWaypointId.Cooling, "Open emergency cooling");
                case PrototypeShiftState.Won:
                case PrototypeShiftState.Failed: return SetTarget(PrototypeFacilityWaypointId.Debrief, "Review shift debrief");
                default: ClearTarget(); return true;
            }
        }

        public bool SetTarget(PrototypeFacilityWaypointId id, string objective = null)
        {
            PrototypeFacilityWaypoint waypoint;
            if (!waypoints.TryGetValue(id, out waypoint)) return false;
            TargetId = id;
            hasTarget = true;
            TargetLabel = waypoint.label;
            ObjectiveLabel = string.IsNullOrEmpty(objective) ? waypoint.label : objective;
            TargetWorldPosition = waypoint.worldPosition;
            return true;
        }

        public void SetWorldTarget(string label, Vector3 worldPosition, string objective = null)
        {
            TargetId = null;
            hasTarget = true;
            TargetLabel = label ?? "TARGET";
            ObjectiveLabel = string.IsNullOrEmpty(objective) ? TargetLabel : objective;
            TargetWorldPosition = worldPosition;
        }

        public void ClearTarget()
        {
            TargetId = null; hasTarget = false; TargetLabel = string.Empty; ObjectiveLabel = string.Empty; TargetWorldPosition = Vector3.zero;
        }

        public void Reset()
        {
            Phase = PrototypeShiftState.Briefing;
            SetTarget(PrototypeFacilityWaypointId.Briefing, "Open briefing");
        }
    }

    /// Low-cost world marker. It does not allocate per-frame and uses a property block,
    /// preserving shared materials while providing a readable pulsing beacon.
    public sealed class PrototypeFacilityGuidanceBeacon : MonoBehaviour
    {
        [SerializeField] float pulseSpeed = 3f;
        [SerializeField] float pulseScale = .12f;
        [SerializeField] Renderer beaconRenderer;
        MaterialPropertyBlock propertyBlock;
        Vector3 baseScale;
        bool targeted;
        string targetLabel = string.Empty;
        float distance;

        public bool IsTargeted { get { return targeted; } }
        public string TargetLabel { get { return targetLabel; } }
        public Vector3 TargetWorldPosition { get { return targeted ? transform.position : Vector3.zero; } }
        public float DistanceToTarget { get { return distance; } }
        public float Pulse01 { get; private set; }

        void Awake()
        {
            baseScale = transform.localScale;
            if (beaconRenderer == null) beaconRenderer = GetComponentInChildren<Renderer>();
            propertyBlock = new MaterialPropertyBlock();
        }

        void Update()
        {
            if (!targeted) return;
            Pulse01 = (Mathf.Sin(Time.time * pulseSpeed) + 1f) * .5f;
            transform.localScale = baseScale * (1f + Pulse01 * pulseScale);
            if (beaconRenderer != null)
            {
                beaconRenderer.GetPropertyBlock(propertyBlock);
                propertyBlock.SetColor("_EmissionColor", Color.Lerp(new Color(.05f, .35f, 1f), Color.cyan, Pulse01));
                beaconRenderer.SetPropertyBlock(propertyBlock);
            }
        }

        public void Target(Vector3 worldPosition, string label, Transform observer = null)
        {
            transform.position = worldPosition;
            targetLabel = label ?? "TARGET";
            targeted = true;
            distance = observer == null ? 0f : Vector3.Distance(observer.position, worldPosition);
        }

        public void UpdateDistance(Transform observer)
        { distance = targeted && observer != null ? Vector3.Distance(observer.position, transform.position) : 0f; }

        public void ResetBeacon()
        {
            targeted = false; targetLabel = string.Empty; distance = 0f; Pulse01 = 0f;
            transform.localScale = baseScale == Vector3.zero ? Vector3.one : baseScale;
        }
    }

    /// Scene-facing bridge: consumers can drive this with PrototypeShiftState without
    /// coupling the model to a particular HUD or navigation implementation.
    public sealed class PrototypeFacilityGuidance : MonoBehaviour
    {
        public PrototypeFacilityGuidanceModel Model { get; private set; }
        public PrototypeFacilityGuidanceBeacon Beacon { get; private set; }
        public string ObjectiveLabel { get { return Model == null ? string.Empty : Model.ObjectiveLabel; } }
        public string TargetLabel { get { return Model == null ? string.Empty : Model.TargetLabel; } }

        void Awake()
        {
            Model = new PrototypeFacilityGuidanceModel();
            Beacon = GetComponentInChildren<PrototypeFacilityGuidanceBeacon>();
        }

        public void SetPhase(PrototypeShiftState phase)
        {
            if (Model == null) Model = new PrototypeFacilityGuidanceModel();
            Model.SetPhase(phase);
            ApplyTarget();
        }

        public bool SetTarget(PrototypeFacilityWaypointId id, string objective = null)
        {
            if (Model == null) Model = new PrototypeFacilityGuidanceModel();
            bool found = Model.SetTarget(id, objective); ApplyTarget(); return found;
        }

        public void SetWorldTarget(string label, Vector3 position, string objective = null)
        {
            if (Model == null) Model = new PrototypeFacilityGuidanceModel();
            Model.SetWorldTarget(label, position, objective); ApplyTarget();
        }

        public void ResetGuidance()
        {
            if (Model == null) Model = new PrototypeFacilityGuidanceModel();
            Model.Reset();
            if (Beacon != null) Beacon.ResetBeacon();
        }

        void ApplyTarget()
        {
            if (Beacon == null || Model == null || !Model.HasTarget) return;
            Beacon.Target(Model.TargetWorldPosition, Model.TargetLabel);
        }
    }
}
