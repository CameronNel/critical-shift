import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('arrival');

/**
 * Worker arrival block. X -120..-88, Z -18..+18, 6 m clear height.
 * Three bays: lockers north, briefing south-west, suit-up and decon south-east
 * next to the two exits that feed the rest of the site.
 */
export const ARRIVAL_ENTITIES: Entity[] = [
  a.floor('slab', [-104, 0, 0], [32, 36]),
  a.roof('lid', [-104, 6, 0], [32, 36]),

  ...roomWalls(a, 'shell', {
    min: [-120, -18],
    max: [-88, 18],
    height: 6,
    openings: [
      // Site entrance from the west approach.
      { side: 'w', at: 0, width: 6, top: 3.6 },
      // North route to the decline bridge and the crusher.
      { side: 'e', at: -10, width: 4.5, top: 3.6 },
      // South route to the yard, storage and the long way round the decline.
      { side: 'e', at: 12, width: 4.5, top: 3.6 },
    ],
  }),

  // Locker bay (north). Broad blocks, not individual lockers.
  a.wall('part.lockers', [-120, -4], [-88, -4], 3.2, {
    thickness: 0.3,
    gaps: [
      { at: 8, width: 4 },
      { at: 26, width: 4 },
    ],
  }),
  a.prop('lockers.1', [-115, 0, -14], [9, 2.3, 1.4]),
  a.prop('lockers.2', [-115, 0, -9], [9, 2.3, 1.4]),
  a.prop('lockers.3', [-99, 0, -14], [9, 2.3, 1.4]),
  a.prop('lockers.4', [-99, 0, -9], [9, 2.3, 1.4]),
  a.machine('bench.lockers', 'LOCKERS', [-107, 0, -16], [4, 1.1, 1.2]),

  // Briefing bay (south-west).
  a.wall('part.brief', [-104, -4], [-104, 18], 3.2, {
    thickness: 0.3,
    gaps: [{ at: 12, width: 5 }],
  }),
  a.platform('brief.dais', [-112, 0.3, 8], [12, 12], { label: 'SHIFT BRIEFING' }),
  a.machine('brief.board', 'BRIEFING BOARD', [-112, 0.3, 13.4], [10, 3.4, 0.5]),
  a.prop('brief.bench.1', [-112, 0.3, 5], [8, 0.5, 0.9]),
  a.prop('brief.bench.2', [-112, 0.3, 7.5], [8, 0.5, 0.9]),

  // Suit-up and decontamination (south-east), on the way out to the plant.
  a.prop('suits.1', [-99, 0, 0], [1.4, 2.4, 6]),
  a.prop('suits.2', [-94, 0, 0], [1.4, 2.4, 6]),
  a.machine('decon', 'DECON', [-93, 0, 12], [6, 3.2, 6]),

  a.doorway('door.east.north', [-88, 0, -10], 4.5, 3.6, { rotationY: 90 }),
  a.doorway('door.east.south', [-88, 0, 12], 4.5, 3.6, { rotationY: 90 }),

  a.spawn('spawn.start', [-110, 0, 2], 'Shift entrance', { primary: true, rotationY: 90 }),
  a.spawn('spawn.brief', [-112, 0.3, 8], 'Briefing'),

  a.marker('m.suits', [-96, 0, 4], 'interaction', 'Suit-up: the decision that costs time'),
  a.marker('m.exit.choice', [-90, 0, 1], 'shortcut', 'North exit = bridge. South exit = long way'),

  a.mannequin('scale.1', [-106, 0, -8], { rotationY: 30 }),
  a.mannequin('scale.2', [-112, 0.3, 6], { rotationY: 180 }),
  a.mannequin('scale.3', [-95, 0, 6], { rotationY: 250 }),
];
