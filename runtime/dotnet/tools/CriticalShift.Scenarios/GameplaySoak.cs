using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;

namespace CriticalShift.Scenarios
{
    /// <summary>Tool-only compositional endurance probes through the actual public gameplay ports.</summary>
    internal static class GameplaySoak
    {
        internal static int Run(string[] args)
        {
            string? report = null, control = null; int seed = 20261018, seconds = 0, cases = 0; int? onlySeed = null;
            try
            {
                var seen = new HashSet<string>();
                for (int i = 0; i < args.Length; i++)
                {
                    string option = args[i];
                    if (!seen.Add(option) || ++i >= args.Length) throw new ArgumentException("Unique options need a value.");
                    string value = args[i];
                    switch (option)
                    {
                        case "--report": report = value; break;
                        case "--seed": seed = int.Parse(value); break;
                        case "--seconds": seconds = int.Parse(value); break;
                        case "--cases": cases = int.Parse(value); break;
                        case "--case-seed": onlySeed = int.Parse(value); break;
                        case "--control":
                            if (value != "failure" && value != "medical-ledger" && value != "contamination-ledger" && value != "backup-ledger" && value != "fitting-ledger" && value != "feed-ledger" && value != "repair-ledger") throw new ArgumentException("Unknown control.");
                            control = value; break;
                        default: throw new ArgumentException("Unknown soak option.");
                    }
                }
                if (report == null || seconds < 0 || seconds > 86400 || cases < 0 || cases > 100000000 ||
                    (seconds > 0 ? 1 : 0) + (cases > 0 ? 1 : 0) + (onlySeed.HasValue ? 1 : 0) != 1)
                    throw new ArgumentException("Use --soak --report FILE with exactly one of --seconds 1..86400, --cases 1..100000000, --case-seed INT.");
                string? parent = Path.GetDirectoryName(Path.GetFullPath(report));
                if (parent != null) Directory.CreateDirectory(parent);
                using var file = new FileStream(report, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
                using var output = new StreamWriter(file) { AutoFlush = true };
                string applicationHash = Hash(typeof(WorldSession).Assembly.Location);
                string runnerHash = Hash(typeof(GameplaySoak).Assembly.Location);
                var assemblies = Directory.EnumerateFiles(AppContext.BaseDirectory, "CriticalShift*.dll")
                    .OrderBy(Path.GetFileName, StringComparer.Ordinal).ToDictionary(p => Path.GetFileName(p), Hash);
                Write(output, new { Status = "Running", StartedUtc = DateTimeOffset.UtcNow, Seed = seed, Seconds = seconds,
                    RequestedCases = cases, CaseSeed = onlySeed, Control = control, ApplicationSha256 = applicationHash, RunnerSha256 = runnerHash, Assemblies = assemblies,
                    Scope = "Offline logical gameplay; synthetic access/recovery; no Unity physics or networking" });
                var random = new Random(seed); var clock = Stopwatch.StartNew(); long completed = 0, actions = 0;
                long nextReport = 30; int currentSeed = onlySeed ?? random.Next();
                try
                {
                    do
                    {
                        actions += Exercise(currentSeed, control == "medical-ledger", control == "contamination-ledger", control == "backup-ledger", control == "fitting-ledger", control == "feed-ledger", control == "repair-ledger"); completed++;
                        Require(control != "failure", "Intentional negative control.");
                        if (clock.Elapsed.TotalSeconds >= nextReport)
                        {
                            var pulse = new { Status = "Running", AtUtc = DateTimeOffset.UtcNow, Cases = completed, CheckedSteps = actions,
                                ElapsedSeconds = clock.Elapsed.TotalSeconds, ManagedBytes = GC.GetTotalMemory(false) };
                            Write(output, pulse); Console.WriteLine(JsonSerializer.Serialize(pulse)); nextReport += 30;
                        }
                        currentSeed = random.Next();
                    } while (!onlySeed.HasValue && (cases > 0 ? completed < cases : clock.Elapsed.TotalSeconds < seconds));
                    var result = new { Status = "Passed", FinishedUtc = DateTimeOffset.UtcNow, Cases = completed, CheckedSteps = actions,
                        ElapsedSeconds = clock.Elapsed.TotalSeconds, Seed = seed, ApplicationSha256 = applicationHash, RunnerSha256 = runnerHash, Assemblies = assemblies };
                    Write(output, result); Console.WriteLine(JsonSerializer.Serialize(result)); return 0;
                }
                catch (Exception error)
                {
                    // Only explicit invariant names/type/seed are recorded, never account or arbitrary machine data.
                    var failed = new { Status = "Failed", FinishedUtc = DateTimeOffset.UtcNow, Cases = completed, CheckedSteps = actions,
                        CaseSeed = currentSeed, Control = control, ErrorType = error.GetType().Name,
                        Invariant = error is SoakInvariantException ? error.Message : "Unexpected gameplay exception",
                        ElapsedSeconds = clock.Elapsed.TotalSeconds };
                    Write(output, failed); Console.Error.WriteLine(JsonSerializer.Serialize(failed)); return 1;
                }
            }
            catch (Exception error) when (error is ArgumentException || error is FormatException || error is OverflowException || error is IOException || error is UnauthorizedAccessException)
            { Console.Error.WriteLine("Soak configuration failed: " + error.GetType().Name); return 2; }
        }

        private static string Hash(string path)
        { using var sha = SHA256.Create(); using var input = File.OpenRead(path); return Convert.ToHexString(sha.ComputeHash(input)).ToLowerInvariant(); }
        private static void Write(StreamWriter output, object entry) => output.WriteLine(JsonSerializer.Serialize(entry));
        internal static void Require(bool value, string invariant)
        { if (!value) throw new SoakInvariantException(invariant); }
        private sealed class SoakInvariantException : Exception { internal SoakInvariantException(string message) : base(message) { } }
        private sealed class Policies : IInteractionAccessPolicy, IWorkerRecoveryPolicy
        {
            internal bool Allow = true, Safe = true;
            public AccessDecision Evaluate(Guid actor, Guid entity, InteractionKind kind) => Allow ? AccessDecision.Allowed : AccessDecision.OutOfReach;
            public RecoveryClearance Evaluate(Guid epoch, Guid worker, long attempt) => Safe ? RecoveryClearance.Safe : RecoveryClearance.Blocked;
        }

        private static int Exercise(int seed, bool dropMedicalStart = false, bool dropContact = false, bool dropBackup = false, bool dropFitting = false, bool dropFeed = false, bool dropRepair = false)
        {
            var random = new Random(seed); var policies = new Policies(); int duration = random.Next(1200, 12001);
            var configuration = new WorldSessionConfiguration(seed, duration, true, receiptCapacity: random.Next(1, 9), leaseMilliseconds: random.Next(100, 1001));
            int traceCapacity = random.Next(1, 130);
            var world = new WorldSession(configuration, policies, policies, traceCapacity: traceCapacity, maxProductionCycles: 96);
            int actions = CheckSupplyModel(seed) + CheckClinicalModel(seed ^ 0x1a43d7); Guid previousEpoch = Guid.Empty;
            for (int lifetime = 0; lifetime < 3; lifetime++)
            {
                var ports = Bind(world, random, out var medicalDefinition, out var feeds, out long repairDuration);
                var medicalLedger = new MedicalSoakLedger(world, medicalDefinition);
                world.Start(); long host = 0;
                var observations = new long[4];
                ProductionChange? lastMixedRepair = null;
                int mixedRepairCompletions = 0;
                var contactSequences = new long[4, 2]; var contactEligibleAt = new long[4, 2];
                bool omitNextFeed = dropFeed && lifetime == 0;
                InteractionReply Reactor(int who, ReactorAction action, Guid container = default, bool cooling = false)
                {
                    var reply = ports[who].OperateReactor(Id(30), action, container, cooling);
                    medicalLedger.Observe(reply, action); return reply;
                }
                InteractionReply Medical(int who, MedicalAction action, Guid body = default)
                {
                    medicalLedger.BeforeMedical(action, ports[who].ActorId, body, policies.Allow);
                    var reply = ports[who].OperateMedical(Id(60), action, body);
                    // A verifier-only loss injection must be caught by the independent ledger's next check.
                    if (!(dropMedicalStart && reply.HasNewCommit && reply.Medical?.Change?.Kind == MedicalEvent.Started))
                        medicalLedger.Observe(reply, medicalAction: action, requestedBody: body);
                    return reply;
                }
                void Contact(int who, int source)
                {
                    var worker = world.GetWorker(ports[who].ActorId); if (worker == null) return;
                    bool washing = source == 1, paused = world.View.Phase == WorldPhase.Paused;
                    long time = world.View.ElapsedMilliseconds;
                    bool cooling = contactSequences[who, source] > 0 && time < contactEligibleAt[who, source];
                    int load = washing ? 15 : (int)Math.Ceiling(20m * (worker.Suit == WorkerSuit.Intact ? 0.25m : worker.Suit == WorkerSuit.Compromised ? 0.5m : 1m));
                    int after = paused || cooling ? worker.Contamination : Math.Clamp(worker.Contamination + (washing ? -load : load), 0, 100);
                    var claimBefore = world.GetObject(Id(40 + who));
                    var contact = feeds[who, source].ObserveIfDue();
                    if (paused || cooling) Require(contact == null, "Mixed feed sampled excluded time or ignored its canonical eligibility hint.");
                    else
                    {
                        var expected = after == worker.Contamination ? WorkerStatus.NoChange : WorkerStatus.Applied;
                        Require(contact?.Status == expected && contact.Changed == (expected == WorkerStatus.Applied),
                            "Mixed feed admission disagrees with independent source/PPE/cooldown arithmetic.");
                        if (omitNextFeed) omitNextFeed = false; else contactSequences[who, source]++;
                        contactEligibleAt[who, source] = time + 150;
                        Require(contact!.ContaminationContact?.Sequence == contactSequences[who, source] &&
                            contact.ContaminationContact.OriginalOutcome == expected && contact.ContaminationContact.SampleShiftMilliseconds == time,
                            "Mixed feed sequence differs from independent accepted samples.");
                    }
                    Require(feeds[who, source].LastAcceptedSequence == contactSequences[who, source] &&
                        feeds[who, source].NextEligibleAtMilliseconds == contactEligibleAt[who, source],
                        "Mixed feed hint or sequence drifted across a sampled or excluded call.");
                    var conditionAfter = world.GetWorker(worker.Id)!; var claimAfter = world.GetObject(Id(40 + who));
                    Require(conditionAfter.Contamination == after && conditionAfter.Awareness == worker.Awareness && conditionAfter.Pose == worker.Pose &&
                        conditionAfter.RecoveryEpisode == worker.RecoveryEpisode && conditionAfter.RecoveryAttempt == worker.RecoveryAttempt &&
                        conditionAfter.LastCauseId == worker.LastCauseId && conditionAfter.SuitFitting?.Id == worker.SuitFitting?.Id && claimAfter?.Revision == claimBefore?.Revision,
                        "Mixed feed changed injury, fitting, recovery or body custody.");
                    if (contact != null) medicalLedger.ObserveEnvironment(contact, worker.Id, after);
                }
                void Advance(long target)
                {
                    var pendingRecoveries = Enumerable.Range(200, 4).Select(i => world.GetWorker(Id(i)))
                        .Where(w => w?.Pose == WorkerPose.Recovering).ToArray();
                    medicalLedger.BeforeAdvance();
                    var result = world.AdvanceTo(target);
                    foreach (var change in result.ProductionChanges)
                        if (change.Machine.Id == Id(20) && change.Kind == ProductionEvent.RepairCompleted)
                        { lastMixedRepair = change; mixedRepairCompletions++; }
                    foreach (var change in result.ProductionChanges)
                        if (change.Machine.Id == Id(22) && change.Kind == ProductionEvent.Completed)
                        {
                            var output = change.Output!; var input = change.Input;
                            Require(output.Kind == input.Kind && output.Units == input.Units && change.WasteUnits == 0 &&
                                output.Moisture == 100 && input.Moisture > 100 && output.Contamination == input.Contamination &&
                                output.Flags == input.Flags && !change.BypassedInspection && output.ParentBatchId == input.BatchId &&
                                output.CauseId == input.CauseId && output.OriginId == input.OriginId,
                                "Mixed drying changed conserved material, contamination or suspect lineage.");
                        }
                    foreach (var change in result.MedicalChanges) medicalLedger.ObserveAdvance(change);
                    medicalLedger.AfterAdvance();
                    var expectedExpiries = pendingRecoveries.Where(w => w!.RecoveryExpiresAtMilliseconds <= world.View.ElapsedMilliseconds).ToArray();
                    Require(result.WorkerChanges.Count == expectedExpiries.Length, "Mixed owner poll omitted or invented a stored recovery expiry.");
                    foreach (var expected in expectedExpiries)
                    {
                        Require(result.WorkerChanges.Any(c => c.Status == WorkerStatus.RecoveryExpired && c.Worker?.Id == expected!.Id &&
                            c.OccurredAtMilliseconds == expected.RecoveryExpiresAtMilliseconds && c.Worker.Pose == WorkerPose.Down &&
                            c.Worker.RecoveryExpiresAtMilliseconds == 0), "Mixed recovery expiry lost its worker, applied state or exact deadline.");
                        var current = world.GetWorker(expected!.Id) ?? world.Debrief?.WorkersAtEnd.SingleOrDefault(w => w.Id == expected.Id);
                        Require(current?.Pose == WorkerPose.Down && current.RecoveryExpiresAtMilliseconds == 0,
                            "Mixed expiry receipt disagrees with current or terminal worker condition.");
                    }
                }
                // Every lifetime begins with actual work; random interference then exercises consequences.
                Require(ports[0].Grab(Id(10)).HasNewCommit, "Initial fuel custody failed.");
                Require(Reactor(0, ReactorAction.Insert, Id(10)).HasNewCommit, "Initial fuel insertion failed.");
                Reactor(0, ReactorAction.SetCooling, cooling: true);
                Require(Reactor(0, ReactorAction.Start).HasNewCommit, "Initial reactor start failed.");
                Require(ports[1].Grab(Id(13)).HasNewCommit, "Initial ore custody failed.");
                Require(ports[1].OperateMachine(Id(20), ProductionAction.Insert, Id(13)).HasNewCommit, "Initial ore insertion failed.");
                Require(ports[1].OperateMachine(Id(20), ProductionAction.Start, bypass: true).HasNewCommit, "Initial production start failed.");
                Require(ports[1].Grab(Id(14)).HasNewCommit && ports[1].OperateMachine(Id(22), ProductionAction.Insert, Id(14)).HasNewCommit &&
                    ports[1].OperateMachine(Id(22), ProductionAction.Start).HasNewCommit, "Initial safe drying work failed.");
                Require(world.ApplyWorkerImpact(world.Epoch, Id(203), 1, WorkerImpact.Incapacitating, 0, Id(300), Id(303)).Changed,
                    "Initial mixed patient injury failed."); observations[3] = 1;
                Require(ports[2].Grab(Id(43)).HasNewCommit, "Initial mixed patient custody failed.");
                Require(Medical(2, MedicalAction.Insert, Id(43)).HasNewCommit, "Initial mixed patient insertion failed.");
                Require(Medical(2, MedicalAction.Start).HasNewCommit, "Initial treatment could not share reserve with active production/reactor.");
                Require(Reactor(0, ReactorAction.StartBackup).HasNewCommit, "Initial backup supply could not join mixed owner work.");
                Require(ports[0].OperateSuitFitting(Id(65), SuitFittingAction.Start).HasNewCommit, "Initial fitting could not join autonomous production/reactor/medical work.");
                Contact(0, 0);
                medicalLedger.Check();
                // Force an isolated clearing while the other autonomous owners are still active.
                host = 100; Advance(host);
                Require(world.Production.GetMachine(Id(20))!.Mode == ProductionMode.Jammed && world.Medical.View!.Phase == MedicalPhase.Treating &&
                    world.Reactor.EmergencyPowerSummary!.Running, "Mixed jam did not overlap active treatment and backup work.");
                Require(ports[1].OperateMachine(Id(20), ProductionAction.SetPower, powered: false).HasNewCommit,
                    "Mixed jam isolation failed.");
                var clearing = ports[1].OperateMachine(Id(20), ProductionAction.Repair);
                Require(clearing.HasNewCommit && clearing.Production!.Change?.Kind == ProductionEvent.RepairStarted,
                    "Mixed isolated clearing could not join the other owners.");
                long repairDue = host + repairDuration;
                host = repairDue; Advance(host);
                var repaired = world.Production.GetMachine(Id(20))!;
                Require(repaired.Mode == ProductionMode.PowerPaused && !repaired.Powered && repaired.WorkMilliseconds == 100 &&
                    repaired.RepairRemainingMilliseconds == 0 && mixedRepairCompletions == 1 && lastMixedRepair?.ShiftMilliseconds == repairDue &&
                    lastMixedRepair.CycleId == clearing.Production!.Change!.CycleId,
                    "Mixed owner settlement lost exact isolated clearing or advanced frozen production.");
                medicalLedger.Check();
                var previousDelivery = new long[3]; var previousSettled = new bool[3];
                for (int step = 0; step < 240 && world.View.Phase != WorldPhase.Ended; step++)
                {
                    int who = random.Next(4); var port = ports[who]; var worker = world.GetWorker(port.ActorId);
                    Guid entity = random.Next(3) == 0 ? Id(40 + random.Next(4)) : Id(10 + random.Next(8));
                    Guid machine = Id(20 + random.Next(3));
                    policies.Allow = random.Next(8) != 0; policies.Safe = random.Next(4) != 0;
                    switch (random.Next(29))
                    {
                        case 0: host += random.Next(351); Advance(host); break;
                        case 1: port.Grab(entity); break;
                        case 2: port.Release(entity); break;
                        case 3: port.Renew(entity); break;
                        case 4: port.OperateMachine(machine, ProductionAction.Insert, entity); break;
                        case 5: port.OperateMachine(machine, ProductionAction.Start, bypass: random.Next(2) == 0); break;
                        case 6: port.OperateMachine(machine, ProductionAction.SetPower, powered: random.Next(2) == 0); break;
                        case 7: port.OperateMachine(machine, new[] { ProductionAction.Repair, ProductionAction.Resume, ProductionAction.CancelCycle, ProductionAction.Eject }[random.Next(4)]); break;
                        case 8: Reactor(who, ReactorAction.Insert, entity); break;
                        case 9: Reactor(who, new[] { ReactorAction.Start, ReactorAction.Shutdown, ReactorAction.ResetTrip,
                            ReactorAction.EmergencyCooling, ReactorAction.AuxiliaryPower, ReactorAction.Eject, ReactorAction.SetCooling }[random.Next(7)], cooling: random.Next(2) == 0); break;
                        case 10:
                            if (port.CanReplayLast)
                            {
                                long revision = world.View.Revision; var before = world.Reactor.PowerSummary!;
                                var reply = port.ReplayLast(); Require(!reply.HasNewCommit, "Replay committed a second effect.");
                                medicalLedger.Observe(reply);
                                Require(world.View.Revision == revision, "Replay changed world revision.");
                                Require(world.Reactor.PowerSummary!.Spent == before.Spent, "Replay charged reserve twice.");
                            }
                            break;
                        case 11:
                            if (worker != null)
                            {
                                var hit = world.ApplyWorkerImpact(world.Epoch, worker.Id, observations[who] + 1,
                                    random.Next(3) == 0 ? WorkerImpact.Incapacitating : WorkerImpact.Knockdown,
                                    random.Next(101), Id(300), Id(301));
                                if (hit.Status == WorkerStatus.Applied) observations[who]++;
                            }
                            break;
                        case 12: if (worker != null) world.StabilizeWorker(world.Epoch, worker.Id, worker.Revision, random.Next(101)); break;
                        case 13:
                            if (worker != null)
                            {
                                if (worker.Pose == WorkerPose.Recovering) world.CompleteWorkerRecovery(world.Epoch, worker.Id, worker.RecoveryAttempt);
                                else world.BeginWorkerRecovery(world.Epoch, worker.Id, worker.RecoveryEpisode, worker.Revision);
                            }
                            break;
                        case 14:
                            if (world.View.Phase == WorldPhase.Paused) world.Resume(world.Epoch); else world.Pause(world.Epoch);
                            break;
                        case 15:
                            if (worker != null && world.View.ConnectedPlayerCount > 1)
                            { world.Disconnect(world.Epoch, Id(100 + who)); medicalLedger.PatientDisconnected(worker.Id); }
                            break;
                        case 16:
                            world.Schedule(world.Epoch, entity, "soak", random.Next(401), random.Next(2) == 0 ? WorldTimeBasis.RealTime : WorldTimeBasis.ShiftTime);
                            if (random.Next(2) == 0) world.CancelTimersForOwner(world.Epoch, entity);
                            break;
                        case 17: port.OperateDoor(Id(50), random.Next(2) == 0 ? DoorAction.Open : DoorAction.Close); break;
                        case 18: if (random.Next(4) == 0) world.BeginEvacuation(world.Epoch, Id(302)); break;
                        case 19:
                            Medical(who, new[] { MedicalAction.Start, MedicalAction.Cancel, MedicalAction.Eject, MedicalAction.EmergencyEject }[random.Next(4)]);
                            break;
                        case 20:
                            if (world.Medical.View?.Phase == MedicalPhase.Empty)
                            {
                                Guid patientBody = Id(40 + random.Next(4)); port.Grab(patientBody);
                                Medical(who, MedicalAction.Insert, patientBody);
                            }
                            break;
                        case 21:
                            var station = world.Medical.View;
                            if (station?.Phase == MedicalPhase.Loaded || station?.Phase == MedicalPhase.Interrupted) Medical(who, MedicalAction.Start);
                            else if (station?.Phase == MedicalPhase.Ready)
                                Medical(who, station.PatientId == port.ActorId && worker?.Pose == WorkerPose.Down ? MedicalAction.EmergencyEject : MedicalAction.Eject);
                            else if (station?.Phase == MedicalPhase.Treating && random.Next(3) == 0) Medical(who, MedicalAction.Cancel);
                            break;
                        case 22:
                            if (worker != null)
                            {
                                var suit = random.Next(2) == 0 ? WorkerSuit.Intact : WorkerSuit.Compromised;
                                int contamination = random.Next(101);
                                var environment = world.SetWorkerEnvironment(world.Epoch, worker.Id, worker.Revision, suit, contamination);
                                medicalLedger.ObserveEnvironment(environment, worker.Id, contamination);
                            }
                            break;
                        case 25:
                        case 26:
                            Reactor(who, random.Next(2) == 0 ? ReactorAction.StartBackup : ReactorAction.CancelBackup);
                            break;
                        case 27:
                        case 28:
                            port.OperateSuitFitting(Id(65), random.Next(2) == 0 ? SuitFittingAction.Start : SuitFittingAction.Cancel);
                            break;
                        case 23:
                        case 24:
                            Contact(who, random.Next(2));
                            break;
                    }
                    if (previousEpoch != Guid.Empty)
                    {
                        long revision = world.View.Revision;
                        Require(world.Finish(previousEpoch, WorldEndReason.Failed) == WorldControlStatus.WrongEpoch, "Old epoch accepted a control.");
                        Require(world.View.Revision == revision, "Old epoch changed successor.");
                    }
                    Check(world, previousDelivery, previousSettled, traceCapacity); medicalLedger.Check(); actions++;
                }
                policies.Allow = true;
                if (world.View.Phase == WorldPhase.Paused) world.Resume(world.Epoch);
                if (world.View.Phase == WorldPhase.Running)
                {
                    if (random.Next(4) == 0) world.Finish(world.Epoch, random.Next(2) == 0 ? WorldEndReason.Aborted : WorldEndReason.HostLost);
                    else Advance(long.MaxValue);
                }
                Check(world, previousDelivery, previousSettled, traceCapacity); medicalLedger.Check(); var debrief = world.Debrief!;
                Require(debrief != null, "Terminal world has no debrief.");
                Require(debrief!.Timeline.Count <= 128, "Incident journal became unbounded.");
                Require(world.View.ActiveClaimCount == 0 && world.WorkerCount == 0 && world.View.RegisteredObjectCount == 0 &&
                    world.View.PendingTimerCount == 0 && world.View.ConnectedPlayerCount == 0 && world.Doors.Count == 0 &&
                    world.Production.MachineCount == 0 && world.Production.BatchCount == 0 && world.Reactor.View == null && world.Medical.View == null && world.SuitFitting.StationCount == 0,
                    "Terminal owner leaked live resources.");
                Require(debrief!.Power!.Delivered == world.Reactor.PowerSummary!.Delivered, "Debrief delivery disagrees with owner.");
                Require(debrief.Production.ActiveUnits + debrief.Production.WasteUnits == debrief.Production.IssuedUnits, "Debrief material conservation failed.");
                foreach (var worker in debrief.WorkersAtEnd)
                    Require(worker.Pose != WorkerPose.Recovering || worker.RecoveryExpiresAtMilliseconds > debrief.World.ElapsedMilliseconds,
                        "Terminal roster retained an expired standing recovery.");
                long previousTime = -1;
                foreach (var row in debrief.Timeline)
                { Require(row.OccurredAtMilliseconds >= previousTime, "Debrief timeline order regressed."); previousTime = row.OccurredAtMilliseconds; }
                world.Stop(); world.Stop(); medicalLedger.Check(); Require(ReferenceEquals(world.Debrief, debrief), "Stop rewrote frozen terminal evidence.");
                previousEpoch = world.Epoch;
                if (lifetime < 2) world = world.Restart(policies, policies);
            }
            return actions + ContaminationSoak.Exercise(random, dropContact) + EmergencyPowerSoak.Exercise(random, dropBackup) +
                SuitFittingSoak.Exercise(random, dropFitting) + TimedRepairSoak.Exercise(random, dropRepair);
        }

        private static LocalCommandPort[] Bind(WorldSession world, Random random, out MedicalDefinition medical, out WorkerContaminationFeed[,] feeds, out long repairDuration)
        {
            var ports = new LocalCommandPort[4];
            for (int i = 0; i < ports.Length; i++)
            { world.RegisterConnection(Id(100 + i), Id(200 + i)); world.RegisterWorkerBody(Id(200 + i), Id(40 + i)); ports[i] = new LocalCommandPort(world, Id(100 + i)); }
            for (int i = 0; i < 8; i++) world.Production.RegisterBatch(Id(10 + i), Id(110 + i), Id(120 + i), Id(130 + i),
                i < 3 ? MaterialKind.Fuel : i < 6 ? MaterialKind.Ore : MaterialKind.CrushedOre, random.Next(1, 31), moisture: i == 3 || i == 4 ? 900 : random.Next(2) == 0 ? 0 : 900);
            repairDuration = random.Next(100, 1001);
            world.Production.RegisterMachine(Id(20), new MachineRecipe(Id(400), MaterialKind.Ore, MaterialKind.CrushedOre, 500, 250, 100, 100, repairDurationMilliseconds: repairDuration));
            world.Production.RegisterMachine(Id(21), new MachineRecipe(Id(401), MaterialKind.CrushedOre, MaterialKind.Fuel, 600, 300, 100, 100, repairDurationMilliseconds: random.Next(100, 1001)));
            world.Production.RegisterMachine(Id(22), MachineRecipe.Drying(Id(403), MaterialKind.Ore, 450, 100, 100));
            world.Reactor.Register(Id(30), new ReactorDefinition(Id(402)));
            world.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(random.Next(250, 1001), random.Next(4, 16), 4));
            medical = new MedicalDefinition(random.Next(250, 1001), random.Next(1, 8), random.Next(2, 6));
            world.Medical.Register(Id(60), medical);
            world.SuitFitting.Register(Id(65), new SuitFittingDefinition());
            world.RegisterWorkerContaminationSource(Id(62), new WorkerContaminationDefinition(WorkerContaminationKind.Exposure, 20, 150));
            world.RegisterWorkerContaminationSource(Id(63), new WorkerContaminationDefinition(WorkerContaminationKind.Decontamination, 15, 150));
            feeds = new WorkerContaminationFeed[4, 2];
            for (int who = 0; who < 4; who++)
                for (int source = 0; source < 2; source++) feeds[who, source] = new WorkerContaminationFeed(world, Id(200 + who), Id(62 + source));
            world.Doors.Register(Id(50), "soak-door", DoorState.Closed, DoorState.Open);
            long end = world.Configuration.ShiftDurationMilliseconds;
            world.Contracts.Register(new ShiftContractDefinition(Id(410), "Endurance supply",
                new GridDemandWave(Id(411), "First", end / 3, random.Next(20)),
                new GridDemandWave(Id(412), "Second", end * 2 / 3, random.Next(30)),
                new GridDemandWave(Id(413), "Last", end, random.Next(40))));
            return ports;
        }

        private static void Check(WorldSession world, long[] previousDelivery, bool[] previousSettled, int traceCapacity)
        {
            var material = world.Production.Summary; var power = world.Reactor.PowerSummary!; var contract = world.Contracts.View!;
            Require(material.IssuedUnits == material.ActiveUnits + material.WasteUnits, "Material conservation failed.");
            Require(power.Initial + power.Generated == power.Available + power.Spent + power.Delivered + power.Spilled, "Power conservation failed.");
            Require(power.Available >= 0 && power.Available <= power.Capacity, "Reserve outside capacity.");
            Require(contract.DeliveredEnergyUnits == power.Delivered, "Contract invented or lost delivered power.");
            Require(contract.Waves.Sum(w => w.DeliveredEnergyUnits) == power.Delivered, "Window delivery sum disagrees with canonical power.");
            for (int i = 0; i < contract.Waves.Count; i++)
            {
                var wave = contract.Waves[i];
                Require(wave.DeliveredEnergyUnits >= previousDelivery[i], "Window delivery moved backwards.");
                if (previousSettled[i]) Require(wave.Settled && wave.DeliveredEnergyUnits == previousDelivery[i], "Settled window changed after its cutoff.");
                if (wave.StartMilliseconds >= contract.ElapsedMilliseconds) Require(wave.DeliveredEnergyUnits == 0, "Future window received early delivery.");
                Require(wave.Met == (wave.DeliveredEnergyUnits >= wave.RequiredEnergyUnits), "Window assessment disagrees with its quota.");
                previousDelivery[i] = wave.DeliveredEnergyUnits; previousSettled[i] = wave.Settled;
            }
            if (world.View.Outcome == WorldOutcome.Succeeded) Require(contract.AllPeriodsMet, "Success bypassed an unmet contract.");
            Require(world.Trace.Records.Count <= traceCapacity, "Trace exceeded its configured capacity.");
            var holders = new HashSet<Guid>();
            foreach (var entity in Enumerable.Range(10, 8).Concat(Enumerable.Range(40, 4)))
            {
                var claim = world.GetObject(Id(entity)); if (claim == null) continue;
                Require(!(claim.HolderId.HasValue && claim.SlotId.HasValue), "Object has both holder and slot custody.");
                if (claim.HolderId.HasValue)
                { Require(holders.Add(claim.HolderId.Value), "Actor holds more than one object."); Require(world.GetWorker(claim.HolderId.Value)?.CanInteract == true, "Unavailable worker retains a claim."); }
            }
        }

        private static int CheckSupplyModel(int seed)
        {
            var random = new Random(seed); int duration = random.Next(1200, 12001), units = random.Next(1, 201);
            long[] ends = { random.Next(1, duration / 3), random.Next(duration / 3, duration * 2 / 3), duration };
            var quotas = new long[] { random.Next(50), random.Next(100), random.Next(150) };
            WorldSession Supply()
            {
                var policies = new Policies(); var world = new WorldSession(new WorldSessionConfiguration(seed, duration), policies);
                world.RegisterConnection(Id(100), Id(200));
                world.Production.RegisterBatch(Id(10), Id(110), Id(120), Id(130), MaterialKind.Fuel, units);
                world.Reactor.Register(Id(30), new ReactorDefinition(Id(402)));
                world.Contracts.Register(new ShiftContractDefinition(Id(410), "Independent demand model",
                    new GridDemandWave(Id(411), "First", ends[0], quotas[0]), new GridDemandWave(Id(412), "Second", ends[1], quotas[1]),
                    new GridDemandWave(Id(413), "Last", ends[2], quotas[2])));
                var port = new LocalCommandPort(world, Id(100)); world.Start(); port.Grab(Id(10));
                port.OperateReactor(Id(30), ReactorAction.Insert, Id(10)); port.OperateReactor(Id(30), ReactorAction.SetCooling, cooling: true);
                Require(port.OperateReactor(Id(30), ReactorAction.Start).HasNewCommit, "Supply model failed to start."); return world;
            }
            var one = Supply(); var many = Supply(); one.AdvanceTo(long.MaxValue); int actions = 1;
            for (int time = 0; time < duration;)
            { time = Math.Min(duration, time + random.Next(1, 302)); many.AdvanceTo(time); actions++; }
            long start = 0; bool met = true;
            for (int i = 0; i < ends.Length; i++)
            {
                // Independent arithmetic: finite fuel, complete 100ms quanta, four grid units per quantum.
                long expected = 4 * (Math.Min(ends[i], units * 100L) / 100 - Math.Min(start, units * 100L) / 100);
                Require(one.Contracts.View!.Waves[i].DeliveredEnergyUnits == expected, "Large jump disagrees with independent window model.");
                Require(many.Contracts.View!.Waves[i].DeliveredEnergyUnits == expected, "Partitioned samples disagree with independent window model.");
                met &= expected >= quotas[i]; start = ends[i];
            }
            Require(one.View.Outcome == (met ? WorldOutcome.Succeeded : WorldOutcome.Failed) && many.View.Outcome == one.View.Outcome,
                "Deadline outcome disagrees with independent demand model.");
            one.Stop(); many.Stop(); return actions;
        }

        private static int CheckClinicalModel(int seed)
        {
            var random = new Random(seed); int duration = random.Next(1, 6001), shift = random.Next(1000, 10001);
            int stock = random.Next(5), cost = random.Next(1, 11), reserve = random.Next(31), contamination = random.Next(101);
            var policies = new Policies(); var world = new WorldSession(new WorldSessionConfiguration(seed, shift, true), policies, policies);
            world.RegisterConnection(Id(100), Id(200)); world.RegisterConnection(Id(101), Id(201)); world.RegisterWorkerBody(Id(200), Id(40));
            world.Reactor.Register(Id(30), new ReactorDefinition(Id(402), initialReserve: reserve));
            world.Medical.Register(Id(50), new MedicalDefinition(duration, cost, stock));
            var port = new LocalCommandPort(world, Id(101)); var patientPort = new LocalCommandPort(world, Id(100)); world.Start();
            world.ApplyWorkerImpact(world.Epoch, Id(200), 1, WorkerImpact.Incapacitating, 0, Id(300), Id(301));
            world.SetWorkerEnvironment(world.Epoch, Id(200), world.GetWorker(Id(200))!.Revision, WorkerSuit.Intact, contamination);
            Require(port.Grab(Id(40)).HasNewCommit, "Clinical model could not retrieve its patient.");
            Require(port.OperateMedical(Id(50), MedicalAction.Insert, Id(40)).HasNewCommit, "Clinical model could not load its patient.");
            var first = port.OperateMedical(Id(50), MedicalAction.Start);
            var expectedStatus = contamination > 50 ? MedicalStatus.Contaminated : stock == 0 ? MedicalStatus.NoCartridge :
                reserve < cost ? MedicalStatus.InsufficientReserve : MedicalStatus.Applied;
            Require(first.Medical?.Status == expectedStatus, "Clinical admission disagrees with independent resource/condition model.");
            int used = 0, completed = 0, cancelled = 0, interrupted = 0, steps = 1;
            bool removed = false, externallyAided = false; int expectedContamination = contamination; var expectedSuit = WorkerSuit.Intact;
            if (expectedStatus == MedicalStatus.Applied)
            {
                used = 1; bool treating = true;
                for (int i = 0; i < 3; i++) { Require(!port.ReplayLast().HasNewCommit, "Clinical start replay committed again."); steps++; }
                switch (random.Next(9))
                {
                    case 1:
                        int before = Math.Min(duration - 1, shift - 1); world.AdvanceTo(before); world.Pause(world.Epoch);
                        world.AdvanceTo(60000); Require(world.Medical.Summary.CompletedCycles == 0, "Paused treatment completed early.");
                        world.Resume(world.Epoch); world.AdvanceTo(60000L + shift); steps += 3; break;
                    case 2:
                        world.ApplyWorkerImpact(world.Epoch, Id(200), 2, WorkerImpact.Incapacitating, 0, Id(300), Id(302));
                        interrupted = 1; treating = false; break;
                    case 3:
                        world.StabilizeWorker(world.Epoch, Id(200), world.GetWorker(Id(200))!.Revision, 0);
                        world.Disconnect(world.Epoch, Id(101)); world.AdvanceTo(0);
                        Require(patientPort.OperateMedical(Id(50), MedicalAction.EmergencyEject).HasNewCommit,
                            "Externally aided sole patient could not leave the interrupted chamber.");
                        interrupted = 1; treating = false; externallyAided = true; break;
                    case 4:
                        Require(port.OperateMedical(Id(50), MedicalAction.Cancel).HasNewCommit, "Clinical cancellation failed.");
                        cancelled = 1; treating = false;
                        var retry = port.OperateMedical(Id(50), MedicalAction.Start);
                        var retryStatus = stock < 2 ? MedicalStatus.NoCartridge : reserve < cost * 2 ? MedicalStatus.InsufficientReserve : MedicalStatus.Applied;
                        Require(retry.Medical?.Status == retryStatus, "Clinical retry disagrees with remaining stock/reserve model.");
                        if (retryStatus == MedicalStatus.Applied) { used = 2; treating = true; }
                        break;
                    case 5:
                        world.Disconnect(world.Epoch, Id(100)); removed = true; interrupted = 1; treating = false;
                        Require(world.View.Phase == WorldPhase.Running && world.GetObject(Id(40))!.IsRetired, "Clinical patient disconnect faulted or retained its body."); break;
                    case 6:
                        world.Disconnect(world.Epoch, Id(101));
                        if (duration < shift)
                        {
                            world.AdvanceTo(duration);
                            Require(patientPort.OperateMedical(Id(50), MedicalAction.EmergencyEject).HasNewCommit,
                                "Sole surviving clinical patient could not leave their ready chamber.");
                            Require(world.GetObject(Id(40))!.SlotId == null, "Emergency chamber release retained slot custody.");
                        }
                        break;
                    case 7:
                        expectedContamination = random.Next(51); expectedSuit = WorkerSuit.Compromised;
                        world.SetWorkerEnvironment(world.Epoch, Id(200), world.GetWorker(Id(200))!.Revision, WorkerSuit.Compromised, expectedContamination); break;
                    case 8:
                        expectedContamination = 51; expectedSuit = WorkerSuit.Compromised;
                        world.SetWorkerEnvironment(world.Epoch, Id(200), world.GetWorker(Id(200))!.Revision, WorkerSuit.Compromised, expectedContamination);
                        interrupted = 1; treating = false; break;
                }
                if (treating) { if (duration <= shift) completed = 1; else cancelled++; }
            }
            if (world.View.Phase == WorldPhase.Running) world.AdvanceTo(long.MaxValue);
            var summary = world.Medical.Summary; var power = world.Reactor.PowerSummary!; steps++;
            Require(summary.UsedCartridges == used && summary.RemainingCartridges == stock - used, "Clinical stock disagrees with independent cost model.");
            Require(summary.CompletedCycles == completed && summary.CancelledCycles == cancelled && summary.InterruptedCycles == interrupted,
                "Clinical terminal outcomes disagree with independent cycle model.");
            Require(power.Spent == cost * used && power.Available == reserve - cost * used, "Clinical debit disagrees with independent reserve model.");
            var patient = world.Debrief!.WorkersAtEnd.SingleOrDefault(w => w.Id == Id(200));
            Require((patient == null) == removed, "Clinical terminal roster disagrees with disconnect model.");
            if (patient != null)
            {
                Require(patient.Awareness == (completed > 0 || externallyAided ? WorkerAwareness.Alert : WorkerAwareness.Unconscious), "Clinical worker condition disagrees with model.");
                Require(patient.Pose == WorkerPose.Down && patient.Contamination == expectedContamination && patient.Suit == expectedSuit,
                    "Clinical completion overwrote patient facts.");
            }
            Require(world.WorkerCount == 0 && world.Medical.View == null && world.View.ActiveClaimCount == 0, "Clinical teardown leaked state.");
            world.Stop(); return steps;
        }
    }
}
