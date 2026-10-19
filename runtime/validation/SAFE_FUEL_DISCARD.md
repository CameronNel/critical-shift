# Safe partial fuel discard, 19 October 2026

Branch `codex/safe-fuel-discard-20261019`, based on draft PR135 `25ed108c`.
Root is sole author. Independent ultra reviews cover reactor/material accounting,
retained evidence, the input-driven model and Unity command composition.

A worker can shut down the reactor, keep cooling open and wait for instability
at or below its reset threshold, then explicitly discard the remaining fuel.
The full original quantity becomes spent fuel and its container is released.
Remaining running time is forfeited, without output, startup refund or a new
material-history reservation. This permits replacing suspect partly used fuel.
The ordinary eject command keeps its unused/exhausted semantics. N and the
reactor panel expose the distinct destructive action with explicit lost-time
and no-refund wording; this is prototype gameplay, not balance acceptance.

The existing guarded Reactor owner validates its exact pending conversion,
current slotted input and checked accounting before exact custody admission.
A stale object revision rejects before conversion. Accepted discard finishes
the existing reserved full-yield Fuel→SpentFuel plan once, installs Empty and
publishes an immutable event with original cycle, input, cause, output and lost
milliseconds. Completion counting is idempotent. The core retains its sample
clock and cooling; new fuel has zero work. Output routing, power and running
backup remain intact. Existing pause, access, worker, revision, sequence and
epoch admission apply; historical retries cannot discard newly inserted fuel.

S01/S02/S03/S05/S07/S08, TX/POWER/CAUSE/LIFE:25 focused pure cases passed,
covering zero/partial work, all wrong modes, cooling and inclusive thermal
threshold, dirty/bypassed lineage, full quantity, stale custody, exhausted
history, replay after reload, backup/routing, pause/range, malformed payloads,
idempotent completion, readouts and detached debrief after raw trace eviction.
The18-step versioned discard/reload/retry/restart scenario passed twice with73
assertions per run, including command outcomes and teardown checks.

The separate authored-input model predicts first-cycle quanta, allocation,
spill, thermal waiting, paused clocks, lost duration, material lineage and the
new cycle's first quantum. It checks the single typed event and detached
terminal incident. Its omitted-spent prediction control fails the named
material invariant. Model counts describe selected operations/checks, not
distinct assertions. Full frozen verifier and10,000-case results are appended
after the exact committed candidate is checked.

One native physical release case and the real debounced N/O/V dispatch case
are authored. Catalogue179. All current Unity import, physics, rendered UI,
Player, multiplayer and performance execution remain NotRun: the pinned editor
is unavailable locally and the configured remote is Offline. Source parsing
does not establish Unity binding or runtime correctness. Draft awaits
independent maintainer review/merge; no acceptance gate advanced.

Final candidate `91df0439ac4ec8f3f0d1b982a0de03d70649b304` passed the full
verifier13:39:30–13:40:13UTC: **1208 executed/passed, zero failed/skipped;
28 scenarios each twice**. The new omitted-conversion control and all existing
negative controls were rejected. All284 recorded inputs match that git tree;
nine DLLs match the frozen closure in ignored
`out/safe-discard-verification-20261019`. Final frozen seed20261064 passed
10,000 mixed cases/15,615,906 selected operations and model checks in39.254191s.
Tooling182 and static204 GUIDs/21 asmdefs/133 C# checks passed. C#8 syntax
parsing covered79 Unity-side files with zero errors, without binding or native
execution. Review also caught and root fixed action-less replay cooling guidance
that incorrectly described a discard as starting the reactor. Current native
cases remain NotRun; draft awaits independent maintainer review/merge.
