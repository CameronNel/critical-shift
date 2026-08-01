import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('maintenance');

/**
 * Service spine on the -6 m datum. It runs from the crusher pit, under the
 * refinery, past a stairwell that surfaces in the yard, and out to cooling.
 * 4 m clear width: two people pass, and a body drags without snagging.
 * Learnable on purpose — one spine, one branch, one dead-end store.
 */
export const MAINTENANCE_ENTITIES: Entity[] = [
  // The rise continues from the mine, climbing 2 m over 50 m to the spine.
  a.tunnel(
    'rise.east',
    [
      [-104, -11, 4],
      [-96, -9.5, 7],
      [-84, -8, 11],
      [-72, -6.6, 16],
      [-54, -6, 16],
    ],
    3.2,
    2.8,
    { seed: 97, rough: 0.5 },
  ),

  a.floor('spine', [9, -6, 16], [122, 4]),
  a.roof('spine.lid', [9, -2, 16], [122, 4]),
  ...roomWalls(a, 'spine', {
    min: [-52, 14],
    max: [70, 18],
    base: -6,
    height: 4,
    thickness: 0.3,
    openings: [
      { side: 'n', at: -50, width: 4 }, // crusher pit leg
      { side: 's', at: 5, width: 3 }, // tool store
      { side: 's', at: 28, width: 3.6 }, // stairwell to the yard
      { side: 's', at: 68, width: 4 }, // cooling leg
      { side: 'w', at: 16, width: 3.6 },
    ],
  }),

  // West leg up into the crusher pit.
  a.floor('leg.west', [-50, -6, 10], [4, 14]),
  a.roof('leg.west.lid', [-50, -2, 10], [4, 14]),
  a.wall('leg.west.w', [-52, 3], [-52, 14], 4, { base: -6, thickness: 0.3 }),
  a.wall('leg.west.e', [-48, 14], [-48, 3], 4, { base: -6, thickness: 0.3 }),

  // East leg out to the cooling hall.
  a.floor('leg.east', [68, -6, 28], [4, 24]),
  a.roof('leg.east.lid', [68, -2, 28], [4, 24]),
  a.wall('leg.east.w', [66, 18], [66, 40], 4, { base: -6, thickness: 0.3 }),
  a.wall('leg.east.e', [70, 40], [70, 18], 4, { base: -6, thickness: 0.3 }),

  // Tool store: the one room down here with a door and a reason to linger.
  a.floor('store', [5, -6, 22], [10, 8]),
  a.roof('store.lid', [5, -2, 22], [10, 8]),
  ...roomWalls(a, 'store', {
    min: [0, 18],
    max: [10, 26],
    base: -6,
    height: 4,
    thickness: 0.3,
    openings: [{ side: 'n', at: 5, width: 3 }],
  }),
  a.machine('bench', 'TOOL STORE', [3, -6, 24], [4, 1.2, 5]),
  a.prop('racks', [8, -6, 22], [1.4, 2.4, 6]),
  a.prop('spares', [5, -6, 19.5], [4, 1.6, 2]),

  // Stairwell surfacing in the yard between the refinery and fuel.
  a.floor('shaft.base', [28, -6, 21], [8, 18]),
  a.wall('shaft.w', [24, 12], [24, 30], 6, { base: -6 }),
  a.wall('shaft.e', [32, 30], [32, 12], 6, { base: -6 }),
  a.wall('shaft.s', [32, 30], [24, 30], 6, { base: -6 }),
  a.wall('shaft.n', [24, 12], [32, 12], 6, { base: -6 }),
  a.stair('shaft.stair', [28, 0, 26], [28, -6, 17], 2),

  a.mannequin('scale.1', [0, -6, 16], { rotationY: 90 }),
  a.mannequin('scale.2', [-70, -6.2, 16], { rotationY: 270 }),

  a.spawn('spawn.spine', [10, -6, 16], 'Maintenance spine'),
  a.marker('m.spine', [40, -6, 16], 'shortcut', 'Spine: crusher to cooling, unseen'),
  a.marker('m.store', [5, -6, 22], 'hiding', 'Tool store: lockable, and nobody audits it'),
  a.marker('m.shaft', [28, -6, 20], 'shortcut', 'Stairwell surfaces beside the refinery'),
  a.marker('m.rise', [-70, -6.2, 16], 'hazard', '2.8 m headroom, no lighting, no second exit'),
];
