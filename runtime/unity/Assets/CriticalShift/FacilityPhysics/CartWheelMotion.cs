using System;
using UnityEngine;

namespace CriticalShift.FacilityPhysics
{
    /// <summary>Wheel rotation from observed cart travel. Visual only: wheels never write cart pose.</summary>
    public sealed class CartWheelMotion : MonoBehaviour
    {
        private Transform[] pivots;
        private Quaternion[] rest;
        private CartMotor motor;
        private Vector3 previousPosition;
        private float radius, angle;

        public void Initialize(CartMotor drive, Transform[] wheelPivots, float wheelRadius = 0.22f)
        {
            if (pivots != null || drive == null || wheelPivots == null || wheelPivots.Length != 4 || wheelRadius <= 0 ||
                float.IsNaN(wheelRadius) || float.IsInfinity(wheelRadius))
                throw new ArgumentException("Bind one cart with four wheel pivots and a positive radius.");
            motor = drive; radius = wheelRadius; pivots = (Transform[])wheelPivots.Clone(); rest = new Quaternion[4];
            for (int i = 0; i < pivots.Length; i++)
            {
                if (pivots[i] == null) throw new ArgumentException("A wheel pivot is missing.");
                rest[i] = pivots[i].localRotation;
            }
            previousPosition = transform.position;
        }

        private void LateUpdate()
        {
            if (pivots == null || motor == null) return;
            Vector3 travel = transform.position - previousPosition;
            previousPosition = transform.position;
            if (travel.sqrMagnitude < 9)
                angle = Mathf.Repeat(angle + Vector3.Dot(travel, transform.forward) / radius * Mathf.Rad2Deg, 360);
            float commandedSteering = motor.Steering;
            for (int i = 0; i < pivots.Length; i++)
            {
                if (pivots[i] == null) continue;
                Quaternion steering = Quaternion.AngleAxis(i < 2 ? commandedSteering * 22 : 0, Vector3.up);
                pivots[i].localRotation = rest[i] * steering * Quaternion.AngleAxis(angle, Vector3.right);
            }
        }
    }
}
