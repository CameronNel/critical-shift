/**
 * Collision for the walk camera.
 *
 * Everything the builders produce is reduced to Y-rotated boxes. Ground height
 * is resolved analytically against box tops and blocking is a circle-versus-box
 * push-out. That is enough to evaluate a layout, and it means walking never
 * depends on mesh raycasts — which is what makes it cheap on a phone.
 *
 * Ramps and stairs are emitted as short stepped boxes so the same analytic
 * ground query handles slopes without a special case.
 */

export interface BoxCollider {
  entityId: string;
  /** Centre. */
  cx: number;
  cy: number;
  cz: number;
  /** Half extents in the box's local frame. */
  hx: number;
  hy: number;
  hz: number;
  rotY: number;
  /** Blocks horizontal movement. */
  solid: boolean;
  /** The top face can be stood on. */
  walkable: boolean;
}

const CELL = 8;

export interface GroundHit {
  y: number;
  entityId: string;
}

export class CollisionWorld {
  private readonly cells = new Map<number, number[]>();
  private readonly colliders: BoxCollider[] = [];

  constructor(colliders: BoxCollider[] = []) {
    for (const collider of colliders) this.add(collider);
  }

  get count(): number {
    return this.colliders.length;
  }

  add(collider: BoxCollider): void {
    const index = this.colliders.length;
    this.colliders.push(collider);
    const cos = Math.abs(Math.cos(collider.rotY));
    const sin = Math.abs(Math.sin(collider.rotY));
    const ex = collider.hx * cos + collider.hz * sin;
    const ez = collider.hx * sin + collider.hz * cos;
    const minX = Math.floor((collider.cx - ex) / CELL);
    const maxX = Math.floor((collider.cx + ex) / CELL);
    const minZ = Math.floor((collider.cz - ez) / CELL);
    const maxZ = Math.floor((collider.cz + ez) / CELL);
    for (let x = minX; x <= maxX; x++) {
      for (let z = minZ; z <= maxZ; z++) {
        const key = hash(x, z);
        let bucket = this.cells.get(key);
        if (!bucket) {
          bucket = [];
          this.cells.set(key, bucket);
        }
        bucket.push(index);
      }
    }
  }

  private query(x: number, z: number, radius: number, out: Set<number>): void {
    out.clear();
    const minX = Math.floor((x - radius) / CELL);
    const maxX = Math.floor((x + radius) / CELL);
    const minZ = Math.floor((z - radius) / CELL);
    const maxZ = Math.floor((z + radius) / CELL);
    for (let cx = minX; cx <= maxX; cx++) {
      for (let cz = minZ; cz <= maxZ; cz++) {
        const bucket = this.cells.get(hash(cx, cz));
        if (!bucket) continue;
        for (const index of bucket) out.add(index);
      }
    }
  }

  private readonly scratch = new Set<number>();

  /**
   * Highest walkable surface under (x, z) that is not above `ceiling`.
   * Returns null when there is nothing to stand on.
   */
  groundAt(x: number, z: number, ceiling: number, floorLimit: number): GroundHit | null {
    this.query(x, z, 0.05, this.scratch);
    let best: GroundHit | null = null;
    for (const index of this.scratch) {
      const c = this.colliders[index];
      if (!c.walkable) continue;
      const top = c.cy + c.hy;
      if (top > ceiling || top < floorLimit) continue;
      if (best && top <= best.y) continue;
      if (!containsPoint(c, x, z, 0.02)) continue;
      best = { y: top, entityId: c.entityId };
    }
    return best;
  }

  /**
   * Push a capsule of the given radius out of solid boxes that overlap the
   * body's vertical band. Returns the corrected position.
   */
  resolve(
    x: number,
    z: number,
    radius: number,
    bodyBottom: number,
    bodyTop: number,
  ): { x: number; z: number; hit: boolean } {
    let px = x;
    let pz = z;
    let hit = false;
    // Two passes settle inside corners without an expensive solver.
    for (let pass = 0; pass < 2; pass++) {
      this.query(px, pz, radius, this.scratch);
      for (const index of this.scratch) {
        const c = this.colliders[index];
        if (!c.solid) continue;
        if (c.cy + c.hy <= bodyBottom || c.cy - c.hy >= bodyTop) continue;
        // World -> box local. A box rotated by r maps local (0,0,1) to
        // (sin r, cos r), so the inverse is the transpose below.
        const cos = Math.cos(c.rotY);
        const sin = Math.sin(c.rotY);
        const dx = px - c.cx;
        const dz = pz - c.cz;
        const lx = dx * cos - dz * sin;
        const lz = dx * sin + dz * cos;
        const penX = c.hx + radius - Math.abs(lx);
        const penZ = c.hz + radius - Math.abs(lz);
        if (penX <= 0 || penZ <= 0) continue;
        let nx = lx;
        let nz = lz;
        if (penX < penZ) {
          nx = lx + Math.sign(lx || 1) * penX;
        } else {
          nz = lz + Math.sign(lz || 1) * penZ;
        }
        // Local -> world.
        px = c.cx + nx * cos + nz * sin;
        pz = c.cz - nx * sin + nz * cos;
        hit = true;
      }
    }
    return { x: px, z: pz, hit };
  }
}

function containsPoint(c: BoxCollider, x: number, z: number, margin: number): boolean {
  const cos = Math.cos(c.rotY);
  const sin = Math.sin(c.rotY);
  const dx = x - c.cx;
  const dz = z - c.cz;
  const lx = dx * cos - dz * sin;
  const lz = dx * sin + dz * cos;
  return Math.abs(lx) <= c.hx + margin && Math.abs(lz) <= c.hz + margin;
}

function hash(x: number, z: number): number {
  // Cantor-ish pairing on shifted values; the site never exceeds +/-2048 cells.
  return ((x + 2048) << 13) ^ (z + 2048);
}
