"""Architecture: floor, walls, columns, roof, trusses, doors, crane. Clear shell 14 x 24 x 7.2 m (x -4..10, y 0..24)."""
import math
from mathutils import Vector

X0, X1, Y0, Y1, H = -4.0, 10.0, 0.0, 24.0, 7.2
T = 0.25                                   # wall thickness
BAYS = [2, 6, 10, 14, 18, 22]              # column / truss stations along Y
HOLE = (3.35, 5.85, 10.7, 12.2)            # U04 exhaust opening (x0,x1,y0,y1): 2.5 x 1.5 m at (4.6, 11.45)

def rect_minus(r, holes):
    """r=(u0,u1,z0,z1); holes list of same -> list of remaining rects."""
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

def slab(b, rects, d0, d1, sw, nb=False):
    for u0, u1, z0, z1 in rects:
        if u1 - u0 < 1e-4 or z1 - z0 < 1e-4: continue
        b.box(((u0 + u1) / 2, (d0 + d1) / 2, (z0 + z1) / 2), (u1 - u0, d1 - d0, z1 - z0), sw)

def wall(b, frame, u0, u1, holes, windows=()):
    """Build one wall in its local frame: local x along wall, local y into room, z up."""
    org, rz = frame
    with b.push(org, rz):
        # structural core (outside, thickness T)
        g0 = b.group; b.use('OCC')
        slab(b, rect_minus((u0 - T, u1 + T, -0.4, H + 0.25), holes), -T, 0, 'concrete_dark')
        b.use(g0)
        slab(b, rect_minus((u0, u1, 0, H), holes), 0, .002, 'backing')                # visible only through panel seams
        # skirt / wainscot / rail / upper panels (inside skin)
        for (z0, z1, d, sw, w) in ((0, .22, .06, 'charcoal', 1.2), (.22, 1.30, .04, 'wainscot', 1.17), (1.30, 1.40, .07, 'steel_mid', 2.0),
                                   (1.40, 3.10, .03, 'ivory', 1.9), (3.50, 4.45, .03, 'ivory_warm', 1.9), (4.45, H, .03, 'ivory', 1.9)):
            n = max(1, int(round((u1 - u0) / w))); step = (u1 - u0) / n
            for i in range(n):
                a, c = u0 + i * step + .01, u0 + (i + 1) * step - .01
                sws = sw
                if sw == 'ivory' and b.rng.random() < .22: sws = 'ivory_dirty'
                if sw == 'wainscot' and b.rng.random() < .14: sws = 'wainscot_blue'
                for r in rect_minus((a, c, z0, z1), holes):
                    slab(b, [r], 0, d, sws)
        # colour-block stripes (orange band + yellow marking line)
        for r in rect_minus((u0, u1, 3.10, 3.50), holes): slab(b, [r], 0, .045, 'orange')
        for r in rect_minus((u0, u1, 4.45, 4.51), holes): slab(b, [r], 0, .05, 'steel_mid')
        for r in rect_minus((u0, u1, 1.40, 1.46), holes): slab(b, [r], .07, .075, 'chalk') if False else None

def windows(b, frame, centres, half, z0=4.55, z1=6.55):
    org, rz = frame
    with b.push(org, rz):
        for c in centres:
            slab(b, [(c - half - .1, c - half, z0 - .1, z1 + .1), (c + half, c + half + .1, z0 - .1, z1 + .1)], -T, .06, 'steel_dark')      # jambs
            slab(b, [(c - half, c + half, z0 - .12, z0)], -T, .12, 'steel_light')                                                       # deep sill
            slab(b, [(c - half, c + half, z1, z1 + .1)], -T, .06, 'steel_dark')
            for k in range(1, 3):                                                                                                         # mullions
                x = c - half + k * (2 * half) / 3
                b.box((x, -0.06, (z0 + z1) / 2), (.06, .1, z1 - z0), 'steel_dark')
            b.box((c, -0.06, (z0 + z1) / 2), (2 * half, .1, .05), 'steel_dark')

def column(b, x, y, side):
    """I-section pilaster on a long wall. side=-1 west wall, +1 east wall."""
    with b.push((x, y, 0), 0 if side < 0 else math.pi):
        # local +x points into the room for the west column; for east we rotated 180 about the column
        b.box((.2, 0, .03), (.4, .5, .06), 'steel_dark')                                           # base plate
        b.box((.19, 0, H / 2), (.3, .035, H - .1), 'steel_dark')                                   # web
        b.box((.04, 0, H / 2), (.03, .3, H - .1), 'steel_dark')                                    # wall-side flange
        b.box((.34, 0, H / 2), (.035, .3, H - .1), 'steel_mid')                                    # inner flange
        for k in range(6):                                                                         # safety banding to 1.0 m
            b.box((.355, 0, .08 + k * .16), (.012, .31, .15), 'yellow' if k % 2 == 0 else 'charcoal')
        b.box((.5, 0, 5.52), (.7, .24, .06), 'steel_light'); b.rod((.2, 0, 5.2), (.8, 0, 5.52), .03, 'steel_dark', 4)   # crane bracket + strut
        b.reserve_box((.2, 0, 3.5), (.4, .5, 7))

def truss(b, y):
    x0, x1 = X0, X1
    b.box(((x0 + x1) / 2, y, 6.06), (14, .14, .12), 'steel_mid')
    b.box(((x0 + x1) / 2, y, 7.14), (14, .14, .12), 'steel_mid')
    n = 8; step = (x1 - x0) / n
    for i in range(n):
        xa, xb, xc = x0 + i * step, x0 + (i + .5) * step, x0 + (i + 1) * step
        b.rod((xa, y, 7.14), (xb, y, 6.06), .04, 'steel_dark', 4); b.rod((xb, y, 6.06), (xc, y, 7.14), .04, 'steel_dark', 4)
    for i in range(n + 1):
        b.box((x0 + i * step, y, 6.6), (.05, .1, 1.0), 'steel_dark')
    b.box((x0 + .3, y, 6.1), (.5, .3, .04), 'steel_light'); b.box((x1 - .3, y, 6.1), (.5, .3, .04), 'steel_light')

def roof(b):
    g0 = b.group; b.use('OCC'); b.box((3, 12, H + .125), (14.5, 24.5, .25), 'concrete_dark'); b.use(g0)   # deck slab (occluder only)
    for y0 in [0.3] + [y + 2 for y in BAYS[:-1]] + [23.3]:                                         # underside rib panels between trusses
        pass
    ys = [0] + BAYS + [24]
    for a, c in zip(ys, ys[1:]):
        yc, w = (a + c) / 2, c - a - .25
        n = int(14 / .45)
        for i in range(n):
            x = X0 + .225 + i * .45
            sw = 'steel_light' if (i % 2 == 0) else 'steel_mid'
            if b.rng.random() < .06: sw = 'steel_worn'
            b.box((x, yc, H - .02), (.4, w, .035), sw, nb=False, nt=True)                         # ribbed deck panels
    for i in range(0, 8):                                                                         # purlins along Y on top chord
        pass

def crane(b, ybridge=10.0, zr=5.55):
    for x in (-3.35, 9.35):                                                                       # runway I-beams
        b.box((x, 12, zr), (.28, 23, .05), 'steel_dark'); b.box((x, 12, zr + .22), (.05, 23, .38), 'steel_dark'); b.box((x, 12, zr + .43), (.28, 23, .05), 'steel_dark')
    for yb in (ybridge - .5, ybridge + .5):                                                       # bridge girders
        b.box((3, yb, zr - .3), (12.7, .22, .5), 'yellow'); b.box((3, yb, zr - .56), (12.7, .3, .04), 'steel_dark')
    for x in (-3.35, 9.35):
        b.box((x, ybridge, zr - .22), (.45, 1.5, .55), 'yellow_worn'); b.reserve_box((x, ybridge, zr), (.5, 1.5, 1))
    tr = 4.6                                                                                      # hoist trolley over the turbine axis
    b.box((tr, ybridge, zr - .78), (1.0, 1.3, .5), 'orange'); b.box((tr, ybridge, zr - .45), (1.1, 1.5, .08), 'steel_dark')
    b.cyl((tr, ybridge, zr - 1.15), .22, .3, 'steel_dark', 'Z', 8)
    b.rod((tr - .08, ybridge, zr - 1.2), (tr - .08, ybridge, zr - 2.3), .02, 'steel_mid', 4); b.rod((tr + .08, ybridge, zr - 1.2), (tr + .08, ybridge, zr - 2.3), .02, 'steel_mid', 4)
    b.box((tr, ybridge, zr - 2.5), (.3, .22, .3), 'yellow'); b.box((tr, ybridge, zr - 2.76), (.12, .08, .22), 'steel_dark')
    b.rod((tr, ybridge + .65, zr - .6), (tr + .5, ybridge + 1.4, 1.9), .012, 'rubber', 4)         # pendant cable
    b.box((tr + .5, ybridge + 1.4, 1.75), (.14, .1, .28), 'red')

def door(b, frame, side_sign):
    """Orange portal frame with hazard threshold and a parked sliding leaf. Opening 2.4 x 2.7 m."""
    org, rz = frame
    with b.push(org, rz):
        w, h = 2.4, 2.7
        b.box((-w / 2 - .18, .06, h / 2 + .1), (.36, .16, h + .2), 'orange'); b.box((w / 2 + .18, .06, h / 2 + .1), (.36, .16, h + .2), 'orange')
        b.box((0, .06, h + .22), (w + .72, .16, .44), 'orange'); b.box((0, .1, h + .24), (w + .5, .02, .26), 'charcoal')
        for i in range(12):                                                                                       # hazard threshold chevrons
            b.box((-w / 2 + .1 + i * .2, -0.0, .006), (.1, .5, .008), 'yellow' if i % 2 == 0 else 'charcoal', (0, 0, .5), nb=True)
        b.box((0, 0, -.01), (w, .3, .03), 'steel_worn', nb=True)
        lx = side_sign * (w / 2 + .15 + 1.25)                                                                    # parked leaf
        b.box((lx, .22, h / 2), (2.4, .06, h), 'steel_light'); b.box((lx, .26, h - .5), (1.7, .02, .4), 'charcoal')
        b.box((lx, .17, h + .12), (2.6, .12, .1), 'steel_dark')                                                  # track
        for k in range(3): b.box((lx + (k - 1) * .85, .17, h + .05), (.05, .12, .1), 'steel_mid')
        b.box((lx - side_sign * .9, .27, 1.0), (.05, .03, .5), 'red')                                            # pull handle

def floor(b):
    # slab core with the U04 opening cut through it
    g0 = b.group; b.use('OCC')
    for r in rect_minus((X0, X1, Y0, Y1), [(HOLE[0], HOLE[1], HOLE[2], HOLE[3])]):
        b.box(((r[0] + r[1]) / 2, (r[2] + r[3]) / 2, -0.22), (r[1] - r[0], r[3] - r[2], .38), 'concrete_dark')
    b.use(g0)
    for r in rect_minus((X0, X1, Y0, Y1), [(HOLE[0], HOLE[1], HOLE[2], HOLE[3])]):
        b.box(((r[0] + r[1]) / 2, (r[2] + r[3]) / 2, -0.031), (r[1] - r[0], r[3] - r[2], .002), 'backing', nb=True)      # grout seen between tiles
    # pit under the exhaust opening
    cx, cy, w, d = (HOLE[0] + HOLE[1]) / 2, (HOLE[2] + HOLE[3]) / 2, HOLE[1] - HOLE[0], HOLE[3] - HOLE[2]
    b.box((cx, cy, -2.5), (w, d, .1), 'black')
    for dx, dy, sx, sy in ((0, d / 2, w, .05), (0, -d / 2, w, .05), (w / 2, 0, .05, d), (-w / 2, 0, .05, d)):
        b.box((cx + dx, cy + dy, -1.3), (sx, sy, 2.4), 'concrete_dark')
    # tiles 1.0 m, varied and worn (skipped under the turbine foundation and exhaust opening)
    r = b.rng
    for ix in range(14):
        for iy in range(24):
            x, y = X0 + ix + .5, Y0 + iy + .5
            if 2.0 < x < 7.2 and 2.6 < y < 23.0: continue
            nd = abs(x) < 1.8 and (y < 3 or y > 21)
            roll = r.random() + (.18 if nd else 0)
            sw = 'tile_a' if roll < .50 else 'tile_b' if roll < .72 else 'tile_c' if roll < .84 else 'tile_worn' if roll < .93 else 'tile_crack' if roll < .97 else 'tile_oil'
            h = r.uniform(.0, .006)
            b.box((x, y, -.015 + h / 2), (.975, .975, .03 + h), sw, nb=True)

def build(b):
    b.use('ARCH')
    floor(b)
    south = ((0, 0), 0); north = ((0, 24), math.pi); west = ((-4, 24), -math.pi / 2); east = ((10, 0), math.pi / 2)
    D = lambda x0, x1, z0, z1: (x0, x1, z0, z1)
    # ---- holes (local wall coords) ----
    wall(b, south, -4, 10, [D(-1.2, 1.2, 0, 2.7), D(8.15, 8.65, 4.65, 5.15), D(9.35, 9.65, .3, .6)])
    wall(b, ((0, 24), math.pi), -10, 4, [D(-1.2, 1.2, 0, 2.7), D(3.6, 4.0, 3.73, 4.03)])            # north: local x = -world x
    win_e = [4, 8, 12, 16, 20]; win_w = [4, 12, 20]
    wall(b, east, 0, 24, [D(c - 1.3, c + 1.3, 4.55, 6.55) for c in win_e])
    wall(b, ((-4, 24), -math.pi / 2), 0, 24, [D(24 - c - 1.1, 24 - c + 1.1, 5.0, 6.4) for c in win_w])   # west: local x = 24 - world y
    windows(b, east, win_e, 1.3)
    windows(b, ((-4, 24), -math.pi / 2), [24 - c for c in win_w], 1.1, 5.0, 6.4)
    door(b, ((0, 0), 0), -1); door(b, ((0, 24), math.pi), -1)
    for y in BAYS:
        column(b, -4, y, -1); column(b, 10, y, 1); truss(b, y)
    roof(b); crane(b)
    # clamp rings around utility penetrations
    b.box((8.4, .03, 4.9), (.7, .08, .7), 'steel_dark'); b.box((9.5, .03, .45), (.45, .08, .45), 'steel_dark')
