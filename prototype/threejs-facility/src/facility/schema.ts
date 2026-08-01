/**
 * Facility data schema.
 *
 * This is the authoritative description of the Critical Shift greybox. It is
 * plain JSON-serialisable data with no Three.js types, so the same document can
 * be exported, hand-edited, diffed, and eventually translated into whichever
 * production engine `docs/ENGINE_DECISION.md` selects.
 *
 * Units are metres. +X is east, +Z is south, +Y is up.
 * Rotations are degrees around Y unless stated otherwise.
 */

export type Vec2 = [number, number];
export type Vec3 = [number, number, number];

export const FACILITY_FORMAT = 'critical-shift.facility';
export const FACILITY_FORMAT_VERSION = 1;

export type ZoneId =
  | 'arrival'
  | 'mine'
  | 'haulage'
  | 'crusher'
  | 'refinery'
  | 'fuel'
  | 'reactor'
  | 'control'
  | 'cooling'
  | 'maintenance'
  | 'compliance'
  | 'storage'
  | 'medical'
  | 'yard';

export interface Zone {
  id: ZoneId;
  name: string;
  /** Orientation colour. Restrained palette, not an art pass. */
  color: string;
  /** Approximate XZ footprint, used by map mode and the zone legend. */
  bounds: { min: Vec2; max: Vec2 };
  /** Where the big orientation sign floats. */
  signAt: Vec3;
  /** Vertical band the zone occupies, for the map-mode elevation readout. */
  levels: string;
  summary: string;
}

export type EntityType =
  | 'floor'
  | 'wall'
  | 'platform'
  | 'stair'
  | 'ramp'
  | 'catwalk'
  | 'machine'
  | 'prop'
  | 'conveyor'
  | 'track'
  | 'pipe'
  | 'doorway'
  | 'cavern'
  | 'tunnel'
  | 'mannequin'
  | 'landmark'
  | 'spawn'
  | 'marker';

export interface EntityBase {
  /** Stable identifier. Used by persistence, the editor and cross-references. */
  id: string;
  type: EntityType;
  zone: ZoneId;
  label?: string;
  notes?: string;
  tags?: string[];
  /** Hex colour override. Omit to inherit the zone material. */
  color?: string;
  /** Force collision on or off. Omit to use the per-type default. */
  collision?: boolean;
  /** Hide from the walk/fly view but keep in the document (e.g. blockout aids). */
  hidden?: boolean;
}

/** Opening cut out of a wall: doorway, window, or conveyor penetration. */
export interface WallGap {
  /** Distance along the wall from `from`, to the centre of the gap. */
  at: number;
  width: number;
  /** Gap bottom, relative to the wall base. Default 0. */
  bottom?: number;
  /** Gap top, relative to the wall base. Default = wall height. */
  top?: number;
}

export interface FloorEntity extends EntityBase {
  type: 'floor';
  /** Centre of the walkable top surface. */
  position: Vec3;
  /** [sizeX, sizeZ] before rotation. */
  size: Vec2;
  /** Slab thickness, extending downwards from `position.y`. Default 0.3. */
  thickness?: number;
  rotationY?: number;
}

export interface WallEntity extends EntityBase {
  type: 'wall';
  from: Vec2;
  to: Vec2;
  /** Base elevation. Default 0. */
  base?: number;
  height: number;
  /** Default 0.3. */
  thickness?: number;
  gaps?: WallGap[];
}

export type RailSide = 'n' | 's' | 'e' | 'w';

export interface PlatformEntity extends EntityBase {
  type: 'platform';
  position: Vec3;
  size: Vec2;
  thickness?: number;
  rotationY?: number;
  /** Sides that get a guard rail, in the platform's local frame. */
  railings?: RailSide[];
  /** Drop legs to the level below. */
  supports?: boolean;
}

export interface StairEntity extends EntityBase {
  type: 'stair';
  /** Centre of the bottom of the flight, at the lower floor surface. */
  from: Vec3;
  /** Centre of the top of the flight, at the upper floor surface. */
  to: Vec3;
  width: number;
  railings?: boolean;
}

export interface RampEntity extends EntityBase {
  type: 'ramp';
  from: Vec3;
  to: Vec3;
  width: number;
  railings?: boolean;
}

export interface CatwalkEntity extends EntityBase {
  type: 'catwalk';
  /** Polyline of deck centre points. Elevation may change between points. */
  path: Vec3[];
  width: number;
  railings?: 'both' | 'left' | 'right' | 'none';
  supports?: boolean;
}

export type MachineShape = 'box' | 'cylinder' | 'cone' | 'frame' | 'hopper';

export interface MachineEntity extends EntityBase {
  type: 'machine';
  shape: MachineShape;
  /** Centre of the machine footprint, at its base. */
  position: Vec3;
  /** [x, height, z]. For cylinders/cones x is the diameter and z is ignored. */
  size: Vec3;
  rotationY?: number;
}

export interface PropEntity extends EntityBase {
  type: 'prop';
  shape: MachineShape;
  position: Vec3;
  size: Vec3;
  rotationY?: number;
}

export interface ConveyorEntity extends EntityBase {
  type: 'conveyor';
  /** Belt centreline. Material flows from path[0] toward the last point. */
  path: Vec3[];
  width: number;
  supports?: boolean;
  /** Walkable service deck alongside the belt is modelled as a catwalk. */
}

export interface TrackEntity extends EntityBase {
  type: 'track';
  path: Vec3[];
  gauge?: number;
  sleepers?: boolean;
}

export interface PipeEntity extends EntityBase {
  type: 'pipe';
  path: Vec3[];
  radius: number;
}

export interface DoorwayEntity extends EntityBase {
  type: 'doorway';
  /** Floor centre of the opening. */
  position: Vec3;
  width: number;
  height: number;
  rotationY?: number;
}

/** Opening in one side of a cavern, measured from the centre of that side. */
export interface CavernOpening {
  side: RailSide;
  /** Signed offset from the centre of the side. */
  at: number;
  width: number;
  /** Default: full chamber height. */
  height?: number;
}

/** Rough excavated chamber. Irregular shell, unlike the built facility. */
export interface CavernEntity extends EntityBase {
  type: 'cavern';
  /** Centre of the chamber floor. */
  position: Vec3;
  /** [x, height, z] of the void the chamber encloses. */
  size: Vec3;
  rotationY?: number;
  /** Deterministic irregularity seed. */
  seed?: number;
  /** Roughness of the rock shell, 0..1. Default 0.5. */
  rough?: number;
  openings?: CavernOpening[];
  /** Omit the rock ceiling, e.g. where a shaft rises. */
  openRoof?: boolean;
}

/** Rough excavated drift connecting caverns. */
export interface TunnelEntity extends EntityBase {
  type: 'tunnel';
  path: Vec3[];
  width: number;
  height: number;
  seed?: number;
  rough?: number;
}

export interface MannequinEntity extends EntityBase {
  type: 'mannequin';
  position: Vec3;
  rotationY?: number;
  /** Default 1.75. */
  height?: number;
}

export interface LandmarkEntity extends EntityBase {
  type: 'landmark';
  position: Vec3;
  text: string;
  /** Sign height in metres. Default 3. */
  size?: number;
}

export interface SpawnEntity extends EntityBase {
  type: 'spawn';
  position: Vec3;
  rotationY?: number;
  /** Shown in the teleport menu. */
  label: string;
  /** The default respawn point. Exactly one should set this. */
  primary?: boolean;
}

export type MarkerKind =
  | 'interaction'
  | 'hazard'
  | 'hiding'
  | 'shortcut'
  | 'sightline'
  | 'crossing'
  | 'objective';

export interface MarkerEntity extends EntityBase {
  type: 'marker';
  position: Vec3;
  kind: MarkerKind;
  label: string;
}

export type Entity =
  | FloorEntity
  | WallEntity
  | PlatformEntity
  | StairEntity
  | RampEntity
  | CatwalkEntity
  | MachineEntity
  | PropEntity
  | ConveyorEntity
  | TrackEntity
  | PipeEntity
  | DoorwayEntity
  | CavernEntity
  | TunnelEntity
  | MannequinEntity
  | LandmarkEntity
  | SpawnEntity
  | MarkerEntity;

/** A named circulation route, drawn in map mode to explain traversal. */
export interface Route {
  id: string;
  name: string;
  /** 'primary' safe production circulation, or an alternative. */
  kind: 'primary' | 'shortcut' | 'maintenance' | 'hazard' | 'compliance';
  color: string;
  path: Vec3[];
  notes?: string;
}

export interface FacilityDoc {
  format: typeof FACILITY_FORMAT;
  version: number;
  name: string;
  /** Free-form design notes carried with the layout. */
  description: string;
  zones: Zone[];
  entities: Entity[];
  routes: Route[];
}

/** Types that block movement by default. */
const SOLID_BY_DEFAULT: ReadonlySet<EntityType> = new Set<EntityType>([
  'wall',
  'machine',
  'prop',
  'cavern',
  'tunnel',
  'pipe',
]);

/** Types the player can stand on by default. */
const WALKABLE_BY_DEFAULT: ReadonlySet<EntityType> = new Set<EntityType>([
  'floor',
  'platform',
  'stair',
  'ramp',
  'catwalk',
  'cavern',
  'tunnel',
]);

export function isSolidByDefault(type: EntityType): boolean {
  return SOLID_BY_DEFAULT.has(type);
}

export function isWalkableByDefault(type: EntityType): boolean {
  return WALKABLE_BY_DEFAULT.has(type);
}

/** Entities that exist only as design annotations. */
export function isAnnotation(type: EntityType): boolean {
  return type === 'marker' || type === 'spawn' || type === 'landmark';
}
