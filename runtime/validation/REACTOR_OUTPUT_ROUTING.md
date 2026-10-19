# Routing newly generated reactor output, 19 October 2026

Branch `codex/reactor-output-routing-20261019`, based on draft PR133 `6b343cce`.
Root is sole author; independent ultra reviewers inspect reactor ownership,
boundaries, native composition, readout advice and the input-driven model.

The reactor equipment setting selects Balanced (the unchanged authored split),
GridPriority (all new output to grid) or ReservePriority (all to reserve). The
ReactorOperations owner already allocates new core quanta and owns its installed
PowerAccount; it now owns this setting. The immutable Core retains fuel/work/risk
and quantum timing. No second power or material ledger is introduced.

Each newly completed quantum conserves authored reserve+grid output. Partial
work persists across switches: switching at99ms in a100ms quantum redirects the
whole newly completed quantum at100ms. Previously completed output stays settled.
Host commands pump first: at an exact demand endpoint, the endpoint quantum and
old demand window settle before the valve change. No client timestamp, hidden
clock, direct reserve export, per-frame integration or new cutoff is added.
Full reserve spills excess; it does not redirect it to the grid. Initial and
backup energy remain reserve-only. Routing persists through trip/reset, shutdown,
restart and fuel replacement within one world; new composition defaults Balanced.

A typed appended action/event and optional neutral-default request field retain
the existing authenticated sequence/revision, spatial/worker, retry and malformed
payload admission. Changing routing alone spends/generates nothing. NoChange
and historical retries cannot rewrite the current valve. Definition rates/costs/
thresholds and Core interlocks are immutable projection facts, not full command
admission guarantees. Existing actual command results remain authoritative.

The console offers V and explicit panel buttons. A pure readout shows current
allocation, remaining running-fuel time, reserve capacity/spill, startup/emergency
costs and actionable cooling/reset/exhausted-fuel guidance. Backup advice checks
charges, running state and whole-charge headroom. The source formatter does not
submit commands. Trace/debrief retain the routing event with its original cause.
No physical room/body/binding/observation count is added.

S01/S02/S03/S05/S08, POWER/TX/CAUSE/LIFE evidence:33 new focused routing/readout
cases passed. They cover quantum99/100/101, exact quota endpoint[4,5,0], default
balance, all-route conservation/fuel, full reserve spill, simultaneous core-before-
backup storage, current access/revision, pause, retries/mismatched routing payload,
trip/reset/reload persistence and partitioned sampling. Pure readouts check
custom authored costs/rates, strict/inclusive thermal thresholds, depleted or
headroom-blocked backup and frozen snapshots. The new versioned scenario passed
twice:16steps/53assertions per run, including teardown checks.

A separate input-driven routing soak predicts work, due quanta, current route,
reserve/grid/spill, paid restarts, pause and reserve-only backup. It checks
aggregate state and fuel lineage; it does not establish event-publication
coverage. The forced ReservePriority quantum makes an intentionally ignored
route fail the named independent allocation invariant, even if reserve rate is0.
Preliminary seed20261057 passed10,000 mixed cases/15,422,859 selected operations
and model checks in40.9133582s; final frozen evidence follows verification.
Counts are aggregate model work, not15.4million distinct assertions.

Existing182 tooling cases and static204 GUIDs/21 asmdefs/133 C# checks passed.
A C#8 syntax-only pass parsed79 Unity-side files with no syntax errors; this is
not reference resolution, Unity compilation or execution. One new native console
case declares spatial admission and pump-before-routing timing; catalogue175.
Native import/PlayMode/physics/rendered controls/Player/performance/multiplayer
remain NotRun because pinned Unity is unavailable and the remote is Offline.
Draft pending independent maintainer review and merge; no acceptance gate or
fictional balance acceptance is advanced.

Final candidate `0d8274635421d9f320c0eb15eb632f5ac24a54ab` passed the full
verifier12:59:09–12:59:48UTC: **1154 executed/passed, zero failed/skipped;26
scenarios each twice**. Existing controls and the named ignored-routing control
were rejected. All279 recorded inputs match that git tree; all nine DLL hashes
match the frozen closure in ignored `out/reactor-routing-verification-20261019`.
Final frozen seed20261058 passed10,000 mixed cases/15,429,160 selected
operations and model checks in38.3388238s. Ultra source reviews
found no remaining concrete core or native-composition blocker. All current
native behavior remains NotRun; draft awaits independent maintainer review.
