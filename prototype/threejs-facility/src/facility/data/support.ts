import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const med = zoneAuthor('medical');
const store = zoneAuthor('storage');

/** Reanimation and decontamination, off the production line on purpose. */
export const MEDICAL_ENTITIES: Entity[] = [
  med.floor('slab', [39, 0, 26], [22, 16]),
  med.roof('lid', [39, 5, 26], [22, 16]),
  ...roomWalls(med, 'shell', {
    min: [28, 18],
    max: [50, 34],
    height: 5,
    openings: [
      { side: 'n', at: 36, width: 4, top: 3.4 },
      { side: 'w', at: 26, width: 3.5, top: 3.4 },
    ],
  }),
  med.machine('reanimation', 'REANIMATION BAY', [34, 0, 22], [8, 3.4, 6]),
  med.machine('decon', 'DECONTAMINATION', [45, 0, 30], [8, 3, 6]),
  med.prop('trolley.1', [34, 0, 29], [1, 0.9, 2.2]),
  med.prop('trolley.2', [37, 0, 29], [1, 0.9, 2.2]),
  med.spawn('spawn.medical', [39, 0, 26], 'Medical'),
  med.marker('m.reanimate', [34, 0, 25], 'interaction', 'Reanimation: costly, slow, loud'),
  med.marker('m.decon', [45, 0, 27], 'interaction', 'Decontamination chamber'),
  med.mannequin('scale.1', [39, 0, 27], { rotationY: 250 }),
];

/** Waste yard and bulk store. A few memorable places, not dozens of closets. */
export const STORAGE_ENTITIES: Entity[] = [
  store.floor('slab', [0, 0, 36], [28, 20]),
  store.roof('lid', [0, 6, 36], [28, 20]),
  ...roomWalls(store, 'shell', {
    min: [-14, 26],
    max: [14, 46],
    height: 6,
    openings: [
      { side: 'n', at: 6, width: 4, top: 3.6 },
      { side: 'w', at: 36, width: 4, top: 3.6 },
    ],
  }),
  store.machine('press', 'WASTE PRESS', [8, 0, 42], [6, 4, 6]),
  store.prop('waste.1', [-10, 0, 30], [4, 3, 4]),
  store.prop('waste.2', [-10, 0, 35], [4, 3, 4]),
  store.prop('waste.3', [-10, 0, 40], [4, 3, 4]),
  store.prop('crates.stack', [-2, 0, 42], [5, 3.4, 5]),
  store.prop('tarp', [3, 0, 32], [4, 1.4, 5]),
  store.prop('drums', [-4, 0, 29], [2.2, 1.4, 2.2], { shape: 'cylinder' }),
  store.spawn('spawn.storage', [0, 0, 36], 'Storage'),
  store.marker('m.waste', [-10, 0, 35], 'hiding', 'Waste containers: capacity, and nobody looks'),
  store.marker('m.tarp', [3, 0, 32], 'hiding', 'Under the tarp'),
  store.mannequin('scale.1', [0, 0, 38], { rotationY: 20 }),
];
