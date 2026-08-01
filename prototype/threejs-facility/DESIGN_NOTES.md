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

About 256 m east–west by 206 m north–south including the mine and the
compliance road; the built plant itself is roughly 150 m across. Walking at
4.2 m/s:

| Leg | Distance | Walk |
|---|---|---|
| Crusher to refinery | 39 m | ~9 s |
| Refinery to reactor | 58 m | ~14 s |
| Mine face to refinery | ~115 m | ~27 s |
| Arrival to control (full crossing) | ~170 m | ~40 s (23 s sprinting) |

That matches the travel targets in `GAME_SPEC.md` §23.2.

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
under the plant starts inside the busiest machine on it.

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
- No lighting design. One ambient level, one key, one fill.
- The mine, the compliance road and the yard are more generous than the
  blueprint's proportions; the built plant matches it closely.

## Asking for changes

Every entity has a stable id of the form `zone.name`, shown in the Edit panel
when you select something. That id is the most useful thing to quote:

> "`yard.diag.floor` is too narrow — make it 12 m."
> "Move `control.deck` to the north side of the reactor instead of the east."
> "`haulage.loop` should be an oval twice this long."

Exporting the JSON from the menu gives the whole document with those ids in it.
