import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

import { configureKit, fuelAssembly } from './art/kit.js';
import { setMaterialQuality } from './art/materials.js';
import { createLightRig } from './art/lighting.js';
import { createPostChain } from './art/post.js';
import { createDust } from './art/particles.js';
import { buildRoom, ROOM } from './scene/room.js';
import { buildBooth } from './scene/booth.js';
import { buildMachines } from './scene/machines.js';

const $ = id => document.getElementById(id);
const clamp = THREE.MathUtils.clamp;
const coarse = matchMedia('(pointer: coarse)').matches;
const V = THREE.Vector3;

/* ------------------------------------------------------------- quality */

/**
 * Two tiers, picked from the pointer type and the device's core count. The high
 * tier is what the screenshots are taken at; the low tier keeps the same
 * materials and the same pool shader but drops shadows, halves the particle
 * counts and turns the normal maps off.
 *
 * `G`, or the GFX button on touch, toggles the parts that can change without
 * rebuilding the scene.
 */
const lowPower = coarse || (navigator.hardwareConcurrency || 4) <= 4;
const QUALITY = lowPower
  ? {
    name: 'LOW',
    shadows: false, shadowCasters: 0, shadowMapSize: 512,
    normalMaps: false, bevels: true, detail: 0.5, anisotropy: 2,
    bloomStrength: 0.5, bloomRadius: 0.7, bloomThreshold: 0.95,
    pixelRatio: 1.15, dust: 90,
  }
  : {
    name: 'HIGH',
    shadows: true, shadowCasters: 2, shadowMapSize: 1024,
    normalMaps: true, bevels: true, detail: 1, anisotropy: 8,
    bloomStrength: 0.58, bloomRadius: 0.8, bloomThreshold: 0.92,
    pixelRatio: 1.5, dust: 240,
  };

/* -------------------------------------------------------------- renderer */

const scene = new THREE.Scene();
scene.background = new THREE.Color('#161b1e');
scene.fog = new THREE.Fog('#1d2429', 16, 62);

const camera = new THREE.PerspectiveCamera(coarse ? 68 : 72, innerWidth / innerHeight, 0.04, 160);
camera.rotation.order = 'YXZ';

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: !lowPower, powerPreference: 'high-performance' });
} catch (error) {
  $('start-card').innerHTML = '<div class="eyebrow">WebGL unavailable</div><h1>REACTOR POOL</h1><p>This test requires a WebGL-capable browser.</p>';
  throw error;
}
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, QUALITY.pixelRatio));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.98;
renderer.shadowMap.enabled = QUALITY.shadows;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);

const visual = new THREE.Group();
const dynamic = new THREE.Group();
const colliderRoot = new THREE.Group();
scene.add(visual, dynamic);

/* ----------------------------------------------------------- build order */

setMaterialQuality({ normalMaps: QUALITY.normalMaps, anisotropy: QUALITY.anisotropy });
configureKit({ visual, collider: colliderRoot, quality: QUALITY });

const lights = createLightRig(scene, renderer, QUALITY);

const interactionMeshes = [];
function register(mesh, action) {
  mesh.userData.action = action;
  interactionMeshes.push(mesh);
}

const fuelSlots = [[-1.65, -1.65], [1.65, -1.65], [-1.65, 1.65], [1.65, 1.65]];

const room = buildRoom({ scene, visual, lights, quality: QUALITY, fuelSlots });
const booth = buildBooth({ visual, lights, register });
const machines = buildMachines({ visual, lights, register, quality: QUALITY });

const dust = createDust({ x: 24, y: 11, z: 20 }, QUALITY.dust);
scene.add(dust.points);

const post = createPostChain(renderer, scene, camera, QUALITY);

/* --------------------------------------------------------------- state */

const sim = {
  time: 0, temp: 32, coolant: 0, output: 0, demand: 45, waste: 0, reserve: 55,
  coolingAuthorised: false, pumps: false, valves: false, emergencyCooling: false,
  fuelCount: 0, carryingFuel: false, rodDepth: 100, targetRodDepth: 100,
  turbine: 0, breakers: false, alarm: false, autoShutdown: true, running: true,
  state: 'SHUTDOWN / SAFE', insertion: null, alarmPhase: 0, rodMoving: false,
  pool: { glow: 0, agitation: 0, activeShafts: 0 },
};
const insertedFuel = [];

// The carried assembly, parented to the camera. Same kit piece as the racked and
// the seated rods, so a fuel rod looks like a fuel rod wherever it is.
const heldFuel = fuelAssembly({ length: 1.25, radius: 0.08, heat: 0.7 });
heldFuel.position.set(0.5, -0.52, -0.9);
heldFuel.rotation.set(-0.2, 0.3, -0.36);
heldFuel.visible = false;
camera.add(heldFuel);

function toast(message, seconds = 2.6) {
  $('toast').textContent = message;
  $('toast').style.opacity = '1';
  toast.time = seconds;
}
toast.time = 0;
function flash() {
  $('flash').style.opacity = '.34';
  setTimeout(() => ($('flash').style.opacity = '0'), 130);
}
function setState(text, alarm = sim.alarm) { sim.state = text; sim.alarm = alarm; }

function insertFuelRod() {
  if (!sim.carryingFuel) { toast('Bring a fuel rod from the rack first.'); return; }
  if (sim.fuelCount >= fuelSlots.length) { toast('All four fuel channels are occupied.'); return; }
  const [x, z] = fuelSlots[sim.fuelCount];
  const assembly = fuelAssembly({ length: 2.4, radius: 0.15, heat: 1 });
  assembly.position.set(x, 3.4, z);
  dynamic.add(assembly);
  insertedFuel.push(assembly);
  sim.insertion = { mesh: assembly, targetY: -2.95, speed: 1.5 };
  sim.carryingFuel = false;
  heldFuel.visible = false;
  sim.fuelCount++;
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
    case 'authorise_cooling':
      sim.coolingAuthorised = true;
      toast('Coolant loop authorised. Start the pumps on the service deck.');
      break;
    case 'control_rods': cycleControlRods(); break;
    case 'turbine_load':
      if (!sim.breakers) toast('Grid breakers are open. Close them on the service deck.');
      else if (!sim.fuelCount) toast('The turbine has no steam source.');
      else { sim.turbine = sim.turbine >= 1 ? 0.25 : sim.turbine + 0.25; toast(`Turbine setpoint: ${Math.round(sim.turbine * 100)}%.`); }
      break;
    case 'scram':
      sim.targetRodDepth = 100; sim.turbine = 0; sim.breakers = false;
      sim.alarm = false; sim.emergencyCooling = false;
      setState('SCRAM / SAFE'); flash(); toast('SCRAM — all safety rods dropping.');
      break;
    case 'pickup_fuel':
      if (sim.carryingFuel) toast('You are already carrying a fuel rod.');
      else if (sim.fuelCount >= 4) toast('No more fuel is required.');
      else { sim.carryingFuel = true; heldFuel.visible = true; toast('Fuel rod lifted. Take it to the west pool gantry.'); }
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
      else {
        sim.reserve -= 15; sim.emergencyCooling = true; sim.coolant = 100;
        sim.temp = Math.max(50, sim.temp - 135); flash();
        toast('Emergency cooling dumped into the pool.');
      }
      break;
    case 'grid_breakers':
      sim.breakers = !sim.breakers;
      toast(sim.breakers ? 'Grid breakers closed.' : 'Grid breakers opened.');
      break;
    case 'backup_generator':
      sim.reserve = clamp(sim.reserve + 30, 0, 100);
      toast('Backup generator online. Reserve restored.');
      break;
    case 'waste_transfer':
      sim.waste = Math.max(0, sim.waste - 65);
      toast('Waste transferred to shielded storage.');
      break;
  }
  updateHud();
}

/* ------------------------------------------------------------------ hud */

function objectiveText() {
  if (!sim.coolingAuthorised) return 'Authorise the coolant loop from the control desk.';
  if (!sim.pumps) return 'Leave the booth. Take the right exit and ramp down to the pumps.';
  if (!sim.valves) return 'Open the coolant valves at the pump skid.';
  if (!sim.fuelCount && !sim.carryingFuel) return 'Collect a fuel rod from the rack beyond the pool.';
  if (sim.carryingFuel) return 'Carry the rod to the west-side loading gantry.';
  if (sim.targetRodDepth === 100) return 'Return upstairs and withdraw the control rods.';
  if (!sim.breakers) return 'Close the grid breakers on the service deck.';
  if (sim.output < sim.demand * 0.75) return 'Set turbine load from the elevated control desk.';
  if (sim.waste > 65) return 'Transfer waste before the holding tanks fill.';
  if (sim.alarm) return 'Stabilise cooling or hit SCRAM.';
  return 'Hold grid output and watch the pool.';
}

function zoneText() {
  const p = camera.position;
  if (p.y > 4.5 && p.x < 5.0) return 'ELEVATED CONTROL BOOTH';
  if (p.x > 6.5 && p.y > 0.9) return 'SERVICE ACCESS RAMP';
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
  $('state').textContent = sim.state;
  $('state').classList.toggle('alarm', sim.alarm || sim.temp > 610);
  $('carry').classList.toggle('on', sim.carryingFuel);
  $('objective').textContent = objectiveText();
  $('zone').textContent = zoneText();
  const prompt = $('prompt');
  if (focused && started) {
    prompt.classList.add('on');
    $('prompt-action').textContent = `[E] ${focused.name}`;
    $('prompt-detail').textContent = focused.detail;
    $('prompt-place').textContent = focused.place;
  } else prompt.classList.remove('on');
}

/* ------------------------------------------------------------ simulation */

function simulate(dt) {
  if (!started) return;
  sim.time += dt;
  sim.alarmPhase += dt * 7.5;
  sim.demand = 45 + Math.sin(sim.time * 0.08) * 8 + Math.max(0, Math.sin(sim.time * 0.021)) * 20;
  const previousDepth = sim.rodDepth;
  sim.rodDepth = THREE.MathUtils.damp(sim.rodDepth, sim.targetRodDepth, 2.7, dt);
  sim.rodMoving = Math.abs(sim.rodDepth - previousDepth) > 0.02;

  if (sim.insertion) {
    sim.insertion.mesh.position.y = Math.max(
      sim.insertion.targetY,
      sim.insertion.mesh.position.y - sim.insertion.speed * dt,
    );
    if (sim.insertion.mesh.position.y <= sim.insertion.targetY + 0.01) {
      toast('Fuel assembly seated in the core lattice.');
      sim.insertion = null;
    }
  }

  const coolingReady = sim.coolingAuthorised && sim.pumps && sim.valves;
  const targetCoolant = coolingReady ? (sim.emergencyCooling ? 100 : 82) : (sim.pumps ? 24 : 0);
  sim.coolant = THREE.MathUtils.damp(sim.coolant, targetCoolant, 1.5, dt);
  const fuelPower = sim.fuelCount / 4;
  const reactivity = fuelPower * (1 - sim.rodDepth / 100);
  sim.output = sim.breakers ? sim.turbine * reactivity * 155 : 0;
  sim.temp += (reactivity * 118 + sim.output * 0.055 - sim.coolant * 0.085 - 4.2) * dt;
  sim.temp = clamp(sim.temp, 32, 1020);
  sim.waste = clamp(sim.waste + sim.output * 0.0021 * dt, 0, 100);
  if (sim.temp > 590 || sim.waste > 82) sim.alarm = true;
  if (sim.temp > 710 && sim.autoShutdown) { sim.targetRodDepth = 100; sim.turbine = 0; setState('AUTO-SHUTDOWN', true); }
  else if (sim.temp > 880) { setState('CORE DAMAGE / EVACUATE', true); sim.running = false; sim.output = 0; }
  else if (sim.alarm) setState(sim.temp > 650 ? 'COOLING EMERGENCY' : 'ALARM / CHECK SYSTEMS', true);
  else if (sim.output > 1) setState('ONLINE / GENERATING');
  else if (sim.fuelCount) setState('FUEL LOADED / STANDBY');
  else setState('SHUTDOWN / SAFE', false);

  // The pool is driven by two numbers: how hard the core is running, and how
  // hard the coolant is moving through it.
  sim.pool.glow = clamp(fuelPower * 0.3 + reactivity * 0.9 + (sim.temp - 32) / 1600, 0, 1.3);
  sim.pool.agitation = clamp(sim.coolant / 100, 0, 1);
  sim.pool.activeShafts = sim.fuelCount;

  for (const assembly of insertedFuel) {
    assembly.userData.core.emissiveIntensity = 1.4 + reactivity * 5.6 + fuelPower * 1.2;
  }

  room.update(dt, sim);
  booth.update(dt, sim);
  machines.update(dt, sim);
  lights.update(dt, {
    alarmOn: sim.alarm,
    alarmPhase: sim.alarmPhase,
    power: sim.temp > 880 ? 0.35 : 1,
  });
  updateHud();
}

/* ---------------------------------------------------------- targeting */

const raycaster = new THREE.Raycaster();
let focused = null;
function findAction() {
  raycaster.setFromCamera({ x: 0, y: 0 }, camera);
  const hit = raycaster.intersectObjects(interactionMeshes, false).find(item => item.distance < 4.3);
  if (hit) return hit.object.userData.action;
  let nearest = null;
  let nearestDistance = 2.7;
  const forward = new V();
  camera.getWorldDirection(forward);
  for (const mesh of interactionMeshes) {
    const point = mesh.getWorldPosition(new V());
    const distance = point.distanceTo(camera.position);
    if (distance >= nearestDistance) continue;
    const direction = point.sub(camera.position).normalize();
    if (forward.dot(direction) > 0.24) { nearest = mesh.userData.action; nearestDistance = distance; }
  }
  return nearest;
}

/* ----------------------------------------------------------- movement */

colliderRoot.updateMatrixWorld(true);
const worldOctree = new Octree().fromGraphNode(colliderRoot);
const boothFloorY = 5.18;
const spawn = new V(0, boothFloorY, 7.35);
const playerCollider = new Capsule(
  new V(spawn.x, spawn.y + 0.35, spawn.z),
  new V(spawn.x, spawn.y + 1.65, spawn.z),
  0.35,
);
const velocity = new V();
const controls = new PointerLockControls(camera, renderer.domElement);
scene.add(camera);
camera.position.copy(playerCollider.end);
let playerOnFloor = false;
let jumpQueued = false;
let started = false;
let bobPhase = 0;
const keys = {};
const moveDirection = new V();

function resetPlayer(message = 'Back in the elevated control booth.') {
  playerCollider.start.set(spawn.x, spawn.y + 0.35, spawn.z);
  playerCollider.end.set(spawn.x, spawn.y + 1.65, spawn.z);
  velocity.set(0, 0, 0);
  camera.position.copy(playerCollider.end);
  if (coarse) { camera.rotation.set(-0.28, 0, 0); touchYaw = 0; touchPitch = -0.28; }
  toast(message);
}

function resetShift() {
  Object.assign(sim, {
    time: 0, temp: 32, coolant: 0, output: 0, demand: 45, waste: 0, reserve: 55,
    coolingAuthorised: false, pumps: false, valves: false, emergencyCooling: false,
    fuelCount: 0, carryingFuel: false, rodDepth: 100, targetRodDepth: 100,
    turbine: 0, breakers: false, alarm: false, autoShutdown: true, running: true,
    state: 'SHUTDOWN / SAFE', insertion: null,
  });
  for (const mesh of insertedFuel) dynamic.remove(mesh);
  insertedFuel.length = 0;
  heldFuel.visible = false;
  resetPlayer('Shift reset. Start from the control desk.');
  updateHud();
}

function getForward() { camera.getWorldDirection(moveDirection); moveDirection.y = 0; return moveDirection.normalize(); }
function getSide() { getForward(); return moveDirection.cross(camera.up).normalize(); }

function resolveCollisions() {
  playerOnFloor = false;
  for (let i = 0; i < 5; i++) {
    const result = worldOctree.capsuleIntersect(playerCollider);
    if (!result) break;
    playerOnFloor ||= result.normal.y > 0.38;
    playerCollider.translate(result.normal.clone().multiplyScalar(result.depth));
    if (result.normal.y > 0.38 && velocity.y < 0) velocity.y = 0;
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
  if (!playerOnFloor) { velocity.y -= 18.5 * dt; damping *= 0.1; }
  velocity.addScaledVector(velocity, damping);
  const speedLimit = (sprint ? 5.0 : 3.35) * (sim.carryingFuel ? 0.82 : 1);
  const planar = Math.hypot(velocity.x, velocity.z);
  if (planar > speedLimit) { velocity.x *= speedLimit / planar; velocity.z *= speedLimit / planar; }
  playerCollider.translate(velocity.clone().multiplyScalar(dt));
  resolveCollisions();
  camera.position.copy(playerCollider.end);
  // Head bob, scaled by speed. Enough to read as weight, not enough to nauseate.
  if (playerOnFloor && planar > 0.4) {
    bobPhase += dt * planar * 2.4;
    camera.position.y += Math.sin(bobPhase) * 0.022;
  }
  if (camera.position.y < ROOM.poolFloorY - 2) resetPlayer('Recovered from the pool access ladder.');
}

/* -------------------------------------------------------------- input */

addEventListener('keydown', event => {
  keys[event.code] = true;
  if (['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space', 'ShiftLeft', 'ShiftRight'].includes(event.code)) event.preventDefault();
  if (!event.repeat && event.code === 'KeyE') interact(focused);
  if (!event.repeat && event.code === 'KeyR') resetShift();
  if (!event.repeat && event.code === 'KeyG') toggleGraphics();
});
addEventListener('keyup', event => { keys[event.code] = false; });

let touchYaw = 0;
let touchPitch = -0.28;
let looking = false;
let lastLook = null;
const lookZone = $('look-zone');
lookZone.addEventListener('pointerdown', event => {
  looking = true;
  lastLook = { x: event.clientX, y: event.clientY };
  lookZone.setPointerCapture(event.pointerId);
});
lookZone.addEventListener('pointermove', event => {
  if (!looking) return;
  touchYaw -= (event.clientX - lastLook.x) * 0.0045;
  touchPitch = clamp(touchPitch - (event.clientY - lastLook.y) * 0.004, -1.42, 1.35);
  lastLook = { x: event.clientX, y: event.clientY };
  camera.rotation.set(touchPitch, touchYaw, 0);
});
lookZone.addEventListener('pointerup', () => { looking = false; });
lookZone.addEventListener('pointercancel', () => { looking = false; });

const stick = $('stick');
const knob = $('knob');
function setJoy(event) {
  const rect = stick.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  const max = rect.width * 0.34;
  let dx = event.clientX - cx;
  let dy = event.clientY - cy;
  const length = Math.hypot(dx, dy) || 1;
  if (length > max) { dx *= max / length; dy *= max / length; }
  joy.x = dx / max; joy.y = dy / max;
  knob.style.transform = `translate(${dx}px,${dy}px)`;
}
function clearJoy() { joy.x = joy.y = 0; knob.style.transform = 'translate(0,0)'; }
stick.addEventListener('pointerdown', event => { stick.setPointerCapture(event.pointerId); setJoy(event); });
stick.addEventListener('pointermove', event => { if (stick.hasPointerCapture(event.pointerId)) setJoy(event); });
stick.addEventListener('pointerup', clearJoy);
stick.addEventListener('pointercancel', clearJoy);
$('jump-button').addEventListener('pointerdown', () => { jumpQueued = true; });
$('use-button').addEventListener('pointerdown', event => { event.preventDefault(); interact(focused); });
$('restart-button').addEventListener('pointerdown', () => resetShift());
$('gfx-button').addEventListener('pointerdown', () => toggleGraphics());

/**
 * Runtime graphics toggle. Only the settings that can change without rebuilding
 * the scene: bloom, shadow casting, and resolution.
 */
let graphicsHigh = !lowPower;
function toggleGraphics() {
  graphicsHigh = !graphicsHigh;
  renderer.shadowMap.enabled = graphicsHigh && QUALITY.shadows;
  renderer.shadowMap.needsUpdate = true;
  renderer.setPixelRatio(Math.min(devicePixelRatio, graphicsHigh ? QUALITY.pixelRatio : 1));
  post.bloom.enabled = graphicsHigh;
  post.setSize(innerWidth, innerHeight);
  $('gfx-button').textContent = graphicsHigh ? 'GFX HI' : 'GFX LO';
  toast(`Graphics: ${graphicsHigh ? 'high' : 'low'}.`, 1.6);
}

$('enter').addEventListener('click', () => {
  started = true;
  $('start').style.display = 'none';
  if (!coarse) controls.lock();
  else camera.rotation.set(touchPitch, touchYaw, 0);
  toast('You are above the pool. Authorise coolant, then use the right-hand exit.');
});
renderer.domElement.addEventListener('click', () => {
  if (started && !coarse && !controls.isLocked) controls.lock();
});
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, graphicsHigh ? QUALITY.pixelRatio : 1));
  post.setSize(innerWidth, innerHeight);
});

/* --------------------------------------------------------------- loop */

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  movePlayer(dt);
  focused = findAction();
  simulate(dt);
  dust.update(dt);
  post.update(dt, {
    alarm: sim.alarm ? 0.35 + 0.35 * Math.sin(sim.alarmPhase) : 0,
    glow: sim.pool.glow,
  });
  post.render();
  if (toast.time > 0) { toast.time -= dt; if (toast.time <= 0) $('toast').style.opacity = '0'; }
  requestAnimationFrame(frame);
}

camera.position.copy(playerCollider.end);
camera.rotation.set(-0.28, 0, 0);
room.update(0.016, sim);
booth.update(0.016, sim);
machines.update(0.016, sim);
updateHud();
$('quality-tag').textContent = QUALITY.name;
$('gfx-button').textContent = graphicsHigh ? 'GFX HI' : 'GFX LO';
// The surface library is painted synchronously above, so the entry button stays
// disabled until the plant actually exists.
$('enter').disabled = false;
$('enter').textContent = 'START THE SHIFT';
requestAnimationFrame(frame);

