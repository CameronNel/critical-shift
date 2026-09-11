# Cooling Plant architecture — CP-A03

The architectural plan and interface.json define a section-local room in metres. Entry is (0,0,0), +Y inward, +Z up. Footprint11×13m; ceiling plane5.8m; roof girders descend to5.385m. Wall thickness0.3m. The 5×5m CP-P01 entry is fixed open with flush threshold. There is one internal personnel door, CP-D02,1.2×2.2m, at(-4.1,9.9,0). Its full1.22m leaf opens90° about(-4.74,10.145), endingY11.365 before the bench standing stripY11.4. No raised platform is needed.

P-01 and P-02 occupy west skids, each reserved3.05×2.10m. Their shaft axes runX, motors toward the central aisle. Front operator lane1.4m, shared between-pump lane1.3m, rear pump/workshop approach1.3m. Central cart/rescue lane2.2m wide, headroom reservation2.4m. Actual saved-geometry and swept-route evidence is in production/technical; plan arithmetic alone is not a physics test.

HX-01 is east, axisY, body/instrument envelopeX2.3..4.6,Y4.49..9.3. The side reach strip is1.2m wide. Rear extraction volumeX2..4.6,Y9.3..12.8,Z0..3 is2.6×3.5m, reserved empty. The nominal3.35m game-scale removable cartridge fits3.5m travel. The dedicated overhead hoist alone may occupy its own working zoneZ3.1..5.35. Ordinary circulation must not place storage in this box. Secondary wall crossings are raised toZ3.0 and3.3 so rear maintenance access remains walkable; these are local design choices, not externally agreed sockets.

Rear-west workshop has a2.8×0.7m bench with topZ0.936,0.9m standing strip, open door and a parked service cart outside the doorway. A vise, spanner, rag, removed seal, spare seal, thermos, clipboard and hung tools supply a specific repair story without filling circulation space.

Primary return enters west front, feeds the two pumps, joins the pumped header, crosses overhead atY2.5 with underside4.08m, feeds HX-01 and returns as cooled supply along east front. Secondary water remains a separate circuit. Reserve-power feeder, portable battery socket, capped backup-water inlet and drain collector have named local interface markers. The backup-water branch joins the secondary circuit. No remote pipes, reserve pool or engine simulation is invented.

The correct proposed reactor transform is translation(11.0162950904,-11.0162950904,0), rotationZ=-135°. Reactor owns the3.7m connector between its hall threshold and this seam. Saved-scene measurements confirm the floor's local boundsX±2.5,Y0..3.70000005,Z-.32..0 and closed doorY3.58999991..3.69000006,Z0..5. Neither scene has been globally moved. The static reactor door and facility-wide placement remain integration work.

Sources: original ops/facility-run/BUILD_BRIEF.md and briefs/cooling-plant.md; canonical reactor-valorant/design/GAME_SPEC.md, ART_DIRECTION.md, ART_REFERENCE_INDEX.md and AUTONOMOUS_SECTION_BUILD_PROTOCOL.md; current reactor source and saved scene; refinery source/saved scene; Fuel Corridor interface.json P07, CONNECTION_CONTRACTS.md and saved scene. Current user instructions override the old slice-first, Astra-reviewer and fixed-cycle requirements. Luna reviews full-room integration readiness. Latest user palette explicitly forbids teal.

floorplan.svg is the original dimensioned vector artifact; floorplan.png is its inspected preview. build_plan.py validates contract arithmetic. CONNECTIONS.md records exact topology and ownership. No whole-map or runtime acceptance is claimed.
