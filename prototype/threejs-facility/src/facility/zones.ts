import type { Zone } from './schema';

/**
 * Macro layout, following `docs/FACILITY_BLUEPRINT.md`.
 *
 * A compact loop rather than a line. The reactor hall is a central octagonal
 * volume; the production row (crusher, refinery, fuel) runs along the north
 * edge; haulage and the mine sit west; storage, medical and cooling south.
 * Everything is reachable more than one way, so route choice is tactical.
 *
 * Three working datums:
 *   Y =  0  surface      - production row, reactor, control, the yard
 *   Y = -5  service      - maintenance ring, crusher pit, cooling hall
 *   Y = -2  mine         - excavated chambers inside the rock mass to the west
 */
export const ZONES: Zone[] = [
  {
    id: 'yard',
    name: 'YARD',
    color: '#6a6d63',
    bounds: { min: [-182, -122], max: [74, 84] },
    signAt: [-30, 9, 76],
    levels: 'grade (0 m)',
    summary: 'Open surface, the north spine corridor, and the diagonal access run.',
  },
  {
    id: 'arrival',
    name: 'ARRIVAL',
    color: '#6b7a8f',
    bounds: { min: [-132, -56], max: [-100, -28] },
    signAt: [-116, 9, -42],
    levels: '0 m',
    summary: 'Shift entrance, lockers, suit-up and briefing, on the cart hall corner by the adit.',
  },
  {
    id: 'mine',
    name: 'MINE',
    color: '#6e6257',
    bounds: { min: [-170, -32], max: [-116, 14] },
    signAt: [-144, 3, -8],
    levels: '-2 m, inside the rock',
    summary: 'Extraction chambers driven west into the rock mass. Ore vein, dead-end store.',
  },
  {
    id: 'haulage',
    name: 'HAULAGE',
    color: '#7a6a52',
    bounds: { min: [-112, -28], max: [-56, 28] },
    signAt: [-84, 10, 0],
    levels: '0 m',
    summary: 'Cart loop between the mine and the crusher. Spurs north and east.',
  },
  {
    id: 'crusher',
    name: 'CRUSHER',
    color: '#8a6a4a',
    bounds: { min: [-88, -62], max: [-58, -32] },
    signAt: [-73, 14, -47],
    levels: '-5 m to +20 m',
    summary: 'Tipping deck over an open pit. The pit is the way into the service ring.',
  },
  {
    id: 'refinery',
    name: 'REFINERY',
    color: '#7e8a72',
    bounds: { min: [-54, -62], max: [-14, -32] },
    signAt: [-34, 15, -47],
    levels: '0 m, +5 m, +10 m, +14 m',
    summary: 'Sorter, processor and dryer on one belt line. Four working elevations.',
  },
  {
    id: 'fuel',
    name: 'FUEL',
    color: '#8a8452',
    bounds: { min: [-10, -62], max: [18, -32] },
    signAt: [4, 12, -47],
    levels: '0 m, +10 m roof deck',
    summary: 'Assembly, inspection, containment store. Its roof watches the compliance road.',
  },
  {
    id: 'reactor',
    name: 'REACTOR',
    color: '#5f7d8c',
    bounds: { min: [-26, -26], max: [26, 26] },
    signAt: [0, 27, 0],
    levels: '0 m gallery; the rest sealed',
    summary: 'Sealed octagonal hall. A gallery reaches the fuel deposit, the operating face and the way out to cooling; nothing else.',
  },
  {
    id: 'control',
    name: 'CONTROL',
    color: '#8c8a9c',
    bounds: { min: [30, -14], max: [54, 14] },
    signAt: [42, 20, 0],
    levels: '+10 m',
    summary: 'East of the reactor, raised, looking in through the overlook windows.',
  },
  {
    id: 'cooling',
    name: 'COOLING',
    color: '#5b7f88',
    bounds: { min: [28, 28], max: [60, 62] },
    signAt: [44, 6, 45],
    levels: '-5 m, lid flush with grade',
    summary: 'Sunk south-east of the reactor. Open cut on its north side, drains west.',
  },
  {
    id: 'storage',
    name: 'STORAGE',
    color: '#74705f',
    bounds: { min: [-86, 30], max: [-46, 58] },
    signAt: [-66, 8, 44],
    levels: '0 m',
    summary: 'Waste yard and bulk store, with a stair down into the service ring.',
  },
  {
    id: 'medical',
    name: 'MEDICAL',
    color: '#7d8a8a',
    bounds: { min: [-36, 44], max: [-6, 70] },
    signAt: [-21, 7, 57],
    levels: '0 m',
    summary: 'Reanimation and decontamination, on the southern loop.',
  },
  {
    id: 'maintenance',
    name: 'MAINTENANCE',
    color: '#6a6a6a',
    bounds: { min: [-130, -38], max: [44, 38] },
    signAt: [-96, -1.5, 0],
    levels: '-5 m',
    summary: 'Service ring under the site. Hidden flanking access to almost everywhere.',
  },
  {
    id: 'compliance',
    name: 'COMPLIANCE',
    color: '#8c7a86',
    bounds: { min: [-4, -122], max: [34, -24] },
    signAt: [18, 9, -100],
    levels: '0 m',
    summary: 'Road and dock north of the plant, then one long corridor to the reactor door.',
  },
];

export const ZONE_BY_ID = new Map(ZONES.map((z) => [z.id, z]));
