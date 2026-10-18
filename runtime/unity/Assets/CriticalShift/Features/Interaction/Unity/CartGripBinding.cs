using System;
using UnityEngine;

namespace CriticalShift.Features.Interaction.Unity
{
    /// <summary>Cart-handle geometry and proximity only. The claim store owns its holder; CartMotor owns cart forces.</summary>
    internal sealed class CartGripBinding
    {
        internal readonly Guid Id;
        internal readonly Rigidbody Body;
        internal readonly Transform Handle, Stand;

        internal CartGripBinding(Guid id, Rigidbody body, Transform handle, Transform stand)
        {
            if (id == Guid.Empty || body == null || body.isKinematic || handle == null || stand == null ||
                !handle.IsChildOf(body.transform) || !stand.IsChildOf(body.transform))
                throw new ArgumentException("A cart grip needs one dynamic body and its explicit handle/standing anchors.");
            Id = id; Body = body; Handle = handle; Stand = stand;
        }

        internal bool CanEnter(Transform actorRoot) => actorRoot != null && actorRoot.gameObject.activeInHierarchy &&
            Body != null && Body.gameObject.activeInHierarchy && Handle != null && Handle.gameObject.activeInHierarchy &&
            Stand != null && Stand.gameObject.activeInHierarchy && Body.linearVelocity.magnitude <= 1.5f &&
            Vector3.Distance(actorRoot.position, Stand.position) <= 1.4f;

        internal bool CanMaintain(Transform actorRoot) => actorRoot != null && actorRoot.gameObject.activeInHierarchy &&
            Body != null && Body.gameObject.activeInHierarchy && Handle != null && Handle.gameObject.activeInHierarchy &&
            Stand != null && Stand.gameObject.activeInHierarchy &&
            Vector3.Distance(actorRoot.position, Stand.position) <= 2;
    }
}
