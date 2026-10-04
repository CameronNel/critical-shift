"""Cafeteria / chill room: dining, booths, vending, counter and kitchen, lounge, appliances, lights, small props."""
from fe_common import *
from fe_props import *
from fe_yard import inst

CAF = (-8.0, 26.0, -80.0, -60.0)

def p_chair(F, P, rgba):
    m = MB([F['plastic'], F['steel_charcoal']])
    m.use(0, rgba)
    m.box(0, 0, 0.47, 0.44, 0.44, 0.045, bevel=0.014); m.box(0, -0.2, 0.74, 0.42, 0.04, 0.3, bevel=0.012)
    m.use(1, (0.1, 0.1, 0.11, 1))
    for sx in (-0.18, 0.18):
        for sy in (-0.18, 0.18): m.cyl(sx, sy, 0.0, 0.45, 0.016, seg=8)
        m.cyl(sx + (0.01 if sx > 0 else -0.01), -0.2, 0.45, 0.9, 0.014, seg=8)
    for z in (0.14, 0.3): m.box(0, -0.18, z, 0.36, 0.014, 0.014); m.box(0, 0.18, z, 0.36, 0.014, 0.014)
    m.box(0, -0.2, 0.905, 0.42, 0.03, 0.03, bevel=0.008)
    return m.finish('proto_chair', P)

def p_table(F, P):
    m = MB([F['timber'], F['steel_charcoal']])
    m.use(0); m.box(0, 0, 0.75, 1.8, 0.9, 0.04, bevel=0.01); m.box(0, 0, 0.72, 1.74, 0.84, 0.03, bevel=0.006)
    m.use(1)
    for sx in (-0.6, 0.6):
        m.cyl(sx, 0, 0.02, 0.72, 0.045, seg=14); m.box(sx, 0, 0.012, 0.5, 0.1, 0.024, bevel=0.006); m.box(sx, 0, 0.7, 0.2, 0.55, 0.03, bevel=0.006)
    m.box(0, 0, 0.12, 1.2, 0.04, 0.04, bevel=0.006)
    return m.finish('proto_table', P)

def p_booth(F, P):
    m = MB([F['fabric'], F['timber'], F['steel_charcoal'], F['laminate']])
    m.use(2); m.box(0, 0.12, 0.17, 3.0, 0.9, 0.3, bevel=0.015)
    m.use(0, (0.46, 0.16, 0.1, 1))
    for i in range(3):
        x = -1.0 + i * 1.0
        m.box(x, 0.12, 0.43, 0.96, 0.78, 0.2, bevel=0.06)
        m.box(x, -0.17, 0.78, 0.96, 0.18, 0.5, bevel=0.06)
    m.use(1); m.box(0, -0.31, 0.95, 3.0, 0.05, 0.9, bevel=0.01)
    m.use(2)
    for sx in (-1.5, 1.5): m.box(sx, 0.1, 0.5, 0.05, 0.9, 0.95, bevel=0.01)
    m.use(3)
    m.box(0, 1.1, 0.74, 2.2, 0.75, 0.04, bevel=0.01); m.use(2); m.cyl(0, 1.1, 0.02, 0.72, 0.05, seg=12); m.box(0, 1.1, 0.012, 0.6, 0.5, 0.024, bevel=0.006)
    return m.finish('proto_booth', P)

def p_vending(F, P, rgba):
    m = MB([F['plastic'], F['glass'], F['emissive'], F['steel_charcoal']])
    m.use(0, rgba); m.box(0, 0, 0.95, 0.95, 0.85, 1.9, bevel=0.025)
    m.use(2, (1, 0.97, 0.9, 1)); m.box(0, 0.43, 1.78, 0.9, 0.02, 0.2)
    m.use(3, (0.1, 0.1, 0.12, 1)); m.box(0.32, 0.43, 0.96, 0.22, 0.03, 1.2, bevel=0.006); m.box(0, 0.43, 0.2, 0.7, 0.03, 0.22, bevel=0.006)
    m.use(2, (0.95, 0.9, 0.7, 1)); m.box(-0.1, 0.425, 1.1, 0.62, 0.01, 1.1)   # lit product bay
    cols = [(0.8, 0.1, 0.1, 1), (0.1, 0.4, 0.8, 1), (0.9, 0.7, 0.1, 1), (0.1, 0.6, 0.3, 1), (0.9, 0.9, 0.9, 1), (0.5, 0.3, 0.1, 1)]
    for r in range(5):
        for c in range(6):
            m.use(0, cols[(r * 3 + c) % 6])
            m.cyl(-0.34 + c * 0.1, 0.38, 0.62 + r * 0.2, 0.62 + r * 0.2 + 0.14, 0.032, seg=8)
    m.use(3, (0.2, 0.2, 0.22, 1))
    for r in range(5):
        m.box(-0.1, 0.4, 0.58 + r * 0.2, 0.62, 0.08, 0.012)
    for k in range(8): m.use(2, (0.3, 0.7, 0.4, 1)); m.box(0.27 + (k % 2) * 0.09, 0.44, 1.35 - (k // 2) * 0.09, 0.06, 0.012, 0.05)
    m.use(1); m.box(-0.1, 0.45, 1.1, 0.64, 0.01, 1.14)
    return m.finish('proto_vending', P)

def p_couch(F, P):
    m = MB([F['fabric'], F['steel_charcoal']])
    m.use(0, (0.52, 0.2, 0.12, 1))
    m.box(0, 0, 0.3, 2.3, 0.92, 0.3, bevel=0.07, seg=3)
    for sx in (-0.56, 0.56): m.box(sx, 0.08, 0.5, 1.08, 0.74, 0.18, bevel=0.06, seg=3); m.box(sx, -0.3, 0.72, 1.08, 0.24, 0.5, bevel=0.07, seg=3)
    for sx in (-1.07, 1.07): m.box(sx, 0, 0.5, 0.2, 0.92, 0.55, bevel=0.07, seg=3)
    m.box(0, -0.42, 0.62, 2.3, 0.14, 0.7, bevel=0.06, seg=3)
    m.use(1, (0.08, 0.08, 0.09, 1))
    for sx in (-1.0, 1.0):
        for sy in (-0.35, 0.35): m.cyl(sx, sy, 0.0, 0.16, 0.03, seg=8, r2=0.022)
    return m.finish('proto_couch', P, smooth=False)

def p_plant(F, P, seed, tall):
    m = MB([F['concrete_slab'], F['props'], F['foliage']]); rnd = random.Random(seed)
    m.use(0); m.cyl(0, 0, 0.0, 0.32, 0.2, seg=16, r2=0.16)
    m.use(1, (0.15, 0.1, 0.07, 1)); m.cyl(0, 0, 0.3, 0.33, 0.17, seg=16)
    m.use(2, (0.30, 0.24, 0.10, 1))
    for i in range(7 if tall else 5):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(0.05, 0.22)
        m.blob(math.cos(a) * r, math.sin(a) * r, 0.7 + rnd.uniform(0, 0.8 if tall else 0.4), 0.18, 0.1, 0.36, sub=2, jitter=0.15, seed=seed * 9 + i)
    return m.finish(f'proto_plant_{seed}', P, smooth=True)

def p_pendant(F, P):
    m = MB([F['steel_accent'], F['emissive'], F['steel_charcoal']])
    m.use(2); m.cyl(0, 0, 0.1, 1.25, 0.008, seg=6)
    m.use(0); m.cyl(0, 0, 0.0, 0.25, 0.3, seg=20, r2=0.07)
    m.use(1, (1.0, 0.86, 0.62, 1)); m.cyl(0, 0, -0.01, 0.0, 0.27, seg=20)
    return m.finish('proto_pendant', P)

def p_mug(F, P):
    m = MB([F['plastic']]); m.use(0, (0.9, 0.9, 0.85, 1)); m.cyl(0, 0, 0, 0.09, 0.04, seg=12); m.torus(0.05, 0, 0.05, 0.025, 0.006, ns=8, nt=5, tilt=True)
    return m.finish('proto_mug', P)

def p_tray(F, P):
    m = MB([F['plastic'], F['props']]); m.use(0, (0.12, 0.35, 0.5, 1)); m.box(0, 0, 0.012, 0.42, 0.3, 0.024, bevel=0.006); m.box(0, 0.14, 0.03, 0.42, 0.012, 0.03)
    m.use(1, (0.9, 0.82, 0.6, 1)); m.cyl(-0.1, 0, 0.024, 0.036, 0.07, seg=14); m.use(1, (0.7, 0.25, 0.15, 1)); m.box(0.1, 0, 0.04, 0.12, 0.08, 0.04, bevel=0.01)
    return m.finish('proto_tray', P)

def p_bottle(F, P):
    m = MB([F['glass'], F['plastic']]); m.use(0); m.cyl(0, 0, 0, 0.2, 0.032, seg=10); m.use(1, (0.8, 0.1, 0.1, 1)); m.cyl(0, 0, 0.2, 0.225, 0.016, seg=8)
    return m.finish('proto_bottle', P)

def p_bin(F, P, rgba):
    m = MB([F['plastic'], F['steel_charcoal']]); m.use(0, rgba); m.box(0, 0, 0.45, 0.42, 0.42, 0.9, bevel=0.02); m.use(1, (0.05, 0.05, 0.05, 1)); m.box(0, 0.211, 0.7, 0.2, 0.01, 0.12)
    return m.finish('proto_bin', P)

def p_floor_lamp(F, P):
    m = MB([F['steel_charcoal'], F['emissive']]); m.use(0); m.cyl(0, 0, 0, 0.03, 0.2, seg=14); m.cyl(0, 0, 0.03, 1.55, 0.015, seg=8); m.use(1, (1.0, 0.82, 0.55, 1)); m.cyl(0, 0, 1.45, 1.75, 0.15, seg=16, r2=0.1)
    return m.finish('proto_floor_lamp', P)

def p_foosball(F, P):
    m = MB([F['timber'], F['steel_charcoal'], F['plastic'], F['laminate']])
    m.use(0, (0.3, 0.2, 0.1, 1)); m.box(0, 0, 0.8, 1.4, 0.75, 0.22, bevel=0.015)
    m.use(3, (0.2, 0.3, 0.16, 1)); m.box(0, 0, 0.915, 1.3, 0.65, 0.012)
    m.use(1, (0.1, 0.1, 0.11, 1))
    for sx in (-0.6, 0.6):
        for sy in (-0.32, 0.32): m.box(sx, sy, 0.35, 0.07, 0.07, 0.7, bevel=0.01)
    for k in range(4):
        x = -0.45 + k * 0.3; m.cyl_h(x, 0, 1.03, 0.95 + 0.2, 0.011, seg=6, rz=math.pi / 2 * 0 + math.pi / 2) if False else None
        m.box(x, 0, 1.03, 0.014, 1.15, 0.014)
        m.use(2, (0.75, 0.15, 0.12, 1) if k % 2 == 0 else (0.15, 0.25, 0.6, 1))
        for j in range(3 if k in (1, 2) else 2): m.box(x, -0.2 + j * 0.2, 0.96, 0.05, 0.05, 0.14, bevel=0.008)
        m.use(1, (0.1, 0.1, 0.11, 1)); m.box(x, 0.6, 1.03, 0.04, 0.12, 0.04)
    return m.finish('proto_foosball', P)

def p_airhockey(F, P):
    m = MB([F['plastic'], F['steel_charcoal'], F['emissive']])
    m.use(0, (0.12, 0.2, 0.34, 1)); m.box(0, 0, 0.78, 2.1, 1.0, 0.12, bevel=0.02)
    m.use(0, (0.82, 0.84, 0.86, 1)); m.box(0, 0, 0.845, 1.9, 0.8, 0.012)
    m.use(0, (0.14, 0.22, 0.36, 1)); m.box(0, 0.45, 0.88, 2.1, 0.08, 0.06, bevel=0.01); m.box(0, -0.45, 0.88, 2.1, 0.08, 0.06, bevel=0.01)
    for sx in (-1, 1): m.box(sx * 1.0, 0, 0.88, 0.08, 1.0, 0.06, bevel=0.01)
    m.use(1, (0.1, 0.1, 0.11, 1))
    for sx in (-0.9, 0.9):
        for sy in (-0.4, 0.4): m.box(sx, sy, 0.36, 0.08, 0.08, 0.72, bevel=0.01)
    m.use(0, (0.8, 0.1, 0.1, 1)); m.cyl(-0.5, 0.1, 0.857, 0.9, 0.06, seg=12); m.use(0, (0.1, 0.3, 0.8, 1)); m.cyl(0.6, -0.12, 0.857, 0.9, 0.06, seg=12)
    m.use(0, (0.1, 0.1, 0.1, 1)); m.cyl(0.0, 0.0, 0.857, 0.865, 0.04, seg=10)
    m.use(2, (0.2, 0.9, 0.3, 1)); m.box(0.9, -0.52, 0.99, 0.2, 0.01, 0.06)
    return m.finish('proto_airhockey', P)

def p_hoops(F, P):
    """Arcade basketball: two lanes, backboards, hoops with nets, a ball rack, score display. Long axis along x, hoops at +x end."""
    m = MB([F['plastic'], F['steel_charcoal'], F['fabric'], F['emissive'], F['rubber']])
    m.use(0, (0.55, 0.14, 0.09, 1)); m.box(0, 0, 0.48, 2.4, 1.5, 0.95, bevel=0.03)
    m.use(1, (0.12, 0.12, 0.13, 1)); m.box(0, 0, 0.98, 2.2, 1.3, 0.04, bevel=0.01)
    m.box(1.25, 0, 1.5, 0.08, 1.5, 1.2, bevel=0.01)   # frame behind hoops
    for sy in (-0.35, 0.35):
        m.use(0, (0.9, 0.9, 0.88, 1)); m.box(1.2, sy, 1.9, 0.04, 0.55, 0.42, bevel=0.01)
        m.use(1, (0.8, 0.28, 0.1, 1)); m.torus(1.03, sy, 1.62, 0.15, 0.012, ns=14, nt=5, tilt=False)
        m.use(2, (0.75, 0.75, 0.72, 1))
        for k in range(8): a = k * math.pi / 4; m.cyl(1.03 + math.cos(a) * 0.14, sy + math.sin(a) * 0.14, 1.38, 1.62, 0.006, seg=4)
        m.use(4, (0.7, 0.28, 0.1, 1)); m.blob(-0.3, sy, 1.06, 0.12, 0.12, 0.12, sub=1, jitter=0.03, seed=int(sy * 10) + 20)
    m.use(3, (0.2, 0.9, 0.3, 1)); m.box(1.19, 0, 2.55, 0.05, 0.9, 0.22)
    m.use(1, (0.1, 0.1, 0.11, 1)); m.box(1.25, 0, 2.2, 0.06, 0.1, 0.8)
    return m.finish('proto_hoops', P)

def p_dartboard(F, P):
    m = MB([F['timber'], F['plastic'], F['steel_charcoal']])
    m.use(0, (0.12, 0.08, 0.05, 1)); m.box(0, 0, 0, 0.72, 0.05, 0.72, bevel=0.01)
    m.use(1, (0.08, 0.08, 0.08, 1)); m.cyl_h(0, -0.03, 0.0, 0.0001, 0.0001, seg=3) if False else None
    # concentric rings as thin discs facing -Y
    for i, (r, c) in enumerate(((0.225, (0.05, 0.05, 0.05, 1)), (0.2, (0.75, 0.15, 0.1, 1)), (0.185, (0.85, 0.8, 0.6, 1)), (0.105, (0.1, 0.4, 0.2, 1)), (0.09, (0.85, 0.8, 0.6, 1)), (0.03, (0.1, 0.4, 0.2, 1)), (0.012, (0.75, 0.15, 0.1, 1)))):
        m.use(1, c)
        res = bmesh.ops.create_cone(m.bm, cap_ends=True, cap_tris=False, segments=24, radius1=r, radius2=r, depth=0.01)
        for v in res['verts']: v.co = Vector((v.co.x, -0.03 - i * 0.002, v.co.z)) if False else Vector((v.co.x, -0.032 - i * 0.002 + v.co.z * 0 , v.co.y))
        for f in set(f for v in res['verts'] for f in v.link_faces): f.material_index = 1
        m._tag(set())
    m.use(2, (0.5, 0.5, 0.5, 1))
    for k, (x, z) in enumerate(((0.08, 0.1), (-0.12, -0.05), (0.02, -0.2))): m.box(x, -0.07, z, 0.012, 0.09, 0.012)
    return m.finish('proto_dartboard', P)

def p_kiosk(F, P):
    m = MB([F['steel_charcoal'], F['emissive'], F['plastic']])
    m.use(0, (0.12, 0.13, 0.14, 1)); m.box(0, 0, 0.9, 0.7, 0.45, 1.8, bevel=0.03)
    m.use(2, (0.05, 0.05, 0.06, 1)); m.box(0, 0.215, 1.35, 0.5, 0.04, 0.5, bevel=0.01)
    m.use(1, (0.15, 0.35, 0.22, 1)); m.box(0, 0.24, 1.35, 0.44, 0.005, 0.42)
    m.use(2, (0.4, 0.4, 0.42, 1)); m.box(0, 0.25, 0.9, 0.3, 0.12, 0.04, bevel=0.01)
    return m.finish('proto_kiosk', P)

def p_stanchion(F, P):
    m = MB([F['steel_charcoal'], F['signage']]); m.use(0, (0.18, 0.18, 0.2, 1)); m.cyl(0, 0, 0, 0.03, 0.14, seg=12); m.cyl(0, 0, 0.03, 1.0, 0.025, seg=8); m.cyl(0, 0, 1.0, 1.04, 0.045, seg=8)
    m.use(1, (0.6, 0.12, 0.1, 1)); m.box(0.5, 0, 0.9, 1.0, 0.012, 0.05)
    return m.finish('proto_stanchion', P)

def p_pendant_dead(F, P):
    m = MB([F['steel_accent'], F['steel_charcoal']])
    m.use(1); m.cyl(0, 0, 0.1, 1.25, 0.008, seg=6)
    m.use(0); m.cyl(0, 0, 0.0, 0.25, 0.3, seg=20, r2=0.07)
    return m.finish('proto_pendant_dead', P)

def dead(F, rgba):
    return rgba

def place_chairs_around(caf, chairs, rng, i, tx, ty, skip=(), tipped=()):
    for k, (dx, dy, rz) in enumerate(((-0.5, -0.85, 0), (0.5, -0.85, 0), (-0.5, 0.85, math.pi), (0.5, 0.85, math.pi))):
        if k in skip: continue
        if k in tipped:
            o = inst(chairs[(i + k) % 3], f'caf_chair_{i}_{k}', tx + dx * 1.3, ty + dy * 1.2, caf, rz=rz + rng.uniform(-1, 1), support=None)
            o.rotation_euler = (math.pi / 2 * rng.choice((-1, 1)), 0, o.rotation_euler[2]); ground_object(o); o['support'] = 'floor'
        else:
            inst(chairs[(i + k) % 3], f'caf_chair_{i}_{k}', tx + dx + rng.uniform(-0.15, 0.15), ty + dy + rng.uniform(-0.2, 0.2), caf, rz=rz + rng.uniform(-0.4, 0.4))

def build_cafeteria(F, C):
    from fe_scrap import ground_object
    globals()['ground_object'] = ground_object
    caf = C['CAFETERIA']; P = collection('PROTOTYPES'); rng = random.Random(5)
    chairs = [p_chair(F, P, c) for c in ((0.5, 0.17, 0.1, 1), (0.1, 0.11, 0.13, 1), (0.62, 0.4, 0.09, 1))]
    table = p_table(F, P); booth = p_booth(F, P)
    vend = [p_vending(F, P, c) for c in ((0.6, 0.1, 0.09, 1), (0.09, 0.25, 0.45, 1), (0.65, 0.5, 0.08, 1))]
    couch = p_couch(F, P); plants = [p_plant(F, P, 1, False), p_plant(F, P, 2, True), p_plant(F, P, 3, True)]
    pend = p_pendant(F, P); pdead = p_pendant_dead(F, P); mug = p_mug(F, P); tray = p_tray(F, P); bottle = p_bottle(F, P)
    bins = [p_bin(F, P, c) for c in ((0.15, 0.4, 0.2, 1), (0.15, 0.25, 0.5, 1), (0.1, 0.1, 0.1, 1))]
    flamp = p_floor_lamp(F, P); foos = p_foosball(F, P); airh = p_airhockey(F, P); hoops = p_hoops(F, P); dart = p_dartboard(F, P)
    kiosk = p_kiosk(F, P); stan = p_stanchion(F, P)
    # ---------------- EAST: small dining area under the serving counter
    tbl = [(16.6, -73.7), (21.4, -73.9), (16.9, -77.4), (21.5, -77.6)]
    for i, (tx, ty) in enumerate(tbl):
        if i == 3:        # overturned table with scattered chairs
            o = inst(table, 'caf_table_3_overturned', tx, ty, caf, rz=0.5, support=None); o.rotation_euler = (math.pi, 0, 0.5); o.location.z = 0.8; ground_object(o); o['support'] = 'floor'
            place_chairs_around(caf, chairs, rng, i, tx, ty, tipped=(0, 2), skip=(1,)); continue
        inst(table, f'caf_table_{i}', tx, ty, caf, rz=rng.uniform(-0.1, 0.1))
        place_chairs_around(caf, chairs, rng, i, tx, ty, skip=((2,) if i == 0 else (1,) if i == 2 else ()), tipped=((3,) if i == 1 else ()))
        inst(tray, f'caf_tray_{i}', tx - 0.35, ty, caf, z=0.77, support='table', rz=rng.uniform(-0.2, 0.2))
        inst(mug, f'caf_mug_{i}a', tx + 0.35, ty + 0.18, caf, z=0.77, support='table'); inst(bottle, f'caf_bottle_{i}', tx + 0.05, ty - 0.1, caf, z=0.77, support='table')
    o = inst(booth, 'caf_booth_0', 11.8, -79.5, caf, rz=0.0)
    for k, dx in enumerate((-0.6, 0.6)): inst(chairs[k], f'caf_booth_chair_{k}', 11.8 + dx, -77.6, caf, rz=math.pi + rng.uniform(-0.1, 0.1))
    # kiosk and queue
    inst(kiosk, 'order_kiosk', 13.2, -66.9, caf, rz=-math.pi / 2)
    for i in range(4): inst(stan, f'queue_stanchion_{i}', 14.6 + i * 1.0, -67.9 if i != 2 else -68.0, caf, rz=rng.uniform(-0.1, 0.1) if i != 3 else 0.0)
    for i in range(2): inst(vend[i], f'caf_vending_{i}', 12.0 + i * 1.05, -60.7, caf, rz=math.pi)
    o = inst(vend[2], 'caf_vending_tipped', 5.6 if False else 24.8, -62.7, caf, rz=0.0, support=None); o.rotation_euler = (0, math.pi / 2 * 0, 0)
    # ---------------- WEST: small living room
    inst(couch, 'living_couch_0', -3.4, -75.3, caf, rz=math.pi)
    inst(couch, 'living_couch_1', -6.7, -77.4, caf, rz=-math.pi / 2)
    o = inst(couch, 'living_armchair', 0.3, -77.4, caf, rz=math.pi / 2, scale=(0.5, 1, 1)); 
    ct = inst(table, 'coffee_table', -3.3, -77.5, caf, rz=0.05, scale=(0.75, 0.8, 0.55))
    inst(mug, 'living_mug', -3.0, -77.4, caf, z=0.44, support='table'); inst(bottle, 'living_bottle', -3.7, -77.55, caf, z=0.44, support='table')
    o = inst(flamp, 'living_floor_lamp', -7.1, -73.2, caf, support=None); o.rotation_euler = (0.9, 0.0, 0.4); ground_object(o); o['support'] = 'floor'
    inst(plants[1], 'plant_sw', -7.2, -79.2, caf); inst(plants[2], 'plant_living', 2.6, -79.2, caf); inst(plants[0], 'plant_ne', 25.2, -61.0, caf)
    # ---------------- WEST-NORTH: recreation corner
    inst(foos, 'rec_foosball', -3.4, -63.4, caf, rz=0.0); inst(airh, 'rec_airhockey', 1.6, -64.2, caf, rz=0.15)
    inst(hoops, 'rec_basketball', -6.2, -66.4, caf, rz=0.0, z=-0.005)
    wd = inst(dart, 'rec_dartboard', -0.4, -60.2, caf, rz=0.0, z=1.7, support=None); wd.rotation_euler = (0, 0, 0)
    wall_item(wd, 'y', -60.15, -1)
    box('rec_oche_line', -1.2, 0.4, -63.0 + 0.0, -62.95, 0.0, 0.004, F['signage'], caf, rgba=(0.85, 0.85, 0.8, 1))
    box('rec_rug', -7.6, 4.0, -68.0, -61.0, 0.0, 0.012, F['fabric'], caf, rgba=(0.14, 0.16, 0.2, 1), bev=0.004)
    for i, (x, y) in enumerate(((-2.0, -62.3), (3.3, -66.5))):
        o = inst(chairs[i], f'rec_chair_{i}', x, y, caf, support=None); o.rotation_euler = (math.pi / 2, 0, i * 2.0); ground_object(o); o['support'] = 'floor'
    inst(bins[0], 'caf_bin_0', -7.4, -68.0, caf); inst(bins[1], 'caf_bin_1', 25.4, -66.6, caf); inst(bins[2], 'caf_bin_2', 5.2, -61.0, caf)
    # ---------------- knocked-over chairs and a toppled table in the open middle of the room
    for pi, (px, py) in enumerate(((4.0, -73.4), (4.6, -66.0), (12.4, -66.2 + 5.0), (-1.2, -71.9 - 0.4), (13.8, -75.6), (1.0, -66.9))):
        if px > 9 and -71.2 < py < -68.8: py -= 2.0
        for k in range(4 if pi < 3 else 2):
            o = inst(chairs[(pi + k) % 3], f'pile_chair_{pi}_{k}', px + rng.uniform(-0.45, 0.45), py + rng.uniform(-0.45, 0.45), caf, support=None)
            o.rotation_euler = (rng.choice((-1.57, 1.57, 0.5, -0.5, 3.0)), rng.choice((0, 0, 0.4)), rng.uniform(0, 6.28)); ground_object(o); o['support'] = 'floor'
    o = inst(table, 'caf_table_toppled_mid', 3.6, -70.0 + 4.0, caf, support=None); o.rotation_euler = (3.14159, 0.12, 0.6); ground_object(o); o['support'] = 'floor'
    # ---------------- ceiling: only a few pendants still lit, the rest dead
    live = {(0, 1), (1, 2), (3, 0)}
    for j, (x, y) in enumerate(((-3.0, -75.0), (1.0, -64.0), (-4.0, -64.0), (17.0, -74.0), (21.5, -75.5), (13.5, -70.8), (21.0, -69.0), (17.0, -77.4))):
        inst(pend if j in (1, 4, 6) else pdead, f'caf_pendant_{j}', x, y, caf, z=3.7, support=None)
    build_counter_and_kitchen(F, C)
    build_lounge_and_walls(F, C)

def build_counter_and_kitchen(F, C):
    caf = C['CAFETERIA']
    # kitchen block: walls with a serving hatch, hood, range, steel tables, shelves
    m = MB([F['plaster'], F['steel_charcoal'], F['laminate'], F['emissive'], F['plastic']])
    cx0, cx1, cy0, cy1 = 14.0, 25.85, -64.0, -60.15
    LXa, LXb, LYa, LYb = LX(cx0), LX(cx1), LY(cy0), LY(cy1)
    m.use(0); m.box((LXa + LXb) / 2, LYa, 1.55, LXb - LXa, 0.15, 3.1, bevel=0.0)   # front wall (full) – hatch is cut by adding the opening pieces below instead
    m.bm.free(); m = MB([F['plaster'], F['steel_charcoal'], F['laminate'], F['emissive'], F['plastic']])
    # front wall pieces around the hatch (hatch x 15..25, z 1.1..2.3)
    def wbox(x0, x1, z0, z1, mi, rgba=(1, 1, 1, 1), bev=0.0, y0=LYa - 0.075, y1=LYa + 0.075):
        m.use(mi, rgba); m.box((LX(x0) + LX(x1)) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, bevel=bev)
    wbox(14.0, 25.9, 0.0, 1.1, 1, (0.12, 0.13, 0.14, 1), 0.01); wbox(14.0, 25.9, 2.3, 3.2, 0, (0.74, 0.69, 0.6, 1)); wbox(14.0, 15.0, 1.1, 2.3, 0, (0.74, 0.69, 0.6, 1)); wbox(25.0, 25.9, 1.1, 2.3, 0, (0.74, 0.69, 0.6, 1))
    # hatch frame and shelf
    wbox(15.0, 25.0, 1.07, 1.12, 1, (0.55, 0.57, 0.6, 1), 0.006, LYa - 0.2, LYa + 0.2); wbox(15.0, 25.0, 2.28, 2.33, 1, (0.1, 0.1, 0.11, 1), 0.006, LYa - 0.1, LYa + 0.1)
    # side wall west with a staff door gap, roof slab, hood
    m.use(0); m.box(LX(14.0), (LYa + LYb) / 2, 1.6, 0.15, LYb - LYa, 3.2)
    m.use(1, (0.1, 0.1, 0.11, 1)); m.box((LXa + LXb) / 2, (LYa + LYb) / 2, 3.2, LXb - LXa, LYb - LYa, 0.1, bevel=0.01)
    m.use(1, (0.6, 0.62, 0.65, 1)); m.box(LX(20.0), LYb - 1.0, 2.7, 4.2, 1.1, 0.7, bevel=0.02); m.box(LX(20.0), LYb - 1.0, 3.1, 0.8, 0.8, 0.4)
    # range, steel tables, shelves, sink
    m.use(1, (0.62, 0.64, 0.67, 1))
    for i, x in enumerate((16.0, 19.0, 22.0)):
        m.box(LX(x), LYb - 1.0, 0.45, 2.4, 0.9, 0.9, bevel=0.015)
        for k in range(4): m.use(1, (0.05, 0.05, 0.06, 1)); m.cyl(LX(x) - 0.7 + k * 0.45, LYb - 1.0, 0.9, 0.94, 0.12, seg=14); m.use(1, (0.62, 0.64, 0.67, 1))
    for k in range(3): m.box(LX(20.0), LYb - 0.2, 1.2 + k * 0.5, 9.0, 0.3, 0.03)
    for k in range(18): m.use(4, [(0.8, 0.8, 0.8, 1), (0.6, 0.35, 0.15, 1), (0.3, 0.45, 0.3, 1)][k % 3]); m.box(LX(16.2 + k * 0.5), LYb - 0.2, 1.3 + (k % 3) * 0.5, 0.3, 0.2, 0.2, bevel=0.01)
    m.use(3, (1, 0.93, 0.8, 1)); m.box(LX(20.0), LYb - 1.8, 3.1, 8.0, 0.1, 0.03)
    o = m.finish('kitchen_block', caf); o['support'] = 'floor'
    # serving counter
    m = MB([F['laminate'], F['steel_charcoal'], F['glass'], F['emissive'], F['plastic']])
    cy = LY(-65.2)
    m.use(1, (0.1, 0.11, 0.12, 1)); m.box(LX(20.2), cy, 0.45, 10.8, 1.2, 0.9, bevel=0.0)
    for k in range(9): m.use(1, (0.16, 0.17, 0.18, 1)); m.box(LX(15.4 + k * 1.2), cy - 0.61, 0.5, 1.12, 0.03, 0.78, bevel=0.012)
    m.use(0, (0.72, 0.68, 0.6, 1)); m.box(LX(20.2), cy, 0.93, 11.0, 1.3, 0.05, bevel=0.01)
    m.use(1, (0.5, 0.52, 0.55, 1)); m.box(LX(20.2), cy - 0.8, 0.82, 10.8, 0.04, 0.04); m.cyl_h(LX(20.2), cy - 0.85, 0.82, 10.8, 0.02, seg=8)
    m.use(1, (0.1, 0.11, 0.12, 1)); m.box(LX(20.2), cy - 0.3, 0.05, 10.8, 0.5, 0.1)
    for k in range(5): m.use(1, (0.1, 0.1, 0.11, 1)); m.box(LX(15.5 + k * 2.3), cy - 0.5, 1.2, 0.04, 0.04, 0.5, bevel=0.005)
    m.use(2); m.box(LX(20.2), cy - 0.5, 1.45, 10.4, 0.01, 0.5)
    m.use(3, (0.5, 0.42, 0.3, 1)); m.box(LX(20.2), cy - 0.5, 1.72, 10.4, 0.05, 0.02)
    for k in range(4): m.use(4, [(0.8, 0.8, 0.8, 1), (0.5, 0.5, 0.52, 1)][k % 2]); m.box(LX(16.0 + k * 2.6), cy, 1.0, 0.8, 0.5, 0.06, bevel=0.01)
    o = m.finish('serving_counter', caf); o['support'] = 'floor'
    # menu board over the hatch with text
    mb = box('menu_board', 15.0, 25.0, -64.2, -64.1, 2.4, 3.0, F['emissive'], caf, rgba=(0.02, 0.02, 0.022, 1), bev=0.01); wall_item(mb, 'y', -64.1, -1)
    cu = bpy.data.curves.new('menu_text', 'FONT'); cu.body = 'TODAY   SOUP  -  BREAD  -  TEA\nSTAFF MEAL  18:00'; cu.size = 0.2; cu.extrude = 0.004; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    t = bpy.data.objects.new('menu_text', cu); t.data.materials.append(F['signage']); caf.objects.link(t)
    t.rotation_euler = (math.pi / 2, 0, 0); t.location = (LX(20.0), LY(-64.2) - 0.02, 2.7)

def make_static_mat():
    if 'tv_static' in bpy.data.materials: return bpy.data.materials['tv_static']
    m = bpy.data.materials.new('tv_static'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); tx = nt.nodes.new('ShaderNodeTexNoise'); tc = nt.nodes.new('ShaderNodeTexCoord')
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.6
    tx.inputs['Scale'].default_value = 260; tx.inputs['Detail'].default_value = 0.0; tx.inputs['Roughness'].default_value = 1.0
    em.inputs['Strength'].default_value = 2.2
    nt.links.new(tc.outputs['Object'], tx.inputs['Vector']); nt.links.new(tx.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs[0], em.inputs['Color']); nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m

def build_lounge_and_walls(F, C):
    caf = C['CAFETERIA']
    # TV wall: timber slats and a screen showing static
    for k in range(14):
        box(f'tv_slat_{k}', -6.8 + k * 0.5, -6.4 + k * 0.5, -79.95, -79.78, 0.0, 3.4, F['timber'], caf, bev=0.01)
    static = make_static_mat()
    scr = box('tv_screen', -5.2, -0.6, -79.76, -79.72, 1.0, 2.5, static, caf, bev=0.008)
    bz = box('tv_bezel', -5.3, -0.5, -79.78, -79.68, 0.95, 2.55, F['plastic'], caf, rgba=(0.02, 0.02, 0.02, 1), bev=0.012); wall_item(bz, 'y', -79.85, +1)
    # rug
    box('lounge_rug', -7.6, 1.6, -80.0, -73.6, 0.0, 0.015, F['fabric'], caf, rgba=(0.24, 0.1, 0.08, 1), bev=0.004)
    # notice board with papers, west wall south of the door
    nb = box('notice_board', -7.9, -7.84, -77.0, -73.0, 1.0, 2.2, F['timber'], caf, bev=0.01); wall_item(nb, 'x', -7.84, +1)
    cork = box('notice_cork', -7.85, -7.83, -76.85, -73.15, 1.1, 2.1, F['props'], caf, rgba=(0.6, 0.45, 0.28, 1)); 
    rng = random.Random(3)
    for k in range(18):
        y = -76.6 + (k % 6) * 0.62; z = 1.2 + (k // 6) * 0.3
        box(f'notice_paper_{k}', -7.835, -7.82, y, y + 0.34, z, z + 0.24, F['signage'], caf, rgba=rng.choice([(0.95, 0.95, 0.9, 1), (0.95, 0.85, 0.3, 1), (0.8, 0.9, 0.95, 1)]))
    # wall decor: clock, sconces on pilasters, exit signs, posters, extinguisher
    for i, (x, y) in enumerate(((-3.0, -79.84), (14.0, -79.84), (21.0, -60.16))):
        pass
    for i, y in enumerate((-77.0, -73.0, -67.0, -63.0)): box(f'sconce_{i}', -7.8, -7.62, y - 0.1, y + 0.1, 2.4, 2.8, F['emissive'], caf, rgba=(1, 0.82, 0.55, 1) if i == 2 else (0.1, 0.09, 0.08, 1), bev=0.012)
    box('exit_sign_W', -7.85, -7.7, -71.0, -69.0, 3.0, 3.25, F['emissive'], caf, rgba=(0.1, 0.8, 0.3, 1), bev=0.01)
    box('exit_sign_E', 25.7, 25.85, -71.0, -69.0, 3.0, 3.25, F['emissive'], caf, rgba=(0.1, 0.8, 0.3, 1), bev=0.01)
    ck = cylinder('wall_clock', 0, 0, 0.28, -0.03, 0.03, F['signage'], caf, rgba=(0.55, 0.52, 0.45, 1), plan=False); ck.rotation_euler = (math.pi / 2, 0, 0)
    ck.location = (LX(3.0), LY(-79.84), 3.0); wall_item(ck, 'y', -79.85, +1)
    for i, x in enumerate((-4.0, 0.0, 12.0, 19.0, 22.5)):
        b = box(f'poster_{i}', x, x + 0.8, -79.86, -79.84, 1.5, 2.4, F['signage'], caf, rgba=[(0.8, 0.3, 0.1, 1), (0.2, 0.4, 0.6, 1), (0.85, 0.8, 0.5, 1), (0.3, 0.5, 0.3, 1), (0.6, 0.2, 0.2, 1)][i], bev=0.008); wall_item(b, 'y', -79.85, +1)
    fe = box('fire_ext_box', -7.88, -7.62, -68.6, -68.2, 0.9, 1.5, F['plastic'], caf, rgba=(0.7, 0.1, 0.08, 1), bev=0.01); wall_item(fe, 'x', -7.85, +1)
    # skirting boards along the interior faces
    box('skirt_S', -8, 26, -79.85, -79.8, 0, 0.12, F['rubber'], caf); box('skirt_W', -7.85, -7.8, -80, -60, 0, 0.12, F['rubber'], caf); box('skirt_E', 25.8, 25.85, -80, -60, 0, 0.12, F['rubber'], caf)
