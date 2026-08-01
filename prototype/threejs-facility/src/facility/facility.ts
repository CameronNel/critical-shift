import {
  FACILITY_FORMAT,
  FACILITY_FORMAT_VERSION,
  type Entity,
  type FacilityDoc,
} from './schema';
import { ZONES } from './zones';
import { YARD_ENTITIES } from './data/yard';
import { ARRIVAL_ENTITIES } from './data/arrival';
import { MINE_ENTITIES } from './data/mine';
import { HAULAGE_ENTITIES } from './data/haulage';
import { CRUSHER_ENTITIES } from './data/crusher';
import { ROUTES } from './data/routes';

const ENTITIES: Entity[] = [
  ...YARD_ENTITIES,
  ...ARRIVAL_ENTITIES,
  ...MINE_ENTITIES,
  ...HAULAGE_ENTITIES,
  ...CRUSHER_ENTITIES,
];

export const DEFAULT_FACILITY: FacilityDoc = {
  format: FACILITY_FORMAT,
  version: FACILITY_FORMAT_VERSION,
  name: 'Critical Shift — Facility Greybox',
  description:
    'Structural skeleton of the Critical Shift site. Surface datum 0 m, service ' +
    'datum -6 m, mine datum -8 m. Greybox only: no props, no dressing, no art.',
  zones: ZONES,
  entities: ENTITIES,
  routes: ROUTES,
};

/** Deep copy so edits never mutate the repository default. */
export function defaultFacility(): FacilityDoc {
  return structuredClone(DEFAULT_FACILITY);
}
