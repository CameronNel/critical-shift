"""Purposefully built small assets for the turbine room (v4). Everything here is real form: lathe-turned bodies, hinged lids,
drawers with handles, hoses, valves; every sign, dial, label and screen is a texture decal (decals.py), never geometry.
Wall assets are built in the wall frames (local x along the wall, y into the room, z up); WALL is the decal rotation that faces +Y."""
import math
from mathutils import Vector

PI = math.pi
WALL = (PI / 2, 0, PI)

def ring(b, c, R, r, sw, plane='Z', n=24):
    pts = []
    for i in range(n + 1):
        a = 2 * PI * i / n
        p = (R * math.cos(a), R * math.sin(a), 0) if plane == 'Z' else (R * math.cos(a), 0, R * math.sin(a)) if plane == 'Y' else (0, R * math.cos(a), R * math.sin(a))
        pts.append((c[0] + p[0], c[1] + p[1], c[2] + p[2]))
    b.sweep(pts, r, sw, 8, R * .15, caps=False)

def gauge_dial(b, c, kind='gauge_a', face='Y', r=.09, flip=1):
    """Pressure gauge: steel bezel, glass-front dial decal. face='Y' (wall frame, faces +Y) or 'X' (faces +X)."""
    if face == 'Y':
        b.cyl(c, r + .012, .034, 'steel_light', 'Y', 28, bev=.006); b.decal(kind, (c[0], c[1] + .0175, c[2]), rot=WALL, scale=r / .095)
    else:
        b.cyl(c, r + .012, .034, 'steel_light', 'X', 28, bev=.006); b.decal(kind, (c[0] + .0175, c[1], c[2]), rot=(PI / 2, 0, PI / 2), scale=r / .095)

# ------------------------------------------------------------------ safety equipment
def extinguisher(b, u, z0=.5, y=.125):
    """5 kg CO2 extinguisher on a wall bracket (wall frame)."""
    b.box((u, .015, z0 + .3), (.14, .03, .78), 'steel_dark', bev=.008)
    body = [(0, 0), (.07, 0), (.083, .012), (.09, .04), (.09, .40), (.088, .44), (.076, .48), (.056, .505), (.036, .516), (.03, .53), (.03, .56)]
    b.lathe((u, y, z0), body, 'red', 30)
    b.cyl((u, y, z0 + .015), .085, .03, 'trim_black', 'Z', 24, bev=.006)                                            # foot ring
    for zs in (.17, .38):                                                                                              # straps to the wall plate
        b.lathe((u, y, z0 + zs), [(.091, -.014), (.097, -.014), (.097, .014), (.091, .014)], 'trim_black', 24)
        b.box((u, y / 2 + .02, z0 + zs), (.05, y - .07, .028), 'trim_black', bev=.004)
    b.box((u, y, z0 + .59), (.085, .08, .075), 'brass', bev=.01); b.cyl((u, y, z0 + .65), .018, .06, 'steel_dark', 'Z', 10)
    b.sweep([(u, y - .05, z0 + .62), (u, y - .06, z0 + .69), (u, y + .06, z0 + .69), (u, y + .1, z0 + .63)], .009, 'trim_black', 8, .03)          # carry handle
    b.sweep([(u, y + .035, z0 + .575), (u, y + .115, z0 + .57), (u, y + .125, z0 + .5)], .008, 'trim_black', 8, .02)                             # lever
    ring(b, (u + .036, y + .015, z0 + .62), .018, .0035, 'steel_light', 'X', 10)                                                                     # safety pin ring
    b.sweep([(u + .042, y, z0 + .58), (u + .1, y + .035, z0 + .56), (u + .13, y + .1, z0 + .4), (u + .09, y + .125, z0 + .24)], .011, 'rubber', 8, .05)    # hose
    b.lathe((u + .09, y + .125, z0 + .12), [(0, 0), (.02, 0), (.026, .035), (.018, .08), (.014, .12), (0, .12)], 'steel_dark', 12)                  # horn on the wall hook
    b.box((u + .09, .05, z0 + .22), (.04, .1, .03), 'steel_dark', bev=.005)
    b.decal_wrap('ext_label', (u, y), .09, z0 + .1, z0 + .4, PI / 2, .17 / .09 * .95)
    b.decal('sign_ext', (u, .006, z0 + 1.55), rot=WALL, scale=.62)
    b.box((u, .003, z0 + 1.55), (.34, .006, .34), 'trim_black', bev=.003)

def gas_cylinder(b, x, y, body='orange', shoulder='steel_light', label='label_gas_ac', rz=0.0):
    prof = [(0, 0), (.07, 0), (.093, .016), (.099, .05), (.1, .08), (.1, 1.0), (.098, 1.06), (.09, 1.12), (.07, 1.175), (.045, 1.215), (.036, 1.235), (.035, 1.255)]
    sws = [body] * 6 + [shoulder] * 5
    b.lathe((x, y, .0), prof, sws, 28)
    b.cyl((x, y, .0 + .02), .092, .04, 'trim_black', 'Z', 24, bev=.005)
    b.lathe((x, y, 1.245), [(.0, 0), (.052, 0), (.052, .035), (.044, .045), (.0, .045)], 'steel_dark', 16)                                                      # neck collar
    b.box((x, y, 1.32), (.07, .06, .1), 'brass', bev=.01)                                                                                                        # valve body
    b.rod((x + .035, y, 1.33), (x + .09, y, 1.33), .012, 'brass', 8); b.cyl((x + .095, y, 1.33), .016, .02, 'steel_dark', 'X', 8)                                    # outlet
    b.rod((x, y, 1.37), (x, y, 1.42), .01, 'steel_dark', 8); ring(b, (x, y, 1.42), .04, .006, 'red', 'Z', 14)
    for k in range(2): b.box((x, y, 1.42), (.08, .008, .008), 'red', (0, 0, k * PI / 2))
    b.decal_wrap(label, (x, y), .1, .62, .74, -PI / 2 + rz, .3 / .1 * .6)

def gas_rack(b, x0, y0):
    """two cylinders standing in a wall rack, chained."""
    cols = [('orange', 'steel_light', 'label_gas_ac'), ('steel_light', 'steel_light', 'label_gas_o2')]
    for k, (c1, c2, lb) in enumerate(cols): gas_cylinder(b, x0 + .3 * k, y0, c1, c2, lb)
    b.box((x0 + .15, y0 + .18, .0 + .05), (.74, .2, .1), 'steel_dark', bev=.01)                                                                              # base tray
    b.box((x0 + .15, y0 + .22, .05), (.74, .02, .02), 'trim_black')
    for z in (.45, .95):
        b.box((x0 + .15, y0 + .115, z), (.74, .012, .035), 'steel_dark', bev=.003)
        pts = [(x0 - .12 + .06 * i, y0 + .112, z + .004 * (i % 2)) for i in range(0, 14)]
        for p, q in zip(pts[::2], pts[1::2]): b.box(((p[0] + q[0]) / 2, p[1] + .004, z), (.075, .012, .012), 'steel_mid')
    b.box((x0 - .16, y0 + .13, .7), (.03, .04, 1.4), 'steel_dark', bev=.005); b.box((x0 + .46, y0 + .13, .7), (.03, .04, 1.4), 'steel_dark', bev=.005)

def hose_reel(b, u, z=1.3, y=.27):
    """wall-mounted fire hose reel (wall frame): flanged drum with spokes, spiral hose, bracket, valve and nozzle."""
    b.box((u, .03, z), (.8, .06, .8), 'steel_dark', bev=.012)
    for dx in (-.34, .34):
        for dz in (-.34, .34): b.cyl((u + dx, .066, z + dz), .018, .012, 'steel_light', 'Y', 6)
    b.rod((u, .06, z), (u, y + .12, z), .03, 'steel_mid', 12)
    for yy in (y - .09, y + .09):                                                                                      # flanges: ring + spokes
        b.lathe((u, yy, z), [(.265, -.012), (.33, -.012), (.34, -.004), (.34, .004), (.33, .012), (.265, .012)], 'red', 40, axis='Y')
        b.lathe((u, yy, z), [(0, -.012), (.1, -.012), (.1, .012), (0, .012)], 'red', 24, axis='Y')
        for k in range(6):
            a = k * PI / 3 + .2; b.box((u + .18 * math.cos(a), yy, z + .18 * math.sin(a)), (.17, .02, .028), 'red', (0, -a, 0), bev=.004)
    b.lathe((u, y, z), [(0, -.09), (.14, -.09), (.14, .09), (0, .09)], 'steel_dark', 28, axis='Y')
    pts = []
    for t in range(0, 110):                                                                                            # three layers of hose on the drum
        a = t * .52; lay = int(t / 36); w = ((t % 36) / 35 - .5) * .15; rr = .165 + .035 * lay
        pts.append((u + rr * math.cos(a), y + (w if lay % 2 == 0 else -w), z + rr * math.sin(a)))
    b.sweep(pts, .017, 'rubber', 8, .002)
    b.sweep([pts[-1], (u + .22, y + .1, z - .26), (u + .3, y + .18, z - .45)], .017, 'rubber', 8, .1)
    b.lathe((u + .3, y + .18, z - .66), [(0, 0), (.012, 0), (.02, .05), (.03, .15), (.034, .21), (0, .21)], 'brass', 12)                                   # nozzle
    b.box((u + .3, .06, z - .5), (.05, .12, .04), 'steel_dark', bev=.006)
    b.cyl((u - .3, .1, z + .27), .045, .12, 'brass', 'Y', 12, bev=.005); ring(b, (u - .3, .17, z + .27), .05, .008, 'red', 'Y', 14)                             # isolating valve + wheel

def first_aid(b, u, z=1.5):
    b.box((u, .06, z), (.4, .12, .4), 'green', bev=.02); b.box((u, .125, z), (.36, .012, .36), 'green', bev=.01)
    b.decal('firstaid_box', (u, .1315, z), rot=WALL, scale=.88)
    for dz in (-.15, .15): b.cyl((u - .19, .07, z + dz), .012, .02, 'steel_dark', 'Z', 8)
    b.box((u + .17, .135, z), (.02, .02, .06), 'steel_light', bev=.004)

def socket(b, u, z, plug=False):
    """industrial 16 A socket outlet with a spring lid (wall frame); optional plug and curly cable"""
    b.box((u, .02, z), (.15, .04, .17), 'steel_dark', bev=.01)
    b.lathe((u, .04, z), [(0, 0), (.058, 0), (.062, .012), (.062, .04), (.05, .05), (.0, .05)], 'blue_panel' if not plug else 'red_dark', 18, axis='Y')
    b.lathe((u, .09, z), [(0, 0), (.042, 0), (.042, .01), (.0, .01)], 'trim_black', 14, axis='Y')
    for k in range(3):
        a = k * 2 * PI / 3 + PI / 2; b.cyl((u + .022 * math.cos(a), .098, z + .022 * math.sin(a)), .005, .008, 'brass', 'Y', 6)
    b.box((u, .075, z + .07), (.05, .06, .02), 'steel_mid', bev=.004)                                                                                    # lid hinge
    if plug:
        b.lathe((u, .1, z), [(0, 0), (.05, 0), (.05, .08), (.036, .11), (.03, .16), (0, .16)], 'red', 16, axis='Y')
        pts = [(u, .26, z)] + [(u + .09 + .04 * math.sin(i * .9), .26 + .03 * math.cos(i * .9), z - .05 - i * .028) for i in range(12)] + [(u + .45, .3, .06)]
        b.sweep([(u, .24, z)] + pts[1:], .011, 'rubber', 8, .1)

def notice_board(b, u, z=1.75):
    b.box((u, .04, z), (1.3, .08, .95), 'steel_light', bev=.012)                                                         # aluminium frame
    b.box((u, .075, z), (1.2, .02, .85), 'wood', bev=.006)                                                               # cork face
    b.decal('notice_header', (u, .0865, z + .36), rot=WALL, scale=.78)
    for (dx, dz, nm, rot) in ((-.38, -.02, 'notice_a', .03), (0.0, 0.0, 'notice_b', -.03), (.38, -.04, 'notice_c', .02), (-.2, -.3, 'notice_d', -.05), (.25, -.3, 'notice_e', .04)):
        b.decal(nm, (u + dx, .0875, z + dz), rot=WALL, spin=rot)
        b.sphere((u + dx, .09, z + dz + .19), .011, 'red', 8)

def poster(b, u, z, kind):
    b.box((u, .03, z), (.62, .06, .86), 'trim_black', bev=.012); b.box((u, .0615, z), (.56, .004, .8), 'paper')
    b.decal('poster_%d' % kind, (u, .0645, z), rot=WALL, scale=.98)

def wall_clock(b, u, z):
    b.lathe((u, .02, z), [(0, 0), (.21, 0), (.21, .035), (.2, .045), (0, .045)], 'trim_black', 36, axis='Y')
    b.decal('clock_face', (u, .0475, z), rot=WALL, scale=.98)

def vent(b, u, z, w=.9, h=.5):
    b.box((u, .03, z), (w + .1, .06, h + .1), 'trim_black', bev=.012); b.box((u, .062, z), (w, .01, h), 'backing')
    for k in range(6): b.box((u, .08, z - h / 2 + .06 + k * (h - .12) / 5), (w - .06, .02, .03), 'steel_dark', (math.radians(-28), 0, 0), bev=.004)
    b.box((u, .09, z), (.03, .02, h), 'steel_dark')

def sign_board(b, name, u, z, w, h, depth=.05, frame=.02, y=.0, d_name=None):
    """wall-frame board with a decal face (frame box + decal)"""
    b.box((u, y + depth / 2, z), (w + frame * 2, depth, h + frame * 2), 'trim_black', bev=.012)
    b.decal(name, (u, y + depth + .0015, z), rot=WALL, size=(w, h))

# ------------------------------------------------------------------ furniture
def tool_trolley(b, tx, ty):
    """three-drawer tool trolley with top tray, push handle, casters and a few tools on top (world frame; drawers face -X? no: face +Y)."""
    W, D = .9, .48
    b.box((tx, ty, .5), (W, D, .62), 'steel_dark', bev=.012)                                                              # carcass
    b.box((tx, ty, .835), (W + .04, D + .04, .05), 'steel_mid', bev=.014)                                                  # top
    for sx in (-1, 1): b.box((tx + sx * (W / 2 + .005), ty, .88), (.03, D + .04, .05), 'steel_mid', bev=.008)             # tray lips
    b.box((tx, ty + D / 2 + .02, .88), (W + .04, .03, .05), 'steel_mid', bev=.008); b.box((tx, ty - D / 2 - .02, .88), (W + .04, .03, .05), 'steel_mid', bev=.008)
    for k, zc in enumerate((.66, .5, .34)):
        b.box((tx, ty + D / 2 + .008, zc), (W - .05, .02, .14), 'red' if k != 1 else 'red_dark', bev=.006)
        b.rod((tx - .18, ty + D / 2 + .035, zc), (tx + .18, ty + D / 2 + .035, zc), .009, 'steel_light', 8)
        for sx in (-.18, .18): b.box((tx + sx, ty + D / 2 + .022, zc), (.014, .03, .014), 'steel_light')
    b.decal('label_trolley', (tx, ty + D / 2 + .0195, .735), rot=(PI / 2, 0, PI))
    b.sweep([(tx - W / 2 + .06, ty - D / 2 - .02, .86), (tx - W / 2 + .06, ty - D / 2 - .04, 1.0), (tx + W / 2 - .06, ty - D / 2 - .04, 1.0), (tx + W / 2 - .06, ty - D / 2 - .02, .86)], .014, 'steel_light', 8, .06)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = tx + sx * (W / 2 - .06), ty + sy * (D / 2 - .06)
            b.box((cx, cy, .22), (.06, .07, .03), 'steel_dark', bev=.004); b.rod((cx, cy, .21), (cx, cy, .13), .008, 'steel_mid', 6)
            b.lathe((cx, cy, .065), [(0, -.015), (.06, -.015), (.065, 0), (.06, .015), (0, .015)], 'rubber', 16, axis='X'); b.lathe((cx, cy, .065), [(0, -.02), (.03, -.02), (.03, .02), (0, .02)], 'steel_mid', 10, axis='X')
    # tools on the tray
    b.box((tx - .25, ty + .02, .865), (.22, .03, .008), 'steel_light', (0, 0, .15), bev=.002); b.cyl((tx - .15, ty - .01, .868), .018, .008, 'steel_light', 'Z', 10)           # spanner
    b.rod((tx + .1, ty - .05, .87), (tx + .26, ty - .02, .87), .011, 'wood', 8); b.box((tx + .08, ty - .055, .875), (.05, .03, .028), 'steel_dark', (0, 0, .18), bev=.004)  # hammer
    b.lathe((tx + .3, ty + .12, .86), [(0, 0), (.035, 0), (.035, .06), (.025, .09), (.014, .12), (.006, .15), (0, .15)], 'yellow', 14)                                      # oil can
    b.rod((tx + .3, ty + .12, .98), (tx + .36, ty + .12, 1.04), .005, 'steel_mid', 6)
    b.box((tx - .1, ty + .12, .895), (.34, .16, .07), 'orange', bev=.01); b.sweep([(tx - .22, ty + .12, .93), (tx - .22, ty + .12, .97), (tx + .02, ty + .12, .97), (tx + .02, ty + .12, .93)], .008, 'steel_dark', 8, .04)   # tool case

def pallet(b, x, y, w=1.0, d=1.2, rz=0.0):
    with b.push((x, y, 0), rz):
        for dx in (-w / 2 + .06, 0, w / 2 - .06): b.box((dx, 0, .06), (.1, d, .1), 'wood_dark', bev=.01)
        for k in range(3): b.box((0, -d / 2 + .06 + k * (d - .12) / 2, .035), (w, .1, .025), 'wood', bev=.006)
        for k in range(5): b.box((0, -d / 2 + .06 + k * (d - .12) / 4 + (0 if k else 0), .13), (w, .12, .028), 'wood', bev=.006)

def crate(b, x, y, w=.8, d=.6, h=.4, z0=.145, rz=0.0, stencil=True):
    """slatted timber crate: corner posts, three slat boards a side, lid boards and a stencil"""
    with b.push((x, y, z0), rz):
        for sx in (-1, 1):
            for sy in (-1, 1): b.box((sx * (w / 2 - .025), sy * (d / 2 - .025), h / 2), (.05, .05, h), 'wood_dark', bev=.006)
        for k in range(3):
            zz = .06 + k * (h - .09) / 2.4
            for sy in (-1, 1): b.box((0, sy * (d / 2 - .01), zz + .02), (w - .1, .02, .11), 'wood', bev=.004)
            for sx in (-1, 1): b.box((sx * (w / 2 - .01), 0, zz + .02), (.02, d - .1, .11), 'wood', bev=.004)
        for k in range(4): b.box((0, -d / 2 + .08 + k * (d - .16) / 3, h + .012), (w + .02, .13, .024), 'wood', bev=.004)
        b.box((0, 0, h + .036), (.05, d + .02, .024), 'wood_dark', bev=.004); b.box((-w / 4, 0, h + .036), (.05, d + .02, .024), 'wood_dark', bev=.004)
        if stencil: b.decal('stencil_fragile', (0, d / 2 + .0105, h * .45), rot=(PI / 2, 0, PI), scale=.7 * w / .8 * .9)

def steel_case(b, x, y, z0, w=.7, d=.5, h=.36, rz=0.0):
    with b.push((x, y, z0), rz):
        b.box((0, 0, h / 2), (w, d, h), 'orange_worn', bev=.02)
        b.box((0, 0, h + .006), (w + .02, d + .02, .02), 'orange_dark', bev=.006)
        for sx in (-1, 1): b.box((sx * (w / 2 + .005), 0, h * .7), (.018, .1, .05), 'steel_mid', bev=.004)
        for sx in (-.2, .2): b.box((sx, d / 2 + .012, h * .72), (.06, .025, .05), 'steel_light', bev=.004)                       # latches
        b.sweep([(-.1, 0, h + .012), (-.1, 0, h + .07), (.1, 0, h + .07), (.1, 0, h + .012)], .01, 'steel_dark', 6, .03)         # carry handle
        b.decal('label_ship', (0, d / 2 + .0105, h * .38), rot=(PI / 2, 0, PI), scale=.95)

def desk(b, u):
    """working desk (north wall frame): wood top, drawer pedestal, legs, monitor with a live-looking screen, keyboard, mouse, lamp, mug, papers"""
    b.box((u, .38, .74), (1.5, .72, .04), 'wood', bev=.01); b.box((u, .38, .705), (1.42, .64, .035), 'wood_dark', bev=.006)
    b.box((u - .52, .38, .36), (.4, .62, .68), 'steel_dark', bev=.012)
    for k, zc in enumerate((.6, .42, .24)):
        b.box((u - .52, .695, zc), (.36, .014, .15), 'steel_mid', bev=.005); b.rod((u - .6, .715, zc + .03), (u - .44, .715, zc + .03), .008, 'steel_light', 8)
        for sx in (-.6, -.44): b.box((u + sx, .705, zc + .03), (.012, .02, .012), 'steel_light')
    for dy in (.08, .68): b.box((u + .69, dy, .36), (.05, .05, .7), 'steel_dark', bev=.006)
    b.box((u + .15, .08, .42), (1.0, .02, .55), 'steel_dark', bev=.006)
    b.box((u + .69, .38, .12), (.04, .6, .04), 'steel_dark', bev=.004)
    # monitor
    mx = u + .1
    b.lathe((mx, .54, .76), [(0, 0), (.095, 0), (.1, .008), (.09, .016), (0, .016)], 'trim_black', 20); b.box((mx, .56, .86), (.045, .03, .2), 'trim_black', bev=.006)
    b.box((mx, .55, 1.0), (.54, .036, .33), 'trim_black', bev=.012); b.box((mx, .52, 1.0), (.2, .05, .2), 'trim_black', bev=.01)
    b.decal('desk_monitor', (mx, .5695, 1.0), rot=WALL, scale=1.0)
    b.box((mx, .573, .852), (.03, .008, .008), 'led_green')
    # keyboard + mouse
    b.box((mx, .3, .768), (.38, .14, .018), 'charcoal', bev=.007); b.decal('keyboard', (mx, .3, .7775), rot=(0, 0, 0), spin=PI, scale=1.0)
    b.box((mx + .31, .3, .77), (.06, .1, .026), 'charcoal', bev=.012); b.sweep([(mx + .31, .35, .775), (mx + .31, .45, .775), (mx + .12, .56, .78)], .003, 'rubber', 6, .05)
    # lamp
    lx = u - .1
    b.lathe((lx, .58, .76), [(0, 0), (.07, 0), (.074, .008), (.06, .02), (0, .02)], 'steel_dark', 20); b.rod((lx, .58, .77), (lx - .03, .52, .98), .007, 'steel_mid', 8); b.sphere((lx - .03, .52, .98), .014, 'steel_dark', 8)
    b.rod((lx - .03, .52, .98), (lx - .13, .46, 1.12), .007, 'steel_mid', 8)
    b.lathe((lx - .13, .46, 1.12), [(.012, 0), (.04, -.02), (.075, -.08), (.082, -.085), (.078, -.085), (.04, -.04), (.012, -.01)], 'yellow', 16)
    b.sphere((lx - .13, .46, 1.07), .022, 'lamp', 8)
    # mug, papers, binder
    b.lathe((u + .56, .3, .76), [(0, 0), (.036, 0), (.04, .005), (.04, .09), (.0375, .092), (.0345, .09), (.0345, .012), (0, .012)], 'chalk', 18)
    b.sweep([(u + .6, .3, .84), (u + .64, .3, .84), (u + .64, .3, .79), (u + .6, .3, .79)], .006, 'chalk', 6, .02)
    for k, (dx, dy, r) in enumerate(((.0, .0, .08), (.01, .0, -.1), (-.01, .02, .05))): b.box((u - .02 + dx, .28 + dy, .765 + k * .003), (.22, .3, .002), 'paper', (0, 0, r))
    b.box((u - .32, .32, .78), (.24, .3, .05), 'red_dark', bev=.008); b.box((u - .32, .32, .81), (.22, .28, .012), 'paper')
    # phone
    b.box((u + .36, .56, .775), (.2, .14, .04), 'trim_black', bev=.01); b.box((u + .36, .56, .805), (.22, .05, .026), 'trim_black', bev=.008)

# ------------------------------------------------------------------ oil store
def spill_pallet(b, cx, cy, w=1.42, d=.82):
    """polyethylene two-drum spill pallet: rounded sump, steel grating on corner posts, fork pockets, drain plug"""
    zt = .17
    with b.push((cx, cy, 0), 0):
        b.box((0, 0, zt / 2), (w, d, zt), 'yellow', bev=.025)
        b.box((0, 0, zt - .004), (w - .08, d - .08, .012), 'backing')                                                           # sump well
        for sx in (-1, 1): b.box((sx * (w / 2 - .005), 0, .06), (.012, .24, .08), 'backing', bev=.004)                          # fork pockets
        for k in range(2): b.box((0, -d / 2 + .004 + k * (d - .008), .12), (w - .06, .01, .02), 'yellow_worn')
        for sx in (-1, 1):
            for sy in (-1, 1): b.box((sx * (w / 2 - .06), sy * (d / 2 - .06), zt + .02), (.05, .05, .04), 'yellow', bev=.008)
        for k in range(int((w - .12) / .055)): b.box((-w / 2 + .07 + k * .055, 0, zt + .042), (.022, d - .1, .03), 'steel_dark', bev=.004)    # grating bars
        for sy in (-.25, 0, .25): b.box((0, sy, zt + .03), (w - .1, .018, .02), 'steel_mid')
        b.cyl((w / 2 - .02, d / 2 + .004, .06), .018, .012, 'steel_light', 'Y', 8)
        b.box((w / 2 - .06, -d / 2 - .006, .09), (.2, .012, .04), 'trim_black', bev=.004)

def drum_pump(b, x, y, z):
    """rotary hand pump seated in the 2 in bung: tube, body, crank and delivery hose with a nozzle"""
    b.lathe((x, y, z), [(0, 0), (.04, 0), (.04, .02), (.02, .03), (.02, .12), (.03, .13), (.03, .2), (0, .2)], 'steel_dark', 14)
    b.box((x + .04, y, z + .17), (.12, .05, .06), 'steel_mid', bev=.01); b.rod((x + .1, y, z + .17), (x + .2, y, z + .17), .011, 'steel_light', 8)
    b.rod((x + .2, y, z + .17), (x + .2, y, z + .27), .009, 'steel_dark', 8); b.cyl((x + .2, y, z + .29), .014, .1, 'red', 'X', 8)
    b.sweep([(x + .1, y, z + .15), (x + .17, y + .02, z + .08), (x + .2, y + .06, z - .05)], .011, 'rubber', 8, .05)

def funnel(b, x, y, z):
    b.lathe((x, y, z), [(0, 0), (.012, 0), (.012, .05), (.07, .1), (.075, .11), (.07, .11), (.0, .0)], 'orange', 16)

# ------------------------------------------------------------------ maintenance bay hand tools and shelf stock (world frame; boards face +X)
def spanner(b, y, z, L, x=-3.755, sw='steel_light'):
    """open-ended spanner hanging from a peg: shaft, round ring head at the bottom, open jaw at the top"""
    b.box((x, y, z - L / 2), (.016, .03, L - .06), sw, bev=.004)
    b.cyl((x, y, z - L + .03), .036, .016, sw, 'X', 14, bev=.003); b.cyl((x + .001, y, z - L + .03), .018, .018, 'backing', 'X', 8)
    b.cyl((x, y, z - .03), .04, .016, sw, 'X', 14, bev=.003); b.box((x + .001, y, z - .005), (.02, .028, .05), 'backing')
    b.rod((x + .008, y, z), (x + .02, y, z + .015), .004, 'steel_dark', 6)

def screwdriver(b, y, z, L, x=-3.752, grip='orange'):
    b.lathe((x, y, z - .1), [(0, 0), (.012, 0), (.018, .02), (.019, .07), (.014, .1), (.0, .1)], grip, 10)
    b.rod((x, y, z - .1), (x, y, z - L), .0045, 'steel_light', 6); b.rod((x, y, z), (x + .01, y, z + .012), .004, 'steel_dark', 6)

def hammer(b, y, z, x=-3.752):
    b.rod((x, y, z - .3), (x, y, z), .012, 'wood', 8); b.box((x, y, z - .015), (.03, .11, .035), 'steel_dark', bev=.006); b.box((x, y + .07, z - .015), (.026, .035, .03), 'steel_mid', bev=.004)
    b.rod((x + .005, y, z + .015), (x + .01, y, z + .03), .004, 'steel_dark', 6)

def pliers(b, y, z, x=-3.752):
    for s in (-1, 1):
        b.rod((x, y + s * .028, z - .22), (x, y + s * .006, z - .06), .009, 'red', 8); b.box((x, y + s * .008, z - .035), (.012, .016, .07), 'steel_mid', bev=.003)
    b.cyl((x, y, z - .06), .01, .02, 'steel_dark', 'X', 8)

def jerry_can(b, x, y, z, col='orange', rz=0.0):
    with b.push((x, y, z), rz):
        b.box((0, 0, .21), (.34, .16, .42), col, bev=.02); b.box((0, 0, .21), (.34, .164, .02), 'trim_black'); b.box((0, 0, .31), (.34, .164, .02), 'trim_black')
        b.box((-.06, 0, .445), (.17, .1, .03), col, bev=.008)
        b.cyl((.1, 0, .44), .026, .045, 'steel_dark', 'Z', 10, bev=.004); b.cyl((.1, 0, .47), .017, .02, 'red', 'Z', 8)

def parts_bin(b, x, y, z, w, d, h, sw='yellow', rz=0.0, fill=True):
    with b.push((x, y, z), rz):
        b.box((0, 0, .008), (w, d, .016), sw, bev=.004)
        b.box((0, d / 2 - .006, h / 2), (w, .012, h), sw, bev=.004); b.box((0, -d / 2 + .006, h / 2), (w, .012, h * .75), sw, bev=.004)
        for s in (-1, 1): b.box((s * (w / 2 - .006), 0, h / 2), (.012, d, h), sw, bev=.004)
        if fill:
            for k in range(4): b.cyl((-w * .3 + k * w * .2, .0, .035), .02, .05, 'steel_mid', 'Z', 8); b.cyl((-w * .3 + k * w * .2, 0, .062), .012, .008, 'steel_dark', 'Z', 6)

def carton(b, x, y, z, w, d, h, rz=0.0, label=True):
    with b.push((x, y, z), rz):
        b.box((0, 0, h / 2), (w, d, h), 'sand_dark', bev=.006); b.box((0, 0, h + .001), (.05, d + .004, .004), 'chalk')
        if label: b.decal('label_ship', (w / 2 + .0015, 0, h * .55), rot=(PI / 2, 0, PI / 2), scale=.7)

def mallet(b, y, z, x=-3.752):
    b.rod((x, y, z - .3), (x, y, z), .013, 'wood', 8); b.cyl((x, y, z - .02), .032, .1, 'rubber', 'Y', 12, bev=.004); b.cyl((x, y, z - .02), .034, .008, 'steel_dark', 'Y', 12) 
