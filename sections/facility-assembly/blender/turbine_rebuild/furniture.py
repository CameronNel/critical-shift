"""Shared furniture: operator chair. Local frame: seat faces +x, backrest at -x."""
import math

def chair(b, x, y, rz=0.0, accent='oxide'):
    with b.push((x, y, 0), rz):
        for k in range(5):                                                                                       # five-star base with casters
            a = k * 2 * math.pi / 5 + .3; ca, sa = math.cos(a), math.sin(a)
            b.box((.17 * ca, .17 * sa, .105), (.36, .05, .035), 'steel_dark', (0, 0, a), bev=.01)
            b.cyl((.33 * ca, .33 * sa, .052), .03, .05, 'rubber', 'Y', 12, bev=.006)
            b.cyl((.33 * ca, .33 * sa, .082), .018, .05, 'steel_mid', 'Z', 8)
        b.cyl((0, 0, .15), .06, .08, 'trim_black', 'Z', 16, bev=.008)
        b.cyl((0, 0, .31), .032, .32, 'steel_light', 'Z', 12)                                                    # gas lift
        b.cyl((0, 0, .36), .05, .2, 'trim_black', 'Z', 16, r2=.036, bev=.006)
        b.box((0, 0, .45), (.3, .3, .035), 'steel_dark', bev=.012)                                              # seat pan
        oct_ring = [(.27 * math.cos(math.pi / 8 + k * math.pi / 4), .27 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
        b.prism(oct_ring, .09, 'rubber', (0, 0, .5), True, 'Z', bev=.035)
        b.prism([(r * .96 * math.cos(math.atan2(py, px)), r * .96 * math.sin(math.atan2(py, px))) for (px, py) in oct_ring for r in [math.hypot(px, py)]], .02, accent, (0, 0, .466), True, 'Z', bev=.006)   # piping
        for s in (-1, 1):                                                                                        # curved backrest in three panels
            b.box((-.27, s * .17, .93), (.07, .2, .5), 'rubber', (0, 0, -s * .5), bev=.025)
        b.box((-.3, 0, .93), (.07, .22, .5), 'rubber', bev=.025)
        b.box((-.285, 0, .93), (.012, .16, .36), accent, bev=.004)                                              # stitched insert
        b.rod((-.2, 0, .53), (-.29, 0, .72), .02, 'steel_dark', 8); b.box((-.29, 0, .68), (.05, .12, .09), 'trim_black', bev=.01)
        for s in (-1, 1):                                                                                        # armrests
            b.rod((.0, s * .28, .53), (.0, s * .28, .68), .016, 'steel_dark', 8)
            b.box((.02, s * .28, .71), (.3, .07, .04), 'trim_black', bev=.016)
