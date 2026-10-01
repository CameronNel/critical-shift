"""Turbine train, generator, process services, controls, switchgear and maintenance bay (new design, same footprint)."""
import math
from mathutils import Vector
from arch import HOLE

CX, AZ = 4.6, 2.3            # shaft axis x and height (shaft runs along Y)

def bolts_along(b, y0, y1, x, z, step=.3, sw='steel_dark'):
    n = int((y1 - y0) / step)
    for i in range(n + 1): b.cyl((x, y0 + i * step, z), .028, .09, sw, 'X', 6)

def ring_bolts(b, y, r, n, sw='steel_dark', c=(CX, 0, AZ)):
    for i in range(n):
        a = 2 * math.pi * i / n
        b.cyl((c[0] + r * math.cos(a), y, c[2] + r * math.sin(a)), .03, .09, sw, 'Y', 6)

def casing(b, y0, y1, r, body, band='orange', flange_r=None, nbolt=18):
    L = y1 - y0; yc = (y0 + y1) / 2
    b.cyl((CX, yc, AZ), r, L, body, 'Y', 16)
    fr = flange_r or r + .1
    for y in (y0 + .06, y1 - .06): b.cyl((CX, y, AZ), fr, .12, 'steel_mid', 'Y', 16); ring_bolts(b, y + (.07 if y < yc else -.07), fr - .06, nbolt)
    for k in range(3): b.cyl((CX, y0 + L * (k + 1) / 4, AZ), r + .03, .22, band, 'Y', 16)
    for s in (-1, 1):                                                       # horizontal split flange + bolts
        b.box((CX + s * (r + .06), yc, AZ), (.17, L - .3, .08), 'steel_mid'); bolts_along(b, y0 + .25, y1 - .25, CX + s * (r + .06), AZ + .05, .32)
    b.box((CX, yc, AZ - r - .06), (r * 1.6, L - .4, .12), 'steel_dark')    # lower saddle plate

def saddles(b, y0, y1, r):
    for y in (y0 + .4, y1 - .4):
        b.box((CX, y, 1.22), (r * 1.7, .5, .44), 'steel_dark', nb=True)

def bearing(b, y0, y1):
    yc = (y0 + y1) / 2
    b.box((CX, yc, 1.7), (1.25, y1 - y0, 1.4), 'steel_dark', nb=True); b.box((CX, yc, 2.45), (1.1, y1 - y0 - .1, .12), 'steel_mid')
    b.cyl((CX, yc, AZ), .42, y1 - y0 - .06, 'steel_mid', 'Y', 12)
    b.box((CX + .64, yc, 1.8), (.04, .3, .3), 'brass'); b.box((CX + .67, yc, 1.8), (.02, .2, .2), 'screen')     # oil sight glass
    b.reserve_box((CX, yc, 1.7), (1.4, y1 - y0, 1.4))

def valve(b, c, r=.14, wheel=True):
    b.box(c, (r * 2.4, r * 2.4, r * 2.4), 'steel_dark'); b.cyl((c[0], c[1], c[2] + r * 2), .04, r * 2.4, 'steel_light', 'Z', 6)
    if wheel:
        b.cyl((c[0], c[1], c[2] + r * 3.3), r * 1.5, .03, 'red', 'Z', 12)
        for k in range(2): b.box((c[0], c[1], c[2] + r * 3.3), (r * 3, .025, .02), 'red', (0, 0, k * math.pi / 2))

def flanged_pipe(b, pts, r, body='lagging', flange='steel_dark', every=1.6):
    b.pipe(pts, r, body, 8)
    for a, c in zip(pts, pts[1:]):
        A, C = Vector(a), Vector(c); L = (C - A).length
        if L < .5: continue
        n = max(1, int(L / every)); d = (C - A).normalized()
        axis = 'X' if abs(d.x) > .9 else 'Y' if abs(d.y) > .9 else 'Z'
        for i in range(n + 1):
            if i in (0, n) and n > 1 and False: continue
            p = A + d * (L * i / n)
            b.cyl(tuple(p), r * 1.32, .07, flange, axis, 8)

def hanger(b, p, top=6.0, r=.012):
    b.rod((p[0], p[1], p[2] + .15), (p[0], p[1], top), r, 'steel_dark', 4)

def duct(b, pts, w, h, sw='steel_light'):
    """Rectangular bus duct with axis-aligned legs."""
    for a, c in zip(pts, pts[1:]):
        a, c = Vector(a), Vector(c); m = (a + c) / 2; d = c - a
        s = (max(abs(d.x), w), max(abs(d.y), w), max(abs(d.z), h)) if True else None
        b.box(tuple(m), (abs(d.x) + (w if abs(d.x) < 1e-6 else 0) , abs(d.y) + (w if abs(d.y) < 1e-6 else 0), abs(d.z) + (h if abs(d.z) < 1e-6 else 0)), sw)
    for p in pts[1:-1]: b.box(p, (w * 1.06, w * 1.06, h * 1.06), 'steel_mid')
    for a, c in zip(pts, pts[1:]):
        a, c = Vector(a), Vector(c); L = (c - a).length
        for i in range(1, int(L / 1.2)):
            p = a + (c - a) * (i * 1.2 / L); b.box(tuple(p), (w * 1.08 if abs((c - a).x) < 1e-6 else .06, w * 1.08 if abs((c - a).y) < 1e-6 else .06, h * 1.08 if abs((c - a).z) < 1e-6 else .06), 'steel_dark')

def foundation(b):
    z1 = 1.0; xa, xb, ya, yb = 2.0, 7.2, 2.6, 23.0
    x0, x1, y0, y1 = HOLE
    segs = [(xa, xb, ya, y0), (xa, xb, y1, yb), (xa, x0, y0, y1), (x1, xb, y0, y1)]
    for a, c, d, e in segs:
        b.box(((a + c) / 2, (d + e) / 2, z1 / 2), (c - a, e - d, z1), 'concrete', nb=True)
        b.box(((a + c) / 2, (d + e) / 2, z1 + .01), (c - a - .3, e - d - .3 if e - d > .4 else e - d, .02), 'concrete_dark', nb=True)
    # yellow edge lining and chamfer ledge
    for sx in (xa + .08, xb - .08): b.box((sx, (ya + yb) / 2, z1 + .012), (.14, yb - ya - .02, .006), 'yellow_worn', nb=True)
    for sy in (ya + .08, yb - .08): b.box(((xa + xb) / 2, sy, z1 + .012), (xb - xa - .02, .14, .006), 'yellow_worn', nb=True)
    b.box((CX, ya - .1, .08), (xb - xa + .3, .2, .16), 'concrete_dark', nb=True); b.box((CX, yb + .1, .08), (xb - xa + .3, .2, .16), 'concrete_dark', nb=True)
    for sx in (xa - .1, xb + .1): b.box((sx, (ya + yb) / 2, .08), (.2, yb - ya, .16), 'concrete_dark', nb=True)
    # anchor bolt covers
    for y in range(3, 23, 2):
        for x in (xa + .3, xb - .3): b.cyl((x, y, z1 + .02), .06, .04, 'steel_dark', 'Z', 6)
    # steps at the south end, centred
    for k in range(4): b.box((CX, ya - .35 - (3 - k) * .0 - (3 - k) * .28 + .0, .125 * (k + 1)), (1.6, .3, .25 * (k + 1) / 1.0 * .5), 'steel_worn', nb=True) if False else None
    for k in range(4): b.box((CX, ya - .3 * (k + .5) + 0.15 * 0, .25 * (4 - k) / 4 * 1.0 / 1.0 * .5 + .0), (1.6, .3, .25 * (4 - k) ), 'steel_worn', nb=True) if False else None
    for k in range(4): b.box((CX, ya - .15 - .28 * (3 - k), .125 * (k + 1)), (1.6, .28, .25 * (k + 1)), 'steel_worn', nb=True)
    for k in range(4): b.box((CX, yb + .15 + .28 * (3 - k) if False else yb + .15 + .28 * (3 - k), .125 * (k + 1)), (1.6, .28, .25 * (k + 1)), 'steel_worn', nb=True) if (yb + 1.2 < 24) else None
    # handrails
    for xr in (xa + .12, xb - .12):
        for y in [ya + .1 + i * 1.0 for i in range(int((yb - ya) / 1.0) + 1)]:
            if abs(y - 12) < .3 and False: continue
            b.box((xr, y, z1 + .55), (.05, .05, 1.1), 'yellow')
        b.box((xr, (ya + yb) / 2, z1 + 1.05), (.05, yb - ya, .05), 'yellow'); b.box((xr, (ya + yb) / 2, z1 + .55), (.04, yb - ya, .04), 'yellow')
    for yr in (ya + .12, yb - .12):
        for x in (xa + .6, CX, xb - .6): pass
        b.box((CX - 1.15 if False else (xa + CX - .85) / 2, yr, z1 + 1.05), (CX - .85 - xa, .05, .05), 'yellow'); b.box(((xb + CX + .85) / 2, yr, z1 + 1.05), (xb - CX - .85, .05, .05), 'yellow')
        b.box(((xa + CX - .85) / 2, yr, z1 + .55), (CX - .85 - xa, .04, .04), 'yellow'); b.box(((xb + CX + .85) / 2, yr, z1 + .55), (xb - CX - .85, .04, .04), 'yellow')
    b.claim((xa - .5, ya - 1.6, 0), (xb + .5, yb + 1.6, 3.9))

def train(b):
    b.use('MACH'); foundation(b)
    # HP turbine
    casing(b, 3.2, 7.0, .9, 'lagging'); saddles(b, 3.2, 7.0, .9)
    b.box((CX, 4.2, 3.35), (1.3, 1.6, .7), 'steel_dark'); b.box((CX, 4.2, 3.72), (1.0, 1.3, .06), 'steel_mid')       # steam chest
    for dx in (-.35, .35):
        b.cyl((CX + dx, 4.2, 4.15), .13, .8, 'orange', 'Z', 8); b.cyl((CX + dx, 4.2, 4.6), .17, .12, 'steel_dark', 'Z', 8)
    bearing(b, 7.0, 8.1)
    # LP turbine
    casing(b, 8.1, 14.4, 1.3, 'lagging_dark', flange_r=1.42, nbolt=24); saddles(b, 8.1, 14.4, 1.3)
    b.box((CX, 9.3, 3.62), (1.0, .8, .12), 'steel_dark'); b.box((CX, 13.3, 3.62), (1.0, .8, .12), 'steel_dark')       # inspection hatches
    for hy in (9.3, 13.3):
        for ix in (-1, 1):
            for iy in (-1, 1): b.cyl((CX + ix * .4, hy + iy * .3, 3.7), .03, .06, 'steel_light', 'Z', 6)
    flanged_pipe(b, [(CX, 6.4, 3.2), (CX, 6.4, 4.5), (CX, 11.25, 4.5), (CX, 11.25, 3.65)], .26)                         # crossover
    bearing(b, 14.4, 15.3)
    # coupling guard
    b.cyl((CX, 15.6, AZ), .6, .6, 'yellow', 'Y', 12); b.cyl((CX, 15.6, AZ), .62, .06, 'steel_dark', 'Y', 12)
    b.box((CX, 15.6, AZ + .62), (.5, .3, .02), 'charcoal'); b.box((CX, 15.6, AZ), (.15, .65, .15), 'steel_light')
    # generator
    casing(b, 15.9, 21.3, 1.05, 'ivory', band='steel_mid', flange_r=1.15, nbolt=20); saddles(b, 15.9, 21.3, 1.05)
    b.cyl((CX, 15.95, AZ), 1.12, .38, 'orange', 'Y', 20); b.cyl((CX, 21.25, AZ), 1.12, .38, 'orange', 'Y', 20)
    for k in range(6): b.cyl((CX, 16.4 + k * .8, AZ), 1.08, .07, 'steel_mid', 'Y', 20)
    b.box((CX, 18.6, 3.55), (1.9, 3.6, .65), 'orange')                                                                  # cooler
    for k in range(10): b.box((CX, 17.0 + k * .36, 3.9), (1.7, .05, .05), 'charcoal')
    for k in range(4): b.box((CX - .72 + k * .48, 18.6, 3.9), (.05, 3.4, .05), 'orange_dark')
    b.box((CX - 1.45, 20.0, AZ + .1), (.9, 1.1, 1.0), 'steel_dark'); b.box((CX - 1.45, 20.0, AZ + .62), (.8, 1.0, .06), 'red')   # terminal box
    b.box((CX - 1.9, 20.0, AZ + .1), (.04, .7, .5), 'yellow'); b.text('HV', (CX - 1.93, 20.0, AZ + .12), .26, 'charcoal', math.pi / 2, math.pi / 2)
    # exciter
    b.cyl((CX, 21.85, AZ), .72, 1.1, 'steel_light', 'Y', 14); b.cyl((CX, 21.3, AZ), .78, .12, 'steel_dark', 'Y', 14)
    bearing(b, 22.35, 22.9)
    # visible rotating shaft segments + coupling flange (animated object is named separately in build.py)
    b.use('SHAFT'); b.cyl((CX, 7.55, AZ), .22, .9, 'steel_light', 'Y', 12); b.cyl((CX, 14.85, AZ), .22, .9, 'steel_light', 'Y', 12)
    b.cyl((CX, 15.6, AZ), .3, .25, 'steel_mid', 'Y', 12); b.cyl((CX, 22.65, AZ), .22, .5, 'steel_light', 'Y', 12)
    for k in range(6): b.box((CX + .3 * math.cos(k * math.pi / 3), 15.6 + .0, AZ + .3 * math.sin(k * math.pi / 3)), (.05, .3, .05), 'steel_dark')
    b.use('MACH')
    # steam main from U01, over the east aisle, into the steam chest
    steam = [(8.4, -.25, 4.9), (8.4, 4.0, 4.9), (8.4, 4.0, 3.55), (CX + .2, 4.0, 3.55), (CX + .2, 4.2, 3.55)]
    flanged_pipe(b, steam, .22, 'lagging')
    b.box((8.4, .25, 4.9), (.46, .3, .46), 'steel_dark')
    valve(b, (8.4, 2.0, 5.2)); b.box((8.4, 2.0, 4.9), (.5, .5, .5), 'steel_dark')
    hanger(b, (8.4, 2.0, 5.1)); hanger(b, (8.4, 3.6, 5.1)); hanger(b, (6.6, 4.0, 3.75))
    b.claim((8.1, 0, 4.4), (8.7, 4.1, 5.5))
    for x in (8.4,):
        b.box((x, 4.0, 1.7), (.3, .3, 3.4), 'steel_dark'); b.box((x, 4.0, .04), (.7, .7, .08), 'steel_dark')       # pipe stand
    # drains
    b.pipe([(CX - .7, 4.8, 1.55), (CX - 1.4, 4.8, 1.55), (CX - 1.4, 4.8, 1.05)], .035, 'brass', 6); b.pipe([(CX + .7, 9.4, 1.5), (CX + 1.5, 9.4, 1.5), (CX + 1.5, 9.4, 1.05)], .035, 'brass', 6)
    b.claim((1.4, 2.0, 0), (7.8, 23.5, 4.8))

def services(b):
    b.use('MACH')
    # condensate return U02 -> pump skid -> blind end
    cond = [(9.5, -.25, .45), (9.5, 7.0, .45)]
    b.pipe(cond, .1, 'steel_mid', 8)
    for y in (1.5, 3.5, 5.5): b.cyl((9.5, y, .45), .135, .07, 'steel_dark', 'Y', 8); b.box((9.5, y, .2), (.2, .2, .4), 'steel_dark')
    sk = (9.0, 8.3)
    b.box((sk[0], sk[1], .08), (1.4, 2.4, .16), 'steel_dark'); b.cyl((sk[0], sk[1] - .4, .6), .3, 1.0, 'steel_light', 'Y', 12)
    b.cyl((sk[0], sk[1] - .95, .6), .36, .14, 'orange', 'Y', 12); b.cyl((sk[0], sk[1] + .55, .55), .38, .5, 'orange', 'Y', 12)
    b.pipe([(9.5, 7.0, .45), (9.5, 8.5, .45), (9.5, 8.5, 1.2), (9.2, 8.8, 1.2)], .09, 'steel_mid', 8); valve(b, (9.5, 7.6, .62), .1)
    b.box((sk[0], sk[1] + 1.1, .55), (.2, .1, .3), 'charcoal'); b.claim((8.2, 6.5, 0), (9.9, 9.6, 1.4))
    # lube oil skid
    b.box((9.0, 16.0, .09), (1.6, 4.4, .18), 'steel_dark', nb=True); b.box((9.0, 17.2, .85), (1.4, 2.0, 1.1), 'steel_mid')
    b.box((9.0, 17.2, 1.42), (1.46, 2.06, .06), 'steel_dark'); b.box((9.4, 15.0, .55), (.3, .12, .5), 'charcoal')
    for k in range(3):
        b.cyl((8.55 + k * .38, 14.6, .55), .15, .7, 'orange' if k else 'orange_dark', 'Z', 10); b.cyl((8.55 + k * .38, 14.6, .93), .17, .05, 'steel_dark', 'Z', 10)
    b.cyl((9.0, 15.7, .5), .28, 1.4, 'steel_light', 'X', 12)
    for y in (16.3, 15.2): b.cyl((8.4, y, .35), .22, .5, 'orange', 'X', 10)
    b.box((8.2, 17.2, .85), (.04, 1.4, .5), 'chalk'); b.box((8.18, 17.2, .85), (.02, .3, .4), 'screen')
    b.rod((9.0, 18.7, .18), (9.0, 18.7, 1.4), .03, 'steel_dark', 4)
    for y in (13.9, 19.0, 19.0): pass
    b.pipe([(8.45, 14.0, .1), (7.4, 14.0, .1), (7.4, 14.0, .55)], .05, 'brass', 6); b.pipe([(7.4, 14.0, .55), (7.4, 13.2, .55), (7.35, 13.2, 1.4)], .05, 'brass', 6)
    b.claim((8.0, 13.5, 0), (9.9, 19.1, 1.5)); b.claim((7.2, 13.0, 0), (8.0, 14.3, 1.5))
    # instrument rack + hose cabinet east wall
    b.box((9.6, 10.5, 1.0), (.5, 1.4, 2.0), 'steel_dark'); b.box((9.4, 10.5, 1.0), (.04, 1.2, 1.8), 'charcoal')
    for i in range(4):
        for j in range(2): b.cyl((9.37, 10.1 + .4 * j + .2, 1.5 + i * .3 - .35), .08, .02, 'chalk', 'X', 12); b.box((9.355, 10.1 + .4 * j + .2, 1.5 + i * .3 - .35), (.005, .02, .12), 'red')
    b.claim((9.0, 9.6, 0), (9.9, 11.4, 2.1))
    b.box((9.75, 20.9, 1.2), (.3, .9, 1.4), 'red'); b.box((9.58, 20.9, 1.2), (.03, .7, 1.2), 'red_dark'); b.box((9.57, 20.9, 1.5), (.02, .5, .3), 'chalk'); b.claim((9.2, 20.3, 0), (9.9, 21.6, 1.9))
    # overhead cable trays along both long walls and across to the switchgear
    for x in (-3.55, 9.55):
        b.box((x, 12, 3.4), (.36, 23, .04), 'steel_dark'); b.box((x - .17, 12, 3.45), (.02, 23, .1), 'steel_dark'); b.box((x + .17, 12, 3.45), (.02, 23, .1), 'steel_dark')
        for y in range(1, 24, 2): hanger(b, (x, y, 3.4 - .15), top=3.4)
        for k in range(3): b.box((x + (k - 1) * .09, 12, 3.46), (.05, 22.5, .05), ['rubber', 'rubber', 'red_dark'][k])
    # HVAC trunk along the west ceiling
    b.box((-2.2, 12, 5.0), (1.0, 22.5, .7), 'steel_light'); b.box((-2.2, 12, 4.64), (1.1, 22.5, .03), 'steel_dark')
    for y in range(2, 24, 3): b.box((-2.2, y, 5.0), (1.06, .06, .76), 'steel_mid'); hanger(b, (-2.6, y, 4.7), top=6.0); hanger(b, (-1.8, y, 4.7), top=6.0)
    for y in (6, 12, 18): b.box((-2.2, y + 1.2, 4.62), (.7, .7, .04), 'steel_dark'); [b.box((-2.2, y + 1.2, 4.6), (.62, .02, .03), 'black') for _ in range(1)]

def controls(b):
    b.use('MACH')
    # three console cabinets against the west wall, operator side faces +X
    for k, yc in enumerate((4.5, 5.65, 6.8)):
        b.box((-3.4, yc, .55), (.8, 1.08, 1.1), 'wainscot', nb=True); b.box((-3.4, yc, .1), (.84, 1.12, .2), 'charcoal', nb=True)
        b.box((-3.0, yc, .55), (.02, .86, .8), 'charcoal'); b.box((-3.0, yc + .3, .55), (.03, .04, .22), 'steel_light')
        b.box((-3.4, yc, 1.12), (.9, 1.1, .05), 'steel_dark')                                                 # worktop
        b.box((-3.55, yc, 1.55), (.4, 1.06, .8), 'ivory', (0, -.45, 0))                                       # sloped instrument panel
        for j in range(2):
            b.box((-3.37, yc - .26 + .52 * j, 1.62), (.03, .36, .36), 'black', (0, -.45, 0))
            b.cyl((-3.355, yc - .26 + .52 * j, 1.62), .13, .02, 'chalk', 'X', 14); b.box((-3.34, yc - .26 + .52 * j, 1.62), (.01, .02, .12), 'red', (0, 0, 0))
            b.box((-3.34, yc - .26 + .52 * j, 1.85), (.02, .06, .04), 'screen' if (j + k) % 2 else 'led_green')
        b.box((-3.2, yc - .25, 1.19), (.14, .04, .1), 'steel_dark'); b.rod((-3.2, yc - .25, 1.2), (-3.0, yc - .25, 1.38), .02, 'steel_dark', 4); b.sphere((-3.0, yc - .25, 1.4), .04, 'red')
    b.cyl((-3.1, 7.05 - .05, 1.22), .09, .06, 'yellow', 'Z', 12); b.cyl((-3.1, 7.05 - .05, 1.27), .06, .05, 'red', 'Z', 12)    # e-stop
    # annunciator board on the wall
    b.box((-3.9, 5.65, 2.55), (.1, 3.4, 1.0), 'charcoal')
    cols = ['led_green', 'screen', 'led_red', 'screen', 'led_green', 'led_green']
    for i in range(10):
        for j in range(3): b.box((-3.83, 4.1 + i * .34, 2.25 + j * .3), (.03, .26, .2), cols[(i * 2 + j) % 6])
    b.box((-3.85, 5.65, 3.55), (.1, 3.6, .55), 'orange'); b.text('TURBINE CONTROL', (-3.78, 5.65, 3.55), .28, 'chalk', math.pi / 2, math.pi / 2)
    # operator desk + chair
    b.box((-2.2, 5.6, .72), (.8, 1.5, .05), 'wood'); [b.box((-2.2 + dx, 5.6 + dy, .36), (.05, .05, .72), 'steel_dark') for dx in (-.35, .35) for dy in (-.7, .7)]
    b.box((-2.2, 5.3, .78), (.3, .22, .01), 'paper', (0, 0, .3)); b.box((-2.12, 6.0, .86), (.3, .02, .2), 'black'); b.box((-2.12, 6.0, .76), (.12, .1, .02), 'steel_dark')
    b.box((-2.12, 6.0, .88), (.26, .005, .16), 'screen_cool')
    b.box((-1.5, 5.6, .46), (.42, .42, .06), 'rubber'); b.box((-1.3, 5.6, .72), (.06, .42, .5), 'rubber'); b.cyl((-1.5, 5.6, .22), .04, .44, 'steel_dark', 'Z', 6)
    for a in range(5): b.box((-1.5 + .2 * math.cos(a * 1.256), 5.6 + .2 * math.sin(a * 1.256), .03), (.2, .04, .03), 'steel_dark', (0, 0, a * 1.256))
    b.claim((-3.95, 3.8, 0), (-1.0, 7.5, 3.9))
    # switchgear row at the north-west wall (HV bus leaves overhead through U03)
    for k, x in enumerate((-3.35, -2.3, -1.25)):
        b.box((x, 23.55, 1.1), (.98, .8, 2.2), 'steel_mid', nb=True); b.box((x, 23.14, 1.1), (.9, .02, 2.1), 'steel_dark')
        b.box((x, 23.12, 1.4), (.7, .015, .5), 'chalk'); b.box((x, 23.11, 1.65), (.5, .012, .12), 'screen' if k != 1 else 'led_green')
        b.box((x, 23.11, .5), (.5, .012, .6), 'orange_dark'); [b.box((x, 23.1, .35 + i * .08), (.4, .012, .02), 'black') for i in range(4)]
        b.box((x, 23.55, 2.25), (.98, .8, .1), 'steel_dark')
    b.text('GEN PROTECTION', (-2.3, 23.1, 2.55), .18, 'chalk', 0, math.pi / 2)
    b.claim((-3.9, 22.8, 0), (-.7, 24.0, 2.4))
    # generator HV bus duct: terminal box -> up -> west across the room -> through the north wall at U03
    d = [(CX - 1.9, 20.0, AZ + .1), (CX - 2.5, 20.0, AZ + .1), (CX - 2.5, 20.0, 3.88), (-3.8, 20.0, 3.88), (-3.8, 24.25, 3.88)]
    duct(b, d, .4, .3)
    b.box((-3.8, 24.5, 3.88), (.4, .6, .3), 'steel_light'); b.box((-4.1, 24.85, 3.88), (.4, .6, .3), 'steel_light', (0, 0, -.9)); b.box((-4.32, 25.0, 3.88), (.4, 1.0, .3), 'steel_mid')
    for y in (21.5, 23.0): hanger(b, (-3.8, y, 3.7), top=6.0)
    hanger(b, (-2.0, 20.0, 3.7), top=6.0); hanger(b, (0.8, 20.0, 3.7), top=6.0)
    b.text('HV BUS / U03', (-3.2, 20.0, 4.2), .2, 'yellow', 0, math.pi / 2)

def maintenance(b):
    b.use('MACH')
    # spare rotor on two cradles (hero prop, crane-liftable)
    ry, rx, rz = 17.0, -.9, .62
    for y in (14.6, 19.4): b.box((rx, y, .3), (.9, .22, .6), 'steel_dark', nb=True); b.box((rx, y, .56), (.7, .2, .1), 'orange_dark')
    b.cyl((rx, ry, rz + .14), .17, 6.0 if False else 5.8, 'steel_light', 'Y', 10)
    for i, yy in enumerate((15.3, 15.75, 16.2, 16.65, 17.1, 17.55, 18.0, 18.45)):
        b.cyl((rx, yy, rz + .14), .55 - .02 * abs(i - 3.5), .38, 'steel_mid' if i % 2 else 'steel_light', 'Y', 18)
        b.cyl((rx, yy, rz + .14), .5 - .02 * abs(i - 3.5), .4, 'steel_dark', 'Y', 18)
    b.claim((-1.9, 14.2, 0), (.3, 19.7, 1.3))
    # workbench along the west wall with vice, shelf and tool wall
    b.box((-3.35, 16.0, .46), (.7, 3.0, .08), 'wood'); b.box((-3.35, 16.0, .54), (.72, 3.0, .02), 'wood_dark')
    for y in (14.6, 17.4): b.box((-3.35, y, .22), (.66, .08, .44), 'steel_dark'); b.box((-3.35, y, .8), (.04, .04, .04), 'steel_dark') if False else None
    b.box((-3.35, 14.55, .24), (.62, .06, .48), 'steel_dark'); b.box((-3.35, 17.45, .24), (.62, .06, .48), 'steel_dark'); b.box((-3.35, 16.0, .12), (.62, 2.9, .04), 'steel_dark')
    b.box((-3.45, 15.1, .62), (.18, .26, .16), 'steel_dark'); b.box((-3.45, 15.1, .72), (.1, .26, .05), 'steel_mid')                 # vice
    b.box((-3.7, 16.0, 1.9), (.3, 3.0, .04), 'wood'); b.box((-3.78, 16.0, 1.6), (.02, 3.0, 1.0), 'wood_dark')
    for i in range(7):
        y = 14.7 + i * .43
        b.box((-3.74, y, 1.65), (.04, .03, .45), 'steel_mid'); b.box((-3.74, y, 1.43), (.05, .08, .1), 'steel_mid'); b.box((-3.74, y, 1.9 - .01), (.045, .04, .18), ['orange', 'yellow'][i % 2], (0, 0, 0))
    b.box((-3.45, 17.1, .66), (.3, .3, .24), 'orange'); b.box((-3.3, 16.5, .58), (.25, .4, .08), 'steel_dark')
    b.claim((-3.9, 14.2, 0), (-2.9, 17.9, 2.3))
    # parts racking
    for yc in (19.9, 21.2):
        for z in (.1, .7, 1.3, 1.9): b.box((-3.45, yc, z), (.6, 1.1, .04), 'orange_dark')
        for y in (yc - .53, yc + .53): [b.box((-3.7 + dx, y, 1.0), (.05, .05, 2.0), 'steel_dark') for dx in (0, .6)]
        for i, z in enumerate((.1, .7, 1.3)): b.box((-3.45, yc + (.1 if i % 2 else -.1), z + .17), (.4, .5, .3), ['wood', 'steel_mid', 'orange'][i])
    b.claim((-3.9, 19.2, 0), (-3.0, 21.9, 2.2))
    # lay-down floor marking + welding cart
    for dx in (-1.6, .9): b.flat((dx, 17.0), .08, 7.0, 'yellow', 0, z=.008) if False else None
    b.flat((-.3, 12.1), 5.3, .09, 'yellow', 0, z=.008); b.flat((-.3, 21.9), 5.3, .09, 'yellow', 0, z=.008)
    b.flat((-2.95, 17), .09, 9.8, 'yellow', 0, z=.008); b.flat((2.35, 17), .09, 9.8, 'yellow', 0, z=.008) if False else None
    b.box((.2, 21.2, .45), (.6, .9, .06), 'steel_dark'); [b.cyl((.2 + dx, 21.2 + dy, .1), .08, .08, 'rubber', 'X', 8) for dx in (-.25, .25) for dy in (-.35, .35)]
    b.cyl((.1, 21.5, .85), .1, 1.0, 'steel_light', 'Z', 8); b.cyl((.3, 21.5, .8), .1, .9, 'red', 'Z', 8); b.box((.2, 20.95, .6), (.3, .25, .3), 'orange')
    b.claim((-.3, 20.6, 0), (.7, 22.0, 1.4))
    # stairs + landing to nothing: none. Gate lights above the bay come from lights.py
