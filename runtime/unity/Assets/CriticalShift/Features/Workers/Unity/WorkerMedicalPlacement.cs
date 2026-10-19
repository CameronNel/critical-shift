using System;
using CriticalShift.Application;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    /// <summary>World-scoped staged physical handoff. Medical rules and custody remain in Application.</summary>
    public sealed class WorkerMedicalPlacement
    {
        private sealed class Shape
        {
            internal readonly Rigidbody Body;
            internal readonly CapsuleCollider Contact;
            internal readonly Vector3 Offset, Axis;
            internal readonly float Radius, Extent;
            private readonly Vector3 center;
            private readonly float height;
            private readonly int direction;
            internal Shape(Rigidbody body, Collider contact)
            {
                Body = body; Contact = contact as CapsuleCollider;
                if (Contact == null || !ValidDimensions(Contact) || !UnitScale(Contact.transform) || !DefaultLayers(Contact) || !DefaultBodyLayers(Body))
                    throw new ArgumentException("Medical fixture body segments require explicit unit-scale capsule contacts.");
                center = Contact.center; height = Contact.height; direction = Contact.direction; Radius = Contact.radius;
                Extent = Mathf.Max(0, height * 0.5f - Radius);
                Offset = body.transform.InverseTransformPoint(Contact.transform.TransformPoint(center));
                Vector3 axis = direction == 0 ? Vector3.right : direction == 1 ? Vector3.up : Vector3.forward;
                Axis = Quaternion.Inverse(body.transform.rotation) * (Contact.transform.rotation * axis);
            }
            internal bool Matches()
            {
                if (Body == null || Contact == null || !ValidDimensions(Contact) || !UnitScale(Contact.transform) || !DefaultLayers(Contact) || !DefaultBodyLayers(Body) ||
                    !Finite(Body.position) || !WorkerBodyRig.ValidMedicalRotation(Body.rotation) ||
                    !Finite(Body.linearVelocity) || !Finite(Body.angularVelocity) ||
                    Contact.center != center || Contact.height != height || Contact.radius != Radius || Contact.direction != direction) return false;
                Vector3 axis = direction == 0 ? Vector3.right : direction == 1 ? Vector3.up : Vector3.forward;
                return (Body.transform.InverseTransformPoint(Contact.transform.TransformPoint(center)) - Offset).sqrMagnitude <= 0.0000001f &&
                    (Quaternion.Inverse(Body.transform.rotation) * (Contact.transform.rotation * axis) - Axis).sqrMagnitude <= 0.0000001f;
            }
            private static bool ValidDimensions(CapsuleCollider shape) => !shape.isTrigger &&
                Finite(shape.center) && Finite(shape.radius) && Finite(shape.height) && shape.radius > 0 && shape.height > 0 &&
                shape.direction >= 0 && shape.direction <= 2;
        }

        private sealed class Plan
        {
            internal readonly ObjectClaimView Before;
            internal readonly Guid Station;
            internal readonly bool Entering;
            internal readonly Transform Anchor;
            internal readonly BoxCollider Support;
            internal readonly Vector3 AnchorPosition, AnchorScale, SupportPosition, SupportScale, SupportCenter, SupportSize;
            internal readonly Quaternion AnchorRotation, SupportRotation;
            internal readonly Vector3[] Positions;
            internal readonly Quaternion[] Rotations;
            internal Plan(ObjectClaimView before, Guid station, bool entering, Transform anchor, BoxCollider support, int count)
            {
                Before = before; Station = station; Entering = entering; Anchor = anchor; Support = support;
                AnchorPosition = anchor.position; AnchorRotation = anchor.rotation; AnchorScale = anchor.lossyScale;
                SupportPosition = support.transform.position; SupportRotation = support.transform.rotation; SupportScale = support.transform.lossyScale;
                SupportCenter = support.center; SupportSize = support.size;
                Positions = new Vector3[count]; Rotations = new Quaternion[count];
            }
        }

        private WorkerBodyRig rig;
        private bool bound;
        private Shape[] shapes;
        private Plan staged, held;
        private readonly Collider[] overlaps = new Collider[32];

        public void Bind(WorkerBodyRig body)
        {
            if (bound || body == null || body.BodyEntity == Guid.Empty || !body.Available)
                throw new InvalidOperationException("Bind one initialized worker with its explicit logical body identity.");
            var segments = body.CopyBodySegments(); var contacts = body.CopyMedicalContacts();
            if (segments.Length != contacts.Length || segments.Length < 2 || segments.Length > 16)
                throw new InvalidOperationException("Medical placement requires every bounded worker segment and contact.");
            var proposed = new Shape[segments.Length];
            for (int i = 0; i < proposed.Length; i++) proposed[i] = new Shape(segments[i], contacts[i]);
            body.BindMedicalPlacement();
            rig = body; shapes = proposed; bound = true;
        }

        public bool Prepare(ObjectClaimView before, Guid station, Transform anchor, Collider support, bool entering)
        {
            staged = null;
            if (rig == null || !rig.Available || before == null || before.Epoch != rig.Epoch || before.EntityId != rig.BodyEntity ||
                before.IsRetired || before.Revision == long.MaxValue || station == Guid.Empty ||
                (entering ? !rig.IsFreeRagdoll || !before.HolderId.HasValue || before.SlotId.HasValue || before.LeaseGeneration < 1 :
                    !rig.IsChambered || before.HolderId.HasValue || before.SlotId != station)) return false;
            if (!entering) ValidateHeld(before, station);
            var box = support as BoxCollider;
            if (!ValidSupport(anchor, box)) return false;
            foreach (var shape in shapes) if (!shape.Matches()) throw new InvalidOperationException("A worker's medical contact geometry changed after binding.");
            var plan = new Plan(before, station, entering, anchor, box, shapes.Length);
            // Stored local +Y points toward the head and +Z toward the face: head along bed forward, face up.
            Quaternion supine = Quaternion.LookRotation(anchor.up, anchor.forward);
            rig.BuildMedicalPose(anchor.position, supine, plan.Positions, plan.Rotations);
            float lowest = float.PositiveInfinity;
            for (int i = 0; i < shapes.Length; i++)
            {
                var shape = shapes[i]; Vector3 center = plan.Positions[i] + plan.Rotations[i] * shape.Offset;
                Vector3 axis = plan.Rotations[i] * shape.Axis;
                lowest = Mathf.Min(lowest, center.y - Mathf.Abs(axis.y) * shape.Extent - shape.Radius);
            }
            if (!Finite(lowest)) return false;
            float lift = SupportTop(box).y + 0.04f - lowest;
            for (int i = 0; i < plan.Positions.Length; i++) plan.Positions[i] += Vector3.up * lift;
            if (!Clear(plan)) return false;
            staged = plan; return true;
        }

        public void CancelStage() => staged = null;

        public void Reconcile(ObjectClaimView current, Guid station)
        {
            if (rig == null) throw new InvalidOperationException("A live medical worker lost its placement binding.");
            if (current != null && (current.Epoch != rig.Epoch || current.EntityId != rig.BodyEntity))
                throw new InvalidOperationException("Medical placement cannot accept another epoch or body.");
            if (current == null || current.IsRetired) { Clear(); return; }
            if (current.SlotId.HasValue)
            {
                if (station == Guid.Empty || current.SlotId != station || current.HolderId.HasValue)
                    throw new InvalidOperationException("A worker occupies an unbound medical slot.");
                if (held != null)
                {
                    ValidateHeld(current, station);
                    return;
                }
                Apply(current, station, true); return;
            }
            if (rig.IsChambered) Apply(current, station, false);
            else if (held != null) throw new InvalidOperationException("Medical custody lost its chambered motion owner.");
        }

        private void ValidateHeld(ObjectClaimView current, Guid station)
        {
            if (held == null || current.SlotId != station || current.HolderId.HasValue ||
                current.Revision != held.Before.Revision + 1 || current.LeaseGeneration != held.Before.LeaseGeneration || station != held.Station ||
                !BindingsMatch(held) || !rig.MatchesMedicalPose(held.Positions, held.Rotations))
                throw new InvalidOperationException("The chambered worker lost its exact custody, pose or static binding.");
            foreach (var shape in shapes)
                if (!shape.Matches()) throw new InvalidOperationException("A chambered worker's contact geometry or motion became invalid.");
        }

        private void Apply(ObjectClaimView current, Guid station, bool entering)
        {
            var plan = staged;
            if (plan == null || plan.Entering != entering || plan.Station != station || current.HolderId.HasValue ||
                current.Revision != plan.Before.Revision + 1 || current.LeaseGeneration != plan.Before.LeaseGeneration ||
                (entering ? current.SlotId != station : current.SlotId.HasValue) || !BindingsMatch(plan) || !Clear(plan))
                throw new InvalidOperationException("Accepted medical custody has no exact safe staged physical handoff.");
            if (!entering) ValidateHeld(plan.Before, station);
            rig.ApplyMedicalPose(entering, plan.Positions, plan.Rotations);
            held = entering ? plan : null; staged = null;
        }

        private bool Clear(Plan plan)
        {
            if (!BindingsMatch(plan) || !rig.Available) return false;
            Vector3 scale = plan.Support.transform.lossyScale;
            for (int i = 0; i < shapes.Length; i++)
            {
                var shape = shapes[i]; if (!shape.Matches()) return false;
                if (Physics.GetIgnoreLayerCollision(shape.Contact.gameObject.layer, plan.Support.gameObject.layer) ||
                    Physics.GetIgnoreCollision(shape.Contact, plan.Support)) return false;
                Vector3 position = plan.Positions[i]; Quaternion rotation = plan.Rotations[i];
                if (!Finite(position) || !WorkerBodyRig.ValidMedicalRotation(rotation)) return false;
                Vector3 center = position + rotation * shape.Offset, axis = rotation * shape.Axis;
                Vector3 a = center + axis * shape.Extent, b = center - axis * shape.Extent;
                // A flat static box supports the complete projected capsule, including its radius.
                // This uses actual collider geometry and works while the patient's contacts are disabled.
                if (!Supported(a, shape.Radius, plan.Support, scale) || !Supported(b, shape.Radius, plan.Support, scale)) return false;
                int count = Physics.OverlapCapsuleNonAlloc(a, b, shape.Radius + 0.01f, overlaps, Physics.AllLayers, QueryTriggerInteraction.Ignore);
                if (count == overlaps.Length) return false;
                for (int hit = 0; hit < count; hit++)
                {
                    var contact = overlaps[hit];
                    if (contact == null) continue;
                    if (!DefaultLayers(contact)) return false;
                    if (rig.Owns(contact) ||
                        Physics.GetIgnoreLayerCollision(shape.Contact.gameObject.layer, contact.gameObject.layer) ||
                        Physics.GetIgnoreCollision(shape.Contact, contact)) continue;
                    return false;
                }
            }
            return true;
        }

        private static bool Supported(Vector3 worldPoint, float radius, BoxCollider support, Vector3 scale)
        {
            Vector3 point = support.transform.InverseTransformPoint(worldPoint) - support.center;
            return Mathf.Abs(point.x) + radius / scale.x <= support.size.x * 0.5f &&
                Mathf.Abs(point.z) + radius / scale.z <= support.size.z * 0.5f;
        }

        private static bool BindingsMatch(Plan plan) => plan != null && ValidSupport(plan.Anchor, plan.Support) &&
            (plan.Anchor.position - plan.AnchorPosition).sqrMagnitude <= 0.0000001f &&
            Mathf.Abs(Quaternion.Dot(plan.Anchor.rotation, plan.AnchorRotation)) >= 0.999999f && plan.Anchor.lossyScale == plan.AnchorScale &&
            (plan.Support.transform.position - plan.SupportPosition).sqrMagnitude <= 0.0000001f &&
            Mathf.Abs(Quaternion.Dot(plan.Support.transform.rotation, plan.SupportRotation)) >= 0.999999f &&
            plan.Support.transform.lossyScale == plan.SupportScale && plan.Support.center == plan.SupportCenter && plan.Support.size == plan.SupportSize;

        private static bool ValidSupport(Transform anchor, BoxCollider support)
        {
            if (anchor == null || !anchor.gameObject.activeInHierarchy || !UnitScale(anchor) || anchor.GetComponentInParent<Rigidbody>() != null ||
                anchor.GetComponentInParent<ArticulationBody>() != null ||
                !Finite(anchor.position) || !WorkerBodyRig.ValidMedicalRotation(anchor.rotation) || Vector3.Dot(anchor.up, Vector3.up) < 0.99999f ||
                support == null || !support.enabled || support.isTrigger || !support.gameObject.activeInHierarchy ||
                !DefaultLayers(support) ||
                support.GetComponentInParent<Rigidbody>() != null || support.GetComponentInParent<ArticulationBody>() != null || !Finite(support.transform.position) ||
                !WorkerBodyRig.ValidMedicalRotation(support.transform.rotation) || !Finite(support.center) || !Finite(support.size) ||
                support.size.x <= 0 || support.size.y <= 0 || support.size.z <= 0 || Vector3.Dot(support.transform.up, Vector3.up) < 0.99999f) return false;
            Vector3 scale = support.transform.lossyScale;
            if (!Finite(scale) || scale.x <= 0 || scale.y <= 0 || scale.z <= 0) return false;
            Vector3 x = support.transform.TransformVector(Vector3.right).normalized;
            Vector3 y = support.transform.TransformVector(Vector3.up).normalized;
            Vector3 z = support.transform.TransformVector(Vector3.forward).normalized;
            return Mathf.Abs(Vector3.Dot(x, y)) < 0.0001f && Mathf.Abs(Vector3.Dot(x, z)) < 0.0001f &&
                Mathf.Abs(Vector3.Dot(y, z)) < 0.0001f && Mathf.Abs(SupportTop(support).y - anchor.position.y) <= 0.005f;
        }

        private static Vector3 SupportTop(BoxCollider support) => support.transform.TransformPoint(support.center + Vector3.up * support.size.y * 0.5f);
        // This bounded fixture does not implement Unity's per-collider/body override-priority rules.
        // Reject overrides before treating a support as colliding or discarding an observed obstacle.
        private static bool DefaultLayers(Collider contact)
        {
            if (contact.GetComponentInParent<ArticulationBody>() != null || contact.includeLayers.value != 0 || contact.excludeLayers.value != 0) return false;
            var owner = contact.GetComponentInParent<Rigidbody>();
            // Disabled chamber contacts may temporarily lack a native attachment. The explicit
            // hierarchy owner still controls their masks when discharge re-enables collision.
            return (contact.attachedRigidbody == null || contact.attachedRigidbody == owner) && (owner == null || DefaultBodyLayers(owner));
        }
        private static bool DefaultBodyLayers(Rigidbody body) => body.includeLayers.value == 0 && body.excludeLayers.value == 0;
        private static bool UnitScale(Transform value) => Finite(value.lossyScale) && (value.lossyScale - Vector3.one).sqrMagnitude <= 0.0001f;
        private static bool Finite(Vector3 value) => WorkerBodyRig.ValidMedicalVector(value);
        private static bool Finite(float value) => !float.IsNaN(value) && !float.IsInfinity(value);

        public void Clear()
        {
            staged = held = null;
            if (rig != null) rig.Freeze();
            rig = null; shapes = null; Array.Clear(overlaps, 0, overlaps.Length);
        }
    }
}
