# Fuel Corridor — P01 connection contracts

This document records an independent read-only audit of existing source, then a proposed section-local connector. Existing rooms were not imported, moved or rebuilt. A source-derived dimension is not a whole-facility collision or runtime passage check. `../interface.json` owns the proposed connector geometry; `A101-plan.svg` is generated from it by `build_plan.py`.

## Source authority and coordinate convention

All coordinates are metres, Z up. Each existing department has its own local frame. A threshold center is the center of the opening at finished-floor level; add half the opening height for its geometric center. No authoritative shared facility placement was found.

- **RF**: `C:/Users/Camer/Games/critical-shift/worktrees/refinery-compact/sections/refinery`.
- **RR**: `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/sections/reactor-room`.
- **SPEC**: `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/GAME_SPEC.md`.
- **Run brief**: `C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md` and `briefs/fuel-corridor.md`. Its current mine instruction is shallow decline, no mine elevator; that overrides the old Mine Lift sequence at SPEC:2395–2411.

Refinery source is the saved corrected department authority, but its own final-art/cold-start acceptance remains incomplete: RF/production/TASK_STATE.md:11–19,41–43. The reactor's current source is RR/blender/build_scene.py, matching archived art-08 and validation SHA256 `9c2d57ba4aca3243cb0c4af66483e002a1cac50ddd1086bbe5607c6fb7061593`. RR/art/renders/art-08/validation.json:2–3,449–450 records matching source, pass and cold-start true. Those checks do not test passage through the fuel link. Foundation checkpoints and foundation_manifest.json are superseded layout history, per RR/production/TASK_STATE.md:11–15.

## Existing measured and source-derived interfaces

| Department interface | Threshold center | Outward normal | Nominal W × H | External seam / ownership |
|---|---|---|---|---|
| Refinery REACTOR | (7, −3.65, 0) | (+1, 0, 0) | 2.60 × 3.00 | (8.10, −3.65, 0), refinery owns 1.10 m sill |
| Refinery MINE | (−7, −3.65, 0) | (−1, 0, 0) | 2.60 × 3.00 | (−8.10, −3.65, 0), refinery owns 1.10 m sill |
| Refinery ENTRY | (−1.8, −6, 0) | (0, −1, 0) | 2.40 × 2.60 | Personnel threshold; no long sill authored |
| Reactor FUEL HANDLING | (0, 10.8, 0) | (0, +1, 0) | 5.00 × 5.00 | (0, 14.50, 0), reactor owns 3.70 m stub |
| Reactor MAIN ACCESS | (−10.8, 0, 0) | (−1, 0, 0) | 6.00 × 5.50 | (−14.50, 0, 0), reactor owns 3.70 m stub |
| Reactor COOLING PLANT | (8.4, −8.4, 0) | (+√½, −√½, 0) | 5.00 × 5.00 | (11.016295, −11.016295, 0), reactor owns 3.70 m stub |
| Reactor CONTROL ACCESS | (10.8, 3.6, 0) | (+1, 0, 0) | 4.00 × 5.00 | Existing P02 vestibule and stairs; not an external section reservation |

**Refinery evidence.** RF/blender/architecture.py:10–22 defines floor Z0 and the shell; :53–55 defines three portals; :62–85 defines their physical components and markers. The REACTOR sill occupies X7.00..8.10, Y−4.95..−2.35, with finished floor Z0. Threshold soffit underside is Z3.01; the doorway lintel underside is Z3.00. At Z0..1.04, yellow bollards have inner Y faces −4.895 and −2.405, leaving **2.49 m**, despite the 2.60 m nominal marker. Stored verification RF/production/validation_report.json:3319–3325 passed 104 rays over **2.40 m width × 2.20 m height**, with no obstructions. This smaller sampled rectangle, not the full nominal aperture, is the verified scope. The central 2.20 m refinery route is clear in the same report :3296–3309.

**Reactor evidence.** RR/blender/build_scene.py:53–60 defines the local transform; :497 gives the octagon; :578–635 authors ports and retained stubs. The fuel stub floor/walls run from Y10.80 to Y14.50. The distant closed slab occupies **Y14.39..14.49**, and decorative door leaves **Y14.33..14.39** (:590–591). Those are static boxes with no evidenced opening controller. The existing fuel connection is therefore **blocked in the authored state**. This connector stops at the outer seam; it does not remove, duplicate or claim to open reactor-owned geometry. Main and cooling stubs use the same closed construction. Source-derived fuel throat width between bumpers is **4.98 m** below Z1.35; its central headlight underside is **Z4.85** (:580–584). These local bounds are not a swept clearance check. Finished floor is Z0 (:539–542,588); the radial substrate at Z−0.035 is below the finished slabs.

## Proposed connector topology and independent mating transforms

Connector-local F01 is (0,0,0), with +Y entering the new section. F02 is (14.2,24,0). The freight centerline is `(0,0) → (0,10) → (14.2,10) → (14.2,24)`, length **38.20 m**. The service bypass is `(0,10) → (0,19.8) → (14.2,19.8)`, length **24.00 m**. These positions and floor cells are preserved from P01.

For column vectors, `p_adjacent = R p_connector + t`:

| Independent mapping | Rotation about Z | Translation t | Endpoint proof | Normal proof |
|---|---:|---|---|---|
| F01 into refinery frame | −90° | (8.10, −3.65, 0) | (0,0,0) → (8.10,−3.65,0) | Connector outward (0,−1,0) → (−1,0,0), opposite refinery +X |
| F02 into reactor frame | 180° | (14.20, 38.50, 0) | (14.2,24,0) → (0,14.50,0) | Connector outward (0,+1,0) → (0,−1,0), opposite reactor +Y |

These are **two separate alignment equations**, not simultaneous placement evidence. The existing room poses are unchanged. No approved relative refinery/reactor pose, global clash test, complete wall-to-wall assembly or cross-section navigation test is supplied. Assembling all three modules needs their owners' authoritative world poses and a collision audit, while retaining the existing sill/stub ownership.

| Proposed service header | Local center / outward | Clear W × H | Intended topology | Status |
|---|---|---|---|---|
| S01_PLANT | (−5.4,17.4,0), −X | 2.00 × 2.50 | Cooling / turbine / electrical service header | New reservation only; endpoint, levels and circulation unverified |
| S02_CLEAN | (6.6,21,0), +Y | 2.00 × 2.50 | Medical / reanimation / compliance | New reservation only; no clean/dirty operational separation validated |
| S03_WASTE | (16.4,16,0), +X | 2.40 × 3.00 | Waste-transfer branch | New reservation only; destination handling and containment unverified |

These headers identify plausible destinations without promising a seamless fit or building those rooms. The plant header is a shared service connection, not a claim to three distinct completed doorways. Geometry of the reservations remains P01.

## Fuel and carrier compatibility

The original new carrier is a **2.20 m long × 0.90 m wide × at most 1.30 m high cradle trolley**, including its handle. It carries one envelope of **1.95 m length × Ø0.52 m maximum diameter**, taken from the current reactor's largest receiving cartridge and closures. This trolley is a connector implementation decision and is not a copy of an existing asset.

| Existing evidence | Dimensions / meaning | Source |
|---|---|---|
| Refinery delivery trolley | Deck world X0.80 × Y1.20 m; approximately 1.155 m to handle top | RF/blender/machines.py:215–220,319–337 |
| Refinery completed fuel unit | Casing Ø0.170; retention-band maximum Ø0.184; overall length 0.480 m; six units shown on trolley | RF/blender/machines.py:237–253,335–336 |
| Reactor receiving cartridge | Body Ø0.460 × length1.950 m; closure Ø0.520 | RR/blender/build_scene.py:937–946 |
| Reactor sample caddy | Separate sample equipment: tray1.22 ×0.81 m, cap span1.34 m, handle top about1.295 m | RR/blender/build_scene.py:1077–1088 |
| Unloaded ore-cart source mesh | 1.647522 ×2.488 m plan bounding envelope, local Z0.103..1.450 | RF/assets/cart_geometry.json:1, recorded bounds |

Refinery world coordinates are preserved when parenting (RF/blender/geometry.py:33–35,50–55), so its trolley pivot Z0.20 does not add 0.20 m to its geometry height. Its West mapping is `(a,b,z) → (5.35+b,−3.45−a,z)` (machines.py:215–220).

**Unresolved transport semantics:** small refinery fuel units and long reactor cartridges are different authored payloads. Their packing, conversion, assembly, ownership, compatibility and loading mechanism have not been established. The new long-cask carrier is sized for the reactor envelope, but this does not prove interchange or a production process. The existing refinery trolley cannot contain the long cartridge on its deck. Ore-cart dimensions are contextual only; no ore-cart route through Fuel Corridor is asserted.

The bare centered trolley rotation diameter is `sqrt(2.20²+0.90²) = 2.376973 m`. A **3.00 m operating circle** at each main freight turn is a design allowance, not measured wheel steering or operator-body clearance. The main corridor has 4.40 m nominal straight bays, larger turn bays, a 2.60 m inlet and a 5.00 m terminal adapter. The 2.40 m bypass would leave only about 11.5 mm per side around a centered bare rotation before dressing; its minimum dressed width is only 2.00 m. The long-cask trolley is therefore assigned **freight centerline only**. No bypass turning claim is made. A 2.20 ×0.75 ×1.10 m stretcher is an explicitly assumed design envelope; team-carry movement still needs runtime testing.

## Travel, thresholds and completion boundary

SPEC:2414–2432 gives adjacent-area10–20 s, refinery-to-reactor15–30 s and full crossing under60 s, plus alternative maintenance/emergency/compliance routes. It does not give numerical player speed. P01's assumed loaded speed1.50 m/s gives **25.47 s for the connector alone**, excluding existing room legs, doors, loading and turns. Adding the existing refinery sill1.10 m and reactor stub3.70 m alone gives43.00 m /1.50 = **28.67 s**, leaving little room for those other delays. The full refinery-to-reactor travel target is **not verified**.

New thresholds target Z0 with upstand at most5 mm, an implementation decision. Existing adjacent floors are also Z0 in their own frames. The plan depicts architectural clear envelopes; trims, parked equipment, door leaves, low fittings, interaction poses, cart motion and runtime collisions must preserve them. Architectural plan acceptance cannot substitute for those checks. Reactor opening state and all three external service destinations remain explicit handoff work.
