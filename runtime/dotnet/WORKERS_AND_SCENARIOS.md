# Workers, recovery and offline scenarios

**OFFLINE-003, updated by OFFLINE-004 | 8 September 2026 | Engine-independent implementation**

Requested scope: worker condition/recovery, coordinated possession cleanup, a bounded diagnostic trace and a runnable scenario tool. This work is based on PR #41 at `63f81a5e31c10c4a5569f3616828c67313466dfc`, which itself depends on PR #40. Follow the active PR for tested revisions and independent-review status. No Unity/physics/multiplayer gate is advanced by these files.

## Ownership and dependency decision

`Features.Workers.Domain` owns consciousness, logical posture, suit condition, contamination and recovery identity/deadlines. It references base libraries only, not Interaction or Session. `Application/WorkerWorkflow.cs` coordinates worker operations with the EXISTING InteractionWorld; no second custody or connection store exists. WorldSession owns construction, clock, epoch, revision and teardown. A successful setup connection automatically registers a worker; disconnect removes that worker and cancels its actor-ID timer group.

`WorldSession.Workers.cs` is part of the SAME WorldSession type, not another session. It routes worker requests through the existing epoch/readiness/reentrancy guard. Count both partial files together in complexity reviews. This facade now exceeds the approximate 400-line review trigger; the bounded justification is shared readiness and lifetime, with worker algorithms extracted to WorkerWorkflow/WorkerState. Do not add inventory/reactor logic to this facade. Independent review must assess that boundary before accepting further growth.

The new scenario executable references Application only. Production assemblies cannot reference it. No production package was added; existing .NET Standard 2.1/C# 8.0 and test-only dependencies remain. These local decisions implement the user-authorized offline-prework scope without selecting Unity transport, UI, save or physics packages.

## Worker calling contract

All methods run on the same trusted host thread after advancing WorldSession's absolute monotonic host clock. Worker deadlines use its pause-sensitive shift time, not a separate clock and not the advisory timer queue. Inputs carry their ORIGINAL world epoch. Trusted host observations/aid/environment updates must not be exposed directly as unvalidated client authority.

Consciousness (Alert/Unconscious), logical posture (Upright/Down/Recovering), suit (None/Intact/Compromised) and contamination (integer 0..100 abstract test/configuration units) are separate. Contamination/suit values do not currently apply damage, medical effects or suit protection calculations. No hit points, injury simulation, physical ragdoll, body dragging or reanimation economy is claimed.

- `ApplyWorkerImpact` requires explicit hazard/cause IDs and the next positive sequence for that worker/hazard pair. Repeating a retained source sequence with the same severity/delay/cause is Duplicate; changed payloads, old sequences and forward gaps are rejected. Independent hazards have separate streams. Up to 32 sources are retained per worker; exhausted source capacity rejects new sources without evicting replay protection. An actually new impact starts a new recovery episode. A minor hit cannot wake an unconscious worker. [PRODUCTION.md](PRODUCTION.md) records this PR #42 review repair.
- A newly applied impact releases that worker's existing claim through the existing custody owner WITHOUT disconnecting the player. Both logical changes finish before a result is returned. Unexpected integrity failure faults/clears the world instead of allowing a partial transaction to continue. The returned released-claim view must later drive physical cleanup; no joint was removed by this offline module.
- Down/unconscious/recovering workers cannot Grab or Renew. Rejections go through the existing interaction receipt stream, so later valid input is not wedged. Release remains possible. Historical successful interaction receipts still do not imply a new commit.
- `StabilizeWorker` is an explicit trusted aid authorization against the current worker revision. It restores alertness and establishes a new cooldown/episode, not automatic standing. It does not charge resources or implement revive/medical equipment. Repeating an old revision cannot apply aid twice.
- `SetWorkerEnvironment` checks the expected revision and bounds. It does not overwrite consciousness/posture. These independent facts survive impacts and recovery.

## Two-phase recovery and missing responses

A conscious Down worker can `BeginWorkerRecovery` only after RecoveryNotBeforeMilliseconds, for the current episode AND expected revision. The worker becomes Recovering and receives a new attempt token. A matching retry while that attempt remains pending is Duplicate, not another attempt or a restarted deadline. A denied/cancelled attempt requires a new revision to start again.

`CompleteWorkerRecovery` requires the original epoch/worker/attempt and asks the supplied `IWorkerRecoveryPolicy` for actual clearance. No production default returns Safe. No provider means ClearanceUnavailable and a return to Down; a blocked pose likewise returns Down. A stale token never invokes the provider. A new impact invalidates an in-progress recovery, preventing a delayed callback from standing an incapacitated worker.

`CancelWorkerRecovery` can abort the matching pending attempt, including during pause. Pending recovery also has a bounded completion window: default 5,000 shift milliseconds, constructor-configurable from 1 to 60,000. This is an offline integration timeout fixture, not final animation/network tuning. AdvanceTo scans this stored deadline directly, returns expired worker changes in WorldAdvanceResult.WorkerChanges and leaves the worker Down for a fresh request. Missing or cancelled advisory prompts cannot suppress expiration. Pausing stops both recovery cooldown and this completion window; real-time claim expiry still continues.

World timeout/finish/Stop/fault clears the worker roster along with claims/timers. Restart explicitly accepts new access and recovery policies and creates a new epoch; it does not silently retain an old engine clearance provider. Old observations, recovery callbacks and disconnects cannot modify the successor. A terminal snapshot still requires full engine-binding teardown when an engine adapter exists.

## Diagnostic trace

WorldSession.Trace returns a detached, read-only snapshot of a fixed-capacity ring. Default capacity is 128 records, configurable 1..4096. Overflow drops oldest records and increments a visible dropped-record count. Sequence-counter exhaustion is visible and cannot overflow into gameplay failure. Old-session terminal evidence is retained within that bounded instance; the successor starts a fresh trace.

Records use typed event/result fields and IDs, original request epoch, host/shift time, world revision, worker before/after revisions and recovery/impact correlation where applicable. The causal key for worker recovery is `(epoch, workerId, hazardId, impactSequence)`, with explicit cause ID, not an unscoped sequence number. No arbitrary message string, exception payload, credential, voice or filesystem path is accepted by the runtime recorder. It runs no callback and changes no gameplay state. Reading it does not advance time or revision.

This is scoped diagnostics, not an event bus, durable audit log, save file, full incident history or completed debrief. Dropped records mean history is incomplete. Operational resource transfers must never depend on the trace. The scenario tool writes its own bounded result report; that is developer evidence, not a player save.

## Run actual scenarios without Unity

From `runtime/dotnet/`:

```sh
python tools/verify.py
```

This runs the existing tests AND builds/runs the scenario executable. To run one script directly after initial restore/build:

```sh
dotnet run --project tools/CriticalShift.Scenarios --configuration Release -- --scenario scenarios/worker-recovery.json --report artifacts/manual-worker-recovery.json --repeat 2
```

**Report output is create-new only:** an existing path, including an alias of the input, is rejected without replacement. Use a new report filename on repeated manual runs. Automated alias tests cover this behavior.

The command-line tool executes versioned JSON actions against the actual WorldSession/Interaction/Workers libraries. It creates four logical worker identities and one crate, advances explicit time, checks expected statuses and state assertions, and returns a nonzero exit on mismatch. Limits are 256 KiB input, 512 steps and 50 repetitions. Scenario seed is configuration metadata; these scripts do not claim procedural worlds or random network traffic.

Worker scripts included (the additional production scripts are listed in [PRODUCTION.md](PRODUCTION.md)):

| Script | Behaviour exercised |
| --- | --- |
| worker-recovery.json | Crate contention; unconscious holder cleanup; environment preservation; aid; blocked and successful recovery; rejection sequencing; stale input after restart |
| pause-and-expired-recovery.json | Shift pause versus real-time claims; cooldown; missing recovery response; stale completion; terminal cleanup |
| cleanup-and-trace.json | Cancellation during pause; fresh recovery attempts; bounded trace; restart; old-epoch disconnect; worker removal |

Each script contains explicit expected outcomes. The verifier checks exact script discovery, runs, steps and assertion totals from expected-scenarios.json. It also runs an intentionally incorrect assertion and a zero-step script, which must fail. Passing test declarations or a green deploy preview are not evidence of successful scenarios.

`ScriptedPolicies` exists ONLY in the tool: spatial access is synthetic and the script supplies synthetic recovery clearance. This proves logical orchestration, not authentication, pose safety, character feel, physics or connected multiplayer. The tool explicitly labels that distinction in reports and console output.

## Checks, review and remaining work

WorkerRuleTests cover identity/retry/gap handling, independent dimensions, bounds, cooldown, aid, stale attempts, two-phase confirmation and expiry. WorkerWorldTests exercise custody cleanup, paused recovery, missing/throwing/reentrant providers, restart/disconnect and trace behaviour through the real application. Existing tests remain intact. Compiled/public-API checks include the worker assembly and immutable views; guard controls reject a worker-to-peer-domain reference and a production-to-runner dependency.

The read-only CI workflow now retains the exact first-party verification inputs as well as logs/results, with 30-day artifact retention. Preserve required evidence beyond that retention before accepting a formal milestone. No branch protection or deployment setting is changed.

No old active implementation is replaced: WorldSession/InteractionWorld are extended, not copied. No source art, textures, assets, engine metadata or supported save schema is removed. These files do not prove absence of all dead code or architectural defects. Remaining gates include independent review, actual Unity import/AOT/Player compilation, host input authentication, real clearance and physical cleanup, network replication, movement and human feel testing.
