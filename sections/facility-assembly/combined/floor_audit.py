"""Stacked-slab audit: is the surface you walk on the room's own floor, or a slab of another room poking through it? Run on a built scene:

    blender --background combined_map.blend --python floor_audit.py -- [validation/floor_audit.json]

Why: rooms are authored on their own, each with full-thickness floors and roofs. Stacking them (the condenser bay under the turbine) or laying the front end's ground slab
under them can put one room's roof above another's floor. The first case was found by eye (2026-10-13): the condenser's roof slab stood 0.3 m proud of the turbine floor and
read as raw ground; the plan cuts (0.4 m and up) and the walk test (0.35 m step) both passed it.
Method: a 0.5 m grid over the map at two levels (ground z 0 and the condenser level, `condenser_z`: -6.3 since 2026-10-19). From 2.0 m above each level a ray goes down; the first upward-facing horizontal surface
hit is the walked surface. It is flagged when it lies 0.02 to 0.5 m above the level and the next upward-facing horizontal surface below it (within 0.6 m) belongs to a
different room or connector (owners compared at room level: props on their own room's floor are not flagged; the front end's context ground, the underlay of the whole map, is
not counted as a floor). Every evaluated mesh counts (COLLIDERS, haze and volumes excluded)."""
import bpy, sys, os, json
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = (0.0, float(bpy.context.scene.get('condenser_z', -6.0))); STEP, RISE_MIN, RISE_MAX, BELOW = 0.5, 0.02, 0.5, 0.6

def scene_bvh():
    """The evaluated triangles from z -7.2 to 2.1 by top-level owner (walk_test.world_tris: COLLIDERS, haze and volume boxes excluded)."""
    import numpy as np
    sys.path.insert(0, HERE); import walk_test as W
    T, own, names = W.world_tris(-7.2, 2.1)
    return BVHTree.FromPolygons(T.reshape(-1, 3).tolist(), np.arange(len(T) * 3).reshape(-1, 3).tolist(), all_triangles=True), own, names

def walked(bvh, own, x, y, z0):
    """Upward-facing horizontal hits under (x, y), top down, from z0 + 2 to z0 - 1: [(z, owner index)]."""
    out, o = [], Vector((x, y, z0 + 2.0))
    while True:
        r = bvh.ray_cast(o, Vector((0, 0, -1)), (o.z - (z0 - 1.0)))
        if r[0] is None: return out
        if r[1].z > 0.95: out.append((r[0].z, own[r[2]]))
        o = r[0] - Vector((0, 0, 0.001))

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[0] if a else os.path.join(HERE, 'validation', 'floor_audit.json')
    bvh, own, names = scene_bvh()
    rooms = [o for o in bpy.data.objects if o.name.startswith('ROOM_') and o.instance_type == 'COLLECTION']
    xs = [o.location.x for o in rooms]; ys = [o.location.y for o in rooms]
    x0, x1, y0, y1 = min(xs) - 25, max(xs) + 25, min(ys) - 25, max(ys) + 25
    flags = defaultdict(list); n = 0
    for z0 in LEVELS:
        y = y0
        while y <= y1:
            x = x0
            while x <= x1:
                h = walked(bvh, own, x, y, z0); n += 1
                if h and RISE_MIN <= h[0][0] - z0 <= RISE_MAX:
                    below = [b for b in h[1:] if h[0][0] - b[0] <= BELOW]
                    room = lambda k: names[k].split(' / ')[0]
                    if below and room(below[0][1]) != room(h[0][1]) and 'context_ground' not in names[below[0][1]]:
                        flags[(names[h[0][1]], names[below[0][1]], z0)].append((round(x, 2), round(y, 2), round(h[0][0], 3)))
                x += STEP
            y += STEP
    rows = [dict(slab_owner=k[0], over_floor_of=k[1], level=k[2], samples=len(v), area_m2=len(v) * STEP * STEP, first=v[0], plan_box=[min(p[0] for p in v), min(p[1] for p in v), max(p[0] for p in v), max(p[1] for p in v)],
                 top_z=max(p[2] for p in v)) for k, v in sorted(flags.items(), key=lambda kv: -len(kv[1]))]
    for r in rows: print('FLOOR %-34s over %-34s level %5.1f  %4d samples (%.1f m2) top z %.3f box %s' % (r['slab_owner'], r['over_floor_of'], r['level'], r['samples'], r['area_m2'], r['top_z'], r['plan_box']))
    json.dump(dict(method=__doc__.split('\n\n')[2], grid_m=STEP, rise_m=[RISE_MIN, RISE_MAX], samples=n, flagged=rows), open(out, 'w'), indent=1)
    print('FLOOR AUDIT %d samples, %d owner pairs flagged' % (n, len(rows)))
