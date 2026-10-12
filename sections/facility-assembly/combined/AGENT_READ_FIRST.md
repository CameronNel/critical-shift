# Combined map: agent instructions (read before any environment or map work)

Last updated 2026-10-06. Status of everything in this folder: **unreviewed, not accepted.** It was merged to `main` (PR 95) on the owner's explicit
instruction, which waives the repository rule that an agent does not merge its own work. No independent review has happened. Do not describe any of it as accepted.

## What this is

`combined_map.blend` is the new assembled scene that replaces the retiring `sections/facility-assembly/blender/facility_environment.blend`
(owner plan 2026-10-03, see `AGENTS.md`). It is built room by room from the layout drafted with the owner on 2026-10-04:
`design/facility-layout/README.md` (plan v7), `design/facility-layout/MEASURED_ROOM_SIZES.md` and `design/facility-layout/front-end-area/DESIGN.md`.
Where plan v7 and the as-built front end disagree, the as-built front end and DESIGN.md win, and the difference is written down in `COMBINED_MAP.md`.

- **Do not extend, relink or promote rooms into the old map.** Continue here instead.
- **Frame:** plan metres, +x east, +y north, +z up, origin at the reactor centre. Each room is a linked collection instance with one translation and one rotation about z.
- **Source of truth is `build_combined_map.py`.** `combined_map.blend` is generated output. Never hand-edit the `.blend`; change the script and rebuild.
- **Record of every decision is `COMBINED_MAP.md`:** per room, the source file, what fixed the placement (with the measurement), what was patched, evidence renders, what was not checked.
- Evidence renders are in `renders/` (per room), `renders/review/` (whole-scene review) and `renders/fixes/` (fix log and room 5).

## Current state (through room 11)

Build keys, in `ROOMS` order. `--through <key>` builds that room and every room before it.

| # | Key | Room | Plan placement |
|---|---|---|---|
| 0 | `front-end-area` | cafeteria, hall, yard | translation (8, -80), rotation 0 |
| 1 | `spawn-room` | spawn room | (8, -92.38), 0 |
| 2 | `mine` | mine R39 (wooden) | (-14.4, -41.0), 0 |
| 3 | `refinery` | refinery overhaul R1 | (-26.28, -52.2), 90 |
| 4 | `medical-reanimation` | medical overhaul R2 | (26, -70), -90 |
| 5 | `fuel-corridor` | fuel corridor F23ci | (-22.2, -43.6), 0 |
| 6 | `reactor-room` | reactor, refined hall (candidate A), joined by a south concourse | (0, 0), 0 |
| 7 | `turbine-room` | turbine (AAA finish from branch `claude/turbine-aaa`) | (0, 17.0), 0 |
| 8 | `electrical-room` | electrical (overhaul R11) | (19.75, 26.25), 0 |
| 9 | `waste-storage` | waste storage | (28.32, -24), -90 |
| 10 | `cooling-plant` | cooling plant | (-44.1, -19), 90 |
| 11 | `compliance-dock` | compliance dock (overhaul R1) | (60, -79), -90 |

The committed `combined_map.blend` is built `--through compliance-dock`. Every room is "added, awaiting owner OK" except the front end, which is "built, unreviewed".
Not placed: condenser bay (not in the plan), gantry (no attachment spec). Known defects and open items are listed in `COMBINED_MAP.md` (fix log and "Defects and open items").

## Files this folder needs that are not committed here (fetch before building)

`build_combined_map.py --through compliance-dock` links source files that live elsewhere in the repository; fetch each single file (never a wide sparse checkout):
- Turbine, the AAA finish from the unmerged branch `claude/turbine-aaa`: `git show origin/claude/turbine-aaa:sections/facility-assembly/sources/turbine-room/module_overhaul_R1.blend | git lfs smudge > sections/facility-assembly/sources/turbine-room/module_overhaul_R1.blend` (the build does not fall back to another turbine file; its door and wall positions are specific to this one).
- Dock: `sources/compliance-dock/module_overhaul_R1.blend` is a plain Git blob on `main` (`git show origin/main:<path> > <path>`). Electrical `overhaul/checkpoints/full-R11.blend`, waste `module.blend`, cooling `module.blend`, medical `module_overhaul_R2.blend`, fuel corridor `fuel_full_F23ci.blend`, spawn `module.blend` and the front end's `textures/` folder are LFS files on `main`; the spawn module is also linked for the halls' materials, airlock doors and props.
- The hall screens (`textures/hall_screen_*.png`) are committed here; regenerate with `python3 make_hall_screens.py textures`.

## Hall network tools (committed here)

- `reactor_links.py`: hall builder, wall-cutting, dressing (used by the build). `LINKS` and the room cut tables (`TURBINE_CUTS`, `MEDICAL_CUTS`, `reactor_links.HALL_CUTS`) in `build_combined_map.py` are the only places a hall or door is defined.
- `validate_halls.py`: repeatable geometry audit (ray walk, sphere leak, junction probes, hall-to-hall and hall-to-room clearance, triangle counts); writes `validation/halls_report.json`. About ten minutes. Geometry evidence only.
- `dump_network.py` + `draw_network_plan.py`: draw `renders/14_network_plan.png` from the same `LINKS`.

## Rules

1. **One room at a time, and only on the owner's say-so.** Add a room when the owner asks for it. Show renders; the owner approves before the next room.
2. **Never edit a source room file.** Rooms are linked. Anything that must differ in the combined scene (opened doorways, removed stand-in props, trimmed meshes) is a local copy made by the
   build script (see `OMIT`, `PATCHES` and the helper functions in `build_combined_map.py`). Say in `COMBINED_MAP.md` what was changed and why.
3. **Do not reopen "done and dusted" rooms** (see the status table in `AGENTS.md`: refinery, electrical, turbine, medical-reanimation, compliance-dock). Linking them here is allowed; editing their files or starting an art pass is not.
4. **Nothing is guessed.** A placement must come from the room's own port or interface (`sources/<room>/contracts/interface.json`, door lists, `DOOR_BINDINGS.json`) and a measurement of the actual file, plus the layout documents above.
   Write the numbers and where they came from into `COMBINED_MAP.md`. If you cannot find a number, ask the owner instead of picking one.
5. **Report only what was run.** State what was checked by render, by ray test or by number, and what was not checked (collision, walk test, lighting balance, performance, Unity). No claim of acceptance.
6. **Use the review pass.** After adding a room, render the join views and an overview, look at every image, and fix or record what looks wrong. A closed door that opens onto black is a defect to record or fix.
7. **Update the record in the same PR:** the room table in `COMBINED_MAP.md`, the table above, the `AGENTS.md` combined-map section, and `combined_map.blend` rebuilt from the final script.
8. Repository policy still applies: one task branch, one primary author, no direct edits to `main`. This PR was merged by an agent only because the owner told it to; do not assume that permission carries over.

## How to add the next room (procedure)

1. Read the room's `AGENT_READ_FIRST.md`, its `contracts/interface.json` and the layout documents. Pick the source file the status table in `AGENTS.md` names (reviewed version first; an unreviewed finish is not used unless the owner says so).
2. **Fetch only the files you need. Do not use a broad sparse checkout.** The repository is several GB of Blender files with a fixed disk allowance; a wide sparse-checkout once filled the disk in this environment.
   Fetch a single file with `git show origin/main:<path> > <path>` (plain blob) or `git show origin/main:<path> | git lfs smudge > <path>` (LFS pointer), and run `export GIT_LFS_SKIP_SMUDGE=1` before git commands that touch the working tree.
   Check `df -h` before and after.
3. Inspect the file headlessly (Blender 5.2 LTS; `/opt/blender52/blender-5.2.2-linux-x64/blender` in the cloud container): collections, bounding box, port empties, lights, hidden objects.
4. Add one tuple to `ROOMS` in `build_combined_map.py`: `(key, path relative to ../sources, collection name, (x, y, z), rotation_degrees, note)`. The note must say what fixed the placement.
   A path outside `sources/` works with `../`, as the fuel corridor entry shows. Exterior skins: add to `EXTERIOR_SKINS` if the room has a reviewed or accepted exterior file under `sections/facility-assembly/exteriors/`.
5. Build: `blender --background --python build_combined_map.py -- --through <key> --output <path>.blend`. Build to a scratch path first, then to `combined_map.blend` when done.
6. Render with `render_views.py` (usage in its header). Hide `ROOM_mine` (4.08M triangles) for views that do not look into the mine. Look at every image.
7. Write the room section in `COMBINED_MAP.md`, copy the evidence renders into `renders/`, rebuild `combined_map.blend`, update the tables, commit, open a draft PR.

## Traps already hit (do not repeat)

- Linked objects report an identity `matrix_world` at build time. Use `wm(obj)` in the script, not `matrix_world`.
- Lowering a sign's emission did not fix a blank sign; the cause was missing UVs on the back face. Diagnose from the mesh before changing materials.
- The mine's mountain material renders near black on the yard's cliff mesh; the yard cliff material is adjusted locally instead.
- `PLACEHOLDER_*` objects stand in for rooms that are not placed yet and are not built once the room is in `INCLUDED`. Add a placeholder when a new room leaves a doorway opening onto nothing, and remove it when the room behind it is placed.
- Cameras inside geometry render as flat walls. A dark render is not evidence of anything until the lighting is understood.
