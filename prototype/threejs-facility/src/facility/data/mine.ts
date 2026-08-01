import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('mine');

/**
 * Mine, driven west into the rock mass beyond the plant. Floor at -2 m, so the
 * rough rock ceiling rises above grade and reads as a hillside from the yard.
 * Geometry here is deliberately unlike the built plant: irregular shells,
 * uneven openings, low headroom in the connectors.
 *
 * Compact on purpose — one main face, one ore-vein branch, one dead end, and
 * the service tunnel that climbs back under the plant into the maintenance ring.
 */
export const MINE_ENTITIES: Entity[] = [
  // Main extraction chamber. X -152..-126, Z -11..11.
  a.cavern('chamber.main', [-139, -2, 0], [26, 8, 22], {
    label: 'EXTRACTION FACE',
    seed: 11,
    rough: 0.6,
    openings: [
      { side: 'e', at: 0, width: 8 }, // adit to the haulage hall
      { side: 'n', at: -3, width: 6 }, // ore-vein branch
      { side: 's', at: 6, width: 4, height: 3.2 }, // service tunnel
    ],
  }),

  a.tunnel('drift.vein', [[-142, -2, -11], [-142, -2, -19]], 6, 5.4, {
    seed: 23,
    rough: 0.5,
  }),
  a.cavern('chamber.vein', [-142, -2, -25], [18, 6.5, 12], {
    label: 'ORE VEIN',
    seed: 41,
    rough: 0.65,
    openings: [
      { side: 's', at: 0, width: 6 },
      { side: 'w', at: 0, width: 4.5, height: 4 },
    ],
  }),
  a.tunnel('drift.store', [[-151, -2, -25], [-161, -2, -25]], 4.5, 4, {
    label: 'STORE DRIFT',
    seed: 67,
    rough: 0.7,
  }),

  // Service tunnel: 2.8 m of headroom, no lighting, and the only way out of
  // the mine that is not the adit the carts use.
  a.tunnel(
    'service',
    [
      [-133, -2, 11],
      [-130, -2.6, 17],
      [-118, -3.6, 19],
      [-104, -4.6, 14],
      [-98, -5, 8],
    ],
    3.2,
    2.8,
    { label: 'SERVICE TUNNEL UP', seed: 83, rough: 0.55 },
  ),

  a.machine('drill', 'DRILL RIG', [-148, -2, 4], [4, 3.2, 7], { rotationY: 12 }),
  a.machine('loader', 'ORE LOADER', [-137, -2, -6], [7, 3.4, 5]),
  a.platform('load.deck', [-133, -1.2, 0], [8, 7], {
    label: 'CART LOADING',
    railings: ['n'],
    supports: false,
  }),
  a.prop('pillar.1', [-142, -2, 6], [2.6, 8, 2.6], { shape: 'cylinder' }),
  a.prop('pillar.2', [-133, -2, 7], [2.4, 8, 2.4], { shape: 'cylinder' }),
  a.prop('ore.pile.1', [-146, -2, -4], [5, 1.6, 4]),
  a.prop('ore.pile.2', [-139, -2, -25], [5, 1.5, 4]),
  a.prop('crates.store', [-159, -2, -25], [3, 1.8, 3]),
  a.prop('tarp.store', [-156, -2, -25], [2.4, 1.2, 2.6]),

  a.track('track.face', [[-126, -2, 0], [-133, -2, 0], [-139, -2, -2]]),
  a.prop('cart.parked', [-136, -2, -1], [2, 1.6, 3], { rotationY: 16 }),

  a.spawn('spawn.face', [-141, -2, 0], 'Mine face'),
  a.marker('m.service', [-133, -2, 10], 'shortcut', 'Service tunnel: back up under the plant'),
  a.marker('m.store', [-159, -2, -25], 'hiding', 'Store drift: nobody comes here'),
  a.marker('m.ground', [-142, -2, -15], 'hazard', 'Poor ground: blast damage collapses this'),
  a.marker('m.load', [-133, -1.2, 0], 'interaction', 'Ore loading point'),

  a.mannequin('scale.1', [-145, -2, 0], { rotationY: 90 }),
  a.mannequin('scale.2', [-135, -2, -4], { rotationY: 210 }),
];
