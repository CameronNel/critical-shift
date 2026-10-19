# Safe wet-ore conditioning, 19 October 2026

Bounded implementation branch `codex/safe-ore-conditioning-20261019`, based on
`94f991dd` (draft PR #121). Primary author: Codex. Independent read-only ultra
reviewer: `audit_gameplay_integration`. The continuing owner request authorizes
useful game systems without questions or new framework selection.

Purpose: provide the safe drying alternative to bypassing wet ore, as described
by GAME_SPEC 10.5 and 11.7. Keep moisture, quantity, contamination and lineage in
the existing Materials ledger. Production keeps machine timing and Application
coordinates the same authenticated custody/receipt workflow. No new material
kind, domain, assembly edge, inventory, package or framework is introduced.

An explicit MachineRecipe drying factory authors same-kind, 100% yield, a lower
moisture target and safe admission up to moisture 1000. Ordinary conversion
construction keeps its existing different-kind rule. Start rejects already-dry
input and unsupported inspection bypass before reserving cycle history. Completion
creates one normal child batch in the same container, preserving quantity,
contamination, origin, original cause and inherited bypass flags. Drying cannot
launder suspect material. Power pause/resume, cancellation, exact deadline and
teardown retain the existing machine contract.

Canonical sandbox setup registers a stable dryer ID and the temporary physical
fixture reuses its existing machine builder/loading/custody adapters at a separate
position. Existing GUI/focus hints show drying rather than offering inspection
bypass. Native geometry, placement, GUI and physical feasibility remain NotRun;
public-port route tests establish logical feasibility only.

Expected scope: recipe/view contracts, narrow Production start validation,
scenario definition routing, canonical sandbox registration and existing fixture
composition/readout, focused tests/public-port wet→dry→crusher→processor→reactor
scenario, affected S01/S03/S05/S08 and TX/MACHINE validation mapping. No owner or
serialized identity is replaced or deleted. Fixture timing/moisture values remain
D-09 prototype parameters, not accepted balance or real industrial procedure.

Planned acceptance: conserved units and retained contamination/flags/lineage,
already-dry and bypass rejections before history, retry/pause/cancel/deadline,
zero skipped full verifier, and independent source review. Native execution,
Player, physical feel, multiplayer and roadmap acceptance remain separate.

## Source review correction

Independent integration review caught the initial dryer placement overlapping
the fixture patient's enabled thigh collider. Root moved the dryer north to
(-8.5, 0, 9), keeping the new loading support away from the patient's startup
ragdoll. This was geometric source review, not a native physics run. Physical
reach, contacts and native execution remain NotRun.

## Intermediate checks and review

The first build passed with zero warnings/errors. All 19 targeted cases passed,
including canonical wet stock to fuel/grid delivery with one large or partitioned
clock advance. The versioned safe route scenario passed twice, each with 22 steps
and 79 assertions. It verifies 12 wet units remain 12 through drying, become 11
fuel/spent units with one waste unit, and generate 440 grid units with original
cause/contamination retained. Native reach is synthetic in these logical checks.

Static source checks passed 188 metadata GUIDs, 21 asmdefs and 117 production C#
files. Independent ultra integration review found no further blocker after the
placement correction and checked current consumer migration. Root added active
drying to mixed probes, preserving the existing independent contact/backup/
clinical models and adding relational completion invariants. Full verification
and a final mixed probe are pending.
