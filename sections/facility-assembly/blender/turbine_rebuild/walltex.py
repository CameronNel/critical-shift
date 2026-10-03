"""Per-wall texture sets (albedo / ORM / normal). One texture covers one whole wall (planar UV: u along the wall, v = height / 7.2 m).

Painted into the maps: corrugated cladding, panel seams and rivet rows, grime and soot, water streaks and rust bleeds, peeling paint, impact
scuffs, painted zone numerals, evacuation arrows and the warm-gold stripe. Texturing only: no light or shadow is stored.
"""
import math
import numpy as np
import floortex as ft

PXM, HM = 96, 7.2

# 7-segment style stencil digits (segments: a top, b upper-right, c lower-right, d bottom, e lower-left, f upper-left, g middle)
_SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abfgcd'}
def _digit(mask, cx, cy, h, ch, w, value=1.0):
    ww = h * .55; hh = h / 2
    P = dict(a=((-ww, hh), (ww, hh)), g=((-ww, 0), (ww, 0)), d=((-ww, -hh), (ww, -hh)), f=((-ww, 0), (-ww, hh)), b=((ww, 0), (ww, hh)), e=((-ww, -hh), (-ww, 0)), c=((ww, -hh), (ww, 0)))
    for s in _SEG.get(ch, ''):
        (x0, y0), (x1, y1) = P[s]; ft.seg_field(mask, (cx + x0, cy + y0), (cx + x1, cy + y1), w, value, .8)

def generate(prefix, name, L, feat, seed=3):
    from lib import write_png
    ft.W, ft.H, ft.X0, ft.Y0, ft.FW, ft.FH = int(L * PXM), int(HM * PXM), 0.0, 0.0, L, HM
    W, H = ft.W, ft.H; rng = np.random.default_rng(seed)
    px = ft.px
    Z = (np.arange(H, dtype=np.float32) / PXM)[:, None] * np.ones((1, W), np.float32)            # height of each row in metres
    U = np.ones((H, 1), np.float32) * (np.arange(W, dtype=np.float32) / PXM)[None, :]
    low, mid, fine = ft.gnoise(rng, 60), ft.gnoise(rng, 12), ft.gnoise(rng, 1.8)
    # ---------- zones: plinth, wainscot, cap trim, corrugated cladding, dark band, upper smooth panels ----------
    def band(z0, z1): return ((Z >= z0) & (Z < z1)).astype(np.float32)
    cols = {'plinth': (.06, .065, .075), 'wains': (.115, .135, .165), 'cap': (.27, .29, .32), 'clad': (.175, .2, .24), 'dark': (.07, .08, .095), 'upper': (.215, .24, .285)}
    alb = np.zeros((H, W, 3), np.float32)
    for k, (z0, z1) in dict(plinth=(0, .2), wains=(.2, 1.2), cap=(1.2, 1.32), clad=(1.32, 4.45), dark=(4.45, 4.55), upper=(4.55, HM + .01)).items():
        alb += band(z0, z1)[..., None] * np.array(cols[k], np.float32)[None, None, :]
    alb *= (1 + .08 * low[..., None] + .05 * mid[..., None] + .03 * fine[..., None])
    rough = (.78 + .06 * mid).astype(np.float32); rough -= .22 * band(.2, 1.2)                        # painted steel wainscot is semi-gloss
    height = (.02 * mid + .01 * fine).astype(np.float32)
    # corrugated cladding (trapezoid ribs, 0.2 m pitch) between 1.32 and 4.45
    cl = band(1.32, 4.45); ph = (U / .2) % 1.0; rib = np.clip(np.minimum(ph, 1 - ph) * 5.0 - .35, 0, 1)
    height += cl * rib * 1.0; alb *= 1 + cl[..., None] * (rib[..., None] - .5) * .09
    # ---------- seams, rivet rows ----------
    S = np.zeros((H, W), np.float32)
    pitch = feat.get('seam_pitch', 1.5)
    for k in range(1, int(L / pitch) + 1):
        u = k * pitch
        if u < L - .05: ft.stroke(S, [px(u, 0.2), px(u, 1.2)], 2.0, 1.0, .8); ft.stroke(S, [px(u, 4.55), px(u, HM)], 2.0, 1.0, .8)
    for z in (1.2, 4.45, 4.55, 5.55, 6.45): ft.stroke(S, [px(0, z), px(L, z)], 2.0, 1.0, .8)
    for u in feat.get('cols', []): ft.stroke(S, [px(u, 0), px(u, HM)], 2.6, 1.0, .8)
    height -= 2.0 * S; alb *= (1 - .55 * S)[..., None]
    Rv = np.zeros((H, W), np.float32); rust = np.zeros((H, W), np.float32)
    for k in range(1, int(L / pitch) + 1):
        u = k * pitch
        for z in np.arange(.25, 1.2, .15): ft.blob(Rv, *px(u + .04, z), 1.7, rng, .1, .7); ft.blob(Rv, *px(u - .04, z), 1.7, rng, .1, .7)
        for z in np.arange(4.65, HM - .1, .25): ft.blob(Rv, *px(u + .04, z), 1.5, rng, .1, .7)
        if rng.random() < .8: ft.stroke(rust, [px(u + .04, 1.1), px(u + .05 + rng.uniform(-.02, .02), rng.uniform(.3, 1.0))], 3.0, rng.uniform(.4, .9), 2.5)
    height += 1.1 * Rv; alb *= 1 + .1 * Rv[..., None]
    # ---------- grime, soot, streaks, efflorescence ----------
    dirt = np.clip(np.exp(-Z / .9) * .55 + .22 * np.clip(mid, 0, 2) * np.exp(-Z / 2.4), 0, .8)
    soot = np.clip((Z - 5.6) / 1.6, 0, 1) * np.clip(.55 + .4 * low, 0, 1) * .55
    alb *= (1 - .55 * dirt - .5 * soot)[..., None]
    streak = np.zeros((H, W), np.float32); wetm = np.zeros((H, W), np.float32)
    for _ in range(26):
        u = rng.uniform(.2, L - .2); z1 = HM - rng.uniform(.05, .6); z0 = z1 - rng.uniform(.6, 3.2)
        ft.stroke(streak, [px(u, z1), px(u + rng.uniform(-.05, .05), z0)], rng.uniform(3, 11), rng.uniform(.3, .8), 3.0)
    for (u, z, z0) in feat.get('leaks', []): ft.stroke(wetm, [px(u, z), px(u + .03, z0)], 4.5, .9, 3.0)
    streak = ft.blur(streak * np.clip(.6 + .6 * mid, 0, 1), 1.2); wetm = ft.blur(wetm, 1.0)
    alb *= (1 - .35 * streak)[..., None]; rough = rough * (1 - .35 * streak) + .3 * .35 * streak; rough = rough * (1 - wetm) + .12 * wetm; alb *= (1 - .25 * wetm)[..., None]
    for (u0, u1) in feat.get('floor_runs', [(0, L)]):
        for _ in range(int((u1 - u0) / .6)):
            ft.blob(streak, *px(rng.uniform(u0, u1), rng.uniform(.0, .3)), rng.uniform(4, 11), rng, .5, 2.0, 1.6, .7, .6)
    alb[..., :] += (streak * .0)[..., None]
    rust = ft.blur(rust, 2.0); alb += np.stack([.075, .033, .016])[None, None, :] * rust[..., None]; rough = np.maximum(rough, .6 * rust)
    # ---------- peeling paint, scuffs, dents ----------
    P = np.zeros((H, W), np.float32)
    for _ in range(18):
        z = rng.choice([rng.uniform(.05, .8), rng.uniform(.8, 4.4)]); ft.blob(P, *px(rng.uniform(.2, L - .2), z), rng.uniform(6, 20), rng, .55, 1.5)
    edge = np.clip(ft.blur(P, 1.2) - P * .6, 0, 1); alb = alb * (1 - .65 * P[..., None]) + P[..., None] * np.array([.11, .075, .06], np.float32) * (1 + .3 * mid[..., None])
    alb += np.stack([.05, .02, .01])[None, None, :] * np.clip(edge, 0, 1)[..., None]; rough = rough * (1 - P) + .88 * P; height -= .8 * P
    Sc = np.zeros((H, W), np.float32)
    for _ in range(90):
        u, z = rng.uniform(.2, L - .2), rng.uniform(.25, 1.3); a = rng.uniform(-.7, .7); l = rng.uniform(.08, .5) * PXM
        ft.seg_field(Sc, px(u, z), (px(u, z)[0] + math.cos(a) * l, px(u, z)[1] + math.sin(a) * l), rng.uniform(1.2, 3.5), rng.uniform(.4, 1.0), .7)
    alb += .08 * Sc[..., None]; rough = rough * (1 - .6 * Sc) + .35 * .6 * Sc
    Dn = np.zeros((H, W), np.float32)
    for _ in range(9): ft.blob(Dn, *px(rng.uniform(.5, L - .5), rng.uniform(.3, 1.1)), rng.uniform(5, 12), rng, .3, 4.0)
    height -= 1.6 * Dn
    # ---------- painted marks: gold stripe, bay numerals, arrows ----------
    gold = np.array([.40, .30, .11], np.float32); G = np.zeros((H, W), np.float32)
    ft.stroke(G, [px(0, 3.26), px(L, 3.26)], .05 * PXM, 1.0, 1.0)
    for (u, ch) in feat.get('bay_marks', []):
        _digit(G, *px(u, 2.35), .34 * PXM, ch, 4.2)
        ft.seg_field(G, px(u - .22, 1.95), px(u + .22, 1.95), 3.0, 1.0, .8)
    for (u, z, d) in feat.get('arrows', []):
        x, y = px(u, z); l = .42 * PXM
        ft.seg_field(G, (x - d * l / 2, y), (x + d * l / 2, y), 6, 1.0, .8); ft.seg_field(G, (x + d * l / 2, y), (x + d * l * .2, y + l * .28), 6, 1.0, .8); ft.seg_field(G, (x + d * l / 2, y), (x + d * l * .2, y - l * .28), 6, 1.0, .8)
    G *= np.clip(.82 + .5 * fine + .3 * mid, 0, 1) * (1 - .6 * P)
    alb = alb * (1 - G[..., None]) + G[..., None] * gold; rough = rough * (1 - G) + .55 * G; height += .4 * G
    # ---------- write ----------
    write_png(f'{prefix}_{name}_albedo.png', (np.clip(alb, 0, 1) * 255 + .5).astype(np.uint8))
    orm = np.stack([np.ones_like(rough), np.clip(rough, .05, 1), np.zeros_like(rough)], axis=-1); write_png(f'{prefix}_{name}_orm.png', (orm * 255 + .5).astype(np.uint8))
    height = ft.blur(height, .8); k = 3.2
    dhx = np.gradient(height, axis=1) * k; dhy = np.gradient(height, axis=0) * k
    n = np.stack([-dhx, -dhy, np.ones_like(dhx)], axis=-1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    write_png(f'{prefix}_{name}_normal.png', ((n * .5 + .5) * 255 + .5).astype(np.uint8))
    return (W, H)
