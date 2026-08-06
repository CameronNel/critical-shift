import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';
import { CONTROL_VISUAL_ENTITIES, REACTOR_VISUAL_ENTITIES } from './reactorVisual';

const a = zoneAuthor('reactor');
const c = zoneAuthor('control');

const HAZARD = '#c2622c';
const ELECTRIC = '#8c8a5c';

/**
 * A compact reactor workroom, not a destination-sized hall. `SITE_SCALE`
 * turns this 36 m authored octagon into a ~22 m in-game room, so every normal
 * station is visible from the reactor pool and reachable in a few seconds.
 *
 * The layout is deliberately a readable clockwise loop:
 * fuel/reactivity north, waste and vent north-east, output east, cooling
 * south, recovery west, and alarms/SCRAM on the south pool-side emergency
 * station. The detailed central pool and dual-bank visual pass lives in
 * reactorVisual.ts and follows docs/REACTOR_ROOM_VISUAL_SPEC.md exactly.
 *
 * Short enclosed links join the existing fuel corridor, control nook and
 * cooling approach without adding a long exterior run.
 */
export const REACTOR_ENTITIES: Entity[] = [
  // --- Tight, four-door octagonal shell ------------------------------------
  // The former solid centre slab is intentionally gone: reactorVisual.ts
  // creates a walkable annular service ring around a real recessed pool hole.
  a.floor('slab.n', [0, 0, -13], [20, 6]),
  a.floor('slab.s', [0, 0, 13], [20, 6]),
  a.floor('slab.ne', [12, 0, -10], [6, 6]),
  a.floor('slab.nw', [-12, 0, -10], [6, 6]),
  a.floor('slab.se', [12, 0, 10], [6, 6]),
  a.floor('slab.sw', [-12, 0, 10], [6, 6]),
  a.roof('lid', [0, 16, 0], [36, 36]),

  a.wall('shell.n', [-10, -18], [10, -18], 16, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 5, top: 5 }],
  }),
  a.wall('shell.ne', [10, -18], [18, -10], 16, { thickness: 0.6 }),
  a.wall('shell.e', [18, -10], [18, 10], 16, {
    thickness: 0.6,
    gaps: [{ at: 4, width: 4, top: 5 }],
  }),
  a.wall('shell.se', [18, 10], [10, 18], 16, {
    thickness: 0.6,
    gaps: [{ at: 5.6, width: 5, top: 5 }],
  }),
  a.wall('shell.s', [10, 18], [-10, 18], 16, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 4, top: 5 }],
  }),
  a.wall('shell.sw', [-10, 18], [-18, 10], 16, { thickness: 0.6 }),
  a.wall('shell.w', [-18, 10], [-18, -10], 16, {
    thickness: 0.6,
    gaps: [{ at: 10, width: 6, top: 5.5 }],
  }),
  a.wall('shell.nw', [-18, -10], [-10, -18], 16, { thickness: 0.6 }),

  // Small direct links prevent a hidden dead zone between the compact room and
  // its neighbouring departments.
  a.floor('link.fuel', [0, 0, -25], [6, 14]),
  a.roof('link.fuel.lid', [0, 5, -25], [6, 14]),
  a.wall('link.fuel.w', [-3, -32], [-3, -18], 5),
  a.wall('link.fuel.e', [3, -18], [3, -32], 5),
  a.floor('link.control', [21, 0, -6], [6, 8]),
  a.roof('link.control.lid', [21, 5, -6], [6, 8]),
  a.wall('link.control.n', [18, -10], [24, -10], 5),
  a.wall('link.control.s', [24, -2], [18, -2], 5),
  a.floor('link.cooling', [15.5, 0, 15.5], [5, 5]),
  a.floor('link.west', [-21, 0, 0], [6, 8]),

  // --- Finished central visual pass ----------------------------------------
  ...REACTOR_VISUAL_ENTITIES,

  // --- Overview -------------------------------------------------------------
  // Kept as the existing compact call-out perch. It sits above the north edge
  // of the pool circulation envelope rather than becoming a second route.
  a.platform('core.perch', [0, 4.8, -7.5], [6, 2.5], {
    label: 'REACTOR OVERVIEW +5',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.stair('core.perch.stair', [-13, 0, -3], [-3, 4.8, -7.5], 2.2),
  a.marker('m.core', [-6, 0, 0], 'hazard', 'Pool edge — every reactor cascade becomes visible here'),
  a.marker('m.overview', [0, 4.8, -7.5], 'sightline', 'All critical stations visible from this perch'),

  // --- North: fuel and reactivity -------------------------------------------
  a.machine('fuel.receiving', 'FUEL RECEIVING', [-7, 0, -13], [4, 3, 4], {
    color: '#71877e',
    tags: ['reactor-gameplay', 'sector:north', 'fuel', 'blender:FUEL_RECEIVING'],
  }),
  a.machine('fuel.rack', 'NEW / UNCERTAIN FUEL RACK', [-2, 0, -14], [4, 2, 3], {
    color: '#6f827b',
    tags: ['reactor-gameplay', 'sector:north', 'fuel', 'hiding-opportunity', 'blender:FUEL_RACK'],
  }),
  a.machine('drives', 'CONTROL BANK POSITION', [4, 0, -13], [3, 3, 3], {
    color: ELECTRIC,
    tags: ['reactor-gameplay', 'sector:north', 'reactivity', 'blender:BANK_CONTROL_STATION'],
  }),
  a.marker('m.fuel.insert', [-6, 0, -10.5], 'interaction', 'Fuel insertion'),
  a.marker('m.fuel.uncertain', [-2, 0, -11], 'hazard', 'Use uncertain fuel'),
  a.marker('m.control', [4, 0, -10.5], 'interaction', 'Control-bank position · raise output too quickly'),

  // --- North-east: waste and containment relief ----------------------------
  a.machine('waste.transfer', 'WASTE TRANSFER', [12, 0, -13], [4, 3.5, 4], {
    shape: 'cylinder',
    color: '#71877e',
    tags: ['reactor-gameplay', 'sector:north-east', 'waste', 'blender:WASTE_TRANSFER'],
  }),
  a.machine('vent.valve', 'VENT VALVE', [14, 0, -8], [2, 2.2, 2], {
    color: HAZARD,
    tags: ['reactor-gameplay', 'sector:north-east', 'venting', 'blender:VENT_VALVE'],
  }),
  a.prop('waste.trolley', [10, 0, -8], [2, 1.2, 3], {
    color: '#59676a',
    tags: ['reactor-gameplay', 'waste', 'movable', 'blender:WASTE_TROLLEY'],
  }),
  a.marker('m.waste', [10, 0, -12], 'interaction', 'Waste transfer'),
  a.marker('m.waste.illegal', [13, 0, -10], 'hiding', 'Store waste illegally'),
  a.marker('m.vent', [14, 0, -6], 'interaction', 'Venting'),

  // --- East: output ----------------------------------------------------------
  a.machine('turbine', 'TURBINE THROTTLE', [12.5, 0, 5], [3.5, 3.5, 7], {
    shape: 'cylinder',
    color: '#738d96',
    tags: ['reactor-gameplay', 'sector:east', 'turbine', 'blender:TURBINE_THROTTLE'],
  }),
  a.machine('breakers', 'GRID BREAKERS', [15, 0, -3], [2, 3, 5], {
    color: ELECTRIC,
    tags: ['reactor-gameplay', 'sector:east', 'grid', 'blender:GRID_BREAKERS'],
  }),
  a.machine('demand', 'GRID DEMAND', [12, 0, -7.5], [3, 2.4, 2], {
    color: ELECTRIC,
    tags: ['reactor-gameplay', 'sector:east', 'grid-demand', 'blender:GRID_DEMAND'],
  }),
  a.prop('sensor', [15, 0, 7.5], [0.8, 1.8, 0.8], {
    color: '#38464b',
    label: 'CONTAINMENT SENSOR',
    tags: ['reactor-gameplay', 'sector:east', 'sensor', 'blender:CONTAINMENT_SENSOR'],
  }),
  a.marker('m.throttle', [10, 0, 5], 'interaction', 'Turbine throttle · overload turbine'),
  a.marker('m.breakers', [13.5, 0, -1], 'interaction', 'Breakers · match grid demand'),
  a.marker('m.sensor', [14, 0, 7], 'hazard', 'Operate with a damaged sensor'),

  // --- South: cooling --------------------------------------------------------
  a.machine('pump', 'COOLANT PUMP', [-8, 0, 13], [4, 3.5, 4], {
    shape: 'cylinder',
    color: '#738d96',
    tags: ['reactor-gameplay', 'sector:south', 'cooling', 'blender:COOLANT_PUMP_LOCAL'],
  }),
  a.machine('valves', 'COOLANT VALVES', [-2, 0, 14], [4, 2.4, 3], {
    color: ELECTRIC,
    tags: ['reactor-gameplay', 'sector:south', 'cooling', 'blender:COOLANT_VALVES_LOCAL'],
  }),
  a.machine('eci', 'EMERGENCY COOLING', [5, 0, 13], [5, 3, 4], {
    color: HAZARD,
    tags: ['reactor-gameplay', 'sector:south', 'emergency-cooling', 'blender:EMERGENCY_COOLING'],
  }),
  a.marker('m.pump', [-8, 0, 10], 'interaction', 'Pump activation · maintain pumps'),
  a.marker('m.valves', [-2, 0, 11], 'interaction', 'Coolant valves · reduce cooling to save power'),
  a.marker('m.eci', [5, 0, 10], 'interaction', 'Emergency cooling injection'),

  // --- West: recovery and repair --------------------------------------------
  a.machine('backup', 'BACKUP GENERATOR', [-14, 0, 7], [4, 3, 4], {
    color: '#71877e',
    tags: ['reactor-gameplay', 'sector:west', 'backup-power', 'blender:BACKUP_GENERATOR'],
  }),
  a.machine('reserve', 'RESERVE POWER', [-15, 0, -2], [2.5, 2.2, 5], {
    color: ELECTRIC,
    tags: ['reactor-gameplay', 'sector:west', 'reserve-power', 'blender:RESERVE_POWER'],
  }),
  a.machine('repair', 'LIVE REPAIR BAY', [-13, 0, -9], [3, 2.5, 3], {
    color: HAZARD,
    tags: ['reactor-gameplay', 'sector:west', 'repair', 'blender:LIVE_REPAIR_BAY'],
  }),
  a.marker('m.backup', [-12, 0, 7], 'interaction', 'Backup generator'),
  a.marker('m.reserve', [-14, 0, -2], 'hazard', 'Use reserve power'),
  a.marker('m.repair', [-12, 0, -8], 'interaction', 'Repair point · delay maintenance / repair while live'),

  // --- South pool-side emergency functions ---------------------------------
  // Geometry is in reactorVisual.ts. These markers retain the original
  // gameplay interaction identities while pointing at the finished console.
  a.marker('m.alarm', [0, 0, 9.15], 'interaction', 'Alarm acknowledgement · suppress alarms'),
  a.marker('m.auto', [1.1, 0, 9.25], 'hazard', 'Disable automatic shutdown'),
  a.marker('m.scram', [0, 0, 9.5], 'interaction', 'Emergency shutdown / SCRAM'),

  a.doorway('door.fuel', [0, 0, -18], 5, 5, { label: 'FUEL CORRIDOR' }),
  a.doorway('door.control', [18, 0, -6], 4, 5, { rotationY: 90, label: 'CONTROL LINK' }),
  a.doorway('door.cooling', [14, 0, 14], 5, 5, { rotationY: 45, label: 'COOLING ACCESS' }),
  a.doorway('door.west', [-18, 0, 0], 6, 5.5, { rotationY: 90, label: 'MAIN ACCESS' }),

  a.spawn('spawn.floor', [-10, 0, 0], 'Reactor floor'),
  a.spawn('spawn.core', [-6, 0, 0], 'Reactor pool'),
  a.spawn('spawn.overview', [0, 4.8, -7.5], 'Reactor overview'),
  a.marker('m.flow', [0, 0, 11.5], 'objective', 'Fuel north · output east · cooling south · recovery west'),
  a.mannequin('scale.1', [-10, 0, 0], { rotationY: 90 }),
  a.mannequin('scale.2', [-2, 0, 11], { rotationY: 180 }),
  a.mannequin('scale.3', [10, 0, 5], { rotationY: 270 }),
];

/**
 * Control remains a visible oversight nook rather than another critical-run
 * destination: all time-sensitive reactor controls are on the floor below.
 */
export const CONTROL_ENTITIES: Entity[] = [
  c.floor('link', [27, 0, -6], [6, 8]),
  c.roof('link.lid', [27, 5, -6], [6, 8]),
  c.wall('link.n', [24, -10], [30, -10], 5),
  c.wall('link.s', [30, -2], [24, -2], 5),

  c.floor('slab', [42, 0, 0], [24, 28]),
  c.roof('lid', [42, 16, 0], [24, 28]),
  c.wall('shell.n', [30, -14], [54, -14], 16),
  c.wall('shell.e', [54, -14], [54, 14], 16, { gaps: [{ at: 14, width: 4, top: 4 }] }),
  c.wall('shell.s', [54, 14], [30, 14], 16),
  c.wall('shell.w', [30, 14], [30, -14], 16, {
    gaps: [
      { at: 11, width: 8, bottom: 10, top: 15 },
      { at: 20, width: 4, top: 4 },
    ],
  }),
  c.platform('deck', [40, 10, 0], [20, 24], {
    label: 'REACTOR CONTROL',
    railings: ['s', 'e'],
    supports: true,
  }),
  c.platform('stair.head', [42, 10, -13], [24, 2], { supports: true }),
  c.stair('stair', [52, 0, 13], [52, 10, -12], 2.2),
  c.machine('desk.core', 'CORE', [32, 10, -6], [1.4, 1.2, 5], { color: ELECTRIC }),
  c.machine('desk.scram', 'EMERGENCY SHUTDOWN', [32, 10, 0], [1.4, 1.3, 2], { color: HAZARD }),
  c.machine('desk.grid', 'TURBINE & GRID', [32, 10, 5], [1.4, 1.2, 5], { color: ELECTRIC }),
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

  ...CONTROL_VISUAL_ENTITIES,

  c.doorway('door.east', [54, 0, 0], 4, 4, { rotationY: 90 }),
  c.spawn('spawn.control', [38, 10, 0], 'Reactor control'),
  c.marker('m.view', [31, 10, 0], 'sightline', 'Whole reactor floor, with a short direct link to it'),
  c.marker('m.demand', [48, 10, 6], 'objective', 'Demand rises in readable waves — you get warning'),
  c.mannequin('scale.1', [34, 10, -6], { rotationY: 90 }),
  c.mannequin('scale.2', [34, 10, 5], { rotationY: 90 }),
];
