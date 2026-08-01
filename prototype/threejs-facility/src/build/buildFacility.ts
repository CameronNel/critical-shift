import * as THREE from 'three';
import type { SceneLayers } from '../core/scene';
import { CollisionWorld, type BoxCollider } from '../nav/collision';
import { buildEntity } from './builders';
import { GeoBatch } from './geoBatch';
import { createTextSprite } from './textSprite';
import type { Entity, FacilityDoc, Route, SpawnEntity, Zone } from '../facility/schema';

export interface FacilityBuild {
  collision: CollisionWorld;
  /** Entity id -> the object that represents it, for picking and editing. */
  objects: Map<string, THREE.Object3D>;
  entities: Map<string, Entity>;
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

export function buildFacility(doc: FacilityDoc, layers: SceneLayers): FacilityBuild {
  clearFacility(layers);

  const zones = new Map(doc.zones.map((z) => [z.id as string, z]));
  const objects = new Map<string, THREE.Object3D>();
  const entities = new Map<string, Entity>();
  const colliders: BoxCollider[] = [];
  const spawns: SpawnEntity[] = [];
  let meshes = 0;

  for (const entity of doc.entities) {
    if (entity.type === 'spawn') spawns.push(entity);
    entities.set(entity.id, entity);
    if (entity.hidden) continue;
    const zoneColor = zones.get(entity.zone)?.color ?? DEFAULT_ZONE_COLOR;
    const built = buildEntity(entity, zoneColor);
    built.object.name = entity.id;
    built.object.userData.entityId = entity.id;
    built.object.userData.zone = entity.zone;
    built.object.traverse((node) => {
      node.userData.entityId = entity.id;
      if ((node as THREE.Mesh).isMesh) meshes++;
    });
    layerFor(layers, entity).add(built.object);
    objects.set(entity.id, built.object);
    for (const collider of built.colliders) colliders.push(collider);
  }

  for (const zone of doc.zones) {
    const sign = createTextSprite(zone.name, {
      height: 5,
      bold: true,
      color: '#0d1014',
      background: zone.color,
      border: 'rgba(255,255,255,0.55)',
    });
    sign.position.set(zone.signAt[0], zone.signAt[1], zone.signAt[2]);
    sign.userData.zoneSign = zone.id;
    sign.userData.isLabel = true;
    layers.labels.add(sign);
  }

  for (const route of doc.routes) {
    const ribbon = buildRoute(route);
    if (ribbon) layers.routes.add(ribbon);
  }

  return {
    collision: new CollisionWorld(colliders),
    objects,
    entities,
    spawns,
    zones,
    stats: { entities: doc.entities.length, meshes, colliders: colliders.length },
  };
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
