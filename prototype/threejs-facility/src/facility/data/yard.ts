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
  // Row 1: everything north of the plant.
  a.grade('g.north', [-8, -0.02, -49], [268, 58]),

  // Row 2 (Z -20..12): split around the decline and the crusher hall.
  a.grade('g.mid.w', [-113, -0.02, -4], [58, 32]),
  a.grade('g.mid.trenchE', [-73, -0.02, -4], [6, 32]),
  a.grade('g.mid.e', [45, -0.02, -4], [162, 32]),

  // Row 3 (Z 12..30): split around the decline and the maintenance stairwell.
  a.grade('g.s1.w', [-113, -0.02, 21], [58, 18]),
  a.grade('g.s1.mid', [-26, -0.02, 21], [100, 18]),
  a.grade('g.s1.e', [79, -0.02, 21], [94, 18]),

  // Row 4 (Z 30..40): split around the decline and the cooling hall.
  a.grade('g.s2.w', [-113, -0.02, 35], [58, 10]),
  a.grade('g.s2.mid', [-6, -0.02, 35], [140, 10]),
  a.grade('g.s2.e', [120, -0.02, 35], [12, 10]),

  // Row 5 (Z 40..60): only the cooling hall is missing.
  a.grade('g.s3.w', [-39, -0.02, 50], [206, 20]),
  a.grade('g.s3.e', [120, -0.02, 50], [12, 20]),

  // Row 6: southern site edge.
  a.grade('g.south', [-8, -0.02, 63], [268, 6]),

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
