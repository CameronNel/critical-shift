# Blender art source

`gullet-mine.blend` is a look-development scene for the Gullet Mine, not game
data. Nothing here is loaded by the game or by any prototype — it exists so the
mine's surfaces, lighting and proportions can be judged at eye level before the
look is committed to engine assets.

## Provenance

Geometry originates from `prototype/gullet-mine/` on the
`prototype/gullet-mine-work` branch. The Three.js scene was exported to glTF and
imported here; it is a snapshot, not a live link. Re-exporting overwrites any
Blender-side edits.

Since import the scene has been reworked in ways the prototype does not know
about:

- Rock, ground and timber use image-based PBR materials rather than the
  prototype's canvas textures.
- The floor was rebuilt from a flat plane into displaced terrain that banks up
  into the rock, and its boundary was extruded onto the cave wall.
- The cave ceiling was pulled down onto the timber sets.
- `SafetyFloor` is an invisible collision plane for Blender's walk navigation.
  It is not part of the mine and must never be exported.

## Textures

`textures/` holds 2K PBR maps from [ambientCG](https://ambientcg.com), all
released under **CC0 1.0 (public domain)**: free for commercial use, no
attribution required, no monetary restriction.

| Set | Used for |
| --- | --- |
| Rock030 | Cave walls, cap rock, ore matrix, rubble |
| Rock023 | Stone blended up the floor/wall bank |
| Ground054 | Drift floor |
| Gravel023 | Spoil banked against the walls |
| Wood067 | Sawn timber |
| Bark012 | Round props |

Only the maps the scene actually samples are kept (Color, NormalGL, Roughness,
AmbientOcclusion). Displacement and DX-normal variants were discarded.

Standing water samples one further CC0 map, a seamless ocean normal from
[ProcTexture](https://proctexture.com/textures/water/normal-maps/ocean-normal-map),
kept outside this directory in `art/textures/water/` alongside its `SOURCE.md`.

Paths are relative (`//textures/...`, `//../textures/...`), so the scene opens
correctly from any clone.

## Standing water

The drift crosses water twice — a timber deck around y = 7..16, and a ballast
causeway on post bents around y = 24..42. Both crossings are wadeable pools:
a solid bottom, water over it, nothing else. Neither is deeper than a long
step, so the player can always climb out.

[`rebuild_pit_water.py`](rebuild_pit_water.py) generates all of it — carve,
floor, water — rather than any of it being modelled by hand. It drops a ray at
every point on a grid, passes through timber, rail and props, and stops at the
first rock, ground or pool floor, so the shoreline lands where the bottom
actually dips under the waterline. Edit the script and re-run it in the live
scene; do not nudge the meshes, they will be replaced.

Two things it does that are not reversible by re-running:

- The deck crossing was imported as an 8.6 m shaft furnished most of the way
  down with an iron platform, hanging lanterns, ropes and scaffolding. All of
  it below the new bottom is **cut away** from the source meshes.
- `SafetyFloor` has the wet footprints **cut out of it**, otherwise it catches
  the player above the waterline and the pool bottoms may as well not exist.
  The hole is the wet footprint itself, never a rectangle around it: a cell is
  only wet because a solid surface was found below the waterline there, so
  everything removed has something to land on.

The imported asset's own coarse `water_001` pool is hidden, not deleted, since
the fitted surfaces supersede it.

## Fidelity note

This scene deliberately exceeds the fidelity ceiling in
[`docs/ART_DIRECTION.md`](../../docs/ART_DIRECTION.md) — 2K PBR sets and ~137k
triangles are well past "low-to-mid fidelity" and "limited shared material
families". It is a look-dev target for discussion, **not** an approved change to
the art direction. Treat any decision to ship this fidelity as a deliberate
revision of that document.
