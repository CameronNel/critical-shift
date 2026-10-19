using System;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only raw-load/receipt oracle. No production contamination arithmetic or trace is read.</summary>
    internal static class ContaminationSoak
    {
        private sealed class Receipt
        {
            internal long Sequence, Sample, Next;
            internal Guid Cause;
            internal int Before, After, Effective;
            internal WorkerStatus Outcome;
        }
        private sealed class Worker
        {
            internal int Contamination;
            internal long Revision;
            internal WorkerSuit Suit;
            internal readonly Receipt?[] Receipts = new Receipt?[8];
        }
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => AccessDecision.Allowed; }

        internal static int Exercise(Random random, bool omitFirstExposure)
        {
            var kinds = new WorkerContaminationKind[8]; var amounts = new int[8]; var cooldowns = new long[8];
            for (int i = 0; i < 8; i++)
            { kinds[i] = i == 0 ? WorkerContaminationKind.Exposure : i == 1 ? WorkerContaminationKind.Decontamination :
                    (WorkerContaminationKind)random.Next(2); amounts[i] = i == 0 ? 10 : random.Next(1, 101); cooldowns[i] = random.Next(1, 1001); }
            WorldSession NewWorld(WorldSession? previous = null)
            {
                var result = previous == null ? new WorldSession(new WorldSessionConfiguration(42, 1000000, true), new Access(), traceCapacity: 8) : previous.Restart(new Access());
                for (int i = 0; i < 2; i++) result.RegisterConnection(Id(800 + i), Id(810 + i));
                for (int i = 0; i < 8; i++) result.RegisterWorkerContaminationSource(Id(700 + i), new WorkerContaminationDefinition(kinds[i], amounts[i], cooldowns[i]));
                result.Start(); return result;
            }
            var world = NewWorld(); int steps = 0;
            for (int lifetime = 0; lifetime < 2; lifetime++)
            {
                var workers = new[] { new Worker(), new Worker() }; long host = 0, shift = 0; bool paused = false;
                void Check()
                {
                    Require(world.View.ElapsedMilliseconds == shift, "Contact model process clock diverged.");
                    for (int i = 0; i < 2; i++)
                    {
                        var actual = world.GetWorker(Id(810 + i))!; var expected = workers[i];
                        Require(actual.Contamination == expected.Contamination, "Contact meter differs from independent raw-load ledger.");
                        Require(actual.Revision == expected.Revision && actual.Suit == expected.Suit, "Contact condition revision or PPE differs from independent ledger.");
                        Require(actual.CanInteract && actual.LastCauseId == Guid.Empty && actual.LastHazardId == Guid.Empty && actual.RecoveryEpisode == 0,
                            "Contact unexpectedly changed injury, posture or recovery ownership.");
                    }
                    steps++;
                }
                void Contact(int who, int source, long sequence, Guid cause, long sample, bool omit = false)
                {
                    var worker = workers[who]; var previous = worker.Receipts[source]; long last = previous?.Sequence ?? 0;
                    WorkerStatus status; Receipt? receipt = null;
                    if (paused) status = WorkerStatus.Paused;
                    else if (sequence < 1 || sample < 0) status = WorkerStatus.InvalidInput;
                    else if (sequence == last)
                    { status = previous!.Cause == cause && previous.Sample == sample ? WorkerStatus.Duplicate : WorkerStatus.PayloadMismatch; receipt = previous; }
                    else if (sequence < last) status = WorkerStatus.TooOld;
                    else if (sequence != last + 1) status = WorkerStatus.SequenceGap;
                    else if (sample != shift) status = WorkerStatus.StaleObservation;
                    else
                    {
                        bool cooling = previous != null && shift < previous.Next;
                        decimal retainedPercent = worker.Suit == WorkerSuit.Intact ? 25 : worker.Suit == WorkerSuit.Compromised ? 50 : 100;
                        int effective = cooling ? 0 : kinds[source] == WorkerContaminationKind.Decontamination ? amounts[source] :
                            (int)Math.Ceiling(amounts[source] * retainedPercent / 100m);
                        int after = Math.Clamp(worker.Contamination + (kinds[source] == WorkerContaminationKind.Exposure ? effective : -effective), 0, 100);
                        status = cooling ? WorkerStatus.CoolingDown : after == worker.Contamination ? WorkerStatus.NoChange : WorkerStatus.Applied;
                        receipt = new Receipt { Sequence = sequence, Cause = cause, Sample = sample, Before = worker.Contamination,
                            After = after, Effective = effective, Next = cooling ? previous!.Next : shift + cooldowns[source], Outcome = status };
                    }
                    var reply = world.ObserveWorkerContamination(world.Epoch, Id(810 + who), Id(700 + source), sequence, cause, sample);
                    Require(reply.Status == status && reply.Changed == (status == WorkerStatus.Applied), "Contact admission differs from independent identity/cooldown ledger.");
                    if (receipt == null) Require(reply.ContaminationContact == null, "Rejected contact invented an accepted receipt.");
                    else
                    {
                        var actual = reply.ContaminationContact;
                        Require(actual != null && actual.SourceId == Id(700 + source) && actual.CauseId == receipt.Cause && actual.Sequence == receipt.Sequence &&
                            actual.SampleShiftMilliseconds == receipt.Sample && actual.RawUnits == amounts[source] && actual.Kind == kinds[source] &&
                            actual.Before == receipt.Before && actual.After == receipt.After && actual.EffectiveUnits == receipt.Effective &&
                            actual.NextEligibleAtMilliseconds == receipt.Next && actual.OriginalOutcome == receipt.Outcome,
                            "Contact receipt lost original payload, arithmetic, cooldown or historical outcome.");
                        if (!omit && status != WorkerStatus.Duplicate && status != WorkerStatus.PayloadMismatch)
                        {
                            worker.Receipts[source] = receipt; worker.Contamination = receipt.After;
                            if (status == WorkerStatus.Applied) worker.Revision++;
                        }
                    }
                    Check();
                }
                Contact(0, 0, 1, Id(9000), 0, omitFirstExposure && lifetime == 0);
                Contact(0, 1, 1, Id(9001), 0);
                for (int operation = 0; operation < 128; operation++)
                {
                    int who = random.Next(2), source = random.Next(8), choice = random.Next(10); var worker = workers[who];
                    if (choice == 0)
                    {
                        long delta = random.Next(1001); host += delta; if (!paused) shift += delta;
                        world.AdvanceTo(host); Check(); continue;
                    }
                    if (choice == 1)
                    { if (paused) world.Resume(world.Epoch); else world.Pause(world.Epoch); paused = !paused; Check(); continue; }
                    if (choice == 2)
                    {
                        var suit = (WorkerSuit)random.Next(3); var reply = world.SetWorkerEnvironment(world.Epoch, Id(810 + who), worker.Revision, suit, worker.Contamination);
                        var expected = paused ? WorkerStatus.Paused : suit == worker.Suit ? WorkerStatus.Duplicate : WorkerStatus.Applied;
                        Require(reply.Status == expected, "Contact model PPE admission changed unexpectedly.");
                        if (expected == WorkerStatus.Applied) { worker.Suit = suit; worker.Revision++; } Check(); continue;
                    }
                    var last = worker.Receipts[source]; long seq = (last?.Sequence ?? 0) + 1, sample = shift; Guid cause = Id(9100 + operation);
                    if (choice == 3 && last != null) { seq = last.Sequence; cause = last.Cause; sample = last.Sample; }
                    if (choice == 4 && last != null) { seq = last.Sequence; sample = last.Sample; }
                    if (choice == 5) seq++;
                    if (choice == 6 && last != null) seq = last.Sequence - 1;
                    if (choice == 7) sample++;
                    if (choice == 8 && last != null) { seq = last.Sequence; cause = last.Cause; sample = last.Sample + 1; }
                    Contact(who, source, seq, cause, sample);
                }
                var epoch = world.Epoch; world.Stop();
                Require(world.WorkerCount == 0 && world.View.ActiveClaimCount == 0, "Contact model leaked terminal owner state.");
                for (int i = 0; i < 2; i++)
                {
                    var final = world.Debrief!.WorkersAtEnd[i];
                    Require(final.Id == Id(810 + i) && final.Contamination == workers[i].Contamination && final.Suit == workers[i].Suit,
                        "Contact debrief lost canonical terminal condition.");
                }
                if (lifetime == 0)
                {
                    world = NewWorld(world);
                    Require(world.ObserveWorkerContamination(epoch, Id(810), Id(700), 1, Id(9000), 0).Status == WorkerStatus.WrongEpoch,
                        "Old contact epoch changed a successor worker.");
                }
                steps++;
            }
            return steps;
        }
    }
}
