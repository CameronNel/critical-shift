"""Cafeteria / chill room at spawn-room quality: east dining with kiosk and serving counter, west living room, recreation corner."""
from fe_kit import *
from fe_assets_int import *
from fe_yard import inst
from fe_assets_caf2 import *

CAF = (-8.0, 26.0, -80.0, -60.0)

def p_table_low(F, P):
    return coffee_table(F, P)

def serving_counter(F, P, L=10.8):
    """Serving counter: laminate top, steel front, glass sneeze guard, hot wells with pans, tray rail, coffee machine and till."""
    m = mb(F)
    m.rbox(0, 0, 0.45, L, 1.1, 0.9, 0.02, mi=I['steel_charcoal'], rgba=(0.1, 0.11, 0.13, 1))
    for k in range(int(L / 1.2)):
        xd = -L / 2 + 0.6 + k * 1.2
        m.rbox(xd, -0.555, 0.5, 1.12, 0.03, 0.78, 0.012, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.85, 1))
        m.rbox(xd + 0.46, -0.585, 0.62, 0.025, 0.025, 0.3, 0.008, mi=I['steel_charcoal'], rgba=(0.06, 0.06, 0.07, 1))
    m.rbox(0, 0.02, 0.93, L + 0.1, 1.3, 0.05, 0.02, mi=I['laminate'], rgba=(0.72, 0.64, 0.52, 1))
    m.rbox(0, -0.08, 0.1, L - 0.1, 0.9, 0.2, 0.02, mi=I['steel_charcoal'], rgba=(0.05, 0.05, 0.06, 1))
    # tray rail
    m.between((-L / 2 - 0.2, -0.88, 0.82), (L / 2 + 0.2, -0.88, 0.82), 0.02, seg=10, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int(L / 2.4) + 1): m.between((-L / 2 + k * 2.4, -0.88, 0.82), (-L / 2 + k * 2.4, -0.64, 0.92), 0.012, seg=6, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    # sneeze guard and heat lamps
    for k in range(int(L / 2.4) + 1): m.rbox(-L / 2 + k * 2.4, -0.3, 1.2, 0.03, 0.03, 0.55, 0.008, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    m.rbox(0, -0.3, 1.3, L - 0.1, 0.012, 0.4, 0.004, rot=(-0.25, 0, 0), mi=I['glass'])
    m.rbox(0, -0.3, 1.52, L - 0.1, 0.1, 0.04, 0.015, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
    for k in range(int(L / 1.2)): m.rbox(-L / 2 + 0.6 + k * 1.2, -0.3, 1.5, 0.9, 0.02, 0.012, 0.004, mi=I['emissive'], rgba=(1.0, 0.7, 0.4, 1))
    # hot wells with pans of food
    foods = [(0.65, 0.4, 0.18, 1), (0.8, 0.65, 0.2, 1), (0.35, 0.5, 0.15, 1), (0.7, 0.2, 0.12, 1), (0.85, 0.8, 0.6, 1)]
    for k in range(int((L - 3.2) / 1.1)):
        x = -L / 2 + 0.9 + k * 1.1
        m.rbox(x, 0.1, 0.975, 0.95, 0.52, 0.06, 0.012, mi=I['steel_brushed'], rgba=(0.7, 0.72, 0.74, 1))
        m.rbox(x, 0.1, 0.99, 0.86, 0.44, 0.05, 0.01, mi=I['props'], rgba=(0.5, 0.5, 0.52, 1))
        m.sphere(x, 0.1, 1.02, 0.4, 0.2, 0.07, rings=8, seg=14, mi=I['props'], rgba=foods[k % 5])
        m.between((x + 0.18, 0.2, 1.1), (x + 0.3, 0.32, 1.0), 0.008, seg=6, mi=I['steel_brushed'], rgba=(0.8, 0.82, 0.84, 1))
    # coffee machine, till, bread basket
    xm = L / 2 - 0.7
    m.rbox(xm, 0.05, 1.18, 0.6, 0.5, 0.5, 0.04, mi=I['steel_charcoal'], rgba=(0.12, 0.13, 0.15, 1)); m.rbox(xm, -0.21, 1.2, 0.5, 0.02, 0.3, 0.01, mi=I['screen'], rgba=(0.9, 0.6, 0.2, 1))
    for sx in (-0.15, 0.15): m.cylz(xm + sx, -0.18, 0.97, 1.07, 0.03, seg=12, mi=I['steel_brushed'], rgba=(0.6, 0.62, 0.64, 1))
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
        m.rbox(x, 1.0, 0.45, 2.0, 0.02, 0.6, 0.006, rot=(0, 0, 0), mi=I['steel_brushed'], rgba=(0.9, 0.9, 0.92, 1)) if False else None
        for kn in range(4): m.add(p_cyl(0.025, 0.03, 10), (x - 0.75 + kn * 0.5, 0.54, 0.7), (math.pi / 2, 0, 0), mi=I['plastic'], rgba=(0.1, 0.1, 0.11, 1))
    m.lathe([(0.0, 0.0), (1.2, 0.0), (1.1, 0.5), (0.35, 0.8), (0.3, 1.0), (0.0, 1.0)], loc=(-2.8, 1.0, 2.1), seg=4, mi=I['steel_charcoal'], rgba=steel, rot=(0, 0, math.pi / 4), scale=(2.5, 0.9, 1.0))
    m.rbox(-2.8, 1.0, 3.0, 0.5, 0.5, 0.3, 0.03, mi=I['steel_charcoal'], rgba=steel)
    for x in (2.2, 4.4):
        m.rbox(x, -1.4, 0.45, 1.9, 0.8, 0.9, 0.02, mi=I['steel_charcoal'], rgba=steel)
        m.rbox(x, -1.4, 0.92, 1.9, 0.8, 0.04, 0.012, mi=I['steel_brushed'], rgba=(0.7, 0.72, 0.75, 1))
    m.rbox(5.2, 1.0, 0.95, 0.9, 0.9, 1.9, 0.03, mi=I['steel_brushed'], rgba=(0.85, 0.86, 0.88, 1))
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
    m.rbox(0, 0.0, 0.02, 1.0, 0.3, 0.04, 0.01, mi=I['steel_charcoal'], rgba=(0.08, 0.08, 0.09, 1))
    return m.finish('proto_totem', P)

def pc(chairs, i): return chairs[i % len(chairs)]

def rug_object(F, coll, name, x0, x1, y0, y1, img, t=0.016):
    """Rug: a thin slab whose top face carries a baked pattern texture (UV 0..1 across the top)."""
    from fe_assets_caf2 import rug_texture
    rug_texture(img.replace('.png', ''), 'game' if 'game' in img else 'lounge', (1024, 1024) if (x1 - x0) / (y1 - y0) < 1.15 else (1200, 1024))
    mat = make_img_mat(name + '_mat', img, 0.0, 0.95, 0.3)
    me = bpy.data.meshes.new(name); X0, X1, Y0, Y1 = LX(x0), LX(x1), LY(y0), LY(y1)
    verts = [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0), (X0, Y0, t), (X1, Y0, t), (X1, Y1, t), (X0, Y1, t)]
    me.from_pydata(verts, [], [(4, 5, 6, 7), (0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]); me.update()
    uv = me.uv_layers.new(name='UVMap')
    for pi, p in enumerate(me.polygons):
        for li, (u, v) in zip(range(p.loop_start, p.loop_start + 4), ((0, 0), (1, 0), (1, 1), (0, 1)) if pi == 0 else ((0.5, 0.5),) * 4): uv.data[li].uv = (u, v)
    me.materials.append(mat); o = bpy.data.objects.new(name, me); coll.objects.link(o); o['support'] = 'rug'; return o

def build_cafeteria(F, C):
    caf = C['CAFETERIA']; P = collection('PROTOTYPES'); rng = random.Random(5)
    chairs = [chair(F, P, c, f'chair_{i}') for i, c in enumerate(((0.55, 0.16, 0.09, 1), (0.12, 0.17, 0.35, 1), (0.74, 0.46, 0.1, 1), (0.14, 0.34, 0.28, 1)))]
    tbl = table(F, P); bth = booth(F, P); vend = [vending(F, P, c, s, f'vending_{s}') for s, c in enumerate(((0.62, 0.11, 0.09, 1), (0.1, 0.22, 0.48, 1)))]
    cof = coffee_table(F, P); sof = sofa(F, P); arm = armchair(F, P)
    plants = [plant_leafy(F, P, 1, 1.5), plant_leafy(F, P, 2, 1.2), plant_spiky(F, P, 3, 1.15)]
    pend = pendant(F, P); mg = mug(F, P); tr = tray(F, P); bt = bottle(F, P); lamp = floor_lamp(F, P); bn = bin_(F, P)
    foos = foosball(F, P); hoopm = hoops(F, P); dart = dartboard(F, P); ksk = kiosk_v2(F, P); stan = stanchion(F, P); tvp = tv(F, P)
    strip = ceiling_strip(F, P); ts = table_set(F, P); wc = water_cooler(F, P); fr = fridge_display(F, P); bc = bookcase(F, P); mw = microwave_bench(F, P)
    cr = coat_rack(F, P); wfs = wet_floor_sign(F, P); mpb = mop_bucket(F, P); wsh = [wall_shelf(F, P, s) for s in range(2)]
    # ---------------- DINING HALL: the main cafeteria. Twelve four-seat tables in blocks, a booth bank on the south wall
    tbls = []
    for cx in (15.4, 19.3, 23.2):                      # east block, south of the medical lane
        for cy in (-73.6, -77.3): tbls.append((cx, cy))
    tbls += [(2.8, -63.4), (2.8, -66.4), (11.9, -73.6), (4.0, -74.4)]  # north-middle pair and a table beside the lane
    for i, (tx, ty) in enumerate(tbls):
        inst(tbl, f'caf_table_{i}', tx, ty, caf, rz=0.0)
        for k, (dx, dy, rz) in enumerate(((-0.45, -0.7, 0), (0.45, -0.7, 0), (-0.45, 0.7, math.pi), (0.45, 0.7, math.pi))):
            if (i + k) % 11 == 5: continue
            inst(pc(chairs, i + k), f'caf_chair_{i}_{k}', tx + dx + rng.uniform(-0.04, 0.04), ty + dy + (0.1 if dy < 0 else -0.1) * rng.choice((0, 1, 1)), caf, rz=rz + rng.uniform(-0.12, 0.12))
        inst(tr, f'caf_tray_{i}', tx - 0.4, ty, caf, z=0.77, support='table', rz=rng.uniform(-0.2, 0.2))
        inst(ts, f'caf_tableset_{i}', tx + 0.05, ty - 0.05, caf, z=0.77, support='table', rz=rng.uniform(-0.3, 0.3))
        if i % 2 == 0: inst(mg, f'caf_mug_{i}', tx + 0.4, ty + 0.18, caf, z=0.77, support='table')
        if i % 3 == 0: inst(bt, f'caf_bottle_{i}', tx + 0.3, ty - 0.2, caf, z=0.77, support='table')
    # booth bank along the south wall
    inst(bth, 'caf_booth_0', 12.0, -79.5, caf, rz=0.0); inst(bth, 'caf_booth_1', 4.4, -79.5, caf, rz=0.0)
    for k, dx in enumerate((-0.6, 0.6)): inst(pc(chairs, k + 2), f'caf_booth_chair_w{k}', 4.4 + dx, -77.15, caf, rz=math.pi)
    for k, dx in enumerate((-0.6, 0.6)): inst(pc(chairs, k), f'caf_booth_chair_{k}', 12.0 + dx, -77.15, caf, rz=math.pi)
    # ---------------- SERVING AREA (north-east): counter, kitchen, kiosk, queue, drinks, cutlery
    inst(ksk, 'order_kiosk', 13.1, -66.8, caf, rz=-math.pi / 2)
    for i in range(4): inst(stan, f'queue_stanchion_{i}', 14.6 + i * 1.0, -67.9, caf, rz=0.0)
    for i in range(2): inst(vend[i], f'caf_vending_{i}', 12.05 + i * 1.08, -60.6, caf, rz=math.pi)
    inst(fr, 'caf_fridge_0', 25.45, -72.9, caf, rz=math.pi / 2)
    inst(wc, 'caf_water_cooler', 25.55, -74.3, caf, rz=math.pi / 2)
    inst(mw, 'caf_microwave_bench', 21.5, -79.6, caf, rz=0.0)
    inst(bn, 'caf_bin_E', 25.45, -75.3, caf); inst(bn, 'caf_bin_N', 10.4, -61.0, caf); inst(plants[0], 'plant_ne', 25.3, -67.4, caf)
    inst(cr, 'caf_coat_rack', 9.75, -79.2, caf); inst(wfs, 'caf_wet_floor', 8.0 + 2.2, -71.6 if False else -76.2, caf, rz=0.4) if False else None
    inst(mpb, 'caf_mop_bucket', 25.2, -79.0, caf, rz=2.0); inst(wfs, 'caf_wet_floor_sign', 20.5, -71.6, caf, rz=0.3, z=-0.012)
    # ---------------- LOUNGE (west side, south): L of sofas around a coffee table facing the TV
    sof3 = sofa(F, P, (0.52, 0.16, 0.09, 1), seats=3, name='sofa3'); sof2 = sofa(F, P, (0.52, 0.16, 0.09, 1), seats=2, name='sofa2')
    arm2 = armchair(F, P, (0.14, 0.2, 0.38, 1))
    inst(sof3, 'lounge_sofa_main', -4.2, -75.3, caf, rz=math.pi)
    inst(sof2, 'lounge_sofa_side', -6.95, -77.5, caf, rz=-math.pi / 2)
    inst(arm, 'lounge_armchair_0', -1.7, -77.9, caf, rz=math.pi / 2 + 0.3); inst(arm2, 'lounge_armchair_1', -1.7, -75.4, caf, rz=math.pi / 2 - 0.2)
    inst(cof, 'lounge_coffee_table', -4.2, -77.6, caf, rz=0.0)
    inst(mg, 'lounge_mug', -3.9, -77.55, caf, z=0.42, support='table'); inst(bt, 'lounge_bottle', -4.6, -77.7, caf, z=0.42, support='table'); inst(tr, 'lounge_tray', -4.2, -77.5, caf, z=0.42, support='table', rz=0.3)
    inst(lamp, 'lounge_floor_lamp_0', -6.9, -74.7, caf); inst(lamp, 'lounge_floor_lamp_1', -0.9, -79.3, caf)
    inst(plants[1], 'lounge_plant_0', -1.0, -73.2, caf); inst(plants[2], 'lounge_plant_1', -7.2, -79.3, caf); inst(plants[0], 'lounge_plant_2', -7.2, -72.9, caf)
    inst(bc, 'lounge_bookcase', -7.65, -80.0 + 6.0 - 0.0, caf, rz=-math.pi / 2) if False else None
    rug_object(F, caf, 'lounge_rug', -7.4, -0.8, -79.7, -74.0, 'rug_lounge.png')
    for k in range(11): box(f'tv_slat_{k}', -7.0 + k * 0.5, -6.55 + k * 0.5, -79.97, -79.84, 0.0, 3.3, F['timber'], caf, bev=0.008)
    t = inst(tvp, 'lounge_tv', -4.2, -79.82, caf, z=1.0, rz=0.0, support=None, scale=(1.7, 1.7, 1.7)); wall_item(t, 'y', -79.85, +1)
    inst(bc, 'lounge_bookcase', -7.55, -73.3, caf, rz=-math.pi / 2)
    # ---------------- GAME CORNER (north-west, small): foosball, arcade basketball, darts
    rug_object(F, caf, 'game_rug', -7.6, -0.6, -66.2, -60.4, 'rug_game.png')
    inst(foos, 'rec_foosball', -3.4, -62.4, caf, rz=0.0)
    inst(arcade_basketball(F, P), 'rec_basketball', -6.4, -64.6, caf, rz=math.pi)
    dd = inst(dart, 'rec_dartboard', -1.0, -60.17, caf, z=1.73, support=None); wall_item(dd, 'y', -60.15, -1)
    box('rec_oche', -1.6, -0.4, -62.57, -62.52, 0.0, 0.006, F['signage'], caf, rgba=(0.9, 0.88, 0.8, 1))
    # ---------------- ceiling and dividers
    for i, x in enumerate((-2, 6, 14, 22)):
        for j, y in enumerate((-64.5, -70, -75.5)): inst(strip, f'caf_light_strip_{i}{j}', x, y, caf, z=4.93, rz=math.pi / 2, support=None)
    for j, (x, y) in enumerate(tbls[:9]): inst(pend, f'caf_pendant_{j}', x, y, caf, z=3.3, support=None)
    inst(P_counter(F, P), 'serving_counter', 20.2, -65.4, caf)
    inst(P_kitchen(F, P), 'kitchen_block', 20.0, -62.1, caf)
    pl = planter_long(F, P); tt = totem(F, P)
    for i in range(3): inst(pl, f'divider_game_{i}', -6.2 + i * 1.95, -66.9, caf, rz=0.0)
    for i in range(2): inst(pl, f'divider_dining_{i}', 13.4, -76.0 - i * 1.95, caf, rz=math.pi / 2) if False else None
    inst(tt, 'directory_totem', 10.8, -66.5, caf, rz=math.pi)
    for i, x in enumerate((-5.5, -3.2)): inst(wsh[i % 2], f'game_wall_shelf_{i}', x, -60.17, caf, z=2.3, support=None, rz=math.pi)
    # ---- food service dressing on the counter and around the queue
    ts_, ps_, cs_, bb_, cb_ = tray_stack(F, P), plate_stack(F, P), cup_stack(F, P), bread_basket(F, P), cutlery_bin(F, P)
    inst(ts_, 'counter_trays_0', 15.4, -65.95, caf, z=0.96, support='table'); inst(ts_, 'counter_trays_1', 15.95, -65.95, caf, z=0.96, support='table', rz=0.1)
    for i in range(3): inst(ps_, f'counter_plates_{i}', 16.7 + i * 0.32, -65.95, caf, z=0.96, support='table')
    for i in range(4): inst(cs_, f'counter_cups_{i}', 18.0 + i * 0.1, -65.95, caf, z=0.96, support='table')
    for i in range(2): inst(bb_, f'counter_bread_{i}', 21.2 + i * 0.5, -65.9, caf, z=0.96, support='table')
    for i in range(2): inst(cb_, f'counter_cutlery_{i}', 24.0 + i * 0.4, -65.95, caf, z=0.96, support='table')
    inst(sanitiser_station(F, P), 'queue_sanitiser', 13.7, -68.4, caf)
    inst(recycling_bins(F, P), 'recycling_bins', 25.4, -77.6, caf, rz=math.pi / 2); inst(tray_trolley(F, P), 'tray_trolley', 24.7, -79.0, caf, rz=0.0)
    # ---- lounge softs
    st_, bg_, sd_, cu_, tl_ = stool(F, P), bean_bag(F, P), side_table(F, P), throw_cushion(F, P), table_lamp(F, P)
    inst(sd_, 'lounge_side_table_0', -6.2, -74.6, caf); inst(tl_, 'lounge_table_lamp_0', -6.2, -74.6, caf, z=0.48, support='table')
    inst(sd_, 'lounge_side_table_1', -2.6, -73.9, caf) if False else None
    for i, (x, y, z, rz, col) in enumerate(((-5.0, -75.5, 0.45, 0.2, (0.82, 0.62, 0.2, 1)), (-3.4, -75.5, 0.45, -0.3, (0.14, 0.2, 0.38, 1)), (-6.6, -77.0, 0.45, 1.6, (0.82, 0.62, 0.2, 1)))):
        o = inst(cu_, f'lounge_cushion_{i}', x, y, caf, z=z, rz=rz, support='soft'); o.rotation_euler = (0.2, 0, rz)
    # ---- game corner softs
    inst(bg_, 'game_beanbag_0', -6.9, -61.3, caf, rz=0.4); inst(bg_, 'game_beanbag_1', -5.8, -61.0, caf, rz=-0.5, z=0.0)
    inst(st_, 'game_stool_0', -1.8, -64.2, caf); inst(st_, 'game_stool_1', -0.9, -64.6, caf, rz=0.7); inst(sd_, 'game_side_table', -0.4, -65.4, caf)
    pend2 = pendant(F, P)
    for j, (x, y) in enumerate(((-4.2, -76.2), (-2.0, -74.4), (-3.6, -64.0), (-1.0, -62.6))): inst(pend2, f'caf_pendant_L{j}', x, y, caf, z=3.4, support=None)
    for i, (x, y) in enumerate(((-7.55, -75.3), (-7.55, -78.7))): inst(wsh[i % 2], f'lounge_wall_shelf_{i}', x, y, caf, z=2.1, support=None, rz=-math.pi / 2)
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
    box('hatch_shutter_housing', 14.9, 25.1, y - 0.14, y + 0.1, 2.28, 2.4, F['steel_charcoal'], caf, bev=0.01)
    for k in range(5): box(f'hatch_shutter_{k}', 15.0, 25.0, y - 0.03, y + 0.03, 2.2 - k * 0.04, 2.235 - k * 0.04, F['steel_charcoal'], caf, bev=0.003)
