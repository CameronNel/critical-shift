import * as THREE from 'three';
import { P } from '../art/palette.js';
import {
  annunciatorTile, box, collide, cylinder, gauge, glow, handrail, hazardStrip,
  mat, paintedWall, ring, signPlate, tint, toggleBank, workLight,
} from '../art/kit.js';

/**
 * The elevated control booth, its landing, and the ramp down to the deck.
 *
 * Dressed as a Soviet control room of the period: cream enamel over riveted
 * steel, a bakelite desk, brass toggles, big analogue gauges, and a mimic board
 * of annunciator tiles across the back wall. The four time-critical controls sit
 * on two banks either side of a clear viewing bay, so the operator can reach
 * every control and still step forward to look into the water.
 *
 * Every collider from the greybox is reproduced exactly — the booth shell, the
 * window, the landing and the ramp — because movement was tuned against them.
 */
export function buildBooth({ visual, lights, register }) {
  const floorY = 5.18;
  const booth = new THREE.Group();
  visual.add(booth);

  /* ------------------------------------------------------------- shell */
  box(10.0, 0.34, 4.5, mat('tread'), { pos: [-0.35, 5.01, 7.28], solid: true, bevel: 0.02, cast: false });
  // Linoleum over the deck plate — control rooms were not walked on in boots.
  box(9.5, 0.03, 4.1, tint('bakelite', P.enamelGreenDeep, { roughness: 0.42 }), {
    pos: [-0.35, 5.2, 7.28], bevel: 0.008, tile: 1.2, cast: false,
  });
  box(10.0, 0.32, 4.5, mat('concreteDark'), { pos: [-0.35, 9.48, 7.28], solid: true, bevel: 0.03, cast: false });
  box(10.0, 0.4, 0.34, mat('concrete'), { pos: [-0.35, 9.42, 9.45], solid: true, bevel: 0.04 });

  paintedWall(10.0, 4.25, 0.34, { pos: [-0.35, 7.28, 9.45], solid: true });
  paintedWall(0.34, 4.25, 4.5, { pos: [-5.35, 7.28, 7.28], solid: true, uvOffset: [0.3, 0] });
  paintedWall(0.34, 4.25, 1.15, { pos: [4.65, 7.28, 5.72], solid: true, uvOffset: [0.6, 0] });
  paintedWall(0.34, 4.25, 1.05, { pos: [4.65, 7.28, 8.93], solid: true, uvOffset: [0.9, 0] });

  // Window: sill, head, mullions, glass, and an invisible pane the player cannot
  // walk through.
  //
  // The sill is deliberately low — 0.35 m above the booth floor. Anything taller
  // and the operator's sightline over the console clips the near coping and the
  // pool disappears, which defeats the entire room. The console top is now the
  // only thing between the eye and the water.
  box(10.0, 0.35, 0.28, mat('enamelGreen'), { pos: [-0.35, 5.355, 5.06], solid: true, bevel: 0.03 });
  box(10.0, 0.09, 0.4, mat('steel'), { pos: [-0.35, 5.55, 5.06], bevel: 0.02 });
  box(10.0, 0.35, 0.28, mat('steel'), { pos: [-0.35, 9.23, 5.06], solid: true, bevel: 0.03 });
  const glass = box(9.6, 3.46, 0.05, mat('glass'), { pos: [-0.35, 7.29, 5.06], bevel: 0, cast: false, receive: false });
  glass.renderOrder = 8;
  collide(9.8, 3.7, 0.18, { pos: [-0.35, 7.38, 5.06] });
  for (const x of [-4.0, -1.7, 0.65, 3.0]) {
    box(0.11, 3.6, 0.22, mat('steel'), { pos: [x, 7.32, 5.02], bevel: 0.02 });
    box(0.15, 0.15, 0.26, mat('darkSteel'), { pos: [x, 5.62, 5.02], bevel: 0.02 });
  }
  box(9.8, 0.09, 0.24, mat('steel'), { pos: [-0.35, 8.98, 5.02], bevel: 0.02 });

  /* -------------------------------------------------------------- desk */
  /**
   * The console is split into two banks with a clear **viewing bay** between
   * them.
   *
   * This is the room's one real architectural constraint: the booth floor sits
   * 5.7 m above the water and 7 m back from the pool centre, so the sightline
   * down to the lattice is about 47°. Any console within arm's reach of the
   * window blocks it. Splitting the desk means the operator works at a bank,
   * then steps into the bay to actually look at the pool — which is the beat the
   * room is built around.
   */
  const deskTilt = -0.3;
  const BANKS = [
    { centre: -3.25, width: 3.0 },
    { centre: 2.8, width: 3.5 },
  ];
  for (const { centre, width } of BANKS) {
    box(width, 0.62, 0.78, tint('darkSteel', P.enamelGreen), { pos: [centre, 5.39, 5.86], rot: [-0.16, 0, 0], bevel: 0.04 });
    box(width + 0.1, 0.1, 1.05, mat('bakelite'), { pos: [centre, 5.74, 5.76], rot: [-0.06, 0, 0], bevel: 0.025, tile: 1.4 });
    box(width + 0.1, 0.72, 0.14, tint('steel', P.enamelCreamDeep), { pos: [centre, 6.06, 5.5], rot: [deskTilt, 0, 0], bevel: 0.02 });
    box(width + 0.1, 0.06, 0.06, mat('brass'), { pos: [centre, 5.78, 5.29], bevel: 0.012 });
    box(width, 0.16, 0.7, mat('darkSteel'), { pos: [centre, 5.26, 5.9], bevel: 0.03 });
  }
  // The bay itself: nothing but a lean-on rail, pushed right up against the
  // glass. Anything further back sits in the sightline down to the water.
  cylinder(0.032, 2.7, mat('brassDark'), { pos: [-0.35, 5.6, 5.22], rot: [0, 0, Math.PI / 2], radial: 10 });
  for (const x of [-1.55, 0.85]) {
    box(0.06, 0.26, 0.06, mat('brassDark'), { pos: [x, 5.46, 5.22], bevel: 0.014 });
  }

  /**
   * One control station: illuminated push-button in a brass bezel, engraved
   * plate under it, indicator lamp above.
   */
  function control(x, { label, id, detail, colour, mushroom = false }) {
    const group = new THREE.Group();
    group.position.set(x, 5.62, 5.72);
    group.rotation.x = deskTilt;
    booth.add(group);
    box(1.85, 0.76, 0.16, mat('bakelite'), { parent: group, bevel: 0.02, tile: 0.8 });
    box(1.7, 0.62, 0.06, tint('steel', P.enamelCream), { pos: [0, 0, 0.1], parent: group, bevel: 0.015 });

    const bezel = cylinder(mushroom ? 0.19 : 0.14, 0.06, mat('brass'), {
      pos: [-0.5, 0.02, 0.14], rot: [Math.PI / 2, 0, 0], radial: 18, parent: group,
    });
    const buttonMaterial = new THREE.MeshStandardMaterial({
      color: colour, emissive: new THREE.Color(colour), emissiveIntensity: 1.1, roughness: 0.32, metalness: 0.1,
    });
    const button = cylinder(mushroom ? 0.17 : 0.12, mushroom ? 0.1 : 0.07, buttonMaterial, {
      pos: [-0.5, 0.02, 0.2], rot: [Math.PI / 2, 0, 0], radial: 18, parent: group,
    });
    register(button, { id, name: label, detail, place: 'ELEVATED CONTROL DESK' });
    button.userData.pulse = buttonMaterial;

    const plate = signPlate(label, {
      pos: [0.36, -0.02, 0.14], width: 0.94, height: 0.24, parent: group,
      bg: P.enamelCream, fg: P.ironBlack, bolts: false,
    });
    plate.scale.setScalar(1);
    // Indicator lamp above the button, so the desk reads as live at a glance.
    const lamp = cylinder(0.05, 0.05, glow(colour, 0.4), {
      pos: [-0.5, 0.26, 0.16], rot: [Math.PI / 2, 0, 0], radial: 12, parent: group,
    });
    return { button, lamp, material: buttonMaterial, bezel };
  }

  const controls = {
    cooling: control(-4.05, {
      label: 'COOLANT LOOP', id: 'authorise_cooling', colour: P.cherenkov,
      detail: 'authorise the primary coolant circuit',
    }),
    rods: control(-2.45, {
      label: 'CONTROL RODS', id: 'control_rods', colour: P.signalAmber,
      detail: 'cycle the rod bank between safe positions',
    }),
    turbine: control(1.75, {
      label: 'TURBINE LOAD', id: 'turbine_load', colour: P.signalGreen,
      detail: 'raise the turbine setpoint',
    }),
    scram: control(3.6, {
      label: 'SCRAM', id: 'scram', colour: P.signalRed, mushroom: true,
      detail: 'drop every safety rod immediately',
    }),
  };
  // A hinged guard over SCRAM. Nobody hits it by accident, and it draws the eye.
  box(0.6, 0.06, 0.5, tint('steel', P.hazard), { pos: [3.1, 6.06, 5.52], rot: [deskTilt - 0.9, 0, 0], bevel: 0.015, tile: 0.4 });

  /* -------------------------------------------------- gauges and toggles */
  const gauges = [];
  for (const [x, label] of [[-4.3, 'MW'], [-2.9, '°C'], [1.35, 'BAR'], [2.6, 'kg/s'], [4.25, '%']]) {
    const dial = gauge(0.19, label, { pos: [x, 6.42, 5.44], rot: [deskTilt * 0.6, 0, 0] });
    gauges.push(dial);
  }
  for (const x of [-3.4, 2.1]) {
    toggleBank(5, { pos: [x, 5.98, 5.62], rot: [deskTilt, 0, 0] });
  }

  // Mimic board across the rear wall: the room's status readout, in the room.
  const tiles = [];
  const tileText = [
    ['CORE TEMP', P.cherenkov], ['ROD DEPTH', P.signalAmber], ['GRID LOAD', P.cherenkov],
    ['COOLANT', P.cherenkov], ['WASTE', P.signalAmber], ['SAFETY', P.signalRed],
  ];
  box(7.4, 2.2, 0.12, mat('darkSteel'), { pos: [-0.35, 7.7, 9.2], bevel: 0.04 });
  box(7.6, 0.12, 0.2, mat('brass'), { pos: [-0.35, 8.86, 9.18], bevel: 0.02 });
  tileText.forEach(([text, colour], index) => {
    const tile = annunciatorTile(text, colour, {
      pos: [-3.0 + (index % 3) * 2.2, 8.3 - Math.floor(index / 3) * 0.62, 9.13],
      width: 1.9, height: 0.46,
    });
    tiles.push({ tile, colour });
  });
  // A wall clock. Every one of these rooms had one, and it dates the place free.
  cylinder(0.3, 0.08, mat('enamelCream'), { pos: [3.6, 8.2, 9.18], rot: [Math.PI / 2, 0, 0], radial: 22 });
  ring(0.3, 0.03, mat('brass'), { pos: [3.6, 8.2, 9.14], radial: 24 }).rotation.set(0, 0, 0);
  const clockHands = new THREE.Group();
  clockHands.position.set(3.6, 8.2, 9.11);
  booth.add(clockHands);
  box(0.03, 0.19, 0.012, mat('ink'), { pos: [0, 0.09, 0], parent: clockHands, bevel: 0.004 });
  box(0.024, 0.26, 0.012, mat('ink'), { pos: [0.09, 0.06, 0], rot: [0, 0, -1.1], parent: clockHands, bevel: 0.004 });

  signPlate(['ELEVATED REACTOR CONTROL'], {
    pos: [-0.35, 9.0, 9.16], width: 3.6, height: 0.42, bg: P.enamelGreenDeep, fg: '#eef3e6',
  });

  /* ------------------------------------------------------- booth dressing */
  // Operator's chair, log book, mug, and the ashtray that makes it a workplace.
  const chair = new THREE.Group();
  chair.position.set(-3.3, 5.2, 6.9);
  chair.rotation.y = 0.25;
  booth.add(chair);
  cylinder(0.26, 0.06, mat('darkSteel'), { pos: [0, 0.04, 0], radial: 16, parent: chair });
  cylinder(0.05, 0.42, mat('chrome'), { pos: [0, 0.26, 0], radial: 10, parent: chair });
  box(0.46, 0.1, 0.44, tint('bakelite', P.signalRed, { roughness: 0.7 }), { pos: [0, 0.5, 0], parent: chair, bevel: 0.03, tile: 0.5 });
  box(0.44, 0.5, 0.09, tint('bakelite', P.signalRed, { roughness: 0.7 }), { pos: [0, 0.78, -0.2], rot: [-0.16, 0, 0], parent: chair, bevel: 0.03, tile: 0.5 });

  box(0.42, 0.06, 0.3, tint('bakelite', P.enamelCreamDeep), { pos: [3.4, 5.86, 6.4], rot: [0, 0.4, 0], bevel: 0.01, tile: 0.4 });
  cylinder(0.07, 0.11, mat('enamelCream'), { pos: [2.6, 5.89, 6.5], radial: 14 });
  ring(0.055, 0.014, mat('enamelCream'), { pos: [2.68, 5.89, 6.5], rot: [0, Math.PI / 2, 0], radial: 12 });
  cylinder(0.13, 0.05, mat('chrome'), { pos: [-4.2, 5.86, 6.4], radial: 14 });

  // Booth ceiling light and its fill.
  workLight({ pos: [-0.35, 9.25, 7.4], colour: P.enamelCream });
  lights.addFill([-0.35, 8.6, 7.3], P.lampWarm, 7, 9);
  // Desk lamps, one per bank. Kept weak and close: an earlier single fill at
  // the window blew every dial face out to white.
  lights.addFill([-3.25, 6.5, 6.1], P.lampWarm, 1.2, 3.2);
  lights.addFill([2.8, 6.5, 6.1], P.lampWarm, 1.2, 3.2);

  /* ------------------------------------------------ landing, ramp, treads */
  box(4.7, 0.3, 2.35, mat('tread'), { pos: [6.95, 5.03, 7.05], solid: true, bevel: 0.02, cast: false });
  handrail([4.6, 8.22], [9.28, 8.22], { y: floorY });
  handrail([9.28, 5.9], [9.28, 8.22], { y: floorY });
  signPlate(['SERVICE DECK', '↓'], { pos: [4.62, 8.35, 7.25], rot: [0, -Math.PI / 2, 0], width: 1.5, height: 0.6, accent: P.hazard });

  const rampRun = 10.2;
  const rampRise = floorY;
  const rampAngle = -Math.atan(rampRise / rampRun);
  const rampLength = Math.hypot(rampRun, rampRise);
  box(2.45, 0.28, rampLength, mat('tread'), {
    pos: [8.0, rampRise / 2 - 0.05, 1.7], rot: [rampAngle, 0, 0], solid: true, bevel: 0.02, cast: false,
  });
  // Under-ramp structure. Visible from the deck, and empty space under a walkway
  // is the fastest way to look unfinished.
  for (let i = 0; i < 5; i++) {
    const t = i / 4;
    const z = -3.2 + t * 9.6;
    const y = t * rampRise;
    box(0.16, Math.max(0.2, y), 0.16, mat('darkSteel'), { pos: [6.95, y / 2, z], bevel: 0.02 });
    box(0.16, Math.max(0.2, y), 0.16, mat('darkSteel'), { pos: [9.05, y / 2, z], bevel: 0.02 });
    box(2.3, 0.12, 0.12, mat('darkSteel'), { pos: [8.0, Math.max(0.2, y) - 0.1, z], bevel: 0.02 });
  }
  // Sloped rails. `handrail` is a level-run piece, so the ramp gets its own —
  // a rail that ignored the slope would float off the top of the walkway.
  for (const x of [6.73, 9.27]) {
    const rail = new THREE.Group();
    rail.position.set(x, rampRise / 2, 1.7);
    rail.rotation.x = rampAngle;
    visual.add(rail);
    cylinder(0.032, rampLength, mat('steel'), { pos: [0, 1.06, 0], rot: [Math.PI / 2, 0, 0], radial: 8, parent: rail });
    cylinder(0.024, rampLength, mat('steel'), { pos: [0, 0.58, 0], rot: [Math.PI / 2, 0, 0], radial: 6, parent: rail });
    box(0.035, 0.13, rampLength, tint('darkSteel', P.hazardDeep), { pos: [0, 0.09, 0], parent: rail, bevel: 0.01 });
    for (let i = 0; i < 9; i++) {
      const z = -rampLength / 2 + 0.4 + (i * (rampLength - 0.8)) / 8;
      box(0.055, 1.06, 0.055, mat('steel'), { pos: [0, 0.53, z], parent: rail, bevel: 0.012 });
    }
    collide(0.14, 1.2, rampLength, { pos: [x, rampRise / 2 + 0.55, 1.7], rot: [rampAngle, 0, 0] });
  }
  // Anti-slip treads bonded to the ramp deck.
  for (let i = 0; i < 18; i++) {
    const t = i / 17;
    const z = -3.4 + t * 10.2;
    const y = t * rampRise + 0.16;
    box(2.2, 0.02, 0.07, tint('steel', P.hazard), { pos: [8.0, y, z], rot: [rampAngle, 0, 0], bevel: 0.004, tile: 0.3, cast: false });
  }
  hazardStrip(8.0, -3.8, 2.45, 0.42);

  return {
    controls,
    gauges,
    tiles,
    update(dt, state) {
      // Desk buttons breathe when their action is the next thing to do.
      const ready = {
        cooling: !state.coolingAuthorised,
        rods: state.fuelCount > 0 && state.targetRodDepth === 100,
        turbine: state.breakers && state.fuelCount > 0,
        scram: state.alarm,
      };
      const pulse = 0.6 + 0.4 * Math.sin(state.time * 4.2);
      for (const [key, control] of Object.entries(controls)) {
        control.material.emissiveIntensity = ready[key] ? 1.6 + pulse * 2.2 : 0.55;
      }
      const readings = [
        state.temp / 1020, 1 - state.rodDepth / 100, state.output / 160,
        state.coolant / 100, state.waste / 100,
      ];
      gauges.forEach((dial, index) => {
        const target = THREE.MathUtils.clamp(readings[index] ?? 0, 0, 1);
        dial.userData.needle.rotation.z = THREE.MathUtils.damp(
          dial.userData.needle.rotation.z, Math.PI * 1.24 - target * Math.PI * 1.44, 4, dt,
        );
      });
      const lit = [
        state.temp > 590, state.rodDepth < 90, state.output > 1,
        state.coolant > 40, state.waste > 60, state.alarm,
      ];
      tiles.forEach(({ tile }, index) => {
        const on = lit[index];
        const flash = index === 5 && state.alarm ? 0.5 + 0.5 * Math.sin(state.alarmPhase) : 1;
        tile.userData.face.material.emissiveIntensity = on ? 1.8 * flash : 0.12;
      });
      clockHands.rotation.z -= dt * 0.05;
    },
  };
}
