# C79 station-drain grille contact review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle79/hall_final.blend`  
**Scene SHA-256:** `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b`  
**Disposition:** physical bearing/contact confirmed for the access-lane square drain; rendered confirmation remains pending in exact C79 main03 and tighter view33.

## Correct subject

Item #72 is the removable square station-drain grille, not the three remote catch-basin grates at `(±7.5, 7.5)` and `(3, -7.7)`. The matching drain is the sixth `rh_st_props.py::drain` placement at `(-6.95, -0.60)`, yaw `0`, which sits in the intended main03/view33 access-lane target area. Its corresponding `rh_floor.py::OTHER_DRAINS` cut has a main pocket `0.605 × 0.425 m` deep to `z=-0.20 m` and a wider `0.665 × 0.485 m` rebate to `z=-0.04 m`.

## Saved-mesh interface probe

I loaded the exact C79 scene in portable Blender 5.2.2 and built BVHs from the saved `RH stations props IRON` and `RH stations props STEEL` meshes. At both grille-to-support intersections, the two actual surfaces coincide at `z=-0.035 m`:

| Interface point (m) | Saved surface result |
|---|---|
| `(-6.95, -0.48, -0.035)` | IRON grille underside normal `(0,0,-1)` and STEEL crossrail top normal `(0,0,1)`; separation below `0.1 μm` |
| `(-6.95, -0.72, -0.035)` | IRON grille underside normal `(0,0,-1)` and STEEL crossrail top normal `(0,0,1)`; separation below `0.2 μm` |

The two STEEL crossrails span the square opening at local `y=±0.12 m`, from `z=-0.055` to `-0.035 m`; the nine IRON grille bars meet their tops with their lower faces at `z=-0.035 m`. This provides two actual internal support rails below the removable bar grate.

The four saved frame-to-floor contacts at `(-7.265,-0.8,-0.04)`, `(-7.265,-0.4,-0.04)`, `(-6.635,-0.8,-0.04)`, and `(-6.635,-0.4,-0.04)` were independently queried on the saved `RH stations props IRON` mesh. Each lies on the frame underside within `0.12 μm`. The exact C79 audit rays from those frame surfaces hit the `R2 floor` rebate with zero measured gap and zero normal error. The frame outer edges are at `x=±0.33 m`, `y=±0.24 m`, inside the wider rebate by approximately `2.5 mm` at each side.

These measured interfaces establish that the grille is physically supported by the two crossrails and the assembled frame is seated on the floor rebate. The saved prop has open bar spacing through which a service hook can engage. The original criterion asks for underside/contact evidence; it does not require a separate lifting eye, so the absent eye is not a failure.

## Render scope

Main03 provides the context frame. View33 uses the same elevated camera position with a tighter lens to show the access-lane grate more closely. View34 targets the annular pool trench and is not evidence for this station drain. Neither access-lane view exposes the hidden underside directly, so the saved surface probe is the evidence for the support interface; use pixels to judge whether the visible grille and rebate read clearly and whether the absence of a dedicated lifting tab is a genuine criterion failure.
