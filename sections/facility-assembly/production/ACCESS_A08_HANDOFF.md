# A08 — condenser access and working Blender doors

Step 2 adds the six-metre condenser stair, cart lift and lower passage to the existing horizontal map. The rescue route stays at x32–36; the stair and lift openings sit west of it. A07 and every source module remain intact.

## Delivered

- Two stair flights, 36 equal 166.7 mm risers, 280 mm treads, 1.48 m clear width, intermediate landing, guards, retaining enclosure and framed upper entrance.
- Two-stop cart lift: 6 m travel, landing gates, travelling cabin gate, interlocked movement and passenger-view follow. Cabin clear space is approximately 2.0 × 2.8 m; a long cart must be oriented along the cabin's long axis. Physical cart manoeuvring remains a step 3 test.
- 34 working roller-door controllers, including lift gates and process/compliance airlocks. Automatic proximity opening and explicit controls are in N → Walkthrough → Doors and Cart Lift.
- Assembly-local source collection overrides remove scenic closed leaves/caps. Compliance's back wall and condenser D01 blanking closures are replaced with open framed portals. Turbine U02 is untouched.
- Matching edited display meshes, batched curtains and cached controller references. Idle doors do not repeatedly update the scene.

## Open and use

`blender/facility_walkthrough_A08_access.blend` is the optimized walkthrough; `blender/facility_master_A08_access.blend` retains source authoring collections for editing/rendering. The launcher selects A08. Enable `facility_access_tools.py` alongside `facility_walkthrough_tools.py` if opening on another profile.

Shift+F starts native Blender walk. Gravity stays disabled. E/Q changes elevation; game-controller stair climbing/collision is not implemented by this Blender navigation mode. Stand inside the lift, then use Lift to ground / Lift to condenser. The viewpoint follows the moving cabin. Disable Automatic proximity doors when manually staging door states.

## Verification

`connections/access/VALIDATION.json` records cold-process checks of every door, 60 airlock transition samples, 420 lift samples, passenger follow in both directions, source doorway rays and 2.1 m vertical headroom at all 36 stair centres. `renders/` contains five fresh Workbench geometry review views; these are not final lighting/art renders.

`PERFORMANCE.json` records approximately 50 FPS for a 40-frame static solid viewport redraw at the stair. This is not an engine gameplay frame-rate guarantee.

## Replay

From the assembly directory, run Blender headless in order: `build_access.py`, `integrate_access.py`, `finalize_access.py`, `open_condenser_access.py`, `finish_access_shaft.py`. Run `verify_access.py` through the shared GPU gate with owner `astra-facility-assembly`. `plan_access_doors.py` regenerates the initial exact source-name bindings. Later compliance/condenser cap overrides are explicit in the finishing scripts.

## Remaining

Step 3: actual game-controller collision/navmesh, physical cart loading, door collision/obstruction sensors, lift passenger physics and route playtests. Step 4: final materials, lighting, signs and art polish. Blender door/lift logic is an inspectable prototype and must be bound to the game runtime before gameplay acceptance.
