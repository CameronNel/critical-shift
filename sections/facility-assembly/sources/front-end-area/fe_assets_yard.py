"""Yard assets at spawn-room quality: crates, pallets, drums, tyres, cones, bollards, benches, planters, poles, rail kit."""
from fe_kit import *
from fe_assets_int import STD, I, mb

def crate(F, P, variant=0):
    cols = [(0.50, 0.36, 0.20, 1), (0.28, 0.36, 0.30, 1), (0.62, 0.50, 0.28, 1), (0.22, 0.28, 0.36, 1)]; c = cols[variant % 4]
    m = mb(F); rnd = random.Random(variant)
    S = 0.96
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * 0.45, sy * 0.45, 0.5, 0.09, 0.09, 1.0, 0.008, mi=I['timber'], rgba=tuple(x * 0.85 for x in c[:3]) + (1,))
    for z in (0.04, 0.5, 0.96):
        m.rbox(0, 0.45, z, 0.9, 0.09, 0.08, 0.006, mi=I['timber'], rgba=tuple(x * 0.85 for x in c[:3]) + (1,)); m.rbox(0, -0.45, z, 0.9, 0.09, 0.08, 0.006, mi=I['timber'], rgba=tuple(x * 0.85 for x in c[:3]) + (1,))
        m.rbox(0.45, 0, z, 0.09, 0.9, 0.08, 0.006, mi=I['timber'], rgba=tuple(x * 0.85 for x in c[:3]) + (1,)); m.rbox(-0.45, 0, z, 0.09, 0.9, 0.08, 0.006, mi=I['timber'], rgba=tuple(x * 0.85 for x in c[:3]) + (1,))
    n = 6
    for i in range(n):
        z = 0.1 + i * 0.145
        for sx in (-1, 1): m.rbox(sx * 0.452, 0, z + 0.06, 0.03, 0.82, 0.13, 0.004, mi=I['timber'], rgba=tuple(x * (0.92 + 0.08 * rnd.random()) for x in c[:3]) + (1,))
        for sy in (-1, 1): m.rbox(0, sy * 0.452, z + 0.06, 0.82, 0.03, 0.13, 0.004, mi=I['timber'], rgba=tuple(x * (0.92 + 0.08 * rnd.random()) for x in c[:3]) + (1,))
    m.rbox(0, 0, 0.5, 0.88, 0.88, 0.88, 0.0, mi=I['timber'], rgba=(0.1, 0.07, 0.04, 1))
    m.rbox(0, 0, 0.995, 0.96, 0.96, 0.024, 0.006, mi=I['timber'], rgba=c)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for z in (0.12, 0.88): m.cylz(sx * 0.462, sy * 0.462, z - 0.005, z + 0.005, 0.012, seg=8, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.5, 1)) if False else None
    m.rbox(0, 0.485, 0.62, 0.34, 0.012, 0.2, 0.004, mi=I['signage'], rgba=(0.88, 0.86, 0.8, 1))
    m.rbox(0, 0.492, 0.62, 0.22, 0.006, 0.03, 0.002, mi=I['signage'], rgba=(0.1, 0.1, 0.1, 1))
    return m.finish(f'proto_crate_{variant}', P)

def pallet(F, P):
    m = mb(F); w = (0.55, 0.38, 0.2, 1)
    for x in (-0.5, 0.0, 0.5):
        m.rbox(x, 0, 0.075, 0.1, 1.0, 0.09, 0.006, mi=I['timber'], rgba=w)
    for i in range(7): m.rbox(0, -0.46 + i * 0.153, 0.16, 1.2, 0.1, 0.022, 0.004, mi=I['timber'], rgba=tuple(c * (0.9 + 0.1 * ((i * 7) % 3) / 2) for c in w[:3]) + (1,))
    for sy in (-1, 1):
        for sx in (-1, 1): m.rbox(sx * 0.55, sy * 0.45, 0.012, 0.1, 0.1, 0.024, 0.004, mi=I['timber'], rgba=w) if False else None
    for y in (-0.45, 0.0, 0.45): m.rbox(0, y, 0.012, 1.2, 0.1, 0.022, 0.004, mi=I['timber'], rgba=w)
    return m.finish('proto_pallet', P)

def barrel(F, P, rgba=(0.12, 0.3, 0.45, 1), name='barrel'):
    m = mb(F)
    prof = [(0.0, 0.0), (0.27, 0.0), (0.285, 0.015), (0.29, 0.05), (0.285, 0.08), (0.292, 0.09), (0.292, 0.12), (0.285, 0.13), (0.29, 0.28), (0.29, 0.45), (0.292, 0.46), (0.292, 0.49), (0.285, 0.5),
            (0.29, 0.64), (0.285, 0.8), (0.292, 0.81), (0.292, 0.84), (0.285, 0.85), (0.29, 0.88), (0.288, 0.9), (0.27, 0.905), (0.265, 0.9), (0.26, 0.89), (0.0, 0.89)]
    m.lathe(prof, seg=32, mi=I['props'], rgba=rgba)
    m.cylz(0.12, 0.1, 0.9, 0.925, 0.03, seg=14, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1)); m.cylz(-0.12, -0.08, 0.9, 0.915, 0.022, seg=14, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    m.add(p_torus(0.275, 0.007, 36, 6), (0, 0, 0.885), (0, 0, 0), mi=I['steel_charcoal'], rgba=(0.45, 0.45, 0.47, 1))
    return m.finish('proto_' + name, P)

def cable_drum(F, P):
    m = mb(F)
    for z in (0.0, 0.62): m.cylz(0, 0, z, z + 0.05, 0.5, seg=40, bevel=0.01, mi=I['timber'], rgba=(0.5, 0.34, 0.18, 1))
    m.cylz(0, 0, 0.05, 0.62, 0.12, seg=24, mi=I['timber'], rgba=(0.4, 0.27, 0.14, 1))
    for r in range(8):
        m.add(p_torus(0.27, 0.03, 24, 6), (0, 0, 0.09 + r * 0.063), (0, 0, 0), mi=I['plastic'], rgba=(0.06, 0.06, 0.07, 1))
    for k in range(6):
        a = k * math.pi / 3
        for z in (0.052, 0.62): m.cylz(math.cos(a) * 0.38, math.sin(a) * 0.38, z - 0.002, z + 0.008, 0.02, seg=10, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.5, 1)) if False else None
    m.rbox(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0) if False else None
    return m.finish('proto_cable_drum', P)

def tyre(F, P, stack=1, name='tyre'):
    m = mb(F)
    prof = [(0.17, 0.0), (0.235, 0.0), (0.29, 0.015), (0.32, 0.06), (0.325, 0.12), (0.32, 0.18), (0.29, 0.225), (0.235, 0.24), (0.17, 0.24), (0.165, 0.2), (0.165, 0.04)]
    for k in range(stack):
        m.lathe(prof, loc=(0, 0, k * 0.235), seg=28, mi=I['rubber'], rgba=(0.035, 0.035, 0.038, 1), close=False)
    return m.finish('proto_' + name, P)

def cone(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.012, 0.42, 0.42, 0.024, 0.01, mi=I['rubber'], rgba=(0.06, 0.06, 0.06, 1))
    m.lathe([(0.15, 0.024), (0.12, 0.2), (0.09, 0.4), (0.04, 0.68), (0.032, 0.7), (0.0, 0.7)], seg=28, mi=I['plastic'], rgba=(0.9, 0.35, 0.08, 1))
    m.lathe([(0.108, 0.24), (0.1, 0.32), (0.083, 0.32), (0.091, 0.24)], seg=28, mi=I['plastic'], rgba=(0.92, 0.92, 0.9, 1))
    m.lathe([(0.075, 0.43), (0.07, 0.5), (0.057, 0.5), (0.061, 0.43)], seg=28, mi=I['plastic'], rgba=(0.92, 0.92, 0.9, 1))
    return m.finish('proto_cone', P)

def bollard(F, P):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.12, 0.0), (0.12, 0.03), (0.09, 0.05), (0.085, 0.9), (0.09, 0.92), (0.075, 0.98), (0.0, 1.0)], seg=24, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.16, 1))
    m.lathe([(0.0861, 0.5), (0.0862, 0.7), (0.0862, 0.7), (0.0861, 0.5)], seg=24) if False else None
    m.cylz(0, 0, 0.55, 0.72, 0.0885, seg=24, mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1))
    return m.finish('proto_bollard', P)

def bench(F, P):
    m = mb(F)
    wood = (0.45, 0.27, 0.12, 1); steel = (0.1, 0.1, 0.12, 1)
    for i in range(4): m.rbox(0, -0.2 + i * 0.12, 0.45, 1.8, 0.1, 0.035, 0.01, mi=I['timber'], rgba=wood)
    for i in range(3): m.rbox(0, -0.24, 0.66 + i * 0.13, 1.8, 0.03, 0.1, 0.01, rot=(-0.18, 0, 0), mi=I['timber'], rgba=wood)
    for sx in (-1, 1):
        x = sx * 0.78
        m.rbox(x, -0.02, 0.2, 0.06, 0.06, 0.4, 0.01, mi=I['steel_charcoal'], rgba=steel)
        m.rbox(x, 0.0, 0.43, 0.06, 0.52, 0.04, 0.01, mi=I['steel_charcoal'], rgba=steel)
        m.rbox(x, -0.26, 0.62, 0.06, 0.04, 0.38, 0.01, rot=(-0.18, 0, 0), mi=I['steel_charcoal'], rgba=steel)
        m.rbox(x, -0.02, 0.012, 0.08, 0.5, 0.024, 0.008, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_bench', P)

def planter(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.3, 1.2, 1.2, 0.6, 0.03, mi=I['concrete_slab'])
    m.rbox(0, 0, 0.605, 1.1, 1.1, 0.02, 0.008, mi=I['concrete_slab'])
    m.cylz(0, 0, 0.5, 0.62, 0.0, seg=3) if False else None
    for k in range(5): m.rbox(0, 0.605, 0.3 + (k - 2) * 0.025, 0.4, 0.012, 0.012, 0.003, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(0, 0, 0.58, 1.02, 1.02, 0.05, 0.008, mi=I['props'], rgba=(0.12, 0.08, 0.05, 1))
    return m.finish('proto_planter', P)

def light_pole(F, P):
    m = mb(F); d = (0.12, 0.12, 0.14, 1)
    m.lathe([(0.0, 0.0), (0.16, 0.0), (0.16, 0.03), (0.1, 0.08), (0.075, 0.5), (0.06, 4.6), (0.0, 4.6)], seg=20, mi=I['steel_charcoal'], rgba=d)
    m.between((0, 0, 4.55), (0.35, 0, 4.82), 0.045, seg=12, mi=I['steel_charcoal'], rgba=d)
    m.between((0.35, 0, 4.82), (0.88, 0, 4.82), 0.04, seg=12, mi=I['steel_charcoal'], rgba=d)
    m.rbox(1.05, 0, 4.8, 0.52, 0.22, 0.09, 0.03, mi=I['steel_charcoal'], rgba=d)
    m.rbox(1.05, 0, 4.74, 0.46, 0.17, 0.02, 0.006, mi=I['emissive'], rgba=(1.0, 0.92, 0.75, 1))
    m.rbox(0.0, 0.09, 1.2, 0.16, 0.025, 0.4, 0.008, mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))
    return m.finish('proto_light_pole', P)

def _wave_panel(L, H, depth=0.04, pitch=0.2):
    """Corrugated sheet profile extruded along z: zig-zag polygon in (x, y)."""
    pts = []; n = int(L / pitch); 
    for i in range(n):
        x0 = -L / 2 + i * pitch
        pts += [(x0, 0.0), (x0 + pitch * 0.25, depth), (x0 + pitch * 0.5, depth), (x0 + pitch * 0.75, 0.0)]
    pts.append((L / 2, 0.0))
    back = [(x, -0.012) for x, _ in reversed(pts)]
    return p_ring_prism(pts + back, H)

def container(F, P, rgba=(0.45, 0.12, 0.08, 1), name='container', L=6.0):
    m = mb(F); W, H = 2.44, 2.59
    steel = (0.12, 0.12, 0.13, 1)
    for sy in (-1, 1):
        pb = _wave_panel(L - 0.2, H - 0.2); xf(pb, (0, sy * (W / 2 - 0.04), 0.1), (0, 0, 0 if sy > 0 else math.pi)); m.add(pb, mi=I['props'], rgba=rgba)
    m.rbox(0, 0, H - 0.04, L, W, 0.07, 0.012, mi=I['props'], rgba=tuple(c * 0.9 for c in rgba[:3]) + (1,))
    m.rbox(0, 0, 0.14, L - 0.1, W - 0.12, 0.1, 0.01, mi=I['steel_charcoal'], rgba=steel)
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.08), sy * (W / 2 - 0.08), H / 2, 0.16, 0.16, H, 0.012, mi=I['steel_charcoal'], rgba=steel)
        for sy in (-1, 1): m.rbox(sx * (L / 2 - 0.08), sy * (W / 2 - 0.08), H - 0.08, 0.2, 0.2, 0.16, 0.014, mi=I['steel_charcoal'], rgba=(0.3, 0.3, 0.32, 1))
        # door end: two leaves with vertical lock bars
        x = sx * (L / 2 - 0.02)
        for k, sy in enumerate((-1, 1)):
            m.rbox(x, sy * 0.58, H / 2, 0.05, 1.04, H - 0.28, 0.01, mi=I['props'], rgba=tuple(c * 0.85 for c in rgba[:3]) + (1,))
            for r in range(6): m.rbox(x + sx * 0.03, sy * 0.58, 0.28 + r * 0.4, 0.02, 0.92, 0.05, 0.006, mi=I['props'], rgba=tuple(c * 0.7 for c in rgba[:3]) + (1,))
            for yy in (0.2, 0.34) if sy > 0 else (-0.2, -0.34):
                m.cylz(x + sx * 0.07, yy * 1.0 + (0.0), 0.32, H - 0.32, 0.016, seg=10, mi=I['steel_charcoal'], rgba=(0.55, 0.56, 0.58, 1))
                for z in (0.34, 1.28, 2.2): m.rbox(x + sx * 0.08, yy, z, 0.04, 0.08, 0.08, 0.008, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
            m.rbox(x + sx * 0.08, sy * 0.1, 1.15, 0.03, 0.04, 0.18, 0.01, mi=I['steel_charcoal'], rgba=(0.55, 0.56, 0.58, 1))
        m.rbox(x + sx * 0.03, 0.0, H / 2, 0.02, 0.012, H - 0.28, 0.003, mi=I['steel_charcoal'], rgba=(0.02, 0.02, 0.02, 1))
        m.rbox(x + sx * 0.04, 0.0, H - 0.16, 0.05, W - 0.3, 0.08, 0.01, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_' + name, P)

def skip_bin(F, P, rgba=(0.62, 0.32, 0.06, 1)):
    m = mb(F); L, W = 3.4, 1.7
    prof = lambda sx: None
    for sy in (-1, 1):
        m.rbox(0, sy * 0.78, 0.55, L, 0.06, 1.0, 0.01, rot=(sy * 0.16, 0, 0), mi=I['props'], rgba=rgba)
        m.rbox(0, sy * 0.88, 1.06, L + 0.1, 0.1, 0.1, 0.03, mi=I['props'], rgba=tuple(c * 0.8 for c in rgba[:3]) + (1,))
    for sx in (-1, 1): m.rbox(sx * 1.66, 0, 0.55, 0.06, 1.5, 1.0, 0.01, rot=(0, sx * 0.1, 0), mi=I['props'], rgba=rgba)
    m.rbox(0, 0, 0.1, L - 0.1, 1.4, 0.06, 0.01, mi=I['props'], rgba=tuple(c * 0.7 for c in rgba[:3]) + (1,))
    for k in range(7):
        x = -1.4 + k * 0.467
        for sy in (-1, 1): m.rbox(x, sy * 0.8, 0.55, 0.07, 0.05, 0.9, 0.008, rot=(sy * 0.16, 0, 0), mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for sx in (-1, 1):
        m.rbox(sx * 1.2, 0, 0.05, 0.14, 1.7, 0.1, 0.02, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
        m.between((sx * 1.62, -0.88, 1.0), (sx * 1.62, -0.7, 0.6), 0.03, seg=8, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
        m.add(p_cyl(0.07, 0.1, 12), (sx * 1.62, -0.92, 1.0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(0, -0.86, 0.6, 1.0, 0.012, 0.22, 0.004, mi=I['signage'], rgba=(0.92, 0.9, 0.8, 1), rot=(-0.16, 0, 0))
    return m.finish('proto_skip', P)

def i_beam(L, h=0.2, w=0.1, tw=0.012, tf=0.02):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, -h / 2 + tf), (tw / 2, -h / 2 + tf), (tw / 2, h / 2 - tf), (w / 2, h / 2 - tf), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, h / 2 - tf), (-tw / 2, h / 2 - tf), (-tw / 2, -h / 2 + tf), (-w / 2, -h / 2 + tf)]
    pb = p_ring_prism(pts, L); xf(pb, (0, 0, -L / 2), (0, 0, 0)); return pb

def steel_stock(F, P, seed=1):
    """Stacked I-beams, pipes and plate: tidy salvage stock."""
    m = mb(F); rnd = random.Random(seed); rust = [(0.32, 0.17, 0.09, 1), (0.25, 0.14, 0.09, 1), (0.4, 0.22, 0.1, 1)]
    for row in range(3):
        for k in range(4 - row):
            y = (k - (3 - row) / 2) * 0.24; c = rnd.choice(rust)
            m.add(i_beam(3.6 - 0.05 * k, 0.2, 0.1), (0, y, 0.12 + row * 0.2), (0, math.pi / 2, 0), mi=I['props'], rgba=c)
    for k in range(5): m.rbox(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) if False else m.rbox(-1.2 + k * 1.2, 0, 0.04, 0.1, 1.2, 0.08, 0.01, mi=I['timber'], rgba=(0.35, 0.22, 0.1, 1))
    return m.finish(f'proto_steel_stock_{seed}', P)

def pipe_stack(F, P, seed=1):
    m = mb(F); rnd = random.Random(seed); cols = [(0.35, 0.17, 0.09, 1), (0.22, 0.24, 0.27, 1), (0.5, 0.42, 0.2, 1)]
    for r in range(3):
        for c in range(4 - r):
            col = rnd.choice(cols); L = 3.6 + rnd.uniform(-0.3, 0.2)
            x = (c - (3 - r) / 2) * 0.33; z = 0.17 + r * 0.29
            m.add(p_cyl(0.155, L, 22), (0.0, x, z), (0, math.pi / 2, 0), mi=I['props'], rgba=col)
            m.add(p_cyl(0.125, L + 0.01, 22), (0.0, x, z), (0, math.pi / 2, 0), mi=I['props'], rgba=(0.04, 0.035, 0.03, 1))
    for sx in (-1.2, 0.0, 1.2): m.rbox(sx, 0, 0.02, 0.1, 1.5, 0.04, 0.008, mi=I['timber'], rgba=(0.35, 0.22, 0.1, 1))
    return m.finish(f'proto_pipe_stack_{seed}', P)

def bale(F, P, seed=0):
    """Compressed scrap bale, strapped."""
    m = mb(F); rnd = random.Random(seed)
    base = [(0.3, 0.17, 0.09, 1), (0.22, 0.2, 0.18, 1), (0.34, 0.25, 0.13, 1)][seed % 3]
    m.rbox(0, 0, 0.45, 1.3, 1.0, 0.9, 0.04, mi=I['props'], rgba=base)
    for i in range(36):
        x = rnd.uniform(-0.62, 0.62); y = rnd.uniform(-0.47, 0.47); z = rnd.uniform(0.05, 0.86); face = rnd.choice(('x', 'y', 'z'))
        k_ = rnd.uniform(0.6, 1.4); c = tuple(min(1, max(0, v * k_)) for v in base[:3]) + (1,)
        if face == 'z': m.rbox(x, y, 0.905, rnd.uniform(0.2, 0.5), rnd.uniform(0.15, 0.4), 0.02, 0.004, rot=(0, 0, rnd.uniform(0, 3)), mi=I['props'], rgba=c)
        elif face == 'y': m.rbox(x, (0.505 if rnd.random() > 0.5 else -0.505), z, rnd.uniform(0.2, 0.5), 0.02, rnd.uniform(0.1, 0.3), 0.004, rot=(0, rnd.uniform(-0.3, 0.3), 0), mi=I['props'], rgba=c)
        else: m.rbox((0.655 if rnd.random() > 0.5 else -0.655), y, z, 0.02, rnd.uniform(0.2, 0.5), rnd.uniform(0.1, 0.3), 0.004, rot=(rnd.uniform(-0.3, 0.3), 0, 0), mi=I['props'], rgba=c)
    for x in (-0.4, 0.0, 0.4):
        m.rbox(x, 0, 0.92, 0.035, 1.04, 0.012, 0.003, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.1, 1))
        for sy in (-1, 1): m.rbox(x, sy * 0.51, 0.45, 0.035, 0.012, 0.92, 0.003, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.1, 1))
    return m.finish(f'proto_bale_{seed}', P)

def generator(F, P):
    m = mb(F); body = (0.7, 0.35, 0.06, 1)
    m.rbox(0, 0, 0.86, 2.6, 1.3, 1.3, 0.05, mi=I['props'], rgba=body)
    m.rbox(0, 0, 0.12, 2.8, 1.5, 0.16, 0.03, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    for k in range(14): m.rbox(-0.9 + k * 0.14, 0.655, 0.9, 0.06, 0.02, 0.8, 0.004, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(-0.9 + 0.98 + 0.0, 0.66, 0.9, 1.96, 0.012, 0.86, 0.004, mi=I['steel_charcoal'], rgba=(0.03, 0.03, 0.03, 1))
    m.rbox(1.0, 0.66, 1.1, 0.4, 0.04, 0.38, 0.01, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1)); m.rbox(1.0, 0.685, 1.15, 0.3, 0.01, 0.16, 0.004, mi=I['screen'], rgba=(0.3, 0.8, 0.45, 1))
    for k in range(3): m.cylz(0.9 + k * 0.1, 0.69, 0.0, 0.0, 0.0) if False else m.add(p_cyl(0.025, 0.03, 12), (0.9 + k * 0.1, 0.695, 0.95), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=[(0.1, 0.7, 0.2, 1), (0.9, 0.7, 0.1, 1), (0.85, 0.15, 0.1, 1)][k])
    m.cylz(1.05, -0.4, 1.5, 2.5, 0.08, seg=18, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1)); m.cylz(1.05, -0.4, 2.5, 2.54, 0.14, seg=18, bevel=0.01, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.rbox(-1.0, -0.2, 1.55, 0.3, 0.3, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    for sx in (-1, 1): m.cylz(sx * 1.2, 0.5, 0.0, 0.0, 0.0) if False else m.add(p_cyl(0.18, 0.1, 20), (sx * 1.0, 0.62, 0.18), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_generator', P)

def tank_vertical(F, P, h=2.6, r=1.05, rgba=(0.5, 0.52, 0.5, 1), name='tank'):
    m = mb(F)
    m.lathe([(0.0, 0.3), (r * 0.95, 0.3), (r, 0.36), (r, h), (r * 0.95, h + 0.08), (r * 0.6, h + 0.18), (r * 0.5, h + 0.2), (0.0, h + 0.2)], seg=48, mi=I['props'], rgba=rgba)
    for k in range(6):
        a = k * math.pi / 3 + 0.2
        m.rbox(math.cos(a) * r * 0.82, math.sin(a) * r * 0.82, 0.15, 0.14, 0.14, 0.3, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for z in (0.7, 1.5, 2.2):
        if z < h: m.add(p_torus(r + 0.006, 0.02, 48, 6), (0, 0, z), (0, 0, 0), mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for k in range(int((h - 0.4) / 0.3)): m.rbox(r + 0.07, 0.0, 0.5 + k * 0.3, 0.05, 0.42, 0.035, 0.008, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for sy in (-0.22, 0.22): m.rbox(r + 0.07, sy, h / 2 + 0.2, 0.05, 0.03, h - 0.3, 0.008, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    m.cylz(0.0, 0.0, h + 0.2, h + 0.5, 0.06, seg=14, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.between((r * 0.5, 0, 0.6), (r + 0.4, 0, 0.6), 0.06, seg=14, mi=I['steel_charcoal'], rgba=(0.55, 0.56, 0.58, 1))
    return m.finish('proto_' + name, P)

def wheel(m, x, y, z, r=0.36, w=0.26, flip=1):
    """Wheel with tyre, rim, hub and lug nuts; axis along Y."""
    prof = [(r * 0.55, -w / 2), (r * 0.85, -w / 2), (r * 0.97, -w * 0.36), (r, -w * 0.15), (r, w * 0.15), (r * 0.97, w * 0.36), (r * 0.85, w / 2), (r * 0.55, w / 2)]
    pb = p_lathe(prof, 36); xf(pb, (x, y, z), (math.pi / 2, 0, 0)); m.add(pb, mi=I['rubber'], rgba=(0.035, 0.035, 0.038, 1))
    pb = p_lathe([(0.0, w * 0.5), (r * 0.5, w * 0.5), (r * 0.56, w * 0.42), (r * 0.56, -w * 0.3), (0.0, -w * 0.3)], 28); xf(pb, (x, y, z), (math.pi / 2, 0, 0)); m.add(pb, mi=I['steel_charcoal'], rgba=(0.55, 0.57, 0.6, 1))
    for k in range(5):
        a = k * 2 * math.pi / 5; m.add(p_cyl(0.018, 0.03, 8), (x + math.cos(a) * r * 0.26, y + flip * w * 0.5, z + math.sin(a) * r * 0.26), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))
    m.add(p_cyl(r * 0.12, 0.04, 16), (x, y + flip * w * 0.52, z), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.25, 0.25, 0.27, 1))

def pickup(F, P, rgba=(0.82, 0.62, 0.08, 1), name='pickup', stripped=False):
    m = mb(F); L, W = 5.2, 1.95; paint = rgba; dark = (0.07, 0.07, 0.08, 1); cx = 0.0
    m.rbox(0, 0, 0.62, L - 0.2, W - 0.1, 0.6, 0.07, mi=I['props'], rgba=paint)                      # lower body
    m.rbox(L / 2 - 0.85, 0, 0.98, 1.5, W - 0.14, 0.14, 0.05, rot=(0, 0.05, 0), mi=I['props'], rgba=paint)   # bonnet
    m.rbox(0.4, 0, 1.45, 1.75, W - 0.18, 0.9, 0.12, mi=I['props'], rgba=paint)                       # cab
    m.rbox(0.4, 0, 1.92, 1.6, W - 0.28, 0.06, 0.03, mi=I['props'], rgba=tuple(c * 0.92 for c in paint[:3]) + (1,))
    for sy in (-1, 1):
        m.rbox(0.45, sy * (W / 2 - 0.1), 1.52, 1.3, 0.02, 0.52, 0.04, mi=I['glass'])                  # side glass
        m.rbox(0.45, sy * (W / 2 - 0.095), 1.52, 1.34, 0.01, 0.56, 0.02, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
        m.rbox(0.45, sy * (W / 2 - 0.1), 1.4, 0.02, 0.025, 0.9, 0.006, mi=I['steel_charcoal'], rgba=dark)
        m.rbox(1.0, sy * (W / 2 + 0.06), 1.62, 0.08, 0.14, 0.18, 0.03, mi=I['plastic'], rgba=dark)                  # mirror
        m.rbox(1.25, sy * (W / 2 - 0.06), 0.8, 0.9, 0.012, 0.012, 0.004, mi=I['steel_charcoal'], rgba=dark)
        m.rbox(0.9, sy * (W / 2 - 0.05), 1.1, 0.14, 0.03, 0.02, 0.008, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))      # door handle
    m.rbox(1.26, 0, 1.55, 0.02, W - 0.34, 0.5, 0.03, rot=(0, -0.28, 0), mi=I['glass'])              # windscreen
    m.rbox(-0.5, 0, 1.55, 0.02, W - 0.4, 0.4, 0.03, mi=I['glass'])
    if not stripped:
        for sy in (-1, 1): m.rbox(0.0, sy * 0.1, 0.0, 0.0, 0.0, 0.0, 0.0) if False else None
    # bed
    m.rbox(-1.55, 0, 0.98, 2.0, W - 0.14, 0.06, 0.02, mi=I['steel_charcoal'], rgba=dark)
    for sy in (-1, 1): m.rbox(-1.55, sy * (W / 2 - 0.08), 1.2, 2.04, 0.06, 0.44, 0.02, mi=I['props'], rgba=paint)
    m.rbox(-2.57, 0, 1.2, 0.06, W - 0.1, 0.44, 0.02, mi=I['props'], rgba=paint)
    m.rbox(-0.56, 0, 1.2, 0.06, W - 0.1, 0.44, 0.02, mi=I['props'], rgba=paint)
    # front end: grille, headlights, bumpers
    m.rbox(L / 2 - 0.1, 0, 0.62, 0.06, W - 0.4, 0.34, 0.02, mi=I['steel_charcoal'], rgba=dark)
    for k in range(6): m.rbox(L / 2 - 0.05, 0, 0.5 + k * 0.05, 0.02, W - 0.5, 0.012, 0.003, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    for sy in (-1, 1):
        m.rbox(L / 2 - 0.08, sy * 0.72, 0.78, 0.06, 0.26, 0.14, 0.03, mi=I['emissive'] if False else I['plastic'], rgba=(0.88, 0.88, 0.8, 1))
        m.rbox(-L / 2 + 0.07, sy * 0.72, 0.84, 0.05, 0.18, 0.1, 0.02, mi=I['plastic'], rgba=(0.75, 0.1, 0.08, 1))
    m.rbox(L / 2 + 0.02, 0, 0.36, 0.16, W, 0.18, 0.05, mi=I['steel_charcoal'], rgba=(0.45, 0.46, 0.48, 1))
    m.rbox(-L / 2 - 0.02, 0, 0.36, 0.16, W, 0.18, 0.05, mi=I['steel_charcoal'], rgba=(0.45, 0.46, 0.48, 1))
    for sy in (-1, 1):
        for x in (L / 2 - 1.1, -L / 2 + 1.1):
            wheel(m, x, sy * (W / 2 - 0.12), 0.37, flip=sy)
            m.add(p_torus(0.43, 0.035, 28, 6), (x, sy * (W / 2 - 0.07), 0.37), (math.pi / 2, 0, 0), mi=I['props'], rgba=tuple(c * 0.8 for c in paint[:3]) + (1,))
    m.rbox(0.4, 0, 1.0, 1.7, 1.7, 0.02, 0.005, mi=I['rubber'], rgba=(0.05, 0.05, 0.05, 1))
    m.rbox(0.15, 0.45, 1.22, 0.45, 0.25, 0.05, 0.02, mi=I['plastic'], rgba=(0.12, 0.12, 0.13, 1)) if False else None
    return m.finish('proto_' + name, P)

def van(F, P, rgba=(0.9, 0.9, 0.88, 1), name='van'):
    m = mb(F); L, W = 5.3, 2.0; paint = rgba; dark = (0.07, 0.07, 0.08, 1)
    m.rbox(0, 0, 1.1, L - 0.2, W - 0.1, 1.55, 0.14, mi=I['props'], rgba=paint)
    m.rbox(L / 2 - 0.6, 0, 0.95, 1.1, W - 0.14, 0.8, 0.12, rot=(0, 0.0, 0), mi=I['props'], rgba=paint)
    m.rbox(0.0, 0, 0.28, L - 0.1, W - 0.2, 0.2, 0.04, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(L / 2 - 1.3, 0, 1.55, 0.02, W - 0.4, 0.7, 0.03, rot=(0, -0.55, 0), mi=I['glass'])
    for sy in (-1, 1):
        m.rbox(L / 2 - 1.7, sy * (W / 2 - 0.06), 1.45, 1.05, 0.02, 0.55, 0.05, mi=I['glass'])
        m.rbox(L / 2 - 1.7, sy * (W / 2 - 0.055), 1.45, 1.09, 0.01, 0.59, 0.02, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
        m.rbox(L / 2 - 1.2, sy * (W / 2 + 0.08), 1.7, 0.1, 0.16, 0.2, 0.03, mi=I['plastic'], rgba=dark)
        m.rbox(-0.8, sy * (W / 2 - 0.045), 0.9, 0.012, 0.012, 1.2, 0.004, mi=I['steel_charcoal'], rgba=dark) if False else None
        m.rbox(-0.2, sy * (W / 2 - 0.05), 1.05, 0.02, 0.012, 1.4, 0.004, mi=I['steel_charcoal'], rgba=dark)
        m.rbox(L / 2 - 0.08, sy * 0.7, 0.8, 0.06, 0.26, 0.14, 0.03, mi=I['plastic'], rgba=(0.88, 0.88, 0.8, 1))
        m.rbox(-L / 2 + 0.07, sy * 0.72, 1.0, 0.05, 0.14, 0.4, 0.02, mi=I['plastic'], rgba=(0.75, 0.1, 0.08, 1))
        for x in (L / 2 - 1.05, -L / 2 + 1.2):
            wheel(m, x, sy * (W / 2 - 0.12), 0.37, flip=sy)
            m.add(p_torus(0.43, 0.035, 28, 6), (x, sy * (W / 2 - 0.07), 0.37), (math.pi / 2, 0, 0), mi=I['props'], rgba=tuple(c * 0.85 for c in paint[:3]) + (1,))
    m.rbox(L / 2 - 0.05, 0, 0.55, 0.06, W - 0.4, 0.3, 0.02, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(L / 2 + 0.02, 0, 0.36, 0.16, W, 0.18, 0.05, mi=I['steel_charcoal'], rgba=(0.45, 0.46, 0.48, 1))
    m.rbox(-L / 2 - 0.02, 0, 0.36, 0.16, W, 0.18, 0.05, mi=I['steel_charcoal'], rgba=(0.45, 0.46, 0.48, 1))
    m.rbox(0.4, W / 2 + 0.006, 1.2, 1.4, 0.01, 0.34, 0.004, mi=I['signage'], rgba=(0.82, 0.38, 0.06, 1))
    m.rbox(-L / 2 + 0.01, 0, 1.35, 0.02, 0.02, 1.4, 0.004, mi=I['steel_charcoal'], rgba=dark)
    return m.finish('proto_' + name, P)

def fence_panel(F, P, L=3.0, H=2.2):
    """Welded-mesh security fence panel with round bars and a top rail."""
    m = mb(F); steel = (0.1, 0.1, 0.12, 1)
    m.between((-L / 2, 0, H), (L / 2, 0, H), 0.022, seg=8, mi=I['steel_charcoal'], rgba=steel)
    m.between((-L / 2, 0, 0.03), (L / 2, 0, 0.03), 0.02, seg=8, mi=I['steel_charcoal'], rgba=steel)
    n = int(L / 0.11)
    for k in range(n + 1):
        x = -L / 2 + k * L / n; m.between((x, 0, 0.03), (x, 0, H), 0.006, seg=4, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.16, 1))
    for z in (0.6, 1.1, 1.6): m.between((-L / 2, 0.0, z), (L / 2, 0.0, z), 0.0065, seg=4, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.16, 1))
    return m.finish('proto_fence_panel', P)

def fence_post(F, P, H=2.4):
    m = mb(F); steel = (0.1, 0.1, 0.12, 1)
    m.cylz(0, 0, 0.0, H, 0.045, seg=10, mi=I['steel_charcoal'], rgba=steel)
    m.cylz(0, 0, H, H + 0.03, 0.055, seg=10, mi=I['steel_charcoal'], rgba=steel)
    m.cylz(0, 0, 0.0, 0.04, 0.08, seg=10, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_fence_post', P)

def ore_cart(F, P):
    m = mb(F); rust = (0.34, 0.2, 0.11, 1); steel = (0.1, 0.1, 0.11, 1)
    m.rbox(0, 0, 0.7, 2.2, 1.15, 0.07, 0.015, mi=I['props'], rgba=rust)
    for sy in (-1, 1):
        m.rbox(0, sy * 0.54, 1.02, 2.3, 0.06, 0.7, 0.02, rot=(sy * -0.12, 0, 0), mi=I['props'], rgba=rust)
        m.rbox(0, sy * 0.58, 1.38, 2.4, 0.1, 0.08, 0.025, mi=I['props'], rgba=tuple(c * 0.8 for c in rust[:3]) + (1,))
    for sx in (-1, 1):
        m.rbox(sx * 1.12, 0, 1.02, 0.06, 1.1, 0.7, 0.02, rot=(0, sx * 0.1, 0), mi=I['props'], rgba=rust)
        m.rbox(sx * 1.16, 0, 1.38, 0.1, 1.2, 0.08, 0.025, mi=I['props'], rgba=tuple(c * 0.8 for c in rust[:3]) + (1,))
        m.rbox(sx * 1.35, 0, 0.5, 0.35, 0.07, 0.07, 0.01, mi=I['steel_charcoal'], rgba=steel)
        m.add(p_cyl(0.05, 0.12, 12), (sx * 1.55, 0, 0.5), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=steel)
    for k in range(3):
        x = -0.9 + k * 0.9
        for sy in (-1, 1): m.cylz(x, sy * 0.57, 0.9, 1.3, 0.0, seg=3) if False else m.add(p_cyl(0.014, 0.05, 8), (x, sy * 0.61, 1.0 + k * 0.0), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.3, 0.3, 0.3, 1))
    for sx in (-0.75, 0.75):
        m.between((sx, -0.62, 0.34), (sx, 0.62, 0.34), 0.03, seg=10, mi=I['steel_charcoal'], rgba=steel)
        for sy in (-1, 1):
            m.add(p_cyl(0.3, 0.07, 24), (sx, sy * 0.66, 0.34), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
            m.add(p_cyl(0.06, 0.1, 12), (sx, sy * 0.68, 0.34), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.4, 0.4, 0.42, 1))
            for k in range(6): m.add(p_between((sx, sy * 0.71, 0.34), (sx + math.cos(k * 1.047) * 0.27, sy * 0.71, 0.34 + math.sin(k * 1.047) * 0.27), 0.012, 6) if False else p_cyl(0.001, 0.001, 3), (sx, sy * 0.71, 0.34))
    m.rbox(0, 0, 0.52, 1.9, 0.12, 0.1, 0.015, mi=I['steel_charcoal'], rgba=steel)
    for sx in (-0.75, 0.75): m.rbox(sx, 0, 0.45, 0.1, 1.4, 0.05, 0.01, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_ore_cart', P)

def shrub(F, P, seed=1, r=0.55, n=95):
    m = mb(F); rnd = random.Random(seed)
    greens = [(0.10, 0.28, 0.08, 1), (0.14, 0.34, 0.1, 1), (0.08, 0.22, 0.07, 1), (0.2, 0.38, 0.1, 1)]
    for i in range(n):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.0, r * 0.8); z = 0.12 + rnd.uniform(0.0, r * 1.3) * (1 - d / r * 0.5)
        m.leaf((math.cos(a) * d, math.sin(a) * d, z), rnd.uniform(0.26, 0.4), rnd.uniform(0.09, 0.14), bend=rnd.uniform(0.1, 0.4), twist=rnd.uniform(-0.3, 0.3), yaw=a - math.pi / 2 + rnd.uniform(-0.5, 0.5), pitch=rnd.uniform(0.2, 1.0), segs=3, mi=I['foliage'], rgba=rnd.choice(greens))
    for k in range(5):
        a = k * 1.26; m.between((0, 0, 0.0), (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.35), 0.012, seg=6, mi=I['props'], rgba=(0.3, 0.2, 0.1, 1))
    return m.finish(f'proto_shrub_{seed}', P)

def tree(F, P, seed=1, h=4.2):
    m = mb(F); rnd = random.Random(seed)
    greens = [(0.10, 0.28, 0.08, 1), (0.14, 0.34, 0.1, 1), (0.08, 0.22, 0.07, 1), (0.22, 0.4, 0.1, 1)]
    bark = (0.26, 0.17, 0.1, 1)
    m.lathe([(0.0, 0.0), (0.17, 0.0), (0.14, 0.4), (0.1, 1.6), (0.06, h * 0.75), (0.0, h * 0.75)], seg=14, mi=I['props'], rgba=bark)
    branches = []
    for k in range(9):
        a = k * 2.4 + rnd.uniform(0, 1); z0 = h * (0.4 + 0.055 * k); ln = rnd.uniform(0.9, 1.5) * (1.0 - 0.06 * k)
        p1 = (math.cos(a) * ln, math.sin(a) * ln, z0 + rnd.uniform(0.3, 0.7)); m.between((0, 0, z0), p1, 0.035, seg=8, r2=0.02, mi=I['props'], rgba=bark); branches.append(p1)
    branches.append((0, 0, h * 0.8))
    for (bx, by, bz) in branches:
        for i in range(46):
            a = rnd.uniform(0, 6.28); d = rnd.uniform(0.0, 0.8)
            m.leaf((bx + math.cos(a) * d * 0.5, by + math.sin(a) * d * 0.5, bz + rnd.uniform(-0.25, 0.65)), rnd.uniform(0.26, 0.4), rnd.uniform(0.1, 0.15), bend=0.2, yaw=a - math.pi / 2, pitch=rnd.uniform(-0.4, 0.8), segs=3, mi=I['foliage'], rgba=rnd.choice(greens))
    return m.finish(f'proto_tree_{seed}', P)

def forklift(F, P, rgba=(0.85, 0.62, 0.06, 1)):
    m = mb(F); dark = (0.07, 0.07, 0.08, 1)
    m.rbox(-0.35, 0, 0.7, 1.9, 1.1, 0.8, 0.07, mi=I['props'], rgba=rgba)
    m.rbox(-0.9, 0, 1.15, 0.6, 1.0, 0.45, 0.05, mi=I['props'], rgba=rgba)
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(0.1 + sx * 0.35, sy * 0.52, 1.1, 2.1, 0.03, seg=8, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(0.1, 0, 2.1, 0.8, 1.1, 0.05, 0.015, mi=I['steel_charcoal'], rgba=dark)
    m.rbox(0.0, 0.0, 1.35, 0.55, 0.6, 0.08, 0.03, mi=I['plastic'], rgba=(0.1, 0.1, 0.12, 1)); m.rbox(-0.2, 0.0, 1.6, 0.1, 0.6, 0.45, 0.03, mi=I['plastic'], rgba=(0.1, 0.1, 0.12, 1))
    for sy in (-1, 1): m.rbox(0.82, sy * 0.28, 1.2, 0.08, 0.1, 2.4, 0.015, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1)); m.rbox(0.95, sy * 0.28, 0.1, 1.0, 0.14, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1)); m.rbox(0.9, sy * 0.28, 0.4, 0.06, 0.1, 0.7, 0.01, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    m.rbox(0.82, 0, 2.3, 0.08, 0.7, 0.06, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1)); m.rbox(0.82, 0, 1.5, 0.08, 0.7, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for x, r in ((0.35, 0.3), (-0.95, 0.26)):
        for sy in (-1, 1): wheel(m, x, sy * 0.5, r, r=r, w=0.24, flip=sy)
    m.rbox(-1.3, 0, 0.9, 0.2, 0.9, 0.6, 0.06, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    return m.finish('proto_forklift', P)

def gas_rack(F, P):
    m = mb(F); cols = [(0.7, 0.1, 0.08, 1), (0.1, 0.3, 0.6, 1), (0.15, 0.4, 0.2, 1), (0.85, 0.85, 0.82, 1)]
    for sx in (-1, 1):
        for sy in (-1, 1): m.cylz(sx * 0.65, sy * 0.3, 0.0, 1.6, 0.025, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    m.rbox(0, 0, 0.05, 1.4, 0.7, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1)); m.rbox(0, 0, 1.6, 1.4, 0.7, 0.04, 0.01, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    for i, (x, y) in enumerate(((-0.45, -0.15), (-0.15, -0.15), (0.15, -0.15), (0.45, -0.15), (-0.45, 0.17), (-0.15, 0.17), (0.15, 0.17), (0.45, 0.17))):
        c = cols[i % 4]; m.lathe([(0.0, 0.0), (0.1, 0.0), (0.115, 0.05), (0.12, 0.8), (0.1, 1.0), (0.05, 1.08), (0.0, 1.1)], loc=(x, y, 0.08), seg=16, mi=I['props'], rgba=c)
        m.cylz(x, y, 1.18, 1.3, 0.025, seg=8, mi=I['steel_charcoal'], rgba=(0.6, 0.6, 0.62, 1))
    for z in (0.5, 1.0): 
        for sy in (-1, 1): m.between((-0.65, sy * 0.3, z), (0.65, sy * 0.3, z), 0.012, seg=6, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
    return m.finish('proto_gas_rack', P)

def hand_truck(F, P):
    m = mb(F); b = (0.15, 0.25, 0.5, 1)
    for sy in (-1, 1): m.between((0.0, sy * 0.2, 0.2), (-0.2, sy * 0.2, 1.2), 0.016, seg=8, mi=I['props'], rgba=b)
    m.between((-0.2, -0.2, 1.2), (-0.2, 0.2, 1.2), 0.016, seg=8, mi=I['props'], rgba=b)
    for z in (0.5, 0.85): m.between((-0.08 - (z - 0.2) * 0.2, -0.2, z), (-0.08 - (z - 0.2) * 0.2, 0.2, z), 0.012, seg=6, mi=I['props'], rgba=b)
    m.rbox(0.12, 0.0, 0.1, 0.3, 0.36, 0.02, 0.006, mi=I['props'], rgba=b)
    for sy in (-1, 1): wheel(m, -0.05, sy * 0.27, 0.12, r=0.12, w=0.06, flip=sy)
    return m.finish('proto_hand_truck', P)

def hose_reel(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.4, 0.5, 0.5, 0.8, 0.03, mi=I['props'], rgba=(0.15, 0.2, 0.35, 1)) if False else None
    m.rbox(0, -0.05, 0.02, 0.5, 0.45, 0.04, 0.008, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for sx in (-1, 1): m.rbox(sx * 0.2, 0, 0.35, 0.03, 0.4, 0.7, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.add(p_cyl(0.28, 0.34, 28), (0, 0, 0.45), (0, math.pi / 2, 0), mi=I['props'], rgba=(0.12, 0.3, 0.2, 1))
    for r in range(5): m.add(p_torus(0.18, 0.03, 24, 6), (0, 0, 0.45), (0, math.pi / 2, 0), mi=I['rubber'], rgba=(0.1, 0.4, 0.2, 1)) if False else None
    m.add(p_cyl(0.2, 0.3, 24), (0, 0, 0.45), (0, math.pi / 2, 0), mi=I['rubber'], rgba=(0.08, 0.35, 0.18, 1))
    m.rbox(0.0, 0.0, 0.95, 0.5, 0.06, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    return m.finish('proto_hose_reel', P)

def traffic_barrier(F, P):
    m = mb(F)
    for sx in (-1, 1): m.between((sx * 0.7, 0.0, 0.0), (sx * 0.6, 0.0, 1.0), 0.02, seg=8, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    for z in (0.35, 0.8):
        for k in range(8): m.rbox(-0.7 + (k + 0.5) * 0.175, 0.0, z, 0.1, 0.03, 0.14, 0.004, rot=(0, 0.6 if k % 2 else -0.6, 0), mi=I['signage'], rgba=(0.9, 0.7, 0.05, 1) if k % 2 else (0.1, 0.1, 0.1, 1))
        m.rbox(0, 0, z, 1.45, 0.03, 0.15, 0.006, mi=I['signage'], rgba=(0.92, 0.92, 0.9, 1)) if False else None
    return m.finish('proto_traffic_barrier', P)

def sign_post(F, P, text_rgba=(0.85, 0.12, 0.1, 1)):
    m = mb(F)
    m.cylz(0, 0, 0.0, 2.2, 0.03, seg=10, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    m.rbox(0, 0.035, 1.95, 0.5, 0.02, 0.5, 0.01, mi=I['signage'], rgba=text_rgba)
    m.rbox(0, 0.05, 1.95, 0.34, 0.006, 0.08, 0.002, mi=I['signage'], rgba=(0.95, 0.95, 0.92, 1))
    return m.finish('proto_sign_post', P)

def car_on_blocks(F, P, rgba=(0.14, 0.2, 0.28, 1)):
    """Stripped utility car on blocks awaiting parts: body shell, no wheels, bonnet up."""
    m = mb(F); L, W = 4.3, 1.8; dark = (0.07, 0.07, 0.08, 1)
    m.rbox(0, 0, 0.78, L - 0.2, W - 0.1, 0.62, 0.08, mi=I['props'], rgba=rgba)
    m.rbox(-0.2, 0, 1.3, 2.2, W - 0.2, 0.55, 0.12, mi=I['props'], rgba=rgba)
    m.rbox(-0.2, 0, 1.3, 2.0, W - 0.1, 0.4, 0.05, mi=I['glass'])
    m.rbox(L / 2 - 0.9, 0, 1.4, 1.2, W - 0.2, 0.03, 0.01, rot=(0, -0.9, 0), mi=I['props'], rgba=rgba)
    m.rbox(L / 2 - 0.9, 0, 1.0, 1.4, W - 0.4, 0.5, 0.04, mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))
    m.rbox(L / 2 + 0.02, 0, 0.45, 0.14, W, 0.2, 0.04, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1)); m.rbox(-L / 2 - 0.02, 0, 0.45, 0.14, W, 0.2, 0.04, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    for x in (-1.3, 1.3):
        for sy in (-1, 1): m.rbox(x, sy * 0.7, 0.2, 0.3, 0.3, 0.4, 0.02, mi=I['concrete_slab']); m.add(p_cyl(0.06, 0.1, 12), (x, sy * 0.78, 0.45), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    return m.finish('proto_car_blocks', P)
