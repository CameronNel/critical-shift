import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('compliance');

/**
 * Compliance road and dock, north of the plant.
 *
 * One obvious primary approach: road → dock → eighteen open metres → reactor
 * north door. Those metres are visible from the reactor upper gantry, the
 * refinery clerestory and the fuel roof deck, so an elevated player gets a
 * warning and a floor player does not. The road continues west past the
 * refinery north door, which is the quieter second way in.
 */
export const COMPLIANCE_ENTITIES: Entity[] = [
  a.floor('road', [30, 0.04, -66], [140, 8], { label: 'COMPLIANCE ROAD' }),
  a.floor('apron', [76, 0.04, -44], [24, 12]),

  a.floor('dock.slab', [76, 0, -55], [20, 14]),
  a.roof('dock.lid', [76, 6, -55], [20, 14]),
  ...roomWalls(a, 'dock', {
    min: [66, -62],
    max: [86, -48],
    height: 6,
    openings: [
      { side: 'n', at: 76, width: 6, top: 4.5 },
      { side: 's', at: 76, width: 5, top: 4 },
    ],
  }),

  a.machine('dock.desk', 'AUDIT DOCK', [70, 0, -55], [5, 3.4, 6]),
  a.prop('barrier.1', [66, 0, -46], [6, 1.1, 0.5]),
  a.prop('barrier.2', [86, 0, -46], [6, 1.1, 0.5]),
  a.prop('vehicle', [90, 0, -66], [3, 2.6, 7]),

  a.doorway('door.dock', [76, 0, -48], 5, 4),

  a.spawn('spawn.compliance', [76, 0, -58], 'Compliance dock', { rotationY: 180 }),
  a.marker('m.arrival', [76, 0, -66], 'objective', 'Auditors arrive here'),
  a.marker('m.open', [76, 0, -38], 'sightline', 'Eighteen open metres to the reactor door'),
  a.marker('m.westroad', [34, 0, -66], 'shortcut', 'Road continues past the refinery north door'),
  a.marker('m.refinery', [-24, 0, -38], 'objective', 'Second way in: refinery north door'),

  a.mannequin('scale.1', [76, 0, -44], { rotationY: 180 }),
  a.mannequin('scale.2', [76, 0, -60], { rotationY: 180 }),
];
