# A07 — complete horizontal connection construction

User scope: step 1, build the remaining hallways, airlocks and outdoor courtyards. All 21 horizontal routes are built and integrated. Architectural review PASS in connections/network/REVIEW_R03.md. This is not final art or runtime acceptance.

## Delivered
Enclosed transfer/process/service links with wall bays, plinths, stripes, roofs, supported utilities, portal frames, crossing openings and retracted airlock/shutter architecture. Outdoor rescue/clean routes, power and receiving courts, service streets and maintenance loops have paving, edge structures, shade, lighting fixtures and furnished utility/planting pockets. The rescue courtyard and whole-map ground remain intact.

| Route | Architecture | Clear route width |
|---|---|---|
| R01 | ore yard | 5 m |
| R02 | transfer hall | 4.5 m |
| R03 | process airlock | 6 m |
| R04 | machinery hall | 4 m |
| R05 | power courtyard | 4 m |
| R06 | receiving court | 4.5 m |
| R07 | rescue service street | 4.5 m |
| R08 | service vestibule | 4 m |
| R09 | clean promenade | 4.5 m |
| R10 | spawn garden walk | 4.5 m |
| R11 | medical approach | 4.5 m |
| R12 | compliance airlock | 4 m |
| R13 | clean vestibule | 4 m |
| R14 | junction gallery | 4 m |
| R15 | cooling garden route | 4 m |
| R16 | cooling vestibule | 6 m |
| R17 | power service court | 4 m |
| R18 | waste service gallery | 4.5 m |
| R20 | refinery personnel walk | 4 m |
| R21 | maintenance crossover | 4 m |
| R22 | rescue courtyard diagonal | 4 m |

## Verification
- All 21 horizontal route assets built; all existing room sources untouched.
- 1,804 added object bounds checked against full route strips at player height: zero obstacle candidates.
- 10 Cycles scene views plus 21 independent cold-process first-person geometry views reviewed.
- Roof overlap artifacts and invalid review cameras repaired from R02 to R03.
- R12 actual downward ray samples: -0.020m network floor to -0.005m courtyard floor, a 15mm transition; review accepts this for architectural scope.
- R20 turning lane passes the same full-width obstruction audit.
- Saved A07 master and walkthrough; A06 preserved. A live integration command lost its transport response while Blender was busy; fresh readback confirmed the complete saved A07 file, both collections and clean state. No duplicate application.
- New network is one 141,635-face display mesh; 2,780 original authoring objects retained. Latest static 40-frame redraw: 54.01 FPS at promenade view. Not a game FPS guarantee or comparable-camera regression test.
- Shift+F safe walk and gravity disabled remain active. Installed display toggle handles new network/originals; launcher selects newest A07.

## Files
- blender/facility_master_A07_horizontal_network.blend — linked render/authoring master.
- blender/facility_walkthrough_A07_horizontal_network.blend — optimized open walkthrough.
- connections/network/network-R03.blend — independent connector geometry.
- connections/network/network-viewport-R03.blend — disposable display batch.
- connections/network/gallery.html — actual renders, route-by-route geometry views, and separate concept target.
- production/LAYOUT_A07.json — current route status.

## Still separate work
Step 2: actual R19 stairs/lift and source door/threshold integration. Airlock leaves are modeled in open/retracted state; engine interlocks and animation are not bound. Step 3: controller collision/navmesh and cart/route playtests. Step 4: final materials, lighting and art polish. Do not report whole-map gameplay completion from this construction acceptance.
