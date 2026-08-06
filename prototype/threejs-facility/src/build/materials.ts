import * as THREE from 'three';

/**
 * A deliberately small material vocabulary. Zones are separated by restrained
 * tint, roles by lightness. The reactor visual pass adds only two semantic
 * exceptions: emissive display/core surfaces and transparent reactor water.
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

/** Lit housing/display surface. Cheap: a real light is not implied. */
export function emissiveMaterial(hex: string): THREE.MeshLambertMaterial {
  const existing = emissiveCache.get(hex);
  if (existing) return existing;
  const color = new THREE.Color(hex);
  const material = new THREE.MeshLambertMaterial({
    color: color.clone().multiplyScalar(0.34),
    emissive: color,
    emissiveIntensity: 1.15,
  });
  emissiveCache.set(hex, material);
  return material;
}

const waterCache = new Map<string, THREE.MeshPhysicalMaterial>();

/**
 * Reactor-pool water. This stays intentionally simple enough for phones while
 * giving the deep pool an actual transparent surface instead of an opaque cyan
 * disc. The separate submerged emissive/core objects provide most of the glow.
 */
export function waterMaterial(hex: string): THREE.MeshPhysicalMaterial {
  const existing = waterCache.get(hex);
  if (existing) return existing;
  const color = new THREE.Color(hex);
  const material = new THREE.MeshPhysicalMaterial({
    color: color.clone().multiplyScalar(0.72),
    roughness: 0.14,
    metalness: 0,
    transparent: true,
    opacity: 0.58,
    transmission: 0.18,
    thickness: 0.22,
    ior: 1.33,
    side: THREE.DoubleSide,
    depthWrite: false,
  });
  waterCache.set(hex, material);
  return material;
}

/** Shared, zone-independent materials. Guard rails read the same everywhere. */
export const SHARED = {
  // Keep the established greybox rail colour site-wide. The finished reactor
  // pool rails use explicit stainless colours in reactorVisual.ts instead of
  // silently restyling stairs/catwalks in every other department.
  rail: new THREE.MeshLambertMaterial({ color: 0xc9a23f }),
  steel: new THREE.MeshLambertMaterial({ color: 0x657078 }),
  belt: new THREE.MeshLambertMaterial({ color: 0x3d444b }),
  track: new THREE.MeshLambertMaterial({ color: 0x757d86 }),
  glass: new THREE.MeshPhysicalMaterial({
    color: 0x9fcfe0,
    transparent: true,
    opacity: 0.22,
    roughness: 0.08,
    transmission: 0.26,
    thickness: 0.08,
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
  cylinder: new THREE.CylinderGeometry(0.5, 0.5, 1, 20),
  cone: new THREE.CylinderGeometry(0.08, 0.5, 1, 16),
  hopper: new THREE.CylinderGeometry(0.5, 0.18, 1, 8),
};

export function disposeMaterialCache(): void {
  for (const material of cache.values()) material.dispose();
  cache.clear();
  for (const material of emissiveCache.values()) material.dispose();
  emissiveCache.clear();
  for (const material of waterCache.values()) material.dispose();
  waterCache.clear();
}
