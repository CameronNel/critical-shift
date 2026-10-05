"""Door leaves, handles and fittings for the cafeteria openings. Leaves are prototypes hinged at their local origin (x 0..w) and instanced."""
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_yard import inst

def _hinges(m, h, steel, n=3):
    for z in [0.25, h / 2, h - 0.25][:n]: m.cylz(0.0, 0.0, z - 0.07, z + 0.07, 0.016, seg=10, mi=I['steel_charcoal'], rgba=steel)

def leaf_airlock(F, P, w=1.28, h=2.62):
    """Pressure door leaf: painted steel, hazard band, porthole, wheel handle, edge seal."""
    m = mb(F); steel = (0.55, 0.57, 0.6, 1); body = (0.34, 0.37, 0.4, 1)
    m.rbox(w / 2, 0, h / 2, w - 0.02, 0.07, h, 0.012, mi=I['props'], rgba=body)
    for z0 in (0.5, 2.0):
        for k in range(8): m.rbox(0.1 + k * (w - 0.2) / 8 + (w - 0.2) / 16, 0.037, z0, (w - 0.2) / 8 * 0.98, 0.006, 0.22, 0.001, rot=(0, 0.0, 0), mi=I['signage'], rgba=(0.92, 0.72, 0.05, 1) if k % 2 == 0 else (0.08, 0.08, 0.09, 1))
        for k in range(8): m.rbox(0.1 + k * (w - 0.2) / 8 + (w - 0.2) / 16, -0.037, z0, (w - 0.2) / 8 * 0.98, 0.006, 0.22, 0.001, mi=I['signage'], rgba=(0.92, 0.72, 0.05, 1) if k % 2 == 0 else (0.08, 0.08, 0.09, 1))
    m.add(p_torus(0.17, 0.028, 28, 8), (w * 0.62, 0.04, 1.62), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=steel)
    m.add(p_cyl(0.165, 0.02, 28), (w * 0.62, 0.0, 1.62), (math.pi / 2, 0, 0), mi=I['glass'])
    m.add(p_torus(0.1, 0.014, 24, 6), (w * 0.62, 0.075, 1.05), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=(0.8, 0.12, 0.08, 1))
    for k in range(4):
        a = k * math.pi / 2; m.between((w * 0.62, 0.075, 1.05), (w * 0.62 + math.cos(a) * 0.1, 0.075, 1.05 + math.sin(a) * 0.1), 0.01, seg=6, mi=I['steel_brushed'], rgba=(0.8, 0.12, 0.08, 1))
    m.rbox(w - 0.1, 0.055, 1.0, 0.05, 0.05, 0.3, 0.012, mi=I['steel_charcoal'], rgba=steel)
    m.rbox(w - 0.02, 0, h / 2, 0.025, 0.09, h - 0.1, 0.006, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    _hinges(m, h, steel)
    return m.finish('proto_leaf_airlock', P)

def leaf_glazed(F, P, w=1.48, h=2.5):
    """Aluminium and glass entrance leaf with push bar, kick plate and overhead closer."""
    m = mb(F); al = (0.68, 0.7, 0.72, 1)
    m.rbox(0.04, 0, h / 2, 0.08, 0.05, h, 0.008, mi=I['steel_charcoal'], rgba=al); m.rbox(w - 0.05, 0, h / 2, 0.1, 0.05, h, 0.008, mi=I['steel_charcoal'], rgba=al)
    m.rbox(w / 2, 0, h - 0.08, w, 0.05, 0.16, 0.008, mi=I['steel_charcoal'], rgba=al); m.rbox(w / 2, 0, 0.17, w, 0.05, 0.34, 0.008, mi=I['steel_charcoal'], rgba=al)
    m.rbox(w / 2, 0, 1.3, w - 0.16, 0.012, 1.85, 0.002, mi=I['glass'])
    m.between((w * 0.7, 0.07, 0.95), (w * 0.7, 0.07, 1.25), 0.016, seg=8, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    m.between((w * 0.78, 0.04, 1.1), (w * 0.9, 0.04, 1.1), 0.014, seg=8, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1)) if False else None
    m.between((w * 0.3, 0.075, 1.1), (w * 0.9, 0.075, 1.1), 0.016, seg=10, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    for x in (w * 0.3, w * 0.9): m.between((x, 0.03, 1.1), (x, 0.075, 1.1), 0.01, seg=6, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    m.rbox(w * 0.5, -0.05, h - 0.02, 0.35, 0.05, 0.05, 0.01, mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))
    _hinges(m, h, al)
    return m.finish('proto_leaf_glazed', P)

def leaf_medical(F, P, w=1.08, h=2.4):
    """Clean white hospital-style door leaf with a vision panel, green stripe and push plate."""
    m = mb(F)
    m.rbox(w / 2, 0, h / 2, w - 0.02, 0.05, h, 0.01, mi=I['plastic'], rgba=(0.88, 0.88, 0.85, 1))
    m.rbox(w / 2, 0.027, h * 0.72, w * 0.32, 0.006, 0.7, 0.003, mi=I['glass']); m.rbox(w / 2, 0.012, h * 0.72, w * 0.36, 0.01, 0.74, 0.004, mi=I['steel_brushed'], rgba=(0.55, 0.57, 0.6, 1))
    m.rbox(w / 2, 0.028, 1.15, w - 0.05, 0.006, 0.08, 0.002, mi=I['signage'], rgba=(0.1, 0.55, 0.3, 1))
    m.rbox(w * 0.78, 0.034, 1.0, 0.24, 0.012, 0.4, 0.008, mi=I['steel_brushed'], rgba=(0.75, 0.77, 0.8, 1))
    m.rbox(w / 2, 0.028, 0.22, w - 0.08, 0.008, 0.34, 0.003, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    _hinges(m, h, (0.6, 0.62, 0.64, 1), 3)
    return m.finish('proto_leaf_medical', P)

def leaf_staff(F, P, w=0.9, h=2.1):
    """Kitchen staff door: steel leaf, small window, kick plate, lever."""
    m = mb(F)
    m.rbox(w / 2, 0, h / 2, w - 0.02, 0.045, h, 0.008, mi=I['steel_brushed'], rgba=(0.62, 0.64, 0.67, 1))
    m.rbox(w / 2, 0.025, 1.55, 0.3, 0.006, 0.4, 0.004, mi=I['glass']); m.rbox(w / 2, 0.012, 1.55, 0.34, 0.01, 0.44, 0.004, mi=I['steel_charcoal'], rgba=(0.3, 0.32, 0.35, 1))
    m.rbox(w / 2, 0.026, 0.2, w - 0.06, 0.008, 0.38, 0.003, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    m.between((w - 0.1, 0.05, 1.0), (w - 0.1, 0.09, 1.0), 0.016, seg=8, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1)); m.between((w - 0.1, 0.09, 1.0), (w - 0.28, 0.09, 1.0), 0.012, seg=8, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    _hinges(m, h, (0.5, 0.5, 0.52, 1), 3)
    return m.finish('proto_leaf_staff', P)

def sliding_panel(F, P, w=1.5, h=2.55):
    m = mb(F); al = (0.68, 0.7, 0.72, 1)
    for x in (0.03, w - 0.03): m.rbox(x, 0, h / 2, 0.06, 0.05, h, 0.006, mi=I['steel_charcoal'], rgba=al)
    for z in (0.04, h - 0.04): m.rbox(w / 2, 0, z, w, 0.05, 0.08, 0.006, mi=I['steel_charcoal'], rgba=al)
    m.rbox(w / 2, 0, h / 2, w - 0.1, 0.012, h - 0.12, 0.002, mi=I['glass'])
    m.rbox(w / 2, 0.03, 1.25, 0.012, 0.01, 1.2, 0.002, mi=I['signage'], rgba=(0.9, 0.9, 0.9, 1))   # manifestation stripe
    return m.finish('proto_leaf_sliding', P)

def place_leaf(proto, name, coll, wall_axis, hx, hy, swing=0.0, interior='+', mirror=False):
    """Instance a leaf hinged at plan (hx, hy). wall_axis 'x': wall runs along x. Normal leaf extends +x (or +y on a y-wall); mirror extends -x (or -y).
    swing opens it toward the interior side ('+' = +y on an x-wall, +x on a y-wall)."""
    base = {('x', False): 0.0, ('x', True): math.pi, ('y', False): math.pi / 2, ('y', True): -math.pi / 2}[(wall_axis, mirror)]
    sign = {('x', False, '+'): 1, ('x', False, '-'): -1, ('x', True, '+'): -1, ('x', True, '-'): 1,
            ('y', False, '+'): -1, ('y', False, '-'): 1, ('y', True, '+'): 1, ('y', True, '-'): -1}[(wall_axis, mirror, interior)]
    o = inst(proto, name, hx, hy, coll, rz=base + sign * swing, support=None)
    o['support'] = 'door'; return o
