# Astra independent engineering audit — eng05

Date: 2026-09-11. **Targeted acceptance: FAIL.** F02's nominal approach, branch continuity and the former large wall-equipment body conflicts now pass the bounded checks. The new suspended clean sign intersects its surroundings, guide 08 retains a structural intersection, and several smaller mounting-face conflicts remain. Source intent and the main validator result were not used as passing evidence.

Authority: frozen `production/checkpoints/eng05/Fuel_Corridor.blend`, **7,661 objects**, SHA-256 `f793907fcf4774d84c9c372996b641d9f28acd3142c12e98b4d22a8dbcd1ca23`. Fresh factory-started Blender 5.2 CPU processes reopened this exact save. No scene save, rendering, GPU operation, transform mutation, neighbor import or neighbor edit occurred. Earlier evidence is preserved. This geometry-only audit assigns no visual score or accepted art-cycle credit.

## Confirmed remaining defects

### Major — new clean blade sign intersects the door head and wall construction

Actual evaluated triangle intersections establish nine distinct outside-body conflicts:

- `Clean_blade_panel` intersects both `CLEAN_PORT_lintel_cheek` objects, both running rails, and the north wall's upper rail, `vertical_flange.001` and knee gusset.
- `Clean_blade_drop.001` intersects the second lintel cheek and the lintel roof.

Representative shared bounding extents are **23 × 270 × 190 mm** for panel/front cheek, **23 × 30 × 40 mm** for panel/running rail, and **18 × 18 × 70 mm** for drop/cheek. These are scales of overlap bounds, not intersection volumes. The evidence includes actual intersecting triangles, so the finding is not based on bounding boxes alone.

Both ceiling feet have real zero-gap backing, and both drops meet the panel to within 0.24 micrometres. This establishes an attachment chain but does **not** excuse the surrounding-body collisions. The complete assembly lies above the tested 2.20 m operating height and outside the straight clean-door approach; passing those route tests does not establish assembly fit.

### Moderate — guide 08 still intersects a vertical wall member

`Route_guide_08_back` and `Route_guide_08_housing` intersect `Wall_S18.0_0_1.2_vertical_web.001`; one fastener also intersects it. The housing/web shared extents are **20 × 48 × 120 mm**. This is a body conflict, not merely an embedded screw. The guide's central anchor has genuine zero-gap contact with the washable lining, demonstrating again why a single mount ray cannot establish full-body fit.

The other ten guides have no positive outside-body intersection in this probe. All eleven have actual backing, and the previous widespread lining embedment and guide 04's unsupported mount are resolved. Guide 08 is a residual defect from eng03, not a claimed new regression introduced in eng05.

### Smaller mounting-face conflicts

| Assembly | Actual evaluated conflict | Assessment |
|---|---|---|
| `Reactor_turn_key_back` | Intersects the west wall's panel joint by shared extents about **8 × 12 × 300 mm**, and its cross seam by **3.5 × 180 × 8 mm**. | Moderate: the relocated light's back does not fit the complete raised mounting surface. Its central anchor still passes. |
| `Bypass_first_aid_wall_spacer` | Intersects the panel cross seam, about **3.5 × 130 × 8 mm** shared extents. | Minor physical fit defect; the case itself now clears the structural flange. |
| `Bypass_work_permit_mounting_spacer` | Intersects the panel cross seam, about **3.5 × 100 × 8 mm** shared extents. | Minor physical fit defect; the exposed permit assembly clears the wall bodies. |

These are not silently treated as intentional fastener embedment: they involve rigid backplates/spacers and raised wall trim. Their severity is lower than the sign and guide-body intersections.

## Independently established corrections

- **Recessed service assembly:** all 112 inspected physical members clear architecture and neighboring equipment, apart from the intended pipe-to-feed connection. The former frame, hook-foot and dust-cap wall conflicts are gone. All three 200 mm spacers meet their wall feet and the service board; the feet meet actual panel geometry with errors below 0.2 micrometres. The assembly's most aisleward point is X−1.10950 m, outside the declared X−1.00 m edge of the 2 m centered west-bypass envelope by approximately **109.5 mm**.
- **Supply continuity:** branch and union clear architecture, as does the station pipe. The branch/station centerline endpoint difference is **0.12 micrometres**, and branch/main-loop centerline difference is zero. Evaluated tube surfaces connect. This is geometric continuity, not an operating pneumatic simulation.
- **Recess task light:** pan and diffuser clear all other tested local bodies. The pan contacts the actual recess ceiling within **0.24 micrometres** and meets the diffuser. Its lower face is **2.410 m**, above the tested operating height.
- **Other corrected equipment:** East/Clean distribution shells, doors, hinges, packet holder and conduit equipment, bypass isolation, first-aid case and plant permit body clear their previous large structural conflicts. New mounting and conduit spacers have actual backing and component contacts. A seemingly missing bypass termination contact in the triangle-only result was independently resolved to a **0.12-micrometre** gap; it is not an unsupported-part failure.
- **Numerical contacts:** the plant permit spacer and seven clean-distribution spacers produce approximately **1.91-micrometre** panel overlaps because of world-space floating-point evaluation. These are disclosed as numerical contact, not material penetration defects. This is distinct from the measured millimetre-scale trim conflicts above.
- **Shallow reactor lights:** both complete light assemblies clear adjacent physical geometry. Actual hood separation is **5.20 m**; all **15,876 F02 nominal 5 × 5 m approach rays pass**, with moving cap assemblies filtered. The prior hood obstruction is resolved.
- **Branches and seams:** all five nominal grids and operating grids, plus **12,645 straight branch walk-up rays**, pass; sampled floor discontinuities remain within 5 mm. All five fixed portal assemblies remain inboard. Wider F01/F02 scans find no beyond-seam geometry, including masonry shoulders.
- **Handoff:** all 12 carriage records, 34 markers and **7,268 collision records** resolve against saved geometry and properties. Port, ownership, cap/removal and coordinate semantics agree. Canonical handoff data, saved properties, disk export and manifest identities agree; raw file hashes are recorded separately in the evidence.

## Method, coverage and limits

The complete-body probe freshly evaluated **6,693 local mesh/tubular-curve bodies**, excluding font-only objects and flagged surface decals. It checked all members of **25 targeted assemblies** against every other nearby physical body, extending the prior architecture-only test to door heads, rails and equipment as well. It includes the new sign, task light, moved lights, complete service board, distribution/permit/first-aid assemblies and all eleven guides. Tests combine evaluated BVH triangle overlaps, bounded containment samples, overlap thickness, independent anchor rays and individual new mounting-piece contacts.

An independent bounded branch audit tested the full nominal reactor approach, ports, straight branch walk-ups, floors, seam ownership and typed handoff. It did not certify the sign's mounting fit; that is why its route pass and this report's sign failure are compatible.

No freight-gate motion replay was requested or performed for eng05. No continuously swept door test, all-part load-path certification, live neighbor fit, runtime collision/controller behavior or visual-lighting judgment is claimed. Closed branch/cap leaves were filtered only for counterfactual clear-opening tests; this does not demonstrate their storage motion or passage into unassembled neighbors. The current known collisions prevent targeted technical acceptance even though the tested routes pass.

Evidence in this directory: `astra-eng05-mesh-core.py`, `astra-eng05-details-probe.py`, `astra-eng05-details-evidence.json` and log; `astra-eng05-contact-refinement.py/.json` and log; `astra-eng05-branch-evidence.json`, branch shell/hood evidence and their scripts/logs.

| Frozen file | SHA-256 |
|---|---|
| build.py | `24a1359ae2127e4d6f9ed5073c95ce0f68c56456b69d197a41821e78dfc26dcf` |
| valorant_details.py | `8d1029c8f1bfdd844f43ba4a1a020e0a179896be65b73675ab6181f5bb173caf` |
| interface.json | `d410821c4fec77fa8cf49dfc9ba3f7acd7e34ebcd80559cd3513e1b5c731fcb7` |
| handoff.json, raw file | `ca6ad6fdca5befae4416d7f5207d167dee709b8d4b409d17750740a5be916c87` |
