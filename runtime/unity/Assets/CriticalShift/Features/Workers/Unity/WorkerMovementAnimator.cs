using System;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace CriticalShift.Features.Workers.Unity
{
    [DisallowMultipleComponent]
    public sealed class WorkerMovementAnimator : MonoBehaviour
    {
        [SerializeField] private Animator animator;
        [SerializeField] private WorkerAnimationLibrary library;
        [SerializeField, Min(0)] private float blendSeconds = 0.10f;
        private PlayableGraph graph;
        private AnimationMixerPlayable mixer;
        private AnimationClipPlayable[] players;
        private AnimationClip[] clips;
        private MovementAnimationSelector selector;
        private readonly float[] weights = new float[MovementClipInfo.Count];
        private readonly float[] targets = new float[MovementClipInfo.Count];
        private readonly float[] rates = new float[MovementClipInfo.Count];
        private readonly double[] times = new double[MovementClipInfo.Count];
        private readonly bool[] targeted = new bool[MovementClipInfo.Count];
        private float[] lengths;
        private double stridePhase;
        private ulong playedActionSequence;
        private bool playing, capturedRootMotion, originalRootMotion;
        public bool Ready => graph.IsValid();
        public Transform ModelRoot => animator != null ? animator.transform : null;
        public MovementClip? ActiveAction => selector?.ActiveAction;

        // Inspector references are explicit. Call ApplySample once per visual frame from the motion binding.
        private void OnEnable()
        {
            try
            {
                if (animator == null || library == null)
                    throw new InvalidOperationException("Assign the worker Animator and animation library.");
                if (animator.runtimeAnimatorController != null)
                    throw new InvalidOperationException("Remove the Animator controller; this component owns playback.");
                if (!MovementAnimationSample.Finite(blendSeconds) || blendSeconds < 0)
                    throw new InvalidOperationException("Blend duration must be finite and nonnegative.");
                clips = library.CreateClipTable();
                lengths = new float[clips.Length];
                for (int i = 0; i < clips.Length; i++) lengths[i] = clips[i].length;
                selector = new MovementAnimationSelector(lengths);
                originalRootMotion = animator.applyRootMotion;
                capturedRootMotion = true;
                animator.applyRootMotion = false;
                animator.enabled = false;
                graph = PlayableGraph.Create("Worker movement: " + name);
                graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
                mixer = AnimationMixerPlayable.Create(graph, clips.Length);
                players = new AnimationClipPlayable[clips.Length];
                for (int i = 0; i < clips.Length; i++)
                {
                    players[i] = AnimationClipPlayable.Create(graph, clips[i]);
                    players[i].SetApplyFootIK(false);
                    players[i].SetSpeed(0); // Explicit clocks permit gait phase alignment and exact restarts.
                    graph.Connect(players[i], 0, mixer, i);
                    rates[i] = 1;
                }
                var output = AnimationPlayableOutput.Create(graph, "Worker pose", animator);
                output.SetSourcePlayable(mixer);
            }
            catch (Exception error)
            {
                Debug.LogError("Worker animation setup failed: " + error.Message, this);
                enabled = false;
            }
        }

        public void ApplySample(MovementAnimationSample sample, float deltaTime)
        {
            if (!isActiveAndEnabled || !Ready) throw new InvalidOperationException("Worker animation is not bound.");
            var blend = selector.Step(sample, deltaTime);
            if (blend.Count == 0) { Suspend(); return; }
            Array.Clear(targets, 0, targets.Length);
            for (int j = 0; j < blend.Count; j++)
            {
                var entry = blend[j];
                int i = (int)entry.Clip;
                targets[i] = entry.Weight;
                rates[i] = entry.Rate;
            }
            float smoothing = !playing || blendSeconds == 0 ? 1 : 1 - Mathf.Exp(-deltaTime / blendSeconds);
            float total = 0;
            bool newAction = playedActionSequence != selector.ActionSequence;
            for (int i = 0; i < weights.Length; i++)
            {
                weights[i] = Mathf.Lerp(weights[i], targets[i], smoothing);
                if (weights[i] < 0.0001f && targets[i] == 0) weights[i] = 0;
                total += weights[i];
            }
            stridePhase = (stridePhase + deltaTime * GaitCalibration.Frequency(sample.Speed, weights, lengths, sample.Pose)) % 2;
            for (int i = 0; i < weights.Length; i++)
            {
                var info = MovementClipInfo.For((MovementClip)i);
                bool target = targets[i] > 0;
                bool restart = target && (!targeted[i] || (newAction && selector.ActiveAction == (MovementClip)i));
                if (restart && (!info.Loop || info.Action)) times[i] = 0;
                if (info.Strides > 0) times[i] = (stridePhase % info.Strides) * clips[i].length / info.Strides;
                else
                    times[i] = info.Loop ? (times[i] + deltaTime * rates[i]) % clips[i].length
                        : Math.Min(clips[i].length, times[i] + deltaTime * rates[i]);
                targeted[i] = target;
                players[i].SetTime(times[i]);
            }
            for (int i = 0; i < weights.Length; i++) mixer.SetInputWeight(i, weights[i] / total);
            playedActionSequence = selector.ActionSequence;
            animator.enabled = true;
            graph.Play();
            graph.Evaluate(0);
            playing = true;
        }

        public float Duration(MovementClip clip) => Ready ? clips[(int)clip].length : 0;
        public bool BeginJump(bool allowCoyote = false) => Ready && selector.BeginJump(allowCoyote);
        public void CancelJump() { selector?.CancelJump(); }
        public bool TryPlayAction(MovementClip clip, ulong sequence, MovementClip? resume = null) =>
            isActiveAndEnabled && Ready && selector.TryPlayAction(clip, sequence, resume);

        // Physics/cabinet owners prime selection without evaluating a standing pose over a frozen body.
        public bool PrimeGroundedAction(MovementClip clip, ulong sequence)
        {
            if (!isActiveAndEnabled || !Ready) return false;
            selector.Step(new MovementAnimationSample(0, 0, 0, true), 0);
            if (!selector.TryPlayAction(clip, sequence)) return false;
            Array.Clear(weights, 0, weights.Length); Array.Clear(targeted, 0, targeted.Length);
            playing = false;
            return true;
        }

        public bool StopAction(ulong sequence) => Ready && selector.StopAction(sequence);
        public void SuspendPlayback() { if (Ready) { selector.Step(default, 0); Suspend(); } }

        private void Suspend()
        {
            graph.Stop();
            animator.enabled = false;
            playing = false;
            stridePhase = 0;
            Array.Clear(weights, 0, weights.Length);
            Array.Clear(times, 0, times.Length);
            Array.Clear(targeted, 0, targeted.Length);
        }

        private void OnDisable()
        {
            if (graph.IsValid()) graph.Destroy();
            if (animator != null && capturedRootMotion)
            {
                animator.enabled = false;
                animator.applyRootMotion = originalRootMotion;
            }
            selector?.Reset();
            capturedRootMotion = playing = false;
            playedActionSequence = 0;
            stridePhase = 0;
            Array.Clear(weights, 0, weights.Length);
            Array.Clear(times, 0, times.Length);
            Array.Clear(targeted, 0, targeted.Length);
        }
    }
}
