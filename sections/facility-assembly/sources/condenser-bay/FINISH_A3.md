# Condenser A3: A2 plus authored wear, reachable controls and a full-height bay

Owner, 2026-10-19, after seeing A2 (Codex, PR #107) next to the A1 the map used: *"Rework the room to your liking, build into the main map
and then ensure the baking process will work"*, and on the layout *"Fix everything needed to make this scene perfect."*

A3 is `module_aaa_A3.blend`, built by [condenser_finish_A3.py](condenser_finish_A3.py) from A2's output
[module_aaa_A2.blend](module_aaa_A2.blend) (A2: [FINISH_A2.md](FINISH_A2.md), [condenser_finish_A2.py](condenser_finish_A2.py), from the
reviewed R34 `module.blend`). Every A2 object, name and material stays; A3 only adds. The build receipt, with every change and the source and
output hashes, is [finish-A3-build.json](finish-A3-build.json).

```
blender -b --factory-startup module_aaa_A2.blend --python condenser_finish_A3.py            # writes module_aaa_A3.blend + finish-A3-build.json
blender -b --factory-startup module_aaa_A3.blend --python audit_A3_reach.py -- --ceiling 5.995 --out reach-A3.json
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

## What A3 changes

**Headroom: the map, not the room.** `combined/build_compact_map.py` now places the bay at map z **-6.3** (`COND`), so its roof sits exactly
under the turbine floor; the roof patch keeps it 5 mm clear of the turbine floor's faces (no z-fighting). The stair takes the extra 0.3 m in
the same 34 risers (185 mm), the escape ladder follows `COND`, and `walk_test.py`, `measure_lighting.py` and `floor_audit.py` read the level
from the scene (`condenser_z`). Gallery headroom in the map: **2.068 m** (was 1.768 m by the same audit).

**Reach** (measured by [audit_A3_reach.py](audit_A3_reach.py): 1.75 m worker, shoulder 1.45 m, arm 0.70 m, body radius 0.22 m, standing on
the floor, stairs and gallery, line of sight to the control):

| Control | A2 | A3 | Fix |
|---|---|---|---|
| `INTERACT_CW_ISOL_S`, `_R` (overhead globes, handwheels at 3.4 m) | no spot | 0.29 m | bevel-gear chain-wheel operator on each stem; chain loop dropped on the side clear to the floor (ray test) to a grip at 1.11 m |
| `INTERACT_EJ` (ejector steam isolation handwheel, 2.15 m) | 0.72 m | 0.25 m | chain wheel bolted in front of the vertical handwheel, chain at the aisle edge (the skid and aisle leave no floor for a step) |
| `INTERACT_CD_ISOLATE` (floating inside the west waterbox) | no control | 0.45 m | the isolation is motor-operated: a CD ISOL selector on a desk-front control housing (the panel's selector row is full) |
| `INTERACT_CSB_TRIP` (panel face above the desk's back edge) | 0.75 m | 0.45 m | the original trip parts moved, facing up, onto the same housing; a blanking plate covers the old hole |
| West waterbox vent wheel (4.64 m) | 0.97 m | 0.64 m | extension spindle: 0.155 m towards the west gallery run and 0.45 m up, clear above its rail |
| East waterbox vent wheel | 0.54 m | 0.38 m | extension spindle, 0.10 m east and 0.30 m up |

The other hooks are unchanged (D01 0.41, CEP-A 0.32, CEP-B 0.31, CSB CEP 0.58, CSB VACUUM 0.44, HOIST 0.26 m). The waterbox manways (3.27 m)
remain outage work from a temporary platform, as in R34; they are not contract hooks.

**Wear** (positions from the mesh attribute `A3_pos`, module-space vertex positions, so localized wear stays put in the module, in the map and
in the bake; only single-user meshes get it, shared fastener meshes and curves keep the attribute-free layers):
- painted machinery: cavity grime (AO), chipped paint on hard edges in broken lengths (bevel-normal mask), grime at the bases up to 0.6 m,
  settled dust on upward faces, low-frequency tone (blue and red enamel, +-6 %), two fresher touch-up patches on the shell's south flank,
  weep streaks under the waterbox covers' lower bolts;
- the impact dado and column feet: a few larger chips showing grey primer, only where trolleys and boots hit;
- walls: about 22 % darker and warmer than A2's near-white, +-7 % per 1.5 x 3 m formwork panel, a floor-line grime band, faint water marks
  from above and streaks under wall-hung services;
- floor: oil at the two pump bases and under the hotwell drain, damp patches under the CW valves and at the trench drain.

**Light:** A2's nine ceiling battens (about 1 kW of 1.8 kW) -35 %, the equipment task lights +10 %, for key zones and falloff.

**Small defects from A2's review:** the desk lamp no longer covers the LOCAL caption (moved between LOCAL and CW ISOLATE, head 0.10 m lower).

Triangles: **354,840** evaluated, text included (A2 349,678; budget 400,000).

## Checks

See the PR and `combined/ASSEMBLY_REPORT.md` for the map chain on the rebuilt map; the reach audit is above.

## Limits

- Cycles renders on the cloud CPU (owner's choice for review renders), 640 to 960 px; the GPU bake is the owner's, later.
- No Unity run; the interaction anchors are geometry, not engine interactions.
- The chain loops are rigid meshes (no swing).
