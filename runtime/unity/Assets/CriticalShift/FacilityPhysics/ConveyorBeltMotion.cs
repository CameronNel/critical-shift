using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Bounded loop for debug belt tread markers; has no collision or rule authority.</summary>
    [DisallowMultipleComponent]
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
            if (markers != null || motor == null || !motor.transform.IsChildOf(transform) || treadMarkers == null || treadMarkers.Length == 0 || treadMarkers.Length > 64 ||
                beltLength <= 0 || float.IsNaN(beltLength) || float.IsInfinity(beltLength) || endRollers == null || endRollers.Length != 2 ||
                radius <= 0 || float.IsNaN(radius) || float.IsInfinity(radius))
                throw new ArgumentException("Bind an existing belt and its bounded tread markers.");
            var positions = new Vector3[treadMarkers.Length];
            var rotations = new Quaternion[endRollers.Length];
            var unique = new HashSet<Transform>();
            for (int i = 0; i < treadMarkers.Length; i++)
            {
                if (treadMarkers[i] == null || !unique.Add(treadMarkers[i])) throw new ArgumentException("Tread markers must be unique and present.");
                positions[i] = treadMarkers[i].localPosition;
            }
            for (int i = 0; i < endRollers.Length; i++)
            {
                if (endRollers[i] == null || !unique.Add(endRollers[i])) throw new ArgumentException("Roller pivots must be unique and present.");
                rotations[i] = endRollers[i].localRotation;
            }
            foreach (var visual in unique)
            {
                if (visual == transform || !visual.IsChildOf(transform)) throw new ArgumentException("Belt visuals must be descendants of their owner.");
                foreach (var other in unique)
                    if (visual != other && visual.IsChildOf(other)) throw new ArgumentException("Belt visuals cannot be nested.");
                if (visual.GetComponentsInChildren<Rigidbody>(true).Length != 0) throw new ArgumentException("Belt presentation cannot move physical bodies.");
                foreach (var collider in visual.GetComponentsInChildren<Collider>(true))
                    if (collider.enabled) throw new ArgumentException("Moving belt visuals must be non-contacting.");
            }
            drive = motor; length = beltLength; markers = (Transform[])treadMarkers.Clone(); rest = positions;
            rollers = (Transform[])endRollers.Clone(); rollerRest = rotations; rollerRadius = radius;
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
