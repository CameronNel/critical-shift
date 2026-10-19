# Timed protective suit removal, 19 October 2026

Branch `codex/timed-suit-removal-20261019`, based on draft PR134 `d6584d01`.
Root is sole author; independent ultra reviews cover target/duration admission,
clock/replay/lifecycle, native input composition and the generalized model.

Players can now remove worn PPE at the existing locker to regain normal walking.
The appended Remove action maps on the server to None; Start still maps to Intact.
No client target field is accepted. The existing Workers-owned attempt captures
immutable OriginalSuit and TargetSuit plus its complete selected deadline. Only
exact completion changes gear. Original protection and800-permille walking
remain throughout removal; successful removal yields None/1000. Contamination,
injury history, material/custody/power and exposure cooldowns stay unchanged.
This removes equipment only; it does not wash the worker or simulate clothing
inventory. Fitting keeps its15–30s bounds; removal is independently authored,
default5s and bounded1–15s. Prototype tuning is not balance acceptance.

Start/Remove share revision-bearing, no-attempt payload admission. Only exact
own-attempt Cancel retains the existing busy/paused escape path. Free hands,
station occupancy, sampled current access, immediate impact/suit-replacement
interruption, contamination-only progress, deadline and terminal behavior reuse
the fitting workflow. Historical removal cannot remove a later fitted suit;
old cancellation cannot stop its successor. Target-specific overflow guards
allow the shorter operation near the maximum shift clock.

O focuses removal through the existing host command path; the panel uses the
same typed action. E/R retains fitting. Pending text and trace events distinguish
removal; the debrief labels aggregate suit station work. Ultra review caught an
O/V dispatch mistake, which root fixed. A native regression now invokes the real
HUD input handler and spies separate, debounced removal/routing callbacks.

S01/S02/S03/S07/S08, WORKER/HOLD/LIFE/CAUSE:29 new removal cases and40 existing
fitting cases passed. Coverage includes both worn suits,4999/5000ms, original PPE
contacts and cooldowns, no-op/busy/hands/occupancy/range, pause cancellation,
late observed access loss, both impact types, suit replacement, opposite-action
retry, stale cancel, malformed payloads, cutoff±1ms, exact long.MaxValue completion,
invalid domain target, retained injury and operation-specific trace/debrief.
The21-step versioned removal/refit/contamination/pause/restart scenario passed
twice with79 assertions per run including teardown checks.

The input-driven fitting model now predicts both targets and independent captured
durations. Every lifetime forces a completed removal before random interleavings;
Started/pending/Completed/Interrupted/Cancelled projections check original/target
suit and exact attempt times. The removal-ledger control deliberately omits the
first predicted None assignment and fails the named protection invariant; the
existing fitting-ledger still checks the first Intact completion. Preliminary
seed20261060 passed10,000 mixed cases/15,455,319 selected operations and model
checks in39.0729674s. These counts are aggregate work, not distinct assertions.

Tooling182 passed; static checks204 GUIDs/21 asmdefs/133 C# passed. Supplementary
C#8 syntax parsed79 Unity-side files with zero syntax errors, without reference
resolution or native execution. Three new native cases cover physical locker
completion/access and actual O/V dispatch. Catalogue178; all current native
import, physics, rendered controls, Player/performance/multiplayer remain NotRun
because the pinned editor is unavailable and the configured remote is Offline.
Draft awaits independent maintainer review/merge. No acceptance gate advanced.

Final candidate `8c1b59caeacd440a0d933bca4eb8aef97ec4ed12` passed the full
verifier13:17:07–13:17:49UTC: **1183 executed/passed, zero failed/skipped;27
scenarios each twice**. Existing controls and the named omitted-removal control
were rejected. All281 recorded inputs match that git tree; nine DLL hashes
match the frozen closure in ignored `out/suit-removal-verification-20261019`.
Final frozen seed20261061 passed10,000 mixed cases/15,448,743 selected
operations and model checks in42.9084003s. Ultra source reviews
confirmed the O/V correction and found no remaining concrete blocker. Current
native cases remain NotRun; draft awaits independent maintainer review.
