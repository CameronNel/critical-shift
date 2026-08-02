import type { Entity } from '../schema';
import { translateEntity } from '../../editor/transforms';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('arrival');

/**
 * The block is authored around its own origin and then moved as one piece.
 * It used to sit at the far north-west, a long walk from anything; it now sits
 * on the cart hall's north-west corner so that stepping out of it puts the
 * mine adit about thirty metres away and the crusher spur about the same.
 */
const MOVE: [number, number, number] = [-4, 0, 30];

const HAZARD = '#c2622c';
const CLEAN = '#5f8f96';

/**
 * Arrival block, authored at X -128..-96, Z -86..-58 and moved to
 * X -132..-100, Z -56..-28 by MOVE. 6 m clear.
 *
 * Built to carry the whole preparation beat (GAME_SPEC §8.2) and every step of
 * the suit procedure (§6.2), because the three minutes spent in here are the
 * first real decision of the shift and players cannot afford everything.
 *
 * Three bands north to south:
 *   Z -86..-76   shift office | locker room | suit-up
 *   Z -76..-70   central corridor, with decontamination at its east end
 *   Z -70..-58   briefing | requisition
 *
 * The two east exits belong to different routes: the north one is the suited
 * route out through decontamination, the south one drops onto S1 with whatever
 * you drew from the store. You cannot easily do both and still be on time.
 */
const ARRIVAL_SOURCE: Entity[] = [
  a.floor('slab', [-112, 0, -72], [32, 28]),
  a.roof('lid', [-112, 6, -72], [32, 28]),

  ...roomWalls(a, 'shell', {
    min: [-128, -86],
    max: [-96, -58],
    height: 6,
    openings: [
      { side: 'w', at: -73, width: 6, top: 3.6 }, // site entrance
      { side: 'e', at: -73, width: 5, top: 3.6 }, // suited route out
      { side: 'e', at: -64.5, width: 4.5, top: 4 }, // onto S1
      { side: 's', at: -112, width: 4, top: 3.6 }, // down to haulage
    ],
  }),

  // --- Band partitions ------------------------------------------------------
  a.wall('part.north', [-127.6, -76], [-96.4, -76], 3.6, {
    thickness: 0.3,
    gaps: [
      { at: 3.6, width: 3 }, // shift office
      { at: 8.6, width: 3, bottom: 1.1, top: 2.6 }, // office window
      { at: 14.6, width: 4 }, // locker room
      { at: 26.6, width: 4 }, // suit-up
    ],
  }),
  a.wall('part.south', [-96.4, -70], [-127.6, -70], 3.6, {
    thickness: 0.3,
    gaps: [
      { at: 7.6, width: 5 }, // requisition
      { at: 23.6, width: 5 }, // briefing
    ],
  }),
  a.wall('part.office', [-118, -85.6], [-118, -76], 3.6, {
    thickness: 0.3,
  }),
  a.wall('part.suits', [-105, -85.6], [-105, -76], 3.6, {
    thickness: 0.3,
    gaps: [{ at: 6, width: 4 }],
  }),
  a.wall('part.brief', [-112, -70], [-112, -58.4], 3.6, {
    thickness: 0.3,
    gaps: [{ at: 6, width: 4 }],
  }),
  a.wall('part.decon', [-103, -76], [-103, -70], 3.6, {
    thickness: 0.3,
    gaps: [{ at: 3, width: 3, top: 2.6 }],
  }),

  // --- Shift office ---------------------------------------------------------
  a.machine('office.desk', 'SHIFT SUPERVISOR', [-123, 0, -82], [4, 1.1, 1.8]),
  a.prop('office.chair', [-123, 0, -80.4], [0.7, 1.1, 0.7]),
  a.prop('office.cabinets', [-127, 0, -79], [1, 2, 5]),
  a.machine('office.roster', 'DUTY ROSTER', [-124.5, 1.2, -85.2], [5, 2, 0.3]),
  a.prop('office.radio', [-119.4, 0, -83], [0.8, 1.6, 2.4]),
  a.light('office.l1', [-124, 5.4, -83]),
  a.light('office.l2', [-122, 5.4, -78]),
  a.marker('m.roles', [-123, 0, -80], 'interaction', 'Informal roles get decided here'),

  // --- Locker room ----------------------------------------------------------
  a.prop('lockers.n1', [-116.5, 0, -85], [3, 2.3, 0.7]),
  a.prop('lockers.n2', [-113, 0, -85], [3, 2.3, 0.7]),
  a.prop('lockers.n3', [-109.5, 0, -85], [3, 2.3, 0.7]),
  a.prop('lockers.n4', [-106.2, 0, -85], [3, 2.3, 0.7]),
  a.prop('lockers.i1', [-116.5, 0, -80.5], [3, 2.3, 1.4]),
  a.prop('lockers.i2', [-113, 0, -80.5], [3, 2.3, 1.4]),
  a.prop('lockers.i3', [-109.5, 0, -80.5], [3, 2.3, 1.4]),
  a.prop('lockers.i4', [-106.2, 0, -80.5], [3, 2.3, 1.4]),
  a.prop('lockers.bench.n', [-111.5, 0, -83], [12, 0.44, 0.6]),
  a.prop('lockers.bench.s', [-111.5, 0, -78], [12, 0.44, 0.6]),
  a.prop('lockers.boots', [-117.6, 0, -77.5], [1, 1.4, 3]),
  a.machine('lockers.sign', 'LOCKERS 01–24', [-111.5, 3, -85.4], [6, 0.8, 0.3]),
  a.light('lockers.l1', [-116, 5.4, -83], { cast: true, intensity: 90, distance: 22 }),
  a.light('lockers.l2', [-111, 5.4, -83]),
  a.light('lockers.l3', [-113, 5.4, -78]),
  a.marker('m.locker', [-113, 0, -83], 'interaction', 'Open assigned locker · step out of duty gear'),

  // --- Suit-up --------------------------------------------------------------
  a.prop('suits.n1', [-103.5, 0, -85], [1.1, 2.4, 0.8]),
  a.prop('suits.n2', [-101.8, 0, -85], [1.1, 2.4, 0.8]),
  a.prop('suits.n3', [-100.1, 0, -85], [1.1, 2.4, 0.8]),
  a.prop('suits.n4', [-98.4, 0, -85], [1.1, 2.4, 0.8]),
  a.prop('suits.w1', [-104.2, 0, -83], [0.8, 2.4, 1.1]),
  a.prop('suits.w2', [-104.2, 0, -81.3], [0.8, 2.4, 1.1]),
  a.prop('suits.w3', [-104.2, 0, -79.6], [0.8, 2.4, 1.1]),
  a.machine('suits.helmets', 'HELMET SHELF', [-100.5, 1.3, -82], [4, 0.4, 1]),
  a.machine('suits.test', 'SUIT INTEGRITY TEST', [-98.6, 0, -82.5], [2.4, 3, 2.4], {
    color: CLEAN,
  }),
  a.light('suits.test.lamp', [-98.6, 3.1, -82.5], { size: [1.8, 1.8], color: '#8fe3d0' }),
  a.machine('suits.dosimeters', 'DOSIMETERS', [-98.6, 0, -78], [1.2, 2, 2.4]),
  a.light('suits.l1', [-101, 5.4, -84], { cast: true, intensity: 90, distance: 20 }),
  a.light('suits.l2', [-101, 5.4, -79]),
  a.marker('m.suit.equip', [-102, 0, -83.5], 'interaction', 'Equip protective layer'),
  a.marker('m.suit.helmet', [-100.5, 0, -81], 'interaction', 'Seal helmet'),
  a.marker('m.suit.test', [-98.6, 0, -80.5], 'interaction', 'Run integrity test — skippable, and people skip it'),
  a.marker('m.suit.dose', [-98.6, 0, -76.6], 'interaction', 'Collect dosimeter'),

  // --- Central corridor -----------------------------------------------------
  a.prop('corridor.notice.1', [-120, 0, -75.6], [4, 2.2, 0.25]),
  a.prop('corridor.notice.2', [-108, 0, -75.6], [4, 2.2, 0.25]),
  a.prop('corridor.bench', [-116, 0, -70.6], [5, 0.44, 0.6]),
  a.light('corridor.l1', [-124, 5.4, -73]),
  a.light('corridor.l2', [-116, 5.4, -73], { cast: true, intensity: 110, distance: 26 }),
  a.light('corridor.l3', [-108, 5.4, -73]),
  a.marker('m.split', [-114, 0, -73], 'shortcut', 'North: suit and decon. South: draw stores and take S1.'),

  // --- Decontamination ------------------------------------------------------
  a.machine('decon.arch', 'DECONTAMINATION', [-100, 0, -73], [5, 3.2, 5], {
    shape: 'frame',
    color: CLEAN,
  }),
  a.machine('decon.monitor', 'CONTAMINATION MONITOR', [-97.4, 0, -71], [1, 2.2, 1.6], {
    color: CLEAN,
  }),
  a.prop('decon.drain', [-100, 0, -73], [3, 0.12, 3]),
  a.light('decon.l1', [-100, 5.4, -73], { size: [3, 1], color: '#a9e6dd' }),
  a.marker('m.decon', [-100, 0, -74.5], 'interaction', 'Pass decontamination'),
  a.marker('m.decon.risk', [-97.4, 0, -73], 'hazard', 'A damaged suit traps contamination inside'),

  // --- Briefing -------------------------------------------------------------
  a.platform('brief.dais', [-120, 0.25, -63], [13, 9]),
  a.machine('brief.board', 'BRIEFING BOARD', [-120, 0.25, -58.9], [10, 3, 0.4]),
  a.machine('brief.contract', 'CONTRACT', [-127, 0.25, -62], [0.4, 2.4, 6]),
  a.prop('brief.podium', [-114.5, 0.25, -60.5], [1.2, 1.2, 0.8]),
  a.prop('brief.bench.1', [-120, 0.25, -60.5], [10, 0.44, 0.7]),
  a.prop('brief.bench.2', [-120, 0.25, -62.5], [10, 0.44, 0.7]),
  a.prop('brief.bench.3', [-120, 0.25, -64.5], [10, 0.44, 0.7]),
  a.light('brief.l1', [-124, 5.4, -62], { cast: true, intensity: 90, distance: 22 }),
  a.light('brief.l2', [-118, 5.4, -62]),
  a.light('brief.l3', [-120, 5.4, -67]),
  a.marker('m.brief', [-120, 0.25, -61.5], 'objective', 'Shift briefing'),

  // --- Requisition ----------------------------------------------------------
  a.machine('req.tools', 'TOOL CRIB', [-109, 0, -68], [5, 2.6, 3]),
  a.machine('req.explosives', 'EXPLOSIVES CAGE', [-102, 0, -68], [4.5, 2.6, 3], {
    color: HAZARD,
  }),
  a.machine('req.spares', 'SPARE PARTS', [-109, 0, -61], [5, 2.4, 3]),
  a.machine('req.medical', 'MEDICAL SUPPLIES', [-102.5, 0, -61], [4, 2.2, 3]),
  a.machine('req.upgrades', 'MACHINE UPGRADES', [-97.6, 0, -60.5], [1.6, 2.2, 3]),
  a.machine('req.priority', 'REPAIR PRIORITIES', [-105.5, 0, -58.9], [5, 2.4, 0.4]),
  a.prop('req.counter', [-105.5, 0, -64.5], [9, 1.1, 0.7]),
  a.prop('req.pallet.1', [-110.5, 0, -64.5], [2, 0.3, 2]),
  a.prop('req.cart', [-99, 0, -68.5], [1, 1, 1.8]),
  a.light('req.l1', [-108, 5.4, -67], { cast: true, intensity: 90, distance: 22 }),
  a.light('req.l2', [-102, 5.4, -67]),
  a.light('req.l3', [-105, 5.4, -61]),
  a.marker('m.req.tools', [-109, 0, -65.8], 'interaction', 'Tools'),
  a.marker('m.req.explosives', [-102, 0, -65.8], 'interaction', 'Explosives — the shortcut you pay for later'),
  a.marker('m.req.spares', [-109, 0, -63], 'interaction', 'Spare parts'),
  a.marker('m.req.medical', [-102.5, 0, -63], 'interaction', 'Medical supplies'),
  a.marker('m.req.budget', [-105.5, 0, -66.5], 'objective', 'You cannot afford everything'),

  // --- Doors, spawns, scale -------------------------------------------------
  a.doorway('door.west', [-128, 0, -73], 6, 3.6, { rotationY: 90, label: 'SHIFT ENTRANCE' }),
  a.doorway('door.east', [-96, 0, -73], 5, 3.6, { rotationY: 90 }),
  a.doorway('door.spine', [-96, 0, -64.5], 4.5, 4, { rotationY: 90, label: 'S1' }),
  a.doorway('door.south', [-112, 0, -58], 4, 3.6),

  a.spawn('spawn.start', [-124, 0, -73], 'Shift entrance', { primary: true, rotationY: 270 }),
  a.spawn('spawn.brief', [-120, 0.25, -64], 'Briefing'),
  a.spawn('spawn.lockers', [-108, 0, -82], 'Locker room'),
  a.spawn('spawn.req', [-105, 0, -65], 'Requisition'),

  a.mannequin('scale.1', [-113, 0, -82.5], { rotationY: 0 }),
  a.mannequin('scale.2', [-101.8, 0, -83.8], { rotationY: 0 }),
  a.mannequin('scale.3', [-120, 0.25, -64.5], { rotationY: 180 }),
  a.mannequin('scale.4', [-105.5, 0, -65.8], { rotationY: 0 }),
  a.mannequin('scale.5', [-116, 0, -73], { rotationY: 270 }),
];

export const ARRIVAL_ENTITIES: Entity[] = ARRIVAL_SOURCE.map((e) =>
  translateEntity(e, MOVE),
);
