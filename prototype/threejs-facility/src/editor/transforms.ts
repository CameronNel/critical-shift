import type { Entity, Vec2, Vec3 } from '../facility/schema';

type Mutable = Record<string, unknown>;

const POINT_KEYS = ['position'] as const;
const ENDPOINT_KEYS = ['from', 'to'] as const;
/** Scalars that describe an extent and therefore follow a uniform scale. */
const EXTENT_KEYS = [
  'width',
  'height',
  'thickness',
  'radius',
  'gauge',
  'size',
  'base',
] as const;

function isVec(value: unknown, length: number): value is number[] {
  return Array.isArray(value) && value.length === length && value.every((n) => typeof n === 'number');
}

export function cloneEntity(entity: Entity): Entity {
  return structuredClone(entity);
}

/**
 * A representative point for the entity: what the gizmo attaches to and what
 * rotation and scale operate around.
 */
export function entityAnchor(entity: Entity): Vec3 {
  const record = entity as unknown as Mutable;
  if (isVec(record.position, 3)) return [...(record.position as Vec3)];
  if (Array.isArray(record.path) && record.path.length > 0) {
    const path = record.path as Vec3[];
    const sum: Vec3 = [0, 0, 0];
    for (const point of path) {
      sum[0] += point[0];
      sum[1] += point[1];
      sum[2] += point[2];
    }
    return [sum[0] / path.length, sum[1] / path.length, sum[2] / path.length];
  }
  const from = record.from;
  const to = record.to;
  if (isVec(from, 3) && isVec(to, 3)) {
    return [(from[0] + to[0]) / 2, (from[1] + to[1]) / 2, (from[2] + to[2]) / 2];
  }
  if (isVec(from, 2) && isVec(to, 2)) {
    const base = typeof record.base === 'number' ? record.base : 0;
    const height = typeof record.height === 'number' ? record.height : 0;
    return [(from[0] + to[0]) / 2, base + height / 2, (from[1] + to[1]) / 2];
  }
  return [0, 0, 0];
}

/** Apply `fn` to every geometric point the entity owns. */
function mapPoints(entity: Entity, fn: (p: Vec3) => Vec3): void {
  const record = entity as unknown as Mutable;
  for (const key of POINT_KEYS) {
    if (isVec(record[key], 3)) record[key] = fn(record[key] as Vec3);
  }
  for (const key of ENDPOINT_KEYS) {
    const value = record[key];
    if (isVec(value, 3)) {
      record[key] = fn(value as Vec3);
    } else if (isVec(value, 2)) {
      // Wall endpoints are XZ only; height lives in `base` and `height`.
      const base = typeof record.base === 'number' ? record.base : 0;
      const moved = fn([value[0], base, value[1]]);
      record[key] = [moved[0], moved[2]] satisfies Vec2;
    }
  }
  if (Array.isArray(record.path)) {
    record.path = (record.path as Vec3[]).map(fn);
  }
}

export function translateEntity(entity: Entity, delta: Vec3): Entity {
  const next = cloneEntity(entity);
  const record = next as unknown as Mutable;
  const hadFlatEndpoints = isVec(record.from, 2);
  mapPoints(next, (p) => [p[0] + delta[0], p[1] + delta[1], p[2] + delta[2]]);
  // Walls carry their vertical position in `base`, which mapPoints cannot move.
  if (hadFlatEndpoints && typeof record.base === 'number') {
    record.base = (record.base as number) + delta[1];
  } else if (hadFlatEndpoints && delta[1] !== 0) {
    record.base = delta[1];
  }
  return next;
}

export function rotateEntity(entity: Entity, degrees: number): Entity {
  const next = cloneEntity(entity);
  const record = next as unknown as Mutable;
  const anchor = entityAnchor(entity);
  const angle = (degrees * Math.PI) / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  mapPoints(next, (p) => {
    const dx = p[0] - anchor[0];
    const dz = p[2] - anchor[2];
    return [anchor[0] + dx * cos + dz * sin, p[1], anchor[2] - dx * sin + dz * cos];
  });
  if (typeof record.rotationY === 'number' || 'rotationY' in record) {
    record.rotationY = ((record.rotationY as number) ?? 0) + degrees;
  } else if (supportsRotationY(entity)) {
    record.rotationY = degrees;
  }
  return next;
}

function supportsRotationY(entity: Entity): boolean {
  switch (entity.type) {
    case 'floor':
    case 'platform':
    case 'machine':
    case 'prop':
    case 'doorway':
    case 'cavern':
    case 'mannequin':
    case 'spawn':
      return true;
    default:
      return false;
  }
}

export function scaleEntity(entity: Entity, factor: number): Entity {
  const next = cloneEntity(entity);
  const record = next as unknown as Mutable;
  const anchor = entityAnchor(entity);
  mapPoints(next, (p) => [
    anchor[0] + (p[0] - anchor[0]) * factor,
    anchor[1] + (p[1] - anchor[1]) * factor,
    anchor[2] + (p[2] - anchor[2]) * factor,
  ]);
  for (const key of EXTENT_KEYS) {
    const value = record[key];
    if (typeof value === 'number' && key !== 'base') record[key] = value * factor;
    if (Array.isArray(value)) record[key] = (value as number[]).map((n) => n * factor);
  }
  return next;
}

export interface EditableField {
  key: string;
  label: string;
  /** Component labels, e.g. ['x','y','z']. */
  parts: string[];
  values: number[];
}

/** Numeric fields the inspector exposes for direct editing. */
export function editableFields(entity: Entity): EditableField[] {
  const record = entity as unknown as Mutable;
  const fields: EditableField[] = [];
  if (isVec(record.position, 3)) {
    fields.push({ key: 'position', label: 'Position', parts: ['x', 'y', 'z'], values: [...(record.position as number[])] });
  }
  if (isVec(record.from, 3)) {
    fields.push({ key: 'from', label: 'From', parts: ['x', 'y', 'z'], values: [...(record.from as number[])] });
  } else if (isVec(record.from, 2)) {
    fields.push({ key: 'from', label: 'From', parts: ['x', 'z'], values: [...(record.from as number[])] });
  }
  if (isVec(record.to, 3)) {
    fields.push({ key: 'to', label: 'To', parts: ['x', 'y', 'z'], values: [...(record.to as number[])] });
  } else if (isVec(record.to, 2)) {
    fields.push({ key: 'to', label: 'To', parts: ['x', 'z'], values: [...(record.to as number[])] });
  }
  if (isVec(record.size, 3)) {
    fields.push({ key: 'size', label: 'Size', parts: ['x', 'y', 'z'], values: [...(record.size as number[])] });
  } else if (isVec(record.size, 2)) {
    fields.push({ key: 'size', label: 'Size', parts: ['x', 'z'], values: [...(record.size as number[])] });
  }
  for (const key of ['width', 'height', 'thickness', 'radius', 'base'] as const) {
    if (typeof record[key] === 'number') {
      fields.push({ key, label: key[0].toUpperCase() + key.slice(1), parts: [''], values: [record[key] as number] });
    }
  }
  if (typeof record.rotationY === 'number') {
    fields.push({ key: 'rotationY', label: 'Rotation Y°', parts: [''], values: [record.rotationY as number] });
  }
  return fields;
}

export function setField(entity: Entity, key: string, index: number, value: number): Entity {
  const next = cloneEntity(entity);
  const record = next as unknown as Mutable;
  const current = record[key];
  if (Array.isArray(current)) {
    const copy = [...(current as number[])];
    copy[index] = value;
    record[key] = copy;
  } else {
    record[key] = value;
  }
  return next;
}

/** Fresh id for a duplicate, avoiding collisions with what already exists. */
export function duplicateId(id: string, taken: (candidate: string) => boolean): string {
  const base = id.replace(/\.copy(\d+)?$/, '');
  for (let n = 1; n < 500; n++) {
    const candidate = n === 1 ? `${base}.copy` : `${base}.copy${n}`;
    if (!taken(candidate)) return candidate;
  }
  return `${base}.copy.${Date.now()}`;
}
