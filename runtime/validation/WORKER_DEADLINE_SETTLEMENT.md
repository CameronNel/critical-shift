# Worker deadline settlement,19 October2026

Branch `codex/worker-deadline-settlement-20261019`, based on supply-route
checkpoint523f4274. Primary author Codex. Additional independent ultra reviewers
`audit_shift_boundaries` and `audit_debrief_retention` identified the same P2:
a direct leap to the shift deadline freezes an already-expired standing attempt
as Recovering; an intermediate sample correctly leaves it Down. Both also found
that overdue expiry is timestamped at polling time instead of its stored deadline.

The bounded repair keeps Workers as the condition/deadline owner, adds no package
or assembly dependency, and settles required worker expirations before terminal
publication/roster capture. Advisory timers remain suppressed at termination.
The terminal advance must retain detached worker changes, and unexpected expiry
failure must fault before publishing a timeout. Diagnostics must carry occurrence
time separately from observation time. S03/S07/S08, WORKER-01, SHIFT-01 and CAUSE
apply. No serialized identity or art change is needed.

Executed first regression run:five failed/one passed, reproducing the stale
terminal pose, polling-time timestamp and missing failure-before-timeout path.
After repair all six passed. First full verifier:824 executed/passed, zero
failed/skipped;18 scenarios each twice, with negative/failure controls intact.
Static source check passed182 GUIDs/21 asmdefs/111 C# files. Independent ultra
reviewer `audit_shift_boundaries` found no blocking findings in the repair,
including pause-sensitive capped time, retained terminal changes and advisory
suppression; they ran no builds. Existing Python tooling had passed182 tests at
the unchanged tooling checkpoint. Latest commit/CI evidence remains pending.
Native Unity
and physical recovery remain NotRun; the cloud editor is absent and workstation
offline. This source repair does not establish a roadmap gate or merge approval.
