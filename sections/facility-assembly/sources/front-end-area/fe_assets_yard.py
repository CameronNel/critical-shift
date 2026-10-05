"""Yard assets at spawn-room quality: crates, pallets, drums, tyres, cones, bollards, benches, planters, poles, rail kit."""
from fe_kit import *
from fe_propkit import *
from fe_assets_int import STD, I, mb

def crate(F, P, variant=0):
    """Shipping crate 0.96 x 0.96 x 1.0. v0: planked pine with corner posts, diagonal braces, nailed lid cleats, steel strapping and a stencil panel;
    v1 (and odd variants): olive-painted planked box with corner caps, hasp and padlock, side handles and a yellow-black stencil panel."""
    m = mb(F); rnd = random.Random(variant * 7 + 3); painted = variant % 2 == 1
    BODY = I['paint'] if painted else I['timber']
    pal = [(0.07, 0.09, 0.20, 1), (0.42, 0.34, 0.40, 1), (0.62, 0.27, 0.16, 1)][(variant // 2) % 3] if painted else (0.7, 0.55, 0.35, 1)
    DARKW = (0.05, 0.035, 0.025, 1); H = 0.45
    for sx in (-1, 1): m.rbox(sx * 0.33, 0, 0.045, 0.1, 0.96, 0.09, 0.01, seg=1, mi=I['timber'])                                   # skids
    m.rbox(0, 0, 0.5, 0.88, 0.88, 0.8, 0.0, mi=I['timber'], rgba=DARKW)                                                          # core shadow
    nb = 6; bh = 0.8 / nb
    for i in range(nb):
        z = 0.1 + (i + 0.5) * bh
        for sx in (-1, 1): m.rbox(sx * H, 0, z, 0.03, 0.9, bh - 0.012, 0.0, mi=BODY, rgba=tuple(c * rnd.uniform(0.85, 1.12) for c in pal[:3]) + (1,))
        for sy in (-1, 1): m.rbox(0, sy * H, z, 0.84, 0.03, bh - 0.012, 0.0, mi=BODY, rgba=tuple(c * rnd.uniform(0.85, 1.12) for c in pal[:3]) + (1,))
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * H, sy * H, 0.5, 0.095, 0.095, 0.86, 0.012, seg=1, mi=BODY, rgba=tuple(c * 0.82 for c in pal[:3]) + (1,))
    for z in (0.14, 0.9):
        for sy in (-1, 1): m.rbox(0, sy * H, z, 0.84, 0.095, 0.07, 0.0, mi=BODY, rgba=tuple(c * 0.82 for c in pal[:3]) + (1,))
        for sx in (-1, 1): m.rbox(sx * H, 0, z, 0.095, 0.84, 0.07, 0.0, mi=BODY, rgba=tuple(c * 0.82 for c in pal[:3]) + (1,))
    # lid: boards across, slightly askew
    lid = rnd.uniform(-0.03, 0.03)
    for i in range(6): m.rbox(0, -0.4 + i * 0.16, 0.975, 0.98, 0.15, 0.03, 0.0, rot=(0, 0, lid), mi=BODY, rgba=tuple(c * rnd.uniform(0.9, 1.1) for c in pal[:3]) + (1,))
    for sx in (-1, 1): m.rbox(sx * 0.32, 0, 1.0, 0.09, 0.98, 0.025, 0.0, rot=(0, 0, lid), mi=BODY, rgba=tuple(c * 0.85 for c in pal[:3]) + (1,))
    nails = [(sx * 0.32, -0.4 + i * 0.16, 1.014) for sx in (-1, 1) for i in range(6)]
    studs(m, nails, '+z', r=0.01, h=0.007, seg=4, mi=I['steel_charcoal'])
    for sy in (-1, 1):                                                                                               # nails along posts
        f = '+y' if sy > 0 else '-y'
        studs(m, [(sx * 0.4, sy * 0.499, z) for sx in (-1, 1) for z in (0.2, 0.5, 0.82)], f, r=0.01, h=0.007, seg=4, mi=I['steel_charcoal'])
    # diagonal braces on the x faces
    for sx in (-1, 1): m.rbox(sx * 0.472, 0, 0.52, 0.026, 1.0, 0.07, 0.0, rot=(0.72 if sx > 0 else -0.72, 0, 0), mi=BODY, rgba=tuple(c * 0.9 for c in pal[:3]) + (1,))
    # stencil panels on the y faces
    for sy in (-1, 1):
        f = '+y' if sy > 0 else '-y'; y = sy * 0.469
        if not painted:
            m.rbox(0, y, 0.53, 0.40, 0.006, 0.22, 0.002, mi=I['signage'], rgba=(0.78, 0.76, 0.68, 1))
            m.rbox(0, y + sy * 0.004, 0.62, 0.30, 0.004, 0.025, 0.0, mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1)); m.rbox(0, y + sy * 0.004, 0.55, 0.22, 0.004, 0.02, 0.0, mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1))
            m.rbox(-0.1, y + sy * 0.004, 0.46, 0.012, 0.004, 0.09, 0.0, mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1))
            for a in (-0.6, 0.6): m.rbox(-0.1 + math.sin(a) * -0.025, y + sy * 0.004, 0.50 - abs(a) * 0.0, 0.012, 0.004, 0.06, 0.0, rot=(0, a, 0), mi=I['signage'], rgba=(0.08, 0.08, 0.08, 1))
            for sx in (-1, 1):                                                                                      # steel strap down the face
                m.rbox(sx * 0.28, y + sy * 0.001, 0.5, 0.03, 0.008, 0.86, 0.0, mi=I['steel_charcoal'])
            m.rbox(0.28 * rnd.choice((-1, 1)), y + sy * 0.006, 0.45, 0.05, 0.01, 0.04, 0.003, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
        else:
            m.rbox(0, y, 0.55, 0.42, 0.006, 0.26, 0.002, mi=I['signage'], rgba=(0.85, 0.62, 0.12, 1))
            for k in range(5): m.rbox(-0.16 + k * 0.08, y + sy * 0.004, 0.55, 0.035, 0.004, 0.19, 0.0, rot=(0, 0.5, 0), mi=I['signage'], rgba=(0.06, 0.06, 0.06, 1)) if k % 2 == 0 else None
            m.rbox(0, y + sy * 0.005, 0.55, 0.24, 0.004, 0.1, 0.0, mi=I['signage'], rgba=(0.88, 0.86, 0.78, 1))
    if not painted:
        for sx in (-1, 1): m.rbox(sx * 0.28, 0, 1.02, 0.03, 0.96, 0.008, 0.0, mi=I['steel_charcoal'])
        for sx in (-1, 1):
            for sy in (-1, 1): m.rbox(sx * 0.46, sy * 0.46, 0.96, 0.17, 0.17, 0.02, 0.004, rot=(0, 0, math.pi / 4 * 0), seg=1, mi=I['steel_charcoal'])
    else:
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.rbox(sx * 0.475, sy * 0.475, 0.96, 0.11, 0.11, 0.1, 0.012, seg=1, mi=I['steel_charcoal'])
                m.rbox(sx * 0.475, sy * 0.475, 0.08, 0.11, 0.11, 0.1, 0.012, seg=1, mi=I['steel_charcoal'])
        for sx in (-1, 1):
            m.add(p_torus(0.065, 0.011, 10, 5), (sx * 0.495, 0, 0.72), (0, math.pi / 2, 0), mi=I['steel_charcoal'])
            m.rbox(sx * 0.49, 0.0, 0.72, 0.03, 0.2, 0.05, 0.006, seg=1, mi=I['steel_charcoal'])
        m.rbox(0, 0.485, 0.9, 0.1, 0.012, 0.09, 0.004, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))            # hasp and padlock
        m.rbox(0, 0.488, 0.8, 0.06, 0.02, 0.07, 0.006, seg=1, mi=I['steel_charcoal'])
        m.add(p_cyl(0.025, 0.03, 8), (0, 0.5, 0.78), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
    weather(m, variant, dirt=0.55, dirt_h=0.22, streak=0.2, blotch=0.18, top=0.25)
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
    """Steel drum 0.9 m: rolled chimes, three rolling hoops, dented body, recessed lid with ring-lock clamp, flanged bung and vent plug, and a stencil label panel."""
    PAL = [(0.07, 0.09, 0.20, 1), (0.62, 0.27, 0.16, 1), (0.42, 0.34, 0.40, 1), (0.85, 0.62, 0.12, 1)]
    m = mb(F); rnd = random.Random(int(sum(rgba[:3]) * 1000) + 7)
    rgba = min(PAL, key=lambda c: sum((a - b) ** 2 for a, b in zip(c[:3], rgba[:3])))   # painted props use the studio palette only
    prof = [(0.0, 0.0), (0.262, 0.0), (0.284, 0.018), (0.294, 0.05), (0.284, 0.088), (0.287, 0.115), (0.298, 0.13), (0.298, 0.165), (0.287, 0.18), (0.288, 0.26), (0.289, 0.34), (0.289, 0.43),
            (0.298, 0.445), (0.298, 0.485), (0.287, 0.50), (0.289, 0.58), (0.289, 0.66), (0.287, 0.70), (0.298, 0.715), (0.298, 0.75), (0.287, 0.765), (0.288, 0.83), (0.296, 0.875), (0.296, 0.9), (0.282, 0.915), (0.262, 0.9), (0.256, 0.885), (0.0, 0.885)]
    pb = p_lathe(prof, 24)
    for _ in range(3): dent(pb, rnd.uniform(0, 6.28), rnd.uniform(0.25, 0.65), rnd.uniform(0.008, 0.016), rnd.uniform(0.05, 0.09), 0.29)
    add_var(m, pb, mi=I['props'], rgba=rgba, var=0.0, rnd=rnd, flat=False)
    m.add(p_torus(0.268, 0.011, 24, 5), (0, 0, 0.9), mi=I['steel_charcoal'])                                       # ring-lock band
    a = rnd.uniform(0, 6.28); ca, sa = math.cos(a), math.sin(a)
    m.rbox(ca * 0.272, sa * 0.272, 0.915, 0.05, 0.05, 0.035, 0.008, rot=(0, 0, a), seg=1, mi=I['steel_charcoal'])
    m.between((ca * 0.28, sa * 0.28, 0.935), (ca * 0.2, sa * 0.2, 0.95), 0.007, seg=5, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
    m.add(p_cyl(0.045, 0.012, 12), (0.12, 0.1, 0.892), mi=I['steel_charcoal']); m.add(p_cyl(0.028, 0.026, 6), (0.12, 0.1, 0.9), mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))   # bung
    m.add(p_cyl(0.026, 0.01, 10), (-0.12, -0.08, 0.89), mi=I['steel_charcoal']); m.add(p_cyl(0.015, 0.02, 6), (-0.12, -0.08, 0.895), mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))    # vent plug
    la = rnd.uniform(0, 6.28); lc = rnd.choice([(0.88, 0.85, 0.76, 1), (0.85, 0.7, 0.12, 1), (0.8, 0.8, 0.78, 1)])
    m.add(p_arc_band(0.289, 0.52, 0.69, la, la + 1.5, 10, 0.005), mi=I['signage'], rgba=lc)                      # label panel
    m.add(p_arc_band(0.289, 0.58, 0.60, la + 0.1, la + 1.4, 8, 0.008), mi=I['signage'], rgba=(0.07, 0.07, 0.07, 1))
    m.add(p_arc_band(0.289, 0.62, 0.64, la + 0.1, la + 1.0, 8, 0.008), mi=I['signage'], rgba=(0.07, 0.07, 0.07, 1))
    m.add(p_arc_band(0.289, 0.54, 0.56, la + 0.1, la + 0.6, 6, 0.008), mi=I['signage'], rgba=(0.07, 0.07, 0.07, 1))
    weather(m, int(rgba[0] * 100), dirt=0.45, dirt_h=0.15, streak=0.3, blotch=0.22, top=0.3, angle=26.0)
    return m.finish('proto_' + name, P)

def cable_drum(F, P):
    """Timber cable drum 1.0 dia x 0.67: banded flanges with cross battens and rim through-bolts, steel hub plates, wound cable layers and a loose cable tail."""
    m = mb(F); rnd = random.Random(11); W = (0.5, 0.34, 0.18, 1); CAB = (0.045, 0.045, 0.05, 1)
    for z, s in ((0.0, 1), (0.62, -1)):
        m.cylz(0, 0, z, z + 0.05, 0.5, seg=28, bevel=0.012, mi=I['timber'])
        face = z + 0.05 if s > 0 else z                                  # outer face of this flange is the one away from the barrel
        zo = z if s > 0 else z + 0.05
        for y in (-0.24, 0.0, 0.24):
            L = 2 * math.sqrt(0.5 ** 2 - y * y) - 0.06
            m.rbox(0, y, zo - s * 0.012, L, 0.11, 0.02, 0.004, seg=1, mi=I['timber'], rgba=W)
        m.add(p_cyl(0.13, 0.014, 14), (0, 0, zo - s * 0.024), mi=I['steel_charcoal'])
        hex_bolt(m, (0, 0, zo - s * 0.034), '+z' if s < 0 else '-z', 0.035, 0.02, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
        for k in range(8):
            a = k * math.pi / 4 + 0.2; x, y = math.cos(a) * 0.43, math.sin(a) * 0.43
            hex_bolt(m, (x, y, zo - s * 0.018), '+z' if s < 0 else '-z', 0.016, 0.012, mi=I['steel_charcoal'])
        m.add(p_torus(0.5, 0.008, 28, 4), (0, 0, z + 0.025), mi=I['steel_charcoal'])                              # rim band
    m.cylz(0, 0, 0.05, 0.62, 0.12, seg=14, mi=I['timber'], rgba=W)
    prof = [(0.27, 0.05)]
    for k in range(8): z0 = 0.05 + k * 0.0713; prof += [(0.275, z0 + 0.01), (0.305, z0 + 0.0357), (0.275, z0 + 0.0713 - 0.01)]
    prof += [(0.27, 0.62)]
    m.lathe(prof, seg=24, mi=I['rubber'])                                                              # wound cable layers
    cable(m, bez((0.29, 0.0, 0.5), (0.62, 0.05, 0.56), (0.63, 0.12, 0.05), 6), 0.016, 6, mi=I['rubber'])    # loose tail
    m.rbox(0.62, 0.14, 0.02, 0.07, 0.06, 0.04, 0.006, seg=1, mi=I['rubber'])
    weather(m, 11, dirt=0.4, dirt_h=0.2, streak=0.2, blotch=0.2, top=0.2)
    return m.finish('proto_cable_drum', P)

def tyre(F, P, stack=1, name='tyre'):
    m = mb(F)
    prof = [(0.17, 0.0), (0.235, 0.0), (0.29, 0.015), (0.32, 0.06), (0.325, 0.12), (0.32, 0.18), (0.29, 0.225), (0.235, 0.24), (0.17, 0.24), (0.165, 0.2), (0.165, 0.04)]
    for k in range(stack):
        m.lathe(prof, loc=(0, 0, k * 0.235), seg=28, mi=I['rubber'], rgba=(0.035, 0.035, 0.038, 1), close=False)
    return m.finish('proto_' + name, P)

def cone(F, P):
    """Traffic cone 0.7 m: chamfered square rubber base with slots, tall orange body with moulded neck, two retro-reflective bands, handle ring."""
    m = mb(F)
    m.rbox(0, 0, 0.016, 0.42, 0.42, 0.032, 0.012, seg=2, mi=I['rubber'])
    m.rbox(0, 0, 0.03, 0.34, 0.34, 0.014, 0.006, seg=1, mi=I['rubber'])
    for sx in (-1, 1):
        for sy in (-1, 1): m.rbox(sx * 0.17, sy * 0.17, 0.034, 0.05, 0.05, 0.004, 0.0, mi=I['rubber'], rgba=(0.01, 0.01, 0.01, 1))
    m.lathe([(0.152, 0.03), (0.15, 0.06), (0.118, 0.2), (0.088, 0.4), (0.062, 0.58), (0.045, 0.66), (0.036, 0.69), (0.03, 0.7), (0.0, 0.7)], seg=20, mi=I['plastic'], rgba=(0.92, 0.34, 0.05, 1))
    m.add(p_torus(0.04, 0.008, 12, 4), (0, 0, 0.67), mi=I['plastic'], rgba=(0.86, 0.3, 0.05, 1))
    m.lathe([(0.108, 0.24), (0.1, 0.33), (0.0905, 0.33), (0.1005, 0.24)], seg=20, mi=I['signage'], rgba=(0.9, 0.9, 0.86, 1))
    m.lathe([(0.0795, 0.43), (0.0735, 0.5), (0.0645, 0.5), (0.0705, 0.43)], seg=20, mi=I['signage'], rgba=(0.9, 0.9, 0.86, 1))
    weather(m, 3, dirt=0.4, dirt_h=0.12, streak=0.1, blotch=0.12, top=0.1)
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
    weather(m, 9, dirt=0.35, dirt_h=0.6, streak=0.35, blotch=0.25, top=0.1, angle=32.0)
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
    """Diesel generator set 3.0 x 1.3 x 2.5 in a sound-proof canopy (front toward +y): channel skid with integral fuel tank, filler cap, drain valve and level gauge, louvred hinged doors with
    handles, a recessed control compartment (LCD, dials, lamps, e-stop, switches), roof lifting eye, silencer with exhaust stack and hinged rain cap, cable gland box with cable runs, lifting eyes."""
    m = mb(F); rnd = random.Random(31); OR = (0.62, 0.27, 0.16, 1); OR2 = (0.50, 0.21, 0.13, 1); DK = (0.07, 0.07, 0.08, 1); BR = (0.8, 0.8, 0.8, 1)
    for sy in (-1, 1): m.rbox(0, sy * 0.58, 0.09, 3.0, 0.14, 0.18, 0.012, seg=1, mi=I['steel_charcoal'])              # skid runners
    for x in (-1.35, -0.45, 0.45, 1.35): m.rbox(x, 0, 0.09, 0.1, 1.1, 0.14, 0.01, seg=1, mi=I['steel_charcoal'])
    m.rbox(0, 0, 0.31, 2.72, 1.06, 0.24, 0.025, seg=2, mi=I['paint'], rgba=(0.12, 0.12, 0.13, 1))                    # integral fuel tank
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.rbox(sx * 1.46, sy * 0.58, 0.1, 0.07, 0.05, 0.2, 0.006, seg=1, mi=I['steel_charcoal'])                  # lifting eye plate + ring
            m.add(p_torus(0.06, 0.013, 10, 5), (sx * 1.5, sy * 0.58, 0.14), (0, math.pi / 2, 0), mi=I['steel_charcoal'])
    m.rbox(0, 0, 0.88, 2.66, 1.16, 1.12, 0.05, seg=2, mi=I['paint'], rgba=OR)                                       # canopy
    m.rbox(0, 0, 1.46, 2.7, 1.2, 0.06, 0.03, seg=2, mi=I['paint'], rgba=OR2)                                         # roof cap
    for sx in (-1, 1): m.rbox(sx * 1.2, 0, 0.5, 0.18, 1.2, 0.04, 0.01, seg=1, mi=I['steel_charcoal']) if False else None
    m.rbox(0, 0, 0.45, 2.72, 1.2, 0.04, 0.01, seg=1, mi=I['steel_charcoal'])                                          # plinth rail
    # --- front doors with louvres
    for (x, w, c) in ((-0.72, 1.1, OR), (0.36, 0.88, OR)):
        m.rbox(x, 0.592, 0.9, w, 0.026, 0.98, 0.008, seg=1, mi=I['paint'], rgba=tuple(k * 0.94 for k in c[:3]) + (1,))
        m.rbox(x, 0.606, 0.84, w - 0.22, 0.012, 0.7, 0.0, mi=I['steel_charcoal'], rgba=DK)
        for i in range(7): m.rbox(x, 0.62, 0.55 + i * 0.1, w - 0.2, 0.034, 0.032, 0.0, rot=(-0.55, 0, 0), mi=I['paint'], rgba=tuple(k * 0.8 for k in c[:3]) + (1,))
        for z in (0.55, 0.9, 1.3): m.add(p_cyl(0.013, 0.07, 6), (x - w / 2 + 0.01, 0.6, z), mi=I['steel_brushed'], rgba=BR)   # hinge barrels
        m.rbox(x + w / 2 - 0.1, 0.612, 0.92, 0.035, 0.03, 0.14, 0.008, seg=1, mi=I['steel_charcoal'])                  # lever handle
        m.add(p_cyl(0.022, 0.014, 8), (x + w / 2 - 0.1, 0.62, 1.02), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR)
        stud_row(m, (x - w / 2 + 0.05, 0.606, 1.34), (x + w / 2 - 0.05, 0.606, 1.34), 6, '+y', r=0.011, h=0.009, mi=I['steel_charcoal'])
    m.rbox(-0.72, 0.612, 1.3, 0.2, 0.004, 0.1, 0.0, mi=I['signage'], rgba=(0.9, 0.7, 0.06, 1)); m.rbox(-0.72, 0.616, 1.3, 0.16, 0.004, 0.012, 0.0, mi=I['signage'], rgba=(0.06, 0.06, 0.06, 1)); m.rbox(-0.72, 0.616, 1.26, 0.1, 0.004, 0.012, 0.0, mi=I['signage'], rgba=(0.06, 0.06, 0.06, 1))
    # --- control compartment
    cx = 1.0
    m.rbox(cx, 0.585, 0.95, 0.46, 0.03, 0.74, 0.01, seg=1, mi=I['steel_charcoal'])
    m.rbox(cx, 0.605, 1.1, 0.24, 0.012, 0.13, 0.004, seg=1, mi=I['steel_charcoal'], rgba=DK); m.rbox(cx, 0.613, 1.1, 0.2, 0.004, 0.1, 0.0, mi=I['screen'], rgba=(0.35, 0.85, 0.5, 1))
    for k, dx in enumerate((-0.1, 0.1)):
        m.add(p_cyl(0.052, 0.014, 12), (cx + dx, 0.608, 0.92), (-math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR)
        m.add(p_cyl(0.042, 0.006, 12), (cx + dx, 0.617, 0.92), (-math.pi / 2, 0, 0), mi=I['signage'], rgba=(0.9, 0.88, 0.8, 1))
        m.rbox(cx + dx + 0.012 * (1 if k else -1), 0.621, 0.93, 0.004, 0.003, 0.034, 0.0, rot=(0, 0.6 * (1 if k else -1), 0), mi=I['signage'], rgba=(0.05, 0.05, 0.05, 1))
    for k, c in enumerate(((0.1, 0.9, 0.2, 1), (1.0, 0.65, 0.1, 1), (0.9, 0.12, 0.08, 1))): m.add(p_cyl(0.018, 0.014, 8), (cx - 0.12 + k * 0.12, 0.612, 0.8), (-math.pi / 2, 0, 0), mi=I['emissive'], rgba=c)
    m.add(p_cyl(0.05, 0.01, 12), (cx - 0.1, 0.608, 0.67), (-math.pi / 2, 0, 0), mi=I['paint'], rgba=(0.9, 0.7, 0.05, 1)); m.add(p_cyl(0.034, 0.03, 10), (cx - 0.1, 0.62, 0.67), (-math.pi / 2, 0, 0), mi=I['paint'], rgba=(0.85, 0.08, 0.06, 1))   # e-stop
    m.add(p_cyl(0.022, 0.012, 8), (cx + 0.08, 0.608, 0.67), (-math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR); m.rbox(cx + 0.08, 0.62, 0.67, 0.006, 0.01, 0.03, 0.0, mi=I['steel_charcoal'])   # key switch
    for dx in (0.15, 0.19): m.rbox(dx + cx, 0.612, 0.66, 0.012, 0.012, 0.02, 0.0, mi=I['steel_charcoal'])
    m.rbox(cx, 0.6, 0.6, 0.4, 0.008, 0.03, 0.0, mi=I['signage'], rgba=(0.88, 0.7, 0.08, 1))
    for z in (0.58, 1.3): m.add(p_cyl(0.013, 0.06, 6), (cx - 0.2, 0.595, z), mi=I['steel_brushed'], rgba=BR)
    # --- back grille and end details
    m.rbox(-0.3, -0.595, 0.9, 1.5, 0.014, 0.8, 0.006, seg=1, mi=I['steel_charcoal'], rgba=DK)
    for i in range(8): m.rbox(-0.3, -0.606, 0.58 + i * 0.09, 1.4, 0.012, 0.025, 0.0, mi=I['steel_charcoal'])
    for i in range(7): m.rbox(-1.335, 0.0, 0.62 + i * 0.1, 0.014, 0.8, 0.04, 0.0, rot=(0, 0, 0), mi=I['paint'], rgba=OR2) if False else None
    m.rbox(1.345, -0.05, 0.9, 0.04, 0.5, 0.5, 0.01, seg=1, mi=I['steel_charcoal'])                                     # cable gland box
    for k in range(3): m.add(p_cyl(0.026, 0.05, 8), (1.38, -0.2 + k * 0.15, 0.7), (0, math.pi / 2, 0) if False else (0, 0, 0), mi=I['steel_brushed'], rgba=BR) if False else None
    for k in range(3):
        gx = 1.38; gy = -0.2 + k * 0.15
        m.add(p_cyl(0.026, 0.06, 8), (gx, gy, 0.68), (0, 0, 0), mi=I['steel_brushed'], rgba=BR) if False else m.add(p_cyl(0.026, 0.05, 8), (gx, gy, 0.67), (0, math.pi / 2, 0) if False else (0, 0, 0))
    studs(m, [(1.368, y, z) for y in (-0.25, 0.15) for z in (1.12, 0.7)], '+x', r=0.012, h=0.01, mi=I['steel_charcoal'])
    cable(m, bez((1.4, -0.2, 0.62), (1.62, -0.2, 0.3), (1.58, -0.35, 0.025), 5), 0.022, 6, mi=I['rubber'])
    cable(m, bez((1.4, -0.05, 0.62), (1.7, -0.05, 0.35), (1.72, 0.15, 0.025), 5), 0.022, 6, mi=I['rubber'])
    cable(m, bez((1.4, 0.1, 0.62), (1.55, 0.2, 0.3), (1.45, 0.5, 0.025), 5), 0.022, 6, mi=I['rubber'])
    # --- fuel filler, drain valve, gauge
    m.add(p_cyl(0.05, 0.06, 10), (1.1, -0.2, 0.44), mi=I['steel_charcoal']); m.add(p_cyl(0.058, 0.02, 10), (1.1, -0.2, 0.47), mi=I['paint'], rgba=(0.85, 0.7, 0.06, 1))
    m.add(p_cyl(0.025, 0.06, 8), (-1.1, 0.5, 0.2), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR); m.rbox(-1.1, 0.545, 0.2, 0.1, 0.012, 0.012, 0.0, mi=I['paint'], rgba=(0.8, 0.1, 0.06, 1))
    m.add(p_cyl(0.045, 0.018, 12), (-0.5, 0.53, 0.3), (-math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR); m.add(p_cyl(0.036, 0.006, 12), (-0.5, 0.541, 0.3), (-math.pi / 2, 0, 0), mi=I['signage'], rgba=(0.9, 0.88, 0.8, 1))
    # --- roof: lifting eye, silencer, stack with rain cap
    m.rbox(0, 0, 1.5, 0.22, 0.22, 0.02, 0.004, seg=1, mi=I['steel_charcoal']); m.add(p_torus(0.075, 0.016, 12, 5), (0, 0, 1.58), (math.pi / 2, 0, 0), mi=I['steel_charcoal'])
    m.rbox(0.55, 0.12, 1.56, 0.62, 0.46, 0.1, 0.02, seg=1, mi=I['paint'], rgba=OR2)                                  # intake hood
    for i in range(4): m.rbox(0.55, 0.35, 1.53 + i * 0.03, 0.5, 0.012, 0.015, 0.0, mi=I['steel_charcoal'])
    for x in (-0.95, 0.0, 1.0): m.rbox(x, 0, 1.495, 0.03, 1.1, 0.01, 0.0, mi=I['paint'], rgba=tuple(k * 0.75 for k in OR2[:3]) + (1,))   # roof seams
    stud_row(m, (-1.2, 0.5, 1.5), (1.2, 0.5, 1.5), 10, '+z', r=0.012, h=0.01, mi=I['steel_charcoal'])
    m.add(p_cyl(0.125, 0.75, 16), (-0.55, -0.22, 1.66), (0, math.pi / 2, 0), mi=I['steel_charcoal'], rgba=(0.16, 0.14, 0.12, 1))
    for dx in (-0.9, -0.2): m.add(p_cyl(0.14, 0.03, 16), (dx, -0.22, 1.66), (0, math.pi / 2, 0), mi=I['steel_brushed'], rgba=(0.55, 0.52, 0.5, 1))
    for dx in (-0.8, -0.3): m.rbox(dx, -0.22, 1.52, 0.05, 0.22, 0.06, 0.006, seg=1, mi=I['steel_charcoal'])
    m.cylz(-0.3, -0.22, 1.72, 2.42, 0.048, seg=10, mi=I['steel_charcoal'], rgba=(0.14, 0.12, 0.1, 1))
    for z in (1.78, 2.3): m.add(p_torus(0.055, 0.009, 10, 4), (-0.3, -0.22, z), mi=I['steel_brushed'], rgba=(0.55, 0.52, 0.5, 1))
    m.add(p_cyl(0.085, 0.012, 12), (-0.3, -0.22, 2.55), (0.42, 0, 0), mi=I['steel_charcoal'], rgba=(0.16, 0.14, 0.12, 1))        # rain cap flap
    for a in (0.0, 2.1, 4.2): m.between((-0.3 + math.cos(a) * 0.04, -0.22 + math.sin(a) * 0.04, 2.42), (-0.3 + math.cos(a) * 0.05, -0.22 + math.sin(a) * 0.05, 2.52), 0.005, seg=4, mi=I['steel_charcoal'])
    weather(m, 31, dirt=0.35, dirt_h=0.3, streak=0.28, blotch=0.2, top=0.2, angle=32.0)
    return m.finish('proto_generator', P)

def tank_vertical(F, P, h=2.6, r=1.05, rgba=(0.5, 0.52, 0.5, 1), name='tank'):
    """Welded plate water tank: four plate courses with ring and vertical weld seams and bolted lap flanges, stiffened legs on a concrete plinth, blue band, conical roof with hatch, hinged lid and
    handrail, ladder with safety cage (toward the yard), level gauge with isolating valves, flanged outlet pipe with gate valve and drain, vertical inlet pipe with clips, manway with bolted cover."""
    rgba = (0.42, 0.34, 0.40, 1)   # mauve-grey painted plate
    m = mb(F); rnd = random.Random(21); ST = I['steel_charcoal']; BR = (0.8, 0.8, 0.8, 1); n = 4; ch = (h - 0.3) / n
    def Pt(rr, t=0.0, z=0.0, th=0.0): return (rr * math.cos(th) - t * math.sin(th), rr * math.sin(th) + t * math.cos(th), z)
    m.lathe([(0, 0), (r + 0.14, 0), (r + 0.14, 0.07), (r + 0.1, 0.09), (0, 0.09)], seg=28, mi=I['concrete_slab'], rgba=(0.55, 0.53, 0.5, 1))   # plinth
    for k in range(6):
        a = k * math.pi / 3 + 0.2
        m.rbox(math.cos(a) * r * 0.86, math.sin(a) * r * 0.86, 0.19, 0.12, 0.12, 0.22, 0.012, rot=(0, 0, a), seg=1, mi=ST)           # legs
        m.rbox(math.cos(a) * r * 0.86, math.sin(a) * r * 0.86, 0.1, 0.22, 0.22, 0.02, 0.006, rot=(0, 0, a), seg=1, mi=ST)           # foot plates
        studs(m, [Pt(r * 0.86, t, 0.115, a) for t in (-0.07, 0.07)], '+z', r=0.014, h=0.012, mi=I['steel_brushed'], rgba=BR)
    m.add(p_torus(r * 0.93, 0.03, 28, 4), (0, 0, 0.3), mi=ST)                                                                         # base ring
    z0 = 0.3
    for c in range(n):                                                                                                                # courses
        col = tuple(k * rnd.uniform(0.94, 1.06) for k in rgba[:3]) + (1,); rc = r + (0.0 if c % 2 == 0 else 0.012)
        m.lathe([(rc, z0 + 0.004), (rc + 0.002, z0 + ch / 2), (rc, z0 + ch - 0.004)], seg=28, mi=I['paint'], rgba=col)
        if c: m.add(p_torus(r + 0.016, 0.014, 28, 4), (0, 0, z0), mi=I['paint'], rgba=tuple(k * 0.8 for k in col[:3]) + (1,))        # horizontal weld seam
        for k in range(5):
            a = k * 2 * math.pi / 5 + (0.5 if c % 2 else 0.0)
            m.rbox(*Pt(rc + 0.006, 0, z0 + ch / 2, a), 0.012, 0.035, ch - 0.02, 0.0, rot=(0, 0, a), mi=I['paint'], rgba=tuple(k_ * 0.75 for k_ in col[:3]) + (1,))   # vertical weld
        z0 += ch
    for zz in (0.3 + ch, 0.3 + 2 * ch, 0.3 + 3 * ch):                                                                                  # bolt rows at the lap joints
        for i in range(22):
            a = 2 * math.pi * i / 22; m.add(p_stud(0.014, 0.012, 5), Pt(r + 0.03, 0, zz + 0.05, a), (0, math.pi / 2, a), mi=ST)
    m.lathe([(r + 0.006, 1.95), (r + 0.01, 1.96), (r + 0.01, 2.2), (r + 0.006, 2.21)], seg=28, mi=I['paint'], rgba=(0.07, 0.09, 0.20, 1))   # navy band
    m.lathe([(r, h), (r + 0.05, h + 0.012), (r * 0.62, h + 0.17), (r * 0.5, h + 0.2), (0.0, h + 0.2)], seg=28, mi=I['paint'], rgba=tuple(k * 0.86 for k in rgba[:3]) + (1,))   # roof
    m.add(p_torus(r + 0.03, 0.02, 28, 4), (0, 0, h + 0.005), mi=ST)                                                                   # roof angle ring
    # --- roof hatch, handrail
    hx, hy = -0.2, -0.15
    m.rbox(hx, hy, h + 0.28, 0.58, 0.58, 0.08, 0.02, seg=1, mi=ST, rgba=(0.08, 0.08, 0.09, 1)); m.rbox(hx, hy, h + 0.33, 0.52, 0.52, 0.03, 0.012, rot=(0, 0.07, 0.0), seg=1, mi=I['paint'], rgba=(0.55, 0.58, 0.6, 1))
    m.add(p_cyl(0.012, 0.3, 6), (hx - 0.3, hy, h + 0.32), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=BR); m.rbox(hx + 0.2, hy, h + 0.36, 0.1, 0.05, 0.03, 0.008, seg=1, mi=ST)
    stud_row(m, (hx - 0.24, hy + 0.27, h + 0.325), (hx + 0.24, hy + 0.27, h + 0.325), 5, '+y', r=0.012, h=0.01, mi=ST)
    m.cylz(0.5, 0.6, h + 0.19, h + 0.5, 0.06, seg=10, mi=ST); m.add(p_cyl(0.09, 0.02, 12), (0.5, 0.6, h + 0.5), (0.2, 0.0, 0.0), mi=ST)    # vent pipe with cap
    nrail = 14
    for i in range(nrail):
        a = 2 * math.pi * i / nrail + 0.1
        if abs(math.atan2(math.sin(a - 0.35), math.cos(a - 0.35))) < 0.3: continue
        px, py = math.cos(a) * (r * 0.97), math.sin(a) * (r * 0.97)
        m.cylz(px, py, h + 0.02, h + 0.62, 0.015, seg=5, mi=ST)
    for zz in (h + 0.34, h + 0.62): m.add(p_torus(r * 0.97, 0.013, 28, 4), (0, 0, zz), mi=ST)
    m.add(p_torus(r * 0.97, 0.01, 28, 4), (0, 0, h + 0.07), mi=ST)
    # --- ladder with safety cage (faces the yard, angle th)
    th = 0.35; lr = r + 0.13
    for t in (-0.19, 0.19):
        m.rbox(*Pt(lr, t, (0.3 + h + 0.55) / 2, th), 0.035, 0.03, h + 0.25, 0.006, rot=(0, 0, th), seg=1, mi=ST)
    for k in range(int((h - 0.4) / 0.28)):
        z = 0.5 + k * 0.28; m.between(Pt(lr, -0.19, z, th), Pt(lr, 0.19, z, th), 0.014, seg=5, mi=I['steel_brushed'], rgba=BR)
    for z in (0.6, 1.5, 2.4):
        for t in (-0.19, 0.19): m.rbox(*Pt((lr + r + 0.02) / 2, t, z, th), 0.14, 0.03, 0.05, 0.005, rot=(0, 0, th), seg=1, mi=ST)      # standoff brackets
    for zc in (1.75, 2.05, 2.35, 2.65):
        pts = [Pt(lr + 0.04 + 0.34 * math.sin(math.pi * j / 6), 0.34 * math.cos(math.pi * j / 6) * 1.0, zc, th) for j in range(7)]
        for a_, b_ in zip(pts[:-1], pts[1:]): m.between(a_, b_, 0.009, seg=4, mi=ST)
    for j in (0, 2, 3, 4, 6):
        a_ = math.pi * j / 6; m.between(Pt(lr + 0.04 + 0.34 * math.sin(a_), 0.34 * math.cos(a_), 1.75, th), Pt(lr + 0.04 + 0.34 * math.sin(a_), 0.34 * math.cos(a_), 2.65, th), 0.008, seg=4, mi=ST)
    # --- level gauge
    ga = 1.05
    m.between(Pt(r + 0.12, 0, 0.6, ga), Pt(r + 0.12, 0, 2.3, ga), 0.022, seg=8, mi=I['glass'])
    for zz in (0.6, 2.3):
        m.rbox(*Pt(r + 0.1, 0, zz, ga), 0.1, 0.06, 0.07, 0.01, rot=(0, 0, ga), seg=1, mi=ST); m.add(p_cyl(0.026, 0.03, 8), Pt(r + 0.1, 0.0, zz + 0.07, ga), (0, 0, 0), mi=I['paint'], rgba=(0.85, 0.12, 0.08, 1))
    for k in range(9): m.rbox(*Pt(r + 0.12, 0.05, 0.7 + k * 0.18, ga), 0.01, 0.05 if k % 2 == 0 else 0.03, 0.01, 0.0, rot=(0, 0, ga), mi=I['signage'], rgba=(0.9, 0.9, 0.85, 1))
    m.rbox(*Pt(r + 0.12, 0, 1.55, ga), 0.04, 0.045, 0.03, 0.006, rot=(0, 0, ga), seg=1, mi=I['paint'], rgba=(0.9, 0.5, 0.06, 1))        # float
    for t in (-0.04, 0.04): m.between(Pt(r + 0.045, t, 0.6, ga), Pt(r + 0.045, t, 2.3, ga), 0.008, seg=4, mi=ST)
    # --- outlet pipe with gate valve and drain (angle oa)
    oa = 2.55
    m.between(Pt(r - 0.02, 0, 0.65, oa), Pt(r + 0.42, 0, 0.65, oa), 0.06, seg=10, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for dd in (0.04, 0.3):
        m.add(p_cyl(0.095, 0.03, 12), Pt(r + dd, 0, 0.65, oa), (0, math.pi / 2, oa), mi=ST)
    m.rbox(*Pt(r + 0.18, 0, 0.7, oa), 0.14, 0.12, 0.16, 0.02, rot=(0, 0, oa), seg=1, mi=I['paint'], rgba=(0.07, 0.09, 0.20, 1))           # valve body
    m.between(Pt(r + 0.18, 0, 0.78, oa), Pt(r + 0.18, 0, 1.0, oa), 0.014, seg=6, mi=I['steel_brushed'], rgba=BR)
    m.add(p_torus(0.075, 0.011, 12, 4), Pt(r + 0.18, 0, 1.0, oa), (0, 0, 0), mi=I['paint'], rgba=(0.85, 0.1, 0.07, 1))                    # hand wheel
    m.between(Pt(r + 0.42, 0, 0.65, oa), Pt(r + 0.42, 0, 0.2, oa), 0.055, seg=10, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    m.add(p_cyl(0.075, 0.03, 12), Pt(r + 0.42, 0, 0.2, oa), (0, 0, 0), mi=ST); m.rbox(*Pt(r + 0.42, 0, 0.12, oa), 0.14, 0.14, 0.12, 0.02, seg=1, mi=ST)
    # --- inlet pipe up the shell with clips
    ia = 0.75 + 2.2
    m.between(Pt(r + 0.09, 0, 0.5, ia), Pt(r + 0.09, 0, h + 0.05, ia), 0.045, seg=8, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for z in (0.8, 1.5, 2.2): m.rbox(*Pt(r + 0.05, 0, z, ia), 0.09, 0.07, 0.04, 0.006, rot=(0, 0, ia), seg=1, mi=ST)
    m.between(Pt(r + 0.09, 0, h + 0.05, ia), Pt(r * 0.7, 0, h + 0.12, ia), 0.045, seg=8, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    # --- manway
    ma = 3.8
    m.add(p_cyl(0.28, 0.04, 16), Pt(r + 0.02, 0, 1.1, ma), (0, math.pi / 2, ma), mi=ST)
    m.add(p_cyl(0.23, 0.05, 16), Pt(r + 0.06, 0, 1.1, ma), (0, math.pi / 2, ma), mi=I['paint'], rgba=tuple(k * 0.85 for k in rgba[:3]) + (1,))
    for i in range(10):
        a_ = i * math.pi / 5; pp = Pt(r + 0.075, 0.255 * math.cos(a_), 1.1 + 0.255 * math.sin(a_), ma); m.add(p_cyl(0.017, 0.02, 6), pp, (0, math.pi / 2, ma), mi=I['steel_brushed'], rgba=BR)
    m.rbox(*Pt(r + 0.1, 0, 1.1, ma), 0.03, 0.1, 0.03, 0.006, rot=(0, 0, ma), seg=1, mi=ST)
    weather(m, 21, dirt=0.4, dirt_h=0.4, streak=0.3, blotch=0.2, top=0.2, angle=32.0)
    return m.finish('proto_' + name, P)

# ---------------------------------------------------------------- vehicle kit (shared by fe_depot_assets)
def p_panel_xz(pts, y0, y1, bevel=0.0):
    """Polygon given in (x, z) extruded across y0..y1 (body skins, fenders, arch bands, profile extrusions)."""
    pb = bmesh.new(); vs = [pb.verts.new(Vector((x, y0, z))) for x, z in pts]
    f = pb.faces.new(vs); r = bmesh.ops.extrude_face_region(pb, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.y = y1
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    if bevel > 0: bmesh.ops.bevel(pb, geom=pb.edges[:], offset=bevel, segments=1, affect='EDGES')
    return pb

def panel(m, pts, y0, y1, bevel=0.0, mi=None, rgba=None):
    return m.add(p_panel_xz(pts, y0, y1, bevel), mi=mi, rgba=rgba)

def arc_pts(cx, cz, R, a0, a1, n):
    """Points on a circle in the XZ plane, angle measured from +x toward +z (degrees)."""
    return [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cz + R * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def tube(m, pts, r, seg=8, mi=None, rgba=None, joints=True):
    """Polyline of cylinders with ball joints at the bends (roll bars, handrails, hoses)."""
    for a, b in zip(pts, pts[1:]): m.between(a, b, r, seg=seg, mi=mi, rgba=rgba)
    if joints:
        for p in pts[1:-1]: m.sphere(p[0], p[1], p[2], r, rings=4, seg=seg, mi=mi, rgba=rgba)

def bezier(p0, p1, p2, n=6):
    return [tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2)) for t in [k / n for k in range(n + 1)]]

def lowpoly_boxes(m):
    """Vehicles hold hundreds of small rounded boxes: use chamfer-class bevels (2 segments only on big radii) to stay inside the triangle budget."""
    orig = m.rbox
    def rb(cx, cy, cz, sx, sy, sz, r=0.02, rot=(0, 0, 0), seg=None, mi=None, rgba=None):
        return orig(cx, cy, cz, sx, sy, sz, r, rot, 2 if r >= 0.05 else 1, mi, rgba)
    m.rbox = rb; return m

def cube_into(pb, loc, size, rot=(0, 0, 0)):
    M = Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    bmesh.ops.create_cube(pb, size=1.0, matrix=M @ Matrix.Diagonal(Vector((*size, 1))))

def wheel(m, x, y, z, r=0.36, w=0.26, flip=1, rim=(0.5, 0.52, 0.55, 1), lugs=True, detail=1.0):
    """Tyre with sidewall bulge, circumferential grooves and chevron tread blocks, dished rim with lip and bolt ring, six lug nuts, hub cap, valve stem. Axis along Y; flip=+1 puts the outer face toward +y."""
    h = w / 2; seg = max(18, int(28 * detail)); rot = (-math.pi / 2, 0, 0) if flip > 0 else (math.pi / 2, 0, 0)
    half = [(r * 0.60, -h * 0.80), (r * 0.70, -h * 0.98), (r * 0.84, -h * 1.04), (r * 0.94, -h * 0.94), (r * 0.975, -h * 0.70), (r * 0.975, -h * 0.34),
            (r * 0.96, -h * 0.26), (r * 0.96, -h * 0.12)]
    prof = half + [(rr, -zz) for rr, zz in reversed(half)]
    pb = p_lathe(prof, seg); xf(pb, (x, y, z), rot); m.add(pb, mi=I['rubber'], rgba=(0.04, 0.04, 0.043, 1))
    if lugs:                                               # tread blocks standing proud of the grooved base
        n = int(16 * detail) if detail >= 1 else 11; tb = bmesh.new()
        for k in range(n):
            a = 2 * math.pi * k / n
            for zc, sk in ((-h * 0.5, 0.35), (h * 0.5, -0.35)):
                M = Matrix.Rotation(a + (0.05 if zc > 0 else 0), 4, 'Z') @ Matrix.Translation(Vector((r * 0.972, 0, zc))) @ Matrix.Rotation(sk, 4, 'X')
                bmesh.ops.create_cube(tb, size=1.0, matrix=M @ Matrix.Diagonal(Vector((r * 0.05, r * 0.16, h * 0.62, 1))))
            M = Matrix.Rotation(a + 0.025, 4, 'Z') @ Matrix.Translation(Vector((r * 0.968, 0, 0)))
            bmesh.ops.create_cube(tb, size=1.0, matrix=M @ Matrix.Diagonal(Vector((r * 0.04, r * 0.10, h * 0.34, 1))))
        for f in tb.faces: f.smooth = False
        xf(tb, (x, y, z), rot); m.add(tb, mi=I['rubber'], rgba=(0.05, 0.05, 0.055, 1))
    prof = [(0.0, h * 0.50), (r * 0.17, h * 0.50), (r * 0.21, h * 0.40), (r * 0.46, h * 0.36), (r * 0.52, h * 0.70), (r * 0.60, h * 0.76), (r * 0.62, h * 0.66),
            (r * 0.58, h * 0.30), (r * 0.58, -h * 0.5), (0.0, -h * 0.5)]
    pb = p_lathe(prof, max(16, int(20 * detail))); xf(pb, (x, y, z), rot); m.add(pb, mi=I['steel_charcoal'], rgba=rim)
    pb = p_lathe([(r * 0.43, h * 0.375), (r * 0.5, h * 0.39), (r * 0.5, h * 0.33), (r * 0.43, h * 0.33)], 24); xf(pb, (x, y, z), rot); m.add(pb, mi=I['steel_charcoal'], rgba=(0.03, 0.03, 0.035, 1))
    nb = bmesh.new(); hb = bmesh.new()
    for k in range(6):
        a = k * math.pi / 3 + 0.3; px, py = math.cos(a) * r * 0.29, math.sin(a) * r * 0.29
        bmesh.ops.create_cone(nb, cap_ends=True, segments=6, radius1=r * 0.042, radius2=r * 0.042, depth=0.03, matrix=Matrix.Translation(Vector((px, py, h * 0.56))))
    xf(nb, (x, y, z), rot); m.add(nb, mi=I['steel_charcoal'], rgba=(0.62, 0.62, 0.64, 1))
    hc = p_lathe([(0.0, h * 0.62), (r * 0.09, h * 0.60), (r * 0.12, h * 0.52), (r * 0.14, h * 0.47), (0.0, h * 0.47)], 18); xf(hc, (x, y, z), rot); m.add(hc, mi=I['steel_charcoal'], rgba=(0.36, 0.37, 0.4, 1))
    vs = p_cyl(0.008, 0.03, 6); xf(vs, (math.cos(1.0) * r * 0.5, math.sin(1.0) * r * 0.5, h * 0.42), (0, 0, 0)); xf(vs, (x, y, z), rot); m.add(vs, mi=I['rubber'], rgba=(0.02, 0.02, 0.02, 1))

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

def panel_yz(m, pts, x0, x1, bevel=0.0, mi=None, rgba=None):
    """Polygon given in (y, z) extruded across x0..x1 (rear faces, front fascias, hazard stripes)."""
    pb = p_panel_xz(pts, -x1, -x0, bevel); xf(pb, (0, 0, 0), (0, 0, math.pi / 2)); return m.add(pb, mi=mi, rgba=rgba)

def hazard_band(m, x, y0, y1, z0, z1, side=1, w=0.07, slant=0.07, t=0.004):
    """Yellow/black chevron band on a face whose normal is +x (side=1) or -x (side=-1)."""
    xa, xb = (x, x + t) if side > 0 else (x - t, x)
    m.rbox((xa + xb) / 2, (y0 + y1) / 2, (z0 + z1) / 2, t, y1 - y0, z1 - z0, 0.0, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.05, 1))
    y = y0 - slant; k = 0
    while y < y1:
        ya, yb = y, y + w; pts = [(ya, z0), (yb, z0), (yb + slant, z1), (ya + slant, z1)]
        pts = [(min(max(a, y0), y1), b) for a, b in pts]
        if abs(pts[0][0] - pts[1][0]) + abs(pts[2][0] - pts[3][0]) > 0.01: panel_yz(m, pts, xa + (t if side > 0 else 0) * 0.5, xb + (t if side > 0 else 0) * 0.5 + 0.0005, 0.0, I['signage'], (0.95, 0.72, 0.05, 1))
        y += w * 2; k += 1

def forklift(F, P, rgba=(0.85, 0.62, 0.06, 1)):
    """Counterbalance forklift, ~2.0 m body + forks: chamfered counterweight with tow pin and tail lamps, hinged louvred hood with seat, tubular ROPS guard, steering column and levers,
    channel-section mast with chains, lift and tilt rams, carriage with backrest and tapered L forks, fenders, step plate, hoses, beacon."""
    m = lowpoly_boxes(mb(F)); PA = I['paint']; ST = I['steel_charcoal']; BR = I['steel_brushed']; PL = I['plastic']; RB = I['rubber']; EM = I['emissive']; GL = I['glass']
    org = rgba; orgd = tuple(c * 0.74 for c in rgba[:3]) + (1,); orgl = tuple(min(1, c * 1.08) for c in rgba[:3]) + (1,)
    dk = (0.06, 0.06, 0.07, 1); gr = (0.2, 0.21, 0.23, 1); ch = (0.62, 0.64, 0.67, 1); blk = (0.1, 0.1, 0.11, 1)
    # ---- chassis, axles
    m.rbox(-0.2, 0, 0.36, 1.7, 0.74, 0.2, 0.03, mi=ST, rgba=dk)
    m.rbox(0.2, 0, 0.42, 0.5, 0.8, 0.22, 0.04, mi=ST, rgba=gr)                                          # drive axle housing
    m.between((0.35, -0.5, 0.3), (0.35, 0.5, 0.3), 0.055, seg=10, mi=ST, rgba=dk); m.sphere(0.35, 0, 0.3, 0.13, 0.11, 0.11, rings=6, seg=10, mi=ST, rgba=gr)
    m.between((-1.0, -0.46, 0.26), (-1.0, 0.46, 0.26), 0.04, seg=8, mi=ST, rgba=dk)
    for sy in (-1, 1):
        m.rbox(-1.0, sy * 0.38, 0.4, 0.14, 0.05, 0.28, 0.01, mi=ST, rgba=gr)                              # steer knuckle
        m.between((-0.9, sy * 0.46, 0.22), (-0.62, sy * 0.3, 0.3), 0.015, seg=6, mi=ST, rgba=ch)            # tie rod
    # ---- counterweight: cheeks with wheel arches + solid middle + chamfered rear profile
    cw = [(-1.34, 0.26), (-1.34, 0.92), (-1.30, 1.06), (-1.22, 1.15), (-1.12, 1.2), (-0.72, 1.2), (-0.72, 0.26)] + arc_pts(-1.0, 0.26, 0.31, 0, 180, 8)[::-1][:-1][::-1][::-1]
    cw = [(-1.34, 0.26), (-1.34, 0.92), (-1.30, 1.06), (-1.22, 1.15), (-1.12, 1.2), (-0.72, 1.2), (-0.72, 0.26), (-0.69, 0.26)] + arc_pts(-1.0, 0.26, 0.31, 0, 180, 9) + [(-1.31, 0.26)]
    for sy in (-1, 1):
        panel(m, cw, sy * 0.36, sy * 0.55, 0.012, PA, orgd)
        panel(m, [(-0.69, 0.57), (-1.31, 0.57), (-1.31, 0.64), (-0.69, 0.64)], sy * 0.355, sy * 0.555, 0.006, PA, org)    # arch crown stiffener
    panel(m, [(-1.34, 0.45), (-1.34, 0.92), (-1.30, 1.06), (-1.22, 1.15), (-1.12, 1.2), (-0.72, 1.2), (-0.72, 0.45)], -0.36, 0.36, 0.014, PA, org)
    m.rbox(-1.345, 0, 0.8, 0.012, 1.0, 0.016, 0, mi=ST, rgba=dk); m.rbox(-1.345, 0, 1.02, 0.012, 1.0, 0.016, 0, mi=ST, rgba=dk)  # cast ribs
    m.rbox(-0.72, 0, 1.0, 0.012, 1.08, 0.46, 0, mi=ST, rgba=dk)                                         # seam to hood
    hazard_band(m, -1.347, -0.5, 0.5, 0.52, 0.74, side=-1)
    for sy in (-1, 1):
        m.rbox(-1.36, sy * 0.42, 0.96, 0.04, 0.12, 0.1, 0.015, mi=ST, rgba=dk)                             # tail lamp housing
        m.rbox(-1.385, sy * 0.42, 0.96, 0.02, 0.09, 0.07, 0.01, mi=EM, rgba=(0.85, 0.06, 0.04, 1))
        m.torus(-1.0, sy * 0.28, 1.215, 0.045, 0.011, ns=12, nt=6, mi=ST, rgba=ch)                           # lifting eyes
    m.rbox(-1.39, 0, 0.5, 0.1, 0.3, 0.1, 0.012, mi=ST, rgba=gr)                                            # tow plate
    m.cylz(-1.43, 0, 0.42, 0.62, 0.02, seg=10, mi=ST, rgba=ch); m.torus(-1.43, 0, 0.64, 0.03, 0.007, ns=12, nt=6, mi=ST, rgba=ch)   # tow pin + clip
    m.rbox(-1.35, -0.18, 1.12, 0.018, 0.2, 0.09, 0, mi=I['signage'], rgba=(0.7, 0.72, 0.74, 1))        # data plate
    # ---- hood (engine cover) with seams, louvres and hinges
    m.rbox(-0.4, 0, 0.78, 0.64, 0.8, 0.42, 0.04, mi=PA, rgba=org)
    m.rbox(-0.4, 0, 1.0, 0.66, 0.84, 0.05, 0.02, mi=PA, rgba=orgl)                                         # lid
    m.rbox(-0.4, 0, 1.026, 0.6, 0.78, 0.012, 0, mi=ST, rgba=dk)                                        # lid seam
    for sy in (-1, 1):
        for k in range(6): m.rbox(-0.55 + k * 0.055, sy * 0.405, 0.8, 0.026, 0.016, 0.22, 0, mi=ST, rgba=dk)   # side louvres
        m.rbox(-0.2, sy * 0.405, 0.8, 0.012, 0.014, 0.34, 0, mi=ST, rgba=dk)                            # panel gap
        m.cylz(-0.71, sy * 0.28, 0.99, 1.04, 0.013, seg=8, mi=ST, rgba=ch); m.rbox(-0.69, sy * 0.28, 1.02, 0.06, 0.07, 0.012, 0, mi=ST, rgba=gr)   # hinges
    m.rbox(-0.07, 0, 0.99, 0.03, 0.08, 0.03, 0, mi=ST, rgba=ch)                                       # latch
    m.rbox(-0.4, 0, 0.55, 0.7, 0.82, 0.05, 0.015, mi=PA, rgba=orgd)                                        # skirt
    # ---- mid body, floor, cowl, step
    for sy in (-1, 1):
        panel(m, [(-0.7, 0.36), (0.6, 0.36), (0.6, 0.6), (-0.7, 0.6)], sy * 0.36, sy * 0.405, 0.008, PA, orgd)
        m.rbox(-0.2, sy * 0.55, 0.37, 0.5, 0.2, 0.035, 0.012, mi=BR, rgba=(0.5, 0.5, 0.52, 1))             # step plate
        for k in range(8): m.rbox(-0.4 + k * 0.06, sy * 0.55, 0.395, 0.014, 0.17, 0.008, 0, mi=ST, rgba=dk)
        m.between((-0.38, sy * 0.45, 0.36), (-0.38, sy * 0.41, 0.5), 0.015, seg=6, mi=ST, rgba=dk); m.between((-0.02, sy * 0.45, 0.36), (-0.02, sy * 0.41, 0.5), 0.015, seg=6, mi=ST, rgba=dk)
    m.rbox(0.25, 0, 0.57, 0.8, 0.8, 0.05, 0.012, mi=ST, rgba=gr)                                           # floor plate
    for k in range(10): m.rbox(0.0 + k * 0.05, 0, 0.6, 0.012, 0.6, 0.008, 0, mi=ST, rgba=dk)
    m.rbox(0.46, 0, 0.82, 0.3, 0.8, 0.52, 0.05, mi=PA, rgba=org)                                           # cowl
    m.rbox(0.44, 0, 1.08, 0.28, 0.76, 0.05, 0.02, mi=PA, rgba=orgl)                                        # dash top
    m.rbox(0.56, 0, 0.64, 0.02, 0.5, 0.12, 0, mi=ST, rgba=dk)                                          # front grille slots
    for k in range(5): m.rbox(0.575, 0, 0.6 + k * 0.025, 0.012, 0.44, 0.008, 0, mi=ST, rgba=blk)
    for sy in (-1, 1):
        m.rbox(0.6, sy * 0.28, 0.82, 0.05, 0.12, 0.09, 0.015, mi=ST, rgba=dk); m.add(p_cyl(0.04, 0.02, 14), (0.63, sy * 0.28, 0.82), (0, math.pi / 2, 0), mi=EM, rgba=(1.0, 0.92, 0.7, 1))  # head lamps
        m.rbox(0.47, sy * 0.405, 0.84, 0.012, 0.014, 0.36, 0, mi=ST, rgba=dk)
    m.rbox(0.48, 0.405, 0.9, 0.1, 0.014, 0.05, 0, mi=I['signage'], rgba=(0.75, 0.77, 0.8, 1))            # service plate
    # ---- wheels, fenders
    for sy in (-1, 1):
        wheel(m, 0.35, sy * 0.52, 0.3, r=0.3, w=0.24, flip=sy, rim=(0.55, 0.12, 0.08, 1) if False else (0.7, 0.55, 0.12, 1))
        wheel(m, -1.0, sy * 0.46, 0.26, r=0.26, w=0.2, flip=sy, rim=(0.7, 0.55, 0.12, 1), detail=0.8)
        fe = arc_pts(0.35, 0.3, 0.375, 0, 180, 10) + arc_pts(0.35, 0.3, 0.345, 180, 0, 10)
        panel(m, fe, sy * 0.4, sy * 0.66, 0.006, PA, org)
        m.rbox(0.35, sy * 0.53, 0.686, 0.64, 0.3, 0.02, 0, mi=PA, rgba=orgl)                           # fender top shelf
        m.rbox(0.35, sy * 0.53, 0.72, 0.6, 0.012, 0.05, 0, mi=PA, rgba=orgd) if False else None
    # ---- operator: seat, belt, steering, levers, pedals, props
    m.rbox(-0.36, 0, 1.075, 0.44, 0.46, 0.05, 0.015, mi=ST, rgba=dk)                                       # slide rails
    m.cushion(-0.36, 0, 1.15, 0.44, 0.44, 0.1, r=0.035, levels=1, mi=I['fabric'], rgba=(0.1, 0.1, 0.12, 1))
    m.cushion(-0.58, 0, 1.45, 0.1, 0.42, 0.56, r=0.04, levels=1, rot=(0, -0.14, 0), mi=I['fabric'], rgba=(0.1, 0.1, 0.12, 1))
    m.rbox(-0.62, 0, 1.45, 0.02, 0.38, 0.5, 0.01, mi=ST, rgba=dk, rot=(0, -0.14, 0))                        # backrest shell
    for sy in (-1, 1): m.rbox(-0.4, sy * 0.25, 1.3, 0.3, 0.04, 0.03, 0.01, mi=I['fabric'], rgba=(0.14, 0.14, 0.15, 1)) if sy > 0 else m.rbox(-0.4, sy * 0.25, 1.26, 0.2, 0.04, 0.03, 0.01, mi=I['fabric'], rgba=(0.14, 0.14, 0.15, 1))    # arm rests
    m.between((-0.5, 0.2, 1.5), (-0.28, -0.12, 1.2), 0.018, seg=6, mi=I['fabric'], rgba=(0.55, 0.14, 0.06, 1))   # seat belt
    m.rbox(-0.3, -0.12, 1.2, 0.07, 0.04, 0.03, 0, mi=ST, rgba=ch)
    m.sphere(-0.32, 0.06, 1.23, 0.1, 0.1, 0.07, rings=6, seg=12, mi=PL, rgba=(0.95, 0.78, 0.08, 1))        # hard hat on the seat
    m.cylz(-0.32, 0.06, 1.2, 1.205, 0.12, seg=14, mi=PL, rgba=(0.95, 0.78, 0.08, 1)); m.rbox(-0.2, 0.06, 1.206, 0.07, 0.1, 0.01, 0, mi=PL, rgba=(0.9, 0.72, 0.06, 1))
    col = [(0.42, 0.0, 0.98), (0.24, 0.0, 1.38)]
    m.between(col[0], col[1], 0.022, seg=10, mi=ST, rgba=blk); m.cylz(0.42, 0, 0.98, 1.1, 0.04, seg=10, r2=0.03, mi=PL, rgba=blk)
    m.torus(0.22, 0, 1.43, 0.17, 0.016, ns=24, nt=8, rot=(0, -0.55, 0), mi=PL, rgba=blk)
    for a in (0, 2.1, 4.2): m.between((0.22, 0, 1.43), (0.22 + 0.17 * math.cos(a) * math.sin(-0.55) * 0 + 0.0, 0.17 * math.cos(a), 1.43 + 0.17 * math.sin(a) * 0.82), 0.008, seg=6, mi=ST, rgba=blk)
    m.sphere(0.27, 0.0, 1.405, 0.025, 0.025, 0.04, rings=4, seg=8, mi=PL, rgba=(0.8, 0.8, 0.8, 1)); m.cylz(0.1, 0.12, 1.43, 1.431, 0.0, seg=3, mi=PL, rgba=blk) if False else None
    m.rbox(0.38, 0, 1.12, 0.12, 0.34, 0.05, 0.01, mi=ST, rgba=dk)                                           # dash cluster
    m.rbox(0.355, 0, 1.135, 0.018, 0.2, 0.03, 0, mi=I['screen'], rgba=(0.4, 0.8, 0.5, 1))
    for k in range(3): m.add(p_cyl(0.008, 0.01, 8), (0.352, -0.1 + k * 0.1, 1.105), (0, math.pi / 2, 0), mi=EM, rgba=[(0.2, 0.9, 0.3, 1), (1.0, 0.6, 0.1, 1), (0.9, 0.12, 0.08, 1)][k])
    for k, c in enumerate(((0.8, 0.1, 0.06, 1), (0.1, 0.1, 0.12, 1), (0.9, 0.6, 0.08, 1))):                 # hydraulic levers
        yy = -0.28 + k * 0.07; m.cylz(0.42, yy, 1.1, 1.13, 0.016, seg=8, mi=RB, rgba=blk)
        m.between((0.42, yy, 1.12), (0.37 - k * 0.01, yy, 1.4), 0.007, seg=6, mi=ST, rgba=ch); m.sphere(0.37 - k * 0.01, yy, 1.42, 0.02, rings=5, seg=8, mi=PL, rgba=c)
    m.between((0.38, 0.3, 1.1), (0.28, 0.3, 1.26), 0.008, seg=6, mi=ST, rgba=ch); m.sphere(0.28, 0.3, 1.27, 0.02, rings=5, seg=8, mi=RB, rgba=blk)    # parking brake
    for k, yy in enumerate((-0.14, 0.04, 0.17)):                                                           # pedals
        m.rbox(0.3, yy, 0.65, 0.07, 0.09 if k < 2 else 0.07, 0.025, 0, rot=(0, -0.7, 0), mi=ST, rgba=(0.2, 0.2, 0.22, 1)); m.between((0.33, yy, 0.64), (0.4, yy, 0.78), 0.008, seg=6, mi=ST, rgba=dk)
    m.rbox(0.4, -0.2, 1.125, 0.3, 0.2, 0.014, 0, rot=(0.0, 0.0, 0.3), mi=PL, rgba=(0.42, 0.28, 0.14, 1)); m.rbox(0.4, -0.2, 1.135, 0.27, 0.17, 0.004, 0, rot=(0.0, 0.0, 0.3), mi=PL, rgba=(0.86, 0.86, 0.82, 1))   # clipboard
    m.rbox(0.52, -0.1, 1.14, 0.04, 0.06, 0.012, 0, rot=(0, 0, 0.3), mi=ST, rgba=ch)
    # extinguisher on the hood side
    m.cylz(-0.62, 0.42, 0.72, 1.0, 0.055, seg=12, bevel=0.012, mi=PL, rgba=(0.78, 0.08, 0.05, 1)); m.cylz(-0.62, 0.42, 1.0, 1.04, 0.025, seg=8, mi=ST, rgba=ch); m.rbox(-0.6, 0.42, 1.06, 0.06, 0.02, 0.03, 0, mi=ST, rgba=blk)
    m.between((-0.58, 0.42, 1.05), (-0.5, 0.45, 0.82), 0.007, seg=6, mi=RB, rgba=blk)
    for z in (0.78, 0.94): m.rbox(-0.62, 0.42, z, 0.14, 0.14, 0.02, 0, mi=ST, rgba=dk)
    # ---- ROPS overhead guard (tubular)
    tr = 0.024
    for sy in (-1, 1):
        fr = [(0.5, sy * 0.43, 0.98), (0.5, sy * 0.43, 1.62), (0.6, sy * 0.43, 2.04)]; rr = [(-0.62, sy * 0.43, 1.03), (-0.62, sy * 0.43, 1.7), (-0.7, sy * 0.43, 2.04)]
        tube(m, fr, tr, seg=8, mi=ST, rgba=(0.09, 0.09, 0.1, 1)); tube(m, rr, tr, seg=8, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
        tube(m, [(0.6, sy * 0.43, 2.04), (-0.7, sy * 0.43, 2.04)], tr, seg=8, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
        for p in (fr[0], rr[0]): m.rbox(p[0], p[1], p[2] + 0.01, 0.1, 0.1, 0.02, 0, mi=ST, rgba=gr); m.cylz(p[0] + 0.03, p[1] + 0.03, p[2] + 0.02, p[2] + 0.04, 0.012, seg=6, mi=ST, rgba=ch)
        m.between((0.5, sy * 0.43, 1.6), (-0.62, sy * 0.43, 1.66), 0.014, seg=6, mi=ST, rgba=(0.12, 0.12, 0.13, 1))          # side rail
    tube(m, [(0.6, -0.43, 2.04), (0.6, 0.43, 2.04)], tr, seg=8, mi=ST, rgba=(0.09, 0.09, 0.1, 1)); tube(m, [(-0.7, -0.43, 2.04), (-0.7, 0.43, 2.04)], tr, seg=8, mi=ST, rgba=(0.09, 0.09, 0.1, 1))
    tube(m, [(-0.62, -0.43, 1.7), (-0.62, 0.43, 1.7)], 0.016, seg=6, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
    for k in range(9): m.rbox(0.0, -0.4 + k * 0.1, 2.05, 1.3, 0.035, 0.012, 0, mi=ST, rgba=(0.1, 0.1, 0.11, 1))   # roof slats
    for x in (-0.4, 0.1, 0.5): m.rbox(x, 0, 2.06, 0.03, 0.88, 0.014, 0, mi=ST, rgba=(0.1, 0.1, 0.11, 1))
    for sy in (-1, 1):
        m.add(p_cyl(0.045, 0.07, 14), (0.62, sy * 0.3, 2.1), (0, math.pi / 2, 0), mi=EM, rgba=(1.0, 0.95, 0.8, 1)); m.cylz(0.58, sy * 0.3, 2.06, 2.14, 0.055, seg=10, r2=0.04, mi=ST, rgba=dk) if False else None
        m.rbox(0.58, sy * 0.3, 2.1, 0.05, 0.12, 0.1, 0.02, mi=ST, rgba=dk)
    m.cylz(-0.7, 0.3, 2.06, 2.16, 0.025, seg=8, mi=ST, rgba=dk); m.add(p_cyl(0.07, 0.07, 14), (-0.7, 0.3, 2.22), mi=EM, rgba=(1.0, 0.55, 0.05, 1)); m.sphere(-0.7, 0.3, 2.255, 0.07, 0.07, 0.045, rings=5, seg=14, mi=EM, rgba=(1.0, 0.55, 0.05, 1))   # beacon
    m.rbox(0.45, 0.47, 1.55, 0.04, 0.1, 0.16, 0.012, mi=PL, rgba=dk); m.between((0.5, 0.45, 1.55), (0.46, 0.45, 1.55), 0.008, seg=6, mi=ST, rgba=ch) # mirror
    m.between((0.5, 0.43, 1.2), (0.5, 0.43, 1.0), 0.0, seg=3, mi=ST, rgba=dk) if False else None
    tube(m, [(0.37, 0.44, 0.82), (0.37, 0.52, 0.82), (0.37, 0.52, 1.28), (0.37, 0.44, 1.28)], 0.014, seg=8, mi=PL, rgba=(0.95, 0.75, 0.06, 1))     # hand grab
    # ---- mast: C-channel rails, cross members, rams, chains
    for sy in (-1, 1):
        y = sy * 0.31
        m.rbox(0.775, y, 1.06, 0.022, 0.1, 2.0, 0, mi=ST, rgba=gr)
        for fy in (-1, 1): m.rbox(0.835, y + fy * 0.04, 1.06, 0.1, 0.022, 2.0, 0, mi=ST, rgba=gr)
        m.rbox(0.9, y, 1.2, 0.022, 0.07, 1.9, 0, mi=ST, rgba=(0.26, 0.27, 0.29, 1))
        for fy in (-1, 1): m.rbox(0.945, y + fy * 0.025, 1.2, 0.07, 0.016, 1.9, 0, mi=ST, rgba=(0.26, 0.27, 0.29, 1))
        m.rbox(0.77, sy * 0.38, 0.12, 0.2, 0.06, 0.12, 0.01, mi=ST, rgba=gr)                                # mast foot pivot
    for z in (0.3, 0.75, 1.5, 2.04): m.rbox(0.8, 0, z, 0.05, 0.6, 0.05, 0, mi=ST, rgba=gr)
    for z in (0.35, 1.05, 2.13): m.rbox(0.93, 0, z, 0.05, 0.58, 0.05, 0, mi=ST, rgba=(0.26, 0.27, 0.29, 1))
    m.cylz(0.78, 0.0, 0.2, 1.2, 0.05, seg=12, mi=ST, rgba=(0.2, 0.21, 0.22, 1)); m.cylz(0.78, 0.0, 1.2, 2.1, 0.026, seg=10, mi=BR, rgba=ch)     # lift ram
    m.cylz(0.78, 0, 1.2, 1.24, 0.058, seg=12, mi=ST, rgba=gr)
    m.add(p_cyl(0.07, 0.05, 14), (0.84, 0, 2.18), (math.pi / 2, 0, 0), mi=ST, rgba=ch)                      # chain sheave
    for sy in (-1, 1):
        yc = sy * 0.1
        m.between((0.9, yc, 0.8), (0.9, yc, 2.18), 0.009, seg=6, mi=ST, rgba=(0.3, 0.3, 0.32, 1))
        for k in range(14): m.rbox(0.9, yc, 0.9 + k * 0.095, 0.022, 0.034, 0.03, 0, mi=ST, rgba=(0.38, 0.38, 0.4, 1))
        a, b = (0.78, sy * 0.31, 0.0), (0.0, 0.0, 0.0)
        m.between((0.805, sy * 0.35, 0.6), (0.805, sy * 0.35, 0.74), 0.01, seg=6, mi=ST, rgba=ch)
        # tilt rams: from the cowl to the mast
        m.between((0.5, sy * 0.36, 0.78), (0.74, sy * 0.355, 1.02), 0.032, seg=10, mi=ST, rgba=(0.2, 0.21, 0.22, 1)); m.between((0.74, sy * 0.355, 1.02), (0.82, sy * 0.355, 1.1), 0.018, seg=8, mi=BR, rgba=ch)
        m.sphere(0.5, sy * 0.36, 0.78, 0.04, rings=5, seg=8, mi=ST, rgba=gr); m.sphere(0.82, sy * 0.355, 1.1, 0.03, rings=5, seg=8, mi=ST, rgba=gr)
    # ---- carriage, backrest, forks
    for z in (0.2, 0.78): m.rbox(0.97, 0, z, 0.07, 0.98, 0.06, 0.012, mi=ST, rgba=gr)
    for sy in (-1, 1): m.rbox(0.95, sy * 0.46, 0.5, 0.07, 0.06, 0.64, 0.012, mi=ST, rgba=gr)
    m.rbox(0.95, 0, 0.5, 0.05, 0.86, 0.04, 0, mi=ST, rgba=gr)
    for sy in (-1, 1): m.add(p_cyl(0.035, 0.05, 12), (0.9, sy * 0.4, 0.5), (math.pi / 2, 0, 0), mi=ST, rgba=ch)  # rollers
    for k in range(8): m.rbox(1.0, -0.455 + k * 0.13, 1.17, 0.035, 0.035, 0.78, 0, mi=ST, rgba=(0.12, 0.12, 0.13, 1))   # load backrest
    for z in (0.84, 1.56): m.rbox(1.0, 0, z, 0.045, 1.0, 0.045, 0.01, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
    for sy in (-1, 1): m.rbox(1.0, sy * 0.5, 1.2, 0.045, 0.045, 0.78, 0.01, mi=ST, rgba=(0.12, 0.12, 0.13, 1))
    for sy in (-1, 1):
        y = sy * 0.3; fk = [(0.99, 0.82), (1.07, 0.82), (1.07, 0.075), (1.5, 0.062), (2.0, 0.034), (2.0, 0.018), (0.99, 0.018)]
        panel(m, fk, y - 0.055, y + 0.055, 0.004, I['steel_brushed'], (0.34, 0.34, 0.36, 1))
        m.rbox(1.02, y, 0.8, 0.05, 0.1, 0.06, 0.01, mi=ST, rgba=gr)                                         # fork hook
    # ---- hoses
    for sy in (-1, 1):
        tube(m, bezier((0.62, sy * 0.1, 0.62), (0.75, sy * 0.17, 0.3), (0.74, sy * 0.15, 0.82), 6) , 0.011, seg=6, mi=RB, rgba=(0.03, 0.03, 0.035, 1), joints=False)
        tube(m, bezier((0.74, sy * 0.15, 0.85), (0.9, sy * 0.2, 1.0), (0.92, sy * 0.15, 0.82), 6), 0.011, seg=6, mi=RB, rgba=(0.03, 0.03, 0.035, 1), joints=False)
    tube(m, bezier((0.72, 0.38, 1.0), (0.8, 0.45, 1.3), (0.78, 0.36, 1.9), 6), 0.01, seg=6, mi=RB, rgba=(0.03, 0.03, 0.035, 1), joints=False)
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
