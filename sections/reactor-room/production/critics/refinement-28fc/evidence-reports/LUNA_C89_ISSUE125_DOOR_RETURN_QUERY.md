# C89 issue 125: D1 door-return staining

**Finding:** C89 does not show the requested localized door-return stain, and the saved D1 return surfaces have no localized stain assignment. Keep #125 open as a source correction; do not infer acceptance from the warm light patch around the lintel.

## Evidence identity

- Candidate blend: `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`
- Candidate SHA-256: `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`
- Full current view 10: `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/10/10_walls_west_access.png`
- Image SHA-256: `0a6c7887eb0f418361aa08990ad0e761c98bb37bd404ee98af2a7b2c84a5ba3d`
- Manifest SHA-256: `f5e0375a00bcb2b9b866af53fbf03b992907de11154b46461e02747503c4ea0e`
- Read-only exact-scene query: [script](evidence/C89_DOOR_RETURN_MATERIAL_QUERY.py), SHA-256 `e06a66e50308c86bcf6bc4c2e81d18561cec90d4d2b490ff751bae4267c6e9a4`
- Query result: [JSON](evidence/C89_DOOR_RETURN_MATERIAL_QUERY.json), SHA-256 `df172d6604ce46eca3a16f7f59b8e484aabc7eff8151ba167c3a9c2e278881a6`
- `rh_refine.py` SHA-256: `d70ffe054dfe128c708e8877925ec04553c1c07cca63fe0bae0bac473de5470b`
- `rh_walls.py` SHA-256: `65ea9985d0056ee55509bb7d57818c5431cb8b50f8e67fdcd4482cfd1ede13e9`

## Exact-scene assignment check

The query hashes the opened blend and samples mesh faces in bounded D1 side-return, head-return, and adjacent-alcove regions. `MAIN ACCESS.link wall` and `.001` are the side return walls. They use the shared `RH refine wall concrete` material. The opening head and nearby formed concrete use the shared `RH refine cast concrete` material. The reveal liners use `RH refine wall steel panel`.

`rh_refine.py` builds the wall concrete family with low global mottle (`variation=.15`) and explicitly sets `streak=0`, `grime=0`; the cast-concrete family uses the same quiet surface helper. The wall steel panel family is also a shared finish. The D1 return faces have no separate stain mesh, mask, or material assignment. The nearby warm appearance in full view 10 comes from the doorway task-light region and does not supply the requested localized stain.

## Disposition

This confirms an implementation gap for #125 in C89. Full view 10 shows the main access opening and adjacent return area at 1280×720, but no convincing localized dirt or stain; the saved object/material query explains the absence. The row remains pending correction and current-source re-review. The query is finite: it covers the D1 side returns, head return, and adjacent alcove bounds, not every wall opening in the hall.
