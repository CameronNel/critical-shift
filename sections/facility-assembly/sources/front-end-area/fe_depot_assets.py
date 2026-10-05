"""Mine surface depot props. Vehicles are built with the length along +x (front toward +x), standing on z = 0; wheels use fe_assets_yard.wheel.
Lettering is never modelled: names and numbers come from the baked atlas (fe_signs) on instances."""
import math, random
from fe_kit import *
from fe_propkit import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import wheel, lowpoly_boxes, panel, panel_yz, arc_pts, tube, bezier, hazard_band, p_panel_xz

WHITE = (0.86, 0.86, 0.84, 1); ORANGE = (0.9, 0.4, 0.05, 1); DARK = (0.06, 0.06, 0.07, 1); STEEL = (0.72, 0.74, 0.76, 1); AMBER = (1.0, 0.62, 0.1, 1)

def _lamp(m, x, y, z, w, h, rgba, side=1, depth=0.05):
    """Lamp unit on a face with normal +x (side=1) or -x: dark bezel with an emissive lens set into it."""
    m.rbox(x, y, z, depth, w, h, 0.012, mi=I['plastic'], rgba=(0.07, 0.07, 0.08, 1))
    m.rbox(x + side * depth * 0.45, y, z, 0.012, w * 0.82, h * 0.78, 0.004, mi=I['emissive'], rgba=rgba)

def _arches(m, xs, R, rc, wy0, wy1, flare_out, paint_flare, liner=True):
    """Wheel arch features for each wheel centre x: dark liner disc behind the tyre and a rubber flare ring on the outside."""
    for x in xs:
        for sy in (-1, 1):
            if liner: panel(m, arc_pts(x, 0.42, R - 0.01, 0, 180, 12), sy * wy0, sy * wy1, 0.0, I['steel_charcoal'], (0.03, 0.03, 0.035, 1))
            panel(m, arc_pts(x, 0.42, R + 0.06, 0, 180, 12) + arc_pts(x, 0.42, R - 0.005, 180, 0, 12), sy * (wy1 - 0.02), sy * flare_out, 0.006, I['plastic'], paint_flare)

def site_pickup(F, P, paint=WHITE):
    """Crew-cab 4x4 pickup 5.3 m: arch-cut body skins with rubber flares, four door panels with handles, A/B/C pillars, tinted glass over a seated interior, bonnet with power dome,
    grille with bars, headlamp units, steel bull bar with tow hooks and spot lamps, mirrors, wipers, side steps, mud flaps, load bed with ribbed floor, wheel humps, tailgate, tail lamps,
    plate holder, tow ball, ladder rack, roof light bar, exhaust and ladder frame underneath, tow strap, toolbox and extinguisher in the bed."""
    m = lowpoly_boxes(mb(F)); L, W = 5.3, 1.95; PA = I['paint']; ST = I['steel_charcoal']; PL = I['plastic']; RB = I['rubber']; GL = I['glass']; EM = I['emissive']
    low = tuple(c * 0.78 for c in paint[:3]) + (1,); hi = tuple(min(1, c * 1.04) for c in paint[:3]) + (1,); gr = (0.2, 0.21, 0.23, 1); ch = (0.62, 0.64, 0.67, 1)
    H = W / 2; X1 = 1.62
    # ---- underbody: frame rails, axles, diffs, shafts, exhaust, tank
    m.rbox(-0.05, 0, 0.7, 4.9, 1.3, 0.5, 0.03, mi=ST, rgba=(0.03, 0.03, 0.035, 1))
    for sy in (-1, 1):
        m.rbox(-0.05, sy * 0.48, 0.38, 4.8, 0.1, 0.16, 0.02, mi=ST, rgba=gr)
        m.rbox(-1.62, sy * 0.62, 0.52, 1.5, 0.05, 0.035, 0.01, mi=ST, rgba=gr); m.rbox(-1.62, sy * 0.62, 0.48, 1.3, 0.05, 0.03, 0.01, mi=ST, rgba=gr)   # leaf springs
    for x in (-X1, X1):
        m.between((x, -0.78, 0.42), (x, 0.78, 0.42), 0.05, seg=8, mi=ST, rgba=gr); m.sphere(x, 0, 0.42, 0.17, 0.13, 0.13, rings=6, seg=10, mi=ST, rgba=(0.14, 0.14, 0.15, 1))
    m.between((-1.6, 0, 0.42), (1.6, 0, 0.42), 0.04, seg=8, mi=ST, rgba=(0.12, 0.12, 0.13, 1)); m.rbox(0.2, 0, 0.38, 0.5, 0.34, 0.3, 0.04, mi=ST, rgba=gr)
    m.rbox(-0.9, 0.3, 0.42, 0.9, 0.5, 0.2, 0.05, mi=ST, rgba=(0.14, 0.14, 0.15, 1))                         # fuel tank
    tube(m, [(1.2, -0.3, 0.36), (-1.0, -0.34, 0.34), (-2.3, -0.4, 0.34)], 0.032, seg=8, mi=ST, rgba=(0.3, 0.22, 0.17, 1))
    m.add(p_cyl(0.085, 0.55, 12), (-2.0, -0.4, 0.36), (0, math.pi / 2, 0), mi=ST, rgba=(0.3, 0.26, 0.22, 1))
    tube(m, [(-2.3, -0.4, 0.34), (-2.58, -0.45, 0.3), (-2.66, -0.5, 0.22)], 0.032, seg=8, mi=ST, rgba=(0.45, 0.45, 0.47, 1))
    # ---- body skins with wheel arches
    skin = [(-2.62, 0.42)] + arc_pts(-X1, 0.42, 0.5, 180, 0, 12) + arc_pts(X1, 0.42, 0.5, 180, 0, 12)[:0]
    skin = [(-2.62, 0.42), (-2.12, 0.42)] + arc_pts(-X1, 0.42, 0.5, 180, 0, 12) + [(-1.12, 0.42), (1.12, 0.42)] + arc_pts(X1, 0.42, 0.5, 180, 0, 12) + [(2.12, 0.42), (2.62, 0.42), (2.62, 0.96), (2.4, 1.04), (1.25, 1.08), (-0.68, 1.08), (-0.68, 1.38), (-2.62, 1.38)]
    for sy in (-1, 1):
        panel(m, skin, sy * (H - 0.07), sy * H, 0.01, PA, paint)
        panel(m, [(-1.1, 0.42), (1.1, 0.42), (1.1, 0.62), (-1.1, 0.62)], sy * (H - 0.03), sy * (H + 0.012), 0.004, PA, low)   # rocker panel
    _arches(m, (-X1, X1), 0.5, 0.64, 0.9, 1.04, True and 1.045, (0.07, 0.07, 0.08, 1))
    m.rbox(0, 0, 0.74, 2.2, 1.8, 0.62, 0.02, mi=PA, rgba=paint)                                              # cab sill body between the arches
    m.rbox(1.9, 0, 0.995, 1.45, 1.84, 0.14, 0.03, mi=PA, rgba=paint)                                        # deck above the front arches
    m.rbox(-1.62, 0, 0.9, 2.1, 1.84, 0.06, 0.01, mi=PA, rgba=low)                                           # bed support
    # ---- bonnet, front fascia, grille, lamps
    m.rbox(1.92, 0, 1.075, 1.3, 1.62, 0.05, 0.03, rot=(0, 0.03, 0), mi=PA, rgba=hi)                         # bonnet
    m.rbox(1.95, 0, 1.115, 0.95, 0.56, 0.035, 0.016, mi=PA, rgba=hi)                                        # power dome
    for k in range(4): m.rbox(1.98 + k * 0.1 - 0.15, 0, 1.136, 0.04, 0.4, 0.008, 0, mi=ST, rgba=(0.05, 0.05, 0.06, 1))
    for sy in (-1, 1): m.rbox(1.92, sy * 0.81, 1.1, 1.3, 0.012, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))   # bonnet shut lines
    m.rbox(1.3, 0, 1.1, 0.012, 1.62, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
    m.rbox(2.55, 0, 0.74, 0.14, 1.86, 0.64, 0.05, mi=PA, rgba=paint)                                        # front fascia
    m.rbox(2.62, 0, 0.8, 0.05, 1.04, 0.3, 0.02, mi=ST, rgba=(0.05, 0.05, 0.06, 1))                         # grille opening
    for k in range(6): m.rbox(2.645, 0, 0.68 + k * 0.045, 0.02, 1.0, 0.02, 0.006, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(2.65, 0, 0.8, 0.02, 0.012, 0.3, 0, mi=ST, rgba=(0.5, 0.5, 0.52, 1)); m.rbox(2.65, 0, 0.82, 0.03, 0.14, 0.06, 0.012, mi=ST, rgba=(0.4, 0.4, 0.42, 1))   # centre bar + badge blank
    for sy in (-1, 1):
        _lamp(m, 2.6, sy * 0.76, 0.82, 0.34, 0.2, (1.0, 0.95, 0.82, 1))
        m.rbox(2.64, sy * 0.76, 0.69, 0.04, 0.34, 0.05, 0.015, mi=EM, rgba=(1.0, 0.5, 0.05, 1))             # indicator
    m.rbox(2.72, 0, 0.5, 0.18, 1.94, 0.26, 0.05, mi=ST, rgba=(0.09, 0.09, 0.1, 1))                          # bumper
    m.rbox(2.74, 0, 0.58, 0.1, 1.5, 0.05, 0.015, mi=ST, rgba=(0.55, 0.56, 0.58, 1))
    m.rbox(2.55, 0, 0.36, 0.24, 1.2, 0.04, 0.015, mi=ST, rgba=(0.12, 0.12, 0.13, 1))                        # skid plate
    for sy in (-1, 1):
        tube(m, [(2.72, sy * 0.62, 0.5), (2.82, sy * 0.62, 0.62), (2.82, sy * 0.62, 1.08)], 0.034, seg=8, mi=ST, rgba=(0.06, 0.06, 0.07, 1))     # bull bar
        m.add(p_cyl(0.06, 0.07, 14), (2.84, sy * 0.3, 1.0), (0, math.pi / 2, 0), mi=EM, rgba=(1.0, 0.95, 0.85, 1)); m.rbox(2.78, sy * 0.3, 1.0, 0.1, 0.16, 0.16, 0.03, mi=ST, rgba=(0.06, 0.06, 0.07, 1))
        m.add(p_torus(0.04, 0.012, 10, 5), (2.8, sy * 0.4, 0.44), (0, math.pi / 2, 0), mi=I['paint'], rgba=(0.75, 0.1, 0.06, 1))   # tow hooks
    tube(m, [(2.82, -0.62, 1.08), (2.82, 0.62, 1.08)], 0.034, seg=8, mi=ST, rgba=(0.06, 0.06, 0.07, 1)); tube(m, [(2.82, -0.62, 0.78), (2.82, 0.62, 0.78)], 0.026, seg=8, mi=ST, rgba=(0.06, 0.06, 0.07, 1))
    # ---- cab: roof, pillars, glass, interior
    m.rbox(0.28, 0, 1.82, 1.6, 1.8, 0.07, 0.03, mi=PA, rgba=hi)                                               # roof
    m.rbox(0.3, 0, 1.86, 1.1, 1.3, 0.025, 0.01, mi=PA, rgba=paint)
    m.rbox(1.12, 0, 1.82, 0.14, 1.82, 0.06, 0.02, mi=PA, rgba=paint)                                         # sun visor
    m.rbox(0.3, 0, 1.43, 1.8, 1.62, 0.66, 0.02, mi=ST, rgba=(0.025, 0.025, 0.03, 1))                          # dark interior volume
    m.rbox(0.07, 0, 1.2, 0.5, 1.3, 0.14, 0.03, mi=ST, rgba=(0.06, 0.06, 0.07, 1)); m.rbox(1.0, 0, 1.2, 0.4, 1.5, 0.12, 0.04, mi=PL, rgba=(0.08, 0.08, 0.09, 1))    # dash
    m.torus(0.88, 0.42, 1.38, 0.15, 0.015, ns=20, nt=6, rot=(0, -0.6, 0), mi=PL, rgba=(0.05, 0.05, 0.06, 1))
    for sy in (-1, 1):
        m.cushion(0.3, sy * 0.4, 1.28, 0.5, 0.45, 0.14, r=0.04, levels=1, mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1))
        m.cushion(0.1, sy * 0.4, 1.55, 0.14, 0.45, 0.62, r=0.04, levels=1, rot=(0, -0.12, 0), mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1))
        m.rbox(0.07, sy * 0.4, 1.7, 0.06, 0.2, 0.1, 0.02, mi=PL, rgba=(0.08, 0.08, 0.09, 1))
    m.cushion(-0.35, 0, 1.3, 0.5, 1.4, 0.14, r=0.04, levels=1, mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1)); m.cushion(-0.55, 0, 1.5, 0.12, 1.4, 0.5, r=0.04, levels=1, mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1))
    m.rbox(1.0, -0.4, 1.285, 0.28, 0.22, 0.012, 0.004, rot=(0, 0, 0.15), mi=PL, rgba=(0.82, 0.82, 0.78, 1))     # clipboard on the dash
    # glass: windscreen, side windows, rear window
    panel(m, [(1.2, 1.09), (1.23, 1.09), (0.92, 1.76), (0.89, 1.76)], -0.83, 0.83, 0.0, GL, None)
    panel(m, [(1.19, 1.08), (1.235, 1.08), (0.925, 1.78), (0.885, 1.78)], -0.87, 0.87, 0.0, RB, (0.02, 0.02, 0.02, 1))
    m.rbox(1.1, 0, 1.5, 0.01, 1.7, 0.86, 0.02, rot=(0, -0.5, 0), mi=RB, rgba=(0.02, 0.02, 0.02, 1)) if False else None
    panel_yz(m, [(-0.75, 1.2), (0.75, 1.2), (0.75, 1.7), (-0.75, 1.7)], -0.64, -0.625, 0.0, GL, None)
    for sy in (-1, 1):
        yg = sy * (H - 0.04)
        panel(m, [(0.16, 1.14), (1.0, 1.14), (0.9, 1.84), (0.16, 1.84)], yg - 0.01, yg + 0.01, 0.0, GL, None) if False else None
        panel(m, [(0.14, 1.12), (1.0, 1.12), (0.84, 1.76), (0.14, 1.76)], sy * (H - 0.045), sy * (H - 0.025), 0.0, GL, None)
        panel(m, [(-0.55, 1.12), (0.04, 1.12), (0.04, 1.76), (-0.5, 1.76)], sy * (H - 0.045), sy * (H - 0.025), 0.0, GL, None)
        for (a, b) in (((0.14, 1.12), (1.0, 1.12)), ((0.14, 1.76), (0.84, 1.76))): m.between((a[0], sy * (H - 0.03), a[1]), (b[0], sy * (H - 0.03), b[1]), 0.012, seg=6, mi=RB, rgba=(0.02, 0.02, 0.02, 1))
        # pillars
        m.between((1.25, sy * (H - 0.07), 1.08), (0.9, sy * (H - 0.07), 1.78), 0.04, seg=8, mi=PA, rgba=paint)         # A
        m.rbox(0.09, sy * (H - 0.06), 1.44, 0.1, 0.08, 0.68, 0.02, mi=PA, rgba=paint)                                  # B
        m.rbox(-0.56, sy * (H - 0.07), 1.44, 0.1, 0.08, 0.68, 0.02, rot=(0, 0.12, 0), mi=PA, rgba=paint)               # C
        # door panels, cut lines, handles
        for (xa, xb, hx) in ((0.12, 1.04, 0.22), (-0.55, 0.06, -0.46)):
            panel(m, [(xa, 0.48), (xb, 0.48), (xb, 1.12), (xa, 1.12)], sy * (H - 0.002), sy * (H + 0.016), 0.01, PA, paint)
            m.rbox(hx, sy * (H + 0.026), 1.03, 0.14, 0.03, 0.03, 0.01, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
            m.rbox(hx + 0.12 * (1 if hx > 0 else 1), sy * (H + 0.02), 1.03, 0.012, 0.02, 0.02, 0, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
        m.rbox(0.56, sy * (H + 0.02), 0.5, 0.6, 0.02, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
        m.rbox(0.45, sy * (H + 0.1), 0.4, 1.5, 0.16, 0.035, 0.012, mi=ST, rgba=(0.12, 0.12, 0.13, 1))                # side step
        for k in range(9): m.rbox(-0.2 + k * 0.17, sy * (H + 0.14), 0.42, 0.04, 0.17, 0.006, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
        for x in (-0.25, 1.15): m.rbox(x, sy * (H + 0.07), 0.45, 0.05, 0.12, 0.1, 0.01, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
        # mirrors and wipers
        m.between((1.12, sy * (H - 0.02), 1.4), (1.1, sy * (H + 0.12), 1.42), 0.014, seg=6, mi=PL, rgba=(0.07, 0.07, 0.08, 1))
        m.rbox(1.08, sy * (H + 0.12), 1.45, 0.07, 0.1, 0.22, 0.03, mi=PL, rgba=(0.07, 0.07, 0.08, 1)); m.rbox(1.045, sy * (H + 0.12), 1.45, 0.012, 0.085, 0.19, 0.01, mi=I['steel_brushed'], rgba=(0.5, 0.52, 0.55, 1))
        m.between((1.14, sy * 0.3, 1.13), (0.98, sy * 0.3 + sy * 0.5, 1.45), 0.006, seg=4, mi=ST, rgba=(0.03, 0.03, 0.03, 1))
        m.rbox(0.3 + sy * 0.0, sy * 0.0, 0, 0, 0, 0, 0, mi=PA, rgba=paint) if False else None
        # roof rails & rear lamps
        m.between((-0.48, sy * 0.86, 1.87), (0.9, sy * 0.86, 1.87), 0.016, seg=6, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
        _lamp(m, -2.64, sy * 0.88, 1.12, 0.16, 0.34, (0.9, 0.08, 0.05, 1), side=-1)
        m.rbox(-2.65, sy * 0.88, 0.92, 0.04, 0.16, 0.06, 0.012, mi=EM, rgba=(1.0, 0.5, 0.05, 1))
        # mud flaps
        for x in (-X1 - 0.58, X1 - 0.58): m.rbox(x, sy * (H - 0.0), 0.27, 0.025, 0.3, 0.34, 0.008, mi=RB, rgba=(0.03, 0.03, 0.035, 1)); m.rbox(x, sy * (H - 0.0), 0.12, 0.03, 0.3, 0.05, 0.004, mi=RB, rgba=(0.5, 0.5, 0.52, 1)) if False else None
    # ---- load bed
    m.rbox(-1.65, 0, 0.99, 2.0, 1.72, 0.05, 0.01, mi=ST, rgba=(0.07, 0.07, 0.08, 1))                         # floor
    for k in range(9): m.rbox(-1.65, -0.7 + k * 0.175, 1.02, 1.96, 0.05, 0.02, 0.006, mi=ST, rgba=(0.1, 0.1, 0.11, 1))   # floor ribs
    m.rbox(-0.64, 0, 1.2, 0.05, 1.72, 0.4, 0.01, mi=PA, rgba=paint)                                          # headboard
    for sy in (-1, 1):
        m.rbox(-1.65, sy * (H - 0.1), 1.2, 2.0, 0.03, 0.34, 0.006, mi=PA, rgba=low)                              # inner side wall
        m.rbox(-1.65, sy * (H - 0.05), 1.39, 2.0, 0.17, 0.045, 0.02, mi=PA, rgba=hi)                            # top cap
        m.rbox(-X1, sy * 0.66, 1.1, 0.8, 0.34, 0.22, 0.08, mi=PA, rgba=paint)                                   # wheel humps
        m.rbox(-1.65, sy * (H - 0.08), 1.38, 1.9, 0.015, 0.015, 0, mi=ST, rgba=(0.05, 0.05, 0.06, 1))
    m.rbox(-2.6, 0, 1.18, 0.07, 1.74, 0.4, 0.02, mi=PA, rgba=paint)                                           # tailgate
    m.rbox(-2.65, 0, 1.24, 0.03, 1.55, 0.09, 0.015, mi=PA, rgba=hi); m.rbox(-2.66, 0, 1.1, 0.012, 1.2, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
    m.rbox(-2.67, 0, 1.3, 0.04, 0.34, 0.05, 0.015, mi=ST, rgba=(0.08, 0.08, 0.09, 1))                         # tailgate handle
    for sy in (-1, 1): m.cylz(-2.64, sy * 0.78, 1.34, 1.38, 0.018, seg=8, mi=ST, rgba=ch) if False else m.rbox(-2.64, sy * 0.78, 1.36, 0.05, 0.1, 0.04, 0.01, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(-2.72, 0, 0.5, 0.16, 1.94, 0.22, 0.05, mi=ST, rgba=(0.12, 0.12, 0.13, 1)); m.rbox(-2.74, 0, 0.62, 0.1, 1.2, 0.06, 0.02, mi=ST, rgba=(0.5, 0.5, 0.52, 1))   # rear bumper step
    m.rbox(-2.72, 0, 0.82, 0.02, 0.52, 0.13, 0.008, mi=PL, rgba=(0.82, 0.82, 0.78, 1)); m.rbox(-2.70, 0, 0.82, 0.03, 0.56, 0.17, 0.012, mi=ST, rgba=(0.06, 0.06, 0.07, 1))   # plate holder
    m.rbox(-2.74, -0.5, 0.74, 0.03, 0.1, 0.05, 0.01, mi=EM, rgba=(0.95, 0.95, 0.9, 1))                       # reversing lamp
    m.cylz(-2.8, 0.3, 0.52, 0.62, 0.016, seg=8, mi=ST, rgba=ch); m.sphere(-2.8, 0.3, 0.66, 0.04, rings=6, seg=10, mi=ST, rgba=ch)   # tow ball
    # ---- bed rack and cargo
    for sx in (-2.15, -1.0):
        tube(m, [(sx, -0.89, 1.41), (sx, -0.89, 1.88), (sx, 0.89, 1.88), (sx, 0.89, 1.41)], 0.022, seg=8, mi=ST, rgba=(0.07, 0.07, 0.08, 1))
    for sy in (-1, 1): m.between((-2.15, sy * 0.89, 1.88), (-0.5, sy * 0.89, 1.88), 0.02, seg=8, mi=ST, rgba=(0.07, 0.07, 0.08, 1))
    m.rbox(-0.85, 0.5, 1.2, 0.5, 0.9, 0.3, 0.03, mi=I['steel_brushed'], rgba=(0.45, 0.46, 0.48, 1)); m.rbox(-0.85, 0.5, 1.36, 0.52, 0.92, 0.02, 0.01, mi=ST, rgba=(0.1, 0.1, 0.11, 1))   # toolbox
    m.rbox(-0.85, 0.5, 1.2, 0.02, 0.1, 0.05, 0.004, mi=ST, rgba=(0.8, 0.8, 0.8, 1)) if False else None
    for k in range(3): m.torus(-1.5, -0.5, 1.07 + k * 0.045, 0.17, 0.034, ns=18, nt=6, mi=I['fabric'], rgba=(0.9, 0.42, 0.06, 1))   # coiled tow strap
    m.between((-1.5, -0.33, 1.1), (-1.2, -0.1, 1.03), 0.02, seg=6, mi=I['fabric'], rgba=(0.9, 0.42, 0.06, 1))
    m.cylz(-0.78, -0.72, 1.01, 1.28, 0.06, seg=12, mi=PL, rgba=(0.75, 0.08, 0.05, 1)); m.cylz(-0.78, -0.72, 1.28, 1.31, 0.028, seg=8, mi=ST, rgba=ch)   # extinguisher
    # ---- roof light bar, aerial, vent
    m.rbox(0.35, 0, 1.92, 0.2, 1.3, 0.07, 0.02, mi=ST, rgba=(0.06, 0.06, 0.07, 1))
    for k in range(5): m.rbox(0.46, -0.5 + k * 0.25, 1.92, 0.015, 0.2, 0.045, 0.005, mi=EM, rgba=AMBER)
    for sy in (-1, 1): m.rbox(0.35, sy * 0.62, 1.88, 0.1, 0.05, 0.05, 0.01, mi=ST, rgba=(0.06, 0.06, 0.07, 1))
    m.add(p_cyl(0.007, 0.6, 6), (-0.5, 0.88, 2.17), mi=ST, rgba=(0.04, 0.04, 0.04, 1)); m.cylz(-0.5, 0.88, 1.88, 1.92, 0.035, seg=10, mi=ST, rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(-0.1, 0, 1.875, 0.4, 0.3, 0.03, 0.01, mi=PA, rgba=paint)
    for sy in (-1, 1):
        for x in (-X1, X1): wheel(m, x, sy * 0.86, 0.42, r=0.42, w=0.3, flip=sy, rim=(0.55, 0.56, 0.58, 1))
    return m.finish('proto_site_pickup', P)

def crew_van(F, P, paint=WHITE):
    """Crew van 5.4 m: arch-cut skins with rubber flares, raked screen, bonded door glass, cab doors with handles, sliding side door with track, split rear doors with hinges and hazard strip,
    grille with bars, headlamp units, bumpers, mirrors, wipers, roof ribs, rack with ladder, jerry can and strap, beacon, mud flaps, underbody, exhaust, plate holder and tow eye."""
    m = lowpoly_boxes(mb(F)); L, W = 5.4, 2.0; PA = I['paint']; ST = I['steel_charcoal']; PL = I['plastic']; RB = I['rubber']; GL = I['glass']; EM = I['emissive']
    low = tuple(c * 0.78 for c in paint[:3]) + (1,); hi = tuple(min(1, c * 1.04) for c in paint[:3]) + (1,); gr = (0.2, 0.21, 0.23, 1); ch = (0.62, 0.64, 0.67, 1)
    H = W / 2; X1 = 1.65; dkp = (0.07, 0.07, 0.08, 1); wb = (0.02, 0.02, 0.02, 1)
    # ---- underbody
    m.rbox(0, 0, 0.7, 5.0, 1.34, 0.5, 0.03, mi=ST, rgba=(0.03, 0.03, 0.035, 1))
    for sy in (-1, 1):
        m.rbox(0, sy * 0.5, 0.38, 4.9, 0.1, 0.16, 0.02, mi=ST, rgba=gr)
        m.rbox(-1.65, sy * 0.64, 0.5, 1.4, 0.05, 0.035, 0.01, mi=ST, rgba=gr)
    for x in (-X1, X1):
        m.between((x, -0.8, 0.42), (x, 0.8, 0.42), 0.05, seg=8, mi=ST, rgba=gr); m.sphere(x, 0, 0.42, 0.17, 0.13, 0.13, rings=6, seg=10, mi=ST, rgba=(0.14, 0.14, 0.15, 1))
    m.between((-1.6, 0, 0.42), (1.6, 0, 0.42), 0.04, seg=8, mi=ST, rgba=(0.12, 0.12, 0.13, 1)); m.rbox(-0.6, 0.3, 0.42, 1.0, 0.5, 0.2, 0.05, mi=ST, rgba=(0.14, 0.14, 0.15, 1))
    tube(m, [(1.3, -0.3, 0.36), (-1.0, -0.34, 0.34), (-2.35, -0.4, 0.34)], 0.032, seg=8, mi=ST, rgba=(0.3, 0.22, 0.17, 1)); m.add(p_cyl(0.09, 0.55, 12), (-2.0, -0.4, 0.36), (0, math.pi / 2, 0), mi=ST, rgba=(0.3, 0.26, 0.22, 1))
    tube(m, [(-2.35, -0.4, 0.34), (-2.62, -0.45, 0.3), (-2.7, -0.5, 0.22)], 0.032, seg=8, mi=ST, rgba=(0.45, 0.45, 0.47, 1))
    # ---- skins (arch-cut side silhouette with sloped screen line and roof)
    skin = [(-2.65, 0.42), (-2.15, 0.42)] + arc_pts(-X1, 0.42, 0.5, 180, 0, 12) + [(-1.15, 0.42), (1.15, 0.42)] + arc_pts(X1, 0.42, 0.5, 180, 0, 12) + [(2.15, 0.42), (2.65, 0.42), (2.65, 0.98), (2.3, 1.07), (1.9, 1.1), (1.35, 1.98), (1.25, 2.08), (-2.55, 2.08), (-2.65, 1.98)]
    for sy in (-1, 1):
        panel(m, skin, sy * (H - 0.07), sy * H, 0.01, PA, paint)
        panel(m, [(-1.15, 0.42), (1.15, 0.42), (1.15, 0.64), (-1.15, 0.64)], sy * (H - 0.03), sy * (H + 0.012), 0.004, PA, low)
    _arches(m, (-X1, X1), 0.5, 0.64, 0.9, 1.04, 1.045, (0.07, 0.07, 0.08, 1))
    m.rbox(0, 0, 0.74, 2.3, 1.84, 0.62, 0.02, mi=PA, rgba=paint)
    m.rbox(-0.65, 0, 1.52, 3.9, 1.84, 1.0, 0.04, mi=PA, rgba=paint)                                          # cargo volume
    m.rbox(2.0, 0, 1.0, 1.3, 1.84, 0.14, 0.03, mi=PA, rgba=paint)
    m.rbox(-0.6, 0, 2.1, 3.7, 1.9, 0.07, 0.03, mi=PA, rgba=hi)                                               # roof
    for sy in (-0.5, 0, 0.5): m.rbox(-0.6, sy, 2.15, 3.6, 0.1, 0.03, 0.012, mi=PA, rgba=hi)                    # roof ribs
    m.rbox(1.45, 0, 2.05, 0.2, 1.86, 0.09, 0.03, rot=(0, -0.5, 0), mi=PA, rgba=paint)                        # header
    # ---- nose: bonnet, fascia, grille, lamps, bumper
    m.rbox(2.12, 0, 1.085, 0.9, 1.7, 0.05, 0.03, rot=(0, 0.1, 0), mi=PA, rgba=hi)
    m.rbox(2.12, 0, 1.115, 0.012, 1.7, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
    m.rbox(2.58, 0, 0.74, 0.14, 1.88, 0.64, 0.05, mi=PA, rgba=paint)
    m.rbox(2.66, 0, 0.86, 0.04, 0.95, 0.26, 0.02, mi=ST, rgba=(0.05, 0.05, 0.06, 1))
    for k in range(5): m.rbox(2.68, 0, 0.77 + k * 0.045, 0.02, 0.9, 0.018, 0.005, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(2.69, 0, 0.86, 0.025, 0.13, 0.07, 0.012, mi=ST, rgba=(0.4, 0.4, 0.42, 1))
    for sy in (-1, 1):
        _lamp(m, 2.64, sy * 0.76, 0.92, 0.4, 0.2, (1.0, 0.95, 0.82, 1))
        m.rbox(2.68, sy * 0.76, 0.76, 0.04, 0.4, 0.05, 0.015, mi=EM, rgba=(1.0, 0.5, 0.05, 1))
        m.rbox(2.7, sy * 0.72, 0.55, 0.04, 0.2, 0.1, 0.03, mi=ST, rgba=(0.04, 0.04, 0.05, 1)); m.rbox(2.72, sy * 0.72, 0.55, 0.012, 0.14, 0.06, 0.015, mi=EM, rgba=(1.0, 0.95, 0.85, 1))   # fog lamps
    m.rbox(2.72, 0, 0.5, 0.2, 1.96, 0.3, 0.07, mi=PL, rgba=(0.09, 0.09, 0.1, 1)); m.rbox(2.76, 0, 0.62, 0.1, 1.3, 0.04, 0.015, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(2.8, 0, 0.5, 0.02, 0.3, 0.1, 0.01, mi=PL, rgba=(0.82, 0.82, 0.78, 1))                              # plate blank
    m.add(p_torus(0.045, 0.014, 10, 5), (2.82, 0.55, 0.42), (0, math.pi / 2, 0), mi=I['paint'], rgba=(0.75, 0.1, 0.06, 1))   # tow eye
    # ---- glass and cab
    panel(m, [(1.88, 1.09), (1.915, 1.09), (1.36, 1.94), (1.325, 1.94)], -0.85, 0.85, 0.0, GL, None)
    panel(m, [(1.87, 1.07), (1.92, 1.07), (1.365, 1.96), (1.32, 1.96)], -0.9, 0.9, 0.0, RB, wb)
    m.rbox(1.3, 0, 1.4, 0.5, 1.5, 0.6, 0.03, mi=ST, rgba=(0.025, 0.025, 0.03, 1)); m.rbox(1.55, 0, 1.2, 0.5, 1.7, 0.12, 0.04, mi=PL, rgba=(0.08, 0.08, 0.09, 1))   # dash
    m.torus(1.15, 0.45, 1.45, 0.16, 0.016, ns=20, nt=6, rot=(0, -0.6, 0), mi=PL, rgba=(0.05, 0.05, 0.06, 1))
    for sy in (-1, 1):
        m.cushion(0.7, sy * 0.42, 1.3, 0.5, 0.45, 0.14, r=0.04, levels=1, mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1)); m.cushion(0.5, sy * 0.42, 1.6, 0.14, 0.45, 0.62, r=0.04, levels=1, rot=(0, -0.1, 0), mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1))
        m.rbox(0.48, sy * 0.42, 1.98, 0.06, 0.2, 0.1, 0.02, mi=PL, rgba=(0.08, 0.08, 0.09, 1))
    m.sphere(1.5, -0.4, 1.31, 0.09, 0.09, 0.06, rings=6, seg=12, mi=PL, rgba=(0.95, 0.78, 0.08, 1))             # hard hat on the dash
    m.rbox(1.65, 0.3, 1.275, 0.3, 0.22, 0.012, 0.004, rot=(0, 0, 0.2), mi=PL, rgba=(0.82, 0.82, 0.78, 1))
    for sy in (-1, 1):
        # door (cab) with glazed window, handle, cut lines
        door = [(0.0, 0.48), (1.12, 0.48), (1.12, 1.1), (1.78, 1.1), (1.35, 1.96), (0.0, 1.96)]
        panel(m, door, sy * (H - 0.002), sy * (H + 0.016), 0.01, PA, paint)
        panel(m, [(0.12, 1.3), (1.6, 1.3), (1.33, 1.84), (0.12, 1.84)], sy * (H + 0.012), sy * (H + 0.024), 0.0, GL, None)
        for a, b in (((0.12, 1.3), (1.6, 1.3)), ((1.6, 1.3), (1.33, 1.84)), ((1.33, 1.84), (0.12, 1.84)), ((0.12, 1.84), (0.12, 1.3))): m.between((a[0], sy * (H + 0.02), a[1]), (b[0], sy * (H + 0.02), b[1]), 0.011, seg=6, mi=RB, rgba=wb)
        m.rbox(0.14, sy * (H + 0.028), 1.05, 0.16, 0.03, 0.035, 0.012, mi=ST, rgba=dkp)
        m.rbox(0.5, sy * (H + 0.02), 0.5, 1.0, 0.012, 0.012, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
        # mirror, wiper
        m.between((1.55, sy * (H - 0.02), 1.55), (1.5, sy * (H + 0.14), 1.6), 0.016, seg=6, mi=PL, rgba=dkp)
        m.rbox(1.48, sy * (H + 0.2), 1.62, 0.08, 0.12, 0.3, 0.035, mi=PL, rgba=dkp); m.rbox(1.44, sy * (H + 0.2), 1.62, 0.012, 0.1, 0.26, 0.01, mi=I['steel_brushed'], rgba=(0.5, 0.52, 0.55, 1))
        m.between((1.78, sy * 0.15, 1.17), (1.52, sy * 0.15 + sy * 0.6, 1.62), 0.007, seg=4, mi=ST, rgba=(0.03, 0.03, 0.03, 1))
        # side steps, flares done; mud flaps
        for x in (-X1 - 0.6, X1 - 0.6): m.rbox(x, sy * H, 0.27, 0.025, 0.3, 0.34, 0.008, mi=RB, rgba=(0.03, 0.03, 0.035, 1))
        m.rbox(0.6, sy * (H + 0.12), 0.4, 1.3, 0.18, 0.03, 0.012, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
        # cargo-side detail: pressed ribs, orange band, quarter window on the plain side
        for z in (1.45, 1.75): m.rbox(-1.35, sy * (H + 0.008), z, 2.5, 0.016, 0.03, 0.006, mi=PA, rgba=hi)
        _lamp(m, -2.66, sy * 0.9, 1.1, 0.16, 0.44, (0.9, 0.08, 0.05, 1), side=-1)
        m.rbox(-2.67, sy * 0.9, 0.78, 0.04, 0.16, 0.06, 0.012, mi=EM, rgba=(1.0, 0.5, 0.05, 1))
        m.rbox(-1.3, sy * (H + 0.02), 1.22, 2.7, 0.012, 0.13, 0, mi=I['signage'], rgba=ORANGE)
    # sliding door on +y: panel, window, track, handle
    panel(m, [(-1.35, 0.5), (-0.08, 0.5), (-0.08, 1.96), (-1.35, 1.96)], H + 0.016, H + 0.04, 0.012, PA, paint)
    panel(m, [(-1.2, 1.3), (-0.2, 1.3), (-0.2, 1.84), (-1.2, 1.84)], H + 0.04, H + 0.052, 0.0, GL, None)
    m.rbox(-0.2, H + 0.06, 1.05, 0.06, 0.04, 0.2, 0.012, mi=ST, rgba=dkp)
    m.rbox(-1.6, H + 0.05, 0.98, 1.0, 0.04, 0.045, 0.01, mi=ST, rgba=(0.1, 0.1, 0.11, 1)); m.rbox(-1.0, H + 0.05, 2.02, 2.4, 0.04, 0.035, 0.01, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
    panel(m, [(-1.9, 1.3), (-1.55, 1.3), (-1.55, 1.84), (-1.9, 1.84)], -H + 0.012, -H - 0.01, 0.0, GL, None)     # quarter window on the plain side
    # ---- rear doors
    m.rbox(-2.68, 0, 1.22, 0.04, 1.84, 1.5, 0.03, mi=PA, rgba=paint)
    m.rbox(-2.705, 0, 1.22, 0.012, 0.014, 1.5, 0, mi=ST, rgba=(0.04, 0.04, 0.05, 1))
    for sy in (-1, 1):
        panel_yz(m, [(sy * 0.45 - 0.35, 1.3), (sy * 0.45 + 0.35, 1.3), (sy * 0.45 + 0.35, 1.82), (sy * 0.45 - 0.35, 1.82)], -2.712, -2.7, 0.0, GL, None)
        m.rbox(-2.7, sy * 0.45, 1.55, 0.01, 0.75, 0.55, 0.02, mi=RB, rgba=wb) if False else None
        for z in (0.66, 1.78): m.rbox(-2.7, sy * 0.92, z, 0.05, 0.05, 0.12, 0.01, mi=ST, rgba=(0.55, 0.56, 0.58, 1))     # hinges
    m.rbox(-2.715, 0.12, 1.0, 0.025, 0.05, 0.14, 0.012, mi=ST, rgba=dkp)
    hazard_band(m, -2.705, -0.88, 0.88, 0.66, 0.8, side=-1, w=0.1, slant=0.1)
    m.rbox(-2.84, 0, 0.5, 0.2, 1.96, 0.26, 0.06, mi=PL, rgba=(0.09, 0.09, 0.1, 1)); m.rbox(-2.88, 0, 0.62, 0.1, 1.3, 0.04, 0.015, mi=ST, rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(-2.74, 0, 0.85, 0.02, 0.5, 0.12, 0.008, mi=PL, rgba=(0.82, 0.82, 0.78, 1)); m.rbox(-2.72, 0, 0.85, 0.03, 0.54, 0.16, 0.012, mi=ST, rgba=dkp)
    m.rbox(-2.74, 0.48, 0.9, 0.03, 0.1, 0.05, 0.01, mi=EM, rgba=(0.95, 0.95, 0.9, 1))
    # ---- roof gear: rack, ladder, jerry can, strap, beacon, vent
    for x in (-1.9, -0.6, 0.7): m.rbox(x, 0, 2.2, 0.06, 1.84, 0.05, 0.015, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
    for sy in (-1, 1):
        m.rbox(-0.6, sy * 0.88, 2.2, 2.9, 0.06, 0.05, 0.015, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
        for x in (-1.9, -0.6, 0.7): m.rbox(x, sy * 0.88, 2.15, 0.06, 0.06, 0.08, 0.01, mi=ST, rgba=gr)
        m.between((-1.9, sy * 0.28, 2.3), (0.7, sy * 0.28, 2.3), 0.022, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for k in range(10): m.between((-1.85 + k * 0.27, -0.28, 2.3), (-1.85 + k * 0.27, 0.28, 2.3), 0.012, seg=6, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(-1.5, 0.62, 2.37, 0.4, 0.17, 0.4, 0.03, mi=PL, rgba=(0.75, 0.08, 0.05, 1)); m.rbox(-1.5, 0.62, 2.6, 0.12, 0.05, 0.05, 0.01, mi=ST, rgba=dkp)   # jerry can
    for k in range(3): m.torus(-0.1, -0.62, 2.27 + k * 0.04, 0.15, 0.03, ns=16, nt=6, mi=I['fabric'], rgba=(0.9, 0.42, 0.06, 1))                         # strap coil
    m.cylz(1.0, 0.0, 2.14, 2.22, 0.1, seg=12, mi=PL, rgba=(0.8, 0.8, 0.78, 1)); m.cylz(0.7, 0.62, 2.22, 2.3, 0.035, seg=8, mi=ST, rgba=dkp); m.add(p_cyl(0.1, 0.09, 14), (0.7, 0.62, 2.34), mi=EM, rgba=AMBER)
    m.rbox(0.9, 0, 2.2, 0.16, 1.2, 0.05, 0.015, mi=ST, rgba=dkp)
    for k in range(4): m.rbox(0.99, -0.45 + k * 0.3, 2.2, 0.012, 0.2, 0.035, 0, mi=EM, rgba=AMBER)
    for sy in (-1, 1):
        for x in (-X1, X1): wheel(m, x, sy * 0.88, 0.4, r=0.42, w=0.3, flip=sy, rim=(0.55, 0.56, 0.58, 1))
    return m.finish('proto_crew_van', P)

def _ore_heap(m, rnd, cx, cy, cz, ax, ay, hh, n_med=60, n_big=8, base_col=(0.06, 0.055, 0.05, 1), sc=1.0):
    """Ore heap: an angular displaced core plus a dense cover of dark broken lumps, with a few copper-green and rusty chunks."""
    pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=2, radius=1.0)
    for v in res['verts']:
        k = 1.0 + 0.14 * math.sin(v.co.x * 6 + cx) * math.cos(v.co.y * 5) + rnd.uniform(-0.1, 0.1)
        v.co = Vector((v.co.x * ax * 0.97 * k, v.co.y * ay * 0.97 * k, max(v.co.z, -0.1) * hh * 0.9 * k))
    bmesh.ops.delete(pb, geom=[f for f in pb.faces if sum(v.co.z for v in f.verts) / 3 < -0.04], context='FACES')
    add_var(m, pb, (cx, cy, cz), mi=I['props'], rgba=base_col, var=0.3, rnd=rnd)
    dark = [(0.055, 0.052, 0.05, 1), (0.09, 0.085, 0.08, 1), (0.04, 0.042, 0.05, 1), (0.14, 0.125, 0.11, 1), (0.07, 0.065, 0.075, 1)]
    rust = [(0.30, 0.12, 0.05, 1), (0.38, 0.17, 0.06, 1)]; green = [(0.08, 0.27, 0.20, 1), (0.12, 0.34, 0.24, 1)]
    def hz(x, y): return cz + hh * math.sqrt(max(0.0, 1 - (x / ax) ** 2 - (y / ay) ** 2))
    for i in range(n_med + n_big):
        big = i >= n_med
        a = rnd.uniform(0, 6.283); d = rnd.uniform(0.0, 1.0) ** 0.6 * 0.98; x = math.cos(a) * ax * d; y = math.sin(a) * ay * d
        s = (rnd.uniform(0.11, 0.17) if big else rnd.uniform(0.07, 0.125)) * sc
        j = i % 13
        col = rnd.choice(green) if j == 3 else rnd.choice(rust) if j in (6, 10) else rnd.choice(dark)
        add_var(m, p_rock(rnd, s, 0.72, 0.32, 1 if big else 0), (cx + x, cy + y, hz(x, y) - s * 0.2), (rnd.uniform(-.4, .4), rnd.uniform(-.4, .4), rnd.uniform(0, 6.28)), mi=I['paint'], rgba=col, var=0.3, rnd=rnd)

def ore_car(F, P):
    """Mine tipper car 2.4 m on rail (gauge 1.56 m): rust-red riveted tub with rolled rim, angle ribs, stencil band and number plate (the baked car number sits flush on it),
    channel underframe, hung axle boxes, spoked iron wheels, sprung buffers and a hook coupling, brake lever, heaped with dark ore with copper-green and rusty chunks."""
    m = mb(F); rnd = random.Random(4); RED = (0.40, 0.125, 0.065, 1); RED2 = (0.30, 0.095, 0.055, 1); BAND = (0.74, 0.52, 0.09, 1); GR = (0.07, 0.07, 0.08, 1); BR = (0.55, 0.53, 0.5, 1)
    m.add(p_frustum(2.0, 1.28, 2.34, 1.56, 0.68, 0.025), (0, 0, 0.62), mi=I['paint'], rgba=RED)                 # tub body
    m.rbox(0, 0, 1.24, 2.26, 1.48, 0.04, 0.0, mi=I['props'], rgba=(0.06, 0.055, 0.05, 1))                       # ore bed
    for sy in (-1, 1):
        m.rbox(0, sy * 0.775, 1.31, 2.42, 0.1, 0.08, 0.018, seg=1, mi=I['paint'], rgba=RED2)                    # rolled rim
        m.rbox(0, sy * 0.68, 0.62, 2.1, 0.06, 0.05, 0.01, seg=1, mi=I['steel_charcoal'])                         # bottom angle
        for x in (-0.9, -0.45, 0.45, 0.9):
            m.rbox(x, sy * 0.725, 0.97, 0.06, 0.035, 0.66, 0.007, rot=(-sy * 0.203, 0, 0), seg=1, mi=I['paint'], rgba=RED2)   # angle rib
            studs(m, [(x, sy * 0.75, z) for z in (0.7, 1.22)], '+y' if sy > 0 else '-y', r=0.016, h=0.014, mi=I['steel_charcoal'])
        m.rbox(0, sy * 0.727, 1.0, 2.1, 0.014, 0.11, 0.003, rot=(-sy * 0.203, 0, 0), seg=1, mi=I['paint'], rgba=BAND)       # stencil band
        m.rbox(0, sy * 0.674, 0.72, 0.62, 0.014, 0.28, 0.004, seg=1, mi=I['steel_charcoal'])                      # number plate backing
        studs(m, [(sx * 0.27, sy * 0.683, 0.72 + sz * 0.11) for sx in (-1, 1) for sz in (-1, 1)], '+y' if sy > 0 else '-y', r=0.012, h=0.01, seg=5, mi=I['steel_brushed'])
        for k in range(8):                                                                                       # seam rivets, lower seam
            x = -1.0 + k * 0.285 + (0.0 if k % 2 else 0.0)
            if abs(x) < 0.4 and False: continue
            studs(m, [(x, sy * 0.687, 0.84)], '+y' if sy > 0 else '-y', r=0.012, h=0.01, mi=I['steel_charcoal'])
    for sx in (-1, 1):
        m.rbox(sx * 1.165, 0, 1.31, 0.1, 1.56, 0.08, 0.018, seg=1, mi=I['paint'], rgba=RED2)
        for y in (-0.5, 0.0, 0.5): m.rbox(sx * 1.14, y, 0.97, 0.035, 0.07, 0.62, 0.007, rot=(0, sx * 0.1, 0), seg=1, mi=I['paint'], rgba=RED2)
        studs(m, [(sx * 1.095, y, z) for y in (-0.5, 0.0, 0.5) for z in (0.7, 1.2)], '+x' if sx > 0 else '-x', r=0.015, h=0.012, mi=I['steel_charcoal'])
        for sy in (-1, 1): m.rbox(sx * 1.165, sy * 0.775, 1.31, 0.14, 0.14, 0.1, 0.02, seg=1, mi=I['paint'], rgba=RED2)      # rim corner caps
        # headstock, buffers, drawbar and coupling
        m.rbox(sx * 1.1, 0, 0.56, 0.1, 1.2, 0.14, 0.012, seg=1, mi=I['steel_charcoal'])
        for sy in (-1, 1):
            m.add(p_cyl(0.04, 0.2, 8), (sx * 1.22, sy * 0.4, 0.56), (0, math.pi / 2, 0), mi=I['steel_charcoal'])
            m.add(p_cyl(0.09, 0.035, 12), (sx * 1.335, sy * 0.4, 0.56), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=BR)
        m.between((sx * 1.05, 0, 0.56), (sx * 1.34, 0, 0.56), 0.03, seg=6, mi=I['steel_charcoal'])
    m.add(p_torus(0.07, 0.016, 12, 5), (1.36, 0, 0.56), (math.pi / 2, 0, 0), mi=I['steel_charcoal'])           # coupling link
    m.rbox(-1.34, 0, 0.56, 0.1, 0.06, 0.1, 0.01, seg=1, mi=I['steel_charcoal']); m.between((-1.34, -0.04, 0.6), (-1.34, -0.04, 0.46), 0.012, seg=5, mi=I['steel_brushed'], rgba=BR)   # hook and pin
    for sy in (-1, 1):
        m.rbox(0, sy * 0.46, 0.52, 2.2, 0.1, 0.12, 0.012, seg=1, mi=I['steel_charcoal'])                         # underframe channels
    for x in (-0.8, 0.0, 0.8): m.rbox(x, 0, 0.55, 0.08, 1.0, 0.1, 0.01, seg=1, mi=I['steel_charcoal'])
    for sx in (-0.8, 0.8):
        m.between((sx, -0.84, 0.26), (sx, 0.84, 0.26), 0.026, seg=6, mi=I['steel_charcoal'])                    # axle
        for sy in (-1, 1):
            m.add(p_wheel_spoked(0.21, 0.05, 5, 16), (sx, sy * 0.77, 0.26), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=GR)
            m.rbox(sx, sy * 0.66, 0.30, 0.15, 0.1, 0.17, 0.014, seg=1, mi=I['steel_charcoal'])                  # axle box
            m.rbox(sx, sy * 0.66, 0.40, 0.12, 0.085, 0.03, 0.006, seg=1, mi=I['steel_brushed'], rgba=BR)        # box lid
            m.rbox(sx, sy * 0.66, 0.46, 0.05, 0.05, 0.16, 0.008, seg=1, mi=I['steel_charcoal'])                 # hanger
            m.add(p_cyl(0.035, 0.03, 6), (sx, sy * 0.81, 0.26), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR)   # axle end cap
    m.between((0.95, 0.70, 0.58), (0.95, 0.88, 1.02), 0.012, seg=5, mi=I['steel_charcoal'])                     # brake lever with ball handle
    m.sphere(0.95, 0.885, 1.04, 0.032, rings=4, seg=6, mi=I['plastic'], rgba=(0.1, 0.1, 0.11, 1))
    m.rbox(0.95, 0.69, 0.58, 0.05, 0.05, 0.06, 0.008, seg=1, mi=I['steel_charcoal'])
    _ore_heap(m, rnd, 0.0, 0.0, 1.25, 1.1, 0.72, 0.34, n_med=52, n_big=6, sc=0.85)
    weather(m, 4, dirt=0.4, dirt_h=0.3, streak=0.22, blotch=0.2)
    return m.finish('proto_ore_car', P)

def ore_pile(F, P, seed=0, r=1.4, h=1.1):
    """Heap of broken ore: angular displaced mound plus loose dark lumps with rusty and copper-green chunks, spilling around the foot."""
    rnd = random.Random(seed); m = mb(F)
    base = [(0.06, 0.055, 0.05, 1), (0.07, 0.05, 0.035, 1), (0.04, 0.04, 0.045, 1)][seed % 3]
    _ore_heap(m, rnd, 0.0, 0.0, 0.0, r, r * 0.86, h, n_med=95, n_big=12, base_col=base, sc=1.45)
    for k in range(22):                                                                          # spill at the foot
        a = rnd.uniform(0, 6.283); d = rnd.uniform(0.9, 1.25) * r; x = math.cos(a) * d; y = math.sin(a) * d * 0.86; s = rnd.uniform(0.03, 0.08)
        add_var(m, p_rock(rnd, s, 0.7, 0.3, 0), (x, y, s * 0.2), (0, 0, rnd.uniform(0, 6.28)), mi=I['paint'], rgba=rnd.choice([(0.07, 0.065, 0.06, 1), (0.12, 0.10, 0.09, 1), (0.28, 0.13, 0.06, 1), (0.10, 0.28, 0.2, 1)]), var=0.3, rnd=rnd)
    weather(m, seed, dirt=0.5, dirt_h=0.18, streak=0.0, blotch=0.25)
    return m.finish(f'proto_ore_pile_{seed}', P)

def site_cabin(F, P):
    """Portable site cabin 6.0 x 2.6 x 2.7: pressed-steel body, plinth, roof overhang with gutter, two barred windows, glazed door with canopy, three steps and rails, AC unit, roof vent, lifting eyes, conduit. Front (door side) toward +y."""
    m = mb(F); L, D, H = 6.0, 2.6, 2.7; body = (0.5, 0.55, 0.58, 1)
    m.rbox(0, 0, 0.12, L, D, 0.24, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0, 1.45, L - 0.1, D - 0.1, 2.5, 0.05, mi=I['paint'], rgba=body)
    for k in range(int(L / 0.6)):                                                                                       # pressed ribs
        x = -L / 2 + 0.3 + k * 0.6
        m.rbox(x, D / 2 - 0.045, 1.45, 0.025, 0.012, 2.4, 0.003, mi=I['paint'], rgba=tuple(c * 0.85 for c in body[:3]) + (1,)); m.rbox(x, -D / 2 + 0.045, 1.45, 0.025, 0.012, 2.4, 0.003, mi=I['paint'], rgba=tuple(c * 0.85 for c in body[:3]) + (1,))
    m.rbox(0, 0, 0.5, L - 0.08, D - 0.08, 0.34, 0.03, mi=I['paint'], rgba=(0.9, 0.4, 0.05, 1))                      # orange base band
    m.rbox(0, 0, H + 0.04, L + 0.3, D + 0.3, 0.1, 0.02, mi=I['paint'], rgba=tuple(c * 0.8 for c in body[:3]) + (1,))   # roof
    m.between((-L / 2 - 0.15, D / 2 + 0.15, H - 0.02), (L / 2 + 0.15, D / 2 + 0.15, H - 0.02), 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)   # gutter
    for wx in (-1.8, 0.2):
        m.rbox(wx, D / 2 - 0.02, 1.6, 1.0, 0.06, 0.8, 0.01, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(wx, D / 2 + 0.005, 1.6, 0.9, 0.012, 0.7, 0.004, mi=I['glass'])
        for k in range(5): m.between((wx - 0.4 + k * 0.2, D / 2 + 0.05, 1.25), (wx - 0.4 + k * 0.2, D / 2 + 0.05, 1.95), 0.008, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(wx, D / 2 + 0.05, 1.18, 1.1, 0.1, 0.04, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    dx = 2.1
    m.rbox(dx, D / 2 - 0.02, 1.1, 1.0, 0.07, 2.1, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(dx, D / 2 + 0.02, 1.1, 0.88, 0.05, 2.0, 0.01, mi=I['paint'], rgba=(0.2, 0.3, 0.4, 1))
    m.rbox(dx, D / 2 + 0.05, 1.55, 0.5, 0.012, 0.6, 0.004, mi=I['glass'])
    m.rbox(dx + 0.34, D / 2 + 0.07, 1.05, 0.04, 0.05, 0.16, 0.01, mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(dx, D / 2 + 0.3, 2.3, 1.4, 0.6, 0.05, 0.01, mi=I['paint'], rgba=tuple(c * 0.8 for c in body[:3]) + (1,))   # door canopy
    for sx in (-0.65, 0.65): m.between((dx + sx, D / 2 + 0.02, 2.28), (dx + sx, D / 2 + 0.55, 2.28), 0.015, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(dx, D / 2 + 0.3, 2.22, 0.3, 0.12, 0.05, 0.01, mi=I['emissive'], rgba=(1.0, 0.92, 0.75, 1))
    for k in range(3): m.rbox(dx, D / 2 + 0.3 + (2 - k) * 0.28, 0.24 + k * 0.2 - 0.1 + 0.1, 1.1, 0.26, 0.04, 0.008, mi=I['steel_brushed'], rgba=STEEL)   # steps
    for sx in (-0.58, 0.58):
        m.between((dx + sx, D / 2 + 0.2, 0.3), (dx + sx, D / 2 + 0.2, 1.0), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.between((dx + sx, D / 2 + 0.2, 1.0), (dx + sx, D / 2 + 0.85, 0.5), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
        m.between((dx + sx, D / 2 + 0.85, 0.4), (dx + sx, D / 2 + 0.85, 0.5), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-2.4, -D / 2 - 0.15, 1.9, 0.9, 0.3, 0.55, 0.03, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1))                  # AC unit (rear)
    for k in range(6): m.rbox(-2.4, -D / 2 - 0.31, 1.7 + k * 0.07, 0.8, 0.012, 0.03, 0.004, mi=I['steel_charcoal'], rgba=DARK)
    m.cylz(1.6, 0.4, H + 0.09, H + 0.32, 0.18, seg=14, mi=I['steel_brushed'], rgba=STEEL); m.cylz(1.6, 0.4, H + 0.32, H + 0.36, 0.24, seg=14, mi=I['steel_brushed'], rgba=STEEL)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.15), sy * (D / 2 - 0.15), H + 0.14, 0.14, 0.14, 0.08, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.between((-0.3, D / 2 + 0.02, 2.4), (-0.3, D / 2 + 0.02, H), 0.014, seg=6, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_site_cabin', P)

def track_scale(F, P):
    """Flush rail weighbridge 4.2 x 2.4: steel deck set into the apron with a yellow frame and checker plate. The deck stays below the sleepers so the rail runs over it."""
    m = mb(F); L, W = 4.2, 2.4
    m.rbox(0, 0, -0.04, L, W, 0.1, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0, 0.0, L - 0.12, W - 0.12, 0.012, 0.003, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int((L - 0.3) / 0.12)): m.rbox(-L / 2 + 0.2 + k * 0.12, 0, 0.008, 0.012, W - 0.2, 0.006, 0.001, mi=I['steel_charcoal'], rgba=DARK)
    for sy in (-1, 1): m.rbox(0, sy * (W / 2 - 0.03), 0.004, L, 0.06, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    for sx in (-1, 1): m.rbox(sx * (L / 2 - 0.03), 0, 0.004, 0.06, W, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    return m.finish('proto_track_scale', P)

def scale_post(F, P):
    """Weighbridge display on a post: pole, sloped cabinet with a screen, amber beacon, hand rail."""
    m = mb(F)
    m.cylz(0, 0, 0.0, 1.5, 0.05, seg=10, mi=I['steel_charcoal'], rgba=DARK); m.cylz(0, 0, 0.0, 0.02, 0.14, seg=14, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0, 0.1, 1.5, 0.55, 0.22, 0.4, 0.03, rot=(-0.2, 0, 0), mi=I['paint'], rgba=(0.2, 0.22, 0.26, 1))
    m.rbox(0, 0.205, 1.52, 0.46, 0.012, 0.26, 0.004, rot=(-0.2, 0, 0), mi=I['screen'], rgba=(0.5, 0.9, 0.55, 1))
    m.add(p_cyl(0.07, 0.12, 14), (0, 0, 1.84), mi=I['emissive'], rgba=AMBER)
    return m.finish('proto_scale_post', P)

def skid_loader(F, P):
    """Compact skid-steer loader 3.0 m: orange body with louvred hinged engine door, exhaust, ROPS cab with glazed screens, seat, lap bar, joysticks and display, bent lift arms with pins and rams,
    tilt ram, bucket with side plates, ribs, bolt-on cutting edge and teeth, four lugged tyres, work lights, beacon, grab handles, hazard strip, fuel cap. Front toward +x."""
    m = lowpoly_boxes(mb(F)); PA = I['paint']; ST = I['steel_charcoal']; PL = I['plastic']; RB = I['rubber']; GL = I['glass']; EM = I['emissive']; BR = I['steel_brushed']
    org = (0.9, 0.42, 0.06, 1); orgd = tuple(c * 0.72 for c in org[:3]) + (1,); orgl = (0.95, 0.46, 0.08, 1); dk = (0.06, 0.06, 0.07, 1); gr = (0.2, 0.21, 0.23, 1); ch = (0.62, 0.64, 0.67, 1)
    # ---- chassis and body sides
    m.rbox(-0.1, 0, 0.5, 2.2, 1.1, 0.34, 0.04, mi=ST, rgba=dk)
    for sy in (-1, 1):
        side = [(-1.18, 0.3), (-1.18, 1.1), (-1.1, 1.3), (-0.6, 1.36), (-0.4, 1.0), (-0.34, 0.9), (0.6, 0.9), (0.62, 0.3)]
        panel(m, side, sy * 0.52, sy * 0.6, 0.012, PA, org)
        panel(m, [(-0.55, 0.3), (0.6, 0.3), (0.6, 0.46), (-0.55, 0.46)], sy * 0.585, sy * 0.615, 0.004, PA, orgd)
        m.rbox(0.1, sy * 0.615, 0.62, 0.5, 0.012, 0.012, 0, mi=ST, rgba=dk)
    m.rbox(-0.77, 0, 1.0, 0.8, 1.04, 0.5, 0.05, mi=PA, rgba=org)                                           # engine cover
    m.rbox(-0.78, 0, 1.27, 0.84, 1.06, 0.06, 0.03, mi=PA, rgba=orgl)
    m.rbox(-1.2, 0, 0.82, 0.06, 1.1, 0.66, 0.04, mi=PA, rgba=org)                                           # rear door
    for k in range(7): m.rbox(-1.235, 0, 0.62 + k * 0.045, 0.014, 0.8, 0.02, 0, mi=ST, rgba=dk)
    m.rbox(-1.225, 0, 1.1, 0.014, 0.8, 0.012, 0, mi=ST, rgba=dk)
    hazard_band(m, -1.225, -0.5, 0.5, 0.42, 0.56, side=-1, w=0.08, slant=0.08)
    for sy in (-1, 1):
        for z in (0.8, 1.15): m.cylz(-1.17, sy * 0.45, z - 0.04, z + 0.04, 0.014, seg=8, mi=ST, rgba=ch)       # door hinges
        m.rbox(-1.24, sy * 0.45, 1.0, 0.04, 0.14, 0.08, 0.012, mi=ST, rgba=dk); m.rbox(-1.25, sy * 0.45, 1.0, 0.012, 0.1, 0.05, 0.008, mi=EM, rgba=(0.9, 0.08, 0.05, 1))   # tail lamps
        for k in range(6): m.rbox(-0.65 + k * 0.06, sy * 0.536, 1.1, 0.025, 0.014, 0.3, 0, mi=ST, rgba=dk)           # side vents
    m.rbox(-1.22, 0, 0.5, 0.18, 0.9, 0.2, 0.05, mi=PA, rgba=orgd)                                           # counterweight lip
    m.rbox(-1.34, 0, 0.46, 0.12, 0.2, 0.12, 0.012, mi=ST, rgba=gr); m.cylz(-1.35, 0, 0.4, 0.5, 0.02, seg=8, mi=ST, rgba=ch)   # tow pin
    m.cylz(-0.95, 0.3, 1.3, 1.78, 0.045, seg=10, mi=ST, rgba=(0.25, 0.2, 0.17, 1)); m.cylz(-0.95, 0.3, 1.78, 1.82, 0.06, seg=10, mi=ST, rgba=dk)   # exhaust stack
    m.cylz(-0.55, -0.3, 1.31, 1.35, 0.06, seg=12, mi=PL, rgba=(0.1, 0.1, 0.11, 1)); m.cylz(-0.55, -0.3, 1.35, 1.38, 0.03, seg=8, mi=ST, rgba=ch)    # fuel cap
    m.rbox(-0.1, 0, 0.75, 0.75, 0.9, 0.1, 0.03, mi=ST, rgba=gr)                                             # cab floor / foot plate
    for k in range(8): m.rbox(-0.38 + k * 0.1, 0, 0.805, 0.02, 0.8, 0.008, 0, mi=ST, rgba=dk)
    # ---- wheels with guards
    for sy in (-1, 1):
        for x in (-0.85, 0.65):
            wheel(m, x, sy * 0.77, 0.34, r=0.34, w=0.3, flip=sy, rim=(0.7, 0.4, 0.08, 1))
            panel(m, arc_pts(x, 0.34, 0.405, 20, 160, 8) + arc_pts(x, 0.34, 0.375, 160, 20, 8), sy * 0.64, sy * 0.9, 0.0, PA, orgd)   # fender hoops
    # ---- ROPS cab
    for sy in (-1, 1):
        for x in (-0.38, 0.55):
            m.rbox(x, sy * 0.5, 1.4, 0.07, 0.07, 1.3, 0.012, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
            m.rbox(x, sy * 0.5, 0.78, 0.14, 0.14, 0.04, 0.01, mi=ST, rgba=gr)
        m.rbox(0.085, sy * 0.5, 2.03, 1.0, 0.07, 0.07, 0.015, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
        m.rbox(0.085, sy * 0.5, 1.55, 0.9, 0.05, 0.05, 0, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
        panel(m, [(-0.3, 1.57), (0.48, 1.57), (0.48, 2.0), (-0.3, 2.0)], sy * 0.5 - 0.006, sy * 0.5 + 0.006, 0.0, GL, None)   # side window
        tube(m, [(0.5, sy * 0.55, 0.95), (0.5, sy * 0.58, 0.95), (0.5, sy * 0.58, 1.4)], 0.014, seg=8, mi=PL, rgba=(0.95, 0.75, 0.06, 1))   # grab handle
    m.rbox(0.085, 0, 2.04, 1.0, 1.07, 0.04, 0.015, mi=ST, rgba=(0.08, 0.08, 0.09, 1))
    for k in range(9): m.rbox(0.085, -0.5 + k * 0.125, 2.065, 1.0, 0.04, 0.012, 0, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
    panel_yz(m, [(-0.46, 1.2), (0.46, 1.2), (0.46, 1.62), (-0.46, 1.62)], 0.555, 0.57, 0.0, GL, None)   # front screen
    for sy in (-1, 1): m.rbox(0.56, sy * 0.48, 1.4, 0.04, 0.05, 0.44, 0.01, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
    m.rbox(-0.38, 0, 1.45, 0.03, 0.96, 0.5, 0.01, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
    # operator station
    m.cushion(-0.16, 0, 1.0, 0.44, 0.44, 0.14, r=0.05, levels=1, mi=I['fabric'], rgba=(0.1, 0.1, 0.12, 1))
    m.cushion(-0.32, 0, 1.36, 0.1, 0.44, 0.62, r=0.04, levels=1, rot=(0, -0.12, 0), mi=I['fabric'], rgba=(0.1, 0.1, 0.12, 1))
    m.rbox(-0.2, 0, 0.88, 0.3, 0.3, 0.1, 0.02, mi=ST, rgba=dk)
    m.sphere(-0.16, 0.05, 1.12, 0.1, 0.1, 0.06, rings=6, seg=12, mi=PL, rgba=(0.95, 0.78, 0.08, 1))             # hard hat on seat
    for sy in (-1, 1):
        m.rbox(0.0, sy * 0.28, 1.17, 0.36, 0.05, 0.05, 0.015, mi=I['fabric'], rgba=(0.12, 0.12, 0.13, 1))    # arm rests
        m.cylz(0.14, sy * 0.28, 1.17, 1.36, 0.012, seg=6, mi=ST, rgba=ch); m.sphere(0.14, sy * 0.28, 1.38, 0.025, rings=5, seg=8, mi=PL, rgba=(0.08, 0.08, 0.09, 1))   # joysticks
    tube(m, [(-0.05, -0.3, 1.2), (0.3, -0.3, 1.35), (0.3, 0.3, 1.35), (-0.05, 0.3, 1.2)], 0.022, seg=8, mi=ST, rgba=(0.95, 0.75, 0.06, 1))   # lap bar
    m.rbox(0.42, 0, 1.2, 0.1, 0.5, 0.18, 0.03, mi=ST, rgba=dk); m.rbox(0.37, 0, 1.22, 0.012, 0.22, 0.1, 0, mi=I['screen'], rgba=(0.4, 0.8, 0.5, 1))
    m.rbox(0.4, -0.25, 1.1, 0.26, 0.2, 0.012, 0.004, mi=PL, rgba=(0.84, 0.84, 0.8, 1), rot=(0, 0, 0.2)) if False else None
    m.rbox(0.38, 0.0, 1.31, 0.014, 0.24, 0.3, 0.004, mi=PL, rgba=(0.5, 0.36, 0.2, 1), rot=(0, -0.2, 0)); m.rbox(0.372, 0.0, 1.31, 0.004, 0.2, 0.26, 0, mi=PL, rgba=(0.86, 0.86, 0.82, 1), rot=(0, -0.2, 0))   # clipboard
    for sy in (-1, 1):
        m.rbox(0.62, sy * 0.3, 2.07, 0.07, 0.12, 0.09, 0.02, mi=ST, rgba=dk); m.add(p_cyl(0.045, 0.03, 14), (0.67, sy * 0.3, 2.07), (0, math.pi / 2, 0), mi=EM, rgba=(1.0, 0.95, 0.8, 1))
    m.cylz(-0.35, -0.4, 2.07, 2.15, 0.02, seg=8, mi=ST, rgba=dk); m.add(p_cyl(0.07, 0.07, 14), (-0.35, -0.4, 2.2), mi=EM, rgba=AMBER); m.sphere(-0.35, -0.4, 2.235, 0.07, 0.07, 0.04, rings=5, seg=14, mi=EM, rgba=AMBER)
    m.cylz(-0.2, 0.42, 1.55, 1.9, 0.045, seg=10, mi=PL, rgba=(0.78, 0.08, 0.05, 1)) if False else None
    # ---- lift arms, rams, pins
    for sy in (-1, 1):
        y = sy * 0.66
        arm = [(-0.55, 1.35), (-0.4, 1.4), (0.2, 1.1), (0.9, 0.82), (1.22, 0.74), (1.3, 0.55), (1.12, 0.46), (0.9, 0.58), (0.2, 0.85), (-0.45, 1.08), (-0.58, 1.18)]
        panel(m, arm, y - 0.045, y + 0.045, 0.01, PA, org)
        panel(m, [(0.2, 1.1), (0.9, 0.82), (0.9, 0.58), (0.2, 0.85)], y - 0.052 * sy, y + 0.052 * sy, 0.0, PA, orgd) if False else None
        m.add(p_cyl(0.045, 0.14, 12), (-0.5, y, 1.28), (math.pi / 2, 0, 0), mi=ST, rgba=ch); m.add(p_cyl(0.04, 0.14, 12), (1.18, y, 0.56), (math.pi / 2, 0, 0), mi=ST, rgba=ch)
        m.between((0.0, sy * 0.58, 0.5), (0.45, sy * 0.58, 0.98), 0.04, seg=10, mi=ST, rgba=(0.2, 0.21, 0.22, 1)); m.between((0.45, sy * 0.58, 0.98), (0.58, sy * 0.6, 1.0), 0.022, seg=8, mi=BR, rgba=ch)   # lift ram
        m.sphere(0.0, sy * 0.58, 0.5, 0.045, rings=5, seg=8, mi=ST, rgba=gr)
    m.between((-0.1, -0.66, 1.0), (-0.1, 0.66, 1.0), 0.04, seg=8, mi=PA, rgba=orgd)                          # cross tube
    m.between((0.25, -0.35, 1.0), (1.05, -0.35, 0.78), 0.032, seg=10, mi=ST, rgba=(0.2, 0.21, 0.22, 1)); m.between((1.05, -0.35, 0.78), (1.22, -0.35, 0.7), 0.02, seg=8, mi=BR, rgba=ch)   # tilt ram
    # ---- bucket
    bk = [(1.86, 0.1), (1.28, 0.12), (1.18, 0.4), (1.24, 0.85), (1.36, 0.88), (1.34, 0.52), (1.45, 0.26), (1.86, 0.19)]
    panel(m, bk, -0.84, 0.84, 0.012, PA, (0.16, 0.16, 0.17, 1))
    for sy in (-1, 1):
        panel(m, [(1.95, 0.08), (1.28, 0.1), (1.14, 0.4), (1.2, 0.95), (1.4, 0.95), (1.36, 0.5), (1.5, 0.3), (1.95, 0.2)], sy * 0.84 - 0.03, sy * 0.84 + 0.03, 0.006, PA, (0.2, 0.2, 0.21, 1))
        m.rbox(1.17, sy * 0.4, 0.62, 0.05, 0.05, 0.5, 0.01, mi=PA, rgba=(0.18, 0.18, 0.19, 1)); m.rbox(1.17, sy * 0.4, 0.62, 0.05, 0.05, 0.5, 0.01, mi=PA, rgba=(0.18, 0.18, 0.19, 1)) if False else None
    for y in (-0.42, 0.0, 0.42): m.rbox(1.2, y, 0.62, 0.04, 0.05, 0.56, 0.01, mi=ST, rgba=(0.14, 0.14, 0.15, 1))   # back ribs
    m.rbox(1.86, 0, 0.12, 0.05, 1.7, 0.1, 0.01, mi=BR, rgba=(0.45, 0.45, 0.47, 1))                           # cutting edge
    for k in range(5):
        y = -0.68 + k * 0.34; panel(m, [(1.84, 0.045), (2.0, 0.045), (2.03, 0.1), (1.84, 0.2)], y - 0.06, y + 0.06, 0.004, BR, (0.5, 0.5, 0.52, 1))
        m.add(p_cyl(0.012, 0.01, 6), (1.88, y, 0.2), mi=ST, rgba=ch)
    for sy in (-1, 1): m.rbox(1.2, sy * 0.74, 0.62, 0.1, 0.08, 0.08, 0.02, mi=ST, rgba=gr)                  # carriage pivot lugs
    # ---- front lights and hoses
    for sy in (-1, 1):
        m.rbox(0.78, sy * 0.5, 1.02, 0.06, 0.1, 0.1, 0.02, mi=ST, rgba=dk); m.add(p_cyl(0.04, 0.02, 14), (0.82, sy * 0.5, 1.02), (0, math.pi / 2, 0), mi=EM, rgba=(1.0, 0.95, 0.8, 1))
    tube(m, bezier((0.5, 0.2, 0.9), (0.9, 0.2, 0.5), (1.15, 0.1, 0.65), 6), 0.012, seg=6, mi=RB, rgba=(0.03, 0.03, 0.035, 1), joints=False)
    tube(m, bezier((0.5, 0.26, 0.9), (0.95, 0.26, 0.45), (1.15, 0.16, 0.6), 6), 0.012, seg=6, mi=RB, rgba=(0.03, 0.03, 0.035, 1), joints=False)
    return m.finish('proto_skid_loader', P)

def fuel_station(F, P):
    """Bunded diesel station 4.6 x 3.0: concrete bund wall, two horizontal tanks on saddles with filler caps, vent pipes and gauges, and a pump with hose, nozzle holster and reel. Pump side toward +x."""
    m = mb(F); Lb, Wb = 4.6, 3.0
    for sy in (-1, 1): m.rbox(0, sy * (Wb / 2 - 0.1), 0.2, Lb, 0.2, 0.4, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    for sx in (-1, 1): m.rbox(sx * (Lb / 2 - 0.1), 0, 0.2, 0.2, Wb - 0.2, 0.4, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    m.rbox(0, 0, 0.02, Lb - 0.2, Wb - 0.2, 0.04, 0.01, mi=I['concrete_slab'], rgba=(0.5, 0.5, 0.48, 1))
    for k, y in enumerate((-0.75, 0.75)):
        for sx in (-0.9, 0.9): m.rbox(sx, y, 0.2, 0.2, 0.9, 0.4, 0.02, mi=I['steel_charcoal'], rgba=DARK)
        pb = p_lathe([(0.0, -1.3), (0.55, -1.3), (0.62, -1.15), (0.62, 1.15), (0.55, 1.3), (0.0, 1.3)], 28); xf(pb, (0, y, 0.95), (0, math.pi / 2, 0)); m.add(pb, mi=I['paint'], rgba=(0.82, 0.8, 0.74, 1) if k == 0 else (0.9, 0.55, 0.1, 1))
        m.cylz(-0.3, y, 1.54, 1.62, 0.16, seg=14, mi=I['steel_charcoal'], rgba=DARK); m.cylz(0.5, y, 1.54, 2.2, 0.03, seg=8, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(0.0, y - 0.05, 1.62, 0.2, 0.12, 0.2, 0.02, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1))
        m.add(p_torus(0.62, 0.015, 30, 6), (-1.15, y, 0.95), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=DARK) if False else None
    px = Lb / 2 + 0.6
    m.rbox(px, 0, 0.04, 1.0, 1.0, 0.08, 0.02, mi=I['concrete_slab'], rgba=(0.6, 0.6, 0.58, 1))
    m.rbox(px, 0, 0.8, 0.5, 0.36, 1.5, 0.04, mi=I['paint'], rgba=(0.82, 0.12, 0.08, 1))
    m.rbox(px + 0.26, 0, 1.2, 0.02, 0.28, 0.2, 0.01, mi=I['screen'], rgba=(0.5, 0.9, 0.55, 1)); m.rbox(px + 0.26, 0, 0.9, 0.03, 0.2, 0.26, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(px, 0, 1.58, 0.56, 0.4, 0.06, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    m.add(p_torus(0.2, 0.018, 24, 6), (px + 0.3, 0.18, 0.9), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.04, 0.04, 0.05, 1))
    m.between((px + 0.3, -0.12, 1.15), (px + 0.5, -0.12, 0.7), 0.025, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for sy in (-1, 1): m.cylz(px + 0.7, sy * 0.55, 0.0, 1.0, 0.09, seg=12, mi=I['steel_painted'] if 'steel_painted' in I else I['paint'], rgba=(0.95, 0.75, 0.05, 1))
    # ---- finish detail: tank straps, manways, gauges, manifold with valves, bund hazard band and step, nozzle, hose and pump lamp
    BR = (0.8, 0.8, 0.8, 1)
    for y in (-0.75, 0.75):
        for x in (-0.8, 0.8): m.add(p_torus(0.632, 0.013, 22, 4), (x, y, 0.95), (0, math.pi / 2, 0), mi=I['steel_charcoal'])
        m.add(p_cyl(0.22, 0.05, 14), (0.15, y, 1.57), mi=I['steel_charcoal'])
        for k in range(8): a = k * math.pi / 4; m.add(p_cyl(0.014, 0.02, 6), (0.15 + math.cos(a) * 0.18, y + math.sin(a) * 0.18, 1.6), mi=I['steel_brushed'], rgba=BR)
        m.add(p_cyl(0.045, 0.02, 12), (0.8, y, 1.585), mi=I['steel_charcoal']); m.add(p_cyl(0.034, 0.008, 12), (0.8, y, 1.6), mi=I['signage'], rgba=(0.9, 0.88, 0.8, 1))     # level dial
        m.add(p_cyl(0.045, 0.03, 10, 0.0), (0.5, y, 2.23), (0.3, 0, 0), mi=I['steel_charcoal'])                                                                       # vent cap
    for sy in (-1, 1): m.rbox(0, sy * (Wb / 2 - 0.1), 0.405, Lb, 0.12, 0.012, 0.0, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    for sx in (-1, 1): m.rbox(sx * (Lb / 2 - 0.1), 0, 0.405, 0.12, Wb - 0.2, 0.012, 0.0, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    for k in range(2): m.rbox(-Lb / 2 - 0.2 - k * 0.2, -0.3, 0.1 + k * 0.2, 0.2, 0.7, 0.04, 0.008, seg=1, mi=I['steel_brushed'], rgba=STEEL)                              # step over the bund
    m.rbox(-Lb / 2 - 0.12, -0.3, 0.2, 0.05, 0.7, 0.4, 0.008, seg=1, mi=I['steel_charcoal'])
    m.between((1.5, -0.75, 0.45), (1.5, 0.75, 0.45), 0.04, seg=8, mi=I['steel_brushed'], rgba=STEEL)                                                                      # manifold
    m.between((1.5, 0.0, 0.45), (px - 0.25, 0.0, 0.45), 0.04, seg=8, mi=I['steel_brushed'], rgba=STEEL)
    for y in (-0.75, 0.0, 0.75):
        m.rbox(1.5, y, 0.45, 0.1, 0.1, 0.1, 0.012, seg=1, mi=I['steel_charcoal']); m.between((1.5, y, 0.5), (1.5, y, 0.68), 0.01, seg=5, mi=I['steel_brushed'], rgba=BR)
        m.add(p_torus(0.05, 0.009, 10, 4), (1.5, y, 0.68), mi=I['paint'], rgba=(0.85, 0.1, 0.07, 1))
    m.rbox(px + 0.34, -0.12, 1.12, 0.07, 0.08, 0.3, 0.012, seg=1, mi=I['steel_charcoal']); m.between((px + 0.4, -0.12, 1.2), (px + 0.5, -0.12, 1.0), 0.016, seg=6, mi=I['paint'], rgba=(0.1, 0.1, 0.11, 1))   # holster, nozzle
    m.rbox(px + 0.27, 0.0, 0.56, 0.03, 0.16, 0.16, 0.006, seg=1, mi=I['paint'], rgba=(0.85, 0.7, 0.06, 1))
    m.add(p_cyl(0.035, 0.03, 10), (px + 0.28, 0.12, 0.7), (0, math.pi / 2, 0), mi=I['paint'], rgba=(0.85, 0.1, 0.07, 1))                                                  # e-stop
    m.add(p_cyl(0.07, 0.07, 12), (px, 0, 1.66), mi=I['emissive'], rgba=AMBER)
    m.rbox(px + 0.26, 0, 1.4, 0.015, 0.3, 0.05, 0.004, seg=1, mi=I['screen'], rgba=(0.55, 0.9, 0.5, 1))
    weather(m, 12, dirt=0.3, dirt_h=0.4, streak=0.2, blotch=0.15, angle=32.0)
    return m.finish('proto_fuel_station', P)

def bay_walls(F, P, w=3.2, d=3.4, h=1.8):
    """Push-wall ore bay: interlocking concrete blocks on three sides (open front toward +y), each wall with block joints and stud tops. Origin at the back centre."""
    m = mb(F); blk = (0.62, 0.6, 0.56, 1); t = 0.8
    def wall(cx, cy, sx, sy):
        m.rbox(cx, cy, h / 2, sx, sy, h, 0.02, mi=I['concrete_slab'], rgba=blk)
        n = int(max(sx, sy) / 1.6)
        for k in range(1, 3): m.rbox(cx, cy, k * h / 3, sx + 0.004, sy + 0.004, 0.012, 0.002, mi=I['steel_charcoal'], rgba=DARK)
        for k in range(n + 1):
            if sx > sy: m.rbox(cx - sx / 2 + k * sx / max(n, 1), cy, h / 2, 0.012, sy + 0.004, h, 0.002, mi=I['steel_charcoal'], rgba=DARK)
            else: m.rbox(cx, cy - sy / 2 + k * sy / max(n, 1), h / 2, sx + 0.004, 0.012, h, 0.002, mi=I['steel_charcoal'], rgba=DARK)
        for k in range(max(int(max(sx, sy) / 0.8), 2)):
            if sx > sy: m.cylz(cx - sx / 2 + 0.4 + k * 0.8, cy, h, h + 0.06, 0.13, seg=8, mi=I['concrete_slab'], rgba=blk)
            else: m.cylz(cx, cy - sy / 2 + 0.4 + k * 0.8, h, h + 0.06, 0.13, seg=8, mi=I['concrete_slab'], rgba=blk)
    wall(0, t / 2, w, t); wall(-w / 2 + t / 2, d / 2, t, d); wall(w / 2 - t / 2, d / 2, t, d)
    return m.finish('proto_bay_walls', P)

def rock_bolt(F, P):
    m = mb(F)
    m.rbox(0, 0.01, 0, 0.22, 0.02, 0.22, 0.004, mi=I['steel_charcoal'], rgba=(0.3, 0.3, 0.32, 1))
    m.add(p_cyl(0.045, 0.05, 6), (0, 0.04, 0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.35, 0.34, 0.33, 1))
    m.between((0, 0.0, 0), (0, -0.3, 0), 0.012, seg=5, mi=I['steel_charcoal'], rgba=(0.25, 0.2, 0.15, 1))
    return m.finish('proto_rock_bolt', P)

def safety_mesh(F, P, w=2.4, h=1.6):
    """Rock-face safety mesh panel: welded diamond mesh in a bolted steel border (front toward +y)."""
    m = mb(F); steel = (0.22, 0.22, 0.24, 1)
    for z in (0.0, h): m.between((-w / 2, 0.01, z), (w / 2, 0.01, z), 0.02, seg=6, mi=I['steel_charcoal'], rgba=steel)
    for x in (-w / 2, w / 2): m.between((x, 0.01, 0), (x, 0.01, h), 0.02, seg=6, mi=I['steel_charcoal'], rgba=steel)
    n = int(w / 0.2)
    for k in range(n + 1):
        x = -w / 2 + k * w / n; m.between((x, 0.0, 0.0), (min(x + h * 0.5, w / 2), 0.0, h), 0.005, seg=4, mi=I['steel_charcoal'], rgba=steel)
        m.between((x, 0.0, 0.0), (max(x - h * 0.5, -w / 2), 0.0, h), 0.005, seg=4, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_safety_mesh', P)

def led_pole(F, P, h=6.2):
    """Yard floodlight pole: tapered 12-sided steel pole on a base plate with gussets and anchor nuts, hand-hole cover and cable gland, reinforced swan-neck arm, and two LED floodlights
    (cast housing with heat-sink fins, visor, emissive lens, yoke with bolts, safety cable)."""
    m = mb(F); steel = (0.20, 0.21, 0.23, 1); ST = I['steel_charcoal']
    m.rbox(0, 0, 0.02, 0.42, 0.42, 0.04, 0.01, seg=1, mi=ST, rgba=DARK)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.add(p_cyl(0.022, 0.035, 6), (sx * 0.16, sy * 0.16, 0.058), mi=I['steel_brushed'], rgba=STEEL)                       # anchor nuts
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; m.rbox(math.cos(a) * 0.12, math.sin(a) * 0.12, 0.11, 0.1, 0.012, 0.14, 0.0, rot=(0, 0, a), mi=ST, rgba=DARK)   # gussets
    m.lathe([(0.0, 0.0), (0.15, 0.04), (0.13, 0.15), (0.095, 1.0), (0.08, 3.0), (0.052, h), (0.0, h)], seg=12, mi=ST, rgba=steel)
    m.rbox(0.0, 0.105, 0.95, 0.17, 0.02, 0.42, 0.008, seg=1, mi=ST, rgba=DARK)                                                           # hand-hole plate
    studs(m, [(sx * 0.065, 0.118, 0.95 + sz * 0.17) for sx in (-1, 1) for sz in (-1, 1)], '+y', r=0.014, h=0.012, mi=I['steel_brushed'], rgba=STEEL)
    m.add(p_cyl(0.025, 0.06, 8), (0.0, 0.1, 1.3), (-math.pi / 2, 0, 0), mi=ST, rgba=DARK)                                              # cable gland
    cable(m, [(0.0, 0.12, 1.33), (0.0, 0.27, 0.9), (0.0, 0.3, 0.06)], 0.014, 5, mi=I['rubber'])
    m.between((0, 0, h - 0.25), (0.45, 0, h + 0.06), 0.032, seg=8, mi=ST, rgba=steel)
    m.between((0.45, 0, h + 0.06), (0.8, 0, h + 0.1), 0.032, seg=8, mi=ST, rgba=steel)
    m.between((0.0, 0, h - 0.7), (0.4, 0, h + 0.02), 0.018, seg=6, mi=ST, rgba=steel)                                                      # brace
    for sy in (-0.25, 0.25):
        m.rbox(0.8, sy, h + 0.1, 0.5, 0.36, 0.08, 0.02, seg=1, mi=ST, rgba=DARK)                                                           # housing
        m.rbox(0.8, sy, h + 0.052, 0.43, 0.29, 0.014, 0.004, seg=1, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))                          # lens
        for dx in (-1, 1): m.rbox(0.8 + dx * 0.235, sy, h + 0.056, 0.03, 0.34, 0.022, 0.0, mi=ST, rgba=DARK)                       # bezel frame
        for dy in (-1, 1): m.rbox(0.8, sy + dy * 0.165, h + 0.056, 0.5, 0.03, 0.022, 0.0, mi=ST, rgba=DARK)
        for k in range(4): m.rbox(0.8 - 0.1 + k * 0.06 - 0.05, sy, h + 0.165, 0.014, 0.3, 0.05, 0.0, mi=ST, rgba=DARK)                   # heat-sink fins
        for dx in (-0.18, 0.18): m.rbox(0.8 + dx, sy + (-0.19 if sy < 0 else 0.19), h + 0.1, 0.05, 0.02, 0.08, 0.0, mi=ST)     # yoke ears
    m.rbox(0.8, 0, h + 0.07, 0.07, 0.55, 0.05, 0.0, mi=ST, rgba=DARK)                                                              # cross-arm
    weather(m, 7, dirt=0.15, dirt_h=0.4, streak=0.1, blotch=0.1, angle=30.0)
    return m.finish('proto_led_pole', P)

def wheel_stop(F, P):
    """Concrete wheel stop 1.6 m: chamfered, with two steel anchor spikes through washers, a reflective yellow strip and tyre-scuff marks."""
    m = mb(F)
    m.rbox(0, 0, 0.06, 1.6, 0.16, 0.12, 0.03, seg=2, mi=I['concrete_slab'])
    for sx in (-0.62, 0.62):
        m.add(p_cyl(0.03, 0.012, 10), (sx, 0.0, 0.126), mi=I['steel_charcoal']); m.add(p_cyl(0.014, 0.02, 6), (sx, 0.0, 0.14), mi=I['steel_brushed'], rgba=STEEL)
    m.rbox(0, 0.0, 0.126, 1.0, 0.1, 0.006, 0.0, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    for k in range(3): m.rbox(-0.2 + k * 0.2, 0.082, 0.07, 0.1, 0.004, 0.05, 0.0, rot=(0, 0.3, 0), mi=I['signage'], rgba=(0.05, 0.05, 0.05, 1))
    weather(m, 3, dirt=0.4, dirt_h=0.1)
    return m.finish('proto_wheel_stop', P)

def dock_platform(F, P, L=6.0, D=2.6, H=0.95):
    """Loading dock platform with kerb nosing, hazard edge, steps at one end, toe rail and tie-down eyes. Long edge toward +y."""
    m = mb(F)
    m.rbox(0, 0, H / 2, L, D, H, 0.02, mi=I['concrete_slab'], rgba=(0.62, 0.6, 0.56, 1))
    m.rbox(0, D / 2 - 0.12, H + 0.004, L, 0.24, 0.012, 0.002, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    m.rbox(0, D / 2 + 0.03, H - 0.1, L, 0.08, 0.2, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    for k in range(3): m.rbox(-L / 2 - 0.3 - k * 0.0, -0.2 - k * 0.0, 0.25 + k * 0.2 - 0.12, 0.6, 1.0, 0.04, 0.01, mi=I['steel_brushed'], rgba=STEEL) if False else None
    for k in range(4): m.rbox(-L / 2 - 0.15 - (3 - k) * 0.3, -0.3, 0.2 + k * 0.22, 0.3, 1.1, 0.05, 0.008, mi=I['steel_brushed'], rgba=STEEL)
    for sy in (-0.85, 0.25):
        m.between((-L / 2 - 1.2, sy, 0.95), (-L / 2 - 0.1, sy, 1.0 + 0.0), 0.02, seg=6, mi=I['steel_charcoal'], rgba=DARK) if False else None
    for sx in (-0.4 * L, 0.4 * L): m.torus(sx, -D / 2 + 0.2, H + 0.02, 0.07, 0.014, ns=14, nt=6, mi=I['steel_charcoal'], rgba=DARK)
    for x in (-0.38 * L, 0.0, 0.38 * L): m.rbox(x, D / 2 + 0.1, H - 0.28, 0.4, 0.1, 0.34, 0.015, seg=1, mi=I['rubber'])                                  # dock bumpers
    for x in (-0.2 * L, 0.2 * L): m.rbox(x, 0, H + 0.003, 0.012, D - 0.3, 0.006, 0.0, mi=I['steel_charcoal'], rgba=(0.03, 0.03, 0.03, 1))      # expansion joints
    for sx in (-1, 1): m.rbox(-L / 2 - 0.45, sx * 0.62 - 0.3, 0.4, 0.04, 0.04, 0.8, 0.006, seg=1, mi=I['steel_charcoal'])                         # step stringer posts
    m.rbox(-L / 2 - 0.45, -0.3, 0.05, 0.9, 0.12, 0.1, 0.01, seg=1, mi=I['steel_charcoal'])
    m.rbox(0.0, D / 2 - 0.35, H + 0.01, 1.6, 0.55, 0.02, 0.006, seg=1, mi=I['steel_brushed'], rgba=STEEL)                                           # dock leveller plate
    stud_row(m, (-0.7, D / 2 - 0.1, H + 0.022), (0.7, D / 2 - 0.1, H + 0.022), 6, '+z', r=0.012, h=0.01, mi=I['steel_charcoal'])
    stud_row(m, (-0.4 * L, D / 2 + 0.075, H - 0.06), (0.4 * L, D / 2 + 0.075, H - 0.06), 14, '+y', r=0.012, h=0.01, mi=I['steel_brushed'], rgba=STEEL)
    weather(m, 2, dirt=0.35, dirt_h=0.3, streak=0.15, blotch=0.12)
    return m.finish('proto_dock_platform', P)

def beacon_post(F, P, h=3.0):
    """Gate warning light: post with two amber heads and a lamp hood."""
    m = mb(F)
    m.cylz(0, 0, 0.0, h, 0.06, seg=10, mi=I['paint'], rgba=(0.95, 0.75, 0.05, 1)); m.cylz(0, 0, 0.0, 0.03, 0.16, seg=12, mi=I['steel_charcoal'], rgba=DARK)
    for sx in (-1, 1): m.add(p_cyl(0.09, 0.1, 14), (sx * 0.13, 0.0, h + 0.08), mi=I['emissive'], rgba=AMBER)
    m.rbox(0, 0, h - 0.4, 0.3, 0.12, 0.2, 0.02, mi=I['steel_charcoal'], rgba=DARK)
    return m.finish('proto_beacon_post', P)

def vent_fan(F, P):
    """Mine ventilation fan unit 2.4 m: cylindrical shroud with inlet bell, grille, motor, flanged outlet, steel cradle and electrical box. Axis along x, intake toward -x (cliff)."""
    m = mb(F); grey = (0.55, 0.58, 0.6, 1)
    pb = p_lathe([(0.0, -1.2), (0.95, -1.2), (1.0, -1.1), (1.0, 1.0), (0.9, 1.2), (0.0, 1.2)], 36); xf(pb, (0, 0, 1.15), (0, math.pi / 2, 0)); m.add(pb, mi=I['paint'], rgba=grey)
    pb2 = p_lathe([(0.0, -2.6), (0.88, -2.6), (0.88, -1.2), (0.0, -1.2)], 28); xf(pb2, (0, 0, 1.15), (0, math.pi / 2, 0)); m.add(pb2, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))      # duct stub into the cliff
    m.add(p_torus(0.98, 0.04, 36, 8), (-1.2, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=STEEL)
    m.add(p_torus(0.9, 0.05, 36, 8), (1.2, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=STEEL)
    for k in range(7): m.between((-1.25, 0, 1.15 - 0.9 + k * 0.3), (-1.25, 0, 1.15 - 0.9 + k * 0.3), 0.001, seg=3, mi=I['steel_charcoal'], rgba=DARK) if False else None
    for k in range(6):
        a = k * math.pi / 3; m.between((-1.26, 0, 1.15), (-1.26, math.cos(a) * 0.95, 1.15 + math.sin(a) * 0.95), 0.012, seg=5, mi=I['steel_charcoal'], rgba=DARK)
    for r in (0.3, 0.6): m.add(p_torus(r, 0.01, 28, 5), (-1.26, 0, 1.15), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.2, 0, 2.28, 0.8, 0.5, 0.3, 0.04, mi=I['paint'], rgba=(0.2, 0.3, 0.45, 1))                                  # motor housing on top
    for sx in (-0.8, 0.8):
        for sy in (-0.5, 0.5): m.rbox(sx, sy, 0.1, 0.1, 0.1, 0.2, 0.01, mi=I['steel_charcoal'], rgba=DARK)
        m.rbox(sx, 0, 0.18, 0.1, 1.2, 0.08, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(0.0, 0, 0.1, 2.4, 0.1, 0.08, 0.01, mi=I['steel_charcoal'], rgba=DARK)
    m.rbox(-0.1, -1.05, 1.3, 0.5, 0.18, 0.7, 0.02, mi=I['paint'], rgba=(0.7, 0.72, 0.74, 1))
    m.rbox(-0.1, -1.15, 1.45, 0.3, 0.012, 0.18, 0.004, mi=I['screen'], rgba=(0.4, 0.8, 0.5, 1))
    return m.finish('proto_vent_fan', P)
