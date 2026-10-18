using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Presentation
{
    /// <summary>Setup checks for this presentation assembly's explicitly moved, non-contacting parts.</summary>
    internal static class MovingVisualBindings
    {
        internal static void Validate(Transform owner, params Transform[][] groups)
        {
            if (owner == null || groups == null) throw new ArgumentException("Moving visuals need an explicit owner.");
            var unique = new HashSet<Transform>();
            foreach (var group in groups)
            {
                if (group == null) throw new ArgumentException("A moving visual group is missing.");
                foreach (var part in group)
                {
                    if (part == null || part == owner || !part.IsChildOf(owner) || !unique.Add(part))
                        throw new ArgumentException("Moving visuals must be unique descendants of their presentation owner.");
                    // Include inactive descendants: enabling a pooled part must not wake a hidden motion body.
                    if (part.GetComponentsInChildren<Rigidbody>(true).Length != 0)
                        throw new ArgumentException("Presentation cannot move physical bodies.");
                    foreach (var collider in part.GetComponentsInChildren<Collider>(true))
                        if (collider.enabled) throw new ArgumentException("Moving visuals must be non-contacting.");
                }
            }
            foreach (var part in unique)
                foreach (var other in unique)
                    if (part != other && part.IsChildOf(other))
                        throw new ArgumentException("Independently moved visuals cannot be nested.");
        }
    }
}
