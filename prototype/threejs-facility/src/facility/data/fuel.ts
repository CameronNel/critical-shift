import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('fuel');

/**
 * Fuel processing and transfer. X 28..58, Z -20..+12, 8 m clear.
 * Its roof is a walkable deck: the best low-effort place on the site to spot
 * something arriving on the compliance road while still being near the plant.
 * The north door opens straight onto that approach, which cuts both ways.
 */
export const FUEL_ENTITIES: Entity[] = [
  a.floor('slab', [43, 0, -4], [30, 32]),
  a.platform('roofdeck', [43, 8, -4], [30, 32], {
    label: 'FUEL ROOF DECK',
    railings: ['n', 'e', 's', 'w'],
    tags: ['roof'],
  }),

  ...roomWalls(a, 'shell', {
    min: [28, -20],
    max: [58, 12],
    height: 8,
    openings: [
      { side: 'w', at: -10, width: 5, bottom: 2.5, top: 7.5 }, // dried material in
      { side: 'w', at: 4, width: 4, top: 3.6 }, // refinery ground route
      { side: 'e', at: -2, width: 5, top: 4.2 }, // fuel corridor to reactor
      { side: 'e', at: -12, width: 4, bottom: 3, top: 7.5 }, // fuel belt out
      { side: 'n', at: 44, width: 4, top: 3.6 }, // compliance-side door
      { side: 's', at: 36, width: 4, top: 3.6 }, // medical
    ],
  }),

  a.machine('assembly', 'FUEL ASSEMBLY', [36, 0, -12], [10, 6, 10]),
  a.machine('inspection', 'INSPECTION', [50, 0, -12], [8, 5, 8]),
  a.machine('store', 'CONTAINMENT STORE', [36, 0, 4], [9, 7, 9], { shape: 'cylinder' }),

  a.conveyor('conv.assemble', [[41, 4, -12], [46, 4, -12]], 2),
  a.conveyor('conv.reactor', [[54, 5, -12], [62, 5, -12], [68, 5, -12]], 2.2, {
    label: 'FUEL → REACTOR',
  }),

  a.platform('staging', [50, 0.35, 4], [12, 12], { label: 'FUEL STAGING' }),
  a.prop('crates.1', [46, 0.35, 8], [2.4, 2.2, 2.4]),
  a.prop('crates.2', [49, 0.35, 8], [2.4, 2.2, 2.4]),
  a.prop('crates.3', [46, 0.35, 1], [2.4, 2.2, 2.4]),
  a.prop('flask.1', [54, 0.35, 2], [1.6, 2.6, 1.6], { shape: 'cylinder' }),
  a.prop('flask.2', [54, 0.35, 6], [1.6, 2.6, 1.6], { shape: 'cylinder' }),

  a.stair('stair.roof', [30.5, 0, 9], [30.5, 8, -3], 2),

  // Fuel corridor: six exposed metres between fuel and the reactor.
  a.floor('corridor', [61, 0, -2], [6, 8]),
  a.roof('corridor.lid', [61, 5, -2], [6, 8]),
  a.wall('corridor.n', [58, -6], [64, -6], 5),
  a.wall('corridor.s', [64, 2], [58, 2], 5),
  a.doorway('door.corridor', [58, 0, -2], 5, 4.2, { rotationY: 90 }),

  a.doorway('door.north', [44, 0, -20], 4, 3.6),
  a.doorway('door.south', [36, 0, 12], 4, 3.6),

  a.spawn('spawn.fuel', [43, 0, 0], 'Fuel hall'),
  a.spawn('spawn.roof', [43, 8, -4], 'Fuel roof deck'),

  a.marker('m.roofview', [43, 8, -18], 'sightline', 'Roof deck: the compliance road is right there'),
  a.marker('m.crates', [46, 0.35, 8], 'hiding', 'Empty fuel crates'),
  a.marker('m.inspect', [50, 0, -6], 'interaction', 'Inspection: the last chance to catch a bad batch'),
  a.marker('m.northdoor', [44, 0, -22], 'hazard', 'North door: an auditor can walk straight in'),

  a.mannequin('scale.1', [43, 0, -2], { rotationY: 200 }),
  a.mannequin('scale.2', [43, 8, -14], { rotationY: 0 }),
];
