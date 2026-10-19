# Retained settlement evidence on fault, 19 October 2026

Branch `codex/fault-settlement-evidence-20261019`, based on draft PR136 `7fa3ad90`.
Root authored the fix after independent ultra review found a concrete gap.

If machine A completed and a later machine or owner threw during the same clock
poll, A's conversion was already committed. Its private result list was lost,
then fail-closed cleanup cleared the ledger receipt. Terminal totals showed the
completion without its input/output provenance. The same local-list pattern
affected earlier fitting completions/interruptions and recovery expiries when
a later worker failed.

The guarded world advance now owns typed buffers throughout settlement. Internal
production and multi-worker loops append only after installing their complete
transaction. The world journals those facts once on success or before fault
cleanup. Normal owner/event order stays unchanged. No external callback or
second inventory is introduced. Return lists retain read-only wrappers.

Trace records also retain the immutable typed production change, including
input/output properties and parent lineage. Recovery expiry joins the bounded
incident journal. The fault row records the capped attempted shift coordinate;
its world snapshot still shows the last successfully committed timeline sample.
This keeps the terminal fault after the retained facts without pretending the
failed overall poll completed normally. The world still faults and clears all
live owners; no timeout or normal end is published before required settlement.

Eight new fault-injection cases pass: earlier conversion followed by a second
machine or reactor revision overflow, at terminal and nonterminal samples;
earlier fitting completion or access interruption followed by another worker's
failure; and earlier recovery expiry followed by another worker's overflow.
Checks cover exact event/cause/cycle/output, full material balance, detached
parent lineage, bounded cleanup, fault occurrence vs world time, and no duplicate
publication after Stop. These are deliberate injected failures, not naturally
reachable counter-overflow claims. Native catalogue remains179/NotRun.

Full exact-candidate verification and the isolated pre-fix regression result
are appended after execution. Draft awaits independent maintainer review/merge;
no native, performance, multiplayer or acceptance gate is advanced.

Earlier candidate `ca9b59d955958d8027582d1c83ce9995ba832cb6` passed the full
verifier13:50:07–13:50:47UTC: **1216 executed/passed, zero failed/skipped;
28 scenarios each twice**. All285 recorded source inputs match that git tree
and nine DLL hashes match ignored `out/fault-settlement-verification-20261019`.
All13 logical negative controls and existing NUnit/scenario/overwrite controls
were rejected. Frozen seed20261065 passed10,000 mixed cases/15,606,127 selected
operations and model checks in39.9844144s. Tooling182 and static source checks
passed; no Unity-side source or native test inventory changed.

An isolated export of pre-fix `7fa3ad90` executed the same eight new injected
regressions: **8 failed, zero passed/skipped**. Only the new typed-production
property assertion was omitted because that property did not exist before the
fix; all behavioral expectations remained. The corrected source passes all8.
Independent ultra transaction and retention reviews found no remaining concrete
blocker. Current native execution remains NotRun; draft review/merge pending.

Final review also identified a related expiry batch: a later claim revision
could overflow after releasing an earlier holder and moving the clock. The
claim owner now constructs every checked release snapshot before clock/index
installation. Rejection preserves both holders and time, with sorted once-only
releases on a fresh retry. Two new atomicity cases cover first/second overflow;
a third injects a post-journal lease fault to prove that already published
production facts are not flushed again. All11 focused cases pass. Final full
verification of this additional fix follows below.
