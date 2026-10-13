"""Door-frame audit of the built map: does every doorway open onto space on both sides, and does every closed exit face open ground rather than a wall? Run on a built scene:

    blender --background combined_map.blend --python door_audit.py -- [validation/door_audit.json]

Doors audited: every row of validation/doors.json (the map's doors, with their states) plus every portal in the placed rooms' own contracts
(sources/<room>/contracts/interface.json), placed with the room instance's transform; internal portals included (they show cut-outs inside a room).
Method: from the door plane, rays along the door normal to both sides (start 0.35 m off the plane so the door's own leaves and frame are skipped, up to 8 m),
at three points across the middle of the door (centre and +-min(0.3 w, 0.9 m): a player with margin) and two heights (1.0 m and 1.7 m, capped below the clear height); the clear depth of a side is the
shortest of its six rays plus 0.35 m. Every evaluated mesh, curve and text triangle counts (instances included; COLLIDERS, haze and volume boxes excluded).
Verdicts: an open door or internal portal needs >= 1.2 m on both sides; a closed or emergency exit needs >= 1.5 m outside (a door that opens onto less is a
door staring into a wall). Doors wider than 3 m are also probed at +-0.3 w and reported as "narrows" when the full width meets a wall
within 1.2 m (a wide frame onto a narrower passage: information, not a fail). Geometry only: it does not know what a player should see behind a door."""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk_test as W

SRC = os.path.normpath(os.path.join(HERE, '..', 'sources'))
OPEN_MIN, EXIT_MIN, SKIP, REACH = 1.2, 1.5, 0.35, 8.0

def contract_portals():
    """Portals of every placed room that has a contract, in plan coordinates: (id, room, centre, normal (one of the two sides), width, height, note)."""
    out = []
    for inst in bpy.data.objects:
        if not inst.name.startswith('ROOM_') or inst.instance_type != 'COLLECTION': continue
        key = inst.name[5:]; f = os.path.join(SRC, key, 'contracts', 'interface.json')
        if key == 'fuel-corridor': continue          # F23ci's contract; the short corridor S1 has only F01 and F02E, both in doors.json
        if not os.path.exists(f): continue
        try: d = json.load(open(f))
        except Exception: continue
        M = inst.matrix_world
        for p in d.get('portals', []) or d.get('ports', []):
            c = p.get('centre') or p.get('center') or p.get('threshold')
            if not c: continue
            n = p.get('outward_normal') or p.get('inward_normal')
            if not n:
                wa = (p.get('width_axis') or '+X').upper()
                n = [0, 1, 0] if 'X' in wa else [1, 0, 0]
            w = p.get('clear_width_m') or p.get('clear_width') or 2.0; h = p.get('clear_height_m') or p.get('clear_height') or 2.4
            cc = M @ Vector((c[0], c[1], 0.0)); nn = (M.to_3x3() @ Vector((n[0], n[1], 0.0))).normalized()
            out.append(dict(id='%s/%s' % (key, p.get('id')), room=key, plan=[cc.x, cc.y, cc.z], outward=[nn.x, nn.y], clear_w=float(w), clear_h=float(h),
                            state=str(p.get('default_state') or p.get('type') or ''), source='contract'))
    return out

def depth(bvh, origin, d, own, names):
    best, what = REACH + SKIP, ''
    for e in origin:
        r = bvh.ray_cast(e, d, REACH)
        if r[0] is not None and r[3] + SKIP < best: best, what = r[3] + SKIP, names[own[r[2]]]
    return best, what

def audit(T, own, names, rows):
    bvh = BVHTree.FromPolygons(T.reshape(-1, 3).tolist(), np.arange(len(T) * 3).reshape(-1, 3).tolist(), all_triangles=True)
    res = []
    for r in rows:
        c = Vector(r['plan']); n = Vector((r['outward'][0], r['outward'][1], 0.0)).normalized(); t = Vector((-n.y, n.x, 0.0)); w, h = r['clear_w'], r['clear_h']
        zs = [z for z in (1.0, 1.7) if z < h - 0.15] or [min(1.0, h * 0.5)]
        pts = [c + t * (k * min(0.3 * w, 0.9)) + Vector((0, 0, z)) for k in (-1, 0, 1) for z in zs]        # verdict: the central 1.8 m (a player plus margin)
        wide = [c + t * (k * 0.3 * w) + Vector((0, 0, z)) for k in (-1, 1) for z in zs]                    # note: the full clear width
        (out_d, out_w), (in_d, in_w) = depth(bvh, [p + n * SKIP for p in pts], n, own, names), depth(bvh, [p - n * SKIP for p in pts], -n, own, names)
        (wo, wow), (wi, wiw) = depth(bvh, [p + n * SKIP for p in wide], n, own, names), depth(bvh, [p - n * SKIP for p in wide], -n, own, names)
        narrows = '' if min(wo, wi) >= OPEN_MIN or 0.3 * w <= 0.9 else 'the full %.1f m width narrows within %.2f m (%s side, %s)' % (w, min(wo, wi), 'outward' if wo < wi else 'inward', wow if wo < wi else wiw)
        st = r.get('state', ''); emergency = r.get('emergency_exit', False)
        closed_exit = (st != 'open' and r.get('source') != 'contract') or emergency
        if closed_exit: ok = out_d >= EXIT_MIN; why = '' if ok else 'closed exit faces %s %.2f m away' % (out_w, out_d)
        else:
            ok = out_d >= OPEN_MIN and in_d >= OPEN_MIN
            why = '' if ok else 'blocked within %.2f m on the %s side by %s' % (min(out_d, in_d), 'outward' if out_d < in_d else 'inward', out_w if out_d < in_d else in_w)
        res.append(dict(id=r['id'], source=r.get('source', 'doors.json'), state=st, emergency_exit=emergency, plan=[round(v, 2) for v in r['plan']],
                        depth_out_m=round(out_d, 2), depth_in_m=round(in_d, 2), nearest_out=out_w, nearest_in=in_w, ok=ok, why=why, narrows=narrows))
        print('DOOR %-44s %-10s out %5.2f in %5.2f %s %s' % (r['id'], st[:10], out_d, in_d, 'ok' if ok else 'FLAG ' + why, ('| ' + narrows) if narrows else ''))
    return res

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[0] if a else os.path.join(HERE, 'validation', 'door_audit.json')
    T, own, names = W.world_tris(-6.6, 4.6)
    doors = json.load(open(os.path.join(HERE, 'validation', 'doors.json')))['doors']
    rows = [dict(d, source='doors.json') for d in doors]
    for c in contract_portals():                     # a contract portal at a map door (within 0.6 m) is the same door: the map row, with its state, is audited
        if all(math.dist(c['plan'][:2], d['plan'][:2]) > 0.6 for d in doors): rows.append(c)
    res = audit(T, own, names, rows)
    bad = [r for r in res if not r['ok']]
    json.dump(dict(method=__doc__.split('\n\n')[2] if __doc__.count('\n\n') > 1 else '', thresholds=dict(open_min_m=OPEN_MIN, exit_min_m=EXIT_MIN, skip_m=SKIP, reach_m=REACH),
                   doors=res, flagged=bad), open(out, 'w'), indent=1)
    print('AUDIT %d doors, %d flagged' % (len(res), len(bad)))
