"""Yard v2: sunny, tidy salvage and loading yard. Ragged but kept: tilted and sunken slabs, a few cracks, weeds in the joints, blocky layered cliff with planting."""
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import *
from fe_yard import inst, build_trench, build_canopies, YARD, RAIL_Y, RAIL_X, GATE
import mathutils.noise as mnoise

def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)

def hash2(i, j, s=0):
    return random.Random(i * 7919 + j * 104729 + s * 31).random()

def build_ground(F, C):
    yard = C['YARD']; rnd = random.Random(77)
    ground = box('context_ground', -170, 90, -200, 60, -0.9, -0.15, F['props'], C['SHARED'], rgba=(0.34, 0.31, 0.26, 1)); ground['note'] = 'context only, outside the module footprint'
    box('yard_base', *YARD[:2], *YARD[2:], -0.45, -0.3, F['props'], yard, rgba=(0.14, 0.12, 0.1, 1))
    bm = bmesh.new(); NX, NY = 80, 48; dx = 40.0 / NX; dy = 24.0 / NY; g = []
    for i in range(NX + 1):
        row = []
        for j in range(NY + 1):
            x = YARD[0] + i * dx; y = YARD[2] + j * dy
            z = -0.16 + 0.05 * mnoise.noise(Vector((x * 0.5, y * 0.5, 1.3))) + 0.02 * mnoise.noise(Vector((x * 2.4, y * 2.4, 4.1)))
            row.append(bm.verts.new(Vector((LX(x), LY(y), z))))
        g.append(row)
    for i in range(NX):
        for j in range(NY): bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
    mesh_obj('yard_earth', bm, F['gravel'], yard, smooth=True)
    missing = {(6, 0), (3, 5)}; smashed = {(2, 3), (7, 4)}
    for ix in range(10):
        for iy in range(6):
            x0 = YARD[0] + ix * 4 + 0.02; y0 = YARD[2] + iy * 4 + 0.02
            if (ix, iy) in missing:
                for k in range(3):
                    sx = rnd.uniform(0.5, 1.2); sy = rnd.uniform(0.4, 1.0)
                    o = box(f'yard_shard_{ix}_{iy}_{k}', 0, sx, 0, sy, -0.14, rnd.uniform(-0.02, 0.05), F['concrete_slab'], yard, bev=0.01, plan=False)
                    o.location = (LX(x0 + rnd.uniform(0.2, 3.2)), LY(y0 + rnd.uniform(0.2, 3.2)), 0); o.rotation_euler = (rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), rnd.uniform(0, 6.28)); o['support'] = 'floor_broken'
            elif (ix, iy) in smashed:
                cuts = [0.0, rnd.uniform(1.0, 1.8), rnd.uniform(2.3, 3.0), 3.96]
                for k in range(3):
                    w = cuts[k + 1] - cuts[k] - 0.04
                    o = box(f'yard_slab_{ix}_{iy}_{k}', 0, w, 0, 3.96, -0.15, 0.0, F['concrete_slab'], yard, bev=0.012, plan=False)
                    o.location = (LX(x0 + cuts[k]), LY(y0), rnd.uniform(-0.05, 0.0)); o.rotation_euler = (rnd.uniform(-0.015, 0.015), rnd.uniform(-0.015, 0.015), 0); o['support'] = 'floor_broken'
            else:
                sink = rnd.choice((0, 0, 0, 0, -0.02, -0.04, -0.07)) if (ix, iy) != (7, 3) else 0
                o = box(f'yard_slab_{ix}_{iy}', 0, 3.96, 0, 3.96, -0.15, 0.0, F['concrete_slab'], yard, bev=0.012, plan=False)
                o.location = (LX(x0), LY(y0), sink); o.rotation_euler = (rnd.uniform(-0.008, 0.008), rnd.uniform(-0.008, 0.008), 0); o['support'] = 'floor_broken'
    # wet patches (shallow glass blobs) and a few cracks
    for i in range(9):
        x = rnd.uniform(-45, -11); y = rnd.uniform(-82, -62)
        if -71.6 < y < -68.4: y += 3.2
        bmm = bmesh.new(); res = bmesh.ops.create_icosphere(bmm, subdivisions=3, radius=1.0); r = rnd.uniform(0.5, 1.4)
        for v in res['verts']:
            k = 1 + 0.25 * mnoise.noise(Vector((v.co.x * 1.5 + i, v.co.y * 1.5, 0.4))); v.co = Vector((LX(x) + v.co.x * r * k, LY(y) + v.co.y * r * 0.7 * k, 0.004 + max(v.co.z, 0) * 0.003))
        mesh_obj(f'wet_patch_{i}', bmm, F['glass'], yard)
    bmm = bmesh.new()
    for i in range(24):
        x = rnd.uniform(-47, -9); y = rnd.uniform(-83.5, -60.5); a = rnd.uniform(0, 6.28)
        for k in range(rnd.randint(3, 6)):
            if not (-47.5 < x < -8.5 and -83.5 < y < -60.5): break
            L = rnd.uniform(0.4, 1.1); bm_box(bmm, LX(x), LY(y), 0.003, L, 0.018, 0.004, rz=a)
            x += math.cos(a) * L * 0.9; y += math.sin(a) * L * 0.9; a += rnd.uniform(-0.8, 0.8)
    mesh_obj('ground_cracks', bmm, F['props'], yard, rgba=(0.08, 0.075, 0.07, 1))

def build_cliff(F, C):
    yard = C['YARD']
    Y0, Y1, ZH = -92.0, -54.0, 17.0
    CY, CZ = 0.22, 0.2
    NY, NZ = int((Y1 - Y0) / CY), int(ZH / CZ)
    bm = bmesh.new(); verts = []
    BY, BZ = 4.3, 2.6       # block size
    def cliff_x(y, zz):
        r = zz / BZ; c = (y + 0.4 * math.floor(r) * BY) / BY
        r0, c0 = math.floor(r), math.floor(c); fr, fc = r - r0, c - c0
        off = lambda rr, cc: 1.7 * hash2(rr, cc) ** 1.3 + 0.5 * math.sin(rr * 1.7 + cc * 0.9)
        o0 = off(r0, c0); e = 0.06
        sm_r = smoothstep(0, e * 2.4, fr) * smoothstep(0, e * 2.4, 1 - fr); sm_c = smoothstep(0, e, fc) * smoothstep(0, e, 1 - fc)
        face = o0 * (0.55 + 0.45 * sm_r * sm_c) - 0.35 * (1 - sm_r * sm_c)
        n1 = mnoise.noise(Vector((y * 0.5, zz * 0.5, 3.3))); n2 = mnoise.noise(Vector((y * 2.0, zz * 2.0, 7.1)))
        x = -48.0 - 0.07 * zz - 0.0004 * zz * zz - face - 0.35 * n1 - 0.07 * n2
        if -73.6 <= y <= -66.4 and zz <= 3.9: x = -53.6 + 0.04 * n2
        elif -74.2 <= y <= -65.8 and zz <= 4.4: x = min(x, -50.0)
        return x
    for i in range(NY + 1):
        y = Y0 + CY * i; row = []
        for j in range(NZ + 1):
            z = CZ * j
            ztop = ZH * (0.78 + 0.22 * (0.5 + 0.5 * mnoise.noise(Vector((y * 0.09, 5.5, 0.2))))) * min(1.0, 0.3 + min(y - Y0, Y1 - y) / 9.0)
            zz = min(z, ztop)
            row.append(bm.verts.new(Vector((LX(cliff_x(y, zz)), LY(y), zz))))
        verts.append(row)
    for i in range(NY):
        for j in range(NZ): bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces: f.smooth = True
    mesh_obj('cliff_face', bm, F['rock'], yard, smooth=True)
    box('mountain_mass', -90, -56.0, -96, -50, -1.0, 9.0, F['rock'], C['SHARED'])
    box('cliff_kerb_S', -48.4, -47.4, -84, -71.4, -0.15, 0.35, F['concrete_slab'], yard, bev=0.03); box('cliff_kerb_N', -48.4, -47.4, -68.6, -60, -0.15, 0.35, F['concrete_slab'], yard, bev=0.03)
    # boulders along the foot (angular chunks)
    P = collection('PROTOTYPES'); rb = random.Random(21)
    from fe_assets_site import rubble_chunk
    rocks = [rubble_chunk(F, P, 20 + s, 0.9) for s in range(6)]
    for i in range(16):
        yy = -91 + i * 2.35 + rb.uniform(-0.6, 0.6)
        if -75 < yy < -65: continue
        inst(rocks[i % 6], f'boulder_{i}', -49.0 + rb.uniform(-0.9, 0.1), yy, yard, rz=rb.uniform(0, 6.28), z=-0.05, scale=(rb.uniform(1.0, 2.1),) * 3, support='floor_broken')
    shs = [shrub(F, P, 30 + s, 0.38, 40) for s in range(3)]; vr = random.Random(9)
    from fe_assets_yard import shrub as _s
    for i in range(40):
        yy = vr.uniform(-90, -56)
        if -75 < yy < -65: continue
        rr = vr.randint(1, 5); zz = rr * BZ - 0.05
        xx = cliff_x(yy, zz - 0.25) + 0.12
        o = inst(shs[i % 3], f'cliff_shrub_{i}', xx, yy, yard, rz=vr.uniform(0, 6.28), z=zz, scale=(vr.uniform(0.8, 1.5),) * 3, support=None)
    # dark void, timbered mouth
    box('portal_void', -58.0, -53.4, -73.3, -66.7, 0.0, 3.5, F['rubber'], yard, rgba=(0.01, 0.01, 0.01, 1))
    box('portal_floor', -53.6, -47.5, -73.3, -66.7, -0.2, 0.0, F['props'], yard, rgba=(0.12, 0.1, 0.08, 1))
    box('mouth_wall_L', -53.5, -49.3, -73.35, -73.1, 0.0, 3.5, F['timber'], yard, bev=0.02); box('mouth_wall_R', -53.5, -49.3, -66.9, -66.65, 0.0, 3.5, F['timber'], yard, bev=0.02)
    box('mouth_roof', -53.5, -49.3, -73.35, -66.65, 3.4, 3.6, F['timber'], yard, bev=0.02)
    for k, xx in enumerate((-50.3, -51.9)):
        for s_, yy in (('L', -73.0), ('R', -67.0)): box(f'mouth_post_{k}{s_}', xx - 0.15, xx + 0.15, yy - 0.15, yy + 0.15, 0.0, 3.4, F['timber'], yard, bev=0.02)
        box(f'mouth_cap_{k}', xx - 0.15, xx + 0.15, -73.2, -66.8, 3.25, 3.45, F['timber'], yard, bev=0.02)
    box('mouth_lamp', -52.6, -52.2, -70.15, -69.85, 3.1, 3.25, F['emissive'], yard, rgba=(1.0, 0.7, 0.35, 1), bev=0.01)

def rail_path(F, yard, name, pts, gauge=0.78):
    """Rails (I-section built from boxes), sleepers, fishplates along a polyline given in plan coordinates (dense points)."""
    rail_bm = bmesh.new(); sl_bm = bmesh.new(); fp_bm = bmesh.new()
    acc = 0.0; k = 0
    for a, b in zip(pts[:-1], pts[1:]):
        dxy = (b[0] - a[0], b[1] - a[1]); L = math.hypot(*dxy); ang = math.atan2(dxy[1], dxy[0]); nx, ny = -math.sin(ang), math.cos(ang)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        for s in (-1, 1):
            cx, cy = mx + nx * s * gauge, my + ny * s * gauge
            bm_box(rail_bm, LX(cx), LY(cy), 0.155, L + 0.01, 0.07, 0.04, rz=ang, bevel=0.006)    # head
            bm_box(rail_bm, LX(cx), LY(cy), 0.115, L + 0.01, 0.018, 0.08, rz=ang)               # web
            bm_box(rail_bm, LX(cx), LY(cy), 0.075, L + 0.01, 0.11, 0.016, rz=ang)               # foot
        acc += L
        if acc >= 0.62:
            acc = 0.0
            bm_box(sl_bm, LX(mx), LY(my), 0.04, 0.2, 1.9, 0.09, rz=ang, bevel=0.012, seg=2)
            for s in (-1, 1):
                bm_box(sl_bm, LX(mx + nx * s * gauge), LY(my + ny * s * gauge), 0.092, 0.16, 0.17, 0.014, rz=ang)
        k += 1
        if k % 20 == 0:
            for s in (-1, 1):
                cx, cy = mx + nx * s * gauge, my + ny * s * gauge
                bm_box(fp_bm, LX(cx), LY(cy), 0.115, 0.55, 0.1, 0.07, rz=ang, bevel=0.008)
                for d in (-0.2, -0.07, 0.07, 0.2):
                    bm_cyl(fp_bm, LX(cx + math.cos(ang) * d), LY(cy + math.sin(ang) * d), 0.1, 0.13, 0.014, seg=6)
    mesh_obj(name + '_rails', rail_bm, F['steel_rust'], yard); mesh_obj(name + '_sleepers', sl_bm, F['timber'], yard); mesh_obj(name + '_fishplates', fp_bm, F['steel_charcoal'], yard)

def build_rails(F, C):
    yard = C['YARD']
    xa = -53.0; xb = RAIL_X - 6.0; step = 0.5
    pts = [(xa + i * step, RAIL_Y) for i in range(int((xb - xa) / step) + 1)]
    R = 6.0; cxx, cyy = RAIL_X - R, RAIL_Y + R
    for i in range(1, 25):
        t = i / 24 * math.pi / 2; pts.append((cxx + R * math.sin(t), cyy - R * math.cos(t)))
    y = RAIL_Y + R
    while y < -59.4: y += step; pts.append((RAIL_X, y))
    rail_path(F, yard, 'rail', pts)
    # ballast: angular stones along the track
    P = collection('PROTOTYPES'); rb = random.Random(5)
    from fe_assets_site import rubble_chunk
    st = [rubble_chunk(F, P, 40 + s, 0.07) for s in range(4)]
    for i in range(0, len(pts), 2):
        for s in (-1, 1):
            x, y = pts[i]; j = min(i + 1, len(pts) - 1); ang = math.atan2(pts[j][1] - y, pts[j][0] - x); nx, ny = -math.sin(ang), math.cos(ang)
            off = rb.uniform(1.0, 1.25) * s
            if rb.random() < 0.35: inst(st[rb.randrange(4)], f'ballast_{i}_{s}', x + nx * off, y + ny * off, yard, rz=rb.uniform(0, 6), z=-0.01, scale=(rb.uniform(0.8, 1.6),) * 3, support='floor_debris')

def build_fences(F, C):
    yard = C['YARD']; P = collection('PROTOTYPES')
    fp = fence_panel(F, P); fpost = fence_post(F, P)
    def run(name, x0, x1, y, gaps):
        cuts = [x0]
        for c, w in sorted(gaps): cuts += [c - w / 2, c + w / 2]
        cuts.append(x1); k = 0
        for i in range(0, len(cuts), 2):
            a, b = cuts[i], cuts[i + 1]
            if b - a < 0.2: continue
            n = max(int(round((b - a) / 3.0)), 1); step = (b - a) / n
            for j in range(n):
                o = inst(fp, f'{name}_panel{k}', a + j * step + step / 2, y, yard, scale=((step - 0.1) / 3.0, 1, 1), support='floor'); k += 1
            for j in range(n + 1): inst(fpost, f'{name}_post{k}', a + j * step, y, yard); k += 1
    run('fence_N', -48.0, -12.0, -60.1, [(RAIL_X, 3.0), (-46.0, 2.4)])
    run('fence_S', -48.0, -8.0, -84.0, [(-28.0, 6.0)])
    for s in (-1, 1):
        box(f'freight_gate_post{s}', RAIL_X + s * 1.55 - 0.15, RAIL_X + s * 1.55 + 0.15, -60.25, -59.95, 0, 3.3, F['steel_accent'], yard, bev=0.02)
    box('freight_gate_header', RAIL_X - 1.7, RAIL_X + 1.7, -60.25, -59.95, 3.1, 3.3, F['steel_accent'], yard, bev=0.02)
    inst(fp, 'freight_gate_leaf', RAIL_X + 2.3, -60.5, yard, scale=(0.55, 1, 1), z=0.0, support='floor')
    for s in (-1, 1):
        cx = -28.0 + s * 1.5
        box(f'evac_leaf_frame{s}', cx - 1.45, cx + 1.45, -84.07, -83.93, 0.1, 2.3, F['steel_accent'], yard, bev=0.012)
        for k in range(8):
            xx = cx - 1.3 + k * 0.37
            box(f'evac_stripe_{s}_{k}', xx, xx + 0.17, -84.1, -83.9, 0.3, 2.0, F['signage'], yard, rgba=(0.05, 0.05, 0.05, 1) if k % 2 else (0.92, 0.72, 0.05, 1), bev=0.004)
        box(f'evac_post{s}', -28.0 + s * 3.1 - 0.15, -28.0 + s * 3.1 + 0.15, -84.15, -83.85, 0, 2.5, F['steel_charcoal'], yard, bev=0.02)
    box('evac_keypad', -28.15, -27.85, -83.8, -83.7, 1.1, 1.4, F['plastic'], yard, rgba=(0.1, 0.1, 0.1, 1), bev=0.01)
    box('service_door_L', -47.35, -47.2, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01); box('service_door_R', -44.8, -44.65, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01)
    box('service_door_H', -47.35, -44.65, -60.25, -59.95, 2.4, 2.55, F['steel_charcoal'], yard, bev=0.01)

def rect_(cx, cy, hx, hy, rz=0.0):
    c, s = abs(math.cos(rz)), abs(math.sin(rz)); ex = hx * c + hy * s; ey = hx * s + hy * c
    return (cx - ex, cx + ex, cy - ey, cy + ey)

def build_props(F, C):
    yard = C['YARD']; P = collection('PROTOTYPES'); rng = random.Random(11); rects = []
    def put(proto, name, x, y, rz=0.0, z=0.0, hx=0.0, hy=0.0, support='floor', scale=(1, 1, 1)):
        o = inst(proto, name, x, y, yard, rz=rz, z=z, scale=scale, support=support)
        if hx: rects.append(rect_(x, y, hx * scale[0], hy * scale[1], rz))
        return o
    cont = [container(F, P, c, f'container_{i}') for i, c in enumerate(((0.52, 0.13, 0.08, 1), (0.1, 0.22, 0.3, 1), (0.64, 0.5, 0.12, 1), (0.22, 0.34, 0.2, 1)))]
    pk = pickup(F, P); vn = van(F, P); skip = skip_bin(F, P); stock = steel_stock(F, P, 1); pipes = [pipe_stack(F, P, s) for s in (1, 2)]
    bales = [bale(F, P, s) for s in range(3)]; gen = generator(F, P); tk = [tank_vertical(F, P, 2.6, 1.05, (0.55, 0.57, 0.55, 1), 'tank_a'), tank_vertical(F, P, 2.2, 0.85, (0.6, 0.38, 0.12, 1), 'tank_b')]
    crates = [crate(F, P, v) for v in range(4)]; pal = pallet(F, P); brl = [barrel(F, P, c, f'barrel_{i}') for i, c in enumerate(((0.12, 0.3, 0.45, 1), (0.55, 0.14, 0.1, 1), (0.3, 0.34, 0.3, 1)))]
    drum = cable_drum(F, P); tyres = [tyre(F, P, 1, 'tyre'), tyre(F, P, 3, 'tyre_stack3'), tyre(F, P, 4, 'tyre_stack4')]; cn = cone(F, P); bol = bollard(F, P); bn = bench(F, P)
    plt = planter(F, P); shr = [shrub(F, P, s, 0.5) for s in range(3)]; trs = [tree(F, P, s, 4.2 + 0.5 * s) for s in range(3)]; pole = light_pole(F, P); cart = ore_cart(F, P)
    # containers
    put(cont[0], 'container_0', -42.6, -81.6, 0.0, hx=3.0, hy=1.25); put(cont[1], 'container_0b', -42.4, -81.6, 0.05, z=2.59, support='stack')
    put(cont[2], 'container_1', -36.0, -81.7, -0.03, hx=3.0, hy=1.25); put(cont[3], 'container_2', -39.6, -76.6, 0.0, hx=3.0, hy=1.25)
    put(cont[0], 'container_3', -40.4, -62.7, 0.0, hx=3.0, hy=1.25); put(cont[2], 'container_3b', -40.2, -62.7, -0.04, z=2.59, support='stack')
    put(cont[1], 'container_4', -33.0, -62.9, -0.05, hx=3.0, hy=1.25); put(cont[3], 'container_5', -17.4, -82.6, 0.03, hx=3.0, hy=1.25)
    # vehicles and plant
    put(pk, 'pickup_0', -33.2, -74.7, 0.1, hx=2.7, hy=1.0); put(vn, 'van_0', -20.5, -76.3, math.pi + 0.05, hx=2.7, hy=1.0)
    put(gen, 'generator', -12.3, -79.6, math.pi / 2, hx=1.4, hy=0.8); put(tk[0], 'tank_0', -15.8, -64.3 if False else -66.4, 0.0, hx=1.1, hy=1.1); put(tk[1], 'tank_1', -18.8, -66.4, 0.0, hx=0.9, hy=0.9)
    put(skip, 'skip_0', -23.6, -82.3, 0.0, hx=1.9, hy=1.0); put(skip, 'skip_1', -35.5, -66.4, 0.15, hx=1.9, hy=1.0)
    put(stock, 'steel_stock_0', -29.6, -66.4, 0.0, hx=1.9, hy=0.8)
    for i, (x, y, rz) in enumerate(((-33.4, -78.9, 0.0), (-19.0, -80.2, 0.05))): put(pipes[i % 2], f'pipes_{i}', x, y, rz, hx=1.9, hy=0.7)
    for i, (x, y) in enumerate(((-15.4, -74.4), (-15.3, -76.0), (-26.0, -66.4), (-25.9, -64.9), (-44.2, -66.8))): put(bales[i % 3], f'bale_{i}', x, y, rng.uniform(-0.15, 0.15), hx=0.7, hy=0.55)
    put(bales[1], 'bale_top_0', -15.4, -75.2, 0.1, z=0.9, support='stack'); put(bales[2], 'bale_top_1', -26.0, -65.6, -0.1, z=0.9, support='stack')
    for i, (x, y, k) in enumerate(((-45.9, -80.0, 1), (-46.1, -78.7, 2), (-30.6, -82.5, 1), (-20.0, -67.1, 1), (-39.0, -66.6, 2))): put(tyres[k], f'tyres_{i}', x, y, rng.uniform(0, 6), hx=0.4, hy=0.4)
    # crates, pallets, barrels
    cl = {'A': (-46.0, -42.5, -68.0, -64.2), 'B': (-47.0, -44.0, -76.0, -72.2), 'C': (-32.0, -27.5, -81.8, -78.0)}
    pts = []
    def free(x, y, r=0.9):
        if -71.4 < y < -68.6 or (-23.5 < x < -20.9 and y > -70.5) or (-29.7 < x < -26.3 and y < -71.2) or (-47.4 < x < -44.8 and y > -68.8) or (-12.6 < x < -7.9) or (-27.2 < x < -16.8 and y > -65.2): return False
        for (a, b, c, d) in rects:
            if a - r < x < b + r and c - r < y < d + r: return False
        return all((x - p[0]) ** 2 + (y - p[1]) ** 2 > (r + 0.3) ** 2 for p in pts)
    n = 0
    fk = forklift(F, P); cob = car_on_blocks(F, P); gr = gas_rack(F, P); ht = hand_truck(F, P); hr = hose_reel(F, P); tbar = traffic_barrier(F, P); spost = sign_post(F, P); spost2 = sign_post(F, P, (0.1, 0.45, 0.8, 1))
    put(fk, 'forklift_0', -42.5, -66.3, math.pi, hx=1.8, hy=0.8); put(cob, 'car_blocks', -45.3, -74.6, math.pi / 2, hx=2.2, hy=0.95)
    put(gr, 'gas_rack_0', -24.4, -76.4, math.pi / 2, hx=0.9, hy=0.5); put(gr, 'gas_rack_1', -44.0, -69.0 if False else -78.4, 0.0, hx=0.8, hy=0.5) if False else None
    put(hr, 'hose_reel_0', -45.8, -66.1 if False else -61.0, 0.5); put(hr, 'hose_reel_1', -14.8, -63.9, 0.0); put(hr, 'hose_reel_2', -10.0, -82.5, 3.0)
    for i, (x, y, rz) in enumerate(((-30.0, -82.8, 0.0), (-26.0, -82.8, 0.0), (-24.6, -61.6, 1.57), (-19.6, -61.6, 1.57), (-44.3, -61.4, 0.0))): put(tbar, f'traffic_barrier_{i}', x, y, rz)
    for i, (x, y, rz) in enumerate(((-24.9, -83.4, 0.2), (-47.0, -71.9, 0.0), (-11.5, -60.9, 3.0), (-47.0, -68.0, 0.0))): put(spost if i % 2 == 0 else spost2, f'sign_post_{i}', x, y, rz)
    for zone, cnt in (('A', 8), ('B', 6), ('C', 6)):
        x0, x1, y0, y1 = cl[zone]
        for _ in range(cnt):
            for _ in range(60):
                x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
                if free(x, y):
                    pts.append((x, y)); kind = rng.choice(('crate', 'crate', 'pallet', 'barrel', 'drum'))
                    if kind == 'crate':
                        h = rng.choice((1, 2, 2)); rz = rng.uniform(-0.3, 0.3)
                        for k in range(h): put(crates[rng.randrange(4)], f'crate_{n}_{k}', x, y, rz + rng.uniform(-0.05, 0.05), z=k * 0.995, hx=0.0, support='floor' if k == 0 else 'stack')
                        rects.append(rect_(x, y, 0.6, 0.6, rz))
                    elif kind == 'pallet':
                        put(pal, f'pallet_{n}', x, y, rng.uniform(0, 3)); rects.append(rect_(x, y, 0.65, 0.55, 0))
                    elif kind == 'barrel':
                        for dx, dy in ((0, 0), (0.62, 0.1), (0.3, 0.55)): put(brl[rng.randrange(3)], f'barrel_{n}_{int(dx*10)}', x + dx, y + dy, rng.uniform(0, 6))
                        rects.append(rect_(x + 0.3, y + 0.3, 0.7, 0.7, 0))
                    else:
                        put(drum, f'drum_{n}', x, y, rng.uniform(0, 6)); rects.append(rect_(x, y, 0.55, 0.55, 0))
                    n += 1; break
    # cones and bollards
    for i, (x, y) in enumerate(((-24.8, -61.5), (-19.8, -61.5), (-24.8, -66.3), (-19.6, -66.3), (-13.0, -62.0), (-13.0, -83.0), (-32.6, -83.0), (-22.8, -83.0))): put(cn, f'cone_{i}', x, y, rng.uniform(0, 3))
    for i, y in enumerate((-61.0, -66.5, -73.8, -77.0, -80.5)): put(bol, f'bollard_{i}', -8.9, y, 0.0)
    # carts on the track, facing east
    put(ht, 'hand_truck_0', -37.7, -80.0, 0.7); put(ht, 'hand_truck_1', -33.0, -66.8, 2.2)
    put(cart, 'ore_cart_0', -41.0, RAIL_Y, 0.0, support=None); put(cart, 'ore_cart_1', -37.2, RAIL_Y, 0.0, support=None)
    # porch benches, planters with shrubs, trees
    for i, (x, y) in enumerate(((-10.5, -64.8), (-10.5, -75.2), (-10.5, -77.2))): put(bn, f'bench_{i}', x, y, math.pi / 2)
    for i, (x, y) in enumerate(((-9.0, -62.0), (-9.0, -65.0), (-9.0, -78.0), (-9.0, -81.0), (-14.0, -63.0), (-9.0, -61.0))):
        put(plt, f'planter_{i}', x, y, 0.0); put(shr[i % 3], f'planter_shrub_{i}', x, y, rng.uniform(0, 3), z=0.6, support=None, scale=(1.1, 1.1, 1.1))
    for i, (x, y) in enumerate(((-45.5, -61.5), (-44.0, -81.0), (-34.0, -61.5), (-16.0, -81.0), (-12.0, -73.0))): put(trs[i % 3], f'tree_{i}', x, y, rng.uniform(0, 6), support=None)
    for i in range(14):
        for _ in range(40):
            x, y = rng.uniform(-47, -10), rng.uniform(-83, -61)
            if free(x, y, 0.6): pts.append((x, y)); put(shr[i % 3], f'shrub_{i}', x, y, rng.uniform(0, 6), support=None, scale=(rng.uniform(0.8, 1.3),) * 3); break
    # light poles
    for i, (x, y) in enumerate(((-40.0, -66.4), (-30.0, -67.0), (-20.0, -67.0), (-34.0, -80.0), (-14.0, -67.0))): put(pole, f'pole_{i}', x, y, math.pi)
    P.hide_viewport = False
    return rects
