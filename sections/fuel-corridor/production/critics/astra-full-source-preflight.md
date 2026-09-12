# Astra engineering preflight — planned full stage / P04

Date: 2026-09-10. **Source review only; full scene not built or accepted.** No visual scores are assigned to unseen geometry. No Blender process, GPU render, neighbor import or scene mutation was used. Only this report was written.

The brief requires believable freight turns, thresholds/doors, a service bypass, handling clearance and honest measured connection data. The master brief preserves neighboring ownership. GAME_SPEC 23.4 requires modular collision/navigation and gameplay handoff data; the production protocol separately requires intersection, clearance, support and cold-start validation. Engine implementation remains engine-owned (protocol lines 574–589).

All source paths below are relative to `sections/fuel-corridor/`. Build/detail/interface hashes were confirmed against the preserved `production/checkpoints/style19/` copies. References to those files identify that captured source, not subsequent mutable edits. Validator and contract hashes are also recorded at the end. No later save is certified by this review.

## Findings requiring engineering resolution

### 1. Major: full-only bulkhead returns intersect the authored open gate leaves

**Source-derived positive solid overlap.** `blender/build.py:251–253,607` places the open FREIGHT_GATE leaves using width 3.4 m and heading −90°. Their undeformed box bounds are:

- Both leaves: X 6.420–6.520, Z 0.030–3.370.
- South leaf: Y 6.4625–8.1375. North leaf: Y 11.8625–13.5375.

The full-only `Gate_steel_return` boxes (`build.py:609–612`) occupy X 6.180–6.520, Z 0–3.400, with Y 7.800–8.060 and 11.940–12.200. Each therefore overlaps its open leaf by **0.100 × 0.260 × 3.340 m** before small bevel trims. This is substantial interior overlap, not a tolerance-level edge contact. The figures identify the problem; they are not replacement geometry instructions.

P04's pocket cells exist in the full floor-cell union (`interface.json:229–248`; `build.py:493–509`), so they do create architectural space. Their addition alone does not remove these later bulkhead solids. The open leaf also extends 0.3375 m beyond the pocket's passage-side boundary, although it remains outside the nominal 3.4 m aperture. The contract's statement that the pockets contain the open leaves needs to be assessed against the complete bulkhead/leaf assembly, not pocket dimensions in isolation.

### 2. Major risk: gate machinery, crown and longitudinal tray share solid volume

**Source-derived overlaps; no evaluated full-scene collision test.** The full `Gate_crown` occupies Z 3.800–4.400 (`build.py:613`). The generic gate motor cover occupies Z 3.670–3.950 (`:245,607`) and intersects the crown across a broad area: **0.150 m of vertical overlap**. Several nearby drive mounts are also in this transition; their intended structural penetrations versus unintended burial need explicit review.

The full longitudinal tray rail at Y 8.28 spans Z 3.720–3.840 (`:585–589`) and crosses the motor-cover footprint. It also intersects the crown's lower 0.040 m. Cable paths at Y 8.095 and 8.15 traverse the motor-cover volume. These are not moving-leaf checks, but they can still yield impossible service routing, obscured machinery and inaccessible maintenance faces. No sleeve/cutout or intentional intersection exception is expressed by the inspected source.

### 3. Major: the recessed service-air station has no authored feed connection

**Confirmed source discontinuity.** The active implementations come from `valorant_details.py`, loaded before `shell()` (`build.py:603–605`); the earlier same-named `pipework()` in build.py is superseded.

The staging station is internally coherent: `Bay_air_header` ends at (3.40,13.04,2.25), exactly matching the transformed staging-station inlet (`valorant_details.py:242,259,474`).

The full-only recessed `Service_air_station` uses the same local inlet with origin (−1.65,14.95), heading +90°, inlet height 2.46 (`:253–259,504`). Its inlet is consequently (−1.49,14.55,2.46). The nearest centerline point on full `Service_air_loop` is (0.91,14.55,2.67), approximately **2.409 m away** (`build.py:598–601`). There is no branch connecting them in either active file. The loop also has no declared supply interface or connection to the capped staging header. This is an authored-network gap, not a claim that the depicted system was simulated and failed.

### 4. Major risk: that inlet intersects the recess ceiling details

**Analytic source intersection.** P04 gives the recess height 2.45 m (`interface.json:219–227`). The shell's coffer generation places the recessed ceiling panel bottom at that height (`build.py:520–526`). The station's vertical inlet reaches 2.46 m, leaving **10 mm of pipe/coffer overlap** at its endpoint.

The first recess ceiling crossmember also intersects the vertical inlet. Its generated Y range is 14.40–14.52 and Z range 2.23–2.45 (`build.py:516–519`); the inlet center is Y 14.55 with 0.042 m pipe radius (`valorant_details.py:259`). The envelopes overlap in Y by about 12 mm, with positive pipe/beam volume across the vertical segment. This is separate from the missing feed above.

The recess itself is a sound circulation reservation: the handwheel's greatest projection remains around X −1.31, outside the nominal bypass boundary X −1.20. This source fact supports the recess intent, but it does not certify the full dressed route, all wall details or stretcher motion.

### 5. External door ownership and advertised clear openings remain unresolved

**Source facts:** all five external/branch doors are authored closed (`build.py:614–619`). Carriage pose and translation metadata exist, but the code explicitly states controller/sweep status is unverified (`:273–274`). Only F01/F02 parts are marked presentation caps (`:268–270`); branch doors are actual closed section geometry. There are no branch-door open-storage reservations equivalent to the internal gate pockets.

**Derived integration risks, not observed assembled collisions:**

- Every sill is 0.40 m deep and centered on its seam (`:277`). The documented F01/F02 mating equations therefore place **0.20 m inside the neighboring owned sill/stub footprint**. The neighbor contract reserves those existing sill/stub lengths (`architecture/CONNECTION_CONTRACTS.md:14–16,24–27`). No ownership/overlap resolution is specified, and cap removal retains the sill.
- The F02 closed cap leaf spans corridor Y 24.07–24.17. The documented mating equation maps it to reactor Y 14.33–14.43, overlapping the recorded existing leaf/slab bands (`CONNECTION_CONTRACTS.md:16,25`). This uses recorded neighboring data, not a new audit of the neighbor's current saved scene. The contract correctly states that the reactor closure remains blocking.
- Leaf hangers are created **after** the cap flags (`build.py:268–271`) and are not among `validate.py:45`'s cap suffixes. They remain after the validator excludes cap panels. Their lower surface is h−0.12, reducing clearance locally to **2.88 m at F01 and 4.88 m at F02**, below those ports' declared full clear heights. The 2.20 m freight test would not reveal this nominal-opening discrepancy.
- PLANT_PORT's heading makes its label/front face point global −X, toward the reserved destination (`build.py:236,278–280,614`), rather than toward the corridor approach. This is a source-derived wayfinding orientation issue, not an unseen-pixel score.

The brief permits clearly identified unverified mating; it does not require inventing destination dimensions or moving existing rooms. Current separate transforms and explicit closed-door caveats should be retained. They must not be presented as a seamless assembled passage.

### 6. Major: F01/F02 head construction exceeds its authored enclosure

**Source-derived height and intersection issue.** F01 is authored at h = 3.0 m in the 3.0 m inlet cell; F02 is authored at h = 5.0 m in the 5.0 m reactor-adapter cell (`interface.json` floor cells; `build.py:618–619`). The generic lintel spans **h to h+0.26**, and the motor cover spans **h+0.27 to h+0.55** (`build.py:244–245`). Both assemblies therefore extend beyond the declared ceiling, with motor-cover tops at 3.55 m / 5.55 m and no explicit extra head enclosure in the cells.

The floor-cell ceiling slab occupies **h+0.018 to h+0.218** (`build.py:509`), so its internal footprint overlaps the lintel through the slab's full 0.20 m thickness. The direction-panel geometry also intrudes into this roof region. The motor cover is above the slab rather than contained beneath it. This is not a report of measured player headroom: it is a source-level enclosure/solid-intersection defect that must be reconciled with the portal and ownership design.

## Validator coverage that does not establish these checks

`validate.py:473–474` explicitly allows different-part assembly intersections in the attachment graph. The geometry audit catches exact coincident geometry, not every different solid sharing volume. Consequently, a support PASS can coexist with the gate/roof penetrations above.

`validate.py:572–590` tests the freight route at 2.40 × 2.20 m, the bypass at 2.00 × 2.20 m, two freight operating cylinders and nominal stretcher motion. It does **not** test the full 2.60 m declared freight minimum or each port's full nominal opening. It also does not validate the plant branch centerline, clean/waste branch approach volumes, a continuous moving-gate sweep, leaf/pocket fit, utility-network continuity or neighboring assembled geometry. The report already honestly discloses several of these limits.

Required later evidence should therefore include:

- Targeted evaluated leaf/static-solid intersection checks in the authored open and closed states, plus a sampled or swept carriage path against its fixed surround and services.
- Full-stage service-station/ceiling clearance, member support and explicit feed/termination connectivity checks.
- Each branch approach and retained external frame/sill opening checked at its declared usable dimensions, with closed leaves and cap exclusions separately reported.
- Separate seam ownership/overlap review under the documented mating equations. A corridor-only route PASS is insufficient evidence of neighbor passage.

These are technical acceptance checks, not instructions to build full geometry before the style gate passes.

## Missing or incomplete handoff data

The interface already provides units, axes, origins, floor cells, port normals/dimensions, local transforms, conservative handling allowances and honest timing caveats. The 38.20 m connector-only estimate is 25.47 s at the assumed 1.50 m/s; adding the recorded sill/stub lengths leaves 28.67 s before room legs, turns, handling or door delays. GAME_SPEC's 15–30 s refinery-to-reactor target therefore remains unverified, with little allowance at that assumed speed.

Before claiming runtime handoff readiness, the package needs an explicit mapping or pending-owner declaration for GAME_SPEC 23.4's collision/navigation assets, spawn markers, incident hooks, audio zones and network relevance boundaries (`GAME_SPEC.md:2434–2448`; also acknowledged by `architecture/SPEC_CONTENTS.md`). The inspected build/contract contains no typed handoff entities for those systems. This does not require implementing the engine inside Blender; it requires making the handoff complete and unambiguous.

Door handoff also needs a complete component inclusion/removal list, motion-vector coordinate-space semantics, open/closed clearance evidence and ownership for cap/frame/sill/controller work. Destination-specific adapters and fuel packing/conversion remain explicitly unverified, as permitted by the brief. There is no shared facility pose or end-to-end runtime acceptance to inherit.

Minor provenance issue in the captured interface: line 4 says P04 while line 9 begins P03. **Resolved during this review:** the current interface readback now begins P04, hash `5f553e47adca3c1bcdaf1c539242c68dd0a46c43d3c05211b5ae842467baffb0`. This status-text correction does not change the captured geometric findings.

## Reviewed source identity

| File | SHA-256 |
|---|---|
| blender/build.py | `a55f4b584cc6367505fc1bf6a8b0b63675e6bfaf94c74185468159920d9a32ff` |
| blender/valorant_details.py | `71ecc0a0d8117434c48f216edbc2cf54f057ad6be340e1a1368680fa7259f313` |
| blender/validate.py | `cd6b4ba288efdfff157d8fa2d5e8ceb031ab3089615d5d1d9be649c3bed719cb` |
| interface.json | `37c251e45186fc368dd22408ac44b2d9bb82b565ef6279febeda0bf4bd11cc26` |
| architecture/CONNECTION_CONTRACTS.md | `56b1e968f32bdcfdb0872e77a46ae536e25cde71600c7b403af4bc429a9dcc4a` |

An independent read-only subreview covered external doors and handoff requirements. The reported numerical overlaps are source derivations, not fabricated outcomes from an unbuilt full scene.
