# Turbine room detail pass (derivative, not promoted)

- Source `sources/turbine-room/module.blend` is untouched. Output: `sources/turbine-room/module_detailed.blend`.
- Rebuild: `blender --background --disable-autoexec --python-exit-code 1 --python sections/facility-assembly/blender/turbine_detail_pass.py -- OUT.blend --render DIR` (Blender 5.2.2 LTS).
- Adds ~4.2k faces in 8 joined meshes (collection `10 Detail pass`), reusing the room's 28 existing materials, no new images or lights. Room footprint unchanged; placement avoids existing geometry by AABB test.
- 20 detail families: floor scuff/oil decals, broken floor tiles, hazard-stripe edging, floor cables with ramp protectors, hanging ceiling cables, wall sockets/plugs, junction boxes + conduit, fire extinguishers, warning signs, tool pegboards, hose reels, scaffolding bay, desks/chairs/lamps/papers, ceiling strip fixtures, roof stains/loose panels/exposed purlins, pallets and crates, oil drums (upright/tipped/leaking), gas cylinders, loose floor tools, leaning ladder, broken dangling pipe with puddle.
- Renders are Workbench previews of cameras C01/C03/C05/W02, not Cycles/art acceptance.
- NOT done yet: UV atlas, lightmap/texture bake, material-family reduction, measured triangle/texture budget, Unity validation. No independent review.
