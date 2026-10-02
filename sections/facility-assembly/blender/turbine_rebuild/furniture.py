"""Shared furniture: operator chair. Local frame: seat faces +x, backrest at -x."""
import math

def _arc_ring(cx, cy, r_out, r_in, a0, a1, n=14):
    out = [(cx + r_out * math.cos(a0 + (a1 - a0) * i / n), cy + r_out * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inn = [(cx + r_in * math.cos(a0 + (a1 - a0) * i / n), cy + r_in * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n, -1, -1)]
    return out + inn

def chair(b, x, y, rz=0.0, accent='oxide'):
    with b.push((x, y, 0), rz):
        for k in range(5):                                                                                       # five-star base: tapered legs, twin-wheel casters
            a = k * 2 * math.pi / 5 + .3; ca, sa = math.cos(a), math.sin(a)
            b.rod((.05 * ca, .05 * sa, .17), (.3 * ca, .3 * sa, .085), .022, 'steel_dark', 8)
            b.box((.34 * ca, .34 * sa, .105), (.05, .05, .05), 'steel_dark', (0, 0, a), bev=.005)
            for s in (-1, 1):
                wx, wy = .34 * ca - s * .018 * sa, .34 * sa + s * .018 * ca
                b.lathe((wx, wy, .05), [(0, -.007), (.028, -.007), (.032, 0), (.028, .007), (0, .007)], 'rubber', 12, axis='X' if abs(ca) < .7 else 'Y')
        b.lathe((0, 0, .14), [(0, 0), (.07, 0), (.075, .03), (.05, .06), (0, .06)], 'trim_black', 16)               # hub
        b.lathe((0, 0, .2), [(0, 0), (.03, 0), (.03, .2), (0, .2)], 'steel_light', 12)                                # gas lift column
        b.lathe((0, 0, .26), [(0, 0), (.05, 0), (.045, .1), (.036, .2), (0, .2)], 'trim_black', 16)                   # bellows cover
        b.box((0, 0, .45), (.3, .3, .03), 'steel_dark', bev=.01)                                                      # seat pan
        seat = [(.22, -.2), (.22, .2), (.1, .26), (-.18, .24), (-.22, .18), (-.22, -.18), (-.18, -.24), (.1, -.26)]
        b.prism(seat, .08, 'slate_dark', (0, 0, .5), True, 'Z', bev=.03)                                                # fabric seat cushion
        b.prism([(.2, -.16), (.2, .16), (.1, .22), (-.16, .2), (-.2, .15), (-.2, -.15), (-.16, -.2), (.1, -.22)], .012, accent, (0, 0, .547), True, 'Z', bev=.004)   # accent inlay
        b.prism(_arc_ring(.08, 0, .275, .235, math.radians(180 - 58), math.radians(180 + 58)), .46, 'slate_dark', (0, 0, .88), True, 'Z', bev=.02)          # curved backrest shell
        b.prism(_arc_ring(.08, 0, .28, .27, math.radians(180 - 48), math.radians(180 + 48)), .3, accent, (0, 0, .88), True, 'Z', bev=.004)                    # stitched insert
        b.prism(_arc_ring(.08, 0, .24, .23, math.radians(180 - 50), math.radians(180 + 50)), .4, 'trim_black', (0, 0, .88), True, 'Z', bev=.004)                # back panel
        b.sweep([(-.14, 0, .48), (-.26, 0, .55), (-.215, 0, .7)], .014, 'steel_dark', 8, .08); b.box((-.2, 0, .7), (.05, .1, .1), 'trim_black', bev=.01)      # backrest stem + mount
        b.rod((-.12, 0, .45), (-.12, 0, .44), .02, 'steel_dark', 8); b.box((-.1, .1, .43), (.06, .03, .05), 'steel_mid', bev=.004)                                # tilt lever
        for s in (-1, 1):                                                                                        # armrests: post, pad
            b.rod((-.02, s * .26, .5), (-.02, s * .26, .68), .016, 'steel_dark', 8)
            b.box((.02, s * .26, .7), (.3, .07, .04), 'trim_black', bev=.016)
