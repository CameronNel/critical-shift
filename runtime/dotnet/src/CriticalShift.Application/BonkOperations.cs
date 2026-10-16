using System;
using System.Collections.Generic;

namespace CriticalShift.Application
{
    // One bounded per-worker action history; custody and health stay with their existing owners.
    internal sealed class BonkOperations
    {
        internal const long Windup = BonkView.WindupMilliseconds, StrikeEnd = BonkView.StrikeEndMilliseconds, Duration = BonkView.DurationMilliseconds, Cooldown = BonkView.CooldownMilliseconds, RecoveryDelay = 2000;
        private readonly WorldSession world;
        private readonly HashSet<Guid> tools = new HashSet<Guid>();
        private readonly Dictionary<Guid, BonkView> attacks = new Dictionary<Guid, BonkView>();
        private readonly Dictionary<(Guid Target, Guid Tool), long> observations = new Dictionary<(Guid, Guid), long>();
        internal BonkOperations(WorldSession world) { this.world = world; }
        internal void Register(Guid tool) { tools.Add(tool); }
        internal InteractionReply Begin(Guid actor, Guid tool, long lease)
        {
            if (!tools.Contains(tool)) return new InteractionReply(InteractionStatus.TargetUnavailable, true);
            var claim = world.GetObject(tool);
            if (claim == null || claim.HolderId != actor) return new InteractionReply(InteractionStatus.NotHolder, true);
            if (claim.LeaseGeneration != lease) return new InteractionReply(InteractionStatus.StaleLease, true);
            if (world.GetWorker(actor)?.CanInteract != true) return new InteractionReply(InteractionStatus.ActorUnavailable, true);
            attacks.TryGetValue(actor, out var previous); long now = world.View.ElapsedMilliseconds;
            if (previous != null && now - previous.StartedMilliseconds < Cooldown)
                return new InteractionReply(InteractionStatus.AttackCoolingDown, true);
            var attack = new BonkView(actor, tool, checked((previous?.Sequence ?? 0) + 1), lease, now, Guid.NewGuid(), false);
            attacks[actor] = attack;
            return new InteractionReply(InteractionStatus.Applied, true, claim, bonk: attack);
        }
        internal BonkView? Get(Guid actor)
        {
            if (!attacks.TryGetValue(actor, out var attack) || attack.Cancelled || world.GetWorker(actor)?.CanInteract != true ||
                world.View.ElapsedMilliseconds - attack.StartedMilliseconds >= Duration) return null;
            var claim = world.GetObject(attack.Tool);
            return claim?.HolderId == actor && claim.LeaseGeneration == attack.LeaseGeneration ? attack : null;
        }
        internal bool CanContact(Guid actor, long sequence, out BonkView? attack)
        {
            attack = Get(actor); long elapsed = attack != null ? world.View.ElapsedMilliseconds - attack.StartedMilliseconds : -1;
            return attack != null && attack.Sequence == sequence && !attack.ContactConsumed && elapsed >= Windup && elapsed <= StrikeEnd;
        }
        internal long NextObservation(Guid target, Guid tool)
        { observations.TryGetValue((target, tool), out long before); return checked(before + 1); }
        internal void Consume(BonkView attack, Guid? target = null, long observation = 0)
        {
            attacks[attack.Actor] = new BonkView(attack.Actor, attack.Tool, attack.Sequence, attack.LeaseGeneration,
                attack.StartedMilliseconds, attack.Cause, true);
            if (target.HasValue) observations[(target.Value, attack.Tool)] = observation;
        }
        internal bool Cancel(Guid actor, long sequence)
        {
            if (!attacks.TryGetValue(actor, out var attack) || attack.Sequence != sequence || attack.Cancelled) return false;
            attacks[actor] = new BonkView(actor, attack.Tool, attack.Sequence, attack.LeaseGeneration, attack.StartedMilliseconds, attack.Cause, true, true); return true;
        }
        internal void CancelAll()
        { foreach (var actor in new List<Guid>(attacks.Keys)) Cancel(actor, attacks[actor].Sequence); }
        internal void Remove(Guid actor) { attacks.Remove(actor); }
        internal void Clear() { attacks.Clear(); observations.Clear(); tools.Clear(); }
    }
}
