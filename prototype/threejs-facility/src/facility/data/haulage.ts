import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('haulage');

/**
 * The decline: an open cut from grade at Z = +40 down to the mine datum at
 * Z = -20, 13% grade, 7.5 m wide. Carts and people share it, which is the
 * point. Two bridges cross it, so the yard is split by a permanent hazard.
 */
export const HAULAGE_ENTITIES: Entity[] = [
  a.ramp('decline', [-80, -8, -20], [-80, 0, 40], 7.5, { label: 'DECLINE' }),

  // Retaining walls, stepped so their tops stay level with grade.
  a.wall('cut.w.1', [-84, -20], [-84, -5], 8, { base: -8 }),
  a.wall('cut.w.2', [-84, -5], [-84, 10], 6, { base: -6 }),
  a.wall('cut.w.3', [-84, 10], [-84, 25], 4, { base: -4 }),
  a.wall('cut.w.4', [-84, 25], [-84, 40], 2, { base: -2 }),
  a.wall('cut.e.1', [-76, -20], [-76, -5], 8, { base: -8 }),
  a.wall('cut.e.2', [-76, -5], [-76, 10], 6, { base: -6 }),
  a.wall('cut.e.3', [-76, 10], [-76, 25], 4, { base: -4 }),
  a.wall('cut.e.4', [-76, 25], [-76, 40], 2, { base: -2 }),

  // Refuge bay: the only place to stand when a loaded cart runs away.
  a.platform('refuge', [-77.6, -4.05, 10], [2.8, 6], {
    label: 'REFUGE',
    railings: ['e'],
    supports: false,
  }),

  // Cart drift from the bottom of the decline to the extraction face.
  a.tunnel(
    'drift.main',
    [
      [-80, -8, -20],
      [-92, -8, -18],
      [-104, -8, -17],
      [-111, -8, -16],
    ],
    6,
    5.4,
    { label: 'HAULAGE DRIFT', seed: 5, rough: 0.45 },
  ),

  a.track('track.drift', [[-111, -8, -16], [-92, -8, -18], [-80, -8, -20]]),
  a.track('track.decline', [[-80, -8, -20], [-80, 0, 40]]),
  a.track('track.yard', [[-80, 0, 40], [-72, 0, 44], [-58, 0, 44], [-50, 0, 32], [-50, 0, 12]]),

  a.prop('cart.decline', [-80, -3.4, 8], [2, 1.6, 3]),
  a.prop('cart.yard', [-56, 0, 44], [2, 1.6, 3], { rotationY: 90 }),

  a.machine('winch', 'HAUL WINCH', [-80, 0, 43], [5, 3.5, 4]),

  a.marker('m.crossing', [-62, 0, 44], 'crossing', 'CART CROSSING — south route'),
  a.marker('m.decline', [-80, -6.9, -12], 'hazard', 'Nothing to hide behind below the refuge'),
  a.marker('m.bottom', [-80, -8, -19], 'crossing', 'Shaft bottom: carts turn into the drift here'),

  a.mannequin('scale.decline', [-78, -5.9, 3], { rotationY: 0 }),
];
