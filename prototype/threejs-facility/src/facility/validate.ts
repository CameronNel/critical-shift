import {
  FACILITY_FORMAT,
  type Entity,
  type FacilityDoc,
  type Vec2,
  type Vec3,
} from './schema';

export interface ValidationIssue {
  level: 'error' | 'warning';
  where: string;
  message: string;
}

const LIMITS = { minX: -200, maxX: 200, minY: -60, maxY: 80, minZ: -140, maxZ: 120 };

function finiteVec(value: unknown, length: number): boolean {
  return (
    Array.isArray(value) &&
    value.length === length &&
    value.every((n) => typeof n === 'number' && Number.isFinite(n))
  );
}

function checkPoint(issues: ValidationIssue[], where: string, p: Vec3): void {
  if (p[0] < LIMITS.minX || p[0] > LIMITS.maxX || p[2] < LIMITS.minZ || p[2] > LIMITS.maxZ) {
    issues.push({ level: 'warning', where, message: `point ${p.join(', ')} is outside the site` });
  }
  if (p[1] < LIMITS.minY || p[1] > LIMITS.maxY) {
    issues.push({ level: 'warning', where, message: `point ${p.join(', ')} is outside the site height` });
  }
}

/**
 * Structural validation for the facility document. Used both by the JSON
 * importer and by `npm run validate`, so a bad hand edit fails loudly instead
 * of producing a silently broken map.
 */
export function validateFacility(doc: unknown): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  if (typeof doc !== 'object' || doc === null) {
    return [{ level: 'error', where: 'document', message: 'not an object' }];
  }
  const d = doc as Partial<FacilityDoc>;
  if (d.format !== FACILITY_FORMAT) {
    issues.push({
      level: 'error',
      where: 'document',
      message: `format must be "${FACILITY_FORMAT}", got ${JSON.stringify(d.format)}`,
    });
  }
  if (!Array.isArray(d.zones) || d.zones.length === 0) {
    issues.push({ level: 'error', where: 'zones', message: 'missing or empty' });
  }
  if (!Array.isArray(d.entities)) {
    issues.push({ level: 'error', where: 'entities', message: 'missing' });
    return issues;
  }

  const zoneIds = new Set((d.zones ?? []).map((z) => z.id));
  const seen = new Set<string>();
  let primarySpawns = 0;

  for (const entity of d.entities as Entity[]) {
    const where = entity?.id ?? '(missing id)';
    if (!entity || typeof entity.id !== 'string' || entity.id.length === 0) {
      issues.push({ level: 'error', where, message: 'entity has no id' });
      continue;
    }
    if (seen.has(entity.id)) {
      issues.push({ level: 'error', where, message: 'duplicate entity id' });
    }
    seen.add(entity.id);
    if (!zoneIds.has(entity.zone)) {
      issues.push({ level: 'error', where, message: `unknown zone "${entity.zone}"` });
    }

    const record = entity as unknown as Record<string, unknown>;
    for (const key of ['position'] as const) {
      if (key in record && !finiteVec(record[key], 3)) {
        issues.push({ level: 'error', where, message: `${key} must be three finite numbers` });
      }
    }
    for (const key of ['from', 'to'] as const) {
      if (key in record) {
        const value = record[key];
        if (!finiteVec(value, 3) && !finiteVec(value, 2)) {
          issues.push({ level: 'error', where, message: `${key} must be a finite vector` });
        }
      }
    }
    if ('size' in record && !finiteVec(record.size, 3) && !finiteVec(record.size, 2)) {
      issues.push({ level: 'error', where, message: 'size must be a finite vector' });
    }
    if ('path' in record) {
      const path = record.path;
      if (!Array.isArray(path) || path.length < 2) {
        issues.push({ level: 'error', where, message: 'path needs at least two points' });
      } else {
        for (const point of path) {
          if (!finiteVec(point, 3)) {
            issues.push({ level: 'error', where, message: 'path point must be three numbers' });
          } else {
            checkPoint(issues, where, point as Vec3);
          }
        }
      }
    }
    if (finiteVec(record.position, 3)) checkPoint(issues, where, record.position as Vec3);
    if (finiteVec(record.size, 2)) {
      const size = record.size as Vec2;
      if (size[0] <= 0 || size[1] <= 0) {
        issues.push({ level: 'error', where, message: 'size must be positive' });
      }
    }
    if (finiteVec(record.size, 3)) {
      const size = record.size as Vec3;
      if (size[0] <= 0 || size[1] <= 0 || size[2] < 0) {
        issues.push({ level: 'error', where, message: 'size must be positive' });
      }
    }
    if (entity.type === 'spawn' && entity.primary) primarySpawns++;
  }

  if (primarySpawns === 0) {
    issues.push({ level: 'error', where: 'spawns', message: 'no spawn is marked primary' });
  } else if (primarySpawns > 1) {
    issues.push({ level: 'warning', where: 'spawns', message: 'more than one primary spawn' });
  }

  for (const route of d.routes ?? []) {
    if (!Array.isArray(route.path) || route.path.length < 2) {
      issues.push({ level: 'error', where: route.id ?? 'route', message: 'route path too short' });
    }
  }

  return issues;
}

export function hasErrors(issues: ValidationIssue[]): boolean {
  return issues.some((issue) => issue.level === 'error');
}

export function formatIssues(issues: ValidationIssue[]): string {
  return issues.map((i) => `${i.level.toUpperCase()} ${i.where}: ${i.message}`).join('\n');
}
