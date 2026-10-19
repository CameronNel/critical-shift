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
