import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('crusher');

/**
 * Crusher hall. X -70..-36, Z -26..+12, 20 m clear.
 * Grade is a ring around an open pit at -6 m. The cart track crosses the pit
 * on an unrailed deck, which is the fastest way across the hall and the worst
 * place to be standing when a cart arrives.
 */
export const CRUSHER_ENTITIES: Entity[] = [
  a.floor('deck.w', [-65, 0, -7], [10, 38]),
  a.floor('deck.e', [-38, 0, -7], [4, 38]),
  a.floor('deck.n', [-50, 0, -22.5], [20, 7]),
  a.floor('deck.s', [-50, 0, 9], [20, 6]),
  a.floor('deck.track', [-50, 0, -6.5], [5, 25], { label: 'TIPPING DECK' }),
  a.floor('pit', [-50, -6, -6.5], [20, 25]),
  a.roof('lid', [-53, 20, -7], [34, 38]),

  ...roomWalls(a, 'shell', {
    min: [-70, -26],
    max: [-36, 12],
    height: 20,
    openings: [
      { side: 'w', at: -10, width: 4.5, top: 3.6 }, // north walkway door
      { side: 's', at: -50, width: 6, top: 5 }, // cart track
      { side: 's', at: -64, width: 4, top: 3.6 }, // south walkway door
      { side: 'e', at: -6, width: 5, bottom: 0, top: 8 }, // output conveyor
      { side: 'e', at: 3, width: 4, bottom: 5, top: 8.5 }, // high catwalk
      { side: 'e', at: 8, width: 4, top: 3.6 }, // ground route to refinery
      { side: 'n', at: -53, width: 8, bottom: 12, top: 18 }, // north clerestory
    ],
  }),

  a.track('track.hall', [[-50, 0, 12], [-50, 0, -19]]),

  a.machine('hopper', 'RECEIVING HOPPER', [-51, -6, -21.5], [10, 7, 5], { shape: 'hopper' }),
  a.machine('crusher', 'PRIMARY CRUSHER', [-44, -6, -6], [8, 16, 11]),
  a.conveyor('conv.feed', [[-51, -4.5, -19], [-47, -4, -11]], 2.5, { label: 'FEED' }),
  a.conveyor(
    'conv.out',
    [
      [-40, -3, -6],
      [-37, 0, -6],
      [-33, 3, -6],
      [-31, 5, -9],
      [-31, 6.5, -16],
    ],
    2.6,
    { label: 'CRUSHED ORE → REFINERY' },
  ),

  // Operator level: sees the tipping deck, the pit and the crusher throat.
  a.platform('op.deck', [-59, 6, -6], [10, 14], {
    label: 'CRUSHER CONTROL',
    railings: ['n', 'e', 's'],
    supports: true,
  }),
  a.prop('op.console', [-56, 6, -6], [1.2, 1.1, 4]),
  a.stair('op.stair', [-64, 0, 6], [-64, 6, -6], 2.2),

  a.platform('maint.deck', [-44, 6, 0], [8, 6], {
    label: 'CRUSHER MAINTENANCE',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.catwalk(
    'cat.east',
    [
      [-54, 6, 3],
      [-46, 6, 3],
      [-38, 5.6, 3],
      [-30, 5, 3],
    ],
    2.4,
    { label: 'CRUSHER → REFINERY HIGH LINK' },
  ),

  a.stair('pit.stair', [-61, 0, -14], [-55, -6, -14], 2),

  a.doorway('door.west', [-70, 0, -10], 4.5, 3.6, { rotationY: 90 }),
  a.doorway('door.east', [-36, 0, 8], 4, 3.6, { rotationY: 90 }),

  a.spawn('spawn.hall', [-65, 0, -2], 'Crusher hall'),
  a.marker('m.deck', [-50, 0, -6], 'crossing', 'Tipping deck: no rails, live track'),
  a.marker('m.pit', [-57, 0, 2], 'hazard', 'Open pit edge'),
  a.marker('m.jam', [-44, 6, 0], 'interaction', 'Crusher jam clearance'),
  a.marker('m.beltup', [-33, 3, -6], 'shortcut', 'Ride the output belt up to the refinery'),
  a.marker('m.spine', [-50, -6, 4], 'shortcut', 'Pit connects to the maintenance spine'),

  a.mannequin('scale.1', [-64, 0, -2], { rotationY: 90 }),
  a.mannequin('scale.2', [-50, -6, -2]),
  a.mannequin('scale.3', [-59, 6, -2], { rotationY: 180 }),
];
