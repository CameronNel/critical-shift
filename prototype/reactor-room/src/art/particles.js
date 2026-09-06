import * as THREE from 'three';
import { P } from './palette.js';
import { softDot } from './textures.js';

/**
 * Air.
 *
 * Two cheap systems, both `Points`, both additive. Dust drifting through the
 * worklight cones is what makes an interior feel like it has volume; steam off
 * the pump skid is what makes a machine feel like it is running. Neither is
 * simulated — they are looping fields, which is all they need to be.
 */

export function createDust(bounds, count) {
  const positions = new Float32Array(count * 3);
  const drift = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * bounds.x;
    positions[i * 3 + 1] = Math.random() * bounds.y;
    positions[i * 3 + 2] = (Math.random() - 0.5) * bounds.z;
    drift[i * 3] = (Math.random() - 0.5) * 0.14;
    drift[i * 3 + 1] = 0.02 + Math.random() * 0.07;
    drift[i * 3 + 2] = (Math.random() - 0.5) * 0.14;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const points = new THREE.Points(geometry, new THREE.PointsMaterial({
    map: softDot(),
    color: new THREE.Color(P.lampSodium),
    size: 0.035,
    sizeAttenuation: true,
    transparent: true,
    opacity: 0.34,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  }));
  points.renderOrder = 7;
  points.frustumCulled = false;

  function update(dt) {
    const attribute = geometry.attributes.position;
    for (let i = 0; i < count; i++) {
      let y = attribute.getY(i) + drift[i * 3 + 1] * dt;
      let x = attribute.getX(i) + drift[i * 3] * dt;
      let z = attribute.getZ(i) + drift[i * 3 + 2] * dt;
      if (y > bounds.y) { y = 0; x = (Math.random() - 0.5) * bounds.x; z = (Math.random() - 0.5) * bounds.z; }
      if (x > bounds.x / 2) x -= bounds.x;
      if (x < -bounds.x / 2) x += bounds.x;
      if (z > bounds.z / 2) z -= bounds.z;
      if (z < -bounds.z / 2) z += bounds.z;
      attribute.setXYZ(i, x, y, z);
    }
    attribute.needsUpdate = true;
  }

  return { points, update };
}

/**
 * A steam plume anchored to a machine. `rate` is 0..1 — a stopped pump makes a
 * lazy wisp, a running one makes a column.
 */
export function createSteam(origin, count = 26, { spread = 0.35, rise = 0.9, colour = '#cfd8d4' } = {}) {
  const positions = new Float32Array(count * 3);
  const life = new Float32Array(count);
  const speed = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    life[i] = Math.random();
    speed[i] = 0.6 + Math.random() * 0.8;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const points = new THREE.Points(geometry, new THREE.PointsMaterial({
    map: softDot(),
    color: new THREE.Color(colour),
    size: 0.5,
    sizeAttenuation: true,
    transparent: true,
    opacity: 0,
    depthWrite: false,
    blending: THREE.NormalBlending,
  }));
  points.renderOrder = 7;
  points.frustumCulled = false;

  let elapsed = 0;
  function update(dt, rate = 0) {
    elapsed += dt;
    const attribute = geometry.attributes.position;
    for (let i = 0; i < count; i++) {
      life[i] += dt * speed[i] * (0.25 + rate * 0.9);
      if (life[i] > 1) life[i] -= 1;
      const t = life[i];
      const wobble = Math.sin(elapsed * 1.6 + i) * spread * t;
      attribute.setXYZ(
        i,
        origin[0] + wobble,
        origin[1] + t * rise * (1 + rate * 1.6),
        origin[2] + Math.cos(elapsed * 1.3 + i * 1.7) * spread * t,
      );
    }
    attribute.needsUpdate = true;
    points.material.opacity = rate * 0.24;
    points.material.size = 0.34 + rate * 0.5;
  }

  return { points, update };
}
