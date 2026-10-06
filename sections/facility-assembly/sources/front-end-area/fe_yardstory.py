"""Lived-in storytelling props around the lamp room cabin: the shift's small human traces (workbench with vice, tools, hard hat and thermos; hi-vis jackets and a helmet on hooks;
a notice board; a lit lantern; tool boxes; a coiled hose; a fire extinguisher post; a first-aid cabinet; a radio on a shelf; ore spilled beside the cars).
Plan frame: cabin centre (-42.8, -74.4), 6.0 x 2.6, door at x = -40.7 facing +y toward the mine lane. Wall items stand on the cabin's front face (y = -73.15) or its east end (x = -39.85).
Clear lanes are never entered: mine lane y -71.3..-68.7, refinery rail x -23.5..-20.9 (y > -70.5), evacuation path x -29.7..-26.3 (y < -71.2), north-west door path x -47.4..-44.8 (y > -68.8).
Lettering is baked through fe_signs.sign(); no modelled text."""
import math, random
from fe_common import *
from fe_kit import *
from fe_propkit import *
from fe_assets_int import STD, I, mb
from fe_yard import inst
from fe_signs import sign
from fe_assets_site import toolbox

WALL_Y = -73.15            # cabin front wall face (plan y)
END_X = -39.85             # cabin east end wall face (plan x)
ST = I['steel_charcoal']; BR = (0.8, 0.8, 0.8, 1); DK = (0.07, 0.07, 0.08, 1)
LANES = [(-49.0, -8.0, -71.3, -68.7), (-23.5, -20.9, -70.5, -59.5), (-29.7, -26.3, -84.5, -71.2), (-47.4, -44.8, -68.8, -59.5)]

# ---------------------------------------------------------------------------------------------------------------- prototypes
def hardhat(m, x=0.0, y=0.0, z=0.0, yaw=0.0, rgba=(0.92, 0.72, 0.06, 1), lamp=True):
    """Hard hat with ridged shell, brim, peak and a cap-lamp bracket; origin at the rim centre."""
    prof = [(0.118, 0.0), (0.12, 0.02), (0.112, 0.055), (0.092, 0.092), (0.055, 0.112), (0.0, 0.118)]
    m.lathe(prof, (x, y, z), seg=14, mi=I['plastic'], rgba=rgba, rot=(0, 0, yaw))
    m.lathe([(0.118, 0.004), (0.138, 0.0), (0.14, -0.006), (0.116, -0.004)], (x, y, z), seg=14, mi=I['plastic'], rgba=tuple(c * 0.9 for c in rgba[:3]) + (1,), rot=(0, 0, yaw))
    c, s = math.cos(yaw), math.sin(yaw)
    m.rbox(x + c * 0.15, y + s * 0.15, z + 0.0, 0.07, 0.17, 0.014, 0.004, rot=(0, 0, yaw), seg=1, mi=I['plastic'], rgba=tuple(k * 0.9 for k in rgba[:3]) + (1,))   # peak
    for t in (-0.035, 0.035): m.rbox(x - s * t, y + c * t, z + 0.097, 0.02, 0.2, 0.012, 0.0, rot=(0, 0, yaw), mi=I['plastic'], rgba=rgba) if False else m.rbox(x + s * -t, y + c * t, z + 0.1, 0.19, 0.016, 0.014, 0.0, rot=(0, 0, yaw + math.pi / 2), mi=I['plastic'], rgba=rgba)
    if lamp:
        m.rbox(x + c * 0.1, y + s * 0.1, z + 0.075, 0.04, 0.05, 0.04, 0.006, rot=(0, 0, yaw), seg=1, mi=ST, rgba=DK)
        m.add(p_cyl(0.017, 0.016, 8), (x + c * 0.125, y + s * 0.125, z + 0.075), (0, math.pi / 2, yaw), mi=I['emissive'], rgba=(1.0, 0.9, 0.65, 1))

def proto_hardhat(F, P, rgba=(0.92, 0.72, 0.06, 1), name='hardhat'):
    m = mb(F); hardhat(m, 0, 0, 0, 0.0, rgba); weather(m, 4, dirt=0.2, dirt_h=0.1, streak=0.0, blotch=0.2, angle=30.0)
    return m.finish('proto_' + name, P)

def proto_workbench(F, P):
    """Trestle workbench 1.95 x 0.62 (back toward -y, user side +y): plank top, A-frame trestles with stretchers, lower shelf, bolted vice with T-handle, tools, a hard hat, a thermos, a grease tin and a rag."""
    m = mb(F); rnd = random.Random(5); W = I['timber']; TOP = 0.92
    for x in (-0.78, 0.78):
        for sy in (-1, 1):
            m.rbox(x, sy * 0.25, 0.44, 0.07, 0.07, 0.9, 0.006, rot=(-sy * 0.1, 0, 0), seg=1, mi=W)                               # splayed legs
        m.rbox(x, 0, 0.87, 0.1, 0.6, 0.07, 0.006, seg=1, mi=W)                                                                    # trestle head
        m.rbox(x, 0, 0.24, 0.06, 0.62, 0.04, 0.0, mi=W)                                                                           # foot stretcher
        studs(m, [(x + 0.055, sy * 0.25, 0.86) for sy in (-1, 1)], '+x', r=0.014, h=0.01, mi=ST)
    for i in range(3): m.rbox(0, -0.205 + i * 0.205, TOP - 0.025, 1.95, 0.195, 0.045, 0.0, mi=W)                                   # top planks
    m.rbox(0, -0.26, 0.76, 1.6, 0.04, 0.14, 0.0, mi=W)                                                                            # back rail
    for i in range(3): m.rbox(0, -0.18 + i * 0.18, 0.3, 1.62, 0.17, 0.03, 0.0, mi=W)                                              # lower shelf
    # vice
    vx = -0.74; VI = (0.12, 0.17, 0.27, 1)
    m.rbox(vx, 0.24, TOP + 0.03, 0.2, 0.17, 0.06, 0.01, seg=1, mi=I['paint'], rgba=VI)
    m.rbox(vx, 0.19, TOP + 0.1, 0.18, 0.05, 0.09, 0.008, seg=1, mi=I['paint'], rgba=VI)                                            # fixed jaw
    m.rbox(vx, 0.285, TOP + 0.1, 0.18, 0.05, 0.09, 0.008, seg=1, mi=I['paint'], rgba=VI)                                           # moving jaw
    m.between((vx, 0.3, TOP + 0.07), (vx, 0.5, TOP + 0.07), 0.013, seg=6, mi=I['steel_brushed'], rgba=BR)                         # screw
    m.between((vx - 0.1, 0.5, TOP + 0.07), (vx + 0.1, 0.5, TOP + 0.07), 0.011, seg=5, mi=I['steel_brushed'], rgba=BR)            # T-handle
    for sx in (-1, 1): m.add(p_cyl(0.014, 0.02, 6), (vx + sx * 0.07, 0.24, TOP + 0.075), mi=I['steel_brushed'], rgba=BR)
    m.rbox(vx + 0.03, 0.2, TOP + 0.0, 0.1, 0.1, 0.0, 0.0, mi=ST) if False else None
    # tools
    m.rbox(-0.2, 0.12, TOP + 0.012, 0.3, 0.026, 0.012, 0.0, rot=(0, 0, 0.2), mi=I['steel_brushed'], rgba=BR)                         # spanner
    m.add(p_torus(0.03, 0.009, 8, 4), (-0.355, 0.157, TOP + 0.012), mi=I['steel_brushed'], rgba=BR); m.add(p_torus(0.026, 0.008, 8, 4), (-0.045, 0.083, TOP + 0.012), mi=I['steel_brushed'], rgba=BR)
    m.between((0.05, 0.1, TOP + 0.02), (0.3, 0.2, TOP + 0.02), 0.014, seg=6, mi=W)                                                 # hammer handle
    m.rbox(0.05, 0.1, TOP + 0.03, 0.05, 0.1, 0.05, 0.006, rot=(0, 0, 0.38), seg=1, mi=ST, rgba=DK)                                  # hammer head
    m.between((0.18, 0.05, TOP + 0.016), (0.35, 0.02, TOP + 0.016), 0.012, seg=6, mi=I['plastic'], rgba=(0.85, 0.5, 0.05, 1))      # screwdriver
    m.between((0.35, 0.02, TOP + 0.016), (0.5, 0.0, TOP + 0.014), 0.004, seg=4, mi=I['steel_brushed'], rgba=BR)
    m.rbox(0.62, 0.19, TOP + 0.01, 0.22, 0.12, 0.012, 0.004, rot=(0, 0, 0.1), seg=1, mi=ST, rgba=(0.12, 0.12, 0.13, 1))             # parts tray with bolts
    for k in range(6): m.add(p_cyl(0.011, 0.02, 6), (0.55 + rnd.uniform(0, 0.15), 0.15 + rnd.uniform(0, 0.08), TOP + 0.026), (0, math.pi / 2 * rnd.choice((0, 1)), rnd.uniform(0, 3)), mi=I['steel_brushed'], rgba=BR)
    # thermos and mug
    tx, ty = 0.82, 0.02
    m.lathe([(0.0, 0.0), (0.05, 0.0), (0.056, 0.01), (0.056, 0.26), (0.05, 0.285), (0.0, 0.285)], (tx, ty, TOP), seg=12, mi=I['paint'], rgba=(0.1, 0.3, 0.22, 1))
    m.cylz(tx, ty, TOP + 0.285, TOP + 0.34, 0.045, seg=12, bevel=0.006, mi=I['steel_brushed'], rgba=(0.75, 0.76, 0.78, 1))
    m.add(p_torus(0.033, 0.007, 10, 4), (tx + 0.06, ty, TOP + 0.2), (math.pi / 2, 0, 0), mi=I['paint'], rgba=(0.06, 0.06, 0.07, 1))
    m.lathe([(0.0, 0.0), (0.04, 0.0), (0.045, 0.09), (0.0, 0.09)], (0.5, -0.12, TOP), seg=10, mi=I['plastic'], rgba=(0.82, 0.8, 0.72, 1))   # enamel mug
    m.add(p_torus(0.028, 0.006, 8, 4), (0.55, -0.12, TOP + 0.05), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.82, 0.8, 0.72, 1))
    hardhat(m, 0.2, -0.12, TOP + 0.0, 0.7, (0.92, 0.72, 0.06, 1))
    m.add(p_bag(0.2, 0.12, 0.05, rnd), (-0.42, -0.15, TOP + 0.02), (0, 0, 0.5), mi=I['fabric'], rgba=(0.5, 0.18, 0.1, 1))           # rag
    m.add(p_cyl(0.05, 0.06, 12), (0.0, 0.2, TOP + 0.03), mi=I['paint'], rgba=(0.6, 0.55, 0.45, 1)); m.add(p_cyl(0.052, 0.012, 12), (0.0, 0.2, TOP + 0.06), mi=I['paint'], rgba=(0.5, 0.45, 0.35, 1))   # grease tin
    # lower shelf clutter: box and oil can
    m.rbox(0.4, 0.0, 0.42, 0.34, 0.26, 0.2, 0.012, seg=1, mi=I['timber'])
    m.rbox(0.4, 0.132, 0.42, 0.2, 0.004, 0.1, 0.0, mi=I['signage'], rgba=(0.85, 0.82, 0.72, 1))
    m.lathe([(0.0, 0.0), (0.05, 0.0), (0.055, 0.02), (0.055, 0.14), (0.04, 0.17), (0.02, 0.18), (0.0, 0.18)], (-0.3, 0.05, 0.315), seg=10, mi=I['paint'], rgba=(0.7, 0.55, 0.08, 1))
    weather(m, 5, dirt=0.4, dirt_h=0.3, streak=0.1, blotch=0.15, angle=30.0)
    return m.finish('proto_story_workbench', P)

def proto_hook_rail(F, P):
    """Wall plank with three iron coat hooks; front toward +y, origin at the wall face, hooks at z 0 (local), plank centred at z = +0.06."""
    m = mb(F)
    m.rbox(0, 0.012, 0.07, 0.72, 0.024, 0.1, 0.004, seg=1, mi=I['timber'])
    for x in (-0.24, 0.0, 0.24):
        m.between((x, 0.024, 0.07), (x, 0.09, 0.07), 0.009, seg=5, mi=ST); m.between((x, 0.09, 0.07), (x, 0.11, 0.1), 0.009, seg=5, mi=ST)
        m.add(p_cyl(0.02, 0.006, 8), (x, 0.027, 0.07), (math.pi / 2, 0, 0), mi=ST)
    studs(m, [(-0.33, 0.024, 0.07), (0.33, 0.024, 0.07)], '+y', r=0.012, h=0.008, mi=I['steel_brushed'], rgba=BR)
    weather(m, 2, dirt=0.0, streak=0.0, blotch=0.15)
    return m.finish('proto_story_hook_rail', P)

def proto_jacket(F, P, rgba=(0.98, 0.42, 0.02, 1), name='jacket'):
    """Hi-vis jacket hanging from a hook (origin at the hook, hanging toward -z): padded torso, sleeves, collar, pockets, two silver reflective bands."""
    m = mb(F); rnd = random.Random(int(rgba[0] * 100)); SIL = (0.82, 0.82, 0.78, 1); dk = tuple(k * 0.78 for k in rgba[:3]) + (1,)
    m.rbox(0, 0.0, -0.33, 0.44, 0.1, 0.58, 0.04, seg=2, rot=(0.05, 0, 0), mi=I['fabric'], rgba=rgba)
    m.rbox(0, -0.01, -0.07, 0.34, 0.1, 0.1, 0.035, seg=2, mi=I['fabric'], rgba=dk)                                                  # shoulders/collar
    for sx in (-1, 1):
        m.between((sx * 0.22, 0.0, -0.1), (sx * 0.265, 0.035, -0.58), 0.052, seg=7, r2=0.045, mi=I['fabric'], rgba=rgba)             # sleeve
        m.add(p_torus(0.047, 0.012, 8, 4), (sx * 0.265, 0.035, -0.58), (0, 0, 0), mi=I['fabric'], rgba=dk)                             # cuff
        m.add(p_torus(0.054, 0.012, 8, 4), (sx * 0.247, 0.02, -0.38), (0.05, 0, 0), mi=I['signage'], rgba=SIL)                         # sleeve band
        m.rbox(sx * 0.12, 0.055, -0.46, 0.14, 0.012, 0.1, 0.004, rot=(0.05, 0, 0), seg=1, mi=I['fabric'], rgba=dk)                     # pocket flap
        m.rbox(sx * 0.1, 0.057, -0.3, 0.05, 0.012, 0.44, 0.0, rot=(0.05, 0, sx * 0.1), mi=I['signage'], rgba=SIL)                      # vertical band
    for z in (-0.3, -0.44): m.rbox(0, 0.054, z, 0.45, 0.012, 0.04, 0.0, rot=(0.05, 0, 0), mi=I['signage'], rgba=SIL)
    m.rbox(0, 0.057, -0.33, 0.012, 0.012, 0.55, 0.0, rot=(0.05, 0, 0), mi=ST, rgba=DK)                                              # zip
    m.between((0, 0.0, -0.03), (0, 0.0, 0.0), 0.012, seg=5, mi=I['rubber'])
    weather(m, int(rgba[0] * 50), dirt=0.35, dirt_h=0.25, streak=0.25, blotch=0.22, angle=30.0)
    return m.finish('proto_story_' + name, P)

def proto_lantern(F, P):
    """Hurricane lantern: pressed base, glass globe with a warm flame, wire guard, vented cap and bail handle. The flame is emissive; build_yard_story adds a small real light."""
    m = mb(F); BRZ = (0.2, 0.17, 0.12, 1)
    m.lathe([(0.0, 0.0), (0.075, 0.0), (0.082, 0.012), (0.07, 0.04), (0.05, 0.05), (0.0, 0.05)], seg=14, mi=I['paint'], rgba=(0.5, 0.12, 0.07, 1))
    m.lathe([(0.04, 0.05), (0.046, 0.08), (0.05, 0.12), (0.04, 0.17), (0.034, 0.2), (0.04, 0.2), (0.046, 0.17), (0.056, 0.12), (0.052, 0.08), (0.046, 0.05)], seg=12, mi=I['glass'])
    m.lathe([(0.0, 0.055), (0.014, 0.06), (0.022, 0.09), (0.014, 0.125), (0.0, 0.14)], seg=8, mi=I['emissive'], rgba=(1.0, 0.62, 0.2, 1))
    for a in (0.0, math.pi / 2, math.pi, 1.5 * math.pi): m.between((math.cos(a) * 0.062, math.sin(a) * 0.062, 0.05), (math.cos(a) * 0.042, math.sin(a) * 0.042, 0.2), 0.0045, seg=4, mi=ST)
    m.lathe([(0.052, 0.19), (0.058, 0.21), (0.03, 0.235), (0.02, 0.255), (0.0, 0.26)], seg=12, mi=I['paint'], rgba=(0.5, 0.12, 0.07, 1))
    m.add(p_torus(0.054, 0.006, 12, 4), (0, 0, 0.2), mi=ST)
    pts = [(0.075 * math.cos(math.pi * j / 6), 0.0, 0.2 + 0.07 * math.sin(math.pi * j / 6)) for j in range(7)]
    for a, b in zip(pts[:-1], pts[1:]): m.between(a, b, 0.004, seg=4, mi=ST)
    weather(m, 3, dirt=0.3, dirt_h=0.05)
    return m.finish('proto_story_lantern', P)

def proto_extinguisher_post(F, P):
    """Fire point: steel post on a base plate with a wall bracket and strap, dry-powder extinguisher (gauge, pin and tamper seal, hose and horn, label), and a floor stencil plate. Front toward +y."""
    m = mb(F); RD = (0.7, 0.05, 0.04, 1)
    m.rbox(0, 0, 0.012, 0.3, 0.3, 0.024, 0.006, seg=1, mi=ST, rgba=DK)
    m.cylz(0, 0, 0.0, 1.9, 0.034, seg=8, mi=I['paint'], rgba=(0.85, 0.12, 0.08, 1))
    for sx in (-1, 1):
        for sy in (-1, 1): m.add(p_cyl(0.014, 0.02, 6), (sx * 0.11, sy * 0.11, 0.034), mi=I['steel_brushed'], rgba=BR)
    m.rbox(0, 0.045, 1.0, 0.16, 0.012, 0.5, 0.004, seg=1, mi=ST, rgba=DK)                                                          # mounting plate
    ex, ey = 0.0, 0.1
    m.lathe([(0.0, 0.0), (0.05, 0.0), (0.07, 0.02), (0.075, 0.06), (0.075, 0.3), (0.07, 0.34), (0.052, 0.385), (0.03, 0.4), (0.0, 0.4)], (ex, ey, 0.78), seg=14, mi=I['paint'], rgba=RD)
    m.cylz(ex, ey, 1.17, 1.22, 0.03, seg=8, mi=ST, rgba=DK)                                                                          # valve neck
    m.rbox(ex, ey + 0.02, 1.245, 0.14, 0.05, 0.04, 0.008, seg=1, mi=ST, rgba=DK); m.rbox(ex + 0.03, ey + 0.02, 1.285, 0.14, 0.03, 0.014, 0.004, rot=(0, 0.12, 0), seg=1, mi=ST, rgba=DK)   # head and lever
    m.add(p_cyl(0.025, 0.014, 10), (ex - 0.05, ey + 0.05, 1.225), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR); m.add(p_cyl(0.019, 0.005, 10), (ex - 0.05, ey + 0.058, 1.225), (math.pi / 2, 0, 0), mi=I['signage'], rgba=(0.9, 0.9, 0.8, 1))
    m.add(p_torus(0.016, 0.003, 8, 3), (ex + 0.06, ey, 1.25), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR)
    cable(m, bez((ex + 0.04, ey - 0.02, 1.23), (ex + 0.17, ey - 0.02, 1.1), (ex + 0.09, ey - 0.04, 0.9), 5), 0.011, 5, mi=I['rubber'])
    m.rbox(ex + 0.09, ey - 0.04, 0.88, 0.035, 0.035, 0.06, 0.006, seg=1, mi=I['rubber'])
    for z in (0.92, 1.1): m.rbox(0, ey - 0.005, z, 0.17, 0.17, 0.018, 0.004, seg=1, mi=ST, rgba=(0.1, 0.1, 0.11, 1)) if False else m.add(p_torus(0.075, 0.009, 14, 4), (ex, ey, z + 0.0), mi=I['steel_charcoal'])
    m.add(p_arc_band(0.0755, 0.9, 1.1, math.pi * 0.2, math.pi * 0.9, 8, 0.004), (ex, ey, 0.0), mi=I['signage'], rgba=(0.88, 0.86, 0.78, 1))
    m.add(p_arc_band(0.0755, 1.03, 1.05, math.pi * 0.25, math.pi * 0.85, 6, 0.007), (ex, ey, 0.0), mi=I['signage'], rgba=(0.06, 0.06, 0.06, 1))
    m.rbox(0, 0.0, 1.78, 0.04, 0.0, 0.04, 0.0, mi=ST) if False else None
    weather(m, 6, dirt=0.35, dirt_h=0.2, streak=0.15, blotch=0.15, angle=30.0)
    return m.finish('proto_story_extinguisher_post', P)

def proto_first_aid(F, P):
    """Wall first-aid cabinet 0.36 x 0.14 x 0.46 (front toward +y): green pressed box, raised door with piano hinge, latch, rain lip; the white cross plate is a baked sign."""
    m = mb(F); G = (0.08, 0.42, 0.26, 1)
    m.rbox(0, 0.07, 0.23, 0.36, 0.14, 0.46, 0.012, seg=1, mi=I['paint'], rgba=G)
    m.rbox(0, 0.152, 0.23, 0.32, 0.016, 0.42, 0.006, seg=1, mi=I['paint'], rgba=tuple(k * 1.08 for k in G[:3]) + (1,))               # door
    m.rbox(0, 0.1, 0.475, 0.4, 0.2, 0.02, 0.006, seg=1, mi=I['paint'], rgba=tuple(k * 0.85 for k in G[:3]) + (1,))                    # rain lip
    m.between((-0.158, 0.16, 0.03), (-0.158, 0.16, 0.43), 0.008, seg=5, mi=I['steel_brushed'], rgba=BR)
    m.rbox(0.13, 0.168, 0.23, 0.03, 0.02, 0.07, 0.006, seg=1, mi=I['steel_brushed'], rgba=BR)
    studs(m, [(sx * 0.15, 0.16, z) for sx in (-1, 1) for z in (0.06, 0.4)], '+y', r=0.01, h=0.008, mi=ST)
    weather(m, 8, dirt=0.2, dirt_h=0.2, streak=0.15, blotch=0.15, angle=30.0)
    return m.finish('proto_story_first_aid', P)

def proto_radio_shelf(F, P):
    """Wall shelf with a scuffed two-way radio: bracketed plank, rubberised radio with telescopic antenna, grille slots, knobs, display and handle, and a tin mug."""
    m = mb(F)
    m.rbox(0, 0.1, 0.0, 0.62, 0.2, 0.03, 0.004, seg=1, mi=I['timber'])
    for x in (-0.24, 0.24):
        m.rbox(x, 0.015, -0.1, 0.03, 0.02, 0.2, 0.0, mi=ST); m.rbox(x, 0.09, -0.012, 0.03, 0.18, 0.014, 0.0, mi=ST); m.between((x, 0.02, -0.19), (x, 0.17, -0.02), 0.01, seg=4, mi=ST)
    ra = (0.78, 0.42, 0.05, 1)
    m.rbox(-0.1, 0.1, 0.105, 0.19, 0.075, 0.16, 0.02, seg=1, mi=I['plastic'], rgba=ra)
    m.rbox(-0.1, 0.141, 0.075, 0.12, 0.006, 0.07, 0.004, seg=1, mi=ST, rgba=DK)
    for k in range(5): m.rbox(-0.1, 0.146, 0.052 + k * 0.014, 0.1, 0.004, 0.006, 0.0, mi=I['plastic'], rgba=(0.02, 0.02, 0.02, 1))
    m.rbox(-0.1, 0.141, 0.165, 0.1, 0.006, 0.04, 0.004, seg=1, mi=I['screen'], rgba=(0.35, 0.85, 0.5, 1))
    for dx in (-0.045, 0.045): m.add(p_cyl(0.017, 0.022, 10), (-0.1 + dx, 0.13, 0.205), mi=ST, rgba=DK)
    m.between((-0.04, 0.1, 0.185), (-0.04, 0.1, 0.62), 0.005, seg=4, mi=I['steel_brushed'], rgba=BR); m.between((-0.04, 0.1, 0.185), (-0.04, 0.1, 0.4), 0.009, seg=5, mi=I['rubber'])
    m.rbox(-0.1, 0.1, 0.2, 0.12, 0.025, 0.02, 0.006, seg=1, mi=I['rubber'])
    m.lathe([(0.0, 0.0), (0.04, 0.0), (0.044, 0.09), (0.0, 0.09)], (0.17, 0.1, 0.015), seg=10, mi=I['steel_brushed'], rgba=(0.75, 0.76, 0.78, 1))
    m.rbox(0.22, 0.14, 0.04, 0.1, 0.08, 0.05, 0.008, seg=1, mi=I['paint'], rgba=(0.1, 0.3, 0.5, 1))
    weather(m, 9, dirt=0.1, dirt_h=0.1, blotch=0.2, angle=30.0)
    return m.finish('proto_story_radio_shelf', P)

def proto_notice_board(F, P):
    """Cork notice board 0.56 x 0.8 in a timber frame with pins and a tape strip; papers are baked signs placed by build_yard_story. Front toward +y, origin at the wall face, centred in x, bottom at z = 0."""
    m = mb(F); rnd = random.Random(3)
    m.rbox(0, 0.012, 0.4, 0.5, 0.024, 0.74, 0.0, mi=I['cork'])
    for sx in (-1, 1): m.rbox(sx * 0.27, 0.02, 0.4, 0.04, 0.04, 0.8, 0.004, seg=1, mi=I['timber'])
    for z in (0.02, 0.78): m.rbox(0, 0.02, z, 0.58, 0.04, 0.04, 0.004, seg=1, mi=I['timber'])
    for k in range(10): m.add(p_stud(0.007, 0.012, 4), (rnd.uniform(-0.22, 0.22), 0.024, rnd.uniform(0.1, 0.7)), (-math.pi / 2, 0, 0), mi=I['paint'], rgba=rnd.choice([(0.8, 0.1, 0.06, 1), (0.1, 0.4, 0.7, 1), (0.9, 0.8, 0.1, 1)]))
    weather(m, 1, dirt=0.15, dirt_h=0.1, blotch=0.15, angle=30.0)
    return m.finish('proto_story_notice_board', P)

def proto_hose_coil(F, P):
    """Coiled air/water hose: a flat spiral of orange hose two layers high with brass couplings on both ends and a loose end trailing off the coil."""
    m = mb(F); pts = []; turns = 3.6; n = 66
    for i in range(n + 1):
        t = i / n; a = turns * 2 * math.pi * t; R = 0.31 - 0.12 * t
        pts.append((R * math.cos(a), R * math.sin(a), 0.024 + 0.002 * math.sin(a * 3)))
    m.add(p_sweep(pts, 0.022, 5), mi=I['plastic'], rgba=(0.88, 0.42, 0.04, 1))
    pts2 = [(0.27 * math.cos(a), 0.27 * math.sin(a), 0.07) for a in [turns * 2 * math.pi * 0 + k * 0.35 for k in range(18)]]
    m.add(p_sweep(pts2, 0.022, 5), mi=I['plastic'], rgba=(0.82, 0.38, 0.04, 1))
    tail = bez(pts[0], (pts[0][0] + 0.2, pts[0][1] - 0.05, 0.03), (0.52, -0.22, 0.024), 6)
    m.add(p_sweep(tail, 0.022, 5), mi=I['plastic'], rgba=(0.88, 0.42, 0.04, 1))
    for p, q in ((tail[-1], tail[-2]), (pts[-1], pts[-2])):
        d = Vector(p) - Vector(q); d.normalize(); a = Vector(p)
        m.between(a - d * 0.03, a + d * 0.05, 0.03, seg=6, mi=I['steel_brushed'], rgba=(0.72, 0.55, 0.2, 1))
    weather(m, 3, dirt=0.4, dirt_h=0.05, streak=0.0, blotch=0.2, angle=30.0)
    return m.finish('proto_story_hose', P)

def proto_ore_spill(F, P, seed=0):
    """Ore spilled beside a car: a low scatter of broken lumps (none above 0.14 m) with rusty and copper-green chunks and a dark dust patch."""
    m = mb(F); rnd = random.Random(seed + 40)
    dust = bmesh.new(); res = bmesh.ops.create_icosphere(dust, subdivisions=1, radius=1.0)
    for v in res['verts']: v.co = Vector((v.co.x * 0.55, v.co.y * 0.32, max(v.co.z, 0.0) * 0.02))
    add_var(m, dust, (0, 0, 0.0), mi=I['props'], rgba=(0.06, 0.055, 0.05, 1), var=0.2, rnd=rnd)
    cols = [(0.055, 0.052, 0.05, 1), (0.09, 0.085, 0.08, 1), (0.04, 0.042, 0.05, 1), (0.14, 0.125, 0.11, 1), (0.30, 0.12, 0.05, 1), (0.08, 0.27, 0.2, 1), (0.07, 0.065, 0.075, 1)]
    for i in range(15):
        a = rnd.uniform(0, 6.283); d = rnd.uniform(0.0, 0.5) ** 0.8; s = rnd.uniform(0.035, 0.09)
        add_var(m, p_rock(rnd, s, 0.7, 0.3, 1 if s > 0.07 else 0), (math.cos(a) * 0.5 * d, math.sin(a) * 0.3 * d, s * 0.12), (0, 0, rnd.uniform(0, 6.28)), mi=I['paint'], rgba=cols[i % 7], var=0.3, rnd=rnd)
    weather(m, seed, dirt=0.0, streak=0.0, blotch=0.15)
    return m.finish(f'proto_story_ore_spill_{seed}', P)

def proto_shovel(F, P):
    """Long-handled round-point shovel lying flat: ash handle with D grip, riveted socket, worn steel blade."""
    m = mb(F)
    m.between((-0.55, 0.0, 0.022), (0.5, 0.0, 0.022), 0.017, seg=6, mi=I['timber'])
    m.rbox(-0.58, 0.0, 0.035, 0.05, 0.12, 0.03, 0.008, seg=1, mi=I['timber']); m.rbox(-0.58, 0.0, 0.04, 0.0, 0.0, 0.0, 0.0) if False else None
    m.lathe([(0.0, 0.0), (0.03, 0.0), (0.02, 0.08), (0.0, 0.08)], (0.45, 0, 0.022), (0, math.pi / 2, 0), seg=8, mi=I['steel_charcoal']) if False else m.add(p_cyl(0.026, 0.12, 8, 0.02), (0.54, 0, 0.026), (0, math.pi / 2, 0), mi=ST)
    m.rbox(0.74, 0.0, 0.012, 0.3, 0.25, 0.012, 0.004, rot=(0, 0.04, 0), seg=1, mi=I['steel_brushed'], rgba=(0.55, 0.52, 0.5, 1))
    m.rbox(0.9, 0.0, 0.012, 0.06, 0.1, 0.012, 0.0, mi=I['steel_brushed'], rgba=(0.55, 0.52, 0.5, 1))
    studs(m, [(0.58, sy * 0.03, 0.044) for sy in (-1, 1)], '+z', r=0.008, h=0.006, seg=4, mi=I['steel_brushed'], rgba=BR)
    weather(m, 2, dirt=0.3, dirt_h=0.05, blotch=0.2, angle=30.0)
    return m.finish('proto_story_shovel', P)

# ---------------------------------------------------------------------------------------------------------------- placement
def _free(x, y, r, boxes):
    for (a, b, c, d) in LANES:
        if a - r < x < b + r and c - r < y < d + r: return False
    for (a, b, c, d) in boxes:
        if a - r < x < b + r and c - r < y < d + r: return False
    return True

def _scene_boxes(ignore=('lamp_room_cabin',)):
    """Plan bounds of everything standing in the yard that could be walked into (same filter as fe_yardprops, minus the cabin whose wall we deliberately stand against)."""
    import fe_yardprops
    out = []; bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith(fe_yardprops.SKIP) or o.hide_render or o.name in ignore or o.name.startswith('proto_'): continue
        try: cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        except Exception: continue
        if min(c.z for c in cs) > 3.0 or max(c.z for c in cs) < 0.02: continue
        out.append((min(c.x for c in cs) + 8.0, max(c.x for c in cs) + 8.0, min(c.y for c in cs) - 80.0, max(c.y for c in cs) - 80.0))
    return out

def build_yard_story(F, C):
    yard = C['YARD']; P = collection('PROTOTYPES'); rnd = random.Random(88); placed = []; skipped = []
    pr = {'bench': proto_workbench(F, P), 'rail': proto_hook_rail(F, P), 'jacket_o': proto_jacket(F, P, (0.98, 0.42, 0.02, 1), 'jacket_orange'),
          'jacket_y': proto_jacket(F, P, (0.78, 0.88, 0.04, 1), 'jacket_lime'), 'hat_w': proto_hardhat(F, P, (0.9, 0.9, 0.86, 1), 'hardhat_white'), 'lantern': proto_lantern(F, P),
          'ext': proto_extinguisher_post(F, P), 'aid': proto_first_aid(F, P), 'radio': proto_radio_shelf(F, P), 'board': proto_notice_board(F, P), 'hose': proto_hose_coil(F, P),
          'spill0': proto_ore_spill(F, P, 0), 'spill1': proto_ore_spill(F, P, 1), 'shovel': proto_shovel(F, P),
          'tb_red': toolbox(F, P), 'tb_blue': toolbox(F, P, (0.07, 0.09, 0.20, 1), 'toolbox_blue')}
    boxes = _scene_boxes()
    def place(key, name, x, y, rz=0.0, z=0.0, support='floor', r=0.3, wall=False, **kw):
        """Instance if the footprint is clear of scene objects and lanes (wall items only test the lanes and neighbours, not the cabin they hang on)."""
        if not wall and not _free(x, y, r, boxes + placed_boxes):
            skipped.append(name); return None
        if wall and not _free(x, y, 0.0, [b for b in boxes if not (b[0] <= x <= b[1] and b[2] <= y <= b[3] and False)]):
            skipped.append(name); return None
        o = inst(pr[key], name, x, y, yard, rz=rz, z=z, support=support)
        if not wall: placed_boxes.append((x - r, x + r, y - r, y + r))
        return o
    placed_boxes = []

    # ---- workbench against the front wall between the two windows, with a radio shelf above it
    bx, by = -43.6, -72.73
    place('bench', 'story_workbench', bx, by, support='floor', r=0.0, wall=True)
    place('radio', 'story_radio_shelf', bx - 0.02, WALL_Y, z=1.45, support='wall', wall=True)
    # ---- notice board on the west part of the front wall, papers pinned on it (baked signs)
    nbx, nz = -45.46, 1.05
    place('board', 'story_notice_board', nbx, WALL_Y, z=nz, support='wall', wall=True)
    py = WALL_Y + 0.05
    sign(yard, 'sign_story_notices', 'LAMP ROOM NOTICES', nbx, py, nz + 0.7, 'N', 0.46, 0.09, style='board')
    for k, (txt, sub, sx, sz, w, h, st) in enumerate((('SHIFT ROTA', None, -0.1, 0.45, 0.2, 0.22, 'info'), ('LAMPS OUT', 'Charge nightly', 0.1, 0.5, 0.17, 0.16, 'staff'),
                                                        ('GAS TEST', 'Before entry', -0.11, 0.14, 0.18, 0.2, 'hazard'), ('KEYS FOUND', 'Ask at desk', 0.09, 0.15, 0.2, 0.18, 'info'))):
        sign(yard, f'sign_story_note_{k}', txt, nbx + sx, py, nz + sz, 'N', w, h, sub=sub, style=st, t=0.004)
    # ---- hooks beside the door with two hi-vis jackets and a helmet
    hx = -41.66; hz = 1.42
    place('rail', 'story_hook_rail', hx, WALL_Y, z=hz, support='wall', wall=True)
    place('jacket_o', 'story_jacket_0', hx - 0.24, WALL_Y + 0.11, z=hz + 0.1, rz=0.0, support='wall', wall=True)
    place('jacket_y', 'story_jacket_1', hx, WALL_Y + 0.11, z=hz + 0.1, rz=0.04, support='wall', wall=True)
    o = place('hat_w', 'story_hardhat_hook', hx + 0.24, WALL_Y + 0.13, z=hz + 0.0, rz=0.0, support='wall', wall=True)
    if o: o.rotation_euler = (-math.pi / 2 + 0.15, 0, 0); o.location.z = hz + 0.17
    # ---- lantern on the bench end with a small real light
    lx, ly, lz = bx + 0.95 - 0.3, by + 0.05, 0.92
    inst(pr['lantern'], 'story_lantern', lx - 0.05, ly + 0.0, yard, z=lz, support='stack')
    try:
        lc = C['LIGHTS']; l = bpy.data.lights.new('LIGHT_story_lantern', 'POINT'); l.energy = 26.0; l.color = (1.0, 0.6, 0.24); l.shadow_soft_size = 0.05
        lo = bpy.data.objects.new('LIGHT_story_lantern', l); lo.location = (LX(lx - 0.05), LY(ly), lz + 0.14); lc.objects.link(lo)
    except Exception: pass
    # ---- tool boxes stacked west of the bench, on the floor against the wall
    tx, ty = -45.0, -72.78
    if _free(tx, ty, 0.0, boxes):
        inst(pr['tb_red'], 'story_toolbox_0', tx, ty, yard, rz=0.04, support='floor'); inst(pr['tb_blue'], 'story_toolbox_1', tx + 0.02, ty + 0.01, yard, rz=-0.08, z=0.285, support='stack')
        inst(pr['tb_red'], 'story_toolbox_2', tx + 0.33, ty, yard, rz=0.0, support='floor')
    # ---- fire extinguisher post and first-aid cabinet at the east end of the cabin
    ex, ey = -39.35, -73.0
    if place('ext', 'story_extinguisher_post', ex, ey, rz=0.0, support='floor', r=0.18):
        sign(yard, 'sign_story_fire', 'FIRE POINT', ex, ey + 0.05, 1.62, 'N', 0.34, 0.2, sub='Dry powder', style='staff', icon='warn')
    o = place('aid', 'story_first_aid', END_X, -74.3, rz=-math.pi / 2, z=1.25, support='wall', wall=True)
    sign(yard, 'sign_story_first_aid', 'FIRST AID', END_X + 0.17, -74.3, 1.45, 'E', 0.26, 0.2, style='med', icon='cross')
    # ---- coiled hose on the ground near the bench, ore spilled and a shovel by the first car
    for (x, y, rz) in ((-42.3, -72.35, 0.6), (-44.55, -72.1, 0.2), (-45.4, -71.95, 0.1)):
        if place('hose', 'story_hose', x, y, rz=rz, support='floor', r=0.42): break
    for k, (x, y, rz) in enumerate(((-39.0, -71.85, 0.4), (-37.9, -71.75, 2.0))):
        place(f'spill{k}', f'story_ore_spill_{k}', x, y, rz=rz, support='floor_debris', r=0.35)
    place('shovel', 'story_shovel', -40.0, -71.6, rz=0.35, support='floor_debris', r=0.5)
    print('YARD_STORY placed', len(placed_boxes), 'skipped', skipped)
    return skipped
