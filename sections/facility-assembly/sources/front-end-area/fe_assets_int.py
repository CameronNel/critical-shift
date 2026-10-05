"""Interior furniture and fittings at spawn-room quality: rounded forms, turned legs, subdivided upholstery, real leaves."""
from fe_kit import *

STD = ['plastic', 'steel_charcoal', 'fabric', 'timber', 'laminate', 'glass', 'emissive', 'rubber', 'foliage', 'props', 'signage', 'steel_accent', 'trim', 'concrete_slab', 'screen', 'poster_land', 'poster_port', 'tv_slide']
I = {k: i for i, k in enumerate(STD)}
def mb(F): return MB2([F[k] for k in STD])

def chair(F, P, rgba=(0.55, 0.17, 0.09, 1), name='chair'):
    m = mb(F)
    # moulded shell seat and back on a bent-tube frame
    m.rbox(0, 0.0, 0.455, 0.45, 0.43, 0.05, 0.022, mi=I['plastic'], rgba=rgba)
    m.rbox(0, -0.205, 0.72, 0.43, 0.04, 0.30, 0.018, rot=(-0.10, 0, 0), mi=I['plastic'], rgba=rgba)
    m.rbox(0, 0.0, 0.425, 0.40, 0.38, 0.012, 0.004, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    for sx in (-1, 1):
        for sy, splay in ((-1, -0.05), (1, 0.07)):
            m.between((sx * 0.185, sy * 0.17, 0.43), (sx * 0.2, sy * 0.19 + splay, 0.012), 0.0135, seg=12, mi=I['steel_charcoal'], rgba=(0.13, 0.13, 0.14, 1))
            m.cylz(sx * 0.2, sy * 0.19 + splay, 0.0, 0.016, 0.019, seg=12, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
        m.between((sx * 0.185, -0.17, 0.43), (sx * 0.19, -0.222, 0.86), 0.0125, seg=12, mi=I['steel_charcoal'], rgba=(0.13, 0.13, 0.14, 1))
    for z in (0.17, 0.30): m.between((-0.19, 0.0, z), (0.19, 0.0, z), 0.0085, seg=8, mi=I['steel_charcoal'], rgba=(0.13, 0.13, 0.14, 1))
    for sy in (-1, 1): m.between((-0.19, sy * 0.185, 0.34), (0.19, sy * 0.185, 0.34), 0.0085, seg=8, mi=I['steel_charcoal'], rgba=(0.13, 0.13, 0.14, 1))
    return m.finish('proto_' + name, P)

def table(F, P, L=1.8, W=0.9, H=0.75, name='table'):
    m = mb(F)
    m.rbox(0, 0, H - 0.02, L, W, 0.036, 0.014, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    m.rbox(0, 0, H - 0.045, L - 0.02, W - 0.02, 0.014, 0.004, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.3)
        m.rbox(x, 0, 0.012, 0.09, W - 0.28, 0.024, 0.008, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
        m.rbox(x, 0, H - 0.07, 0.08, W - 0.3, 0.03, 0.008, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
        m.cylz(x, 0, 0.024, H - 0.07, 0.036, seg=20, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
        for sy in (-1, 1): m.cylz(x, sy * (W / 2 - 0.2), 0.0, 0.025, 0.026, seg=14, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(0, 0, 0.16, L - 0.62, 0.035, 0.035, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    return m.finish('proto_' + name, P)

def coffee_table(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.40, 1.1, 0.6, 0.04, 0.018, mi=I['timber'])
    m.rbox(0, 0, 0.16, 0.9, 0.42, 0.03, 0.01, mi=I['timber'])
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.between((sx * 0.46, sy * 0.24, 0.38), (sx * 0.5, sy * 0.26, 0.015), 0.021, seg=14, r2=0.014, mi=I['timber'])
            m.cylz(sx * 0.5, sy * 0.26, 0.0, 0.012, 0.018, seg=14, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    return m.finish('proto_coffee_table', P)

def sofa(F, P, rgba=(0.52, 0.16, 0.09, 1), seats=2, name='sofa'):
    m = mb(F); w = 0.78 * seats + 0.34; d = 0.92
    leg = (0.07, 0.065, 0.06, 1)
    m.rbox(0, 0, 0.22, w, d, 0.16, 0.03, mi=I['fabric'], rgba=tuple(c * 0.85 for c in rgba[:3]) + (1,))
    for i in range(seats):
        x = (i - (seats - 1) / 2) * 0.78
        m.cushion(x, 0.06, 0.38, 0.76, 0.72, 0.20, r=0.07, levels=1, mi=I['fabric'], rgba=rgba)
        m.cushion(x, -0.34, 0.66, 0.76, 0.26, 0.52, r=0.09, rot=(-0.16, 0, 0), levels=1, mi=I['fabric'], rgba=rgba)
    for sx in (-1, 1):
        m.cushion(sx * (w / 2 - 0.08), 0.0, 0.46, 0.18, d, 0.46, r=0.06, levels=1, mi=I['fabric'], rgba=tuple(c * 0.92 for c in rgba[:3]) + (1,))
    m.rbox(0, -0.44, 0.58, w - 0.1, 0.1, 0.62, 0.04, mi=I['fabric'], rgba=tuple(c * 0.8 for c in rgba[:3]) + (1,))
    for sx in (-1, 1):
        for sy in (-1, 1): m.between((sx * (w / 2 - 0.12), sy * 0.34, 0.13), (sx * (w / 2 - 0.08), sy * 0.36, 0.008), 0.032, seg=12, r2=0.02, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    return m.finish('proto_' + name, P)

def armchair(F, P, rgba=(0.12, 0.17, 0.33, 1)):
    o = sofa(F, P, rgba, seats=1, name='armchair'); return o

def pot(m, h, r, rgba=(0.62, 0.27, 0.14, 1), slot='concrete_slab'):
    prof = [(r * 0.62, 0.0), (r * 0.7, 0.012), (r * 0.88, h * 0.35), (r, h * 0.92), (r * 1.04, h), (r * 0.96, h), (r * 0.9, h - 0.01), (r * 0.86, h - 0.03)]
    m.lathe(prof, seg=28, mi=I['props'], rgba=rgba)
    m.cylz(0, 0, h - 0.06, h - 0.03, r * 0.88, seg=28, mi=I['props'], rgba=(0.09, 0.055, 0.035, 1))

def plant_leafy(F, P, seed=1, h=1.5):
    m = mb(F); rnd = random.Random(seed); pot(m, 0.34, 0.2)
    green = [(0.10, 0.28, 0.08, 1), (0.13, 0.33, 0.09, 1), (0.08, 0.24, 0.07, 1)]
    for t in range(3):
        a = t * 2.1 + rnd.uniform(0, 1); lean = rnd.uniform(0.04, 0.12)
        m.between((0, 0, 0.30), (math.cos(a) * lean, math.sin(a) * lean, h * 0.55), 0.016, seg=8, r2=0.011, mi=I['props'], rgba=(0.30, 0.2, 0.1, 1))
    for i in range(34):
        z = rnd.uniform(0.35 * h, h * 1.0); a = rnd.uniform(0, 6.28); R = 0.05 + (z / h) * 0.12
        m.leaf((math.cos(a) * R * 0.5, math.sin(a) * R * 0.5, z), rnd.uniform(0.22, 0.34), rnd.uniform(0.085, 0.12), bend=rnd.uniform(0.2, 0.5), twist=rnd.uniform(-0.3, 0.3),
               yaw=a - math.pi / 2, pitch=rnd.uniform(0.0, 0.55), mi=I['foliage'], rgba=rnd.choice(green))
    return m.finish(f'proto_plant_leafy_{seed}', P)

def plant_spiky(F, P, seed=2, h=1.2):
    m = mb(F); rnd = random.Random(seed); pot(m, 0.3, 0.19, rgba=(0.12, 0.13, 0.2, 1))
    green = [(0.11, 0.30, 0.09, 1), (0.14, 0.34, 0.1, 1), (0.09, 0.26, 0.08, 1)]
    for i in range(46):
        a = rnd.uniform(0, 6.28); tilt = rnd.uniform(0.8, 1.45); L = h * rnd.uniform(0.5, 1.0)
        m.leaf((math.cos(a) * 0.02, math.sin(a) * 0.02, 0.3), L, rnd.uniform(0.022, 0.032), bend=0.0, twist=rnd.uniform(-0.4, 0.4), droop=rnd.uniform(0.2, 0.7),
               yaw=a - math.pi / 2, pitch=tilt, mi=I['foliage'], rgba=rnd.choice(green))
    return m.finish(f'proto_plant_spiky_{seed}', P)

def floor_lamp(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.16, 0.0), (0.17, 0.012), (0.15, 0.03), (0.02, 0.035)], seg=28, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.cylz(0, 0, 0.03, 1.5, 0.014, seg=12, mi=I['steel_accent'], rgba=(0.7, 0.55, 0.2, 1))
    m.lathe([(0.07, 1.42), (0.08, 1.46), (0.15, 1.72), (0.155, 1.74), (0.145, 1.74), (0.14, 1.72), (0.07, 1.48)], seg=32, mi=I['fabric'], rgba=(0.82, 0.72, 0.55, 1))
    m.sphere(0, 0, 1.52, 0.045, rings=8, seg=14, mi=I['emissive'], rgba=(1.0, 0.82, 0.55, 1))
    return m.finish('proto_floor_lamp', P)

def pendant(F, P, name='pendant'):
    m = mb(F)
    m.cylz(0, 0, 0.26, 1.4, 0.006, seg=6, mi=I['steel_charcoal'], rgba=(0.08, 0.08, 0.09, 1))
    m.cylz(0, 0, 1.4, 1.43, 0.045, seg=16, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.lathe([(0.04, 0.3), (0.06, 0.29), (0.22, 0.04), (0.26, 0.0), (0.255, -0.004), (0.215, 0.034), (0.055, 0.28), (0.04, 0.28)], seg=36, mi=I['steel_accent'], rgba=(0.72, 0.36, 0.06, 1))
    m.sphere(0, 0, 0.1, 0.07, rings=8, seg=14, mi=I['emissive'], rgba=(1.0, 0.86, 0.6, 1))
    return m.finish('proto_' + name, P)

def vending(F, P, rgba=(0.62, 0.11, 0.09, 1), seed=0, name='vending'):
    m = mb(F); rnd = random.Random(seed); W, D, H = 0.98, 0.86, 1.92
    wx0, wx1, wz0, wz1 = -0.43, 0.2, 0.58, 1.66          # product bay cavity
    # cabinet built around the bay so products are really visible
    m.rbox(0, -D / 2 + 0.2, H / 2 + 0.05, W, 0.4, H - 0.1, 0.02, mi=I['plastic'], rgba=rgba)                         # back block
    m.rbox(wx0 - 0.03, 0.0, H / 2 + 0.05, 0.12, D, H - 0.1, 0.02, mi=I['plastic'], rgba=rgba)                        # left wall
    m.rbox((wx1 + W / 2) / 2, 0.0, H / 2 + 0.05, W / 2 - wx1, D, H - 0.1, 0.02, mi=I['plastic'], rgba=rgba)           # control block
    m.rbox((wx0 + wx1) / 2, 0.0, (wz1 + H) / 2 + 0.02, wx1 - wx0, D, H - wz1 - 0.02, 0.02, mi=I['plastic'], rgba=rgba) # top block
    m.rbox((wx0 + wx1) / 2, 0.0, wz0 / 2 + 0.05, wx1 - wx0, D, wz0 - 0.05, 0.02, mi=I['plastic'], rgba=rgba)           # bottom block
    m.rbox((wx0 + wx1) / 2, -D / 2 + 0.41, (wz0 + wz1) / 2, wx1 - wx0, 0.02, wz1 - wz0, 0.004, mi=I['steel_charcoal'], rgba=(0.9, 0.9, 0.92, 1))  # bay back panel
    m.rbox(0, 0.0, 0.025, W - 0.08, D - 0.08, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.07, 0.07, 0.08, 1))
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(sx * (W / 2 - 0.1), sy * (D / 2 - 0.1), -0.0, 0.03, 0.03, seg=12, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox((wx0 + wx1) / 2, D / 2 - 0.02, wz1 + 0.12, wx1 - wx0, 0.03, 0.2, 0.01, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))   # lit header
    m.rbox((wx0 + wx1) / 2, D / 2 + 0.0, wz1 + 0.12, 0.4, 0.012, 0.05, 0.004, mi=I['signage'], rgba=(0.08, 0.08, 0.1, 1))
    m.rbox((wx0 + wx1) / 2, 0.1, wz1 - 0.04, wx1 - wx0 - 0.04, 0.5, 0.012, 0.004, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))     # bay light
    cols = [(0.78, 0.1, 0.08, 1), (0.1, 0.35, 0.72, 1), (0.9, 0.7, 0.1, 1), (0.12, 0.55, 0.28, 1), (0.9, 0.9, 0.88, 1), (0.45, 0.25, 0.1, 1), (0.85, 0.4, 0.1, 1)]
    for r in range(5):
        z = wz0 + 0.08 + r * 0.2
        m.rbox((wx0 + wx1) / 2, 0.1, z - 0.02, wx1 - wx0 - 0.04, 0.52, 0.012, 0.004, mi=I['steel_charcoal'], rgba=(0.55, 0.57, 0.6, 1))
        for c in range(6):
            x = wx0 + 0.07 + c * 0.1
            if rnd.random() < 0.12: continue
            col = rnd.choice(cols)
            m.cylz(x, 0.33, z - 0.012, z + 0.1, 0.03, seg=10, mi=I['plastic'], rgba=col)
            m.add(p_torus(0.05, 0.004, 16, 5), (x, 0.36, z - 0.018), (0, 0, 0), (1, 1, 1), I['steel_charcoal'], (0.5, 0.5, 0.52, 1))
    m.rbox((wx0 + wx1) / 2, D / 2 + 0.004, (wz0 + wz1) / 2, wx1 - wx0 - 0.02, 0.008, wz1 - wz0 - 0.02, 0.002, mi=I['glass'])
    cx = (wx1 + W / 2) / 2
    m.rbox(cx, D / 2 + 0.004, 1.2, 0.2, 0.025, 1.1, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.rbox(cx, D / 2 + 0.02, 1.52, 0.14, 0.012, 0.08, 0.004, mi=I['screen'], rgba=(0.3, 0.75, 0.45, 1))
    for r in range(4):
        for c in range(3): m.rbox(cx - 0.05 + c * 0.05, D / 2 + 0.022, 1.32 - r * 0.055, 0.035, 0.012, 0.035, 0.005, mi=I['plastic'], rgba=(0.75, 0.75, 0.74, 1))
    m.rbox(cx, D / 2 + 0.02, 1.02, 0.12, 0.014, 0.012, 0.004, mi=I['steel_charcoal'], rgba=(0.02, 0.02, 0.02, 1))
    m.rbox(-0.12, D / 2 + 0.002, 0.3, 0.7, 0.03, 0.26, 0.012, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
    m.rbox(-0.12, D / 2 + 0.022, 0.3, 0.6, 0.012, 0.17, 0.008, mi=I['plastic'], rgba=(0.02, 0.02, 0.02, 1))
    return m.finish('proto_' + name, P)

def tv(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.62, 1.38, 0.05, 0.8, 0.012, mi=I['steel_charcoal'], rgba=(0.03, 0.03, 0.035, 1))
    m.quad_image(0, 0.0345, 0.62, 1.32, 0.74, I['tv_slide'])
    m.rbox(0, 0.0, 0.015, 0.7, 0.28, 0.03, 0.01, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(0, -0.02, 0.2, 0.08, 0.04, 0.4, 0.01, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    return m.finish('proto_tv', P)

def bin_(F, P, rgba=(0.12, 0.3, 0.2, 1), name='bin'):
    m = mb(F)
    m.lathe([(0.16, 0.0), (0.2, 0.02), (0.235, 0.45), (0.24, 0.8), (0.235, 0.81), (0.225, 0.8), (0.22, 0.05)], seg=32, mi=I['plastic'], rgba=rgba)
    m.lathe([(0.0, 0.84), (0.1, 0.84), (0.24, 0.82), (0.26, 0.8), (0.24, 0.79), (0.0, 0.79)], seg=32, mi=I['plastic'], rgba=tuple(c * 0.7 for c in rgba[:3]) + (1,))
    m.rbox(0, 0.21, 0.82, 0.13, 0.05, 0.03, 0.01, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
    return m.finish('proto_' + name, P)

def mug(F, P):
    m = mb(F); m.lathe([(0.0, 0.0), (0.036, 0.0), (0.04, 0.01), (0.042, 0.09), (0.04, 0.09), (0.036, 0.085), (0.0, 0.01)], seg=24, mi=I['plastic'], rgba=(0.92, 0.9, 0.84, 1))
    m.add(p_torus(0.028, 0.0045, 16, 6), (0.05, 0, 0.05), (math.pi / 2, 0, 0), (1, 1, 1), I['plastic'], (0.92, 0.9, 0.84, 1))
    return m.finish('proto_mug', P)

def tray(F, P):
    m = mb(F); m.rbox(0, 0, 0.012, 0.44, 0.32, 0.024, 0.01, mi=I['plastic'], rgba=(0.12, 0.35, 0.5, 1))
    m.lathe([(0.0, 0.024), (0.07, 0.024), (0.095, 0.05), (0.0, 0.034)], loc=(-0.1, 0.02, 0.0), seg=24, mi=I['laminate'], rgba=(0.9, 0.86, 0.78, 1))
    m.rbox(0.12, -0.02, 0.05, 0.12, 0.09, 0.05, 0.015, mi=I['props'], rgba=(0.7, 0.3, 0.15, 1))
    m.cylz(0.14, 0.1, 0.024, 0.11, 0.03, seg=14, bevel=0.006, mi=I['plastic'], rgba=(0.85, 0.85, 0.82, 1))
    return m.finish('proto_tray', P)

def bottle(F, P):
    m = mb(F); m.lathe([(0.0, 0.0), (0.03, 0.0), (0.032, 0.02), (0.032, 0.14), (0.024, 0.18), (0.012, 0.2), (0.012, 0.225), (0.0, 0.225)], seg=20, mi=I['glass'])
    m.cylz(0, 0, 0.22, 0.236, 0.014, seg=12, mi=I['plastic'], rgba=(0.75, 0.1, 0.08, 1))
    return m.finish('proto_bottle', P)

def stanchion(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.15, 0.0), (0.155, 0.015), (0.12, 0.035), (0.03, 0.045)], seg=24, mi=I['steel_charcoal'], rgba=(0.62, 0.64, 0.66, 1))
    m.cylz(0, 0, 0.04, 1.0, 0.024, seg=14, mi=I['steel_charcoal'], rgba=(0.62, 0.64, 0.66, 1))
    m.sphere(0, 0, 1.03, 0.04, rings=8, seg=14, mi=I['steel_charcoal'], rgba=(0.62, 0.64, 0.66, 1))
    m.rbox(0.5, 0, 0.9, 1.0, 0.012, 0.06, 0.004, mi=I['fabric'], rgba=(0.5, 0.1, 0.08, 1))
    return m.finish('proto_stanchion', P)

def kiosk(F, P):
    """Self-service ordering kiosk: pedestal cabinet with tilted touchscreen, card reader and ticket slot."""
    m = mb(F)
    m.rbox(0, 0, 0.5, 0.56, 0.4, 1.0, 0.03, mi=I['plastic'], rgba=(0.14, 0.15, 0.2, 1))
    m.rbox(0, 0.05, 1.18, 0.54, 0.22, 0.4, 0.04, rot=(-0.28, 0, 0), mi=I['plastic'], rgba=(0.14, 0.15, 0.2, 1))
    m.rbox(0, 0.178, 1.205, 0.44, 0.01, 0.32, 0.004, rot=(-0.28, 0, 0), mi=I['screen'], rgba=(0.9, 0.62, 0.2, 1))
    m.rbox(0, 0.205, 0.93, 0.2, 0.05, 0.1, 0.012, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(0, 0.205, 0.72, 0.16, 0.03, 0.02, 0.006, mi=I['steel_charcoal'], rgba=(0.01, 0.01, 0.01, 1))
    m.rbox(0, 0.0, 1.43, 0.58, 0.32, 0.05, 0.02, mi=I['steel_accent'], rgba=(0.72, 0.36, 0.06, 1))
    m.rbox(0, 0, 0.02, 0.62, 0.46, 0.04, 0.012, mi=I['steel_charcoal'], rgba=(0.07, 0.07, 0.08, 1))
    return m.finish('proto_kiosk', P)

def booth(F, P, rgba=(0.45, 0.14, 0.08, 1)):
    m = mb(F); W = 3.0
    m.rbox(0, 0.1, 0.17, W, 0.9, 0.3, 0.03, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    for i in range(3):
        x = -1.0 + i * 1.0
        m.cushion(x, 0.12, 0.43, 0.94, 0.78, 0.2, r=0.07, levels=1, mi=I['fabric'], rgba=rgba)
        m.cushion(x, -0.2, 0.84, 0.94, 0.2, 0.62, r=0.08, levels=1, mi=I['fabric'], rgba=rgba)
    m.rbox(0, -0.31, 0.9, W, 0.05, 1.0, 0.015, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    for sx in (-1, 1): m.rbox(sx * W / 2, 0.08, 0.5, 0.06, 0.92, 0.95, 0.02, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    m.rbox(0, 1.1, 0.74, 2.3, 0.78, 0.04, 0.016, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    m.cylz(0, 1.1, 0.0, 0.72, 0.05, seg=20, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.lathe([(0.0, 0.0), (0.3, 0.0), (0.32, 0.02), (0.1, 0.05)], loc=(0, 1.1, 0), seg=24, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    return m.finish('proto_booth', P)

def foosball(F, P):
    """Table football, long axis along X (0..1.4 x 0.75)."""
    m = mb(F); L, W = 1.42, 0.76
    wood = (0.32, 0.18, 0.09, 1); metal = (0.7, 0.72, 0.74, 1)
    m.rbox(0, 0, 0.86, L, W, 0.14, 0.02, mi=I['timber'], rgba=wood)
    m.rbox(0, 0, 0.935, L - 0.16, W - 0.16, 0.012, 0.004, mi=I['laminate'], rgba=(0.14, 0.4, 0.2, 1))
    for sx in (-1, 1):
        m.rbox(sx * (L / 2 - 0.04), 0, 0.95, 0.08, W - 0.1, 0.05, 0.012, mi=I['timber'], rgba=wood)
        for sy in (-1, 1): m.lathe([(0.0, 0.0), (0.045, 0.0), (0.05, 0.03), (0.03, 0.2), (0.04, 0.5), (0.04, 0.78), (0.0, 0.78)], loc=(sx * (L / 2 - 0.08), sy * (W / 2 - 0.08), 0.0), seg=16, mi=I['timber'], rgba=wood)
        m.rbox(sx * (L / 2 - 0.085), 0, 0.93, 0.1, 0.2, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.05, 1))
    m.rbox(0, 0, 0.78, L - 0.2, 0.06, 0.04, 0.01, mi=I['timber'], rgba=wood)
    # rods and players
    xs = [-0.58, -0.43, -0.28, -0.13, 0.03, 0.18, 0.33, 0.48]
    counts = [1, 2, 3, 5, 5, 3, 2, 1][:8]; counts = [1, 2, 3, 5, 5, 3, 2, 1]
    for i, (x, n) in enumerate(zip(xs, counts)):
        x = -0.6 + i * 0.172
        team = (0.78, 0.12, 0.1, 1) if i in (0, 1, 3, 6) else (0.12, 0.28, 0.7, 1)
        m.between((x, -0.43, 1.0), (x, 0.43, 1.0), 0.0075, seg=8, mi=I['steel_charcoal'], rgba=metal)
        sg = 0.64 / (n + 1) if n > 1 else 0
        for j in range(n):
            y = (j - (n - 1) / 2) * (0.5 / max(n - 1, 1) if n > 1 else 0)
            m.rbox(x, y, 0.985, 0.032, 0.05, 0.09, 0.012, mi=I['plastic'], rgba=team)
            m.sphere(x, y, 1.055, 0.027, rings=5, seg=8, mi=I['plastic'], rgba=team)
            m.rbox(x, y, 0.945, 0.03, 0.045, 0.03, 0.01, mi=I['plastic'], rgba=(0.9, 0.9, 0.88, 1))
        for sy in (-1, 1):
            m.cylz(x, sy * 0.46, 0.0 + 0.0, 0.0, 0.0, seg=3) if False else None
        m.lathe([(0.0, 0.0), (0.012, 0.0), (0.014, 0.03), (0.02, 0.06), (0.02, 0.1), (0.0, 0.1)], loc=(0, 0, 0), seg=12, mi=I['plastic'], rgba=(0.06, 0.06, 0.06, 1), rot=(math.pi / 2, 0, 0), scale=(1, 1, 1)) if False else None
        gy = 0.44 if i % 2 == 0 else -0.44
        m.add(p_cyl(0.019, 0.1, 14), (x, gy * 1.12, 1.0), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.05, 0.05, 0.05, 1))
        m.add(p_cyl(0.026, 0.012, 14), (x, gy * 1.0 + (0.03 if gy > 0 else -0.03), 1.0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=metal)
    m.sphere(0.0, 0.1, 0.96, 0.017, rings=8, seg=12, mi=I['plastic'], rgba=(0.95, 0.95, 0.9, 1))
    return m.finish('proto_foosball', P)

def airhockey(F, P):
    m = mb(F); L, W = 2.1, 1.05
    blue = (0.1, 0.22, 0.42, 1)
    m.rbox(0, 0, 0.76, L, W, 0.1, 0.02, mi=I['plastic'], rgba=blue)
    m.rbox(0, 0, 0.815, L - 0.14, W - 0.14, 0.014, 0.004, mi=I['laminate'], rgba=(0.82, 0.85, 0.88, 1))
    for sy in (-1, 1): m.rbox(0, sy * (W / 2 - 0.035), 0.86, L, 0.07, 0.08, 0.025, mi=I['plastic'], rgba=blue)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.035), sy * (W / 4 + 0.07), 0.86, 0.07, W / 2 - 0.14, 0.08, 0.025, mi=I['plastic'], rgba=blue)
        m.rbox(sx * (L / 2 - 0.036), 0, 0.82, 0.08, 0.32, 0.03, 0.006, mi=I['steel_charcoal'], rgba=(0.03, 0.03, 0.03, 1))
        for sy in (-1, 1): m.between((sx * (L / 2 - 0.12), sy * (W / 2 - 0.12), 0.7), (sx * (L / 2 - 0.1), sy * (W / 2 - 0.1), 0.0), 0.04, seg=14, r2=0.03, mi=I['plastic'], rgba=blue)
    m.rbox(0, 0, 0.822, 0.012, W - 0.15, 0.003, 0.0008, mi=I['plastic'], rgba=(0.8, 0.12, 0.1, 1))
    m.add(p_torus(0.16, 0.003, 36, 5), (0, 0, 0.822), (0, 0, 0), (1, 1, 1), I['plastic'], (0.8, 0.12, 0.1, 1))
    for sx, col in ((-1, (0.82, 0.1, 0.1, 1)), (1, (0.1, 0.3, 0.8, 1))):
        m.lathe([(0.0, 0.0), (0.05, 0.0), (0.052, 0.008), (0.04, 0.014), (0.014, 0.02), (0.014, 0.05), (0.02, 0.058), (0.02, 0.07), (0.0, 0.07)], loc=(sx * 0.55, sx * 0.1, 0.826), seg=24, mi=I['plastic'], rgba=col)
    m.cylz(0.1, -0.1, 0.826, 0.832, 0.03, seg=20, mi=I['plastic'], rgba=(0.05, 0.05, 0.05, 1))
    for sx, col in ((-1, (0.9, 0.3, 0.2, 1)), (1, (0.2, 0.5, 0.9, 1))):
        m.rbox(sx * (L / 2 - 0.2), W / 2 - 0.0, 0.62, 0.34, 0.02, 0.1, 0.008, mi=I['screen'], rgba=col) if False else None
    m.rbox(0, -(W / 2 + 0.005), 0.74, 0.55, 0.01, 0.12, 0.004, mi=I['screen'], rgba=(0.9, 0.35, 0.2, 1))
    return m.finish('proto_airhockey', P)

def hoops(F, P):
    """Arcade basketball. Long axis X: shooting end at -X, backboards at +X."""
    m = mb(F); L, W = 2.5, 1.5
    red = (0.55, 0.12, 0.08, 1); dark = (0.1, 0.1, 0.12, 1); org = (0.88, 0.38, 0.1, 1)
    m.rbox(0.0, 0, 0.24, L, W, 0.46, 0.03, mi=I['plastic'], rgba=red)
    m.rbox(0.0, 0, 0.55, L - 0.1, W - 0.12, 0.18, 0.03, mi=I['plastic'], rgba=red)
    m.rbox(0.05, 0, 0.66, L - 0.14, W - 0.3, 0.05, 0.02, mi=I['plastic'], rgba=(0.15, 0.15, 0.18, 1))
    m.rbox(-0.55, 0, 0.7, 0.9, W - 0.34, 0.022, 0.01, mi=I['steel_charcoal'], rgba=(0.18, 0.18, 0.2, 1), rot=(0, -0.14, 0))
    # lane dividers and ball returns
    for sy in (-0.37, 0.37):
        m.rbox(0.0, sy * 0.0 + (sy), 0.75, L - 0.3, 0.04, 0.18, 0.015, mi=I['plastic'], rgba=dark) if False else None
    m.rbox(0.0, 0, 0.78, L - 0.4, 0.05, 0.22, 0.015, mi=I['plastic'], rgba=dark)
    for sy in (-1, 1): m.rbox(0.0, sy * (W / 2 - 0.1), 0.78, L - 0.3, 0.05, 0.26, 0.015, mi=I['plastic'], rgba=dark)
    # back frame and hoops
    for sy in (-1, 1): m.rbox(L / 2 - 0.12, sy * (W / 2 - 0.1), 1.3, 0.08, 0.1, 1.7, 0.02, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(L / 2 - 0.12, 0, 2.2, 0.08, W - 0.1, 0.12, 0.02, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(L / 2 - 0.12, 0, 2.44, 0.06, 0.9, 0.2, 0.01, mi=I['emissive'], rgba=(0.95, 0.3, 0.15, 1))
    for sy in (-0.36, 0.36):
        m.rbox(L / 2 - 0.2, sy, 1.78, 0.03, 0.56, 0.4, 0.012, mi=I['plastic'], rgba=(0.9, 0.9, 0.88, 1))
        m.rbox(L / 2 - 0.22, sy, 1.72, 0.012, 0.18, 0.12, 0.004, mi=I['plastic'], rgba=(0.85, 0.2, 0.15, 1))
        m.add(p_torus(0.115, 0.0075, 28, 6), (L / 2 - 0.35, sy, 1.62), (0, 0, 0), (1, 1, 1), I['steel_accent'], org)
        m.rbox(L / 2 - 0.23, sy, 1.62, 0.12, 0.03, 0.02, 0.006, mi=I['steel_accent'], rgba=org)
        for k in range(14):
            a = k * 2 * math.pi / 14
            m.between((L / 2 - 0.35 + math.cos(a) * 0.113, sy + math.sin(a) * 0.113, 1.615), (L / 2 - 0.35 + math.cos(a) * 0.07, sy + math.sin(a) * 0.07, 1.38), 0.0035, seg=4, mi=I['fabric'], rgba=(0.85, 0.85, 0.82, 1))
    for i in range(4):
        m.sphere(-0.85 + i * 0.16, 0.38 * (1 if i % 2 else -1), 0.82, 0.062, rings=10, seg=16, mi=I['plastic'], rgba=(0.82, 0.36, 0.1, 1))
    m.rbox(-L / 2 + 0.2, 0, 0.9, 0.24, 0.8, 0.012, 0.004, mi=I['screen'], rgba=(0.3, 0.8, 0.4, 1), rot=(0, -0.4, 0))
    return m.finish('proto_hoops', P)

def dartboard(F, P):
    """Dartboard in an open cabinet, wall-mounted at the origin, board facing -Y; three darts in the board."""
    m = mb(F)
    wood = (0.18, 0.1, 0.05, 1)
    m.rbox(0, 0.03, 0, 0.72, 0.1, 0.72, 0.012, mi=I['timber'], rgba=wood)
    m.rbox(0, -0.03, 0, 0.62, 0.04, 0.62, 0.01, mi=I['fabric'], rgba=(0.06, 0.06, 0.07, 1))
    # wedges
    seg = 20; ring_r = [(0.0, 0.012, 'bull_i'), (0.012, 0.03, 'bull'), (0.03, 0.1, 'single'), (0.1, 0.108, 'treble'), (0.108, 0.17, 'single'), (0.17, 0.182, 'double'), (0.182, 0.2, 'rim')]
    cols = {0: ((0.06, 0.06, 0.06, 1), (0.9, 0.85, 0.65, 1)), 1: ((0.1, 0.45, 0.2, 1), (0.8, 0.12, 0.1, 1))}
    for si in range(seg):
        a0 = si * 2 * math.pi / seg - math.pi / seg; a1 = a0 + 2 * math.pi / seg
        for ri, (r0, r1, kind) in enumerate(ring_r):
            if kind == 'bull_i': col = (0.8, 0.12, 0.1, 1)
            elif kind == 'bull': col = (0.1, 0.45, 0.2, 1)
            elif kind == 'rim': col = (0.04, 0.04, 0.04, 1)
            elif kind in ('treble', 'double'): col = cols[1][si % 2]
            else: col = cols[0][si % 2]
            pb = bmesh.new()
            pts = []
            n = 3
            for k in range(n + 1):
                a = a0 + (a1 - a0) * k / n; pts.append((r0 * math.cos(a), r0 * math.sin(a)))
            for k in range(n, -1, -1):
                a = a0 + (a1 - a0) * k / n; pts.append((r1 * math.cos(a), r1 * math.sin(a)))
            if r0 == 0: pts = pts[n:]
            vs = [pb.verts.new(Vector((x, 0.0, z))) for x, z in pts]
            try: f = pb.faces.new(vs)
            except ValueError: pb.free(); continue
            r = bmesh.ops.extrude_face_region(pb, geom=[f])
            for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.y -= 0.014
            bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
            m.add(pb, (0, -0.05, 0), mi=I['plastic'], rgba=col)
    for k, (x, z, tilt) in enumerate(((0.07, 0.09, 0.1), (-0.1, 0.05, -0.15), (0.0, -0.13, 0.05))):
        m.between((x, -0.06, z), (x + tilt * 0.4, -0.2, z + 0.02), 0.0045, seg=8, mi=I['steel_charcoal'], rgba=(0.7, 0.72, 0.74, 1))
        m.between((x + tilt * 0.4, -0.2, z + 0.02), (x + tilt * 0.55, -0.25, z + 0.025), 0.007, seg=8, mi=I['plastic'], rgba=(0.1, 0.1, 0.12, 1))
        m.add(p_leaf(0.04, 0.012, 0, 0, 2), (x + tilt * 0.6, -0.26, z + 0.025), (0, 0, 0), mi=I['plastic'], rgba=(0.85, 0.15, 0.1, 1))
    return m.finish('proto_dartboard', P)

def water_cooler(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.55, 0.34, 0.34, 1.1, 0.03, mi=I['plastic'], rgba=(0.86, 0.86, 0.84, 1))
    m.rbox(0, 0.17, 0.95, 0.24, 0.03, 0.12, 0.01, mi=I['plastic'], rgba=(0.12, 0.14, 0.2, 1))
    for sx, c in ((-0.06, (0.2, 0.4, 0.8, 1)), (0.06, (0.8, 0.2, 0.15, 1))): m.rbox(sx, 0.19, 0.97, 0.04, 0.03, 0.03, 0.008, mi=I['plastic'], rgba=c)
    m.rbox(0, 0.17, 0.72, 0.2, 0.1, 0.01, 0.003, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    m.lathe([(0.0, 1.1), (0.12, 1.1), (0.16, 1.16), (0.17, 1.3), (0.14, 1.42), (0.08, 1.48), (0.06, 1.5), (0.0, 1.5)], seg=28, mi=I['glass'])
    m.lathe([(0.0, 1.12), (0.115, 1.12), (0.155, 1.17), (0.165, 1.3), (0.0, 1.3)], seg=28, mi=I['glass'], rgba=(0.5, 0.7, 0.9, 1)) if False else None
    return m.finish('proto_water_cooler', P)

def fridge_display(F, P, rgba=(0.88, 0.88, 0.86, 1)):
    m = mb(F); rnd = random.Random(6)
    m.rbox(0, 0, 0.95, 0.9, 0.7, 1.9, 0.03, mi=I['plastic'], rgba=rgba)
    m.rbox(0, 0.33, 1.0, 0.76, 0.05, 1.5, 0.01, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    for r in range(4):
        z = 0.5 + r * 0.38; m.rbox(0, 0.15, z, 0.74, 0.5, 0.012, 0.004, mi=I['steel_charcoal'], rgba=(0.6, 0.6, 0.62, 1))
        for c in range(7):
            col = rnd.choice([(0.8, 0.1, 0.08, 1), (0.1, 0.4, 0.8, 1), (0.9, 0.7, 0.1, 1), (0.15, 0.55, 0.3, 1), (0.9, 0.9, 0.88, 1)])
            m.cylz(-0.3 + c * 0.1, 0.28, z + 0.006, z + 0.2, 0.032, seg=10, mi=I['plastic'], rgba=col)
    m.rbox(0, 0.36, 1.0, 0.8, 0.008, 1.5, 0.002, mi=I['glass'])
    m.rbox(0, 0.352, 1.85, 0.78, 0.03, 0.14, 0.01, mi=I['emissive'], rgba=(0.85, 0.95, 1.0, 1))
    m.rbox(0.36, 0.38, 1.0, 0.03, 0.03, 0.4, 0.01, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    for sx in (-1, 1): m.cylz(sx * 0.38, -0.28, 0.0, 0.04, 0.03, seg=8, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_fridge_display', P)

def bookcase(F, P, seed=0):
    m = mb(F); rnd = random.Random(seed); wood = (0.34, 0.2, 0.09, 1)
    W, H, D = 1.2, 2.0, 0.34
    for sx in (-1, 1): m.rbox(sx * W / 2, 0, H / 2, 0.03, D, H, 0.006, mi=I['timber'], rgba=wood)
    for z in (0.02, 0.5, 0.98, 1.46, 1.98): m.rbox(0, 0, z, W, D, 0.03, 0.006, mi=I['timber'], rgba=wood)
    m.rbox(0, -D / 2, H / 2, W, 0.01, H, 0.002, mi=I['timber'], rgba=tuple(c * 0.7 for c in wood[:3]) + (1,))
    cols = [(0.55, 0.14, 0.08, 1), (0.12, 0.2, 0.4, 1), (0.8, 0.62, 0.2, 1), (0.2, 0.3, 0.2, 1), (0.85, 0.82, 0.74, 1), (0.4, 0.25, 0.15, 1)]
    for sh, z in enumerate((0.04, 0.52, 1.0, 1.48)):
        x = -W / 2 + 0.05
        while x < W / 2 - 0.1:
            if sh == 3 and rnd.random() < 0.25: x += 0.2; continue
            w = rnd.uniform(0.025, 0.05); h = rnd.uniform(0.22, 0.4)
            m.rbox(x + w / 2, 0.0, z + h / 2 + 0.015, w, 0.22, h, 0.003, mi=I['plastic'], rgba=rnd.choice(cols)); x += w + 0.003
    return m.finish(f'proto_bookcase_{seed}', P)

def microwave_bench(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.45, 1.6, 0.6, 0.9, 0.02, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    m.rbox(0, 0.0, 0.915, 1.64, 0.64, 0.04, 0.012, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    m.rbox(-0.4, 0.02, 1.08, 0.5, 0.36, 0.28, 0.025, mi=I['plastic'], rgba=(0.82, 0.82, 0.8, 1)); m.rbox(-0.46, 0.2, 1.08, 0.34, 0.012, 0.2, 0.004, mi=I['glass']); m.rbox(-0.2, 0.2, 1.08, 0.08, 0.012, 0.22, 0.004, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.lathe([(0.0, 0.0), (0.07, 0.0), (0.08, 0.04), (0.09, 0.18), (0.05, 0.2), (0.0, 0.2)], loc=(0.35, 0.0, 0.935), seg=20, mi=I['plastic'], rgba=(0.8, 0.8, 0.78, 1))
    m.rbox(0.62, 0.0, 1.08, 0.26, 0.3, 0.28, 0.03, mi=I['plastic'], rgba=(0.12, 0.13, 0.15, 1))
    for k in range(3): m.rbox(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) if False else None
    m.rbox(-0.1, 0.31, 0.5, 1.2, 0.012, 0.6, 0.004, mi=I['steel_charcoal'], rgba=(0.16, 0.17, 0.3, 1))
    return m.finish('proto_microwave_bench', P)

def table_set(F, P):
    """Tabletop clutter: napkin dispenser, salt and pepper, sugar caddy, a menu card."""
    m = mb(F)
    m.rbox(0, 0, 0.07, 0.1, 0.07, 0.14, 0.012, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1)); m.rbox(0, 0.036, 0.075, 0.07, 0.004, 0.1, 0.001, mi=I['signage'], rgba=(0.92, 0.9, 0.86, 1))
    for x in (0.1, 0.15): m.lathe([(0.0, 0.0), (0.018, 0.0), (0.02, 0.05), (0.016, 0.08), (0.0, 0.085)], loc=(x, 0.0, 0.0), seg=12, mi=I['glass'])
    m.rbox(-0.12, 0.0, 0.04, 0.09, 0.06, 0.08, 0.01, mi=I['plastic'], rgba=(0.8, 0.8, 0.78, 1))
    m.rbox(0.0, 0.1, 0.075, 0.1, 0.012, 0.15, 0.003, rot=(-0.15, 0, 0), mi=I['signage'], rgba=(0.88, 0.82, 0.62, 1))
    return m.finish('proto_table_set', P)

def coat_rack(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.22, 0.0), (0.22, 0.02), (0.1, 0.05), (0.03, 0.08)], seg=20, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.cylz(0, 0, 0.05, 1.75, 0.022, seg=10, mi=I['timber'], rgba=(0.3, 0.17, 0.08, 1))
    for k in range(6):
        a = k * math.pi / 3; m.between((0, 0, 1.68), (math.cos(a) * 0.22, math.sin(a) * 0.22, 1.82), 0.01, seg=6, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for k, a in enumerate((0.0, 2.1)): m.cushion(math.cos(a) * 0.2, math.sin(a) * 0.2, 1.4, 0.12, 0.2, 0.55, r=0.03, mi=I['fabric'], rgba=[(0.7, 0.3, 0.1, 1), (0.15, 0.2, 0.4, 1)][k])
    return m.finish('proto_coat_rack', P)

def wet_floor_sign(F, P):
    m = mb(F)
    for s in (-1, 1): m.rbox(0, s * 0.11, 0.3, 0.28, 0.012, 0.6, 0.006, rot=(s * -0.28, 0, 0), mi=I['plastic'], rgba=(0.92, 0.75, 0.05, 1)); m.rbox(0, s * 0.125, 0.33, 0.2, 0.004, 0.2, 0.002, rot=(s * -0.28, 0, 0), mi=I['signage'], rgba=(0.1, 0.1, 0.1, 1))
    return m.finish('proto_wet_floor_sign', P)

def mop_bucket(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.2, 0.42, 0.3, 0.38, 0.04, mi=I['plastic'], rgba=(0.85, 0.7, 0.05, 1)); m.rbox(0, 0, 0.385, 0.34, 0.22, 0.01, 0.004, mi=I['glass'])
    for sx in (-1, 1): m.cylz(sx * 0.17, 0, -0.0, 0.05, 0.03, seg=10, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    m.between((0.1, -0.05, 0.4), (0.38, -0.1, 1.1), 0.014, seg=8, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    return m.finish('proto_mop_bucket', P)

def wall_shelf(F, P, seed=0):
    m = mb(F); rnd = random.Random(seed)
    m.rbox(0, 0.1, 0, 1.2, 0.2, 0.035, 0.008, mi=I['timber'], rgba=(0.34, 0.2, 0.09, 1))
    for sx in (-0.45, 0.45): m.rbox(sx, 0.02, -0.09, 0.03, 0.04, 0.2, 0.006, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1)); m.rbox(sx, 0.1, -0.03, 0.03, 0.17, 0.03, 0.006, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    for k, x in enumerate((-0.4, 0.05, 0.4)):
        m.lathe([(0.0, 0.0), (0.05, 0.0), (0.06, 0.1), (0.065, 0.11), (0.0, 0.11)], loc=(x, 0.1, 0.018), seg=14, mi=I['props'], rgba=[(0.7, 0.35, 0.2, 1), (0.14, 0.15, 0.25, 1), (0.8, 0.7, 0.5, 1)][k])
        for i in range(14): m.leaf((x, 0.1, 0.12), rnd.uniform(0.1, 0.18), 0.03, bend=0.3, yaw=rnd.uniform(0, 6.28), pitch=rnd.uniform(0.4, 1.2), segs=3, mi=I['foliage'], rgba=(0.12, 0.32, 0.1, 1))
    return m.finish(f'proto_wall_shelf_{seed}', P)
