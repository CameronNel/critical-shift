import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('arrival');

/**
 * Arrival block, north-west corner. X -128..-96, Z -86..-58.
 * Lockers north, briefing south, lobby along the east side.
 * Two exits split the route: east onto S1 behind the production row, or south
 * into the haulage hall and the cart loop.
 */
export const ARRIVAL_ENTITIES: Entity[] = [
  a.floor('slab', [-112, 0, -72], [32, 28]),
  a.roof('lid', [-112, 6, -72], [32, 28]),

  ...roomWalls(a, 'shell', {
    min: [-128, -86],
    max: [-96, -58],
    height: 6,
    openings: [
      { side: 'w', at: -72, width: 6, top: 3.6 }, // site entrance
      { side: 'e', at: -64.5, width: 5, top: 4 }, // onto S1
      { side: 'e', at: -78, width: 4, top: 3.6 }, // west yard
      { side: 's', at: -112, width: 4, top: 3.6 }, // down to haulage
    ],
  }),

  a.wall('part.lockers', [-128, -76], [-104, -76], 3.2, {
    thickness: 0.3,
    gaps: [{ at: 10, width: 4 }],
  }),
  a.wall('part.lobby', [-104, -86], [-104, -62], 3.2, {
    thickness: 0.3,
    gaps: [
      { at: 12, width: 5 },
      { at: 21, width: 4 },
    ],
  }),

  a.prop('lockers.1', [-120, 0, -83], [9, 2.3, 1.4]),
  a.prop('lockers.2', [-120, 0, -79], [9, 2.3, 1.4]),
  a.prop('lockers.3', [-110, 0, -83], [7, 2.3, 1.4]),
  a.machine('bench.lockers', 'LOCKERS', [-116, 0, -77.5], [4, 1.1, 1.2]),

  a.platform('brief.dais', [-118, 0.3, -66], [16, 12], { label: 'SHIFT BRIEFING' }),
  a.machine('brief.board', 'BRIEFING BOARD', [-118, 0.3, -60.6], [10, 3.4, 0.5]),
  a.prop('brief.bench.1', [-118, 0.3, -69], [10, 0.44, 0.9]),
  a.prop('brief.bench.2', [-118, 0.3, -66.5], [10, 0.44, 0.9]),

  a.prop('suits.1', [-101, 0, -80], [1.4, 2.4, 6]),
  a.prop('suits.2', [-101, 0, -70], [1.4, 2.4, 6]),
  a.machine('decon', 'DECON', [-100, 0, -62], [5, 3.2, 5]),

  a.doorway('door.spine', [-96, 0, -64.5], 5, 4, { rotationY: 90, label: 'S1' }),
  a.doorway('door.south', [-112, 0, -58], 4, 3.6),

  a.spawn('spawn.start', [-112, 0, -72], 'Shift entrance', { primary: true, rotationY: 270 }),
  a.spawn('spawn.brief', [-118, 0.3, -66], 'Briefing'),

  a.marker('m.suits', [-101, 0, -75], 'interaction', 'Suit-up: the decision that costs time'),
  a.marker('m.split', [-98, 0, -70], 'shortcut', 'East = S1 behind the plant. South = the cart loop.'),

  a.mannequin('scale.1', [-114, 0, -80], { rotationY: 30 }),
  a.mannequin('scale.2', [-118, 0.3, -68], { rotationY: 180 }),
  a.mannequin('scale.3', [-100, 0, -66], { rotationY: 250 }),
];
