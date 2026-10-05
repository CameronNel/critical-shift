"""Generated tileable PBR texture sets (numpy + Pillow, build time only): plaster5, wood5, metal5, cork5, plus wear decal atlas.
Each set writes <name>_color.jpg, _rough.jpg, _normal.jpg and _height.jpg into textures/ using the same naming as the CC0 sets.
Noise is made by FFT filtering white noise, so every map tiles seamlessly. Deterministic (fixed seeds)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
from PIL import Image

TEXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures')
N = 1024

def noise(seed, beta=2.0, fx=1.0, fy=1.0, n=N):
    """Tileable 1/f^beta noise in [0,1]. fx/fy > 1 stretch the spectrum (fx small = features long in x)."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((n, n))
    F = np.fft.fft2(w)
    kx = np.fft.fftfreq(n)[None, :] * n; ky = np.fft.fftfreq(n)[:, None] * n
    r = np.sqrt((kx * fx) ** 2 + (ky * fy) ** 2); r[0, 0] = 1.0
    F = F / r ** (beta / 2.0); F[0, 0] = 0
    a = np.real(np.fft.ifft2(F)); a -= a.min(); a /= a.max()
    return a

def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def normal_from_height(h, strength=2.0):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength * N / 64.0
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength * N / 64.0
    nz = np.ones_like(h); l = np.sqrt(gx * gx + gy * gy + nz * nz)
    return np.stack([(-gx / l) * 0.5 + 0.5, (gy / l) * 0.5 + 0.5, nz / l * 0.5 + 0.5], -1)

def save(name, color, rough, height, nstrength=2.0):
    def u8(a): return (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
    os.makedirs(TEXDIR, exist_ok=True)
    Image.fromarray(u8(color)).save(os.path.join(TEXDIR, name + '_color.jpg'), quality=92)
    Image.fromarray(u8(np.repeat(rough[..., None], 3, -1))).save(os.path.join(TEXDIR, name + '_rough.jpg'), quality=92)
    Image.fromarray(u8(np.repeat(height[..., None], 3, -1))).save(os.path.join(TEXDIR, name + '_height.jpg'), quality=92)
    Image.fromarray(u8(normal_from_height(height, nstrength))).save(os.path.join(TEXDIR, name + '_normal.jpg'), quality=92)

def lerp(a, b, t): return a + (b - a) * t[..., None]

def cracks(seed, count, length, n=N):
    """Hairline cracks as a [0,1] mask (1 = crack). Random walks, tile-wrapped."""
    rng = np.random.default_rng(seed); m = np.zeros((n, n))
    for _ in range(count):
        x, y = rng.integers(0, n, 2); a = rng.uniform(0, 6.28)
        for _ in range(length):
            a += rng.normal(0, 0.35); x = (x + np.cos(a) * 1.4) % n; y = (y + np.sin(a) * 1.4) % n
            m[int(y), int(x)] = 1.0
    from PIL import ImageFilter
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    a = np.asarray(im).astype(float) / 255.0; return np.clip(a * 3.0, 0, 1)

def make_plaster():
    """Painted lime plaster: orange-peel stipple, trowel swirls, roller streaks, a few hairline cracks and pits. Neutral grey (tinted in the material)."""
    peel = noise(11, 1.2); swirl = noise(12, 3.2); roll = noise(13, 2.0, fx=0.25, fy=2.2); big = noise(14, 3.5)
    pits = (noise(15, 0.4) > 0.985).astype(float)
    ck = cracks(16, 4, 180) * 0.35
    h = 0.45 * peel + 0.35 * swirl + 0.10 * roll - 0.5 * ck - 0.3 * pits
    h = (h - h.min()) / (h.max() - h.min())
    lum = 0.55 + 0.10 * (big - 0.5) + 0.05 * (swirl - 0.5) + 0.04 * (roll - 0.5) - 0.12 * ck - 0.05 * pits
    col = np.stack([lum, lum * 0.985, lum * 0.97], -1)
    rough = np.clip(0.80 + 0.12 * (peel - 0.5) - 0.06 * smooth(roll, 0.6, 0.9), 0, 1)
    save('plaster5', col, rough, h, 1.6)

def make_wood():
    """Sealed oak/walnut veneer: long cathedral grain, pores, ring bands. Real colour (tint 1)."""
    warp = noise(21, 3.2, fx=6.0, fy=1.6)
    y = np.arange(N)[:, None] / N * np.ones((1, N))
    v = y + 0.16 * (warp - 0.5)
    rings = 0.6 * (np.sin(2 * np.pi * (v * 7.3)) * 0.5 + 0.5) + 0.4 * (np.sin(2 * np.pi * (v * 19.1 + 0.15)) * 0.5 + 0.5)
    band = smooth(rings, 0.15, 0.95)
    fibre = noise(23, 0.8, fx=14.0, fy=1.0); pores = noise(24, 0.3, fx=10.0, fy=1.0)
    light = np.array([0.62, 0.44, 0.26]); dark = np.array([0.46, 0.28, 0.15])
    t = np.clip(0.55 * band + 0.25 * (warp - 0.5) + 0.2, 0, 1)
    col = lerp(light, dark, t) * (0.93 + 0.14 * fibre[..., None]) * (0.97 + 0.06 * pores[..., None])
    scuff = noise(25, 1.4, fx=0.3, fy=0.3) > 0.82
    col = col * (1 - 0.12 * scuff[..., None])
    h = 0.5 * fibre + 0.35 * pores + 0.25 * band
    h = (h - h.min()) / (h.max() - h.min())
    rough = np.clip(0.50 + 0.15 * (pores - 0.5) + 0.12 * scuff, 0, 1)
    save('wood5', col, rough, h, 0.8)

def make_metal():
    """Brushed painted steel: fine horizontal brushing, hairline scratches, a few dull patches. Neutral grey (tinted in the material)."""
    brush = noise(31, 0.5, fx=14.0, fy=1.0); brush2 = noise(32, 1.2, fx=8.0, fy=1.0); patch = noise(33, 3.2)
    sc = noise(34, 0.3, fx=20.0, fy=1.0) > 0.992
    from PIL import ImageFilter
    scr = np.asarray(Image.fromarray((sc * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(float) / 255.0 * 3
    scr = np.clip(scr, 0, 1)
    lum = 0.5 + 0.07 * (brush - 0.5) + 0.05 * (brush2 - 0.5) + 0.08 * (patch - 0.5) + 0.12 * scr
    col = np.stack([lum, lum, lum * 1.01], -1)
    h = 0.6 * brush + 0.4 * brush2 - 0.5 * scr; h = (h - h.min()) / (h.max() - h.min())
    rough = np.clip(0.42 + 0.14 * (brush2 - 0.5) + 0.25 * smooth(patch, 0.55, 0.8) + 0.15 * scr, 0, 1)
    save('metal5', col, rough, h, 0.5)

def make_cork():
    sp = noise(41, 0.6); sp2 = noise(42, 1.4); dk = (noise(43, 0.2) > 0.9).astype(float)
    base = np.array([0.55, 0.38, 0.22])
    col = lerp(base * 0.7, base * 1.25, np.clip(0.7 * sp + 0.3 * sp2, 0, 1) ** 1.5) * (1 - 0.45 * dk[..., None])
    h = 0.6 * sp + 0.4 * sp2 - 0.3 * dk; h = (h - h.min()) / (h.max() - h.min())
    save('cork5', col, np.full((N, N), 0.9), h, 1.6)

def make_wear_atlas():
    """Wear decal atlas, RGBA 2048x1024 (alpha = dirt amount, colour near-black brown). 8 cells of 512:
    0 scuff streaks, 1 floor traffic path (long), 2 water streaks, 3 corner grime, 4 handprint smudges, 5 skid marks, 6 stain blotch, 7 edge dust."""
    from PIL import ImageDraw, ImageFilter
    W, Hh = 2048, 1024; cell = 512
    rng = np.random.default_rng(51); A = np.zeros((Hh, W))
    def cellarr(ix, iy): return A[iy * cell:(iy + 1) * cell, ix * cell:(ix + 1) * cell]
    def blob_noise(seed, beta, n=cell):
        return noise(seed, beta, n=n)
    # 0 scuff streaks (short diagonal strokes)
    im = Image.new('L', (cell, cell), 0); d = ImageDraw.Draw(im)
    for _ in range(60):
        x, y = rng.integers(20, cell - 20, 2); l = rng.integers(25, 90); a = rng.uniform(-0.6, 0.2) + 3.14 * (rng.random() < 0.5)
        d.line((x, y, x + np.cos(a) * l, y + np.sin(a) * l), fill=int(rng.integers(40, 140)), width=int(rng.integers(1, 4)))
    im = im.filter(ImageFilter.GaussianBlur(1.3)); cellarr(0, 0)[:] = np.asarray(im) / 255.0
    # 1 traffic path: soft long band, fading at the ends, mottled
    n1 = blob_noise(52, 2.5); yy = np.abs(np.linspace(-1, 1, cell))[:, None]; xx = np.abs(np.linspace(-1, 1, cell))[None, :]
    cellarr(1, 0)[:] = np.clip((1 - smooth(yy, 0.2, 0.95)) * (1 - smooth(xx, 0.55, 1.0)) * (0.35 + 0.65 * n1), 0, 1) * 0.8
    # 2 water streaks: vertical drips from the top
    im = Image.new('L', (cell, cell), 0); d = ImageDraw.Draw(im)
    for _ in range(26):
        x = int(rng.integers(10, cell - 10)); l = int(rng.integers(120, 480)); wv = int(rng.integers(2, 7))
        for k in range(l): d.line((x + np.sin(k / 23.0 + x) * 2.0, k, x + np.sin(k / 23.0 + x) * 2.0, k + 1), fill=int(110 * (1 - k / l) ** 0.8 + 6), width=wv)
    im = im.filter(ImageFilter.GaussianBlur(2.4)); cellarr(2, 0)[:] = np.asarray(im) / 255.0
    # 3 corner grime: quarter radial
    r = np.sqrt(np.linspace(0, 1, cell)[None, :] ** 2 + np.linspace(0, 1, cell)[:, None] ** 2)
    cellarr(3, 0)[:] = np.clip((1 - smooth(r, 0.0, 1.0)) * (0.5 + 0.5 * blob_noise(53, 2.4)), 0, 1) * 0.9
    # 4 handprint-ish smudges around switch height
    im = Image.new('L', (cell, cell), 0); d = ImageDraw.Draw(im)
    for _ in range(14):
        x, y = rng.integers(60, cell - 60, 2); rw, rh = rng.integers(14, 38), rng.integers(22, 60)
        d.ellipse((x - rw, y - rh, x + rw, y + rh), fill=int(rng.integers(30, 90)))
    im = im.filter(ImageFilter.GaussianBlur(7)); cellarr(0, 1)[:] = np.asarray(im) / 255.0
    # 5 skid / tyre marks: curved dark arcs
    im = Image.new('L', (cell, cell), 0); d = ImageDraw.Draw(im)
    for k in range(7):
        x0 = int(rng.integers(-100, 200)); d.arc((x0, 40 + k * 8, x0 + 600, 600 + k * 8), 200, 260, fill=int(rng.integers(60, 130)), width=int(rng.integers(3, 7)))
    im = im.filter(ImageFilter.GaussianBlur(2.2)); cellarr(1, 1)[:] = np.asarray(im) / 255.0
    # 6 stain blotch
    n6 = blob_noise(54, 3.0); yy2 = np.linspace(-1, 1, cell)[:, None]; xx2 = np.linspace(-1, 1, cell)[None, :]
    rr = np.sqrt(xx2 ** 2 + yy2 ** 2); cellarr(2, 1)[:] = np.clip(smooth(n6 - 0.35 * rr, 0.38, 0.62) * (1 - smooth(rr, 0.7, 1.0)), 0, 1) * 0.5
    # 7 edge dust: one-sided gradient
    cellarr(3, 1)[:] = np.clip((1 - np.linspace(0, 1, cell))[:, None] ** 2.2 * (0.45 + 0.55 * blob_noise(55, 1.6)), 0, 1) * 0.9
    rgba = np.zeros((Hh, W, 4), np.uint8); rgba[..., 0] = 34; rgba[..., 1] = 26; rgba[..., 2] = 22; rgba[..., 3] = (np.clip(A, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(TEXDIR, 'wear_atlas.png'))

STAMP = 'v5-6'
def ensure():
    stamp = os.path.join(TEXDIR, '.v5stamp')
    try:
        if open(stamp).read() == STAMP and os.path.exists(os.path.join(TEXDIR, 'wear_atlas.png')): return
    except Exception: pass
    make_plaster(); make_wood(); make_metal(); make_cork(); make_wear_atlas()
    open(stamp, 'w').write(STAMP)

if __name__ == '__main__':
    ensure()
