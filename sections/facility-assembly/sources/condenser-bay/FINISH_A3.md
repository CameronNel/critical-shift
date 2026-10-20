# Condenser A3: A2 plus legible wear, reachable controls, a warmer key-lit room and a full-height bay

Owner, 2026-10-19, after seeing A2 (Codex, PR #107) next to the A1 the map used: *"Rework the room to your liking, build into the main map
and then ensure the baking process will work"*, and on the layout *"Fix everything needed to make this scene perfect."*

A3 is `module_aaa_A3.blend`, built by [condenser_finish_A3.py](condenser_finish_A3.py) from A2's output
[module_aaa_A2.blend](module_aaa_A2.blend) (A2: [FINISH_A2.md](FINISH_A2.md), [condenser_finish_A2.py](condenser_finish_A2.py), from the
reviewed R34 `module.blend`). A3 adds to A2 and changes it only where listed below (the two CW isolation handwheels and the gauge impulse
lines they enclosed are replaced; the trip parts, desk lamp, west vent wheel, panel gauge needles, CW wall tags and north wall boards move; the two pump volutes and the U04
bellows are rebuilt). The build receipt, with every change, the
source and output hashes and an intersection check of the new parts, is [finish-A3-build.json](finish-A3-build.json).

```
blender -b --factory-startup module_aaa_A2.blend --python condenser_finish_A3.py            # writes module_aaa_A3.blend + finish-A3-build.json
blender -b --factory-startup module_aaa_A3.blend --python-exit-code 1 --python audit_A3_reach.py -- --ceiling 5.995 --out reach-A3.json
```

## Why

A2 answered the palette (machine-blue condenser, oxide-red waterboxes, graphite framing) and its independent review passed materials,
lighting, construction and machinery logic. It was still **rejected**, on things a finish brief could not touch:

1. **Gallery headroom 1.755 m** in the map. The bay sat at map z -6.0, so its own 0.3 m roof slab (module z 6.0..6.3) shared the turbine
   floor's volume and the map squeezed it 0.3 m down into the room.
2. **Controls out of reach** (rubric hard gate 8): the two overhead CW isolation valves (handwheels at 3.4 m), the condenser isolate (an
   anchor inside the west waterbox at 3.17 m, with no control at all), and the trip button (0.75 m from a standing operator).
3. Missing approved neighbour reference renders (a process gap: the reviewer had none to compare with).

And, on the pixels, it reads factory-new: flat paint, near-white walls, even light everywhere. `design/ART_DIRECTION.md` asks for an
"active and maintained" facility with "restrained evidence of use" (section 9), key light zones and darker secondary spaces (section 8).

The first A3 pass (same day) fixed 1 and 2 but its own independent review rejected it on the pixels: the wear did not render (its edge mask
compared the bevel normal with the shading normal, which is zero on these smooth-shaded meshes), the box-link chains read as dashed lines,
the chain wheels as three-spoke handwheels, the west vent spindle leaned out of a floating guide, and the desk housing read as a toy. This
file describes the second pass, which answers that review.

## What A3 changes

**Headroom: the map, not the room.** `combined/build_compact_map.py` places the bay at map z **-6.3** (`COND`), so its roof sits exactly
under the turbine floor; the roof patch keeps it 5 mm clear of the turbine floor's faces (no z-fighting). The stair takes the extra 0.3 m in
the same 34 risers (185 mm), the escape ladder follows `COND`, the U04 pit walls are stretched locally to meet the turbine machinery's
underside again (they stopped 6 cm short of it at -6.3), and `walk_test.py`, `measure_lighting.py` and `floor_audit.py` read the level from
the scene (`condenser_z`). Gallery headroom in the map: **2.068 m** at the standing spots, roof clearance over the deck 2.095 m (was 1.768 m).

**Reach** (measured by [audit_A3_reach.py](audit_A3_reach.py): 1.75 m worker, shoulder 1.45 m, arm 0.70 m, body radius 0.22 m, standing on
the floor, stairs and gallery, line of sight to the control; [reach-A3.json](reach-A3.json)):

| Control | A2 | A3 | Fix |
|---|---|---|---|
| `INTERACT_CW_ISOL_S`, `_R` (overhead globes, handwheels at 3.4 m) | no spot | 0.37 m | the handwheel gives way to a blue bevel-gear operator on the yoke; its shaft carries a pocketed chain wheel 0.22 m out, on whichever side the chain drops clear to the floor (ray test: south for SUPPLY, west for RETURN); a closed loop of oval links runs over the wheel to a U at 1.05 m |
| `INTERACT_EJ` (ejector steam isolation handwheel, 2.15 m) | 0.72 m | 0.31 m | the same chain wheel bolted in front of the vertical handwheel, its loop at the aisle edge (the skid and aisle leave no floor for a step) |
| `INTERACT_CD_ISOLATE` (floating inside the west waterbox) | no control | 0.45 m | the isolation is motor-operated: a CD ISOL selector on a desk-front control housing (the panel's selector row is full) |
| `INTERACT_CSB_TRIP` (panel face above the desk's back edge) | 0.75 m | 0.45 m | the original trip parts, turned to face up, on the same housing, on a yellow emergency-stop ground with a guard collar; a blanking plate on the panel face covers the old hole |
| West waterbox vent wheel (4.64 m) | 0.97 m | 0.66 m | a vertical extension spindle in a guide bracket bolted to the waterbox top, a right-angle gearbox at 5.05 m and the same wheel stood on edge facing the gallery |
| East waterbox vent wheel | 0.54 m | 0.54 m | unchanged: already within reach |

The other hooks are unchanged (D01 0.41, CEP-A 0.32, CEP-B 0.31, CSB CEP 0.52, CSB VACUUM 0.44, HOIST 0.26 m). The waterbox manways (3.27 m)
remain outage work from a temporary platform, as in R34; they are not contract hooks.

The CW gauges' impulse lines rose through the old handwheel hubs; they now leave the instrument root sideways at 3.30 m and enter each gauge
from below. The CW wall tags sit on the wall now (A2's plates stood 6.5 cm off it, their lettering 2.5 cm in front of the plate); RETURN is
raised 0.25 m, and SUPPLY, whose chain and gear operator stand in front of it from the cooling camera, moves 1.0 m north and 0.55 m up
(a ray test of C06 and C05 picked it: 81 % of the tag seen from C06, was 51 %).

**Wear**, sized to read at 3 to 5 m. Positions come from the mesh attribute `A3_pos` (module-space vertex positions), so localized wear stays
put in the module, in the map and in the bake; shared meshes and curves keep the attribute-free layers.
- painted machinery: cavity and contact grime (AO), worn paint on convex edges in small, broken lengths showing dark steel (inside-AO edge mask; parts under
  8 cm thick get a variant without it, since inside AO marks a thin plate's whole face), a broken film of handling grime, run-off streaks
  on vertical faces, dust on tops, grime at the bases up to 1 m, quieter large fields on the condenser and waterboxes (a third of the way
  to grey, +-10 % tone), two fresher touch-up patches on the shell's south flank, weep streaks under the waterbox covers' lower bolts;
- the impact dado and column feet: scuffed bands of dark primer where trolleys and boots hit (the west entry and the east pull bay);
- walls: about 40 % of A2's fine grain and a third of its bump (it read as mottle), darker and warmer, +-9 % per 1.5 x 3 m formwork panel,
  water marks from above in patches, a floor-line grime band and streaks under wall-hung services;
- floor: +-18 % large-scale dirt, grime against walls and plinths, glossy oil at the two pump bases, their seals, the hotwell and ejector
  drains, damp patches under the CW valves and at the trench drain.

**Light** (`design/ART_DIRECTION.md` section 8; the neighbours are warm and dark): A2's nine ceiling battens to 45 % and warmer (about
3,800 K), the fill washes to 60 % (the gallery inspection lights to 45 %), a 45 W warm wash up onto the roof slab, the task lights over the condenser, the pumps and the desk and the three wall practicals +30 %. The fill
washes, which have no fixture, are hidden from glossy rays: their rectangles showed as a pale panel on the east waterbox (A2 review, W05).

**Repairs to A2 geometry** (found by the second and third independent reviews): each CEP pump's volute was a flat disc with a notch, now
a scroll growing from 0.30 to 0.40 m round the impeller centre, with a full-width discharge throat into the cast boss over the cutwater
step, on cast-iron grey feet; the U04 expansion joint was a 36-vertex folded sheet whose knife-edged pleats overhung the flanges, now four
rounded convolutions (60 mm crests, 0.16 m corner radius) inside the bolting plates' outline; the desk lamp's head stood 0.10 m beside its
post, held by nothing, now a conical shade on it; the six gauges (four on the panel, two on the CW valves) all read the same angle, now
each its own running value; the room ID and hazard boards on the north wall stood 2 cm off it and were cut by pipes and rails in most
views: they are on the wall and 1.2 m west (the best of the positions a ray test of the north-facing views tried), and a second room ID
hangs on the south wall at x 7.5, the clearest place in a ray test of every wall from the review views. A review camera, `C11_WEST_VENT`,
shows the west vent extension.

**Palette:** the large machine fields move into the facility's family (turbine, cooling plant): the machine blue a third of the way to
grey and 30 % towards gunmetal, the waterbox and pump reds 30 to 45 % towards burgundy oxide, so the room no longer reads royal blue and
signal red next to its neighbours. Hues are kept; the two reviews of A3 both scored the saturated fields down.

**Desk:** the control housing is charcoal, its legends light and 26 mm high; the trip mushroom stands on a round yellow emergency-stop
enclosure (the panel bezel's square block is gone) and CD ISOL is a rotary handle on a knob, turned to ON; the lamp is a dark conical
shade with the warm diffuser under it (it was a glowing white puck), between LOCAL and CW ISOLATE, 0.10 m lower, clear of the captions.

Triangles: **394,676** evaluated, text included (A2 349,678; budget 400,000). The chains are 80 triangles a link.

## Independent reviews: not accepted

Four independent reviews against `sections/condenser-bay/production/RUBRIC.md` (a category passes only above 90, every hard gate must pass),
each by a fresh reviewer that did not build the room. All four **rejected** it:

| Round | File | Coverage | Scale | Machinery | Circulation | Construction | Materials | Lighting | Palette | Storytelling | Fidelity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (first pass, 960 px) | first A3 | 91 | 91 | 90 | 90 | 86 | 89 | 89 | 88 | 89 | 87 |
| 2 (second pass) | `06f9...` / `34b7...` | 87 | 89 | 85 | 85 | 81 | 83 | 87 | 80 | 84 | 77 |
| 3 | `87d8ca5e...` | 91 | 92 | 90 | 89 | 88 | 87 | 90 | 89 | 89 | 87 |
| 4 (final) | `20df1300...` | 91 | 92 | 90 | 90 | 89 | 87 | 90 | 89 | 89 | 87 |

Each round's concrete defects were fixed in the next (floating lamp head and trip parts, the vent spindle gap, knife-edged bellows,
blotchy and pale wear, the C10 speck, the pink reflection, unreadable signs, identical gauges, missing evidence). What the final review
still holds against it: the pump volutes and chain links read low-poly up close, the D01 door jambs' orange, wear that reads only close up
(surfaces "factory-clean" next to the cooling plant), the CW SUPPLY tag crossed by its gauge's impulse line in C06, the room ID boards
partly hidden from some views, a blown highlight on the east waterbox cover (W04), salmon waterbox tops under the gallery light, the
near-black roof beam underside, blade-like motor fins (A2), the U04 bolt-hole light spots (inherited).

**Owner decision, 2026-10-20**, after the third review: *"One more pass, then merge"*: fix the objective defects, re-run the checks and the
evidence, then merge whatever the score, recorded honestly. This file, `AGENTS.md` and the PR record it as **not accepted** at the
rubric's bar; the room's status stays "built but not ready".

## Checks

The map chain on the rebuilt map, the CPU bake rehearsal and the review renders are in `combined/ASSEMBLY_REPORT.md` (section "Condenser A3")
and the PR. The reach audit is above; with the roof at 5.5 it fails, as it should (no standing room on the deck).

## Limits

- Cycles renders on the cloud CPU (owner's choice for review renders); the GPU bake is the owner's, later.
- No Unity run; the interaction anchors are geometry, not engine interactions.
- The chain loops are rigid meshes (no swing). The inside-AO edge wear makes the bake slower than plain textures would (it is a ray-traced
  node); it bakes like the AO grime A1 and A2 already used.
- Palette: the machine colours keep A2's hues (its answer to the "more machine colour" brief) but are pulled into the facility's
  gunmetal / burgundy-oxide family; if the owner wants A2's brighter fields back, `PALETTE` in the script is the one place to change.
- The north wall boards are still partly hidden from some floor views; the room is identified at its entry by the CSB-01 signs over D01.
- Inherited and left: the soft light spots on the U04 bolting plate above each nut (light through the bolt holes, C04).
