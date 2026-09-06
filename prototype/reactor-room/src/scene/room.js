import * as THREE from 'three';
import { P } from '../art/palette.js';
import {
  additive, beam, box, collide, column, cylinder, glow, handrail, hazardStrip, ladder,
  mat, paintedWall, pipeRun, ring, signPlate, tint, valveWheel, workLight,
} from '../art/kit.js';
import { decal } from '../art/textures.js';
import { createPool } from '../art/water.js';

/**
 * The containment hall: floor, walls, ceiling, and the open pool in the middle
 * of it.
 *
 * Layout is inherited unchanged from the greybox — deck plates, wall lines, pool
 * size and every guard rail sit exactly where they did, because the movement and
 * collision work in `main.js` was tuned against them. What changed is what they
 * are made of.
 */

export const ROOM = {
  wallX: 12.2,
  wallZ: 10.2,
  wallHeight: 12,
  ceilingY: 11.6,
  poolHalf: 4.55,
  waterHalf: 4.3,
  surfaceY: -0.5,
  poolFloorY: -5.0,
};

export function buildRoom({ scene, visual, lights, quality, fuelSlots }) {
  const pool = createPool({
    half: ROOM.waterHalf,
    surfaceY: ROOM.surfaceY,
    floorY: ROOM.poolFloorY,
    quality,
  });
  visual.add(pool.group);

  /* ------------------------------------------------------------ the deck */
  // Four plates around a genuine hole. There is no invisible floor over the water.
  const plates = [
    [-8.25, -0.17, -2.5, 7.4, 15.0],
    [8.25, -0.17, -2.5, 7.4, 15.0],
    [0, -0.17, -7.25, 9.1, 5.5],
    [0, -0.17, 5.0, 9.1, 1.0],
  ];
  plates.forEach(([x, y, z, w, d], index) => {
    box(w, 0.34, d, mat('tread'), {
      pos: [x, y, z], solid: true, bevel: 0.02, uvOffset: [index * 0.37, index * 0.21], cast: false,
    });
    // A concrete kerb under each plate stops the deck reading as a floating slab.
    box(w + 0.12, 0.22, d + 0.12, mat('concreteDark'), { pos: [x, y - 0.28, z], bevel: 0.03, cast: false });
  });

  // Painted walkway edges and a wear path from the ramp foot to the gantry.
  hazardStrip(-4.95, -7.6, 0.28, 4.6);
  hazardStrip(4.95, -7.6, 0.28, 4.6);
  hazardStrip(0, -9.6, 18, 0.28);
  for (const [x, z, size, rot] of [[6.4, -1.6, 3.4, 0.4], [-6.6, -0.4, 3.0, -0.7], [0, -7.6, 3.6, 0.2]]) {
    const wear = new THREE.Mesh(
      new THREE.PlaneGeometry(size, size),
      new THREE.MeshBasicMaterial({ map: decal('stain', P.grime), transparent: true, opacity: 0.3, depthWrite: false, toneMapped: false }),
    );
    wear.rotation.set(-Math.PI / 2, 0, rot);
    wear.position.set(x, 0.012, z);
    wear.renderOrder = 1;
    visual.add(wear);
  }

  /* ----------------------------------------------------------- the shell */
  const h = ROOM.wallHeight;
  paintedWall(24.4, h, 0.38, { pos: [0, h / 2 - 0.2, -ROOM.wallZ], solid: true });
  paintedWall(24.4, h, 0.38, { pos: [0, h / 2 - 0.2, ROOM.wallZ], solid: true });
  paintedWall(0.38, h, 20.4, { pos: [-ROOM.wallX, h / 2 - 0.2, 0], solid: true, uvOffset: [0.4, 0] });
  paintedWall(0.38, h, 20.4, { pos: [ROOM.wallX, h / 2 - 0.2, 0], solid: true, uvOffset: [0.7, 0] });

  // Pilasters. Cheap vertical rhythm, and they break up 24 m of flat wall.
  for (const x of [-10.4, -5.2, 0, 5.2, 10.4]) {
    for (const z of [-9.9, 9.9]) {
      box(0.5, h - 0.6, 0.34, mat('concrete'), { pos: [x, 5.3, z], bevel: 0.05, uvOffset: [x * 0.1, 0] });
      box(0.66, 0.16, 0.44, mat('steel'), { pos: [x, 10.9, z], bevel: 0.02 });
    }
  }
  for (const z of [-8.4, -2.8, 2.8, 8.4]) {
    for (const x of [-11.9, 11.9]) {
      box(0.34, h - 0.6, 0.5, mat('concrete'), { pos: [x, 5.3, z], bevel: 0.05, uvOffset: [z * 0.1, 0] });
      box(0.44, 0.16, 0.66, mat('steel'), { pos: [x, 10.9, z], bevel: 0.02 });
    }
  }

  /* ---------------------------------------------------------- the ceiling */
  box(25, 0.5, 21, mat('concreteDark'), { pos: [0, ROOM.ceilingY + 0.25, 0], bevel: 0.05, cast: false });
  // Coffers: a grid of shallow recesses so the ceiling catches the uplight.
  for (let gx = -2; gx <= 2; gx++) {
    for (let gz = -2; gz <= 2; gz++) {
      box(4.2, 0.18, 3.5, mat('concrete'), { pos: [gx * 4.7, ROOM.ceilingY - 0.1, gz * 4.0], bevel: 0.06, cast: false });
    }
  }
  // Roof trusses and the crane rails they carry.
  for (const z of [-7.6, -3.4, 3.4, 7.6]) {
    beam(24, { pos: [0, 10.75, z], depth: 0.52 });
  }
  for (const x of [-9.2, 9.2]) {
    box(0.28, 0.3, 20, tint('darkSteel', P.hazardDeep), { pos: [x, 10.2, 0], bevel: 0.03 });
  }
  visual.add(pool.ceilingCaustics(ROOM.ceilingY - 0.24, 22));

  /* ------------------------------------------------------ overhead crane */
  const crane = new THREE.Group();
  visual.add(crane);
  beam(19.6, { pos: [0, 9.85, 0], depth: 0.72, parent: crane });
  beam(19.6, { pos: [0, 9.85, 1.1], depth: 0.72, parent: crane });
  for (const z of [0, 1.1]) {
    for (const x of [-9.2, 9.2]) {
      box(0.5, 0.7, 0.9, mat('darkSteel'), { pos: [x, 10.1, z], bevel: 0.03, parent: crane });
    }
  }
  const trolley = new THREE.Group();
  crane.add(trolley);
  box(1.5, 0.9, 1.9, tint('steel', P.hazard), { pos: [0, 9.4, 0.55], bevel: 0.06, parent: trolley });
  box(1.1, 0.5, 1.1, mat('darkSteel'), { pos: [0, 8.85, 0.55], bevel: 0.04, parent: trolley });
  cylinder(0.05, 3.6, mat('chrome'), { pos: [0, 7.0, 0.55], radial: 8, parent: trolley });
  const hook = new THREE.Group();
  hook.position.set(0, 5.2, 0.55);
  trolley.add(hook);
  box(0.34, 0.3, 0.34, mat('darkSteel'), { pos: [0, 0, 0], bevel: 0.04, parent: hook });
  ring(0.2, 0.05, mat('steel'), { pos: [0, -0.32, 0], parent: hook, radial: 16 }).rotation.set(0, 0, 0);
  crane.userData.trolley = trolley;

  /* ---------------------------------------------------------- the pool */
  const half = ROOM.poolHalf;
  const depth = -ROOM.poolFloorY;
  // Concrete curb, then the stainless liner inside it.
  for (let i = 0; i < 4; i++) {
    const angle = (i * Math.PI) / 2;
    const sx = Math.sin(angle);
    const sz = Math.cos(angle);
    box(sz ? half * 2 + 0.6 : 0.6, depth, sz ? 0.6 : half * 2 + 0.6, mat('concrete'), {
      pos: [sx * (half + 0.3), -depth / 2, sz * (half + 0.3)], bevel: 0.05, uvOffset: [i * 0.3, 0],
    });
    box(sz ? half * 2 : 0.12, depth - 0.12, sz ? 0.12 : half * 2, mat('liner'), {
      pos: [sx * (half - 0.06), -depth / 2 + 0.06, sz * (half - 0.06)], bevel: 0.02,
    });
    // Coping stone: a bevelled lip that catches the pool light and reads all the
    // way from the booth.
    box(sz ? half * 2 + 0.9 : 0.62, 0.16, sz ? 0.62 : half * 2 + 0.9, tint('steel', P.steelDeep), {
      pos: [sx * (half + 0.3), 0.08, sz * (half + 0.3)], bevel: 0.045,
    });
  }
  box(half * 2, 0.3, half * 2, mat('liner'), { pos: [0, ROOM.poolFloorY - 0.15, 0], bevel: 0.02, cast: false });

  // Hazard trim outlining the opening — the first thing that reads as "hole".
  hazardStrip(0, -half - 0.72, half * 2 + 2.0, 0.34);
  hazardStrip(0, half + 0.72, half * 2 + 2.0, 0.34);
  hazardStrip(-half - 0.72, 0, 0.34, half * 2 + 2.0);
  hazardStrip(half + 0.72, 0, 0.34, half * 2 + 2.0);

  /* ------------------------------------------------------ the core lattice */
  const core = new THREE.Group();
  core.position.y = ROOM.poolFloorY;
  visual.add(core);
  cylinder(3.35, 0.9, mat('graphite'), { pos: [0, 0.45, 0], radial: 32, parent: core });
  cylinder(3.5, 0.24, mat('darkSteel'), { pos: [0, 0.12, 0], radial: 32, parent: core });
  const latticeTop = cylinder(3.3, 0.18, mat('liner'), { pos: [0, 0.99, 0], radial: 32, parent: core });
  latticeTop.receiveShadow = false;
  // Channel caps in concentric rings — the shape everyone recognises as a reactor face.
  for (const [radius, count] of [[0.95, 8], [1.75, 14], [2.55, 20]]) {
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2 + radius;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      cylinder(0.19, 0.14, mat('steel'), { pos: [x, 1.13, z], radial: 10, parent: core });
      ring(0.19, 0.028, mat('chrome'), { pos: [x, 1.2, z], parent: core, radial: 10 });
    }
  }
  // The four live channels, collared in hazard yellow so a carried rod has an
  // obvious destination.
  fuelSlots.forEach(([x, z]) => {
    cylinder(0.3, 0.3, mat('darkSteel'), { pos: [x, 1.12, z], radial: 14, parent: core });
    ring(0.31, 0.045, tint('steel', P.hazard), { pos: [x, 1.28, z], parent: core, radial: 16 });
    const halo = new THREE.Mesh(new THREE.CircleGeometry(0.42, 18), additive(P.cherenkovCore, 0.22));
    halo.rotation.x = -Math.PI / 2;
    halo.position.set(x, 1.3, z);
    halo.renderOrder = 5;
    core.add(halo);
    pool.addShaft(x, z, depth - 1.4);
  });

  /* --------------------------------------------- control-rod drive frame */
  // An *open* square frame over the pool, not a walkway. An earlier solid
  // bridge here read well from the deck but hid the water from the control
  // booth, which is the one view the room exists to serve.
  const bridge = new THREE.Group();
  visual.add(bridge);
  const frameY = 2.55;
  for (const z of [-1.35, 1.35]) {
    beam(half * 2 + 1.6, { pos: [0, frameY, z], depth: 0.3, parent: bridge });
  }
  for (const x of [-1.35, 1.35]) {
    beam(2.7, { pos: [x, frameY, 0], depth: 0.3, rot: [0, Math.PI / 2, 0], parent: bridge });
  }
  for (const x of [-half - 0.5, half + 0.5]) {
    for (const z of [-1.35, 1.35]) {
      column(frameY, { pos: [x, 0, z], radius: 0.1, parent: bridge });
    }
  }

  const rodDrives = [];
  const rodPositions = [[-0.72, 0], [0.72, 0], [0, -0.72], [0, 0.72]];
  rodPositions.forEach(([x, z], index) => {
    // Drive head hanging under the frame, directly over its rod.
    const head = new THREE.Group();
    head.position.set(x, frameY + 0.05, z);
    bridge.add(head);
    box(0.42, 0.6, 0.42, tint('darkSteel', P.enamelGreen), { pos: [0, 0.3, 0], bevel: 0.04, parent: head });
    cylinder(0.13, 0.3, mat('chrome'), { pos: [0, 0.72, 0], radial: 12, parent: head });
    valveWheel(0.19, { pos: [0, 0.95, 0], rot: [Math.PI / 2, 0, 0], parent: head, material: mat('brassDark') });
    const lamp = glow(P.signalRed, 2.4);
    cylinder(0.05, 0.07, lamp, { pos: [0.16, 0.58, 0.16], radial: 8, parent: head });

    // The rod itself, which slides.
    const rod = new THREE.Group();
    rod.position.set(x, -2.65, z);
    visual.add(rod);
    cylinder(0.075, 4.6, mat('chrome'), { pos: [0, 0.9, 0], radial: 10, parent: rod });
    cylinder(0.15, 3.4, mat('graphite'), { pos: [0, -0.9, 0], radial: 12, parent: rod });
    for (let i = 0; i < 5; i++) {
      ring(0.16, 0.022, mat('darkSteel'), { pos: [0, -2.4 + i * 0.72, 0], parent: rod, radial: 12 });
    }
    cylinder(0.2, 0.24, tint('ink', P.signalRed), { pos: [0, 2.24, 0], radial: 12, parent: rod });
    rodDrives.push({ rod, head, lamp, index });
  });

  /* -------------------------------------------------------- pool railings */
  handrail([-4.4, -4.92], [4.4, -4.92]);
  handrail([-4.4, 4.92], [4.4, 4.92]);
  handrail([4.92, -4.4], [4.92, 4.4]);
  // West side leaves a controlled opening for the loading gantry; a chain and a
  // waist-high barrier keep the player out of it.
  handrail([-4.92, -4.35], [-4.92, -1.25]);
  handrail([-4.92, 1.25], [-4.92, 4.35]);
  collide(0.28, 1.15, 2.6, { pos: [-4.92, 0.56, 0] });
  for (const z of [-0.95, 0.95]) {
    box(0.09, 1.0, 0.09, mat('steel'), { pos: [-4.92, 0.5, z], bevel: 0.02 });
  }
  for (let i = 0; i < 7; i++) {
    ring(0.055, 0.016, mat('darkSteel'), {
      pos: [-4.92, 0.86 - Math.sin((i / 6) * Math.PI) * 0.16, -0.8 + i * 0.266],
      rot: [0, 0, i % 2 ? Math.PI / 2 : 0], radial: 8,
    });
  }

  /* --------------------------------------------------- services and dressing */
  // Coolant headers running down the north wall and diving into the pool.
  pipeRun([[-11.4, 3.4, -9.5], [-6.5, 3.4, -9.5], [-5.4, 3.4, -8.2], [-5.4, 1.4, -6.0], [-5.0, 0.2, -5.2]], 0.19, tint('steel', P.enamelGreen));
  pipeRun([[11.4, 3.9, -9.5], [6.0, 3.9, -9.5], [5.2, 3.9, -8.0], [5.2, 1.2, -6.2], [4.9, 0.2, -5.3]], 0.19, tint('steel', P.enamelGreen));
  pipeRun([[-11.6, 6.2, 8.6], [-6, 6.4, 9.2], [4, 6.4, 9.2], [11.6, 6.2, 8.6]], 0.15, tint('steel', P.copper));
  pipeRun([[-11.9, 8.4, -6], [-11.9, 8.4, 6]], 0.12, mat('steel'), { flanges: false });
  pipeRun([[11.9, 8.4, -6], [11.9, 8.4, 6]], 0.12, mat('steel'), { flanges: false });

  // Cable trays and conduit — the industrial equivalent of skirting board.
  for (const [x, z, len, yaw] of [[-11.85, 0, 19.6, Math.PI / 2], [11.85, 0, 19.6, Math.PI / 2], [0, -9.85, 23.6, 0], [0, 9.85, 23.6, 0]]) {
    const tray = new THREE.Group();
    tray.position.set(x, 7.4, z);
    tray.rotation.y = yaw;
    visual.add(tray);
    box(len, 0.1, 0.34, mat('darkSteel'), { parent: tray, bevel: 0.02, cast: false });
    box(len, 0.22, 0.06, mat('darkSteel'), { pos: [0, 0.12, 0.16], parent: tray, bevel: 0.01, cast: false });
    for (let i = 0; i < 3; i++) {
      cylinder(0.035, len * 0.98, tint('ink', P.bakelite), {
        pos: [0, 0.04 + i * 0.06, -0.1], rot: [0, 0, Math.PI / 2], radial: 6, parent: tray, cast: false,
      });
    }
  }

  // Strip light bonded to the booth soffit, washing the south deck and the near
  // pool coping that the operator looks straight down onto.
  box(9.4, 0.16, 0.34, mat('darkSteel'), { pos: [0, 4.68, 4.86], bevel: 0.02 });
  box(9.0, 0.07, 0.2, glow(P.lampSodium, 0.9), { pos: [0, 4.58, 4.86], bevel: 0.015 });
  lights.addFill([0, 4.4, 4.4], P.lampSodium, 7, 11);
  lights.addFill([0, 1.4, 6.6], P.lampWarm, 3, 7);

  ladder(7.2, { pos: [-11.7, 0, -6.4], rot: [0, Math.PI / 2, 0] });
  ladder(7.2, { pos: [11.7, 0, 6.4], rot: [0, -Math.PI / 2, 0] });

  /* --------------------------------------------------------------- signage */
  signPlate(['REACTOR HALL', 'NO UNESCORTED ENTRY'], {
    pos: [0, 4.4, -9.95], width: 3.4, height: 1.0, accent: P.hazard,
  });
  signPlate(['RADIATION', 'CONTROLLED AREA'], {
    pos: [-8.4, 3.2, -9.95], width: 2.2, height: 0.8, bg: P.hazard, fg: P.ironBlack,
  });
  signPlate('DOSIMETRY', { pos: [8.6, 3.0, -9.95], width: 1.8, height: 0.5 });
  signPlate('POOL LEVEL −0.5 m', { pos: [-11.95, 2.4, -3.2], rot: [0, Math.PI / 2, 0], width: 2.0, height: 0.44 });
  signPlate(['EMERGENCY', 'MUSTER →'], {
    pos: [11.95, 2.6, 5.4], rot: [0, -Math.PI / 2, 0], width: 2.0, height: 0.7, bg: P.enamelGreenDeep, fg: '#eef3e6',
  });

  /* ----------------------------------------------------------- worklights */
  // Two rows down the hall plus a pair over the pool. The pool pair are the ones
  // that get real shadows, because they are what the player is looking at.
  const fixtures = [];
  for (const z of [-7.4, -3.2, 3.2, 7.4]) {
    for (const x of [-7.6, 7.6]) {
      fixtures.push([x, 9.6, z, false]);
    }
  }
  fixtures.push([-3.2, 8.6, 0, true], [3.2, 8.6, 0, true]);
  // Under the booth. Without these the whole south end of the hall reads as a
  // black band from the one viewpoint the player spends most of their time at.
  fixtures.push([-6.6, 4.4, 8.4, false], [6.2, 4.4, 8.4, false]);
  for (const [x, y, z, hero] of fixtures) {
    const fixture = workLight({ pos: [x, y, z] });
    cylinder(0.03, 0.9, mat('steel'), { pos: [x, y + 0.5, z], radial: 6 });
    lights.addWorkLight([x, y - 0.25, z], {
      intensity: hero ? 34 : 20,
      distance: hero ? 26 : 18,
      target: [x * 0.4, 0, z * 0.6],
    });
    fixture.userData.hero = hero;
  }

  // Emergency luminaires: dead until the alarm, then the only thing you see.
  // One shared material, so the whole hall strobes on the same beat.
  const emergencyMaterial = new THREE.MeshStandardMaterial({
    color: P.signalRed, emissive: new THREE.Color(P.signalRed), emissiveIntensity: 0.05, roughness: 0.4,
  });
  for (const [x, z, yaw] of [[-11.9, -4, Math.PI / 2], [11.9, -4, -Math.PI / 2], [-11.9, 5, Math.PI / 2], [11.9, 5, -Math.PI / 2], [0, -9.9, 0]]) {
    const housing = new THREE.Group();
    housing.position.set(x, 5.6, z);
    housing.rotation.y = yaw;
    visual.add(housing);
    box(0.5, 0.24, 0.2, mat('darkSteel'), { parent: housing, bevel: 0.03 });
    box(0.4, 0.16, 0.06, emergencyMaterial, { pos: [0, 0, -0.12], parent: housing, bevel: 0.02 });
  }

  return {
    pool,
    rodDrives,
    crane,
    update(dt, state) {
      pool.update(dt, state.pool);
      // Rod travel: 100% inserted parks the absorber in the lattice, 0% lifts it
      // clear into the drive bridge.
      const y = -2.65 + ((100 - state.rodDepth) / 100) * 5.2;
      for (const drive of rodDrives) {
        drive.rod.position.y = y;
        drive.head.rotation.y += dt * (state.rodMoving ? 2.4 : 0);
      }
      crane.userData.trolley.position.x = Math.sin(state.time * 0.06) * 3.4;
      emergencyMaterial.emissiveIntensity = state.alarm ? 2.6 + Math.sin(state.alarmPhase) * 1.6 : 0.05;
    },
  };
}
