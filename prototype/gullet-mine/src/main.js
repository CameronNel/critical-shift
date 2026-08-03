import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

const coarse = matchMedia('(pointer: coarse)').matches;
const $ = id => document.getElementById(id);
const clamp = THREE.MathUtils.clamp;
const V = THREE.Vector3;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x091416);
scene.fog = new THREE.Fog(0x0a191b, 24, 108);

const camera = new THREE.PerspectiveCamera(coarse ? 67 : 70, innerWidth / innerHeight, .05, 150);
camera.rotation.order = 'YXZ';

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 1.6));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = coarse ? 1.22 : 1.16;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);

const visual = new THREE.Group();
const colliderRoot = new THREE.Group();
const dynamic = new THREE.Group();
scene.add(visual, colliderRoot, dynamic);

function canvasTexture(size, painter, repeatX = 1, repeatY = 1) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  painter(ctx, size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(repeatX, repeatY);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

const rockTexture = canvasTexture(512, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, s);
  g.addColorStop(0, '#536760'); g.addColorStop(.48, '#344843'); g.addColorStop(1, '#1d302f');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 18; i++) {
    ctx.strokeStyle = `rgba(178, 195, 173, ${.055 + i % 3 * .02})`;
    ctx.lineWidth = 2 + i % 3;
    ctx.beginPath();
    let x = (i * 83) % s, y = (i * 47) % s;
    ctx.moveTo(x, y);
    for (let j = 0; j < 5; j++) { x += 24 + (i * 13 + j * 17) % 40; y += ((i + j) % 3 - 1) * 17; ctx.lineTo(x, y); }
    ctx.stroke();
  }
  for (let i = 0; i < 28; i++) {
    ctx.fillStyle = `rgba(8, 20, 21, ${.08 + (i % 4) * .025})`;
    ctx.beginPath(); ctx.ellipse((i * 97) % s, (i * 53) % s, 18 + i % 4 * 7, 5 + i % 3 * 3, i * .4, 0, Math.PI * 2); ctx.fill();
  }
}, 2.7, 2.1);

const earthTexture = canvasTexture(512, (ctx, s) => {
  ctx.fillStyle = '#4c4a3d'; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 32; i++) {
    ctx.fillStyle = `rgba(${62 + i % 5 * 8}, ${53 + i % 4 * 7}, ${39 + i % 3 * 6}, .18)`;
    ctx.beginPath(); ctx.ellipse((i * 71) % s, (i * 113) % s, 10 + i % 5 * 8, 4 + i % 3 * 3, i, 0, Math.PI * 2); ctx.fill();
  }
  for (let i = 0; i < 9; i++) {
    ctx.strokeStyle = 'rgba(18, 24, 22, .26)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo((i * 67) % s, 0); ctx.lineTo((i * 67 + 40) % s, s); ctx.stroke();
  }
}, 3.4, 7);

const woodTexture = canvasTexture(256, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, 0);
  g.addColorStop(0, '#8a5437'); g.addColorStop(.5, '#5b3527'); g.addColorStop(1, '#9a6540');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 13; i++) {
    ctx.strokeStyle = `rgba(29, 15, 10, ${.18 + i % 3 * .05})`; ctx.lineWidth = 1 + i % 3;
    ctx.beginPath(); ctx.moveTo(0, i * 21 + 4); ctx.bezierCurveTo(55, i * 21 - 5, 120, i * 21 + 11, s, i * 21 + 2); ctx.stroke();
  }
}, 1.3, 4.5);

const metalTexture = canvasTexture(256, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, s);
  g.addColorStop(0, '#8a928a'); g.addColorStop(.5, '#434e4b'); g.addColorStop(1, '#232e2d');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 22; i++) { ctx.strokeStyle = `rgba(239, 214, 158, ${.04 + i % 3 * .02})`; ctx.beginPath(); ctx.moveTo(i * 19, 0); ctx.lineTo(i * 19 + 18, s); ctx.stroke(); }
}, 1.2, 1.2);

const waterTexture = canvasTexture(256, (ctx, s) => {
  const g = ctx.createLinearGradient(0, 0, s, s); g.addColorStop(0, '#2c7674'); g.addColorStop(1, '#102e35');
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 14; i++) {
    ctx.strokeStyle = `rgba(170, 236, 216, ${.13 - i * .004})`; ctx.lineWidth = 2;
    ctx.beginPath(); for (let x = 0; x <= s; x += 14) { const y = i * 18 + Math.sin(x * .07 + i) * 3; x ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke();
  }
}, 2.8, 2.2);

const mats = {
  cave: new THREE.MeshStandardMaterial({ map: rockTexture, color: 0x98aaa0, roughness: .98, side: THREE.BackSide, vertexColors: true }),
  rock: new THREE.MeshStandardMaterial({ map: rockTexture, color: 0x7f9188, roughness: .98 }),
  darkRock: new THREE.MeshStandardMaterial({ map: rockTexture, color: 0x304a47, roughness: 1 }),
  earth: new THREE.MeshStandardMaterial({ map: earthTexture, color: 0x8a8068, roughness: 1 }),
  wood: new THREE.MeshStandardMaterial({ map: woodTexture, color: 0xa76b45, roughness: .93 }),
  woodDark: new THREE.MeshStandardMaterial({ map: woodTexture, color: 0x613925, roughness: .98 }),
  metal: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x87948d, metalness: .45, roughness: .52 }),
  ironDark: new THREE.MeshStandardMaterial({ color: 0x273332, metalness: .62, roughness: .48 }),
  rope: new THREE.MeshStandardMaterial({ color: 0x9d784d, roughness: 1 }),
  gold: new THREE.MeshStandardMaterial({ color: 0xd89d42, metalness: .55, roughness: .34 }),
  red: new THREE.MeshStandardMaterial({ color: 0x933c2d, roughness: .84 }),
  canvas: new THREE.MeshStandardMaterial({ color: 0x476d68, roughness: 1 }),
  crystal: new THREE.MeshStandardMaterial({ color: 0x7fe1d1, emissive: 0x185b55, emissiveIntensity: .75, roughness: .25, metalness: .06 }),
  crystalBlue: new THREE.MeshStandardMaterial({ color: 0x7cc8e2, emissive: 0x124d67, emissiveIntensity: .65, roughness: .28 }),
  vein: new THREE.MeshStandardMaterial({ color: 0x7de5c7, emissive: 0x176b5d, emissiveIntensity: .75, roughness: .3 }),
  water: new THREE.MeshPhysicalMaterial({ map: waterTexture, color: 0x438f8b, roughness: .16, metalness: .05, transparent: true, opacity: .79, clearcoat: .35, clearcoatRoughness: .2, side: THREE.DoubleSide }),
  black: new THREE.MeshBasicMaterial({ color: 0x02080a }),
  flame: new THREE.MeshBasicMaterial({ color: 0xffc66b }),
  paper: new THREE.MeshStandardMaterial({ color: 0xd7bc7e, roughness: 1 }),
};

function receive(mesh, cast = true) { mesh.castShadow = cast; mesh.receiveShadow = true; return mesh; }
function add(mesh, parent = visual) { parent.add(receive(mesh)); return mesh; }
function box(w, h, d, mat, x = 0, y = 0, z = 0, ry = 0, rz = 0, rx = 0, parent = visual) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); return add(mesh, parent);
}
function cyl(rt, rb, h, segments, mat, x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, parent = visual) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, segments), mat);
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); return add(mesh, parent);
}
function beamBetween(a, b, radius, mat, parent = visual) {
  const direction = new V().subVectors(b, a); const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius * 1.08, direction.length(), 8), mat);
  mesh.position.copy(a).add(b).multiplyScalar(.5); mesh.quaternion.setFromUnitVectors(new V(0, 1, 0), direction.normalize()); return add(mesh, parent);
}
function colliderBox(w, h, d, x, y, z, ry = 0, rz = 0, rx = 0) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ visible: false }));
  mesh.position.set(x, y, z); mesh.rotation.set(rx, ry, rz); colliderRoot.add(mesh); return mesh;
}
function signTexture(text, sub = '', accent = '#e9b35a') {
  const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 170; const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#30231b'; ctx.fillRect(0, 0, 512, 170);
  ctx.strokeStyle = accent; ctx.lineWidth = 7; ctx.strokeRect(10, 10, 492, 150);
  ctx.fillStyle = accent; ctx.font = 'bold 44px Georgia'; ctx.textAlign = 'center'; ctx.fillText(text, 256, 79);
  ctx.fillStyle = '#e4d0a4'; ctx.font = '19px system-ui'; ctx.fillText(sub, 256, 119);
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace; return texture;
}
function sign(text, sub, x, y, z, ry = 0, accent = '#e9b35a', scale = 1) {
  const g = new THREE.Group(); const board = box(1.75 * scale, .62 * scale, .10, mats.woodDark, 0, 0, 0, 0, 0, 0, g);
  const label = new THREE.Mesh(new THREE.PlaneGeometry(1.58 * scale, .52 * scale), new THREE.MeshBasicMaterial({ map: signTexture(text, sub, accent), side: THREE.DoubleSide }));
  label.position.z = .061; g.add(label); g.position.set(x, y, z); g.rotation.y = ry; visual.add(g); return g;
}

// The route is intentionally short and composed as connected rooms, not an endless procedural tube.
const pathNodes = [
  { x: 0, z: 19, w: 6.1, h: 5.4 }, { x: 0, z: 12, w: 5.8, h: 5.1 }, { x: 0, z: 5, w: 4.8, h: 4.7 },
  { x: 0, z: -3, w: 4.7, h: 4.6 }, { x: 0, z: -10, w: 5.3, h: 5.0 }, { x: 0, z: -24, w: 5.2, h: 5.2 },
  { x: 6, z: -28, w: 5.8, h: 5.3 }, { x: 10, z: -34, w: 7.0, h: 5.8 }, { x: 10, z: -42, w: 7.1, h: 5.9 },
  { x: 6, z: -50, w: 6.2, h: 5.4 }, { x: 2, z: -56, w: 5.7, h: 5.0 }, { x: -1, z: -62, w: 6.0, h: 5.4 },
  { x: -8, z: -68, w: 6.7, h: 5.7 }, { x: -9, z: -77, w: 7.0, h: 5.9 },
].map(p => new V(p.x, 0, p.z));
const pathCurve = new THREE.CatmullRomCurve3(pathNodes, false, 'catmullrom', .35);
const nodeProfiles = [6.1,5.8,4.8,4.7,5.3,5.2,5.8,7,7.1,6.2,5.7,6,6.7,7];
const nodeHeights = [5.4,5.1,4.7,4.6,5,5.2,5.3,5.8,5.9,5.4,5,5.4,5.7,5.9];
function profile(t, list) { const q = t * (list.length - 1), i = Math.floor(q), f = q - i; return THREE.MathUtils.lerp(list[Math.min(i, list.length - 1)], list[Math.min(i + 1, list.length - 1)], f); }
function basis(t) { const p = pathCurve.getPointAt(t), tangent = pathCurve.getTangentAt(t).setY(0).normalize(); return { p, tangent, side: new V(-tangent.z, 0, tangent.x) }; }
function inWater(p) { return p.x > 2.5 && p.z < -24 && p.z > -40; }
function inShaft(p) { return Math.abs(p.x) < 4.3 && p.z < -11 && p.z > -23; }

function buildCaveShell() {
  const segments = 128, ring = 18, positions = [], colors = [], indices = [], rockColor = new THREE.Color();
  for (let i = 0; i <= segments; i++) {
    const t = i / segments, { p, side } = basis(t), width = profile(t, nodeProfiles), height = profile(t, nodeHeights);
    for (let j = 0; j <= ring; j++) {
      const a = j / ring * Math.PI * 2, c = Math.cos(a), s = Math.sin(a);
      const rough = 1 + Math.sin(i * .61 + j * 1.27) * .035 + Math.sin(i * .19 - j * .7) * .022;
      const point = p.clone().addScaledVector(side, c * width * rough); point.y = s * height * rough + (s < -.45 ? -.08 : 0);
      positions.push(point.x, point.y, point.z);
      rockColor.setHSL(.43, .12, .30 + (s + 1) * .055 + ((i + j) % 4) * .009); colors.push(rockColor.r, rockColor.g, rockColor.b);
    }
  }
  for (let i = 0; i < segments; i++) for (let j = 0; j < ring; j++) { const a = i * (ring + 1) + j, b = a + ring + 1; indices.push(a, b, a + 1, a + 1, b, b + 1); }
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3)); geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3)); geometry.setIndex(indices); geometry.computeVertexNormals();
  const mesh = new THREE.Mesh(geometry, mats.cave); mesh.receiveShadow = true; visual.add(mesh);
}
function buildGround() {
  const segments = 128, positions = [], uvs = [], indices = [];
  for (let i = 0; i <= segments; i++) {
    const t = i / segments, { p, side } = basis(t), width = profile(t, nodeProfiles) * .83;
    const left = p.clone().addScaledVector(side, -width), right = p.clone().addScaledVector(side, width); left.y = right.y = -.04;
    positions.push(left.x, left.y, left.z, right.x, right.y, right.z); uvs.push(0, t * 13, 2.5, t * 13);
  }
  for (let i = 0; i < segments; i++) { const a = i * 2, mid = new V().fromArray(positions, a * 3).add(new V().fromArray(positions, (a + 2) * 3)).multiplyScalar(.5); if (!inShaft(mid) && !inWater(mid)) indices.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3)); geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2)); geometry.setIndex(indices); geometry.computeVertexNormals(); const mesh = new THREE.Mesh(geometry, mats.earth); mesh.receiveShadow = true; visual.add(mesh);
}
buildCaveShell(); buildGround();

// Simplified collision follows the route but intentionally leaves the Blackshaft void open.
for (let i = 0; i < 110; i++) {
  const t0 = i / 110, t1 = (i + 1) / 110, a = basis(t0).p, b = basis(t1).p, mid = a.clone().add(b).multiplyScalar(.5), tangent = new V().subVectors(b, a), length = Math.max(.5, Math.hypot(tangent.x, tangent.z)), yaw = Math.atan2(tangent.x, tangent.z), width = profile((t0 + t1) / 2, nodeProfiles) * .78;
  if (!inShaft(mid) && !inWater(mid)) colliderBox(width * 2, .48, length + .14, mid.x, -.27, mid.z, yaw);
  if (!inWater(mid)) {
    const side = new V(-tangent.z, 0, tangent.x).normalize(), wallOffset = width + .38, wallHeight = profile((t0 + t1) / 2, nodeHeights) + 2.6;
    const left = mid.clone().addScaledVector(side, -wallOffset), right = mid.clone().addScaledVector(side, wallOffset);
    colliderBox(.7, wallHeight, length + .15, left.x, wallHeight / 2 - .08, left.z, yaw); colliderBox(.7, wallHeight, length + .15, right.x, wallHeight / 2 - .08, right.z, yaw);
  }
}

function railCurve(points, offset = 0) { return new THREE.CatmullRomCurve3(points.map(p => p.clone().add(new V(offset, .09, 0))), false, 'catmullrom', .2); }
function buildRails() {
  const points = [new V(-.52, 0, 18), new V(-.52, 0, 12), new V(-.47, 0, 6), new V(-.4, 0, -.5), new V(-.3, 0, -8.7)];
  for (const offset of [-.52, .52]) { const rail = new THREE.Mesh(new THREE.TubeGeometry(railCurve(points, offset + .52), 64, .055, 7, false), mats.metal); add(rail); }
  for (let z = 17.6; z > -8.5; z -= 1.18) { const width = z > 6 ? 1.8 : 1.62; box(width, .12, .26, mats.woodDark, 0, .06, z); }
}
buildRails();

function timberFrame(x, z, width, height, lean = 0, ry = 0, damaged = false) {
  const group = new THREE.Group(); group.position.set(x, 0, z); group.rotation.y = ry; visual.add(group);
  const leftBottom = new V(-width, 0, 0), rightBottom = new V(width, 0, 0);
  const leftTop = new V(-width + lean, height, 0), rightTop = new V(width - lean, height - (damaged ? .14 : 0), 0);
  beamBetween(leftBottom, leftTop, .28, mats.woodDark, group); beamBetween(rightBottom, rightTop, .28, mats.wood, group);
  beamBetween(leftTop, rightTop, .30, mats.wood, group);
  if (damaged) beamBetween(new V(-width + .1, .5, .04), new V(width - .3, height - .55, .04), .11, mats.woodDark, group);
  colliderBox(.48, height, .52, x - width + lean * .5, height / 2, z, ry); colliderBox(.48, height, .52, x + width - lean * .5, height / 2, z, ry);
}
[[0, 12.2, 2.55, 4.5, .12, 0, false], [0, 7.4, 2.35, 4.25, -.16, .015, false], [0, 2.2, 2.25, 4.1, .2, -.01, true], [0, -3.2, 2.35, 4.4, -.1, .01, false], [0, -8.5, 2.55, 4.65, .18, -.02, true]].forEach(args => timberFrame(...args));

function crate(x, z, scale = 1, ry = 0, label = '') {
  const w = 1.15 * scale, h = .9 * scale, group = new THREE.Group(); group.position.set(x, 0, z); group.rotation.y = ry; visual.add(group);
  box(w, h, w, mats.woodDark, 0, h / 2, 0, 0, 0, 0, group); box(w + .06, .09 * scale, w + .06, mats.wood, 0, .12 * scale, 0, 0, 0, 0, group); box(w + .06, .09 * scale, w + .06, mats.wood, 0, h - .12 * scale, 0, 0, 0, 0, group);
  box(.09 * scale, h + .03, w + .06, mats.wood, 0, h / 2, 0, 0, 0, .62, group); box(.09 * scale, h + .03, w + .06, mats.wood, 0, h / 2, 0, 0, 0, -.62, group);
  if (label) { const labelMesh = new THREE.Mesh(new THREE.PlaneGeometry(.7 * scale, .23 * scale), new THREE.MeshBasicMaterial({ map: signTexture(label, 'HANDLE WITH CARE', '#dbab5c') })); labelMesh.position.set(0, h * .54, w / 2 + .01); labelMesh.rotation.y = Math.PI; group.add(labelMesh); }
  colliderBox(w * .92, h, w * .92, x, h / 2, z, ry);
}
function barrel(x, z, scale = 1, ry = 0, band = true) {
  const group = new THREE.Group(); group.position.set(x, 0, z); group.rotation.y = ry; visual.add(group); cyl(.43 * scale, .47 * scale, 1.05 * scale, 14, mats.wood, 0, .525 * scale, 0, 0, 0, 0, group);
  if (band) for (const y of [.18, .52, .87]) { const ring = new THREE.Mesh(new THREE.TorusGeometry(.455 * scale, .035 * scale, 6, 16), mats.metal); ring.rotation.x = Math.PI / 2; ring.position.y = y * scale; group.add(ring); }
  colliderBox(.88 * scale, 1.05 * scale, .88 * scale, x, .525 * scale, z, ry);
}
function ropeCoil(x, z, scale = 1) {
  const ring = new THREE.Mesh(new THREE.TorusGeometry(.42 * scale, .075 * scale, 7, 18), mats.rope); ring.rotation.x = Math.PI / 2; ring.position.set(x, .09 * scale, z); add(ring);
}
function cart(x, z, ry = 0, full = true) {
  const group = new THREE.Group(); group.position.set(x, 0, z); group.rotation.y = ry; visual.add(group);
  box(1.45, .58, 1.72, mats.metal, 0, .66, 0, 0, 0, 0, group); box(1.20, .14, 1.45, mats.woodDark, 0, .78, 0, 0, 0, 0, group);
  for (const xx of [-.57, .57]) for (const zz of [-.57, .57]) cyl(.18, .18, .12, 10, mats.ironDark, xx, .25, zz, 0, 0, Math.PI / 2, group);
  if (full) { const ore = new THREE.Mesh(new THREE.DodecahedronGeometry(.36, 0), mats.rock); ore.scale.set(1.25, .55, .9); ore.position.set(-.25, 1.04, -.2); group.add(ore); const ore2 = new THREE.Mesh(new THREE.DodecahedronGeometry(.28, 0), mats.crystal); ore2.scale.set(1.3, .65, .8); ore2.position.set(.22, 1.02, .18); group.add(ore2); }
  colliderBox(1.5, 1.18, 1.72, x, .59, z, ry);
}

// Maw Camp: a deliberate staging vignette rather than a prop field.
timberFrame(0, 19.2, 3.1, 5.2, .06, 0, false); sign('MAW CAMP', 'STAGING / SHIFT 03', 0, 4.25, 19.05, Math.PI, '#e9b35a', 1.15);
crate(-4.35, 17.1, 1.05, .16, 'LAMP OIL'); crate(-4.9, 18.5, .75, -.12); barrel(4.25, 17.6, 1.05, .12); ropeCoil(4.35, 18.75, 1.1); cart(2.15, 16.9, -.06, true);
box(1.7, .08, .8, mats.woodDark, -2.9, .9, 16.1); box(1.52, .08, .66, mats.paper, -2.9, .99, 16.1); sign('SHIFT BOARD', 'KEEP THE LANTERN UP', -2.9, 1.2, 15.68, Math.PI, '#83c7bc', .72);

// Lamps are real fixtures attached to timber or rock positions; only a few cast large pools.
const lampLights = [];
function lamp(x, y, z, color = 0xffc169, real = true, scale = 1) {
  const group = new THREE.Group(); group.position.set(x, y, z); visual.add(group);
  box(.10 * scale, .10 * scale, .62 * scale, mats.ironDark, 0, .22 * scale, .16 * scale, 0, 0, -.18, group);
  cyl(.14 * scale, .19 * scale, .13 * scale, 8, mats.ironDark, 0, -.17 * scale, .42 * scale, 0, 0, 0, group);
  cyl(.14 * scale, .14 * scale, .26 * scale, 8, mats.ironDark, 0, -.35 * scale, .42 * scale, 0, 0, 0, group);
  const flame = new THREE.Mesh(new THREE.SphereGeometry(.085 * scale, 10, 8), new THREE.MeshBasicMaterial({ color })); flame.scale.set(.7, 1.35, .7); flame.position.set(0, -.35 * scale, .42 * scale); group.add(flame);
  if (real) { const light = new THREE.PointLight(color, coarse ? 3.6 : 4.9, coarse ? 9 : 11, 1.8); light.position.set(0, -.27 * scale, .34 * scale); group.add(light); lampLights.push({ light, phase: lampLights.length * 1.41 }); }
}
lamp(-2.55, 3.85, 12.1, 0xffc26a, true); lamp(2.55, 3.8, 7.1, 0x9ad9c4, false); lamp(-2.45, 3.78, 2.0, 0xffc26a, true); lamp(2.55, 3.95, -3.2, 0x9fd6df, false); lamp(-2.75, 4.1, -8.4, 0xffb35d, true);
lamp(-4.5, 3.1, 17.3, 0xffbd65, true); lamp(4.55, 3.15, 17.3, 0xffbd65, false);

// Blackshaft: a real opening under a narrow, raised crossing.
const shaftBottom = box(8.2, .18, 11.8, mats.black, 0, -7.2, -17, 0, 0, 0, visual); shaftBottom.receiveShadow = false;
for (const x of [-3.9, 3.9]) { box(.52, 7.4, .52, mats.woodDark, x, -3.45, -12.1); box(.52, 7.4, .52, mats.woodDark, x, -3.45, -21.9); beamBetween(new V(x, -.1, -12), new V(x, 2.9, -21.8), .12, mats.rope); }
box(2.45, .34, 10.4, mats.wood, 0, .72, -17); colliderBox(2.45, .38, 10.4, 0, .72, -17);
box(2.45, .16, 2.5, mats.wood, 0, .36, -11.15, 0, 0, .28); colliderBox(2.45, .18, 2.5, 0, .36, -11.15, 0, 0, .28);
box(2.45, .16, 2.5, mats.wood, 0, .36, -22.85, 0, 0, -.28); colliderBox(2.45, .18, 2.5, 0, .36, -22.85, 0, 0, -.28);
for (let z = -12.3; z >= -21.7; z -= 1.15) box(2.7, .10, .24, mats.woodDark, 0, .94, z);
for (const x of [-1.32, 1.32]) { for (const z of [-12.1, -14.6, -17.1, -19.6, -21.9]) { box(.16, .72, .18, mats.metal, x, 1.17, z); } box(.18, .16, 10.3, mats.metal, x, 1.52, -17); beamBetween(new V(x, 1.2, -12.1), new V(x, 1.2, -21.9), .06, mats.rope); }
box(7.6, .5, 2.2, mats.earth, 0, -.25, -10.25); colliderBox(7.6, .48, 2.2, 0, -.25, -10.25); box(7.6, .5, 2.2, mats.earth, 0, -.25, -23.75); colliderBox(7.6, .48, 2.2, 0, -.25, -23.75);
const winch = new THREE.Group(); winch.position.set(-3.65, 3.8, -10.8); visual.add(winch); box(1.1, .18, .8, mats.woodDark, 0, 0, 0, 0, 0, 0, winch); cyl(.62, .62, .16, 14, mats.metal, 0, .06, 0, 0, 0, Math.PI / 2, winch); cyl(.13, .13, 1.0, 10, mats.wood, 0, .08, 0, 0, 0, Math.PI / 2, winch); beamBetween(new V(0, .18, 0), new V(0, -6.6, 0), .025, mats.rope, winch);
lamp(-2.55, 3.8, -12.1, 0xffbd66, true); lamp(2.55, 3.8, -21.9, 0x76cbd0, true);
sign('BLACKSHAFT', 'BRIDGE ONLY // WATCH YOUR STEP', 0, 2.25, -11.2, Math.PI, '#d98352', .92);

function walkSegment(a, b, width = 2.8, y = .28) {
  const midpoint = a.clone().add(b).multiplyScalar(.5), d = b.clone().sub(a), length = Math.hypot(d.x, d.z), yaw = Math.atan2(d.x, d.z);
  box(width, .20, length, mats.wood, midpoint.x, y, midpoint.z, yaw); colliderBox(width, .25, length, midpoint.x, y, midpoint.z, yaw);
  return { midpoint, length, yaw };
}
const drownedPath = [new V(0, 0, -24.2), new V(5.2, 0, -27), new V(9.7, 0, -30.6), new V(10, 0, -38.2)];
for (let i = 0; i < drownedPath.length - 1; i++) { const a = drownedPath[i], b = drownedPath[i + 1], d = b.clone().sub(a); const length = Math.hypot(d.x, d.z); for (let u = 0; u < length; u += 1.15) { const p = a.clone().addScaledVector(d, (u + .48) / length); box(2.75, .12, .25, mats.woodDark, p.x, .39, p.z, Math.atan2(d.x, d.z)); } walkSegment(a, b, 2.65, .28); }
box(16, .10, 11, mats.water, 10, .04, -32.1); box(16, .10, 7.5, mats.water, 10, .04, -38.5);
// Damaged side walkway and pump make the water pocket read as a workplace, not a blue plane.
box(2.5, .16, 4.9, mats.woodDark, 15.1, .30, -31.8); colliderBox(2.5, .20, 4.9, 15.1, .30, -31.8);
const pump = new THREE.Group(); pump.position.set(14.8, .22, -33); visual.add(pump); box(1.0, 1.35, .85, mats.metal, 0, .68, 0, 0, 0, 0, pump); cyl(.62, .62, .12, 16, mats.metal, 0, 1.34, 0, 0, 0, Math.PI / 2, pump); cyl(.12, .12, 1.7, 8, mats.wood, 0, 1.35, 0, 0, 0, Math.PI / 2, pump); beamBetween(new V(0, 1.35, 0), new V(.7, 1.9, 0), .07, mats.metal, pump);
lamp(7.5, 3.9, -28.2, 0x83d0d0, true); lamp(13.8, 3.55, -34.7, 0x7ed1d0, false); lamp(11.5, 4.0, -39.2, 0x9fd6e2, true);
sign('DROWNED POCKET', 'PUMP BATTERY // WALKWAY DAMAGED', 14.2, 3.2, -27.4, Math.PI * .98, '#79c8c0', .75);

function veinStrip(points, z, material, width = .12) {
  const vertices = [], index = [];
  for (let i = 0; i < points.length; i++) { const p = points[i], next = points[Math.min(i + 1, points.length - 1)], tangent = new V(next[0] - p[0], next[1] - p[1], 0).normalize(), normal = new V(-tangent.y, tangent.x, 0).multiplyScalar(width); vertices.push(p[0] - normal.x, p[1] - normal.y, z, p[0] + normal.x, p[1] + normal.y, z); if (i) { const a = (i - 1) * 2; index.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3)); geometry.setIndex(index); geometry.computeVertexNormals(); const mesh = new THREE.Mesh(geometry, material); mesh.castShadow = true; visual.add(mesh); return mesh;
}
function crystal(x, y, z, scale, material = mats.crystal, ry = 0) {
  const mesh = new THREE.Mesh(new THREE.DodecahedronGeometry(1, 0), material); mesh.position.set(x, y, z); mesh.scale.set(scale * .55, scale * 1.25, scale * .42); mesh.rotation.set(.12, ry, -.1); add(mesh); return mesh;
}
// Saint Glimmer hero wall: a mineral seam in a dark matrix, with only a few exposed faces.
box(6.7, 2.9, .56, mats.darkRock, 10, 2.05, -48.7, 0, 0, 0);
veinStrip([[6.7,1.3],[7.5,1.7],[8.2,1.52],[8.9,2.12],[9.6,2.0],[10.4,2.72],[11.25,2.5],[12.5,3.2]], -48.36, mats.vein, .14);
veinStrip([[8.15,1.55],[7.8,.95],[8.0,.46]], -48.34, mats.vein, .09);
veinStrip([[9.65,2.03],[9.4,2.75],[9.55,3.38]], -48.33, mats.vein, .085);
crystal(7.5, 1.72, -48.28, .48, mats.crystal, -.2); crystal(8.9, 2.16, -48.27, .64, mats.crystalBlue, .25); crystal(10.45, 2.75, -48.25, .58, mats.crystal, -.35); crystal(11.35, 2.55, -48.27, .39, mats.crystalBlue, .15);
// Mining scars and a hand tool give the seam a reason to be exposed.
box(1.6, .08, .08, mats.ironDark, 8.3, .72, -48.22, -.26, 0, 0); box(.10, .5, .10, mats.woodDark, 8.9, .93, -48.18, 0, 0, -.48);
const glimmerLight = new THREE.PointLight(0x59c9b4, coarse ? 3.2 : 4.4, 12, 1.8); glimmerLight.position.set(9.5, 2.3, -46.5); scene.add(glimmerLight); lamp(6.2, 3.8, -45.8, 0x9be0cb, true); lamp(13.6, 3.85, -46.5, 0x83c9dd, false); sign('SAINT GLIMMER', 'MARKED SEAM // DO NOT BLAST', 10, 4.25, -48.1, 0, '#7be1c5', 1.1);

// Powderworks: warmer, stricter construction and deliberately staged powder storage.
timberFrame(2.2, -55.5, 2.45, 4.6, -.12, .12, false); timberFrame(-.8, -61, 2.55, 4.9, .14, -.1, true);
crate(4.15, -55.6, 1.05, .08, 'POWDER'); crate(4.35, -57.1, .9, -.12, 'POWDER'); barrel(1.7, -57.7, 1.05, .1, true); barrel(2.65, -58.4, .82, -.1, true);
box(1.15, .85, .85, mats.red, -1.8, .43, -57.8); box(1.21, .08, .9, mats.gold, -1.8, .88, -57.8); sign('POWDERWORKS', 'NO OPEN FLAME // NO HEROICS', 1, 3.45, -55.0, Math.PI, '#e8794f', .95);
const drill = new THREE.Group(); drill.position.set(-3.55, 0, -58.4); visual.add(drill); box(.9, 1.55, .72, mats.metal, 0, .78, 0, 0, 0, 0, drill); box(.18, 1.8, .18, mats.woodDark, .4, 1.0, 0, 0, 0, -.12, drill); cyl(.34, .18, 1.35, 10, mats.ironDark, .42, .82, 0, 0, 0, Math.PI / 2, drill); colliderBox(.9, 1.55, .72, -3.55, .78, -58.4);
lamp(3.8, 3.9, -55.2, 0xffa455, true); lamp(-2.6, 4.1, -61.2, 0xff7f4e, true);

// Foreman's Vault: an end composition with a gate, ironwork and a single warm reward focal point.
function gate(x, z) {
  for (const xx of [-2.2, 2.2]) { box(.28, 3.5, .28, mats.ironDark, x + xx, 1.75, z); box(.48, .24, .48, mats.gold, x + xx, 3.55, z); }
  box(4.7, .22, .32, mats.ironDark, x, 3.45, z); for (let xx = -1.7; xx <= 1.7; xx += .85) box(.11, 3.2, .12, mats.metal, x + xx, 1.6, z);
  colliderBox(.34, 3.5, .34, x - 2.2, 1.75, z); colliderBox(.34, 3.5, .34, x + 2.2, 1.75, z);
}
gate(-8.5, -66.1); sign('FOREMAN\'S VAULT', 'AUTHORIZED CREW ONLY', -8.5, 4.1, -65.65, 0, '#edb75c', .9);
box(3.0, .14, 1.2, mats.woodDark, -9, .95, -72.4); box(2.65, .08, 1.0, mats.paper, -9, 1.06, -72.4); box(.75, .13, .56, mats.gold, -9, 1.18, -72.42);
crate(-12.2, -72.1, 1.05, .12); crate(-12.1, -74.0, .82, -.1); barrel(-6.0, -74.0, .9, .2); ropeCoil(-5.7, -72.55, .85);
for (const x of [-12.8, -5.1]) lamp(x, 3.75, -70.5, 0xffc569, true);
const vaultLight = new THREE.PointLight(0xffb35e, coarse ? 4 : 5.5, 15, 1.7); vaultLight.position.set(-9, 3.6, -72.2); scene.add(vaultLight);
sign('LEDGER ROOM', 'THE MINE REMEMBERS', -9, 3.2, -76.1, Math.PI, '#e9b35a', .8);

// Lighting stays limited and practical: strong pools near fixtures, cool ambient between them.
scene.add(new THREE.HemisphereLight(0x8bb5ac, 0x261f1c, coarse ? .62 : .56));
const moon = new THREE.DirectionalLight(0x9fc8c5, .42); moon.position.set(-18, 25, 14); moon.castShadow = !coarse; moon.shadow.mapSize.set(1024, 1024); moon.shadow.camera.left = -30; moon.shadow.camera.right = 30; moon.shadow.camera.top = 24; moon.shadow.camera.bottom = -82; scene.add(moon);
const coolBounce = new THREE.PointLight(0x3a8587, coarse ? 1.3 : 1.8, 28, 2); coolBounce.position.set(3, 3.2, -29); scene.add(coolBounce);
const warmBounce = new THREE.PointLight(0xa85b35, coarse ? 1.2 : 1.5, 24, 2); warmBounce.position.set(1, 3.2, -58); scene.add(warmBounce);

// Player and collision.
colliderRoot.updateMatrixWorld(true);
const worldOctree = new Octree().fromGraphNode(colliderRoot);
const spawn = new V(0, 0, 16.6);
const playerCollider = new Capsule(new V(spawn.x, .35, spawn.z), new V(spawn.x, 1.65, spawn.z), .35);
const velocity = new V(); let playerOnFloor = false; let ghost = false; let lanternOn = true; let jumpQueued = false;
const controls = new PointerLockControls(camera, renderer.domElement);
camera.position.copy(playerCollider.end); scene.add(camera);
const handLamp = new THREE.SpotLight(0xffdca1, coarse ? 5.3 : 6.8, 22, Math.PI / 5, .62, 1.7); handLamp.position.set(.16, -.08, .12); handLamp.target.position.set(0, -.12, -4); camera.add(handLamp, handLamp.target);
function resetPlayer() { playerCollider.start.set(spawn.x, .35, spawn.z); playerCollider.end.set(spawn.x, 1.65, spawn.z); velocity.set(0, 0, 0); camera.position.copy(playerCollider.end); toast('Back at Maw Camp'); }
function getForward() { camera.getWorldDirection(playerDirection); playerDirection.y = 0; return playerDirection.normalize(); }
function getSide() { getForward(); return playerDirection.cross(camera.up).normalize(); }
const playerDirection = new V();
function collisions() {
  playerOnFloor = false;
  for (let i = 0; i < 3; i++) { const result = worldOctree.capsuleIntersect(playerCollider); if (!result) break; playerOnFloor = result.normal.y > .35; playerCollider.translate(result.normal.multiplyScalar(result.depth)); if (result.normal.y > .35 && velocity.y < 0) velocity.y = 0; else velocity.addScaledVector(result.normal, -result.normal.dot(velocity)); }
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
function toggleLantern() { lanternOn = !lanternOn; handLamp.intensity = lanternOn ? (coarse ? 5.3 : 6.8) : 0; toast(lanternOn ? 'Hand lantern lit' : 'Hand lantern snuffed'); }

let yaw = 0, pitch = 0, looking = false, lastPointer = null;
const lookZone = $('look-zone');
lookZone.addEventListener('pointerdown', event => { looking = true; lastPointer = { x: event.clientX, y: event.clientY }; lookZone.setPointerCapture(event.pointerId); });
lookZone.addEventListener('pointermove', event => { if (!looking) return; const dx = event.clientX - lastPointer.x, dy = event.clientY - lastPointer.y; lastPointer = { x: event.clientX, y: event.clientY }; yaw -= dx * .0042; pitch = clamp(pitch - dy * .0038, -1.25, 1.25); camera.rotation.set(pitch, yaw, 0); });
lookZone.addEventListener('pointerup', () => { looking = false; });
const stick = $('stick'), knob = $('knob'); let joy = { x: 0, y: 0 };
function setJoy(event) { const rect = stick.getBoundingClientRect(), cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2, max = rect.width * .34; let dx = event.clientX - cx, dy = event.clientY - cy, len = Math.hypot(dx, dy) || 1; if (len > max) { dx *= max / len; dy *= max / len; } joy = { x: dx / max, y: dy / max }; knob.style.transform = `translate(${dx}px,${dy}px)`; }
stick.addEventListener('pointerdown', event => { stick.setPointerCapture(event.pointerId); setJoy(event); }); stick.addEventListener('pointermove', event => { if (stick.hasPointerCapture(event.pointerId)) setJoy(event); }); stick.addEventListener('pointerup', () => { joy = { x: 0, y: 0 }; knob.style.transform = 'translate(0,0)'; });
$('jump-button').addEventListener('pointerdown', () => jumpQueued = true); $('lamp-button').addEventListener('pointerdown', toggleLantern);

function movePlayer(dt) {
  const forward = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0) - joy.y, side = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0) + joy.x, sprint = keys.ShiftLeft || keys.ShiftRight;
  if (ghost) { const speed = (sprint ? 10 : 6) * dt; camera.position.addScaledVector(getForward(), forward * speed); camera.position.addScaledVector(getSide(), side * speed); if (keys.Space) camera.position.y += speed; if (keys.ControlLeft) camera.position.y -= speed; return; }
  const accel = playerOnFloor ? (sprint ? 29 : 21) : 8;
  if (forward) velocity.addScaledVector(getForward(), forward * accel * dt); if (side) velocity.addScaledVector(getSide(), side * accel * dt);
  if ((keys.Space || jumpQueued) && playerOnFloor) velocity.y = 5.55; jumpQueued = false;
  let damping = Math.exp(-8 * dt) - 1; if (!playerOnFloor) { velocity.y -= 19 * dt; damping *= .12; } velocity.addScaledVector(velocity, damping);
  playerCollider.translate(velocity.clone().multiplyScalar(dt)); collisions(); camera.position.copy(playerCollider.end);
  if (camera.position.y < -5.8) { toast('The shaft wins. Back to camp.'); resetPlayer(); }
}

const zones = [
  ['MAW CAMP', 0, 16, 'Follow the rail into the old workings.'], ['CROOKED RAIL', 0, 4, 'The supports are older than the warning signs.'], ['BLACKSHAFT', 0, -17, 'Cross the bridge. Do not step off the bridge.'], ['DROWNED POCKET', 9, -32, 'Keep to the repaired walkway over the sump.'], ['SAINT GLIMMER', 10, -46, 'A valuable seam. Someone has already started the work.'], ['POWDERWORKS', 0, -58, 'Powder, sparks and a very bad idea.'], ["FOREMAN'S VAULT", -9, -72, 'The ledger is behind the iron gate.']
];
function updateZone() { let nearest = zones[0], distance = Infinity; for (const zone of zones) { const d = (camera.position.x - zone[1]) ** 2 + (camera.position.z - zone[2]) ** 2; if (d < distance) { distance = d; nearest = zone; } } $('zone').textContent = nearest[0]; $('objective').textContent = nearest[3]; }

const qaViews = [
  { p: [0, 1.65, 16.5], r: [0, 0, 0] }, { p: [0, 1.65, 7.2], r: [0, Math.PI, 0] }, { p: [0, 2.0, -9.2], r: [-.04, Math.PI, 0] },
  { p: [0, 1.95, -15], r: [0, Math.PI, 0] }, { p: [8.4, 1.7, -31], r: [0, Math.PI * .5, 0] }, { p: [10, 1.7, -43], r: [0, Math.PI, 0] },
  { p: [10, 2.3, -45.4], r: [-.08, Math.PI, 0] }, { p: [1.5, 1.7, -57], r: [0, -.4, 0] }, { p: [-9, 1.7, -70], r: [0, Math.PI, 0] }
];
function teleportQa(view) { ghost = true; camera.position.set(...view.p); camera.rotation.set(...view.r); toast('QA viewpoint · ghost mode'); }

const clock = new THREE.Clock();
function toast(message) { const element = $('toast'); element.textContent = message; element.style.opacity = 1; clearTimeout(toast.timer); toast.timer = setTimeout(() => element.style.opacity = 0, 1200); }
function frame() {
  requestAnimationFrame(frame); const dt = Math.min(clock.getDelta(), .033), t = clock.elapsedTime; movePlayer(dt); updateZone();
  for (const lamp of lampLights) lamp.light.intensity *= 1 + Math.sin(t * 5.5 + lamp.phase) * .018;
  renderer.render(scene, camera);
}

const start = $('start'); $('enter').addEventListener('click', () => { start.style.display = 'none'; if (!coarse) controls.lock(); }); renderer.domElement.addEventListener('click', () => { if (start.style.display === 'none' && !coarse) controls.lock(); });
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 1.6)); });
frame();
