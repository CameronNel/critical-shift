# Cafeteria, hall and yard: design package

**Status: proposal.** Drafted with the owner on 2026-10-04. Not reviewed, not accepted, nothing built. Sizes of the three
zones are proposals (the repo gives none); the spawn room, medical and every neighbouring room are at their measured sizes.
Numbers marked "estimate" are design targets, not measurements.

![Plan](plan.png)

## 1. One connected module, three zones
The yard, cafeteria and hall are one module in one file with one roof language (steel portal frames, corrugated and
standing-seam roofs, charcoal steel with ochre accents). They are zones, not separate buildings:

| Zone | Size | What it is |
|---|---|---|
| Hall | 36 x 12 m, 6 m ceiling | Junction. Three ways on: west colonnade to the refinery, a heavy door onto the 34 m spine to the reactor, and one east door onto the trunk that splits to the dock and waste. |
| Cafeteria / chill room | 34 x 20 m, 5 m ceiling | First room after spawn. Warm, social, the pace-setter before the danger. Shares a 6 m opening with the hall. |
| Yard | 40 x 24 m, open air | Staging and logistics. Rail from the mine, junk and equipment, evacuation gate, the cliff on its west edge. A 4 m covered porch joins it to the cafeteria. |

Compared with plan v7 the 6 m connectors between rooms are gone: the cafeteria now touches the hall, and the yard touches the
cafeteria through the porch. That moves the spawn 12 m north and shortens the front end. The spawn exit to the reactor
is about 66 m (15 s walking) and the spawn exit to the mine portal is also about 66 m (15 s).

## 2. Two axes, one choice
From the spawn door the player sees the whole decision:
- **Reactor axis (x = 8):** spawn door, cafeteria aisle, 6 m opening, hall, heavy spine door, 34 m spine, reactor door. A 75 m
  straight sightline ending on a lit red door.
- **Mine axis (y = -70):** cafeteria west door, porch, 40 m across the yard to the mine portal under the cliff.

Both axes keep a 2.4 m clear lane. Furniture, junk and planting stay off them.

## 3. Zone briefs
### Yard (open air)
- Floor: 66 concrete slabs on a 4 m grid with recessed joints and two shallow puddles. No painted-on joints.
- West edge is the cliff and the mine portal. A cart track runs from the portal along y = -72 and turns north to the
  refinery freight gate. Two ore carts sit on it.
- Junk is built in four clusters (north-west corner, south-west, mid-south, south-east with generator, fuel and water tanks).
  Crate stacks, pallets, barrels, cable drums, scrap steel, tarp piles, tyres. Six prop families, instanced.
- Porch canopy and smoking shelter at the cafeteria door; loading canopy over the refinery gate; planters and four trees.
- Perimeter: fence and a 6 m vehicle gate on the south edge (the evacuation route), a 2.4 m service door at the north-west
  corner onto the passage to the cooling plant, and the mine-water riser along the cliff.
- Light: sun and sky, with the cliff shading the western third in the morning. Warm concrete, machine grey, charcoal steel,
  rust and ochre. No teal (the spawn-yard concept notes ask for none).

### Cafeteria / chill room
- Aisle: a 2.4 m lane on x = 8 from the spawn door to the hall opening.
- West half: six four-seat tables, three booths on the south wall, three vending machines beside the yard door, a notice board.
- East half: serving counter and kitchen block in the north-east corner, coffee machine, water cooler and fridge, and a lounge
  in the south-east (two rust-red couches, a coffee table, a wall TV) kept clear of the 2.2 m medical door.
- High windows on the yard side show the cliff and the mine portal from inside. Skylights over the dining area.
- Light: warm strips and pendants, daylight through the high windows. No mechanics are assumed. The spec does not mention a
  cafeteria, so furniture is static scenery in the first pass; physics props are a separate decision.

### Hall
- Floor: a 4 m clear route with yellow route lines, the reactor door's lane widest.
- Heavy blast door on the spine (3.6 x 3.2 m) with status lights; plain 2.4 m doors at the west end and the east end.
- Gantry landing 4.2 m up over the spine door, reached by a stair at its west end, as the start of the overhead gantry.
- Shift desk with monitors, benches, eyewash, first-aid and fire cabinets, a PPE return, a status board over the doors.
- Light: cool strips and a clerestory, red status lights at the doors.

## 4. Doors and openings
| Opening | Size (clear) | Notes |
|---|---|---|
| Spawn exit to cafeteria | 2.6 m | Measured: the built spawn exit is a two-leaf steel airlock, 2.58 m clear and about 2.6 m high. The scenery spec's 1.5 to 1.8 m predates it. Keep the built width. |
| Cafeteria to hall | 6 m opening | Open arch, can take a rolling shutter. |
| Cafeteria to yard | 3 m double door | Onto the porch. |
| Cafeteria to medical | 2.2 m | Measured width of medical's only door. |
| Hall to spine (reactor) | 3.6 x 3.2 m | Heavy blast door. |
| Hall to refinery | 2.4 m | West colonnade, 15 m, covered. |
| Hall east end to east trunk | 2.4 m | The trunk splits just outside: dock one way, waste the other. |
| Yard to refinery freight gate | 3 m | Rail passes through. |
| Yard to cooling passage | 2.4 m | North-west corner. |
| Yard evacuation gate | 6 m | South edge. |
| Mine portal | 7.2 m | In the cliff. |

## 5. Triangle budget (800k)
![Budget](budget.png)

Planned about 701k of 800k with a 99k (12%) reserve: yard 285k, cafeteria 215k, hall 116k, shared shell 85k. Shortening the hall from 44 m to 36 m saved about 13.5k. The repo flags
rooms over 400k, so this area needs that noted at review. These are design estimates with each instance counted;
the real figure comes from the room validator once something is built.

## 6. Materials
Eighteen shared families for the whole area (listed on the budget sheet), one atlas per zone. A view from the yard also
sees the mountain and the refinery, so the per-view material cap has to be checked with those loaded.

## 7. Concept views
Greybox views built from the same layout data (plain boxes, no materials or art). They check scale, sightlines and clearances.
Not the module.

![Spawn exit looking north](V1_spawn_exit_north.png)
![Yard door looking west](V2_yard_door_west.png)
![Hall looking east](V3_hall_east.png)
![Aerial](V4_aerial.png)

## 8. If this is approved
1. Shell blockout at real size, then a triangle count against the budget before any prop work.
2. Yard, then cafeteria, then hall, counting after each.
3. Lighting and material pass, then the room validator and a reach check on the doors.
4. Independent review before anything is called finished.

## 9. Open questions for the owner
- Are the three zone sizes right, or should the cafeteria or yard grow or shrink?
- Is the cafeteria scenery only, or should anything in it be interactive?
- Is the south yard gate how players leave the facility during evacuation?
- Do the hall doors lock during a meltdown (the spec lists "restore blast door" as an objective)?
- The hall is 36 x 12 m (432 m2), down from 44 x 12 m. Keep, or shorten further?
- The area is about 701k against a 400k flag. Accept, or trim?
