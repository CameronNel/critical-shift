import type { Entity } from '../schema';
import { roomWalls, zoneAuthor } from './authoring';

const a = zoneAuthor('compliance');

/**
 * Compliance road and dock, north of the plant, and one long approach corridor
 * running south past the fuel block to the reactor's north door.
 *
 * The approach is deliberately legible: it is the obvious way in, it is a
 * single line, and three elevated positions can see it — the fuel roof deck,
 * the refinery clerestory, and the reactor's upper gantry. Anyone standing on
 * a working floor gets no warning at all.
 */
export const COMPLIANCE_ENTITIES: Entity[] = [
  a.floor('road', [10, 0.04, -114], [120, 8], { label: 'COMPLIANCE ROAD' }),

  a.floor('dock.slab', [18, 0, -102], [28, 16]),
  a.roof('dock.lid', [18, 6, -102], [28, 16]),
  ...roomWalls(a, 'dock', {
    min: [4, -110],
    max: [32, -94],
    height: 6,
    openings: [
      { side: 'n', at: 22, width: 6, top: 4.5 },
      { side: 's', at: 22, width: 5, top: 4 },
    ],
  }),

  // Dock down to the north spine, which it joins end-on.
  a.floor('approach.n', [22, 0, -82], [8, 24]),
  a.roof('approach.n.lid', [22, 5, -82], [8, 24]),
  a.wall('approach.n.w', [18, -94], [18, -70], 5),
  a.wall('approach.n.e', [26, -70], [26, -94], 5),

  // South past the east face of the fuel block. The fuel block's own east
  // wall is the corridor's west side, so its door opens straight into this.
  a.floor('approach.s', [22, 0, -51], [8, 38]),
  a.roof('approach.s.lid', [22, 5, -51], [8, 38]),
  a.wall('approach.s.w', [18, -70], [18, -62], 5),
  a.wall('approach.s.e', [26, -32], [26, -70], 5),

  // Last leg west to the reactor's north door, picking up the fuel block's
  // south door on the way.
  a.floor('approach.w', [16.5, 0, -28], [19, 8]),
  a.roof('approach.w.lid', [16.5, 5, -28], [19, 8]),
  a.wall('approach.w.s', [26, -24], [9, -24], 5),

  a.machine('dock.desk', 'AUDIT DOCK', [10, 0, -102], [5, 3.4, 6]),
  a.prop('barrier.1', [8, 0, -92], [6, 1.1, 0.5]),
  a.prop('barrier.2', [28, 0, -92], [6, 1.1, 0.5]),
  a.prop('vehicle', [40, 0, -114], [3, 2.6, 7]),

  a.doorway('door.dock', [22, 0, -94], 5, 4),

  a.spawn('spawn.compliance', [18, 0, -104], 'Compliance dock', { rotationY: 180 }),
  a.marker('m.arrival', [18, 0, -114], 'objective', 'Auditors arrive here'),
  a.marker('m.approach', [22, 0, -66], 'sightline', 'One line, seen from three elevated positions'),
  a.marker('m.fuel', [22, 0, -40], 'objective', 'Second way in: the fuel block east door'),
  a.marker('m.door', [7, 0, -27], 'objective', 'Reactor north door'),

  a.mannequin('scale.1', [22, 0, -88], { rotationY: 180 }),
  a.mannequin('scale.2', [18, 0, -106], { rotationY: 180 }),
];
