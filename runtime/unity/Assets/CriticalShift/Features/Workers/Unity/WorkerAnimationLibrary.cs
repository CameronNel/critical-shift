using System;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    [CreateAssetMenu(menuName = "Critical Shift/Worker animation library")]
    public sealed class WorkerAnimationLibrary : ScriptableObject
    {
        [Serializable]
        public struct Binding
        {
            public MovementClip id;
            public AnimationClip clip;
        }

        [SerializeField] private Binding[] clips = Array.Empty<Binding>();

        // Validate and detach the binding table; runtime never mutates the shared asset.
        public AnimationClip[] CreateClipTable()
        {
            var table = new AnimationClip[MovementClipInfo.Count];
            foreach (var binding in clips)
            {
                int index = (int)binding.id;
                var info = MovementClipInfo.For(binding.id);
                if (table[index] != null) throw new InvalidOperationException("Duplicate clip: " + binding.id);
                if (binding.clip == null || binding.clip.legacy || binding.clip.length <= 0)
                    throw new InvalidOperationException("Missing, legacy or empty clip: " + binding.id);
                if (binding.clip.isLooping != info.Loop)
                    throw new InvalidOperationException("Set Loop Time to " + info.Loop + " for " + binding.id);
                table[index] = binding.clip;
            }
            for (int i = 0; i < table.Length; i++)
                if (table[i] == null) throw new InvalidOperationException("Assign clip: " + (MovementClip)i);
            return table;
        }
    }
}
