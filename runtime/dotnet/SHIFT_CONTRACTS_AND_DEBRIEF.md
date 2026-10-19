# Shift contracts and debrief

Session Domain owns one optional `ShiftContract` per world epoch. Setup registers
an immutable `ShiftContractDefinition` containing 1–32 named demand windows.
The final window must end at the configured shift deadline. Quotas measure grid
**energy delivered within each window**, not continuous power. Surplus cannot
prepay a later window or repair a missed earlier one.

Application observes the existing Power owner's cumulative delivery. It splits
host advances at every crossed demand boundary; a generation quantum completed
at the endpoint belongs to the ending window. Production and reactor settlement
precede terminal result publication. A settlement exception faults the world.
All windows met yields Succeeded; any missed window yields Failed. Without a
contract the existing TimedOut result remains. An unfinished contract rejects
manual success without changing the world. Abort, host loss and failure remain
explicit terminal paths. Pause consumes neither contract time nor delivery.

`ShiftContractView` exposes detached current/upcoming demand and settled results.
Warnings announce the immediate next window at its authored warning time. The
sandbox's twelve-minute, four-window contract is a development fixture; its
numbers have not been accepted as balance or validated for player feel.

`WorldSession.Debrief` is null while active, then freezes once after settlement
and cleanup. It contains canonical terminal material/power summaries, the
contract result, worker condition captured before roster removal, diagnostic
incident totals and a retained chronological incident timeline. It is a read
projection and cannot spend power, consume materials, inflict injury or repeat
an accepted operation. Stop after End does not overwrite it. Restart starts
with fresh objectives, counters and no debrief.

Incident totals are updated only for committed changes. Replays, duplicate
hazards, blocked standing attempts and NoChange cannot inflate them. The
`BypassedConversions` counter means completed machine conversions that used
bypass; a jammed/cancelled cycle is not a completed conversion. `Incapacitations`
counts newly applied incapacitating impacts. `StandingRecoveries` does not mean
medical reanimation. Production's completed conversions also include reactor
fuel conversion to spent material. `Stabilizations` counts explicit Aid commits;
powered treatment has its separate `Medical.CompletedCycles` summary. These are
different operation counts. No profit or compliance statistics are invented for
systems not yet implemented.

The incident journal retains up to min(trace capacity,128) significant events,
independently of the raw diagnostic trace's routine samples. Retention selects
the latest occurrence times; equal times use recording sequence. The debrief
shows dropped incident details explicitly while aggregate counters survive
eviction. Counters saturate with a visible flag. Diagnostic sequence exhaustion
continues aggregate counting and records lost details without faulting gameplay.
Machine jam/completion timestamps use actual completed work from the prior clock
sample; reactor/demand events supply their own occurrence times.

The sandbox terminal HUD reads this frozen timeline. Its engine-free formatter
and tests are linked from their canonical Unity source into the offline test
assembly; source hashes include those links. This validates their pure logic,
not Unity compilation, GUI rendering or native Player behavior. Full native
deadline/restart and trace tests remain in the native manifest. Current execution
evidence and the Unity availability blocker are in
[SHIFT_GAMEPLAY.md](../validation/SHIFT_GAMEPLAY.md).
