# Reactor hall pass: owner brief, ownership and rules

## Owner correction pass — 2026-10-07

The owner now requests correction of all 140 numbered review items, with an
independent Luna critic and per-item evidence. This expands the previous pass's
rod-appearance exclusion for the listed rod/housing corrections. Preserve the
reference-derived twin-bank design, exact axes, equal rest heights, synchronized
motion, named bindings, pivots, port positions and parents. Different service
identification may clarify A/B; asymmetric mechanisms are not required.
The lift, anteroom and control-room interior remain outside this correction pass.
Continue the 01:45 Amsterdam integrated hall source as an additive candidate;
the canonical map and frozen module remain unchanged until separate promotion.
The current owner palette is neutral concrete/Audi grey with safety colours and
green/orange/red stability light; historical cyan references do not override it.

Candidate checks also cover actual wall bores, registered contact/sign samples,
cone footprints against floor guidance, the saved gantry guard inventory, and
actual inherited roof tube profiles/structural intersections. Legacy converted
mesh glyphs are included in the frontal signage audit.
`rh_roof_utility_audit.py` must reproduce the C59 small-loop/girder intersections
and distinguish the corrected 42 mm loops and 100 mm distribution trunk. It
also checks positive 0.5–5 mm separation between the three legacy glyph planes
and actual backing panels; exact registered rear-face seats remain subject to
the support audit.
`rh_gantry_guard_audit.py` verifies the posts/return rails and fixed-rail access
opening: it must catch the remote component loss from the former gate Boolean.
These scoped checks support the independent full-resolution item review; they
do not establish whole-room collision coverage or engine performance.

Owner brief (verbatim intent): **floors** become wet concrete with rain puddles, draining grates and roughness. **Walls** are redone in an appropriate colour with appropriate supports, detail and thickness, with accents and small assets. **Every asset in the scene** is redone "to perfection", work until perfect; an independent reviewer must score it **85 / 100 or better**.
Scope: the whole reactor hall and pool. **Out of scope (do not touch):** the lift itself (shaft, car, doors, ropes: objects `CR lift*`), the anteroom / area outside the lift on the top floor (`CR ante*`, `CR_*`), the control room (collections `31 CR CONTROL ROOM REDO`, `32 CR COLLISION`, `20 CONTROL MEZZANINE`) and the control-rod banks `RP bank*` / `BANK_*` geometry already rebuilt in `rp_rods.py` (pool surround, gantry and housings' surroundings are in scope; the rods are not).
Palette: weathered concrete, dark Audi grey (dark metallic grey), safety colours (yellow, orange, red, white). **STRICTLY NO TEAL, cyan, aqua, turquoise, plum, navy or purple** in any material, light, decal or text. The only green in the hall is the stability-driven pool/state glow (`pool_glow`, `R2 state glow`; green at stability 1.0, orange at 0.5, red at 0.1), which is lighting, not paint. Art direction: grounded stylised semi-realism (see `../RUBRIC.md`, `../../art/README.md`): readable silhouettes, anti-plastic material separation, quiet detail between focal machinery, no pipe spaghetti, no repeated bevelled boxes, no flat even lighting.

## Refinement roof clearance correction

The inherited roof geometry intersects the main trolley, while its longitudinal
girders intersect the travelling hoist ropes. The correction candidate raises
the roof-girder bases to 16.60/16.75 m and the complete RF roof assembly by 1.67 m,
including all sixteen glazing panels and modeled lamp lenses, excluding the sky
proxy. Built perimeter columns bear on measured existing ring/column surfaces
(13.70 or 14.40 m); an upper
enclosure closes the added roof zone. Pool-crane hanger plates seat against the
raised longitudinal girders. These levels supersede the historical roof levels
below for the correction candidate and require contact, clearance and visual
review. The main bridge's decorative loop is constrained to its installed north
bay (centre y4.60–4.30); its timing and frame-one placement remain intact. Rod
motion, named ports, lift and control-room geometry remain protected.

## Scene facts
Metres, floor z = 0. Hall = octagon `r2lib.V = [(-6,-10.8),(6,-10.8),(10.8,-6),(10.8,6),(6,10.8),(-6,10.8),(-10.8,6),(-10.8,-6)]`; `WALLS[i]` runs V[i] -> V[i+1] (u along the wall, v into the hall, `Wall.pt(u,v)`); wall 0 south, 1 south-east diagonal, 2 east, 3 north-east, 4 north, 5 north-west, 6 west, 7 south-west. Wall height 15 m, girders at z 13.7-13.9, skylight roof above. Door openings (`j3_rebuild_architecture.py`): wall 1 COOLING PLANT (centre 3.395, half width 2.8), wall 4 FUEL HANDLING (6.0, 2.8), wall 6 MAIN ACCESS (6.0, 3.0), height 5. Pool at the origin (water r 3.39, curb r 3.43, floor opening r 3.95). Rod banks hang from housings at x = +-1.4 (z 9.7-12.6). The control-room mezzanine and the lift occupy the south-west / south of the hall (x -9.1..2, y -12..-5); equipment stands under the mezzanine.
Existing build history is in `README.md` and the `j3 / k1 / m1 / n2 / o1 / q2 / pipes_and_cables / ports` scripts; the scene is a merged result, so inspect objects, do not assume the scripts regenerate it.

## Ownership (each builder only deletes and replaces its own objects)
| Area | Script | Owns |
|---|---|---|
| FLOOR | `rh_floor.py` | object `R2 floor`, collection `23 R2 FLOOR AND DRESSING`, floor markings/graphics/hatches, new floor details |
| WALLS | `rh_walls.py` | collection `22 R2 ARCHITECTURE` (walls, columns, cornices, door frames, signs; NOT the floor object), `30 R2 DOOR STUBS` (keep animated leaves), `02 ROOF STRUCTURE`, `RF APPROVED SKYLIGHT ROOF`, new wall-mounted small assets |
| STATIONS | `rh_stations.py` | `27 R2 STATIONS`, `28 R2 HERO STATIONS`, `29 R2 DRESSING 2`, `22 ASSET KIT 1`, `05 PERIMETER EQUIPMENT`, `MF WORKFLOW MACHINERY`, `WA..WF` collections (generator, reserve power A/B, grid cabinets, turbine, fuel bay and racks, waste cask, pumps, valves, benches, cones, crates, barrels ...) |
| SERVICES | `rh_services.py` | `24 R2 PIPING AND CABLES` (pipes, cable trays, hangers, risers), `25 LIGHTING` fixtures (not the state-driven pool lights' behaviour) |
| POOL | `rh_pool_surround.py` | `03 POOL AND RAIL` except water and glow (curb, rim, guardrail, gate, controls/console, SCRAM etc.), gantry and roof hangers in `04 BANK MECHANISMS` (not `BANK_*` nor `RP bank*`) |
Shared, do not edit: `crk.py`, `r2lib.py`, `cr_*.py`, `rp_*.py`, `rh_mats.py`, `rh_views.py`, `rh_contract.py`. Add your own helper module if you need more.

## Rules
1. **Stage interface:** `python rh_<area>.py -- <in.blend> <out.blend>`; `in.blend` is `hall_base.blend` (the current shipped hall); your script must produce the finished area from it, deterministic and re-runnable. Stages are later chained in series (floor, walls, stations, services, pool) on one blend, so touch ONLY your own objects and new objects named `RH <area> ...` (join per (group, material) with `crk.Kit.build` / `r2lib.Acc` so the object count stays reasonable, a few dozen per area, not thousands).
2. **Contract (`rh_contract.py`, snapshot `hall_contract.json`):** every EMPTY (ports, pivots, state), every object with animation/drivers, every UPPER_CASE_NAME mesh (SCRAM_BUTTON, COOLANT_PUMP_START, BYPASS_SWITCH ...) keeps its name and pivot; meshes stay within 40 cm. Restyle freely but keep those objects (replace their geometry in place like `rp_rods.swap`). Port empties (`23 ASSET PORTS`, `PORT_*`) must not move: pipes and cables connect to them (`verify_piping.py`, `clearance.py`, `piping_runs_generated.json`). Run `rh_contract.py -- check hall_contract.json <out.blend>` (needs CONTRACT PASS).
3. **Materials:** use `rh_mats.lib()` (concrete, Audi grey, steel, galvanised, cast iron, safety colours, rubber, brass, hazard stripes). Define extra materials only with the prefix `RH <area> ...` and keep the total small (a handful per area, shared across objects). No per-object unique materials.
4. **Animation / emission:** anything moving or pulsing is driven by scene SECONDS through `crk.drv(..., expr)` using `T` (never the raw `frame` variable); `fps_independence_check.py -- <blend> --prefix ''` must pass. Light rig: keep the stability-driven pool/state glow drivers; do not add many lights (the hall already has 47); emission must not wash the hall.
5. **Checks to run on your output** (all under `scripts/`, Blender python is `/tmp/bv/bin/python`): `cr_verify.py -- <blend>` (RESULT PASS), `verify_piping.py -- <dir> <file.blend>`, `clearance.py -- <dir> <file.blend>` (0 clashes), `fps_independence_check.py -- <blend> --prefix ''`, `rh_contract.py check`. Scratch space: your own directory under `/tmp/claude-0/-home-user-critical-shift/5ebcceb3-8a21-50cc-b118-020108004558/scratchpad/`.
6. **Looking:** render with `rh_views.py -- <blend> <out_dir> 20 [--only h01_hero,...] [--state 0.5]` (Cycles CPU, 4 cores shared with other builders: use 16-24 samples, 960x540, a few views at a time) plus your own close-ups with `cam.shoot(name,loc,target,out,lens,res,samples)`. Open the images and judge them against `../RUBRIC.md` and the owner brief before every revision. Check at stability 1.0 (green), 0.5 (orange), 0.1 (red).
7. **Quality bar:** stylised-clean grounded semi-realism: crisp silhouettes, believable construction (supports, brackets, fasteners, thickness, reveals), material separation (concrete vs painted steel vs cast iron vs rubber), small purposeful assets, quiet space between focal pieces, nothing floating or unsupported, no veto items (repeated bevelled boxes, uniform plastic response, flat lighting, toy-like equipment, pipe spaghetti). Triangles are not capped; do not go silly (keep the hall under ~600k total).
8. **Honest report:** at the end give: what changed, what deliberately did not, what you ran (with results), what is not verified or still weak, and the paths of your script and final renders. Do not claim a pass you did not see.
9. Other builders work at the same time on the other areas; do not fix things outside your area, note them in the report instead. Do not commit or push; do not touch GitHub.

The required camera-sign regression in `rh_refine_audit.py` checks ZONE C from machinery view01 and ZONE A/the retained safety warning/the EMERGENCY COOLING header from cooling machinery view02. Each must retain in-frame glyph samples with no opaque obstruction. This is a finite placement gate; full720p text readability remains independent visual review. `rh_zone_sign.py` moves merged zone backing/trim/glyph components together and attaches the safety warning to a measured backed assembly.

The rod-guide gate (`rh_rod_guide_audit.py`) requires actual through-bores in the retained fixed housings, fixed annular guide seats, positive nominal shaft clearance throughout all480 sampled poses, cap clearance above the guides, and5–10mm actual central-column/grid-sleeve gaps at41 vertical stations and64 azimuths for each of seven sleeves per bank. This finite retained-animation gate does not claim arbitrary runtime poses or global collision coverage. Final guide appearance requires independent current720p evidence.

The blind-cover gate (`rh_blind_cover_audit.py`) checks both retained EC header ends: 770 finite cover-face rays, 20 bolt-head axes, registered plate/flange and bolt/plate contacts, and closed manifold plate meshes with positive signed volume. C70 passes; the uncorrected C69 scene fails the retained negative regression. These checks cover the two specified terminations, not every pipe joint. Full-quality current-scene appearance requires separate independent visual acceptance.
