import * as THREE from 'three';
import type { InputState } from '../input/inputState';
import type { CollisionWorld } from './collision';
import { applyLook, horizontalBasis, type NavState } from './navState';

/** 1.75 m worker; the camera sits at eye height, not at the crown. */
export const WORKER_HEIGHT = 1.75;
export const EYE_HEIGHT = 1.62;
const RADIUS = 0.42;
const STEP_UP = 0.45;
/** Waist height: anything lower is stepped over rather than blocking. */
const STEP_OVER = 0.4;
/**
 * Nothing in the design documents fixes a movement speed yet, and every travel
 * time in this layout depends on it. These are a starting point, adjustable at
 * runtime so the plan can be judged against a speed rather than an assumption.
 */
export const SPEEDS = {
  walk: 4.2,
  sprint: 7.4,
  /** Multiplier applied to both. 1 = the values above. */
  scale: 1,
};
const ACCEL = 34;
const GRAVITY = -22;
const JUMP = 6.2;
const TERMINAL = -45;

export interface WalkStatus {
  grounded: boolean;
  standingOn: string | null;
  speed: number;
}

/**
 * Deliberately simple first-person walker: enough to judge distances, widths,
 * slopes and sightlines. It is not a character controller for the real game.
 */
export class WalkController {
  private readonly forward = new THREE.Vector3();
  private readonly right = new THREE.Vector3();
  private readonly velocity = new THREE.Vector3();
  private verticalVelocity = 0;
  readonly status: WalkStatus = { grounded: false, standingOn: null, speed: 0 };

  reset(): void {
    this.velocity.set(0, 0, 0);
    this.verticalVelocity = 0;
    this.status.grounded = false;
    this.status.standingOn = null;
  }

  update(dt: number, input: InputState, nav: NavState, world: CollisionWorld): void {
    const look = input.consumeLook(new THREE.Vector2());
    applyLook(nav, look.x, look.y);
    horizontalBasis(nav.yaw, this.forward, this.right);

    const sprinting = input.sprint || input.vertical < 0;
    const target = new THREE.Vector3()
      .addScaledVector(this.forward, input.move.y)
      .addScaledVector(this.right, input.move.x);
    if (target.lengthSq() > 1) target.normalize();
    target.multiplyScalar((sprinting ? SPEEDS.sprint : SPEEDS.walk) * SPEEDS.scale);

    // Simple acceleration so stopping and starting reads naturally on a phone.
    this.velocity.x = THREE.MathUtils.damp(this.velocity.x, target.x, ACCEL * 0.35, dt);
    this.velocity.z = THREE.MathUtils.damp(this.velocity.z, target.z, ACCEL * 0.35, dt);

    let feet = nav.position.y - EYE_HEIGHT;
    let x = nav.position.x + this.velocity.x * dt;
    let z = nav.position.z + this.velocity.z * dt;

    const resolved = world.resolve(x, z, RADIUS, feet + STEP_OVER, feet + WORKER_HEIGHT);
    if (resolved.hit) {
      // Kill the component of velocity that ran into the wall so we slide.
      const dx = resolved.x - x;
      const dz = resolved.z - z;
      const len = Math.hypot(dx, dz);
      if (len > 1e-5) {
        const nx = dx / len;
        const nz = dz / len;
        const into = this.velocity.x * nx + this.velocity.z * nz;
        if (into < 0) {
          this.velocity.x -= nx * into;
          this.velocity.z -= nz * into;
        }
      }
    }
    x = resolved.x;
    z = resolved.z;

    if (input.jump && this.status.grounded) this.verticalVelocity = JUMP;

    this.verticalVelocity = Math.max(TERMINAL, this.verticalVelocity + GRAVITY * dt);
    let nextFeet = feet + this.verticalVelocity * dt;

    const ground = world.groundAt(x, z, feet + STEP_UP, feet - 60);
    if (ground && nextFeet <= ground.y) {
      nextFeet = ground.y;
      this.verticalVelocity = 0;
      this.status.grounded = true;
      this.status.standingOn = ground.entityId;
    } else {
      this.status.grounded = false;
      this.status.standingOn = null;
    }

    feet = nextFeet;
    nav.position.set(x, feet + EYE_HEIGHT, z);
    this.status.speed = Math.hypot(this.velocity.x, this.velocity.z);
  }
}
