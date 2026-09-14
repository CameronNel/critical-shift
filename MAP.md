# Build on this map

This is the current assembled Critical Shift map, approximately **75% complete by the owner's estimate**. Continue this map; do not rebuild the rooms or assemble a second map from older branches.

## Get the actual assets

Clone this repository's **main** branch with Git LFS installed, then run:

```sh
git lfs install
git lfs pull
git lfs fsck
```

Blender and image files are stored in Git LFS. A text pointer is not a Blender scene. GitHub's source ZIP is not a reliable substitute for a hydrated checkout. Keep the whole repository, particularly `sections/facility-assembly/`, together.

## Open the current map

- **Editable entire map:** [facility_spawn_concept02_R17.blend](sections/facility-assembly/blender/facility_spawn_concept02_R17.blend).
- **Batched visual/walkthrough preview:** [facility_spawn_material_preview_R17.blend](sections/facility-assembly/blender/facility_spawn_material_preview_R17.blend).
- **Machine-readable entrypoints:** [MAP.json](MAP.json).

Despite `spawn` in the revision filename, **both scenes contain the entire assembled map**, including all twelve room modules, connector floors/halls, courtyard, vertical access, perimeter/terrain, exterior work and roof services. R17 adds the latest spawn/courtyard exterior and non-RT lighting work to the whole-map A14 baseline. The preview is a derived inspection cache; make geometry changes in the editable scene and its linked modules, then regenerate the preview.

Use Blender **5.2 LTS**. Open the editable file directly, or run `blender --python open_map.py`. For the rendered walkthrough use `blender --python open_map.py -- --preview`. Windows users can run `./OPEN_MAP.ps1` or `./OPEN_MAP.ps1 -Preview`; set `BLENDER_EXECUTABLE` if Blender is not on PATH or in its standard installation location. Preview controls are bundled: Shift+F walking, WASD movement, E/Q elevation. Gravity is disabled; this is Blender navigation, not game collision. Blender MCP is optional, enabled only by `MAP_ENABLE_MCP=1` when installed.

## Continue safely

Read the canonical `design/` spec and art direction, then [the source registry](sections/facility-assembly/production/SOURCES.json), [current layout](sections/facility-assembly/production/LAYOUT_A12.json), [A12 construction handoff](sections/facility-assembly/production/CONSTRUCTION_A12_HANDOFF.md), [A13 roof services](sections/facility-assembly/production/ROOF_SERVICES_A13_HANDOFF.md), and [latest exterior checkpoint](sections/facility-assembly/production/spawn-exterior-review/IMPLEMENTATION_CHECKPOINT.md).

The portable room copies are `sections/facility-assembly/sources/<section>/module.blend`; byte-exact input snapshots and contract records sit beside them. Exteriors are in `exteriors/<section>/`. Do not fetch older room branches to replace these selected modules. Original Windows paths in source provenance describe where assets came from, not required runtime locations. Work on a task branch, preserve interfaces and section placement, and update MAP.json if the canonical scene changes.

The owner authorized integrating this map into main on 2026-09-14 so remote agents can continue it. This is **integration, not final visual acceptance**: R17 independent Luna lighting90, materials88, professional finish82; every category must eventually exceed93. Prior failed reviews, concepts and replay scripts remain available. Current outstanding art includes rock treatment, material variation, roof/paving separation and planting rhythm. Unity import, collision/navmesh, interactions and measured performance remain separate work; do not claim this is a finished Unity game or a measured 60FPS scene.

Older handoffs describe historical A04/A05 stages and may say connectors are unbuilt or "no main merge". Those statements are historical; this guide and MAP.json identify the current integrated map. Do not resume from `facility_master.blend` (A04) merely because an older README mentions it.
