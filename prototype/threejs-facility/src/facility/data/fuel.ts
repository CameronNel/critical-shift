import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('fuel');

/**
 * Fuel. Two rooms and the corridor that funnels the whole shift at the
 * reactor. The roof deck and its switchback are gone.
 *
 *   assembly hall     X -6..10, Z -52..-38   build the assembly, inspect it
 *   containment store X 12..20, Z -50..-42   finished fuel, and the crate you
 *                                            can fit inside
 *
 * The south corridor is the only way from the production row to the reactor,
 * which is what makes the reactor feel like the end of the line rather than
 * one more room.
 */
export const FUEL_ENTITIES: Entity[] = [
  // --- Assembly hall --------------------------------------------------------
  a.floor('hall.slab', [2, 0, -45], [16, 14]),
  a.roof('hall.lid', [2, 6, -45], [16, 14]),
  ...roomWalls(a, 'hall', {
    min: [-6, -52],
    max: [10, -38],
    height: 6,
    openings: [
      { side: 'w', at: -45, width: 4, bottom: 2, top: 5 }, // refined ore in
      { side: 'n', at: 2, width: 4, top: 3.6 }, // S1 spine
      { side: 'e', at: -46, width: 4, top: 3.6 }, // through to the store
      { side: 's', at: 6, width: 4, top: 3.6 }, // out to the reactor
    ],
  }),
  a.machine('assembly', 'FUEL ASSEMBLY', [-1, 0, -48], [5, 3, 5]),
  a.machine('inspection', 'ASSEMBLY INSPECTION', [6, 0, -48], [4, 2.6, 4]),
  a.prop('bench', [2, 0, -41], [8, 0.9, 1.2]),
  a.light('hall.l1', [2, 5.4, -45], { cast: true, intensity: 110, distance: 24 }),
  a.marker('m.assemble', [-1, 0, -44.5], 'interaction', 'Build the assembly'),
  a.marker('m.inspect', [6, 0, -44.5], 'interaction', 'Inspect it — skipping this is invisible until it is not'),
  a.spawn('spawn.hall', [2, 0, -43], 'Fuel assembly'),
  a.mannequin('scale.1', [0, 0, -44], { rotationY: 180 }),

  // --- Containment store ----------------------------------------------------
  a.floor('store.slab', [16, 0, -46], [8, 8]),
  a.roof('store.lid', [16, 4.5, -46], [8, 8]),
  ...roomWalls(a, 'store', {
    min: [12, -50],
    max: [20, -42],
    height: 4.5,
    openings: [{ side: 'w', at: -46, width: 4, top: 3.6 }],
  }),
  a.machine('containment', 'CONTAINMENT STORE', [18, 0, -48], [3, 3, 5], { color: '#8a8452' }),
  a.prop('crates', [14, 0, -44], [3, 2.2, 3]),
  a.light('store.l1', [16, 4, -46], { cast: true, intensity: 80, distance: 16 }),
  a.marker('m.store', [17, 0, -46], 'interaction', 'Draw or return a finished assembly'),
  a.marker('m.crate', [14, 0, -45.5], 'hiding', 'Empty crate — big enough, if nobody is counting'),
  a.spawn('spawn.store', [15, 0, -47], 'Containment store'),
  a.mannequin('scale.2', [16, 0, -44], { rotationY: 0 }),

  // --- The reactor corridor -------------------------------------------------
  a.floor('link.slab', [6, 0, -31], [6, 14]),
  a.roof('link.lid', [6, 5, -31], [6, 14]),
  a.wall('link.w', [3, -24], [3, -38], 5),
  a.wall('link.e', [9, -38], [9, -24], 5),
  a.marker('m.funnel', [6, 0, -31], 'crossing', 'Everyone goes through here, in both directions'),
  a.mannequin('scale.3', [6, 0, -30], { rotationY: 180 }),

  a.conveyor('conv.charge', [[10, 3.5, -46], [8, 4, -30], [6, 4, -26]], 2, {
    label: 'FUEL → CHARGE MACHINE',
  }),
  a.doorway('door.spine', [2, 0, -52], 4, 3.6),
  a.doorway('door.reactor', [6, 0, -38], 4, 3.6),
];
