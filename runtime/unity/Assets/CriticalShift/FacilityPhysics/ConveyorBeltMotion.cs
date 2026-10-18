using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded loop for debug belt tread markers; has no collision or rule authority.</summary>
    public sealed class ConveyorBeltMotion : MonoBehaviour
    {
        private ConveyorDrive drive;
        private Transform[] markers;
        private Transform[] rollers;
        private Quaternion[] rollerRest;
        private Vector3[] rest;
        private float length, travel, rollerRadius, rollerAngle;
        public void Initialize(ConveyorDrive motor, Transform[] treadMarkers, float beltLength, Transform[] endRollers, float radius)
        {
            if (markers != null || motor == null || treadMarkers == null || treadMarkers.Length == 0 || treadMarkers.Length > 64 ||
                beltLength <= 0 || float.IsNaN(beltLength) || float.IsInfinity(beltLength) || endRollers == null || endRollers.Length != 2 ||
                radius <= 0 || float.IsNaN(radius) || float.IsInfinity(radius))
                throw new ArgumentException("Bind an existing belt and its bounded tread markers.");
            drive = motor; length = beltLength; markers = (Transform[])treadMarkers.Clone(); rest = new Vector3[markers.Length];
            rollers = (Transform[])endRollers.Clone(); rollerRest = new Quaternion[rollers.Length]; rollerRadius = radius;
            var unique = new HashSet<Transform>();
            for (int i = 0; i < markers.Length; i++)
            {
                if (markers[i] == null || !unique.Add(markers[i])) throw new ArgumentException("Tread markers must be unique and present.");
                rest[i] = markers[i].localPosition;
            }
            for (int i = 0; i < rollers.Length; i++)
            {
                if (rollers[i] == null || !unique.Add(rollers[i])) throw new ArgumentException("Roller pivots must be unique and present.");
                rollerRest[i] = rollers[i].localRotation;
            }
            foreach (var visual in unique)
            {
                if (visual.GetComponentsInChildren<Rigidbody>().Length != 0) throw new ArgumentException("Belt presentation cannot move physical bodies.");
                foreach (var collider in visual.GetComponentsInChildren<Collider>())
                    if (collider.enabled) throw new ArgumentException("Moving belt visuals must be non-contacting.");
            }
        }
        private void LateUpdate()
        {
            if (markers == null) return;
            if (drive == null) { enabled = false; throw new InvalidOperationException("A bound belt presentation drive was lost."); }
            foreach (var marker in markers)
                if (marker == null) { enabled = false; throw new InvalidOperationException("A bound belt tread visual was lost."); }
            foreach (var roller in rollers)
                if (roller == null) { enabled = false; throw new InvalidOperationException("A bound belt roller visual was lost."); }
            if (!drive.Running) return;
            float distance = drive.BeltSpeed * Mathf.Min(Time.deltaTime, 0.05f);
            travel = Mathf.Repeat(travel + distance, length);
            rollerAngle = Mathf.Repeat(rollerAngle + distance / rollerRadius * Mathf.Rad2Deg, 360);
            for (int i = 0; i < markers.Length; i++)
            {
                Vector3 position = rest[i]; position.z = Mathf.Repeat(rest[i].z + length * 0.5f + travel, length) - length * 0.5f;
                markers[i].localPosition = position;
            }
            for (int i = 0; i < rollers.Length; i++)
                rollers[i].localRotation = rollerRest[i] * Quaternion.AngleAxis(rollerAngle, Vector3.right);
        }
    }
}
