using System;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded loop for debug belt tread markers; has no collision or rule authority.</summary>
    public sealed class ConveyorBeltMotion : MonoBehaviour
    {
        private ConveyorDrive drive;
        private Transform[] markers;
        private Vector3[] rest;
        private float length, travel;
        public void Initialize(ConveyorDrive motor, Transform[] treadMarkers, float beltLength)
        {
            if (markers != null || motor == null || treadMarkers == null || treadMarkers.Length == 0 || beltLength <= 0)
                throw new ArgumentException("Bind an existing belt and its bounded tread markers.");
            drive = motor; length = beltLength; markers = (Transform[])treadMarkers.Clone(); rest = new Vector3[markers.Length];
            for (int i = 0; i < markers.Length; i++)
            {
                if (markers[i] == null) throw new ArgumentException("A tread marker is missing.");
                rest[i] = markers[i].localPosition;
            }
        }
        private void LateUpdate()
        {
            if (drive == null || markers == null || !drive.Running) return;
            travel = Mathf.Repeat(travel + drive.BeltSpeed * Time.deltaTime, length);
            for (int i = 0; i < markers.Length; i++)
            {
                if (markers[i] == null) continue;
                Vector3 position = rest[i]; position.z = Mathf.Repeat(rest[i].z + length * 0.5f + travel, length) - length * 0.5f;
                markers[i].localPosition = position;
            }
        }
    }
}
