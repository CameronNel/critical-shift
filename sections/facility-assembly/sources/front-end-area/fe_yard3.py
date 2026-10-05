"""Yard shell for the mine surface depot: concrete apron with light wear, natural rock cliff, mine portal collar and timbered mouth, rail, perimeter fence and gates, canopies, drains.
Everything standing on the apron lives in fe_depot. Plan frame: yard x -48..-8, y -84..-60; mine axis y = -70; rail turns north at x = -22.2 to the refinery freight gate."""
import math, random
from fe_common import *
from fe_props import *
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import fence_panel, fence_post
from fe_yard import inst, YARD, RAIL_Y, RAIL_X, GATE
from fe_signs import sign, hanging_sign
import mathutils.noise as mnoise

PORTAL_Y = -70.0
FLAT_X = -49.0            # cliff face is flattened to this x around the portal so the collar sits on it

def smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)

# ----------------------------------------------------------------------------------------------------- ground
# Hardstanding where the work is: plan rectangles (x0, x1, y0, y1). Everything else is wet mud, with a gravel haul road along the mine lane and to the evacuation gate.
PADS = [(-47.8, -29.9, -83.8, -76.4),    # fuel and vehicle bays
        (-47.0, -39.0, -76.4, -72.6),    # lamp room cabin
        (-46.0, -29.0, -63.9, -60.0),    # ore bays
        (-27.5, -16.8, -67.4, -60.0),    # rail dock and loading canopy
        (-25.0, -17.0, -83.8, -72.0),    # stores and muster
        (-16.8, -9.5, -83.8, -77.6),     # generator and water
        (-13.0, -8.0, -77.6, -60.0),     # porch forecourt
        (-16.8, -13.0, -65.0, -60.0)]    # skips
RUTS = [([(-34.8, -72.0), (-35.2, -74.5), (-35.0, -76.6)], 0.78), ([(-38.4, -72.0), (-38.0, -74.0), (-37.2, -76.6)], 0.75), ([(-31.6, -72.0), (-31.2, -74.4), (-31.8, -76.6)], 0.8),
        ([(-40.0, -68.0), (-38.6, -66.0), (-37.2, -64.2)], 0.78), ([(-34.0, -68.0), (-33.2, -66.0), (-32.6, -64.2)], 0.78), ([(-31.0, -68.0), (-29.2, -66.8), (-27.6, -66.0)], 0.7),
        ([(-44.5, -71.8), (-44.8, -73.0), (-46.0, -74.5)], 0.7), ([(-16.0, -71.8), (-15.4, -74.5), (-15.2, -77.2)], 0.75), ([(-16.0, -68.0), (-15.6, -66.0)], 0.7)]
POOLS = [(-34.4, -74.4, 1.5, 0.05), (-37.4, -74.4, 0.9, 0.04), (-31.4, -75.6, 1.0, 0.04), (-40.6, -66.6, 1.1, 0.045), (-33.2, -66.6, 1.0, 0.04), (-15.0, -75.5, 1.1, 0.045),
         (-15.2, -66.6, 0.9, 0.04), (-47.2, -66.0, 0.9, 0.04), (-28.2, -74.2, 0.7, 0.03)]
GRAVEL = [(-49.5, -13.0, -71.9, -68.1, 0.5), (-29.7, -26.3, -84.0, -71.0, 0.4)]

def on_pad(x, y, m=0.0):
    return any(a - m <= x <= b + m and c - m <= y <= d + m for a, b, c, d in PADS)

def build_ground(F, C):
    import copy
    from fe_mud import build_terrain
    yard = C['YARD']; rnd = random.Random(77)
    ground = box('context_ground', -170, 90, -200, 60, -0.9, -0.15, F['props'], C['SHARED'], rgba=(0.06, 0.05, 0.04, 1)); ground['note'] = 'context only, outside the module footprint'
    box('yard_base', *YARD[:2], *YARD[2:], -0.45, -0.3, F['props'], yard, rgba=(0.06, 0.05, 0.04, 1))
    build_terrain(F, C, YARD, RUTS, POOLS, PADS, GRAVEL)
    Pc = collection('PROTOTYPES')
    def stone(seed, size):
        r = random.Random(seed); m = mb(F); pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=1, radius=1.0)
        for v in res['verts']:
            k = 1.0 + r.uniform(-0.3, 0.3); v.co = Vector((v.co.x * size * k, v.co.y * size * 0.85 * k, v.co.z * size * 0.55 * k))
        for f in pb.faces: f.smooth = False
        m.add(pb, mi=I['props'], rgba=r.choice(((0.05, 0.045, 0.04, 1), (0.09, 0.075, 0.06, 1), (0.14, 0.12, 0.10, 1), (0.07, 0.06, 0.07, 1))))
        return m.finish(f'proto_stone_{seed}', Pc)
    stones = [stone(61 + k, 0.05 + 0.014 * (k % 3)) for k in range(6)]
    for k in range(520):
        x = rnd.uniform(-47.5, -8.5); y = rnd.uniform(-83.5, -60.5)
        if on_pad(x, y, 0.3): continue
        inst(stones[k % 6], f'stone_{k}', x, y, yard, rz=rnd.uniform(0, 6.28), z=-0.02, scale=(rnd.uniform(0.6, 1.8),) * 3, support='floor_debris')
    wet = F['apron'].copy(); wet.name = 'apron_wet'
    for n in wet.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED' and 'Coat Weight' in n.inputs: n.inputs['Coat Weight'].default_value = 0.45; n.inputs['Coat Roughness'].default_value = 0.08
    sunk = {}
    for pi, (a, b, c, d) in enumerate(PADS):
        nx = max(int(round((b - a) / 4.0)), 1); ny = max(int(round((d - c) / 4.0)), 1); sw = (b - a) / nx; sh = (d - c) / ny
        for ix in range(nx):
            for iy in range(ny):
                x0 = a + ix * sw + 0.015; y0 = c + iy * sh + 0.015
                o = box(f'pad_{pi}_{ix}_{iy}', 0, sw - 0.03, 0, sh - 0.03, -0.15, 0.0, wet, yard, bev=0.012, plan=False)
                o.location = (LX(x0), LY(y0), rnd.choice((0.0, 0.0, -0.004, -0.008))); o.rotation_euler = (rnd.uniform(-0.002, 0.002), rnd.uniform(-0.002, 0.002), 0); o['support'] = 'floor_broken'
    bmm = bmesh.new()
    for i in range(14):
        a, b, c, d = rnd.choice(PADS); x = rnd.uniform(a + 0.5, b - 0.5); y = rnd.uniform(c + 0.5, d - 0.5); ang = rnd.uniform(0, 6.28)
        for k in range(rnd.randint(3, 5)):
            if not on_pad(x, y): break
            L = rnd.uniform(0.4, 0.9); bm_box(bmm, LX(x), LY(y), 0.003, L, 0.014, 0.004, rz=ang)
            x += math.cos(ang) * L * 0.9; y += math.sin(ang) * L * 0.9; ang += rnd.uniform(-0.7, 0.7)
    mesh_obj('ground_cracks', bmm, F['props'], yard, rgba=(0.03, 0.028, 0.026, 1))

def build_drains(F, C):
    """Three trench drains: across the loading apron, in front of the fuel bay and on the porch approach. Gratings are bars, not text."""
    yard = C['YARD']
    def trench(name, x0, x1, y):
        box(name + '_frame_a', x0, x1, y - 0.2, y - 0.14, -0.1, 0.0, F['steel_charcoal'], yard); box(name + '_frame_b', x0, x1, y + 0.14, y + 0.2, -0.1, 0.0, F['steel_charcoal'], yard)
        box(name + '_sump', x0, x1, y - 0.14, y + 0.14, -0.22, -0.1, F['props'], yard, rgba=(0.05, 0.05, 0.05, 1))
        bm = bmesh.new(); x = x0 + 0.1
        while x < x1 - 0.05: bm_box(bm, LX(x), LY(y), -0.03, 0.035, 0.28, 0.05); x += 0.12
        mesh_obj(name + '_grating', bm, F['steel_charcoal'], yard)
    trench('drain_apron', -26.0, -18.0, -66.6); trench('drain_fuel', -47.0, -43.0, -79.3); trench('drain_porch', -12.0, -8.4, -77.0)

# ----------------------------------------------------------------------------------------------------- cliff
def cliff_x(y, z):
    """Cliff face x (plan) at (y, z): natural batter, strata benches, jointing and weathering; flattened to FLAT_X around the portal; recess cut for the portal."""
    n0 = mnoise.noise(Vector((y * 0.08, z * 0.10, 1.1))); n1 = mnoise.noise(Vector((y * 0.22, z * 0.28, 4.4)))
    n2 = mnoise.noise(Vector((y * 0.7, z * 0.8, 7.7))); n3 = mnoise.noise(Vector((y * 2.2, z * 2.2, 3.3)))
    t = z / 3.4; fr = t - math.floor(t)
    bench = 0.5 * (math.floor(t) + smooth(0.72, 1.0, fr))
    jn = abs(mnoise.noise(Vector((y * 1.25, 0.5, z * 0.12))))
    joint = 0.45 * (1.0 - smooth(0.0, 0.07, jn)) * smooth(0.4, 1.5, z)
    x = -48.3 - 0.09 * z - 0.0006 * z * z - bench - 1.8 * n0 - 1.1 * n1 - 0.45 * n2 - 0.1 * n3 - joint
    dy = abs(y - PORTAL_Y); wp = smooth(6.5, 12.0, dy); wz = smooth(7.5, 11.0, z)
    w = max(wp, wz)
    x = (FLAT_X + 0.03 * n3) * (1 - w) + x * w
    if dy <= 3.6 and z <= 3.9: x = -53.6 + 0.03 * n3
    elif dy <= 4.2 and z <= 4.4: x = min(x, -50.4)
    return x

def build_cliff(F, C):
    yard = C['YARD']
    Y0, Y1, ZH = -92.0, -54.0, 17.0
    CY, CZ = 0.25, 0.25
    NY, NZ = int((Y1 - Y0) / CY), int(ZH / CZ)
    bm = bmesh.new(); verts = []
    for i in range(NY + 1):
        y = Y0 + CY * i; row = []
        for j in range(NZ + 1):
            ztop = ZH * (0.8 + 0.2 * (0.5 + 0.5 * mnoise.noise(Vector((y * 0.09, 5.5, 0.2))))) * min(1.0, 0.3 + min(y - Y0, Y1 - y) / 9.0)
            zz = min(CZ * j, ztop)
            row.append(bm.verts.new(Vector((LX(cliff_x(y, zz)), LY(y), zz))))
        verts.append(row)
    for i in range(NY):
        for j in range(NZ): bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces: f.smooth = True
    mesh_obj('cliff_face', bm, F['rock'], yard, smooth=True)
    box('mountain_mass', -90, -56.0, -96, -50, -1.0, 9.0, F['rock'], C['SHARED'])
    box('cliff_kerb_S', -48.4, -47.4, -84, -71.4, -0.15, 0.35, F['concrete_slab'], yard, bev=0.03); box('cliff_kerb_N', -48.4, -47.4, -68.6, -60, -0.15, 0.35, F['concrete_slab'], yard, bev=0.03)
    P = collection('PROTOTYPES'); rb = random.Random(21)
    from fe_assets_site import rubble_chunk
    rocks = [rubble_chunk(F, P, 20 + s, 0.9) for s in range(6)]
    for i in range(12):
        yy = -91 + i * 2.8 + rb.uniform(-0.6, 0.6)
        if -78 < yy < -62: continue
        inst(rocks[i % 6], f'boulder_{i}', -49.0 + rb.uniform(-0.9, 0.1), yy, yard, rz=rb.uniform(0, 6.28), z=-0.05, scale=(rb.uniform(1.0, 2.0),) * 3, support='floor_broken')
    from fe_assets_yard import shrub
    shs = [shrub(F, P, 30 + s, 0.38, 36) for s in range(3)]; vr = random.Random(9)
    for i in range(16):
        yy = vr.uniform(-90, -56)
        if -78 < yy < -62: continue
        zz = vr.choice((3.4, 6.8, 10.2)) - 0.05
        inst(shs[i % 3], f'cliff_shrub_{i}', cliff_x(yy, zz - 0.25) + 0.12, yy, yard, rz=vr.uniform(0, 6.28), z=zz, scale=(vr.uniform(0.8, 1.4),) * 3, support=None)
    return cliff_x

# ----------------------------------------------------------------------------------------------------- portal
def build_portal(F, C):
    """Mine portal: concrete collar with piers and lintel on the flattened face, steel jamb liners, three timber sets with lagging in the mouth, hazard-striped lintel kicker, lamps, baked entrance plates, rock bolts and safety mesh on the face above."""
    yard = C['YARD']; P = collection('PROTOTYPES')
    xf0, xf1 = -49.9, -48.5; y0, y1 = -75.6, -64.4
    for nm, a, b in (('L', y0, -73.6), ('R', -66.4, y1)): box(f'portal_pier_{nm}', xf0, xf1, a, b, 0.0, 3.9, F['concrete_slab'], yard, bev=0.0)
    box('portal_lintel', xf0, xf1, y0, y1, 3.9, 5.3, F['concrete_slab'], yard, bev=0.03)
    box('portal_cap', xf0 - 0.1, xf1 + 0.15, y0 - 0.15, y1 + 0.15, 5.3, 5.5, F['concrete_slab'], yard, bev=0.03)
    for nm, yy in (('L', -73.6), ('R', -66.4)): box(f'portal_jamb_{nm}', xf1 - 0.04, xf1 + 0.06, yy - 0.12 if nm == 'R' else yy - 0.02, yy + 0.02 if nm == 'R' else yy + 0.12, 0.0, 3.9, F['steel_charcoal'], yard, bev=0.01)
    box('portal_header_steel', xf1 - 0.04, xf1 + 0.06, -73.62, -66.38, 3.78, 3.9, F['steel_charcoal'], yard, bev=0.01)
    k = 0
    for i in range(14):                                                                                   # hazard kicker on the lintel soffit
        yy = -73.6 + i * (7.2 / 14); box(f'portal_haz_{i}', xf1 + 0.06, xf1 + 0.1, yy, yy + 7.2 / 14, 3.58, 3.78, F['signage'], yard, rgba=(0.95, 0.75, 0.05, 1) if i % 2 == 0 else (0.04, 0.04, 0.04, 1))
    sign(yard, 'sign_mine_entrance', 'MINE ENTRANCE', xf1 + 0.1, PORTAL_Y, 4.1, 'E', 3.8, 0.7, sub='Authorised personnel  -  tag in at the lamp room', icon='warn', style='nav')
    for nm, yy in (('L', -73.9), ('R', -66.1)):
        box(f'portal_lamp_{nm}', xf1 + 0.1, xf1 + 0.3, yy - 0.12, yy + 0.12, 3.0, 3.25, F['emissive'], yard, rgba=(1.0, 0.8, 0.5, 1), bev=0.02)
        box(f'portal_lamp_cage_{nm}', xf1 + 0.1, xf1 + 0.34, yy - 0.16, yy + 0.16, 2.95, 3.3, F['steel_charcoal'], yard, bev=0.01) if False else None
    # timbered mouth
    box('portal_void', -58.0, -53.4, -73.3, -66.7, 0.0, 3.5, F['rubber'], yard, rgba=(0.01, 0.01, 0.01, 1))
    box('portal_floor', -53.6, -47.5, -73.3, -66.7, -0.2, 0.0, F['props'], yard, rgba=(0.12, 0.1, 0.08, 1))
    box('mouth_wall_L', -53.5, -49.9, -73.35, -73.1, 0.0, 3.5, F['timber'], yard, bev=0.02); box('mouth_wall_R', -53.5, -49.9, -66.9, -66.65, 0.0, 3.5, F['timber'], yard, bev=0.02)
    box('mouth_roof', -53.5, -49.9, -73.35, -66.65, 3.4, 3.6, F['timber'], yard, bev=0.02)
    for k, xx in enumerate((-50.6, -52.0, -53.2)):
        for s_, yy in (('L', -73.0), ('R', -67.0)): box(f'mouth_post_{k}{s_}', xx - 0.15, xx + 0.15, yy - 0.15, yy + 0.15, 0.0, 3.4, F['timber'], yard, bev=0.02)
        box(f'mouth_cap_{k}', xx - 0.15, xx + 0.15, -73.2, -66.8, 3.25, 3.45, F['timber'], yard, bev=0.02)
    for k, xx in enumerate((-51.3, -52.6)): box(f'mouth_lamp_{k}', xx - 0.2, xx + 0.2, -70.15, -69.85, 3.1, 3.25, F['emissive'], yard, rgba=(1.0, 0.7, 0.35, 1), bev=0.01)
    # rock bolts and safety mesh on the face above and either side of the portal
    rbolt = rock_bolt_proto(F, P); mesh = safety_mesh_proto(F, P)
    for r_ in range(3):
        for c_ in range(14):
            yy = -76.5 + c_ * 0.9 + (0.45 if r_ % 2 else 0.0); zz = 6.1 + r_ * 1.05
            if -75.9 < yy < -64.1 and zz < 5.6: continue
            inst(rbolt, f'rock_bolt_{r_}_{c_}', cliff_x(yy, zz) + 0.0, yy, yard, rz=-math.pi / 2, z=zz, support=None)
    for i, yy in enumerate((-77.4, -75.0, -72.6, -70.2, -67.8, -65.4, -63.0)):
        inst(mesh, f'safety_mesh_{i}', cliff_x(yy, 6.5) + 0.06, yy, yard, rz=-math.pi / 2, z=5.55, support=None)

def rock_bolt_proto(F, P):
    from fe_depot_assets import rock_bolt
    return rock_bolt(F, P)

def safety_mesh_proto(F, P):
    from fe_depot_assets import safety_mesh
    return safety_mesh(F, P, 2.4, 1.6)

# ----------------------------------------------------------------------------------------------------- rails
def rail_path(F, yard, name, pts, gauge=0.78):
    rail_bm = bmesh.new(); sl_bm = bmesh.new(); fp_bm = bmesh.new()
    acc = 0.0; k = 0
    for a, b in zip(pts[:-1], pts[1:]):
        dxy = (b[0] - a[0], b[1] - a[1]); L = math.hypot(*dxy); ang = math.atan2(dxy[1], dxy[0]); nx, ny = -math.sin(ang), math.cos(ang)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        for s in (-1, 1):
            cx, cy = mx + nx * s * gauge, my + ny * s * gauge
            bm_box(rail_bm, LX(cx), LY(cy), 0.155, L + 0.01, 0.07, 0.04, rz=ang, bevel=0.006)
            bm_box(rail_bm, LX(cx), LY(cy), 0.115, L + 0.01, 0.018, 0.08, rz=ang)
            bm_box(rail_bm, LX(cx), LY(cy), 0.075, L + 0.01, 0.11, 0.016, rz=ang)
        acc += L
        if acc >= 0.62:
            acc = 0.0
            bm_box(sl_bm, LX(mx), LY(my), 0.04, 0.2, 1.9, 0.09, rz=ang, bevel=0.012, seg=2)
            for s in (-1, 1): bm_box(sl_bm, LX(mx + nx * s * gauge), LY(my + ny * s * gauge), 0.092, 0.16, 0.17, 0.014, rz=ang)
        k += 1
        if k % 20 == 0:
            for s in (-1, 1):
                cx, cy = mx + nx * s * gauge, my + ny * s * gauge
                bm_box(fp_bm, LX(cx), LY(cy), 0.115, 0.55, 0.1, 0.07, rz=ang, bevel=0.008)
                for d in (-0.2, -0.07, 0.07, 0.2): bm_cyl(fp_bm, LX(cx + math.cos(ang) * d), LY(cy + math.sin(ang) * d), 0.1, 0.13, 0.014, seg=6)
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
    P = collection('PROTOTYPES'); rb = random.Random(5)
    from fe_assets_site import rubble_chunk
    st = [rubble_chunk(F, P, 40 + s, 0.07) for s in range(4)]
    for i in range(0, len(pts), 3):
        for s in (-1, 1):
            x, y = pts[i]; j = min(i + 1, len(pts) - 1); ang = math.atan2(pts[j][1] - y, pts[j][0] - x); nx, ny = -math.sin(ang), math.cos(ang)
            if rb.random() < 0.3: inst(st[rb.randrange(4)], f'ballast_{i}_{s}', x + nx * rb.uniform(1.0, 1.25) * s, y + ny * rb.uniform(1.0, 1.25) * s, yard, rz=rb.uniform(0, 6), z=-0.01, scale=(rb.uniform(0.8, 1.5),) * 3, support='floor_debris')
    # buffer stop where the rail leaves the tunnel mouth is not needed (the track runs on); rail-end marker at the freight gate threshold
    box('rail_stop_marker', RAIL_X - 0.2, RAIL_X + 0.2, -60.6, -60.4, 0.0, 0.5, F['steel_accent'], yard, bev=0.01)

# ----------------------------------------------------------------------------------------------------- fences, gates, canopies
def build_fences(F, C):
    """Perimeter mesh fence with three gates: refinery freight gate (rail), evacuation gate (south) and the cooling-plant service door (north-west). Gate furniture and signs come from fe_depot."""
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
                inst(fp, f'{name}_panel{k}', a + j * step + step / 2, y, yard, scale=((step - 0.1) / 3.0, 1, 1), support='floor'); k += 1
            for j in range(n + 1): inst(fpost, f'{name}_post{k}', a + j * step, y, yard); k += 1
    run('fence_N', -48.0, -8.4, -60.1, [(RAIL_X, 3.0), (-46.0, 2.4)])
    run('fence_S', -48.0, -8.0, -84.0, [(-28.0, 6.0)])
    for s in (-1, 1): box(f'freight_gate_post{s}', RAIL_X + s * 1.55 - 0.15, RAIL_X + s * 1.55 + 0.15, -60.25, -59.95, 0, 3.3, F['steel_accent'], yard, bev=0.02)
    box('freight_gate_header', RAIL_X - 1.7, RAIL_X + 1.7, -60.25, -59.95, 3.1, 3.3, F['steel_accent'], yard, bev=0.02)
    inst(fp, 'freight_gate_leaf', RAIL_X + 2.3, -60.5, yard, scale=(0.55, 1, 1), z=0.0, support='floor')
    for s in (-1, 1):
        cx = -28.0 + s * 1.5
        box(f'evac_leaf_frame{s}', cx - 1.45, cx + 1.45, -84.07, -83.93, 0.1, 2.3, F['steel_accent'], yard, bev=0.012)
        for k in range(8):
            xx = cx - 1.3 + k * 0.37
            box(f'evac_stripe_{s}_{k}', xx, xx + 0.17, -84.1, -83.9, 0.3, 2.0, F['signage'], yard, rgba=(0.05, 0.05, 0.05, 1) if k % 2 else (0.92, 0.72, 0.05, 1), bev=0.004)
        box(f'evac_push_bar_{s}', cx - 1.2, cx + 1.2, -83.86, -83.8, 1.0, 1.05, F['steel_brushed'], yard, bev=0.01)
        box(f'evac_post{s}', -28.0 + s * 3.1 - 0.15, -28.0 + s * 3.1 + 0.15, -84.15, -83.85, 0, 2.5, F['steel_charcoal'], yard, bev=0.02)
    box('evac_keypad', -28.15, -27.85, -83.8, -83.7, 1.1, 1.4, F['plastic'], yard, rgba=(0.1, 0.1, 0.1, 1), bev=0.01)
    box('service_door_L', -47.35, -47.2, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01); box('service_door_R', -44.8, -44.65, -60.25, -59.95, 0, 2.4, F['steel_charcoal'], yard, bev=0.01)
    box('service_door_H', -47.35, -44.65, -60.25, -59.95, 2.4, 2.55, F['steel_charcoal'], yard, bev=0.01)
    box('service_door_leaf', -47.2, -44.8, -60.2, -60.1, 0.05, 2.35, F['paint'], yard, rgba=(0.45, 0.1, 0.08, 1), bev=0.01)
    box('service_door_push', -47.1, -46.9, -60.3, -60.2, 1.0, 1.05, F['steel_brushed'], yard, bev=0.01)

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
    for i, (x, y) in enumerate(((-10.0, -70.0), (-10.0, -66.0), (-10.0, -74.0), (-22.2, -62.0))):
        box(f'canopy_lamp{i}', x - 0.35, x + 0.35, y - 0.12, y + 0.12, 3.15 if x > -15 else 3.65, 3.25 if x > -15 else 3.75, F['emissive'], yard, rgba=(1, 0.88, 0.62, 1), bev=0.01)
