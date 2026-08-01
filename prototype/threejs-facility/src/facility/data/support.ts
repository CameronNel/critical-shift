import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const store = zoneAuthor('storage');
const med = zoneAuthor('medical');

/**
 * Storage, on the southern leg of the loop. Its floor is cut around a stairwell
 * that drops straight into the maintenance ring, which makes it the quietest
 * way to get under the plant.
 */
export const STORAGE_ENTITIES: Entity[] = [
  store.floor('slab.w', [-73, 0, 44], [26, 28]),
  store.floor('slab.e', [-49, 0, 44], [6, 28]),
  store.floor('slab.n', [-56, 0, 31], [8, 2]),
  store.floor('slab.s', [-56, 0, 53], [8, 10]),
  store.roof('lid', [-66, 6, 44], [40, 28]),
  ...roomWalls(store, 'shell', {
    min: [-86, 30],
    max: [-46, 58],
    height: 6,
    openings: [
      { side: 'n', at: -66, width: 4, top: 3.6 }, // S2 from haulage
      { side: 'e', at: 44, width: 4, top: 3.6 }, // southern loop
      { side: 'w', at: 44, width: 3, top: 3 }, // yard
    ],
  }),
  store.floor('shaft.base', [-56, -5, 42], [8, 12]),
  store.stair('stair.down', [-56, 0, 44], [-56, -5, 35], 2),
  store.machine('press', 'WASTE PRESS', [-80, 0, 52], [6, 4, 6]),
  store.prop('waste.1', [-82, 0, 36], [4, 3, 4]),
  store.prop('waste.2', [-77, 0, 36], [4, 3, 4]),
  store.prop('waste.3', [-72, 0, 36], [4, 3, 4]),
  store.prop('crates.stack', [-66, 0, 52], [5, 3.4, 5]),
  store.prop('tarp', [-66, 0, 38], [4, 1.4, 5]),
  store.prop('drums', [-50, 0, 36], [2.2, 1.4, 2.2], { shape: 'cylinder' }),
  store.spawn('spawn.storage', [-70, 0, 44], 'Storage'),
  store.marker('m.waste', [-77, 0, 36], 'hiding', 'Waste containers: capacity, and nobody looks'),
  store.marker('m.tarp', [-66, 0, 38], 'hiding', 'Under the tarp'),
  store.marker('m.stair', [-56, 0, 50], 'shortcut', 'Stairwell straight down into the service ring'),
  store.mannequin('scale.1', [-70, 0, 47], { rotationY: 20 }),
];

/** Reanimation and decontamination, on the southern loop between S2 and S3. */
export const MEDICAL_ENTITIES: Entity[] = [
  med.floor('slab', [-21, 0, 57], [30, 26]),
  med.roof('lid', [-21, 5, 57], [30, 26]),
  ...roomWalls(med, 'shell', {
    min: [-36, 44],
    max: [-6, 70],
    height: 5,
    openings: [
      { side: 'n', at: -21, width: 4, top: 3.4 }, // reactor south yard
      { side: 'w', at: 57, width: 3.5, top: 3.4 }, // storage
      { side: 'e', at: 50, width: 4, top: 3.4 }, // S3 to cooling
    ],
  }),
  med.machine('reanimation', 'REANIMATION BAY', [-30, 0, 52], [8, 3.4, 6]),
  med.machine('decon', 'DECONTAMINATION', [-12, 0, 62], [8, 3, 6]),
  med.prop('trolley.1', [-24, 0, 62], [1, 0.9, 2.2]),
  med.prop('trolley.2', [-21, 0, 62], [1, 0.9, 2.2]),
  med.spawn('spawn.medical', [-21, 0, 57], 'Medical'),
  med.marker('m.reanimate', [-30, 0, 56], 'interaction', 'Reanimation: costly, slow, loud'),
  med.marker('m.s3', [-6, 0, 50], 'shortcut', 'S3: across to the cooling lid without the reactor'),
  med.mannequin('scale.1', [-21, 0, 58], { rotationY: 250 }),
];
