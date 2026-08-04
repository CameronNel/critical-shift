import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

const $ = id => document.getElementById(id);
const clamp = THREE.MathUtils.clamp;
const coarse = matchMedia('(pointer: coarse)').matches;
const V = THREE.Vector3;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x081214);
scene.fog = new THREE.Fog(0x0b1a1c, 18, 70);

const camera = new THREE.PerspectiveCamera(coarse ? 66 : 70, innerWidth / innerHeight, .04, 140);
camera.rotation.order = 'YXZ';
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
} catch (error) {
  $('start-card').innerHTML = '<div class="eyebrow">WebGL unavailable</div><h1>REACTOR POOL</h1><p>This test requires a WebGL-capable browser.</p>';
  throw error;
}
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.2 : 1.55));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = coarse ? 1.22 : 1.15;
renderer.shadowMap.enabled = false;
document.body.prepend(renderer.domElement);

const visual = new THREE.Group();
const dynamic = new THREE.Group();
const colliderRoot = new THREE.Group();
const colliderMaterial = new THREE.MeshBasicMaterial({ visible: false });
scene.add(visual, dynamic);

function canvasTexture(painter, size = 512) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  painter(canvas.getContext('2d'), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

const concreteTexture = canvasTexture((ctx, s) => {
  ctx.fillStyle = '#59615f'; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 170; i++) {
    const shade = 62 + (i * 37) % 48;
    ctx.fillStyle = `rgba(${shade},${shade + 5},${shade + 3},${.035 + (i % 4) * .018})`;
    ctx.beginPath(); ctx.arc((i * 83) % s, (i * 137) % s, 2 + (i % 8), 0, Math.PI * 2); ctx.fill();
  }
  ctx.strokeStyle = 'rgba(20,28,28,.22)'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(0, 256); ctx.lineTo(s, 256); ctx.moveTo(256, 0); ctx.lineTo(256, s); ctx.stroke();
});
const metalTexture = canvasTexture((ctx, s) => {
  const gradient = ctx.createLinearGradient(0, 0, s, s);
  gradient.addColorStop(0, '#64716f'); gradient.addColorStop(.5, '#354442'); gradient.addColorStop(1, '#74817d');
  ctx.fillStyle = gradient; ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 45; i++) {
    ctx.strokeStyle = `rgba(222,211,178,${.025 + (i % 3) * .025})`; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo((i * 29) % s, 0); ctx.lineTo(((i * 29) % s) + 80, s); ctx.stroke();
  }
  for (let i = 0; i < 18; i++) {
    ctx.fillStyle = `rgba(113,52,29,${.08 + (i % 4) * .03})`;
    ctx.beginPath(); ctx.ellipse((i * 91) % s, (i * 57) % s, 8 + i % 5 * 3, 4 + i % 3 * 2, i, 0, Math.PI * 2); ctx.fill();
  }
});
concreteTexture.repeat.set(3, 3);
metalTexture.repeat.set(2.5, 2.5);

const mats = {
  concrete: new THREE.MeshStandardMaterial({ map: concreteTexture, color: 0x8b918c, roughness: .98 }),
  deck: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x51615f, roughness: .72, metalness: .42 }),
  steel: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x7b8783, roughness: .48, metalness: .68 }),
  darkSteel: new THREE.MeshStandardMaterial({ map: metalTexture, color: 0x263534, roughness: .67, metalness: .58 }),
  black: new THREE.MeshStandardMaterial({ color: 0x071012, roughness: .84, metalness: .18 }),
  rubber: new THREE.MeshStandardMaterial({ color: 0x161b1b, roughness: .98 }),
  amber: new THREE.MeshStandardMaterial({ color: 0xd79a37, roughness: .45, metalness: .38 }),
  amberGlow: new THREE.MeshStandardMaterial({ color: 0xf3bd55, emissive: 0x8d3f06, emissiveIntensity: 2.3, roughness: .28 }),
  teal: new THREE.MeshStandardMaterial({ color: 0x4db5a5, emissive: 0x123e3a, emissiveIntensity: .9, roughness: .36 }),
  green: new THREE.MeshStandardMaterial({ color: 0x67bd79, emissive: 0x123b1c, emissiveIntensity: .95, roughness: .4 }),
  red: new THREE.MeshStandardMaterial({ color: 0xd95743, emissive: 0x5d130a, emissiveIntensity: 1.15, roughness: .38 }),
  white: new THREE.MeshStandardMaterial({ color: 0xd7d7c7, roughness: .7, metalness: .1 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0x6aa9a5, transparent: true, opacity: .26, roughness: .1, metalness: .05, transmission: .18, side: THREE.DoubleSide }),
  water: new THREE.MeshPhysicalMaterial({ color: 0x1c8d93, emissive: 0x052f36, emissiveIntensity: .55, transparent: true, opacity: .58, roughness: .12, metalness: .12, side: THREE.DoubleSide }),
  waterGlow: new THREE.MeshBasicMaterial({ color: 0x127f86, transparent: true, opacity: .24, side: THREE.DoubleSide }),
  stripe: new THREE.MeshBasicMaterial({ color: 0xe2a444 }),
  ink: new THREE.MeshBasicMaterial({ color: 0x04090a }),
};

function addBox(w, h, d, material, position, rotation = [0, 0, 0], collide = false, parent = visual) {
  const geometry = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...position); mesh.rotation.set(...rotation); parent.add(mesh);
  if (collide) {
    const proxy = new THREE.Mesh(geometry.clone(), colliderMaterial);
    proxy.position.copy(mesh.position); proxy.rotation.copy(mesh.rotation); colliderRoot.add(proxy);
  }
  return mesh;
}
function addCylinder(radius, height, material, position, radial = 18, rotation = [0, 0, 0], parent = visual) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, radial), material);
  mesh.position.set(...position); mesh.rotation.set(...rotation); parent.add(mesh); return mesh;
}
function addRing(radius, tube, material, position, rotation = [Math.PI / 2, 0, 0], parent = visual) {
  const mesh = new THREE.Mesh(new THREE.TorusGeometry(radius, tube, 10, 40), material);
  mesh.position.set(...position); mesh.rotation.set(...rotation); parent.add(mesh); return mesh;
}
function addPipe(points, radius, material = mats.steel, parent = visual) {
  const curve = new THREE.CatmullRomCurve3(points.map(point => new V(...point)));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 28, radius, 8, false), material);
  parent.add(mesh); return mesh;
}
function label(text, color = '#ebddbc', width = 2.4) {
  const canvas = document.createElement('canvas'); canvas.width = 640; canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = 'rgba(3,10,12,.88)'; ctx.fillRect(8, 18, 624, 92);
  ctx.strokeStyle = color; ctx.globalAlpha = .7; ctx.lineWidth = 3; ctx.strokeRect(8, 18, 624, 92);
  ctx.globalAlpha = 1; ctx.fillStyle = color; ctx.font = '800 31px system-ui,sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, 320, 65);
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: true, depthWrite: false }));
  sprite.scale.set(width, width * .2, 1); return sprite;
}
function floorStripe(x, z, w, d, rotationY = 0) {
  const group = new THREE.Group(); group.position.set(x, .035, z); group.rotation.y = rotationY; visual.add(group);
  for (let i = 0; i < Math.ceil(w / .58); i++) {
    const stripe = addBox(.25, .018, d, mats.stripe, [-w / 2 + .28 + i * .58, 0, 0], [0, 0, -.58], false, group);
    stripe.renderOrder = 2;
  }
}
function addRail(x, y, z, w, d, rotation = [0, 0, 0], collide = true) {
  addBox(w, .10, d, mats.steel, [x, y + 1.0, z], rotation, collide);
  addBox(w, .08, d, mats.darkSteel, [x, y + .48, z], rotation, false);
}

/* --------------------------------------------------------------- shell */
// Ground deck is assembled around a genuine open pit. There is no invisible floor over the water.
addBox(7.4, .34, 15.0, mats.deck, [-8.25, -.17, -2.5], [0, 0, 0], true);
addBox(7.4, .34, 15.0, mats.deck, [8.25, -.17, -2.5], [0, 0, 0], true);
addBox(9.1, .34, 5.5, mats.deck, [0, -.17, -7.25], [0, 0, 0], true);
addBox(9.1, .34, 1.0, mats.deck, [0, -.17, 5.0], [0, 0, 0], true);
addBox(24.4, 12.0, .38, mats.concrete, [0, 5.8, -10.2], [0, 0, 0], true);
addBox(24.4, 12.0, .38, mats.concrete, [0, 5.8, 10.2], [0, 0, 0], true);
addBox(.38, 12.0, 20.4, mats.concrete, [-12.2, 5.8, 0], [0, 0, 0], true);
addBox(.38, 12.0, 20.4, mats.concrete, [12.2, 5.8, 0], [0, 0, 0], true);
for (const x of [-10.4, -5.2, 5.2, 10.4]) {
  addBox(.26, 10.8, .42, mats.darkSteel, [x, 5.4, -9.92]);
  addBox(1.15, .11, .4, mats.teal, [x, 9.5, -9.68]);
}
for (const z of [-8.4, -2.8, 2.8, 8.4]) {
  addBox(.42, 10.8, .26, mats.darkSteel, [-11.92, 5.4, z]);
  addBox(.42, 10.8, .26, mats.darkSteel, [11.92, 5.4, z]);
}
for (const x of [-9.5, -3.2, 3.2, 9.5]) {
  addBox(5.4, .22, .22, mats.steel, [x, 10.8, 0]);
  const light = new THREE.PointLight(0x80cabb, 1.8, 10, 2); light.position.set(x, 9.7, -1.2); scene.add(light);
}

/* --------------------------------------------------------- reactor pool */
const poolHalf = 4.55;
addBox(.30, 5.2, 9.1, mats.concrete, [-poolHalf, -2.55, 0]);
addBox(.30, 5.2, 9.1, mats.concrete, [poolHalf, -2.55, 0]);
addBox(9.1, 5.2, .30, mats.concrete, [0, -2.55, -poolHalf]);
addBox(9.1, 5.2, .30, mats.concrete, [0, -2.55, poolHalf]);
addBox(9.1, .28, 9.1, mats.darkSteel, [0, -5.17, 0]);
addBox(8.78, .04, 8.78, mats.water, [0, -.48, 0]);
addBox(7.8, .03, 7.8, mats.waterGlow, [0, -4.86, 0]);
for (const y of [-4.4, -2.5, -.72]) addRing(3.55, .08, mats.teal, [0, y, 0]);
for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) {
  const material = (x + z) % 3 === 0 ? mats.amberGlow : mats.darkSteel;
  addCylinder(.18, 3.5, material, [x * 1.15, -3.05, z * 1.15], 12);
  addRing(.26, .035, mats.steel, [x * 1.15, -1.30, z * 1.15]);
}
floorStripe(-5.05, 0, .8, 8.8, Math.PI / 2);
floorStripe(5.05, 0, .8, 8.8, Math.PI / 2);
floorStripe(0, -5.05, 8.8, .8);
floorStripe(0, 5.05, 8.8, .8);
// Guard rail surrounds the open pool; the west loading gantry has a controlled opening.
addRail(0, 0, -4.92, 8.8, .12);
addRail(0, 0, 4.92, 8.8, .12);
addRail(4.92, 0, 0, .12, 8.8);
addRail(-4.92, 0, -2.8, .12, 3.1);
addRail(-4.92, 0, 2.8, .12, 3.1);
addBox(.28, 1.15, 1.9, colliderMaterial, [-4.92, .56, 0], [0, 0, 0], false, colliderRoot);

const poolLight = new THREE.PointLight(0x35c5d0, 5.5, 18, 1.7); poolLight.position.set(0, -1.8, 0); scene.add(poolLight);
const fuelLight = new THREE.PointLight(0xffb044, 1.8, 11, 2); fuelLight.position.set(0, -3.1, 0); scene.add(fuelLight);

/* ------------------------------------------------------ control rods */
const controlRodMeshes = [];
for (const [x, z] of [[-.72, 0], [.72, 0], [0, -.72], [0, .72]]) {
  const group = new THREE.Group();
  const shaft = addCylinder(.13, 4.6, mats.black, [0, 0, 0], 10, [0, 0, 0], group);
  addCylinder(.20, .24, mats.red, [0, 2.12, 0], 12, [0, 0, 0], group);
  group.position.set(x, -2.65, z); dynamic.add(group); controlRodMeshes.push(group);
  shaft.userData.controlRod = true;
}

/* ------------------------------------------------------ control booth */
const boothFloorY = 5.18;
addBox(10.0, .34, 4.5, mats.deck, [-.35, 5.01, 7.28], [0, 0, 0], true);
addBox(10.0, .32, 4.5, mats.darkSteel, [-.35, 9.48, 7.28], [0, 0, 0], true);
addBox(10.0, .40, .34, mats.concrete, [-.35, 9.42, 9.45], [0, 0, 0], true);
addBox(10.0, 4.25, .34, mats.concrete, [-.35, 7.28, 9.45], [0, 0, 0], true);
addBox(.34, 4.25, 4.5, mats.concrete, [-5.35, 7.28, 7.28], [0, 0, 0], true);
// Right wall leaves a full-height exit onto the landing.
addBox(.34, 4.25, 1.15, mats.concrete, [4.65, 7.28, 5.72], [0, 0, 0], true);
addBox(.34, 4.25, 1.05, mats.concrete, [4.65, 7.28, 8.93], [0, 0, 0], true);
addBox(10.0, .78, .28, mats.concrete, [-.35, 5.57, 5.06], [0, 0, 0], true);
addBox(10.0, .35, .28, mats.steel, [-.35, 9.23, 5.06], [0, 0, 0], true);
addBox(9.6, 3.28, .08, mats.glass, [-.35, 7.38, 5.06]);
// Invisible full window collision prevents stepping into the pool hall from the booth.
addBox(9.8, 3.48, .18, colliderMaterial, [-.35, 7.38, 5.06], [0, 0, 0], false, colliderRoot);
for (const x of [-4.0, -1.7, .65, 3.0]) addBox(.10, 3.45, .18, mats.darkSteel, [x, 7.38, 5.0]);

const boothSign = label('ELEVATED REACTOR CONTROL', '#64c6b5', 4.2); boothSign.position.set(-.35, 8.85, 9.08); visual.add(boothSign);
const exitSign = label('SERVICE DECK →', '#e9ad4b', 2.0); exitSign.position.set(4.18, 8.35, 7.25); visual.add(exitSign);

/* ---------------------------------------------------- catwalk + ramp */
addBox(4.7, .30, 2.35, mats.deck, [6.95, 5.03, 7.05], [0, 0, 0], true);
addRail(6.95, boothFloorY, 8.22, 4.65, .12);
addRail(9.28, boothFloorY, 7.05, .12, 2.3);
const rampRun = 10.2, rampRise = boothFloorY, rampAngle = -Math.atan(rampRise / rampRun), rampLength = Math.hypot(rampRun, rampRise);
addBox(2.45, .28, rampLength, mats.deck, [8.0, rampRise / 2 - .05, 1.70], [rampAngle, 0, 0], true);
addRail(6.73, rampRise / 2, 1.70, .12, rampLength, [rampAngle, 0, 0]);
addRail(9.27, rampRise / 2, 1.70, .12, rampLength, [rampAngle, 0, 0]);
for (let i = 0; i < 16; i++) {
  const t = i / 15; const z = -3.4 + t * 10.2; const y = t * rampRise + .12;
  addBox(2.20, .035, .08, mats.amber, [8.0, y, z], [rampAngle, 0, 0]);
}

/* ------------------------------------------------------- interactions */
const interactionMeshes = [];
function actionMesh(mesh, id, name, detail, place) {
  mesh.userData.action = { id, name, detail, place }; interactionMeshes.push(mesh); return mesh;
}
function controlButton(x, name, id, detail, material = mats.teal) {
  const base = addBox(1.85, .76, .78, mats.darkSteel, [x, 5.62, 5.72], [-.30, 0, 0]);
  const screen = addBox(1.52, .08, .44, material, [x, 6.02, 5.61], [-.30, 0, 0]);
  actionMesh(screen, id, name, detail, 'ELEVATED CONTROL DESK');
  const tag = label(name, id === 'scram' ? '#ef7159' : '#64c6b5', 1.62); tag.position.set(x, 6.52, 5.66); visual.add(tag);
  return base;
}
controlButton(-3.45, 'COOLANT LOOP', 'authorise_cooling', 'authorise the primary coolant circuit');
controlButton(-1.25, 'CONTROL RODS', 'control_rods', 'cycle the rod bank between safe positions', mats.amberGlow);
controlButton(1.10, 'TURBINE LOAD', 'turbine_load', 'raise the turbine setpoint', mats.green);
controlButton(3.28, 'SCRAM', 'scram', 'drop every safety rod immediately', mats.red);
addBox(9.2, .62, .78, mats.darkSteel, [-.10, 5.39, 5.86], [-.16, 0, 0]);

// Status wall makes the booth read as an operating room rather than a row of anonymous blocks.
for (const [x, text, color] of [[-3.3, 'CORE TEMP', '#64c6b5'], [-1.1, 'ROD DEPTH', '#e9ad4b'], [1.1, 'GRID LOAD', '#64c6b5'], [3.3, 'SAFETY', '#ef7159']]) {
  addBox(1.85, 1.15, .16, mats.black, [x, 7.62, 9.18]);
  const tag = label(text, color, 1.55); tag.position.set(x, 7.88, 9.05); visual.add(tag);
  addBox(1.35, .12, .08, color === '#ef7159' ? mats.red : (color === '#e9ad4b' ? mats.amberGlow : mats.teal), [x, 7.34, 9.07]);
}

function stationCabinet({ x, z, yaw = 0, title, color = '#64c6b5', actions }) {
  addBox(3.4, .28, 1.35, mats.darkSteel, [x, .14, z], [0, yaw, 0]);
  addBox(3.05, 1.75, .72, mats.steel, [x, 1.10, z], [0, yaw, 0]);
  const normal = new V(Math.sin(yaw), 0, Math.cos(yaw));
  const side = new V(Math.cos(yaw), 0, -Math.sin(yaw));
  actions.forEach((action, index) => {
    const offset = (index - (actions.length - 1) / 2) * .82;
    const pos = new V(x, 2.02, z).addScaledVector(side, offset).addScaledVector(normal, -.37);
    const button = addBox(.56, .19, .40, action.red ? mats.red : (index === 0 ? mats.amberGlow : mats.teal), [pos.x, pos.y, pos.z], [0, yaw, 0]);
    actionMesh(button, action.id, action.name, action.detail, title);
  });
  const tag = label(title, color, 2.35); tag.position.set(x, 2.75, z); visual.add(tag);
}

// Fuel rack: rods are actual carried objects, not a menu counter.
addBox(3.6, .24, 1.5, mats.darkSteel, [-9.5, .12, -7.75]);
addBox(.18, 2.8, 1.3, mats.steel, [-11.05, 1.52, -7.75]);
addBox(.18, 2.8, 1.3, mats.steel, [-7.95, 1.52, -7.75]);
addBox(3.25, .16, 1.3, mats.steel, [-9.5, 2.83, -7.75]);
const rackRods = [];
for (let i = 0; i < 4; i++) {
  const x = -10.55 + i * .70;
  const rod = addCylinder(.16, 2.35, mats.amberGlow, [x, 1.40, -7.75], 12);
  addCylinder(.24, .18, mats.steel, [x, 2.58, -7.75], 12);
  rackRods.push(rod);
}
const rackButton = addBox(.72, .28, .45, mats.amberGlow, [-9.5, 1.15, -6.92]);
actionMesh(rackButton, 'pickup_fuel', 'PICK UP FUEL ROD', 'carry one assembly to the pool gantry', 'FUEL ROD RACK');
const rackLabel = label('FUEL ROD RACK', '#e9ad4b', 2.5); rackLabel.position.set(-9.5, 3.35, -7.70); visual.add(rackLabel);

// West-side loading gantry looks and behaves like a physical transfer machine.
for (const z of [-1.35, 1.35]) addBox(.24, 4.4, .24, mats.steel, [-6.18, 2.20, z]);
addBox(.24, 4.4, .24, mats.steel, [-4.90, 2.20, -1.35]);
addBox(.24, 4.4, .24, mats.steel, [-4.90, 2.20, 1.35]);
addBox(1.55, .24, 3.0, mats.amber, [-5.54, 4.34, 0]);
addBox(5.6, .20, .28, mats.steel, [-2.95, 4.10, 0]);
const hoist = addCylinder(.33, .42, mats.darkSteel, [-2.3, 3.92, 0], 14, [Math.PI / 2, 0, 0]);
addCylinder(.055, 4.0, mats.steel, [-2.3, 1.85, 0], 8);
const gantryButton = addBox(.72, .30, .46, mats.amberGlow, [-6.15, 1.25, 0]);
actionMesh(gantryButton, 'insert_fuel', 'INSERT FUEL ROD', 'lower the carried assembly into an open channel', 'POOL LOADING GANTRY');
const gantryLabel = label('POOL LOADING GANTRY', '#e9ad4b', 2.8); gantryLabel.position.set(-6.2, 4.85, 0); visual.add(gantryLabel);
hoist.userData.hoist = true;

// Pump skid is deliberately outside the booth so the operator has to leave the overlook.
for (const x of [7.2, 9.2]) {
  addCylinder(.72, 2.2, mats.teal, [x, 1.15, -7.45], 18, [0, 0, Math.PI / 2]);
  addRing(.72, .08, mats.steel, [x, 1.15, -7.45], [0, Math.PI / 2, 0]);
}
addPipe([[6.2, 1.1, -7.45], [5.4, 1.1, -7.45], [5.4, -.3, -4.8], [4.4, -.3, -4.1]], .18, mats.teal);
stationCabinet({ x: 8.2, z: -5.85, yaw: Math.PI, title: 'PRIMARY COOLANT PUMPS', actions: [
  { id: 'start_pumps', name: 'START PUMPS', detail: 'start both primary circulation pumps' },
  { id: 'open_valves', name: 'OPEN VALVES', detail: 'route coolant through the pool heat exchanger' },
  { id: 'emergency_cooling', name: 'EMERGENCY COOL', detail: 'spend reserve power on a hard flush', red: true },
] });

// Breakers, generator and waste are separate ground-floor jobs around the short loop.
for (const x of [-9.8, -8.55, -7.30]) {
  addBox(1.05, 3.25, .72, mats.darkSteel, [x, 1.63, 3.70]);
  addBox(.65, .42, .06, mats.teal, [x, 2.30, 3.32]);
}
const breaker = addBox(.76, .30, .48, mats.amberGlow, [-8.55, 1.25, 3.26]);
actionMesh(breaker, 'grid_breakers', 'CLOSE GRID BREAKERS', 'connect the turbine bus to the grid', 'GRID SWITCHGEAR');
const breakerLabel = label('GRID SWITCHGEAR', '#64c6b5', 2.5); breakerLabel.position.set(-8.55, 3.65, 3.70); visual.add(breakerLabel);

addCylinder(1.0, 2.6, mats.darkSteel, [5.65, 1.33, -8.0], 18, [0, 0, Math.PI / 2]);
addPipe([[5.65, 1.3, -7.0], [5.65, 1.3, -6.4], [6.8, 1.3, -6.0]], .14, mats.amber);
const generator = addBox(.76, .30, .48, mats.green, [5.65, 1.35, -6.66]);
actionMesh(generator, 'backup_generator', 'START BACKUP GENERATOR', 'restore emergency reserve power', 'BACKUP GENERATOR');
const generatorLabel = label('BACKUP GENERATOR', '#64c6b5', 2.4); generatorLabel.position.set(5.65, 3.05, -8.0); visual.add(generatorLabel);

for (const z of [3.45, 4.40]) addCylinder(.62, 2.6, mats.darkSteel, [9.1, 1.33, z], 18);
addPipe([[9.1, 2.6, 3.45], [9.1, 3.35, 3.45], [9.1, 3.35, 5.1]], .15, mats.steel);
const wasteButton = addBox(.76, .30, .48, mats.red, [8.0, 1.25, 3.92]);
actionMesh(wasteButton, 'waste_transfer', 'TRANSFER WASTE', 'pump the holding tank to shielded storage', 'WASTE HOLDING');
const wasteLabel = label('WASTE HOLDING', '#ef7159', 2.2); wasteLabel.position.set(9.05, 3.60, 4.0); visual.add(wasteLabel);

/* ------------------------------------------------------------ state */
const sim = {
  time: 0, temp: 32, coolant: 0, output: 0, demand: 45, waste: 0, reserve: 55,
  coolingAuthorised: false, pumps: false, valves: false, emergencyCooling: false,
  fuelCount: 0, carryingFuel: false, rodDepth: 100, targetRodDepth: 100,
  turbine: 0, breakers: false, alarm: false, autoShutdown: true, running: true,
  state: 'SHUTDOWN / SAFE', insertion: null,
};
const fuelSlots = [[-1.65, -1.65], [1.65, -1.65], [-1.65, 1.65], [1.65, 1.65]];
const insertedFuel = [];

const heldFuel = new THREE.Group();
addCylinder(.075, 1.30, mats.amberGlow, [0, 0, 0], 10, [0, 0, 0], heldFuel);
addCylinder(.12, .10, mats.steel, [0, .66, 0], 10, [0, 0, 0], heldFuel);
addCylinder(.12, .10, mats.steel, [0, -.66, 0], 10, [0, 0, 0], heldFuel);
heldFuel.position.set(.48, -.48, -.92); heldFuel.rotation.set(-.18, 0, -.34); heldFuel.visible = false; camera.add(heldFuel);

function toast(message, seconds = 2.5) {
  $('toast').textContent = message; $('toast').style.opacity = '1'; toast.time = seconds;
}
toast.time = 0;
function flash() { $('flash').style.opacity = '.34'; setTimeout(() => $('flash').style.opacity = '0', 130); }
function setState(text, alarm = sim.alarm) { sim.state = text; sim.alarm = alarm; }

function insertFuelRod() {
  if (!sim.carryingFuel) { toast('Bring a fuel rod from the rack first.'); return; }
  if (sim.fuelCount >= fuelSlots.length) { toast('All four fuel channels are occupied.'); return; }
  const [x, z] = fuelSlots[sim.fuelCount];
  const group = new THREE.Group();
  addCylinder(.16, 3.30, mats.amberGlow, [0, 0, 0], 12, [0, 0, 0], group);
  addCylinder(.24, .16, mats.steel, [0, 1.65, 0], 12, [0, 0, 0], group);
  group.position.set(x, 3.25, z); dynamic.add(group); insertedFuel.push(group);
  sim.insertion = { mesh: group, targetY: -3.05, speed: 1.35 };
  sim.carryingFuel = false; heldFuel.visible = false; sim.fuelCount++;
  toast(`Fuel rod ${sim.fuelCount}/4 locked to the gantry. Lowering into pool.`);
}

function cycleControlRods() {
  if (!sim.fuelCount) { toast('No fuel in the pool. Leave the booth and load a rod.'); return; }
  const positions = [100, 70, 40, 10];
  const current = positions.findIndex(value => Math.abs(value - sim.targetRodDepth) < 2);
  sim.targetRodDepth = positions[(current + 1) % positions.length];
  toast(`Control rod target: ${sim.targetRodDepth}% inserted.`);
}

function interact(action) {
  if (!action || !started) return;
  switch (action.id) {
    case 'authorise_cooling': sim.coolingAuthorised = true; toast('Coolant loop authorised. Start the pumps on the service deck.'); break;
    case 'control_rods': cycleControlRods(); break;
    case 'turbine_load':
      if (!sim.breakers) toast('Grid breakers are open. Close them on the service deck.');
      else if (!sim.fuelCount) toast('The turbine has no steam source.');
      else { sim.turbine = sim.turbine >= 1 ? .25 : sim.turbine + .25; toast(`Turbine setpoint: ${Math.round(sim.turbine * 100)}%.`); }
      break;
    case 'scram': sim.targetRodDepth = 100; sim.turbine = 0; sim.breakers = false; sim.alarm = false; sim.emergencyCooling = false; setState('SCRAM / SAFE'); flash(); toast('SCRAM — all safety rods dropping.'); break;
    case 'pickup_fuel':
      if (sim.carryingFuel) toast('You are already carrying a fuel rod.');
      else if (sim.fuelCount >= 4) toast('No more fuel is required.');
      else { sim.carryingFuel = true; heldFuel.visible = true; if (rackRods[sim.fuelCount]) rackRods[sim.fuelCount].visible = false; toast('Fuel rod lifted. Take it to the west pool gantry.'); }
      break;
    case 'insert_fuel': insertFuelRod(); break;
    case 'start_pumps':
      if (!sim.coolingAuthorised) toast('Authorise the loop from the elevated control booth first.');
      else { sim.pumps = true; toast('Primary pumps spinning up. Open the coolant valves.'); }
      break;
    case 'open_valves':
      if (!sim.pumps) toast('Pumps are offline.');
      else { sim.valves = true; toast('Coolant valves open. Flow established through the pool.'); }
      break;
    case 'emergency_cooling':
      if (sim.reserve < 15) toast('Reserve power is too low for emergency cooling.');
      else { sim.reserve -= 15; sim.emergencyCooling = true; sim.coolant = 100; sim.temp = Math.max(50, sim.temp - 135); flash(); toast('Emergency cooling dumped into the pool.'); }
      break;
    case 'grid_breakers': sim.breakers = !sim.breakers; toast(sim.breakers ? 'Grid breakers closed.' : 'Grid breakers opened.'); break;
    case 'backup_generator': sim.reserve = clamp(sim.reserve + 30, 0, 100); toast('Backup generator online. Reserve restored.'); break;
    case 'waste_transfer': sim.waste = Math.max(0, sim.waste - 65); toast('Waste transferred to shielded storage.'); break;
  }
  updateHud();
}

function objectiveText() {
  if (!sim.coolingAuthorised) return 'Authorise the coolant loop from the control desk.';
  if (!sim.pumps) return 'Leave the booth. Take the right exit and ramp down to the pumps.';
  if (!sim.valves) return 'Open the coolant valves at the pump skid.';
  if (!sim.fuelCount && !sim.carryingFuel) return 'Collect a fuel rod from the rack beyond the pool.';
  if (sim.carryingFuel) return 'Carry the rod to the west-side loading gantry.';
  if (sim.targetRodDepth === 100) return 'Return upstairs and withdraw the control rods.';
  if (!sim.breakers) return 'Close the grid breakers on the service deck.';
  if (sim.output < sim.demand * .75) return 'Set turbine load from the elevated control desk.';
  if (sim.waste > 65) return 'Transfer waste before the holding tanks fill.';
  if (sim.alarm) return 'Stabilise cooling or hit SCRAM.';
  return 'Hold grid output and watch the pool.';
}
function zoneText() {
  const p = camera.position;
  if (p.y > 4.5 && p.x < 5.0) return 'ELEVATED CONTROL BOOTH';
  if (p.x > 6.5 && p.y > .9) return 'SERVICE ACCESS RAMP';
  if (p.x < -6.5 && p.z < -5.5) return 'FUEL ROD STORAGE';
  if (p.x < -5.0 && Math.abs(p.z) < 2.8) return 'POOL LOADING GANTRY';
  if (p.x > 5.5 && p.z < -4.0) return 'PRIMARY PUMP BAY';
  if (p.x < -6.0 && p.z > 2.0) return 'GRID SWITCHGEAR';
  return 'REACTOR SERVICE DECK';
}
function updateHud() {
  $('temp').textContent = `${Math.round(sim.temp)}°`;
  $('cool').textContent = `${Math.round(sim.coolant)}%`;
  $('output').textContent = `${Math.round(sim.output)} MW`;
  $('demand').textContent = `${Math.round(sim.demand)} MW`;
  $('rods').textContent = `${Math.round(sim.rodDepth)}%`;
  $('fuel').textContent = `${sim.fuelCount}/4`;
  $('temp').parentElement.classList.toggle('hot', sim.temp > 590);
  $('state').textContent = sim.state; $('state').classList.toggle('alarm', sim.alarm || sim.temp > 610);
  $('carry').classList.toggle('on', sim.carryingFuel);
  $('objective').textContent = objectiveText(); $('zone').textContent = zoneText();
  const prompt = $('prompt');
  if (focused && started) {
    prompt.classList.add('on'); $('prompt-action').textContent = `[E] ${focused.name}`; $('prompt-detail').textContent = focused.detail; $('prompt-place').textContent = focused.place;
  } else prompt.classList.remove('on');
}

function simulate(dt) {
  if (!started) return;
  sim.time += dt; sim.demand = 45 + Math.sin(sim.time * .08) * 8 + Math.max(0, Math.sin(sim.time * .021)) * 20;
  sim.rodDepth = THREE.MathUtils.damp(sim.rodDepth, sim.targetRodDepth, 2.7, dt);
  const rodY = -2.65 + (100 - sim.rodDepth) / 100 * 5.2;
  for (const rod of controlRodMeshes) rod.position.y = rodY;
  if (sim.insertion) {
    sim.insertion.mesh.position.y = Math.max(sim.insertion.targetY, sim.insertion.mesh.position.y - sim.insertion.speed * dt);
    if (sim.insertion.mesh.position.y <= sim.insertion.targetY + .01) { toast('Fuel assembly seated in the core lattice.'); sim.insertion = null; }
  }
  const coolingReady = sim.coolingAuthorised && sim.pumps && sim.valves;
  const targetCoolant = coolingReady ? (sim.emergencyCooling ? 100 : 82) : (sim.pumps ? 24 : 0);
  sim.coolant = THREE.MathUtils.damp(sim.coolant, targetCoolant, 1.5, dt);
  const fuelPower = sim.fuelCount / 4;
  const reactivity = fuelPower * (1 - sim.rodDepth / 100);
  sim.output = sim.breakers ? sim.turbine * reactivity * 155 : 0;
  sim.temp += (reactivity * 118 + sim.output * .055 - sim.coolant * .085 - 4.2) * dt;
  sim.temp = clamp(sim.temp, 32, 1020);
  sim.waste = clamp(sim.waste + sim.output * .0021 * dt, 0, 100);
  if (sim.temp > 590 || sim.waste > 82) sim.alarm = true;
  if (sim.temp > 710 && sim.autoShutdown) { sim.targetRodDepth = 100; sim.turbine = 0; setState('AUTO-SHUTDOWN', true); }
  else if (sim.temp > 880) { setState('CORE DAMAGE / EVACUATE', true); sim.running = false; sim.output = 0; }
  else if (sim.alarm) setState(sim.temp > 650 ? 'COOLING EMERGENCY' : 'ALARM / CHECK SYSTEMS', true);
  else if (sim.output > 1) setState('ONLINE / GENERATING');
  else if (sim.fuelCount) setState('FUEL LOADED / STANDBY');
  else setState('SHUTDOWN / SAFE', false);
  poolLight.intensity = 4.5 + fuelPower * 4 + reactivity * 4;
  fuelLight.intensity = 1.2 + fuelPower * 3.8;
  updateHud();
}

/* ---------------------------------------------------------- targeting */
const raycaster = new THREE.Raycaster();
let focused = null;
function findAction() {
  raycaster.setFromCamera({ x: 0, y: 0 }, camera);
  const hit = raycaster.intersectObjects(interactionMeshes, false).find(item => item.distance < 4.3);
  if (hit) return hit.object.userData.action;
  let nearest = null, nearestDistance = 2.7;
  const forward = new V(); camera.getWorldDirection(forward);
  for (const mesh of interactionMeshes) {
    const point = mesh.getWorldPosition(new V()); const distance = point.distanceTo(camera.position);
    if (distance >= nearestDistance) continue;
    const direction = point.sub(camera.position).normalize();
    if (forward.dot(direction) > .24) { nearest = mesh.userData.action; nearestDistance = distance; }
  }
  return nearest;
}

/* ----------------------------------------------------------- movement */
colliderRoot.updateMatrixWorld(true);
const worldOctree = new Octree().fromGraphNode(colliderRoot);
const spawn = new V(0, boothFloorY, 7.35);
const playerCollider = new Capsule(new V(spawn.x, spawn.y + .35, spawn.z), new V(spawn.x, spawn.y + 1.65, spawn.z), .35);
const velocity = new V();
const controls = new PointerLockControls(camera, renderer.domElement);
scene.add(camera); camera.position.copy(playerCollider.end);
let playerOnFloor = false, jumpQueued = false, started = false;
const keys = {};
const moveDirection = new V();

function resetPlayer(message = 'Back in the elevated control booth.') {
  playerCollider.start.set(spawn.x, spawn.y + .35, spawn.z); playerCollider.end.set(spawn.x, spawn.y + 1.65, spawn.z);
  velocity.set(0, 0, 0); camera.position.copy(playerCollider.end);
  if (coarse) { camera.rotation.set(-.28, 0, 0); touchYaw = 0; touchPitch = -.28; }
  toast(message);
}
function resetShift() {
  Object.assign(sim, { time: 0, temp: 32, coolant: 0, output: 0, demand: 45, waste: 0, reserve: 55, coolingAuthorised: false, pumps: false, valves: false, emergencyCooling: false, fuelCount: 0, carryingFuel: false, rodDepth: 100, targetRodDepth: 100, turbine: 0, breakers: false, alarm: false, autoShutdown: true, running: true, state: 'SHUTDOWN / SAFE', insertion: null });
  for (const mesh of insertedFuel) dynamic.remove(mesh); insertedFuel.length = 0;
  rackRods.forEach(rod => { rod.visible = true; }); heldFuel.visible = false; resetPlayer('Shift reset. Start from the control desk.'); updateHud();
}
function getForward() { camera.getWorldDirection(moveDirection); moveDirection.y = 0; return moveDirection.normalize(); }
function getSide() { getForward(); return moveDirection.cross(camera.up).normalize(); }
function resolveCollisions() {
  playerOnFloor = false;
  for (let i = 0; i < 5; i++) {
    const result = worldOctree.capsuleIntersect(playerCollider); if (!result) break;
    playerOnFloor ||= result.normal.y > .38;
    playerCollider.translate(result.normal.clone().multiplyScalar(result.depth));
    if (result.normal.y > .38 && velocity.y < 0) velocity.y = 0;
    else velocity.addScaledVector(result.normal, -result.normal.dot(velocity));
  }
}
const joy = { x: 0, y: 0 };
function movePlayer(dt) {
  const forwardInput = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0) - joy.y;
  const sideInput = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0) + joy.x;
  const sprint = keys.ShiftLeft || keys.ShiftRight;
  const acceleration = playerOnFloor ? (sprint ? 27 : 20) : 7;
  if (forwardInput) velocity.addScaledVector(getForward(), forwardInput * acceleration * dt);
  if (sideInput) velocity.addScaledVector(getSide(), sideInput * acceleration * dt);
  if ((keys.Space || jumpQueued) && playerOnFloor) velocity.y = 5.25;
  jumpQueued = false;
  let damping = Math.exp(-8.5 * dt) - 1;
  if (!playerOnFloor) { velocity.y -= 18.5 * dt; damping *= .10; }
  velocity.addScaledVector(velocity, damping);
  const speedLimit = (sprint ? 5.0 : 3.35) * (sim.carryingFuel ? .82 : 1);
  const planar = Math.hypot(velocity.x, velocity.z);
  if (planar > speedLimit) { velocity.x *= speedLimit / planar; velocity.z *= speedLimit / planar; }
  playerCollider.translate(velocity.clone().multiplyScalar(dt)); resolveCollisions(); camera.position.copy(playerCollider.end);
  if (camera.position.y < -7.0) resetPlayer('Recovered from the pool access ladder.');
}

addEventListener('keydown', event => {
  keys[event.code] = true;
  if (['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space', 'ShiftLeft', 'ShiftRight'].includes(event.code)) event.preventDefault();
  if (!event.repeat && event.code === 'KeyE') interact(focused);
  if (!event.repeat && event.code === 'KeyR') resetShift();
});
addEventListener('keyup', event => { keys[event.code] = false; });

let touchYaw = 0, touchPitch = -.28, looking = false, lastLook = null;
const lookZone = $('look-zone');
lookZone.addEventListener('pointerdown', event => { looking = true; lastLook = { x: event.clientX, y: event.clientY }; lookZone.setPointerCapture(event.pointerId); });
lookZone.addEventListener('pointermove', event => {
  if (!looking) return;
  touchYaw -= (event.clientX - lastLook.x) * .0045; touchPitch = clamp(touchPitch - (event.clientY - lastLook.y) * .0040, -1.42, 1.35);
  lastLook = { x: event.clientX, y: event.clientY }; camera.rotation.set(touchPitch, touchYaw, 0);
});
lookZone.addEventListener('pointerup', () => { looking = false; });
lookZone.addEventListener('pointercancel', () => { looking = false; });

const stick = $('stick'), knob = $('knob');
function setJoy(event) {
  const rect = stick.getBoundingClientRect(), cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2, max = rect.width * .34;
  let dx = event.clientX - cx, dy = event.clientY - cy; const length = Math.hypot(dx, dy) || 1;
  if (length > max) { dx *= max / length; dy *= max / length; }
  joy.x = dx / max; joy.y = dy / max; knob.style.transform = `translate(${dx}px,${dy}px)`;
}
function clearJoy() { joy.x = joy.y = 0; knob.style.transform = 'translate(0,0)'; }
stick.addEventListener('pointerdown', event => { stick.setPointerCapture(event.pointerId); setJoy(event); });
stick.addEventListener('pointermove', event => { if (stick.hasPointerCapture(event.pointerId)) setJoy(event); });
stick.addEventListener('pointerup', clearJoy); stick.addEventListener('pointercancel', clearJoy);
$('jump-button').addEventListener('pointerdown', () => { jumpQueued = true; });
$('use-button').addEventListener('pointerdown', event => { event.preventDefault(); interact(focused); });
$('restart-button').addEventListener('pointerdown', () => resetShift());

$('enter').addEventListener('click', () => {
  started = true; $('start').style.display = 'none';
  if (!coarse) controls.lock(); else camera.rotation.set(touchPitch, touchYaw, 0);
  toast('You are above the pool. Authorise coolant, then use the right-hand exit.');
});
renderer.domElement.addEventListener('click', () => { if (started && !coarse && !controls.isLocked) controls.lock(); });
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.2 : 1.55));
});

const hemisphere = new THREE.HemisphereLight(0x9bcfc7, 0x081011, 1.15); scene.add(hemisphere);
const warmFill = new THREE.DirectionalLight(0xffc675, .92); warmFill.position.set(-8, 14, 7); scene.add(warmFill);
const alarmLight = new THREE.PointLight(0xee6048, 0, 18, 2); alarmLight.position.set(0, 9, 6.5); scene.add(alarmLight);

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, .05); last = now;
  movePlayer(dt); focused = findAction(); simulate(dt);
  alarmLight.intensity = sim.alarm ? 3 + Math.abs(Math.sin(sim.time * 7.5)) * 3 : 0;
  if (toast.time > 0) { toast.time -= dt; if (toast.time <= 0) $('toast').style.opacity = '0'; }
  renderer.render(scene, camera); requestAnimationFrame(frame);
}

camera.position.copy(playerCollider.end); camera.rotation.set(-.28, 0, 0); updateHud(); requestAnimationFrame(frame);
