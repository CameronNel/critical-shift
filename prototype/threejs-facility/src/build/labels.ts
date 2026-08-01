import * as THREE from 'three';

export type LabelKind = 'zone' | 'plate' | 'marker';

interface Tuning {
  /** Beyond this distance the label is hidden entirely. */
  maxDistance: number;
  /** Scale with distance to hold a roughly constant screen size. */
  scaleWithDistance: boolean;
  minHeight: number;
  maxHeight: number;
}

const TUNING: Record<LabelKind, Tuning> = {
  zone: { maxDistance: 700, scaleWithDistance: true, minHeight: 2.6, maxHeight: 11 },
  plate: { maxDistance: 70, scaleWithDistance: false, minHeight: 0, maxHeight: 0 },
  marker: { maxDistance: 34, scaleWithDistance: false, minHeight: 0, maxHeight: 0 },
};

/**
 * Sprites do not care how close the camera is, so a room-sized machine plate
 * ends up filling the screen from a metre away and a zone sign is unreadable
 * from the far side of the site. This keeps both usable: labels fade out past
 * a sensible range, and zone signs hold a roughly constant apparent size.
 */
export class LabelManager {
  private readonly sprites: THREE.Sprite[] = [];
  private readonly cameraPosition = new THREE.Vector3();

  add(sprite: THREE.Sprite, kind: LabelKind): void {
    sprite.userData.isLabel = true;
    sprite.userData.labelKind = kind;
    this.sprites.push(sprite);
  }

  get count(): number {
    return this.sprites.length;
  }

  update(camera: THREE.Camera, labelsVisible: boolean): void {
    if (!labelsVisible) return;
    camera.getWorldPosition(this.cameraPosition);
    for (const sprite of this.sprites) {
      const kind = sprite.userData.labelKind as LabelKind;
      const tuning = TUNING[kind];
      const distance = this.cameraPosition.distanceTo(sprite.position);
      sprite.visible = distance <= tuning.maxDistance;
      if (!sprite.visible || !tuning.scaleWithDistance) continue;
      const aspect = (sprite.userData.aspect as number) ?? 4;
      const height = THREE.MathUtils.clamp(
        distance * 0.034,
        tuning.minHeight,
        tuning.maxHeight,
      );
      sprite.scale.set(height * aspect, height, 1);
    }
  }
}
