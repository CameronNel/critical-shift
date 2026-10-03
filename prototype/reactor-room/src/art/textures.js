import * as THREE from 'three';
import { P } from './palette.js';
import {
  chips,
  fbm,
  fieldWash,
  greyFromField,
  grooveHeight,
  normalFromHeight,
  paint,
  paintData,
  rgba,
  rivetHeight,
  rivetLine,
  rng,
  scratches,
  streaks,
} from './canvas.js';

/**
 * The surface library.
 *
 * Every family is authored as one **two-metre square** of real surface and is
 * always applied through `boxUV` in `kit.js`, so a rivet is the same size on a
 * wall as it is on a pump skid. That single rule is most of what separates this
 * from the greybox it replaces.
 *
 * Each family returns a material-ready set: albedo, a normal map derived from
 * the same height field that carved the albedo, and a roughness map. Families
 * are built lazily and cached, so a scene that never shows graphite never pays
 * for it.
 */

export const TEXEL_METRES = 2;

const cache = new Map();
const families = {};

/** Fetch a surface family by name, painting it on first use. */
export function surface(name) {
  if (!cache.has(name)) {
    const builder = families[name];
    if (!builder) throw new Error(`unknown surface family: ${name}`);
    cache.set(name, builder());
  }
  return cache.get(name);
}

function pack({ size, albedo, height, roughness, normalStrength = 2.2 }) {
  return {
    map: paint(size, albedo, { repeat: [1, 1] }),
    normalMap: normalFromHeight(height, size, normalStrength),
    roughnessMap: roughness ? greyFromField(roughness, size) : null,
  };
}

/* ------------------------------------------------------------- concrete */

families.concrete = () => {
  const size = 512;
  const grain = fbm(size, { seed: 21, cells: 5, octaves: 5 });
  const patch = fbm(size, { seed: 44, cells: 2, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.45 + grain[i] * 0.35 + patch[i] * 0.2;

  // Form-board seams: poured walls remember the shuttering they were cast in.
  for (const y of [0, 170, 341]) grooveHeight(height, size, 0, y, size, 3, -0.42);
  for (const x of [86, 342]) grooveHeight(height, size, x, 0, 3, size, -0.3);
  // Tie-rod holes on the seam lines.
  rivetHeight(height, size, 43, 172, 470, 172, 6, 5, -0.55);

  return pack({
    size,
    height,
    normalStrength: 2.0,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.82 + grain[i] * 0.16;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.concrete;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, patch, P.concreteLight, { low: 0.5, high: 1, alpha: 0.5 });
      fieldWash(ctx, s, grain, P.concreteDeep, { low: 0.45, high: 0.95, alpha: 0.45 });
      // Seam lines, drawn dark then re-lit on their lower lip so they read as relief.
      for (const y of [0, 170, 341]) {
        ctx.fillStyle = rgba(P.concreteDeep, 0.6);
        ctx.fillRect(0, y, s, 3);
        ctx.fillStyle = rgba(P.concreteLight, 0.3);
        ctx.fillRect(0, y + 3, s, 2);
      }
      for (const x of [86, 342]) {
        ctx.fillStyle = rgba(P.concreteDeep, 0.4);
        ctx.fillRect(x, 0, 3, s);
      }
      rivetLine(ctx, 43, 172, 470, 172, 6, 5, rgba(P.concreteDeep, 0.85), rgba(P.grime, 0.5));
      streaks(ctx, s, P.grime, { count: 20, seed: 5, maxAlpha: 0.2 });
      streaks(ctx, s, P.rust, { count: 7, seed: 15, maxAlpha: 0.14 });
      chips(ctx, s, rgba(P.concreteDeep, 1), { count: 26, seed: 9, radius: 5, alpha: 0.35 });
      scratches(ctx, s, P.concreteLight, { count: 30, seed: 12, alpha: 0.06 });
    },
  });
};

/* ------------------------------------------ painted floor screed and paths */

families.screed = () => {
  const size = 512;
  const grain = fbm(size, { seed: 31, cells: 6, octaves: 4 });
  const wear = fbm(size, { seed: 77, cells: 2, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.2;
  for (let i = 0; i < 4; i++) grooveHeight(height, size, 0, i * 128, size, 2, -0.35);
  for (let i = 0; i < 4; i++) grooveHeight(height, size, i * 128, 0, 2, size, -0.35);

  return pack({
    size,
    height,
    normalStrength: 1.4,
    roughness: (() => {
      const field = new Float32Array(size * size);
      // Walked-on ground polishes: worn areas get shinier, not rougher.
      for (let i = 0; i < field.length; i++) field[i] = 0.9 - wear[i] * 0.42;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.screed;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, wear, P.concreteDeep, { low: 0.4, high: 1, alpha: 0.55 });
      fieldWash(ctx, s, grain, P.concrete, { low: 0.5, high: 1, alpha: 0.3 });
      ctx.strokeStyle = rgba(P.grime, 0.4);
      ctx.lineWidth = 2;
      for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * 128); ctx.lineTo(s, i * 128);
        ctx.moveTo(i * 128, 0); ctx.lineTo(i * 128, s);
        ctx.stroke();
      }
      streaks(ctx, s, P.grime, { count: 14, seed: 23, maxAlpha: 0.14 });
      chips(ctx, s, P.concreteDeep, { count: 34, seed: 19, radius: 7, alpha: 0.3 });
      scratches(ctx, s, P.concreteLight, { count: 50, seed: 8, alpha: 0.07 });
    },
  });
};

/* --------------------------------------------------------- enamel panels */

/**
 * The plant's paint. Two colours over the same riveted steel substrate: cream
 * above waist height, pale green below, which is exactly how these halls were
 * finished and gives the room a free horizontal band without any extra geometry.
 */
function enamelFamily({ seed, base, deep, chipTo }) {
  return () => {
    const size = 512;
    const grain = fbm(size, { seed, cells: 7, octaves: 4 });
    const blotch = fbm(size, { seed: seed + 90, cells: 2, octaves: 3 });
    const height = new Float32Array(size * size);
    for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.08;

    // Panel divisions with a riveted flange down each seam.
    grooveHeight(height, size, 0, 254, size, 4, -0.5);
    grooveHeight(height, size, 254, 0, 4, size, -0.5);
    rivetHeight(height, size, 16, 246, 496, 246, 12, 4, 0.55);
    rivetHeight(height, size, 246, 16, 246, 496, 12, 4, 0.55);

    return pack({
      size,
      height,
      normalStrength: 2.6,
      roughness: (() => {
        const field = new Float32Array(size * size);
        // Enamel is glossy where it survives and dull where it has chalked off.
        for (let i = 0; i < field.length; i++) field[i] = 0.32 + blotch[i] * 0.4 + grain[i] * 0.1;
        return field;
      })(),
      albedo: (ctx, s) => {
        ctx.fillStyle = base;
        ctx.fillRect(0, 0, s, s);
        fieldWash(ctx, s, blotch, deep, { low: 0.42, high: 1, alpha: 0.42 });
        ctx.fillStyle = rgba(deep, 0.75);
        ctx.fillRect(0, 254, s, 4);
        ctx.fillRect(254, 0, 4, s);
        ctx.fillStyle = rgba(base, 0.5);
        ctx.fillRect(0, 258, s, 2);
        ctx.fillRect(258, 0, 2, s);
        rivetLine(ctx, 16, 246, 496, 246, 12, 4, rgba('#ffffff', 0.4), rgba(deep, 0.9));
        rivetLine(ctx, 246, 16, 246, 496, 12, 4, rgba('#ffffff', 0.4), rgba(deep, 0.9));
        // Paint failure: a dark halo of substrate around every chip.
        chips(ctx, s, rgba(chipTo, 0.9), { count: 30, seed: seed + 5, radius: 7, alpha: 0.55 });
        chips(ctx, s, rgba(P.rust, 0.9), { count: 12, seed: seed + 6, radius: 4, alpha: 0.4 });
        streaks(ctx, s, P.grime, { count: 16, seed: seed + 7, maxAlpha: 0.17 });
        streaks(ctx, s, P.rust, { count: 6, seed: seed + 8, maxAlpha: 0.12 });
        scratches(ctx, s, deep, { count: 44, seed: seed + 9, alpha: 0.1 });
      },
    });
  };
}

families.enamelCream = enamelFamily({
  seed: 101, base: P.enamelCream, deep: P.enamelCreamDeep, chipTo: P.steelDark,
});
families.enamelGreen = enamelFamily({
  seed: 202, base: P.enamelGreen, deep: P.enamelGreenDeep, chipTo: P.steelDark,
});

/* ------------------------------------------------------- steel and plate */

families.steel = () => {
  const size = 512;
  const grain = fbm(size, { seed: 303, cells: 8, octaves: 4 });
  const bloom = fbm(size, { seed: 313, cells: 3, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.14;
  grooveHeight(height, size, 0, 256, size, 3, -0.4);
  rivetHeight(height, size, 20, 34, 492, 34, 14, 5, 0.7);
  rivetHeight(height, size, 20, 478, 492, 478, 14, 5, 0.7);
  rivetHeight(height, size, 20, 224, 492, 224, 14, 5, 0.7);
  rivetHeight(height, size, 20, 288, 492, 288, 14, 5, 0.7);

  return pack({
    size,
    height,
    normalStrength: 2.8,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.34 + bloom[i] * 0.5;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.steel;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, grain, P.steelDeep, { low: 0.4, high: 1, alpha: 0.5 });
      fieldWash(ctx, s, bloom, P.rust, { low: 0.62, high: 1, alpha: 0.55 });
      // Weld bead down the plate join.
      const weld = ctx.createLinearGradient(0, 253, 0, 262);
      weld.addColorStop(0, rgba(P.steelDark, 0.8));
      weld.addColorStop(0.5, rgba(P.steelDeep, 0.5));
      weld.addColorStop(1, rgba(P.steelDark, 0.7));
      ctx.fillStyle = weld;
      ctx.fillRect(0, 253, s, 9);
      for (const y of [34, 224, 288, 478]) {
        rivetLine(ctx, 20, y, 492, y, 14, 5, rgba(P.chrome, 0.55), rgba(P.steelDark, 0.9));
      }
      streaks(ctx, s, P.rust, { count: 18, seed: 33, maxAlpha: 0.2 });
      streaks(ctx, s, P.grime, { count: 12, seed: 34, maxAlpha: 0.15 });
      scratches(ctx, s, P.chrome, { count: 70, seed: 35, alpha: 0.1 });
    },
  });
};

families.darkSteel = () => {
  const size = 512;
  const grain = fbm(size, { seed: 404, cells: 9, octaves: 4 });
  const bloom = fbm(size, { seed: 414, cells: 3, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.18;
  rivetHeight(height, size, 24, 40, 488, 40, 10, 6, 0.75);
  rivetHeight(height, size, 24, 472, 488, 472, 10, 6, 0.75);

  return pack({
    size,
    height,
    normalStrength: 2.4,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.5 + bloom[i] * 0.42;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.steelDark;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, grain, P.ironBlack, { low: 0.4, high: 1, alpha: 0.6 });
      fieldWash(ctx, s, bloom, P.rust, { low: 0.66, high: 1, alpha: 0.5 });
      for (const y of [40, 472]) {
        rivetLine(ctx, 24, y, 488, y, 10, 6, rgba(P.steel, 0.5), rgba('#000000', 0.75));
      }
      streaks(ctx, s, P.rust, { count: 14, seed: 44, maxAlpha: 0.22 });
      scratches(ctx, s, P.steel, { count: 46, seed: 45, alpha: 0.12 });
    },
  });
};

/** Diamond tread deck. Everything the player walks on outside the concrete. */
families.tread = () => {
  const size = 512;
  const grain = fbm(size, { seed: 505, cells: 8, octaves: 3 });
  const wear = fbm(size, { seed: 515, cells: 2, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.36 + grain[i] * 0.1;

  // Two opposed rows of raised lozenges: the classic checker plate pattern.
  const cell = 64;
  const drawDiamond = (cx, cy, angle) => {
    const halfLong = 22;
    const halfShort = 6;
    for (let t = -halfLong; t <= halfLong; t++) {
      const w = Math.round(halfShort * (1 - Math.abs(t) / halfLong) ** 0.45);
      for (let n = -w; n <= w; n++) {
        const x = Math.round(cx + Math.cos(angle) * t - Math.sin(angle) * n);
        const y = Math.round(cy + Math.sin(angle) * t + Math.cos(angle) * n);
        const index = ((y + size) % size) * size + ((x + size) % size);
        height[index] = Math.min(1, height[index] + 0.62);
      }
    }
  };
  for (let gy = 0; gy < size / cell; gy++) {
    for (let gx = 0; gx < size / cell; gx++) {
      drawDiamond(gx * cell + 32, gy * cell + 32, (gy % 2 ? 1 : -1) * 0.62);
    }
  }

  return pack({
    size,
    height,
    normalStrength: 3.6,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.72 - height[i] * 0.34 + wear[i] * 0.1;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.steelDeep;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, grain, P.steelDark, { low: 0.4, high: 1, alpha: 0.55 });
      // Light the lozenges from the height field so paint and relief agree.
      const image = ctx.getImageData(0, 0, s, s);
      for (let i = 0; i < height.length; i++) {
        const proud = Math.max(0, height[i] - 0.55) * 1.9;
        const p = i * 4;
        image.data[p] = Math.min(255, image.data[p] + proud * 92);
        image.data[p + 1] = Math.min(255, image.data[p + 1] + proud * 96);
        image.data[p + 2] = Math.min(255, image.data[p + 2] + proud * 90);
      }
      ctx.putImageData(image, 0, 0);
      fieldWash(ctx, s, wear, P.rust, { low: 0.68, high: 1, alpha: 0.4 });
      streaks(ctx, s, P.grime, { count: 10, seed: 55, maxAlpha: 0.16 });
    },
  });
};

/* -------------------------------------------------------- hazard and ink */

/** Diagonal warning trim. Authored one metre tall so it bands neatly round a step. */
families.hazard = () => {
  const size = 512;
  const wear = fbm(size, { seed: 606, cells: 3, octaves: 4 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + wear[i] * 0.12;

  return pack({
    size,
    height,
    normalStrength: 1.2,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.46 + wear[i] * 0.4;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.hazard;
      ctx.fillRect(0, 0, s, s);
      ctx.fillStyle = P.ironBlack;
      ctx.save();
      ctx.translate(s / 2, s / 2);
      ctx.rotate(-Math.PI / 4);
      for (let i = -12; i < 12; i++) ctx.fillRect(i * 90, -s, 45, s * 2);
      ctx.restore();
      // Wear takes the paint off the edges of the stripes first.
      fieldWash(ctx, s, wear, P.steelDeep, { low: 0.58, high: 1, alpha: 0.72 });
      chips(ctx, s, P.steelDeep, { count: 40, seed: 61, radius: 6, alpha: 0.5 });
      streaks(ctx, s, P.grime, { count: 12, seed: 62, maxAlpha: 0.22 });
      scratches(ctx, s, P.concreteLight, { count: 60, seed: 63, alpha: 0.1 });
    },
  });
};

/* ------------------------------------------------------- desks and knobs */

families.bakelite = () => {
  const size = 512;
  const grain = fbm(size, { seed: 707, cells: 10, octaves: 4 });
  const swirl = fbm(size, { seed: 717, cells: 3, octaves: 3 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.06;

  return pack({
    size,
    height,
    normalStrength: 0.9,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.22 + swirl[i] * 0.28;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = P.bakelite;
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, swirl, P.bakeliteLight, { low: 0.4, high: 1, alpha: 0.55 });
      fieldWash(ctx, s, grain, '#2c1d13', { low: 0.5, high: 1, alpha: 0.4 });
      scratches(ctx, s, P.bakeliteLight, { count: 70, seed: 71, alpha: 0.09 });
      // Decades of elbows have polished the working edge.
      const polish = ctx.createLinearGradient(0, 0, 0, s);
      polish.addColorStop(0, rgba(P.bakeliteLight, 0.16));
      polish.addColorStop(0.6, rgba(P.bakeliteLight, 0));
      ctx.fillStyle = polish;
      ctx.fillRect(0, 0, s, s);
    },
  });
};

/* ------------------------------------------------------------- pool liner */

/** Stainless liner below the waterline. Tiled, so light in the water has something to break on. */
families.liner = () => {
  const size = 512;
  const grain = fbm(size, { seed: 808, cells: 6, octaves: 4 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.55 + grain[i] * 0.1;
  for (let i = 0; i <= 8; i++) {
    grooveHeight(height, size, 0, i * 64, size, 3, -0.45);
    grooveHeight(height, size, i * 64, 0, 3, size, -0.45);
  }

  return pack({
    size,
    height,
    normalStrength: 2.6,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.18 + grain[i] * 0.2;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = '#9fb3b4';
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, grain, '#6a8386', { low: 0.42, high: 1, alpha: 0.45 });
      ctx.strokeStyle = rgba('#3d5457', 0.8);
      ctx.lineWidth = 3;
      for (let i = 0; i <= 8; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * 64); ctx.lineTo(s, i * 64);
        ctx.moveTo(i * 64, 0); ctx.lineTo(i * 64, s);
        ctx.stroke();
      }
      scratches(ctx, s, '#d5e6e6', { count: 40, seed: 81, alpha: 0.08 });
    },
  });
};

/** Graphite blocks in the core lattice. Matte, sooty, and very dark. */
families.graphite = () => {
  const size = 256;
  const grain = fbm(size, { seed: 909, cells: 7, octaves: 4 });
  const height = new Float32Array(size * size);
  for (let i = 0; i < height.length; i++) height[i] = 0.5 + grain[i] * 0.2;

  return pack({
    size,
    height,
    normalStrength: 1.8,
    roughness: (() => {
      const field = new Float32Array(size * size);
      for (let i = 0; i < field.length; i++) field[i] = 0.74 + grain[i] * 0.2;
      return field;
    })(),
    albedo: (ctx, s) => {
      ctx.fillStyle = '#26292c';
      ctx.fillRect(0, 0, s, s);
      fieldWash(ctx, s, grain, '#0e1113', { low: 0.4, high: 1, alpha: 0.7 });
      scratches(ctx, s, '#5a6166', { count: 26, seed: 91, alpha: 0.12 });
    },
  });
};

/* ------------------------------------------------------------- overlays */

/**
 * Alpha decals. A handful of small stains reused everywhere buys more perceived
 * age than any amount of extra unique surface work.
 */
export function decal(kind, colour) {
  const key = `decal:${kind}:${colour}`;
  if (cache.has(key)) return cache.get(key);
  const size = 256;
  const random = rng(kind.length * 37 + colour.length);
  const texture = paint(size, (ctx, s) => {
    ctx.clearRect(0, 0, s, s);
    if (kind === 'stain') {
      const field = fbm(s, { seed: 1201, cells: 3, octaves: 4 });
      const image = ctx.createImageData(s, s);
      const [r, g, b] = [parseInt(colour.slice(1, 3), 16), parseInt(colour.slice(3, 5), 16), parseInt(colour.slice(5, 7), 16)];
      for (let y = 0; y < s; y++) {
        for (let x = 0; x < s; x++) {
          const i = y * s + x;
          const edge = 1 - Math.min(1, Math.hypot(x - s / 2, y - s / 2) / (s * 0.46));
          const a = THREE.MathUtils.clamp((field[i] - 0.42) * 2.6, 0, 1) * edge;
          image.data[i * 4] = r; image.data[i * 4 + 1] = g; image.data[i * 4 + 2] = b;
          image.data[i * 4 + 3] = a * 235;
        }
      }
      ctx.putImageData(image, 0, 0);
    } else if (kind === 'scorch') {
      const gradient = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      gradient.addColorStop(0, rgba(colour, 0.85));
      gradient.addColorStop(0.55, rgba(colour, 0.34));
      gradient.addColorStop(1, rgba(colour, 0));
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, s, s);
      chips(ctx, s, colour, { count: 26, seed: 5, radius: 14, alpha: 0.28 });
    } else if (kind === 'puddle') {
      ctx.fillStyle = rgba(colour, 0.55);
      ctx.beginPath();
      const points = 14;
      for (let i = 0; i <= points; i++) {
        const angle = (i / points) * Math.PI * 2;
        const r = s * (0.24 + random() * 0.15);
        const x = s / 2 + Math.cos(angle) * r;
        const y = s / 2 + Math.sin(angle) * r * 0.72;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.fill();
    }
  });
  texture.wrapS = texture.wrapT = THREE.ClampToEdgeWrapping;
  cache.set(key, texture);
  return texture;
}

/** Painted stencil lettering on a plate, used for every sign in the room. */
export function stencilTexture(lines, {
  width = 512, height = 256, bg = P.enamelCream, fg = P.ironBlack, accent = null, weathered = true,
} = {}) {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);
  if (accent) {
    ctx.fillStyle = accent;
    ctx.fillRect(0, 0, width, Math.round(height * 0.13));
    ctx.fillRect(0, height - Math.round(height * 0.13), width, Math.round(height * 0.13));
  }
  ctx.strokeStyle = rgba(fg, 0.5);
  ctx.lineWidth = 4;
  ctx.strokeRect(14, 14, width - 28, height - 28);
  const rows = Array.isArray(lines) ? lines : [lines];
  ctx.fillStyle = fg;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const rowHeight = (height - 56) / rows.length;
  rows.forEach((row, index) => {
    const fontSize = Math.min(rowHeight * 0.72, (width - 70) / Math.max(6, row.length) * 1.65);
    ctx.font = `900 ${Math.round(fontSize)}px "Arial Narrow", "Helvetica Neue", system-ui, sans-serif`;
    ctx.fillText(row, width / 2, 28 + rowHeight * (index + 0.5));
  });
  if (weathered) {
    chips(ctx, Math.max(width, height), P.steelDeep, { count: 22, seed: rows.join('').length + 3, radius: 6, alpha: 0.34 });
    scratches(ctx, Math.max(width, height), P.concreteLight, { count: 26, seed: 4, alpha: 0.08 });
    streaks(ctx, Math.max(width, height), P.grime, { count: 6, seed: 6, maxAlpha: 0.16 });
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 8;
  return texture;
}

/** Analogue dial face for the gauges scattered over the machinery. */
export function gaugeTexture({ label = '', ticks = 11, redline = 0.78 } = {}) {
  const size = 256;
  return paint(size, (ctx, s) => {
    ctx.fillStyle = '#b8b39c';
    ctx.beginPath(); ctx.arc(s / 2, s / 2, s / 2, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = P.ironBlack; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.arc(s / 2, s / 2, s / 2 - 8, 0, Math.PI * 2); ctx.stroke();
    const start = Math.PI * 0.78;
    const sweep = Math.PI * 1.44;
    ctx.strokeStyle = P.signalRed; ctx.lineWidth = 12;
    ctx.beginPath();
    ctx.arc(s / 2, s / 2, s * 0.36, start + sweep * redline, start + sweep);
    ctx.stroke();
    ctx.strokeStyle = P.ironBlack;
    for (let i = 0; i < ticks; i++) {
      const angle = start + (sweep * i) / (ticks - 1);
      const major = i % 2 === 0;
      ctx.lineWidth = major ? 6 : 3;
      const r0 = s * (major ? 0.28 : 0.31);
      const r1 = s * 0.4;
      ctx.beginPath();
      ctx.moveTo(s / 2 + Math.cos(angle) * r0, s / 2 + Math.sin(angle) * r0);
      ctx.lineTo(s / 2 + Math.cos(angle) * r1, s / 2 + Math.sin(angle) * r1);
      ctx.stroke();
    }
    ctx.fillStyle = P.ironBlack;
    ctx.font = '900 24px "Arial Narrow", system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, s / 2, s * 0.68);
    // Glass: an off-centre highlight so a row of gauges does not look printed.
    const glass = ctx.createLinearGradient(0, 0, s, s);
    glass.addColorStop(0, 'rgba(255,255,255,.18)');
    glass.addColorStop(0.45, 'rgba(255,255,255,.03)');
    glass.addColorStop(1, 'rgba(255,255,255,.09)');
    ctx.fillStyle = glass;
    ctx.beginPath(); ctx.arc(s / 2, s / 2, s / 2 - 10, 0, Math.PI * 2); ctx.fill();
  });
}

/** Slow-rolling caustics, sampled as an additive projection on walls and ceiling. */
export function causticTexture() {
  if (cache.has('caustic')) return cache.get('caustic');
  const size = 256;
  const a = fbm(size, { seed: 1301, cells: 4, octaves: 3 });
  const b = fbm(size, { seed: 1302, cells: 6, octaves: 3 });
  const texture = paintData(size, (ctx, s) => {
    const image = ctx.createImageData(s, s);
    for (let i = 0; i < a.length; i++) {
      // Ridged noise: the thin bright filaments are what read as caustics.
      const ridge = 1 - Math.abs(a[i] - b[i]) * 4.2;
      const v = THREE.MathUtils.clamp(ridge, 0, 1) ** 2.6;
      image.data[i * 4] = v * 210;
      image.data[i * 4 + 1] = v * 250;
      image.data[i * 4 + 2] = v * 255;
      image.data[i * 4 + 3] = 255;
    }
    ctx.putImageData(image, 0, 0);
  });
  cache.set('caustic', texture);
  return texture;
}

/** Soft round sprite used for dust, steam and bubbles. */
export function softDot() {
  if (cache.has('softDot')) return cache.get('softDot');
  const texture = paint(64, (ctx, s) => {
    const gradient = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
    gradient.addColorStop(0, 'rgba(255,255,255,1)');
    gradient.addColorStop(0.45, 'rgba(255,255,255,.36)');
    gradient.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, s, s);
  });
  texture.wrapS = texture.wrapT = THREE.ClampToEdgeWrapping;
  cache.set('softDot', texture);
  return texture;
}
