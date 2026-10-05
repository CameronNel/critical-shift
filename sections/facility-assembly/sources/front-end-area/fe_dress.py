"""Dressing: posters, bulletin boards, extinguishers, first aid, clocks, signs, exterior fittings. Spawn-room idiom, light wear only."""
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_wallart import *
from fe_yard import inst
RAIL_X = -22.2

TEXT_ROT = {'S': (math.pi / 2, 0, 0), 'N': (math.pi / 2, 0, math.pi), 'E': (math.pi / 2, 0, math.pi / 2), 'W': (math.pi / 2, 0, -math.pi / 2)}
NORMAL = {'S': (0, -1), 'N': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

import fe_signs
def _style_for(plate):
    r, g, bl = plate[0], plate[1], plate[2]
    if r > 0.85 and g > 0.6 and bl < 0.2: return 'hazard'
    if r > 0.7 and g < 0.2: return 'staff'
    if g > r and g > bl and g > 0.4: return 'green'
    return 'nav'

def wall_sign(F, coll, name, text, x, y, z, facing, w=1.4, h=0.4, plate=(0.08, 0.08, 0.09, 1), ink='emissive', size=None, wall_plane=None, register=True, ink_rgba=None, sub=None, icon=None, style=None):
    """Baked-texture sign (lettering is painted into the sign atlas; no text objects)."""
    return fe_signs.sign(coll, name, text, x, y, z, facing, w, h, sub=sub, style=style or _style_for(plate), icon=icon)

def put_item(proto, name, coll, facing, c, z, face_off=0.0):
    """Instance a wall prop on the interior face of a wall. facing = direction the prop faces; c = plan coordinate along the wall."""
    return proto, name

def wall_face(wall, c):
    """(x, y) plan point on the interior face; (facing)"""
    return None

# interior faces: (axis along wall, face coordinate, facing)
FACES = {
    'caf_S': ('x', -79.83, 'N'), 'caf_N': ('x', -60.17, 'S'), 'caf_W': ('y', -7.83, 'E'), 'caf_E': ('y', 25.83, 'W'),
    'hall_S': ('x', -59.83, 'N'), 'hall_N': ('y' if False else 'x', -48.17, 'S'), 'hall_W': ('y', -3.83, 'E'), 'hall_E': ('y', 31.83, 'W'),
}

def hang(P_items, coll, key, items):
    axis, face, facing = FACES[key]
    for k, (proto, c, z) in enumerate(items):
        if axis == 'x': x, y = c, face
        else: x, y = face, c
        o = inst(proto, f'{key}_{proto.name[6:]}_{k}', x, y, coll, rz=ROT[facing], z=z, support=None)
        wall_item(o, 'y' if axis == 'x' else 'x', face, +1 if facing in ('N', 'E') else -1)

def build_dressing(F, C, parts=('caf', 'hall', 'yard')):
    caf, hall, yard, sh = C['CAFETERIA'], C['HALL'], C['YARD'], C['SHARED']; P = collection('PROTOTYPES')
    posters = [poster(F, P, v, 0.8, 1.2) for v in range(6)]; posters_l = [poster(F, P, 10 + v, 1.2, 0.8, 'poster_l') for v in range(3)]
    bul = bulletin(F, P); ext = extinguisher(F, P); aid = first_aid(F, P); clk = wall_clock(F, P); sock = socket(F, P)
    # ---------------- cafeteria, interior faces
    hang(P, caf, 'caf_S', [(posters[0], 3.6, 1.4), (posters[1], 4.9, 1.4), (posters_l[0], 10.5, 1.5), (posters_l[1], 13.0, 1.5), (clk, 17.5, 3.55), (aid, 15.2, 1.5), (posters[2], 19.2, 1.5), (posters[3], 21.0, 1.5),
                         (posters_l[2], 23.2, 1.5), (ext, 24.9, 0.75), (sock, 1.4, 0.4), (sock, 5.8, 0.4), (sock, 10.3, 0.4)])
    hang(P, caf, 'caf_W', [(bul, -74.6, 1.25), (posters[4], -72.9, 1.5), (posters[5], -61.9, 1.6), (posters_l[1], -67.2, 1.6), (clk, -62.9, 3.4), (ext, -67.5 - 0.0, 0.75), (sock, -75.6, 0.4), ])
    hang(P, caf, 'caf_N', [(posters[1], -5.2, 1.6), (posters[2], 3.2, 1.6), (aid, 24.0, 1.5), (sock, -2.0, 0.4), (sock, 4.4, 0.4)])
    hang(P, caf, 'caf_E', [(bul, -66.2, 1.3), (posters[3], -75.2, 1.7), (posters[0], -78.6, 1.7), (ext, -63.0, 0.75), (sock, -77.0, 0.4)])
    # ---------------- hall, interior faces
    if 'hall' in parts: hang(P, hall, 'hall_S', [(posters[4], -1.6, 1.6), (posters[5], -0.2, 1.6), (bul, 2.0, 1.3), (ext, 13.3, 0.75), (aid, 14.6, 1.5), (posters_l[1], 20.0, 1.6), (clk, 17.0, 3.8), (posters[1], 28.6, 1.6), (posters[2], 30.0, 1.6)])
    if 'hall' in parts: hang(P, hall, 'hall_N', [(posters[0], -2.6, 1.6), (ext, 1.0 + 0.0, 0.75), (posters[3], 27.0, 1.6), (posters_l[2], 29.2, 1.6), (bul, 4.2 - 0.0, 1.3)]) if False else None
    if 'hall' in parts: hang(P, hall, 'hall_W', [(posters[0], -57.0, 1.6), (posters[3], -50.4, 1.6), (clk, -58.0, 3.9), (ext, -56.3, 0.75)])
    if 'hall' in parts: hang(P, hall, 'hall_E', [(posters[5], -57.0, 1.6), (posters[4], -50.4, 1.6), (ext, -56.3, 0.75), ])
    # ---------------- exterior: control joints, downpipes, cabinets, lamps on the yard-facing wall of the cafeteria
    for y in range(-78, -61, 3):
        if -72.2 < y < -67.8: continue
        box(f'caf_W_joint_{y}', -8.2, -8.19, y - 0.01, y + 0.01, 0.5, 4.8, F['steel_charcoal'], yard)
    for i, y in enumerate((-79.0, -73.4, -66.6, -61.0)):
        cylinder(f'caf_W_downpipe{i}', -8.3, y, 0.07, 0.0, 4.9, F['steel_charcoal'], yard, rgba=None, verts=14)
        box(f'caf_W_downpipe_clip{i}', -8.36, -8.14, y - 0.1, y + 0.1, 3.8, 3.9, F['steel_charcoal'], yard, bev=0.01)
        box(f'caf_W_downpipe_clip2_{i}', -8.36, -8.14, y - 0.1, y + 0.1, 1.8, 1.9, F['steel_charcoal'], yard, bev=0.01)
    for i, y in enumerate((-78.0, -62.5)):
        box(f'yard_cabinet{i}', -8.55, -8.15, y - 0.5, y + 0.5, 0.0, 1.9, F['steel_accent'], yard, bev=0.02)
        box(f'yard_cabinet_door{i}', -8.575, -8.55, y - 0.44, y + 0.44, 0.1, 1.8, F['steel_accent'], yard, bev=0.012)
        box(f'yard_cabinet_hazard{i}', -8.58, -8.575, y - 0.18, y + 0.18, 1.5, 1.7, F['signage'], yard, rgba=(0.95, 0.75, 0.05, 1))
        box(f'yard_cabinet_handle{i}', -8.62, -8.58, y + 0.3, y + 0.34, 0.9, 1.1, F['steel_charcoal'], yard, bev=0.01)
    for i, y in enumerate((-75.0, -65.0)):
        box(f'yard_wall_lamp{i}', -8.5, -8.15, y - 0.2, y + 0.2, 3.2, 3.4, F['emissive'], yard, rgba=(1, 0.9, 0.7, 1), bev=0.03)
        box(f'yard_wall_lamp_hood{i}', -8.56, -8.15, y - 0.24, y + 0.24, 3.4, 3.46, F['steel_charcoal'], yard, bev=0.01)
    # ---------------- signs
    S = lambda *a, **k: wall_sign(F, *a, **k)
    if 'yard' in parts: S(yard, 'sign_mine', 'MINE ENTRANCE', -47.7, -70.0, 4.6, 'E', w=3.0, h=0.5, plate=(0.95, 0.75, 0.05, 1), ink='signage', size=0.22, wall_plane=None, register=False)
    if 'yard' in parts: S(yard, 'sign_refinery_gate', 'REFINERY  FREIGHT', -22.2, -60.28, 3.05, 'S', w=2.6, h=0.35, plate=(0.08, 0.08, 0.09, 1), size=0.16, wall_plane=-60.265)
    if 'yard' in parts: S(yard, 'sign_evac', 'EVACUATION  GATE', -28.0, -83.78, 2.6, 'N', w=2.4, h=0.35, plate=(0.1, 0.55, 0.25, 1), ink='signage', size=0.15, wall_plane=-83.8)
    if 'yard' in parts: S(yard, 'sign_cooling', 'COOLING PLANT >>', -46.0, -59.7, 2.8, 'S', w=1.9, h=0.32, plate=(0.08, 0.08, 0.09, 1), size=0.13, wall_plane=-59.7, register=False)
    if 'hall' in parts: S(hall, 'sign_hall_refinery', 'REFINERY  <<', 0.0, -59.82, 3.4, 'N', w=1.9, h=0.36, plate=(0.08, 0.08, 0.09, 1), size=0.15, wall_plane=-59.85)
    if 'hall' in parts: S(hall, 'sign_hall_dock', 'DOCK  >>', 28.0, -59.82, 3.4, 'N', w=1.6, h=0.36, plate=(0.08, 0.08, 0.09, 1), size=0.15, wall_plane=-59.85)
    if 'hall' in parts: S(hall, 'sign_hard_hats', 'HARD HATS BEYOND THIS POINT', 13.5, -48.18, 3.9, 'S', w=3.4, h=0.34, plate=(0.95, 0.75, 0.05, 1), ink='signage', size=0.14, wall_plane=-48.15)
    if 'hall' in parts: S(hall, 'sign_no_running', 'NO RUNNING', 31.82, -57.6, 2.2, 'W', w=1.1, h=0.3, plate=(0.8, 0.12, 0.1, 1), ink='signage', size=0.11, wall_plane=31.85)
    if 'hall' in parts: S(hall, 'sign_route_a', 'ROUTE A', -3.82, -57.6, 2.2, 'E', w=1.0, h=0.3, plate=(0.1, 0.55, 0.25, 1), ink='signage', size=0.12, wall_plane=-3.85)
    # ---------------- floor markings: hall joints, painted lane edges along the mine axis, rail crossing hatching
    rng = random.Random(13)
    if 'yard' not in parts: return
    for k in range(20):
        for yy in (-71.25, -68.75): box(f'lane_{k}_{yy}', -46.0 + k * 2.0, -45.0 + k * 2.0, yy - 0.06, yy + 0.06, 0.0, 0.004, F['signage'], yard, rgba=(0.9, 0.7, 0.06, 1))
    for k in range(10): box(f'rail_crossing_{k}', -23.4 + k * 0.25, -23.4 + k * 0.25 + 0.12, -71.0, -66.0, 0.0, 0.004, F['signage'], yard, rgba=(0.9, 0.7, 0.06, 1) if k % 2 == 0 else (0.08, 0.08, 0.08, 1))
