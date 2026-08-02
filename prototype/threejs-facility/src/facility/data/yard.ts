import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('yard');

/**
 * Surface grade, the site perimeter, and the two circulation spines that are
 * not part of any single block:
 *
 *   S1  north spine corridor  - straight run behind the production row, from
 *                               arrival to the compliance approach
 *   the reactor entrance link  - fuel block to the reactor's one worker door,
 *                               which the whole shift has to funnel through
 *
 * Grade is authored as strips with holes for the crusher pit and the cooling
 * cut, so hiding the ground layer exposes the service datum below.
 */
export const YARD_ENTITIES: Entity[] = [
  a.grade('g.n', [-55, -0.02, -86.5], [250, 57]),
  a.grade('g.mid.w', [-132, -0.02, -47], [96, 22]),
  a.grade('g.mid.e', [4, -0.02, -47], [132, 22]),
  // Centre band, cut around the mine adit.
  a.grade('g.c.n', [-56, -0.02, -21], [252, 30]),
  a.grade('g.c.adit.w', [-155, -0.02, 0], [54, 12]),
  a.grade('g.c.adit.e', [-21, -0.02, 0], [182, 12]),
  a.grade('g.c.s', [-56, -0.02, 17], [252, 22]),
  // Cooling cut and the storage stairwell.
  a.grade('g.cut.w', [-121, -0.02, 31], [122, 6]),
  a.grade('g.cut.m', [-12, -0.02, 31], [80, 6]),
  a.grade('g.cut.e', [65, -0.02, 31], [10, 6]),
  a.grade('g.s.w', [-121, -0.02, 41], [122, 14]),
  a.grade('g.s.m', [-12, -0.02, 41], [80, 14]),
  a.grade('g.s.e', [65, -0.02, 41], [10, 14]),
  a.grade('g.s2.w', [-77, -0.02, 55], [210, 14]),
  a.grade('g.s2.e', [65, -0.02, 55], [10, 14]),
  a.grade('g.s', [-55, -0.02, 71], [250, 18]),

  a.wall('perim.n', [-182, -122], [74, -122], 10),
  a.wall('perim.e', [74, -122], [74, 84], 10),
  a.wall('perim.s', [74, 84], [-182, 84], 10),
  a.wall('perim.w', [-182, 84], [-182, -122], 10),

  // S1: north spine. The production blocks' own north walls form its south
  // side, so stepping out of any of them puts you straight into the corridor.
  a.floor('spine.floor', [-37, 0, -64.5], [118, 5], { label: 'S1 — NORTH SPINE' }),
  a.wall('spine.n', [-96, -67], [22, -67], 5),
  a.roof('spine.lid', [-37, 5, -64.5], [118, 5]),

  // The last leg of the production row: out of the fuel block's south door and
  // straight into the reactor's only worker entrance. The whole shift funnels
  // through these eight metres, which is why the reactor has no second way in.
  a.floor('link.reactor', [8, 0, -28], [6, 8], { label: 'REACTOR ENTRANCE' }),
  a.roof('link.reactor.lid', [8, 5, -28], [6, 8]),
  a.wall('link.reactor.e', [11, -32], [11, -24], 5),
  a.wall('link.reactor.w', [5, -24], [5, -32], 5),

  // S2: the short hop between the haulage hall and storage.
  a.floor('s2', [-75, 0, 29], [22, 6], { label: 'S2' }),
  a.roof('s2.lid', [-75, 4.5, 29], [22, 6]),

  // S3: medical across to the cooling lid, avoiding the reactor entirely.
  a.floor('s3', [11, 0, 50], [34, 5], { label: 'S3' }),

  a.marker('m.spine', [-37, 0, -64.5], 'shortcut', 'S1: straight behind the whole production row'),

  a.mannequin('scale.link', [8, 0, -28], { rotationY: 180 }),
  a.mannequin('scale.spine', [-60, 0, -64.5], { rotationY: 90 }),
];
