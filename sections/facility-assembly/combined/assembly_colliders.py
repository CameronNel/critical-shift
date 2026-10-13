"""Collision and navigation proxies for the connective parts of the compact map (halls, reactor stubs, junctions, the condenser stair), separate from the visual meshes.
Called by build_compact_map.py (post_build); everything goes into the COLLIDERS collection, hidden from render and viewport.

Every proxy is a box (or, for the stair, a sloped slab) with custom properties the Unity side binds on:
  collider_role: floor | wall | roof | ramp | door_blocker | door_threshold
  zone: the hall or junction it belongs to;  door_id: for blockers and thresholds (validation/doors.json)
  is_trigger: thresholds are triggers; blockers are solid and enabled only while the door is closed.
Rooms keep their own collision (their modules or a later per-room pass); these proxies end at each room's door plane. Dimensions are the build's own numbers
(build_compact_map.py RY, CONC, WASTE_HOLE, reactor_links) and measured stub walls (reactor N stub clear x +-2.5, W stub clear y +-2.9, plan cut 2026-10-13), in reactor-local
coordinates moved by RY where the part moved with the reactor.
Unreviewed. The proxies are checked by walk_test.py --colliders (capsule against the proxies alone) as well as by the visual-mesh walk test."""
import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix

ROWS = []

def _coll(root):
    c = bpy.data.collections.new('COLLIDERS'); root.children.link(c); c.hide_render = True; return c

def box(coll, name, xs, ys, zs, role, zone, door=None, trigger=False, rz=0.0, about=(0.0, 0.0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = xs[0] if v.co.x < 0 else xs[1]; v.co.y = ys[0] if v.co.y < 0 else ys[1]; v.co.z = zs[0] if v.co.z < 0 else zs[1]
    if rz:
        M = Matrix.Translation((about[0], about[1], 0)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Translation((-about[0], -about[1], 0)); bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    me = bpy.data.meshes.new('COL ' + name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('COL ' + name, me); coll.objects.link(o); o.display_type = 'WIRE'; o.hide_render = True
    o['collider_role'] = role; o['zone'] = zone; o['is_trigger'] = trigger
    if door: o['door_id'] = door
    ROWS.append(dict(name=o.name, role=role, zone=zone, door_id=door, trigger=trigger, bounds=[[round(min(v.co[i] for v in me.vertices), 3) for i in range(3)], [round(max(v.co[i] for v in me.vertices), 3) for i in range(3)]]))
    return o

def slab(coll, name, p0, p1, half_w, thick, role, zone, axis_x=True):
    """Sloped slab from p0 to p1 (plan x, y, z of the walking surface centre line), half width half_w, thickness below the surface."""
    a, b = Vector(p0), Vector(p1); d = (b - a); d2 = Vector((d.x, d.y, 0)).normalized(); n = Vector((-d2.y, d2.x, 0))
    vs = []
    for p in (a, b):
        for s in (-1, 1):
            for dz in (0.0, -thick): vs.append(p + n * s * half_w + Vector((0, 0, dz)))
    bm = bmesh.new(); V = [bm.verts.new(v) for v in vs]
    for f in ((0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)): bm.faces.new([V[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new('COL ' + name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('COL ' + name, me); coll.objects.link(o); o.display_type = 'WIRE'; o.hide_render = True; o['collider_role'] = role; o['zone'] = zone; o['is_trigger'] = False
    ROWS.append(dict(name=o.name, role=role, zone=zone, door_id=None, trigger=False, bounds=[[round(min(v.co[i] for v in me.vertices), 3) for i in range(3)], [round(max(v.co[i] for v in me.vertices), 3) for i in range(3)]]))
    return o

def hall_x(c, zone, x0, x1, yc, w, h, t=0.3, gaps_n=(), gaps_s=()):
    """Straight hall along x: floor, roof, north and south walls with door gaps (lists of (x0, x1))."""
    y0, y1 = yc - w / 2, yc + w / 2
    box(c, zone + ' floor', (x0, x1), (y0 - t, y1 + t), (-0.3, 0.0), 'floor', zone)
    box(c, zone + ' roof', (x0, x1), (y0 - t, y1 + t), (h, h + 0.25), 'roof', zone)
    for side, (ya, yb), gaps in (('north', (y1, y1 + t), gaps_n), ('south', (y0 - t, y0), gaps_s)):
        cur = x0
        for ga, gb in sorted(gaps) + [(x1, x1)]:
            if ga - cur > 0.01: box(c, '%s %s wall %.1f' % (zone, side, cur), (cur, ga), (ya, yb), (0.0, h), 'wall', zone)
            cur = gb

def hall_y(c, zone, y0, y1, xc, w, h, t=0.3, gaps_e=(), gaps_w=()):
    x0, x1 = xc - w / 2, xc + w / 2
    box(c, zone + ' floor', (x0 - t, x1 + t), (y0, y1), (-0.3, 0.0), 'floor', zone)
    box(c, zone + ' roof', (x0 - t, x1 + t), (y0, y1), (h, h + 0.25), 'roof', zone)
    for side, (xa, xb), gaps in (('east', (x1, x1 + t), gaps_e), ('west', (x0 - t, x0), gaps_w)):
        cur = y0
        for ga, gb in sorted(gaps) + [(y1, y1)]:
            if ga - cur > 0.01: box(c, '%s %s wall %.1f' % (zone, side, cur), (xa, xb), (cur, ga), (0.0, h), 'wall', zone)
            cur = gb

def build(root, L):
    """L: the build_compact_map module (its placement constants and DOORS table)."""
    import build_combined_map as BM
    ROWS.clear(); c = _coll(root)
    RY = L.RY; C = L.CONC; x0, y0, y1, xs = C['x0'], C['y0'], C['y1'], L.SPINE_W
    # spine (front end, plan x 6.15..9.85 clear, from the hall's north wall to its moved end door; clear height 3.6 under the frame; walls 0.3): dock door east, concourse west
    hall_y(c, 'spine', -47.85, L.SPINE_END, 8.0, 3.7, 3.6, gaps_e=[(L.DOCK[1] - 1.3, L.DOCK[1] + 1.3)], gaps_w=[(y0, y1)])
    # south concourse (build_compact_map.CONC): its west wall is the fuel corridor's east face, with the F02E door; the tunnel into the reactor south door
    fy0, fy1 = L.F02E[1] - 1.19, L.F02E[1] + 1.19
    box(c, 'concourse floor', (x0, xs), (y0 - 0.3, y1 + 0.3), (-0.3, 0.0), 'floor', 'concourse')
    box(c, 'concourse roof', (x0 - 0.3, xs), (y0 - 0.3, y1 + 0.3), (C['roof'], C['roof'] + 0.25), 'roof', 'concourse')
    box(c, 'concourse west wall south', (x0 - 0.3, x0), (y0 - 0.3, fy0), (0, C['roof']), 'wall', 'concourse')
    box(c, 'concourse west wall north', (x0 - 0.3, x0), (fy1, y1 + 0.3), (0, C['roof']), 'wall', 'concourse')
    box(c, 'concourse west wall over door', (x0 - 0.3, x0), (fy0, fy1), (3.0, C['roof']), 'wall', 'concourse')
    box(c, 'concourse south wall', (x0, xs), (y0 - 0.3, y0), (0, C['roof']), 'wall', 'concourse')
    box(c, 'concourse north wall west', (x0, -2.5), (y1, y1 + 0.3), (0, C['roof']), 'wall', 'concourse')
    box(c, 'concourse north wall east', (2.5, xs), (y1, y1 + 0.3), (0, C['roof']), 'wall', 'concourse')
    hall_y(c, 'reactor south tunnel', y1 + 0.3, RY - 10.8, 0.0, 5.0, 5.0)
    # reactor stubs: north (to turbine D01) and west (to cooling P01); the closed south-east stub gets a blocker in the door pass below
    hall_y(c, 'reactor north stub', RY + 10.8, RY + 14.5, 0.0, 5.0, 5.0)
    hall_x(c, 'reactor west stub', -14.5, -10.8, RY, 5.8, 5.0)
    # junction thresholds through the new wall openings (floor plates spanning the wall thickness, heads)
    for zone, xr, yc, w, h in (('reactor-waste junction', (10.8, L.WASTE[0] - 0.32), L.WASTE[1], L.WASTE_HOLE[1] - L.WASTE_HOLE[0], L.WASTE_HOLE[2]),
                               ('spine-dock junction', (9.85, L.DOCK[0]), L.DOCK[1], 2.4, 2.6), ('turbine-electrical junction', (10.0, L.ELEC[0] + 0.2), L.ELEC[1], 2.4, 2.7)):
        box(c, zone + ' floor', xr, (yc - w / 2 - 0.3, yc + w / 2 + 0.3), (-0.3, 0.0), 'floor', zone)
        box(c, zone + ' head', xr, (yc - w / 2, yc + w / 2), (h, h + 0.3), 'roof', zone)
        if zone == 'reactor-waste junction':   # jambs: the wall either side of the opening
            box(c, zone + ' jamb south', xr, (yc - w / 2 - 0.3, yc - w / 2), (0, h), 'wall', zone); box(c, zone + ' jamb north', xr, (yc + w / 2, yc + w / 2 + 0.3), (0, h), 'wall', zone)
        if zone == 'spine-dock junction':      # the dock P1 tube walls (module x +-1.2..1.3, y -2.0..0)
            box(c, zone + ' tube north', (10.15, L.DOCK[0]), (yc + 1.2, yc + 1.3), (0, 2.6), 'wall', zone); box(c, zone + ' tube south', (10.15, L.DOCK[0]), (yc - 1.3, yc - 1.2), (0, 2.6), 'wall', zone)
            box(c, zone + ' tube floor', (10.15, L.DOCK[0]), (yc - 1.3, yc + 1.3), (-0.3, 0.0), 'floor', zone)
    # condenser stair: top landing, a ramp along the flight's pitch line (34 risers, 30.5 degrees: under a 45 degree slope limit), shaft walls, the lower corridor
    S = L.ST; z1 = -S['drop']; zone = 'condenser stair'
    yd0, yd1 = L.TURB[1] + L.STAIR_DOOR_Y - 1.0, L.TURB[1] + L.STAIR_DOOR_Y + 1.0
    box(c, 'stair top landing', (S['xw'], S['xe'] + S['t']), (S['ytop'], S['yn']), (-0.3, 0.0), 'floor', zone)
    slab(c, 'stair ramp', ((S['xw'] + S['xe']) / 2, S['ytop'], 0.0), ((S['xw'] + S['xe']) / 2, S['ybot'], z1), (S['xe'] - S['xw']) / 2, 0.3, 'ramp', zone)
    box(c, 'stair west wall', (S['xw'] - S['t'], S['xw']), (S['cy0'], S['yn'] + S['t']), (z1, S['roof']), 'wall', zone)
    box(c, 'stair east wall south', (S['xe'], S['xe'] + S['t']), (S['ybot'], yd0), (z1, S['roof']), 'wall', zone)
    box(c, 'stair east wall north', (S['xe'], S['xe'] + S['t']), (yd1, S['yn']), (z1, S['roof']), 'wall', zone)
    box(c, 'stair east wall below door', (S['xe'], S['xe'] + S['t']), (yd0, yd1), (z1, -0.3), 'wall', zone)
    box(c, 'stair north wall', (S['xw'], S['xe']), (S['yn'], S['yn'] + S['t']), (-0.3, S['roof']), 'wall', zone)
    box(c, 'stair roof', (S['xw'] - S['t'], S['xe'] + S['t']), (S['ybot'], S['yn'] + S['t']), (S['roof'], S['roof'] + 0.25), 'roof', zone)
    cx0, cx1, cy0, cy1, zc = S['xw'], S['cx1'], S['cy0'], S['cy1'], z1 + S['ch']
    box(c, 'condenser corridor floor', (cx0, cx1), (cy0, cy1), (z1 - 0.3, z1), 'floor', zone)
    box(c, 'condenser corridor north floor', (S['cx0b'], cx1), (cy1, S['vy']), (z1 - 0.3, z1), 'floor', zone)
    box(c, 'condenser corridor south wall', (cx0 - S['t'], cx1 + S['t']), (cy0 - S['t'], cy0), (z1, zc), 'wall', zone)
    box(c, 'condenser corridor east wall', (cx1, cx1 + S['t']), (cy0, S['vy']), (z1, zc), 'wall', zone)
    box(c, 'condenser corridor north wall', (S['xe'], S['cx0b']), (cy1, cy1 + S['t']), (z1, zc), 'wall', zone)
    box(c, 'condenser corridor west jamb', (S['cx0b'] - S['t'], S['cx0b']), (cy1, S['vy']), (z1, zc), 'wall', zone)
    box(c, 'condenser corridor roof', (S['xe'], cx1 + S['t']), (cy0 - S['t'], cy1 + S['t']), (zc, zc + 0.25), 'roof', zone)
    box(c, 'condenser corridor north roof', (S['cx0b'] - S['t'], cx1 + S['t']), (cy1, S['vy']), (zc, zc + 0.25), 'roof', zone)
    # doors: a trigger threshold on every door plane, and a solid blocker on every door (enabled while closed; the map opens with the states in doors.json)
    place = {r[0]: (r[3], r[4]) for r in BM.ROOMS}
    for did, room, cc, n, w, h, kind, state, to, leaf in L.DOORS:
        loc, rz = place[room]; p = L.wxy(loc, rz, *cc); d = Vector(L.rot(rz)(*n)).normalized(); ang = math.atan2(d.y, d.x); z0 = loc[2]
        box(c, 'DOOR_%s threshold' % did, (p.x - 0.3, p.x + 0.3), (p.y - w / 2, p.y + w / 2), (z0, z0 + min(h, 2.4)), 'door_threshold', room, door=did, trigger=True, rz=ang, about=(p.x, p.y))
        b = box(c, 'DOOR_%s blocker' % did, (p.x - 0.06, p.x + 0.06), (p.y - w / 2, p.y + w / 2), (z0, z0 + h), 'door_blocker', room, door=did, rz=ang, about=(p.x, p.y))
        b['enabled_when'] = 'closed,locked'; b['enabled_now'] = state != 'open'
    c.hide_viewport = False
    for o in c.objects: o.hide_set(False)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validation', 'colliders.json')
    json.dump(dict(note='Collision/navigation proxies of the compact map (halls, stubs, junctions, stair, door thresholds and blockers). Unreviewed. Plan metres, z up; Unity import is not run.',
                   counts={r: sum(1 for x in ROWS if x['role'] == r) for r in sorted({x['role'] for x in ROWS})}, colliders=ROWS), open(out, 'w'), indent=1)
    print('COLLIDERS', len(ROWS), 'proxies')
