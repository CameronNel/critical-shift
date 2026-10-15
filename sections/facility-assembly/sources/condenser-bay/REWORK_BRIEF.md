# Condenser bay rework: brief for Codex (2026-10-14)

Owner, on the combined-map render of the condenser bay: *"It looks terrible. Rework it to perfection."* Then: *"give instruction to codex on
where and how to rework the condenser bay without breaking anything"*. This file is that instruction. Read it whole before starting.

## 1. What is wrong, and why

The map shows `module_aaa_A1.blend`: the reviewed R34 room (`module.blend`) with a procedural grime layer added by
`condenser_aaa_finish.py` (see `AAA_FINISH.md`). That layer is the problem:

- `wall_plaster()`: rust inside Voronoi "chip cells" picked by a noise at scale 7, plus cavity grime. On 6 m walls it reads as orange and
  black **camouflage blotches**, not plaster or concrete.
- `machine_detail(..., rust=.4)`: a "rust bloom" on the painted steel in `RUSTY` and on `Oiled iron` (the condenser plinths and supports
  turn the same orange-black camo).
- `floor_screed()`: a wet, cracked, stained slab with dark rims everywhere.
- `mood()`: battens cut to 30 %, other lights to 50 %, exposure -0.5 EV, world fill 0.03. The room goes muddy rather than dramatic.

`design/ART_DIRECTION.md` lists "a grunge-covered abandoned bunker" as an explicit **non-target** (section 1.2). Section 9 says the facility is
"active and maintained", with wear that is localized and plausible. Painted metal, bare metal, concrete, rubber and flooring must be
distinguishable without labels. A1's own notes admit it is heavier than the art direction.

Also note: before A1, a "restrained" version (calm floor, bright flat ambient light) was **rejected by the owner** as looking bad. So the
target is neither flat-clean nor grunge. It is believable, well-made industrial materials with real surface detail, readable value
contrast, and wear only where things are touched, walked on or leak.

## 2. Where to work

- Folder: `sections/facility-assembly/sources/condenser-bay/` (the map-facing module). The section history lives in
  `sections/condenser-bay/` (`production/TASK_STATE.md`, `FINAL_HANDOFF.md`, `RUBRIC.md`, cameras). Read those for the room's design
  intent and its R34 review. Add a short note to its TASK_STATE when done.
- **Start from R34 `module.blend`** (independently reviewed geometry: Luna 91 to 94 per category), **not** from A1's materials. You may
  reuse A1's `trim_geometry()` triangle-budget step, but none of its material or light changes.
- Write a new script `condenser_finish_A2.py` that opens `module.blend` and saves a **new additive file** `module_aaa_A2.blend`, plus
  `finish-A2-build.json`, `FINISH_A2.md` and a `renders-A2/` folder.
- **Do not modify:** `module.blend`, `module_aaa_A1.blend`, `accepted.blend`, `contracts/`, any other room, the front end or its
  cafeteria revamp (PR 105), or the combined map scripts. The only exception is the one-line source switch in section 5.
- The condenser bay is "built but not ready" in `AGENTS.md`, so an art pass is allowed. The owner asked for it.
- Fetch files one at a time: `git lfs pull --include=sections/facility-assembly/sources/condenser-bay/module.blend` (it is an LFS
  pointer until hydrated). Never use a broad sparse checkout; it has filled the cloud disk before. Run `df -h /` before big renders.
- Load `.agents/skills/blender-headless/SKILL.md` and `.agents/skills/blender-uv-texturing/SKILL.md` first. Use Blender 5.2.2 headless.

## 3. How (art targets)

1. **Painted steel** (`Astra ivory painted steel`, `Service ochre enamel`, `Structural painted steel`, `Oxide orange enamel`,
   `Light oxide enamel`, `Safety burgundy`, `Charcoal impact dado`):
   - factory paint with fine roughness variation and slight orange-peel;
   - restrained edge wear only on contact edges (handrails, hatch rims, kick zones, bolt heads);
   - no rust on painted faces except small, explained spots (drips under valves, flange weeps).
2. **Bare metals** (`Oiled iron`, `Machined cast iron`, `Astra brushed fastener steel`, `Service brass`, rubber): physically distinct
   metalness and roughness. Machined faces should read machined; oiled iron should be dark with a subtle sheen, not orange.
3. **Walls** (`Warm mineral plaster`, `Dense cast concrete`): an even mineral surface with formwork or panel joints and tie holes. Keep
   large-scale tonal variation within about ±8 % value. Grime only at the floor line and under services. **No orange.**
4. **Floor** (`Basement coated concrete`, `Replacement floor patch`): coated concrete with saw cuts and drains. Traffic wear only along
   the walk lanes and around the pumps. At most a few small wet patches at drains and pump bases. Safety markings stay crisp.
5. **Mapping:** UV or box-projected texture sets at real-world texel density. Avoid object-coordinate noise whose features exceed about
   0.3 m: that is what made the camo. Check every material at 1:1 and from 8 m.
6. **Lighting:** restore the R34 rig as the base (battens, task, wash, gallery and practical lights), then tune for readable value:
   - no near-black where players walk;
   - no clipped highlights;
   - accents allowed, mood from contrast rather than global darkness.
   The combined map's bar (`combined/measure_lighting.py`) is median luma ≥ 0.15, near-black ≤ 15 % and clipped ≤ 5 %.
7. **Geometry:** no layout change. Budget **≤ 400,000 evaluated triangles, text curves included** (R34 is 641,598; A1 reached 386,490
   with `trim_geometry`).
8. Optional, if cheap and without moving anything listed in section 4: A1's reach-check items (`reach-check.json`). The overhead
   cooling-water valves (3.4 m) and the isolate hook (3.17 m) are unreachable.

## 4. Do not break the combined map (hard constraints)

The map (`sections/facility-assembly/combined/build_compact_map.py`) links `condenser-bay/<file>`, collection **`MODULE_condenser-bay`**, at
`COND` = turbine-local (1.6, 7.4, -6.0). The module origin is the D01 threshold centre at bay floor level. Module coordinates below are
turbine-local minus (1.6, 7.4).

1. **Keep** the collection name, module origin and frame, and the transforms of the architecture and equipment.
2. **Keep these object names** (`patch_condenser` finds them by name; verified present in A1, which did not rename anything from R34).
   If you must rename one, update `patch_condenser` in the same PR.

   | Name (or prefix) | What the map does with it |
   |---|---|
   | `D01 stub end wall`, `D01 local blanking*`, `D01 blanking*` | left out, so the stub opens onto the stair corridor |
   | `Ceiling slab` | squeezed under the turbine floor |
   | `gallery inspection light*` | lowered 0.12 m |
   | `CEP-B motor feed` (a curve), `CEP-B motor feed end cap` | the riser is moved to the north wall |
   | `WestWall`, `West dado` | split by the escape-door cut |
   | `North dado` | the dado edge the escape lane must clear |
3. **Keep these zones clear** (module x, y; heights above the bay floor):
   - D01 stub: x ±1.24, y -2.56..0. The stair corridor joins here.
   - Escape door: west wall x -2.08..-1.80, y 8.4..9.4, z 0..2.4. The map cuts a door there, with frames 0.1 m either side. Put nothing
     on that wall stretch below 2.6 m.
   - Escape lane, walked by `walk_test.py` with a 0.8 m capsule, z 0.1..2.0: D01 (0, 0.6) → (0, 5.2) → (0.6, 5.6) → (0.6, 8.75) →
     (-1.3, 8.75) → door (-1.95, 8.9). The pinch is between the ejector exhaust riser at about (-0.77, 8.1) and the CEP-B riser, which
     the map moves to y 9.36. Keep at least 0.9 m clear there and along the north wall strip y 8.6..9.5.
   - U04 receive opening, centred at (3.0, 4.05) (turbine U04 at turbine-local (4.6, 11.45)): keep it aligned and open.
4. **Roof and ceiling:**
   - The map squeezes `Ceiling slab` (module z 6.0..6.3) to z 5.695..5.985, because the turbine floor sits above it.
   - Anything above module z 5.68 is buried in the turbine floor slab. Keep ceiling lights, beams and hangers visible below z 5.6.
   - Ceiling lights must sit below z 5.55.
5. **Footprint:** stay inside the roof-slab bounds, module x -2.08..9.88, y -0.14..9.54, plus the D01 stub. Outside them are the stair
   corridor (south and west), the escape tunnel (west wall), the turbine and electrical floors (above), and earth.

## 5. Checks (all must pass before asking for review)

**Room level**
- Run the room's own saved audits (`sections/condenser-bay/blender/astra_validate_saved.py`, `validate.py`): bore, doorway, supports,
  fastener seating, routes, gallery, cameras.
- Do a triangle count with text curves included.
- Render the room's camera set (`sections/condenser-bay/production/cameras.json` and A1's four AAA cameras) at 1920×1080.
- Get an **independent review** against `production/RUBRIC.md` at the repository's bar. Record the scores. Do not self-accept.

**Map level**, after switching the one `ROOMS` line in `build_compact_map.py` from `condenser-bay/module_aaa_A1.blend` to
`condenser-bay/module_aaa_A2.blend`:
- Fetch the other sources first; the list is in `combined/AGENT_READ_FIRST.md` ("Files this folder needs").
- From `sections/facility-assembly/combined/`:

```bash
B=blender   # 5.2.2
$B --background --factory-startup --python build_compact_map.py
$B --background combined_map.blend --python plan_cut.py -- /tmp/cut.npz 0.15 0.4 1.1 1.8 2.8 4.5 -0.6 -3.5 -5.0 -5.6
python3 check_overlaps.py /tmp/cut.npz > validation/overlaps.txt
$B --background combined_map.blend --python walk_test.py -- validation/walk_report.json
$B --background combined_map.blend --python walk_test.py -- validation/walk_report.json --colliders
$B --background combined_map.blend --python walk_test.py -- validation/walk_report.json --meltdown
python3 evac_report.py
$B --background combined_map.blend --python door_audit.py
$B --background combined_map.blend --python floor_audit.py
$B --background combined_map.blend --python perf_report.py -- validation/perf_report.json
$B --background combined_map.blend --python export_unity.py -- export
$B --background combined_map.blend --python measure_lighting.py -- /tmp/light validation/lighting.json
```

Run them one at a time. Two Blender processes with this map run out of memory on a 15 GB machine.

**Pass criteria** (current values on the A1 map, 2026-10-14):

| Check | Must show |
|---|---|
| Build log | `CONDENSER D01 stub opened` > 0, `CONDENSER pump B power riser moved to the north wall: 8 curve points`, `CONDENSER west escape door cut:` > 0 objects, `CONDENSER ceiling slab lowered under the turbine floor`, `GROUND hole over the condenser bay: 1 ground pieces cut`. A zero count means a renamed object. |
| Walk, normal | 17/17 (since 2026-10-15; before, 17/18 with the freight cart route failing) |
| `cart_check.py` | PASS (the ore cart's cycle; unaffected by the bay, run it anyway) |
| Walk, colliders | 10/10 |
| Walk, meltdown | 20/20, including `evac_condenser_to_escape_ladder` and `evac_condenser_to_turbine_D02` |
| Closed doors | 13/13 block |
| `door_audit.py` | 45 doors, 0 flagged |
| `evac_report.py` | condenser: 2 evacuation routes, no single-door cut-off |
| `floor_audit.py` | no new owner pair involving `ROOM_condenser-bay` |
| Lighting | `condenser_D01`, `condenser_inside`, `condenser_escape_tunnel`, `stair_bottom` all `ok` |
| `perf_report.py` | `ROOM_condenser-bay` ≤ 400k triangles |
| Export | re-import PASS |

Also render, from the combined map, the owner's view: eye (1.6, 3.9, -4.4) → target (6.0, 10.3, -4.8), lens 16
(`combined/render_views.py`, which takes a views JSON like the evidence sets). Put it next to the A1 render.

## 6. Process

- One task branch and one draft PR.
- Do not merge your own work (`design/GAME_SPEC.md` section 32.6).
- Update the `condenser-bay` row in `AGENTS.md`, citing the review file, and add a line to `combined/COMPACT_MAP.md` and
  `combined/ASSEMBLY_REPORT.md` that the map now uses A2.
- Report exactly what ran, what did not, and the review status. Unrun checks are not passes.
