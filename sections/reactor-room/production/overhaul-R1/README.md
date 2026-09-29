# Reactor room overhaul R1 (draft, needs review)

Additive candidate: `sections/facility-assembly/sources/reactor-room/module_overhaul_R1.blend` (**not in this commit**: the Git LFS upload was blocked by the session's network policy for `lfs.github.com`; it will be added once that host is allowed. Until then the file can be rebuilt from `module.blend` with `scripts/`).
`module.blend` is untouched because `MASTER_MANIFEST.json` pins its SHA-256, and the assembled map still links it. The map shows none of this until the revision is reviewed and promoted (manifest hash, MAP.json and the derived preview regenerated).

## What changed in R1

| Area | Before | R1 |
|---|---|---|
| Control room | Outside the east wall at +10 m, window facing the east, so bank B hides behind bank A | Inside the hall on the -Y wall as a mezzanine (floor +5.4 m), 5.4 x 2.4 m window on the axis where both banks and the pool are side by side |
| Access | External stair core (about 700 objects) and a floor-level door to it | Traction elevator in the hall's south-west corner zone (x -8.0 to -5.6, y -8.0 to -5.6): glazed shaft, car, guide rails, counterweight, ropes, sheave and motor, with a railed upper landing and a door into the control room's west wall |
| East wall | Door and window openings | Patched panels; old "REACTOR CONTROL / 10" sign removed |
| Motion | Single 200-frame bank descent | 480-frame loop (16 s at 30 fps): banks A and B move out of phase between 7.0 and 8.5 m, pool glow pulses, elevator cycles ground and upper landing with ropes and counterweight following |
| Palette | White, grey and orange with an amber pool | Putty walls, petrol/ink steel, mustard trim, coral emergency red, warm clay floor, cyan pool (pool lights and volume restored to cyan) |
| Review cameras | `01_HERO` and `09_BANK_MECHANISMS` sat inside the new room | Moved to clear positions |

Interior contents of the old control room (1,493 objects from desks, screens and mimic panel) were rotated -90 degrees about Z and translated (x0 = -1.4, y +5.0, z -4.6) onto the mezzanine. Nothing else in the hall was moved.

## Placement constraints found

- The -Y wall is fully occupied at floor level (coolant pumps x -5.3 to -2.5, coolant valve x -1.7 to 0.7, emergency cooling EC-1/EC-2 x 1.1 to 3.9, storage x 4.3 to 5.1). The elevator therefore stands in the free south-west zone; the mezzanine only covers the emergency-cooling and pump area overhead (underside at +4.9 m, tallest equipment 2.8 m, coolant header at 4.7 m).
- All eight walls carry a door or equipment. The two banks sit at x = -1.4 and +1.4 (same y), so a window on the east or west wall always sees one behind the other; the -Y and +Y walls see them side by side.
- The east wall panels around the old door and window were patched with plain panels. The wall-mounted "A / SECTOR" graphics remain.

## Not done in R1

- Pipe, conduit and cable logic audit (every run needs a source, a sink and supports). Only the elevator ropes and the elevator/control-room additions were built with logic.
- Cables from the control room to the pool console and the banks, and elevator power feed.
- Remaining dressing, new assets, equipment layout changes and per-room lighting balance.
- Floor colour and the pool tile still need tuning after review; old conduit saddles at the back of the mezzanine (y -10.1 to -9.9, z 6.8 to 7.2) may clip and need rerouting.
- Not promoted: `module.blend`, `MASTER_MANIFEST.json`, MAP.json and the R17 preview are unchanged. The spec (`scenery/reactorroom.md` section 8) still says +10 m for the control room.
- No independent review, no collision/navmesh, no measured performance, no Unity import.

## Reproduce

`scripts/` holds the Blender Python steps in order: `b1.py` (relocate/delete), `b2.py` (wall patches, mezzanine, elevator), `b3.py` (palette via `palette.py`, pool lights, animation), `b4.py` (cameras, cleanup), `b5.py` (moves the elevator to the free south-west zone, rebuilds the landing and the door, patches the rest of the old east window). `render_final.py` makes the PR renders. They read and write `w1..w5.blend` from a scratch directory and need `bpy` 5.2.x (`pip install bpy==5.2.2` on Python 3.13). Renders in `../renders/overhaul-R1/` were Cycles CPU, 24 samples, frame 180. Before images in `before/` are 960x540, 12 samples.
