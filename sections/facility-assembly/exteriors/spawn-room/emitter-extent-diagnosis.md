# Finite emitter extent diagnosis — spawn R04 / turbine R01

Confirmed geometric defect: several **tilted AREA emitters cross the shell**, even though their centers are indoors and shadow casting is enabled. There are no POINT/SPOT lights in either inspected set, so no operative point shadow_soft_size radius explains these scenes. For DISK emitters below, listed size is diameter; for RECTANGLE it is width x height.

The script computes evaluated closest mesh surfaces, transforms emitter planes into world coordinates, and raycasts 64 radial segments from emitter center to its actual disk/rectangle boundary against exterior meshes plus original roof/ceiling meshes. The listed positive hits establish actual finite-plane/surface crossings, not just overlapping AABBs. A no-hit is not an exhaustive proof for arbitrary tiny intersections.

| Spawn light | Disk diameter | Center-to-original ceiling | Center-to-added membrane | Confirmed crossings |
|---|---:|---:|---:|---|
| V_LIGHT_BRIEF_wall | 1.70 m | .250 m | .410 m | BRIEFING_ceiling + Briefing membrane |
| V_LIGHT_HALL_info | 1.40 m | .250 m | .410 m | HALL_ceiling + Hall membrane |
| V_LIGHT_HALL_staff | 1.20 m | .230 m | .390 m | HALL_ceiling + Hall membrane |
| V_LIGHT_LOCKER_bays | 1.80 m | .260 m | .420 m | LOCKER_ceiling + Locker membrane |

These are angled wall/bay fill lights. In contrast, BRIEFING/HALL/LOCKER/SERVICE photometric emitters are horizontal downward-facing rectangles (lengths 1.27/1.14/1.47/1.02 m, width .23 m), about .287 m below their added membrane; no roof-crossing hit was found for them. Floor-bounce disks are horizontal at Z=.25 and do not reach the roof. The four V_LIGHT names are the priority, not the earlier floor-bounce shadow flags.

| Turbine light | Emitter size | Nearest exterior skin distance from center | Confirmed crossings |
|---|---:|---:|---|
| Entry broad fill | DISK 4.0 m | 1.000 m (front wall; original roof girder nearer at .750 m) | Roof deck, front wall/overwall skin, sign and roof girders |
| Hall broad daylight | DISK 5.0 m | .701 m | Roof deck, side skins, exterior pilaster and girders |
| Clerestory broad fill, .001, .002 | RECTANGLE 2.8 x 1.3 m | .481 m each | Side skin panels .013/.016/.018 |

For turbine, roof-deck hit examples are Z=7.200 m: Entry broad fill intersects near (2.008,1.350,7.200); Hall broad daylight near (8.260,11.563,7.200). Their tilted emitter extents reach above that plane. The report's nearest-roof metric includes girders, so it must not be mistaken for center-to-deck distance.

Secondary fixture-local intersections: spawn Shift entry pool emitters cross their sconce glass; turbine Turbine entrance pool intersects overwall/sign geometry. These are distinct from the broad roof/wall leakage candidates and should not automatically be treated as identical failures.

Action: in assembly-only local light overrides, shrink/reposition the named angled fill emitters so their **entire emitting plane** remains inside intended room boundaries with clearance. Keep source files and original room meshes untouched. Verify actual emitter extents after adjustment, then rerender identical cameras. Enabling shadows or adding another roof cannot occlude the part of an emitter already outside the shell. This establishes a concrete leakage mechanism but does not claim per-pixel sole causality without the subsequent render comparison.

Evidence: emitter-extents.py; spawn-room/emitter-extents-R04.json; turbine-room/emitter-extents-R01.json. JSON includes dimensions, directions, world corners, closest surfaces and exact ray-hit coordinates. CPU inspection only; no rendering/model saves/asset edits.
