import * as THREE from 'three';

export interface TextStyle {
  /** Sprite height in metres. */
  height: number;
  color?: string;
  background?: string;
  border?: string;
  /** Extra weight for zone signage. */
  bold?: boolean;
}

const textureCache = new Map<string, THREE.CanvasTexture>();
const FONT_PX = 96;

function makeTexture(text: string, style: TextStyle): THREE.CanvasTexture {
  const key = [text, style.color, style.background, style.border, style.bold].join('|');
  const cached = textureCache.get(key);
  if (cached) return cached;

  const measure = document.createElement('canvas').getContext('2d');
  if (!measure) throw new Error('2D canvas context unavailable');
  const font = `${style.bold ? '700' : '500'} ${FONT_PX}px ui-sans-serif, system-ui, sans-serif`;
  measure.font = font;
  const padX = FONT_PX * 0.45;
  const padY = FONT_PX * 0.3;
  const width = Math.ceil(measure.measureText(text).width + padX * 2);
  const height = Math.ceil(FONT_PX + padY * 2);

  const canvas = document.createElement('canvas');
  canvas.width = Math.max(2, width);
  canvas.height = Math.max(2, height);
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('2D canvas context unavailable');

  if (style.background) {
    ctx.fillStyle = style.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  if (style.border) {
    ctx.strokeStyle = style.border;
    ctx.lineWidth = Math.max(3, FONT_PX * 0.06);
    ctx.strokeRect(
      ctx.lineWidth / 2,
      ctx.lineWidth / 2,
      canvas.width - ctx.lineWidth,
      canvas.height - ctx.lineWidth,
    );
  }
  ctx.font = font;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = style.color ?? '#f2f5f8';
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 + FONT_PX * 0.04);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  texture.userData.aspect = canvas.width / canvas.height;
  textureCache.set(key, texture);
  return texture;
}

/** Camera-facing label. Used for zone signs and machine name plates. */
export function createTextSprite(text: string, style: TextStyle): THREE.Sprite {
  const texture = makeTexture(text, style);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: true,
    depthWrite: false,
    sizeAttenuation: true,
  });
  const sprite = new THREE.Sprite(material);
  const aspect = (texture.userData.aspect as number) ?? 4;
  sprite.scale.set(style.height * aspect, style.height, 1);
  sprite.renderOrder = 10;
  return sprite;
}

export function disposeTextCache(): void {
  for (const texture of textureCache.values()) texture.dispose();
  textureCache.clear();
}
