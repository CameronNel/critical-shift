import type { Zone } from './schema';

/**
 * Macro layout of the site.
 *
 * Two working datums keep the facility compact and interconnected:
 *   Y =  0  surface datum   - arrival, refinery floor, fuel, reactor floor,
 *                             medical, storage, compliance dock, yard
 *   Y = -8  underground     - mine, haulage drift, crusher pit, maintenance spine
 * Cooling sits at Y = -4 so that it reads as "below control" from the reactor.
 */
export const ZONES: Zone[] = [
  {
    id: 'yard',
    name: 'YARD',
    color: '#6a6d63',
    bounds: { min: [-132, -74], max: [122, 64] },
    signAt: [-64, 7, -40],
    levels: 'grade (0 m)',
    summary: 'Open surface between blocks. Long sightlines toward the compliance road.',
  },
  {
    id: 'arrival',
    name: 'ARRIVAL',
    color: '#6b7a8f',
    bounds: { min: [-122, -18], max: [-86, 18] },
    signAt: [-104, 8.5, 0],
    levels: '0 m',
    summary: 'Shift entrance, lockers, suit-up and briefing. Player start.',
  },
  {
    id: 'mine',
    name: 'MINE',
    color: '#6e6257',
    bounds: { min: [-146, -46], max: [-96, 24] },
    signAt: [-124, -2.5, -14],
    levels: '-8 m',
    summary: 'Excavated extraction chambers, branch drift and a risky maintenance rise.',
  },
  {
    id: 'haulage',
    name: 'HAULAGE',
    color: '#7a6a52',
    bounds: { min: [-98, -14], max: [-74, 14] },
    signAt: [-86, -2.5, 0],
    levels: '-8 m',
    summary: 'Cart drift from the mine to the crusher. Crosses the shaft-bottom walking route.',
  },
  {
    id: 'crusher',
    name: 'CRUSHER',
    color: '#8a6a4a',
    bounds: { min: [-76, -24], max: [-42, 16] },
    signAt: [-59, 12, -6],
    levels: '-8 m to +16 m',
    summary: 'Sunken tipping floor, primary crusher, and the climb onto the refinery deck.',
  },
  {
    id: 'refinery',
    name: 'REFINERY',
    color: '#7e8a72',
    bounds: { min: [-38, -34], max: [18, 24] },
    signAt: [-10, 13, -8],
    levels: '0 m, +5 m, +10 m',
    summary: 'Sorter, processor and dryer across three connected working levels.',
  },
  {
    id: 'fuel',
    name: 'FUEL',
    color: '#8a8452',
    bounds: { min: [22, -20], max: [52, 14] },
    signAt: [37, 9, -4],
    levels: '0 m, +6 m roof walk',
    summary: 'Assembly, inspection, containment store and the fuel corridor to the reactor.',
  },
  {
    id: 'medical',
    name: 'MEDICAL',
    color: '#7d8a8a',
    bounds: { min: [22, 18], max: [44, 34] },
    signAt: [33, 6.5, 26],
    levels: '0 m',
    summary: 'Reanimation and decontamination, deliberately off the main production line.',
  },
  {
    id: 'storage',
    name: 'STORAGE',
    color: '#74705f',
    bounds: { min: [-20, 26], max: [8, 48] },
    signAt: [-6, 7.5, 37],
    levels: '0 m',
    summary: 'Waste yard and bulk store. The obvious place to lose something inconvenient.',
  },
  {
    id: 'reactor',
    name: 'REACTOR',
    color: '#5f7d8c',
    bounds: { min: [58, -30], max: [114, 28] },
    signAt: [86, 24, 0],
    levels: '0 m, +9 m, +18 m',
    summary: 'The dominant volume. Core, working floor, catwalk ring and upper gantry.',
  },
  {
    id: 'control',
    name: 'CONTROL',
    color: '#8c8a9c',
    bounds: { min: [56, -8], max: [74, 12] },
    signAt: [63, 18.5, 2],
    levels: '+11 m',
    summary: 'Overlooks the core from the west wall. Good view, long walk down.',
  },
  {
    id: 'cooling',
    name: 'COOLING',
    color: '#5b7f88',
    bounds: { min: [60, 32], max: [108, 58] },
    signAt: [84, 7.5, 45],
    levels: '-4 m',
    summary: 'Pump hall below and south of control. Valves are a run away from the desk.',
  },
  {
    id: 'maintenance',
    name: 'MAINTENANCE',
    color: '#6a6a6a',
    bounds: { min: [-44, 8], max: [62, 22] },
    signAt: [12, -2.5, 15],
    levels: '-8 m',
    summary: 'Service spine under the plant. Fast, unlit, and out of sight of the floor.',
  },
  {
    id: 'compliance',
    name: 'COMPLIANCE',
    color: '#8c7a86',
    bounds: { min: [26, -70], max: [96, -32] },
    signAt: [74, 8.5, -52],
    levels: '0 m',
    summary: 'Auditor road and dock north of the plant. Visible from anything elevated.',
  },
];

export const ZONE_BY_ID = new Map(ZONES.map((z) => [z.id, z]));
