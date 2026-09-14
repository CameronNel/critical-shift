# A11 map construction handoff — 2026-09-13

Unity work is paused at the user's request. A11 continues the assembled Blender map, preserving room placements, the rescue courtyard shortcut, existing indoor/outdoor routes and source modules.

## Built

- Detailed condenser access passage: supported pipes, bolted olive service panels, hose reel, clipped conduit, service enclosures, sealed warm lights and wayfinding.
- One continuous lower access floor replaces four overlapping slabs. The stair retains 36 equal risers, with 34 separate tread meshes and the two landing surfaces.
- Additive finishing across the horizontal network: continuous overhead services, post anchors, wall skins, edge drains, route markers, rack shoes, bench supports and trees in existing planters. The finished rescue courtyard is preserved.
- Reactor exterior panel seam backing and a mounted identification board; original room geometry stays intact.
- Three batched display meshes keep the new authored objects out of the fast viewport's per-object work. Original geometry remains available for editing and rendering.

## Files and controls

Open `blender/facility_walkthrough_A11_map_finish.blend`; the launcher now chooses A11. `facility_master_A11_map_finish.blend` is the authoring counterpart. Both retain source collections and dependencies.

Shift+F starts walking. Gravity is off. N > Walkthrough switches between fast display and original geometry, and exposes the existing door/lift controls. This is Blender free navigation, not game collision.

## Verification

`connections/map-finish/ACCESS_REGRESSION.json`: cold-load PASS after the floor union, with 34 doors, 60 interlock samples, 420 lift samples, passenger follow and unobstructed doorway/headroom rays.

`CLEARANCE.json`: 409 new objects within the player-height band checked against full-width ground routes; no overlap candidates. This is a bounds check of the additions, not a runtime navmesh test.

`renders-A11/`: fifteen actual Cycles review views, with native new detail and display-cache context. Cache context does not prove final source-material fidelity. PROCESS in this first batch is occluded by a closed shutter and is retained as failed evidence; use the corrected later view. WASTE and COMPLIANCE elevated views mainly show roofs and cannot establish interior art quality.

## Replay from A08

Run the Blender scripts in order: build_access_finish.py, integrate_access_finish.py, build_network_finish.py, integrate_map_finish.py, build_reactor_exterior_finish.py, finalize_map_finish.py, union_access_finish_floor.py. Then run verify_access.py with ACCESS_VERIFY_FILE set to A11 and ACCESS_VERIFY_REPORT set to the new report. review_map_finish.py generates the camera evidence; FINISH_VIEWS filters views and FINISH_NATIVE_RENDER=1 uses original context geometry.

GPU rendering uses the shared gate, owner astra-facility-assembly. Source sections are not edited. No main merge.

## Remaining acceptance work

The map is assembled and these connector details are built. This is not a claim of final whole-map art acceptance: exterior richness, terrain/large ground-cutout treatment, final materials and lighting still need an independent visual review. Game collision, navigation, cart physics and Unity performance remain deferred until map work is ready. The old approximately 50 FPS A08 static redraw result is not a new A11 or Unity benchmark.

Native-context render attempt was stopped before any image completed because full-scene processing was too slow for this walkthrough delivery. Its log is retained; native-material final art review remains outstanding. `renders-A11-corrected/PROCESS.png` uses the same camera with the nearest interlocked leaf staged open. The opposite leaf remains closed by design.

A11 live verification: Shift+F maps to view3d.facility_safe_walk; fast display enabled; gravity disabled; file saved and MCP released. A 40-frame static Solid redraw at the stair measured 30.38 FPS after the rendering job ended. This is slower than A08's earlier roughly 50 FPS result and remains an optimization item; it is not a Unity prediction. See PERFORMANCE.json.
