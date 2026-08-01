import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('cooling');

/**
 * Cooling hall, sunk to -6 m south of the reactor and directly below the line
 * of sight from control. You can see the valves from the balcony and you
 * cannot touch them: the only fast way down is one stair through the reactor
 * south wall, and the only quiet way is the maintenance spine.
 */
export const COOLING_ENTITIES: Entity[] = [
  a.floor('slab', [89, -6, 45], [46, 26]),
  // The lid is flush with grade and stops short of the north wall, leaving an
  // open cut you can look straight down into from the yard.
  a.platform('lid', [89, 0, 48], [46, 20], {
    label: 'COOLING LID',
    railings: ['n'],
    tags: ['roof'],
  }),

  ...roomWalls(a, 'shell', {
    min: [66, 32],
    max: [112, 58],
    base: -6,
    height: 6,
    openings: [
      { side: 'n', at: 88, width: 8 }, // stair from the reactor floor
      { side: 's', at: 100, width: 4 }, // emergency stair to grade
      { side: 'w', at: 40, width: 4 }, // maintenance spine
    ],
  }),

  a.stair('stair.reactor', [88, 0, 26], [88, -6, 36], 3),
  a.stair('stair.escape', [100, -6, 54], [100, 0, 62], 2),

  a.machine('pump.a', 'COOLANT PUMP A', [74, -6, 38], [7, 5, 7], { shape: 'cylinder' }),
  a.machine('pump.b', 'COOLANT PUMP B', [74, -6, 50], [7, 5, 7], { shape: 'cylinder' }),
  a.machine('pump.c', 'COOLANT PUMP C', [104, -6, 38], [7, 5, 7], { shape: 'cylinder' }),
  a.machine('exchanger', 'HEAT EXCHANGER', [100, -6, 51], [16, 6, 10]),

  a.platform('gallery', [89, -2, 45], [8, 22], {
    label: 'VALVE GALLERY',
    railings: ['e', 'w'],
    supports: true,
  }),
  a.stair('stair.gallery', [85, -6, 50], [85, -2, 44], 1.8),
  a.prop('valve.1', [89, -2, 38], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.2', [89, -2, 43], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.3', [89, -2, 48], [1.6, 1.4, 1.6], { shape: 'cylinder' }),
  a.prop('valve.4', [89, -2, 53], [1.6, 1.4, 1.6], { shape: 'cylinder' }),

  a.pipe('pipe.up.a', [[88, 1, 34], [88, 6, 30], [88, 12, 22]], 0.9),
  a.pipe('pipe.up.b', [[100, 1, 34], [100, 6, 30], [100, 12, 22]], 0.9),
  a.pipe('pipe.loop', [[74, -3, 42], [74, -3, 46], [100, -3, 46]], 0.7),

  a.spawn('spawn.cooling', [89, -6, 45], 'Cooling hall'),
  a.marker('m.valves', [89, -2, 45], 'interaction', 'Main coolant valves'),
  a.marker('m.run', [88, -6, 35], 'hazard', 'The run from the reactor floor: 40 m and a stair'),
  a.marker('m.escape', [100, -6, 54], 'shortcut', 'Emergency stair straight up to grade'),

  a.mannequin('scale.1', [89, -6, 40], { rotationY: 0 }),
  a.mannequin('scale.2', [89, -2, 50], { rotationY: 180 }),
];
