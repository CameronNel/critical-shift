"""Curated set dressing (v3). Deliberate placements only: signage, notices, safety gear, a working desk, tidy storage, and a few
storytelling wear marks. Text convention: in wall frames text faces +Y (into the room) with rz=pi, rx=pi/2."""
import math
from mathutils import Vector

FR = {'W': (((-4, 24), -math.pi / 2), lambda t: 24 - t), 'E': (((10, 0), math.pi / 2), lambda t: t),
      'S': (((0, 0), 0.0), lambda t: t), 'N': (((0, 24), math.pi), lambda t: -t)}

import assets as A
from assets import WALL

def puddle(b, x, y, rx, ry, sw, z=.0085, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    ring = [((rx * math.cos(2 * math.pi * i / 28)) * c - (ry * math.sin(2 * math.pi * i / 28)) * s, (rx * math.cos(2 * math.pi * i / 28)) * s + (ry * math.sin(2 * math.pi * i / 28)) * c) for i in range(28)]
    b.prism(ring, .004, sw, (x, y, z), True, 'Z')

DRUMS = [(8.98, 23.45, 0.0, .215), (9.58, 23.45, .8, .215)]   # (x, y, bung rotation, base z): built by drums.py (textured lathe objects) on the spill pallet

def work_lamp(b, wx, wy, aim_to):
    """cage work lamp on a telescoping tripod"""
    b.cyl((wx, wy, 1.012), .22, .024, 'steel_dark', 'Z', 24, bev=.006)
    for k in range(3):
        a = 2 * math.pi * k / 3; ca, sa = math.cos(a), math.sin(a)
        b.rod((wx + .03 * ca, wy + .03 * sa, 2.1), (wx + .26 * ca, wy + .26 * sa, 1.02), .016, 'steel_mid', 8); b.rod((wx + .03 * ca, wy + .03 * sa, 2.1), (wx + .12 * ca, wy + .12 * sa, 1.7), .022, 'steel_dark', 8)
        b.cyl((wx + .26 * ca, wy + .26 * sa, 1.03), .03, .02, 'rubber', 'Z', 8)
    b.cyl((wx, wy, 2.12), .035, .08, 'steel_dark', 'Z', 12, bev=.004); b.rod((wx, wy, 2.12), (wx, wy, 3.4), .02, 'steel_mid', 12); b.cyl((wx, wy, 2.4), .03, .05, 'red', 'Z', 10)
    d = (Vector(aim_to) - Vector((wx, wy, 3.55))).normalized(); q = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    from mathutils import Matrix
    b.push((wx, wy, 3.55)); b.m = b.m @ q
    b.box((0, 0, -.15), (.1, .08, .08), 'steel_dark', bev=.01)
    b.lathe((0, 0, 0), [(0, -.13), (.06, -.13), (.11, -.08), (.135, .0), (.14, .1), (.125, .115), (.12, .1), (.115, .0), (0, -.02)], 'trim_black', 20)
    b.lathe((0, 0, 0), [(.115, .108), (0, .108)], 'lamp', 20)
    for k in range(8):
        a = k * math.pi / 4; b.rod((.135 * math.cos(a), .135 * math.sin(a), .11), (.12 * math.cos(a), .12 * math.sin(a), .2), .006, 'steel_mid', 6)
    A.ring(b, (0, 0, .2), .12, .006, 'steel_mid', 'Z', 18); A.ring(b, (0, 0, .15), .128, .005, 'steel_mid', 'Z', 18)
    b.sweep([(-.14, 0, -.03), (-.14, 0, .1), (-.14, 0, .1)], .01, 'steel_dark', 6, .02) if False else None
    b.pop()
    b.sweep([(wx, wy, 1.0), (wx + .1, wy - .2, .7), (wx + .5, wy - .4, .04)], .008, 'rubber', 6, .15)

def build(b):
    b.use('PROPS'); R = b.rng
    # --- signage hung over the bay, exhaust label ---
    b.box((-1.2, 13.7, 4.25), (3.24, .05, .6), 'trim_black', bev=.014)
    b.decal('sign_maint_bay', (-1.2, 13.7 - .0265, 4.25), rot=(math.pi / 2, 0, 0)); b.decal('sign_maint_bay', (-1.2, 13.7 + .0265, 4.25), rot=(math.pi / 2, 0, math.pi))
    for dx in (-1.1, 1.1):
        for k in range(int(1.7 / .07)): b.box((-1.2 + dx, 13.7, 4.5 + k * .07), (.02, .012 if k % 2 else .03, .06), 'steel_mid')
    b.box((7.215, 12.6, .55), (.03, .94, .26), 'trim_black', bev=.008); b.decal('sign_exhaust', (7.2315, 12.6, .55), rot=(math.pi / 2, 0, math.pi / 2))
    # --- west wall: notice board, posters, first aid, sockets, conduit, extinguisher ---
    (o, rz), fu = FR['W']
    with b.push(o, rz):
        A.notice_board(b, fu(9.4), 1.75)
        A.poster(b, fu(11.2), 1.8, 0); A.poster(b, fu(12.3), 1.8, 1)
        A.first_aid(b, fu(13.3), 1.5)
        for t in (8.4, 10.1, 12.0): A.socket(b, fu(t), .5, plug=(t == 10.1))
        A.extinguisher(b, fu(3.0))
        b.rod((fu(8.0), .04, 2.9), (fu(13.5), .04, 2.9), .022, 'steel_mid', 12)
        for t in (8.4, 10.2, 12.0, 13.4): b.box((fu(t), .035, 2.9), (.06, .05, .08), 'steel_dark', bev=.006)
        b.box((fu(13.5), .08, 2.9), (.18, .14, .2), 'steel_dark', bev=.012); b.rod((fu(13.5), .08, 2.8), (fu(13.5), .08, 1.9), .022, 'steel_mid', 12)
    # --- east wall: extinguisher ---
    (o, rz), fu = FR['E']
    with b.push(o, rz): A.extinguisher(b, fu(5.0))
    # --- south wall: hose reel, clock, wayfinding sign ---
    (o, rz), fu = FR['S']
    with b.push(o, rz):
        A.hose_reel(b, fu(6.7)); A.wall_clock(b, fu(3.0), 3.4)
        A.sign_board(b, 'sign_hall', fu(5.5), 2.6, 1.8, .5, depth=.05)
    # --- tool trolley in the bay ---
    A.tool_trolley(b, .75, 13.0)
    # --- north wall: working desk, flammables sign ---
    (o, rz), fu = FR['N']
    with b.push(o, rz):
        A.desk(b, fu(8.0))
        A.sign_board(b, 'sign_desk', fu(8.0), 1.9, .82, .42, depth=.05)
        A.socket(b, fu(8.4), .5)
        b.decal('sign_flammable', (fu(9.28), .006, 1.7), rot=WALL, scale=1.05)
    import machinery as MM                                                                           # nameplates on the generator and on the foundation rail
    b.box((MM.CX + 1.14, 18.95, MM.AZ + .05), (.04, 1.5, .46), 'trim_black', bev=.012); b.decal('nameplate_gen', (MM.CX + 1.1625, 18.95, MM.AZ + .05), rot=(math.pi / 2, 0, math.pi / 2))
    with b.push((6.45, 10.95, 0), math.pi / 2):                                                           # tag sign hung from the foundation rail, facing along the walkway
        b.box((0, 0, 1.78), (.04, 1.0, .34), 'trim_black', bev=.012); b.decal('tag_lp', (-.0215, 0, 1.78), rot=(math.pi / 2, 0, -math.pi / 2))
        for dy in (-.4, .4): b.rod((0, dy, 1.95), (0, dy, 2.05), .012, 'steel_dark', 8)
    b.rod((6.9, 10.95, 2.05), (7.08, 10.95, 2.05), .012, 'steel_dark', 8); b.rod((6.45, 10.95, 2.05), (6.9, 10.95, 2.05), .012, 'steel_dark', 8)
    # --- tidy storage: oil store on a spill pallet (drums are textured lathe objects, see drums.py), pallet with crate and case, gas cylinders in a rack ---
    A.spill_pallet(b, 9.28, 23.45)
    A.drum_pump(b, 8.98 + .125, 23.45 + .085, .215 + .848)
    A.pallet(b, 6.8, 1.2, 1.0, 1.2); A.crate(b, 6.8, 1.2, .8, .6, .42, z0=.158); A.steel_case(b, 6.8, 1.2, .158 + .42 + .05, .5, .36, .26, rz=.15)
    with b.push((-3.55, 1.3, 0), math.pi / 2): A.gas_rack(b, 0, 0)
    # --- broken: a leaking pipe stub, a missing ceiling panel with dangling cable ---
    b.cyl((1.3, 19.6, 4.95), .12, 2.1, 'lagging', 'Z', 24); b.cyl((1.3, 19.6, 3.9), .18, .06, 'steel_mid', 'Z', 24, bev=.006)
    b.sweep([(1.3, 19.6, 3.88), (1.45, 19.7, 3.5), (1.55, 19.75, 3.1)], .08, 'lagging', 20, .2); b.box((1.57, 19.76, 3.05), (.3, .08, .26), 'primer', (.5, 0, .4), bev=.01)
    b.box((6.5, 6.5, 7.17), (.94, 1.0, .004), 'primer')                                       # panel missing, bare deck showing
    b.sweep([(6.5, 6.5, 7.15), (6.4, 6.6, 6.5), (6.55, 6.9, 5.9), (6.45, 7.1, 5.5)], .014, 'rubber', 8, .25)
    # --- wall rhythm: high vent grilles on the west wall ---
    (o, rz), fu = FR['W']
    with b.push(o, rz):
        for t in (9.0, 12.0): A.vent(b, fu(t), 4.05)
    # --- work lamp on a stand at the foundation walkway: lights the open rotor (its light lives in run.py) ---
    work_lamp(b, 6.55, 7.3, (4.6, 11.0, 2.2))
