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

The scene is lit live for a night mood: 15 amber hooded pendant spots (pools with dark gaps), warm floor uplights and wall washers, focused spots on the rotor, consoles, bay and desk, a work lamp on a stand, restrained red warning lights, and a cold moon plus rim lights through the clerestory windows. AgX view transform. **Lighting is not baked.**
Baking is the final production step, run only after geometry, materials and live lighting are accepted. `bake.py` is the
final-step tool and has not been run for this rebuild; its lightmap layout (`LightmapUV`) and denoise path are untested at
full quality, and it must be re-run after any later change.

## Floor

The floor is ONE concrete slab (`floormesh.py`, 14 x 24 x 0.3 m, 876 triangles) with real holes cut through it for the two drainage channels, two sumps,
five round drains and the exhaust opening. One planar UV covers the whole top; `floortex.py` paints albedo, roughness (wet / damp / polished) and a
normal map at 160 texels per metre (2240 x 3840) with joints, cracks, spalls, stains, repair patches, tyre scuffs, worn lane paint and wet flow to the drains.
Gratings and drain covers (`floor.py`) are the only separate meshes. These maps are texturing, not baked lighting.

## Walls

Each wall is ONE 0.05 m skin (`wallmesh.py`) with the real openings (doors, windows, utility ports) cut through it and one per-wall texture set
(`walltex.py`, 96 px/m: corrugated cladding, plinth, wainscot, seams, rivets, grime, streaks, peeling, painted numerals and arrows, gold stripe; albedo/ORM/normal).
`arch.py` adds the structure (chamfered plinth, rails, cornice with drip lip, black bay frames, X-bracing, glazed windows with hinges and latches) and
`walldress.py` the dressing (pipe bundles with ID bands, valves and gauges, cable ladders and risers, louvred fans, EXIT signs, hazard plaques, DB boards,
e-stops, eyewash, PA horns and strobes, evacuation plan, bump rails, quilted acoustic panels). Wall textures total about 5 MB on disk; no light is baked.

## Review status (agent self-review, not a human review)

A single rubric reviewer (a Claude subagent, 100-point rubric: value separation 15, silhouette 15, trim/panels 15, signage 10, props 15, materials 15, lighting 10, artifacts 5; spawn room as the finish bar; dark ambience accepted by the owner) scored 12 named cameras round by round on hash-checked renders.
Mean progression: about 52 (first pass) -> 66.8 -> 72.3 -> 74.1 -> 76.3 -> 77.1 -> 78.0 -> 79.2 (round 26). **No view has reached 95; the best views score 83-84 (door D01, entry north), the weakest 75-77.**
The reviewer's ranked gap (about 16 points per view): surface materials (~4: smeared grey gradients on floors and casings, denoiser softness), prop specificity (~3.5: sparse blades, small hatches, clutter pockets), value separation (~3: dark hero masses read only by a thin rim),
silhouette/shape language (~3), trim and panel logic (~2), lighting (~2), artifacts (~1: cropped edge objects), signage (~0.5). Incremental polish now yields about +0.3 mean per round; closing the rest needs larger work (a real trim-sheet / higher-resolution material system and a hero prop kit), not more small fixes.
These scores are one model's opinion against a fixed rubric, with the owner's dark-ambience direction applied, and have not been confirmed by a human art review.
Late-round additions: control station off the west wall (sloped panels, monitors, operator chair), annunciator wall and sign, per-wall texture sets and wall dressing, casing access hatches, hung tag signs, pale trim colour, a stylised grazing-angle rim in every material
(a material feature that the runtime shader must reproduce), per-view warm light pools and cool wall rim spots. Triangle count about 395k including the drums (budget 400k).

## Props and decals (v4 pass, owner request: purposeful small assets, no text-as-shapes)

- **Decal sheets** (`decals.py`, system python + PIL, run by `run.py`): `turbine_decals.png` (lit: signs, labels, posters, dials, notices, evacuation plan, console bezels, tool shadow board) and `turbine_decals_emit.png` (emissive: the control-room mimic, six console monitors, the desk monitor, the exit sign), plus `decals.json` (UV rect and size in metres per decal). Every sign, label, dial and screen is texture art on a flat quad (`Builder.decal`, or `decal_wrap` for curved bodies); no text is geometry any more. Objects `TURBINE_DECAL` (lit) and `TURBINE_DECAL_E` (emissive) are alpha-blended with shadows off. **Runtime needs:** alpha-blend (or alpha-test) decal materials, a small depth bias, and an emissive path for the second sheet.
- **Mimic screen:** a rendered UI (title bar, heads-up hall plan with zones, plant-status panel, alarms, navigation bar). The zone-3 alarm highlight is the separate object `TURBINE_MIMIC_FAULT` so the runtime can flicker or hide it.
- **Drums:** two 200 L drums are lathe-turned objects (`drums.py`): rolled chimes, pressed rolling hoops, recessed head with reinforcing bead, 2 in and 3/4 in bungs. They carry their own painted and worn albedo/ORM maps (`drumtex.py`, label stencilled in the paint) and stand on a modelled spill pallet with a hand pump.
- **Hero props** (`assets.py`): extinguishers (lathe body, valve, lever, pin, hose, horn, bracket), gas cylinders in a chained rack, hose reel with a spiral hose, tool trolley with drawers, casters and tools, working desk set (pedestal, monitor, keyboard decal, lamp, mug, papers), pallet + slatted crate + steel case, notice board, posters, first-aid box, industrial sockets, wall clock, cage work lamp, shadow-board hand tools and shelf stock. Chair rebuilt with a curved shell backrest.

## Not done

Independent review, Cycles art-acceptance against the spawn room, measured runtime performance, collision, Unity import, and
the final lighting bake. Previews are Cycles 32-sample denoised renders (1067 x 600) from the named `CAM_*` cameras, all from the committed build: `production/turbine-rebuild/renders/`. Agent self-review only; no independent review.

Known lesson: coplanar duplicate faces (e.g. a casing cap and a flange cap in one plane) shadow each other and render black. Keep caps inset or offset.
