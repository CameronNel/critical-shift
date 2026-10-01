"""Turbine train, generator, process services, controls, switchgear and maintenance bay (v3: hero-quality, restrained)."""
import math
from mathutils import Vector, Matrix
from arch import HOLE

CX, AZ = 4.6, 2.3            # shaft axis x and height (shaft runs along Y)

# ---------- small reusable assets ----------
def hexbolt(b, c, axis='Y', r=.026, h=.03, sw='steel_dark'): b.cyl(c, r, h, sw, axis, 6)

def torus(b, c, R, r, sw, plane='Z', n=28):
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        p = (R * math.cos(a), R * math.sin(a), 0) if plane == 'Z' else (R * math.cos(a), 0, R * math.sin(a)) if plane == 'Y' else (0, R * math.cos(a), R * math.sin(a))
        pts.append((c[0] + p[0], c[1] + p[1], c[2] + p[2]))
    b.sweep(pts, r, sw, 10, R * .15, caps=False)

def handwheel(b, c, R=.17, sw='red'):
    torus(b, c, R, .014, sw, 'Z', 24); b.cyl(c, .03, .05, 'steel_dark', 'Z', 12)
    for k in range(3): b.box(c, (R * 2 - .02, .018, .014), sw, (0, 0, k * math.pi / 3))

def valve(b, c, r=.14, wheel=True):
    b.box(c, (r * 2.4, r * 2.2, r * 2.0), 'steel_dark', bev=.02); b.cyl((c[0], c[1], c[2] + r * 1.4), r * .7, r * 1.2, 'steel_mid', 'Z', 20, bev=.008)
    b.cyl((c[0], c[1], c[2] + r * 2.4), .02, r * 1.4, 'steel_light', 'Z', 10)
    if wheel: handwheel(b, (c[0], c[1], c[2] + r * 3.2), r * 1.3)

def gauge(b, c, axis='X', r=.1, face='paper'):
    """Dial on a vertical panel facing +X (axis X) or -Y (axis Y)."""
    b.cyl(c, r, .035, 'steel_light', axis, 28, bev=.006); d = (.019 if axis in 'XY' else 0)
    cc = (c[0] + (d if axis == 'X' else 0), c[1] - (d if axis == 'Y' else 0), c[2])
    b.cyl(cc, r * .82, .014, face, axis, 28)
    cn = (c[0] + (.027 if axis == 'X' else 0), c[1] - (.027 if axis == 'Y' else 0), c[2])
    b.box(cn, (.004 if axis == 'X' else .008, .008 if axis == 'X' else .004, r * .7), 'red', (0, 0, 0))

def pipe_lagged(b, path, r, body='lagging', flange=True, bend=.35):
    b.sweep(path, r, body, 28, bend)
    for A, C in zip(path, path[1:]):
        A, C = Vector(A), Vector(C); L = (C - A).length; d = (C - A).normalized()
        ax = 'X' if abs(d.x) > .9 else 'Y' if abs(d.y) > .9 else 'Z'
        k = .6
        while k < L - .5: b.cyl(tuple(A + d * k), r + .012, .05, 'steel_mid', ax, 28, bev=.005); k += 1.2
    if flange:
        for P, Q in ((path[0], path[1]), (path[-1], path[-2])):
            P, Q = Vector(P), Vector(Q); d = (Q - P).normalized(); ax = 'X' if abs(d.x) > .9 else 'Y' if abs(d.y) > .9 else 'Z'
            b.cyl(tuple(P + d * .05), r * 1.35, .08, 'steel_dark', ax, 28, bev=.008)
            for i in range(8):
                a = 2 * math.pi * i / 8; o = Vector((math.cos(a), math.sin(a), 0)) * r * 1.2
                off = Vector((o.x, o.y, 0)) if ax == 'Z' else Vector((0, o.x, o.y)) if ax == 'X' else Vector((o.x, 0, o.y))
                hexbolt(b, tuple(P + d * .1 + off), ax, .018, .02)

def hanger(b, p, top=6.0, r=.012): b.rod((p[0], p[1], p[2] + .1), (p[0], p[1], top), r, 'steel_dark', 8)

def duct(b, pts, w, h, sw='steel_light'):
    for a, c in zip(pts, pts[1:]):
        a, c = Vector(a), Vector(c); m = (a + c) / 2; d = c - a
        b.box(tuple(m), (abs(d.x) + (w if abs(d.x) < 1e-6 else 0), abs(d.y) + (w if abs(d.y) < 1e-6 else 0), abs(d.z) + (h if abs(d.z) < 1e-6 else 0)), sw, bev=.014)
    for p in pts[1:-1]: b.box(p, (w * 1.08, w * 1.08, h * 1.08), 'steel_mid', bev=.014)
    for a, c in zip(pts, pts[1:]):
        a, c = Vector(a), Vector(c); L = (c - a).length; d = c - a
        for i in range(1, int(L / 1.5)):
            p = a + d * (i * 1.5 / L)
            b.box(tuple(p), (w * 1.1 if abs(d.x) < 1e-6 else .05, w * 1.1 if abs(d.y) < 1e-6 else .05, h * 1.1 if abs(d.z) < 1e-6 else .05), 'steel_dark', bev=.008)

def manway(b, c, r=.28):
    b.cyl(c, r, .1, 'steel_mid', 'Z', 32, bev=.01); b.cyl((c[0], c[1], c[2] + .07), r * .78, .06, 'steel_light', 'Z', 32, bev=.008)
    for i in range(12):
        a = 2 * math.pi * i / 12; hexbolt(b, (c[0] + (r - .035) * math.cos(a), c[1] + (r - .035) * math.sin(a), c[2] + .07), 'Z', .02, .03)
    b.sphere((c[0], c[1], c[2] + .1), .07, 'steel_dark', 12)

def gauge_plate(b, x, y, z):
    b.box((x, y, z), (.04, .8, .34), 'steel_dark', bev=.012)
    for i in range(3): gauge(b, (x + .03, y - .26 + i * .26, z), 'X', .08)

def bypass(b, x, y, z):
    b.sweep([(x, y, z), (x + .45, y, z), (x + .45, y, z - .5)], .05, 'steel_mid', 16, .12); valve(b, (x + .45, y, z - .35), .08)

# ---------- turbine train (v4: tapered stepped casings, exposed bladed rotor, gold coupling) ----------
def handrails(b, xa, xb, ya, yb, z1):
    for xr in (xa + .12, xb - .12):
        n = int((yb - ya) / 2.0) + 1; ys = [ya + .12 + i * (yb - ya - .24) / n for i in range(n + 1)]
        for y in ys: b.cyl((xr, y, z1 + .55), .042, 1.1, 'trim_black', 'Z', 14, bev=.006); b.cyl((xr, y, z1 + .02), .1, .03, 'steel_dark', 'Z', 16, bev=.006); b.cyl((xr, y, z1 + 1.1), .05, .03, 'gold_paint', 'Z', 14, bev=.006)
        b.rod((xr, ys[0], z1 + 1.05), (xr, ys[-1], z1 + 1.05), .032, 'gold_paint', 12); b.rod((xr, ys[0], z1 + .55), (xr, ys[-1], z1 + .55), .024, 'trim_black', 12)
        b.box((xr, (ya + yb) / 2, z1 + .06), (.012, yb - ya - .2, .1), 'trim_black')
    for yr in (ya + .12, yb - .12):
        for (x0, x1) in ((xa + .12, CX - .95), (CX + .95, xb - .12)):
            for z in (z1 + .55, z1 + 1.05): b.rod((x0, yr, z), (x1, yr, z), .032 if z > z1 + .6 else .024, 'gold_paint' if z > z1 + .6 else 'trim_black', 12)
        for x in (CX - .95, CX + .95): b.cyl((x, yr, z1 + .55), .042, 1.1, 'trim_black', 'Z', 14, bev=.006)

def foundation(b):
    z1 = 1.0; xa, xb, ya, yb = 2.0, 7.2, 2.6, 23.0; x0, x1, y0, y1 = HOLE
    for a, c, d, e in [(xa, xb, ya, y0), (xa, xb, y1, yb), (xa, x0, y0, y1), (x1, xb, y0, y1)]:
        b.box(((a + c) / 2, (d + e) / 2, z1 / 2), (c - a, e - d, z1), 'concrete', nb=True, bev=.05)
        b.box(((a + c) / 2, (d + e) / 2, z1 + .008), (c - a - .26, e - d - .26 if e - d > .5 else e - d, .016), 'slate_dark', nb=True)
    for sx in (xa + .07, xb - .07): b.box((sx, (ya + yb) / 2, z1 + .012), (.1, yb - ya - .02, .006), 'yellow_worn', nb=True)
    for sy in (ya + .07, yb - .07): b.box(((xa + xb) / 2, sy, z1 + .012), (xb - xa - .02, .1, .006), 'yellow_worn', nb=True)
    b.box((CX, ya - .06, .07), (xb - xa + .24, .12, .14), 'concrete_dark', nb=True, bev=.015); b.box((CX, yb + .06, .07), (xb - xa + .24, .12, .14), 'concrete_dark', nb=True, bev=.015)
    for sx in (xa - .06, xb + .06): b.box((sx, (ya + yb) / 2, .07), (.12, yb - ya, .14), 'concrete_dark', nb=True, bev=.015)
    for y in range(3, 23, 3):
        for x in (xa + .3, xb - .3): b.cyl((x, y, z1 + .02), .055, .03, 'steel_dark', 'Z', 14)
    for k in range(4):                                                        # steps, south end
        b.box((CX, ya - .14 - .26 * (3 - k), .125 * (k + 1)), (1.6, .26, .25 * (k + 1)), 'steel_worn', nb=True, bev=.01)
        b.box((CX, ya - .02 - .26 * (3 - k), .25 * (k + 1) - .008), (1.6, .03, .016), 'yellow')
    for sx, sgn in ((xb, 1), (xa, -1)):
        b.box((sx + sgn * .006, (ya + yb) / 2, .09), (.024, yb - ya - .1, .18), 'trim_black', bev=.01)                  # kick plate
        for k in range(40): b.box((sx + sgn * .004, ya + .4 + k * .5, .24), (.014, .25, .06), 'yellow' if k % 2 == 0 else 'trim_black')
        for idx in range(12):
            y = 3.5 + idx * 1.62
            for (fy, fz, fw, fh) in ((y, .86, 1.36, .03), (y, .34, 1.36, .03)): b.box((sx + sgn * .012, fy, fz), (.024, fw, fh), 'orange', bev=.006)
            for dy in (-.68, .68): b.box((sx + sgn * .012, y + dy, .6), (.024, .03, .55), 'orange', bev=.006)
            b.box((sx + sgn * .008, y, .6), (.016, 1.3, .5), 'concrete_dark', bev=.008)
            if idx % 2 == 0:
                b.box((sx + sgn * .018, y, .6), (.012, 1.0, .34), 'backing')
                for q in range(5): b.box((sx + sgn * .026, y, .47 + q * .065), (.012, .96, .02), 'steel_dark', bev=.004)
            else:
                b.text('%02d' % (idx + 1), (sx + sgn * .02, y, .6), .26, 'chalk', sgn * math.pi / 2, math.pi / 2)
    handrails(b, xa, xb, ya, yb, z1)
    b.claim((xa - .5, ya - 1.6, 0), (xb + .5, yb + 1.6, 3.9))

def flange_ring(b, y, r, nbolt=16, face=1):
    b.cyl((CX, y, AZ), r, .12, 'steel_mid', 'Y', 48, bev=.012)
    for i in range(nbolt):
        a = 2 * math.pi * i / nbolt; hexbolt(b, (CX + (r - .07) * math.cos(a), y + face * .075, AZ + (r - .07) * math.sin(a)), 'Y', .028, .03)

def stepped(b, segs, body, flanges=True, nbolt=16):
    """segs: [(y0, y1, r0, r1), ...] frustums joined by flange rings."""
    for k, (y0, y1, r0, r1) in enumerate(segs):
        b.cyl((CX, (y0 + y1) / 2, AZ), r0, y1 - y0, body, 'Y', 48, r2=r1)
    ys = [(segs[0][0], segs[0][2], -1)] + [(s[0], max(s[2], segs[i][3]), 0) for i, s in enumerate(segs[1:])] + [(segs[-1][1], segs[-1][3], 1)]
    for y, r, face in ys:
        flange_ring(b, y + (.06 if face == -1 else -.06 if face == 1 else 0), r + .1, nbolt, face or 1)

def saddles(b, y0, y1, r):
    for y in (y0 + .4, y1 - .4): b.box((CX, y, 1.22), (r * 1.7, .5, .44), 'steel_dark', nb=True, bev=.04)

def bearing(b, y0, y1):
    yc = (y0 + y1) / 2; L = y1 - y0
    b.prism([(-.62, 0), (.62, 0), (.62, .85), (.4, 1.3), (-.4, 1.3), (-.62, .85)], L, 'steel_dark', (CX, yc, 1.0), True, 'Y', bev=.03)
    b.cyl((CX, yc, AZ), .42, L - .06, 'steel_mid', 'Y', 32, bev=.012)
    b.cyl((CX + .64, yc - L * .25, 1.8), .06, .04, 'brass', 'X', 20, bev=.006); b.cyl((CX + .66, yc - L * .25, 1.8), .045, .02, 'glass', 'X', 20)
    for dy in (-.2, .2): b.cyl((CX + .64, yc + dy, 1.4), .015, .06, 'brass', 'X', 8)
    b.reserve_box((CX, yc, 1.7), (1.4, L, 1.4))

def exposed_lp(b, y0, y1):
    """Lower-half LP casing with the rotor and its gold blading open to the hall."""
    L = y1 - y0; yc = (y0 + y1) / 2
    b.arc_shell((CX, yc, AZ), 1.34, 1.24, L, math.pi, 2 * math.pi, 'casing_dark', 32, bev=.012)
    for s in (-1, 1):
        b.box((CX + s * 1.3, yc, AZ), (.2, L, .08), 'steel_mid', bev=.02)
        for i in range(int(L / .28)): b.cyl((CX + s * 1.3, y0 + .16 + i * .28, AZ + .05), .036, .04, 'steel_dark', 'Z', 6)
        b.box((CX + s * 1.3, yc, AZ - .1), (.28, L, .06), 'steel_dark', bev=.02)
    stages = [y0 + .45 + k * (L - .9) / 5 for k in range(6)]
    b.cyl((CX, yc, AZ), .26, L + .2, 'steel_light', 'Y', 32)
    for k, y in enumerate(stages):
        R = .86 + .035 * k
        b.cyl((CX, y, AZ), R, .34, 'steel_mid', 'Y', 48, bev=.02); b.cyl((CX, y, AZ), R + .05, .12, 'steel_light', 'Y', 48, bev=.008)
        b.arc_shell((CX, y + .25, AZ), 1.22, R + .13, .1, math.pi, 2 * math.pi, 'steel_dark', 24)                    # stator diaphragm
        for q in range(32):
            a = 2 * math.pi * q / 32; ca, sa = math.cos(a), math.sin(a)
            M = Matrix(((0, -sa, ca, CX + R * ca), (1, 0, 0, y), (0, ca, sa, AZ + R * sa), (0, 0, 0, 1))) @ Matrix.Rotation(math.radians(24), 4, 'Z')
            b.push_m(M); b.prism([(-.17, 0), (-.09, .035), (.09, .035), (.17, 0), (.09, -.035), (-.09, -.035)], .17, 'brass_blade', (0, 0, .09), True, 'Z', bev=.004); b.pop()
        b.arc_shell((CX, y, AZ), R + .2, R + .16, .05, 0, 2 * math.pi, 'steel_light', 40)                        # shroud band
        b.cyl((CX, y + .22, AZ), .3, .06, 'brass', 'Y', 32, bev=.006)                                              # seal collar on the shaft
    b.reserve_box((CX, yc, AZ), (2.7, L, 1.5))

def coupling(b, y):
    b.cyl((CX, y, AZ), .42, .5, 'orange', 'Y', 40, bev=.015)
    for i in range(12):
        a = 2 * math.pi * i / 12; hexbolt(b, (CX + .36 * math.cos(a), y - .27, AZ + .36 * math.sin(a)), 'Y', .026, .03, 'steel_dark')
    b.cyl((CX, y, AZ), .445, .05, 'lamp', 'Y', 40)                                                              # hot glow band
    b.arc_shell((CX, y, AZ), .66, .58, .62, math.pi, 2 * math.pi, 'steel_dark', 20, bev=.01)
    for s in (-1, 1): b.box((CX + s * .62, y, AZ), (.1, .62, .05), 'steel_mid', bev=.012)

def train(b):
    b.use('MACH'); foundation(b)
    stepped(b, [(3.2, 4.3, .66, .80), (4.3, 5.7, .80, .95), (5.7, 7.0, .95, .78)], 'casing'); saddles(b, 3.2, 7.0, .9)
    for y in (3.9, 6.2): b.cyl((CX, y, AZ), .965 if y > 5 else .82, .16, 'orange', 'Y', 48, bev=.01)
    b.prism([(-.72, 0), (.72, 0), (.52, .62), (-.52, .62)], 1.5, 'steel_dark', (CX, 4.2, 3.12), True, 'Y', bev=.035)                # steam chest
    b.box((CX, 4.2, 3.75), (.9, 1.2, .04), 'orange', bev=.012)
    for dx in (-.35, .35):
        b.cyl((CX + dx, 4.2, 4.1), .13, .66, 'steel_mid', 'Z', 28, bev=.01); b.cyl((CX + dx, 4.2, 4.5), .17, .1, 'steel_dark', 'Z', 28, bev=.01); b.sphere((CX + dx, 4.2, 4.58), .1, 'orange', 16)
    bearing(b, 7.0, 8.1)
    stepped(b, [(8.1, 9.2, 1.0, 1.32)], 'casing_dark'); exposed_lp(b, 9.2, 13.3); stepped(b, [(13.3, 14.4, 1.32, 1.05)], 'casing_dark')
    saddles(b, 8.1, 9.2, 1.1); saddles(b, 13.3, 14.4, 1.1)
    pipe_lagged(b, [(CX, 6.4, 3.15), (CX, 6.4, 4.5), (CX, 11.25, 4.5), (CX, 11.25, 3.65)], .26, bend=.5)                           # crossover (now lagged to the exposed section)
    gauge_plate(b, CX + 1.31, 8.7, AZ + .1); gauge_plate(b, CX + 1.31, 13.9, AZ + .1); bypass(b, CX + 1.28, 14.15, AZ - .35)
    b.box((CX + .9, 5.0, AZ + .1), (.04, .5, .28), 'steel_dark', bev=.01); gauge(b, (CX + .93, 5.0, AZ + .1), 'X', .09)
    manway(b, (CX, 6.1, 3.15), .22)
    bearing(b, 14.4, 15.3); coupling(b, 15.6)
    stepped(b, [(15.9, 16.7, .92, 1.05), (16.7, 20.5, 1.05, 1.05), (20.5, 21.3, 1.05, .9)], 'casing', nbolt=20); saddles(b, 15.9, 21.3, 1.05)
    for k in range(15): b.cyl((CX, 16.9 + k * .26, AZ), 1.1, .055, 'steel_mid', 'Y', 48, bev=.01)                  # cooling-fin bands
    b.prism([(-.98, 0), (.98, 0), (.62, .56), (-.62, .56)], 3.7, 'hood_orange', (CX, 18.6, 3.2), True, 'Y', bev=.04)                    # cooler hood, chamfered
    for s in (-1, 1): b.box((CX + s * .78, 18.6, 3.5), (.04, 3.7, .05), 'orange', (0, 0, -s * .55 if False else 0), bev=.01)
    b.box((CX, 18.6, 3.18), (2.06, 3.78, .06), 'orange_dark', bev=.012)
    b.box((CX, 18.6, 3.77), (1.0, 2.2, .012), 'backing')
    for k in range(10): b.box((CX, 17.55 + k * .2, 3.785), (.9, .07, .02), 'steel_dark', bev=.004)
    b.box((CX, 16.43, 3.55), (.9, .02, .24), 'steel_dark', bev=.006); b.cyl((CX, 16.41, 3.55), .08, .02, 'chalk', 'Y', 20)
    b.box((CX - 1.2, 15.98, 1.55), (.5, .01, .26), 'chalk'); b.text('TG-3', (CX - 1.2, 15.97, 1.55), .1, 'trim_black', 0, math.pi / 2)
    b.box((CX - 1.45, 20.0, AZ + .1), (.9, 1.1, 1.0), 'steel_dark', bev=.05); b.box((CX - 1.45, 20.0, AZ + .62), (.8, 1.0, .05), 'red', bev=.012)
    b.box((CX - 1.91, 20.0, AZ + .1), (.03, .7, .5), 'yellow', bev=.008); b.text('HV', (CX - 1.94, 20.0, AZ + .12), .24, 'trim_black', -math.pi / 2, math.pi / 2)
    for sx_ in (-.36, 0, .36):
        for sy_ in (-.44, .44): b.cyl((CX - 1.45 + sx_, 20.0 + sy_, AZ + .66), .03, .035, 'steel_light', 'Z', 6)
    for k in range(3):                                                                                           # HV bushings on the terminal box
        bx = CX - 1.45 + (k - 1) * .28; b.cyl((bx, 20.0, AZ + .66), .13, .09, 'steel_dark', 'Z', 20, bev=.01); b.cyl((bx, 20.0, AZ + .9), .075, .42, 'ivory', 'Z', 20)
        for q in range(5): b.cyl((bx, 20.0, AZ + .76 + q * .08), .115, .025, 'ivory', 'Z', 24)
        b.cyl((bx, 20.0, AZ + 1.13), .06, .07, 'orange', 'Z', 16)
    for yy in (17.4, 19.8):                                                                                      # generator cooling water pipes
        for s in (-1, 1):
            b.sweep([(CX + s * .98, yy, 3.3), (CX + s * 1.3, yy, 3.3), (CX + s * 1.3, yy, 1.14)], .06, 'steel_mid', 16, .14); b.cyl((CX + s * 1.3, yy, 1.03), .11, .05, 'steel_dark', 'Z', 20, bev=.006)
    for s in (-1, 1): b.sweep([(CX + s * 1.3, 17.4, 1.14), (CX + s * 1.3, 19.8, 1.14)], .06, 'steel_mid', 16, .1, caps=False)
    for sx in (-.75, .75):
        for yy in (17.1, 20.1): torus(b, (CX + sx, yy, 3.8), .07, .014, 'yellow', 'Y', 16)                        # hood lifting lugs
    stepped(b, [(21.3, 22.3, .78, .62)], 'steel_light', nbolt=12); bearing(b, 22.35, 22.9)
    b.box((CX, 21.85, AZ + .86), (.5, .6, .26), 'steel_dark', bev=.04); b.cyl((CX, 21.85, AZ + .62), .2, .5, 'orange', 'Y', 28, bev=.01)   # slip-ring housing
    b.box((CX + .55, 22.65, AZ - .55), (.5, .01, .26), 'chalk'); b.text('GEN-3', (CX + .55, 22.66, AZ - .55), .1, 'trim_black', 0, math.pi / 2)
    b.use('SHAFT'); b.cyl((CX, 7.55, AZ), .22, .9, 'steel_light', 'Y', 24); b.cyl((CX, 22.65, AZ), .22, .5, 'steel_light', 'Y', 24)
    b.use('MACH')
    pipe_lagged(b, [(8.4, -.25, 4.9), (8.4, 4.0, 4.9), (8.4, 4.0, 3.55), (CX + .2, 4.0, 3.55), (CX + .2, 4.2, 3.55)], .22, bend=.55)
    b.box((8.4, .25, 4.9), (.46, .3, .46), 'steel_dark', bev=.03)
    valve(b, (8.4, 2.0, 5.2)); b.box((8.4, 2.0, 4.9), (.5, .5, .5), 'steel_dark', bev=.04)
    b.box((8.4, 4.0, 1.7), (.3, .3, 3.0), 'steel_dark', bev=.03); b.box((8.4, 4.0, .04), (.7, .7, .08), 'steel_dark', bev=.02)
    hanger(b, (8.4, 2.0, 5.1)); hanger(b, (8.4, 3.4, 5.1)); hanger(b, (6.6, 4.0, 3.75))
    b.claim((8.1, 0, 4.4), (8.7, 4.1, 5.5))
    b.sweep([(CX - .7, 4.8, 1.55), (CX - 1.3, 4.8, 1.55), (CX - 1.3, 4.8, 1.05)], .035, 'brass', 12, .1)
    b.claim((1.4, 2.0, 0), (7.8, 23.5, 4.8))

# ---------- services ----------
def services(b):
    b.use('MACH')
    b.sweep([(9.5, -.25, .45), (9.5, 8.5, .45), (9.5, 8.5, 1.2), (9.2, 8.8, 1.2)], .09, 'steel_mid', 20, .25)
    for y in (1.5, 3.5, 5.5): b.cyl((9.5, y, .45), .13, .06, 'steel_dark', 'Y', 20, bev=.006); b.box((9.5, y, .2), (.2, .2, .4), 'steel_dark', bev=.012)
    valve(b, (9.5, 7.2, .62), .1)
    b.box((9.0, 8.3, .08), (1.4, 2.4, .16), 'steel_dark', bev=.015)
    b.cyl((9.0, 7.9, .6), .3, 1.0, 'steel_light', 'Y', 36, bev=.008); b.cyl((9.0, 7.35, .6), .35, .14, 'orange', 'Y', 36, bev=.008); b.cyl((9.0, 8.85, .55), .38, .5, 'orange', 'Y', 36, bev=.01)
    b.box((9.0, 9.4, .55), (.2, .1, .3), 'trim_black', bev=.01)
    b.claim((8.2, 6.5, 0), (9.9, 9.6, 1.4))
    b.box((9.0, 16.0, .09), (1.6, 4.4, .18), 'steel_dark', nb=True, bev=.03); b.cyl((9.0, 17.2, .85), .55, 2.0, 'steel_mid', 'Y', 40, bev=.02); b.cyl((9.0, 18.3, .85), .55, .24, 'steel_dark', 'Y', 40, r2=.32)
    b.cyl((9.0, 16.1, .85), .32, .24, 'steel_dark', 'Y', 40, r2=.55)
    b.box((8.28, 17.2, .85), (.03, 1.4, .5), 'chalk', bev=.005); b.box((8.265, 17.2, .85), (.01, .3, .4), 'screen')
    for k in range(3): b.cyl((8.55 + k * .38, 14.6, .55), .15, .7, 'orange' if k else 'orange_dark', 'Z', 28, bev=.008); b.cyl((8.55 + k * .38, 14.6, .93), .17, .05, 'steel_dark', 'Z', 28, bev=.006)
    b.cyl((9.0, 15.7, .5), .28, 1.4, 'steel_light', 'X', 32, bev=.008)
    for y in (16.3, 15.2): b.cyl((8.4, y, .35), .22, .5, 'orange', 'X', 28, bev=.008)
    b.sweep([(8.45, 14.0, .1), (7.4, 14.0, .1), (7.4, 14.0, .6), (7.35, 13.2, .6), (7.35, 13.2, 1.4)], .045, 'brass', 12, .2)
    b.claim((8.0, 13.5, 0), (9.9, 19.1, 1.5)); b.claim((7.2, 13.0, 0), (8.0, 14.3, 1.5))
    b.box((9.6, 10.5, 1.0), (.5, 1.4, 2.0), 'steel_dark', bev=.025); b.box((9.34, 10.5, 1.0), (.03, 1.2, 1.8), 'trim_black', bev=.008)
    for i in range(3):
        for j in range(2): gauge(b, (9.31, 10.1 + .4 * j + .2, 1.25 + i * .32), 'X', .09)
    b.claim((9.0, 9.6, 0), (9.9, 11.4, 2.1))
    b.box((9.75, 20.9, 1.2), (.3, .9, 1.4), 'red', bev=.025); b.box((9.58, 20.9, 1.2), (.03, .7, 1.2), 'red_dark', bev=.01)
    b.box((9.57, 20.9, 1.5), (.02, .5, .3), 'chalk'); b.text('HOSE', (9.56, 20.9, 1.5), .12, 'trim_black', -math.pi / 2, math.pi / 2); b.claim((9.2, 20.3, 0), (9.9, 21.6, 1.9))
    for x in (-3.55, 9.55):
        b.box((x, 12, 3.4), (.36, 23, .04), 'steel_dark', bev=.006)
        for s in (-.17, .17): b.box((x + s, 12, 3.45), (.02, 23, .1), 'steel_dark')
        for y in range(1, 24, 3): hanger(b, (x, y, 3.3), top=3.4)
        for k in range(3): b.box((x + (k - 1) * .09, 12, 3.46), (.05, 22.5, .05), ['rubber', 'rubber', 'red_dark'][k], bev=.008)
    b.box((-2.2, 12, 5.0), (1.0, 22.5, .7), 'steel_light', bev=.03); b.box((-2.2, 12, 4.64), (1.1, 22.5, .03), 'steel_dark')
    for y in range(2, 24, 4): b.box((-2.2, y, 5.0), (1.06, .06, .76), 'steel_mid', bev=.01); hanger(b, (-2.6, y, 4.7), top=6.0); hanger(b, (-1.8, y, 4.7), top=6.0)
    for y in (6, 14, 20): b.box((-2.2, y + 1.2, 4.62), (.7, .7, .04), 'steel_dark', bev=.008); b.box((-2.2, y + 1.2, 4.60), (.62, .02, .03), 'trim_black')

# ---------- controls ----------
def controls(b):
    b.use('MACH')
    for k, yc in enumerate((4.5, 5.65, 6.8)):
        b.box((-3.4, yc, .55), (.8, 1.08, 1.1), 'slate_blue', nb=True, bev=.02); b.box((-3.4, yc, .08), (.84, 1.12, .16), 'trim_black', nb=True, bev=.01)
        b.box((-2.995, yc, .55), (.014, .88, .82), 'slate_dark', bev=.008); b.rod((-2.97, yc + .3, .4), (-2.97, yc + .3, .7), .012, 'steel_light', 10)
        for i in range(4): b.box((-2.992, yc - .25, .3 + i * .05), (.01, .3, .012), 'trim_black')
        b.box((-3.4, yc, 1.12), (.9, 1.1, .05), 'steel_dark', bev=.012)
        b.box((-3.55, yc, 1.55), (.4, 1.06, .8), 'blue_panel', (0, -.45, 0), bev=.014)
        for j in range(2):
            yy = yc - .26 + .52 * j
            gauge(b, (-3.36, yy, 1.62), 'X', .105)
            b.box((-3.36, yy, 1.82), (.02, .15, .05), 'screen' if (j + k) % 2 else 'led_green', bev=.004); b.box((-3.345, yy, 1.5), (.01, .22, .035), 'chalk', (0, -.45, 0))
        for i in range(3): b.cyl((-3.22, yc - .3 + i * .12, 1.25), .014, .05, 'steel_light', 'Z', 10); b.box((-3.22, yc - .3 + i * .12, 1.28), (.012, .012, .035), 'steel_dark')
        b.rod((-3.2, yc + .25, 1.19), (-3.02, yc + .25, 1.38), .014, 'steel_dark', 10); b.sphere((-3.02, yc + .25, 1.4), .035, 'red', 12)
    b.cyl((-3.1, 7.3, 1.17), .1, .05, 'yellow', 'Z', 24, bev=.006); b.cyl((-3.1, 7.3, 1.215), .065, .05, 'red', 'Z', 24, bev=.008)
    for ya, yb_ in ((3.9, 5.8), (6.2, 7.3)): b.box((-3.9, (ya + yb_) / 2, 2.25), (.1, yb_ - ya, .92), 'trim_black', bev=.015)
    cols = ['led_green', 'led_green', 'screen', 'led_green', 'led_red', 'led_green', 'screen', 'led_green']
    for i in range(8):
        if abs(4.2 + i * .4 - 6.0) < .3: continue
        for j in range(3): b.box((-3.842, 4.2 + i * .4, 1.95 + j * .3), (.014, .35, .25), 'trim_black', bev=.006); b.box((-3.835, 4.2 + i * .4, 1.95 + j * .3), (.02, .3, .2), cols[(i + j * 3) % 8], bev=.006); b.text(str(i * 3 + j + 1), (-3.82, 4.2 + i * .4, 1.95 + j * .3), .06, 'trim_black', math.pi / 2, math.pi / 2)
    b.box((-3.9, 5.65, 3.02), (.1, 3.6, .46), 'orange', bev=.02); b.text('TURBINE CONTROL', (-3.84, 5.65, 3.02), .25, 'trim_black', math.pi / 2, math.pi / 2)
    b.box((-2.2, 5.6, .72), (.8, 1.5, .05), 'steel_dark', bev=.012); b.box((-1.795, 5.6, .72), (.012, 1.5, .052), 'orange')
    for dx in (-.35, .35):
        for dy in (-.7, .7): b.box((-2.2 + dx, 5.6 + dy, .36), (.05, .05, .7), 'steel_dark', bev=.006)
    b.box((-2.2, 5.3, .755), (.3, .22, .008), 'paper', (0, 0, .3)); b.box((-2.12, 6.0, .86), (.3, .02, .2), 'trim_black', bev=.008); b.box((-2.12, 6.0, .86), (.26, .005, .16), 'screen_cool')
    b.box((-2.12, 6.0, .77), (.1, .08, .02), 'steel_dark', bev=.005); b.box((-2.38, 5.9, .755), (.36, .12, .015), 'charcoal', bev=.006)
    b.cyl((-2.4, 5.2, .8), .035, .08, 'chalk', 'Z', 16)
    b.cyl((-1.5, 5.6, .46), .22, .06, 'rubber', 'Z', 28, bev=.012); b.box((-1.3, 5.6, .72), (.06, .38, .46), 'rubber', bev=.02); b.cyl((-1.5, 5.6, .24), .035, .42, 'steel_dark', 'Z', 12)
    for a in range(5): b.box((-1.5 + .17 * math.cos(a * 1.2566), 5.6 + .17 * math.sin(a * 1.2566), .04), (.18, .04, .03), 'steel_dark', (0, 0, a * 1.2566), bev=.006)
    b.claim((-3.95, 3.8, 0), (-1.0, 7.5, 3.9))
    for k, x in enumerate((-3.35, -2.3, -1.25)):
        b.box((x, 23.55, 1.1), (.98, .8, 2.2), 'steel_mid', nb=True, bev=.025); b.box((x, 23.145, 1.1), (.9, .012, 2.1), 'steel_dark', bev=.01)
        b.box((x, 23.135, 1.55), (.62, .01, .5), 'chalk'); b.text(['PROT A', 'PROT B', 'EXCITER'][k], (x, 23.13, 1.55), .08, 'trim_black', 0, math.pi / 2)
        for i in range(3): b.cyl((x - .2 + i * .2, 23.13, 1.9), .03, .02, ['led_green', 'screen', 'led_green'][(i + k) % 3], 'Y', 14)
        for i in range(5): b.box((x, 23.135, .35 + i * .07), (.5, .01, .02), 'backing')
        b.rod((x + .38, 23.1, .95), (x + .38, 23.1, 1.25), .014, 'steel_light', 10)
        b.box((x, 23.55, 2.25), (.98, .8, .1), 'steel_dark', bev=.012)
    b.claim((-3.9, 22.8, 0), (-.7, 24.0, 2.4))
    duct(b, [(CX - 1.9, 20.0, AZ + .1), (CX - 2.5, 20.0, AZ + .1), (CX - 2.5, 20.0, 3.88), (-3.8, 20.0, 3.88), (-3.8, 24.25, 3.88)], .4, .3)
    b.box((-3.8, 24.5, 3.88), (.4, .6, .3), 'steel_light', bev=.012); b.box((-4.1, 24.85, 3.88), (.4, .6, .3), 'steel_light', (0, 0, -.9), bev=.012); b.box((-4.32, 25.0, 3.88), (.4, 1.0, .3), 'steel_mid', bev=.012)
    for y in (21.5, 23.0): hanger(b, (-3.8, y, 3.7), top=6.0)
    hanger(b, (-2.0, 20.0, 3.7), top=6.0); hanger(b, (0.8, 20.0, 3.7), top=6.0)
    b.text('HV BUS  /  U03', (-3.2, 19.98, 4.15), .17, 'yellow', 0, math.pi / 2)

# ---------- maintenance bay ----------
def maintenance(b):
    b.use('MACH')
    rx, rz = -.9, .62
    for y in (14.6, 19.4):
        b.prism([(-.48, 0), (.48, 0), (.3, .58), (-.3, .58)], .24, 'steel_dark', (rx, y, 0), True, 'Y', bev=.025); b.box((rx, y, .6), (.62, .22, .05), 'orange_dark', bev=.01)
    b.cyl((rx, 17.0, rz + .14), .17, 5.8, 'steel_light', 'Y', 32, bev=.008)
    for i, yy in enumerate((15.3, 15.75, 16.2, 16.65, 17.1, 17.55, 18.0, 18.45)):
        R = .55 - .02 * abs(i - 3.5)
        b.cyl((rx, yy, rz + .14), R, .36, 'steel_mid' if i % 2 else 'steel_light', 'Y', 48, bev=.01)
        if i in (1, 3, 5, 6):                                                   # turbine blades on four rotor discs
            for k in range(16):
                a = 2 * math.pi * k / 16
                b.box((rx + (R + .05) * math.cos(a), yy, rz + .14 + (R + .05) * math.sin(a)), (.18, .26, .06), 'steel_dark', (0, -a, 0), bev=.004)
    for y in (15.5, 18.5): torus(b, (rx, y, rz + .74), .06, .012, 'yellow', 'X', 16)
    b.claim((-1.9, 14.2, 0), (.3, 19.7, 1.3))
    b.box((-3.35, 15.9, .46), (.7, 2.2, .07), 'steel_dark', bev=.014); b.box((-3.0, 15.9, .46), (.012, 2.2, .075), 'orange')
    for y in (14.9, 16.9): b.box((-3.35, y, .22), (.62, .06, .44), 'steel_dark', bev=.008)
    b.box((-3.35, 15.9, .12), (.62, 2.1, .04), 'steel_dark', bev=.008)
    b.box((-3.45, 15.1, .6), (.18, .26, .14), 'steel_dark', bev=.012); b.box((-3.45, 15.1, .7), (.1, .26, .05), 'steel_mid', bev=.008)
    b.box((-3.78, 16.0, 1.5), (.03, 2.9, 1.0), 'slate_blue', bev=.01); b.box((-3.7, 16.0, 1.98), (.18, 2.9, .035), 'wood', bev=.008)
    for i in range(6):                                                         # tidy tool wall: wrenches and screwdrivers on a rail
        y = 14.85 + i * .46
        b.box((-3.755, y, 1.62), (.008, .075, .5), 'trim_black'); b.box((-3.755, y + .22, 1.5), (.008, .08, .3), 'trim_black')
        b.box((-3.74, y, 1.62), (.02, .035, .42), 'steel_mid', bev=.006); b.box((-3.74, y, 1.4), (.02, .09, .08), 'steel_mid', bev=.006); b.box((-3.74, y, 1.37), (.02, .04, .05), 'wood_dark')
        b.box((-3.74, y + .22, 1.5), (.025, .04, .24), ['orange', 'yellow'][i % 2], bev=.008); b.box((-3.74, y + .22, 1.34), (.012, .012, .1), 'steel_light')
    b.claim((-3.9, 14.2, 0), (-2.9, 17.9, 2.3))
    for yc in (19.9, 21.2):
        for z in (.1, .7, 1.3, 1.9): b.box((-3.45, yc, z), (.6, 1.1, .035), 'orange_dark', bev=.006)
        for y in (yc - .53, yc + .53):
            for dx in (0, .6): b.box((-3.7 + dx, y, 1.0), (.045, .045, 2.0), 'steel_dark', bev=.005)
        for i, z in enumerate((.1, .7, 1.3)): b.box((-3.45, yc + (.15 if i % 2 else -.15), z + .15), (.4, .4, .26), ['wood', 'steel_mid', 'orange'][i], bev=.01)
    b.claim((-3.9, 19.2, 0), (-3.0, 21.9, 2.2))
    b.box((.2, 21.2, .45), (.6, .9, .05), 'steel_dark', bev=.01)
    for dx in (-.25, .25):
        for dy in (-.35, .35): b.cyl((.2 + dx, 21.2 + dy, .1), .08, .06, 'rubber', 'X', 20)
    b.cyl((.1, 21.5, .85), .1, 1.0, 'steel_light', 'Z', 24, bev=.006); b.sphere((.1, 21.5, 1.35), .1, 'steel_light', 14)
    b.cyl((.3, 21.5, .8), .1, .9, 'red', 'Z', 24, bev=.006); b.sphere((.3, 21.5, 1.25), .1, 'red', 14); b.box((.2, 20.95, .6), (.3, .25, .3), 'orange', bev=.015)
    b.claim((-.3, 20.6, 0), (.7, 22.0, 1.4))
