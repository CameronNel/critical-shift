"""Hall as an operations hub. Every item sits in a zone with a job:

  SW  Locker room and PPE issue (west wall lockers, benches, PPE dispenser, safety briefing board, water)
  S   Shift desk behind the cafeteria side (desk and chair, schedule board, radios and keys)
  SE  Dispatch / goods-in toward the east trunk door (three marked pallet bays, parcels, pallet jack, roll cage, shelving)
  NE  Emergency and status (safety station, hose cabinet, facility status board, evacuation plan, muster point)
  N   Blast door to the reactor spine with its control post, interlock notice and bollards; plant gantry above
  NW  Maintenance bay (workbench, tool wall, tool chest, parts shelving, marked floor zone) under the gantry stair

Clear lanes: reactor axis x 6.8..9.2 and door line y -55.3..-52.7 stay open. Lettering is baked (fe_signs); nothing here is a text object."""
import math, random
from fe_common import *
from fe_hall_assets import *
from fe_assets_int import water_cooler
from fe_assets_yard import hand_truck, bench as yard_bench
from fe_wallart import bulletin
from fe_signs import sign, hanging_sign, ROT
from fe_yard import inst

HALL_W, HALL_E, HALL_S, HALL_N = -3.83, 31.83, -59.83, -48.17     # interior wall faces (plan)
YELLOW = (0.92, 0.72, 0.06, 1); BLACK = (0.05, 0.05, 0.06, 1); GREEN = (0.1, 0.5, 0.25, 1)

def _wall(proto, name, key, c, z, coll, off=0.0):
    """Instance a back-on-y=0 wall item on interior face `key` at coordinate c along it, bottom edge z."""
    axis, face, facing = {'S': ('x', HALL_S, 'N'), 'N': ('x', HALL_N, 'S'), 'W': ('y', HALL_W, 'E'), 'E': ('y', HALL_E, 'W')}[key]
    sgn = 1 if facing in ('N', 'E') else -1; face = face + sgn * off          # off clears the wainscot (7 cm) for items that start below the rail
    x, y = (c, face) if axis == 'x' else (face, c)
    o = inst(proto, name, x, y, coll, rz=ROT[facing], z=z, support=None)
    wall_item(o, 'y' if axis == 'x' else 'x', face, sgn)
    return o

def floor_sign(coll, name, text, x, y, w, h, reads, sub=None, icon=None, style='hazard'):
    """Baked-text sign lying on the floor, readable by someone looking in direction `reads` ('N','S','E','W') (top of the text points that way)."""
    o = sign(coll, name, text, x, y, 0.0, 'N', w, h, sub=sub, style=style, icon=icon, t=0.008)
    o.location = (LX(x), LY(y), 0.0045)
    o.rotation_euler = (math.pi / 2, 0, {'N': math.pi, 'S': 0.0, 'E': math.pi / 2, 'W': -math.pi / 2}[reads]); o['support'] = 'floor'
    return o

def strip(coll, name, x0, x1, y0, y1, rgba, F):
    return box(name, x0, x1, y0, y1, 0.0, 0.005, F['signage'], coll, rgba=rgba)

def bay(coll, name, x0, x1, y0, y1, F, w=0.1):
    strip(coll, name + '_s', x0, x1, y0, y0 + w, YELLOW, F); strip(coll, name + '_n', x0, x1, y1 - w, y1, YELLOW, F)
    strip(coll, name + '_w', x0, x0 + w, y0 + w, y1 - w, YELLOW, F); strip(coll, name + '_e', x1 - w, x1, y0 + w, y1 - w, YELLOW, F)

def hatch(coll, name, x0, x1, y0, y1, n, F, vertical=False):
    for k in range(n):
        a, b = (x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n) if not vertical else (x0, x1)
        c, d = (y0, y1) if not vertical else (y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n)
        strip(coll, f'{name}_{k}', a, b, c, d, YELLOW if k % 2 == 0 else BLACK, F)

def build_hall_ops(F, C):
    hall = C['HALL']; P = collection('PROTOTYPES'); rnd = random.Random(31)
    # ---------------------------------------------------------------- prototypes
    lockers = locker_bank(F, P, 8, ajar=(2, 5)); lbench = locker_bench(F, P); dispenser = ppe_dispenser(F, P); cooler = water_cooler(F, P)
    desk = ops_desk(F, P); chair = office_chair(F, P); rdock = radio_dock(F, P); kcab = key_cabinet(F, P)
    shelf = staging_shelf(F, P); parcels = [parcel_stack(F, P, s, 3 - (s % 2)) for s in range(2)]; jack = pallet_jack(F, P); cage = roll_cage(F, P); htruck = hand_truck(F, P)
    station = safety_station(F, P); hosec = hose_cabinet(F, P); console = blast_console(F, P); bol = bollard_hall(F, P)
    wbench = workbench(F, P); twall = tool_wall(F, P); chest = tool_chest(F, P); binshelf = bin_shelf(F, P); cart = wet_cart(F, P)
    cctv = cctv_dome(F, P); smoke = ceiling_fitting(F, P, 'smoke'); horn = ceiling_fitting(F, P, 'horn'); spr = ceiling_fitting(F, P, 'sprinkler')

    # ---------------------------------------------------------------- SW: locker room and PPE issue
    inst(lockers, 'ppe_lockers', HALL_W + 0.34, -57.8, hall, rz=ROT['E'])
    for i, y in enumerate((-58.9, -56.7)): inst(lbench, f'locker_bench_{i}', -2.3, y, hall, rz=math.pi / 2)
    _wall(dispenser, 'ppe_dispenser', 'S', -2.0, 1.1, hall, off=0.075)
    sign(hall, 'sign_ppe_issue', 'PPE ISSUE', -2.0, HALL_S, 2.15, 'N', 1.3, 0.4, sub='Take what you need', icon='hat', style='nav')
    sign(hall, 'sign_lockers', 'LOCKERS', HALL_W, -57.8, 2.12, 'E', 1.5, 0.4, sub='Keep your kit tidy', icon='person', style='nav')
    sign(hall, 'board_briefing', 'SAFETY BRIEFING', 2.0, HALL_S, 1.5, 'N', 1.5, 1.0, style='board', lines=['Hard hat in the hall  ', 'Boots on, always  ', 'Hi-vis past the desk  ', 'Radio check each shift  ', 'Report hazards  at once'])
    inst(cooler, 'hall_water_cooler', 4.55, HALL_S + 0.27, hall, rz=ROT['N'])
    inst(cart, 'hall_cleaning_cart', 1.0, -59.35, hall, rz=ROT['N'] + 0.2)
    hanging_sign(hall, 'hang_locker_room', 'LOCKER ROOM', -0.9, -57.8, 3.55, 'N', 2.0, 0.5, sub='PPE issue  -  changing', icon='hat', style='nav', ceiling=5.55, F=F)

    # ---------------------------------------------------------------- S: shift desk
    dx, dy = 14.0, -58.3
    inst(desk, 'shift_desk', dx, dy, hall, rz=math.pi)
    inst(chair, 'shift_chair', dx + 0.3, dy - 0.95, hall, rz=0.15)
    sign(hall, 'board_schedule', 'SHIFT SCHEDULE', dx, HALL_S, 1.55, 'N', 2.6, 1.0, style='board', lit=True, lines=['Day shift  06:00', 'Evening shift  14:00', 'Night shift  22:00', 'Handover  15 min before'])
    sign(hall, 'sign_shift_desk', 'SHIFT DESK', dx, HALL_S, 2.7, 'N', 1.8, 0.4, sub='Check in here', icon='person', style='nav')
    _wall(rdock, 'radio_dock', 'S', 17.3, 1.1, hall, off=0.075); _wall(kcab, 'key_cabinet', 'S', 18.9, 1.0, hall, off=0.075)
    sign(hall, 'sign_radios_keys', 'RADIOS  AND  KEYS', 18.1, HALL_S, 2.0, 'N', 2.4, 0.38, style='staff')
    hanging_sign(hall, 'hang_shift_desk', 'SHIFT DESK', dx, -56.4, 3.55, 'N', 2.0, 0.5, sub='Check in and out', icon='person', style='nav', ceiling=5.55, F=F)

    # ---------------------------------------------------------------- SE: dispatch / goods in
    inst(shelf, 'dispatch_shelf_0', 26.0, HALL_S + 0.39, hall, rz=ROT['N']); inst(shelf, 'dispatch_shelf_1', 30.0, HALL_S + 0.39, hall, rz=ROT['N'])
    inst(cage, 'dispatch_roll_cage', 21.2, -59.3, hall, rz=ROT['N']); inst(htruck, 'dispatch_hand_truck', 22.6, -59.5, hall, rz=ROT['N'] + 0.1)
    bays = ((20.4, 23.2, 'A'), (23.8, 26.6, 'B'), (27.2, 30.0, 'C'))
    for x0, x1, tag in bays:
        bay(hall, f'floor_bay_{tag}', x0, x1, -58.8, -56.4, F)
        floor_sign(hall, f'floor_bay_label_{tag}', f'BAY {tag}', (x0 + x1) / 2, -57.1, 1.0, 0.3, 'N', style='hazard')
    inst(parcels[0], 'dispatch_parcels_0', 21.8, -57.6, hall, rz=0.05); inst(parcels[1], 'dispatch_parcels_1', 25.2, -57.6, hall, rz=-0.04)
    inst(jack, 'dispatch_pallet_jack', 28.0, -57.6, hall, rz=math.pi / 2 + 0.08)
    hanging_sign(hall, 'hang_dispatch', 'DISPATCH', 25.0, -55.9, 3.55, 'N', 2.2, 0.5, sub='Goods in and out  -  bays A to C', icon='box', style='nav', ceiling=5.55, F=F)
    sign(hall, 'sign_dispatch_rule', 'STAGE LOADS INSIDE THE LINES', 22.0, HALL_S, 2.35, 'N', 2.6, 0.34, style='hazard')

    # ---------------------------------------------------------------- NE: emergency, status, muster
    _wall(station, 'safety_station', 'N', 14.0, 0.0, hall, off=0.075)
    sign(hall, 'sign_safety_station', 'SAFETY STATION', 14.0, HALL_N, 2.15, 'S', 2.2, 0.42, sub='Eyewash  -  first aid  -  AED', icon='cross', style='med')
    _wall(hosec, 'hose_cabinet', 'N', 18.0, 0.9, hall, off=0.075)
    sign(hall, 'sign_fire_hose', 'FIRE HOSE', 18.0, HALL_N, 2.1, 'S', 1.1, 0.3, style='staff')
    sign(hall, 'board_status', 'FACILITY STATUS', 22.0, HALL_N, 1.5, 'S', 2.4, 1.3, style='board', lit=True, lines=['Reactor  ONLINE', 'Cooling  ONLINE', 'Power grid  STABLE', 'Fuel corridor  SEALED', 'Radiation  NORMAL', 'Spine door  LOCKED'])
    sign(hall, 'board_evacuation', 'EVACUATION PLAN', 26.0, HALL_N, 1.5, 'S', 1.5, 1.0, style='board', lines=['Walk, never run  ', 'East door  to the trunk  ', 'Muster at point A  ', 'Wait for the head count'])
    sign(hall, 'sign_muster', 'MUSTER POINT A', HALL_E, -50.4, 1.9, 'W', 1.5, 0.5, sub='Assemble here', icon='muster', style='exit')
    strip(hall, 'floor_muster_fill', 28.4, 31.4, -52.2, -48.7, (0.08, 0.35, 0.2, 1), F)
    bay(hall, 'floor_muster_edge', 28.4, 31.4, -52.2, -48.7, F, 0.08)
    floor_sign(hall, 'floor_muster_label', 'MUSTER A', 29.9, -50.45, 1.8, 0.4, 'W', icon='muster', style='exit')

    # ---------------------------------------------------------------- N: blast door post, notices, bollards
    _wall(console, 'blast_console', 'N', 11.0, 1.0, hall, off=0.075)
    sign(hall, 'sign_console', 'DOOR CONTROL', 11.0, HALL_N, 1.9, 'S', 1.2, 0.3, style='nav')
    sign(hall, 'board_spine_ppe', 'REACTOR SPINE', 5.0, HALL_N, 1.4, 'S', 1.4, 1.0, style='staff', lines=['Hard hat  required  ', 'Dosimeter  required  ', 'Two-person rule  ', 'Door opens on  shift lead'])
    for i, x in enumerate((6.25, 9.75)): inst(bol, f'blast_bollard_{i}', x, -49.2, hall)
    hatch(hall, 'floor_blast_hatch', 6.2, 9.8, -49.6, -49.25, 14, F)

    # ---------------------------------------------------------------- NW: maintenance bay under the gantry stair
    inst(wbench, 'maintenance_bench', HALL_W + 0.45, -50.9, hall, rz=ROT['E'])
    _wall(twall, 'maintenance_tool_wall', 'W', -50.9, 1.25, hall)
    inst(chest, 'maintenance_tool_chest', HALL_W + 0.34, -49.35, hall, rz=ROT['E'])
    inst(binshelf, 'maintenance_parts_shelf', 1.5, HALL_N - 0.34, hall, rz=ROT['S'])
    bay(hall, 'floor_maint_bay', -3.7, -1.3, -52.5, -50.05, F, 0.08)
    hanging_sign(hall, 'hang_maintenance', 'MAINTENANCE BAY', -2.0, -51.4, 3.55, 'E', 2.4, 0.5, sub='Hot work needs a permit', icon='wrench', style='nav', ceiling=5.55, F=F)

    # ---------------------------------------------------------------- wayfinding: hanging signs, floor stencils, walkway lines, door signs
    hanging_sign(hall, 'hang_to_refinery', 'REFINERY', -1.2, -54.0, 3.55, 'E', 2.0, 0.5, sub='Covered colonnade', icon='arrow_l', style='nav', ceiling=5.55, F=F)
    hanging_sign(hall, 'hang_to_dock', 'DOCK  /  WASTE', 29.0, -54.0, 3.55, 'W', 2.4, 0.5, sub='Trunk road', icon='arrow_r', style='nav', ceiling=5.55, F=F)
    hanging_sign(hall, 'hang_to_reactor', 'REACTOR SPINE', 8.0, -52.2, 3.55, 'S', 2.6, 0.5, sub='Authorised personnel only', icon='arrow_u', style='staff', ceiling=5.55, F=F)
    hanging_sign(hall, 'hang_to_cafeteria', 'CAFETERIA', 8.0, -58.0, 3.55, 'N', 2.2, 0.5, sub='Dining  -  lounge  -  game room', icon='cutlery', style='nav', ceiling=5.55, F=F)
    floor_sign(hall, 'floor_stencil_reactor', 'REACTOR', 8.0, -50.9, 2.2, 0.6, 'N', icon='arrow_u'); floor_sign(hall, 'floor_stencil_refinery', 'REFINERY', -1.8, -54.0, 2.4, 0.6, 'W', icon='arrow_l')
    floor_sign(hall, 'floor_stencil_dock', 'DOCK / WASTE', 29.4, -54.0, 2.6, 0.6, 'E', icon='arrow_r'); floor_sign(hall, 'floor_stencil_cafe', 'CAFETERIA', 8.0, -58.6, 2.2, 0.6, 'S', icon='arrow_d')
    for i, (x0, x1) in enumerate(((-3.7, 6.5), (9.5, 31.7))):
        for y in (-55.55, -52.45): strip(hall, f'floor_walk_ew_{i}_{y}', x0, x1, y - 0.06, y + 0.06, YELLOW, F)
    for i, (y0, y1) in enumerate(((-59.8, -55.7), (-52.3, -48.4))):
        for x in (6.6, 9.4): strip(hall, f'floor_walk_ns_{i}_{x}', x - 0.06, x + 0.06, y0, y1, YELLOW, F)
    sign(hall, 'sign_cafeteria_hall_side', 'CAFETERIA', 8.0, HALL_S, 3.8, 'N', 2.4, 0.45, icon='cutlery', style='nav')
    for nm, x, f in (('w', HALL_W, 'E'), ('e', HALL_E, 'W')): sign(hall, f'sign_exit_{nm}', 'EXIT', x, -54.0, 3.1, f, 0.9, 0.3, icon='run', style='exit', lit=True)

    # ---------------------------------------------------------------- ceiling fittings
    for i, (x, y) in enumerate(((-3.2, -59.3), (31.2, -59.3), (-3.2, -48.7), (31.2, -48.7))): inst(cctv, f'hall_cctv_{i}', x, y, hall, z=5.42, support='hanging')
    for i, x in enumerate(range(2, 32, 6)): inst(smoke, f'hall_smoke_{i}', x + 0.5, -56.0 if i % 2 else -52.0, hall, z=5.45, support='hanging')
    for i, x in enumerate((0.0, 16.0, 31.0)): inst(horn, f'hall_pa_horn_{i}', x, -59.3, hall, z=5.4, support='hanging')
    for i in range(10): inst(spr, f'hall_sprinkler_{i}', -2.2 + i * 3.7, -53.4, hall, z=4.98, support='hanging')
    return True
