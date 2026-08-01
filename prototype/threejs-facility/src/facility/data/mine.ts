import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('mine');

/**
 * Mine datum Y = -8. Geometry here is deliberately unlike the built plant:
 * rough rock shells, irregular openings, low headroom in the connectors.
 * Compact on purpose — one main face, one branch, one dead end, one rise.
 */
export const MINE_ENTITIES: Entity[] = [
  // Primary extraction chamber. X -137..-111, Z -27..-5.
  a.cavern('chamber.main', [-124, -8, -16], [26, 8, 22], {
    label: 'EXTRACTION FACE',
    seed: 11,
    rough: 0.6,
    openings: [
      { side: 'e', at: 0, width: 7 }, // haulage drift
      { side: 'n', at: -4, width: 6 }, // branch drift
      { side: 's', at: 9, width: 4, height: 3.2 }, // the rise
    ],
  }),

  // Branch drift and secondary chamber.
  a.tunnel('drift.branch', [[-128, -8, -27], [-128, -8, -35]], 6, 5.4, {
    seed: 23,
    rough: 0.5,
  }),
  a.cavern('chamber.branch', [-128, -8, -41], [18, 6.5, 12], {
    label: 'SECONDARY FACE',
    seed: 41,
    rough: 0.65,
    openings: [
      { side: 's', at: 0, width: 6 },
      { side: 'w', at: 0, width: 4.5, height: 4 },
    ],
  }),

  // Dead-end store drift. Nothing official happens down here.
  a.tunnel('drift.store', [[-137, -8, -41], [-144, -8, -41]], 4.5, 4, {
    label: 'STORE DRIFT',
    seed: 67,
    rough: 0.7,
  }),

  // The rise: low, tight, unlit, and much faster than walking the decline.
  a.tunnel(
    'rise',
    [
      [-115, -8, -5],
      [-112, -8, 0],
      [-104, -7.6, 4],
    ],
    3.2,
    2.8,
    { label: 'THE RISE', seed: 83, rough: 0.55 },
  ),

  // Working gear. Broad placeholders only.
  a.machine('drill', 'DRILL RIG', [-133, -8, -12], [4, 3.2, 7], { rotationY: 12 }),
  a.machine('loader', 'ORE LOADER', [-122, -8, -22], [7, 3.4, 5]),
  a.platform('load.deck', [-118, -7.2, -16], [8, 7], {
    label: 'CART LOADING',
    railings: ['n'],
    supports: false,
  }),
  a.prop('pillar.1', [-127, -8, -10], [2.6, 8, 2.6], { shape: 'cylinder' }),
  a.prop('pillar.2', [-118, -8, -9], [2.4, 8, 2.4], { shape: 'cylinder' }),
  a.prop('ore.pile.1', [-131, -8, -20], [5, 1.6, 4]),
  a.prop('ore.pile.2', [-125, -8, -41], [5, 1.5, 4]),
  a.prop('crates.store', [-142, -8, -41], [3, 1.8, 3]),
  a.prop('tarp.store', [-139, -8, -41], [2.4, 1.2, 2.6]),

  // Cart track through the chamber to the loading point.
  a.track('track.face', [[-111, -8, -16], [-118, -8, -16], [-124, -8, -18]]),
  a.prop('cart.parked', [-121, -8, -17], [2, 1.6, 3], { rotationY: 16 }),

  a.spawn('spawn.face', [-126, -8, -16], 'Mine face'),
  a.marker('m.rise', [-115, -8, -6], 'shortcut', 'The rise: 60 m crawl, skips the decline'),
  a.marker('m.store', [-142, -8, -41], 'hiding', 'Store drift: nobody comes here'),
  a.marker('m.roof', [-128, -8, -30], 'hazard', 'Poor ground: blast damage collapses this'),
  a.marker('m.load', [-118, -7.2, -16], 'interaction', 'Ore loading point'),

  a.mannequin('scale.1', [-130, -8, -16], { rotationY: 90 }),
  a.mannequin('scale.2', [-120, -8, -20], { rotationY: 210 }),
];
