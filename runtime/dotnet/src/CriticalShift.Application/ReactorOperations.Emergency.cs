#nullable enable
using System;
using CriticalShift.Features.Power.Domain;

namespace CriticalShift.Application
{
    public sealed partial class ReactorOperations
    {
        private EmergencySupplyState? _backup;
        private EmergencyPowerView? _terminalBackup;
        public EmergencyPowerView? EmergencyPowerSummary => _backup == null ? _terminalBackup : new EmergencyPowerView(_world.Epoch, _backup);
        internal long NextBackupBoundary => _backup?.Running == true ? _backup.DueAtMilliseconds : long.MaxValue;
        public void RegisterEmergencyPower(EmergencyPowerDefinition definition) => _world.RegisterProduction(() =>
        {
            if (definition == null) throw new ArgumentNullException(nameof(definition));
            if (_core == null || _power == null || _backup != null || _terminalBackup != null)
                throw new InvalidOperationException("Register one backup supply after the setup reactor.");
            if (definition.ReserveUnits > _power.Capacity)
                throw new ArgumentException("A backup charge must fit the canonical reserve capacity.", nameof(definition));
            var next = new EmergencySupplyState(definition.Rules); long revision = checked(_revision + 1);
            _backup = next; _revision = revision;
        });
        private InteractionReply StartBackup()
        {
            if (_backup == null) return Reply(ReactorStatus.BackupUnavailable);
            if (_backup.Running) return Reply(ReactorStatus.NoChange);
            if (_backup.RemainingCharges == 0) return Reply(ReactorStatus.NoBackupCharge);
            if (_power!.Capacity - _power.Available < _backup.Rules.ReserveUnits) return Reply(ReactorStatus.InsufficientHeadroom);
            long now = _world.View.ElapsedMilliseconds;
            if (now > long.MaxValue - _backup.Rules.DurationMilliseconds) return Reply(ReactorStatus.InvalidTime);
            var next = _backup.Begin(Guid.NewGuid(), now); long revision = checked(_revision + 1);
            _backup = next; _revision = revision;
            return Reply(ReactorStatus.Applied, BackupChange(ReactorEvent.BackupStarted, now));
        }
        private InteractionReply CancelBackup()
        {
            if (_backup == null) return Reply(ReactorStatus.BackupUnavailable);
            if (!_backup.Running) return Reply(ReactorStatus.InvalidState);
            var next = _backup.Cancel(); long revision = checked(_revision + 1);
            _backup = next; _revision = revision;
            return Reply(ReactorStatus.Applied, BackupChange(ReactorEvent.BackupCancelled, _world.View.ElapsedMilliseconds));
        }
        internal ReactorChange? CompleteBackupAt(long at)
        {
            if (_backup == null || !_backup.Running || at < _backup.DueAtMilliseconds) return null;
            if (at != _backup.DueAtMilliseconds) throw new InvalidOperationException("World settlement skipped a required backup boundary.");
            var power = _power!.Credit(_backup.Rules.ReserveUnits, 0);
            var backup = _backup.Complete(at, power.Available - _power.Available);
            long revision = checked(_revision + 1);
            _power = power; _backup = backup; _revision = revision;
            return BackupChange(ReactorEvent.BackupCompleted, at, backup.Rules.ReserveUnits);
        }
        private ReactorChange BackupChange(ReactorEvent kind, long at, long generated = 0) =>
            new ReactorChange(kind, View!, at, _backup!.CycleId, Guid.Empty, _backup.CycleId, ReactorRisk.None, generated);
        private void ClearBackup()
        {
            if (_backup == null) return;
            var closed = _backup.Running ? _backup.Cancel() : _backup;
            _terminalBackup = new EmergencyPowerView(_world.Epoch, closed); _backup = null;
        }
    }
}
