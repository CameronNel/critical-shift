# Powered stabilization prototype, 19 October 2026

Branch `codex/powered-stabilization-20261019`, based on contracts/debrief checkpoint
`567a8fc6` (draft PR113). Primary author: Codex. Existing ultra `review_domain`
agent is the independent read-only reviewer. No additional agents were spawned.
This continues the owner's request to build missing useful game systems without
questions; the status question did not cancel that request. PR113 stays separate
and passed Ubuntu/Windows CI at its own head. The earlier interrupted endurance
run and unmet eight-hour requirement remain recorded in SHIFT_GAMEPLAY.md.

## Source scope

Implement one logical OCRU prototype for powered stabilization of an incapacitated
worker, following GAME_SPEC5.4/5.5 and ownership/transaction contracts S05/S07/S08.
Workers own condition and chamber rules. Interaction owns body custody and the
existing ordered command/receipt stream. Power, still composed by Reactor, owns
the only reserve account. Application validates/proposes then coordinates installs.
No new package, transport, persistence or generic transaction framework is chosen.

- Setup registers one chamber definition with bounded duration, reserve cost,
  cartridge stock, recovery delay and contamination limit. Values are authored
  prototype parameters, not accepted balance.
- A registered unconscious/down worker body must be held by the acting operator
  before insertion transfers its one custody owner to the station slot.
- Start validates station/patient revisions, condition, contamination, stock and
  reserve before committing any cost. A cycle consumes one cartridge and the
  authored reserve once. Retried receipts cannot charge again.
- Required owner polling completes at the exact shift-time due coordinate, before
  terminal teardown. Pause freezes work; a due time after the capped deadline
  cannot heal a worker. There is no advisory-timer dependency.
- Completion restores Alert/Down with suit/contamination facts preserved. Explicit
  ejection and separate current physical standing clearance are still required.
- Episode changes or contamination above the limit interrupt a pending cycle once.
  Suit and safe contamination revisions alone do not cancel treatment. Cancellation
  and interruption keep spent resources and body custody. A new paid cycle may be
  attempted if condition, stock and reserve permit it.
- Operator disconnect leaves committed treatment autonomous. Patient disconnect
  cancels/ejects before body retirement, so a slotted worker cannot fault peers.
- An awake/down patient may request emergency ejection only from their own safely
  ejectable chamber (Loaded, Ready or Interrupted). This has a separate typed admission path which cannot submit Start,
  affect another patient, or operate an unfinished treatment. It releases custody
  without standing/healing and still requires normal recovery delay/clearance.
  This prevents a sole surviving treated patient from being stranded when every
  operator has disconnected.
- Detached medical receipts, typed timeline events and canonical summary survive
  terminal debrief; restart gets fresh stock/state and rejects the old epoch.

## Original physical boundary

This is powered stabilization, not full biological shutdown/reanimation, physical
cartridge inventory, all ten OCRU procedure steps or post-reanimation debuffs.
Existing portable-crate placement/worker-drag adapters do not support a chamber.
No medical insertion button or physical success is exposed through those adapters.
A dedicated worker-chamber placement/reconciliation adapter and native tests are
required before playable physical integration. Unity remains unavailable here;
changed native recovery preflight is source-only and NotRun.

The later [physical rescue adapter](PHYSICAL_MEDICAL_RESCUE.md) adds explicit
chamber/discharge placement and controls on a separate draft branch. That source
supersedes the missing-adapter boundary above; its native execution remains
NotRun. The historical logical evidence below belongs to its recorded revision.

## Evidence

- First build passed with zero warnings/errors; first20 targeted medical tests
  passed. Two production-port scenarios passed twice: stabilization/recovery
  (15 steps,49 assertions per run) and patient-disconnect cleanup (6/24).
- First full run passed799 tests/17 scenarios. Follow-up regressions and the
  shared medical formatter brought a later full run to804 tests. Independent
  review found the disconnect event's pre-commit revision; recording moved after
  full cleanup/revision installation, with matching-revision assertions.
- Clinical model probe:10,000 cases passed against independent admission,
  stock/reserve and terminal-outcome arithmetic. Review then identified the
  sole-patient/operator-disconnect recovery dead end; emergency egress was added
  with narrow payload/actor/state admission and suit-preservation assertions.
  Full follow-up:808 tests/17 scenarios passed before the new egress scenario.
- Final medical candidate full verifier,19 October06:06:29–06:06:57 UTC:
  **812 executed/passed, zero failed/skipped;18 scenarios, each twice**. The real
  failing NUnit/scenario/endurance controls were rejected, seed replay passed,
  and create-new report protections passed. Exact source inputs and all nine
  gameplay assembly hashes are retained in ignored `dotnet/artifacts/summary.json`.
  SDK8.0.423; Release libraries target netstandard2.1/C#8.0. Static source checks
  passed181 metadata GUIDs/21 asmdefs/110 C# files. Python tooling passed182 tests.
- Final model seed20261021:10,000 cases/7,643,483 checked steps passed in16.89s,
  including externally aided patients releasing themselves after operator loss.
  Steps include model samples and selected commands, not only committed actions.
  Report: ignored `runtime/out/medical-model-final-20261021.jsonl`.
- Independent ultra reviewer `review_domain` found no blocking findings after
  reviewing the final egress/admission/model changes. Their review was read-only;
  they independently ran the static check, not builds or native physics. Earlier
  findings were fixed by the primary author. Review does not establish physical
  chamber behavior, Unity import, Player compatibility or multiplayer acceptance.
- The native catalogue now contains139 cases; the shared pure formatter executes
  offline, while new/changed native behavior remains NotRun. No current Unity
  result or complete game/roadmap gate is claimed.
- The replacement contract/debrief endurance run uses supervised45-second chunks
  with per-chunk Passed records and binary closure hashes. It covers its preserved
  earlier snapshot, not this medical branch. Its eight-hour target is pending.
