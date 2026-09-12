# Fuel Corridor — P07 connection contracts

Updated 11 September 2026. Authoritative numeric data: interface.json. Independent exact source derivations and source/save hashes: production/critics/astra-interface-recheck.md. P01-contracts-historical.md is superseded history. All dimensions are metres. No neighboring geometry was imported, rebuilt or moved.

Final-pass freshness: Luna independently rechecked current neighboring source on 11 September (`production/critics/final-pass/luna-current-interface-source-check.md`). P07 seam coordinates and reactor payload dimensions remain source-consistent. The current refinery save is now `890460de55c331bba30abc80da3eb71f29d11f9f8ada6bca465cd178b43d71d8`; older spacing050 clearance measurements below are historical, not exact current-save proof. The reactor current saved identity remains `5c62f8f6fbe66322148aec53c9f272d40ca5c6ad13223961465c6bfc86714f52`. No newly assembled passage is claimed.

Floor junction correction: functional plant-header and bypass-turn cells overlap by0.30 ×0.60m. The final-pass physical plant slab is trimmed to an L outline to eliminate coplanar finish faces. Their combined footprint, branch seams, floor elevation and route centerlines are unchanged. Functional audio/network cells may overlap; physical floor finish faces do not at this junction.

Origin F01 is the refinery's outer sill face; +Y enters this connector and +Z is up. Finished floor is Z0. The following equations are separate local mappings, not evidence of shared world placement or collision-free facility assembly.

## Measured existing interfaces

| Interface | Existing threshold XYZ | Existing outer seam XYZ | Outward | Nominal W × H |
|---|---|---|---|---|
| Refinery REACTOR | 7.506663706, −4.084283177, 0 | 8.606663706334526, −4.084283176858165, 0 | +X | 2.60 × 3.00 |
| Reactor FUEL HANDLING | 0, 10.80, 0 | 0, 14.50, 0 | +Y | 5.00 × 5.00 |

Refinery sources: worktrees/refinery-compact/sections/refinery/blender/config.py, architecture.py and layout_expansion.py. Expansion uses S=√1.15, DX=.506663706334526, DY=.434283176858165. Refinery owns its 1.10 m sill. Bollards leave 2.49 m width below Z1.04. Hash-bound spacing050 evidence passes 104 short rays over 2.40 × 2.20 m at Z.18 and above; this does not prove the whole sill, floor-level cart sweep or nominal opening. Newer cobalt source differs from that validated save.

Reactor sources: current worktrees/reactor-valorant/sections/reactor-room/blender/build_scene.py:897–937 and active machinery/palette passes. Reactor owns its 3.70 m stub. Bumpers leave 4.98 m below Z1.35; central light underside is Z4.85. The existing static fuel closure is closed: slabs Y14.39..14.49, leaves Y14.33..14.39, meeting strips reach Y14.253. No opening controller or through-passage proof was found. This section does not change those doors.

## Exact local mating equations

For column vectors: p_neighbor = Rz(angle) × p_corridor + translation. Exact 4×4 matrices are in interface.json. Outward normals oppose at each mapped seam.

| Seam | Corridor XYZ | Rotation Z | Translation in neighbor coordinates |
|---|---|---|---|
| F01 → refinery | 0, 0, 0 | −90° | 8.606663706334526, −4.084283176858165, 0 |
| F02 → reactor | 14.2, 24, 0 | 180° | 14.2, 38.5, 0 |

Existing room poses remain unchanged. Combined collisions, shared placement, retained neighboring closures and engine navigation are unverified.

## Proposed coherent topology

Refinery → F01 → 4.40 m gross freight approach → 6.60 × 6.20 m staging/turn bay → 3.40 × 3.40 m internal sliding gate → 4.40 m gross cross passage → east turn → delivery passage → 5.60 m gross reactor adapter with a 5.00 m nominal opening → F02/reactor stub.

Freight centerline: (0,0) → (0,10) → (14.2,10) → (14.2,24), length 38.20 m. Personnel/service bypass: (0,10) → (0,19.2) → (14.2,19.2), length 23.40 m; it rejoins beyond the freight gate. The completed mine retains its authoritative shallow decline; this proposal adds no mine elevator.

| Reserved branch | Corridor seam XYZ / outward | W × H | Proposed destinations and certainty |
|---|---|---|---|
| S01 PLANT | −5.4, 17.4, 0 / −X | 2.00 × 2.50 | Shared cooling/turbine/electrical header; destination seams unverified |
| S02 CLEAN | 6.6, 21, 0 / +Y | 2.00 × 2.50 | Medical/reanimation/compliance header; destination seams unverified |
| S03 WASTE | 16.4, 16, 0 / +X | 2.40 × 3.00 | Waste transfer; destination seam unverified |

Only connectors and termination doors are authored. Reservations do not claim destination rooms or seamless fit. Plant is one shared header, not three completed connections. Destination adapters remain owner/integration work.

## Local construction decisions

The service-air recess is X[−1.65,−1.20], Y[14.30,15.70], H2.45 m. The eng05/eng06 service board stands on three physical200mm steel spacers to clear the wall's raised rails/gussets. Complete evaluated assembly bounds are X[−1.650000,−1.109500], Y[14.558542,15.507999], Z[.735628,2.325000] m, including wall feet and the handwheel. Its outermost handle projects90.5mm into the gross bypass margin but remains109.5mm outside the dressed2.00m route edge X−1.00. The recess itself is not falsely described as containing the entire projection.

The exact air-branch centerline is (.91,14.80,2.67) → (−1.06,14.80,2.67) → (−1.06,14.80,2.16) → (−1.29,14.80,2.14) m. The last point coincides with the station inlet. The main line and staging header terminate in capped supply reservations; operating pressure/flow and supply integration remain unverified. Main eng05 CPU route/support checks pass; independent eng05 confirms station/wall and feed clearance with real mounting contacts. Final saved-revision proof is still required.

P04 introduced paired enclosed leaf pockets. P05 lengthens them for lining/steelwork clearance: X[6.07,6.78], with Y[6.15,7.80] and Y[12.20,13.85], each 0.71 × 1.65 m, H4.40. Each leaf has an editable rigid carriage with a 1.85 m closed-to-open translation. A leaf extends partly into its fixed jamb channel; the complete enclosure and motion must be checked together. Open pose metadata is not an engine controller.

P05 corrects bulkhead returns around the leaf depth, raises the crossing cable tray above its motor cover and provides an explicit crown service aperture. Eng03's independent checks covered the tray against selected crown/head parts and sampled leaf/static clearance; they were not a complete crown-support audit. Eng08 subsequently exposed an unsupported infill/ledge island and a beam/crossmember overlap. Eng11 resolves the crown fit: the beam occupies X[6.125,6.500], Y[7.800,12.200], Z[4.290,4.400] and its east face meets the existing section crossmember at X6.500. A declared anchor at (6.500,10.000,4.345) has independently measured zero gap and opposing normals. Infill X[6.220,6.480], Y[8.440,12.200], Z[3.980,4.290] meets its underside; the ledge meets the infill. This establishes the modeled contact path, not structural load capacity.

The original C10-derived gate motor is 300 mm long along its axis, with 180 mm end bells and a nominal 200 mm fin envelope. Its terminal box, guarded reducer and supports are separate attachments. The supply cable has a secured two-ear clamp with spacers and side fasteners clear of the cable. Two backing segments leave the retained head-access plate free and occupy Z[3.675,3.770]. Eng12 mount shanks engage this backing by 18 mm without touching the adjacent track bearing. A 450 mm projecting task-light arm places its diffuser ahead of the motor face while the fixture back meets the crown at (6.220,9.030,4.160). These parts stay above the freight aperture. Exact saved evidence and scope are in the independent eng11/eng12 reports; visual acceptance remains a separate gate.

Ceilings: freight H4.40, service H3.00, F01 inlet H3.90, reactor adapter H5.90. P05 raises only the new head enclosures to fit the nominal 3.00/5.00 m door openings, 0.55 m head housings and ceiling steelwork. External seams and nominal apertures are unchanged. All external frame centers move 0.50 m inboard of their seams; their 0.40 m sills therefore remain inside this section. Dedicated foundation shoes support jambs. PLANT/CLEAN have manual sliding heads below H3.00. Runtime opening and storage behavior remain unverified.

New sill upstand target ≤5 mm. A101-plan.svg is the editable dimensioned plan. Portal frame/cap clearances, approach routes, gate motion and support contacts need separate evaluated verification.

## Current payload and handling contract

Original single-cartridge carrier: 1.60 L × .90 W × at most 1.30 H including handle/brakes, parked at (2.65,12.32,0), axis +X. It carries a preloaded sealed cartridge. Loading/conversion machinery is outside connector scope; the carrier does not copy the neighboring cart.

Current reactor replacement payload: body 1.18 L × Ø.310; closures centered ±.605, thickness .035, diameter .340. Complete bare cartridge: 1.245 L × Ø.340. Saddles at ±.43 give .86 m spacing. Source: reactor production/build_machinery_flow.py:32–43; later wall A/F passes preserve size. Receiving, storage and cart use this family. Our straps, latches and lifting eyes are external transport hardware: excluded from bare-core dimensions, included in carrier envelope/collision/support checks.

Reactor's own two-cartridge cart has stored envelope 1.24500078 × .84200048 × 1.13267767 m. Refinery units are .480 long, base retaining diameter .184; newer cobalt locks increase a source box span to .196 without matching completed envelope validation. Refinery deck remains .80 × 1.20 m. Packing, conversion and ownership between those units and reactor cartridges are UNVERIFIED. Envelope compatibility does not establish process interchange.

Conservative transport allowance: 2.20 × .90 m, planar diagonal 2.376973 m; both freight turns reserve Ø3.00 m operating circles. Actual carrier diagonal is 1.835756 m. These are planar allowances, not a wheel-steering/operator simulation. Loaded carriers use freight only. Service bypass is 2.40 m nominal / 2.00 m dressed target. Assumed design stretcher: 2.20 × .75 × 1.10 m; team-carry engine motion is unverified.

## Travel and acceptance limits

GAME_SPEC23: refinery→reactor 15–30 s; adjacent areas 10–20 s; full crossing <60 s. Assumed loaded speed 1.50 m/s gives 25.47 s for this connector. Adding the owned 1.10 m sill and 3.70 m stub gives 43.00 m / 1.50 = 28.67 s, excluding room legs, turns, handling and door delays. End-to-end timing is not runtime verified.

F01/F02 presentation caps are section-owned removable assemblies, distinct from neighboring doors. Internal acceptance must report exact cap exclusions and retained frame/sill/hanger clearances. A corridor-only PASS cannot certify an open end-to-end facility route. Full module, motion, cold-render and engine handoff acceptance remain pending at P07 correction stage.

P06 widens only the northern service leg to3.00m gross (Y18.00..21.00) and shifts its route centerline toY19.20. This gives the inboard clean-header jambs a separate margin beside the2.00m dressed through-route. The west service bypass remains2.40m gross. All external port coordinates and the38.20m freight route remain unchanged. The bypass length becomes23.40m; evaluated clearance and stretcher motion remain required.

P07 responds to evaluated full01 geometry. The inlet enclosure is3.20m gross (X−1.60..1.60) and reactor adapter5.60m gross (X11.40..17.00), reserving wall/frame depth outside the unchanged2.60/5.00m nominal port openings. The service turning bay extends toX−1.50 overY18.00..21.00, outside the unchanged bypass centerline, to clear the nominal2.20×.75m stretcher spin. External port centers/normals/mappings and route lengths remain unchanged. Main eng04/eng05 evaluated route, floor, turn and support checks pass. Independent eng05 nominal apertures and seam scans also pass; new detail conflicts remain under correction, so this is not final section acceptance.
