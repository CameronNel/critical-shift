import * as THREE from 'three';
import type { SceneLayers } from '../core/scene';
import { CollisionWorld, type BoxCollider } from '../nav/collision';
import { buildEntity } from './builders';
import { GeoBatch } from './geoBatch';
import { createTextSprite } from './textSprite';
import { LabelManager } from './labels';
import { SHARED, emissiveMaterial, waterMaterial } from './materials';
import type { Entity, FacilityDoc, PipeEntity, Route, SpawnEntity, Zone } from '../facility/schema';

export interface FacilityBuild {
  /** Replaced, not mutated, whenever an entity is rebuilt. */
  collision: CollisionWorld;
  labels: LabelManager;
  /** Entity id -> the object that represents it, for picking and editing. */
  objects: Map<string, THREE.Object3D>;
  entities: Map<string, Entity>;
  /** Kept per entity so a single edit can rebuild without touching the rest. */
  collidersByEntity: Map<string, BoxCollider[]>;
  spawns: SpawnEntity[];
  zones: Map<string, Zone>;
  stats: { entities: number; meshes: number; colliders: number };
}

const DEFAULT_ZONE_COLOR = '#7a8088';

/** Remove everything a previous build added, so the doc can be rebuilt in place. */
export function clearFacility(layers: SceneLayers): void {
  for (const group of Object.values(layers)) {
    for (const child of [...group.children]) {
      if (child.userData.persistent) continue;
      group.remove(child);
      disposeObject(child);
    }
  }
}

function disposeObject(object: THREE.Object3D): void {
  object.traverse((node) => {
    const mesh = node as THREE.Mesh;
    // Materials and unit geometries are shared caches; only merged geometry
    // and sprite materials are owned by the object.
    if (mesh.geometry && mesh.geometry.userData.shared !== true) {
      if (!(mesh.geometry as THREE.BufferGeometry).userData.unit) mesh.geometry.dispose?.();
    }
    if (node instanceof THREE.Sprite) node.material.dispose();
  });
}

function layerFor(layers: SceneLayers, entity: Entity): THREE.Group {
  if (entity.type === 'landmark') return layers.labels;
  if (entity.type === 'marker' || entity.type === 'spawn') return layers.markers;
  if (entity.type === 'mannequin') return layers.scaleRefs;
  if (entity.tags?.includes('roof')) return layers.roofs;
  if (entity.tags?.includes('grade')) return layers.ground;
  return layers.world;
}

/**
 * Tags remain plain facility data, but a few visual semantics deserve a richer
 * browser material than the generic greybox palette. Keeping this translation
 * here means the JSON/GLB object still has one stable semantic identity.
 */
function applySemanticMaterial(object: THREE.Object3D, entity: Entity): void {
  const tags = entity.tags ?? [];
  let material: THREE.Material | null = null;
  if (tags.includes('water')) material = waterMaterial(entity.color ?? '#36d9ff');
  else if (tags.includes('glass')) material = SHARED.glass;
  else if (tags.includes('emissive')) material = emissiveMaterial(entity.color ?? '#55d9f2');
  if (!material) return;

  object.traverse((node) => {
    const mesh = node as THREE.Mesh;
    if (mesh.isMesh) mesh.material = material as THREE.Material;
  });
}

/**
 * Thin pool handrails use pipe geometry for the right silhouette. The generic
 * pipe builder only blocks large industrial pipes, so tagged rail pipes get
 * narrow segment colliders here to stop the walk controller stepping through
 * the visible guardrail into the pool.
 */
function semanticPipeColliders(entity: Entity): BoxCollider[] {
  if (entity.type !== 'pipe' || !entity.tags?.includes('collision-rail')) return [];
  const pipe = entity as PipeEntity;
  const result: BoxCollider[] = [];
  for (let i = 0; i < pipe.path.length - 1; i++) {
    const a = pipe.path[i];
    const b = pipe.path[i + 1];
    const dx = b[0] - a[0];
    const dz = b[2] - a[2];
    const planar = Math.hypot(dx, dz);
    if (planar < 1e-3) continue;
    result.push({
      entityId: entity.id,
      cx: (a[0] + b[0]) / 2,
      cy: (a[1] + b[1]) / 2,
      cz: (a[2] + b[2]) / 2,
      hx: Math.max(pipe.radius, 0.055),
      hy: Math.max(pipe.radius, 0.055),
      hz: planar / 2 + 0.03,
      rotY: Math.atan2(dx, dz),
      solid: true,
      walkable: false,
    });
  }
  return result;
}

/**
 * Carry facility semantics onto every built Three.js node. This is useful for
 * editor picking today, browser/MCP inspection while art-directing the room,
 * and GLTF extras when the geometry is exported for Blender later.
 */
function stampEntityMetadata(object: THREE.Object3D, entity: Entity): void {
  const metadata = {
    entityId: entity.id,
    entityType: entity.type,
    zone: entity.zone,
    semanticLabel: entity.label ?? null,
    semanticTags: entity.tags ?? [],
    semanticNotes: entity.notes ?? null,
  };
  object.name = entity.id;
  Object.assign(object.userData, metadata);
  object.traverse((node) => {
    Object.assign(node.userData, metadata);
  });
}

export function buildFacility(doc: FacilityDoc, layers: SceneLayers): FacilityBuild {
  clearFacility(layers);

  const zones = new Map(doc.zones.map((z) => [z.id as string, z]));
  const objects = new Map<string, THREE.Object3D>();
  const entities = new Map<string, Entity>();
  const collidersByEntity = new Map<string, BoxCollider[]>();
  const spawns: SpawnEntity[] = [];
  const labels = new LabelManager();
  let meshes = 0;

  for (const entity of doc.entities) {
    if (entity.type === 'spawn') spawns.push(entity);
    entities.set(entity.id, entity);
    if (entity.hidden) continue;
    const zoneColor = zones.get(entity.zone)?.color ?? DEFAULT_ZONE_COLOR;
    const built = buildEntity(entity, zoneColor);
    applySemanticMaterial(built.object, entity);
    stampEntityMetadata(built.object, entity);
    built.object.traverse((node) => {
      if ((node as THREE.Mesh).isMesh) meshes++;
      if (node instanceof THREE.Sprite && node.userData.labelKind) {
        labels.add(node, node.userData.labelKind);
      }
    });
    layerFor(layers, entity).add(built.object);
    objects.set(entity.id, built.object);
    collidersByEntity.set(entity.id, [...built.colliders, ...semanticPipeColliders(entity)]);
  }

  for (const zone of doc.zones) {
    const sign = createTextSprite(zone.name, {
      height: 5,
      maxWidth: 26,
      bold: true,
      color: '#0d1014',
      background: zone.color,
      border: 'rgba(255,255,255,0.55)',
    });
    sign.position.set(zone.signAt[0], zone.signAt[1], zone.signAt[2]);
    sign.userData.zoneSign = zone.id;
    labels.add(sign, 'zone');
    layers.labels.add(sign);
  }

  for (const route of doc.routes) {
    const ribbon = buildRoute(route);
    if (ribbon) layers.routes.add(ribbon);
  }

  let colliderCount = 0;
  for (const list of collidersByEntity.values()) colliderCount += list.length;

  return {
    collision: buildCollision(collidersByEntity),
    labels,
    objects,
    entities,
    collidersByEntity,
    spawns,
    zones,
    stats: { entities: doc.entities.length, meshes, colliders: colliderCount },
  };
}

function buildCollision(byEntity: Map<string, BoxCollider[]>): CollisionWorld {
  const all: BoxCollider[] = [];
  for (const list of byEntity.values()) for (const collider of list) all.push(collider);
  return new CollisionWorld(all);
}

/**
 * Rebuild one entity in place after an edit. Much cheaper and far less
 * disruptive than rebuilding the whole facility on every nudge.
 */
export function rebuildEntity(
  build: FacilityBuild,
  layers: SceneLayers,
  entity: Entity,
): void {
  removeBuiltEntity(build, entity.id, false);
  build.entities.set(entity.id, entity);
  if (!entity.hidden) {
    const zoneColor = build.zones.get(entity.zone)?.color ?? DEFAULT_ZONE_COLOR;
    const built = buildEntity(entity, zoneColor);
    applySemanticMaterial(built.object, entity);
    stampEntityMetadata(built.object, entity);
    built.object.traverse((node) => {
      if (node instanceof THREE.Sprite && node.userData.labelKind) {
        build.labels.add(node, node.userData.labelKind);
      }
    });
    layerFor(layers, entity).add(built.object);
    build.objects.set(entity.id, built.object);
    build.collidersByEntity.set(entity.id, [...built.colliders, ...semanticPipeColliders(entity)]);
  }
  build.collision = buildCollision(build.collidersByEntity);
}

/** Drop an entity from the built scene. */
export function removeBuiltEntity(build: FacilityBuild, id: string, refresh = true): void {
  const previous = build.objects.get(id);
  if (previous) {
    previous.parent?.remove(previous);
    disposeObject(previous);
  }
  build.objects.delete(id);
  build.collidersByEntity.delete(id);
  if (refresh) {
    build.entities.delete(id);
    build.collision = buildCollision(build.collidersByEntity);
  }
}

function buildRoute(route: Route): THREE.Object3D | null {
  const batch = new GeoBatch();
  for (let i = 0; i < route.path.length - 1; i++) {
    const a = new THREE.Vector3(...route.path[i]);
    const b = new THREE.Vector3(...route.path[i + 1]);
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const run = Math.hypot(dx, dz);
    const rise = b.y - a.y;
    if (run < 1e-3 && Math.abs(rise) < 1e-3) continue;
    const angle = Math.atan2(dx, dz);
    const steps = Math.max(1, Math.round(Math.max(run / 4, Math.abs(rise) / 0.6)));
    for (let s = 0; s < steps; s++) {
      const t = (s + 0.5) / steps;
      batch.addBox(
        new THREE.Vector3(a.x + dx * t, a.y + rise * t + 0.14, a.z + dz * t),
        new THREE.Vector3(0.85, 0.1, (run / steps) * 1.02 + 0.05),
        angle,
      );
    }
  }
  const material = new THREE.MeshBasicMaterial({
    color: new THREE.Color(route.color),
    transparent: true,
    opacity: 0.75,
  });
  const mesh = batch.build(material, route.id);
  if (!mesh) return null;
  mesh.renderOrder = 5;
  mesh.userData.routeId = route.id;
  return mesh;
}
