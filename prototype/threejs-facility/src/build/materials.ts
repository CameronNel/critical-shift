import * as THREE from 'three';

/**
 * A deliberately tiny material vocabulary. Zones are separated by restrained
 * tint, roles by lightness. This is orientation, not an art pass.
 */
export type MaterialRole =
  | 'floor'
  | 'wall'
  | 'roof'
  | 'deck'
  | 'machine'
  | 'rock'
  | 'pipe'
  | 'prop';

const ROLE_TINT: Record<MaterialRole, number> = {
  floor: 0.66,
  wall: 0.94,
  roof: 0.8,
  deck: 1.18,
  machine: 0.82,
  rock: 0.9,
  pipe: 1.06,
  prop: 0.74,
};

const cache = new Map<string, THREE.MeshLambertMaterial>();

function tinted(hex: string, factor: number, key: string): THREE.MeshLambertMaterial {
  const existing = cache.get(key);
  if (existing) return existing;
  const color = new THREE.Color(hex);
  const hsl = { h: 0, s: 0, l: 0 };
  color.getHSL(hsl);
  color.setHSL(hsl.h, hsl.s, THREE.MathUtils.clamp(hsl.l * factor, 0.04, 0.92));
  const material = new THREE.MeshLambertMaterial({ color });
  cache.set(key, material);
  return material;
}

export function zoneMaterial(zoneColor: string, role: MaterialRole): THREE.MeshLambertMaterial {
  return tinted(zoneColor, ROLE_TINT[role], `${zoneColor}|${role}`);
}

export function customMaterial(hex: string, role: MaterialRole = 'machine'): THREE.MeshLambertMaterial {
  return tinted(hex, ROLE_TINT[role], `custom|${hex}|${role}`);
}

const emissiveCache = new Map<string, THREE.MeshLambertMaterial>();

/** Lit housing for a fixture. Cheap: no real light is implied. */
export function emissiveMaterial(hex: string): THREE.MeshLambertMaterial {
  const existing = emissiveCache.get(hex);
  if (existing) return existing;
  const color = new THREE.Color(hex);
  const material = new THREE.MeshLambertMaterial({
    color: color.clone().multiplyScalar(0.35),
    emissive: color,
    emissiveIntensity: 1,
  });
  emissiveCache.set(hex, material);
  return material;
}

/** Shared, zone-independent materials. Guard rails read the same everywhere. */
export const SHARED = {
  rail: new THREE.MeshLambertMaterial({ color: 0xc9a23f }),
  steel: new THREE.MeshLambertMaterial({ color: 0x5c646d }),
  belt: new THREE.MeshLambertMaterial({ color: 0x3d444b }),
  track: new THREE.MeshLambertMaterial({ color: 0x757d86 }),
  glass: new THREE.MeshLambertMaterial({
    color: 0xa9d3e6,
    transparent: true,
    opacity: 0.24,
    side: THREE.DoubleSide,
    depthWrite: false,
  }),
  hazard: new THREE.MeshLambertMaterial({ color: 0xd2732f }),
  mannequin: new THREE.MeshLambertMaterial({ color: 0xd7d2c6 }),
  doorway: new THREE.MeshLambertMaterial({ color: 0x9aa7b3 }),
};

/** Unit primitives reused by every builder, so the GPU sees very few buffers. */
export const UNIT = {
  box: new THREE.BoxGeometry(1, 1, 1),
  cylinder: new THREE.CylinderGeometry(0.5, 0.5, 1, 16),
  cone: new THREE.CylinderGeometry(0.08, 0.5, 1, 16),
  hopper: new THREE.CylinderGeometry(0.5, 0.18, 1, 8),
};

export function disposeMaterialCache(): void {
  for (const material of cache.values()) material.dispose();
  cache.clear();
}
