import type { Entity, Vec2, Vec3 } from '../schema';
import { zoneAuthor } from './authoring';

const r = zoneAuthor('reactor');
const c = zoneAuthor('control');
const SCALE = 0.6;
const d = (n: number) => n / SCALE;
const p3 = (x: number, y: number, z: number): Vec3 => [d(x), y, d(z)];
const s2 = (x: number, z: number): Vec2 => [d(x), d(z)];
const s3 = (x: number, y: number, z: number): Vec3 => [d(x), y, d(z)];
const deg = (rad: number) => (rad * 180) / Math.PI;

const WHITE = '#dce4e7';
const PALE = '#c7d0d4';
const STEEL = '#7b878d';
const STAINLESS = '#b9c3c7';
const BLUE_GREY = '#718b95';
const GREEN_GREY = '#6e847b';
const DARK = '#263239';
const SCREEN = '#2bbbd7';
const CORE = '#30d8ff';
const CORE_WHITE = '#d4fbff';
const YELLOW = '#d6ad39';
const RED = '#b84a38';
const ORANGE = '#d06c32';
const BLACK = '#151b1f';
const CONCRETE = '#aeb7ba';

const tags = (name: string, ...extra: string[]) => ['reactor-building', `asset:${name}`, ...extra];

function radialRing(
  prefix: string,
  inner: number,
  outer: number,
  y: number,
  thickness: number,
  count: number,
  color: string,
  walkable = false,
): Entity[] {
  const out: Entity[] = [];
  const radius = (inner + outer) / 2;
  const depth = outer - inner;
  const chord = 2 * radius * Math.tan(Math.PI / count) * 1.03;
  for (let i = 0; i < count; i++) {
    const t = (i / count) * Math.PI * 2;
    const name = `${prefix}.${String(i + 1).padStart(2, '0')}`;
    const pos = p3(radius * Math.cos(t), y, radius * Math.sin(t));
    const rotationY = deg(Math.PI / 2 - t);
    if (walkable) {
      out.push(r.floor(name, pos, s2(chord, depth), {
        thickness,
        rotationY,
        color,
        tags: tags(name, 'module', 'walkable', 'blender:separate'),
      }));
    } else {
      out.push(r.prop(name, p3(radius * Math.cos(t), y - thickness, radius * Math.sin(t)), s3(chord, thickness, depth), {
        rotationY,
        color,
        collision: false,
        tags: tags(name, 'module', 'blender:separate'),
      }));
    }
  }
  return out;
}

function shaftPanels(count = 32): Entity[] {
  const out: Entity[] = [];
  const radius = 3.5;
  const chord = 2 * radius * Math.tan(Math.PI / count) * 1.04;
  for (let i = 0; i < count; i++) {
    const t = (i / count) * Math.PI * 2;
    const name = `interior.pool.shaft.panel.${String(i + 1).padStart(2, '0')}`;
    out.push(r.prop(name, p3(radius * Math.cos(t), -6.5, radius * Math.sin(t)), s3(chord, 6.1, 0.18), {
      rotationY: deg(Math.PI / 2 - t),
      color: i % 2 ? '#b9d0d6' : '#c5d9de',
      collision: false,
      tags: tags(name, 'pool', 'submerged', 'shaft-panel', 'blender:separate'),
    }));
  }
  return out;
}

function arc(radius: number, y: number, a0: number, a1: number, steps: number): Vec3[] {
  const pts: Vec3[] = [];
  for (let i = 0; i <= steps; i++) {
    const t = a0 + ((a1 - a0) * i) / steps;
    pts.push(p3(radius * Math.cos(t), y, radius * Math.sin(t)));
  }
  return pts;
}

function poolRails(): Entity[] {
  const radius = 3.92;
  const gate = 1.4;
  const half = Math.asin(gate / (2 * radius));
  const south = Math.PI / 2;
  const start = south + half;
  const end = south - half + Math.PI * 2;
  const out: Entity[] = [
    r.pipe('interior.pool.rail.top', arc(radius, 1.1, start, end, 46), 0.045, {
      color: STAINLESS,
      tags: tags('interior.pool.rail.top', 'guardrail', 'collision-rail', 'blender:separate'),
    }),
    r.pipe('interior.pool.rail.knee', arc(radius, 0.55, start, end, 46), 0.038, {
      color: STAINLESS,
      tags: tags('interior.pool.rail.knee', 'guardrail', 'collision-rail', 'blender:separate'),
    }),
  ];
  for (let i = 0; i < 20; i++) {
    const t = start + ((end - start) * i) / 19;
    const name = `interior.pool.rail.post.${String(i + 1).padStart(2, '0')}`;
    out.push(r.prop(name, p3(radius * Math.cos(t), 0, radius * Math.sin(t)), s3(0.09, 1.1, 0.09), {
      color: STAINLESS,
      tags: tags(name, 'guardrail', 'blender:separate'),
    }));
  }
  return out;
}

function bank(letter: 'A' | 'B', x: number): Entity[] {
  const key = letter.toLowerCase();
  const base = ['control-bank', `bank:${key}`, `query:control-bank-${key}`];
  const out: Entity[] = [
    r.prop(`interior.bank.${key}.ceiling-support`, p3(x, 12.8, 0), s3(2.5, 0.45, 2.5), {
      shape: 'cylinder', color: STEEL, collision: false,
      tags: tags(`interior.bank.${key}.ceiling-support`, ...base, 'fixed', 'blender:separate'),
    }),
    r.machine(`interior.bank.${key}.upper-housing`, `CONTROL BANK ${letter}`, p3(x, 9.6, 0), s3(2.0, 3.2, 2.0), {
      shape: 'cylinder', color: STAINLESS, collision: false,
      tags: tags(`interior.bank.${key}.upper-housing`, ...base, 'fixed', 'hero', 'blender:separate'),
    }),
    r.prop(`interior.bank.${key}.motor-band`, p3(x, 11.85, 0), s3(2.18, 0.42, 2.18), {
      shape: 'cylinder', color: DARK, collision: false,
      tags: tags(`interior.bank.${key}.motor-band`, ...base, 'fixed', 'blender:separate'),
    }),
    r.machine(`interior.bank.${key}.moving-carriage`, `BANK ${letter} MOVING CARRIAGE`, p3(x, 7.55, 0), s3(1.55, 1.65, 1.55), {
      shape: 'cylinder', color: BLUE_GREY, collision: false,
      tags: tags(`interior.bank.${key}.moving-carriage`, ...base, 'moving-y', 'scram-travel:1.8m', 'blender:separate'),
    }),
    r.prop(`interior.bank.${key}.drive-column`, p3(x, -0.9, 0), s3(0.48, 8.9, 0.48), {
      shape: 'cylinder', color: STAINLESS, collision: false,
      tags: tags(`interior.bank.${key}.drive-column`, ...base, 'moving-y', 'blender:separate'),
    }),
    r.machine(`interior.bank.${key}.submerged-guide`, `BANK ${letter} SUBMERGED GUIDE`, p3(x, -2.05, 0), s3(1.7, 1.35, 1.7), {
      shape: 'cylinder', color: STEEL, collision: false,
      tags: tags(`interior.bank.${key}.submerged-guide`, ...base, 'submerged', 'blender:separate'),
    }),
    r.prop(`interior.bank.${key}.status-screen`, p3(x, 10.25, 1.02), s3(0.7, 0.5, 0.1), {
      color: SCREEN, collision: false, label: `CONTROL BANK ${letter}`,
      tags: tags(`interior.bank.${key}.status-screen`, ...base, 'screen', 'emissive', 'blender:replaceable-screen'),
    }),
  ];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    const name = `interior.bank.${key}.guide.${i + 1}`;
    out.push(r.prop(name, p3(x + 0.62 * Math.cos(a), 9.1, 0.62 * Math.sin(a)), s3(0.14, 4.0, 0.14), {
      shape: 'cylinder', color: DARK, collision: false,
      tags: tags(name, ...base, 'fixed', 'blender:separate'),
    }));
  }
  return out;
}

function console(name: string, label: string, x: number, z: number, rot: number, w: number, dpt: number): Entity[] {
  return [
    r.machine(`${name}.body`, label, p3(x, 0, z), s3(w, 1.15, dpt), {
      rotationY: rot, color: GREEN_GREY,
      tags: tags(`${name}.body`, 'console', `query:${label.toLowerCase().replaceAll(' ', '-')}`, 'blender:separate'),
    }),
    r.prop(`${name}.screen`, p3(x, 1.18, z), s3(w * 0.55, 0.52, 0.08), {
      rotationY: rot, color: SCREEN, collision: false, label,
      tags: tags(`${name}.screen`, 'screen', 'emissive', 'blender:replaceable-screen'),
    }),
    r.prop(`${name}.switch-bank`, p3(x - 0.22, 0.98, z + 0.05), s3(w * 0.28, 0.12, 0.18), {
      rotationY: rot, color: BLACK, collision: false,
      tags: tags(`${name}.switch-bank`, 'switches', 'interactive-detail', 'blender:separate'),
    }),
  ];
}

function coolingTower(prefix: string, x: number, z: number, height = 28, baseR = 7.6, neckR = 3.5, topR = 5.0): Entity[] {
  const out: Entity[] = [];
  const segments = 18;
  for (let i = 0; i < segments; i++) {
    const y0 = (i / segments) * height;
    const y1 = ((i + 1) / segments) * height;
    const mid = (y0 + y1) / 2;
    const t = mid / height;
    const radius = t < 0.58
      ? baseR + (neckR - baseR) * (t / 0.58)
      : neckR + (topR - neckR) * ((t - 0.58) / 0.42);
    const name = `${prefix}.shell.${String(i + 1).padStart(2, '0')}`;
    out.push(r.prop(name, p3(x, mid, z), s3(radius * 2, y1 - y0 + 0.08, radius * 2), {
      shape: 'cylinder', color: CONCRETE, collision: i < 4,
      tags: tags(name, 'exterior', 'cooling-tower', 'hyperboloid', 'blender:separate'),
    }));
  }
  out.push(
    r.prop(`${prefix}.rim`, p3(x, height, z), s3(topR * 2.08, 0.45, topR * 2.08), {
      shape: 'cylinder', color: PALE, collision: false,
      tags: tags(`${prefix}.rim`, 'exterior', 'cooling-tower', 'blender:separate'),
    }),
    r.prop(`${prefix}.basin`, p3(x, -0.6, z), s3(baseR * 2.2, 0.9, baseR * 2.2), {
      shape: 'cylinder', color: '#8a999e',
      tags: tags(`${prefix}.basin`, 'exterior', 'cooling-tower', 'basin', 'blender:separate'),
    }),
  );
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    const sx = x + Math.cos(a) * 1.1;
    const sz = z + Math.sin(a) * 1.1;
    const name = `${prefix}.steam.${i + 1}`;
    out.push(r.prop(name, p3(sx, height + 0.8 + i * 0.45, sz), s3(2.6 + i * 0.18, 1.8, 2.6 + i * 0.18), {
      shape: 'cylinder', color: '#eef4f4', collision: false,
      tags: tags(name, 'exterior', 'steam', 'fx-anchor', 'blender:separate'),
    }));
  }
  return out;
}

function buildingExterior(): Entity[] {
  const out: Entity[] = [
    r.grade('exterior.site-pad', p3(0, -0.2, 18), s2(68, 86), { color: '#69767b', tags: tags('exterior.site-pad', 'exterior', 'site') }),
    r.prop('exterior.main-block', p3(0, 0, 0), s3(31, 15.5, 29), {
      color: WHITE, tags: tags('exterior.main-block', 'exterior', 'building-shell', 'blender:separate'),
      notes: 'Primary reactor building shell surrounding the compact interior hall.',
    }),
    r.prop('exterior.containment-drum', p3(0, 0, 0), s3(24, 19, 24), {
      shape: 'cylinder', color: PALE, collision: false,
      tags: tags('exterior.containment-drum', 'exterior', 'containment', 'hero', 'blender:separate'),
    }),
    r.prop('exterior.containment-cap.1', p3(0, 18.0, 0), s3(20, 1.2, 20), {
      shape: 'cylinder', color: PALE, collision: false,
      tags: tags('exterior.containment-cap.1', 'exterior', 'containment', 'roof', 'blender:separate'),
    }),
    r.prop('exterior.containment-cap.2', p3(0, 19.0, 0), s3(14, 1.1, 14), {
      shape: 'cylinder', color: WHITE, collision: false,
      tags: tags('exterior.containment-cap.2', 'exterior', 'containment', 'roof', 'blender:separate'),
    }),
    r.prop('exterior.turbine-annex', p3(24, 0, 2), s3(17, 10, 28), {
      color: '#b9c3c7', tags: tags('exterior.turbine-annex', 'exterior', 'annex', 'turbine-hall', 'blender:separate'),
    }),
    r.prop('exterior.control-annex', p3(-22, 0, -2), s3(13, 8, 22), {
      color: '#c7d0d4', tags: tags('exterior.control-annex', 'exterior', 'annex', 'control', 'blender:separate'),
    }),
    r.prop('exterior.service-annex', p3(3, 0, 22), s3(24, 7, 12), {
      color: '#aebbc0', tags: tags('exterior.service-annex', 'exterior', 'annex', 'service', 'blender:separate'),
    }),
    r.doorway('exterior.main-entry', p3(-13.8, 0, 4), d(3.0), 3.8, { rotationY: 90, label: 'REACTOR BUILDING ENTRY' }),
    r.doorway('exterior.loading-entry', p3(15.5, 0, -6), d(4.5), 4.8, { rotationY: 90, label: 'FUEL / SERVICE ACCESS' }),
    r.pipe('exterior.pipebridge.supply', [p3(14, 8.5, 8), p3(32, 8.5, 8), p3(32, 5, 30)], d(0.38), {
      color: WHITE, tags: tags('exterior.pipebridge.supply', 'exterior', 'pipe', 'coolant-supply', 'blender:separate'),
    }),
    r.pipe('exterior.pipebridge.return', [p3(14, 7.3, 10), p3(28, 7.3, 10), p3(28, 4.5, 30)], d(0.32), {
      color: '#b9d4df', tags: tags('exterior.pipebridge.return', 'exterior', 'pipe', 'coolant-return', 'blender:separate'),
    }),
    r.machine('exterior.transformer-yard', 'TRANSFORMER YARD', p3(31, 0, -19), s3(13, 4.5, 12), {
      color: '#6e7f84', tags: tags('exterior.transformer-yard', 'exterior', 'electrical', 'blender:separate'),
    }),
    r.machine('exterior.ventilation-house', 'VENTILATION / FILTER HOUSE', p3(-20, 0, 17), s3(12, 7, 10), {
      color: BLUE_GREY, tags: tags('exterior.ventilation-house', 'exterior', 'ventilation', 'blender:separate'),
    }),
    r.prop('exterior.vent-stack', p3(-20, 7, 17), s3(3.2, 18, 3.2), {
      shape: 'cylinder', color: '#8f9ba0', collision: false,
      tags: tags('exterior.vent-stack', 'exterior', 'ventilation', 'stack', 'blender:separate'),
    }),
    r.landmark('exterior.label.main', p3(0, 11, -15.2), 'REACTOR BUILDING', { size: 1.4, color: '#dde5e8' }),
    r.landmark('exterior.label.cooling', p3(0, 7, 38), 'COOLING TOWERS / STEAM PLUME', { size: 1.2, color: '#d8e4e7' }),
    r.spawn('spawn.exterior', p3(-18, 0, -20), 'Reactor building exterior', { rotationY: 35 }),
  ];
  out.push(...coolingTower('exterior.cooling-tower.a', -12, 42));
  out.push(...coolingTower('exterior.cooling-tower.b', 12, 42));
  for (let i = 0; i < 6; i++) {
    out.push(r.prop(`exterior.roof.ahu.${i + 1}`, p3(-10 + i * 4, 15.5, -7), s3(2.2, 1.6, 3.0), {
      color: STEEL, collision: false,
      tags: tags(`exterior.roof.ahu.${i + 1}`, 'exterior', 'roof-equipment', 'air-handler', 'blender:separate'),
    }));
  }
  return out;
}

function interiorShell(): Entity[] {
  return [
    ...radialRing('interior.floor.service-ring', 3.9, 7.0, 0, 0.28, 32, FLOOR, true),
    ...radialRing('interior.pool.rim', 3.4, 3.9, 0.12, 0.42, 32, STAINLESS, false),
    ...shaftPanels(),
    r.prop('interior.pool.water', p3(0, -0.45, 0), s3(6.8, 0.06, 6.8), {
      shape: 'cylinder', color: CORE, collision: false,
      tags: tags('interior.pool.water', 'pool', 'water', 'hero', 'blender:separate'),
    }),
    r.prop('interior.pool.core-glow', p3(0, -5.75, 0), s3(3.8, 0.45, 3.8), {
      shape: 'cylinder', color: CORE_WHITE, collision: false,
      tags: tags('interior.pool.core-glow', 'pool', 'emissive', 'core', 'fx-anchor', 'blender:separate'),
    }),
    r.prop('interior.pool.lower-reactor', p3(0, -5.3, 0), s3(4.6, 1.3, 4.6), {
      shape: 'cylinder', color: STEEL, collision: false,
      tags: tags('interior.pool.lower-reactor', 'pool', 'submerged', 'reactor-core', 'blender:separate'),
    }),
    ...poolRails(),
    ...bank('A', -1.4),
    ...bank('B', 1.4),
    r.prop('interior.ceiling.bank-beam', p3(0, 13.25, 0), s3(8.4, 0.55, 1.2), {
      color: DARK, collision: false,
      tags: tags('interior.ceiling.bank-beam', 'ceiling', 'structural', 'blender:separate'),
    }),
    r.stair('interior.front-stair', p3(0, -0.45, 5.3), p3(0, 0, 7.2), d(1.8), { railings: false, tags: tags('interior.front-stair', 'stairs', 'blender:separate') }),
    r.machine('interior.scram.body', 'EMERGENCY SHUTDOWN', p3(0, 0, 6.35), s3(2.2, 1.15, 0.85), {
      color: WHITE, tags: tags('interior.scram.body', 'emergency', 'scram', 'query:emergency-shutdown', 'blender:separate'),
    }),
    r.prop('interior.scram.handle', p3(0, 1.0, 6.15), s3(0.26, 0.55, 0.22), {
      color: RED, collision: false, label: 'SCRAM HANDLE',
      tags: tags('interior.scram.handle', 'interactive', 'scram', 'animation:rotate', 'blender:separate'),
    }),
    r.machine('interior.fuel-cart', 'FUEL HANDLING POSITION', p3(-4.7, 0, 6.2), s3(1.25, 1.05, 0.85), {
      color: '#8d7a47', tags: tags('interior.fuel-cart', 'fuel-handling', 'movable', 'blender:separate'),
    }),
    r.machine('interior.sampling-station', 'SAMPLING STATION', p3(4.6, 0, 6.25), s3(1.25, 1.2, 0.75), {
      color: BLUE_GREY, tags: tags('interior.sampling-station', 'sampling', 'interactive', 'blender:separate'),
    }),
    ...console('interior.console.front-left', 'ROD CONTROL / SIGNAL', -7.0, 6.4, -12, 3.0, 1.3),
    ...console('interior.console.front-right', 'CORE STATUS / GRID', 7.0, 6.4, 12, 3.5, 1.4),
    ...console('interior.console.north-left', 'FUEL RECEIVING', -6.5, -6.6, 0, 2.4, 1.0),
    ...console('interior.console.north-right', 'REACTIVITY CONTROL', 5.7, -6.6, 0, 2.8, 1.0),
    ...console('interior.console.east', 'TURBINE / BREAKERS', 8.3, 0.5, 90, 3.0, 1.0),
    ...console('interior.console.west', 'COOLING / RESERVE', -8.3, 0.5, -90, 3.0, 1.0),
    r.machine('interior.tank.1', 'COOLANT BUFFER A', p3(8.1, 0, -5.3), s3(1.6, 3.0, 1.6), { shape: 'cylinder', color: GREEN_GREY, tags: tags('interior.tank.1', 'tank', 'blender:separate') }),
    r.machine('interior.tank.2', 'COOLANT BUFFER B', p3(9.8, 0, -5.3), s3(1.4, 2.6, 1.4), { shape: 'cylinder', color: GREEN_GREY, tags: tags('interior.tank.2', 'tank', 'blender:separate') }),
    r.pipe('interior.pipe.coolant-supply', [p3(-10, 10.8, -8), p3(10, 10.8, -8), p3(10, 4.2, -4)], d(0.28), { color: WHITE, tags: tags('interior.pipe.coolant-supply', 'pipe', 'coolant-supply', 'blender:separate') }),
    r.pipe('interior.pipe.coolant-return', [p3(-10, 9.5, -10), p3(-10, 9.5, 2), p3(-7, 4.2, 2)], d(0.24), { color: '#b9d4df', tags: tags('interior.pipe.coolant-return', 'pipe', 'coolant-return', 'blender:separate') }),
    r.pipe('interior.pipe.sampling-line', [p3(10, 8.7, -6), p3(10, 8.7, 5), p3(4.7, 1.2, 6.2)], d(0.10), { color: WHITE, tags: tags('interior.pipe.sampling-line', 'pipe', 'sampling-line', 'blender:separate') }),
    r.light('interior.light.pool', p3(0, 4.3, 0), { size: [2.0, 2.0], color: CORE, cast: true, intensity: 210, distance: 24, tags: tags('interior.light.pool', 'light', 'pool') }),
    r.light('interior.light.north', p3(0, 13.8, -7.5), { size: [5, 0.8], cast: true, intensity: 210, distance: 30, tags: tags('interior.light.north', 'light', 'ceiling') }),
    r.light('interior.light.south', p3(0, 13.8, 7.5), { size: [5, 0.8], cast: true, intensity: 210, distance: 30, tags: tags('interior.light.south', 'light', 'ceiling') }),
    r.landmark('interior.label.coolant-supply', p3(8.0, 11.6, -8), 'COOLANT SUPPLY', { size: 0.75, color: WHITE }),
    r.landmark('interior.label.coolant-return', p3(-9.4, 10.3, -5), 'COOLANT RETURN', { size: 0.75, color: WHITE }),
    r.landmark('interior.label.pool', p3(0, 2.5, 0), '6.8 m REACTOR POOL / DUAL CONTROL BANKS', { size: 0.9, color: CORE }),
    r.spawn('spawn.floor', p3(0, 0, 9.5), 'Reactor floor', { rotationY: 180 }),
    r.spawn('spawn.pool', p3(-5.7, 0, 2.0), 'Reactor pool', { rotationY: 75 }),
  ];
}

function controlInterior(): Entity[] {
  return [
    c.floor('building.control.floor', p3(-10.8, 5.5, -4.5), s2(5.4, 8.4), { color: FLOOR, tags: tags('building.control.floor', 'control-room', 'walkable') }),
    c.prop('building.control.glass', p3(-8.05, 5.5, -4.5), s3(0.10, 2.8, 5.4), {
      color: '#9fd8ea', collision: false,
      tags: tags('building.control.glass', 'glass', 'control-room-window', 'blender:separate'),
    }),
    ...console('building.control.desk.1', 'CORE STATUS', -11.8, -6.2, 90, 2.0, 0.9),
    ...console('building.control.desk.2', 'GRID / TURBINE', -11.8, -3.8, 90, 2.0, 0.9),
    c.prop('building.control.chair.1', p3(-10.2, 5.5, -6.2), s3(0.7, 1.0, 0.7), { color: DARK, tags: tags('building.control.chair.1', 'control-room', 'chair') }),
    c.prop('building.control.chair.2', p3(-10.2, 5.5, -3.8), s3(0.7, 1.0, 0.7), { color: DARK, tags: tags('building.control.chair.2', 'control-room', 'chair') }),
    c.landmark('building.control.label', p3(-8.2, 8.6, -4.5), 'REACTOR CONTROL / SECURE AREA', { size: 0.7, color: WHITE }),
    c.spawn('spawn.control', p3(-10.5, 5.5, -4.5), 'Reactor control room', { rotationY: 90 }),
  ];
}

export const REACTOR_BUILDING_ENTITIES: Entity[] = [
  ...buildingExterior(),
  ...interiorShell(),
];

export const REACTOR_BUILDING_CONTROL_ENTITIES: Entity[] = controlInterior();
