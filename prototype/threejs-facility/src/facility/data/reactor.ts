import type { Entity } from '../schema';
import {
  REACTOR_BUILDING_CONTROL_ENTITIES,
  REACTOR_BUILDING_ENTITIES,
} from './reactorBuilding';

/**
 * Complete reactor-building rebuild.
 *
 * The previous greybox-derived visual scene is intentionally no longer used.
 * reactorBuilding.ts owns the new reference-driven interior, full exterior,
 * cooling towers, steam features, semantic labels and Blender-ready parts.
 */
export const REACTOR_ENTITIES: Entity[] = REACTOR_BUILDING_ENTITIES;
export const CONTROL_ENTITIES: Entity[] = REACTOR_BUILDING_CONTROL_ENTITIES;
