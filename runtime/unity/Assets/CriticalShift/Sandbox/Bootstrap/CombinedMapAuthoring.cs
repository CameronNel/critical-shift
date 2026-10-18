using System;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    [Serializable] public sealed class CombinedDoorCatalogue { public CombinedDoorRow[] doors; }
    [Serializable] public sealed class CombinedDoorRow
    {
        public string id, owner, kind, state, evac_state;
        public float[] plan, outward;
        public float clear_w, clear_h;
        public bool emergency_exit;
    }
    [Serializable] public sealed class CombinedColliderCatalogue { public CombinedColliderRow[] colliders; }
    [Serializable] public sealed class CombinedColliderRow
    { public string name, role, zone, door_id; public bool trigger; public float[] minimum, maximum; }
    [Serializable] public sealed class CombinedBindingManifest
    { public CombinedExportIdentity export; public CombinedRoomPlacement[] room_placements; }
    [Serializable] public sealed class CombinedExportIdentity { public string file, sha256; }
    [Serializable] public sealed class CombinedRoomPlacement { public string room; public float[] translation; public float rotation_z_deg; }

    [Serializable] public sealed class CombinedMapDoorReference
    {
        public CombinedDoorRow definition;
        public Transform anchor, interactionPoint;
        public Collider blocker, threshold;
    }

    /// <summary>Generated explicit scene references, copied with their one owned model subtree.</summary>
    public sealed class CombinedMapAuthoring : MonoBehaviour
    {
        [SerializeField] private CombinedMapDoorReference[] doors;
        [SerializeField] private Vector3 startPoint;
        [SerializeField] private Bounds localSafetyBounds;
        [SerializeField] private string sourceSha256;
        public CombinedMapDoorReference[] CopyDoorReferences() => doors == null ? null : (CombinedMapDoorReference[])doors.Clone();
        public Vector3 StartPoint => transform.TransformPoint(startPoint);
        public string SourceSha256 => sourceSha256;
        public Bounds LocalSafetyBounds => localSafetyBounds;
        public void Configure(CombinedMapDoorReference[] bindings, Vector3 localStartPoint, Bounds safetyBounds, string hash)
        {
            if (doors != null || bindings == null || bindings.Length == 0 || bindings.Length > 128 || hash == null || hash.Length != 64)
                throw new ArgumentException("Bind one generated combined-map reference set.");
            foreach (char value in hash) if (!Uri.IsHexDigit(value)) throw new ArgumentException("A map source SHA-256 is required.");
            doors = (CombinedMapDoorReference[])bindings.Clone(); startPoint = localStartPoint; localSafetyBounds = safetyBounds; sourceSha256 = hash;
        }
    }
}
