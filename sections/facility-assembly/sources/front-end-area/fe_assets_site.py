"""Site/refit kit for the hall: jersey barriers, sandbags, scaffold tower, plasterboard, ladder, bags, buckets, rubble."""
from fe_kit import *
from fe_propkit import *
from fe_assets_int import STD, I, mb

def jersey(F, P):
    """Concrete jersey barrier 2.0 m: bevelled profile, red/white chevron reflective stripes on both faces, recessed steel lifting loops, forklift pockets, end connector pins, cracks and spalled chips."""
    m = mb(F); rnd = random.Random(8)
    prof = [(-0.3, 0.0), (0.3, 0.0), (0.3, 0.1), (0.2, 0.28), (0.12, 0.62), (0.1, 0.8), (-0.1, 0.8), (-0.12, 0.62), (-0.2, 0.28), (-0.3, 0.1)]
    m.add(p_extrude_x(prof, 2.0, 0.014), mi=I['concrete_slab'])
    for sy in (-1, 1):
        for i in range(10):                                                                  # chevrons
            x0 = -0.95 + i * 0.19; red = i % 2 == 0; y = sy * 0.1065
            pts = [(x0, y, 0.63), (x0 + 0.095, y, 0.63), (x0 + 0.095 + 0.09, y, 0.785), (x0 + 0.09, y, 0.785)]
            m.add(p_quad(pts, flip=sy < 0), mi=I['signage'], rgba=(0.78, 0.07, 0.05, 1) if red else (0.88, 0.87, 0.82, 1))
        m.add(p_quad([(-1.0, sy * 0.3045, 0.1), (1.0, sy * 0.3045, 0.1), (1.0, sy * 0.2475, 0.19), (-1.0, sy * 0.2475, 0.19)], flip=sy < 0), mi=I['signage'], rgba=(0.2, 0.17, 0.13, 1))   # splash line
        for x in (-0.76, 0.76): m.add(p_quad([(x - 0.03, sy * 0.1065, 0.8), (x + 0.03, sy * 0.1065, 0.8), (x + 0.045, sy * 0.1065, 0.5), (x - 0.02, sy * 0.1065, 0.5)], flip=sy < 0), mi=I['signage'], rgba=(0.30, 0.15, 0.07, 1)) if False else None
    for x in (-0.45, 0.45): m.rbox(x, 0, 0.065, 0.22, 0.62, 0.13, 0.0, mi=I['steel_charcoal'])                  # fork pockets (dark openings through the base)
    for x in (-0.76, 0.76):
        m.rbox(x, 0, 0.8, 0.22, 0.17, 0.014, 0.003, seg=1, mi=I['steel_charcoal'])                              # lifting-loop recess plate
        m.add(p_torus(0.065, 0.015, 12, 5), (x, 0, 0.855), (math.pi / 2, 0, 0), mi=I['steel_charcoal'])         # loop
    for sx in (-1, 1):
        for z in (0.25, 0.55): m.add(p_cyl(0.02, 0.05, 6), (sx * 1.0, 0.0, z), (0, math.pi / 2, 0), mi=I['steel_charcoal'])    # connector pins
    for sy in (-1, 1):
        pts = [(-0.5, 0.35), (-0.46, 0.43), (-0.52, 0.5), (-0.47, 0.58)]
        for a, b in zip(pts[:-1], pts[1:]):
            m.between((a[0], sy * 0.158, a[1]), (b[0], sy * 0.152, b[1]), 0.004, seg=3, mi=I['steel_charcoal'], rgba=(0.02, 0.02, 0.02, 1))
    for k in range(6):                                                                                       # spalled chips at the foot
        x = rnd.uniform(-1.05, 1.05); y = rnd.choice((-1, 1)) * rnd.uniform(0.33, 0.45); s = rnd.uniform(0.03, 0.06)
        m.add(p_rock(rnd, s, 0.6, 0.3, 0), (x, y, s * 0.15), (0, 0, rnd.uniform(0, 6)), mi=I['concrete_slab'])
    weather(m, 8, dirt=0.5, dirt_h=0.25, streak=0.2, blotch=0.12)
    return m.finish('proto_jersey', P)

def sandbags(F, P, seed=0):
    """Slumped sandbag wall: pinched, flat-bottomed sacks in dark earthy burlap tones, offset rows with a leaning top bag, two loose bags in front and a split bag spilling sand."""
    m = mb(F); rnd = random.Random(seed * 13 + 5)
    cols = [(0.25, 0.19, 0.11, 1), (0.19, 0.16, 0.11, 1), (0.14, 0.12, 0.085, 1), (0.30, 0.25, 0.17, 1), (0.21, 0.17, 0.12, 1), (0.17, 0.15, 0.12, 1)]
    def bag(x, y, z, yaw, pitch=0.0, roll=0.0, L=0.5, W=0.3, T=0.15):
        c = rnd.choice(cols)
        m.add(p_bag(L, W, T, rnd), (x, y, z), (pitch, roll, yaw), mi=I['fabric'], rgba=c)
        for sx in (-1, 1):                                                                                  # tied corners
            ex = math.cos(yaw) * sx * L * 0.5; ey = math.sin(yaw) * sx * L * 0.5
            m.rbox(x + ex, y + ey, z + 0.01, 0.05, 0.075, 0.04, 0.0, rot=(0, 0, yaw), mi=I['fabric'], rgba=tuple(k * 0.8 for k in c[:3]) + (1,))
    for r in range(3):
        for c in range(4 - r):
            x = (c - (3 - r) / 2) * 0.5 + rnd.uniform(-0.03, 0.03); y = rnd.uniform(-0.04, 0.04)
            bag(x, y, 0.07 + r * 0.115, rnd.uniform(-0.08, 0.08) + (0.0 if r < 2 else rnd.uniform(-0.1, 0.1)), pitch=rnd.uniform(-0.05, 0.05) + (0.12 if r == 2 and c == 1 else 0.0), roll=rnd.uniform(-0.05, 0.05))
    bag(0.55, -0.33, 0.065, 0.4, pitch=0.05); bag(-0.35, -0.38, 0.06, -0.25, L=0.46)
    bag(-0.9, -0.15, 0.05, 1.2, pitch=0.1, roll=0.3)
    pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=1, radius=1.0)
    for v in res['verts']: v.co = Vector((v.co.x * 0.2 * (1 + rnd.uniform(-.2, .2)), v.co.y * 0.14, max(v.co.z * 0.05, -0.0)))
    add_var(m, pb, (-0.42, -0.34, 0.02), mi=I['props'], rgba=(0.5, 0.43, 0.3, 1), var=0.1, rnd=rnd)
    weather(m, seed, dirt=0.6, dirt_h=0.12, streak=0.0, blotch=0.3, top=0.15)
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
    """Plastic bucket: tapered body with moulded ribs, rolled rim and foot ring, wire handle with grip on lug ears, a label panel and a dirty fill."""
    m = mb(F)
    m.lathe([(0.0, 0.0), (0.118, 0.0), (0.126, 0.012), (0.132, 0.03), (0.15, 0.14), (0.152, 0.145), (0.158, 0.17), (0.16, 0.2), (0.168, 0.28), (0.172, 0.3), (0.18, 0.31), (0.182, 0.322), (0.172, 0.325), (0.166, 0.31),
             (0.16, 0.26), (0.14, 0.05), (0.0, 0.04)], seg=20, mi=I['plastic'], rgba=rgba)
    m.lathe([(0.0, 0.25), (0.158, 0.25), (0.0, 0.25)], seg=14, mi=I['props'], rgba=(0.10, 0.075, 0.05, 1))
    for s in (-1, 1): m.rbox(s * 0.178, 0, 0.29, 0.03, 0.05, 0.04, 0.006, seg=1, mi=I['plastic'], rgba=rgba)
    pts = [(0.18 * math.cos(math.pi * j / 8), 0.0, 0.29 + 0.17 * math.sin(math.pi * j / 8)) for j in range(9)]
    for a, b in zip(pts[:-1], pts[1:]): m.between(a, b, 0.0065, seg=4, mi=I['steel_charcoal'])
    m.add(p_cyl(0.014, 0.1, 6), (0.0, 0.0, 0.46), (0, math.pi / 2, 0), mi=I['plastic'], rgba=(0.08, 0.08, 0.09, 1))
    m.add(p_arc_band(0.1675, 0.12, 0.2, 0.3, 1.5, 6, 0.004), mi=I['signage'], rgba=(0.85, 0.85, 0.8, 1))
    weather(m, 5, dirt=0.5, dirt_h=0.1, streak=0.1, blotch=0.2, angle=30.0)
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
    """Builder's wheelbarrow: pressed yellow tub with rolled rim and ribs, dirty rubble fill, pneumatic tyre on a spoked rim with fork, tubular chassis and handles with rubber grips, brace feet."""
    m = mb(F); rnd = random.Random(14); Y = (0.82, 0.62, 0.08, 1); TUBE = (0.1, 0.1, 0.11, 1)
    pb = p_frustum(0.62, 0.34, 1.0, 0.68, 0.3, 0.05, 2, shift=(0.1, 0.0)); fs = [f for f in pb.faces if f.normal.z > 0.99]; bmesh.ops.delete(pb, geom=fs, context='FACES_ONLY')
    add_var(m, pb, (0.0, 0.0, 0.42), (0, -0.08, 0), mi=I['paint'], rgba=Y, var=0.0, rnd=rnd, flat=False)
    m.rbox(0.05, 0, 0.67, 0.86, 0.5, 0.02, 0.0, rot=(0, -0.08, 0), mi=I['props'], rgba=(0.12, 0.09, 0.06, 1))                    # fill
    for i in range(7):
        x = rnd.uniform(-0.28, 0.32); y = rnd.uniform(-0.18, 0.18); s = rnd.uniform(0.05, 0.09)
        m.add(p_rock(rnd, s, 0.7, 0.3, 0), (x, y, 0.68 + s * 0.2), (0, 0, rnd.uniform(0, 6)), mi=I['props'], rgba=rnd.choice([(0.35, 0.33, 0.3, 1), (0.5, 0.45, 0.4, 1), (0.25, 0.22, 0.2, 1), (0.45, 0.3, 0.2, 1)]))
    for sy in (-1, 1):
        m.rbox(0.06, sy * 0.335, 0.715, 1.0, 0.045, 0.045, 0.012, rot=(0, -0.08, 0), seg=1, mi=I['paint'], rgba=tuple(k * 0.85 for k in Y[:3]) + (1,))     # rolled rim
        for x in (-0.15, 0.2): m.rbox(x, sy * 0.28, 0.5, 0.04, 0.03, 0.26, 0.006, rot=(sy * 0.0, 0, 0), seg=1, mi=I['paint'], rgba=tuple(k * 0.85 for k in Y[:3]) + (1,)) if False else None
    m.rbox(-0.43, 0, 0.7, 0.045, 0.7, 0.045, 0.012, seg=1, mi=I['paint'], rgba=tuple(k * 0.85 for k in Y[:3]) + (1,)); m.rbox(0.6, 0, 0.7, 0.045, 0.56, 0.045, 0.012, seg=1, mi=I['paint'], rgba=tuple(k * 0.85 for k in Y[:3]) + (1,))
    m.add(p_lathe([(0.15, -0.06), (0.17, -0.065), (0.21, -0.04), (0.225, 0.0), (0.21, 0.04), (0.17, 0.065), (0.15, 0.06)], 18), (0.62, 0, 0.225), (math.pi / 2, 0, 0), mi=I['rubber'])                  # tyre
    m.add(p_wheel_spoked(0.15, 0.04, 6, 14), (0.62, 0, 0.225), (math.pi / 2, 0, 0), mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
    m.between((0.62, -0.1, 0.225), (0.62, 0.1, 0.225), 0.012, seg=5, mi=I['steel_charcoal'])
    for sy in (-1, 1):
        m.between((0.62, sy * 0.1, 0.225), (0.34, sy * 0.2, 0.46), 0.017, seg=6, mi=I['paint'], rgba=TUBE)                                      # fork
        m.between((0.34, sy * 0.2, 0.46), (-0.2, sy * 0.3, 0.46), 0.017, seg=6, mi=I['paint'], rgba=TUBE)                                      # chassis rail
        m.between((-0.2, sy * 0.3, 0.46), (-0.9, sy * 0.3, 0.7), 0.019, seg=6, mi=I['paint'], rgba=TUBE)                                       # handle
        m.between((-0.9, sy * 0.3, 0.7), (-1.05, sy * 0.3, 0.74), 0.026, seg=8, mi=I['rubber'])                                                # grip
        m.between((-0.48, sy * 0.3, 0.53), (-0.56, sy * 0.3, 0.02), 0.017, seg=6, mi=I['paint'], rgba=TUBE)                                   # leg
        m.rbox(-0.56, sy * 0.3, 0.012, 0.1, 0.05, 0.024, 0.006, seg=1, mi=I['rubber'])
        m.rbox(0.3, sy * 0.2, 0.43, 0.09, 0.03, 0.05, 0.006, seg=1, mi=I['steel_charcoal'])
    m.between((-0.48, -0.3, 0.3), (-0.48, 0.3, 0.3), 0.014, seg=5, mi=I['paint'], rgba=TUBE)
    weather(m, 14, dirt=0.5, dirt_h=0.18, streak=0.2, blotch=0.2, angle=30.0)
    return m.finish('proto_wheelbarrow', P)

def toolbox(F, P, rgba=(0.62, 0.08, 0.05, 1), name='toolbox'):
    """Red steel toolbox 0.55 x 0.25: pressed body with swage ribs, separate lid with seam, front latches, carry handle on brackets, rear hinges, corner caps and a stencil label."""
    m = mb(F); RD = rgba; DK = (0.07, 0.07, 0.08, 1)
    m.rbox(0, 0, 0.115, 0.55, 0.25, 0.23, 0.02, seg=1, mi=I['paint'], rgba=RD)                                                      # body
    m.rbox(0, 0, 0.255, 0.56, 0.26, 0.06, 0.02, seg=1, mi=I['paint'], rgba=tuple(k * 0.92 for k in RD[:3]) + (1,))                  # lid
    m.rbox(0, 0, 0.226, 0.565, 0.265, 0.012, 0.003, seg=1, mi=I['steel_charcoal'], rgba=DK)                                           # seam
    for sy in (-1, 1):
        for z in (0.1, 0.17): m.rbox(0, sy * 0.127, z, 0.4, 0.008, 0.012, 0.0, mi=I['paint'], rgba=tuple(k * 0.78 for k in RD[:3]) + (1,))   # swage ribs
    for sx in (-1, 1):
        m.rbox(sx * 0.255, 0, 0.13, 0.04, 0.26, 0.2, 0.012, seg=1, mi=I['steel_charcoal'], rgba=DK) if False else None
        for sy in (-1, 1): m.rbox(sx * 0.275, sy * 0.125, 0.03, 0.035, 0.035, 0.06, 0.008, seg=1, mi=I['steel_charcoal'])            # corner feet
        m.rbox(sx * 0.17, 0.134, 0.21, 0.07, 0.016, 0.07, 0.004, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))                  # latch plates
        m.rbox(sx * 0.17, 0.142, 0.2, 0.03, 0.01, 0.04, 0.003, seg=1, mi=I['steel_charcoal'])
        m.rbox(sx * 0.18, -0.134, 0.24, 0.07, 0.02, 0.05, 0.004, seg=1, mi=I['steel_charcoal'])                                           # hinges
        m.rbox(sx * 0.13, 0, 0.29, 0.03, 0.05, 0.03, 0.006, seg=1, mi=I['steel_charcoal'])                                                  # handle bracket
    m.between((-0.13, 0, 0.335), (0.13, 0, 0.335), 0.014, seg=6, mi=I['rubber'])
    for sx in (-1, 1): m.between((sx * 0.13, 0, 0.31), (sx * 0.13, 0, 0.335), 0.01, seg=5, mi=I['steel_charcoal'])
    m.rbox(0, 0.1292, 0.12, 0.17, 0.004, 0.09, 0.0, mi=I['signage'], rgba=(0.85, 0.82, 0.72, 1)); m.rbox(0, 0.1315, 0.14, 0.12, 0.003, 0.02, 0.0, mi=I['signage'], rgba=(0.07, 0.07, 0.07, 1)); m.rbox(0, 0.1315, 0.1, 0.09, 0.003, 0.014, 0.0, mi=I['signage'], rgba=(0.07, 0.07, 0.07, 1))
    studs(m, [(sx * 0.24, 0.131, z) for sx in (-1, 1) for z in (0.06, 0.18)], '+y', r=0.008, h=0.006, seg=4, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.8, 1))
    weather(m, 6, dirt=0.4, dirt_h=0.1, streak=0.1, blotch=0.15, top=0.2, angle=30.0)
    return m.finish('proto_' + name, P)

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
