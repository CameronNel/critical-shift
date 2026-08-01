import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('cooling');

/**
 * Cooling hall, sunk to -5 m south-east of the reactor and directly below the
 * control room's line of sight. Its lid is flush with grade and stops short of
 * the north wall, leaving an open cut you can see down into from the yard —
 * so the state of the pumps is public, and reaching them still is not.
 *
 * Two ways in: the corridor and stair from the reactor's south-east door, or
 * the maintenance ring, which drains in through the west wall.
 */
export const COOLING_ENTITIES: Entity[] = [
  a.floor('slab', [44, -5, 45], [32, 34]),
  a.platform('lid', [44, 0, 48], [32, 28], {
    label: 'COOLING LID',
    railings: ['n'],
    tags: ['roof'],
  }),

  ...roomWalls(a, 'shell', {
    min: [28, 28],
    max: [60, 62],
    base: -5,
    height: 5,
    openings: [
      { side: 'n', at: 32, width: 7 }, // stair down from the reactor
      { side: 's', at: 52, width: 4 }, // emergency stair to grade
      { side: 'w', at: 34, width: 5 }, // maintenance ring drains in
    ],
  }),

  // Approach from the reactor's south-east door.
  a.floor('approach.a', [22.5, 0, 17], [11, 6]),
  a.floor('approach.b', [30, 0, 24], [6, 14]),
  a.roof('approach.a.lid', [22.5, 5, 17], [11, 6]),
  a.roof('approach.b.lid', [30, 5, 24], [6, 14]),
  a.wall('approach.n', [17, 14], [28, 14], 5),
  a.wall('approach.s', [27, 20], [17, 20], 5),
  a.wall('approach.b.w', [27, 20], [27, 31], 5),
  a.wall('approach.b.n', [28, 17], [33, 17], 5),
  a.wall('approach.b.e', [33, 31], [33, 17], 5),
  a.stair('stair.reactor', [30, 0, 27], [30, -5, 35], 3),
  a.stair('stair.escape', [52, -5, 58], [52, 0, 66], 2),

  a.machine('pump.a', 'COOLANT PUMP A', [34, -5, 40], [6, 4.5, 6], { shape: 'cylinder' }),
  a.machine('pump.b', 'COOLANT PUMP B', [34, -5, 52], [6, 4.5, 6], { shape: 'cylinder' }),
  a.machine('pump.c', 'COOLANT PUMP C', [56, -5, 40], [6, 4.5, 6], { shape: 'cylinder' }),
  a.machine('exchanger', 'HEAT EXCHANGER', [52, -5, 54], [12, 5, 8]),

  a.platform('gallery', [44, -1.5, 46], [7, 20], {
    label: 'VALVE GALLERY',
    railings: ['e', 'w'],
    supports: true,
  }),
  a.stair('stair.gallery', [40, -5, 52], [40, -1.5, 46], 1.8),
  a.prop('valve.1', [44, -1.5, 39], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.2', [44, -1.5, 44], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.3', [44, -1.5, 49], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.4', [44, -1.5, 54], [1.6, 1.4, 1.6], { shape: 'cylinder' }),

  a.pipe('pipe.up.a', [[36, 0, 32], [30, 6, 26], [22, 10, 18]], 0.9),
  a.pipe('pipe.up.b', [[48, 0, 34], [44, 8, 28], [36, 12, 22]], 0.8),
  a.pipe('pipe.loop', [[34, -2, 44], [34, -2, 48], [56, -2, 48]], 0.7),

  a.spawn('spawn.cooling', [44, -5, 45], 'Cooling hall'),
  a.marker('m.valves', [44, -1.5, 46], 'interaction', 'Main coolant valves'),
  a.marker('m.cut', [44, 0, 31], 'sightline', 'Open cut: the pumps are visible from the yard'),
  a.marker('m.run', [30, -5, 36], 'hazard', 'The run from the reactor floor: a corridor and a stair'),
  a.marker('m.escape', [52, -5, 58], 'shortcut', 'Emergency stair straight up to grade'),

  a.mannequin('scale.1', [44, -5, 40], { rotationY: 0 }),
  a.mannequin('scale.2', [44, -1.5, 50], { rotationY: 180 }),
];
