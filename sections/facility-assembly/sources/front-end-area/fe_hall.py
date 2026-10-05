"""Hall shell details (junction, colonnade, spine and trunk stubs): blast door, end doors, plant gantry, ceiling services. Contents live in fe_hallops."""
from fe_common import *
from fe_props import *
from fe_yard import inst
from fe_signs import sign
from fe_assets_int import mb, I
from fe_kit import *

HALL = (-4.0, 32.0, -60.0, -48.0)

def hazard_stripes(F, coll, name, x0, x1, y0, y1, z0, z1, vertical=True, n=8):
    for k in range(n):
        a = z0 + (z1 - z0) * k / n; b = z0 + (z1 - z0) * (k + 1) / n
        box(f'{name}_haz{k}', x0, x1, y0, y1, a, b, F['signage'], coll, rgba=(0.95, 0.75, 0.05, 1) if k % 2 == 0 else (0.04, 0.04, 0.04, 1))

def blast_door(F, C):
    """3.6 x 3.2 m blast door in the north wall: jambs and header with hazard stripes, two amber beacons either side of a baked REACTOR SPINE plate, two sliding leaves parked in wall pockets."""
    hall = C['HALL']
    cx, cy = 8.0, -48.0
    for s in (-1, 1):
        box(f'blast_jamb_{s}', cx + s * 1.8 - (0.0 if s > 0 else 0.35), cx + s * 1.8 + (0.35 if s > 0 else 0.0), cy - 0.45, cy + 0.2, 0, 3.4, F['steel_charcoal'], hall, bev=0.03)
        hazard_stripes(F, hall, f'blast_jamb_{s}', cx + s * 1.8 - (0.0 if s > 0 else 0.35) + 0.02, cx + s * 1.8 + (0.35 if s > 0 else 0.0) - 0.02, cy - 0.47, cy - 0.45, 0.0, 3.2)
    box('blast_header', cx - 2.15, cx + 2.15, cy - 0.5, cy + 0.2, 3.2, 3.9, F['steel_charcoal'], hall, bev=0.04)
    box('blast_header_stripe', cx - 2.15, cx + 2.15, cy - 0.52, cy - 0.5, 3.2, 3.35, F['steel_accent'], hall, bev=0.01)
    for i, xx in enumerate((cx - 1.6, cx + 1.6)): box(f'blast_beacon_{i}', xx - 0.14, xx + 0.14, cy - 0.7, cy - 0.5, 3.45, 3.75, F['emissive'], hall, rgba=(1.0, 0.45, 0.05, 1), bev=0.02)
    sign(hall, 'blast_sign', 'BLAST DOOR', cx, cy - 0.52, 3.42, 'S', 2.2, 0.4, sub='Keep clear  -  opens on shift lead', icon='lock', style='staff')
    for s in (-1, 1):
        m = MB([F['steel_charcoal'], F['steel_accent'], F['glass']])
        m.use(0, (0.1, 0.1, 0.11, 1)); m.box(0, 0, 1.6, 1.8, 0.28, 3.2, bevel=0.025)
        m.use(1)
        for k in range(5): m.box(0, -0.15, 0.4 + k * 0.62, 1.6, 0.03, 0.12, bevel=0.01)
        m.use(2); m.cyl_h(0, -0.16, 2.5, 0.02, 0.28, seg=18, rz=math.pi / 2)
        m.use(0, (0.14, 0.14, 0.15, 1))
        for k in range(8): m.cyl(-0.7 + (k % 4) * 0.47, -0.16, 0.2 + (k // 4) * 2.7, 0.2 + (k // 4) * 2.7 + 0.03, 0.035, seg=8)
        o = m.finish(f'blast_leaf_{s}', hall); o.location = (LX((cx + s * 3.0)), LY(cy - 0.5), 0.0); o['support'] = 'floor'
    box('blast_floor_track', cx - 4.8, cx + 4.8, cy - 0.65, cy - 0.5, 0.0, 0.02, F['steel_charcoal'], hall, bev=0.005)

def end_door(F, C, name, x, y, axis_sign):
    """Closed double steel door in an end wall: painted leaves with a glazed vision panel, brushed kick plate, push bar, hinge knuckles and a closer arm on the hall side. Signs are placed by fe_hallops."""
    hall = C['HALL']; P = collection('PROTOTYPES'); blue = (0.16, 0.26, 0.38, 1)
    for s in (-1, 1):
        m = mb(F)
        m.rbox(0, 0, 1.3, 0.06, 1.14, 2.6, 0.012, seg=1, mi=I['paint'], rgba=blue)
        m.rbox(0, 0, 1.78, 0.07, 0.42, 0.62, 0.008, seg=1, mi=I['glass'])
        m.rbox(-0.036, 0, 1.78, 0.012, 0.5, 0.7, 0.004, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.82, 1))
        m.rbox(-0.035, 0, 0.19, 0.012, 1.04, 0.34, 0.004, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.82, 1))
        m.between((-0.075, -0.45, 1.0), (-0.075, 0.45, 1.0), 0.02, seg=8, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.82, 1))
        for sy in (-0.45, 0.45): m.rbox(-0.05, sy, 1.0, 0.04, 0.03, 0.04, 0.004, seg=1, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        for z in (0.4, 1.3, 2.2): m.cylz(-0.0, s * 0.575, z - 0.07, z + 0.07, 0.016, seg=8, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        m.rbox(-0.06, s * 0.3, 2.55, 0.06, 0.5, 0.05, 0.006, seg=1, mi=I['steel_charcoal'], rgba=(0.1, 0.1, 0.11, 1))
        o = m.finish(f'{name}_leaf_{s}', P); o = inst(o, f'{name}_leaf_{s}', x, y + s * 0.6, hall, rz=0 if axis_sign > 0 else math.pi, support='floor')

def gantry(F, C):
    """Plant gantry: a 10 x 2 m grated deck at 4.2 m along the north wall over the blast door, reached by a 21-tread stair rising from the north-west corner. It serves the plant-room hatch and the overhead services."""
    hall = C['HALL']; P = collection('PROTOTYPES')
    x0, x1, y0, y1, z = 3.0, 13.0, -50.2, -48.2, 4.2
    steel = (0.12, 0.12, 0.13, 1); yel = (0.9, 0.7, 0.06, 1)
    m = mb(F)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(int((x1 - x0) / 0.09)): m.rbox(x0 + 0.05 + k * 0.09 - cx, 0, z, 0.012, y1 - y0, 0.035, 0.002, seg=1, mi=I['steel_charcoal'], rgba=steel)
    for k in range(6): m.rbox(0, y0 + 0.2 - cy + k * 0.38, z - 0.03, x1 - x0, 0.04, 0.05, 0.004, seg=1, mi=I['steel_charcoal'], rgba=steel)
    for yy in (y0, y1): m.rbox(0, yy - cy, z - 0.1, x1 - x0, 0.08, 0.16, 0.008, seg=1, mi=I['steel_charcoal'], rgba=steel)
    for xx in (x0, x1):
        m.rbox(xx - cx, 0, z / 2 - 0.02, 0.2, 0.2, z - 0.04, 0.012, seg=1, mi=I['steel_charcoal'], rgba=steel); m.rbox(xx - cx, 0, 0.02, 0.5, 0.5, 0.04, 0.01, seg=1, mi=I['steel_charcoal'], rgba=steel)
        for sg in (-1, 1): m.between((xx - cx, sg * 0.1, 0.2), (xx - cx + (0.7 if xx == x0 else -0.7), sg * 0.9, z - 0.2), 0.02, seg=6, mi=I['steel_charcoal'], rgba=steel) if False else None
    # handrail along the open south edge and the east end; the stair side is open at x0
    for k in range(11): m.rbox(x0 + k * 1.0 - cx, y0 - cy, z + 0.55, 0.05, 0.05, 1.1, 0.006, seg=1, mi=I['steel_accent'], rgba=yel)
    for zz in (z + 1.08, z + 0.6): m.rbox(0, y0 - cy, zz, x1 - x0, 0.05, 0.05, 0.006, seg=1, mi=I['steel_accent'], rgba=yel)
    m.rbox(0, y0 - cy, z + 0.1, x1 - x0, 0.015, 0.1, 0.002, seg=1, mi=I['steel_accent'], rgba=yel)
    for k in range(3): m.rbox(x1 - cx, y0 - cy + k * (y1 - y0) / 2 - (0 if k else 0), z + 0.55, 0.05, 0.05, 1.1, 0.006, seg=1, mi=I['steel_accent'], rgba=yel)
    for zz in (z + 1.08, z + 0.6): m.rbox(x1 - cx, 0, zz, 0.05, y1 - y0, 0.05, 0.006, seg=1, mi=I['steel_accent'], rgba=yel)
    o = m.finish('gantry_landing', P); inst(o, 'gantry_landing', cx, cy, hall, support='overhead')
    # stair: treads, sloped stringers and handrails
    steps = 21; rise = z / steps; run = 0.27; yc = -49.35; xs0 = x0 - steps * run
    ang = math.atan2(z, steps * run); sl = math.hypot(z, steps * run)
    m = mb(F); mx = (xs0 + x0) / 2
    for k in range(steps):
        xs = xs0 + k * run + run / 2
        m.rbox(xs - mx, 0, rise * (k + 1) - 0.02, run, 1.1, 0.04, 0.004, seg=1, mi=I['steel_charcoal'], rgba=steel)
        for j in range(6): m.rbox(xs - mx, -0.5 + j * 0.2, rise * (k + 1) + 0.002, run - 0.03, 0.012, 0.012, 0.002, seg=1, mi=I['steel_brushed'], rgba=(0.8, 0.8, 0.82, 1))
    for sy in (-0.57, 0.57):
        m.rbox(0, sy, z / 2 - 0.12, sl, 0.05, 0.24, 0.006, rot=(0, -ang, 0), seg=1, mi=I['steel_charcoal'], rgba=steel)
    for k in range(0, steps, 2):
        xs = xs0 + k * run + run / 2; zt = rise * (k + 1)
        m.rbox(xs - mx, -0.57, zt + 0.5, 0.04, 0.04, 1.0, 0.004, seg=1, mi=I['steel_accent'], rgba=yel)
    m.between((xs0 + run / 2 - mx, -0.57, rise + 1.0), (x0 - mx, -0.57, z + 1.0), 0.022, seg=8, mi=I['steel_accent'], rgba=yel)
    m.between((xs0 + run / 2 - mx, 0.57, rise + 0.95), (x0 - mx, 0.57, z + 0.95), 0.02, seg=8, mi=I['steel_accent'], rgba=yel)   # wall-side rail
    o2 = m.finish('gantry_stair', P); inst(o2, 'gantry_stair', mx, yc, hall, support='stack')
    sign(hall, 'gantry_sign', 'PLANT ACCESS', 8.0, y0 - 0.05, 4.6, 'S', 2.4, 0.45, sub='Authorised staff only', icon='bolt', style='hazard')

def plant_door(F, C):
    """Closed plant-room hatch in the north wall, reached from the gantry deck."""
    hall = C['HALL']; x0, x1, z0, z1 = 10.5, 11.7, 4.3, 5.7
    box('plant_door_frame', x0 - 0.08, x1 + 0.08, -48.2, -48.12, z0 - 0.08, z1 + 0.08, F['steel_charcoal'], hall, bev=0.01)
    box('plant_door_leaf', x0, x1, -48.28, -48.2, z0, z1, F['steel_painted'], hall, rgba=(0.55, 0.1, 0.08, 1), bev=0.012)
    box('plant_door_handle', x1 - 0.2, x1 - 0.1, -48.34, -48.28, 4.95, 5.05, F['steel_brushed'], hall, bev=0.01)
    box('plant_door_kick', x0 + 0.04, x1 - 0.04, -48.3, -48.28, z0 + 0.04, z0 + 0.2, F['steel_brushed'], hall)
    sign(hall, 'plant_door_sign', 'PLANT ROOM', (x0 + x1) / 2, -48.3, z1 + 0.04, 'S', 1.1, 0.14, style='hazard') if False else None

def ceiling_services(F, C):
    """Overhead services at working heights, all clear of the gantry (north strip) and hanging signs:
    supply duct and PA along the south wall, sprinkler main down the middle with heads, cable tray with cables over the north zone, two light rows."""
    hall = C['HALL']
    box('hall_duct', -3.7, 31.7, -59.2, -58.4, 4.5, 5.2, F['corrugated'], hall, bev=0.02)
    for k in range(10): box(f'hall_duct_flange{k}', -3.7 + k * 4.0, -3.5 + k * 4.0, -59.24, -58.36, 4.46, 5.24, F['steel_charcoal'], hall, bev=0.01)
    for k in range(9): box(f'hall_duct_hanger_{k}', -2.0 + k * 4.0, -1.96 + k * 4.0, -59.0, -58.96, 5.2, 5.5, F['steel_charcoal'], hall)
    m = mb(F)
    m.between((-3.7, -53.4, 5.06), (31.7, -53.4, 5.06), 0.04, seg=12, mi=I['paint'], rgba=(0.75, 0.1, 0.07, 1))
    for k in range(10): m.cylz(-2.2 + k * 3.7, -53.4, 4.98, 5.06, 0.016, seg=8, mi=I['paint'], rgba=(0.75, 0.1, 0.07, 1))
    for k in range(9): m.rbox(-3.0 + k * 4.0, -53.4, 5.3, 0.04, 0.04, 0.45, 0.004, seg=1, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    o = m.finish('hall_sprinkler_main', collection('PROTOTYPES')); inst(o, 'hall_sprinkler_main', 0.0, 0.0, hall, support='hanging')
    m = mb(F)
    m.rbox(14.0, -51.4, 4.95, 35.4, 0.45, 0.04, 0.004, seg=1, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for yy in (-51.62, -51.18): m.rbox(14.0, yy, 5.02, 35.4, 0.03, 0.1, 0.004, seg=1, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for k in range(70): m.rbox(-3.4 + k * 0.5, -51.4, 4.97, 0.02, 0.45, 0.02, 0.002, seg=1, mi=I['steel_charcoal'], rgba=(0.14, 0.14, 0.15, 1))
    for j, c in enumerate(((0.05, 0.05, 0.06, 1), (0.75, 0.1, 0.07, 1), (0.1, 0.25, 0.6, 1))): m.between((-3.6, -51.52 + j * 0.12, 4.99), (31.6, -51.52 + j * 0.12, 4.99), 0.014, seg=6, mi=I['rubber'], rgba=c)
    for k in range(9): m.rbox(-3.0 + k * 4.0, -51.4, 5.25, 0.03, 0.03, 0.55, 0.004, seg=1, mi=I['steel_charcoal'], rgba=(0.12, 0.12, 0.13, 1))
    o = m.finish('hall_cable_tray', collection('PROTOTYPES')); inst(o, 'hall_cable_tray', 0.0, 0.0, hall, support='hanging')
    for row, yy in enumerate((-56.0, -52.0)):
        for i, x in enumerate(range(0, 32, 6)):
            mm = MB([F['steel_charcoal'], F['emissive']]); mm.use(0, (0.1, 0.1, 0.11, 1)); mm.box(0, 0, 0, 0.5, 2.4, 0.12, bevel=0.015); mm.use(1, (1.0, 0.95, 0.85, 1)); mm.box(0, 0, -0.065, 0.36, 2.3, 0.02)
            o = mm.finish(f'hall_light_fixture_{row}_{i}', hall); o.location = (LX(x + 0.0), LY(yy), 5.5)
    for i, (x, y) in enumerate(((2.0, -57.5), (14.0, -55.0), (26.0, -55.0))):
        box(f'hall_drain_{i}', x - 0.35, x + 0.35, y - 0.35, y + 0.35, -0.01, 0.003, F['corrugated'], hall, bev=0.004)
        for k in range(8): box(f'hall_drain_slot_{i}_{k}', x - 0.3, x + 0.3, y - 0.3 + k * 0.08, y - 0.3 + k * 0.08 + 0.03, 0.003, 0.005, F['rubber'], hall)
    n = 6
    for i in range(n):
        xa = -3.0 + i * 5.0
        if xa < 11 and xa + 4.2 > 5.9: continue
        box(f'clerestory_glass_{i}', xa, xa + 4.2, -48.06, -48.04, 4.3, 5.5, F['glass'], hall)
        box(f'clerestory_frame_{i}', xa - 0.05, xa + 4.25, -48.1, -48.0, 4.25, 4.3, F['steel_charcoal'], hall, bev=0.006); box(f'clerestory_frame_t{i}', xa - 0.05, xa + 4.25, -48.1, -48.0, 5.5, 5.55, F['steel_charcoal'], hall, bev=0.006)
        for k in range(4): box(f'clerestory_mull_{i}_{k}', xa + k * 1.4, xa + k * 1.4 + 0.05, -48.1, -48.0, 4.3, 5.5, F['steel_charcoal'], hall)

def build_hall(F, C):
    hall = C['HALL']
    blast_door(F, C)
    end_door(F, C, 'hall_W_door', -4.0, -54.0, -1)
    end_door(F, C, 'hall_E_door', 32.0, -54.0, 1)
    gantry(F, C); plant_door(F, C); ceiling_services(F, C)

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
