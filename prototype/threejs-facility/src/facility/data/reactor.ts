import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('reactor');
const c = zoneAuthor('control');

/**
 * Reactor hall: an octagonal volume 52 m across and 30 m clear, sitting in the
 * middle of the site. Every other zone touches it or looks into it, and it has
 * four doors on four different sides, so it is the hub of the loop rather than
 * the end of a corridor.
 *
 * Octagon vertices, clockwise from the north-west corner:
 *   A(-10,-24) B(10,-24) C(24,-10) D(24,10) E(10,24) F(-10,24) G(-24,10) H(-24,-10)
 *
 * Working floor 0, catwalk ring +8, upper gantry +17.
 */
export const REACTOR_ENTITIES: Entity[] = [
  a.floor('slab', [0, 0, 0], [48, 48]),
  a.roof('lid', [0, 30, 0], [48, 48]),

  a.wall('shell.n', [-10, -24], [10, -24], 30, {
    thickness: 0.6,
    gaps: [
      { at: 4, width: 4, bottom: 2.5, top: 7 }, // fuel belt in
      { at: 11, width: 8, bottom: 17, top: 23 }, // gantry clerestory
      { at: 17, width: 4, top: 4.5 }, // compliance door
    ],
  }),
  a.wall('shell.ne', [10, -24], [24, -10], 30, { thickness: 0.6 }),
  a.wall('shell.e', [24, -10], [24, 10], 30, {
    thickness: 0.6,
    gaps: [
      { at: 3, width: 4, top: 4.5 }, // link to control
      { at: 13, width: 12, bottom: 9, top: 15 }, // overlook windows
    ],
  }),
  a.wall('shell.se', [24, 10], [10, 24], 30, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 6, top: 5 }], // corridor to cooling
  }),
  a.wall('shell.s', [10, 24], [-10, 24], 30, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 4, top: 4 }], // south yard
  }),
  a.wall('shell.sw', [-10, 24], [-24, 10], 30, { thickness: 0.6 }),
  a.wall('shell.w', [-24, 10], [-24, -10], 30, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 7, top: 5.5 }], // main access / cart diagonal
  }),
  a.wall('shell.nw', [-24, -10], [-10, -24], 30, { thickness: 0.6 }),

  a.machine('core', 'REACTOR CORE', [0, 0, 0], [16, 22, 16], { shape: 'cylinder' }),
  a.machine('containment', 'CONTAINMENT FRAME', [0, 0, 0], [26, 26, 26], { shape: 'frame' }),
  a.machine('transfer', 'FUEL TRANSFER', [-16, 0, -14], [7, 5, 7]),
  a.machine('drives', 'CONTROL DRIVES', [16, 0, -14], [6, 4, 6]),
  a.machine('header.a', 'COOLANT HEADER A', [14, 0, 14], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('header.b', 'COOLANT HEADER B', [-14, 0, 14], [5, 6, 5], { shape: 'cylinder' }),

  a.catwalk(
    'ring.8',
    [
      [7, 8, -17],
      [17, 8, -7],
      [17, 8, 7],
      [7, 8, 17],
      [-7, 8, 17],
      [-17, 8, 7],
      [-17, 8, -7],
      [-7, 8, -17],
      [7, 8, -17],
    ],
    2.4,
    { label: 'REACTOR CATWALK +8' },
  ),
  a.catwalk(
    'ring.17',
    [
      [8, 17, -20],
      [20, 17, -8],
      [20, 17, 8],
      [8, 17, 20],
      [-8, 17, 20],
      [-20, 17, 8],
      [-20, 17, -8],
      [-8, 17, -20],
      [8, 17, -20],
    ],
    2.2,
    { label: 'UPPER GANTRY +17' },
  ),
  a.catwalk('spur.stair.low', [[17, 8, -6], [18, 8, -6]], 2, { railings: 'both' }),
  a.catwalk('spur.stair.high', [[18, 17, 6], [20, 17, 6]], 2, { railings: 'both' }),

  a.stair('stair.floor', [-6, 0, 18], [-15, 8, 9], 2.2),
  a.stair('stair.upper', [18, 8, -6], [18, 17, 6], 2),

  a.pipe('pipe.cool.a', [[6, 12, 10], [14, 12, 16], [18, 6, 20]], 0.9),
  a.pipe('pipe.cool.b', [[-6, 12, 10], [-12, 10, 17], [-8, 4, 22]], 0.8),

  a.doorway('door.compliance', [7, 0, -24], 4, 4.5, { label: 'COMPLIANCE ENTRANCE' }),
  a.doorway('door.west', [-24, 0, 0], 7, 5.5, { rotationY: 90, label: 'MAIN ACCESS' }),

  a.spawn('spawn.floor', [0, 0, 18], 'Reactor floor'),
  a.spawn('spawn.gantry', [-8, 17, -20], 'Reactor upper gantry'),

  a.marker('m.core', [-9, 0, 0], 'hazard', 'Core face: nothing between you and it'),
  a.marker('m.clerestory', [0, 17, -19], 'sightline', 'Gantry clerestory looks up the compliance road'),
  a.marker('m.compliance', [7, 0, -20], 'objective', 'Auditors come through this door'),
  a.marker('m.westdoor', [-21, 0, 0], 'crossing', 'West door opens onto the live cart diagonal'),
  a.marker('m.overlook', [21, 0, 3], 'sightline', 'Control is watching through these windows'),

  a.mannequin('scale.1', [0, 0, 12], { rotationY: 0 }),
  a.mannequin('scale.2', [-14, 0, -8], { rotationY: 90 }),
  a.mannequin('scale.3', [-7, 8, 17], { rotationY: 180 }),
  a.mannequin('scale.4', [-8, 17, -20], { rotationY: 180 }),
];

/**
 * Control room: a raised block east of the reactor, looking in through the
 * overlook windows. The view is total and the walk down is not, which is the
 * whole tension of the position.
 */
export const CONTROL_ENTITIES: Entity[] = [
  // Link corridor at grade, reactor east door to the control block.
  c.floor('link', [27, 0, -7], [6, 8]),
  c.roof('link.lid', [27, 5, -7], [6, 8]),
  c.wall('link.n', [24, -11], [30, -11], 5),
  c.wall('link.s', [30, -3], [24, -3], 5),

  c.floor('slab', [42, 0, 0], [24, 28]),
  c.roof('lid', [42, 16, 0], [24, 28]),
  c.wall('shell.n', [30, -14], [54, -14], 16),
  c.wall('shell.e', [54, -14], [54, 14], 16, {
    gaps: [{ at: 14, width: 4, top: 4 }],
  }),
  c.wall('shell.s', [54, 14], [30, 14], 16),
  c.wall('shell.w', [30, 14], [30, -14], 16, {
    gaps: [
      { at: 10, width: 12, bottom: 10, top: 15 }, // overlook windows
      { at: 21, width: 4, top: 4 }, // link corridor
    ],
  }),

  c.platform('deck', [40, 10, 0], [20, 24], {
    label: 'REACTOR CONTROL',
    railings: ['e', 'n', 's'],
    supports: true,
  }),
  c.stair('stair', [33, 0, 10], [33, 10, -4], 2.2),

  c.prop('console.1', [32, 10, -6], [1.4, 1.2, 4]),
  c.prop('console.2', [32, 10, 0], [1.4, 1.2, 4]),
  c.prop('console.3', [32, 10, 6], [1.4, 1.2, 4]),
  c.prop('cabinet', [48, 10, 8], [3, 2.2, 5]),
  c.machine('switchgear', 'SWITCHGEAR', [48, 0, -8], [6, 4, 8]),

  c.doorway('door.east', [54, 0, 0], 4, 4, { rotationY: 90 }),

  c.spawn('spawn.control', [38, 10, 0], 'Reactor control'),
  c.marker('m.view', [31, 10, 0], 'sightline', 'Whole reactor floor, and no quick way to reach it'),
  c.marker('m.walk', [33, 0, 8], 'hazard', 'One stair down, then the length of the link corridor'),
  c.mannequin('scale.1', [34, 10, 0], { rotationY: 90 }),
];
