import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('mine');

/**
 * Mine. Two working rooms and the shafts that serve them.
 *
 *   face chamber   X -150..-128, Z -10..10   the drill, the loader, the carts
 *   store drift    X -158..-146, Z -30..-22  dead end, and nobody comes here
 *
 * Everything between is a bored drift you pass through rather than work in.
 * Two vertical shafts break the roof: the hoist shaft over the loading point,
 * which is how ore leaves when the cart line is down, and the vent shaft over
 * the vein, which is the only daylight underground.
 *
 * The carts are pushable. That is the point of the drift widths — a 6 m drift
 * you can get a 1.7 m cart round is a different room from one you cannot, and
 * no amount of looking at it tells you which you have.
 */
export const MINE_ENTITIES: Entity[] = [
  // --- Face chamber ---------------------------------------------------------
  a.cavern('chamber.face', [-139, -2, 0], [22, 7, 20], {
    label: 'EXTRACTION FACE',
    seed: 11,
    rough: 0.6,
    openings: [
      { side: 'e', at: 0, width: 8 }, // adit to the cart hall
      { side: 'n', at: -2, width: 6 }, // drift to the vein
    ],
  }),
  a.machine('drill', 'DRILL RIG', [-147, -2, 4], [4, 3.2, 6], { rotationY: 12 }),
  a.machine('loader', 'ORE LOADER', [-144, -2, -6], [6, 3.4, 5]),
  a.prop('ore.pile', [-147, -2, -2], [4, 1.5, 3.5]),
  a.prop('pillar.1', [-136, -2, 6], [2.4, 7, 2.4], { shape: 'cylinder' }),
  a.light('face.l1', [-144, 3.4, 0], { cast: true, intensity: 110, distance: 26 }),
  a.light('face.l2', [-133, 3.4, 0]),
  a.marker('m.face', [-147, -2, 1], 'interaction', 'Drill the face'),
  a.marker('m.load', [-141, -2, -4], 'interaction', 'Load a cart'),
  a.spawn('spawn.face', [-140, -2, 2], 'Mine face'),
  a.mannequin('scale.1', [-143, -2, 2], { rotationY: 90 }),

  // --- Hoist shaft ----------------------------------------------------------
  // Straight up through the rock to grade. Ore goes up it in a bucket when the
  // cart line is down, which is the excuse for it existing; what it really
  // does is put a column of daylight in the middle of the working room.
  a.cavern('shaft.hoist', [-134, -2, -4], [5, 14, 5], {
    label: 'HOIST SHAFT',
    seed: 91,
    rough: 0.35,
    openings: [{ side: 's', at: 0, width: 4, height: 4 }],
  }),
  a.machine('hoist.frame', 'HOIST HEADFRAME', [-134, 10, -4], [4, 5, 4], { shape: 'frame' }),
  a.prop('hoist.bucket', [-134, -2, -4], [2.2, 2, 2.2], { shape: 'cylinder' }),
  a.light('shaft.l1', [-134, 9, -4], { size: [3, 3], color: '#cfe0ea' }),
  a.marker('m.hoist', [-134, -2, -1.5], 'interaction', 'Send a bucket up — slower than the carts, and always available'),

  // --- Drift to the vein ----------------------------------------------------
  a.tunnel('drift.vein', [[-141, -2, -10], [-141, -2, -20]], 6, 5.4, {
    label: 'VEIN DRIFT',
    seed: 23,
    rough: 0.5,
  }),
  a.light('drift.l1', [-141, 2.4, -15]),
  a.marker('m.ground', [-141, -2, -15], 'hazard', 'Poor ground: blast damage collapses this'),

  // --- Vein chamber and its vent shaft --------------------------------------
  a.cavern('chamber.vein', [-142, -2, -26], [16, 6, 12], {
    label: 'ORE VEIN',
    seed: 41,
    rough: 0.65,
    openings: [
      { side: 's', at: 1, width: 6 },
      { side: 'w', at: 0, width: 4.5, height: 4 },
    ],
  }),
  a.cavern('shaft.vent', [-138, -2, -26], [3.5, 13, 3.5], {
    label: 'VENT SHAFT',
    seed: 77,
    rough: 0.3,
    openings: [{ side: 'w', at: 0, width: 3, height: 3.6 }],
  }),
  a.light('vent.l1', [-138, 8, -26], { size: [2.4, 2.4], color: '#cfe0ea' }),
  a.prop('ore.vein', [-145, -2, -26], [4, 1.4, 3]),
  a.marker('m.vent', [-138, -2, -24], 'sightline', 'Daylight. The only piece of it down here.'),

  // --- Store drift ----------------------------------------------------------
  a.tunnel('drift.store', [[-150, -2, -26], [-158, -2, -26]], 4.5, 4, {
    label: 'STORE DRIFT',
    seed: 67,
    rough: 0.7,
  }),
  a.prop('crates.store', [-157, -2, -26], [2.6, 1.8, 2.6]),
  a.prop('tarp.store', [-154, -2, -26], [2.4, 1.2, 2.4]),
  a.marker('m.store', [-156, -2, -26], 'hiding', 'Store drift: nobody comes here'),
  a.spawn('spawn.store', [-152, -2, -26], 'Store drift'),

  // --- The cart line --------------------------------------------------------
  a.track('track.face', [[-126, -2, 0], [-138, -2, 0], [-143, -2, -5]]),
  a.cart('cart.1', [-133, -2, 0], { rotationY: 90 }),
  a.cart('cart.2', [-142, -2, -6], { rotationY: 45 }),
  a.cart('cart.3', [-141, -2, -17], { rotationY: 0 }),
  a.cart('cart.wreck', [-146, -2, -26], { rotationY: 24, pushable: false }),
  a.marker('m.push', [-133, -2, 2], 'interaction', 'Push it. That is the whole mechanism.'),
  a.marker('m.wreck', [-146, -2, -24], 'hazard', 'Off the rails and going nowhere'),
];
