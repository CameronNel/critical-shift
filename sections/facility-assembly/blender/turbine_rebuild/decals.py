"""Decal sheets for the turbine room: signs, labels, posters, gauge faces, plates and every screen are real
texture art (PIL, system python), never geometry. Two RGBA sheets are written:

  turbine_decals.png        lit decals   (painted signs, labels, posters, gauge dials)  -> alpha-blended PBR
  turbine_decals_emit.png   emissive decals (control-room screens, exit sign)           -> alpha-blended emission
  decals.json               {sheet: {name: {uv:[u0,v0,u1,v1], size:[w_m,h_m]}}}  (v measured from the bottom, like Blender)

python3 decals.py OUT_DIR
"""
import sys, os, json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = '/usr/share/fonts/truetype/liberation/'
FB, FR, FM, FMB = FD + 'LiberationSans-Bold.ttf', FD + 'LiberationSans-Regular.ttf', FD + 'LiberationMono-Regular.ttf', FD + 'LiberationMono-Bold.ttf'
FN = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
_fc = {}
def font(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]

# palette (screens are tuned for an emissive look: values are the colour the screen glows)
AMB, AMB_D, TEAL, TEAL_D, WHITE, RED, GRN = (236, 166, 66), (150, 98, 36), (92, 188, 186), (38, 78, 80), (214, 218, 212), (226, 78, 54), (72, 206, 120)
CHALK, YEL, BLK, STEEL = (232, 228, 214), (214, 170, 52), (22, 24, 27), (62, 66, 72)

class C:
    """Supersampled canvas in final-pixel units."""
    def __init__(s, wm, hm, ppm, bg=(0, 0, 0, 0), ss=3):
        s.ss, s.ppm = ss, ppm; s.W, s.H = int(round(wm * ppm)), int(round(hm * ppm)); s.wm, s.hm = wm, hm
        s.im = Image.new('RGBA', (s.W * ss, s.H * ss), bg); s.d = ImageDraw.Draw(s.im)
    def q(s, v): return v * s.ss
    def pts(s, p): return [(x * s.ss, y * s.ss) for x, y in p]
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        b = [x0 * s.ss, y0 * s.ss, x1 * s.ss, y1 * s.ss]
        if r: s.d.rounded_rectangle(b, r * s.ss, fill=fill, outline=outline, width=int(w * s.ss))
        else: s.d.rectangle(b, fill=fill, outline=outline, width=int(w * s.ss))
    def line(s, p, fill, w=1): s.d.line(s.pts(p), fill=fill, width=max(1, int(w * s.ss)), joint='curve')
    def poly(s, p, fill=None, outline=None): s.d.polygon(s.pts(p), fill=fill, outline=outline)
    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, w=1):
        ry = rx if ry is None else ry; s.d.ellipse([(cx - rx) * s.ss, (cy - ry) * s.ss, (cx + rx) * s.ss, (cy + ry) * s.ss], fill=fill, outline=outline, width=int(w * s.ss))
    def arc(s, cx, cy, r, a0, a1, fill, w=1): s.d.arc([(cx - r) * s.ss, (cy - r) * s.ss, (cx + r) * s.ss, (cy + r) * s.ss], a0, a1, fill=fill, width=max(1, int(w * s.ss)))
    def text(s, xy, t, size, fill, f=FB, anchor='la', track=0):
        fo = font(f, size * s.ss)
        if not track: s.d.text((xy[0] * s.ss, xy[1] * s.ss), t, font=fo, fill=fill, anchor=anchor); return
        tw = sum(fo.getlength(ch) for ch in t) + track * s.ss * (len(t) - 1); x = xy[0] * s.ss
        if anchor[0] == 'm': x -= tw / 2
        elif anchor[0] == 'r': x -= tw
        for ch in t: s.d.text((x, xy[1] * s.ss), ch, font=fo, fill=fill, anchor='l' + anchor[1]); x += fo.getlength(ch) + track * s.ss
    def tw(s, t, size, f=FB): return font(f, size * s.ss).getlength(t) / s.ss
    def fit(s, box, t, fill, f=FB, anchor='mm', maxsize=999, track=0):
        x0, y0, x1, y1 = box; sz = min(maxsize, (y1 - y0) * 1.0)
        while sz > 4 and s.tw(t, sz, f) + track * (len(t) - 1) > (x1 - x0): sz -= 1
        cx = (x0 + x1) / 2 if anchor[0] == 'm' else x0 if anchor[0] == 'l' else x1
        s.text((cx, (y0 + y1) / 2), t, sz, fill, f, anchor, track); return sz
    def done(s): return s.im.resize((s.W, s.H), Image.LANCZOS)

def noise(W, H, cell, rng):
    n = rng.random((max(2, H // cell + 2), max(2, W // cell + 2))).astype(np.float32)
    return np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255

def weather(im, seed, amt=.5, edge=True, streak=True, scuff=True):
    """Paint wear: soft dirt, vertical streaks, edge grime and scratches on the opaque part of a decal."""
    rng = np.random.default_rng(seed); a = np.asarray(im).astype(np.float32) / 255; H, W = a.shape[:2]
    g = 1 - amt * .45 * (noise(W, H, 40, rng) - .5) - amt * .18 * (noise(W, H, 9, rng) - .5)
    if streak:
        sx = np.asarray(Image.fromarray((rng.random((1, max(2, W // 6))) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]; g = g * (1 - amt * .5 * np.clip(sx - .5, 0, 1) * (.3 + yy))
    if edge:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); e = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)); g = g * (1 - amt * .6 * np.clip(1 - e / (min(W, H) * .06), 0, 1))
    a[..., :3] *= g[..., None]
    if scuff:
        sc = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sc)
        for _ in range(int(W * H / 9000 * amt) + 3):
            x, y = rng.random() * W, rng.random() * H; l = rng.random() * 40 + 8; t = rng.random() * 6.28
            d.line([(x, y), (x + math.cos(t) * l, y + math.sin(t) * l * .3)], fill=int(60 + rng.random() * 100), width=1)
        s2 = np.asarray(sc.filter(ImageFilter.GaussianBlur(.6))).astype(np.float32) / 255
        a[..., :3] = a[..., :3] * (1 - .25 * s2[..., None]) + .10 * s2[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')

def stripes(c, x0, y0, x1, y1, a=(214, 170, 52), b=(26, 26, 28), pitch=26, ang=1):
    c.rect(x0, y0, x1, y1, fill=b)
    k = x0 - (y1 - y0)
    while k < x1 + (y1 - y0):
        c.poly([(k, y1), (k + pitch / 2, y1), (k + pitch / 2 + (y1 - y0) * ang, y0), (k + (y1 - y0) * ang, y0)], fill=a); k += pitch
    c.rect(x0, y0 - 2, x1, y0 - 1, fill=None)

# ---------------------------------------------------------------- pictograms
def gear(c, cx, cy, r, fill, hole=None):
    for k in range(8):
        a = k * math.pi / 4; c.poly([(cx + (r * .78) * math.cos(a - .26) , cy + (r * .78) * math.sin(a - .26)), (cx + r * 1.06 * math.cos(a - .17), cy + r * 1.06 * math.sin(a - .17)),
                                     (cx + r * 1.06 * math.cos(a + .17), cy + r * 1.06 * math.sin(a + .17)), (cx + (r * .78) * math.cos(a + .26), cy + (r * .78) * math.sin(a + .26))], fill=fill)
    c.ell(cx, cy, r * .82, fill=fill); c.ell(cx, cy, r * .36, fill=hole or (0, 0, 0, 0))
def bolt(c, cx, cy, s, fill):
    c.poly([(cx + .1 * s, cy - .5 * s), (cx - .28 * s, cy + .08 * s), (cx - .02 * s, cy + .08 * s), (cx - .14 * s, cy + .5 * s), (cx + .3 * s, cy - .1 * s), (cx + .04 * s, cy - .1 * s)], fill=fill)
def warn_tri(c, cx, cy, s, fill=YEL, edge=BLK, mark='!'):
    c.poly([(cx, cy - s * .62), (cx + s * .72, cy + s * .5), (cx - s * .72, cy + s * .5)], fill=edge)
    c.poly([(cx, cy - s * .48), (cx + s * .58, cy + s * .42), (cx - s * .58, cy + s * .42)], fill=fill)
    if mark == '!': c.rect(cx - s * .035, cy - s * .2, cx + s * .035, cy + s * .12, fill=edge); c.ell(cx, cy + s * .26, s * .045, fill=edge)
    elif mark == 'bolt': bolt(c, cx, cy + s * .05, s * .62, edge)
    elif mark == 'hot':
        for k in (-1, 0, 1): c.line([(cx + k * s * .16, cy + s * .28), (cx + k * s * .16 + s * .06, cy + s * .12), (cx + k * s * .16 - s * .06, cy - s * .02), (cx + k * s * .16, cy - s * .18)], edge, s * .045)
def cross(c, cx, cy, s, fill):
    c.rect(cx - s * .11, cy - s * .34, cx + s * .11, cy + s * .34, fill=fill); c.rect(cx - s * .34, cy - s * .11, cx + s * .34, cy + s * .11, fill=fill)
def runner(c, cx, cy, s, fill):
    c.ell(cx + s * .06, cy - s * .38, s * .09, fill=fill)
    c.line([(cx + s * .02, cy - s * .26), (cx - s * .06, cy + s * .02), (cx - s * .22, cy + s * .24)], fill, s * .1); c.line([(cx - s * .06, cy + s * .02), (cx + s * .12, cy + s * .18), (cx + s * .1, cy + s * .42)], fill, s * .1)
    c.line([(cx + s * .0, cy - s * .2), (cx + s * .22, cy - s * .08), (cx + s * .3, cy - s * .2)], fill, s * .08); c.line([(cx, cy - s * .2), (cx - s * .22, cy - s * .1), (cx - s * .3, cy + s * .02)], fill, s * .08)
def arrow(c, cx, cy, s, fill, d=1):
    c.poly([(cx + d * s * .5, cy), (cx, cy - s * .38), (cx, cy - s * .16), (cx - d * s * .5, cy - s * .16), (cx - d * s * .5, cy + s * .16), (cx, cy + s * .16), (cx, cy + s * .38)], fill=fill)
def extinguisher_icon(c, cx, cy, s, fill):
    c.rect(cx - s * .14, cy - s * .12, cx + s * .14, cy + s * .42, fill=fill, r=s * .06); c.rect(cx - s * .06, cy - s * .3, cx + s * .06, cy - s * .12, fill=fill)
    c.line([(cx - s * .06, cy - s * .28), (cx - s * .22, cy - s * .32), (cx - s * .34, cy - .0 * s)], fill, s * .045); c.line([(cx + s * .06, cy - s * .3), (cx + s * .2, cy - s * .3)], fill, s * .05)
def flame(c, cx, cy, s, fill):
    c.poly([(cx, cy - s * .5), (cx + s * .18, cy - s * .15), (cx + s * .3, cy + s * .12), (cx + s * .16, cy + s * .42), (cx - s * .16, cy + s * .42), (cx - s * .3, cy + s * .12), (cx - s * .12, cy - s * .12), (cx - s * .06, cy - s * .3)], fill=fill)
def drop(c, cx, cy, s, fill):
    c.poly([(cx, cy - s * .5), (cx + s * .26, cy + s * .08), (cx + s * .2, cy + s * .3), (cx, cy + s * .42), (cx - s * .2, cy + s * .3), (cx - s * .26, cy + s * .08)], fill=fill)

# ---------------------------------------------------------------- signs
def sign(name_, wm, hm, bg, fg, lines, ppm=380, border=None, icon=None, seed=1, amt=.55, hazard=None, pad=.07, left=0.0, right=0.0, rounded=.02):
    """lines: [(text, height_frac_of_inner_h, color or None, font)]"""
    c = C(wm, hm, ppm, (0, 0, 0, 0)); W, H = c.W, c.H
    c.rect(0, 0, W, H, fill=bg, r=int(rounded * ppm))
    if border: bw = max(2, int(.018 * ppm)); c.rect(int(pad * ppm * .6), int(pad * ppm * .6), W - int(pad * ppm * .6), H - int(pad * ppm * .6), outline=border, w=bw, r=int(rounded * ppm * .6))
    ih = H - 2 * pad * ppm - (int(hazard * ppm) if hazard else 0); x0 = pad * ppm + left * ppm; x1 = W - pad * ppm - right * ppm; y = pad * ppm
    tot = sum(l[1] for l in lines)
    for t, fr, col, f in lines:
        hh = ih * fr / tot; c.fit((x0, y, x1, y + hh), t, col or fg, f, 'mm', maxsize=hh * .92); y += hh
    if hazard: stripes(c, 0, H - int(hazard * ppm), W, H, pitch=int(.11 * ppm))
    if icon: icon(c, W, H)
    return weather(c.done(), seed, amt)

def paper(wm, hm, ppm=300, seed=1, kind='memo', title='', tint=(226, 222, 206), rng=None):
    c = C(wm, hm, ppm, tint + (255,)); W, H = c.W, c.H; r = random.Random(seed)
    c.rect(0, 0, W, int(.12 * H), fill=(max(tint[0] - 90, 0), max(tint[1] - 80, 0), max(tint[2] - 70, 0))) if kind != 'blank' else None
    if title: c.text((W * .06, H * .06), title, H * .075, (240, 236, 224), FB, 'lm')
    yy = H * (.2 if kind != 'blank' else .08)
    if kind == 'table':
        for i in range(9):
            c.line([(W * .06, yy), (W * .94, yy)], (120, 116, 106), 1)
            for j in range(4): c.rect(W * (.1 + j * .22), yy + 3, W * (.1 + j * .22 + r.uniform(.06, .17)), yy + 8, fill=(70, 70, 76))
            yy += H * .09
    else:
        while yy < H * .92:
            ln = r.uniform(.45, .88) if r.random() > .15 else .3
            c.rect(W * .08, yy, W * (.08 + ln * .84), yy + max(2, H * .018), fill=(66, 66, 72)); yy += H * .055
    return weather(c.done(), seed, .35, True, False, False)

def gauge_face(name_, ang, ppm=900, r=.095, red_from=.72, label='BAR', seed=0, lo=0, hi=100):
    d = r * 2.0; c = C(d, d, ppm); R = c.W / 2
    c.ell(R, R, R * .995, fill=(238, 234, 220, 255)); c.ell(R, R, R * .93, fill=(244, 240, 228, 255), outline=(24, 24, 24, 255), w=max(1, R * .018))
    a0, a1 = 135, 405
    c.arc(R, R, R * .78, a0 + (a1 - a0) * red_from, a1, (200, 50, 36, 255), R * .09)
    c.arc(R, R, R * .78, a0 + (a1 - a0) * .45, a0 + (a1 - a0) * red_from, (210, 164, 50, 255), R * .09)
    n = 10
    for k in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * k / n); cs, sn = math.cos(t), math.sin(t); L = .17 if k % 5 == 0 else .1
        c.line([(R + cs * R * .66, R + sn * R * .66), (R + cs * R * (.66 - L), R + sn * R * (.66 - L))], (24, 24, 24, 255), R * (.034 if k % 5 == 0 else .018))
        if k % 2 == 0 and not (a0 + (a1 - a0) * k / n) % 360 in (): c.text((R + cs * R * .44, R + sn * R * .44), str(int(lo + (hi - lo) * k / n)), R * .14, (30, 30, 30, 255), FB, 'mm')
    c.text((R, R * 1.5), label, R * .15, (40, 40, 40, 255), FB, 'mm')
    t = math.radians(a0 + (a1 - a0) * ang); cs, sn = math.cos(t), math.sin(t)
    c.poly([(R + cs * R * .72, R + sn * R * .72), (R - sn * R * .035, R + cs * R * .035), (R - cs * R * .2, R - sn * R * .2), (R + sn * R * .035, R - cs * R * .035)], fill=(190, 30, 22, 255))
    c.ell(R, R, R * .07, fill=(30, 30, 32, 255)); c.ell(R - R * .02, R - R * .02, R * .03, fill=(120, 120, 124, 255))
    im = c.done(); a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]].astype(np.float32); rr = np.hypot(xx - R, yy - R) / R
    a[..., :3] *= (1 - .18 * np.clip(rr - .55, 0, 1) ** 2 * 2)[..., None]; a[..., :3] *= (1 - .1 * (yy / im.size[1]))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

# ---------------------------------------------------------------- screens (emissive sheet)
def screen_bg(c, seed=1, grid=True, tint=(10, 18, 19)):
    W, H = c.W, c.H; c.rect(0, 0, W, H, fill=tint + (255,))
    if grid:
        for x in range(0, W, max(8, W // 28)): c.line([(x, 0), (x, H)], (18, 34, 35, 255), .7)
        for y in range(0, H, max(8, W // 28)): c.line([(0, y), (W, y)], (18, 34, 35, 255), .7)

def scanlines(im, amt=.10):
    a = np.asarray(im).astype(np.float32); H = a.shape[0]; a[..., :3] *= (1 - amt * (np.arange(H) % 3 == 0))[:, None, None]
    yy, xx = np.mgrid[0:H, 0:a.shape[1]].astype(np.float32); v = np.hypot((xx / a.shape[1] - .5) * 1.1, (yy / H - .5) * 1.4)
    a[..., :3] *= (1 - .35 * np.clip(v - .35, 0, 1))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

# hall plan geometry (world metres): plan is drawn "heads-up" for an operator facing the west wall: up = west (-x), right = north (+y)
HALL = (-4.0, 10.0, 0.0, 24.0)
def mimic(ppm=620, fault=False):
    W_M, H_M = 2.44, 1.26; c = C(W_M, H_M, ppm); W, H = c.W, c.H; screen_bg(c, 3)
    # title bar
    c.rect(0, 0, W, 64, fill=(16, 32, 33, 255)); c.line([(0, 64), (W, 64)], AMB + (255,), 2)
    c.text((22, 32), 'HALL PLAN  -  TURBINE T-2', 34, AMB + (255,), FB, 'lm', track=2)
    c.text((W * .64, 32), 'UNIT 2 ONLINE', 26, GRN + (255,), FB, 'lm'); c.ell(W * .64 - 22, 32, 8, fill=GRN + (255,))
    c.text((W - 22, 32), '02:47:13  27/09', 26, TEAL + (255,), FMB, 'rm')
    # plan area
    px0, py0, px1, py1 = 30, 92, int(W * .625), H - 86
    sc = min((px1 - px0) / 24.0, (py1 - py0) / 14.0); ox = px0 + ((px1 - px0) - 24 * sc) / 2; oy = py0 + ((py1 - py0) - 14 * sc) / 2
    def P(x, y): return (ox + y * sc, oy + (x + 4) * sc)               # up = west, right = north
    def box(x0, y0, x1, y1, fill=None, out=None, w=2, r=0):
        a, b = P(x0, y0), P(x1, y1); c.rect(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), fill=fill, outline=out, w=w, r=r)
    def ln(pts, col, w=2, dash=0):
        pp = [P(*p) for p in pts]
        if not dash: c.line(pp, col, w); return
        for (a, b) in zip(pp, pp[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L / dash)
            for i in range(0, n, 2): c.line([(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n), (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)], col, w)
    box(-4, 0, 10, 24, fill=(14, 26, 27, 255), out=AMB + (255,), w=4)                                      # hall walls
    for (x0, x1) in ((-4, 10),):
        pass
    for yz, nm in ((0, 'Z1'), (6, 'Z2'), (12, 'Z3'), (18, 'Z4')):                                         # zone bands
        a = P(-4, yz); c.line([(a[0], P(-4, 0)[1]), (a[0], P(10, 0)[1])], TEAL_D + (255,), 1.5) if yz else None
    zones = ((0, 6, 'ZONE 1  INLET'), (6, 12.5, 'ZONE 2  TURBINE'), (12.5, 17.5, 'ZONE 3  COUPLING'), (17.5, 24, 'ZONE 4  GENERATOR'))
    for y0, y1, nm in zones:
        a = P(9.6, y0 + .25); c.text((a[0] + 4, a[1]), nm, 14, TEAL + (255,), FB, 'lm')
    for y in (6, 12.5, 17.5):
        ln([(-4, y), (10, y)], TEAL_D + (255,), 1.5, 14)
    box(2.0, 2.6, 7.2, 23.0, fill=(20, 38, 39, 255), out=TEAL_D + (255,), w=2)                           # foundation
    box(7.0, 0, 7.55, 1.6, fill=None)                                                                    # (spacing)
    ln([(4.6, 3.0), (4.6, 22.9)], TEAL + (255,), 3)                                                       # shaft
    for (y0, y1, hw) in ((3.2, 4.3, .66), (4.3, 5.7, .8), (5.7, 7.0, .95), (8.1, 9.2, 1.0), (9.2, 13.3, .55), (13.3, 14.4, 1.2), (15.9, 21.3, 1.05), (21.3, 22.3, .7)):
        box(4.6 - hw, y0, 4.6 + hw, y1, fill=(32, 64, 66, 255), out=AMB + (255,), w=2)
    box(3.6, 17.0, 5.6, 21.0, fill=None, out=AMB + (255,), w=2)
    for y in (7.4, 14.9): box(4.0, y, 5.2, y + .5, fill=(60, 36, 14, 255), out=AMB + (255,), w=2)         # bearings / coupling
    ln([(8.4, 0), (8.4, 4.0), (4.8, 4.0)], AMB + (255,), 4)                                                # main steam
    for (a, b_) in (((8.4, 2.0), (8.4, 2.0)),): pass
    c.ell(*P(8.4, 2.0), 7, fill=AMB + (255,))                                                              # stop valve
    ln([(-1.45, 20.0), (-3.8, 20.0), (-3.8, 24.0)], TEAL + (255,), 3)                                       # HV bus duct
    box(-3.4, 22.8, -.8, 24, fill=(20, 38, 39, 255), out=TEAL_D + (255,), w=2)                               # protection cubicles
    box(-3.9, 2.4, -2.5, 5.6, fill=(20, 38, 39, 255), out=TEAL + (255,), w=2)                                # control consoles
    box(-1.4, 14.1, -.4, 19.9, fill=None, out=TEAL + (255,), w=2)                                            # lay-down rotor
    ln([(-1.0, 14.3), (-1.0, 19.7)], TEAL + (255,), 3)
    ln([(0, 0), (0, 24)], TEAL_D + (255,), 1.5, 8)                                                         # crane rail
    for (x0, x1, y, lab) in ((-1.5, 1.5, 0, 'D01'), (-1.5, 1.5, 24, 'D02')):
        box(x0, y - .5, x1, y + .5, fill=(10, 18, 19, 255), out=GRN + (255,), w=3)
        a = P((x0 + x1) / 2, y); c.text((a[0] + (28 if y == 0 else -28), a[1] + 2), lab, 15, GRN + (255,), FB, 'mm')
    box(8.5, 22.9, 9.8, 23.9, fill=(40, 32, 22, 255), out=AMB_D + (255,), w=2)                               # drum store
    for tx, ty, t in ((4.6, 5.3, 'HP'), (4.6, 11.2, 'LP'), (4.6, 18.9, 'GEN'), (-2.95, 4.0, 'CTRL'), (-1.9, 17.0, 'ROTOR LAY-DOWN'), (9.2, 23.4, 'FUEL')):
        a = P(tx, ty); c.text(a, t, 18, WHITE + (255,), FB, 'mm')
    a = P(10.0, 12.0); c.text((a[0], a[1] + 22), 'EAST WALL', 13, TEAL_D + (255,), FB, 'mm')
    a = P(-4.0, 12.0); c.text((a[0], a[1] - 18), 'MIMIC  WALL', 13, TEAL_D + (255,), FB, 'mm')
    # right: status panel
    rx0 = int(W * .655); rx1 = W - 24
    c.rect(rx0, 84, rx1, H - 86, fill=(13, 26, 27, 255), outline=TEAL_D + (255,), w=2)
    c.text((rx0 + 16, 108), 'PLANT STATUS', 22, AMB + (255,), FB, 'lm', track=2); c.line([(rx0 + 16, 128), (rx1 - 16, 128)], TEAL_D + (255,), 1.5)
    rows = (('STEAM PRESS', '84', 'bar', .84, TEAL), ('STEAM TEMP', '512', 'C', .74, TEAL), ('ROTOR SPEED', '3000', 'rpm', 1.0, GRN), ('GEN LOAD', '62', 'MW', .62, TEAL), ('VIBRATION', '1.2', 'mm/s', .22, GRN), ('COOLING FLOW', '41', '%', .41, AMB))
    yy = 156
    for lab, val, un, fr, col in rows:
        c.text((rx0 + 18, yy), lab, 17, WHITE + (255,), FB, 'lm'); c.text((rx1 - 74, yy), val, 26, col + (255,), FMB, 'rm'); c.text((rx1 - 20, yy + 2), un, 14, TEAL + (255,), FB, 'rm')
        c.rect(rx0 + 18, yy + 16, rx1 - 18, yy + 25, fill=(24, 44, 45, 255)); c.rect(rx0 + 18, yy + 16, rx0 + 18 + (rx1 - rx0 - 36) * fr, yy + 25, fill=col + (255,)); yy += 52
    c.line([(rx0 + 16, yy - 6), (rx1 - 16, yy - 6)], TEAL_D + (255,), 1.5)
    c.text((rx0 + 16, yy + 16), 'ALARMS', 22, AMB + (255,), FB, 'lm', track=2); yy += 38
    for t, m, col in (('02:41', 'GEN COOLING FLOW LOW', AMB), ('02:39', 'BRG 3 TEMP HIGH', AMB), ('02:12', 'TRIP RESET OK', TEAL)):
        c.text((rx0 + 18, yy), t, 15, col + (255,), FMB, 'lm'); c.text((rx0 + 84, yy), m, 15, col + (255,), FB, 'lm'); yy += 26
    # bottom navigation + trend
    by = H - 70
    c.line([(0, by - 12), (W, by - 12)], TEAL_D + (255,), 1.5)
    for i, (t, on) in enumerate((('OVERVIEW', True), ('STEAM', False), ('GENERATOR', False), ('ELECTRICAL', False), ('ALARMS', False), ('TRENDS', False))):
        x0 = 30 + i * 176; c.rect(x0, by, x0 + 164, by + 50, fill=(AMB_D + (255,)) if on else (16, 32, 33, 255), outline=(AMB if on else TEAL_D) + (255,), w=2, r=6)
        c.text((x0 + 82, by + 25), t, 20, (WHITE if on else TEAL) + (255,), FB, 'mm', track=1)
    tx0, tx1 = 30 + 6 * 176 + 12, W - 24; c.rect(tx0, by, tx1, by + 50, fill=(10, 20, 21, 255), outline=TEAL_D + (255,), w=2)
    pts = [(tx0 + 8 + i * (tx1 - tx0 - 16) / 40, by + 28 + 12 * math.sin(i * .45) - 6 * math.sin(i * 1.3 + 1)) for i in range(41)]; c.line(pts, TEAL + (255,), 2)
    return scanlines(c.done())

def mimic_fault(ppm=620):
    """Alarm overlay for zone 3: emissive amber on transparent; runtime flickers this quad's emission."""
    W_M, H_M = 2.44, 1.26; full = C(W_M, H_M, ppm); W, H = full.W, full.H
    px0, py0, px1, py1 = 30, 92, int(W * .625), H - 86
    sc = min((px1 - px0) / 24.0, (py1 - py0) / 14.0); ox = px0 + ((px1 - px0) - 24 * sc) / 2; oy = py0 + ((py1 - py0) - 14 * sc) / 2
    def P(x, y): return (ox + y * sc, oy + (x + 4) * sc)
    x0, y0 = P(-4, 17.5); x1, y1 = P(10, 24)
    c = full
    c.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill=(236, 110, 40, 16), outline=(255, 130, 44, 255), w=3)
    gx, gy = P(4.6, 19.3)
    c.poly([(gx, gy - 40), (gx + 38, gy + 26), (gx - 38, gy + 26)], fill=(255, 140, 40, 255), outline=(255, 190, 90, 255))
    c.rect(gx - 4, gy - 16, gx + 4, gy + 6, fill=(30, 12, 6, 255)); c.ell(gx, gy + 16, 4.5, fill=(30, 12, 6, 255))
    bx0, by0 = int(W * .655), H - 86 - 54
    c.rect(bx0, by0, W - 24, H - 90, fill=(120, 40, 18, 230), outline=(255, 150, 60, 255), w=3, r=6)
    c.text(((bx0 + W - 24) / 2, by0 + 27), 'FAULT: ZONE 3  -  GEN COOLING', 21, (255, 214, 150, 255), FB, 'mm')
    im = scanlines(c.done(), .08); a = np.asarray(im).copy(); return Image.fromarray(a, 'RGBA')

def monitor(kind, ppm=1100):
    c = C(.35, .22, ppm); W, H = c.W, c.H; screen_bg(c, 1, True, (8, 16, 17))
    c.rect(0, 0, W, 40, fill=(18, 36, 37, 255)); c.line([(0, 40), (W, 40)], AMB + (255,), 2)
    spec = {'press': ('STEAM PRESS', '84', 'bar', TEAL, .84), 'temp': ('STEAM TEMP', '512', 'deg C', AMB, .74), 'rpm': ('ROTOR SPEED', '3000', 'rpm', GRN, 1.0),
            'load': ('GEN LOAD', '62', 'MW', TEAL, .62), 'trip': ('TRIP STATUS', 'OK', 'ARMED', GRN, 0), 'vib': ('VIBRATION', 'LOW', '1.2 mm/s', GRN, .2)}[kind]
    c.text((14, 20), spec[0], 22, AMB + (255,), FB, 'lm', track=1); c.ell(W - 24, 20, 6, fill=GRN + (255,))
    c.text((W / 2, H * .46), spec[1], 98 if len(spec[1]) < 4 else 80, spec[3] + (255,), FMB, 'mm'); c.text((W / 2, H * .72), spec[2], 24, WHITE + (255,), FB, 'mm', track=2)
    if spec[4]:
        c.rect(24, H - 44, W - 24, H - 30, fill=(24, 44, 45, 255), outline=TEAL_D + (255,), w=1); c.rect(24, H - 44, 24 + (W - 48) * spec[4], H - 30, fill=spec[3] + (255,))
        for k in range(1, 10): c.line([(24 + (W - 48) * k / 10, H - 44), (24 + (W - 48) * k / 10, H - 30)], (8, 16, 17, 255), 1)
    else:
        pts = [(24 + i * (W - 48) / 60, H - 36 + 8 * math.sin(i * .6) * (1 if kind == 'vib' else 0)) for i in range(61)]; c.line(pts, spec[3] + (255,), 2)
    return scanlines(c.done(), .12)

def desk_monitor(ppm=800):
    c = C(.46, .26, ppm); W, H = c.W, c.H; screen_bg(c, 4, True, (9, 17, 18))
    c.rect(0, 0, W, 34, fill=(18, 36, 37, 255)); c.text((12, 17), 'TURBINE 02  -  LOG', 20, AMB + (255,), FB, 'lm')
    for i in range(7):
        y = 56 + i * 34; c.text((14, y), '02:%02d' % (41 - i * 3), 16, TEAL + (255,), FMB, 'lm'); c.rect(86, y - 6, 86 + 120 + (i * 53) % 130, y + 6, fill=(60, 122, 124, 255) if i % 3 else AMB_D + (255,))
    pts = [(W * .62 + i * (W * .34) / 30, H * .6 + 30 * math.sin(i * .5) - 12 * math.sin(i * 1.7)) for i in range(31)]; c.line(pts, AMB + (255,), 2)
    c.rect(W * .6, 52, W - 14, H - 24, outline=TEAL_D + (255,), w=1)
    return scanlines(c.done(), .1)

def exit_sign(ppm=560):
    c = C(.54, .17, ppm, (6, 40, 24, 255)); W, H = c.W, c.H
    c.rect(4, 4, W - 4, H - 4, outline=(72, 206, 120, 255), w=3, r=6)
    runner(c, W * .17, H * .5, H * .78, (130, 255, 170, 255)); c.fit((W * .30, H * .12, W * .80, H * .88), 'EXIT', (150, 255, 185, 255), FB, 'mm', track=6)
    arrow(c, W * .89, H * .5, H * .6, (130, 255, 170, 255)); return c.done()

# ---------------------------------------------------------------- catalogue
def build_lit(add):
    S = sign
    add('sign_turbine_control', 3.08, .5, S('x', 3.08, .5, (34, 38, 44, 255), CHALK, [('TURBINE CONTROL', 1.0, None, FB)], 340, border=(150, 124, 56, 255), hazard=0.045, pad=.06, seed=3))
    add('sign_hv_bus', 2.3, .46, S('x', 2.3, .46, (222, 178, 46, 255), BLK, [('HV BUS  /  U03', 1.0, None, FB)], 340, border=BLK + (255,), seed=4, hazard=.04))
    def gear_icon(c, W, H): gear(c, H * .5 + 10, H * .5, H * .3, YEL + (255,), (30, 32, 36, 255))
    add('sign_maint_bay', 3.1, .56, S('x', 3.1, .56, (30, 34, 40, 255), CHALK, [('MAINTENANCE BAY', 1.0, None, FB)], 320, border=(150, 124, 56, 255), icon=gear_icon, left=.5, pad=.06, seed=5))
    add('sign_exhaust', .9, .22, S('x', .9, .22, YEL + (255,), BLK, [('EXHAUST  U04', 1.0, None, FB)], 380, seed=6, pad=.035))
    add('sign_hall', 1.8, .5, S('x', 1.8, .5, (28, 32, 38, 255), CHALK, [('TURBINE HALL', 1.0, None, FB)], 360, border=(150, 124, 56, 255), left=0, right=.42, pad=.07, seed=7,
        icon=lambda c, W, H: arrow(c, W - H * .75, H * .5, H * .62, YEL + (255,))))
    add('sign_hall02', 1.8, .62, S('x', 1.8, .62, (28, 32, 38, 255), CHALK, [('TURBINE HALL 02', 1.0, None, FB), ('AUTHORISED PERSONNEL ONLY', .5, (230, 184, 60, 255), FB)], 360, border=(150, 124, 56, 255), hazard=.04, pad=.07, seed=8))
    add('sign_desk', .82, .42, S('x', .82, .42, (214, 172, 52, 255), BLK, [('TURBINE 02', 1.0, None, FB), ('CONTROL DESK', .62, None, FB)], 380, border=BLK + (255,), seed=9, pad=.04))
    add('nameplate_gen', 1.4, .38, S('x', 1.4, .38, (36, 24, 20, 255), CHALK, [('GENERATOR  G-2', 1.0, None, FB), ('24 kV  /  3 PHASE  /  50 Hz', .52, (212, 176, 100, 255), FM), ('SER. NO.  GT-2-0419', .4, (150, 140, 124, 255), FM)], 360, border=(150, 100, 70, 255), seed=10, pad=.045))
    add('tag_lp', .94, .28, S('x', .94, .28, (36, 24, 20, 255), CHALK, [('LP TURBINE  2', 1.0, None, FB), ('ROTOR  3000 RPM', .62, (212, 176, 100, 255), FB)], 380, border=(150, 100, 70, 255), seed=11, pad=.03))
    add('plate_main_steam', .74, .14, S('x', .74, .14, (18, 20, 22, 255), CHALK, [('MAIN STEAM  T-2', 1.0, None, FB)], 460, seed=12, pad=.012))
    add('label_tg3', .5, .26, S('x', .5, .26, (232, 228, 214, 255), BLK, [('TG-3', 1.0, None, FB)], 420, seed=13, pad=.03))
    add('label_gen3', .5, .26, S('x', .5, .26, (232, 228, 214, 255), BLK, [('GEN-3', 1.0, None, FB)], 420, seed=14, pad=.03))
    add('label_hose', .5, .3, S('x', .5, .3, (232, 228, 214, 255), BLK, [('HOSE', 1.0, None, FB)], 420, seed=15, pad=.03))
    add('plate_hv', .7, .5, S('x', .7, .5, (214, 172, 52, 255), BLK, [('HV', 1.0, None, FB)], 380, seed=16, pad=.07, icon=lambda c, W, H: warn_tri(c, W * .5, H * .5, H * .0)))
    for k, (t, s2) in enumerate((('PROT A', 'DIFF. RELAY'), ('PROT B', 'EARTH FAULT'), ('EXCITER', 'AVR  /  FIELD'))):
        add('plate_prot%d' % k, .62, .5, S('x', .62, .5, (228, 224, 210, 255), BLK, [(t, 1.0, None, FB), (s2, .42, (80, 80, 84, 255), FM)], 380, seed=17 + k, pad=.05, border=(40, 40, 44, 255)))
    for k, t in enumerate(('UNIT 1  STEAM', 'UNIT 2  GOVERNOR', 'UNIT 3  TRIP')):
        add('label_unit%d' % k, .62, .1, S('x', .62, .1, (24, 26, 30, 255), CHALK, [(t, 1.0, None, FB)], 520, border=(120, 100, 56, 255), seed=20 + k, pad=.014, amt=.4))
    for k, (t, s2) in enumerate((('02', ''), ('04', ''), ('06', ''), ('08', ''), ('10', ''), ('12', ''))):
        c = C(.36, .36, 300); c.fit((10, 10, c.W - 10, c.H - 10), t, (210, 206, 192, 255), FB, 'mm'); add('num_%s' % t, .36, .36, weather(c.done(), 30 + k, .6, False, True, True))
    # hazard / warning plates
    def hz(mark):
        c = C(.4, .4, 360, (22, 24, 27, 255)); W = c.W; warn_tri(c, W / 2, W * .52, W * .88, YEL + (255,), BLK + (255,), mark); c.rect(2, 2, W - 2, W - 2, outline=(70, 72, 78, 255), w=3, r=6); return weather(c.done(), 40 + len(mark), .5)
    add('hazard_bolt', .4, .4, hz('bolt')); add('hazard_warn', .4, .4, hz('!')); add('hazard_hot', .4, .4, hz('hot'))
    c = C(.5, .5, 360, (210, 60, 44, 255)); W = c.W; c.rect(10, 10, W - 10, W - 10, outline=(240, 236, 224, 255), w=5, r=8); extinguisher_icon(c, W / 2, W * .5, W * .6, (240, 236, 224, 255)); add('sign_ext', .5, .5, weather(c.done(), 50, .5))
    c = C(.5, .5, 360, (30, 120, 98, 255)); W = c.W; c.rect(10, 10, W - 10, W - 10, outline=(240, 236, 224, 255), w=5, r=8); cross(c, W / 2, W * .5, W * .72, (240, 236, 224, 255)); add('sign_firstaid', .5, .5, weather(c.done(), 51, .5))
    c = C(.5, .5, 360, (30, 120, 98, 255)); W = c.W; c.rect(10, 10, W - 10, W - 10, outline=(240, 236, 224, 255), w=5, r=8); c.ell(W / 2, W * .42, W * .17, fill=(240, 236, 224, 255)); c.ell(W / 2, W * .42, W * .07, fill=(30, 120, 98, 255))
    drop(c, W * .5, W * .72, W * .18, (240, 236, 224, 255)); add('sign_eyewash', .5, .5, weather(c.done(), 52, .5))
    c = C(.4, .4, 360, (30, 120, 98, 255)); W = c.W; c.rect(8, 8, W - 8, W - 8, outline=(240, 236, 224, 255), w=4, r=6); cross(c, W / 2, W / 2, W * .7, (240, 236, 224, 255)); add('firstaid_box', .4, .4, weather(c.done(), 53, .5))
    c = C(.42, .5, 360, (214, 172, 52, 255)); W, H = c.W, c.H; c.rect(8, 8, W - 8, H - 8, outline=BLK + (255,), w=5, r=6); flame(c, W / 2, H * .32, H * .3, (200, 56, 40, 255))
    c.fit((W * .08, H * .55, W * .92, H * .72), 'FLAMMABLE', BLK + (255,), FB, 'mm'); c.fit((W * .08, H * .73, W * .92, H * .88), 'LIQUIDS STORE', BLK + (255,), FB, 'mm'); add('sign_flammable', .42, .5, weather(c.done(), 54, .5))
    add('label_eyewash', .3, .12, S('x', .3, .12, (232, 228, 214, 255), (30, 110, 90, 255), [('EYEWASH', 1.0, None, FB)], 520, seed=55, pad=.014))
    # extinguisher body label (wraps the red cylinder): cream label with pictograms
    c = C(.17, .3, 520, (236, 232, 218, 255)); W, H = c.W, c.H; c.rect(0, 0, W, int(H * .13), fill=(200, 50, 40, 255)); c.text((W / 2, H * .065), 'CO2', H * .09, (250, 244, 232, 255), FB, 'mm')
    extinguisher_icon(c, W * .3, H * .3, H * .2, (30, 30, 32, 255)); flame(c, W * .68, H * .3, H * .16, (200, 50, 40, 255))
    for i, t in enumerate(('1  PULL PIN', '2  AIM NOZZLE', '3  SQUEEZE', '4  SWEEP')): c.text((W * .1, H * (.5 + i * .07)), t, H * .043, (30, 30, 32, 255), FB, 'lm')
    c.text((W / 2, H * .88), '5 kg  /  CLASS B  E', H * .04, (80, 80, 84, 255), FB, 'mm'); add('ext_label', .17, .3, weather(c.done(), 56, .4))
    # posters
    c = C(.54, .78, 360, (30, 46, 72, 255)); W, H = c.W, c.H; c.rect(10, 10, W - 10, H - 10, outline=(232, 145, 58, 255), w=5)
    warn_tri(c, W / 2, H * .3, W * .6, (232, 145, 58, 255), (30, 46, 72, 255), 'hot'); c.fit((W * .1, H * .54, W * .9, H * .68), 'STEAM', (240, 236, 224, 255), FB, 'mm'); c.fit((W * .1, H * .68, W * .9, H * .76), 'ISOLATE FIRST', (232, 145, 58, 255), FB, 'mm')
    c.fit((W * .12, H * .80, W * .88, H * .86), 'LOCK  -  TAG  -  TEST', (200, 204, 210, 255), FB, 'mm'); c.line([(W * .12, H * .78), (W * .88, H * .78)], (232, 145, 58, 255), 2); add('poster_0', .54, .78, weather(c.done(), 60, .5))
    c = C(.54, .78, 360, (240, 201, 90, 255)); W, H = c.W, c.H; c.rect(10, 10, W - 10, H - 10, outline=BLK + (255,), w=5)
    c.ell(W / 2, H * .3, W * .24, fill=BLK + (255,)); c.rect(W * .38, H * .24, W * .62, H * .36, fill=(240, 201, 90, 255)); c.ell(W / 2, H * .3, W * .17, fill=(240, 201, 90, 255)); c.rect(W * .46, H * .22, W * .54, H * .38, fill=BLK + (255,)); c.rect(W * .4, H * .28, W * .6, H * .32, fill=BLK + (255,))
    c.fit((W * .1, H * .54, W * .9, H * .67), 'MIND YOUR', BLK + (255,), FB, 'mm'); c.fit((W * .1, H * .67, W * .9, H * .8), 'HEAD', (200, 50, 40, 255), FB, 'mm'); c.fit((W * .12, H * .83, W * .88, H * .89), 'LOW PIPEWORK AHEAD', BLK + (255,), FB, 'mm'); add('poster_1', .54, .78, weather(c.done(), 61, .5))
    # notice board
    add('notice_header', 1.0, .14, S('x', 1.0, .14, (30, 70, 58, 255), CHALK, [('TURBINE LOG', 1.0, None, FB)], 420, seed=62, pad=.02))
    add('notice_a', .3, .42, paper(.3, .42, 340, 70, 'memo', 'SHIFT NOTES')); add('notice_b', .32, .46, paper(.32, .46, 340, 71, 'table', 'READINGS')); add('notice_c', .3, .38, paper(.3, .38, 340, 72, 'memo', 'ROTA', (240, 214, 120)))
    add('notice_d', .24, .16, paper(.24, .16, 340, 73, 'blank')); add('notice_e', .26, .16, paper(.26, .16, 340, 74, 'memo', 'PERMIT'))
    # evacuation plan
    c = C(.74, .52, 400, (236, 232, 218, 255)); W, H = c.W, c.H; c.rect(0, 0, W, int(H * .14), fill=(30, 120, 98, 255)); c.text((W * .04, H * .07), 'EVACUATION PLAN  -  TURBINE HALL', H * .075, (245, 242, 232, 255), FB, 'lm')
    mx0, my0, mx1, my1 = W * .05, H * .2, W * .7, H * .94; c.rect(mx0, my0, mx1, my1, fill=(250, 248, 240, 255), outline=(60, 60, 64, 255), w=3)
    c.rect(mx0 + (mx1 - mx0) * .32, my0 + (my1 - my0) * .16, mx0 + (mx1 - mx0) * .7, my0 + (my1 - my0) * .84, fill=(210, 206, 196, 255), outline=(120, 118, 112, 255), w=2)
    c.line([(mx0 + (mx1 - mx0) * .85, my1 - 8), (mx0 + (mx1 - mx0) * .85, my0 + (my1 - my0) * .5), (mx0 + 8, my0 + (my1 - my0) * .5)], GRN + (255,), 5)
    c.ell(mx0 + (mx1 - mx0) * .85, my1 - 14, 7, fill=(210, 60, 44, 255)); c.text((mx0 + (mx1 - mx0) * .85 + 12, my1 - 22), 'YOU ARE HERE', H * .045, (200, 50, 40, 255), FB, 'lm')
    lx = W * .74
    for i, (col, t) in enumerate(((GRN, 'ESCAPE ROUTE'), ((200, 50, 40), 'EXTINGUISHER'), ((30, 120, 98), 'FIRST AID'), ((214, 172, 52), 'ASSEMBLY'))):
        c.rect(lx, H * (.26 + i * .1), lx + H * .05, H * (.26 + i * .1) + H * .05, fill=col + (255,)); c.text((lx + H * .075, H * (.285 + i * .1)), t, H * .042, (40, 40, 44, 255), FB, 'lm')
    add('evac_plan', .74, .52, weather(c.done(), 63, .4))
    # DB board label + drain label + clock
    add('label_db04', .5, .09, S('x', .5, .09, (230, 226, 212, 255), BLK, [('DB-04', 1.0, None, FB)], 520, seed=64, pad=.01))
    c = C(.5, .1, 520, (0, 0, 0, 0)); c.fit((4, 4, c.W - 4, c.H - 4), 'DRAIN', (150, 152, 156, 255), FB, 'mm', track=12); add('drain', .5, .1, weather(c.done(), 65, .5, False, False, True))
    c = C(.4, .4, 500); R = c.W / 2; c.ell(R, R, R * .99, fill=(24, 26, 29, 255)); c.ell(R, R, R * .88, fill=(240, 236, 224, 255))
    for k in range(60):
        t = math.radians(k * 6 - 90); L = .13 if k % 5 == 0 else .05; c.line([(R + math.cos(t) * R * .83, R + math.sin(t) * R * .83), (R + math.cos(t) * R * (.83 - L), R + math.sin(t) * R * (.83 - L))], (30, 30, 30, 255), R * (.03 if k % 5 == 0 else .012))
    for k in range(1, 13): t = math.radians(k * 30 - 90); c.text((R + math.cos(t) * R * .6, R + math.sin(t) * R * .6), str(k), R * .17, (30, 30, 30, 255), FB, 'mm')
    c.line([(R, R), (R + math.cos(math.radians(-90 + 5 * 6 + 2)) * R * .6, R + math.sin(math.radians(-90 + 5 * 6 + 2)) * R * .6)], (30, 30, 30, 255), R * .035); c.line([(R, R), (R + math.cos(math.radians(-90 + 120 + 12)) * R * .4, R + math.sin(math.radians(-90 + 120 + 12)) * R * .4)], (30, 30, 30, 255), R * .05)
    c.line([(R, R), (R + math.cos(math.radians(-90 + 200)) * R * .7, R + math.sin(math.radians(-90 + 200)) * R * .7)], (190, 40, 30, 255), R * .014); c.ell(R, R, R * .05, fill=(30, 30, 30, 255)); add('clock_face', .4, .4, c.done())
    # crate / box stencils
    c = C(.5, .34, 360, (0, 0, 0, 0)); W, H = c.W, c.H; c.fit((W * .05, H * .08, W * .95, H * .42), 'FRAGILE', (30, 28, 24, 255), FB, 'mm', track=6)
    c.fit((W * .05, H * .46, W * .6, H * .62), 'THIS WAY UP', (30, 28, 24, 255), FB, 'lm'); arrow(c, W * .82, H * .62, H * .3, (30, 28, 24, 255)); c.im = c.im.rotate(0); add('stencil_fragile', .5, .34, weather(c.done(), 66, .5, False, False, True))
    c = C(.3, .12, 400, (232, 228, 214, 255)); W, H = c.W, c.H; c.rect(0, 0, W * .5, H, fill=(190, 50, 40, 255)); c.text((W * .25, H * .5), 'SPARES', H * .24, (245, 240, 230, 255), FB, 'mm'); c.text((W * .76, H * .3), 'T2-HP-0417', H * .18, BLK + (255,), FM, 'mm'); c.text((W * .76, H * .66), 'QTY 12', H * .18, BLK + (255,), FMB, 'mm'); add('label_ship', .3, .12, weather(c.done(), 67, .4))
    c = C(.5, .2, 360, (0, 0, 0, 0)); c.fit((4, 4, c.W - 4, c.H - 4), 'LP-2  ROTOR', (230, 226, 210, 255), FB, 'mm', track=4); add('stencil_rotor', .5, .2, weather(c.done(), 68, .5, False, False, True))
    # gauge dials
    add('gauge_a', .19, .19, gauge_face('a', .62, label='BAR')); add('gauge_b', .19, .19, gauge_face('b', .38, label='C', hi=600)); add('gauge_c', .19, .19, gauge_face('c', .78, label='MPa', hi=10, red_from=.8)); add('gauge_d', .19, .19, gauge_face('d', .2, label='RPM x100', hi=40))

    def door_icon(kind):
        def f(c, W, H):
            cx, cy = H * .55, H * .5; c.ell(cx, cy, H * .34, fill=(214, 120, 40, 255)); c.ell(cx, cy, H * .28, fill=(24, 26, 30, 255))
            if kind == 'bolt': bolt(c, cx, cy, H * .46, (230, 170, 60, 255))
            else:
                c.ell(cx, cy, H * .15, outline=(230, 170, 60, 255), w=H * .045); c.ell(cx, cy, H * .04, fill=(230, 170, 60, 255))
        return f
    add('door_reactor', 3.7, .7, S('x', 3.7, .7, (24, 27, 31, 255), CHALK, [('REACTOR  /  D01', 1.0, None, FB)], 300, border=(150, 124, 56, 255), icon=door_icon('r'), left=.62, right=.2, pad=.07, seed=80))
    add('door_electrical', 3.7, .7, S('x', 3.7, .7, (24, 27, 31, 255), CHALK, [('ELECTRICAL  /  D02', 1.0, None, FB)], 300, border=(150, 124, 56, 255), icon=door_icon('bolt'), left=.62, right=.2, pad=.07, seed=81))
    for nm, t in (('pass_reactor', 'TO REACTOR'), ('pass_electrical', 'TO ELECTRICAL')):
        c = C(1.9, .36, 300); c.fit((6, 6, c.W - 6, c.H - 6), t, (232, 228, 214, 255), FB, 'mm', track=6); add(nm, 1.9, .36, weather(c.done(), 82, .35, False, False, True))
    # pump / cylinder / tool tags
    add('label_gas_o2', .24, .12, S('x', .24, .12, (230, 226, 212, 255), (30, 90, 160, 255), [('OXYGEN', 1.0, None, FB)], 500, seed=69, pad=.012))
    add('label_gas_ac', .24, .12, S('x', .24, .12, (230, 226, 212, 255), (150, 40, 34, 255), [('ACETYLENE', 1.0, None, FB)], 500, seed=70, pad=.012))
    add('label_trolley', .3, .06, S('x', .3, .06, (24, 26, 30, 255), CHALK, [('TOOLS  -  BAY 2', 1.0, None, FB)], 520, seed=71, pad=.008, amt=.3))


def console_panel(k, ppm=520):
    """Printed bezel for the sloped console panel (0.84 across x 0.56 up the slope). Control positions match machinery.controls()."""
    c = C(.84, .56, ppm, (24, 27, 31, 255)); W, H = c.W, c.H; S = .576
    def P(dy, t): return (W / 2 + dy * ppm, H / 2 - (t - .5) * S * ppm)
    c.rect(3, 3, W - 3, H - 3, outline=(90, 96, 104, 255), w=2, r=8)
    for sx in (14, W - 14):
        for sy in (14, H - 14): c.ell(sx, sy, 4, fill=(70, 74, 80, 255)); c.line([(sx - 3, sy), (sx + 3, sy)], (30, 30, 34, 255), 1)
    col = (214, 216, 208, 255); dim = (150, 154, 150, 255); amb = (214, 170, 70, 255)
    def lab(dy, t, tx, sz=12, f=FB, fill=col): c.text(P(dy, t), tx, sz, fill, f, 'mm')
    def grp(d0, d1, t0, t1, title):
        a, b2 = P(d0, t1), P(d1, t0); c.rect(a[0], a[1], b2[0], b2[1], outline=(104, 110, 116, 255), w=1.5, r=4); c.text((a[0] + 6, a[1] - 0), title, 11, amb, FB, 'lm')
    if k == 0:
        c.text((16, 22), 'UNIT 1  -  STEAM ADMISSION', 15, amb, FB, 'lm', track=1)
        grp(-.39, .02, .06, .31, 'STATUS'); grp(-.37, -.04, .4, .68, 'STOP VALVE'); grp(.14, .41, .52, .88, 'GOVERNOR')
        for i, t in enumerate(('RUN', 'LOW P', 'TRIP', 'READY', 'AUX', 'TEST')): lab(-.32 + i * .128, .12, t, 11)
        for i, t in enumerate(('OPEN', 'HOLD', 'CLOSE')): lab(-.3 + i * .1, .46, t, 11)
        lab(.2, .8, 'STOP', 11); lab(.34, .8, 'GOV', 11)
        pts = [P(-.1, .62), P(.15, .62)]
        for pa, pb in ((P(-.32, .62), P(-.2, .62)), (P(-.1, .62), P(-.03, .62)),):
            c.line([pa, pb], dim, 2)
        c.rect(P(-.34, .66)[0], P(-.34, .66)[1], P(-.27, .58)[0], P(-.27, .58)[1], outline=dim, w=2); lab(-.305, .62, 'HP', 10)
        c.poly([P(-.03, .64), P(.04, .66), P(.04, .58), P(-.03, .60)], fill=None, outline=dim)
    elif k == 1:
        c.text((16, 22), 'UNIT 2  -  GOVERNOR / AUX', 15, amb, FB, 'lm', track=1)
        grp(-.41, .41, .16, .44, 'AUXILIARY DRIVES'); grp(-.35, -.07, .56, .86, 'SPEED SET'); grp(.07, .35, .56, .86, 'LOAD SET')
        for i, t in enumerate(('BFP1', 'BFP2', 'CWP', 'LOP', 'JOP', 'TG', 'VAC', 'AUX')): lab(-.35 + i * .1, .2, t, 11)
        lab(-.22, .76, 'RAISE / LOWER', 10, FB, dim); lab(.22, .76, 'RAISE / LOWER', 10, FB, dim)
    else:
        c.text((16, 22), 'UNIT 3  -  PROTECTION / TRIP', 15, amb, FB, 'lm', track=1)
        grp(-.41, -.12, .1, .5, 'EMERGENCY'); grp(-.1, .41, .38, .7, 'RESET / ACK'); grp(-.0, .41, .62, .86, 'TRIP STATUS')
        lab(-.28, .15, 'TRIP', 12, FB, (226, 90, 70, 255))
        for i, t in enumerate(('', 'RESET', 'ACK', 'LAMP', 'HORN')):
            if t: lab(-.28 + i * .13 - .13 + .13, .42, t, 10) if False else None
        for i, t in enumerate(('RESET', 'ACK', 'LAMP', 'HORN')): lab(-.28 + i * .13 + 0.0, .43, t, 10)
    return c.done()

def toolboard(ppm=330):
    """painted shadow board: pegboard with white tool outlines (3D tools hang inside the outlines) and a label strip"""
    c = C(2.9, 1.0, ppm, (34, 44, 58, 255)); W, H = c.W, c.H
    for gx in range(14, W, 18):
        for gy in range(14, H, 18): c.ell(gx, gy, 2.2, fill=(16, 22, 30, 255))
    lw = (214, 216, 208, 255)
    def X(u): return W / 2 + u * ppm
    def Y(v): return H / 2 - v * ppm
    c.rect(X(-1.4), Y(.46), X(-.2), Y(.38), fill=(24, 26, 30, 255)); c.text((X(-.8), Y(.42)), 'BAY 2  -  SPANNERS / DRIVERS', 13, lw, FB, 'mm', track=2)
    for i in range(6):
        u = -1.2 + .22 * i; L = .4 - .025 * i; c.rect(X(u - .02), Y(.36), X(u + .02), Y(.36 - L), outline=lw, w=1.5, r=3); c.ell(X(u), Y(.36 - L + .03), .045 * ppm * .85, outline=lw, w=1.5)
    for i in range(6):
        u = -1.2 + .2 * i; c.rect(X(u - .02), Y(-.1), X(u + .02), Y(-.4), outline=lw, w=1.5, r=4)
    c.rect(X(.1), Y(.32), X(.14), Y(.0), outline=lw, w=1.5); c.rect(X(.04), Y(.02), X(.2), Y(-.05), outline=lw, w=1.5)
    c.rect(X(.36), Y(.3), X(.4), Y(.0), outline=lw, w=1.5); c.rect(X(.3), Y(.03), X(.46), Y(-.07), outline=lw, w=1.5)
    c.line([(X(.65), Y(.3)), (X(.62), Y(.02)), (X(.7), Y(.02)), (X(.67), Y(.3))], lw, 1.5); c.line([(X(.8), Y(.3)), (X(.83), Y(.02)), (X(.75), Y(.02)), (X(.78), Y(.3))], lw, 1.5)
    for u in (1.0, 1.2, 1.4): c.ell(X(u), Y(.15), .07 * ppm, outline=lw, w=1.5)
    c.rect(X(-1.45), Y(-.47), X(1.45), Y(-.5), fill=(214, 170, 52, 255))
    return weather(c.done(), 90, .35, True, False, True)

def keyboard(ppm=600):
    c = C(.34, .12, ppm, (30, 32, 35, 255)); W, H = c.W, c.H; r = random.Random(5)
    for row in range(5):
        n = 14 if row < 4 else 1; x = W * .03
        for k in range(n):
            kw = (W * .94 / 14 - 3) if row < 4 else W * .5
            if row == 4: x = W * .25
            c.rect(x, H * .08 + row * H * .17, x + kw, H * .08 + row * H * .17 + H * .14, fill=(52, 55, 60, 255), r=3); x += kw + 3
    return c.done()

def build_emit(add):
    add('mimic_main', 2.44, 1.26, mimic())
    add('mimic_fault', 2.44, 1.26, mimic_fault())
    for k in ('press', 'temp', 'rpm', 'load', 'trip', 'vib'): add('mon_' + k, .35, .22, monitor(k))
    add('desk_monitor', .46, .26, desk_monitor())
    add('exit_sign', .54, .17, exit_sign())

# ---------------------------------------------------------------- packing
def pack(items, width, pad=6):
    """shelf packer: items = [(name, img)] -> (sheet, {name: (x0, y0, x1, y1)})"""
    items = sorted(items, key=lambda t: -t[1].size[1]); x = y = row = 0; place = {}
    for n, im in items:
        w, h = im.size
        if x + w + pad > width: x, y, row = 0, y + row + pad, 0
        place[n] = (x, y); x += w + pad; row = max(row, h)
    H = 1
    while H < y + row + pad: H *= 2
    sheet = Image.new('RGBA', (width, H), (0, 0, 0, 0))
    for n, im in items: sheet.paste(im, place[n])
    return sheet, {n: (place[n][0], place[n][1], place[n][0] + im.size[0], place[n][1] + im.size[1]) for n, im in items}

def generate(out):
    os.makedirs(out, exist_ok=True); meta = {}
    for sheet_name, builder, width in (('turbine_decals', build_lit, 2048), ('turbine_decals_emit', build_emit, 2048)):
        items, sizes = [], {}
        def add(name, w, h, im): items.append((name, im)); sizes[name] = (w, h)
        builder(add)
        if sheet_name == 'turbine_decals':
            add('keyboard', .34, .12, keyboard())
            for k in range(3): add('panel_u%d' % k, .84, .56, console_panel(k))
            add('toolboard', 2.9, 1.0, toolboard())
        sheet, place = pack(items, width); sheet.save(os.path.join(out, sheet_name + '.png'))
        W, H = sheet.size
        meta[sheet_name] = {n: dict(uv=[x0 / W, 1 - y1 / H, x1 / W, 1 - y0 / H], size=list(sizes[n])) for n, (x0, y0, x1, y1) in place.items()}
        print(sheet_name, sheet.size, len(place))
    json.dump(meta, open(os.path.join(out, 'decals.json'), 'w'), indent=1)

if __name__ == '__main__': generate(sys.argv[1])
