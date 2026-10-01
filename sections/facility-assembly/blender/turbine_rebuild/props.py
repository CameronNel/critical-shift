"""Detail families: wear, broken stuff, tools, cables, plugs, scaffolding, desks, roof damage, signage ... (group PROPS)."""
import math
from mathutils import Vector

WALL = {   # frame origin, rz, wall-plane coordinate fn(world y/x -> local u), range of the free coordinate
    'W': (((-4, 24), -math.pi / 2), lambda t: 24 - t, 'y'),
    'E': (((10, 0), math.pi / 2), lambda t: t, 'y'),
    'S': (((0, 0), 0.0), lambda t: t, 'x'),
    'N': (((0, 24), math.pi), lambda t: -t, 'x'),
}

def near_col(t, tol=.5): return any(abs(t - y) < tol for y in (2, 6, 10, 14, 18, 22))

def wall_spot(b, w, h, z, sides='WESN', tries=400):
    for _ in range(tries):
        s = b.rng.choice(sides)
        frame, fu, ax = WALL[s]
        if s in 'WE':
            t = b.rng.uniform(.8, 23.2)
            if near_col(t, .5 + w / 2): continue
            lo, hi = ((-4.0, t - w / 2, z - h / 2), (-3.7, t + w / 2, z + h / 2)) if s == 'W' else ((9.7, t - w / 2, z - h / 2), (10.0, t + w / 2, z + h / 2))
            if z + h / 2 > 4.4 and (s == 'E' or (s == 'W' and any(abs(t - c) < 1.4 for c in (4, 12, 20)))): continue
        else:
            t = b.rng.uniform(-3.4, 9.4)
            if (-1.5 < t < 1.5 and z < 3.2) or (s == 'S' and (t > 8 and z > 4.4) ): continue
            lo, hi = ((t - w / 2, 0, z - h / 2), (t + w / 2, .3, z + h / 2)) if s == 'S' else ((t - w / 2, 23.7, z - h / 2), (t + w / 2, 24.0, z + h / 2))
        if b.free(lo, hi, .08): b.claim(lo, hi); return frame, fu(t)
    return None

def spot(b, sx, sy, h=.6, region=((-3.6, 9.6), (.8, 23.2)), tries=600):
    for _ in range(tries):
        x, y = b.rng.uniform(*region[0]), b.rng.uniform(*region[1])
        lo, hi = (x - sx / 2, y - sy / 2, 0), (x + sx / 2, y + sy / 2, h)
        if b.free(lo, hi, .1): b.claim(lo, hi); return x, y
    return None

def build(b):
    b.use('PROPS'); R = b.rng
    # ---- 1/2/3. worn floor: scuffs, oil, broken + cracked tile shards, hazard edging, walkway lines ----
    for _ in range(70):
        x, y = R.uniform(-3.8, 9.8), R.uniform(.3, 23.7)
        b.flat((x, y), R.uniform(.3, 1.2), R.uniform(.2, .8), R.choice(['tile_worn', 'tile_oil', 'primer', 'tile_crack']), R.uniform(0, 3.1), z=.0075 + R.random() * .0015)
    for _ in range(14):
        x, y = R.uniform(-3.6, 9.6), R.uniform(.6, 23.4)
        if 1.9 < x < 7.3 and 2.5 < y < 23.1: continue
        b.flat((x, y), .55, .55, 'primer', R.uniform(0, 3), z=.0085)
        for k in range(4): b.box((x + R.uniform(-.2, .2), y + R.uniform(-.2, .2), .02), (R.uniform(.1, .22), R.uniform(.1, .22), .035), 'tile_crack', (R.uniform(-.2, .2), R.uniform(-.2, .2), R.uniform(0, 3)))
    for i in range(30):                                                    # hazard chevrons hugging the foundation foot
        for sx, sy, ax in ((1.55, 2.6 + i * .66, 'y'), (7.65, 2.6 + i * .66, 'y')):
            if sy < 23.0: b.box((sx, sy, .008), (.25, .33, .004), 'yellow' if i % 2 == 0 else 'charcoal', (0, 0, .0), nb=True)
    for lx in (-1.6, 1.6): b.flat((lx, 12), .1, 20, 'yellow_worn', 0, z=.009)          # walkway edge lines
    for sx in (-3.9, 9.9): pass
    # ---- 4. hanging cables from the roof ----
    for _ in range(9):
        x, y = R.uniform(-3, 9), R.uniform(1, 23); dx, dy = R.uniform(-2.5, 2.5), R.uniform(1.5, 3.5); sag = R.uniform(.5, 1.1); prev = None
        for i in range(8):
            t = i / 7; p = (x + dx * t, y + dy * t, 5.95 - sag * 4 * t * (1 - t) - .35 * t)
            if prev: b.rod(prev, p, .028, 'rubber', 5)
            if prev and i % 3 == 0: b.box(p, (.1, .1, .05), 'steel_mid')
            prev = p
    # ---- 5. sockets with plugged leads, 7. junction boxes, 15. extinguishers, 19. signs, 16. hose reel, clocks, notices ----
    for _ in range(14):
        w = wall_spot(b, .3, .3, .55)
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.box((u, .03, .55), (.16, .06, .16), 'steel_light'); b.box((u, .075, .55), (.1, .03, .1), 'charcoal')
            for dx in (-.025, .025): b.box((u + dx, .1, .55), (.02, .02, .03), 'brass')
            if R.random() < .5:
                b.box((u, .13, .55), (.07, .07, .09), 'red'); b.rod((u, .17, .55), (u + R.uniform(-.4, .4), .3, .1), .02, 'rubber', 5)
    for _ in range(8):
        w = wall_spot(b, .5, .7, 1.8)
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.box((u, .09, 1.8), (.4, .16, .5), 'steel_dark'); b.box((u, .18, 1.8), (.32, .03, .42), 'orange_worn'); b.box((u + .12, .2, 1.85), (.05, .02, .12), 'chalk')
            b.rod((u + .1, .1, 1.55), (u + .1, .1, .0), .025, 'steel_mid', 6)
    for _ in range(3):
        w = wall_spot(b, .4, 1.0, 1.2)
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.box((u, .04, 1.2), (.12, .03, .6), 'steel_dark'); b.cyl((u, .16, 1.05), .09, .5, 'red', 'Z', 10); b.cyl((u, .16, 1.34), .04, .08, 'steel_dark', 'Z', 8)
            b.box((u, .09, 1.7), (.34, .02, .3), 'red'); b.box((u, .1, 1.7), (.18, .01, .06), 'chalk')
    for _ in range(7):
        w = wall_spot(b, .6, .45, 2.5)
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.box((u, .03, 2.5), (.5, .03, .35), 'yellow'); b.box((u, .05, 2.5), (.42, .01, .05), 'charcoal'); b.box((u, .05, 2.4), (.3, .01, .035), 'charcoal'); b.box((u, .05, 2.6), (.34, .01, .05), 'charcoal')
    for _ in range(2):
        w = wall_spot(b, .8, .8, 1.3)
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.cyl((u, .25, 1.3), .35, .22, 'red', 'Y', 10); b.cyl((u, .25, 1.3), .12, .3, 'steel_dark', 'Y', 8); b.box((u, .07, 1.3), (.1, .1, .9), 'steel_dark')
            b.rod((u, .3, 1.0), (u + .3, .5, .5), .035, 'rubber', 5)
    w = wall_spot(b, .5, .5, 3.0, 'S')                                                  # wall clock
    if w:
        (org, rz), u = w[0], w[1]
        with b.push(org, rz): b.cyl((u, .05, 3.0), .22, .05, 'chalk', 'Y', 14); b.box((u, .08, 3.07), (.015, .01, .16), 'charcoal'); b.box((u + .04, .08, 3.0), (.1, .01, .015), 'charcoal')
    for _ in range(3):                                                                    # notice boards with pinned papers
        w = wall_spot(b, 1.0, .8, 1.9, 'WENS')
        if not w: continue
        (org, rz), u = w[0], w[1]
        with b.push(org, rz):
            b.box((u, .03, 1.9), (1.0, .03, .8), 'wood_dark'); b.box((u, .05, 1.9), (.92, .01, .72), 'green')
            for i in range(5): b.box((u - .35 + i * .17, .065, 1.95 + R.uniform(-.1, .1)), (.12, .005, .16), 'paper', (0, 0, R.uniform(-.2, .2)))
    # first-aid and eyewash
    w = wall_spot(b, .4, .4, 1.5, 'E')
    if w:
        (org, rz), u = w[0], w[1]
        with b.push(org, rz): b.box((u, .07, 1.5), (.4, .12, .4), 'green'); b.box((u, .14, 1.5), (.2, .02, .06), 'chalk'); b.box((u, .14, 1.5), (.06, .02, .2), 'chalk')
    # ---- 6. scaffolding bay ----
    sc = spot(b, 2.6, 1.4, 3.0, region=((-3.4, -2.4), (9.0, 12.5)))
    if sc:
        x, y = sc; w, d, h = 2.4 if False else 1.2, 2.4, 3.0
        for ix in (-w / 2, w / 2):
            for iy in (-d / 2, d / 2): b.rod((x + ix, y + iy, 0), (x + ix, y + iy, h), .032, 'steel_mid', 6)
        for z in (.4, 1.5, 2.6):
            for iy in (-d / 2, d / 2): b.rod((x - w / 2, y + iy, z), (x + w / 2, y + iy, z), .026, 'steel_mid', 6)
            for ix in (-w / 2, w / 2): b.rod((x + ix, y - d / 2, z), (x + ix, y + d / 2, z), .026, 'steel_mid', 6)
        for z in (1.5, 2.6): b.box((x, y, z + .035), (w, d, .05), 'wood')
        for ix in (-w / 2, w / 2): b.rod((x + ix, y - d / 2, .4), (x + ix, y + d / 2, 2.6), .02, 'steel_dark', 4)
        b.box((x + .2, y + .6, 1.62), (.3, .3, .22), 'orange'); b.rod((x - .3, y - .8, 2.65), (x - .5, y - 1.1, .05), .012, 'rubber', 4)
        b.cyl((x, y + 1.1, .03), .09, .06, 'steel_dark', 'Z', 6)
    # ---- 7. desks with chairs, lamps and papers (control-room overflow near D02 east, one south) ----
    for rect, n in (((6.0, 9.6, 21.0, 23.4), 1), ((7.6, 9.6, 1.0, 3.5), 1), ((-3.4, -1.8, 9.6, 13.0), 0)):
        sp = spot(b, 1.5, .8, 1.0, region=((rect[0], rect[1]), (rect[2], rect[3])))
        if not sp: continue
        x, y = sp
        b.box((x, y, .74), (1.4, .7, .05), 'wood'); [b.box((x + dx, y + dy, .36), (.05, .05, .72), 'steel_dark') for dx in (-.65, .65) for dy in (-.3, .3)]
        b.box((x + .3, y, .77), (.3, .22, .01), 'paper', (0, 0, R.uniform(-.4, .4))); b.cyl((x - .5, y + .2, .78), .05, .04, 'steel_dark', 'Z', 6)
        b.rod((x - .5, y + .2, .78), (x - .4, y + .2, 1.1), .01, 'steel_dark', 4); b.box((x - .37, y + .2, 1.12), (.12, .06, .04), 'yellow')
        b.box((x, y - .65, .45), (.4, .4, .05), 'rubber'); b.box((x, y - .83, .72), (.4, .05, .4), 'rubber'); b.cyl((x, y - .65, .22), .04, .45, 'steel_dark', 'Z', 6)
    # ---- 9. loose tools / 10. fallen tools ----
    for _ in range(5):
        sp = spot(b, .8, .5, .2)
        if not sp: continue
        x, y = sp; a = R.uniform(0, 3.1)
        b.box((x, y, .02), (.5, .04, .03), 'steel_light', (0, 0, a)); b.box((x + .25 * math.cos(a), y + .25 * math.sin(a), .02), (.1, .1, .03), 'steel_light', (0, 0, a))
        b.box((x + .2, y + .2, .03), (.3, .05, .05), 'wood', (0, 0, a + 1)); b.box((x + .2 + .15 * math.cos(a + 1), y + .2 + .15 * math.sin(a + 1), .04), (.1, .06, .06), 'steel_mid', (0, 0, a + 1))
    # ---- 12. pallets & crates / 11. drums / 20. gas cylinders ----
    for _ in range(4):
        sp = spot(b, 1.1, .9, 1.4)
        if not sp: continue
        x, y = sp
        for dx in (-.4, 0, .4): b.box((x + dx, y, .06), (.1, .8, .1), 'wood_dark')
        for dy in (-.3, 0, .3): b.box((x, y + dy, .13), (1.0, .12, .03), 'wood')
        for k in range(R.randint(1, 3)): b.box((x + R.uniform(-.1, .1), y, .3 + .32 * k), (.7, .6, .3), R.choice(['wood', 'orange_worn', 'steel_worn']), (0, 0, R.uniform(-.1, .1)))
    for _ in range(7):
        sp = spot(b, .6, .6, .9)
        if not sp: continue
        x, y = sp; c = R.choice(['red', 'yellow', 'steel_mid', 'orange'])
        if R.random() < .25: b.cyl((x, y, .27), .27, .85, c, 'X', 10); b.flat((x + .7, y), .9, .7, 'tile_oil', 0, z=.009)
        else: b.cyl((x, y, .45), .27, .9, c, 'Z', 10); b.cyl((x, y, .91), .27, .03, 'steel_dark', 'Z', 10); b.box((x, y, .6), (.56, .56, .035), 'steel_dark') if False else b.cyl((x, y, .6), .285, .04, 'steel_dark', 'Z', 10)
    for _ in range(3):
        sp = spot(b, .9, .5, 1.5)
        if not sp: continue
        x, y = sp
        for k in range(2): b.cyl((x - .2 + .4 * k, y, .7), .1, 1.3, ['orange', 'steel_light'][k], 'Z', 8); b.cyl((x - .2 + .4 * k, y, 1.4), .05, .1, 'steel_dark', 'Z', 6)
        b.box((x, y, .04), (.9, .4, .04), 'steel_dark'); b.box((x, y, .6), (.85, .03, .05), 'yellow')
    # ---- 18. ladder, 13. broken pipe + puddle, floor cables with ramps ----
    lx = spot(b, 1.0, 1.0, 2.8, region=((8.3, 9.4), (22.0, 23.2)))
    if lx:
        x, y = lx
        for dy in (-.25, .25): b.rod((x + .1, y + dy, 0), (x + .75, y + dy, 2.6), .022, 'orange', 4)
        for k in range(8): z = .3 + k * .3; b.rod((x + .1 + .65 * z / 2.6, y - .25, z), (x + .1 + .65 * z / 2.6, y + .25, z), .015, 'steel_mid', 4)
    sp = spot(b, 1.4, 1.4, 4.0, region=((-.8, 1.6), (7.5, 10.5)))
    if sp:
        x, y = sp
        b.cyl((x, y, 4.9), .14, 2.1, 'lagging', 'Z', 8); b.cyl((x, y, 3.85), .21, .06, 'steel_dark', 'Z', 8)
        b.rod((x, y, 3.85), (x + .5, y + .2, 3.2), .12, 'lagging', 6); b.box((x + .55, y + .22, 3.15), (.35, .1, .3), 'primer', (.5, 0, .4))
        b.flat((x + .5, y + .2), 1.1, .8, 'tile_oil', .3, z=.01)
    for _ in range(6):
        x0, y0 = R.uniform(-3.5, 9), R.uniform(1, 22); pts = [(x0, y0), (x0 + R.uniform(-2, 2), y0 + R.uniform(1, 4)), (x0 + R.uniform(-2, 2), y0 + R.uniform(4, 7))]
        if not all(b.free((p[0] - .1, p[1] - .1, 0), (p[0] + .1, p[1] + .1, .1), .05) and -3.9 < p[0] < 9.9 and .3 < p[1] < 23.8 for p in pts): continue
        for a, c in zip(pts, pts[1:]):
            b.rod((a[0], a[1], .035), (c[0], c[1], .035), .035, 'rubber', 6)
            m = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2); b.box((m[0], m[1], .03), (.35, .22, .05), 'yellow', (0, 0, math.atan2(c[1] - a[1], c[0] - a[0])))
    # ---- extra broken / lived-in props ----
    sp = spot(b, .6, .6, .9)
    if sp: x, y = sp; b.box((x, y, .12), (.45, .45, .05), 'rubber', (1.3, 0, .6)); b.box((x + .05, y, .32), (.45, .05, .4), 'rubber', (1.3, 0, .6)); b.cyl((x + .1, y + .2, .1), .04, .5, 'steel_dark', 'X', 6)   # toppled chair
    for _ in range(2):                                                                    # wet-floor A-frame sign + cones
        sp = spot(b, .5, .5, .8)
        if not sp: continue
        x, y = sp
        for s in (-1, 1): b.box((x, y + s * .12, .35), (.35, .02, .6), 'yellow', (s * .3, 0, 0))
        b.box((x, y, .6), (.36, .27, .02), 'yellow')
    for _ in range(3):
        sp = spot(b, .3, .3, .5)
        if not sp: continue
        x, y = sp; b.cyl((x, y, .22), .13, .44, 'orange', 'Z', 10, r2=.045); b.box((x, y, .01), (.34, .34, .02), 'rubber'); b.cyl((x, y, .2), .105, .08, 'chalk', 'Z', 10)
    for _ in range(3):                                                                    # waste bins with paper
        sp = spot(b, .45, .45, .7)
        if not sp: continue
        x, y = sp; b.cyl((x, y, .3), .22, .6, 'steel_mid', 'Z', 10, r2=.19); b.box((x + .05, y, .62), (.12, .1, .1), 'paper', (.3, .4, .2))
    sp = spot(b, 1.0, .6, 1.0)
    if sp: x, y = sp; b.box((x, y, .6), (.9, .55, .06), 'steel_dark'); b.box((x, y, .85), (.9, .04, .5), 'steel_dark', nb=False) if False else None; [b.cyl((x + dx, y + dy, .12), .06, .08, 'rubber', 'X', 8) for dx in (-.4, .4) for dy in (-.22, .22)]; b.box((x, y - .27, .9), (.9, .04, .5), 'steel_dark'); b.box((x + .1, y, .7), (.4, .3, .1), 'orange')  # parts trolley
    sp = spot(b, 1.4, .6, 1.4, region=((8.6, 9.6), (3, 6)))
    if sp: x, y = sp; b.box((x, y, .8), (.9, .5, 1.6), 'red_dark'); [b.box((x - .46, y, .3 + i * .4), (.02, .45, .3), 'red') for i in range(3)]; [b.box((x - .47, y, .3 + i * .4), (.01, .2, .03), 'steel_light') for i in range(3)]  # tool chest
    # ---- 17. ceiling: stains, loose / hanging panels, exposed purlins and one broken pendant ----
    for _ in range(7):
        x, y = R.uniform(-3, 9), R.uniform(1, 23); sx, sy = R.uniform(.8, 1.6), R.uniform(.6, 1.2)
        b.box((x, y, 7.16), (sx, sy, .004), R.choice(['rust', 'primer', 'tile_oil']), (0, 0, R.uniform(0, 3)), nt=False)
        if R.random() < .5:
            b.box((x + .3, y, 6.9), (.9, .5, .02), 'steel_worn', (R.uniform(.3, .6), 0, R.uniform(-.3, .3))); b.rod((x - .3, y - .3, 7.12), (x + .6, y + .4, 7.12), .035, 'steel_dark', 4)
    # ---- ceiling fixtures: emissive lamp bodies (light sources are in lights.py) ----
    for y in (4, 8, 12, 16, 20):
        for x in (-1.2, 4.6, 8.6):
            if abs(x - 4.6) < .01 and abs(y - 10) < 3: pass
            b.box((x, y, 5.35), (1.2, .22, .08), 'steel_dark'); b.box((x, y, 5.3), (1.1, .15, .02), 'lamp')
            b.rod((x - .5, y, 5.4), (x - .5, y, 6.06), .008, 'steel_dark', 4); b.rod((x + .5, y, 5.4), (x + .5, y, 6.06), .008, 'steel_dark', 4)
    b.box((2.0, 20.5, 5.0), (1.2, .22, .08), 'steel_dark', (.9, 0, 0)); b.box((2.0, 20.5, 4.95), (1.1, .15, .02), 'lamp', (.9, 0, 0))   # dangling, broken-hinge lamp
    b.rod((1.5, 20.5, 5.35), (1.5, 20.5, 6.06), .008, 'steel_dark', 4)
