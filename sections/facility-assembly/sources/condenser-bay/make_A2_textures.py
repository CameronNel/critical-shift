"""Original seamless numeric surface maps; no photographic assets or baked lighting."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = Path(__file__).resolve().parent / 'textures-A2'

def periodic(rng, size, radius):
    a = rng.normal(size=(size, size))
    fy = np.fft.fftfreq(size)[:, None]
    fx = np.fft.fftfreq(size)[None, :]
    a = np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * np.pi**2 * radius**2 * (fx*fx + fy*fy))).real
    return np.clip(a / max(a.std(), 1e-6), -2.5, 2.5) / 5 + .5

def main():
    ROOT.mkdir(exist_ok=True)
    rng = np.random.default_rng(28102026)
    size = 512
    maps = {
        'paint_peel': (.12, periodic(rng, size, 2.4)),
        'mineral_grain': (.24, .7 * periodic(rng, size, 3.5) + .3 * periodic(rng, size, .8)),
        'mineral_tone': (.24, periodic(np.random.default_rng(17032026), size, 55)),
        'cast_grain': (.24, periodic(rng, size, 2)),
        'metal_brush': (.24, periodic(rng, size, 1.6)),
    }
    # Subtle, directional machining streaks, under 0.24 m in physical extent.
    stripe = rng.uniform(.35, .65, (size, 1))
    maps['metal_brush'] = (.24, .45 * maps['metal_brush'][1] + .55 * stripe)
    scuff = Image.new('L', (size, size), 128)
    draw = ImageDraw.Draw(scuff)
    for _ in range(32):
        x, y = rng.integers(0, size, 2)
        length = int(rng.integers(12, 150))
        draw.line((int(x), int(y), int(x + length), int(y + length * .16)), fill=int(rng.integers(95, 120)), width=int(rng.integers(1, 3)))
    maps['traffic_scuff'] = (.24, np.asarray(scuff.filter(ImageFilter.GaussianBlur(.55))) / 255)
    receipt = {'authorship': 'Original deterministic numeric maps by the condenser A2 builder; no third-party artwork.', 'mapping': 'Box-projected in physical metres; floor traffic masks use a named metre-space UV layer.', 'lighting_baked': False, 'maps': {}}
    for name, (metres, data) in maps.items():
        rgb = np.repeat(np.uint8(np.clip(data, 0, 1) * 255)[..., None], 3, axis=2)
        Image.fromarray(rgb).save(ROOT / (name + '.png'))
        receipt['maps'][name] = {'tile_metres': metres, 'resolution': [size, size], 'meaning': 'Numeric surface variation / height, Non-Color; not albedo or lighting.'}
    (ROOT / 'maps.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('A2_TEXTURES', len(maps))

if __name__ == '__main__':
    main()
