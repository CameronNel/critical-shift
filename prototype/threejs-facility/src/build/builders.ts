import * as THREE from 'three';
import type { BoxCollider } from '../nav/collision';
import { GeoBatch } from './geoBatch';
import { SHARED, UNIT, customMaterial, emissiveMaterial, zoneMaterial } from './materials';
import { createTextSprite } from './textSprite';
import { makeRng, range } from './rng';
import {
  type CatwalkEntity,
  type CavernEntity,
  type ConveyorEntity,
  type DoorwayEntity,
  type Entity,
  type FloorEntity,
  type LandmarkEntity,
  type LightEntity,
  type MachineEntity,
  type MannequinEntity,
  type MarkerEntity,
  type PipeEntity,
  type PlatformEntity,
  type PropEntity,
  type RampEntity,
  type SpawnEntity,
  type StairEntity,
  type TrackEntity,
  type TunnelEntity,
  type Vec3,
  type WallEntity,
  type WallGap,
} from '../facility/schema';

export interface EntityBuild {
  object: THREE.Object3D;
  colliders: BoxCollider[];
}

const RAIL_HEIGHT = 1.1;
const RAIL_THICKNESS = 0.09;
const STEP_RISE = 0.18;
/** Ramp and slope colliders are diced into steps this tall. */
const SLOPE_STEP = 0.22;

const vec = (a: Vec3) => new THREE.Vector3(a[0], a[1], a[2]);

function box(
  id: string,
  centre: THREE.Vector3,
  size: THREE.Vector3,
  rotY: number,
  solid: boolean,
  walkable: boolean,
): BoxCollider {
  return {
    entityId: id,
    cx: centre.x,
    cy: centre.y,
    cz: centre.z,
    hx: Math.max(size.x, 0.02) / 2,
    hy: Math.max(size.y, 0.02) / 2,
    hz: Math.max(size.z, 0.02) / 2,
    rotY,
    solid,
    walkable,
  };
}

/** Which datum support legs drop to. */
function supportBase(y: number): number {
  return y > 0.5 ? 0 : -8;
}

function mesh(
  geometry: THREE.BufferGeometry,
  material: THREE.Material,
  centre: THREE.Vector3,
  scale: THREE.Vector3,
  rotY = 0,
): THREE.Mesh {
  const m = new THREE.Mesh(geometry, material);
  m.position.copy(centre);
  m.scale.copy(scale);
  m.rotation.y = rotY;
  return m;
}

function namePlate(text: string, at: THREE.Vector3, height = 0.9): THREE.Sprite {
  const sprite = createTextSprite(text, {
    height,
    maxWidth: 4.6,
    color: '#eef3f8',
    background: 'rgba(14,17,21,0.72)',
    border: 'rgba(200,215,230,0.35)',
  });
  sprite.position.copy(at);
  sprite.userData.isLabel = true;
  sprite.userData.labelKind = 'plate';
  return sprite;
}

interface Panel {
  d0: number;
  d1: number;
  y0: number;
  y1: number;
}

/** Split a wall run into solid panels around its openings. */
export function splitWall(length: number, height: number, gaps: WallGap[] = []): Panel[] {
  const sorted = [...gaps]
    .map((g) => ({
      start: Math.max(0, g.at - g.width / 2),
      end: Math.min(length, g.at + g.width / 2),
      bottom: g.bottom ?? 0,
      top: Math.min(g.top ?? height, height),
    }))
    .filter((g) => g.end > g.start)
    .sort((a, b) => a.start - b.start);

  const panels: Panel[] = [];
  let cursor = 0;
  for (const gap of sorted) {
    if (gap.start > cursor) panels.push({ d0: cursor, d1: gap.start, y0: 0, y1: height });
    if (gap.bottom > 0) panels.push({ d0: gap.start, d1: gap.end, y0: 0, y1: gap.bottom });
    if (gap.top < height) panels.push({ d0: gap.start, d1: gap.end, y0: gap.top, y1: height });
    cursor = Math.max(cursor, gap.end);
  }
  if (cursor < length) panels.push({ d0: cursor, d1: length, y0: 0, y1: height });
  return panels.filter((p) => p.d1 - p.d0 > 1e-3 && p.y1 - p.y0 > 1e-3);
}

function buildFloor(e: FloorEntity, zoneColor: string): EntityBuild {
  const thickness = e.thickness ?? 0.3;
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const centre = new THREE.Vector3(e.position[0], e.position[1] - thickness / 2, e.position[2]);
  const size = new THREE.Vector3(e.size[0], thickness, e.size[1]);
  const role = e.tags?.includes('roof') ? 'roof' : 'floor';
  const material = e.color ? customMaterial(e.color, role) : zoneMaterial(zoneColor, role);
  const object = mesh(UNIT.box, material, centre, size, rotY);
  return {
    object,
    colliders: [
      box(e.id, centre, size, rotY, e.collision === true, e.collision !== false),
    ],
  };
}

function buildWall(e: WallEntity, zoneColor: string): EntityBuild {
  const base = e.base ?? 0;
  const thickness = e.thickness ?? 0.3;
  const from = new THREE.Vector3(e.from[0], base, e.from[1]);
  const to = new THREE.Vector3(e.to[0], base, e.to[1]);
  const dx = to.x - from.x;
  const dz = to.z - from.z;
  const length = Math.hypot(dx, dz);
  const angle = Math.atan2(dx, dz);
  const dir = new THREE.Vector3(dx / (length || 1), 0, dz / (length || 1));

  const batch = new GeoBatch();
  const colliders: BoxCollider[] = [];
  const solid = e.collision !== false;
  for (const panel of splitWall(length, e.height, e.gaps)) {
    const mid = (panel.d0 + panel.d1) / 2;
    const centre = new THREE.Vector3(
      from.x + dir.x * mid,
      base + (panel.y0 + panel.y1) / 2,
      from.z + dir.z * mid,
    );
    const size = new THREE.Vector3(thickness, panel.y1 - panel.y0, panel.d1 - panel.d0);
    batch.addBox(centre, size, angle);
    colliders.push(box(e.id, centre, size, angle, solid, false));
  }
  const material = e.color ? customMaterial(e.color, 'wall') : zoneMaterial(zoneColor, 'wall');
  const object = batch.build(material, e.id) ?? new THREE.Group();
  return { object, colliders };
}

/**
 * Guard rail along a straight run, returned as merged geometry plus a blocker.
 *
 * `inset` shortens the *collider* at both ends without shortening the rail you
 * can see. A stair's rail is one long slab spanning the whole flight, so
 * without this every landing, spur and catwalk that meets a flight at its head
 * or its foot is walled off by the rail beside it.
 */
function addRail(
  batch: GeoBatch,
  colliders: BoxCollider[],
  id: string,
  a: THREE.Vector3,
  b: THREE.Vector3,
  inset = 0,
): void {
  const dx = b.x - a.x;
  const dz = b.z - a.z;
  const length = Math.hypot(dx, dz);
  if (length < 0.2) return;
  const angle = Math.atan2(dx, dz);
  const dir = new THREE.Vector3(dx / length, (b.y - a.y) / length, dz / length);

  const posts = Math.max(2, Math.round(length / 2.2) + 1);
  for (let i = 0; i < posts; i++) {
    const t = (i / (posts - 1)) * length;
    const p = new THREE.Vector3(a.x + dir.x * t, a.y + dir.y * t, a.z + dir.z * t);
    batch.addBox(
      new THREE.Vector3(p.x, p.y + RAIL_HEIGHT / 2, p.z),
      new THREE.Vector3(RAIL_THICKNESS, RAIL_HEIGHT, RAIL_THICKNESS),
      angle,
    );
  }
  for (const h of [RAIL_HEIGHT, RAIL_HEIGHT * 0.52]) {
    batch.addSegment(
      new THREE.Vector3(a.x, a.y + h, a.z),
      new THREE.Vector3(b.x, b.y + h, b.z),
      RAIL_THICKNESS,
      RAIL_THICKNESS,
      0,
    );
  }
  // The blocker follows the rail in short segments rather than being one box
  // spanning the whole run. On a stair a single box would be as tall as the
  // flight's entire rise everywhere along it, walling off anything that passes
  // above or below the rail's actual height.
  const blocked = Math.max(0, length - inset * 2);
  if (blocked < 0.2) return;
  const segments = Math.max(1, Math.round(blocked / 2.5));
  const segLength = blocked / segments;
  for (let i = 0; i < segments; i++) {
    const t0 = inset + segLength * i;
    const t1 = t0 + segLength;
    const mid = (t0 + t1) / 2;
    const centre = new THREE.Vector3(
      a.x + dir.x * mid,
      a.y + dir.y * mid + RAIL_HEIGHT / 2,
      a.z + dir.z * mid,
    );
    const size = new THREE.Vector3(0.18, RAIL_HEIGHT + Math.abs(dir.y) * segLength, segLength);
    colliders.push(box(id, centre, size, angle, true, false));
  }
}

function buildPlatform(e: PlatformEntity, zoneColor: string): EntityBuild {
  const thickness = e.thickness ?? 0.25;
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const [sx, sz] = e.size;
  const deckCentre = new THREE.Vector3(
    e.position[0],
    e.position[1] - thickness / 2,
    e.position[2],
  );
  const deckSize = new THREE.Vector3(sx, thickness, sz);
  const deckMaterial = e.color ? customMaterial(e.color, 'deck') : zoneMaterial(zoneColor, 'deck');
  group.add(mesh(UNIT.box, deckMaterial, deckCentre, deckSize, rotY));
  colliders.push(box(e.id, deckCentre, deckSize, rotY, false, e.collision !== false));

  const y = e.position[1];
  const corner = (lx: number, lz: number) => {
    const c = Math.cos(rotY);
    const s = Math.sin(rotY);
    return new THREE.Vector3(
      e.position[0] + lx * c + lz * s,
      y,
      e.position[2] - lx * s + lz * c,
    );
  };
  const nw = corner(-sx / 2, -sz / 2);
  const ne = corner(sx / 2, -sz / 2);
  const se = corner(sx / 2, sz / 2);
  const sw = corner(-sx / 2, sz / 2);

  const railBatch = new GeoBatch();
  for (const side of e.railings ?? []) {
    if (side === 'n') addRail(railBatch, colliders, e.id, nw, ne);
    if (side === 'e') addRail(railBatch, colliders, e.id, ne, se);
    if (side === 's') addRail(railBatch, colliders, e.id, se, sw);
    if (side === 'w') addRail(railBatch, colliders, e.id, sw, nw);
  }
  const rails = railBatch.build(SHARED.rail, `${e.id}:rails`);
  if (rails) group.add(rails);

  if (e.supports) {
    const legBatch = new GeoBatch();
    const base = supportBase(y);
    const height = y - thickness - base;
    if (height > 0.4) {
      for (const p of [nw, ne, se, sw]) {
        const inset = 0.5;
        const toCentre = new THREE.Vector3(e.position[0] - p.x, 0, e.position[2] - p.z);
        if (toCentre.lengthSq() > 0) toCentre.normalize().multiplyScalar(inset);
        legBatch.addBox(
          new THREE.Vector3(p.x + toCentre.x, base + height / 2, p.z + toCentre.z),
          new THREE.Vector3(0.34, height, 0.34),
          rotY,
        );
      }
    }
    const legs = legBatch.build(SHARED.steel, `${e.id}:legs`);
    if (legs) group.add(legs);
  }

  if (e.label) {
    group.add(namePlate(e.label, new THREE.Vector3(e.position[0], y + 2.4, e.position[2]), 1.1));
  }
  return { object: group, colliders };
}

function buildStair(e: StairEntity, zoneColor: string): EntityBuild {
  const from = vec(e.from);
  const to = vec(e.to);
  const rise = to.y - from.y;
  const run = Math.hypot(to.x - from.x, to.z - from.z);
  const angle = Math.atan2(to.x - from.x, to.z - from.z);
  const steps = Math.max(1, Math.round(Math.abs(rise) / STEP_RISE));
  const stepRise = rise / steps;
  const stepRun = run / steps;
  const dir = new THREE.Vector3((to.x - from.x) / (run || 1), 0, (to.z - from.z) / (run || 1));

  const batch = new GeoBatch();
  const colliders: BoxCollider[] = [];
  for (let i = 0; i < steps; i++) {
    const top = from.y + stepRise * (i + 1);
    const thickness = Math.max(0.2, Math.abs(stepRise) + 0.12);
    const d = stepRun * (i + 0.5);
    const centre = new THREE.Vector3(
      from.x + dir.x * d,
      top - thickness / 2,
      from.z + dir.z * d,
    );
    const size = new THREE.Vector3(e.width, thickness, stepRun + 0.02);
    batch.addBox(centre, size, angle);
    colliders.push(box(e.id, centre, size, angle, false, true));
  }
  const material = e.color ? customMaterial(e.color, 'deck') : zoneMaterial(zoneColor, 'deck');
  const group = new THREE.Group();
  const treads = batch.build(material, e.id);
  if (treads) group.add(treads);

  if (e.railings !== false) {
    const railBatch = new GeoBatch();
    const perp = new THREE.Vector3(dir.z, 0, -dir.x).multiplyScalar(e.width / 2);
    const lowA = new THREE.Vector3(from.x + perp.x, from.y, from.z + perp.z);
    const highA = new THREE.Vector3(to.x + perp.x, to.y, to.z + perp.z);
    const lowB = new THREE.Vector3(from.x - perp.x, from.y, from.z - perp.z);
    const highB = new THREE.Vector3(to.x - perp.x, to.y, to.z - perp.z);
    // Leave the head and foot of the flight open so landings can meet it.
    addRail(railBatch, colliders, e.id, lowA, highA, 1.6);
    addRail(railBatch, colliders, e.id, lowB, highB, 1.6);
    const rails = railBatch.build(SHARED.rail, `${e.id}:rails`);
    if (rails) group.add(rails);
  }
  return { object: group, colliders };
}

function buildRamp(e: RampEntity, zoneColor: string): EntityBuild {
  const from = vec(e.from);
  const to = vec(e.to);
  const run = Math.hypot(to.x - from.x, to.z - from.z);
  const rise = to.y - from.y;
  const angle = Math.atan2(to.x - from.x, to.z - from.z);
  const dir = new THREE.Vector3((to.x - from.x) / (run || 1), 0, (to.z - from.z) / (run || 1));

  const group = new THREE.Group();
  const material = e.color ? customMaterial(e.color, 'deck') : zoneMaterial(zoneColor, 'deck');

  // One sloped slab for the visual, stepped boxes for the walker.
  const slab = new THREE.Mesh(UNIT.box, material);
  const span = Math.hypot(run, rise);
  slab.scale.set(e.width, 0.28, span);
  slab.position.set((from.x + to.x) / 2, (from.y + to.y) / 2 - 0.14, (from.z + to.z) / 2);
  slab.rotation.order = 'YXZ';
  slab.rotation.y = angle;
  slab.rotation.x = -Math.atan2(rise, run);
  group.add(slab);

  const colliders: BoxCollider[] = [];
  const steps = Math.max(1, Math.round(Math.abs(rise) / SLOPE_STEP) || 1);
  for (let i = 0; i < steps; i++) {
    const t0 = i / steps;
    const t1 = (i + 1) / steps;
    const top = from.y + rise * ((t0 + t1) / 2);
    const d = run * ((t0 + t1) / 2);
    const centre = new THREE.Vector3(from.x + dir.x * d, top - 0.15, from.z + dir.z * d);
    const size = new THREE.Vector3(e.width, 0.3, (run / steps) * 1.05 + 0.02);
    colliders.push(box(e.id, centre, size, angle, false, true));
  }

  if (e.railings) {
    const railBatch = new GeoBatch();
    const perp = new THREE.Vector3(dir.z, 0, -dir.x).multiplyScalar(e.width / 2);
    addRail(
      railBatch,
      colliders,
      e.id,
      new THREE.Vector3(from.x + perp.x, from.y, from.z + perp.z),
      new THREE.Vector3(to.x + perp.x, to.y, to.z + perp.z),
    );
    addRail(
      railBatch,
      colliders,
      e.id,
      new THREE.Vector3(from.x - perp.x, from.y, from.z - perp.z),
      new THREE.Vector3(to.x - perp.x, to.y, to.z - perp.z),
    );
    const rails = railBatch.build(SHARED.rail, `${e.id}:rails`);
    if (rails) group.add(rails);
  }
  return { object: group, colliders };
}

function buildCatwalk(e: CatwalkEntity, zoneColor: string): EntityBuild {
  const path = e.path.map(vec);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const deckBatch = new GeoBatch();
  const railBatch = new GeoBatch();
  const legBatch = new GeoBatch();
  const railMode = e.railings ?? 'both';
  const half = e.width / 2;

  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const run = Math.hypot(dx, dz);
    if (run < 1e-3) continue;
    const angle = Math.atan2(dx, dz);
    const dir = new THREE.Vector3(dx / run, 0, dz / run);
    const perp = new THREE.Vector3(dir.z, 0, -dir.x).multiplyScalar(half);
    const rise = b.y - a.y;

    if (Math.abs(rise) < 0.05) {
      const centre = new THREE.Vector3((a.x + b.x) / 2, a.y - 0.09, (a.z + b.z) / 2);
      const size = new THREE.Vector3(e.width, 0.18, run);
      deckBatch.addBox(centre, size, angle);
      colliders.push(box(e.id, centre, size, angle, false, true));
    } else {
      const steps = Math.max(1, Math.round(Math.abs(rise) / SLOPE_STEP));
      for (let s = 0; s < steps; s++) {
        const t = (s + 0.5) / steps;
        const centre = new THREE.Vector3(
          a.x + dir.x * run * t,
          a.y + rise * t - 0.09,
          a.z + dir.z * run * t,
        );
        const size = new THREE.Vector3(e.width, 0.18, (run / steps) * 1.05);
        deckBatch.addBox(centre, size, angle);
        colliders.push(box(e.id, centre, size, angle, false, true));
      }
    }

    if (railMode === 'both' || railMode === 'left') {
      addRail(
        railBatch,
        colliders,
        e.id,
        new THREE.Vector3(a.x + perp.x, a.y, a.z + perp.z),
        new THREE.Vector3(b.x + perp.x, b.y, b.z + perp.z),
      );
    }
    if (railMode === 'both' || railMode === 'right') {
      addRail(
        railBatch,
        colliders,
        e.id,
        new THREE.Vector3(a.x - perp.x, a.y, a.z - perp.z),
        new THREE.Vector3(b.x - perp.x, b.y, b.z - perp.z),
      );
    }

    if (e.supports !== false) {
      const legs = Math.max(1, Math.floor(run / 7));
      for (let s = 0; s <= legs; s++) {
        const t = s / legs;
        const y = a.y + rise * t;
        const base = supportBase(y);
        const height = y - 0.18 - base;
        if (height < 0.6) continue;
        legBatch.addBox(
          new THREE.Vector3(
            a.x + dir.x * run * t,
            base + height / 2,
            a.z + dir.z * run * t,
          ),
          new THREE.Vector3(0.3, height, 0.3),
          angle,
        );
      }
    }
  }

  const deckMaterial = e.color ? customMaterial(e.color, 'deck') : zoneMaterial(zoneColor, 'deck');
  const deck = deckBatch.build(deckMaterial, e.id);
  if (deck) group.add(deck);
  const rails = railBatch.build(SHARED.rail, `${e.id}:rails`);
  if (rails) group.add(rails);
  const legs = legBatch.build(SHARED.steel, `${e.id}:legs`);
  if (legs) group.add(legs);

  if (e.label && path.length) {
    const mid = path[Math.floor(path.length / 2)];
    group.add(namePlate(e.label, new THREE.Vector3(mid.x, mid.y + 2.6, mid.z), 1.0));
  }
  return { object: group, colliders };
}

function shapeGeometry(shape: MachineEntity['shape']): THREE.BufferGeometry {
  switch (shape) {
    case 'cylinder':
      return UNIT.cylinder;
    case 'cone':
      return UNIT.cone;
    case 'hopper':
      return UNIT.hopper;
    default:
      return UNIT.box;
  }
}

function buildMassing(
  e: MachineEntity | PropEntity,
  zoneColor: string,
  role: 'machine' | 'prop',
): EntityBuild {
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const [sx, sy, sz] = e.size;
  const centre = new THREE.Vector3(e.position[0], e.position[1] + sy / 2, e.position[2]);
  const material = e.color ? customMaterial(e.color, role) : zoneMaterial(zoneColor, role);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];

  if (e.shape === 'frame') {
    // Open steel structure: four columns, top and bottom ring beams.
    const batch = new GeoBatch();
    const t = 0.42;
    for (const [ox, oz] of [
      [-1, -1],
      [1, -1],
      [1, 1],
      [-1, 1],
    ] as const) {
      batch.addBox(
        new THREE.Vector3(
          e.position[0] + (ox * (sx - t)) / 2,
          e.position[1] + sy / 2,
          e.position[2] + (oz * (sz - t)) / 2,
        ),
        new THREE.Vector3(t, sy, t),
        rotY,
      );
    }
    for (const y of [e.position[1] + sy - t / 2, e.position[1] + t / 2, e.position[1] + sy * 0.5]) {
      batch.addBox(
        new THREE.Vector3(e.position[0], y, e.position[2] - (sz - t) / 2),
        new THREE.Vector3(sx, t, t),
        rotY,
      );
      batch.addBox(
        new THREE.Vector3(e.position[0], y, e.position[2] + (sz - t) / 2),
        new THREE.Vector3(sx, t, t),
        rotY,
      );
    }
    const built = batch.build(material, e.id);
    if (built) group.add(built);
    // Frames are structure, not obstacles: only the columns block.
    for (const [ox, oz] of [
      [-1, -1],
      [1, -1],
      [1, 1],
      [-1, 1],
    ] as const) {
      const c = new THREE.Vector3(
        e.position[0] + (ox * (sx - t)) / 2,
        e.position[1] + sy / 2,
        e.position[2] + (oz * (sz - t)) / 2,
      );
      colliders.push(box(e.id, c, new THREE.Vector3(t, sy, t), rotY, true, false));
    }
  } else {
    const geometry = shapeGeometry(e.shape);
    const scale =
      e.shape === 'box'
        ? new THREE.Vector3(sx, sy, sz)
        : new THREE.Vector3(sx, sy, sz || sx);
    group.add(mesh(geometry, material, centre, scale, rotY));
    const footprint =
      e.shape === 'box'
        ? new THREE.Vector3(sx, sy, sz)
        : new THREE.Vector3(sx * 0.82, sy, (sz || sx) * 0.82);
    const active = e.collision !== false;
    colliders.push(box(e.id, centre, footprint, rotY, active, active));
  }

  if (e.label) {
    group.add(
      namePlate(
        e.label,
        new THREE.Vector3(e.position[0], e.position[1] + sy + 1.4, e.position[2]),
        role === 'machine' ? 1 : 0.8,
      ),
    );
  }
  return { object: group, colliders };
}

function buildConveyor(e: ConveyorEntity, zoneColor: string): EntityBuild {
  const path = e.path.map(vec);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const beltBatch = new GeoBatch();
  const frameBatch = new GeoBatch();
  const legBatch = new GeoBatch();
  const arrowBatch = new GeoBatch();
  const half = e.width / 2;

  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const run = Math.hypot(dx, dz);
    if (run < 1e-3) continue;
    const angle = Math.atan2(dx, dz);
    const dir = new THREE.Vector3(dx / run, 0, dz / run);
    const rise = b.y - a.y;
    const steps = Math.max(1, Math.round(Math.max(Math.abs(rise) / SLOPE_STEP, run / 6)));

    for (let s = 0; s < steps; s++) {
      const t = (s + 0.5) / steps;
      const centre = new THREE.Vector3(
        a.x + dir.x * run * t,
        a.y + rise * t,
        a.z + dir.z * run * t,
      );
      const size = new THREE.Vector3(e.width, 0.22, (run / steps) * 1.06);
      beltBatch.addBox(centre, size, angle);
      // Belts are climbable: a tempting, stupid shortcut is the point.
      colliders.push(box(e.id, centre, size, angle, false, true));
      frameBatch.addBox(
        new THREE.Vector3(centre.x, centre.y - 0.28, centre.z),
        new THREE.Vector3(e.width + 0.24, 0.34, (run / steps) * 1.06),
        angle,
      );
    }

    const arrows = Math.max(1, Math.floor(run / 11));
    for (let s = 0; s < arrows; s++) {
      const t = (s + 0.5) / arrows;
      arrowBatch.addBox(
        new THREE.Vector3(
          a.x + dir.x * run * t,
          a.y + rise * t + 0.18,
          a.z + dir.z * run * t,
        ),
        new THREE.Vector3(half * 0.7, 0.1, 1.6),
        angle,
      );
    }

    if (e.supports !== false) {
      const legs = Math.max(1, Math.floor(run / 9));
      for (let s = 0; s <= legs; s++) {
        const t = s / legs;
        const y = a.y + rise * t;
        const base = supportBase(y);
        const height = y - 0.45 - base;
        if (height < 0.8) continue;
        const c = new THREE.Vector3(
          a.x + dir.x * run * t,
          base + height / 2,
          a.z + dir.z * run * t,
        );
        legBatch.addBox(c, new THREE.Vector3(0.34, height, 0.34), angle);
        colliders.push(box(e.id, c, new THREE.Vector3(0.34, height, 0.34), angle, true, false));
      }
    }
  }

  const belt = beltBatch.build(SHARED.belt, e.id);
  if (belt) group.add(belt);
  const frame = frameBatch.build(
    e.color ? customMaterial(e.color, 'machine') : zoneMaterial(zoneColor, 'machine'),
    `${e.id}:frame`,
  );
  if (frame) group.add(frame);
  const legs = legBatch.build(SHARED.steel, `${e.id}:legs`);
  if (legs) group.add(legs);
  const arrows = arrowBatch.build(SHARED.hazard, `${e.id}:flow`);
  if (arrows) group.add(arrows);

  if (e.label && path.length) {
    const mid = path[Math.floor(path.length / 2)];
    group.add(namePlate(e.label, new THREE.Vector3(mid.x, mid.y + 1.9, mid.z), 1.0));
  }
  return { object: group, colliders };
}

function buildTrack(e: TrackEntity): EntityBuild {
  const path = e.path.map(vec);
  const gauge = e.gauge ?? 1.2;
  const railBatch = new GeoBatch();
  const sleeperBatch = new GeoBatch();

  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const run = Math.hypot(dx, dz);
    if (run < 1e-3) continue;
    const angle = Math.atan2(dx, dz);
    const dir = new THREE.Vector3(dx / run, 0, dz / run);
    const perp = new THREE.Vector3(dir.z, 0, -dir.x).multiplyScalar(gauge / 2);
    for (const sign of [1, -1]) {
      railBatch.addSegment(
        new THREE.Vector3(a.x + perp.x * sign, a.y + 0.09, a.z + perp.z * sign),
        new THREE.Vector3(b.x + perp.x * sign, b.y + 0.09, b.z + perp.z * sign),
        0.12,
        0.18,
      );
    }
    if (e.sleepers !== false) {
      const count = Math.max(1, Math.floor(run / 1.8));
      for (let s = 0; s < count; s++) {
        const t = (s + 0.5) / count;
        sleeperBatch.addBox(
          new THREE.Vector3(
            a.x + dir.x * run * t,
            a.y + (b.y - a.y) * t + 0.03,
            a.z + dir.z * run * t,
          ),
          new THREE.Vector3(gauge + 0.7, 0.12, 0.28),
          angle,
        );
      }
    }
  }
  const group = new THREE.Group();
  const rails = railBatch.build(SHARED.track, e.id);
  if (rails) group.add(rails);
  const sleepers = sleeperBatch.build(SHARED.steel, `${e.id}:sleepers`);
  if (sleepers) group.add(sleepers);
  return { object: group, colliders: [] };
}

function buildPipe(e: PipeEntity, zoneColor: string): EntityBuild {
  const path = e.path.map(vec);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const material = e.color ? customMaterial(e.color, 'pipe') : zoneMaterial(zoneColor, 'pipe');
  const parts: THREE.BufferGeometry[] = [];

  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    const delta = new THREE.Vector3().subVectors(b, a);
    const length = delta.length();
    if (length < 1e-3) continue;
    const geometry = new THREE.CylinderGeometry(e.radius, e.radius, length, 12, 1, true);
    const quat = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 1, 0),
      delta.clone().normalize(),
    );
    const matrix = new THREE.Matrix4().compose(
      new THREE.Vector3().addVectors(a, b).multiplyScalar(0.5),
      quat,
      new THREE.Vector3(1, 1, 1),
    );
    geometry.applyMatrix4(matrix);
    parts.push(geometry);

    if (e.collision !== false && e.radius >= 0.35) {
      const angle = Math.atan2(delta.x, delta.z);
      colliders.push(
        box(
          e.id,
          new THREE.Vector3().addVectors(a, b).multiplyScalar(0.5),
          new THREE.Vector3(e.radius * 2, e.radius * 2, Math.hypot(delta.x, delta.z)),
          angle,
          true,
          false,
        ),
      );
    }
  }
  for (let i = 1; i < path.length - 1; i++) {
    const elbow = new THREE.SphereGeometry(e.radius * 1.06, 10, 8);
    elbow.translate(path[i].x, path[i].y, path[i].z);
    parts.push(elbow);
  }

  const batch = new GeoBatch();
  for (const part of parts) batch.addGeometry(part);
  const built = batch.build(material, e.id);
  if (built) group.add(built);
  return { object: group, colliders };
}

function buildDoorway(e: DoorwayEntity, zoneColor: string): EntityBuild {
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const batch = new GeoBatch();
  const jamb = 0.24;
  for (const sign of [1, -1]) {
    batch.addBox(
      new THREE.Vector3(
        e.position[0] + Math.cos(rotY) * ((e.width / 2 + jamb / 2) * sign),
        e.position[1] + e.height / 2,
        e.position[2] - Math.sin(rotY) * ((e.width / 2 + jamb / 2) * sign),
      ),
      new THREE.Vector3(jamb, e.height, 0.5),
      rotY,
    );
  }
  batch.addBox(
    new THREE.Vector3(e.position[0], e.position[1] + e.height + jamb / 2, e.position[2]),
    new THREE.Vector3(e.width + jamb * 2, jamb, 0.5),
    rotY,
  );
  const material = e.color ? customMaterial(e.color, 'machine') : zoneMaterial(zoneColor, 'machine');
  const group = new THREE.Group();
  const built = batch.build(material, e.id);
  if (built) group.add(built);
  if (e.label) {
    group.add(
      namePlate(
        e.label,
        new THREE.Vector3(e.position[0], e.position[1] + e.height + 1.2, e.position[2]),
        0.9,
      ),
    );
  }
  return { object: group, colliders: [] };
}

/**
 * Rough rock built from overlapping slabs placed strictly outside the nominal
 * void. The clean nominal box stays the collision surface, so the player never
 * clips into rock while the space still reads as excavated rather than built.
 */
function addRoughFace(
  batch: GeoBatch,
  colliders: BoxCollider[],
  id: string,
  a: THREE.Vector3,
  b: THREE.Vector3,
  base: number,
  height: number,
  rough: number,
  rng: () => number,
  gaps: WallGap[],
): void {
  const dx = b.x - a.x;
  const dz = b.z - a.z;
  const length = Math.hypot(dx, dz);
  if (length < 0.1) return;
  const angle = Math.atan2(dx, dz);
  const dir = new THREE.Vector3(dx / length, 0, dz / length);
  // Outward is to the right of the run; callers order points clockwise.
  const out = new THREE.Vector3(dir.z, 0, -dir.x);

  for (const panel of splitWall(length, height, gaps)) {
    const panelLength = panel.d1 - panel.d0;
    const panelHeight = panel.y1 - panel.y0;
    const mid = (panel.d0 + panel.d1) / 2;
    // The blocker sits just outside the nominal void; rock is placed beyond it.
    colliders.push(
      box(
        id,
        new THREE.Vector3(
          a.x + dir.x * mid + out.x * 0.5,
          base + (panel.y0 + panel.y1) / 2,
          a.z + dir.z * mid + out.z * 0.5,
        ),
        new THREE.Vector3(1.0, panelHeight, panelLength),
        angle,
        true,
        false,
      ),
    );

    const chunks = Math.max(1, Math.round(panelLength / 2.4));
    const bands = Math.max(1, Math.round(panelHeight / 2.4));
    for (let c = 0; c < chunks; c++) {
      for (let bnd = 0; bnd < bands; bnd++) {
        const t = (c + 0.5) / chunks;
        const vt = (bnd + 0.5) / bands;
        const depth = range(rng, 0.9, 0.9 + 2.4 * rough);
        const offset = 0.5 + depth / 2 + range(rng, -0.06, 0.05);
        const p = new THREE.Vector3(
          a.x + dir.x * (panel.d0 + panelLength * t) + out.x * offset,
          base + panel.y0 + panelHeight * vt,
          a.z + dir.z * (panel.d0 + panelLength * t) + out.z * offset,
        );
        batch.addBox(
          p,
          new THREE.Vector3(
            depth,
            (panelHeight / bands) * range(rng, 1.05, 1.5),
            (panelLength / chunks) * range(rng, 1.1, 1.6),
          ),
          angle + range(rng, -0.22, 0.22) * rough,
        );
      }
    }
  }
}

function buildCavern(e: CavernEntity, zoneColor: string): EntityBuild {
  const rng = makeRng(e.seed ?? 1);
  const rough = e.rough ?? 0.5;
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const [sx, sy, sz] = e.size;
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const rockBatch = new GeoBatch();
  const material = e.color ? customMaterial(e.color, 'rock') : zoneMaterial(zoneColor, 'rock');

  const cos = Math.cos(rotY);
  const sin = Math.sin(rotY);
  const local = (lx: number, lz: number) =>
    new THREE.Vector3(
      e.position[0] + lx * cos + lz * sin,
      e.position[1],
      e.position[2] - lx * sin + lz * cos,
    );

  const nw = local(-sx / 2, -sz / 2);
  const ne = local(sx / 2, -sz / 2);
  const se = local(sx / 2, sz / 2);
  const sw = local(-sx / 2, sz / 2);

  // North and east faces run in the +local direction, south and west reverse,
  // so the signed offset from the side centre flips for the latter pair.
  const gapsFor = (side: 'n' | 'e' | 's' | 'w', length: number): WallGap[] => {
    const sign = side === 'n' || side === 'e' ? 1 : -1;
    return (e.openings ?? [])
      .filter((o) => o.side === side)
      .map((o) => ({
        at: length / 2 + sign * o.at,
        width: o.width,
        bottom: 0,
        top: o.height ?? sy,
      }));
  };

  // Clockwise so the outward normal is consistent for every face.
  addRoughFace(rockBatch, colliders, e.id, nw, ne, e.position[1], sy, rough, rng, gapsFor('n', sx));
  addRoughFace(rockBatch, colliders, e.id, ne, se, e.position[1], sy, rough, rng, gapsFor('e', sz));
  addRoughFace(rockBatch, colliders, e.id, se, sw, e.position[1], sy, rough, rng, gapsFor('s', sx));
  addRoughFace(rockBatch, colliders, e.id, sw, nw, e.position[1], sy, rough, rng, gapsFor('w', sz));

  // Floor: flat and clean so walking is predictable.
  const floorCentre = new THREE.Vector3(e.position[0], e.position[1] - 0.4, e.position[2]);
  const floorSize = new THREE.Vector3(sx + 1.6, 0.8, sz + 1.6);
  group.add(mesh(UNIT.box, material, floorCentre, floorSize, rotY));
  colliders.push(box(e.id, floorCentre, floorSize, rotY, false, true));

  if (!e.openRoof) {
    const cols = Math.max(2, Math.round(sx / 4));
    const rows = Math.max(2, Math.round(sz / 4));
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        const lx = -sx / 2 + (sx * (c + 0.5)) / cols;
        const lz = -sz / 2 + (sz * (r + 0.5)) / rows;
        const p = local(lx, lz);
        const drop = range(rng, 0, 1.1 * rough);
        rockBatch.addBox(
          new THREE.Vector3(p.x, e.position[1] + sy + 0.7 - drop, p.z),
          new THREE.Vector3(
            (sx / cols) * range(rng, 1.1, 1.5),
            1.4 + drop,
            (sz / rows) * range(rng, 1.1, 1.5),
          ),
          rotY + range(rng, -0.12, 0.12),
        );
      }
    }
  }

  const rock = rockBatch.build(material, e.id);
  if (rock) group.add(rock);
  if (e.label) {
    group.add(
      namePlate(
        e.label,
        new THREE.Vector3(e.position[0], e.position[1] + Math.min(sy - 1, 4.5), e.position[2]),
        1.4,
      ),
    );
  }
  return { object: group, colliders };
}

function buildTunnel(e: TunnelEntity, zoneColor: string): EntityBuild {
  const rng = makeRng(e.seed ?? 7);
  const rough = e.rough ?? 0.45;
  const path = e.path.map(vec);
  const group = new THREE.Group();
  const colliders: BoxCollider[] = [];
  const rockBatch = new GeoBatch();
  const material = e.color ? customMaterial(e.color, 'rock') : zoneMaterial(zoneColor, 'rock');
  const half = e.width / 2;

  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const run = Math.hypot(dx, dz);
    if (run < 1e-3) continue;
    const angle = Math.atan2(dx, dz);
    const dir = new THREE.Vector3(dx / run, 0, dz / run);
    const perp = new THREE.Vector3(dir.z, 0, -dir.x);
    const rise = b.y - a.y;

    // A face's rock is laid on the far side of its run direction, so the
    // right-hand wall runs a->b and the left-hand wall runs b->a.
    addRoughFace(
      rockBatch,
      colliders,
      e.id,
      new THREE.Vector3(a.x + perp.x * half, a.y, a.z + perp.z * half),
      new THREE.Vector3(b.x + perp.x * half, b.y, b.z + perp.z * half),
      Math.min(a.y, b.y),
      e.height + Math.abs(rise),
      rough,
      rng,
      [],
    );
    addRoughFace(
      rockBatch,
      colliders,
      e.id,
      new THREE.Vector3(b.x - perp.x * half, b.y, b.z - perp.z * half),
      new THREE.Vector3(a.x - perp.x * half, a.y, a.z - perp.z * half),
      Math.min(a.y, b.y),
      e.height + Math.abs(rise),
      rough,
      rng,
      [],
    );

    const steps = Math.max(1, Math.round(Math.max(run / 3, Math.abs(rise) / SLOPE_STEP)));
    for (let s = 0; s < steps; s++) {
      const t = (s + 0.5) / steps;
      const centre = new THREE.Vector3(
        a.x + dir.x * run * t,
        a.y + rise * t - 0.4,
        a.z + dir.z * run * t,
      );
      const size = new THREE.Vector3(e.width + 1.4, 0.8, (run / steps) * 1.08);
      rockBatch.addBox(centre, size, angle);
      colliders.push(box(e.id, centre, size, angle, false, true));
      rockBatch.addBox(
        new THREE.Vector3(centre.x, centre.y + 0.4 + e.height + 0.7, centre.z),
        new THREE.Vector3(e.width + 1.4, 1.4 + range(rng, 0, rough), (run / steps) * 1.08),
        angle,
      );
    }
  }

  const rock = rockBatch.build(material, e.id);
  if (rock) group.add(rock);
  if (e.label && path.length) {
    const mid = path[Math.floor(path.length / 2)];
    group.add(namePlate(e.label, new THREE.Vector3(mid.x, mid.y + e.height - 0.8, mid.z), 1.0));
  }
  return { object: group, colliders };
}

function buildMannequin(e: MannequinEntity): EntityBuild {
  const height = e.height ?? 1.75;
  const group = new THREE.Group();
  group.position.set(e.position[0], e.position[1], e.position[2]);
  group.rotation.y = THREE.MathUtils.degToRad(e.rotationY ?? 0);

  const legH = height * 0.47;
  const torsoH = height * 0.34;
  const headR = height * 0.075;
  const body = new THREE.Mesh(
    new THREE.CapsuleGeometry(height * 0.13, torsoH, 4, 8),
    SHARED.mannequin,
  );
  body.position.y = legH + torsoH / 2 + height * 0.06;
  group.add(body);
  const legs = new THREE.Mesh(
    new THREE.CapsuleGeometry(height * 0.1, legH * 0.7, 4, 8),
    SHARED.mannequin,
  );
  legs.position.y = legH * 0.6;
  group.add(legs);
  const head = new THREE.Mesh(new THREE.SphereGeometry(headR, 10, 8), SHARED.mannequin);
  head.position.y = height - headR;
  group.add(head);

  return { object: group, colliders: [] };
}

function buildLandmark(e: LandmarkEntity, zoneColor: string): EntityBuild {
  const size = e.size ?? 3;
  const sprite = createTextSprite(e.text, {
    height: size,
    maxWidth: 24,
    bold: true,
    color: '#0e1116',
    background: e.color ?? zoneColor,
    border: 'rgba(255,255,255,0.5)',
  });
  sprite.position.set(e.position[0], e.position[1], e.position[2]);
  sprite.userData.isLabel = true;
  sprite.userData.labelKind = 'zone';
  return { object: sprite, colliders: [] };
}

const MARKER_COLORS: Record<string, number> = {
  interaction: 0x5ec7f0,
  hazard: 0xe0662f,
  hiding: 0x9b6fd0,
  shortcut: 0x54c98a,
  sightline: 0xe4c452,
  crossing: 0xe23f3f,
  objective: 0xffffff,
};

function buildMarker(e: MarkerEntity): EntityBuild {
  const group = new THREE.Group();
  group.position.set(e.position[0], e.position[1], e.position[2]);
  const color = MARKER_COLORS[e.kind] ?? 0xffffff;
  const pin = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.42),
    new THREE.MeshLambertMaterial({ color }),
  );
  pin.position.y = 1.5;
  group.add(pin);
  const stem = new THREE.Mesh(
    new THREE.CylinderGeometry(0.045, 0.045, 1.5, 6),
    new THREE.MeshLambertMaterial({ color }),
  );
  stem.position.y = 0.75;
  group.add(stem);
  const label = createTextSprite(e.label, {
    height: 0.42,
    maxWidth: 2.8,
    color: '#f2f6fa',
    background: 'rgba(10,13,17,0.78)',
    border: `#${color.toString(16).padStart(6, '0')}`,
  });
  label.position.y = 2.5;
  label.userData.isLabel = true;
  label.userData.labelKind = 'marker';
  group.add(label);
  return { object: group, colliders: [] };
}

/**
 * Fixture housing plus, optionally, a real point light. Housings are cheap and
 * carry most of the read; actual lights are rationed because each one costs
 * per-fragment work on every lit material in range.
 */
function buildLight(e: LightEntity): EntityBuild {
  const [sx, sz] = e.size ?? [2.4, 0.7];
  const rotY = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const colour = e.color ?? '#ffeccd';
  const group = new THREE.Group();

  const housing = new THREE.Mesh(UNIT.box, SHARED.steel);
  housing.position.set(e.position[0], e.position[1] + 0.11, e.position[2]);
  housing.scale.set(sx + 0.2, 0.22, sz + 0.2);
  housing.rotation.y = rotY;
  group.add(housing);

  const lens = new THREE.Mesh(UNIT.box, emissiveMaterial(colour));
  lens.position.set(e.position[0], e.position[1] - 0.01, e.position[2]);
  lens.scale.set(sx, 0.08, sz);
  lens.rotation.y = rotY;
  group.add(lens);

  if (e.cast) {
    const light = new THREE.PointLight(
      new THREE.Color(colour),
      e.intensity ?? 60,
      e.distance ?? 26,
      2,
    );
    light.position.set(e.position[0], e.position[1] - 0.4, e.position[2]);
    group.add(light);
  }
  return { object: group, colliders: [] };
}

function buildSpawn(e: SpawnEntity): EntityBuild {
  const group = new THREE.Group();
  group.position.set(e.position[0], e.position[1], e.position[2]);
  group.rotation.y = THREE.MathUtils.degToRad(e.rotationY ?? 0);
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.55, 0.85, 20),
    new THREE.MeshBasicMaterial({
      color: e.primary ? 0x6ee7a5 : 0x8fb4d8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8,
    }),
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = 0.06;
  group.add(ring);
  const label = createTextSprite(e.label, {
    height: 0.45,
    maxWidth: 3.2,
    color: '#eef4fa',
    background: 'rgba(10,13,17,0.7)',
  });
  label.position.y = 1.7;
  label.userData.isLabel = true;
  label.userData.labelKind = 'marker';
  group.add(label);
  return { object: group, colliders: [] };
}

export function buildEntity(entity: Entity, zoneColor: string): EntityBuild {
  switch (entity.type) {
    case 'floor':
      return buildFloor(entity, zoneColor);
    case 'wall':
      return buildWall(entity, zoneColor);
    case 'platform':
      return buildPlatform(entity, zoneColor);
    case 'stair':
      return buildStair(entity, zoneColor);
    case 'ramp':
      return buildRamp(entity, zoneColor);
    case 'catwalk':
      return buildCatwalk(entity, zoneColor);
    case 'machine':
      return buildMassing(entity, zoneColor, 'machine');
    case 'prop':
      return buildMassing(entity, zoneColor, 'prop');
    case 'conveyor':
      return buildConveyor(entity, zoneColor);
    case 'track':
      return buildTrack(entity);
    case 'pipe':
      return buildPipe(entity, zoneColor);
    case 'doorway':
      return buildDoorway(entity, zoneColor);
    case 'cavern':
      return buildCavern(entity, zoneColor);
    case 'tunnel':
      return buildTunnel(entity, zoneColor);
    case 'mannequin':
      return buildMannequin(entity);
    case 'landmark':
      return buildLandmark(entity, zoneColor);
    case 'marker':
      return buildMarker(entity);
    case 'spawn':
      return buildSpawn(entity);
    case 'light':
      return buildLight(entity);
    default: {
      const never: never = entity;
      throw new Error(`Unhandled entity type: ${JSON.stringify(never)}`);
    }
  }
}
