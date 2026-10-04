"""Yard: ground, slabs, cliff and mine portal, rail, fences and gates, canopies, junk, planting, poles."""
from fe_common import *
from fe_props import *
import mathutils.noise as mnoise

YARD = (-48.0, -8.0, -84.0, -60.0)
RAIL_Y = -70.0
RAIL_X = -22.2
GATE = 0.78    # half gauge

def inst(proto, name, x, y, coll, rz=0.0, z=0.0, scale=(1, 1, 1), support='floor'):
    o = bpy.data.objects.new(name, proto.data)
    o.location = (LX(x), LY(y), z); o.rotation_euler = (0, 0, rz); o.scale = scale
    if proto.data.materials: pass
    coll.objects.link(o)
    if support: o['support'] = support
    return o

def build_ground(F, C):
    yard = C['YARD']; rnd = random.Random(77)
    ground = box('context_ground', -170, 90, -200, 60, -0.9, -0.15, F['props'], C['SHARED'], rgba=(0.14, 0.125, 0.11, 1))
    ground['note'] = 'context only, outside the module footprint'
    box('yard_base', *YARD[:2], *YARD[2:], -0.45, -0.3, F['props'], yard, rgba=(0.08, 0.075, 0.07, 1))
    # rough earth showing through every gap: displaced grid under the slabs
    bm = bmesh.new(); NX, NY = 80, 48; dx = 40.0 / NX; dy = 24.0 / NY; g = []
    for i in range(NX + 1):
        row = []
        for j in range(NY + 1):
            x = YARD[0] + i * dx; y = YARD[2] + j * dy
            z = -0.16 + 0.07 * mnoise.noise(Vector((x * 0.5, y * 0.5, 1.3))) + 0.025 * mnoise.noise(Vector((x * 2.4, y * 2.4, 4.1)))
            row.append(bm.verts.new(Vector((LX(x), LY(y), z))))
        g.append(row)
    for i in range(NX):
        for j in range(NY): bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
    mesh_obj('yard_earth', bm, F['props'], yard, rgba=(0.17, 0.14, 0.105, 1), smooth=True)
    missing = {(1, 2), (4, 4), (6, 0), (8, 3), (3, 5), (9, 1)}
    smashed = {(2, 3), (5, 1), (7, 4), (0, 4), (4, 0)}
    for ix in range(10):
        for iy in range(6):
            x0 = YARD[0] + ix * 4 + 0.02; y0 = YARD[2] + iy * 4 + 0.02
            if (ix, iy) in missing:
                # hole with broken edge shards and a puddle
                for k in range(4):
                    sx = rnd.uniform(0.5, 1.4); sy = rnd.uniform(0.4, 1.1)
                    o = box(f'yard_shard_{ix}_{iy}_{k}', 0, sx, 0, sy, -0.14, rnd.uniform(-0.02, 0.06), F['concrete_slab'], yard, bev=0.01, plan=False)
                    o.location = (LX(x0 + rnd.uniform(0.2, 3.2)), LY(y0 + rnd.uniform(0.2, 3.2)), 0); o.rotation_euler = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), rnd.uniform(0, 6.28))
                    o['support'] = 'floor_broken'
                if (ix + iy) % 2 == 0: box(f'yard_puddle_{ix}_{iy}', x0 + 0.8, x0 + 3.0, y0 + 0.8, y0 + 3.0, -0.18, -0.15, F['glass'], yard)
            elif (ix, iy) in smashed:
                # cracked in three pieces at different heights and tilts
                cuts = [0.0, rnd.uniform(1.0, 1.8), rnd.uniform(2.3, 3.0), 3.96]
                for k in range(3):
                    w = cuts[k + 1] - cuts[k] - 0.05
                    o = box(f'yard_slab_{ix}_{iy}_{k}', 0, w, 0, 3.96, -0.15, 0.0, F['concrete_slab'], yard, bev=0.012, plan=False)
                    o.location = (LX(x0 + cuts[k]), LY(y0), rnd.uniform(-0.09, 0.0)); o.rotation_euler = (rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), 0)
                    o['support'] = 'floor_broken'
            else:
                sink = rnd.choice((0, 0, 0, -0.03, -0.06, -0.1)) if (ix, iy) != (7, 3) else 0
                o = box(f'yard_slab_{ix}_{iy}', 0, 3.96, 0, 3.96, -0.15, 0.0, F['concrete_slab'], yard, bev=0.012, plan=False)
                o.location = (LX(x0), LY(y0), sink); o.rotation_euler = (rnd.uniform(-0.012, 0.012), rnd.uniform(-0.012, 0.012), 0); o['support'] = 'floor_broken'
    # potholes and ragged patches: dark irregular blobs pressed into the earth/slab, cracks as dark seams
    for i in range(26):
        x = rnd.uniform(-46, -10); y = rnd.uniform(-83, -61)
        if -71.6 < y < -68.4 and x < -20: continue
        bmm = bmesh.new(); res = bmesh.ops.create_icosphere(bmm, subdivisions=2, radius=1.0)
        r = rnd.uniform(0.25, 0.7)
        for v in res['verts']:
            k = 1 + rnd.uniform(-0.3, 0.3); v.co = Vector((LX(x) + v.co.x * r * k, LY(y) + v.co.y * r * 0.8 * k, 0.002 + max(v.co.z, 0) * 0.006))
        mesh_obj(f'pothole_{i}', bmm, F['props'], yard, rgba=(0.05, 0.045, 0.04, 1))
    bmm = bmesh.new()
    for i in range(60):
        x = rnd.uniform(-47, -9); y = rnd.uniform(-83.5, -60.5); a = rnd.uniform(0, 6.28)
        for k in range(rnd.randint(3, 6)):
            if not (-47.5 < x < -8.5 and -83.5 < y < -60.5): break
            L = rnd.uniform(0.4, 1.1); bm_box(bmm, LX(x), LY(y), 0.003, L, 0.025, 0.004, rz=a)
            x += math.cos(a) * L * 0.9; y += math.sin(a) * L * 0.9; a += rnd.uniform(-0.8, 0.8)
    mesh_obj('ground_cracks', bmm, F['props'], yard, rgba=(0.03, 0.03, 0.03, 1))

def build_trench(F, C, name, x0, x1, y):
    yard = C['YARD']
    box(name + '_frame_a', x0, x1, y - 0.2, y - 0.14, -0.1, 0.0, F['steel_charcoal'], yard)
    box(name + '_frame_b', x0, x1, y + 0.14, y + 0.2, -0.1, 0.0, F['steel_charcoal'], yard)
    box(name + '_sump', x0, x1, y - 0.14, y + 0.14, -0.22, -0.1, F['props'], yard, rgba=(0.05, 0.05, 0.05, 1))
    k = 0; x = x0 + 0.1
    bm = bmesh.new()
    while x < x1 - 0.05:
        bm_box(bm, LX(x), LY(y), -0.03, 0.035, 0.28, 0.05)
        x += 0.12; k += 1
    mesh_obj(name + '_grating', bm, F['steel_charcoal'], yard)

def build_cliff(F, C):
    yard = C['YARD']
    Y0, Y1, ZH = -92.0, -54.0, 18.0
    NY, NZ = 205, 160
    bm = bmesh.new()
    verts = []
    for i in range(NY + 1):
        y = Y0 + (Y1 - Y0) * i / NY; row = []
        for j in range(NZ + 1):
            ztop = ZH * (0.7 + 0.3 * (0.5 + 0.5 * mnoise.noise(Vector((y * 0.11, 5.5, 0.2))))) * min(1.0, 0.25 + min(y - Y0, Y1 - y) / 9.0)
            z = ztop * j / NZ
            n1 = mnoise.noise(Vector((y * 0.16, z * 0.2, 3.1)))
            n0 = mnoise.noise(Vector((y * 0.07, z * 0.09, 9.3)))
            n2 = mnoise.noise(Vector((y * 0.6, z * 0.7, 7.7)))
            n3 = mnoise.noise(Vector((y * 1.7, z * 1.6, 1.3)))
            terr = 0.7 * (round(z * 0.42 + n1 * 0.9) / 0.42 - z) * 0.35
            groove = 0.5 * abs(mnoise.noise(Vector((y * 1.1, 0.5, 4.0)))) ** 1.4 * (1.0 if z > 1.2 else z / 1.2)
            strata = 0.25 * math.sin(z * 1.3 + n1 * 2.4) + terr - groove
            base = -48.0 - 0.12 * z - 0.9 * max(z - 6, 0) ** 0.5 * 0.3
            x = base - (2.4 * n1 + 1.8 * n0 + 0.55 * n2 + 0.14 * n3 + strata * 0.5)
            # taper to flush with the ground at the base and with the fences at the ends
            x += 0.0
            # mine portal recess
            if -73.6 <= y <= -66.4 and z <= 3.9:
                x = -53.6 + 0.05 * n3
            elif -74.2 <= y <= -65.8 and z <= 4.4:
                x = min(x, -49.4)
            row.append(bm.verts.new(Vector((LX(x), LY(y), z))))
        verts.append(row)
    for i in range(NY):
        for j in range(NZ):
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces: f.smooth = True
    o = mesh_obj('cliff_face', bm, F['rock'], yard, smooth=True)
    # boulders along the cliff foot
    P = collection('PROTOTYPES'); rb = random.Random(21)
    for i in range(16):
        bm = bmesh.new(); bm_blob(bm, 0, 0, 0.0, rb.uniform(0.8, 1.7), rb.uniform(0.8, 1.7), rb.uniform(0.6, 1.3), sub=3, jitter=0.28, seed=i)
        for v in bm.verts: v.co.z = max(v.co.z, -0.1)
        me = bpy.data.meshes.new(f'boulder_{i}'); bm.to_mesh(me); bm.free(); me.materials.append(F['rock'])
        o = bpy.data.objects.new(f'boulder_{i}', me); yard.objects.link(o)
        yy = -91 + i * 2.35 + rb.uniform(-0.6, 0.6)
        if -75 < yy < -65: yy += 8.5
        o.location = (LX(-49.6 + rb.uniform(-0.9, 0.2)), LY(yy), 0.0); o.rotation_euler = (0, 0, rb.uniform(0, 6.28)); o['support'] = 'floor'
    # mountain mass behind
    box('mountain_mass', -90, -56.0, -96, -50, -1.0, 14.0, F['rock'], C['SHARED'])
    # kerb and rock shelf at the base
    box('cliff_kerb_S', -48.4, -47.4, -84, -71.4, -0.15, 0.4, F['concrete_slab'], yard, bev=0.03); box('cliff_kerb_N', -48.4, -47.4, -68.6, -60, -0.15, 0.4, F['concrete_slab'], yard, bev=0.03)
    # mine portal: dark void; the front frame is the R39 portal (fe_minefront) added by the build script
    box('portal_void', -58.0, -53.4, -73.3, -66.7, 0.0, 3.5, F['rubber'], yard, rgba=(0.01, 0.01, 0.01, 1))
    box('portal_floor', -53.6, -47.5, -73.3, -66.7, -0.2, 0.0, F['props'], yard, rgba=(0.06, 0.055, 0.05, 1))
    # short timbered tunnel mouth behind the portal frame: lagging, ceiling, two timber sets, a lamp
    box('mouth_wall_L', -53.5, -49.3, -73.35, -73.1, 0.0, 3.5, F['timber'], yard, bev=0.02); box('mouth_wall_R', -53.5, -49.3, -66.9, -66.65, 0.0, 3.5, F['timber'], yard, bev=0.02)
    box('mouth_roof', -53.5, -49.3, -73.35, -66.65, 3.4, 3.6, F['timber'], yard, bev=0.02)
    for k, xx in enumerate((-50.3, -51.9)):
        for s_, yy in (('L', -73.0), ('R', -67.0)): box(f'mouth_post_{k}{s_}', xx - 0.15, xx + 0.15, yy - 0.15, yy + 0.15, 0.0, 3.4, F['timber'], yard, bev=0.02)
        box(f'mouth_cap_{k}', xx - 0.15, xx + 0.15, -73.2, -66.8, 3.25, 3.45, F['timber'], yard, bev=0.02)
    box('mouth_lamp', -52.6, -52.2, -70.15, -69.85, 3.1, 3.25, F['emissive'], yard, rgba=(1.0, 0.65, 0.3, 1), bev=0.01)

def build_rails(F, C):
    yard = C['YARD']
    bm = bmesh.new(); xa, xb = -53.0, RAIL_X
    for sy in (-GATE, GATE): bm_box(bm, LX((xa + xb) / 2), LY(RAIL_Y + sy), 0.1, xb - xa, 0.07, 0.12, bevel=0.008)
    for sy in (-GATE, GATE): bm_box(bm, LX((xa + xb) / 2), LY(RAIL_Y + sy), 0.05, xb - xa, 0.15, 0.02)
    x = xa + 0.3
    while x < xb: bm_box(bm, LX(x), LY(RAIL_Y), 0.03, 0.16, 1.7, 0.07, bevel=0.006); x += 0.6
    mesh_obj('rail_east_west', bm, F['steel_rust'], yard)
    bm = bmesh.new(); ya, yb = RAIL_Y, -60.2
    for sx in (-GATE, GATE): bm_box(bm, LX(RAIL_X + sx), LY((ya + yb) / 2), 0.1, 0.07, yb - ya, 0.12, bevel=0.008)
    y = ya + 0.3
    while y < yb: bm_box(bm, LX(RAIL_X), LY(y), 0.03, 1.7, 0.16, 0.07, bevel=0.006); y += 0.6
    mesh_obj('rail_north_south', bm, F['steel_rust'], yard)
    box('ballast_ew', -53.0, RAIL_X + 0.9, RAIL_Y - 1.1, RAIL_Y + 1.1, 0.0, 0.03, F['props'], yard, rgba=(0.34, 0.32, 0.29, 1))
    box('ballast_ns', RAIL_X - 1.1, RAIL_X + 1.1, RAIL_Y, -60.2, 0.0, 0.03, F['props'], yard, rgba=(0.34, 0.32, 0.29, 1))

def fence_panel(F, coll, name, x, y, axis, length, h=2.2):
    bm = bmesh.new()
    cx, cy = (LX(x), LY(y))
    if axis == 'x':
        bm_box(bm, cx, cy, h - 0.03, length, 0.05, 0.05, bevel=0.004); bm_box(bm, cx, cy, 0.18, length, 0.05, 0.05, bevel=0.004)
        for k in range(1, int(length / 0.25)): bm_box(bm, cx - length / 2 + k * 0.25, cy, h / 2, 0.012, 0.012, h - 0.3)
        for z in (0.7, 1.2, 1.7): bm_box(bm, cx, cy, z, length, 0.012, 0.012)
    else:
        bm_box(bm, cx, cy, h - 0.03, 0.05, length, 0.05, bevel=0.004); bm_box(bm, cx, cy, 0.18, 0.05, length, 0.05, bevel=0.004)
        for k in range(1, int(length / 0.25)): bm_box(bm, cx, cy - length / 2 + k * 0.25, h / 2, 0.012, 0.012, h - 0.3)
        for z in (0.7, 1.2, 1.7): bm_box(bm, cx, cy, z, 0.012, length, 0.012)
    return mesh_obj(name, bm, F['steel_charcoal'], coll)

def build_fences(F, C):
    yard = C['YARD']
    def run(name, x0, x1, y, gaps):
        cuts = [x0]
        for c, w in sorted(gaps): cuts += [c - w / 2, c + w / 2]
        cuts.append(x1)
        k = 0
        for i in range(0, len(cuts), 2):
            a, b = cuts[i], cuts[i + 1]
            if b - a < 0.2: continue
            n = max(int(round((b - a) / 3.0)), 1); step = (b - a) / n
            for j in range(n):
                fence_panel(F, yard, f'{name}_panel{k}', a + j * step + step / 2, y, 'x', step - 0.14); k += 1
            for j in range(n + 1): box(f'{name}_post{k}', a + j * step - 0.06, a + j * step + 0.06, y - 0.06, y + 0.06, 0, 2.35, F['steel_charcoal'], yard, bev=0.008); k += 1
    run('fence_N', -48.0, -12.0, -60.1, [(RAIL_X, 3.0), (-46.0, 2.4)])
    run('fence_S', -48.0, -8.0, -84.0, [(-28.0, 6.0)])
    # freight gate: sliding leaf partly open on the rails + gate posts
    for s in (-1, 1):
        box(f'freight_gate_post{s}', RAIL_X + s * 1.55 - 0.15, RAIL_X + s * 1.55 + 0.15, -60.25, -59.95, 0, 3.3, F['steel_accent'], yard, bev=0.02)
    box('freight_gate_header', RAIL_X - 1.7, RAIL_X + 1.7, -60.25, -59.95, 3.1, 3.3, F['steel_accent'], yard, bev=0.02)
    fence_panel(F, yard, 'freight_gate_leaf', RAIL_X + 2.3, -60.5, 'x', 1.6, 2.4)
    # evacuation gate: two closed leaves with hazard stripes, posts and a keypad box
    for s in (-1, 1):
        cx = -28.0 + s * 1.5
        box(f'evac_leaf_frame{s}', cx - 1.45, cx + 1.45, -84.07, -83.93, 0.1, 2.3, F['steel_accent'], yard, bev=0.012)
        for k in range(8):
            xx = cx - 1.3 + k * 0.37
            box(f'evac_stripe_{s}_{k}', xx, xx + 0.17, -84.1, -83.9, 0.3, 2.0, F['signage'], yard, rgba=(0.05, 0.05, 0.05, 1) if k % 2 else (0.95, 0.75, 0.05, 1), bev=0.004)
        box(f'evac_post{s}', -28.0 + s * 3.1 - 0.15, -28.0 + s * 3.1 + 0.15, -84.15, -83.85, 0, 2.5, F['steel_charcoal'], yard, bev=0.02)
    box('evac_keypad', -28.15, -27.85, -83.8, -83.7, 1.1, 1.4, F['plastic'], yard, rgba=(0.1, 0.1, 0.1, 1), bev=0.01)
    # NW service door frame in the north fence
    box('service_door_L', -47.35, -47.2, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01)
    box('service_door_R', -44.8, -44.65, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01)
    box('service_door_H', -47.35, -44.65, -60.25, -59.95, 2.4, 2.55, F['steel_charcoal'], yard, bev=0.01)

def build_canopies(F, C):
    yard = C['YARD']
    def canopy(name, x0, x1, y0, y1, h, posts):
        for i, (px, py) in enumerate(posts): box(f'{name}_post{i}', px - 0.1, px + 0.1, py - 0.1, py + 0.1, 0, h, F['steel_charcoal'], yard, bev=0.012)
        box(f'{name}_beamA', x0, x1, y0 - 0.1, y0 + 0.1, h - 0.3, h, F['steel_charcoal'], yard, bev=0.012)
        box(f'{name}_beamB', x0, x1, y1 - 0.1, y1 + 0.1, h - 0.3, h, F['steel_charcoal'], yard, bev=0.012)
        k = 0; y = y0 + 1.0
        while y < y1: box(f'{name}_rafter{k}', x0, x1, y - 0.05, y + 0.05, h - 0.12, h, F['steel_charcoal'], yard); k += 1; y += 1.2
        box(f'{name}_roof', x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, h, h + 0.06, F['corrugated'], yard)
        x = x0; k = 0
        while x < x1: box(f'{name}_rib{k}', x, x + 0.04, y0 - 0.15, y1 + 0.15, h + 0.06, h + 0.12, F['corrugated'], yard); x += 0.5; k += 1
        box(f'{name}_edge_accent', x0 - 0.17, x1 + 0.17, y0 - 0.17, y0 - 0.13, h - 0.05, h + 0.14, F['steel_accent'], yard)
        box(f'{name}_edge_accent2', x0 - 0.17, x1 + 0.17, y1 + 0.13, y1 + 0.17, h - 0.05, h + 0.14, F['steel_accent'], yard)
    canopy('porch', -12.0, -8.0, -76.0, -64.0, 3.4, [(-12.0, -76.0), (-12.0, -73.0), (-12.0, -67.0), (-12.0, -64.0)])
    canopy('loading_canopy', -26.0, -18.0, -64.0, -60.0, 3.9, [(-26.0, -64.0), (-18.0, -64.0), (-26.0, -60.4), (-18.0, -60.4)])
    # stack of hanging lamps under canopies
    for i, (x, y) in enumerate(((-10.0, -70.0), (-10.0, -66.0), (-10.0, -74.0), (-22.2, -62.0))):
        box(f'canopy_lamp{i}', x - 0.35, x + 0.35, y - 0.12, y + 0.12, 3.15 if x > -15 else 3.65, 3.25 if x > -15 else 3.75, F['emissive'], yard, rgba=(1, 0.88, 0.62, 1), bev=0.01)

def scatter(rng, rect, n, avoid, min_d, tries=400):
    pts = []
    for _ in range(n):
        for _ in range(tries):
            x = rng.uniform(rect[0], rect[1]); y = rng.uniform(rect[2], rect[3])
            if any(a[0] <= x <= a[1] and a[2] <= y <= a[3] for a in avoid): continue
            if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < min_d ** 2 for p in pts): continue
            pts.append((x, y)); break
    return pts

def build_props(F, C, extra_avoid=()):
    yard = C['YARD']
    P = collection('PROTOTYPES')       # excluded from render
    rng = random.Random(11)
    crate = [proto_crate(F, P, v) for v in range(4)]
    pallet = proto_pallet(F, P)
    barrels = [proto_barrel(F, P, c) for c in ((0.18, 0.28, 0.42, 1), (0.55, 0.15, 0.12, 1), (0.32, 0.34, 0.30, 1))]
    drum = proto_drum(F, P); cabledrum = proto_cable_drum(F, P); tyre = proto_tyre(F, P); cone = proto_cone(F, P); bollard = proto_bollard(F, P)
    bench = proto_bench(F, P); planter = proto_planter(F, P); soil = proto_soil(F, P)
    shrubs = [proto_shrub(F, P, s) for s in range(3)]; trees = [proto_tree(F, P, s) for s in range(2)]
    pole = proto_pole(F, P); glow = proto_lamp_glow(F, P)
    scraps = [proto_scrap(F, P, s) for s in range(3)]; tarps = [proto_tarp(F, P, s) for s in range(2)]
    cart = proto_cart(F, P); gen = proto_generator(F, P); tank = proto_tank_v(F, P)
    # keep-clear: mine lane, rails, gates, canopy footprints, porch
    avoid = [(-48, -8, -71.3, -68.7), (-47.2, RAIL_X + 1.2, RAIL_Y - 1.2, RAIL_Y + 1.2), (RAIL_X - 1.2, RAIL_X + 1.2, RAIL_Y, -59.5),
             (-31.5, -24.5, -85, -82), (-12.5, -8, -77, -63), (-27, -17, -65, -59.5), (-47.3, -44.9, -68.7, -59.5), (-29.6, -26.4, -84, -71.3)] + list(extra_avoid)
    clusters = {
        'A': (-46.5, -20.0, -67.8, -60.5), 'B': (-46.5, -26.0, -83.5, -72.0), 'C': (-30.0, -12.0, -83.5, -72.0), 'D': (-14.0, -9.5, -83.0, -77.0)}
    junk = []
    # crates: 10 stacks of 1-3
    for i, (x, y) in enumerate(scatter(rng, clusters['A'], 5, avoid, 1.5) + scatter(rng, clusters['B'], 3, avoid, 1.5) + scatter(rng, clusters['C'], 2, avoid, 1.5)):
        n = rng.choice((1, 2, 2, 3)); rz = rng.uniform(-0.4, 0.4)
        for k in range(n):
            o = inst(crate[rng.randrange(4)], f'crate_{i}_{k}', x + rng.uniform(-0.05, 0.05) * k, y, yard, rz=rz + rng.uniform(-0.08, 0.08), z=k * 1.0, support='floor' if k == 0 else 'stack')
    for i, (x, y) in enumerate(scatter(rng, clusters['C'], 4, avoid, 1.4) + scatter(rng, clusters['A'], 2, avoid, 1.4) + scatter(rng, clusters['D'], 2, avoid, 1.4)):
        inst(pallet, f'pallet_{i}', x, y, yard, rz=rng.uniform(0, math.pi))
    for i, (x, y) in enumerate(scatter(rng, clusters['A'], 6, avoid, 0.7) + scatter(rng, clusters['B'], 8, avoid, 0.7) + scatter(rng, clusters['D'], 6, avoid, 0.7)):
        inst(barrels[rng.randrange(3)], f'barrel_{i}', x, y, yard)
    for i, (x, y) in enumerate(scatter(rng, clusters['B'], 4, avoid, 1.4)):
        inst(drum, f'drum_{i}', x, y, yard) if False else inst(cabledrum, f'cable_drum_{i}', x, y, yard, rz=rng.uniform(0, 3))
    for i, (x, y) in enumerate(scatter(rng, clusters['B'], 3, avoid, 3.0)):
        inst(scraps[i % 3], f'scrap_{i}', x, y, yard, rz=rng.uniform(0, 3), support=None)
    for i, (x, y) in enumerate(scatter(rng, clusters['C'], 2, avoid, 3.0)):
        inst(tarps[i % 2], f'tarp_pile_{i}', x, y, yard, rz=rng.uniform(0, 3), support=None)
    for i, (x, y) in enumerate(scatter(rng, clusters['B'], 6, avoid, 0.9)):
        inst(tyre, f'tyre_{i}', x, y, yard)
    # cones and bollards
    cone_pts = [(-24.6, -61.5), (-19.8, -61.5), (-24.6, -66.5), (-19.8, -66.5), (-45.5, -72.9), (-45.5, -72.0), (-13.0, -62.0), (-13.0, -83.0), (-33.2, -83.0), (-22.8, -83.0)]
    for i, (x, y) in enumerate(cone_pts): inst(cone, f'cone_{i}', x, y, yard, rz=rng.uniform(0, 3))
    for i, y in enumerate((-61.0, -66.5, -73.8, -77.0, -80.5)): inst(bollard, f'bollard_{i}', -8.9, y, yard)
    for i, x in enumerate((-30.0, -26.0, -20.0)): inst(bollard, f'gate_bollard_{i}', x, -83.0, yard) if False else None
    # carts on the track (wheels at track gauge)
    for i, x in enumerate((-40.0, -35.0)): inst(cart, f'ore_cart_{i}', x, RAIL_Y, yard, support=None).location.z = 0.0
    # generator, tanks
    inst(gen, 'generator', -13.0, -80.0, yard, rz=math.pi / 2); inst(tank, 'fuel_tank', -16.5, -81.0, yard); inst(tank, 'water_tank', -11.0, -62.6, yard, scale=(0.9, 0.9, 0.9))
    # benches, planters, shrubs, trees
    for i, (x, y) in enumerate(((-10.5, -64.8), (-10.5, -75.2), (-10.5, -77.2))): inst(bench, f'bench_{i}', x, y, yard, rz=math.pi / 2)
    for i, (x, y) in enumerate(((-9.0, -62.0), (-9.0, -65.0), (-9.0, -78.0), (-9.0, -81.0), (-14.0, -63.0), (-9.0, -61.0))):
        inst(planter, f'planter_{i}', x, y, yard); inst(soil, f'planter_soil_{i}', x, y, yard, support=None)
        inst(shrubs[i % 3], f'planter_shrub_{i}', x, y, yard, rz=rng.uniform(0, 3), z=0.6, support=None)
    for i, (x, y) in enumerate(scatter(rng, (-47, -9, -83, -61), 14, avoid + [(-12.5, -8, -83, -60)], 3.0)):
        inst(shrubs[i % 3], f'shrub_{i}', x, y, yard, rz=rng.uniform(0, 3), scale=(rng.uniform(0.8, 1.2),) * 3, support=None)
    for i, (x, y) in enumerate(((-45.0, -62.0), (-44.2, -80.6), (-34.0, -62.0), (-16.0, -80.8))): inst(trees[i % 2], f'tree_{i}', x, y, yard, rz=rng.uniform(0, 3), support=None)
    # pole lights with a soft spot each
    for i, (x, y) in enumerate(((-40.0, -66.0), (-30.0, -66.0), (-20.0, -66.5), (-34.0, -80.0), (-14.0, -66.5))):
        inst(pole, f'pole_{i}', x, y, yard, rz=math.pi); inst(glow, f'pole_glow_{i}', x, y, yard, rz=math.pi, support=None)
        l = bpy.data.lights.new(f'POLE_SPOT_{i}', 'SPOT'); l.energy = 900; l.spot_size = math.radians(110); l.spot_blend = 0.6; l.color = (1.0, 0.86, 0.62)
        o = bpy.data.objects.new(f'POLE_SPOT_{i}', l); o.location = (LX(x) - 0.88, LY(y), 4.8); o.rotation_euler = (0, 0, 0); C['LIGHTS'].objects.link(o)
    # exclude prototypes from view layers
    bpy.context.view_layer.layer_collection.children[P.name].exclude = True if P.name in bpy.context.view_layer.layer_collection.children else False

def build_signs(F, C):
    yard = C['YARD']
    signs = [('MINE', (-47.7, -70.0), 'W', (0.95, 0.75, 0.05, 1)), ]
    def sign(name, text, x, y, z, facing, plate=(0.9, 0.9, 0.9, 1), ink=(0.05, 0.05, 0.05, 1), w=1.4, h=0.45, mount='wall', support=None):
        # plate
        if facing in ('E', 'W'): pl = box(name + '_plate', x - 0.025, x + 0.025, y - w / 2, y + w / 2, z, z + h, F['signage'], yard, rgba=plate, bev=0.006)
        else: pl = box(name + '_plate', x - w / 2, x + w / 2, y - 0.025, y + 0.025, z, z + h, F['signage'], yard, rgba=plate, bev=0.006)
        cu = bpy.data.curves.new(name + '_text', 'FONT'); cu.body = text; cu.size = h * 0.55; cu.extrude = 0.004; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        o = bpy.data.objects.new(name + '_text', cu); yard.objects.link(o)
        o.data.materials.append(F['signage']); color_attr_obj = None
        rot = {'E': (math.pi / 2, 0, math.pi / 2), 'W': (math.pi / 2, 0, -math.pi / 2), 'N': (math.pi / 2, 0, math.pi), 'S': (math.pi / 2, 0, 0)}[facing]
        o.rotation_euler = rot
        off = {'E': (0.03, 0), 'W': (-0.03, 0), 'N': (0, 0.03), 'S': (0, -0.03)}[facing]
        o.location = (LX(x) + off[0], LY(y) + off[1], z + h / 2)
        return pl, o
    return sign
