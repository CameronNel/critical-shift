import type { Entity, Vec2, Vec3 } from '../schema';
import { zoneAuthor } from './authoring';

const r = zoneAuthor('reactor');
const c = zoneAuthor('control');
const SCALE = 0.6;
const d = (n: number) => n / SCALE;
const p3 = (x: number, y: number, z: number): Vec3 => [d(x), y, d(z)];
const s2 = (x: number, z: number): Vec2 => [d(x), d(z)];
const s3 = (x: number, y: number, z: number): Vec3 => [d(x), y, d(z)];
const tag = (name: string, ...rest: string[]) => ['reactor-building', `asset:${name}`, ...rest];

const WALL = '#dce4e7';
const CEILING = '#aebbc0';
const DARK = '#263239';
const GREEN = '#6e847b';
const SCREEN = '#2bbbd7';

/**
 * Corrections intentionally live separately from the large authored scene:
 * they keep the first clean-slate commit reviewable while preventing a solid
 * exterior mass from becoming an invisible walk-collision through the hall.
 */
export const REACTOR_BUILDING_FIXUPS: Entity[] = [
  // Eight-sided interior shell, 24 m clear span and 16 m high. Openings retain
  // the gameplay links while the exterior mass remains collision-free scenery.
  r.wall('building.shell.n', [d(-6), d(-12)], [d(6), d(-12)], 16, {
    thickness: d(0.35), color: WALL,
    gaps: [{ at: d(6), width: d(3.2), top: 4.0 }],
    tags: tag('building.shell.n', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.ne', [d(6), d(-12)], [d(12), d(-6)], 16, {
    thickness: d(0.35), color: WALL, tags: tag('building.shell.ne', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.e', [d(12), d(-6)], [d(12), d(6)], 16, {
    thickness: d(0.35), color: WALL,
    gaps: [{ at: d(6), width: d(3.0), top: 4.0 }],
    tags: tag('building.shell.e', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.se', [d(12), d(6)], [d(6), d(12)], 16, {
    thickness: d(0.35), color: WALL, tags: tag('building.shell.se', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.s', [d(6), d(12)], [d(-6), d(12)], 16, {
    thickness: d(0.35), color: WALL,
    gaps: [{ at: d(6), width: d(3.0), top: 4.0 }],
    tags: tag('building.shell.s', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.sw', [d(-6), d(12)], [d(-12), d(6)], 16, {
    thickness: d(0.35), color: WALL, tags: tag('building.shell.sw', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.w', [d(-12), d(6)], [d(-12), d(-6)], 16, {
    thickness: d(0.35), color: WALL,
    gaps: [{ at: d(6), width: d(3.4), top: 4.2 }],
    tags: tag('building.shell.w', 'interior-shell', 'blender:separate'),
  }),
  r.wall('building.shell.nw', [d(-12), d(-6)], [d(-6), d(-12)], 16, {
    thickness: d(0.35), color: WALL, tags: tag('building.shell.nw', 'interior-shell', 'blender:separate'),
  }),

  // Ceiling plates leave a central service slot around the actuator support.
  r.roof('building.ceiling.n', p3(0, 16, -7.5), s2(24, 9), {
    color: CEILING, tags: tag('building.ceiling.n', 'ceiling', 'blender:separate'),
  }),
  r.roof('building.ceiling.s', p3(0, 16, 7.5), s2(24, 9), {
    color: CEILING, tags: tag('building.ceiling.s', 'ceiling', 'blender:separate'),
  }),
  r.roof('building.ceiling.w', p3(-8.5, 16, 0), s2(7, 6), {
    color: CEILING, tags: tag('building.ceiling.w', 'ceiling', 'blender:separate'),
  }),
  r.roof('building.ceiling.e', p3(8.5, 16, 0), s2(7, 6), {
    color: CEILING, tags: tag('building.ceiling.e', 'ceiling', 'blender:separate'),
  }),

  // Exterior building envelope is visual only. Individual annexes retain their
  // own collisions, but the enclosing block must never fill the playable hall.
  r.prop('building.exterior.skin.n', p3(0, 0, -14.2), s3(31, 15.5, 0.45), {
    color: WALL, collision: false, tags: tag('building.exterior.skin.n', 'exterior-skin', 'blender:separate'),
  }),
  r.prop('building.exterior.skin.s', p3(0, 0, 14.2), s3(31, 15.5, 0.45), {
    color: WALL, collision: false, tags: tag('building.exterior.skin.s', 'exterior-skin', 'blender:separate'),
  }),
  r.prop('building.exterior.skin.w', p3(-15.3, 0, 0), s3(0.45, 15.5, 28), {
    color: WALL, collision: false, tags: tag('building.exterior.skin.w', 'exterior-skin', 'blender:separate'),
  }),
  r.prop('building.exterior.skin.e', p3(15.3, 0, 0), s3(0.45, 15.5, 28), {
    color: WALL, collision: false, tags: tag('building.exterior.skin.e', 'exterior-skin', 'blender:separate'),
  }),
];

function controlDesk(name: string, label: string, z: number): Entity[] {
  return [
    c.machine(`${name}.body`, label, p3(-11.8, 5.5, z), s3(2.0, 1.1, 0.9), {
      rotationY: 90, color: GREEN,
      tags: tag(`${name}.body`, 'control-room', 'console', 'blender:separate'),
    }),
    c.prop(`${name}.screen`, p3(-11.35, 6.72, z), s3(1.15, 0.55, 0.08), {
      rotationY: 90, color: SCREEN, collision: false, label,
      tags: tag(`${name}.screen`, 'control-room', 'screen', 'emissive', 'blender:replaceable-screen'),
    }),
    c.prop(`${name}.chair`, p3(-10.2, 5.5, z), s3(0.7, 1.0, 0.7), {
      color: DARK, tags: tag(`${name}.chair`, 'control-room', 'chair', 'blender:separate'),
    }),
  ];
}

export const REACTOR_BUILDING_CONTROL_FIXUPS: Entity[] = [
  ...controlDesk('building.control.corrected.core', 'CORE STATUS', -6.2),
  ...controlDesk('building.control.corrected.grid', 'GRID / TURBINE', -3.8),
];
