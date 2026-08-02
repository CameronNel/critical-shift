import * as THREE from 'three';
import type { InputState } from '../input/inputState';
import type { NavState } from './navState';

const MIN_DISTANCE = 24;
const MAX_DISTANCE = 620;
const MIN_POLAR = 0.05;
const MAX_POLAR = 1.42;

/**
 * High-angle site view. It reuses the same input surface as walk and fly, so
 * on a phone the left thumb pans, the right thumb orbits and the ▲/▼ buttons
 * zoom — no separate gesture vocabulary to learn.
 */
export class MapController {
  readonly target = new THREE.Vector3(-10, 0, -2);
  distance = 330;
  azimuth = 0;
  /** Angle from straight down. 0 is plan view. */
  polar = 0.62;

  private readonly forward = new THREE.Vector3();
  private readonly right = new THREE.Vector3();

  /** Pull back just far enough that the whole footprint fits the viewport. */
  frameSite(min: THREE.Vector3, max: THREE.Vector3, camera: THREE.PerspectiveCamera): void {
    this.target.addVectors(min, max).multiplyScalar(0.5);
    this.target.y = 0;
    const halfV = THREE.MathUtils.degToRad(camera.fov) / 2;
    const halfH = Math.atan(Math.tan(halfV) * camera.aspect);
    const width = (max.x - min.x) / 2;
    // The site foreshortens as the view tilts away from plan.
    const depth = ((max.z - min.z) / 2) * Math.max(0.35, Math.cos(this.polar));
    this.distance = THREE.MathUtils.clamp(
      Math.max(width / Math.tan(halfH), depth / Math.tan(halfV)) * 1.18,
      MIN_DISTANCE,
      MAX_DISTANCE,
    );
  }

  update(dt: number, input: InputState, nav: NavState): void {
    const look = input.consumeLook(new THREE.Vector2());
    this.azimuth += look.x;
    this.polar = THREE.MathUtils.clamp(this.polar - look.y, MIN_POLAR, MAX_POLAR);

    // Pan in the plane the user is looking along, scaled by zoom so the map
    // moves by a similar amount on screen at any distance.
    this.forward.set(-Math.sin(this.azimuth), 0, -Math.cos(this.azimuth));
    this.right.set(Math.cos(this.azimuth), 0, -Math.sin(this.azimuth));
    const panSpeed = this.distance * 0.55 * (input.sprint ? 2.5 : 1);
    this.target
      .addScaledVector(this.forward, input.move.y * panSpeed * dt)
      .addScaledVector(this.right, input.move.x * panSpeed * dt);

    if (input.vertical !== 0) {
      this.distance = THREE.MathUtils.clamp(
        this.distance * (1 - input.vertical * dt * 1.1),
        MIN_DISTANCE,
        MAX_DISTANCE,
      );
    }

    const sinPolar = Math.sin(this.polar);
    nav.position.set(
      this.target.x + sinPolar * Math.sin(this.azimuth) * this.distance,
      this.target.y + Math.cos(this.polar) * this.distance,
      this.target.z + sinPolar * Math.cos(this.azimuth) * this.distance,
    );
    nav.yaw = this.azimuth;
    nav.pitch = this.polar - Math.PI / 2;
  }

  /** Wheel and pinch both arrive here as a multiplicative step. */
  zoomBy(factor: number): void {
    this.distance = THREE.MathUtils.clamp(this.distance * factor, MIN_DISTANCE, MAX_DISTANCE);
  }
}
