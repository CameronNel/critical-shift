"""Wall-hung dressing in the spawn room's idiom: framed posters, bulletin board, extinguisher, first-aid box, clock, signs."""
from fe_kit import *
from fe_assets_int import STD, I, mb

def _text(F, coll, name, body, size, loc, rot, mat='signage', align='CENTER', extrude=0.002, color=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); cu.materials.append(F[mat]); coll.objects.link(o); o.location = loc; o.rotation_euler = rot
    return o

FACE = {'S': (0, -1), 'N': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
ROT = {'N': 0.0, 'S': math.pi, 'E': -math.pi / 2, 'W': math.pi / 2}

def put(o, facing, x, y, z):
    """Place a wall prop (built with its back at local y=0 and its front toward +y) on a wall; (x, y) is the plan point on the wall face."""
    o.location = (LX(x), LY(y), z); o.rotation_euler = (0, 0, ROT[facing]); return o

def poster(F, P, variant=0, w=0.8, h=1.1, name='poster'):
    """Framed poster using the spawn room's poster art (portrait or landscape by shape)."""
    m = mb(F); frame = (0.07, 0.06, 0.06, 1)
    land = w > h
    m.rbox(0, 0.02, h / 2, w, 0.04, h, 0.008, mi=I['timber'], rgba=frame)
    m.rbox(0, 0.041, h / 2, w - 0.05, 0.006, h - 0.05, 0.002, mi=I['signage'], rgba=(0.6, 0.57, 0.5, 1))
    m.quad_image(0, 0.0452, h / 2, w - 0.1, h - 0.1, I['poster_land'] if land else I['poster_port'])
    return m.finish(f'proto_{name}_{variant}', P)

def bulletin(F, P, w=1.5, h=1.0):
    """Cork notice board in a timber frame with pinned notices."""
    m = mb(F); rnd = random.Random(4)
    m.rbox(0, 0.025, h / 2, w, 0.05, h, 0.01, mi=I['timber'], rgba=(0.2, 0.12, 0.06, 1))
    m.rbox(0, 0.055, h / 2, w - 0.08, 0.012, h - 0.08, 0.003, mi=I['cork'], rgba=(0.5, 0.36, 0.22, 1))
    for k in range(8):
        x = -w / 2 + 0.2 + (k % 4) * 0.34 + rnd.uniform(-0.03, 0.03); z = h * 0.32 + (k // 4) * 0.36 + rnd.uniform(-0.02, 0.02)
        pw, ph = rnd.uniform(0.2, 0.28), rnd.uniform(0.25, 0.32)
        m.rbox(x, 0.064, z, pw, 0.003, ph, 0.001, rot=(0, rnd.uniform(-0.07, 0.07), 0), mi=I['signage'], rgba=rnd.choice([(0.86, 0.84, 0.76, 1), (0.85, 0.74, 0.42, 1), (0.74, 0.78, 0.82, 1), (0.78, 0.46, 0.38, 1)]))
        m.add(p_sphere(0.009, rings=4, seg=6), (x, 0.069, z + ph / 2 - 0.02), mi=I['plastic'], rgba=rnd.choice([(0.8, 0.12, 0.1, 1), (0.1, 0.3, 0.8, 1), (0.9, 0.8, 0.1, 1)]))
        for ln in range(5): m.rbox(x, 0.067, z + ph / 2 - 0.055 - ln * 0.045, pw - rnd.uniform(0.05, 0.12), 0.002, 0.008, 0.0005, mi=I['signage'], rgba=(0.14, 0.14, 0.14, 1))
    return m.finish('proto_bulletin', P)

def extinguisher(F, P):
    m = mb(F); red = (0.62, 0.06, 0.04, 1)
    m.rbox(0, 0.01, 0.55, 0.14, 0.02, 0.12, 0.004, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.lathe([(0.0, 0.0), (0.06, 0.0), (0.075, 0.03), (0.08, 0.1), (0.08, 0.38), (0.07, 0.46), (0.04, 0.5), (0.0, 0.5)], loc=(0, 0.09, 0.0), seg=28, mi=I['plastic'], rgba=red)
    m.cylz(0, 0.09, 0.5, 0.56, 0.022, seg=12, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.rbox(0.03, 0.09, 0.59, 0.1, 0.03, 0.03, 0.01, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.between((0.07, 0.09, 0.56), (0.12, 0.14, 0.22), 0.01, seg=6, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(0, 0.09, 0.28, 0.17, 0.17, 0.05, 0.01, mi=I['plastic'], rgba=(0.9, 0.78, 0.1, 1)); m.rbox(0, 0.175, 0.3, 0.08, 0.004, 0.1, 0.001, mi=I['signage'], rgba=(0.9, 0.9, 0.88, 1))
    m.rbox(0, 0.08, 0.08, 0.16, 0.12, 0.016, 0.004, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    return m.finish('proto_extinguisher', P)

def first_aid(F, P):
    m = mb(F)
    m.rbox(0, 0.07, 0.25, 0.46, 0.14, 0.4, 0.02, mi=I['plastic'], rgba=(0.82, 0.82, 0.78, 1))
    m.rbox(0, 0.145, 0.25, 0.42, 0.012, 0.36, 0.004, mi=I['plastic'], rgba=(0.88, 0.88, 0.84, 1))
    m.rbox(0, 0.155, 0.27, 0.05, 0.006, 0.16, 0.002, mi=I['signage'], rgba=(0.1, 0.55, 0.3, 1)); m.rbox(0, 0.155, 0.27, 0.16, 0.006, 0.05, 0.002, mi=I['signage'], rgba=(0.1, 0.55, 0.3, 1))
    m.rbox(0.17, 0.15, 0.25, 0.02, 0.012, 0.04, 0.004, mi=I['plastic'], rgba=(0.3, 0.3, 0.3, 1))
    return m.finish('proto_first_aid', P)

def wall_clock(F, P):
    m = mb(F)
    m.add(p_torus(0.17, 0.014, 40, 8), (0, 0.04, 0.0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.08, 0.08, 0.09, 1))
    m.add(p_cyl(0.165, 0.018, 40), (0, 0.03, 0.0), (math.pi / 2, 0, 0), mi=I['signage'], rgba=(0.88, 0.86, 0.8, 1))
    for k in range(12): a = k * math.pi / 6; m.rbox(math.sin(a) * 0.14, 0.042, math.cos(a) * 0.14, 0.012, 0.004, 0.025, 0.001, rot=(0, -a, 0), mi=I['signage'], rgba=(0.1, 0.1, 0.1, 1))
    m.rbox(0.0, 0.048, 0.05, 0.012, 0.004, 0.11, 0.001, mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1)); m.rbox(0.045, 0.05, 0.015, 0.012, 0.004, 0.09, 0.001, rot=(0, 1.0, 0), mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1))
    return m.finish('proto_wall_clock', P)

def socket(F, P):
    m = mb(F); m.rbox(0, 0.012, 0, 0.09, 0.024, 0.09, 0.006, mi=I['plastic'], rgba=(0.88, 0.88, 0.85, 1)); m.rbox(0, 0.026, 0.0, 0.02, 0.006, 0.02, 0.002, mi=I['plastic'], rgba=(0.2, 0.2, 0.2, 1)); return m.finish('proto_socket', P)

def exit_sign(F, P):
    m = mb(F); m.rbox(0, 0.03, 0.0, 0.5, 0.06, 0.2, 0.012, mi=I['plastic'], rgba=(0.85, 0.85, 0.82, 1)); m.rbox(0, 0.062, 0.0, 0.46, 0.004, 0.16, 0.002, mi=I['emissive'], rgba=(0.1, 0.85, 0.35, 1))
    return m.finish('proto_exit_sign', P)

def sign_plate(F, P, w, h, rgba, name):
    m = mb(F); m.rbox(0, 0.01, 0, w, 0.02, h, 0.006, mi=I['signage'], rgba=rgba); return m.finish('proto_' + name, P)

def door_leaf(F, P, w=1.0, h=2.1, rgba=(0.2, 0.2, 0.22, 1), glazed=True):
    m = mb(F)
    m.rbox(0, 0.0, h / 2, w, 0.045, h, 0.008, mi=I['plastic'], rgba=rgba)
    if glazed: m.rbox(0, 0.024, h * 0.7, w * 0.4, 0.006, h * 0.32, 0.004, mi=I['glass'])
    m.rbox(w * 0.38, 0.05, 1.0, 0.04, 0.04, 0.18, 0.012, mi=I['steel_brushed'], rgba=(0.62, 0.64, 0.66, 1))
    return m.finish('proto_door_leaf', P)
