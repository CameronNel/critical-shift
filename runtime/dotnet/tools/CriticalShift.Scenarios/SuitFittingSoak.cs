using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only input-driven ledger. Only an accepted attempt's opaque identity comes from owner output.</summary>
    internal static class SuitFittingSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        {
            internal bool Allowed = true;
            public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => Allowed ? AccessDecision.Allowed : AccessDecision.OutOfReach;
        }
        private sealed class Worker
        {
            internal WorkerSuit Suit, Original;
            internal int Load, Station;
            internal long Revision, Start, Due, ContactSequence, NextContact;
            internal bool Pending;
            internal Guid Attempt;
        }
        internal static int Exercise(Random random, bool omitFirstProtection)
        {
            long duration = random.Next(15000, 30001), deadline = duration * 3 + random.Next(1, 5001);
            var access = new Access(); WorldSession? world = null; int steps = 0;
            for (int lifetime = 0; lifetime < 2; lifetime++)
            {
                var previous = world?.Epoch ?? Guid.Empty;
                world = world == null ? new WorldSession(new WorldSessionConfiguration(42, deadline, true), access, traceCapacity: 8) : world.Restart(access);
                var ports = new LocalCommandPort[2]; var workers = new[] { new Worker(), new Worker() };
                var attemptIds = new HashSet<Guid>();
                for (int i = 0; i < 2; i++)
                {
                    world.RegisterConnection(Id(800 + i), Id(810 + i)); ports[i] = new LocalCommandPort(world, Id(800 + i));
                    world.SuitFitting.Register(Id(820 + i), new SuitFittingDefinition(duration));
                }
                world.RegisterWorkerContaminationSource(Id(830), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20, 1));
                world.RegisterObject(Id(840));
                access.Allowed = true; world.Start(); long host = 0, shift = 0;
                long starts = 0, completed = 0, cancelled = 0, interrupted = 0; bool paused = false, terminal = false, omitted = false;
                if (previous != Guid.Empty)
                {
                    var stale = new InteractionCommand(previous, 1, InteractionKind.SuitFitting, Id(820),
                        suitFitting: new SuitFittingRequest(SuitFittingAction.Cancel, attempt: Id(999)));
                    Require(world.ExecuteInteraction(Id(800), stale).Status == InteractionStatus.WrongEpoch, "Old fitting epoch reached a successor owner.");
                }
                void Check()
                {
                    Require(world.View.ElapsedMilliseconds == shift, "Fitting process clock differs from independent host/pause ledger.");
                    var summary = world.SuitFitting.Summary; int pending = terminal ? 0 : workers.Count(w => w.Pending);
                    Require(summary.Started == starts && summary.Completed == completed && summary.Cancelled == cancelled &&
                        summary.Interrupted == interrupted && summary.Pending == pending && !summary.CountersSaturated && starts == completed + cancelled + interrupted + pending,
                        "Fitting counters differ from independent attempt ledger.");
                    for (int i = 0; i < 2; i++)
                    {
                        var expected = workers[i]; var actual = terminal ? world.Debrief!.WorkersAtEnd.Single(w => w.Id == Id(810 + i)) : world.GetWorker(Id(810 + i))!;
                        Require(actual.Suit == expected.Suit, "Suit protection differs from independent fitting ledger.");
                        Require(actual.Contamination == expected.Load && actual.Revision == expected.Revision,
                            "Fitting changed contamination or revision outside the independent transition model.");
                        Require(actual.CanInteract == !expected.Pending && actual.PhysicallyUpright && actual.Awareness == WorkerAwareness.Alert &&
                            actual.Pose == WorkerPose.Upright && actual.LastCauseId == Guid.Empty && actual.LastHazardId == Guid.Empty && actual.RecoveryEpisode == 0,
                            "Fitting changed injury/recovery facts or failed to gate incompatible work.");
                        Require((actual.SuitFitting != null) == expected.Pending, "Fitting attempt presence differs from independent ledger.");
                        if (expected.Pending)
                            Require(actual.SuitFitting!.Id == expected.Attempt && actual.SuitFitting.StationId == Id(820 + expected.Station) &&
                                actual.SuitFitting.StartedAtMilliseconds == expected.Start && actual.SuitFitting.DueAtMilliseconds == expected.Due &&
                                actual.SuitFitting.OriginalSuit == expected.Original, "Fitting identity, full duration or original protection drifted.");
                    }
                    Require(world.View.ActiveClaimCount == 0, "Suit fitting invented object custody.");
                    if (terminal) Require(world.WorkerCount == 0 && world.SuitFitting.StationCount == 0, "Suit fitting leaked terminal resources.");
                    steps++;
                }
                void Start(int who, int station)
                {
                    var worker = workers[who]; SuitFittingStatus? typed = null; InteractionStatus expected;
                    if (paused || worker.Pending) expected = InteractionStatus.ActorUnavailable;
                    else if (!access.Allowed) expected = InteractionStatus.OutOfReach;
                    else
                    {
                        typed = worker.Suit == WorkerSuit.Intact ? SuitFittingStatus.NoChange :
                            workers.Any(w => w.Pending && w.Station == station) ? SuitFittingStatus.StationOccupied : SuitFittingStatus.Applied;
                        expected = typed == SuitFittingStatus.Applied ? InteractionStatus.Applied :
                            typed == SuitFittingStatus.NoChange ? InteractionStatus.NoChange : InteractionStatus.SuitFittingRejected;
                    }
                    var reply = ports[who].OperateSuitFitting(Id(820 + station), SuitFittingAction.Start);
                    Require(reply.Status == expected && reply.SuitFitting?.Status == typed, "Fitting start admission differs from independent busy/access/occupancy model.");
                    Require(reply.HasNewCommit == (typed == SuitFittingStatus.Applied), "Fitting start committed despite denial or omitted an accepted mutation.");
                    if (typed == SuitFittingStatus.Applied)
                    {
                        var change = reply.SuitFitting!.Change; var attempt = change?.Attempt;
                        Require(change?.Kind == SuitFittingEvent.Started && change.ShiftMilliseconds == shift &&
                            change.PreviousWorkerRevision == worker.Revision && change.Worker.Id == Id(810 + who) &&
                            change.Worker.Revision == worker.Revision + 1 && change.Worker.Suit == worker.Suit && change.Worker.Contamination == worker.Load &&
                            !change.Worker.CanInteract && attempt?.StationId == Id(820 + station) && attempt.StartedAtMilliseconds == shift &&
                            attempt.DueAtMilliseconds == shift + duration && attempt.OriginalSuit == worker.Suit &&
                            change.Worker.SuitFitting?.Id == attempt.Id, "Fitting Started event differs from independently predicted inputs.");
                        Require(attempt!.Id != Guid.Empty && attemptIds.Add(attempt.Id), "A new fitting reused an old attempt identity.");
                        worker.Pending = true; worker.Attempt = attempt.Id; worker.Start = shift; worker.Due = shift + duration;
                        worker.Station = station; worker.Original = worker.Suit; worker.Revision++; starts++;
                    }
                    Check();
                }
                void Cancel(int who)
                {
                    var worker = workers[who]; if (!worker.Pending) return;
                    var attempt = worker.Attempt; long revision = worker.Revision;
                    var reply = ports[who].OperateSuitFitting(Id(820 + worker.Station), SuitFittingAction.Cancel);
                    Require(reply.HasNewCommit && reply.SuitFitting?.Change?.Kind == SuitFittingEvent.Cancelled &&
                        reply.SuitFitting.Change.Attempt.Id == attempt && reply.SuitFitting.Change.PreviousWorkerRevision == revision,
                        "Own fitting cancellation lost exact identity, revision or busy/paused escape path.");
                    worker.Pending = false; worker.Revision++; cancelled++; Check();
                }
                void Advance(long delta)
                {
                    host += delta; long target = paused ? shift : Math.Min(deadline, shift + delta);
                    var expected = new List<(int Who, SuitFittingEvent Kind, long At, Guid Attempt, long Previous)>();
                    for (int i = 0; i < 2; i++)
                    {
                        var worker = workers[i]; if (!worker.Pending) continue;
                        if (!access.Allowed || worker.Due <= target)
                        {
                            bool finish = access.Allowed;
                            expected.Add((i, finish ? SuitFittingEvent.Completed : SuitFittingEvent.Interrupted,
                                finish ? worker.Due : target, worker.Attempt, worker.Revision));
                            worker.Pending = false; worker.Revision++;
                            if (finish)
                            {
                                completed++;
                                if (omitFirstProtection && lifetime == 0 && !omitted) omitted = true;
                                else worker.Suit = WorkerSuit.Intact;
                            }
                            else interrupted++;
                        }
                    }
                    shift = target;
                    if (shift == deadline) { cancelled += workers.Count(w => w.Pending); terminal = true; }
                    var result = world.AdvanceTo(host);
                    Require(result.SuitFittingChanges.Count == expected.Count, "Fitting poll omitted or invented an independently predicted transition.");
                    foreach (var row in expected)
                    {
                        var actual = result.SuitFittingChanges.Single(c => c.Worker.Id == Id(810 + row.Who));
                        Require(actual.Kind == row.Kind && actual.ShiftMilliseconds == row.At && actual.Attempt.Id == row.Attempt &&
                            actual.PreviousWorkerRevision == row.Previous && actual.Worker.Revision == row.Previous + 1,
                            "Fitting settlement lost exact completion/current observation time, attempt or revisions.");
                    }
                    Check();
                }
                void Environment(int who, WorkerSuit suit, int load)
                {
                    var worker = workers[who]; bool changed = worker.Suit != suit || worker.Load != load;
                    var expected = paused ? WorkerStatus.Paused : changed ? WorkerStatus.Applied : WorkerStatus.Duplicate;
                    var reply = world.SetWorkerEnvironment(world.Epoch, Id(810 + who), worker.Revision, suit, load);
                    Require(reply.Status == expected, "Fitting environment admission differs from independent condition model.");
                    if (expected == WorkerStatus.Applied)
                    {
                        if (worker.Pending && suit != worker.Suit) { worker.Pending = false; interrupted++; }
                        worker.Suit = suit; worker.Load = load; worker.Revision++;
                    }
                    Check();
                }
                void Contact(int who)
                {
                    var worker = workers[who]; int percent = worker.Suit == WorkerSuit.Intact ? 25 : worker.Suit == WorkerSuit.Compromised ? 50 : 100;
                    bool cooling = worker.ContactSequence > 0 && shift < worker.NextContact;
                    int load = (int)Math.Ceiling(20m * percent / 100m), after = Math.Min(100, worker.Load + load);
                    var expected = paused ? WorkerStatus.Paused : cooling ? WorkerStatus.CoolingDown : after == worker.Load ? WorkerStatus.NoChange : WorkerStatus.Applied;
                    var reply = world.ObserveWorkerContamination(world.Epoch, Id(810 + who), Id(830), worker.ContactSequence + 1, Guid.NewGuid(), shift);
                    Require(reply.Status == expected, "Fitting granted early protection or changed canonical contact admission.");
                    if (!paused)
                    {
                        worker.ContactSequence++; if (!cooling) worker.NextContact = shift + 1;
                        if (expected == WorkerStatus.Applied) { worker.Load = after; worker.Revision++; }
                    }
                    Check();
                }
                if (lifetime == 1) Environment(0, WorkerSuit.Compromised, 7);
                Contact(0); Start(0, 0);
                Require(ports[0].Grab(Id(840)).Status == InteractionStatus.ActorUnavailable && world.GetObject(Id(840))!.Revision == 0,
                    "Busy fitting accepted a grab or changed target custody."); Check();
                Advance(duration - 1); Contact(0); Advance(1); Advance(1); Contact(0); Start(0, 0);
                Require(ports[0].Grab(Id(840)).HasNewCommit && ports[0].Release(Id(840)).HasNewCommit,
                    "Completed fitting did not restore ordinary work admission."); Check();
                Environment(0, WorkerSuit.None, workers[0].Load); Start(0, 0); Start(1, 1);
                world.Pause(world.Epoch); paused = true; Advance(random.Next(1, 10001)); access.Allowed = false; Cancel(0);
                world.Resume(world.Epoch); paused = false; access.Allowed = true;
                Environment(1, WorkerSuit.Compromised, random.Next(101));
                for (int operation = 0; operation < 96 && !terminal; operation++)
                {
                    int who = random.Next(2);
                    switch (random.Next(8))
                    {
                        case 0: Start(who, random.Next(2)); break;
                        case 1: Cancel(who); break;
                        case 2: Advance(random.Next(1, 10001)); break;
                        case 3: access.Allowed = random.Next(3) != 0; Check(); break;
                        case 4: Environment(who, (WorkerSuit)random.Next(3), random.Next(101)); break;
                        case 5: Contact(who); break;
                        case 6:
                            if (paused) world.Resume(world.Epoch); else world.Pause(world.Epoch);
                            paused = !paused; Check(); break;
                        case 7:
                            if (ports[who].CanReplayLast)
                            {
                                long revision = world.View.Revision; var reply = ports[who].ReplayLast();
                                Require(reply.IsReplay && !reply.HasNewCommit && world.View.Revision == revision, "Historical fitting receipt repeated its mutation."); Check();
                            }
                            break;
                    }
                }
                if (!terminal)
                {
                    if (paused) { world.Resume(world.Epoch); paused = false; }
                    access.Allowed = true; Advance(deadline);
                }
                var frozen = world.Debrief; world.Stop(); world.AdvanceTo(host + 1); world.Stop();
                Require(ReferenceEquals(world.Debrief, frozen), "Fitting terminal evidence was rewritten by later polling or stop."); Check();
            }
            return steps;
        }
    }
}
