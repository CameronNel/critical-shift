# Compact layout: the main map (2026-10-12)

**Unreviewed, not accepted.** Owner instructions: "the map should be as compact as possible ... make this thing as close knit and tight as possible. Reuse what you can", then "Use the compact layout as the main map".
`combined_map.blend` is now built by `build_compact_map.py` (it imports `build_combined_map.py` and overrides the room placements and the hall list). `COMBINED_MAP.md` keeps the decision record of the older spread-out layout (plan v7 positions, long halls, outer ring), which is superseded wherever it disagrees with this file; its measurements and door data still stand.
Never hand-edit `combined_map.blend`. Rebuild: `blender --background --python build_compact_map.py`. The older layout still rebuilds with `build_combined_map.py --through compliance-dock --output spread_layout.blend`. The same source-file fetches as `AGENT_READ_FIRST.md` apply, plus the AAA finishes `sources/{waste-storage,cooling-plant,condenser-bay}/module_aaa_A1.blend` (LFS).

## What changed against the combined layout

| Room | Combined layout | Compact layout | Fixed by |
|---|---|---|---|
| Reactor, front end, spawn, mine, refinery, medical, fuel corridor | as built | **unchanged** | their own rails, the 34 m spine, the corridor and the yard portal; moving any of them breaks those interfaces |
| Turbine (AAA finish) | origin (0, 17) | origin **(0, 14.5)**: end wall on the reactor N stub outer end, no hall | reactor stub measured y 10.8 to 14.5; turbine end wall module y 0.0 |
| Electrical (R11) | (19.75, 26.25) NE, 2 halls away | origin **(0, 39.95)**, touching the turbine's far door | turbine and electrical CONNECTIONS.md: origin (0, 25.45) in turbine coordinates, collinear 2.4 m openings |
| Condenser bay (AAA finish) | not placed | origin **(1.6, 21.9, -6.0)**, under the turbine | its CONNECTIONS.md: turbine = local + (1.6, 7.4, -6.0); U04 receive lands on turbine U04 (4.6, 11.45, 0) |
| Waste (AAA finish `module_aaa_A1.blend`) | (28.32, -24), 23 m hall | origin **(16.2, -16.2)**, rotation -135, 7 m hall from the SE stub seam | WS_RECEIVING threshold on the stub axis (11.0163, -11.0163 seam, cooling CONNECTIONS.md) |
| Cooling (AAA finish `module_aaa_A1.blend`) | (-44.1, -19), 40 m hall | origin **(-14.5, 0)**, rotation +90, on the W stub end | CP-P01 on the stub end; cooling owns y >= 0, reactor owns the stub |
| Compliance dock | (60, -79), 129 m trunk | origin **(38, -54)**, rotation -90, 2 m past the front-end hall east stub | P1 threshold; hall east door stub ends at x 36 |

Dropped halls: the bridge, electrical spur, east trunk, dock link, waste personnel and dispatch halls, medical direct door, outer ring west arm, yard passage and the fuel-service hall (about 450 m of hall in all). Kept: the south concourse and tunnel, and the 7 m waste hall.
New: a 3.9 m hall from the waste personnel door (WS_PERSONNEL, module (6.32, 2.4)) to the front-end spine's east wall (cut in a local copy, like the concourse cut on the west wall), so waste is also reachable from the spine.
Reactor stub doors: the closed door pieces on the N, W and SE stubs (75 objects) are left out of the local membership so the stubs are open. **This also applies to the combined layout, where they were still closed** (the earlier audits started past the door and did not see it).

## Checked (run)
- Build `build_compact_map.py`: about 40 s.
- `check_footprints.py` (plain Python, 2D rotated-rectangle overlap of every room's measured outer bounds): no new overlap; 18 footprints; the only overlap >= 0.5 m, fuel corridor against refinery, is the pre-existing sill overlap of rough bounding boxes. Extent x -52 to 54, y -105 to 57 (mine further west at x -112, unchanged).
- Ray lanes (z 1.5): reactor to turbine to electrical along x = 0, clear to the electrical north door plate; reactor to cooling clear to its rear wall; reactor to waste clear to the dispatch plate; front-end hall east door to the dock clear to the sealed P2 leaf; waste personnel door through the new hall and spine east wall clear.
- Renders (every image looked at): reactor stub into turbine D01, turbine into electrical, reactor into cooling, reactor into waste with the airlock, the waste dispatch hall, the dock entry, the condenser bay under the turbine, plan views. The waste-to-spine hall render only shows a wall (camera at the bend), so that hall is checked by rays only.
- `validate_halls.py` (compact is the default; `SPREAD=1` audits the old layout) (two halls left): `PASS (geometry audit only)`, report `validation/compact_report.json`: waste hall 7.0 m and waste-spine hall 3.9 m, 0 walk obstructions, 0 sphere escapes of 1,000 each. Evaluated triangles of the whole scene: 13,230,889 (vs 13.16 M in the combined layout, the condenser bay adds 0.77 M while the long halls drop from 0.46 M to 0.06 M). The compact layout is smaller in area, not lighter in triangles.
- Renders `renders/15_compact_*`.

## Not checked
No collision with a player capsule, door animation (the stub, turbine D01/D02, electrical D01 and cooling P01 doors are open or parked in these renders; closed leaves on other doors are untouched), lighting balance, the condenser bay's service door D01 (plated, underground), whether the condenser top meets the turbine floor cleanly, performance, Unity. The condenser bay at z -6 has no walkable access from the facility yet; only the U04 opening above links the two. Not built here: gantry (no attachment spec). Travel times are not recomputed.

## Source files in use (swap done 2026-10-12 on the owner's request)
Waste, cooling and the condenser bay now use their **AAA finishes** (`module_aaa_A1.blend`, 3 and 4 Oct on `main`, material and lighting passes, unreviewed, no validator run) instead of the 14 Sep originals. The same turbine file (AAA, branch `claude/turbine-aaa`, 3 Oct) was already in use. Measured before the swap: same bounding boxes and the same interface empties as the originals (waste x -6.32 to 7.61, y -0.32 to 18.32; cooling x -5.8 to 5.8, y 0 to 13.3; condenser x -2.1 to 9.88, y -2.56 to 9.68), so no placement moved. After the swap: same ray lanes (reactor to cooling, to waste, waste personnel hall to the spine) clear. Waste AAA has a few more architecture meshes (432 against 428). Triangles: waste AAA 329k and cooling AAA 276k and condenser AAA 345k by the file inspector (the originals counted 329k, 383k and 513k there).
Files older than two weeks still in use: none. Every other file was last changed between 1 and 10 Oct (spawn 1 Oct, electrical R11 2 Oct, fuel corridor 2 Oct).
Checked after the swap: `validate_halls.py` PASS (geometry only), report refreshed in `validation/compact_report.json`; whole-scene evaluated triangles **12,462,677** (down from 13.23 M, mostly the condenser bay's AAA file at 345k against 513k). Renders `16_aaa_*`, every image looked at: the AAA rooms read darker and dirtier than the originals (wet floor reflections, rust on the condenser bay's walls and shell, cold light in waste), the doors and lanes line up unchanged. Not checked: that the darker finish still lets players see (no lighting-balance measurement), the AAA files' own known open items (waste and condenser reach checks in their `reach-check.json`: some overhead cooling-water valves are unreachable in the condenser bay).

## Owner acceptance (2026-10-12)
The owner accepted the AAA finishes now in the map (turbine, waste, cooling, condenser bay) with "Accept them". This is the owner's decision. No independent review or validator run has happened on any of these finishes, so this file and `AGENTS.md` record it as **owner accepted, unreviewed**, not as a review pass. The layout, halls and the rest of the scene remain unreviewed.
