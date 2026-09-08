# World/session, shift clock and timers

**Task OFFLINE-002, 8 September 2026.** Authorized scope: useful world/session/time coding without Unity. Dependency: PR #40's interaction implementation at `1d43c02eb318e3dd5879ccd14b8e0a8f8da68e83`. Implementation and test sources exist; consult the current PR for actual execution/independent-review status. No engine or multiplayer gate advances.

## State ownership and scope

WorldSession is an Application coordinator for exactly one shift. SessionTimeline owns phase, outcome, elapsed shift time and the supplied host-time coordinate. WorldTimerQueue owns pending advisory one-shot signals. The existing InteractionWorld continues to own connection admission/receipts and delegates custody to ExclusiveClaimStore. No feature domain depends on a peer domain.

This is the logical world lifetime, not a 3D world generator or scene loader. The stored seed is configuration for later feature consumers; no RNG or procedural geometry is introduced. Currency, production quota and reactor success rules are not invented here.

## Lifecycle contract

Create immutable WorldSessionConfiguration with an explicit positive duration in milliseconds. Construct WorldSession with a non-null trusted access policy, bind the setup roster/entities, then call Start with the current nonnegative unscaled host timestamp. Lobby time is not deducted from the shift. At least one connected actor is required; object/connection registration closes at Start.

Phases are Setup, Running, Paused, Ended, Stopped and Faulted. An explicit host operation can finish with Succeeded, Failed, Aborted or HostLost. Reaching the configured duration produces TimedOut. Time expiry is not automatically quota failure or meltdown. Unexpected integrity/access-policy exceptions produce Faulted, clear owned resources and propagate the error. The first terminal outcome is retained through Stop and cannot be overwritten by later finish requests.

WorldSessionView is detached and immutable. Epoch identifies this world; Revision orders changed session snapshots even when the host clock has not moved. Reads do not advance revision. Object state has its own authoritative object revision; the world snapshot is not a mutable copy of all objects. Results/views can be stale and must not be used as authority for new commands.

## Two clock coordinates

- **RealTime:** supplied monotonic, unscaled host milliseconds. This continues while the shift is paused, including ownership expiry and real-time advisory timers.
- **ShiftTime:** elapsed active shift milliseconds, capped at the configured duration. It stops during pause and resumes without charging the paused interval.

AdvanceTo accepts an absolute host coordinate, not delta time. Duplicate samples do not double-count elapsed time; backwards samples are rejected before mutation. Large forward jumps clamp the countdown safely. No client timestamps, wall-clock date or hidden system-clock read determines domain state.

The caller must continue advancing host time during pause and must sample before applying pause/resume. Controls operate at the last processed sample. Pause is disabled by default and requires explicit configuration opt-in; this is not a silently chosen multiplayer pause/voting feature. While paused, new grabs are rejected through the existing terminal receipt stream, while release and host-approved lease renewal remain possible.

## Advisory one-shot timers

Schedule takes the expected world epoch, a stable owner-group ID, a 1-64-character signal label, nonnegative delay and an explicit time basis (ShiftTime by default). Labels are scoped data interpreted by the owner, not global event-bus topics or reflection handler names. The returned immutable handle contains epoch and sequence. A full queue returns TimerCapacityReached without evicting another timer; default capacity is 128 and maximum configurable capacity is 4096.

AdvanceTo returns due signals; it never invokes a delegate. Zero delay means next poll, not immediate/reentrant execution. Within a batch, real-time signals precede shift-time signals; each group sorts by deadline then creation sequence. The two clock coordinates do not imply one global chronological order across pause. Each signal is dequeued at most once from the queue. Consumer processing is not crash-durable or exactly-once delivery.

CancelTimer validates the full handle. CancelTimersForOwner explicitly clears pending signals for an owner group. Retiring a registered object through WorldSession also cancels the group matching that entity ID. With OFFLINE-003, Disconnect releases the connection's claim, removes its registered worker, and cancels the timer group matching that actor ID. Other machine/group timer lifetimes still require explicit owner cancellation; they are not inferred from a connection. Cancellation cannot retract a batch already returned to a caller.

**Deadline priority:** when an advancement reaches shift duration, the shift ends first, and all pending advisory signals are discarded, including ones overdue in that batch. There is no hidden catch-up burst after end. These timers are therefore for warnings/countdowns and advisory prompts, not guaranteed material transfers, resource spending or causal incidents. Such required effects need their separately specified workflow/commit semantics. Recurring timers, durable schedules and task retries are intentionally not implemented.

## Required production outcomes

[OFFLINE-004 production](PRODUCTION.md) does not use advisory timers. World advancement commits machine work due by the capped shift deadline before terminal cleanup, then discards pending advisory signals as before. Unfinished production is cancelled with input quantities retained in a detached terminal accounting summary. This is logical accounting, not persisted or physical inventory.

## Teardown and restart

Finish, timeout, fault and Stop clear pending timers, logical claims, connection receipts and registered object state. EndedThisAdvance is true only on the tick that first times out. A terminal snapshot means a future engine adapter must tear down ALL bindings; an empty ReleasedClaims list on termination is not permission to retain joints or visuals.

Restart requires an explicitly supplied access policy for the new world. It returns one fresh setup-only successor with the same immutable configuration and a newly generated epoch. Roster/entity registration, timers, receipts, claims and clock origins do not transfer. A given instance creates at most one successor; reusing a stopped instance is not a restart. Tests exercise 50 consecutive restarts.

World control requests, attachment callbacks, timer handles and disconnect callbacks carry the originating epoch. Old-epoch input is rejected against a successor, even if logical entity/connection IDs are reused. Do not replace a delayed message's old epoch with the current one. Trusted composition methods such as Start/Stop/Restart are not exposed as raw client-authority APIs.

## Validation mapping and remaining work

TimelineTests cover origin, pause/resume, invalid time, deadline, finish, overflow boundaries and chunking. TimerTests cover independent clocks, ordering, exact-once dequeue, cancellation, capacity, overflow, immutable batches and 100 seeded sequences of 200 list-oracle actions. WorldSessionTests cover real interaction expiry while paused, rejection sequencing, cleanup, snapshot versions, stale callbacks, roster churn, fault paths and fresh-policy restarts. Existing interaction tests remain in the positive suite.

The graph/public-API/static-state checks now cover the session, interaction, worker and Application libraries and generic/array-wrapped domain exposures. Clock-read and peer-domain negative fixtures prove the new source checks can reject deliberate violations. These are scoped checks, not a proof of complete architecture correctness.

Still unverified: actual engine clock sampling, pause UI, physical cleanup, player movement, transport ordering/authentication, replicated session views, multi-client timing and supported Unity/Player compilation. No claim is made that a timer test proves real multiplayer or that a seed generates the physical facility.

## Technical rationale

Microsoft documents that [threading timers](https://learn.microsoft.com/en-us/dotnet/standard/threading/timers) execute callbacks on ThreadPool threads, and that callbacks can remain queued around [timer disposal](https://learn.microsoft.com/en-us/dotnet/api/system.threading.timer.dispose). This implementation instead uses explicit single-threaded polling and returns data. A future host adapter can supply elapsed measurements using an appropriate monotonic source; [Stopwatch](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.stopwatch) documents elapsed measurement facilities. No such adapter or timer thread is installed here.

## Worker integration (OFFLINE-003)

[WORKERS_AND_SCENARIOS.md](WORKERS_AND_SCENARIOS.md) documents the worker extension. WorldSession now composes a worker owner as well as the existing interaction owner. `WorldAdvanceResult.WorkerChanges` reports expired recovery attempts; readiness and expiry are stored worker facts, not advisory timer callbacks. Teardown clears workers too. Restart must explicitly rebind physical recovery policy as well as access policy; an omitted recovery provider cannot approve standing. The bounded diagnostic trace is retained on the stopped instance for failure inspection and starts fresh in the successor. None of these additions implement engine physics or connected multiplayer.
