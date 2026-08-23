using UnityEngine;

namespace CriticalShift.Prototype
{
    /// Runtime-generated low-cost machine tones keep machine state audible without
    /// introducing external audio assets into the proof-of-fun build.
    [RequireComponent(typeof(AudioSource))]
    public sealed class PrototypeMachineAudio : MonoBehaviour
    {
        AudioSource source;
        PrototypeCrusher crusher;
        PrototypeReactorMachine reactor;

        void Awake()
        {
            source = GetComponent<AudioSource>();
            source.playOnAwake = false;
            source.spatialBlend = .75f;
            source.volume = .18f;
            source.maxDistance = 24f;
        }

        public void Bind(PrototypeCrusher target)
        {
            crusher = target;
            crusher.AudioStateChanged += PlayState;
        }

        public void Bind(PrototypeReactorMachine target)
        {
            reactor = target;
            reactor.AudioStateChanged += PlayState;
        }

        void PlayState(MachineAudioState state)
        {
            if (!Application.isPlaying) return;
            if (source == null) source = GetComponent<AudioSource>();
            if (source == null) return;
            float frequency = 180f + (int)state * 45f;
            int samples = 1200;
            const int sampleRate = 12000;
            var data = new float[samples];
            for (int i = 0; i < samples; i++)
            {
                float envelope = 1f - i / (float)samples;
                data[i] = Mathf.Sin(2f * Mathf.PI * frequency * i / sampleRate) * envelope * .35f;
            }
            var clip = AudioClip.Create("Machine " + state, samples, 1, sampleRate, false);
            clip.SetData(data, 0);
            source.PlayOneShot(clip);
            Destroy(clip, 1f);
        }

        void OnDestroy()
        {
            if (crusher != null) crusher.AudioStateChanged -= PlayState;
            if (reactor != null) reactor.AudioStateChanged -= PlayState;
        }
    }
}
