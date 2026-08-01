import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('reactor');
const c = zoneAuthor('control');

const HAZARD = '#c2622c';
const ELECTRIC = '#8c8a5c';

/**
 * Reactor hall: an octagonal volume 52 m across and 30 m clear, in the middle
 * of the site. Every other zone touches it or looks into it, and it has four
 * doors on four different sides, so it is the hub of the loop rather than the
 * end of a corridor.
 *
 * Octagon vertices, clockwise from the north-west corner:
 *   A(-10,-24) B(10,-24) C(24,-10) D(24,10) E(10,24) F(-10,24) G(-24,10) H(-24,-10)
 *
 * The floor is laid out so that every control in GAME_SPEC §12.4 has a physical
 * station, and so that the ones you need at the same moment are deliberately
 * far apart. Clockwise from the north:
 *
 *   N   charge floor and fuel handling      NE  waste transfer and store
 *   E   operating face, under the windows   SE  turbine and generator
 *   S   coolant headers and injection       SW  switchgear, breakers, backup
 *   W   main access and muster              NW  vent stack and the stair up
 *
 * Working floor 0, catwalk ring +8, upper gantry +17, charge deck +20 on the
 * core itself, travelling crane at +23.
 */
export const REACTOR_ENTITIES: Entity[] = [
  // Octagonal floor, approximated by a centre band, two ends and four corner
  // fills. The small gaps at the diagonals sit 2 cm above the yard grade.
  a.floor('slab.centre', [0, 0, 0], [48, 20]),
  a.floor('slab.n', [0, 0, -17], [20, 14]),
  a.floor('slab.s', [0, 0, 17], [20, 14]),
  a.floor('slab.ne', [13, 0, -13], [6, 6]),
  a.floor('slab.nw', [-13, 0, -13], [6, 6]),
  a.floor('slab.se', [13, 0, 13], [6, 6]),
  a.floor('slab.sw', [-13, 0, 13], [6, 6]),
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

  // --- Core -----------------------------------------------------------------
  a.machine('core', 'REACTOR CORE', [0, 0, 0], [16, 20, 16], { shape: 'cylinder' }),
  a.machine('containment', 'CONTAINMENT', [0, 0, 0], [26, 26, 26], { shape: 'frame' }),

  // Charge deck sits on the core: control rod drives and the fuelling machine.
  a.platform('charge.deck', [0, 20, 0], [18, 18], {
    label: 'CHARGE DECK +20',
    railings: ['n', 'e', 's', 'w'],
  }),
  a.machine('drives', 'CONTROL ROD DRIVES', [0, 20, 1], [10, 2.5, 10]),
  a.machine('fuelling', 'FUELLING MACHINE', [0, 20, -6], [4.5, 3, 3.5]),
  a.catwalk('charge.spur', [[0, 17, -20], [0, 17, -12]], 2, { railings: 'both' }),
  a.stair('charge.stair', [0, 17, -12], [0, 20, -6], 1.8),

  // --- North: charge floor and fuel handling --------------------------------
  a.platform('charge.floor', [0, 1.2, -17.5], [16, 7], {
    label: 'CHARGE FLOOR',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.stair('charge.floor.stair', [0, 0, -11], [0, 1.2, -14], 3),
  a.machine('fuel.receiving', 'FUEL RECEIVING', [-5, 1.2, -18.5], [4.5, 3, 4]),
  a.machine('fuel.flask', 'FUEL TRANSFER FLASK', [-8.5, 0, -20], [4, 5, 4], {
    shape: 'cylinder',
  }),
  a.machine('fuel.rack', 'NEW FUEL RACK', [5, 1.2, -18.5], [6, 2, 4]),
  a.marker('m.fuel.insert', [0, 1.2, -15], 'interaction', 'Fuel insertion'),
  a.marker('m.fuel.uncertain', [5, 1.2, -16], 'hazard', 'Use uncertain fuel — nobody checks twice'),

  // --- North-east: waste ----------------------------------------------------
  a.machine('waste.flask', 'WASTE FLASK', [14, 0, -14], [4.5, 5, 4.5], { shape: 'cylinder' }),
  a.machine('waste.store', 'SHIELDED WASTE STORE', [16, 0, -9], [7, 4, 6], { rotationY: -45 }),
  a.prop('waste.trolley', [11, 0, -10], [2, 1.2, 3]),
  a.marker('m.waste', [14, 0, -11], 'interaction', 'Waste transfer'),
  a.marker('m.waste.illegal', [17, 0, -6], 'hiding', 'Store waste illegally'),

  // --- East: operating face, under the control windows ----------------------
  a.machine('annunciator', 'ANNUNCIATOR', [22.6, 1, 0], [0.5, 2.4, 10], { color: ELECTRIC }),
  a.light('annunciator.lamp', [22, 3.6, 0], { size: [0.4, 9], color: '#e8d08a' }),
  a.machine('scram.east', 'EMERGENCY SHUTDOWN', [19, 0, -8], [1.4, 1.6, 1.4], { color: HAZARD }),
  a.prop('rad.monitor.1', [20, 0, 6], [0.8, 1.8, 0.8]),
  a.prop('log.desk', [20, 0, 2], [1, 1.1, 3]),
  a.marker('m.scram.e', [19, 0, -6], 'interaction', 'Emergency shutdown'),
  a.marker('m.alarm', [22, 0, 0], 'interaction', 'Alarm acknowledgement · suppress alarms'),
  a.marker('m.sensor', [20, 0, 6], 'hazard', 'Operate with a damaged sensor'),

  // --- South-east: turbine and generator ------------------------------------
  a.platform('turbine.deck', [14, 0.6, 6], [8, 16], {
    label: 'TURBINE DECK',
    railings: ['w'],
    supports: true,
  }),
  a.machine('turbine', 'TURBINE', [14, 0.6, 11], [4, 3.5, 10]),
  a.machine('generator', 'GENERATOR', [14, 0.6, 3], [4, 3.5, 5]),
  a.machine('condenser', 'CONDENSER', [19, 0, 8], [4, 3, 4], { shape: 'cylinder' }),
  a.machine('throttle', 'TURBINE THROTTLE', [10, 0.6, 0], [1.4, 1.4, 2], { color: ELECTRIC }),
  a.machine('lube', 'LUBE SKID', [18, 0, 3], [3, 2, 3]),
  a.stair('turbine.stair', [10, 0, 8], [12, 0.6, 8], 2, { railings: false }),
  a.marker('m.throttle', [10, 0.6, -2], 'interaction', 'Turbine throttle · match turbine load'),
  a.marker('m.overload', [14, 0.6, 16], 'hazard', 'Overload the turbine'),

  // --- South: coolant connections -------------------------------------------
  a.machine('header.a', 'COOLANT HEADER A', [-8, 0, 17], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('header.b', 'COOLANT HEADER B', [6, 0, 17], [5, 6, 5], { shape: 'cylinder' }),
  a.machine('eci', 'EMERGENCY COOLING INJECTION', [-1, 0, 21], [7, 4, 4], { color: HAZARD }),
  a.prop('valve.1', [-11, 0, 14], [1.2, 1.4, 1.2], { shape: 'cylinder' }),
  a.prop('valve.2', [-4, 0, 14], [1.2, 1.4, 1.2], { shape: 'cylinder' }),
  a.prop('valve.3', [2, 0, 14], [1.2, 1.4, 1.2], { shape: 'cylinder' }),
  a.prop('valve.4', [9, 0, 14], [1.2, 1.4, 1.2], { shape: 'cylinder' }),
  a.prop('flowmeter', [-1, 0, 13], [2.4, 1.6, 0.8]),
  a.machine('scram.south', 'EMERGENCY SHUTDOWN', [8, 0, 20], [1.4, 1.6, 1.4], { color: HAZARD }),
  a.marker('m.valves', [-1, 0, 12], 'interaction', 'Coolant valves · confirm cooling'),
  a.marker('m.cooling.cut', [-1, 0, 19], 'hazard', 'Reduce cooling to save power'),

  // --- South-west: electrical -----------------------------------------------
  a.machine('switchgear', 'SWITCHGEAR', [-16, 0, 11], [3, 3.5, 8], { color: ELECTRIC }),
  a.machine('breakers', 'BREAKERS', [-19, 0, 4], [1, 2.6, 6], { color: ELECTRIC }),
  a.machine('backup', 'BACKUP GENERATOR', [-12, 0, 16], [5, 3, 5]),
  a.machine('reserve', 'RESERVE POWER', [-19, 0, -3], [2.5, 2.2, 6], { color: ELECTRIC }),
  a.marker('m.breakers', [-17, 0, 4], 'interaction', 'Breakers'),
  a.marker('m.backup', [-12, 0, 13], 'interaction', 'Backup generator · confirm reserve power'),
  a.marker('m.reserve', [-17, 0, -3], 'hazard', 'Use reserve power'),

  // --- West: main access and muster -----------------------------------------
  a.machine('scram.west', 'EMERGENCY SHUTDOWN', [-17, 0, 0], [1.4, 1.6, 1.4], { color: HAZARD }),
  a.machine('toolpoint', 'TOOL POINT', [-21, 0, -6], [2, 1.6, 3]),
  a.machine('emergency.locker', 'EMERGENCY LOCKER', [-21, 0, 5], [1.5, 2.2, 3], { color: HAZARD }),
  a.prop('muster.board', [-22, 0, -2], [0.4, 2, 3]),
  a.marker('m.muster', [-19, 0, -2], 'objective', 'Muster point'),
  a.marker('m.repair', [-19, 0, 8], 'interaction', 'Repair point — repairing while live is the shortcut'),

  // --- North-west: vent stack and the stair up ------------------------------
  a.machine('vent.stack', 'VENT STACK', [-15, 0, -13], [4, 30, 4], { shape: 'cylinder' }),
  a.machine('vent.valve', 'VENT VALVE', [-12, 0, -16], [2, 2, 2], { color: HAZARD }),
  a.marker('m.vent', [-12, 0, -13], 'interaction', 'Venting'),

  // --- Circulation ----------------------------------------------------------
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
  a.stair('stair.floor.w', [-6, 0, 18], [-15, 8, 9], 2.2),
  a.stair('stair.floor.ne', [9, 0, -18], [15.5, 8, -8.5], 2.2),
  a.stair('stair.upper', [18, 8, -6], [18, 17, 6], 2),

  // --- Overhead travelling crane --------------------------------------------
  a.prop('crane.rail.w', [-21, 22.4, 0], [0.8, 0.8, 40]),
  a.prop('crane.rail.e', [21, 22.4, 0], [0.8, 0.8, 40]),
  a.prop('crane.bridge', [0, 23.2, -6], [42, 1.2, 2.2]),
  a.prop('crane.hoist', [0, 21, -6], [2.2, 2, 2.2]),

  // --- Services -------------------------------------------------------------
  a.pipe('pipe.cool.a', [[6, 12, 8], [10, 12, 15], [8, 6, 19]], 0.9),
  a.pipe('pipe.cool.b', [[-6, 12, 8], [-9, 12, 15], [-8, 6, 19]], 0.9),
  a.pipe('pipe.steam', [[8, 14, 2], [14, 14, 8], [14, 5, 10]], 0.7),

  // --- Lighting -------------------------------------------------------------
  a.light('hi.n', [0, 27, -16], { size: [4, 1.2], cast: true, intensity: 260, distance: 46 }),
  a.light('hi.s', [0, 27, 16], { size: [4, 1.2], cast: true, intensity: 260, distance: 46 }),
  a.light('hi.e', [17, 27, 0], { size: [1.2, 4] }),
  a.light('hi.w', [-17, 27, 0], { size: [1.2, 4] }),
  a.light('hi.ne', [13, 27, -13], { size: [3, 1.2] }),
  a.light('hi.nw', [-13, 27, -13], { size: [3, 1.2] }),
  a.light('hi.se', [13, 27, 13], { size: [3, 1.2] }),
  a.light('hi.sw', [-13, 27, 13], { size: [3, 1.2] }),
  a.light('ring.l.n', [0, 7.4, -17], { size: [3, 0.7] }),
  a.light('ring.l.s', [0, 7.4, 17], { size: [3, 0.7] }),
  a.light('alarm.w', [-23, 6, 0], { size: [0.8, 0.8], color: '#e0602c' }),
  a.light('alarm.e', [23, 6, 0], { size: [0.8, 0.8], color: '#e0602c' }),
  a.light('alarm.n', [0, 6, -23], { size: [0.8, 0.8], color: '#e0602c' }),

  a.doorway('door.compliance', [7, 0, -24], 4, 4.5, { label: 'COMPLIANCE ENTRANCE' }),
  a.doorway('door.west', [-24, 0, 0], 7, 5.5, { rotationY: 90, label: 'MAIN ACCESS' }),

  a.spawn('spawn.floor', [-14, 0, 0], 'Reactor floor'),
  a.spawn('spawn.charge', [0, 1.2, -17.5], 'Charge floor'),
  a.spawn('spawn.ring', [0, 8, -17], 'Reactor catwalk +8'),
  a.spawn('spawn.gantry', [0, 17, -20], 'Reactor upper gantry'),
  a.spawn('spawn.deck', [0, 20, 7.5], 'Charge deck +20'),

  a.marker('m.core', [-9, 0, 0], 'hazard', 'Core face: nothing between you and it'),
  a.marker('m.clerestory', [0, 17, -19], 'sightline', 'Gantry clerestory looks up the compliance road'),
  a.marker('m.compliance', [7, 0, -20], 'objective', 'Auditors come through this door'),
  a.marker('m.westdoor', [-21, 0, 0], 'crossing', 'West door opens onto the live cart diagonal'),
  a.marker('m.overlook', [21, 0, 3], 'sightline', 'Control is watching through these windows'),
  a.marker('m.spread', [0, 0, 8], 'objective', 'Cooling south, breakers west, throttle east — by design'),

  a.mannequin('scale.1', [-14, 0, 0], { rotationY: 270 }),
  a.mannequin('scale.2', [0, 1.2, -16], { rotationY: 0 }),
  a.mannequin('scale.3', [-1, 0, 12], { rotationY: 180 }),
  a.mannequin('scale.4', [11, 0.6, 6], { rotationY: 90 }),
  a.mannequin('scale.5', [-7, 8, 17], { rotationY: 180 }),
  a.mannequin('scale.6', [0, 20, 7.5], { rotationY: 0 }),
];

/**
 * Control room: a raised block east of the reactor at +10, looking in through
 * the overlook windows. Total visibility, and one stair plus the length of the
 * link corridor to reach any of it.
 */
export const CONTROL_ENTITIES: Entity[] = [
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

  // Desk faces the windows: reactivity and temperature on the left, turbine
  // and grid on the right, with the shutdown key between them.
  c.machine('desk.core', 'CORE', [32, 10, -6], [1.4, 1.2, 5], { color: ELECTRIC }),
  c.machine('desk.scram', 'EMERGENCY SHUTDOWN', [32, 10, 0], [1.4, 1.3, 2], { color: HAZARD }),
  c.machine('desk.grid', 'TURBINE & GRID', [32, 10, 5], [1.4, 1.2, 5], { color: ELECTRIC }),
  c.machine('mimic', 'PLANT MIMIC', [40, 10, -11.4], [12, 2.6, 0.4], { color: ELECTRIC }),
  c.light('mimic.lamp', [40, 12.9, -11], { size: [11, 0.5], color: '#9fd8e8' }),
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
  c.marker('m.view', [31, 10, 0], 'sightline', 'Whole reactor floor, and no quick way to reach it'),
  c.marker('m.walk', [33, 0, 8], 'hazard', 'One stair down, then the length of the link corridor'),
  c.marker('m.demand', [48, 10, 6], 'objective', 'Demand rises in readable waves — you get warning'),
  c.marker('m.auto', [32, 10, 2], 'hazard', 'Disable automatic shutdown'),
  c.mannequin('scale.1', [34, 10, -6], { rotationY: 90 }),
  c.mannequin('scale.2', [34, 10, 5], { rotationY: 90 }),
];
