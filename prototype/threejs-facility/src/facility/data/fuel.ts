import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('fuel');

/**
 * Fuel processing, east end of the north production row. X -10..18, Z -62..-32.
 * Its roof at +10 is a walkable deck and the cheapest early warning on the
 * site: it looks straight down the compliance approach. Its east door opens
 * onto that approach, which cuts both ways.
 */
export const FUEL_ENTITIES: Entity[] = [
  a.floor('slab', [4, 0, -47], [28, 30]),
  a.platform('roofdeck', [4, 10, -47], [28, 30], {
    label: 'FUEL ROOF DECK',
    railings: ['n', 'e', 's', 'w'],
    tags: ['roof'],
  }),

  ...roomWalls(a, 'shell', {
    min: [-10, -62],
    max: [18, -32],
    height: 10,
    openings: [
      { side: 'w', at: -52, width: 5, bottom: 2, top: 9 }, // dried material in
      { side: 'w', at: -40, width: 4, top: 3.6 }, // ground route to refinery
      { side: 'e', at: -40, width: 4, top: 3.6 }, // compliance approach
      { side: 'n', at: 4, width: 4, top: 3.6 }, // onto S1
      { side: 's', at: 8, width: 5, top: 4.2 }, // main route to the reactor
      { side: 's', at: -4, width: 4, bottom: 2, top: 8 }, // fuel belt out
    ],
  }),

  a.machine('assembly', 'FUEL ASSEMBLY', [-2, 0, -52], [8, 6, 8]),
  a.machine('inspection', 'INSPECTION', [10, 0, -52], [7, 5, 7]),
  a.machine('store', 'CONTAINMENT STORE', [-2, 0, -40], [8, 7, 8], { shape: 'cylinder' }),

  a.conveyor('conv.assemble', [[2, 4, -52], [6.5, 4, -52]], 2),
  a.conveyor(
    'conv.reactor',
    [
      [10, 4.5, -48],
      [4, 4.5, -42],
      [-4, 4.5, -34],
      [-5, 4.5, -28],
      [-5, 4, -22],
    ],
    2,
    { label: 'FUEL → REACTOR' },
  ),

  a.platform('staging', [10, 0.35, -40], [10, 10], { label: 'FUEL STAGING' }),
  a.prop('crates.1', [7, 0.35, -37], [2.4, 2.2, 2.4]),
  a.prop('crates.2', [10, 0.35, -37], [2.4, 2.2, 2.4]),
  a.prop('crates.3', [13, 0.35, -37], [2.4, 2.2, 2.4]),
  a.prop('flask.1', [14, 0.35, -43], [1.6, 2.6, 1.6], { shape: 'cylinder' }),
  a.prop('flask.2', [14, 0.35, -46], [1.6, 2.6, 1.6], { shape: 'cylinder' }),

  a.stair('stair.roof', [-8, 0, -36], [-8, 10, -50], 2),

  a.doorway('door.spine', [4, 0, -62], 4, 3.6, { label: 'S1' }),
  a.doorway('door.south', [8, 0, -32], 5, 4.2),
  a.doorway('door.east', [18, 0, -40], 4, 3.6, { rotationY: 90 }),

  a.spawn('spawn.fuel', [4, 0, -40], 'Fuel hall'),
  a.spawn('spawn.roof', [4, 10, -47], 'Fuel roof deck'),

  a.marker('m.roofview', [4, 10, -58], 'sightline', 'Roof deck: straight down the compliance approach'),
  a.marker('m.crates', [10, 0.35, -37], 'hiding', 'Empty fuel crates'),
  a.marker('m.inspect', [10, 0, -46], 'interaction', 'Inspection: last chance to catch a bad batch'),
  a.marker('m.eastdoor', [20, 0, -40], 'hazard', 'East door: an auditor can walk straight in'),

  a.mannequin('scale.1', [4, 0, -44], { rotationY: 200 }),
  a.mannequin('scale.2', [4, 10, -54], { rotationY: 0 }),
];
