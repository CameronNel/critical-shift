using System;
using System.Globalization;
using CriticalShift.Application;
using CriticalShift.Features.Interaction.Unity;
using UnityEngine;

namespace CriticalShift.Sandbox
{
    /// <summary>Opt-in Player evidence driver. All custody intentions still pass through the existing host.</summary>
    internal sealed class SandboxPlayerExercise
    {
        private enum Phase { Settling, Carrying, Released, Completed }
        private const int StageFrames = 35, MaximumFrames = 180;
        private const double MaximumSeconds = 15;
        private readonly WorldSession world;
        private readonly LocalCommandPort commands;
        private readonly LocalWorldHost host;
        private readonly SpatialInteractionAccess access;
        private readonly Guid epoch, actor, nearby, distant;
        private readonly Rigidbody body;
        private readonly Collider contact;
        private readonly Transform target;
        private readonly MaterialView nearbyBatch, distantBatch;
        private readonly float mass;
        private readonly double beganAt;
        private Phase phase;
        private int frames, stageFrames;
        private long lease, releaseRevision, grabSequence;
        private Vector3 carryStart, carryOffset, releaseStart, gravityDirection;
        private float initialDistance, carryDistance, carryProgress, fallDistance;

        internal bool Holding => phase == Phase.Carrying;
        internal bool Completed => phase == Phase.Completed;
        internal string Stage => phase.ToString();

        internal SandboxPlayerExercise(WorldSession session, LocalCommandPort sender, LocalWorldHost commandHost,
            SpatialInteractionAccess spatial, Guid actorId, Guid nearbyId, Guid distantId, Rigidbody nearbyBody, Transform carryTarget)
        {
            world = session; commands = sender; host = commandHost; access = spatial;
            epoch = session.Epoch; actor = actorId; nearby = nearbyId; distant = distantId;
            body = nearbyBody; target = carryTarget;
            contact = body == null ? null : body.GetComponent<Collider>();
            nearbyBatch = world.Production.GetBatch(nearby); distantBatch = world.Production.GetBatch(distant);
            Require(body != null && contact != null && target != null && nearbyBatch != null && distantBatch != null,
                "Exercise needs its explicit composed body, solid contact, carry anchor and immutable material snapshots.");
            mass = body.mass; beganAt = Time.realtimeSinceStartupAsDouble;
            RequireFree(ReadClaim(nearby)); RequireFree(ReadClaim(distant));
            Debug.Log("CS_SANDBOX_EXERCISE_REQUESTED" + Identity() + " nearby=" + nearby.ToString("N") +
                " distant=" + distant.ToString("N") + " max_frames=" + MaximumFrames + " max_seconds=15");
        }

        internal void CheckDeadline()
        {
            if (Completed) return;
            Require(frames < MaximumFrames && Time.realtimeSinceStartupAsDouble - beganAt < MaximumSeconds,
                "Exercise exceeded its bounded fixed-frame or real-time deadline.");
        }

        internal void Step()
        {
            if (Completed) return;
            CheckDeadline(); frames++; stageFrames++;
            Require(world.Epoch == epoch && world.View.Phase == WorldPhase.Running, "Exercise world changed epoch or stopped.");
            Require(body != null && body.gameObject.activeInHierarchy && !body.isKinematic && body.useGravity &&
                body.detectCollisions && contact != null && contact.enabled && !contact.isTrigger &&
                contact.gameObject.activeInHierarchy && contact.attachedRigidbody == body &&
                target != null && target.gameObject.activeInHierarchy && Mathf.Approximately(body.mass, mass),
                "Exercise body lost its original dynamic solid-contact/mass binding or carry anchor.");
            ObserveMaterials();

            if (phase == Phase.Settling)
            {
                RequireFree(ReadClaim(nearby)); RequireFree(ReadClaim(distant));
                if (stageFrames < StageFrames) return;
                Acquire();
            }
            else if (phase == Phase.Carrying)
            {
                var held = ReadClaim(nearby);
                Require(held.HolderId == actor && held.LeaseGeneration == lease && world.View.ActiveClaimCount == 1 &&
                    Mathf.Approximately(host.CarriedPhysicalMass(), mass) && !host.IsBodyFree(body),
                    "The exact current exercise lease or its physical carry projection was lost.");
                if (stageFrames < StageFrames) return;
                carryDistance = Vector3.Distance(target.position, body.worldCenterOfMass);
                carryProgress = Vector3.Dot(body.worldCenterOfMass - carryStart, carryOffset.normalized);
                Require(carryDistance < initialDistance * 0.5f && carryProgress > initialDistance * 0.5f,
                    "Native carry made insufficient progress: initial=" + Number(initialDistance) +
                    " error=" + Number(carryDistance) + " progress=" + Number(carryProgress));
                Debug.Log("CS_SANDBOX_EXERCISE_CARRIED" + Identity() + " entity=" + nearby.ToString("N") +
                    " sequence=" + grabSequence + " lease=" + lease + " revision=" + held.Revision +
                    " initial_m=" + Number(initialDistance) + " remaining_m=" + Number(carryDistance) +
                    " progress_m=" + Number(carryProgress));
                Release(held);
            }
            else
            {
                var released = ReadClaim(nearby); RequireFree(released);
                Require(released.Revision == releaseRevision && released.LeaseGeneration == lease &&
                    world.View.ActiveClaimCount == 0 && host.CarriedPhysicalMass() == 0 && host.IsBodyFree(body),
                    "The released body reacquired custody or retained a physical carry projection.");
                if (stageFrames < StageFrames) return;
                fallDistance = Vector3.Dot(body.worldCenterOfMass - releaseStart, gravityDirection);
                Vector3 extents = contact.bounds.extents;
                float contactRadius = Vector3.Dot(extents, new Vector3(Mathf.Abs(gravityDirection.x),
                    Mathf.Abs(gravityDirection.y), Mathf.Abs(gravityDirection.z)));
                Require(contactRadius > 0 && fallDistance > contactRadius,
                    "Released native body did not fall at least one contact half-extent: fall=" + Number(fallDistance) +
                    " radius=" + Number(contactRadius));
                phase = Phase.Completed;
                Debug.Log("CS_SANDBOX_EXERCISE_COMPLETED" + Identity() + " entity=" + nearby.ToString("N") +
                    " frames=" + frames + " lease=" + lease + " revision=" + releaseRevision +
                    " progress_m=" + Number(carryProgress) + " fall_m=" + Number(fallDistance) + " claims=0");
            }
        }

        private void Acquire()
        {
            Require(access.Evaluate(actor, distant, InteractionKind.Grab) == AccessDecision.OutOfReach &&
                access.Evaluate(actor, nearby, InteractionKind.Grab) == AccessDecision.Allowed,
                "Actual starting spatial bindings do not provide the declared denied/reachable pair.");
            var deniedBefore = ReadClaim(distant);
            long sequence = commands.LastTerminalSequence;
            host.Grab(distant);
            ObserveCommand(sequence, distant, InteractionStatus.OutOfReach, false);
            var deniedAfter = ReadClaim(distant); RequireFree(deniedAfter);
            Require(deniedAfter.Revision == deniedBefore.Revision && deniedAfter.LeaseGeneration == deniedBefore.LeaseGeneration &&
                deniedAfter.ExpiresAtMilliseconds == deniedBefore.ExpiresAtMilliseconds && world.View.ActiveClaimCount == 0,
                "Out-of-reach host command changed custody.");
            ObserveMaterials();
            Debug.Log("CS_SANDBOX_EXERCISE_DENIED" + Identity() + " entity=" + distant.ToString("N") +
                " sequence=" + commands.LastTerminalSequence + " status=OutOfReach claims=0");

            var before = ReadClaim(nearby);
            carryStart = body.worldCenterOfMass; carryOffset = target.position - carryStart; initialDistance = carryOffset.magnitude;
            Require(initialDistance > contact.bounds.size.magnitude, "The native carry must cover more than the original contact diagonal.");
            sequence = commands.LastTerminalSequence;
            host.Grab(nearby);
            var trace = ObserveCommand(sequence, nearby, InteractionStatus.Applied, true);
            var held = ReadClaim(nearby);
            Require(held.HolderId == actor && held.Revision == before.Revision + 1 &&
                held.LeaseGeneration == before.LeaseGeneration + 1 && world.View.ActiveClaimCount == 1 &&
                trace.ClaimRevision == held.Revision && trace.ClaimLeaseGeneration == held.LeaseGeneration,
                "Reachable host grab did not commit exactly one fresh current-world lease.");
            lease = held.LeaseGeneration; grabSequence = commands.LastTerminalSequence;
            ObserveMaterials();
            phase = Phase.Carrying; stageFrames = 0;
        }

        private void Release(ObjectClaimView held)
        {
            releaseStart = body.worldCenterOfMass; gravityDirection = Physics.gravity.normalized;
            Require(gravityDirection.sqrMagnitude > 0.99f, "Released-body evidence needs the existing nonzero fixture gravity.");
            long sequence = commands.LastTerminalSequence;
            host.DropHeld();
            var trace = ObserveCommand(sequence, nearby, InteractionStatus.Applied, true);
            var released = ReadClaim(nearby); RequireFree(released);
            Require(released.Revision == held.Revision + 1 && released.LeaseGeneration == lease && world.View.ActiveClaimCount == 0 &&
                trace.ClaimRevision == released.Revision && trace.ClaimLeaseGeneration == lease,
                "Host drop did not commit release of the same lease and advance its revision once.");
            releaseRevision = released.Revision; phase = Phase.Released; stageFrames = 0;
            ObserveMaterials();
            Debug.Log("CS_SANDBOX_EXERCISE_DROPPED" + Identity() + " entity=" + nearby.ToString("N") +
                " sequence=" + commands.LastTerminalSequence + " lease=" + lease + " revision=" + releaseRevision + " claims=0");
        }

        private SessionTraceRecord ObserveCommand(long previousSequence, Guid entity, InteractionStatus result, bool changed)
        {
            Require(commands.LastTerminalSequence == previousSequence + 1, "Host command did not finalize the next local sequence.");
            SessionTraceRecord observed = null;
            foreach (var record in world.Trace.Records)
            {
                if (record.Kind != SessionTraceKind.Interaction || record.ActorId != actor || record.EntityId != entity ||
                    record.InputSequence != commands.LastTerminalSequence) continue;
                Require(observed == null, "One command produced duplicate interaction trace records."); observed = record;
            }
            Require(observed != null && observed.Epoch == epoch && observed.RequestEpoch == epoch &&
                observed.Phase == WorldPhase.Running && observed.InteractionResult == result && observed.Changed == changed,
                "Typed host command trace is absent or disagrees with the expected epoch/result/commit.");
            return observed;
        }

        private ObjectClaimView ReadClaim(Guid id)
        {
            var claim = world.GetObject(id);
            Require(claim != null && claim.Epoch == epoch && claim.EntityId == id && !claim.IsRetired && !claim.SlotId.HasValue,
                "Exercise lost its explicit unslotted current-world object projection.");
            return claim;
        }

        private static void RequireFree(ObjectClaimView claim) => Require(!claim.HolderId.HasValue, "Expected a free exercise body.");
        private void ObserveMaterials() => Require(SameBatch(nearbyBatch, world.Production.GetBatch(nearby)) &&
            SameBatch(distantBatch, world.Production.GetBatch(distant)), "Interaction changed immutable material data.");
        private static bool SameBatch(MaterialView before, MaterialView after) => after != null && before.Epoch == after.Epoch &&
            before.ContainerId == after.ContainerId && before.BatchId == after.BatchId && before.ParentBatchId == after.ParentBatchId &&
            before.OriginId == after.OriginId && before.CauseId == after.CauseId && before.Kind == after.Kind && before.Units == after.Units &&
            before.Moisture == after.Moisture && before.Contamination == after.Contamination && before.Revision == after.Revision && before.Flags == after.Flags;
        private string Identity() => " build=" + UnityEngine.Application.buildGUID + " epoch=" + epoch.ToString("N");
        private static string Number(float value) => value.ToString("R", CultureInfo.InvariantCulture);
        private static void Require(bool condition, string reason) { if (!condition) throw new InvalidOperationException(reason); }
    }
}
