"""Paint + material maps for the two steel drums (system python / PIL).  python3 drumtex.py OUT_DIR
Layout (1024^2, v up): rows 0.5-1.0 = painted body wall (u wraps the circumference, label centred at u=.75, facing -Y);
rows 0-0.5 = bare steel (lid, bottom, bungs: planar UVs into the lower-left square)."""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
N = 1024
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def noise(rng, cell, shape=(N, N)):
    n = rng.random((shape[0] // cell + 2, shape[1] // cell + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)).astype(np.float32) / 255

def make(path, paint, text1, text2, text3, code, seed):
    rng = np.random.default_rng(seed)
    H = N // 2; body = np.zeros((H, N, 3), np.float32); base = np.array(paint, np.float32)
    # row 0 = top of the body strip in image space. z=.87 at top
    z = np.linspace(.87, 0, H, dtype=np.float32)[:, None]
    shade = (1 - .22 * np.clip(1 - z / .5, 0, 1) ** 1.5) * (1 + .05 * np.sin(np.linspace(0, 6.28, N))[None, :])
    body[:] = base * shade[..., None]
    g = 1 + (noise(rng, 64, (H, N)) - .5) * .16 + (noise(rng, 16, (H, N)) - .5) * .07 + (rng.random((H, N)).astype(np.float32) - .5) * .03
    body *= g[..., None]
    # vertical dirt streaks, heavier toward the bottom
    sx = np.asarray(Image.fromarray((rng.random((1, 90)) * 255).astype(np.uint8)).resize((N, H), Image.BICUBIC)).astype(np.float32) / 255
    body *= (1 - .38 * np.clip(sx - .5, 0, 1) * 2 * (.25 + (1 - z / .87) ** 1.2))[..., None]
    # rolling hoops: z of crest .23 and .62 -> rows; chipped paint (bright metal) on crests, dark grime in the valleys
    metal = np.zeros((H, N), np.float32); rough = np.full((H, N), .52, np.float32)
    for zc in (.216, .62):
        r0 = int((.87 - zc) / .87 * H)
        for dr, w in ((0, 1.0), (-14, .25), (14, .25)):
            band = np.exp(-((np.arange(H) - (r0 + dr)) / 4.5) ** 2)[:, None]
            chips = np.clip((noise(rng, 6, (H, N)) - .66) * 6, 0, 1)
            metal = np.maximum(metal, band * chips * w)
        valley = np.exp(-((np.arange(H) - (r0 + 22)) / 8) ** 2)[:, None]; body *= (1 - .3 * valley)[..., None]
    for zc in (.04, .85):                                        # chime rings: rust and wear
        r0 = int((.87 - zc) / .87 * H); band = np.exp(-((np.arange(H) - r0) / 14) ** 2)[:, None]
        chips = np.clip((noise(rng, 9, (H, N)) - .5) * 5, 0, 1); metal = np.maximum(metal, band * chips)
        body = body * (1 - .55 * band[..., None] * chips[..., None]) + np.array([.34, .17, .08]) * .55 * band[..., None] * chips[..., None] * 255
    body = body * (1 - metal[..., None]) + np.array([150, 148, 144], np.float32) * metal[..., None]
    rough = rough * (1 - metal) + .30 * metal
    # scuffs and dents shading
    sc = Image.new('L', (N, H), 0); d = ImageDraw.Draw(sc)
    for _ in range(90):
        x, y = rng.random() * N, rng.random() * H; l = rng.random() * 60 + 10; t = rng.random() * 3.14
        d.line([(x, y), (x + math.cos(t) * l, y + math.sin(t) * l * .25)], fill=int(70 + rng.random() * 120), width=1)
    s2 = np.asarray(sc.filter(ImageFilter.GaussianBlur(.7))).astype(np.float32) / 255
    body = body * (1 - .18 * s2[..., None]) + 38 * s2[..., None]
    img = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8), 'RGB').convert('RGBA'); d = ImageDraw.Draw(img)
    # stencil label, centred at u=.75, z .30-.64 -> rows
    cx = int(N * .68); tcol = (214, 210, 196, 255); amb = (176, 140, 52, 255)
    zr = lambda zz: int((.87 - zz) / .87 * H)
    for zz in (.565, .305): d.rectangle([cx - 175, zr(zz) - 4, cx + 175, zr(zz) + 6], fill=amb)                      # thin amber rules
    f1 = ImageFont.truetype(FB, 70 if len(text1) < 8 else 60); d.text((cx, zr(.495)), text1, font=f1, fill=tcol, anchor='mm')
    f2 = ImageFont.truetype(FR, 28); d.text((cx, zr(.425)), text2, font=f2, fill=amb, anchor='mm')
    f3 = ImageFont.truetype(FR, 17); d.text((cx, zr(.375)), text3, font=f3, fill=tcol, anchor='mm')
    d.text((cx, zr(.338)), code, font=ImageFont.truetype(FR, 14), fill=(190, 186, 172, 255), anchor='mm')
    # thin flame pictogram outline either side of the title
    tw = f1.getlength(text1) / 2
    for sx_ in (-1, 1):
        px, py = cx + sx_ * (tw + 30), zr(.495); s = 26
        d.line([(px, py - s), (px + s * .6, py - s * .1), (px + s * .45, py + s * .8), (px - s * .45, py + s * .8), (px - s * .6, py - s * .1), (px - s * .15, py - s * .45), (px, py - s)], fill=amb, width=3, joint='curve')
    # stencil wear: knock back the label a little so it sits in the paint
    arr = np.asarray(img).astype(np.float32); wear = np.clip((noise(rng, 5, (H, N)) - .70) * 5, 0, 1)
    arr[..., :3] = arr[..., :3] * (1 - .10 * wear[..., None])
    full = np.zeros((N, N, 3), np.float32); full[:H] = np.clip(arr[..., :3], 0, 255)
    # steel half (lower rows)
    st = np.zeros((H, N, 3), np.float32); st[:] = np.array([84, 86, 90], np.float32)
    st *= (1 + (noise(rng, 48, (H, N)) - .5) * .35 + (noise(rng, 6, (H, N)) - .5) * .12 + (rng.random((H, N)).astype(np.float32) - .5) * .06)[..., None]
    yy, xx = np.mgrid[0:H, 0:N].astype(np.float32)
    ring = np.exp(-((np.hypot(xx - 240, yy - 240) - 140) / 6) ** 2)                           # swirl of scratch rings on the lid
    st *= (1 - .12 * ring[..., None]) * (1 - .22 * np.clip(noise(rng, 20, (H, N)) - .55, 0, 1)[..., None] * 3 * 0.3)
    rust = np.clip((noise(rng, 30, (H, N)) - .66) * 5, 0, 1); st = st * (1 - rust[..., None] * .6) + np.array([110, 60, 30], np.float32) * rust[..., None] * .6
    full[H:] = np.clip(st, 0, 255)
    Image.fromarray(full.astype(np.uint8), 'RGB').save(path + '_albedo.png')
    orm = np.zeros((N, N, 3), np.float32); orm[..., 0] = 255
    orm[:H, :, 1] = np.clip(rough, 0, 1) * 255; orm[:H, :, 2] = metal * 255
    orm[H:, :, 1] = (.38 + .2 * rust) * 255; orm[H:, :, 2] = (.85 - .5 * rust) * 255
    Image.fromarray(orm.astype(np.uint8), 'RGB').save(path + '_orm.png')

if __name__ == '__main__':
    out = sys.argv[1]
    make(os.path.join(out, 'drum_a'), (152, 58, 40), 'DIESEL', 'FLAMMABLE', 'KEEP AWAY FROM IGNITION', 'UN1202   200 L   BATCH 2231', 3)
    make(os.path.join(out, 'drum_b'), (46, 62, 78), 'LUBE OIL', 'ISO VG 46', 'TURBINE GRADE', 'ZN FREE   200 L   BATCH 0877', 4)
