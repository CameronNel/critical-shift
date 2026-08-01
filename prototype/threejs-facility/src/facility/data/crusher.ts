import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('crusher');

/**
 * Crusher hall, west end of the north production row. X -88..-58, Z -62..-32.
 * Grade is a ring around an open pit at -5 m, and the pit is the west entrance
 * to the maintenance ring — so the fastest way under the plant is through the
 * busiest machine on the site.
 */
export const CRUSHER_ENTITIES: Entity[] = [
  a.floor('deck.n', [-73, 0, -60], [30, 4]),
  a.floor('deck.s', [-73, 0, -34], [30, 4]),
  a.floor('deck.w', [-86, 0, -47], [4, 22]),
  a.floor('deck.e', [-60, 0, -47], [4, 22]),
  a.floor('deck.track', [-73, 0, -47], [6, 22], { label: 'TIPPING DECK' }),
  a.floor('pit', [-73, -5, -47], [22, 22]),
  a.roof('lid', [-73, 20, -47], [30, 30]),

  ...roomWalls(a, 'shell', {
    min: [-88, -62],
    max: [-58, -32],
    height: 20,
    openings: [
      { side: 'n', at: -73, width: 4, top: 3.6 }, // onto S1
      { side: 's', at: -73, width: 7, top: 6 }, // cart spur from the loop
      { side: 's', at: -84, width: 4, top: 3.6 }, // worker door
      { side: 'w', at: -40, width: 4, top: 3.6 }, // west yard
      { side: 'e', at: -52, width: 5, bottom: 0, top: 8 }, // output conveyor
      { side: 'e', at: -38, width: 4, bottom: 5, top: 8.5 }, // high link
      { side: 'e', at: -44, width: 4, top: 3.6 }, // ground route to refinery
    ],
  }),

  a.track('track.hall', [[-73, 0, -30], [-73, 0, -55]]),

  a.machine('hopper', 'RECEIVING HOPPER', [-73, -5, -57.5], [9, 6, 5], { shape: 'hopper' }),
  a.machine('crusher', 'PRIMARY CRUSHER', [-66, -5, -47], [7, 15, 10]),
  a.conveyor('conv.feed', [[-73, -3.5, -55], [-70, -3, -49]], 2.4, { label: 'FEED' }),
  a.conveyor(
    'conv.out',
    [
      [-62.5, -2, -47],
      [-60, 0.5, -48],
      [-57, 3, -50],
      [-54, 5, -52],
    ],
    2.4,
    { label: 'CRUSHED ORE → REFINERY' },
  ),

  a.platform('op.deck', [-80, 6, -47], [8, 14], {
    label: 'CRUSHER CONTROL',
    railings: ['n', 'e', 's'],
    supports: true,
  }),
  a.prop('op.console', [-77.5, 6, -47], [1.2, 1.1, 4]),
  a.stair('op.stair', [-85, 0, -40], [-85, 6, -52], 2.2),

  a.platform('maint.deck', [-66, 6, -40], [7, 5], {
    label: 'CRUSHER MAINTENANCE',
    railings: ['n', 'e', 'w'],
    supports: true,
  }),
  a.catwalk('cat.east', [[-76, 6, -38], [-64, 6, -38], [-58, 5.5, -38], [-52, 5, -38]], 2.4, {
    label: 'CRUSHER → REFINERY HIGH LINK',
  }),

  a.stair('pit.stair', [-86, 0, -52], [-80, -5, -52], 2),

  a.doorway('door.spine', [-73, 0, -62], 4, 3.6, { label: 'S1' }),
  a.doorway('door.east', [-58, 0, -44], 4, 3.6, { rotationY: 90 }),

  a.spawn('spawn.hall', [-85, 0, -47], 'Crusher hall'),
  a.marker('m.deck', [-73, 0, -47], 'crossing', 'Tipping deck: no rails, live track'),
  a.marker('m.pit', [-80, -5, -47], 'shortcut', 'Pit floor is the west door of the service ring'),
  a.marker('m.jam', [-66, 6, -40], 'interaction', 'Crusher jam clearance'),
  a.marker('m.beltup', [-56, 3.5, -50], 'shortcut', 'Ride the output belt into the refinery'),

  a.mannequin('scale.1', [-86, 0, -47], { rotationY: 90 }),
  a.mannequin('scale.2', [-78, -5, -47]),
  a.mannequin('scale.3', [-80, 6, -43], { rotationY: 180 }),
];
