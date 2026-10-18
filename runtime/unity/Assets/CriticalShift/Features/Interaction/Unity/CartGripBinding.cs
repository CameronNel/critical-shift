using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Cart-handle geometry and proximity only. The claim store owns its holder; CartMotor owns cart forces.</summary>
    internal sealed class CartGripBinding
    {
        internal readonly Guid Id;
        internal readonly Rigidbody Body;
        internal readonly Transform Handle, Stand;
        private readonly Collider[] shapes;
        internal bool Available
        {
            get
            {
                if (Body == null || Body.isKinematic || !Body.detectCollisions || !Body.gameObject.activeInHierarchy ||
                    Handle == null || !Handle.gameObject.activeInHierarchy || Stand == null || !Stand.gameObject.activeInHierarchy ||
                    !Handle.IsChildOf(Body.transform) || !Stand.IsChildOf(Body.transform)) return false;
                foreach (var shape in shapes)
                    if (shape == null || !shape.enabled || !shape.gameObject.activeInHierarchy || shape.isTrigger || shape.attachedRigidbody != Body)
                        return false;
                return true;
            }
        }

        internal CartGripBinding(Guid id, Rigidbody body, Transform handle, Transform stand)
        {
            if (id == Guid.Empty || body == null || body.isKinematic || !body.detectCollisions || handle == null || stand == null ||
                !handle.IsChildOf(body.transform) || !stand.IsChildOf(body.transform))
                throw new ArgumentException("A cart grip needs one dynamic body and its explicit handle/standing anchors.");
            Id = id; Body = body; Handle = handle; Stand = stand;
            var contacts = new List<Collider>();
            foreach (var shape in body.GetComponentsInChildren<Collider>())
            {
                if (shape.isTrigger || !shape.enabled) continue; // Sensors and disabled decorative primitives are not contact geometry.
                if (shape.attachedRigidbody != body) throw new ArgumentException("Cart contact geometry must belong to its one drive body.");
                contacts.Add(shape);
            }
            if (contacts.Count == 0) throw new ArgumentException("A cart grip requires solid cart contact geometry.");
            shapes = contacts.ToArray();
        }

        internal bool CanEnter(Transform actorRoot) => actorRoot != null && actorRoot.gameObject.activeInHierarchy &&
            Available && Body.linearVelocity.magnitude <= 1.5f &&
            Vector3.Distance(actorRoot.position, Stand.position) <= 1.4f;

        internal bool CanMaintain(Transform actorRoot) => actorRoot != null && actorRoot.gameObject.activeInHierarchy &&
            Available &&
            Vector3.Distance(actorRoot.position, Stand.position) <= 2;
    }
}
