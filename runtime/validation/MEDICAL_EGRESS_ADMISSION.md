# Medical emergency egress admission, 19 October 2026

Bounded regression task on `codex/medical-egress-admission-20261019`, based on
`aa1bffa5` (compact objectives, draft PR118). Primary author: Codex. Independent
read-only ultra reviewer: `audit_medical_authority`. This follows the owner's
request to review and improve the game while useful endurance checks continue.

The patient-only egress exception must retain ordinary host admission. Cover
process pause, current access denial, stale station/body revisions, historical
retries, and old epochs without releasing custody or spending again. This is
S02/S03/S04/S07/S08, CMD/HOLD/WORKER/POWER evidence at the offline layer.

Only the existing medical regression fixture, explicit expected-test inventory
and this task record are expected to change. Application remains the single coordinator; Workers, Interaction and
Power retain their state ownership. No runtime API, dependency, serialized asset,
package, clinical policy, physical chamber or migration is introduced. Search
included MedicalWorkflowTests, MedicalOperations, LocalCommandPort,
WorldSession actor admission and InteractionWorld receipt/access handling.

Definition of done: targeted regressions and the full shared-state offline
verifier pass, independent review resolves concrete findings, and the exact
revision is submitted for review. Native Unity/Player/physical/multiplayer
execution remains NotRun because the pinned editor is unavailable. This does
not advance a roadmap gate or establish playable physical chamber integration.

## Evidence

- Eight new parameterized cases passed in the targeted run (nine selected tests,
  including one existing historical-egress regression). Independent read-only
  ultra review found no blocking findings and suggested checking the outer stale
  body status; that assertion was added.
- The first full run executed/passed839 NUnit cases but correctly failed discovery
  reconciliation because the explicit expected-test inventory had not yet been
  updated. After registering the eight new cases, the complete verifier passed
  at07:16:26–07:16:55 UTC:839 passed, zero failed/skipped;18 production-port
  scenarios each ran twice. Real failing NUnit/scenario/invariant/medical-ledger
  controls and report-overwrite attempts were rejected; seed replay passed.
- Static source validation passed183 GUIDs/21 asmdefs/112 C# files. Diff whitespace
  validation passed. Runtime, probe and Python tooling sources were unchanged;
  the earlier182-test Python result remains the relevant tooling checkpoint.
- Detailed ignored result: `runtime/dotnet/artifacts/summary.json`; full log:
  `/tmp/medical-egress-verification-final.log`. The verifier ran before the test
  commit; its recorded source hashes identify exactly the reviewed test inputs.
  Native Unity, Player, physical chamber and multiplayer checks remain NotRun.
- Review status: bounded source review complete; draft stacked PR pending.
  No runtime behavior change or roadmap acceptance is claimed.
