import * as THREE from 'three';
import { P } from './palette.js';
import { surface } from './textures.js';

/**
 * Material families.
 *
 * The room is deliberately built from a *small* set of shared materials, in line
 * with the project's art direction: a handful of surface families, dressed
 * differently by geometry rather than by unique texture work. Anything that
 * needs to be its own colour is a tint of one of these, not a new map.
 */

const built = new Map();

/**
 * Quality tier, set once at boot. Mobile keeps the albedo and roughness maps —
 * they carry the hand-painted look — and drops only the normal maps, which are
 * the expensive part and the least missed on a small screen.
 */
let quality = { normalMaps: true, anisotropy: 8 };

export function setMaterialQuality(next) {
  quality = { ...quality, ...next };
}

function textured(family, { color = 0xffffff, roughness = 1, metalness = 0, normalScale = 1, ...rest } = {}) {
  const { map, normalMap, roughnessMap } = surface(family);
  map.anisotropy = quality.anisotropy;
  const material = new THREE.MeshStandardMaterial({
    map,
    normalMap: quality.normalMaps ? normalMap : null,
    roughnessMap,
    color,
    roughness,
    metalness,
    ...rest,
  });
  material.normalScale = new THREE.Vector2(normalScale, normalScale);
  return material;
}

/** Named material, built once. */
export function mat(name) {
  if (!built.has(name)) built.set(name, RECIPES[name]());
  return built.get(name);
}

/**
 * A tinted clone of an existing family. Used for the dozens of machine shells
 * that should read as "the same steel, painted a different colour" rather than
 * as separate assets.
 */
export function tint(name, colour, overrides = {}) {
  const key = `${name}:${colour}:${JSON.stringify(overrides)}`;
  if (!built.has(key)) {
    const base = mat(name).clone();
    base.color = new THREE.Color(colour);
    Object.assign(base, overrides);
    built.set(key, base);
  }
  return built.get(key);
}

/** Emissive signal material — lamps, indicators, mimic-board segments. */
export function glow(colour, intensity = 2.2, { roughness = 0.4 } = {}) {
  const key = `glow:${colour}:${intensity}:${roughness}`;
  if (!built.has(key)) {
    built.set(key, new THREE.MeshStandardMaterial({
      color: colour,
      emissive: colour,
      emissiveIntensity: intensity,
      roughness,
      metalness: 0.1,
      toneMapped: true,
    }));
  }
  return built.get(key);
}

const RECIPES = {
  concrete: () => textured('concrete', { roughness: 1, metalness: 0, normalScale: 1.1 }),
  concreteDark: () => textured('concrete', { color: 0x8a8378, roughness: 1, normalScale: 1.1 }),
  screed: () => textured('screed', { roughness: 0.94, metalness: 0.02 }),
  enamelCream: () => textured('enamelCream', { roughness: 0.55, metalness: 0.12, normalScale: 0.9 }),
  enamelGreen: () => textured('enamelGreen', { roughness: 0.55, metalness: 0.12, normalScale: 0.9 }),
  steel: () => textured('steel', { roughness: 0.6, metalness: 0.68, normalScale: 1.15 }),
  darkSteel: () => textured('darkSteel', { roughness: 0.72, metalness: 0.6, normalScale: 1.1 }),
  tread: () => textured('tread', { roughness: 0.78, metalness: 0.5, normalScale: 1.35 }),
  // Knocked back off full value: at full strength the trim reads as fresh
  // road paint rather than as something that has been walked on for years.
  hazard: () => textured('hazard', { color: 0xb2ada2, roughness: 0.7, metalness: 0.12 }),
  bakelite: () => textured('bakelite', { roughness: 0.34, metalness: 0.05, normalScale: 0.5 }),
  liner: () => textured('liner', { roughness: 0.28, metalness: 0.72, normalScale: 1.2 }),
  graphite: () => textured('graphite', { roughness: 0.86, metalness: 0.1 }),

  // Untextured trim. Small parts where a map would only add cost.
  chrome: () => new THREE.MeshStandardMaterial({ color: P.chrome, roughness: 0.18, metalness: 0.95 }),
  brass: () => new THREE.MeshStandardMaterial({ color: P.brass, roughness: 0.3, metalness: 0.9 }),
  brassDark: () => new THREE.MeshStandardMaterial({ color: P.brassDeep, roughness: 0.44, metalness: 0.85 }),
  copper: () => new THREE.MeshStandardMaterial({ color: P.copper, roughness: 0.34, metalness: 0.88 }),
  rubber: () => new THREE.MeshStandardMaterial({ color: P.rubber, roughness: 0.98, metalness: 0 }),
  ink: () => new THREE.MeshStandardMaterial({ color: P.ironBlack, roughness: 0.8, metalness: 0.15 }),

  /**
    * Booth glazing. Deliberately *not* a transmission material: transmission
    * costs an extra scene render, and the one thing this window must do is let
    * the operator see the pool clearly.
    */
  glass: () => new THREE.MeshStandardMaterial({
    color: 0xdae8e4,
    transparent: true,
    opacity: 0.07,
    roughness: 0.09,
    // Almost no metalness and a damped environment: at glancing incidence a
    // shinier pane threw a white sheet across both edges of the booth view.
    metalness: 0.04,
    envMapIntensity: 0.3,
    side: THREE.DoubleSide,
    depthWrite: false,
  }),

  /** Gauge and dial glass — cheap, no transmission, just a sheen. */
  dialGlass: () => new THREE.MeshStandardMaterial({
    color: 0xdff0ef, transparent: true, opacity: 0.2, roughness: 0.05, metalness: 0.5, depthWrite: false,
  }),
};

/** Additive material for light shafts, glow columns and steam. Never lit, never shadowed. */
export function additive(colour, opacity = 0.3) {
  const key = `add:${colour}:${opacity}`;
  if (!built.has(key)) {
    built.set(key, new THREE.MeshBasicMaterial({
      color: colour,
      transparent: true,
      opacity,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
    }));
  }
  return built.get(key);
}

export { P };
