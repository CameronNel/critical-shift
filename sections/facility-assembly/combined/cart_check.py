"""Cart clearance through the refinery freight door: does the animated ore cart (build_compact_map.patch_refinery_cart) pass through its whole cycle without
running into the map? Run on a built scene:

    blender --background combined_map.blend --python cart_check.py -- [validation/cart_check.json] [--step 4] [--tip-sweep]

Why: the freight door is a cart door (owner, 2026-10-15): a rail line with a side tipper built into the doorway, which the walk test's capsule cannot pass and is not meant
to. People use the colonnade door (walk route hall_to_refinery). This replaces the walk test's former "cart route" with the check that matters for a cart.
Method: every `step` frames of the loop the cart's evaluated triangles (the local copies with cart_part 1: cart, wheels, load) are tested against the map's triangles
near the rail, the tipper's moving parts included at the same frame (cradle, wheel guides, tip lock; BVH overlap, exact triangle intersection). A contact present in the authored pose (frame 1: cradle on its trunnion and base, wheels
in the captive guides) is not a fault; a pair of objects that touches at any other frame and not at frame 1 is. Wheel-on-rail contact is expected and left out (object
names with rail, sleeper or track ironwork). --tip-sweep also tests the tipper alone at 50 to 140 degrees (5 degree steps) and reports the largest clear angle."""
import bpy, sys, os, json, re
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__))
BOX = (-26.0, -18.5, -67.5, -53.5, -1.0, 4.0)        # plan x0, x1, y0, y1, z0, z1 around the rail, the tipper and the freight door
EXPECTED = re.compile(r'rail|sleeper|track ironwork', re.I)

def gather(pick):
    """Evaluated world triangles of the instances whose original object name passes pick(name): (tris, owner index per tri, names)."""
    dg = bpy.context.evaluated_depsgraph_get(); parts, owners, on = [], [], {}
    x0, x1, y0, y1, z0, z1 = BOX
    for inst in dg.object_instances:
        ob = inst.object
        if ob.type not in ('MESH', 'CURVE', 'FONT') or not pick(ob.original.name): continue
        if any(k in ob.name.lower() for k in ('haze', 'fog', 'volume')) or (ob.original.users_collection and ob.original.users_collection[0].name.startswith('COLLIDERS')): continue
        try: me = ob.to_mesh()
        except Exception: continue
        if me is None or not len(me.polygons): ob.to_mesh_clear(); continue
        me.calc_loop_triangles(); co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
        ix = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', ix); ob.to_mesh_clear()
        M = np.array(inst.matrix_world, np.float32); T = (co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3])[ix.reshape(-1, 3)]
        lo, hi = T.min(1), T.max(1)
        m = (hi[:, 0] >= x0) & (lo[:, 0] <= x1) & (hi[:, 1] >= y0) & (lo[:, 1] <= y1) & (hi[:, 2] >= z0) & (lo[:, 2] <= z1)
        if m.any():
            parts.append(T[m]); owners.append(np.full(int(m.sum()), on.setdefault(ob.original.name, len(on)), np.int32))
    names = [None] * len(on)
    for k, v in on.items(): names[v] = k
    if not parts: return np.zeros((0, 3, 3), np.float32), np.zeros(0, np.int32), names
    return np.concatenate(parts), np.concatenate(owners), names

def bvh(T):
    v = T.reshape(-1, 3).tolist(); return BVHTree.FromPolygons(v, np.arange(len(v)).reshape(-1, 3).tolist(), all_triangles=True)

def is_cart(name):
    o = bpy.data.objects.get(name); return bool(o is not None and o.get('cart_part'))

def contacts(S, so, sn, sb, f):
    """Object pairs (cart part, other) whose triangles intersect at frame f: the static map (S) plus the tipper's own moving parts at that frame."""
    bpy.context.scene.frame_set(f)
    T, o, n = gather(is_cart)
    if not len(T): return set(), 0
    K, ko, kn = gather(lambda s: s.endswith(' anim') and not is_cart(s))
    pairs = {(n[o[a]], sn[so[b]]) for a, b in bvh(T).overlap(sb)}
    if len(K): pairs |= {(n[o[a]], kn[ko[b]]) for a, b in bvh(T).overlap(bvh(K))}
    return {p for p in pairs if not EXPECTED.search(p[1]) and not EXPECTED.search(p[0])}, len(T)

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[0] if a and not a[0].startswith('--') else os.path.join(HERE, 'validation', 'cart_check.json')
    step = int(a[a.index('--step') + 1]) if '--step' in a else 4
    sc = bpy.context.scene; f0, f1 = sc.frame_start, sc.frame_end
    sc.frame_set(1)
    S, so, sn = gather(lambda s: not s.endswith(' anim')); sb = bvh(S)
    print('CART static triangles near the rail', len(S), 'objects', len(sn))
    base, nt = contacts(S, so, sn, sb, 1)
    print('CART authored contacts at frame 1:', sorted(base))
    faults = {}; frames = list(range(f0, f1 + 1, step)) + [f1]
    for f in frames:
        c, _ = contacts(S, so, sn, sb, f)
        for p in c - base: faults.setdefault('%s -> %s' % p, []).append(f)
    tip = None
    if '--tip-sweep' in a:
        pv = next(o for o in bpy.data.objects if o.name == 'CART_SIDE_TIP_PIVOT anim'); ad = pv.animation_data; act = ad.action; ad.action = None
        r0 = pv.rotation_euler.x; tip = {}
        for deg in range(50, 141, 5):
            pv.rotation_euler.x = r0 - np.radians(deg); c, _ = contacts(S, so, sn, sb, 1)
            tip[deg] = sorted('%s -> %s' % p for p in c - base); print('CART tip %3d deg: %s' % (deg, tip[deg] or 'clear'))
        pv.rotation_euler.x = r0; ad.action = act
    sc.frame_set(1)
    res = dict(method=__doc__.split('\n\n')[2], loop_frames=[f0, f1], fps=sc.render.fps, step=step, frames_tested=len(frames), cart_triangles=nt,
               static_triangles=len(S), authored_contacts=sorted('%s -> %s' % p for p in base), new_contacts={k: v[:12] for k, v in sorted(faults.items())},
               passed=not faults, tip_sweep=tip)
    json.dump(res, open(out, 'w'), indent=1)
    for k, v in sorted(faults.items()): print('CART contact %-70s frames %s' % (k, v[:12]))
    print('CART CHECK %d frames, %d new contacts: %s' % (len(frames), len(faults), 'PASS' if not faults else 'FAIL'))
