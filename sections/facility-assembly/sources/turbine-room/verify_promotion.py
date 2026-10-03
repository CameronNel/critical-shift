"""Numeric interface check for the turbine module, run on the old and the promoted file:
    blender -b FILE.blend --python verify_promotion.py -- OUT.json
Shipping geometry = every mesh except OCCLUDER_ONLY and HAZE_VOLUME. Rays are cast against shipping geometry only."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out = sys.argv[sys.argv.index('--') + 1]
dg = bpy.context.evaluated_depsgraph_get()
skip = ('OCCLUDER_ONLY', 'HAZE_VOLUME')
verts, polys, owner = [], [], []
tris = total = 0
xs, ys, zs = [], [], []
for o in bpy.data.objects:
    if o.type not in ('MESH', 'CURVE', 'FONT'):
        continue
    ev = o.evaluated_get(dg)
    m = ev.to_mesh()
    t = sum(len(p.vertices) - 2 for p in m.polygons)
    total += t
    if o.name in skip or o.hide_render or o.hide_viewport:
        ev.to_mesh_clear()
        continue
    tris += t
    base = len(verts)
    wv = [o.matrix_world @ v.co for v in m.vertices]
    verts += wv
    for p in m.polygons:
        polys.append(tuple(base + i for i in p.vertices))
        owner.append(o.name)
    if wv:
        xs += [v.x for v in wv]; ys += [v.y for v in wv]; zs += [v.z for v in wv]
    ev.to_mesh_clear()
tree = BVHTree.FromPolygons(verts, polys)


def cast(origin, direction, dist=60.0):
    hit, n, idx, d = tree.ray_cast(Vector(origin), Vector(direction), dist)
    return None if hit is None else {'at': [round(c, 3) for c in hit], 'object': owner[idx]}


res = {'file': bpy.data.filepath, 'shipping_triangles': tris, 'all_triangles': total,
       'bbox': {'x': [round(min(xs), 3), round(max(xs), 3)], 'y': [round(min(ys), 3), round(max(ys), 3)], 'z': [round(min(zs), 3), round(max(zs), 3)]}}
# doors: clear passage through the doorway plane (rays along +Y from outside, door at y=0 and y=24)
for name, y0 in (('D01', 0.0), ('D02', 24.0)):
    blocked = []
    for x in (-1.1, 0.0, 1.1):
        for z in (0.15, 1.35, 2.55):
            h = cast((x, y0 - 0.3, z), (0, 1, 0), 0.6)
            if h:
                blocked.append({'x': x, 'z': z, **h})
    res[name + '_blocked_samples_of_9'] = len(blocked)
    res[name + '_blockers'] = blocked[:4]
# main aisle floor height along the route (rays straight down)
floor = []
for y in (1.0, 6.0, 12.0, 18.0, 23.0):
    h = cast((0.0, y, 1.0), (0, 0, -1), 3.0)
    floor.append(round(h['at'][2], 3) if h else None)
res['aisle_floor_z'] = floor
# U04 exhaust opening 2.5 x 1.5 centred at (4.6, 11.45): rays down at inset corners and centre
open_hits = []
for dx, dy in ((-1.1, -.6), (1.1, -.6), (-1.1, .6), (1.1, .6), (0, 0)):
    h = cast((4.6 + dx, 11.45 + dy, 0.5), (0, 0, -1), 4.0)
    open_hits.append(None if h is None else h['at'][2])
res['U04_opening_floor_z_at_5_points'] = open_hits
# markers
res['markers'] = {o.name: [round(v, 3) for v in o.matrix_world.translation] for o in bpy.data.objects if o.type == 'EMPTY' and o.name.startswith(('IF_',))}
# textures
missing = []
for img in bpy.data.images:
    if img.source == 'FILE' and not img.packed_file:
        if not Path(bpy.path.abspath(img.filepath)).exists():
            missing.append(img.filepath)
res['missing_textures'] = missing
res['has_MODULE_collection'] = 'MODULE_turbine-room' in bpy.data.collections
json.dump(res, open(out, 'w'), indent=2)
print('VERIFY', json.dumps({k: v for k, v in res.items() if k not in ('D01_blockers', 'D02_blockers', 'markers')})[:900])
