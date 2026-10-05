"""Hall (junction), colonnade, spine and trunk stubs."""
from fe_common import *
from fe_props import *
from fe_yard import inst

HALL = (-4.0, 32.0, -60.0, -48.0)

def text_obj(name, text, x, y, z, rot, size, mat, coll, extrude=0.004, align='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = text; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); o.data.materials.append(mat); coll.objects.link(o); o.rotation_euler = rot; o.location = (LX(x), LY(y), z); return o

def hazard_stripes(F, coll, name, x0, x1, y0, y1, z0, z1, vertical=True, n=8):
    # alternating yellow / black bands on a jamb
    for k in range(n):
        a = z0 + (z1 - z0) * k / n; b = z0 + (z1 - z0) * (k + 1) / n
        box(f'{name}_haz{k}', x0, x1, y0, y1, a, b, F['signage'], coll, rgba=(0.95, 0.75, 0.05, 1) if k % 2 == 0 else (0.04, 0.04, 0.04, 1))

def blast_door(F, C):
    hall = C['HALL']
    cx, cy = 8.0, -48.0
    # frame jambs and header with hazard stripes, amber beacon lights, reactor sign
    for s in (-1, 1):
        box(f'blast_jamb_{s}', cx + s * 1.8 - (0.0 if s > 0 else 0.35), cx + s * 1.8 + (0.35 if s > 0 else 0.0), cy - 0.45, cy + 0.2, 0, 3.4, F['steel_charcoal'], hall, bev=0.03)
        hazard_stripes(F, hall, f'blast_jamb_{s}', cx + s * 1.8 - (0.0 if s > 0 else 0.35) + 0.02, cx + s * 1.8 + (0.35 if s > 0 else 0.0) - 0.02, cy - 0.47, cy - 0.45, 0.0, 3.2)
    box('blast_header', cx - 2.15, cx + 2.15, cy - 0.5, cy + 0.2, 3.2, 3.9, F['steel_charcoal'], hall, bev=0.04)
    box('blast_header_stripe', cx - 2.15, cx + 2.15, cy - 0.52, cy - 0.5, 3.2, 3.35, F['steel_accent'], hall, bev=0.01)
    for i, (xx, col) in enumerate(((cx - 1.5, (1.0, 0.45, 0.05, 1)), (cx + 1.5, (1.0, 0.45, 0.05, 1)), (cx, (0.1, 0.9, 0.3, 1)))):
        box(f'blast_beacon_{i}', xx - 0.14, xx + 0.14, cy - 0.7, cy - 0.5, 3.45, 3.75, F['emissive'], hall, rgba=col, bev=0.02)
    sp = box('blast_sign', cx - 1.4, cx + 1.4, cy - 0.53, cy - 0.5, 3.4, 3.8, F['signage'], hall, rgba=(0.1, 0.1, 0.1, 1), bev=0.01); wall_item(sp, 'y', cy - 0.5, -1)
    text_obj('blast_sign_text', 'REACTOR', cx, cy - 0.54, 3.6, (math.pi / 2, 0, 0), 0.26, F['emissive'], hall)
    # leaves, mostly retracted into pockets on the hall side
    for s in (-1, 1):
        x0 = cx + s * (1.95 if s > 0 else 1.95 + 1.8); lx0 = (cx + s * 2.1) if s > 0 else (cx + s * 2.1 - 1.8)
        m = MB([F['steel_charcoal'], F['steel_accent'], F['glass']])
        m.use(0, (0.1, 0.1, 0.11, 1)); m.box(0, 0, 1.6, 1.8, 0.28, 3.2, bevel=0.025)
        m.use(1)
        for k in range(5): m.box(0, -0.15, 0.4 + k * 0.62, 1.6, 0.03, 0.12, bevel=0.01)
        m.use(2); m.cyl_h(0, -0.16, 2.5, 0.02, 0.28, seg=18, rz=math.pi / 2)
        m.use(0, (0.14, 0.14, 0.15, 1))
        for k in range(8): m.cyl(-0.7 + (k % 4) * 0.47, -0.16, 0.2 + (k // 4) * 2.7, 0.2 + (k // 4) * 2.7 + 0.03, 0.035, seg=8)
        o = m.finish(f'blast_leaf_{s}', hall); o.location = (LX((cx + s * 3.0)), LY(cy - 0.5), 0.0); o['support'] = 'floor'
    box('blast_floor_track', cx - 4.8, cx + 4.8, cy - 0.65, cy - 0.5, 0.0, 0.02, F['steel_charcoal'], hall, bev=0.005)

def end_door(F, C, name, x, y, axis_sign, sign_text):
    hall = C['HALL']
    # a closed double steel door in the end wall (leaves flush), kick plates, vision panels, push bars, sign above
    for s in (-1, 1):
        yy = y + s * 0.6
        m = MB([F['steel_charcoal'], F['glass'], F['steel_accent']])
        m.use(0, (0.12, 0.13, 0.14, 1)); m.box(0, 0, 1.3, 0.06, 1.15, 2.6, bevel=0.01)
        m.use(1); m.box(0.032, 0, 1.75, 0.01, 0.5, 0.6)
        m.use(2); m.box(0.04, 0, 0.18, 0.02, 1.1, 0.3, bevel=0.005); m.box(0.05, -0.35 * s, 1.0, 0.03, 0.04, 0.6, bevel=0.005)
        o = m.finish(f'{name}_leaf_{s}', hall); o.location = (LX(x), LY(yy), 0.0); o.rotation_euler = (0, 0, 0 if axis_sign > 0 else math.pi); o['support'] = 'floor'
    sp = box(f'{name}_sign', x - 0.05, x + 0.05, y - 1.2, y + 1.2, 2.9, 3.35, F['signage'], hall, rgba=(0.08, 0.08, 0.09, 1), bev=0.008)
    wall_item(sp, 'x', x - 0.05 * axis_sign * -1 if False else x, +1 if axis_sign > 0 else -1) if False else None
    text_obj(f'{name}_sign_text', sign_text, x + (-0.06 if axis_sign > 0 else 0.06), y, 3.12, (math.pi / 2, 0, -math.pi / 2 if axis_sign > 0 else math.pi / 2), 0.2, F['emissive'], hall)

def gantry_landing(F, C):
    hall = C['HALL']
    x0, x1, y0, y1, z = 3.0, 13.0, -50.2, -48.2, 4.2
    # grating deck
    m = MB([F['steel_charcoal'], F['steel_accent']])
    m.use(0, (0.12, 0.12, 0.13, 1))
    for k in range(int((x1 - x0) / 0.09)): m.box(LX(x0 + 0.05 + k * 0.09), LY((y0 + y1) / 2), z, 0.012, y1 - y0, 0.04)
    for k in range(5): m.box(LX((x0 + x1) / 2), LY(y0 + 0.2 + k * 0.4), z - 0.03, x1 - x0, 0.04, 0.05, bevel=0.005)
    m.box(LX((x0 + x1) / 2), LY(y0), z - 0.1, x1 - x0, 0.08, 0.16, bevel=0.01); m.box(LX((x0 + x1) / 2), LY(y1), z - 0.1, x1 - x0, 0.08, 0.16, bevel=0.01)
    for xx in (x0, x1): m.box(LX(xx), LY((y0 + y1) / 2), z - 2.1, 0.2, 0.2, 4.2, bevel=0.015); m.box(LX(xx), LY((y0 + y1) / 2), 0.02, 0.5, 0.5, 0.04, bevel=0.01)
    # bracing
    m.use(1)
    # handrails along the open (south) side and ends
    for k in range(11): m.box(LX(x0 + k * 1.0), LY(y0), z + 0.55, 0.05, 0.05, 1.1, bevel=0.006)
    m.box(LX((x0 + x1) / 2), LY(y0), z + 1.08, x1 - x0, 0.05, 0.05); m.box(LX((x0 + x1) / 2), LY(y0), z + 0.6, x1 - x0, 0.04, 0.04); m.box(LX((x0 + x1) / 2), LY(y0), z + 0.1, x1 - x0, 0.015, 0.1)
    for xx in (x1,): m.box(LX(xx), LY((y0 + y1) / 2), z + 1.08, 0.05, y1 - y0, 0.05); m.box(LX(xx), LY((y0 + y1) / 2), z + 0.6, 0.04, y1 - y0, 0.04)
    o = m.finish('gantry_landing', hall)
    # stair along the north wall from the west end up to the landing
    steps = 21; rise = z / steps; run = 0.27
    m = MB([F['steel_charcoal'], F['steel_accent']]); m.use(0, (0.12, 0.12, 0.13, 1))
    for k in range(steps):
        xs = x0 - (steps - k) * run
        m.box(LX(xs + run / 2), LY(-49.35), rise * (k + 1) - 0.02, run, 1.1, 0.04, bevel=0.004)
        for j in range(6): m.box(LX(xs + run / 2), LY(-49.35 - 0.5 + j * 0.2), rise * (k + 1) - 0.005, run - 0.02, 0.012, 0.02)
    for sy in (-0.57, 0.57):
        m.box(LX(x0 - steps * run / 2), LY(-49.35 + sy), z / 2 - 0.1, steps * run, 0.05, 0.22, rz=0.0)
    m.use(1)
    for k in range(0, steps, 2):
        xs = x0 - (steps - k) * run + run / 2
        m.box(LX(xs), LY(-49.92), rise * (k + 1) + 0.5, 0.04, 0.04, 1.0, bevel=0.005)
    ang = math.atan2(z, steps * run)
    m.box(LX(x0 - steps * run / 2), LY(-49.92), z / 2 + 1.0, steps * run / math.cos(ang) , 0.04, 0.04) if False else None
    o2 = m.finish('gantry_stair', hall)
    box('gantry_sign', 6.0, 10.0, -50.22, -50.18, 4.5, 5.0, F['signage'], hall, rgba=(0.95, 0.75, 0.05, 1), bev=0.006)
    text_obj('gantry_sign_text', 'GANTRY ACCESS', 8.0, -50.23, 4.75, (math.pi / 2, 0, 0), 0.2, F['signage'], hall)

def desk_and_safety(F, C):
    hall = C['HALL']; rng = random.Random(8)
    # shift desk against the south wall
    m = MB([F['laminate'], F['steel_charcoal'], F['plastic'], F['emissive'], F['signage']])
    m.use(1, (0.1, 0.11, 0.12, 1)); m.box(0, 0, 0.5, 3.0, 1.0, 1.0, bevel=0.0)
    for k in range(5): m.use(1, (0.16, 0.17, 0.18, 1)); m.box(-1.2 + k * 0.6, 0.51, 0.5, 0.56, 0.03, 0.82, bevel=0.01)
    m.use(0, (0.72, 0.68, 0.6, 1)); m.box(0, 0.05, 1.03, 3.1, 1.1, 0.06, bevel=0.01); m.box(0, 0.7, 1.12, 3.1, 0.18, 0.2, bevel=0.01)
    m.use(2, (0.08, 0.08, 0.09, 1))
    for k, dx in enumerate((-0.9, 0.0, 0.9)):
        m.box(dx, 0.1, 1.12, 0.58, 0.04, 0.38, bevel=0.01); m.cyl(dx, 0.1, 1.06, 1.12, 0.05, seg=10)
        m.use(3, (0.15, 0.35, 0.5, 1) if k != 1 else (0.2, 0.5, 0.3, 1)); m.box(dx, 0.075, 1.14, 0.54, 0.01, 0.33); m.use(2, (0.08, 0.08, 0.09, 1))
    m.use(2, (0.2, 0.2, 0.22, 1)); m.box(1.2, -0.1, 1.08, 0.2, 0.26, 0.06, bevel=0.01); m.use(4, (0.9, 0.9, 0.85, 1)); m.box(-1.2, -0.25, 1.07, 0.3, 0.2, 0.012)
    m.use(1, (0.1, 0.1, 0.11, 1)); m.cyl(0.5, 0.25, 1.06, 1.35, 0.012, seg=6); m.use(3, (1.0, 0.9, 0.7, 1)); m.box(0.5, 0.25, 1.38, 0.18, 0.1, 0.06, bevel=0.01)
    o = m.finish('shift_desk', hall); o.location = (LX(22.5), LY(-59.3), 0.0); o['support'] = 'floor'
    # desk chair
    ch = p_chair_hall(F, collection('PROTOTYPES')); inst(ch, 'shift_chair', 22.5, -58.1, hall, rz=math.pi + 0.2, z=-0.035)
    # schedule board on the south wall above the desk
    sb = box('schedule_board', 20.0, 25.0, -59.88, -59.84, 1.7, 3.0, F['emissive'], hall, rgba=(0.08, 0.14, 0.2, 1), bev=0.008); wall_item(sb, 'y', -59.85, +1)
    for k in range(9): box(f'schedule_row_{k}', 20.2, 24.8 - (k % 3) * 0.7, -59.84, -59.835, 1.85 + k * 0.12, 1.92 + k * 0.12, F['emissive'], hall, rgba=(0.5, 0.75, 0.9, 1) if k % 3 else (0.9, 0.7, 0.2, 1))
    # safety station on the north wall: eyewash, first aid, fire cabinet, defibrillator, PPE return
    nx = -48.2 + 0.15
    def cab(name, x0, x1, z0, z1, rgba, extra=None):
        b = box(name, x0, x1, -48.45, -48.2, z0, z1, F['plastic'], hall, rgba=rgba, bev=0.015); wall_item(b, 'y', -48.2, -1); return b
    cab('eyewash_station', 16.0, 17.1, 0.9, 1.5, (0.15, 0.6, 0.25, 1)); box('eyewash_bowl', 16.15, 16.95, -48.9, -48.45, 0.95, 1.05, F['steel_charcoal'], hall, bev=0.02)
    box('eyewash_sign', 16.1, 17.0, -48.5, -48.46, 1.8, 2.4, F['signage'], hall, rgba=(0.15, 0.6, 0.25, 1), bev=0.006)
    cab('first_aid_cabinet', 17.6, 18.5, 1.2, 1.9, (0.92, 0.92, 0.9, 1)); box('first_aid_cross_v', 17.97, 18.13, -48.47, -48.45, 1.35, 1.75, F['signage'], hall, rgba=(0.8, 0.1, 0.1, 1)); box('first_aid_cross_h', 17.77, 18.33, -48.47, -48.45, 1.47, 1.63, F['signage'], hall, rgba=(0.8, 0.1, 0.1, 1))
    cab('fire_cabinet', 19.0, 19.9, 0.7, 1.9, (0.75, 0.12, 0.1, 1)); cyl_ = cylinder('fire_extinguisher', 19.45, -48.8, 0.14, 0.75, 1.5, F['plastic'], hall, rgba=(0.8, 0.1, 0.1, 1), verts=14)
    cab('defib_cabinet', 20.3, 21.0, 1.3, 1.8, (0.9, 0.5, 0.1, 1)); box('defib_light', 20.55, 20.75, -48.47, -48.45, 1.62, 1.72, F['emissive'], hall, rgba=(0.2, 0.9, 0.3, 1))
    m = MB([F['steel_charcoal'], F['plastic'], F['props']]); m.use(0, (0.1, 0.1, 0.11, 1))
    for sx in (-1.2, 1.2): m.box(sx, 0, 1.0, 0.06, 0.5, 2.0)
    m.box(0, -0.2, 2.0, 2.5, 0.06, 0.06); m.box(0, -0.2, 0.9, 2.5, 0.04, 0.04)
    for k in range(6):
        m.use(2, [(0.8, 0.55, 0.1, 1), (0.8, 0.8, 0.8, 1), (0.2, 0.3, 0.5, 1)][k % 3]); m.box(-1.0 + k * 0.4, -0.05, 1.2, 0.3, 0.14, 0.7, bevel=0.03)
        m.use(0); m.cyl(-1.0 + k * 0.4, -0.2, 1.8, 2.0, 0.015, seg=6)
    for k in range(3): m.use(1, (0.15, 0.15, 0.17, 1)); m.box(-0.8 + k * 0.8, 0.25, 0.2, 0.55, 0.4, 0.4, bevel=0.02)
    o = m.finish('ppe_return_rack', hall); o.location = (LX(24.0), LY(-48.55), 0.0); o['support'] = 'floor'
    # status board above the doors
    sb2 = box('status_board', 16.0, 26.0, -48.22, -48.18, 2.2, 3.5, F['emissive'], hall, rgba=(0.06, 0.1, 0.12, 1), bev=0.008); wall_item(sb2, 'y', -48.2, -1)
    for k in range(7): box(f'status_row_{k}', 16.3, 25.7 - (k % 4) * 1.2, -48.23, -48.215, 2.35 + k * 0.16, 2.43 + k * 0.16, F['emissive'], hall, rgba=[(0.2, 0.8, 0.35, 1), (0.9, 0.7, 0.15, 1), (0.2, 0.8, 0.35, 1), (0.85, 0.2, 0.15, 1)][k % 4])
    text_obj('status_title', 'FACILITY STATUS', 21.0, -48.235, 3.38, (math.pi / 2, 0, 0), 0.16, F['emissive'], hall)

def p_chair_hall(F, P):
    m = MB([F['plastic'], F['steel_charcoal']]); m.use(0, (0.1, 0.1, 0.12, 1))
    m.box(0, 0, 0.5, 0.5, 0.5, 0.08, bevel=0.03, seg=2); m.box(0, -0.24, 0.85, 0.46, 0.08, 0.5, bevel=0.03, seg=2)
    m.use(1); m.cyl(0, 0, 0.1, 0.46, 0.03, seg=8)
    for a in range(5): m.box(math.cos(a * 1.2566) * 0.25, math.sin(a * 1.2566) * 0.25, 0.06, 0.4, 0.05, 0.04, rz=a * 1.2566, bevel=0.005)
    return m.finish('proto_chair_hall', P)

def ceiling_services(F, C):
    hall = C['HALL']
    # supply duct, two pipes, cable tray along the north side; light fixtures on the centre line
    box('hall_duct', -3.7, 31.7, -50.0, -49.2, 4.8, 5.4, F['corrugated'], hall, bev=0.02)
    for k in range(9): box(f'hall_duct_flange{k}', -3.7 + k * 4.0, -3.5 + k * 4.0, -50.04, -49.16, 4.76, 5.44, F['steel_charcoal'], hall, bev=0.01)
    for i, (z, rgba) in enumerate(((4.5, (0.75, 0.12, 0.1, 1)), (4.25, (0.8, 0.5, 0.08, 1)))):
        m = MB([F['props']]); m.use(0, rgba); m.cyl_h(LX(14.0), LY(-48.7), z, 35.4, 0.07, seg=14)
        o = m.finish(f'hall_pipe_{i}', hall)
        for k in range(8): box(f'hall_pipe_clamp_{i}_{k}', -3.0 + k * 4.5, -2.8 + k * 4.5, -48.8, -48.6, z - 0.1, 4.78, F['steel_charcoal'], hall)
    m = MB([F['steel_charcoal']]); m.use(0, (0.14, 0.14, 0.15, 1))
    m.box(LX(14.0), LY(-52.0), 5.5, 35.4, 0.5, 0.05); m.box(LX(14.0), LY(-52.25), 5.55, 35.4, 0.03, 0.12); m.box(LX(14.0), LY(-51.75), 5.55, 35.4, 0.03, 0.12)
    for k in range(70): m.box(LX(-3.4 + k * 0.5), LY(-52.0), 5.52, 0.02, 0.5, 0.02)
    m.finish('hall_cable_tray', hall)
    for i, x in enumerate(range(0, 32, 6)):
        mm = MB([F['steel_charcoal'], F['emissive']]); mm.use(0, (0.1, 0.1, 0.11, 1)); mm.box(0, 0, 0, 0.5, 2.4, 0.12, bevel=0.015); mm.use(1, (0.88, 0.93, 1.0, 1)); mm.box(0, 0, -0.065, 0.36, 2.3, 0.02)
        for sy in (-1.15, 1.15): mm.use(0); mm.box(0, sy, 0.3, 0.02, 0.02, 0.6)
        o = mm.finish(f'hall_light_fixture_{i}', hall); o.location = (LX(x + 0.0), LY(-54.0), 5.55)
    # floor drains
    for i, (x, y) in enumerate(((2.0, -55.0), (14.0, -55.0), (26.0, -55.0))):
        box(f'hall_drain_{i}', x - 0.35, x + 0.35, y - 0.35, y + 0.35, -0.01, 0.003, F['corrugated'], hall, bev=0.004)
        for k in range(8): box(f'hall_drain_slot_{i}_{k}', x - 0.3, x + 0.3, y - 0.3 + k * 0.08, y - 0.3 + k * 0.08 + 0.03, 0.003, 0.005, F['rubber'], hall)
    for k in range(5): pass
    # clerestory glass on the north wall
    n = 6
    for i in range(n):
        xa = -3.0 + i * 5.0
        if xa < 11 and xa + 4.2 > 5.9: continue
        box(f'clerestory_glass_{i}', xa, xa + 4.2, -48.06, -48.04, 4.3, 5.5, F['glass'], hall)
        box(f'clerestory_frame_{i}', xa - 0.05, xa + 4.25, -48.1, -48.0, 4.25, 4.3, F['steel_charcoal'], hall, bev=0.006); box(f'clerestory_frame_t{i}', xa - 0.05, xa + 4.25, -48.1, -48.0, 5.5, 5.55, F['steel_charcoal'], hall, bev=0.006)
        for k in range(4): box(f'clerestory_mull_{i}_{k}', xa + k * 1.4, xa + k * 1.4 + 0.05, -48.1, -48.0, 4.3, 5.5, F['steel_charcoal'], hall)

def build_hall(F, C):
    hall = C['HALL']; P = collection('PROTOTYPES')
    blast_door(F, C)
    end_door(F, C, 'hall_W_door', -4.0, -54.0, -1, 'REFINERY  <<')
    end_door(F, C, 'hall_E_door', 32.0, -54.0, 1, 'DOCK  /  WASTE  >>')
    gantry_landing(F, C); desk_and_safety(F, C); ceiling_services(F, C)
    bench = proto_bench(F, P)
    pass

def build_connectors(F, C):
    sh = C['SHARED']
    # west colonnade to the refinery: floor, roof, posts, kerb wall, lights
    box('colonnade_floor', -18.9, -4.0, -55.5, -52.5, -0.2, 0.0, F['concrete_slab'], sh)
    for i, x in enumerate((-18.4, -14.7, -11.0, -7.3, -4.4)):
        box(f'colonnade_post_{i}', x - 0.12, x + 0.12, -55.6, -55.35, 0, 3.3, F['steel_charcoal'], sh, bev=0.012)
    box('colonnade_beam', -18.9, -4.0, -55.6, -55.3, 3.0, 3.3, F['steel_charcoal'], sh, bev=0.012); box('colonnade_beam_n', -18.9, -4.0, -52.7, -52.4, 3.0, 3.3, F['steel_charcoal'], sh, bev=0.012)
    k = 0; x = -18.9
    while x < -4.0: box(f'colonnade_rafter_{k}', x, x + 0.1, -55.6, -52.4, 3.22, 3.34, F['steel_charcoal'], sh); x += 1.0; k += 1
    box('colonnade_roof', -19.0, -3.9, -55.7, -52.3, 3.34, 3.4, F['corrugated'], sh)
    x = -18.9; k = 0
    while x < -4.0: box(f'colonnade_rib_{k}', x, x + 0.04, -55.7, -52.3, 3.4, 3.46, F['corrugated'], sh); x += 0.5; k += 1
    box('colonnade_kerb', -18.9, -4.0, -52.65, -52.5, 0.0, 1.0, F['concrete_slab'], sh, bev=0.012)
    for i, x in enumerate((-16.5, -12.5, -8.5)): box(f'colonnade_lamp_{i}', x - 0.35, x + 0.35, -54.2, -53.8, 3.2, 3.26, F['emissive'], sh, rgba=(1, 0.9, 0.7, 1), bev=0.01)
    # spine mouth to the reactor: 34 m corridor shown as context, ending in the reactor door
    sp = sh
    for s in (-1, 1):
        box(f'spine_wall_{s}', 8.0 + s * 2.0 - 0.15, 8.0 + s * 2.0 + 0.15, -48.0, -14.4, 0, 4.2, F['plaster'], sp)
        box(f'spine_dado_{s}', 8.0 + s * 1.82 - 0.03 if False else 8.0 + s * 1.84, 8.0 + s * 1.84 + (0.03 * s), -48.0, -14.4, 0, 1.1, F['steel_charcoal'], sp)
    box('spine_roof', 5.85, 10.15, -48.0, -14.4, 4.2, 4.4, F['corrugated'], sp); box('spine_floor', 5.85, 10.15, -48.0, -14.4, -0.2, 0.0, F['concrete_slab'], sp)
    for k in range(10): box(f'spine_beam_{k}', 6.0, 10.0, -46.0 + k * 3.5, -45.8 + k * 3.5, 3.85, 4.2, F['steel_charcoal'], sp, bev=0.01)
    for k in range(10): box(f'spine_light_{k}', 7.4, 8.6, -45.0 + k * 3.5, -44.6 + k * 3.5, 3.82, 3.85, F['emissive'], sp, rgba=(1, 0.9, 0.75, 1))
    for k in range(10):
        for s in (-1, 1): box(f'spine_rib_{s}_{k}', 8.0 + s * 1.84 - 0.1, 8.0 + s * 1.84 + 0.1, -47.0 + k * 3.5, -46.8 + k * 3.5, 1.1, 3.9, F['steel_charcoal'], sp, bev=0.01)
    box('spine_route_line', 7.6, 8.4, -48, -14.4, 0.0, 0.006, F['signage'], sp, rgba=(0.9, 0.7, 0.05, 1))
    box('reactor_door_frame', 6.0, 10.0, -14.55, -14.3, 0, 3.6, F['steel_charcoal'], sp, bev=0.03)
    box('reactor_door', 6.35, 9.65, -14.6, -14.55, 0, 3.3, F['emissive'], sp, rgba=(0.9, 0.12, 0.08, 1), bev=0.01)
    # east trunk threshold stub, 4 m
    for s in (-1, 1): box(f'trunk_wall_{s}', 32.0, 36.0, -54.0 + s * 1.5 - 0.15, -54.0 + s * 1.5 + 0.15, 0, 3.4, F['plaster'], sh)
    box('trunk_roof', 32.0, 36.0, -55.8, -52.2, 3.4, 3.6, F['corrugated'], sh); box('trunk_floor', 32.0, 36.0, -55.6, -52.4, -0.2, 0.0, F['concrete_slab'], sh)
