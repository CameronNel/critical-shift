/**
 * One palette for the whole room.
 *
 * The reference is a Soviet RBMK control hall: cream and pale-green enamel over
 * riveted steel, brown bakelite desks, brass and chrome switchgear, and a lot of
 * sodium worklight. Against that warm, dusty envelope the pool is the only cold
 * thing in the building, which is what makes it read as dangerous.
 *
 * Every value is a CSS string so the canvas painters and the Three.js materials
 * can share it without conversion.
 */
export const P = {
  // --- structure -----------------------------------------------------------
  concrete: '#9b9284',
  concreteDeep: '#6d675d',
  concreteLight: '#b9b0a0',
  screed: '#7f7a6c',

  // --- enamel: the two panel colours the whole plant is painted in ----------
  enamelCream: '#d9cfae',
  enamelCreamDeep: '#b3a888',
  enamelGreen: '#8fa48a',
  enamelGreenDeep: '#5f7361',

  // --- metal ---------------------------------------------------------------
  steel: '#8d9895',
  steelDeep: '#5b6866',
  steelDark: '#374442',
  ironBlack: '#22292a',
  chrome: '#cfd6d4',
  brass: '#c8a24c',
  brassDeep: '#8a6c2c',
  copper: '#b0693a',

  // --- surfacing -----------------------------------------------------------
  bakelite: '#4b3628',
  bakeliteLight: '#6d5138',
  rust: '#8a4a28',
  rustLight: '#b1663a',
  grime: '#2c2820',
  rubber: '#1e2322',

  // --- hazard and signal ---------------------------------------------------
  hazard: '#e0ad3c',
  hazardDeep: '#a97b1e',
  signalRed: '#d9503c',
  signalGreen: '#69b25c',
  signalAmber: '#e8a33a',
  lampWarm: '#ffc98d',
  lampSodium: '#ffd7a8',

  // --- the pool ------------------------------------------------------------
  cherenkov: '#3fd8ff',
  cherenkovDeep: '#0c4e6b',
  cherenkovCore: '#c9f4ff',
  poolDark: '#0c2f3a',
  fuelHot: '#ffd28a',

  // --- atmosphere ----------------------------------------------------------
  fog: '#20232a',
  sky: '#5f6a6b',
  ground: '#2a2018',
};

/** Sea-of-Thieves-ish signage ink, kept off the pure-white end so it sits in the paint. */
export const INK = {
  paint: '#f0e6c8',
  paintDim: '#c3b48e',
  stencil: '#2a2620',
  warn: '#e0ad3c',
  danger: '#d9503c',
  cold: '#7fd8e4',
};
