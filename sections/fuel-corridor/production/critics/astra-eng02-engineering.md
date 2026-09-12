# Astra independent engineering audit — eng02 / P07

Date: 2026-09-11. **Targeted acceptance: FAIL.** The previous nominal-opening, lintel-slot, ceiling and typed-handoff issues show measured improvement. Opposing rollers now collide near closure, the service station still intersects wall construction, and outboard masonry shoulders leave a seam-ownership risk. This geometry-only save has no visual acceptance or full-scene art-cycle credit.

Independently opened frozen `production/checkpoints/eng02/Fuel_Corridor.blend` in fresh factory-started Blender 5.2 CPU processes. Actual scene: **7,096 objects**, revision eng02, stage full. SHA-256 before and after: `82fa3305998592fa793a1625cc2958c12826cfb97274868b3cf1bced30bc8bb5`. No render, GPU operation, scene save, object transform mutation, neighbor import or neighbor edit occurred. Previous full01 evidence is preserved. Mutable art sources were not used as authority.

## Remaining defects and regressions

### Major — opposing carriage rollers penetrate near the closed state

The replacement track fixes the former hanger-versus-solid-lintel conflict, but the opposite carriages' rollers occupy common volume at closure. In FREIGHT_GATE's mathematically closed pose, these actual evaluated pairs intersect:

- `FREIGHT_GATE_leaf_carriage_roller` / `.002`.
- `FREIGHT_GATE_leaf_carriage_roller.001` / `.003`.

The shared bounding extents are approximately **14 mm across the axle, 20 mm along travel and 120 mm vertically**; triangle surface intersections confirm actual penetration. These extents are collision witnesses, not an overlap-volume calculation. Roller centers are about 100 mm apart along travel, while the combined diameter is 120 mm. Frozen `build.py:301–305` authors these assemblies.

Additional near-closed probes find the two intersections at opening fractions 0, .001, .002, .004 and .005; they are absent at .0055, .006 and .01. Thus the conflict persists into the first approximately half-percent of opening, rather than being an isolated floating-point contact at a single endpoint.

The issue is **generic across the saved closed doors**. Each of REFINERY_BOUNDARY, REACTOR_BOUNDARY, PLANT_PORT, CLEAN_PORT and WASTE_PORT has the same two actual opposing-roller penetration pairs in its saved pose: ten saved-state pairs total, in addition to the freight gate's two counterfactual closed-state pairs. F01/F02 rollers are removable cap members, but the three branch doors are retained operational geometry. This is a new regression relative to full01's roller-free construction.

### Moderate — the service feed still intersects wall hardware, with additional station-pipe conflicts

Actual evaluated intersections remain between `Recess_air_branch` and `Wall_W-1.65_0_14.3_knee_gusset.001`. `Service_air_station_service_pipe` also intersects that gusset and now additionally intersects the same wall assembly's:

- `vertical_flange.001`;
- `splice_plate.001`;
- `splice_bolt.006`.

All five pairs have positive bounding overlap and evaluated triangle intersections; none is a zero-thickness tangency. The station-pipe/flange shared extents are approximately 28 × 47 × 610 mm, and the branch/gusset extents about 20 × 50 × 114 mm. Detailed triangles and world bounds are retained in the probe JSON. The branch no longer intersects the old `gusset_bolt.004`, but the overall wall-interference issue has not cleared. The additional flange/splice contacts are a regression in the station's new position.

### Major integration risk — widened enclosures introduce outboard masonry shoulders

The nominal aperture footprints, upper masonry, ceilings and endpoint steel now clear the external seam ownership checks within those footprints. **That is not a whole-shell seam pass.** Four plain masonry shoulder boxes still occupy neighbor-side space outside the nominal aperture:

| Saved object | Evaluated corridor bounds X / Y / Z, metres |
|---|---|
| `Wall_S0_0_-1.6_concrete` | −1.60…−1.42 / −0.34…−0.04 / 0…3.90 |
| `Wall_S0_0_1.42_concrete` | 1.42…1.60 / −0.34…−0.04 / 0…3.90 |
| `Wall_N24_0_11.4_concrete` | 11.40…11.58 / 24.04…24.34 / 0…5.90 |
| `Wall_N24_0_16.82_concrete` | 16.82…17.00 / 24.04…24.34 / 0…5.90 |

They sit 120 mm laterally outside the nominal opening edges but extend up to **340 mm** beyond the seam. F02's documented mapping places its two shoulders at reactor X±[2.62,2.80], Y14.16…14.46. The measured ownership overrun is real; intersection with actual neighboring wall solids was **not tested**. No neighbor was imported, and no approved adjacent wall ownership allowance was evidenced. This remains an integration risk even though it does not obstruct the nominal aperture test.

## Roller support: contact is real, without rail penetration

All four freight rollers have a rail directly beneath their minimum-Z vertices through **all 39** evenly spaced gate states. Roller bottom and corresponding rail top have zero evaluated Z separation. Independent short downward support rays hit in every state, with signed gaps below **0.1 micrometre** in magnitude. The roller/rail BVH contacts have zero vertical overlap thickness. This supports actual tangential contact, **not positive roller-into-rail penetration**.

The general closest-surface helper shows numerical values up to 0.443 mm for two rollers in some states; the direct vertical contact rays and exact common contact-plane bounds resolve that ambiguity. Contact is judged from those more specific witnesses, not from a forced interpretation of the helper distance.

The valid rail contact does not excuse the opposing-roller penetration above. Roller rotation and friction were not simulated; rigid translated geometry is sufficient for these cylindrical clearance/contact checks, not for runtime physics acceptance.

## Previously failing checks now pass within the audited scope

- **Freight gate fixed surround:** no positive moving-part/static-solid penetration was found in 39 closed-to-open states. Hangers clear the built-up cheeks/roof/rails. Leaf bodies, returns and pocket surrounds remain clear. The only positive gate-motion conflicts are the opposing rollers near closure. Four rivet/track witnesses at about 84.2% opening remain zero-thickness contacts, not penetration defects.
- **Crown/tray integration:** 39 crown/overhead, 884 tray/overhead and 204 tray/crown pair checks found no actual intersections. Conservative AABB separation remains about 20 mm crown/overhead and 107 mm tray/overhead.
- **Door heads and ceilings:** all five external/branch assemblies now clear the authored ceiling slab/panel/crossmember/height-step solids. CLEAN's previous direction-panel conflict is resolved. Minimum conservative AABB separations are about 130 mm F01/F02, 20 mm PLANT, 7 mm CLEAN and 630 mm WASTE.
- **Local air continuity and ceiling clearance:** branch-to-station and branch-to-loop centerline gaps are exactly zero; tube surfaces meet at both junctions. Both branch and station pipe clear local ceiling geometry. Supply ends remain explicitly reserved/capped; operating air supply is not simulated.
- **Nominal retained openings:** independent opening grids at all five declared dimensions now have zero blocked rays across 32,056 samples: F01 2.60 × 3.00 m, F02 5.00 × 5.00 m, S01/S02 2.00 × 2.50 m and S03 2.40 × 3.00 m. Sampled widths agree with those declarations. F01/F02 operating-envelope probes and all three straight 2.00 × 2.20 m branch walk-ups also clear (12,645 walk-up crosshatch rays plus floor samples). Actual leaves remain closed; cap/member exclusion is explicitly counterfactual, not a door-opening or through-neighbor passage test.
- **Seams within nominal footprints:** former F01/F02 endpoint flanges/splices, plain upper masonry and ceiling overruns are absent within the nominal mating footprints. The outboard shoulders above prevent a whole-envelope ownership pass.
- **Typed handoff integrity:** explicit assembly, port association, geometry owner, presentation-cap designation, removal scope and translation-space fields now exist for all 12 carriage records and agree with the saved hierarchy and flags. Each external freight cap has exactly 56 flagged moving members. All 34 markers, incident targets and 6,829 collision records resolve. Disk handoff, saved handoff, manifest and frozen build/detail/interface identities agree. This resolves the previous export-semantic omission; runtime controller, collision cooking and navmesh integration remain pending.

## Method and limits

The gate/service/head probe evaluated **2,161** selected mesh/curve objects in world space. Moving positions were translated copies of evaluated vertices; no Blender object was moved. Main motion sampling uses 39 states across 1.85 m travel, maximum step 48.7 mm, with eight additional near-closed roller diagnostics. Tests use evaluated BVH triangle intersections plus bounded two-ray containment supplementation. AABB distances are conservative bounds; positive surface contacts were separately classified against overlap thickness and support rays.

The independent branch probe repeats its evaluated nominal/operating crosshatches, walk-up/floor checks, shell bounds and typed-export comparisons. Finite rays/states do not certify a continuous sweep, branch turn/storage motion or complete all-object collision graph. This audit does not inherit the main validator's outcome, test a shared facility pose or provide visual acceptance. A subsequent save requires its own evidence.

Evidence in this directory: `astra-eng02-engineering-probe.py` and `.json`; `astra-eng02-branch-audit.py`, `astra-eng02-branch-evidence.json`, `astra-eng02-branch-shell.py`, `astra-eng02-branch-shell-evidence.json` and their CPU logs.

| Frozen checkpoint file | SHA-256 |
|---|---|
| build.py | `dc1cea2d148bda1f27f39eebaac29a4eb1fe163d7286a3212858cea5543d035d` |
| valorant_details.py | `7a9b0fbdf74ac4250e45341a74c24308e1f0db8c14ed8f3af9ad8a2512386499` |
| interface.json (P07) | `d410821c4fec77fa8cf49dfc9ba3f7acd7e34ebcd80559cd3513e1b5c731fcb7` |
