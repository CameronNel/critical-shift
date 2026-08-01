# Facility layout — design notes

What the greybox is trying to do, so that a change request can be specific.
Everything below is implemented in `src/facility/data/`. Units are metres,
+X east, +Z south, +Y up.

## Three working datums

| Datum | Y | Contains |
|---|---|---|
| Surface | `0` | arrival, crusher hall deck, refinery, fuel, medical, storage, reactor floor, compliance dock, yard |
| Service | `-6` | crusher pit, maintenance spine, cooling hall |
| Mine | `-12` | extraction chambers, haulage drift |

Three datums instead of one flat site is what makes the plant feel stacked
rather than spread out. The mine sits deep enough that its rough rock ceiling
clears the surface slabs above it.

## Overall footprint

Roughly 268 m east–west by 144 m north–south. Arrival at the far west, the
reactor at the far east, everything else between them. Walking the full
crossing takes about 50 seconds; sprinting, about 28. That matches the travel
targets in `GAME_SPEC.md` §23.2.

```
 W                                                                        E
 ARRIVAL ─ decline ─ CRUSHER ─ REFINERY ─ FUEL ─ corridor ─ REACTOR
    │         │                    │        │                 │
   MINE     (-12)              STORAGE   MEDICAL           COOLING (-6)
                          MAINTENANCE SPINE (-6) ───────────────┘
                     COMPLIANCE road and dock along the north edge
```

## Zone by zone

**Arrival** (X -120..-88). Lockers north, briefing south-west, suit-up and
decon south-east. Two east doors, and which one you take commits you to a
route: north leads to the decline bridge and the short way to the crusher,
south leads the long way round and across the cart track.

**Mine** (-12 m). One main extraction chamber, one branch drift to a secondary
face, one dead-end store drift, and the rise. Rock is built from slabs placed
strictly outside the nominal void, so the space reads as excavated while the
clean nominal box stays the collision surface.

**Haulage**. An open cut from grade at Z +40 down to the mine at Z -20 — 60 m
at a 20% grade, 7.5 m wide. Carts and people share it. Two bridges cross it,
so the yard is permanently split by a hazard. One refuge bay part-way down is
the only place to stand when a loaded cart comes at you.

**Crusher** (X -70..-36, -6 to +20 m). Grade is a ring around an open pit. The
cart track crosses the pit on an unrailed tipping deck — the fastest way across
the hall and the worst place to be standing when a cart arrives. Operator level
at +6 overlooks the pit, the crusher throat and the deck. The crusher body
pokes 10 m above grade, so it is a landmark from the yard.

**Refinery** (X -32..+24, 18 m clear). Sorter, processor and dryer on a
continuous belt line across the north half, circulation south of them. Four
usable elevations: floor 0, mezzanine +5, aisle catwalk +10, gantry +14. The
belt line is unbroken from the crusher to fuel, so a bad batch has a clear path
downstream — which is the point of the room. A clerestory at +14 in the north
wall looks out at the compliance road.

**Fuel** (X 28..58). Assembly, inspection, containment store, staging. Its roof
at +8 is a walkable deck and the cheapest place on the site to spot something
arriving on the compliance road. Its north door opens straight onto that
approach, which cuts both ways.

**Reactor** (X 64..120, 30 m clear). The dominant volume, visible from
everywhere. Core and containment frame in the middle, catwalk ring at +9, upper
gantry ring at +18 with a clerestory looking north over the compliance
approach. Access is asymmetric on purpose: the floor-to-catwalk stair is on the
east side, the control stair is on the west, so nobody is ever near both.

**Control** (+11 m, reactor west wall). An open balcony, not a sealed box — the
sightline over the core is the mechanic. Whole reactor floor visible, two
flights and a long walk to reach any of it.

**Cooling** (-6 m, south of and below control). Pumps, heat exchanger and a
valve gallery. Two ways in: one stair through the reactor south wall, or the
maintenance spine. The lid is flush with grade and stops short of the north
wall, leaving an open cut you can look down into from the yard.

**Maintenance** (-6 m). A 4 m spine from the crusher pit, under the refinery,
past a stairwell that surfaces in the yard, out to cooling. 4 m clear so two
people pass and a body drags without snagging. One spine, one branch, one
dead-end tool store — learnable, not a labyrinth.

**Storage / medical**. Waste containers, a crate stack and a tarp in storage;
reanimation and decontamination in medical, off the production line.

**Compliance**. Road along the north edge, dock, then eighteen open metres to
the reactor north door. The road continues west past the refinery north door,
which is the quieter second way in.

## Routes

Drawn as coloured ribbons; toggle them in the Layers menu.

| Route | Colour | What it is |
|---|---|---|
| Primary production circulation | blue | arrival → bridge → crusher → refinery → fuel → reactor |
| Ore and material flow | amber | mine → decline → crusher → the three refinery stages → fuel → reactor |
| The rise | green | mine face to the crusher pit without touching the decline |
| Maintenance spine | violet | crusher pit to cooling, unseen from any working floor |
| Cart route | red | crosses the south yard walkway, then runs through the crusher hall |
| Compliance approach | pink | road, dock, and the exposed metres to the reactor door |
| South yard walkway | yellow | the long way round the decline, across the cart track |

## Deliberate tensions

- **Cart versus worker.** The track crosses the south walkway in the open yard
  and then runs the length of the crusher hall floor. Both are places where a
  cart and a person want to be at the same time.
- **The rise.** About 60 m of 2.8 m-headroom tunnel from the mine face to the
  crusher pit, versus about 130 m by the decline and the yard. Faster, tighter,
  unlit, no second exit.
- **Belt walking.** Conveyor belts are walkable. From the refinery north
  mezzanine you can step onto the sorter belt and ride the line east to fuel
  without touching a stair.
- **Control versus cooling.** From the control balcony you can see the whole
  reactor floor and, out to the south, the cooling cut. You cannot reach either
  quickly. That gap is the coordination pressure.
- **Elevation versus warning.** The reactor upper gantry, the refinery
  clerestory and the fuel roof deck all see the compliance road. The working
  floors do not. Whoever is high up is the early-warning system.
- **Hiding places.** Four, not forty: the mine store drift, the maintenance
  tool store, the storage waste containers and tarp, and the empty fuel crates
  on the staging platform.

## Known simplifications

- The decline runs at 20%, steeper than a real haulage decline, to keep the
  site compact. If it should read as gentler, the trench needs to run further
  south and the yard grade strips need re-cutting to match.
- Conveyor and pipe runs are indicative, not engineered. They exist to explain
  where material goes.
- Rough rock is slabs, not a sculpted mesh. It reads correctly at gameplay
  distance and is wrong close up.
- No lighting design. One ambient level, one key, one fill. Interiors are
  legible rather than atmospheric.

## Asking for changes

Every entity has a stable id of the form `zone.name`, shown in the Edit panel
when you select something. That id is the most useful thing to quote:

> "`crusher.deck.track` is too narrow — make it 7 m."
> "Move `control.deck` to the south wall instead of the west."
> "The gap between `refinery.mezz.south` and `fuel` needs a direct link at +5."

Exporting the JSON from the menu gives the whole document with those ids in it.
