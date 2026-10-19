# Physical medical rescue adapter, 19 October 2026

Branch `codex/physical-medical-rescue-20261019`, based on draft PR #128 at
b819189d. Primary author: Codex. The owner authorizes continued game building
without questions. Independent read-only ultra design tracks: composition,
worker recovery, gameplay bindings, lifecycle boundaries and rescue controls.

Purpose: make existing paid timed stabilization physically usable in the local
sandbox. Application MedicalOperations still owns cartridge/time/interlock/
patient rules and Interaction owns custody. Workers.Unity remains the sole rig
motion writer. Bootstrap composes explicit callbacks so peer Unity assemblies
do not gain a dependency on one another. No new clinical rule domain, package,
UI framework, network/Steam/voice, persistence, map/art or equipment allocator.

The bounded fixture adds explicit static chamber, discharge and console anchors.
All bound body capsules, actual physical collision filtering and static support
must validate before insertion/ejection. Saturated/blocked observation rejects
before command/sequence/custody/resource mutation. One pump precedes staging;
there is no second clock sample between geometry preparation and logical commit.
Only exact current post-claim identity may accept the staged pose. Historical
receipts cannot move a body. Unexpected postcommit missing/moved binding stops
the trial visibly; a held-attachment failure is not a slotted-patient rollback.

A reversible chamber mode keeps controller off, body segments kinematic and
non-contacting, preserving hierarchy/joints/recovery yaw and original injury,
suit/contamination. It is distinct from terminal Freeze and standing recovery.
Loaded/Treating/Interrupted/Ready patients remain physically slotted; completing
treatment only yields Alert/Down. Discharge restores a staged free ragdoll with
no added impulse. Existing recovery delay and both clearance checks still apply.
Exposure/wash sampling remains active for chambered workers.

E/R and the existing temporary panel route through LocalCommandPort. Medical
loading precedes the generic held-worker equipment guard. Own-patient emergency
egress derives current body/chamber custody despite ordinary down-worker focus
exclusion, retains spatial range/LOS and cannot target another patient. Numeric
interlocks/countdowns derive from immutable authored rules. A separate explicit
diagnostic incapacitation produces a medically eligible unconscious patient;
ordinary knockdown remains Alert/Down and cannot silently become eligible.

Affected S01/S02/S03/S05/S07/S08, TX/POWER/WORKER/HOLD/PHYS/LIFE validation:
placement, obstruction/IgnoreRaycast/saturation, original body/cycle/lease,
pause/cancel/interruption/completion, self-egress, historical retry, standing
recovery, missing bindings, disconnect/deadline/restart and truthful readout.
All new native cases are Planned/NotRun until the pinned Unity editor executes
them. Offline logic/source checks cannot establish physical behavior or controls.

Migration: the canonical fixture registers both physical worker body identities;
logical/physical bindings rise from10 to11, while the same31 physical bodies are
observed. Player smoke validation and its synthetic fixtures use the new exact
baseline. Historical logs/results are retained unchanged. No serialized scene,
asset identity or package changes; new scripts have unique metadata. Existing
crate and cart placement/lease owners remain in use. Only the chamber callbacks
can enter/exit the new reversible worker mode.

Independent source reviews found and the primary author fixed: foreign retired
claims reaching freeze cleanup; placement reuse after teardown; changed held
pose/bed hidden by discharge staging; first-E completion routing; unsupported
collider/Rigidbody collision overrides; articulation-owned static references;
stale smoke inventory and an incorrect native test property. Follow-up reviews
are source review only. Native assertions cannot establish a pass without Unity.

The27 declared medical PlayMode methods cover whole-rig/joint-consistent handoff,
E/R routing, exact custody, completion and separate recovery; bed/discharge block,
IgnoreRaycast/saturation; pause, injury/actual-pelvis exposure interruption; moved
anchors, disconnect, historical ejection; foreign claims and lifetime reuse;
corrupted held pose, changed destination after staging; exact-time and externally
aided own egress, console occlusion and sole-patient egress after operator loss;
deadline freeze with blocked pad; rejected Treating ejection then fresh discharge;
unsupported collision filters and articulation ownership. Catalogue166 total:
**NotRun** for this revision.

The linked pure medical readout exercises authored cost/duration/limits/recovery
delay, five phases, pause/countdowns, cutoff warning, patient identity, historical
cost snapshots, actual resource/interlock rejection, cancellation/discharge,
external aid and locale-independent fractional time. Initial15 cases plus six
canonical quota routes passed; a later aid regression is included in the final
inventory. Full-suite and final review evidence will be recorded below.

Final source candidate `6a6ac6cdfbd12c4df6aa309f0a59c509180c79b6`:
19 October11:39:32–11:40:07 UTC, SDK8.0.423 Release/C#8/netstandard2.1:
**1062 executed/passed, zero failed/skipped;24 scenarios, each twice**. Real
failing NUnit/scenario and all eight independent-ledger/control paths were
rejected; seed reproduction and create-new report checks passed. All266 recorded
source inputs match that exact git tree; nine executable assembly hashes were
validated and frozen under ignored `out/physical-medical-verification-20261019`.
Static checks:201 unique metadata GUIDs,21 asmdefs,130 C# files. Python tooling:
182 passed. The16 medical-readout cases are included in1062, not an additional
total. Independent ultra source reviewers rechecked host/custody/clock, rig
geometry, setup/teardown, readout and controls after root-authored repairs; no
remaining concrete blocker was reported. Review is not native acceptance.

Pinned Unity6000.4.3f1 remains unavailable locally (download denied403), and the
last remote workstation check at10:45 UTC was Offline. New/current native166
catalogue, GUI controls, actual clearance/settling/recovery, Player/build and
multiplayer remain **NotRun**. The earlier132-case Unity record belongs to its
earlier source. This feature remains a draft for independent maintainer review;
it does not establish full OCRU reanimation, cartridge item inventory or balance.
