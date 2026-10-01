"""Curated set dressing (v3). Deliberate placements only: signage, notices, safety gear, a working desk, tidy storage, and a few
storytelling wear marks. Text convention: in wall frames text faces +Y (into the room) with rz=pi, rx=pi/2."""
import math
from mathutils import Vector

FR = {'W': (((-4, 24), -math.pi / 2), lambda t: 24 - t), 'E': (((10, 0), math.pi / 2), lambda t: t),
      'S': (((0, 0), 0.0), lambda t: t), 'N': (((0, 24), math.pi), lambda t: -t)}

def wt(b, s, x, z, size, sw='trim_black', y=.0):
    b.text(s, (x, y, z), size, sw, math.pi, math.pi / 2)

def frame_box(b, u, z, w, h, fsw='trim_black', t=.035):
    b.box((u, .03, z), (w, .06, h), fsw, bev=.012)

def poster(b, u, z, kind):
    frame_box(b, u, z, .62, .86); b.box((u, .062, z), (.54, .01, .78), 'poster_a')
    if kind == 0:
        for i, (r, sw) in enumerate(((.2, 'poster_b'), (.14, 'poster_c'), (.08, 'poster_a'))): b.cyl((u, .07 + i * .002, z + .06), r, .004, sw, 'Y', 40)
        b.box((u, .07, z - .27), (.4, .003, .04), 'poster_b')
    else:
        b.prism([(-.18, -.12), (.18, -.12), (0, .2)], .004, 'poster_b', (u, .07, z), True, 'Y'); b.cyl((u, .071, z + .2), .05, .004, 'poster_c', 'Y', 24)

def socket(b, u, z, plug=False):
    b.box((u, .02, z), (.13, .04, .13), 'chalk', bev=.01); b.box((u, .045, z), (.1, .012, .1), 'sand_dark', bev=.006)
    for dx in (-.022, .022): b.box((u + dx, .054, z + .01), (.012, .01, .03), 'brass')
    b.cyl((u, .054, z - .03), .008, .01, 'brass', 'Y', 8)
    if plug:
        b.box((u, .09, z), (.07, .09, .09), 'red', bev=.012)
        b.sweep([(u, .13, z), (u, .2, z), (u + .15, .2, z - .35), (u + .55, .3, .06)], .014, 'rubber', 10, .12)

def extinguisher(b, u):
    b.box((u, .02, 1.2), (.1, .04, .5), 'steel_dark', bev=.008); b.box((u, .07, 1.26), (.3, .02, .05), 'steel_dark', bev=.006)
    b.cyl((u, .17, 1.05), .09, .5, 'red', 'Z', 28, bev=.01); b.sphere((u, .17, 1.3), .09, 'red', 16); b.cyl((u, .17, 1.38), .03, .08, 'steel_dark', 'Z', 12)
    b.sweep([(u + .03, .17, 1.4), (u + .12, .17, 1.38), (u + .14, .2, 1.0)], .01, 'rubber', 8, .06)
    b.box((u, .03, 1.85), (.34, .03, .3), 'red', bev=.01); b.cyl((u, .05, 1.85), .06, .006, 'chalk', 'Y', 16)

def puddle(b, x, y, rx, ry, sw, z=.0085, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    ring = [((rx * math.cos(2 * math.pi * i / 28)) * c - (ry * math.sin(2 * math.pi * i / 28)) * s, (rx * math.cos(2 * math.pi * i / 28)) * s + (ry * math.sin(2 * math.pi * i / 28)) * c) for i in range(28)]
    b.prism(ring, .004, sw, (x, y, z), True, 'Z')

def vent(b, u, z, w=.9, h=.5):
    b.box((u, .03, z), (w + .1, .06, h + .1), 'trim_black', bev=.012); b.box((u, .062, z), (w, .01, h), 'backing')
    for k in range(6): b.box((u, .08, z - h / 2 + .06 + k * (h - .12) / 5), (w - .06, .02, .03), 'steel_dark', (math.radians(-28), 0, 0), bev=.004)
    b.box((u, .09, z), (.03, .02, h), 'steel_dark')

def build(b):
    b.use('PROPS'); R = b.rng
    # --- signage hung over the bay and on the foundation ---
    b.box((-1.2, 13.7, 4.25), (2.6, .05, .5), 'trim_black', bev=.014)
    for sgn, rz_ in ((-1, 0), (1, math.pi)): b.text('MAINTENANCE BAY', (-.95, 13.7 + (.032 if sgn == 1 else -.032), 4.25), .112, 'chalk', rz_, math.pi / 2)
    for sgn in (-1, 1):                                                                                  # gear icon, both faces
        yf = 13.7 + sgn * .033
        b.cyl((-2.2, yf, 4.25), .13, .008, 'yellow', 'Y', 24)
        for k in range(8): b.box((-2.2 + .15 * math.cos(k * math.pi / 4), yf, 4.25 + .15 * math.sin(k * math.pi / 4)), (.06, .008, .06), 'yellow', (0, k * math.pi / 4 * -1, 0))
        b.cyl((-2.2, yf + sgn * .005, 4.25), .055, .008, 'trim_black', 'Y', 16)
    for dx in (-1.1, 1.1):                                                                                # chains
        for k in range(int(1.7 / .07)): b.box((-1.2 + dx, 13.7, 4.5 + k * .07), (.02, .012 if k % 2 else .03, .06), 'steel_mid')
    b.box((7.215, 12.6, .55), (.03, .9, .22), 'yellow', bev=.008); b.text('EXHAUST  U04', (7.235, 12.6, .55), .1, 'trim_black', math.pi / 2, math.pi / 2)
    # --- west wall: notice board, posters, first aid, conduit ---
    (o, rz), fu = FR['W']
    with b.push(o, rz):
        u = fu(9.4)
        b.box((u, .04, 1.75), (1.3, .08, .95), 'wood_dark', bev=.02); b.box((u, .085, 1.75), (1.18, .01, .83), 'green')
        wt(b, 'TURBINE LOG', u, 2.08, .08, 'chalk', .092)
        for i, (dx, dz, w, h, sw) in enumerate(((-.38, 1.75, .3, .42, 'paper'), (0.0, 1.8, .32, .46, 'paper'), (.38, 1.72, .3, .38, 'poster_c'), (-.2, 1.5, .24, .16, 'paper'), (.25, 1.5, .26, .16, 'paper'))):
            b.box((u + dx, .1, dz), (w, .004, h), sw, (0, 0, math.radians(R.uniform(-3, 3))))
            b.cyl((u + dx, .104, dz + h / 2 - .03), .012, .008, 'red', 'Y', 10)
        poster(b, fu(11.2), 1.8, 0); poster(b, fu(12.3), 1.8, 1)
        u = fu(13.3); b.box((u, .06, 1.5), (.4, .12, .4), 'green', bev=.02); b.box((u, .125, 1.5), (.2, .01, .06), 'chalk'); b.box((u, .125, 1.5), (.06, .01, .2), 'chalk')
        for t in (8.4, 10.1, 12.0): socket(b, fu(t), .5, plug=(t == 10.1))
        extinguisher(b, fu(3.0))
        b.rod((fu(8.0), .04, 2.9), (fu(13.5), .04, 2.9), .022, 'steel_mid', 12)
        for t in (8.4, 10.2, 12.0, 13.4): b.box((fu(t), .035, 2.9), (.06, .05, .08), 'steel_dark', bev=.006)
        b.box((fu(13.5), .08, 2.9), (.18, .14, .2), 'steel_dark', bev=.012); b.rod((fu(13.5), .08, 2.8), (fu(13.5), .08, 1.9), .022, 'steel_mid', 12)
    # --- east wall: extinguisher + hose reel ---
    (o, rz), fu = FR['E'];
    with b.push(o, rz): extinguisher(b, fu(5.0))
    (o, rz), fu = FR['S']
    with b.push(o, rz):
        b.cyl((fu(6.7), .25, 1.3), .33, .2, 'red', 'Y', 36, bev=.008); b.cyl((fu(6.7), .25, 1.3), .14, .26, 'steel_dark', 'Y', 20); b.box((fu(6.7), .07, 1.3), (.1, .1, .8), 'steel_dark', bev=.01)
        b.sweep([(fu(6.7) + .1, .32, 1.0), (fu(6.7) + .3, .5, .55), (fu(6.7) + .25, .6, .08)], .03, 'rubber', 12, .15)
        b.cyl((fu(3.0), .05, 3.4), .22, .05, 'chalk', 'Y', 36, bev=.006); b.box((fu(3.0), .08, 3.47), (.012, .01, .15), 'trim_black'); b.box((fu(3.0) + .05, .08, 3.4), (.09, .01, .012), 'trim_black')
    # --- wayfinding on the south wall, tool trolley in the bay ---
    (o, rz), fu = FR['S']
    with b.push(o, rz):
        b.box((fu(5.5), .04, 2.6), (1.8, .05, .5), 'trim_black', bev=.014); wt(b, 'TURBINE HALL', fu(5.5) - .2, 2.6, .12, 'chalk', .066)
        b.prism([(-.12, -.12), (.12, 0), (-.12, .12)], .006, 'yellow', (fu(5.5) + .68, .066, 2.6), True, 'Y')
    tx, ty = .75, 13.0
    b.box((tx, ty, .62), (.9, .5, .05), 'steel_dark', bev=.01); b.box((tx, ty, .27), (.86, .46, .03), 'steel_dark', bev=.008)
    for dx in (-.4, .4):
        for dy in (-.2, .2): b.rod((tx + dx, ty + dy, .08), (tx + dx, ty + dy, .96), .014, 'steel_mid', 10)
    for dx in (-.4, .4):
        for dy in (-.2, .2): b.cyl((tx + dx, ty + dy, .05), .05, .04, 'rubber', 'X', 16)
    b.box((tx, ty - .24, .88), (.9, .02, .6), 'steel_dark', bev=.008); b.box((tx - .2, ty, .72), (.3, .3, .14), 'orange', bev=.015); b.box((tx + .2, ty, .74), (.3, .25, .18), 'wood', bev=.015)
    b.box((tx, ty, .35), (.3, .3, .12), 'steel_light', bev=.012); b.cyl((tx + .3, ty + .1, .31), .04, .24, 'red', 'Z', 14); b.sphere((tx + .3, ty + .1, .44), .04, 'red', 10)
    # --- north wall: working desk with a monitor, mug, lamp and chair; pinned poster ---
    (o, rz), fu = FR['N']
    with b.push(o, rz):
        u = fu(8.0)
        b.box((u, .38, .74), (1.5, .72, .05), 'wood', bev=.012)
        for dx in (-.68, .68):
            for dy in (.08, .68): b.box((u + dx, dy, .36), (.05, .05, .7), 'steel_dark', bev=.006)
        b.box((u, .62, .775), (.4, .24, .012), 'charcoal', bev=.006)
        b.box((u + .05, .68, .93), (.5, .03, .3), 'trim_black', bev=.012); b.box((u + .05, .700, .93), (.46, .006, .26), 'screen_cool'); b.box((u + .05, .704, .98), (.3, .004, .02), 'screen'); b.box((u + .05, .704, .93), (.36, .004, .02), 'screen'); b.box((u + .05, .704, .88), (.2, .004, .02), 'screen'); b.box((u + .05, .45, .0) if False else (u + .05, .4, .78), (.34, .14, .014), 'charcoal', bev=.005); b.box((u + .05, .68, .78), (.1, .08, .02), 'steel_dark'); b.box((u + .05, .68, .83), (.03, .03, .1), 'steel_dark')
        b.box((u - .1, .35, .766), (.38, .14, .018), 'charcoal', bev=.008); b.cyl((u + .55, .3, .8), .04, .09, 'chalk', 'Z', 20, bev=.004)
        b.cyl((u - .55, .55, .765), .06, .03, 'steel_dark', 'Z', 20); b.sweep([(u - .55, .55, .78), (u - .55, .55, 1.05), (u - .4, .5, 1.15)], .008, 'steel_dark', 8, .1); b.box((u - .37, .49, 1.14), (.14, .08, .04), 'yellow', bev=.01)
        b.box((u, .32, .45), (.46, .46, .06), 'rubber', bev=.02) if False else None
        b.box((fu(8.0), .03, 1.9), (.9, .06, .5), 'trim_black', bev=.014); b.box((fu(8.0), .062, 1.9), (.82, .006, .42), 'yellow'); wt(b, 'TURBINE 02', fu(8.0), 2.0, .1, 'trim_black', .068); wt(b, 'CONTROL DESK', fu(8.0), 1.8, .06, 'trim_black', .068)
        for t, p in ((8.4, False),): socket(b, fu(t), .5, plug=p)
    ux, uy = 8.0, 22.7                                                       # the chair, in front of the desk
    b.cyl((ux, uy, .46), .22, .06, 'rubber', 'Z', 28, bev=.012); b.box((ux, uy - .2, .72), (.4, .06, .46), 'rubber', bev=.02); b.cyl((ux, uy, .24), .035, .42, 'steel_dark', 'Z', 12)
    for a in range(5): b.box((ux + .17 * math.cos(a * 1.2566), uy + .17 * math.sin(a * 1.2566), .04), (.18, .04, .03), 'steel_dark', (0, 0, a * 1.2566), bev=.006)
    # --- tidy storage: drum group, pallet with crates, gas cylinders in a rack ---
    for (x, y, c) in ((9.35, 22.4, 'red_dark'), (8.75, 22.9, 'orange_dark'), (9.4, 23.3, 'steel_dark')):
        b.box((x, y - .272, .5), (.3, .01, .26), 'chalk'); b.box((x, y - .278, .5), (.3, .006, .05), 'trim_black'); b.prism([(-.06, -.05), (.06, -.05), (0, .06)], .004, 'trim_black', (x, y - .28, .56), True, 'Y')
        b.cyl((x, y, .45), .27, .9, c, 'Z', 32, bev=.01); b.cyl((x, y, .75), .285, .035, 'steel_dark', 'Z', 32); b.cyl((x, y, .3), .285, .035, 'steel_dark', 'Z', 32)
    for dx in (-.4, 0, .4): b.box((6.8 + dx, 1.2, .06), (.1, .8, .1), 'wood_dark', bev=.01)
    for dy in (-.3, 0, .3): b.box((6.8, 1.2 + dy, .13), (1.0, .12, .03), 'wood', bev=.008)
    b.box((6.8, 1.2, .38), (.8, .6, .4), 'wood', bev=.015); b.box((6.8, 1.2, .79), (.7, .5, .36), 'orange_worn', bev=.015)
    b.box((6.8, .9, .79), (.3, .004, .12), 'chalk')
    for k in range(2): b.cyl((-3.55 + .3 * k, 1.5, .65), .1, 1.2, ['orange', 'steel_light'][k], 'Z', 24, bev=.008); b.sphere((-3.55 + .3 * k, 1.5, 1.25), .1, ['orange', 'steel_light'][k], 14); b.cyl((-3.55 + .3 * k, 1.5, 1.35), .03, .08, 'steel_dark', 'Z', 10)
    b.box((-3.4, 1.5, .5), (.7, .03, .05), 'yellow'); b.box((-3.4, 1.38, .3), (.7, .03, .05), 'steel_dark')
    # --- broken: a leaking pipe stub, a missing ceiling panel with dangling cable, a lamp off its hanger ---
    b.cyl((-.6, 9.0, 4.95), .12, 2.1, 'lagging', 'Z', 24); b.cyl((-.6, 9.0, 3.9), .18, .06, 'steel_mid', 'Z', 24, bev=.006)
    b.sweep([(-.6, 9.0, 3.88), (-.45, 9.1, 3.5), (-.35, 9.15, 3.1)], .08, 'lagging', 20, .2); b.box((-.33, 9.16, 3.05), (.3, .08, .26), 'primer', (.5, 0, .4), bev=.01)
    b.box((2.0, 20.5, 5.0), (1.3, .22, .07), 'steel_dark', (.9, 0, 0), bev=.012); b.box((2.0, 20.5, 4.955), (1.15, .15, .02), 'lamp', (.9, 0, 0)); b.rod((1.4, 20.5, 5.35), (1.4, 20.5, 6.06), .008, 'steel_dark', 8)
    b.box((6.5, 6.5, 7.17), (.94, 1.0, .004), 'primer')                                       # panel missing, bare deck showing
    b.sweep([(6.5, 6.5, 7.15), (6.4, 6.6, 6.5), (6.55, 6.9, 5.9), (6.45, 7.1, 5.5)], .014, 'rubber', 8, .25)

    # --- wall rhythm: high vent grilles on the west, south and north walls ---
    (o, rz), fu = FR['W']
    with b.push(o, rz):
        for t in (9.0, 12.0): vent(b, fu(t), 4.05)
    (o, rz), fu = FR['S']
    pass
    (o, rz), fu = FR['N']
    pass
    # --- work lamp on a stand at the foundation walkway: lights the open rotor (its light lives in run.py) ---
    wx, wy = 6.55, 7.3
    b.cyl((wx, wy, 1.012), .22, .024, 'steel_dark', 'Z', 24, bev=.006)
    for k in range(3):
        a = 2 * math.pi * k / 3; b.rod((wx, wy, 2.3), (wx + .24 * math.cos(a), wy + .24 * math.sin(a), 1.02), .014, 'steel_mid', 8)
    b.rod((wx, wy, 1.0), (wx, wy, 3.45), .02, 'steel_mid', 12)
    b.box((wx - .08, wy + .05, 3.6), (.34, .12, .26), 'trim_black', (0, .5, .25), bev=.02); b.box((wx - .17, wy + .06, 3.54), (.04, .1, .2), 'lamp', (0, .5, .25))
