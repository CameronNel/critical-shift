import * as THREE from 'three';

export const MAX_PITCH = Math.PI / 2 - 0.02;

/**
 * Shared camera state. Walk, fly and map modes all read and write this so
 * switching modes never loses the user's place or facing.
 */
export interface NavState {
  /** Eye position. */
  position: THREE.Vector3;
  yaw: number;
  pitch: number;
}

export function createNavState(position: THREE.Vector3, yaw = 0): NavState {
  return { position: position.clone(), yaw, pitch: 0 };
}

export function applyLook(nav: NavState, deltaYaw: number, deltaPitch: number): void {
  nav.yaw += deltaYaw;
  nav.pitch = THREE.MathUtils.clamp(nav.pitch + deltaPitch, -MAX_PITCH, MAX_PITCH);
}

export function applyToCamera(nav: NavState, camera: THREE.Camera): void {
  camera.position.copy(nav.position);
  camera.quaternion.setFromEuler(new THREE.Euler(nav.pitch, nav.yaw, 0, 'YXZ'));
}

/** Forward and right vectors on the horizontal plane. */
export function horizontalBasis(
  yaw: number,
  forward: THREE.Vector3,
  right: THREE.Vector3,
): void {
  forward.set(-Math.sin(yaw), 0, -Math.cos(yaw));
  right.set(Math.cos(yaw), 0, -Math.sin(yaw));
}
