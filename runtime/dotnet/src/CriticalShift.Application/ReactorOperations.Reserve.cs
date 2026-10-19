#nullable enable
using System;
using CriticalShift.Features.Power.Domain;

namespace CriticalShift.Application
{
    public sealed partial class ReactorOperations
    {
        internal sealed class ReserveDebit
        {
            internal ReserveDebit(PowerAccount before, PowerAccount after, long previousRevision, long nextRevision)
            { Before = before; After = after; PreviousRevision = previousRevision; NextRevision = nextRevision; }
            internal PowerAccount Before { get; }
            internal PowerAccount After { get; }
            internal long PreviousRevision { get; }
            internal long NextRevision { get; }
        }
        internal bool TryPrepareReserveDebit(long cost, out ReserveDebit? debit)
        {
            debit = null;
            if (_power == null || !_power.TrySpend(cost, out var after)) return false;
            debit = new ReserveDebit(_power, after, _revision, checked(_revision + 1)); return true;
        }
        internal void CommitReserveDebit(ReserveDebit debit)
        {
            if (!ReferenceEquals(_power, debit.Before) || _revision != debit.PreviousRevision)
                throw new InvalidOperationException("Reserve changed after transaction preparation.");
            _power = debit.After; _revision = debit.NextRevision;
        }
    }
}
