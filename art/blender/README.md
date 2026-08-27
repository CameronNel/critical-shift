# Blender art source

## Shift Muster Bay production source

`production/spawn_2026-08-27.blend` is the from-scratch source scene for the
spawn/start area's Shift Muster Bay. It follows `docs/ART_DIRECTION.md`: simple
faceted geometry, texture-light shared materials, bold interaction silhouettes,
four hero PPE displays, and a clear safe-to-production airlock transition. No
geometry, material, texture, or scene content from an older spawn asset was
reused, and the file has no external or linked-library dependencies.

The file uses metre scale, contains four 2.2 m-spaced player-spawn hooks, keeps
an obstacle-free 3.6 m carry/body-drag lane, and opens on `CAM_Spawn_POV`.
Validation and handoff views are stored beside this README as
`spawn_2026-08-27_*.png`.

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

Paths are relative (`//textures/...`), so the scene opens correctly from any
clone.

## Fidelity note

This scene deliberately exceeds the fidelity ceiling in
[`docs/ART_DIRECTION.md`](../../docs/ART_DIRECTION.md) — 2K PBR sets and ~137k
triangles are well past "low-to-mid fidelity" and "limited shared material
families". It is a look-dev target for discussion, **not** an approved change to
the art direction. Treat any decision to ship this fidelity as a deliberate
revision of that document.
