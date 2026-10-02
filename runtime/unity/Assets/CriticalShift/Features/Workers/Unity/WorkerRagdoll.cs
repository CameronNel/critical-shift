using UnityEngine;
using System;
using System.Linq;

namespace CriticalShift.Features.Workers.Unity
{
    [DisallowMultipleComponent]
    public sealed class WorkerRagdoll : MonoBehaviour
    {
        [SerializeField] private Rigidbody pelvis;
        [SerializeField] private Rigidbody[] bones = Array.Empty<Rigidbody>();
        [SerializeField] private Collider[] colliders = Array.Empty<Collider>();
        public bool Active { get; private set; }
        private Vector3[] recoveryPositions;
        private Quaternion[] recoveryRotations;
        private float blendTime;
        public bool Valid => pelvis != null && bones.Length > 0 && colliders.Length > 0 && bones.All(b => b != null) && colliders.All(c => c != null);
        public bool FaceDown => pelvis != null && Vector3.Dot(pelvis.transform.forward, Vector3.down) > 0;
        private void Awake() { Freeze(); }
        public void Activate(Vector3 impulse)
        {
            recoveryPositions = null; recoveryRotations = null;
            Active = true;
            foreach (var collider in colliders) collider.enabled = true;
            foreach (var bone in bones) { bone.isKinematic = false; bone.linearVelocity = Vector3.zero; bone.angularVelocity = Vector3.zero; }
            if (pelvis != null) pelvis.AddForce(impulse, ForceMode.Impulse);
        }
        public void Freeze()
        {
            foreach (var bone in bones) if (bone != null) { if (!bone.isKinematic) { bone.linearVelocity = Vector3.zero; bone.angularVelocity = Vector3.zero; } bone.isKinematic = true; }
            foreach (var collider in colliders) if (collider != null) collider.enabled = false;
            Active = false;
        }
        public void BeginRecoveryBlend()
        {
            recoveryPositions = bones.Select(b => b.transform.localPosition).ToArray();
            recoveryRotations = bones.Select(b => b.transform.localRotation).ToArray(); blendTime = 0;
        }
        public void BlendToAnimation(float delta)
        {
            if (recoveryPositions == null || Active) return;
            blendTime += delta; float weight = Mathf.Clamp01(blendTime / 0.15f);
            for (int i = 0; i < bones.Length; i++)
            {
                var bone = bones[i].transform;
                bone.localPosition = Vector3.Lerp(recoveryPositions[i], bone.localPosition, weight);
                bone.localRotation = Quaternion.Slerp(recoveryRotations[i], bone.localRotation, weight);
            }
            if (weight == 1) { recoveryPositions = null; recoveryRotations = null; }
        }
        public void PrepareRoot(Transform root, LayerMask mask)
        {
            // Moving the capsule must not move the currently simulated ragdoll bones with it.
            if (pelvis == null) return;
            var hits = Physics.RaycastAll(pelvis.position + Vector3.up * 0.2f, Vector3.down, 2, mask, QueryTriggerInteraction.Ignore);
            System.Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            RaycastHit hit = default;
            bool found = false;
            foreach (var candidate in hits)
            { if (System.Array.IndexOf(colliders, candidate.collider) < 0) { hit = candidate; found = true; break; } }
            if (!found) return;
            var positions = new Vector3[bones.Length]; var rotations = new Quaternion[bones.Length];
            for (int i = 0; i < bones.Length; i++) { positions[i] = bones[i].position; rotations[i] = bones[i].rotation; }
            Vector3 direction = Vector3.ProjectOnPlane(pelvis.transform.up, Vector3.up);
            root.SetPositionAndRotation(hit.point, direction.sqrMagnitude > 0.01f ? Quaternion.LookRotation(direction) : root.rotation);
            for (int i = 0; i < bones.Length; i++) { bones[i].position = positions[i]; bones[i].rotation = rotations[i]; }
        }
    }
}
