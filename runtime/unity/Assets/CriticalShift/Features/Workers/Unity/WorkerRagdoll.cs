using System;
using System.Collections.Generic;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Features.Workers.Unity
{
    public readonly struct RagdollRecoveryPose
    {
        public readonly Vector3 Position;
        public readonly Quaternion Rotation;
        public readonly bool FaceDown;
        public RagdollRecoveryPose(Vector3 position, Quaternion rotation, bool faceDown)
        { Position = position; Rotation = rotation; FaceDown = faceDown; }
    }

    [DisallowMultipleComponent]
    public sealed class WorkerRagdoll : MonoBehaviour
    {
        [SerializeField] private Rigidbody pelvis;
        [SerializeField] private Rigidbody[] bones = Array.Empty<Rigidbody>();
        [SerializeField] private Collider[] colliders = Array.Empty<Collider>();
        [SerializeField] private RagdollTuning tuning = new RagdollTuning();
        [SerializeField] private Vector3 anatomicalForward = Vector3.forward, anatomicalUp = Vector3.up;
        private readonly CollisionIgnoreScope selfIgnores = new CollisionIgnoreScope();
        private readonly RaycastHit[] supportHits = new RaycastHit[64];
        private Vector3[] lastPositions, limbVelocity, limbAngularVelocity, recoveryPositions, worldPositions;
        private Quaternion[] lastRotations, recoveryRotations, worldRotations;
        private int[] parentFirst;
        private CharacterJoint[] structuralJoints;
        private Rigidbody[] connectedBodies;
        private Vector3 lastRootPosition;
        private float blendTime, settledTime;
        private bool sampled, initialized, braced, selfPolicyCaptured;
        private Vector3 crawlDirection;
        public bool Active { get; private set; }
        public bool Faulted { get; private set; }
        public Rigidbody Pelvis => pelvis;
        public Collider[] Colliders => colliders;
        public float TotalMass { get { float mass = 0; foreach (var bone in bones) if (bone != null) mass += bone.mass; return mass; } }
        public bool Owns(Rigidbody body) => body != null && Array.IndexOf(bones, body) >= 0;
        public bool Valid => TryValidate(out _);
        public bool FaceDown => pelvis != null && Vector3.Dot(pelvis.transform.TransformDirection(anatomicalForward), Vector3.down) > 0;
        public bool Settled => Active && settledTime >= tuning.settleSeconds;

        public bool TryValidate(out string reason)
        {
            reason = "";
            try { tuning?.Validate(); } catch (ArgumentException error) { reason = error.Message; return false; }
            if (tuning == null || pelvis == null || bones == null || colliders == null || bones.Length < 1 || bones.Length > 32 || colliders.Length < 1 || colliders.Length > 64)
            { reason = "Assign a pelvis, 1–32 unique bodies and 1–64 limb colliders."; return false; }
            if (GetComponent<Rigidbody>() != null || !Finite(anatomicalForward) || !Finite(anatomicalUp) ||
                anatomicalForward.sqrMagnitude < 0.5f || anatomicalUp.sqrMagnitude < 0.5f || Mathf.Abs(Vector3.Dot(anatomicalForward.normalized, anatomicalUp.normalized)) > 0.1f)
            { reason = "The capsule root must have no Rigidbody; assign perpendicular anatomical pelvis axes."; return false; }
            return WorkerRagdollRigValidation.Validate(transform, pelvis, bones, colliders, out reason);
        }

        private void Awake() { Freeze(); }
        private void Initialize()
        {
            if (initialized) return;
            if (!TryValidate(out var error)) throw new InvalidOperationException(error);
            int count = bones.Length;
            lastPositions = new Vector3[count]; limbVelocity = new Vector3[count]; limbAngularVelocity = new Vector3[count];
            lastRotations = new Quaternion[count]; worldPositions = new Vector3[count]; worldRotations = new Quaternion[count];
            parentFirst = new int[count]; for (int i = 0; i < count; i++) parentFirst[i] = i;
            Array.Sort(parentFirst, (a, b) => Depth(bones[a].transform).CompareTo(Depth(bones[b].transform)));
            structuralJoints = new CharacterJoint[count]; connectedBodies = new Rigidbody[count];
            for (int i = 0; i < count; i++)
            { structuralJoints[i] = bones[i].GetComponent<CharacterJoint>(); connectedBodies[i] = structuralJoints[i] != null ? structuralJoints[i].connectedBody : null; }
            foreach (var body in bones)
            {
                body.useGravity = true; body.linearDamping = tuning.linearDamping; body.angularDamping = tuning.angularDamping;
                body.solverIterations = tuning.solverIterations; body.solverVelocityIterations = tuning.solverVelocityIterations;
                body.maxAngularVelocity = tuning.maximumAngularSpeed; body.interpolation = RigidbodyInterpolation.Interpolate;
            }
            initialized = true;
        }
        private static int Depth(Transform bone) { int depth = 0; while (bone.parent != null) { depth++; bone = bone.parent; } return depth; }

        // Sample after playback. Bone motion relative to the root supplements current motor velocity.
        public void SampleAnimatedPose(float delta)
        {
            if (Active || Faulted || !float.IsFinite(delta) || delta <= 0) return;
            Initialize(); Vector3 rootVelocity = sampled ? (transform.position - lastRootPosition) / delta : Vector3.zero;
            for (int i = 0; i < bones.Length; i++)
            {
                var bone = bones[i].transform;
                limbVelocity[i] = sampled ? Vector3.ClampMagnitude((bone.position - lastPositions[i]) / delta - rootVelocity, tuning.maximumSpeed) : Vector3.zero;
                var rotation = bone.rotation * Quaternion.Inverse(lastRotations[i]); rotation.ToAngleAxis(out float degrees, out Vector3 axis);
                if (degrees > 180) degrees -= 360;
                limbAngularVelocity[i] = sampled && Finite(axis) ? Vector3.ClampMagnitude(axis * degrees * Mathf.Deg2Rad / delta, tuning.maximumAngularSpeed) : Vector3.zero;
                lastPositions[i] = bone.position; lastRotations[i] = bone.rotation;
            }
            lastRootPosition = transform.position; sampled = true;
        }

        public void Activate(Vector3 impulse) => Activate(Vector3.zero, impulse, pelvis != null ? pelvis.worldCenterOfMass : transform.position);
        public void Activate(Vector3 inheritedVelocity, Vector3 impulse, Vector3 contactPoint)
        {
            if (!isActiveAndEnabled) throw new InvalidOperationException("A disabled physics owner cannot activate.");
            if (Faulted) throw new InvalidOperationException("A faulted ragdoll cannot restart; rebuild the scene binding.");
            Initialize();
            if (!Finite(inheritedVelocity) || !Finite(impulse) || !Finite(contactPoint)) throw new ArgumentException("Physical impact values must be finite.");
            foreach (var body in bones) if (!body.gameObject.activeInHierarchy) throw new InvalidOperationException("Every physical limb must be active during simulation.");
            if (Active) { ApplyImpulse(impulse, contactPoint); return; }
            recoveryPositions = null; recoveryRotations = null; settledTime = 0;
            foreach (var shape in colliders) shape.enabled = true;
            for (int i = 0; i < bones.Length; i++)
            {
                var bone = bones[i]; bone.isKinematic = false; bone.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
                bone.linearVelocity = Vector3.ClampMagnitude(inheritedVelocity + (sampled ? limbVelocity[i] : Vector3.zero), tuning.maximumSpeed);
                bone.angularVelocity = sampled ? limbAngularVelocity[i] : Vector3.zero; bone.WakeUp();
            }
            selfIgnores.Restore(release: false);
            if (!tuning.selfCollision)
            {
                if (!selfPolicyCaptured) { selfIgnores.Capture(colliders, colliders); selfPolicyCaptured = true; }
                else selfIgnores.IgnoreCaptured();
            }
            Active = true; sampled = false; ApplyImpulse(impulse, contactPoint);
        }
        public void ApplyImpulse(Vector3 impulse, Vector3 contactPoint)
        {
            if (!Active || !Finite(impulse) || !Finite(contactPoint)) return;
            float mass = TotalMass; impulse = Vector3.ClampMagnitude(impulse, mass * tuning.maximumImpactSpeed);
            foreach (var bone in bones)
            {
                Vector3 lever = Vector3.ClampMagnitude(contactPoint - bone.worldCenterOfMass, 0.25f);
                bone.AddForceAtPosition(impulse * (bone.mass / mass), bone.worldCenterOfMass + lever, ForceMode.Impulse);
            }
            settledTime = 0;
        }
        public void SetConsciousMotion(Vector3 direction, bool brace)
        { crawlDirection = Finite(direction) ? Vector3.ClampMagnitude(Vector3.ProjectOnPlane(direction, Vector3.up), 1) : Vector3.zero; braced = brace; }
        private void FixedUpdate()
        {
            if (!Active) return;
            foreach (var shape in colliders) if (shape == null || !shape.enabled || !shape.gameObject.activeInHierarchy)
            { PhysicsFault("An owned ragdoll shape was removed or disabled."); return; }
            bool quiet = true;
            for (int i = 0; i < bones.Length; i++)
            {
                var bone = bones[i];
                if (bone != pelvis && (structuralJoints[i] == null || structuralJoints[i].connectedBody != connectedBodies[i]))
                { PhysicsFault("The owned limb joint graph changed during simulation."); return; }
                if (bone == null || !bone.gameObject.activeInHierarchy || bone.isKinematic || !Finite(bone.position) || !Finite(bone.linearVelocity) || !Finite(bone.angularVelocity)) { PhysicsFault("Missing body or non-finite ragdoll motion."); return; }
                bone.linearVelocity = Vector3.ClampMagnitude(bone.linearVelocity, tuning.maximumSpeed);
                bone.angularVelocity = Vector3.ClampMagnitude(bone.angularVelocity, tuning.maximumAngularSpeed);
                bone.angularDamping = braced ? Mathf.Max(4, tuning.angularDamping) : tuning.angularDamping;
                quiet &= bone.linearVelocity.sqrMagnitude <= tuning.settleSpeed * tuning.settleSpeed && bone.angularVelocity.sqrMagnitude <= tuning.settleAngularSpeed * tuning.settleAngularSpeed;
            }
            settledTime = quiet ? settledTime + Time.fixedDeltaTime : 0;
            if (!braced && crawlDirection.sqrMagnitude > 0 && TrySupport(~0, 50, out _))
            {
                Vector3 planar = Vector3.ProjectOnPlane(pelvis.linearVelocity, Vector3.up);
                Vector3 acceleration = Vector3.ClampMagnitude((crawlDirection * tuning.crawlSpeed - planar) / Time.fixedDeltaTime, tuning.crawlAcceleration);
                pelvis.AddForce(acceleration * TotalMass, ForceMode.Force);
            }
        }
        private void PhysicsFault(string reason) { Stop(); Faulted = true; Debug.LogError("Ragdoll physics stopped: " + reason, this); }

        public void Freeze()
        {
            selfIgnores.Restore(release: false);
            if (bones != null) foreach (var bone in bones) if (bone != null)
            {
                if (!bone.isKinematic) { bone.linearVelocity = Vector3.zero; bone.angularVelocity = Vector3.zero; }
                bone.collisionDetectionMode = CollisionDetectionMode.Discrete; bone.isKinematic = true;
            }
            if (colliders != null) foreach (var shape in colliders) if (shape != null) shape.enabled = false;
            Active = false; crawlDirection = Vector3.zero; braced = false;
        }
        public void Stop() { Freeze(); recoveryPositions = null; recoveryRotations = null; sampled = false; settledTime = 0; }
        public void BeginRecoveryBlend()
        {
            Initialize(); recoveryPositions = new Vector3[bones.Length]; recoveryRotations = new Quaternion[bones.Length];
            for (int i = 0; i < bones.Length; i++) { recoveryPositions[i] = bones[i].transform.localPosition; recoveryRotations[i] = bones[i].transform.localRotation; }
            blendTime = 0;
        }
        public void BlendToAnimation(float delta)
        {
            if (recoveryPositions == null || Active) return;
            blendTime += delta; float weight = Mathf.Clamp01(blendTime / tuning.blendSeconds);
            for (int i = 0; i < bones.Length; i++)
            {
                var bone = bones[i].transform;
                bone.localPosition = Vector3.Lerp(recoveryPositions[i], bone.localPosition, weight);
                bone.localRotation = Quaternion.Slerp(recoveryRotations[i], bone.localRotation, weight);
            }
            if (weight == 1) { recoveryPositions = null; recoveryRotations = null; }
        }
        public bool TryRecoveryPose(int mask, float maximumSlope, out RagdollRecoveryPose pose)
        {
            pose = default;
            if (!Settled || !TrySupport(mask, maximumSlope, out var hit)) return false;
            Vector3 direction = Vector3.ProjectOnPlane(pelvis.transform.TransformDirection(anatomicalUp), Vector3.up);
            if (!FaceDown) direction = -direction;
            if (direction.sqrMagnitude < 0.01f) direction = Vector3.ProjectOnPlane(transform.forward, Vector3.up);
            pose = new RagdollRecoveryPose(hit.point + Vector3.up * 0.02f, Quaternion.LookRotation(direction), FaceDown); return true;
        }
        private bool TrySupport(int mask, float maximumSlope, out RaycastHit support)
        {
            support = default;
            int count = Physics.RaycastNonAlloc(pelvis.position + Vector3.up * 0.4f, Vector3.down, supportHits, 2.4f, mask, QueryTriggerInteraction.Ignore);
            if (count == supportHits.Length) return false;
            float closest = float.PositiveInfinity;
            for (int i = 0; i < count; i++)
            {
                var hit = supportHits[i];
                if (Array.IndexOf(colliders, hit.collider) >= 0 || hit.collider.transform.IsChildOf(transform) || hit.distance >= closest) continue;
                closest = hit.distance; support = hit;
            }
            return support.collider != null && Vector3.Angle(support.normal, Vector3.up) <= maximumSlope &&
                (support.rigidbody == null || support.rigidbody.GetPointVelocity(support.point).magnitude <= tuning.settleSpeed);
        }
        public void MoveRootPreservingPose(RagdollRecoveryPose pose)
        {
            Initialize();
            for (int i = 0; i < bones.Length; i++) { worldPositions[i] = bones[i].position; worldRotations[i] = bones[i].rotation; }
            transform.SetPositionAndRotation(pose.Position, pose.Rotation);
            foreach (int i in parentFirst) { bones[i].position = worldPositions[i]; bones[i].rotation = worldRotations[i]; }
            Physics.SyncTransforms();
        }
        private static bool Finite(Vector3 value) => float.IsFinite(value.x) && float.IsFinite(value.y) && float.IsFinite(value.z);
        private void OnDisable() { Stop(); }
        private void OnDestroy() { selfIgnores.Restore(); }
    }
}
