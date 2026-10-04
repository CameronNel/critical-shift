"""Cafeteria / chill room at spawn-room quality: east dining with kiosk and serving counter, west living room, recreation corner."""
from fe_kit import *
from fe_assets_int import *
from fe_yard import inst

CAF = (-8.0, 26.0, -80.0, -60.0)

def p_table_low(F, P):
    return coffee_table(F, P)

def serving_counter(F, P, L=10.8):
    """Serving counter: laminate top, steel front, glass sneeze guard, hot wells with pans, tray rail, coffee machine and till."""
    m = mb(F)
    m.rbox(0, 0, 0.45, L, 1.1, 0.9, 0.02, mi=I['steel_charcoal'], rgba=(0.1, 0.11, 0.13, 1))
    for k in range(int(L / 1.2)):
        m.rbox(-L / 2 + 0.6 + k * 1.2, -0.555, 0.5, 1.12, 0.03, 0.78, 0.012, mi=I['steel_charcoal'], rgba=(0.14, 0.17, 0.3, 1))
    m.rbox(0, 0.02, 0.93, L + 0.1, 1.3, 0.05, 0.02, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    m.rbox(0, -0.08, 0.1, L - 0.1, 0.9, 0.2, 0.02, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
    # tray rail
    m.between((-L / 2 - 0.2, -0.88, 0.82), (L / 2 + 0.2, -0.88, 0.82), 0.02, seg=10, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int(L / 2.4) + 1): m.between((-L / 2 + k * 2.4, -0.88, 0.82), (-L / 2 + k * 2.4, -0.64, 0.92), 0.012, seg=6, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    # sneeze guard and heat lamps
    for k in range(int(L / 2.4) + 1): m.rbox(-L / 2 + k * 2.4, -0.3, 1.2, 0.03, 0.03, 0.55, 0.008, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    m.rbox(0, -0.3, 1.3, L - 0.1, 0.012, 0.4, 0.004, rot=(-0.25, 0, 0), mi=I['glass'])
    m.rbox(0, -0.3, 1.52, L - 0.1, 0.1, 0.04, 0.015, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int(L / 1.2)): m.rbox(-L / 2 + 0.6 + k * 1.2, -0.3, 1.5, 0.9, 0.02, 0.012, 0.004, mi=I['emissive'], rgba=(1.0, 0.7, 0.4, 1))
    # hot wells with pans of food
    foods = [(0.65, 0.4, 0.18, 1), (0.8, 0.65, 0.2, 1), (0.35, 0.5, 0.15, 1), (0.7, 0.2, 0.12, 1), (0.85, 0.8, 0.6, 1)]
    for k in range(int((L - 3.2) / 1.1)):
        x = -L / 2 + 0.9 + k * 1.1
        m.rbox(x, 0.1, 0.96, 0.95, 0.52, 0.04, 0.012, mi=I['steel_charcoal'], rgba=(0.7, 0.72, 0.74, 1))
        m.cylz(x, 0.1, 0.96, 0.975, 0.0, seg=3) if False else None
        m.rbox(x, 0.1, 0.995, 0.86, 0.44, 0.02, 0.01, mi=I['props'], rgba=foods[k % 5])
    # coffee machine, till, bread basket
    xm = L / 2 - 0.7
    m.rbox(xm, 0.05, 1.18, 0.6, 0.5, 0.5, 0.04, mi=I['steel_charcoal'], rgba=(0.12, 0.13, 0.15, 1)); m.rbox(xm, -0.21, 1.2, 0.5, 0.02, 0.3, 0.01, mi=I['screen'], rgba=(0.9, 0.6, 0.2, 1))
    for sx in (-0.15, 0.15): m.cylz(xm + sx, -0.18, 0.97, 1.07, 0.03, seg=12, mi=I['steel_charcoal'], rgba=(0.6, 0.62, 0.64, 1))
    m.rbox(-L / 2 + 0.6, 0.15, 1.04, 0.4, 0.3, 0.14, 0.03, mi=I['plastic'], rgba=(0.12, 0.13, 0.15, 1)); m.rbox(-L / 2 + 0.6, 0.02, 1.15, 0.28, 0.01, 0.2, 0.004, mi=I['screen'], rgba=(0.3, 0.7, 0.4, 1), rot=(-0.4, 0, 0))
    return m.finish('proto_serving_counter', P)

def kitchen_block(F, P):
    """Back-of-house seen through the hatch: range with extractor hood, steel benches, shelving with tubs, fridge."""
    m = mb(F); L = 11.8
    steel = (0.62, 0.64, 0.67, 1); dark = (0.1, 0.11, 0.12, 1)
    m.rbox(0, 0, 3.15, L, 3.8, 0.12, 0.02, mi=I['steel_charcoal'], rgba=dark)
    for k, x in enumerate((-4.2, -1.4, 1.4)):
        m.rbox(x, 1.0, 0.45, 2.4, 0.9, 0.9, 0.02, mi=I['steel_charcoal'], rgba=steel)
        for b in range(4):
            m.cylz(x - 0.75 + b * 0.5, 1.0, 0.9, 0.93, 0.13, seg=20, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
        m.rbox(x, 1.0, 0.45, 2.0, 0.02, 0.6, 0.006, rot=(0, 0, 0), mi=I['steel_charcoal'], rgba=(0.9, 0.9, 0.92, 1)) if False else None
        for kn in range(4): m.add(p_cyl(0.025, 0.03, 10), (x - 0.75 + kn * 0.5, 0.54, 0.7), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.1, 0.1, 0.11, 1))
    m.lathe([(0.0, 0.0), (1.2, 0.0), (1.1, 0.5), (0.35, 0.8), (0.3, 1.0), (0.0, 1.0)], loc=(-2.8, 1.0, 2.1), seg=4, mi=I['steel_charcoal'], rgba=steel, rot=(0, 0, math.pi / 4), scale=(2.5, 0.9, 1.0))
    m.rbox(-2.8, 1.0, 3.0, 0.5, 0.5, 0.3, 0.03, mi=I['steel_charcoal'], rgba=steel)
    for x in (2.2, 4.4):
        m.rbox(x, -1.4, 0.45, 1.9, 0.8, 0.9, 0.02, mi=I['steel_charcoal'], rgba=steel)
        m.rbox(x, -1.4, 0.92, 1.9, 0.8, 0.04, 0.012, mi=I['steel_charcoal'], rgba=(0.7, 0.72, 0.75, 1))
    m.rbox(5.2, 1.0, 0.95, 0.9, 0.9, 1.9, 0.03, mi=I['steel_charcoal'], rgba=(0.85, 0.86, 0.88, 1))
    m.rbox(5.2, 0.54, 1.3, 0.04, 0.03, 0.7, 0.008, mi=I['steel_charcoal'], rgba=dark)
    for k in range(3): m.rbox(0, 1.8, 1.0 + k * 0.5, 9.0, 0.35, 0.03, 0.006, mi=I['steel_charcoal'], rgba=steel)
    rnd = random.Random(8)
    for k in range(3):
        for j in range(16):
            x = -4.2 + j * 0.55
            m.rbox(x, 1.8, 1.18 + k * 0.5, 0.36, 0.25, 0.28, 0.015, mi=I['plastic'], rgba=rnd.choice([(0.88, 0.88, 0.85, 1), (0.6, 0.35, 0.15, 1), (0.3, 0.45, 0.3, 1), (0.8, 0.2, 0.12, 1)]))
    m.rbox(0, 1.95, 1.8, 9.0, 0.02, 2.4, 0.004, mi=I['laminate'], rgba=(0.82, 0.8, 0.74, 1))
    return m.finish('proto_kitchen_block', P)

def ceiling_strip(F, P):
    m = mb(F)
    m.rbox(0, 0, 0, 0.3, 1.5, 0.07, 0.02, mi=I['trim'], rgba=(0.82, 0.82, 0.8, 1))
    m.rbox(0, 0, -0.04, 0.22, 1.42, 0.012, 0.004, mi=I['emissive'], rgba=(1.0, 0.95, 0.85, 1))
    return m.finish('proto_ceiling_strip', P)

def planter_long(F, P):
    m = mb(F)
    m.rbox(0, 0, 0.27, 1.8, 0.5, 0.54, 0.03, mi=I['timber'], rgba=(0.34, 0.2, 0.09, 1))
    for k in range(5): m.rbox(-0.72 + k * 0.36, 0.252, 0.27, 0.3, 0.008, 0.46, 0.003, mi=I['timber'], rgba=(0.28, 0.16, 0.07, 1))
    m.rbox(0, 0, 0.555, 1.7, 0.4, 0.04, 0.01, mi=I['props'], rgba=(0.1, 0.07, 0.045, 1))
    rnd = random.Random(2)
    for k in range(3):
        for i in range(26):
            a = rnd.uniform(0, 6.28); d = rnd.uniform(0, 0.12)
            m.leaf((-0.6 + k * 0.6 + math.cos(a) * d, math.sin(a) * d * 0.5, 0.58), rnd.uniform(0.25, 0.4), rnd.uniform(0.04, 0.06), bend=-rnd.uniform(0, 0.2), droop=rnd.uniform(0.2, 0.6), yaw=a - math.pi / 2, pitch=rnd.uniform(0.7, 1.3), segs=4, mi=I['foliage'], rgba=rnd.choice([(0.11, 0.3, 0.09, 1), (0.15, 0.35, 0.1, 1)]))
    return m.finish('proto_planter_long', P)

def totem(F, P):
    m = mb(F)
    m.rbox(0, 0, 1.05, 0.9, 0.16, 2.1, 0.02, mi=I['plastic'], rgba=(0.12, 0.14, 0.3, 1))
    m.rbox(0, 0.085, 1.45, 0.76, 0.01, 0.9, 0.004, mi=I['screen'], rgba=(0.9, 0.78, 0.5, 1))
    for k in range(5): m.rbox(0.0, 0.092, 1.7 - k * 0.15, 0.55 - (k % 2) * 0.2, 0.004, 0.035, 0.001, mi=I['signage'], rgba=(0.12, 0.1, 0.07, 1))
    m.rbox(0, 0.085, 0.7, 0.6, 0.01, 0.3, 0.004, mi=I['signage'], rgba=(0.8, 0.38, 0.06, 1))
    m.rbox(0, 0.0, 0.02, 1.0, 0.3, 0.04, 0.01, mi=I['steel_charcoal'], rgba=(0.08, 0.08, 0.09, 1))
    return m.finish('proto_totem', P)

def pc(chairs, i): return chairs[i % len(chairs)]

def build_cafeteria(F, C):
    caf = C['CAFETERIA']; P = collection('PROTOTYPES'); rng = random.Random(5)
    chairs = [chair(F, P, c, f'chair_{i}') for i, c in enumerate(((0.55, 0.16, 0.09, 1), (0.12, 0.17, 0.35, 1), (0.74, 0.46, 0.1, 1)))]
    tbl = table(F, P); bth = booth(F, P); vend = [vending(F, P, c, s, f'vending_{s}') for s, c in enumerate(((0.62, 0.11, 0.09, 1), (0.1, 0.22, 0.48, 1)))]
    cof = coffee_table(F, P); sof = sofa(F, P); arm = armchair(F, P)
    plants = [plant_leafy(F, P, 1, 1.5), plant_leafy(F, P, 2, 1.2), plant_spiky(F, P, 3, 1.15)]
    pend = pendant(F, P); mg = mug(F, P); tr = tray(F, P); bt = bottle(F, P); lamp = floor_lamp(F, P); bn = bin_(F, P)
    foos = foosball(F, P); airh = airhockey(F, P); hoopm = hoops(F, P); dart = dartboard(F, P); ksk = kiosk(F, P); stan = stanchion(F, P); tvp = tv(F, P)
    strip = ceiling_strip(F, P)
    # ---------------- EAST: small dining area facing the serving area
    tbls = [(16.7, -73.6), (21.5, -73.6), (16.7, -77.2), (21.5, -77.2)]
    for i, (tx, ty) in enumerate(tbls):
        inst(tbl, f'caf_table_{i}', tx, ty, caf, rz=0.0)
        for k, (dx, dy, rz) in enumerate(((-0.45, -0.7, 0), (0.45, -0.7, 0), (-0.45, 0.7, math.pi), (0.45, 0.7, math.pi))):
            if (i, k) in ((1, 2), (3, 1)): continue
            inst(pc(chairs, i + k), f'caf_chair_{i}_{k}', tx + dx + rng.uniform(-0.04, 0.04), ty + dy + (0.08 if dy < 0 else -0.08) * rng.choice((0, 1)), caf, rz=rz + rng.uniform(-0.1, 0.1))
        inst(tr, f'caf_tray_{i}', tx - 0.4, ty, caf, z=0.77, support='table', rz=rng.uniform(-0.2, 0.2))
        inst(mg, f'caf_mug_{i}', tx + 0.4, ty + 0.18, caf, z=0.77, support='table'); inst(bt, f'caf_bottle_{i}', tx + 0.05, ty - 0.12, caf, z=0.77, support='table')
    inst(bth, 'caf_booth_0', 12.0, -79.5, caf, rz=0.0)
    for k, dx in enumerate((-0.6, 0.6)): inst(pc(chairs, k), f'caf_booth_chair_{k}', 12.0 + dx, -77.6, caf, rz=math.pi)
    inst(ksk, 'order_kiosk', 13.1, -66.8, caf, rz=-math.pi / 2)
    for i in range(4): inst(stan, f'queue_stanchion_{i}', 14.6 + i * 1.0, -67.9, caf, rz=0.0)
    for i in range(2): inst(vend[i], f'caf_vending_{i}', 12.05 + i * 1.08, -60.6, caf, rz=math.pi)
    inst(bn, 'caf_bin_E', 25.4, -66.6, caf); inst(bn, 'caf_bin_N', 10.4, -61.0, caf); inst(plants[0], 'plant_ne', 25.2, -61.0, caf)
    # ---------------- WEST: small living room
    inst(sof, 'living_sofa', -3.4, -75.4, caf, rz=math.pi)
    inst(sof, 'living_sofa_side', -6.7, -77.4, caf, rz=-math.pi / 2, scale=(0.82, 1, 1))
    inst(arm, 'living_armchair', 0.5, -77.0, caf, rz=math.pi / 2 + 0.25)
    inst(cof, 'coffee_table', -3.3, -77.4, caf, rz=0.0)
    inst(mg, 'living_mug', -3.0, -77.35, caf, z=0.42, support='table'); inst(bt, 'living_bottle', -3.7, -77.5, caf, z=0.42, support='table')
    inst(lamp, 'living_floor_lamp', -7.2, -73.2, caf); inst(plants[1], 'plant_living', 2.7, -79.2, caf); inst(plants[2], 'plant_sw', -7.2, -79.2, caf)
    box('living_rug', -7.4, 2.6, -79.6, -73.8, 0.0, 0.014, F['fabric'], caf, rgba=(0.5, 0.2, 0.13, 1), bev=0.004)
    box('living_rug_inner', -6.4, 1.6, -79.0, -74.6, 0.014, 0.02, F['fabric'], caf, rgba=(0.82, 0.74, 0.58, 1), bev=0.002)
    # TV on a slatted wall
    for k in range(15): box(f'tv_slat_{k}', -7.0 + k * 0.5, -6.55 + k * 0.5, -79.97, -79.84, 0.0, 3.3, F['timber'], caf, bev=0.008)
    t = inst(tvp, 'living_tv', -2.7, -79.8, caf, z=1.0, rz=math.pi, support=None); wall_item(t, 'y', -79.85, +1)
    # ---------------- NORTH-WEST: recreation corner
    box('rec_rug', -7.6, 4.2, -68.2, -61.0, 0.0, 0.014, F['fabric'], caf, rgba=(0.08, 0.1, 0.26, 1), bev=0.004)
    inst(foos, 'rec_foosball', -3.4, -63.4, caf, rz=0.0); inst(airh, 'rec_airhockey', 1.7, -64.4, caf, rz=0.0)
    inst(hoopm, 'rec_basketball', -6.15, -66.6, caf, rz=math.pi, z=-0.01)
    dd = inst(dart, 'rec_dartboard', -0.4, -60.17, caf, z=1.73, support=None); wall_item(dd, 'y', -60.15, -1)
    box('rec_oche', -1.0, 0.2, -62.57, -62.52, 0.0, 0.006, F['signage'], caf, rgba=(0.9, 0.88, 0.8, 1))
    inst(plants[1], 'plant_rec', -7.2, -61.0, caf, rz=1.0)
    # ---------------- ceiling: lit strips on the same grid as the fills, pendants over the dining area
    for i, x in enumerate((-2, 6, 14, 22)):
        for j, y in enumerate((-64.5, -70, -75.5)): inst(strip, f'caf_light_strip_{i}{j}', x, y, caf, z=4.93, rz=math.pi / 2, support=None)
    for j, (x, y) in enumerate(((16.7, -73.6), (21.5, -73.6), (16.7, -77.2), (21.5, -77.2))): inst(pend, f'caf_pendant_{j}', x, y, caf, z=3.3, support=None)
    for j, (x, y) in enumerate(((-3.4, -75.4), (-1.0, -77.6))): inst(pend, f'caf_pendant_L{j}', x, y, caf, z=3.4, support=None)
    cnt = inst(P_counter(F, P), 'serving_counter', 20.2, -65.4, caf)
    inst(P_kitchen(F, P), 'kitchen_block', 20.0, -62.1, caf)
    pl = planter_long(F, P); tt = totem(F, P)
    for i in range(4): inst(pl, f'divider_rec_{i}', -5.8 + i * 1.95, -67.9, caf, rz=0.0)
    for i in range(3): inst(pl, f'divider_dining_{i}', 14.0, -72.4 - i * 1.95, caf, rz=math.pi / 2)
    inst(tt, 'directory_totem', 10.8, -66.5, caf, rz=-math.pi / 2 if False else 0.0)
    build_walls_and_hatch(F, C)

_pc = {}
def P_counter(F, P):
    if 'c' not in _pc: _pc['c'] = serving_counter(F, P, 10.8)
    return _pc['c']
def P_kitchen(F, P):
    if 'k' not in _pc: _pc['k'] = kitchen_block(F, P)
    return _pc['k']

def build_walls_and_hatch(F, C):
    """Kitchen front wall with a serving hatch and half-lowered shutter; menu board."""
    caf = C['CAFETERIA']
    y = -64.0
    box('kitchen_front_lo', 14.0, 25.9, y - 0.08, y + 0.08, 0.0, 1.0, F['dado'], caf, bev=0.01)
    box('kitchen_front_hi', 14.0, 25.9, y - 0.08, y + 0.08, 2.4, 3.3, F['plaster'], caf)
    box('kitchen_front_L', 14.0, 15.0, y - 0.08, y + 0.08, 1.0, 2.4, F['plaster'], caf); box('kitchen_front_R', 25.0, 25.9, y - 0.08, y + 0.08, 1.0, 2.4, F['plaster'], caf)
    box('hatch_frame_sill', 15.0, 25.0, y - 0.2, y + 0.2, 0.98, 1.03, F['steel_charcoal'], caf, bev=0.006)
    box('hatch_frame_head', 15.0, 25.0, y - 0.1, y + 0.1, 2.33, 2.4, F['steel_charcoal'], caf, bev=0.006)
    for k in range(8): box(f'hatch_shutter_{k}', 15.0, 25.0, y - 0.04, y + 0.04, 2.0 + k * 0.04, 2.032 + k * 0.04, F['steel_charcoal'], caf, rgba=None)
    box('kitchen_side_W', 13.9, 14.05, -64.0, -60.15, 0.0, 3.3, F['plaster'], caf)
    mbd = box('menu_board', 15.2, 24.8, -64.19, -64.15, 2.45, 3.1, F['screen'], caf, rgba=(0.05, 0.06, 0.08, 1), bev=0.01); wall_item(mbd, 'y', -64.15, -1)
    for k in range(3):
        box(f'menu_col_{k}', 15.6 + k * 3.0, 17.9 + k * 3.0, -64.2, -64.19, 2.55, 3.0, F['screen'], caf, rgba=(0.9, 0.78, 0.5, 1))
        for r in range(5): box(f'menu_line_{k}_{r}', 15.8 + k * 3.0, 17.4 - (r % 2) * 0.5 + k * 3.0, -64.205, -64.2, 2.62 + r * 0.08, 2.66 + r * 0.08, F['screen'], caf, rgba=(0.12, 0.1, 0.07, 1))
