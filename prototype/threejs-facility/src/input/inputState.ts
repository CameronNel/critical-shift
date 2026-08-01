import * as THREE from 'three';

/**
 * One input surface shared by every navigation mode. Desktop and touch sources
 * both write here so controllers never need to know where a value came from.
 */
export class InputState {
  /** x = strafe (+right), y = forward (+forward). Length clamped to 1. */
  readonly move = new THREE.Vector2();
  /** Radians accumulated since the last consumeLook(). x = yaw, y = pitch. */
  readonly look = new THREE.Vector2();
  /** -1 down .. +1 up. Fly mode only. */
  vertical = 0;
  sprint = false;
  jump = false;
  /** True while any look input is actively being dragged or pointer-locked. */
  looking = false;

  consumeLook(out: THREE.Vector2): THREE.Vector2 {
    out.copy(this.look);
    this.look.set(0, 0);
    return out;
  }

  clearFrame(): void {
    this.jump = false;
  }

  reset(): void {
    this.move.set(0, 0);
    this.look.set(0, 0);
    this.vertical = 0;
    this.sprint = false;
    this.jump = false;
    this.looking = false;
  }
}
