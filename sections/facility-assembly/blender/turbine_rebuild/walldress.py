"""Wall dressing pass: pipe bundles, cable ladders, louvred fans, wayfinding, wall equipment, bump rails and acoustic quilting.
Everything is built in the wall frames (local x along the wall, y into the room, z up). Text faces +Y with rz=pi, rx=pi/2."""
import math
import arch

PI = math.pi
FR = {k: v['frame'] for k, v in arch.wall_specs().items()}

def txt(b, s, u, z, size, sw='chalk', y=.0): b.text(s, (u, y, z), size, sw, PI, PI / 2)

def pipe_run(b, u0, u1, z, r, d, sw, bands=(), brackets=1.3):
    b.rod((u0, d, z), (u1, d, z), r, sw, 14)
    for u in [u0 + .4 + k * brackets for k in range(int((u1 - u0 - .4) / brackets) + 1)]:
        b.box((u, d / 2, z), (.07, d, .05), 'steel_dark', bev=.006); b.cyl((u, d, z), r + .02, .05, 'steel_dark', 'X', 14, bev=.004)
    for u, c in bands: b.cyl((u, d, z), r + .008, .12, c, 'X', 14)
    for u in (u0, u1): b.cyl((u, d, z), r + .03, .05, 'steel_light', 'X', 14, bev=.006)                                     # flanges

def wheel_valve(b, u, z, d, r=.15):
    b.cyl((u, d, z), .07, .22, 'steel_dark', 'Z', 14, bev=.006); b.rod((u, d, z + .1), (u, d, z + .3), .014, 'steel_mid', 8)
    b.cyl((u, d, z + .32), r, .02, 'red', 'Z', 20); b.cyl((u, d, z + .32), .02, .05, 'steel_dark', 'Z', 8)
    for k in range(4): b.rod((u, d, z + .32), (u + r * math.cos(k * PI / 2), d + r * math.sin(k * PI / 2), z + .32), .008, 'red', 6)

def gauge(b, u, z, d, r=.09):
    b.cyl((u, d + .02, z), r + .015, .04, 'steel_dark', 'Y', 20, bev=.005); b.cyl((u, d + .045, z), r, .006, 'chalk', 'Y', 20)
    b.box((u + .012, d + .052, z + .012), (.005, .004, .07), 'trim_black', (0, -.7, 0)); b.rod((u, d, z - .1), (u, d, z - r), .01, 'steel_mid', 6)

def ladder(b, u0, u1, z, d, w=.34, rung=.3):
    """horizontal cable ladder lying flat against the wall: two rails and rungs across them"""
    for s in (-1, 1): b.box(((u0 + u1) / 2, d, z + s * w / 2), (u1 - u0, .05, .03), 'steel_mid', bev=.004)
    for k in range(int((u1 - u0) / rung) + 1): b.box((u0 + k * rung, d, z), (.02, .04, w), 'steel_dark')
    for u in (u0 + .2, (u0 + u1) / 2, u1 - .2): b.box((u, d / 2, z - w / 2), (.04, d, .04), 'steel_dark', bev=.004)

def fan(b, u, z, d_out=.5):
    b.box((u, .03, z), (1.3, .06, 1.3), 'trim_black', bev=.02)
    b.cyl((u, .1, z), d_out + .02, .14, 'steel_dark', 'Y', 36, bev=.01); b.cyl((u, .16, z), d_out - .03, .02, 'backing', 'Y', 32)
    for k in range(7):
        a = k * 2 * PI / 7 + .3; b.box((u + math.cos(a) * .24, .15, z + math.sin(a) * .24), (.34, .012, .13), 'steel_mid', (0, -a, 0), bev=.004)
    b.cyl((u, .17, z), .09, .06, 'steel_light', 'Y', 18, bev=.006)
    b.arc_shell((u, .2, z), d_out - .02, d_out - .05, .02, 0, 2 * PI, 'steel_dark', 36); b.arc_shell((u, .2, z), .3, .27, .02, 0, 2 * PI, 'steel_dark', 28)
    for k in range(8): a = k * PI / 4; b.rod((u + .08 * math.cos(a), .2, z + .08 * math.sin(a)), (u + (d_out - .03) * math.cos(a), .2, z + (d_out - .03) * math.sin(a)), .008, 'steel_dark', 6)
    b.box((u, .09, z + .72), (1.3, .2, .05), 'steel_dark', (-.4, 0, 0), bev=.01)                                          # rain hood
    b.box((u + .5, .1, z - .56), (.2, .12, .12), 'yellow', bev=.01)                                                      # isolator
    b.cyl((u + .5, .17, z - .56), .035, .02, 'red', 'Y', 12)

def exit_sign(b, u, z):
    b.box((u, .04, z), (.62, .08, .24), 'trim_black', bev=.012); b.box((u, .085, z), (.54, .006, .17), 'led_green')
    txt(b, 'EXIT', u + .04, z, .09, 'trim_black', .092)
    b.prism([(.05, 0), (-.03, .04), (-.03, -.04)], .004, 'trim_black', (u - .2, .091, z), True, 'Y')

def hazard_plaque(b, u, z, kind='bolt'):
    b.box((u, .03, z), (.4, .05, .4), 'trim_black', bev=.012)
    b.prism([(-.17, -.14), (.17, -.14), (0, .17)], .008, 'yellow', (u, .06, z + .0), True, 'Y')
    if kind == 'bolt': b.prism([(.0, .1), (-.045, -.015), (-.005, -.015), (-.03, -.09), (.05, .015), (.01, .015)], .006, 'trim_black', (u, .068, z - .01), True, 'Y')
    else: b.cyl((u, .068, z - .02), .03, .006, 'trim_black', 'Y', 12)

def strobe(b, u, z):
    b.cyl((u, .05, z), .075, .06, 'trim_black', 'Y', 16, bev=.006); b.sphere((u, .1, z), .06, 'lamp', 12)

def horn(b, u, z):
    b.box((u, .04, z), (.12, .08, .12), 'steel_dark', bev=.008); b.cyl((u, .17, z), .035, .16, 'steel_dark', 'Y', 12, r2=.11, bev=.004); b.cyl((u, .26, z), .115, .01, 'steel_mid', 'Y', 16)

def estop(b, u, z):
    b.box((u, .04, z), (.14, .08, .22), 'yellow', bev=.01); b.cyl((u, .1, z + .03), .04, .04, 'red', 'Y', 16, bev=.006); b.cyl((u, .12, z + .03), .028, .02, 'red_dark', 'Y', 12)
    b.box((u, .085, z - .07), (.08, .006, .025), 'trim_black')

def db_board(b, u, z):
    b.box((u, .09, z), (.8, .18, 1.1), 'steel_dark', bev=.02); b.box((u, .185, z), (.74, .02, 1.04), 'steel_mid', bev=.015)
    for k in range(4): b.box((u - .27 + k * .18, .2, z + .3), (.1, .01, .1), 'chalk' if k != 1 else 'yellow')
    for k in range(3): b.cyl((u - .24 + k * .24, .2, z - .05), .035, .02, 'trim_black', 'Y', 12)
    b.box((u, .2, z - .3), (.5, .01, .14), 'screen_cool'); b.box((u + .3, .2, z + .3), (.04, .01, .04), 'led_green')
    b.box((u + .46, .1, z), (.04, .04, .6), 'trim_black'); b.text('DB-04', (u, .2, z + .45), .07, 'chalk', PI, PI / 2)
    for dx in (-.2, .2): b.rod((u + dx, .1, z + .55), (u + dx, .1, 4.4), .022, 'steel_mid', 8)                          # conduit risers

def eyewash(b, u):
    b.box((u, .04, 1.3), (.5, .08, .7), 'green', bev=.015); b.cyl((u, .1, 1.05), .13, .14, 'steel_light', 'Z', 18, bev=.006)
    for dx in (-.07, .07): b.cyl((u + dx, .1, 1.17), .018, .1, 'yellow', 'Z', 10)
    b.rod((u, .08, 1.45), (u, .22, 1.6), .015, 'steel_light', 8); b.cyl((u, .22, 1.62), .035, .02, 'green', 'Z', 10)
    b.box((u, .09, 1.55), (.3, .01, .12), 'chalk'); txt(b, 'EYEWASH', u, 1.55, .045, 'green', .096)
    b.box((u, .03, 2.15), (.5, .05, .5), 'green', bev=.012); b.box((u, .062, 2.15), (.05, .01, .3), 'chalk'); b.box((u, .062, 2.15), (.3, .01, .05), 'chalk')

def evac_plan(b, u, z):
    b.box((u, .03, z), (.8, .05, .58), 'trim_black', bev=.012); b.box((u, .062, z), (.74, .01, .52), 'paper')
    b.box((u, .07, z), (.5, .004, .34), 'poster_a'); b.box((u - .08, .074, z), (.12, .003, .2), 'chalk'); b.box((u + .12, .074, z - .06), (.2, .003, .08), 'chalk')
    b.cyl((u - .14, .076, z + .1), .018, .004, 'led_green', 'Y', 8); b.cyl((u + .2, .076, z + .1), .018, .004, 'red', 'Y', 8)

def bump_rail(b, u0, u1, z=.78):
    b.box(((u0 + u1) / 2, .09, z), (u1 - u0, .1, .14), 'rubber', bev=.02); b.box(((u0 + u1) / 2, .09, z + .09), (u1 - u0, .1, .025), 'yellow')
    for u in [u0 + .1 + k * .9 for k in range(int((u1 - u0) / .9) + 1)]: b.box((u, .04, z), (.06, .08, .22), 'steel_dark', bev=.008)

def quilt(b, u0, u1, z0, z1):
    nu, nz = int((u1 - u0) / .6), int((z1 - z0) / .6); w, h = (u1 - u0) / nu, (z1 - z0) / nz
    for i in range(nu):
        for j in range(nz):
            b.box((u0 + (i + .5) * w, .05, z0 + (j + .5) * h), (w - .04, .06, h - .04), 'blue_panel' if (i + j) % 2 else 'wall_slate_lt', bev=.02)
    b.box(((u0 + u1) / 2, .035, z1 + .02), (u1 - u0 + .06, .07, .04), 'trim_black', bev=.008); b.box(((u0 + u1) / 2, .035, z0 - .02), (u1 - u0 + .06, .07, .04), 'trim_black', bev=.008)

def build(b):
    b.use('PROPS')
    # ---- south wall (lx = x)
    with b.push(*FR['south']):
        fan(b, 3.0, 5.4)
        pipe_run(b, 3.7, 7.7, 3.35, .06, .14, 'lagging', [(4.6, 'yellow'), (6.4, 'yellow')]); pipe_run(b, 3.7, 7.7, 3.62, .035, .13, 'steel_mid', [(5.2, 'red'), (7.0, 'green')])
        pipe_run(b, 3.7, 7.7, 3.85, .035, .13, 'steel_dark', [(5.6, 'orange')])
        wheel_valve(b, 5.0, 3.35, .14); gauge(b, 6.9, 3.84, .14); gauge(b, 4.2, 3.84, .14)
        exit_sign(b, 2.2, 3.05); hazard_plaque(b, -2.4, 2.4, 'bolt'); hazard_plaque(b, 9.2, 2.2, 'bolt')
        horn(b, 1.8, 4.1); strobe(b, -2.0, 3.0); bump_rail(b, -3.9, -1.6); bump_rail(b, 1.6, 3.2)
        db_board(b, -3.1, 1.75)
    # ---- north wall (lx = -x)
    with b.push(*FR['north']):
        fan(b, -5.0, 5.2)
        quilt(b, -3.6, 1.0, 4.75, 5.95)
        b.box((-7.7, .03, 3.55), (1.9, .06, .62), 'trim_black', bev=.016); b.box((-7.7, .064, 3.8), (1.8, .006, .03), 'yellow'); b.box((-7.7, .064, 3.3), (1.8, .006, .03), 'yellow'); txt(b, 'TURBINE HALL 02', -7.7, 3.6, .14, 'chalk', .07); txt(b, 'AUTHORISED PERSONNEL ONLY', -7.7, 3.4, .06, 'chalk', .07)
        for u in (1.25, 2.3, 3.35):
            b.rod((u, .09, 2.6), (u, .09, 6.15), .03, 'steel_mid', 10)
        ladder(b, 1.0, 4.0, 6.15, .14)
        b.sweep([(1.8, .18, 6.15), (2.5, .18, 6.15), (3.2, .18, 6.15)], .02, 'rubber', 8, .1); b.sweep([(1.8, .2, 6.15), (3.5, .2, 6.15)], .012, 'red', 8, .1)
        exit_sign(b, 2.2, 3.05); hazard_plaque(b, 1.9, 2.4, 'bolt'); horn(b, -3.8, 3.7); strobe(b, -2.2, 3.0)
        bump_rail(b, -9.5, -6.3)
    # ---- east wall (lx = y)
    with b.push(*FR['east']):
        db_board(b, 12.4, 1.75); estop(b, 14.6, 1.4); estop(b, 5.6, 1.4)
        horn(b, 6.0, 3.9); horn(b, 18.0, 3.9); strobe(b, 10.0, 3.9); strobe(b, 14.0, 3.9)
        bump_rail(b, 2.6, 5.2); bump_rail(b, 15.5, 21.0)
        for z in (3.1, 3.35): pipe_run(b, 14.8, 21.4, z, .04, .12, 'steel_mid', [(16.0, 'red'), (19.0, 'yellow')])
        wheel_valve(b, 17.6, 3.1, .12, .12); gauge(b, 20.4, 3.55, .12)
        hazard_plaque(b, 8.0, 2.6, 'bolt'); hazard_plaque(b, 22.8, 2.4, 'x')
    # ---- west wall (lx = 24 - y)
    with b.push(*FR['west']):
        eyewash(b, 24 - 1.8); evac_plan(b, 24 - 7.9, 1.75)
        bump_rail(b, 24 - 22.8, 24 - 14.5); bump_rail(b, 24 - 6.5, 24 - 2.8)
        for z in (3.25, 3.5): pipe_run(b, 24 - 20.0, 24 - 13.0, z, .04, .12, 'steel_mid', [(24 - 18.0, 'green'), (24 - 15.0, 'yellow')])
        estop(b, 24 - 16.0, 1.4); horn(b, 24 - 7.0, 3.9); strobe(b, 24 - 17.2, 3.9)
        hazard_plaque(b, 24 - 5.0, 2.4, 'x')
