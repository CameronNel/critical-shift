"""Floor texture set for the single floor slab (one planar UV over the whole 14 x 24 m floor).

Writes floor_albedo.png (sRGB), floor_orm.png (R=1, G=roughness, B=metal) and floor_normal.png (tangent normal).
Wetness, flow, dampness, polish, joints, cracks, spalls, stains, repairs, scuffs and worn paint all live in these maps.
This is texturing, not a lighting bake: nothing here contains light or shadow.
"""
import math
import numpy as np

X0, Y0, FW, FH = -4.0, 0.0, 14.0, 24.0
PXM = 160                                   # texels per metre
W, H = int(FW * PXM), int(FH * PXM)         # 2240 x 3840

def px(x, y): return (x - X0) / FW * W, (y - Y0) / FH * H

def gnoise(rng, sigma):
    w = rng.standard_normal((H, W)).astype(np.float32)
    F = np.fft.rfft2(w); fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.rfftfreq(W)[None, :]
    F *= np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2)).astype(np.float32)
    n = np.fft.irfft2(F, s=(H, W)).astype(np.float32)
    return (n - n.mean()) / (n.std() + 1e-6)

def seg_field(mask, p0, p1, width, value=1.0, soft=1.0):
    (x0, y0), (x1, y1) = p0, p1; pad = int(width / 2 + soft + 2)
    xa, xb = max(0, int(min(x0, x1)) - pad), min(W, int(max(x0, x1)) + pad + 1)
    ya, yb = max(0, int(min(y0, y1)) - pad), min(H, int(max(y0, y1)) + pad + 1)
    if xb <= xa or yb <= ya: return
    X, Y = np.meshgrid(np.arange(xa, xb, dtype=np.float32), np.arange(ya, yb, dtype=np.float32))
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1); d = np.hypot(X - (x0 + t * dx), Y - (y0 + t * dy))
    m = np.clip(1 - (d - width / 2) / soft, 0, 1) * value
    sub = mask[ya:yb, xa:xb]; np.maximum(sub, m, out=sub)

def stroke(mask, pts, width, value=1.0, soft=1.0):
    for a, b in zip(pts, pts[1:]): seg_field(mask, a, b, width, value, soft)

def blob(mask, cx, cy, r, rng, irr=.25, soft=2.0, ax=1.0, ay=1.0, value=1.0):
    ph = rng.uniform(0, 6.28, 3); R = r * 1.0 + soft + 2; xa, xb = max(0, int(cx - R * ax)), min(W, int(cx + R * ax) + 1); ya, yb = max(0, int(cy - R * ay)), min(H, int(cy + R * ay) + 1)
    if xb <= xa or yb <= ya: return
    X, Y = np.meshgrid(np.arange(xa, xb, dtype=np.float32), np.arange(ya, yb, dtype=np.float32))
    dx, dy = (X - cx) / ax, (Y - cy) / ay; d = np.hypot(dx, dy); th = np.arctan2(dy, dx)
    k = 1 + irr * (np.sin(2 * th + ph[0]) * .5 + np.sin(3 * th + ph[1]) * .3 + np.sin(5 * th + ph[2]) * .2)
    m = np.clip((r * k - d) / soft, 0, 1) * value
    sub = mask[ya:yb, xa:xb]; np.maximum(sub, m, out=sub)

def rect(mask, x0, y0, x1, y1, value=1.0, soft=1.0):
    xa, xb, ya, yb = max(0, int(x0 - soft)), min(W, int(x1 + soft) + 1), max(0, int(y0 - soft)), min(H, int(y1 + soft) + 1)
    if xb <= xa or yb <= ya: return
    X, Y = np.meshgrid(np.arange(xa, xb, dtype=np.float32), np.arange(ya, yb, dtype=np.float32))
    m = np.clip(np.minimum(np.minimum(X - x0, x1 - X), np.minimum(Y - y0, y1 - Y)) / soft + .5, 0, 1) * value
    sub = mask[ya:yb, xa:xb]; np.maximum(sub, m, out=sub)

def blur(a, s):
    F = np.fft.rfft2(a); fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.rfftfreq(W)[None, :]
    F *= np.exp(-2 * (np.pi * s) ** 2 * (fx ** 2 + fy ** 2)).astype(np.float32)
    return np.fft.irfft2(F, s=(H, W)).astype(np.float32)

def crack(mask, rng, x, y, ang, length, w, depth=0):
    seg = 22; n = max(3, int(length / seg)); cur = (x, y); pts = [cur]
    for i in range(n):
        ang += rng.uniform(-.5, .5); cur = (cur[0] + math.cos(ang) * seg, cur[1] + math.sin(ang) * seg); pts.append(cur)
        if depth < 2 and rng.random() < .2: crack(mask, rng, cur[0], cur[1], ang + rng.choice((-1, 1)) * rng.uniform(.5, 1.1), length * .5, w * .7, depth + 1)
    stroke(mask, pts, w * 1.0, 1.0, .8)

def meander(rng, pts_m, amp=.04, step=.12):
    P = np.array(pts_m, np.float32); out = []
    for a, b in zip(P, P[1:]):
        L = np.linalg.norm(b - a); n = max(1, int(L / step)); d = (b - a) / L; nrm = np.array([-d[1], d[0]])
        for k in range(n): out.append(a + (b - a) * k / n + nrm * amp * math.sin(len(out) * .9 + 1.3 + rng.uniform(0, .4)))
    out.append(P[-1]); return [px(*p) for p in out]

def generate(path_prefix, layout):
    """layout: dict(joints_x, joints_y, channels=[(x,y0,y1,w)], sumps=[(x,y,s)], drains=[(x,y,r)], flows=[pts...], puddles=[(x,y,r)], patches, scuffs, cracks, paint)"""
    from lib import write_png
    rng = np.random.default_rng(31)
    low, mid, fine = gnoise(rng, 90), gnoise(rng, 14), gnoise(rng, 2.0)
    # ---------- base concrete ----------
    base = np.array([.1, .1, .1], np.float32)
    alb = base[None, None, :] * 1.9 * (1 + .10 * low[..., None] + .05 * mid[..., None] + .035 * fine[..., None])
    # slab-to-slab tone
    xs = [-4.0] + list(layout['joints_x']) + [10.0]; ys = [0.0] + list(layout['joints_y']) + [24.0]
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            x0, y0 = px(xa, ya); x1, y1 = px(xb, yb); alb[int(y0):int(y1), int(x0):int(x1)] *= 1 + rng.uniform(-.07, .07)
    rough = np.clip(.52 + .05 * mid + .03 * low, .12, .9).astype(np.float32)
    height = (.05 * mid + .02 * fine + .04 * low).astype(np.float32)
    # polished traffic corridors (door to bay, along the channels) and general wear
    pol = np.zeros((H, W), np.float32)
    for pts in layout['lanes']: stroke(pol, [px(*p) for p in pts], 2.2 * PXM, 1.0, 40)
    pol = blur(pol, 25); rough -= .12 * np.clip(pol, 0, 1)
    # ---------- scratches (fine lines in roughness / albedo) ----------
    scr = np.zeros((H, W), np.float32)
    for _ in range(520):
        x, y = rng.uniform(0, W), rng.uniform(0, H); a = rng.uniform(0, 3.14); l = rng.uniform(.25, 1.1) * PXM
        seg_field(scr, (x, y), (x + math.cos(a) * l, y + math.sin(a) * l), 1.0, rng.uniform(.3, 1.0), .7)
    rough += .18 * scr; alb *= 1 + .06 * scr[..., None]
    # ---------- expansion joints and channel edges ----------
    J = np.zeros((H, W), np.float32)
    for xj in layout['joints_x']: stroke(J, [px(xj, 0), px(xj, 24)], 2.4, 1.0, .9)
    for yj in layout['joints_y']: stroke(J, [px(-4, yj), px(10, yj)], 2.4, 1.0, .9)
    J *= np.clip(.72 + .5 * fine, 0, 1)
    height -= 2.2 * J; alb *= (1 - .78 * J)[..., None]; rough = np.maximum(rough, .55 * J + rough * (1 - J))
    # ---------- oil, grease, rust ----------
    oil = np.zeros((H, W), np.float32)
    for (x, y, r) in layout['stains']: blob(oil, *px(x, y), r * PXM, rng, .4, 6.0)
    oil *= np.clip(.75 + .25 * mid, 0, 1)
    alb *= (1 - .45 * oil)[..., None] * (1 + .0 * oil[..., None]); alb[..., 0] += .012 * oil; rough = np.minimum(rough, rough * (1 - .6 * oil) + .12 * oil)
    rust = np.zeros((H, W), np.float32)
    for pts in layout['rust']: stroke(rust, [px(*p) for p in pts], .05 * PXM, 1.0, 6)
    rust = blur(rust, 3) * np.clip(.6 + .5 * mid, 0, 1); alb += np.stack([.06, .028, .014])[None, None, :] * rust[..., None]; rough = np.maximum(rough, .6 * rust)
    # ---------- repaired patches with sealed edges ----------
    for (x, y, w_, h_) in layout['patches']:
        P = np.zeros((H, W), np.float32); a, b = px(x - w_ / 2, y - h_ / 2); c, d = px(x + w_ / 2, y + h_ / 2); rect(P, a, b, c, d, 1.0, 1.0)
        E = np.zeros((H, W), np.float32)
        for A, B in (((a, b), (c, b)), ((c, b), (c, d)), ((c, d), (a, d)), ((a, d), (a, b))): seg_field(E, A, B, 3.0, 1.0, .8)
        alb = alb * (1 - .6 * P[..., None]) + P[..., None] * np.array([.15, .17, .20], np.float32) * (1 + .1 * mid[..., None]); rough = rough * (1 - P) + .62 * P
        alb *= (1 - .85 * E)[..., None]; height += .8 * P - 1.2 * E
    # ---------- tyre scuffs ----------
    S = np.zeros((H, W), np.float32)
    for pts in layout['scuffs']:
        pp = meander(rng, pts, .03, .3)
        for i in range(len(pp) - 1):
            if rng.random() > .12: seg_field(S, pp[i], pp[i + 1], .07 * PXM, rng.uniform(.4, 1.0), 2.5)
    S *= np.clip(.7 + .5 * mid, 0, 1); alb *= (1 - .5 * S)[..., None]; rough = np.maximum(rough, .62 * S + rough * (1 - S))
    # ---------- cracks and spalls ----------
    C = np.zeros((H, W), np.float32)
    for (x, y, a, l) in layout['cracks']: crack(C, rng, *px(x, y), a, l * PXM, 1.7)
    for _ in range(46):
        x, y = rng.choice(layout['joints_x'] + [rng.uniform(-3.8, 9.8)]) + rng.uniform(-.25, .25), rng.uniform(.3, 23.7); blob(C, *px(x, y), rng.uniform(3, 9), rng, .5, 1.2)
    height -= 3.0 * C; alb *= (1 - .88 * C)[..., None]; rough = np.maximum(rough, .85 * C + rough * (1 - C))
    # ---------- painted lane lines (worn, chipped) ----------
    gold = np.array([.34, .26, .10], np.float32)
    PA = np.zeros((H, W), np.float32)
    for (x0, y0, x1, y1) in layout['paint']: rect(PA, *px(x0, y0), *px(x1, y1), 1.0, 1.2)
    PA *= np.clip((fine + .9 * low * 0 + gnoise(rng, 5) * .8) * .6 + .85, 0, 1) * np.clip(.6 + .8 * mid, 0, 1)
    PA = np.clip(PA, 0, 1); alb = alb * (1 - PA[..., None]) + PA[..., None] * gold * (1 + .08 * mid[..., None]); rough = rough * (1 - PA) + .7 * PA
    # ---------- wetness and flow ----------
    Wm = np.zeros((H, W), np.float32); Dm = np.zeros((H, W), np.float32)
    for pts, w0, w1 in layout['flows']:
        pp = meander(rng, pts, .035, .12); n = len(pp)
        for i in range(n - 1):
            t = i / max(n - 2, 1); w = (w0 + (w1 - w0) * t) * (1 + .3 * math.sin(i * 1.7 + 2.0)) * PXM
            seg_field(Dm, pp[i], pp[i + 1], w * 2.0, .7, 5.0); seg_field(Wm, pp[i], pp[i + 1], w, 1.0, 2.5)
    for (x, y, r) in layout['puddles']:
        cx, cy = px(x, y); blob(Dm, cx, cy, r * 1.5 * PXM, rng, .3, 8.0, 1.2, .85, .7); blob(Wm, cx, cy, r * PXM, rng, .3, 3.0, 1.2, .85, 1.0)
    for (x, y, r) in layout['drains']: cx, cy = px(x, y); blob(Dm, cx, cy, (r + .5) * PXM, rng, .3, 8.0, 1, 1, .7); blob(Wm, cx, cy, (r + .22) * PXM, rng, .3, 3.0, 1, 1, .9)
    for (x, y0_, y1_, w_) in layout['channels']:
        for side in (-1, 1):
            xx = x + side * (w_ / 2 + .22)
            for (a, b) in layout['wet_runs']: seg_field(Dm, px(xx, a), px(xx, b), .14 * PXM, .6, 5.0)
    Dm = np.clip(blur(np.clip(Dm, 0, 1), 1.5), 0, 1); Wm = np.clip(blur(np.clip(Wm, 0, 1), 1.0), 0, 1)
    alb *= (1 - .22 * Dm - .38 * Wm)[..., None]
    rough = rough * (1 - .3 * Dm) + .2 * .3 * Dm; rough = rough * (1 - Wm) + .035 * Wm
    height *= (1 - .55 * np.clip(Wm + .5 * Dm, 0, 1))
    # ---------- write ----------
    alb_s = np.power(np.clip(alb, 0, 1), 1.0)                                    # already authored in sRGB-like space
    write_png(path_prefix + '_albedo.png', (alb_s * 255 + .5).astype(np.uint8))
    orm = np.stack([np.ones_like(rough), np.clip(rough, .02, 1), np.zeros_like(rough)], axis=-1)
    write_png(path_prefix + '_orm.png', (orm * 255 + .5).astype(np.uint8))
    height = blur(height, 0.9)
    k = 3.0; dhx = np.gradient(height, axis=1) * k; dhy = np.gradient(height, axis=0) * k
    n = np.stack([-dhx, -dhy, np.ones_like(dhx)], axis=-1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    write_png(path_prefix + '_normal.png', ((n * .5 + .5) * 255 + .5).astype(np.uint8))
    return dict(size=(W, H), px_per_m=PXM, wet_fraction=float((Wm > .5).mean()), damp_fraction=float((Dm > .3).mean()))
