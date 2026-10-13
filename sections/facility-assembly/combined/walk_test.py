"""Player-capsule walk test on the built map (geometry only; it is not the runtime controller). Run on a built scene:

    blender --background combined_map.blend --python walk_test.py -- [validation/walk_report.json]

Capsule: radius 0.40 m, height 1.80 m, step offset 0.35 m (Unity CharacterController-like: anything lower than 0.35 m above the floor under the capsule is a step,
not an obstacle). Each route is a polyline of plan points (x, y, floor z) through door centres. Every 0.1 m the test
  * casts a ray down from 0.9 m above the expected floor: a walkable floor (normal z >= 0.7) must lie within 0.45 m of the expected height (stairs included);
  * checks seven spheres of radius 0.40 centred 0.75 to 1.40 m above that floor against every evaluated triangle near the route (BVH find_nearest), which covers
    the capsule from 0.35 to 1.80 m;
  * if the centre line is blocked, searches sideways up to 1.5 m (0.1 m steps) for a lane, and joins the lanes into one continuous path (at most 0.2 m sideways per 0.1 m
    forward, dynamic programming). A route passes when a continuous lane exists from its first point to its last.
Door states are those of the built scene (closed leaves are geometry, so a route through a closed door fails). The BLOCK_CHECKS list asserts that closed doors block.
Writes the lane length of every route (the walked distance used for the travel times) and every blocked sample with the owner of the nearest triangle."""
import bpy, sys, os, json, math, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
R_CAP, STEP, H_CAP, DS, SIDE, MAXSHIFT = 0.40, 0.35, 1.80, 0.1, 1.5, 0.2

def P(*pts): return [tuple(map(float, p)) for p in pts]
RY = float(bpy.context.scene.get('reactor_y', 0.0)) if bpy.context.scene else 0.0    # reactor centre y, stored by build_compact_map.py
def R(*pts): return [(float(x), float(y) + RY, float(z)) for x, y, z in pts]         # reactor-local points (everything that moved with the reactor)
CY = RY - 17.2                                                                         # concourse centre line
F02E = (-5.46, -36.62)                                                                 # short fuel corridor reactor door (module (16.74, 6.98) + F01 (-22.2, -43.6))
WY = RY + 3.86                                                                         # reactor east opening to waste (centre)
# Routes (plan metres). Door centres come from validation/doors.json; interior waypoints follow each room's contract lanes where it has them.
ROUTES = {
    'spawn_to_reactor': P((8, -88, 0), (8, -80, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0), (0, RY - 12, 0), (0, RY - 6, 0)),
    'reactor_to_turbine_to_electrical': R((0, 6.5, 0), (0, 10.5, 0), (0, 14.5, 0), (0, 16.5, 0), (8.2, 17.5, 0), (8.2, 33.0, 0), (10.4, 33.0, 0), (13.0, 33.0, 0), (19.0, 33.0, 0)),
    'turbine_to_condenser': R((0, 16.5, 0), (-2.4, 18.0, 0), (-2.6, 27.95, 0), (-4.2, 27.95, 0), (-5.6, 27.9, 0), (-5.6, 26.8, 0), (-5.6, 16.9, -6), (-5.6, 15.7, -6), (1.6, 15.7, -6), (1.6, 19.3, -6), (1.6, 21.9, -6), (1.6, 24.0, -6)),
    'reactor_to_cooling': R((-9.0, 0, 0), (-11.6, 0, 0), (-14.5, 0, 0), (-18, 0, 0), (-24, 0, 0)),
    'reactor_to_waste': R((0, -6, 0), (6.5, -6.5, 0), (7.5, 0, 0), (8.5, 3.86, 0), (10.8, 3.86, 0), (11.94, 3.86, 0), (16.0, 3.86, 0), (24.0, 3.86, 0)),
    'spine_to_dock': P((8, -45, 0), (8, -40.39, 0), (10.15, -40.39, 0), (12.15, -40.39, 0), (13.3, -40.39, 0), (19.15, -40.39, 0), (26.0, -40.39, 0)),
    # the fuel run: refinery fuel door F01, north through the corridor, east through the middle of the freight gate to F02E, the concourse and the reactor floor
    'refinery_fuel_to_reactor': P((-22.2, -46.5, 0), (-22.2, -43.6, 0), (-22.2, -35.1, 0), (-8.5, -35.1, 0), (-7.0, F02E[1], 0), (F02E[0], F02E[1], 0), (-3.0, CY, 0), (0, CY, 0), (0, RY - 12, 0), (0, RY - 6, 0)),
    # the same run on the shortest clear line (inside the gate's south post, then across the concourse diagonally): what a player takes; the route above keeps the cart on the gate centre
    'refinery_fuel_to_reactor_shortest': P((-22.2, -46.5, 0), (-22.2, -43.6, 0), (-22.2, -38.6, 0), (-20.7, -36.0, 0), (-6.5, -36.0, 0), (F02E[0], F02E[1], 0), (-1.0, -34.2, 0), (0, RY - 12, 0), (0, RY - 6, 0)),
    'hall_to_refinery': P((8, -54, 0), (-4, -54, 0), (-18.9, -54, 0), (-22, -54, 0)),
    'cafeteria_to_yard_to_mine': P((8, -70, 0), (-7.27, -70, 0), (-12, -70, 0), (-30, -70, 0), (-50, -70, 0), (-56, -70, 0)),
    'yard_to_refinery_freight (cart route)': P((-22.2, -66, 0), (-22.2, -60.1, 0), (-22.2, -57.5, 0), (-22.2, -54.5, 0)),
    'cafeteria_to_medical': P((8, -70, 0), (24, -70, 0), (26, -70, 0), (28, -70, 0), (31, -70, 0)),
    # travel-time routes (ASSEMBLY_REPORT.md): door to door through the real interiors
    'reactor_to_dock': P((0, RY - 6, 0), (0, RY - 12, 0), (0, CY, 0), (8, CY, 0), (8, -40.39, 0), (10.15, -40.39, 0), (12.15, -40.39, 0), (14.5, -40.39, 0)),
    'medical_to_reactor': P((31, -70, 0), (26, -70, 0), (8, -70, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0), (0, RY - 12, 0), (0, RY - 6, 0)),
    'spawn_to_mine_portal': P((8, -88, 0), (8, -80, 0), (8, -70, 0), (-7.27, -70, 0), (-12, -70, 0), (-30, -70, 0), (-50, -70, 0), (-53.4, -70, 0)),
    'spawn_to_electrical': P((8, -88, 0), (8, -80, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0)) + R((0, -12, 0), (0, -7.5, 0), (6.5, -6.5, 0), (7.5, 0, 0), (6.5, 6.5, 0),
                              (0, 7.5, 0), (0, 10.5, 0), (0, 14.5, 0), (0, 16.5, 0), (8.2, 17.5, 0), (8.2, 33.0, 0), (10.4, 33.0, 0), (13.0, 33.0, 0)),
    'reactor_to_condenser': R((0, 7.5, 0), (0, 14.5, 0), (0, 16.5, 0), (-2.4, 18.0, 0), (-2.6, 27.95, 0), (-4.2, 27.95, 0), (-5.6, 27.9, 0), (-5.6, 26.8, 0), (-5.6, 16.9, -6), (-5.6, 15.7, -6),
                              (1.6, 15.7, -6), (1.6, 19.3, -6), (1.6, 22.0, -6)),
    'spawn_to_waste': P((8, -88, 0), (8, -80, 0), (8, -60, 0), (8, -49, 0), (8, -40, 0), (8, CY, 0), (0, CY, 0)) + R((0, -12, 0), (0, -7.5, 0), (6.5, -6.5, 0), (7.5, 0, 0), (8.5, 3.86, 0), (10.8, 3.86, 0), (14.0, 3.86, 0)),
}
# halls, stubs, junctions and the stair, walked against the collision proxies alone (assembly_colliders.py): floors must carry the capsule and walls must leave a lane
COLLIDER_ROUTES = {
    'spine': P((8, -47.5, 0), (8, -34.0, 0)), 'spine_to_concourse_to_reactor': P((8, CY, 0), (0, CY, 0), (0, RY - 11.0, 0)), 'concourse_to_fuel_F02E': P((0, CY, 0), (-4.0, F02E[1], 0), (-5.3, F02E[1], 0)),
    'reactor_waste_junction': P((10.85, WY, 0), (11.55, WY, 0)), 'spine_to_dock_tube': P((8, -40.39, 0), (12.1, -40.39, 0)),
    'reactor_north_stub': R((0, 11.0, 0), (0, 14.4, 0)), 'reactor_west_stub': R((-11.0, 0, 0), (-14.4, 0, 0)), 'turbine_electrical_junction': R((10.05, 33.0, 0), (10.65, 33.0, 0)),
    'condenser_stair': R((-5.6, 28.6, 0), (-5.6, 26.8, 0), (-5.6, 16.9, -6), (-5.6, 15.7, -6), (1.6, 15.7, -6), (1.6, 19.2, -6)),
}
# closed doors that must block: a short segment through each door centre (from doors.json at run time)
BLOCK_CHECKS = ['TURBINE_D02', 'ELECTRICAL_D02', 'WASTE_DISPATCH', 'WASTE_PERSONNEL', 'REACTOR_SE', 'HALL_EAST', 'DOCK_P2', 'SPINE_NORTH_END']

def world_tris(zlo, zhi, colliders=False):
    """All evaluated triangles (world space) whose z range meets [zlo, zhi], with an owner index. colliders=True: only the COLLIDERS proxies (door blockers only when enabled now)."""
    dg = bpy.context.evaluated_depsgraph_get(); cache = {}; parts = []; owners = []; on = {}
    for inst in dg.object_instances:
        ob = inst.object
        if ob.type not in ('MESH', 'CURVE', 'FONT'): continue
        owner = inst.parent.original.name if (inst.is_instance and inst.parent) else (ob.original.users_collection[0].name if ob.original.users_collection else ob.name)
        if colliders:
            if not owner.startswith('COLLIDERS') or ob.original.get('is_trigger') or (ob.original.get('collider_role') == 'door_blocker' and not ob.original.get('enabled_now')): continue
        elif owner.startswith('COLLIDERS') or 'haze' in ob.name.lower() or 'fog' in ob.name.lower() or 'volume' in ob.name.lower(): continue
        key = (ob.original.session_uid, ob.data.session_uid if ob.data else 0)
        if key not in cache:
            try: me = ob.to_mesh()
            except Exception: me = None
            if me is None or not len(me.polygons): cache[key] = None
            else:
                me.calc_loop_triangles(); co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
                ix = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', ix); cache[key] = (co.reshape(-1, 3), ix.reshape(-1, 3))
            ob.to_mesh_clear()
        if cache[key] is None: continue
        co, ix = cache[key]; M = np.array(inst.matrix_world, np.float32); T = (co @ M[:3, :3].T + M[:3, 3])[ix]
        z = T[:, :, 2]; m = (z.max(1) >= zlo) & (z.min(1) <= zhi)
        if m.any():
            parts.append(T[m]); oi = on.setdefault(owner + ' / ' + ob.original.name, len(on)); owners.append(np.full(int(m.sum()), oi, np.int32))
    names = [None] * len(on)
    for k, v in on.items(): names[v] = k
    return np.concatenate(parts), np.concatenate(owners), names

def build_bvh(T, sel):
    t = T[sel]; v = t.reshape(-1, 3).tolist(); f = np.arange(len(v)).reshape(-1, 3).tolist()
    return BVHTree.FromPolygons(v, f, all_triangles=True), np.nonzero(sel)[0]

def sample(route):
    pts = [Vector(p) for p in route]; out = []
    for a, b in zip(pts, pts[1:]):
        L = (Vector((b.x, b.y)) - Vector((a.x, a.y))).length; n = max(1, int(math.ceil(L / DS)))
        for i in range(n): out.append(a.lerp(b, i / n))
    out.append(pts[-1]); return out

def test_route(name, route, T, own, names):
    pts = np.array(route, np.float32); lo = pts.min(0) - [SIDE + 1.5, SIDE + 1.5, 0.6]; hi = pts.max(0) + [SIDE + 1.5, SIDE + 1.5, H_CAP + 0.6]
    sel = np.zeros(len(T), bool)
    for a, b in zip(route, route[1:]):           # triangles whose box meets the swept box of each leg
        A = np.minimum(a, b) - np.array([SIDE + 0.6, SIDE + 0.6, 0.6]); B = np.maximum(a, b) + np.array([SIDE + 0.6, SIDE + 0.6, H_CAP + 0.3])
        sel |= np.all(T.max(1) >= A, 1) & np.all(T.min(1) <= B, 1)
    bvh, idx = build_bvh(T, sel)
    S = sample(route); N = len(S); offs = np.round(np.arange(-SIDE, SIDE + 1e-6, DS), 2); K = len(offs)
    ok = np.zeros((N, K), bool); floor = np.full((N, K), np.nan); why = {}
    for i, p in enumerate(S):
        q = S[min(i + 1, N - 1)] - S[max(i - 1, 0)]; d = Vector((q.x, q.y)); d = d.normalized() if d.length > 1e-6 else Vector((1, 0)); nrm = Vector((-d.y, d.x))
        for k, o in enumerate(offs):
            c = Vector((p.x + nrm.x * o, p.y + nrm.y * o, p.z))
            hit = (None,)
            for jx, jy in ((0, 0), (0.013, 0.007), (-0.011, -0.013)):        # a ray that grazes a vertical face at a threshold is retried slightly off
                h_ = bvh.ray_cast(Vector((c.x + jx, c.y + jy, p.z + 0.9)), Vector((0, 0, -1)), 1.4)
                if h_[0] is not None and h_[1].z >= 0.7: hit = h_; break
                if hit[0] is None: hit = h_
            if hit[0] is None or hit[1].z < 0.7 or abs(hit[0].z - p.z) > 0.45:
                if o == 0: why.setdefault(i, 'no floor within 0.45 m' if hit[0] is None or abs(hit[0].z - p.z) > 0.45 else 'floor too steep')
                continue
            fz = hit[0].z; blocked = None
            for j in range(7):
                r = bvh.find_nearest(Vector((c.x, c.y, fz + 0.75 + 0.1 * j)), R_CAP)
                if r[0] is not None: blocked = r; break
            if blocked is None: ok[i, k] = True; floor[i, k] = fz
            elif o == 0: why.setdefault(i, 'capsule hits ' + names[own[idx[blocked[2]]]] + ' at (%.2f, %.2f, %.2f)' % tuple(blocked[0]))
    # continuity: offsets may change by MAXSHIFT per sample; start and end lanes must be within 0.3 m of the route
    step = int(round(MAXSHIFT / DS)); reach = np.zeros((N, K), bool); prev = np.full((N, K), -1)
    near = np.abs(offs) <= 0.3 + 1e-6
    reach[0] = ok[0] & near
    for i in range(1, N):
        for k in np.nonzero(ok[i])[0]:
            ks = range(max(0, k - step), min(K, k + step + 1)); cand = [kk for kk in ks if reach[i - 1, kk]]
            if cand: reach[i, k] = True; prev[i, k] = min(cand, key=lambda kk: abs(kk - k))
    ends = np.nonzero(reach[-1] & near)[0]
    res = dict(route=name, samples=N, centre_line_clear=int(ok[:, K // 2].sum()), passed=bool(len(ends)))
    if len(ends):
        k = ends[np.argmin(np.abs(offs[ends]))]; lane = []
        for i in range(N - 1, -1, -1):
            p = S[i]; q = S[min(i + 1, N - 1)] - S[max(i - 1, 0)]; d = Vector((q.x, q.y)).normalized(); nrm = Vector((-d.y, d.x))
            lane.append((p.x + nrm.x * offs[k], p.y + nrm.y * offs[k], floor[i, k])); k = prev[i, k] if i else k
        lane = lane[::-1]; L = sum(math.dist(a, b) for a, b in zip(lane, lane[1:]))
        res.update(lane_length_m=round(L, 2), max_offset_m=float(np.max(np.abs([math.hypot(a[0] - s.x, a[1] - s.y) for a, s in zip(lane, S)]))), lane=[[round(v, 2) for v in p] for p in lane[::5]])
    else:
        last = int(np.max(np.nonzero(reach.any(1))[0])) if reach.any() else -1
        res.update(reached_m=round(last * DS, 1), stuck_at=[round(v, 2) for v in S[max(last, 0)]], stuck_reason=why.get(last + 1, why.get(last, '?')))
    res['centre_line_obstructions'] = [dict(at_m=round(i * DS, 1), point=[round(v, 2) for v in S[i]], why=w) for i, w in sorted(why.items())][:40]
    print('ROUTE %-36s %s  %s' % (name, 'PASS' if res['passed'] else 'FAIL', ('lane %.1f m' % res['lane_length_m']) if res['passed'] else ('stuck at %.1f m: %s' % (res['reached_m'], res['stuck_reason']))))
    return res

def blocked_check(door, T, own, names):
    loc = Vector(door['plan']); d = Vector((door['outward'][0], door['outward'][1], 0)); a = loc - d * 0.8; b = loc + d * 0.8
    route = [(a.x, a.y, loc.z), (b.x, b.y, loc.z)]
    sel = np.all(T.max(1) >= np.minimum(route[0], route[1]) - [1.5, 1.5, 0.5], 1) & np.all(T.min(1) <= np.maximum(route[0], route[1]) + [1.5, 1.5, 2.2], 1)
    bvh, idx = build_bvh(T, sel); hits = 0
    for p in sample(route):
        if any(bvh.find_nearest(Vector((p.x, p.y, p.z + 0.75 + 0.1 * j)), R_CAP)[0] is not None for j in range(7)): hits += 1
    r = dict(door=door['id'], state=door['state'], samples_blocked=hits, blocks=hits > 0); print('BLOCK %-18s %s' % (door['id'], 'blocks' if hits else 'DOES NOT BLOCK')); return r

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[0] if a else os.path.join(HERE, 'validation', 'walk_report.json'); only = a[1:]
    col = '--colliders' in only; only = [x for x in only if x != '--colliders']
    t0 = time.time(); T, own, names = world_tris(-6.6, 2.3, colliders=col); print('TRIANGLES near walking heights', len(T), '%.0fs' % (time.time() - t0), '(collision proxies only)' if col else '')
    res = [test_route(k, v, T, own, names) for k, v in (COLLIDER_ROUTES if col else ROUTES).items() if not only or k in only]
    doors = {d['id']: d for d in json.load(open(os.path.join(HERE, 'validation', 'doors.json')))['doors']}
    blk = [blocked_check(doors[d], T, own, names) for d in BLOCK_CHECKS if d in doors] if not only else []
    if col: out = out.replace('.json', '') + '_colliders.json' if not out.endswith('_colliders.json') else out
    json.dump(dict(geometry='collision proxies only (COLLIDERS)' if col else 'visual meshes (every evaluated triangle)', capsule=dict(radius=R_CAP, height=H_CAP, step_offset=STEP), sample_m=DS, side_search_m=SIDE, routes=res, closed_doors=blk,
                   note='Geometry test against every evaluated triangle near the routes; not a runtime controller test. Door states as built.'), open(out, 'w'), indent=1)
    print('WALK done %.0fs: %d/%d routes pass, %d/%d closed doors block' % (time.time() - t0, sum(r['passed'] for r in res), len(res), sum(b['blocks'] for b in blk), len(blk)))
