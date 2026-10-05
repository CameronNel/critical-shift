"""Night sky for the front-end area: a deterministic equirectangular star map (textures/night_sky.jpg).

Real star positions (RA/Dec, approximate J2000) for the named constellations and the brightest stars, seen from latitude 40 N at local
sidereal time 8.5 h, so Orion hangs in the south-west with Taurus beyond it and Capella high in the north-west. The Milky Way band is laid on the real
galactic plane with dust lanes. A gibbous moon is painted at MOON_DIR; fe_lighting puts the moon light at the same direction.

World direction frame: +x east, +y north, +z up. Blender equirect mapping: u = 0.5 - atan2(d.y, d.x) / 2pi, v = atan2(d.z, hypot(d.x, d.y)) / pi + 0.5.
Run standalone (python3, needs numpy and Pillow) or through ensure().
"""
import math, os
import numpy as np

LAT = math.radians(40.0); LST_H = 8.5
W, H = 6144, 3072
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures', 'night_sky.jpg')
GAIN = 4.0                                   # image value 1.0 = 4x linear in the world shader

# name: ([(star, ra_h, dec_deg, mag), ...], [(i, j), ...] line pairs)
CONST = {
 'Orion': ([('Betelgeuse', 5.919, 7.407, 0.5), ('Rigel', 5.242, -8.202, 0.12), ('Bellatrix', 5.419, 6.350, 1.64), ('Mintaka', 5.533, -0.299, 2.2),
            ('Alnilam', 5.603, -1.202, 1.7), ('Alnitak', 5.679, -1.943, 1.75), ('Saiph', 5.796, -9.670, 2.1), ('Meissa', 5.585, 9.934, 3.3)],
           [(7, 0), (7, 2), (0, 5), (2, 3), (3, 4), (4, 5), (5, 6), (3, 1)]),
 'Taurus': ([('Aldebaran', 4.599, 16.509, 0.85), ('Elnath', 5.438, 28.608, 1.65), ('Zeta Tau', 5.627, 21.14, 3.0), ('Gamma Tau', 4.330, 15.63, 3.65),
             ('Delta Tau', 4.382, 17.54, 3.77), ('Epsilon Tau', 4.477, 19.18, 3.53), ('Theta Tau', 4.478, 15.87, 3.4), ('Lambda Tau', 4.011, 12.49, 3.5)],
            [(2, 0), (0, 3), (3, 4), (4, 5), (5, 1), (3, 7), (0, 6)]),
 'Pleiades': ([('Alcyone', 3.790, 24.105, 2.87), ('Atlas', 3.820, 24.053, 3.6), ('Electra', 3.748, 24.113, 3.7), ('Maia', 3.763, 24.368, 3.9),
               ('Merope', 3.772, 23.948, 4.2), ('Taygeta', 3.754, 24.467, 4.3), ('Pleione', 3.821, 24.138, 5.0)], []),
 'Big Dipper': ([('Dubhe', 11.062, 61.751, 1.8), ('Merak', 11.031, 56.382, 2.4), ('Phecda', 11.897, 53.695, 2.4), ('Megrez', 12.257, 57.033, 3.3),
                 ('Alioth', 12.900, 55.960, 1.8), ('Mizar', 13.399, 54.925, 2.2), ('Alkaid', 13.792, 49.313, 1.9)],
                [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 6)]),
 'Cassiopeia': ([('Caph', 0.153, 59.150, 2.3), ('Schedar', 0.675, 56.537, 2.2), ('Gamma Cas', 0.945, 60.717, 2.5), ('Ruchbah', 1.430, 60.235, 2.7), ('Segin', 1.907, 63.670, 3.4)],
                [(0, 1), (1, 2), (2, 3), (3, 4)]),
 'Gemini': ([('Castor', 7.577, 31.888, 1.58), ('Pollux', 7.755, 28.026, 1.14), ('Alhena', 6.629, 16.399, 1.9), ('Tejat', 6.383, 22.514, 2.9),
             ('Mebsuta', 6.732, 25.131, 3.0), ('Wasat', 7.335, 21.982, 3.5), ('Propus', 6.248, 22.507, 3.3)],
            [(0, 4), (4, 3), (3, 6), (1, 5), (5, 2), (4, 5)]),
 'Canis Major': ([('Sirius', 6.752, -16.716, -1.46), ('Mirzam', 6.378, -17.956, 2.0), ('Adhara', 6.977, -28.972, 1.5), ('Wezen', 7.140, -26.393, 1.84),
                  ('Aludra', 7.403, -29.303, 2.45)], [(0, 1), (0, 3), (3, 2), (3, 4)]),
 'Auriga': ([('Capella', 5.278, 45.998, 0.08), ('Menkalinan', 5.992, 44.947, 1.9), ('Mahasim', 5.995, 37.213, 2.6), ('Hassaleh', 4.950, 33.166, 2.7), ('Elnath ', 5.438, 28.608, 1.65)],
            [(0, 1), (1, 2), (2, 4), (4, 3), (3, 0)]),
 'Ursa Minor': ([('Polaris', 2.530, 89.264, 2.0), ('Yildun', 17.537, 86.586, 4.3), ('Eps UMi', 16.766, 82.037, 4.2), ('Zeta UMi', 15.734, 77.795, 4.3),
                 ('Eta UMi', 16.292, 75.755, 5.0), ('Pherkad', 15.345, 71.834, 3.0), ('Kochab', 14.845, 74.156, 2.1)],
                [(0, 1), (1, 2), (2, 3), (3, 6), (6, 5), (5, 4), (4, 3)]),
 'Leo': ([('Regulus', 10.140, 11.967, 1.4), ('Denebola', 11.818, 14.572, 2.1), ('Algieba', 10.333, 19.842, 2.0), ('Zosma', 11.235, 20.524, 2.6),
          ('Eta Leo', 10.122, 16.763, 3.5), ('Adhafera', 10.278, 23.417, 3.4), ('Rasalas', 9.879, 26.007, 3.9), ('Eps Leo', 9.764, 23.774, 3.0)],
         [(0, 4), (4, 2), (2, 5), (5, 6), (6, 7), (2, 3), (3, 1), (1, 0)]),
 'Cygnus': ([('Deneb', 20.690, 45.280, 1.25), ('Sadr', 20.370, 40.257, 2.2), ('Albireo', 19.512, 27.960, 3.1), ('Gienah', 20.770, 33.970, 2.5), ('Delta Cyg', 19.750, 45.131, 2.9)],
            [(0, 1), (1, 2), (3, 1), (4, 1)]),
 'Lyra': ([('Vega', 18.616, 38.784, 0.03), ('Sheliak', 18.834, 33.363, 3.5), ('Sulafat', 18.982, 32.690, 3.3), ('Zeta Lyr', 18.746, 37.605, 4.3), ('Delta Lyr', 18.909, 36.899, 4.3)],
          [(0, 3), (3, 4), (4, 2), (2, 1), (1, 3)]),
 'Scorpius': ([('Antares', 16.490, -26.432, 1.0), ('Graffias', 16.091, -19.805, 2.6), ('Dschubba', 16.005, -22.622, 2.3), ('Sargas', 17.622, -42.998, 1.9),
               ('Shaula', 17.560, -37.104, 1.6), ('Epsilon Sco', 16.836, -34.293, 2.3)], [(1, 2), (2, 0), (0, 5), (5, 3), (3, 4)]),
 'Bootes': ([('Arcturus', 14.261, 19.182, -0.05), ('Izar', 14.750, 27.074, 2.4), ('Seginus', 14.535, 38.308, 3.0), ('Nekkar', 15.032, 40.390, 3.5), ('Muphrid', 13.911, 18.398, 2.7)],
            [(0, 1), (1, 2), (2, 3), (0, 4)]),
}
SINGLES = [('Procyon', 7.655, 5.225, 0.34), ('Altair', 19.846, 8.868, 0.77), ('Spica', 13.420, -11.161, 1.0), ('Fomalhaut', 22.961, -29.622, 1.16),
           ('Alphard', 9.460, -8.659, 2.0), ('Hamal', 2.120, 23.462, 2.0), ('Mirfak', 3.405, 49.861, 1.8), ('Algol', 3.136, 40.956, 2.1), ('Deneb Kaitos', 0.727, -17.987, 2.0),
           ('Alpheratz', 0.139, 29.091, 2.1), ('Markab', 23.079, 15.205, 2.5), ('Dubhe2', 11.062, 61.751, 1.8), ('Canopus', 6.399, -52.696, -0.74), ('Capella2', 5.278, 45.998, 0.08)]
NGP = (192.859, 27.128); GC = (266.405, -28.936)   # galactic north pole and centre (RA deg, Dec deg)

def altaz_vec(ra_h, dec_deg):
    """Unit vector (x east, y north, z up) for an RA/Dec at LAT, LST_H."""
    ha = math.radians((LST_H - ra_h) * 15.0); dec = math.radians(dec_deg)
    sa = math.sin(dec) * math.sin(LAT) + math.cos(dec) * math.cos(LAT) * math.cos(ha)
    alt = math.asin(max(-1.0, min(1.0, sa)))
    az = math.atan2(-math.cos(dec) * math.sin(ha), math.sin(dec) * math.cos(LAT) - math.cos(dec) * math.sin(LAT) * math.cos(ha))
    return np.array([math.sin(az) * math.cos(alt), math.cos(az) * math.cos(alt), math.sin(alt)])

MOON_AZ, MOON_ALT = 288.0, 33.0
def moon_dir():
    a, e = math.radians(MOON_AZ), math.radians(MOON_ALT)
    return np.array([math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)])

def to_uv(v):
    u = 0.5 - math.atan2(v[1], v[0]) / (2 * math.pi); vv = math.atan2(v[2], math.hypot(v[0], v[1])) / math.pi + 0.5
    return u * W, (1.0 - vv) * H

def _fbm(rng, h, w, octaves, base):
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0
    from PIL import Image
    for o in range(octaves):
        n = max(base * 2 ** o, 2); g = rng.random((max(n // 2, 2), n)).astype(np.float32)
        im = Image.fromarray(g, mode='F').resize((w, h), Image.BICUBIC); a = np.asarray(im)
        out += amp * a; tot += amp; amp *= 0.55
    return out / tot

def generate(path=OUT):
    from PIL import Image, ImageDraw, ImageFilter
    rng = np.random.default_rng(20261003)
    img = np.zeros((H, W, 3), np.float32)
    ngp = altaz_vec(NGP[0] / 15.0, NGP[1]); gc = altaz_vec(GC[0] / 15.0, GC[1])
    gc = gc - ngp * np.dot(gc, ngp); gc /= np.linalg.norm(gc); e2 = np.cross(ngp, gc)
    # ---- Milky Way: brightness from galactic latitude, a brighter bulge, dust lanes from noise in (l, b)
    gl, gb = 2048, 1024
    noise = _fbm(rng, gb, gl, 6, 8); lanes = _fbm(rng, gb, gl, 5, 14)
    for r0 in range(0, H, 256):
        rows = np.arange(r0, min(r0 + 256, H)); vv = 1.0 - (rows + 0.5) / H; el = (vv - 0.5) * math.pi
        uu = (np.arange(W) + 0.5) / W; az = (0.5 - uu) * 2 * math.pi            # u = 0.5 - atan2(y, x)/2pi
        X = np.cos(az)[None, :] * np.cos(el)[:, None]; Y = np.sin(az)[None, :] * np.cos(el)[:, None]; Z = np.broadcast_to(np.sin(el)[:, None], X.shape)
        sb = X * ngp[0] + Y * ngp[1] + Z * ngp[2]; b = np.arcsin(np.clip(sb, -1, 1))
        l = np.arctan2(X * e2[0] + Y * e2[1] + Z * e2[2], X * gc[0] + Y * gc[1] + Z * gc[2])
        li = ((l / (2 * math.pi)) % 1.0) * (gl - 1); bi = (b / math.pi + 0.5) * (gb - 1)
        i0 = np.floor(li).astype(int); j0 = np.floor(bi).astype(int); fx = (li - i0).astype(np.float32); fy = (bi - j0).astype(np.float32)
        i1 = (i0 + 1) % gl; j1 = np.clip(j0 + 1, 0, gb - 1); j0 = np.clip(j0, 0, gb - 1)
        def samp(M): return (M[j0, i0] * (1 - fx) + M[j0, i1] * fx) * (1 - fy) + (M[j1, i0] * (1 - fx) + M[j1, i1] * fx) * fy
        n = samp(noise); ln = samp(lanes)
        bd = np.degrees(b); core = np.exp(-(bd / (7.5 + 5.0 * np.exp(-(np.degrees(l) / 40.0) ** 2))) ** 2)
        bulge = 0.55 + 0.9 * np.exp(-(np.degrees(l) / 38.0) ** 2)
        patch = np.clip((n - 0.30) / 0.30, 0.0, 1.4)
        dust = np.clip(1.0 - 1.9 * np.clip((ln - 0.52) / 0.18, 0, 1) * np.exp(-(bd / 6.0) ** 2), 0.12, 1.0)
        mw = 0.010 * core * bulge * (0.35 + 0.85 * patch) * dust
        tint = np.array([1.0, 0.93, 0.80], np.float32); cool = np.array([0.80, 0.88, 1.0], np.float32)
        wcol = (bulge / 1.45)[..., None] * tint + (1 - bulge / 1.45)[..., None] * cool
        img[rows[0]:rows[-1] + 1] = (mw[..., None] * wcol)
    # ---- stars
    def splat(px, py, lin, color, sigma):
        r = int(math.ceil(sigma * 3.2)) + 1; ix = int(round(px)); iy = int(round(py))
        ys = np.arange(iy - r, iy + r + 1); xs = np.arange(ix - r, ix + r + 1)
        if ys[0] < 0 or ys[-1] >= H: ys = ys[(ys >= 0) & (ys < H)]
        if len(ys) == 0: return
        g = np.exp(-(((ys[:, None] - py) ** 2) + (((xs[None, :] - px + W / 2) % W - W / 2) ** 2)) / (2 * sigma ** 2))
        img[ys[:, None], (xs[None, :]) % W] += (g * lin)[..., None] * color
    def star_color(ci): return np.array([[0.75, 0.85, 1.0], [1.0, 1.0, 1.0], [1.0, 0.88, 0.7], [1.0, 0.7, 0.5]][ci], np.float32)
    named = {}
    for cname, (stars, lines) in CONST.items():
        for (nm, ra, dec, mag) in stars:
            v = altaz_vec(ra, dec)
            if nm in ('Betelgeuse', 'Antares', 'Aldebaran', 'Arcturus'): col = star_color(3)
            elif nm in ('Rigel', 'Vega', 'Sirius', 'Bellatrix', 'Spica'): col = star_color(0)
            elif nm in ('Capella', 'Pollux'): col = star_color(2)
            else: col = star_color(1)
            px, py = to_uv(v); lin = min(0.30 * 10 ** (-0.4 * (mag - 3.0)), 6.0) / GAIN * 4.0; sig = 0.9 + 0.30 * max(0.0, 3.2 - mag)
            splat(px, py, lin, col, sig)
            if mag < 1.3:                                                      # soft halo for the brightest
                splat(px, py, 0.06 * lin, col, sig * 4.0)
    for (nm, ra, dec, mag) in SINGLES:
        px, py = to_uv(altaz_vec(ra, dec)); lin = min(0.30 * 10 ** (-0.4 * (mag - 3.0)), 6.0) / GAIN * 4.0; sig = 0.9 + 0.30 * max(0.0, 3.2 - mag); splat(px, py, lin, star_color(1), sig)
    # field stars: 40 percent on the galactic plane, the rest uniform on the sphere
    N = 16000
    mags = 3.6 + 3.3 * rng.random(N) ** 0.6
    for k in range(N):
        if rng.random() < 0.5:
            l_ = rng.uniform(0, 2 * math.pi); b_ = rng.normal(0, 0.10) * (0.6 + 0.9 * math.exp(-(math.degrees(l_) % 360 - 0) ** 2 / 2e4)) if False else rng.normal(0, math.radians(9.0))
            v = math.cos(b_) * math.cos(l_) * gc + math.cos(b_) * math.sin(l_) * e2 + math.sin(b_) * ngp
        else:
            z = rng.uniform(-1, 1); t = rng.uniform(0, 2 * math.pi); s = math.sqrt(1 - z * z); v = np.array([s * math.cos(t), s * math.sin(t), z])
        px, py = to_uv(v); lin = 0.30 * 10 ** (-0.4 * (mags[k] - 3.0)) / GAIN * 4.0
        splat(px, py, lin, star_color(int(rng.choice(4, p=[0.2, 0.45, 0.25, 0.1]))), 0.75 + 0.12 * rng.random())
    # ---- moon: gibbous disc with maria, lit from the left-below; exaggerated to about 1.1 degrees radius
    md = moon_dir(); mx, my = to_uv(md); R = 19.0; yy, xx = np.mgrid[int(my - 140):int(my + 141), int(mx - 140):int(mx + 141)]
    dx = (xx - mx) / R; dy = (yy - my) / R; rr2 = dx * dx + dy * dy
    dpx = np.sqrt(rr2) * R; fade = np.clip((140.0 - dpx) / 60.0, 0, 1)
    glow = (0.010 * np.exp(-dpx / 8.0) + 0.0015 * np.exp(-dpx / 40.0)) * fade
    nz = np.asarray(Image.fromarray(rng.random((12, 12)).astype(np.float32), mode='F').resize((282, 282), Image.BICUBIC))[:rr2.shape[0], :rr2.shape[1]]
    disc = rr2 <= 1.0; nzv = np.sqrt(np.clip(1 - rr2, 0, 1)); light = np.array([-0.55, -0.25, 0.8]); light /= np.linalg.norm(light)
    lam = np.clip(dx * light[0] + dy * light[1] + nzv * light[2], 0, 1)
    surf = (0.78 - 0.30 * np.clip((nz - 0.45) * 3.0, 0, 1)) * lam ** 0.6
    edge = np.clip((1.0 - np.sqrt(rr2)) * R, 0, 1)
    moon = np.where(disc, 1.15 * surf * edge, 0.0) / 1.0
    mcol = np.array([1.0, 0.97, 0.90], np.float32)
    ys = (yy % H); xs = (xx % W)
    img[ys, xs] += ((moon + glow)[..., None] * mcol)
    # ---- constellation lines: faint blue on a separate layer, drawn as great-circle polylines
    layer = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(layer)
    for cname, (stars, lines) in CONST.items():
        vs = [altaz_vec(ra, dec) for (_, ra, dec, _) in stars]
        for (i, j) in lines:
            a, b2 = vs[i], vs[j]; ang = math.acos(max(-1, min(1, float(np.dot(a, b2))))); n = max(int(ang / 0.004), 2); pts = []
            for t in np.linspace(0.06, 0.94, n):
                p = (a * math.sin((1 - t) * ang) + b2 * math.sin(t * ang)) / max(math.sin(ang), 1e-6); pts.append(to_uv(p))
            seg = [pts[0]]
            for p in pts[1:]:
                if abs(p[0] - seg[-1][0]) > W / 2:
                    if len(seg) > 1: dr.line(seg, fill=255, width=2)
                    seg = [p]
                else: seg.append(p)
            if len(seg) > 1: dr.line(seg, fill=255, width=2)
    lm = np.asarray(layer.filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255.0
    img += lm[..., None] * np.array([0.0045, 0.0100, 0.0200], np.float32) * 0.9
    # ---- encode: linear -> sRGB, dither so the dark gradient does not band
    lin = np.clip(img, 0.0, 1.0)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    srgb = srgb * 255.0
    srgb = np.where(srgb < 2.0, 0.0, srgb + rng.random(srgb.shape, dtype=np.float32) - 0.5)
    Image.fromarray(np.clip(np.round(srgb), 0, 255).astype(np.uint8), 'RGB').save(path, quality=94, subsampling=0, optimize=True)
    return path

def ensure():
    if not os.path.exists(OUT): generate(OUT)
    return OUT

if __name__ == '__main__':
    print(generate())
