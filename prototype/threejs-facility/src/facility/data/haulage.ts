import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('haulage');

/**
 * Haulage hall. X -112..-56, Z -28..+28, 8 m clear.
 *
 * A cart loop, not a line: carts run continuously round it, take the north
 * spur to the crusher, or the east spur onto the diagonal access run. Because
 * the loop never stops, crossing this floor on foot is a timing problem, and
 * because the east spur shares the diagonal with workers, so is leaving it.
 */
export const HAULAGE_ENTITIES: Entity[] = [
  a.floor('slab', [-84, 0, 0], [56, 56]),
  a.roof('lid', [-84, 8, 0], [56, 56]),

  ...roomWalls(a, 'shell', {
    min: [-112, -28],
    max: [-56, 28],
    height: 8,
    openings: [
      { side: 'w', at: 0, width: 9, top: 6 }, // mine adit
      { side: 'n', at: -73, width: 7, top: 6 }, // cart spur to the crusher
      { side: 'n', at: -100, width: 4, top: 3.6 }, // door up to arrival
      { side: 'e', at: -14, width: 4, top: 3.6 }, // yard door
      { side: 's', at: -84, width: 4, top: 3.6 }, // S2 to storage
    ],
  }),

  // Adit: the hall floor is at grade, the mine two metres below, and the
  // approach is a rock cutting rather than a built ramp.
  a.tunnel('adit', [[-127, -2, 0], [-118, -1, 0], [-110, 0, 0]], 8, 6, {
    label: 'MINE ADIT',
    seed: 31,
    rough: 0.5,
  }),

  // The loop.
  a.track('loop', [
    [-100, 0, -20],
    [-70, 0, -20],
    [-64, 0, -8],
    [-64, 0, 8],
    [-72, 0, 20],
    [-98, 0, 20],
    [-106, 0, 8],
    [-106, 0, -8],
    [-100, 0, -20],
  ]),
  a.track('spur.crusher', [[-73, 0, -20], [-73, 0, -32]]),
  a.track('spur.mine', [[-106, 0, 0], [-126, -2, 0]]),

  a.machine('winch', 'HAUL WINCH', [-104, 0, -24], [5, 3.5, 4]),
  a.machine('marshal', 'MARSHALLING CONTROL', [-84, 0, -24], [6, 3, 4]),
  a.platform('inspect.deck', [-84, 5, 0], [10, 12], {
    label: 'LOOP OVERSIGHT',
    railings: ['n', 'e', 's', 'w'],
    supports: true,
  }),
  a.stair('inspect.stair', [-92, 0, 8], [-92, 5, -4], 2),

  a.prop('cart.1', [-88, 0, -20], [2, 1.6, 3], { rotationY: 90 }),
  a.prop('cart.2', [-64, 0, 2], [2, 1.6, 3]),
  a.prop('cart.3', [-96, 0, 20], [2, 1.6, 3], { rotationY: 90 }),
  a.prop('spares', [-108, 0, -22], [4, 2, 5]),

  a.doorway('door.adit', [-112, 0, 0], 9, 6, { rotationY: 90 }),

  a.spawn('spawn.loop', [-84, 0, 0], 'Haulage loop'),
  a.marker('m.loop', [-84, 0, -10], 'crossing', 'The loop never stops; crossing is a timing problem'),
  a.marker('m.adit', [-110, 0, 0], 'interaction', 'Mine adit'),

  a.mannequin('scale.1', [-84, 0, 8], { rotationY: 0 }),
  a.mannequin('scale.2', [-84, 5, 0], { rotationY: 180 }),
];
