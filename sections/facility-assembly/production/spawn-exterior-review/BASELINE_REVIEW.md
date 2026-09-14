# Spawn exterior + rescue courtyard A14 baseline review

Revision: `baseline-fixed-v1` from `facility_master_A14_exterior.blend`  
Source hash: `00b371d369b11d242e71daac6a7bd39b8dfe5ce81eb5a81e6823a5d84cc972ef`  
Views inspected at native 1600x1100: `01_COURTYARD`, `02_SOUTH`, `03_EAST`, `04_TOP`  
Evidence: `baseline-fixed-v1/*.png`, `FIXED_CAMERAS.json`, `TASK_STATE.md`  
Concept approval: **UNVERIFIED / not requested yet**. This is a baseline only; no polish or acceptance is approved.

## Decision

**REJECT baseline.** The four images are present and visually inspectable, but concept approval is absent and several construction, support, reservation, and runtime categories have no current revision-specific evidence. The rendered exterior reads as a large, very pale assembled facility with strong route furniture and a visible spawn entry, but it is still a rough visual baseline rather than a finished art pass.

Per rubric, no category with missing evidence receives a score. Numeric visual scores are observations of these four images only; they are not transferred from R05 or from technical reports.

## View observations

- `01_COURTYARD`: valid and useful for spawn entry, courtyard paving, planters, benches, railings, roof equipment and the adjacent rock context. The entry is legible, but the pale ground and façade compress value separation and the rear/courtyard service logic is only partly visible.
- `02_SOUTH`: valid but tight. The door, wings, roof unit, sign and front rail are readable. Foreground rail dominates the lower edge and the route beyond is visually compressed.
- `03_EAST`: valid and wider. It exposes the rear/service side, courtyard benches, planters, conduits and roof masses. The service elevation has broad quiet walls and limited focal storytelling.
- `04_TOP`: valid plan evidence. The courtyard footprint, open paving, planters, benches, roof blocks and route edges are readable. The very light ground makes some edges and grade transitions difficult to judge.

## Category scores

| # | Category | Result | Baseline evidence / reason |
|---:|---|---|---|
| 1 | Reference fidelity and concept adherence | **UNVERIFIED** | No user-approved concept exists yet. The scene is plausibly institutional, but concept comparison cannot be scored. |
| 2 | Silhouette and massing | **72/100 — REJECT** | Four views show a clear stepped spawn mass and entry frame. Roof blocks and wings read, but the shell remains broad rectangular masses with limited distinctive secondary form. |
| 3 | Scale and spatial layout | **78/100 — REJECT** | Top view establishes coherent footprint and relative courtyard placement; doors, rails, benches and planters read at believable scale. Exact dimensions and authoritative alignment were not supplied in this review. |
| 4 | Circulation, access, and rescue route | **74/100 — REJECT** | Courtyard paving, central arrival and rail-lined edges are visible, with a readable entry. Route widths, thresholds, collision and rescue endpoint continuity are unverified. |
| 5 | Construction and load/support logic | **UNVERIFIED** | Pixels show roof trims, rails, planters and lights in plausible positions, but no current evaluated support/penetration report accompanies A14. |
| 6 | Utility and service continuity | **UNVERIFIED** | Some roof units, conduits and drains are visible, especially in `03_EAST` and `04_TOP`; endpoint/clearance continuity is not proven for this revision. |
| 7 | Exterior materials and surface response | **63/100 — REJECT** | Concrete/mineral, dark trim, green panels, paving, timber and vegetation separate at a glance. Most large surfaces are nearly white and low contrast; material variation and authored wear are sparse. |
| 8 | Lighting, palette, and readability | **67/100 — REJECT** | Entry practicals have readable glow and soft shadows. Overall exposure is very bright and cool, with low contact/value separation across ground and shell; the spawn focal hierarchy is weak outside the sign and lamps. |
| 9 | Environmental storytelling and human use | **62/100 — REJECT** | Benches, planters, rails and the arrival sign suggest a maintained staff/rescue campus. The service side is mostly empty; little visible maintenance evidence, PPE, repair history or rescue staging explains how the place is used. |
| 10 | Terrain, drainage, and ground transitions | **UNVERIFIED** | Paving seams and several linear drains are visible, but grade, drainage function, terrain cutout and slab transitions need current probes/audit. |
| 11 | Roof and elevated detail | **64/100 — REJECT** | Roofs are visible in all non-top views and top view confirms the mass plan; trims and HVAC units read. Surfaces are broad and under-detailed, and roof support/weather/drain evidence is absent. |
| 12 | View-to-view consistency | **76/100 — REJECT** | Same A14 baseline and fixed camera manifest are present; entry, green panels, roof unit and courtyard language persist. The framing changes substantially and the reverse side exposes unfinished/quiet areas, so consistency is only partial. |
| 13 | Interface and reservation integrity | **UNVERIFIED** | Four views show adjoining routes and neighboring structures, but no current portal/reservation overlay or source-preservation audit was provided. |
| 14 | Runtime and delivery readiness | **UNVERIFIED** | Native renders and source hash are recorded. Collision, navmesh, dependency, texture, cold-load and runtime performance evidence are not present in this baseline package. |
| 15 | Art-direction veto and professional finish | **58/100 — REJECT** | No single hard veto dominates, and the scene is grounded enough to read as an industrial campus. It is visibly short of professional finish: pale/flat value grouping, sparse rear dressing, repeated panel masses and insufficient authored wear/detail. |

## Concrete blockers before any polish review

1. Obtain explicit user approval of the concept sheet built from these exact four locked views.
2. Supply current A14 support/connectivity, utility endpoint, terrain/transition, portal/reservation, and source-preservation evidence.
3. Improve value/material separation and selective wear while preserving the restrained institutional palette; add authored rescue/staff use cues to the courtyard and service elevation.
4. Recheck the fixed views after the approved concept pass. `02_SOUTH` is valid but tight, so the front entry and both wings must remain readable after additions; `03_EAST` must continue to expose the rear/service logic.
5. Add runtime/cold-load/collision/navigation evidence before claiming delivery readiness.

Historical R05 visual scores and support reports are context only and were not used as current A14 proof.
