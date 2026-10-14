"""Horizontal section of the built map (every evaluated mesh, curve and text object, instances included), by top-level owner. Run on a built scene:

    blender --background combined_map.blend --python plan_cut.py -- out.npz z1 z2 ...

Writes segments 'owner|z' (x0, y0, x1, y1 plan metres) and '__meta__' (room placements, triangles per owner). Used by check_overlaps.py, walk_test.py and the plan drawings."""
import bpy, sys, numpy as np, time, json, math
a = sys.argv[sys.argv.index('--') + 1:]; out = a[0]; ZS = [float(z) for z in a[1:]]
dg = bpy.context.evaluated_depsgraph_get(); t0 = time.time()
cache = {}; segs = {z: {} for z in ZS}; tris = {}
def local_tris(ob):
    key = (ob.original.session_uid, ob.data.session_uid if ob.data else 0)
    if key in cache: return cache[key]
    try: me = ob.to_mesh()
    except Exception: me = None
    if me is None: cache[key] = None; return None
    me.calc_loop_triangles(); n = len(me.loop_triangles)
    if n == 0: ob.to_mesh_clear(); cache[key] = None; return None
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
    ix = np.empty(n * 3, np.int32); me.loop_triangles.foreach_get('vertices', ix)
    ob.to_mesh_clear(); cache[key] = (co.reshape(-1, 3), ix.reshape(-1, 3)); return cache[key]
for inst in dg.object_instances:
    ob = inst.object
    if ob.type not in ('MESH', 'CURVE', 'FONT'): continue
    if inst.is_instance and inst.parent: owner = inst.parent.original.name
    else: owner = ob.original.users_collection[0].name if ob.original.users_collection else ob.name
    if owner.startswith('COLLIDERS'): continue
    lt = local_tris(ob)
    if lt is None: continue
    co, ix = lt; M = np.array(inst.matrix_world, np.float32); T = (co @ M[:3, :3].T + M[:3, 3])[ix]
    tris[owner] = tris.get(owner, 0) + len(ix)
    zmin = T[:, :, 2].min(1); zmax = T[:, :, 2].max(1)
    for z in ZS:
        m = (zmin < z) & (zmax > z)
        if not m.any(): continue
        t = T[m]; d = t[:, :, 2] - z; cs = []; ps = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            di, dj = d[:, i], d[:, j]; c = (di * dj) < 0; f = np.where(c, di / np.where(c, di - dj, 1), 0)
            cs.append(c); ps.append(t[:, i, :2] + (t[:, j, :2] - t[:, i, :2]) * f[:, None])
        cs = np.stack(cs, 1); ps = np.stack(ps, 1); ok = cs.sum(1) == 2; cs, ps = cs[ok], ps[ok]
        order = np.argsort(~cs, axis=1, kind='stable')[:, :2]
        A = np.take_along_axis(ps, order[:, 0:1, None].repeat(2, 2), 1)[:, 0]; B = np.take_along_axis(ps, order[:, 1:2, None].repeat(2, 2), 1)[:, 0]
        segs[z].setdefault(owner, []).append(np.hstack([A, B]).astype(np.float32))
data = {'%s|%.2f' % (k, z): np.vstack(v) for z in ZS for k, v in segs[z].items()}
pl = {o.name: (list(o.location), math.degrees(o.rotation_euler.z)) for o in bpy.data.objects if o.name.startswith('ROOM_') and o.instance_type == 'COLLECTION'}
data['__meta__'] = np.array(json.dumps(dict(placements=pl, triangles=tris, heights=ZS)))
np.savez_compressed(out, **data)
print('PLANCUT done %.1fs owners %d triangles %d' % (time.time() - t0, len(tris), sum(tris.values())))
