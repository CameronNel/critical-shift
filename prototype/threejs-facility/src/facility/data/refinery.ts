import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('refinery');

/**
 * Refinery, middle of the north production row. X -54..-14, Z -62..-32.
 * Sorter, processor and dryer on one unbroken belt line along the north half,
 * circulation south of them. Four usable elevations: floor 0, mezzanine +5,
 * centre aisle +10, gantry +14. A clerestory at +14 looks north over the
 * compliance road, which is the only warning the production floor ever gets.
 */
export const REFINERY_ENTITIES: Entity[] = [
  a.floor('slab', [-34, 0, -47], [40, 30]),
  a.roof('lid', [-34, 18, -47], [40, 30]),

  ...roomWalls(a, 'shell', {
    min: [-54, -62],
    max: [-14, -32],
    height: 18,
    openings: [
      { side: 'w', at: -52, width: 5, bottom: 2, top: 9 }, // crushed ore in
      { side: 'w', at: -38, width: 4, bottom: 4.5, top: 8 }, // high link
      { side: 'w', at: -44, width: 4, top: 3.6 }, // ground route
      { side: 'e', at: -52, width: 5, bottom: 2, top: 9 }, // dried material out
      { side: 'e', at: -40, width: 4, top: 3.6 }, // ground route to fuel
      { side: 'n', at: -34, width: 4, top: 3.6 }, // onto S1
      { side: 'n', at: -44, width: 12, bottom: 10, top: 14 }, // clerestory
      { side: 's', at: -24, width: 4, top: 3.6 }, // down to the diagonal
      { side: 's', at: -46, width: 4, top: 3.6 }, // yard door
    ],
  }),

  a.machine('sorter', 'SORTER', [-46, 0, -52], [10, 8, 12]),
  a.machine('processor', 'PROCESSOR', [-32, 0, -52], [11, 11, 11], { shape: 'cylinder' }),
  a.machine('dryer', 'DRYER', [-20, 0, -52], [9, 9, 12]),

  a.conveyor('conv.in', [[-54, 5, -52], [-51, 5.2, -52]], 2, { label: 'CRUSHED' }),
  a.conveyor('conv.sort', [[-41, 5.5, -52], [-37.5, 5.5, -52]], 2, { label: 'SORTED' }),
  a.conveyor('conv.proc', [[-26.5, 6.5, -52], [-24.5, 6, -52]], 2, { label: 'PROCESSED' }),
  a.conveyor('conv.out', [[-15.5, 5.5, -52], [-10, 5, -52]], 2, { label: 'DRIED → FUEL' }),

  a.platform('mezz', [-34, 5, -37], [38, 8], {
    label: 'REFINERY MEZZANINE',
    railings: ['n'],
    supports: true,
  }),
  a.catwalk('cat.aisle', [[-39.3, 10, -60], [-39.3, 10, -36]], 2, { label: 'CENTRE AISLE' }),
  a.catwalk(
    'cat.gantry',
    [
      [-49, 14, -58],
      [-49, 14, -36],
      [-18, 14, -36],
      [-18, 14, -58],
    ],
    2.2,
    { label: 'UPPER GANTRY' },
  ),
  a.catwalk('cat.beltaccess', [[-44, 5, -40], [-42, 5.5, -46], [-40, 5.6, -50]], 1.6, {
    railings: 'left',
  }),

  a.stair('stair.ground', [-52, 0, -46], [-52, 5, -38], 2.2),
  a.stair('stair.mezz', [-39.3, 5, -38], [-39.3, 10, -46], 1.8),
  a.stair('stair.gantry', [-42, 10, -58], [-49, 14, -58], 1.6),

  a.prop('batch.1', [-44, 0, -36], [3, 2.2, 3]),
  a.prop('batch.2', [-40, 0, -36], [3, 2.2, 3]),
  a.prop('batch.3', [-36, 0, -36], [3, 2.2, 3]),
  a.prop('console.sorter', [-46, 0, -44], [3, 1.2, 1]),
  a.prop('console.proc', [-32, 0, -44], [3, 1.2, 1]),
  a.prop('console.dryer', [-20, 0, -44], [3, 1.2, 1]),

  a.doorway('door.spine', [-34, 0, -62], 4, 3.6, { label: 'S1' }),
  a.doorway('door.south', [-24, 0, -32], 4, 3.6),

  a.spawn('spawn.floor', [-34, 0, -38], 'Refinery floor'),
  a.spawn('spawn.gantry', [-49, 14, -46], 'Refinery gantry'),

  a.marker('m.beltwalk', [-40, 5.6, -50], 'shortcut', 'Belt walk: mezzanine to fuel, no stairs'),
  a.marker('m.clerestory', [-44, 14, -56], 'sightline', 'Clerestory: the compliance road is out there'),
  a.marker('m.downstream', [-15, 5.5, -52], 'objective', 'A bad batch leaves here and never stops'),
  a.marker('m.south', [-24, 0, -34], 'crossing', 'South door drops you onto the cart diagonal'),

  a.mannequin('scale.1', [-34, 0, -40], { rotationY: 180 }),
  a.mannequin('scale.2', [-39.3, 10, -48], { rotationY: 0 }),
  a.mannequin('scale.3', [-20, 0, -40], { rotationY: 300 }),
  a.mannequin('scale.4', [-34, 5, -37], { rotationY: 90 }),
];
