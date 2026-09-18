import * as THREE from 'three';
import { P } from '../art/palette.js';
import {
  annunciatorTile, box, collide, cylinder, fuelAssembly, gauge, glow, hazardStrip,
  mat, motor, pipeRun, ring, signPlate, tank, tint, valveWheel,
} from '../art/kit.js';
import { createSteam } from '../art/particles.js';

/**
 * The ground-floor stations.
 *
 * Each one is the same three ideas — an enamel machine shell, a brass-bezelled
 * control, and a bolted sign — recombined. That is deliberate: the art direction
 * asks for reuse made legible through coherent industrial design rather than
 * hidden behind unique props.
 *
 * Positions and interaction ids are unchanged from the greybox, so the objective
 * chain and the zone readout in `main.js` still describe the room correctly.
 */

/** An illuminated machine-mounted push-button in a brass bezel. */
function pushButton(position, colour, { parent = null, radius = 0.11 } = {}) {
  const group = new THREE.Group();
  group.position.set(position[0], position[1], position[2]);
  if (parent) parent.add(group);
  const material = new THREE.MeshStandardMaterial({
    color: colour, emissive: new THREE.Color(colour), emissiveIntensity: 1.2, roughness: 0.34, metalness: 0.1,
  });
  box(radius * 4.4, radius * 3.4, 0.08, mat('darkSteel'), { parent: group, bevel: 0.02 });
  cylinder(radius * 1.5, 0.06, mat('brass'), { pos: [0, 0, 0.06], rot: [Math.PI / 2, 0, 0], radial: 16, parent: group });
  const cap = cylinder(radius, 0.07, material, { pos: [0, 0, 0.11], rot: [Math.PI / 2, 0, 0], radial: 16, parent: group });
  cap.userData.pulse = material;
  return { group, cap, material };
}

/** Enamel control cabinet: plinth, cabinet, louvres, buttons, sign. */
function cabinet({ x, z, yaw = 0, title, colour = P.enamelGreen, actions, register, place }) {
  const group = new THREE.Group();
  group.position.set(x, 0, z);
  group.rotation.y = yaw;
  const buttons = [];

  box(1.7, 0.16, 0.9, mat('darkSteel'), { pos: [0, 0.08, 0], parent: group, bevel: 0.03 });
  box(1.5, 1.75, 0.72, tint('steel', colour), { pos: [0, 1.03, 0], parent: group, bevel: 0.05 });
  box(1.56, 0.1, 0.78, mat('steel'), { pos: [0, 1.95, 0], parent: group, bevel: 0.03 });
  // Louvres and a hinged door make a plain box read as a cabinet.
  for (let i = 0; i < 5; i++) {
    box(0.9, 0.04, 0.03, mat('darkSteel'), { pos: [0, 0.42 + i * 0.11, 0.37], parent: group, bevel: 0.008 });
  }
  for (const sy of [-1, 1]) {
    cylinder(0.03, 0.14, mat('brass'), { pos: [0.66, 1.03 + sy * 0.55, 0.34], radial: 8, parent: group });
  }
  cylinder(0.035, 0.12, mat('chrome'), { pos: [-0.6, 1.03, 0.4], rot: [Math.PI / 2, 0, 0], radial: 10, parent: group });

  actions.forEach((action, index) => {
    const offset = (index - (actions.length - 1) / 2) * 0.42;
    const { cap } = pushButton([offset, 1.52, 0.38], action.colour || P.signalGreen, { parent: group });
    register(cap, { id: action.id, name: action.name, detail: action.detail, place: title });
    buttons.push(cap);
    const lamp = cylinder(0.035, 0.05, glow(action.colour || P.signalGreen, 0.5), {
      pos: [offset, 1.74, 0.38], rot: [Math.PI / 2, 0, 0], radial: 10, parent: group,
    });
    lamp.userData.action = null;
  });

  signPlate(title, { pos: [0, 2.24, 0.1], width: 1.5, height: 0.34, parent: group, bg: P.enamelCream });
  collide(1.6, 2.1, 0.9, { pos: [x, 1.05, z], rot: [0, yaw, 0] });
  place(group);
  return { group, buttons };
}

export function buildMachines({ visual, lights, register, quality }) {
  const place = group => visual.add(group);
  const steamers = [];

  /* ------------------------------------------------------- fuel rod rack */
  const rack = new THREE.Group();
  rack.position.set(-9.5, 0, -7.75);
  visual.add(rack);
  box(3.9, 0.22, 1.7, mat('darkSteel'), { pos: [0, 0.11, 0], parent: rack, bevel: 0.03 });
  hazardStrip(-9.5, -6.75, 4.2, 0.3);
  for (const x of [-1.6, 1.6]) {
    box(0.2, 2.9, 1.5, mat('steel'), { pos: [x, 1.55, 0], parent: rack, bevel: 0.035 });
  }
  box(3.4, 0.18, 1.4, mat('steel'), { pos: [0, 2.95, 0], parent: rack, bevel: 0.03 });
  box(3.4, 0.12, 0.12, tint('steel', P.hazard), { pos: [0, 0.5, -0.72], parent: rack, bevel: 0.02 });
  // Shielded storage tubes, one per assembly, with a lid that stays open on the
  // ones still holding fuel.
  const rackRods = [];
  for (let i = 0; i < 4; i++) {
    const x = -1.05 + i * 0.7;
    cylinder(0.24, 2.7, mat('darkSteel'), { pos: [x, 1.45, 0], radial: 14, parent: rack });
    ring(0.25, 0.03, mat('steel'), { pos: [x, 2.78, 0], parent: rack, radial: 14 });
    const rod = fuelAssembly({ length: 2.3, radius: 0.14, heat: 0.55 });
    rod.position.set(x, 1.5, 0);
    rack.add(rod);
    rackRods.push(rod);
  }
  const rackButton = pushButton([0, 1.15, 0.83], P.signalAmber, { parent: rack });
  register(rackButton.cap, {
    id: 'pickup_fuel', name: 'PICK UP FUEL ROD', detail: 'carry one assembly to the pool gantry', place: 'FUEL ROD RACK',
  });
  signPlate(['FUEL ROD RACK', 'FOUR ASSEMBLIES'], {
    pos: [0, 3.45, -0.1], width: 2.4, height: 0.62, parent: rack, accent: P.hazard,
  });
  collide(3.9, 2.9, 1.7, { pos: [-9.5, 1.45, -7.75] });
  lights.addFill([-9.5, 2.2, -7.0], P.fuelHot, 4, 6);

  /* ---------------------------------------------------- pool loading gantry */
  const gantry = new THREE.Group();
  gantry.position.set(0, 0, 0);
  visual.add(gantry);
  for (const [x, z] of [[-6.18, -1.35], [-6.18, 1.35], [-4.9, -1.35], [-4.9, 1.35]]) {
    box(0.26, 4.4, 0.26, mat('steel'), { pos: [x, 2.2, z], parent: gantry, bevel: 0.03 });
    box(0.42, 0.12, 0.42, mat('darkSteel'), { pos: [x, 0.06, z], parent: gantry, bevel: 0.02 });
    for (const z2 of [z]) {
      box(0.06, 0.6, 0.5, mat('steel'), { pos: [x, 0.5, z2 * 0.82], parent: gantry, bevel: 0.01 });
    }
  }
  box(1.75, 0.26, 3.1, tint('steel', P.hazard), { pos: [-5.54, 4.34, 0], parent: gantry, bevel: 0.04 });
  box(1.6, 0.16, 0.16, mat('darkSteel'), { pos: [-5.54, 4.12, -1.4], parent: gantry, bevel: 0.02 });
  box(1.6, 0.16, 0.16, mat('darkSteel'), { pos: [-5.54, 4.12, 1.4], parent: gantry, bevel: 0.02 });
  // The rail the hoist runs out over the water on.
  box(5.9, 0.22, 0.3, mat('steel'), { pos: [-2.8, 4.1, 0], parent: gantry, bevel: 0.03 });
  box(5.9, 0.1, 0.1, tint('steel', P.hazard), { pos: [-2.8, 3.96, 0], parent: gantry, bevel: 0.02 });

  const hoist = new THREE.Group();
  hoist.position.set(-2.3, 0, 0);
  gantry.add(hoist);
  box(0.62, 0.5, 0.62, tint('steel', P.hazard), { pos: [0, 3.88, 0], parent: hoist, bevel: 0.04 });
  cylinder(0.2, 0.44, mat('darkSteel'), { pos: [0, 3.9, 0], rot: [Math.PI / 2, 0, 0], radial: 14, parent: hoist });
  motor(0.17, 0.44, { pos: [0.42, 3.9, 0], colour: P.enamelGreen, parent: hoist });
  const hoistCable = cylinder(0.022, 4.0, mat('chrome'), { pos: [0, 1.85, 0], radial: 6, parent: hoist });
  const grapple = new THREE.Group();
  grapple.position.set(0, -0.2, 0);
  hoist.add(grapple);
  box(0.3, 0.24, 0.3, mat('darkSteel'), { pos: [0, 0, 0], parent: grapple, bevel: 0.03 });
  for (const [dx, dz] of [[0.14, 0], [-0.14, 0], [0, 0.14], [0, -0.14]]) {
    box(0.05, 0.3, 0.05, mat('steel'), { pos: [dx, -0.2, dz], parent: grapple, bevel: 0.01 });
  }

  const gantryButton = pushButton([-6.15, 1.25, 0], P.signalAmber, { parent: gantry });
  register(gantryButton.cap, {
    id: 'insert_fuel', name: 'INSERT FUEL ROD', detail: 'lower the carried assembly into an open channel', place: 'POOL LOADING GANTRY',
  });
  gantryButton.group.rotation.y = -Math.PI / 2;
  signPlate(['POOL LOADING GANTRY'], { pos: [-6.3, 4.9, 0], rot: [0, Math.PI / 2, 0], width: 2.4, height: 0.44, parent: gantry, accent: P.hazard });
  box(0.9, 1.1, 0.36, tint('steel', P.enamelGreen), { pos: [-6.35, 1.4, 0.9], rot: [0, -Math.PI / 2, 0], bevel: 0.04, parent: gantry });
  collide(0.5, 2.2, 0.5, { pos: [-6.18, 1.1, -1.35] });
  collide(0.5, 2.2, 0.5, { pos: [-6.18, 1.1, 1.35] });
  lights.addFill([-5.4, 3.2, 0], P.lampSodium, 7, 8);

  /* ------------------------------------------------------ primary pumps */
  const pumps = new THREE.Group();
  visual.add(pumps);
  const pumpWheels = [];
  for (const x of [7.2, 9.2]) {
    box(1.9, 0.22, 1.6, mat('darkSteel'), { pos: [x, 0.11, -7.45], parent: pumps, bevel: 0.03 });
    const volute = cylinder(0.72, 0.9, tint('steel', P.enamelGreen), {
      pos: [x, 0.95, -7.45], rot: [0, 0, Math.PI / 2], radial: 22, parent: pumps,
    });
    volute.rotation.set(0, 0, Math.PI / 2);
    ring(0.74, 0.07, mat('darkSteel'), { pos: [x, 0.95, -7.45], rot: [0, Math.PI / 2, 0], parent: pumps, radial: 24 });
    motor(0.42, 1.0, { pos: [x, 1.7, -7.45], colour: P.enamelGreenDeep, parent: pumps });
    const wheel = valveWheel(0.24, { pos: [x, 1.62, -6.7], rot: [0, 0, 0], parent: pumps });
    pumpWheels.push(wheel);
    gauge(0.14, 'BAR', { pos: [x - 0.45, 1.35, -6.72], parent: pumps });
    const steam = createSteam([x, 2.3, -7.45], quality.detail > 0.6 ? 26 : 12, { spread: 0.4, rise: 2.6 });
    pumps.add(steam.points);
    steamers.push(steam);
  }
  pipeRun([[6.2, 0.95, -7.45], [5.4, 0.95, -7.45], [5.4, -0.3, -4.9], [4.6, -0.35, -4.3]], 0.19, tint('steel', P.enamelGreen), { parent: pumps });
  pipeRun([[7.2, 1.9, -7.45], [7.2, 2.9, -7.45], [9.2, 2.9, -7.45], [9.2, 1.9, -7.45]], 0.13, mat('copper'), { parent: pumps });
  pipeRun([[10.0, 0.95, -7.45], [11.4, 0.95, -7.45], [11.4, 2.6, -8.6]], 0.19, tint('steel', P.enamelGreen), { parent: pumps });
  collide(1.9, 2.0, 1.6, { pos: [7.2, 1.0, -7.45] });
  collide(1.9, 2.0, 1.6, { pos: [9.2, 1.0, -7.45] });
  lights.addFill([8.2, 2.6, -7.2], P.lampSodium, 6, 9);

  const pumpCabinet = cabinet({
    x: 8.2, z: -5.85, yaw: Math.PI, title: 'PRIMARY COOLANT PUMPS', register, place, colour: P.enamelGreen,
    actions: [
      { id: 'start_pumps', name: 'START PUMPS', detail: 'start both primary circulation pumps', colour: P.signalGreen },
      { id: 'open_valves', name: 'OPEN VALVES', detail: 'route coolant through the pool heat exchanger', colour: P.cherenkov },
      { id: 'emergency_cooling', name: 'EMERGENCY COOL', detail: 'spend reserve power on a hard flush', colour: P.signalRed },
    ],
  });

  /* -------------------------------------------------------- switchgear */
  const switchgear = new THREE.Group();
  visual.add(switchgear);
  for (const x of [-9.8, -8.55, -7.3]) {
    box(1.15, 3.3, 0.85, tint('steel', P.enamelCream), { pos: [x, 1.65, 3.7], parent: switchgear, bevel: 0.05 });
    box(1.2, 0.12, 0.9, mat('steel'), { pos: [x, 3.36, 3.7], parent: switchgear, bevel: 0.03 });
    box(1.0, 0.7, 0.05, mat('bakelite'), { pos: [x, 2.3, 3.25], parent: switchgear, bevel: 0.015, tile: 0.6 });
    for (let i = 0; i < 3; i++) {
      cylinder(0.05, 0.07, glow([P.signalGreen, P.signalAmber, P.signalRed][i], i === 0 ? 1.8 : 0.4), {
        pos: [x - 0.24 + i * 0.24, 2.52, 3.23], rot: [Math.PI / 2, 0, 0], radial: 12, parent: switchgear,
      });
    }
    gauge(0.16, 'kV', { pos: [x, 2.06, 3.23], parent: switchgear });
    // Bus bars and ceramic insulators on the roof: unmistakably electrical.
    for (const dz of [-0.22, 0.22]) {
      cylinder(0.07, 0.34, tint('enamelCream', '#d8d2c2'), { pos: [x, 3.6, 3.7 + dz], radial: 12, parent: switchgear });
      box(0.9, 0.05, 0.09, mat('copper'), { pos: [x, 3.8, 3.7 + dz], parent: switchgear, bevel: 0.012 });
    }
  }
  box(3.9, 0.16, 1.0, mat('darkSteel'), { pos: [-8.55, 0.08, 3.7], parent: switchgear, bevel: 0.03 });
  const breakerButton = pushButton([-8.55, 1.25, 3.22], P.signalGreen, { parent: switchgear });
  register(breakerButton.cap, {
    id: 'grid_breakers', name: 'CLOSE GRID BREAKERS', detail: 'connect the turbine bus to the grid', place: 'GRID SWITCHGEAR',
  });
  signPlate(['GRID SWITCHGEAR', '6 kV — DANGER'], {
    pos: [-8.55, 4.2, 3.7], width: 2.6, height: 0.66, parent: switchgear, bg: P.hazard, fg: P.ironBlack,
  });
  collide(3.9, 3.3, 0.85, { pos: [-8.55, 1.65, 3.7] });
  lights.addFill([-8.55, 2.8, 3.0], P.signalGreen, 2.5, 5);

  /* --------------------------------------------------- backup generator */
  const generator = new THREE.Group();
  visual.add(generator);
  box(3.2, 0.24, 1.9, mat('darkSteel'), { pos: [5.65, 0.12, -8.0], parent: generator, bevel: 0.03 });
  box(2.0, 0.8, 1.5, mat('rubber'), { pos: [5.65, 0.5, -8.0], parent: generator, bevel: 0.04 });
  cylinder(0.95, 2.4, tint('steel', P.signalRed), { pos: [5.65, 1.5, -8.0], rot: [0, 0, Math.PI / 2], radial: 22, parent: generator });
  motor(0.6, 1.1, { pos: [4.2, 1.5, -8.0], colour: P.enamelGreenDeep, parent: generator });
  for (let i = 0; i < 4; i++) {
    box(0.16, 0.5, 1.4, mat('darkSteel'), { pos: [5.0 + i * 0.45, 2.5, -8.0], parent: generator, bevel: 0.02 });
  }
  pipeRun([[6.9, 1.5, -8.0], [7.6, 1.5, -8.0], [7.6, 3.4, -8.6]], 0.16, tint('steel', P.rust), { parent: generator });
  const generatorButton = pushButton([5.65, 1.3, -6.9], P.signalGreen, { parent: generator });
  register(generatorButton.cap, {
    id: 'backup_generator', name: 'START BACKUP GENERATOR', detail: 'restore emergency reserve power', place: 'BACKUP GENERATOR',
  });
  signPlate(['BACKUP GENERATOR'], { pos: [5.65, 3.15, -8.9], width: 2.4, height: 0.44, parent: generator });
  collide(3.2, 2.6, 1.9, { pos: [5.65, 1.3, -8.0] });
  const generatorSteam = createSteam([7.6, 3.6, -8.6], 18, { spread: 0.3, rise: 2.2, colour: '#8f9a96' });
  generator.add(generatorSteam.points);
  lights.addFill([5.65, 2.4, -7.4], P.signalAmber, 3, 6);

  /* -------------------------------------------------------- waste holding */
  const waste = new THREE.Group();
  visual.add(waste);
  for (const z of [3.45, 4.4]) {
    tank(0.62, 2.2, { pos: [9.1, 1.35, z], parent: waste, material: tint('steel', P.enamelCreamDeep) });
  }
  box(2.2, 0.2, 2.4, mat('darkSteel'), { pos: [9.1, 0.1, 3.92], parent: waste, bevel: 0.03 });
  hazardStrip(9.1, 3.92, 2.6, 2.8);
  pipeRun([[9.1, 2.6, 3.45], [9.1, 3.5, 3.45], [9.1, 3.5, 5.4], [11.3, 3.5, 5.9]], 0.15, tint('steel', P.hazardDeep), { parent: waste });
  const wasteButton = pushButton([7.9, 1.25, 3.92], P.signalRed, { parent: waste });
  wasteButton.group.rotation.y = -Math.PI / 2;
  register(wasteButton.cap, {
    id: 'waste_transfer', name: 'TRANSFER WASTE', detail: 'pump the holding tank to shielded storage', place: 'WASTE HOLDING',
  });
  signPlate(['WASTE HOLDING', 'RADIOACTIVE'], {
    pos: [9.1, 3.4, 2.6], width: 2.2, height: 0.62, parent: waste, bg: P.hazard, fg: P.ironBlack,
  });
  const wasteLevel = annunciatorTile('LEVEL', P.signalAmber, { pos: [8.42, 2.2, 3.92], rot: [0, -Math.PI / 2, 0], width: 0.7, height: 0.24 });
  collide(1.6, 2.6, 2.4, { pos: [9.1, 1.3, 3.92] });
  lights.addFill([9.1, 2.6, 3.9], P.signalAmber, 2.2, 5);

  /* ---------------------------------------------------- deck-side dressing */
  // Tool board, fire point, dosimeter station, and a few drums. Small, cheap,
  // and they are what make the deck feel occupied.
  box(1.8, 1.2, 0.14, tint('steel', P.enamelCream), { pos: [-11.9, 2.2, -2.0], rot: [0, Math.PI / 2, 0], bevel: 0.03 });
  for (let i = 0; i < 6; i++) {
    box(0.06, 0.5 + (i % 3) * 0.16, 0.06, mat('darkSteel'), { pos: [-11.8, 2.2, -2.7 + i * 0.28], bevel: 0.012 });
  }
  signPlate('TOOLS', { pos: [-11.78, 3.0, -2.0], rot: [0, Math.PI / 2, 0], width: 1.0, height: 0.28 });

  for (const [x, z] of [[-11.4, 6.6], [11.4, -2.4]]) {
    box(0.7, 1.2, 0.36, tint('steel', P.signalRed), { pos: [x, 0.6, z], bevel: 0.04 });
    cylinder(0.13, 0.7, tint('steel', P.signalRed), { pos: [x, 0.85, z + 0.28], radial: 14 });
    signPlate('FIRE', { pos: [x, 1.45, z], width: 0.6, height: 0.24, bg: P.signalRed, fg: '#f6ece0' });
  }
  for (const [x, z, colour] of [[-11.2, -8.6, P.hazard], [-10.4, -8.8, P.enamelGreenDeep], [11.3, 8.4, P.rust]]) {
    const drum = cylinder(0.32, 0.9, tint('steel', colour), { pos: [x, 0.45, z], radial: 18 });
    for (const y of [0.24, 0.66]) ring(0.33, 0.03, mat('darkSteel'), { pos: [x, y, z], radial: 20 });
    drum.rotation.y = Math.random() * 3;
  }

  return {
    rackRods,
    hoist,
    grapple,
    hoistCable,
    pumpWheels,
    steamers: [...steamers, generatorSteam],
    wasteLevel,
    update(dt, state) {
      const running = state.pumps ? 1 : 0;
      for (const wheel of pumpWheels) wheel.rotation.z += dt * running * 1.4;
      for (const steam of steamers) steam.update(dt, state.valves ? 0.85 : running * 0.3);
      generatorSteam.update(dt, state.reserve > 60 ? 0.5 : 0.1);
      // The grapple sits over the pool while an assembly is being lowered.
      const target = state.insertion ? -2.6 : -0.2;
      grapple.position.y = THREE.MathUtils.damp(grapple.position.y, target, 3, dt);
      hoistCable.scale.y = THREE.MathUtils.clamp(1 + (-0.2 - grapple.position.y) * 0.3, 1, 2.2);
      wasteLevel.userData.face.material.emissiveIntensity = state.waste > 60 ? 1.8 : 0.15;
      rackRods.forEach((rod, index) => {
        rod.visible = index >= state.fuelCount + (state.carryingFuel ? 1 : 0);
      });
    },
  };
}
