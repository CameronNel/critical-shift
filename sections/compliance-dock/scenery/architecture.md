# Compliance Dock architecture — P01

This is the authored dimensional plan and section interface contract dated 8 September 2026. It describes intended geometry, operation and runtime handoff. It does not certify the Blender scene, collision, navigation, physics, visibility, travel time, reviewer scores or acceptance.

The drawing is [CD–A01, floorplan.svg](floorplan.svg), also supplied as [floorplan.png](floorplan.png). The canonical machine-readable contract for this package is [../interface.json](../interface.json). [build_architecture.py](build_architecture.py) reproduces the SVG, JSON and, when `resvg_py` is available, PNG. The A2 SVG has a physical size of 594 × 420 mm and its plan is 1:50 when printed at 100%; the comparative elevation is diagrammatic. The scale bar remains usable after resizing. All linear dimensions are metres.

## Authority and implementation decisions

The design follows the canonical `GAME_SPEC.md` at `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/`, the same checkout's current art direction and production protocol, and the original checkout's `ops/facility-run/BUILD_BRIEF.md` and `briefs/compliance-dock.md`. The dimensions below are explicit section-builder implementation decisions; the game specification does not prescribe these measurements.

The section builder supplied the 13.6 × 15.8 m interior, office, scanner positions, apron depths, door sizes and equipment envelope. During this documentation pass the builder confirmed an opaque support screen at x−2.4, y9.8–14.25, height 2.7, and moved the transaction hatch to the office front wall. The front staff door is authored locked closed. Its dashed open leaf and arc show a possible operating envelope; the rear staff door is the alternate open-state route. These choices supersede the early proposal for an east-facing hatch counter.

The smaller fit-out footprints, evidence cabinet position, eye points, movement allowances and numerical hiding-space tuning are authored candidates for reconciliation with final geometry. In particular, the evidence cabinet is placed at the west end of the north wall to leave room for the drawn north-return approach. No numeric tuning value should be treated as canonical balance or implemented code.

## Datum, shell and clear heights

The local origin `(0,0,0)` is the centre of the clear main facility entry at finished floor. +Y points into the dock, +X is right, and +Z is up. Drawing north means +Y; neither geographical north nor a facility world transform is agreed. All thresholds are specified flush at z0.

The clear inside perimeter is x[−6.8,6.8], y[0,15.8]. The 0.28 m perimeter wall projects outward, giving an exterior plan allowance x[−7.08,7.08], y[−0.28,16.08]. Gross interior floor area is 214.88 m² before internal partitions, machines or circulation deductions. The frontage has 3.40 m clear ceiling and the main dock has 4.40 m. No services may reduce these reserved clear heights without revising this contract.

The office's x[−6.8,−2.4], y[3.6,9.6] coordinates are zoning and partition datums. Its 0.16 m partitions are centred on x−2.4 and y3.6/9.6, while x−6.8 is the perimeter inside face. Net clear office bounds are therefore x[−6.8,−2.48], y[3.68,9.52], approximately 4.32 × 5.84 m (25.23 m²) before fit-out. Clear ceiling is 3.05 m. The front partition projects 0.08 m into the nominal 3.6 m apron zone; the plan does not claim an unobstructed 3.6 m depth across the full frontage.

| Zone | Plan bounds / datum | Purpose |
|---|---|---|
| 01 Release apron | x−6.8…6.8, y0…3.6 | Facility threshold, queue, public check-in and lower cart turn |
| 02 Staff office | x−6.8…−2.4, y3.6…9.6 | Logs, staff support, observation and conditional shortcut |
| 03 Controlled check | x−2.32…6.8, y3.6…10.2 | Person scan, cart inspection gate and cargo scanner |
| 04 Arrival dock | x−2.32…3.4, y10.2…15.8 | Contained north arrival with a central approach |
| 05 Concealed support bay | x−6.8…−2.4, y9.8…15.8 | Tarp trolley and evidence storage behind a screen |
| 06 Equipment nook | x3.4…6.8, y11…15.8 | Parked hand cart and wall utilities |

The support screen is 0.16 m thick about x−2.4, so its solid bounds are x[−2.48,−2.32], y[9.8,14.25], z[0,2.7]. Its north return is an internal 1.55 m opening along y[14.25,15.8]. This is an inspectable storage pocket, not an inaccessible hiding volume. The small gap between office rear partition and the screen start is not a player route.

## Openings and state

| ID | Threshold | Clear opening | Mechanism and state |
|---|---|---|---|
| P1 facility entry | (0,0,0) | 2.40 W × 2.60 H | Sliding along X; facility connector assignment pending |
| P2 external access | (0,15.8,0) | 4.60 W × 3.50 H | Opposed sliding leaves, normally sealed; external transport scene unassigned |
| D1 staff front | (−5.4,3.6,0) | 1.05 W × 2.20 H | West jamb hinge, swings +Y into office; authored locked shut |
| D2 staff rear | (−5.4,9.6,0) | 1.05 W × 2.20 H | West jamb hinge, swings −Y into office; alternate open-state shown |
| G1 cart bypass gate | (1.95,7,0) | 1.80 W, overhead clear to 4.40 | Side pocket, no swing into route; open/retracted for cart traversal |
| Support north return | (−2.4,15.025,0) | 1.55 W along Y × 4.40 H | No door; internal circulation only |

There are exactly two perimeter boundary cuts, P1 and P2. No medical doorway, duct shortcut or other external connection is implied by the staff office or support bay. The hatch is a transaction opening above a sill, not a navigable portal.

D1 and D2 have 1.05 m swing radii about their west jambs x−5.925. Their inward operating areas must be kept free of furniture. Drawing a swing does not assert that the closed authored D1 is currently traversable. The full green R3 route requires unlocking D1 and opening both staff doors. A person entering from the dock can instead go around the screen and use open D2 to reach the office; the locked front door still stops onward travel to the release apron.

G1's candidate pocket x[2.86,3.36], y[6.75,7.25] assumes a compact four-panel telescoping arrangement. Panel construction, stacking and handle collision require detailed reconciliation; the clearance contract is the 1.80 m aperture x[1.05,2.85]. P1/P2 slide tracks and stowed leaves must stay outside their reserved clear opening.

## Equipment and staff working positions

The human scanner is mounted on the (0,7) datum. Its 1.70 m overall width contains a 1.20 m clear opening x[−0.6,0.6] with 2.25 m headroom. The documentation footprint is x[−0.85,0.85], y[6.55,7.45], with a 2.55 m overall-height allowance. It is the R1 bottleneck, and R2 is the route for loaded carts and offline bodies.

The cargo inspection installation uses the specified x[3.4,5.9], y[5.3,10.0], z[0,2.1] envelope, with belt surface z0.8. Its mounting datum is (4.65,7.7); the envelope's geometric y-midpoint is 7.65, so the named datum is intentionally not asserted to be its bounding-box centroid. A full 0.90 m east service strip x[5.9,6.8], y[5.3,10.0] is reserved. Equipment panels or dressing must not consume that strip. Candidate load/unload positions are (4.65,4.5) and (4.65,10.55).

The transaction hatch is centred at (−3.51,3.6), facing the release apron. Its opening spans x[−4.35,−2.67] and counter top is z1.04. The depicted counter footprint x[−4.35,−2.67], y[3.25,3.95] is an allowance to reconcile with final geometry; upper opening height is deliberately unspecified. Public use marker B is (−3.51,2.6,0), facing +Y. The office's east glazing at x−2.4 runs y4.0–8.9 with sill z1.05 and top z2.50, facing +X for observation only. There is no separate east counter.

Candidate support fit-out comprises a tarp trolley x[−6.4,−5.3], y[12,14.5], and evidence storage x[−6.45,−4.7], y[14.8,15.55]. The north cabinet's south access face requires local reach and retrieval checks around the trolley. The staff route approaches the screen return to the east of both objects. The east nook carries a parked 0.75 × 2.10 m hand cart at x[4.05,4.8], y[11.65,13.75] plus wall utilities; neither extends into the central arrival dock.

## Routes, swept envelopes and obstructions

The coloured lines are intended route centrelines. Their vertices are in `reserved_routes` in the JSON; they are not exported navigation meshes. All routes are bidirectional where door state permits, although the inspection progression proceeds from sealed north arrival toward the south facility threshold.

| Route | Spatial reservation | Required state and limitation |
|---|---|---|
| R1 person / officer | x0, y15→0; minimum 1.20 m wide and 2.25 m high at scanner | P1/P2 open for full traversal; scanner operational. A fallen body can block the lane. |
| R2 cart / body | Straight centre x1.95, y3.2–12.2; 1.35 m swept planning width; gate 1.80 m | G1 fully retracted; P1/P2 open. P1 limits headroom to 2.60 m. Turn transitions are provisional. |
| R3 staff shortcut | x−5.4 through office; north approach x−3.5 and y15.025 around screen | D1 must be unlocked, both D1/D2 opened. 1.05 m door clearances and 2.20 m headroom limit this path. Default D1 state blocks it. |

The nominal cart is 0.75 m wide × 2.10 m long. Its 1.35 m straight swept allowance reserves 0.30 m nominal lateral handling space on each side. The drawn body allowance is 0.70 × 1.80 m; limbs, dragging posture and the handler can exceed that footprint. The blue circles, radius 1.50 m at (1,2) and (1.25,12.1), reserve manoeuvring areas. They are **not** a calculated Minkowski sweep of the schematic polyline and cannot be used as proof of a successful turn. Full loaded-cart and body/handler sweeps are still required.

A 0.75 m cart nominally leaves 0.15 m on either side within a 1.05 m staff door when perfectly aligned. That arithmetic does not establish practical trolley access through the shortcut: the leaf, hand clearance, approach angle and turns need checking. Keep the staff lane free; do not treat the green line as proof that every depicted prop can be moved through it.

Two relevant obstruction scenarios are a transverse 2.10 m cart at the 2.40 m P1 entrance and a 1.80 m body across the 1.20 m human scanner. The first can block the sole facility handoff despite small residual side gaps. The second motivates the cart bypass if its gate can be opened. Grabbing, dragging, manual clearing, door recovery and network ownership need actual gameplay tests.

## Inspection, concealment and runtime markers

E at (−3.05,5.3,1.6) is a candidate office observation eye, looking through the east glass toward the person scan, cart gate and north arrival. The orange rays express intended sightlines, not raycast or final mesh results. Glazing frames, fixtures and bodies may occlude them. The 2.7 m opaque support screen should interrupt central-eye views of the low trolley; a searching officer can go around its north end and reveal the contents. Sound remains a discoverable cue.

| Marker | Local position | Intended hook |
|---|---|---|
| A officer arrival | (0,14,0), faces −Y | Arrival spawn; initial routine inspection route |
| B transaction hatch | (−3.51,2.6,0), faces +Y | Headcount, logs, explanation and distraction |
| C worker inspection | (0,8.3,0), faces −Y | Registration, suit and injury check |
| D cargo inspection | (4.65,10.55,0), faces −Y | Waste scan, cargo interest and evidence collection |
| F support search | (−3.55,13.5,0), faces −X | Cover search, cabinet search and body discovery |
| Facility handoff | (0,0,0) | Connector navigation/network boundary; neighbour transform unresolved |

The JSON contains two candidate hiding spaces with every field requested by GAME_SPEC §16.3. H1 is a tarp trolley, capacity one offline/unconscious body and two small items; H2 is a staff evidence cabinet, zero bodies and six small-item slots. Visibility, sound transmission, search probability, escape possibility and environmental risk are recorded. Example search probabilities are explicitly provisional tuning, not claims about an implemented officer. H1 permits an unrestrained occupant to lift the cover, make noise, escape or be accidentally moved with the trolley. H2 hides objects behind an opaque door but retains possible registration/log evidence and must be accessible for formal audit and confiscation. It is not a radiation shield.

Runtime handoff also declares audit, scanner fault, destroyed sensor, restricted door, body discovery, contraband, falsified log, evidence collection, disabled officer and lockdown hooks; provisional dock/office/support audio zones; spawn/interest targets; and a network relevance allowance. Evidence entities need the canonical `EvidenceState` fields including owner, related event, visibility, hidden and discovered. These are authored data requirements, not working engine systems.

## Medical adjacency and facility connection

The read-only adjacent source is `C:/Users/Camer/.codex/worktrees/1edf/critical-shift/sections/medical-reanimation/scenery/interface.json`, revision P01. It defines its own local origin at a 2.20 × 2.50 m sliding main entry. This dock's P1 is 2.40 × 2.60 m. The facility connector must transition to the smaller medical aperture, and its route bottleneck cannot be represented as the dock's larger size.

GAME_SPEC §23.1 places Reanimation and Medical before Compliance Dock in the facility sequence. This supports an adjacency contract, not direct world placement. Relative transform, connector identity, length, topology, geography and final adjacent geometry are all unconfirmed (`null` or `false` in JSON). Do not move either module to make these local origins coincide. No old medical geometry was imported or changed. The 10–20 second adjacent-area target from §23.2 remains for connector/runtime testing rather than inferred from room dimensions.

## GAME_SPEC traceability

| Canonical requirement | Architectural response | Remaining runtime work |
|---|---|---|
| §14.1–14.3 compliance escalation; officer arrives, scans, follows routes and opens selected access points | Sealed arrival, person/cargo inspection, transaction hatch, staff doors and cabinet | Inspection state progression, door authority and escalation |
| §14.4–14.6 distraction, concealment, evidence and AI interest targets | Public transaction position, visible machinery, covered trolley and named search markers | Distraction evaluation, search behaviour, memory and navigation recovery |
| §16.1–16.2 offline/unconscious bodies and evidence | Body-sized movement allowance and non-graphic tarp storage | Identity, injury, registration and attached-evidence handling |
| §16.3 hiding capacity, visibility, sound, search, escape and risk | H1/H2 complete candidate records in JSON | Balance, discoverability, interactions and audio tuning |
| §16.4–16.5 wake-up and context-dependent discovery | Escape space and hooks around covered trolley; searchable storage | Wake/noise timing and officer interpretation |
| §23.1–23.3 facility sequence, 10–20 s adjacent travel and shortcuts | Medical connector contract and conditional staff route | Final topology, travel time and door-state pathfinding |
| §23.4 modular collision, navigation, spawns, incidents, audio, network and metadata | Local datums, portals, markers, zones and pending-check list | Engine implementation and integration |
| §30.5 EvidenceState; §31.2 officer state machine | Hiding/inspection hooks with evidence state-field handoff | Actual state transitions and network synchronisation |

## Outstanding checks

The handoff must compare final object geometry with these dimensions; test leaf/frame, scanner, overhead and service clearances; sweep loaded carts and ragdoll/handler extents through door states and turns; check the north screen return and cabinet access; confirm tarp retrieval/escape and officer marker reachability; test sightline rays, audio propagation, incident state transitions, obstruction recovery and network handoff; and resolve the medical connector transition and travel time. File generation and visual inspection of this drawing do not satisfy those checks. No pass score or acceptance is claimed here.
