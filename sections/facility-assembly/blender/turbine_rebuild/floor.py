"""Floor (v7): ONE concrete slab (floormesh.py) with real holes for channels, sumps, drains and the exhaust opening, and one texture set
(floortex.py) carrying wetness, flow, cracks, joints, wear and paint. This module holds the layout and the drain hardware that sits in the holes."""
import math, random
from mathutils import Vector
from arch import HOLE, torus, rect_minus

CH_X = (1.45, 7.62)            # linear drainage channels along the foundation (west / east)
CH_Y0, CH_Y1, CH_W = 2.5, 22.9, .32
SUMPS = [(1.45, 23.5), (7.62, 23.5)]
DRAINS = [(-1.05, 8.55), (0.9, 3.2), (8.0, 1.7), (-2.8, 12.4), (-1.0, 22.2)]
SLOPE = .004

def grate_channel(b, x, y0, y1, w, rng):
    L = y1 - y0; ym = (y0 + y1) / 2
    b.box((x, ym, -.28), (w + .04, L, .002), 'backing')                                # dark liner at the bottom of the channel
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
    b.box((x, y, .0035), (s + .12, s + .12, .014), 'steel_dark', bev=.008); b.box((x, y, -.28), (s, s, .003), 'backing')
    for i in range(10): b.box((x, y - s / 2 + .05 + i * (s - .1) / 9, .004), (s - .04, .028, .022), 'steel_mid')
    for sx in (-1, 1): b.box((x + sx * (s / 2 - .03), y, .008), (.03, s - .02, .012), 'steel_dark', bev=.004)
    for sx in (-1, 1):
        for sy in (-1, 1): b.cyl((x + sx * (s / 2 + .01), y + sy * (s / 2 + .01), .013), .018, .008, 'steel_light', 'Z', 8)

def round_drain(b, x, y, r=.2):
    b.cyl((x, y, .004), r + .055, .014, 'steel_dark', 'Z', 36, bev=.006); b.cyl((x, y, -.28), r, .003, 'backing', 'Z', 28)
    for k in range(6): b.box((x, y, .0135), (r * 1.7, .022, .012), 'steel_mid', (0, 0, k * math.pi / 6), bev=.004)
    torus(b, (x, y, .0145), r * .55, .009, 'steel_mid', 'Z', 20); b.cyl((x, y, .0145), .035, .012, 'steel_light', 'Z', 14, bev=.004)


def _layout():
    R = random.Random(21)
    flows = [([(-.35, 9.15), (-.55, 8.9), (-.85, 8.65), (-1.05, 8.55)], .22, .12), ([(8.18, 8.7), (8.0, 8.9), (7.84, 9.15), (7.7, 9.35)], .13, .08),
             ([(8.2, 15.3), (8.0, 15.6), (7.86, 15.9), (7.7, 16.0)], .12, .07), ([(8.15, 17.9), (7.95, 18.2), (7.78, 18.3)], .1, .06),
             ([(7.0, .7), (7.15, 1.4), (7.35, 2.0), (7.55, 2.7)], .13, .09), ([(8.7, 21.9), (8.4, 22.3), (8.0, 22.9), (7.7, 23.3)], .16, .1)]
    for yy in (4.6, 6.4, 9.6, 12.0, 14.4, 17.0, 19.6, 21.2):
        x0 = R.uniform(-.9, .1); flows.append(([(x0, yy), (x0 + .7, yy + R.uniform(-.25, .25)), (1.12, yy + R.uniform(-.3, .3)), (1.27, yy + R.uniform(-.2, .2))], .05, .1))
    paint = []
    for xl in (1.0, 7.98):
        y = 3.0
        while y < 22.4:
            ln = R.uniform(.7, 1.6); gap = R.choice((.0, .08, .22, .35)); paint.append((xl - .045, y, xl + .045, y + ln)); y += ln + gap
    paint += [(-2.995, 12.1, -2.905, 21.9), (-2.95, 12.055, 2.35, 12.145), (-2.95, 21.855, 2.35, 21.945)]
    return dict(
        joints_x=[-2.5, -1.33, 0.1, 8.3], joints_y=[24 * k / 7 for k in range(1, 7)],
        channels=[(CH_X[0], CH_Y0, CH_Y1, CH_W + .02), (CH_X[1], CH_Y0, CH_Y1, CH_W + .02)], sumps=[(sx, sy, .92) for sx, sy in SUMPS], drains=[(dx, dy, .2) for dx, dy in DRAINS],
        flows=flows, wet_runs=[(3.0, 9.5), (11.0, 17.5), (18.5, 22.4)],
        puddles=[],
        patches=[(-3.0, 10.6, 1.2, .8), (9.15, 3.0, .9, .7), (.45, 6.7, .8, .6), (-2.6, 1.1, .9, .6)],
        scuffs=[[(.02, 1.2), (-.18, 4.0), (-.78, 8.0), (-1.18, 11.5)], [(.58, 1.2), (.38, 4.0), (-.22, 8.0), (-.62, 11.5)]],
        cracks=[(-3.1, 2.0, .7, 2.4), (9.1, 11.0, 1.4, 2.0)],
        paint=paint, stains=[(-3.2, 6.8, .22), (6.4, 21.2, .24), (-.4, 12.8, .22), (8.6, 8.8, .5), (8.5, 16.0, .45), (-.35, 9.15, .45)],
        rust=[[(7.6, 3.0), (7.62, 6.0)], [(1.4, 14.0), (1.45, 17.0)]],
        lanes=[[(-.2, 1.0), (-.8, 12.0)], [(1.0, 3.0), (1.0, 22.0)], [(7.9, 3.0), (7.9, 22.0)], [(0.0, 20.5), (0.0, 23.5)]])

LAYOUT = _layout()

def build(b):
    """Drain hardware that sits in the holes cut through the floor slab."""
    b.use('ARCH'); R = random.Random(21)
    for xc in CH_X: grate_channel(b, xc, CH_Y0, CH_Y1, CH_W, R)
    for sx, sy in SUMPS: sump(b, sx, sy)
    for dx, dy in DRAINS: round_drain(b, dx, dy)
    b.cyl((-2.1, 10.2, .004), .36, .012, 'steel_dark', 'Z', 40, bev=.006); torus(b, (-2.1, 10.2, .012), .27, .012, 'trim_black', 'Z', 28)       # manhole cover (a lid, not a hole)
    for k in range(2): b.box((-2.1 + (-.12 if k == 0 else .12), 10.2, .012), (.1, .03, .008), 'backing')
    b.decal('drain', (-2.1, 10.2, .0132), rot=(0, 0, 0))
