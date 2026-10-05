"""Site/refit kit for the hall: jersey barriers, sandbags, scaffold tower, plasterboard, ladder, bags, buckets, rubble."""
from fe_kit import *
from fe_assets_int import STD, I, mb

def jersey(F, P):
    prof = [(-0.3, 0.0), (0.3, 0.0), (0.3, 0.1), (0.2, 0.28), (0.12, 0.62), (0.1, 0.8), (-0.1, 0.8), (-0.12, 0.62), (-0.2, 0.28), (-0.3, 0.1)]
    m = mb(F)
    pb = p_ring_prism([(y, z) for y, z in prof], 2.0, 0.012); xf(pb, (0, 0, 0), (0, 0, 0))
    # profile is in (x,y)=(depth,height); rotate so it extrudes along X with height along Z
    pb2 = bmesh.new(); vs = [pb2.verts.new(Vector((0, y, z))) for y, z in prof]; f = pb2.faces.new(vs); r = bmesh.ops.extrude_face_region(pb2, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.x += 2.0
    for v in pb2.verts: v.co.x -= 1.0
    bmesh.ops.recalc_face_normals(pb2, faces=pb2.faces[:]); bmesh.ops.bevel(pb2, geom=pb2.edges[:], offset=0.012, segments=1, affect='EDGES')
    pb.free()
    m.add(pb2, mi=I['concrete_slab'])
    for k in range(4): m.rbox(-0.75 + k * 0.5, -0.131, 0.5, 0.2, 0.004, 0.32, 0.001, rot=(-0.12, 0, 0), mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1)) if False else None
    for sy in (-1, 1):
        for k in range(4): m.rbox(-0.75 + k * 0.5, sy * 0.14, 0.52, 0.22, 0.008, 0.3, 0.001, rot=(sy * -0.12 * 0.0, 0, 0), mi=I['signage'], rgba=(0.92, 0.72, 0.06, 1) if k % 2 == 0 else (0.1, 0.1, 0.1, 1)) if False else None
    for sy in (-1, 1):
        for k in range(4): m.rbox(-0.75 + k * 0.5, sy * 0.113, 0.5, 0.2, 0.006, 0.28, 0.001, mi=I['signage'], rgba=(0.88, 0.1, 0.08, 1) if k % 2 == 0 else (0.92, 0.92, 0.9, 1))
    m.cylz(0.9, 0.0, 0.8, 0.8, 0.0, seg=3) if False else None
    return m.finish('proto_jersey', P)

def sandbags(F, P, seed=0):
    m = mb(F); rnd = random.Random(seed)
    for r in range(3):
        for c in range(4 - (r % 2)):
            col = (0.4 + rnd.uniform(-0.04, 0.04), 0.34 + rnd.uniform(-0.03, 0.03), 0.22, 1)
            m.add(p_rbox(0.5, 0.3, 0.14, 0.06, 2), ((c - 1.5 + 0.5 * (r % 2)) * 0.5, rnd.uniform(-0.02, 0.02), 0.08 + r * 0.14), (rnd.uniform(-0.05, 0.05), rnd.uniform(-0.04, 0.04), rnd.uniform(-0.1, 0.1)), mi=I['fabric'], rgba=col)
    return m.finish(f'proto_sandbags_{seed}', P)

def scaffold(F, P, w=1.6, d=1.0, h=3.0, levels=(0.0, 1.0, 2.0)):
    m = mb(F); steel = (0.7, 0.72, 0.74, 1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.cylz(sx * w / 2, sy * d / 2, 0.0, h + 0.9, 0.024, seg=10, mi=I['steel_charcoal'], rgba=steel)
            m.cylz(sx * w / 2, sy * d / 2, 0.0, 0.06, 0.05, seg=10, mi=I['steel_charcoal'], rgba=(0.2, 0.2, 0.22, 1))
    for z in (0.3,) + tuple(l + 1.0 for l in levels[:-1]) + (h,):
        for sy in (-1, 1): m.between((-w / 2, sy * d / 2, z), (w / 2, sy * d / 2, z), 0.02, seg=8, mi=I['steel_charcoal'], rgba=steel)
        for sx in (-1, 1): m.between((sx * w / 2, -d / 2, z), (sx * w / 2, d / 2, z), 0.02, seg=8, mi=I['steel_charcoal'], rgba=steel)
    for k in range(len(levels) - 1):
        z0 = levels[k] + 0.3; z1 = levels[k] + 1.3
        for sy in (-1, 1): m.between((-w / 2, sy * d / 2, z0), (w / 2, sy * d / 2, z1), 0.014, seg=6, mi=I['steel_charcoal'], rgba=steel)
    for z in (h - 0.0,):
        for i in range(4): m.rbox(0, -d / 2 + 0.12 + i * 0.25, z + 0.03, w + 0.1, 0.22, 0.04, 0.006, mi=I['timber'], rgba=(0.6, 0.45, 0.25, 1))
    for sx in (-1, 1):
        m.between((sx * w / 2, -d / 2, h + 0.9), (sx * w / 2, d / 2, h + 0.9), 0.018, seg=8, mi=I['steel_charcoal'], rgba=steel)
        m.between((sx * w / 2, -d / 2, h + 0.45), (sx * w / 2, d / 2, h + 0.45), 0.018, seg=8, mi=I['steel_charcoal'], rgba=steel)
    return m.finish('proto_scaffold', P)

def plasterboard(F, P):
    m = mb(F)
    for k in range(10): m.rbox(0, 0, 0.1 + k * 0.0125 + 0.0, 2.4, 1.2, 0.0125, 0.002, mi=I['plastic'], rgba=(0.78, 0.76, 0.7, 1))
    m.rbox(0, 0, 0.04, 2.5, 1.25, 0.08, 0.006, mi=I['timber'], rgba=(0.5, 0.36, 0.2, 1))
    m.rbox(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0) if False else None
    m.rbox(0, 0, 0.27, 2.45, 0.04, 0.012, 0.002, mi=I['plastic'], rgba=(0.1, 0.1, 0.1, 1)) if False else None
    return m.finish('proto_plasterboard', P)

def ladder(F, P, h=2.4):
    m = mb(F); alu = (0.7, 0.72, 0.74, 1)
    for sx in (-1, 1): m.between((sx * 0.22, 0.0, 0.0), (sx * 0.2, -0.65, h), 0.022, seg=8, mi=I['steel_charcoal'], rgba=alu)
    for k in range(8):
        t = (k + 0.7) / 8.7; m.between((-0.22 + 0.02 * t, -0.65 * t, h * t), (0.22 - 0.02 * t, -0.65 * t, h * t), 0.012, seg=6, mi=I['steel_charcoal'], rgba=alu)
    for sx in (-1, 1): m.rbox(sx * 0.22, 0.0, 0.02, 0.07, 0.07, 0.04, 0.01, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_ladder', P)

def bucket(F, P, rgba=(0.85, 0.8, 0.1, 1)):
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.12, 0.0), (0.14, 0.02), (0.17, 0.3), (0.175, 0.31), (0.165, 0.31), (0.13, 0.04), (0.0, 0.03)], seg=24, mi=I['plastic'], rgba=rgba)
    m.add(p_torus(0.17, 0.006, 24, 5), (0, 0, 0.305), (0, 0, 0), mi=I['plastic'], rgba=rgba)
    return m.finish('proto_bucket', P)

def cement_bags(F, P, seed=0):
    m = mb(F); rnd = random.Random(seed)
    m.rbox(0, 0, 0.075, 1.2, 1.0, 0.15, 0.01, mi=I['timber'], rgba=(0.5, 0.36, 0.2, 1))
    for r in range(5):
        for c in range(2):
            for d in range(2):
                m.add(p_rbox(0.55, 0.38, 0.12, 0.04, 2), (-0.28 + c * 0.56 + rnd.uniform(-0.02, 0.02), -0.2 + d * 0.4 + rnd.uniform(-0.02, 0.02), 0.22 + r * 0.115), (0, 0, rnd.uniform(-0.08, 0.08)), mi=I['plastic'], rgba=(0.72, 0.7, 0.62, 1))
    return m.finish(f'proto_cement_bags_{seed}', P)

def wheelbarrow(F, P):
    m = mb(F); y = (0.85, 0.7, 0.1, 1)
    m.add(p_rbox(0.95, 0.62, 0.3, 0.06, 2), (0.0, 0.0, 0.55), (0.0, 0.18, 0.0), mi=I['plastic'], rgba=y)
    m.add(p_cyl(0.19, 0.08, 20), (0.55, 0, 0.19), (math.pi / 2, 0, 0), mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1)); m.add(p_cyl(0.08, 0.1, 12), (0.55, 0, 0.19), (math.pi / 2, 0, 0), mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    for sy in (-1, 1):
        m.between((-0.15, sy * 0.3, 0.45), (-0.9, sy * 0.28, 0.62), 0.016, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        m.between((0.55, sy * 0.12, 0.19), (-0.1, sy * 0.3, 0.45), 0.016, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        m.between((-0.45, sy * 0.28, 0.5), (-0.5, sy * 0.28, 0.0), 0.016, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        m.rbox(-0.5, sy * 0.28, 0.01, 0.08, 0.05, 0.02, 0.006, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        m.between((-0.9, sy * 0.28, 0.62), (-1.0, sy * 0.28, 0.62), 0.024, seg=8, mi=I['rubber'], rgba=(0.03, 0.03, 0.03, 1))
    return m.finish('proto_wheelbarrow', P)

def toolbox(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.14, 0.55, 0.25, 0.28, 0.025, mi=I['plastic'], rgba=(0.7, 0.1, 0.07, 1)); m.rbox(0, 0, 0.29, 0.55, 0.25, 0.02, 0.01, mi=I['plastic'], rgba=(0.1, 0.1, 0.11, 1))
    m.between((-0.15, 0, 0.3), (0.15, 0, 0.3), 0.012, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1)); m.rbox(0, 0.126, 0.18, 0.12, 0.01, 0.04, 0.004, mi=I['steel_charcoal'], rgba=(0.5, 0.5, 0.52, 1))
    return m.finish('proto_toolbox', P)

def rubble_chunk(F, P, seed=0, size=0.35):
    """Angular broken-concrete chunk with an exposed face and a rebar stub."""
    rnd = random.Random(seed); m = mb(F)
    pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=2, radius=1.0)
    for v in res['verts']:
        k = 1.0 + rnd.uniform(-0.28, 0.28); v.co = Vector((v.co.x * size * k, v.co.y * size * 0.8 * k, v.co.z * size * 0.6 * k))
    cut = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.2, 1))).normalized(); d0 = size * 0.35
    for v in pb.verts:
        dd = v.co.dot(cut)
        if dd > d0: v.co -= cut * (dd - d0)
    for f in pb.faces: f.smooth = False
    m.add(pb, mi=I['concrete_slab'])
    if seed % 3 == 0: m.between((0, 0, size * 0.1), (cut.x * 0.2, cut.y * 0.2, size * 0.1 + 0.3), 0.007, seg=5, mi=I['steel_rust'] if 'steel_rust' in STD else I['props'], rgba=(0.35, 0.18, 0.1, 1))
    return m.finish(f'proto_rubble_{seed}', P)

def rack(F, P, seed=0, bays=2, H=2.4):
    """Pallet racking with orange beams, blue uprights and boxed stock."""
    m = mb(F); rnd = random.Random(seed); W = 1.25 * bays; D = 0.8
    up = (0.1, 0.2, 0.5, 1); beam = (0.85, 0.4, 0.06, 1)
    for k in range(bays + 1):
        for sy in (-1, 1): m.rbox(-W / 2 + k * 1.25, sy * D / 2, H / 2, 0.07, 0.07, H, 0.01, mi=I['steel_charcoal'], rgba=up)
        m.rbox(-W / 2 + k * 1.25, 0, 0.012, 0.1, D + 0.1, 0.024, 0.006, mi=I['steel_charcoal'], rgba=up)
    for z in (0.3, 1.0, 1.7):
        for sy in (-1, 1): m.rbox(0, sy * D / 2, z, W, 0.06, 0.1, 0.01, mi=I['steel_accent'], rgba=beam)
        m.rbox(0, 0, z + 0.04, W - 0.06, D - 0.1, 0.02, 0.004, mi=I['timber'], rgba=(0.5, 0.36, 0.2, 1))
        for b in range(bays):
            x0 = -W / 2 + b * 1.25 + 0.62
            for k in range(rnd.randint(1, 3)):
                m.rbox(x0 + rnd.uniform(-0.3, 0.3), rnd.uniform(-0.1, 0.1), z + 0.2 + 0.0, rnd.uniform(0.3, 0.5), rnd.uniform(0.3, 0.55), rnd.uniform(0.25, 0.5), 0.012, mi=I['plastic'], rgba=rnd.choice([(0.55, 0.4, 0.24, 1), (0.6, 0.45, 0.28, 1), (0.5, 0.5, 0.48, 1), (0.25, 0.35, 0.5, 1)]))
    return m.finish(f'proto_rack_{seed}', P)
