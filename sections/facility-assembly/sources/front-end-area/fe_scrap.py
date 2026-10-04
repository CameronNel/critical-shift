"""Scrapyard junk, rubble and barricade prototypes plus piling helpers (shared by yard, cafeteria and hall)."""
from fe_common import *
from fe_props import *
from fe_yard import inst

def ground_object(o):
    """Shift an object up/down so its lowest evaluated vertex sits on z=0 (used for tipped furniture and wrecks)."""
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    o.location.z -= min(zs)

def p_chunk(F, P, seed, size=0.4):
    m = MB([F['concrete_slab']]); m.use(0)
    m.blob(0, 0, 0, size, size * 0.8, size * 0.6, sub=1, jitter=0.35, seed=seed)
    return m.finish(f'proto_chunk_{seed}', P)

def p_rebar(F, P):
    m = MB([F['steel_rust']]); m.use(0)
    for i in range(5): m.cyl_h(0.0, i * 0.06 - 0.12, 0.0, 1.0 + i * 0.25, 0.008, seg=5)
    return m.finish('proto_rebar', P)

def p_container(F, P, rgba, rusty=True):
    m = MB([F['corrugated'], F['steel_rust']]); L, W, H = 6.0, 2.44, 2.6
    m.use(0, rgba)
    m.box(0, 0, H / 2, L, W - 0.1, H - 0.1, bevel=0.01)
    for sy in (-1, 1):
        for k in range(int(L / 0.22)): m.box(-L / 2 + 0.11 + k * 0.22, sy * (W / 2 - 0.04), H / 2, 0.11, 0.07, H - 0.2)
    for sx in (-1, 1):
        m.use(1, (0.25, 0.12, 0.06, 1))
        for sy in (-1, 1): m.box(sx * L / 2, sy * (W / 2 - 0.06), H / 2, 0.14, 0.14, H, bevel=0.01)
        m.box(sx * L / 2, 0, 0.07, 0.14, W, 0.14, bevel=0.01); m.box(sx * L / 2, 0, H - 0.07, 0.14, W, 0.14, bevel=0.01)
        m.use(0, tuple(c * 0.8 for c in rgba[:3]) + (1,)); m.box(sx * (L / 2 + 0.02), 0, H / 2, 0.04, W - 0.2, H - 0.2)
        for sy in (-0.3, 0.3): m.use(1, (0.12, 0.12, 0.12, 1)); m.cyl(sx * (L / 2 + 0.07), sy, 0.2, H - 0.2, 0.025, seg=6)
    m.use(1, (0.2, 0.1, 0.05, 1)); m.box(0, 0, 0.12, L - 0.3, W - 0.2, 0.2); m.box(0, 0, H - 0.04, L, W, 0.08, bevel=0.01)
    return m.finish('proto_container_%d' % int(rgba[0] * 100), P)

def p_skip(F, P):
    m = MB([F['steel_accent'], F['steel_rust'], F['props']]); m.use(0, (0.55, 0.3, 0.07, 1))
    # tapered open skip with a ribbed side, partially filled with junk
    for sy in (-1, 1): m.box(0, sy * 0.85, 0.55, 3.4, 0.07, 1.0, bevel=0.01)
    for sx in (-1, 1): m.box(sx * 1.7, 0, 0.55, 0.07, 1.8, 1.0, bevel=0.01)
    m.box(0, 0, 0.1, 3.4, 1.8, 0.07)
    m.use(1, (0.18, 0.1, 0.06, 1))
    for k in range(6):
        for sy in (-1, 1): m.box(-1.4 + k * 0.56, sy * 0.9, 0.55, 0.06, 0.05, 0.95)
    for sx in (-1, 1): m.cyl_h(sx * 1.1, 0, 0.0, 0.0 + 0.0001, 0.001, seg=3) if False else None
    rnd = random.Random(3); m.use(2, (0.3, 0.22, 0.16, 1))
    for k in range(14): m.box(rnd.uniform(-1.4, 1.4), rnd.uniform(-0.6, 0.6), 0.2 + rnd.uniform(0, 0.6), rnd.uniform(0.3, 0.9), rnd.uniform(0.2, 0.5), rnd.uniform(0.1, 0.4), rz=rnd.uniform(0, 3), bevel=0.01)
    m.use(1, (0.25, 0.12, 0.06, 1)); m.box(0.4, 0.3, 0.95, 1.4, 0.04, 0.9, rz=0.4); m.cyl_h(-0.6, -0.2, 0.9, 1.6, 0.05, seg=8, rz=0.9)
    for sx in (-1.5, 1.5):
        m.use(1, (0.1, 0.1, 0.1, 1)); m.cyl_h(sx, 0, 0.08, 0.2, 0.08, seg=8, rz=math.pi / 2)
    return m.finish('proto_skip', P)

def p_wreck(F, P, seed):
    """Stripped car/truck hulk: body box, cab, missing doors, open bonnet, flat tyres or none, rust-through patches."""
    rnd = random.Random(seed); m = MB([F['props'], F['steel_rust'], F['glass'], F['rubber'], F['steel_charcoal']])
    cols = [(0.32, 0.10, 0.07, 1), (0.16, 0.2, 0.27, 1), (0.34, 0.3, 0.16, 1), (0.22, 0.25, 0.18, 1)]
    c = cols[seed % 4]; truck = seed % 2 == 1
    L = 5.6 if truck else 4.3; Wd = 2.0 if truck else 1.75
    m.use(0, c); m.box(0, 0, 0.62, L, Wd, 0.7, bevel=0.06, seg=2)                 # lower body
    m.use(0, c)
    if truck:
        m.box(1.5, 0, 1.35, 1.7, Wd - 0.1, 0.95, bevel=0.07, seg=2); m.use(2, (0.4, 0.45, 0.45, 1))
        m.box(1.82, 0, 1.4, 0.04, Wd - 0.3, 0.45)
        m.use(1, (0.2, 0.1, 0.06, 1)); m.box(-0.9, 0, 1.0, 3.0, Wd - 0.08, 0.06)  # flat bed
        for sy in (-1, 1): m.box(-0.9, sy * (Wd / 2 - 0.05), 1.25, 3.0, 0.05, 0.5)
    else:
        m.box(-0.2, 0, 1.2, 2.2, Wd - 0.15, 0.55, bevel=0.1, seg=2); m.use(2, (0.4, 0.45, 0.45, 1))
        for sx in (-0.2,): m.box(sx, 0, 1.22, 2.0, Wd - 0.12, 0.38)
    # open bonnet and tilted door
    m.use(0, c); m.box(L / 2 - 0.7, 0.0, 1.05 + 0.3, 1.3, Wd - 0.15, 0.04, rz=0.0, bevel=0.01)
    m.use(1, (0.2, 0.1, 0.05, 1))
    for i in range(rnd.randint(4, 8)): m.box(rnd.uniform(-L / 2 + 0.3, L / 2 - 0.3), rnd.choice((-1, 1)) * (Wd / 2 + 0.01), 0.62 + rnd.uniform(-0.2, 0.2), rnd.uniform(0.2, 0.7), 0.03, rnd.uniform(0.15, 0.35))
    m.use(4, (0.05, 0.05, 0.05, 1))
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (L / 2 - 0.8); y = sy * (Wd / 2 - 0.1)
            if rnd.random() < 0.35: m.cyl_h(x, y, 0.22, 0.16, 0.16, seg=8, rz=math.pi / 2)    # rim only
            else: m.use(3, (0.04, 0.04, 0.04, 1)); m.cyl_h(x, y, 0.3 if rnd.random() < 0.6 else 0.22, 0.22, 0.3, seg=14, rz=math.pi / 2)
    m.use(4, (0.1, 0.1, 0.1, 1)); m.box(L / 2 + 0.02, 0, 0.45, 0.14, Wd - 0.1, 0.12); m.box(-L / 2 - 0.02, 0, 0.45, 0.14, Wd - 0.1, 0.12)
    return m.finish(f'proto_wreck_{seed}', P)

def p_cube(F, P, seed):
    rnd = random.Random(seed); m = MB([F['props'], F['steel_rust']]); m.use(0, [(0.3, 0.17, 0.1, 1), (0.2, 0.22, 0.25, 1), (0.28, 0.25, 0.14, 1)][seed % 3])
    m.box(0, 0, 0.5, 1.3, 1.0, 1.0, bevel=0.06, seg=2)
    m.use(1, (0.2, 0.1, 0.06, 1))
    for i in range(18): m.box(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.45, 0.45), rnd.uniform(0.05, 0.95), rnd.uniform(0.25, 0.6), rnd.uniform(0.2, 0.5), 0.05, rz=rnd.uniform(0, 3), bevel=0.005)
    return m.finish(f'proto_cube_{seed}', P)

def p_pipes(F, P):
    m = MB([F['steel_rust']]); m.use(0, (0.28, 0.14, 0.08, 1))
    for r in range(3):
        for c in range(4 - r): m.cyl_h(0, (c - (3 - r) / 2) * 0.34, 0.17 + r * 0.29, 3.8, 0.15, seg=10)
    return m.finish('proto_pipes', P)

def p_tyre_stack(F, P):
    m = MB([F['rubber']]); m.use(0, (0.05, 0.05, 0.05, 1))
    for k in range(5): m.torus(0, 0, 0.12 + k * 0.24, 0.3, 0.12, ns=14, nt=7, tilt=False)
    return m.finish('proto_tyre_stack', P)

def p_jersey(F, P):
    m = MB([F['concrete_slab'], F['signage']]); m.use(0)
    m.box(0, 0, 0.12, 2.0, 0.6, 0.24, bevel=0.01); m.box(0, 0, 0.5, 2.0, 0.34, 0.55, bevel=0.03); m.box(0, 0, 0.9, 2.0, 0.2, 0.3, bevel=0.03)
    m.use(1, (0.9, 0.7, 0.05, 1))
    for k in range(4): m.box(-0.75 + k * 0.5, -0.171, 0.55, 0.2, 0.005, 0.4)
    return m.finish('proto_jersey', P)

def p_sandbags(F, P, seed):
    rnd = random.Random(seed); m = MB([F['fabric']]); m.use(0, (0.27, 0.23, 0.14, 1))
    for r in range(3):
        for c in range(4 - (r % 2)):
            m.use(0, (0.27 + rnd.uniform(-0.05, 0.05), 0.23, 0.14, 1))
            m.blob((c - 1.5 + 0.5 * (r % 2)) * 0.5, rnd.uniform(-0.02, 0.02), 0.1 + r * 0.17, 0.27, 0.18, 0.1, sub=1, jitter=0.12, seed=seed * 20 + r * 4 + c)
    return m.finish(f'proto_sandbags_{seed}', P)

def p_slab_leaning(F, P):
    m = MB([F['concrete_slab'], F['steel_rust']]); m.use(0)
    m.box(0, 0, 0, 3.0, 0.3, 0.9, bevel=0.03)
    m.use(1, (0.25, 0.12, 0.06, 1))
    for i in range(7): m.cyl_h(-1.4 + i * 0.45, 0.0, -0.5, 0.0001, 0.001, seg=3) if False else m.cyl(-1.35 + i * 0.45, 0, -0.9, -0.3, 0.012, seg=5)
    return m.finish('proto_slab_piece', P)

def p_locker(F, P):
    m = MB([F['steel_charcoal'], F['plastic']]); m.use(0, (0.18, 0.2, 0.22, 1)); m.box(0, 0, 0.9, 1.0, 0.5, 1.8, bevel=0.01)
    m.use(1, (0.3, 0.32, 0.34, 1))
    for k in range(3): m.box(-0.33 + k * 0.33, 0.255, 0.9, 0.3, 0.015, 1.7)
    return m.finish('proto_locker', P)

def p_shelf(F, P):
    m = MB([F['steel_charcoal'], F['props']]); m.use(0, (0.15, 0.17, 0.2, 1))
    for sx in (-1, 1):
        for sy in (-1, 1): m.box(sx * 1.0, sy * 0.25, 1.0, 0.05, 0.05, 2.0)
    for z in (0.15, 0.7, 1.25, 1.8): m.box(0, 0, z, 2.05, 0.55, 0.03)
    rnd = random.Random(2); m.use(1, (0.5, 0.4, 0.28, 1))
    for z in (0.2, 0.75, 1.3):
        for k in range(rnd.randint(2, 4)): m.box(rnd.uniform(-0.8, 0.8), 0, z + 0.13, rnd.uniform(0.25, 0.5), 0.35, 0.22, bevel=0.01)
    return m.finish('proto_shelf', P)

class Protos: pass

def make_protos(F, P):
    X = Protos()
    X.chunks = [p_chunk(F, P, s, 0.28 + 0.06 * (s % 4)) for s in range(5)]; X.rebar = p_rebar(F, P)
    X.containers = [p_container(F, P, c) for c in ((0.34, 0.1, 0.07, 1), (0.1, 0.19, 0.25, 1), (0.36, 0.3, 0.08, 1), (0.2, 0.24, 0.15, 1))]
    X.skip = p_skip(F, P); X.wrecks = [p_wreck(F, P, s) for s in range(4)]; X.cubes = [p_cube(F, P, s) for s in range(3)]
    X.pipes = p_pipes(F, P); X.tyres = p_tyre_stack(F, P); X.jersey = p_jersey(F, P); X.sandbags = [p_sandbags(F, P, s) for s in range(2)]
    X.piece = p_slab_leaning(F, P); X.locker = p_locker(F, P); X.shelf = p_shelf(F, P)
    return X

def rubble_pile(X, coll, name, cx, cy, rx, ry, h, n, seed, rebar_n=6, avoid=None):
    """A heap of concrete chunks; instances rest on the heap, not on the floor (support='heap')."""
    rnd = random.Random(seed); k = 0
    for i in range(n * 3):
        if k >= n: break
        a = rnd.uniform(0, 6.283); r = math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        if avoid and any(q[0] <= x <= q[1] and q[2] <= y <= q[3] for q in avoid): continue
        z = h * (1 - r ** 1.5) * rnd.uniform(0.55, 1.0)
        o = inst(X.chunks[rnd.randrange(5)], f'{name}_c{k}', x, y, coll, rz=rnd.uniform(0, 6.28), z=max(z - 0.1, -0.02), scale=(rnd.uniform(0.7, 1.5),) * 3, support='heap')
        o.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), o.rotation_euler[2]); k += 1
    for i in range(rebar_n):
        a = rnd.uniform(0, 6.283); r = rnd.uniform(0.1, 0.7)
        o = inst(X.rebar, f'{name}_rebar{i}', cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r, coll, rz=rnd.uniform(0, 6.28), z=h * (1 - r) * 0.8, support='heap')
        o.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.7, 0.2), o.rotation_euler[2])

def scrap_heap(X, protos, coll, name, cx, cy, r, h, n, seed):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 6.283); q = math.sqrt(rnd.random()); x, y = cx + math.cos(a) * r * q, cy + math.sin(a) * r * q * 0.8
        z = h * (1 - q ** 1.4) * rnd.uniform(0.3, 1.0)
        pr = rnd.choice(protos)
        o = inst(pr, f'{name}_{i}', x, y, coll, rz=rnd.uniform(0, 6.28), z=z, support='heap', scale=(rnd.uniform(0.5, 0.9),) * 3)
        o.rotation_euler = (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), o.rotation_euler[2])

def _rect(cx, cy, hx, hy, rz):
    c, s = abs(math.cos(rz)), abs(math.sin(rz)); ex = hx * c + hy * s; ey = hx * s + hy * c
    return (cx - ex, cx + ex, cy - ey, cy + ey)

def build_scrapyard(F, C, P, X):
    """Heavy scrapyard junk on both sides of the mine lane. Returns rectangles the later scatter should avoid."""
    yard = C['YARD']; rnd = random.Random(404); rects = []
    def put(proto, name, x, y, rz, z=0.0, hx=0.0, hy=0.0, support='floor', scale=(1, 1, 1)):
        o = inst(proto, name, x, y, yard, rz=rz, z=z, scale=scale, support=support)
        if hx: rects.append(_rect(x, y, hx * scale[0], hy * scale[1], rz))
        return o
    # containers: stacked, skewed, one half open
    put(X.containers[0], 'container_0', -42.6, -81.6, 0.0, hx=3.0, hy=1.25)
    put(X.containers[1], 'container_0b', -42.3, -81.7, 0.07, z=2.6, support='stack')
    put(X.containers[2], 'container_1', -36.0, -81.8, -0.05, hx=3.0, hy=1.25)
    put(X.containers[3], 'container_2', -39.6, -76.7, 0.32, hx=3.0, hy=1.25)
    put(X.containers[0], 'container_3', -41.0, -62.7, 0.0, hx=3.0, hy=1.25)
    put(X.containers[3], 'container_3b', -40.8, -62.6, -0.06, z=2.6, support='stack')
    put(X.containers[1], 'container_4', -33.2, -62.9, -0.1, hx=3.0, hy=1.25)
    put(X.containers[2], 'container_5', -17.4, -82.4, 1.5708 * 0 + 0.05, hx=3.0, hy=1.25)
    # wrecks
    for i, (x, y, rz) in enumerate(((-44.2, -74.6, 1.57), (-33.5, -79.3, 2.7), (-30.0, -66.4, 0.3), (-17.2, -66.2, 0.1), (-31.0, -74.5, -0.4))):
        put(X.wrecks[i % 4], f'wreck_{i}', x, y, rz, hx=2.6, hy=1.0)
    # skips
    for i, (x, y, rz) in enumerate(((-23.6, -78.4, 0.1), (-35.5, -66.3, 0.25), (-25.5, -63.6 if False else -66.8, 0.0))):
        put(X.skip, f'skip_{i}', x, y, rz, hx=1.9, hy=1.0)
    # crushed car cubes, stacked
    for i, (x, y) in enumerate(((-15.4, -74.6), (-15.2, -76.2), (-29.3, -61.6), (-27.8, -61.7), (-45.0, -63.0))):
        put(X.cubes[i % 3], f'cube_{i}', x, y, rnd.uniform(-0.3, 0.3), hx=0.75, hy=0.6)
        if i in (0, 2): put(X.cubes[(i + 1) % 3], f'cube_{i}_top', x + 0.1, y, rnd.uniform(-0.3, 0.3), z=1.0, support='stack')
    # pipes, tyre stacks
    for i, (x, y, rz) in enumerate(((-19.0, -73.2, 0.05), (-19.2, -72.6, 0.1), (-13.5, -83.1, 0.0), (-28.5, -64.0, 1.4 if False else 0.2), (-44.5, -65.4, 1.3))):
        put(X.pipes, f'pipes_{i}', x, y, rz, hx=1.9, hy=0.7)
    for i in range(14):
        x, y = rnd.choice(((rnd.uniform(-47, -43), rnd.uniform(-83.5, -79)), (rnd.uniform(-31, -26.5), rnd.uniform(-83.5, -81)), (rnd.uniform(-20, -13), rnd.uniform(-70.8 if False else -66.5, -62)), (rnd.uniform(-39, -35), rnd.uniform(-67, -64.5))))
        if -71.5 < y < -68.5: continue
        put(X.tyres, f'tyre_stack_{i}', x, y, rnd.uniform(0, 6), hx=0.4, hy=0.4)
    # scrap heaps (mixed metal) – instanced chunks of the scrap prototypes
    sc = [proto_scrap(F, P, s) for s in (7, 8, 9)]
    for i, (x, y, r, h, n) in enumerate(((-38.0, -74.2, 2.0, 1.7, 14), (-24.0, -82.0, 2.2, 2.0, 16), (-44.0, -74.0, 1.2, 1.3, 8), (-22.0, -76.0, 1.8, 1.5, 12), (-30.0, -70.3 if False else -65.6, 1.2, 1.0, 6), (-12.8, -68.5 if False else -64.8, 1.2, 1.0, 6))):
        if -71.3 < y + 0 < -68.7: continue
        scrap_heap(X, sc, yard, f'heap_{i}', x, y, r, h, n, 100 + i); rects.append((x - r, x + r, y - r, y + r))
    # rubble where the fence and cliff foot have crumbled
    for i, (x, y, rx, ry, h, n) in enumerate(((-46.2, -80.5, 1.6, 1.2, 0.7, 30), (-46.5, -63.5, 1.4, 1.0, 0.6, 24), (-10.6, -83.0, 1.2, 0.8, 0.5, 18), (-30.0, -60.9, 1.0, 0.6, 0.4, 12))):
        rubble_pile(X, yard, f'yard_rubble_{i}', x, y, rx, ry, h, n, 200 + i, rebar_n=3); rects.append((x - rx, x + rx, y - ry, y + ry))
    # fallen fence panels and tarp heaps
    for i, (x, y, rz) in enumerate(((-17.0, -61.5, 0.1), (-34.0, -60.8, 0.0))):
        pass
    return rects

def tilted_box(F, coll, name, cx, cy, cz, sx, sy, sz, rx, ry, rz, mat, rgba=None, bev=0.02):
    o = box(name, -sx / 2, sx / 2, -sy / 2, sy / 2, -sz / 2, sz / 2, mat, coll, rgba=rgba, bev=bev, plan=False)
    o.location = (LX(cx), LY(cy), cz); o.rotation_euler = (rx, ry, rz); return o

def build_hall_clutter(F, C, P, X):
    """Cave-ins, barricades and wreckage that funnel the hall: clear lanes stay on the cafeteria-spine axis (x 6.8..9.2) and the west/east door line (y -55.3..-52.7)."""
    hall = C['HALL']; rnd = random.Random(909)
    crates = [proto_crate(F, P, v) for v in range(4)]
    lane_ns = (6.8, 9.2, -60.0, -48.0); lane_ew = (-4.0, 32.0, -55.3, -52.7)
    # ---- south-west cave-in: heap, fallen ceiling slab, torn duct, rebar
    rubble_pile(X, hall, 'cavein_SW', -0.2, -58.2, 3.9, 1.3, 1.7, 170, 1, rebar_n=10, avoid=[lane_ns])
    t = tilted_box(F, hall, 'cavein_slab_SW_a', 0.3, -57.6, 1.05, 3.6, 1.3, 0.28, 0.0, 0.42, 0.15, F['concrete_slab']); t['support'] = 'heap'
    t = tilted_box(F, hall, 'cavein_slab_SW_b', -2.3, -58.3, 0.7, 2.4, 1.1, 0.25, 0.25, -0.35, 0.6, F['concrete_slab']); t['support'] = 'heap'
    t = tilted_box(F, hall, 'cavein_duct_SW', 2.8, -58.0, 3.0, 3.8, 0.8, 0.6, 0.0, -0.78, 0.05, F['corrugated'], bev=0.03); t['support'] = 'hanging'
    t = tilted_box(F, hall, 'cavein_beam_SW', -1.3, -58.9, 3.2, 5.5, 0.28, 0.32, 0.0, 0.55, 0.0, F['steel_charcoal'], bev=0.01); t['support'] = 'hanging'
    # ---- south-east cave-in
    rubble_pile(X, hall, 'cavein_SE', 16.6, -58.2, 3.2, 1.3, 1.5, 130, 2, rebar_n=8)
    t = tilted_box(F, hall, 'cavein_slab_SE', 16.4, -58.0, 0.95, 3.0, 1.2, 0.26, 0.0, -0.4, -0.2, F['concrete_slab']); t['support'] = 'heap'
    t = tilted_box(F, hall, 'cavein_tray_SE', 18.8, -58.6, 2.7, 3.2, 0.5, 0.1, 0.0, 0.7, 0.2, F['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1), bev=0.005); t['support'] = 'hanging'
    # ---- chicane at the cafeteria opening: two jersey barriers leave exactly the 2.4 m axis lane
    for i, x in enumerate((5.6, 10.4)): inst(X.jersey, f'chicane_jersey_{i}', x, -57.7, hall, rz=(0.04 if i == 0 else -0.05))
    inst(X.sandbags[0], 'chicane_sandbags_0', 5.6, -56.6, hall, rz=0.1, z=0.012); inst(X.sandbags[1], 'chicane_sandbags_1', 10.4, -56.7, hall, rz=-0.15, z=0.012)
    # ---- north-west: barricade of barriers, crates, a fallen locker and shelving
    for i, (x, y, rz) in enumerate(((-2.2, -51.7, 0.05), (0.0, -51.8, -0.04), (-3.0, -50.9, 1.5))): inst(X.jersey, f'nw_jersey_{i}', x, y, hall, rz=rz)
    for i, (x, y) in enumerate(((-1.2, -50.7), (-2.2, -50.7), (-1.6, -50.7))):
        inst(crates[i % 4], f'nw_crate_{i}', x, y, hall, rz=rnd.uniform(-0.3, 0.3), z=0.0 if i < 2 else 1.0, scale=(1, 1, 1), support='floor' if i < 2 else 'stack')
    o = inst(X.locker, 'nw_locker_fallen', 1.2, -50.8, hall, support=None); o.rotation_euler = (0, math.pi / 2 - 0.1, 0.4); ground_object(o); o['support'] = 'floor'
    # ---- north-middle: under the gantry
    for i, (x, y, rz) in enumerate(((4.6, -51.2, 0.1), (11.2, -51.3, -0.1), (13.4, -50.2, 1.5))): inst(X.jersey, f'mid_jersey_{i}', x, y, hall, rz=rz)
    inst(X.sandbags[0], 'mid_sandbags_0', 4.4, -50.2, hall, rz=0.3, z=0.012); inst(X.sandbags[1], 'mid_sandbags_1', 11.6, -50.3, hall, rz=-0.2, z=0.012)
    for i, (x, y, rz) in enumerate(((16.2, -49.4, 0.1), (18.6, -49.9, -0.3))):
        o = inst(X.shelf, f'shelf_toppled_{i}', x, y, hall, support=None); o.rotation_euler = (math.pi / 2 if i == 0 else 0.0, 0, rz) if i == 0 else (0, 0, rz); ground_object(o); o['support'] = 'floor'
    # ---- east side: collapsed shelving, crate wall and a dead floor scrubber of crates
    for i, (x, y) in enumerate(((27.2, -50.2), (28.2, -50.3), (27.7, -50.2), (29.4, -50.2), (30.5, -50.6), (30.4, -49.8))):
        inst(crates[i % 4], f'ne_crate_{i}', x, y, hall, rz=rnd.uniform(-0.25, 0.25), z=0.0 if i not in (2,) else 1.0, support='floor' if i != 2 else 'stack')
    for i, (x, y, rz) in enumerate(((26.0, -51.4, 0.1), (29.2, -51.8, -0.1), (31.0, -51.6, 1.55))): inst(X.jersey, f'ne_jersey_{i}', x, y, hall, rz=rz)
    for i, (x, y) in enumerate(((27.6, -58.4), (28.7, -58.5), (28.1, -58.4), (30.2, -58.0), (26.6, -57.8), (31.0, -59.2))):
        inst(crates[(i + 1) % 4], f'se_crate_{i}', x, y, hall, rz=rnd.uniform(-0.3, 0.3), z=0.0 if i != 2 else 1.0, support='floor' if i != 2 else 'stack')
    for i, (x, y, rz) in enumerate(((24.0, -56.6, 0.0), (32.0 - 1.0, -56.6, 1.57))): inst(X.jersey, f'se_jersey_{i}', x, y, hall, rz=rz)
    o = inst(X.shelf, 'shelf_toppled_E', 25.4, -49.9, hall, support=None); o.rotation_euler = (0, 0, 0.1); o['support'] = 'floor'
    # ---- weaving barrier on the east/west line (still >= 2.4 m of clear width)
    inst(X.jersey, 'weave_jersey_0', 19.5, -56.1, hall, rz=0.1); inst(X.jersey, 'weave_jersey_1', 23.0, -51.9, hall, rz=-0.08)
    # ---- loose floor debris
    cnt = 0
    for i in range(120):
        x = rnd.uniform(-3.6, 31.6); y = rnd.uniform(-59.6, -48.4)
        if lane_ns[0] < x < lane_ns[1] and rnd.random() < 0.8: continue
        o = inst(X.chunks[rnd.randrange(5)], f'hall_debris_{cnt}', x, y, hall, rz=rnd.uniform(0, 6.28), z=-0.05, scale=(rnd.uniform(0.25, 0.55),) * 3, support='floor_debris'); cnt += 1
    # ---- hanging cables and dead tubes in the broken ceiling
    cb = bmesh.new()
    for i in range(14):
        x = rnd.uniform(-3, 31); y = rnd.uniform(-59, -49); L = rnd.uniform(0.8, 2.6)
        bm_cyl(cb, LX(x), LY(y), 5.7 - L, 5.7, 0.012, seg=5)
        if rnd.random() < 0.6: bm_box(cb, LX(x), LY(y), 5.7 - L - 0.04, 0.1, 0.1, 0.08, bevel=0.01)
    mesh_obj('hall_hanging_cables', cb, F['steel_charcoal'], hall, rgba=(0.04, 0.04, 0.04, 1))
    return [lane_ns, lane_ew]

def build_grime(F, C, P, X):
    """Run-down surface storytelling: floor cracks and puddles, wall streaks and mould, fallen ceiling tiles, litter."""
    caf, hall, yard = C['CAFETERIA'], C['HALL'], C['YARD']; rnd = random.Random(31)
    def cracks(coll, name, rect, n):
        bm = bmesh.new()
        for i in range(n):
            x = rnd.uniform(rect[0], rect[1]); y = rnd.uniform(rect[2], rect[3]); a = rnd.uniform(0, 6.28)
            for k in range(rnd.randint(3, 7)):
                L = rnd.uniform(0.3, 0.9)
                if not (rect[0] + 0.5 < x < rect[1] - 0.5 and rect[2] + 0.5 < y < rect[3] - 0.5): break
                bm_box(bm, LX(x), LY(y), 0.003, L, 0.02, 0.004, rz=a)
                x += math.cos(a) * L * 0.9; y += math.sin(a) * L * 0.9; a += rnd.uniform(-0.9, 0.9)
        mesh_obj(name, bm, F['props'], coll, rgba=(0.03, 0.028, 0.025, 1))
    cracks(caf, 'caf_floor_cracks', (-7.5, 25.5, -79.5, -60.5), 60); cracks(hall, 'hall_floor_cracks', (-3.5, 31.5, -59.5, -48.5), 45)
    def blob_patch(coll, name, x, y, rx, ry, mat, rgba, z):
        bm = bmesh.new(); res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        for v in res['verts']:
            k = 1 + rnd.uniform(-0.25, 0.25); v.co = Vector((LX(x) + v.co.x * rx * k, LY(y) + v.co.y * ry * k, z + max(v.co.z, 0) * 0.004))
        return mesh_obj(name, bm, mat, coll, rgba=rgba)
    for i in range(5):
        x, y = rnd.uniform(-6, 24), rnd.uniform(-78, -62)
        if 6.5 < x < 9.5: x += 4
        blob_patch(caf, f'caf_stain_{i}', x, y, rnd.uniform(0.4, 0.9), rnd.uniform(0.3, 0.7), F['props'], (0.1, 0.085, 0.07, 1), 0.002)
        if i % 2 == 0: blob_patch(caf, f'caf_puddle_{i}', x, y, rnd.uniform(0.4, 1.0) * 0.8, rnd.uniform(0.3, 0.7) * 0.8, F['glass'], None, 0.006)
    for i in range(5):
        x, y = rnd.uniform(0, 30), rnd.uniform(-58, -49)
        blob_patch(hall, f'hall_stain_b{i}', x, y, rnd.uniform(0.6, 1.5), rnd.uniform(0.4, 1.0), F['props'], (0.05, 0.045, 0.04, 1), 0.002)
        if i % 2: blob_patch(hall, f'hall_puddle_{i}', x, y, 0.7, 0.45, F['glass'], None, 0.006)
    # wall streaks / mould: thin dark panels hanging from the ceiling line and the dado, per interior face
    def streaks(coll, prefix, axis, pos, a0, a1, z_top, off, n, excl=()):
        bm = bmesh.new(); s = 1 if off > 0 else -1
        for i in range(n):
            c = rnd.uniform(a0, a1); 
            if any(e0 < c < e1 for e0, e1 in excl): continue
            w = rnd.uniform(0.12, 0.7); h = rnd.uniform(0.6, 2.6); zc = z_top - h / 2 - rnd.uniform(0, 0.6)
            if axis == 'x': bm_box(bm, LX(c), LY(pos + off + s * 0.002), zc, w, 0.004, h)
            else: bm_box(bm, LX(pos + off + s * 0.002), LY(c), zc, 0.004, w, h)
        mesh_obj(prefix, bm, F['props'], coll, rgba=(0.07, 0.065, 0.045, 1))
    streaks(caf, 'caf_streak_S', 'x', -80.0, -8, 26, 5.0, 0.151, 30, excl=[(6.5, 9.5)]); streaks(caf, 'caf_streak_N', 'x', -60.0, -8, 26, 5.0, -0.151, 26, excl=[(4.5, 11.5)])
    streaks(caf, 'caf_streak_E', 'y', 26.0, -80, -60, 5.0, -0.151, 16, excl=[(-71.5, -68.5)]); streaks(caf, 'caf_streak_W', 'y', -8.0, -80, -60, 5.0, 0.151, 16, excl=[(-71.7, -68.3)])
    streaks(hall, 'hall_streak_S', 'x', -60.0, -4, 32, 6.0, 0.151, 28, excl=[(4.5, 11.5)]); streaks(hall, 'hall_streak_N', 'x', -48.0, -4, 32, 6.0, -0.151, 28, excl=[(5.5, 10.5)])
    streaks(hall, 'hall_streak_W', 'y', -4.0, -60, -48, 6.0, 0.151, 8); streaks(hall, 'hall_streak_E', 'y', 32.0, -60, -48, 6.0, -0.151, 8)
    streaks(yard, 'yard_streak_W', 'y', -8.0, -84, -60, 5.0, -0.151, 24, excl=[(-71.7, -68.3)])
    # fallen ceiling tiles and litter
    bm = bmesh.new()
    for i in range(34):
        x = rnd.uniform(-7.5, 25.5); y = rnd.uniform(-79.5, -60.5)
        if 6.7 < x < 9.3: continue
        bm_box(bm, LX(x), LY(y), 0.03, 0.6, 0.6, 0.02, rz=rnd.uniform(0, 3))
    mesh_obj('caf_fallen_tiles', bm, F['plaster'], caf, rgba=(0.55, 0.52, 0.45, 1))
    for coll, rect, n, nm in ((caf, (-7.5, 25.5, -79.5, -60.5), 70, 'caf'), (hall, (-3.5, 31.5, -59.5, -48.5), 40, 'hall'), (yard, (-47, -9, -83.5, -60.5), 90, 'yard')):
        bm = bmesh.new()
        for i in range(n):
            x = rnd.uniform(rect[0], rect[1]); y = rnd.uniform(rect[2], rect[3])
            if rnd.random() < 0.5: bm_box(bm, LX(x), LY(y), 0.006, rnd.uniform(0.1, 0.3), rnd.uniform(0.08, 0.2), 0.008, rz=rnd.uniform(0, 3))
            else: bm_cyl_h(bm, LX(x), LY(y), 0.03, 0.12, 0.03, seg=8, rz=rnd.uniform(0, 3))
        mesh_obj(f'{nm}_litter', bm, F['props'], coll, rgba=(0.35, 0.3, 0.22, 1))
