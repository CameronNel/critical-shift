import * as THREE from 'three';

/**
 * The painting toolkit every texture in this room is made with.
 *
 * Nothing here loads a file. Each map is drawn once at boot into a 2D canvas and
 * uploaded, which keeps the prototype a drop-in directory with no binary assets
 * and no build step, and lets a colour change in `palette.js` repaint the whole
 * plant.
 */

/** Deterministic RNG, so a texture looks the same on every machine and reload. */
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const lerp = (a, b, t) => a + (b - a) * t;
const smooth = t => t * t * (3 - 2 * t);

/**
 * Tiling value noise. Wrapping the lattice is what stops a repeated wall from
 * showing a seam every three metres.
 */
function valueNoise(size, cells, random) {
  const grid = new Float32Array(cells * cells);
  for (let i = 0; i < grid.length; i++) grid[i] = random();
  const out = new Float32Array(size * size);
  const step = cells / size;
  for (let y = 0; y < size; y++) {
    const gy = y * step;
    const y0 = Math.floor(gy);
    const ty = smooth(gy - y0);
    for (let x = 0; x < size; x++) {
      const gx = x * step;
      const x0 = Math.floor(gx);
      const tx = smooth(gx - x0);
      const xa = x0 % cells;
      const xb = (x0 + 1) % cells;
      const ya = (y0 % cells) * cells;
      const yb = ((y0 + 1) % cells) * cells;
      out[y * size + x] = lerp(
        lerp(grid[ya + xa], grid[ya + xb], tx),
        lerp(grid[yb + xa], grid[yb + xb], tx),
        ty,
      );
    }
  }
  return out;
}

/** Fractal sum of tiling value noise, normalised to 0..1. */
export function fbm(size, { seed = 1, cells = 4, octaves = 4, gain = 0.5, lacunarity = 2 } = {}) {
  const random = rng(seed);
  const out = new Float32Array(size * size);
  let amplitude = 1;
  let total = 0;
  let scale = cells;
  for (let o = 0; o < octaves; o++) {
    const layer = valueNoise(size, Math.max(2, Math.round(scale)), random);
    for (let i = 0; i < out.length; i++) out[i] += layer[i] * amplitude;
    total += amplitude;
    amplitude *= gain;
    scale *= lacunarity;
  }
  for (let i = 0; i < out.length; i++) out[i] /= total;
  return out;
}

export function makeCanvas(size) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  return canvas;
}

/** Painters read their own pixels back constantly; the hint roughly halves boot time. */
function context2d(canvas) {
  return canvas.getContext('2d', { willReadFrequently: true });
}

/** Wrap a painter into a repeating sRGB colour map. */
export function paint(size, painter, { repeat = [1, 1], anisotropy = 8, srgb = true } = {}) {
  const canvas = makeCanvas(size);
  const ctx = context2d(canvas);
  painter(ctx, size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(repeat[0], repeat[1]);
  texture.anisotropy = anisotropy;
  if (srgb) texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

/** Same, but tagged as linear data — for roughness, metalness and normal maps. */
export function paintData(size, painter, options = {}) {
  return paint(size, painter, { ...options, srgb: false });
}

/**
 * Turn a height field into a tangent-space normal map. Every surface family in
 * the room gets one, which is where the hand-painted relief comes from without
 * a single extra triangle.
 */
export function normalFromHeight(height, size, strength = 2.4) {
  const canvas = makeCanvas(size);
  const ctx = context2d(canvas);
  const image = ctx.createImageData(size, size);
  const at = (x, y) => height[((y + size) % size) * size + ((x + size) % size)];
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (at(x + 1, y) - at(x - 1, y)) * strength;
      const dy = (at(x, y + 1) - at(x, y - 1)) * strength;
      const length = Math.hypot(dx, dy, 1);
      const i = (y * size + x) * 4;
      image.data[i] = ((-dx / length) * 0.5 + 0.5) * 255;
      image.data[i + 1] = ((-dy / length) * 0.5 + 0.5) * 255;
      image.data[i + 2] = (1 / length) * 0.5 * 255 + 127.5;
      image.data[i + 3] = 255;
    }
  }
  ctx.putImageData(image, 0, 0);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = 4;
  return texture;
}

/** Grey map from a scalar field, used for roughness and ambient occlusion. */
export function greyFromField(field, size, low = 0, high = 1) {
  const canvas = makeCanvas(size);
  const ctx = context2d(canvas);
  const image = ctx.createImageData(size, size);
  for (let i = 0; i < field.length; i++) {
    const v = Math.round(255 * (low + (high - low) * field[i]));
    image.data[i * 4] = image.data[i * 4 + 1] = image.data[i * 4 + 2] = v;
    image.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  return texture;
}

/* ------------------------------------------------------- painting helpers */

/** Draw a scalar field as translucent ink — the base of every grime pass. */
export function fieldWash(ctx, size, field, colour, { low = 0.45, high = 1, alpha = 0.5 } = {}) {
  const image = ctx.getImageData(0, 0, size, size);
  const tint = hexToRgb(colour);
  for (let i = 0; i < field.length; i++) {
    const t = THREE.MathUtils.clamp((field[i] - low) / (high - low), 0, 1) * alpha;
    const p = i * 4;
    image.data[p] = lerp(image.data[p], tint[0], t);
    image.data[p + 1] = lerp(image.data[p + 1], tint[1], t);
    image.data[p + 2] = lerp(image.data[p + 2], tint[2], t);
  }
  ctx.putImageData(image, 0, 0);
}

export function hexToRgb(hex) {
  const value = parseInt(hex.slice(1), 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

export function rgba(hex, alpha) {
  const [r, g, b] = hexToRgb(hex);
  return `rgba(${r},${g},${b},${alpha})`;
}

/** Vertical drip streaks. Reads as decades of condensation off a pipe flange. */
export function streaks(ctx, size, colour, { count = 26, seed = 7, maxAlpha = 0.16 } = {}) {
  const random = rng(seed);
  for (let i = 0; i < count; i++) {
    const x = random() * size;
    const width = 1 + random() * 7;
    const top = random() * size * 0.7;
    const length = size * (0.15 + random() * 0.6);
    const gradient = ctx.createLinearGradient(0, top, 0, top + length);
    gradient.addColorStop(0, rgba(colour, maxAlpha * (0.4 + random() * 0.6)));
    gradient.addColorStop(1, rgba(colour, 0));
    ctx.fillStyle = gradient;
    ctx.fillRect(x, top, width, length);
  }
}

/** Chips that expose the layer underneath — the single most useful wear cue. */
export function chips(ctx, size, colour, { count = 40, seed = 3, radius = 6, alpha = 0.8 } = {}) {
  const random = rng(seed);
  ctx.fillStyle = rgba(colour, alpha);
  for (let i = 0; i < count; i++) {
    const x = random() * size;
    const y = random() * size;
    const r = 1 + random() * radius;
    ctx.beginPath();
    const points = 5 + Math.floor(random() * 4);
    for (let p = 0; p <= points; p++) {
      const angle = (p / points) * Math.PI * 2;
      const wobble = r * (0.55 + random() * 0.65);
      const px = x + Math.cos(angle) * wobble;
      const py = y + Math.sin(angle) * wobble;
      if (p === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
  }
}

/** Fine directional scratches. Kept low-contrast so they never read as noise. */
export function scratches(ctx, size, colour, { count = 60, seed = 11, alpha = 0.09 } = {}) {
  const random = rng(seed);
  ctx.lineWidth = 1;
  for (let i = 0; i < count; i++) {
    const x = random() * size;
    const y = random() * size;
    const angle = random() * Math.PI;
    const length = 8 + random() * size * 0.28;
    ctx.strokeStyle = rgba(colour, alpha * (0.3 + random() * 0.7));
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + Math.cos(angle) * length, y + Math.sin(angle) * length);
    ctx.stroke();
  }
}

/** A line of proud rivet heads, drawn with a highlight so they catch the key light. */
export function rivetLine(ctx, x0, y0, x1, y1, count, radius, light, dark) {
  for (let i = 0; i < count; i++) {
    const t = count === 1 ? 0.5 : i / (count - 1);
    const x = lerp(x0, x1, t);
    const y = lerp(y0, y1, t);
    const gradient = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.35, 0, x, y, radius);
    gradient.addColorStop(0, light);
    gradient.addColorStop(1, dark);
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

/** Height-field equivalent of `rivetLine`, so the normal map agrees with the paint. */
export function rivetHeight(field, size, x0, y0, x1, y1, count, radius, amount = 0.5) {
  for (let i = 0; i < count; i++) {
    const t = count === 1 ? 0.5 : i / (count - 1);
    const cx = lerp(x0, x1, t);
    const cy = lerp(y0, y1, t);
    for (let y = Math.floor(cy - radius); y <= cy + radius; y++) {
      for (let x = Math.floor(cx - radius); x <= cx + radius; x++) {
        const d = Math.hypot(x - cx, y - cy) / radius;
        if (d > 1) continue;
        const index = ((y + size) % size) * size + ((x + size) % size);
        field[index] = Math.min(1, field[index] + Math.cos(d * Math.PI * 0.5) * amount);
      }
    }
  }
}

/** Rectangular groove in a height field — panel seams, tread plate, tile joints. */
export function grooveHeight(field, size, x, y, w, h, amount = -0.5) {
  for (let py = y; py < y + h; py++) {
    for (let px = x; px < x + w; px++) {
      const index = ((py + size) % size) * size + ((px + size) % size);
      field[index] = THREE.MathUtils.clamp(field[index] + amount, 0, 1);
    }
  }
}
