using System;
using System.Collections.Generic;
using UnityEngine;

namespace CriticalShift.Unity.Shared
{
    // Attachment-owned lifetime. Restore the actual previous policy, including authored ignores.
    public sealed class CollisionIgnoreScope
    {
        private readonly List<Pair> pairs = new List<Pair>();
        private readonly struct Pair
        {
            public readonly Collider A, B;
            public readonly bool Ignored;
            public Pair(Collider a, Collider b) { A = a; B = b; Ignored = Physics.GetIgnoreCollision(a, b); }
        }
        public void Capture(Collider[] own, Collider[] other)
        {
            Restore();
            if (own == null || other == null || own.Length > 64 || other.Length > 64)
                throw new ArgumentException("Collision scopes require at most 64 shapes per participant.");
            foreach (var a in own) foreach (var b in other)
            {
                if (a == null || b == null || a == b) continue;
                bool duplicate = false;
                foreach (var pair in pairs) if (pair.A == a && pair.B == b || pair.A == b && pair.B == a) { duplicate = true; break; }
                if (!duplicate) pairs.Add(new Pair(a, b));
            }
            IgnoreCaptured();
        }
        public void IgnoreCaptured()
        { foreach (var pair in pairs) if (pair.A != null && pair.B != null) Physics.IgnoreCollision(pair.A, pair.B, true); }
        public void Restore(bool release = true)
        {
            foreach (var pair in pairs) if (pair.A != null && pair.B != null) Physics.IgnoreCollision(pair.A, pair.B, pair.Ignored);
            if (release) pairs.Clear();
        }
    }
}
