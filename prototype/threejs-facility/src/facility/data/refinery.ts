import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('refinery');

/**
 * Refinery. One belt hall you work in and one assay room off it — the four
 * working elevations are gone. The belt line runs the length of the hall at
 * waist height so the process reads at a glance, and the sorter, processor and
 * dryer are machines you stand at rather than structures you climb.
 *
 *   process hall   X -50..-30, Z -56..-42
 *   control room   X -28..-18, Z -52..-44
 */
export const REFINERY_ENTITIES: Entity[] = [
  // --- Process hall ---------------------------------------------------------
  a.floor('hall.slab', [-40, 0, -49], [20, 14]),
  a.roof('hall.lid', [-40, 6, -49], [20, 14]),
  ...roomWalls(a, 'hall', {
    min: [-50, -56],
    max: [-30, -42],
    height: 6,
    openings: [
      { side: 'w', at: -49, width: 5, bottom: 2, top: 5 }, // crushed ore in
      { side: 'n', at: -40, width: 4, top: 3.6 }, // S1 spine
      { side: 'e', at: -49, width: 4, top: 3.6 }, // through to control
      { side: 's', at: -40, width: 4, top: 3.6 }, // yard
    ],
  }),
  a.machine('sorter', 'SORTER', [-46, 0, -52], [5, 3, 5]),
  a.machine('processor', 'PROCESSOR', [-40, 0, -52], [5, 3.5, 5]),
  a.machine('dryer', 'DRYER', [-34, 0, -52], [5, 3, 5]),
  a.conveyor('conv.line', [[-50, 1.2, -49], [-32, 1.2, -49]], 2, { label: 'PROCESS LINE' }),
  a.prop('drums', [-47, 0, -44], [2.2, 1.4, 2.2], { shape: 'cylinder' }),
  a.prop('spares', [-43, 0, -44], [3, 1.6, 1.6]),
  a.light('hall.l1', [-45, 5.4, -49], { cast: true, intensity: 110, distance: 24 }),
  a.light('hall.l2', [-35, 5.4, -49]),
  a.marker('m.sort', [-46, 0, -46], 'interaction', 'Set the sorter — tight grade is slow, loose grade is a problem later'),
  a.marker('m.process', [-40, 0, -46], 'interaction', 'Run the processor'),
  a.marker('m.dry', [-34, 0, -46], 'interaction', 'Dryer temperature · run it hot to catch up'),
  a.spawn('spawn.hall', [-40, 0, -45], 'Refinery hall'),
  a.mannequin('scale.1', [-43, 0, -46], { rotationY: 0 }),
  a.mannequin('scale.2', [-37, 0, -47], { rotationY: 270 }),

  // --- Control room ---------------------------------------------------------
  a.floor('ctrl.slab', [-23, 0, -48], [10, 8]),
  a.roof('ctrl.lid', [-23, 4.5, -48], [10, 8]),
  ...roomWalls(a, 'ctrl', {
    min: [-28, -52],
    max: [-18, -44],
    height: 4.5,
    openings: [
      { side: 'w', at: -48, width: 4, top: 3.6 }, // from the hall
      { side: 'e', at: -48, width: 4, top: 3.6 }, // on to fuel
    ],
  }),
  a.machine('desk', 'REFINERY CONTROL', [-23, 0, -50.5], [5, 1.2, 1.4]),
  a.machine('grade.board', 'GRADE BOARD', [-27.5, 1.2, -48], [0.3, 2, 4]),
  a.prop('ctrl.chair', [-23, 0, -49], [0.7, 1.1, 0.7]),
  a.light('ctrl.l1', [-23, 4, -48], { cast: true, intensity: 80, distance: 16 }),
  a.marker('m.grade', [-23, 0, -49.4], 'interaction', 'Declare the batch grade'),
  a.marker('m.fudge', [-26.5, 0, -48], 'hazard', 'Declare it better than it is — nobody re-tests upstream'),
  a.spawn('spawn.ctrl', [-22, 0, -47], 'Refinery control'),
  a.mannequin('scale.3', [-23, 0, -48.6], { rotationY: 180 }),

  // --- Scenery --------------------------------------------------------------
  a.conveyor('conv.fuel', [[-18, 3, -48], [-11, 3.5, -48]], 2, { label: 'REFINED ORE → FUEL' }),
  a.doorway('door.spine', [-40, 0, -56], 4, 3.6),
  a.doorway('door.yard', [-40, 0, -42], 4, 3.6),
];
