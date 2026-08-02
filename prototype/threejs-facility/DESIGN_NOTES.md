# Facility layout — design notes

What the greybox is trying to do, so that a change request can be specific.
The layout follows the compact-facility blueprint
([`docs/facility-blueprint.png`](docs/facility-blueprint.png)). Everything below
is implemented in `src/facility/data/`. Units are metres, +X east, +Z south,
+Y up.

## The shape of it

A **compact loop**, not a line. The reactor hall is a central octagonal volume
with four doors on four different sides; the production row runs along the
north edge; haulage and the mine sit west; storage, medical and cooling south.
Nothing is a dead end, so route choice is tactical rather than obligatory.

```
                    COMPLIANCE  (road and dock, far north)
                         |
  ARRIVAL ─── S1 north spine ─────────────────────────┐
     │      CRUSHER ── REFINERY ── FUEL               │
     │         │           │         │                │
   MINE ─── HAULAGE ═══════╪═════ REACTOR ── CONTROL  │
             (cart loop)   │      (octagon)     │     │
                │          │                    │     │
              STORAGE ── MEDICAL ───────── COOLING ───┘
                ╰──────── maintenance ring (-5 m) ────╯
```

## Three working datums

| Datum | Y | Contains |
|---|---|---|
| Surface | `0` | production row, reactor, control, haulage, storage, medical, compliance, yard |
| Service | `-5` | maintenance ring, crusher pit, cooling hall |
| Mine | `-2` | extraction chambers, inside the rock mass west of the plant |

## Scale and travel

The layout is authored at a comfortable drafting scale and then **compacted in
plan by a single factor** (`SITE_SCALE` in `src/facility/scale.ts`, currently
`0.6`) before it is built. The compaction is not uniform:

- **Scaled:** X and Z positions, wall runs, room footprints, machine
  footprints, distances along a wall to an opening.
- **Not scaled:** every vertical dimension, and every human-scale clearance —
  corridor and catwalk widths, stair widths, door widths, wall thickness, pipe
  radius, ceiling heights.

So the plan tightens without corridors narrowing, doors shrinking below what a
dragged body needs, or the reactor hall losing the height that makes it worth
looking at. A 1.75 m worker stays 1.75 m. Set `SITE_SCALE` to `1` to inspect
the uncompacted drafting scale.

Compacted, the site is about 153 m east–west by 123 m north–south including the
mine and the compliance road; the built plant is roughly 90 m across.

**Stairs are the thing compaction breaks.** Shortening the plan shortens a
stair's run but not its rise, so every flight gets steeper as `SITE_SCALE`
drops. `validateFacility` therefore checks stair slope: it errors past 48°
(no longer a stair by any industrial standard) and warns past 40°. Most flights
in the plant now sit at 33–35°, which is why several of them are far longer
than the room they serve strictly needs, and why the fuel roof and the control
deck are reached by switchbacks rather than single flights.

### Emergency runs

These are what the scale is really for. The meltdown beat is only frightening
if the run to the valves is short enough to attempt.

| Run | Distance | Sprint | Walk | Suited |
|---|---|---|---|---|
| Control desk → coolant valves | 75 m | 10 s | 18 s | 23 s |
| Control desk → reactor scram | 28 m | 4 s | 7 s | 9 s |
| Reactor floor → coolant valves | 52 m | 7 s | 12 s | 16 s |
| Reactor west door → south scram | 21 m | 3 s | 5 s | 7 s |
| Refinery floor → reactor core | 42 m | 6 s | 10 s | 13 s |
| Crusher → reactor | 65 m | 9 s | 15 s | 20 s |
| Mine face → reactor | 111 m | 15 s | 26 s | 35 s |
| Arrival → reactor | 98 m | 13 s | 23 s | 31 s |

**These times depend entirely on a movement speed that nothing in the design
documents fixes yet.** The figures above assume 7.4 m/s sprinting, 4.2 m/s
walking and 3.2 m/s suited. The Movement speed section of the menu switches
between Slow, Default and Fast at runtime, because the honest way to judge the
scale is to run to the coolant valves at each and see which one feels right.

The compacted numbers sit at or just under the travel targets in
`GAME_SPEC.md` §23.2, which were written for a walking pace, not a sprint.

## Two rooms built out in full

Most of the site is greybox: massing, circulation and footprints. **Arrival and
the reactor hall are built to a further level** — every station the design
documents call for physically exists, is placed where it makes spatial sense,
and carries an interaction marker. The rest of the facility is still blockout,
and should be read that way.

### Arrival — the preparation beat

Carries the whole of GAME_SPEC §8.2 and every step of the suit procedure in
§6.2. Three bands north to south:

```
Z -86..-76   shift office  |  locker room  |  suit-up
Z -76..-70   central corridor, decontamination at its east end
Z -70..-58   briefing      |  requisition
```

The suit route runs along the north band — lockers, suit racks, helmet shelf,
integrity test booth, dosimeter rack — and leaves east through decontamination.
The requisition route runs along the south band — tool crib, explosives cage,
spare parts, medical supplies, machine upgrades, repair priorities — and leaves
east onto S1. The two exits belong to different routes, and the three minutes
you have will not cover both. That is the point of the room.

The shift office overlooks the corridor through a window, which is where
informal roles get settled.

### Reactor hall — every control has a place

Laid out so that every control in GAME_SPEC §12.4 has a physical station, and
so that the ones you need at the same moment are deliberately far apart.
Clockwise from the north:

| Octant | Contains |
|---|---|
| N | charge floor, fuel receiving, transfer flask, new fuel rack |
| NE | waste flask, shielded waste store, transfer trolley |
| E | annunciator, log desk, radiation monitor, scram station — under the control windows |
| SE | turbine, generator, condenser, throttle stand, lube skid |
| S | coolant headers, valve stands, flow meter, emergency cooling injection |
| SW | switchgear, breakers, backup generator, reserve power |
| W | main access, muster point, tool point, emergency locker, scram station |
| NW | vent stack, vent valve |

The two coolant headers sit either side of a clear lane at Z 12..15. That lane
is not decoration: it is the only straight run on the working floor long enough
to carry a stair up to the catwalk ring at a pitch you can walk.

Four levels: working floor 0, catwalk ring +8, upper gantry +17, and a charge
deck at +20 carrying the control rod drives and the fuelling machine, sitting
on the core itself. A travelling crane spans the hall at +23.

Getting between them is deliberately slow. The floor reaches the catwalk ring
in two places only — a west flight off the south floor and a north-east flight
off the charge floor — and the ring reaches the gantry by one long flight that
runs the entire east annulus, past the operating face and over the turbine.

Three emergency shutdown stations — west, east and south — because one would
always be on the wrong side of the core.

## Zone by zone

**Reactor hall.** Octagonal, 52 m across, 30 m clear. Core cylinder and
containment frame in the middle, catwalk ring at +8, upper gantry ring at +17
with a clerestory looking north up the compliance approach. Doors west (the
cart diagonal), north (compliance), east (control) and south-east (cooling).
Because it is central, most journeys can go through it or around it.

**Control room.** A raised block east of the reactor at +10, looking in through
the overlook windows in the reactor's east wall. Total visibility, one stair
down and the length of the link corridor to reach anything.

**Crusher.** West end of the production row. Grade is a ring around an open pit
at -5 m, crossed by an unrailed tipping deck carrying the live cart track. The
pit floor *is* the west door of the maintenance ring, so the quietest route
under the plant starts inside the busiest machine on it. The stair into the pit
runs north off the south deck; the operator's stair runs the full length of the
west deck.

**Refinery.** Sorter, processor and dryer on one unbroken belt line along the
north half, circulation south. Four working elevations: floor, mezzanine +5,
centre aisle +10, gantry +14. The clerestory at +14 is one of only three places
that can see the compliance road.

**Fuel.** Assembly, inspection, containment store, staging. Its roof at +10 is
walkable and looks straight down the compliance approach. Its east door opens
directly onto that approach.

**Haulage.** A cart *loop*, not a line — carts run continuously, take the north
spur to the crusher, or the east spur out onto the diagonal. Crossing the floor
on foot is a timing problem.

**Mine.** Driven west into the rock at -2 m, so its rough ceiling rises above
grade and reads as a hillside. Main face, ore-vein branch, dead-end store, and
a 2.8 m service tunnel that climbs back under the plant into the ring.

**Cooling.** Sunk to -5 m south-east of the reactor, below control's line of
sight. The lid is flush with grade and stops short of the north wall, leaving
an open cut: the state of the pumps is public, reaching them is not.

**Maintenance.** A closed ring of 4 m corridors at -5 m with four ways in — the
crusher pit, the storage stairwell, the mine's service tunnel, and the cooling
hall it drains into. 4 m clear so two people pass and a body drags. A loop, not
a maze.

**Compliance.** Road, dock, and one straight corridor south past the fuel block
to the reactor's north door. Deliberately legible.

## Routes

Toggle them in the Layers menu.

| Route | Colour | What it is |
|---|---|---|
| Primary production flow | green | mine → haulage → crusher → refinery → fuel → reactor |
| Main worker access | blue | arrival → S1 → refinery link → the diagonal → reactor |
| Cart line | red | the loop, the crusher spur, and the east spur onto the diagonal |
| S1 north spine | yellow | straight behind crusher, refinery and fuel |
| S2 haulage to storage | yellow | out of the cart hall without crossing the diagonal |
| S3 medical to cooling | yellow | reaches cooling without entering the reactor at all |
| Maintenance ring | violet | the closed loop one level down |
| Compliance approach | pink | road, dock, and the last exposed stretch |

## Deliberate tensions

- **The diagonal.** The cart line's east spur and the main worker route from
  the refinery share one 8 m corridor between haulage and the reactor's west
  door. That crossing is the site's signature hazard, and there is no refuge
  bay on it.
- **The loop never stops.** Because haulage is a loop rather than a siding,
  crossing that floor is always a timing decision.
- **Through the machine to get underneath.** The maintenance ring's west door
  is the crusher pit, so the sneakiest route starts in the loudest room.
- **Control versus cooling.** From the control deck you can see the whole
  reactor floor, and out to the south, the cooling cut. You cannot reach either
  quickly.
- **Elevation versus warning.** The fuel roof deck, the refinery clerestory and
  the reactor's upper gantry all see the compliance approach. Working floors
  see nothing. Whoever is high up is the early-warning system.
- **Belt walking.** Conveyor belts are walkable. From the refinery mezzanine
  you can step onto the sorter belt and ride the line east to fuel without
  touching a stair.
- **Hiding places.** Four, not forty: the mine store drift, the maintenance
  tool store, the storage waste containers and tarp, and the empty fuel crates.

## Known simplifications

- The reactor's floor slab is square under an octagonal shell, so its corners
  poke a little past the diagonal walls at grade.
- Conveyor and pipe runs are indicative, not engineered.
- Rough rock is overlapping slabs, not a sculpted mesh. It reads correctly at
  gameplay distance and is wrong close up.
- No lighting design beyond housings and a handful of real point lights.
- `reactor.stair.floor.w` is 46°, steeper than anything else on the site. The
  south-west octant is full of coolant headers and switchgear and there is
  nowhere to put a longer flight without moving equipment that belongs where
  it is. It reads as an industrial stair rather than a public one.
- Stairs that climb to a level and land inside that level's slab come up
  through it, rather than through a modelled stairwell. The fuel roof deck is
  the exception: it is laid in four pieces around a real hole.
- Guard rails are solid, so anything that meets a railed catwalk from another
  level has to meet it at a gap. Both reactor rings, the refinery centre aisle
  and gantry, and the crusher high link are therefore split into railed runs
  plus short unrailed landings at each stair head. A stair's own rails stop
  1.6 m short of its ends for the same reason.
- Widths and clearances do not shrink with the plan, so a two-metre stair
  parked two metres from a catwalk ends up with its rail in the walkway once
  the plan is compacted. Keep flights clear of walkways by more than half
  their own width.
- The mine, the compliance road and the yard are more generous than the
  blueprint's proportions; the built plant matches it closely.

## Asking for changes

Every entity has a stable id of the form `zone.name`, shown in the Edit panel
when you select something. That id is the most useful thing to quote:

> "`yard.diag.floor` is too narrow — make it 12 m."
> "Move `control.deck` to the north side of the reactor instead of the east."
> "`haulage.loop` should be an oval twice this long."

Exporting the JSON from the menu gives the whole document with those ids in it.
