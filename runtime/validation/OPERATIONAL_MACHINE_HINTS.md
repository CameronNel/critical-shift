# Readable machine tradeoffs and interlocks, 19 October 2026

Bounded branch `codex/operational-machine-hints-20261019`, based on
`cf2508bff26692e9f2c80d49481062d3cc8d8040` (draft PR #124).
Primary author: Codex. Independent read-only ultra audit: `identify_repo`;
composition/source review: `review_composition`. The owner authorizes continued
useful game implementation without questions.

Purpose: expose actual authored recipe tradeoffs and the next valid machine
action, following GAME_SPEC 11.3/26.2. Fix focused hints that tell players to
toggle power in the wrong direction after isolation/restoration. Keep text
derived from detached canonical state. No tutorial progress owner, gameplay
rule change, package, input framework or new domain is introduced.

Expected scope: immutable recipe/current-cycle facts in MachineView, one pure
shared presentation formatter, existing focused controls and temporary HUD,
offline linked formatter checks and source/consumer review. MachineState,
material/custody and world/session remain canonical. S01/S02/S03/S05/S08 and
TX/CAUSE/ARCH/UI validation apply. No serialized identity is removed.

Planned checks: truthful normal/bypass/drying values, state-aware powered/off
jam/paused/output hints, useful rejection text, retained historical reply
semantics, immutable projections and unchanged canonical state, native consumer
source review and full verifier. Unity import, keys, GUI, physical feel and
multiplayer remain NotRun. D-09 timing/moisture values remain prototypes.

## Intermediate checks and review

All 20 targeted readout/projection cases passed, with zero failures/skips.
The initial build had zero warnings/errors. Static source checks passed 195
metadata GUIDs, 21 asmdefs and 124 production C# files. Focused cases use actual
Application commands and detached snapshots to exercise recipe facts, equal
normal/bypass durations, inherited suspect input, current/historical bypass,
jammed/paused/output/idle power combinations, wet/power rejections, safe drying,
historical started replies and locale-stable fractional seconds.

Independent read-only ultra composition review found no concrete blocker.
Recipe is sealed/getter-only; aliases derive from it and current bypass comes
from the reserved plan/completed receipt. Bootstrap binds public pure formatter
methods through the existing host, then teardown clears those delegates. No
assembly edge was added. The offline test project links the canonical formatter
source under the same explicit boundary guard used for other shared readouts.
Unbound synthetic native-host fixtures retain their prior raw-result fallback.
Neither the reviewer nor these offline checks ran native controls or GUI.

Root authored all changes. Full verification is pending. Machine simulation,
timing, input reservation, custody and resource rules are unchanged by this
slice. The ongoing long probes remain attributed to their older frozen sources.

## Final full verification

Source `ba084341247ee621e6ad25ebe2769532115e1854` passed the verifier from
2026-10-19T10:21:20.281135+00:00 to 2026-10-19T10:21:53.866567+00:00 UTC:
**1,003 executed/passed, zero failed/skipped; 22 scenarios each twice**.
All 20 focused cases ran. The real NUnit/scenario/invariant and independent
medical/contact/backup/fitting/feed omission controls were rejected. Seed
reproduction and report create-new checks passed. All 259 recorded source/input
hashes match this commit; all nine frozen gameplay DLLs match the verifier's
closure. Independent ignored snapshot:
`runtime/out/operational-hints-verification-20261019`.

Independent ultra source composition review found no remaining blocker in the
examined graph/projection/consumer scope. Root authored the implementation.
Native import, focus/keys, GUI, Player, physical behavior and multiplayer remain
NotRun. Earlier long probe seconds do not cover this source revision. This is a
reviewable readout prototype, not native or roadmap acceptance.
