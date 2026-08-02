import type { Entity, Route, Vec2, Vec3, Zone } from './schema';

/**
 * Plan compaction.
 *
 * Travel time is the thing this facility gets wrong most easily: a meltdown is
 * only frightening if the run to the valves is short enough to attempt. So the
 * whole layout is authored at a comfortable drafting scale and then compacted
 * by a single factor before it is built.
 *
 * The compaction is deliberately **not** a uniform scale:
 *
 *   scaled      X and Z positions, wall runs, room footprints, machine
 *               footprints, distances along a wall to an opening
 *   not scaled  every vertical dimension, and every human-scale clearance —
 *               corridor and catwalk widths, stair widths, door widths, wall
 *               thickness, pipe radius, rock bore sections, ceiling heights
 *
 * That way the plan tightens without corridors becoming too narrow to pass in,
 * doors too small to drag a body through, or the reactor hall losing the height
 * that makes it worth looking at. A 1.75 m worker stays 1.75 m.
 *
 * Set to 1 to author and inspect at the uncompacted drafting scale.
 */
export const SITE_SCALE = 0.6;

const s = (n: number) => n * SITE_SCALE;

function scaleVec3(v: Vec3): Vec3 {
  return [s(v[0]), v[1], s(v[2])];
}

/** Wall endpoints are XZ only, so both components scale. */
function scaleVec2(v: Vec2): Vec2 {
  return [s(v[0]), s(v[1])];
}

/**
 * `size` means different things per type. For floors and platforms it is
 * [X, Z] and both scale. For machines and props it is [X, height, Z] and the
 * height must not.
 */
function scaleSize(value: unknown): unknown {
  if (!Array.isArray(value)) return value;
  if (value.length === 2) return scaleVec2(value as Vec2);
  if (value.length === 3) return scaleVec3(value as Vec3);
  return value;
}

export function scaleEntity(entity: Entity): Entity {
  const next = structuredClone(entity) as Entity & Record<string, unknown>;

  if (Array.isArray(next.position)) next.position = scaleVec3(next.position as Vec3);
  if (Array.isArray(next.size)) next.size = scaleSize(next.size);
  if (Array.isArray(next.path)) {
    next.path = (next.path as Vec3[]).map(scaleVec3);
  }
  for (const key of ['from', 'to'] as const) {
    const value = next[key];
    if (Array.isArray(value)) {
      next[key] = value.length === 2 ? scaleVec2(value as Vec2) : scaleVec3(value as Vec3);
    }
  }
  // Distance along a wall to an opening scales; the opening itself does not.
  if (Array.isArray(next.gaps)) {
    next.gaps = (next.gaps as { at: number }[]).map((gap) => ({ ...gap, at: s(gap.at) }));
  }
  // Cavern openings are offsets from the centre of a side.
  if (Array.isArray(next.openings)) {
    next.openings = (next.openings as { at: number }[]).map((o) => ({ ...o, at: s(o.at) }));
  }
  return next as Entity;
}

export function scaleZone(zone: Zone): Zone {
  return {
    ...zone,
    bounds: { min: scaleVec2(zone.bounds.min), max: scaleVec2(zone.bounds.max) },
    signAt: scaleVec3(zone.signAt),
  };
}

export function scaleRoute(route: Route): Route {
  return { ...route, path: route.path.map(scaleVec3) };
}
