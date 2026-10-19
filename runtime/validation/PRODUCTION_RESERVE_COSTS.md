# Production startup draws from the shared reserve, 19 October 2026

Branch `codex/production-reserve-costs-20261019`, based on timed-clearing draft
PR #127 at d8e59d79. Primary author: Codex. Independent read-only ultra design
review: identify_repo. The owner authorizes continued useful implementation.

Purpose: production preparation must share the same finite reserve used by
reactor startup, cooling and medical stabilization. An optional immutable
recipe cost defaults zero for existing fixtures; canonical crusher/processor/
dryer opt into 1/2/1 abstract reserve units per new cycle. These are prototype
balance values, not a new continuous electrical allocation system.

Production.Start validates and prepares material/process replacements and a
checked spending subtotal, then prepares a debit through the existing sole
ReactorOperations reserve owner. Positive cost without sufficient reserve
rejects without reservation or debit. Zero skips debit preparation and still
works without a registered reactor. No callbacks/awaits/adapter effects occur
between installs. One new Start pays once; retry, stale/denied command,
Repair/Resume/completion do not pay. Cancel/terminal keep committed spending.

Started facts retain original cycle, input/cause and cost. A detached production
subtotal explains part of total PowerView.Spent; it is not another balance.
The readout shows cost before startup. The canonical full-quota safe route
must use existing finite backup during preparation, without raising initial
reserve, stock or quota, and retain its original passing/failing reload bounds.

Affected S01/S02/S03/S05/S08, TX/POWER/CAUSE/LIFE validation: rejected/once-only
spend, cross-consumer contention/revision, material/custody/history conservation,
restart/teardown, overflow fail-closed, cause/trace eviction, paid safe drying
and actual canonical route. No new domain/package, network/Steam/voice,
persistence, map/art work or continuous power allocator. Unity native controls,
GUI, physics, Player and multiplayer remain NotRun.

## Intermediate verification

All 24 focused cost cases passed. The earlier combined run also passed all 6
canonical full-shift route variants and 19 drying cases (47 cases before adding
the final two cost regressions). The new paid-production-backup scenario passed
twice, 19 steps and 74 assertions per run. It proves a historical insufficient
Start stays rejected after backup credit, a fresh Start pays once, pause and
completion cannot pay again, and a later production debit invalidates a stale
reactor command. Build: zero warnings/errors.

The mixed ledger now accounts independently for distinct paid production cycles
alongside reactor and medical costs, using Bind's authored 1/2/1 values rather
than resulting recipe/balance projections. The independent timed repair model
also authors random positive startup costs and predicts remaining reserve and
the production subtotal from those inputs through cancellation/terminal edges.
A deliberate omitted modeled startup debit fails case seed 55 at the specific
paid-cycle resource invariant. Paid Started facts are emitted only for positive
cost; free legacy recipes keep their existing event behavior.

Independent ultra transaction/authority review found no blocking source defect.
Root authored all implementation and tests; reviewers ran no builds/tests.
Final full verification and exact source evidence remain pending. The ongoing
long probe still belongs to the frozen timed-clearing source, not this revision.

## Final verification

Source `4841a03e1500fcc3d7f52cf368d6866e123e76de` passed the full verifier
from 2026-10-19T10:54:35.148968+00:00 to
2026-10-19T10:55:09.839443+00:00 UTC: **1,046 executed/passed, zero
failed/skipped; 24 scenarios each twice**. Real NUnit/scenario/invariant and
independent medical/contact/backup/fitting/feed/repair/production omission
controls were rejected. Seed reproduction and report create-new checks passed.
All 264 recorded source/input hashes match the tested commit, and all nine
frozen DLLs match its verifier closure. Static checks passed 195 metadata GUIDs,
21 asmdefs and 124 production C# files. Snapshot:
`runtime/out/production-cost-verification-20261019`.

The final frozen runner passed 10,000 randomized cases with seed 20261043:
13,776,178 checked steps in 32.865 seconds. The mixed ledger checks admitted
commit accounting; it does not independently predict every random admission.
Focused tests cover that policy. Checked steps are modeled observations and
selected operations, not distinct assertions. Earlier long probe time remains
attributed to its preserved build, and this latest verification is stored as a
separate closure alongside that evidence.

Three independent read-only ultra source/authority, setup/readout and model
reviews found no blocker in their examined scopes. Root authored all changes.
Native import, PlayMode, GUI/keys, physics, Player and multiplayer remain NotRun;
this does not establish full native rescue or continuous power allocation.
