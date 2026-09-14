# A12 — construction gaps closed

Built the remaining terrain/perimeter work and repaired the blocked spawn transition. Unity remains paused. This handoff covers map construction; art polish and game-runtime integration remain separate.

## Delivered

- 4,151 fitted ground cells close uncovered space around the room footprints. Existing roof, wall and below-grade source surfaces are preserved. Stair and lift openings remain intact.
- Retaining walls and 1.1 m guards along exposed drop edges, skipped at planned routes and existing facades. A 2.4 m outside wall encloses the site at x -110..82, y -67..86.
- A continuous below-grade base at z -8 closes the site beneath the basement rooms; outside wall foundations extend to it.
- Spawn's SERVICE_end wall, dado, coved skirt and dado cap are excluded from the assembly collection and matching display mesh. A 2.6 m wide, 2.7 m high framed portal connects the working inner airlock to R10. The linked source file is unchanged.
- Six additional mesh objects total. Room layout and rescue shortcuts are unchanged. A12 layout documentation replaces R19's stale reservation with the actual stair centreline.

## Verification and limits

All 21 horizontal routes plus the spawn inner transition were checked at intervals no greater than 0.4 m. The scan tests floor support and vertical clearance at centre and +/-0.6 m, plus centreline crossing rays every 0.15 m from 0.15 to 1.95 m height. 4,779 sample positions: zero findings after the spawn fix. Doors are staged open for this geometric test; this is not continuous collision detection or a complete interior gameplay test.

The existing regression also passes: 34 door controllers, 60 airlock transition samples, 420 lift samples, passenger follow, source doorway rays and stair headroom. Geometry evidence is in connections/completion. Earlier failed spawn scans/renders remain as history.

Cycles previews use the original new geometry with display-cache room context. They establish construction, not final source-material quality. The final render folder supersedes the first batch for spawn and below-grade views.

## Open and replay

The existing Blender walkthrough is updated to facility_walkthrough_A12_complete.blend; the launcher prefers A12. Shift+F starts walk, gravity is disabled, and N > Walkthrough retains fast/original display and door/lift controls. facility_master_A12_complete.blend retains the authoring display configuration.

Replay from A11: build_map_completion.py, fix_spawn_transition.py, close_site_base.py. Run audit_map_routes.py with MAP_AUDIT_FILE=facility_walkthrough_A12_complete.blend and verify_access.py with ACCESS_VERIFY_FILE/REPORT overrides. review_map_finish.py supports FINISH_FILE, FINISH_VIEWS and FINISH_RENDER_DIR. GPU owner is astra-facility-assembly through the shared gate.

No source-room edits and no main merge. Final art, viewport optimization, Unity colliders/navmesh and physical gameplay/cart tests remain separate work.

The last spawn image is `connections/completion/renders-verified/SPAWN_EXIT.png`; it supersedes the intermediate image with residual wall trims. The two trim objects and 78 corresponding cached faces were removed after pixel inspection. `audit-final-dense.log` records the tightened crossing-height scan.
