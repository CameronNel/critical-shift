# Turbine conversion train — implementation design

**Status: design only, 2026-09-08.** Prepared against current `../interface.json` revision A. The style-validation gate is still pending; this document does not authorize a full-hall build or claim machine geometry exists. All equipment sizes, construction details, service points, and named subsystems below are implementation decisions, not additional game-spec facts. No existing geometry is imported. The user requested wind-down while this document was in progress; it is saved as a bounded continuation reference.

## Primary construction

Use one restrained horizontal train: a narrow high-pressure (HP) casing grows into a broader low-pressure (LP) exhaust casing, followed by one guarded coupling and a distinct ribbed generator. The shared shaft is exactly `x=4.6`, `z=2.0`, parallel to `+Y`. The common foundation remains `x 2.5..6.7`, `y 5.5..20`, top at most `z=.45`. Keep all brackets, flanges and bolt heads within the foundation's lateral envelope unless an explicit service access projection has been checked.

| Assembly | Chosen local extent | Shape and construction |
|---|---|---|
| Front thrust/journal bearing | `y 5.60..5.94`, shaft centre `z2` | Compact split bearing housing on a tall, tapered pedestal connected to the base; oil inspection face toward west apron. |
| HP admission end | `y 6.00..6.30` | Stepped cast end shoulder, gland collar and one credible steam chest; no flat cylinder cap with decorative controls. |
| HP working casing | `y 6.30..8.35`, nominal radius .80 m | Horizontal split at `z2`; upper crown flatter than a perfect tube, lower half with cast feet. Two axial shell pieces, distinct end shoulders. |
| HP–LP transfer shoulder | `y 8.35..8.90` | Short expanding transition, not a third unrelated tank. Steam flow continues internally along the shaft. |
| LP expansion casing | `y 8.90..10.55`, nominal radius 1.35 m | Broad cast shell with horizontal split flange and shallow stiffening webs. |
| LP exhaust casing | `y 10.55..12.35`, nominal radius 1.50 m | Fuller lower exhaust hood and narrower raised crown; leave width for flanges. |
| Rear gland/end shoulder | `y 12.35..12.60` | Tapered end face and shaft seal collar; separate from the rear bearing. |
| Turbine rear bearing | `y 12.65..12.97` | Split cap on supported pedestal, slightly offset oil feed on west side; no unsupported bearing suspended on the shaft. |
| Coupling | `y 13.00..14.00` | Shaft coupling inside a low, two-piece perforated sheet guard; guard sides and top are distinct meshes. |
| Generator front bearing | `y 14.08..14.36` | Supported bearing in the shaft gap; guard and pedestal must not intersect. |
| Generator | `y 14.40..18.70` | Barrel with flattened foot line and broad cast end bells; nominal body radius 1.15 m; shallow axial cooling ribs and a purposeful end ventilation ring. |
| Generator rear support | `y 18.78..19.30` | Rear bearing/end support and a compact terminal/service region before the base ends at `y20`. |

A .22 m nominal visible shaft diameter gives readable scale without making it another hero pipe. LP radius 1.50 m gives top `z3.50`; flange/web additions must stay below the architecture limit `z3.80` and within `x2.5..6.7`. Do not increase every segment to the maximum envelope. The dimensional hierarchy should remain visible in silhouette from the entry.

Model split flanges as cast horizontal shelves with a restrained sequence of real through-bolt/nut pairs, especially on the visible west edge. Axial joints use a few broad bands, not identical rings every .3 m. Add lifting eyes only where a detachable part has an identifiable joint and support. Cast feet meet steel soleplates; soleplates meet grout pads; grout meets foundation. Slightly differing foot spacing and end-bell shapes distinguish turbine from generator. Two or three inspection covers are sufficient. Fasteners, seams and localized paint wear follow those construction decisions.

Use muted teal painted cast metal for the turbine, a darker desaturated generator body, grey soleplates and pedestal structure, matte dark rubber at flexible connections, and restrained bare metal on the shaft. Yellow belongs on the removable guard and useful hazard edges. Keep broad shell surfaces quiet. No internal rotor blade arrays are needed for this external environment stage.

## Process and utility routing

**Steam admission:** preserve U01 `(8.4,0,4.9)` and the agreed overhead route to `(8.4,7.2,4.9)`, then `(4.6,7.2,4.9)`. A short vertical drop terminates on the HP steam chest above the working casing. Use one inlet isolation body and one throttle actuator beside the chest, supported by the machine rather than hanging from a pipe bend. Pipe support brackets belong on credible structure. The branch crosses the east aisle overhead, so fittings/insulation/supports must keep underside above `z2.7`.

The HP inlet crosses the conceptual upper lift reservation. Make the last drop and short final branch visibly removable with two flanged joints. Upper-casing removal therefore requires isolated, cooled, disconnected inlet parts and removal of that branch first. Do not claim the complete casing can lift through an unchanged inlet pipe.

**Condensate:** preserve U02 `(9.5,0,.45)` and the wall-side line `x9.5`, `y0..12.6`. A small low-point drain collector under the LP end can reach this line through a covered trench across the east aisle at approximately `y12.2`. The cover must be flush at `z0`, with the crossing pipe below the walking surface; the exact below-floor envelope is unresolved. Bring the branch up again in the wall-side strip, keeping the existing .1 m design margin to the marked aisle. Do not run a raised hose across the aisle or the main route.

**Process dependency:** U02 is a liquid-return interface; it is not a complete main LP steam-exhaust or condenser design. A drain collector does not itself perform phase change. For a believable complete process later, provide a separately agreed exhaust-to-condenser service handoff from the lower LP exhaust hood, or explicitly document a gameplay abstraction of that loop. A provisional `IF_STEAM_EXHAUST_TO_CONDENSER` marker may identify this unresolved dependency, but its position, route, destination and reciprocal interface are not settled and it must not be presented as an existing bound utility. No cooling-plant pump room or hidden working condenser has been added here.

**Electrical output:** place one generator terminal box high on the rear half, facing east within the foundation envelope. Its supported riser reaches the agreed bus origin `(4.6,18.7,4.6)`, then `(8.4,18.7,4.6)` and U03 `(8.4,24,4.6)`. Use bolted rectangular trunk sections, a visible flexible terminal connection, and a few access covers. Keep the riser at the north end so generator side panels remain accessible. U03 remains unbound; the electrical-room input is at its own local `(-4.4,0,3.9)`, requiring connector reconciliation.

No pressures, temperatures, speeds, megawatt ratings, cooling capacities, real trip thresholds, or electrical clearances are established by these visual design decisions.

## Controls, reach and runtime markers

The open control station faces east in the west bay. Keep its front surface around `x−2.82`, leaving the specified apron to `x−1.5`. A nominal standing operator position is `x−2.20`, facing `−X`, about .62 m from that surface. Main hand controls sit at `z1.00..1.15`; speed/load/output gauges sit at `z1.30..1.55`, tilted toward the operator. These are proposed authoring heights, not verified rig reach. Use readable 0.14–0.20 m gauge faces, physical pointers and distinct engraved scale shapes; color alone cannot encode state.

| Marker / component | Proposed point or parent | Function |
|---|---|---|
| `INTERACT_TURBINE_THROTTLE` | `(-2.82,9.25,1.08)` | Bounded lever travel; requests steam admission. Separate lever mesh and pivot. |
| `INTERACT_TURBINE_LOAD` | `(-2.82,10.20,1.08)` | Detented load request control; electrical system resolves delivered output and demand matching. |
| `READ_TURBINE_OUTPUT` | `(-2.82,10.25,1.45)` | Adjacent speed, load, output and demand readouts; use a small coherent bank, not a wall of screens. |
| `INTERACT_OVERSPEED_TRIP` | `(-2.82,11.25,1.10)` | Guarded trip with a clearly separate latched reset action; no automatic restart after fault clearance. |
| `INTERACT_BEARING_OIL_SERVICE` | Interface point `(2.15,12.9,1.0)` | Reach target at west apron for a compact supported service face; feed/return lines continue to the actual bearing housings. |
| `INTERACT_TURBINE_REPAIR` | Bench front near `(-2.62,21.2,1.02)` | Component repair target; final Z follows actual bench height. |
| `ANIM_TURBINE_SHAFT` | Axis `(4.6,*,2.0)` | Local visible rotation driven from host-owned machine state; avoid exposing an unguarded animated hazard without gameplay rules. |
| `ANIM_COUPLING_GUARD` | Coupling shell parent | Separate lift-off halves, not a hinged door sweeping through a worker. |
| `FAULT_BEARING_OIL` | Turbine rear bearing | Local gauge change, sound and restrained leak cue tied to a known fault. |
| `FAULT_STEAM_LEAK` | HP inlet flange parent | Warning source follows the actual joint; incident state is engine-owned. |
| `AUDIO_TRAIN_RUNNING` | Train centreline near `(4.6,11.5,2)` | Idle/start/running/stressed/trip/repair states; rising pitch communicates speed stress. |
| `IF_STEAM_IN_REACTOR`, `IF_CONDENSATE_RETURN`, `IF_POWER_OUT_ELECTRICAL` | Existing interface points | Preserve IDs and coordinates; bound connections remain pending. |

These marker coordinates are proposed choices, not a report that a mesh or marker exists. Preserve interface marker IDs when implementing. Clients request throttle/load/trip/service actions; the host validates reach, state, ownership and cooldowns, and owns machine state, incidents and downstream output. A trip request can close admission and disconnect output through the electrical contract; the client cannot declare a repaired or restarted machine.

## Access and disassembly within the floorplan

West-side small inspection covers should be lift-off panels. Their supporting feet and fixed hardware stay on the foundation; the operator occupies the `x1.2..2.5` apron. Keep a removable cover below approximately .65 × .90 m so it can be handled without claiming clearance for an entire shell. Generator side service uses the east aisle. Avoid big hinged panels whose open swept volume permanently occupies that 2.2 m aisle.

The casing halves are heavy maintenance pieces. Their first move is vertical within the architecture's `z3.8..5.8` lift reservation, after the inlet branch is removed. Casing piece size, lifting attachments, overhead hardware and actual swept volumes remain untested. A proposed upper shell with transverse width near 3 m does not fit the .8 × 2.2 m cart envelope; keep that work in-room until an appropriate larger removal opening and rigging plan exist. Do not label upper-casing extraction as a passed doorway route.

Only small parts that fit the existing carried/cart envelope travel to the north staging region `x2.5..6.7`, `y20.4..23`, then west into the main route. Keep that staging floor empty during ordinary operation. The 2.4 m rescue route remains continuous. Turn carts at the north/south crossovers: the 2.2 m east aisle does not contain the full Ø2.341 m ideal rotation. The .8 × 2.2 m envelope omits carriers and collision skin.

The maintenance bench remains `x−3.87..−2.62`, `y19.85..22.85`; the 1.42 m apron to the main route is preserved. Store one spare bearing shell, a drain tray and a compact tool roll on the bench rather than filling the aisle with loose equipment. The separate oil stand at `x−3.31..−2.59`, `y18.425..19.075` can hold the consumable/service prop cluster.

## Implementation order after the style gate

1. Author foundation, distinct HP/LP shells, correct axis, bearing pedestals and generator silhouette; validate envelopes before small details.
2. Add split flanges, feet, soleplates, coupling guard, terminal box and inlet branch with visible support contact.
3. Add controls and the three agreed utility interfaces; leave the main exhaust/condenser dependency explicitly unresolved.
4. Add removable cover separation, marker parents, a few purposeful service props and localized wear.
5. Check actual machine, door, support, route, panel and overhead bounds; render the fixed gameplay cameras. Independent art review, final geometry checks and engine validation are still required.

No Blender source was edited and no full-hall build was started by this document task.
