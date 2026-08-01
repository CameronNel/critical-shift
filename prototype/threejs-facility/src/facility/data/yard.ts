import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('yard');

/**
 * Surface grade is authored as strips with deliberate holes: the haulage
 * decline, the crusher hall footprint, the maintenance stairwell and the
 * cooling hall. Hiding the grade layer therefore exposes the whole
 * underground level for inspection without deleting any interior floor.
 */
export const YARD_ENTITIES: Entity[] = [
  // Row 1 (Z -78..-26): unbroken northern apron.
  a.grade('g.r1', [-8, -0.02, -52], [268, 52]),

  // Row 2 (Z -26..-20): around the crusher hall's receiving end.
  a.grade('g.r2.w', [-106, -0.02, -23], [72, 6]),
  a.grade('g.r2.e', [45, -0.02, -23], [162, 6]),

  // Row 3 (Z -20..12): around the decline and the crusher hall.
  a.grade('g.r3.w', [-113, -0.02, -4], [58, 32]),
  a.grade('g.r3.trenchE', [-73, -0.02, -4], [6, 32]),
  a.grade('g.r3.e', [45, -0.02, -4], [162, 32]),

  // Row 4 (Z 12..30): around the decline and the maintenance stairwell.
  a.grade('g.r4.w', [-113, -0.02, 21], [58, 18]),
  a.grade('g.r4.mid', [-26, -0.02, 21], [100, 18]),
  a.grade('g.r4.e', [79, -0.02, 21], [94, 18]),

  // Row 5 (Z 30..32): around the decline only.
  a.grade('g.r5.w', [-113, -0.02, 31], [58, 2]),
  a.grade('g.r5.e', [21, -0.02, 31], [202, 2]),

  // Row 6 (Z 32..40): around the decline and the cooling hall.
  a.grade('g.r6.w', [-113, -0.02, 36], [58, 8]),
  a.grade('g.r6.mid', [-5, -0.02, 36], [142, 8]),
  a.grade('g.r6.e', [119, -0.02, 36], [14, 8]),

  // Row 7 (Z 40..58): the decline has surfaced; only cooling is missing.
  a.grade('g.r7.w', [-38, -0.02, 49], [208, 18]),
  a.grade('g.r7.e', [119, -0.02, 49], [14, 18]),

  // Row 8: southern site edge.
  a.grade('g.r8', [-8, -0.02, 62], [268, 8]),

  // Site perimeter. Stops you wandering off without a hard invisible wall.
  a.wall('perim.n', [-142, -78], [126, -78], 10),
  a.wall('perim.e', [126, -78], [126, 66], 10),
  a.wall('perim.s', [126, 66], [-142, 66], 10),
  a.wall('perim.w', [-142, 66], [-142, -78], 10),

  // Bridges over the decline. The north one is the fast way to the crusher and
  // the best place to watch a loaded cart come up at you.
  a.catwalk('bridge.north', [[-87, 0.15, -10], [-73, 0.15, -10]], 3, {
    label: 'DECLINE BRIDGE',
    railings: 'both',
    supports: false,
  }),
  a.catwalk('bridge.south', [[-87, 0.15, 26], [-73, 0.15, 26]], 2.2, {
    railings: 'both',
    supports: false,
  }),

  a.marker('m.bridge', [-80, 0.2, -10], 'sightline', 'Watch the decline from here'),
  a.marker('m.yard.mid', [-2, 0, 30], 'shortcut', 'Open yard crossing: fast, fully exposed'),

  a.mannequin('scale.yard', [-60, 0, 30], { rotationY: 200 }),
];
