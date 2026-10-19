using System;
using System.Linq;
using System.Reflection;
using CriticalShift.Application;
using CriticalShift.Presentation;
using NUnit.Framework;

namespace CriticalShift.Offline.Tests
{
    [TestFixture]
    public sealed class EmergencyPowerTests
    {
        private static Guid Id(int value) => Fixture.Id(value);
        private sealed class Setup
        {
            internal readonly WorldSession World;
            internal readonly LocalCommandPort Port, Other;
            internal Guid Reactor => Id(90);
            internal Guid Fuel => Id(30);
            internal Setup(long initial = 0, long capacity = 100, long duration = 500, long output = 12,
                int charges = 2, long shift = 10000, bool register = true, bool start = true,
                int trace = 128, IInteractionAccessPolicy? access = null, int reservePerQuantum = 1)
            {
                World = new WorldSession(new WorldSessionConfiguration(42, shift, true), access ?? new TestAccess(), traceCapacity: trace);
                World.RegisterConnection(Id(20), Id(10)); World.RegisterConnection(Id(21), Id(11));
                World.Production.RegisterBatch(Fuel, Id(60), Id(70), Id(80), MaterialKind.Fuel, 100);
                World.Reactor.Register(Reactor, new ReactorDefinition(Id(91), capacity, initial,
                    millisecondsPerFuelUnit: 1000, powerQuantumMilliseconds: 1000, reservePerQuantum: reservePerQuantum, gridPerQuantum: 2));
                if (register) World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(duration, output, charges));
                Port = new LocalCommandPort(World, Id(20)); Other = new LocalCommandPort(World, Id(21));
                if (start) World.Start();
            }
            internal InteractionReply Act(ReactorAction action) => Port.OperateReactor(Reactor, action);
            internal EmergencyPowerView Backup => World.Reactor.EmergencyPowerSummary!;
            internal PowerView Power => World.Reactor.PowerSummary!;
            internal void Load()
            {
                Assert.That(Port.Grab(Fuel).HasNewCommit, Is.True);
                Assert.That(Port.OperateReactor(Reactor, ReactorAction.Insert, Fuel).HasNewCommit, Is.True);
                Assert.That(Port.OperateReactor(Reactor, ReactorAction.SetCooling, cooling: true).HasNewCommit, Is.True);
            }
        }
        private static void Balanced(PowerView p) => Assert.That(p.Initial + p.Generated,
            Is.EqualTo(p.Available + p.Spent + p.Delivered + p.Spilled));

        [Test] public void ZeroReserveBackupEnablesAnExplicitFueledReactorStart()
        {
            var f = new Setup(); f.Load();
            Assert.That(f.Act(ReactorAction.Start).Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientReserve));
            var start = f.Act(ReactorAction.StartBackup); var cycle = start.Reactor!.Change!.CycleId;
            Assert.That(start.HasNewCommit, Is.True); Assert.That(cycle, Is.Not.EqualTo(Guid.Empty));
            Assert.That(f.Power.Available, Is.Zero); Assert.That(f.Backup.UsedCharges, Is.EqualTo(1));
            Assert.That(f.Act(ReactorAction.StartBackup).Status, Is.EqualTo(InteractionStatus.NoChange));
            f.World.AdvanceTo(499); Assert.That(f.Power.Generated, Is.Zero);
            var done = f.World.AdvanceTo(500).ReactorChanges.Single();
            Assert.That(done.Kind, Is.EqualTo(ReactorEvent.BackupCompleted)); Assert.That(done.CycleId, Is.EqualTo(cycle));
            Assert.That(done.CauseId, Is.EqualTo(cycle)); Assert.That(done.InputBatchId, Is.EqualTo(Guid.Empty));
            Assert.That(done.GeneratedUnits, Is.EqualTo(12)); Assert.That(f.Power.Delivered, Is.Zero);
            Assert.That(f.World.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Loaded));
            Assert.That(f.Act(ReactorAction.Start).HasNewCommit, Is.True);
            Assert.That(f.Power.Available, Is.EqualTo(9)); f.World.AdvanceTo(1500);
            Assert.That(f.Power.Delivered, Is.EqualTo(2)); Balanced(f.Power);
        }

        [Test] public void BackupRetryIsHistoricalAfterCompletionAndCannotSpendAnotherCharge()
        {
            var f = new Setup(); var before = f.World.Reactor.View!.Revision;
            var first = f.Act(ReactorAction.StartBackup); long sequence = f.Port.LastTerminalSequence;
            var retry = new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.StartBackup, before));
            f.World.AdvanceTo(500); var revision = f.World.Reactor.View!.Revision;
            var replay = f.World.ExecuteInteraction(Id(20), retry);
            Assert.That(replay.IsReplay, Is.True); Assert.That(replay.HasNewCommit, Is.False);
            Assert.That(replay.Reactor!.Change!.EventId, Is.EqualTo(first.Reactor!.Change!.EventId));
            Assert.That(replay.Reactor.State!.EmergencyPower!.Running, Is.True);
            Assert.That(f.Backup.CompletedCycles, Is.EqualTo(1)); Assert.That(f.Backup.UsedCharges, Is.EqualTo(1));
            Assert.That(f.World.Reactor.View!.Revision, Is.EqualTo(revision)); Assert.That(f.Power.Generated, Is.EqualTo(12));
            Assert.That(f.World.Trace.Records.Last().ReactorEvent, Is.Null);
            var changed = new InteractionCommand(f.World.Epoch, sequence, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.CancelBackup, before));
            Assert.That(f.World.ExecuteInteraction(Id(20), changed).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
        }

        [Test] public void CancelKeepsConsumedChargeAndExhaustionCannotMintAnotherCycle()
        {
            var f = new Setup(charges: 2); f.Act(ReactorAction.StartBackup); f.World.AdvanceTo(100);
            Assert.That(f.Act(ReactorAction.CancelBackup).HasNewCommit, Is.True);
            Assert.That(f.Backup.CancelledCycles, Is.EqualTo(1)); Assert.That(f.Backup.RemainingCharges, Is.EqualTo(1));
            f.World.AdvanceTo(500); Assert.That(f.Power.Generated, Is.Zero);
            Assert.That(f.Act(ReactorAction.StartBackup).HasNewCommit, Is.True); f.World.AdvanceTo(1000);
            Assert.That(f.Backup.UsedCharges, Is.EqualTo(2)); Assert.That(f.Backup.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.Act(ReactorAction.StartBackup).Reactor!.Status, Is.EqualTo(ReactorStatus.NoBackupCharge));
            Assert.That(f.Act(ReactorAction.CancelBackup).Reactor!.Status, Is.EqualTo(ReactorStatus.InvalidState));
            Assert.That(f.Power.Generated, Is.EqualTo(12)); Balanced(f.Power);
        }

        [Test] public void BackupPauseFreezesWorkAndFinalizesRejectedCommandSequences()
        {
            var f = new Setup(); f.Act(ReactorAction.StartBackup); f.World.AdvanceTo(200); f.World.Pause(f.World.Epoch);
            var denied = f.Act(ReactorAction.CancelBackup); Assert.That(denied.IsTerminal, Is.True);
            Assert.That(denied.Status, Is.EqualTo(InteractionStatus.ActorUnavailable));
            f.World.AdvanceTo(5000); Assert.That(f.World.View.ElapsedMilliseconds, Is.EqualTo(200));
            Assert.That(f.Backup.Running, Is.True); Assert.That(f.Power.Generated, Is.Zero);
            f.World.Resume(f.World.Epoch); f.World.AdvanceTo(5299); Assert.That(f.Power.Generated, Is.Zero);
            f.World.AdvanceTo(5300); Assert.That(f.Backup.CompletedCycles, Is.EqualTo(1));
            Assert.That(f.Act(ReactorAction.AuxiliaryPower).HasNewCommit, Is.True);
        }

        [TestCase(500, 10)] [TestCase(1000, 5)] [TestCase(1500, 5)]
        public void LargeAndPartitionedClockStepsPreserveBackupStorageAttribution(long duration, long stored)
        {
            Setup Run(bool partition)
            {
                var f = new Setup(initial: 3, capacity: 10, output: 10, duration: duration, reservePerQuantum: 5);
                f.Load(); f.Act(ReactorAction.Start); f.Act(ReactorAction.StartBackup);
                if (partition) for (long time = 250; time < 2000; time += 250) f.World.AdvanceTo(time);
                f.World.AdvanceTo(2000); return f;
            }
            var leap = Run(false); var small = Run(true);
            Assert.That(leap.Backup.StoredUnits, Is.EqualTo(stored)); Assert.That(leap.Backup.SpilledUnits, Is.EqualTo(10 - stored));
            Assert.That(small.Backup.StoredUnits, Is.EqualTo(leap.Backup.StoredUnits)); Assert.That(small.Backup.SpilledUnits, Is.EqualTo(leap.Backup.SpilledUnits));
            Assert.That(small.Power.Available, Is.EqualTo(leap.Power.Available)); Assert.That(small.Power.Generated, Is.EqualTo(leap.Power.Generated));
            Assert.That(small.Power.Spilled, Is.EqualTo(leap.Power.Spilled)); Assert.That(small.Power.Delivered, Is.EqualTo(leap.Power.Delivered));
            Assert.That(leap.Power.Spilled, Is.EqualTo(10)); Balanced(leap.Power); Balanced(small.Power);
            var events = leap.World.Trace.Records.Where(r => r.ReactorEvent == ReactorEvent.Generated || r.ReactorEvent == ReactorEvent.BackupCompleted).ToArray();
            if (duration == 1000)
            {
                Assert.That(events[0].ReactorEvent, Is.EqualTo(ReactorEvent.Generated));
                Assert.That(events[1].ReactorEvent, Is.EqualTo(ReactorEvent.BackupCompleted));
            }
        }

        [TestCase(499, false)] [TestCase(500, true)] [TestCase(501, true)]
        public void DeadlineSettlesOnlyDueBackupWorkBeforeTerminalPublication(long shift, bool completed)
        {
            var f = new Setup(shift: shift); f.Act(ReactorAction.StartBackup); var result = f.World.AdvanceTo(10000);
            Assert.That(result.World.Phase, Is.EqualTo(WorldPhase.Ended)); Assert.That(f.World.Reactor.View, Is.Null);
            Assert.That(f.Power.Generated, Is.EqualTo(completed ? 12 : 0));
            Assert.That(f.Backup.Running, Is.False); Assert.That(f.Backup.CompletedCycles, Is.EqualTo(completed ? 1 : 0));
            Assert.That(f.Backup.CancelledCycles, Is.EqualTo(completed ? 0 : 1)); Assert.That(f.Backup.UsedCharges, Is.EqualTo(1));
            Assert.That(f.World.Debrief!.EmergencyPower, Is.SameAs(f.Backup));
            var power = f.Power; f.World.AdvanceTo(20000); Assert.That(f.Power, Is.SameAs(power));
            Assert.That(result.ReactorChanges.Count(c => c.Kind == ReactorEvent.BackupCompleted), Is.EqualTo(completed ? 1 : 0));
        }

        [Test] public void BackupCannotPayContractDemandOrReportAnEarlySuccess()
        {
            var f = new Setup(start: false, shift: 500);
            f.World.Contracts.Register(new ShiftContractDefinition(Id(300), "Grid", new GridDemandWave(Id(301), "Supply", 500, 1)));
            f.World.Start(); f.Act(ReactorAction.StartBackup); var result = f.World.AdvanceTo(500);
            Assert.That(f.Power.Generated, Is.EqualTo(12)); Assert.That(f.Power.Delivered, Is.Zero);
            Assert.That(result.World.Outcome, Is.EqualTo(WorldOutcome.Failed)); Assert.That(f.World.Contracts.View!.Waves.Single().Met, Is.False);
        }

        [Test] public void FullReserveRejectsWithoutConsumingStockAndCurrentRevisionProtectsBothConsumers()
        {
            var f = new Setup(initial: 100); var revision = f.World.Reactor.View!.Revision;
            Assert.That(f.Act(ReactorAction.StartBackup).Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientHeadroom));
            Assert.That(f.Backup.UsedCharges, Is.Zero); Assert.That(f.World.Reactor.View!.Revision, Is.EqualTo(revision));
            f.Act(ReactorAction.AuxiliaryPower); f.Act(ReactorAction.AuxiliaryPower);
            Assert.That(f.Act(ReactorAction.StartBackup).HasNewCommit, Is.True); long old = f.World.Reactor.View.Revision;
            f.World.AdvanceTo(500);
            var stale = f.World.ExecuteInteraction(Id(21), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.AuxiliaryPower, old)));
            Assert.That(stale.Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict)); Assert.That(f.Power.Available, Is.EqualTo(100));
            Assert.That(f.Other.OperateReactor(f.Reactor, ReactorAction.AuxiliaryPower).Status, Is.EqualTo(InteractionStatus.PayloadMismatch));
        }

        [Test] public void OperatorDisconnectLeavesPaidBackupAutonomousAndNewEpochHasFreshSetup()
        {
            var f = new Setup(); f.Act(ReactorAction.StartBackup); var epoch = f.World.Epoch;
            f.World.Disconnect(epoch, Id(20)); f.World.AdvanceTo(500);
            Assert.That(f.Backup.CompletedCycles, Is.EqualTo(1)); Assert.That(f.Power.Available, Is.EqualTo(12));
            var stopped = f.Backup; f.World.Stop(); Assert.That(f.World.Debrief!.EmergencyPower!.UsedCharges, Is.EqualTo(1));
            var successor = f.World.Restart(new TestAccess()); Assert.That(successor.Reactor.EmergencyPowerSummary, Is.Null);
            Assert.That(successor.Epoch, Is.Not.EqualTo(epoch)); Assert.That(stopped.CompletedCycles, Is.EqualTo(1));
            successor.RegisterConnection(Id(20), Id(10)); successor.Reactor.Register(f.Reactor, new ReactorDefinition(Id(91)));
            successor.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition()); successor.Start();
            var old = successor.ExecuteInteraction(Id(20), new InteractionCommand(epoch, 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.StartBackup, 1)));
            Assert.That(old.Status, Is.EqualTo(InteractionStatus.WrongEpoch)); Assert.That(successor.Reactor.EmergencyPowerSummary!.UsedCharges, Is.Zero);
        }

        [Test] public void BackupCausalityAndReadoutSurviveTraceEvictionWithoutFuelAttribution()
        {
            var f = new Setup(trace: 8); var feed = new SandboxTraceFeed(f.Port); f.Act(ReactorAction.StartBackup); feed.Refresh();
            f.Port.ReplayLast(); feed.Refresh(); f.World.AdvanceTo(500); feed.Refresh();
            Assert.That(feed.Entries.Count(e => e.Reactor == ReactorEvent.BackupStarted), Is.EqualTo(1));
            Assert.That(feed.Entries.Count(e => e.Reactor == ReactorEvent.BackupCompleted), Is.EqualTo(1));
            var completion = f.World.Trace.Records.Single(r => r.ReactorEvent == ReactorEvent.BackupCompleted);
            Assert.That(completion.ReactorChange!.InputBatchId, Is.EqualTo(Guid.Empty));
            Assert.That(completion.ReactorChange.CauseId, Is.EqualTo(completion.ReactorChange.CycleId));
            Assert.That(completion.CycleId, Is.EqualTo(completion.ReactorChange.CycleId));
            Assert.That(completion.CauseId, Is.EqualTo(completion.ReactorChange.CauseId));
            for (int i = 501; i <= 520; i++) f.World.AdvanceTo(i);
            Assert.That(f.World.Trace.Records.Any(r => r.ReactorEvent == ReactorEvent.BackupCompleted), Is.False);
            f.World.Stop(); var retained = f.World.Debrief!.Timeline.Single(r => r.ReactorEvent == ReactorEvent.BackupCompleted);
            Assert.That(retained.ReactorChange!.EventId, Is.EqualTo(completion.ReactorChange.EventId));
            Assert.That(retained.OccurredAtMilliseconds, Is.EqualTo(500));
        }

        [Test] public void CompletionArithmeticFailureFaultsBeforePublishingDeadlineOrEnergy()
        {
            var f = new Setup(shift: 500); f.Act(ReactorAction.StartBackup);
            typeof(ReactorOperations).GetField("_revision", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(f.World.Reactor, long.MaxValue);
            Assert.Throws<OverflowException>(() => f.World.AdvanceTo(500));
            Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Faulted)); Assert.That(f.World.Debrief!.World.Outcome, Is.EqualTo(WorldOutcome.Faulted));
            Assert.That(f.Power.Generated, Is.Zero); Assert.That(f.Backup.CompletedCycles, Is.Zero);
            Assert.That(f.Backup.CancelledCycles, Is.EqualTo(1)); Assert.That(f.Backup.UsedCharges, Is.EqualTo(1));
            Assert.That(f.World.Trace.Records.Any(r => r.Kind == SessionTraceKind.Ended || r.ReactorEvent == ReactorEvent.BackupCompleted), Is.False);
        }

        [Test] public void UnrepresentableBackupDueTimeRejectsBeforeStockConsumption()
        {
            var f = new Setup(shift: long.MaxValue, duration: 5000); f.World.AdvanceTo(long.MaxValue - 1000);
            long revision = f.World.Reactor.View!.Revision;
            Assert.That(f.Act(ReactorAction.StartBackup).Reactor!.Status, Is.EqualTo(ReactorStatus.InvalidTime));
            Assert.That(f.Backup.UsedCharges, Is.Zero); Assert.That(f.Backup.Running, Is.False);
            Assert.That(f.World.Reactor.View.Revision, Is.EqualTo(revision)); Assert.That(f.World.View.Phase, Is.EqualTo(WorldPhase.Running));
        }

        [Test] public void DeniedBackupAccessFinalizesItsReceiptAndStaleCompetingStartCannotConsumeStock()
        {
            var access = new TestAccess { Decision = AccessDecision.OutOfReach }; var f = new Setup(access: access);
            long revision = f.World.Reactor.View!.Revision;
            var denied = f.Act(ReactorAction.StartBackup); Assert.That(denied.Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(denied.IsTerminal, Is.True); Assert.That(f.Backup.UsedCharges, Is.Zero);
            access.Decision = AccessDecision.Allowed;
            Assert.That(f.Port.ReplayLast().Status, Is.EqualTo(InteractionStatus.OutOfReach));
            Assert.That(f.Act(ReactorAction.StartBackup).HasNewCommit, Is.True);
            var stale = f.World.ExecuteInteraction(Id(21), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor,
                reactor: new ReactorRequest(ReactorAction.StartBackup, revision)));
            Assert.That(stale.Reactor!.Status, Is.EqualTo(ReactorStatus.RevisionConflict)); Assert.That(f.Backup.UsedCharges, Is.EqualTo(1));
        }

        [TestCase(false)] [TestCase(true)]
        public void BackupMedicalAndCoreUseOneReserveRegardlessOfConsumerOrder(bool medicalFirst)
        {
            var f = new Setup(start: false); f.World.RegisterWorkerBody(Id(11), Id(31));
            f.World.Medical.Register(Id(100), new MedicalDefinition(reserveCost: 9)); f.World.Start(); f.Load();
            f.World.ApplyWorkerImpact(f.World.Epoch, Id(11), 1, WorkerImpact.Incapacitating, 0, Id(400), Id(401));
            Assert.That(f.Port.Grab(Id(31)).HasNewCommit, Is.True);
            Assert.That(f.Port.OperateMedical(Id(100), MedicalAction.Insert, Id(31)).HasNewCommit, Is.True);
            f.Act(ReactorAction.StartBackup); f.World.AdvanceTo(500);
            InteractionReply Care() => f.Port.OperateMedical(Id(100), MedicalAction.Start);
            var first = medicalFirst ? Care() : f.Act(ReactorAction.Start);
            var second = medicalFirst ? f.Act(ReactorAction.Start) : Care();
            Assert.That(first.HasNewCommit && second.HasNewCommit, Is.True);
            Assert.That(f.Power.Generated, Is.EqualTo(12)); Assert.That(f.Power.Spent, Is.EqualTo(12)); Assert.That(f.Power.Available, Is.Zero);
            Assert.That(f.World.Medical.Summary.UsedCartridges, Is.EqualTo(1)); Assert.That(f.World.Reactor.View!.Mode, Is.EqualTo(ReactorMode.Running));
            Assert.That(f.Act(ReactorAction.AuxiliaryPower).Reactor!.Status, Is.EqualTo(ReactorStatus.InsufficientReserve)); Balanced(f.Power);
        }

        [TestCase(false)] [TestCase(true)]
        public void BackupCommandsCannotCarryClientEnergyOrUnrelatedCoolingPayload(bool unknownAction)
        {
            var f = new Setup(); long revision = f.World.Reactor.View!.Revision;
            var bad = new ReactorRequest(unknownAction ? (ReactorAction)999 : ReactorAction.StartBackup, revision, cooling: !unknownAction);
            var result = f.World.ExecuteInteraction(Id(20), new InteractionCommand(f.World.Epoch, 1, InteractionKind.Reactor, f.Reactor, reactor: bad));
            Assert.That(result.Status, Is.EqualTo(InteractionStatus.InvalidPayload)); Assert.That(result.IsTerminal, Is.False);
            Assert.That(f.Backup.UsedCharges, Is.Zero); Assert.That(f.Act(ReactorAction.StartBackup).HasNewCommit, Is.True);
        }

        [Test] public void OptionalBackupAndSetupRulesRejectBeforeCreatingUsableStock()
        {
            var absent = new Setup(register: false);
            Assert.That(absent.Act(ReactorAction.StartBackup).Reactor!.Status, Is.EqualTo(ReactorStatus.BackupUnavailable));
            var f = new Setup(start: false);
            Assert.Throws<InvalidOperationException>(() => f.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition()));
            f.World.Start(); Assert.Throws<InvalidOperationException>(() => f.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition()));
            var tooLarge = new Setup(capacity: 10, register: false, start: false);
            Assert.Throws<ArgumentException>(() => tooLarge.World.Reactor.RegisterEmergencyPower(new EmergencyPowerDefinition(reserveUnits: 11)));
            Assert.That(tooLarge.World.Reactor.EmergencyPowerSummary, Is.Null);
        }

        [TestCase(0, 12, 2)] [TestCase(60001, 12, 2)] [TestCase(500, 0, 2)]
        [TestCase(500, 1000000001, 2)] [TestCase(500, 12, 0)] [TestCase(500, 12, 33)]
        public void InvalidBackupDefinitionsCannotCreateACharge(long duration, long output, int charges) =>
            Assert.Throws<ArgumentOutOfRangeException>(() => new EmergencyPowerDefinition(duration, output, charges));
    }
}
