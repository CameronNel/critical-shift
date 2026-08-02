import * as THREE from 'three';
import type { CollisionWorld } from './collision';
import { EYE_HEIGHT, WORKER_HEIGHT } from './walkController';

/** Matches the walker, so what fits past a cart is what fits past a person. */
const WALKER_RADIUS = 0.42;
/** A loaded cart does not slide off a nudge. */
const PUSH_THRESHOLD = 0.02;

export interface CartBody {
  id: string;
  object: THREE.Object3D;
  /** Half-extents in the cart's own frame. */
  halfX: number;
  halfZ: number;
  height: number;
  rotY: number;
  x: number;
  y: number;
  z: number;
  pushable: boolean;
}

/** Signed penetration of a circle into a Y-rotated box, and the way out. */
function penetration(
  cart: CartBody,
  px: number,
  pz: number,
  radius: number,
): { depth: number; nx: number; nz: number } | null {
  const cos = Math.cos(cart.rotY);
  const sin = Math.sin(cart.rotY);
  const dx = px - cart.x;
  const dz = pz - cart.z;
  // World -> cart local.
  const lx = dx * cos - dz * sin;
  const lz = dx * sin + dz * cos;

  const clampedX = Math.max(-cart.halfX, Math.min(cart.halfX, lx));
  const clampedZ = Math.max(-cart.halfZ, Math.min(cart.halfZ, lz));
  const offX = lx - clampedX;
  const offZ = lz - clampedZ;
  const distSq = offX * offX + offZ * offZ;

  let nx: number;
  let nz: number;
  let depth: number;
  if (distSq > 1e-9) {
    // Outside the box: push straight out along the nearest-point normal.
    const dist = Math.sqrt(distSq);
    if (dist >= radius) return null;
    depth = radius - dist;
    nx = offX / dist;
    nz = offZ / dist;
  } else {
    // Centre is inside the box: leave by the nearest face.
    const toX = cart.halfX - Math.abs(lx);
    const toZ = cart.halfZ - Math.abs(lz);
    if (toX < toZ) {
      nx = lx >= 0 ? 1 : -1;
      nz = 0;
      depth = toX + radius;
    } else {
      nx = 0;
      nz = lz >= 0 ? 1 : -1;
      depth = toZ + radius;
    }
  }
  // Local -> world.
  return { depth, nx: nx * cos + nz * sin, nz: -nx * sin + nz * cos };
}

/**
 * Carts are the one thing here that moves. They are not simulated — no mass,
 * no momentum, no rolling resistance — they are simply displaced by whoever
 * walks into them, and stopped by the same walls that stop a person. That is
 * enough to answer the only question a layout tool needs to ask about a cart:
 * can you actually get it through there.
 */
export class PushableSystem {
  private readonly carts: CartBody[] = [];

  add(cart: CartBody): void {
    this.carts.push(cart);
    this.place(cart);
  }

  clear(): void {
    this.carts.length = 0;
  }

  get bodies(): readonly CartBody[] {
    return this.carts;
  }

  private place(cart: CartBody): void {
    cart.object.position.set(cart.x, cart.y, cart.z);
    cart.object.rotation.y = cart.rotY;
  }

  /**
   * Would the cart sit clear of the static world here? Tested at the four
   * corners rather than as one circle, because a cart is long and a circle
   * that contains it would never fit down a drift.
   */
  private fits(cart: CartBody, x: number, z: number, world: CollisionWorld): boolean {
    const cos = Math.cos(cart.rotY);
    const sin = Math.sin(cart.rotY);
    const lo = cart.y + 0.35;
    const hi = cart.y + cart.height;
    for (const [ox, oz] of [
      [-cart.halfX, -cart.halfZ],
      [cart.halfX, -cart.halfZ],
      [cart.halfX, cart.halfZ],
      [-cart.halfX, cart.halfZ],
    ] as const) {
      const wx = x + ox * cos + oz * sin;
      const wz = z - ox * sin + oz * cos;
      if (world.resolve(wx, wz, 0.05, lo, hi).hit) return false;
    }
    return true;
  }

  /**
   * Run after the walk step: displace carts the walker has moved into, and
   * push the walker back out of any that could not move.
   */
  update(position: THREE.Vector3, world: CollisionWorld): void {
    const feet = position.y - EYE_HEIGHT;
    for (const cart of this.carts) {
      // Only interact when the walker actually overlaps the cart vertically.
      if (cart.y + cart.height <= feet + 0.2 || cart.y >= feet + WORKER_HEIGHT) continue;

      const hit = penetration(cart, position.x, position.z, WALKER_RADIUS);
      if (!hit || hit.depth <= PUSH_THRESHOLD) continue;

      let moved = false;
      if (cart.pushable) {
        // The cart goes the way the walker is pressing, which is opposite the
        // normal that would push the walker out.
        const nx = cart.x - hit.nx * hit.depth;
        const nz = cart.z - hit.nz * hit.depth;
        if (this.fits(cart, nx, nz, world)) {
          cart.x = nx;
          cart.z = nz;
          const ground = world.groundAt(cart.x, cart.z, cart.y + 0.6, cart.y - 8);
          if (ground) cart.y = ground.y;
          this.place(cart);
          moved = true;
        }
      }
      if (!moved) {
        // Parked, or wedged against something. It becomes a wall.
        position.x += hit.nx * hit.depth;
        position.z += hit.nz * hit.depth;
      }
    }
  }
}
