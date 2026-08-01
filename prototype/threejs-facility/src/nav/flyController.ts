import * as THREE from 'three';
import { SITE_BOUNDS } from '../core/scene';
import type { InputState } from '../input/inputState';
import { applyLook, horizontalBasis, type NavState } from './navState';

const BASE_SPEED = 14;
const SPRINT_MULTIPLIER = 3.2;

/**
 * Free inspection camera. Ignores collision on purpose: the point is to look
 * at roofs, spans and vertical relationships without fighting the geometry.
 */
export class FlyController {
  private readonly forward = new THREE.Vector3();
  private readonly right = new THREE.Vector3();
  private readonly velocity = new THREE.Vector3();

  update(dt: number, input: InputState, nav: NavState): void {
    const look = input.consumeLook(new THREE.Vector2());
    applyLook(nav, look.x, look.y);

    horizontalBasis(nav.yaw, this.forward, this.right);

    // Flying follows the pitch of the camera so "forward" means where you look.
    const pitchScale = Math.cos(nav.pitch);
    const dir = new THREE.Vector3()
      .addScaledVector(this.forward, input.move.y * pitchScale)
      .addScaledVector(this.right, input.move.x);
    dir.y += input.move.y * Math.sin(nav.pitch);
    dir.y += input.vertical;

    if (dir.lengthSq() > 1) dir.normalize();

    const speed = BASE_SPEED * (input.sprint ? SPRINT_MULTIPLIER : 1);
    this.velocity.copy(dir).multiplyScalar(speed);
    nav.position.addScaledVector(this.velocity, dt);

    nav.position.clamp(SITE_BOUNDS.min, SITE_BOUNDS.max);
  }
}
