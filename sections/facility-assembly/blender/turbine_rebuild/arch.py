"""Architecture (v3): calm colour-blocked shell with black door trims, tiled floor with a blue border, steel frame, roof, crane.
Clear shell 14 x 24 x 7.2 m (x -4..10, y 0..24)."""
import math
from mathutils import Vector

X0, X1, Y0, Y1, H = -4.0, 10.0, 0.0, 24.0, 7.2
T = 0.25                                   # wall thickness
BAYS = [2, 6, 10, 14, 18, 22]              # column / truss stations along Y
HOLE = (3.35, 5.85, 10.7, 12.2)            # U04 exhaust opening (x0,x1,y0,y1): 2.5 x 1.5 m at (4.6, 11.45)
LAMP_X, LAMP_Y = (-1.2, 4.6, 8.6), (4, 8, 12, 16, 20)

def rect_minus(r, holes):
    out = [r]
    for h in holes:
        nxt = []
        for a in out:
            if h[1] <= a[0] or h[0] >= a[1] or h[3] <= a[2] or h[2] >= a[3]: nxt.append(a); continue
            if h[0] > a[0]: nxt.append((a[0], h[0], a[2], a[3]))
            if h[1] < a[1]: nxt.append((h[1], a[1], a[2], a[3]))
            lo, hi = max(a[0], h[0]), min(a[1], h[1])
            if h[2] > a[2]: nxt.append((lo, hi, a[2], h[2]))
            if h[3] < a[3]: nxt.append((lo, hi, h[3], a[3]))
        out = nxt
    return out

def torus(b, c, R, r, sw, plane='Z', n=28):
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        p = (R * math.cos(t), R * math.sin(t), 0) if plane == 'Z' else (R * math.cos(t), 0, R * math.sin(t)) if plane == 'Y' else (0, R * math.cos(t), R * math.sin(t))
        pts.append((c[0] + p[0], c[1] + p[1], c[2] + p[2]))
    b.sweep(pts, r, sw, 10, R * .15, caps=False)

def slab(b, rects, d0, d1, sw, bev=0.0, nb=False):
    for u0, u1, z0, z1 in rects:
        if u1 - u0 < 1e-4 or z1 - z0 < 1e-4: continue
        b.box(((u0 + u1) / 2, (d0 + d1) / 2, (z0 + z1) / 2), (u1 - u0, d1 - d0, z1 - z0), sw, bev=bev, nb=nb)

def spans(u0, u1, pitch):
    n = max(1, int(round((u1 - u0) / pitch))); st = (u1 - u0) / n
    return [(u0 + i * st + .008, u0 + (i + 1) * st - .008) for i in range(n)]

def wall_specs():
    """Single source of truth for the four walls (used by the 3D structure here and by the wall skins / textures in run.py)."""
    D = lambda x0, x1, z0, z1: (x0, x1, z0, z1)
    win_e, win_w = [4, 8, 12, 16, 20], [4, 12, 20]
    return {
        'south': dict(frame=((0, 0), 0.0), u0=-4, u1=10, holes=[D(-1.2, 1.2, 0, 2.7), D(8.15, 8.65, 4.65, 5.15), D(9.35, 9.65, .3, .6)], stations=[-4, -.5, 3, 6.5, 10],
                      braces=[], feat=dict(seam_pitch=3.5, cols=[], bay_marks=[], arrows=[(4.2, .95, -1)], leaks=[(3.0, 3.8, 2.0)], floor_runs=[(-4, 10)])),
        'north': dict(frame=((0, 24), math.pi), u0=-10, u1=4, holes=[D(-1.2, 1.2, 0, 2.7), D(3.6, 4.0, 3.73, 4.03)], stations=[-10, -6.5, -3, .5, 4],
                      braces=[], feat=dict(seam_pitch=3.5, cols=[], bay_marks=[], arrows=[(-5.0, .95, 1)], leaks=[(-6.0, 3.9, 2.2)], floor_runs=[(-10, 4)])),
        'east': dict(frame=((10, 0), math.pi / 2), u0=0, u1=24, holes=[D(c - 1.3, c + 1.3, 4.55, 6.55) for c in win_e], stations=[0, 2, 6, 10, 14, 18, 22, 24], braces=[(0, 2), (22, 24)],
                     feat=dict(seam_pitch=2.0, cols=list(BAYS), bay_marks=[(y + .75, str(i + 1)) for i, y in enumerate(BAYS)], arrows=[(3.0, .95, -1), (21.0, .95, 1)],
                               leaks=[(c, 4.55, 2.6) for c in win_e], floor_runs=[(0, 24)])),
        'west': dict(frame=((-4, 24), -math.pi / 2), u0=0, u1=24, holes=[D(24 - c - 1.1, 24 - c + 1.1, 5.0, 6.4) for c in win_w], stations=[0, 2, 6, 10, 14, 18, 22, 24], braces=[(22, 24)],
                     feat=dict(seam_pitch=2.0, cols=[24 - y for y in BAYS], bay_marks=[(24 - y + .75, str(i + 1)) for i, y in enumerate(BAYS)], arrows=[(21.0, .95, 1), (3.0, .95, -1)],
                               leaks=[(24 - c, 5.0, 3.0) for c in win_w], floor_runs=[(0, 24)])),
    }

def wall(b, name, spec):
    """3D structure on a textured wall skin: occluder core, plinth, rails, cornice, bay frames and X-bracing."""
    org, rz = spec['frame']; u0, u1, holes, st = spec['u0'], spec['u1'], spec['holes'], spec['stations']
    with b.push(org, rz):
        g0 = b.group; b.use('OCC')
        slab(b, rect_minus((u0 - T, u1 + T, -0.4, H + 0.25), holes), -T, 0, 'concrete_dark')
        b.use(g0)
        for r in rect_minus((u0, u1, 0, .2), [h for h in holes if h[2] < .2]): slab(b, [r], 0.04, .105, 'concrete_dark', bev=.025)                  # chamfered plinth
        for z0, z1, d, sw, bv in ((1.20, 1.27, .075, 'pale_steel', .012), (4.45, 4.52, .07, 'slate_dark', .01)):
            for r in rect_minus((u0, u1, z0, z1), holes): slab(b, [r], 0.04, d, sw, bev=bv)                                                       # cap rail and dark course
        slab(b, [(u0, u1, H - .2, H)], 0.04, .13, 'steel_dark', bev=.02); slab(b, [(u0, u1, H - .27, H - .2)], 0.04, .16, 'steel_mid', bev=.02)   # cornice with drip lip
        for k, (a, c) in enumerate(zip(st, st[1:])):
            ia, ic = a + .24, c - .24
            if ic - ia < .8: continue
            if any(h[1] > ia and h[0] < ic and h[3] > 1.45 and h[2] < 4.35 for h in holes): continue                                                    # not across openings
            for cz in (1.5, 4.3): b.box(((ia + ic) / 2, .075, cz), (ic - ia, .05, .1), 'trim_black', bev=.015)
            for cu in (ia + .05, ic - .05): b.box((cu, .075, 2.9), (.1, .05, 2.9), 'trim_black', bev=.015)
            if (a, c) in spec['braces']:
                for (xa, za, xb, zb) in ((ia + .1, 1.6, ic - .1, 4.2), (ia + .1, 4.2, ic - .1, 1.6)): b.rod((xa, .12, za), (xb, .12, zb), .03, 'steel_mid', 10)
                b.box(((ia + ic) / 2, .13, 2.9), (.26, .03, .26), 'steel_dark', bev=.01)
                for (cu, cz) in ((ia + .12, 1.62), (ic - .12, 1.62), (ia + .12, 4.18), (ic - .12, 4.18)): b.box((cu, .12, cz), (.2, .03, .2), 'steel_dark', bev=.01)

def window(b, frame, c, half, z0, z1):
    org, rz = frame
    with b.push(org, rz):
        t = .13
        for s in (-1, 1): b.box((c + s * (half + t / 2), -.06, (z0 + z1) / 2), (t, .3, z1 - z0 + 2 * t), 'trim_black', bev=.02)
        b.box((c, -.06, z1 + t / 2), (2 * half + 2 * t, .3, t), 'trim_black', bev=.02)
        b.box((c, -.02, z0 - .03), (2 * half + .1, .4, .06), 'steel_light', bev=.015)                                   # sill
        for k in (1, 2): b.box((c - half + k * (2 * half) / 3, -.06, (z0 + z1) / 2), (.05, .1, z1 - z0), 'trim_black', bev=.008)
        b.box((c, -.06, (z0 + z1) / 2), (2 * half, .1, .04), 'trim_black', bev=.008)
        g0 = b.group; b.use('GLASS'); b.box((c, .02, (z0 + z1) / 2), (2 * half, .012, z1 - z0), 'glass'); b.use(g0)                                        # glass pane
        for s in (-1, 1): b.box((c + s * (half - .1), .075, z0 + .6), (.05, .03, .12), 'steel_mid', bev=.008)
        b.box((c, .075, (z0 + z1) / 2), (.06, .04, .16), 'brass', bev=.01)

def column(b, x, y, side):
    with b.push((x, y, 0), 0 if side < 0 else math.pi):
        b.box((.2, 0, .03), (.42, .5, .06), 'steel_dark', bev=.01)
        for dy in (-.17, .17):
            for dx in (.08, .32): b.cyl((dx, dy, .075), .026, .03, 'steel_light', 'Z', 6)
        b.box((.19, 0, H / 2), (.3, .035, H - .1), 'steel_dark', bev=.006)
        b.box((.04, 0, H / 2), (.03, .3, H - .1), 'steel_dark', bev=.006)
        b.box((.34, 0, H / 2), (.04, .3, H - .1), 'steel_mid', bev=.008)
        b.box((.355, 0, .5), (.012, .31, .22), 'yellow'); b.box((.355, 0, .75), (.012, .31, .08), 'trim_black')       # one safety band, not a barber pole
        b.box((.5, 0, 5.52), (.7, .24, .06), 'steel_light', bev=.01); b.rod((.2, 0, 5.2), (.8, 0, 5.52), .03, 'steel_dark', 8)
        b.reserve_box((.2, 0, 3.5), (.4, .5, 7))

def truss(b, y):
    x0, x1 = X0, X1; n = 8; st = (x1 - x0) / n
    b.box((3, y, 6.08), (14, .2, .16), 'steel_light', bev=.012); b.box((3, y, 7.12), (14, .2, .16), 'steel_light', bev=.012)
    for i in range(n):
        xa, xb, xc = x0 + i * st, x0 + (i + .5) * st, x0 + (i + 1) * st
        b.rod((xa, y, 7.14), (xb, y, 6.06), .07, 'pale_steel', 12); b.rod((xb, y, 6.06), (xc, y, 7.14), .07, 'pale_steel', 12)
    for i in range(n + 1): b.box((x0 + i * st, y, 6.6), (.05, .1, 1.0), 'steel_dark', bev=.005); b.box((x0 + i * st, y, 6.06), (.2, .2, .03), 'steel_light', bev=.006)
    b.box((x0 + .3, y, 6.1), (.5, .3, .04), 'steel_light', bev=.008); b.box((x1 - .3, y, 6.1), (.5, .3, .04), 'steel_light', bev=.008)

def roof(b):
    g0 = b.group; b.use('OCC'); b.box((3, 12, H + .125), (14.5, 24.5, .25), 'concrete_dark'); b.use(g0)
    ys = [0] + BAYS + [24]
    for a, c in zip(ys, ys[1:]):
        yc, w = (a + c) / 2, c - a - .25
        for i in range(14):
            x = X0 + .5 + i
            b.box((x, yc, H - .02), (.94, w, .03), 'slate_dark' if b.rng.random() > .08 else 'charcoal', nt=True, bev=.005)

def crane(b, ybridge=10.0, zr=5.55):
    for x in (-3.35, 9.35):
        b.box((x, 12, zr), (.28, 23, .05), 'steel_dark', bev=.006); b.box((x, 12, zr + .22), (.05, 23, .38), 'steel_dark'); b.box((x, 12, zr + .43), (.28, 23, .05), 'steel_dark', bev=.006)
    for yb in (ybridge - .5, ybridge + .5):
        b.box((3, yb, zr - .3), (12.7, .22, .5), 'steel_dark', bev=.012); b.box((3, yb, zr - .56), (12.7, .3, .04), 'pale_steel', bev=.006); b.box((3, yb, zr - .03), (12.7, .26, .035), 'pale_steel', bev=.006)
        for i in range(13): b.box((-3.2 + i, yb, zr - .3), (.04, .235, .5), 'steel_mid')
    for x in (-3.35, 9.35):
        b.box((x, ybridge, zr - .22), (.45, 1.5, .55), 'oxide_dark', bev=.015); b.reserve_box((x, ybridge, zr), (.5, 1.5, 1))
        for dy in (-.6, .6): b.cyl((x, ybridge + dy, zr - .22), .12, .5, 'steel_dark', 'X', 20)
    tr = 4.6
    b.box((tr, ybridge, zr - .78), (1.0, 1.3, .5), 'oxide', bev=.02); b.box((tr, ybridge, zr - .45), (1.1, 1.5, .08), 'steel_dark', bev=.01)
    b.cyl((tr, ybridge, zr - 1.1), .2, .3, 'steel_dark', 'Z', 24, bev=.008)
    for dx in (-.07, .07): b.rod((tr + dx, ybridge, zr - 1.2), (tr + dx, ybridge, zr - 2.3), .018, 'steel_mid', 10)
    b.box((tr, ybridge, zr - 2.45), (.3, .22, .26), 'oxide', bev=.015)
    b.sweep([(tr, ybridge, zr - 2.58), (tr, ybridge, zr - 2.8), (tr + .2, ybridge, zr - 2.95), (tr + .2, ybridge, zr - 3.15)], .028, 'steel_dark', 14, .12)   # hook
    b.sweep([(tr, ybridge + .65, zr - .6), (tr + .35, ybridge + 1.2, zr - 1.8), (tr + .5, ybridge + 1.4, 1.9)], .012, 'rubber', 8, .4)
    b.box((tr + .5, ybridge + 1.4, 1.75), (.14, .1, .28), 'red', bev=.012)

def door(b, frame, side_sign, label):
    """Black-trimmed portal with a rivetted bulkhead leaf parked beside it. Opening 2.4 x 2.7 m."""
    org, rz = frame
    with b.push(org, rz):
        w, h = 2.4, 2.7
        for s in (-1, 1): b.box((s * (w / 2 + .12), .1, h / 2 + .13), (.24, .2, h + .26), 'trim_black', bev=.022)
        b.box((0, .1, h + .13), (w + .48, .2, .26), 'trim_black', bev=.022)
        b.box((0, 0, -.01), (w, .3, .03), 'steel_worn', nb=True, bev=.006)
        for dx in (-.9, .9): b.flat((dx, .35), .12, .5, 'yellow', 0, z=.012)
        b.box((0, .07, h + .6), (3.7, .05, .7), 'trim_black', bev=.012); b.text(label, (.3, .1, h + .6), .26, 'chalk', math.pi, math.pi / 2)
        b.cyl((-1.62, .094, h + .6), .23, .012, 'orange_dark', 'Y', 28, bev=.004)
        if label.startswith('ELECTRICAL'): b.prism([(.0, .16), (-.07, -.02), (-.01, -.02), (-.05, -.16), (.08, .03), (.01, .03)], .006, 'trim_black', (-1.62, .104, h + .6), True, 'Y')
        else: torus(b, (-1.62, .104, h + .6), .12, .018, 'trim_black', 'Y', 24); b.cyl((-1.62, .104, h + .6), .04, .008, 'trim_black', 'Y', 16)
        lx = side_sign * (w / 2 + .2 + 1.2)
        b.box((lx, .22, h / 2), (2.4, .08, h - .08), 'steel_mid', bev=.02)
        for dx in (-.6, .6): b.box((lx + dx, .27, h / 2 - .1), (1.0, .02, h - .6), 'steel_dark', bev=.012)
        b.box((lx, .27, h - .4), (1.7, .02, .3), 'glass', bev=.008)
        for k in range(15):
            for z in (.1, h - .18): b.cyl((lx - 1.08 + k * .155, .265, z), .017, .02, 'steel_light', 'Y', 8)
        for k in range(10):
            for dx in (-1.12, 1.12): b.cyl((lx + dx, .265, .3 + k * .22), .017, .02, 'steel_light', 'Y', 8)
        for dz in (.75, 1.25): b.rod((lx - side_sign * .9, .27, dz), (lx - side_sign * .9, .32, dz), .015, 'brass', 8)
        b.rod((lx - side_sign * .9, .33, .7), (lx - side_sign * .9, .33, 1.3), .02, 'brass', 12)
        b.box((lx, .17, h + .12), (2.6, .12, .1), 'steel_dark', bev=.012)
        for k in range(3): b.box((lx + (k - 1) * .85, .17, h + .05), (.05, .12, .1), 'steel_mid')

def passage(b, frame, label):
    """1.7 m deep service passage behind a portal (the real connector is future work): dark walls, floor strip, lit end wall."""
    org, rz = frame
    with b.push(org, rz):
        w, h, d = 2.4, 2.7, 1.7
        for s in (-1, 1): b.box((s * (w / 2 + .02), -d / 2, h / 2), (.04, d, h), 'slate_dark', bev=.006)
        b.box((0, -d / 2, h + .02), (w + .08, d, .04), 'slate_dark'); b.box((0, -d / 2, -.02), (w, d, .04), 'tile_border')
        b.box((0, -d - .03, h / 2), (w, .06, h), 'slate_blue', bev=.01)
        b.box((0, -d + .02, h / 2), (1.4, .03, 2.1), 'steel_mid', bev=.02); b.box((0, -d + .005, 1.0), (.04, .02, 1.9), 'trim_black')
        for s in (-1, 1):
            b.box((s * .35, -d + .04, 1.75), (.3, .015, .45), 'glass', bev=.01); b.rod((s * .12, -d + .045, .9), (s * .12, -d + .045, 1.3), .015, 'brass', 10)
            for k in range(8): b.cyl((s * .62, -d + .04, .25 + k * .22), .014, .015, 'steel_light', 'Y', 8)
        b.box((0, -d + .02, h - .14), (w * .9, .04, .05), 'screen'); b.box((0, -.9, h - .02), (1.6, .2, .03), 'screen'); b.box((0, -d + .02, h - .3), (w * .9, .03, .04), 'red_dark')
        for k in range(8): b.box((-.9 + k * .26, -d + .06, .005), (.12, .5, .006), 'yellow' if k % 2 == 0 else 'trim_black', (0, 0, .5), nb=True)
        b.text(label, (0, -d + .045, 2.45), .27, 'chalk', math.pi, math.pi / 2)

def floor(b):
    """The floor is one slab with real holes (floormesh.py); only the exhaust pit below it is built here."""
    cx, cy, w, d = (HOLE[0] + HOLE[1]) / 2, (HOLE[2] + HOLE[3]) / 2, HOLE[1] - HOLE[0], HOLE[3] - HOLE[2]
    b.box((cx, cy, -2.5), (w, d, .1), 'black') if False else b.box((cx, cy, -2.5), (w, d, .1), 'backing')
    for dx, dy, sx, sy in ((0, d / 2, w, .05), (0, -d / 2, w, .05), (w / 2, 0, .05, d), (-w / 2, 0, .05, d)): b.box((cx + dx, cy + dy, -1.3), (sx, sy, 2.4), 'concrete_dark')

def build(b):
    b.use('ARCH'); floor(b)
    specs = wall_specs(); east, west = specs['east']['frame'], specs['west']['frame']; south, north = specs['south']['frame'], specs['north']['frame']
    win_e, win_w = [4, 8, 12, 16, 20], [4, 12, 20]
    for nm, sp in specs.items(): wall(b, nm, sp)
    for c in win_e: window(b, east, c, 1.3, 4.55, 6.55)
    for c in win_w: window(b, west, 24 - c, 1.1, 5.0, 6.4)
    door(b, south, -1, 'REACTOR  /  D01'); door(b, north, -1, 'ELECTRICAL  /  D02')
    passage(b, south, 'TO REACTOR'); passage(b, north, 'TO ELECTRICAL')
    for y in BAYS: column(b, -4, y, -1); column(b, 10, y, 1); truss(b, y)
    roof(b); crane(b)
    b.box((8.4, .03, 4.9), (.7, .08, .7), 'steel_dark', bev=.015); b.box((9.5, .03, .45), (.45, .08, .45), 'steel_dark', bev=.012)
    import floor as floor_mod; floor_mod.build(b)                                     # slabs, drainage, flow and imperfections
    b.use('ARCH')
    for y in LAMP_Y:                                                                  # hooded pendant lamps
        for x in LAMP_X:
            b.cyl((x, y, 5.45), .38, .28, 'trim_black', 'Z', 36, r2=.09, bev=.01)
            b.sphere((x, y, 5.3), .085, 'lamp', 14); b.rod((x, y, 5.59), (x, y, 6.06), .014, 'steel_dark', 10)
