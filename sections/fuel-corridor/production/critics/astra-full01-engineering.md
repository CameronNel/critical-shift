# Astra independent engineering audit — full01 / P06

Date: 2026-09-11. **Targeted engineering acceptance: FAIL.** Actual saved geometry retains clearance and solid-intersection defects. This is an engineering review, with no visual scores and no claim of complete facility or runtime validation.

The frozen `production/checkpoints/full01/Fuel_Corridor.blend` was independently reopened in factory-started Blender 5.2 CPU processes. Its SHA-256 remained `b0e595264118404479147f72646a1f26038729d9b9fdc617911c2496c2b71909` before and after. It contains 6,949 objects and identifies itself as full01/full. No scene save, render, GPU use, carriage transform mutation, neighbor import or neighbor edit occurred. Only Astra critic evidence was written.

## Remaining findings

### 1. Major — refinery approach fails the retained freight envelope

The independent branch probe finds **226 blocked rays out of 3,416** through the F01 retained 2.40 × 2.20 m operating envelope after counterfactually excluding its presentation-cap carriage geometry. The blocking objects are inlet wall endpoint webs and splice hardware, rather than the cap. A measured cross-section between splice plates is **2.252 m**. This fails even the smaller sampled freight envelope acknowledged by P06; the nominal opening remains 2.60 × 3.00 m.

Other retained nominal openings also narrow at shell endpoint dressing:

| Port | Declared width | Witnessed cross-section |
|---|---:|---:|
| F01 refinery | 2.60 m | 2.252 m |
| F02 reactor | 5.00 m | 4.652 m |
| S01 plant | 2.00 m | 1.880 m |
| S02 clean | 2.00 m | 1.880 m |
| S03 waste | 2.40 m | 2.280 m |

These are witnessed sampled widths, **not certified global minima**. Other plate/bolt elevations may be tighter. Branch witnesses occur at cut-end wall flanges about 0.15 m inside their seams. Frozen `build.py:190–211` authors the endpoint steelwork. F02's smaller 2.40 × 2.20 m operating test passes. The actual saved branch leaves remain closed; removing them from the aperture test does not establish an operable open state.

### 2. Major — moving freight hangers penetrate the static lintel

`FREIGHT_GATE_leaf_carriage_hanger` and `.001` intersect `FREIGHT_GATE_lintel` at **all 39 sampled states**, including closed and authored open. Actual evaluated triangles intersect; this is not just a bounding-box candidate. At the closed state their shared bounding extents are approximately **0.080 × 0.085 × 0.100 m**. Hangers reach Z3.50 while the lintel begins at Z3.40. These extents describe the collision witness, not an overlap-volume calculation.

The typed collision policy makes these carriage members kinematic and the lintel static. No explicit mechanical exception or non-solid guide channel was evidenced. The represented engagement must therefore be reconciled before the gate's motion can be accepted. Frozen `build.py:264,292,297–300` identifies the involved construction and motion metadata.

Four rivet/track pairs also produce BVH contacts near 84.2% opening. Their X overlap is **exactly zero** in evaluated bounds; these are coplanar surface contacts, **not reported as positive penetration defects**.

### 3. Moderate — continuous recessed air feed intersects wall hardware

`Service_air_station_service_pipe` and `Recess_air_branch` both intersect `Wall_W-1.65_0_14.3_knee_gusset.001`; the branch also intersects `Wall_W-1.65_0_14.3_gusset_bolt.004`. Actual evaluated triangle intersections confirm all three pairs. The branch/gusset shared bounds are approximately 20 × 50 × 114 mm, and the branch/bolt bounds 11 × 23 × 23 mm. These are positive solid conflicts, separate from the now-correct feed endpoints.

Frozen `build.py:625–631` and `valorant_details.py:259,505` locate the network and station authorship. The evaluated station inlet and branch endpoint coincide exactly, and the branch joins the loop centerline exactly; both junctions have touching/intersecting tube surfaces. The old missing connection has been resolved. Supply ends remain explicitly reserved/capped, so this is local geometric continuity rather than a simulated operating air network.

### 4. Moderate — clean direction panel intersects ceiling steelwork

`CLEAN_PORT_direction_panel` intersects `Ceiling_crossmember.031`, with **44 triangle-pair intersections** and shared bounds approximately **0.120 × 0.040 × 0.030 m**. The panel reaches Z2.810 and the crossmember begins at Z2.780. Frozen `build.py:303–305,543` identifies the panel and ceiling construction. This is a separate head/detail conflict, despite the manual lintel fitting below the enclosure.

### 5. Major integration risk — generic shell steelwork still crosses external seams

The corrected door-owned construction stays inside the corridor: all five sills occupy 0.30–0.70 m inboard with top Z0; retained frames stay at least 0.19 m inboard and foundation shoes at least 0.17 m. F01/F02 carriage geometry also stays inside.

However, F01/F02 **generic shell** endpoint flanges extend about **60 mm** past their seams and low splice plates about **67.5 mm**. These are retained architecture, outside the presentation-cap roots. For example, `Wall_W11.7_0_21_splice_plate` reaches corridor Y24.067499. P06's separate F02 mapping places that bound at reactor Y14.432501, within the recorded reactor closed-slab depth band Y14.39–14.49.

Corridor seam trespass is measured in the saved scene. Collision with a neighbor is a **source-derived integration risk**, not an imported-neighbor intersection result. No global assembled pose, neighbor opening or passage is certified here.

**Additional plain-shell ownership check:** `Port_upper_masonry.001` at F01 and `.003` at F02 also extend **150 mm** beyond their seams, above the nominal clear openings. Their evaluated Z bands are 3.00–3.90 m and 5.00–5.90 m; the overrun maps to refinery X8.456664–8.606664 and reactor Y14.35–14.50 respectively. These are plain `mineral` mesh boxes from frozen `build.py:593`, not endpoint steelwork. They overlap the reserved neighbor footprint in plan without entering the nominal aperture height. The four adjacent plain concrete sidewalls stop at the seams. `Ceiling_inlet` and `Ceiling_reactor_adapter` additionally extend 10 mm beyond at Z3.918–4.118 and Z5.918–6.118. Again, these are measured ownership overruns, not proven neighbor-solid collisions. Exact evaluated bounds and mappings are in `astra-full01-branch-shell-evidence.json`.

### 6. Moderate handoff gap — typed door records omit ownership/cap semantics

The saved handoff is internally consistent in the tests performed: 34 typed markers (3 spawn, 3 incident, 14 audio, 14 network), all three incident targets, 12 carriage records and 6,687 collision records resolve and agree with scene properties. No missing, extra or duplicate collision records were found; navigation centerlines and the frozen interface hash agree. F01/F02 each have exactly 50 cap-flagged geometry members, matching their entire carriage geometry including hangers. Branches each have 50 carriage members and zero cap flags.

But each exported door record contains only carriage, pose, motion vector, members and pending controller/motion status. It omits an explicit presentation-cap designation, port association and removal/ownership assignment. A consumer must infer these from names or separate scene properties. Frozen `build.py:684–699` is the relevant export. This resolves the former absence of typed gameplay data but leaves the door ownership/removal handoff incomplete. Engine cooking, controller implementation, navmesh and runtime physics are correctly marked pending.

## Preflight items now supported by actual geometry

- No leaf-body, folded-return or pocket-surround intersection was found in the 39 freight-gate states, nor between opposing carriage members. The hangers above prevent an overall gate pass.
- Crown/ledge versus gate overhead: 27 pairs checked, no intersections. Tray versus gate overhead: 612 pairs, none. Tray versus crown/ledge: 204 pairs, none. The smallest crown/overhead AABB separation is about 20 mm; tray/overhead about 107 mm. Zero AABB separation for a cable/crown pair did **not** produce an actual triangle intersection.
- Both recessed station pipe and feed branch clear the local ceiling geometry. Station pipe/ceiling conservative AABB separation is about 90 mm. Wall-gusset interference remains as reported above.
- Actual door-versus-ceiling checks found no intersection for F01, F02, PLANT or WASTE. F01/F02 minimum conservative AABB separation is about 130 mm, PLANT about 20 mm and WASTE about 630 mm. The previously inadequate F01/F02 head enclosures are resolved in this saved geometry. CLEAN has the panel conflict above.
- Independent 5 cm crosshatches and floor checks found no obstacle or >5 mm floor discontinuity on the three straight **2.00 × 2.20 m walk-ups to the closed branch leaves**. This verifies neither turns nor leaf storage/motion nor through-door passage.

## Method, evidence and limits

The gate/service probe evaluated 2,111 selected meshes/curves in world space. Motion used translated copies of evaluated vertices, with 39 evenly spaced states over 1.85 m travel (maximum step 48.7 mm). It tested BVH triangle surfaces and supplemented contained-part detection with bounded two-ray parity samples. External assemblies were compared with the authored ceiling slab, panel, fixing, crossmember and height-step geometry. Branch analysis used independent evaluated rays and explicit cap/member exclusions.

Finite motion/ray sampling does not prove a continuous collision-free sweep. AABB distances are conservative lower bounds, not exact closest-surface distances. Structural mounting contacts were not treated as proof of runtime behavior. This report covers the requested preflight risks; it is not exhaustive all-object collision, support, full-route, carrier, engine or visual acceptance. No other validator's PASS was inherited.

Evidence in this same directory:

- `astra-full01-engineering-probe.py` and `astra-full01-engineering-probe.json`: reproducible gate, service and head/ceiling checks, object bounds and triangle witnesses.
- `astra-full01-branch-audit.py`, `astra-full01-branch-evidence.json` and `astra-full01-branch-run.log`: independent branch/ownership/handoff audit.
- `astra-full01-branch-shell-evidence.json`: narrow follow-up distinguishing plain-shell overrun from endpoint dressing.

Frozen source hashes independently match the saved scene properties:

| Checkpoint file | SHA-256 |
|---|---|
| build.py | `793a896616c4ae447ef3c9c5934c6f727d1c4fffc18742e08e387bde6330fa4b` |
| valorant_details.py | `c15cc85e16e18f51ea2d45ae71cc7d1ae995370973e99252ab57c2c24505a1ad` |
| interface.json (P06) | `8fcf53cd41c01de17ff68e5b71aa40f5b2b8d5459c71461c45e5585df8d10f60` |

Later mutable source changes or rebuilt revisions require their own saved-geometry evidence.
