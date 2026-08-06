import type { Entity, Vec2, Vec3 } from '../schema';
import { zoneAuthor } from './authoring';

/**
 * Finished-scale visual dressing for the reactor hall.
 *
 * Facility data is authored at the draft plan scale and then compacted by
 * SITE_SCALE=0.6. Helpers below accept FINAL in-game X/Z dimensions so the
 * numbers in docs/REACTOR_ROOM_VISUAL_SPEC.md can be copied directly without
 * mental rescaling. Y dimensions and clearances are never scaled by the
 * facility compactor.
 *
 * Every important part is a separate Entity with a stable semantic id and
 * machine-readable tags. The Three.js build therefore remains useful as a
 * browser walk-through, an MCP inspection surface and a GLB source for later
 * Blender work.
 */
const a = zoneAuthor('reactor');
const c = zoneAuthor('control');
const PLAN_SCALE = 0.6;
const draft = (n: number) => n / PLAN_SCALE;
const p3 = (x: number, y: number, z: number): Vec3 => [draft(x), y, draft(z)];
const s2 = (x: number, z: number): Vec2 => [draft(x), draft(z)];
const s3 = (x: number, y: number, z: number): Vec3 => [draft(x), y, draft(z)];
const degrees = (radians: number) => (radians * 180) / Math.PI;

const SHELL = '#d7dde0';
const FLOOR = '#8e999f';
const STEEL = '#7f8b91';
const STAINLESS = '#b8c1c5';
const BLUE_GREY = '#738d96';
const GREEN_GREY = '#71877e';
const DARK = '#29343a';
const SCREEN = '#39bad0';
const CORE_BLUE = '#36d9ff';
const CORE_WHITE = '#c7f6ff';
const PIPE_WHITE = '#dbe3e5';
const HAZARD = '#d16d32';
const RED = '#b84936';
const GREEN = '#64c58d';
const YELLOW = '#d9b74c';

const semantic = (name: string, ...rest: string[]) => [
  'reactor-visual',
  `asset:${name}`,
  ...rest,
];

function radialSegments(
  prefix: string,
  innerRadius: number,
  outerRadius: number,
  y: number,
  thickness: number,
  count: number,
  color: string,
  tags: string[],
  walkable: boolean,
): Entity[] {
  const entities: Entity[] = [];
  const radius = (innerRadius + outerRadius) / 2;
  const radial = outerRadius - innerRadius;
  // Tangent length of the polygonal chord, with a small overlap so the ring
  // never opens pinholes between neighbouring modules in the browser build.
  const tangent = 2 * radius * Math.tan(Math.PI / count) * 1.035;
  for (let i = 0; i < count; i++) {
    const theta = (i / count) * Math.PI * 2;
    const x = radius * Math.cos(theta);
    const z = radius * Math.sin(theta);
    const rotationY = degrees(Math.PI / 2 - theta);
    const name = `${prefix}.${String(i + 1).padStart(2, '0')}`;
    if (walkable) {
      entities.push(
        a.floor(name, p3(x, y, z), s2(tangent, radial), {
          thickness,
          rotationY,
          color,
          tags: semantic(name, ...tags, 'blender:walkable-module'),
          notes: `Radial ring module ${i + 1}/${count}; final radius ${radius.toFixed(3)} m.`,
        }),
      );
    } else {
      entities.push(
        a.prop(name, p3(x, y - thickness, z), s3(tangent, thickness, radial), {
          rotationY,
          color,
          collision: false,
          tags: semantic(name, ...tags, 'blender:static-module'),
          notes: `Radial decorative module ${i + 1}/${count}.`,
        }),
      );
    }
  }
  return entities;
}

function shaftPanels(count = 32): Entity[] {
  const entities: Entity[] = [];
  const radius = 3.47;
  const radialThickness = 0.16;
  const tangent = 2 * radius * Math.tan(Math.PI / count) * 1.04;
  for (let i = 0; i < count; i++) {
    const theta = (i / count) * Math.PI * 2;
    const x = radius * Math.cos(theta);
    const z = radius * Math.sin(theta);
    const rotationY = degrees(Math.PI / 2 - theta);
    const name = `pool.shaft.panel.${String(i + 1).padStart(2, '0')}`;
    entities.push(
      a.prop(name, p3(x, -6.5, z), s3(tangent, 6.05, radialThickness), {
        rotationY,
        color: i % 2 === 0 ? '#b7d0d7' : '#a9c2c9',
        tags: semantic(name, 'pool', 'shaft', 'submerged', 'blender:POOL_SHAFT_PANEL'),
        notes: 'Segmented pool liner from Y=-6.50 m to waterline Y=-0.45 m.',
      }),
    );
  }
  return entities;
}

function arcPoints(radius: number, y: number, start: number, end: number, steps: number): Vec3[] {
  const points: Vec3[] = [];
  for (let i = 0; i <= steps; i++) {
    const theta = start + ((end - start) * i) / steps;
    points.push(p3(radius * Math.cos(theta), y, radius * Math.sin(theta)));
  }
  return points;
}

function poolRails(): Entity[] {
  const radius = 3.90;
  const gateWidth = 1.40;
  const halfGate = Math.asin(Math.min(0.95, gateWidth / (2 * radius)));
  const south = Math.PI / 2;
  const start = south + halfGate;
  const end = south - halfGate + Math.PI * 2;
  const top = a.pipe('pool.rail.top', arcPoints(radius, 1.10, start, end, 42), 0.045, {
    color: STAINLESS,
    tags: semantic('pool.rail.top', 'pool', 'guardrail', 'collision-rail', 'blender:POOL_RAIL_TOP'),
    notes: '1.10 m guardrail top rail; exact 1.40 m south service gate intentionally omitted.',
  });
  const knee = a.pipe('pool.rail.knee', arcPoints(radius, 0.56, start, end, 42), 0.04, {
    color: STAINLESS,
    tags: semantic('pool.rail.knee', 'pool', 'guardrail', 'collision-rail', 'blender:POOL_RAIL_KNEE'),
  });
  const posts: Entity[] = [];
  const count = 18;
  const span = end - start;
  for (let i = 0; i <= count; i++) {
    const theta = start + (span * i) / count;
    const x = radius * Math.cos(theta);
    const z = radius * Math.sin(theta);
    const name = `pool.rail.post.${String(i + 1).padStart(2, '0')}`;
    posts.push(
      a.prop(name, p3(x, 0, z), s3(0.09, 1.10, 0.09), {
        color: STAINLESS,
        tags: semantic(name, 'pool', 'guardrail', 'blender:POOL_RAIL_POST'),
      }),
    );
  }
  return [top, knee, ...posts];
}

function bank(letter: 'A' | 'B', x: number): Entity[] {
  const key = letter.toLowerCase();
  const baseTags = ['control-bank', `bank:${key}`, `blender:BANK_${letter}`];
  const entities: Entity[] = [
    a.machine(`bank.${key}.fixed.housing`, `CONTROL BANK ${letter}`, p3(x, 9.8, 0), s3(1.8, 2.6, 1.8), {
      shape: 'cylinder',
      color: STAINLESS,
      collision: false,
      tags: semantic(`bank.${key}.fixed.housing`, ...baseTags, 'animation:fixed', `blender:BANK_${letter}_FIXED_HOUSING`),
      notes: 'Fixed upper actuator housing. Never translate during SCRAM.',
    }),
    a.prop(`bank.${key}.fixed.top-collar`, p3(x, 12.35, 0), s3(2.02, 0.28, 2.02), {
      shape: 'cylinder',
      color: STEEL,
      collision: false,
      tags: semantic(`bank.${key}.fixed.top-collar`, ...baseTags, 'animation:fixed'),
    }),
    a.prop(`bank.${key}.fixed.lower-collar`, p3(x, 9.52, 0), s3(2.02, 0.30, 2.02), {
      shape: 'cylinder',
      color: STEEL,
      collision: false,
      tags: semantic(`bank.${key}.fixed.lower-collar`, ...baseTags, 'animation:fixed'),
    }),
    a.machine(`bank.${key}.moving.carriage`, `BANK ${letter} MOVING CARRIAGE`, p3(x, 7.95, 0), s3(1.45, 1.55, 1.45), {
      shape: 'cylinder',
      color: BLUE_GREY,
      collision: false,
      tags: semantic(`bank.${key}.moving.carriage`, ...baseTags, 'animation:moving-y', 'scram-travel:1.80m', `blender:BANK_${letter}_MOVING_CARRIAGE`),
      notes: 'Nominal moving carriage. Blender/Unity pivot must remain on bank axis; usable vertical travel 1.80 m.',
    }),
    a.prop(`bank.${key}.moving.upper-collar`, p3(x, 9.42, 0), s3(1.64, 0.22, 1.64), {
      shape: 'cylinder',
      color: STAINLESS,
      collision: false,
      tags: semantic(`bank.${key}.moving.upper-collar`, ...baseTags, 'animation:moving-y'),
    }),
    a.prop(`bank.${key}.moving.lower-collar`, p3(x, 7.72, 0), s3(1.64, 0.24, 1.64), {
      shape: 'cylinder',
      color: STAINLESS,
      collision: false,
      tags: semantic(`bank.${key}.moving.lower-collar`, ...baseTags, 'animation:moving-y'),
    }),
    a.prop(`bank.${key}.drive-column`, p3(x, -1.15, 0), s3(0.46, 9.15, 0.46), {
      shape: 'cylinder',
      color: STAINLESS,
      collision: false,
      tags: semantic(`bank.${key}.drive-column`, ...baseTags, 'animation:moving-y', `blender:BANK_${letter}_DRIVE_COLUMN`),
      notes: 'Single readable drive column representing an absorber bank, not one literal control rod.',
    }),
    a.machine(`bank.${key}.submerged.guide`, `BANK ${letter} SUBMERGED GUIDE`, p3(x, -2.0, 0), s3(1.45, 1.35, 1.45), {
      shape: 'cylinder',
      color: STEEL,
      collision: false,
      tags: semantic(`bank.${key}.submerged.guide`, ...baseTags, 'submerged', `blender:BANK_${letter}_SUBMERGED_GUIDE`),
    }),
    a.prop(`bank.${key}.status.panel`, p3(x, 10.50, 0.91), s3(0.58, 0.48, 0.12), {
      color: DARK,
      collision: false,
      label: `BANK ${letter} STATUS`,
      tags: semantic(`bank.${key}.status.panel`, ...baseTags, 'screen', 'blender:SCREEN_REPLACEABLE'),
    }),
    a.prop(`bank.${key}.status.ready`, p3(x - 0.14, 10.64, 0.99), s3(0.12, 0.12, 0.06), {
      color: GREEN,
      collision: false,
      tags: semantic(`bank.${key}.status.ready`, ...baseTags, 'emissive', 'status-lamp', 'blender:STATUS_LAMP'),
    }),
    a.prop(`bank.${key}.status.warn`, p3(x + 0.14, 10.64, 0.99), s3(0.12, 0.12, 0.06), {
      color: HAZARD,
      collision: false,
      tags: semantic(`bank.${key}.status.warn`, ...baseTags, 'emissive', 'status-lamp', 'blender:STATUS_LAMP'),
    }),
  ];

  // Four fixed guide columns give the upper actuator believable support while
  // keeping the two-bank silhouette readable from the floor.
  for (const [i, dx] of [-0.48, -0.16, 0.16, 0.48].entries()) {
    const name = `bank.${key}.fixed.guide.${i + 1}`;
    entities.push(
      a.prop(name, p3(x + dx, 12.35, -0.42), s3(0.16, 1.85, 0.16), {
        shape: 'cylinder',
        color: STEEL,
        collision: false,
        tags: semantic(name, ...baseTags, 'animation:fixed', 'blender:GUIDE_COLUMN'),
      }),
    );
  }
  return entities;
}

function screen(
  name: string,
  label: string,
  x: number,
  y: number,
  z: number,
  rotationY: number,
  width = 0.72,
  height = 0.48,
): Entity {
  return a.prop(name, p3(x, y, z), s3(width, height, 0.08), {
    rotationY,
    color: SCREEN,
    collision: false,
    label,
    tags: semantic(name, 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE', `query:${label.toLowerCase().replaceAll(' ', '-')}`),
  });
}

function controlDetail(): Entity[] {
  return [
    // North: fuel receiving / reactivity.
    screen('console.north.fuel-screen', 'FUEL RECEIVING STATUS', -4.2, 1.55, -6.65, 0, 0.82, 0.54),
    screen('console.north.bank-screen', 'REACTIVITY / BANK POSITION', 2.4, 1.52, -6.66, 0, 1.05, 0.58),
    a.prop('console.north.bank-lever', p3(2.9, 1.0, -6.62), s3(0.18, 0.52, 0.18), {
      color: YELLOW,
      collision: false,
      label: 'CONTROL BANK COMMAND LEVER',
      tags: semantic('console.north.bank-lever', 'interactive', 'lever', 'animation:rotate', 'blender:CONTROL_BANK_LEVER'),
    }),
    // North-east: waste / venting.
    screen('console.ne.waste-screen', 'WASTE TRANSFER', 7.1, 1.55, -6.68, -25, 0.72, 0.48),
    a.prop('console.ne.vent-wheel', p3(7.95, 1.03, -4.35), s3(0.48, 0.12, 0.48), {
      shape: 'cylinder',
      rotationY: 90,
      color: RED,
      collision: false,
      label: 'CONTAINMENT VENT HANDWHEEL',
      tags: semantic('console.ne.vent-wheel', 'interactive', 'valve', 'animation:rotate', 'blender:VENT_VALVE_WHEEL'),
    }),
    // East: turbine / grid / demand.
    screen('console.east.grid-demand-screen', 'GRID DEMAND', 6.55, 1.48, -4.42, 90, 0.92, 0.54),
    screen('console.east.breaker-screen', 'GRID BREAKER STATUS', 8.38, 1.55, -1.80, 90, 0.72, 0.52),
    screen('console.east.turbine-screen', 'TURBINE OUTPUT', 6.62, 1.56, 2.70, 90, 0.88, 0.54),
    a.prop('console.east.turbine-throttle-handle', p3(6.38, 1.02, 3.50), s3(0.20, 0.72, 0.20), {
      color: RED,
      collision: false,
      label: 'TURBINE THROTTLE HANDLE',
      tags: semantic('console.east.turbine-throttle-handle', 'interactive', 'lever', 'animation:rotate', 'blender:TURBINE_THROTTLE_HANDLE'),
    }),
    // South: cooling and emergency response.
    screen('console.south.pump-screen', 'COOLANT PUMP STATUS', -4.75, 1.50, 6.70, 180, 0.86, 0.54),
    screen('console.south.valve-screen', 'COOLANT VALVE POSITION', -1.20, 1.42, 7.32, 180, 0.84, 0.52),
    screen('console.south.emergency-cooling-screen', 'EMERGENCY COOLING', 3.10, 1.50, 6.72, 180, 0.92, 0.54),
    // West: backup, reserve and live repair.
    screen('console.west.backup-screen', 'BACKUP GENERATOR', -7.62, 1.48, 4.18, -90, 0.84, 0.52),
    screen('console.west.reserve-screen', 'RESERVE POWER', -8.44, 1.44, -1.10, -90, 0.78, 0.50),
    screen('console.west.repair-screen', 'LIVE REPAIR BAY', -7.45, 1.40, -5.18, -90, 0.72, 0.48),
  ];
}

function emergencyAndService(): Entity[] {
  return [
    a.machine('emergency.console', 'EMERGENCY SHUTDOWN', p3(0, 0, 5.62), s3(1.65, 1.20, 0.78), {
      color: BLUE_GREY,
      tags: semantic('emergency.console', 'emergency', 'south', 'blender:EMERGENCY_CONSOLE'),
      notes: 'Pool-side emergency console replacing the old central-south greybox island.',
    }),
    a.prop('emergency.scram.handle', p3(0, 1.02, 5.16), s3(0.24, 0.55, 0.22), {
      color: RED,
      collision: false,
      label: 'SCRAM / EMERGENCY SHUTDOWN',
      tags: semantic('emergency.scram.handle', 'interactive', 'scram', 'animation:rotate', 'blender:SCRAM_HANDLE'),
      notes: 'Separate, animation-ready emergency control. Keep readable from first-person distance.',
    }),
    a.prop('emergency.alarm-ack', p3(-0.48, 1.04, 5.16), s3(0.20, 0.16, 0.18), {
      color: YELLOW,
      collision: false,
      label: 'ALARM ACKNOWLEDGE',
      tags: semantic('emergency.alarm-ack', 'interactive', 'alarm', 'blender:ALARM_ACK_BUTTON'),
    }),
    a.prop('emergency.auto-bypass', p3(0.48, 1.04, 5.16), s3(0.20, 0.16, 0.18), {
      color: HAZARD,
      collision: false,
      label: 'AUTO SHUTDOWN BYPASS',
      tags: semantic('emergency.auto-bypass', 'interactive', 'shortcut', 'blender:AUTO_SHUTDOWN_BYPASS'),
    }),
    a.prop('fuel-handling.cart.body', p3(-2.75, 0, 5.85), s3(1.25, 0.72, 0.85), {
      color: GREEN_GREY,
      label: 'FUEL HANDLING CART',
      tags: semantic('fuel-handling.cart.body', 'fuel-handling', 'movable', 'animation:translate', 'blender:FUEL_CART_BODY'),
    }),
    a.prop('fuel-handling.cart.rack', p3(-2.75, 0.70, 5.85), s3(0.94, 0.48, 0.62), {
      color: DARK,
      collision: false,
      tags: semantic('fuel-handling.cart.rack', 'fuel-handling', 'blender:FUEL_CART_RACK'),
    }),
    a.prop('fuel-handling.cart.wheel.lf', p3(-3.18, 0.08, 5.55), s3(0.24, 0.24, 0.12), {
      shape: 'cylinder', rotationY: 90, color: DARK, collision: false,
      tags: semantic('fuel-handling.cart.wheel.lf', 'fuel-handling', 'animation:rotate', 'blender:FUEL_CART_WHEEL'),
    }),
    a.prop('fuel-handling.cart.wheel.rf', p3(-2.32, 0.08, 5.55), s3(0.24, 0.24, 0.12), {
      shape: 'cylinder', rotationY: 90, color: DARK, collision: false,
      tags: semantic('fuel-handling.cart.wheel.rf', 'fuel-handling', 'animation:rotate', 'blender:FUEL_CART_WHEEL'),
    }),
    a.prop('fuel-handling.cart.wheel.lr', p3(-3.18, 0.08, 6.14), s3(0.24, 0.24, 0.12), {
      shape: 'cylinder', rotationY: 90, color: DARK, collision: false,
      tags: semantic('fuel-handling.cart.wheel.lr', 'fuel-handling', 'animation:rotate', 'blender:FUEL_CART_WHEEL'),
    }),
    a.prop('fuel-handling.cart.wheel.rr', p3(-2.32, 0.08, 6.14), s3(0.24, 0.24, 0.12), {
      shape: 'cylinder', rotationY: 90, color: DARK, collision: false,
      tags: semantic('fuel-handling.cart.wheel.rr', 'fuel-handling', 'animation:rotate', 'blender:FUEL_CART_WHEEL'),
    }),
    a.machine('sampling.station', 'SAMPLING STATION', p3(2.65, 0, 5.88), s3(0.80, 1.05, 0.60), {
      color: BLUE_GREY,
      tags: semantic('sampling.station', 'sampling', 'south', 'blender:SAMPLING_STATION'),
    }),
    a.pipe('sampling.line.local', [p3(2.65, 0.92, 5.72), p3(2.65, 1.75, 6.80), p3(4.10, 2.05, 6.80)], 0.07, {
      color: PIPE_WHITE,
      collision: false,
      tags: semantic('sampling.line.local', 'sampling', 'pipe', 'blender:SAMPLING_LINE'),
    }),
  ];
}

function overheadAndPipework(): Entity[] {
  return [
    // Major overhead support silhouette for the two hero actuators.
    a.prop('bank.support.crossbeam', p3(0, 13.92, 0), s3(6.2, 0.50, 0.68), {
      color: STEEL,
      collision: false,
      label: 'CONTROL BANK SUPPORT GANTRY',
      tags: semantic('bank.support.crossbeam', 'overhead', 'structure', 'blender:BANK_SUPPORT_CROSSBEAM'),
    }),
    a.prop('bank.support.beam.n', p3(0, 13.60, -1.55), s3(5.5, 0.34, 0.34), {
      color: STEEL, collision: false,
      tags: semantic('bank.support.beam.n', 'overhead', 'structure'),
    }),
    a.prop('bank.support.beam.s', p3(0, 13.60, 1.55), s3(5.5, 0.34, 0.34), {
      color: STEEL, collision: false,
      tags: semantic('bank.support.beam.s', 'overhead', 'structure'),
    }),
    // Spec-compliant 0.30-0.45 m primary coolant families.
    a.pipe('pipe.coolant-supply.main', [p3(9.4, 10.7, -7.1), p3(4.8, 10.7, -7.1), p3(4.8, 8.2, -5.5)], 0.38, {
      color: PIPE_WHITE,
      label: 'COOLANT SUPPLY',
      tags: semantic('pipe.coolant-supply.main', 'pipe', 'coolant-supply', 'blender:COOLANT_SUPPLY'),
    }),
    a.pipe('pipe.coolant-return.main', [p3(-9.4, 10.4, -7.0), p3(-5.0, 10.4, -7.0), p3(-5.0, 8.0, -5.4)], 0.38, {
      color: PIPE_WHITE,
      label: 'COOLANT RETURN',
      tags: semantic('pipe.coolant-return.main', 'pipe', 'coolant-return', 'blender:COOLANT_RETURN'),
    }),
    a.pipe('pipe.vent-relief.main', [p3(7.7, 7.5, -4.2), p3(8.8, 8.7, -4.2), p3(8.8, 11.0, -1.5)], 0.18, {
      color: PIPE_WHITE,
      tags: semantic('pipe.vent-relief.main', 'pipe', 'vent-relief', 'blender:VENT_RELIEF'),
    }),
    a.pipe('pipe.cable-conduit.west', [p3(-8.8, 6.0, -4.8), p3(-8.8, 8.5, -4.8), p3(-3.6, 8.5, -4.8)], 0.11, {
      color: DARK, collision: false,
      tags: semantic('pipe.cable-conduit.west', 'conduit', 'power', 'blender:CABLE_CONDUIT'),
    }),
  ];
}

function tanksAndInstrumentation(): Entity[] {
  const entities: Entity[] = [];
  for (const [i, x] of [6.55, 7.45, 8.35].entries()) {
    const name = `instrument.tank.${i + 1}`;
    entities.push(
      a.machine(name, i === 0 ? 'COOLANT SAMPLE VESSEL' : `AUX VESSEL ${i + 1}`, p3(x, 0, 6.55), s3(0.72, 2.25 + i * 0.12, 0.72), {
        shape: 'cylinder',
        color: i === 0 ? GREEN_GREY : BLUE_GREY,
        tags: semantic(name, 'vessel', 'instrumentation', 'blender:VERTICAL_VESSEL'),
      }),
    );
    entities.push(
      a.prop(`${name}.lid`, p3(x, 2.24 + i * 0.12, 6.55), s3(0.82, 0.16, 0.82), {
        shape: 'cylinder', color: STAINLESS, collision: false,
        tags: semantic(`${name}.lid`, 'vessel', 'animation:removable', 'blender:VESSEL_LID'),
      }),
    );
  }
  entities.push(
    screen('instrument.containment-monitor', 'CONTAINMENT MONITOR / RADIATION', 8.65, 3.05, 4.95, 90, 1.25, 0.72),
    a.prop('instrument.radiation-sensor', p3(8.90, 1.15, 4.10), s3(0.28, 0.62, 0.28), {
      color: DARK,
      label: 'RADIATION SENSOR',
      tags: semantic('instrument.radiation-sensor', 'sensor', 'radiation', 'blender:RADIATION_SENSOR'),
    }),
  );
  return entities;
}

function aiMarkers(): Entity[] {
  return [
    a.marker('ai.pool.water', p3(-3.1, 0, 0), 'objective', 'AI: POOL WATER Ø6.80 m · SURFACE Y=-0.45'),
    a.marker('ai.pool.rim', p3(-3.9, 0, 1.6), 'objective', 'AI: STRUCTURAL POOL RIM Ø7.80 m'),
    a.marker('ai.pool.service-ring', p3(-5.0, 0, 2.1), 'objective', 'AI: SERVICE RING Ø10.40 m · KEEP ≥1.20 m CLEAR'),
    a.marker('ai.bank-a', p3(-1.4, 0, -1.1), 'interaction', 'AI: CONTROL BANK A · X=-1.40 · SCRAM TRAVEL 1.80 m'),
    a.marker('ai.bank-b', p3(1.4, 0, -1.1), 'interaction', 'AI: CONTROL BANK B · X=+1.40 · SCRAM TRAVEL 1.80 m'),
    a.marker('ai.scram', p3(0, 0, 5.2), 'interaction', 'AI: EMERGENCY SHUTDOWN / SCRAM'),
    a.marker('ai.fuel-cart', p3(-2.75, 0, 5.35), 'interaction', 'AI: FUEL HANDLING CART · MOVABLE'),
    a.marker('ai.sampling', p3(2.65, 0, 5.35), 'interaction', 'AI: SAMPLING STATION'),
    a.marker('ai.north', p3(0, 0, -6.4), 'objective', 'AI SECTOR NORTH: FUEL + REACTIVITY'),
    a.marker('ai.northeast', p3(6.2, 0, -5.6), 'objective', 'AI SECTOR NORTH-EAST: WASTE + VENT'),
    a.marker('ai.east', p3(6.3, 0, 0), 'objective', 'AI SECTOR EAST: TURBINE + GRID'),
    a.marker('ai.south', p3(0, 0, 6.25), 'objective', 'AI SECTOR SOUTH: COOLING + EMERGENCY'),
    a.marker('ai.west', p3(-6.3, 0, 0), 'objective', 'AI SECTOR WEST: BACKUP + RESERVE + REPAIR'),
    a.marker('ai.control-window', p3(9.4, 0, -3.6), 'sightline', 'AI: CONTROL ROOM OVERLOOK IS EAST / +10 m'),
  ];
}

export const REACTOR_VISUAL_ENTITIES: Entity[] = [
  // Replace the former solid centre slab with four modules that leave a true
  // 10.40 m square opening around the circular service ring. The outer slabs
  // overlap the pre-existing N/S/diagonal floor pieces slightly on purpose.
  a.floor('visual.floor.west', p3(-8.0, 0, 0), s2(5.6, 12.0), {
    color: FLOOR,
    tags: semantic('visual.floor.west', 'architecture', 'floor', 'blender:FLOOR_MODULE'),
  }),
  a.floor('visual.floor.east', p3(8.0, 0, 0), s2(5.6, 12.0), {
    color: FLOOR,
    tags: semantic('visual.floor.east', 'architecture', 'floor', 'blender:FLOOR_MODULE'),
  }),
  a.floor('visual.floor.north', p3(0, 0, -5.60), s2(10.4, 0.80), {
    color: FLOOR,
    tags: semantic('visual.floor.north', 'architecture', 'floor', 'blender:FLOOR_MODULE'),
  }),
  a.floor('visual.floor.south', p3(0, 0, 5.60), s2(10.4, 0.80), {
    color: FLOOR,
    tags: semantic('visual.floor.south', 'architecture', 'floor', 'blender:FLOOR_MODULE'),
  }),

  // Exact pool ring geometry from the visual spec.
  ...radialSegments('pool.service-ring.deck', 3.90, 5.20, 0, 0.20, 32, FLOOR,
    ['pool', 'service-ring', 'dimensions:inner-3.90m', 'dimensions:outer-5.20m'], true),
  ...radialSegments('pool.rim.segment', 3.40, 3.90, 0.18, 0.22, 32, STAINLESS,
    ['pool', 'structural-rim', 'dimensions:inner-3.40m', 'dimensions:outer-3.90m'], true),
  ...shaftPanels(),
  ...poolRails(),

  // Water and submerged core. These are deliberately distinct assets so
  // emergency visuals can manipulate water, cyan light and hot core light
  // independently later.
  a.prop('pool.water.surface', p3(0, -0.50, 0), s3(6.76, 0.05, 6.76), {
    shape: 'cylinder',
    color: CORE_BLUE,
    collision: false,
    label: 'REACTOR POOL WATER Ø6.80 m',
    tags: semantic('pool.water.surface', 'pool', 'water', 'animation:water-state', 'blender:POOL_WATER'),
    notes: 'Visible water diameter is 6.80 m; mesh is 6.76 m to avoid z-fighting the rim.',
  }),
  a.floor('pool.bottom.walkable', p3(0, -6.50, 0), s2(6.60, 6.60), {
    color: DARK,
    tags: semantic('pool.bottom.walkable', 'pool', 'submerged', 'debug-recovery-floor'),
    notes: 'Browser prototype recovery floor at shaft bottom; production water gameplay may replace this.',
  }),
  a.prop('pool.core.lower-housing', p3(0, -6.40, 0), s3(3.25, 1.15, 3.25), {
    shape: 'cylinder', color: STEEL, collision: false,
    label: 'SUBMERGED CORE HOUSING',
    tags: semantic('pool.core.lower-housing', 'pool', 'core', 'submerged', 'blender:CORE_HOUSING'),
  }),
  a.prop('pool.core.glow.low', p3(0, -6.22, 0), s3(2.55, 0.16, 2.55), {
    shape: 'cylinder', color: CORE_WHITE, collision: false,
    tags: semantic('pool.core.glow.low', 'pool', 'core', 'emissive', 'fx:normal-core', 'blender:FX_CORE_GLOW'),
  }),
  a.prop('pool.core.glow.mid', p3(0, -5.72, 0), s3(4.15, 0.12, 4.15), {
    shape: 'cylinder', color: CORE_BLUE, collision: false,
    tags: semantic('pool.core.glow.mid', 'pool', 'core', 'emissive', 'fx:normal-core', 'blender:FX_CORE_GLOW'),
  }),
  a.prop('pool.core.glow.meltdown', p3(0, -6.05, 0), s3(1.95, 0.10, 1.95), {
    shape: 'cylinder', color: '#ffd1a0', collision: false,
    tags: semantic('pool.core.glow.meltdown', 'pool', 'core', 'emissive', 'fx:meltdown-hot-core', 'state:off-by-default'),
    notes: 'Dedicated future white/orange core-damage emitter; leave visually secondary in healthy state.',
  }),
  a.light('pool.light.core', p3(0, -4.65, 0), {
    size: [0.4, 0.4], color: CORE_BLUE, cast: true, intensity: 260, distance: 15,
    tags: semantic('pool.light.core', 'pool', 'lighting', 'fx:normal-core'),
  }),
  a.light('pool.light.bank-a', p3(-1.4, -2.7, 0), {
    size: [0.25, 0.25], color: CORE_BLUE, cast: true, intensity: 120, distance: 9,
    tags: semantic('pool.light.bank-a', 'pool', 'lighting', 'bank:a'),
  }),
  a.light('pool.light.bank-b', p3(1.4, -2.7, 0), {
    size: [0.25, 0.25], color: CORE_BLUE, cast: true, intensity: 120, distance: 9,
    tags: semantic('pool.light.bank-b', 'pool', 'lighting', 'bank:b'),
  }),

  // Exactly two hero banks.
  ...bank('A', -1.40),
  ...bank('B', 1.40),

  ...emergencyAndService(),
  ...controlDetail(),
  ...overheadAndPipework(),
  ...tanksAndInstrumentation(),

  // Clean 1990s room light: the pool is secondary illumination, never the sole
  // source. These real lights supplement the existing fixture housings.
  a.light('visual.light.nw', p3(-5.5, 14.6, -5.4), { size: [3.2, 0.55], color: '#f2f6f5', cast: true, intensity: 125, distance: 24, tags: semantic('visual.light.nw', 'lighting') }),
  a.light('visual.light.ne', p3(5.5, 14.6, -5.4), { size: [3.2, 0.55], color: '#f2f6f5', cast: true, intensity: 125, distance: 24, tags: semantic('visual.light.ne', 'lighting') }),
  a.light('visual.light.sw', p3(-5.5, 14.6, 5.4), { size: [3.2, 0.55], color: '#f2f6f5', cast: true, intensity: 125, distance: 24, tags: semantic('visual.light.sw', 'lighting') }),
  a.light('visual.light.se', p3(5.5, 14.6, 5.4), { size: [3.2, 0.55], color: '#f2f6f5', cast: true, intensity: 125, distance: 24, tags: semantic('visual.light.se', 'lighting') }),
  a.light('visual.light.alarm-a', p3(-4.9, 5.1, 5.6), { size: [0.35, 0.35], color: RED, tags: semantic('visual.light.alarm-a', 'warning-beacon', 'fx:alarm', 'blender:ALARM_BEACON') }),
  a.light('visual.light.alarm-b', p3(4.9, 5.1, 5.6), { size: [0.35, 0.35], color: RED, tags: semantic('visual.light.alarm-b', 'warning-beacon', 'fx:alarm', 'blender:ALARM_BEACON') }),

  // Visual query anchors for humans and MCP agents. Marker layer is toggleable
  // if the labels get in the way while evaluating pure composition.
  ...aiMarkers(),
];

export const CONTROL_VISUAL_ENTITIES: Entity[] = [
  // The existing control west wall already contains the +10 m observation
  // opening. These pieces dress that opening without changing its route.
  c.prop('visual.window.glass', p3(18.02, 10.30, 0), s3(0.06, 2.60, 5.40), {
    color: '#92d7e8',
    collision: false,
    label: 'REACTOR CONTROL OVERLOOK',
    tags: ['reactor-visual', 'asset:control-overlook-glass', 'glass', 'control-window', 'blender:CONTROL_WINDOW_GLASS'],
    notes: '5.40 m × 2.60 m visible glazing module from reactor visual spec.',
  }),
  c.prop('visual.window.frame.top', p3(18.00, 12.82, 0), s3(0.18, 0.18, 5.70), {
    color: STEEL, collision: false, tags: ['reactor-visual', 'control-window', 'blender:CONTROL_WINDOW_FRAME'],
  }),
  c.prop('visual.window.frame.bottom', p3(18.00, 10.18, 0), s3(0.18, 0.18, 5.70), {
    color: STEEL, collision: false, tags: ['reactor-visual', 'control-window', 'blender:CONTROL_WINDOW_FRAME'],
  }),
  c.prop('visual.window.frame.n', p3(18.00, 10.30, -2.76), s3(0.18, 2.60, 0.18), {
    color: STEEL, collision: false, tags: ['reactor-visual', 'control-window', 'blender:CONTROL_WINDOW_FRAME'],
  }),
  c.prop('visual.window.frame.s', p3(18.00, 10.30, 2.76), s3(0.18, 2.60, 0.18), {
    color: STEEL, collision: false, tags: ['reactor-visual', 'control-window', 'blender:CONTROL_WINDOW_FRAME'],
  }),
  // Readable 90s operator screens through the glazing.
  c.prop('visual.crt.core', p3(19.0, 10.92, -1.6), s3(0.72, 0.56, 0.16), {
    color: SCREEN, collision: false, label: 'CORE STATUS CRT',
    tags: ['reactor-visual', 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE'],
  }),
  c.prop('visual.crt.cooling', p3(19.0, 10.92, 0), s3(0.72, 0.56, 0.16), {
    color: '#63c9b2', collision: false, label: 'COOLING CRT',
    tags: ['reactor-visual', 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE'],
  }),
  c.prop('visual.crt.grid', p3(19.0, 10.92, 1.6), s3(0.72, 0.56, 0.16), {
    color: SCREEN, collision: false, label: 'GRID CRT',
    tags: ['reactor-visual', 'screen', 'emissive', 'blender:SCREEN_REPLACEABLE'],
  }),
  c.marker('visual.ai.window', p3(18.4, 10, 0), 'sightline', 'AI: 5.40 × 2.60 m CONTROL OVERLOOK GLAZING'),
];
