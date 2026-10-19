using System;
using System.Collections.Generic;
using System.Linq;
using CriticalShift.Application;
using static CriticalShift.Scenarios.ScenarioInput;
using static CriticalShift.Scenarios.GameplaySoak;

namespace CriticalShift.Scenarios
{
    /// <summary>Independent event-clock model of finite backup stock, core quanta and one shared reserve.</summary>
    internal static class EmergencyPowerSoak
    {
        private sealed class Access : IInteractionAccessPolicy
        { public AccessDecision Evaluate(Guid actor, Guid target, InteractionKind kind) => AccessDecision.Allowed; }
        internal static int Exercise(Random random, bool omitFirstCompletion)
        {
            long capacity = random.Next(12, 32), output = random.Next(3, (int)capacity + 1);
            long duration = random.Next(10, 251), quantum = random.Next(10, 201), limit = random.Next(1500, 6001);
            int charges = random.Next(2, 9), reservePerQuantum = random.Next(1, 6), gridPerQuantum = random.Next(1, 6);
            var world = new WorldSession(new WorldSessionConfiguration(42, limit, true), new Access(), traceCapacity: 8);
            world.RegisterConnection(Id(950), Id(951));
            world.Production.RegisterBatch(Id(952), Id(953), Id(954), Id(955), MaterialKind.Fuel, 100);
            world.Reactor.Register(Id(956), new ReactorDefinition(Id(957), capacity, 0, millisecondsPerFuelUnit: 1000,
                powerQuantumMilliseconds: quantum, reservePerQuantum: reservePerQuantum, gridPerQuantum: gridPerQuantum));
            world.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(duration, output, charges));
            var port = new LocalCommandPort(world, Id(950)); world.Start();
            Require(port.Grab(Id(952)).HasNewCommit && port.OperateReactor(Id(956), ReactorAction.Insert, Id(952)).HasNewCommit &&
                port.OperateReactor(Id(956), ReactorAction.SetCooling, cooling: true).HasNewCommit, "Backup model fuel setup failed.");
            long available = 0, generated = 0, spent = 0, delivered = 0, spilled = 0;
            long host = 0, shift = 0, work = 0, due = 0, produced = 0, stored = 0, backupSpilled = 0;
            int remaining = charges, completed = 0, cancelled = 0, steps = 0;
            Guid cycle = Guid.Empty; var cycles = new HashSet<Guid>();
            bool coreRunning = false, backupRunning = false, paused = false, ended = false, omitted = false;
            void Check()
            {
                var power = world.Reactor.PowerSummary!; var backup = world.Reactor.EmergencyPowerSummary!;
                Require(power.Available == available, "Backup reserve differs from independent source chronology.");
                Require(power.Generated == generated && power.Spent == spent && power.Delivered == delivered && power.Spilled == spilled,
                    "Backup/shared-core accounting differs from independent quantum ledger.");
                Require(backup.RemainingCharges == remaining && backup.UsedCharges == charges - remaining && backup.Running == backupRunning &&
                    backup.CompletedCycles == completed && backup.CancelledCycles == cancelled && backup.ProducedUnits == produced &&
                    backup.StoredUnits == stored && backup.SpilledUnits == backupSpilled, "Backup source stock/outcomes differ from independent ledger.");
                Require(world.View.ElapsedMilliseconds == shift && (ended ? world.Debrief!.EmergencyPower!.UsedCharges == charges - remaining : true),
                    "Backup clock or terminal source projection diverged."); steps++;
            }
            void Credit(long reserve, long grid)
            {
                long kept = Math.Min(reserve, capacity - available);
                available += kept; generated += reserve + grid; delivered += grid; spilled += reserve - kept;
            }
            void Advance(long delta)
            {
                host += delta; long target = paused ? shift : Math.Min(limit, shift + delta);
                long? completedAt = null;
                while (true)
                {
                    long coreAt = coreRunning ? shift + quantum - work % quantum : long.MaxValue;
                    long backupAt = backupRunning ? due : long.MaxValue;
                    long at = Math.Min(coreAt, backupAt); if (at > target) break;
                    if (coreRunning) work += at - shift; shift = at;
                    // Core quanta win an exact tie, matching the explicit authored settlement policy.
                    if (coreAt == at) Credit(reservePerQuantum, gridPerQuantum);
                    if (backupAt == at)
                    {
                        long kept = Math.Min(output, capacity - available);
                        if (!(omitFirstCompletion && !omitted)) Credit(output, 0);
                        else omitted = true;
                        completedAt = due; produced += output; stored += kept; backupSpilled += output - kept; completed++; backupRunning = false;
                    }
                }
                if (coreRunning) work += target - shift; shift = target;
                if (shift == limit) { ended = true; if (backupRunning) { backupRunning = false; cancelled++; } }
                var advance = world.AdvanceTo(host);
                var completions = advance.ReactorChanges.Where(c => c.Kind == ReactorEvent.BackupCompleted).ToArray();
                Require(completions.Length == (completedAt.HasValue ? 1 : 0), "Backup completion publication disagrees with independent due schedule.");
                if (completedAt.HasValue)
                {
                    var completion = completions.Single();
                    Require(completion.ShiftMilliseconds == completedAt.Value && completion.CycleId == cycle &&
                        completion.CauseId == cycle && completion.InputBatchId == Guid.Empty && completion.GeneratedUnits == output,
                        "Backup completion lost its modeled occurrence coordinate or committed source cycle.");
                }
                Check();
            }
            void Act(ReactorAction action)
            {
                ReactorStatus expected;
                if (paused)
                {
                    var denied = port.OperateReactor(Id(956), action);
                    Require(denied.Status == InteractionStatus.ActorUnavailable && denied.IsTerminal, "Paused backup command was admitted or wedged its receipt."); Check(); return;
                }
                switch (action)
                {
                    case ReactorAction.StartBackup:
                        expected = backupRunning ? ReactorStatus.NoChange : remaining == 0 ? ReactorStatus.NoBackupCharge :
                            capacity - available < output ? ReactorStatus.InsufficientHeadroom : ReactorStatus.Applied;
                        if (expected == ReactorStatus.Applied) { remaining--; backupRunning = true; due = shift + duration; }
                        break;
                    case ReactorAction.CancelBackup:
                        expected = backupRunning ? ReactorStatus.Applied : ReactorStatus.InvalidState;
                        if (expected == ReactorStatus.Applied) { backupRunning = false; cancelled++; }
                        break;
                    case ReactorAction.Start:
                        expected = coreRunning ? ReactorStatus.NoChange : available < 3 ? ReactorStatus.InsufficientReserve : ReactorStatus.Applied;
                        if (expected == ReactorStatus.Applied) { coreRunning = true; available -= 3; spent += 3; }
                        break;
                    case ReactorAction.Shutdown:
                        expected = coreRunning ? ReactorStatus.Applied : ReactorStatus.NoChange; coreRunning = false; break;
                    case ReactorAction.AuxiliaryPower:
                        expected = available < 6 ? ReactorStatus.InsufficientReserve : ReactorStatus.Applied;
                        if (expected == ReactorStatus.Applied) { available -= 6; spent += 6; }
                        break;
                    default: throw new InvalidOperationException("Unmodelled backup action.");
                }
                var result = port.OperateReactor(Id(956), action);
                Require(result.Reactor?.Status == expected && result.HasNewCommit == (expected == ReactorStatus.Applied),
                    "Backup/core admission disagrees with independent stock/headroom/spend model.");
                if (action == ReactorAction.StartBackup && expected == ReactorStatus.Applied)
                {
                    var start = result.Reactor!.Change;
                    Require(start != null && start.Kind == ReactorEvent.BackupStarted && start.CycleId != Guid.Empty &&
                        start.CauseId == start.CycleId && start.InputBatchId == Guid.Empty && start.ShiftMilliseconds == shift && cycles.Add(start.CycleId),
                        "Backup start did not publish one fresh attributed source identity.");
                    cycle = start!.CycleId;
                }
                if (action == ReactorAction.CancelBackup && expected == ReactorStatus.Applied)
                    Require(result.Reactor!.Change?.Kind == ReactorEvent.BackupCancelled && result.Reactor.Change.CycleId == cycle &&
                        result.Reactor.Change.ShiftMilliseconds == shift, "Backup cancellation lost its active source identity or coordinate.");
                Check();
            }
            Act(ReactorAction.StartBackup); Advance(duration); Act(ReactorAction.Start);
            var actions = new[] { ReactorAction.StartBackup, ReactorAction.CancelBackup, ReactorAction.Start, ReactorAction.Shutdown, ReactorAction.AuxiliaryPower };
            for (int i = 0; i < 96 && !ended; i++)
            {
                int op = random.Next(9);
                if (op < 5) Act(actions[op]);
                else if (op < 7) Advance(random.Next(251));
                else if (op == 7)
                {
                    if (paused) world.Resume(world.Epoch); else world.Pause(world.Epoch);
                    paused = !paused; Check();
                }
                else if (port.CanReplayLast)
                {
                    var replay = port.ReplayLast(); Require(replay.IsReplay && !replay.HasNewCommit, "Backup model replay escaped historical admission."); Check();
                }
            }
            if (!ended)
            {
                if (paused) { world.Resume(world.Epoch); paused = false; }
                Advance(limit + 100);
            }
            Require(world.View.Phase == WorldPhase.Ended && world.View.RegisteredObjectCount == 0 && world.View.ActiveClaimCount == 0,
                "Backup terminal cleanup retained live claims."); Check(); return steps;
        }
    }
}
