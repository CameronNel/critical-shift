import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('haulage');

/**
 * Haulage. The 56 m cart hall is gone. What is left is the room where you
 * actually do something with a cart, and the office that decides where it
 * goes.
 *
 *   cart hall     X -106..-90, Z -10..6   tip a cart, hook it on, cross the track
 *   marshalling   X  -88..-80, Z  -6..2   which way the next one goes
 *
 * The loop itself runs outside both rooms and passes through the hall on one
 * live track. Crossing that track is the only timing problem here, which is
 * the point: one hazard, legible, in a room small enough to read at a glance.
 */
export const HAULAGE_ENTITIES: Entity[] = [
  // --- Cart hall ------------------------------------------------------------
  a.floor('hall.slab', [-98, 0, -2], [16, 16]),
  a.roof('hall.lid', [-98, 6, -2], [16, 16]),
  ...roomWalls(a, 'hall', {
    min: [-106, -10],
    max: [-90, 6],
    height: 6,
    openings: [
      { side: 'w', at: -2, width: 8, top: 5 }, // the adit, and the track in
      { side: 'e', at: -2, width: 8, top: 5 }, // the track out
      { side: 'n', at: -98, width: 4, top: 3.6 }, // up to arrival
      { side: 's', at: -98, width: 4, top: 3.6 }, // S2 to storage
    ],
  }),
  a.track('through', [[-108, 0, -2], [-88, 0, -2]]),
  a.machine('winch', 'HAUL WINCH', [-103, 0, 3], [4, 3, 3]),
  a.machine('tipper', 'CART TIPPER', [-93, 0, 3], [4, 3, 4]),
  a.prop('cart.1', [-100, 0, -2], [2, 1.6, 3], { rotationY: 90 }),
  a.prop('cart.2', [-95, 0, -7], [2, 1.6, 3], { rotationY: 90 }),
  a.light('hall.l1', [-98, 5.4, -2], { cast: true, intensity: 110, distance: 24 }),
  a.marker('m.cross', [-98, 0, -2], 'crossing', 'Live track. It does not stop for you.'),
  a.marker('m.hook', [-103, 0, 1], 'interaction', 'Hook a cart on'),
  a.marker('m.tip', [-93, 0, 1], 'interaction', 'Tip a cart — overfill it and it jams the crusher'),
  a.spawn('spawn.hall', [-98, 0, 2], 'Cart hall'),
  a.mannequin('scale.1', [-101, 0, 1], { rotationY: 90 }),
  a.mannequin('scale.2', [-95, 0, -6], { rotationY: 0 }),

  // --- Marshalling ----------------------------------------------------------
  a.floor('marsh.slab', [-84, 0, -2], [8, 8]),
  a.roof('marsh.lid', [-84, 4.5, -2], [8, 8]),
  ...roomWalls(a, 'marsh', {
    min: [-88, -6],
    max: [-80, 2],
    height: 4.5,
    openings: [
      { side: 'w', at: -2, width: 4, top: 3.6 },
      { side: 'e', at: -2, width: 4, top: 3.6 }, // out toward the crusher
    ],
  }),
  a.machine('marshal', 'MARSHALLING CONTROL', [-84, 0, -4.5], [5, 1.3, 1.4]),
  a.machine('board', 'CART BOARD', [-87.5, 1.2, -2], [0.3, 2, 4]),
  a.light('marsh.l1', [-84, 4, -2], { cast: true, intensity: 80, distance: 16 }),
  a.marker('m.route', [-84, 0, -3.4], 'interaction', 'Send the next cart: crusher, or back to the face'),
  a.spawn('spawn.marsh', [-83, 0, -1], 'Marshalling'),
  a.mannequin('scale.3', [-84, 0, -2.6], { rotationY: 180 }),

  // --- Scenery: the adit and the loop outside -------------------------------
  a.tunnel('adit', [[-126, -2, -2], [-116, -1, -2], [-107, 0, -2]], 8, 6, {
    label: 'MINE ADIT',
    seed: 31,
    rough: 0.5,
  }),
  a.track('spur.crusher', [[-80, 0, -2], [-72, 0, -20], [-72, 0, -44]]),
  a.doorway('door.adit', [-106, 0, -2], 8, 5.5, { rotationY: 90 }),
];
