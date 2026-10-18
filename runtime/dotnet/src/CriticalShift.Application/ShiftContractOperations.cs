#nullable enable
using System;
using CriticalShift.Features.Session.Domain;

namespace CriticalShift.Application
{
    /// <summary>One Session-owned objective; delivery is read from the existing Power owner.</summary>
    public sealed class ShiftContractOperations
    {
        private readonly WorldSession world;
        private ShiftContract? state;
        private ShiftContractView? terminal;
        internal ShiftContractOperations(WorldSession session) => world = session;

        public ShiftContractView? View => terminal ?? (state == null ? null :
            new ShiftContractView(world.Epoch, state, world.View.Phase, world.View.Outcome));
        public void Register(ShiftContractDefinition definition) => world.RegisterContract(definition);
        internal bool Configured => state != null;
        internal bool ReadyToSucceed => state?.AllPeriodsMet == true;
        internal long NextBoundary => state?.NextBoundaryMilliseconds ?? long.MaxValue;
        internal void Configure(ShiftContractDefinition definition)
        {
            if (definition == null) throw new ArgumentNullException(nameof(definition));
            if (state != null) throw new InvalidOperationException("One shift contract may be registered.");
            if (definition.DurationMilliseconds != world.Configuration.ShiftDurationMilliseconds)
                throw new ArgumentException("The final demand boundary must equal the shift deadline.", nameof(definition));
            state = new ShiftContract(definition.Rules);
        }
        internal GridDemandChange? Observe(long elapsedMilliseconds)
        {
            if (state == null) return null;
            int closing = state.SettledPeriods;
            if (!state.AdvanceTo(elapsedMilliseconds, world.Reactor.PowerSummary?.Delivered ?? 0)) return null;
            return new GridDemandChange(world.Epoch, state.Plan.Id, new GridDemandView(state.Snapshot()[closing]));
        }
        internal TimelineOutcome DeadlineOutcome
        {
            get
            {
                if (state == null) return TimelineOutcome.TimedOut;
                if (!state.Complete) throw new InvalidOperationException("The final demand window was not settled.");
                return state.AllPeriodsMet ? TimelineOutcome.Succeeded : TimelineOutcome.Failed;
            }
        }
        internal void Close()
        {
            if (terminal == null && state != null)
                terminal = new ShiftContractView(world.Epoch, state, world.View.Phase, world.View.Outcome);
        }
    }
}
