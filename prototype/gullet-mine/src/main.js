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

const visual = new THREE.Group();
// Collision proxies are never drawn, so they stay out of the scene graph
// entirely; the Octree only needs their world matrices.
const colliderRoot = new THREE.Group();
const colliderMaterial = new THREE.MeshBasicMaterial({ visible: false });
scene.add(visual);

/* ------------------------------------------------------------------ *
 * Surfaces
 *
 * Every texture is painted once into a canvas and tiled in *metres*: the
 * UVs of each primitive are rescaled by its real size (see `worldUv`), so
 * a sleeper and a roof beam carved from the same timber read at the same
 * grain. Without that step every box samples 0..1 across its own face and
 * the whole mine looks like flat plastic.
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
// Spoil underfoot: crushed rock trodden into mud. Deliberately free of any
// long directional stroke — the first pass looked like floorboards.
const earthTexture = canvasTexture(512, (ctx, s) => {
  ctx.fillStyle = '#585448'; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 16; i++) {
      c.fillStyle = i % 2 ? 'rgba(96, 90, 74, .11)' : 'rgba(44, 42, 35, .12)';
      c.beginPath(); c.ellipse((i * 137) % s, (i * 101) % s, 22 + (i % 4) * 14, 17 + (i % 3) * 11, i, 0, Math.PI * 2); c.fill();
    }
    // Loose stone, the size a boot would kick aside.
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
  g.addColorStop(0, '#8c6a4a'); g.addColorStop(.42, '#6d4f37'); g.addColorStop(1, '#96755209');
  ctx.fillStyle = '#7a5a3e'; ctx.fillRect(0, 0, s, s);
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  tiled(ctx, s, c => {
    for (let i = 0; i < 26; i++) {
      c.strokeStyle = `rgba(42, 27, 17, ${.20 + i % 3 * .07})`; c.lineWidth = 1 + i % 3;
      c.beginPath(); c.moveTo(-10, i * 21 + 5);
      c.bezierCurveTo(s * .3, i * 21 - 7, s * .7, i * 21 + 12, s + 10, i * 21 + 3); c.stroke();
    }
    // Saw ends and splits, so the grain has somewhere to start and stop.
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
    // Rust blooms, so the ironwork looks like it has been down here a while.
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
  ironDark: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x3c4644, metalness: .6, roughness: .52 }),
  rope: new THREE.MeshStandardMaterial({ color: 0x8a7048, roughness: 1 }),
  gold: new THREE.MeshStandardMaterial({ color: 0xd8a24a, metalness: .55, roughness: .34 }),
  red: new THREE.MeshStandardMaterial({ color: 0x9c4433, roughness: .84 }),
  // Ore reads as mineral, not neon: colour and a low emissive lift, so a
  // lantern still has to find it rather than the seam lighting the room.
  crystal: new THREE.MeshStandardMaterial({ color: 0x2f7f6f, emissive: 0x0a2a24, emissiveIntensity: .35, roughness: .34, metalness: .15 }),
  crystalBlue: new THREE.MeshStandardMaterial({ color: 0x2e6f80, emissive: 0x08222a, emissiveIntensity: .35, roughness: .38 }),
  vein: new THREE.MeshStandardMaterial({ color: 0x27675a, emissive: 0x08231d, emissiveIntensity: .3, roughness: .55, metalness: .1 }),
  water: new THREE.MeshStandardMaterial({ color: 0x1d4d4e, roughness: .16, metalness: .3, transparent: true, opacity: .78 }),
  black: new THREE.MeshBasicMaterial({ color: 0x05100f }),
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
 * One spline through seven authored rooms. Every wall, floor, collider,
 * timber set, lamp and sign below is placed from this curve rather than
 * from hand-typed coordinates, which is what keeps props out of the rock.
 * ------------------------------------------------------------------ */
const NODES = [
  { x: 0, z: 27, w: 3.6, h: 4.4 },   // portal back to the plant
  { x: 0, z: 21, w: 3.6, h: 4.4 },   // Maw Camp
  { x: 0, z: 16, w: 3.4, h: 4.2 },
  { x: 0, z: 10, w: 2.9, h: 3.7 },
  { x: 0, z: 4, w: 2.7, h: 3.5 },    // Crooked Rail
  { x: 0, z: -3, w: 2.7, h: 3.5 },
  { x: 0, z: -9, w: 3.5, h: 4.4 },
  { x: 0, z: -17, w: 4.3, h: 5.8 },  // Blackshaft
  { x: 0, z: -24.5, w: 3.9, h: 4.9 },
  { x: 5, z: -29, w: 4.2, h: 4.8 },
  { x: 9.5, z: -34, w: 4.7, h: 4.9 },// Drowned Pocket
  { x: 9.5, z: -42, w: 4.7, h: 4.9 },
  { x: 6, z: -49, w: 4.6, h: 4.8 },  // Saint Glimmer
  { x: 2, z: -56, w: 3.5, h: 4.1 },  // Powderworks
  { x: -1, z: -62, w: 3.6, h: 4.2 },
  { x: -8, z: -68, w: 4.1, h: 4.6 }, // Foreman's Vault
  { x: -9, z: -76, w: 4.2, h: 4.6 },
];
const pathCurve = new THREE.CatmullRomCurve3(NODES.map(n => new V(n.x, 0, n.z)), false, 'catmullrom', .32);
const widths = NODES.map(n => n.w), heights = NODES.map(n => n.h);
function profile(t, list) {
  const q = clamp(t, 0, 1) * (list.length - 1), i = Math.min(Math.floor(q), list.length - 2), f = q - i;
  return THREE.MathUtils.lerp(list[i], list[i + 1], f);
}

// Blackshaft and the sump are holes in the floor, so both the rendered
// invert and the floor colliders have to know about them.
const SHAFT = { z0: -10.9, z1: -23.1 };
const SUMP = { z0: -27.6, z1: -45.2 };
const inShaftZ = z => z < SHAFT.z0 && z > SHAFT.z1;
const inSumpZ = z => z < SUMP.z0 && z > SUMP.z1;
/** How far the rock invert drops below the walking surface. */
function invertAt(z) {
  if (!inSumpZ(z)) return .34;
  const edge = Math.min(Math.abs(z - SUMP.z0), Math.abs(z - SUMP.z1));
  return .34 + clamp(edge / 3.2, 0, 1) * .78;
}

const SEGMENTS = 176;
const stations = [];
for (let i = 0; i <= SEGMENTS; i++) {
  const t = i / SEGMENTS;
  const p = pathCurve.getPointAt(t);
  const tangent = pathCurve.getTangentAt(t).setY(0).normalize();
  stations.push({
    t, p, tangent,
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
 * Where the rock actually is. The shell is displaced by its own roughness,
 * so the nominal half-width is up to a foot out — everything that has to
 * touch the wall asks the mesh instead of trusting the number.
 */
let shellMesh = null;
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

/**
 * Cross-section of the drift: flat invert, near-vertical ribs, arched back.
 * `n` below 1 squares the ellipse off into the horseshoe a drill-and-blast
 * heading actually leaves behind. Returns the lateral offset and height.
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
function buildCaveShell() {
  const positions = [], colors = [], uvs = [], indices = [], tint = new THREE.Color();
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
      // bulges and shelves the eye can read as form, then chisel-scale grain.
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
      const a = i * (RING + 1) + j, b = a + RING + 1;
      indices.push(a, b, a + 1, a + 1, b, b + 1);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  shellMesh = new THREE.Mesh(geometry, mats.cave); visual.add(shellMesh);
}

/** Rock plug at each end of the drift, so the route never opens onto the void. */
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

/**
 * The walked surface: packed spoil laid over the invert. Wound so its normal
 * points up — the previous build had this inverted, which is why the floor
 * was invisible and the mine appeared to be floating over a void.
 */
function buildFloor() {
  const positions = [], uvs = [], indices = [];
  let run = 0;
  for (let i = 0; i <= SEGMENTS; i++) {
    const st = stations[i];
    if (i > 0) run += st.p.distanceTo(stations[i - 1].p);
    const half = st.width * .86;
    const left = st.p.clone().addScaledVector(st.side, -half), right = st.p.clone().addScaledVector(st.side, half);
    left.y = right.y = 0;
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

/** Standing water in the sump, filling the drift rib to rib. */
function buildWater() {
  const positions = [], uvs = [], indices = [];
  const range = stations.filter(s => inSumpZ(s.p.z));
  range.forEach((st, i) => {
    const half = st.width * .99;
    const left = st.p.clone().addScaledVector(st.side, -half), right = st.p.clone().addScaledVector(st.side, half);
    positions.push(left.x, .10, left.z, right.x, .10, right.z);
    uvs.push(0, i * .5, 2, i * .5);
  });
  for (let i = 0; i < range.length - 1; i++) { const a = i * 2; indices.push(a, a + 1, a + 2, a + 2, a + 1, a + 3); }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  const mesh = new THREE.Mesh(geometry, mats.water); mesh.renderOrder = 2; visual.add(mesh);
}

buildCaveShell(); capEnd(0, 1.6); capEnd(SEGMENTS, -1.6); buildFloor(); buildWater();

/* --------------------------------------------------------- collision */
// Simplified proxies generated from the same stations as the art, so what
// you can see and what you can walk into never disagree.
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
    colliderBox(.7, height + 2.4, length, p.x, height / 2, p.z, a.yaw);
  }
}

/* ------------------------------------------------------------------ *
 * Rail
 *
 * One 900 mm tramway, bedded on sleepers, running the drift from Maw Camp
 * to the lip of Blackshaft where the shaft cut it, with a buffer stop at
 * the break and a stranded stub on the far side. It follows the route
 * spline, so it curves with the drift instead of ignoring it.
 * ------------------------------------------------------------------ */
const GAUGE = .9, RAIL_TOP = .18;
function railRun(z0, z1) {
  const run = stations.filter(s => s.p.z <= z0 && s.p.z >= z1);
  if (run.length < 2) return null;
  // Sleepers first: the rail has to be seen to be sitting on something.
  let carried = 0;
  for (let i = 0; i < run.length - 1; i++) {
    carried += run[i].p.distanceTo(run[i + 1].p);
    if (carried < .72) continue;
    carried = 0;
    box(GAUGE + .62, .14, .22, mats.woodDark, run[i].p.x, .05, run[i].p.z, run[i].yaw);
  }
  for (const sign of [-1, 1]) {
    const points = run.map(s => {
      const p = s.p.clone().addScaledVector(s.side, sign * GAUGE / 2); p.y = RAIL_TOP - .05; return p;
    });
    const curve = new THREE.CatmullRomCurve3(points, false, 'catmullrom', .2);
    const geometry = new THREE.TubeGeometry(curve, points.length * 2, .05, 4, false);
    const rail = new THREE.Mesh(geometry, mats.railHead); rail.rotation.y = 0; visual.add(rail);
  }
  return { head: run[0], tail: run[run.length - 1] };
}
function bufferStop(station, facing) {
  const p = station.p;
  for (const sign of [-1, 1]) {
    const post = p.clone().addScaledVector(station.side, sign * GAUGE / 2);
    box(.26, .95, .3, mats.woodDark, post.x, .42, post.z, station.yaw);
  }
  box(GAUGE + .7, .34, .28, mats.wood, p.x, .78, p.z, station.yaw);
  box(GAUGE + .5, .14, .5, mats.ironDark, p.x, .30, p.z + facing * .34, station.yaw);
  colliderBox(GAUGE + .7, 1.0, .5, p.x, .5, p.z, station.yaw);
}
railRun(25.2, SHAFT.z0 + .9);
bufferStop(stationAtZ(SHAFT.z0 + 1.0), -1);
railRun(SHAFT.z1 - .8, -27.4);

/* ------------------------------------------------------------------ *
 * Timber
 *
 * Each set is sized from the drift at its own station: feet on the invert,
 * posts inside the rib, cap beam tucked under the back. Nothing is typed
 * in by hand, so nothing pushes through the rock.
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
const timberSets = [
  timberSet(24.6, { inset: .4 }), timberSet(18.2), timberSet(13.4, { damaged: true }),
  timberSet(9.2), timberSet(5.0), timberSet(.6, { damaged: true }), timberSet(-4.2),
  timberSet(-8.2, { inset: .4 }),
];

/* ------------------------------------------------------------------ *
 * Practical lights
 *
 * A handful of real point lights carry the route; everything else is an
 * emissive flame with no light attached. The eye reads the fixture, the
 * GPU only pays for the ones that change the shape of a room.
 * ------------------------------------------------------------------ */
const lampLights = [];
// Shared per colour so every fixture in the mine still merges into two draws.
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
  // Glass shade, emissive whether or not a real light is attached: a fixture
  // has to read as lit from across the room without costing a point light.
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
  const p = ribPoint(st, sideSign, .18, height);
  const yaw = Math.atan2(-st.side.x * sideSign, -st.side.z * sideSign);
  return lampFixture(p, yaw, options);
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
  // Hanger from the lamp ring back up into the cap beam it is nailed to.
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
/** An ore cart, sitting on the rail at the station you give it. */
function cart(z, { loaded = true, spin = 0, offRail = 0 } = {}) {
  const st = stationAtZ(z);
  const p = st.p.clone().addScaledVector(st.side, offRail);
  const group = new THREE.Group(); group.position.copy(p); group.rotation.y = st.yaw + spin; visual.add(group);
  for (const x of [-GAUGE / 2, GAUGE / 2]) for (const z0 of [-.52, .52]) {
    cyl(.2, .2, .09, 12, mats.ironDark, x, RAIL_TOP + .2, z0, 0, 0, Math.PI / 2, group);
    cyl(.25, .25, .03, 12, mats.metal, x + (x < 0 ? -.05 : .05), RAIL_TOP + .2, z0, 0, 0, Math.PI / 2, group);
  }
  box(GAUGE + .34, .12, 1.42, mats.ironDark, 0, RAIL_TOP + .44, 0, 0, 0, 0, group);
  box(1.16, .58, 1.3, mats.ironDark, 0, RAIL_TOP + .78, 0, 0, 0, 0, group);
  box(1.22, .07, 1.36, mats.metal, 0, RAIL_TOP + 1.08, 0, 0, 0, 0, group);
  if (loaded) {
    for (const [ox, oz, s, mat] of [[-.24, -.18, .34, mats.rock], [.2, .16, .27, mats.darkRock], [0, -.02, .22, mats.crystal]]) {
      const ore = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), mat);
      ore.scale.set(1.3, .6, .95); ore.position.set(ox, RAIL_TOP + 1.12, oz); ore.rotation.set(.2, ox * 3, .1); group.add(ore);
    }
  }
  colliderBox(1.3, 1.35, 1.5, p.x, .68, p.z, st.yaw + spin);
  return group;
}
/** A plank walkway laid between two route stations. */
function boardwalk(z0, z1, width = 2.2, y = .3) {
  const run = stations.filter(s => s.p.z <= z0 && s.p.z >= z1);
  for (let i = 0; i < run.length - 1; i++) {
    const a = run[i], b = run[i + 1];
    const mid = a.p.clone().add(b.p).multiplyScalar(.5), length = a.p.distanceTo(b.p) + .1;
    box(width, .12, length, mats.woodDark, mid.x, y, mid.z, a.yaw);
    colliderBox(width, .3, length, mid.x, y - .06, mid.z, a.yaw);
    if (i % 3 === 0) {
      for (const sign of [-1, 1]) {
        const post = mid.clone().addScaledVector(a.side, sign * (width / 2 - .12));
        beamBetween(new V(post.x, y - .1, post.z), new V(post.x, -invertAt(mid.z), post.z), .07, mats.woodDark);
        beamBetween(new V(post.x, y + .9, post.z), new V(post.x, y, post.z), .05, mats.metal);
      }
    }
  }
  // A single continuous handrail reads better than a row of disconnected posts.
  for (const sign of [-1, 1]) {
    const points = run.map(s => s.p.clone().addScaledVector(s.side, sign * (width / 2 - .12)).setY(y + .9));
    if (points.length < 2) continue;
    const rail = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), points.length * 2, .045, 5, false), mats.metal);
    visual.add(rail);
  }
}

/* ------------------------------------------------------- Maw Camp */
capLamp(timberSets[0], { color: 0xffcf8a, range: 14, power: 24 });
// The way back to the plant: a timbered portal with a dark stepped drift
// behind it, so the mine has an entrance rather than a sealed end.
const portal = stationAtZ(25.6);
box(2.1, 2.7, .5, mats.black, portal.p.x, 1.35, portal.p.z + .35);
for (const sign of [-1, 1]) box(.32, 2.9, .38, mats.woodDark, portal.p.x + sign * 1.2, 1.45, portal.p.z + .1);
box(3.1, .34, .42, mats.wood, portal.p.x, 3.05, portal.p.z + .1);
box(3.1, .16, .3, mats.woodDark, portal.p.x, 2.78, portal.p.z + .18);
// Hung off the portal timber set's cap beam, facing whoever walks in.
const campSign = signBoard('MAW CAMP', 'STAGING / SHIFT 03', '#e9b35a', 1.05);
campSign.position.set(timberSets[0].st.p.x, timberSets[0].capY - .52, timberSets[0].st.p.z - .3);
campSign.rotation.y = Math.PI;
for (const sx of [-.7, .7]) beamBetween(
  new V(campSign.position.x + sx, timberSets[0].capY - .1, campSign.position.z + .12),
  new V(campSign.position.x + sx, campSign.position.y, campSign.position.z + .02), .022, mats.ironDark);

crate(22.4, -1, .55, { scale: 1.05, spin: .16, label: 'LAMP OIL' });
crate(23.5, -1, .5, { scale: .78, spin: -.2 });
crate(22.8, -1, 1.5, { scale: .7, spin: .35 });
barrel(21.4, 1, .5); barrel(22.5, 1, .66, { scale: .84 });
ropeCoil(23.6, 1, .8, 1.1);
cart(19.6, { loaded: true });
cart(24.2, { loaded: false, spin: .04 });
// Shift board, standing against the rib where a crew would actually read it.
const boardSt = stationAtZ(19.4), boardAt = ribPoint(boardSt, -1, .5, 0);
box(1.6, .1, .74, mats.woodDark, boardAt.x, .92, boardAt.z, boardSt.yaw);
box(1.44, .06, .62, mats.paper, boardAt.x, .98, boardAt.z, boardSt.yaw);
for (const sign of [-1, 1]) box(.1, .92, .1, mats.woodDark, boardAt.x + sign * .6, .46, boardAt.z, boardSt.yaw);
ribLamp(20.4, -1, 2.5, { color: 0xffc26a, range: 14, power: 22 });
ribLamp(23.4, 1, 2.4, { color: 0xffbd65, real: false });

/* ---------------------------------------------------- Crooked Rail */
capLamp(timberSets[2], { color: 0xffc26a, real: false });
ribLamp(11.2, 1, 2.3, { color: 0x9ad9c4, real: false });
capLamp(timberSets[4], { color: 0xffb35d, range: 11, power: 18 });
ribLamp(2.4, 1, 2.2, { color: 0x9fd6df, real: false });
capLamp(timberSets[6], { color: 0xffb35d, range: 12, power: 20 });
// Tools left leaning on the rib: the reason the drift looks worked, not grown.
const toolSt = stationAtZ(6.4), toolAt = ribPoint(toolSt, -1, .3, 0);
const toolHead = new V(toolAt.x + .34, 1.2, toolAt.z + .16);
beamBetween(new V(toolAt.x, .02, toolAt.z), toolHead, .028, mats.wood);
box(.34, .06, .07, mats.ironDark, toolHead.x, toolHead.y, toolHead.z, 0, .34);
const shovel = new V(toolAt.x + .5, 1.1, toolAt.z - .34);
beamBetween(new V(toolAt.x + .16, .02, toolAt.z - .3), shovel, .026, mats.wood);
box(.24, .3, .04, mats.metal, toolAt.x + .1, .16, toolAt.z - .32, 0, .3);
barrel(7.6, -1, .5, { scale: .78 });
// An exposed ore seam in the rib, mined at and abandoned.
for (const [z, sideSign, len] of [[3.2, 1, 2.4], [-2.4, -1, 1.9]]) {
  const st = stationAtZ(z), anchor = ribPoint(st, sideSign, .12, 1.5);
  const points = [];
  for (let k = 0; k <= 5; k++) {
    const s2 = stationAtZ(z + (k / 5 - .5) * len), p = ribPoint(s2, sideSign, .1 + Math.sin(k * 1.7) * .06, 1.5 + Math.sin(k * 2.1) * .55);
    points.push(p);
  }
  const seam = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 22, .06, 5, false), mats.vein);
  visual.add(seam);
  box(.7, .5, .5, mats.darkRock, anchor.x, .25, anchor.z, st.yaw);
}

/* ---------------------------------------------------- Blackshaft */
// A real hole, rib to rib, crossed by one narrow deck. Stepping off is fatal.
const shaftMid = stationAtZ((SHAFT.z0 + SHAFT.z1) / 2);
const shaftHalf = shaftMid.width, shaftLen = SHAFT.z0 - SHAFT.z1, shaftDepth = 7.6;
for (const sign of [-1, 1]) box(.6, shaftDepth, shaftLen + 1.2, mats.darkRock, shaftMid.p.x + sign * (shaftHalf + .25), -shaftDepth / 2, shaftMid.p.z);
for (const z of [SHAFT.z0 + .3, SHAFT.z1 - .3]) box(shaftHalf * 2 + 1.2, shaftDepth, .6, mats.darkRock, shaftMid.p.x, -shaftDepth / 2, z);
box(shaftHalf * 2, .3, shaftLen, mats.darkRock, shaftMid.p.x, -shaftDepth - .15, shaftMid.p.z);
box(shaftHalf * 1.4, .06, shaftLen * .5, mats.water, shaftMid.p.x, -shaftDepth + .04, shaftMid.p.z + 1.2);
// Shaft timbering: corner posts and the old hoist ropes running to the bottom.
for (const sx of [-1, 1]) for (const sz of [SHAFT.z0 - .5, SHAFT.z1 + .5]) {
  const x = shaftMid.p.x + sx * (shaftHalf - .45);
  box(.42, shaftDepth, .42, mats.woodDark, x, -shaftDepth / 2 + .3, sz);
  beamBetween(new V(x, .1, sz), new V(x, -shaftDepth + .2, sz), .05, mats.rope);
}
for (let d = 1.6; d < shaftDepth; d += 2.1) {
  for (const sz of [SHAFT.z0 - .5, SHAFT.z1 + .5]) {
    box(shaftHalf * 2 - .9, .26, .3, mats.woodDark, shaftMid.p.x, -d, sz);
  }
}
// Two eerie lights on a broken staging far below, for depth.
box(2.6, .16, 3.4, mats.woodDark, shaftMid.p.x - 1.1, -shaftDepth + .9, shaftMid.p.z - 1.6, 0, 0, .12);
lampFixture(new V(shaftMid.p.x - 1.1, -shaftDepth + 1.9, shaftMid.p.z - 1.6), 0, { color: 0x6fc9cf, range: 9, power: 14 });
lampFixture(new V(shaftMid.p.x + 2.2, -shaftDepth + 1.3, shaftMid.p.z + 3.1), 0, { color: 0x74c7bd, real: false });

// The crossing: a 2.2 m deck laid flush with the drift floor and carried on
// bearers across the shaft. Flush means no ramps, no step and no seam for the
// capsule to catch on — you walk straight out over the hole.
const bridgeWidth = 2.2;
const deckZ0 = SHAFT.z0 + .9, deckZ1 = SHAFT.z1 - .9, deckMid = (deckZ0 + deckZ1) / 2, deckLen = deckZ0 - deckZ1;
for (const x of [-.82, .82]) box(.22, .3, deckLen, mats.woodDark, x, -.24, deckMid);
box(bridgeWidth, .18, deckLen, mats.wood, 0, 0, deckMid);
colliderBox(bridgeWidth, .34, deckLen, 0, -.12, deckMid);
for (let z = deckZ0 - .55; z > deckZ1; z -= 1.05) box(bridgeWidth + .26, .07, .2, mats.woodDark, 0, .12, z);
for (const sign of [-1, 1]) {
  const x = sign * (bridgeWidth / 2 - .14);
  for (let z = deckZ0 - .5; z > deckZ1; z -= 2.4) box(.12, 1.0, .14, mats.ironDark, x, .58, z);
  const railPoints = [new V(x, 1.0, deckZ0 - .5), new V(x, 1.04, deckMid), new V(x, 1.0, deckZ1 + .5)];
  visual.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(railPoints), 18, .045, 5, false), mats.metal));
  colliderBox(.16, 1.1, deckLen, x, .6, deckMid);
}
// Hoist at the shaft head: a hand winch on a trestle, its rope running over
// the lip to the bottom. Both legs stand on the drift floor.
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
ribLamp(SHAFT.z1 - .4, 1, 2.6, { color: 0x76cbd0, range: 15, power: 28 });
const shaftSign = signBoard('BLACKSHAFT', 'BRIDGE ONLY // WATCH YOUR STEP', '#d98352', .95);
shaftSign.position.set(0, 2.5, SHAFT.z0 + 2.1);

/* -------------------------------------------------- Drowned Pocket */
boardwalk(SUMP.z0 + 1.6, SUMP.z1 - 1.4, 2.2, .34);
// A pump on a repaired staging, the reason the route is passable at all.
const pumpSt = stationAtZ(-33.5), pumpAt = ribPoint(pumpSt, 1, 1.5, .3);
box(2.6, .16, 3.6, mats.woodDark, pumpAt.x, .3, pumpAt.z, pumpSt.yaw);
colliderBox(2.6, .3, 3.6, pumpAt.x, .26, pumpAt.z, pumpSt.yaw);
const pump = new THREE.Group(); pump.position.copy(pumpAt); pump.rotation.y = pumpSt.yaw; visual.add(pump);
box(.95, 1.25, .8, mats.metal, 0, 1.0, 0, 0, 0, 0, pump);
cyl(.55, .55, .12, 16, mats.metal, .1, 1.6, 0, 0, 0, Math.PI / 2, pump);
cyl(.09, .09, 1.5, 8, mats.wood, .1, 1.6, 0, 0, 0, Math.PI / 2, pump);
colliderBox(1.0, 1.6, .9, pumpAt.x, .8, pumpAt.z, pumpSt.yaw);
// Suction hose into the water: the pump has to be connected to something.
const hose = new THREE.CatmullRomCurve3([
  pumpAt.clone().setY(1.2), pumpAt.clone().addScaledVector(pumpSt.side, -1.3).setY(.75),
  pumpAt.clone().addScaledVector(pumpSt.side, -3.0).setY(.05),
]);
visual.add(new THREE.Mesh(new THREE.TubeGeometry(hose, 20, .08, 6, false), mats.ironDark));
// Collapsed timber, one end still on the rib and the other under the water.
const wreckSt = stationAtZ(-40.5), wreckAt = ribPoint(wreckSt, 1, .35, 0);
beamBetween(new V(wreckAt.x, 2.2, wreckAt.z - 1.4), new V(wreckAt.x - 2.4, -.55, wreckAt.z + .8), .16, mats.woodDark);
beamBetween(new V(wreckAt.x, 1.7, wreckAt.z + .6), new V(wreckAt.x - 1.6, -.45, wreckAt.z + 2.0), .13, mats.woodDark);
beamBetween(new V(wreckAt.x - .3, 1.95, wreckAt.z - .5), new V(wreckAt.x - 1.9, 1.1, wreckAt.z + 1.4), .09, mats.wood);
ribLamp(-29.5, -1, 2.7, { color: 0x83d0d0, range: 15, power: 26 });
ribLamp(-36, 1, 2.6, { color: 0x7ed1d0, range: 14, power: 24 });
ribLamp(-43, -1, 2.6, { color: 0x7ed1d0, real: false });
ribSign(-28.6, 1, 2.4, 'DROWNED POCKET', 'PUMP BATTERY // KEEP TO THE WALK', '#79c8c0');

/* ------------------------------------------------- Saint Glimmer *
 * The hero deposit. One authored cluster of matrix lobes bolted to the
 * real rib, with the seam branching through the cracks between them and
 * the scars of the crew who found it. Not a gem forest.
 * ---------------------------------------------------------------- */
const glimmerSt = stationAtZ(-48);
const glimmer = new THREE.Group();
// Anchor on the chord of the rib the cluster spans, not on one station: the
// drift is turning here, and a rigid group hung off a single point ends up
// out over the water. Local +X runs along the wall, +Z out into the drift.
const glimmerA = ribPoint(stationAtZ(-45.7), 1, 0, 1.8);
const glimmerB = ribPoint(stationAtZ(-50.3), 1, 0, 1.8);
glimmer.position.copy(glimmerA).add(glimmerB).multiplyScalar(.5).setY(0);
glimmer.rotation.y = Math.atan2(-glimmerSt.side.x, -glimmerSt.side.z);
visual.add(glimmer);
/**
 * A boss of host rock standing out of the rib. Deep enough to have a lit top
 * and a shadowed underside — the flat version of this read as a paper cutout
 * stuck to the wall rather than as rock the crew had been cutting into.
 */
function rockLobe(x, y, sx, sy, rotation = 0, material = mats.matrix, out = .38) {
  const sides = 11, outline = [];
  for (let i = 0; i < sides; i++) {
    const a = (i / sides) * Math.PI * 2, r = .72 + ((i * 5) % 4) * .1;
    outline.push([Math.cos(a) * r, Math.sin(a) * r]);
  }
  const front = [], back = [], c = Math.cos(rotation), s = Math.sin(rotation);
  outline.forEach((point, i) => {
    const px = x + (point[0] * c - point[1] * s) * sx, py = y + (point[0] * s + point[1] * c) * sy;
    front.push(new V(px, py, out * (.42 + (i % 3) * .16))); back.push(new V(px, py, -.9));
  });
  const vertices = [...front, new V(x, y, out), ...back, new V(x, y, -.9)], index = [];
  const frontCenter = outline.length, backStart = frontCenter + 1, backCenter = backStart + outline.length;
  for (let i = 0; i < outline.length; i++) {
    const next = (i + 1) % outline.length;
    index.push(frontCenter, i, next, i, backStart + i, backStart + next, i, backStart + next, next);
    index.push(backCenter, backStart + next, backStart + i);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices.flatMap(v => [v.x, v.y, v.z]), 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(vertices.flatMap(v => [v.x / TILE, v.y / TILE]), 2));
  geometry.setIndex(index); geometry.computeVertexNormals();
  const mesh = new THREE.Mesh(geometry, material); glimmer.add(mesh); return mesh;
}
function seamTube(points, radius = .045) {
  const curve = new THREE.CatmullRomCurve3(points.map(([x, y, z]) => new V(x, y, z)));
  glimmer.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 20, radius, 5, false), mats.vein));
}
function facet(x, y, z, scale, material = mats.crystal, spin = 0) {
  const mesh = new THREE.Mesh(new THREE.DodecahedronGeometry(1, 0), material);
  mesh.position.set(x, y, z); mesh.scale.set(scale * .8, scale * 1.1, scale * .55);
  mesh.rotation.set(.12, spin, -.1); glimmer.add(mesh); return mesh;
}
// Host rock: a broken face of darker matrix standing out of the country rock.
rockLobe(-1.85, 1.5, 1.05, .78, -.14, mats.matrix, .5);
rockLobe(-.55, 2.0, 1.25, .92, .1, mats.matrix, .62);
rockLobe(.85, 1.85, 1.1, .8, -.1, mats.matrix, .56);
rockLobe(1.95, 1.35, .85, .6, .14, mats.matrix, .44);
rockLobe(-.5, .85, .78, .5, .2, mats.darkRock, .4);
rockLobe(.5, 2.7, .72, .42, -.18, mats.darkRock, .36);
// The seam itself: short branches following the cracks between the bosses,
// varying in thickness, mostly still buried. No continuous glowing cable.
seamTube([[-1.35, 1.5, .5], [-.85, 1.72, .62], [-.35, 1.6, .66]], .035);
seamTube([[-.35, 1.6, .66], [.1, 1.95, .68], [.62, 1.86, .64]], .03);
seamTube([[.62, 1.86, .64], [1.15, 2.1, .58], [1.68, 1.95, .48]], .024);
seamTube([[-.35, 1.6, .64], [-.55, 1.22, .5], [-.44, .95, .42]], .019);
seamTube([[.62, 1.86, .62], [.5, 2.24, .5], [.6, 2.55, .4]], .017);
facet(-.82, 1.74, .68, .12, mats.crystal, -.2);
facet(.1, 1.98, .72, .14, mats.crystalBlue, .25);
facet(1.12, 2.08, .62, .1, mats.crystal, -.35);
// The crew's work: a shored face, a bar left in the cut, and the spoil they
// knocked down sitting at the foot of it.
for (const x of [-1.15, 1.0]) beamBetween(new V(x, 0, .95), new V(x, 2.5, .55), .075, mats.woodDark, glimmer);
beamBetween(new V(-1.15, 2.5, .55), new V(1.0, 2.5, .55), .08, mats.woodDark, glimmer);
box(1.0, .06, .07, mats.ironDark, -.1, .72, .78, 0, -.3, 0, glimmer);
box(.07, .34, .07, mats.woodDark, .62, .9, .72, 0, -.5, 0, glimmer);
for (const [x, s] of [[-1.5, .5], [-.6, .68], [.35, .58], [1.3, .44]]) {
  const spoil = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), mats.darkRock);
  spoil.scale.set(1.3, .5, 1.0); spoil.position.set(x, s * .22, .85 + (x % .4)); spoil.rotation.set(.1, x, .06);
  glimmer.add(spoil);
}
const glimmerLight = new THREE.PointLight(0x5fbfa6, coarse ? 5 : 7, 7, 2);
glimmerLight.position.copy(glimmer.position).addScaledVector(glimmerSt.side, -1.6).setY(1.9);
scene.add(glimmerLight);
const glimmerSign = signBoard('SAINT GLIMMER', 'MARKED SEAM // DO NOT BLAST', '#7be1c5', .78, glimmer);
glimmerSign.position.set(-.05, 3.0, .5);
ribLamp(-46.4, 1, 2.6, { color: 0xffc169, real: false });
ribLamp(-51.5, -1, 2.6, { color: 0xffc169, range: 12, power: 20 });

/* ------------------------------------------------------ Powderworks */
timberSet(-55.2, { inset: .3 }); const powderSet = timberSet(-60.4, { damaged: true, inset: .34 });
capLamp(powderSet, { color: 0xff9c52, range: 13, power: 24 });
crate(-54.6, 1, .55, { scale: 1.02, spin: .08, label: 'POWDER' });
crate(-55.9, 1, .5, { scale: .82, spin: -.14 });
crate(-55.2, 1, 1.5, { scale: .7, spin: .3 });
barrel(-56.9, -1, .55); barrel(-57.7, -1, 1.5, { scale: .82 });
// Locked powder chest, kept apart from everything with a flame in it.
const chestSt = stationAtZ(-59.6), chestAt = ribPoint(chestSt, -1, .6, 0);
box(1.15, .78, .8, mats.red, chestAt.x, .39, chestAt.z, chestSt.yaw);
box(1.2, .07, .85, mats.gold, chestAt.x, .8, chestAt.z, chestSt.yaw);
colliderBox(1.15, .8, .8, chestAt.x, .4, chestAt.z, chestSt.yaw);
// Drill rig against the far rib, with its steel in the face it was cutting.
const drillSt = stationAtZ(-61.4), drillAt = ribPoint(drillSt, 1, .9, 0);
const drill = new THREE.Group(); drill.position.copy(drillAt); drill.rotation.y = drillSt.yaw; visual.add(drill);
box(.85, 1.35, .68, mats.metal, 0, .68, 0, 0, 0, 0, drill);
box(.16, 1.6, .16, mats.woodDark, .36, .9, 0, 0, 0, -.12, drill);
cyl(.16, .1, 1.25, 10, mats.ironDark, .55, .95, 0, 0, 0, Math.PI / 2.6, drill);
colliderBox(.9, 1.4, .8, drillAt.x, .7, drillAt.z, drillSt.yaw);
// Shot holes drilled into the rib, charged and not yet fired.
for (let k = 0; k < 5; k++) {
  const st = stationAtZ(-62.4 - k * .5), hole = ribPoint(st, 1, .05, .9 + (k % 2) * .5);
  cyl(.06, .06, .3, 6, mats.black, hole.x, hole.y, hole.z, Math.PI / 2, st.yaw);
}
ribSign(-54.4, -1, 2.4, 'POWDERWORKS', 'NO OPEN FLAME // NO HEROICS', '#e8794f', .9);
ribLamp(-56.6, 1, 2.4, { color: 0xffa455, range: 13, power: 24 });

/* -------------------------------------------------- Foreman's Vault */
const gateSt = stationAtZ(-66.2);
const gate = new THREE.Group(); gate.position.copy(gateSt.p); gate.rotation.y = gateSt.yaw; visual.add(gate);
const gateHalf = Math.min(gateSt.width - .5, 2.4), gateTop = crownAt(gateSt, (gateHalf + .2) / gateSt.width) - .1;
for (const sign of [-1, 1]) {
  box(.26, gateTop, .26, mats.ironDark, sign * gateHalf, gateTop / 2, 0, 0, 0, 0, gate);
  box(.42, .22, .42, mats.gold, sign * gateHalf, gateTop + .1, 0, 0, 0, 0, gate);
  const p = gateSt.p.clone().addScaledVector(gateSt.side, sign * gateHalf);
  colliderBox(.34, gateTop, .34, p.x, gateTop / 2, p.z, gateSt.yaw);
}
box(gateHalf * 2 + .4, .2, .3, mats.ironDark, 0, gateTop - .1, 0, 0, 0, 0, gate);
for (let x = -gateHalf + .55; x <= gateHalf - .5; x += .78) {
  box(.1, gateTop - .3, .11, mats.metal, x, (gateTop - .3) / 2, 0, 0, 0, 0, gate);
  const p = gateSt.p.clone().addScaledVector(gateSt.side, x);
  colliderBox(.16, gateTop - .3, .18, p.x, (gateTop - .3) / 2, p.z, gateSt.yaw);
}
const vaultSign = signBoard("FOREMAN'S VAULT", 'AUTHORIZED CREW ONLY', '#edb75c', .88);
vaultSign.position.copy(gateSt.p).addScaledVector(gateSt.tangent, .5).setY(gateTop + .55);
vaultSign.rotation.y = gateSt.yaw + Math.PI;
// Ledger table, the one thing in the mine anybody came down here for.
const deskSt = stationAtZ(-70.4), deskAt = deskSt.p.clone().addScaledVector(deskSt.side, -1.2);
box(2.6, .12, 1.15, mats.woodDark, deskAt.x, .88, deskAt.z, deskSt.yaw);
box(2.3, .06, .95, mats.paper, deskAt.x, .97, deskAt.z, deskSt.yaw);
box(.7, .12, .5, mats.gold, deskAt.x + .2, 1.06, deskAt.z, deskSt.yaw, 0, 0);
for (const sign of [-1, 1]) box(.11, .82, .11, mats.woodDark, deskAt.x + sign * 1.1, .41, deskAt.z, deskSt.yaw);
colliderBox(2.6, .95, 1.2, deskAt.x, .47, deskAt.z, deskSt.yaw);
crate(-72.4, 1, .6, { scale: 1.05, spin: .12 }); crate(-73.9, 1, .55, { scale: .8, spin: -.1 });
crate(-73.2, 1, 1.6, { scale: .7, spin: .3 });
barrel(-73.6, -1, .55, { scale: .92 }); ropeCoil(-72.2, -1, .7, .85);
ribLamp(-67.6, -1, 2.7, { color: 0xffc569, range: 15, power: 30 });
ribLamp(-72.5, 1, 2.6, { color: 0xffc569, real: false });
const ledgerSign = signBoard('LEDGER ROOM', 'THE MINE REMEMBERS', '#e9b35a', .8);
ledgerSign.position.set(stations[SEGMENTS].p.x, 2.6, stations[SEGMENTS].p.z + 1.4);

/* ------------------------------------------------------------ light *
 * Ambient stays low but never black: the fill has to keep rock readable
 * between lantern pools on a phone screen without flattening the pools.
 * ------------------------------------------------------------------ */
scene.add(new THREE.HemisphereLight(0x9fc6bb, 0x3a3128, coarse ? 1.5 : 1.35));
scene.add(new THREE.AmbientLight(0x5d7a78, coarse ? .85 : .7));
// Daylight leaking in around the portal. It pools at the doorway rather than
// washing the rock face behind it — the only outside light in the mine.
const daylight = new THREE.PointLight(0xc2dbe0, coarse ? 11 : 14, 15, 2);
daylight.position.set(portal.p.x, 2.0, portal.p.z - 1.1); scene.add(daylight);

/* ------------------------------------------------------------------ *
 * Static merge
 *
 * The mine is authored as a few hundred small meshes, which is the right way
 * to place them and the wrong way to draw them. Nothing here moves, so once
 * it is all positioned we bake the world transforms and merge everything
 * sharing a material into one buffer. Draw calls drop by more than an order
 * of magnitude, which is the difference between this running on a phone and
 * not.
 * ------------------------------------------------------------------ */
/**
 * Concatenate geometries that all carry position, normal and uv. Small enough
 * to keep here rather than vendoring another add-on for one call site.
 */
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
  const byMaterial = new Map();
  const keep = [];
  root.updateMatrixWorld(true);
  // Lights live inside the lamp groups those groups are about to lose, so
  // lift them out first and bake their world position.
  const lights = [];
  root.traverse(n => { if (n.isLight) lights.push(n); });
  for (const light of lights) {
    light.getWorldPosition(light.position);
    light.removeFromParent();
    keep.push(light);
  }
  const meshes = [];
  root.traverse(n => { if (n.isMesh) meshes.push(n); });
  for (const mesh of meshes) {
    const geometry = mesh.geometry;
    // The cave shell carries vertex colours and is a single mesh already;
    // anything without matching attributes is left to draw on its own.
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
colliderRoot.updateMatrixWorld(true);
const worldOctree = new Octree().fromGraphNode(colliderRoot);
const spawn = new V(0, 0, 23.4);
const playerCollider = new Capsule(new V(spawn.x, .35, spawn.z), new V(spawn.x, 1.65, spawn.z), .35);
const velocity = new V(); let playerOnFloor = false; let ghost = false; let lanternOn = true; let jumpQueued = false;
const controls = new PointerLockControls(camera, renderer.domElement);
camera.position.copy(playerCollider.end); scene.add(camera);
const handLamp = new THREE.SpotLight(0xffdca1, coarse ? 46 : 58, 20, Math.PI / 4.6, .68, 1.6);
handLamp.position.set(.16, -.08, .12); handLamp.target.position.set(0, -.12, -4); camera.add(handLamp, handLamp.target);
function resetPlayer() {
  playerCollider.start.set(spawn.x, .35, spawn.z); playerCollider.end.set(spawn.x, 1.65, spawn.z);
  velocity.set(0, 0, 0); camera.position.copy(playerCollider.end); toast('Back at Maw Camp');
}
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
const keys = {};
addEventListener('keydown', event => {
  keys[event.code] = true;
  if (event.code === 'KeyF') toggleLantern();
  if (event.code === 'KeyG') { ghost = !ghost; toast(ghost ? 'Ghost QA ON' : 'Collision ON'); if (!ghost) resetPlayer(); }
  if (event.code === 'KeyR') resetPlayer();
  if (event.code.startsWith('Digit')) { const index = Number(event.code.slice(5)) - 1; if (qaViews[index]) teleportQa(qaViews[index]); }
});
addEventListener('keyup', event => { keys[event.code] = false; });
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
  if (camera.position.y < -5.8) { toast('The shaft wins. Back to camp.'); resetPlayer(); }
}

const zones = [
  ['MAW CAMP', 0, 22, 'Follow the rail into the old workings.'],
  ['CROOKED RAIL', 0, 5, 'The supports are older than the warning signs.'],
  ['BLACKSHAFT', 0, -17, 'Cross the bridge. Do not step off the bridge.'],
  ['DROWNED POCKET', 9.5, -36, 'Keep to the repaired walkway over the sump.'],
  ['SAINT GLIMMER', 6, -48, 'A valuable seam. Someone has already started the work.'],
  ['POWDERWORKS', 1, -58, 'Powder, sparks and a very bad idea.'],
  ["FOREMAN'S VAULT", -8.5, -69, 'The ledger is behind the iron gate.'],
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
  { p: [0, 1.65, 23.4], r: [0, 0, 0] }, { p: [0, 1.65, 12], r: [0, 0, 0] }, { p: [0, 1.75, 2], r: [0, 0, 0] },
  { p: [0, 1.85, -9], r: [0, 0, 0] }, { p: [0, 1.75, -17], r: [0, 0, 0] }, { p: [6, 1.75, -30], r: [0, 0, 0] },
  { p: [9.5, 1.8, -44], r: [0, 0, 0] }, { p: [3, 1.75, -55], r: [0, 0, 0] }, { p: [-8, 1.8, -64], r: [0, 0, 0] },
];
function teleportQa(view) { ghost = true; camera.position.set(...view.p); camera.rotation.set(...view.r); toast('QA viewpoint · ghost mode'); }

const clock = new THREE.Clock();
function toast(message) {
  const element = $('toast'); element.textContent = message; element.style.opacity = 1;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => element.style.opacity = 0, 1200);
}
function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), .033), t = clock.elapsedTime;
  movePlayer(dt); updateZone();
  for (const lamp of lampLights) lamp.light.intensity = lamp.base * (1 + Math.sin(t * 5.5 + lamp.phase) * .05);
  renderer.render(scene, camera);
}

const start = $('start');
$('enter').addEventListener('click', () => { start.style.display = 'none'; if (!coarse) controls.lock(); });
renderer.domElement.addEventListener('click', () => { if (start.style.display === 'none' && !coarse) controls.lock(); });
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 1.6));
});
frame();
