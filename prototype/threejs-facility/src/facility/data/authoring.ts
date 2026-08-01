import type {
  CatwalkEntity,
  CavernEntity,
  ConveyorEntity,
  DoorwayEntity,
  FloorEntity,
  LandmarkEntity,
  MachineEntity,
  MannequinEntity,
  MarkerEntity,
  PipeEntity,
  PlatformEntity,
  PropEntity,
  RampEntity,
  SpawnEntity,
  StairEntity,
  TrackEntity,
  TunnelEntity,
  Vec2,
  Vec3,
  WallEntity,
  ZoneId,
} from '../schema';

type Extra<T> = Partial<Omit<T, 'id' | 'type' | 'zone'>>;

/**
 * Thin authoring sugar over the schema. Every helper returns plain data, so
 * the exported JSON is exactly what the layout modules describe.
 */
export function zoneAuthor(zone: ZoneId) {
  const id = (name: string) => `${zone}.${name}`;
  return {
    floor: (name: string, position: Vec3, size: Vec2, extra: Extra<FloorEntity> = {}): FloorEntity => ({
      id: id(name),
      type: 'floor',
      zone,
      position,
      size,
      ...extra,
    }),
    roof: (name: string, position: Vec3, size: Vec2, extra: Extra<FloorEntity> = {}): FloorEntity => ({
      id: id(name),
      type: 'floor',
      zone,
      position,
      size,
      ...extra,
      tags: ['roof', ...(extra.tags ?? [])],
    }),
    grade: (name: string, position: Vec3, size: Vec2, extra: Extra<FloorEntity> = {}): FloorEntity => ({
      id: id(name),
      type: 'floor',
      zone,
      position,
      size,
      thickness: 0.6,
      ...extra,
      tags: ['grade', ...(extra.tags ?? [])],
    }),
    wall: (
      name: string,
      from: Vec2,
      to: Vec2,
      height: number,
      extra: Extra<WallEntity> = {},
    ): WallEntity => ({ id: id(name), type: 'wall', zone, from, to, height, ...extra }),
    platform: (
      name: string,
      position: Vec3,
      size: Vec2,
      extra: Extra<PlatformEntity> = {},
    ): PlatformEntity => ({ id: id(name), type: 'platform', zone, position, size, ...extra }),
    stair: (
      name: string,
      from: Vec3,
      to: Vec3,
      width: number,
      extra: Extra<StairEntity> = {},
    ): StairEntity => ({ id: id(name), type: 'stair', zone, from, to, width, ...extra }),
    ramp: (
      name: string,
      from: Vec3,
      to: Vec3,
      width: number,
      extra: Extra<RampEntity> = {},
    ): RampEntity => ({ id: id(name), type: 'ramp', zone, from, to, width, ...extra }),
    catwalk: (
      name: string,
      path: Vec3[],
      width: number,
      extra: Extra<CatwalkEntity> = {},
    ): CatwalkEntity => ({ id: id(name), type: 'catwalk', zone, path, width, ...extra }),
    machine: (
      name: string,
      label: string,
      position: Vec3,
      size: Vec3,
      extra: Extra<MachineEntity> = {},
    ): MachineEntity => ({
      id: id(name),
      type: 'machine',
      zone,
      shape: 'box',
      position,
      size,
      label,
      ...extra,
    }),
    prop: (
      name: string,
      position: Vec3,
      size: Vec3,
      extra: Extra<PropEntity> = {},
    ): PropEntity => ({
      id: id(name),
      type: 'prop',
      zone,
      shape: 'box',
      position,
      size,
      ...extra,
    }),
    conveyor: (
      name: string,
      path: Vec3[],
      width: number,
      extra: Extra<ConveyorEntity> = {},
    ): ConveyorEntity => ({ id: id(name), type: 'conveyor', zone, path, width, ...extra }),
    track: (name: string, path: Vec3[], extra: Extra<TrackEntity> = {}): TrackEntity => ({
      id: id(name),
      type: 'track',
      zone,
      path,
      ...extra,
    }),
    pipe: (
      name: string,
      path: Vec3[],
      radius: number,
      extra: Extra<PipeEntity> = {},
    ): PipeEntity => ({ id: id(name), type: 'pipe', zone, path, radius, ...extra }),
    doorway: (
      name: string,
      position: Vec3,
      width: number,
      height: number,
      extra: Extra<DoorwayEntity> = {},
    ): DoorwayEntity => ({
      id: id(name),
      type: 'doorway',
      zone,
      position,
      width,
      height,
      ...extra,
    }),
    cavern: (
      name: string,
      position: Vec3,
      size: Vec3,
      extra: Extra<CavernEntity> = {},
    ): CavernEntity => ({ id: id(name), type: 'cavern', zone, position, size, ...extra }),
    tunnel: (
      name: string,
      path: Vec3[],
      width: number,
      height: number,
      extra: Extra<TunnelEntity> = {},
    ): TunnelEntity => ({ id: id(name), type: 'tunnel', zone, path, width, height, ...extra }),
    mannequin: (name: string, position: Vec3, extra: Extra<MannequinEntity> = {}): MannequinEntity => ({
      id: id(name),
      type: 'mannequin',
      zone,
      position,
      ...extra,
    }),
    landmark: (
      name: string,
      position: Vec3,
      text: string,
      extra: Extra<LandmarkEntity> = {},
    ): LandmarkEntity => ({ id: id(name), type: 'landmark', zone, position, text, ...extra }),
    spawn: (
      name: string,
      position: Vec3,
      label: string,
      extra: Extra<SpawnEntity> = {},
    ): SpawnEntity => ({ id: id(name), type: 'spawn', zone, position, label, ...extra }),
    marker: (
      name: string,
      position: Vec3,
      kind: MarkerEntity['kind'],
      label: string,
      extra: Extra<MarkerEntity> = {},
    ): MarkerEntity => ({ id: id(name), type: 'marker', zone, position, kind, label, ...extra }),
  };
}

/** Rectangular room shell: four walls with named openings. */
export interface RoomOpening {
  side: 'n' | 's' | 'e' | 'w';
  /** World coordinate along the side (X for n/s, Z for e/w). */
  at: number;
  width: number;
  bottom?: number;
  top?: number;
}

export interface RoomSpec {
  /** [minX, minZ] and [maxX, maxZ]. */
  min: Vec2;
  max: Vec2;
  base?: number;
  height: number;
  thickness?: number;
  openings?: RoomOpening[];
}

/**
 * Build the four walls of a rectangular room. Openings are given in world
 * coordinates, which is far easier to keep consistent across zones than
 * distances measured from an arbitrary corner.
 */
export function roomWalls(
  author: ReturnType<typeof zoneAuthor>,
  name: string,
  spec: RoomSpec,
): WallEntity[] {
  const [x0, z0] = spec.min;
  const [x1, z1] = spec.max;
  const base = spec.base ?? 0;
  const thickness = spec.thickness ?? 0.4;
  const gapsFor = (side: RoomOpening['side'], origin: number, sign: number) =>
    (spec.openings ?? [])
      .filter((o) => o.side === side)
      .map((o) => ({
        at: (o.at - origin) * sign,
        width: o.width,
        bottom: o.bottom,
        top: o.top,
      }));

  return [
    author.wall(`${name}.n`, [x0, z0], [x1, z0], spec.height, {
      base,
      thickness,
      gaps: gapsFor('n', x0, 1),
    }),
    author.wall(`${name}.e`, [x1, z0], [x1, z1], spec.height, {
      base,
      thickness,
      gaps: gapsFor('e', z0, 1),
    }),
    author.wall(`${name}.s`, [x1, z1], [x0, z1], spec.height, {
      base,
      thickness,
      gaps: gapsFor('s', x1, -1),
    }),
    author.wall(`${name}.w`, [x0, z1], [x0, z0], spec.height, {
      base,
      thickness,
      gaps: gapsFor('w', z1, -1),
    }),
  ];
}
