# Electrical Room architecture contract

Revision C — 2026-09-08. Metric design baseline for original Blender authorship. Revision C parks both doorway leaves on the hall side of their walls and records the built main-bus centreline at x=−4.32, z=3.88. The corrected transfer placement and P03's 3.20 m opening remain. This document describes design intent; final scene and engine verification are recorded separately by production.

## Authority and implementation decisions

The current source is `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/GAME_SPEC.md`, chapters 5.3–5.6, 12, 18, 19 and 23, together with current `ART_DIRECTION.md`, `ART_REFERENCE_INDEX.md`, `AUTONOMOUS_SECTION_BUILD_PROTOCOL.md` and `ops/facility-run/briefs/electrical-room.md`. Canon fixes the facility order **Turbine Room → Electrical Room → Waste Storage → Reanimation and Medical** and requires modular geometry, collision, lighting, navigation, markers, incidents, audio and network boundaries. It does not fix this room's dimensions, equipment arrangement, voltages or neighboring transforms.

All dimensions and placements below are explicit implementation decisions. They are gameplay architecture, not a real electrical-installation certification. No adjacent section has been moved or assumed aligned. No existing geometry is imported. The adjacent-room 10–20 second travel target requires whole-facility routing and runtime movement-speed validation; room length alone does not establish it.

## Coordinate system and envelope

Local entry threshold D01 is `(0, 0, 0)`. +Y points into the section; +Z is up; +X is right when entering. Floor datum is z=0 with flush thresholds. Units are metres. No facility-global transform has been accepted.

| Element | Coordinates / dimensions |
| --- | --- |
| Main hall clear envelope | x −5.50…5.50; y 0.00…16.40; z 0.00…4.80; 11.00 × 16.40 m |
| Main exterior envelope | x −5.75…5.75; y −0.25…16.65; 11.50 × 16.90 m |
| External walls | 0.25 m nominal; frames and guards stay outside clear route envelopes |
| Reserve bay nominal envelope | x 5.50…8.30; y 11.00…15.40; ceiling z=3.60; 2.80 × 4.40 m |
| Reserve bay return-wall allowance | Main east partition is x 5.50…5.75 outside P03; clear bay width behind those returns is 2.55 m. The opening band has the full 2.80 m envelope. |
| Reserve bay external envelope | x 5.50…8.55; y 10.75…15.65; 0.25 m perimeter walls |
| Overall exterior extents | x −5.75…8.55 = 14.30 m; y −0.25…16.65 = 16.90 m |

Outer perimeter chain, clockwise from southwest: 11.50 m east; 11.00 m north; 2.80 m east; 4.90 m north; 2.80 m west; 1.00 m north; 11.50 m west; 16.90 m south. This captures the side-bay projection rather than implying a rectangular 14.30 × 16.90 floor.

## Portals and passage

| ID | Threshold centre | Clear opening | Behavior / status |
| --- | --- | --- | --- |
| D01 | (0, 0, 0), outward −Y | 2.40 W × 2.70 H; x −1.20…1.20 | Sliding entry; leaves park parallel to the hall-side south wall, outside the protected route. Provisional turbine connection; reciprocal portal and alignment unbound. |
| D02 | (0, 16.40, 0), outward +Y | 2.40 W × 2.70 H; x −1.20…1.20 | Sliding service exit; leaves park parallel to the hall-side north wall, outside the protected route. Provisional Waste Storage continuation; reciprocal portal and alignment unbound. |
| P03 | (5.50, 13.20, 0), outward +X from hall | 2.40 W along Y × 3.20 H; y 12.00…14.40 | Permanently open reserve-bay portal; no swing or leaf. Header starts at z=3.20 under the 3.60 m bay ceiling. |

D01 and D02 each leave 4.30 m clear-wall runs to the main interior corners. Their two parked leaf X footprints are −2.49…−1.23 and +1.23…+2.49, leaving the protected route x=−1.20…+1.20 clear. Leaves are 0.07 m thick at a nominal 0.30 m near-wall depth; handles and track project up to 0.50 m into the hall. Both doors slide without a swing arc. This hall-side implementation exposes the full leaf construction and requires no external pocket or neighboring pocket alignment. P03 is 1.00 m from each end of the bay's nominal 4.40 m length. D01's local inward direction is +Y; D02's is −Y. Optional 2.80 m scenic vestibule returns extend beyond the main thresholds for render continuation; these are not part of the binding architectural envelope. Any closed privacy screens terminating these stubs are scenery-only and must be omitted when the engine connects neighboring modules.

The uninterrupted main passage is x −1.20…1.20, y 0…16.40: **2.40 m clear**. Do not place carts, open cabinet doors, tools, cable coils or freestanding story props inside it. Reserve access branches east across y 12.00…14.40. Equipment to its south and north remains outside that branch.

The design check envelope for a stretcher/cart is 0.80 W × 2.20 L × 1.60 H. Straight passage leaves 0.80 m each side in the 2.40 m route and 1.10 m height below the 2.70 m portals. A 90-degree rotation of that rectangular envelope requires a 2.341 m bounding width; a 2.40 m square has only 0.059 m total geometric allowance. Treat turning as a runtime swept-volume check, not a proven gameplay maneuver. Reserve-bay rescue access is optional; the primary D01–D02 stretcher route is straight. Two simultaneous carriers, ragdoll sway, collision skin and door animation must be tested in engine.

## Equipment and working space

Dimensions are floor envelopes, inclusive of fixed guards/plinths; service/front direction is the required accessible side. Cabinet opening and animated component envelopes must remain within their assigned working space.

| Equipment | Plan bounds (x; y) | Footprint | Front / working area |
| --- | --- | --- | --- |
| SG — incoming/switchgear/breaker sequence | −5.10…−3.55; 3.20…10.90 | 1.55 × 7.70 | +X; x −3.55…−1.20 gives 2.35 m clear working depth |
| TX — enclosed/fenced transformer niche | 3.05…5.30; 4.70…8.10 | 2.25 × 3.40 | −X; x 1.20…3.05 gives 1.85 m access depth |
| TD — transfer and priority distribution | 4.35…5.30; 9.45…11.15 | 0.95 × 1.70 | −X; x 2.30…4.35 gives 2.05 m working depth |
| RB — reserve battery cabinets | 7.35…8.10; 11.70…14.70 | 0.75 × 3.00 | −X; x 5.75…7.35 gives at least 1.60 m working depth |
| WB — northwest repair bench | −5.25…−3.55; 12.60…15.20 | 1.70 × 2.60 | +X; x −3.55…−1.20 gives 2.35 m working depth |

The initial TD placement obstructed P03's direct approach. Revision B moves TD to y=9.45…11.15 and preserves the full branch x=1.20…7.35, y=12.00…14.40. The 0.85 m longitudinal gap from TD's northern edge to the opening band is not a passage constraint because the branch itself spans 2.40 m along Y. Keep all additional furnishings and cabinet sweeps clear of this branch. Both the main D01–D02 route and reserve branch now have unobstructed design envelopes; final-mesh and runtime checks remain outstanding.

Wall-to-machine gaps are 0.40 m west of SG, 0.20 m west of WB, 0.20 m east of TX/TD and 0.20 m east of RB. These are installation gaps, not passage routes. Keep the protected main route and west repair/work areas legible in actual first-person renders.

## Overhead routing and headroom

Incoming turbine bus enters the south boundary at x=−4.32, z=3.88, runs +Y along the switchgear line, branches east at y=6.40 toward TX and continues north at x=−4.32 toward outgoing distribution. The route shown dashed in the plan records the built centreline; all ducts need physical junctions, corner transitions and visible brackets/supports. The final bus size and supports must preserve z≥3.50 m underneath the route-crossing branch. Main ceiling clear height is 4.80 m; reserve ceiling clear height is 3.60 m; all walking/headroom clearance minima remain 2.70 m.

The essential-supply interface is provisionally on the bay service wall at `(8.30, 14.00, 2.80)`, outward +X. This is a placeholder utility socket, not proof of a neighboring connection. The bus entry/exit and essential inlet have no validated voltage, cable capacity or reciprocal socket yet. Do not fabricate technical ratings from architecture.

## Functional hierarchy and recovery hooks

The worker should visually trace incoming power to the isolator/metering section, grouped switchgear/breakers, transformer branch and outgoing feeders. Distinct device construction matters: deep serviceable switchgear compartments, a transformer behind a readable barrier, tactile transfer controls, reserve cabinets and an equipped repair bench. The room must read as facility distribution rather than a repeated reactor local-breaker prop. Use painted steel, concrete, rubber grips/mats, controlled bare metal, glass gauge faces and restrained paper/fabric dressing. Keep signs brief and functional; practical lighting distinguishes machine fronts, the main route and darker reserve space.

Reserve hooks support the canonical conflict between emergency cooling and OCRU reanimation, which has a large power draw and can deplete reserve or cause a blackout. Recovery affordances include turbine isolation, selective load shedding, restoring backup power, manual transfer, accessible component repair and portable-power connection. They are proposed interaction anchors; the Blender scene does not implement electrical simulation, hazards, networking or medical gameplay.

## Integration boundary and unresolved checks

`../interface.json` is the machine-readable design contract. `floorplan.svg` is the dimensioned companion and reflects the corrected TD/P03 arrangement. All utility bindings and both adjacent-room portals remain provisional until the connector builder resolves actual transforms. Geometry collision, navigation, interaction scripts, save/network authority, audio triggers, incident state, optimization and final lighting belong to the selected game engine. Marker names are a proposed schema until Blender source and engine import validate them.

Required outstanding checks: verify cabinet opening sweeps and sliding-door animation; test actual stretcher/carrier movement; omit scenic vestibule privacy screens for connected runtime use; validate 3.50 m overhead underside, practical-support contact and thresholds against final mesh bounds; confirm all emitted markers match this contract; bind portals/utilities reciprocally; measure full-facility travel time in engine.
