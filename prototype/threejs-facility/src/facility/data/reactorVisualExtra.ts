import type { Entity, Vec2, Vec3 } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('reactor');
const PLAN_SCALE = 0.6;
const draft = (n: number) => n / PLAN_SCALE;
const p3 = (x: number, y: number, z: number): Vec3 => [draft(x), y, draft(z)];
const s2 = (x: number, z: number): Vec2 => [draft(x), draft(z)];
const s3 = (x: number, y: number, z: number): Vec3 => [draft(x), y, draft(z)];

const STEEL = '#8f9ba0';
const DARK = '#273238';
const PANEL = '#718a92';
const RED = '#b74d3c';
const YELLOW = '#d7b84f';
const SCREEN = '#3dbbd0';

const tags = (name: string, ...extra: string[]) => ['reactor-visual', `asset:${name}`, ...extra];

/**
 * Small animation-contract pieces kept out of reactorVisual.ts so the hero
 * composition remains readable. Every item here is intentionally a separate
 * exportable entity for Blender/Unity pivots, future interaction and MCP
 * queries.
 */
export const REACTOR_DETAIL_ENTITIES: Entity[] = [
  // --- Front-centre 1.80 m approach / shallow beauty-shot steps ------------
  a.platform('detail.front-approach.landing', p3(0, 0.36, 6.55), s2(1.80, 1.05), {
    color: '#909ba0',
    railings: [],
    supports: false,
    tags: tags('front-approach.landing', 'architecture', 'front-stair', 'blender:FRONT_APPROACH_LANDING'),
    notes: 'Local 0.36 m raised landing for the concept-art front stair. Main circulation can still bypass it at grade.',
  }),
  a.stair('detail.front-approach.steps', p3(0, 0, 5.34), p3(0, 0.36, 6.10), 1.80, {
    railings: false,
    color: '#929da2',
    tags: tags('front-approach.steps', 'architecture', 'front-stair', 'blender:FRONT_APPROACH_STEPS'),
  }),

  // --- Fuel-cart retainers / payload slots ----------------------------------
  ...[-0.36, -0.12, 0.12, 0.36].map((dx, index) =>
    a.prop(`detail.fuel-cart.slot.${index + 1}`, p3(-2.75 + dx, 1.02, 5.85), s3(0.12, 0.48, 0.12), {
      shape: 'cylinder',
      color: STEEL,
      collision: false,
      label: index === 0 ? 'FUEL PAYLOAD RETAINERS' : undefined,
      tags: tags(`fuel-cart.slot.${index + 1}`, 'fuel-handling', 'retainer', 'animation:release', 'blender:FUEL_RETAINER'),
    }),
  ),

  // --- South coolant handwheels ---------------------------------------------
  a.prop('detail.coolant-valve.handwheel-a', p3(-1.62, 1.03, 7.12), s3(0.46, 0.12, 0.46), {
    shape: 'cylinder', rotationY: 90, color: RED, collision: false,
    label: 'COOLANT VALVE A HANDWHEEL',
    tags: tags('coolant-valve.handwheel-a', 'interactive', 'cooling', 'valve-wheel', 'animation:rotate', 'blender:COOLANT_VALVE_A_WHEEL'),
  }),
  a.prop('detail.coolant-valve.handwheel-b', p3(-0.78, 1.03, 7.12), s3(0.46, 0.12, 0.46), {
    shape: 'cylinder', rotationY: 90, color: RED, collision: false,
    label: 'COOLANT VALVE B HANDWHEEL',
    tags: tags('coolant-valve.handwheel-b', 'interactive', 'cooling', 'valve-wheel', 'animation:rotate', 'blender:COOLANT_VALVE_B_WHEEL'),
  }),

  // --- East grid breaker handles --------------------------------------------
  ...[-0.48, 0, 0.48].map((dz, index) =>
    a.prop(`detail.grid-breaker.handle.${index + 1}`, p3(8.35, 1.04 + index * 0.18, -1.80 + dz), s3(0.16, 0.50, 0.18), {
      color: index === 1 ? RED : YELLOW,
      collision: false,
      label: index === 0 ? 'GRID BREAKER HANDLES' : undefined,
      tags: tags(`grid-breaker.handle.${index + 1}`, 'interactive', 'grid', 'breaker-handle', 'animation:rotate', 'blender:GRID_BREAKER_HANDLE'),
    }),
  ),

  // --- West reserve / backup physical controls ------------------------------
  a.prop('detail.reserve.breaker-handle', p3(-8.34, 1.02, -1.10), s3(0.20, 0.56, 0.18), {
    color: RED, collision: false, label: 'RESERVE POWER BREAKER',
    tags: tags('reserve.breaker-handle', 'interactive', 'reserve-power', 'breaker-handle', 'animation:rotate', 'blender:RESERVE_BREAKER'),
  }),
  a.prop('detail.backup.start-handle', p3(-7.55, 1.04, 4.72), s3(0.20, 0.48, 0.18), {
    color: YELLOW, collision: false, label: 'BACKUP GENERATOR START',
    tags: tags('backup.start-handle', 'interactive', 'backup-power', 'lever', 'animation:rotate', 'blender:BACKUP_START_HANDLE'),
  }),

  // --- Analogue gauge faces and independent needles -------------------------
  a.prop('detail.gauge.coolant-pressure.face', p3(-1.20, 1.68, 7.24), s3(0.42, 0.42, 0.08), {
    color: '#d5dcda', collision: false, label: 'COOLANT PRESSURE GAUGE',
    tags: tags('gauge.coolant-pressure.face', 'gauge', 'cooling', 'blender:GAUGE_FACE'),
  }),
  a.prop('detail.gauge.coolant-pressure.needle', p3(-1.20, 1.87, 7.18), s3(0.035, 0.26, 0.035), {
    color: DARK, collision: false,
    tags: tags('gauge.coolant-pressure.needle', 'gauge-needle', 'cooling', 'animation:rotate', 'blender:GAUGE_NEEDLE'),
  }),
  a.prop('detail.gauge.turbine-speed.face', p3(6.55, 1.88, 3.08), s3(0.42, 0.42, 0.08), {
    color: '#d5dcda', collision: false, label: 'TURBINE SPEED GAUGE',
    tags: tags('gauge.turbine-speed.face', 'gauge', 'turbine', 'blender:GAUGE_FACE'),
  }),
  a.prop('detail.gauge.turbine-speed.needle', p3(6.55, 2.07, 3.02), s3(0.035, 0.26, 0.035), {
    color: DARK, collision: false,
    tags: tags('gauge.turbine-speed.needle', 'gauge-needle', 'turbine', 'animation:rotate', 'blender:GAUGE_NEEDLE'),
  }),

  // --- Replaceable local displays not already covered by hero screens -------
  a.prop('detail.screen.core-temperature', p3(5.72, 1.48, -5.15), s3(0.78, 0.48, 0.08), {
    color: SCREEN, collision: false, label: 'CORE TEMPERATURE',
    tags: tags('screen.core-temperature', 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE'),
  }),
  a.prop('detail.screen.pool-level', p3(3.72, 1.46, 6.70), s3(0.72, 0.46, 0.08), {
    color: SCREEN, collision: false, label: 'POOL / COOLANT LEVEL',
    tags: tags('screen.pool-level', 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE'),
  }),

  // --- Operable door leaves, parked open so the browser remains traversable -
  a.prop('detail.door.west.leaf', p3(-10.48, 0, -2.10), s3(0.16, 4.80, 2.45), {
    color: PANEL, collision: false, label: 'MAIN ACCESS DOOR LEAF',
    tags: tags('door.west.leaf', 'door-leaf', 'animation:door', 'blender:DOOR_MAIN_ACCESS'),
  }),
  a.prop('detail.door.fuel.leaf', p3(-2.25, 0, -10.45), s3(2.25, 4.50, 0.16), {
    color: PANEL, collision: false, label: 'FUEL CORRIDOR DOOR LEAF',
    tags: tags('door.fuel.leaf', 'door-leaf', 'animation:door', 'blender:DOOR_FUEL'),
  }),
  a.prop('detail.door.control.leaf', p3(10.38, 0, -4.55), s3(0.16, 4.50, 1.85), {
    color: PANEL, collision: false, label: 'CONTROL LINK DOOR LEAF',
    tags: tags('door.control.leaf', 'door-leaf', 'animation:door', 'blender:DOOR_CONTROL'),
  }),
  a.prop('detail.door.cooling.leaf', p3(8.48, 0, 8.16), s3(0.16, 4.50, 2.10), {
    rotationY: 45, color: PANEL, collision: false, label: 'COOLING ACCESS DOOR LEAF',
    tags: tags('door.cooling.leaf', 'door-leaf', 'animation:door', 'blender:DOOR_COOLING'),
  }),

  // --- Hazard bands: separate strips instead of texture-baked markings ------
  a.floor('detail.hazard.south-left', p3(-2.35, 0.025, 5.28), s2(1.10, 0.10), {
    thickness: 0.03, rotationY: 0, color: YELLOW, collision: false,
    tags: tags('hazard.south-left', 'hazard-marking', 'blender:HAZARD_STRIP'),
  }),
  a.floor('detail.hazard.south-right', p3(2.35, 0.025, 5.28), s2(1.10, 0.10), {
    thickness: 0.03, rotationY: 0, color: YELLOW, collision: false,
    tags: tags('hazard.south-right', 'hazard-marking', 'blender:HAZARD_STRIP'),
  }),

  // --- Future VFX anchors: deliberately labelled query pins -----------------
  a.marker('fx.core-glow', p3(0, -5.85, 0), 'objective', 'FX: CORE GLOW / MELTDOWN LIGHT ORIGIN'),
  a.marker('fx.steam.pool-a', p3(-2.45, 0, 2.10), 'hazard', 'FX: POOL STEAM A'),
  a.marker('fx.steam.pool-b', p3(2.45, 0, 2.10), 'hazard', 'FX: POOL STEAM B'),
  a.marker('fx.steam.coolant-east', p3(5.15, 1.4, 5.85), 'hazard', 'FX: COOLANT STEAM EAST'),
  a.marker('fx.steam.coolant-west', p3(-4.95, 1.4, 5.85), 'hazard', 'FX: COOLANT STEAM WEST'),
  a.marker('fx.alarm.left', p3(-4.9, 4.7, 5.6), 'hazard', 'FX: ALARM BEACON LEFT'),
  a.marker('fx.alarm.right', p3(4.9, 4.7, 5.6), 'hazard', 'FX: ALARM BEACON RIGHT'),
];
