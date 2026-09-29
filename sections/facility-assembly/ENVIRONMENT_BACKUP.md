# Environment backup — 2026-09-29

This branch preserves the owner's approved saved environment from the separate
main-integration-20260914 worktree. It is a draft backup, not an art acceptance,
runtime integration, or a reproducible rebuild claim.

## Original backup provenance

- Scene: `blender/facility_environment.blend`.
- Original backup SHA-256 (before the PR #48 integration below): `964d81807cd3cc6c43f86a1de5c5a33cba8c13aceb32c44fccc93372cc28d763`.
- Blender: 5.2.0 LTS, build `fbe6228777e7`.
- R18 is separately retained by cherry-picking b3cfbc31 and 008f20a2.
- All 24 linked libraries match the verified saved-scene baseline; retain the
  R17 material preview, exterior libraries, and twelve source modules.
- Room module files are unchanged from the fetched main baseline.
- SOURCES.json is intentionally unchanged from main, not copied from the dirty
  authoring worktree. No unrelated staged deletions are included.

## Scope

The scene includes the mine/refinery transition courtyard, refinery exterior
systems and finishes, grey/oxide palette, geometric panel/fitting gaps,
dimensional weathered paving, ground finish, and spawn/medical courtyard pass.
The new spawn/medical work is in `ART | Spawn and medical courtyard`.

Read `../../design/NON_FLAT_ENVIRONMENTS.md` for geometry-first finishing guidance.
Construction, correction, render and verification scripts are preserved as
historical migrations, not an idempotent rebuild pipeline. Many require prior
hash-guarded checkpoints and transient runtime/out inspection reports; these
local records and recovery .blend files are not included in this backup. Some
launchers contain original-machine absolute paths. Do not blindly rerun them.

The authoritative backup is the saved .blend and its retained linked libraries.
No new render or Unity validation was performed when creating the original
backup. The subsequent integration checks are described below. Git LFS must be
hydrated to open it.

MAP.json selects this scene for authoring and inspection. Older R18 instructions
elsewhere remain historical; do not regenerate R17 over the current dependency
or replace this scene with R18. Review launcher behavior before changing workflow.

## PR #48 spawn integration (draft PR #50)

Merged `origin/main` at `47b7eec8` into the clean backup branch before making
these changes. That main commit is the PR #48 merge; the latest spawn module
path commit is `ed80c9aa` (restore the 17 cm slab). No source module was edited.

- Current environment SHA-256: `7d263a04e42b357f30c38df1ff012a4b7e80fc9bab3f4869e4782318e9fa88c8`.
- Spawn module SHA-256: `9635f41aec585768285317399af9d6a3943411a66e20e2e3d96b05ad86dcfa40`, byte-identical to main.
- R17 SHA-256: `4d5d160d5c9d25b0a447fda933974790260cdde7aced2db1da1c908afdcdc937`, unchanged; never regenerated.
- Spawn is linked from `//../sources/spawn-room/module.blend`, not appended or
  baked into a replacement cache. The instance retains all 73 `COZY_` art objects
  and 1,958 linked objects in total.
- The local membership wrapper omits the 22 established airlock exclusions from
  `connections/access/DOOR_BINDINGS.json` and the four `SERVICE_end*` closures
  previously omitted by `fix_spawn_transition.py`. This preserves existing map
  doorways rather than restoring source-room closures across connected routes.
- Seventeen obsolete cached interior-light copies were retired to avoid double
  lighting. Existing exterior entry lights are preserved. Three inspection
  cameras were added. The linked slab spans Z=-0.170 to -0.001 m.

Measured corrections are confined to the existing `SY |` yard details:

- Extend two canopy wall-anchor backs across an 80 mm gap, with 1 mm seating.
- Raise four canopy fixture housings and their four diffusers by 15 mm.
- Seat four medical support anchors by 10 mm.
- Extend the undersides of courtyard slabs `.058` and `.059` to their support
  beds; walking/top elevations are unchanged.
- Move the tall reactor-adjacent riser's straight run and its flanges/joints
  200 mm toward its mounting facade, keeping both end connections fixed and
  shortening five brackets. This removes its intersection with the vestibule
  roof; it does not modify a reactor door or stair.

The construction files are guarded, one-time migrations, not rebuild commands.
For read-only checks of the saved scene, run from the repository root:

```powershell
& ./sections/facility-assembly/blender/run_spawn_integration.ps1 -Script audit_sy_contacts.py
& ./sections/facility-assembly/blender/run_spawn_integration.ps1 -Script probe_reactor_interfaces.py
& ./sections/facility-assembly/blender/run_spawn_integration.ps1 -Script check_spawn_exit_clearance.py
& ./sections/facility-assembly/blender/run_spawn_integration.ps1 -Script render_spawn_integration.py
```

The launcher uses one hidden, BelowNormal Blender 5.2 CPU worker. Inspection
renders are 960x540, eight Cycles samples, seed 73, CPU denoising. Reports and
images are written under `runtime/out/spawn-integration/`, not to R17.
`verify_spawn_integration.py` additionally compares against the original local
backup and its inspection manifest; those transient prerequisites are not a
portable test fixture and must not be invented on another machine.

The support screen examines all 1,623 yard meshes, including their material
assignments and world bounds. It uses sampled surface distances, triangle
overlap and external support rays with an 8 mm screen tolerance; this is not
exhaustive collision, burial-volume, navmesh or runtime certification. Intentional
shallow paving bedding and embedded cliff-foot boulders are retained. Final
saved-file verification and render evidence are recorded in the integration
summary accompanying this draft PR.

Cold-open verification of the current hash above found 37 changed local objects,
all `SY |` details listed above; 16,635 original local objects were unchanged.
Only the 17 obsolete spawn interior-light copies were removed, and only the
direct-link instance plus three inspection cameras were added locally. There
were no missing used datablocks or file-backed images. All linked library file
hashes were unchanged by the integration. The final support audit found 77
connected groups and zero unanchored groups; the reactor screen found no
triangle intersections against the 15 selected vestibule/stair/door surfaces.
All 12 sampled service-exit rays were clear. Five final-hash CPU renders were
visually inspected: front yard, spawn threshold, spawn east attachments,
medical attachments and reverse yard. No additional visible seating or palette
clashes were identified in those views; this is a bounded visual review, not
independent art acceptance or proof that every hidden surface is collision-free.
A fresh-process repeat of the front-yard camera used the same saved scene hash,
camera matrix, lens and render settings. Pixel comparison found only 20 of
518,400 pixels differing, by at most 1/255 per channel (mean absolute channel
delta 0.00001286 in byte units). This is visually stable, not byte-identical.

### Reactor east-wall dependency

In **source-local reactor coordinates**, no external connector is bound to the
east-wall D01 entry or D02 stair/control-room entry. The stair core is not used
as a mount for these yard additions. However, the `SY |` riser and large vent
are on the adjacent facade, so a future east-annex redesign still needs a local
clearance review. The riser/vestibule-roof clash discovered here was corrected;
the source reactor module and its existing preview remain untouched.

The reactor is rotated 180 degrees in the map. Its **map-east** route is the
R04 turbine connector at the source-local **west** `MAIN_ACCESS` port; that
door is an active connector dependency. Do not confuse it with the source-local
east stair annex. Existing reactor stair geometry is also present in its old
preview, so changing the reactor source alone will not refresh that appearance.

MAP.json, LAYOUT_A12.json and SOURCES.json were not changed by this integration.
No Unity import, collision/navmesh or gameplay validation was performed. The
branch remains a draft for independent review; it has not been merged to main.
