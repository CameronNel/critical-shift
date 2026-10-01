# Turbine room rebuild (derivative, not promoted)

A from-scratch rebuild of the turbine hall. **Only the room size and the interface positions are kept** from the
old room: clear shell 14 x 24 x 7.2 m (x -4..10, y 0..24), doors D01 (0,0) and D02 (0,24) at 2.4 x 2.7 m,
steam U01 (8.4,0,4.9), condensate U02 (9.5,0,0.45), HV bus U03 and the 2.5 x 1.5 m exhaust opening U04 at (4.6,11.45).
No object, material or texture from the previous room is loaded. `sources/turbine-room/module.blend` is untouched.

## Build

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python sections/facility-assembly/blender/turbine_rebuild/run.py -- OUT_DIR
blender -b OUT_DIR/turbine_room_v2_geo.blend --python sections/facility-assembly/blender/turbine_rebuild/preview.py -- RENDER_DIR lit
```

Blender 5.2.2 LTS. `lib.py` (primitives, painted atlas), `arch.py` (shell, floor, walls, columns, trusses, roof, crane, doors),
`machinery.py` (turbine train, generator, steam/condensate/lube services, controls, switchgear, maintenance bay),
`props.py` (wear, tools, plugs, cables, scaffolding, desks, signage, broken/lived-in props), `run.py` (assembly, lights, cameras).

## Look and budget

- Sharp, flat-shaded facets, painted colour blocking (ivory / charcoal / oxide orange / safety yellow). One 2048 x 2048 albedo atlas
  generated procedurally (edge wear, dirt gradient, speckle); every face is UV-fitted into one swatch.
- 4 shipping meshes (ARCH, MACH, PROPS, animated shaft), 8 materials (two per group: opaque and emissive), 1 image.
- About 40k triangles after culling faces that are buried or outside the shell. Atlas is 16 MB uncompressed, about 4 MB block-compressed.
- Culled faces are kept in a non-shipping `OCCLUDER_ONLY` object so the lit scene stays sealed (no light leaks through wall seams).
  Remove it from any runtime export.

## Lighting: live, not baked

The scene is lit live (15 ceiling area lights, one broken lamp, an east sun through clerestories, sky world). **Lighting is not baked.**
Baking is the final production step, run only after geometry, materials and live lighting are accepted. `bake.py` is the
final-step tool and has not been run for this rebuild; its lightmap layout (`LightmapUV`) and denoise path are untested at
full quality, and it must be re-run after any later change.

## Not done

Independent review, Cycles art-acceptance against the spawn room, measured runtime performance, collision, Unity import, and
the final lighting bake. Previews are Cycles 32-sample denoised renders from the named `CAM_*` cameras.
