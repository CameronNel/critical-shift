# Worker contamination contacts, 19 October 2026

Bounded task on `codex/worker-contamination-20261019`, based on `483b577a`
(draft PR #119). Primary author: Codex. Independent read-only ultra reviewers:
`audit_worker_recovery`, `audit_medical_authority` and `audit_endurance_models`. The owner authorized useful game systems without
questions. Existing eight-hour frozen probes continue separately; their results
will not be attributed to this new source.

Implement discrete authored exposure/decontamination contacts in the existing
Workers owner, following GAME_SPEC 6.3/6.7 and S01/S02/S03/S07/S08. Keep the canonical
0–100 worker contamination meter. Intact/compromised suits reduce newly admitted
exposure; decontamination removes contamination without suit repair, healing,
standing, new injury episodes or custody changes. This is not radiation dose,
exposure stages, biological shutdown, materials-scale conversion or accepted
balance. No new domain/assembly/framework/package/transport is introduced.

Setup registers bounded immutable source definitions (kind, amount, cooldown).
A trusted host sample identifies epoch, target, source, per-source sequence,
cause and sampled shift time. New contacts use the current authoritative shift
coordinate. Exact retained retries precede current suit/time calculation; changed
payload, gaps, old identities and unknown sources are explicit non-effects.
Accepted clean/saturated/cooldown samples still advance their bounded source
receipt, keeping callback spam from adding contamination or wedging the source.
Current suit affects new contact only. Unexpected integrity errors fail closed.

Unsafe contamination must interrupt a pending medical cycle once at the accepted
condition change, preserving costs, custody, original injury cause and cycle.
Washing before a later poll must not erase that unsafe excursion. A new paid
attempt may then begin if condition, stock and reserve permit it.

Expected touched scope: Workers Domain/Application contracts and workflows,
typed trace/retained incident projection, targeted offline tests/scenario and
independent probe coverage, affected architecture calling/validation rows and
this evidence note. Existing implementation searched: WorkerState, WorkerWorkflow, 
SetWorkerEnvironment, MedicalOperations, SessionDiagnostics, ShiftIncidentJournal.
No serialized identity migration or native physical adapter is included.

Definition of done: public-port contamination→wash→medical/recovery scenario and
focused identity/time/protection/orthogonal-condition/custody tests, a useful
independent contact model, full verifier with real controls, and independent
source review. Unity import/volumes/controls/physics/multiplayer remain NotRun.

## Review and checks completed before full verification

The worker and clinical reviewers found no remaining blockers. Review caught a
medical trace identity defect in the initial candidate: immediate interruption
now records the station identity, with the contact cause/source as trigger and
the original injury cause preserved in the medical payload. Focused regressions
cover those identities, the shared world revision and one retained interruption.
Root authored all changes; reviewers made no edits.

The first 34 targeted cases passed. The public-port contamination/medical/recovery
scenario passed twice, with 21 steps and 73 assertions per run. A strengthened
10,000-case seed 20261029 run passed with 10,289,231 CheckedSteps, including a
successful wash in every independent contact-model lifetime and contacts mixed
into active medical, reactor and production work. The deliberately omitted
exposure control failed with its intended raw-load ledger invariant.

Five further malformed/stale contact cases and the complete suite await the full
verifier. These intermediate runs are not the final suite result or native proof.
