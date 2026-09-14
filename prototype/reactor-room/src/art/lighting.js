import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { P } from './palette.js';

/**
 * The light rig.
 *
 * The room is lit like a working night shift: a warm sodium key from the ceiling
 * gantry, a very soft neutral ambient so nothing goes to solid black, and the
 * pool as the only cold source. The art direction asks for atmosphere from
 * lighting rather than from geometry, so this file is where most of the "looks
 * expensive" comes from.
 *
 * Shadow casting is rationed hard: two spots on desktop, one on mobile,
 * everything else is unshadowed fill.
 */
export function createLightRig(scene, renderer, quality) {
  // A tiny neutral environment probe. Costs one render at boot and stops every
  // metal surface in the room from reading as flat grey.
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.32;
  pmrem.dispose();

  const hemisphere = new THREE.HemisphereLight(P.sky, P.ground, 0.55);
  scene.add(hemisphere);

  // Ambient bounce off the concrete, warm, very low.
  const bounce = new THREE.DirectionalLight(P.lampWarm, 0.34);
  bounce.position.set(-6, 3, 9);
  scene.add(bounce);

  const keys = [];
  let shadowBudget = quality.shadowCasters;

  /** Register a worklight fixture. The first few get real shadows. */
  function addWorkLight(position, { colour = P.lampSodium, intensity = 26, distance = 20, target = null } = {}) {
    const wantsShadow = shadowBudget > 0 && quality.shadows;
    const light = wantsShadow
      ? new THREE.SpotLight(colour, intensity * 1.5, distance * 1.4, 1.15, 0.55, 1.6)
      : new THREE.PointLight(colour, intensity, distance, 1.8);
    light.position.set(position[0], position[1], position[2]);
    if (wantsShadow) {
      shadowBudget--;
      light.castShadow = true;
      light.shadow.mapSize.set(quality.shadowMapSize, quality.shadowMapSize);
      light.shadow.bias = -0.0022;
      light.shadow.normalBias = 0.045;
      light.shadow.camera.near = 0.6;
      light.shadow.camera.far = distance * 1.5;
      light.target.position.set(target?.[0] ?? position[0], target?.[1] ?? 0, target?.[2] ?? position[2]);
      scene.add(light.target);
    }
    scene.add(light);
    keys.push({ light, base: light.intensity, flicker: 0.02 + Math.random() * 0.05, phase: Math.random() * 9 });
    return light;
  }

  /** Localised fill with no shadow cost — used inside machines and the booth. */
  function addFill(position, colour, intensity, distance) {
    const light = new THREE.PointLight(colour, intensity, distance, 2);
    light.position.set(position[0], position[1], position[2]);
    scene.add(light);
    return light;
  }

  const alarm = new THREE.PointLight(P.signalRed, 0, 26, 1.8);
  alarm.position.set(0, 6.2, 0);
  scene.add(alarm);

  const alarmDeck = new THREE.PointLight(P.signalRed, 0, 18, 2);
  alarmDeck.position.set(0, 2.2, -6);
  scene.add(alarmDeck);

  let elapsed = 0;
  function update(dt, { alarmOn = false, power = 1, alarmPhase = 0 } = {}) {
    elapsed += dt;
    // Sodium lamps hum. A couple of percent of noise per fixture, uncorrelated,
    // is enough to stop the room looking baked.
    for (const key of keys) {
      const noise = Math.sin(elapsed * 11 + key.phase) * Math.sin(elapsed * 3.3 + key.phase * 2);
      key.light.intensity = key.base * power * (1 + noise * key.flicker);
    }
    hemisphere.intensity = 0.55 * (0.5 + power * 0.5);
    const strobe = alarmOn ? 0.5 + 0.5 * Math.sin(alarmPhase) : 0;
    alarm.intensity = strobe * 34;
    alarmDeck.intensity = strobe * 20;
  }

  return { addWorkLight, addFill, update, hemisphere };
}
