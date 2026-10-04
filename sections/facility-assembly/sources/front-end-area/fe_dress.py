"""Wall panels, vents, conduits, signs, floor wear: the surface detail that stops big walls and floors reading as blank."""
from fe_common import *
from fe_props import *
from fe_yard import inst

TEXT_ROT = {'S': (math.pi / 2, 0, 0), 'N': (math.pi / 2, 0, math.pi), 'E': (math.pi / 2, 0, math.pi / 2), 'W': (math.pi / 2, 0, -math.pi / 2)}
NORMAL = {'S': (0, -1), 'N': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

def wall_sign(F, coll, name, text, x, y, z, facing, w=1.4, h=0.4, plate=(0.08, 0.08, 0.09, 1), ink='emissive', size=None, wall_plane=None, register=True, ink_rgba=None):
    nx, ny = NORMAL[facing]
    t = 0.025
    if facing in ('E', 'W'): pl = box(name + '_plate', x - t / 2, x + t / 2, y - w / 2, y + w / 2, z, z + h, F['signage'], coll, rgba=plate, bev=0.005)
    else: pl = box(name + '_plate', x - w / 2, x + w / 2, y - t / 2, y + t / 2, z, z + h, F['signage'], coll, rgba=plate, bev=0.005)
    cu = bpy.data.curves.new(name + '_text', 'FONT'); cu.body = text; cu.size = size or h * 0.5; cu.extrude = 0.003; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name + '_text', cu); o.data.materials.append(F['emissive' if ink == 'emissive' else 'signage']); coll.objects.link(o)
    o.rotation_euler = TEXT_ROT[facing]; o.location = (LX(x) + nx * (t / 2 + 0.003), LY(y) + ny * (t / 2 + 0.003), z + h / 2)
    if register and wall_plane is not None:
        wall_item(pl, 'x' if facing in ('E', 'W') else 'y', wall_plane, -1 if (nx + ny) > 0 else +1)
    return pl

def panels(F, coll, prefix, axis, pos, a0, a1, z0, z1, face_off, excl=(), pitch=1.2, mat='plaster', rgba=None):
    """Raised wall panels on one face. face_off is the signed offset from the wall centre line to the face (e.g. +0.15)."""
    n = int((a1 - a0) / pitch); k = 0
    for i in range(n):
        c0 = a0 + i * pitch + 0.06; c1 = a0 + (i + 1) * pitch - 0.06
        if any(not (c1 < e0 or c0 > e1) for e0, e1 in excl): continue
        s = 1 if face_off > 0 else -1
        d0, d1 = pos + face_off, pos + face_off + s * 0.022
        if axis == 'x': box(f'{prefix}_pnl{k}', c0, c1, min(d0, d1), max(d0, d1), z0, z1, F[mat], coll, bev=0.006, rgba=rgba)
        else: box(f'{prefix}_pnl{k}', min(d0, d1), max(d0, d1), c0, c1, z0, z1, F[mat], coll, bev=0.006, rgba=rgba)
        k += 1
    return k

def vent(F, coll, name, axis, pos, c, z, face_off, w=0.7, h=0.5):
    s = 1 if face_off > 0 else -1; m = MB([F['steel_charcoal'], F['corrugated']])
    m.use(0, (0.1, 0.1, 0.11, 1)); m.box(0, 0, 0, w, 0.06, h, bevel=0.008)
    m.use(1)
    for k in range(7): m.box(0, 0.02 * s, -h / 2 + 0.07 + k * (h - 0.14) / 6, w - 0.1, 0.02, 0.022, rz=0.0)
    o = m.finish(name, coll)
    if axis == 'x': o.location = (LX(c), LY(pos + face_off + s * 0.03), z)
    else: o.location = (LX(pos + face_off + s * 0.03), LY(c), z); o.rotation_euler = (0, 0, math.pi / 2)
    return o

def conduit(F, coll, name, axis, pos, a0, a1, z, face_off, r=0.022, rgba=(0.6, 0.6, 0.62, 1)):
    s = 1 if face_off > 0 else -1
    m = MB([F['steel_charcoal']]); m.use(0, rgba)
    L_ = a1 - a0
    m.cyl_h(0, 0, 0, L_, r, seg=8)
    for k in range(int(L_ / 0.9) + 1): m.box(-L_ / 2 + k * 0.9, 0, -0.01, 0.04, 0.05 + 0.02, 0.012 + 0.02)
    o = m.finish(name, coll)
    if axis == 'x': o.location = (LX((a0 + a1) / 2), LY(pos + face_off + s * 0.04), z)
    else: o.location = (LX(pos + face_off + s * 0.04), LY((a0 + a1) / 2), z); o.rotation_euler = (0, 0, math.pi / 2)
    return o

def jbox(F, coll, name, axis, pos, c, z, face_off, w=0.28, h=0.34, rgba=(0.55, 0.57, 0.6, 1)):
    s = 1 if face_off > 0 else -1
    if axis == 'x': return box(name, c - w / 2, c + w / 2, pos + face_off, pos + face_off + s * 0.12, z, z + h, F['plastic'], coll, rgba=rgba, bev=0.01)
    return box(name, pos + face_off, pos + face_off + s * 0.12, c - w / 2, c + w / 2, z, z + h, F['plastic'], coll, rgba=rgba, bev=0.01)

def stain(F, coll, name, x, y, rx, ry, rgba, seed):
    bm = bmesh.new(); res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0); rnd = random.Random(seed)
    for v in res['verts']:
        k = 1 + rnd.uniform(-0.25, 0.25); v.co = Vector((LX(x) + v.co.x * rx * k, LY(y) + v.co.y * ry * k, 0.001 + max(v.co.z, 0) * 0.004))
    return mesh_obj(name, bm, F['props'], coll, rgba)

def build_dressing(F, C):
    caf, hall, yard, sh = C['CAFETERIA'], C['HALL'], C['YARD'], C['SHARED']
    # ---------------- interior panels
    panels(F, caf, 'caf_S_in', 'x', -80.0, -8.0, 26.0, 1.3, 4.6, +0.15, excl=[(6.5, 9.5)], mat='plaster', rgba=(0.80, 0.73, 0.62, 1) if False else None)
    panels(F, caf, 'caf_E_in', 'y', 26.0, -80.0, -60.0, 1.3, 4.6, -0.15, excl=[(-71.5, -68.5)])
    panels(F, caf, 'caf_W_in', 'y', -8.0, -80.0, -60.0, 1.3, 2.6, +0.15, excl=[(-71.7, -68.3)])
    panels(F, caf, 'caf_N_in', 'x', -60.0, -8.0, 26.0, 1.3, 4.6, -0.15, excl=[(4.5, 11.5)])
    panels(F, hall, 'hall_S_in', 'x', -60.0, -4.0, 32.0, 1.3, 5.7, +0.15, excl=[(4.5, 11.5)])
    panels(F, hall, 'hall_N_in', 'x', -48.0, -4.0, 32.0, 1.3, 4.2, -0.15, excl=[(5.5, 10.5)])
    panels(F, hall, 'hall_W_in', 'y', -4.0, -60.0, -48.0, 1.3, 5.7, +0.15, excl=[(-55.5, -52.5)])
    panels(F, hall, 'hall_E_in', 'y', 32.0, -60.0, -48.0, 1.3, 5.7, -0.15, excl=[(-55.5, -52.5)])
    # ---------------- exterior facade onto the yard (cafeteria west wall) and hall ends / north
    panels(F, yard, 'caf_W_out', 'y', -8.0, -80.0, -60.0, 0.0, 2.6, -0.15, excl=[(-71.7, -68.3)], mat='concrete_slab')
    panels(F, yard, 'caf_W_out_hi', 'y', -8.0, -80.0, -60.0, 4.5, 5.0, -0.15, excl=[], mat='steel_charcoal')
    panels(F, sh, 'hall_N_out', 'x', -48.0, -4.0, 32.0, 0.0, 5.7, +0.15, excl=[(5.5, 10.5)], mat='plaster')
    panels(F, sh, 'hall_W_out', 'y', -4.0, -60.0, -48.0, 0.0, 5.7, -0.15, excl=[(-55.5, -52.5)], mat='plaster')
    # ---------------- vents, conduits, junction boxes
    for i, c in enumerate((-4.0, 12.5, 20.0)): vent(F, caf, f'caf_S_vent{i}', 'x', -80.0, c, 3.5, +0.15)
    for i, c in enumerate((-70.0 - 6.5, -63.0)): vent(F, caf, f'caf_E_vent{i}', 'y', 26.0, c, 3.4, -0.15)
    for i, c in enumerate((2.0, 14.0, 26.0)): vent(F, hall, f'hall_S_vent{i}', 'x', -60.0, c, 4.6, +0.15, w=0.9, h=0.6)
    conduit(F, caf, 'caf_S_conduit_a', 'x', -80.0, -7.5, 25.5, 3.1, +0.15); conduit(F, caf, 'caf_E_conduit', 'y', 26.0, -79.5, -60.5, 3.0, -0.15, rgba=(0.7, 0.45, 0.1, 1))
    conduit(F, hall, 'hall_S_conduit', 'x', -60.0, -3.5, 31.5, 3.6, +0.15); conduit(F, hall, 'hall_S_conduit_b', 'x', -60.0, -3.5, 31.5, 3.75, +0.15, rgba=(0.7, 0.2, 0.12, 1))
    conduit(F, hall, 'hall_W_conduit', 'y', -4.0, -59.5, -48.5, 3.4, +0.15); conduit(F, hall, 'hall_E_conduit', 'y', 32.0, -59.5, -48.5, 3.4, -0.15)
    for i, c in enumerate((-2.0, 7.0, 16.0, 22.5)): jbox(F, caf, f'caf_S_jbox{i}', 'x', -80.0, c, 1.4, +0.15)
    for i, c in enumerate((0.0, 12.0, 26.0)): jbox(F, hall, f'hall_S_jbox{i}', 'x', -60.0, c, 1.5, +0.15)
    # yard facade fittings: downpipes, electrical cabinets, hose reel, wall lamps
    for i, y in enumerate((-79.0, -73.4, -66.6, -61.0)):
        cylinder(f'caf_W_downpipe{i}', -8.3, y, 0.07, 0.0, 5.0, F['steel_charcoal'], yard, rgba=None, verts=10)
        box(f'caf_W_downpipe_clip{i}', -8.36, -8.14, y - 0.1, y + 0.1, 3.8, 3.9, F['steel_charcoal'], yard)
    for i, y in enumerate((-78.0, -62.5)):
        box(f'yard_cabinet{i}', -8.55, -8.15, y - 0.5, y + 0.5, 0.0, 1.9, F['steel_accent'], yard, bev=0.02)
        box(f'yard_cabinet_door{i}', -8.575, -8.55, y - 0.44, y + 0.44, 0.1, 1.8, F['steel_accent'], yard, bev=0.012)
        box(f'yard_cabinet_hazard{i}', -8.58, -8.575, y - 0.18, y + 0.18, 1.5, 1.7, F['signage'], yard, rgba=(0.95, 0.75, 0.05, 1))
    for i, y in enumerate((-75.0, -65.0)): box(f'yard_wall_lamp{i}', -8.5, -8.15, y - 0.2, y + 0.2, 3.2, 3.4, F['emissive'], yard, rgba=(1, 0.85, 0.6, 1), bev=0.03)
    # ---------------- signs
    S = lambda *a, **k: wall_sign(F, *a, **k)
    S(yard, 'sign_cafeteria', 'CAFETERIA  /  STAFF ARRIVAL', -8.2, -70.0, 3.2, 'W', w=3.4, h=0.55, plate=(0.8, 0.4, 0.07, 1), ink='signage', size=0.24, wall_plane=-8.15)
    S(yard, 'sign_mine', 'MINE ENTRANCE', -48.65, -70.0, 4.5, 'E', w=3.0, h=0.5, plate=(0.95, 0.75, 0.05, 1), ink='signage', size=0.22, wall_plane=None, register=False)
    S(yard, 'sign_carts', 'CARTS HAVE PRIORITY', -22.2, -70.0, 2.6, 'S', w=2.8, h=0.4, plate=(0.95, 0.75, 0.05, 1), ink='signage', size=0.17, register=False) if False else None
    S(yard, 'sign_refinery_gate', 'REFINERY  FREIGHT', RAIL_X if False else -22.2, -60.28, 3.05, 'S', w=2.6, h=0.35, plate=(0.08, 0.08, 0.09, 1), size=0.16, wall_plane=-60.265)
    S(yard, 'sign_evac', 'EVACUATION  GATE', -28.0, -83.78, 2.6, 'N', w=2.4, h=0.35, plate=(0.1, 0.55, 0.25, 1), ink='signage', size=0.15, wall_plane=-83.8)
    S(yard, 'sign_cooling', 'COOLING PLANT >>', -46.0, -59.7, 2.8, 'S', w=1.9, h=0.32, plate=(0.08, 0.08, 0.09, 1), size=0.13, wall_plane=-59.7, register=False)
    S(yard, 'sign_speed', '5', -36.0, -66.0, 2.3, 'N', w=0.5, h=0.5, plate=(0.95, 0.95, 0.9, 1), ink='signage', size=0.35, register=False) if False else None
    S(caf, 'sign_wash', 'WASH HANDS', 7.0, -79.82, 2.6, 'N', w=1.1, h=0.3, plate=(0.12, 0.35, 0.55, 1), ink='signage', size=0.11, wall_plane=-79.85)
    S(caf, 'sign_staff', 'STAFF ONLY', 14.15, -62.0, 2.0, 'W', w=0.9, h=0.3, plate=(0.8, 0.12, 0.1, 1), ink='signage', size=0.1, wall_plane=14.0) if False else None
    S(caf, 'sign_medical', 'MEDICAL >>', 25.82, -68.6, 3.3, 'W', w=1.5, h=0.38, plate=(0.8, 0.1, 0.1, 1), ink='signage', size=0.15, wall_plane=25.85)
    S(caf, 'sign_hall', 'HALL / ROUTES  ^', 8.0, -60.18, 3.75, 'S', w=3.0, h=0.4, plate=(0.08, 0.08, 0.09, 1), size=0.17, wall_plane=-60.15)
    S(hall, 'sign_hall_refinery', 'REFINERY  <<', 0.0, -59.82, 3.4, 'N', w=1.9, h=0.36, plate=(0.08, 0.08, 0.09, 1), size=0.15, wall_plane=-59.85)
    S(hall, 'sign_hall_reactor', 'REACTOR  ^', 8.0, -59.82, 4.4, 'N', w=1.9, h=0.36, plate=(0.08, 0.08, 0.09, 1), size=0.15, wall_plane=-59.85) if False else None
    S(hall, 'sign_hall_dock', 'DOCK  >>', 28.0, -59.82, 3.4, 'N', w=1.6, h=0.36, plate=(0.08, 0.08, 0.09, 1), size=0.15, wall_plane=-59.85)
    S(hall, 'sign_hard_hats', 'HARD HATS BEYOND THIS POINT', 13.5, -48.18, 3.9, 'S', w=3.4, h=0.34, plate=(0.95, 0.75, 0.05, 1), ink='signage', size=0.14, wall_plane=-48.15)
    S(hall, 'sign_no_running', 'NO RUNNING', 31.82, -57.6, 2.2, 'W', w=1.1, h=0.3, plate=(0.8, 0.12, 0.1, 1), ink='signage', size=0.11, wall_plane=31.85)
    S(hall, 'sign_route_a', 'ROUTE A', -3.82, -57.6, 2.2, 'E', w=1.0, h=0.3, plate=(0.1, 0.55, 0.25, 1), ink='signage', size=0.12, wall_plane=-3.85)
    # ---------------- floor wear and joints
    for x in range(0, 33, 4): box(f'hall_joint_x{x}', x - 0.008, x + 0.008, -59.8, -48.2, 0.0, 0.003, F['props'], hall, rgba=(0.05, 0.05, 0.05, 1))
    for y in (-56.0, -52.0): box(f'hall_joint_y{y}', -3.8, 31.8, y - 0.008, y + 0.008, 0.0, 0.003, F['props'], hall, rgba=(0.05, 0.05, 0.05, 1))
    rng = random.Random(13)
    for i in range(14): stain(F, hall, f'hall_stain{i}', rng.uniform(-2, 30), rng.uniform(-59, -49), rng.uniform(0.4, 1.4), rng.uniform(0.3, 0.9), (0.22 + rng.uniform(0, 0.05),) * 3 + (1,), i)
    for i in range(10): stain(F, yard, f'yard_stain{i}', rng.uniform(-46, -10), rng.uniform(-83, -61), rng.uniform(0.4, 1.6), rng.uniform(0.3, 1.0), (0.17, 0.165, 0.16, 1), 30 + i)
    # painted lane edges along the mine axis and a hatched crossing at the rail
    for k in range(20):
        for yy in (-71.25, -68.75): box(f'lane_{k}_{yy}', -46.0 + k * 2.0, -45.0 + k * 2.0, yy - 0.06, yy + 0.06, 0.0, 0.004, F['signage'], yard, rgba=(0.95, 0.75, 0.05, 1))
    for k in range(10): box(f'rail_crossing_{k}', RAIL_X_ - 1.2 + k * 0.25 if False else -23.4 + k * 0.25, -23.4 + k * 0.25 + 0.12, -71.0, -66.0, 0.0, 0.004, F['signage'], yard, rgba=(0.95, 0.75, 0.05, 1) if k % 2 == 0 else (0.04, 0.04, 0.04, 1))
