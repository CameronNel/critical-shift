"""Floor (v6): polished concrete slabs that fall toward grated drainage channels, round drains and sumps, wet films and rivulets that
flow to them, plus the imperfections a working hall collects (cracks, spalls, repairs, tyre scuffs, worn paint, patched joints)."""
import math, random
from mathutils import Vector
from arch import HOLE, torus, rect_minus

CH_X = (1.45, 7.62)            # linear drainage channels along the foundation (west / east)
CH_Y0, CH_Y1, CH_W = 2.5, 22.9, .32
SUMPS = [(1.45, 23.5), (7.62, 23.5)]
DRAINS = [(-1.05, 8.55), (0.9, 3.2), (8.0, 1.7), (-2.8, 12.4), (-1.0, 22.2)]
SLOPE = .004

def blob(b, x, y, r, sw, z, rng, irr=.2, sx=1.0, sy=1.0, rot=0.0):
    n = 16; ph = [rng.uniform(0, 6.28) for _ in range(3)]; c, s = math.cos(rot), math.sin(rot); ring = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + irr * (math.sin(2 * a + ph[0]) * .5 + math.sin(3 * a + ph[1]) * .3 + math.sin(5 * a + ph[2]) * .2)
        px, py = r * k * math.cos(a) * sx, r * k * math.sin(a) * sy
        ring.append((px * c - py * s, px * s + py * c))
    b.prism(ring, .003, sw, (x, y, z), True, 'Z')

def ribbon(b, pts, w0, w1, sw, z, rng, meander=.05, step=.14, gaps=0.0):
    """Wet trail along a polyline: meanders, width varies, optional broken segments."""
    P = [Vector((p[0], p[1], 0)) for p in pts]; dense = []
    for A, B in zip(P, P[1:]):
        L = (B - A).length; n = max(1, int(L / step))
        for k in range(n): dense.append(A + (B - A) * (k / n))
    dense.append(P[-1])
    N = len(dense); left, right = [], []
    for i, p in enumerate(dense):
        t = i / max(N - 1, 1); d = (dense[min(i + 1, N - 1)] - dense[max(i - 1, 0)]).normalized(); nrm = Vector((-d.y, d.x, 0))
        off = meander * math.sin(i * .9 + 1.3) * (1 if meander else 0)
        w = (w0 + (w1 - w0) * t) * (1 + .3 * math.sin(i * 1.7 + 2.0)) * .5
        c = p + nrm * off
        left.append(c + nrm * w); right.append(c - nrm * w)
    for i in range(N - 1):
        if gaps and rng.random() < gaps: continue
        b.poly([(left[i].x, left[i].y, z), (right[i].x, right[i].y, z), (right[i + 1].x, right[i + 1].y, z), (left[i + 1].x, left[i + 1].y, z)], sw, hint=(0, 0, 1), fit=False)

def flow(b, pts, w0, w1, rng, **kw):
    """Damp halo + wet core, ending in a small pool."""
    ribbon(b, pts, w0 * 1.9, w1 * 1.9, 'damp', .0087, rng, **kw); ribbon(b, pts, w0, w1, 'wet', .0096, rng, **kw)
    ex, ey = pts[-1]; blob(b, ex, ey, w1 * .9, 'wet', .0096, rng, .25)

def crack(b, x, y, ang, length, w, rng, depth=0):
    seg = .22; n = max(2, int(length / seg)); px, py = x, y
    for i in range(n):
        ang += rng.uniform(-.45, .45); dx, dy = math.cos(ang) * seg, math.sin(ang) * seg
        ww = w * (1 - .5 * i / n)
        b.box((px + dx / 2, py + dy / 2, .0078), (seg * 1.08, ww, .002), 'crack', (0, 0, ang))
        if depth < 2 and rng.random() < .22: crack(b, px + dx, py + dy, ang + rng.choice((-1, 1)) * rng.uniform(.5, 1.1), length * .45, w * .7, rng, depth + 1)
        px, py = px + dx, py + dy

def grate_channel(b, x, y0, y1, w, rng):
    L = y1 - y0; ym = (y0 + y1) / 2
    b.box((x, ym, -.013), (w, L, .002), 'backing')                                   # dark sump under the bars
    for s in (-1, 1): b.box((x + s * (w / 2 + .022), ym, .0035), (.044, L, .015), 'steel_dark', bev=.006)   # angle-iron curbs
    n = int(L / .6); st = L / n
    for k in range(n):
        yc = y0 + (k + .5) * st
        for e in (-1, 1): b.box((x, yc + e * (st / 2 - .008), .005), (w, .016, .018), 'steel_mid')
        m = int((st - .05) / .052)
        for i in range(m):
            sw = 'steel_worn' if rng.random() < .1 else 'steel_dark'
            b.box((x, yc - (st - .06) / 2 + i * (st - .06) / (m - 1), .002), (w - .012, .02, .02), sw)
        for s in (-.09, .09): b.box((x + s, yc, -.006), (.012, st - .02, .012), 'steel_dark')       # support bars
        for e in (-1, 1): b.cyl((x + e * (w / 2 - .035), yc, .011), .014, .006, 'steel_light', 'Z', 6)    # bolts

def sump(b, x, y, s=.9):
    b.box((x, y, .0035), (s + .12, s + .12, .014), 'steel_dark', bev=.008); b.box((x, y, -.01), (s, s, .003), 'backing')
    for i in range(10): b.box((x, y - s / 2 + .05 + i * (s - .1) / 9, .004), (s - .04, .028, .022), 'steel_mid')
    for sx in (-1, 1): b.box((x + sx * (s / 2 - .03), y, .008), (.03, s - .02, .012), 'steel_dark', bev=.004)
    for sx in (-1, 1):
        for sy in (-1, 1): b.cyl((x + sx * (s / 2 + .01), y + sy * (s / 2 + .01), .013), .018, .008, 'steel_light', 'Z', 8)

def round_drain(b, x, y, r=.2):
    b.cyl((x, y, .004), r + .05, .014, 'steel_dark', 'Z', 36, bev=.006); b.cyl((x, y, .0115), r, .005, 'backing', 'Z', 32)
    for k in range(6): b.box((x, y, .0135), (r * 1.7, .022, .012), 'steel_mid', (0, 0, k * math.pi / 6), bev=.004)
    torus(b, (x, y, .0145), r * .55, .009, 'steel_mid', 'Z', 20); b.cyl((x, y, .0145), .035, .012, 'steel_light', 'Z', 14, bev=.004)

def build(b):
    b.use('ARCH'); R = random.Random(21)
    # ---- slabs: fall toward the channels, tiny height and tilt differences so the polished surface breaks up reflections ----
    xcols = [(-4.0, -1.33), (-1.33, CH_X[0] - CH_W / 2 - .02), (CH_X[1] + CH_W / 2 + .02, 10.0)]
    ybs = [24 * k / 7 for k in range(8)]
    for (xa, xb) in xcols:
        for ya, yb in zip(ybs, ybs[1:]):
            x, y = (xa + xb) / 2, (ya + yb) / 2
            tilt = SLOPE if x < CH_X[0] else -SLOPE
            traffic = abs(x) < 2.4 and (y < 3.6 or y > 20.4)
            roll = R.random()
            sw = 'terra_worn' if roll < (.3 if traffic else .06) else 'terra_b' if roll < .35 else 'terra_c' if roll < .62 else 'terra_a'
            b.box((x, y, -.015 + R.uniform(-.002, .002)), (xb - xa - .016, yb - ya - .016, .03), sw, (R.uniform(-.0015, .0015), tilt + R.uniform(-.0012, .0012), 0), nb=True, bev=.004)
    # sealed expansion joints
    for xj in (-1.33,): b.box((xj, 12, -.012), (.014, 24, .004), 'sealant')
    for yj in ybs[1:-1]:
        for xa, xb in xcols: b.box(((xa + xb) / 2, yj, -.012), (xb - xa, .014, .004), 'sealant')
    # ---- drainage: two grated channels, sumps, round drains, a manhole ----
    for xc in CH_X: grate_channel(b, xc, CH_Y0, CH_Y1, CH_W, R)
    for sx, sy in SUMPS: sump(b, sx, sy)
    for dx, dy in DRAINS: round_drain(b, dx, dy)
    b.cyl((-2.1, 10.2, .004), .36, .012, 'steel_dark', 'Z', 40, bev=.006); torus(b, (-2.1, 10.2, .012), .27, .012, 'trim_black', 'Z', 28)
    for k in range(2): b.box((-2.1 + (-.12 if k == 0 else .12), 10.2, .012), (.1, .03, .008), 'backing')
    b.text('DRAIN', (-2.1, 10.2, .0125), .075, 'steel_light', 0, 0)
    # ---- flow: water leaves the machinery and runs to the drains and channels ----
    flow(b, [(-.35, 9.15), (-.55, 8.9), (-.85, 8.65), (-1.05, 8.55)], .22, .12, R, meander=.03)
    blob(b, -.35, 9.2, .5, 'damp', .0087, R, .3, 1.2, .9, .4); blob(b, -.38, 9.18, .34, 'wet', .0096, R, .3, 1.15, .85, .4)
    flow(b, [(8.18, 8.7), (8.0, 8.9), (7.84, 9.15), (7.7, 9.35)], .13, .08, R, meander=.04)
    flow(b, [(8.2, 15.3), (8.0, 15.6), (7.86, 15.9), (7.7, 16.0)], .12, .07, R)
    flow(b, [(8.15, 17.9), (7.95, 18.2), (7.78, 18.3)], .1, .06, R)
    flow(b, [(7.0, .7), (7.15, 1.4), (7.35, 2.0), (7.55, 2.7)], .13, .09, R, meander=.05)                               # hose reel drip
    flow(b, [(8.7, 21.9), (8.4, 22.3), (8.0, 22.9), (7.7, 23.3)], .16, .1, R, meander=.05)                              # drum spill
    flow(b, [(1.0, 3.3), (.95, 3.25)], .3, .22, R)
    for xc, side in ((CH_X[0], 1), (CH_X[1], -1)):                                                                       # wet film beside the channels
        ribbon(b, [(xc + side * .3, CH_Y0 + .3), (xc + side * .3, CH_Y1 - .3)], .1, .12, 'damp', .0088, R, meander=.02, gaps=.28)
    ribbon(b, [(1.95, 6.0), (1.92, 12.5), (1.95, 20.5)], .06, .08, 'wet', .0096, R, meander=.015, gaps=.45)
    blob(b, 0.9, 3.4, .55, 'damp', .0087, R, .3, 1.3, .9); blob(b, 0.9, 3.3, .35, 'wet', .0096, R, .3, 1.3, .9)           # standing water at the low points
    blob(b, 8.0, 1.9, .5, 'damp', .0087, R, .3); blob(b, 8.02, 1.85, .32, 'wet', .0096, R, .3)
    blob(b, -2.8, 12.5, .45, 'damp', .0087, R, .3); blob(b, -2.8, 12.45, .28, 'wet', .0096, R, .3)
    blob(b, -1.0, 22.3, .5, 'damp', .0087, R, .3); blob(b, -1.0, 22.25, .3, 'wet', .0096, R, .3)
    for (px, py, rr) in ((-.2, 5.5, .35), (-2.5, 6.0, .3), (.4, 15.0, .32)): blob(b, px, py, rr * 1.3, 'damp', .0087, R, .3); blob(b, px, py, rr, 'wet', .0096, R, .3)
    for yy in (4.6, 6.4, 9.6, 12.0, 14.4, 17.0, 19.6, 21.2):                                                            # sheet flow across the slabs into the west channel
        x0 = R.uniform(-.9, .1); flow(b, [(x0, yy), (x0 + .7, yy + R.uniform(-.25, .25)), (1.12, yy + R.uniform(-.3, .3)), (1.27, yy + R.uniform(-.2, .2))], .05, .1, R, meander=.03)
    # ---- imperfections ----
    for (cx_, cy_, a_, l_) in ((-3.1, 2.0, .7, 3.2), (-.9, 6.1, 1.9, 2.8), (.7, 19.0, -.5, 3.0), (9.1, 11.0, 1.4, 2.6), (-2.0, 20.0, .3, 2.4), (8.8, 2.3, 2.6, 2.0), (-3.3, 15.0, 1.2, 1.8)):
        crack(b, cx_, cy_, a_, l_, .008, R)
    for i in range(18):                                                                                                  # spalls and chips along joints
        x, y = R.choice((-1.33, 7.9, 9.4, -2.7)) + R.uniform(-.3, .3), R.uniform(.5, 23.5)
        if 1.7 < x < 7.4 and 2.3 < y < 23.2: continue
        blob(b, x, y, R.uniform(.03, .08), 'crack', .0082, R, .45)
    for (px, py, w_, h_) in ((-3.0, 10.6, 1.2, .8), (9.15, 3.0, .9, .7), (.45, 6.7, .8, .6), (-2.6, 1.1, .9, .6)):         # repaired patches with sealed edges
        b.box((px, py, .0075), (w_, h_, .004), 'patch', (0, 0, R.uniform(-.05, .05)), nb=True)
        for s in (-1, 1):
            b.box((px + s * w_ / 2, py, .0085), (.012, h_ + .012, .003), 'sealant'); b.box((px, py + s * h_ / 2, .0085), (w_, .012, .003), 'sealant')
    for off in (-.28, .28):                                                                                              # tyre scuffs from D01 to the bay
        ribbon(b, [(.3 + off, 1.2), (.1 + off, 4.0), (-.5 + off, 8.0), (-.9 + off, 11.5)], .07, .06, 'floor_grime', .0086, R, meander=.025, step=.3, gaps=.12)
    for (px, py) in ((-3.2, 6.8), (6.4, 21.2), (-.4, 12.8)): blob(b, px, py, .22, 'floor_grime', .0088, R, .35); blob(b, px, py, .11, 'floor_grime', .0089, R, .3)
    for xl in (1.0, 7.98):                                                                                               # worn gold lane paint with chipped breaks
        y = 3.0
        while y < 22.4:
            ln = R.uniform(.7, 1.6); gap = R.choice((.0, .08, .22, .35)); b.flat((xl, y + ln / 2), .09, ln, 'gold_paint', 0, z=.0079); y += ln + gap
    for xl in (1.45 - .0, 7.62):                                                                                         # channel stencil
        b.text('DRAIN', (xl + (-.34 if xl < 4 else .34), 5.0, .0092), .09, 'gold_paint', math.pi / 2, 0)
