import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('reactor');
const c = zoneAuthor('control');

/**
 * Reactor hall. X 64..120, Z -30..+28, 30 m clear — the largest volume on the
 * site by a wide margin, and the only one you can see from everywhere.
 * Working floor 0, catwalk ring +9, upper gantry ring +18.
 * Access is asymmetric on purpose: the floor-to-catwalk stair is on the east
 * side, the control stair is on the west, so nobody is ever near both.
 */
export const REACTOR_ENTITIES: Entity[] = [
  a.floor('slab', [92, 0, -1], [56, 58]),
  a.roof('lid', [92, 30, -1], [56, 58]),

  ...roomWalls(a, 'shell', {
    min: [64, -30],
    max: [120, 28],
    height: 30,
    openings: [
      { side: 'w', at: -2, width: 5, top: 4.2 }, // fuel corridor
      { side: 'w', at: -12, width: 4, bottom: 3.5, top: 7.5 }, // fuel belt
      { side: 'n', at: 76, width: 5, top: 4.5 }, // compliance door
      { side: 'n', at: 96, width: 18, bottom: 17, top: 23 }, // gantry clerestory
      { side: 'n', at: 112, width: 4, top: 4.5 }, // emergency exit
      { side: 's', at: 88, width: 8, top: 6 }, // down to cooling
      { side: 's', at: 70, width: 4, top: 3.6 }, // maintenance yard door
      { side: 'e', at: 10, width: 4, top: 3.6 }, // east yard door
    ],
  }),

  a.machine('core', 'REACTOR CORE', [94, 0, -2], [18, 24, 18], { shape: 'cylinder' }),
  a.machine('containment', 'CONTAINMENT FRAME', [94, 0, -2], [28, 27, 28], { shape: 'frame' }),
  a.machine('transfer', 'FUEL TRANSFER', [72, 0, -14], [8, 5, 8]),
  a.machine('drives', 'CONTROL DRIVES', [76, 0, 16], [8, 4, 8]),
  a.machine('header.a', 'COOLANT HEADER A', [84, 0, 18], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('header.b', 'COOLANT HEADER B', [104, 0, 18], [5, 6, 5], { shape: 'cylinder' }),

  a.catwalk(
    'ring.9',
    [
      [78, 9, -18],
      [110, 9, -18],
      [110, 9, 14],
      [78, 9, 14],
      [78, 9, -18],
    ],
    2.4,
    { label: 'REACTOR CATWALK +9' },
  ),
  a.catwalk(
    'ring.18',
    [
      [76, 18, -27],
      [110, 18, -27],
      [110, 18, 18],
      [76, 18, 18],
      [76, 18, -27],
    ],
    2.2,
    { label: 'UPPER GANTRY +18' },
  ),
  a.catwalk('spur.9.east', [[110, 9, -6], [116, 9, -6]], 2, { railings: 'both' }),
  a.catwalk('spur.9.stair', [[110, 9, 6], [113, 9, 6]], 2, { railings: 'both' }),
  a.catwalk('spur.18.stair', [[113, 18, -8], [110, 18, -8]], 2, { railings: 'both' }),

  a.stair('stair.floor.east', [116, 0, -20], [116, 9, -6], 2.2),
  a.stair('stair.floor.south', [86, 0, 26], [86, 9, 14], 2.2),
  a.stair('stair.9to18', [113, 9, 6], [113, 18, -8], 2),

  // Control access: two flights hugging the west wall, away from everything.
  a.stair('stair.control.a', [66, 0, -24], [66, 5.5, -16], 2),
  a.platform('landing.control', [66, 5.5, -14], [4, 4], { railings: ['e', 'w'], supports: true }),
  a.stair('stair.control.b', [66, 5.5, -12], [66, 11, -4], 2),

  a.pipe('pipe.cool.a', [[88, 12, 8], [88, 12, 24], [88, 5, 28]], 0.9),
  a.pipe('pipe.cool.b', [[100, 12, 8], [100, 12, 24], [100, 5, 28]], 0.9),

  a.doorway('door.compliance', [76, 0, -30], 5, 4.5, { label: 'COMPLIANCE ENTRANCE' }),
  a.doorway('door.cooling', [88, 0, 28], 8, 6),

  a.spawn('spawn.floor', [92, 0, 20], 'Reactor floor'),
  a.spawn('spawn.gantry', [92, 18, -27], 'Reactor upper gantry'),

  a.marker('m.core', [86, 0, -2], 'hazard', 'Core face: nothing between you and it'),
  a.marker('m.clerestory', [96, 18, -26], 'sightline', 'See the compliance road from here'),
  a.marker('m.compliance', [76, 0, -26], 'objective', 'Auditors come through this door'),
  a.marker('m.cooling', [88, 0, 24], 'shortcut', 'Down to cooling — the run under pressure'),
  a.marker('m.longwalk', [70, 0, -20], 'sightline', 'Control is 11 m up and two flights away'),

  a.mannequin('scale.1', [92, 0, 12], { rotationY: 0 }),
  a.mannequin('scale.2', [78, 0, -10], { rotationY: 90 }),
  a.mannequin('scale.3', [92, 9, 14], { rotationY: 180 }),
  a.mannequin('scale.4', [92, 18, -27], { rotationY: 180 }),
];

/**
 * Control room: an open balcony hung on the reactor west wall at +11.
 * Deliberately not enclosed on the core side — the sightline is the mechanic.
 */
export const CONTROL_ENTITIES: Entity[] = [
  c.platform('deck', [70, 11, -1], [14, 18], {
    label: 'REACTOR CONTROL',
    railings: ['e'],
    supports: true,
  }),
  c.roof('lid', [70, 15, -1], [14, 18]),
  c.wall('w', [63, 8], [63, -10], 4, { base: 11 }),
  c.wall('n', [63, -10], [77, -10], 4, {
    base: 11,
    gaps: [{ at: 3, width: 3, top: 3 }],
  }),
  c.wall('s', [77, 8], [63, 8], 4, { base: 11 }),

  c.prop('console.1', [75, 11, -6], [1.4, 1.2, 4]),
  c.prop('console.2', [75, 11, -1], [1.4, 1.2, 4]),
  c.prop('console.3', [75, 11, 4], [1.4, 1.2, 4]),
  c.prop('cabinet', [65, 11, 5], [3, 2.2, 4]),

  c.spawn('spawn.control', [70, 11, 0], 'Reactor control'),
  c.marker('m.view', [76, 11, -1], 'sightline', 'Whole reactor floor, no way to reach it quickly'),
  c.marker('m.below', [70, 11, 6], 'sightline', 'Cooling is below and south of this balcony'),
  c.mannequin('scale.1', [74, 11, -1], { rotationY: 90 }),
];
