import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('refinery');

/**
 * Refinery. X -32..+24, Z -34..+22, 18 m clear.
 * Three stages north to south of the belt line, circulation south of them.
 * Four usable elevations: floor 0, mezzanine +5, aisle catwalk +10, gantry +14.
 * The belt line is continuous from the crusher to fuel, so a bad batch has an
 * unbroken path downstream — which is the whole point of the room.
 */
export const REFINERY_ENTITIES: Entity[] = [
  a.floor('slab', [-4, 0, -6], [56, 56]),
  a.roof('lid', [-4, 18, -6], [56, 56]),

  ...roomWalls(a, 'shell', {
    min: [-32, -34],
    max: [24, 22],
    height: 18,
    openings: [
      { side: 'w', at: -7, width: 7, bottom: 0, top: 9 }, // crushed ore belt
      { side: 'w', at: 3, width: 4, bottom: 4.5, top: 8 }, // crusher high link
      { side: 'w', at: 8, width: 4, top: 3.6 }, // ground route from crusher
      { side: 'e', at: -2, width: 5, top: 4 }, // fuel corridor
      { side: 'e', at: -10, width: 5, bottom: 2.5, top: 8 }, // dryer belt out
      { side: 'n', at: -24, width: 4, top: 3.6 }, // north yard door
      { side: 'n', at: -4, width: 16, bottom: 9.5, top: 14 }, // clerestory
      { side: 's', at: 6, width: 4, top: 3.6 }, // storage door
    ],
  }),

  // Three major operations. Bold masses, no internals.
  a.machine('sorter', 'SORTER', [-21, 0, -16], [12, 9, 16]),
  a.machine('processor', 'PROCESSOR', [0, 0, -14], [14, 12, 14], { shape: 'cylinder' }),
  a.machine('dryer', 'DRYER', [16, 0, -12], [12, 10, 16]),

  a.conveyor('conv.sort', [[-15, 6.5, -16], [-9, 6.8, -15], [-6, 7, -14]], 2.2, {
    label: 'SORTED',
  }),
  a.conveyor('conv.proc', [[7, 7.5, -14], [10, 7, -12]], 2.2, { label: 'PROCESSED' }),
  a.conveyor('conv.dry', [[22, 6, -12], [27, 5.5, -11], [34, 4.5, -10]], 2.2, {
    label: 'DRIED → FUEL',
  }),

  // Mezzanine ring: the working level people actually cross the room on.
  a.platform('mezz.south', [-4, 5, 10], [52, 16], {
    label: 'REFINERY MEZZANINE',
    railings: ['n'],
    supports: true,
  }),
  a.platform('mezz.north', [-4, 5, -30], [52, 6], { railings: ['s'], supports: true }),

  // Aisle catwalk between sorter and processor, and the gantry over everything.
  a.catwalk('cat.aisle', [[-11, 10, -30], [-11, 10, 4]], 2.2, { label: 'CENTRE AISLE' }),
  a.catwalk(
    'cat.gantry',
    [
      [-29, 14, -30],
      [-29, 14, -22],
      [18, 14, -22],
      [18, 14, 4],
    ],
    2.2,
    { label: 'UPPER GANTRY' },
  ),
  a.catwalk('cat.beltaccess', [[-18, 5, -28], [-18, 6, -22], [-16, 6.6, -17]], 1.6, {
    railings: 'left',
  }),

  a.stair('stair.ground', [-28, 0, -6], [-28, 5, 2], 2.2),
  a.stair('stair.mezz', [-11, 5, 4], [-11, 10, -4], 1.8),
  a.stair('stair.gantry', [-11, 10, -28], [-11, 14, -22], 1.6),
  a.stair('stair.east', [20, 5, 4], [20, 0, 12], 2),

  a.prop('batch.1', [-6, 0, 4], [3, 2.2, 3]),
  a.prop('batch.2', [-2, 0, 4], [3, 2.2, 3]),
  a.prop('batch.3', [2, 0, 4], [3, 2.2, 3]),
  a.prop('console.sorter', [-21, 0, -6], [3, 1.2, 1]),
  a.prop('console.proc', [0, 0, -5], [3, 1.2, 1]),
  a.prop('console.dryer', [16, 0, -2], [3, 1.2, 1]),

  a.doorway('door.west', [-32, 0, 8], 4, 3.6, { rotationY: 90 }),
  a.doorway('door.east', [24, 0, -2], 5, 4, { rotationY: 90 }),
  a.doorway('door.north', [-24, 0, -34], 4, 3.6),
  a.doorway('door.south', [6, 0, 22], 4, 3.6),

  a.spawn('spawn.floor', [-4, 0, 8], 'Refinery floor'),
  a.spawn('spawn.gantry', [-29, 14, -26], 'Refinery gantry'),

  a.marker('m.beltwalk', [-16, 6.8, -17], 'shortcut', 'Belt walk: mezzanine to fuel, no stairs'),
  a.marker('m.clerestory', [-4, 14, -22], 'sightline', 'Clerestory: see the compliance road'),
  a.marker('m.pinch', [-11, 0, -6], 'hazard', 'Pinch point under the sorter discharge'),
  a.marker('m.downstream', [10, 7, -12], 'objective', 'A bad batch leaves here and never stops'),
  a.marker('m.storage', [6, 0, 20], 'shortcut', 'South door to storage'),

  a.mannequin('scale.1', [-4, 0, 6], { rotationY: 180 }),
  a.mannequin('scale.2', [-11, 10, -14], { rotationY: 0 }),
  a.mannequin('scale.3', [16, 0, 2], { rotationY: 300 }),
  a.mannequin('scale.4', [-4, 5, 12], { rotationY: 90 }),
];
