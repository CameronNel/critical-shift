import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { P } from './palette.js';
import { additive, glow, mat, tint } from './materials.js';
import { TEXEL_METRES, gaugeTexture, stencilTexture } from './textures.js';

/**
 * The modular industrial kit.
 *
 * Everything visible in the room is one of these pieces, tinted and repeated.
 * Two rules make the reuse read as coherent engineering rather than as
 * copy-paste:
 *
 *  1. **World-scale UVs.** `boxUV` projects texture coordinates from the mesh's
 *     own dimensions, so a rivet is the same physical size on a 12 m wall and on
 *     a 0.4 m junction box, and nothing ever needs a bespoke `repeat`.
 *  2. **Everything is bevelled.** A chamfered edge is what catches a worklight,
 *     and it is the single cheapest way to stop a box from reading as a box.
 */

let ctx = {
  visual: null,
  collider: null,
  quality: { bevels: true, shadows: true, detail: 1 },
};

export function configureKit(next) {
  ctx = { ...ctx, ...next, quality: { ...ctx.quality, ...(next.quality || {}) } };
}

export const colliderMaterial = new THREE.MeshBasicMaterial({ visible: false });

/* --------------------------------------------------------------- geometry */

/**
 * Project UVs from the box's own size, in tiles of `TEXEL_METRES`. `offset`
 * shifts the projection so two identical panels do not show the same chip.
 */
export function boxUV(geometry, { tile = TEXEL_METRES, offset = [0, 0] } = {}) {
  const position = geometry.attributes.position;
  const normal = geometry.attributes.normal;
  const uv = new Float32Array(position.count * 2);
  for (let i = 0; i < position.count; i++) {
    const x = position.getX(i), y = position.getY(i), z = position.getZ(i);
    const nx = Math.abs(normal.getX(i)), ny = Math.abs(normal.getY(i)), nz = Math.abs(normal.getZ(i));
    let u, v;
    if (nx >= ny && nx >= nz) { u = z; v = y; }
    else if (ny >= nx && ny >= nz) { u = x; v = z; }
    else { u = x; v = y; }
    uv[i * 2] = u / tile + offset[0];
    uv[i * 2 + 1] = v / tile + offset[1];
  }
  geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  return geometry;
}

const boxCache = new Map();

/** Bevelled box geometry, cached by shape so repeated kit pieces share buffers. */
export function bevelBox(w, h, d, bevel = 0.035, tile = TEXEL_METRES, offset = [0, 0]) {
  const radius = ctx.quality.bevels ? Math.min(bevel, Math.min(w, h, d) * 0.3) : 0;
  const key = `${w}|${h}|${d}|${radius}|${tile}|${offset}`;
  if (boxCache.has(key)) return boxCache.get(key);
  const geometry = radius > 0.002
    ? new RoundedBoxGeometry(w, h, d, 1, radius)
    : new THREE.BoxGeometry(w, h, d);
  boxUV(geometry, { tile, offset });
  boxCache.set(key, geometry);
  return geometry;
}

function place(mesh, { pos = [0, 0, 0], rot = [0, 0, 0], parent = null } = {}) {
  mesh.position.set(pos[0], pos[1], pos[2]);
  mesh.rotation.set(rot[0], rot[1], rot[2]);
  (parent || ctx.visual).add(mesh);
  return mesh;
}

function shade(mesh, { cast = true, receive = true } = {}) {
  mesh.castShadow = ctx.quality.shadows && cast;
  mesh.receiveShadow = ctx.quality.shadows && receive;
  return mesh;
}

/** Register an invisible collision proxy. Always a plain box — the octree wants simple. */
export function collide(w, h, d, { pos = [0, 0, 0], rot = [0, 0, 0] } = {}) {
  const proxy = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), colliderMaterial);
  proxy.position.set(pos[0], pos[1], pos[2]);
  proxy.rotation.set(rot[0], rot[1], rot[2]);
  ctx.collider.add(proxy);
  return proxy;
}

/* ------------------------------------------------------------- primitives */

/** The workhorse. A bevelled, world-UV'd box with optional collision. */
export function box(w, h, d, material, options = {}) {
  const { bevel = 0.035, tile = TEXEL_METRES, uvOffset = [0, 0], solid = false, cast, receive } = options;
  const mesh = new THREE.Mesh(bevelBox(w, h, d, bevel, tile, uvOffset), material);
  shade(mesh, { cast, receive });
  place(mesh, options);
  if (solid) collide(w, h, d, options);
  return mesh;
}

export function cylinder(radius, height, material, options = {}) {
  const { radial = 20, radiusTop = radius, open = false, cast, receive } = options;
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radiusTop, radius, height, radial, 1, open),
    material,
  );
  shade(mesh, { cast, receive });
  return place(mesh, options);
}

export function ring(radius, tube, material, options = {}) {
  const mesh = new THREE.Mesh(new THREE.TorusGeometry(radius, tube, 8, options.radial || 28), material);
  shade(mesh, { cast: false });
  return place(mesh, { rot: [Math.PI / 2, 0, 0], ...options });
}

export function sphere(radius, material, options = {}) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 14, 10), material);
  shade(mesh, { cast: false });
  return place(mesh, options);
}

/* ------------------------------------------------------------ structure */

/**
 * A wall in the plant's two-tone paint scheme: pale green dado below the
 * 1.4 m line, cream above, with a steel capping strip where they meet. One call
 * gives a wall three materials' worth of interest.
 */
export function paintedWall(w, h, d, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const dado = Math.min(1.4, h * 0.45);
  box(w, dado, d, mat('enamelGreen'), { pos: [0, -h / 2 + dado / 2, 0], parent: group, bevel: 0.05, uvOffset: options.uvOffset });
  box(w, h - dado, d, mat('enamelCream'), { pos: [0, -h / 2 + dado + (h - dado) / 2, 0], parent: group, bevel: 0.05, uvOffset: options.uvOffset });
  box(w + 0.02, 0.09, d + 0.03, mat('steel'), { pos: [0, -h / 2 + dado, 0], parent: group, bevel: 0.02 });
  if (options.solid !== false) collide(w, h, d, options);
  return group;
}

/** Structural column with a riveted base plate and cap. */
export function column(height, options = {}) {
  const { radius = 0.17, material = mat('darkSteel') } = options;
  const group = new THREE.Group();
  place(group, options);
  box(radius * 2, height, radius * 2, material, { pos: [0, height / 2, 0], parent: group, bevel: 0.045 });
  for (const y of [0.08, height - 0.08]) {
    box(radius * 3.1, 0.11, radius * 3.1, mat('steel'), { pos: [0, y, 0], parent: group, bevel: 0.02 });
  }
  // Corner gussets: four small triangles read as a welded footing.
  for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    box(0.06, 0.42, 0.3, mat('steel'), {
      pos: [dx * radius * 1.05, 0.34, dz * radius * 1.05],
      rot: [0, dz ? Math.PI / 2 : 0, 0],
      parent: group,
      bevel: 0.015,
    });
  }
  if (options.solid) collide(radius * 2.2, height, radius * 2.2, { pos: [options.pos?.[0] ?? 0, (options.pos?.[1] ?? 0) + height / 2, options.pos?.[2] ?? 0] });
  return group;
}

/** Riveted I-beam, run along X unless rotated. */
export function beam(length, options = {}) {
  const { depth = 0.34, material = mat('darkSteel') } = options;
  const group = new THREE.Group();
  place(group, options);
  box(length, 0.06, depth, material, { pos: [0, depth / 2 - 0.03, 0], parent: group, bevel: 0.012 });
  box(length, 0.06, depth, material, { pos: [0, -depth / 2 + 0.03, 0], parent: group, bevel: 0.012 });
  box(length, depth - 0.1, 0.05, material, { pos: [0, 0, 0], parent: group, bevel: 0.01 });
  return group;
}

/**
 * Guard rail: kickplate, mid rail, top rail, posts. Collision is a single slab
 * so the player is stopped by the rail rather than by its individual bars.
 */
export function handrail(from, to, options = {}) {
  const { y = 0, height = 1.08, material = mat('steel'), kick = true, solid = true } = options;
  const group = new THREE.Group();
  place(group, { parent: options.parent });
  const dx = to[0] - from[0];
  const dz = to[1] - from[1];
  const length = Math.hypot(dx, dz);
  const yaw = Math.atan2(dx, dz);
  group.position.set((from[0] + to[0]) / 2, y, (from[1] + to[1]) / 2);
  group.rotation.y = yaw;
  cylinder(0.032, length, material, { pos: [0, height, 0], rot: [Math.PI / 2, 0, 0], radial: 8, parent: group });
  cylinder(0.024, length, material, { pos: [0, height * 0.55, 0], rot: [Math.PI / 2, 0, 0], radial: 6, parent: group });
  if (kick) box(0.035, 0.13, length, tint('darkSteel', P.hazardDeep), { pos: [0, 0.075, 0], parent: group, bevel: 0.01 });
  const posts = Math.max(2, Math.round(length / 1.25) + 1);
  for (let i = 0; i < posts; i++) {
    const t = posts === 1 ? 0.5 : i / (posts - 1);
    const z = -length / 2 + t * length;
    box(0.055, height, 0.055, material, { pos: [0, height / 2, z], parent: group, bevel: 0.012 });
    sphere(0.038, mat('chrome'), { pos: [0, height + 0.02, z], parent: group });
  }
  if (solid) {
    collide(0.14, height + 0.1, length, { pos: [group.position.x, y + height / 2, group.position.z], rot: [0, yaw, 0] });
  }
  return group;
}

/** Painted hazard trim let into the floor around an opening or a step. */
export function hazardStrip(x, z, w, d, options = {}) {
  return box(w, 0.02, d, mat('hazard'), {
    pos: [x, 0.012, z],
    rot: [0, options.yaw || 0, 0],
    bevel: 0.006,
    tile: 1,
    cast: false,
    ...options,
  });
}

/** Caged wall ladder. Purely decorative here, but it sells the vertical scale. */
export function ladder(height, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  for (const x of [-0.24, 0.24]) {
    box(0.05, height, 0.05, mat('steel'), { pos: [x, height / 2, 0], parent: group, bevel: 0.012 });
  }
  for (let y = 0.3; y < height - 0.1; y += 0.32) {
    cylinder(0.021, 0.48, mat('steel'), { pos: [0, y, 0], rot: [0, 0, Math.PI / 2], radial: 6, parent: group });
  }
  for (let y = 1.9; y < height - 0.3; y += 0.55) {
    const hoop = ring(0.38, 0.022, mat('darkSteel'), { pos: [0, y, 0.26], rot: [0, 0, 0], parent: group, radial: 14 });
    hoop.rotation.set(0, 0, 0);
  }
  return group;
}

/* ------------------------------------------------------------ machinery */

/** Pipe run with flanges at every bend and a hanger where it crosses open air. */
export function pipeRun(points, radius, material = mat('steel'), options = {}) {
  const group = new THREE.Group();
  place(group, { parent: options.parent });
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const tube = new THREE.Mesh(
    new THREE.TubeGeometry(curve, Math.max(16, points.length * 12), radius, options.radial || 12, false),
    material,
  );
  shade(tube, { cast: true, receive: true });
  group.add(tube);
  if (options.flanges !== false) {
    for (let i = 0; i < points.length; i++) {
      const t = i / (points.length - 1);
      const point = curve.getPointAt(THREE.MathUtils.clamp(t, 0.001, 0.999));
      const tangent = curve.getTangentAt(THREE.MathUtils.clamp(t, 0.001, 0.999));
      const flange = cylinder(radius * 1.75, radius * 0.6, mat('steel'), { radial: 14, parent: group });
      flange.position.copy(point);
      flange.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), tangent.normalize());
      const bolts = cylinder(radius * 1.9, radius * 0.22, mat('chrome'), { radial: 14, parent: group });
      bolts.position.copy(point);
      bolts.quaternion.copy(flange.quaternion);
    }
  }
  return group;
}

/** Hand wheel on a valve stem. Returned so the sim can spin it. */
export function valveWheel(radius, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const material = options.material || mat('brass');
  ring(radius, radius * 0.13, material, { parent: group, radial: 22, rot: [0, 0, 0] }).rotation.set(0, 0, 0);
  for (let i = 0; i < 4; i++) {
    box(radius * 1.85, 0.035, 0.05, material, { rot: [0, 0, (i * Math.PI) / 4], parent: group, bevel: 0.012 });
  }
  cylinder(radius * 0.22, 0.14, mat('chrome'), { rot: [Math.PI / 2, 0, 0], parent: group, radial: 12 });
  return group;
}

/** Analogue gauge with a live needle. */
export function gauge(radius, label, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  cylinder(radius, 0.07, mat('chrome'), { rot: [Math.PI / 2, 0, 0], parent: group, radial: 20 });
  const face = new THREE.Mesh(
    new THREE.CircleGeometry(radius * 0.92, 24),
    new THREE.MeshStandardMaterial({ map: gaugeTexture({ label }), roughness: 0.4, metalness: 0.05 }),
  );
  face.position.z = 0.038;
  group.add(face);
  const needle = new THREE.Group();
  box(radius * 0.75, 0.018, 0.012, tint('ink', P.signalRed), { pos: [radius * 0.3, 0, 0], parent: needle, bevel: 0.004 });
  needle.position.z = 0.045;
  group.add(needle);
  group.userData.needle = needle;
  return group;
}

/** Bakelite panel of brass toggles and indicator lamps. */
export function toggleBank(cols, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const width = cols * 0.16 + 0.1;
  box(width, 0.26, 0.05, mat('bakelite'), { parent: group, bevel: 0.015, tile: 0.5 });
  for (let i = 0; i < cols; i++) {
    const x = -width / 2 + 0.09 + i * 0.16;
    cylinder(0.022, 0.05, mat('chrome'), { pos: [x, -0.05, 0.04], rot: [Math.PI / 2, 0, 0], radial: 10, parent: group });
    box(0.022, 0.075, 0.022, mat('brass'), { pos: [x, -0.015, 0.075], rot: [(i % 3) - 1 ? -0.5 : 0.5, 0, 0], parent: group, bevel: 0.006 });
    const lampColour = [P.signalGreen, P.signalAmber, P.signalRed][i % 3];
    sphere(0.026, glow(lampColour, i % 3 === 0 ? 1.6 : 0.5), { pos: [x, 0.075, 0.045], parent: group });
  }
  return group;
}

/** Sodium worklight in a wire cage, with the additive cone that sells it. */
export function workLight(options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const colour = options.colour || P.lampSodium;
  box(0.44, 0.16, 0.44, mat('darkSteel'), { pos: [0, 0.08, 0], parent: group, bevel: 0.03 });
  cylinder(0.3, 0.22, tint('steel', P.enamelCreamDeep), { pos: [0, -0.06, 0], radiusTop: 0.42, radial: 16, parent: group });
  const lens = cylinder(0.27, 0.05, glow(colour, options.on === false ? 0.05 : 5.5), {
    pos: [0, -0.17, 0], radial: 16, parent: group,
  });
  for (let i = 0; i < 4; i++) {
    box(0.02, 0.3, 0.02, mat('steel'), {
      pos: [Math.cos((i * Math.PI) / 2) * 0.26, -0.14, Math.sin((i * Math.PI) / 2) * 0.26],
      parent: group, bevel: 0.005,
    });
  }
  ring(0.27, 0.016, mat('steel'), { pos: [0, -0.28, 0], parent: group, radial: 16 });
  const cone = new THREE.Mesh(new THREE.ConeGeometry(1.5, 3.2, 14, 1, true), additive(colour, 0.055));
  cone.position.y = -1.75;
  cone.rotation.x = Math.PI;
  cone.renderOrder = 3;
  group.add(cone);
  group.userData.lens = lens;
  group.userData.cone = cone;
  return group;
}

/** Wall-mounted enamel sign, bolted on. Every label in the room is one of these. */
export function signPlate(lines, options = {}) {
  const {
    width = 1.6, height = 0.44, bg = P.enamelCream, fg = P.ironBlack, accent = null, bolts = true,
  } = options;
  const group = new THREE.Group();
  place(group, options);
  const texture = stencilTexture(lines, {
    width: 512, height: Math.round((512 * height) / width), bg, fg, accent,
  });
  const plate = new THREE.Mesh(
    new RoundedBoxGeometry(width, height, 0.035, 1, 0.012),
    new THREE.MeshStandardMaterial({ map: texture, roughness: 0.48, metalness: 0.15 }),
  );
  shade(plate, { cast: false });
  group.add(plate);
  if (bolts) {
    for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      cylinder(0.016, 0.02, mat('chrome'), {
        pos: [sx * (width / 2 - 0.045), sy * (height / 2 - 0.045), 0.026],
        rot: [Math.PI / 2, 0, 0], radial: 8, parent: group,
      });
    }
  }
  return group;
}

/**
 * Illuminated indicator plate — the mimic-board style annunciator tiles that
 * cover the back wall of every control room of this era.
 */
export function annunciatorTile(text, colour, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const width = options.width || 0.46;
  const height = options.height || 0.2;
  box(width + 0.03, height + 0.03, 0.05, mat('darkSteel'), { parent: group, bevel: 0.008 });
  const texture = stencilTexture(text, {
    width: 256, height: Math.round((256 * height) / width), bg: '#141a1a', fg: colour, weathered: false,
  });
  const face = new THREE.Mesh(
    new THREE.PlaneGeometry(width, height),
    new THREE.MeshStandardMaterial({
      map: texture, emissiveMap: texture, emissive: 0xffffff, emissiveIntensity: 0.15, roughness: 0.5,
    }),
  );
  face.position.z = 0.028;
  group.add(face);
  group.userData.face = face;
  return group;
}

/** Riveted process tank with dished ends and a level sight glass. */
export function tank(radius, height, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  const material = options.material || mat('steel');
  cylinder(radius, height, material, { parent: group, radial: options.radial || 22 });
  for (const y of [-height / 2, height / 2]) {
    const cap = new THREE.Mesh(new THREE.SphereGeometry(radius, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2), material);
    cap.position.y = y;
    cap.scale.y = 0.42 * (y > 0 ? 1 : -1);
    shade(cap);
    group.add(cap);
  }
  for (const y of [-height * 0.3, height * 0.3]) {
    ring(radius * 1.02, 0.035, mat('darkSteel'), { pos: [0, y, 0], parent: group, radial: 24 });
  }
  if (options.solid) collide(radius * 2, height, radius * 2, options);
  return group;
}

/** Electric motor with cooling fins and a terminal box — dressing for pumps and fans. */
export function motor(radius, length, options = {}) {
  const group = new THREE.Group();
  place(group, options);
  cylinder(radius, length, tint('steel', options.colour || P.enamelGreen), {
    rot: [0, 0, Math.PI / 2], radial: 18, parent: group,
  });
  for (let i = 0; i < 9; i++) {
    ring(radius * 1.04, 0.018, tint('steel', options.colour || P.enamelGreen), {
      pos: [-length / 2 + 0.08 + (i * (length - 0.16)) / 8, 0, 0], rot: [0, 0, Math.PI / 2], parent: group, radial: 18,
    });
  }
  box(radius * 0.7, radius * 0.5, radius * 0.9, mat('darkSteel'), { pos: [0, radius * 0.85, 0], parent: group, bevel: 0.02 });
  cylinder(radius * 1.15, 0.06, mat('darkSteel'), { pos: [length / 2, 0, 0], rot: [0, 0, Math.PI / 2], radial: 18, parent: group });
  return group;
}

/* ------------------------------------------------------------- fuel rods */

/**
 * A fuel assembly. Used three ways — racked, carried in first person, and seated
 * in the pool — so it is built once here with a `heat` parameter that drives its
 * emissive strength.
 */
export function fuelAssembly({ length = 2.4, radius = 0.15, heat = 1 } = {}) {
  const group = new THREE.Group();
  const core = glow(P.fuelHot, 1.4 + heat * 2.6, { roughness: 0.34 });
  const pins = new THREE.Group();
  for (const [dx, dz] of [[0, 0], [0.055, 0.055], [-0.055, 0.055], [0.055, -0.055], [-0.055, -0.055]]) {
    const pin = cylinder(radius * 0.34, length * 0.92, core, { radial: 8, parent: pins });
    pin.position.set(dx, 0, dz);
  }
  group.add(pins);
  // Zircaloy shroud, open at the corners so the glow leaks out.
  for (let i = 0; i < 4; i++) {
    const angle = (i * Math.PI) / 2 + Math.PI / 4;
    box(radius * 1.5, length * 0.9, 0.022, mat('chrome'), {
      pos: [Math.cos(angle) * radius * 0.82, 0, Math.sin(angle) * radius * 0.82],
      rot: [0, -angle + Math.PI / 2, 0],
      parent: group, bevel: 0.006, tile: 0.4,
    });
  }
  for (const y of [-length * 0.3, 0, length * 0.3]) {
    ring(radius * 1.12, 0.018, mat('steel'), { pos: [0, y, 0], parent: group, radial: 14 });
  }
  // Lifting bail and the machined foot that locates it in the lattice.
  cylinder(radius * 1.25, 0.12, mat('darkSteel'), { pos: [0, length / 2 + 0.06, 0], radial: 14, parent: group });
  const bail = ring(0.09, 0.018, mat('steel'), { pos: [0, length / 2 + 0.2, 0], parent: group, radial: 14 });
  bail.rotation.set(0, 0, 0);
  cylinder(radius * 1.1, 0.1, mat('darkSteel'), { pos: [0, -length / 2 - 0.05, 0], radiusTop: radius * 0.8, radial: 14, parent: group });
  group.userData.core = core;
  return group;
}

export { mat, tint, glow, additive };
