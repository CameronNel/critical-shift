import type { Zone } from './schema';

/**
 * Macro layout of the site.
 *
 * Three working datums keep the facility compact and interconnected:
 *   Y =  0  surface datum  - arrival, crusher hall, refinery, fuel, medical,
 *                            storage, reactor floor, compliance dock, yard
 *   Y = -6  service datum  - crusher pit and the maintenance spine that runs
 *                            under the plant from the crusher to cooling
 *   Y = -8  mine datum     - extraction chambers and the haulage drift
 *
 * Cooling sits on the service datum directly south of and below the control
 * room, so "cooling is below control" is literally true when you look down.
 */
export const ZONES: Zone[] = [
  {
    id: 'yard',
    name: 'YARD',
    color: '#6a6d63',
    bounds: { min: [-142, -78], max: [126, 66] },
    signAt: [-20, 9, 56],
    levels: 'grade (0 m)',
    summary: 'Open surface between blocks. Long sightlines toward the compliance road.',
  },
  {
    id: 'arrival',
    name: 'ARRIVAL',
    color: '#6b7a8f',
    bounds: { min: [-120, -18], max: [-88, 18] },
    signAt: [-104, 9, 0],
    levels: '0 m',
    summary: 'Shift entrance, lockers, suit-up and briefing. Player start.',
  },
  {
    id: 'mine',
    name: 'MINE',
    color: '#6e6257',
    bounds: { min: [-146, -48], max: [-108, -4] },
    signAt: [-124, -3, -16],
    levels: '-8 m',
    summary: 'Excavated extraction face, a branch drift, a dead-end store, and the rise.',
  },
  {
    id: 'haulage',
    name: 'HAULAGE',
    color: '#7a6a52',
    bounds: { min: [-112, -22], max: [-74, 42] },
    signAt: [-80, 2.5, 24],
    levels: '-8 m to 0 m',
    summary: 'Open decline and cart drift. Everyone shares it with the carts.',
  },
  {
    id: 'crusher',
    name: 'CRUSHER',
    color: '#8a6a4a',
    bounds: { min: [-70, -26], max: [-36, 12] },
    signAt: [-53, 14, -6],
    levels: '-6 m to +20 m',
    summary: 'Tipping deck over an open pit, the primary crusher, and the climb east.',
  },
  {
    id: 'refinery',
    name: 'REFINERY',
    color: '#7e8a72',
    bounds: { min: [-32, -34], max: [24, 22] },
    signAt: [-4, 20, -6],
    levels: '0 m, +5 m, +10 m',
    summary: 'Sorter, processor and dryer across three connected working levels.',
  },
  {
    id: 'fuel',
    name: 'FUEL',
    color: '#8a8452',
    bounds: { min: [28, -20], max: [58, 12] },
    signAt: [43, 11, -4],
    levels: '0 m, +8 m roof walk',
    summary: 'Assembly, inspection, containment store and the corridor to the reactor.',
  },
  {
    id: 'medical',
    name: 'MEDICAL',
    color: '#7d8a8a',
    bounds: { min: [28, 18], max: [50, 34] },
    signAt: [39, 7, 26],
    levels: '0 m',
    summary: 'Reanimation and decontamination, deliberately off the production line.',
  },
  {
    id: 'storage',
    name: 'STORAGE',
    color: '#74705f',
    bounds: { min: [-14, 26], max: [14, 46] },
    signAt: [0, 8, 36],
    levels: '0 m',
    summary: 'Waste yard and bulk store. The obvious place to lose something.',
  },
  {
    id: 'reactor',
    name: 'REACTOR',
    color: '#5f7d8c',
    bounds: { min: [64, -30], max: [120, 28] },
    signAt: [92, 26, -1],
    levels: '0 m, +9 m, +18 m',
    summary: 'The dominant volume. Core, working floor, catwalk ring and upper gantry.',
  },
  {
    id: 'control',
    name: 'CONTROL',
    color: '#8c8a9c',
    bounds: { min: [63, -7], max: [77, 11] },
    signAt: [70, 18, 2],
    levels: '+11 m',
    summary: 'Open balcony on the reactor west wall. Great view, long walk down.',
  },
  {
    id: 'cooling',
    name: 'COOLING',
    color: '#5b7f88',
    bounds: { min: [66, 32], max: [112, 58] },
    signAt: [89, 4, 45],
    levels: '-6 m, +1 m lid',
    summary: 'Pump hall below and south of control. The valves are a run away.',
  },
  {
    id: 'maintenance',
    name: 'MAINTENANCE',
    color: '#6a6a6a',
    bounds: { min: [-106, 2], max: [70, 40] },
    signAt: [10, -2.5, 16],
    levels: '-6 m',
    summary: 'Service spine under the plant. Fast, unlit, and out of sight of the floor.',
  },
  {
    id: 'compliance',
    name: 'COMPLIANCE',
    color: '#8c7a86',
    bounds: { min: [-40, -70], max: [100, -34] },
    signAt: [76, 9, -55],
    levels: '0 m',
    summary: 'Auditor road and dock north of the plant. Visible from anything elevated.',
  },
];

export const ZONE_BY_ID = new Map(ZONES.map((z) => [z.id, z]));
