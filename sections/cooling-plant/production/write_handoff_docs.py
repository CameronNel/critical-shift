"""Maintain the section-local handoff with current numeric contract and provenance."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'interface.json').read_text())
def write(p,s):(R/p).write_text(s.strip()+'\n',encoding='utf-8')
# Active/final status documents are maintained separately; never overwrite them here.
write('architecture/README.md','''# Cooling Plant architecture — CP-A03

The architectural plan and interface.json define a section-local room in metres. Entry is (0,0,0), +Y inward, +Z up. Footprint11×13m; ceiling plane5.8m; roof girders descend to5.385m. Wall thickness0.3m. The 5×5m CP-P01 entry is fixed open with flush threshold. There is one internal personnel door, CP-D02,1.2×2.2m, at(-4.1,9.9,0). Its full1.22m leaf opens90° about(-4.74,10.145), endingY11.365 before the bench standing stripY11.4. No raised platform is needed.

P-01 and P-02 occupy west skids, each reserved3.05×2.10m. Their shaft axes runX, motors toward the central aisle. Front operator lane1.4m, shared between-pump lane1.3m, rear pump/workshop approach1.3m. Central cart/rescue lane2.2m wide, headroom reservation2.4m. Actual saved-geometry and swept-route evidence is in production/technical; plan arithmetic alone is not a physics test.

HX-01 is east, axisY, body/instrument envelopeX2.3..4.6,Y4.49..9.3. The side reach strip is1.2m wide. Rear extraction volumeX2..4.6,Y9.3..12.8,Z0..3 is2.6×3.5m, reserved empty. The nominal3.35m game-scale removable cartridge fits3.5m travel. The dedicated overhead hoist alone may occupy its own working zoneZ3.1..5.35. Ordinary circulation must not place storage in this box. Secondary wall crossings are raised toZ3.0 and3.3 so rear maintenance access remains walkable; these are local design choices, not externally agreed sockets.

Rear-west workshop has a2.8×0.7m bench with topZ0.936,0.9m standing strip, open door and a parked service cart outside the doorway. A vise, spanner, rag, removed seal, spare seal, thermos, clipboard and hung tools supply a specific repair story without filling circulation space.

Primary return enters west front, feeds the two pumps, joins the pumped header, crosses overhead atY2.5 with underside4.08m, feeds HX-01 and returns as cooled supply along east front. Secondary water remains a separate circuit. Reserve-power feeder, portable battery socket, capped backup-water inlet and drain collector have named local interface markers. The backup-water branch joins the secondary circuit. No remote pipes, reserve pool or engine simulation is invented.

The correct proposed reactor transform is translation(11.0162950904,-11.0162950904,0), rotationZ=-135°. Reactor owns the3.7m connector between its hall threshold and this seam. Saved-scene measurements confirm the floor's local boundsX±2.5,Y0..3.70000005,Z-.32..0 and closed doorY3.58999991..3.69000006,Z0..5. Neither scene has been globally moved. The static reactor door and facility-wide placement remain integration work.

Sources: original ops/facility-run/BUILD_BRIEF.md and briefs/cooling-plant.md; canonical reactor-valorant/design/GAME_SPEC.md, ART_DIRECTION.md, ART_REFERENCE_INDEX.md and AUTONOMOUS_SECTION_BUILD_PROTOCOL.md; current reactor source and saved scene; refinery source/saved scene; Fuel Corridor interface.json P07, CONNECTION_CONTRACTS.md and saved scene. Current user instructions override the old slice-first, Astra-reviewer and fixed-cycle requirements. Luna reviews full-room integration readiness. Latest user palette explicitly forbids teal.

floorplan.svg is the original dimensioned vector artifact; floorplan.png is its inspected preview. build_plan.py validates contract arithmetic. CONNECTIONS.md records exact topology and ownership. No whole-map or runtime acceptance is claimed.
''')
rows=[]
for s in d['utilities']['sockets']:
    rows.append('| '+s['id']+' | '+str(s['position'])+' | '+str(s['normal'])+' | '+str(s.get('nominal_bore',s.get('cable_diameter','—')))+' |')
write('architecture/CONNECTIONS.md','''# Measured connection contract and topology

All values are metres, Z up. The scene contains empties with the exact CP identifiers in interface.json. Local coordinate origin and transform are unapplied authoring coordinates, not an assembled-map claim.

| Connection | Threshold/position | Normal into destination | Opening | Ownership/status |
|---|---|---|---|---|
| CP-P01 | Cooling(0,0,0) | Cooling+Y |5.0×5.0| Cooling ownsY≥0; reactor owns its existing stubY0..3.7 in reactor portal coordinates |
| Reactor cooling hall portal | Reactor(8.4,-8.4,0) |(.707106781,-.707106781,0)|5.0×5.0 nominal| Reactor-owned |
| Reactor stub outer seam | Reactor(11.0162950904,-11.0162950904,0)|same|5.0×5.0 nominal| Proposed mating seam; saved static doors prevent traversal |
| CP-D02 | Cooling(-4.1,9.9,0)|+Y|1.2×2.2| Cooling internal workshop |
| Fuel F01_REFINERY | Corridor(0,0,0)|outward(0,-1,0)|2.6×3.0| Mates refinery outer sill(8.6066637063,-4.0842831769,0), outward+X; refinery owns1.1m sill |
| Fuel F02_REACTOR | Corridor(14.2,24,0)|outward+Y|5.0×5.0| Mates reactor fuel outer seam(0,14.5,0); reactor owns3.7m stub from(0,10.8,0), static doors remain |
| Fuel S01_PLANT | Corridor(-5.4,17.4,0)|outward-X|2.0×2.5| Reserved shared plant header, no installed Cooling destination |

Proposed coherent topology: refinery dispatch → Fuel Corridor freight route → reactor fuel stub → reactor hall → existing southeast cooling stub → CP-P01 → Cooling central route. CP-D02 branches to the maintenance alcove. A separate future link from S01_PLANT requires a connector-owner decision and assembled footprint checks; this section adds no speculative door or duplicate corridor for it.

Cooling-to-reactor transform: Rz(-135°), t=(11.0162950904,-11.0162950904,0). Map points as p_reactor=R*p_cooling+t. The two5m threshold endpoints become(12.7840620434,-9.2485281374,0) and(9.2485281374,-12.7840620434,0). Finished floors areZ0 with zero step. Reactor link floor's saved local bounds areX[-2.5,2.5],Y[0,3.7000000477],Z[-.319999993,0]. Its closed distant doors occupyY[3.589999914,3.690000057], full5m width/height. Source and saved object measurements agree; the nominal seam rounds their float precision to3.7m. The Cooling footprint lies beyond the stub and does not claim its walls/floor.

Fuel's two published local mating transforms are independent contracts, not a solved global assembly: corridor→refinery Rz(-90°),t=(8.6066637063,-4.0842831769,0); corridor→reactor Rz(180°),t=(14.2,38.5,0). Fuel's freight centerline length is38.2m and its bypass23.4m. Refinery's bollards reduce low-level lateral width to about2.49m; inherited short clearance rays do not prove whole-cart transit. Final assembly must reconcile these transforms rather than force another worker's room to move.

## Local utility sockets

| Identifier | XYZ | Outward normal | Bore/cable diameter |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

All remote utility endpoints remain unassigned. Local pipe endpoints, water recovery branch, feeder and buried drainage collector exist in the saved scene. Portable battery and backup-water couplings are capped/presentation-ready; functional hose insertion, valve actuation, shared reserve competition, cooling failures and repairs are later engine integration work. No duplicate power reserve is created here.

Read-only survey: production/technical/neighbour-saved-measurements.json records neighbour file hashes before/after, world/object-local bounds, rotations and names. All three files were unchanged by the survey. Current data must be rechecked if neighbouring owners revise their artifacts. Current whole-map turbine fit and shared plant-header destinations are unresolved.
''')
write('production/REQUIREMENTS.md','''# Required equipment and scope traceability

| Requirement | Authority | Authored implementation | Verification scope |
|---|---|---|---|
| Pump/exchanger/valve maintenance room | Cooling assignment | Two original centrifugal pumps P-01/P-02, HX-01, isolators, service workshop | Saved geometry, rendered pixels, route checks |
| Traceable coolant supply/return | Assignment; GAME_SPEC cooling | West return → pump branches → hot header/crossfeed → HX → east supply | Local endpoint and pipe network checks; remote circuit unassembled |
| Pump health, pressure, flow, temperature readability | GAME_SPEC12,18 | Pump gauges, local FLOW/TEMP/PRESSURE/PUMP control panel, machine IDs | Visual/semantic handoff; simulated values not implemented |
| Cooling failure/repair/manual valve hold | GAME_SPEC2.3,12,18 | Accessible couplings/casings, isolators, repair bench, tools, manual wheels | Authored maintenance access; engine interactions deferred |
| Reserve restart and competing reserve usage | GAME_SPEC5.5,18–19 | Reserve isolator cabinet and feeder/socket | Local artifact only; shared authoritative pool remains engine responsibility |
| Portable mine battery and backup mine-water recovery | GAME_SPEC19 | Named capped battery and water connections; water branch connects secondary circuit | Local connections measured; no remote hose implied |
| Worker/cart/rescue circulation | Assignment, facility topology |2.2m center route,1.4/1.3m pump lanes,1.2m HX reach strip, workshop door | Evaluated volumes and sampled swept boxes; no engine physics claim |
| Reactor SE interface | Cooling brief and actual reactor |5×5m CP-P01; corrected outer-stub mating transform | Read-only saved-neighbour survey; closed reactor door unresolved |
| Drainage, supports and exchanger access | Assignment | Flush recessed grates/collector; saddles/bolts;3.5m pullout bay and hoist | Actual geometry/contacts and supplementary views |
| Original game art | Art specification + latest user | Ivory/charcoal/oxide-orange/yellow Valorant direction; no teal or imported mesh | Luna pixel review; built-in imagegen guidance |

Design choices, not explicit canonical dimensions:11×13m footprint;5.8m ceiling plane; two redundant18kW-labelled fictional pumps;3.85m exchanger shell, nominal3.35m cartridge; workshop dimensions; all utility bore sizes and local socket coordinates; wall palette, hoist, maintenance props. The brief explicitly fixes the reactor entry at5×5m; the existing3.7m stub is measured ownership evidence. The room includes no raised platform because floor-level service suffices.

Door/opening count: one external personnel/freight opening CP-P01, one internal personnel opening CP-D02, one glazed side aperture into workshop, eight named utility sockets (not pedestrian doors). All routes return to CP-P01; no invented turbine or refinery door. Unresolved neighbouring interfaces are recorded in architecture/CONNECTIONS.md.

Ten primary fixed cameras C01–C10 cover room/machinery/workshop. Eight supplementary W01–W08 views cover approaches, reserve/water, turns, workshop, withdrawal and rear utility service. The repeated saved-scene route audit uses player eye1.68m, body1.85m and conservative box footprints; it does not stand in for game-engine walkability.
''')
concepts=[('R01-overall','exec-0be9f683-7a64-4420-aa98-5392e4f8e6b5','Rejected: Luna layout88; later user rejected photoreal drift and teal.'),('R02-layout','exec-ef4847f1-1aad-4f1a-8bde-182ed2e2c4c1','Superseded unscored: photoreal/teal; dimension labels are guidance only.'),('R03-valorant-overall','exec-3ff40c3c-d13b-4e42-a804-93cd474c8566','Luna style approval, later user explicitly rejected teal; branding excluded.'),('R04-components','exec-d6668fbe-f893-4e97-9c37-492ad724fde3','Superseded unscored teal sheet; regenerated asR06.'),('R05-oxide-overall','exec-c5074485-4fb9-45eb-8d8b-f6c32d6c08c9','Approved Luna: art94,materials92,lighting92,layout91,construction93.'),('R06-oxide-components','exec-e2ffad49-f278-4c37-980b-00fd48673dea','Panels1–5 approved94/94/93/92/91. Reverse panel6 rejected88 for outdoor context; replacedR07.'),('R07-oxide-reverse','exec-bb98daf6-0cc1-4fb8-b712-070732eeb513','Approved Luna: art94,materials92,lighting93,composition94,layout91,construction92. Neighbour imagery is composition only.')]
lines=['# Concept provenance and rejection history','','All images were generated with the built-in ChatGPT image generation tool in this task on11September2026. Original generated files remain in C:/Users/Camer/.codex/generated_images/01a07deb-e7a7-7ee1-b3c6-03e0ad16ca0c/. Section PNGs are exact copies, not Blender render evidence. No generated image is used as an external scene texture or imported geometry.','', '| Concept | Original filename | SHA256 | Decision |','|---|---|---|---|']
for stem,src,state in concepts:
    p=R/'art/concepts'/f'{stem}.png';lines.append(f'|{stem}|{src}.png|{hashlib.sha256(p.read_bytes()).hexdigest()}|{state}|')
lines+=['','Prompt progression: R01 used directly inspected approved reactor hall and mine sump references for industrial style, specifying11×13×5.8m, two west pumps, east exchanger,2.2m central route, rear workshop and3.5m extraction. R02 requested a roofless dimensioned cutaway and complementary rear view. R03 explicitly requested unmistakable clean Valorant screenshot-like rendering, broad matte gradients and purposeful mechanical forms, excluding photoreal/grunge. R04 requested separate machinery/hoist/cabinet/prop/reverse panels. R05 explicitly removed all teal/cyan/blue-green and branding, replacing them with ivory/charcoal/oxide-orange/yellow. R06 applied that palette to the five machine/prop concepts; its outdoor reverse panel was rejected. R07 specifically regenerated an enclosed-interior reverse approach with no sky/yard/trees. Exact generation requests are retained in this task tool history; this document is their concise provenance summary.','','The approved subset is R05 overall, R06 panels1–5 and R07 reverse composition. Their numerical annotations and depicted neighbouring connector never overrule the dimensioned plan or measured ownership. User palette correction supersedes all earlier teal references. Reviewer-authored reports are in production/critics/luna-concept-*.md.']
write('art/concepts/PROVENANCE.md','\n'.join(lines))
print('HANDOFF_DOCS_WRITTEN')
