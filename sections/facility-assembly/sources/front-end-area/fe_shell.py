"""Shell: floors, walls with openings, door frames, roofs, structure, colonnade, interface markers."""
from fe_common import *

T = 0.3
H_CAF, H_HALL = 5.0, 6.0
CAF = (-8.0, 26.0, -80.0, -60.0)
HALL = (-4.0, 32.0, -60.0, -48.0)
IFACES = []   # (name, plan x, plan y, normal (nx,ny), width, height)

def interface(name, x, y, normal, w, h, coll):
    e = bpy.data.objects.new('IF_PORTAL_' + name, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = 0.8
    e.location = (LX(x), LY(y), 0.0)
    e.rotation_euler = (0, 0, math.atan2(normal[1], normal[0]) - math.pi / 2)
    e['clear_width_m'] = w; e['clear_height_m'] = h; e['outward_normal'] = list(normal)
    coll.objects.link(e)
    IFACES.append((name, x, y, normal, w, h))

def frame(name, cx, cy, axis, w, h, depth, F, coll, mat='steel_charcoal'):
    """Steel door frame around an opening. axis 'x': wall runs along x (opening faces +-y)."""
    t = 0.14; d = depth
    m = F[mat]
    if axis == 'x':
        box(name + '_L', cx - w / 2 - t, cx - w / 2, cy - d / 2, cy + d / 2, 0, h + t, m, coll, bev=0.012)
        box(name + '_R', cx + w / 2, cx + w / 2 + t, cy - d / 2, cy + d / 2, 0, h + t, m, coll, bev=0.012)
        box(name + '_H', cx - w / 2 - t, cx + w / 2 + t, cy - d / 2, cy + d / 2, h, h + t, m, coll, bev=0.012)
    else:
        box(name + '_L', cx - d / 2, cx + d / 2, cy - w / 2 - t, cy - w / 2, 0, h + t, m, coll, bev=0.012)
        box(name + '_R', cx - d / 2, cx + d / 2, cy + w / 2, cy + w / 2 + t, 0, h + t, m, coll, bev=0.012)
        box(name + '_H', cx - d / 2, cx + d / 2, cy - w / 2 - t, cy + w / 2 + t, h, h + t, m, coll, bev=0.012)

def wall(name, axis, pos, a0, a1, h, openings, F, coll, dado=True, pilasters=0.0, inside='both'):
    """Wall along axis ('x': runs in x at y=pos) from a0 to a1, with openings [(centre, width, height)].
    inside: which face is interior: '+', '-' or 'both'. Interior faces get lilac plaster, a navy dado, a white rail and a cornice;
    an exterior face keeps the concrete core, with an orange stripe and a charcoal cap."""
    ops = sorted(openings)
    cuts = [a0]
    for c, w, oh in ops: cuts += [c - w / 2, c + w / 2]
    cuts.append(a1)
    segs = [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts), 2) if cuts[i + 1] - cuts[i] > 0.02]
    sides = {'both': (1, -1), '+': (1,), '-': (-1,)}[inside]
    ext = [] if inside == 'both' else [-sides[0]]
    core = F['plaster'] if inside == 'both' else F['concrete_slab']
    def sb(s0, s1, z0, z1, side, o0, o1, mat, bev=0.0, nm=''):
        lo, hi = sorted((pos + side * o0, pos + side * o1))
        if axis == 'x': return box(nm, s0, s1, lo, hi, z0, z1, mat, coll, bev=bev)
        return box(nm, lo, hi, s0, s1, z0, z1, mat, coll, bev=bev)
    def run(s0, s1, z0, z1, nm):
        if axis == 'x': box(nm + '_core', s0, s1, pos - T / 2, pos + T / 2, z0, z1, core, coll)
        else: box(nm + '_core', pos - T / 2, pos + T / 2, s0, s1, z0, z1, core, coll)
        if inside != 'both':
            for sd in sides: sb(s0, s1, z0, z1, sd, T / 2, T / 2 + 0.02, F['plaster'], nm=nm + '_skin')
    for i, (s0, s1) in enumerate(segs):
        run(s0, s1, 0, h, f'{name}_seg{i}')
        if dado:
            for sd in sides:
                sb(s0, s1, 0.0, 1.1, sd, T / 2, T / 2 + 0.045, F['dado'], 0.008, f'{name}_dado{i}')
                sb(s0, s1, 1.1, 1.17, sd, T / 2, T / 2 + 0.06, F['trim'], 0.006, f'{name}_rail{i}')
                sb(s0, s1, 0.0, 0.12, sd, T / 2 + 0.045, T / 2 + 0.06, F['rubber'], 0.004, f'{name}_skirt{i}')
                sb(s0, s1, h - 0.14, h, sd, T / 2, T / 2 + 0.07, F['trim'], 0.01, f'{name}_cornice{i}')
            for sd in ext:
                sb(s0, s1, 0.0, 0.5, sd, T / 2, T / 2 + 0.03, F['concrete_slab'], 0.01, f'{name}_plinth{i}')
                sb(s0, s1, 1.1, 1.22, sd, T / 2, T / 2 + 0.05, F['steel_accent'], 0.006, f'{name}_stripe{i}')
                sb(s0, s1, h - 0.18, h, sd, T / 2, T / 2 + 0.07, F['steel_charcoal'], 0.01, f'{name}_cap{i}')
    for j, (c, w, oh) in enumerate(ops):
        if axis == 'x': box(f'{name}_hdr{j}_core', c - w / 2, c + w / 2, pos - T / 2, pos + T / 2, oh, h, core, coll)
        else: box(f'{name}_hdr{j}_core', pos - T / 2, pos + T / 2, c - w / 2, c + w / 2, oh, h, core, coll)
        if inside != 'both':
            for sd in sides: sb(c - w / 2, c + w / 2, oh, h, sd, T / 2, T / 2 + 0.02, F['plaster'], nm=f'{name}_hdr{j}_skin')
        frame(f'{name}_frame{j}', *( (c, pos) if axis == 'x' else (pos, c) ), axis, w, oh, T + 0.08, F, coll)
    if pilasters:
        n = int((a1 - a0) / pilasters); sd = sides[0]
        for k in range(1, n):
            p = a0 + k * pilasters
            if any(c - w / 2 - 0.4 < p < c + w / 2 + 0.4 for c, w, _ in ops): continue
            lo, hi = sorted((pos + sd * T / 2, pos + sd * (T / 2 + 0.2)))
            if axis == 'x': box(f'{name}_pilaster{k}', p - 0.16, p + 0.16, lo, hi, 0, h - 0.14, F['plaster'], coll, bev=0.015)
            else: box(f'{name}_pilaster{k}', lo, hi, p - 0.16, p + 0.16, 0, h - 0.14, F['plaster'], coll, bev=0.015)

def windows_strip(name, x, y0, y1, z0, z1, F, coll, face=+1):
    """High window band on a wall running along y at plan x: frame, mullions and glass."""
    n = max(int((y1 - y0) / 1.5), 1); step = (y1 - y0) / n
    box(name + '_sill', x - 0.2, x + 0.2, y0, y1, z0 - 0.08, z0, F['steel_charcoal'], coll, bev=0.01)
    box(name + '_head', x - 0.2, x + 0.2, y0, y1, z1, z1 + 0.08, F['steel_charcoal'], coll, bev=0.01)
    for k in range(n + 1):
        box(f'{name}_mull{k}', x - 0.14, x + 0.14, y0 + k * step - 0.04, y0 + k * step + 0.04, z0, z1, F['steel_charcoal'], coll, bev=0.008)
    box(name + '_glass', x - 0.02, x + 0.02, y0, y1, z0, z1, F['glass'], coll)

def build_shell(F, C):
    yard, caf, hall, shared, ifc = C['YARD'], C['CAFETERIA'], C['HALL'], C['SHARED'], C['INTERFACES']
    # ---------------- floors
    box('caf_floor', CAF[0], CAF[1], CAF[2], CAF[3], -0.25, 0.0, F['cafe_tile'], caf)
    box('hall_floor', HALL[0], HALL[1], HALL[2], HALL[3], -0.25, 0.0, F['cafe_tile'], hall)
    # blue tile border along every wall, as in the spawn room
    bw = 0.9
    for nm, (x0, x1, y0, y1), co in (('caf', CAF, caf), ('hall', HALL, hall)):
        box(nm + '_border_S', x0 + 0.15, x1 - 0.15, y0 + 0.15, y0 + 0.15 + bw, -0.01, 0.003, F['tile_blue'], co)
        box(nm + '_border_N', x0 + 0.15, x1 - 0.15, y1 - 0.15 - bw, y1 - 0.15, -0.01, 0.003, F['tile_blue'], co)
        box(nm + '_border_W', x0 + 0.15, x0 + 0.15 + bw, y0 + 0.15 + bw, y1 - 0.15 - bw, -0.01, 0.003, F['tile_blue'], co)
        box(nm + '_border_E', x1 - 0.15 - bw, x1 - 0.15, y0 + 0.15 + bw, y1 - 0.15 - bw, -0.01, 0.003, F['tile_blue'], co)
    # hall route lines (inset yellow strips) and rubber entry mats
    for y in (-56.2, -51.8): box(f'hall_route_line_{y}', -3.7, 31.7, y - 0.07, y + 0.07, 0.0, 0.006, F['signage'], hall, rgba=(0.9, 0.7, 0.05, 1))
    for x in (4.9, 11.1): box(f'hall_lane_line_{x}', x - 0.07, x + 0.07, -60.0, -48.2, 0.0, 0.006, F['signage'], hall, rgba=(0.9, 0.7, 0.05, 1))
    box('caf_door_mat_S', 6.6, 9.4, -80.4, -78.4, 0.0, 0.015, F['rubber'], caf, bev=0.004)
    box('caf_door_mat_W', -8.0, -6.0, -71.6, -68.4, 0.0, 0.015, F['rubber'], caf, bev=0.004)
    box('hall_blast_mat', 6.0, 10.0, -50.0, -48.2, 0.0, 0.015, F['rubber'], hall, bev=0.004)
    # ---------------- walls
    wall('caf_S', 'x', -80.0, CAF[0], CAF[1], H_CAF, [(8.0, 2.6, 2.7)], F, caf, pilasters=4.0, inside='+')
    wall('cafhall_mid', 'x', -60.0, CAF[0], HALL[1], H_HALL, [(8.0, 6.0, 3.6)], F, hall, pilasters=4.0)
    wall('caf_W', 'y', CAF[0], CAF[2], CAF[3], H_CAF, [(-70.0, 3.0, 2.7)], F, caf, pilasters=0.0, inside='+')
    wall('caf_E', 'y', CAF[1], CAF[2], CAF[3], H_CAF, [(-70.0, 2.2, 2.5)], F, caf, pilasters=4.0, inside='-')
    wall('hall_W', 'y', HALL[0], HALL[2], HALL[3], H_HALL, [(-54.0, 2.4, 2.7)], F, hall, inside='+')
    wall('hall_E', 'y', HALL[1], HALL[2], HALL[3], H_HALL, [(-54.0, 2.4, 2.7)], F, hall, inside='-')
    wall('hall_N', 'x', -48.0, HALL[0], HALL[1], H_HALL, [(8.0, 3.6, 3.2)], F, hall, pilasters=4.0, inside='-')
    # cafeteria north wall piece west of the hall (x -8..-4) is covered by cafhall_mid (height 6): trim it down to the cafeteria ceiling
    # high windows on the yard side
    windows_strip('caf_W_win_S', CAF[0], -79.0, -72.0, 2.7, 4.4, F, caf)
    windows_strip('caf_W_win_N', CAF[0], -68.0, -61.0, 2.7, 4.4, F, caf)
    # ---------------- interface markers (plan x, y, outward normal, clear w, h)
    interface('CAF_S_SPAWN_AIRLOCK', 8.0, -80.0, (0, -1), 2.6, 2.7, ifc)
    interface('CAF_N_HALL_OPENING', 8.0, -60.0, (0, 1), 6.0, 3.6, ifc)
    interface('CAF_W_YARD', -8.0, -70.0, (-1, 0), 3.0, 2.7, ifc)
    interface('CAF_E_MEDICAL', 26.0, -70.0, (1, 0), 2.2, 2.5, ifc)
    interface('HALL_W_REFINERY', -4.0, -54.0, (-1, 0), 2.4, 2.7, ifc)
    interface('HALL_N_SPINE_REACTOR', 8.0, -48.0, (0, 1), 3.6, 3.2, ifc)
    interface('HALL_E_TRUNK', 32.0, -54.0, (1, 0), 2.4, 2.7, ifc)

def build_roofs(F, C):
    caf, hall, shared = C['CAFETERIA'], C['HALL'], C['SHARED']
    # ceilings/roofs: deck strips with skylight slots, portal beams, purlins, standing-seam ribs
    def roof(name, x0, x1, y0, y1, h, coll, skylights):
        # beams across x every 4 m
        k = 0; y = y0 + 2.0
        while y < y1:
            box(f'{name}_beam{k}', x0, x1, y - 0.12, y + 0.12, h - 0.55, h - 0.05, F['steel_charcoal'], coll, bev=0.015)
            k += 1; y += 4.0
        # purlins along y every 3 m
        x = x0 + 1.5; k = 0
        while x < x1:
            box(f'{name}_purlin{k}', x - 0.06, x + 0.06, y0, y1, h - 0.12, h, F['steel_charcoal'], coll)
            k += 1; x += 3.0
        # deck as strips along x with skylight slots
        slots = sorted(skylights); cur = x0
        for i, (s0, s1) in enumerate(slots + [(x1, x1)]):
            if s0 - cur > 0.05: box(f'{name}_deck{i}', cur, s0, y0, y1, h, h + 0.12, F['ceiling'], coll)
            if s1 > s0: box(f'{name}_sky{i}', s0, s1, y0, y1, h + 0.02, h + 0.06, F['glass'], coll)
            cur = s1
        # ribs on top
        x = x0 + 0.3; k = 0
        while x < x1 - 0.1:
            if not any(s0 - 0.1 < x < s1 + 0.1 for s0, s1 in slots):
                box(f'{name}_rib{k}', x - 0.025, x + 0.025, y0, y1, h + 0.12, h + 0.2, F['corrugated'], coll)
            x += 0.65; k += 1
        # parapet trim
        box(f'{name}_edgeS', x0 - 0.1, x1 + 0.1, y0 - 0.12, y0 + 0.12, h - 0.1, h + 0.3, F['steel_charcoal'], coll, bev=0.015)
        box(f'{name}_edgeN', x0 - 0.1, x1 + 0.1, y1 - 0.12, y1 + 0.12, h - 0.1, h + 0.3, F['steel_charcoal'], coll, bev=0.015)
        box(f'{name}_edgeW', x0 - 0.12, x0 + 0.12, y0, y1, h - 0.1, h + 0.3, F['steel_charcoal'], coll, bev=0.015)
        box(f'{name}_edgeE', x1 - 0.12, x1 + 0.12, y0, y1, h - 0.1, h + 0.3, F['steel_charcoal'], coll, bev=0.015)
    roof('caf_roof', CAF[0], CAF[1], CAF[2], CAF[3], H_CAF, caf, [(-2.0, -1.2), (4.6, 5.4), (11.0, 11.8), (17.4, 18.2), (23.0, 23.8)])
    roof('hall_roof', HALL[0], HALL[1], HALL[2], HALL[3], H_HALL, hall, [(1.0, 2.0), (14.0, 15.0), (22.0, 23.0)])
    # corner columns, exposed
    for i, (x, y) in enumerate([(CAF[0], CAF[2]), (CAF[1], CAF[2]), (CAF[0], CAF[3]), (HALL[1], HALL[2]), (HALL[1], HALL[3]), (HALL[0], HALL[3])]):
        box(f'corner_column{i}', x - 0.2, x + 0.2, y - 0.2, y + 0.2, 0, H_HALL, F['steel_charcoal'], shared, bev=0.02)
