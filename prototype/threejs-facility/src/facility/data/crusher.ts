import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('crusher');

/**
 * Crusher. Two small rooms and nothing else you can walk into.
 *
 *   crush house   X -80..-64, Z -58..-44   the machine, and the jam you clear
 *   pit head      X -76..-66, Z -42..-34   the hatch down into the service ring
 *
 * The tipping deck, the ore pit and the cart track are outside both rooms:
 * you see the carts tip through the crush house window and you never stand on
 * the deck. Everything a player does here is done in those two rooms.
 */
export const CRUSHER_ENTITIES: Entity[] = [
  // --- Crush house ----------------------------------------------------------
  a.floor('house.slab', [-72, 0, -51], [16, 14]),
  a.roof('house.lid', [-72, 6, -51], [16, 14]),
  ...roomWalls(a, 'house', {
    min: [-80, -58],
    max: [-64, -44],
    height: 6,
    openings: [
      { side: 'n', at: -72, width: 4, top: 3.6 }, // in from the cart hall
      { side: 'e', at: -51, width: 5, bottom: 2, top: 5 }, // crushed ore out
      { side: 's', at: -71, width: 4, top: 3.6 }, // through to the pit head
      { side: 'w', at: -51, width: 6, bottom: 1.2, top: 3 }, // window onto the tipping deck
    ],
  }),
  a.machine('crusher', 'PRIMARY CRUSHER', [-69, 0, -52], [7, 5, 8]),
  a.machine('jaw.control', 'CRUSHER CONTROL', [-77, 0, -48], [1.2, 1.3, 3]),
  a.prop('bar.rack', [-77, 0, -54], [0.8, 1.8, 3]),
  a.light('house.l1', [-72, 5.4, -51], { cast: true, intensity: 110, distance: 24 }),
  a.marker('m.jam', [-73, 0, -52], 'interaction', 'Clear a jam — the machine does not stop for you'),
  a.marker('m.bars', [-76, 0, -54], 'interaction', 'Take a bar'),
  a.marker('m.window', [-78, 0, -51], 'sightline', 'Carts tip on the far side of this glass'),
  a.spawn('spawn.house', [-75, 0, -50], 'Crush house'),
  a.mannequin('scale.1', [-74, 0, -48], { rotationY: 90 }),

  // --- Sample room ----------------------------------------------------------
  // Flat, small, and the only other place here you can stand. The hatch in the
  // floor is welded: the service ring is reached from storage, one way in.
  a.floor('sample.slab', [-71, 0, -38], [10, 8]),
  a.roof('sample.lid', [-71, 4.5, -38], [10, 8]),
  ...roomWalls(a, 'sample', {
    min: [-76, -42],
    max: [-66, -34],
    height: 4.5,
    openings: [
      { side: 'n', at: -71, width: 4, top: 3.6 }, // from the crush house
      { side: 'e', at: -38, width: 4, top: 3.6 }, // out to the spine
    ],
  }),
  a.machine('assay', 'ORE ASSAY', [-74, 0, -40], [3, 2.2, 2.5]),
  a.prop('sample.bench', [-71, 0, -35.5], [6, 0.9, 1.2]),
  a.prop('sample.hatch', [-68, 0, -40], [2.5, 0.3, 2.5]),
  a.light('sample.l1', [-71, 4, -38], { cast: true, intensity: 90, distance: 18 }),
  a.marker('m.assay', [-74, 0, -38.2], 'interaction', 'Log the grade — or log the grade you want'),
  a.marker('m.hatch', [-68, 0, -38.2], 'hiding', 'Welded hatch: nothing goes down here any more'),
  a.spawn('spawn.sample', [-70, 0, -37], 'Sample room'),
  a.mannequin('scale.2', [-72, 0, -37]),

  // --- Scenery: the tipping deck and the ore pit, seen and not entered ------
  a.machine('tip.deck', 'TIPPING DECK', [-88, 0, -51], [10, 1, 16]),
  a.machine('hopper', 'ORE HOPPER', [-84, 0, -58], [8, 6, 5]),
  a.conveyor('conv.out', [[-63, 3, -51], [-56, 4, -51]], 2.4, { label: 'CRUSHED ORE → REFINERY' }),
  a.doorway('door.spine', [-66, 0, -38], 4, 3.6, { rotationY: 90 }),
  a.doorway('door.hall', [-72, 0, -58], 4, 3.6),
];
