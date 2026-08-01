import type { Entity } from '../schema';
import { zoneAuthor } from './authoring';

const a = zoneAuthor('maintenance');

/**
 * Service ring on the -5 m datum: a closed loop of 4 m corridors under the
 * plant with four ways in and out — the crusher pit, the storage stairwell,
 * the mine's service tunnel, and the cooling hall it drains into.
 *
 * 4 m clear so two people pass and a body drags without snagging. A loop, not
 * a maze: whichever way you set off, you come out somewhere useful.
 */
export const MAINTENANCE_ENTITIES: Entity[] = [
  a.floor('leg.w', [-96, -5, 1], [4, 70]),
  a.floor('leg.n', [-59, -5, -34], [78, 4]),
  a.floor('leg.s', [-32, -5, 34], [132, 4]),
  a.floor('leg.e', [32, -5, 15], [4, 38]),
  a.roof('leg.w.lid', [-96, -1, 1], [4, 70]),
  a.roof('leg.n.lid', [-59, -1, -34], [78, 4]),
  a.roof('leg.s.lid', [-32, -1, 34], [132, 4]),
  a.roof('leg.e.lid', [32, -1, 15], [4, 38]),

  // West leg. The mine's service tunnel arrives through the outer wall.
  a.wall('leg.w.outer', [-98, -34], [-98, 36], 4, {
    base: -5,
    thickness: 0.3,
    gaps: [{ at: 42, width: 4 }],
  }),
  a.wall('leg.w.inner.n', [-94, -32], [-94, 4], 4, { base: -5, thickness: 0.3 }),
  a.wall('leg.w.inner.s', [-94, 12], [-94, 32], 4, { base: -5, thickness: 0.3 }),

  // North leg. The crusher pit opens straight into it.
  a.wall('leg.n.outer', [-98, -36], [-20, -36], 4, {
    base: -5,
    thickness: 0.3,
    gaps: [{ at: 25, width: 22 }],
  }),
  a.wall('leg.n.inner', [-20, -32], [-92, -32], 4, { base: -5, thickness: 0.3 }),
  a.wall('leg.n.end', [-20, -36], [-20, -32], 4, { base: -5, thickness: 0.3 }),

  // South leg. Its outer wall is broken for the storage stairwell.
  a.wall('leg.s.outer', [34, 36], [-98, 36], 4, {
    base: -5,
    thickness: 0.3,
    gaps: [{ at: 90, width: 8 }], // storage stairwell
  }),
  a.wall('leg.s.inner', [-92, 32], [30, 32], 4, { base: -5, thickness: 0.3 }),

  // East leg, running north from the cooling hall.
  a.wall('leg.e.outer', [34, 32], [34, -4], 4, { base: -5, thickness: 0.3 }),
  a.wall('leg.e.inner', [30, -4], [30, 32], 4, { base: -5, thickness: 0.3 }),
  a.wall('leg.e.end', [30, -4], [34, -4], 4, { base: -5, thickness: 0.3 }),

  // Tool store: the one room down here with a door and a reason to linger.
  a.floor('store', [-87, -5, 8], [10, 8], { label: 'TOOL STORE' }),
  a.roof('store.lid', [-87, -1, 8], [10, 8]),
  a.wall('store.n', [-92, 4], [-82, 4], 4, { base: -5, thickness: 0.3 }),
  a.wall('store.e', [-82, 4], [-82, 12], 4, { base: -5, thickness: 0.3 }),
  a.wall('store.s', [-82, 12], [-92, 12], 4, { base: -5, thickness: 0.3 }),
  a.machine('bench', 'TOOL STORE', [-89, -5, 10], [4, 1.2, 5]),
  a.prop('racks', [-83, -5, 8], [1.4, 2.4, 6]),
  a.prop('spares', [-87, -5, 5.5], [4, 1.6, 2]),

  a.spawn('spawn.ring', [-96, -5, 0], 'Service ring'),
  a.marker('m.ring', [-32, -5, 34], 'shortcut', 'Service ring: a loop, not a maze'),
  a.marker('m.store', [-87, -5, 8], 'hiding', 'Tool store: lockable, and nobody audits it'),
  a.marker('m.pit', [-73, -5, -34], 'shortcut', 'Up into the crusher pit'),
  a.marker('m.drain', [32, -5, 28], 'shortcut', 'East leg drains into the cooling hall'),
  a.marker('m.mine', [-96, -5, 8], 'shortcut', 'Mine service tunnel arrives here'),

  a.mannequin('scale.1', [-60, -5, 34], { rotationY: 90 }),
  a.mannequin('scale.2', [-96, -5, -10], { rotationY: 0 }),
];
