# Timed protective suit fitting

An authored suit station gives an authenticated worker a preparation-time route
to an intact protective suit. Workers owns the suit and pending immutable attempt;
Application coordinates station access, occupancy, receipts, settlement and
teardown. [Task evidence](../validation/TIMED_SUIT_FITTING.md) records executed
checks and native limitations. This is a fictional gameplay procedure.

```csharp
// Setup only; station identity shares the existing equipment target namespace.
world.SuitFitting.Register(stationId, new SuitFittingDefinition(20000));
// After start, the existing connection-bound port derives its own worker/revision.
commands.OperateSuitFitting(stationId, SuitFittingAction.Start);
commands.OperateSuitFitting(stationId, SuitFittingAction.Cancel);
```

Each of at most eight stations authors a 15–30-second shift-time duration.
Start requires Alert/Upright, empty hands, current worker revision, available
station and trusted current access. One wearer occupies a station. Already
Intact returns NoChange. The command contains no target worker, desired suit,
duration or asserted completion. A new accepted start receives a fresh attempt
ID and its entire authored duration.

While fitting, ordinary voluntary movement, grabs and equipment work are busy.
Gravity and physical impact eligibility use physical upright state separately,
so fitting cannot confer hazard immunity or suspend an airborne worker. The
temporary fixture's explicitly labelled diagnostic controls retain their existing
direct host purpose. Own exact-attempt Cancel remains usable while busy, paused
or out of reach. A stale cancellation cannot stop a later attempt.

None/Compromised retain their original PPE until exact completion sets Intact.
Contamination, injury cause, posture, recovery facts and object custody are
preserved. Safe contamination-only revisions do not restart progress. Impact,
trusted suit replacement, observed access loss and disconnect interrupt; any
cancelled/interrupted progress is discarded. There is no removal, suit stock,
physical inventory or permanent movement/stamina penalty in this slice.

The world samples current station access once at each poll's projected, capped
shift coordinate before settling historical boundaries. An invalid current
sample conservatively interrupts even an overdue attempt at that current
coordinate; unrelated backup/contract boundaries cannot backdate the observation.
Valid completion settles at its exact due coordinate before terminal publication.
These sampled observations do not prove continuous physical presence. Pause
freezes progress while permitting current access loss or explicit cancellation.

Start/Cancel/Complete/Interrupted records include attempt identity, worker
revision and occurrence time. Impact interruption retains its actual hazard and
cause separately from fitting-cycle identity. The bounded incident journal and
debrief retain these records after ordinary trace eviction. Teardown counts
pending work as terminal cancellations and retires live workers without checked
gameplay cancellation. Historical cutoff roster facts may still describe a
pending attempt. Terminal count addition saturates explicitly with
CountersSaturated rather than blocking cleanup during arithmetic failure.

Canonical sandbox station 710 uses a 20-second duration and the existing host,
access binder and temporary GUI. Its simple locker sits at (-9, 0, -5). Unity
import, Player, movement/contact behavior, GUI, physical reach and multiplayer
remain NotRun. Fixture values remain prototype parameters under D-09.
