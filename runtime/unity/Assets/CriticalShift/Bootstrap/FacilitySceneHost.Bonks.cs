using System;
using CriticalShift.Application;
using CriticalShift.FacilityPhysics.Unity;
using CriticalShift.Unity.Shared;
using UnityEngine;

namespace CriticalShift.Bootstrap
{
    public sealed partial class FacilitySceneHost
    {
        private readonly BonkHitQuery bonkQuery = new BonkHitQuery();
        public override bool BeginBonk(WorkerScenePort worker, out string reason)
        {
            if (executing) { reason = "An interaction is already being committed."; return false; }
            executing = true;
            try { return BeginBonkBound(worker, out reason); }
            catch { Shutdown(); throw; }
            finally { executing = false; }
        }
        private bool BeginBonkBound(WorkerScenePort worker, out string reason)
        {
            reason = "Hold a bonk shovel and finish your current action first.";
            if (!CanAct(worker) || !actors[worker.Id].BonkReady || !(Held(worker) is CarryableObject item) || item.Holder != worker ||
                item.Kind != CarryableKind.Shovel || !(item.GetComponent<BonkShovel>() is BonkShovel shovel) || !shovel.Ready || item.Body.isKinematic) return false;
            var claim = world.GetObject(item.Id); if (claim?.HolderId != worker.Id || claim.LeaseGeneration != item.Generation) return false;
            var reply = Command(worker, item.Id, InteractionKind.Bonk, lease: item.Generation);
            reason = reply.Status == InteractionStatus.AttackCoolingDown ? "Shovel is recovering from the last swing." : reply.Status.ToString();
            if (!reply.HasNewCommit) return false;
            if (!shovel.BeginMotion(worker)) { reason = "Shovel animation binding failed."; world.CancelWorkerBonk(world.Epoch, worker.Id, reply.Bonk.Sequence); return false; }
            return true;
        }
        public override float BonkPhase(WorkerScenePort worker)
        {
            if (!Running || worker == null) return -1;
            var attack = world.GetWorkerBonk(worker.Id);
            return attack == null ? -1 : Mathf.Clamp01((world.View.ElapsedMilliseconds - attack.StartedMilliseconds) / (float)BonkView.DurationMilliseconds);
        }
        public override BonkSwingPose BonkPose(WorkerScenePort worker)
        {
            float phase = Mathf.Max(0, BonkPhase(worker));
            var shovel = Held(worker) is CarryableObject item ? item.GetComponent<BonkShovel>() : null;
            return shovel != null ? shovel.Pose(phase) : BonkSwingPose.Sample(phase);
        }
        public override void CancelBonk(WorkerScenePort worker)
        {
            if (worker == null || world == null) return;
            var attack = world.GetWorkerBonk(worker.Id);
            if (attack != null) world.CancelWorkerBonk(world.Epoch, worker.Id, attack.Sequence);
            if (Held(worker) is CarryableObject item) item.GetComponent<BonkShovel>()?.EndMotion();
        }
        private void TickBonks()
        {
            foreach (var actor in actors.Values)
            {
                var attack = world.GetWorkerBonk(actor.Id);
                if (attack == null || attack.ContactConsumed || !entities.TryGetValue(attack.Tool, out var target) || target == null || !target.isActiveAndEnabled ||
                    !(target.GetComponent<BonkShovel>() is BonkShovel shovel) || !shovel.Animating) continue;
                long elapsed = world.View.ElapsedMilliseconds - attack.StartedMilliseconds;
                if (elapsed < BonkView.WindupMilliseconds || elapsed > BonkView.StrikeEndMilliseconds) continue;
                float strike = (elapsed - BonkView.WindupMilliseconds) / (float)(BonkView.StrikeEndMilliseconds - BonkView.WindupMilliseconds);
                int steps = Mathf.Clamp(Mathf.CeilToInt((strike - shovel.LastStrike) * 8), 1, 8);
                for (int i = 1; i <= steps; i++)
                {
                    float a = Mathf.Lerp(shovel.LastStrike, strike, (i - 1) / (float)steps), b = Mathf.Lerp(shovel.LastStrike, strike, i / (float)steps);
                    Vector3 from = Blade(actor.Eye.position, shovel.Aim, a), to = Blade(actor.Eye.position, shovel.Aim, b);
                    bool hit = bonkQuery.TryContact(actor, target, actor.Eye.position, from, to, .16f, obstructionMask, out var contact, out bool complete);
                    if (!complete) { world.BlockWorkerBonk(world.Epoch, actor.Id, attack.Sequence); break; }
                    if (!hit) continue;
                    var victim = contact.Shape.GetComponentInParent<WorkerScenePort>();
                    if (victim != null && actors.TryGetValue(victim.Id, out var bound) && bound == victim && victim.isActiveAndEnabled && victim != actor)
                    {
                        var reply = world.ApplyWorkerBonkContact(world.Epoch, actor.Id, attack.Sequence, victim.Id);
                        if (reply.Changed)
                        {
                            Vector3 impulse = (shovel.Aim * Vector3.forward * 2.8f + Vector3.up * .35f) * bound.PhysicalMass;
                            bound.KnockDown(impulse, contact.Position); SynchronizeBindings(); shovel.PlayImpact(contact.Position);
                        }
                    }
                    else if (world.BlockWorkerBonk(world.Epoch, actor.Id, attack.Sequence)) shovel.PlayImpact(contact.Position);
                    break;
                }
                shovel.LastStrike = strike;
            }
        }
        private static Vector3 Blade(Vector3 eye, Quaternion aim, float strike) => eye + aim *
            new Vector3(Mathf.Lerp(-.22f, .22f, strike), Mathf.Lerp(.22f, -.35f, strike), Mathf.Lerp(.95f, 1.4f, strike));
    }
}
