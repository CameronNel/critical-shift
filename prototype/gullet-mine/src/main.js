import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

const coarse = matchMedia('(pointer: coarse)').matches;
const $ = id => document.getElementById(id);
const clamp = THREE.MathUtils.clamp;
const V = THREE.Vector3;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x121f21);
scene.fog = new THREE.Fog(0x142325, 18, 96);

const camera = new THREE.PerspectiveCamera(coarse ? 67 : 70, innerWidth / innerHeight, .05, 220);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 1.6));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = coarse ? 1.34 : 1.28;
// No shadow maps: an enclosed drift lit by lanterns gets its form from the
// falloff of a few practical lights, and the budget is better spent on
// texture and geometry that survive on a phone.
renderer.shadowMap.enabled = false;
document.body.prepend(renderer.domElement);

// `visual` is merged into a handful of draw calls once building is finished.
// `dynamic` is everything the blasting loop creates at runtime and has to stay
// individually addressable: drill holes, charges, alcoves, muck, ore.
const visual = new THREE.Group();
const dynamic = new THREE.Group();
const colliderRoot = new THREE.Group();
const colliderMaterial = new THREE.MeshBasicMaterial({ visible: false });
scene.add(visual, dynamic);

/* ------------------------------------------------------------------ *
 * Surfaces
 *
 * Every texture is painted once into a canvas and tiled in *metres*: the
 * UVs of each primitive are rescaled by its real size, so a sleeper and a
 * roof beam carved from the same timber read at the same grain.
 * ------------------------------------------------------------------ */
const TILE = 2.4;

function tiled(ctx, size, paint) {
  // Draw each element nine times so strokes that run off an edge come back
  // on the opposite one and the tile joins without a visible seam.
  for (const ox of [-size, 0, size]) for (const oy of [-size, 0, size]) {
    ctx.save(); ctx.translate(ox, oy); paint(ctx); ctx.restore();
  }
}
function canvasTexture(size, painter) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  painter(canvas.getContext('2d'), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}
function bumpTexture(size, painter) {
  const texture = canvasTexture(size, painter);
  texture.colorSpace = THREE.NoColorSpace;
  return texture;
}

function paintRock(ctx, s, palette) {
  const g = ctx.createLinearGradient(0, 0, s * .6, s);
  g.addColorStop(0, palette[0]); g.addColorStop(.5, palette[1]); g.addColorStop(1, palette[2]);
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  // Broad blotches first, so the surface has variation larger than the detail.
  tiled(ctx, s, c => {
    for (let i = 0; i < 9; i++) {
      c.fillStyle = i % 2 ? 'rgba(126, 138, 126, .16)' : 'rgba(38, 50, 48, .18)';
      c.beginPath(); c.ellipse((i * 121) % s, (i * 167) % s, 60 + (i % 3) * 34, 40 + (i % 4) * 26, i * .8, 0, Math.PI * 2); c.fill();
    }
  });
  // Bedding planes: the rock was laid down in layers before anyone cut it.
  tiled(ctx, s, c => {
    for (let i = 0; i < 7; i++) {
      c.strokeStyle = `rgba(20, 32, 30, ${.10 + (i % 3) * .04})`; c.lineWidth = 3 + (i % 3) * 3;
      c.beginPath(); c.moveTo(-20, i * 74 + 12);
      for (let x = -20; x <= s + 20; x += 46) c.lineTo(x, i * 74 + 12 + Math.sin(x * .021 + i) * 9);
      c.stroke();
    }
  });
  // Fractures and drill scars, the marks of the working itself.
  tiled(ctx, s, c => {
    for (let i = 0; i < 13; i++) {
      c.strokeStyle = `rgba(11, 22, 22, ${.18 + (i % 4) * .05})`; c.lineWidth = 1 + (i % 2);
      c.beginPath(); let x = (i * 91) % s, y = (i * 137) % s; c.moveTo(x, y);
      for (let j = 0; j < 4; j++) { x += 18 + (i * 7 + j * 23) % 44; y += ((i + j) % 3 - 1) * 26; c.lineTo(x, y); }
      c.stroke();
    }
  });
  tiled(ctx, s, c => {
    for (let i = 0; i < 26; i++) {
      c.fillStyle = `rgba(${palette[3]}, ${.05 + (i % 5) * .022})`;
      c.beginPath(); c.ellipse((i * 103) % s, (i * 61) % s, 13 + (i % 4) * 9, 5 + (i % 3) * 4, i * .5, 0, Math.PI * 2); c.fill();
    }
  });
}

const rockTexture = canvasTexture(512, (ctx, s) => paintRock(ctx, s, ['#8d8f85', '#6a6f68', '#4d5450', '222, 228, 216']));
const rockBump = bumpTexture(512, (ctx, s) => {
  ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 22; i++) {
      c.strokeStyle = i % 2 ? 'rgba(255,255,255,.30)' : 'rgba(0,0,0,.34)'; c.lineWidth = 3 + (i % 4) * 2;
      c.beginPath(); let x = (i * 77) % s, y = (i * 121) % s; c.moveTo(x, y);
      for (let j = 0; j < 5; j++) { x += 22 + (i * 11 + j * 19) % 48; y += ((i + j) % 3 - 1) * 20; c.lineTo(x, y); }
      c.stroke();
    }
  });
});
// Spoil underfoot: crushed rock trodden into mud, deliberately free of any
// long directional stroke — an earlier pass looked like floorboards.
const earthTexture = canvasTexture(512, (ctx, s) => {
  ctx.fillStyle = '#585448'; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 16; i++) {
      c.fillStyle = i % 2 ? 'rgba(96, 90, 74, .11)' : 'rgba(44, 42, 35, .12)';
      c.beginPath(); c.ellipse((i * 137) % s, (i * 101) % s, 22 + (i % 4) * 14, 17 + (i % 3) * 11, i, 0, Math.PI * 2); c.fill();
    }
    for (let i = 0; i < 190; i++) {
      const x = (i * 79 + (i % 7) * 13) % s, y = (i * 151 + (i % 5) * 29) % s, r = 2 + (i % 6) * 1.7;
      c.fillStyle = `rgba(${118 + i % 6 * 11}, ${116 + i % 5 * 10}, ${99 + i % 4 * 9}, ${.26 + (i % 3) * .12})`;
      c.beginPath(); c.ellipse(x, y, r, r * .74, i * .6, 0, Math.PI * 2); c.fill();
      c.fillStyle = 'rgba(26, 24, 20, .26)';
      c.beginPath(); c.ellipse(x + r * .35, y + r * .4, r * .7, r * .5, i * .6, 0, Math.PI * 2); c.fill();
    }
  });
});
const woodTexture = canvasTexture(512, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, 0);
  g.addColorStop(0, '#8c6a4a'); g.addColorStop(.42, '#6d4f37'); g.addColorStop(1, '#967552');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 26; i++) {
      c.strokeStyle = `rgba(42, 27, 17, ${.20 + i % 3 * .07})`; c.lineWidth = 1 + i % 3;
      c.beginPath(); c.moveTo(-10, i * 21 + 5);
      c.bezierCurveTo(s * .3, i * 21 - 7, s * .7, i * 21 + 12, s + 10, i * 21 + 3); c.stroke();
    }
    for (let i = 0; i < 6; i++) {
      c.strokeStyle = 'rgba(30, 18, 11, .34)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo((i * 97) % s, (i * 71) % s); c.lineTo((i * 97) % s + 3, ((i * 71) % s) + 70); c.stroke();
    }
  });
});
const woodBump = bumpTexture(256, (ctx, s) => {
  ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 22; i++) {
      c.strokeStyle = i % 2 ? 'rgba(255,255,255,.28)' : 'rgba(0,0,0,.30)'; c.lineWidth = 1 + i % 3;
      c.beginPath(); c.moveTo(-10, i * 12 + 3); c.bezierCurveTo(s * .3, i * 12 - 4, s * .7, i * 12 + 7, s + 10, i * 12 + 2); c.stroke();
    }
  });
});
const metalTexture = canvasTexture(256, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, s);
  g.addColorStop(0, '#8d968f'); g.addColorStop(.5, '#5d6866'); g.addColorStop(1, '#3b4645');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 26; i++) { c.strokeStyle = `rgba(228, 208, 160, ${.05 + i % 3 * .03})`; c.lineWidth = 1; c.beginPath(); c.moveTo(i * 15, -6); c.lineTo(i * 15 + 14, s + 6); c.stroke(); }
    for (let i = 0; i < 16; i++) { c.fillStyle = `rgba(126, 74, 42, ${.10 + i % 4 * .04})`; c.beginPath(); c.ellipse((i * 83) % s, (i * 47) % s, 7 + i % 4 * 5, 5 + i % 3 * 4, i, 0, Math.PI * 2); c.fill(); }
  });
});

/**
 * Rescale a primitive's UVs so the texture tiles in metres rather than once
 * per face. This is the single change that makes the shared timber, iron and
 * rock materials read as materials instead of flat colour.
 */
function worldUvBox(geometry, w, h, d, tile = TILE) {
  const uv = geometry.attributes.uv;
  const spans = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]]; // +x -x +y -y +z -z
  for (let face = 0; face < 6; face++) {
    const [su, sv] = spans[face];
    for (let i = face * 4; i < face * 4 + 4; i++) uv.setXY(i, uv.getX(i) * su / tile, uv.getY(i) * sv / tile);
  }
  uv.needsUpdate = true;
  return geometry;
}
function worldUvCylinder(geometry, radius, height, tile = TILE) {
  const uv = geometry.attributes.uv;
  const su = 2 * Math.PI * radius / tile, sv = height / tile;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * su, uv.getY(i) * sv);
  uv.needsUpdate = true;
  return geometry;
}

const mats = {
  cave: new THREE.MeshStandardMaterial({ map: rockTexture, bumpMap: rockBump, bumpScale: .8, color: 0xa8ada2, roughness: .97, side: THREE.BackSide, vertexColors: true }),
  capRock: new THREE.MeshStandardMaterial({ map: rockTexture, bumpMap: rockBump, bumpScale: .8, color: 0x4e544f, roughness: 1, side: THREE.DoubleSide }),
  rock: new THREE.MeshStandardMaterial({ map: rockTexture, bumpMap: rockBump, bumpScale: .5, color: 0x9ba096, roughness: .96 }),
  darkRock: new THREE.MeshStandardMaterial({ map: rockTexture, bumpMap: rockBump, bumpScale: .7, color: 0x59605c, roughness: 1 }),
  matrix: new THREE.MeshStandardMaterial({ map: rockTexture, bumpMap: rockBump, bumpScale: .7, color: 0x554a3c, roughness: 1 }),
  earth: new THREE.MeshStandardMaterial({ map: earthTexture, color: 0x9a9179, roughness: 1 }),
  wood: new THREE.MeshStandardMaterial({ map: woodTexture, bumpMap: woodBump, bumpScale: .35, color: 0x9d8a6d, roughness: .9 }),
  woodDark: new THREE.MeshStandardMaterial({ map: woodTexture, bumpMap: woodBump, bumpScale: .4, color: 0x6b5a45, roughness: .96 }),
  metal: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x6f7973, metalness: .5, roughness: .52 }),
  railHead: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x9aa29c, metalness: .78, roughness: .3 }),
  ironDark: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x333c3b, metalness: .3, roughness: .6 }),
  rope: new THREE.MeshStandardMaterial({ color: 0x8a7048, roughness: 1 }),
  gold: new THREE.MeshStandardMaterial({ color: 0xd8a24a, metalness: .55, roughness: .34 }),
  red: new THREE.MeshStandardMaterial({ color: 0x9c4433, roughness: .84 }),
  // Ore reads as mineral crust, not neon: colour plus a low emissive lift, so
  // a lantern still has to find it rather than the seam lighting the room.
  GLIMMER: new THREE.MeshStandardMaterial({ color: 0x24564d, emissive: 0x071a17, emissiveIntensity: .16, roughness: .44, metalness: .2 }),
  IRON: new THREE.MeshStandardMaterial({ color: 0x554034, emissive: 0x0d0805, emissiveIntensity: .1, roughness: .6, metalness: .32 }),
  COPPER: new THREE.MeshStandardMaterial({ color: 0x3d5548, emissive: 0x08150f, emissiveIntensity: .12, roughness: .52, metalness: .26 }),
  water: new THREE.MeshStandardMaterial({ color: 0x1d4d4e, roughness: .16, metalness: .3, transparent: true, opacity: .78 }),
  black: new THREE.MeshBasicMaterial({ color: 0x05100f }),
  chalk: new THREE.MeshBasicMaterial({ color: 0xb8ad8c }),
  fuse: new THREE.MeshBasicMaterial({ color: 0xc79a4e }),
  paper: new THREE.MeshStandardMaterial({ color: 0xa89468, roughness: 1 }),
};

/* ---------------------------------------------------------- primitives */
function box(w, h, d, mat, x = 0, y = 0, z = 0, ry = 0, rz = 0, rx = 0, parent = visual) {
  const mesh = new THREE.Mesh(worldUvBox(new THREE.BoxGeometry(w, h, d), w, h, d), mat);
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); parent.add(mesh); return mesh;
}
function cyl(rt, rb, h, segments, mat, x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, parent = visual) {
  const mesh = new THREE.Mesh(worldUvCylinder(new THREE.CylinderGeometry(rt, rb, h, segments), Math.max(rt, rb), h), mat);
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); parent.add(mesh); return mesh;
}
function beamBetween(a, b, radius, mat, parent = visual) {
  const direction = new V().subVectors(b, a), length = direction.length();
  const mesh = new THREE.Mesh(worldUvCylinder(new THREE.CylinderGeometry(radius, radius * 1.06, length, 8), radius, length), mat);
  mesh.position.copy(a).add(b).multiplyScalar(.5);
  mesh.quaternion.setFromUnitVectors(new V(0, 1, 0), direction.normalize());
  parent.add(mesh); return mesh;
}
function colliderBox(w, h, d, x, y, z, ry = 0, rz = 0, rx = 0) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), colliderMaterial);
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); colliderRoot.add(mesh); return mesh;
}

function signTexture(text, sub = '', accent = '#e9b35a') {
  const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 170; const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#3a2b20'; ctx.fillRect(0, 0, 512, 170);
  ctx.strokeStyle = accent; ctx.lineWidth = 7; ctx.strokeRect(10, 10, 492, 150);
  ctx.fillStyle = accent; ctx.font = 'bold 44px Georgia'; ctx.textAlign = 'center'; ctx.fillText(text, 256, 79);
  ctx.fillStyle = '#e4d0a4'; ctx.font = '19px system-ui'; ctx.fillText(sub, 256, 119);
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace; return texture;
}
function signBoard(text, sub, accent = '#e9b35a', scale = 1, parent = visual) {
  const g = new THREE.Group();
  box(1.75 * scale, .62 * scale, .09, mats.woodDark, 0, 0, 0, 0, 0, 0, g);
  const label = new THREE.Mesh(new THREE.PlaneGeometry(1.58 * scale, .52 * scale),
    new THREE.MeshBasicMaterial({ map: signTexture(text, sub, accent) }));
  label.position.z = .051; g.add(label); parent.add(g); return g;
}

/* ------------------------------------------------------------------ *
 * The route
 *
 * One spline through seven authored rooms, deliberately compact: about 80 m
 * end to end with no long empty runs between beats. Every wall, floor,
 * collider, rail, timber set, lamp and sign below is placed from this curve
 * rather than from hand-typed coordinates.
 * ------------------------------------------------------------------ */
const NODES = [
  { x: 0, z: 21, w: 3.5, h: 4.3 },      // portal back to the plant
  { x: 0, z: 16, w: 3.4, h: 4.2 },      // Maw Camp
  { x: 0, z: 11, w: 2.9, h: 3.7 },
  { x: 0, z: 6, w: 2.7, h: 3.5 },       // Crooked Rail
  { x: 0, z: 1, w: 2.8, h: 3.6 },
  { x: 0, z: -4, w: 3.6, h: 4.7 },
  { x: 0, z: -10, w: 4.0, h: 5.4 },     // Blackshaft
  { x: 0, z: -16, w: 3.7, h: 4.7 },
  { x: 2.5, z: -21, w: 3.8, h: 4.5 },
  { x: 5.5, z: -26, w: 4.1, h: 4.6 },   // Drowned Pocket
  { x: 5.5, z: -32, w: 4.1, h: 4.6 },
  { x: 3.5, z: -38, w: 4.0, h: 4.4 },   // Saint Glimmer
  { x: .5, z: -44, w: 3.3, h: 4.0 },    // Powderworks
  { x: -2.5, z: -49, w: 3.4, h: 4.1 },
  { x: -6, z: -54, w: 3.8, h: 4.3 },    // Foreman's Vault
  { x: -7, z: -60, w: 3.9, h: 4.3 },
];
const pathCurve = new THREE.CatmullRomCurve3(NODES.map(n => new V(n.x, 0, n.z)), false, 'catmullrom', .32);
const widths = NODES.map(n => n.w), heights = NODES.map(n => n.h);
function profile(t, list) {
  const q = clamp(t, 0, 1) * (list.length - 1), i = Math.min(Math.floor(q), list.length - 2), f = q - i;
  return THREE.MathUtils.lerp(list[i], list[i + 1], f);
}

// Blackshaft and the sump are holes in the floor, so both the rendered invert
// and the floor colliders have to know about them. The sump is kept shallow
// enough to jump out of, so falling in is a nuisance and not a trap.
const SHAFT = { z0: -6.4, z1: -13.6 };
const SUMP = { z0: -22.4, z1: -35.4 };
const SUMP_DEPTH = .72, WATER_Y = -.3;
const inShaftZ = z => z < SHAFT.z0 && z > SHAFT.z1;
const inSumpZ = z => z < SUMP.z0 && z > SUMP.z1;
/** How far the rock invert drops below the walking surface. */
function invertAt(z) {
  if (!inSumpZ(z)) return .34;
  const edge = Math.min(Math.abs(z - SUMP.z0), Math.abs(z - SUMP.z1));
  return .34 + clamp(edge / 2.6, 0, 1) * (SUMP_DEPTH - .34);
}

const SEGMENTS = 176;
const stations = [];
for (let i = 0; i <= SEGMENTS; i++) {
  const t = i / SEGMENTS;
  const p = pathCurve.getPointAt(t);
  const tangent = pathCurve.getTangentAt(t).setY(0).normalize();
  stations.push({
    index: i, t, p, tangent,
    side: new V(-tangent.z, 0, tangent.x),
    width: profile(t, widths),
    height: profile(t, heights),
    yaw: Math.atan2(tangent.x, tangent.z),
  });
}
/** Nearest station to a z along the route. The route never doubles back. */
function stationAtZ(z) {
  let best = stations[0], bestD = Infinity;
  for (const s of stations) { const d = Math.abs(s.p.z - z); if (d < bestD) { bestD = d; best = s; } }
  return best;
}

/**
 * Cross-section of the drift: flat invert, near-vertical ribs, arched back.
 * `n` below 1 squares the ellipse off into the horseshoe a drill-and-blast
 * heading actually leaves behind.
 */
const SECTION_N = .62;
function section(a, width, height, invert) {
  const c = Math.cos(a), s = Math.sin(a);
  const uNorm = Math.sign(c) * Math.abs(c) ** SECTION_N;
  const y = s >= 0
    ? height * Math.abs(s) ** SECTION_N
    : -invert * (1 - Math.abs(uNorm) ** 3);
  return { u: width * uNorm, y, uNorm };
}
/** Ceiling height directly above a lateral offset, used to size timber sets. */
function crownAt(station, uNorm) {
  const c = Math.min(Math.abs(uNorm), 1) ** (1 / SECTION_N);
  return station.height * Math.sqrt(Math.max(0, 1 - c * c)) ** SECTION_N;
}

const RING = 22;
let shellMesh = null;
/** Quads of the shell, kept so the blasting loop can cut holes in it later. */
const shellQuads = [];
/** Boxes blasted out of the rib. Quads inside one are dropped from the shell. */
const breaches = [];
function applyShellIndex() {
  const position = shellMesh.geometry.attributes.position;
  const index = [], centre = new V(), corner = new V();
  for (const q of shellQuads) {
    centre.set(0, 0, 0);
    for (const v of q) centre.add(corner.fromBufferAttribute(position, v));
    centre.multiplyScalar(.25);
    if (breaches.some(b => b.containsPoint(centre))) continue;
    index.push(q[0], q[1], q[2], q[2], q[1], q[3]);
  }
  shellMesh.geometry.setIndex(index);
}
function buildCaveShell() {
  const positions = [], colors = [], uvs = [], tint = new THREE.Color();
  let vDist = 0;
  for (let i = 0; i <= SEGMENTS; i++) {
    const st = stations[i];
    if (i > 0) vDist += st.p.distanceTo(stations[i - 1].p);
    const invert = invertAt(st.p.z);
    let uDist = 0, previous = null;
    for (let j = 0; j <= RING; j++) {
      const a = j / RING * Math.PI * 2;
      const { u, y, uNorm } = section(a, st.width, st.height, invert);
      // Roughness lives on the ribs and the back only; a hand-cleared invert
      // has to stay flat or the player trips on nothing. Two octaves: slow
      // bulges the eye reads as form, then chisel-scale grain.
      const above = clamp(y / Math.max(st.height, .01), 0, 1);
      const swell = Math.sin(i * .11 + j * .37) * .075 + Math.sin(i * .043 - j * .21 + 2.1) * .055;
      const grain = Math.sin(i * .61 + j * 1.37) * .028 + Math.sin(i * .27 - j * .93) * .019;
      const rough = 1 + (swell + grain) * above;
      const point = st.p.clone().addScaledVector(st.side, u * rough);
      point.y = y >= 0 ? y * rough : y;
      if (previous) uDist += point.distanceTo(previous);
      previous = point.clone();
      positions.push(point.x, point.y, point.z);
      uvs.push(uDist / TILE, vDist / TILE);
      // Baked occlusion: the invert corners and the back of the arch sit in
      // their own shadow, and there is no shadow map to say so.
      const corner = clamp((Math.abs(uNorm) - .5) / .5, 0, 1) * (1 - above);
      const shade = .52 + above * .16 - corner * .2 - Math.max(0, above - .82) * .5;
      tint.setHSL(.24, .045, clamp(shade + swell * .35, .2, .78));
      colors.push(tint.r, tint.g, tint.b);
    }
  }
  for (let i = 0; i < SEGMENTS; i++) {
    const midZ = (stations[i].p.z + stations[i + 1].p.z) / 2;
    const openFloor = inShaftZ(midZ);
    for (let j = 0; j < RING; j++) {
      // Lower half of the ring is the invert; drop it where the shaft is.
      if (openFloor && j / RING > .5) continue;
      const a = i * (RING + 1) + j;
      shellQuads.push([a, a + RING + 1, a + 1, a + RING + 2]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  shellMesh = new THREE.Mesh(geometry, mats.cave);
  applyShellIndex();
  geometry.computeVertexNormals();
  visual.add(shellMesh);
}
/**
 * EXTENSION POINT — cut a hole in the rock shell. Procedural post-blast
 * generation can call this with any world box to open the drift into whatever
 * it wants to build behind the wall.
 */
function carveShell(worldBox) {
  breaches.push(worldBox);
  applyShellIndex();
  shellMesh.geometry.computeVertexNormals();
}

/**
 * Rock plug at each end of the drift, so the route never opens onto the void.
 * `push` runs along the tangent, so it is negative at the start and positive
 * at the far end to put the plug outside the route rather than inside it.
 */
function capEnd(index, push) {
  const st = stations[index], positions = [], uvs = [], indices = [];
  const invert = invertAt(st.p.z);
  const centre = st.p.clone().addScaledVector(st.tangent, push); centre.y = st.height * .42;
  for (let j = 0; j <= RING; j++) {
    const { u, y } = section(j / RING * Math.PI * 2, st.width, st.height, invert);
    const point = st.p.clone().addScaledVector(st.side, u).addScaledVector(st.tangent, push * .35);
    point.y = y;
    positions.push(point.x, point.y, point.z); uvs.push(u / TILE, y / TILE);
  }
  positions.push(centre.x, centre.y, centre.z); uvs.push(0, 0);
  const hub = RING + 1;
  for (let j = 0; j < RING; j++) indices.push(hub, j, j + 1);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  visual.add(new THREE.Mesh(geometry, mats.capRock));
}

/** The walked surface: packed spoil laid over the invert, wound to face up. */
function buildFloor() {
  const positions = [], uvs = [], indices = [];
  let run = 0;
  for (let i = 0; i <= SEGMENTS; i++) {
    const st = stations[i];
    if (i > 0) run += st.p.distanceTo(stations[i - 1].p);
    const half = st.width * .86;
    const left = st.p.clone().addScaledVector(st.side, -half), right = st.p.clone().addScaledVector(st.side, half);
    positions.push(left.x, 0, left.z, right.x, 0, right.z);
    uvs.push(0, run / TILE, half * 2 / TILE, run / TILE);
  }
  for (let i = 0; i < SEGMENTS; i++) {
    const midZ = (stations[i].p.z + stations[i + 1].p.z) / 2;
    if (inShaftZ(midZ) || inSumpZ(midZ)) continue;
    const a = i * 2;
    indices.push(a, a + 1, a + 2, a + 2, a + 1, a + 3);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  visual.add(new THREE.Mesh(geometry, mats.earth));
}

/** Standing water in the sump, filling the drift rib to rib below the trestle. */
function buildWater() {
  const positions = [], uvs = [], indices = [];
  const range = stations.filter(s => inSumpZ(s.p.z));
  range.forEach((st, i) => {
    const half = st.width * .99;
    const left = st.p.clone().addScaledVector(st.side, -half), right = st.p.clone().addScaledVector(st.side, half);
    positions.push(left.x, WATER_Y, left.z, right.x, WATER_Y, right.z);
    uvs.push(0, i * .5, 2, i * .5);
  });
  for (let i = 0; i < range.length - 1; i++) { const a = i * 2; indices.push(a, a + 1, a + 2, a + 2, a + 1, a + 3); }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  const mesh = new THREE.Mesh(geometry, mats.water); mesh.renderOrder = 2; visual.add(mesh);
}

buildCaveShell(); capEnd(0, -1.6); capEnd(SEGMENTS, 1.6); buildFloor(); buildWater();

/**
 * Where the rock actually is. The shell is displaced by its own roughness,
 * so the nominal half-width is up to a foot out — everything that has to
 * touch the wall asks the mesh instead of trusting the number.
 */
const wallRay = new THREE.Raycaster();
function wallHit(station, sideSign, y) {
  const origin = station.p.clone().setY(y);
  wallRay.set(origin, station.side.clone().multiplyScalar(sideSign));
  wallRay.far = station.width * 2.4;
  const hits = shellMesh ? wallRay.intersectObject(shellMesh, false) : [];
  if (hits.length) return hits[0].point.clone();
  return station.p.clone().addScaledVector(station.side, sideSign * station.width).setY(y);
}
/** A point on the rib wall: `sideSign` -1/+1, `inset` metres in from the rock. */
function ribPoint(station, sideSign, inset = 0, y = 0) {
  return wallHit(station, sideSign, Math.max(y, .3))
    .addScaledVector(station.side, -sideSign * inset)
    .setY(y);
}

/* --------------------------------------------------------- collision */
// Simplified proxies generated from the same stations as the art. Rib boxes
// are tagged so a blast can take the ones it opens back out again.
for (let i = 0; i < SEGMENTS; i++) {
  const a = stations[i], b = stations[i + 1];
  const mid = a.p.clone().add(b.p).multiplyScalar(.5);
  const length = a.p.distanceTo(b.p) + .18;
  const width = (a.width + b.width) / 2, height = (a.height + b.height) / 2;
  if (!inShaftZ(mid.z)) {
    // In the sump the walkable surface is the flooded rock, not the spoil.
    const floorY = inSumpZ(mid.z) ? -invertAt(mid.z) : 0;
    colliderBox(width * 1.9, .8, length, mid.x, floorY - .4, mid.z, a.yaw);
  }
  const rib = width + .30;
  for (const sign of [-1, 1]) {
    const p = mid.clone().addScaledVector(a.side, sign * rib);
    const collider = colliderBox(.7, height + 2.4, length, p.x, height / 2, p.z, a.yaw);
    collider.userData.rib = { index: i, sign };
  }
}

/* ------------------------------------------------------------------ *
 * Rail
 *
 * One continuous 900 mm tramway from the portal to the Foreman's Vault. It
 * runs level at floor height the whole way: over the Blackshaft it crosses
 * on the bridge deck, over the sump on the trestle, and both of those are
 * laid flush so the track never has to climb or break.
 * ------------------------------------------------------------------ */
const GAUGE = .9, RAIL_TOP = .18;
function buildRail(z0, z1) {
  const run = stations.filter(s => s.p.z <= z0 && s.p.z >= z1);
  if (run.length < 2) return;
  let carried = 0;
  for (let i = 0; i < run.length - 1; i++) {
    carried += run[i].p.distanceTo(run[i + 1].p);
    if (carried < .68) continue;
    carried = 0;
    box(GAUGE + .62, .14, .22, mats.woodDark, run[i].p.x, .05, run[i].p.z, run[i].yaw);
  }
  for (const sign of [-1, 1]) {
    const points = run.map(s => {
      const p = s.p.clone().addScaledVector(s.side, sign * GAUGE / 2); p.y = RAIL_TOP - .05; return p;
    });
    const curve = new THREE.CatmullRomCurve3(points, false, 'catmullrom', .2);
    visual.add(new THREE.Mesh(new THREE.TubeGeometry(curve, points.length * 2, .05, 4, false), mats.railHead));
  }
}
/** An ore cart, sitting on the rail at the station you give it. */
function cart(z, { loaded = true, spin = 0 } = {}) {
  const st = stationAtZ(z);
  const group = new THREE.Group(); group.position.copy(st.p); group.rotation.y = st.yaw + spin; visual.add(group);
  for (const x of [-GAUGE / 2, GAUGE / 2]) for (const z0 of [-.52, .52]) {
    cyl(.2, .2, .09, 12, mats.ironDark, x, RAIL_TOP + .2, z0, 0, 0, Math.PI / 2, group);
    cyl(.25, .25, .03, 12, mats.metal, x + (x < 0 ? -.05 : .05), RAIL_TOP + .2, z0, 0, 0, Math.PI / 2, group);
  }
  box(GAUGE + .34, .12, 1.42, mats.ironDark, 0, RAIL_TOP + .44, 0, 0, 0, 0, group);
  box(1.16, .58, 1.3, mats.ironDark, 0, RAIL_TOP + .78, 0, 0, 0, 0, group);
  box(1.22, .07, 1.36, mats.metal, 0, RAIL_TOP + 1.08, 0, 0, 0, 0, group);
  if (loaded) {
    for (const [ox, oz, s, mat] of [[-.24, -.18, .34, mats.rock], [.2, .16, .27, mats.darkRock], [0, -.02, .22, mats.GLIMMER]]) {
      const ore = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), mat);
      ore.scale.set(1.3, .6, .95); ore.position.set(ox, RAIL_TOP + 1.12, oz); ore.rotation.set(.2, ox * 3, .1); group.add(ore);
    }
  }
  colliderBox(1.3, 1.35, 1.5, st.p.x, .68, st.p.z, st.yaw + spin);
}

/* ------------------------------------------------------------------ *
 * Timber
 *
 * Each set is sized from the drift at its own station: feet on the invert,
 * posts inside the rib, cap beam tucked under the back.
 * ------------------------------------------------------------------ */
function timberSet(z, { damaged = false, inset = .32, lean = .12 } = {}) {
  const st = stationAtZ(z);
  const capY = crownAt(st, (st.width - inset - lean) / st.width) - .16;
  const group = new THREE.Group(); visual.add(group);
  const left = ribPoint(st, -1, inset, -.05), right = ribPoint(st, 1, inset, -.05);
  const leftTop = ribPoint(st, -1, inset + lean, capY), rightTop = ribPoint(st, 1, inset + lean, capY);
  if (damaged) rightTop.y -= .18;
  beamBetween(left, leftTop, .16, mats.woodDark, group);
  beamBetween(right, rightTop, .16, mats.wood, group);
  beamBetween(leftTop, rightTop, .17, mats.wood, group);
  // Knee braces: the cap beam needs a reason not to sag.
  for (const [foot0, top0] of [[left, leftTop], [right, rightTop]]) {
    const kneeA = foot0.clone().lerp(top0, .62), kneeB = leftTop.clone().lerp(rightTop, foot0 === left ? .24 : .76);
    beamBetween(kneeA, kneeB, .085, mats.woodDark, group);
  }
  if (damaged) {
    const split = left.clone().lerp(leftTop, .3);
    beamBetween(split, split.clone().addScaledVector(st.side, .55).setY(split.y + .9), .075, mats.woodDark, group);
  }
  for (const p of [left, right]) colliderBox(.42, capY + .2, .5, p.x, capY / 2, p.z, st.yaw);
  return { st, capY, leftTop, rightTop };
}

/* ------------------------------------------------------------------ *
 * Practical lights
 *
 * A handful of real point lights carry the route; everything else is an
 * emissive fixture with no light attached.
 * ------------------------------------------------------------------ */
const lampLights = [];
const glowMaterials = new Map();
function glow(color, opacity) {
  const key = `${color}|${opacity}`;
  if (!glowMaterials.has(key)) {
    glowMaterials.set(key, opacity < 1
      ? new THREE.MeshBasicMaterial({ color, transparent: true, opacity, side: THREE.DoubleSide })
      : new THREE.MeshBasicMaterial({ color }));
  }
  return glowMaterials.get(key);
}
function lampFixture(position, yaw, { color = 0xffc169, real = true, scale = 1, range = 13, power = 26, backplate = true } = {}) {
  const group = new THREE.Group(); group.position.copy(position); group.rotation.y = yaw; visual.add(group);
  // Local +z points away from whatever the lamp is bolted to, so the bracket
  // always starts inside the wall or beam and the lamp never floats.
  if (backplate) box(.3 * scale, .34 * scale, .1 * scale, mats.ironDark, 0, .06 * scale, -.02 * scale, 0, 0, 0, group);
  box(.07 * scale, .07 * scale, .58 * scale, mats.ironDark, 0, .16 * scale, .26 * scale, 0, 0, 0, group);
  beamBetween(new V(0, -.06 * scale, .02 * scale), new V(0, .15 * scale, .32 * scale), .026 * scale, mats.ironDark, group);
  cyl(.03 * scale, .03 * scale, .2 * scale, 6, mats.ironDark, 0, .06 * scale, .52 * scale, 0, 0, 0, group);
  cyl(.17 * scale, .1 * scale, .16 * scale, 8, mats.ironDark, 0, -.06 * scale, .52 * scale, 0, 0, 0, group);
  const shade = new THREE.Mesh(new THREE.CylinderGeometry(.115 * scale, .115 * scale, .23 * scale, 8, 1, true), glow(color, .55));
  shade.position.set(0, -.24 * scale, .52 * scale); group.add(shade);
  const flame = new THREE.Mesh(new THREE.SphereGeometry(.07 * scale, 10, 8), glow(color, 1));
  flame.scale.set(.75, 1.3, .75); flame.position.set(0, -.24 * scale, .52 * scale); group.add(flame);
  if (real) {
    const light = new THREE.PointLight(color, coarse ? power * .8 : power, range, 1.9);
    light.position.set(0, -.18 * scale, .46 * scale); group.add(light);
    lampLights.push({ light, base: light.intensity, phase: lampLights.length * 1.41 });
  }
  return group;
}
/** Hang a lamp off the rib at a station, pointing into the drift. */
function ribLamp(z, sideSign, height, options) {
  const st = stationAtZ(z);
  return lampFixture(ribPoint(st, sideSign, .18, height),
    Math.atan2(-st.side.x * sideSign, -st.side.z * sideSign), options);
}
/** Nail a sign to the rib, facing into the drift. */
function ribSign(z, sideSign, height, text, sub, accent, scale = .82) {
  const st = stationAtZ(z);
  const board = signBoard(text, sub, accent, scale);
  board.position.copy(ribPoint(st, sideSign, .06, height));
  board.rotation.y = Math.atan2(-st.side.x * sideSign, -st.side.z * sideSign);
  return board;
}
/** Hang a lamp under a timber cap beam, which is where a crew would put it. */
function capLamp(set, options = {}) {
  const p = set.leftTop.clone().lerp(set.rightTop, .5); p.y -= .2;
  const group = lampFixture(p, set.st.yaw, { ...options, backplate: false });
  beamBetween(new V(0, .06, .52), new V(0, .3, .04), .028, mats.ironDark, group);
  return group;
}

/* ---------------------------------------------------------- props */
function crate(z, sideSign, offset, { scale = 1, spin = 0, label = '' } = {}) {
  const st = stationAtZ(z);
  const p = ribPoint(st, sideSign, offset, 0);
  const w = 1.05 * scale, h = .82 * scale;
  const group = new THREE.Group(); group.position.copy(p); group.rotation.y = st.yaw + spin; visual.add(group);
  box(w, h, w, mats.woodDark, 0, h / 2, 0, 0, 0, 0, group);
  for (const y of [.12 * scale, h - .12 * scale]) box(w + .05, .08 * scale, w + .05, mats.wood, 0, y, 0, 0, 0, 0, group);
  box(.08 * scale, h + .02, w + .05, mats.wood, 0, h / 2, 0, 0, 0, .62, group);
  if (label) {
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(.66 * scale, .22 * scale),
      new THREE.MeshBasicMaterial({ map: signTexture(label, 'HANDLE WITH CARE', '#dbab5c') }));
    plate.position.set(0, h * .55, w / 2 + .01); group.add(plate);
  }
  colliderBox(w, h, w, p.x, h / 2, p.z, st.yaw + spin);
  return group;
}
function barrel(z, sideSign, offset, { scale = 1 } = {}) {
  const st = stationAtZ(z), p = ribPoint(st, sideSign, offset, 0);
  const group = new THREE.Group(); group.position.copy(p); visual.add(group);
  cyl(.38 * scale, .42 * scale, .95 * scale, 14, mats.wood, 0, .475 * scale, 0, 0, 0, 0, group);
  for (const y of [.16, .48, .8]) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(.405 * scale, .032 * scale, 6, 16), mats.ironDark);
    ring.rotation.x = Math.PI / 2; ring.position.y = y * scale; group.add(ring);
  }
  colliderBox(.8 * scale, .95 * scale, .8 * scale, p.x, .475 * scale, p.z);
  return group;
}
function ropeCoil(z, sideSign, offset, scale = 1) {
  const st = stationAtZ(z), p = ribPoint(st, sideSign, offset, .07 * scale);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(.38 * scale, .07 * scale, 7, 18), mats.rope);
  ring.rotation.x = Math.PI / 2; ring.position.copy(p); visual.add(ring);
}

/* ------------------------------------------------------- Maw Camp */
const portalSets = [timberSet(20.4, { inset: .4 }), timberSet(15.6)];
capLamp(portalSets[0], { color: 0xffcf8a, range: 14, power: 24 });
const portal = stationAtZ(21.4);
box(2.1, 2.7, .5, mats.black, portal.p.x, 1.35, portal.p.z + .35);
for (const sign of [-1, 1]) box(.32, 2.9, .38, mats.woodDark, portal.p.x + sign * 1.2, 1.45, portal.p.z + .1);
box(3.1, .34, .42, mats.wood, portal.p.x, 3.05, portal.p.z + .1);
const campSign = signBoard('MAW CAMP', 'STAGING / SHIFT 03', '#e9b35a', 1.05);
campSign.position.set(portalSets[0].st.p.x, portalSets[0].capY - .52, portalSets[0].st.p.z - .3);
campSign.rotation.y = Math.PI;
for (const sx of [-.7, .7]) beamBetween(
  new V(campSign.position.x + sx, portalSets[0].capY - .1, campSign.position.z + .12),
  new V(campSign.position.x + sx, campSign.position.y, campSign.position.z + .02), .022, mats.ironDark);
crate(18.6, 1, .55, { scale: 1.02, spin: .16, label: 'LAMP OIL' });
crate(19.5, 1, .5, { scale: .76, spin: -.2 });
barrel(17.4, 1, .5);
ropeCoil(19.6, 1, 1.4, 1.1);
cart(16.2, { loaded: false });
ribLamp(17.2, 1, 2.5, { color: 0xffc26a, range: 14, power: 22 });
ribLamp(20, 1, 2.4, { color: 0xffbd65, real: false });

/* ---------------------------------------------------- Crooked Rail */
const railSets = [timberSet(12.4, { damaged: true }), timberSet(9.4), timberSet(4.4, { damaged: true }), timberSet(.4)];
capLamp(railSets[0], { color: 0xffc26a, real: false });
capLamp(railSets[1], { color: 0xffb35d, range: 11, power: 18 });
capLamp(railSets[3], { color: 0xffb35d, range: 12, power: 20 });
ribLamp(11.4, 1, 2.3, { color: 0x9ad9c4, real: false });
// Tools left leaning on the rib: the reason the drift looks worked, not grown.
const toolSt = stationAtZ(13.4), toolAt = ribPoint(toolSt, 1, .3, 0);
const toolHead = new V(toolAt.x - .34, 1.2, toolAt.z + .16);
beamBetween(new V(toolAt.x, .02, toolAt.z), toolHead, .028, mats.wood);
box(.34, .06, .07, mats.ironDark, toolHead.x, toolHead.y, toolHead.z, 0, .34);
barrel(14.2, 1, .5, { scale: .78 });

/* ---------------------------------------------------- Blackshaft */
// A real hole, rib to rib, crossed by one deck that also carries the rail.
const shaftMid = stationAtZ((SHAFT.z0 + SHAFT.z1) / 2);
const shaftHalf = shaftMid.width, shaftLen = SHAFT.z0 - SHAFT.z1, shaftDepth = 7.6;
for (const sign of [-1, 1]) box(.6, shaftDepth, shaftLen + 1.2, mats.darkRock, shaftMid.p.x + sign * (shaftHalf + .25), -shaftDepth / 2, shaftMid.p.z);
for (const z of [SHAFT.z0 + .3, SHAFT.z1 - .3]) box(shaftHalf * 2 + 1.2, shaftDepth, .6, mats.darkRock, shaftMid.p.x, -shaftDepth / 2, z);
box(shaftHalf * 2, .3, shaftLen, mats.darkRock, shaftMid.p.x, -shaftDepth - .15, shaftMid.p.z);
box(shaftHalf * 1.4, .06, shaftLen * .5, mats.water, shaftMid.p.x, -shaftDepth + .04, shaftMid.p.z + 1.2);
for (const sx of [-1, 1]) for (const sz of [SHAFT.z0 - .5, SHAFT.z1 + .5]) {
  const x = shaftMid.p.x + sx * (shaftHalf - .45);
  box(.42, shaftDepth, .42, mats.woodDark, x, -shaftDepth / 2 + .3, sz);
  beamBetween(new V(x, .1, sz), new V(x, -shaftDepth + .2, sz), .05, mats.rope);
}
for (let d = 1.6; d < shaftDepth; d += 2.1) {
  for (const sz of [SHAFT.z0 - .5, SHAFT.z1 + .5]) box(shaftHalf * 2 - .9, .26, .3, mats.woodDark, shaftMid.p.x, -d, sz);
}
box(2.6, .16, 3.4, mats.woodDark, shaftMid.p.x - 1.1, -shaftDepth + .9, shaftMid.p.z - 1.6, 0, 0, .12);
lampFixture(new V(shaftMid.p.x - 1.1, -shaftDepth + 1.9, shaftMid.p.z - 1.6), 0, { color: 0x6fc9cf, range: 9, power: 14 });
lampFixture(new V(shaftMid.p.x + 2.2, -shaftDepth + 1.3, shaftMid.p.z + 3.1), 0, { color: 0x74c7bd, real: false });

// The crossing: flush with the drift floor and wide enough for the tramway
// and a person beside it, on bearers spanning the shaft.
const BRIDGE_W = 2.8;
const deckZ0 = SHAFT.z0 + .9, deckZ1 = SHAFT.z1 - .9, deckMid = (deckZ0 + deckZ1) / 2, deckLen = deckZ0 - deckZ1;
for (const x of [-1.0, 1.0]) box(.24, .32, deckLen, mats.woodDark, x, -.25, deckMid);
box(BRIDGE_W, .18, deckLen, mats.wood, 0, 0, deckMid);
colliderBox(BRIDGE_W, .34, deckLen, 0, -.12, deckMid);
for (const sign of [-1, 1]) {
  const x = sign * (BRIDGE_W / 2 - .14);
  for (let z = deckZ0 - .5; z > deckZ1; z -= 2.2) box(.12, 1.0, .14, mats.ironDark, x, .58, z);
  const railPoints = [new V(x, 1.0, deckZ0 - .5), new V(x, 1.04, deckMid), new V(x, 1.0, deckZ1 + .5)];
  visual.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(railPoints), 18, .045, 5, false), mats.metal));
  colliderBox(.16, 1.1, deckLen, x, .6, deckMid);
}
// Hoist at the shaft head, both legs on the drift floor, rope to the bottom.
const winchSt = stationAtZ(SHAFT.z0 + 1.8);
const winchAt = ribPoint(winchSt, -1, .95, .95);
const winch = new THREE.Group(); winch.position.copy(winchAt); winch.rotation.y = winchSt.yaw; visual.add(winch);
box(1.0, .16, .7, mats.woodDark, 0, 0, 0, 0, 0, 0, winch);
cyl(.26, .26, .5, 12, mats.metal, 0, .2, 0, 0, 0, Math.PI / 2, winch);
cyl(.05, .05, .95, 8, mats.wood, 0, .2, 0, 0, 0, Math.PI / 2, winch);
box(.1, .12, .24, mats.ironDark, .48, .2, .1, 0, 0, 0, winch);
for (const sz of [-.26, .26]) for (const sx of [-.42, .42]) box(.13, .95, .13, mats.woodDark, sx, -.5, sz, 0, 0, 0, winch);
beamBetween(new V(-.42, -.5, 0), new V(.42, -.5, 0), .05, mats.woodDark, winch);
beamBetween(winchAt.clone().setY(winchAt.y + .2), new V(winchAt.x, -shaftDepth + .5, winchAt.z - 3.6), .03, mats.rope);
colliderBox(1.1, 1.2, .8, winchAt.x, .55, winchAt.z, winchSt.yaw);
ribLamp(SHAFT.z0 + .4, -1, 2.6, { color: 0xffbd66, range: 15, power: 30 });
ribLamp(SHAFT.z1 - .4, -1, 2.6, { color: 0x76cbd0, range: 15, power: 28 });
const shaftSign = signBoard('BLACKSHAFT', 'MIND THE DECK', '#d98352', .95);
shaftSign.position.set(0, 2.5, SHAFT.z0 + 2.1);

/* -------------------------------------------------- Drowned Pocket */
// A timber trestle carrying the track across the sump, flush with the floor
// so the rail never breaks, standing on piles down into the water.
const TRESTLE_W = 3.0;
const trestle = stations.filter(s => s.p.z <= SUMP.z0 + 1.0 && s.p.z >= SUMP.z1 - 1.0);
for (let i = 0; i < trestle.length - 1; i++) {
  const a = trestle[i], b = trestle[i + 1];
  const mid = a.p.clone().add(b.p).multiplyScalar(.5), length = a.p.distanceTo(b.p) + .1;
  box(TRESTLE_W, .18, length, mats.wood, mid.x, 0, mid.z, a.yaw);
  colliderBox(TRESTLE_W, .34, length, mid.x, -.12, mid.z, a.yaw);
  if (i % 4 === 0 && inSumpZ(mid.z)) {
    for (const sign of [-1, 1]) {
      const pile = mid.clone().addScaledVector(a.side, sign * (TRESTLE_W / 2 - .2));
      beamBetween(new V(pile.x, -.14, pile.z), new V(pile.x, -invertAt(mid.z) - .1, pile.z), .1, mats.woodDark);
    }
    box(TRESTLE_W - .1, .16, .2, mats.woodDark, mid.x, -.22, mid.z, a.yaw);
  }
}
const sumpMid = stationAtZ((SUMP.z0 + SUMP.z1) / 2);
for (const sign of [-1, 1]) {
  const points = trestle.map(s => s.p.clone().addScaledVector(s.side, sign * (TRESTLE_W / 2 - .13)).setY(.98));
  for (let i = 0; i < trestle.length; i += 5) {
    const post = trestle[i].p.clone().addScaledVector(trestle[i].side, sign * (TRESTLE_W / 2 - .13));
    box(.11, 1.0, .13, mats.ironDark, post.x, .5, post.z, trestle[i].yaw);
  }
  visual.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), points.length * 2, .045, 5, false), mats.metal));
  const guard = sumpMid.p.clone().addScaledVector(sumpMid.side, sign * (TRESTLE_W / 2 - .13));
  colliderBox(.16, 1.1, SUMP.z0 - SUMP.z1 + 2, guard.x, .6, guard.z, sumpMid.yaw);
}
// A pump on a staging over the water, the reason the route is passable.
const pumpSt = stationAtZ(-27.5), pumpAt = ribPoint(pumpSt, 1, 1.3, 0);
box(2.4, .16, 3.2, mats.woodDark, pumpAt.x, 0, pumpAt.z, pumpSt.yaw);
colliderBox(2.4, .3, 3.2, pumpAt.x, -.1, pumpAt.z, pumpSt.yaw);
const pump = new THREE.Group(); pump.position.copy(pumpAt); pump.rotation.y = pumpSt.yaw; visual.add(pump);
box(.95, 1.25, .8, mats.metal, 0, .7, 0, 0, 0, 0, pump);
cyl(.55, .55, .12, 16, mats.metal, .1, 1.3, 0, 0, 0, Math.PI / 2, pump);
cyl(.09, .09, 1.5, 8, mats.wood, .1, 1.3, 0, 0, 0, Math.PI / 2, pump);
colliderBox(1.0, 1.6, .9, pumpAt.x, .8, pumpAt.z, pumpSt.yaw);
visual.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
  pumpAt.clone().setY(.9), pumpAt.clone().addScaledVector(pumpSt.side, 1.0).setY(.4),
  pumpAt.clone().addScaledVector(pumpSt.side, 2.0).setY(WATER_Y - .2),
]), 20, .08, 6, false), mats.ironDark));
// Collapsed timber, one end on the rib and the other under the water.
const wreckSt = stationAtZ(-32.5), wreckAt = ribPoint(wreckSt, -1, .35, 0);
beamBetween(new V(wreckAt.x, 2.2, wreckAt.z - 1.2), new V(wreckAt.x + 2.2, WATER_Y - .3, wreckAt.z + .8), .16, mats.woodDark);
beamBetween(new V(wreckAt.x, 1.7, wreckAt.z + .6), new V(wreckAt.x + 1.5, WATER_Y - .2, wreckAt.z + 1.8), .13, mats.woodDark);
ribLamp(-23.5, -1, 2.7, { color: 0x83d0d0, range: 15, power: 26 });
ribLamp(-30, 1, 2.6, { color: 0x7ed1d0, range: 14, power: 24 });
ribLamp(-34.5, -1, 2.6, { color: 0x7ed1d0, real: false });
ribSign(-22.6, -1, 2.4, 'DROWNED POCKET', 'PUMP BATTERY // KEEP TO THE TRESTLE', '#79c8c0');

/* ------------------------------------------------------ Powderworks */
const powderSets = [timberSet(-42.4, { inset: .3 }), timberSet(-47.4, { damaged: true, inset: .34 })];
capLamp(powderSets[1], { color: 0xff9c52, range: 13, power: 24 });
crate(-41.6, 1, .55, { scale: 1.0, spin: .08, label: 'POWDER' });
crate(-42.8, 1, .5, { scale: .8, spin: -.14 });
barrel(-43.8, 1, 1.4, { scale: .82 });
ribSign(-41.4, -1, 2.4, 'POWDERWORKS', 'NO OPEN FLAME // NO HEROICS', '#e8794f', .9);
ribLamp(-43.4, 1, 2.4, { color: 0xffa455, range: 13, power: 24 });
// Drill rig against the rib, its steel in the face it was cutting.
const drillSt = stationAtZ(-48.4), drillAt = ribPoint(drillSt, 1, .9, 0);
const drillRig = new THREE.Group(); drillRig.position.copy(drillAt); drillRig.rotation.y = drillSt.yaw; visual.add(drillRig);
box(.85, 1.35, .68, mats.metal, 0, .68, 0, 0, 0, 0, drillRig);
box(.16, 1.6, .16, mats.woodDark, .36, .9, 0, 0, 0, -.12, drillRig);
cyl(.16, .1, 1.25, 10, mats.ironDark, .55, .95, 0, 0, 0, Math.PI / 2.6, drillRig);
colliderBox(.9, 1.4, .8, drillAt.x, .7, drillAt.z, drillSt.yaw);

/* -------------------------------------------------- Foreman's Vault */
const gateSt = stationAtZ(-52.4);
const gate = new THREE.Group(); gate.position.copy(gateSt.p); gate.rotation.y = gateSt.yaw; visual.add(gate);
const gateHalf = Math.min(gateSt.width - .5, 2.4), gateTop = crownAt(gateSt, (gateHalf + .2) / gateSt.width) - .1;
for (const sign of [-1, 1]) {
  box(.26, gateTop, .26, mats.ironDark, sign * gateHalf, gateTop / 2, 0, 0, 0, 0, gate);
  box(.42, .22, .42, mats.gold, sign * gateHalf, gateTop + .1, 0, 0, 0, 0, gate);
  const p = gateSt.p.clone().addScaledVector(gateSt.side, sign * gateHalf);
  colliderBox(.34, gateTop, .34, p.x, gateTop / 2, p.z, gateSt.yaw);
}
box(gateHalf * 2 + .4, .2, .3, mats.ironDark, 0, gateTop - .1, 0, 0, 0, 0, gate);
// The tramway runs through the gate, so the bars stop short of the track.
for (let x = -gateHalf + .55; x <= gateHalf - .5; x += .78) {
  if (Math.abs(x) < GAUGE / 2 + .55) continue;
  box(.1, gateTop - .3, .11, mats.metal, x, (gateTop - .3) / 2, 0, 0, 0, 0, gate);
  const p = gateSt.p.clone().addScaledVector(gateSt.side, x);
  colliderBox(.16, gateTop - .3, .18, p.x, (gateTop - .3) / 2, p.z, gateSt.yaw);
}
const vaultSign = signBoard("FOREMAN'S VAULT", 'AUTHORIZED CREW ONLY', '#edb75c', .88);
vaultSign.position.copy(gateSt.p).addScaledVector(gateSt.tangent, .5).setY(gateTop + .55);
vaultSign.rotation.y = gateSt.yaw + Math.PI;
const deskSt = stationAtZ(-56.4), deskAt = deskSt.p.clone().addScaledVector(deskSt.side, -1.6);
box(2.4, .12, 1.1, mats.woodDark, deskAt.x, .88, deskAt.z, deskSt.yaw);
box(2.1, .06, .9, mats.paper, deskAt.x, .97, deskAt.z, deskSt.yaw);
box(.7, .12, .5, mats.gold, deskAt.x + .2, 1.06, deskAt.z, deskSt.yaw, 0, 0);
for (const sign of [-1, 1]) box(.11, .82, .11, mats.woodDark, deskAt.x + sign * 1.0, .41, deskAt.z, deskSt.yaw);
colliderBox(2.4, .95, 1.15, deskAt.x, .47, deskAt.z, deskSt.yaw);
crate(-57.4, 1, .6, { scale: 1.0, spin: .12 }); crate(-58.6, 1, .55, { scale: .78, spin: -.1 });
ribLamp(-53.4, -1, 2.7, { color: 0xffc569, range: 15, power: 30 });
ribLamp(-57.4, 1, 2.6, { color: 0xffc569, real: false });
cart(-58.6, { loaded: true });

buildRail(20.6, -59.4);

/* ------------------------------------------------------------------ *
 * Ore faces
 *
 * Four marked faces in the rock, one per working. Each is somewhere the
 * survey crew chalked up and left: you drill the round, charge it, blow it,
 * and pick the ore out of what the blast exposes.
 *
 * The pre-blast face is authored art; everything the blast leaves behind is
 * generated in `generateBlastResult`, which is the seam procedural
 * generation is meant to replace.
 * ------------------------------------------------------------------ */
const DRILL = { holes: 3, seconds: 3.0, reach: 3.6, depth: 2.0 };
const BLAST = { fuse: 5, safeRadius: 13, depth: 3.4, width: 3.4, height: 2.7 };
const PICK = { seconds: 1.5 };
// You start with exactly one round's worth of powder, so the first face
// teaches the loop for free and every one after it has to be paid for.
const ECONOMY = { startCredits: 60, startTnt: 3, tntCost: 45 };

const ORE_FACES = [
  { id: 'crooked', label: 'CROOKED RAIL SEAM', z: 7.4, side: -1, grade: 'COPPER', value: 30, nodes: 5 },
  { id: 'blackshaft', label: 'SHAFT WALL', z: -16.4, side: 1, grade: 'IRON', value: 38, nodes: 6 },
  { id: 'glimmer', label: 'SAINT GLIMMER', z: -37.4, side: 1, grade: 'GLIMMER', value: 62, nodes: 8 },
  { id: 'powder', label: 'POWDERWORKS FACE', z: -45.4, side: -1, grade: 'IRON', value: 38, nodes: 6 },
];
/** Hole positions on the face, in face-local metres. A round, not a grid. */
const HOLE_MARKS = [[-.86, 1.32], [.05, 1.78], [.92, 1.24]];

const interactables = [];
function addInteractable(object, kind, ref) {
  object.updateMatrixWorld(true);
  interactables.push({ object, kind, ref });
  return object;
}
function removeInteractable(object) {
  const i = interactables.findIndex(entry => entry.object === object);
  if (i >= 0) interactables.splice(i, 1);
}

/**
  * A patch of mineral crust set into the rock, not a gem stuck on it. Small
  * and dull on purpose: the lantern has to find it. Face-local +Z runs into
  * the rock, so anything meant to be seen sits at negative z.
  */
function crustPatch(parent, material, x, y, size, spin) {
  const mesh = new THREE.Mesh(new THREE.DodecahedronGeometry(size, 0), material);
  mesh.scale.set(1.2, .8, .3);
  mesh.position.set(x, y, -.15 - size * .3);
  mesh.rotation.set(.1, spin, spin * .6);
  parent.add(mesh);
}

for (const face of ORE_FACES) {
  const st = stationAtZ(face.z);
  face.station = st;
  // Outward normal of the rib, and the frame the face is authored in.
  face.out = st.side.clone().multiplyScalar(face.side).normalize();
  face.origin = ribPoint(st, face.side, 0, 1.4).setY(0);
  face.yaw = Math.atan2(face.out.x, face.out.z);
  face.holes = 0; face.charges = 0; face.state = 'intact';
  face.holeMeshes = []; face.oreNodes = []; face.owed = 0;

  // Built at the origin, merged by material, then placed: the marked face has
  // to survive as its own object because the blast has to take it away again,
  // and merging it here keeps that to three draw calls instead of eighteen.
  const group = new THREE.Group();

  // Host rock: a band of darker matrix standing out of the country rock, the
  // reason a survey crew stopped here at all. Several small bosses rather than
  // one slab, so it breaks up against the rib behind it.
  const ore = mats[face.grade];
  for (const [x, y, sx, sy, spin] of [[-1.15, 1.35, .72, .58, -.16], [-.42, 1.72, .8, .66, .12],
    [.34, 1.5, .74, .6, -.1], [.98, 1.74, .6, .5, .2], [-.2, 1.08, .5, .38, .3]]) {
    const lobe = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), mats.matrix);
    lobe.scale.set(sx, sy, .55); lobe.position.set(x, y, .4); lobe.rotation.set(.08, spin, spin);
    group.add(lobe);
  }
  // Crust: small, clustered, irregular, no repeating rhythm.
  for (const [x, y, s, spin] of [[-1.02, 1.28, .13, .4], [-.86, 1.46, .08, 1.1], [-.5, 1.62, .11, -.6],
    [-.3, 1.78, .16, .2], [-.02, 1.55, .09, .9], [.28, 1.68, .14, -1.2], [.44, 1.42, .08, .3],
    [.86, 1.8, .1, .75], [-.24, 1.02, .09, -.4]]) {
    crustPatch(group, ore, x, y, s, spin);
  }
  // Chalk: the survey mark and the drill pattern the shot-firer left.
  box(.5, .035, .02, mats.chalk, 0, 2.26, -.24, 0, .22, 0, group);
  box(.035, .3, .02, mats.chalk, 0, 2.26, -.24, 0, 0, 0, group);
  for (const [hx, hy] of HOLE_MARKS) {
    box(.16, .028, .02, mats.chalk, hx, hy, -.26, 0, .78, 0, group);
    box(.16, .028, .02, mats.chalk, hx, hy, -.26, 0, -.78, 0, group);
  }
  mergeStatics(group);
  group.position.copy(face.origin); group.rotation.y = face.yaw;
  dynamic.add(group);
  face.art = group;
  ribSign(face.z + 2.4, face.side, 2.5, face.label, `${face.grade} // MARKED FOR A ROUND`,
    face.grade === 'GLIMMER' ? '#7be1c5' : '#d9a552', .74);

  // Interaction proxy: a slab standing on the face, never rendered.
  const target = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.4, .4), colliderMaterial);
  target.position.copy(face.origin).addScaledVector(face.out, -.15).setY(1.5);
  target.rotation.y = face.yaw;
  addInteractable(target, 'face', face);
  face.target = target;
}

/* ------------------------------------------------------- supply point */
// Where the shift buys powder and hands in ore. Kept at Maw Camp so the loop
// always walks you back past everything you have already opened up.
const supplySt = stationAtZ(19.4);
const supplyAt = ribPoint(supplySt, -1, .95, 0);
const supply = new THREE.Group();
supply.position.copy(supplyAt); supply.rotation.y = supplySt.yaw; visual.add(supply);
box(1.9, .12, 1.0, mats.woodDark, 0, .92, 0, 0, 0, 0, supply);
for (const sx of [-.8, .8]) box(.12, .9, .12, mats.woodDark, sx, .45, 0, 0, 0, 0, supply);
box(1.7, .5, .16, mats.woodDark, 0, .65, -.42, 0, 0, 0, supply);
box(.7, .26, .5, mats.red, -.4, 1.11, .05, 0, .2, 0, supply);
box(.72, .06, .52, mats.gold, -.4, 1.26, .05, 0, .2, 0, supply);
for (const [x, z] of [[.5, .1], [.72, -.16]]) cyl(.09, .09, .34, 8, mats.red, x, 1.15, z, 0, 0, Math.PI / 2, supply);
const supplySign = signBoard('POWDER STORE', 'CHARGES OUT // ORE IN', '#e9b35a', .66, supply);
supplySign.position.set(0, 1.85, -.05);
colliderBox(2.0, 1.0, 1.1, supplyAt.x, .5, supplyAt.z, supplySt.yaw);
ribLamp(20.2, -1, 2.5, { color: 0xffcf8a, range: 12, power: 22 });
{
  const target = new THREE.Mesh(new THREE.BoxGeometry(2.2, 2.0, 1.6), colliderMaterial);
  target.position.copy(supplyAt).setY(1.0); target.rotation.y = supplySt.yaw;
  addInteractable(target, 'supply', null);
}

/* ------------------------------------------------------------ light */
scene.add(new THREE.HemisphereLight(0x9fc6bb, 0x3a3128, coarse ? 1.5 : 1.35));
scene.add(new THREE.AmbientLight(0x5d7a78, coarse ? .85 : .7));
const daylight = new THREE.PointLight(0xc2dbe0, coarse ? 11 : 14, 15, 2);
daylight.position.set(portal.p.x, 2.0, portal.p.z - 1.1); scene.add(daylight);

/* ------------------------------------------------------------------ *
 * Static merge
 *
 * The mine is authored as several hundred small placed meshes, which is the
 * right way to place them and the wrong way to draw them. Everything in
 * `visual` is baked and concatenated by material once placement is done;
 * `dynamic` is left alone because the blasting loop edits it at runtime.
 * ------------------------------------------------------------------ */
function mergeGeometries(parts) {
  let vertexCount = 0, indexCount = 0;
  for (const part of parts) {
    vertexCount += part.attributes.position.count;
    indexCount += part.index ? part.index.count : part.attributes.position.count;
  }
  const position = new Float32Array(vertexCount * 3);
  const normal = new Float32Array(vertexCount * 3);
  const uv = new Float32Array(vertexCount * 2);
  const index = vertexCount > 65535 ? new Uint32Array(indexCount) : new Uint16Array(indexCount);
  let vOffset = 0, iOffset = 0;
  for (const part of parts) {
    const count = part.attributes.position.count;
    position.set(part.attributes.position.array, vOffset * 3);
    normal.set(part.attributes.normal.array, vOffset * 3);
    uv.set(part.attributes.uv.array, vOffset * 2);
    if (part.index) {
      for (let i = 0; i < part.index.count; i++) index[iOffset + i] = part.index.array[i] + vOffset;
      iOffset += part.index.count;
    } else {
      for (let i = 0; i < count; i++) index[iOffset + i] = vOffset + i;
      iOffset += count;
    }
    vOffset += count;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(position, 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(normal, 3));
  geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geometry.setIndex(new THREE.BufferAttribute(index, 1));
  return geometry;
}
function mergeStatics(root) {
  const byMaterial = new Map(), keep = [];
  root.updateMatrixWorld(true);
  const lights = [];
  root.traverse(n => { if (n.isLight) lights.push(n); });
  for (const light of lights) { light.getWorldPosition(light.position); light.removeFromParent(); keep.push(light); }
  const meshes = [];
  root.traverse(n => { if (n.isMesh) meshes.push(n); });
  for (const mesh of meshes) {
    const geometry = mesh.geometry;
    // The cave shell carries vertex colours and gets re-indexed by blasts, so
    // it stays its own mesh; anything without matching attributes does too.
    if (!geometry.attributes.uv || geometry.attributes.color) {
      mesh.matrixWorld.decompose(mesh.position, mesh.quaternion, mesh.scale);
      keep.push(mesh); continue;
    }
    const baked = geometry.clone();
    baked.applyMatrix4(mesh.matrixWorld);
    for (const name of Object.keys(baked.attributes)) {
      if (name !== 'position' && name !== 'normal' && name !== 'uv') baked.deleteAttribute(name);
    }
    if (!baked.attributes.normal) baked.computeVertexNormals();
    const list = byMaterial.get(mesh.material) ?? [];
    list.push(baked); byMaterial.set(mesh.material, list);
  }
  root.clear();
  for (const node of keep) { root.add(node); node.updateMatrix(); node.matrixAutoUpdate = false; }
  for (const [material, parts] of byMaterial) {
    const merged = parts.length === 1 ? parts[0] : mergeGeometries(parts);
    if (!merged) continue;
    if (parts.length > 1) for (const part of parts) part.dispose();
    const mesh = new THREE.Mesh(merged, material);
    mesh.matrixAutoUpdate = false; mesh.frustumCulled = false;
    root.add(mesh);
  }
}
mergeStatics(visual);

/* --------------------------------------------------- player and QA */
let worldOctree = null;
function rebuildCollision() {
  colliderRoot.updateMatrixWorld(true);
  worldOctree = new Octree().fromGraphNode(colliderRoot);
}
rebuildCollision();
const spawn = new V(0, 0, 18.4);
const playerCollider = new Capsule(new V(spawn.x, .35, spawn.z), new V(spawn.x, 1.65, spawn.z), .35);
const velocity = new V(); let playerOnFloor = false; let ghost = false; let lanternOn = true; let jumpQueued = false;
const controls = new PointerLockControls(camera, renderer.domElement);
camera.position.copy(playerCollider.end); scene.add(camera);
const handLamp = new THREE.SpotLight(0xffdca1, coarse ? 46 : 58, 20, Math.PI / 4.6, .68, 1.6);
handLamp.position.set(.16, -.08, .12); handLamp.target.position.set(0, -.12, -4); camera.add(handLamp, handLamp.target);
function resetPlayer(message = 'Back at Maw Camp') {
  playerCollider.start.set(spawn.x, .35, spawn.z); playerCollider.end.set(spawn.x, 1.65, spawn.z);
  velocity.set(0, 0, 0); camera.position.copy(playerCollider.end); toast(message);
}

/* ------------------------------------------------------------------ *
 * The mining loop
 *
 * drill a round -> buy powder -> charge the holes -> get clear -> fire ->
 * pick the ore out of what it opened -> sell it and buy more powder.
 * ------------------------------------------------------------------ */
const TOOLS = ['drill', 'charge', 'pick'];
const player = { credits: ECONOMY.startCredits, tnt: ECONOMY.startTnt, ore: 0, owed: 0, tool: 0 };
let fuseTimer = 0, shake = 0, useHeld = false, actionProgress = 0;

function toolName() { return TOOLS[player.tool]; }
function setTool(index) {
  player.tool = (index + TOOLS.length) % TOOLS.length;
  for (const [i, name] of TOOLS.entries()) $(`tool-${name}`).classList.toggle('on', i === player.tool);
}
function updateWallet() {
  $('credits').textContent = player.credits;
  $('tnt').textContent = player.tnt;
  $('ore').textContent = player.ore;
}

/** Add one drilled hole to a face. */
function addHole(face) {
  const [hx, hy] = HOLE_MARKS[face.holes];
  const holder = new THREE.Group();
  holder.position.copy(face.origin); holder.rotation.y = face.yaw;
  const hole = new THREE.Mesh(new THREE.CylinderGeometry(.055, .04, DRILL.depth, 8, 1, true), mats.black);
  hole.rotation.set(Math.PI / 2, 0, 0);
  hole.position.set(hx, hy, DRILL.depth / 2 - .3);
  holder.add(hole);
  // A ring of cuttings round the collar, where the drill spat them out.
  for (let k = 0; k < 5; k++) {
    const chip = new THREE.Mesh(new THREE.DodecahedronGeometry(.05 + (k % 3) * .02, 0), mats.darkRock);
    chip.position.set(hx + Math.cos(k * 1.9) * .17, hy + Math.sin(k * 1.9) * .17, -.3);
    holder.add(chip);
  }
  dynamic.add(holder);
  face.holeMeshes.push(holder);
  face.holes++;
  if (face.holes >= DRILL.holes) face.state = 'drilled';
}
/** Put a stick of powder in the next open hole. */
function addCharge(face) {
  const [hx, hy] = HOLE_MARKS[face.charges];
  const holder = new THREE.Group();
  holder.position.copy(face.origin); holder.rotation.y = face.yaw;
  const stick = new THREE.Mesh(new THREE.CylinderGeometry(.045, .045, .34, 8), mats.red);
  stick.rotation.set(Math.PI / 2, 0, 0); stick.position.set(hx, hy, -.18);
  holder.add(stick);
  holder.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
    new V(hx, hy, -.34), new V(hx + .12, hy - .3, -.46), new V(hx * .4, hy - .9, -.5),
  ]), 12, .012, 4, false), mats.fuse));
  dynamic.add(holder);
  face.holeMeshes.push(holder);
  face.charges++;
  if (face.charges >= face.holes) face.state = 'charged';
}

/**
 * EXTENSION POINT — everything the blast leaves behind.
 *
 * Right now this cuts a plain alcove into the rib, drops a muck pile at its
 * mouth and hangs a fixed number of ore nodes on the back wall. Procedural
 * generation replaces the body of this function: it owns the shape of the
 * new void, the spoil and where the ore ends up. The contract to keep is
 * only this — carve the shell, add and remove colliders, call
 * `rebuildCollision`, and push whatever is minable onto `face.oreNodes` as
 * interactables of kind `ore` carrying the face.
 */
function generateBlastResult(face) {
  const st = face.station, out = face.out;
  const mouth = face.origin.clone();
  const depth = BLAST.depth, half = BLAST.width / 2, top = BLAST.height;

  // Open the rock shell, so the drift actually gains the space.
  const opening = new THREE.Box3();
  for (const sx of [-1, 1]) for (const sy of [.15, top]) for (const d of [-.5, depth]) {
    opening.expandByPoint(mouth.clone()
      .addScaledVector(out, d)
      .addScaledVector(st.tangent, sx * half)
      .setY(sy));
  }
  carveShell(opening);

  // Alcove shell: floor, back, sides, roof. Local +z points into the rock.
  const alcove = new THREE.Group();
  alcove.position.copy(mouth); alcove.rotation.y = face.yaw; dynamic.add(alcove);
  const wall = (w, h, d, x, y, z) => {
    const mesh = new THREE.Mesh(worldUvBox(new THREE.BoxGeometry(w, h, d), w, h, d), mats.darkRock);
    mesh.position.set(x, y, z); alcove.add(mesh);
  };
  wall(BLAST.width, .4, depth + .8, 0, -.2, depth / 2);
  wall(BLAST.width + 1, top + .8, .5, 0, top / 2, depth + .25);
  for (const sx of [-1, 1]) wall(.5, top + .8, depth + .8, sx * (half + .25), top / 2, depth / 2);
  wall(BLAST.width + 1, .5, depth + .8, 0, top + .25, depth / 2);
  // Broken lip where the round tore the rib open.
  for (let k = 0; k < 10; k++) {
    const a = (k / 10) * Math.PI * 2;
    const lip = new THREE.Mesh(new THREE.DodecahedronGeometry(.2 + (k % 4) * .11, 0), mats.darkRock);
    lip.position.set(Math.cos(a) * (half + .05), top / 2 + Math.sin(a) * (top / 2), -.05);
    lip.scale.set(1.2, 1, .7); lip.rotation.set(k, k * .7, k * .3);
    alcove.add(lip);
  }
  // Muck pile: the rock the round threw back out into the drift.
  for (let k = 0; k < 12; k++) {
    const s = .18 + (k % 5) * .11;
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), k % 3 ? mats.darkRock : mats.rock);
    rock.scale.set(1.3, .62, 1.05);
    rock.position.set((k % 5 - 2) * .6 + (k % 2) * .2, s * .5, -.5 - (k % 4) * .38);
    rock.rotation.set(k * .3, k, k * .2);
    alcove.add(rock);
  }
  const muck = mouth.clone().addScaledVector(out, -1.0);
  colliderBox(BLAST.width, .5, 1.6, muck.x, .12, muck.z, face.yaw);

  // Ore exposed on the new back wall.
  alcove.updateMatrixWorld(true);
  for (let k = 0; k < face.nodes; k++) {
    const node = new THREE.Mesh(new THREE.DodecahedronGeometry(.24 + (k % 3) * .07, 0), mats[face.grade]);
    node.scale.set(1.2, .95, .5);
    node.position.set(((k * 5) % 7 - 3) * .42, .7 + ((k * 3) % 5) * .4, depth - .1);
    node.rotation.set(k * .4, k * .9, k * .2);
    alcove.add(node);
    node.updateMatrixWorld(true);
    face.oreNodes.push(addInteractable(node, 'ore', face));
  }
  const lit = new THREE.PointLight(face.grade === 'GLIMMER' ? 0x5fbfa6 : 0xffb066, 11, 8, 2);
  lit.position.copy(mouth).addScaledVector(out, depth * .5).setY(1.7);
  scene.add(lit);

  // The rib is open here now, so its collision has to go and the alcove's
  // has to take over.
  const step = stations[1].p.distanceTo(stations[0].p);
  const span = 1 + Math.ceil(half / step);
  for (const collider of [...colliderRoot.children]) {
    const rib = collider.userData.rib;
    if (!rib || rib.sign !== face.side) continue;
    if (Math.abs(rib.index - st.index) <= span) colliderRoot.remove(collider);
  }
  for (const sx of [-1, 1]) {
    const p = mouth.clone().addScaledVector(out, depth / 2).addScaledVector(st.tangent, sx * (half + .35));
    colliderBox(.7, top + 1.4, depth + .8, p.x, top / 2, p.z, face.yaw);
  }
  const back = mouth.clone().addScaledVector(out, depth + .35);
  colliderBox(BLAST.width + 1.4, top + 1.4, .7, back.x, top / 2, back.z, face.yaw);
  const floor = mouth.clone().addScaledVector(out, depth / 2);
  colliderBox(BLAST.width, .5, depth + .8, floor.x, -.25, floor.z, face.yaw);
  rebuildCollision();
}

function detonate() {
  if (fuseTimer > 0) return;
  if (!ORE_FACES.some(f => f.state === 'charged')) { toast('Nothing is charged'); return; }
  fuseTimer = BLAST.fuse;
  toast('Fuse lit — get clear');
}
function fireCharges() {
  let caught = false;
  for (const face of ORE_FACES) {
    if (face.state !== 'charged') continue;
    if (camera.position.distanceTo(face.origin) < BLAST.safeRadius) caught = true;
    for (const holder of face.holeMeshes) dynamic.remove(holder);
    face.holeMeshes.length = 0;
    // The chalked-up face is gone — that is the whole point of the round.
    face.art.removeFromParent();
    face.state = 'blasted';
    removeInteractable(face.target);
    generateBlastResult(face);
  }
  shake = 1;
  $('flash').animate([{ opacity: .5 }, { opacity: 0 }], { duration: 420, easing: 'ease-out' });
  if (caught) resetPlayer('You were too close. The mine wins.');
  else toast('Round fired — go and get the ore out');
}

const aimRay = new THREE.Raycaster();
const screenCentre = new THREE.Vector2(0, 0);

function findTarget() {
  // The aim ray reads the camera's world matrix, which the renderer would not
  // refresh until after this runs — update it here so the reticle never lags
  // a frame behind where you are actually looking.
  camera.updateMatrixWorld();
  aimRay.setFromCamera(screenCentre, camera);
  aimRay.far = DRILL.reach;
  const hits = aimRay.intersectObjects(interactables.map(entry => entry.object), false);
  if (!hits.length) return null;
  return interactables.find(e => e.object === hits[0].object) ?? null;
}
/** What the current tool can do to whatever you are looking at, if anything. */
function availableAction(hit) {
  if (!hit) return null;
  if (hit.kind === 'supply') {
    if (player.ore > 0) return { verb: 'SELL ORE', detail: `${player.ore} × ore · ${player.owed} cr`, instant: true, run: sellOre };
    if (player.credits >= ECONOMY.tntCost) return { verb: 'BUY POWDER', detail: `1 stick · ${ECONOMY.tntCost} cr`, instant: true, run: buyTnt };
    return { detail: `Powder is ${ECONOMY.tntCost} cr a stick. Go and sell some ore.` };
  }
  if (hit.kind === 'ore') {
    if (toolName() !== 'pick') return { detail: 'Ore. Switch to the pick.' };
    return { verb: 'MINE', detail: hit.ref.grade, seconds: PICK.seconds, run: () => mineNode(hit) };
  }
  if (hit.kind === 'face') {
    const face = hit.ref;
    if (toolName() === 'drill') {
      if (face.holes >= DRILL.holes) return { detail: 'Round is drilled. Charge it.' };
      return { verb: 'DRILL', detail: `hole ${face.holes + 1} of ${DRILL.holes}`, seconds: DRILL.seconds, run: () => addHole(face) };
    }
    if (toolName() === 'charge') {
      if (face.holes < DRILL.holes) return { detail: `Drill the round first (${face.holes}/${DRILL.holes})` };
      if (face.charges >= face.holes) return { detail: 'Charged. Press B and get clear.' };
      if (player.tnt <= 0) return { detail: 'No powder. Buy some at Maw Camp.' };
      return {
        verb: 'CHARGE', detail: `stick ${face.charges + 1} of ${face.holes}`, instant: true,
        run: () => { player.tnt--; addCharge(face); updateWallet(); },
      };
    }
    return { detail: `${face.label} · ${face.grade}` };
  }
  return null;
}
function buyTnt() { player.credits -= ECONOMY.tntCost; player.tnt++; updateWallet(); toast('One stick of powder'); }
function sellOre() {
  player.credits += player.owed;
  toast(`Sold ${player.ore} ore for ${player.owed} credits`);
  player.ore = 0; player.owed = 0; updateWallet();
}
function mineNode(hit) {
  const face = hit.ref;
  hit.object.removeFromParent();
  removeInteractable(hit.object);
  face.oreNodes = face.oreNodes.filter(n => n !== hit.object);
  player.ore++; player.owed += face.value;
  updateWallet();
  if (!face.oreNodes.length) { face.state = 'mined'; toast(`${face.label} is worked out`); }
}

function updateInteraction(dt) {
  const action = ghost ? null : availableAction(findTarget());
  const prompt = $('prompt');
  if (!action) { prompt.classList.remove('on'); actionProgress = 0; return; }
  prompt.classList.add('on');
  $('prompt-action').textContent = action.verb ? `${coarse ? 'USE' : 'E'} — ${action.verb}` : '';
  $('prompt-detail').textContent = action.detail ?? '';
  if (!action.verb) { $('bar-fill').style.width = '0%'; actionProgress = 0; return; }
  if (action.instant) {
    $('bar-fill').style.width = '0%';
    if (useHeld) { useHeld = false; action.run(); }
    return;
  }
  actionProgress = useHeld
    ? Math.min(1, actionProgress + dt / action.seconds)
    : Math.max(0, actionProgress - dt * 1.6);
  $('bar-fill').style.width = `${Math.round(actionProgress * 100)}%`;
  if (actionProgress >= 1) { actionProgress = 0; action.run(); }
}

/* ------------------------------------------------------------ input */
const keys = {};
addEventListener('keydown', event => {
  if (event.repeat) return;
  keys[event.code] = true;
  if (event.code === 'KeyE') useHeld = true;
  if (event.code === 'KeyB') detonate();
  if (event.code === 'KeyF') toggleLantern();
  if (event.code === 'KeyG') { ghost = !ghost; toast(ghost ? 'Ghost QA ON' : 'Collision ON'); if (!ghost) resetPlayer(); }
  if (event.code === 'KeyR') resetPlayer();
  if (event.code.startsWith('Digit')) {
    // Digits pick tools in play and jump to QA viewpoints in ghost mode, so
    // both fit on the number row without a modifier.
    const index = Number(event.code.slice(5)) - 1;
    if (ghost) { if (qaViews[index]) teleportQa(qaViews[index]); }
    else if (index < TOOLS.length) setTool(index);
  }
});
addEventListener('keyup', event => { keys[event.code] = false; if (event.code === 'KeyE') useHeld = false; });
function toggleLantern() {
  lanternOn = !lanternOn; handLamp.intensity = lanternOn ? (coarse ? 46 : 58) : 0;
  toast(lanternOn ? 'Hand lantern lit' : 'Hand lantern snuffed');
}

let yaw = 0, pitch = 0, looking = false, lastPointer = null;
const lookZone = $('look-zone');
lookZone.addEventListener('pointerdown', event => { looking = true; lastPointer = { x: event.clientX, y: event.clientY }; lookZone.setPointerCapture(event.pointerId); });
lookZone.addEventListener('pointermove', event => {
  if (!looking) return;
  const dx = event.clientX - lastPointer.x, dy = event.clientY - lastPointer.y;
  lastPointer = { x: event.clientX, y: event.clientY };
  yaw -= dx * .0042; pitch = clamp(pitch - dy * .0038, -1.25, 1.25); camera.rotation.set(pitch, yaw, 0);
});
lookZone.addEventListener('pointerup', () => { looking = false; });
const stick = $('stick'), knob = $('knob'); let joy = { x: 0, y: 0 };
function setJoy(event) {
  const rect = stick.getBoundingClientRect(), cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2, max = rect.width * .34;
  let dx = event.clientX - cx, dy = event.clientY - cy; const len = Math.hypot(dx, dy) || 1;
  if (len > max) { dx *= max / len; dy *= max / len; }
  joy = { x: dx / max, y: dy / max }; knob.style.transform = `translate(${dx}px,${dy}px)`;
}
stick.addEventListener('pointerdown', event => { stick.setPointerCapture(event.pointerId); setJoy(event); });
stick.addEventListener('pointermove', event => { if (stick.hasPointerCapture(event.pointerId)) setJoy(event); });
stick.addEventListener('pointerup', () => { joy = { x: 0, y: 0 }; knob.style.transform = 'translate(0,0)'; });
$('jump-button').addEventListener('pointerdown', () => jumpQueued = true);
$('lamp-button').addEventListener('pointerdown', toggleLantern);
$('blast-button').addEventListener('pointerdown', detonate);
$('tool-button').addEventListener('pointerdown', () => setTool(player.tool + 1));
$('use-button').addEventListener('pointerdown', () => useHeld = true);
$('use-button').addEventListener('pointerup', () => useHeld = false);
$('use-button').addEventListener('pointercancel', () => useHeld = false);
for (const [i, name] of TOOLS.entries()) $(`tool-${name}`).addEventListener('pointerdown', () => setTool(i));

/* ---------------------------------------------------------- movement */
const playerDirection = new V();
function getForward() { camera.getWorldDirection(playerDirection); playerDirection.y = 0; return playerDirection.normalize(); }
function getSide() { getForward(); return playerDirection.cross(camera.up).normalize(); }
function collisions() {
  playerOnFloor = false;
  for (let i = 0; i < 4; i++) {
    const result = worldOctree.capsuleIntersect(playerCollider);
    if (!result) break;
    playerOnFloor = playerOnFloor || result.normal.y > .35;
    playerCollider.translate(result.normal.clone().multiplyScalar(result.depth));
    if (result.normal.y > .35 && velocity.y < 0) velocity.y = 0;
    else velocity.addScaledVector(result.normal, -result.normal.dot(velocity));
  }
}
function movePlayer(dt) {
  const forward = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0) - joy.y;
  const side = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0) + joy.x;
  const sprint = keys.ShiftLeft || keys.ShiftRight;
  if (ghost) {
    const speed = (sprint ? 10 : 6) * dt;
    camera.position.addScaledVector(getForward(), forward * speed);
    camera.position.addScaledVector(getSide(), side * speed);
    if (keys.Space) camera.position.y += speed; if (keys.ControlLeft) camera.position.y -= speed;
    return;
  }
  const accel = playerOnFloor ? (sprint ? 29 : 21) : 8;
  if (forward) velocity.addScaledVector(getForward(), forward * accel * dt);
  if (side) velocity.addScaledVector(getSide(), side * accel * dt);
  if ((keys.Space || jumpQueued) && playerOnFloor) velocity.y = 5.55;
  jumpQueued = false;
  let damping = Math.exp(-8 * dt) - 1;
  if (!playerOnFloor) { velocity.y -= 19 * dt; damping *= .12; }
  velocity.addScaledVector(velocity, damping);
  playerCollider.translate(velocity.clone().multiplyScalar(dt));
  collisions();
  camera.position.copy(playerCollider.end);
  if (camera.position.y < -5.8) resetPlayer('The shaft wins. Back to camp.');
}

const zones = [
  ['MAW CAMP', 0, 19, 'Buy powder at the store, then drill a marked face.'],
  ['CROOKED RAIL', 0, 8, 'A copper seam is chalked up on the rib.'],
  ['BLACKSHAFT', 0, -10, 'Cross the deck. Do not step off the deck.'],
  ['DROWNED POCKET', 5.5, -29, 'Keep to the trestle over the sump.'],
  ['SAINT GLIMMER', 3.5, -38, 'The rich seam. Someone marked it and left.'],
  ['POWDERWORKS', .5, -45, 'Powder, sparks and a very bad idea.'],
  ["FOREMAN'S VAULT", -6, -55, 'The ledger is behind the iron gate.'],
];
function updateZone() {
  let nearest = zones[0], distance = Infinity;
  for (const zone of zones) {
    const d = (camera.position.x - zone[1]) ** 2 + (camera.position.z - zone[2]) ** 2;
    if (d < distance) { distance = d; nearest = zone; }
  }
  $('zone').textContent = nearest[0]; $('objective').textContent = nearest[3];
}
const qaViews = [
  { p: [0, 1.65, 18.4], r: [0, 0, 0] }, { p: [0, 1.65, 11], r: [0, 0, 0] }, { p: [0, 1.75, 3], r: [0, 0, 0] },
  { p: [0, 1.85, -4], r: [0, 0, 0] }, { p: [0, 1.75, -10], r: [0, 0, 0] }, { p: [4, 1.75, -24], r: [0, 0, 0] },
  { p: [5, 1.8, -36], r: [0, 0, 0] }, { p: [1, 1.75, -45], r: [0, 0, 0] }, { p: [-6, 1.8, -53], r: [0, 0, 0] },
];
function teleportQa(view) { camera.position.set(...view.p); camera.rotation.set(...view.r); toast('QA viewpoint · ghost mode'); }

const clock = new THREE.Clock();
function toast(message) {
  const element = $('toast'); element.textContent = message; element.style.opacity = 1;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => element.style.opacity = 0, 1600);
}
function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), .033), t = clock.elapsedTime;
  movePlayer(dt);
  updateZone();
  updateInteraction(dt);
  if (fuseTimer > 0) {
    fuseTimer -= dt;
    $('fuse').classList.add('on');
    $('fuse').textContent = `FIRE IN THE HOLE — ${Math.max(0, Math.ceil(fuseTimer))}`;
    if (fuseTimer <= 0) { fuseTimer = 0; $('fuse').classList.remove('on'); fireCharges(); }
  }
  if (shake > 0) {
    shake = Math.max(0, shake - dt * 1.6);
    camera.position.x += Math.sin(t * 61) * shake * .07;
    camera.position.y += Math.sin(t * 47) * shake * .05;
  }
  for (const lamp of lampLights) lamp.light.intensity = lamp.base * (1 + Math.sin(t * 5.5 + lamp.phase) * .05);
  renderer.render(scene, camera);
}

setTool(0); updateWallet();
const start = $('start');
$('enter').addEventListener('click', () => { start.style.display = 'none'; if (!coarse) controls.lock(); });
renderer.domElement.addEventListener('click', () => { if (start.style.display === 'none' && !coarse) controls.lock(); });
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 1.6));
});
frame();
