import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('reactor');
const c = zoneAuthor('control');

const HAZARD = '#c2622c';
const ELECTRIC = '#8c8a5c';

/**
 * Reactor hall: an octagonal volume 52 m across and 30 m clear — and almost
 * none of it is enterable.
 *
 * Workers get a gallery hugging the north and east of the shell: in from the
 * production row, past the fuel deposit, along the operating face under the
 * control windows, and out to cooling. A 1.6 m parapet — too tall to climb,
 * low enough to see the whole hall over — separates that gallery from
 * everything else. The core, the catwalks, the charge deck, the turbine, the
 * switchgear and the vent stack are all in plain sight and none of them can be
 * walked. You can see the entire job and reach three parts of it.
 *
 * Octagon vertices, clockwise from the north-west corner:
 *   A(-10,-24) B(10,-24) C(24,-10) D(24,10) E(10,24) F(-10,24) G(-24,10) H(-24,-10)
 *
 * The gallery, in plan:
 *   X  4..10, Z -24..-13   north leg — in from the production row, fuel deposit
 *   X  4..16, Z -13..-9    the turn
 *   X 11..24, Z -10..10    east leg — operating face, under the control windows
 *   X 11..16, Z  10..19    south leg — out to cooling
 */
export const REACTOR_ENTITIES: Entity[] = [
  // Octagonal floor. The sealed side is still floor; it simply cannot be
  // reached, which keeps the hall reading as one volume from the gallery.
  a.floor('slab.centre', [0, 0, 0], [48, 20]),
  a.floor('slab.n', [0, 0, -17], [20, 14]),
  a.floor('slab.s', [0, 0, 17], [20, 14]),
  a.floor('slab.ne', [13, 0, -13], [6, 6]),
  a.floor('slab.nw', [-13, 0, -13], [6, 6]),
  a.floor('slab.se', [13, 0, 13], [6, 6]),
  a.floor('slab.sw', [-13, 0, 13], [6, 6]),
  a.floor('slab.se.ext', [13, 0, 18], [6, 6]),
  a.roof('lid', [0, 30, 0], [48, 48]),

  a.wall('shell.n', [-10, -24], [10, -24], 30, {
    thickness: 0.6,
    // One tall opening: workers under it, the fuel belt over them.
    gaps: [{ at: 16, width: 4, bottom: 0, top: 7 }],
  }),
  a.wall('shell.ne', [10, -24], [24, -10], 30, { thickness: 0.6 }),
  a.wall('shell.e', [24, -10], [24, 10], 30, {
    thickness: 0.6,
    gaps: [
      { at: 4, width: 4, top: 4.5 }, // link to control
      { at: 13, width: 8, bottom: 9, top: 15 }, // overlook windows
    ],
  }),
  a.wall('shell.se', [24, 10], [10, 24], 30, {
    thickness: 0.6,
    gaps: [{ at: 12.7, width: 5, top: 5 }], // corridor to cooling
  }),
  a.wall('shell.s', [10, 24], [-10, 24], 30, { thickness: 0.6 }),
  a.wall('shell.sw', [-10, 24], [-24, 10], 30, { thickness: 0.6 }),
  a.wall('shell.w', [-24, 10], [-24, -10], 30, { thickness: 0.6 }),
  a.wall('shell.nw', [-24, -10], [-10, -24], 30, { thickness: 0.6 }),

  // --- The parapet ----------------------------------------------------------
  // 1.6 m everywhere: above a jump, below eye height. The whole point of the
  // hall is that you watch it work and cannot get at it.
  a.wall('screen.w', [4, -24], [4, -9], 1.6, { thickness: 0.3 }),
  a.wall('screen.n.e', [10, -24], [10, -13], 1.6, { thickness: 0.3 }),
  a.wall('screen.turn', [10, -13], [16, -13], 1.6, { thickness: 0.3 }),
  a.wall('screen.turn.s', [4, -9], [11, -9], 1.6, { thickness: 0.3 }),
  a.wall('screen.main', [11, -9], [11, 23], 1.6, { thickness: 0.3 }),

  // --- Gallery: north leg, the fuel deposit ---------------------------------
  a.machine('fuel.deposit', 'FUEL DEPOSIT', [7, 0, -18], [4, 2.5, 4], { color: HAZARD }),
  a.machine('fuel.rack', 'NEW FUEL RACK', [7, 0, -22], [4, 2, 3]),
  a.marker('m.fuel.insert', [7, 0, -15], 'interaction', 'Fuel insertion — the charge machine takes it from here'),
  a.marker('m.fuel.uncertain', [7, 0, -21], 'hazard', 'Use uncertain fuel — nobody checks twice'),

  // --- Gallery: east leg, the operating face --------------------------------
  a.machine('annunciator', 'ANNUNCIATOR', [22.6, 1, 0], [0.5, 2.4, 10], { color: ELECTRIC }),
  a.light('annunciator.lamp', [22, 3.6, 0], { size: [0.4, 9], color: '#e8d08a' }),
  a.machine('scram.gallery', 'EMERGENCY SHUTDOWN', [20, 0, -7], [1.4, 1.6, 1.4], { color: HAZARD }),
  a.machine('emergency.locker', 'EMERGENCY LOCKER', [13, 0, -6], [1.5, 2.2, 3], { color: HAZARD }),
  a.prop('log.desk', [21, 0, 3], [1, 1.1, 3]),
  a.prop('rad.monitor', [21, 0, 7], [0.8, 1.8, 0.8]),
  a.marker('m.scram', [19, 0, -7], 'interaction', 'Emergency shutdown — the only one you can reach'),
  a.marker('m.alarm', [22, 0, 0], 'interaction', 'Alarm acknowledgement · suppress alarms'),
  a.marker('m.overlook', [20, 0, 4], 'sightline', 'Control is watching through these windows'),
  a.marker('m.muster', [13, 0, -3], 'objective', 'Muster point'),
  a.marker('m.sealed', [14, 0, 8], 'hazard', 'Everything past the rail is visible and out of reach'),

  // --- Sealed: core and charge ----------------------------------------------
  a.machine('core', 'REACTOR CORE', [0, 0, 0], [16, 20, 16], { shape: 'cylinder' }),
  a.machine('containment', 'CONTAINMENT', [0, 0, 0], [22, 26, 22], { shape: 'frame' }),
  a.platform('charge.deck', [0, 20, 0], [18, 18], {
    label: 'CHARGE DECK +20',
    railings: ['n', 'e', 's', 'w'],
  }),
  a.machine('drives', 'CONTROL ROD DRIVES', [0, 20, 1], [10, 2.5, 10]),
  a.machine('fuelling', 'FUELLING MACHINE', [0, 20, -6], [4.5, 3, 3.5]),
  a.platform('charge.floor', [-2, 1.2, -17.5], [12, 7], {
    label: 'CHARGE FLOOR',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.machine('fuel.receiving', 'FUEL RECEIVING', [-5, 1.2, -18.5], [4.5, 3, 4]),
  a.machine('fuel.flask', 'FUEL TRANSFER FLASK', [-8.5, 0, -20], [4, 5, 4], { shape: 'cylinder' }),

  // --- Sealed: waste, vent, electrical --------------------------------------
  a.machine('waste.flask', 'WASTE FLASK', [-14, 0, -17], [4.5, 5, 4.5], { shape: 'cylinder' }),
  a.machine('waste.store', 'SHIELDED WASTE STORE', [-16, 0, -12], [6, 4, 5], { rotationY: -45 }),
  a.machine('vent.stack', 'VENT STACK', [-20, 0, 0], [4, 30, 4], { shape: 'cylinder' }),
  a.machine('switchgear', 'SWITCHGEAR', [-20, 0, 6], [3, 3.5, 8], { color: ELECTRIC }),
  a.machine('breakers', 'BREAKERS', [-21, 0, -5], [1, 2.6, 6], { color: ELECTRIC }),
  a.machine('backup', 'BACKUP GENERATOR', [-16, 0, 8], [5, 3, 5]),

  // --- Sealed: turbine hall and coolant connections -------------------------
  a.platform('turbine.deck', [2, 0.6, 14], [10, 14], {
    label: 'TURBINE DECK',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.machine('turbine', 'TURBINE', [2, 0.6, 17], [4, 3.5, 8]),
  a.machine('generator', 'GENERATOR', [2, 0.6, 10], [4, 3.5, 5]),
  a.machine('throttle', 'TURBINE THROTTLE', [0, 0.6, 8], [1.4, 1.4, 2], { color: ELECTRIC }),
  a.prop('lube', [5, 0.6, 19], [2, 1.6, 2]),
  a.machine('condenser', 'CONDENSER', [-6, 0, 20], [4, 3, 4], { shape: 'cylinder' }),
  a.machine('header.a', 'COOLANT HEADER A', [-9, 0, 17], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('header.b', 'COOLANT HEADER B', [-16, 0, 13], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('eci', 'EMERGENCY COOLING INJECTION', [-6, 0, 21], [6, 4, 3], { color: HAZARD }),
  a.prop('valve.1', [-13, 0, 16], [1.2, 1.4, 1.2], { shape: 'cylinder' }),
  a.prop('valve.2', [-13, 0, 19], [1.2, 1.4, 1.2], { shape: 'cylinder' }),

  // --- Sealed: circulation, kept as scenery ---------------------------------
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
    { label: 'CATWALK +8 — SEALED' },
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
    { label: 'UPPER GANTRY +17 — SEALED' },
  ),
  a.catwalk('charge.spur', [[0, 17, -20], [0, 17, -16.5]], 2, { railings: 'none' }),
  a.stair('charge.stair', [0, 17, -16.5], [0, 20, -9], 1.8),

  // --- Overhead travelling crane --------------------------------------------
  a.prop('crane.rail.w', [-21, 22.4, 0], [0.8, 0.8, 40]),
  a.prop('crane.rail.e', [21, 22.4, 0], [0.8, 0.8, 40]),
  a.prop('crane.bridge', [0, 23.2, -6], [42, 1.2, 2.2]),
  a.prop('crane.hoist', [0, 21, -6], [2.2, 2, 2.2]),

  // --- Services -------------------------------------------------------------
  a.pipe('pipe.cool.a', [[6, 12, 8], [4, 12, 18], [4, 6, 18]], 0.9),
  a.pipe('pipe.cool.b', [[-6, 12, 8], [-9, 12, 15], [-9, 6, 15]], 0.9),
  a.pipe('pipe.steam', [[6, 14, 2], [6, 14, 12], [5, 5, 13]], 0.7),

  // --- Lighting -------------------------------------------------------------
  a.light('hi.n', [0, 27, -16], { size: [4, 1.2], cast: true, intensity: 260, distance: 46 }),
  a.light('hi.s', [0, 27, 16], { size: [4, 1.2], cast: true, intensity: 260, distance: 46 }),
  a.light('hi.e', [17, 27, 0], { size: [1.2, 4] }),
  a.light('hi.w', [-17, 27, 0], { size: [1.2, 4] }),
  a.light('hi.ne', [13, 27, -13], { size: [3, 1.2] }),
  a.light('hi.nw', [-13, 27, -13], { size: [3, 1.2] }),
  a.light('hi.se', [13, 27, 13], { size: [3, 1.2] }),
  a.light('hi.sw', [-13, 27, 13], { size: [3, 1.2] }),
  a.light('gal.n', [7, 5.4, -18], { cast: true, intensity: 90, distance: 22 }),
  a.light('gal.e', [18, 5.4, 0], { size: [1.2, 4], cast: true, intensity: 90, distance: 22 }),
  a.light('gal.s', [14, 5.4, 14], { size: [3, 1.2] }),
  a.light('alarm.e', [23, 6, 0], { size: [0.8, 0.8], color: '#e0602c' }),
  a.light('alarm.n', [7, 6, -23], { size: [0.8, 0.8], color: '#e0602c' }),

  a.doorway('door.production', [6, 0, -24], 4, 4.5, { label: 'PRODUCTION ROW' }),
  a.doorway('door.cooling', [15, 0, 19], 5, 5, { rotationY: 45, label: 'COOLING' }),

  a.spawn('spawn.gallery', [18, 0, 0], 'Reactor gallery', { primary: false }),
  a.spawn('spawn.fuel', [7, 0, -14], 'Fuel deposit'),
  a.spawn('spawn.sealed.ring', [0, 8, -17], 'Catwalk +8 (sealed — inspection)'),
  a.spawn('spawn.sealed.deck', [0, 20, 7.5], 'Charge deck +20 (sealed — inspection)'),

  a.marker('m.core', [11.5, 0, 0], 'sightline', 'Core face, four metres away and behind a rail'),
  a.marker('m.production', [7, 0, -23], 'objective', 'In from the production row'),
  a.marker('m.cooling', [14, 0, 17], 'shortcut', 'Out to cooling — the only other way through'),

  a.mannequin('scale.1', [7, 0, -16], { rotationY: 180 }),
  a.mannequin('scale.2', [18, 0, -4], { rotationY: 270 }),
  a.mannequin('scale.3', [14, 0, 12], { rotationY: 180 }),
  a.mannequin('scale.4', [-1, 0, 12], { rotationY: 180 }),
  a.mannequin('scale.5', [-7, 8, 17], { rotationY: 180 }),
];

/**
 * Control room: a raised block east of the reactor at +10, looking in through
 * the overlook windows. From here you can see the whole hall including all the
 * parts nobody can walk into; reaching even the gallery is a stair and the
 * length of the link corridor.
 */
export const CONTROL_ENTITIES: Entity[] = [
  c.floor('link', [27, 0, -6], [6, 8]),
  c.roof('link.lid', [27, 5, -6], [6, 8]),
  c.wall('link.n', [24, -10], [30, -10], 5),
  c.wall('link.s', [30, -2], [24, -2], 5),

  c.floor('slab', [42, 0, 0], [24, 28]),
  c.roof('lid', [42, 16, 0], [24, 28]),
  c.wall('shell.n', [30, -14], [54, -14], 16),
  c.wall('shell.e', [54, -14], [54, 14], 16, {
    gaps: [{ at: 14, width: 4, top: 4 }],
  }),
  c.wall('shell.s', [54, 14], [30, 14], 16),
  c.wall('shell.w', [30, 14], [30, -14], 16, {
    gaps: [
      { at: 11, width: 8, bottom: 10, top: 15 }, // overlook windows
      { at: 20, width: 4, top: 4 }, // link corridor
    ],
  }),

  c.platform('deck', [40, 10, 0], [20, 24], {
    label: 'REACTOR CONTROL',
    // North is open onto the stair head, which runs the width of the room.
    railings: ['s', 'e'],
    supports: true,
  }),
  // The stair climbs the four-metre strip east of the deck — in open air, not
  // under the slab it lands on — and arrives on a landing across the north end.
  c.platform('stair.head', [42, 10, -13], [24, 2], { supports: true }),
  c.stair('stair', [52, 0, 13], [52, 10, -12], 2.2),

  // Desk faces the windows: reactivity and temperature on the left, turbine
  // and grid on the right, with the shutdown key between them.
  c.machine('desk.core', 'CORE', [32, 10, -6], [1.4, 1.2, 5], { color: ELECTRIC }),
  c.machine('desk.scram', 'EMERGENCY SHUTDOWN', [32, 10, 0], [1.4, 1.3, 2], { color: HAZARD }),
  c.machine('desk.grid', 'TURBINE & GRID', [32, 10, 5], [1.4, 1.2, 5], { color: ELECTRIC }),
  // Sits on the east half of the north wall: the west half is the way in from
  // the stair head.
  c.machine('mimic', 'PLANT MIMIC', [46, 10, -11.4], [7, 2.6, 0.4], { color: ELECTRIC }),
  c.light('mimic.lamp', [46, 12.9, -11], { size: [6, 0.5], color: '#9fd8e8' }),
  c.machine('demand', 'GRID DEMAND', [48, 10, 8], [4, 2.4, 0.4], { color: ELECTRIC }),
  c.prop('log.table', [44, 10, 4], [2.4, 1.1, 3]),
  c.prop('chair.1', [34, 10, -6], [0.7, 1.1, 0.7]),
  c.prop('chair.2', [34, 10, 5], [0.7, 1.1, 0.7]),
  c.machine('switchgear.ground', 'SWITCHGEAR', [48, 0, -8], [6, 4, 8], { color: ELECTRIC }),
  c.machine('battery', 'CONTROL BATTERY', [48, 0, 6], [4, 2.4, 6], { color: ELECTRIC }),

  c.light('l.deck.n', [40, 15.4, -7], { cast: true, intensity: 120, distance: 26 }),
  c.light('l.deck.s', [40, 15.4, 7]),
  c.light('l.ground', [44, 5.4, 0]),
  c.light('l.link', [27, 4.6, -7]),

  c.doorway('door.east', [54, 0, 0], 4, 4, { rotationY: 90 }),

  c.spawn('spawn.control', [38, 10, 0], 'Reactor control'),
  c.marker('m.view', [31, 10, 0], 'sightline', 'The whole hall, including everywhere you cannot go'),
  c.marker('m.walk', [33, 0, 8], 'hazard', 'One stair down, then the length of the link corridor'),
  c.marker('m.demand', [48, 10, 6], 'objective', 'Demand rises in readable waves — you get warning'),
  c.marker('m.auto', [32, 10, 2], 'hazard', 'Disable automatic shutdown'),
  c.mannequin('scale.1', [34, 10, -6], { rotationY: 90 }),
  c.mannequin('scale.2', [34, 10, 5], { rotationY: 90 }),
];
