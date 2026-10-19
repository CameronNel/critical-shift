# Production startup draws from the shared reserve, 19 October 2026

Branch `codex/production-reserve-costs-20261019`, based on timed-clearing draft
PR127 atd8e59d79. Primary author: Codex. Independent read-only ultra design
review: identify_repo. The owner authorizes continued useful implementation.

Purpose: production preparation must share the same finite reserve used by
reactor startup, cooling and medical stabilization. An optional immutable
recipe cost defaults zero for existing fixtures; canonical crusher/processor/
dryer opt into1/2/1 abstract reserve units per new cycle. These are prototype
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

All24 focused cost cases passed. The earlier combined run also passed all6
canonical full-shift route variants and19 drying cases (47 cases before adding
the final two cost regressions). The new paid-production-backup scenario passed
twice,19 steps and74 assertions per run. It proves a historical insufficient
Start stays rejected after backup credit, a fresh Start pays once, pause and
completion cannot pay again, and a later production debit invalidates a stale
reactor command. Build: zero warnings/errors.

The mixed ledger now accounts independently for distinct paid production cycles
alongside reactor and medical costs, using Bind's authored1/2/1 values rather
than resulting recipe/balance projections. The independent timed repair model
also authors random positive startup costs and predicts remaining reserve and
the production subtotal from those inputs through cancellation/terminal edges.
A deliberate omitted modeled startup debit fails case seed55 at the specific
paid-cycle resource invariant. Paid Started facts are emitted only for positive
cost; free legacy recipes keep their existing event behavior.

Independent ultra transaction/authority review found no blocking source defect.
Root authored all implementation and tests; reviewers ran no builds/tests.
Final full verification and exact source evidence remain pending. The ongoing
long probe still belongs to the frozen timed-clearing source, not this revision.
