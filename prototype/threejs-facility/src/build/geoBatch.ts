import * as THREE from 'three';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

/**
 * Accumulates boxes and merges them into a single mesh.
 *
 * Guard rails, sleepers, stair treads and support legs would otherwise be
 * thousands of draw calls. Merging keeps the whole facility comfortably inside
 * a phone's budget while the authored data stays one entity per structure.
 */
export class GeoBatch {
  private readonly parts: THREE.BufferGeometry[] = [];
  private readonly matrix = new THREE.Matrix4();
  private readonly quat = new THREE.Quaternion();
  private readonly euler = new THREE.Euler();

  get isEmpty(): boolean {
    return this.parts.length === 0;
  }

  /** `centre` is the box centre, `size` its full extents. */
  addBox(centre: THREE.Vector3, size: THREE.Vector3, rotationY = 0): this {
    const geometry = new THREE.BoxGeometry(
      Math.max(size.x, 1e-4),
      Math.max(size.y, 1e-4),
      Math.max(size.z, 1e-4),
    );
    this.euler.set(0, rotationY, 0);
    this.quat.setFromEuler(this.euler);
    this.matrix.compose(centre, this.quat, new THREE.Vector3(1, 1, 1));
    geometry.applyMatrix4(this.matrix);
    this.parts.push(geometry);
    return this;
  }

  /** Box spanning from A to B in XZ, with a given width, height and base. */
  addSegment(
    a: THREE.Vector3,
    b: THREE.Vector3,
    width: number,
    height: number,
    yOffset = 0,
  ): this {
    const dx = b.x - a.x;
    const dz = b.z - a.z;
    const length = Math.hypot(dx, dz);
    if (length < 1e-4 && Math.abs(b.y - a.y) < 1e-4) return this;
    const angle = Math.atan2(dx, dz);
    const centre = new THREE.Vector3(
      (a.x + b.x) / 2,
      (a.y + b.y) / 2 + yOffset,
      (a.z + b.z) / 2,
    );
    // Sloped runs are approximated by a longer horizontal box; slopes in this
    // prototype are gentle enough that the visual error is negligible.
    const span = Math.hypot(length, b.y - a.y);
    this.addBox(centre, new THREE.Vector3(width, height, span), angle);
    return this;
  }

  addGeometry(geometry: THREE.BufferGeometry): this {
    this.parts.push(geometry);
    return this;
  }

  build(material: THREE.Material, name = ''): THREE.Mesh | null {
    if (this.parts.length === 0) return null;
    const merged =
      this.parts.length === 1 ? this.parts[0] : mergeGeometries(this.parts, false);
    if (!merged) return null;
    if (this.parts.length > 1) for (const part of this.parts) part.dispose();
    this.parts.length = 0;
    const mesh = new THREE.Mesh(merged, material);
    mesh.name = name;
    return mesh;
  }
}
