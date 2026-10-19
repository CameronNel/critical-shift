# Powered stabilization prototype

This logical OCRU slice treats an unconscious/down worker using one cartridge and
the existing shared reserve. It does not implement biological shutdown, the full
reanimation procedure, physical cartridge handling or a Unity chamber. The
parameters are bounded development fixtures, not accepted game balance.

## Ownership and setup

Workers Domain owns immutable chamber rules/state and worker condition.
Interaction owns the registered worker body's exclusive custody. Power owns the
only reserve account, composed through Reactor; Application coordinates these
owners on the existing single host simulation thread. No domain references a
peer domain, and no new assembly or transaction framework is introduced.

During Setup, register worker bodies and at most one station:

```csharp
world.RegisterWorkerBody(patientId, bodyId);
world.Medical.Register(stationId, new MedicalDefinition(
    durationMilliseconds: 3000, reserveCost: 6, cartridges: 2,
    recoveryDelayMilliseconds: 500, maximumContamination: 50));
```

Definitions bound duration to 1–60,000 ms, reserve cost to 1–100,000, stock to
0–32, recovery delay to 0–60,000 ms and contamination limit to 0–100. Restart
requires normal fresh setup; stock, station identity and receipts do not cross
epochs.

## Commands and lifecycle

`LocalCommandPort.OperateMedical` builds intentions from current views through
the same authenticated connection/sequence/receipt stream as other operations.
Direct callers use `InteractionKind.Medical` with a versioned `MedicalRequest`:

| Action | Required current values | Result |
| --- | --- | --- |
| Insert | Station revision; held registered body, object revision and lease | Unconscious/down patient becomes the slot's sole occupant |
| Start | Station and patient revisions | Consumes one cartridge and reserve once; begins autonomous treatment |
| Cancel | Station revision | Stops treatment, retaining body and costs |
| Eject | Station and body object revisions | Releases a Loaded, Ready or Interrupted body; Treating is rejected |

Every admitted well-formed rejection finalizes its sequence. Matching retained
retries return historical receipts without another debit, cartridge use or
custody change. Only `HasNewCommit` authorizes a new physical effect. A later
patient cannot be released by replaying an older patient's ejection receipt.

Start checks condition, revisions, contamination, stock, custody, arithmetic and
reserve before committing costs. It captures the patient's injury episode and
cause. Owner polling settles at the exact shift-time due coordinate, before a
terminal debrief is published. Pause freezes treatment. Work due after the shift
deadline cannot heal the patient. Advisory timers are not required for progress.

Completion produces Alert/Down and a separate standing recovery deadline; it
does not stand the patient, restore their suit or remove contamination. New
injury episodes, awareness/posture changes or excessive contamination interrupt
treatment once. Unsafe accepted contamination changes now interrupt immediately,
including trusted absolute environment control and authored contacts; washing
before another owner poll cannot hide the excursion. See the
[contact contract](WORKER_CONTAMINATION.md). Injury/awareness changes retain their
required owner-poll reconciliation. Safe environment/suit revisions alone do not interrupt it.
Cancel, interruption and terminal cancellation retain spent resources. A new
paid attempt is possible only if the current condition, stock and reserve allow
it. Terminal cancellation counts a pending treatment once.

Operator disconnect leaves treatment autonomous. Patient disconnect ejects the
body before worker retirement and interrupts a pending treatment once. Detached
medical changes preserve cycle/patient/body identity even when the resulting
station is empty; the original injury cause stays attached to that cycle.

## Patient emergency egress

An Alert/Down patient can release themselves from their own Loaded, Ready or
Interrupted chamber using `MedicalAction.EmergencyEject`. The local port selects
the separate `InteractionKind.MedicalEgress`; direct callers must use that exact
kind/action pair. It grants no other medical action while down, cannot affect
another patient, cannot eject Treating, and still enforces phase, access policy,
station/object revisions and ordered receipts. Normal recovery delay and
physical standing clearance remain required after release.

If trusted external aid wakes a patient during treatment, the next required
owner poll interrupts that cycle before egress. Polling the current host time
again is sufficient; the patient need not wait for another treatment deadline.
This permits recovery when every operator has disconnected.

## Projections and validation limits

`MedicalView` is detached and read-only. `PatientEpisodeAtStart` and
`PatientRevisionAtStart` describe the captured start, not the current worker.
`MedicalSummary` retains stock use and completed/cancelled/interrupted counts.
The terminal debrief freezes that summary and typed medical timeline events.
These projections cannot mutate condition, reserve or custody.

The existing crate-placement and worker-drag adapters do not support slotted
worker chambers. There are no native insertion controls on those adapters.
Worker standing now rejects a slotted body in the canonical workflow and native
preflight; the changed native path has not run here. A dedicated chamber
placement/reconciliation adapter and Unity tests remain necessary for playable
physical integration. See [task evidence](../validation/MEDICAL_STABILIZATION.md)
for executed checks and the Unity blocker. The logical scenario runner includes
stabilization, patient disconnect and sole-survivor egress fixtures; its clinical
model probes independent admission, costs, outcomes and retained suit facts.
