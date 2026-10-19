# Explicit ore washing prototype, 19 October 2026

Branch `codex/ore-washing-20261019`, based on draft PR131 `2f7f7933`.
Root is sole author; independent ultra reviewers inspect gameplay, material
accounting and lifecycle. User authorizes continued useful game building.

Purpose: add a safe contaminated-ore route through the existing paid Production
cycle and Materials ledger. Explicit same-kind/yield100% washing lowers current
batch contamination to an authored target and produces wet material. The existing
dryer is then needed before ordinary safe crushing. Washing cannot bypass
inspection or remove inherited bypass flags, cause, origin or parent lineage.
Already-clean input rejects before history reservation or reserve spending.

Production owns recipe/time/mode; Materials owns current properties/quantity and
conversion history; Interaction retains custody; existing PowerAccount retains
all paid costs. Reactor fuel exhaustion and all ordinary conversions default to
preserving contamination. No second ledger, inventory, wash-water simulation,
new material kind, worker-dose conversion, package, map/art or framework.

The canonical fixture adds one washer and marks spare crate index5 contaminated;
the existing clean reference route uses0–3 and ready fuel6, while wet crate7
retains its dryer role. Initial total units, quota windows and clean-route cost
remain unchanged. Authored prototype washer:10s,1reserve,100contamination target,
wet output1000. These are game scales/tuning, not industrial parameters.

S01/S02/S03/S05/S08 and TX/POWER/LIFE evidence will cover safe full route,
property/quantity/lineage preservation, cancellation/cutoff/retry/pause, shared
reserve, malformed definitions and current readouts. Native machine placement,
loading and controls remain source-only/NotRun until pinned Unity runs them.

Migration: no removed/renamed sources, serialized scene or content identity.
Machine IDs403/recipe453 and one extra static fixture machine use the existing
slot/presentation builders. Portable registrations and Rigidbody observation
counts remain11/31. Ordinary, drying and Fuel→SpentFuel preparation retain their
existing contamination-preserving default. The common bypass predicate replaces
drying-only UI gates; the current crate readout includes contamination and flags.

Focused evidence:53 washing/drying/reference-route cases passed, including28 new
washing cases. The authored dirty route passed twice:31 steps/107 assertions per
run. Initial1000 model cases passed; after source-review additions,10,000 cases
seed20261049 passed13,981,129 selected command/model checks in35.996s. These
preliminary binaries precede the final source commit. Expected work/properties/
costs come from authored inputs; only opaque cycle/child IDs bind from owners.
The deliberately omitted cleaning failed at the named independent invariant.
Four actual malformed washer scenarios (contradictory modes, fixed moisture,
meaningless target, fixed yield) failed; none produced a Passed result.

Independent ultra reviews found no core accounting blocker. Root fixed numeric
material feedback, material-specific wet-output advice, dirty-history coverage,
publication-count checking and original input/output fields on model facts and
receipts. A declared native physical-socket washer→dryer case was added to the
171-case catalogue; all changed native behavior remains NotRun. Final verifier,
binary/source audit and review status will be recorded below.
