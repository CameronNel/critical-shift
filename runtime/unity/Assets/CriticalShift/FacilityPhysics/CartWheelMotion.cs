using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Wheel rotation from observed cart travel. Visual only: wheels never write cart pose.</summary>
    [DisallowMultipleComponent]
    public sealed class CartWheelMotion : MonoBehaviour
    {
        private Transform[] pivots;
        private Quaternion[] rest;
        private CartMotor motor;
        private Vector3 previousPosition;
        private float radius, angle;

        public void Initialize(CartMotor drive, Transform[] wheelPivots, float wheelRadius = 0.22f)
        {
            if (pivots != null || drive == null || drive.transform != transform || wheelPivots == null || wheelPivots.Length != 4 || wheelRadius <= 0 ||
                float.IsNaN(wheelRadius) || float.IsInfinity(wheelRadius))
                throw new ArgumentException("Bind one cart with four wheel pivots and a positive radius.");
            var unique = new HashSet<Transform>();
            var rotations = new Quaternion[4];
            for (int i = 0; i < wheelPivots.Length; i++)
            {
                var pivot = wheelPivots[i];
                if (pivot == null || !pivot.IsChildOf(transform) || !unique.Add(pivot))
                    throw new ArgumentException("Wheel pivots must be unique descendants of their cart.");
                if (pivot.GetComponentsInChildren<Rigidbody>(true).Length != 0)
                    throw new ArgumentException("Wheel presentation cannot move physical bodies.");
                foreach (var collider in pivot.GetComponentsInChildren<Collider>(true))
                    if (collider.enabled) throw new ArgumentException("Moving wheel visuals must be non-contacting.");
                rotations[i] = pivot.localRotation;
            }
            foreach (var pivot in unique)
                foreach (var other in unique)
                    if (pivot != other && pivot.IsChildOf(other)) throw new ArgumentException("Wheel pivots cannot be nested.");
            motor = drive; radius = wheelRadius; pivots = (Transform[])wheelPivots.Clone(); rest = rotations;
            previousPosition = transform.position;
        }

        private void LateUpdate()
        {
            if (pivots == null) return;
            if (motor == null) { enabled = false; throw new InvalidOperationException("A bound wheel presentation drive was lost."); }
            foreach (var pivot in pivots)
                if (pivot == null) { enabled = false; throw new InvalidOperationException("A bound cart wheel visual was lost."); }
            Vector3 travel = transform.position - previousPosition;
            previousPosition = transform.position;
            if (travel.sqrMagnitude < 9)
                angle = Mathf.Repeat(angle + Vector3.Dot(travel, transform.forward) / radius * Mathf.Rad2Deg, 360);
            float commandedSteering = motor.Steering;
            for (int i = 0; i < pivots.Length; i++)
            {
                Quaternion steering = Quaternion.AngleAxis(i < 2 ? commandedSteering * 22 : 0, Vector3.up);
                pivots[i].localRotation = rest[i] * steering * Quaternion.AngleAxis(angle, Vector3.right);
            }
        }

        private void OnEnable() { if (pivots != null) previousPosition = transform.position; }
    }
}
